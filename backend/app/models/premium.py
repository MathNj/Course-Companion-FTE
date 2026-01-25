"""
Pydantic models for Phase 2 Premium Features
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ============================================================================
# Graded Assessment Models
# ============================================================================

class GradeAssessmentRequest(BaseModel):
    """Request model for grading an assessment"""
    question: str = Field(..., description="The question being asked")
    student_answer: str = Field(..., description="The student's free-form answer")
    rubric: str = Field(default="Clarity: 30%, Accuracy: 40%, Depth: 30%", description="Grading rubric")
    question_type: str = Field(default="short_answer", description="Type of question")
    chapter_id: Optional[int] = Field(None, description="Chapter ID for context")


class RubricScores(BaseModel):
    """Rubric category scores"""
    clarity: int = Field(..., ge=0, le=100)
    accuracy: int = Field(..., ge=0, le=100)
    depth: int = Field(..., ge=0, le=100)


class Feedback(BaseModel):
    """Detailed feedback on the answer"""
    strengths: List[str] = Field(default_factory=list, description="What the student did well")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas that need work")
    specific_suggestions: List[str] = Field(default_factory=list, description="Specific improvement suggestions")


class GradeAssessmentResponse(BaseModel):
    """Response model for graded assessment"""
    score: int = Field(..., ge=0, le=100, description="Overall score (0-100)")
    feedback: Feedback = Field(..., description="Detailed feedback")
    rubric_scores: RubricScores = Field(..., description="Scores by rubric category")
    tokens_used: int = Field(..., description="Tokens consumed by LLM")
    cost_usd: float = Field(..., description="Cost in USD")
    model_name: str = Field(..., description="LLM model used")
    mock_call: bool = Field(..., description="Whether this was a mock call")
    graded_at: str = Field(..., description="Timestamp of grading")


# ============================================================================
# Learning Path Models
# ============================================================================

class GenerateLearningPathRequest(BaseModel):
    """Request model for generating learning path"""
    current_chapter_id: int = Field(..., description="Current chapter ID")
    focus: str = Field(
        default="reinforce_weaknesses",
        description="Learning focus: reinforce_weaknesses, fastest_completion, or deepest_understanding"
    )
    include_completed: bool = Field(default=True, description="Include completed chapters in analysis")
    learning_style: str = Field(default="mixed", description="Learning style: visual, textual, or mixed")


class RecommendedChapter(BaseModel):
    """A recommended chapter to study"""
    chapter: int = Field(..., description="Chapter number")
    title: str = Field(..., description="Chapter title")
    reason: str = Field(..., description="Why this chapter is recommended")
    priority: str = Field(..., description="Priority level: high, medium, or low")
    estimated_difficulty: str = Field(..., description="Difficulty: easy, medium, or hard")


class KnowledgeGap(BaseModel):
    """A knowledge gap identified"""
    topic: str = Field(..., description="Topic name")
    gap_severity: str = Field(..., description="Severity: minor, moderate, or significant")
    recommended_resources: List[str] = Field(default_factory=list, description="Resources to fill the gap")


class StudyPlan(BaseModel):
    """Study plan with weekly tasks"""
    this_week: List[str] = Field(default_factory=list, description="Tasks for this week")
    next_week: List[str] = Field(default_factory=list, description="Tasks for next week")


class LearningPath(BaseModel):
    """Generated learning path"""
    current_status: str = Field(..., description="Current learning status")
    recommended_next: List[RecommendedChapter] = Field(default_factory=list, description="Recommended chapters")
    knowledge_gaps: List[KnowledgeGap] = Field(default_factory=list, description="Identified knowledge gaps")
    study_plan: StudyPlan = Field(..., description="Study plan")
    motivation: str = Field(..., description="Motivational message")


class GenerateLearningPathResponse(BaseModel):
    """Response model for generated learning path"""
    learning_path: LearningPath = Field(..., description="Generated learning path")
    tokens_used: int = Field(..., description="Tokens consumed by LLM")
    cost_usd: float = Field(..., description="Cost in USD")
    model_name: str = Field(..., description="LLM model used")
    mock_call: bool = Field(..., description="Whether this was a mock call")
    generated_at: str = Field(..., description="Timestamp of generation")


# ============================================================================
# Subscription Models
# ============================================================================

class SubscriptionStatus(BaseModel):
    """User subscription status"""
    user_id: int
    subscription_type: str = Field(..., description="free or premium")
    subscription_expires_at: Optional[datetime] = Field(None, description="Expiration date")
    is_premium_active: bool = Field(..., description="Is premium subscription active")
    assessments_used: int = Field(default=0, description="Assessments used this month")
    learning_paths_used: int = Field(default=0, description="Learning paths used this month")
    assessments_limit: int = Field(default=0, description="Monthly assessment limit")
    learning_paths_limit: int = Field(default=0, description="Monthly learning path limit")


class UpgradeRequest(BaseModel):
    """Request to upgrade to premium"""
    subscription_type: str = Field("premium", description="Subscription type")


class UpgradeResponse(BaseModel):
    """Response to upgrade request"""
    user_id: int
    subscription_type: str
    subscription_expires_at: Optional[datetime]
    message: str = Field(..., description="Confirmation message")


# ============================================================================
# Usage Statistics Models
# ============================================================================

class MonthlyUsageStats(BaseModel):
    """Monthly LLM usage statistics"""
    year: int
    month: int
    total_requests: int = Field(default=0, description="Total requests this month")
    total_tokens: int = Field(default=0, description="Total tokens used")
    total_cost_usd: float = Field(default=0.0, description="Total cost in USD")
    assessments_count: int = Field(default=0, description="Number of assessments graded")
    learning_paths_count: int = Field(default=0, description="Number of learning paths generated")


class UsageLimit(BaseModel):
    """Usage limit information"""
    feature_type: str = Field(..., description="Feature type")
    used: int = Field(..., description="Used this month")
    limit: int = Field(..., description="Monthly limit")
    remaining: int = Field(..., description="Remaining uses")
    resets_in_days: int = Field(..., description="Days until reset")
