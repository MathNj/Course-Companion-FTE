"""
Session Model

Tracks user chat sessions with the Course Companion.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.types import UUID as UUIDType, JSON as JSONType


class Session(Base, TimestampMixin):
    """
    User chat session with the Course Companion.

    Attributes:
        id: Unique session identifier
        user_id: Foreign key to User
        started_at: Session start timestamp
        ended_at: Session end timestamp
        interaction_count: Number of messages exchanged
        duration_seconds: Total session duration
        last_chapter_id: Last chapter discussed
        last_section_id: Last section discussed
        context: Session context as JSON (conversation state)
        platform: Platform used (chatgpt/web/api)
    """

    __tablename__ = "sessions"

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

    # Session tracking
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
        index=True,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # Activity tracking
    interaction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Context tracking
    last_chapter_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    last_section_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    context: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    # Platform
    platform: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="chatgpt",
        server_default="chatgpt",
    )

    # Relationships
    # user = relationship("User", back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_started_at", "started_at"),
        Index("idx_sessions_user_started", "user_id", "started_at"),
        Index("idx_sessions_platform", "platform"),
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, platform={self.platform}, interactions={self.interaction_count})>"

    @property
    def is_active(self) -> bool:
        """Check if session is still active."""
        return self.ended_at is None

    @property
    def duration_minutes(self) -> Optional[int]:
        """Get session duration in minutes."""
        if self.duration_seconds is None:
            return None
        return self.duration_seconds // 60

    def end_session(self) -> None:
        """Mark session as ended and calculate duration."""
        if self.ended_at is None:
            self.ended_at = datetime.utcnow()
            delta = self.ended_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
