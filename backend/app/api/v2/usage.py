"""
Usage Quota Tracking Endpoints

Allow premium students to check their remaining monthly quotas.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.usage import PremiumUsageQuota, LLMUsageLog
from app.services.rate_limiter import RateLimiter

router = APIRouter(prefix="/usage", tags=["Usage Tracking"])


@router.get("/quota")
async def get_usage_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current student's remaining monthly quotas for premium features.

    Returns:
    - Monthly quota usage (adaptive paths and assessments)
    - Remaining quota for each feature
    - Reset date
    """
    current_month = datetime.now().replace(day=1)

    # Get or create quota record for current month
    result = await db.execute(
        select(PremiumUsageQuota).where(
            PremiumUsageQuota.student_id == current_user.id,
            PremiumUsageQuota.month == current_month
        )
    )

    quota = result.scalar_one_or_none()

    if not quota:
        # Create new quota record
        quota = PremiumUsageQuota(
            student_id=current_user.id,
            month=current_month,
            reset_date=(current_month.replace(day=28) + timedelta(days=4)).replace(day=1),
            adaptive_paths_used=0,
            adaptive_paths_limit=10,
            assessments_used=0,
            assessments_limit=20
        )
        db.add(quota)
        await db.commit()
        await db.refresh(quota)

    # Calculate remaining
    paths_remaining = quota.adaptive_paths_limit - quota.adaptive_paths_used
    assessments_remaining = quota.assessments_limit - quota.assessments_used

    return {
        "student_id": str(current_user.id),
        "subscription_tier": getattr(current_user, 'subscription_tier', 'free'),
        "month": quota.month.strftime("%Y-%m"),
        "reset_date": quota.reset_date.isoformat(),

        "adaptive_paths_used": quota.adaptive_paths_used,
        "adaptive_paths_limit": quota.adaptive_paths_limit,
        "adaptive_paths_remaining": paths_remaining,

        "assessments_used": quota.assessments_used,
        "assessments_limit": quota.assessments_limit,
        "assessments_remaining": assessments_remaining
    }


@router.get("/quota/status")
async def get_quota_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive quota status with real-time enforcement data.

    Uses RateLimiter service to get:
    - Real-time usage (from Redis)
    - Remaining quota for each feature
    - Reset date (first of next month)
    - Total usage across features

    Returns 429 error when quota exceeded.
    """
    # Create rate limiter instance
    rate_limiter = RateLimiter(db=db)

    # Get comprehensive status
    status = await rate_limiter.get_quota_status(str(current_user.id))

    return {
        "student_id": str(current_user.id),
        "student_email": current_user.email,
        "subscription_tier": getattr(current_user, 'subscription_tier', 'free'),
        "current_month": status["month"],
        "features": {
            "adaptive-paths": {
                "used": status["features"]["adaptive-path"]["used"],
                "limit": status["features"]["adaptive-path"]["limit"],
                "remaining": status["features"]["adaptive-path"]["remaining"],
                "resets_at": status["features"]["adaptive-path"]["resets_at"]
            },
            "assessments": {
                "used": status["features"]["assessment"]["used"],
                "limit": status["features"]["assessment"]["limit"],
                "remaining": status["features"]["assessment"]["remaining"],
                "resets_at": status["features"]["assessment"]["resets_at"]
            }
        },
        "total_usage": status["total_usage"],
        "total_limit": status["total_limit"],
        "utilization_percent": round(
            (status["total_usage"] / status["total_limit"]) * 100, 1
        ) if status["total_limit"] > 0 else 0
    }
