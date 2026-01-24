"""
Tests for Quiz Grading Service

Validates deterministic grading logic for all question types.
"""

import pytest
from app.services.quiz_grader import (
    grade_multiple_choice,
    grade_true_false,
    grade_short_answer,
    grade_quiz,
)


class TestMultipleChoice:
    """Tests for multiple choice grading."""

    def test_grade_multiple_choice_correct(self):
        """Test correct answer gives full points."""
        is_correct, points, explanation = grade_multiple_choice(
            student_answer="option_a",
            correct_answer="option_a",
            explanation_correct="Correct!",
            explanation_incorrect="Wrong",
        )

        assert is_correct is True
        assert points == 1.0
        assert explanation == "Correct!"

    def test_grade_multiple_choice_incorrect(self):
        """Test incorrect answer gives zero points."""
        is_correct, points, explanation = grade_multiple_choice(
            student_answer="option_b",
            correct_answer="option_a",
            explanation_correct="Correct!",
            explanation_incorrect="Wrong",
        )

        assert is_correct is False
        assert points == 0.0
        assert explanation == "Wrong"

    def test_grade_multiple_choice_case_insensitive(self):
        """Test grading is case-insensitive."""
        is_correct, points, _ = grade_multiple_choice(
            student_answer="OPTION_A",
            correct_answer="option_a",
        )

        assert is_correct is True
        assert points == 1.0

    def test_grade_multiple_choice_whitespace_handling(self):
        """Test whitespace is stripped."""
        is_correct, points, _ = grade_multiple_choice(
            student_answer="  option_a  ",
            correct_answer="option_a",
        )

        assert is_correct is True
        assert points == 1.0


class TestTrueFalse:
    """Tests for true/false grading."""

    def test_grade_true_false_correct_bool(self):
        """Test correct boolean answer."""
        is_correct, points, _ = grade_true_false(
            student_answer=True,
            correct_answer=True,
        )

        assert is_correct is True
        assert points == 1.0

    def test_grade_true_false_incorrect_bool(self):
        """Test incorrect boolean answer."""
        is_correct, points, _ = grade_true_false(
            student_answer=False,
            correct_answer=True,
        )

        assert is_correct is False
        assert points == 0.0

    def test_grade_true_false_string_true(self):
        """Test string 'true' is normalized to boolean."""
        is_correct, points, _ = grade_true_false(
            student_answer="true",
            correct_answer=True,
        )

        assert is_correct is True
        assert points == 1.0

    def test_grade_true_false_string_false(self):
        """Test string 'false' is normalized to boolean."""
        is_correct, points, _ = grade_true_false(
            student_answer="false",
            correct_answer=False,
        )

        assert is_correct is True
        assert points == 1.0

    def test_grade_true_false_integer_1(self):
        """Test integer 1 is normalized to True."""
        is_correct, points, _ = grade_true_false(
            student_answer=1,
            correct_answer=True,
        )

        assert is_correct is True
        assert points == 1.0

    def test_grade_true_false_integer_0(self):
        """Test integer 0 is normalized to False."""
        is_correct, points, _ = grade_true_false(
            student_answer=0,
            correct_answer=False,
        )

        assert is_correct is True
        assert points == 1.0


class TestShortAnswer:
    """Tests for short answer grading with keyword matching."""

    def test_grade_short_answer_all_keywords(self):
        """Test full credit when all keywords found."""
        is_correct, points, explanation = grade_short_answer(
            student_answer="Generative AI uses neural networks to create new content",
            keywords=["generative", "neural networks", "content"],
            min_keywords=2,
        )

        assert is_correct is True
        assert points == 10.0  # All 3/3 keywords = 10 points
        assert "3/3" in explanation

    def test_grade_short_answer_partial_credit(self):
        """Test partial credit when some keywords found."""
        is_correct, points, explanation = grade_short_answer(
            student_answer="Generative AI creates content",
            keywords=["generative", "neural networks", "content"],
            min_keywords=2,
        )

        assert is_correct is True  # 2 keywords meets minimum
        assert points == pytest.approx(6.67, abs=0.01)  # 2/3 * 10 = 6.67
        assert "2/3" in explanation

    def test_grade_short_answer_below_minimum(self):
        """Test zero points when below minimum keywords."""
        is_correct, points, explanation = grade_short_answer(
            student_answer="AI is interesting",
            keywords=["generative", "neural networks", "content"],
            min_keywords=2,
        )

        assert is_correct is False
        assert points == 0.0
        assert "No required keywords found" in explanation

    def test_grade_short_answer_case_insensitive(self):
        """Test keyword matching is case-insensitive."""
        is_correct, points, _ = grade_short_answer(
            student_answer="GENERATIVE AI and NEURAL NETWORKS",
            keywords=["generative", "neural networks"],
            min_keywords=1,
        )

        assert is_correct is True
        assert points == 10.0


class TestQuizGrading:
    """Tests for full quiz grading."""

    def test_grade_quiz_all_correct(self):
        """Test quiz with all correct answers."""
        quiz_content = {
            "questions": [
                {
                    "id": "q1",
                    "type": "multiple_choice",
                    "answer_key": "option_a",
                    "points": 1.0,
                    "explanation_correct": "Correct!",
                    "explanation_incorrect": "Wrong",
                },
                {
                    "id": "q2",
                    "type": "true_false",
                    "answer_key": True,
                    "points": 1.0,
                    "explanation_correct": "Yes!",
                    "explanation_incorrect": "No",
                },
            ]
        }

        student_answers = {
            "q1": "option_a",
            "q2": True,
        }

        result = grade_quiz(quiz_content, student_answers)

        assert result["score_percentage"] == 100.0
        assert result["total_questions"] == 2
        assert result["correct_answers"] == 2
        assert result["passed"] is True
        assert len(result["grading_details"]) == 2

    def test_grade_quiz_partial_score(self):
        """Test quiz with some incorrect answers."""
        quiz_content = {
            "questions": [
                {
                    "id": "q1",
                    "type": "multiple_choice",
                    "answer_key": "option_a",
                    "points": 1.0,
                },
                {
                    "id": "q2",
                    "type": "multiple_choice",
                    "answer_key": "option_b",
                    "points": 1.0,
                },
            ]
        }

        student_answers = {
            "q1": "option_a",  # Correct
            "q2": "option_c",  # Incorrect
        }

        result = grade_quiz(quiz_content, student_answers)

        assert result["score_percentage"] == 50.0
        assert result["total_questions"] == 2
        assert result["correct_answers"] == 1
        assert result["passed"] is False  # 50% < 70%

    def test_grade_quiz_passing_threshold(self):
        """Test quiz at exactly 70% passing threshold."""
        quiz_content = {
            "questions": [
                {"id": f"q{i}", "type": "multiple_choice", "answer_key": "a", "points": 1.0}
                for i in range(10)
            ]
        }

        # 7 correct, 3 incorrect = 70%
        student_answers = {f"q{i}": "a" if i < 7 else "b" for i in range(10)}

        result = grade_quiz(quiz_content, student_answers)

        assert result["score_percentage"] == 70.0
        assert result["passed"] is True

    def test_grade_quiz_missing_answers(self):
        """Test quiz with unanswered questions."""
        quiz_content = {
            "questions": [
                {"id": "q1", "type": "multiple_choice", "answer_key": "a", "points": 1.0},
                {"id": "q2", "type": "multiple_choice", "answer_key": "b", "points": 1.0},
            ]
        }

        student_answers = {
            "q1": "a",  # Answered correctly
            # q2 not answered
        }

        result = grade_quiz(quiz_content, student_answers)

        assert result["score_percentage"] == 50.0
        assert result["total_questions"] == 2
        assert result["correct_answers"] == 1
        assert result["grading_details"][1]["explanation"] == "No answer provided"

    def test_grade_quiz_deterministic(self):
        """Test that grading is deterministic (same inputs = same outputs)."""
        quiz_content = {
            "questions": [
                {"id": "q1", "type": "multiple_choice", "answer_key": "option_a", "points": 1.0},
            ]
        }

        student_answers = {"q1": "option_a"}

        result1 = grade_quiz(quiz_content, student_answers)
        result2 = grade_quiz(quiz_content, student_answers)

        assert result1["score_percentage"] == result2["score_percentage"]
        assert result1["correct_answers"] == result2["correct_answers"]
        assert result1["passed"] == result2["passed"]
