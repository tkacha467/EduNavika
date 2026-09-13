from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.curriculum import Topic
from backend.app.models.content import LearningContent
from backend.app.schemas.content import LearningContentCreate, LearningContentResponse

router = APIRouter()


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
