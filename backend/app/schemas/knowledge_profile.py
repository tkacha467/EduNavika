from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel


class TopicKnowledgeProfile(BaseModel):
    """
    Topic-level student knowledge profile derived from empirical interaction history.
    Provides verified metrics for adaptive recommendation and personalized learning.
    """
    topic_id: str
    topic_title: str
    subject_name: str
    mastery_level: MasteryLevel
    accuracy: float = Field(..., ge=0.0, le=100.0, description="Overall lifetime accuracy on this topic")
    total_attempts: int = Field(..., ge=0, description="Total evaluative attempts on this topic")
    correct_attempts: int = Field(..., ge=0, description="Total correct attempts on this topic")
    recent_accuracy: Optional[float] = Field(None, ge=0.0, le=100.0, description="Accuracy over most recent window of attempts (up to 5)")
    trend: PerformanceTrend = Field(default=PerformanceTrend.INSUFFICIENT_DATA, description="Performance trajectory comparing recent to prior attempts")
    retention_risk: RetentionRiskLevel = Field(default=RetentionRiskLevel.UNASSESSED, description="Forgetting/retention risk evaluated from temporal decay evidence")
    average_response_time_ms: Optional[float] = Field(None, ge=0.0, description="Average response time in milliseconds if recorded")
    hint_usage_count: int = Field(default=0, ge=0, description="Total times hints were requested on this topic")
    last_activity_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    learning_pace: Optional[str] = Field(None, description="Pace metric (intentionally null/unassessed until sufficient longitudinal duration baseline exists)")
    current_difficulty: Optional[str] = Field(None, description="Question difficulty metric (intentionally null until item difficulty metadata is active in curriculum)")


class StudentKnowledgeProfileResponse(BaseModel):
    """
    Comprehensive student knowledge profile across all active topics.
    """
    student_id: str
    total_topics_tracked: int
    profiles: List[TopicKnowledgeProfile]
