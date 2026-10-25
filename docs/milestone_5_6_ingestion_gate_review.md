# EduNavika — Milestone 5.6: Production Ingestion Gate & Pilot Integrity Review

**Role:** Senior Data-Ingestion Architect & Independent Assessment QA Engineer  
**Audit Scope:** Production Ingestion Gate, State Machine Verification, Rights Clearance Audit, and Pilot Integrity Review  
**Target Paper:** NEET (UG) 2021 Booklet Code `M4` (`GSEB-Dataset/Dataset/Dataset/Neet/neet-2021.pdf`)  
**Official Reference Key:** `docs/reference/Notice_20211101205130.pdf` (Published 01.11.2021, Page 13: `BOOK : M4`)  
**Date:** October 22, 2026  
**Final Decision for Persistent Database Ingestion:** **STRICT NO-GO**  
**Disposable/In-Memory Test Ingestion:** **APPROVED (GO WITH SAFE STATE GUARDS)**  

---

## 1. Executive Summary

Milestone 5.6 conducted an adversarial audit of the Milestone 5.5 controlled pilot to determine whether EduNavika's actual production ingestion pipeline safely enforces extraction quality, content verification, answer-key reconciliation, and publication permissions.

### Key Audit Conclusions

1. **Milestone 5.5 Pilot Audit Findings:**
   - The Milestone 5.5 10-question pilot executed in Step 5978 **did not call `QuestionIngestionService`**.
   - Questions and options were directly constructed as ORM models (`Question`, `QuestionOption`, `ExamPaper`) and added to the session via `db.add()`, completely bypassing the 10-point automated ingestion validation gate.
   - All 10 questions were promoted to `ELIGIBLE_FOR_SCORING` because the script hardcoded `quarantine_status='CLEAN'`, and `AnswerKeyReconciliationService` previously assumed that any question matching an official key with `quarantine_status=='CLEAN'` was eligible for scoring, thereby conflating answer-key reconciliation with content verification.
   - Rights and permissions were prematurely hardcoded as `rights_status='OFFICIAL_FAIR_USE'` and `publish_permission='ALLOWED'`.
   - Content hashes were assigned dummy synthetic strings (`'pilot_hash_%d'`) rather than cryptographic content digests.
2. **State Machine Disconnect Identified & Repaired:**
   - Answer-key reconciliation must not promote a question to `ELIGIBLE_FOR_SCORING` unless its content has been explicitly verified (`verification_status in ('CONTENT_VERIFIED', 'VERIFIED')`).
   - We updated `AnswerKeyReconciliationService` and `QuestionIngestionService` to enforce this rule: unverified content matching an official key transitions to `INELIGIBLE_UNVERIFIED_CONTENT`.
3. **Publication Permissions Enforced in Serving Layer:**
   - `CompetitiveAssessmentService` and API query endpoints previously lacked checks for `publish_permission`.
   - The serving layer now strictly filters `Question.publish_permission != 'FORBIDDEN'`, ensuring that items with pending legal clearance (`PENDING_LEGAL_REVIEW`) are never served to students.
   - The PDF parser default was updated from `publish_permission='OFFICIAL_FAIR_USE'` to `publish_permission='FORBIDDEN'` and `rights_status='PENDING_LEGAL_REVIEW'`.
4. **Real Ingestion Service Validated via 8-Case Regression Suite:**
   - Built [`backend/tests/test_production_ingestion_gate.py`](file:///d:/EduSens/backend/tests/test_production_ingestion_gate.py) exercising the real `QuestionIngestionService`, `AnswerKeyReconciliationService`, and `CompetitiveAssessmentService` on a disposable in-memory SQLite database across all 8 mandatory boundary conditions. All 8 tests passed.
   - Full competitive test suite now comprises **58 passed tests** (0 failures).
5. **Persistent Database Remains Untouched:**
   - Canonical persistent database [edunavika.db](file:///d:/EduSens/edunavika.db) verified at strictly **0 competitive records** before, during, and after all audits and tests.
6. **Explicit Decision:**
   - **NO-GO FOR PERSISTENT BULK INGESTION:** Bulk ingestion into `edunavika.db` is strictly blocked until:
     - The 13 vector-drawn questions receive raster graphics assets.
     - The remaining 167 text questions receive human content verification.
     - Legal counsel provides formal clearance for official NTA exam question redistribution.

---

## 2. Findings Ranked by Severity

| ID | Severity | Category | Description | Remediation Implemented in Milestone 5.6 |
| :--- | :---: | :--- | :--- | :--- |
| **F-01** | **CRITICAL** | Pipeline Bypass | Milestone 5.5 pilot directly instantiated ORM records, bypassing `QuestionIngestionService.validate_question_data()` and `ingest_paper_batch()`. | Built `test_production_ingestion_gate.py` exercising the real `QuestionIngestionService` pipeline with strict validation assertions. |
| **F-02** | **HIGH** | Conflation of Key with Quality | `AnswerKeyReconciliationService` promoted any question with `quarantine_status=='CLEAN'` to `ELIGIBLE_FOR_SCORING`, regardless of whether content had been verified. | Implemented guard in `AnswerKeyReconciliationService`: questions without verified content transition to `INELIGIBLE_UNVERIFIED_CONTENT`. |
| **F-03** | **HIGH** | Premature Rights Clearance | Digital PDF parser and pilot script hardcoded `rights_status='OFFICIAL_FAIR_USE'` and `publish_permission='ALLOWED'`, automatically granting clearance without legal review. | Updated parser defaults to `rights_status='PENDING_LEGAL_REVIEW'` and `publish_permission='FORBIDDEN'`. Added ingestion gate rejecting publication without explicit clearance. |
| **F-04** | **HIGH** | Serving Layer Leakage | `CompetitiveAssessmentService.start_assessment_session()` and API endpoints did not filter on `publish_permission`, allowing forbidden items to be served if marked eligible. | Enforced `Question.publish_permission != 'FORBIDDEN'` across `CompetitiveAssessmentService` and API endpoints. |
| **F-05** | **MEDIUM** | Ingestion Provenance Gap | Milestone 5.5 pilot assigned synthetic dummy content hashes (`pilot_hash_1`) and omitted automated ingestion verification logs. | Production ingestion service enforces deterministic SHA-256 deduplication via `compute_content_hash()` and generates `QuestionVerificationLog` entries. |

---

## 3. Audit of the Milestone 5.5 Pilot Implementation

### Execution Trace Analysis (Step 5978)
In Milestone 5.5, the pilot script executed the following logic:
```python
# Extracted from Step 5978 in transcript_full.jsonl:
manifest = extract_official_nta_manifest(DEFAULT_NTA_KEY_PDF)
records, summary = parse_and_audit_neet_paper(DEFAULT_PAPER_PDF, manifest)
pilot_qnums = [1, 8, 35, 46, 50, 51, 75, 100, 101, 196]
pilot_records = [r for r in records if r['question_number'] in pilot_qnums]

# BYPASS: QuestionIngestionService was imported but never invoked
paper = ExamPaper(id=paper_id, ...)
db.add(paper)

for pr in pilot_records:
    q = Question(
        id=qid,
        exam_paper_id=paper_id,
        topic_id=top.id,
        paper_question_number=pr['question_number'],
        question_text=pr['normalized_stem'],
        question_type='SCQ',
        content_hash='pilot_hash_%d' % pr['question_number'], # Synthetic hash
        quarantine_status='CLEAN',                            # Hardcoded CLEAN
        eligibility_for_scoring='INELIGIBLE_UNVERIFIED',
        verification_status='PENDING_KEY_RECONCILIATION',
        answer_verification_status='UNVERIFIED',
        rights_status='OFFICIAL_FAIR_USE',                    # Premature rights clearance
        publish_permission='ALLOWED',                         # Premature publication
        official_status='PENDING',
    )
    db.add(q)
    ...
db.commit()

# Reconcile batch
reconciler = AnswerKeyReconciliationService(db)
recon_res = reconciler.reconcile_paper_batch(paper_id=paper_id, manifest=pilot_manifest, ...)
```

### Critical Deficiencies Identified
1. **Validation Gate Bypassed:** `QuestionIngestionService.validate_question_data()` was never called. If a question had unbalanced LaTeX or empty options, it would have been committed directly.
2. **Automated Promotion Artifact:** All 10 questions were promoted to `ELIGIBLE_FOR_SCORING` because the script set `quarantine_status='CLEAN'`, and `reconcile_question_record` had no check to verify whether human or algorithmic content verification had occurred.
3. **No Content Provenance Hash:** Using `'pilot_hash_%d'` bypassed the cryptographic SHA-256 deduplication logic (`compute_content_hash()`).
4. **Distinction Between Fixtures and Production:** While acceptable as an ad-hoc exploratory script, this pattern cannot be used for production ingestion. Production ingestion must route through `QuestionIngestionService.ingest_paper_batch()`.

---

## 4. Enforcing a Safe State Machine

To prevent unverified or defective questions from entering active student assessments, we formalized and implemented the 7-stage question lifecycle state machine:

```
[1. PARSED]
     │
     ▼
[2. QUALITY_CHECKED] ──(Check Fails)──► [3. QUARANTINED / AWAITING_REVIEW]
     │                                            │
     ▼ (Passes 10-Point Gate)                     │ (Remains blocked from scoring)
[4. CONTENT_VERIFIED]                             ▼
     │                                     [INELIGIBLE_MALFORMED]
     ▼
[5. ANSWER_KEY_RECONCILED]
     │
     ├─► Content Verified? ──► YES ──► [6. SCORING_ELIGIBLE]
     │                                          │
     └─► Content Verified? ──► NO               ▼
              │                           Rights Cleared? ──► YES ──► [7. PUBLICATION_APPROVED]
              ▼                                 │
   [INELIGIBLE_UNVERIFIED_CONTENT]              └─► NO  ──► [PUBLICATION_BLOCKED / FORBIDDEN]
```

### State Definitions and Invariants

| State | DB Field Invariants | Permitted Next Transitions | Assessment / API Serving Behavior |
| :--- | :--- | :--- | :--- |
| **1. PARSED** | `verification_status='EXTRACTED_PENDING_REVIEW'`, `answer_verification_status='UNVERIFIED'`, `quarantine_status='CLEAN'`, `publish_permission='FORBIDDEN'` | `QUALITY_CHECKED`, `QUARANTINED` | Excluded from assessments. |
| **2. QUALITY_CHECKED** | Passes 10-point gate (KaTeX balanced, 4 non-empty options, stem >= 10 chars, topic mapped). `verification_status='QUALITY_CHECKED'` | `CONTENT_VERIFIED`, `QUARANTINED` | Excluded from assessments. |
| **3. QUARANTINED** | `quarantine_status in ('INELIGIBLE_EMPTY_OPTIONS', 'INELIGIBLE_REQUIRES_ASSET', 'FLAGGED_MALFORMED')`, `eligibility_for_scoring='INELIGIBLE_QUARANTINED'` | `AWAITING_REVIEW`, `REPAIRED` | **Strictly excluded.** Reconciler can update answer key, but scoring status transitions to `INELIGIBLE_MALFORMED`. |
| **4. CONTENT_VERIFIED** | Human QA or high-fidelity renderer verified against source PDF. `verification_status='CONTENT_VERIFIED'`. | `ANSWER_KEY_RECONCILED` | Excluded from assessments until official key is reconciled. |
| **5. KEY_RECONCILED** | Matched against official NTA manifest. `answer_verification_status='OFFICIAL_KEY_VERIFIED'`. | `SCORING_ELIGIBLE` (if content verified), `INELIGIBLE_UNVERIFIED_CONTENT` (if unverified) | Excluded if content is unverified. |
| **6. SCORING_ELIGIBLE** | `eligibility_for_scoring='ELIGIBLE_FOR_SCORING'`, `quarantine_status='CLEAN'`, `answer_verification_status='OFFICIAL_KEY_VERIFIED'`, `verification_status in ('CONTENT_VERIFIED', 'VERIFIED')`. | `PUBLICATION_APPROVED` | Eligible for scoring, but requires publication clearance before serving. |
| **7. PUBLICATION_APPROVED** | `publish_permission='ALLOWED'`, `rights_status in ('OFFICIAL_FAIR_USE', 'PUBLIC_DOMAIN', 'PROPRIETARY')`. | `REVOKED`, `ARCHIVED` | **Served to students** in active timed assessment sessions and public APIs. |

---

## 5. Review of Rights and Publication Permissions

### Code Audit of Hardcoded Assignments

| File Location | Inspected Field | Original Hardcoded Value | Identified Risk | Milestone 5.6 Remediation |
| :--- | :--- | :--- | :--- | :--- |
| `backend/app/ingestion/competitive_paper_parser.py:381` | `rights_status` | `"OFFICIAL_FAIR_USE"` | Automatically declared legal fair use on raw PDF extraction without human legal review. | Updated to `"PENDING_LEGAL_REVIEW"`. |
| `backend/app/ingestion/competitive_paper_parser.py:382` | `publish_permission` | `"OFFICIAL_FAIR_USE"` | Assigned invalid value and bypassed publication gating. | Updated to `"FORBIDDEN"`. |
| `backend/app/services/answer_key_reconciliation_service.py:275` | `eligibility_for_scoring` | `"ELIGIBLE_FOR_SCORING"` | Promoted unverified content to scoring eligibility solely on key match. | Added content verification check: transitions to `"INELIGIBLE_UNVERIFIED_CONTENT"`. |
| `backend/app/services/competitive_assessment_service.py:153` | `publish_permission` | *(Missing check)* | Allowed questions with pending rights to be served to students. | Added `Question.publish_permission != 'FORBIDDEN'` filter. |
| `backend/app/api/v1/endpoints/competitive.py:144, 185` | `publish_permission` | *(Missing check)* | Allowed public API to retrieve questions without publication permission. | Added `Question.publish_permission != 'FORBIDDEN'` filter. |

### Rights & Legal Clearance Status Documentation
- **Source Document:** NTA NEET (UG) 2021 Question Paper Booklet M4 and NTA Public Notice Dated 01.11.2021.
- **Current Legal Status:** EduNavika does not hold an explicit commercial redistribution license from the National Testing Agency.
- **Fair Use Consideration:** While educational non-commercial testing analysis may qualify under fair use doctrines, production publication requires explicit written clearance or a formal institutional legal review.
- **System Safeguard:** All competitive questions must remain in `rights_status='PENDING_LEGAL_REVIEW'` and `publish_permission='FORBIDDEN'` until administrative sign-off is logged in `QuestionVerificationLog`.

---

## 6. Real Ingestion Service Test Results

We implemented and executed [`backend/tests/test_production_ingestion_gate.py`](file:///d:/EduSens/backend/tests/test_production_ingestion_gate.py), exercising the real service on an isolated in-memory SQLite database:

| Test Case | Scenario Description | Expected Ingestion & Reconciliation Result | Assessment & Serving Visibility Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **Case 1** | Valid, reviewed text-only question | Ingestion passes (valid=1, inserted=1). Reconciled with NTA key $\rightarrow$ `ELIGIBLE_FOR_SCORING`, `VERIFIED`. | Assessment session successfully created; question returned with masked secret answers. | **PASSED** |
| **Case 2** | Question with missing option (3 options) | 10-point gate rejects (invalid=1, inserted=0). Error: `"requires exactly 4 options, found 3"`. | Zero records inserted; assessment cannot be created. | **PASSED** |
| **Case 3** | Question with missing diagram | Ingested as quarantined (`INELIGIBLE_REQUIRES_ASSET`). Reconciled $\rightarrow$ remains `INELIGIBLE_MALFORMED`. | Assessment query filters out question; raises `ValueError: No eligible verified questions`. | **PASSED** |
| **Case 4** | Mismatched official answer key | Reconciler rejects booklet mismatch (Paper M4 vs Manifest P1) with `ReconciliationError: AMBIGUOUS_BOOKLET_CODE`. | Question remains `INELIGIBLE_UNVERIFIED_KEY`; excluded from assessments. | **PASSED** |
| **Case 5** | Correct key but unverified content | Reconciled with NTA key, but content status is `INGESTED` $\rightarrow$ set to `INELIGIBLE_UNVERIFIED_CONTENT`. | Assessment query filters out unverified content; raises `ValueError`. | **PASSED** |
| **Case 6** | Question without publication permission | Reconciled to `ELIGIBLE_FOR_SCORING`, but `publish_permission='FORBIDDEN'`. | Serving layer blocks question; raises `ValueError: No eligible verified questions`. | **PASSED** |
| **Case 7** | Duplicate ingestion and rollback | Re-ingesting identical content skips duplicate (1 skipped, 0 inserted). Constraint failure rolls back cleanly. | Zero duplicates created; rollback leaves DB consistent. | **PASSED** |
| **Case 8** | Persistent DB counts verification | Queries canonical `edunavika.db` in read-only mode across all competitive tables. | `questions=0`, `exam_papers=0`, `question_options=0`, `mcq_questions=80`. | **PASSED** |

### Complete Test Suite Execution
```bash
pytest backend/tests/test_answer_key_reconciliation.py \
       backend/tests/test_digital_pyq_pipeline.py \
       backend/tests/test_neet_2021_independent_audit.py \
       backend/tests/test_neet_2021_quality_audit.py \
       backend/tests/test_pilot_ingestion.py \
       backend/tests/test_competitive_platform.py \
       backend/tests/test_production_ingestion_gate.py
```
**Results:** **58 passed, 4 warnings in 11.58s** (100% test pass rate).

---

## 7. Pilot Dataset Validation & Manual Verification Scope

### Justification of the 10-Question Pilot Sample
The 10 questions selected for pilot testing represent a stratified cross-section of clean items across subjects, sections, and pedagogical categories:
1. **Q1 (Physics Sec A):** Multi-statement Zener diode / p-n junction (Options intact).
2. **Q8 (Physics Sec A):** Lens distance calculation with numerical options (`25`, `15`, `50`, `30`).
3. **Q35 (Physics Sec B):** Nuclear fragmentation with section footer stripping (`Section - B (Physics)`).
4. **Q46 (Physics Sec B):** Step-down transformer numerical calculation (`0.2 A`).
5. **Q50 (Physics Sec B):** Ring moment of inertia two-line fractions ($\frac{3}{4}, \frac{7}{8}, \frac{1}{4}, \frac{1}{8}$).
6. **Q51 (Chemistry Sec A):** Mayer thermodynamic formula ($C_p - C_v = R$).
7. **Q75 (Chemistry Sec A):** Beryllium chloride structure (Polymeric chain and dimer).
8. **Q100 (Chemistry Sec B):** Isothermal expansion formulas and section footer stripping.
9. **Q101 (Botany Sec A):** Gross and Net Primary Productivity ecology statements.
10. **Q196 (Zoology Sec B):** Altitude sickness Assertion (A) & Reason (R) statements.

### Boundary of Certified Content Verification
- **Manually Compared Against PDF Renderings:** Exactly **20 questions** (Q1, Q2, Q4, Q8, Q20, Q26, Q34, Q35, Q38, Q40, Q46, Q49, Q50, Q51, Q60, Q75, Q82, Q100, Q196, Q200).
- **Automated Algorithmic Heuristic Only:** **167 questions** (Passed regex, KaTeX syntax, option cardinality, and NTA answer-key reconciliation, but **have not yet been visually audited line-by-line** by a human subject-matter expert).
- **Confirmed Defects Quarantined:** **13 questions** (9 empty vector options + 4 hard stem diagram references).
- **Rule:** Under the Milestone 5.6 state machine, the 167 algorithmic items must enter the database as `verification_status='INGESTED'` and `eligibility_for_scoring='INELIGIBLE_UNVERIFIED_CONTENT'` until a human reviewer completes visual verification.

---

## 8. Persistent Database Verification

Read-only SQL queries executed against canonical development database [edunavika.db](file:///d:/EduSens/edunavika.db) confirm zero mutation:

| Table | Baseline Before Milestone 5.6 | Count After Milestone 5.6 | Net Mutation |
| :--- | :---: | :---: | :---: |
| `examinations` | 3 | 3 | 0 |
| `exam_papers` | 0 | 0 | 0 |
| `questions` | 0 | 0 | 0 |
| `question_options` | 0 | 0 | 0 |
| `question_verification_logs` | 0 | 0 | 0 |
| `mcq_questions` (Legacy seed) | 80 | 80 | 0 |

---

## 9. Remaining Limitations & Explicit GO/NO-GO Decision

### Remaining Limitations
1. **Vector Drawing Extraction Gap:** 13 questions remain unsolvable from text alone because diagrams are encoded as PDF vector paths (`get_drawings()`). A rasterization sub-pipeline is required.
2. **Unverified Content in 167 Items:** Only 20 questions have been certified via visual rendering comparison. 167 items require human QA sign-off.
3. **Legal Clearance Pending:** Institutional rights status remains `PENDING_LEGAL_REVIEW`.

### Explicit Decision
- **ISOLATED TEST / STAGING PILOT:** **GO WITH SAFE GUARDS.** The pipeline now safely rejects missing options, isolates quarantined items, prevents unverified content promotion, and enforces publication guards.
- **PERSISTENT CANONICAL INGESTION (`edunavika.db`):** **STRICT NO-GO.** Ingestion into the persistent production database is strictly prohibited until:
  1. A vector graphics rasterizer extracts visual figures for the 13 quarantined items.
  2. Human QA verifies the 167 unreviewed questions against rendered source pages.
  3. Formal legal rights clearance transitions `rights_status` from `PENDING_LEGAL_REVIEW` to `OFFICIAL_FAIR_USE` with administrative approval.
