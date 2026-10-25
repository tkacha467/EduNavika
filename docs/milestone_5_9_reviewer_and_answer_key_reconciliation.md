# EduNavika — Milestone 5.9 Report
## Authenticated Reviewer Portal, Answer-Key Reconciliation, and Content Integrity

**Date:** October 25, 2026  
**Auditor / Architect:** Senior Full-Stack Engineer, ML Systems Architect, Database Engineer, and QA Auditor  
**Repository:** [EduNavika (GitHub)](https://github.com/tkacha467/EduNavika.git)  
**Branch:** `master`  
**Baseline HEAD Commit:** `54120ac3a9a19fa5c5e7c874c84781f28bedf2b7`  
**Final Status:** **PASS WITH REVIEW REQUIRED**

---

## 1. Initial Repository State and Baseline Verification

Before introducing modifications or running workflows, the local development environment and database were inspected:

- **Git Status:** Clean baseline on branch `master` tracking `origin/master`.
- **HEAD Commit SHA:** `54120ac3a9a19fa5c5e7c874c84781f28bedf2b7`.
- **Canonical Database Invariant:**
  - File: `D:\EduSens\edunavika.db`
  - Canonical SHA-256 Checksum: `97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`
  - Zero writes, zero schema migrations, and zero pilot mutations were executed against this database.
- **Alembic Migration Graph:**
  - Milestone 5.8 migration `b2c3d4e5f6a7` (`20261025_m5_8_option_diagram_asset_url.py`) adds `diagram_asset_url` (`VARCHAR(512)`, nullable) to `QuestionOption`.

---

## 2. Architecture and Security Decisions

### 2.1 State Separation Matrix
To prevent conflation between extraction, visual quality, correctness, and legal rights, six orthogonal states are strictly maintained in backend database models, service evaluation gates, and frontend review interfaces:

| Dimension | Attribute Name | Allowed Values | Semantic Independence |
| :--- | :--- | :--- | :--- |
| **Visual Fidelity** | `verification_status` | `INGESTED`, `NEEDS_CORRECTION`, `REJECTED`, `CONTENT_VERIFIED` | Governs vector crop quality, bounding boxes, and label clarity. |
| **Answer-Key Provenance** | `answer_verification_status` | `UNVERIFIED`, `OFFICIAL_KEY_VERIFIED`, `DISPUTED` | Governs alignment with authentic official NTA declaration. |
| **Official Question Status**| `official_status` | `REGULAR`, `DROPPED`, `BONUS`, `CANCELLED` | Records official exam authority determinations. |
| **Quarantine & Extraction** | `quarantine_status` | `CLEAN`, `QUARANTINED`, `FLAGGED_MALFORMED` | Captures parser anomalies, missing assets, or corrupt math. |
| **Legal Rights & IP** | `rights_status` | `PENDING_LEGAL_REVIEW`, `OFFICIAL_FAIR_USE`, `PROPRIETARY`, `PUBLIC_DOMAIN` | Explicit legal authorization required; never inferred. |
| **Publication Permission** | `publish_permission` | `FORBIDDEN`, `PERMITTED`, `STUDENT_PRACTICE` | Production deployment barrier. |
| **Scoring Eligibility Gate** | `eligibility_for_scoring` | `INELIGIBLE_UNVERIFIED_KEY`, `INELIGIBLE_UNVERIFIED_CONTENT`, `INELIGIBLE_QUARANTINED`, `ELIGIBLE_FOR_SCORING` | Conjunction of all 6 independent gates passing. |

### 2.2 Server-Side Authentication & Authorization
- **Role Definition:** Added `REVIEWER = "REVIEWER"` to `UserRole` enum.
- **Token Authorization (`get_current_reviewer`):** Uses FastAPI `HTTPBearer` security dependency to decode and validate JWT tokens signed with `settings.SECRET_KEY`.
- **Role Enforcement:** Permits `TEACHER`, `ADMIN`, and `REVIEWER` roles. Rejects unauthenticated callers with HTTP 401 Unauthorized; rejects `STUDENT` callers with HTTP 403 Forbidden.
- **Reviewer Identity Provenance:** The server strictly derives the reviewer identity from the authenticated JWT subject (`current_reviewer.email` or `current_reviewer.id`). Client-supplied `reviewer_id` in request payloads is ignored to prevent identity spoofing.
- **Mandatory Review Notes:** Submissions of `REJECTED` or `NEEDS_CORRECTION` strictly require non-empty notes (minimum 5 characters) validated both client-side and server-side.

---

## 3. Official Answer-Key Provenance and Reconciliation

### 3.1 Primary Source Document Verification
- **Official Source:** National Testing Agency (NTA) Revised Final Answer Key NEET (UG) – 2021
- **File Location:** `docs/reference/Notice_20211101205130.pdf`
- **File Size:** 289,883 bytes (283 KB)
- **Verified SHA-256:** `838e0ba080eb6b9639f12a1dcfb7f36cd8fe80dd5be11ee0be6d725e4c6f3ca9`
- **Target Paper Code:** Booklet `M4` (Page 1: `NEET (UG) - 2021 | BOOK : M4`)

### 3.2 Machine Extraction & Reconciliation Findings
- Automated parser `AnswerKeyReconciliationService.extract_official_manifest_from_pdf` extracted all 200 declared answers directly from the official PDF.
- **Booklet M4 Characteristics:**
  - 200 questions declared.
  - Zero dropped questions in Booklet M4.
  - Zero multiple-correct keys in Booklet M4.
  - Every question mapped to an integer `1..4` corresponding to option keys `A..D`.

### 3.3 Target 13 Diagram Questions Reconciliation
All 13 diagram-bearing questions from the Milestone 5.8 pilot were reconciled against the authentic NTA key:

| Q# | Subject | Extracted Declared Answer | NTA Raw Key | NTA Normalized Key | Status | Visual Review Status | Rights Status | Scoring Eligible |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q4** | Physics | B | 2 | B | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q20** | Physics | D | 4 | D | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q26** | Physics | C | 3 | C | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q38** | Physics | C | 3 | C | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q40** | Physics | D | 4 | D | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q49** | Physics | B | 2 | B | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q60** | Chemistry | B | 2 | B | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q62** | Chemistry | A | 1 | A | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q63** | Chemistry | D | 4 | D | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q79** | Chemistry | C | 3 | C | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q82** | Chemistry | A | 1 | A | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q88** | Chemistry | D | 4 | D | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |
| **Q99** | Chemistry | A | 1 | A | **MATCH** | INGESTED | PENDING_LEGAL_REVIEW | ❌ INELIGIBLE |

**Reconciliation Result:** 13/13 (100%) exact match.  
**Remaining 187 Questions Assessment:** Extracted JSON answers verified against NTA Booklet M4 manifest: 187/187 (100%) exact match.  
**Generated Report Artifact:** `data/processed/neet_2021_answer_key_reconciliation_report.json`

---

## 4. Frontend Reviewer Portal Implementation

Implemented `ReviewerView.ts` adhering to the existing TypeScript/SPA architecture without external framework dependencies:

- **Filter Bar:** Exam (`ALL`, `NEET`, `JEE`), Subject (`Physics`, `Chemistry`, `Biology`), Review State (`UNVERIFIED`, `APPROVED`, `NEEDS_CORRECTION`, `REJECTED`), Issue Type (`DIAGRAM`, `TEXT_ONLY`), and live search by Q# or stem.
- **Queue Panel:** Left pane listing filtered questions with status pills, subject tags, and `[🖼️ Has Diagram]` indicators.
- **Inspection Workspace:**
  - Question stem typography with zoomable diagram asset preview.
  - Option grid (A, B, C, D) displaying text, option diagrams, and declared answer keys.
  - Independent status badges for Visual Review, Answer Key, and Scoring Gate.
  - Full audit timeline rendering reviewer identity, timestamp, decision, and review notes.
- **Review Decision Submission:**
  - Three audited actions: `[✓ Approve Visual Asset]`, `[⚠ Needs Correction]`, `[✕ Reject Asset]`.
  - Enforces required review notes on rejection or correction requests.
- **Navigation Integration:**
  - Registered route `'teacher/review'` in `router.ts`.
  - Added "Question Review" to Teaching navigation group and breadcrumb hierarchy in `AppShell.ts`.
  - Verified clean TypeScript build (`npm run build`: 0 errors).

---

## 5. Verification Test Suite Results

A total of **73 automated regression and feature tests** were executed in sterile, isolated SQLite environments with foreign key constraints enforced:

```bash
pytest backend/tests/test_reviewer_portal_and_reconciliation.py \
       backend/tests/test_asset_linking_and_review.py \
       backend/tests/test_answer_key_reconciliation.py \
       backend/tests/test_production_ingestion_gate.py \
       backend/tests/test_vector_diagram_extractor.py \
       backend/tests/test_pilot_ingestion.py \
       backend/tests/test_competitive_platform.py -v
```

### Test Summary:
- **`test_reviewer_portal_and_reconciliation.py` (11 tests):**
  - `test_unauthenticated_request_rejected`: PASSED
  - `test_student_role_forbidden_from_reviewer_endpoints`: PASSED
  - `test_authorized_roles_accepted`: PASSED
  - `test_reviewer_identity_bound_to_token_subject`: PASSED
  - `test_rejection_requires_mandatory_notes`: PASSED
  - `test_question_detail_endpoint_returns_options_and_history`: PASSED
  - `test_official_nta_answer_key_pdf_checksum_and_extraction`: PASSED
  - `test_answer_key_reconciliation_maintains_independent_states`: PASSED
  - `test_scoring_eligibility_requires_all_six_gates`: PASSED
  - `test_student_assessment_session_filters_ineligible_questions`: PASSED
  - `test_persistent_database_isolation_invariant`: PASSED
- **`test_asset_linking_and_review.py` (13 tests):** ALL PASSED
- **`test_answer_key_reconciliation.py` (10 tests):** ALL PASSED
- **`test_production_ingestion_gate.py` (8 tests):** ALL PASSED
- **`test_vector_diagram_extractor.py` (12 tests):** ALL PASSED
- **`test_pilot_ingestion.py` (8 tests):** ALL PASSED
- **`test_competitive_platform.py` (11 tests):** ALL PASSED

**Total Executed:** 73 passed, 0 failed, 0 skipped (Runtime: 12.40s)

---

## 6. Database Isolation Invariant

- Before test execution: `edunavika.db` SHA-256 = `97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`
- After test execution: `edunavika.db` SHA-256 = `97f760b8cfa3bc22d632700e15b494013dfca2fa2200cebd56f80ba9934ceb01`
- Invariant confirmed: 0 writes to the persistent canonical database.

---

## 7. Remaining Blockers and Prerequisites (Why Status is "PASS WITH REVIEW REQUIRED")

While engineering implementation, cryptographic checksums, automated reconciliation, and security gates are 100% verified, the questions remain intentionally **INELIGIBLE FOR SCORING** due to required human and legal actions:

1. **Human Subject-Matter Expert (SME) Visual Review:**
   - 13 diagram questions require an authorized SME to review visual crops in the Reviewer Portal and commit `APPROVED` decisions.
2. **Legal Rights Clearance & IP Authorization:**
   - Questions currently remain in `rights_status="PENDING_LEGAL_REVIEW"` and `publish_permission="FORBIDDEN"`.
   - Official NTA examination papers are subject to copyright. Institutional legal counsel must document the fair use exemption or licensing authorization before `rights_status` can be promoted to `OFFICIAL_FAIR_USE` or `PUBLIC_DOMAIN`.
3. **No Bulk Ingestion:**
   - Per non-negotiable constraints, bulk ingestion of the 200 NEET 2021 questions into the production database is prohibited until SME visual review and legal clearance are completed.

---

## 8. Exact Files Modified and Created

### Files Created:
- `backend/tests/test_reviewer_portal_and_reconciliation.py` (Milestone 5.9 test suite)
- `frontend/src/features/teacher/ReviewerView.ts` (Authenticated Reviewer Portal UI)
- `scripts/reconcile_neet_2021_answer_keys.py` (Reproducible reconciliation runner)
- `data/processed/neet_2021_answer_key_reconciliation_report.json` (Machine-readable audit report)
- `docs/milestone_5_9_reviewer_and_answer_key_reconciliation.md` (This document)

### Files Modified:
- `backend/app/domain/enums.py` (Added `REVIEWER` role)
- `backend/app/core/security.py` (Implemented `get_current_user` and `get_current_reviewer`)
- `backend/app/api/v1/endpoints/competitive.py` (Secured review endpoints, detail endpoint, query filters)
- `backend/app/services/answer_key_reconciliation_service.py` (Added `extract_official_manifest_from_pdf`)
- `backend/tests/test_asset_linking_and_review.py` (Updated to use authenticated reviewer token)
- `frontend/src/services/competitiveService.ts` (Added API client review methods)
- `frontend/src/routes/router.ts` (Wired `teacher/review` route)
- `frontend/src/layouts/AppShell.ts` (Added Question Review sidebar nav and breadcrumb)

---

## Final Verdict

**PASS WITH REVIEW REQUIRED**

*All engineering requirements, server-side authorization controls, official NTA PDF cryptographic validation, answer-key reconciliation, reviewer portal UI, and 73 regression tests have passed with 100% success. Questions remain securely held in quarantine/ineligible status until authorized subject-matter experts complete visual reviews and institutional legal counsel provides explicit copyright clearance.*
