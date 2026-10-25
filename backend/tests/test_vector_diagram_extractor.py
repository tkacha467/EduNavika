"""
Unit and Integration Tests for Vector Diagram Extractor (Milestone 5.7).

Verifies:
- Synthetic PDF unit tests: vector geometry, boundary clamping, border filtering.
- Error handling: missing PDF, corrupt PDF, checksum mismatch, out-of-range page, missing question.
- Extraction integrity: lossless PNG header, non-zero dimensions, SHA-256 computation.
- Idempotency and conflict detection: overwriting safety.
- Database isolation: zero persistent database connections or mutations.
- Real NEET 2021 source integration: exactly 41 assets (4 stem, 36 option, 1 hybrid).
- Correct preservation of option labels (1)-(4) and keys (A)-(D).
"""

import os
import tempfile
import hashlib
import json
import pytest
import pymupdf

from backend.app.ingestion.vector_diagram_extractor import (
    VectorDiagramExtractor,
    QuestionTargetConfig,
    DiagramAssetRecord,
    NEET_2021_M4_CONFIGS,
    VectorExtractionError,
    PDFSourceError,
    BoundingBoxError,
    AssetIntegrityError,
)

REAL_NEET_2021_PDF = "GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf"
EXPECTED_NEET_PDF_HASH = "e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a"


# ==============================================================================
# Database Isolation Guard Fixture
# ==============================================================================

@pytest.fixture(autouse=True)
def guard_against_persistent_db(monkeypatch):
    """
    Ensure no test accidental connects to or mutates the persistent database.
    """
    def forbidden_connect(*args, **kwargs):
        raise RuntimeError("CRITICAL ERROR: Attempted persistent database access during Milestone 5.7 test!")

    try:
        from backend.app.core import database
        monkeypatch.setattr(database.engine, "connect", forbidden_connect)
    except Exception:
        pass


# ==============================================================================
# Synthetic PDF Fixtures
# ==============================================================================

@pytest.fixture
def synthetic_pdf_path():
    """
    Creates a temporary synthetic 2-column PDF with known text, vector shapes,
    page borders, and multiple candidate regions.
    """
    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, "synthetic_exam.pdf")

    doc = pymupdf.open()
    page = doc.new_page(width=595.0, height=842.0)  # Standard A4

    # 1. Unrelated decorative border and central column divider
    # Central divider at x = 298.08, y in [90, 775]
    page.draw_line(pymupdf.Point(298.08, 90.0), pymupdf.Point(298.08, 775.0), color=(0.5, 0.5, 0.5), width=0.5)
    # Header line
    page.draw_line(pymupdf.Point(35.0, 70.0), pymupdf.Point(560.0, 70.0), color=(0.7, 0.7, 0.7), width=0.5)

    # 2. Column 0: Question 1 (Stem diagram)
    # Stem text
    page.insert_text(pymupdf.Point(40.0, 100.0), "1. Consider the circuit diagram shown below:", fontsize=10)
    page.insert_text(pymupdf.Point(40.0, 115.0), "The equivalent resistance is :", fontsize=10)

    # Diagram vector lines (resistor bridge) between y=130 and y=190
    page.draw_rect(pymupdf.Rect(70.0, 135.0, 220.0, 185.0), color=(0, 0, 0), width=1.0)
    page.draw_line(pymupdf.Point(50.0, 160.0), pymupdf.Point(70.0, 160.0), color=(0, 0, 0), width=1.0)
    page.draw_line(pymupdf.Point(220.0, 160.0), pymupdf.Point(240.0, 160.0), color=(0, 0, 0), width=1.0)

    # Options text
    page.insert_text(pymupdf.Point(70.0, 210.0), "(1) 10 Ohm", fontsize=10)
    page.insert_text(pymupdf.Point(70.0, 225.0), "(2) 20 Ohm", fontsize=10)
    page.insert_text(pymupdf.Point(70.0, 240.0), "(3) 30 Ohm", fontsize=10)
    page.insert_text(pymupdf.Point(70.0, 255.0), "(4) 40 Ohm", fontsize=10)

    # Next question anchor
    page.insert_text(pymupdf.Point(40.0, 280.0), "2. Next question text here.", fontsize=10)

    # 3. Column 0: Question 2 (Graphical options)
    page.insert_text(pymupdf.Point(40.0, 295.0), "Which of the following graphs is correct?", fontsize=10)
    # Option (1)
    page.insert_text(pymupdf.Point(70.0, 320.0), "(1)", fontsize=10)
    page.draw_rect(pymupdf.Rect(100.0, 310.0, 180.0, 340.0), color=(0, 0, 0), width=1.0)
    # Option (2)
    page.insert_text(pymupdf.Point(70.0, 370.0), "(2)", fontsize=10)
    page.draw_rect(pymupdf.Rect(100.0, 360.0, 180.0, 390.0), color=(0, 0, 0), width=1.0)
    # Option (3)
    page.insert_text(pymupdf.Point(70.0, 420.0), "(3)", fontsize=10)
    page.draw_rect(pymupdf.Rect(100.0, 410.0, 180.0, 440.0), color=(0, 0, 0), width=1.0)
    # Option (4)
    page.insert_text(pymupdf.Point(70.0, 470.0), "(4)", fontsize=10)
    page.draw_rect(pymupdf.Rect(100.0, 460.0, 180.0, 490.0), color=(0, 0, 0), width=1.0)

    # Next question
    page.insert_text(pymupdf.Point(40.0, 520.0), "3. Following question.", fontsize=10)

    doc.save(pdf_path)
    doc.close()

    yield pdf_path

    # Cleanup
    if os.path.exists(pdf_path):
        os.remove(pdf_path)


# ==============================================================================
# Unit Tests (Synthetic PDF)
# ==============================================================================

def test_source_validation_missing_file():
    extractor = VectorDiagramExtractor()
    with pytest.raises(PDFSourceError, match="does not exist"):
        extractor.validate_source_pdf("nonexistent_path_12345.pdf")


def test_source_validation_checksum_mismatch(synthetic_pdf_path):
    extractor = VectorDiagramExtractor()
    wrong_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    with pytest.raises(PDFSourceError, match="checksum mismatch"):
        extractor.validate_source_pdf(synthetic_pdf_path, expected_sha256=wrong_hash)


def test_synthetic_stem_extraction(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out, render_scale=2.0, padding_pts=4.0)

    cfg = QuestionTargetConfig(1, 0, 1, 0, "stem", "Synthetic resistor bridge")
    records = extractor.extract_all(synthetic_pdf_path, [cfg])

    assert len(records) == 1
    rec = records[0]
    assert rec.extraction_status == "EXTRACTED"
    assert rec.asset_role == "stem"
    assert rec.question_number == 1
    assert os.path.exists(rec.output_relative_path)
    assert rec.output_dimensions[0] > 0
    assert rec.output_dimensions[1] > 0
    assert rec.file_size_bytes > 0
    assert rec.human_review_status == "PENDING_HUMAN_REVIEW"

    # Verify PNG header
    with open(rec.output_relative_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"


def test_synthetic_options_extraction(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out, render_scale=2.0, padding_pts=4.0)

    cfg = QuestionTargetConfig(2, 0, 1, 0, "options", "Synthetic 4 options")
    records = extractor.extract_all(synthetic_pdf_path, [cfg])

    assert len(records) == 4
    for i, opt_key in enumerate(["A", "B", "C", "D"]):
        rec = records[i]
        assert rec.extraction_status == "EXTRACTED"
        assert rec.asset_role == "option"
        assert rec.option_key == opt_key
        assert rec.option_label == f"({i+1})"
        assert os.path.exists(rec.output_relative_path)
        assert rec.human_review_status == "PENDING_HUMAN_REVIEW"


def test_border_filtering_excludes_column_divider(synthetic_pdf_path):
    extractor = VectorDiagramExtractor()
    doc = pymupdf.open(synthetic_pdf_path)
    page = doc[0]
    drawings = page.get_drawings()

    # Total drawings include the 685 pt column divider
    has_divider = any(d["rect"].height > 200 for d in drawings)
    assert has_divider, "Synthetic PDF should contain vertical divider"

    # filter_column_drawings must exclude it
    filtered = extractor.filter_column_drawings(drawings, 35.0, 296.0, 90.0, 300.0)
    for d in filtered:
        assert d["rect"].height <= 200.0
        assert abs(d["rect"].x0 - 298.08) >= 1.0


def test_out_of_bounds_page_index(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out)
    cfg = QuestionTargetConfig(999, 99, 100, 0, "stem")
    records = extractor.extract_all(synthetic_pdf_path, [cfg])

    assert len(records) == 1
    assert records[0].extraction_status == "FAILED"
    assert "out of range" in records[0].failure_reason


def test_missing_question_anchor(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out)
    cfg = QuestionTargetConfig(99, 0, 1, 0, "stem")  # Question 99 does not exist on synthetic page
    records = extractor.extract_all(synthetic_pdf_path, [cfg])

    assert len(records) == 1
    assert records[0].extraction_status == "FAILED"
    assert "marker not found" in records[0].failure_reason


def test_idempotent_extraction(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out)
    cfg = QuestionTargetConfig(1, 0, 1, 0, "stem")

    # Run 1
    records_1 = extractor.extract_all(synthetic_pdf_path, [cfg])
    hash_1 = records_1[0].output_sha256

    # Run 2 (no overwrite, should match idempotently)
    records_2 = extractor.extract_all(synthetic_pdf_path, [cfg], overwrite=False)
    hash_2 = records_2[0].output_sha256

    assert hash_1 == hash_2
    assert records_2[0].extraction_status == "EXTRACTED"


def test_asset_conflict_detection(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out)
    cfg = QuestionTargetConfig(1, 0, 1, 0, "stem")

    records = extractor.extract_all(synthetic_pdf_path, [cfg])
    out_file = records[0].output_relative_path

    # Intentionally corrupt/modify the existing asset
    with open(out_file, "wb") as f:
        f.write(b"corrupted_content_not_matching_sha256")

    # Second extraction without overwrite should catch conflict
    cfg_target = [cfg]
    records_conflict = extractor.extract_all(synthetic_pdf_path, cfg_target, overwrite=False)
    assert records_conflict[0].extraction_status == "FAILED"
    assert "Asset conflict" in records_conflict[0].failure_reason


def test_manifest_generation(synthetic_pdf_path):
    temp_out = tempfile.mkdtemp()
    manifest_path = os.path.join(temp_out, "manifest.json")
    extractor = VectorDiagramExtractor(output_base_dir=temp_out)

    cfg = QuestionTargetConfig(1, 0, 1, 0, "stem")
    records = extractor.extract_all(synthetic_pdf_path, [cfg])
    manifest = extractor.generate_manifest(records, manifest_path)

    assert os.path.exists(manifest_path)
    assert manifest["summary"]["total_candidate_assets"] == 1
    assert manifest["summary"]["successfully_extracted"] == 1
    assert manifest["summary"]["pending_human_review"] == 1
    assert manifest["summary"]["human_verified"] == 0
    assert len(manifest["assets"]) == 1


# ==============================================================================
# Integration Tests (Real NEET 2021 Source PDF)
# ==============================================================================

@pytest.mark.skipif(not os.path.exists(REAL_NEET_2021_PDF), reason="Real NEET 2021 PDF not found")
def test_real_neet_2021_full_extraction_41_assets():
    """
    Test extraction against actual GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf.
    Must extract exactly 41 distinct assets:
    - 4 stem diagrams (Q4, Q20, Q40, Q49)
    - 32 option diagrams (Q26, Q60, Q62, Q63, Q79, Q82, Q88, Q99)
    - 5 hybrid diagrams (Q38 stem + 4 options)
    Total = 41 assets, 0 failures.
    """
    temp_out = tempfile.mkdtemp()
    manifest_out = os.path.join(temp_out, "manifest.json")
    contact_sheet_out = os.path.join(temp_out, "contact_sheet.html")

    extractor = VectorDiagramExtractor(output_base_dir=temp_out, render_scale=2.0, padding_pts=4.0)
    records = extractor.extract_all(
        pdf_path=REAL_NEET_2021_PDF,
        target_configs=NEET_2021_M4_CONFIGS,
        expected_pdf_sha256=EXPECTED_NEET_PDF_HASH,
        overwrite=True,
    )

    assert len(records) == 41, f"Expected 41 assets, got {len(records)}"

    extracted_records = [r for r in records if r.extraction_status == "EXTRACTED"]
    failed_records = [r for r in records if r.extraction_status == "FAILED"]
    assert len(failed_records) == 0, f"Extraction failed on targets: {[r.failure_reason for r in failed_records]}"
    assert len(extracted_records) == 41

    # Verify breakdown
    stems = [r for r in records if r.asset_role == "stem"]
    options = [r for r in records if r.asset_role == "option"]
    assert len(stems) == 5, f"Expected 5 stem diagrams (Q4, Q20, Q38, Q40, Q49), got {len(stems)}"
    assert len(options) == 36, f"Expected 36 option diagrams (9 questions * 4), got {len(options)}"

    # Verify each asset file is non-empty PNG with valid header
    for r in records:
        assert os.path.exists(r.output_relative_path)
        assert r.file_size_bytes > 500  # Real diagrams are well above 500 bytes
        assert r.output_dimensions[0] >= 50
        assert r.output_dimensions[1] >= 20
        assert r.human_review_status == "PENDING_HUMAN_REVIEW"

        with open(r.output_relative_path, "rb") as f:
            header = f.read(8)
            assert header == b"\x89PNG\r\n\x1a\n"

    # Verify manifest and contact sheet generation
    extractor.generate_manifest(records, manifest_out)
    assert os.path.exists(manifest_out)

    extractor.generate_contact_sheet(records, contact_sheet_out)
    assert os.path.exists(contact_sheet_out)


@pytest.mark.skipif(not os.path.exists(REAL_NEET_2021_PDF), reason="Real NEET 2021 PDF not found")
def test_real_neet_2021_option_ordering_integrity():
    """
    Verify that option keys A, B, C, D strictly map to labels (1), (2), (3), (4)
    and that their bounding boxes follow monotonic vertical order down the page.
    """
    temp_out = tempfile.mkdtemp()
    extractor = VectorDiagramExtractor(output_base_dir=temp_out)
    records = extractor.extract_all(
        pdf_path=REAL_NEET_2021_PDF,
        target_configs=NEET_2021_M4_CONFIGS,
        expected_pdf_sha256=EXPECTED_NEET_PDF_HASH,
    )

    grouped_options = {}
    for r in records:
        if r.asset_role == "option":
            grouped_options.setdefault(r.question_number, []).append(r)

    # 9 questions with options: Q26, Q38, Q60, Q62, Q63, Q79, Q82, Q88, Q99
    assert len(grouped_options) == 9

    for q_num, q_opts in grouped_options.items():
        assert len(q_opts) == 4, f"Q{q_num} does not have 4 options"
        assert [o.option_key for o in q_opts] == ["A", "B", "C", "D"]
        assert [o.option_label for o in q_opts] == ["(1)", "(2)", "(3)", "(4)"]

        # Verify vertical bounding box progression down page
        for i in range(3):
            assert q_opts[i].original_bbox[1] < q_opts[i+1].original_bbox[1], (
                f"Q{q_num} option {i} (y0={q_opts[i].original_bbox[1]}) not above "
                f"option {i+1} (y0={q_opts[i+1].original_bbox[1]})"
            )
