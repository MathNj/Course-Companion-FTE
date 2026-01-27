"""
Adaptive Learning Path Router

API endpoints for generating personalized learning recommendations.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.database import get_db
from app.dependencies import get_current_user, verify_premium, verify_quota
from app.services.llm.adaptive_path_generator import AdaptivePathGenerator
from app.schemas.adaptive import (
    AdaptivePathRequest,
    AdaptivePathResponse,
    InsufficientDataError
)
from app.models.user import User

router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning Paths"])


@router.post("/path", response_model=AdaptivePathResponse)
async def generate_adaptive_path(
    request: AdaptivePathRequest,
    current_user: User = Depends(get_current_user),
    _premium_verified = Depends(verify_premium),
    _quota_verified = Depends(verify_quota),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized adaptive learning path based on student performance.

    This endpoint analyzes:
    - Quiz scores (identifies weak areas < 60%)
    - Time spent per chapter (identifies struggles >1.5x average)
    - Learning progression (suggests prerequisites)

    **Response**:
    - 3-5 prioritized recommendations
    - Specific chapter/section suggestions
    - Reasoning for each recommendation
    - Estimated completion time

    **Rate Limiting**: 10 requests per premium user per month

    **Caching**: Results cached for 24 hours (use force_refresh=true to regenerate)

    Raises:
        403: If user doesn't have premium subscription
        400: If insufficient learning data (<2 quizzes completed)
        429: If monthly quota exceeded
        503: If Claude API is temporarily unavailable
    """
    try:
        # Generate adaptive path
        path_data = await AdaptivePathGenerator.generate_path(
            db=db,
            student_id=str(current_user.id),
            force_refresh=request.force_refresh,
            current_user=current_user
        )

        return path_data

    except ValueError as e:
        # Handle insufficient data error
        if "insufficient" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INSUFFICIENT_DATA",
                    "message": str(e),
                    "required_quizzes": 2,
                    "next_steps": [
                        "Complete Chapter 1 quiz",
                        "Complete Chapter 2 quiz",
                        "Return to request adaptive path after completing more content"
                    ]
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_REQUEST", "message": str(e)}
            )

    except Exception as e:
        # Handle LLM service errors
        logger.error(f"Error generating adaptive path: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "LLM_SERVICE_UNAVAILABLE",
                "message": "The recommendation service is temporarily unavailable. Your progress is saved, and you can continue learning with standard content. Try again in a few minutes for adaptive guidance.",
                "retry_after": 60  # Suggest retry in 60 seconds
            }
        )


@router.get("/path/latest", response_model=AdaptivePathResponse)
async def get_latest_adaptive_path(
    current_user: User = Depends(get_current_user),
    _premium_verified = Depends(verify_premium),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent adaptive path for the current student.

    Returns the latest generated path (if still valid) or 404 if no active path exists.
    """
    from sqlalchemy import select, desc
    from app.models.llm import AdaptivePath

    # Get most recent path
    result = await db.execute(
        select(AdaptivePath)
        .where(AdaptivePath.student_id == current_user.id)
        .where(AdaptivePath.status == "active")
        .where(AdaptivePath.expires_at > datetime.now())
        .order_by(desc(AdaptivePath.generated_at))
        .limit(1)
    )

    path = result.scalar_one_or_none()

    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NO_ACTIVE_PATH",
                "message": "No active adaptive path found. Generate one with POST /api/v2/adaptive/path"
            }
        )

    # Build response
    return {
        "path_id": str(path.path_id),
        "student_id": str(path.student_id),
        "generated_at": path.generated_at.isoformat(),
        "expires_at": path.expires_at.isoformat(),
        "status": path.status,
        "recommendations": path.recommendations_json,
        "reasoning": path.reasoning,
        "metadata": {
            "total_recommendations": len(path.recommendations_json),
            "high_priority_count": sum(1 for r in path.recommendations_json if r.get("priority") == 1),
            "estimated_total_time_minutes": sum(r.get("estimated_time_minutes", 0) for r in path.recommendations_json),
            "cached": True  # Latest path from database is considered cached
        }
    }
