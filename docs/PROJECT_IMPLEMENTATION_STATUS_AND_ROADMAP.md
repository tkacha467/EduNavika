# EduNavika Project Implementation Status and Roadmap

**Status snapshot: 8 November 2026**

## Executive summary

EduNavika has evolved from a GSEB school-learning platform into a JEE Main, JEE Advanced, and NEET preparation product. It has a substantial FastAPI/SQLAlchemy backend, TypeScript/Vite frontend, competitive-question ingestion and verification foundations, curriculum mapping, assessment components, reviewer operations, and an in-progress production authentication architecture.

The project is **not production-ready**. The highest-priority remaining work is to finish and adversarially verify authentication, establish a clean reproducible backend environment, prove content rights/quality for every served question, and validate the JEE/NEET student workflow end to end.

## Product direction

The intended learner journey is:

1. Secure account creation and exam-oriented onboarding.
2. JEE Main, JEE Advanced, or NEET subject/chapter selection.
3. Textbook and PYQ practice with verified questions, diagrams, answers, and explanations.
4. Timed chapter, subject, and full-paper assessments.
5. Results, topic feedback, revision recommendations, and progress analytics.
6. A future five-round learning protocol supporting scientifically validated learning/retention models.

Legacy Standard-10/GSEB interfaces still exist. They must not be mistaken for the finished competitive-exam experience.

## What is implemented

### Backend and data foundation

- FastAPI versioned API application and SQLAlchemy model structure.
- Alembic migration history for core, curriculum, competitive-exam, and diagram-asset work.
- SQLite local development/test support with disposable test database fixtures and foreign-key enforcement.
- Curriculum hierarchy, canonical topic/exam mapping, competitive examination, paper, question, option, verification-log, and assessment models.
- Competitive ingestion/parser, question eligibility gates, deterministic answer-key reconciliation, reviewer workflow, diagram-asset handling, and provenance/audit artefacts.
- NEET 2021 M4 reconciliation artefact: 200 declared questions, 187 text items and 13 diagram-dependent items. Rights/publication approval remains pending.

### Authentication and authorization foundation

- Bcrypt password hashing and signed expiring JWT access tokens.
- Production configuration rejects missing/weak JWT secrets and SQLite production database URLs.
- Application startup no longer auto-creates default users, tables, or curriculum data.
- Explicit administrator bootstrap script accepts credentials through environment variables only.
- RBAC helpers for student, teacher, reviewer, and admin roles.
- Student-ownership and curriculum/standard access checks are present in backend security helpers.
- Persistent `auth_sessions`, `password_reset_tokens`, and `auth_rate_limits` models plus a reversible, unexecuted authentication migration.
- Persistent token-digest primitives for refresh sessions, reset tokens, session-family revocation, and rate limits.
- Registration creates only a server-assigned `STUDENT` role.
- Login creates a refresh session; refresh uses an HttpOnly cookie and rotates the persistent token record; logout and logout-all revoke refresh sessions.
- Password-reset tokens now use persistent digest-only records and reset revokes refresh sessions.
- CSRF double-submit cookie/header validation and origin allowlist checks protect refresh/logout routes.
- Session listing and owner-scoped individual session revocation endpoints exist.
- Frontend removed embedded offline credentials/password login fallback, attaches credentials and CSRF headers to auth requests, and fails closed on login failure.

### Frontend

- TypeScript/Vite application with student, teacher, reviewer, curriculum, adaptive-practice, PYQ, assessment, and authentication views.
- Role-aware hash-router guards and a Class-10 restriction for competitive PYQ navigation.
- Timed competitive assessment UI scaffolding, numerical/multiple-choice flows, student progress/revision/gamification interfaces, and reviewer screens.
- Frontend unit tests use deterministic mocked fetches and no longer make real relative API calls during rendering tests.

## Verification actually executed

| Check | Latest observed result |
|---|---|
| Database isolation suite | 11 passed |
| Earlier focused security/reviewer/isolation suite | 33 passed |
| Frontend unit tests | 37 passed |
| Frontend typecheck | Passed |
| Frontend production build | Passed |
| Full backend collection | 453 tests discovered, 9 collection errors |
| Canonical `edunavika.db` | SHA-256 unchanged: `B02122C54FB680C7B7AA7F5141543BBCB57B258EAB9FB64D333A15322E5D687C` |

No migration was executed against the canonical database. No commit or push was made during these phases.

## Current blockers

### P0: Authentication security verification

- CSRF tokens are not yet bound to an individual persistent refresh session. The current double-submit approach is insufficient against cookie-injection/substitution scenarios.
- Refresh-token replay, session-family revocation, and concurrent refresh behavior have not passed API-level adversarial tests.
- Password-reset consumption and password/session invalidation need one atomic transaction and concurrent-consumption evidence.
- Persistent rate-limit concurrency, expiry, restart, and multi-instance behavior are unverified.
- Email delivery abstraction is not implemented. The API does not expose reset tokens, but delivery cannot yet be claimed.
- Access JWTs remain valid until expiry after logout, logout-all, or password reset. Refresh sessions are revoked immediately; immediate access-token revocation is not implemented.

### P0: Test environment reliability

- Active Python environment cannot import `pymupdf` or `faiss`, despite declarations in `requirements.txt`.
- Full backend collection has nine errors: PyMuPDF imports, FAISS imports, and one obsolete security test that imports removed in-memory auth globals.
- The obsolete test must be replaced with API tests for the persistent architecture, not repaired by restoring insecure global state.

### P1: Student product readiness

- Complete JEE/NEET-first navigation and remove or isolate irrelevant legacy school flows.
- Validate real assessment timer, autosave, scoring, question eligibility, answers, diagrams, explanations, and results end to end.
- Establish a complete question-corpus inventory with source checksum, paper/session/booklet identity, official key, topic mapping, rights state, diagrams, and serving eligibility.
- Complete visual QA and legal/publication review before serving source question content.

### P1: Learning intelligence validity

- The five-round assessment protocol is not verified as an implemented end-to-end workflow.
- Learning-rate and forgetting-risk code/data contracts exist, but no longitudinal labelled dataset, calibrated model, or temporal validation supports scientific prediction claims.

## Recommended next milestones

### Milestone A: Finish authentication safely

1. Add a reversible migration with a CSRF digest and expiry bound to `AuthSession`.
2. Replace unsigned double-submit equality with session-bound CSRF verification.
3. Make reset-token consumption, password update, and session revocation transactional.
4. Add email provider interface, development adapter, production configuration boundary, templates, and failure handling.
5. Add API-level tests for registration, login, CSRF, refresh rotation/replay, concurrent refresh, logout, ownership, reset replay/expiry/concurrency, and persistent rate-limit concurrency.
6. Add frontend single-flight refresh handling and CSRF-aware session restoration.

### Milestone B: Restore reproducible backend verification

1. Pin and install CPU-compatible PyMuPDF and FAISS dependencies for the active Python version.
2. Replace the obsolete legacy auth test import with persistent-auth API tests.
3. Run backend collection and the complete test suite on a disposable database.
4. Record exact commands, environment, pass/fail/skip counts, and failures.

### Milestone C: Content and assessment release gate

1. Build a per-paper/corpus inventory and official-key reconciliation register.
2. Complete diagram extraction, human review, rights review, and publication permission gates.
3. Report eligible question counts by exam, subject, chapter, and type; never use duplicates to meet the 20-question target.
4. Validate assessment and scoring behavior against official exam policies.

### Milestone D: JEE/NEET student experience

1. Complete competitive-exam onboarding and profile eligibility.
2. Deliver a coherent dashboard, chapter practice, timed exam, result, explanation, and revision journey.
3. Add responsive/accessibility validation and browser-level integration tests.

### Milestone E: Evidence-based learning intelligence

1. Implement the five-round protocol with comparable timestamped observations.
2. Define targets and collect real longitudinal data.
3. Build interpretable baselines, temporal/student-disjoint validation, and calibration reports before exposing predictive probabilities.

## Current release verdict

**BLOCKED.** EduNavika has valuable engineering foundations, but the authentication lifecycle is not yet independently security-verified, the full backend suite does not collect in the active environment, content-rights/quality gates are incomplete, and the competitive learner experience requires end-to-end validation.

## Related phase reports

Detailed historical evidence is retained in `docs/PHASE_0_*`, `docs/PHASE_1_*`, and `docs/PHASE_1_3A_*` through `docs/PHASE_1_3H_*`.
