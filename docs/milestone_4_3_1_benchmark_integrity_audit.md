# Milestone 4.3.1 — Research-Grade Benchmark Integrity Audit

============================================================
MILESTONE 4.3.1
BENCHMARK INTEGRITY AUDIT
============================================================

**Repository:** `https://github.com/tkacha467/EduNavika.git`  
**Branch:** `main`  
**HEAD Commit:** `ed4d3d5` (working tree audited with P0/P1 fixes)  
**Auditor Role:** Senior Research Scientist & ML Evaluation Auditor  

---

## 1. Audit Scope & Component Verdicts

| Evaluation Dimension | Verdict | Core Scientific Finding |
|---|---|---|
| **Ground Truth Validity** | **CONCERN** | Contains non-formula fragments (`eq_4` `10 mL`, `eq_9` `F_1`, `eq_12` `-OH`, `eq_22` `4 + 5 = 9`). Pages 40–46 in Maths PDF have unmapped embedded font streams. Transcribed without multi-annotator inter-rater reliability. |
| **Dataset Sampling** | **CONCERN** | Convenience-based sample of 30 pages (18 Maths, 12 Science) with an unstratified contiguous 7-page block (pages 40–46). Cannot support claims of universal GSEB textbook performance. |
| **Evaluator Validity** | **CONCERN (Resolved via P0 Fix)** | Originally equated raw substring presence (`norm_gt in norm_ext`) with formula exact match, and penalized equivalent Unicode mathematical symbols (`√`, `x²`, `±`). Also suffered from cross-document page collisions. Fixed in Milestone 4.3.1. |
| **RapidOCR Verification** | **CONCERN** | The reported single exact match (`1/31 = 3.2%`) was `eq_12` (`-OH`), a 3-character chemical functional group fragment rather than a mathematical formula. RapidOCR achieved 0.0% exact matches on real equations and split fractions. |
| **Heuristic Verification** | **FAIL (Reclassified)** | Previously labeled "Best Trade-Off", but scored 0.0% exact formula match and risked corrupting ordinary prose (`"in a 2 hour period"` $\to$ `"in a^2 hour period"`). Reclassified as an experimental post-processor with insufficient mathematical fidelity. |
| **Runtime Methodology** | **PASS** | Evaluated timing correctly attributes >99.9% of latency to neural OCR inference (14.4s–60s/page on CPU). PDF rendering overhead is negligible (~0.015s). |
| **Extractor Comparison Fairness** | **PASS WITH LIMITATIONS** | Same 30 pages, same 31 formulas, and same evaluator. Modality differences (digital font stream vs 150 DPI raster render) are scientifically valid but must be stated explicitly. |
| **Data Leakage** | **CONCERN** | Heuristic rules (`xyabcrsh`) were designed after observing benchmark ground truth formulas without an isolated, held-out evaluation set. |
| **RAG Safety** | **PASS** | Real-world verification confirmed: mathematically corrupted chunks (e.g. Science page 86 esterification reaction) trigger `CORRUPTED` status in `MathQualityGate` and are strictly blocked by `ContextBuilder`. Validated that safety blocking does not equal extraction accuracy. |
| **Statistical Interpretation** | **CONCERN** | With $N = 31$, a single formula equals ~3.2%. Reporting percentages without raw counts gave a false impression of high statistical precision. |

---

## 2. Granular Audit Findings (P0 — P3 Taxonomy)

### P0 — Invalidates or Directly Distorts Benchmark Conclusions

1. **Page Number Collision Across Multi-Document Corpus**:
   - *Problem*: `MathEvaluator.evaluate_page(page_num, text)` matched ground-truth entries by integer `page_num` alone without document disambiguation. In our 30-page benchmark, pages 40, 160, and 183 appear in both `Std-10_Maths_EnglishMedium.pdf` and `Std-10_Science_English Medium.pdf` (10% of the entire dataset). When evaluating Maths page 40, it fetched Science page 40 (`pH < 5.5`), evaluating the wrong book's ground truth.
   - *Fix*: Updated `MathEvaluator.evaluate_page` to accept `document` and perform path-normalized disambiguation.
2. **Normalized Substring Presence Equated with Formula Exact Match**:
   - *Problem*: `norm_gt in norm_ext` treated any occurrence of characters anywhere on a 2,000-character page as an "Exact Mathematical Match", without verifying formula boundaries.
   - *Fix*: Hardened evaluator with `_clean_syntax` and boundary checking `(?<![a-zA-Z0-9])` for short tokens ($\le 4$ chars), preventing accidental substring matches.
3. **Unicode Symbol Penalization**:
   - *Problem*: The original `_normalize` function checked only ASCII LaTeX strings. Extracted text containing legitimate Unicode mathematical symbols (`x²`, `√3`, `±`, `−`, `θ`, `π`) failed string comparison against LaTeX targets (`x^2`, `\sqrt{3}`, `\pm`, `-`, `\theta`, `\pi`).
   - *Fix*: Implemented canonical bidirectional symbol normalization in `_clean_syntax`, normalizing Unicode superscripts, subscripts, radicals, operators, and grouping braces.

### P1 — Materially Weakens Research Claims

1. **Over-Interpretation of RapidOCR's Single Match (`eq_12`)**:
   - *Problem*: RapidOCR was credited with a 3.2% exact match rate based solely on matching `-OH`. When evaluated under canonical dash normalization, standard digital text extractors (`PyPDFium2` and `PyPDF`) also match `-OH` with boundaries. RapidOCR has **0.0% exact match** on actual mathematical equations.
2. **Prose Corruption Risk in Heuristic Post-Processor**:
   - *Problem*: `HeuristicMathExtractor` blindly elevated any single letter followed by `2` or `3`, mutating natural English sentences (`"In a 2 hour period"` $\to$ `"In a^2 hour period"`).
   - *Fix*: Hardened regex to require mathematical operators or bracket contexts before elevating variable letters.
3. **Conflating Safety Quarantine with Extraction Accuracy**:
   - *Problem*: Prior reporting claimed "100% mathematical correctness" because corrupted chunks were blocked.
   - *Correction*: Blocking corrupted content is **safety quarantine**, not extraction accuracy. True extraction accuracy of the baseline remains 0.0% on complex formulas.

### P2 — Methodological Improvements

1. **Small Sample Size ($N = 31$)**:
   - Wilson score 95% confidence interval for 1/31 is $[0.08\%, 16.7\%]$. Raw counts must always accompany percentages.
2. **Sequential CPU vs Parallel Wall-Clock Runtime**:
   - The 5.8-hour corpus runtime estimate for RapidOCR is strictly sequential single-core CPU time. Parallelized across 4–8 cores, wall-clock time is ~1.0–1.5 hours, though total compute cost remains unchanged.

### P3 — Documentation & Engineering Improvements

1. Clear separation of chemical notation vs mathematical formulas in benchmark documentation.
2. Formally documenting that GSEB Std 10 Maths pages 40–46 contain non-standard font stream encodings.

---

## 3. Corrected Benchmark Results

With P0/P1 evaluator fixes applied (canonical Unicode normalization and document disambiguation across the exact same 30 pages and 31 formulas):

| Extractor | Category | Raw Exact Match | Exact Match % | High Symbols | Semantic High | Semantic Review | Semantic Fail | Avg Time / Page | Total Time (30 pgs) |
|---|---|---|---|---|---|---|---|---|---|
| **PyPDFium2Extractor** *(Baseline)* | Standard PDF Text | **1 / 31** | **3.2%** | **4 / 31 (12.9%)** | **1 (3.2%)** | **5 (16.1%)** | **25 (80.6%)** | **0.011s** | **0.32s** |
| **PyPDFExtractor** | Alternative PDF Text | 1 / 31 | 3.2% | 3 / 31 (9.7%) | 1 (3.2%) | 3 (9.7%) | 27 (87.1%) | 0.210s | 6.32s |
| **RapidOCRExtractor** | Computer Vision OCR | 1 / 31 | 3.2% | 3 / 31 (9.7%) | 1 (3.2%) | 9 (29.0%) | 21 (67.7%) | 14.411s | 432.33s (~7.2m) |
| **HeuristicMathExtractor** | Text + Post-Proc | 1 / 31 | 3.2% | 4 / 31 (12.9%) | 1 (3.2%) | 5 (16.1%) | 25 (80.6%) | 0.027s | 0.80s |

### Before vs After Disambiguation & Canonical Normalization

```
BEFORE AUDIT:
PyPDFium2:   Exact: 0 / 31 (0.0%) | RapidOCR: Exact: 1 / 31 (3.2%)
Claimed: RapidOCR was superior in exact formula recovery.

AFTER AUDIT (CORRECTED):
PyPDFium2:   Exact: 1 / 31 (3.2%) | RapidOCR: Exact: 1 / 31 (3.2%)
Reality: Both matched the exact same single token (eq_12, '-OH').
Neither extractor achieved an exact match on ANY multi-token mathematical equation.
```

---

## 4. Research Conclusion

> **Central Research Question**:  
> *"Can we confidently conclude that PyPDFium2 + MathQualityGate + selective specialized processing is currently the strongest architecture among evaluated approaches?"*

### Verdict:
# YES, WITH LIMITATIONS

### Empirical Rationale:
1. **No Evaluated Specialized Extractor Solves the Problem**: RapidOCR achieves the exact same exact-match count (1/31) as the baseline, while incurring a **1,310x runtime penalty** and fragmenting surrounding prose context.
2. **Heuristics Cannot Reconstruct Stripped Math**: Post-processing text streams cannot recover missing square root radicands or multi-line fraction bars that never existed in the raw text stream.
3. **Defense-in-Depth Is Empirically Validated**: `MathQualityGate` deterministically detects corrupted mathematical text (verified on Science page 86) and safely blocks it from entering LLM context, protecting downstream RAG without sacrificing pipeline throughput.

---

## 5. Publication Readiness

# RESEARCH-GRADE WITH LIMITATIONS

- **Why Not Fully Ready**: The benchmark sample ($N = 31$ formulas across 30 pages) is a convenience sample rather than a stratified random sample of the complete GSEB curriculum. It lacks multi-annotator inter-rater reliability scores for ground-truth transcription.
- **Why Research-Grade**: The evaluator is now 100% deterministic, cross-document page collisions are eliminated, Unicode math is canonically normalized, runtime measurements are verified down to the sub-millisecond level, and all 54 unit and regression tests pass green.

---

## 6. Recommended Next Experiment (For Milestone 4.4+)

Do NOT implement immediately. Recommend for future work:
1. **Targeted Crop OCR with Lightweight Detection**: Instead of whole-page 150 DPI OCR, use a lightweight layout detector (e.g. YOLOv8-DocLayout or OpenCV contour bounding) to isolate ONLY mathematical formula bounding boxes, running specialized math OCR solely on the cropped formula.
2. **Stratified Curriculum Benchmark Expansion**: Expand the ground truth to 100+ formulas stratified across all 15 chapters of Std 10 Mathematics and Science, with independent double-annotation.
