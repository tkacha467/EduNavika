# EduNavika — Milestone 4 Phase E.4: Validation Report

**Document ID:** `docs/MILESTONE_4_PHASE_E4_VALIDATION_REPORT.md`
**Execution Date:** 2026-10-19
**Baseline Persistent Database:** `edunavika.db`
**Baseline SHA-256:** `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` (Verified Unchanged)
**Overall Validation Status:** **PASSED (100% Green)**
**Recommendation:** **GO** (Ready for Persistent Migration and Seeding upon Explicit Operator Approval)

---

## 1. Executive Summary

Milestone 4 Phase E.4 validates that competitive examination users (JEE Main, JEE Advanced, and NEET UG) interact exclusively with topics applicable to their selected examination across all key application touchpoints, while preserving authentic textbook-only content for general study contexts.

All design elements, data synchronization routines, and runtime query paths have been implemented and validated against isolated disposable test databases and sandbox clones of `edunavika.db`.

---

## 2. Safety Invariants & Persistent Database Baseline

Throughout Phase E.4, strict read-only safety constraints were enforced on the persistent development database:

| Safety Metric | Value | Status |
| :--- | :--- | :--- |
| **Target Persistent Database** | `D:\EduNavika\edunavika.db` | Verified |
| **Reported Baseline Hash** | `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` | Confirmed |
| **Pre-Test SHA-256** | `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` | Exact Match |
| **Post-Test SHA-256** | `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` | Exact Match |
| **Migrations Applied to Persistent DB** | 0 | Protected |
| **Records Written to Persistent DB** | 0 | Protected |

The baseline hash has been preserved bit-for-bit.

---

## 3. Automated Test Evidence

### 3.1 Targeted Exam Topic Applicability Test Suite
**Command:** `pytest backend/tests/test_exam_topic_applicability.py -v`
**Result:** **14 passed, 4 warnings in 33.14s**

```text
backend/tests/test_exam_topic_applicability.py::test_01_sync_exam_topics_dry_run PASSED [  7%]
backend/tests/test_exam_topic_applicability.py::test_02_sync_exam_topics_clean_execution PASSED [ 14%]
backend/tests/test_exam_topic_applicability.py::test_03_sync_exam_topics_idempotency PASSED [ 21%]
backend/tests/test_exam_topic_applicability.py::test_04_jee_main_excludes_jee_advanced_only_topics PASSED [ 28%]
backend/tests/test_exam_topic_applicability.py::test_05_subject_level_boundaries_enforced PASSED [ 35%]
backend/tests/test_exam_topic_applicability.py::test_06_textbook_only_topics_have_zero_exam_links PASSED [ 42%]
backend/tests/test_exam_topic_applicability.py::test_07_quarantined_human_review_topics_have_zero_exam_links PASSED [ 50%]
backend/tests/test_exam_topic_applicability.py::test_08_api_endpoint_filters_topics_by_exam_code PASSED [ 57%]
backend/tests/test_exam_topic_applicability.py::test_09_foreign_keys_and_integrity_check PASSED [ 64%]
backend/tests/test_exam_topic_applicability.py::test_10_legacy_data_preservation PASSED [ 71%]
backend/tests/test_exam_topic_applicability.py::test_11_recommendation_and_study_engine_eligibility_filter PASSED [ 78%]
backend/tests/test_exam_topic_applicability.py::test_12_recommendations_endpoint_respects_exam_code PASSED [ 85%]
backend/tests/test_exam_topic_applicability.py::test_13_adaptive_practice_rejects_inapplicable_topics PASSED [ 92%]
backend/tests/test_exam_topic_applicability.py::test_14_progress_and_revision_filter_by_exam_code PASSED [100%]
```

### 3.2 Sandbox Clone Migration & Lifecycle Execution
**Command:** `python scripts/test_phase_e4_sandbox.py`
**Result:** **PASSED (Exit code 0)**

```text
Persistent DB Hash (Pre): 84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174

1. Cloning persistent DB to disposable sandbox: sandbox_test_phase_e4.db
Pre-migration: Standard 10 topics count = 505

2. Executing Alembic migration 'a1b2c3d4e5f6' on sandbox DB...
  [OK] Migration applied successfully to sandbox.
  [OK] Table 'exam_topics' schema and indexes verified.

3. Seeding Canonical Curriculum into sandbox...
  [OK] Seeded 106 chapters and 624 topics (quarantined: 2).

4. Testing Exam-Topic Synchronization (Dry Run)...
  [OK] Dry run verified with 0 table writes.

5. Testing Exam-Topic Synchronization (Live Run)...
  [OK] Synchronized 1377 exam-topic associations.

6. Testing Synchronization Idempotency...
  [OK] Idempotency confirmed: 0 new inserts, 1,377 unchanged.

7. Validating Exam Scope & Domain Boundaries...
  - JEE_MAIN associations:     436
  - JEE_ADVANCED associations: 444
  - NEET_UG associations:      497
  [OK] NEET UG has 0 Mathematics topics.
  [OK] JEE Main & JEE Advanced have 0 Biology topics.
  [OK] PRAGMA integrity_check and foreign_key_check passed with 0 errors.
  [OK] Legacy Std 10 topics preserved intact (505 rows).
  [OK] Sandbox database deleted.

Persistent DB Hash (Post): 84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174
  [PASSED] Persistent DB hash is UNCHANGED and strictly preserved.
```

### 3.3 Full Suite Regression Validation
**Command:** `pytest backend/tests/test_curriculum_seeding.py backend/tests/test_pilot_ingestion.py backend/tests/test_curriculum_coverage_and_runtime.py backend/tests/test_database_isolation.py -v`
**Result:** **33 passed in 6.68s**

```text
======================= 33 passed, 4 warnings in 6.68s ========================
```

---

## 4. Invariant Verification Summary

| Invariant Requirement | Tested Behavior | Verification Result |
| :--- | :--- | :--- |
| **JEE Main Exclusions** | Carnot Engine, Doppler Effect, Tangents & Normals, Planes in 3D excluded from JEE Main queries and practice | **VERIFIED** |
| **JEE Advanced Retention** | All 8 classical topics pruned by NTA remain active for JEE Advanced (444 total topics) | **VERIFIED** |
| **NEET Subject Boundaries** | NEET UG has exactly 0 Mathematics topic links (497 Biology, Chemistry, Physics topics) | **VERIFIED** |
| **JEE Subject Boundaries** | JEE Main & Advanced have exactly 0 Biology topic links | **VERIFIED** |
| **Human-Review Quarantine** | 2 unreviewed topics received 0 exam links and are blocked from scored practice | **VERIFIED** |
| **Textbook-Only Isolation** | Newton's Law of Cooling & Approximations receive 0 exam links but remain accessible in textbook browsing | **VERIFIED** |
| **Synchronization Idempotency**| Second sync run yields 0 inserts, 1,377 unchanged, 0 duplicates | **VERIFIED** |
| **Transaction Rollback** | Dry-run rolls back cleanly leaving 0 table rows | **VERIFIED** |
| **Legacy Data Preservation** | 505 Standard 10 topics remain completely intact with 0 competitive associations | **VERIFIED** |
| **API Exam Filtering** | Endpoints filter correctly when `exam_code` is passed, and revert to textbook mode when omitted | **VERIFIED** |

---

## 5. Affected Endpoints and Query Propagation

The following endpoints have been verified to respect `exam_code`:
1. `GET /api/v1/chapters/{id}/topics?exam_code=...`
2. `GET /api/v1/adaptive/recommendations/{student_id}?exam_code=...`
3. `GET /api/v1/adaptive/next-practice/{student_id}?exam_code=...`
4. `GET /api/v1/adaptive/practice/{student_id}?topic_id={id}&exam_code=...`
5. `GET /api/v1/adaptive/progress/{student_id}?exam_code=...`
6. `GET /api/v1/adaptive/revision-plan/{student_id}?exam_code=...`
7. `GET /api/v1/students/{student_id}/revision-plan?exam_code=...`
8. `GET /api/v1/revision/plans?exam_code=...`

---

## 6. Final Status and Recommendation

### Recommendation: **GO**

All sandbox testing, schema migration proposals, synchronization services, query path propagations, and regression tests have executed with 100% pass rates. The persistent database has not been modified.

### Exact Next Action Requiring Explicit Operator Approval:
**Apply Alembic migration `a1b2c3d4e5f6` to `D:\EduNavika\edunavika.db`, execute `curriculum_seeder.py` (106 chapters, 624 verified topics), and execute `exam_topic_sync_service.py` (1,377 exam associations) against the persistent database after taking a fresh verified backup.**
