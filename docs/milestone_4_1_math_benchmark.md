# Milestone 4.1: Specialized Mathematical Document Extraction Benchmark & Validation

## 1. Benchmark Objective
Secondary and higher-secondary STEM textbooks (Standards 9–12) contain mathematical notation (radicals, fractions, exponents, Greek characters, chemical reaction equations) that frequently undergoes catastrophic corruption when extracted via standard PDF layout extractors (e.g. `pypdf`, `pypdfium2`).

The objective of Milestone 4.1 is:
1. Establish a rigorous, reproducible ground-truth benchmark suite of authentic GSEB mathematical expressions.
2. Evaluate standard PDF extraction against human-curated ground truth across exact match, symbol retention, and semantic preserving dimensions.
3. Validate downstream RAG safety by implementing an explicit `MathQualityGate` to prevent corrupted mathematical chunks from poisoning vector indices and LLM MCQ generators.

---

## 2. Dataset Description
The ground truth benchmark (`backend/app/ingestion/math/ground_truth.json` and `data/processed/reports/math_ground_truth.json`) contains:
- **30 representative pages** across GSEB Standard 10 Mathematics (`Std-10_Maths_EnglishMedium.pdf`) and Standard 10 Science & Technology (`Std-10_Science_English Medium.pdf`).
- **31 target formulas**, covering:
  - Euclidean Coordinate Distance: $\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$
  - Quadratic Factorization: $x^2 - 3 = (x - \sqrt{3})(x + \sqrt{3})$
  - Arithmetic Progressions: $S_n = \frac{n}{2} [2a + (n-1)d]$
  - Quadratic Formula: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
  - Cone Volume & Surface Area: $\frac{1}{3} \pi r^2 h$, $2 \pi r^2$
  - Trigonometric Ratios & Angles: $\sin \theta, \cos \theta, \tan \theta, \angle OPQ = 90^\circ$
  - Optics & Electric Circuits: $P = \frac{1}{f}, V = IR$
  - Chemical Equations & Ions: $Mg + O_2 \rightarrow MgO, H^+ + OH^-, C_2H_6, -OH, CO_2$

Each formula item defines:
- Target LaTeX string
- Required expected symbols (e.g., `\sqrt`, `^`, `\frac`, `\angle`)
- Structural flags (`has_fraction`, `has_subscript`, `has_superscript`)
- Surrounding contextual anchor text

---

## 3. Evaluation Methodology & Metrics
Evaluations are executed via `MathEvaluator` (`backend/app/ingestion/math/evaluator.py`):

1. **Exact Match Rate**: Verifies whether the normalized LaTeX expression is preserved without character loss or structural degradation within the extracted page.
2. **Symbol Retention Rate**: Evaluates whether mathematical and operational tokens (`\sqrt`, `\pm`, `\frac`, operators) survive text extraction.
3. **Subscript/Superscript Fidelity**: Tests whether index positioning is represented via markup (`^`, `_`) or Unicode glyphs (`²`, `₃`).
4. **Fraction Preservation**: Assesses whether numerator/denominator pairs retain division notation (`\frac` or `/`).
5. **Semantic Accuracy Grading**:
   - `HIGH`: Expression is preserved verbatim with structural integrity.
   - `REVIEW`: Core symbols remain but minor formatting loss occurred (requires human or LLM verification).
   - `FAIL`: Severe corruption, dropped exponents, missing radicands, or altered mathematical semantics.

---

## 4. Experimental Results

Execution command:
```bash
python scripts/benchmark_math_ocr.py --extractor pypdfium2 --out data/processed/reports/math_ocr_benchmark_report.json
```

| Metric | DummyExtractor (Synthetic Control) | PyPDFium2Extractor (Current Pipeline Baseline) |
| :--- | :--- | :--- |
| **Total Pages Evaluated** | 30 | 30 |
| **Total Formulas Evaluated** | 31 | 31 |
| **Exact Matches** | 1 (3.2%) | 0 (0.0%) |
| **High Symbol Retention** | 2 (6.5%) | 4 (12.9%) |
| **Semantic HIGH** | 1 (3.2%) | 0 (0.0%) |
| **Semantic REVIEW** | 3 (9.7%) | 5 (16.1%) |
| **Semantic FAIL** | 27 (87.1%) | 26 (83.9%) |
| **Average Time Per Page** | 0.000s | 0.012s |

---

## 5. Limitations & Failure Modes

1. **Radical Glyph Loss**:
   - Square root radical bars ($\sqrt{...}$) are rendered as vector drawing strokes in GSEB PDFs. Pypdfium2 extracts only the radicand or drops the radical completely, converting $\sqrt{x^2+y^2}$ into $(x2 + y2)$.
2. **Exponent De-elevation**:
   - Exponents are positioned by vertical coordinate displacement without font tagging. Standard extractors linearize the digits, converting $x^2 - 3$ into $x2 - 3$ or $a^2+b^2=c^2$ into $a2 + b2 = c2$.
3. **Fraction Splitting**:
   - Horizontal fraction lines are geometric vector rectangles. Extractors treat numerators and denominators as independent lines of text, dropping division operators.
4. **Chemical Bond Scrambling**:
   - Complex organic chemistry bonds produce disordered character sequences (e.g. `CH COOH CH CH OH CH C C CH CH H O3 3 2 3 2 3 2`).

---

## 6. Downstream RAG Implications & The Quality Gate

### RAG Safety Rule
**RAG pipelines must never blindly ingest unvalidated mathematical content.** 
Passing corrupted formulas (e.g., $x2 - 3$ instead of $x^2 - 3$) to an LLM produces hallucinatory MCQs and incorrect answer keys, violating EduNavika's pedagogical integrity.

### Explicit Quality Gate Flow
```text
RAW TEXTBOOK PDF
       │
       ▼
1. Page Extraction (pypdfium2)
       │
       ▼
2. Mathematical Quality Gate (MathQualityGate)
   ├── Inspect for math indicators
   ├── Check corruption signatures (broken bonds, unbalanced brackets, floating digits)
   └── Assign status: SAFE | NEEDS_REVIEW | CORRUPTED
       │
       ├── If CORRUPTED:
       │   └── Tag chunk metadata `math_validity_status: CORRUPTED`
       │       (Excluded from auto-MCQ generation until vision-OCR pass)
       │
       └── If SAFE / NEEDS_REVIEW:
           └── Proceed to Chunking & Normalization
                   │
                   ▼
           Vector & Lexical Indexing (FAISS / BM25)
                   │
                   ▼
           RAG Pipeline & MCQ Generation
```

The `MathQualityGate` is implemented at `backend/app/ingestion/math/quality_gate.py` and validated by `backend/tests/test_math_extractor.py`.

---

## 7. Reproducibility Instructions

1. **Regenerate Ground Truth**:
   ```bash
   python -m scripts.gen_gt
   ```
2. **Run Unit Tests**:
   ```bash
   python -m pytest backend/tests/test_math_extractor.py -v
   ```
3. **Execute Benchmark**:
   ```bash
   python scripts/benchmark_math_ocr.py --extractor pypdfium2
   ```

---

## 8. Known Future Work
- Integrate specialized vision-based mathematical models (Nougat / Marker / Pix2Text) for pages flagged as `NEEDS_OCR` or `CORRUPTED`.
- Implement SymPy AST parsing to verify algebraic equivalence for expressions flagged as `REVIEW`.
