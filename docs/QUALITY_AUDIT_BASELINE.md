# EduNavika — Quality Upgrade Baseline Report (Phase 0)

**Date:** October 27, 2026  
**Auditor:** Principal Application Security Engineer & System Reliability Architect  
**Repository:** [https://github.com/tkacha467/EduNavika.git](https://github.com/tkacha467/EduNavika.git)  
**Branch:** `master`  
**Baseline Commit:** `43be188` (`docs: Add comprehensive CURRENT_PROGRESS.md and update implementation status`)  
**Canonical Database Path:** `D:\EduSens\edunavika.db`  
**Canonical Database SHA-256:** `B02122C54FB680C7B7AA7F5141543BBCB57B258EAB9FB64D333A15322E5D687C`  
**Canonical Database Size:** 5,525,504 bytes  
**Alembic Head Revision:** `b2c3d4e5f6a7` (`add_diagram_asset_url_to_question_options`)

---

## 1. Executive Summary & Audit Scope

EduNavika is an on-device AI-powered adaptive learning and competitive exam platform targeting GSEB / NCERT Standards 10, 11, and 12, with preparation modules for JEE Main, JEE Advanced, and NEET UG.

This baseline report captures the operational state of the codebase prior to the Phase 1–10 quality and security overhaul. In accordance with core rules:
- No unrequested rewrites or architectural replacements.
- Canonical database remains strictly untouched during all security and migration tests.
- Zero commits or pushes to remote without explicit user authorization.
- All historical completion reports are treated as claims to verify against running code.

---

## 2. Discovered Architecture & Runtime Baseline

### 2.1 Technology Stack
- **Backend Framework:** FastAPI (`0.115.6`), Pydantic (`2.10.4`), Starlette
- **ORM & Database:** SQLAlchemy 2.0 (`2.0.36`), SQLite 3 (WAL mode enabled)
- **Migrations:** Alembic (`1.14.0`)
- **Authentication & Security:** Python-Jose (`3.3.0`), Passlib / Bcrypt (`4.0.1`), Secrets module
- **PDF & Vector Extraction:** PyMuPDF (`1.25.1`), SymPy (`1.13.3`)
- **Frontend Framework:** Vanilla TypeScript SPA (`5.7.2`), Vite (`6.0.7`), Hash-based routing (`#/student/...`, `#/teacher/...`)
- **Testing Frameworks:** Pytest (`9.1.1`), Vitest (`2.1.8`)

### 2.2 Running Service Verification
- **API Server:** Port `8000` — `GET /health` returned `{"status":"healthy","service":"EduNavika API","version":"1.0.0"}`
- **Frontend Dev Server:** Port `3000` — Serves SPA with Vite proxy forwarding `/api` -> `http://localhost:8000`
- **Frontend Production Build:** `npm run build` (`tsc && vite build`) passed cleanly in 2.40s.

---

## 3. Baseline Test Results & Pre-Existing Failures

### 3.1 Backend Test Suite (`pytest backend/tests/ -q -m "not slow"`)
- **Total Passing Tests:** 500 tests passed.
- **Failures / Anomalies Recorded:**
  1. `test_pilot_ingestion.py::test_8_persistent_database_is_unchanged`:
     - Failed due to hardcoded historical SHA-256 whitelist missing the post-Milestone 5.10 canonical DB hash (`B02122C54FB680C7B7AA7F5141543BBCB57B258EAB9FB64D333A15322E5D687C`).
  2. `test_production_ingestion_gate.py::test_8_persistent_database_counts_remain_zero`:
     - Failed (`assert 272 == 0`) because Milestone 5.10 legitimately activated 272 verified PYQ questions in `edunavika.db`, whereas this earlier test asserted 0 questions.
  3. `test_reviewer_portal_and_reconciliation.py::test_persistent_database_isolation_invariant`:
     - Failed due to hash difference after the auto-creation of default user accounts during running server startup.
  4. `test_database_isolation.py::test_7_persistent_database_remains_completely_unmodified`:
     - Failed for the same hash discrepancy reason.
  5. **Total Test Coverage Gap:** Zero automated test files existed for authentication (`/api/v1/auth`), student horizontal authorization, or Class 10/11/12 standard boundary enforcement.

### 3.2 Frontend Test Suite (`vitest run`)
- Both `examSelection.test.ts` and `frontend.test.ts` failed collection because `vitest` lacked browser environment configuration (`globals: true` / environment setup in `vite.config.ts`).
- Production build (`tsc && vite build`) is completely green.

---

## 4. Security & Architecture Vulnerability Inventory (Pre-Modification)

Auditing of `backend/app/api/v1/endpoints/auth.py`, `backend/app/core/security.py`, and domain routers revealed 6 critical security deficiencies:

| ID | Component | Vulnerability Class | Severity | Description |
|:---|:---|:---|:---:|:---|
| **SEC-01** | `/api/v1/auth/forgot-password` | **Account Takeover / Token Leak** | **CRITICAL** | Endpoint generates a password reset token and directly returns `reset_token` and `reset_link` in the HTTP response JSON body. Any anonymous caller can request a reset for any email and immediately hijack the account. |
| **SEC-02** | `/api/v1/auth/forgot-password` | **Account Enumeration** | **MEDIUM** | Returns `HTTP 404: No account found associated with {email}` if email is not found, allowing attackers to harvest registered emails. |
| **SEC-03** | `/api/v1/auth/change-password` | **Broken Authentication** | **HIGH** | Does not require an active Bearer JWT session (`Depends(get_current_user)` missing); accepts arbitrary `email` and passwords without validating session identity. |
| **SEC-04** | All Student Endpoints (`/adaptive`, `/learning-events`, `/attempts`, `/assessments`) | **Broken Access Control / IDOR** | **CRITICAL** | Endpoints accept unauthenticated calls and trust client-supplied `student_id` path/query parameters without verifying the caller's JWT token or account ownership. Students can read/write any other student's history. |
| **SEC-05** | `/api/v1/auth/login` | **Hardcoded Student Standard / Profile Mocking** | **MEDIUM** | Login endpoint returns hardcoded `"grade": "Grade 10"` for all students, ignoring their real database `StudentProfile` and standard enrollment. |
| **SEC-06** | Curriculum & Exam APIs (`/competitive`, `/adaptive`, `/curriculum`) | **Standard Boundary Violation** | **HIGH** | Class 10 students can directly query Class 11 & 12 chapters, topics, and competitive examinations (JEE Main / JEE Advanced / NEET UG) because backend queries lack standard/enrollment enforcement. |

---

## 5. Master Private Working Checklist

- [x] **Phase 0:** Repository & Runtime Baseline Documented (`docs/QUALITY_AUDIT_BASELINE.md`).
- [ ] **Phase 1:** Authentication Security Audit and Repair:
  - [ ] SEC-01 & SEC-02: Fix `/forgot-password` to return a generic message without returning reset tokens or disclosing user existence.
  - [ ] SEC-03: Enforce `get_current_user` on `/change-password` and bind to the authenticated caller.
  - [ ] SEC-05: Return authentic student profile & standard information in `/login`.
  - [ ] Add sliding-window rate limiting on `/login` and `/forgot-password`.
  - [ ] Document audit and fixes in `docs/SECURITY_AUTHORIZATION_AUDIT.md`.
- [ ] **Phase 2:** Authorization and Role-Based Access Control:
  - [ ] Implement `get_current_student`, `get_current_teacher`, `get_current_admin`, and `verify_student_ownership`.
  - [ ] Protect student endpoints (`/adaptive/...`, `/learning-events/...`, `/attempts/...`, `/assessments/start`) with JWT authentication and strict ownership verification.
  - [ ] Establish server-authoritative role and permission matrix.
- [ ] **Phase 3:** Class 10, 11, and 12 Curriculum Access Rules:
  - [ ] Class 10 isolation: Block access to Class 11/12 Science subjects, chapters, topics, and competitive exams.
  - [ ] Class 11/12 scope enforcement: Enforce standard-bound curriculum queries on backend.
  - [ ] Document curriculum access rules in `docs/CURRICULUM_ACCESS_POLICY.md`.
- [ ] **Phase 4:** Authentication & Curriculum Test Matrix:
  - [ ] Write isolated unit & integration tests in `backend/tests/test_security_and_curriculum_access.py`.
  - [ ] Validate 401 Unauthorized for anonymous requests.
  - [ ] Validate 403 Forbidden for horizontal student IDOR and vertical privilege escalation.
  - [ ] Validate standard separation between Class 10 and 11/12.
- [ ] **Phase 5:** Complete Feature Inventory:
  - [ ] Trace all 30 frontend routes and backend endpoints.
  - [ ] Document status matrix in `docs/FEATURE_AUDIT_MATRIX.md` with explicit statuses.
- [ ] **Phase 6:** Functional Testing & Defect Repair.
- [ ] **Phase 7:** Database and Migration Safety Verification.
- [ ] **Phase 8:** Frontend Quality, Accessibility, and Routing Verification.
- [ ] **Phase 9:** Automation, Regression, and Performance Check.
- [ ] **Phase 10:** Final Quality Upgrade Report (`docs/QUALITY_UPGRADE_FINAL_REPORT.md`).
