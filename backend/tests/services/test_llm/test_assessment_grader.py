"""
Unit tests for AssessmentGrader service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from app.services.llm.assessment_grader import AssessmentGrader
from app.models.llm import AssessmentSubmission, AssessmentSubmissionStatus
from app.models.user import User


@pytest.mark.asyncio
class TestAssessmentGrader:
    """Unit tests for assessment grading service."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_user(self):
        """Mock user."""
        user = MagicMock(spec=User)
        user.id = "test-user-123"
        return user

    @pytest.fixture
    def sample_submission(self, mock_user):
        """Create sample assessment submission."""
        submission = MagicMock(spec=AssessmentSubmission)
        submission.submission_id = "test-submission-123"
        submission.student_id = mock_user.id
        submission.question_id = "04-rag-q1"
        submission.answer_text = (
            "RAG combines retrieval systems with LLMs by fetching relevant context "
            "before generation, while fine-tuning updates model weights on training data. "
            "I'd choose RAG when accuracy on specific documents is critical but the model "
            "has general reasoning capabilities - it's cheaper, more maintainable, and "
            "reduces hallucinations. For example, customer support bots benefit from RAG's "
            "ability to cite exact policy documents. Fine-tuning is better when domain-specific "
            "patterns or writing styles need to be learned, like medical terminology or code "
            "style guides. However, fine-tuning costs $10-100K in compute and requires weekly "
            "retraining as documents change, whereas RAG simply updates the vector database."
        )
        submission.previous_submission_id = None
        submission.attempt_number = 1
        submission.grading_status = AssessmentSubmissionStatus.PENDING
        return submission

    @pytest.fixture
    def sample_rubric(self):
        """Sample rubric data."""
        return {
            "question_id": "04-rag-q1",
            "question_text": "Compare and contrast RAG versus fine-tuning.",
            "evaluation_criteria": [
                "Understanding of RAG architecture",
                "Understanding of fine-tuning",
                "Comparison of tradeoffs",
                "Real-world use cases"
            ],
            "example_excellent_answer": "Excellent answer...",
            "example_poor_answer": "Poor answer..."
        }

    @pytest.mark.asyncio
    async def test_load_rubric_from_r2(self, mock_db, sample_rubric):
        """Test loading rubric from R2 storage."""
        grader = AssessmentGrader(mock_db)

        # Mock R2 client
        with patch.object(grader.r2_client, 'get_file') as mock_get_file:
            mock_get_file.return_value = json.dumps({
                "chapter_id": "04-rag",
                "questions": [sample_rubric]
            })

            rubric = await grader.load_rubric("04-rag-q1")

            assert rubric["question_id"] == "04-rag-q1"
            assert "evaluation_criteria" in rubric
            mock_get_file.assert_called_once_with("assessments/04-rag-assessments.json")

    @pytest.mark.asyncio
    async def test_load_rubric_caches_result(self, mock_db, sample_rubric):
        """Test that rubric loading caches results."""
        grader = AssessmentGrader(mock_db)

        with patch.object(grader.r2_client, 'get_file') as mock_get_file:
            mock_get_file.return_value = json.dumps({
                "chapter_id": "04-rag",
                "questions": [sample_rubric]
            })

            # First call
            await grader.load_rubric("04-rag-q1")
            # Second call should use cache
            await grader.load_rubric("04-rag-q1")

            # Should only call R2 once
            mock_get_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_format_prompt(self, mock_db):
        """Test prompt formatting."""
        grader = AssessmentGrader(mock_db)

        system_prompt, user_prompt = grader._format_prompt(
            question_text="What is RAG?",
            evaluation_criteria=["Accuracy", "Depth"],
            answer_text="RAG is retrieval-augmented generation.",
            example_excellent="Excellent answer with details.",
            example_poor="Poor answer."
        )

        assert "You are an expert evaluator" in system_prompt
        assert "What is RAG?" in user_prompt
        assert "RAG is retrieval-augmented generation." in user_prompt
        assert "Excellent answer with details." in user_prompt
        assert "Poor answer." in user_prompt

    @pytest.mark.asyncio
    async def test_detect_off_topic_low_overlap(self, mock_db):
        """Test off-topic detection with low keyword overlap."""
        grader = AssessmentGrader(mock_db)

        question = "Compare RAG and fine-tuning architectures for domain applications."
        answer = "I like pizza and playing video games."  # Completely off-topic

        is_off_topic = await grader._detect_off_topic(question, answer)

        assert is_off_topic is True

    @pytest.mark.asyncio
    async def test_detect_off_topic_high_overlap(self, mock_db):
        """Test off-topic detection with high keyword overlap."""
        grader = AssessmentGrader(mock_db)

        question = "Compare RAG and fine-tuning architectures for domain applications."
        answer = "RAG and fine-tuning are both approaches for domain applications with different tradeoffs."

        is_off_topic = await grader._detect_off_topic(question, answer)

        assert is_off_topic is False

    @pytest.mark.asyncio
    async def test_grade_submission_success(self, mock_db, sample_submission, sample_rubric):
        """Test successful grading flow."""
        grader = AssessmentGrader(mock_db)

        # Mock dependencies
        with patch.object(grader, 'load_rubric', return_value=sample_rubric), \
             patch.object(grader, '_detect_off_topic', return_value=False), \
             patch.object(grader.llm_client, 'create_message') as mock_llm, \
             patch.object(grader.cost_tracker, 'calculate_cost', return_value=0.001), \
             patch.object(grader.cost_tracker, 'log_usage'):

            # Mock LLM response
            mock_llm.return_value = {
                "content": json.dumps({
                    "quality_score": 8.5,
                    "strengths": [
                        "Good comparison of RAG and fine-tuning",
                        "Included concrete examples",
                        "Discussed cost implications"
                    ],
                    "improvements": [
                        "Could expand on hybrid approaches",
                        "Add more quantitative details"
                    ],
                    "detailed_feedback": "This is a strong answer demonstrating solid understanding of RAG versus fine-tuning. You provided good concrete examples and discussed the cost tradeoffs effectively. To improve, consider expanding on hybrid approaches and adding more quantitative details about performance metrics.",
                    "is_off_topic": False
                }),
                "usage": {
                    "prompt_tokens": 800,
                    "completion_tokens": 200
                }
            }

            feedback = await grader.grade_submission(sample_submission)

            assert feedback.quality_score == 8.5
            assert len(feedback.strengths_json) == 3
            assert len(feedback.improvements_json) == 2
            assert feedback.is_off_topic is False

            # Verify LLM was called
            mock_llm.assert_called_once()

            # Verify usage was logged
            grader.cost_tracker.log_usage.assert_called_once()

    @pytest.mark.asyncio
    async def test_grade_submission_off_topic(self, mock_db, sample_submission, sample_rubric):
        """Test grading of off-topic submission."""
        grader = AssessmentGrader(mock_db)

        with patch.object(grader, 'load_rubric', return_value=sample_rubric), \
             patch.object(grader, '_detect_off_topic', return_value=True):

            feedback = await grader.grade_submission(sample_submission)

            assert feedback.quality_score == 0.0
            assert feedback.is_off_topic is True
            assert len(feedback.improvements_json) > 0

    @pytest.mark.asyncio
    async def test_validate_feedback_schema_valid(self, mock_db):
        """Test feedback schema validation with valid data."""
        grader = AssessmentGrader(mock_db)

        valid_feedback = {
            "quality_score": 8.5,
            "strengths": ["Strength 1", "Strength 2", "Strength 3"],
            "improvements": ["Improvement 1", "Improvement 2"],
            "detailed_feedback": "This is a detailed feedback message that is at least 50 characters long.",
            "is_off_topic": False
        }

        # Should not raise
        grader._validate_feedback_schema(valid_feedback)

    @pytest.mark.asyncio
    async def test_validate_feedback_schema_missing_field(self, mock_db):
        """Test feedback schema validation with missing field."""
        grader = AssessmentGrader(mock_db)

        invalid_feedback = {
            "quality_score": 8.5,
            "strengths": ["Strength 1"],
            # Missing 'improvements'
            "detailed_feedback": "Feedback",
            "is_off_topic": False
        }

        with pytest.raises(ValueError, match="Missing required field"):
            grader._validate_feedback_schema(invalid_feedback)

    @pytest.mark.asyncio
    async def test_validate_feedback_schema_invalid_score(self, mock_db):
        """Test feedback schema validation with invalid score."""
        grader = AssessmentGrader(mock_db)

        invalid_feedback = {
            "quality_score": 15.0,  # Out of range
            "strengths": ["Strength 1"],
            "improvements": ["Improvement 1"],
            "detailed_feedback": "This is a detailed feedback message that is at least 50 characters long.",
            "is_off_topic": False
        }

        with pytest.raises(ValueError, match="quality_score must be between 0.0 and 10.0"):
            grader._validate_feedback_schema(invalid_feedback)

    @pytest.mark.asyncio
    async def test_validate_feedback_schema_too_few_strengths(self, mock_db):
        """Test feedback schema validation with too few strengths."""
        grader = AssessmentGrader(mock_db)

        invalid_feedback = {
            "quality_score": 8.5,
            "strengths": [],  # Empty array
            "improvements": ["Improvement 1"],
            "detailed_feedback": "This is a detailed feedback message that is at least 50 characters long.",
            "is_off_topic": False
        }

        with pytest.raises(ValueError, match="strengths must be an array with 1-5 items"):
            grader._validate_feedback_schema(invalid_feedback)

    @pytest.mark.asyncio
    async def test_validate_feedback_schema_short_detailed_feedback(self, mock_db):
        """Test feedback schema validation with short detailed feedback."""
        grader = AssessmentGrader(mock_db)

        invalid_feedback = {
            "quality_score": 8.5,
            "strengths": ["Strength 1"],
            "improvements": ["Improvement 1"],
            "detailed_feedback": "Short",  # Too short
            "is_off_topic": False
        }

        with pytest.raises(ValueError, match="detailed_feedback must be at least 50 characters"):
            grader._validate_feedback_schema(invalid_feedback)
