"""
Assessment Grader Service

Grades open-ended assessment submissions using OpenAI GPT-4o-mini.
Loads rubrics from R2, formats prompts, validates feedback, and detects off-topic answers.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.services.llm.client import get_openai_client
from app.services.llm.cost_tracker import CostTracker
from app.models.llm import AssessmentSubmission, AssessmentFeedback
from app.models.user import User
from app.utils.storage import R2StorageClient

logger = logging.getLogger(__name__)


class AssessmentGrader:
    """
    Grades student assessment submissions using LLM.

    Workflow:
    1. Load question and rubric from R2
    2. Format prompt with question, rubric, and student answer
    3. Call OpenAI GPT-4o-mini with JSON mode
    4. Validate and parse feedback
    5. Store feedback in database
    6. Log cost and usage
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_client = get_openai_client()
        self.cost_tracker = CostTracker()
        self.r2_client = R2StorageClient()
        self._rubric_cache = {}  # In-memory cache (TODO: Redis)

    async def load_rubric(
        self,
        question_id: str
    ) -> Dict[str, Any]:
        """
        Load assessment question and rubric from R2.

        Args:
            question_id: Question identifier (e.g., '04-rag-q1')

        Returns:
            Question data with text, evaluation criteria, and examples

        Raises:
            ValueError: If question not found
        """
        # Check cache first
        if question_id in self._rubric_cache:
            logger.debug(f"Rubric cache hit for {question_id}")
            return self._rubric_cache[question_id]

        # Extract chapter_id from question_id
        chapter_id = question_id.split('-')[0] + '-' + question_id.split('-')[1]
        rubric_file = f"{chapter_id}-assessments.json"

        try:
            # Fetch from R2
            rubric_content = self.r2_client.get_file(
                f"assessments/{rubric_file}"
            )
            rubric_data = json.loads(rubric_content)

            # Find the specific question
            questions = rubric_data.get("questions", [])
            question_data = None
            for q in questions:
                if q["question_id"] == question_id:
                    question_data = q
                    break

            if not question_data:
                raise ValueError(f"Question {question_id} not found in {rubric_file}")

            # Cache for 1 hour (in production, use Redis with TTL)
            self._rubric_cache[question_id] = question_data

            return question_data

        except Exception as e:
            logger.error(f"Failed to load rubric for {question_id}: {e}")
            raise ValueError(f"Could not load assessment question: {str(e)}")

    def _format_prompt(
        self,
        question_text: str,
        evaluation_criteria: List[str],
        answer_text: str,
        example_excellent: str,
        example_poor: str
    ) -> tuple[str, str]:
        """
        Format the grading prompt.

        Returns:
            (system_prompt, user_prompt)
        """
        # Load system prompt template
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "assessment_grading.txt"
        with open(prompt_path, "r") as f:
            system_prompt = f.read()

        # Format evaluation criteria for display
        criteria_formatted = "\n".join([
            f"{i+1}. {criterion}"
            for i, criterion in enumerate(evaluation_criteria)
        ])

        # Format user prompt
        user_prompt = f"""Grade this student submission.

Question: {question_text}

Evaluation Criteria:
{criteria_formatted}

Student Answer:
{answer_text}

Reference Excellent Answer (for calibration):
{example_excellent}

Reference Poor Answer (for calibration):
{example_poor}

Provide grading feedback in JSON format."""

        return system_prompt, user_prompt

    async def _detect_off_topic(
        self,
        question_text: str,
        answer_text: str
    ) -> bool:
        """
        Detect if answer is off-topic using keyword overlap.

        A simple heuristic: Extract keywords from question (technical terms),
        check if at least 20% appear in the answer.

        Args:
            question_text: The question being asked
            answer_text: The student's answer

        Returns:
            True if off-topic (less than 20% keyword overlap)
        """
        # Extract potential keywords (words > 5 chars in question)
        question_words = set(
            w.lower() for w in question_text.split()
            if len(w) > 5 and w.isalpha()
        )

        if not question_words:
            return False  # Can't determine, assume on-topic

        # Check overlap in answer
        answer_lower = answer_text.lower()
        overlap_count = sum(1 for word in question_words if word in answer_lower)
        overlap_ratio = overlap_count / len(question_words)

        is_off_topic = overlap_ratio < 0.20

        if is_off_topic:
            logger.warning(
                f"Off-topic detected: {overlap_ratio:.1%} keyword overlap "
                f"({overlap_count}/{len(question_words)} keywords)"
            )

        return is_off_topic

    async def grade_submission(
        self,
        submission: AssessmentSubmission
    ) -> AssessmentFeedback:
        """
        Grade an assessment submission using LLM.

        Args:
            submission: AssessmentSubmission database object

        Returns:
            AssessmentFeedback object with graded results

        Raises:
            ValueError: If submission is invalid or question not found
        """
        logger.info(f"Grading submission {submission.submission_id}")

        # Step 1: Load rubric
        question_data = await self.load_rubric(submission.question_id)

        # Step 2: Check for off-topic
        is_off_topic = await self._detect_off_topic(
            question_data["question_text"],
            submission.answer_text
        )

        if is_off_topic:
            logger.warning(f"Submission {submission.submission_id} is off-topic")
            # Return zero-score feedback
            return await self._create_off_topic_feedback(submission)

        # Step 3: Format prompt
        system_prompt, user_prompt = self._format_prompt(
            question_text=question_data["question_text"],
            evaluation_criteria=question_data["evaluation_criteria"],
            answer_text=submission.answer_text,
            example_excellent=question_data["example_excellent_answer"],
            example_poor=question_data["example_poor_answer"]
        )

        # Step 4: Call LLM
        start_time = datetime.utcnow()

        try:
            response = await self.llm_client.create_message(
                system_prompt=system_prompt,
                user_message=user_prompt,
                max_tokens=1500,
                temperature=0.4,  # Lower temperature for consistent grading
                response_format={"type": "json_object"}
            )

            latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Step 5: Parse and validate feedback
            feedback_data = json.loads(response["content"])

            # Validate required fields
            self._validate_feedback_schema(feedback_data)

            # Step 6: Create AssessmentFeedback record
            feedback = AssessmentFeedback(
                submission_id=submission.submission_id,
                quality_score=float(feedback_data["quality_score"]),
                strengths_json=feedback_data["strengths"],
                improvements_json=feedback_data["improvements"],
                detailed_feedback=feedback_data["detailed_feedback"],
                is_off_topic=feedback_data.get("is_off_topic", False),
                generated_at=datetime.utcnow(),
                tokens_input=response["usage"]["prompt_tokens"],
                tokens_output=response["usage"]["completion_tokens"],
                cost_usd=self.cost_tracker.calculate_cost(
                    response["usage"]["prompt_tokens"],
                    response["usage"]["completion_tokens"]
                )
            )

            self.db.add(feedback)

            # Step 7: Log usage
            await self.cost_tracker.log_usage(
                db=self.db,
                student_id=submission.student_id,
                feature="assessment",
                reference_id=submission.submission_id,
                model_version=self.llm_client.model,
                tokens_input=response["usage"]["prompt_tokens"],
                tokens_output=response["usage"]["completion_tokens"],
                cost_usd=feedback.cost_usd,
                latency_ms=latency_ms,
                success=True
            )

            await self.db.commit()
            await self.db.refresh(feedback)

            logger.info(
                f"Graded submission {submission.submission_id}: "
                f"score={feedback.quality_score:.1f}, "
                f"cost=${feedback.cost_usd:.6f}, "
                f"latency={latency_ms}ms"
            )

            return feedback

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ValueError("LLM returned invalid JSON feedback")

        except Exception as e:
            logger.error(f"Grading failed for {submission.submission_id}: {e}")
            # Log failed attempt
            await self.cost_tracker.log_usage(
                db=self.db,
                student_id=submission.student_id,
                feature="assessment",
                reference_id=submission.submission_id,
                model_version=self.llm_client.model,
                tokens_input=0,
                tokens_output=0,
                cost_usd=0.0,
                latency_ms=0,
                success=False,
                error_code=str(type(e).__name__),
                error_message=str(e)
            )
            raise

    async def _create_off_topic_feedback(
        self,
        submission: AssessmentSubmission
    ) -> AssessmentFeedback:
        """Create zero-score feedback for off-topic submissions."""
        feedback = AssessmentFeedback(
            submission_id=submission.submission_id,
            quality_score=0.0,
            strengths_json=[],
            improvements_json=[
                "Your answer appears to be off-topic or unrelated to the question asked.",
                "Please read the question carefully and ensure you're addressing the specific topic.",
                "Review the course material related to this question before resubmitting.",
                "If you believe this is an error, please contact support."
            ],
            detailed_feedback=(
                "Your submission does not appear to address the question asked. "
                "Please review the question and course materials, then submit an answer "
                "that directly responds to what was asked. You may resubmit up to 3 times."
            ),
            is_off_topic=True,
            generated_at=datetime.utcnow(),
            tokens_input=0,
            tokens_output=0,
            cost_usd=0.0
        )

        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)

        return feedback

    def _validate_feedback_schema(self, feedback_data: Dict[str, Any]) -> None:
        """
        Validate LLM feedback has required schema.

        Args:
            feedback_data: Parsed JSON from LLM

        Raises:
            ValueError: If schema is invalid
        """
        required_fields = [
            "quality_score",
            "strengths",
            "improvements",
            "detailed_feedback",
            "is_off_topic"
        ]

        for field in required_fields:
            if field not in feedback_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate score range
        score = feedback_data["quality_score"]
        if not isinstance(score, (int, float)) or not (0.0 <= score <= 10.0):
            raise ValueError(f"quality_score must be between 0.0 and 10.0, got {score}")

        # Validate arrays
        strengths = feedback_data["strengths"]
        improvements = feedback_data["improvements"]

        if not isinstance(strengths, list) or not (1 <= len(strengths) <= 5):
            raise ValueError("strengths must be an array with 1-5 items")

        if not isinstance(improvements, list) or not (1 <= len(improvements) <= 5):
            raise ValueError("improvements must be an array with 1-5 items")

        # Validate detailed_feedback length
        detailed = feedback_data["detailed_feedback"]
        if not isinstance(detailed, str) or len(detailed) < 50:
            raise ValueError("detailed_feedback must be at least 50 characters")

        logger.debug("Feedback schema validation passed")
