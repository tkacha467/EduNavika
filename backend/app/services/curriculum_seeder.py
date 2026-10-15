"""
EduNavika — Milestone 4: Canonical Curriculum Hierarchy Seeder.
Phase E / E.2: Authoritative Class 11 & 12 Science Curriculum Seeding.

Reads data/manifests/canonical_curriculum_manifest.json and idempotently
seeds Chapter and Topic records for Physics, Chemistry, Mathematics, and Biology
under Standards 11 and 12.

Safety & Design Invariants:
1. Idempotency: Uses natural domain keys (subject_id + chapter_number for chapters,
   chapter_id + topic_order for topics) with deterministic UUIDv5 generation.
2. Conflict Protection: Enforces strict conflict_policy ("ABORT" | "WARN" | "OVERWRITE").
   Never silently overwrites existing records with mismatched titles or source references.
3. Review Filtering: By default (include_unreviewed=False), topics marked UNVERIFIED,
   NEEDS_HUMAN_REVIEW, or UNRESOLVED are quarantined and excluded from production seeding.
4. Test Isolation: Never writes to persistent DB directly unless explicitly invoked.
5. Dry Run: Completely transaction-isolated; zero mutations when dry_run=True.
6. Legacy Preservation: Standard 10 data and historical subjects are strictly untouched.
7. Constraint Verification: Respects all foreign-key and unique constraints.
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.models.curriculum_models import Standard, Subject, Chapter, Topic

logger = logging.getLogger("curriculum_seeder")

# Deterministic namespace for EduNavika canonical curriculum entities
EDUNAVIKA_DNS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

DEFAULT_MANIFEST_PATH = Path("data/manifests/canonical_curriculum_manifest.json")

SUBJECT_PREFIX_MAP = {
    "PHYS11": "PHYS",
    "PHYS12": "PHYS",
    "CHEM11": "CHEM",
    "CHEM12": "CHEM",
    "MATH11": "MATH",
    "MATH12": "MATH",
    "BIO11": "BIO",
    "BIO12": "BIO",
}


class CurriculumConflictError(Exception):
    """Raised when an existing curriculum record conflicts with manifest data under conflict_policy='ABORT'."""
    pass


def deterministic_uuid(seed_key: str) -> str:
    """Generate stable, reproducible UUIDv5 from a domain natural key."""
    return str(uuid.uuid5(EDUNAVIKA_DNS, seed_key))


class CurriculumSeedingReport:
    """Structured report tracking curriculum seeding metrics, conflicts, and validation."""

    def __init__(self, dry_run: bool = False, conflict_policy: str = "ABORT"):
        self.dry_run = dry_run
        self.conflict_policy = conflict_policy
        self.standards_inspected = 0
        self.subjects_inspected = 0
        self.chapters_created = 0
        self.chapters_existing = 0
        self.chapters_updated = 0
        self.topics_created = 0
        self.topics_existing = 0
        self.topics_updated = 0
        self.conflicts: List[Dict[str, Any]] = []
        self.quarantined_items: List[Dict[str, Any]] = []
        self.coverage_by_subject: Dict[str, Dict[str, Any]] = {}
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "conflict_policy": self.conflict_policy,
            "standards_inspected": self.standards_inspected,
            "subjects_inspected": self.subjects_inspected,
            "chapters_created": self.chapters_created,
            "chapters_existing": self.chapters_existing,
            "chapters_updated": self.chapters_updated,
            "topics_created": self.topics_created,
            "topics_existing": self.topics_existing,
            "topics_updated": self.topics_updated,
            "conflicts_count": len(self.conflicts),
            "conflicts": self.conflicts,
            "quarantined_count": len(self.quarantined_items),
            "quarantined_items": self.quarantined_items,
            "coverage_by_subject": self.coverage_by_subject,
            "errors": self.errors,
            "success": len(self.errors) == 0 and len(self.conflicts) == 0,
        }


def load_manifest(manifest_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and validate the canonical curriculum manifest."""
    resolved_path = Path(manifest_path) if manifest_path else DEFAULT_MANIFEST_PATH
    if not resolved_path.is_absolute():
        cur = Path.cwd()
        if (cur / resolved_path).exists():
            resolved_path = cur / resolved_path
        else:
            p = cur
            while p != p.parent:
                if (p / resolved_path).exists():
                    resolved_path = p / resolved_path
                    break
                p = p.parent

    if not resolved_path.exists():
        raise FileNotFoundError(f"Canonical curriculum manifest not found at: {resolved_path}")

    with open(resolved_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "standards" not in data:
        raise ValueError(f"Invalid manifest schema: missing 'standards' key in {resolved_path}")

    return data


def seed_canonical_curriculum(
    db: Session,
    manifest_path: Optional[Path] = None,
    dry_run: bool = False,
    conflict_policy: str = "ABORT",
    include_unreviewed: bool = False,
) -> Dict[str, Any]:
    """
    Idempotently seeds Chapter and Topic records from the canonical curriculum manifest.

    Args:
        db: SQLAlchemy database session.
        manifest_path: Path to canonical curriculum manifest JSON (optional).
        dry_run: If True, executes in a transaction that is rolled back; 0 writes persisted.
        conflict_policy: "ABORT" (raise on mismatched existing titles/refs and rollback),
                         "WARN" (preserve existing record without modification, log warning),
                         "OVERWRITE" (update existing record to match manifest).
        include_unreviewed: If False (default), topics with status UNVERIFIED, NEEDS_HUMAN_REVIEW,
                            or UNRESOLVED are quarantined and excluded from insertion.

    Returns:
        CurriculumSeedingReport dictionary.
    """
    if conflict_policy not in ("ABORT", "WARN", "OVERWRITE"):
        raise ValueError(f"Invalid conflict_policy: {conflict_policy}. Must be 'ABORT', 'WARN', or 'OVERWRITE'.")

    report = CurriculumSeedingReport(dry_run=dry_run, conflict_policy=conflict_policy)
    manifest = load_manifest(manifest_path)

    try:
        for std_entry in manifest["standards"]:
            grade_number = std_entry.get("grade_number")
            if grade_number not in (11, 12):
                logger.warning("Skipping non-target standard grade: %s", grade_number)
                continue

            report.standards_inspected += 1

            # Lookup standard in DB
            standard = db.query(Standard).filter(Standard.grade_number == grade_number).first()
            if not standard:
                err = f"Standard with grade_number={grade_number} does not exist in database."
                report.errors.append(err)
                continue

            for subj_entry in std_entry.get("subjects", []):
                subj_code = subj_entry.get("code")
                subj_name = subj_entry.get("name")
                applicable_exams = subj_entry.get("applicable_exams", [])
                prefix = SUBJECT_PREFIX_MAP.get(subj_code, subj_code[:4])

                # Lookup subject under this standard
                subject = db.query(Subject).filter(
                    Subject.standard_id == standard.id,
                    Subject.code == subj_code
                ).first()

                if not subject:
                    err = f"Subject code={subj_code} for standard grade={grade_number} not found in database."
                    report.errors.append(err)
                    continue

                report.subjects_inspected += 1
                subj_stat = {
                    "standard": grade_number,
                    "code": subj_code,
                    "name": subj_name,
                    "applicable_exams": applicable_exams,
                    "chapters_count": 0,
                    "topics_count": 0,
                }

                # Process Chapters
                for ch_entry in subj_entry.get("chapters", []):
                    ch_num = ch_entry.get("chapter_number")
                    ch_title = ch_entry.get("canonical_title") or ch_entry.get("title")
                    ch_ref = ch_entry.get("source_reference", "")
                    canonical_id = ch_entry.get("canonical_id") or f"STD{grade_number}-{prefix}-CH{ch_num:02d}"
                    mapping_status = ch_entry.get("mapping_status", "VERIFIED_PRIMARY_SOURCE")

                    # Validation: check for missing or invalid chapter fields
                    if not ch_num or ch_num < 1 or not ch_title:
                        report.quarantined_items.append({
                            "type": "chapter",
                            "subject": subj_code,
                            "entry": ch_entry,
                            "reason": "Missing or invalid chapter_number or title",
                        })
                        continue

                    if mapping_status in ("UNRESOLVED", "AMBIGUOUS", "QUARANTINED") or (
                        not include_unreviewed and mapping_status in ("UNVERIFIED", "NEEDS_HUMAN_REVIEW")
                    ):
                        report.quarantined_items.append({
                            "type": "chapter",
                            "subject": subj_code,
                            "entry": ch_entry,
                            "reason": f"Chapter status marked as {mapping_status} (excluded from production seeding)",
                        })
                        continue

                    # Lookup existing chapter by (subject_id, chapter_number)
                    existing_ch = db.query(Chapter).filter(
                        Chapter.subject_id == subject.id,
                        Chapter.chapter_number == ch_num
                    ).first()

                    if existing_ch:
                        # Check for conflict
                        title_mismatch = (existing_ch.title != ch_title)
                        ref_mismatch = (existing_ch.source_reference != ch_ref and ch_ref != "")

                        if title_mismatch or ref_mismatch:
                            conflict_data = {
                                "type": "chapter",
                                "id": existing_ch.id,
                                "subject": subj_code,
                                "chapter_number": ch_num,
                                "existing_title": existing_ch.title,
                                "manifest_title": ch_title,
                                "existing_source_reference": existing_ch.source_reference,
                                "manifest_source_reference": ch_ref,
                            }
                            report.conflicts.append(conflict_data)

                            if conflict_policy == "ABORT":
                                raise CurriculumConflictError(
                                    f"Conflict on chapter {subj_code} #{ch_num}: "
                                    f"existing title='{existing_ch.title}' vs manifest='{ch_title}'"
                                )
                            elif conflict_policy == "WARN":
                                logger.warning("Chapter conflict (WARN: preserving DB record): %s", conflict_data)
                                report.chapters_existing += 1
                                ch_record = existing_ch
                            elif conflict_policy == "OVERWRITE":
                                if not dry_run:
                                    existing_ch.title = ch_title
                                    existing_ch.source_reference = ch_ref
                                    existing_ch.is_active = True
                                report.chapters_updated += 1
                                ch_record = existing_ch
                        else:
                            report.chapters_existing += 1
                            ch_record = existing_ch
                    else:
                        report.chapters_created += 1
                        ch_id = deterministic_uuid(f"edunavika.chapter.{canonical_id}")
                        ch_record = Chapter(
                            id=ch_id,
                            subject_id=subject.id,
                            chapter_number=ch_num,
                            title=ch_title,
                            source_reference=ch_ref,
                            is_active=True,
                        )
                        if not dry_run:
                            db.add(ch_record)
                            db.flush()

                    subj_stat["chapters_count"] += 1

                    # Process Topics
                    for top_entry in ch_entry.get("topics", []):
                        if isinstance(top_entry, str):
                            top_title = top_entry
                            top_order = None
                            top_canonical_id = None
                            top_status = "VERIFIED_PRIMARY_SOURCE"
                            top_section = ""
                        else:
                            top_title = top_entry.get("title")
                            top_order = top_entry.get("topic_order")
                            top_canonical_id = top_entry.get("canonical_id")
                            top_status = top_entry.get("mapping_status") or top_entry.get("exam_verification_status", "VERIFIED_PRIMARY_SOURCE")
                            top_section = top_entry.get("source_section", "")

                        # Validation: check for valid topic fields
                        if not top_title or top_title.strip() == "":
                            report.quarantined_items.append({
                                "type": "topic",
                                "subject": subj_code,
                                "chapter": ch_num,
                                "entry": top_entry,
                                "reason": "Empty or missing topic title",
                            })
                            continue

                        if top_order is None or top_order < 1:
                            report.quarantined_items.append({
                                "type": "topic",
                                "subject": subj_code,
                                "chapter": ch_num,
                                "entry": top_entry,
                                "reason": "Invalid or missing topic_order",
                            })
                            continue

                        # Unreviewed/Ambiguity Quarantine
                        if top_status in ("UNRESOLVED", "AMBIGUOUS", "QUARANTINED") or (
                            not include_unreviewed and top_status in ("UNVERIFIED", "NEEDS_HUMAN_REVIEW")
                        ):
                            report.quarantined_items.append({
                                "type": "topic",
                                "canonical_id": top_canonical_id,
                                "subject": subj_code,
                                "chapter": ch_num,
                                "title": top_title,
                                "reason": f"Topic status marked as {top_status} (excluded from production seeding)",
                            })
                            continue

                        if not top_canonical_id:
                            top_canonical_id = f"{canonical_id}-T{top_order:02d}"

                        # Check existing topic in DB
                        existing_top = None
                        if ch_record.id:
                            existing_top = db.query(Topic).filter(
                                Topic.chapter_id == ch_record.id,
                                Topic.topic_order == top_order
                            ).first()

                        if existing_top:
                            title_mismatch = (existing_top.title != top_title)
                            desc_mismatch = (existing_top.description != top_section and top_section != "")

                            if title_mismatch or desc_mismatch:
                                conflict_data = {
                                    "type": "topic",
                                    "id": existing_top.id,
                                    "chapter_id": ch_record.id,
                                    "topic_order": top_order,
                                    "existing_title": existing_top.title,
                                    "manifest_title": top_title,
                                }
                                report.conflicts.append(conflict_data)

                                if conflict_policy == "ABORT":
                                    raise CurriculumConflictError(
                                        f"Conflict on topic ch #{ch_num} topic #{top_order}: "
                                        f"existing title='{existing_top.title}' vs manifest='{top_title}'"
                                    )
                                elif conflict_policy == "WARN":
                                    logger.warning("Topic conflict (WARN: preserving DB record): %s", conflict_data)
                                    report.topics_existing += 1
                                elif conflict_policy == "OVERWRITE":
                                    if not dry_run:
                                        existing_top.title = top_title
                                        existing_top.description = top_section
                                        existing_top.is_active = True
                                    report.topics_updated += 1
                            else:
                                report.topics_existing += 1
                        else:
                            report.topics_created += 1
                            top_id = deterministic_uuid(f"edunavika.topic.{top_canonical_id}")
                            new_topic = Topic(
                                id=top_id,
                                chapter_id=ch_record.id,
                                topic_order=top_order,
                                title=top_title,
                                description=top_section,
                                is_active=True,
                            )
                            if not dry_run:
                                db.add(new_topic)
                                db.flush()

                        subj_stat["topics_count"] += 1

                report.coverage_by_subject[subj_code] = subj_stat

        if dry_run:
            db.rollback()
        else:
            db.commit()

    except CurriculumConflictError as cfe:
        db.rollback()
        logger.warning("Seeder aborted due to curriculum conflict: %s", cfe)
        report.errors.append(str(cfe))
    except Exception as e:
        db.rollback()
        logger.exception("Error executing curriculum seeder: %s", e)
        report.errors.append(str(e))

    return report.to_dict()
