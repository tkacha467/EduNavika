import pytest
from pathlib import Path
from backend.app.ingestion.ocr.ocr_auditor import OCRAuditor
from backend.app.ingestion.structure_auditor import StructureAuditor


def test_structure_auditor_representative_books():
    dataset_dir = Path("GSEB-Dataset")
    if not dataset_dir.exists() or not list(dataset_dir.rglob("*.pdf")):
        pytest.skip("GSEB-Dataset physical PDFs not available (gitignored corpus)")

    auditor = StructureAuditor(dataset_dir)
    report = auditor.audit_representative_books()

    # Verify that available representative books (Std-10 Science and Std-10 Maths) are audited and pass
    assert report.total_audited >= 2, f"Expected at least 2 representative books audited, got {report.total_audited}"
    assert report.passed_count == report.total_audited, f"All audited representative books must pass, passed: {report.passed_count}/{report.total_audited}"
    assert report.failed_count == 0

    # Ensure Std-10 Maths detected at least 14 chapters
    maths_doc = next((d for d in report.documents if "Math" in d.document_name), None)
    assert maths_doc is not None
    assert maths_doc.detected_chapters >= 14
    assert maths_doc.status == "PASS"


def test_structure_auditor_full_three_book_representative_set():
    """
    Full-corpus integration test: Validates all 3 representative books (Science, English, Maths).
    Requires the complete physical corpus including Std-10_First Flight_EnglishMedium.pdf.
    """
    dataset_dir = Path("GSEB-Dataset")
    if not dataset_dir.exists():
        pytest.skip("GSEB-Dataset not available")

    english_exists = any((dataset_dir / p).exists() for p in [
        "STD-10/Std-10_First Flight_EnglishMedium.pdf",
        "STD-10th/Std-10_First Flight_EnglishMedium.pdf",
    ])
    if not english_exists:
        pytest.skip("Full representative 3-book set requires Std-10_First Flight_EnglishMedium.pdf in GSEB-Dataset")

    auditor = StructureAuditor(dataset_dir)
    report = auditor.audit_representative_books()
    assert report.total_audited >= 3
    assert report.passed_count >= 3
    assert report.failed_count == 0


def test_ocr_auditor_scan():
    dataset_dir = Path("GSEB-Dataset")
    if not dataset_dir.exists() or not list(dataset_dir.rglob("*.pdf")):
        pytest.skip("GSEB-Dataset physical PDFs not available (gitignored corpus)")

    auditor = OCRAuditor(dataset_dir)
    docs, mismatches = auditor.scanner.scan_all()
    assert len(docs) > 0, "OCR auditor scanner must discover available physical PDFs"
    assert len(mismatches) == 0, f"Expected zero manifest mismatches, found {len(mismatches)}"


def test_full_corpus_ocr_auditor_scan_86_books():
    """Full-corpus integration test requiring all 86 physical PDFs in GSEB-Dataset."""
    dataset_dir = Path("GSEB-Dataset")
    if not dataset_dir.exists():
        pytest.skip("GSEB-Dataset not available")
    auditor = OCRAuditor(dataset_dir)
    docs, _ = auditor.scanner.scan_all()
    if len(docs) < 86:
        pytest.skip(f"Full 86-book physical corpus prerequisite not met (found {len(docs)} of 86 PDFs in GSEB-Dataset)")
    assert len(docs) == 86
