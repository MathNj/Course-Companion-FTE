"""
Quiz Grading Service

Business logic for grading quiz submissions using deterministic rules.
Zero LLM - all grading is rule-based and deterministic.
"""

import logging
from typing import Dict, Any, List, Tuple
from decimal import Decimal

logger = logging.getLogger(__name__)


class GradingResult:
    """Result of grading a single question."""

    def __init__(
        self,
        question_id: str,
        is_correct: bool,
        points_earned: float,
        points_possible: float,
        explanation: str = "",
        student_answer: Any = None,
        correct_answer: Any = None,
    ):
        self.question_id = question_id
        self.is_correct = is_correct
        self.points_earned = points_earned
        self.points_possible = points_possible
        self.explanation = explanation
        self.student_answer = student_answer
        self.correct_answer = correct_answer

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "question_id": self.question_id,
            "is_correct": self.is_correct,
            "points_earned": self.points_earned,
            "points_possible": self.points_possible,
            "explanation": self.explanation,
            "student_answer": self.student_answer,
            "correct_answer": self.correct_answer,
        }


def grade_multiple_choice(
    student_answer: str,
    correct_answer: str,
    explanation_correct: str = "",
    explanation_incorrect: str = "",
) -> Tuple[bool, float, str]:
    """
    Grade a multiple-choice question.

    Uses exact string matching (case-insensitive).

    Args:
        student_answer: Student's selected option
        correct_answer: Correct option
        explanation_correct: Explanation to show when answer is correct
        explanation_incorrect: Explanation to show when answer is incorrect

    Returns:
        Tuple of (is_correct, points_earned, explanation)
    """
    # Normalize both answers (strip whitespace, lowercase)
    student_normalized = str(student_answer).strip().lower()
    correct_normalized = str(correct_answer).strip().lower()

    is_correct = student_normalized == correct_normalized
    points = 1.0 if is_correct else 0.0

    explanation = explanation_correct if is_correct else explanation_incorrect

    logger.debug(
        f"Multiple choice: '{student_answer}' vs '{correct_answer}' = {is_correct}"
    )

    return is_correct, points, explanation


def grade_true_false(
    student_answer: Any,
    correct_answer: bool,
    explanation_correct: str = "",
    explanation_incorrect: str = "",
) -> Tuple[bool, float, str]:
    """
    Grade a true/false question.

    Uses boolean comparison with flexible input handling.

    Args:
        student_answer: Student's answer (bool, "true", "false", 1, 0, etc.)
        correct_answer: Correct boolean value
        explanation_correct: Explanation to show when answer is correct
        explanation_incorrect: Explanation to show when answer is incorrect

    Returns:
        Tuple of (is_correct, points_earned, explanation)
    """
    # Normalize student answer to boolean
    student_bool = _normalize_to_bool(student_answer)

    is_correct = student_bool == correct_answer
    points = 1.0 if is_correct else 0.0

    explanation = explanation_correct if is_correct else explanation_incorrect

    logger.debug(f"True/False: {student_answer} -> {student_bool} vs {correct_answer} = {is_correct}")

    return is_correct, points, explanation


def grade_short_answer(
    student_answer: str,
    keywords: List[str],
    min_keywords: int = 1,
    explanation: str = "",
) -> Tuple[bool, float, str]:
    """
    Grade a short-answer question using keyword matching.

    Partial credit awarded based on number of keywords found.
    Maximum partial credit is 10 points on a 0-10 scale.

    Args:
        student_answer: Student's text response
        keywords: List of required keywords
        min_keywords: Minimum keywords required for any credit
        explanation: Explanation of the correct answer

    Returns:
        Tuple of (is_correct, points_earned, explanation)
    """
    if not keywords:
        logger.warning("No keywords provided for short answer grading")
        return False, 0.0, explanation

    # Normalize student answer
    student_text = str(student_answer).strip().lower()

    # Count keyword matches
    keywords_found = []
    for keyword in keywords:
        keyword_lower = keyword.strip().lower()
        if keyword_lower in student_text:
            keywords_found.append(keyword)

    num_found = len(keywords_found)
    num_total = len(keywords)

    # Calculate partial credit (0-10 scale)
    if num_found < min_keywords:
        points = 0.0
        is_correct = False
    else:
        # Award points proportional to keywords found
        points = (num_found / num_total) * 10.0
        # Consider "correct" if at least min_keywords found
        is_correct = num_found >= min_keywords

    # Build feedback
    feedback = explanation
    if num_found > 0:
        feedback += f"\n\nKeywords found: {', '.join(keywords_found)} ({num_found}/{num_total})"
    else:
        feedback += f"\n\nNo required keywords found. Expected keywords: {', '.join(keywords)}"

    logger.debug(
        f"Short answer: {num_found}/{num_total} keywords found, "
        f"points={points:.1f}, correct={is_correct}"
    )

    return is_correct, points, feedback


def grade_quiz(
    quiz_content: Dict[str, Any],
    student_answers: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Grade a complete quiz submission.

    Iterates through all questions, applies appropriate grading function,
    and calculates overall score percentage.

    Args:
        quiz_content: Full quiz JSON (with answer keys and explanations)
        student_answers: Student's submitted answers (question_id -> answer)

    Returns:
        Dictionary with:
            - score_percentage: Overall score (0-100)
            - total_questions: Number of questions
            - correct_answers: Number of fully correct answers
            - passed: Whether score >= 70%
            - grading_details: List of GradingResult objects
    """
    questions = quiz_content.get("questions", [])
    if not questions:
        logger.error("Quiz has no questions")
        return {
            "score_percentage": 0.0,
            "total_questions": 0,
            "correct_answers": 0,
            "passed": False,
            "grading_details": [],
        }

    grading_results: List[GradingResult] = []
    total_points_earned = 0.0
    total_points_possible = 0.0
    correct_count = 0

    for question in questions:
        question_id = question.get("id")
        question_type = question.get("type")
        student_answer = student_answers.get(question_id)

        # Get answer key and explanations
        correct_answer = question.get("answer_key")
        explanation_correct = question.get("explanation_correct", "")
        explanation_incorrect = question.get("explanation_incorrect", "")
        points_possible = float(question.get("points", 1.0))

        # Helper function to get option text from ID
        def get_option_text(option_id: str) -> str:
            """Convert option ID to option text for display."""
            if not option_id:
                return option_id
            options = question.get("options", [])
            for opt in options:
                if opt.get("id") == option_id:
                    return opt.get("text", option_id)
            return option_id

        # Helper function to format answer for display
        def format_answer_for_display(answer: Any, q_type: str) -> str:
            """Format answer for human-readable display in results."""
            if answer is None:
                return "Not answered"
            if q_type == "true_false":
                return "True" if answer else "False"
            if q_type == "multiple_choice":
                # Option IDs should be converted to text
                return get_option_text(str(answer))
            return str(answer)

        # Handle missing answer
        if student_answer is None:
            formatted_correct = format_answer_for_display(correct_answer, question_type)
            grading_results.append(
                GradingResult(
                    question_id=question_id,
                    is_correct=False,
                    points_earned=0.0,
                    points_possible=points_possible,
                    explanation="No answer provided",
                    student_answer="Not answered",
                    correct_answer=formatted_correct,
                )
            )
            total_points_possible += points_possible
            continue

        # Grade based on question type
        if question_type == "multiple_choice":
            is_correct, points, explanation = grade_multiple_choice(
                student_answer,
                correct_answer,
                explanation_correct,
                explanation_incorrect,
            )
            points_earned = points * points_possible
            # Format answers for display (convert option IDs to text)
            formatted_student = format_answer_for_display(student_answer, question_type)
            formatted_correct = format_answer_for_display(correct_answer, question_type)

        elif question_type == "true_false":
            is_correct, points, explanation = grade_true_false(
                student_answer,
                correct_answer,
                explanation_correct,
                explanation_incorrect,
            )
            points_earned = points * points_possible
            # Format answers for display
            formatted_student = format_answer_for_display(student_answer, question_type)
            formatted_correct = format_answer_for_display(correct_answer, question_type)

        elif question_type == "short_answer":
            keywords = question.get("keywords", [])
            min_keywords = question.get("min_keywords", 1)
            explanation_text = question.get("explanation", "")

            is_correct, points, explanation = grade_short_answer(
                student_answer,
                keywords,
                min_keywords,
                explanation_text,
            )
            # Short answer already returns 0-10 points, normalize to points_possible
            points_earned = (points / 10.0) * points_possible
            # For short answer, show the actual text
            formatted_student = str(student_answer)
            formatted_correct = "See explanation"

        else:
            logger.warning(f"Unknown question type: {question_type}")
            grading_results.append(
                GradingResult(
                    question_id=question_id,
                    is_correct=False,
                    points_earned=0.0,
                    points_possible=points_possible,
                    explanation=f"Unknown question type: {question_type}",
                    student_answer=str(student_answer),
                    correct_answer=format_answer_for_display(correct_answer, question_type),
                )
            )
            total_points_possible += points_possible
            continue

        # Track results
        grading_results.append(
            GradingResult(
                question_id=question_id,
                is_correct=is_correct,
                points_earned=points_earned,
                points_possible=points_possible,
                explanation=explanation,
                student_answer=formatted_student,
                correct_answer=formatted_correct,
            )
        )

        total_points_earned += points_earned
        total_points_possible += points_possible

        if is_correct:
            correct_count += 1

    # Calculate score percentage
    score_percentage = (
        (total_points_earned / total_points_possible * 100.0)
        if total_points_possible > 0
        else 0.0
    )

    passed = score_percentage >= 70.0

    logger.info(
        f"Quiz graded: {correct_count}/{len(questions)} correct, "
        f"score={score_percentage:.2f}%, passed={passed}"
    )

    return {
        "score_percentage": round(score_percentage, 2),
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "passed": passed,
        "grading_details": [result.to_dict() for result in grading_results],
    }


def _normalize_to_bool(value: Any) -> bool:
    """
    Normalize various input types to boolean.

    Handles: bool, int (0/1), str ("true"/"false"/"yes"/"no"/etc.)

    Args:
        value: Input value to normalize

    Returns:
        Boolean value

    Raises:
        ValueError: If value cannot be normalized to bool
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value == 0:
            return False
        if value == 1:
            return True
        raise ValueError(f"Integer {value} cannot be normalized to bool (must be 0 or 1)")

    if isinstance(value, str):
        value_lower = value.strip().lower()
        if value_lower in ("true", "yes", "y", "1", "t"):
            return True
        if value_lower in ("false", "no", "n", "0", "f"):
            return False
        raise ValueError(f"String '{value}' cannot be normalized to bool")

    raise ValueError(f"Type {type(value).__name__} cannot be normalized to bool")
