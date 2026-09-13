import pytest
from pathlib import Path
from backend.app.ingestion.scanner import DocumentScanner
from backend.app.ingestion.schemas import DocumentIdentity


def test_scanner_pdf_discovery_and_deterministic_ids():
    input_dir = Path("GSEB-Dataset")
    assert input_dir.exists(), "GSEB-Dataset folder must exist"

    scanner = DocumentScanner(input_dir)
    docs, mismatches = scanner.scan_all()

    # We expect 86 PDFs in total across the 4 Standards
    assert len(docs) == 86, f"Expected 86 PDFs, found {len(docs)}"

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
    # All 86 files should match manifest metadata
    matched_count = sum(1 for d in docs if d.manifest_matched)
    assert matched_count == 86, f"All 86 documents should match manifest, matched: {matched_count}"
