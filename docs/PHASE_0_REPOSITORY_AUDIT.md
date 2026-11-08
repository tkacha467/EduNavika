# Phase 0 Repository Audit

Audited 8 November 2026. This is an evidence-based snapshot of the local working tree, not a release approval.

## Repository state

| Item | Observed state |
|---|---|
| Branch | `master` |
| HEAD | `43be1889bf557975f0edca2a975d956e59eafad1` |
| Remote | `origin` points to `https://github.com/tkacha467/EduNavika.git` |
| Synchronization | `master...origin/master`; neither ahead nor behind at audit time |
| Worktree | Dirty: 19 tracked modifications and 10 untracked files before this audit's reports |
| Staged files | None reported by `git status --short` |
| Persistent DB | `edunavika.db` SHA-256 was unchanged before and after test execution |

The existing uncommitted changes include authentication, authorization, curriculum, reviewer, router, and frontend auth files. They were not overwritten, committed, reset, rebased, or synchronized.

## Architecture observed

- FastAPI application: `backend/app/main.py`, versioned router: `backend/app/api/v1/router.py`.
- SQLAlchemy models are organized across core, curriculum, assessment, adaptive, and competitive model modules; Alembic contains the initial schema plus curriculum, competitive, and constraint migrations.
- The frontend is a TypeScript/Vite single-page hash router under `frontend/src/routes/router.ts` with student, teacher, reviewer, interactive, and auth views.
- Competitive ingestion, question eligibility, answer-key reconciliation, diagram handling, curriculum mapping, adaptive practice, and prediction-data contracts are present in source.

## Material audit findings

| Severity | Finding | Code evidence |
|---|---|---|
| Critical | Application startup can create tables, seed a default student and teacher, and sync questions when not `testing`. Default credentials are embedded in source. | `backend/app/main.py:on_startup`; `backend/app/api/v1/endpoints/auth.py:ensure_default_accounts` |
| Critical | Default JWT secret is an insecure, source-controlled fallback. A deployed environment missing `SECRET_KEY` would use it. | `backend/app/core/config.py:Settings.SECRET_KEY` |
| High | Full backend test collection is blocked because the active virtual environment lacks PyMuPDF and FAISS despite both appearing in `requirements.txt`. | `competitive_paper_parser.py:import pymupdf`; `faiss_store.py:import faiss` |
| High | Production-ingestion test reads a hard-coded external path, `D:\\EduSens\\edunavika.db`, and fails because it expects zero question rows. This is non-portable and invalidates a clean-suite claim. | `backend/tests/test_production_ingestion_gate.py:test_8_persistent_database_counts_remain_zero` |
| Medium | The default development database is a relative SQLite path, while startup mutation occurs automatically outside test mode. | `backend/app/core/config.py`; `backend/app/main.py` |
| Medium | Password-reset tokens and rate-limit counters are process-local memory. They do not survive restart or coordinate across workers. | `backend/app/api/v1/endpoints/auth.py:RESET_TOKENS`, `_FAILED_LOGINS`, `_FORGOT_REQUESTS` |
| Medium | The frontend retains a broad legacy school-oriented route and navigation surface alongside competitive-exam flows. | `frontend/src/routes/router.ts:ROUTES`; `frontend/src/features/student/StudentViews.ts` |

## Audit constraints

No migration, seed command, ingestion command, commit, push, reset, rebase, or operation against the persistent database was executed. Tests used the repository's temporary SQLite fixture and its persistent-database guard.
