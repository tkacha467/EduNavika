from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.user import StudentProfile
from backend.app.models.curriculum import Topic
from backend.app.models.forgetting import ForgettingSignal
from backend.app.domain.enums import ForgettingSignalStatus
from backend.app.schemas.forgetting import ForgettingSignalCreate, ForgettingSignalResponse

router = APIRouter()


@router.get("/students/{id}/forgetting-signals", response_model=List[ForgettingSignalResponse], summary="Get forgetting evidence signals for a student")
def get_student_forgetting_signals(
    id: str,
    status_filter: Optional[ForgettingSignalStatus] = None,
    db: Session = Depends(get_db)
):
    student = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    query = db.query(ForgettingSignal).filter(ForgettingSignal.student_id == id)
    if status_filter:
        query = query.filter(ForgettingSignal.status == status_filter)

    return query.order_by(ForgettingSignal.detected_at.desc()).all()


@router.post("/forgetting-signals", response_model=ForgettingSignalResponse, status_code=status.HTTP_201_CREATED, summary="Record a longitudinal forgetting signal")
def create_forgetting_signal(payload: ForgettingSignalCreate, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    data = payload.model_dump(exclude={"prior_performance_ref", "later_performance_ref", "confidence_metadata"})
    signal = ForgettingSignal(**data)
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return signal
