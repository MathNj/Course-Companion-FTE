"""
Milestone Service

Detects and awards user achievements based on learning progress.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.milestone import Milestone, MilestoneType
from app.models.progress import ChapterProgress
from app.models.quiz import QuizAttempt
from app.models.streak import Streak

logger = logging.getLogger(__name__)

# Total chapters and quizzes in course
TOTAL_CHAPTERS = 6
TOTAL_QUIZZES = 6

# Hour thresholds for time milestones
HOUR_MILESTONES = {
    1: MilestoneType.FIRST_HOUR,
    10: MilestoneType.TEN_HOURS,
    100: MilestoneType.HUNDRED_HOURS,
}

# Streak milestones
STREAK_MILESTONES = {
    3: MilestoneType.STREAK_3,
    7: MilestoneType.STREAK_7,
    14: MilestoneType.STREAK_14,
    30: MilestoneType.STREAK_30,
    60: MilestoneType.STREAK_60,
    100: MilestoneType.STREAK_100,
}


async def check_and_award_milestone(
    db: AsyncSession,
    user_id: UUID,
    milestone_type: MilestoneType,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Milestone]:
    """
    Check if user has already achieved a milestone type and award it if not.

    Args:
        db: Database session
        user_id: User's unique identifier
        milestone_type: Type of milestone to check/award
        metadata: Optional additional data for the milestone

    Returns:
        Milestone if newly awarded, None if already achieved
    """
    # Check if already achieved
    result = await db.execute(
        select(Milestone).where(
            and_(
                Milestone.user_id == user_id,
                Milestone.milestone_type == milestone_type.value
            )
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        logger.debug(f"User {user_id} already achieved milestone {milestone_type.value}")
        return None

    # Award new milestone
    milestone = Milestone(
        user_id=user_id,
        milestone_type=milestone_type.value,
        metadata=metadata or {},
        is_notified=False,
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)

    logger.info(f"🎉 Awarded milestone {milestone_type.value} to user {user_id}")
    return milestone


async def get_user_milestones(
    db: AsyncSession,
    user_id: UUID,
) -> List[Milestone]:
    """
    Get all milestones achieved by a user, ordered by achievement date.

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        List of achieved milestones
    """
    result = await db.execute(
        select(Milestone)
        .where(Milestone.user_id == user_id)
        .order_by(Milestone.achieved_at.desc())
    )
    return result.scalars().all()


async def get_achievable_milestones(
    db: AsyncSession,
    user_id: UUID,
) -> Dict[str, Any]:
    """
    Get all milestones user can still achieve with their current progress.

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        Dictionary with available milestones and user's progress toward each
    """
    # Get user's current state
    completed_chapters = await _get_completed_chapters_count(db, user_id)
    total_time_hours = await _get_total_time_hours(db, user_id)
    perfect_quizzes = await _get_perfect_quiz_count(db, user_id)
    passed_quizzes = await _get_passed_quiz_count(db, user_id)
    current_streak = await _get_current_streak(db, user_id)

    # Get already achieved milestone types
    achieved_types = await _get_achieved_milestone_types(db, user_id)

    # Build achievable milestones
    achievable = {
        "chapters": [],
        "quizzes": [],
        "streaks": [],
        "time": [],
        "badges": [],
    }

    # Chapter milestones
    if MilestoneType.FIRST_CHAPTER not in achieved_types:
        if completed_chapters >= 1:
            achievable["chapters"].append({
                "type": MilestoneType.FIRST_CHAPTER.value,
                "name": "First Chapter Complete",
                "icon": "📖",
                "achieved": True,
            })
        else:
            achievable["chapters"].append({
                "type": MilestoneType.FIRST_CHAPTER.value,
                "name": "First Chapter Complete",
                "icon": "📖",
                "progress": completed_chapters,
                "total": 1,
                "achieved": False,
            })

    if MilestoneType.THREE_CHAPTERS not in achieved_types:
        if completed_chapters >= 3:
            achievable["chapters"].append({
                "type": MilestoneType.THREE_CHAPTERS.value,
                "name": "Three Chapters Down",
                "icon": "📚",
                "achieved": True,
            })
        else:
            achievable["chapters"].append({
                "type": MilestoneType.THREE_CHAPTERS.value,
                "name": "Three Chapters Down",
                "icon": "📚",
                "progress": completed_chapters,
                "total": 3,
                "achieved": False,
            })

    if MilestoneType.SIX_CHAPTERS not in achieved_types:
        if completed_chapters >= 6:
            achievable["chapters"].append({
                "type": MilestoneType.SIX_CHAPTERS.value,
                "name": "Course Complete!",
                "icon": "🎓",
                "achieved": True,
            })
        else:
            achievable["chapters"].append({
                "type": MilestoneType.SIX_CHAPTERS.value,
                "name": "Course Complete!",
                "icon": "🎓",
                "progress": completed_chapters,
                "total": 6,
                "achieved": False,
            })

    # Quiz milestones
    if MilestoneType.FIRST_QUIZ not in achieved_types:
        if passed_quizzes >= 1:
            achievable["quizzes"].append({
                "type": MilestoneType.FIRST_QUIZ.value,
                "name": "First Quiz Passed",
                "icon": "⭐",
                "achieved": True,
            })
        else:
            achievable["quizzes"].append({
                "type": MilestoneType.FIRST_QUIZ.value,
                "name": "First Quiz Passed",
                "icon": "⭐",
                "progress": passed_quizzes,
                "total": 1,
                "achieved": False,
            })

    if MilestoneType.PERFECT_QUIZ not in achieved_types:
        if perfect_quizzes >= 1:
            achievable["quizzes"].append({
                "type": MilestoneType.PERFECT_QUIZ.value,
                "name": "Perfect Score",
                "icon": "💯",
                "achieved": True,
            })
        else:
            achievable["quizzes"].append({
                "type": MilestoneType.PERFECT_QUIZ.value,
                "name": "Perfect Score",
                "icon": "💯",
                "achieved": False,
            })

    if MilestoneType.ALL_QUIZES_PASSED not in achieved_types:
        if passed_quizzes >= TOTAL_QUIZZES:
            achievable["quizzes"].append({
                "type": MilestoneType.ALL_QUIZES_PASSED.value,
                "name": "Quiz Master",
                "icon": "🏅",
                "achieved": True,
            })
        else:
            achievable["quizzes"].append({
                "type": MilestoneType.ALL_QUIZES_PASSED.value,
                "name": "Quiz Master",
                "icon": "🏅",
                "progress": passed_quizzes,
                "total": TOTAL_QUIZZES,
                "achieved": False,
            })

    # Streak milestones
    for days, milestone_type in STREAK_MILESTONES.items():
        if milestone_type not in achieved_types:
            if current_streak >= days:
                achievable["streaks"].append({
                    "type": milestone_type.value,
                    "name": milestone_type.value.replace("_", " ").title(),
                    "icon": "🔥" if days <= 7 else "🏆" if days >= 30 else "⭐",
                    "achieved": True,
                })
            else:
                achievable["streaks"].append({
                    "type": milestone_type.value,
                    "name": milestone_type.value.replace("_", " ").title(),
                    "icon": "🔥" if days <= 7 else "🏆" if days >= 30 else "⭐",
                    "progress": current_streak,
                    "total": days,
                    "achieved": False,
                })

    # Time milestones
    for hours, milestone_type in HOUR_MILESTONES.items():
        if milestone_type not in achieved_types:
            if total_time_hours >= hours:
                achievable["time"].append({
                    "type": milestone_type.value,
                    "name": milestone_type.value.replace("_", " ").title(),
                    "icon": "⏱️" if hours == 1 else "⏳" if hours == 10 else "🌟",
                    "achieved": True,
                })
            else:
                achievable["time"].append({
                    "type": milestone_type.value,
                    "name": milestone_type.value.replace("_", " ").title(),
                    "icon": "⏱️" if hours == 1 else "⏳" if hours == 10 else "🌟",
                    "progress": total_time_hours,
                    "total": hours,
                    "achieved": False,
                })

    # Special achievement badges
    if MilestoneType.PERFECTIONIST not in achieved_types:
        if perfect_quizzes >= 3:
            achievable["badges"].append({
                "type": MilestoneType.PERFECTIONIST.value,
                "name": "Perfectionist",
                "icon": "🎯",
                "description": "Achieve 3 perfect quiz scores",
                "achieved": True,
            })
        else:
            achievable["badges"].append({
                "type": MilestoneType.PERFECTIONIST.value,
                "name": "Perfectionist",
                "icon": "🎯",
                "description": "Achieve 3 perfect quiz scores",
                "progress": perfect_quizzes,
                "total": 3,
                "achieved": False,
            })

    if MilestoneType.CONSISTENT_LEARNER not in achieved_types:
        if current_streak >= 7:
            achievable["badges"].append({
                "type": MilestoneType.CONSISTENT_LEARNER.value,
                "name": "Consistent Learner",
                "icon": "📅",
                "description": "Maintain a 7-day streak",
                "achieved": True,
            })
        else:
            achievable["badges"].append({
                "type": MilestoneType.CONSISTENT_LEARNER.value,
                "name": "Consistent Learner",
                "icon": "📅",
                "description": "Maintain a 7-day streak",
                "progress": current_streak,
                "total": 7,
                "achieved": False,
            })

    if MilestoneType.KNOWLEDGE_SEEKER not in achieved_types:
        if completed_chapters >= TOTAL_CHAPTERS:
            achievable["badges"].append({
                "type": MilestoneType.KNOWLEDGE_SEEKER.value,
                "name": "Knowledge Seeker",
                "icon": "🧠",
                "description": "Complete all chapters",
                "achieved": True,
            })
        else:
            achievable["badges"].append({
                "type": MilestoneType.KNOWLEDGE_SEEKER.value,
                "name": "Knowledge Seeker",
                "icon": "🧠",
                "description": "Complete all chapters",
                "progress": completed_chapters,
                "total": TOTAL_CHAPTERS,
                "achieved": False,
            })

    # Quick learner badge (completed a chapter in < 30 min)
    if MilestoneType.QUICK_LEARNER not in achieved_types:
        quick_learned = await _check_quick_learner(db, user_id)
        if quick_learned:
            achievable["badges"].append({
                "type": MilestoneType.QUICK_LEARNER.value,
                "name": "Quick Learner",
                "icon": "⚡",
                "description": "Complete a chapter in under 30 minutes",
                "achieved": True,
            })

    return achievable


async def get_next_milestones(
    db: AsyncSession,
    user_id: UUID,
    count: int = 3,
) -> List[Dict[str, Any]]:
    """
    Get the next milestones user is closest to achieving.

    Args:
        db: Database session
        user_id: User's unique identifier
        count: Number of milestones to return

    Returns:
        List of next achievable milestones sorted by proximity
    """
    achievable = await get_achievable_milestones(db, user_id)

    # Flatten all milestones
    all_milestones = []
    for category in achievable.values():
        all_milestones.extend(category)

    # Filter out already achieved
    upcoming = [m for m in all_milestones if not m.get("achieved", False)]

    # Calculate progress percentage for sorting
    for milestone in upcoming:
        if "progress" in milestone and "total" in milestone:
            milestone["progress_percent"] = int(
                (milestone["progress"] / milestone["total"]) * 100
            )
        else:
            milestone["progress_percent"] = 0

    # Sort by progress percentage (highest first)
    upcoming.sort(key=lambda m: m.get("progress_percent", 0), reverse=True)

    return upcoming[:count]


async def check_chapter_completion_milestones(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: str,
) -> Optional[Milestone]:
    """
    Check and award chapter completion milestones.

    Should be called when a user completes a chapter.

    Args:
        db: Database session
        user_id: User's unique identifier
        chapter_id: ID of the chapter just completed

    Returns:
        Newly awarded milestone if any
    """
    completed_count = await _get_completed_chapters_count(db, user_id)

    if completed_count == 1:
        return await check_and_award_milestone(
            db, user_id, MilestoneType.FIRST_CHAPTER,
            {"chapter_id": chapter_id}
        )
    elif completed_count == 3:
        return await check_and_award_milestone(
            db, user_id, MilestoneType.THREE_CHAPTERS,
            {"chapter_id": chapter_id}
        )
    elif completed_count == 6:
        return await check_and_award_milestone(
            db, user_id, MilestoneType.SIX_CHAPTERS,
            {"chapter_id": chapter_id}
        )

    return None


async def check_quiz_milestones(
    db: AsyncSession,
    user_id: UUID,
    quiz_attempt: QuizAttempt,
) -> List[Milestone]:
    """
    Check and award quiz-related milestones.

    Should be called when a user submits a quiz.

    Args:
        db: Database session
        user_id: User's unique identifier
        quiz_attempt: The quiz attempt just submitted

    Returns:
        List of newly awarded milestones
    """
    awarded = []

    # Check first quiz passed
    if quiz_attempt.passed:
        passed_count = await _get_passed_quiz_count(db, user_id)
        if passed_count == 1:
            milestone = await check_and_award_milestone(
                db, user_id, MilestoneType.FIRST_QUIZ,
                {"quiz_id": quiz_attempt.quiz_id, "score": quiz_attempt.score_percentage}
            )
            if milestone:
                awarded.append(milestone)

        # Check all quizzes passed
        if passed_count == TOTAL_QUIZZES:
            milestone = await check_and_award_milestone(
                db, user_id, MilestoneType.ALL_QUIZES_PASSED,
                {"quiz_id": quiz_attempt.quiz_id}
            )
            if milestone:
                awarded.append(milestone)

    # Check perfect score
    if quiz_attempt.score_percentage == 100:
        perfect_count = await _get_perfect_quiz_count(db, user_id)
        if perfect_count == 1:
            milestone = await check_and_award_milestone(
                db, user_id, MilestoneType.PERFECT_QUIZ,
                {"quiz_id": quiz_attempt.quiz_id, "chapter_id": quiz_attempt.chapter_id}
            )
            if milestone:
                awarded.append(milestone)

        # Check perfectionist badge (3 perfect quizzes)
        if perfect_count == 3:
            milestone = await check_and_award_milestone(
                db, user_id, MilestoneType.PERFECTIONIST,
                {"quizzes": [quiz_attempt.quiz_id]}
            )
            if milestone:
                awarded.append(milestone)

    return awarded


async def check_streak_milestones(
    db: AsyncSession,
    user_id: UUID,
    current_streak: int,
    previous_streak: int,
) -> Optional[Milestone]:
    """
    Check and award streak milestones.

    Should be called when streak is updated.

    Args:
        db: Database session
        user_id: User's unique identifier
        current_streak: Current streak count
        previous_streak: Previous streak count (before increment)

    Returns:
        Newly awarded milestone if any
    """
    for days, milestone_type in STREAK_MILESTONES.items():
        if current_streak >= days and previous_streak < days:
            return await check_and_award_milestone(
                db, user_id, milestone_type,
                {"days": current_streak}
            )

    return None


async def check_time_milestones(
    db: AsyncSession,
    user_id: UUID,
) -> List[Milestone]:
    """
    Check and award time-based learning milestones.

    Should be called periodically or after significant learning activity.

    Args:
        db: Database session
        user_id: User's unique identifier

    Returns:
        List of newly awarded milestones
    """
    awarded = []
    total_hours = await _get_total_time_hours(db, user_id)

    for hours, milestone_type in HOUR_MILESTONES.items():
        if total_hours >= hours:
            milestone = await check_and_award_milestone(
                db, user_id, milestone_type,
                {"total_hours": total_hours}
            )
            if milestone:
                awarded.append(milestone)

    return awarded


# Helper functions

async def _get_completed_chapters_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of completed chapters for user."""
    result = await db.execute(
        select(func.count(ChapterProgress.id))
        .where(
            and_(
                ChapterProgress.user_id == user_id,
                ChapterProgress.is_completed == True
            )
        )
    )
    return result.scalar() or 0


async def _get_total_time_hours(db: AsyncSession, user_id: UUID) -> float:
    """Get total learning time in hours."""
    result = await db.execute(
        select(func.sum(ChapterProgress.time_spent_seconds))
        .where(ChapterProgress.user_id == user_id)
    )
    total_seconds = result.scalar() or 0
    return round(total_seconds / 3600, 2)


async def _get_passed_quiz_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of unique quizzes passed."""
    # Get the latest attempt for each chapter
    subquery = (
        select(
            QuizAttempt.chapter_id,
            func.max(QuizAttempt.attempt_number).label("max_attempt")
        )
        .where(QuizAttempt.user_id == user_id)
        .group_by(QuizAttempt.chapter_id)
        .subquery()
    )

    result = await db.execute(
        select(func.count(QuizAttempt.id))
        .join(
            subquery,
            and_(
                QuizAttempt.chapter_id == subquery.c.chapter_id,
                QuizAttempt.attempt_number == subquery.c.max_attempt,
                QuizAttempt.passed == True
            )
        )
    )
    return result.scalar() or 0


async def _get_perfect_quiz_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of perfect quiz scores (100%)."""
    result = await db.execute(
        select(func.count(QuizAttempt.id))
        .where(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.score_percentage == 100
            )
        )
    )
    return result.scalar() or 0


async def _get_current_streak(db: AsyncSession, user_id: UUID) -> int:
    """Get user's current streak."""
    result = await db.execute(
        select(Streak).where(Streak.user_id == user_id)
    )
    streak = result.scalar_one_or_none()
    return streak.current_streak if streak else 0


async def _get_achieved_milestone_types(
    db: AsyncSession,
    user_id: UUID,
) -> set:
    """Get set of milestone types already achieved by user."""
    result = await db.execute(
        select(Milestone.milestone_type)
        .where(Milestone.user_id == user_id)
    )
    return set(result.scalars().all())


async def _check_quick_learner(db: AsyncSession, user_id: UUID) -> bool:
    """Check if user completed any chapter in under 30 minutes."""
    result = await db.execute(
        select(ChapterProgress).where(
            and_(
                ChapterProgress.user_id == user_id,
                ChapterProgress.is_completed == True,
                ChapterProgress.time_spent_seconds < 1800  # 30 minutes
            )
        )
    )
    return result.scalar_one_or_none() is not None


# Import func at the bottom to avoid circular imports
from sqlalchemy import func
