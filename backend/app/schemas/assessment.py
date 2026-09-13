from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.assessment import AssessmentStatus
from backend.app.schemas.mcq import MCQResponse


class AssessmentQuestionCreate(BaseModel):
    question_id: str
    question_order: int = Field(default=1, ge=1)
    points: float = Field(default=1.0, ge=0.0)


class AssessmentQuestionResponse(BaseModel):
    id: str
    assessment_id: str
    question_id: str
    question_order: int
    points: float
    question: Optional[MCQResponse] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentBase(BaseModel):
    teacher_id: str
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    topic_id: Optional[str] = None
    status: AssessmentStatus = AssessmentStatus.DRAFT
    scheduled_at: Optional[datetime] = None


class AssessmentCreate(AssessmentBase):
    questions: Optional[List[AssessmentQuestionCreate]] = []


class AssessmentPublish(BaseModel):
    published_at: Optional[datetime] = None


class AssessmentResponse(AssessmentBase):
    id: str
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssessmentDetailResponse(AssessmentResponse):
    question_links: List[AssessmentQuestionResponse] = []
