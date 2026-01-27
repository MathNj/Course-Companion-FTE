"""
Phase 2 Schemas: Usage Tracking & Cost Monitoring

Request and response models for usage quota and cost monitoring endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class UsageQuotaResponse(BaseModel):
    """Response showing student's remaining monthly quotas."""

    student_id: str
    subscription_tier: str
    month: str  # Format: "YYYY-MM"

    adaptive_paths_used: int
    adaptive_paths_limit: int
    adaptive_paths_remaining: int

    assessments_used: int
    assessments_limit: int
    assessments_remaining: int

    reset_date: datetime


class CostBreakdownByFeature(BaseModel):
    """Cost breakdown by feature type."""

    feature: str  # "adaptive-path" or "assessment"
    total_requests: int
    total_cost_usd: float
    average_cost_per_request: float


class CostAlert(BaseModel):
    """Alert when student exceeds cost threshold."""

    type: str = Field(..., description="Alert type (e.g., 'COST_THRESHOLD_EXCEEDED')")
    student_id: str
    cost_usd: float
    threshold_usd: float


class CostBreakdownResponse(BaseModel):
    """Response showing aggregated cost metrics."""

    period: Dict[str, str]  # {"start_date": "2026-01-01", "end_date": "2026-01-31"}

    total_cost_usd: float
    total_requests: int
    average_cost_per_student: float

    breakdown_by_feature: List[CostBreakdownByFeature]

    top_users_by_cost: Optional[List[Dict]] = Field(None, description="Top 5 users by cost (admin only)")
    alerts: List[CostAlert] = Field(default_factory=list)


class AdminCostMetrics(CostBreakdownResponse):
    """Extended cost metrics for admin dashboard."""

    total_students: int
    active_premium_students: int
    monthly_projection: float
