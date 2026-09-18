from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import TeacherProfile, StudentProfile
from backend.app.models import Topic
from backend.app.models import TeacherAction
from backend.app.schemas.teacher_action import TeacherActionCreate, TeacherActionResponse

router = APIRouter()


@router.post("/teacher-actions", response_model=TeacherActionResponse, status_code=status.HTTP_201_CREATED, summary="Log a teacher intervention/action")
def create_teacher_action(payload: TeacherActionCreate, db: Session = Depends(get_db)):
    teacher = db.query(TeacherProfile).filter(TeacherProfile.id == payload.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher profile not found")

    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    topic = db.query(Topic).filter(Topic.id == payload.topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    action = TeacherAction(**payload.model_dump())
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.get("/teachers/{id}/actions", response_model=List[TeacherActionResponse], summary="List interventions logged by teacher")
def get_teacher_actions(id: str, db: Session = Depends(get_db)):
    teacher = db.query(TeacherProfile).filter(TeacherProfile.id == id).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher profile not found")

    return db.query(TeacherAction).filter(TeacherAction.teacher_id == id).order_by(TeacherAction.created_at.desc()).all()
