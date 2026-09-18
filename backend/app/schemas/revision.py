from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models import RevisionPriority, RevisionCompletionState


class RevisionPlanBase(BaseModel):
    student_id: str
    topic_id: str
    recommended_revision_at: datetime
    priority: RevisionPriority = RevisionPriority.MEDIUM
    reason: Optional[str] = None
    completion_state: RevisionCompletionState = RevisionCompletionState.PENDING


class RevisionPlanCreate(RevisionPlanBase):
    pass


class RevisionPlanResponse(RevisionPlanBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
