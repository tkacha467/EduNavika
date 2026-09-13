from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.content import ContentType


class LearningContentBase(BaseModel):
    topic_id: str
    content_type: ContentType = ContentType.TEXT
    title: str = Field(..., max_length=255)
    content_text: str
    source_document: Optional[str] = Field(None, description="Source PDF filename or path")
    source_page: Optional[int] = Field(None, ge=1, description="Page number in source textbook")
    source_reference: Optional[str] = Field(None, description="Section, heading, or figure reference")
    chunk_identifier: Optional[str] = Field(None, description="Unique chunk hash/ID from ingestion")
    content_metadata: Optional[Dict[str, Any]] = None


class LearningContentCreate(LearningContentBase):
    pass


class LearningContentResponse(LearningContentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
