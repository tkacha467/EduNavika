"""
Adaptive & Longitudinal Learning database models:
LearningEvent, TopicPerformance, ForgettingSignal, RevisionPlan, TeacherAction.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, Enum as SQLEnum, ForeignKey, Index, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship

from backend.app.core.database import Base
from backend.app.models.core_models import BaseModelMixin, get_utc_now
from backend.app.domain.enums import (
    EventType,
    ForgettingSignalStatus,
    RevisionPriority,
    RevisionCompletionState,
    TeacherActionType
)

__all__ = [
    "LearningEvent",
    "EventType",
    "TopicPerformance",
    "ForgettingSignal",
    "ForgettingSignalStatus",
    "RevisionPlan",
    "RevisionPriority",
    "RevisionCompletionState",
    "TeacherAction",
    "TeacherActionType",
]


class LearningEvent(BaseModelMixin, Base):
    """Immutable research event stream recording granular student interactions."""
    __tablename__ = "learning_events"
    __table_args__ = (
        Index("ix_learning_events_student_topic", "student_id", "topic_id"),
        Index("ix_learning_events_student_timestamp", "student_id", "timestamp"),
        Index("ix_learning_events_topic_timestamp", "topic_id", "timestamp"),
        CheckConstraint("score IS NULL OR score >= 0", name="chk_event_score_non_negative"),
        CheckConstraint("response_time_ms IS NULL OR response_time_ms >= 0", name="chk_event_response_time_non_negative"),
        CheckConstraint("attempt_number IS NULL OR attempt_number >= 0", name="chk_event_attempt_number_non_negative"),
    )

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    attempt_id = Column(String(36), ForeignKey("attempts.id", ondelete="SET NULL"), nullable=True, index=True)
    score = Column(Float, nullable=True)
    correctness = Column(Boolean, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    hint_used = Column(Boolean, default=False, nullable=True)
    attempt_number = Column(Integer, default=1, nullable=True)
    event_metadata = Column(JSON, nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="learning_events")
    topic = relationship("Topic", back_populates="learning_events")
    attempt = relationship("Attempt", back_populates="learning_events")


class TopicPerformance(BaseModelMixin, Base):
    """Aggregated topic performance metrics for fast dashboard rendering."""
    __tablename__ = "topic_performances"
    __table_args__ = (
        UniqueConstraint("student_id", "topic_id", name="uq_student_topic_performance"),
        CheckConstraint("total_attempts >= 0", name="chk_topic_perf_total_attempts_non_negative"),
        CheckConstraint("correct_attempts >= 0", name="chk_topic_perf_correct_attempts_non_negative"),
        CheckConstraint("accuracy >= 0 AND accuracy <= 100", name="chk_topic_perf_accuracy_range"),
        CheckConstraint("practice_count >= 0", name="chk_topic_perf_practice_count_non_negative"),
        CheckConstraint("revision_count >= 0", name="chk_topic_perf_revision_count_non_negative"),
        CheckConstraint("hint_usage_count >= 0", name="chk_topic_perf_hint_usage_count_non_negative"),
        CheckConstraint("average_response_time >= 0", name="chk_topic_perf_avg_time_non_negative"),
    )

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    accuracy = Column(Float, default=0.0, nullable=False)
    
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    
    practice_count = Column(Integer, default=0, nullable=False)
    revision_count = Column(Integer, default=0, nullable=False)
    average_response_time = Column(Float, default=0.0, nullable=False)
    hint_usage_count = Column(Integer, default=0, nullable=False)
    mastery_state = Column(String(50), default="UNASSESSED", nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="topic_performances")
    topic = relationship("Topic", back_populates="topic_performances")


class ForgettingSignal(BaseModelMixin, Base):
    """Longitudinal evidence of performance decay across temporal observations."""
    __tablename__ = "forgetting_signals"

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    detected_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    
    evidence_type = Column(String(100), nullable=False)
    evidence_strength = Column(String(50), default="MODERATE", nullable=True)
    prior_performance_reference = Column(JSON, nullable=True)
    later_performance_reference = Column(JSON, nullable=True)
    status = Column(SQLEnum(ForgettingSignalStatus), default=ForgettingSignalStatus.UNRESOLVED, nullable=False, index=True)
    evidence_metadata = Column(JSON, nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="forgetting_signals")
    topic = relationship("Topic", back_populates="forgetting_signals")

    # Simplified property aliases
    @property
    def prior_performance_ref(self):
        return self.prior_performance_reference

    @prior_performance_ref.setter
    def prior_performance_ref(self, val):
        self.prior_performance_reference = val

    @property
    def later_performance_ref(self):
        return self.later_performance_reference

    @later_performance_ref.setter
    def later_performance_ref(self, val):
        self.later_performance_reference = val

    @property
    def confidence_metadata(self):
        return self.evidence_metadata

    @confidence_metadata.setter
    def confidence_metadata(self, val):
        self.evidence_metadata = val


class RevisionPlan(BaseModelMixin, Base):
    """Personalized spaced-repetition revision schedule item."""
    __tablename__ = "revision_plans"

    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    recommended_revision_at = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(SQLEnum(RevisionPriority), default=RevisionPriority.MEDIUM, nullable=False)
    reason = Column(Text, nullable=True)
    completion_state = Column(SQLEnum(RevisionCompletionState), default=RevisionCompletionState.PENDING, nullable=False, index=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="revision_plans")
    topic = relationship("Topic", back_populates="revision_plans")


class TeacherAction(BaseModelMixin, Base):
    """Teacher pedagogical intervention tracking."""
    __tablename__ = "teacher_actions"

    teacher_id = Column(String(36), ForeignKey("teacher_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(SQLEnum(TeacherActionType), nullable=False, index=True)
    note = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    teacher = relationship("TeacherProfile", back_populates="actions_created")
    student = relationship("StudentProfile", back_populates="interventions_received")
    topic = relationship("Topic", back_populates="teacher_actions")
