"""
Teacher Endpoints for Phase 2 Monitoring

Cost tracking, usage metrics, and system health for teachers.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.usage import LLMUsageLog, PremiumUsageQuota
from app.models.llm import AdaptivePath, AssessmentSubmission
from app.config.llm_settings import get_llm_settings

router = APIRouter(prefix="/teacher", tags=["Teacher"])


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
    db: AsyncSession = Depends(get_db)
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


@router.get("/alerts")
async def get_cost_alerts(
    threshold: float = Query(0.50, description="Cost alert threshold (default $0.50)"),
    limit: int = Query(50, description="Maximum alerts to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cost alerts for students exceeding monthly threshold.

    This is FR-026: Cost alert system.

    Args:
        threshold: Cost threshold in USD (default $0.50)
        limit: Maximum number of alerts to return

    Returns:
        - List of students exceeding threshold
        - Total alerts in period
        - Average cost per student
        - Recommended actions
    """
    # Default to current month
    start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

    # Query students exceeding threshold
    result = await db.execute(
        select(
            LLMUsageLog.student_id,
            func.sum(LLMUsageLog.cost_usd).label("monthly_cost"),
            func.count(LLMUsageLog.log_id).label("request_count")
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
        .group_by(LLMUsageLog.student_id)
        .having(func.sum(LLMUsageLog.cost_usd) > threshold)
        .order_by(desc("monthly_cost"))
        .limit(limit)
    )

    alerts = []
    for row in result:
        alerts.append({
            "student_id": str(row.student_id),
            "monthly_cost_usd": float(row.monthly_cost),
            "request_count": row.request_count,
            "threshold_usd": threshold,
            "excess_amount": float(row.monthly_cost) - threshold
        })

    # Get summary statistics
    stats_result = await db.execute(
        select(
            func.count(func.distinct(LLMUsageLog.student_id))
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
    )
    total_students = stats_result.scalar() or 0

    cost_result = await db.execute(
        select(func.sum(LLMUsageLog.cost_usd)).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
    )
    total_cost = float(cost_result.scalar() or 0)

    # Get settings for comparison
    settings = get_llm_settings()
    configured_threshold = settings.LLM_COST_ALERT_THRESHOLD

    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "threshold_used": threshold,
        "configured_threshold": configured_threshold,
        "total_students": total_students,
        "total_cost_usd": total_cost,
        "average_cost_per_student": total_cost / total_students if total_students > 0 else 0,
        "alert_count": len(alerts),
        "alerts": alerts,
        "recommended_actions": _generate_alert_recommendations(len(alerts), threshold, total_cost)
    }


@router.get("/dashboard")
async def get_cost_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive cost monitoring dashboard (FR-027).

    Returns:
    - Current month costs (adaptive paths, assessments, total)
    - Cost trends (daily breakdown)
    - Top users by cost
    - Cost alerts
    - Budget utilization
    - Projected monthly cost

    Use for real-time cost monitoring and optimization.
    """
    current_month = datetime.now().replace(day=1)

    # Get current month costs by feature
    start_dt = current_month
    end_dt = datetime.now() + timedelta(days=1)

    # Feature breakdown
    feature_result = await db.execute(
        select(
            LLMUsageLog.feature,
            func.count(LLMUsageLog.log_id).label("total_requests"),
            func.sum(LLMUsageLog.cost_usd).label("total_cost"),
            func.sum(LLMUsageLog.tokens_input).label("total_input_tokens"),
            func.sum(LLMUsageLog.tokens_output).label("total_output_tokens")
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
        .group_by(LLMUsageLog.feature)
    )

    features = {}
    total_cost = 0.0
    total_requests = 0

    for row in feature_result.all():
        feature_cost = float(row.total_cost) if row.total_cost else 0.0
        features[row.feature] = {
            "requests": row.total_requests,
            "cost_usd": feature_cost,
            "average_tokens_per_request": (row.total_input_tokens + row.total_output_tokens) / row.total_requests if row.total_requests > 0 else 0
        }
        total_cost += feature_cost
        total_requests += row.total_requests

    # Daily trend (last 30 days)
    daily_trend_result = await db.execute(
        select(
            func.date(LLMUsageLog.request_timestamp).label("date"),
            func.sum(LLMUsageLog.cost_usd).label("daily_cost"),
            func.count(LLMUsageLog.log_id).label("daily_requests")
        ).where(
            LLMUsageLog.request_timestamp >= datetime.now() - timedelta(days=30),
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
        .group_by(func.date(LLMUsageLog.request_timestamp))
        .order_by(func.date(LLMUsageLog.request_timestamp))
    )

    daily_trend = []
    for row in daily_trend_result.all():
        daily_trend.append({
            "date": str(row.date),
            "cost_usd": float(row.daily_cost) if row.daily_cost else 0.0,
            "requests": row.daily_requests
        })

    # Top users by cost
    top_users_result = await db.execute(
        select(
            LLMUsageLog.student_id,
            func.sum(LLMUsageLog.cost_usd).label("monthly_cost"),
            func.count(LLMUsageLog.log_id).label("request_count")
        ).where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
        .group_by(LLMUsageLog.student_id)
        .order_by(desc("monthly_cost"))
        .limit(10)
    )

    top_users = []
    for row in top_users_result.all():
        top_users.append({
            "student_id": str(row.student_id),
            "monthly_cost_usd": float(row.monthly_cost) if row.monthly_cost else 0.0,
            "request_count": row.request_count
        })

    # Get cost threshold alerts
    settings = get_llm_settings()
    threshold = settings.LLM_COST_ALERT_THRESHOLD

    alert_result = await db.execute(
        select(func.count(func.distinct(LLMUsageLog.student_id)))
        .where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
    )
    total_students = alert_result.scalar() or 0

    high_cost_students_result = await db.execute(
        select(func.count(func.distinct(LLMUsageLog.student_id)))
        .where(
            LLMUsageLog.request_timestamp >= start_dt,
            LLMUsageLog.request_timestamp < end_dt,
            LLMUsageLog.success == True,
            LLMUsageLog.deleted_at.is_(None)
        )
    )
    active_students = high_cost_students_result.scalar() or 0

    # Project monthly cost (extrapolate current month to full month)
    days_in_month = (current_month.replace(month=12, year=current_month.year + 1, day=1) - timedelta(days=1)).day
    days_elapsed = (datetime.now() - current_month).days + 1
    projected_monthly_cost = total_cost / days_elapsed * days_in_month if days_elapsed > 0 else total_cost

    return {
        "dashboard_timestamp": datetime.now().isoformat(),
        "current_month": current_month.strftime("%Y-%m"),
        "period": {
            "start_date": current_month.strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "days_elapsed": days_elapsed,
            "days_total": days_in_month
        },
        "summary": {
            "total_cost_usd": round(total_cost, 4),
            "total_requests": total_requests,
            "total_students": total_students,
            "active_students": active_students,
            "average_cost_per_student": round(total_cost / total_students, 4) if total_students > 0 else 0.0,
            "average_cost_per_request": round(total_cost / total_requests, 6) if total_requests > 0 else 0.0
        },
        "by_feature": features,
        "daily_trend": daily_trend[-7:],  # Last 7 days
        "top_users_by_cost": top_users,
        "alerts": {
            "cost_threshold_usd": threshold,
            "students_exceeding_threshold": len([u for u in top_users if u["monthly_cost_usd"] > threshold]),
            "projected_monthly_cost_usd": round(projected_monthly_cost, 2)
        },
        "budget_utilization": {
            "budget_per_student_usd": 0.50,  # From requirements
            "total_budget_usd": 0.50 * total_students,
            "actual_cost_usd": total_cost,
            "budget_remaining_usd": max(0, (0.50 * total_students) - total_cost),
            "utilization_percent": round((total_cost / (0.50 * total_students)) * 100, 1) if total_students > 0 else 0
        }
    }


def _generate_alert_recommendations(alert_count: int, threshold: float, total_cost: float) -> List[str]:
    """Generate actionable recommendations based on alert metrics."""
    recommendations = []

    if alert_count > 10:
        recommendations.append(
            f"Consider implementing usage caps to prevent cost overruns. "
            f"{alert_count} students have exceeded ${threshold:.2f} threshold."
        )

    if total_cost > 100:
        recommendations.append(
            f"Monthly cost (${total_cost:.2f}) exceeds $100 budget. "
            "Review pricing model or consider increasing subscription tiers."
        )

    if alert_count > 0:
        recommendations.append(
            "Reach out to high-usage students to understand their use patterns "
            "and suggest more efficient learning strategies."
        )

    if not recommendations:
        recommendations.append("Cost levels are within acceptable ranges. Continue monitoring.")

    return recommendations


@router.get("/students")
async def get_all_students(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all students with their progress, quiz scores, and engagement data.

    Returns real student data from the database including:
    - User information (id, email)
    - Chapter progress
    - Quiz scores
    - Streak information
    - Last activity timestamp
    """
    from app.models.progress import ChapterProgress
    from app.models.quiz import QuizAttempt
    from app.models.streak import Streak

    # Get all students (non-admin users)
    result = await db.execute(
        select(User).where(User.is_active == True)
    )
    students = result.scalars().all()

    student_data = []

    for student in students:
        # Get chapter progress
        progress_result = await db.execute(
            select(ChapterProgress)
            .where(ChapterProgress.user_id == student.id)
        )
        all_progress = progress_result.scalars().all()

        completed_chapters = len([p for p in all_progress if p.is_completed])
        total_chapters = 6  # TODO: Get from course config

        # Calculate overall completion percentage
        completion_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0

        # Get quiz scores
        quiz_result = await db.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == student.id)
            .order_by(desc(QuizAttempt.created_at))
        )
        quiz_attempts = quiz_result.scalars().all()

        # Get latest score for each quiz
        quiz_scores = {}
        for attempt in quiz_attempts:
            quiz_id = attempt.quiz_id
            if quiz_id not in quiz_scores:
                quiz_scores[quiz_id] = {
                    "score": attempt.score_percentage,
                    "passed": attempt.passed,
                    "attempted_at": attempt.completed_at.isoformat() if attempt.completed_at else None
                }

        # Get streak data
        streak_result = await db.execute(
            select(Streak)
            .where(Streak.user_id == student.id)
            .order_by(desc(Streak.last_activity_date))
        )
        streak = streak_result.scalar_one_or_none()

        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0

        # Get last activity from progress updates or quiz attempts
        last_progress_result = await db.execute(
            select(ChapterProgress)
            .where(ChapterProgress.user_id == student.id)
            .order_by(desc(ChapterProgress.updated_at))
            .limit(1)
        )
        last_progress = last_progress_result.scalar_one_or_none()

        last_activity = (
            last_progress.updated_at.isoformat() if last_progress else
            student.created_at.isoformat()
        )

        # Get premium usage
        # Note: AdaptivePath uses student_id, not user_id
        adaptive_paths_count = 0  # TODO: Implement when AdaptivePath is properly linked to User model

        # Note: AssessmentSubmission uses student_id, not user_id
        assessments_count = 0  # TODO: Implement when AssessmentSubmission is properly linked to User model

        # Calculate engagement metrics
        total_time_minutes = sum([p.time_spent_seconds or 0 for p in all_progress]) // 60
        sessions = len(all_progress)  # Count unique chapter sessions

        # Find drop-off chapter (first incomplete chapter)
        drop_off_chapter = None
        incomplete_chapters = [p for p in all_progress if not p.is_completed]
        if incomplete_chapters:
            # Sort by updated_at to find most recent incomplete chapter
            incomplete_chapters.sort(key=lambda x: x.updated_at, reverse=True)
            drop_off_chapter = incomplete_chapters[0].chapter_id

        student_data.append({
            "id": str(student.id),
            "email": student.email,
            "progress": {
                "completion_percentage": round(completion_percentage, 1),
                "chapters_completed": completed_chapters,
                "total_chapters": total_chapters
            },
            "streak": {
                "current_streak": current_streak,
                "longest_streak": longest_streak
            },
            "quiz_scores": quiz_scores,
            "last_activity": last_activity,
            "engagement": {
                "total_time_minutes": total_time_minutes,
                "sessions": sessions,
                "drop_off_chapter": drop_off_chapter
            },
            "premium_usage": {
                "adaptive_paths": adaptive_paths_count,
                "assessments": assessments_count
            },
            "created_at": student.created_at.isoformat()
        })

    return {
        "students": student_data,
        "total": len(student_data)
    }
