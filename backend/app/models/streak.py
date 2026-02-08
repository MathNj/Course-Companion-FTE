"""
from app.models.types import UUID as UUIDType, JSON as JSONType
Streak Model
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
Tracks student daily learning streaks.
from app.models.types import UUID as UUIDType, JSON as JSONType
"""
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from datetime import datetime, date
from app.models.types import UUID as UUIDType, JSON as JSONType
from typing import Optional
from app.models.types import UUID as UUIDType, JSON as JSONType
from uuid import UUID, uuid4
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from sqlalchemy import String, DATE, Integer, Boolean, ForeignKey, Index
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.types import UUID as UUIDType, JSON as JSONType

from app.models.types import UUID as UUIDType, JSON as JSONType
from app.models.base import Base, TimestampMixin
from app.models.types import UUID as UUIDType, JSON as JSONType


class Streak(Base, TimestampMixin):
    """
    Tracks student daily learning streaks.

    Attributes:
        id: Unique streak record identifier
        user_id: Foreign key to User (one-to-one)
        current_streak: Current consecutive days
        longest_streak: Best streak ever achieved
        last_activity_date: Last date with activity
        total_active_days: Total days with activity
        streak_freeze_count: Number of freeze days remaining
        is_active: Whether streak is currently active
        timezone: User's timezone for date calculation
    """

    __tablename__ = "streaks"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys (one-to-one with User)
    user_id: Mapped[UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One streak per user
        index=True,
    )

    # Streak tracking
    current_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    total_active_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Date tracking
    last_activity_date: Mapped[Optional[date]] = mapped_column(
        DATE,
        nullable=True,
        index=True,
    )

    # Streak protection
    streak_freeze_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Timezone for accurate date calculation
    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UTC",
        server_default="UTC",
    )

    # Relationships
    # user = relationship("User", back_populates="streak")

    # Indexes
    __table_args__ = (
        Index("idx_streaks_user_id", "user_id"),
        Index("idx_streaks_last_activity", "last_activity_date"),
        Index("idx_streaks_current", "current_streak"),
    )

    def __repr__(self) -> str:
        return f"<Streak(id={self.id}, user_id={self.user_id}, current={self.current_streak}, longest={self.longest_streak})>"

    @property
    def is_streak_active(self) -> bool:
        """Check if streak is currently active (activity within last 24 hours in user's timezone)."""
        if self.last_activity_date is None:
            return False

        today = date.today()  # Note: Should use user's timezone in production
        days_since_activity = (today - self.last_activity_date).days

        # Streak is active if last activity was today or yesterday
        return days_since_activity <= 1

    def increment_streak(self, activity_date: date) -> None:
        """Increment streak counter if activity is consecutive."""
        if self.last_activity_date is None:
            # First activity ever
            self.current_streak = 1
            self.longest_streak = 1
            self.total_active_days = 1
            self.last_activity_date = activity_date
            return

        days_since_last = (activity_date - self.last_activity_date).days

        if days_since_last == 0:
            # Same day, no increment
            return
        elif days_since_last == 1:
            # Consecutive day, increment
            self.current_streak += 1
            self.total_active_days += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # Streak broken, restart
            self.current_streak = 1
            self.total_active_days += 1

        self.last_activity_date = activity_date

    def use_freeze(self) -> bool:
        """Use a streak freeze to protect streak. Returns True if freeze was available."""
        if self.streak_freeze_count > 0:
            self.streak_freeze_count -= 1
            return True
        return False
