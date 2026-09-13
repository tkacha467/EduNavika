from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# Standard
class StandardBase(BaseModel):
    grade_number: int = Field(..., ge=1, le=12, description="Grade level (e.g. 9, 10, 11, 12)")
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class StandardCreate(StandardBase):
    pass


class StandardResponse(StandardBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Subject
class SubjectBase(BaseModel):
    standard_id: str
    name: str = Field(..., max_length=150)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_active: bool = True


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Chapter
class ChapterBase(BaseModel):
    subject_id: str
    chapter_number: int = Field(..., ge=1)
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    source_reference: Optional[str] = None
    is_active: bool = True


class ChapterCreate(ChapterBase):
    pass


class ChapterResponse(ChapterBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Topic
class TopicBase(BaseModel):
    chapter_id: str
    topic_order: int = Field(..., ge=1)
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    learning_objectives: Optional[str] = None
    is_active: bool = True


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
