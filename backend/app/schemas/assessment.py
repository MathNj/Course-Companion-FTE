"""
Phase 2 Schemas: LLM-Graded Assessments

Request and response models for assessment submission and feedback endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class AssessmentSubmitRequest(BaseModel):
    """Request to submit open-ended answer for grading."""

    question_id: str = Field(..., description="Question identifier (e.g., '04-rag-q1')")
    answer_text: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Student's answer (50-5000 characters)"
    )

    @field_validator('answer_text')
    @classmethod
    def validate_word_count(cls, v):
        """Ensure answer is 50-500 words (approximately 250-5000 chars)."""
        word_count = len(v.split())
        if word_count < 10 or word_count > 500:
            raise ValueError('Answer must be between 10 and 500 words')
        return v


class AssessmentSubmitResponse(BaseModel):
    """Response confirming assessment submission."""

    submission_id: str
    student_id: str
    question_id: str
    submitted_at: datetime
    grading_status: str
    estimated_completion_seconds: int
    feedback_url: str


class AssessmentFeedbackMetadata(BaseModel):
    """Metadata about LLM grading."""

    tokens_used: dict = Field(..., description="Token counts (input, output, total)")
    cost_usd: float
    latency_ms: int
    llm_model: str


class AssessmentFeedbackResponse(BaseModel):
    """Response containing graded assessment feedback."""

    feedback_id: str
    submission_id: str
    quality_score: float = Field(..., ge=0.0, le=10.0)

    strengths: List[str]
    improvements: List[str]
    detailed_feedback: str

    metadata: AssessmentFeedbackMetadata

    is_off_topic: bool = False


class RubricScore(BaseModel):
    """Individual rubric criterion score."""

    criterion: str
    max_points: int
    score: float


class DetailedAssessmentFeedback(AssessmentFeedbackResponse):
    """Extended feedback with rubric breakdown."""

    rubric_scores: List[RubricScore] = Field(default_factory=list)
