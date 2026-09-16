from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.curriculum import Topic
from backend.app.models.content import LearningContent
from backend.app.models.user import StudentProfile
from backend.app.models.learning_event import EventType
from backend.app.schemas.content import LearningContentCreate, LearningContentResponse
from backend.app.schemas.learning_event import LearningEventResponse
from backend.app.services.event_recorder import EventRecorderService

router = APIRouter()


class TopicStudyRequest(BaseModel):
    student_id: str
    session_id: Optional[str] = None
    content_id: Optional[str] = None
    dwell_time_seconds: Optional[int] = Field(None, ge=0)
    idempotency_key: Optional[str] = None


@router.get("/topics/{id}/content", response_model=List[LearningContentResponse], summary="Get learning content for a topic")
def get_topic_content(id: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    return db.query(LearningContent).filter(LearningContent.topic_id == id).all()


@router.post("/content", response_model=LearningContentResponse, status_code=status.HTTP_201_CREATED, summary="Create learning content item")
def create_content(payload: LearningContentCreate, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced topic does not exist")
    content = LearningContent(**payload.model_dump())
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@router.post("/topics/{id}/study", response_model=LearningEventResponse, status_code=status.HTTP_201_CREATED, summary="Record a student content study/reading session (LEARN event)")
def record_topic_study(id: str, payload: TopicStudyRequest, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    if payload.content_id:
        content = db.query(LearningContent).filter(LearningContent.id == payload.content_id).first()
        if not content:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Learning content not found")

    dwell_ms = (payload.dwell_time_seconds * 1000) if payload.dwell_time_seconds is not None else None
    event = EventRecorderService.record_event(
        db=db,
        student_id=payload.student_id,
        topic_id=id,
        event_type=EventType.LEARN,
        session_id=payload.session_id,
        response_time_ms=dwell_ms,
        event_metadata={
            "content_id": payload.content_id,
            "dwell_time_seconds": payload.dwell_time_seconds,
        },
        idempotency_key=payload.idempotency_key,
        auto_commit=True,
    )
    return event

