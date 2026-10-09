from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.app.domain.enums import MasteryLevel, PerformanceTrend, RetentionRiskLevel, EventType


class MasteryDistribution(BaseModel):
    unassessed: int = 0
    novice: int = 0
    developing: int = 0
    proficient: int = 0
    mastered: int = 0


class OverallProgressSummary(BaseModel):
    total_attempts: int
    correct_attempts: int
    overall_accuracy: float
    topics_studied: int
    total_topics_available: int
    mastery_distribution: MasteryDistribution
    overall_trend: str
    recent_activity_at: Optional[datetime] = None
    subject_id: Optional[str] = None
    subject_name: Optional[str] = None


class TopicProgressItem(BaseModel):
    topic_id: str
    topic_title: str
    subject_name: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    mastery_level: MasteryLevel
    recent_accuracy: Optional[float] = None
    trend: PerformanceTrend
    retention_risk: RetentionRiskLevel
    recommended_action: str
    recommended_difficulty: str


class StrengthsWeaknessesSummary(BaseModel):
    strengths: List[TopicProgressItem]
    weaknesses: List[TopicProgressItem]
    developing: List[TopicProgressItem]
    unassessed_count: int


class LearningJourneyItem(BaseModel):
    event_id: str
    timestamp: datetime
    topic_id: str
    topic_title: str
    subject_name: str
    event_type: str
    correctness: Optional[bool] = None
    score: Optional[float] = None
    difficulty: Optional[str] = None
    response_time_ms: Optional[int] = None


class StudentProgressResponse(BaseModel):
    student_id: str
    overall: OverallProgressSummary
    topics: List[TopicProgressItem]
    strengths_weaknesses: StrengthsWeaknessesSummary
    learning_journey: List[LearningJourneyItem]
