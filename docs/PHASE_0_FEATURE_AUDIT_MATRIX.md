# Phase 0 Feature Audit Matrix

Statuses reflect source inspection and current test evidence, not historical claims.

| Feature | Backend | Frontend | Tests | Status | Remaining Work |
|---|---|---|---|---|---|
| Authentication and bearer JWT | Implemented | Login and route gating | Targeted auth/security suite collected | IMPLEMENTED BUT UNVERIFIED | Remove default credentials/secret; add logout and revocation; run full suite. |
| RBAC and ownership | Role/ownership helpers present | Student/teacher route redirects present | Targeted tests passed except external-path test | IMPLEMENTED BUT UNVERIFIED | Complete endpoint inventory and integration coverage. |
| JEE Main/JEE Advanced/NEET taxonomy | Exams and subject mappings seeded | Exam selector and PYQ views | Exam-selector unit tests pass | PARTIALLY IMPLEMENTED | Verify enrollment flow and live API behavior. |
| PYQ ingestion | Parser and ingestion service present | PYQ catalogue exists | Blocked at collection by missing PyMuPDF | BLOCKED BY DATA | Restore dependencies; ingest only traced, rights-approved corpus. |
| Answer-key reconciliation | Deterministic service and schema present | Reviewer UI present | Dedicated targeted tests pass | IMPLEMENTED BUT UNVERIFIED | Re-run full suite; reconcile all served papers to primary keys. |
| Diagram assets | Vector extractor and asset fields present | Asset URLs rendered in question flows | Blocked at collection by missing PyMuPDF | PARTIALLY IMPLEMENTED | Complete visual QA and rights review. |
| Chapter/subject/mock assessments | Competitive assessment service present | Exam runner includes navigation and timer | Partial tests; full competitive collection blocked | IMPLEMENTED BUT UNVERIFIED | Verify actual eligible-count behavior, autosave and server authority. |
| Exam scoring variants | Policies/fields exist | UI represents SCQ, multi-correct and numerical flows | Not fully executable | PARTIALLY IMPLEMENTED | Validate each exam policy against official rules and fixtures. |
| Solutions/explanations | Fields and explanation services exist | Student views render feedback | No corpus-completeness evidence | PARTIALLY IMPLEMENTED | Review solution provenance and coverage. |
| Five-round assessment | Event/attempt models exist | No verified five-round product flow | No end-to-end evidence | NOT IMPLEMENTED | Specify and implement comparable five-round protocol. |
| Learning rate/forgetting prediction | Data contracts, validators and heuristics exist | UI makes forgetting-risk claims | Validators explicitly caution against invalid claims | IMPLEMENTED BUT UNVERIFIED | Gather longitudinal labelled data; calibrate and validate temporally. |
| Personalized revision | Revision services and endpoints exist | Revision view exists | Targeted frontend logs API failures in Node test environment | IMPLEMENTED BUT UNVERIFIED | Validate outcomes and graceful live-API failures. |
| Gamification | Service/domain code exists | Missions, achievements, etc. exist | No production-grade evidence | PARTIALLY IMPLEMENTED | Define anti-gaming and measure learning impact. |
| Teacher/reviewer operations | Reviewer verification routes/services exist | Reviewer/teacher views exist | Reviewer targeted tests pass | IMPLEMENTED BUT UNVERIFIED | Operationalize reviewer lifecycle and access governance. |
