from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Index, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin, get_utc_now
from backend.app.domain.enums import EventType

# Re-export for backward compatibility
__all__ = ["LearningEvent", "EventType"]


class LearningEvent(BaseModelMixin, Base):
    """
    Longitudinal raw learning event log.
    Preserves granular student interactions over time without lossy aggregation or future-outcome leakage.
    Critical substrate for future retention modeling and knowledge tracing features.
    Authoritative research source of truth.
    """
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
