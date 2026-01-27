"""
Phase 2 Schemas: Adaptive Learning Paths

Request and response models for adaptive learning path endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RecommendationSchema(BaseModel):
    """Single learning recommendation within an adaptive path."""

    chapter_id: str = Field(..., description="Chapter identifier (e.g., '04-rag')")
    section_id: Optional[str] = Field(None, description="Section identifier (e.g., 'embeddings-review')")
    priority: int = Field(..., ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    reason: str = Field(..., min_length=10, max_length=500, description="Why this content is suggested")
    estimated_impact: str = Field(..., pattern="^(high|medium|low)$", description="Expected learning impact")
    estimated_time_minutes: int = Field(..., gt=0, le=180, description="Estimated time to complete")
    links: dict = Field(default_factory=dict, description="Related resource links")


class AdaptivePathRequest(BaseModel):
    """Request to generate adaptive learning path."""

    force_refresh: bool = Field(False, description="Bypass 24h cache and regenerate path")
    include_reasoning: bool = Field(True, description="Include detailed reasoning for recommendations")


class AdaptivePathMetadata(BaseModel):
    """Metadata about generated adaptive path."""

    total_recommendations: int
    high_priority_count: int
    estimated_total_time_minutes: int
    cached: bool


class AdaptivePathResponse(BaseModel):
    """Response containing personalized learning recommendations."""

    path_id: str
    student_id: str
    generated_at: datetime
    expires_at: datetime
    status: str

    recommendations: List[RecommendationSchema]
    reasoning: str

    metadata: AdaptivePathMetadata


class AdaptivePathErrorResponse(BaseModel):
    """Error response for adaptive path requests."""

    error: dict = Field(..., description="Error details with code, message, and next steps")


class InsufficientDataError(BaseModel):
    """Error response when insufficient data for recommendations."""

    error: dict = {
        "code": "INSUFFICIENT_DATA",
        "message": "Not enough learning data to generate meaningful recommendations",
        "required_quizzes": 2,
        "completed_quizzes": int,
        "next_steps": List[str]
    }
