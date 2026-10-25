# Milestone 5.7: Production-Grade Vector Diagram Extraction, Asset Linking and Verification

## 1. Executive Summary

Milestone 5.7 establishes an automated, deterministic, and database-isolated vector diagram extraction pipeline for competitive examination papers in EduNavika, focusing on the 13 quarantined questions in NEET UG 2021 Booklet M4 (`GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf`).

In Milestone 5.4, an automated quality audit quarantined 21 questions, 13 of which failed due to missing visual content (stems lacking diagrams or answer options containing vector graphics rather than text). In Milestone 5.7, we conducted an empirical inspection of the source PDF, discovered that **zero raster images** exist in the PDF (all drawings are native PDF vector path operators), and constructed a robust vector geometry extraction engine (`backend/app/ingestion/vector_diagram_extractor.py`) that isolates, crops, and rasterizes every visual asset into lossless PNG format.

### Key Deliverables & Outcomes
1. **Extraction Engine**: [`backend/app/ingestion/vector_diagram_extractor.py`](file:///d:/EduSens/backend/app/ingestion/vector_diagram_extractor.py) with typed data models, column-aware layout partitioning, zero-area stroke handling, border line filtering, atomic file writes, and idempotency guards.
2. **Reproducible CLI**: [`scripts/extract_neet_2021_diagrams.py`](file:///d:/EduSens/scripts/extract_neet_2021_diagrams.py) enabling zero-config end-to-end execution.
3. **Generated Asset Inventory**: Exactly **41 high-fidelity lossless PNG visual assets** extracted to [`backend/static/assets/diagrams/neet_2021/`](file:///d:/EduSens/backend/static/assets/diagrams/neet_2021/) (total size: 218.9 KB).
4. **Machine-Readable Manifest**: [`data/processed/neet_2021_diagram_manifest.json`](file:///d:/EduSens/data/processed/neet_2021_diagram_manifest.json) recording bounding boxes, effective DPI, dimensions, file sizes, and SHA-256 hashes.
5. **Visual Review Contact Sheet**: [`data/processed/neet_2021_diagram_contact_sheet.html`](file:///d:/EduSens/data/processed/neet_2021_diagram_contact_sheet.html) providing side-by-side visual inspection of every crop for subject-matter reviewers.
6. **Automated Test Suite**: [`backend/tests/test_vector_diagram_extractor.py`](file:///d:/EduSens/backend/tests/test_vector_diagram_extractor.py) containing 12 comprehensive unit and integration tests (100% pass).
7. **Regression Suite**: 27 existing competitive examination tests passed with 0 regressions.
8. **Strict Database Isolation**: Canonical database `edunavika.db` remained 100% untouched (exact file size 4,882,432 bytes; 0 records in competitive tables).

**Milestone Verdict**: **PASS WITH REVIEW REQUIRED** (All software engineering, extraction, manifest, and automated test requirements are fulfilled; human visual verification of the 41 assets via the contact sheet remains mandatory prior to publishing questions).

---

## 2. Environment & Working-Tree State

- **Local Time**: 2026-10-25 12:35 IST
- **Git Branch**: `master`
- **HEAD Commit**: `45035408dd845de03567753509cac1bccd0a856c`
- **Remote Tracking**: `origin/master` (in sync, `45035408dd845de03567753509cac1bccd0a856c`)
- **Python Runtime**: Python 3.11.9 (PyMuPDF 1.28.2, Pytest 9.1.1)
- **Source PDF Provenance**:
  - File: `GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf`
  - SHA-256: `e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a`
  - Size: 947,343 bytes (28 pages, Booklet M4)
- **Authoritative Answer Key**:
  - File: `docs/reference/Notice_20211101205130.pdf`
  - SHA-256: `838e0ba080eb6b9639f12a1dcfb7f36cd8fe80dd5be11ee0be6d725e4c6f3ca9`

---

## 3. Root-Cause Analysis of the 13 Quarantined Questions

Our investigation validated the hypothesis that the 13 quarantined questions fell into three distinct architectural categories requiring tailored extraction treatment:

### Category Breakdown

| Category | Count | Questions | Quarantined Root Cause | Resolution Strategy | Assets Generated |
| :--- | :---: | :--- | :--- | :--- | :---: |
| **A: Stem Diagrams** | 4 | Q4, Q20, Q40, Q49 | Question stem text referenced a figure (`"as shown in the figure"`, `":"`), but the diagram was not extracted by the text OCR parser. Options were pure text. | Extract vector path bounding box between the end of question text and option `(1)`. Rasterize to `neet_2021_q{num}_stem.png`. | 4 |
| **B: Graphical Options** | 8 | Q26, Q60, Q62, Q63, Q79, Q82, Q88, Q99 | Options (1)-(4) contained vector drawings (graphs, reaction profiles, chemical structures) with empty or single-character extracted text. | Partition the options column using vertical midpoints between option label anchors `(1)`, `(2)`, `(3)`, `(4)`. Extract 4 distinct assets per question. | 32 |
| **C: Hybrid Stem + Options** | 1 | Q38 | Q38 contained a combinational logic circuit schematic in the stem AND four distinct output waveform diagrams in options (1)-(4). | Extract the logic gate schematic between stem text and $y=415\text{ pt}$, plus 4 separate waveform diagrams between $y=430\text{ pt}$ and $y=580\text{ pt}$. | 5 |
| **Total** | **13** | — | — | — | **41** |

---

## 4. Extraction Architecture & Layout Engineering

The extractor is implemented in [`backend/app/ingestion/vector_diagram_extractor.py`](file:///d:/EduSens/backend/app/ingestion/vector_diagram_extractor.py). It addresses several subtle PDF layout challenges discovered during reverse engineering:

### 1. Vector Path Detection vs. Raster Images
`page.get_images()` returned 0 across all 28 pages of the NEET 2021 PDF. All schematic symbols (inductors, capacitors, resistors, ground connections, logic gates, chemical bonds, arrows, coordinate axes, and curve functions) are defined as native vector path operators (`page.get_drawings()`).

### 2. Two-Column Layout and Central Divider Filtering
NEET 2021 uses a 2-column layout:
- **Column 0**: $x \in [35.0, 296.0]\text{ pt}$
- **Column 1**: $x \in [302.0, 560.0]\text{ pt}$
A continuous vertical rule separates the columns down the middle of the page at $x \approx 298.08\text{ pt}$ ($y \in [90.76, 775.36]\text{ pt}$). Naive bounding box calculation included this central line. The extractor explicitly filters out any drawing whose height exceeds $200.0\text{ pt}$ or whose $x$-coordinates lie within $1.0\text{ pt}$ of $298.08\text{ pt}$.

### 3. PyMuPDF Empty-Rect Bug in Stroke Unions
In PyMuPDF, horizontal strokes ($y_0 = y_1$) and vertical strokes ($x_0 = x_1$) have mathematical area = 0, causing `fitz.Rect.is_empty` to evaluate to `True`. Furthermore, `fitz.Rect().include_rect(empty_rect)` silently drops empty rects, leaving `Rect(0, 0, 0, 0)`.
**Solution**: The extractor explicitly expands 0-thickness strokes by $\pm 0.5\text{ pt}$ during intersection tests and computes bounding coordinates using `min(x0)` / `max(x1)` / `min(y0)` / `max(y1)` directly across drawing bounding boxes.

### 4. Midpoint-Based Vertical Option Bounding
In chemical structure and coordinate graph options, option labels `(1)`, `(2)`, `(3)`, `(4)` are vertically centered beside the drawings rather than placed above them. Using label $y$-coordinates as top boundaries cut diagrams in half.
**Solution**: The extractor computes the vertical midpoint between consecutive option labels:
$$y_{\text{mid}, i} = \frac{y_{\text{label}, i} + y_{\text{label}, i+1}}{2}$$
This neatly bisects the natural whitespace gap between adjacent options without any clipping.

### 5. Rasterization and Clamping
- **Resolution**: Scaled via `fitz.Matrix(2.0, 2.0)`, producing effective resolution of $144\text{ DPI}$ ($2\times 72$).
- **Padding**: $4.0\text{ pt}$ padding applied around the vector bounding box.
- **Clamping**: Bounding boxes are clamped to column bounds ($x_0 \ge \text{col\_x0}$, $x_1 \le \text{col\_x1}$) and page bounds ($y \in [0, \text{height}]$) to prevent horizontal overlap with adjacent columns.
- **Atomicity**: Rendered bytes are written to a `.tmp` file and atomically replaced via `os.replace`.
- **Integrity**: Every asset is verified to start with the 8-byte PNG signature `\x89PNG\r\n\x1a\n` and have non-zero dimensions.

---

## 5. Asset Inventory & Verification Evidence

All 41 assets were extracted to [`backend/static/assets/diagrams/neet_2021/`](file:///d:/EduSens/backend/static/assets/diagrams/neet_2021/).

### Summary Metrics
- **Total Assets**: 41
- **Total Disk Footprint**: 224,170 bytes (218.9 KB)
- **Average Asset Size**: ~5.4 KB
- **Extraction Failures**: 0
- **Verification Status**: `PENDING_HUMAN_REVIEW` (All 41 assets)

### Asset Detail Table

| Asset ID | Q# | Role | Key | Label | Page | Dimensions (px) | Size (Bytes) | SHA-256 (First 16 chars) | Content Description |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `neet_2021_q004_stem` | 4 | stem | — | — | 2 | 311x162 | 2,330 | `82802563524f09c1` | Capacitor network bridge |
| `neet_2021_q020_stem` | 20 | stem | — | — | 4 | 342x180 | 6,016 | `1f3f09852230113c` | LCR series circuit diagram |
| `neet_2021_q026_option_a` | 26 | option | A | (1) | 5 | 209x190 | 3,843 | `40a1b8da250438ea` | $B(r)$ vs $r$ coordinate plot (1) |
| `neet_2021_q026_option_b` | 26 | option | B | (2) | 5 | 207x190 | 3,524 | `1f900a6cbfa21a37` | $B(r)$ vs $r$ coordinate plot (2) |
| `neet_2021_q026_option_c` | 26 | option | C | (3) | 5 | 208x189 | 3,886 | `b856a9386c99c756` | $B(r)$ vs $r$ coordinate plot (3) |
| `neet_2021_q026_option_d` | 26 | option | D | (4) | 5 | 205x189 | 3,558 | `3658257d07997424` | $B(r)$ vs $r$ coordinate plot (4) |
| `neet_2021_q038_stem` | 38 | stem | — | — | 7 | 406x541 | 18,740 | `1b899a68bc43d4e8` | Logic gate circuit (AND/NAND/OR) |
| `neet_2021_q038_option_a` | 38 | option | A | (1) | 7 | 401x77 | 3,320 | `e83713f5728a3915` | Waveform output option (1) |
| `neet_2021_q038_option_b` | 38 | option | B | (2) | 7 | 400x63 | 1,962 | `a90623a3b5ce8011` | Waveform output option (2) |
| `neet_2021_q038_option_c` | 38 | option | C | (3) | 7 | 401x31 | 1,607 | `4a3317765106195c` | Waveform output option (3) |
| `neet_2021_q038_option_d` | 38 | option | D | (4) | 7 | 400x63 | 1,987 | `7d7d59049755b3eb` | Waveform output option (4) |
| `neet_2021_q040_stem` | 40 | stem | — | — | 7 | 322x143 | 4,213 | `e4f58be8593a2eb6` | Suspended meter rule on wedge |
| `neet_2021_q049_stem` | 49 | stem | — | — | 9 | 396x159 | 5,744 | `980a32439a04a3f1` | Resistor bridge network |
| `neet_2021_q060_option_a` | 60 | option | A | (1) | 10 | 203x185 | 6,368 | `5107e3ea595d2c20` | Reaction potential curve (1) |
| `neet_2021_q060_option_b` | 60 | option | B | (2) | 10 | 203x185 | 6,290 | `5ca642c650ca431d` | Reaction potential curve (2) |
| `neet_2021_q060_option_c` | 60 | option | C | (3) | 10 | 200x183 | 6,554 | `867aa9991264c126` | Reaction potential curve (3) |
| `neet_2021_q060_option_d` | 60 | option | D | (4) | 10 | 201x185 | 5,907 | `a8d873d6bb64c760` | Reaction potential curve (4) |
| `neet_2021_q062_option_a` | 62 | option | A | (1) | 10 | 264x83 | 3,121 | `d2891d4e414f6b21` | Dehydration alkene structure (1) |
| `neet_2021_q062_option_b` | 62 | option | B | (2) | 10 | 355x82 | 3,747 | `5ea52d58546b3fcf` | Dehydration alkene structure (2) |
| `neet_2021_q062_option_c` | 62 | option | C | (3) | 10 | 212x94 | 3,153 | `141b7ddad496ebf4` | Dehydration alkene structure (3) |
| `neet_2021_q062_option_d` | 62 | option | D | (4) | 10 | 227x83 | 3,086 | `cb1c73b0a7c44955` | Dehydration alkene structure (4) |
| `neet_2021_q063_option_a` | 63 | option | A | (1) | 11 | 288x228 | 13,000 | `232b6c7ff592070f` | Isotherms $P$ vs $1/V$ (1) |
| `neet_2021_q063_option_b` | 63 | option | B | (2) | 11 | 288x246 | 12,897 | `b2c5dc6c968e7ec9` | Isotherms $P$ vs $1/V$ (2) |
| `neet_2021_q063_option_c` | 63 | option | C | (3) | 11 | 288x234 | 12,504 | `fc75d503d212133a` | Isotherms $P$ vs $1/V$ (3) |
| `neet_2021_q063_option_d` | 63 | option | D | (4) | 11 | 288x251 | 13,293 | `5f0b41121d5565e3` | Isotherms $P$ vs $1/V$ (4) |
| `neet_2021_q079_option_a` | 79 | option | A | (1) | 12 | 157x63 | 3,363 | `645fcab6beffdfc1` | Aromatic isomer structure (1) |
| `neet_2021_q079_option_b` | 79 | option | B | (2) | 12 | 210x61 | 3,741 | `4f32997235266851` | Aromatic isomer structure (2) |
| `neet_2021_q079_option_c` | 79 | option | C | (3) | 12 | 157x63 | 3,382 | `3c87cead9b062ca6` | Aromatic isomer structure (3) |
| `neet_2021_q079_option_d` | 79 | option | D | (4) | 12 | 251x111 | 5,699 | `fcb4c73238fc6f22` | Aromatic isomer structure (4) |
| `neet_2021_q082_option_a` | 82 | option | A | (1) | 13 | 154x112 | 2,860 | `0cbdb795c73950ef` | 2,6-Dimethyl-dec-4-ene skeletal (1) |
| `neet_2021_q082_option_b` | 82 | option | B | (2) | 13 | 154x112 | 2,746 | `8612140bb0f8a920` | 2,6-Dimethyl-dec-4-ene skeletal (2) |
| `neet_2021_q082_option_c` | 82 | option | C | (3) | 13 | 154x112 | 2,752 | `1fa14c7fc5208f9c` | 2,6-Dimethyl-dec-4-ene skeletal (3) |
| `neet_2021_q082_option_d` | 82 | option | D | (4) | 13 | 154x112 | 2,740 | `141b212f719464bc` | 2,6-Dimethyl-dec-4-ene skeletal (4) |
| `neet_2021_q088_option_a` | 88 | option | A | (1) | 14 | 248x144 | 6,367 | `eb3a774944d15669` | Phenol/diazonium product (1) |
| `neet_2021_q088_option_b` | 88 | option | B | (2) | 14 | 253x144 | 6,432 | `9c438f72df9b7527` | Phenol/diazonium product (2) |
| `neet_2021_q088_option_c` | 88 | option | C | (3) | 14 | 251x144 | 6,444 | `96bc9d2b27a3c3e8` | Phenol/diazonium product (3) |
| `neet_2021_q088_option_d` | 88 | option | D | (4) | 14 | 250x142 | 6,170 | `f21956556e4c7d0d` | Phenol/diazonium product (4) |
| `neet_2021_q099_option_a` | 99 | option | A | (1) | 15 | 379x123 | 6,560 | `01ec15bf44b5fe4d` | Grignard organometallic intermediate (1) |
| `neet_2021_q099_option_b` | 99 | option | B | (2) | 15 | 249x138 | 5,618 | `510a768f51a705b6` | Grignard organometallic intermediate (2) |
| `neet_2021_q099_option_c` | 99 | option | C | (3) | 15 | 185x119 | 4,374 | `b34cfbf2404e9c71` | Grignard organometallic intermediate (3) |
| `neet_2021_q099_option_d` | 99 | option | D | (4) | 15 | 186x119 | 4,286 | `b0c79e604f56f488` | Grignard organometallic intermediate (4) |

---

## 6. Integration Architecture & Schema Analysis

We inspected the actual SQLAlchemy models in [`backend/app/models/competitive_models.py`](file:///d:/EduSens/backend/app/models/competitive_models.py):

### Current Model Definitions
1. **`Question`**:
   - Contains: `diagram_asset_url = Column(String(512), nullable=True)`
   - Used for stem diagram linking (e.g. `/static/assets/diagrams/neet_2021/neet_2021_q004_stem.png`).
2. **`QuestionOption`**:
   - Contains: `option_key`, `option_text`, `is_correct`, `explanation`, `sort_order`.
   - **Does NOT contain** a dedicated `diagram_asset_url` or `image_url` column.

### Recommended Future Ingestion Strategy
To link these visual assets during future ingestion pilots without violating schema integrity:
- **For Stem Diagrams (Category A & C)**:
  - Populate `Question.diagram_asset_url` with the static URL path `static/assets/diagrams/neet_2021/neet_2021_q{num:03d}_stem.png`.
  - Preserve the complete scientific text in `Question.question_text`.
- **For Graphical Options (Category B & C)**:
  - *Option 1 (Schema Migration - Recommended for Milestone 5.8)*: Add an Alembic migration adding `diagram_asset_url = Column(String(512), nullable=True)` to `QuestionOption`.
  - *Option 2 (Text-Tag Convention - Non-breaking)*: Store standard Markdown image reference in `QuestionOption.option_text`:
    `![Option A](/static/assets/diagrams/neet_2021/neet_2021_q026_option_a.png)`
- **Publication Policy**: Generating visual assets does NOT promote questions to scoring-eligible or published status. All 13 questions must remain in `quarantine_status = "PENDING_VERIFICATION"` until a human reviewer completes visual verification.

---

## 7. Verification and Testing Evidence

### Test Execution Commands & Results
```bash
# 1. Run focused vector diagram extraction test suite
pytest backend/tests/test_vector_diagram_extractor.py -v
# Output: 12 passed in 3.40s

# 2. Run competitive examination regression suites
pytest backend/tests/test_production_ingestion_gate.py \
       backend/tests/test_neet_2021_quality_audit.py \
       backend/tests/test_neet_2021_independent_audit.py \
       backend/tests/test_pilot_ingestion.py -v
# Output: 27 passed in 3.13s
```
**Total Passing Tests**: **39 tests passed, 0 failures, 0 regressions**.

### Canonical Database Safety Proof
```python
# Database verification script output
DB File Size: 4882432 bytes
  questions: 0
  exam_papers: 0
  question_options: 0
  question_verification_logs: 0
  mcq_questions: 80
```
The canonical SQLite database at `D:\EduSens\edunavika.db` maintained identical byte-level size and 0 competitive examination records throughout all test executions.

---

## 8. Milestone Definition of Done Audit

| Requirement | Evaluation | Evidence |
| :--- | :---: | :--- |
| **Implementation exists in repo** | **YES** | `backend/app/ingestion/vector_diagram_extractor.py`, `scripts/extract_neet_2021_diagrams.py` |
| **Documented interfaces & errors** | **YES** | Typed dataclasses, custom exception hierarchy (`PDFSourceError`, `BoundingBoxError`, etc.) |
| **Automated tests pass with evidence** | **YES** | 12/12 new tests passed, 27/27 regression tests passed (39 total) |
| **Real 13 questions attempted** | **YES** | All 13 questions processed against `neet-2021.pdf` |
| **All assets mapped to PDF region** | **YES** | Bounding box coordinates, page index, and DPI recorded in manifest |
| **Failures/ambiguities reported** | **YES** | 0 extraction failures; all assets marked `PENDING_HUMAN_REVIEW` |
| **Reproducible manifest & review** | **YES** | `data/processed/neet_2021_diagram_manifest.json` and `.html` contact sheet |
| **Zero canonical DB writes** | **YES** | Canonical `edunavika.db` verified unchanged at 4,882,432 bytes |
| **Ingestion-gate protections intact** | **YES** | Zero questions promoted; scoring eligibility gate preserved |

---

## 9. Next Steps and Git Staging Guidance

### Human Verification Workflow
1. Open [`data/processed/neet_2021_diagram_contact_sheet.html`](file:///d:/EduSens/data/processed/neet_2021_diagram_contact_sheet.html) in a web browser.
2. Verify that each crop accurately captures the scientific diagram, labels, and axes without clipping or capturing neighboring text.
3. Once verified by a subject-matter expert, update `human_review_status` in the manifest to `VERIFIED`.

### Safe Git Staging Commands (For Reference Only - Do Not Execute Without Approval)
To stage only the milestone-specific files:
```bash
git add backend/app/ingestion/vector_diagram_extractor.py
git add backend/tests/test_vector_diagram_extractor.py
git add scripts/extract_neet_2021_diagrams.py
git add backend/static/assets/diagrams/neet_2021/
git add data/processed/neet_2021_diagram_manifest.json
git add data/processed/neet_2021_diagram_contact_sheet.html
git add docs/milestone_5_7_scope.md
git add docs/milestone_5_7_vector_diagram_extraction.md
```
*(As per execution policy, no commit, push, or global `git add .` has been performed).*
