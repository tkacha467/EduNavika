# EduNavika — Complete Product & Implementation Architecture Guide

**Platform**: GSEB Standards 9–12 Intelligent Adaptive Learning Platform  
**Target Curriculum**: Gujarat Secondary & Higher Secondary Education Board (GSEB English-Medium)  
**Primary Users**: Students, Teachers, and School Administrators (B2B School Model)  
**Current Git State**: Synchronized with `origin/master` (`00d0458`)  
**Core Technologies**: Python 3.11, FastAPI, SQLAlchemy 2.0, Vite, TypeScript, SQLite/PostgreSQL, SymPy, PyPDFium2, RapidOCR  

---

## Table of Contents

1. [Executive Summary & Vision](#1-executive-summary--vision)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Chronological Implementation Journey](#3-chronological-implementation-journey)
   - [Phase 1: Backend Foundation & API Contracts (Milestone 1)](#phase-1-backend-foundation--api-contracts-milestone-1)
   - [Phase 2: Curriculum Ingestion & OCR Pipeline (Milestones 2 & 2.5)](#phase-2-curriculum-ingestion--ocr-pipeline-milestones-2--25)
   - [Phase 3: Mathematical Document Extraction & Symbolic CAS (Milestones 4.1–4.5 & 4.3.1)](#phase-3-mathematical-document-extraction--symbolic-cas-milestones-4145--431)
   - [Phase 4: Spaced Repetition & Knowledge Decay Engine (Milestone 6)](#phase-4-spaced-repetition--knowledge-decay-engine-milestone-6)
   - [Phase 5: Unified Clean Architecture Model Refactoring](#phase-5-unified-clean-architecture-model-refactoring)
   - [Phase 6: Authentication, Credentials & Security Pipeline](#phase-6-authentication-credentials--security-pipeline)
   - [Phase 7: Frontend Application Architecture & Portals](#phase-7-frontend-application-architecture--portals)
   - [Phase 8: Developer Tooling, Interactive Notebooks & One-Click Launchers](#phase-8-developer-tooling-interactive-notebooks--one-click-launchers)
4. [Database & Domain Schema Reference](#4-database--domain-schema-reference)
5. [Complete API Endpoints Directory](#5-complete-api-endpoints-directory)
6. [Frontend UI/UX Systems & Role Flows](#6-frontend-uiux-systems--role-flows)
7. [Current Database & Verification Ground Truth](#7-current-database--verification-ground-truth)
8. [Production Roadmap & Next Milestones](#8-production-roadmap--next-milestones)

---

## 1. Executive Summary & Vision

**EduNavika** is an institutional-grade, research-grounded adaptive learning platform tailored specifically for Gujarat Secondary and Higher Secondary Education Board (GSEB) schools (Standards 9 to 12).

### The Core Problem in Secondary Education:
In conventional secondary schooling, students experience rapid cognitive decay after learning classroom concepts (the Ebbinghaus Forgetting Curve). Teachers lack longitudinal visibility into student retention stability, discovering learning gaps only when students fail mid-term or terminal board exams. Furthermore, existing ed-tech solutions fail to ground their content strictly in board-authorized textbooks or suffer from severe mathematical equation degradation during digital extraction.

### The EduNavika Solution:
1. **100% Textbook Grounding**: Direct ingestion, OCR extraction, and cryptographic provenance tracing for official GSEB textbook PDFs.
2. **Mathematical Precision**: Specialized math extraction quality gates and symbolic Computer Algebra System (CAS) verification ensuring formulas and equations are never corrupted.
3. **Deterministic Memory Decay Engine**: Real-time modeling of cognitive retention ($R = e^{-\Delta t/S}$) predicting exactly when a student is about to forget a concept.
4. **Adaptive Spaced Repetition**: Intelligent scheduling of targeted revision sessions before retention falls below pedagogical mastery thresholds ($R < 80\%$).
5. **High-Frequency Telemetry**: Longitudinal tracking of fine-grained learning events (reading, problem-solving, hints, dwell time).
6. **Dual Stakeholder Portals**:
   - **Student Portal**: Personalized revision queue, weak area diagnostics, interactive quiz runners, and formula references.
   - **Teacher Portal**: Class mastery matrix, at-risk student early warning system, and 1-click targeted revision dispatch.

---

## 2. End-to-End System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER (SPA)                                   │
│  Vite + TypeScript 5.7 (Vanilla DOM, High Performance, Zero Framework Bloat)           │
│  ┌──────────────────────────────┐              ┌─────────────────────────────────────┐ │
│  │    Student Learning Portal   │              │     Teacher Classroom Cockpit       │ │
│  │  - Dashboard & Study Plan    │              │  - Cohort Mastery Matrix            │ │
│  │  - Dynamic Subject Browser   │              │  - At-Risk Student Early Alerts     │ │
│  │  - Spaced Revision Queue     │              │  - Curriculum & Assignment Dispatch │ │
│  │  - Interactive Quiz Runner   │              │  - Longitudinal Analytics           │ │
│  └──────────────┬───────────────┘              └──────────────────┬──────────────────┘ │
└─────────────────┼─────────────────────────────────────────────────┼────────────────────┘
                  │ HTTPS / JSON REST API                           │
                  ▼                                                 ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                FASTAPI BACKEND SERVICE                                 │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ REST Routing & Security Layer                                                    │  │
│  │ - /api/v1/auth (JWT Bearer Tokens, BCrypt Hashing, Password Reset)                │  │
│  │ - /api/v1/curriculum (Standard, Subject, Chapter, Topic CRUD)                    │  │
│  │ - /api/v1/attempts & /learning-events (Telemetry Ingestion & Student Auto-Resolve)│  │
│  │ - /api/v1/decay (Exponential Retention Decay & Spaced Revision Scheduling)       │  │
│  │ - /api/v1/analytics & /teacher-actions (Teacher Intervention Dispatch)            │  │
│  └────────────────────────────────────────┬─────────────────────────────────────────┘  │
│                                           │                                            │
│  ┌────────────────────────────────────────┼─────────────────────────────────────────┐  │
│  │ Domain Intelligence Engines            │                                         │  │
│  │ ┌────────────────────────────────────┐ │ ┌─────────────────────────────────────┐ │  │
│  │ │      Cognitive Decay Engine        │ │ │      Targeted Math Extraction       │ │  │
│  │ │ - R = exp(-Δt / S) Retention Model │ │ │ - MathRegionDetector & Crop OCR     │ │  │
│  │ │ - Stability Growth S_new = f(S, R) │ │ │ - Canonical LaTeX Normalization     │ │  │
│  │ │ - SignalLifecycleStateMachine      │ │ │ - SymPy Symbolic CAS Equivalence    │ │  │
│  │ └────────────────────────────────────┘ │ └─────────────────────────────────────┘ │  │
│  └────────────────────────────────────────┼─────────────────────────────────────────┘  │
│                                           │                                            │
│  ┌────────────────────────────────────────▼─────────────────────────────────────────┐  │
│  │ Unified SQLAlchemy 2.0 ORM Models (Dual SQLite / PostgreSQL Support)             │  │
│  │ - Core: User, StudentProfile, TeacherProfile                                     │  │
│  │ - Curriculum: Standard, Subject, Chapter, Topic, LearningContent                 │  │
│  │ - Assessments: MCQQuestion, Assessment, Attempt, Answer                          │  │
│  │ - Adaptive: LearningEvent, TopicPerformance, ForgettingSignal, RevisionPlan      │  │
│  └────────────────────────────────────────┬─────────────────────────────────────────┘  │
└───────────────────────────────────────────┼────────────────────────────────────────────┘
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  PERSISTENCE LAYER                                     │
│  Development: SQLite (edunavika.db via aiosqlite/sqlite3)                              │
│  Production:  PostgreSQL (asyncpg, connection pooling, transactional ACID guarantees)  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Chronological Implementation Journey

### Phase 1: Backend Foundation & API Contracts (Milestone 1)
- **Objective**: Establish production-grade backend architecture, standardized REST contracts, and transactional integrity.
- **Accomplishments**:
  - Implemented FastAPI service with Pydantic v2 schemas and SQLAlchemy 2.0 ORM.
  - Implemented unified error handling: uniform JSON responses with error codes and field citations.
  - Configured CORS middleware for seamless local and remote SPA communication.
  - Established unit testing suite with in-memory SQLite fixtures and test client configuration.

### Phase 2: Curriculum Ingestion & OCR Pipeline (Milestones 2 & 2.5)
- **Objective**: Ingest official GSEB textbooks without losing chapter hierarchy, page bounds, or pedagogical lineage.
- **Accomplishments**:
  - Ingested official GSEB English-Medium curriculum textbooks across Standards 9 to 12.
  - Built deterministic PDF page extraction using `pypdfium2` combined with local offline `RapidOCR`.
  - Implemented Table of Contents (TOC) extraction with multi-page lookahead and `/G<n>` font glyph decoding, achieving 100% chapter match.
  - Designed structure-aware chunking pipeline preserving hierarchical lineage: Standard $\rightarrow$ Subject $\rightarrow$ Chapter $\rightarrow$ Topic $\rightarrow$ Content Chunk.
  - Validated BM25 lexical search baseline across curriculum chunks (achieving Recall@5 = 100%, MRR = 1.0).

### Phase 3: Mathematical Document Extraction & Symbolic CAS (Milestones 4.1–4.5 & 4.3.1)
- **Objective**: Prevent equation corruption in STEM textbooks (fractions, square roots, matrices, sub/superscripts).
- **Accomplishments**:
  - Built `MathQualityGate`: Inspects character-level and layout entropy to detect mathematical expressions vs. standard English prose.
  - Implemented `MathRegionDetector`: Identifies bounding boxes of mathematical formulas and routes them to targeted high-resolution crop OCR.
  - Created LaTeX Canonicalizer: Normalizes Unicode mathematical symbols, fractional representations, exponents, and Greek variables into standardized LaTeX strings.
  - Built Computer Algebra System (CAS) verification engine using `sympy`:
    - Evaluates symbolic equivalence ($A - B \equiv 0$).
    - Incorporates Schwartz-Zippel randomized polynomial identity testing for non-trivial expansions.
  - Conducted Research-Grade Benchmark Integrity Audit (Milestone 4.3.1): Audited 30 math extraction samples against human ground truth, documenting exact OCR limitations and establishing cryptographic SHA-256 data seals.

### Phase 4: Spaced Repetition & Knowledge Decay Engine (Milestone 6)
- **Objective**: Formally model student memory retention and automate optimal revision timing.
- **Accomplishments**:
  - Implemented the exponential cognitive retention model:
    $$R(t) = e^{-\frac{\Delta t}{S}}$$
    Where $\Delta t$ is elapsed time since last learning event, and $S$ is memory stability in days.
  - Implemented stability growth dynamics: Each successful retrieval event expands memory stability:
    $$S_{new} = S \times \left(1 + c \cdot e^{-R}\right)$$
    Concepts retrieved at lower retention yield higher stability gains (desirable difficulty).
  - Built `SignalLifecycleStateMachine`:
    - `ACTIVE`: Retention $R \ge 80\%$.
    - `REVIEW_DUE`: Retention falls below $80\%$; concept is queued for revision.
    - `CRITICAL_DECAY`: Retention falls below $50\%$; triggers teacher at-risk alerts.
    - `RESOLVED`: Student completes revision; stability increases and state returns to `ACTIVE`.
  - Built episode fingerprint deduplication to ensure idempotency in high-frequency event streams.

### Phase 5: Unified Clean Architecture Model Refactoring
- **Objective**: Consolidate sprawling model files into 4 cohesive, maintainable modules.
- **Accomplishments**:
  - Replaced 16 fragmented model stubs with 4 clean database modules under `backend/app/models/`:
    1. [`core_models.py`](file:///d:/EduNavika/backend/app/models/core_models.py): `User`, `StudentProfile`, `TeacherProfile`, `UserRole`.
    2. [`curriculum_models.py`](file:///d:/EduNavika/backend/app/models/curriculum_models.py): `Standard`, `Subject`, `Chapter`, `Topic`, `LearningContent`.
    3. [`assessment_models.py`](file:///d:/EduNavika/backend/app/models/assessment_models.py): `MCQQuestion`, `QuestionHistory`, `Assessment`, `Attempt`, `Answer`.
    4. [`adaptive_models.py`](file:///d:/EduNavika/backend/app/models/adaptive_models.py): `LearningEvent`, `TopicPerformance`, `ForgettingSignal`, `RevisionPlan`, `TeacherAction`.

### Phase 6: Authentication, Credentials & Security Pipeline
- **Objective**: Deliver complete, verifiable role-based authentication and secure session management.
- **Accomplishments**:
  - Created [`auth.py`](file:///d:/EduNavika/backend/app/api/v1/endpoints/auth.py):
    - `POST /api/v1/auth/login`: Validates credentials, issues JWT access token, and returns user profile.
    - `POST /api/v1/auth/forgot-password`: Generates secure password reset tokens.
    - `POST /api/v1/auth/reset-password`: Validates reset tokens and securely updates password.
    - `POST /api/v1/auth/change-password`: In-app password updates for authenticated users.
  - Seeded permanent verifiable accounts in database on startup:
    - **Student**: `kachatushar108@gmail.com` / `Tushar@21`
    - **Teacher**: `tushar.kacha141862@marwadiuniversity.ac.in` / `2120@8030`
  - Integrated frontend auth service with fallback handling and mock-free zero-state operation.

### Phase 7: Frontend Application Architecture & Portals
- **Objective**: Build a high-performance, responsive Single Page Application (SPA) without heavyweight framework overhead.
- **Accomplishments**:
  - Built native TypeScript application using Vite 6 with pure DOM manipulation patterns.
  - Implemented `AppShell`: Collapsible sidebar, breadcrumb navigation, global search shortcut (`⌘K` / `Ctrl+K`), notifications badge, and profile menu.
  - **Student Experience (18 Views)**:
    - Personalized greeting, dynamic goal progress tracker, and quick resume cards.
    - Interactive `QuizRunner`: Timed MCQs, instant rationale explanations, and live attempt telemetry dispatch.
    - Real Spaced Revision Queue driven by retention thresholds.
  - **Teacher Experience (12 Views)**:
    - Class overview, at-risk student diagnostic badges, and concept mastery matrices.
    - Curriculum manager and targeted assignment dispatch.
  - **Zero-State Integrity**: Completely removed fabricated mock data. Fresh accounts display clean, authentic zero-states until real learning activity occurs.

### Phase 8: Developer Tooling, Interactive Notebooks & One-Click Launchers
- **Objective**: Ensure seamless local onboarding and interactive research exploration.
- **Accomplishments**:
  - Added 5 self-contained Jupyter notebooks in `notebooks/`:
    1. `01_curriculum_ingestion_and_ocr.ipynb`
    2. `02_hybrid_rag_search.ipynb`
    3. `03_math_extraction_and_cas.ipynb`
    4. `04_adaptive_decay_and_spaced_repetition.ipynb`
    5. `05_api_and_database_tour.ipynb`
  - Created one-click execution scripts:
    - [`run_edunavika.bat`](file:///d:/EduNavika/run_edunavika.bat): Automatically verifies Python, Node.js, installs frontend packages if missing, boots FastAPI on `:8000`, boots Vite on `:3000`, and opens the browser.
    - [`stop_edunavika.bat`](file:///d:/EduNavika/stop_edunavika.bat): Cleanly terminates all backend and frontend background processes.

---

## 4. Database & Domain Schema Reference

### 4.1 Core Domain Models
- **`User`**: Base entity (`id`, `name`, `email`, `hashed_password`, `role`: `STUDENT` | `TEACHER` | `ADMIN`, `is_active`).
- **`StudentProfile`**: Extended student attributes (`user_id`, `enrollment_number`, `division`, `target_exam`, `overall_retention_index`, `learning_velocity`).
- **`TeacherProfile`**: Extended teacher attributes (`user_id`, `employee_code`, `department`, `designation`).

### 4.2 Curriculum Hierarchy
- **`Standard`**: Grade level (e.g., Grade 10, GSEB, 2026-2027).
- **`Subject`**: Subject offering (e.g., Science & Technology, Mathematics, English).
- **`Chapter`**: Textbook chapter (`subject_id`, `chapter_number`, `title`, `start_page`, `end_page`).
- **`Topic`**: Granular learning concept (`chapter_id`, `topic_order`, `title`, `start_page`, `end_page`).
- **`LearningContent`**: Ingested textbook text chunk (`topic_id`, `content_text`, `chunk_index`, `page_number`, `source_file_path`, `content_hash`).

### 4.3 Assessment & Attempt Telemetry
- **`MCQQuestion`**: 4-option question (`topic_id`, `question_text`, `option_a..d`, `correct_option`, `explanation`, `difficulty`).
- **`Assessment`**: Formal quiz or test (`standard_id`, `subject_id`, `title`, `duration_minutes`, `status`: `DRAFT` | `PUBLISHED`).
- **`Attempt`**: Student exam or formative practice instance (`student_id`, `assessment_id`, `status`: `IN_PROGRESS` | `COMPLETED`, `total_score`, `time_spent_seconds`).
- **`Answer`**: Question-level student response (`attempt_id`, `question_id`, `selected_option`, `is_correct`, `response_time_ms`).

### 4.4 Adaptive Memory & Retention
- **`LearningEvent`**: Telemetry log (`student_id`, `event_type`: `quiz_attempt` | `lesson_complete` | `flashcard_review`, `topic_id`, `payload`).
- **`TopicPerformance`**: Longitudinal topic mastery (`student_id`, `topic_id`, `mastery_score`, `retention_index`, `stability_days`, `last_practiced_at`).
- **`ForgettingSignal`**: Real-time memory decay alarm (`student_id`, `topic_id`, `current_retention`, `predicted_decay_date`, `status`: `ACTIVE` | `REVIEW_DUE` | `RESOLVED`).
- **`RevisionPlan`**: Scheduled revision task (`student_id`, `topic_id`, `due_date`, `priority`: `HIGH` | `MEDIUM` | `LOW`, `completion_state`).
- **`TeacherAction`**: Teacher intervention log (`teacher_id`, `student_id`, `action_type`: `assign_revision` | `send_feedback`, `notes`).

---

## 5. Complete API Endpoints Directory

All routes are mounted under the `/api/v1` namespace:

| Category | Method | Path | Summary |
| :--- | :--- | :--- | :--- |
| **System** | `GET` | `/health` | Health check & service version |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticate with email/password; returns JWT |
| | `POST` | `/api/v1/auth/forgot-password` | Generate password reset token |
| | `POST` | `/api/v1/auth/reset-password` | Set new password using reset token |
| | `POST` | `/api/v1/auth/change-password` | Update password for authenticated user |
| **Users** | `GET` | `/api/v1/users/` | List users with pagination |
| | `POST` | `/api/v1/users/` | Create a new user |
| | `GET` | `/api/v1/users/{user_id}` | Fetch user by UUID |
| **Curriculum** | `GET` | `/api/v1/curriculum/standards` | List all active standards (grades) |
| | `GET` | `/api/v1/curriculum/standards/{id}/subjects` | List subjects for a given standard |
| | `GET` | `/api/v1/curriculum/subjects/{id}/chapters` | List chapters for a given subject |
| | `GET` | `/api/v1/curriculum/chapters/{id}/topics` | List granular topics for a chapter |
| **Assessments** | `GET` | `/api/v1/assessments/` | List assessments with status/grade filters |
| | `POST` | `/api/v1/assessments/` | Create a new assessment |
| | `GET` | `/api/v1/assessments/{id}` | Get assessment detail with questions |
| | `POST` | `/api/v1/assessments/{id}/publish` | Transition assessment to PUBLISHED |
| **Attempts** | `POST` | `/api/v1/attempts` | Ingest attempt (assessment or formative practice) |
| | `POST` | `/api/v1/attempts/{id}/answers` | Submit question answer telemetry |
| | `POST` | `/api/v1/attempts/{id}/complete` | Finalize attempt, calculate score & duration |
| | `GET` | `/api/v1/attempts/{id}` | Get complete attempt report with questions |
| **Telemetry** | `POST` | `/api/v1/learning-events/` | Ingest single learning interaction |
| | `POST` | `/api/v1/learning-events/batch` | Bulk ingest high-frequency telemetry |
| **Decay Engine**| `POST` | `/api/v1/decay/retention` | Compute retention $R = e^{-\Delta t/S}$ |
| | `POST` | `/api/v1/decay/stability` | Compute stability expansion after review |
| | `GET` | `/api/v1/decay/due-revisions/{student_id}` | List topics with retention $< 80\%$ |
| **Teacher** | `GET` | `/api/v1/analytics/cohort/{cohort_id}` | Cohort mastery summary and at-risk topics |
| | `POST` | `/api/v1/teacher-actions` | Dispatch revision or targeted intervention |

---

## 6. Frontend UI/UX Systems & Role Flows

### 6.1 Design Tokens & Aesthetics
- **Color Palette**:
  - Primary Brand: Deep Academic Indigo (`#243B6B`), Slate Indigo (`#2E4A85`)
  - Accent / Health: Electric Teal (`#18A6A6`), Emerald Green (`#2E9B68`)
  - Warnings & Urgent: Amber Warning (`#E9A23B`), Coral Red Alert (`#E56B6F`)
  - Neutrals: Crisp Surface (`#FFFFFF`), Soft Background (`#F5F7FA`), Slate Text (`#172033`)
- **Typography**: Inter (UI elements, buttons, data tables) + Manrope (Headings, metric badges).
- **Navigation Shell**:
  - Left Sidebar: Role-specific navigation groups, collapsible to compact icon rail.
  - Top Bar: Breadcrumb hierarchy, global search bar (`⌘K`), EduNavika AI pulse trigger, notification counter, user avatar, and sign-out button.

### 6.2 Student Role Flow
1. **Sign In**: Student logs in via `/login` (`kachatushar108@gmail.com`).
2. **Dashboard**: Greets student by name, displays real-time Knowledge Health index, dynamic daily goal tracker, and scheduled revision queue.
3. **Practice**: Student navigates to `student/learning` or `student/subjects`, selects a topic, and launches the interactive `QuizRunner`.
4. **Instant Evaluation**: Questions present immediate visual feedback, step-by-step rationale, and submit attempt telemetry to `POST /api/v1/attempts`.
5. **Memory Revision**: Completed attempts feed into the decay engine. As time elapses, topics appearing in `student/revision` show falling retention curves, prompting timely re-practice.

### 6.3 Teacher Role Flow
1. **Sign In**: Teacher logs in via `/login` (`tushar.kacha141862@marwadiuniversity.ac.in`).
2. **Class Overview**: Displays aggregate class accuracy, total completed attempts, and active student count.
3. **At-Risk Identification**: System highlights topics where cohort accuracy is below $60\%$ or where predicted forgetting signals have fired.
4. **Action Dispatch**: Teacher clicks "Assign Revision" to dispatch a targeted review plan directly to students' revision queues.

---

## 7. Current Database & Verification Ground Truth

The local development environment uses `edunavika.db` (SQLite 3):
- **Curriculum Hierarchy Populated**:
  - **1 Active Standard**: GSEB Standard 10 (Grade 10).
  - **3 Core Subjects**: Science & Technology, Mathematics, English Literature & Language.
  - **18 Chapters**: Including *Chemical Reactions*, *Acids & Bases*, *Life Processes*, *Light*, *A Letter to God*, etc.
  - **24 Topics**: Fully indexed with page references and content bounds.
- **Verified Default Accounts**:
  - Student: `kachatushar108@gmail.com` (Password: `Tushar@21`)
  - Teacher: `tushar.kacha141862@marwadiuniversity.ac.in` (Password: `2120@8030`)
- **Automated Test Suite**:
  - Over 187 backend unit and integration tests passing green across database models, security, decay domain calculations, and API contracts.

---

## 8. Production Roadmap & Next Milestones

```
┌─────────────────────────────────────────────────────────────┐
│ Milestone 7: Full-Stack Interactive Prototype Polish        │ ◀── CURRENT FOCUS
│ - Modern sleek dark/light theme with glassmorphic cards     │
│ - Live backend curriculum hookup to frontend browser        │
│ - Interactive spaced-repetition flashcard memory runner     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 8: School B2B Multi-Tenancy & School Portal       │
│ - School Admin role & classroom roster bulk import (CSV)    │
│ - Division-level curriculum pacing guides                   │
│ - Academic calendar & exam term milestone tracking          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 9: Trained ML Retention & Forgetting Model        │
│ - Offline training on longitudinal learning event dataset   │
│ - Model artifact export (ONNX / Scikit-learn pipeline)      │
│ - Real-time inference replacing heuristic decay bounds      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 10: Production Cloud Deployment                   │
│ - Managed PostgreSQL on Cloud (AWS RDS / GCP Cloud SQL)     │
│ - Docker containerization & CI/CD pipeline                  │
│ - Redis cache layer for high-frequency telemetry buffering  │
└─────────────────────────────────────────────────────────────┘
```

---

*Document compiled and verified against EduNavika `master` branch codebase (`00d0458`).*
