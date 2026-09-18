from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models import AttemptStatus
from backend.app.models import OptionKey


class AnswerSubmit(BaseModel):
    question_id: str
    selected_option: OptionKey
    response_time_ms: int = Field(..., ge=0, description="Response time in milliseconds measured client/server side")
    hint_used: bool = False


class AnswerResponse(BaseModel):
    id: str
    attempt_id: str
    question_id: str
    selected_option: OptionKey
    is_correct: bool
    response_time_ms: int
    hint_used: bool
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttemptCreate(BaseModel):
    student_id: str
    assessment_id: Optional[str] = None
    mcq_id: Optional[str] = None
    topic_id: Optional[str] = None
    selected_option: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    response_time_ms: Optional[int] = Field(default=0, ge=0)
    hint_requested: Optional[bool] = False


class AttemptSubmit(BaseModel):
    submitted_at: Optional[datetime] = None


class AttemptResponse(BaseModel):
    id: str
    student_id: str
    assessment_id: Optional[str] = None
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    total_score: Optional[float] = 0.0
    percentage: Optional[float] = 0.0
    duration_seconds: Optional[int] = None
    status: Optional[AttemptStatus] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Formative practice telemetry fields
    mcq_id: Optional[str] = None
    topic_id: Optional[str] = None
    selected_option: Optional[str] = None
    is_correct: Optional[bool] = None
    score: Optional[float] = None
    response_time_ms: Optional[int] = None
    hint_requested: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class AttemptDetailResponse(AttemptResponse):
    answers: List[AnswerResponse] = []
