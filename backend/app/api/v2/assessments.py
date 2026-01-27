"""
Phase 2 API Router: LLM-Graded Assessments

Endpoints for submitting open-ended answers, receiving AI-generated feedback,
and managing assessment submissions.
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel, Field

from app.database import get_db
from app.dependencies import get_current_user, verify_premium, verify_quota
from app.models.user import User
from app.models.llm import AssessmentSubmission, AssessmentFeedback, AssessmentSubmissionStatus
from app.services.llm.assessment_grader import AssessmentGrader
from app.utils.storage import R2StorageClient
from app.schemas.assessment import (
    AssessmentSubmitRequest,
    AssessmentSubmitResponse,
    AssessmentFeedbackResponse,
    AssessmentFeedbackMetadata
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/assessments",
    tags=["llm-assessments"]
)


# Apply premium verification to all endpoints
router.dependencies = [Depends(verify_premium)]


async def grade_submission_background(
    submission_id: str,
    db: AsyncSession
):
    """
    Background task to grade assessment submission.

    Args:
        submission_id: UUID of submission to grade
        db: Database session
    """
    logger.info(f"Background grading task started for submission {submission_id}")

    try:
        # Fetch submission
        result = await db.execute(
            select(AssessmentSubmission).where(
                AssessmentSubmission.submission_id == submission_id
            )
        )
        submission = result.scalar_one_or_none()

        if not submission:
            logger.error(f"Submission {submission_id} not found")
            return

        # Update status to processing
        submission.grading_status = AssessmentSubmissionStatus.PROCESSING
        submission.grading_started_at = datetime.utcnow()
        await db.commit()

        # Grade it
        grader = AssessmentGrader(db)
        feedback = await grader.grade_submission(submission)

        # Update submission status
        submission.grading_status = AssessmentSubmissionStatus.COMPLETED
        submission.grading_completed_at = datetime.utcnow()
        await db.commit()

        logger.info(
            f"Background grading completed for {submission_id}: "
            f"score={feedback.quality_score:.1f}"
        )

    except Exception as e:
        logger.error(f"Background grading failed for {submission_id}: {e}")
        # Update submission to failed status
        submission.grading_status = AssessmentSubmissionStatus.FAILED
        submission.error_message = str(e)
        await db.commit()


@router.post("/submit", response_model=AssessmentSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_assessment(
    request: AssessmentSubmitRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    _quota_verified = Depends(verify_quota),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an open-ended answer for LLM grading.

    Flow:
    1. Validate answer length (50-5000 characters)
    2. Check attempt count (max 3 per question)
    3. Create AssessmentSubmission record (status=pending)
    4. Trigger background grading task
    5. Return 202 Accepted with submission_id

    Rate Limits:
    - Premium users: 20 assessments per month
    - Max 3 attempts per question

    Expected Grading Time: 5-15 seconds
    """
    logger.info(f"User {current_user.id} submitting assessment for question {request.question_id}")

    # Step 1: Check attempt count
    previous_attempts = await db.execute(
        select(AssessmentSubmission)
        .where(
            and_(
                AssessmentSubmission.student_id == current_user.id,
                AssessmentSubmission.question_id == request.question_id
            )
        )
        .order_by(desc(AssessmentSubmission.submitted_at))
    )
    attempts = previous_attempts.scalars().all()

    if len(attempts) >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum 3 attempts allowed for question {request.question_id}. You have used {len(attempts)}."
        )

    # Step 2: Determine attempt number
    attempt_number = len(attempts) + 1
    previous_submission_id = attempts[0].submission_id if attempts else None

    # Step 3: Create submission record
    submission = AssessmentSubmission(
        student_id=current_user.id,
        question_id=request.question_id,
        answer_text=request.answer_text,
        previous_submission_id=previous_submission_id,
        attempt_number=attempt_number,
        grading_status=AssessmentSubmissionStatus.PENDING
    )

    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    logger.info(f"Created submission {submission.submission_id} (attempt {attempt_number})")

    # Step 4: Trigger background grading
    background_tasks.add_task(grade_submission_background, submission.submission_id, db)

    # Step 5: Return response
    return AssessmentSubmitResponse(
        submission_id=str(submission.submission_id),
        student_id=str(current_user.id),
        question_id=submission.question_id,
        submitted_at=submission.submitted_at,
        grading_status=submission.grading_status.value,
        estimated_completion_seconds=15,
        feedback_url=f"/api/v2/assessments/feedback/{submission.submission_id}"
    )


@router.get("/feedback/{submission_id}", response_model=AssessmentFeedbackResponse)
async def get_assessment_feedback(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve graded feedback for a submission.

    Returns:
    - 202 Accepted: Still grading (check back in 5 seconds)
    - 200 OK: Grading complete, returns feedback
    - 500 Internal Server Error: Grading failed

    Feedback includes:
    - Quality score (0.0 - 10.0)
    - 3-5 specific strengths
    - 3-5 actionable improvements
    - Detailed written feedback
    - Token usage and cost metadata
    """
    # Fetch submission
    result = await db.execute(
        select(AssessmentSubmission).where(
            and_(
                AssessmentSubmission.submission_id == submission_id,
                AssessmentSubmission.student_id == current_user.id
            )
        )
    )
    submission = result.scalar_one_or_none()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    # Check grading status
    if submission.grading_status == AssessmentSubmissionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Grading in progress. Please check back in 5-10 seconds.",
            headers={"Retry-After": "5"}
        )

    if submission.grading_status == AssessmentSubmissionStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Grading in progress. Please check back in 5-10 seconds.",
            headers={"Retry-After": "5"}
        )

    if submission.grading_status == AssessmentSubmissionStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grading failed: {submission.error_message or 'Unknown error'}"
        )

    # Fetch feedback
    result = await db.execute(
        select(AssessmentFeedback).where(
            AssessmentFeedback.submission_id == submission_id
        )
    )
    feedback = result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    return AssessmentFeedbackResponse(
        feedback_id=str(feedback.feedback_id),
        submission_id=str(feedback.submission_id),
        quality_score=float(feedback.quality_score),
        strengths=feedback.strengths_json,
        improvements=feedback.improvements_json,
        detailed_feedback=feedback.detailed_feedback,
        metadata=AssessmentFeedbackMetadata(
            tokens_used={
                "input": feedback.tokens_input,
                "output": feedback.tokens_output,
                "total": feedback.tokens_input + feedback.tokens_output
            },
            cost_usd=float(feedback.cost_usd),
            latency_ms=0,  # Not tracked in feedback model
            llm_model="gpt-4o-mini"
        ),
        is_off_topic=feedback.is_off_topic
    )


@router.get("/submissions")
async def list_assessment_submissions(
    question_id: Optional[str] = None,
    grading_status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List current user's assessment submissions.

    Query Parameters:
    - question_id: Filter by specific question
    - grading_status: Filter by status (pending, processing, completed, failed)
    - limit: Results per page (default 20, max 100)
    - offset: Pagination offset (default 0)

    Returns summary of each submission including:
    - submission_id, question_id, attempt_number
    - submitted_at, grading_status
    - quality_score (if completed)
    """
    # Build query
    query = select(AssessmentSubmission).where(
        AssessmentSubmission.student_id == current_user.id
    )

    # Apply filters
    if question_id:
        query = query.where(AssessmentSubmission.question_id == question_id)

    if grading_status:
        try:
            status_enum = AssessmentSubmissionStatus(grading_status)
            query = query.where(AssessmentSubmission.grading_status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid grading_status: {grading_status}"
            )

    # Order and paginate
    query = query.order_by(desc(AssessmentSubmission.submitted_at))
    query = query.limit(limit).offset(offset)

    # Execute
    result = await db.execute(query)
    submissions = result.scalars().all()

    # Fetch feedback for completed submissions
    submission_ids = [s.submission_id for s in submissions]
    feedback_result = await db.execute(
        select(AssessmentFeedback).where(
            AssessmentFeedback.submission_id.in_(submission_ids)
        )
    )
    feedback_map = {
        str(f.submission_id): f
        for f in feedback_result.scalars().all()
    }

    # Build response
    response_data = []
    for submission in submissions:
        submission_data = {
            "submission_id": str(submission.submission_id),
            "question_id": submission.question_id,
            "attempt_number": submission.attempt_number,
            "submitted_at": submission.submitted_at.isoformat(),
            "grading_status": submission.grading_status.value,
            "feedback_url": f"/api/v2/assessments/feedback/{submission.submission_id}"
        }

        # Add quality_score if available
        feedback = feedback_map.get(str(submission.submission_id))
        if feedback:
            submission_data["quality_score"] = float(feedback.quality_score)

        response_data.append(submission_data)

    return {
        "submissions": response_data,
        "count": len(response_data),
        "limit": limit,
        "offset": offset
    }


@router.get("/questions/{question_id}")
async def get_assessment_question(
    question_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a single assessment question.

    Returns:
    - question_text
    - evaluation_criteria (array)
    - example_excellent_answer
    - example_poor_answer
    - expected_length (character range)
    - premium_only: true
    """
    r2_client = R2StorageClient()

    # Extract chapter_id from question_id
    chapter_id = question_id.split('-')[0] + '-' + question_id.split('-')[1]
    rubric_file = f"{chapter_id}-assessments.json"

    try:
        # Fetch from R2
        rubric_content = await r2_client.get_file(f"assessments/{rubric_file}")
        import json
        rubric_data = json.loads(rubric_content)

        # Find the specific question
        questions = rubric_data.get("questions", [])
        question_data = None
        for q in questions:
            if q["question_id"] == question_id:
                question_data = q
                break

        if not question_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found"
            )

        return {
            "question_id": question_data["question_id"],
            "question_text": question_data["question_text"],
            "evaluation_criteria": question_data["evaluation_criteria"],
            "example_excellent_answer": question_data["example_excellent_answer"],
            "example_poor_answer": question_data["example_poor_answer"],
            "expected_length": "50-5000 characters (approximately 10-500 words)",
            "premium_only": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch question {question_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load question"
        )


@router.get("/questions")
async def list_assessment_questions(
    chapter_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all available assessment questions.

    Query Parameters:
    - chapter_id: Filter by chapter (e.g., "04-rag", "05-fine-tuning")

    Returns list of questions with student's status:
    - question_id, question_text (truncated)
    - student_status: "not_attempted" | "attempted" | "passed" | "needs_work"
    - latest_score: null | 0.0-10.0
    - attempts_remaining: 0-3
    """
    r2_client = R2StorageClient()

    # Get all assessment files
    all_questions = []

    assessment_files = [
        "04-rag-assessments.json",
        "05-fine-tuning-assessments.json",
        "06-ai-apps-assessments.json"
    ]

    for filename in assessment_files:
        try:
            content = await r2_client.get_file(f"assessments/{filename}")
            import json
            data = json.loads(content)

            for q in data.get("questions", []):
                if chapter_id is None or q["question_id"].startswith(chapter_id):
                    all_questions.append(q)
        except Exception as e:
            logger.warning(f"Failed to load {filename}: {e}")

    # Fetch user's submission history
    result = await db.execute(
        select(AssessmentSubmission).where(
            AssessmentSubmission.student_id == current_user.id
        )
    )
    submissions = result.scalars().all()

    # Build submission map: question_id -> best_score, attempt_count
    submission_map = {}
    for sub in submissions:
        qid = sub.question_id
        if qid not in submission_map:
            submission_map[qid] = {
                "attempts": 0,
                "best_score": None
            }

        submission_map[qid]["attempts"] += 1

        # Fetch feedback for score
        feedback_result = await db.execute(
            select(AssessmentFeedback).where(
                AssessmentFeedback.submission_id == sub.submission_id
            )
        )
        feedback = feedback_result.scalar_one_or_none()
        if feedback:
            score = float(feedback.quality_score)
            if submission_map[qid]["best_score"] is None or score > submission_map[qid]["best_score"]:
                submission_map[qid]["best_score"] = score

    # Build response
    response_questions = []
    for q in all_questions:
        qid = q["question_id"]
        user_data = submission_map.get(qid, {"attempts": 0, "best_score": None})

        # Determine status
        if user_data["attempts"] == 0:
            student_status = "not_attempted"
        elif user_data["best_score"] is None:
            student_status = "attempted"  # Still grading
        elif user_data["best_score"] >= 7.0:
            student_status = "passed"
        else:
            student_status = "needs_work"

        response_questions.append({
            "question_id": qid,
            "question_text": q["question_text"][:100] + "...",
            "student_status": student_status,
            "latest_score": user_data["best_score"],
            "attempts_remaining": 3 - user_data["attempts"]
        })

    return {
        "questions": response_questions,
        "count": len(response_questions)
    }
