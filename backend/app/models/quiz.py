"""
Quiz Models

Tracks student quiz attempts and results.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP, Integer, DECIMAL, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.types import UUID as UUIDType, JSON as JSONType


class QuizAttempt(Base, TimestampMixin):
    """
    Tracks individual quiz attempts by students.

    Attributes:
        id: Unique attempt identifier
        user_id: Foreign key to User
        quiz_id: Quiz identifier (e.g., 'quiz-chapter-01')
        chapter_id: Associated chapter identifier
        started_at: When quiz was started
        completed_at: When quiz was submitted
        score_percentage: Final score (0-100)
        total_questions: Number of questions
        correct_answers: Number of correct answers
        answers: Student's answers as JSON
        passed: Whether student passed (score >= 70%)
        attempt_number: Attempt number for this quiz
        time_spent_seconds: Time taken to complete quiz
    """

    __tablename__ = "quiz_attempts"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Quiz tracking
    quiz_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    chapter_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Timing
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
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Scoring
    score_percentage: Mapped[Optional[int]] = mapped_column(
        DECIMAL(5, 2),
        nullable=True,  # NULL until graded
    )
    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    correct_answers: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,  # NULL until graded
    )
    passed: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,  # NULL until graded
    )

    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    # Answers (stored as JSON)
    answers: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    # Relationships
    # user = relationship("User", back_populates="quiz_attempts")

    # Indexes
    __table_args__ = (
        Index("idx_quiz_attempts_user_id", "user_id"),
        Index("idx_quiz_attempts_quiz_id", "quiz_id"),
        Index("idx_quiz_attempts_chapter_id", "chapter_id"),
        Index("idx_quiz_attempts_user_quiz", "user_id", "quiz_id"),
        Index("idx_quiz_attempts_completed", "completed_at"),
        Index("idx_quiz_attempts_passed", "passed"),
    )

    def __repr__(self) -> str:
        return f"<QuizAttempt(id={self.id}, user_id={self.user_id}, quiz={self.quiz_id}, score={self.score_percentage}%)>"

    @property
    def is_completed(self) -> bool:
        """Check if quiz has been completed."""
        return self.completed_at is not None

    @property
    def is_passed(self) -> bool:
        """Check if quiz was passed (score >= 70%)."""
        if self.score_percentage is None:
            return False
        return float(self.score_percentage) >= 70.0

    @property
    def time_spent_minutes(self) -> Optional[int]:
        """Get time spent in minutes."""
        if self.time_spent_seconds is None:
            return None
        return self.time_spent_seconds // 60
