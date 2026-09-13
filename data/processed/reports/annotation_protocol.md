# Milestone 4.3.2: Mathematical Document Annotation Protocol & Taxonomy

## 1. Document Overview & Scientific Scope

This protocol defines the formal guidelines, taxonomy, canonical LaTeX transcription rules, and quality control procedures for the GSEB (Gujarat Secondary and Higher Secondary Education Board) Standards 9–12 Mathematical and Scientific Document Benchmark.

The benchmark evaluates the capacity of document layout analysis and OCR extraction pipelines (such as PyMuPDF, pypdfium2, RapidOCR, Nougat, and Marker) to extract mathematical equations, chemical formulas, and scientific notation without semantic corruption.

---

## 2. Benchmark Taxonomy & Stratification

The benchmark splits formula annotations into two distinct tracks:

### 2.1 Core Mathematical OCR Track
This track measures mathematical OCR fidelity across 4 fundamental mathematical disciplines:
1. **`ALGEBRA`**: Linear and quadratic equations, polynomials, radicals, arithmetic progressions, rational functions, and statistical formulations.
2. **`GEOMETRY`**: Geometric theorems, similarity criteria, angle relationships, coordinate geometry, circle theorems, and 2D/3D surface area and volume equations.
3. **`TRIGONOMETRY`**: Fundamental trigonometric ratios ($\sin, \cos, \tan, \cot, \sec, \csc$), complementary angle relations, Pythagorean trigonometric identities, and elevation/depression models.
4. **`PHYSICS`**: Physical laws expressed with mathematical notation, including optics (mirror and lens formulas, Snell's law) and electrodynamics (Ohm's law, resistance combinations, Joule heating, electric power).

### 2.2 Diagnostic Track
This track is evaluated separately from the core mathematical OCR benchmark:
1. **`CHEMICAL`**: Chemical reaction equations, state symbols (aq, s, l, g), ionic charges, and molecular formulae.
2. **`NUMERIC_EXPRESSION`**: Isolated numerical values with units (e.g., $10\text{ mL}$), single-variable labels, or elementary non-symbolic arithmetic (e.g., $4 + 5 = 9$).

> [!NOTE]
> Evaluation reports must separate `CORE`, `DIAGNOSTIC`, and `OVERALL` metrics. Scientific claims regarding mathematical extraction accuracy are strictly based on the `CORE` track.

---

## 3. Split Policy & Leakage Prevention

To prevent layout and contextual leakage during model evaluation:
1. **Page-Level Isolation**: The fundamental split unit is the **physical textbook page**. All formula items on a page inherit the page's split:
   $$\text{Page } P \in \{\text{DEV}, \text{TEST}\} \implies \forall f \in P, \text{ split}(f) = \text{split}(P)$$
2. **Disjoint Sets**: $\text{DEV\_PAGES} \cap \text{TEST\_PAGES} = \emptyset$. Under no circumstance may any page or layout appear in both sets.
3. **Unique Benchmark Key**: The unique identifier for any formula in the benchmark is the 3-tuple:
   $$(\text{document}, \text{page}, \text{item\_id})$$
4. **Frozen Test Manifest**: The test set (`math_ground_truth_test.json`) is sealed with a SHA-256 cryptographic checksum recorded in `test_manifest.json`. Any modification to the test set invalidates the hash and halts benchmark evaluation.

---

## 4. Canonical LaTeX Transcription Conventions

Annotators must adhere to the following transcription standards:

| Mathematical Construct | Canonical Format | Disallowed / Non-Canonical Format |
|:---|:---|:---|
| Fractions | `\frac{numerator}{denominator}` | `numerator / denominator` or `\frac numerator denominator` |
| Square Roots | `\sqrt{x}` | `x^{1/2}` or `\surd x` |
| N-th Roots | `\sqrt[n]{x}` | `x^{1/n}` |
| Superscripts / Powers | `x^2`, `(a+b)^n` | `x²`, `x**2` |
| Subscripts | `a_n`, `x_1` | `a1`, `a n` |
| Combined Sub/Super | `x_2^2` or `(x_2)^2` | `x2^2` |
| Multiplication | `a \times b` (arithmetic) or juxtaposition `ab` | `a * b` or `a . b` |
| Dot Product / Multiplication | `a \cdot b` | `a . b` |
| Plus-Minus | `\pm` | `+/-` or `+ -` |
| Inequalities | `\le`, `\ge`, `\ne` | `<=`, `>=`, `!=`, `/=` |
| Greek Letters | `\alpha`, `\beta`, `\theta`, `\pi`, `\rho`, `\Delta`, `\sum` | Latin phonetics (`alpha`, `pi`) |
| Geometric Symbols | `\angle`, `\perp`, `\Delta`, `\sim`, `^\circ` | `angle`, `deg`, `degree` |
| Chemical Arrows | `\rightarrow`, `\xrightarrow{\Delta}` | `->`, `-->`, `=>` |

---

## 5. Multi-Annotator Workflow & Known Limitations

### 5.1 Adjudication Protocol
When multiple annotators are available:
1. **Independent Annotation**: Annotator A and Annotator B independently inspect designated PDF pages and transcribe formulas into canonical LaTeX.
2. **Disagreement Detection**: An automated differencing script compares:
   - LaTeX token sequence
   - Structural flags (`has_fraction`, `has_subscript`, `has_superscript`)
   - Bounding context (`surrounding_text`)
3. **Adjudication**: A senior adjudicator reviews discrepancies against the physical textbook PDF and selects or crafts the canonical gold-standard transcription.

### 5.2 Methodological Limitation Disclosure
> [!IMPORTANT]
> **Single-Adjudicator Limitation**: The initial GSEB 141-formula ground truth corpus was manually transcribed and verified against the physical GSEB Std-10 textbooks by a primary annotator and verified through programmatic cross-checks. While comprehensive programmatic validation is enforced (via `validate_math_gt.py`), multi-annotator inter-rater reliability metrics (such as Cohen's $\kappa$) require future multi-human annotation cycles. Researchers utilizing this benchmark should note this limitation when interpreting marginal baseline differences.
