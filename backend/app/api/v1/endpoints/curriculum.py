from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.curriculum import Standard, Subject, Chapter, Topic
from backend.app.schemas.curriculum import (
    StandardCreate,
    StandardResponse,
    SubjectCreate,
    SubjectResponse,
    ChapterCreate,
    ChapterResponse,
    TopicCreate,
    TopicResponse,
)
from backend.app.schemas.common import PaginatedResponse, ResponseMetadata

router = APIRouter()


# Standards
@router.get("/standards", response_model=List[StandardResponse], summary="List all active standards")
def get_standards(db: Session = Depends(get_db)):
    return db.query(Standard).filter(Standard.is_active == True).order_by(Standard.grade_number).all()


@router.post("/standards", response_model=StandardResponse, status_code=status.HTTP_201_CREATED, summary="Create a new standard")
def create_standard(payload: StandardCreate, db: Session = Depends(get_db)):
    existing = db.query(Standard).filter(Standard.grade_number == payload.grade_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Standard with grade number {payload.grade_number} already exists."
        )
    standard = Standard(**payload.model_dump())
    db.add(standard)
    db.commit()
    db.refresh(standard)
    return standard


@router.get("/standards/{id}/subjects", response_model=List[SubjectResponse], summary="List subjects for a standard")
def get_subjects_by_standard(id: str, db: Session = Depends(get_db)):
    standard = db.query(Standard).filter(Standard.id == id).first()
    if not standard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Standard not found")
    return db.query(Subject).filter(Subject.standard_id == id, Subject.is_active == True).order_by(Subject.name).all()


# Subjects
@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, summary="Create a new subject")
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    standard = db.query(Standard).filter(Standard.id == payload.standard_id).first()
    if not standard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced standard does not exist")
    subject = Subject(**payload.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get("/subjects/{id}/chapters", response_model=List[ChapterResponse], summary="List chapters for a subject")
def get_chapters_by_subject(id: str, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return db.query(Chapter).filter(Chapter.subject_id == id, Chapter.is_active == True).order_by(Chapter.chapter_number).all()


# Chapters
@router.post("/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED, summary="Create a new chapter")
def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == payload.subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced subject does not exist")
    chapter = Chapter(**payload.model_dump())
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


@router.get("/chapters/{id}/topics", response_model=List[TopicResponse], summary="List topics for a chapter")
def get_topics_by_chapter(id: str, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == id).first()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return db.query(Topic).filter(Topic.chapter_id == id, Topic.is_active == True).order_by(Topic.topic_order).all()


# Topics
@router.post("/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED, summary="Create a new topic")
def create_topic(payload: TopicCreate, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == payload.chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referenced chapter does not exist")
    topic = Topic(**payload.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.get("/topics/{id}", response_model=TopicResponse, summary="Get topic by ID")
def get_topic(id: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    return topic
