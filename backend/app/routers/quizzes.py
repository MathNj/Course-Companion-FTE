"""
Quiz Endpoints

REST API for quiz retrieval and submission.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.quiz import QuizAttempt
from app.models.progress import ChapterProgress
from app.services.content import get_quiz_with_cache
from app.services.quiz_grader import grade_quiz
from app.services.progress_tracker import update_streak
from app.services.milestone_service import check_quiz_milestones, check_chapter_completion_milestones
from app.schemas.quiz import QuizAttemptCreate, QuizAttemptResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


# Quiz metadata (hardcoded for now, will move to database/storage)
QUIZ_METADATA = [
    {
        "id": "chapter-1-quiz",
        "chapter_id": "chapter-1",
        "title": "Introduction to Generative AI - Quiz",
        "description": "Test your understanding of generative AI fundamentals",
        "total_questions": 10,
        "time_limit_minutes": 15,
        "passing_score": 70,
    },
    {
        "id": "chapter-2-quiz",
        "chapter_id": "chapter-2",
        "title": "How LLMs Work - Quiz",
        "description": "Quiz on language model architecture and training",
        "total_questions": 12,
        "time_limit_minutes": 20,
        "passing_score": 70,
    },
    {
        "id": "chapter-3-quiz",
        "chapter_id": "chapter-3",
        "title": "Prompt Engineering Basics - Quiz",
        "description": "Test your prompt engineering skills",
        "total_questions": 15,
        "time_limit_minutes": 20,
        "passing_score": 70,
    },
    {
        "id": "chapter-4-quiz",
        "chapter_id": "chapter-4",
        "title": "Advanced Prompting Techniques - Quiz",
        "description": "Advanced prompting strategies and patterns",
        "total_questions": 15,
        "time_limit_minutes": 25,
        "passing_score": 70,
    },
    {
        "id": "chapter-5-quiz",
        "chapter_id": "chapter-5",
        "title": "AI Safety and Ethics - Quiz",
        "description": "Understanding AI safety, bias, and ethical considerations",
        "total_questions": 12,
        "time_limit_minutes": 20,
        "passing_score": 70,
    },
    {
        "id": "chapter-6-quiz",
        "chapter_id": "chapter-6",
        "title": "Real-World Applications - Quiz",
        "description": "Applying AI in practical scenarios",
        "total_questions": 15,
        "time_limit_minutes": 25,
        "passing_score": 70,
    },
]


@router.get("/{quiz_id}", response_model=Dict[str, Any])
async def get_quiz(
    quiz_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Get quiz content by ID.

    Returns quiz questions WITHOUT answer keys or explanations.
    Students must submit answers to get graded results.
    Unauthenticated users can access free tier quizzes (chapters 1-3).
    """
    from app.utils.auth import verify_token

    # Manually get optional user from request
    current_user = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = verify_token(token, token_type="access")
            if payload and payload.get("sub"):
                from uuid import UUID
                user_id = UUID(payload["sub"])
                result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                current_user = result.scalar_one_or_none()
        except:
            current_user = None

    # Find quiz metadata
    quiz_meta = next((q for q in QUIZ_METADATA if q["id"] == quiz_id), None)

    if not quiz_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} not found",
        )

    # Check if user has access to this chapter
    # (Quizzes have same access tier as their chapters)
    chapter_id = quiz_meta["chapter_id"]
    chapter_number = int(chapter_id.split("-")[1])

    # Chapters 1-3 are free, 4-6 are premium
    # Unauthenticated users can only access free tier
    if chapter_number >= 4:
        if not current_user or current_user.subscription_tier == "free":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": f"This quiz requires a premium subscription",
                    "quiz_title": quiz_meta["title"],
                    "upgrade_url": "/upgrade",
                },
            )

    # Fetch quiz content from cache/storage (with answers excluded)
    quiz_content = await get_quiz_with_cache(quiz_id, exclude_answers=True)

    if not quiz_content:
        # Return placeholder if content not seeded yet
        quiz_content = {
            "questions": [],
            "note": "Quiz content will be available after content seeding",
        }

    # Get user's previous attempts (only for authenticated users)
    attempts = []
    if current_user:
        result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == current_user.id)
            .where(QuizAttempt.quiz_id == quiz_id)
            .order_by(desc(QuizAttempt.created_at))
        )
        attempts = result.scalars().all()

    # Calculate attempt summary
    attempt_summary = {
        "total_attempts": len(attempts),
        "best_score": max((a.score_percentage for a in attempts), default=None),
        "last_score": attempts[0].score_percentage if attempts else None,
        "has_passed": any(a.is_passed for a in attempts),
    }

    return {
        **quiz_meta,
        **quiz_content,
        "user_attempts": attempt_summary,
    }


@router.post("/{quiz_id}/submit", response_model=Dict[str, Any], openapi_extra={"security": []})
async def submit_quiz(
    quiz_id: str,
    submission: QuizAttemptCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit quiz answers for grading.

    Flow:
    1. Validate quiz_id and answers format
    2. Fetch quiz content with answer keys
    3. Grade submission using quiz_grader service
    4. Create QuizAttempt record
    5. Update ChapterProgress if quiz passed
    6. Return graded results with explanations
    """
    from app.utils.auth import verify_token

    # Manually get optional user from request
    current_user = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = verify_token(token, token_type="access")
            if payload and payload.get("sub"):
                from uuid import UUID
                user_id = UUID(payload["sub"])
                result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                current_user = result.scalar_one_or_none()
        except:
            current_user = None

    # Validate quiz exists
    quiz_meta = next((q for q in QUIZ_METADATA if q["id"] == quiz_id), None)

    if not quiz_meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz {quiz_id} not found",
        )

    # Validate submission matches quiz_id
    if submission.quiz_id != quiz_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Submission quiz_id '{submission.quiz_id}' does not match URL quiz_id '{quiz_id}'",
        )

    chapter_id = quiz_meta["chapter_id"]

    # Fetch quiz content WITH answer keys for grading
    quiz_content = await get_quiz_with_cache(quiz_id, exclude_answers=False)

    if not quiz_content or not quiz_content.get("questions"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Quiz content not available yet. Please try again later.",
        )

    # Validate all questions are answered
    expected_question_ids = {q["id"] for q in quiz_content["questions"]}
    submitted_question_ids = set(submission.answers.keys())

    missing_questions = expected_question_ids - submitted_question_ids
    if missing_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing answers for questions: {', '.join(missing_questions)}",
        )

    # Calculate attempt number (only for authenticated users)
    attempt_number = 1
    if current_user:
        result = await db.execute(
            select(func.count(QuizAttempt.id))
            .where(QuizAttempt.user_id == current_user.id)
            .where(QuizAttempt.quiz_id == quiz_id)
        )
        attempt_count = result.scalar() or 0
        attempt_number = attempt_count + 1

    # Grade the quiz
    if current_user:
        logger.info(f"Grading quiz {quiz_id} for user {current_user.id}, attempt {attempt_number}")
    else:
        logger.info(f"Grading quiz {quiz_id} for anonymous user")
    grading_result = grade_quiz(quiz_content, submission.answers)

    # Create QuizAttempt record (only for authenticated users)
    quiz_attempt = None
    if current_user:
        quiz_attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            chapter_id=chapter_id,
            started_at=datetime.utcnow(),  # TODO: Track actual start time
            completed_at=datetime.utcnow(),
            score_percentage=grading_result["score_percentage"],
            total_questions=grading_result["total_questions"],
            correct_answers=grading_result["correct_answers"],
            passed=grading_result["passed"],
            answers=submission.answers,
            attempt_number=attempt_number,
            time_spent_seconds=0,  # TODO: Track actual time spent
        )
        db.add(quiz_attempt)

        # Update ChapterProgress if quiz passed
        if grading_result["passed"]:
            logger.info(f"Quiz passed! Updating chapter progress for {chapter_id}")

            # Record quiz completion as learning activity for streak tracking
            await update_streak(db, current_user.id, current_user.timezone)

            # Get or create chapter progress
            result = await db.execute(
                select(ChapterProgress)
                .where(ChapterProgress.user_id == current_user.id)
                .where(ChapterProgress.chapter_id == chapter_id)
            )
            chapter_progress = result.scalar_one_or_none()

            if not chapter_progress:
                # Create new progress record
                chapter_progress = ChapterProgress(
                    user_id=current_user.id,
                    chapter_id=chapter_id,
                    started_at=datetime.utcnow(),
                    completion_percentage=100,
                    is_completed=True,
                    completed_at=datetime.utcnow(),
                )
                db.add(chapter_progress)
            else:
                # Update existing progress
                if not chapter_progress.is_completed:
                    chapter_progress.is_completed = True
                    chapter_progress.completed_at = datetime.utcnow()
                    chapter_progress.completion_percentage = 100

        await db.commit()
        await db.refresh(quiz_attempt)

        # Check for quiz-related milestones
        new_milestones = await check_quiz_milestones(db, current_user.id, quiz_attempt)

        # Check for chapter completion milestones if quiz passed
        chapter_milestone = None
        if grading_result["passed"]:
            chapter_milestone = await check_chapter_completion_milestones(
                db, current_user.id, chapter_id
            )

        # Log any new milestones
        if new_milestones or chapter_milestone:
            milestone_names = [m.display_name for m in new_milestones]
            if chapter_milestone:
                milestone_names.append(chapter_milestone.display_name)
            logger.info(f"🎉 New milestones achieved for user {current_user.id}: {milestone_names}")

    logger.info(
        f"Quiz submitted: score={grading_result['score_percentage']}%, "
        f"passed={grading_result['passed']}, attempt={attempt_number}"
    )

    # Return graded results
    return {
        "id": str(quiz_attempt.id) if quiz_attempt else None,
        "quiz_id": quiz_id,
        "user_id": str(current_user.id) if current_user else None,
        "chapter_id": chapter_id,
        "attempt_number": attempt_number,
        "score": grading_result["score_percentage"],
        "score_percentage": grading_result["score_percentage"],
        "total_questions": grading_result["total_questions"],
        "correct_answers": grading_result["correct_answers"],
        "passed": grading_result["passed"],
        "passing_score": quiz_meta["passing_score"],
        "grading_details": grading_result["grading_details"],
        "feedback": _generate_feedback(grading_result["score_percentage"], grading_result["passed"]),
        "chapter_completed": grading_result["passed"] if current_user else False,  # Chapter marked complete if quiz passed (only for authenticated users)
        "submitted_at": quiz_attempt.completed_at.isoformat() if quiz_attempt and quiz_attempt.completed_at else None,
    }


def _generate_feedback(score: float, passed: bool) -> str:
    """
    Generate encouraging feedback based on quiz score.

    Args:
        score: Score percentage (0-100)
        passed: Whether student passed

    Returns:
        Feedback message
    """
    if score >= 90:
        return "Excellent work! You've mastered this material."
    elif score >= 80:
        return "Great job! You have a solid understanding of this chapter."
    elif score >= 70:
        return "Good work! You passed the quiz. Review the explanations to strengthen your understanding."
    elif score >= 60:
        return "You're close! Review the material and try again to pass."
    else:
        return "Keep learning! Review the chapter content and try again when you're ready."
