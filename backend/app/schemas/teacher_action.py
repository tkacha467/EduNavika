from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models import TeacherActionType


class TeacherActionBase(BaseModel):
    teacher_id: str
    student_id: str
    topic_id: str
    action_type: TeacherActionType
    note: Optional[str] = None


class TeacherActionCreate(TeacherActionBase):
    pass


class TeacherActionResponse(TeacherActionBase):
    id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
