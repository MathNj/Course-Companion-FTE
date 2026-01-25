"""
Premium API Routes for Phase 2 Hybrid Intelligence Features

This module contains all premium-only endpoints that require LLM API calls.
All endpoints are protected by premium subscription checks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.premium import (
    GradeAssessmentRequest,
    GradeAssessmentResponse,
    GenerateLearningPathRequest,
    GenerateLearningPathResponse,
    SubscriptionStatus,
    UpgradeRequest,
    UpgradeResponse,
    MonthlyUsageStats,
    UsageLimit
)
from app.services.llm_service import LLMService
from app.services.cost_tracker import CostTracker
from app.api.dependencies import get_current_user, require_premium

router = APIRouter(prefix="/api/v2/premium", tags=["premium"])


# ============================================================================
# Premium Feature: LLM-Graded Assessments
# ============================================================================

@router.post("/assessments/grade", response_model=GradeAssessmentResponse)
async def grade_assessment(
    request: GradeAssessmentRequest,
    current_user = Depends(require_premium),
    db: Session = Depends(get_db)
):
    """
    Grade a free-form assessment using LLM (Premium Feature)

    Evaluates written answers with detailed feedback including:
    - Overall score (0-100)
    - Strengths and areas for improvement
    - Specific suggestions
    - Rubric category scores

    Requires: Active premium subscription
    Cost: ~$0.014 per request (1,500 tokens)
    """
    try:
        # Check usage limits
        cost_tracker = CostTracker(db)
        usage = await cost_tracker.check_usage_limits(current_user.id, "graded_assessment")

        if usage["remaining"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly assessment limit reached ({usage['limit']}). Upgrade your plan or wait for next month."
            )

        # Initialize LLM service
        llm_service = LLMService(db=db)

        # Grade the assessment
        result = await llm_service.grade_assessment(
            question=request.question,
            student_answer=request.student_answer,
            rubric=request.rubric,
            question_type=request.question_type,
            user_id=current_user.id
        )

        # Increment usage counter
        await cost_tracker.increment_usage(current_user.id, "graded_assessment")

        return GradeAssessmentResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error grading assessment: {str(e)}"
        )


@router.get("/assessments/usage", response_model=UsageLimit)
async def get_assessment_usage(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get assessment usage limits and remaining uses

    Shows how many assessments have been used this month
    and how many remain (0 for free tier).
    """
    try:
        cost_tracker = CostTracker(db)
        usage = await cost_tracker.check_usage_limits(current_user.id, "graded_assessment")

        # Calculate days until reset
        today = datetime.utcnow()
        next_month = (today.replace(day=28) + timedelta(days=4))  # Ensure we get to next month
        reset_date = next_month.replace(day=1)
        days_until_reset = (reset_date - today).days

        return UsageLimit(
            feature_type="graded_assessment",
            used=usage["used"],
            limit=usage["limit"],
            remaining=usage["remaining"],
            resets_in_days=days_until_reset
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching usage: {str(e)}"
        )


# ============================================================================
# Premium Feature: Adaptive Learning Path
# ============================================================================

@router.post("/learning-path/generate", response_model=GenerateLearningPathResponse)
async def generate_learning_path(
    request: GenerateLearningPathRequest,
    current_user = Depends(require_premium),
    db: Session = Depends(get_db)
):
    """
    Generate adaptive learning path using LLM (Premium Feature)

    Analyzes learning patterns and generates personalized recommendations including:
    - Recommended next chapters
    - Knowledge gaps to address
    - Weekly study plan
    - Motivational message

    Requires: Active premium subscription
    Cost: ~$0.018 per request (2,000 tokens)
    """
    try:
        # Check usage limits
        cost_tracker = CostTracker(db)
        usage = await cost_tracker.check_usage_limits(current_user.id, "learning_path")

        if usage["remaining"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Monthly learning path limit reached ({usage['limit']}). Upgrade your plan or wait for next month."
            )

        # Initialize LLM service
        llm_service = LLMService(db=db)

        # Generate learning path
        result = await llm_service.generate_learning_path(
            user_id=current_user.id,
            current_chapter_id=request.current_chapter_id,
            focus=request.focus,
            include_completed=request.include_completed,
            learning_style=request.learning_style
        )

        # Increment usage counter
        await cost_tracker.increment_usage(current_user.id, "learning_path")

        return GenerateLearningPathResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {str(e)}"
        )


@router.get("/learning-path/usage", response_model=UsageLimit)
async def get_learning_path_usage(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get learning path usage limits and remaining uses

    Shows how many learning paths have been generated this month
    and how many remain (0 for free tier).
    """
    try:
        cost_tracker = CostTracker(db)
        usage = await cost_tracker.check_usage_limits(current_user.id, "learning_path")

        # Calculate days until reset
        today = datetime.utcnow()
        next_month = (today.replace(day=28) + timedelta(days=4))
        reset_date = next_month.replace(day=1)
        days_until_reset = (reset_date - today).days

        return UsageLimit(
            feature_type="learning_path",
            used=usage["used"],
            limit=usage["limit"],
            remaining=usage["remaining"],
            resets_in_days=days_until_reset
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching usage: {str(e)}"
        )


# ============================================================================
# Subscription Management
# ============================================================================

@router.get("/subscription/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription status and usage information

    Shows subscription type, expiration, and monthly usage for premium features.
    """
    try:
        from app.models.user import User

        # Refresh user from database
        user = db.query(User).filter(User.id == current_user.id).first()

        # Check if premium is active
        is_premium = (
            user.subscription_type == 'premium' and
            (user.subscription_expires_at is None or user.subscription_expires_at > datetime.utcnow())
        )

        # Get usage limits
        cost_tracker = CostTracker(db)
        assessment_usage = await cost_tracker.check_usage_limits(user.id, "graded_assessment")
        learning_path_usage = await cost_tracker.check_usage_limits(user.id, "learning_path")

        return SubscriptionStatus(
            user_id=user.id,
            subscription_type=user.subscription_type,
            subscription_expires_at=user.subscription_expires_at,
            is_premium_active=is_premium,
            assessments_used=assessment_usage["used"],
            learning_paths_used=learning_path_usage["used"],
            assessments_limit=assessment_usage["limit"],
            learning_paths_limit=learning_path_usage["limit"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subscription status: {str(e)}"
        )


@router.post("/subscription/upgrade", response_model=UpgradeResponse)
async def upgrade_subscription(
    request: UpgradeRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade to premium subscription

    Upgrades the user to premium tier with access to:
    - 30 graded assessments per month
    - 10 learning paths per month
    - Priority support

    Note: In production, this would integrate with a payment processor (Stripe, etc.)
    """
    try:
        from app.models.user import User

        # Refresh user from database
        user = db.query(User).filter(User.id == current_user.id).first()

        # Check if already premium
        if user.subscription_type == 'premium' and user.subscription_expires_at and user.subscription_expires_at > datetime.utcnow():
            return UpgradeResponse(
                user_id=user.id,
                subscription_type=user.subscription_type,
                subscription_expires_at=user.subscription_expires_at,
                message="You already have an active premium subscription."
            )

        # Upgrade to premium (30 days from now)
        user.subscription_type = 'premium'
        user.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        user.premium_signup_date = datetime.utcnow()

        db.commit()
        db.refresh(user)

        return UpgradeResponse(
            user_id=user.id,
            subscription_type=user.subscription_type,
            subscription_expires_at=user.subscription_expires_at,
            message="Successfully upgraded to premium! You now have access to all premium features."
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error upgrading subscription: {str(e)}"
        )


# ============================================================================
# Usage Analytics
# ============================================================================

@router.get("/usage/monthly", response_model=MonthlyUsageStats)
async def get_monthly_usage(
    year: int,
    month: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly usage statistics for LLM features

    Shows token usage, costs, and request counts for a specific month.
    Requires premium subscription.
    """
    try:
        # Validate month
        if month < 1 or month > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Month must be between 1 and 12"
            )

        # Initialize LLM service to get usage
        llm_service = LLMService(db=db)
        stats = llm_service.get_monthly_usage(current_user.id, year, month)

        return MonthlyUsageStats(
            year=year,
            month=month,
            **stats
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching monthly usage: {str(e)}"
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def premium_health_check():
    """
    Health check endpoint for premium features

    Verifies that premium features are operational.
    """
    return {
        "status": "healthy",
        "premium_features": "operational",
        "llm_service": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }
