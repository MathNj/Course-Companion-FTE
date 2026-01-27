"""
Rate Limiting Enforcement Service

Tracks and enforces monthly quotas for premium features:
- 10 adaptive paths per month
- 20 assessments per month

Uses Redis for fast, distributed rate limiting with PostgreSQL fallback.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.utils.redis_client import cache_client
from app.models.usage import PremiumUsageQuota
from app.models.user import User

logger = logging.getLogger(__name__)


# Monthly limits (per premium user)
ADAPTIVE_PATHS_LIMIT = 10
ASSESSMENTS_LIMIT = 20


class RateLimitExceededError(Exception):
    """Raised when user exceeds monthly quota."""

    def __init__(self, feature: str, used: int, limit: int, resets_at: datetime):
        self.feature = feature
        self.used = used
        self.limit = limit
        self.resets_at = resets_at


class RateLimiter:
    """
    Enforces rate limits for premium features.

    Features:
    - Redis-based fast distributed limiting
    - PostgreSQL fallback for persistence
    - Automatic monthly reset
    - Graceful degradation
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize rate limiter.

        Args:
            db: Database session
        """
        self.db = db

    async def get_usage(
        self,
        student_id: str,
        feature: str,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current usage for a feature.

        Args:
            student_id: Student UUID
            feature: Feature name ("adaptive-path" or "assessment")
            month: Month in YYYY-MM format (defaults to current month)

        Returns:
            Dictionary with used, limit, resets_at, remaining
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        # Check Redis first (fast path)
        redis_key = f"quota:{student_id}:{month}:{feature}"
        cached = await cache_client.get(redis_key)

        if cached is not None:
            used = int(cached)
            limit = self._get_limit(feature)

            # Calculate reset date (first day of next month)
            year, month_num = map(int, month.split('-'))
            if month_num == 12:
                resets_at = datetime(year + 1, 1, 1)
            else:
                resets_at = datetime(year, month_num + 1, 1)

            return {
                "used": used,
                "limit": limit,
                "remaining": max(0, limit - used),
                "resets_at": resets_at.isoformat(),
                "month": month,
                "source": "redis"
            }

        # Fallback to PostgreSQL
        return await self._get_usage_from_db(student_id, feature, month)

    async def _get_usage_from_db(
        self,
        student_id: str,
        feature: str,
        month: str
    ) -> Dict[str, Any]:
        """Get usage from PostgreSQL database (fallback)."""
        # Parse month to get first and last day
        try:
            year, month_num = map(int, month.split('-'))
            month_start = datetime(year, month_num, 1)

            if month_num == 12:
                next_month = datetime(year + 1, 1, 1)
            else:
                next_month = datetime(year, month_num + 1, 1)

        except ValueError:
            logger.error(f"Invalid month format: {month}")
            return {
                "used": 0,
                "limit": self._get_limit(feature),
                "remaining": self._get_limit(feature),
                "resets_at": next_month.isoformat(),
                "month": month,
                "source": "database"
            }

        # Query usage quota record
        result = await self.db.execute(
            select(PremiumUsageQuota).where(
                and_(
                    PremiumUsageQuota.student_id == UUID(student_id),
                    PremiumUsageQuota.month == month_start.date()
                )
            )
        )
        quota = await result.scalar_one_or_none()

        if feature == "adaptive-path":
            used = quota.adaptive_paths_used if quota else 0
        else:
            used = quota.assessments_used if quota else 0

        limit = self._get_limit(feature)

        return {
            "used": used,
            "limit": limit,
            "remaining": max(0, limit - used),
            "resets_at": next_month.isoformat(),
            "month": month,
            "source": "database"
        }

    async def check_and_increment(
        self,
        student_id: str,
        feature: str
    ) -> Dict[str, Any]:
        """
        Check quota and increment counter if not exceeded.

        This is the main enforcement method - call it before allowing a feature.

        Args:
            student_id: Student UUID
            feature: Feature name ("adaptive-path" or "assessment")

        Returns:
            Dictionary with success, used, limit, remaining, resets_at

        Raises:
            RateLimitExceededError: If quota exceeded
        """
        month = datetime.now().strftime("%Y-%m")
        limit = self._get_limit(feature)

        # Check current usage
        usage = await self.get_usage(student_id, feature, month)

        if usage["used"] >= usage["limit"]:
            # Quota exceeded
            raise RateLimitExceededError(
                feature=feature,
                used=usage["used"],
                limit=usage["limit"],
                resets_at=datetime.fromisoformat(usage["resets_at"])
            )

        # Increment counter
        success = await self._increment_usage(student_id, feature, month)

        if success:
            # Return updated usage
            return {
                "success": True,
                "used": usage["used"] + 1,
                "limit": limit,
                "remaining": limit - usage["used"] - 1,
                "resets_at": usage["resets_at"],
                "month": month,
                "source": usage["source"]
            }
        else:
            # Redis failed, fallback to DB
            return await self._increment_in_db(student_id, feature, month, usage)

    async def _increment_usage(
        self,
        student_id: str,
        feature: str,
        month: str
    ) -> bool:
        """
        Increment Redis quota counter.

        Args:
            student_id: Student UUID
            feature: Feature name
            month: Month string (YYYY-MM)

        Returns:
            True if successful, False otherwise
        """
        redis_key = f"quota:{student_id}:{month}:{feature}"

        # Get current value
        current = await cache_client.get(redis_key)
        if current is None:
            current = 0

        # Increment
        new_value = int(current) + 1
        limit = self._get_limit(feature)

        # Set with 31-day TTL (auto-expires after month)
        success = await cache_client.setex(
            redis_key,
            2678400,  # 31 days in seconds
            str(new_value)
        )

        if success:
            logger.info(f"Incremented quota for student {student_id[:8]}... feature={feature} used={new_value}/{limit}")

        return success

    async def _increment_in_db(
        self,
        student_id: str,
        feature: str,
        month: str,
        usage: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Increment PostgreSQL quota record (fallback when Redis unavailable).

        Args:
            student_id: Student UUID
            feature: Feature name
            month: Month string (YYYY-MM)
            usage: Current usage dict

        Returns:
            Updated usage dict
        """
        try:
            # Parse month
            year, month_num = map(int, month.split('-'))
            month_start = datetime(year, month_num, 1)

            # Find or create quota record
            result = await self.db.execute(
                select(PremiumUsageQuota).where(
                    and_(
                        PremiumUsageQuota.student_id == UUID(student_id),
                        PremiumUsageQuota.month == month_start.date()
                    )
                )
            )
            quota = await result.scalar_one_or_none()

            if quota:
                # Increment appropriate field
                if feature == "adaptive-path":
                    quota.adaptive_paths_used += 1
                else:
                    quota.assessments_used += 1

                quota.updated_at = datetime.utcnow()

                logger.info(f"Incremented DB quota for student {student_id[:8]}... feature={feature}")
            else:
                # Create new quota record
                reset_date = month_start + timedelta(days=32)
                reset_date = reset_date.replace(day=1)

                quota = PremiumUsageQuota(
                    student_id=UUID(student_id),
                    month=month_start.date(),
                    reset_date=reset_date.date(),
                    adaptive_paths_used=1 if feature == "adaptive-path" else 0,
                    assessments_used=1 if feature == "assessment" else 0
                )
                self.db.add(quota)
                logger.info(f"Created DB quota for student {student_id[:8]}... feature={feature}")

            await self.db.commit()

            # Return updated usage
            return {
                "success": True,
                "used": usage["used"] + 1,
                "limit": usage["limit"],
                "remaining": usage["limit"] - usage["used"] - 1,
                "resets_at": usage["resets_at"],
                "month": month,
                "source": "database"
            }

        except Exception as e:
            logger.error(f"Failed to increment DB quota: {e}")
            raise

    def _get_limit(self, feature: str) -> int:
        """Get monthly limit for a feature."""
        limits = {
            "adaptive-path": ADAPTIVE_PATHS_LIMIT,
            "assessment": ASSESSMENTS_LIMIT
        }
        return limits.get(feature, ADAPTIVE_PATHS_LIMIT)

    async def reset_quota(
        self,
        student_id: str,
        feature: str
    ) -> bool:
        """
        Reset quota for testing purposes (admin only).

        Args:
            student_id: Student UUID
            feature: Feature name to reset

        Returns:
            True if successful, False otherwise
        """
        month = datetime.now().strftime("%Y-%m")
        redis_key = f"quota:{student_id}:{month}:{feature}"

        # Reset Redis counter to 0
        success = await cache_client.setex(
            redis_key,
            2678400,  # 31 days
            "0"
        )

        if success:
            logger.info(f"Reset quota for student {student_id[:8]}... feature={feature}")

        return success

    async def get_quota_status(
        self,
        student_id: str
    ) -> Dict[str, Any]:
        """
        Get complete quota status for all features.

        Args:
            student_id: Student UUID

        Returns:
            Dictionary with adaptive_path and assessment quotas
        """
        month = datetime.now().strftime("%Y-%m")

        adaptive_usage = await self.get_usage(student_id, "adaptive-path", month)
        assessment_usage = await self.get_usage(student_id, "assessment", month)

        return {
            "student_id": student_id,
            "month": month,
            "features": {
                "adaptive-path": adaptive_usage,
                "assessment": assessment_usage
            },
            "total_usage": adaptive_usage["used"] + assessment_usage["used"],
            "total_limit": adaptive_usage["limit"] + assessment_usage["limit"]
        }
