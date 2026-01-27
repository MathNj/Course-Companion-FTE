"""
Admin Endpoints for Phase 2 Monitoring

Cost tracking, usage metrics, and system health for administrators.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.usage import LLMUsageLog
from app.models.llm import AdaptivePath, AssessmentSubmission

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/costs")
async def get_cost_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: str = Query("feature", description="Group by: feature, student, day"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get LLM cost metrics for monitoring and alerting.

    Returns:
    - Total cost for period
    - Total requests
    - Average cost per student
    - Breakdown by feature
    - Cost alerts (students exceeding threshold)
    """
    # TODO: Verify admin role (is_admin check)

    # Default to current month if no dates provided
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD."
        )

    # Query total cost and requests
    result = await db.execute(
        select(
            func.count(LLMUsageLog.log_id),
            func.sum(LLMUsageLog.cost_usd),
            func.sum(LLMUsageLog.tokens_input),
            func.sum(LLMUsageLog.tokens_output)
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
    )

    total_requests, total_cost, total_input, total_output = result.one()

    if not total_requests:
        return {
            "period": {"start_date": start_date, "end_date": end_date},
            "total_cost_usd": 0.0,
            "total_requests": 0,
            "average_cost_per_student": 0.0,
            "breakdown_by_feature": [],
            "alerts": []
        }

    # Get breakdown by feature
    feature_result = await db.execute(
        select(
            LLMUsageLog.feature,
            func.count(LLMUsageLog.log_id).label("total_requests"),
            func.sum(LLMUsageLog.cost_usd).label("total_cost_usd")
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        ).group_by(LLMUsageLog.feature)
    )

    feature_breakdown = []
    for row in feature_result:
        feature_breakdown.append({
            "feature": row.feature,
            "total_requests": row.total_requests,
            "total_cost_usd": float(row.total_cost_usd),
            "average_cost_per_request": float(row.total_cost_usd) / row.total_requests
        })

    # Get unique student count
    student_count_result = await db.execute(
        select(func.count(func.distinct(LLMUsageLog.student_id)))
        .where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
    )
    unique_students = student_count_result.scalar()

    # Check for cost alerts (students exceeding threshold)
    from app.config.llm_settings import get_llm_settings
    settings = get_llm_settings()
    threshold = settings.LLM_COST_ALERT_THRESHOLD

    alert_result = await db.execute(
        select(
            LLMUsageLog.student_id,
            func.sum(LLMUsageLog.cost_usd).label("monthly_cost")
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        ).group_by(LLMUsageLog.student_id)
        .having(func.sum(LLMUsageLog.cost_usd) > threshold)
    )

    alerts = []
    for row in alert_result:
        alerts.append({
            "type": "COST_THRESHOLD_EXCEEDED",
            "student_id": str(row.student_id),
            "cost_usd": float(row.monthly_cost),
            "threshold_usd": threshold
        })

    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "total_cost_usd": float(total_cost) if total_cost else 0.0,
        "total_requests": total_requests,
        "average_cost_per_student": float(total_cost) / unique_students if unique_students > 0 else 0.0,
        "breakdown_by_feature": feature_breakdown,
        "alerts": alerts
    }


@router.get("/health")
async def get_llm_health(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = AsyncSession = Depends(get_db)
):
    """
    Check health of LLM services (OpenAI API availability).

    Returns:
    - Service status (healthy/degraded)
    - Recent error rate
    - Average latency
    - Active quota usage
    """
    # Check OpenAI API health
    from app.services.llm.client import get_openai_client

    client = get_openai_client()
    is_healthy = await client.is_available()

    # Get recent error rate (last 100 requests)
    recent_result = await db.execute(
        select(
            func.count(LLMUsageLog.log_id).label("total"),
            func.sum(func.cast(LLMUsageLog.success == False, db.Integer)).label("errors")
        ).where(
            LLMUsageLog.request_timestamp >= datetime.now() - timedelta(hours=1)
        )
    )

    total, errors = recent_result.one() or (0, 0)
    error_rate = (errors / total * 100) if total > 0 else 0.0

    # Get average latency
    latency_result = await db.execute(
        select(func.avg(LLMUsageLog.latency_ms))
        .where(
            LLMUsageLog.request_timestamp >= datetime.now() - timedelta(hours=1)
        )
    )
    avg_latency = latency_result.scalar() or 0

    status = "healthy" if is_healthy and error_rate < 5 else "degraded"

    return {
        "status": status,
        "openai_api": "available" if is_healthy else "unavailable",
        "error_rate_percent": round(error_rate, 2),
        "average_latency_ms": round(avg_latency, 2),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/quotas")
async def get_quota_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get premium usage quota statistics across all students.

    Returns:
    - Total premium students
    - Quota usage distribution
    - Top users by requests
    """
    from app.models.usage import PremiumUsageQuota

    current_month = datetime.now().replace(day=1)

    # Get active premium students
    quota_result = await db.execute(
        select(
            func.count(PremiumUsageQuota.quota_id).label("total_students"),
            func.sum(PremiumUsageQuota.adaptive_paths_used).label("total_paths_used"),
            func.sum(PremiumUsageQuota.assessments_used).label("total_assessments_used")
        ).where(PremiumUsageQuota.month == current_month)
    )

    row = quota_result.one_or_none()

    if not row:
        return {
            "month": current_month.strftime("%Y-%m"),
            "total_premium_students": 0,
            "total_adaptive_paths_used": 0,
            "total_assessments_used": 0,
            "average_paths_per_student": 0,
            "average_assessments_per_student": 0
        }

    return {
        "month": current_month.strftime("%Y-%m"),
        "total_premium_students": row.total_students,
        "total_adaptive_paths_used": row.total_paths_used or 0,
        "total_assessments_used": row.total_assessments_used or 0,
        "average_paths_per_student": round((row.total_paths_used or 0) / row.total_students, 2) if row.total_students > 0 else 0,
        "average_assessments_per_student": round((row.total_assessments_used or 0) / row.total_students, 2) if row.total_students > 0 else 0
    }
