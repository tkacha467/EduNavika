# EduNavika — Milestone 4 Preflight Audit Report

**Date:** October 2026  
**Audience:** Senior Full-Stack Architects, Educational Data Engineers, Backend QA Engineers  
**Target:** Milestone 4: Database Foundation, Curriculum Seeding & First Ingestion Pilot  
**Status:** AUDIT COMPLETE — READY FOR ARCHITECTURAL SIGN-OFF

---

## 1. Executive Summary & Repository State

This preflight audit inspects the current local repository, database targets, migration frameworks, test baselines, and architectural contracts before executing Milestone 4 changes.

### 1.1 Git Status & Commit Lineage
- **Active Branch:** `master` (synchronized with `origin/master`).
- **Working Tree:** Clean (zero uncommitted files).
- **Recent Commits:**
  - `38cdc93`: `docs(milestone-3): deliver JEE/NEET curriculum and question-bank architecture, provenance, and validation report`
  - `2d70f6e`: `chore(cleanup): execute Milestone 2 safe cleanup, decouple dead services, archive reports, and verify build`
  - `b8d1eba`: `fix(practice): resolve student profile in submit_practice_answer and event_recorder to eliminate foreign key 500 error`

### 1.2 Documentation Assets Reviewed
- `docs/CURRICULUM_ARCHITECTURE.md`: 5-tier relational hierarchy, zero-duplication model for Physics/Chemistry, chapter/topic taxonomy for Standards 11 & 12.
- `docs/QUESTION_BANK_SCHEMA.md`: Multi-exam question schema (SCQ, MCQ_MULTI, NUMERICAL, ASSERTION_REASON), KaTeX/LaTeX formatting, Pydantic v2 schemas, and provenance metadata.
- `docs/DATASET_ACQUISITION_AND_PROVENANCE.md`: Section 52 Fair Dealing compliance, 13 preserved science textbook analysis, 9-stage ingestion pipeline, and human-in-the-loop SME review workflows.
- `docs/MILESTONE_3_VALIDATION_REPORT.md`: Baseline forensic audit of `edunavika.db`.

---

## 2. Configured Database Target & Schema State

### 2.1 Database Target Identification
- **Engine:** SQLite 3 (WAL mode enabled, foreign keys enforced via connection pragma).
- **Configured URI:** `settings.DATABASE_URL = "sqlite:///./edunavika.db"` (defined in `backend/app/core/config.py`).
- **File Location:** `d:/EduSens/edunavika.db` (local SQLite database file).
- **Active Migration Framework:** Alembic (configured in `backend/alembic.ini` and `backend/alembic/env.py`).
- **Current Alembic Revision:** `e025394444f5` (head of existing migration chain).

### 2.2 Existing Database Entity Inventory
A forensic count of all 21 tables in `edunavika.db`:
- `standards`: 1 row (Grade 10, 'Standard 10')
- `subjects`: 239 rows (9 authentic Standard 10 curriculum subjects; 230 historical synthetic test fixtures)
- `chapters`: 288 rows (curriculum chapters under Standard 10)
- `topics`: 505 rows (curriculum subtopics)
- `learning_contents`: 573 rows (textbook chunks with page-level citations)
- `mcq_questions`: 80 rows (Standard 10 Science & Technology questions, 100% published)
- `users`: 244 rows
- `student_profiles`: 243 rows
- `teacher_profiles`: 0 rows
- `learning_events`: 776 rows
- `topic_performances`: 149 rows
- `revision_plans`: 21 rows
- `forgetting_signals`: 10 rows
- `alembic_version`: 1 row (`e025394444f5`)

---

## 3. Data Model Comparison & Reuse Strategy

| Target Entity | Existing Implementation in Codebase | Proposed Milestone 4 Strategy | Reuse / Additive Decision |
| :--- | :--- | :--- | :--- |
| **Examinations** | Does not exist | Add `examinations` table (JEE_MAIN, JEE_ADVANCED, NEET_UG). | **New Additive Table** |
| **Exam-Subject Links** | Does not exist | Add `exam_subjects` associative table to link canonical subjects without duplicating content. | **New Additive Table** |
| **Exam Papers / Shifts** | Does not exist | Add `exam_papers` master table (year, session, shift, paper code, source PDF hash). | **New Additive Table** |
| **Standards (Grades)** | `backend/app/models/curriculum_models.py` (`Standard`) | Seed Grade 11 (`Standard 11`) and Grade 12 (`Standard 12`). | **Reuse Existing Table** |
| **Subjects** | `backend/app/models/curriculum_models.py` (`Subject`) | Seed canonical Physics, Chemistry, Mathematics, and Biology for Standards 11 & 12. | **Reuse Existing Table** |
| **Chapters & Topics** | `backend/app/models/curriculum_models.py` (`Chapter`, `Topic`) | Seed canonical science chapters & topics mapped to the 13 preserved textbooks. | **Reuse Existing Tables** |
| **Questions (Canonical Bank)** | Legacy `mcq_questions` table (rigid 4-option schema) | Add `questions` table supporting SCQ, MCQ_MULTI, NUMERICAL, AR, MATCH, LaTeX, provenance, and evaluation policies. | **New Additive Table** (keep `mcq_questions` intact for backward compatibility) |
| **Question Options** | Flattened columns (`option_a`...`option_d` in `mcq_questions`) | Add `question_options` table supporting 1-to-N options with keys and explanations. | **New Additive Table** |
| **Verification / Audit Log** | Does not exist | Add `question_verification_logs` to record SME reviews, status transitions, and NTA answer key revisions. | **New Additive Table** |
| **Learning Content (RAG)** | `backend/app/models/curriculum_models.py` (`LearningContent`) | Store Class 11–12 textbook chunks with exact page citations and hash IDs. | **Reuse Existing Table** |

---

## 4. Root Cause Analysis: Test Suite Pollution & Test Isolation Plan

### 4.1 Root Cause Identified
In `conftest.py`, a clean in-memory database `test_engine = create_engine("sqlite://", poolclass=StaticPool)` and FastAPI client override `app.dependency_overrides[get_db]` were established. However:
- **8 test files directly imported `from backend.app.core.database import SessionLocal`:**
  - `backend/tests/test_audit_repairs.py`
  - `backend/tests/test_curriculum_coverage_and_runtime.py`
  - `backend/tests/test_explanation.py`
  - `backend/tests/test_knowledge_profile.py`
  - `backend/tests/test_misconception_remediation.py`
  - `backend/tests/test_progress_tracking.py`
  - `backend/tests/test_recommendations.py`
  - `backend/tests/test_retrieval.py`
- When these test files ran, their module-level fixtures executed `db = SessionLocal()`, which established a live connection directly to `settings.DATABASE_URL` (`./edunavika.db`) rather than the test database, inserting synthetic test subjects (`SE_050128`, `Sub-1760088924`, etc.) and test user profiles directly into the production SQLite file.

### 4.2 Mandatory Test Isolation Fix for Milestone 4
1. **Dynamic Engine Redirection in Test Mode:** Configure `backend/tests/conftest.py` so that `backend.app.core.database.SessionLocal` is monkeypatched to point to `TestingSessionLocal` across the entire test session.
2. **Database Write Guard:** Add an automated assertion fixture verifying that `edunavika.db` file size and row counts do not change during test suite execution.
3. **Safe Preservation:** Existing synthetic records in `edunavika.db` will remain untouched in this milestone to prevent breaking historical test fixtures, but zero new synthetic records will be permitted.

---

## 5. Baseline Test Execution Results

### 5.1 Frontend Suite (Vitest)
- **Command:** `npm test` in `frontend/`
- **Result:** **20 passed (100%)**
- **Duration:** 1.49s
- **Status:** Baseline established with zero errors.

### 5.2 Backend Suite (Pytest)
- **Command:** `pytest -m "not slow and not integration" --ignore=backend/tests/test_rag_contracts.py --ignore=backend/tests/test_retrieval_embeddings.py --ignore=backend/tests/test_retrieval_rrf.py --ignore=backend/tests/test_retrieval_vector_store.py --ignore=backend/tests/test_targeted_math_pipeline.py`
- **Passed:** **345 tests**
- **Failed:** **5 tests** (Legacy assertions from Milestone 1/2):
  - `test_ingestion_scanner.py` (2 tests): Asserts hardcoded `len(docs) == 86` (pre-cleanup count).
  - `test_ocr_and_structure_auditors.py` (2 tests): Asserts 86 PDFs.
  - `test_chunk_and_provenance_auditors.py` (1 test): Verifies source path against `STD-10/` instead of `STD-10th/`.
- **Ignored / Optional ML Dependencies:** 5 test files requiring `sentence-transformers` and `pymupdf` (optional on-device ML/OCR extras).

---

## 6. Database Safety & Verified Backup Evidence (Gate 1 Passed)

Before executing any database DDL migration or curriculum seeding, a native SQLite backup was performed using Python's `sqlite3.Connection.backup()` API.

### 6.1 Gate 1 Execution Log & Artifact Verification
- **Execution Script:** `scripts/create_verified_backup.py`
- **Execution Timestamp:** `2026-10-15T08:09:53.488371+00:00` (UTC)
- **Source Database:** `D:\EduNavika\edunavika.db` (Size: 3,874,816 bytes)
- **Backup Destination:** `D:\EduNavika\backups\milestone_4_pre_migration\edunavika_pre_m4.db` (Size: 3,874,816 bytes)
- **WAL Journal State:** WAL passive checkpoint returned `(0, 0, 0)`; WAL file flush confirmed.
- **Git Exclusion Status:** Verified via `git status` — `backups/` and `*.db` are strictly excluded by `.gitignore`.

### 6.2 Independent Backup Verification Results
- **Integrity Check:** `PRAGMA integrity_check` returned `[('ok',)]` (100% clean).
- **Foreign Key Check:** `PRAGMA foreign_key_check` returned `0` violations.
- **Alembic Revision Check:** Active revision `e025394444f5` verified intact in the backup.
- **Table Count Verification:** Exactly 21 tables match between source and backup.
- **Row-by-Row Reconciliation (100% Match):**
  - `alembic_version`: 1
  - `standards`: 1
  - `subjects`: 239
  - `chapters`: 288
  - `topics`: 505
  - `learning_contents`: 573
  - `mcq_questions`: 80
  - `users`: 244
  - `student_profiles`: 243
  - `learning_events`: 776
  - `topic_performances`: 149
  - `revision_plans`: 21
  - `forgetting_signals`: 10
  - `learning_quests`: 3
  - All remaining empty tables (`answers`, `attempts`, `assessments`, `assessment_questions`, `question_history`, `teacher_actions`, `teacher_profiles`): 0 rows.

**Gate 1 Verdict:** PASSED & VERIFIED.

---

## 7. Revised Migration Design & Schema Specification (Pre-Application Review)

Following architectural review, the migration design was substantially refined to address legal rights defaults, unverified/missing extraction tolerance, relational consistency, and NULL-safe paper identification.

### 7.1 Separation of Source Type, Rights Status, and Publish Permissions
Public accessibility does **not** equate to permission to redistribute. The schema decouples provenance from legal standing:
1. **`source_type` (Provenance Origin):**
   - `'OFFICIAL_PYQ'`: Public statutory examination paper (NTA / IIT JAB).
   - `'NCERT_EXEMPLAR'`: NCERT problem corpus.
   - `'GSEB_QUESTION_BANK'`: Gujarat State Board assessment item.
   - `'CURATED_PRACTICE'`: Verified proprietary textbook exercises.
   - `'SYNTHETIC_LLM'`: AI-generated practice draft.
2. **`rights_status` (Statutory / License Classification):**
   - **`'PENDING_LEGAL_REVIEW'` (Default):** Assigned to all newly ingested items until formal IP review.
   - `'EDUCATIONAL_STATUTORY_EXEMPTION'`: Section 52(1)(h) Indian Copyright Act fair dealing.
   - `'LICENSED_CC_BY_SA_4_0'`: Open-licensed attribution materials.
   - `'PROPRIETARY_RESERVED'`: Exclusive EduNavika curriculum assets.
   - `'REDISTRIBUTION_RESTRICTED'`: Protected third-party material; internal reference only.
3. **`publish_permission` (Platform Distribution Authorization):**
   - **`'FORBIDDEN'` (Default):** Questions cannot be exposed to student accounts or public endpoints.
   - `'RESTRICTED_STUDY_ONLY'`: Eligible for internal student self-study without public syndication.
   - `'PERMITTED_PUBLIC'`: Fully cleared for practice tests, diagnostic exams, and exports.
   - `'TAKEN_DOWN'`: Withdrawn upon challenge or legal notice.

### 7.2 Missing Solutions, Unverified Answer Keys & Scoring Eligibility
Extraction pipelines often extract question stems before complete solutions or final revised keys are available:
- **`solution_text` is NULLABLE:** Questions without detailed derivations remain valid records.
- **`correct_answer_raw` is NULLABLE:** Questions pending answer-key publication are ingested safely.
- **`answer_verification_status`:** `'UNVERIFIED'` (Default), `'PROVISIONAL_KEY'`, `'FINAL_KEY_RECONCILED'`, `'SME_CONFIRMED'`, `'DISPUTED'`.
- **Strict Scoring Eligibility Predicate:**
  A question is **strictly ineligible** for scored adaptive practice unless all 6 conditions hold:
  $$\text{Eligible} \iff \begin{cases}
  \text{answer\_verification\_status} \in \{\text{'FINAL\_KEY\_RECONCILED'}, \text{'SME\_CONFIRMED'}\} \\
  \text{evaluation\_policy} \neq \text{'UNRESOLVED\_POLICY'} \\
  \text{publish\_permission} \in \{\text{'RESTRICTED\_STUDY\_ONLY'}, \text{'PERMITTED\_PUBLIC'}\} \\
  \text{verification\_status} = \text{'PUBLISHED'} \\
  \text{official\_status} \notin \{\text{'OFFICIALLY\_DROPPED'}, \text{'UNDER\_DISPUTE'}\} \\
  \text{quarantine\_status} = \text{'CLEAN'}
  \end{cases}$$
  Any violation automatically sets `eligibility_for_scoring` to an explicit ineligibility code (`INELIGIBLE_UNVERIFIED_KEY`, `INELIGIBLE_UNRESOLVED_POLICY`, `INELIGIBLE_DROPPED`, `INELIGIBLE_RIGHTS_HOLD`, `INELIGIBLE_QUARANTINE`).

### 7.3 Refined Numerical Evaluation Metadata
Numerical questions require granular, exam-grounded evaluation rather than an arbitrary global $\pm 0.01$ band:
- **`evaluation_policy`:** `'EXACT_CHOICE'`, `'MULTI_PARTIAL_JAB'`, `'NUMERICAL_EXACT_INT'`, `'NUMERICAL_DECIMAL_RANGE'`, `'UNRESOLVED_POLICY'` (Default).
- **`numerical_precision_type`:** `'INTEGER'`, `'DECIMAL_2DP'`, `'DECIMAL_INTERVAL'`, `'FLOAT_EPSILON'`, `'NOT_APPLICABLE'`.
- **`numerical_min_val` & `numerical_max_val`:** Stored as exact double precision floats for valid intervals $[v_{\min}, v_{\max}]$.
- **`numerical_tolerance_epsilon`:** Stored when official circulars permit rounding bounds (e.g. $\pm 0.05$).
- **`scoring_policy_version` & `scoring_policy_source`:** Explicit audit citation (e.g., `"NTA JEE Main 2024 Information Bulletin Section 5.3"`).
- **Quarantine Safeguard:** Any numerical question where the evaluation rule is unverified remains set to `evaluation_policy = 'UNRESOLVED_POLICY'`, forcing `eligibility_for_scoring = 'INELIGIBLE_UNRESOLVED_POLICY'`.

### 7.4 Relational Consistency & Curriculum Anchor
To prevent conflicting foreign-key hierarchies (e.g. specifying a `topic_id` that belongs to Chapter 1, but mistakenly attaching `chapter_id = 2`):
- **Canonical Leaf FK:** `topic_id` (`ForeignKey("topics.id", ondelete="RESTRICT")`) is the single authoritative curriculum relationship on `questions`.
- Chapter, Subject, and Standard are strictly derived through the existing relational hierarchy (`Topic` $\rightarrow$ `Chapter` $\rightarrow$ `Subject` $\rightarrow$ `Standard`).
- **Exam Associativity (`exam_subjects`):** Canonical subjects link to examinations (`JEE_MAIN`, `JEE_ADVANCED`, `NEET_UG`) via `(exam_code, subject_id) UNIQUE`.

### 7.5 NULL-Safe Paper Identity (`paper_identifier`)
In SQL engines (including SQLite), multi-column unique constraints on columns containing `NULL` (such as `paper_code`) allow duplicate rows.
- **Solution:** Added a mandatory non-null canonical slug:
  `paper_identifier VARCHAR(128) NOT NULL UNIQUE`
  Constructed deterministically:
  `f"{exam_code}:{exam_year}:{slugify(session_or_shift)}:{paper_code or 'DEFAULT'}"`
  Example: `'JEE_MAIN:2024:session_1_jan_29_shift_1:DEFAULT'`.

### 7.6 Explicit Statuses for Dropped, Bonus, and Quarantined Questions
- **`official_status`:** `'REGULAR'`, `'OFFICIALLY_DROPPED'`, `'OFFICIALLY_BONUS'`, `'OFFICIALLY_AMBIGUOUS_REVISED_KEY'`, `'UNDER_DISPUTE'`.
- **`official_status_evidence`:** Text field capturing the official NTA/IIT circular reference number, public notice URL, and decision date.
- **`quarantine_status` & `quarantine_reason`:** Explains why an item failed validation (e.g., `"Unbalanced KaTeX display delimiters"`, `"Omitted answer key in source PDF"`).
- **Audit Preservation:** Officially dropped questions are **never deleted**. They remain auditable and searchable, but are excluded from scored student tests.

---

## 8. Migration Downgrade Consequences & Rollback Protocol

### 8.1 Consequences of Migration Downgrade
If `alembic downgrade e025394444f5` is executed:
1. The 6 new tables (`question_verification_logs`, `question_options`, `questions`, `exam_papers`, `exam_subjects`, `examinations`) will be **permanently dropped**.
2. Any ingested competitive exam papers, questions, KaTeX formulas, verification logs, and rights records will be **destroyed**.
3. All legacy tables (`standards`, `subjects`, `chapters`, `topics`, `learning_contents`, `mcq_questions`) will remain **completely untouched**.
4. The database version will revert to `e025394444f5`.

### 8.2 Mandatory Pre-Migration & Pre-Rollback Protocol
- **Strict Rule:** A verified SQLite native backup (using `scripts/create_verified_backup.py`) must be executed immediately before running ANY migration or rollback on persistent databases.
- If data preservation is required prior to rollback, an export script must dump `questions` and `exam_papers` to JSON/Parquet before the downgrade is issued.

---

## 9. Migration Test Evidence on Disposable Sandbox (Gate 2 Verified)

To ensure zero risk to `edunavika.db`, the entire migration lifecycle was executed on an isolated temporary sandbox (`temp_migration_sandbox.db`) via `scripts/test_migration_lifecycle.py`.

### 9.1 Test Execution Output (Exact Terminal Log)
```
--- 1. Creating Disposable Sandbox Copy of Database ---
Created sandbox at D:\EduNavika\temp_migration_sandbox.db (Size: 3874816 bytes)
Pre-migration Alembic revision: e025394444f5
Pre-migration tables count: 21
Pre-migration baseline: standards=1, subjects=239, mcqs=80

--- 2. Executing Alembic Upgrade to Head (Subprocess) ---
Post-upgrade foreign key violations: 0
Post-upgrade Alembic revision: f1e2d3c4b5a6
Post-upgrade tables count: 27 (Added 6 tables)
[VERIFIED] Expected 6 new tables present: ['exam_papers', 'exam_subjects', 'examinations', 'question_options', 'question_verification_logs', 'questions']
[VERIFIED] All 20 pre-existing data tables preserved 100% of rows.

--- 3. Testing Sample Records Insertion in Sandbox ---
[VERIFIED] Inserted sample unverified numerical question with NULL solution and NULL answer key cleanly.
[VERIFIED] Duplicate paper_identifier with NULL paper_code successfully blocked by UNIQUE constraint.

--- 4. Executing Alembic Downgrade to e025394444f5 (Subprocess) ---
Post-downgrade Alembic revision: e025394444f5 (Rolled back successfully)
[VERIFIED] Exactly 21 legacy tables remain after downgrade.
[VERIFIED] All pre-existing table row counts 100% identical after downgrade.

--- Disposable Sandbox Cleaned Up ---
[SUCCESS] Complete migration lifecycle (Upgrade -> Insertion -> Rollback) verified 100% safe and reversible!
```

### 9.2 Verification Confirmations
1. **Additive Schema:** Exactly 6 tables added during upgrade; 0 pre-existing tables modified or dropped.
2. **Data Preservation:** All 20 pre-existing data tables preserved 100% of rows through upgrade and downgrade.
3. **NULL-Safe Uniqueness:** Duplicate papers with `paper_code = NULL` were successfully blocked by `paper_identifier`.
4. **Missing-Data Support:** Questions with missing solutions and unverified keys insert cleanly with default ineligibility.
5. **Clean Rollback:** Downgrade to `e025394444f5` completed with zero foreign key errors or orphaned schema objects.
6. **Zero Persistent Mutation:** `edunavika.db` remained byte-for-byte untouched throughout the test.

---

## 10. Test Isolation Architecture & Hardening Blueprint (Gate 3)

### 10.1 Identified Database Leakage Vectors
1. **Cached `SessionLocal` Module Imports:** 8 test files imported `from backend.app.core.database import SessionLocal` at module scope. If imported before fixture setup, sessions connected directly to `./edunavika.db`.
2. **Unmanaged `TestClient` Instances:** Creating `client = TestClient(app)` at module scope bypassed FastAPI dependency overrides.
3. **Default Configuration Values:** `settings.DATABASE_URL` defaulted to `sqlite:///./edunavika.db` unless explicitly overridden in the process environment.

### 10.2 Comprehensive Isolation Architecture
1. **Early Environment Injection:**
   Configure `os.environ["DATABASE_URL"] = "sqlite:///:memory:"` at the top of `backend/tests/conftest.py` before any application module is imported.
2. **Global Sessionmaker Redirection:**
   In `conftest.py`, dynamically monkeypatch `backend.app.core.database.SessionLocal` to point to `TestingSessionLocal` across all tests.
3. **Database Write Guard Regression Test (`backend/tests/test_database_isolation.py`):**
   A dedicated test that:
   - Records the SHA-256 checksum and row counts of `edunavika.db`.
   - Executes arbitrary CRUD operations, API requests, and service calls.
   - Asserts that `edunavika.db` file size, hash, and row counts are **identical byte-for-byte** before and after the test run.

---

## 11. Explicit Assumptions & Decisions Awaiting Approval

Before applying this migration to `edunavika.db`:
1. **Target Migration Revision:** `backend/alembic/versions/20261015_m4_canonical_curriculum_and_questions.py` (Revision ID: `f1e2d3c4b5a6`).
2. **Approval Gate:** Migration has NOT been applied to `edunavika.db`. Awaiting explicit user confirmation to proceed with `alembic upgrade head`.
