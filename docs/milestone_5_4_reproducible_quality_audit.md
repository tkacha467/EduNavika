# EduNavika — Milestone 5.4: Reproducible NEET 2021 Question Quality Validation

**Role:** Senior ML/Data-Ingestion Architect & Assessment QA Engineer  
**Exam:** NEET (UG) 2021  
**Conducting Authority:** National Testing Agency (NTA)  
**Authoritative Final Answer Key Document:** `docs/reference/Notice_20211101205130.pdf`  
- **SHA-256:** `838e0ba080eb6b9639f12a1dcfb7f36cd8fe80dd5be11ee0be6d725e4c6f3ca9`  
- **File Size:** 38,417 bytes  
- **Publication Date:** 01.11.2021 (Exam Date: 12.09.2021)  
**Target Question Paper Document:** `GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf`  
- **SHA-256:** `e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a`  
- **Total Pages:** 28 pages  
**Audited Booklet Code:** `M4` (Pages 2–27 verified)  
**Final Verdict:** **PASS WITH LIMITATIONS** (100% reproducible; persistent database strictly 0 records)

---

## 1. Executive Summary

Milestone 5.3 reported that 200 NEET 2021 questions had been reconciled against the official NTA Booklet M4 answer key, claiming that 179 questions were provisionally eligible for scoring and 21 were quarantined.

Milestone 5.4 was commissioned to independently establish whether these findings were reproducible from repository-native code or were artifacts of scratch scripts, and to resolve a documented discrepancy where the detailed table listed Question 50 as quarantined despite conflicting summary counts.

### Key Audit Conclusions
1. **Reproducibility Established:** All ad hoc scratch dependencies have been replaced by a deterministic repository audit script (`scripts/audit_neet_2021_quality.py`). The authoritative NTA answer-key document is permanently stored and verified in `docs/reference/Notice_20211101205130.pdf`.
2. **The 21-Question Discrepancy Resolved from Evidence:**
   - The Milestone 5.3 script used an over-aggressive regex (`\d{1,2}`) designed to strip standalone page numbers.
   - That regex unintentionally stripped vertical numbers from 8 valid questions (e.g. Q8 lenses: `25`, `15`, `50`, `30`; Q50 moment of inertia fractions: `3/4`, `7/8`, `1/4`, `1/8`; Q52: `7`, `5`, `2`, `3`; Q168: `8`, `16`, `4`, `32`), corrupting their options and causing them to be falsely classified as "empty graphical options".
   - **Authentic Measured Counts:**
     - **9 questions** have genuine blank options because options are vector drawing diagrams in the PDF: **Q26, Q38, Q60, Q62, Q63, Q79, Q82, Q88, Q99**.
     - **4 questions** have hard diagram dependencies in their stems (circuits/apparatus): **Q4, Q20, Q40, Q49** (with Q38 overlapping both).
     - **Total Distinct Quarantined Questions:** Exactly **13 questions** (not 21).
     - **Total Verified, Solvable & Scoring-Eligible Questions:** Exactly **187 questions (93.5%)** (not 179).
3. **Semantic Fidelity Analysis:** Visual inspection of PDF pages using PyMuPDF vector drawing inspection revealed that diagram/structure areas contain up to 209 vector drawing path operators per page rather than embedded raster images. Pure text extraction extracts glyphs but cannot capture vector drawings.
4. **Zero Database Ingestion:** Canonical database `D:\EduNavika\edunavika.db` was audited before, during, and after execution, remaining strictly at **0 competitive records** (`exam_papers = 0`, `questions = 0`, `question_options = 0`, `question_verification_logs = 0`).

---

## 2. Task 1 — Verification of Reproducibility

We audited the Milestone 5.3 workflow to separate reproducible codebase components from ad hoc scripts:

| Component / Artifact | Milestone 5.3 Status | Milestone 5.4 Hardened Repository Status |
| :--- | :--- | :--- |
| **Official NTA Key PDF** | Ephemeral scratch path (`.tempmediaStorage/ef726d...`) | Documented repo path `docs/reference/Notice_20211101205130.pdf` (configurable via `NTA_NEET_2021_ANSWER_KEY_PATH`). Fails explicitly if missing. |
| **Audit Script** | Ad hoc script in scratch (`poc_neet_2021_reconciliation.py`) | Deterministic CLI script: [`scripts/audit_neet_2021_quality.py`](file:///d:/EduNavika/scripts/audit_neet_2021_quality.py). |
| **Audit Data Artifacts** | Saved in scratch directories | Saved to standard repo location: `data/processed/neet_2021_quality_audit.json` and `.csv`. |
| **Option Extraction Logic** | In-script custom functions | Integrated into production [`competitive_paper_parser.py`](file:///d:/EduNavika/backend/app/ingestion/competitive_paper_parser.py). |
| **Automated Tests** | Isolated scratch test script | Fully integrated test suite: [`backend/tests/test_neet_2021_quality_audit.py`](file:///d:/EduNavika/backend/tests/test_neet_2021_quality_audit.py). |

### Reproducibility Command
The audit can be executed from a clean repository checkout with:
```bash
python scripts/audit_neet_2021_quality.py
```
Outputs are generated deterministically and match byte-for-byte on repeated runs.

---

## 3. Task 2 — Reconcile All 200 Questions

The deterministic auditor extracts exactly 200 questions (numbered strictly 1 through 200) and matches each against Page 13 of the NTA Notice.

### Blueprint Summary Table

| Subject | Section | Question Range | Item Count | Scoring Eligible | Quarantined (Visual Assets) | Option Monotonicity |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Physics** | Section A | 1 – 35 | 35 | 32 | 3 (Q4, Q20, Q26) | 100% $(1)-(4)$ |
| **Physics** | Section B | 36 – 50 | 15 | 12 | 3 (Q38, Q40, Q49) | 100% $(1)-(4)$ |
| **Chemistry** | Section A | 51 – 85 | 35 | 31 | 4 (Q60, Q62, Q63, Q79) | 100% $(1)-(4)$ |
| **Chemistry** | Section B | 86 – 100 | 15 | 12 | 3 (Q82, Q88, Q99) | 100% $(1)-(4)$ |
| **Botany** | Section A | 101 – 135 | 35 | 35 | 0 | 100% $(1)-(4)$ |
| **Botany** | Section B | 136 – 150 | 15 | 15 | 0 | 100% $(1)-(4)$ |
| **Zoology** | Section A | 151 – 185 | 35 | 35 | 0 | 100% $(1)-(4)$ |
| **Zoology** | Section B | 186 – 200 | 15 | 15 | 0 | 100% $(1)-(4)$ |
| **Total** | — | **1 – 200** | **200** | **187 (93.5%)** | **13 (6.5%)** | **100% Monotonic** |

Every question record in `data/processed/neet_2021_quality_audit.json` contains:
- `exam_code`, `exam_year`, `booklet_code` (`M4`)
- `question_number`, `subject`, `section`
- `raw_stem`, `normalized_stem`
- `option_A_raw` .. `option_D_raw` and normalized equivalents
- `official_raw_answer`, `normalized_answer`, `option_mapping` (`1->A, 2->B, 3->C, 4->D`)
- `source_pdf_file`, `source_pdf_page`, `source_pdf_hash`
- `reconciliation_status`, `scoring_eligibility`, `eligibility_reason`, `manual_review_status`

---

## 4. Task 3 — Discrepancy Resolution & Quarantined Question Analysis

### Root Cause of the 21 vs 17 vs 13 Discrepancy
In Milestone 5.3, a cleaning regex attempted to strip standalone page numbers:
```python
# Defective Milestone 5.3 pattern:
cleaned = re.sub(r'(?m)^\s*(?:SPACE FOR ROUGH WORK|M4|\d{1,2})\s*$', '', text)
```
Because `\d{1,2}` matches any standalone one- or two-digit number, vertical mathematical fractions and single-number options were stripped:
- **Q8:** Lenses distance options `25`, `15`, `50`, `30` were erased.
- **Q50:** Moment of inertia options `3\n4` ($\frac{3}{4}$), `7\n8` ($\frac{7}{8}$), `1\n4` ($\frac{1}{4}$), `1\n8` ($\frac{1}{8}$) were erased.
- **Q52:** Bravais lattice options `7`, `5`, `2`, `3` were erased.
- **Q168:** Chromosome count options `8`, `16`, `4`, `32` were erased.

This corrupted 8 legitimate questions into appearing "empty". The author of Milestone 5.3 saw 17 empty questions (9 genuine + 8 corrupted) plus 4 diagram questions, yielding 21, and listed Q50 in the table.

### Corrected, Verified Quarantined Categories

#### Category 1: Blank Graphical Options (9 Questions)
Options are vector drawings in the PDF; raw text extraction yields empty strings.
1. **Q26 (Physics Sec A):** Magnetic field $B(r)$ vs $r$ graphs for cylindrical cable. Options $(1)-(4)$ are vector graphs.
2. **Q38 (Physics Sec B):** Logic gate output waveform. Options $(1)-(4)$ are digital pulse graphs.
3. **Q60 (Chemistry Sec A):** Enthalpy profile curves. Options $(1)-(4)$ are potential energy curves.
4. **Q62 (Chemistry Sec A):** Alcohol dehydration reaction products. Options $(1)-(4)$ are organic structural formulas.
5. **Q63 (Chemistry Sec A):** Boyle's law $P$ vs $1/V$ graphs. Options $(1)-(4)$ are isotherm plots.
6. **Q79 (Chemistry Sec A):** Organic substitution product. Options $(1)-(4)$ are chemical structure drawings.
7. **Q82 (Chemistry Sec B):** Structure of 2,6-Dimethyl-dec-4-ene. Options $(1)-(4)$ are skeletal hydrocarbon structures.
8. **Q88 (Chemistry Sec B):** Multistep benzene reaction product. Options $(1)-(4)$ are substituted aromatic structures.
9. **Q99 (Chemistry Sec B):** Intermediate structure in organic synthesis. Options $(1)-(4)$ are organic structures.

#### Category 2: Hard Stem Diagram Dependencies (4 Questions)
Stems reference circuit or apparatus figures that are missing from pure text:
1. **Q4 (Physics Sec A):** *"The equivalent capacitance of the combination shown in the figure is :"* (Missing capacitor bridge).
2. **Q20 (Physics Sec A):** *"connected in series to an ac source of potential difference 'V' volts as shown in figure."* (Missing LCR schematic).
3. **Q40 (Physics Sec B):** *"balanced on a wedge placed at 40 cm mark... as shown in the figure."* (Missing lever balance illustration).
4. **Q49 (Physics Sec B):** *"Three resistors having resistances r1, r2 and r3 are connected as shown in the given circuit."* (Missing parallel-series circuit).

*(Note: Q38 has both a missing circuit diagram in the stem and blank waveform options, cataloged under Category 1).*

**Total Non-Overlapping Quarantined Questions:** Exactly **13 questions** (`9 + 4 = 13`).

---

## 5. Task 4 — Semantic Fidelity & High-Risk Visual Inspection

We rendered high-risk pages to 150 DPI PNGs (`scratch/page_renders/`) and inspected their vector graphics using PyMuPDF:

```
Page 2  (Q1-Q5):    0 raster images,  68 vector drawing paths
Page 4  (Q18-Q21):  0 raster images, 102 vector drawing paths
Page 5  (Q24-Q27):  0 raster images,  66 vector drawing paths
Page 7  (Q36-Q38):  0 raster images, 183 vector drawing paths
Page 9  (Q48-Q50):  0 raster images,  47 vector drawing paths
Page 11 (Q59-Q62):  0 raster images, 209 vector drawing paths
Page 25 (Q195-Q197):0 raster images,  27 vector drawing paths
Page 26 (Q198-Q200):0 raster images,   0 vector drawing paths
```

### Key Semantic Observations
1. **Absence of Raster Images:** The NTA PDF does not contain embedded JPEGs or PNGs. All diagrams and chemical structures are drawn with PDF vector line/curve operators (`stroke`, `fill`).
2. **Terminal Footer Stripping Verified:**
   - In Q35, `Section - B (Physics)` was stripped from Option 4.
   - In Q200, `- o 0 o -` (the NTA official end-of-booklet marker) and subsequent rough work pages (Pages 27–28) were cleanly partitioned, leaving Option 4 as `(b) and (c) are correct`.
3. **Mathematical Fraction Preservation:**
   - Q50's two-line fractions $\frac{3}{4}$, $\frac{7}{8}$, $\frac{1}{4}$, $\frac{1}{8}$ are normalized as `3/4`, `7/8`, `1/4`, `1/8`.
4. **Font Glyph Encoding Anomalies:**
   - 56 questions exhibit minor font mapping replacements (e.g. `?` replacing $\Omega$ for Ohms, $\mu$ for micro, or smart quotes). These do not prevent human comprehension of text-only questions, but represent an opportunity for KaTeX normalization in Milestone 6.

---

## 6. Task 5 — Hardened Regression Test Suite

We implemented [`backend/tests/test_neet_2021_quality_audit.py`](file:///d:/EduNavika/backend/tests/test_neet_2021_quality_audit.py) to validate quality gating:
1. `test_real_neet_pdf_integration`: Executes real parser against real source PDFs, checking 200 questions, strict 1..200 numbering, 187 clean questions, 13 quarantined questions, Q50 fraction normalization, and Q200 footer stripping.
2. `test_reproducibility_deterministic_outputs`: Confirms repeated audit runs generate identical records.
3. `test_missing_question_fails_audit`: Confirms manifest omission triggers unverified status.
4. `test_booklet_mismatch_fails_safely`: Verifies invalid booklet codes raise explicit `ValueError`.
5. `test_missing_manifest_file_fails_explicitly`: Confirms missing key files raise `FileNotFoundError`.
6. `test_persistent_db_isolation_guard`: Confirms `conftest.py` security listener immediately halts any test attempting to connect to `edunavika.db`.

### Test Suite Execution
```bash
pytest backend/tests/test_neet_2021_quality_audit.py
# Output: 6 passed in 1.71s
```
Full competitive assessment test suite:
```bash
pytest backend/tests/test_answer_key_reconciliation.py \
       backend/tests/test_digital_pyq_pipeline.py \
       backend/tests/test_neet_2021_independent_audit.py \
       backend/tests/test_neet_2021_quality_audit.py \
       backend/tests/test_pilot_ingestion.py
# Output: 39 passed in 4.87s
```

---

## 7. Deliverables & Artifact Inventory

1. **Audit Script:** [`scripts/audit_neet_2021_quality.py`](file:///d:/EduNavika/scripts/audit_neet_2021_quality.py)
2. **Authoritative Key Document:** [`docs/reference/Notice_20211101205130.pdf`](file:///d:/EduNavika/docs/reference/Notice_20211101205130.pdf)
3. **Machine-Readable Outputs:**
   - [`data/processed/neet_2021_quality_audit.json`](file:///d:/EduNavika/data/processed/neet_2021_quality_audit.json)
   - [`data/processed/neet_2021_quality_audit.csv`](file:///d:/EduNavika/data/processed/neet_2021_quality_audit.csv)
   - [`data/processed/neet_2021_audit_summary.json`](file:///d:/EduNavika/data/processed/neet_2021_audit_summary.json)
4. **Regression Tests:** [`backend/tests/test_neet_2021_quality_audit.py`](file:///d:/EduNavika/backend/tests/test_neet_2021_quality_audit.py)
5. **Audit Report:** [`docs/milestone_5_4_reproducible_quality_audit.md`](file:///d:/EduNavika/docs/milestone_5_4_reproducible_quality_audit.md)
6. **Database Integrity Verification:** Confirmed 0 competitive records in [edunavika.db](file:///d:/EduNavika/edunavika.db).

---

## 8. Final Verdict & Acceptance Checklist

| Acceptance Criterion | Result | Evidence |
| :--- | :---: | :--- |
| **1. Every expected question accounted for** | **PASS** | Exactly 200 questions (1–200) parsed without gaps or duplicates. |
| **2. Booklet traceability** | **PASS** | Booklet M4 verified on all paper pages and NTA Notice Page 13. |
| **3. 21-Question discrepancy resolved** | **PASS** | Over-stripping regex corrected; authentic counts are 13 quarantined (9 blank options, 4 hard diagrams) and 187 eligible. |
| **4. Structural integrity checks** | **PASS** | Monotonic option ordering $(1) < (2) < (3) < (4)$ verified across 100% of items. |
| **5. Semantic verification distinguished** | **PASS** | Visual vector dependencies isolated from text-only solvable items. |
| **6. Incomplete questions ineligible** | **PASS** | All 13 visually incomplete questions safely marked `INELIGIBLE_FOR_SCORING`. |
| **7. Persistent DB unchanged** | **PASS** | Canonical `edunavika.db` strictly 0 records across all competitive tables. |
| **8. Deterministic reproducibility** | **PASS** | Script runs reproducibly from repository reference files. |

### Final Audit Verdict: **PASS WITH LIMITATIONS**

The NEET UG 2021 digital paper extraction and reconciliation pipeline is **100% reproducible, verified, and safe**. Exactly **187 questions** are confirmed text-complete and eligible for scoring. Exactly **13 questions** remain safely quarantined awaiting a future vector-graphic asset extraction milestone. Zero database records were ingested.
