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
from backend.app.models import StudentProfile, User, UserRole, Topic, Chapter, Subject, Standard

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

    # 0. Deterministic mapping for frontend placeholder IDs and canonical syllabus codes
    DIRECT_FRONTEND_MAP = {
        # Subject Aliases mapping to primary verified topics
        "mathematics": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
        "math": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
        "mth": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
        "science": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "sci": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "chemistry": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "chem": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "chm": "5a321a44-bc06-4db4-a50f-5e53f913b612",
        "physics": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",
        "phy": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",
        "biology": "203b6750-6dcf-4dfc-89fd-61ca38de5fc0",
        "bio": "203b6750-6dcf-4dfc-89fd-61ca38de5fc0",
        "english": "78c9fedc-72e2-47ff-9ea4-56854e510e43",
        "eng": "78c9fedc-72e2-47ff-9ea4-56854e510e43",
        "diagnostic check": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",
        "diagnostic test": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",

        # Mathematics Topics
        "m1": "c3dd6779-9b5b-411c-9ade-07e241713835",  # Quadratic Equations (4.2 Quadratic Equations)
        "m2": "a5d04c19-6e6b-4a88-a23b-414f71308ba9",  # Trigonometry (8.2 Trigonometric Ratios)
        "m3": "17550e06-fb15-412d-b6a9-97d3c3848c70",  # Coordinate Geometry (7.2 Distance Formula)
        "m4": "dba2e106-7967-4de4-892b-934b06a17b2f",  # Probability (14.2 Summary)
        "m5": "20d70d12-d01a-44d7-82be-772d609eb4f5",  # Statistics (13.2 Mean of Grouped Data)
        "math_real_numbers": "e84e1b11-f928-4b38-93ad-738af5c0b1e5",  # Fundamental Theorem of Arithmetic
        "math_ap": "1d70ba4e-6c09-432c-b740-604677902d40",  # Arithmetic Progressions
        
        # Science Topics
        "c1": "5a321a44-bc06-4db4-a50f-5e53f913b612",  # Chemical Reactions and Equations
        "c2": "efee2da2-bd20-42bb-ad01-df2516530b1f",  # Acids, Bases & Salts (2.2 WHA)
        "c3": "9b029f78-a6e2-4776-93a1-0af927cfea40",  # Carbon Compounds / Organic Chemistry
        "c4": "0a40d615-e590-4088-bbb5-3ab26de1c1e4",  # Metals and Non-metals
        "p1": "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0",  # Electricity (11.7 HEA)
        "p2": "d8e3396b-eb3e-4bb6-9ee7-46031bcc7426",  # Light Reflection & Refraction
        "b1": "203b6750-6dcf-4dfc-89fd-61ca38de5fc0",  # Life Processes / Photosynthesis
        "b2": "203b6750-6dcf-4dfc-89fd-61ca38de5fc0",  # Life Processes
        "b3": "712ce1df-cda6-4b11-ae3e-554ce99666cf",  # Heredity & Evolution
        "e1": "78c9fedc-72e2-47ff-9ea4-56854e510e43",  # A Letter to God
        "e2": "01333c04-a84b-4171-817a-b62d8ea8f645",  # Nelson Mandela: Long Walk to Freedom
        "e3": "b47e3404-0988-4738-b3f9-93bf30ea38c6",  # Two Stories about Flying
    }
    target_mapped_id = DIRECT_FRONTEND_MAP.get(topic_id.strip().lower())
    if target_mapped_id:
        mapped_topic = db.query(Topic).filter(Topic.id == target_mapped_id).first()
        if mapped_topic:
            return mapped_topic

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
    norm_lower = norm.lower()
    topic = db.query(Topic).filter(func.lower(Topic.title) == func.lower(norm)).first()
    if topic:
        return topic

    # 4. Partial Title Match
    topic = db.query(Topic).filter(Topic.title.ilike(f"%{norm}%")).first()
    if topic:
        return topic

    # 4. Granular Subject and Topic Domain Aliases (checked before loose chapter matching)
    # Mathematics
    if "quadratic" in norm_lower:
        q_top = db.query(Topic).filter(Topic.id == "c3dd6779-9b5b-411c-9ade-07e241713835").first()
        if q_top:
            return q_top

    if "trigonometr" in norm_lower:
        trig_top = db.query(Topic).filter(Topic.id == "a5d04c19-6e6b-4a88-a23b-414f71308ba9").first()
        if trig_top:
            return trig_top

    if "coordinate" in norm_lower or "distance" in norm_lower:
        coord_top = db.query(Topic).filter(Topic.id == "17550e06-fb15-412d-b6a9-97d3c3848c70").first()
        if coord_top:
            return coord_top

    if "arithmetic" in norm_lower or "progression" in norm_lower:
        ap_top = db.query(Topic).filter(Topic.id == "1d70ba4e-6c09-432c-b740-604677902d40").first()
        if ap_top:
            return ap_top

    if "statistic" in norm_lower or "mean" in norm_lower or "median" in norm_lower or "mode" in norm_lower:
        stat_top = db.query(Topic).filter(Topic.id == "20d70d12-d01a-44d7-82be-772d609eb4f5").first()
        if stat_top:
            return stat_top

    if "probability" in norm_lower:
        prob_top = db.query(Topic).filter(Topic.id == "dba2e106-7967-4de4-892b-934b06a17b2f").first()
        if prob_top:
            return prob_top

    if "real number" in norm_lower or "polynomial" in norm_lower:
        real_top = db.query(Topic).filter(Topic.id == "e84e1b11-f928-4b38-93ad-738af5c0b1e5").first()
        if real_top:
            return real_top

    # Science
    if "chemical" in norm_lower or "reaction" in norm_lower:
        chem_top = db.query(Topic).filter(Topic.id == "5a321a44-bc06-4db4-a50f-5e53f913b612").first()
        if chem_top:
            return chem_top

    if "acid" in norm_lower or "base" in norm_lower or "salt" in norm_lower:
        acid_top = db.query(Topic).filter(Topic.id == "efee2da2-bd20-42bb-ad01-df2516530b1f").first()
        if acid_top:
            return acid_top

    if "electr" in norm_lower or "circuit" in norm_lower:
        elec_top = db.query(Topic).filter(Topic.id == "ea3cb4fd-f34d-409b-b0f6-d69b70db05b0").first()
        if elec_top:
            return elec_top

    # 5. Reverse Substring Match (e.g. "Chemical Reactions" matching "Chemical Reactions and Equations")
    all_topics = db.query(Topic).all()
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

    # 7. Subject fallback: resolve subject queries to a verified topic under that subject
    matching_subj = db.query(Subject).filter(
        (Subject.name.ilike(f"%{norm_lower}%")) | (Subject.code.ilike(f"%{norm_lower}%")),
        Subject.is_active == True
    ).first()
    if matching_subj:
        # Prioritize topics that have canonical questions
        from backend.app.services.curriculum_question_bank import CANONICAL_CURRICULUM_BANK
        for tid in CANONICAL_CURRICULUM_BANK.keys():
            t_cand = db.query(Topic).join(Chapter).filter(
                Topic.id == tid,
                Chapter.subject_id == matching_subj.id,
                Topic.is_active == True
            ).first()
            if t_cand:
                return t_cand

        # Otherwise pick the first topic with textbook content under this subject
        from backend.app.models import LearningContent
        top_with_content = (
            db.query(Topic)
            .join(Chapter, Topic.chapter_id == Chapter.id)
            .join(LearningContent, LearningContent.topic_id == Topic.id)
            .filter(Chapter.subject_id == matching_subj.id, Topic.is_active == True)
            .first()
        )
        if top_with_content:
            return top_with_content

        # Fallback to first topic
        subj_top = (
            db.query(Topic)
            .join(Chapter, Topic.chapter_id == Chapter.id)
            .filter(Chapter.subject_id == matching_subj.id, Topic.is_active == True)
            .order_by(Topic.topic_order.asc())
            .first()
        )
        if subj_top:
            return subj_top

    return None


def get_or_create_student_profile(db: Session, student_id: str) -> Optional[StudentProfile]:
    """Finds or auto-provisions a StudentProfile for the student."""
    if not student_id:
        return None

    # 1. Direct match by StudentProfile.id
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if student:
        return student

    # 2. Match by StudentProfile.user_id
    student = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
    if student:
        return student

    # 3. Match User by ID
    user = db.query(User).filter(User.id == student_id).first()

    # 4. If student_id is a known demo/default alias or matches default student account
    KNOWN_DEMO_ALIASES = {
        "demo", "default", "me", "default-student", "student-001",
        "ea169b32-edfa-4f07-a5f9-be4cc8816c43"
    }
    if not user and student_id in KNOWN_DEMO_ALIASES:
        user = db.query(User).filter(User.email == "kachatushar108@gmail.com").first()
        if not user:
            user = db.query(User).filter(User.role == UserRole.STUDENT).first()

    if user:
        existing_profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        if existing_profile:
            return existing_profile

        try:
            first_std = db.query(Standard).filter(Standard.grade_number == 10).first() or db.query(Standard).first()
            new_profile = StudentProfile(
                id=student_id if (len(student_id) <= 36 and not student_id.startswith("http")) else None,
                user_id=user.id,
                standard_id=first_std.id if first_std else None,
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

    return None
