"""
Milestone Model

Tracks user achievements and learning milestones.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

from sqlalchemy import String, TIMESTAMP, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin
from app.models.types import UUID as UUIDType, JSON as JSONType


class MilestoneType(str, Enum):
    """Types of milestones users can achieve."""

    # Chapter milestones
    FIRST_CHAPTER = "first_chapter"
    THREE_CHAPTERS = "three_chapters"
    SIX_CHAPTERS = "six_chapters"  # Course completion

    # Quiz milestones
    FIRST_QUIZ = "first_quiz"
    PERFECT_QUIZ = "perfect_quiz"  # 100% score
    ALL_QUIZES_PASSED = "all_quizzes_passed"

    # Streak milestones
    STREAK_3 = "streak_3"
    STREAK_7 = "streak_7"
    STREAK_14 = "streak_14"
    STREAK_30 = "streak_30"
    STREAK_60 = "streak_60"
    STREAK_100 = "streak_100"

    # Time milestones
    FIRST_HOUR = "first_hour"
    TEN_HOURS = "ten_hours"
    HUNDRED_HOURS = "hundred_hours"

    # Achievement badges
    QUICK_LEARNER = "quick_learner"  # Complete chapter in <30 min
    PERFECTIONIST = "perfectionist"  # 3 perfect quizzes
    CONSISTENT_LEARNER = "consistent_learner"  # 7-day streak
    KNOWLEDGE_SEEKER = "knowledge_seeker"  # Complete all chapters


class Milestone(Base, TimestampMixin):
    """
    Tracks student achievements and milestones.

    Attributes:
        id: Unique milestone record identifier
        user_id: Foreign key to User
        milestone_type: Type of milestone achieved
        achieved_at: When milestone was achieved
        metadata: Additional milestone-specific data (JSON)
        is_notified: Whether user has been notified of this milestone
    """

    __tablename__ = "milestones"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid4,
    )

    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Milestone details
    milestone_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # When achieved
    achieved_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        server_default="NOW()",
    )

    # Additional data (chapter_id, score, etc.)
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True,
    )

    # Notification status
    is_notified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Indexes
    __table_args__ = (
        Index("idx_milestones_user_id", "user_id"),
        Index("idx_milestones_type", "milestone_type"),
        Index("idx_milestones_user_type", "user_id", "milestone_type", unique=True),
        Index("idx_milestones_achieved_at", "achieved_at"),
    )

    def __repr__(self) -> str:
        return f"<Milestone(id={self.id}, user_id={self.user_id}, type={self.milestone_type})>"

    @property
    def display_name(self) -> str:
        """Get human-readable milestone name."""
        names = {
            MilestoneType.FIRST_CHAPTER: "First Chapter Complete",
            MilestoneType.THREE_CHAPTERS: "Three Chapters Down",
            MilestoneType.SIX_CHAPTERS: "Course Complete!",
            MilestoneType.FIRST_QUIZ: "First Quiz Passed",
            MilestoneType.PERFECT_QUIZ: "Perfect Score",
            MilestoneType.ALL_QUIZES_PASSED: "Quiz Master",
            MilestoneType.STREAK_3: "3-Day Streak",
            MilestoneType.STREAK_7: "Week Warrior",
            MilestoneType.STREAK_14: "Two Week Champion",
            MilestoneType.STREAK_30: "Month Master",
            MilestoneType.STREAK_60: "60-Day Legend",
            MilestoneType.STREAK_100: "Centurion",
            MilestoneType.FIRST_HOUR: "First Hour Learning",
            MilestoneType.TEN_HOURS: "Dedicated Learner",
            MilestoneType.HUNDRED_HOURS: "Century Club",
            MilestoneType.QUICK_LEARNER: "Quick Learner",
            MilestoneType.PERFECTIONIST: "Perfectionist",
            MilestoneType.CONSISTENT_LEARNER: "Consistent Learner",
            MilestoneType.KNOWLEDGE_SEEKER: "Knowledge Seeker",
        }
        return names.get(self.milestone_type, "Achievement Unlocked")

    @property
    def message(self) -> str:
        """Get congratulatory message for milestone."""
        messages = {
            MilestoneType.FIRST_CHAPTER: "🎉 You've completed your first chapter! Keep up the great work!",
            MilestoneType.THREE_CHAPTERS: "🚀 Halfway there! You've completed 3 chapters!",
            MilestoneType.SIX_CHAPTERS: "🏆 Congratulations! You've mastered the entire course!",
            MilestoneType.FIRST_QUIZ: "⭐ Well done! You've passed your first quiz!",
            MilestoneType.PERFECT_QUIZ: "💯 Perfect! You scored 100% on this quiz!",
            MilestoneType.ALL_QUIZES_PASSED: "🎓 Amazing! You've passed all quizzes!",
            MilestoneType.STREAK_3: "🔥 Amazing! You've maintained a 3-day learning streak!",
            MilestoneType.STREAK_7: "⭐ Incredible! A full week of consistent learning!",
            MilestoneType.STREAK_14: "💪 Outstanding! Two weeks of dedication!",
            MilestoneType.STREAK_30: "🏆 Legendary! 30 days of continuous learning!",
            MilestoneType.STREAK_60: "👑 Phenomenal! 60 days of unwavering commitment!",
            MilestoneType.STREAK_100: "💎 Extraordinary! 100 days of learning excellence!",
            MilestoneType.FIRST_HOUR: "📚 You've spent your first hour learning. Great start!",
            MilestoneType.TEN_HOURS: "⏰ Impressive dedication! 10 hours of learning!",
            MilestoneType.HUNDRED_HOURS: "🌟 Incredible! 100 hours of mastering Generative AI!",
            MilestoneType.QUICK_LEARNER: "⚡ Lightning fast! You completed a chapter in under 30 minutes!",
            MilestoneType.PERFECTIONIST: "🎯 Precision master! You've achieved 3 perfect quiz scores!",
            MilestoneType.CONSISTENT_LEARNER: "📅 7 days in a row! Consistency is key!",
            MilestoneType.KNOWLEDGE_SEEKER: "🧠 True scholar! You've completed every chapter!",
        }
        return messages.get(self.milestone_type, "Achievement unlocked!")

    @property
    def icon_emoji(self) -> str:
        """Get icon emoji for milestone."""
        icons = {
            MilestoneType.FIRST_CHAPTER: "📖",
            MilestoneType.THREE_CHAPTERS: "📚",
            MilestoneType.SIX_CHAPTERS: "🎓",
            MilestoneType.FIRST_QUIZ: "✅",
            MilestoneType.PERFECT_QUIZ: "💯",
            MilestoneType.ALL_QUIZES_PASSED: "🏅",
            MilestoneType.STREAK_3: "🔥",
            MilestoneType.STREAK_7: "⭐",
            MilestoneType.STREAK_14: "💪",
            MilestoneType.STREAK_30: "🏆",
            MilestoneType.STREAK_60: "👑",
            MilestoneType.STREAK_100: "💎",
            MilestoneType.FIRST_HOUR: "⏱️",
            MilestoneType.TEN_HOURS: "⌛",
            MilestoneType.HUNDRED_HOURS: "🌟",
            MilestoneType.QUICK_LEARNER: "⚡",
            MilestoneType.PERFECTIONIST: "🎯",
            MilestoneType.CONSISTENT_LEARNER: "📅",
            MilestoneType.KNOWLEDGE_SEEKER: "🧠",
        }
        return icons.get(self.milestone_type, "🏆")
