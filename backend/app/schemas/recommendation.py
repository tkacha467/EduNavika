from typing import Optional, List
from pydantic import BaseModel, Field
from backend.app.domain.enums import (
    RecommendationAction,
    RevisionPriority,
    MasteryLevel,
    PerformanceTrend,
    RetentionRiskLevel,
)


class TopicRecommendation(BaseModel):
    """
    Actionable next-step recommendation for a student on a specific topic.
    Grounded in current knowledge model profiles and active revision plans.
    """
    topic_id: str
    topic_title: str
    subject_name: str
    action: RecommendationAction = Field(..., description="Recommended action: REVISION, PRACTICE, or REVIEW")
    priority: RevisionPriority = Field(..., description="Urgency: URGENT, HIGH, MEDIUM, or LOW")
    reason: str = Field(..., description="Human-readable explainable rationale for this recommendation")
    score: float = Field(..., description="Deterministic priority ranking score (higher is more urgent)")
    mastery_level: MasteryLevel
    accuracy: float = Field(..., ge=0.0, le=100.0)
    recent_accuracy: Optional[float] = Field(None, ge=0.0, le=100.0)
    retention_risk: RetentionRiskLevel
    trend: PerformanceTrend
    active_revision_plan_id: Optional[str] = None


class RecommendationResponse(BaseModel):
    """
    Ordered recommendations list for a student.
    """
    student_id: str
    total_recommendations: int
    recommendations: List[TopicRecommendation]
