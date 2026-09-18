from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import StudentProfile
from backend.app.domain.decay_engine import (
    AdaptiveLearningService,
    DecayDetectionResponse,
    AdaptiveScheduleResponse,
)

router = APIRouter(prefix="/adaptive")
adaptive_service = AdaptiveLearningService()


from backend.app.models import EventType
from backend.app.services.event_recorder import EventRecorderService


class RevisionOutcomeRequest(BaseModel):
    student_id: str
    topic_id: str
    score: float = Field(..., ge=0.0, le=100.0)
    correctness: bool
    response_time_ms: Optional[int] = Field(None, ge=0)
    session_id: Optional[str] = None
    idempotency_key: Optional[str] = None



@router.post(
    "/detect-decay/{student_id}",
    response_model=DecayDetectionResponse,
    summary="Trigger longitudinal decay analysis and idempotent revision scheduling"
)
def detect_decay_for_student(
    student_id: str,
    topic_id: Optional[str] = Query(None, description="Optional topic filter"),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {student_id} not found"
        )

    return adaptive_service.detect_and_schedule_for_student(
        db=db,
        student_id=student_id,
        topic_id=topic_id
    )


@router.get(
    "/schedule/{student_id}",
    response_model=AdaptiveScheduleResponse,
    summary="Get prioritized adaptive revision queue for a student"
)
def get_adaptive_schedule(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {student_id} not found"
        )

    return adaptive_service.get_student_schedule(db=db, student_id=student_id)


@router.post(
    "/revision-outcome",
    summary="Process a completed revision attempt and drive signal lifecycle"
)
def process_revision_outcome(
    payload: RevisionOutcomeRequest,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student profile {payload.student_id} not found"
        )

    # Record longitudinal REVISION learning event
    event = EventRecorderService.record_event(
        db=db,
        student_id=payload.student_id,
        topic_id=payload.topic_id,
        event_type=EventType.REVISION,
        score=payload.score,
        correctness=payload.correctness,
        response_time_ms=payload.response_time_ms,
        session_id=payload.session_id,
        idempotency_key=payload.idempotency_key,
        event_metadata={"revision_flow": True},
        auto_commit=False,
    )

    result = adaptive_service.handle_revision_attempt(
        db=db,
        student_id=payload.student_id,
        topic_id=payload.topic_id,
        score=payload.score,
        correctness=payload.correctness,
        response_time_ms=payload.response_time_ms
    )
    return {"status": "SUCCESS", "lifecycle_update": result, "event_id": event.id}

