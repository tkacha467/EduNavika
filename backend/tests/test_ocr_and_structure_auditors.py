import pytest
from pathlib import Path
from backend.app.ingestion.ocr.ocr_auditor import OCRAuditor
from backend.app.ingestion.structure_auditor import StructureAuditor


def test_structure_auditor_representative_books():
    dataset_dir = Path("GSEB-Dataset")
    if not dataset_dir.exists():
        pytest.skip("GSEB-Dataset not available")

    auditor = StructureAuditor(dataset_dir)
    report = auditor.audit_representative_books()

    assert report.total_audited >= 3
    assert report.passed_count >= 2
    assert report.failed_count == 0

    # Ensure Std-10 Maths detected at least 14 chapters
    maths_doc = next((d for d in report.documents if "Math" in d.document_name), None)
    assert maths_doc is not None
    assert maths_doc.detected_chapters >= 14
    assert maths_doc.status == "PASS"


def test_ocr_auditor_scan():
    dataset_dir = Path("GSEB-Dataset")
    if not dataset_dir.exists():
        pytest.skip("GSEB-Dataset not available")

    auditor = OCRAuditor(dataset_dir)
    docs, mismatches = auditor.scanner.scan_all()
    assert len(docs) == 86
    assert len(mismatches) == 0
