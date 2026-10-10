"""
Curriculum Package Distribution Service for EduNavika.
Implements School LAN Offline-First Curriculum Distribution (Problem Statement 06, Section 4).
Allows school-local servers to export versioned, tamper-proof curriculum bundles with SHA-256 checksums,
and enables student low-resource devices to verify and import them without internet connectivity.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from backend.app.models import Standard, Subject, Chapter, Topic, LearningContent
from backend.app.domain.enums import ContentType

logger = logging.getLogger("curriculum_package")


class CurriculumPackageService:
    @staticmethod
    def calculate_checksum(data: Any) -> str:
        """Computes deterministic SHA-256 checksum for arbitrary JSON-serializable data."""
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    @classmethod
    def export_package(cls, db: Session, grade: int = 10) -> Dict[str, Any]:
        """
        Exports a complete Standard 10 GSEB curriculum package suitable for LAN distribution.
        Includes full manifest and cryptographic checksum.
        """
        standard = db.query(Standard).filter(Standard.grade_number == grade, Standard.is_active == True).first()
        if not standard:
            raise ValueError(f"Standard {grade} not found in database.")

        subjects = db.query(Subject).filter(Subject.standard_id == standard.id, Subject.is_active == True).all()
        subjects_data = []
        total_chapters = 0
        total_topics = 0
        total_contents = 0

        for subj in subjects:
            chapters = db.query(Chapter).filter(Chapter.subject_id == subj.id, Chapter.is_active == True).all()
            chapters_data = []

            for chap in chapters:
                topics = db.query(Topic).filter(Topic.chapter_id == chap.id, Topic.is_active == True).all()
                topics_data = []

                for top in topics:
                    contents = db.query(LearningContent).filter(LearningContent.topic_id == top.id).all()
                    contents_data = [
                        {
                            "id": c.id,
                            "title": c.title,
                            "content_type": c.content_type.value if hasattr(c.content_type, "value") else str(c.content_type),
                            "content_text": c.content_text,
                            "source_document": c.source_document,
                            "source_page": c.source_page,
                            "source_reference": c.source_reference,
                            "chunk_identifier": c.chunk_identifier,
                        }
                        for c in contents
                    ]
                    total_contents += len(contents_data)

                    topics_data.append({
                        "id": top.id,
                        "title": top.title,
                        "topic_order": top.topic_order,
                        "description": top.description,
                        "contents": contents_data,
                    })

                total_topics += len(topics_data)
                chapters_data.append({
                    "id": chap.id,
                    "title": chap.title,
                    "chapter_number": chap.chapter_number,
                    "description": chap.description,
                    "topics": topics_data,
                })

            total_chapters += len(chapters_data)
            subjects_data.append({
                "id": subj.id,
                "name": subj.name,
                "code": subj.code,
                "chapters": chapters_data,
            })

        payload = {
            "standard": {
                "id": standard.id,
                "grade_number": standard.grade_number,
                "name": standard.name,
                "description": standard.description,
            },
            "subjects": subjects_data,
        }

        checksum = cls.calculate_checksum(payload)

        manifest = {
            "package_id": f"pkg-gseb-{grade}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "standard_grade": grade,
            "standard_name": standard.name,
            "total_subjects": len(subjects_data),
            "total_chapters": total_chapters,
            "total_topics": total_topics,
            "total_contents": total_contents,
            "checksum": checksum,
            "checksum_algorithm": "SHA-256",
        }

        return {
            "manifest": manifest,
            "payload": payload,
        }

    @classmethod
    def import_package(cls, db: Session, package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates package integrity via SHA-256 and idempotently installs curriculum data into SQLite.
        Rejects tampered packages with mismatched checksums.
        """
        manifest = package.get("manifest") or {}
        payload = package.get("payload") or {}

        if not manifest or not payload:
            raise ValueError("Invalid curriculum package: Missing manifest or payload.")

        expected_checksum = manifest.get("checksum")
        if not expected_checksum:
            raise ValueError("Invalid curriculum package: Missing package checksum.")

        actual_checksum = cls.calculate_checksum(payload)
        if actual_checksum != expected_checksum:
            logger.error("[PACKAGE_IMPORT] Checksum mismatch: expected %s, got %s", expected_checksum, actual_checksum)
            raise ValueError(
                f"Curriculum package integrity check failed (SHA-256 mismatch). "
                f"Package may be corrupt or tampered."
            )

        # Idempotently insert / update curriculum hierarchy
        std_data = payload.get("standard") or {}
        std_grade = std_data.get("grade_number", 10)

        standard = db.query(Standard).filter(Standard.grade_number == std_grade).first()
        if not standard:
            standard = Standard(
                id=std_data.get("id"),
                grade_number=std_grade,
                name=std_data.get("name", f"Standard {std_grade}"),
                description=std_data.get("description"),
                is_active=True,
            )
            db.add(standard)
            db.flush()

        imported_subjects = 0
        imported_chapters = 0
        imported_topics = 0
        imported_contents = 0

        for s_data in payload.get("subjects", []):
            subj = db.query(Subject).filter(
                (Subject.id == s_data["id"]) | ((Subject.standard_id == standard.id) & (Subject.code == s_data["code"]))
            ).first()
            if not subj:
                subj = Subject(
                    id=s_data["id"],
                    standard_id=standard.id,
                    name=s_data["name"],
                    code=s_data["code"],
                    is_active=True,
                )
                db.add(subj)
                db.flush()
                imported_subjects += 1

            for c_data in s_data.get("chapters", []):
                chap = db.query(Chapter).filter(
                    (Chapter.id == c_data["id"]) | ((Chapter.subject_id == subj.id) & (Chapter.chapter_number == c_data["chapter_number"]))
                ).first()
                if not chap:
                    chap = Chapter(
                        id=c_data["id"],
                        subject_id=subj.id,
                        title=c_data["title"],
                        chapter_number=c_data["chapter_number"],
                        description=c_data.get("description"),
                        is_active=True,
                    )
                    db.add(chap)
                    db.flush()
                    imported_chapters += 1

                for t_data in c_data.get("topics", []):
                    top = db.query(Topic).filter(
                        (Topic.id == t_data["id"]) | ((Topic.chapter_id == chap.id) & (Topic.topic_order == t_data["topic_order"]))
                    ).first()
                    if not top:
                        top = Topic(
                            id=t_data["id"],
                            chapter_id=chap.id,
                            title=t_data["title"],
                            topic_order=t_data["topic_order"],
                            description=t_data.get("description"),
                            is_active=True,
                        )
                        db.add(top)
                        db.flush()
                        imported_topics += 1

                    for cont_data in t_data.get("contents", []):
                        cont = db.query(LearningContent).filter(LearningContent.id == cont_data["id"]).first()
                        if not cont:
                            # Parse content type
                            ctype_str = cont_data.get("content_type", "TEXT")
                            try:
                                ctype = ContentType[ctype_str]
                            except (KeyError, ValueError):
                                ctype = ContentType.TEXT

                            cont = LearningContent(
                                id=cont_data["id"],
                                topic_id=top.id,
                                title=cont_data["title"],
                                content_type=ctype,
                                content_text=cont_data["content_text"],
                                source_document=cont_data.get("source_document"),
                                source_page=cont_data.get("source_page"),
                                source_reference=cont_data.get("source_reference"),
                                chunk_identifier=cont_data.get("chunk_identifier"),
                            )
                            db.add(cont)
                            imported_contents += 1

        db.commit()

        logger.info(
            "[PACKAGE_IMPORT] Successfully imported curriculum package %s. Subjects: %d, Chapters: %d, Topics: %d, Chunks: %d",
            manifest.get("package_id"), imported_subjects, imported_chapters, imported_topics, imported_contents
        )

        return {
            "status": "SUCCESS",
            "package_id": manifest.get("package_id"),
            "standard_grade": std_grade,
            "imported_subjects": imported_subjects,
            "imported_chapters": imported_chapters,
            "imported_topics": imported_topics,
            "imported_contents": imported_contents,
            "checksum_verified": True,
            "checksum": expected_checksum,
        }
