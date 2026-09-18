from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import StudentProfile
from backend.app.models import Topic
from backend.app.models import TopicPerformance
from backend.app.schemas.performance import TopicPerformanceResponse

router = APIRouter()


@router.get("/students/{id}/topics/{topic_id}/performance", response_model=TopicPerformanceResponse, summary="Get student evidence/performance on a topic")
def get_student_topic_performance(id: str, topic_id: str, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    perf = (
        db.query(TopicPerformance)
        .filter(TopicPerformance.student_id == id, TopicPerformance.topic_id == topic_id)
        .first()
    )
    if not perf:
        # Return a zeroed evidence record if student has not interacted yet
        perf = TopicPerformance(
            student_id=id,
            topic_id=topic_id,
            total_attempts=0,
            correct_attempts=0,
            accuracy=0.0,
            practice_count=0,
            revision_count=0,
            average_response_time=0.0,
            hint_usage_count=0,
            mastery_state="UNASSESSED",
        )
        db.add(perf)
        db.commit()
        db.refresh(perf)

    return perf


@router.get("/students/{id}/performance", response_model=List[TopicPerformanceResponse], summary="Get all topic performance evidence for a student")
def get_student_all_performance(id: str, db: Session = Depends(get_db)):
    student = db.query(StudentProfile).filter(StudentProfile.id == id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    return db.query(TopicPerformance).filter(TopicPerformance.student_id == id).all()
