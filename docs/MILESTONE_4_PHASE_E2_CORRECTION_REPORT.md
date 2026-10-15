# EduNavika — Milestone 4: Phase E.2 Manifest Correction Report

**Document Version:** 1.0.0  
**Phase:** Milestone 4 — Phase E.2 (Evidence-Based Manifest Correction)  
**Date:** October 15, 2026  
**Scope:** Classes 11 & 12 Science (Physics, Chemistry, Mathematics, Biology)  
**Target Examinations:** JEE Main (NTA), JEE Advanced (IIT JAB), NEET UG (NMC)  
**Persistent Database:** `D:\EduNavika\edunavika.db` (Schema Revision: `f1e2d3c4b5a6`)  
**Persistent Database State:** **100% FROZEN & UNTOUCHED** (Baseline SHA-256 Verified)  
**Corrected Candidate Manifest:** `data/manifests/canonical_curriculum_manifest.json`  
**Old-to-New ID Migration Map:** `data/manifests/id_migration_map.json`  
**Final Seeding Recommendation:** **GO (Candidate Ready for Persistent Seeding Sign-Off)**

---

## 1. Executive Summary

Milestone 4 Phase E.2 addresses and resolves all findings identified in the Phase E.1 evidence audit. The unverified blanket `VERIFIED` status and formulaic artifacts have been dismantled, replaced by an authentic multi-tier evidence taxonomy, corrected Biology canonical identifiers, subtopic-level exam applicability mappings, and a conflict-hardened curriculum seeder.

### 1.1 Persistent Database Safety Verification
In compliance with Step 1, the persistent development database was audited before and after all Phase E.2 work:
- **Database Path:** `D:\EduNavika\edunavika.db`
- **Baseline SHA-256:** `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174`
- **Current SHA-256:** `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174`
- **Size:** `3,981,312` bytes
- **Integrity Check:** `ok` | **Foreign-Key Violations:** 0
- **Drift Detected:** **ZERO BYTES (100% Unmodified)**

### 1.2 Summary of Corrections Made
1. **Preserved Pre-Correction Backups:**
   - Saved `data/manifests/canonical_curriculum_manifest.pre_e2_backup.json`
   - Saved `data/manifests/canonical_curriculum_audit.pre_e2_backup.json`
2. **Corrected Biology Canonical IDs:** Fixed the `code[:4]` truncation bug that produced `STD11-BIO1-` and `STD12-BIO1-`. Migrated all 211 Biology entities (32 chapters + 179 topics) to the standard prefix `STD11-BIO-` and `STD12-BIO-`, cataloged in `data/manifests/id_migration_map.json`.
3. **Dismantled Blanket `VERIFIED` Status:** Re-classified all 626 topics into explicit textbook verification (`textbook_verification_status = "VERIFIED_TEXTBOOK"`) and official exam syllabus verification (`exam_verification_status`).
4. **Resolved Subtopic-Level Exam Applicability:** Pruned topics deleted by NTA (JEE Main) and NMC (NEET UG) while retaining them for IIT JAB (JEE Advanced) where supported by ground truth evidence.
5. **Implemented Conflict-Safe Seeder:** Enhanced `backend/app/services/curriculum_seeder.py` with `conflict_policy="ABORT"` (default), `"WARN"`, and `"OVERWRITE"`, preventing silent overwriting of existing modified records in the database.
6. **Automated Quarantining of Unreviewed Content:** Topics marked `NEEDS_HUMAN_REVIEW` or `UNVERIFIED` are automatically quarantined and excluded from database insertion by default.
7. **Validated via Test Suites:** 10/10 automated tests passed in `backend/tests/test_curriculum_seeding.py`, and 100% passage achieved on a full persistent database clone sandbox (`scripts/test_canonical_curriculum_sandbox.py`).

---

## 2. Canonical Identifier Corrections (Biology Prefix Fix)

### 2.1 Investigation and Root Cause
In `scratch/enrich_manifest.py`, canonical IDs were formatted using:
```python
prefix = code[:4]  # Slicing the subject code
```
While `PHYS11`[:4] yielded `PHYS`, `CHEM11`[:4] yielded `CHEM`, and `MATH11`[:4] yielded `MATH`, for the 5-character Biology codes (`BIO11` and `BIO12`), `code[:4]` produced `BIO1`. This resulted in all Biology entities carrying the irregular prefix `STD11-BIO1-` and `STD12-BIO1-`.

### 2.2 Repository Reference Inspection
Before applying the correction, the entire codebase, test fixtures, and migration files were searched for references to `STD11-BIO1-` and `STD12-BIO1-`. No hardcoded references existed in application logic, ORM models, or migrations.

### 2.3 Explicit Prefix Mapping Implemented
Replaced the slicing logic with an explicit, stable mapping table:
```python
SUBJECT_PREFIX_MAP = {
    "PHYS11": "PHYS",
    "PHYS12": "PHYS",
    "CHEM11": "CHEM",
    "CHEM12": "CHEM",
    "MATH11": "MATH",
    "MATH12": "MATH",
    "BIO11": "BIO",
    "BIO12": "BIO",
}
```

### 2.4 Old-to-New ID Migration Map Summary
A total of **211 Biology entities** were renamed and cataloged in [`data/manifests/id_migration_map.json`](file:///d:/EduSens/data/manifests/id_migration_map.json):
- **Class 11 Biology Chapters (19):** `STD11-BIO1-CH01..19` -> `STD11-BIO-CH01..19`
- **Class 11 Biology Topics (103):** `STD11-BIO1-CH01-T01..CH19-T07` -> `STD11-BIO-CH01-T01..CH19-T07`
- **Class 12 Biology Chapters (13):** `STD12-BIO1-CH01..13` -> `STD12-BIO-CH01..13`
- **Class 12 Biology Topics (76):** `STD12-BIO1-CH01-T01..CH13-T04` -> `STD12-BIO-CH01-T01..CH13-T04`

---

## 3. Verification Taxonomy & Exam Applicability Corrections

### 3.1 Topic Verification Status Counts (Before vs. After)

| Verification Status | Pre-Correction Count | Post-Correction Count | Percentage | Operational Meaning |
| :--- | :---: | :---: | :---: | :--- |
| `VERIFIED` (Generic Blanket) | 626 | **0** | 0.0% | **Dismantled and eliminated.** |
| `VERIFIED_PRIMARY_SOURCE` | 0 | **613** | 97.9% | Verified in NCERT textbook AND confirmed active across all assigned examination syllabi. |
| `PARTIAL_MAPPING` | 0 | **9** | 1.4% | Verified in NCERT textbook and active in select entrance exams (e.g. JEE Advanced), but pruned by NTA/NMC. |
| `VERIFIED_TEXTBOOK_ONLY` | 0 | **2** | 0.3% | Verified in NCERT textbook for general secondary instruction, but deleted from all competitive entrance syllabi. |
| `NEEDS_HUMAN_REVIEW` | 0 | **2** | 0.3% | Substantive discrepancy between textbook and syllabus (e.g. extra angiosperm families added by NMC). |
| **TOTAL** | **626** | **626** | **100.0%** | **Rigorous evidence-backed distribution.** |

### 3.2 Detailed Audit Corrections on the 13 High-Risk Topics

| Canonical ID | Topic Title | Subject | Corrected Exam Applicability | Corrected Status | Official Evidence & Provenance Citation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `STD11-PHYS-CH09-T06` | Reynolds Number | `PHYS11` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Pruned from NTA JEE Main and NMC NEET UG 2024 rationalized syllabi; retained in IIT JAB JEE Advanced 2024 syllabus. |
| `STD11-PHYS-CH10-T07` | Newton's Law of Cooling | `PHYS11` | `[]` | `VERIFIED_TEXTBOOK_ONLY` | Deleted from JEE Main, JEE Advanced, and NEET UG 2024 syllabi; exists in NCERT textbook only. |
| `STD11-PHYS-CH11-T08` | Carnot Engine & Efficiency | `PHYS11` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Explicitly deleted from NTA JEE Main and NMC NEET UG 2024; retained in IIT JAB JEE Advanced 2024 syllabus. |
| `STD11-PHYS-CH14-T07` | Doppler Effect (Acoustic) | `PHYS11` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Deleted from JEE Main and NEET UG 2024; retained in IIT JAB JEE Advanced 2024 syllabus. |
| `STD11-CHEM-CH02-T02` | Atomic Models (Thomson, Rutherford) | `CHEM11` | `["NEET_UG"]` | `PARTIAL_MAPPING` | Deleted from JEE Main 2024 syllabus; retained in NMC NEET UG 2024 syllabus and NCERT textbook. |
| `STD11-MATH-CH08-T06` | Sum of Special Series ($\sum n, \sum n^2, \sum n^3$) | `MATH11` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Deleted from NTA JEE Main 2024 syllabus; retained in IIT JAB JEE Advanced 2024 syllabus. |
| `STD12-MATH-CH06-T03` | Tangents and Normals | `MATH12` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Deleted from NTA JEE Main 2024 syllabus; retained in IIT JAB JEE Advanced 2024 syllabus. |
| `STD12-MATH-CH06-T04` | Approximations | `MATH12` | `[]` | `VERIFIED_TEXTBOOK_ONLY` | Deleted from JEE Main and JEE Advanced 2024 syllabi; exists in NCERT textbook only. |
| `STD12-MATH-CH10-T06` | Scalar Triple Product | `MATH12` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Deleted from NTA JEE Main 2024 syllabus; retained in IIT JAB JEE Advanced 2024 syllabus. |
| `STD12-MATH-CH11-T04` | Plane in Space & Angle between Planes | `MATH12` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Planes in 3D deleted from NTA JEE Main 2024 syllabus (limited to lines only); retained in IIT JAB JEE Advanced 2024. |
| `STD12-MATH-CH11-T05` | Distance of a Point from a Plane | `MATH12` | `["JEE_ADVANCED"]` | `PARTIAL_MAPPING` | Planes in 3D deleted from NTA JEE Main 2024 syllabus (limited to lines only); retained in IIT JAB JEE Advanced 2024. |
| `STD11-BIO-CH05-T07` | Flowering Plant Families | `BIO11` | `["NEET_UG"]` | `NEEDS_HUMAN_REVIEW` | Discrepancy: NMC NEET UG syllabus added 4 families (*Malvaceae, Brassicaceae, Asteraceae, Poaceae*) not present in rationalized NCERT text. |
| `STD11-BIO-CH07-T03` | Cockroach / Frog Anatomy | `BIO11` | `["NEET_UG"]` | `NEEDS_HUMAN_REVIEW` | Discrepancy: NMC NEET UG syllabus retained Frog and Cockroach; rationalized NCERT textbook removed Cockroach, retaining only Frog. |

### 3.3 Curriculum Currency Uncertainty Statement
The verified rationalized baseline represents the 2024 national reform enacted by NCERT, NTA, and NMC. Because specific annual session information bulletins for 2026 examination sessions require active online retrieval at the time of each testing cycle, the source register documents currency status as `UNVERIFIED_2026_SESSION_BULLETIN_PENDING` without guessing or assuming future changes.

---

## 4. Seeder Conflict Safety & Architecture

### 4.1 Safe Conflict Policy Implementation
In `backend/app/services/curriculum_seeder.py`, the `seed_canonical_curriculum` function has been enhanced with:
```python
def seed_canonical_curriculum(
    db: Session,
    manifest_path: Optional[Path] = None,
    dry_run: bool = False,
    conflict_policy: str = "ABORT",  # Options: "ABORT", "WARN", "OVERWRITE"
    include_unreviewed: bool = False, # If False, unreviewed items are quarantined
) -> Dict[str, Any]:
```

#### Policy Behavior Matrix:
- **`ABORT` (Default):** If an existing database record matches `(subject_id, chapter_number)` or `(chapter_id, topic_order)` but has a conflicting `title` or `source_reference`, the seeder raises `CurriculumConflictError`, logs the conflict details, rolls back the database transaction, and aborts without persisting any writes.
- **`WARN`:** Logs a conflict warning, leaves the existing database record completely unmodified, and proceeds.
- **`OVERWRITE`:** Updates the existing database record only when explicitly requested by an authorized caller.

### 4.2 Automated Unreviewed Content Quarantining
When `include_unreviewed=False` (default production mode):
- Topics with status `NEEDS_HUMAN_REVIEW`, `UNVERIFIED`, or `UNRESOLVED` are automatically intercepted and routed to `report.quarantined_items`.
- They are **excluded from database insertion**, ensuring that ambiguous or incomplete topics (such as the out-of-textbook NEET plant families) cannot enter the persistent database until human curriculum experts review and resolve them.
- In production mode, **106 chapters and 624 verified topics are seeded**, while exactly **2 unreviewed topics are quarantined**.

### 4.3 Database Relational Schema Limitation & Guidance
**Schema Finding:** The current schema (`f1e2d3c4b5a6`) links examinations to *subjects* (`exam_subjects`), but does **not** contain an `exam_topics` association table or JSON metadata on `topics`.
- Consequently, subtopic-level exam exclusions (e.g. Carnot engine excluded from JEE Main while retained in JEE Advanced) **cannot be represented relationally in the current `topics` table**.
- **Architectural Guidance for Milestone 4 Question Pipeline:** Per-topic exam eligibility must be validated at the question-metadata level (`questions.exam_code`, `questions.topic_id`, and `questions.source_reference`).
- **Proposed Future Schema Migration (Post-Milestone 4):**
  ```sql
  CREATE TABLE exam_topics (
      id VARCHAR(36) PRIMARY KEY,
      exam_code VARCHAR(32) NOT NULL REFERENCES examinations(code),
      topic_id VARCHAR(36) NOT NULL REFERENCES topics(id),
      inclusion_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
      created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      CONSTRAINT uq_exam_topics_link UNIQUE (exam_code, topic_id)
  );
  ```
  *(No migration has been executed in this phase, preserving current schema stability.)*

---

## 5. Verification Test Suite Results

### 5.1 Automated Test Suite (`backend/tests/test_curriculum_seeding.py`)
Executed via `pytest` with 10/10 passing tests:

| Test ID | Test Name | Invariant Tested | Result |
| :---: | :--- | :--- | :---: |
| **Test 1** | `test_01_dry_run_performs_zero_writes` | `dry_run=True` rolls back; 0 database writes occur | **PASSED** |
| **Test 2** | `test_02_clean_disposable_database_receives_curriculum_hierarchy` | Seeds 106 chapters & 624 verified topics; quarantines 2 unreviewed | **PASSED** |
| **Test 3** | `test_03_rerunning_seeder_creates_no_duplicates` | Second execution creates 0 duplicates (100% idempotent) | **PASSED** |
| **Test 4** | `test_04_existing_standard_10_records_remain_unchanged` | Legacy Standard 10 subjects, chapters, and topics untouched | **PASSED** |
| **Test 5** | `test_05_exam_subject_associations_remain_correct` | 18 associations verified; Math excluded from NEET, Bio from JEE | **PASSED** |
| **Test 6** | `test_06_foreign_keys_and_uniqueness_constraints_respected` | `PRAGMA foreign_key_check` = 0; `PRAGMA integrity_check` = ok | **PASSED** |
| **Test 7** | `test_07_conflict_policy_prevents_silent_overwrites` | `ABORT` rolls back on conflict; `WARN` preserves DB; `OVERWRITE` updates | **PASSED** |
| **Test 8** | `test_08_biology_canonical_ids_are_correctly_formatted` | All Biology IDs use `STD11-BIO-` and `STD12-BIO-` (0 `BIO1` IDs) | **PASSED** |
| **Test 9** | `test_09_exam_applicability_subtopic_exclusions` | Carnot/Doppler = `[ADV]`, Cooling = `[]`, Tangents = `[ADV]` verified | **PASSED** |
| **Test 10** | `test_10_deterministic_uuid_reproducibility` | UUIDv5 generation is 100% deterministic and reproducible | **PASSED** |

### 5.2 Real-Data Sandbox Clone Test (`scripts/test_canonical_curriculum_sandbox.py`)
Executed against a full sandbox clone of the persistent database (`sandbox_test_phase_e.db` containing all 244 users, 247 subjects, and 288 legacy chapters):
- **Pre-seed:** Standard 10 Chapters = 288; Standard 11/12 Chapters = 0.
- **Dry Run:** Planned 106 chapters and 624 verified topics (2 quarantined); 0 database writes committed.
- **Live Seed:** Exactly 106 chapters and 624 verified topics inserted. Integrity check: `ok`. Foreign-key violations: `0`.
- **Idempotency Re-run:** 0 chapters created, 0 topics created; 106 chapters existing, 624 topics existing.
- **Legacy Verification:** Standard 10 chapter count remained exactly 288.

---

## 6. Deliverables Inventory

The following files have been created, updated, and validated:
1. **[`data/manifests/canonical_curriculum_manifest.json`](file:///d:/EduSens/data/manifests/canonical_curriculum_manifest.json):** Corrected candidate manifest with multi-tier verification statuses, subtopic-level exam applicability, and fixed Biology canonical identifiers.
2. **[`data/manifests/id_migration_map.json`](file:///d:/EduSens/data/manifests/id_migration_map.json):** Full migration dictionary tracking all 211 renamed Biology entities.
3. **[`data/manifests/canonical_curriculum_audit.json`](file:///d:/EduSens/data/manifests/canonical_curriculum_audit.json):** Machine-readable audit artifact synchronized with post-correction metrics.
4. **[`backend/app/services/curriculum_seeder.py`](file:///d:/EduSens/backend/app/services/curriculum_seeder.py):** Enhanced seeder service with strict conflict handling (`ABORT`/`WARN`/`OVERWRITE`) and automated quarantine of unreviewed topics.
5. **[`backend/tests/test_curriculum_seeding.py`](file:///d:/EduSens/backend/tests/test_curriculum_seeding.py):** Comprehensive 10-point automated test suite.
6. **[`docs/MILESTONE_4_PHASE_E2_CORRECTION_REPORT.md`](file:///d:/EduSens/docs/MILESTONE_4_PHASE_E2_CORRECTION_REPORT.md):** This report.

---

## 7. Seeding Gate Recommendation: GO

With all audit findings resolved, Biology IDs corrected, subtopic exclusions verified, conflict safety enforced, and disposable tests passing with 100% success, the candidate manifest is mathematically consistent and safe for persistent database application.

**Recommendation:** **GO (Candidate Ready for Persistent Seeding Sign-Off)**

### Persistent Seeding Plan (Pending User Approval):
- Target Database: `D:\EduNavika\edunavika.db`
- Expected Chapters to Seed: **106**
- Expected Topics to Seed: **624** (with 2 unreviewed topics safely quarantined in audit manifest)
- Expected Conflicts: **0**
- Expected Foreign-Key Violations: **0**

**STOP AND AWAIT USER APPROVAL:** In compliance with the Stop Condition, no persistent writes have occurred. Awaiting explicit user sign-off to execute persistent seeding.
