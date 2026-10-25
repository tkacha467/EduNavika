"""
EduNavika — Milestone 4: Canonical Curriculum Seeder.
Idempotent, transaction-safe seeder for Examinations, Standards 11 & 12,
canonical STEM Subjects, and Exam-to-Subject relational mappings.
"""

import sys
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from backend.app.core.config import settings
from backend.app.models.curriculum_models import Standard, Subject
from backend.app.models.competitive_models import Examination, ExamSubject
from backend.app.models.core_models import generate_uuid

# Deterministic namespace for EduNavika canonical entities
EDUNAVIKA_DNS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

def deterministic_uuid(seed_key: str) -> str:
    """Generate stable, idempotent UUIDv5 from a natural domain key."""
    return str(uuid.uuid5(EDUNAVIKA_DNS, seed_key))

# 1. Canonical Examinations Data
CANONICAL_EXAMINATIONS = [
    {
        "code": "JEE_MAIN",
        "name": "Joint Entrance Examination Main",
        "conducting_body": "National Testing Agency",
        "description": "National computer-based engineering entrance assessment for NITs, IIITs, and CFTIs, and qualifying examination for JEE Advanced.",
        "is_active": True,
    },
    {
        "code": "JEE_ADVANCED",
        "name": "Joint Entrance Examination Advanced",
        "conducting_body": "IIT Joint Admission Board",
        "description": "Premier national computer-based engineering entrance examination for admission to the Indian Institutes of Technology (IITs).",
        "is_active": True,
    },
    {
        "code": "NEET_UG",
        "name": "National Eligibility cum Entrance Test Undergraduate",
        "conducting_body": "National Testing Agency",
        "description": "National single-window medical entrance examination for undergraduate medical (MBBS, BDS, AYUSH) admissions across India.",
        "is_active": True,
    },
]

# 2. Canonical Standards Data
CANONICAL_STANDARDS = [
    {
        "id": deterministic_uuid("edunavika.standard.11"),
        "grade_number": 11,
        "name": "Standard 11",
        "description": "Senior Secondary Year 1 (Science Stream: Physics, Chemistry, Mathematics, Biology)",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.standard.12"),
        "grade_number": 12,
        "name": "Standard 12",
        "description": "Senior Secondary Year 2 / Higher Secondary (Science Stream: Physics, Chemistry, Mathematics, Biology)",
        "is_active": True,
    },
]

# 3. Canonical STEM Subjects Data (Zero-Duplication Foundation)
CANONICAL_SUBJECTS = [
    # Standard 11 Science
    {
        "id": deterministic_uuid("edunavika.subject.std11.physics"),
        "standard_grade": 11,
        "name": "Physics",
        "code": "PHYS11",
        "description": "Class 11 Physics (Mechanics, Thermal Physics, Waves & Oscillations). Canonical shared core for JEE & NEET.",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.subject.std11.chemistry"),
        "standard_grade": 11,
        "name": "Chemistry",
        "code": "CHEM11",
        "description": "Class 11 Chemistry (Physical, Inorganic, Organic Principles). Canonical shared core for JEE & NEET.",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.subject.std11.mathematics"),
        "standard_grade": 11,
        "name": "Mathematics",
        "code": "MATH11",
        "description": "Class 11 Mathematics (Algebra, Coordinate Geometry, Trigonometry, Calculus foundation). Relevant for JEE.",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.subject.std11.biology"),
        "standard_grade": 11,
        "name": "Biology",
        "code": "BIO11",
        "description": "Class 11 Biology (Diversity, Cell Biology, Plant Physiology, Human Physiology). Relevant for NEET.",
        "is_active": True,
    },
    # Standard 12 Science
    {
        "id": deterministic_uuid("edunavika.subject.std12.physics"),
        "standard_grade": 12,
        "name": "Physics",
        "code": "PHYS12",
        "description": "Class 12 Physics (Electromagnetism, Optics, Modern Physics, Semiconductor Electronics). Canonical shared core for JEE & NEET.",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.subject.std12.chemistry"),
        "standard_grade": 12,
        "name": "Chemistry",
        "code": "CHEM12",
        "description": "Class 12 Chemistry (Electrochemistry, Kinetics, Coordination, Organic Functional Groups). Canonical shared core for JEE & NEET.",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.subject.std12.mathematics"),
        "standard_grade": 12,
        "name": "Mathematics",
        "code": "MATH12",
        "description": "Class 12 Mathematics (Calculus, Vectors & 3D Geometry, Linear Programming, Probability). Relevant for JEE.",
        "is_active": True,
    },
    {
        "id": deterministic_uuid("edunavika.subject.std12.biology"),
        "standard_grade": 12,
        "name": "Biology",
        "code": "BIO12",
        "description": "Class 12 Biology (Reproduction, Genetics & Evolution, Biotechnology, Ecology). Relevant for NEET.",
        "is_active": True,
    },
]

# 4. Canonical Exam-to-Subject Mappings (Zero-Duplication Cross-Linking)
CANONICAL_EXAM_SUBJECT_LINKS = [
    # JEE Main: Physics (11, 12), Chemistry (11, 12), Mathematics (11, 12)
    {"exam_code": "JEE_MAIN", "subject_code": "PHYS11", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_MAIN", "subject_code": "CHEM11", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_MAIN", "subject_code": "MATH11", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_MAIN", "subject_code": "PHYS12", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_MAIN", "subject_code": "CHEM12", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_MAIN", "subject_code": "MATH12", "role": "CORE_MANDATORY"},

    # JEE Advanced: Physics (11, 12), Chemistry (11, 12), Mathematics (11, 12)
    {"exam_code": "JEE_ADVANCED", "subject_code": "PHYS11", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_ADVANCED", "subject_code": "CHEM11", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_ADVANCED", "subject_code": "MATH11", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_ADVANCED", "subject_code": "PHYS12", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_ADVANCED", "subject_code": "CHEM12", "role": "CORE_MANDATORY"},
    {"exam_code": "JEE_ADVANCED", "subject_code": "MATH12", "role": "CORE_MANDATORY"},

    # NEET UG: Physics (11, 12), Chemistry (11, 12), Biology (11, 12)
    {"exam_code": "NEET_UG", "subject_code": "PHYS11", "role": "CORE_MANDATORY"},
    {"exam_code": "NEET_UG", "subject_code": "CHEM11", "role": "CORE_MANDATORY"},
    {"exam_code": "NEET_UG", "subject_code": "BIO11", "role": "CORE_MANDATORY"},
    {"exam_code": "NEET_UG", "subject_code": "PHYS12", "role": "CORE_MANDATORY"},
    {"exam_code": "NEET_UG", "subject_code": "CHEM12", "role": "CORE_MANDATORY"},
    {"exam_code": "NEET_UG", "subject_code": "BIO12", "role": "CORE_MANDATORY"},
]


def seed_canonical_curriculum(db_session: Session, dry_run: bool = False) -> Dict[str, Any]:
    """
    Executes idempotent seeding of examinations, standards, subjects, and exam_subjects.
    Returns metrics on created, already-existing, and skipped records.
    """
    report = {
        "dry_run": dry_run,
        "created": {"examinations": 0, "standards": 0, "subjects": 0, "exam_subjects": 0},
        "already_existing": {"examinations": 0, "standards": 0, "subjects": 0, "exam_subjects": 0},
        "details": [],
    }

    raw_conn = db_session.connection()

    # --- Step 1: Seed Examinations ---
    for exam in CANONICAL_EXAMINATIONS:
        existing = db_session.query(Examination).filter(Examination.code == exam["code"]).first()

        if existing:
            report["already_existing"]["examinations"] += 1
            report["details"].append(f"Examination '{exam['code']}' already exists.")
        else:
            if not dry_run:
                new_exam = Examination(
                    code=exam["code"],
                    name=exam["name"],
                    conducting_body=exam["conducting_body"],
                    description=exam["description"],
                    is_active=exam["is_active"],
                )
                db_session.add(new_exam)
                db_session.flush()
            report["created"]["examinations"] += 1
            report["details"].append(f"Created examination '{exam['code']}' ({exam['conducting_body']}).")

    # --- Step 2: Seed Standards ---
    standard_id_map: Dict[int, str] = {}
    for std_data in CANONICAL_STANDARDS:
        existing = db_session.query(Standard).filter(Standard.grade_number == std_data["grade_number"]).first()
        if existing:
            standard_id_map[std_data["grade_number"]] = existing.id
            report["already_existing"]["standards"] += 1
            report["details"].append(f"Standard {std_data['grade_number']} already exists (ID: {existing.id}).")
        else:
            if not dry_run:
                new_std = Standard(
                    id=std_data["id"],
                    grade_number=std_data["grade_number"],
                    name=std_data["name"],
                    description=std_data["description"],
                    is_active=std_data["is_active"],
                )
                db_session.add(new_std)
                db_session.flush()
                standard_id_map[std_data["grade_number"]] = new_std.id
            else:
                standard_id_map[std_data["grade_number"]] = std_data["id"]
            report["created"]["standards"] += 1
            report["details"].append(f"Created Standard {std_data['grade_number']} ('{std_data['name']}').")

    # --- Step 3: Seed Subjects ---
    subject_code_to_id: Dict[str, str] = {}
    for subj_data in CANONICAL_SUBJECTS:
        std_id = standard_id_map[subj_data["standard_grade"]]
        existing = db_session.query(Subject).filter(
            Subject.standard_id == std_id,
            Subject.code == subj_data["code"]
        ).first()

        if existing:
            subject_code_to_id[subj_data["code"]] = existing.id
            report["already_existing"]["subjects"] += 1
            report["details"].append(f"Subject '{subj_data['code']}' ({subj_data['name']}) already exists.")
        else:
            if not dry_run:
                new_subj = Subject(
                    id=subj_data["id"],
                    standard_id=std_id,
                    name=subj_data["name"],
                    code=subj_data["code"],
                    description=subj_data["description"],
                    is_active=subj_data["is_active"],
                )
                db_session.add(new_subj)
                db_session.flush()
                subject_code_to_id[subj_data["code"]] = new_subj.id
            else:
                subject_code_to_id[subj_data["code"]] = subj_data["id"]
            report["created"]["subjects"] += 1
            report["details"].append(f"Created Subject '{subj_data['code']}' ({subj_data['name']}) for Grade {subj_data['standard_grade']}.")

    # --- Step 4: Seed Exam-Subject Mappings ---
    for link in CANONICAL_EXAM_SUBJECT_LINKS:
        exam_code = link["exam_code"]
        subj_code = link["subject_code"]
        subj_id = subject_code_to_id[subj_code]

        existing = db_session.query(ExamSubject).filter(
            ExamSubject.exam_code == exam_code,
            ExamSubject.subject_id == subj_id
        ).first()

        if existing:
            report["already_existing"]["exam_subjects"] += 1
            report["details"].append(f"ExamSubject mapping ({exam_code} <-> {subj_code}) already exists.")
        else:
            link_id = deterministic_uuid(f"edunavika.exam_subject.{exam_code}.{subj_code}")
            if not dry_run:
                new_link = ExamSubject(
                    id=link_id,
                    exam_code=exam_code,
                    subject_id=subj_id,
                    curriculum_role=link["role"],
                )
                db_session.add(new_link)
                db_session.flush()
            report["created"]["exam_subjects"] += 1
            report["details"].append(f"Linked '{exam_code}' to '{subj_code}' as {link['role']}.")

    if dry_run:
        db_session.rollback()
        report["details"].append("[DRY RUN] Rolled back all changes successfully.")
    else:
        db_session.commit()
        report["details"].append("[COMMIT] Committed all changes cleanly to database.")

    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="EduNavika Canonical Curriculum Seeder (Phase B)")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without committing changes")
    parser.add_argument("--db-url", type=str, default=None, help="Override database connection URL")
    args = parser.parse_args()

    db_url = args.db_url or settings.DATABASE_URL
    print(f"--- EduNavika Canonical Curriculum Seeder ---")
    print(f"Target Database: {db_url}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE SEED'}")

    engine = create_engine(db_url, future=True)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()

    try:
        report = seed_canonical_curriculum(session, dry_run=args.dry_run)
        print("\n--- Seeding Summary ---")
        print(f"Examinations:  +{report['created']['examinations']} created, {report['already_existing']['examinations']} already existing")
        print(f"Standards:     +{report['created']['standards']} created, {report['already_existing']['standards']} already existing")
        print(f"Subjects:      +{report['created']['subjects']} created, {report['already_existing']['subjects']} already existing")
        print(f"Exam-Subjects: +{report['created']['exam_subjects']} created, {report['already_existing']['exam_subjects']} already existing")
        print("\nDetails:")
        for line in report["details"]:
            print(f"  * {line}")
    except Exception as e:
        session.rollback()
        print(f"\n[ERROR] Seeding failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()
        engine.dispose()

if __name__ == "__main__":
    main()
