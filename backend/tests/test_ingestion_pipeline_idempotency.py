import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.models.curriculum import Standard, Subject, Chapter, Topic
from backend.app.models.content import LearningContent
from backend.app.ingestion.mapper import DatabaseCurriculumMapper
from backend.app.ingestion.schemas import (
    DocumentIdentity,
    ChapterCandidate,
    TopicCandidate,
    ContentChunk,
    StructureConfidence,
    DetectionSource,
)


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


def test_mapper_idempotency_and_provenance(memory_db):
    mapper = DatabaseCurriculumMapper(memory_db)

    doc_id = DocumentIdentity(
        document_id="doc_idempotency_test",
        relative_path="STD-10th/science.pdf",
        filename="science.pdf",
        file_hash="1" * 64,
        file_size_bytes=2048,
        standard=10,
        subject="Science",
    )

    topic_cand = TopicCandidate(
        topic_order=1,
        topic_title="Chemical Equations",
        start_pdf_page=14,
        end_pdf_page=16,
        confidence=StructureConfidence.CONFIDENT,
        detection_method=DetectionSource.HEADING,
    )

    chapter_cand = ChapterCandidate(
        chapter_number=1,
        chapter_title="Chemical Reactions and Equations",
        start_pdf_page=14,
        end_pdf_page=30,
        confidence=StructureConfidence.CONFIDENT,
        detection_method=DetectionSource.HEADING,
        topics=[topic_cand],
    )

    chunk = ContentChunk(
        chunk_id="chk_deterministic_001",
        document_id=doc_id.document_id,
        pdf_page_start=14,
        pdf_page_end=16,
        source_file=doc_id.relative_path,
        content_type="TEXT",
        chunk_index=1,
        text="A complete chemical equation represents the reactants, products and their physical states symbolically.",
        approx_token_count=18,
        heading_path="Standard 10 > Science > Chapter 1 > Chemical Equations",
        section_title="Chemical Equations",
        metadata={
            "chapter_number": 1,
            "topic_order": 1,
        },
    )

    # First run
    inserted_1, skipped_1 = mapper.persist_chunks(doc_id, [chapter_cand], [chunk])
    assert inserted_1 == 1
    assert skipped_1 == 0

    count_standard_1 = memory_db.query(Standard).count()
    count_subject_1 = memory_db.query(Subject).count()
    count_chapter_1 = memory_db.query(Chapter).count()
    count_topic_1 = memory_db.query(Topic).count()
    count_content_1 = memory_db.query(LearningContent).count()

    assert count_standard_1 == 1
    assert count_subject_1 == 1
    assert count_chapter_1 == 1
    assert count_topic_1 == 1
    assert count_content_1 == 1

    # Verify provenance on the inserted LearningContent
    content_record = memory_db.query(LearningContent).first()
    assert content_record.chunk_identifier == "chk_deterministic_001"
    assert content_record.source_document == "STD-10th/science.pdf"
    assert content_record.source_page == 14
    assert content_record.topic_id is not None
    assert content_record.content_metadata["heading_path"] == "Standard 10 > Science > Chapter 1 > Chemical Equations"

    # Second run (Idempotency test)
    inserted_2, skipped_2 = mapper.persist_chunks(doc_id, [chapter_cand], [chunk])
    assert inserted_2 == 0
    assert skipped_2 == 1

    # Counts must NOT increase
    assert memory_db.query(Standard).count() == count_standard_1
    assert memory_db.query(Subject).count() == count_subject_1
    assert memory_db.query(Chapter).count() == count_chapter_1
    assert memory_db.query(Topic).count() == count_topic_1
    assert memory_db.query(LearningContent).count() == count_content_1
