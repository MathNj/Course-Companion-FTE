"""
Subscription Model

Tracks user subscription tier and payment status.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, TIMESTAMP, DECIMAL, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Subscription(Base, TimestampMixin):
    """
    User subscription record.

    Attributes:
        id: Unique subscription identifier
        user_id: Foreign key to User
        tier: Subscription tier (free/premium/pro)
        status: Current status (active/cancelled/expired)
        started_at: Subscription start date
        expires_at: Subscription expiration date
        cancelled_at: Cancellation timestamp
        price_cents: Price in cents (for reporting)
        billing_period: Billing cycle (monthly/annual)
    """

    __tablename__ = "subscriptions"

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
        unique=True,  # One subscription per user
        index=True,
    )

    # Subscription details
    tier: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="free",
        server_default="free",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )

    # Dates
    started_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,  # NULL = no expiration (lifetime)
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )

    # Billing
    price_cents: Mapped[int] = mapped_column(
        DECIMAL(10, 0),
        nullable=False,
        default=0,
        server_default="0",
    )
    billing_period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="monthly",
        server_default="monthly",
    )

    # Relationships
    # user = relationship("User", back_populates="subscription")

    # Indexes
    __table_args__ = (
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_status", "status"),
        Index("idx_subscriptions_tier", "tier"),
        Index("idx_subscriptions_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier={self.tier}, status={self.status})>"

    @property
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status != "active":
            return False
        if self.expires_at is None:
            return True
        return datetime.utcnow() < self.expires_at

    @property
    def is_premium_or_higher(self) -> bool:
        """Check if subscription is premium or pro tier."""
        return self.tier in ("premium", "pro") and self.is_active
