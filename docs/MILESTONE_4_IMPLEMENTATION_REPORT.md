# EduNavika — Milestone 4 Implementation Report

**Milestone:** Milestone 4: Database Foundation, Curriculum Seeding & First Ingestion Pilot  
**Phases Completed:** 
- Phase A (Database Migration `f1e2d3c4b5a6` Applied & Verified)
- Phase B (Idempotent Curriculum Seeding & Textbook Corpus Analysis)  
**Date:** October 2026  
**Audience:** Full-Stack Architects, Educational Data Engineers, Backend QA Engineers  
**Status:** PHASES A & B COMPLETE — AWAITING PHASE C (TEST ISOLATION) APPROVAL

---

## 1. Executive Summary

Phases A and B of Milestone 4 have been successfully executed and validated against the local development database (`edunavika.db`).

### Core Accomplishments across Phases A & B:
1. **Fresh Pre-Migration Native Backup:** Captured and verified via Python's native `sqlite3.Connection.backup()` API at `backups/milestone_4_pre_migration/edunavika_pre_m4.db`.
2. **Alembic Additive Migration Applied:** Applied migration `f1e2d3c4b5a6` (`milestone_4_canonical_curriculum_and_questions`).
3. **Active Revision Upgraded:** Database successfully upgraded from `e025394444f5` to `f1e2d3c4b5a6`.
4. **Idempotent Curriculum Seeding Executed:** Seeded 3 competitive examinations (`JEE_MAIN`, `JEE_ADVANCED`, `NEET_UG`), Standards 11 and 12, and 8 canonical STEM subjects.
5. **Zero-Duplication Cross-Exam Association:** Created 18 explicit `exam_subjects` mappings. Physics and Chemistry map across all 3 exams without duplicating records; Mathematics is restricted to JEE; Biology is restricted to NEET.
6. **100% Idempotency Verified:** Re-running the seeder generated 0 duplicates and reported all 31 records already existing.
7. **Legacy Standard 10 Protection:** All 2,829 legacy records (including Standard 10, subjects, chapters, topics, MCQs, and users) remain 100% intact.
8. **Textbook Corpus Inspection Completed:** All 13 preserved Science textbooks (2,803 pages) were verified for page counts, file sizes, and SHA-256 hashes.

---

## 2. Pre-Migration Verification & Backup Evidence

Immediately prior to running the migration, the local development database was snapshotted:
- **Timestamp (UTC):** `2026-10-15T08:28:04.949470+00:00`
- **Source Database:** `D:\EduNavika\edunavika.db` (Size: 3,874,816 bytes)
- **Backup Location:** `D:\EduNavika\backups\milestone_4_pre_migration\edunavika_pre_m4.db` (Size: 3,874,816 bytes)
- **WAL Flush:** Passive checkpoint executed; 0 bytes WAL journal remaining.
- **Integrity & Foreign Keys:** `PRAGMA integrity_check` returned `ok`; `0` foreign key violations.
- **Git Exclusion:** Verified that `backups/` and `*.db` are excluded by `.gitignore`.

---

## 3. Migration Application Execution Log (Phase A)

The migration was applied using the project's standard Alembic toolchain:

```
> python -m alembic -c backend/alembic.ini upgrade head

INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade e025394444f5 -> f1e2d3c4b5a6, milestone_4_canonical_curriculum_and_questions
```
Exit code: `0` (Success).

---

## 4. Phase B: Canonical Curriculum Seeding & Idempotency Evidence

### 4.1 Seeder Implementation (`backend/app/db/seed_canonical_curriculum.py`)
The curriculum seeder was implemented with:
- **Deterministic UUIDv5 Identifiers:** Primary keys derived from domain keys (e.g., `edunavika.standard.11`, `edunavika.subject.std11.physics`, `edunavika.exam_subject.JEE_MAIN.PHYS11`).
- **Idempotent Checks:** Queries existing records by natural keys (`code`, `grade_number`, `(standard_id, code)`, `(exam_code, subject_id)`) prior to insertion.
- **CLI Options:** Supports `--dry-run` and `--db-url`.
- **Atomic Transactions:** Fails safely and rolls back on any constraint error.

### 4.2 Sandbox Test Verification (7 Out of 7 Tests Passed)
The seeder was verified against a disposable sandbox copy via `scripts/test_seed_canonical_curriculum.py`:
1. `Test 1 (Dry-Run)`: Planned 3 exams, 2 standards, 8 subjects, 18 links with 0 database writes. (PASSED)
2. `Test 2 (Clean Live Seed)`: Successfully inserted all 31 records with 0 FK violations. (PASSED)
3. `Test 3 (Idempotency on Second Run)`: 0 records created, 31 reported already existing. (PASSED)
4. `Test 4 (Standard 10 Preservation)`: Standard 10 records completely unmodified. (PASSED)
5. `Test 5 (Cross-Exam Association Rules)`: Physics (6), Chemistry (6), Math strictly JEE (4), Bio strictly NEET (2). (PASSED)
6. `Test 6 (Transaction Safety)`: Forced constraint violation rolled back cleanly. (PASSED)
7. `Test 7 (Persistent DB Guard)`: Persistent database confirmed untouched during testing. (PASSED)

### 4.3 Live Execution Output on `edunavika.db`

#### First Live Run (Creation):
```
--- EduNavika Canonical Curriculum Seeder ---
Target Database: sqlite:///./edunavika.db
Mode: LIVE SEED

--- Seeding Summary ---
Examinations:  +3 created, 0 already existing
Standards:     +2 created, 0 already existing
Subjects:      +8 created, 0 already existing
Exam-Subjects: +18 created, 0 already existing

Details:
  * Created examination 'JEE_MAIN' (National Testing Agency).
  * Created examination 'JEE_ADVANCED' (IIT Joint Admission Board).
  * Created examination 'NEET_UG' (National Testing Agency).
  * Created Standard 11 ('Standard 11').
  * Created Standard 12 ('Standard 12').
  * Created Subject 'PHYS11' (Physics) for Grade 11.
  * Created Subject 'CHEM11' (Chemistry) for Grade 11.
  * Created Subject 'MATH11' (Mathematics) for Grade 11.
  * Created Subject 'BIO11' (Biology) for Grade 11.
  * Created Subject 'PHYS12' (Physics) for Grade 12.
  * Created Subject 'CHEM12' (Chemistry) for Grade 12.
  * Created Subject 'MATH12' (Mathematics) for Grade 12.
  * Created Subject 'BIO12' (Biology) for Grade 12.
  * Linked 'JEE_MAIN' to 'PHYS11', 'CHEM11', 'MATH11', 'PHYS12', 'CHEM12', 'MATH12'.
  * Linked 'JEE_ADVANCED' to 'PHYS11', 'CHEM11', 'MATH11', 'PHYS12', 'CHEM12', 'MATH12'.
  * Linked 'NEET_UG' to 'PHYS11', 'CHEM11', 'BIO11', 'PHYS12', 'CHEM12', 'BIO12'.
  * [COMMIT] Committed all changes cleanly to database.
```

#### Second Live Run (Idempotency Proof):
```
--- EduNavika Canonical Curriculum Seeder ---
Target Database: sqlite:///./edunavika.db
Mode: LIVE SEED

--- Seeding Summary ---
Examinations:  +0 created, 3 already existing
Standards:     +0 created, 2 already existing
Subjects:      +0 created, 8 already existing
Exam-Subjects: +0 created, 18 already existing
```

---

## 5. Post-Seeding Database State & Row Count Reconciliation

| Table Name | Baseline (Pre-M4) | Post-Phase A | Post-Phase B | Net Change | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `alembic_version` | 1 | 1 | 1 | 0 | `f1e2d3c4b5a6` |
| `standards` | 1 | 1 | **3** | +2 | Seeded Standards 11 & 12 |
| `subjects` | 239 | 239 | **247** | +8 | Seeded 8 canonical STEM subjects |
| `examinations` | 0 | 0 | **3** | +3 | `JEE_MAIN`, `JEE_ADVANCED`, `NEET_UG` |
| `exam_subjects` | 0 | 0 | **18** | +18 | Cross-exam zero-duplication links |
| `chapters` | 288 | 288 | 288 | 0 | **UNCHANGED** (Reserved for validated ingestion) |
| `topics` | 505 | 505 | 505 | 0 | **UNCHANGED** (Reserved for validated ingestion) |
| `learning_contents` | 573 | 573 | 573 | 0 | **UNCHANGED** |
| `mcq_questions` | 80 | 80 | 80 | 0 | **UNCHANGED** |
| `users` | 244 | 244 | 244 | 0 | **UNCHANGED** |
| `student_profiles` | 243 | 243 | 243 | 0 | **UNCHANGED** |
| `learning_events` | 776 | 776 | 776 | 0 | **UNCHANGED** |
| `topic_performances` | 149 | 149 | 149 | 0 | **UNCHANGED** |
| `questions` | 0 | 0 | 0 | 0 | Ready for Pipeline A pilot |
| `exam_papers` | 0 | 0 | 0 | 0 | Ready for Pipeline A pilot |

- **Integrity Check:** `[('ok',)]` (100% clean)
- **Foreign Key Violations:** `0` violations

---

## 6. Source-to-Curriculum Mapping Report (13 Science Textbooks)

In accordance with Phase B instructions, all 13 preserved Science textbooks in `GSEB-Dataset/` were inspected and cataloged prior to any chapter/topic insertion:

| Filename | Class | Subject | Part | Pages | Size (MB) | SHA-256 Checksum | Exam Suitability |
| :--- | :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| `Std-11_Physics Part 1_English Medium.pdf` | 11 | Physics | Part 1 | 186 | 9.53 | `68113b0fdfecf722955f1f9ea04da3aa...` | JEE Main, JEE Adv, NEET |
| `Std-11_Physics Part 2_English Medium.pdf` | 11 | Physics | Part 2 | 164 | 4.35 | `53a63c453e1dc1ec9092dca2ea0ea3b5...` | JEE Main, JEE Adv, NEET |
| `Std-11_Chemistry Part-1_English Medium.pdf` | 11 | Chemistry | Part 1 | 254 | 12.26 | `07bb989e5620302b1f062c3e414c77ea...` | JEE Main, JEE Adv, NEET |
| `Std-11_Chemistry Part-2_English Medium.pdf` | 11 | Chemistry | Part 2 | 110 | 4.01 | `5fe7ff2ddea8358d35e0766373b5bf53...` | JEE Main, JEE Adv, NEET |
| `Std-11_Maths_EnglishMedium.pdf` | 11 | Mathematics | Complete | 376 | 43.18 | `7a6e43c4632fb53fef3c7347ad68b98b...` | JEE Main, JEE Adv |
| `Std-11_Bilology_EnglishMedium.pdf` | 11 | Biology | Complete | 266 | 38.19 | `fc1a1a70e4168ce0eeb2e2567ea3d312...` | NEET UG |
| `Std-12_Physics Part-1_English Medium.pdf` | 12 | Physics | Part 1 | 235 | 7.09 | `770bd4beb44ff61f95c8629ca55c28ad...` | JEE Main, JEE Adv, NEET |
| `Std-12_Physics Part-2_English Medium.pdf` | 12 | Physics | Part 2 | 152 | 6.53 | `fcf006583855ca50787e6fae1cf30d70...` | JEE Main, JEE Adv, NEET |
| `Std-12_Chemistry Part-1_EnglishMedium.pdf` | 12 | Chemistry | Part 1 | 172 | 13.59 | `c89255e0dbb7d59c693a74ae877b0eeb...` | JEE Main, JEE Adv, NEET |
| `Std-12 Chemistry Part-2_EnglishMedium.pdf` | 12 | Chemistry | Part 2 | 164 | 10.95 | `a9317b03f86d3ce6b25ea031b2502693...` | JEE Main, JEE Adv, NEET |
| `Std-12_Maths-Part1_EnglishMedium.pdf` | 12 | Mathematics | Part 1 | 236 | 2.61 | `4e99f9a4bae4b6c31e67bb939bebb49a...` | JEE Main, JEE Adv |
| `Std-12_Maths-Part2_EnglishMedium.pdf` | 12 | Mathematics | Part 2 | 248 | 3.08 | `401e5477ec7e0693a3bf2a8d386bc579...` | JEE Main, JEE Adv |
| `Std-12_Biology_EnglishMedium.pdf` | 12 | Biology | Complete | 240 | 176.77 | `9d292433d320dcda38096cf9bcf51b14...` | NEET UG |

**Total Textbook Pages:** 2,803 pages verified.  
**Chapter & Topic Ingestion Rule:** In accordance with the separate validation stage mandate, textbook chapter and topic nodes will be extracted and verified directly during Pipeline B ingestion, rather than fabricated or assumed.

---

## 7. Scope Boundaries & Compliance Audit

- [x] **No unverified chapter/topic structures seeded.**
- [x] **No examination papers or questions ingested yet.**
- [x] **No legacy synthetic records deleted.**
- [x] **No test isolation changes applied in this phase.**
- [x] **No git commits or pushes performed.**

---

## 8. Next Step: Phase C (Test-Isolation Hardening)

Upon user approval to proceed to Phase C:
1. Update `backend/tests/conftest.py` to inject `DATABASE_URL = "sqlite:///:memory:"` early and redirect `SessionLocal`.
2. Implement `backend/tests/test_database_isolation.py` regression tests.
3. Verify that running `pytest` produces zero alterations or record injections into `edunavika.db`.
