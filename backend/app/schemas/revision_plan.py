from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.app.domain.enums import MasteryLevel, RetentionRiskLevel, RevisionPriority


class RevisionPlanItem(BaseModel):
    """
    Individual personalized revision item representing an eligible curriculum topic.
    """
    plan_id: Optional[str] = Field(None, description="Database RevisionPlan ID if persisted")
    topic_id: str = Field(..., description="Canonical topic ID")
    topic_title: str = Field(..., description="Topic title")
    subject_id: Optional[str] = Field(None, description="Subject ID")
    subject_name: str = Field(..., description="Subject name (localized if requested)")
    chapter_id: Optional[str] = Field(None, description="Chapter ID")
    chapter_title: Optional[str] = Field(None, description="Chapter title")
    mastery_level: MasteryLevel = Field(..., description="Current empirical mastery level")
    accuracy: float = Field(..., description="Historical accuracy percentage")
    recent_accuracy: Optional[float] = Field(None, description="Recent rolling accuracy percentage")
    retention_risk: RetentionRiskLevel = Field(..., description="Retention risk level")
    priority: RevisionPriority = Field(..., description="Calculated revision urgency priority")
    scheduled_date: str = Field(..., description="Scheduled revision date in YYYY-MM-DD format")
    recommended_revision_at: datetime = Field(..., description="Recommended revision timestamp")
    days_until_due: int = Field(..., description="Days until due (0=Today, 1=Tomorrow, <0=Overdue)")
    is_due_today: bool = Field(..., description="True if scheduled for today or overdue")
    is_overdue: bool = Field(..., description="True if past the scheduled revision timestamp")
    urgency_tier: str = Field(..., description="'TODAY', 'THIS_WEEK', or 'UPCOMING'")
    reason: str = Field(..., description="Explainable rationale grounded in learner signals")
    recommended_action: str = Field(..., description="Action enum: FOUNDATIONAL_PRACTICE, GUIDED_PRACTICE, etc.")
    recommended_difficulty: str = Field(..., description="Difficulty tier: FOUNDATIONAL, GUIDED, APPLICATION, CHALLENGE")
    source_document: Optional[str] = Field(None, description="Textbook provenance document")
    source_page: Optional[int] = Field(None, description="Textbook page number")


class RevisionPlanResponse(BaseModel):
    """
    Comprehensive, personalized revision plan response for a student.
    """
    student_id: str = Field(..., description="Student profile ID")
    generated_at: datetime = Field(..., description="Timestamp of plan generation")
    total_revisions: int = Field(..., description="Total active revision items")
    due_today_count: int = Field(..., description="Number of items due today or overdue")
    due_this_week_count: int = Field(..., description="Number of items due within 7 days")
    upcoming_count: int = Field(..., description="Number of items due after 7 days")
    urgent_count: int = Field(..., description="Number of URGENT priority items")
    high_count: int = Field(..., description="Number of HIGH priority items")
    medium_count: int = Field(..., description="Number of MEDIUM priority items")
    low_count: int = Field(..., description="Number of LOW priority items")
    revisions: List[RevisionPlanItem] = Field(default_factory=list, description="Ordered list of revision items")
