from sqlalchemy import Column, String, Text, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin
from backend.app.domain.enums import QuestionStatus, QuestionDifficulty, OptionKey

# Re-export for backward compatibility
__all__ = [
    "MCQQuestion",
    "QuestionHistory",
    "QuestionStatus",
    "QuestionDifficulty",
    "OptionKey",
]


class MCQQuestion(BaseModelMixin, Base):
    __tablename__ = "mcq_questions"

    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_option = Column(SQLEnum(OptionKey), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(SQLEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM, nullable=False)
    
    # Provenance tracking
    source_content_id = Column(String(36), ForeignKey("learning_contents.id", ondelete="SET NULL"), nullable=True, index=True)
    generation_model = Column(String(100), nullable=True)
    generation_version = Column(String(50), nullable=True)
    status = Column(SQLEnum(QuestionStatus), default=QuestionStatus.DRAFT, nullable=False, index=True)

    # Relationships
    topic = relationship("Topic", back_populates="mcqs")
    source_content = relationship("LearningContent", back_populates="derived_mcqs")
    history = relationship("QuestionHistory", back_populates="question", uselist=False, cascade="all, delete-orphan")
    assessment_links = relationship("AssessmentQuestion", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="question")


class QuestionHistory(BaseModelMixin, Base):
    __tablename__ = "question_history"

    question_id = Column(String(36), ForeignKey("mcq_questions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    normalized_question_text = Column(Text, nullable=False)
    text_hash = Column(String(64), index=True, nullable=False)  # SHA-256 hex digest
    embedding_reference = Column(String(255), nullable=True)     # Pointer to future vector storage
    generation_metadata = Column(JSON, nullable=True)

    # Relationships
    question = relationship("MCQQuestion", back_populates="history")
