"""
Core database models: Base mixin, User accounts, Student and Teacher profiles.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from backend.app.core.database import Base
from backend.app.domain.enums import UserRole

__all__ = ["BaseModelMixin", "generate_uuid", "get_utc_now", "User", "StudentProfile", "TeacherProfile", "UserRole"]


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseModelMixin:
    """Base model mixin providing UUID primary key and UTC audit timestamps."""
    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)


class User(BaseModelMixin, Base):
    """User account model for authentication and role management."""
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )

    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # 1-to-1 Profile Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class StudentProfile(BaseModelMixin, Base):
    """Student profile tracking standard, enrollment, and learning activity."""
    __tablename__ = "student_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    standard_id = Column(String(36), ForeignKey("standards.id", ondelete="SET NULL"), nullable=True, index=True)
    division = Column(String(20), nullable=True)
    enrollment_number = Column(String(50), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    standard = relationship("Standard", back_populates="students")
    attempts = relationship("Attempt", back_populates="student", cascade="all, delete-orphan")
    learning_events = relationship("LearningEvent", back_populates="student", cascade="all, delete-orphan")
    topic_performances = relationship("TopicPerformance", back_populates="student", cascade="all, delete-orphan")
    revision_plans = relationship("RevisionPlan", back_populates="student", cascade="all, delete-orphan")
    forgetting_signals = relationship("ForgettingSignal", back_populates="student", cascade="all, delete-orphan")
    interventions_received = relationship("TeacherAction", back_populates="student", cascade="all, delete-orphan")


class TeacherProfile(BaseModelMixin, Base):
    """Teacher profile managing assessments and pedagogical actions."""
    __tablename__ = "teacher_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    employee_id = Column(String(50), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    assessments = relationship("Assessment", back_populates="teacher", cascade="all, delete-orphan")
    actions_created = relationship("TeacherAction", back_populates="teacher", cascade="all, delete-orphan")
