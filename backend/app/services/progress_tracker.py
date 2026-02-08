"""
Progress Tracking Service

Business logic for tracking user progress, streaks, and milestones.
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID
import pytz

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.progress import ChapterProgress
from app.models.streak import Streak
from app.models.quiz import QuizAttempt

logger = logging.getLogger(__name__)

# Total chapters in the course
TOTAL_CHAPTERS = 6

# Milestone thresholds (in days)
MILESTONES = [
    {"days": 3, "name": "3-Day Streak", "message": "🔥 Amazing! You've maintained a 3-day learning streak!"},
    {"days": 7, "name": "Week Warrior", "message": "⭐ Incredible! A full week of consistent learning!"},
    {"days": 14, "name": "Two Week Champion", "message": "💪 Outstanding! Two weeks of dedication!"},
    {"days": 30, "name": "Month Master", "message": "🏆 Legendary! 30 days of continuous learning!"},
    {"days": 60, "name": "60-Day Legend", "message": "👑 Phenomenal! 60 days of unwavering commitment!"},
    {"days": 100, "name": "Centurion", "message": "💎 Extraordinary! 100 days of learning excellence!"},
]


async def calculate_completion_percentage(
    db: AsyncSession,
    user_id: UUID,
) -> Dict[str, Any]:
    """
    Calculate overall course completion percentage.

    Formula: (completed_chapters / total_chapters) * 100

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        Dictionary with completion statistics
    """
    # Fetch all chapter progress records
    result = await db.execute(
        select(ChapterProgress).where(ChapterProgress.user_id == user_id)
    )
    progress_records = result.scalars().all()

    # Count completed chapters
    completed_count = sum(1 for p in progress_records if p.is_completed)

    # Count in-progress chapters
    in_progress_count = sum(1 for p in progress_records if p.is_in_progress)

    # Calculate not started
    not_started_count = TOTAL_CHAPTERS - len(progress_records)

    # Calculate overall percentage
    overall_percentage = int((completed_count / TOTAL_CHAPTERS) * 100)

    # Calculate total time spent
    total_time_seconds = sum(p.time_spent_seconds for p in progress_records)

    logger.info(
        f"User {user_id} completion: {completed_count}/{TOTAL_CHAPTERS} chapters "
        f"({overall_percentage}%), {total_time_seconds}s total time"
    )

    return {
        "total_chapters": TOTAL_CHAPTERS,
        "completed_chapters": completed_count,
        "in_progress_chapters": in_progress_count,
        "not_started_chapters": not_started_count,
        "overall_completion_percentage": overall_percentage,
        "total_time_spent_seconds": total_time_seconds,
    }


async def update_streak(
    db: AsyncSession,
    user_id: UUID,
    user_timezone: str = "UTC",
    activity_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Update user's learning streak with timezone awareness.

    Streak rules:
    - Increments by 1 if activity on consecutive day
    - Resets to 1 if gap > 1 day
    - No change if activity on same day

    Args:
        db: Database session
        user_id: User's unique identifier
        user_timezone: User's timezone (e.g., "America/New_York")
        activity_date: Date of activity (defaults to today in user's timezone)

    Returns:
        Dictionary with streak information and milestones
    """
    # Get current date in user's timezone
    if activity_date is None:
        tz = pytz.timezone(user_timezone)
        activity_date = datetime.now(tz).date()

    # Fetch or create streak record
    result = await db.execute(
        select(Streak).where(Streak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    milestone_achieved = None

    if not streak:
        # Create new streak record
        streak = Streak(
            user_id=user_id,
            current_streak=1,
            longest_streak=1,
            total_active_days=1,
            last_activity_date=activity_date,
            timezone=user_timezone,
            is_active=True,
        )
        db.add(streak)
        logger.info(f"Created new streak for user {user_id}")

        # Check for 1-day milestone (first activity)
        milestone_achieved = {
            "name": "First Step",
            "message": "🎉 Welcome! You've started your learning journey!",
        }

    else:
        # Update existing streak
        previous_streak = streak.current_streak

        # Calculate days since last activity
        if streak.last_activity_date:
            days_since_last = (activity_date - streak.last_activity_date).days
        else:
            days_since_last = 1  # First activity

        if days_since_last == 0:
            # Same day, no streak update
            logger.debug(f"User {user_id} activity on same day, no streak update")
        elif days_since_last == 1:
            # Consecutive day, increment streak
            streak.current_streak += 1
            streak.total_active_days += 1
            streak.last_activity_date = activity_date

            # Update longest streak if necessary
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak

            logger.info(
                f"User {user_id} streak incremented: {previous_streak} -> {streak.current_streak}"
            )

            # Check for milestone achievement
            milestone_achieved = _check_milestone(streak.current_streak, previous_streak)

        else:
            # Streak broken, reset to 1
            logger.warning(
                f"User {user_id} streak broken: {previous_streak} days lost "
                f"(gap: {days_since_last} days)"
            )
            streak.current_streak = 1
            streak.total_active_days += 1
            streak.last_activity_date = activity_date

    await db.commit()
    await db.refresh(streak)

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_active_days": streak.total_active_days,
        "last_activity_date": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
        "is_active": streak.is_streak_active,
        "milestone_achieved": milestone_achieved,
    }


def _check_milestone(current_streak: int, previous_streak: int) -> Optional[Dict[str, str]]:
    """
    Check if a milestone was achieved with the latest streak update.

    Args:
        current_streak: Current streak count
        previous_streak: Previous streak count

    Returns:
        Milestone dict if achieved, None otherwise
    """
    for milestone in MILESTONES:
        # Check if we just crossed this milestone threshold
        if current_streak >= milestone["days"] and previous_streak < milestone["days"]:
            logger.info(f"Milestone achieved: {milestone['name']} ({milestone['days']} days)")
            return {
                "name": milestone["name"],
                "message": milestone["message"],
                "days": milestone["days"],
            }

    return None


def get_milestone_encouragement(current_streak: int) -> Dict[str, Any]:
    """
    Get encouragement message based on current streak.

    Returns current milestone status and progress to next milestone.

    Args:
        current_streak: Current streak count

    Returns:
        Dictionary with milestone information
    """
    # Find achieved milestones
    achieved_milestones = [
        m for m in MILESTONES if current_streak >= m["days"]
    ]

    # Find next milestone
    next_milestone = None
    for milestone in MILESTONES:
        if current_streak < milestone["days"]:
            next_milestone = milestone
            break

    if next_milestone:
        days_to_next = next_milestone["days"] - current_streak
        progress_percentage = int((current_streak / next_milestone["days"]) * 100)
    else:
        # All milestones achieved
        days_to_next = 0
        progress_percentage = 100

    return {
        "current_streak": current_streak,
        "achieved_milestones": [
            {"name": m["name"], "days": m["days"], "message": m["message"]}
            for m in achieved_milestones
        ],
        "next_milestone": {
            "name": next_milestone["name"],
            "days": next_milestone["days"],
            "days_remaining": days_to_next,
            "progress_percentage": progress_percentage,
        } if next_milestone else None,
    }


async def get_progress_summary(
    db: AsyncSession,
    user_id: UUID,
    user_timezone: str = "UTC",
) -> Dict[str, Any]:
    """
    Get comprehensive progress summary including chapters, quizzes, and streaks.

    Args:
        db: Database session
        user_id: User's unique identifier
        user_timezone: User's timezone for streak calculation

    Returns:
        Complete progress summary
    """
    # Get chapter completion stats
    completion_stats = await calculate_completion_percentage(db, user_id)

    # Get all chapter progress records
    result = await db.execute(
        select(ChapterProgress)
        .where(ChapterProgress.user_id == user_id)
        .order_by(ChapterProgress.chapter_id)
    )
    chapter_progress = result.scalars().all()

    # Get streak information
    result = await db.execute(
        select(Streak).where(Streak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()

    if streak:
        streak_info = {
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "total_active_days": streak.total_active_days,
            "last_activity_date": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
            "is_active": streak.is_streak_active,
        }
        milestone_info = get_milestone_encouragement(streak.current_streak)
    else:
        streak_info = {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "last_activity_date": None,
            "is_active": False,
        }
        milestone_info = get_milestone_encouragement(0)

    # Get quiz statistics
    result = await db.execute(
        select(func.count(QuizAttempt.id))
        .where(QuizAttempt.user_id == user_id)
        .where(QuizAttempt.passed == True)
    )
    quizzes_passed = result.scalar() or 0

    result = await db.execute(
        select(func.count(QuizAttempt.id))
        .where(QuizAttempt.user_id == user_id)
    )
    total_quiz_attempts = result.scalar() or 0

    # Get all quiz attempts to calculate scores per chapter
    # Order by attempt_number DESC to get the LATEST attempt first
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.attempt_number.desc())
    )
    quiz_attempts = result.scalars().all()

    # Build quiz_scores dict with LATEST score per chapter (most recent attempt)
    quiz_scores = {}
    quiz_attempts_by_chapter = {}  # Track attempts by chapter

    for attempt in quiz_attempts:
        chapter_id = attempt.chapter_id

        # Group attempts by chapter
        if chapter_id not in quiz_attempts_by_chapter:
            quiz_attempts_by_chapter[chapter_id] = []
        quiz_attempts_by_chapter[chapter_id].append(attempt)

        # Store the LATEST score (first one since ordered by attempt_number desc)
        if chapter_id not in quiz_scores:
            quiz_scores[chapter_id] = attempt.score_percentage

    # Add recent quiz attempts for display
    recent_quiz_attempts = []
    for attempt in quiz_attempts[:5]:  # Last 5 attempts
        recent_quiz_attempts.append({
            "quiz_id": attempt.quiz_id,
            "chapter_id": attempt.chapter_id,
            "score_percentage": attempt.score_percentage,
            "passed": attempt.passed,
            "attempt_number": attempt.attempt_number,
            "submitted_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        })

    return {
        **completion_stats,
        "quiz_scores": quiz_scores,
        "recent_quiz_attempts": recent_quiz_attempts,
        "chapters": [
            {
                "chapter_id": p.chapter_id,
                "completion_percentage": p.completion_percentage,
                "is_completed": p.is_completed,
                "time_spent_seconds": p.time_spent_seconds,
                "started_at": p.started_at.isoformat(),
                "completed_at": p.completed_at.isoformat() if p.completed_at else None,
            }
            for p in chapter_progress
        ],
        # Flatten streak info for frontend compatibility
        "current_streak": streak_info["current_streak"],
        "longest_streak": streak_info["longest_streak"],
        "total_active_days": streak_info["total_active_days"],
        "last_activity_date": streak_info["last_activity_date"],
        # Add flattened completion percentage
        "completion_percentage": completion_stats["overall_completion_percentage"],
        "chapters_completed": completion_stats["completed_chapters"],
        # Keep nested versions for detailed views
        "streak": streak_info,
        "milestones": milestone_info,
        "quiz_stats": {
            "total_attempts": total_quiz_attempts,
            "quizzes_passed": quizzes_passed,
            "pass_rate": int((quizzes_passed / total_quiz_attempts * 100)) if total_quiz_attempts > 0 else 0,
        },
        # Frontend expects chapter_progress (alias for chapters)
        "chapter_progress": [
            {
                "chapter_id": p.chapter_id,
                "completion_status": "completed" if p.is_completed else "in_progress" if p.is_in_progress else "not_started",
                "completion_percent": p.completion_percentage,
                "quiz_score": quiz_scores.get(p.chapter_id),
                "time_spent_minutes": p.time_spent_seconds // 60,
                "last_accessed": (p.completed_at or p.started_at).isoformat() if (p.completed_at or p.started_at) else None,
            }
            for p in chapter_progress
        ],
    }


async def record_activity(
    db: AsyncSession,
    user_id: UUID,
    user_timezone: str = "UTC",
) -> None:
    """
    Record user activity for streak tracking.

    Should be called whenever user performs a learning action
    (accesses chapter, submits quiz, etc.)

    Args:
        db: Database session
        user_id: User's unique identifier
        user_timezone: User's timezone
    """
    streak_update = await update_streak(db, user_id, user_timezone)

    if streak_update.get("milestone_achieved"):
        logger.info(
            f"🎉 User {user_id} achieved milestone: {streak_update['milestone_achieved']['name']}"
        )
