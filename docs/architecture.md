# EduNavika — Backend Architecture

## 1. System Vision & Philosophy

> **"Complex system. Simple student experience. Research-grade backend."**

EduNavika is an intelligent adaptive learning and retention platform tailored for secondary and higher secondary education (GSEB English-Medium curriculum, Standards 9 through 12). While students interact with an intuitive, friction-free interface, the backend operates as a research-grade data substrate that captures granular, longitudinal learning interactions over time.

### Core Architectural Principles
- **Modularity & Separation of Concerns**: Clean isolation between API presentation layers, business logic / services, domain persistence entities, and database migration systems.
- **Strict Database Normalization**: No ad-hoc, denormalized class-specific tables (e.g. no `class9_math` or `class10_science`). Curriculum standards and subjects are normalized entities with explicit relational integrity.
- **Relational Integrity & Auditability**: UUID primary keys (UUIDv4), UTC timestamps on all records, strict foreign key constraints, cascading delete rules, and deterministic duplicate tracking.
- **Curriculum Provenance**: Every generated item (learning content chunk, generated MCQ question) maintains explicit provenance tracing back to source documents (e.g. GSEB textbook PDF filenames, page numbers, chunk identifiers, generation model, and prompt version).
- **Longitudinal Research Foundation**: Raw learning events are stored immutably to power future cognitive modeling, knowledge tracing, and forgetting curve analysis without lossy aggregation or data leakage.

---

## 2. High-Level Architectural Layers

```
┌────────────────────────────────────────────────────────┐
│               Client Applications / UI                 │
│         (Student Practice, Teacher Dashboard)          │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON REST
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Presentation Layer                 │
│  - OpenAPI / Swagger 3.0 Documentation                 │
│  - Pydantic v2 Request/Response Schemas                │
│  - Standardized JSON Error Formats & Pagination        │
│  - Route Handlers (/api/v1/...)                        │
└───────────────────────────┬────────────────────────────┘
                            │ Validated Data Transfer Objects
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Service Layer                         │
│  - ExactDuplicateDetector (SHA-256 Text Hashing)       │
│  - SemanticDuplicateDetectorInterface (Future Vectors) │
│  - EventRecorderService (Atomic Event Logging)         │
│  - Evidence Aggregator (TopicPerformance maintenance)  │
└───────────────────────────┬────────────────────────────┘
                            │ SQLAlchemy 2.0 ORM
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Domain Model Layer                    │
│  - User, StudentProfile, TeacherProfile                │
│  - Standard, Subject, Chapter, Topic                   │
│  - LearningContent, MCQQuestion, QuestionHistory       │
│  - Assessment, AssessmentQuestion, Attempt, Answer     │
│  - LearningEvent, TopicPerformance                     │
│  - RevisionPlan, ForgettingSignal, TeacherAction       │
└───────────────────────────┬────────────────────────────┘
                            │ Engine & Connection Pool
                            ▼
┌────────────────────────────────────────────────────────┐
│             Persistence & Storage Layer                │
│  - SQLite: Local Development & Automated Tests         │
│  - PostgreSQL: Production & Longitudinal Research DB   │
│  - Alembic Database Migration Management               │
│  - GSEB Dataset PDF Corpus (STD 9th - 12th)            │
└────────────────────────────────────────────────────────┘
```

---

## 3. Directory Layout

The repository is structured as follows:

```text
EduNavika/
├── backend/
│   ├── alembic/
│   │   ├── versions/            # Versioned database migration scripts
│   │   ├── env.py               # Alembic runner with dynamic DB URL & model metadata
│   │   └── script.py.mako       # Migration template
│   ├── alembic.ini              # Alembic root configuration
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/   # Route handlers by domain
│   │   │       │   ├── curriculum.py
│   │   │       │   ├── content.py
│   │   │       │   ├── mcqs.py
│   │   │       │   ├── assessments.py
│   │   │       │   ├── attempts.py
│   │   │       │   ├── learning_events.py
│   │   │       │   ├── performance.py
│   │   │       │   ├── revision.py
│   │   │       │   ├── forgetting_signals.py
│   │   │       │   ├── teacher_actions.py
│   │   │       │   └── users.py
│   │   │       └── router.py    # Aggregated v1 API router
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic BaseSettings & environment loader
│   │   │   ├── database.py      # SQLAlchemy 2.0 engine, sessions, SQLite FK pragma
│   │   │   └── security.py      # Passlib bcrypt & JWT utility functions
│   │   ├── domain/              # Centralized domain enums and constants
│   │   │   ├── enums.py         # UserRole, EventType, ContentType, etc.
│   │   │   └── constants.py     # Standards, mastery states, evidence levels
│   │   ├── ingestion/           # Milestone 2 Curriculum Ingestion Package
│   │   │   ├── scanner.py       # Deterministic PDF discovery & SHA-256 hashing
│   │   │   ├── metadata.py      # PDF metadata extraction
│   │   │   ├── pdf_extractor.py # Page-level extraction with physical indexing
│   │   │   ├── quality.py       # Quality analysis & OCR-required diagnostics
│   │   │   ├── cleaner.py       # Deterministic text cleaning & glyph translation
│   │   │   ├── structure.py     # TOC & heading-based chapter/topic detection
│   │   │   ├── chunker.py       # Structure-aware chunking (~500-800 tokens)
│   │   │   ├── mapper.py        # Database curriculum mapper with provenance
│   │   │   ├── validator.py     # Quality reports & execution metrics
│   │   │   └── pipeline.py      # Ingestion orchestrator & CLI runner
│   │   ├── models/              # Declarative SQLAlchemy 2.0 models
│   │   │   ├── base.py          # UUID primary key & UTC timestamp mixin
│   │   │   ├── user.py          # User, StudentProfile, TeacherProfile
│   │   │   ├── curriculum.py    # Standard, Subject, Chapter, Topic
│   │   │   ├── content.py       # LearningContent (provenance & chunk metadata)
│   │   │   ├── mcq.py           # MCQQuestion, QuestionHistory
│   │   │   ├── assessment.py    # Assessment, AssessmentQuestion
│   │   │   ├── attempt.py       # Attempt, Answer
│   │   │   ├── learning_event.py# Longitudinal LearningEvent
│   │   │   ├── performance.py   # TopicPerformance evidence aggregation
│   │   │   ├── revision.py      # RevisionPlan
│   │   │   ├── forgetting.py    # ForgettingSignal
│   │   │   └── teacher_action.py# TeacherAction
│   │   ├── schemas/             # Pydantic v2 validation contracts
│   │   │   ├── common.py        # Pagination, metadata, standardized errors
│   │   │   ├── user.py
│   │   │   ├── curriculum.py
│   │   │   ├── content.py
│   │   │   ├── mcq.py
│   │   │   ├── assessment.py
│   │   │   ├── attempt.py
│   │   │   ├── learning_event.py
│   │   │   ├── performance.py
│   │   │   ├── revision.py
│   │   │   ├── forgetting.py
│   │   │   └── teacher_action.py
│   │   ├── services/            # Reusable business logic
│   │   │   ├── duplicate_detection.py
│   │   │   └── event_recorder.py
│   │   └── main.py              # Application entrypoint, CORS, exception handlers
│   └── tests/                   # Pytest test suite
│       ├── conftest.py
│       ├── test_models.py
│       ├── test_duplicate_detection.py
│       ├── test_learning_events.py
│       ├── test_api_curriculum.py
│       ├── test_api_mcqs.py
│       ├── test_api_attempts.py
│       └── test_api_research.py
├── docs/                        # Complete architecture & design documentation
│   ├── architecture.md
│   ├── database-schema.md
│   ├── api-contracts.md
│   └── ml-data-foundation.md
├── GSEB-Dataset/                # Official GSEB textbook & journal PDF corpus (STD 9-12)
├── pytest.ini                   # Pytest path configuration
├── requirements.txt             # Python backend dependencies
└── .gitignore                   # Standard ignore rules
```

---

## 4. Integration Roadmap

1. **Milestone 1 (Current)**: Data models, database schema, Alembic migrations, Pydantic contracts, FastAPI endpoints, duplicate detection abstraction, and test suite.
2. **Milestone 2 (Next)**: GSEB Curriculum Ingestion Pipeline (parsing the 86 textbook PDFs in `GSEB-Dataset/`, extracting chapters and topics, chunking text, generating content metadata, and populating `learning_contents`).
3. **Milestone 3**: RAG & Question Generation Pipeline (prompt versioning, LLM generation, automated quality checks, and teacher review workflow).
4. **Milestone 4**: Longitudinal Data Collection & Knowledge Decay Feature Engineering (deriving lag features, accuracy trends, and spaced-repetition schedules from `learning_events`).
5. **Milestone 5**: Model Training & Pedagogical Intelligence (evaluating knowledge tracing models, predicting retention decay, and driving personalized revision recommendations).
