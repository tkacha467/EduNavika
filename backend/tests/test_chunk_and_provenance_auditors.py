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


def test_chunk_auditor_runs_on_database():
    auditor = ChunkAuditor()
    report = auditor.run_audit()
    assert report.total_chunks_evaluated > 0
    assert report.avg_tokens > 100
    assert report.quality_gate_status in ["PASS", "CONDITIONAL_PASS", "FAIL"]
    assert len(report.retrieval_results) == len(auditor.CURATED_QUERIES)


def test_provenance_auditor_runs_on_database():
    auditor = ProvenanceAuditor(sample_size=10)
    report = auditor.run_audit()
    assert report.total_learning_contents > 0
    assert report.valid_lineage_count == report.total_learning_contents
    assert report.orphaned_contents == 0
    assert report.orphaned_topics == 0
    assert report.orphaned_chapters == 0
    assert report.duplicate_chunks_count == 0
    assert report.provenance_integrity_score >= 0.95
    assert report.quality_gate_status in ["PASS", "CONDITIONAL_PASS"]
