from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models import EventType


class LearningEventBase(BaseModel):
    student_id: str
    topic_id: str
    event_type: EventType
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    attempt_id: Optional[str] = None
    score: Optional[float] = None
    correctness: Optional[bool] = None
    response_time_ms: Optional[int] = Field(None, ge=0)
    hint_used: Optional[bool] = False
    attempt_number: Optional[int] = Field(1, ge=1)
    event_metadata: Optional[Dict[str, Any]] = None


class LearningEventCreate(LearningEventBase):
    pass


class LearningEventResponse(LearningEventBase):
    id: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
