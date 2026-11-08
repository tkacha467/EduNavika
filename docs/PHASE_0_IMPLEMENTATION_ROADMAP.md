# Phase 0 Implementation Roadmap

## Milestone 1: Secure the deployment baseline

1. Remove `ensure_default_accounts` from application startup and rotate the exposed credentials.
2. Require `SECRET_KEY`, database URL, CORS origins, and mail/reset configuration through production environment validation.
3. Implement logout/token invalidation and invalidate active sessions on password change/reset.
4. Replace in-memory reset/rate-limit state with durable TTL-backed infrastructure.

Primary files: `backend/app/core/config.py`, `backend/app/main.py`, `backend/app/core/security.py`, `backend/app/api/v1/endpoints/auth.py`.

## Milestone 2: Restore a trustworthy verification pipeline

1. Recreate the virtual environment from locked, platform-compatible dependencies, including PyMuPDF and FAISS.
2. Repair test imports and the `D:\\EduSens` hard-coded database assertion.
3. Run the complete backend suite against disposable databases and record exact results.
4. Make frontend tests mock API boundaries or add an integration environment that proves the real contract.

Primary files: `requirements.txt`, `backend/tests/test_production_ingestion_gate.py`, `backend/tests/test_competitive_platform.py`, `frontend/src/tests/*`.

## Milestone 3: Establish a releasable question corpus

1. Generate a checksum-based inventory for every paper, key, diagram, and derived asset.
2. Enforce provenance, official answer-key matching, content/diagram review, and legal publication approval before serving.
3. Produce chapter-by-chapter eligible-question coverage; never use raw row counts or duplicates to reach 20.

Primary files: `backend/app/ingestion/competitive_paper_parser.py`, `backend/app/services/question_ingestion_service.py`, `backend/app/services/question_verification_service.py`, `backend/app/services/competitive_assessment_service.py`.

## Milestone 4: Complete the JEE/NEET student workflow

1. Audit each registered route and remove or isolate irrelevant Standard-10 navigation for competitive students.
2. Validate timer, navigation, response persistence, autosubmission, policies, result calculation and explanations with browser/API integration tests.
3. Treat client-side UI messaging as non-authoritative; enforce eligibility and policy server-side.

Primary files: `frontend/src/routes/router.ts`, `frontend/src/features/student/StudentViews.ts`, `frontend/src/services/competitiveService.ts`, `backend/app/api/v1/endpoints/competitive.py`.

## Milestone 5: Make learning intelligence scientifically defensible

1. Implement the five-round protocol with timestamped, comparable student-topic observations.
2. Define targets before training; maintain temporal and student-disjoint splits.
3. Start with interpretable baselines and calibration reporting; do not ship probability claims before validation.

Primary files: `backend/app/domain/prediction/*`, `backend/app/services/event_recorder.py`, `backend/app/services/knowledge_model.py`, `backend/app/services/revision_planner.py`.
