# EduNavika — Step 1: MCQ Reliability, Answer Grading, and Learning Accuracy Report
**Problem Statement:** PS-06 — On-Device Personalized Learning Assistant  
**Team:** Varja  
**Date:** 2026-10-10  
**Environment:** In-place on `D:\EduNavika` (Zero cloud AI dependencies; Teacher portal remains removed)

---

## 1. Confirmed Root Causes (With Files & Functions)

### A. Answer Grading Bug (Primary Root Cause of Unexpected 0% / Low Scores)
- **File:** [`backend/app/services/adaptive_practice.py`](file:///d:/EduNavika/backend/app/services/adaptive_practice.py)
- **Function:** `submit_answer(...)` (lines 670–710)
- **Mechanism:**
  - Frontend practice runner ([`QuizRunner.ts`](file:///d:/EduNavika/frontend/src/features/interactive/QuizRunner.ts) / [`StudentViews.ts`](file:///d:/EduNavika/frontend/src/features/student/StudentViews.ts)) submits option letters (`'A'`, `'B'`, `'C'`, `'D'`) or numeric indexes (`0`, `1`, `2`, `3`).
  - The previous code placed `options[opt_idx]` into `candidate_answers` without mapping the selected submission string to the chosen option text.
  - It then performed `selected_clean in candidate_answers`. Because `selected_clean` was `"a"` and `candidate_answers` contained only full sentences (e.g. `{"total mass of elements in products must equal total mass in reactants"}`), the condition evaluated to `False` on **100% of letter-based submissions**, recording 0.0 scores and false misconceptions for every correct student answer.

### B. Topic & Subject ID Resolution Mismatch Between Frontend and Backend
- **Files:** [`backend/app/services/topic_resolver.py`](file:///d:/EduNavika/backend/app/services/topic_resolver.py) & [`frontend/src/services/curriculumService.ts`](file:///d:/EduNavika/frontend/src/services/curriculumService.ts)
- **Functions:** `resolve_topic(...)` & `APPROVED_SUBJECTS`
- **Mechanism:**
  - Frontend UI components referenced placeholder topic IDs (`m1`, `m2`, `c1`, `p1`).
  - Backend `resolve_topic(...)` did not contain deterministic mappings for these keys and fell back to broad substring searches that resolved `m1` to `1.1 Introduction1` (an unindexed topic), returning empty question sets: `"This topic is not currently included in the verified offline Standard 10 curriculum"`.

### C. Mathematics Curriculum Coverage Gap & Phantom Bank Keys
- **File:** [`backend/app/services/curriculum_question_bank.py`](file:///d:/EduNavika/backend/app/services/curriculum_question_bank.py)
- **Constant:** `CANONICAL_CURRICULUM_BANK`
- **Mechanism:**
  - The Standard 10 Mathematics English textbook (`Std-10_Maths_EnglishMedium.pdf`, 11 MB) was already ingested with 126 chunks across 14 chapters in SQLite `learning_contents`.
  - However, `CANONICAL_CURRICULUM_BANK` only contained 2 Math topics (Real Numbers & Quadratic Equations) while 4 dictionary keys were non-existent phantom UUIDs. Critical topics like Arithmetic Progressions, Distance Formula, Trigonometric Ratios, Statistics, and Probability lacked validated entries in the question bank.

### D. SQLite Database Test Pollution
- **Database:** `edunavika.db` (`subjects` table)
- **Mechanism:**
  - 877 synthetic subjects (`Science Test X`, `Science Exp X`, `Science Rec X`) had accumulated from previous test runs directly invoking `SessionLocal()` instead of isolated in-memory test databases.

---

## 2. Before-and-After Behavior

| Flow | Before Fix | After Fix |
| :--- | :--- | :--- |
| **Student Practice Submission** | Selecting option "A" or "B" always returned `correct: False` (0% score) regardless of accuracy. | Both option letters (`'A'`), 0-based indices (`'0'`), and full text values evaluate with 100% correctness and update mastery curves authentically. |
| **Mathematics Practice Now** | Clicking "Practice Now" on Mathematics topics returned an empty question list or safe-scope error. | Instantly retrieves verified, textbook-grounded questions with exact page citations and explanations. |
| **Subject & Topic Mapping** | Frontend IDs (`m1`, `c1`) failed to match database entities. | `DIRECT_FRONTEND_MAP` and aligned `APPROVED_SUBJECTS` resolve immediately to canonical database UUIDs. |
| **Content Diagnostics** | No endpoint to check whether local textbook chunks or practice questions were ready. | `GET /api/v1/curriculum/diagnostic/{subject_or_topic}` returns structured `READY`, `NO_PRACTICE`, `MISSING_TEXTBOOK`, or `NOT_FOUND` status. |
| **Local Offline Fallback** | Failed DLL imports under OS Application Control policies could halt inference. | Deterministic curriculum bank fallback operates smoothly offline with zero external network requests. |

---

## 3. Files Changed and Reasons

1. **[`backend/app/services/adaptive_practice.py`](file:///d:/EduNavika/backend/app/services/adaptive_practice.py):**
   - Implemented bidirectional option-text and option-letter comparison in `submit_answer(...)`.
   - Resolves student option letters/indices into chosen option texts while simultaneously deriving valid option letters from correct answers.
2. **[`backend/app/services/topic_resolver.py`](file:///d:/EduNavika/backend/app/services/topic_resolver.py):**
   - Added `DIRECT_FRONTEND_MAP` for deterministic resolution of frontend IDs (`m1`, `m2`, `m3`, `m4`, `m5`, `c1`, `c2`, `p1`, `p2`).
   - Prioritized granular subject and chapter aliases before loose chapter title matching.
3. **[`backend/app/services/curriculum_question_bank.py`](file:///d:/EduNavika/backend/app/services/curriculum_question_bank.py):**
   - Expanded `CANONICAL_CURRICULUM_BANK` with 20 questions across 5 core Mathematics topics (Arithmetic Progressions, Coordinate Geometry, Trigonometry, Statistics, Probability).
   - Validated each question against the 10-point `CurriculumQuestionValidator` with exact chunk IDs and textbook page citations.
4. **[`backend/app/api/v1/endpoints/curriculum.py`](file:///d:/EduNavika/backend/app/api/v1/endpoints/curriculum.py):**
   - Added `GET /api/v1/curriculum/diagnostic/{subject_or_topic}` endpoint for checking textbook chunks and practice readiness.
5. **[`frontend/src/services/curriculumService.ts`](file:///d:/EduNavika/frontend/src/services/curriculumService.ts):**
   - Aligned `APPROVED_SUBJECTS` in frontend with canonical database UUIDs for Mathematics and Science topics.
6. **[`frontend/src/features/interactive/QuizRunner.ts`](file:///d:/EduNavika/frontend/src/features/interactive/QuizRunner.ts):**
   - Enhanced `startQuiz` to resolve effective topic IDs robustly from `APPROVED_SUBJECTS` using title and ID matching.
7. **[`backend/tests/test_audit_repairs.py`](file:///d:/EduNavika/backend/tests/test_audit_repairs.py):**
   - Automated regression suite verifying exact grading, incorrect answer grading, Math practice retrieval, diagnostic responses, shuffled option stability, and retry isolation.

---

## 4. Tests Actually Executed and Outcomes

### Backend Test Execution (`pytest`)
Ran comprehensive test suites using Python 3.11 virtual environment (`.venv\Scripts\pytest`):

```bash
.venv\Scripts\pytest backend/tests/test_audit_repairs.py backend/tests/test_adaptive_practice.py backend/tests/test_curriculum_assessment.py backend/tests/test_progress_tracking.py backend/tests/test_offline_ps06_loop.py backend/tests/test_closed_loop_personalization.py backend/tests/test_gamification.py backend/tests/test_multilingual_learning.py backend/tests/test_automated_revision_planning.py -v
```

**Results:** **100 passed, 0 failed** in 2.75s:
- `test_audit_repairs.py`: 6 passed (Option letter/index grading, incorrect grading, Math retrieval, diagnostics, shuffled options, retry isolation).
- `test_adaptive_practice.py`: 19 passed (Difficulty tiers, trend adjustment, learning event recording, offline fallback).
- `test_curriculum_assessment.py`: 14 passed (10-point question validator passed on all 44 canonical questions).
- `test_progress_tracking.py`: 16 passed (Accuracy math, mastery distributions, strength/weakness categorization).
- `test_offline_ps06_loop.py`: 3 passed (Offline curriculum availability, closed-loop personalization, multilingual invariance).
- `test_closed_loop_personalization.py`: 9 passed.
- `test_gamification.py`: 12 passed.
- `test_multilingual_learning.py`: 11 passed.
- `test_automated_revision_planning.py`: 10 passed.

### Frontend Test Execution (`vitest`)
Ran `npm test` inside `frontend`:
- **13 passed, 0 failed** across all UI suites.

### Frontend Production Build
Ran `npm run build` inside `frontend`:
- `tsc && vite build`: **Completed successfully in 336ms** with zero TypeScript or bundling errors.

---

## 5. Verification of Mathematics Real Local Content Flow

- **Physical Textbook Present:** `STD-10/Std-10_Maths_EnglishMedium.pdf` (11 MB).
- **SQLite Database Chunks:** 126 chunks across 14 chapters indexed under Subject ID `3a02d148-e961-4fea-bb5e-2320e4090bed`.
- **Verified Topics:**
  - Real Numbers / Fundamental Theorem of Arithmetic (Ch 1)
  - Quadratic Equations (Ch 4)
  - Arithmetic Progressions (Ch 5)
  - Coordinate Geometry / Distance Formula (Ch 7)
  - Introduction to Trigonometry (Ch 8)
  - Statistics / Mean of Grouped Data (Ch 13)
  - Probability (Ch 14)
- All questions retrieve authentic page citations (e.g. Pages 18, 53, 67, 117, 130, 186, 232) and pass source text support verification.

---

## 6. Remaining Limitations & Blockers

- **Windows Application Control Policy on `llama.dll`:** In this Windows environment, dynamic loading of precompiled `llama.dll` is blocked by Windows Application Control (`WinError 4551`). EduNavika's deterministic curriculum fallback immediately and gracefully handles this, fulfilling the zero-cloud, low-resource PS-06 requirement.
- **Language Models Ingestion Scope:** Additional Standard 10 supplementary subjects (e.g., Computer Studies, Commerce) are indexed in DB tables but do not yet have pre-curated question banks. They accurately report `NO_PRACTICE` via the new diagnostic endpoint.

---

## 7. Next Single Highest-Priority Task

- **Step 2:** Deepen adaptive misconception remediation by connecting student incorrect answers directly to targeted chunk excerpts in the local textbook so students can immediately review the specific page passage where their misconception originated.
