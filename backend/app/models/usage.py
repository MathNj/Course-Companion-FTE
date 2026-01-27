"""
Phase 2 Usage Tracking Models

Models for LLM cost tracking and premium usage quotas.
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, CheckConstraint, Index, UniqueConstraint, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime

from app.models.base import Base


class LLMUsageLog(Base):
    """
    Audit log of all LLM API calls with detailed cost and performance metrics.

    Every LLM call is logged for cost tracking, audit, and optimization.
    """
    __tablename__ = "llm_usage_logs"

    # Primary Key
    log_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign Keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)

    # Feature Tracking
    feature = Column(String(50), nullable=False, index=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # FK to adaptive_paths.path_id or assessment_feedback.feedback_id

    # Request Details
    request_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    model_version = Column(String(100), nullable=False, default="gpt-4o-mini")

    # Token Usage
    tokens_input = Column(Integer, nullable=False)
    tokens_output = Column(Integer, nullable=False)
    tokens_total = Column(Integer, nullable=False, server_default="tokens_input + tokens_output")

    # Cost Calculation
    cost_usd = Column(Numeric(10, 6), nullable=False)
    # Calculated as: (tokens_input * $3/1M) + (tokens_output * $15/1M)

    # Performance
    latency_ms = Column(Integer, nullable=False)

    # Status
    success = Column(Boolean, nullable=False, default=True, index=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Data Retention
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete after 90 days

    # Table Constraints
    __table_args__ = (
        Index("idx_llm_logs_student_id", "student_id"),
        Index("idx_llm_logs_feature", "feature"),
        Index("idx_llm_logs_timestamp", "request_timestamp"),
        Index("idx_llm_logs_success", "success"),
        # Partial index for active logs (not soft-deleted)
        Index("idx_llm_logs_active", "request_timestamp", postgresql_where="deleted_at IS NULL"),
        # Composite indexes for analytics
        Index("idx_llm_logs_student_month", "student_id", func.date_trunc("month", request_timestamp)),
        Index("idx_llm_logs_feature_month", "feature", func.date_trunc("month", request_timestamp)),
        # Validation constraints
        CheckConstraint("feature IN ('adaptive-path', 'assessment')", name="check_feature_type"),
        CheckConstraint("tokens_input > 0", name="check_tokens_input_positive"),
        CheckConstraint("tokens_output > 0", name="check_tokens_output_positive"),
        CheckConstraint("cost_usd > 0", name="check_cost_positive"),
        CheckConstraint("latency_ms >= 0", name="check_latency_non_negative"),
        CheckConstraint(
            "(success = TRUE AND error_code IS NULL) OR (success = FALSE AND error_code IS NOT NULL)",
            name="valid_error_state"
        ),
    )


class PremiumUsageQuota(Base):
    """
    Track monthly usage quotas for premium students.

    Enforces rate limits: 10 adaptive paths + 20 assessments per premium user per month.
    """
    __tablename__ = "premium_usage_quotas"

    # Primary Key
    quota_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    # Foreign Keys
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False, index=True)

    # Time Period
    month = Column(Date, nullable=False)  # First day of month (e.g., 2026-01-01)
    reset_date = Column(Date, nullable=False)  # First day of next month

    # Adaptive Path Quotas
    adaptive_paths_used = Column(Integer, nullable=False, default=0)
    adaptive_paths_limit = Column(Integer, nullable=False, default=10)

    # Assessment Quotas
    assessments_used = Column(Integer, nullable=False, default=0)
    assessments_limit = Column(Integer, nullable=False, default=20)

    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Table Constraints
    __table_args__ = (
        Index("idx_quotas_student_id", "student_id"),
        Index("idx_quotas_month", "month"),
        Index("idx_quotas_reset_date", "reset_date"),
        # Composite index for quota checks
        Index("idx_quotas_student_month", "student_id", "month"),
        # Unique constraint: one record per student per month
        UniqueConstraint("student_id", "month", name="unique_student_month"),
        # Validation constraints
        CheckConstraint("adaptive_paths_used >= 0", name="check_adaptive_paths_used_non_negative"),
        CheckConstraint("adaptive_paths_limit > 0", name="check_adaptive_paths_limit_positive"),
        CheckConstraint("assessments_used >= 0", name="check_assessments_used_non_negative"),
        CheckConstraint("assessments_limit > 0", name="check_assessments_limit_positive"),
        CheckConstraint("month = DATE_TRUNC('month', month)::DATE", name="valid_month"),
        CheckConstraint("reset_date = (month + INTERVAL '1 month')::DATE", name="valid_reset_date"),
    )
