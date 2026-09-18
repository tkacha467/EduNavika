from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import StudentProfile
from backend.app.models import Topic
from backend.app.models import LearningEvent, EventType
from backend.app.schemas.learning_event import LearningEventCreate, LearningEventResponse
from backend.app.schemas.common import PaginatedResponse, ResponseMetadata
from backend.app.services.event_recorder import EventRecorderService

router = APIRouter()

"""
LearningEvent Endpoints:
Strictly append-only research substrate.
MUTATION (PUT/PATCH) AND DELETION (DELETE) ARE STRICTLY FORBIDDEN by architectural design.
Raw longitudinal interaction data must remain immutable for future feature engineering
and cognitive decay modeling.
"""


@router.post("/learning-events", response_model=LearningEventResponse, status_code=status.HTTP_201_CREATED, summary="Log a raw longitudinal learning event")
def log_learning_event(payload: LearningEventCreate, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    event = EventRecorderService.record_event(
        db=db,
        student_id=payload.student_id,
        topic_id=payload.topic_id,
        event_type=payload.event_type,
        timestamp=payload.timestamp,
        session_id=payload.session_id,
        attempt_id=payload.attempt_id,
        score=payload.score,
        correctness=payload.correctness,
        response_time_ms=payload.response_time_ms,
        hint_used=payload.hint_used or False,
        attempt_number=payload.attempt_number or 1,
        event_metadata=payload.event_metadata,
        auto_commit=True,
    )
    return event


@router.get("/students/{id}/learning-events", response_model=PaginatedResponse[LearningEventResponse], summary="Retrieve longitudinal learning events for a student")
def get_student_learning_events(
    id: str,
    topic_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    query = db.query(LearningEvent).filter(LearningEvent.student_id == id)
    if topic_id:
        query = query.filter(LearningEvent.topic_id == topic_id)
    if event_type:
        query = query.filter(LearningEvent.event_type == event_type)
    if since:
        query = query.filter(LearningEvent.timestamp >= since)
    if until:
        query = query.filter(LearningEvent.timestamp <= until)

    total_count = query.count()
    items = query.order_by(LearningEvent.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 0

    return PaginatedResponse(
        items=items,
        metadata=ResponseMetadata(
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    )
