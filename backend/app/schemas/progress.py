"""
Progress Schemas

Pydantic schemas for tracking chapter progress.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ChapterProgressBase(BaseModel):
    """Base chapter progress schema."""

    chapter_id: str = Field(..., max_length=50, description="Chapter identifier (e.g., 'chapter-1')")
    completion_percentage: int = Field(default=0, ge=0, le=100, description="Completion percentage (0-100)")
    time_spent_seconds: int = Field(default=0, ge=0, description="Time spent on chapter in seconds")

    @field_validator("chapter_id")
    @classmethod
    def validate_chapter_id(cls, v: str) -> str:
        """Validate chapter_id format."""
        # Expected format: chapter-1, chapter-2, etc.
        if not v.startswith("chapter-"):
            raise ValueError("chapter_id must start with 'chapter-'")
        try:
            chapter_num = int(v.split("-")[1])
            if not (1 <= chapter_num <= 6):
                raise ValueError("chapter number must be between 1 and 6")
        except (IndexError, ValueError):
            raise ValueError("Invalid chapter_id format. Expected: 'chapter-N' where N is 1-6")
        return v


class ChapterProgressCreate(ChapterProgressBase):
    """Schema for creating chapter progress record."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chapter_id": "chapter-1",
                "completion_percentage": 0,
                "time_spent_seconds": 0
            }
        }
    )


class ChapterProgressUpdate(BaseModel):
    """Schema for updating chapter progress."""

    completion_percentage: Optional[int] = Field(None, ge=0, le=100, description="Updated completion percentage")
    time_spent_seconds: Optional[int] = Field(None, ge=0, description="Additional time spent in seconds")
    is_completed: Optional[bool] = Field(None, description="Mark chapter as completed")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "completion_percentage": 75,
                "time_spent_seconds": 3600,
                "is_completed": False
            }
        }
    )


class ChapterProgressResponse(ChapterProgressBase):
    """Schema for chapter progress in API responses."""

    id: UUID = Field(..., description="Progress record unique identifier")
    user_id: UUID = Field(..., description="User's unique identifier")
    started_at: datetime = Field(..., description="When the user started this chapter")
    completed_at: Optional[datetime] = Field(None, description="When the user completed this chapter")
    is_completed: bool = Field(..., description="Whether the chapter is completed")
    last_accessed_at: Optional[datetime] = Field(None, description="Last time user accessed this chapter")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "chapter_id": "chapter-1",
                "completion_percentage": 75,
                "time_spent_seconds": 3600,
                "started_at": "2026-01-20T10:00:00Z",
                "completed_at": None,
                "is_completed": False,
                "last_accessed_at": "2026-01-24T19:30:00Z",
                "created_at": "2026-01-20T10:00:00Z",
                "updated_at": "2026-01-24T19:30:00Z"
            }
        }
    )


class ChapterProgressSummary(BaseModel):
    """Schema for overall progress summary across all chapters."""

    total_chapters: int = Field(..., description="Total number of chapters in the course")
    completed_chapters: int = Field(..., description="Number of completed chapters")
    in_progress_chapters: int = Field(..., description="Number of chapters in progress")
    not_started_chapters: int = Field(..., description="Number of chapters not started")
    overall_completion_percentage: int = Field(..., ge=0, le=100, description="Overall course completion percentage")
    total_time_spent_seconds: int = Field(..., description="Total time spent across all chapters")
    chapters: list[ChapterProgressResponse] = Field(..., description="List of all chapter progress records")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_chapters": 6,
                "completed_chapters": 2,
                "in_progress_chapters": 1,
                "not_started_chapters": 3,
                "overall_completion_percentage": 45,
                "total_time_spent_seconds": 10800,
                "chapters": []
            }
        }
    )
