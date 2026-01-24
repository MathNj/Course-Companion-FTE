"""
Progress Tracking Models

Tracks student progress through course content.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP, Integer, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ChapterProgress(Base, TimestampMixin):
    """
    Tracks student progress for each chapter.

    Attributes:
        id: Unique progress record identifier
        user_id: Foreign key to User
        chapter_id: Chapter identifier (e.g., '01-intro-genai')
        started_at: When student first accessed chapter
        completed_at: When student marked chapter complete
        time_spent_seconds: Total time spent on chapter
        current_section_id: Last section viewed
        completion_percentage: Progress percentage (0-100)
        is_completed: Whether chapter is marked complete
    """

    __tablename__ = "chapter_progress"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Chapter tracking
    chapter_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Progress tracking
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    time_spent_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Current position
    current_section_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    completion_percentage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Relationships
    # user = relationship("User", back_populates="chapter_progress")

    # Indexes
    __table_args__ = (
        Index("idx_chapter_progress_user_id", "user_id"),
        Index("idx_chapter_progress_chapter_id", "chapter_id"),
        Index("idx_chapter_progress_user_chapter", "user_id", "chapter_id", unique=True),
        Index("idx_chapter_progress_completed", "is_completed"),
    )

    def __repr__(self) -> str:
        return f"<ChapterProgress(id={self.id}, user_id={self.user_id}, chapter={self.chapter_id}, {self.completion_percentage}%)>"

    @property
    def time_spent_minutes(self) -> int:
        """Get time spent in minutes."""
        return self.time_spent_seconds // 60

    @property
    def is_in_progress(self) -> bool:
        """Check if chapter has been started but not completed."""
        return not self.is_completed and self.completion_percentage > 0
