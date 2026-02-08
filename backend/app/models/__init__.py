"""
Database Models

All SQLAlchemy models for the Course Companion application.
Import all models here so Alembic can detect them.
"""

from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.subscription import Subscription
from app.models.progress import ChapterProgress
from app.models.quiz import QuizAttempt
from app.models.session import Session
from app.models.streak import Streak
from app.models.milestone import Milestone, MilestoneType

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Subscription",
    "ChapterProgress",
    "QuizAttempt",
    "Session",
    "Streak",
    "Milestone",
    "MilestoneType",
]
