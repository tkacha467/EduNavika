import pytest
from pathlib import Path
from backend.app.ingestion.chunk_auditor import BM25Index, ChunkAuditor
from backend.app.ingestion.provenance_auditor import ProvenanceAuditor


def test_bm25_index_exact_match():
    corpus = [
        {"id": "doc1", "text": "Euclid's division lemma states that for given positive integers a and b there exist unique integers q and r satisfying a = bq + r."},
        {"id": "doc2", "text": "Photosynthesis is the process by which green plants make their food using carbon dioxide and water in presence of sunlight."},
        {"id": "doc3", "text": "Lencho wrote a letter to God asking for a hundred pesos to sow his field again after the hailstorm."},
    ]
    index = BM25Index(corpus)

    res1 = index.search("euclid division integers", top_k=2)
    assert len(res1) > 0
    assert res1[0][0] == 0  # doc1 is top rank

    res2 = index.search("chlorophyll plants food photosynthesis", top_k=2)
    assert len(res2) > 0
    assert res2[0][0] == 1  # doc2 is top rank

    res3 = index.search("lencho letter god hailstorm", top_k=2)
    assert len(res3) > 0
    assert res3[0][0] == 2  # doc3 is top rank


@pytest.fixture
def synthetic_auditor_data(db_session):
    """
    Seeds a minimal, explicitly synthetic curriculum hierarchy and LearningContent records
    to test ChunkAuditor and ProvenanceAuditor logic in an isolated test database.

    SYNTHETIC LABEL: Strictly synthetic test fixture. Does not represent authentic student content.
    NOTE ON PROVENANCE: Source document references and page numbers (e.g. page 14 of
    STD-10th/Std-10_Maths_EnglishMedium.pdf) are used solely to test physical page-bound
    validation (checking that the PDF file exists and has >= 14 pages). Physical page-bound
    validation confirms page existence within the physical PDF document, but does NOT establish
    that the synthetic fixture text matches the authentic textbook content on that page.
    """
    import uuid
    from backend.app.models import Standard, Subject, Chapter, Topic, LearningContent

    created_ids = {
        "learning_content": [],
        "topic": [],
        "chapter": [],
        "subject": [],
        "standard": [],
    }

    # 1. Standard 10
    std = Standard(id=str(uuid.uuid4()), name="Standard 10 [Synthetic]", grade_number=10)
    db_session.add(std)
    db_session.flush()
    created_ids["standard"].append(std.id)

    # 2. Subject Mathematics
    subj = Subject(id=str(uuid.uuid4()), name="Mathematics [Synthetic]", code=f"SYN_MATH_{uuid.uuid4().hex[:6]}", standard_id=std.id, is_active=True)
    db_session.add(subj)
    db_session.flush()
    created_ids["subject"].append(subj.id)

    # 3. Chapter Real Numbers
    chap = Chapter(id=str(uuid.uuid4()), title="Real Numbers [Synthetic]", chapter_number=1, subject_id=subj.id, is_active=True)
    db_session.add(chap)
    db_session.flush()
    created_ids["chapter"].append(chap.id)

    # 4. Topics
    t1 = Topic(id=str(uuid.uuid4()), title="Euclid's Division Lemma [Synthetic]", topic_order=1, chapter_id=chap.id, is_active=True)
    t2 = Topic(id=str(uuid.uuid4()), title="Fundamental Theorem of Arithmetic [Synthetic]", topic_order=2, chapter_id=chap.id, is_active=True)
    db_session.add_all([t1, t2])
    db_session.flush()
    created_ids["topic"].extend([t1.id, t2.id])

    # 5. Synthetic LearningContent records matching ChunkAuditor retrieval queries
    # Target source doc references the sample PDF available in GSEB-Dataset for physical page bounds verification
    chunk_1_text = (
        "Euclid's division lemma states that for given positive integers a and b there exist unique integers "
        "q and r satisfying the relation a = bq + r with remainder constraint zero less than or equal to r less than b. "
        "This foundational theorem of arithmetic establishes the mathematical framework for the Euclidean algorithm, "
        "enabling deterministic computation of the greatest common divisor between any two natural numbers. "
        "Through systematic quotient division and successive remainder calculation, division lemma forms the basis "
        "for continuous divisibility proofs and modular arithmetic operations across number systems."
    )
    chunk_2_text = (
        "The fundamental theorem of arithmetic states that every composite number can be expressed as a product "
        "of prime factors, and this factorization is unique apart from the order in which the prime factors occur. "
        "Composite natural numbers decompose into unique prime products, ensuring canonical representation in number theory. "
        "This principle provides the foundation for finding the highest common factor and lowest common multiple "
        "of sets of positive integers by prime power decomposition and exponent analysis in algebraic mathematics."
    )

    lc1 = LearningContent(
        id=str(uuid.uuid4()),
        title="[Synthetic Fixture] Euclid's Division Lemma",
        content_text=chunk_1_text,
        topic_id=t1.id,
        chunk_identifier=f"syn_chunk_001_{uuid.uuid4().hex[:6]}",
        source_document="STD-10th/Std-10_Maths_EnglishMedium.pdf",
        source_page=14,
    )
    lc2 = LearningContent(
        id=str(uuid.uuid4()),
        title="[Synthetic Fixture] Fundamental Theorem of Arithmetic",
        content_text=chunk_2_text,
        topic_id=t2.id,
        chunk_identifier=f"syn_chunk_002_{uuid.uuid4().hex[:6]}",
        source_document="STD-10th/Std-10_Maths_EnglishMedium.pdf",
        source_page=14,
    )
    db_session.add_all([lc1, lc2])
    db_session.commit()
    created_ids["learning_content"].extend([lc1.id, lc2.id])

    try:
        yield {"standard": std, "subject": subj, "chapter": chap, "topics": [t1, t2], "contents": [lc1, lc2]}
    finally:
        try:
            db_session.query(LearningContent).filter(LearningContent.id.in_(created_ids["learning_content"])).delete(synchronize_session=False)
            db_session.query(Topic).filter(Topic.id.in_(created_ids["topic"])).delete(synchronize_session=False)
            db_session.query(Chapter).filter(Chapter.id.in_(created_ids["chapter"])).delete(synchronize_session=False)
            db_session.query(Subject).filter(Subject.id.in_(created_ids["subject"])).delete(synchronize_session=False)
            db_session.query(Standard).filter(Standard.id.in_(created_ids["standard"])).delete(synchronize_session=False)
            db_session.commit()
        except Exception:
            db_session.rollback()


def test_chunk_auditor_runs_on_database(synthetic_auditor_data, tmp_path):
    auditor = ChunkAuditor(output_dir=tmp_path)
    report = auditor.run_audit()
    assert report.total_chunks_evaluated > 0
    assert report.avg_tokens > 100
    assert report.quality_gate_status in ["PASS", "CONDITIONAL_PASS", "FAIL"]
    assert len(report.retrieval_results) == len(auditor.CURATED_QUERIES)
    assert (tmp_path / "chunk_quality_report.json").exists()
    assert (tmp_path / "chunk_quality_report.md").exists()


def test_provenance_auditor_runs_on_database(synthetic_auditor_data, tmp_path):
    auditor = ProvenanceAuditor(sample_size=10, output_dir=tmp_path)
    report = auditor.run_audit()
    assert report.total_learning_contents > 0
    assert report.valid_lineage_count == report.total_learning_contents
    assert report.orphaned_contents == 0
    assert report.orphaned_topics == 0
    assert report.orphaned_chapters == 0
    assert report.duplicate_chunks_count == 0
    assert report.provenance_integrity_score >= 0.85
    assert report.quality_gate_status in ["PASS", "CONDITIONAL_PASS"]
    assert (tmp_path / "provenance_audit.json").exists()
    assert (tmp_path / "provenance_audit.md").exists()


def test_provenance_auditor_raises_on_empty_database(db_session, tmp_path):
    """Verifies that ProvenanceAuditor safely raises ValueError when no learning content exists."""
    auditor = ProvenanceAuditor(sample_size=10, output_dir=tmp_path)
    with pytest.raises(ValueError, match="No LearningContent records found in database"):
        auditor.run_audit()
