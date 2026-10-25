"""
EduNavika — Competitive Examination Paper Parser & Ingestion Pipeline (Milestone 5.1).
High-precision extraction for digital text-based previous-year papers (JEE Advanced, NEET UG).
Preserves authentic stems, mathematical notation, option structures, question numbers,
and enforces a strict question verification lifecycle without fabricating answer keys.
"""

import os
import re
import hashlib
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timezone

import pymupdf  # PyMuPDF
from sqlalchemy.orm import Session

from backend.app.services.question_ingestion_service import (
    QuestionIngestionService,
    compute_content_hash,
    validate_katex_syntax,
)
from backend.app.models.competitive_models import (
    Examination,
    ExamPaper,
    Question,
    QuestionOption,
    QuestionVerificationLog,
)
from backend.app.models.curriculum_models import Topic, Subject, Chapter

logger = logging.getLogger(__name__)

# Keywords identifying booklet covers, general candidate directions, and non-question front matter
COVER_INSTRUCTION_KEYWORDS = [
    r"important instructions",
    r"read the instructions carefully",
    r"test booklet",
    r"do not open this test booklet until",
    r"optical response sheet",
    r"\bors\b",
    r"candidate's name",
    r"roll no\b",
    r"general instructions",
    r"instructions to candidates",
    r"this booklet contains",
]


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def extract_paper_metadata(pdf_path: str) -> Dict[str, Any]:
    """
    Infers exam code, year, paper/session, language, and deterministic identifier
    from filepath and filename structure.
    """
    normalized_path = pdf_path.replace("\\", "/")
    filename = os.path.basename(normalized_path)
    file_hash = compute_file_sha256(pdf_path) if os.path.exists(pdf_path) else None

    # Detect Language
    lang = "EN"
    if "hindi" in filename.lower():
        lang = "HI"
    elif "gujarati" in filename.lower():
        lang = "GU"

    if "/jee/" in normalized_path.lower() or "jee" in filename.lower():
        exam_code = "JEE_ADVANCED"
        # Match year and paper: e.g. 2017_1.pdf or 2021_2_English.pdf
        m = re.search(r"(\d{4})_(\d)", filename)
        if m:
            year = int(m.group(1))
            session_num = m.group(2)
            session = f"Paper {session_num}"
            paper_ident = f"JEE_ADV_{year}_P{session_num}_{lang}"
        else:
            m_year = re.search(r"(\d{4})", filename)
            year = int(m_year.group(1)) if m_year else 2024
            session = "Paper 1"
            clean_name = os.path.splitext(filename)[0]
            paper_ident = f"JEE_ADV_{year}_{clean_name}_{lang}"

    elif "/neet/" in normalized_path.lower() or "neet" in filename.lower():
        exam_code = "NEET_UG"
        # Match NEET year: handles neet-2021.pdf, neet2-2016.pdf, neet-023.pdf
        m_phase = re.search(r"neet(\d+)[-_](\d{4})", filename.lower())
        m_year = re.search(r"neet[-_]?0?(\d{2,4})", filename.lower())
        
        if m_phase:
            phase = m_phase.group(1)
            year = int(m_phase.group(2))
            session = f"Phase {phase}"
            paper_ident = f"NEET_UG_{year}_P{phase}_{lang}"
        elif m_year:
            raw_y = m_year.group(1)
            year = int("20" + raw_y if len(raw_y) == 2 else raw_y)
            session = "Main"
            paper_ident = f"NEET_UG_{year}_{lang}"
        else:
            year = 2021
            session = "Main"
            paper_ident = f"NEET_UG_{year}_{lang}"
    else:
        exam_code = "JEE_MAIN"
        m_year = re.search(r"(\d{4})", filename)
        year = int(m_year.group(1)) if m_year else 2024
        session = "Shift 1"
        paper_ident = f"JEE_MAIN_{year}_{lang}"

    return {
        "exam_code": exam_code,
        "exam_year": year,
        "session_or_shift": session,
        "language": lang,
        "paper_identifier": paper_ident,
        "source_pdf_path": normalized_path,
        "source_pdf_hash": file_hash,
    }


def is_cover_or_instruction_page(text: str, page_num: int) -> Tuple[bool, str]:
    """
    Identifies whether a page is purely a cover page, OMR directions, or general instructions.
    Prevents instruction numbers from being misidentified as questions.
    """
    if page_num > 4:
        return False, "REGULAR_CONTENT_PAGE"

    lower_txt = text.lower()
    matches = [kw for kw in COVER_INSTRUCTION_KEYWORDS if re.search(kw, lower_txt)]

    has_booklet = "test booklet" in lower_txt or "this booklet contains" in lower_txt
    has_do_not_open = "do not open" in lower_txt
    has_candidate_info = "candidate" in lower_txt and ("roll no" in lower_txt or "signature" in lower_txt)

    # Check for presence of real question triggers
    has_jee_q = bool(re.search(r'(?:\n|\A)\s*Q\.?\s*[1-9]\b', text))
    has_neet_q = bool(re.search(r'(?:\n|\A)\s*[1-9]\.\s+[A-Za-z]', text)) and not has_booklet

    # If it has heavy instruction signals and no questions, or Page 1 of standard test booklet
    if (has_booklet or has_do_not_open or has_candidate_info) and not has_jee_q:
        if page_num == 1:
            return True, f"COVER_PAGE: Test booklet cover instructions ({len(matches)} matched signals)"

    # Dedicated general instructions page with no questions
    if len(matches) >= 3 and not (has_jee_q or has_neet_q):
        return True, f"INSTRUCTION_PAGE: Pure candidate instructions ({len(matches)} matched signals)"

    return False, "CONTENT_PAGE"


def detect_section_metadata(text: str, current_meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tracks Part/Subject headers and Section marking schemes across the paper.
    Determines whether subsequent questions are MCQ_MULTI, NUMERICAL, or SCQ.
    """
    meta = dict(current_meta)
    upper_txt = text.upper()

    # 1. Subject Header Detection
    if "PART I" in upper_txt or "PHYSICS" in upper_txt:
        if "CHEMISTRY" in upper_txt and "PHYSICS" not in upper_txt:
            meta["subject"] = "Chemistry"
        elif "MATHEMATICS" in upper_txt and "PHYSICS" not in upper_txt:
            meta["subject"] = "Mathematics"
        elif "BIOLOGY" in upper_txt or "BOTANY" in upper_txt or "ZOOLOGY" in upper_txt:
            meta["subject"] = "Biology"
        elif "PHYSICS" in upper_txt and ("PART" in upper_txt or "SECTION" in upper_txt):
            meta["subject"] = "Physics"

    # 2. Section and Question Type Detection
    sec_match = re.search(r'SECTION\s+(\d)', upper_txt)
    if sec_match:
        sec_num = sec_match.group(1)
        meta["section"] = f"SECTION {sec_num}"

        if "ONE OR MORE" in upper_txt or "ONE OR MORE THAN ONE" in upper_txt:
            meta["question_type"] = "MCQ_MULTI"
            meta["evaluation_policy"] = "JEE_ADV_MULTI_PARTIAL"
        elif "SINGLE DIGIT INTEGER" in upper_txt or "NON-NEGATIVE INTEGER" in upper_txt or "NUMERICAL VALUE" in upper_txt:
            meta["question_type"] = "NUMERICAL"
            meta["evaluation_policy"] = "NUMERICAL_TOLERANCE"
        elif "MATCHING" in upper_txt or "MATRIX MATCH" in upper_txt:
            meta["question_type"] = "MATCH"
            meta["evaluation_policy"] = "STANDARD_SCQ"
        elif "ONLY ONE" in upper_txt or "SINGLE CORRECT" in upper_txt:
            meta["question_type"] = "SCQ"
            meta["evaluation_policy"] = "STANDARD_SCQ"

    return meta


def clean_question_text(stem: str) -> str:
    """
    Normalizes stem whitespace and removes repeated running headers/footers
    while strictly preserving LaTeX mathematical symbols and equation line breaks.
    """
    # Remove running exam header / footer lines
    cleaned = re.sub(r'(?m)^\s*(?:Paper-\d\s+Code\s+\d|\d+/\d+|SPACE FOR ROUGH WORK|English/Gujarati).*$', '', stem)
    # Strip leading question number prefixes (e.g. "Q.1", "1.")
    cleaned = re.sub(r'^\s*Q\.?\s*\d+[\.\s:]*', '', cleaned)
    cleaned = re.sub(r'^\s*\d+\.\s*', '', cleaned)
    
    # Clean whitespace while preserving newlines
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in cleaned.splitlines()]
    non_empty = [l for l in lines if l]
    return '\n'.join(non_empty).strip()


def parse_options_flexible(body: str) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Extracts options in varied competitive exam formats:
    - Format 1: [A], [B], [C], [D] (JEE Advanced Bracket)
    - Format 2: (A), (B), (C), (D) (JEE Paren Alpha)
    - Format 3: (1), (2), (3), (4) (NEET Paren Numeric)
    - Format 4: A., B., C., D. (Standard Alpha Dot)
    Returns: (stem, options_list, detected_format_name)
    """
    strip_footers = r'(?i)\s*(?:Section\s*-\s*[AB]\s*\([^\)]+\)|-\s*o\s*0\s*o\s*-|\bM4\b|\bSPACE FOR ROUGH WORK\b|\d{1,2}(?:\s+\d{1,2})*)+$'

    # Format 1: [A] ... [B] ... [C] ... [D]
    opt_matches = list(re.finditer(r'\[([A-D])\]\s*(.*?)(?=\[[A-D]\]|\Z)', body, re.DOTALL))
    if len(opt_matches) >= 4 and len(set(om.group(1).upper() for om in opt_matches[:4])) == 4:
        stem = body[:opt_matches[0].start()].strip()
        opts = []
        for om in opt_matches[:4]:
            raw_o = re.split(r'-\s*o\s*0\s*o\s*-', om.group(2))[0]
            ot = re.sub(r'\s+', ' ', raw_o.strip())
            ot = re.sub(strip_footers, '', ot).strip()
            opts.append({
                "option_key": om.group(1).upper(),
                "option_text": ot,
                "is_correct": False,
                "sort_order": ord(om.group(1).upper()) - ord('A') + 1,
            })
        return stem, opts, "BRACKET_ALPHA"

    # Format 3: (1) ... (2) ... (3) ... (4) (NEET Standard Numeric)
    # Evaluated before paren alpha so statements '(A) and (B)' in stem are not misidentified as options
    opt_matches = list(re.finditer(r'\(([1-4])\)\s*\n?(.*?)(?=\([1-4]\)|\Z)', body, re.DOTALL))
    if len(opt_matches) >= 4 and len(set(om.group(1) for om in opt_matches[:4])) == 4:
        stem = body[:opt_matches[0].start()].strip()
        key_map = {"1": "A", "2": "B", "3": "C", "4": "D"}
        opts = []
        for om in opt_matches[:4]:
            k = key_map.get(om.group(1), "A")
            raw_o = re.split(r'-\s*o\s*0\s*o\s*-', om.group(2))[0]
            ot = re.sub(r'\s+', ' ', raw_o.strip())
            ot = re.sub(strip_footers, '', ot).strip()
            opts.append({
                "option_key": k,
                "option_text": ot,
                "is_correct": False,
                "sort_order": int(om.group(1)),
            })
        return stem, opts, "PAREN_NUMERIC_NEET"

    # Format 2: (A) ... (B) ... (C) ... (D)
    opt_matches = list(re.finditer(r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|\Z)', body, re.DOTALL))
    if len(opt_matches) >= 4 and len(set(om.group(1).upper() for om in opt_matches[:4])) == 4:
        stem = body[:opt_matches[0].start()].strip()
        opts = []
        for om in opt_matches[:4]:
            raw_o = re.split(r'-\s*o\s*0\s*o\s*-', om.group(2))[0]
            ot = re.sub(r'\s+', ' ', raw_o.strip())
            ot = re.sub(strip_footers, '', ot).strip()
            opts.append({
                "option_key": om.group(1).upper(),
                "option_text": ot,
                "is_correct": False,
                "sort_order": ord(om.group(1).upper()) - ord('A') + 1,
            })
        return stem, opts, "PAREN_ALPHA"

    # Format 4: A. ... B. ... C. ... D.
    opt_matches = list(re.finditer(r'(?:\n|\A)\s*([A-D])\.\s+(.*?)(?=(?:\n|\A)\s*[A-D]\.|\Z)', body, re.DOTALL))
    if len(opt_matches) >= 4 and len(set(om.group(1).upper() for om in opt_matches[:4])) == 4:
        stem = body[:opt_matches[0].start()].strip()
        opts = []
        for om in opt_matches[:4]:
            raw_o = re.split(r'-\s*o\s*0\s*o\s*-', om.group(2))[0]
            ot = re.sub(r'\s+', ' ', raw_o.strip())
            ot = re.sub(strip_footers, '', ot).strip()
            opts.append({
                "option_key": om.group(1).upper(),
                "option_text": ot,
                "is_correct": False,
                "sort_order": ord(om.group(1).upper()) - ord('A') + 1,
            })
        return stem, opts, "DOT_ALPHA"

    # No 4-option pattern matched -> treated as Numerical or stem without options
    return body.strip(), [], "NO_OPTIONS_NUMERICAL"


def audit_question_candidate(
    q_data: Dict[str, Any],
    paper_meta: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Applies rigorous quality gating, computes deterministic deduplication hash,
    and sets explicit question lifecycle status fields.
    """
    stem = q_data.get("question_text", "")
    q_type = q_data.get("question_type", "SCQ")
    options = q_data.get("options", [])
    warnings = []
    quarantine_status = "CLEAN"
    quarantine_reason = None
    is_malformed = False

    # 1. Stem Length Check
    if len(stem) < 15:
        is_malformed = True
        warnings.append("Stem length < 15 characters (suspiciously short or fragment)")
        quarantine_status = "FLAGGED_MALFORMED"
        quarantine_reason = "STEM_TOO_SHORT"
    elif len(stem) > 3500:
        warnings.append(f"Stem unusually long ({len(stem)} chars), potential multi-question concatenation")

    # 2. LaTeX / KaTeX Delimiter Balance
    if not validate_katex_syntax(stem):
        warnings.append("Unbalanced LaTeX math delimiters in stem")
        if quarantine_status == "CLEAN":
            quarantine_status = "FLAGGED_MALFORMED"
            quarantine_reason = "UNBALANCED_LATEX_DELIMITERS"

    # 3. Option Cardinality Compliance
    if q_type in ("SCQ", "MCQ_MULTI", "MATCH"):
        if len(options) != 4:
            is_malformed = True
            warnings.append(f"Question type {q_type} expects 4 options, found {len(options)}")
            quarantine_status = "FLAGGED_MALFORMED"
            quarantine_reason = f"OPTION_COUNT_MISMATCH_{len(options)}"
        else:
            empty_keys = [opt.get("option_key") for opt in options if len(opt.get("option_text", "").strip()) == 0]
            if empty_keys:
                is_malformed = True
                warnings.append(f"Empty option text for options {empty_keys} (requires graphic/drawing extraction)")
                if quarantine_status == "CLEAN":
                    quarantine_status = "FLAGGED_MALFORMED"
                    quarantine_reason = "EMPTY_OPTION_TEXT"
    elif q_type == "NUMERICAL":
        if len(options) > 0:
            warnings.append(f"NUMERICAL question contains {len(options)} options")

    # 4. Instruction Leakage Detection
    leakage_terms = ["darken the bubble", "optical response sheet", "space for rough work", "office copy carefully"]
    for term in leakage_terms:
        if term in stem.lower():
            warnings.append(f"Possible instruction leakage in stem ('{term}')")
            quarantine_status = "FLAGGED_MALFORMED"
            quarantine_reason = "INSTRUCTION_LEAKAGE"

    # 5. Compute Deterministic Content Hash
    content_hash = compute_content_hash(stem, options, q_data.get("correct_answer_raw"))

    # 6. Lifecycle & Scoring Eligibility Rules
    # Rule: Raw extracted questions are NEVER eligible for automatic scoring
    # until official answer keys have been reconciled.
    eligibility = "INELIGIBLE_UNVERIFIED_KEY"
    if quarantine_status != "CLEAN":
        eligibility = "INELIGIBLE_MALFORMED"

    q_data.update({
        "content_hash": content_hash,
        "quarantine_status": quarantine_status,
        "quarantine_reason": quarantine_reason,
        "eligibility_for_scoring": eligibility,
        "verification_status": "EXTRACTED_PENDING_REVIEW",
        "answer_verification_status": "UNVERIFIED",
        "rights_status": "PENDING_LEGAL_REVIEW",
        "publish_permission": "FORBIDDEN",
        "official_status": "REGULAR",
        "is_malformed": is_malformed,
        "warnings": warnings,
        "needs_manual_review": bool(warnings or is_malformed),
        "extraction_method": "DIGITAL_PYMUPDF_V2",
    })
    return q_data


def parse_pdf_text_questions(
    pdf_path: str,
    max_pages: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Extracts structured competitive questions from a digital text-based PDF paper.
    Excludes cover pages, preserves mathematical notation, tracks section types,
    and returns questions with complete metadata and quality audit tags.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    paper_meta = extract_paper_metadata(pdf_path)
    doc = pymupdf.open(pdf_path)
    questions = []
    pages_to_read = min(len(doc), max_pages) if max_pages else len(doc)

    section_state = {
        "subject": "Physics",
        "section": "SECTION 1",
        "question_type": "SCQ",
        "evaluation_policy": "STANDARD_SCQ",
    }

    seen_q_numbers = set()

    for page_idx in range(pages_to_read):
        page_num = page_idx + 1
        text = doc[page_idx].get_text()

        # Step 1: Detect and Skip Pure Cover / General Instruction Pages
        is_cover, reason = is_cover_or_instruction_page(text, page_num)
        if is_cover:
            logger.info("Skipping Page %d in %s: %s", page_num, os.path.basename(pdf_path), reason)
            continue

        # Step 2: Track Section and Question Type Context
        section_state = detect_section_metadata(text, section_state)

        # Step 3: Segment Questions based on Exam Pattern
        # Check for JEE Pattern (Q.1, Q. 2, Q1)
        jee_splits = re.split(r'(?:\n|\A)\s*Q\.?\s*(\d{1,3})[\.\s:]\s*', text)
        neet_splits = re.split(r'(?:\n|\A)\s*(\d{1,3})\.\s*\n', text)

        is_jee_page = len(jee_splits) > 1 and "JEE" in paper_meta["exam_code"]
        is_neet_page = len(neet_splits) > 1 and not is_jee_page

        if is_jee_page:
            for i in range(1, len(jee_splits), 2):
                q_num = int(jee_splits[i])
                raw_body = jee_splits[i + 1]

                stem, options, opt_format = parse_options_flexible(raw_body)
                clean_stem = clean_question_text(stem)

                # Determine question type based on section instructions + options
                if section_state["question_type"] == "MCQ_MULTI" and len(options) == 4:
                    q_type = "MCQ_MULTI"
                elif section_state["question_type"] == "NUMERICAL" or len(options) == 0:
                    q_type = "NUMERICAL"
                elif section_state["question_type"] == "MATCH" and len(options) == 4:
                    q_type = "MATCH"
                else:
                    q_type = "SCQ" if len(options) == 4 else "NUMERICAL"

                q_entry = {
                    "paper_question_number": q_num,
                    "question_text": clean_stem,
                    "question_type": q_type,
                    "options": options,
                    "subject": section_state["subject"],
                    "source_page": page_num,
                    "source_document": os.path.basename(pdf_path),
                    "source_pdf_hash": paper_meta["source_pdf_hash"],
                    "evaluation_policy": section_state["evaluation_policy"],
                    "numerical_precision_type": "INTEGER" if section_state["question_type"] == "NUMERICAL" else "NOT_APPLICABLE",
                    "numerical_min_val": 0.0 if q_type == "NUMERICAL" else None,
                    "numerical_max_val": 9.0 if q_type == "NUMERICAL" else None,
                    "numerical_tolerance_epsilon": 0.01 if q_type == "NUMERICAL" else None,
                    "difficulty_tier": "HARD" if paper_meta["exam_code"] == "JEE_ADVANCED" else "MEDIUM",
                    "cognitive_level": "ANALYZING" if paper_meta["exam_code"] == "JEE_ADVANCED" else "APPLYING",
                    "estimated_seconds": 180 if q_type in ("MCQ_MULTI", "NUMERICAL") else 120,
                }

                audited = audit_question_candidate(q_entry, paper_meta)
                if q_num in seen_q_numbers:
                    audited["warnings"].append(f"Duplicate question number Q.{q_num} on page {page_num}")
                seen_q_numbers.add(q_num)
                questions.append(audited)

        elif is_neet_page:
            for i in range(1, len(neet_splits), 2):
                q_num = int(neet_splits[i])
                raw_body = neet_splits[i + 1]

                stem, options, opt_format = parse_options_flexible(raw_body)
                clean_stem = clean_question_text(stem)

                # NEET Standard Subject Bounds
                # Pre-2021: 180 questions (45 Phy, 45 Chem, 90 Bio)
                # 2021+: 200 questions (50 Phy, 50 Chem, 100 Bio)
                if q_num <= 50:
                    subj = "Physics"
                elif q_num <= 100:
                    subj = "Chemistry"
                else:
                    subj = "Biology"

                q_entry = {
                    "paper_question_number": q_num,
                    "question_text": clean_stem,
                    "question_type": "SCQ" if len(options) == 4 else ("NUMERICAL" if len(options) == 0 else "SCQ"),
                    "options": options,
                    "subject": subj,
                    "source_page": page_num,
                    "source_document": os.path.basename(pdf_path),
                    "source_pdf_hash": paper_meta["source_pdf_hash"],
                    "evaluation_policy": "NEET_STANDARD_SCQ",
                    "numerical_precision_type": "NOT_APPLICABLE",
                    "difficulty_tier": "MEDIUM",
                    "cognitive_level": "APPLYING",
                    "estimated_seconds": 60,
                }

                audited = audit_question_candidate(q_entry, paper_meta)
                if q_num in seen_q_numbers:
                    audited["warnings"].append(f"Duplicate question number Q.{q_num} on page {page_num}")
                seen_q_numbers.add(q_num)
                questions.append(audited)

    doc.close()
    return questions


def dry_run_audit_paper(pdf_path: str) -> Dict[str, Any]:
    """
    Performs an isolated extraction audit of a single paper without touching any database.
    Produces counts of candidates, structured questions, option types, and warnings.
    """
    meta = extract_paper_metadata(pdf_path)
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    pages_with_text = sum(1 for p in doc if len(p.get_text().strip()) > 30)
    is_scanned = (pages_with_text / max(1, total_pages)) < 0.3
    doc.close()

    if is_scanned:
        return {
            "filename": os.path.basename(pdf_path),
            "paper_identifier": meta["paper_identifier"],
            "exam_code": meta["exam_code"],
            "exam_year": meta["exam_year"],
            "session": meta["session_or_shift"],
            "language": meta["language"],
            "total_pages": total_pages,
            "extractable_pages": pages_with_text,
            "is_scanned": True,
            "classification": "SCANNED_REQUIRES_OCR",
            "candidate_count": 0,
            "structured_count": 0,
            "scq_count": 0,
            "mcq_multi_count": 0,
            "numerical_count": 0,
            "malformed_count": 0,
            "questions_requiring_manual_review": 0,
            "sha256": meta["source_pdf_hash"],
            "extraction_warnings": ["Zero or insufficient vector text; paper is scanned raster images"],
        }

    raw_questions = parse_pdf_text_questions(pdf_path)
    scq_c = sum(1 for q in raw_questions if q["question_type"] == "SCQ")
    multi_c = sum(1 for q in raw_questions if q["question_type"] == "MCQ_MULTI")
    num_c = sum(1 for q in raw_questions if q["question_type"] == "NUMERICAL")
    malformed_c = sum(1 for q in raw_questions if q.get("is_malformed"))
    review_c = sum(1 for q in raw_questions if q.get("needs_manual_review"))

    all_warnings = []
    for q in raw_questions:
        for w in q.get("warnings", []):
            all_warnings.append(f"Q.{q['paper_question_number']} (p.{q['source_page']}): {w}")

    return {
        "filename": os.path.basename(pdf_path),
        "paper_identifier": meta["paper_identifier"],
        "exam_code": meta["exam_code"],
        "exam_year": meta["exam_year"],
        "session": meta["session_or_shift"],
        "language": meta["language"],
        "total_pages": total_pages,
        "extractable_pages": pages_with_text,
        "is_scanned": False,
        "classification": "DIGITAL_EXTRACTABLE",
        "candidate_count": len(raw_questions),
        "structured_count": len(raw_questions) - malformed_c,
        "scq_count": scq_c,
        "mcq_multi_count": multi_c,
        "numerical_count": num_c,
        "malformed_count": malformed_c,
        "questions_requiring_manual_review": review_c,
        "sha256": meta["source_pdf_hash"],
        "extraction_warnings": all_warnings[:15],
    }


def find_matching_topic_id(db: Session, subject_name: str, question_text: str) -> Optional[str]:
    """
    Maps question to an active Standards 11 or 12 topic based on subject and keyword affinity.
    """
    text_lower = question_text.lower()
    candidate_topics = (
        db.query(Topic)
        .join(Chapter, Chapter.id == Topic.chapter_id)
        .join(Subject, Subject.id == Chapter.subject_id)
        .filter(Subject.name.ilike(f"%{subject_name}%"), Topic.is_active == True)
        .all()
    )

    best_match_id = None
    best_score = 0

    for t in candidate_topics:
        t_words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t.title or '')]
        score = sum(1 for w in t_words if w in text_lower)
        if score > best_score:
            best_score = score
            best_match_id = t.id

    if not best_match_id and candidate_topics:
        best_match_id = candidate_topics[0].id

    return best_match_id


def ingest_competitive_paper(
    db: Session,
    pdf_path: str,
    max_pages: Optional[int] = None,
    dry_run: bool = True,  # Defaults strictly to True to prevent accidental persistent writes
) -> Dict[str, Any]:
    """
    Parses and ingests an authentic competitive paper and its questions idempotently.
    Defaults to dry_run=True.
    """
    paper_meta = extract_paper_metadata(pdf_path)
    raw_questions = parse_pdf_text_questions(pdf_path, max_pages=max_pages)

    for q in raw_questions:
        topic_id = find_matching_topic_id(db, q.get("subject", "Physics"), q["question_text"])
        q["topic_id"] = topic_id

    ingestion_service = QuestionIngestionService(db)
    result = ingestion_service.ingest_paper_batch(
        paper_info=paper_meta,
        questions_data=raw_questions,
        dry_run=dry_run,
    )
    if not dry_run:
        db.commit()

    return {
        "paper_identifier": paper_meta["paper_identifier"],
        "exam_code": paper_meta["exam_code"],
        "exam_year": paper_meta["exam_year"],
        "total_extracted": len(raw_questions),
        "ingestion_result": result,
    }
