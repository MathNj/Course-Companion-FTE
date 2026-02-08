"""
User Model

Represents students using the Course Companion system.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String, TIMESTAMP, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.types import UUID as UUIDType, JSON as JSONType


class User(Base, TimestampMixin):
    """
    Student user account.

    Attributes:
        id: Unique user identifier
        email: User email (authentication)
        password_hash: Hashed password (NULL if OAuth only)
        full_name: Student's name
        subscription_tier: Subscription level (free/premium/pro)
        subscription_expires_at: Premium expiration date
        timezone: User's timezone for streak calculation
        preferences: User preferences JSON
        last_active_at: Last interaction timestamp
        is_active: Soft delete flag
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid4,
    )

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,  # NULL if OAuth only
    )

    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Subscription
    subscription_tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="free",
        server_default="free",
        index=True,
    )
    subscription_expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # Preferences
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UTC",
        server_default="UTC",
    )
    preferences: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False,
        default=dict,
    )

    # Activity tracking
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        index=True,
    )

    # Soft delete
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Teacher role
    is_teacher: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Relationships (will be populated when related models are created)
    # chapter_progress = relationship("ChapterProgress", back_populates="user")
    # quiz_attempts = relationship("QuizAttempt", back_populates="user")
    # sessions = relationship("Session", back_populates="user")
    # streak = relationship("Streak", back_populates="user", uselist=False)
    # subscription = relationship("Subscription", back_populates="user", uselist=False)

    # Indexes
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_subscription_tier", "subscription_tier"),
        Index("idx_users_last_active", "last_active_at"),
        Index("idx_users_active_email", "is_active", "email"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"

    @property
    def is_premium(self) -> bool:
        """Check if user has active premium subscription."""
        if self.subscription_tier in ("premium", "pro"):
            if self.subscription_expires_at is None:
                return True  # No expiration
            return datetime.utcnow() < self.subscription_expires_at
        return False

    @property
    def is_free(self) -> bool:
        """Check if user is on free tier."""
        return self.subscription_tier == "free" or not self.is_premium
