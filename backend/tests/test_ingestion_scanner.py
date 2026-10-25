import pytest
from pathlib import Path
from backend.app.ingestion.scanner import DocumentScanner
from backend.app.ingestion.schemas import DocumentIdentity


def test_scanner_pdf_discovery_and_deterministic_ids():
    input_dir = Path("GSEB-Dataset")
    assert input_dir.exists(), "GSEB-Dataset folder must exist"

    scanner = DocumentScanner(input_dir)
    docs, mismatches = scanner.scan_all()

    if not docs:
        pytest.skip("Physical GSEB textbook PDFs not present in GSEB-Dataset (gitignored corpus)")

    # Verify physical PDFs are discovered and non-empty
    assert len(docs) > 0, "Scanner must discover available physical PDFs"

    # Check deterministic document identity structure
    for doc in docs:
        assert doc.document_id.startswith("doc_"), "Document ID must start with doc_"
        assert len(doc.file_hash) == 64, "File hash must be SHA-256 (64 hex characters)"
        assert doc.standard in [9, 10, 11, 12], f"Invalid standard {doc.standard}"
        assert doc.file_size_bytes > 0, "File size must be positive"
        assert doc.filename.endswith(".pdf"), "Only PDF files should be discovered"

    # Re-running scanner must produce identical document IDs (determinism)
    docs_rerun, _ = scanner.scan_all()
    map_1 = {d.relative_path: d.document_id for d in docs}
    map_2 = {d.relative_path: d.document_id for d in docs_rerun}
    assert map_1 == map_2, "Document IDs must be 100% deterministic across runs"


def test_scanner_manifest_reconciliation():
    input_dir = Path("GSEB-Dataset")
    scanner = DocumentScanner(input_dir)
    docs, mismatches = scanner.scan_all()

    assert len(scanner.manifest_docs) == 86, "Manifest must contain 86 expected documents"
    if not docs:
        pytest.skip("Physical GSEB textbook PDFs not present in GSEB-Dataset (gitignored corpus)")
    assert len(docs) > 0, "At least one document must be discovered"

    # All discovered physical files must match authoritative manifest metadata
    matched_count = sum(1 for d in docs if d.manifest_matched)
    assert matched_count == len(docs), f"All {len(docs)} discovered documents must match manifest, matched: {matched_count}"
    assert len(mismatches) == 0, f"Expected zero manifest mismatches, got {len(mismatches)}"


def test_full_corpus_pdf_discovery_and_reconciliation_86_books():
    """
    Full-corpus integration test: Validates all 86 physical textbook PDFs against manifest.
    Requires the complete 86-document physical dataset to be present in GSEB-Dataset.
    """
    input_dir = Path("GSEB-Dataset")
    assert input_dir.exists(), "GSEB-Dataset folder must exist"
    scanner = DocumentScanner(input_dir)
    docs, mismatches = scanner.scan_all()
    if len(docs) < 86:
        pytest.skip(f"Full 86-book physical corpus prerequisite not met (found {len(docs)} of 86 PDFs in GSEB-Dataset)")
    assert len(docs) == 86
    assert sum(1 for d in docs if d.manifest_matched) == 86
    assert len(mismatches) == 0


def test_scanner_unit_isolated_fixture(tmp_path):
    """
    Isolated unit test: Validates DocumentScanner behavior using a self-contained
    temporary directory and synthetic manifest with zero local filesystem dependencies.
    """
    import json

    # 1. Create synthetic manifest
    manifest_content = {
        "textbooks": [
            {
                "relative_path": "STD-10th/Math.pdf",
                "filename": "Math.pdf",
                "grade": "STD-10th",
                "subject": "Mathematics",
                "category": "CORE_TEXTBOOK",
                "curriculum_relevance": "HIGH",
                "ocr_requirement": "NONE",
                "num_pages": 100,
            },
            {
                "relative_path": "STD-10th/Science.pdf",
                "filename": "Science.pdf",
                "grade": "STD-10th",
                "subject": "Science & Technology",
                "category": "CORE_TEXTBOOK",
                "curriculum_relevance": "HIGH",
                "ocr_requirement": "NONE",
                "num_pages": 120,
            },
        ]
    }
    with open(tmp_path / "dataset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_content, f)

    # 2. Create sample files
    subfolder = tmp_path / "STD-10th"
    subfolder.mkdir()
    (subfolder / "Math.pdf").write_bytes(b"%PDF-1.4 sample math content")
    (subfolder / "Science.pdf").write_bytes(b"%PDF-1.4 sample science content")

    # 3. Scan temporary directory
    scanner = DocumentScanner(tmp_path)
    docs, mismatches = scanner.scan_all()

    assert len(docs) == 2
    assert len(mismatches) == 0
    assert len(scanner.manifest_docs) == 2
    assert all(d.manifest_matched for d in docs)
    assert all(d.standard == 10 for d in docs)
