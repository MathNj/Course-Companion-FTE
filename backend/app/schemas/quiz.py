"""
Quiz Schemas

Pydantic schemas for quiz attempts and results.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal


class QuizAttemptBase(BaseModel):
    """Base quiz attempt schema."""

    quiz_id: str = Field(..., max_length=100, description="Quiz identifier (e.g., 'chapter-1-quiz')")
    answers: dict = Field(default_factory=dict, description="User's answers (question_id -> answer mapping)")

    @field_validator("quiz_id")
    @classmethod
    def validate_quiz_id(cls, v: str) -> str:
        """Validate quiz_id format."""
        # Expected format: chapter-N-quiz
        if not v.endswith("-quiz"):
            raise ValueError("quiz_id must end with '-quiz'")
        if not v.startswith("chapter-"):
            raise ValueError("quiz_id must start with 'chapter-'")
        return v


class QuizAttemptCreate(QuizAttemptBase):
    """Schema for creating a quiz attempt."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quiz_id": "chapter-1-quiz",
                "answers": {
                    "q1": "option_a",
                    "q2": "option_c",
                    "q3": "option_b"
                }
            }
        }
    )


class QuizAttemptUpdate(BaseModel):
    """Schema for updating a quiz attempt (usually after grading)."""

    score_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Quiz score percentage (0-100)")
    answers: Optional[dict] = Field(None, description="Updated answers")
    time_spent_seconds: Optional[int] = Field(None, ge=0, description="Time spent on quiz")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score_percentage": 85.5,
                "time_spent_seconds": 600
            }
        }
    )


class QuizAttemptResponse(QuizAttemptBase):
    """Schema for quiz attempt in API responses."""

    id: UUID = Field(..., description="Attempt unique identifier")
    user_id: UUID = Field(..., description="User's unique identifier")
    score_percentage: Optional[Decimal] = Field(None, description="Quiz score percentage (0-100)")
    time_spent_seconds: int = Field(..., description="Time spent on quiz in seconds")
    attempt_number: int = Field(..., description="Attempt number (1, 2, 3, ...)")
    is_passed: bool = Field(..., description="Whether the attempt passed (score >= 70%)")
    started_at: datetime = Field(..., description="When the attempt started")
    completed_at: Optional[datetime] = Field(None, description="When the attempt was completed")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "quiz_id": "chapter-1-quiz",
                "answers": {
                    "q1": "option_a",
                    "q2": "option_c",
                    "q3": "option_b"
                },
                "score_percentage": 85.5,
                "time_spent_seconds": 600,
                "attempt_number": 1,
                "is_passed": True,
                "started_at": "2026-01-24T19:00:00Z",
                "completed_at": "2026-01-24T19:10:00Z",
                "created_at": "2026-01-24T19:00:00Z",
                "updated_at": "2026-01-24T19:10:00Z"
            }
        }
    )


class QuizAttemptSummary(BaseModel):
    """Schema for quiz attempt summary (best score, total attempts, etc.)."""

    quiz_id: str = Field(..., description="Quiz identifier")
    total_attempts: int = Field(..., description="Total number of attempts")
    best_score_percentage: Optional[Decimal] = Field(None, description="Best score achieved")
    latest_score_percentage: Optional[Decimal] = Field(None, description="Most recent score")
    is_passed: bool = Field(..., description="Whether user has passed this quiz (any attempt >= 70%)")
    first_attempt_at: Optional[datetime] = Field(None, description="Timestamp of first attempt")
    last_attempt_at: Optional[datetime] = Field(None, description="Timestamp of last attempt")
    attempts: list[QuizAttemptResponse] = Field(default_factory=list, description="List of all attempts")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quiz_id": "chapter-1-quiz",
                "total_attempts": 2,
                "best_score_percentage": 90.0,
                "latest_score_percentage": 90.0,
                "is_passed": True,
                "first_attempt_at": "2026-01-24T19:00:00Z",
                "last_attempt_at": "2026-01-24T20:00:00Z",
                "attempts": []
            }
        }
    )
