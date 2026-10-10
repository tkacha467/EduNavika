# Milestone 4.3 — Specialized Mathematical Extraction Benchmark Report

## 1. Executive Benchmark Summary

| Extractor | Category | Exact Match | High Symbols | Semantic High | Semantic Review | Semantic Fail | Avg Time / Page | Total Time (30 pgs) |
|---|---|---|---|---|---|---|---|---|
| **PyPDFium2Extractor** *(Baseline)* | Standard PDF Text | 0 / 31 (0.0%) | 4 / 31 (12.9%) | 0 (0.0%) | 5 (16.1%) | 26 (83.9%) | **0.011s** | **0.32s** |
| **PyPDFExtractor** | Alternative PDF Text | 0 / 31 (0.0%) | 2 / 31 (6.5%) | 0 (0.0%) | 3 (9.7%) | 28 (90.3%) | 0.210s | 6.32s |
| **RapidOCRExtractor** | Computer Vision OCR | **1 / 31 (3.2%)** | 3 / 31 (9.7%) | **1 (3.2%)** | **9 (29.0%)** | **21 (67.7%)** | 14.411s | 432.33s (~7.2m) |
| **HeuristicMathExtractor** | Text + Domain Post-Proc | 0 / 31 (0.0%) | 4 / 31 (12.9%) | 0 (0.0%) | 5 (16.1%) | 26 (83.9%) | 0.027s | 0.80s |

---

## 2. Granular Failure Taxonomy

Across the 31 canonical mathematical formulas in 30 representative GSEB textbook pages, failures broke down as follows:

| Failure Category | PyPDFium2 | PyPDF | RapidOCR | HeuristicMath | Description & Manifestation |
|---|---|---|---|---|---|
| **Exponent Flattening** | 12 | 12 | **7** | 12 | $x^2, r^2$ flattened to `x2`, `x 2`, or disconnected numbers |
| **Subscript Flattening** | 7 | 7 | 7 | 7 | $x_1, y_1, x_2, y_2$ flattened to `x1`, `y1` |
| **Missing Radical** | 4 | 4 | 0 | 4 | Square root $\sqrt{\dots}$ radical sign dropped or substituted by box glyphs |
| **Fraction Splitting** | 2 | 0 | 4 | 2 | Horizontal fraction bar omitted, numerator and denominator split across distant lines |
| **Symbol Omission / Substitution** | 7 | 8 | 5 | 7 | $\pm, \times, \rightarrow, \le, \ge$ omitted or replaced by ASCII approximations |

---

## 3. Candidates Not Evaluated

| Candidate | Category | Status | Engineering & Hardware Rationale |
|---|---|---|---|
| **Nougat** (`facebook/nougat-small`) | Vision-Encoder-Decoder (Swin-T + mBART) | **NOT EVALUATED** | Requires ~1.5GB PyTorch weights. Dedicated CUDA GPU required for viable throughput; CPU latency exceeds 20-30s/page, making full-corpus ingestion prohibitive on consumer hardware. |
| **Marker** (`VikParuchuri/marker`) | Deep Layout + OCR + Texify Pipeline | **NOT EVALUATED** | Requires multi-model ensemble (Surya layout detection + Texify OCR, ~3.5GB weights) and heavy GPU dependencies. |
| **Tesseract OCR** (`pytesseract`) | Traditional OCR Engine | **NOT EVALUATED** | External C++ binary `tesseract.exe` is not present in the Windows system PATH. |

---

## 4. Key Takeaways for Downstream RAG

1. **OCR Accuracy vs. Latency Trade-Off**: RapidOCR achieved a non-zero exact match (3.2%) and reduced semantic failures from 83.9% down to 67.7%, but incurred an **over 1300x runtime penalty** (14.41s vs 0.011s per page).
2. **Context Fragmentation**: Visual OCR strips document heading layout and paragraphs into disjoint bounding boxes, which damages surrounding prose preservation needed for educational RAG embeddings and chunking.
3. **Strategic Verdict**: Specialized vision OCR is **not justified** for whole-corpus ingestion. The optimal strategy remains **hybrid routing (Option C)**: PyPDFium2 fast extraction validated by the `MathQualityGate`, triggering selective specialized extraction only on `MATH_HEAVY` pages failing safety gates.
