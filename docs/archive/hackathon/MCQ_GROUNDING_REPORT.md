# EduNavika — Textbook Grounding and MCQ Provenance Report
**Problem Statement:** PS-06 — On-Device Personalized Learning Assistant  
**Curriculum Standards:** GSEB / NCERT Standard 10 (English Medium)  
**Date:** 2026-10-10

---

## 1. Grounding Guarantee Overview

EduNavika enforces zero ungrounded generation. Every practice question and assessment item presented to the learner is mathematically and pedagogically traceable to official textbook pages stored in the local SQLite database (`learning_contents` table).

The system applies a strict 10-point `CurriculumQuestionValidator` enforcing:
1. Valid 4-option structure with non-empty distinct options.
2. Verified correct answer matching exactly one option.
3. Absence of generic template patterns ("which of the following best describes", "none of these", etc.).
4. Explicit source document citation matching local standard textbooks.
5. Explicit source page citation.
6. Traceable `source_chunk_id` verifying the chunk exists in local database storage.
7. Verification that the question's conceptual keywords exist in the source text.
8. Verification that the correct answer is directly supported by the source text.
9. Verification that the explanation is grounded in the source text.
10. Valid cognitive tier categorization (`FOUNDATIONAL`, `GUIDED`, `APPLICATION`, `CHALLENGE`).

---

## 2. Subject & Topic Provenance Inventory

### Subject: Science & Technology (Std 10 GSEB)
- **Textbook Document:** `STD-10/Std-10_Science_English Medium.pdf`
- **Total Chunks in DB:** 186 chunks across 13 chapters.
- **Representative Grounded Topics:**
  1. **Chemical Reactions and Equations** (`5a321a44-bc06-4db4-a50f-5e53f913b612`)
     - Chunk ID: `06f69c9e-137a-4d30-91af-93fd17e032b1` | Page 16: Law of Conservation of Mass.
     - Questions: `chem-ch1-f01`, `chem-ch1-f02`, `chem-ch1-g01`, `chem-ch1-g02`, `chem-ch1-a01`, `chem-ch1-c01`.
  2. **Acids, Bases and Salts** (`efee2da2-bd20-42bb-ad01-df2516530b1f`)
     - Chunk ID: `45be32ad-920f-488f-b983-cf2d29b0df4d` | Page 37: Hydrogen and Hydroxide ions.
     - Questions: `chem-ch2-f01`, `chem-ch2-g01`, `chem-ch2-a01`, `chem-ch2-c01`.
  3. **Electricity & Circuits** (`ea3cb4fd-f34d-409b-b0f6-d69b70db05b0`)
     - Chunk ID: `e0826cda-0685-42b0-a552-ed8d0d84b628` | Page 202: Joule's Law of Heating ($H = I^2Rt$).
     - Questions: `phys-ch11-f01`, `phys-ch11-g01`, `phys-ch11-a01`, `phys-ch11-c01`.

---

### Subject: Mathematics (Std 10 GSEB)
- **Textbook Document:** `STD-10/Std-10_Maths_EnglishMedium.pdf`
- **Total Chunks in DB:** 126 chunks across 14 chapters.
- **Representative Grounded Topics:**
  1. **Real Numbers & Fundamental Theorem of Arithmetic** (`e84e1b11-f928-4b38-93ad-738af5c0b1e5`)
     - Chunk ID: `042ae613-1a09-4660-87c7-4383df7031fa` | Page 18: Theorem 1.1 Unique Prime Factorisation.
     - Chunk ID: `475ed206-658d-4adc-952c-8a6f39d5c138` | Page 20: HCF × LCM = a × b.
     - Questions: `math-ch1-f01`, `math-ch1-g01`, `math-ch1-a01`, `math-ch1-c01`.
  2. **Quadratic Equations** (`c3dd6779-9b5b-411c-9ade-07e241713835`)
     - Chunk ID: `6f64b243-a2d9-485c-a106-1406a3e13cd5` | Page 53: Standard form $ax^2 + bx + c = 0$, Sridharacharya Formula.
     - Chunk ID: `e3ea0fc7-718a-4210-992c-6bcd8f6b7a4d` | Page 59: Discriminant analysis $b^2 - 4ac < 0$.
     - Questions: `math-ch4-f01`, `math-ch4-g01`, `math-ch4-a01`, `math-ch4-c01`.
  3. **Arithmetic Progressions** (`1d70ba4e-6c09-432c-b740-604677902d40`)
     - Chunk ID: `d30e23d8-966e-4404-b34e-ba946965dae8` | Page 67: Common difference $d = a_2 - a_1$.
     - Chunk ID: `767367f7-a4d6-4f87-8f76-4a3dd4211f97` | Page 68: Succeeding term property.
     - Chunk ID: `15e07cf2-40df-4a0e-b413-728de49b6e86` | Page 73: General term $a_n = a + (n - 1)d$.
     - Chunk ID: `4878bb68-aeeb-4e34-ab37-4e49074162a3` | Page 77: Exercise 5.2 30th term calculation.
     - Questions: `math-ap-f01`, `math-ap-g01`, `math-ap-a01`, `math-ap-c01`.
  4. **Coordinate Geometry — Distance Formula** (`17550e06-fb15-412d-b6a9-97d3c3848c70`)
     - Chunk ID: `b6c1a497-b7ff-4277-b3a9-0d8117d0bca4` | Page 117: Distance formula $PQ = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$, Origin distance.
     - Chunk ID: `1d5888c8-ca92-4b4f-89c0-03f2ba89bdd8` | Page 115: Axis collinear points and Pythagoras application.
     - Questions: `math-coord-f01`, `math-coord-g01`, `math-coord-a01`, `math-coord-c01`.
  5. **Introduction to Trigonometry** (`a5d04c19-6e6b-4a88-a23b-414f71308ba9`)
     - Chunk ID: `eac2327c-c8fe-4f82-bda7-e2f02b4a0723` | Page 130: Trigonometric ratios sine, tangent, secant definitions.
     - Chunk ID: `d2c8ff78-537b-4e3a-8494-d199625a204d` | Page 129: Etymology and real-world angle subtensions.
     - Questions: `math-trig-f01`, `math-trig-g01`, `math-trig-a01`, `math-trig-c01`.
  6. **Statistics** (`20d70d12-d01a-44d7-82be-772d609eb4f5`)
     - Chunk ID: `404252b7-f178-47af-a83e-9db0f98d3258` | Page 186: Measures of central tendency (mean, median, mode).
     - Chunk ID: `78536fe8-ea18-4a8d-b314-085af1965a83` | Page 188: Direct method mean $\bar{x} = \frac{\sum f_i x_i}{\sum f_i}$.
     - Chunk ID: `9969c79a-2641-4105-bea6-d785fb579e21` | Page 189: Class mark calculation.
     - Chunk ID: `6afa8682-bf0b-4b85-8f8d-f1793c3e1c26` | Page 194: Assumed mean method $d_i = x_i - a$.
     - Questions: `math-stats-f01`, `math-stats-g01`, `math-stats-a01`, `math-stats-c01`.
  7. **Probability** (`dba2e106-7967-4de4-892b-934b06a17b2f`)
     - Chunk ID: `8c5d4757-b64e-4ad8-9b8a-416a912ada3d` | Page 232: Empirical vs theoretical probability, law of large numbers, coin sample space.
     - Questions: `math-prob-f01`, `math-prob-g01`, `math-prob-a01`, `math-prob-c01`.

---

## 3. Automated Validation Results

All 44 canonical questions across Science and Mathematics undergo automated verification via `test_curriculum_assessment.py`:
- `test_validator_passes_all_canonical_curriculum_questions`: **PASSED**
- `test_every_question_has_curriculum_source_and_page`: **PASSED**
- `test_question_is_supported_by_source_text`: **PASSED**
- `test_correct_answer_is_supported_by_source`: **PASSED**
- `test_explanation_is_supported_by_source`: **PASSED**
