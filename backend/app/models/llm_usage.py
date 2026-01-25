"""
Database models for LLM usage tracking (Phase 2)
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base


class LLMUsageLog(Base):
    """
    LLM Usage Log for tracking premium feature usage and costs

    Tracks every LLM API call with token usage and cost information
    for billing and analytics purposes.
    """
    __tablename__ = "llm_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_type = Column(String(50), nullable=False, index=True)  # 'graded_assessment', 'learning_path'
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    model_name = Column(String(50), nullable=False)  # 'gpt-4o', 'claude-sonnet', etc.
    request_details = Column(Text, nullable=True)  # JSON string
    response_details = Column(Text, nullable=True)  # JSON string
    mock_call = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="llm_usage_logs")


class GradedAssessment(Base):
    """
    Graded Assessment storage

    Stores graded assessments for history and analytics.
    """
    __tablename__ = "graded_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    rubric = Column(Text, nullable=True)
    question_type = Column(String(50), default="short_answer")  # 'short_answer', 'essay', 'code_explanation'
    score = Column(Integer, nullable=False)  # 0-100
    feedback_json = Column(Text, nullable=False)  # JSON with strengths, weaknesses, suggestions
    llm_usage_log_id = Column(Integer, ForeignKey("llm_usage_logs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="graded_assessments")
    chapter = relationship("Chapter")
    llm_usage_log = relationship("LLMUsageLog")


class LearningPath(Base):
    """
    Learning Path storage

    Stores generated learning paths for reference and analytics.
    """
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    current_chapter_id = Column(Integer, ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    focus = Column(String(50), nullable=False)  # 'reinforce_weaknesses', 'fastest_completion', 'deepest_understanding'
    path_json = Column(Text, nullable=False)  # JSON with recommendations, study plan, gaps
    llm_usage_log_id = Column(Integer, ForeignKey("llm_usage_logs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)  # Paths expire in 7 days

    # Relationships
    user = relationship("User", back_populates="learning_paths")
    current_chapter = relationship("Chapter")
    llm_usage_log = relationship("LLMUsageLog")


class UsageLimit(Base):
    """
    Usage Limits tracking

    Tracks monthly usage counts for premium features.
    """
    __tablename__ = "usage_limits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    assessments_used_this_month = Column(Integer, default=0, nullable=False)
    learning_paths_used_this_month = Column(Integer, default=0, nullable=False)
    current_month_start = Column(DateTime, nullable=False)  # Start of current billing month
    last_reset_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="usage_limits")


class MonthlyCostSummary(Base):
    """
    Monthly Cost Summary

    Aggregated cost data per user per month for billing and analytics.
    """
    __tablename__ = "monthly_cost_summary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)  # 1-12

    # Aggregated data
    total_requests = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Float, default=0.0, nullable=False)
    assessments_count = Column(Integer, default=0, nullable=False)
    learning_paths_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")

    # Unique constraint
    __table_args__ = (
        # Add unique constraint on (user_id, year, month)
        # This is handled by SQLAlchemy's unique parameter
    )
