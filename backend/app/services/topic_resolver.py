"""
Shared Curriculum Topic & Profile Resolution Service for EduNavika.
Resolves client topic identifiers (UUIDs, titles, normalized names, chapter names, subject aliases)
to canonical Topic database records without circular import issues.
"""

from typing import Optional, List
import logging
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from backend.app.models import StudentProfile, User, UserRole, Topic, Chapter, Subject

logger = logging.getLogger("topic_resolver")


def resolve_topic(db: Session, topic_id: Optional[str]) -> Optional[Topic]:
    """
    Robustly resolves a topic by:
    1. Exact UUID match on Topic.id
    2. Exact title match on Topic.title (case-insensitive)
    3. Normalized title match (e.g. '&' -> 'and', '—' -> '-')
    4. Partial / substring match on Topic.title
    5. Reverse substring match on Topic.title
    6. Chapter title match -> returns primary topic under that chapter
    7. Subject / syllabus alias match (e.g. 'Mathematics' -> primary Math topic)
    """
    if not topic_id:
        return None

    # 1. Exact ID
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic:
        return topic

    # 2. Exact Title
    topic = db.query(Topic).filter(func.lower(Topic.title) == func.lower(topic_id)).first()
    if topic:
        return topic

    # 3. Normalized Title
    norm = topic_id.replace('&', 'and').replace('—', '-').replace('–', '-').replace('?', '-').strip()
    topic = db.query(Topic).filter(func.lower(Topic.title) == func.lower(norm)).first()
    if topic:
        return topic

    # 4. Partial Title Match
    topic = db.query(Topic).filter(Topic.title.ilike(f"%{norm}%")).first()
    if topic:
        return topic

    # 5. Reverse Substring Match (e.g. "Chemical Reactions" matching "Chemical Reactions and Equations")
    all_topics = db.query(Topic).all()
    norm_lower = norm.lower()
    for t in all_topics:
        t_clean = t.title.replace('&', 'and').replace('—', '-').replace('–', '-').replace('?', '-').lower().strip()
        if (len(t_clean) >= 4 and t_clean in norm_lower) or (len(norm_lower) >= 4 and norm_lower in t_clean):
            return t

    # 6. Chapter match: check if a chapter matches the topic_id / name
    all_chapters = db.query(Chapter).all()
    for c in all_chapters:
        c_clean = c.title.replace('&', 'and').replace('—', '-').replace('–', '-').replace('?', '-').lower().strip()
        if (len(c_clean) >= 4 and c_clean in norm_lower) or (len(norm_lower) >= 4 and norm_lower in c_clean):
            first_top = (
                db.query(Topic)
                .filter(Topic.chapter_id == c.id)
                .order_by(Topic.topic_order.asc())
                .first()
            )
            if first_top:
                return first_top

    # 7. Syllabus / Subject Domain Aliases (e.g. 'Real Numbers & Polynomials', 'Mathematics', 'Quadratic Equations')
    # Maps Math concepts to primary Math topic in DB
    math_aliases = ["real number", "polynomial", "quadratic", "arithmetic", "math", "statistic", "probability", "geometry", "trigonometry"]
    if any(a in norm_lower for a in math_aliases):
        math_top = (
            db.query(Topic)
            .join(Chapter, Topic.chapter_id == Chapter.id)
            .join(Subject, Chapter.subject_id == Subject.id)
            .filter(Subject.name.ilike("%Math%"))
            .first()
        )
        if math_top:
            return math_top

    # Maps Science concepts to primary topic in relevant Science chapter
    if "chemical" in norm_lower or "reaction" in norm_lower:
        chem_top = db.query(Topic).filter(Topic.title.ilike("%Chemical Reactions%")).first()
        if chem_top:
            return chem_top

    if "acid" in norm_lower or "base" in norm_lower or "salt" in norm_lower:
        acid_top = (
            db.query(Topic)
            .join(Chapter, Topic.chapter_id == Chapter.id)
            .filter(Chapter.title.ilike("%Acid%"))
            .first()
        )
        if acid_top:
            return acid_top

    if "electr" in norm_lower or "circuit" in norm_lower:
        elec_top = (
            db.query(Topic)
            .join(Chapter, Topic.chapter_id == Chapter.id)
            .filter(Chapter.title.ilike("%Electricity%"))
            .first()
        )
        if elec_top:
            return elec_top

    return None


def get_or_create_student_profile(db: Session, student_id: str) -> Optional[StudentProfile]:
    """Finds or auto-provisions a StudentProfile for the student."""
    # 1. Direct match by StudentProfile.id
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if student:
        return student

    # 2. Match by StudentProfile.user_id
    student = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
    if student:
        return student

    # 3. Match User by ID or student role
    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        user = db.query(User).filter(User.role == UserRole.STUDENT).first()
    if not user:
        user = db.query(User).filter(User.email == "kachatushar108@gmail.com").first()

    if user:
        existing_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if existing_profile:
            return existing_profile

        try:
            new_profile = StudentProfile(
                id=student_id if (len(student_id) <= 36 and not student_id.startswith("http")) else None,
                user_id=user.id,
                enrollment_number=f"EN-{user.id[:8]}",
                division="A",
                preferred_language="en",
            )
            db.add(new_profile)
            db.commit()
            db.refresh(new_profile)
            return new_profile
        except (IntegrityError, OperationalError):
            db.rollback()
            return db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()

    return None
