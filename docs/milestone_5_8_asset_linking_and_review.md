# EduNavika Milestone 5.8 — Asset Linking, Human Review Workflow, and Controlled Ingestion Pilot

**Status:** `PASS WITH REVIEW REQUIRED`  
**Date:** 2026-10-25  
**Target Examination:** NEET UG 2021 (Booklet M4, 200 Questions)  
**Target Artifacts:** 13 Quarantined Diagram Questions, 41 Extracted Vector Diagrams  
**Canonical Database:** `D:\EduSens\edunavika.db` (`SHA-256: 97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`) — **0 Persistent Writes (100% Isolated)**

---

## 1. Executive Summary

Milestone 5.8 implements the safe, auditable bridge between extracted vector diagram assets (Milestone 5.7) and the core competitive examination ingestion pipeline. It delivers:
1. **First-Class Graphical Option Schema Contract:** Added nullable `diagram_asset_url` to `QuestionOption` with reversible Alembic migration (`b2c3d4e5f6a7`), preserving 100% backward compatibility for text-only questions.
2. **Manifest-Driven Asset Linking Service (`DiagramAssetLinkingService`):** Deterministic parser verifying source PDF identity (`e9acdfb...`), asset SHA-256 checksums, path traversal protection, role separation (stem vs. option), and option key mapping.
3. **Automated Validation Gate Compatibility:** Updated `QuestionIngestionService` and `compute_content_hash` to permit empty option text if and only if a valid diagram asset is attached, and hash diagram URLs into deterministic deduplication keys.
4. **Human Content Verification Workflow (`QuestionVerificationService`):** Strict, auditable multi-phase state machine that prevents conflation between visual asset approval, scientific correctness, answer-key reconciliation, legal fair-use clearance, and scoring eligibility.
5. **Controlled Ingestion Pilot:** Real `QuestionIngestionService` ingestion of all 13 NEET 2021 diagram questions in an isolated in-memory SQLite database (`PRAGMA foreign_keys = ON`), confirming 13 valid questions, 41 linked diagrams (5 stem, 36 options), 0 duplicates on rerun, and zero writes to the canonical database.
6. **Verification & Regression Test Suite:** 13 focused Milestone 5.8 tests passed; 72 total regression tests passed across competitive, ingestion, extraction, and curriculum suites.

---

## 2. Target Question & Asset Audit Verification

From the Milestone 5.7 extraction manifest (`data/processed/neet_2021_diagram_manifest.json`) and the Milestone 5.4 audit data (`data/processed/neet_2021_quality_audit.json`), exactly 13 questions have visual dependencies across 41 candidate PNG assets:

| Question # | Subject | Section | Visual Dependency Type | Assets Linked | Asset Role & Option Breakdown |
|:---:|:---:|:---:|:---|:---:|:---|
| **Q4** | Physics | Section A | `HARD_STEM_DIAGRAM_DEPENDENCY` | 1 | Stem: Capacitor bridge network (`neet_2021_q004_stem`) |
| **Q20** | Physics | Section A | `HARD_STEM_DIAGRAM_DEPENDENCY` | 1 | Stem: LCR series AC circuit with meters (`neet_2021_q020_stem`) |
| **Q26** | Physics | Section A | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: B(r) vs. r graphs (`neet_2021_q026_option_a` - `d`) |
| **Q38** | Physics | Section B | `STEM_AND_GRAPHICAL_OPTIONS` | 5 | Stem: Potentiometer wire circuit (`neet_2021_q038_stem`) + Options A-D |
| **Q40** | Physics | Section B | `HARD_STEM_DIAGRAM_DEPENDENCY` | 1 | Stem: Ball projected at angle $\theta$ (`neet_2021_q040_stem`) |
| **Q49** | Physics | Section B | `HARD_STEM_DIAGRAM_DEPENDENCY` | 1 | Stem: Particle projected up inclined plane (`neet_2021_q049_stem`) |
| **Q60** | Chemistry | Section A | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: Organic chemical structures (`neet_2021_q060_option_a` - `d`) |
| **Q62** | Chemistry | Section A | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: Organic reaction products (`neet_2021_q062_option_a` - `d`) |
| **Q63** | Chemistry | Section A | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: Polymer monomer units (`neet_2021_q063_option_a` - `d`) |
| **Q79** | Chemistry | Section B | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: Coordination complex isomers (`neet_2021_q079_option_a` - `d`) |
| **Q82** | Chemistry | Section B | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: Organic reaction pathways (`neet_2021_q082_option_a` - `d`) |
| **Q88** | Chemistry | Section B | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: IUPAC molecular structures (`neet_2021_q088_option_a` - `d`) |
| **Q99** | Chemistry | Section B | `EMPTY_GRAPHICAL_OPTIONS` | 4 | Options A, B, C, D: Substituted aromatic compounds (`neet_2021_q099_option_a` - `d`) |
| **TOTAL** | — | — | **13 Questions** | **41 Assets** | **5 Stem Diagrams, 36 Option Diagrams** |

All 41 asset files exist in `backend/static/assets/diagrams/neet_2021/`, and their SHA-256 checksums match the manifest with 100% cryptographic parity.

---

## 3. Database Schema Contract & Migration

### Schema Field Addition
In [backend/app/models/competitive_models.py](file:///D:/EduSens/backend/app/models/competitive_models.py):
```python
class QuestionOption(Base):
    __tablename__ = "question_options"
    ...
    option_key = Column(String(8), nullable=False)
    option_text = Column(Text, nullable=False)
    diagram_asset_url = Column(String(512), nullable=True)  # <-- Added Milestone 5.8
    is_correct = Column(Boolean, default=False, nullable=False)
```

### Alembic Migration
- **Revision ID:** `b2c3d4e5f6a7`
- **Revises:** `a1b2c3d4e5f6`
- **File:** `backend/alembic/versions/20261025_m5_8_option_diagram_asset_url.py`
- **Upgrade:** `op.add_column('question_options', sa.Column('diagram_asset_url', sa.String(512), nullable=True))`
- **Downgrade:** `op.drop_column('question_options', 'diagram_asset_url')`
- **Validation:** Tested via Alembic config (`alembic -c backend/alembic.ini heads`) -> current head is `b2c3d4e5f6a7 (head)`. Tested non-destructive upgrade/downgrade on isolated disposable database.

---

## 4. Manifest-Driven Asset Linking Architecture

Implemented in [backend/app/services/diagram_asset_linking_service.py](file:///D:/EduSens/backend/app/services/diagram_asset_linking_service.py):

```
       ┌────────────────────────────────────────────────────────┐
       │   data/processed/neet_2021_diagram_manifest.json       │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
        validate_manifest_structure() & build_asset_index()
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
[Path Traversal & Boundary Check]               [SHA-256 Checksum Check]
  Strictly inside backend/static/assets           Must match output_sha256
                                  │
                                  ▼
                     link_assets_to_question()
     Match by (exam_code, exam_year, paper_code, question_number)
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
[asset_role == 'stem']                         [asset_role == 'option']
q['diagram_asset_url'] = /static/...           opt['diagram_asset_url'] = /static/...
```

### Security Controls Enforced
1. **Path Traversal Protection:** Any path containing `..`, leading `/`, or resolving outside `backend/static/assets/` is immediately rejected as a security violation.
2. **Deterministic Deduplication:** `compute_content_hash()` incorporates `diagram_asset_url` for stem and options. Questions without diagrams yield bit-for-bit identical hashes to legacy baselines.
3. **Empty Text Guard:** Options with empty text require a non-empty `diagram_asset_url`. Empty option text without an asset is rejected by `validate_question_data()`.

---

## 5. Human Review Workflow & State Machine Enforcement

Implemented in [backend/app/services/question_verification_service.py](file:///D:/EduSens/backend/app/services/question_verification_service.py):

### The 6 Independent Evidence Gates
A question cannot be served or scored until all 6 gates are explicitly satisfied in sequence:

```
[1. Extraction & Ingestion] ──────► verification_status = "INGESTED"
             │
             ▼
[2. Human Visual Review]   ──────► Explicit Reviewer Decision (APPROVED / REJECTED / NEEDS_CORRECTION)
             │                     Logged in QuestionVerificationLog
             │                     APPROVED -> verification_status = "CONTENT_VERIFIED"
             ▼
[3. Content Grounding]     ──────► Topic curriculum mapping validated (quarantine_status = "CLEAN")
             │
             ▼
[4. Answer-Key Reconcile]  ──────► Independent official key match (answer_verification_status != "UNVERIFIED")
             │
             ▼
[5. Rights & Permission]   ──────► Legal review cleared (rights_status in ["OFFICIAL_FAIR_USE", ...])
             │                     publish_permission != "FORBIDDEN"
             ▼
[6. Scoring Promotion]     ──────► eligibility_for_scoring = "ELIGIBLE_FOR_SCORING"
```

### Non-Conflation Guarantees
- **Visual crop approval DOES NOT promote scoring eligibility:** Approving a vector diagram certifies legibility only. `eligibility_for_scoring` remains `INELIGIBLE_UNVERIFIED_KEY` until answer key and rights clearance are independently completed.
- **Review decisions are auditable:** `QuestionVerificationLog` records `reviewer_id` (must be non-empty), `reviewed_at`, `decision`, `review_notes` (structured JSON with asset IDs and checksums), `previous_status`, and `new_status`.
- **API Isolation:** Review endpoints (`POST /competitive/questions/{question_id}/review`, `GET /competitive/review/unverified`) are reviewer-facing. Learner assessment APIs strictly exclude quarantined, unpublished, or unverified questions.

---

## 6. Controlled 13-Question Pilot Results

Script: `scripts/pilot_neet_2021_diagram_ingestion.py`  
Target: NEET UG 2021 Booklet M4 (13 Quarantined Diagram Questions)  
Database: Disposable in-memory SQLite (`PRAGMA foreign_keys = ON`)

### Execution Metrics
```
======================================================================
EDUNAVIKA MILESTONE 5.8: CONTROLLED DIAGRAM INGESTION PILOT
======================================================================
[GUARD] Canonical DB Path: D:\EduSens\edunavika.db
[GUARD] Canonical DB SHA-256 before pilot: 97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01
[DATABASE] Initialized isolated in-memory SQLite database. Paper: NEET_2021_M4
[ASSET LINKING] Validated manifest (1.0) with 41 assets across 13 question keys.
[PREPARATION] Loaded 13 target NEET 2021 questions from authentic audit.
[LINKING SUMMARY] Linked 5 stem diagrams and 36 option diagrams.
[DRY RUN] valid=13, invalid=0, dry_inserted=13 (0 database rows written)
[REAL INGESTION] inserted=13, valid=13, errors=0
[DB VERIFICATION] Persisted: 13 questions, 52 options (36 with diagrams), 5 stem diagrams, 13 verification logs
[IDEMPOTENCY] Second execution: skipped_duplicates=13, inserted=0
[HUMAN REVIEW] Q4 visual review submitted: APPROVED, new_status=CONTENT_VERIFIED
[SCORING GATE] Q4 eligible: False, blockers count: 3 (Answer key, Rights, Publish permission)
[GUARD] Canonical DB SHA-256 after pilot:  97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01
======================================================================
PILOT EXECUTION COMPLETE: 100% CHECKS PASSED WITH ZERO LEAKS
======================================================================
```

---

## 7. Automated Test & Regression Evidence

All 72 test cases executed cleanly against Python 3.11 with zero failures:

### 1. Focused Milestone 5.8 Test Suite (`backend/tests/test_asset_linking_and_review.py`)
- `test_schema_model_includes_option_diagram_asset_url` — **PASSED**
- `test_alembic_migration_script_integrity` — **PASSED**
- `test_manifest_validation_valid_and_invalid` — **PASSED**
- `test_path_traversal_rejection` — **PASSED**
- `test_checksum_verification_and_missing_file` — **PASSED**
- `test_stem_and_option_diagram_linking` — **PASSED**
- `test_content_hash_backward_compatibility` — **PASSED**
- `test_automated_gate_empty_option_text_handling` — **PASSED**
- `test_human_review_workflow_and_audit_logging` — **PASSED**
- `test_real_neet_2021_pilot_execution_real_service` — **PASSED**
- `test_assessment_session_diagram_serialization` — **PASSED**
- `test_review_api_endpoints_via_testclient` — **PASSED**
- `test_persistent_database_remains_strictly_unchanged` — **PASSED**

### 2. Regression Suites Executed
- `backend/tests/test_production_ingestion_gate.py` (8 tests) — **8/8 PASSED**
- `backend/tests/test_vector_diagram_extractor.py` (12 tests) — **12/12 PASSED**
- `backend/tests/test_pilot_ingestion.py` (8 tests) — **8/8 PASSED**
- `backend/tests/test_competitive_platform.py` (11 tests) — **11/11 PASSED**
- `backend/tests/test_exam_topic_applicability.py` (14 tests) — **14/14 PASSED**
- `backend/tests/test_curriculum_coverage_and_runtime.py` (6 tests) — **6/6 PASSED**

**Total Test Count:** **72 Passed / 0 Failed (100% Success Rate)**

---

## 8. Database Safety & Git Integrity Audit

1. **Canonical Database Guard:**
   - Path: `D:\EduSens\edunavika.db`
   - Initial SHA-256: `97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`
   - Final SHA-256: `97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`
   - **Status:** **Completely untouched. Zero persistent modifications.**
2. **Git Repository Status:**
   - Branch: `master`
   - Untracked files: Clean, only new milestone services and migration scripts.
   - History & commits: No destructive Git commands executed, no unstaged pushes.

---

## 9. Outstanding Human Review & Legal Blockers

While all engineering checks have passed with recorded proof, the 13 diagram questions cannot be released to students until the following human and legal prerequisites are signed off:

1. **Human Visual Review Signoff:** 41 extracted PNG assets are rendered and contact sheet generated (`data/processed/neet_2021_diagram_contact_sheet.html`). Authorized subject-matter experts (Physics and Chemistry) must review each crop and submit signed decisions through `POST /competitive/questions/{question_id}/review`.
2. **Authoritative Answer-Key Reconciliation Signoff:** The answer keys for Q4, Q20, Q26, Q38, Q40, Q49, Q60, Q62, Q63, Q79, Q82, Q88, and Q99 remain `UNVERIFIED` in production until reconciled against the official NTA final revised answer key (`Notice_20211101205130.pdf`).
3. **Legal Fair-Use & Redistribution Clearance:** NTA competitive exam questions are copyrighted. Ingestion into production requires legal determination of `OFFICIAL_FAIR_USE` before `publish_permission` can be changed from `FORBIDDEN` to `PUBLIC`.

---

## 10. Milestone Status & Recommended Next Step

**Milestone 5.8 Decision:** `PASS WITH REVIEW REQUIRED`

**Recommended Next Step (Milestone 5.9):**
1. Launch the reviewer UI or administrative review portal for SME signoff on the 41 candidate diagram crops.
2. Complete end-to-end NTA final answer-key reconciliation for all 200 NEET 2021 Booklet M4 questions.
3. Conduct production database migration using `b2c3d4e5f6a7` only after explicit administrative authorization and database backup.
