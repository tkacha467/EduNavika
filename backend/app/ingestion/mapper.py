import uuid
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.models import Standard, Subject, Chapter, Topic
from backend.app.models import LearningContent, ContentType
from backend.app.ingestion.schemas import (
    DocumentIdentity,
    ChapterCandidate,
    ContentChunk,
)


class DatabaseCurriculumMapper:
    """
    Maps validated chunks and structural candidates into the authoritative
    SQLAlchemy database hierarchy:
    Standard -> Subject -> Chapter -> Topic -> LearningContent

    IDEMPOTENCY GUARANTEES:
    - Queries for existing records by unique constraints before inserting.
    - Matches LearningContent by chunk_identifier to ensure re-running ingestion
      never creates duplicate curriculum or content records.
    - Populates complete provenance fields on every LearningContent record.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_or_create_standard(self, grade_number: int) -> Standard:
        standard = self.db.query(Standard).filter(Standard.grade_number == grade_number).first()
        if not standard:
            standard = Standard(
                grade_number=grade_number,
                name=f"Standard {grade_number}",
                description=f"Gujarat Secondary and Higher Secondary Education Board (GSEB) Class {grade_number}",
                is_active=True,
            )
            self.db.add(standard)
            self.db.flush()
        return standard

    def get_or_create_subject(self, standard_id: str, subject_name: str) -> Subject:
        code = subject_name.lower().replace(" ", "_").replace("&", "and")[:50]
        subject = (
            self.db.query(Subject)
            .filter(Subject.standard_id == standard_id, Subject.code == code)
            .first()
        )
        if not subject:
            subject = Subject(
                standard_id=standard_id,
                name=subject_name,
                code=code,
                description=f"GSEB {subject_name}",
                is_active=True,
            )
            self.db.add(subject)
            self.db.flush()
        return subject

    def get_or_create_chapter(
        self,
        subject_id: str,
        chapter_candidate: ChapterCandidate,
        doc_identity: DocumentIdentity,
    ) -> Chapter:
        chapter = (
            self.db.query(Chapter)
            .filter(
                Chapter.subject_id == subject_id,
                Chapter.chapter_number == chapter_candidate.chapter_number,
            )
            .first()
        )
        if not chapter:
            chapter = Chapter(
                subject_id=subject_id,
                chapter_number=chapter_candidate.chapter_number,
                title=chapter_candidate.chapter_title,
                description=f"Chapter {chapter_candidate.chapter_number}: {chapter_candidate.chapter_title}",
                source_reference=f"PDF: {doc_identity.filename} (pp. {chapter_candidate.start_pdf_page}-{chapter_candidate.end_pdf_page})",
                is_active=True,
            )
            self.db.add(chapter)
            self.db.flush()
        return chapter

    def get_or_create_topic(
        self,
        chapter_id: str,
        topic_order: int,
        topic_title: str,
        doc_identity: DocumentIdentity,
        start_page: int,
        end_page: int,
    ) -> Topic:
        topic = (
            self.db.query(Topic)
            .filter(
                Topic.chapter_id == chapter_id,
                Topic.topic_order == topic_order,
            )
            .first()
        )
        if not topic:
            topic = Topic(
                chapter_id=chapter_id,
                topic_order=topic_order,
                title=topic_title,
                description=f"Topic {topic_order}: {topic_title}",
                learning_objectives=f"GSEB curriculum objectives for {topic_title}",
                is_active=True,
            )
            self.db.add(topic)
            self.db.flush()
        return topic

    def persist_chunks(
        self,
        doc_identity: DocumentIdentity,
        chapters: List[ChapterCandidate],
        chunks: List[ContentChunk],
    ) -> Tuple[int, int]:
        """
        Persists curriculum hierarchy and content chunks idempotently.
        Returns: (inserted_count, skipped_duplicate_count)
        """
        # 1. Ensure Standard
        standard = self.get_or_create_standard(doc_identity.standard)

        # 2. Ensure Subject
        subject = self.get_or_create_subject(standard.id, doc_identity.subject)

        # 3. Create/lookup Chapter and Topic maps
        chapter_models: Dict[int, Chapter] = {}
        topic_models: Dict[Tuple[int, int], Topic] = {}

        for ch_cand in chapters:
            ch_model = self.get_or_create_chapter(subject.id, ch_cand, doc_identity)
            chapter_models[ch_cand.chapter_number] = ch_model

            for top_cand in ch_cand.topics:
                top_model = self.get_or_create_topic(
                    chapter_id=ch_model.id,
                    topic_order=top_cand.topic_order,
                    topic_title=top_cand.topic_title,
                    doc_identity=doc_identity,
                    start_page=top_cand.start_pdf_page,
                    end_page=top_cand.end_pdf_page,
                )
                topic_models[(ch_cand.chapter_number, top_cand.topic_order)] = top_model

        # 4. Insert chunks idempotently
        inserted_count = 0
        skipped_count = 0

        # Pre-fetch existing chunk identifiers for this document to avoid N+1 queries
        existing_chunk_ids = set(
            row[0]
            for row in self.db.query(LearningContent.chunk_identifier)
            .filter(LearningContent.source_document == doc_identity.relative_path)
            .all()
        )

        for chunk in chunks:
            if chunk.chunk_id in existing_chunk_ids:
                skipped_count += 1
                continue

            ch_num = chunk.metadata.get("chapter_number", 1)
            top_order = chunk.metadata.get("topic_order", 1)
            topic_model = topic_models.get((ch_num, top_order))

            if not topic_model:
                # Fallback to first topic in chapter or first topic overall
                first_ch = list(chapter_models.values())[0] if chapter_models else None
                if first_ch:
                    topic_model = self.get_or_create_topic(first_ch.id, 1, "General Content", doc_identity, 1, 1)
                else:
                    skipped_count += 1
                    continue

            content_type_enum = ContentType.TEXT
            try:
                content_type_enum = ContentType[chunk.content_type]
            except KeyError:
                content_type_enum = ContentType.TEXT

            content_record = LearningContent(
                topic_id=topic_model.id,
                content_type=content_type_enum,
                title=chunk.section_title or f"Chunk {chunk.chunk_index}",
                content_text=chunk.text,
                source_document=doc_identity.relative_path,
                source_page=chunk.pdf_page_start,
                source_reference=f"{doc_identity.filename} (PDF pp. {chunk.pdf_page_start}-{chunk.pdf_page_end})",
                chunk_identifier=chunk.chunk_id,
                content_metadata={
                    "approx_token_count": chunk.approx_token_count,
                    "heading_path": chunk.heading_path,
                    "pdf_page_start": chunk.pdf_page_start,
                    "pdf_page_end": chunk.pdf_page_end,
                    "printed_page_start": chunk.printed_page_start,
                    "printed_page_end": chunk.printed_page_end,
                    "chunk_index": chunk.chunk_index,
                    "document_id": doc_identity.document_id,
                    "file_hash": doc_identity.file_hash,
                },
            )
            self.db.add(content_record)
            existing_chunk_ids.add(chunk.chunk_id)
            inserted_count += 1

        self.db.commit()
        return inserted_count, skipped_count
