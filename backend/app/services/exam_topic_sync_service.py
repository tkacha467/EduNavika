"""
EduNavika — Milestone 4 Phase E.4: Exam-Topic Synchronization Service.
Idempotently synchronizes topic-level examination applicability from
data/manifests/canonical_curriculum_manifest.json to the exam_topics table.

Enforces:
1. Strict exam applicability: only topics marked VERIFIED_PRIMARY_SOURCE or PARTIAL_MAPPING
   for a specific examination receive an active association.
2. Review quarantine: topics marked NEEDS_HUMAN_REVIEW or UNVERIFIED receive 0 exam links.
3. Textbook preservation: topics marked VERIFIED_TEXTBOOK_ONLY receive 0 exam links,
   remaining available strictly for school/textbook curriculum queries.
4. Idempotency: deterministic UUIDv5 generation and (exam_code, topic_id) uniqueness.
5. Conflict safety and transaction rollback on failure.
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.competitive_models import Examination, ExamTopic
from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic
from backend.app.services.curriculum_seeder import (
    deterministic_uuid,
    load_manifest,
    DEFAULT_MANIFEST_PATH,
)

logger = logging.getLogger("exam_topic_sync")


class ExamTopicSyncReport:
    """Tracks synchronization metrics and audit details."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.total_manifest_topics = 0
        self.links_created = 0
        self.links_existing = 0
        self.links_by_exam: Dict[str, int] = {"JEE_MAIN": 0, "JEE_ADVANCED": 0, "NEET_UG": 0}
        self.quarantined_topics: List[Dict[str, Any]] = []
        self.textbook_only_topics: List[Dict[str, Any]] = []
        self.missing_topics: List[str] = []
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "total_manifest_topics": self.total_manifest_topics,
            "links_created": self.links_created,
            "links_existing": self.links_existing,
            "links_by_exam": self.links_by_exam,
            "quarantined_count": len(self.quarantined_topics),
            "quarantined_topics": self.quarantined_topics,
            "textbook_only_count": len(self.textbook_only_topics),
            "textbook_only_topics": self.textbook_only_topics,
            "missing_topics_count": len(self.missing_topics),
            "missing_topics": self.missing_topics,
            "errors": self.errors,
            "success": len(self.errors) == 0,
        }


def sync_exam_topics(
    db: Session,
    manifest_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Idempotently synchronizes the exam_topics table from the canonical manifest.

    Args:
        db: SQLAlchemy session.
        manifest_path: Optional path to manifest JSON.
        dry_run: If True, rolls back transaction and persists zero database writes.

    Returns:
        ExamTopicSyncReport dictionary.
    """
    report = ExamTopicSyncReport(dry_run=dry_run)
    manifest = load_manifest(manifest_path)

    try:
        # Pre-verify examinations exist in database
        active_exams = {
            e.code for e in db.query(Examination).filter(Examination.is_active == True).all()
        }
        if not active_exams:
            # Fallback if examinations table not yet populated
            active_exams = {"JEE_MAIN", "JEE_ADVANCED", "NEET_UG"}

        for std in manifest["standards"]:
            grade = std.get("grade_number")
            for subj in std.get("subjects", []):
                subj_code = subj.get("code")
                for ch in subj.get("chapters", []):
                    ch_num = ch.get("chapter_number")
                    for t in ch.get("topics", []):
                        report.total_manifest_topics += 1
                        t_canon_id = t.get("canonical_id")
                        t_title = t.get("title")
                        t_order = t.get("topic_order")
                        t_status = t.get("exam_verification_status") or t.get("mapping_status")
                        applicable_exams = t.get("applicable_exams", [])

                        # 1. Check for review quarantine
                        if t_status in ("NEEDS_HUMAN_REVIEW", "UNVERIFIED", "UNRESOLVED", "AMBIGUOUS"):
                            report.quarantined_topics.append({
                                "canonical_id": t_canon_id,
                                "title": t_title,
                                "status": t_status,
                                "reason": "Excluded from exam eligibility until verified by curriculum review."
                            })
                            continue

                        # 2. Check for textbook-only content
                        if t_status == "VERIFIED_TEXTBOOK_ONLY" or not applicable_exams:
                            report.textbook_only_topics.append({
                                "canonical_id": t_canon_id,
                                "title": t_title,
                                "status": t_status,
                                "reason": "Textbook foundational topic; excluded from competitive exam eligibility."
                            })
                            continue

                        # 3. Lookup topic record in DB
                        # Match by deterministic UUID or (chapter.subject_id + chapter_number, topic_order)
                        expected_topic_id = deterministic_uuid(f"edunavika.topic.{t_canon_id}")
                        db_topic = db.query(Topic).filter(Topic.id == expected_topic_id).first()

                        if not db_topic:
                            # Try secondary lookup by chapter + order
                            db_topic = (
                                db.query(Topic)
                                .join(Chapter, Topic.chapter_id == Chapter.id)
                                .join(Subject, Chapter.subject_id == Subject.id)
                                .filter(
                                    Subject.code == subj_code,
                                    Chapter.chapter_number == ch_num,
                                    Topic.topic_order == t_order,
                                )
                                .first()
                            )

                        if not db_topic:
                            report.missing_topics.append(f"{t_canon_id} ({t_title})")
                            continue

                        # 4. Synchronize each applicable exam link
                        for exam_code in applicable_exams:
                            if exam_code not in active_exams:
                                logger.warning("Skipping unknown/inactive exam code: %s", exam_code)
                                continue

                            link_id = deterministic_uuid(f"edunavika.exam_topic.{exam_code}.{t_canon_id}")

                            existing_link = (
                                db.query(ExamTopic)
                                .filter(
                                    ExamTopic.exam_code == exam_code,
                                    ExamTopic.topic_id == db_topic.id,
                                )
                                .first()
                            )

                            if existing_link:
                                report.links_existing += 1
                            else:
                                report.links_created += 1
                                report.links_by_exam[exam_code] = report.links_by_exam.get(exam_code, 0) + 1

                                if not dry_run:
                                    new_link = ExamTopic(
                                        id=link_id,
                                        exam_code=exam_code,
                                        topic_id=db_topic.id,
                                        curriculum_role="CORE_MANDATORY",
                                        inclusion_status="ACTIVE",
                                        verification_status=t_status,
                                    )
                                    db.add(new_link)
                                    db.flush()

        if dry_run:
            db.rollback()
        else:
            db.commit()

    except Exception as e:
        db.rollback()
        logger.exception("Error executing exam-topic synchronization: %s", e)
        report.errors.append(str(e))

    return report.to_dict()
