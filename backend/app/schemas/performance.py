from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TopicPerformanceResponse(BaseModel):
    id: str
    student_id: str
    topic_id: str
    total_attempts: int
    correct_attempts: int
    accuracy: float
    last_activity_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    practice_count: int
    revision_count: int
    average_response_time: float
    hint_usage_count: int
    mastery_state: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
