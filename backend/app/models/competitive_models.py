"""
Competitive Examination & Question Bank models for JEE Main, JEE Advanced, and NEET UG.
Matches Alembic revision f1e2d3c4b5a6.
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import relationship

from backend.app.core.database import Base
from backend.app.models.core_models import BaseModelMixin, get_utc_now

__all__ = [
    "Examination",
    "ExamSubject",
    "ExamTopic",
    "ExamPaper",
    "Question",
    "QuestionOption",
    "QuestionVerificationLog",
]


class Examination(Base):
    """Competitive Examination Master (e.g. JEE_MAIN, JEE_ADVANCED, NEET_UG)."""
    __tablename__ = "examinations"

    code = Column(String(32), primary_key=True)
    name = Column(String(128), nullable=False)
    conducting_body = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    exam_subjects = relationship("ExamSubject", back_populates="examination", cascade="all, delete-orphan")
    exam_topics = relationship("ExamTopic", back_populates="examination", cascade="all, delete-orphan")
    exam_papers = relationship("ExamPaper", back_populates="examination", cascade="all, delete-orphan")


class ExamSubject(Base):
    """Associative table mapping Examinations to Canonical Subjects (Zero-Duplication Core)."""
    __tablename__ = "exam_subjects"
    __table_args__ = (
        UniqueConstraint("exam_code", "subject_id", name="uq_exam_subjects_link"),
    )

    id = Column(String(36), primary_key=True)
    exam_code = Column(String(32), ForeignKey("examinations.code", ondelete="RESTRICT"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    curriculum_role = Column(String(32), default="CORE", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="exam_subjects")
    subject = relationship("Subject")


class ExamTopic(Base):
    """Associative table mapping Examinations to Canonical Topics (Subtopic-Level Applicability Gate)."""
    __tablename__ = "exam_topics"
    __table_args__ = (
        UniqueConstraint("exam_code", "topic_id", name="uq_exam_topics_link"),
    )

    id = Column(String(36), primary_key=True)
    exam_code = Column(String(32), ForeignKey("examinations.code", ondelete="RESTRICT"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    curriculum_role = Column(String(32), default="CORE_MANDATORY", nullable=False)
    inclusion_status = Column(String(32), default="ACTIVE", nullable=False)
    verification_status = Column(String(32), default="VERIFIED_PRIMARY_SOURCE", nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="exam_topics")
    topic = relationship("Topic", back_populates="exam_topics")


class ExamPaper(Base):
    """Official Examination Paper, Shift, or Session."""
    __tablename__ = "exam_papers"

    id = Column(String(36), primary_key=True)
    paper_identifier = Column(String(128), unique=True, nullable=False, index=True)
    exam_code = Column(String(32), ForeignKey("examinations.code", ondelete="RESTRICT"), nullable=False, index=True)
    exam_year = Column(Integer, nullable=False, index=True)
    session_or_shift = Column(String(64), nullable=False)
    paper_code = Column(String(32), nullable=True)
    exam_date = Column(Date, nullable=True)
    total_questions = Column(Integer, nullable=False)
    source_pdf_path = Column(String(512), nullable=True)
    source_pdf_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    examination = relationship("Examination", back_populates="exam_papers")
    questions = relationship("Question", back_populates="exam_paper")


class Question(Base):
    """Canonical Question entity for competitive exams (JEE Main, Advanced, NEET UG)."""
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True)
    exam_paper_id = Column(String(36), ForeignKey("exam_papers.id", ondelete="SET NULL"), nullable=True, index=True)
    paper_question_number = Column(Integer, nullable=True)

    # Authoritative Curriculum Anchor
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Question Classification & Stem
    question_type = Column(String(32), nullable=False)
    question_text = Column(Text, nullable=False)
    diagram_asset_url = Column(String(512), nullable=True)

    # Scoring, Answer Key & Missing-Data Tolerance
    correct_answer_raw = Column(String(256), nullable=True)
    answer_verification_status = Column(String(32), default="UNVERIFIED", nullable=False)
    solution_text = Column(Text, nullable=True)
    ncert_citation = Column(String(256), nullable=True)

    # Numerical Evaluation Policies & Tolerance Bounds
    evaluation_policy = Column(String(64), default="UNRESOLVED_POLICY", nullable=False)
    numerical_precision_type = Column(String(32), default="NOT_APPLICABLE", nullable=False)
    numerical_min_val = Column(Float, nullable=True)
    numerical_max_val = Column(Float, nullable=True)
    numerical_tolerance_epsilon = Column(Float, nullable=True)
    scoring_policy_version = Column(String(32), nullable=True)
    scoring_policy_source = Column(String(256), nullable=True)

    # Pedagogical Attributes
    difficulty_tier = Column(String(16), default="MEDIUM", nullable=False)
    cognitive_level = Column(String(24), default="APPLYING", nullable=False)
    estimated_seconds = Column(Integer, default=120, nullable=False)

    # Provenance, Rights & Publish Permissions
    source_type = Column(String(32), default="OFFICIAL_PYQ", nullable=False)
    rights_status = Column(String(32), default="PENDING_LEGAL_REVIEW", nullable=False)
    publish_permission = Column(String(32), default="FORBIDDEN", nullable=False)
    rights_review_notes = Column(Text, nullable=True)

    # Official Status & Quarantine Disciplinary Fields
    official_status = Column(String(32), default="REGULAR", nullable=False)
    official_status_evidence = Column(Text, nullable=True)
    quarantine_status = Column(String(32), default="CLEAN", nullable=False)
    quarantine_reason = Column(Text, nullable=True)
    eligibility_for_scoring = Column(String(32), default="INELIGIBLE_UNVERIFIED_KEY", nullable=False, index=True)
    verification_status = Column(String(32), default="INGESTED", nullable=False)

    # Deduplication Hash
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    # Relationships
    exam_paper = relationship("ExamPaper", back_populates="questions")
    topic = relationship("Topic")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.sort_order")
    verification_logs = relationship("QuestionVerificationLog", back_populates="question", cascade="all, delete-orphan", order_by="QuestionVerificationLog.reviewed_at")


class QuestionOption(Base):
    """Multiple choice options for SCQ, MCQ_MULTI, AR, and MATCH questions."""
    __tablename__ = "question_options"
    __table_args__ = (
        UniqueConstraint("question_id", "option_key", name="uq_question_option_key"),
    )

    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    option_key = Column(String(8), nullable=False)
    option_text = Column(Text, nullable=False)
    diagram_asset_url = Column(String(512), nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False)
    explanation = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="options")


class QuestionVerificationLog(Base):
    """Audit and verification history for questions."""
    __tablename__ = "question_verification_logs"

    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    verified_by = Column(String(128), nullable=False)
    previous_status = Column(String(32), nullable=False)
    new_status = Column(String(32), nullable=False)
    action_type = Column(String(32), nullable=False)
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="verification_logs")
