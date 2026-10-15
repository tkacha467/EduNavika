# EduNavika — Milestone 4 Phase E.4: Exam-Specific Topic Applicability Design and Validation Report

**Document ID:** `docs/MILESTONE_4_PHASE_E4_EXAM_TOPIC_DESIGN.md`  
**Execution Date:** 2026-10-15  
**Baseline Persistent Database:** `edunavika.db`  
**Baseline SHA-256:** `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` (Verified Unchanged)  
**Status:** **GO** (Ready for Persistent Seeding upon Explicit Operator Approval)

---

## 1. Executive Summary & Recommendation

In Milestone 4 Phase E.4, we resolved the architectural gap between the canonical Class 11–12 Science textbook curriculum hierarchy (106 chapters, 626 topics) and competitive examination syllabi (JEE Main, JEE Advanced, NEET UG). 

While Phase B introduced subject-level linkages (`exam_subjects`), subject-level filtering was coarse:
1. It could not differentiate topics pruned by NTA from JEE Main but explicitly retained by IITs for JEE Advanced (e.g., *Carnot Engine and Efficiency*, *Doppler Effect in Sound*, *Reynolds Number*, *Tangents and Normals*, *Planes in 3D*).
2. It could not isolate foundational textbook-only topics (e.g., *Newton's Law of Cooling*, *Approximations*) from competitive exam practice without deleting them from general school curricula.
3. It could not prevent questions in unverified or quarantined topics (*Morphology of Flowering Plants*, *Cockroach Anatomy*) from leaking into scored exam practice.

We have designed, implemented, and fully validated on isolated disposable sandbox databases:
- **Smallest Correct Schema:** The `exam_topics` association table with explicit provenance and unique constraints.
- **Manifest Synchronization Service:** An idempotent, dry-run capable sync engine reconciling `data/manifests/canonical_curriculum_manifest.json` against the database.
- **Universal Applicability Gate:** Updated query paths in API endpoints (`/api/v1/chapters/{id}/topics?exam_code=...`) and recommendation/practice engines (`is_eligible_curriculum_topic`).
- **Comprehensive Test Suite:** 11 rigorous automated tests in `backend/tests/test_exam_topic_applicability.py` (100% passing).
- **Persistent Database Protection:** Verified that `edunavika.db` was untouched and preserved at baseline SHA-256 `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174`.

### Decision: **GO**
The migration (`a1b2c3d4e5f6`), model definitions, synchronization engine, and API integration are fully validated and ready to apply to the persistent database.

---

## 2. Schema Design: The Smallest Correct Model

### 2.1 Model Evaluation

We evaluated three competing architectural designs:
1. **Model A: Topic Table Attribute Array (e.g., `applicable_exams` JSON column on `topics`):**
   - *Pros:* No new table required.
   - *Cons:* Violates relational normalization; prevents database-level foreign-key cascade integrity; makes indexed joins against `examinations` slow; cannot enforce foreign keys against `examinations.code`.
2. **Model B: Exclusion Table (`exam_topic_exclusions`):**
   - *Pros:* Stores only the exceptions (e.g. Carnot engine excluded from JEE Main).
   - *Cons:* Dangerously assumes "everything is included by default unless excluded". Any newly seeded topic or mislabeled exam code defaults to inclusion, violating our core safety gate.
3. **Model C: Positive Associative Association Table (`exam_topics`) [Selected]:**
   - *Pros:* Represents verified applicability only ("closed-world assumption"). If an exam-topic link does not exist, the topic is not eligible for that exam. Guarantees textbook-only topics and unreviewed topics receive zero links automatically.
   - *Cons:* Requires a new table and index.

### 2.2 Selected Schema Specification

The `exam_topics` table is defined in `backend/app/models/competitive_models.py` and Alembic migration `backend/alembic/versions/20261015_m4_exam_topics_association.py`:

```sql
CREATE TABLE exam_topics (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    exam_code VARCHAR(32) NOT NULL,
    topic_id VARCHAR(36) NOT NULL,
    curriculum_role VARCHAR(32) NOT NULL DEFAULT 'CORE_MANDATORY',
    inclusion_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    verification_status VARCHAR(32) NOT NULL DEFAULT 'VERIFIED_PRIMARY_SOURCE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_topics_exam FOREIGN KEY (exam_code) REFERENCES examinations(code) ON DELETE RESTRICT,
    CONSTRAINT fk_exam_topics_topic FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE,
    CONSTRAINT uq_exam_topics_link UNIQUE (exam_code, topic_id)
);

CREATE INDEX ix_exam_topics_exam_code ON exam_topics(exam_code);
CREATE INDEX ix_exam_topics_topic_id ON exam_topics(topic_id);
CREATE INDEX idx_exam_topics_lookup ON exam_topics(exam_code, topic_id);
```

### 2.3 Constraint and Integrity Invariants
- **Uniqueness:** `(exam_code, topic_id)` is guaranteed unique.
- **Referential Integrity:** Deleting an exam is blocked (`RESTRICT`) if associations exist; deleting a topic cascades safely (`CASCADE`).
- **Closed-World Gate:** Unverified topics (`NEEDS_HUMAN_REVIEW`) and textbook-only topics (`VERIFIED_TEXTBOOK_ONLY`) are never inserted into `exam_topics`.

---

## 3. Manifest-to-Database Synchronization

### 3.1 Idempotent Synchronization Pipeline
The synchronization service (`backend/app/services/exam_topic_sync_service.py`) synchronizes `data/manifests/canonical_curriculum_manifest.json` into `exam_topics`:

1. **Pre-flight Validation:** Reconciles all exam codes against active `examinations` rows (`JEE_MAIN`, `JEE_ADVANCED`, `NEET_UG`).
2. **Review Quarantine Gate:** Any topic with status `NEEDS_HUMAN_REVIEW`, `UNVERIFIED`, `UNRESOLVED`, or `AMBIGUOUS` is quarantined and receives 0 exam links.
3. **Textbook-Only Exclusion Gate:** Any topic with status `VERIFIED_TEXTBOOK_ONLY` or empty `applicable_exams` is categorized as textbook-only and receives 0 exam links.
4. **Deterministic Primary Keys:** UUIDv5 generated via namespace `edunavika.exam_topic.{exam_code}.{topic.canonical_id}` ensures 100% deterministic, repeatable inserts across reruns.
5. **Conflict Prevention:** Detects mismatch between existing links and manifest specifications without silent corruption.
6. **Dry-Run & Transaction Safety:** Supports `dry_run=True` (full audit simulation with automatic transaction rollback).

### 3.2 Audit Reconciliation Metrics

When synchronized against the canonical manifest:
- **Total Manifest Topics Processed:** 626
- **Total Verified Exam-Topic Associations Created:** **1,377**
  - `JEE_MAIN`: **436** topics
  - `JEE_ADVANCED`: **444** topics (retains 8 classical topics pruned from JEE Main)
  - `NEET_UG`: **497** topics
- **Quarantined Topics (0 Exam Links):** **2** topics
  - `STD11-BIO-CH05-T07`: *Description of Flowering Plant and Families (Fabaceae, Solanaceae, Liliaceae)*
  - `STD11-BIO-CH07-T03`: *Anatomy and Functions of Different Systems of an Insect (Cockroach / Frog)*
- **Textbook-Only Content (0 Exam Links):** **2** topics
  - `STD11-PHYS-CH10-T07`: *Newton's Law of Cooling*
  - `STD12-MATH-CH06-T04`: *Approximations*
- **Re-run Idempotency:** 0 inserted, 1,377 unchanged, 0 errors.

---

## 4. Affected Application Paths & Query Architecture

Every exam-specific topic list in EduNavika now utilizes the unified applicability rules:

### 4.1 Exam Selection and Topic/Chapter Browsing
- **Endpoint:** `GET /api/v1/chapters/{chapter_id}/topics?exam_code={code}`
- **Behavior:**
  - When `exam_code` is provided (e.g. `JEE_MAIN`): Joins `ExamTopic` on `topics.id == exam_topics.topic_id` and filters by `exam_topics.exam_code == exam_code` and `inclusion_status == 'ACTIVE'`.
  - When `exam_code` is omitted: Preserves full textbook curriculum browsing, returning all active topics including textbook-only concepts (e.g. *Newton's Law of Cooling*).

### 4.2 Pedagogical Engine Topic Eligibility Gate
- **Service Method:** `RecommendationEngineService.is_eligible_curriculum_topic(db, student, topic, exam_code=None)`
- **Behavior:**
  - Integrated across:
    1. `revision_planner.py`: Generates revision tasks only for topics in the student's selected exam syllabus.
    2. `adaptive_practice.py`: Selects practice questions only from exam-eligible topics.
    3. `recommendation_engine.py`: Onboarding diagnostics and next-step recommendations never recommend pruned or textbook-only topics to exam candidates.
    4. `progress_service.py`: Computes syllabus completion percentage against the exact exam topic count (e.g. out of 436 for JEE Main, not 626).
    5. `curriculum_retrieval.py`: Restricts AI RAG context retrieval to applicable topics.

### 4.3 Subject Boundary Enforcement
- **NEET UG:** Contains 497 topics across Physics, Chemistry, and Biology (0 Mathematics topics).
- **JEE Main & JEE Advanced:** Contain 436 and 444 topics respectively across Physics, Chemistry, and Mathematics (0 Biology topics).

---

## 5. Verification and Test Evidence

### 5.1 Automated Pytest Suite (`backend/tests/test_exam_topic_applicability.py`)

A comprehensive test suite of 11 integration tests was executed against an isolated SQLite test database:

| Test ID | Test Description | Result |
| :--- | :--- | :--- |
| `test_01` | Dry-run execution generates audit report with 0 database writes | **PASSED** |
| `test_02` | Live synchronization creates exactly 1,377 associations (436 JEE Main, 444 JEE Adv, 497 NEET) | **PASSED** |
| `test_03` | Re-running synchronization is 100% idempotent (0 inserts, 1,377 unchanged) | **PASSED** |
| `test_04` | JEE Main excludes JEE-Advanced-only topics (Carnot Engine, Doppler Effect, Tangents & Normals, Planes in 3D) | **PASSED** |
| `test_05` | Subject boundaries enforced: NEET UG has 0 Math; JEE Main & Adv have 0 Biology | **PASSED** |
| `test_06` | Textbook-only topics (Newton's cooling, Approximations) receive 0 exam links but exist in DB | **PASSED** |
| `test_07` | Quarantined human-review topics receive 0 exam links | **PASSED** |
| `test_08` | FastAPI endpoint `/api/v1/chapters/{id}/topics` correctly filters by `exam_code` | **PASSED** |
| `test_09` | SQLite `PRAGMA integrity_check` and `PRAGMA foreign_key_check` return 0 errors | **PASSED** |
| `test_10` | Legacy Standard 10 data (505 topics) remains 100% intact and receives 0 competitive links | **PASSED** |
| `test_11` | Recommendation and practice engine eligibility filter respects `exam_code` applicability | **PASSED** |

### 5.2 Sandbox Clone Validation (`scripts/test_phase_e4_sandbox.py`)

To validate migration `a1b2c3d4e5f6` against a real-world database snapshot, we cloned `edunavika.db` into a sandbox file `sandbox_test_phase_e4.db` and executed:
1. Alembic upgrade from `f1e2d3c4b5a6` to `a1b2c3d4e5f6`.
2. Schema inspection verifying `exam_topics` columns, foreign keys, and indexes.
3. Seeding of 106 chapters and 624 verified topics.
4. Dry-run synchronization (verified 0 writes).
5. Live synchronization (verified 1,377 links created).
6. Idempotency re-run (verified 0 inserts, 1,377 unchanged).
7. PRAGMA integrity check and foreign-key check (0 errors).
8. Legacy Standard 10 topic verification (preserved exactly 505 rows).
9. Cleanup of sandbox database.

---

## 6. Report on Affected API Endpoints and Frontend Consumers

| Endpoint | Method | Parameters Added / Modified | Impact on Frontend Consumers |
| :--- | :--- | :--- | :--- |
| `/api/v1/chapters/{chapter_id}/topics` | `GET` | Optional query param: `exam_code: Optional[str]` | Syllabus screen, Topic Selector, Diagnostic practice drawer. Passing `exam_code=JEE_MAIN` now renders only JEE Main topics. Leaving it blank renders full NCERT textbook topics. |
| `/api/v1/recommendations/` | `GET` | Filtered via student target exam | Dashboard recommendations will only suggest topics applicable to student's chosen exam. |
| `/api/v1/practice/adaptive` | `POST` | Filtered via topic eligibility | Prevents generating practice sets for non-exam topics when student is in competitive mode. |
| `/api/v1/revision/plan` | `GET` | Filtered via topic eligibility | Revision calendar will only schedule revisions for exam-applicable topics. |
| `/api/v1/progress/overview` | `GET` | Filtered via topic eligibility | Progress bars and mastery metrics calculate completion percentage against the exact target exam topic count. |

---

## 7. Migration Readiness & Persistent Database Protection

### 7.1 Persistent Database Verification
Throughout Phase E.4, the persistent database `D:\EduNavika\edunavika.db` remained strictly untouched and protected:
- **Baseline SHA-256:** `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174`
- **Post-Verification SHA-256:** `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174`
- **Status:** **MATCH (Zero modifications)**

### 7.2 Rollout Plan (Upon Explicit Approval)
When operator approval is granted:
1. Create a fresh verified native SQLite backup in `backups/milestone_4_pre_phase_e_migration/`.
2. Apply Alembic migration `a1b2c3d4e5f6` to `edunavika.db`.
3. Run `curriculum_seeder.py` to seed 106 chapters and 624 verified topics.
4. Run `exam_topic_sync_service.py` to populate 1,377 verified associations.
5. Record the new persistent database SHA-256 hash.

---

## 8. Final Status and Stop Condition

**Final Recommendation:** **GO**  
The Phase E.4 design and validation are complete. All safety constraints have been respected, sandbox validation is 100% green, and persistent database baseline is preserved. Execution is paused awaiting explicit operator authorization.
