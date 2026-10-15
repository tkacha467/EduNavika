# EduNavika — Milestone 4: Phase C.1 Isolation Safety Review

**Document Version:** 1.0.0  
**Date:** October 15, 2026  
**Auditor:** Senior Backend & Data Architect / QA Engineer  
**Status:** Audit Completed & Verified — Awaiting User Approval for Phase D  
**Target Database:** `D:\EduNavika\edunavika.db`  
**Alembic Schema Revision:** `f1e2d3c4b5a6`  

---

## 1. Executive Summary

Phase C.1 is a formal safety audit and targeted verification of the test-isolation architecture established in Phase C. This phase does not introduce new product features, curriculum seeds, or exam papers. Its sole purpose is to independently audit code diffs, verify path normalization and isolation boundaries under adversarial inputs, validate production startup behavior, execute regression tests, and confirm that the persistent development database (`D:\EduNavika\edunavika.db`) has maintained byte-for-byte immutability.

### Key Verification Highlights
1. **Zero Database Drift:** The persistent database SHA-256 hash remains byte-for-byte identical to the pre-Phase C baseline (`84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174`), with zero foreign key violations, clean integrity (`ok`), and identical row counts across all 27 tables.
2. **Exhaustive Path Normalization:** The SQLAlchemy class-level connect guard intercepts all URL formats targeting `edunavika.db`, including absolute Windows paths, lowercase drive letters, forward slashes, relative paths (`./edunavika.db`, `../EduNavika/edunavika.db`), and SQLite URI parameters (`file:edunavika.db?uri=true`).
3. **Honest Boundary Documentation:** The isolation boundaries and bypass vectors have been mapped. Specifically, while SQLAlchemy connections are 100% intercepted by the connect listener, direct standard-library `sqlite3.connect` calls bypass SQLAlchemy engine hooks; these are caught post-hoc by the session invariant SHA-256/row-count assertion.
4. **Idempotency Validated:** Targeted tests confirmed that `sync_canonical_questions_to_db` creates exactly one Standard 10 record on an empty database, reuses existing Standard 10 records without duplicating them, and returns 0 insertions on repeated synchronization.
5. **No Production Startup Interference:** Application startup logic in `backend/app/main.py` is guarded strictly for `ENV == "testing"`. Production and development modes execute schema creation, account provisioning, and canonical sync normally.

---

## 2. Comprehensive Code Diff Audit

### 2.1 `backend/tests/conftest.py`
The modifications to `backend/tests/conftest.py` transformed the test suite from an unsafe configuration (which could connect to `D:\EduNavika\edunavika.db` via default settings) to a sandboxed architecture:
- **Environment Pinning:** At module top, sets `os.environ["ENV"] = "testing"` and creates a dedicated temporary database file (`edunavika_test_<uuid>.db`) via `tempfile.NamedTemporaryFile`. Sets `os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"`.
- **Class-Level Hard Guard:** Installs an event listener on `Engine` (`@event.listens_for(Engine, "connect")`) that executes `PRAGMA database_list` on every connection opened by any SQLAlchemy engine. If the resolved path matches `PERSISTENT_DB_PATH` or matches `*edunavika.db` without `test` in the name, it immediately raises a `RuntimeError` with `DATABASE ISOLATION VIOLATION`.
- **Central Symbol Rebinding:** Rebinds `settings.DATABASE_URL`, `app_db.engine`, `app_db.SessionLocal`, `app_main.engine`, and `app_main.SessionLocal` to point to `test_engine` and `TestingSessionLocal`.
- **FastAPI Dependency Override:** Overrides `get_db` on `app.dependency_overrides` so all route handlers resolve to `TestingSessionLocal`.
- **Automated Lifecycle & Cleanup:** 
  - `atexit.register(_cleanup_test_db)` disposes `test_engine` and deletes the temporary SQLite `.db`, `-wal`, and `-shm` files upon process exit.
  - Fixture `db_session` cleans up rows via `conn.execute(table.delete())` across `reversed(Base.metadata.sorted_tables)`. This avoids dropping tables between tests, preventing SQLite schema cache churn.
  - Fixture `persistent_database_guard_session` computes SHA-256 and row counts before and after the pytest session, asserting zero modification.

### 2.2 `backend/app/main.py`
The startup handler was modified with a single targeted guard:
```python
@app.on_event("startup")
def on_startup():
    if settings.ENV == "testing" or os.getenv("ENV") == "testing":
        return
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_accounts(db)
        try:
            from backend.app.services.curriculum_question_bank import sync_canonical_questions_to_db
            sync_canonical_questions_to_db(db)
        except Exception as e:
            logger.warning(f"Failed to auto-sync canonical questions on startup: {e}")
```
- **Audit Findings:** 
  - In development (`ENV="development"`) or production (`ENV="production"`), `on_startup` executes completely unmodified.
  - In test mode (`ENV="testing"`), automated execution of `Base.metadata.create_all`, `ensure_default_accounts`, and `sync_canonical_questions_to_db` is bypassed. This prevents race conditions and ensures tests have explicit, deterministic fixture setups rather than hidden startup mutations.

### 2.3 `backend/app/services/curriculum_question_bank.py`
Two targeted bug fixes were audited:
1. **Missing Variable Bug in `sync_canonical_questions_to_db`:**
   - *Previous code:* `source_content_id=lc.id if lc else None` where `lc` was undefined in the question loop, raising `NameError`.
   - *Corrected code:* `source_content_id=q.get("source_chunk_id")`.
   - *Audit verification:* In the question dictionary, `q.get("source_chunk_id")` directly matches the ID of the `LearningContent` row inserted during step 2 (`new_lc = LearningContent(id=chunk_id, ...)`). This restores exact curriculum provenance without variable scope errors.
2. **Standard 10 Null Constraint Violation & Idempotency:**
   - *Previous code:* `standard_id=s10.id if s10 else None`. On an empty database where Standard 10 did not exist, `s10` evaluated to `None`, triggering an `IntegrityError` (`NOT NULL constraint failed: subjects.standard_id`).
   - *Corrected code:* Checks for `Standard.grade_number == 10`. If not found, creates `Standard(grade_number=10, name="Standard 10", description="GSEB Standard 10")`, flushes to the session, and sets `standard_id=s10.id`.
   - *Audit verification:* Flushed `Standard` is visible to subsequent queries in the same transaction, preventing duplicate standard creation.

### 2.4 `backend/tests/test_database_isolation.py`
A new 9-test regression suite was created to continuously enforce and verify all isolation invariants:
- `test_1_client_uses_isolated_test_database`: Verifies FastAPI TestClient connects to isolated temporary DB.
- `test_2_session_factory_bound_to_isolated_database`: Verifies `TestingSessionLocal` PRAGMA database_list points to temp DB.
- `test_3_representative_write_does_not_reach_persistent_database`: Inserts canary record through test client; queries persistent DB via raw read-only SQLite to verify canary absence.
- `test_4_direct_imports_of_session_factory_cannot_bypass_isolation`: Imports `SessionLocal` directly from `backend.app.core.database`, writes canary, verifies persistent DB is untouched.
- `test_5_hard_guard_blocks_persistent_database_connections`: Directly creates SQLAlchemy engine pointing to `D:\EduNavika\edunavika.db` and asserts `DATABASE ISOLATION VIOLATION` is raised.
- `test_6_test_setup_and_teardown_lifecycle`: Verifies temporary DB creation, session lifecycle, and clean disposal.
- `test_7_persistent_database_remains_completely_unmodified`: Asserts persistent database SHA-256, schema revision `f1e2d3c4b5a6`, and 27 table row counts remain intact.
- `test_8_guard_blocks_all_path_variants_and_uris`: Tests 8 distinct URL variants (relative, absolute, URI, casing) against the guard.
- `test_9_canonical_question_sync_idempotency_and_no_duplicate_standards`: Validates that synchronization is idempotent and does not produce duplicate standards.

### 2.5 Modified Test Fixtures
Three test files were updated to make their schema initialization and question-bank dependencies explicit:
- `backend/tests/test_audit_repairs.py`: Added `Base.metadata.create_all(bind=db.get_bind())` and `sync_canonical_questions_to_db(db)` in `audit_student` fixture.
- `backend/tests/test_curriculum_coverage_and_runtime.py`: Added explicit table creation and canonical sync in `db_session` fixture.
- `backend/tests/test_misconception_remediation.py`: Added explicit table creation and canonical sync in `remediation_student` fixture.
- *Audit verification:* All three files now run deterministically under isolation without relying on implicit global state.

### 2.6 `scripts/audit_persistent_db_state.py`
Audits the persistent database without modifying it. Reads raw binary for SHA-256 hash, runs `PRAGMA integrity_check`, `PRAGMA foreign_key_check`, queries `alembic_version`, and enumerates row counts for all non-system SQLite tables.

---

## 3. Rigorous Test-Isolation Verification

### 3.1 Path Normalization and URL Variant Analysis
The persistent database guard uses SQLite's internal `PRAGMA database_list` coupled with `os.path.realpath(db_file).lower()`.

We tested 8 distinct connection path variants against this guard:
| URL Pattern Tested | Resolved File from SQLite | Guard Behavior | Status |
| :--- | :--- | :--- | :--- |
| `sqlite:///D:/EduNavika/edunavika.db` | `D:\EduNavika\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///d:/edunavika/edunavika.db` | `d:\edunavika\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///D:\EduNavika\edunavika.db` | `D:\EduNavika\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///edunavika.db` (relative from D:\EduSens) | `D:\EduSens\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///./edunavika.db` | `D:\EduSens\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///../EduNavika/edunavika.db` | `D:\EduNavika\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///file:edunavika.db?uri=true` | `D:\EduSens\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |
| `sqlite:///file:///D:/EduNavika/edunavika.db?uri=true` | `D:\EduNavika\edunavika.db` | Raised `RuntimeError: DATABASE ISOLATION VIOLATION` | BLOCKED |

**Why this is airtight for SQLite in SQLAlchemy:** SQLite normalizes relative paths and URI parameters into canonical OS filesystem paths upon file open. When `PRAGMA database_list` is executed on the raw DBAPI connection, column 2 contains the resolved path. Furthermore, because `D:\EduSens` is an NTFS junction to `D:\EduNavika`, `os.path.realpath` resolves both junction paths to the canonical target, ensuring that junction-aliased access is intercepted.

### 3.2 Guard Installation Timing
- In `backend/tests/conftest.py`, the listener is registered at module load time on the class `sqlalchemy.engine.Engine`:
  ```python
  @event.listens_for(Engine, "connect")
  def guard_against_persistent_db(dbapi_connection, connection_record):
      ...
  ```
- Because pytest executes `conftest.py` before loading any test modules, this listener is installed before any application database engine can open a connection. Any `Engine` instantiated anywhere in the process automatically invokes this listener on connection checkout.

### 3.3 Bypass Vector Analysis & Honest Limitation Disclosures
We evaluated every potential bypass vector:

| Potential Bypass Vector | Mechanism | Protection Established | Unresolved Risk / Boundary |
| :--- | :--- | :--- | :--- |
| **Module-level engines (`app_db.engine`, `main.engine`)** | Statically initialized at module load | Rebound to `test_engine` in `conftest.py`; also blocked by class-level `Engine.connect` guard. | None. Both layers prevent access. |
| **Cached / direct import of `SessionLocal`** | `from backend.app.core.database import SessionLocal` | Rebound in `sys.modules["backend.app.core.database"]` to `TestingSessionLocal`. | None. Direct imports resolve to isolated test engine. |
| **FastAPI background tasks** | Tasks spawned via `BackgroundTasks` | Run in the same process/threads and resolve dependencies via `app.dependency_overrides[get_db]`. | None. Tasks inherit rebound session factory. |
| **Raw `sqlite3.connect` calls** | Direct Python standard library `sqlite3.connect("D:/EduNavika/edunavika.db")` | Not intercepted by SQLAlchemy `Engine.connect` event. Only 1 occurrence exists in `test_curriculum_assessment.py:287` (read-only query). | **Disclosed Limitation:** Direct `sqlite3.connect` calls bypass SQLAlchemy engine listeners. Protection is provided post-hoc by the session invariant fixture asserting byte-for-byte SHA-256 identity. |
| **Subprocesses spawned by test suite** | E.g. `subprocess.run(["python", ...])` | Process inherits `DATABASE_URL` and `ENV=testing` from `os.environ`. | **Disclosed Limitation:** If a rogue test spawns a subprocess that explicitly hardcodes `D:\EduNavika\edunavika.db` and ignores environment variables, in-process guards do not execute in that child process. (No such tests currently exist). |

### 3.4 Test Cleanup Behavior
- Fixture `db_session` executes `conn.execute(table.delete())` for all tables in `reversed(Base.metadata.sorted_tables)`.
- Cleanup runs only against `test_engine` (the temporary database).
- Exceptions during cleanup are caught so that a cleanup issue on a dropped table does not mask the actual test assertion outcome.
- Pytest records test failures prior to running fixture teardown; teardown does not alter test pass/fail status.

### 3.5 Session Invariant Execution Under Interruption
- The session fixture `persistent_database_guard_session` is `scope="session", autouse=True`.
- Pytest guarantees that fixture teardown code after `yield` runs even if individual test functions fail or raise unexpected exceptions.
- In the event of an abnormal process termination (`SIGKILL` or OS kill), the teardown cannot run; however, `atexit.register(_cleanup_test_db)` ensures temporary files are unlinked on standard interpreter termination.

---

## 4. Production Behavior Review

### 4.1 FastAPI Startup Behavior
- In `backend/app/main.py`:
  ```python
  if settings.ENV == "testing" or os.getenv("ENV") == "testing":
      return
  ```
- **Development/Production Impact:** When EduNavika runs under `ENV="development"` or `ENV="production"` (e.g. `uvicorn backend.app.main:app`), this conditional evaluates to `False`. The server creates missing tables via `Base.metadata.create_all(bind=engine)`, calls `ensure_default_accounts(db)`, and runs `sync_canonical_questions_to_db(db)`.
- **Test Mode Impact:** When running under pytest, `os.environ["ENV"] = "testing"` causes `on_startup` to return immediately. This eliminates side-effects during `TestClient(app)` instantiation.

### 4.2 Curriculum Question Bank Idempotency & Standard 10 Logic
We verified that `sync_canonical_questions_to_db(db)` is fully idempotent:
1. **Empty Database:** Creates exactly one `Standard` record with `grade_number=10` and `name="Standard 10"`, creates required subjects/chapters/topics, and syncs 68 canonical questions.
2. **Repeated Synchronization:** Running `sync_canonical_questions_to_db(db)` a second time discovers all existing topics and question IDs; returns `0` new questions and maintains the standard count at `1`.
3. **Pre-Existing Standard 10:** If Standard 10 already exists in the database (e.g. `grade_number=10, name="Class 10 Existing"`), the query `(Standard.grade_number == 10) | (Standard.name.ilike("%10%"))` matches the existing record. No duplicate standard is created.

---

## 5. Test Execution Results

### 5.1 Test Suites Executed

```bash
pytest backend/tests/test_database_isolation.py        backend/tests/test_audit_repairs.py        backend/tests/test_curriculum_coverage_and_runtime.py        backend/tests/test_misconception_remediation.py        backend/tests/test_models.py -v
```
**Results:** **28 Passed**, **1 Failed**, **0 Skipped** (in 2.30s)

```bash
pytest backend/tests/test_curriculum_assessment.py        backend/tests/test_adaptive_practice.py -v
```
**Results:** **33 Passed**, **0 Failed**, **0 Skipped** (in 1.42s)

### 5.2 Breakdown by Test File

| Test File | Total | Passed | Failed | Skipped | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `backend/tests/test_database_isolation.py` | 9 | 9 | 0 | 0 | All 9 isolation, guard, and idempotency tests PASSED. |
| `backend/tests/test_curriculum_coverage_and_runtime.py` | 6 | 6 | 0 | 0 | All curriculum coverage & runtime diagnostic tests PASSED. |
| `backend/tests/test_misconception_remediation.py` | 4 | 4 | 0 | 0 | All remediation flow and atomic retry tests PASSED. |
| `backend/tests/test_models.py` | 4 | 4 | 0 | 0 | User profile, unique email, hierarchy, and FK tests PASSED. |
| `backend/tests/test_curriculum_assessment.py` | 14 | 14 | 0 | 0 | Assessment validation, source text grounding tests PASSED. |
| `backend/tests/test_adaptive_practice.py` | 19 | 19 | 0 | 0 | Full adaptive progression and LLM fallback tests PASSED. |
| `backend/tests/test_audit_repairs.py` | 6 | 5 | 1 | 0 | 5 passed; 1 expected legacy failure preserved. |

### 5.3 Documented Legacy Failure
The single failure in `test_audit_repairs.py` is an acknowledged legacy assertion:
- **Test:** `test_content_diagnostic_endpoint_reports_real_status`
- **Assertion:** `assert d_math["textbook_chunks_count"] > 100` (`assert 20 > 100`)
- **Reason:** In the cleaned test database with canonical GSEB questions, 20 mathematics chunks exist. The legacy test asserts `> 100`.
- **Handling:** Per Phase C instructions, this test failure is preserved and not masked.

---

## 6. Persistent Database Audit & Invariant Verification

We executed `python scripts/audit_persistent_db_state.py` before and after all test runs.

### 6.1 State Comparison
| Metric | Pre-Phase C Baseline | Post-Phase C.1 Safety Audit | Status |
| :--- | :--- | :--- | :--- |
| **Database Path** | `D:\EduNavika\edunavika.db` | `D:\EduNavika\edunavika.db` | Verified |
| **File Size (Bytes)** | 3,981,312 | 3,981,312 | **Byte-for-byte identical** |
| **SHA-256 Checksum** | `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` | `84432e58eb4b67f12da53a914e806b448212948a307a799f7de35b4cf04a2174` | **Byte-for-byte identical** |
| **SQLite Integrity Check** | `[("ok",)]` | `[("ok",)]` | Clean |
| **Foreign Key Check** | `[]` (0 violations) | `[]` (0 violations) | Clean |
| **Alembic Version** | `["f1e2d3c4b5a6"]` | `["f1e2d3c4b5a6"]` | Matches Phase A |
| **Total Non-System Tables** | 27 | 27 | Identical |

### 6.2 Table-by-Table Row Counts
| Table Name | Baseline Row Count | Post-Audit Row Count | Delta |
| :--- | :--- | :--- | :--- |
| `alembic_version` | 1 | 1 | 0 |
| `answers` | 0 | 0 | 0 |
| `assessment_questions` | 0 | 0 | 0 |
| `assessments` | 0 | 0 | 0 |
| `attempts` | 0 | 0 | 0 |
| `chapters` | 288 | 288 | 0 |
| `exam_papers` | 0 | 0 | 0 |
| `exam_subjects` | 18 | 18 | 0 |
| `examinations` | 3 | 3 | 0 |
| `forgetting_signals` | 10 | 10 | 0 |
| `learning_contents` | 573 | 573 | 0 |
| `learning_events` | 776 | 776 | 0 |
| `learning_quests` | 3 | 3 | 0 |
| `mcq_questions` | 80 | 80 | 0 |
| `question_history` | 0 | 0 | 0 |
| `question_options` | 0 | 0 | 0 |
| `question_verification_logs` | 0 | 0 | 0 |
| `questions` | 0 | 0 | 0 |
| `revision_plans` | 21 | 21 | 0 |
| `standards` | 3 | 3 | 0 |
| `student_profiles` | 243 | 243 | 0 |
| `subjects` | 247 | 247 | 0 |
| `teacher_actions` | 0 | 0 | 0 |
| `teacher_profiles` | 0 | 0 | 0 |
| `topic_performances` | 149 | 149 | 0 |
| `topics` | 505 | 505 | 0 |
| `users` | 244 | 244 | 0 |

---

## 7. Unresolved Risks and Phase D Recommendations

### 7.1 Unresolved Risks
1. **Raw `sqlite3.connect` Risk:** If future test authors write tests that open raw `sqlite3.connect("D:/EduNavika/edunavika.db")` rather than using SQLAlchemy engines or session fixtures, the SQLAlchemy class-level connect guard will not block the connection. Any mutation would only be caught post-hoc by the session invariant fixture.
   - *Mitigation recommendation:* Keep `persistent_database_guard_session` permanently active in `conftest.py` so any mutation triggers an immediate failure.
2. **Subprocess Isolation:** Subprocesses running outside pytest that hardcode paths would not be intercepted by in-memory python hooks.
   - *Mitigation recommendation:* Phase D scripts should enforce `DATABASE_URL` resolution and avoid hardcoding paths.

### 7.2 Phase D Readiness Checklist
- [x] Test isolation verified across 9 dedicated isolation tests.
- [x] Persistent development database verified unchanged (SHA-256 matching baseline).
- [x] Standard 10 creation idempotency confirmed with zero duplicate creation.
- [x] Undefined variable bug in `curriculum_question_bank.py` resolved with correct source chunk ID mapping.
- [x] Production startup logic verified untouched.
- [x] All temporary test databases, engines, and connections reliably disposed of without disk leaks.

---

## 8. Conclusion and Sign-Off Request

Phase C.1 has demonstrated that the test-isolation hardening in EduNavika is robust, verifiable, and free of persistent database side-effects. The development database at `D:\EduNavika\edunavika.db` is safe from test suite writes.

Per Phase C.1 boundaries:
- No papers, questions, textbooks, or chapters have been ingested.
- No additional curriculum has been seeded.
- No legacy data has been deleted.
- No git commits or pushes have been made.

We are stopped and awaiting user approval before proceeding to Phase D (Pilot Ingestion).
