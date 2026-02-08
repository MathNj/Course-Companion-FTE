"""
Milestone Endpoints

REST API for user achievements and milestones.
"""

import logging
from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.models.milestone import Milestone
from app.services.milestone_service import (
    get_user_milestones,
    get_achievable_milestones,
    get_next_milestones,
    check_time_milestones,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/milestones", tags=["milestones"])


# Response schemas
class MilestoneResponse(BaseModel):
    """Schema for milestone response."""
    id: str
    milestone_type: str
    display_name: str
    message: str
    icon_emoji: str
    achieved_at: str
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, milestone: Milestone) -> "MilestoneResponse":
        """Create response from Milestone model."""
        return cls(
            id=str(milestone.id),
            milestone_type=milestone.milestone_type,
            display_name=milestone.display_name,
            message=milestone.message,
            icon_emoji=milestone.icon_emoji,
            achieved_at=milestone.achieved_at.isoformat(),
            metadata=milestone.metadata or {},
        )


class MilestoneCategory(BaseModel):
    """Schema for milestone category (chapters, quizzes, streaks, etc.)."""
    type: str
    name: str
    icon: str
    achieved: bool = False
    progress: int = 0
    total: int = 0
    progress_percent: int = 0
    description: str = ""


class AchievableMilestonesResponse(BaseModel):
    """Schema for achievable milestones response."""
    chapters: List[MilestoneCategory] = []
    quizzes: List[MilestoneCategory] = []
    streaks: List[MilestoneCategory] = []
    time: List[MilestoneCategory] = []
    badges: List[MilestoneCategory] = []


class NextMilestonesResponse(BaseModel):
    """Schema for next milestones response."""
    next_milestones: List[MilestoneCategory] = []


@router.get("", response_model=List[MilestoneResponse])
async def get_milestones(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all milestones achieved by the current user.

    Returns milestones ordered by achievement date (most recent first).
    Each milestone includes:
    - Display name and congratulatory message
    - Icon emoji for visual display
    - Achievement timestamp
    - Metadata (chapter ID, score, etc.)
    """
    logger.info(f"Fetching milestones for user {current_user.id}")

    milestones = await get_user_milestones(db, current_user.id)

    return [
        MilestoneResponse.from_orm(milestone)
        for milestone in milestones
    ]


@router.get("/achievable", response_model=AchievableMilestonesResponse)
async def get_achievable(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all milestones user can still achieve with current progress.

    Returns milestones organized by category:
    - **chapters**: Chapter completion milestones
    - **quizzes**: Quiz performance milestones
    - **streaks**: Daily streak milestones
    - **time**: Learning time milestones
    - **badges**: Special achievement badges

    Each milestone includes progress tracking showing how close the user is.
    """
    logger.info(f"Fetching achievable milestones for user {current_user.id}")

    # Also check for any newly achieved time milestones
    await check_time_milestones(db, current_user.id)

    achievable = await get_achievable_milestones(db, current_user.id)

    return AchievableMilestonesResponse(
        chapters=[MilestoneCategory(**m) for m in achievable.get("chapters", [])],
        quizzes=[MilestoneCategory(**m) for m in achievable.get("quizzes", [])],
        streaks=[MilestoneCategory(**m) for m in achievable.get("streaks", [])],
        time=[MilestoneCategory(**m) for m in achievable.get("time", [])],
        badges=[MilestoneCategory(**m) for m in achievable.get("badges", [])],
    )


@router.get("/next", response_model=NextMilestonesResponse)
async def get_next_milestones_endpoint(
    count: int = 3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the next milestones user is closest to achieving.

    Returns up to `count` milestones (default: 3) sorted by proximity.
    Useful for showing personalized goals and motivation on dashboards.

    Query Parameters:
    - **count**: Number of milestones to return (default: 3, max: 10)
    """
    logger.info(f"Fetching next milestones for user {current_user.id}")

    # Limit count to max 10
    count = min(count, 10)

    next_ms = await get_next_milestones(db, current_user.id, count)

    return NextMilestonesResponse(
        next_milestones=[MilestoneCategory(**m) for m in next_ms]
    )


@router.get("/summary", response_model=Dict[str, Any])
async def get_milestone_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a summary of user's milestone achievements.

    Returns:
    - Total milestones achieved
    - Recent milestones (last 5)
    - Next milestones to work on
    - Completion percentage across all milestone types
    """
    logger.info(f"Fetching milestone summary for user {current_user.id}")

    # Get achieved milestones
    milestones = await get_user_milestones(db, current_user.id)
    next_ms = await get_next_milestones(db, current_user.id, 3)

    # Count by type
    type_counts: Dict[str, int] = {}
    for milestone in milestones:
        mtype = milestone.milestone_type
        type_counts[mtype] = type_counts.get(mtype, 0) + 1

    # Calculate completion percentage
    # Total possible milestones in the system
    total_milestones = 18  # Count of all defined milestone types
    completion_percent = int((len(milestones) / total_milestones) * 100)

    return {
        "total_achieved": len(milestones),
        "total_possible": total_milestones,
        "completion_percentage": completion_percent,
        "recent_milestones": [
            MilestoneResponse.from_orm(m)
            for m in milestones[:5]
        ],
        "next_milestones": [MilestoneCategory(**m) for m in next_ms],
        "achievements_by_type": type_counts,
    }


@router.post("/check", response_model=Dict[str, Any])
async def check_for_new_milestones(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually check for any newly achieved milestones.

    This endpoint triggers milestone checks for all categories.
    Useful after batch updates or data migrations.

    Returns any newly awarded milestones.
    """
    logger.info(f"Manual milestone check for user {current_user.id}")

    from app.services.milestone_service import (
        check_streak_milestones,
    )
    from app.models.streak import Streak
    from sqlalchemy import select

    # Check time milestones
    time_milestones = await check_time_milestones(db, current_user.id)

    # Check streak milestones
    result = await db.execute(
        select(Streak).where(Streak.user_id == current_user.id)
    )
    streak = result.scalar_one_or_none()

    streak_milestone = None
    if streak:
        streak_milestone = await check_streak_milestones(
            db, current_user.id, streak.current_streak, streak.current_streak - 1
        )

    new_milestones = time_milestones
    if streak_milestone:
        new_milestones.append(streak_milestone)

    return {
        "new_milestones": [
            MilestoneResponse.from_orm(m)
            for m in new_milestones
        ],
        "total_new": len(new_milestones),
    }
