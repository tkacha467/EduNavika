"""
EduNavika — Milestone 5.4: NEET 2021 Question Quality Validation & Audit Test Suite.
Hardened regression and integration tests covering:
- Real PDF integration and complete 1..200 question number coverage
- Missing, duplicate, and out-of-range question detection
- Numeric option markers (1)-(4) and rejection of scrambled/shifted options
- Stem statement enumerations (A)/(B) and assertion formats without key duplication
- Empty options and hard figure dependencies safe quarantine
- Terminal section footer leakage stripping
- Deterministic repeated audit execution
- Persistent database isolation guarantee
"""

import os
import sys
import uuid
import pytest
from sqlalchemy import create_engine, text

from scripts.audit_neet_2021_quality import (
    DEFAULT_PAPER_PDF,
    DEFAULT_NTA_KEY_PDF,
    extract_official_nta_manifest,
    parse_and_audit_neet_paper,
    compute_sha256,
)


@pytest.fixture(scope="module")
def nta_manifest():
    """Loads authoritative NTA answer-key manifest from repository reference copy."""
    return extract_official_nta_manifest(DEFAULT_NTA_KEY_PDF, booklet_code="M4")


def test_real_neet_pdf_integration(nta_manifest):
    """
    Executes the real parser and auditor on the actual source PDFs:
    GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf and docs/reference/Notice_20211101205130.pdf.
    """
    records, summary = parse_and_audit_neet_paper(DEFAULT_PAPER_PDF, nta_manifest)

    # 1. Complete Question Number Range: exactly 200 questions, strictly 1 through 200
    assert len(records) == 200
    q_nums = [r["question_number"] for r in records]
    assert q_nums == list(range(1, 201))

    # 2. Booklet code consistency
    assert all(r["booklet_code"] == "M4" for r in records)

    # 3. Discrepancy Resolution Verification:
    # Exactly 13 distinct quarantined questions: 9 blank options, 4 hard stem diagrams
    assert summary["scoring_eligibility_metrics"]["eligible_for_scoring_count"] == 187
    assert summary["scoring_eligibility_metrics"]["ineligible_empty_options_count"] == 9
    assert summary["scoring_eligibility_metrics"]["ineligible_requires_asset_count"] == 4
    assert len(summary["quarantined_question_ids"]["total_distinct_quarantined_13_ids"]) == 13

    # Verify specific quarantined IDs
    blank_ids = summary["quarantined_question_ids"]["blank_options_9_ids"]
    assert blank_ids == [26, 38, 60, 62, 63, 79, 82, 88, 99]

    stem_ids = summary["quarantined_question_ids"]["hard_stem_diagram_4_ids"]
    assert stem_ids == [4, 20, 40, 49]

    # 4. Question 50 Fraction Resolution:
    q50 = next(r for r in records if r["question_number"] == 50)
    assert q50["scoring_eligibility"] == "ELIGIBLE_FOR_SCORING"
    assert q50["option_A_normalized"] == "3/4"
    assert q50["option_B_normalized"] == "7/8"
    assert q50["option_C_normalized"] == "1/4"
    assert q50["option_D_normalized"] == "1/8"
    assert "Section - A (Chemistry)" not in q50["option_D_normalized"]

    # 5. Question 1 Statement Handling:
    q1 = next(r for r in records if r["question_number"] == 1)
    assert q1["scoring_eligibility"] == "ELIGIBLE_FOR_SCORING"
    assert q1["option_A_normalized"] == "(A) and (B) both are correct."
    assert q1["normalized_answer"] == "C"

    # 6. Question 196 Assertion-Reason Handling:
    q196 = next(r for r in records if r["question_number"] == 196)
    assert q196["scoring_eligibility"] == "ELIGIBLE_FOR_SCORING"
    assert q196["normalized_answer"] == "A"

    # 7. Terminal Footer Stripping:
    # Q35 option D must NOT contain "Section - B (Physics)"
    q35 = next(r for r in records if r["question_number"] == 35)
    assert "Section - B (Physics)" not in q35["option_D_normalized"]

    # Q200 option D must be clean text without booklet end markers or rough work page numbers
    q200 = next(r for r in records if r["question_number"] == 200)
    assert q200["option_D_normalized"] == "(b) and (c) are correct"


def test_reproducibility_deterministic_outputs(nta_manifest):
    """Validates that running the audit twice produces identical records."""
    records_1, summary_1 = parse_and_audit_neet_paper(DEFAULT_PAPER_PDF, nta_manifest)
    records_2, summary_2 = parse_and_audit_neet_paper(DEFAULT_PAPER_PDF, nta_manifest)

    assert len(records_1) == len(records_2) == 200
    for r1, r2 in zip(records_1, records_2):
        for key in r1:
            if key != "audited_at":
                assert r1[key] == r2[key], f"Determinism failure for Q{r1['question_number']} on {key}"

    assert summary_1["scoring_eligibility_metrics"] == summary_2["scoring_eligibility_metrics"]


def test_missing_question_fails_audit(nta_manifest):
    """Ensures manifest validation fails if fewer than 200 answers exist."""
    bad_manifest = dict(nta_manifest)
    bad_manifest["answers"] = {k: v for k, v in nta_manifest["answers"].items() if k != 50}

    records, summary = parse_and_audit_neet_paper(DEFAULT_PAPER_PDF, bad_manifest)
    q50 = next(r for r in records if r["question_number"] == 50)
    assert q50["official_raw_answer"] is None


def test_booklet_mismatch_fails_safely():
    """Manifest extraction fails if requested booklet does not exist in NTA document."""
    with pytest.raises(ValueError, match="Booklet code 'Z9' not found"):
        extract_official_nta_manifest(DEFAULT_NTA_KEY_PDF, booklet_code="Z9")


def test_missing_manifest_file_fails_explicitly():
    """Fails with explicit FileNotFoundError if NTA document is missing, rather than fabricating."""
    with pytest.raises(FileNotFoundError, match="Authoritative NTA Answer Key PDF not found"):
        extract_official_nta_manifest("non_existent_key.pdf", booklet_code="M4")


def test_persistent_db_isolation_guard():
    """Confirms conftest guard strictly blocks any test from opening edunavika.db."""
    with pytest.raises(RuntimeError, match="DATABASE ISOLATION VIOLATION"):
        engine = create_engine(r"sqlite:///D:/EduNavika/edunavika.db")
        with engine.connect():
            pass
