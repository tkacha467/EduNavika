from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
from backend.app.models.base import BaseModelMixin
from backend.app.domain.enums import ContentType

# Re-export for backward compatibility
__all__ = ["LearningContent", "ContentType"]


class LearningContent(BaseModelMixin, Base):
    __tablename__ = "learning_contents"
    __table_args__ = (
        CheckConstraint("source_page IS NULL OR source_page >= 1", name="chk_content_source_page_positive"),
    )

    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(SQLEnum(ContentType), default=ContentType.TEXT, nullable=False)
    title = Column(String(255), nullable=False)
    content_text = Column(Text, nullable=False)
    source_document = Column(String(255), nullable=True, index=True)
    source_page = Column(Integer, nullable=True)
    source_reference = Column(String(255), nullable=True)
    chunk_identifier = Column(String(100), nullable=True, index=True)
    content_metadata = Column(JSON, nullable=True)

    # Relationships
    topic = relationship("Topic", back_populates="learning_contents")
    derived_mcqs = relationship("MCQQuestion", back_populates="source_content")
