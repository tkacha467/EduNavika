# EduNavika — Milestone 5.7: Scope Assessment & Extraction Architecture

**Role:** Senior Data-Ingestion Architect, PDF/OCR Specialist & Assessment QA Reviewer  
**Exam:** NEET (UG) 2021 Booklet Code `M4`  
**Target Document:** `GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf`  
- **SHA-256:** `e9acdfb29dfcff0a3a186819f7336330af4ce51855990d1081c78637b338587a`  
- **File Size:** 947,343 bytes  
- **Page Count:** 28 pages  
**Reference Key Document:** `docs/reference/Notice_20211101205130.pdf` (NTA Final Key 01.11.2021)  
**Date:** October 25, 2026  
**Scope Verdict:** **APPROVED FOR FULL IMPLEMENTATION (DATABASE-ISOLATED)**  

---

## 1. Executive Scope Overview

Milestone 5.6 established that while 187 of the 200 NEET 2021 questions are structurally and textually complete, **13 questions remain quarantined** because their diagrams or answer choices exist solely as PDF vector drawing paths rather than Unicode text. Standard PDF text extraction returns empty strings for these graphical options and omits stem schematics.

Milestone 5.7 establishes a production-grade extraction engine ([backend/app/ingestion/vector_diagram_extractor.py](file:///d:/EduSens/backend/app/ingestion/vector_diagram_extractor.py)) to identify candidate diagram regions from PyMuPDF vector drawing paths, crop each region cleanly with protective padding, rasterize them into high-resolution lossless PNG assets, generate an auditable machine-readable manifest, and link them to EduNavika question models without writing to the persistent database.

---

## 2. Root-Cause Diagnosis of the 13 Quarantined Questions

Inspection of `GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf` using PyMuPDF confirms that the document contains **0 embedded raster bitmap images** (`len(page.get_images()) == 0` on all 28 pages). All electrical circuits, mechanical balances, thermodynamic graphs, and organic chemical structures are composed of PDF vector drawing operators (`page.get_drawings()`).

Detailed layout inspection confirms that the 13 quarantined questions divide into three distinct architectural categories requiring different cropping behaviors:

### Category A: Stem Diagram Dependencies (4 Questions)
The question stem explicitly references a missing apparatus or circuit figure, while the four answer options are standard text or formulas.
- **Q4 (Page 2, Col 0 - Physics):** *"The equivalent capacitance of the combination shown in the figure is :"*
  - **Drawing:** Capacitor bridge schematic between y=631.4 and y=704.0 (15 vector paths).
  - **Options:** Pure text `(1) 3C`, `(2) 2C`, `(3) C/2`, `(4) 3C/2`.
  - **Asset Required:** 1 stem diagram asset (`neet_2021_q004_stem.png`).
- **Q20 (Page 4, Col 1 - Physics):** *"An inductor of inductance L, a capacitor... connected in series... as shown in figure."*
  - **Drawing:** Series LCR circuit schematic with AC source between y=178.4 and y=317.6 (59 vector paths).
  - **Options:** Pure text mathematical formulas.
  - **Asset Required:** 1 stem diagram asset (`neet_2021_q020_stem.png`).
- **Q40 (Page 7, Col 1 - Physics):** *"A uniform rod of length 200 cm... balanced on a wedge placed at 40 cm mark... as shown in the figure."*
  - **Drawing:** Suspended meter rule with weights and fulcrum wedge between y=181.8 and y=245.2 (32 vector paths).
  - **Options:** Pure text numerical values (`66.7 g`, `1/12 kg`, etc.).
  - **Asset Required:** 1 stem diagram asset (`neet_2021_q040_stem.png`).
- **Q49 (Page 9, Col 0 - Physics):** *"Three resistors having resistances r1, r2 and r3... connected as shown in the given circuit."*
  - **Drawing:** Triangular resistor bridge network between y=178.7 and y=250.1 (37 vector paths).
  - **Options:** Pure text algebraic expressions.
  - **Asset Required:** 1 stem diagram asset (`neet_2021_q049_stem.png`).

### Category B: Pure Graphical Options (8 Questions)
The question stem is self-contained text, but the four answer options (1), (2), (3), (4) consist entirely of discrete vector illustrations. Combining these into a single image would violate the data model, which requires individual option records.
- **Q26 (Page 5, Col 0 - Physics):** Magnetic field $B(r)$ distribution curves inside/outside cable. (4 discrete $B$ vs $r$ coordinate plots).
  - **Assets Required:** 4 individual option assets (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q60 (Page 10, Col 0 - Chemistry):** Exothermic reaction enthalpy profile curves ($\Delta H < 0$).
  - **Assets Required:** 4 individual option assets (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q62 (Page 10, Col 1 - Chemistry):** Acid-catalyzed alcohol dehydration reaction products.
  - **Assets Required:** 4 structural alkene chemical formulas (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q63 (Page 11, Col 0 - Chemistry):** Boyle's law isotherms ($P$ vs $1/V$ linear plots at temperatures $T_1, T_2, T_3$).
  - **Assets Required:** 4 individual option assets (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q79 (Page 12, Col 1 - Chemistry):** Nucleophilic aromatic substitution chemical structures.
  - **Assets Required:** 4 substituted benzene ring drawings (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q82 (Page 13, Col 0 - Chemistry):** IUPAC skeletal formula for 2,6-Dimethyl-dec-4-ene.
  - **Assets Required:** 4 skeletal carbon backbone drawings (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q88 (Page 14, Col 0 - Chemistry):** Multi-step aromatic synthesis products (toluene halogenation/hydrolysis).
  - **Assets Required:** 4 chemical product structures (`option_a`, `option_b`, `option_c`, `option_d`).
- **Q99 (Page 15, Col 1 - Chemistry):** Intermediate organometallic / aromatic reaction structure.
  - **Assets Required:** 4 complex organic chemical drawings (`option_a`, `option_b`, `option_c`, `option_d`).

### Category C: Hybrid Stem Diagram AND Graphical Options (1 Question)
- **Q38 (Page 7, Col 0 - Physics):** *"For the given circuit, the input digital signals are applied at the terminals A, B and C. What would be the output at terminal y?"*
  - **Stem Drawing:** Logic gate circuit diagram (NAND/OR gates) with input timing waveforms $A$, $B$, $C$ between y=144.3 and y=430.0.
  - **Option Drawings:** 4 discrete candidate output timing waveforms at (1) y=444.2, (2) y=488.9, (3) y=520.8, (4) y=556.1.
  - **Assets Required:** 1 stem asset (`q038_stem.png`) AND 4 individual option assets (`option_a`, `option_b`, `option_c`, `option_d`).

---

## 3. Total Asset Inventory to be Produced

| Question | Subject | Page | Column | Asset Role | Quantity | Target File Pattern |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Q4** | Physics | 2 | Left (0) | Stem | 1 | `neet_2021_q004_stem.png` |
| **Q20** | Physics | 4 | Right (1) | Stem | 1 | `neet_2021_q020_stem.png` |
| **Q26** | Physics | 5 | Left (0) | Options A–D | 4 | `neet_2021_q026_option_{a,b,c,d}.png` |
| **Q38** | Physics | 7 | Left (0) | Stem + Options A–D | 5 | `neet_2021_q038_stem.png`, `neet_2021_q038_option_{a,b,c,d}.png` |
| **Q40** | Physics | 7 | Right (1) | Stem | 1 | `neet_2021_q040_stem.png` |
| **Q49** | Physics | 9 | Left (0) | Stem | 1 | `neet_2021_q049_stem.png` |
| **Q60** | Chemistry | 10 | Left (0) | Options A–D | 4 | `neet_2021_q060_option_{a,b,c,d}.png` |
| **Q62** | Chemistry | 10 | Right (1) | Options A–D | 4 | `neet_2021_q062_option_{a,b,c,d}.png` |
| **Q63** | Chemistry | 11 | Left (0) | Options A–D | 4 | `neet_2021_q063_option_{a,b,c,d}.png` |
| **Q79** | Chemistry | 12 | Right (1) | Options A–D | 4 | `neet_2021_q079_option_{a,b,c,d}.png` |
| **Q82** | Chemistry | 13 | Left (0) | Options A–D | 4 | `neet_2021_q082_option_{a,b,c,d}.png` |
| **Q88** | Chemistry | 14 | Left (0) | Options A–D | 4 | `neet_2021_q088_option_{a,b,c,d}.png` |
| **Q99** | Chemistry | 15 | Right (1) | Options A–D | 4 | `neet_2021_q099_option_{a,b,c,d}.png` |
| **Total** | | | | | **41** | **5 Stem Assets + 36 Option Assets** |

---

## 4. Extraction & Rasterization Pipeline Architecture

### Core Modules & Separation of Concerns
1. **Extraction Service (`backend/app/ingestion/vector_diagram_extractor.py`):**
   - Pure functional Python module with typed signatures, custom exceptions, and structured logging.
   - Computes column-aware bounding boxes by clustering vector drawing paths (`page.get_drawings()`) within question bounds.
   - Applies padding margins (default: 4.0 pt) while respecting column boundaries to avoid clipping text labels or capturing neighbor items.
   - Renders clipped pixmaps via `page.get_pixmap(clip=rect, matrix=fitz.Matrix(2.0, 2.0))` to achieve 144–200 DPI resolution without blurriness.
   - Writes PNG files atomically and computes SHA-256 digests.
2. **Deterministic Manifest (`data/processed/neet_2021_diagram_manifest.json`):**
   - Records metadata for every asset: `asset_id`, `question_number`, `asset_role`, `option_label`, `page_number`, `bounding_box`, `render_scale`, `file_path`, `dimensions`, `sha256`, `extraction_status`, and `human_review_status: PENDING_HUMAN_REVIEW`.
3. **Contact Sheet Review Artifact (`data/processed/neet_2021_diagram_contact_sheet.html`):**
   - Generates an HTML review document displaying each extracted PNG next to its question text and PDF coordinates for human QA sign-off.
4. **Integration Layer:**
   - Prepares validated dictionaries for `QuestionIngestionService`:
     - Stems attach `diagram_asset_url = "/static/assets/diagrams/neet_2021/neet_2021_q{num}_stem.png"`.
     - Graphical options attach `option_text = "![Option {key}](/static/assets/diagrams/neet_2021/neet_2021_q{num}_option_{key.lower()}.png)"`.
   - Satisfies the 10-point ingestion gate requirement (`len(option_text.strip()) > 0`) without inventing new database columns.

---

## 5. Safety, Data Protection & Go/No-Go

1. **Persistent Database Protection:**
   - Canonical database `D:\EduSens\edunavika.db` remains 100% untouched.
   - All tests execute strictly against in-memory SQLite (`sqlite:///:memory:`) or synthetic PDF fixtures.
2. **Review Status Transparency:**
   - Extracted images are marked `PENDING_HUMAN_REVIEW`. Automated crop generation does not certify semantic correctness.
3. **Execution Decision:**
   - **GO FOR EXTRACTION IMPLEMENTATION.** The source PDF is present, PyMuPDF 1.28.2 is installed, all 13 questions and 41 assets are precisely localized, and the data model cleanly accommodates the asset references.
