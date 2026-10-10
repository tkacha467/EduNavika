from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models import Standard, Subject, Chapter, Topic
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


@router.get("/curriculum/hierarchy", summary="Retrieve complete offline curriculum hierarchy with content & practice availability")
def get_curriculum_hierarchy(
    grade: int = Query(10, description="Standard grade number"),
    db: Session = Depends(get_db)
):
    standard = db.query(Standard).filter(Standard.grade_number == grade, Standard.is_active == True).first()
    if not standard:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Standard {grade} not found")

    subjects = db.query(Subject).filter(
        Subject.standard_id == standard.id,
        Subject.is_active == True
    ).order_by(Subject.name).all()

    from backend.app.services.progress_service import StudentProgressService
    from backend.app.services.curriculum_question_bank import CANONICAL_CURRICULUM_BANK
    from backend.app.models import LearningContent

    valid_subjects = [s for s in subjects if not StudentProgressService._is_synthetic_subject(s)]
    canonical_topic_ids = set(CANONICAL_CURRICULUM_BANK.keys())

    result_subjects = []
    for s in valid_subjects:
        chapters = db.query(Chapter).filter(
            Chapter.subject_id == s.id,
            Chapter.is_active == True
        ).order_by(Chapter.chapter_number).all()

        real_chapters = [c for c in chapters if c.chapter_number < 90 and "general content" not in (c.title or "").lower()]

        result_chapters = []
        for c in real_chapters:
            topics = db.query(Topic).filter(
                Topic.chapter_id == c.id,
                Topic.is_active == True
            ).order_by(Topic.topic_order).all()

            result_topics = []
            for t in topics:
                if "general content" in (t.title or "").lower():
                    continue

                content_items = db.query(LearningContent).filter(LearningContent.topic_id == t.id).all()
                content_count = len(content_items)
                has_content = content_count > 0
                source_doc = content_items[0].source_document if has_content else None
                source_page = content_items[0].source_page if has_content else None

                norm_title = (t.title or "").lower().replace('&', 'and').replace('—', '-').strip()
                has_practice = t.id in canonical_topic_ids
                if not has_practice:
                    for cid, qlist in CANONICAL_CURRICULUM_BANK.items():
                        if qlist:
                            cand_title = qlist[0]["topic_title"].lower().replace('&', 'and').replace('—', '-').strip()
                            cand_chap = qlist[0]["chapter"].lower().replace('&', 'and').replace('—', '-').strip()
                            if norm_title in cand_title or cand_title in norm_title or norm_title in cand_chap or cand_chap in norm_title:
                                has_practice = True
                                break

                result_topics.append({
                    "id": t.id,
                    "title": t.title,
                    "topic_order": t.topic_order,
                    "content_available": has_content,
                    "content_count": content_count,
                    "practice_available": has_practice,
                    "source_document": source_doc,
                    "source_page": source_page,
                })

            result_chapters.append({
                "id": c.id,
                "chapter_number": c.chapter_number,
                "title": c.title,
                "total_topics": len(result_topics),
                "topics": result_topics,
            })

        result_subjects.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "total_chapters": len(result_chapters),
            "chapters": result_chapters,
        })

    return {
        "standard_grade": standard.grade_number,
        "standard_name": standard.name,
        "total_subjects": len(result_subjects),
        "subjects": result_subjects,
    }


# ==============================================================================
# School LAN Offline-First Curriculum Distribution (Problem Statement 06, Section 4)
# ==============================================================================
from backend.app.services.curriculum_package_service import CurriculumPackageService
from fastapi import Body


@router.get(
    "/curriculum/package/export",
    summary="Export versioned, tamper-proof curriculum bundle with SHA-256 checksum for LAN distribution"
)
@router.get(
    "/package/export",
    include_in_schema=False
)
def export_curriculum_package(
    grade: int = Query(10, description="Standard grade number"),
    db: Session = Depends(get_db),
):
    try:
        return CurriculumPackageService.export_package(db=db, grade=grade)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Package export failed: {str(e)}"
        )


@router.post(
    "/curriculum/package/import",
    summary="Verify cryptographic SHA-256 checksum and install curriculum bundle into local SQLite database"
)
@router.post(
    "/package/import",
    include_in_schema=False
)
def import_curriculum_package(
    package: dict = Body(..., description="Curriculum package bundle containing manifest and payload"),
    db: Session = Depends(get_db),
):
    try:
        return CurriculumPackageService.import_package(db=db, package=package)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Package import failed: {str(e)}"
        )

