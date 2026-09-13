from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.attempt import AttemptStatus
from backend.app.models.mcq import OptionKey


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
    assessment_id: str


class AttemptSubmit(BaseModel):
    submitted_at: Optional[datetime] = None


class AttemptResponse(BaseModel):
    id: str
    student_id: str
    assessment_id: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    total_score: float
    percentage: float
    duration_seconds: Optional[int] = None
    status: AttemptStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttemptDetailResponse(AttemptResponse):
    answers: List[AnswerResponse] = []
