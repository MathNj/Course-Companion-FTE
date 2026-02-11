"""
Progress Tracking Endpoints

REST API for user progress, streaks, and milestones.
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_user, get_optional_user
from app.models.user import User
from app.models.streak import Streak
from app.services.progress_tracker import (
    get_progress_summary,
    update_streak,
    get_milestone_encouragement,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("", response_model=Dict[str, Any])
async def get_progress(
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive progress summary for the current user.

    Returns:
    - Chapter completion statistics
    - All chapter progress records
    - Streak information
    - Milestone achievements
    - Quiz statistics

    For unauthenticated users, returns demo data.
    """
    if not current_user:
        # Return demo progress for unauthenticated users
        return {
            "chapters_completed": 0,
            "total_chapters": 6,
            "completion_percentage": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "last_activity_date": None,
            "milestones": [],
            "chapters": [],
            "quiz_stats": {
                "quizzes_taken": 0,
                "quizzes_passed": 0,
                "average_score": 0
            },
            "message": "Sign in to track your progress!"
        }

    logger.info(f"Fetching progress for user {current_user.id}")

    # Record activity for streak tracking
    # (Viewing progress counts as learning activity)
    await update_streak(db, current_user.id, current_user.timezone)

    # Get complete progress summary
    progress_summary = await get_progress_summary(
        db,
        current_user.id,
        current_user.timezone,
    )

    # Ensure completed_sections is always returned as a JSON array for frontend compatibility
    return progress_summary


@router.get("/streak", response_model=Dict[str, Any])
async def get_streak_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed streak information for the current user.

    Returns:
    - Current streak count
    - Longest streak achieved
    - Total active days
    - Last activity date
    - Milestone achievements
    - Progress to next milestone
    """
    logger.info(f"Fetching streak details for user {current_user.id}")

    # Fetch streak record
    result = await db.execute(
        select(Streak).where(Streak.user_id == current_user.id)
    )
    streak = result.scalar_one_or_none()

    if not streak:
        # No streak yet, return empty state
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "last_activity_date": None,
            "is_active": False,
            "streak_freeze_count": 0,
            "milestones": get_milestone_encouragement(0),
        }

    # Get milestone information
    milestone_info = get_milestone_encouragement(streak.current_streak)

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_active_days": streak.total_active_days,
        "last_activity_date": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
        "is_active": streak.is_streak_active,
        "streak_freeze_count": streak.streak_freeze_count,
        "timezone": streak.timezone,
        "milestones": milestone_info,
    }


@router.get("/chapters/{chapter_id}", response_model=Dict[str, Any])
async def get_chapter_progress(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed progress for a specific chapter.

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1")

    Returns:
        Detailed chapter progress including:
        - Completion percentage
        - Time spent
        - Quiz attempts for this chapter
        - Start and completion timestamps
        - Completed sections
    """
    from app.models.progress import ChapterProgress
    from app.models.quiz import QuizAttempt
    from sqlalchemy import func, desc

    logger.info(f"Fetching chapter {chapter_id} progress for user {current_user.id}")

    # Validate chapter_id
    try:
        chapter_num = int(chapter_id.split("-")[1])
        if not (1 <= chapter_num <= 6):
            raise ValueError("Invalid chapter number")
    except (IndexError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid chapter_id format. Expected: 'chapter-N' where N is 1-6",
        )

    # Fetch chapter progress
    result = await db.execute(
        select(ChapterProgress)
        .where(ChapterProgress.user_id == current_user.id)
        .where(ChapterProgress.chapter_id == chapter_id)
    )
    chapter_progress = result.scalar_one_or_none()

    if not chapter_progress:
        # Chapter not started yet
        return {
            "chapter_id": chapter_id,
            "status": "not_started",
            "completion_percentage": 0,
            "time_spent_seconds": 0,
            "is_completed": False,
            "started_at": None,
            "completed_at": None,
            "quiz_attempts": [],
            "completed_sections": [],
        }

    # Fetch quiz attempts for this chapter
    quiz_id = f"{chapter_id}-quiz"
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == current_user.id)
        .where(QuizAttempt.quiz_id == quiz_id)
        .order_by(desc(QuizAttempt.created_at))
    )
    quiz_attempts = result.scalars().all()

    # Build quiz attempts summary
    quiz_attempts_summary = [
        {
            "attempt_number": attempt.attempt_number,
            "score_percentage": float(attempt.score_percentage) if attempt.score_percentage else 0.0,
            "passed": attempt.passed,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        }
        for attempt in quiz_attempts
    ]

    # Determine status
    if chapter_progress.is_completed:
        status_text = "completed"
    elif chapter_progress.completion_percentage > 0:
        status_text = "in_progress"
    else:
        status_text = "not_started"

    return {
        "chapter_id": chapter_id,
        "status": status_text,
        "completion_percentage": chapter_progress.completion_percentage,
        "time_spent_seconds": chapter_progress.time_spent_seconds,
        "is_completed": chapter_progress.is_completed,
        "started_at": chapter_progress.started_at.isoformat(),
        "completed_at": chapter_progress.completed_at.isoformat() if chapter_progress.completed_at else None,
        "current_section_id": chapter_progress.current_section_id,
        "completed_sections": chapter_progress.completed_sections or {},
        "quiz_attempts": quiz_attempts_summary,
        "best_quiz_score": max((a["score_percentage"] for a in quiz_attempts_summary), default=None),
        "quiz_passed": any(a["passed"] for a in quiz_attempts_summary),
    }


@router.post("/chapters/{chapter_id}/sections/{section_id}/complete", response_model=Dict[str, Any])
async def mark_section_complete(
    chapter_id: str,
    section_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a section as completed for the current user.

    Args:
        chapter_id: Chapter identifier (e.g., "chapter-1")
        section_id: Section identifier (e.g., "section-1-1")

    Returns:
        Updated chapter progress with completion status
    """
    from app.models.progress import ChapterProgress
    from datetime import datetime
    from sqlalchemy import select

    logger.info(f"Marking section {section_id} as complete for user {current_user.id}")

    # Get or create chapter progress
    result = await db.execute(
        select(ChapterProgress)
        .where(ChapterProgress.user_id == current_user.id)
        .where(ChapterProgress.chapter_id == chapter_id)
    )
    chapter_progress = result.scalar_one_or_none()

    if not chapter_progress:
        # Create new progress record
        chapter_progress = ChapterProgress(
            user_id=current_user.id,
            chapter_id=chapter_id,
            started_at=datetime.utcnow(),
            current_section_id=section_id,
            completed_sections={section_id: datetime.utcnow().isoformat()},
            time_spent_seconds=0,
            completion_percentage=10,  # Initial progress
        )
        db.add(chapter_progress)
    else:
        # Update existing progress
        if not chapter_progress.completed_sections:
            chapter_progress.completed_sections = {}

        # Mark section as complete if not already marked
        if section_id not in chapter_progress.completed_sections:
            chapter_progress.completed_sections[section_id] = datetime.utcnow().isoformat()

        # Update current section
        chapter_progress.current_section_id = section_id

        # Recalculate completion percentage based on completed sections
        total_sections = len(chapter_progress.completed_sections)
        # Assume roughly 5 sections per chapter for progress calculation
        chapter_progress.completion_percentage = min(95, total_sections * 20)

    await db.commit()
    await db.refresh(chapter_progress)

    return {
        "chapter_id": chapter_id,
        "section_id": section_id,
        "completed": True,
        "completed_sections": chapter_progress.completed_sections,
        "completion_percentage": chapter_progress.completion_percentage,
        "message": "Section marked as complete",
    }


@router.post("/activity", response_model=Dict[str, Any])
async def record_learning_activity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually record a learning activity to update streak.

    This endpoint allows explicit streak updates when user
    performs learning activities that don't trigger automatic updates.

    Returns:
        Updated streak information including any achieved milestones
    """
    logger.info(f"Recording learning activity for user {current_user.id}")

    # Update streak
    streak_info = await update_streak(db, current_user.id, current_user.timezone)

    # Add milestone encouragement
    milestone_details = get_milestone_encouragement(streak_info["current_streak"])

    return {
        **streak_info,
        "milestones": milestone_details,
        "message": "Activity recorded successfully!",
    }
