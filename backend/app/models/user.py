from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin
from backend.app.domain.enums import UserRole

# Re-export for backward compatibility
__all__ = ["User", "StudentProfile", "TeacherProfile", "UserRole"]


class User(BaseModelMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )

    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Profiles (1-to-1)
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class StudentProfile(BaseModelMixin, Base):
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
    __tablename__ = "teacher_profiles"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    employee_id = Column(String(50), nullable=True, index=True)

    # Relationships
    user = relationship("User", back_populates="teacher_profile")
    assessments = relationship("Assessment", back_populates="teacher", cascade="all, delete-orphan")
    actions_created = relationship("TeacherAction", back_populates="teacher", cascade="all, delete-orphan")
