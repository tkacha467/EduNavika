# EduNavika — Project Progress & Status Report

**Repository**: `https://github.com/tkacha467/EduNavika`  
**Current State**: **Milestone 2.5 Complete & Verified**  
**Corpus Quality Verdict**: **`PASS`** (Confidence: 98.0%)  
**RAG Readiness Status**: **`VERIFIED_READY`**  
**Automated Tests**: **32 / 32 Passing** (100% green)  
**Database Migration**: Alembic revision `e025394444f5` (head)  
**Last Updated**: September 2026  

---

## 1. Executive Summary

EduNavika is an intelligent, research-grade personalized learning platform tailored for secondary and higher-secondary school students (Standards 9–12) following the Gujarat Secondary and Higher Secondary Education Board (GSEB) English-medium curriculum.

The project foundation has been built incrementally through verifiable milestones:
1. **Milestone 1**: Complete backend architecture, dual SQLite/PostgreSQL schema, research event stream, and 39 RESTful API endpoints.
2. **Milestone 2**: Deterministic, provenance-preserving curriculum ingestion pipeline for GSEB textbook PDFs.
3. **Milestone 2.5**: Full curriculum corpus audit across all 86 textbooks, local offline OCR benchmarking (`RapidOCR` + `pypdfium2`), Table of Contents structure validation, chunk hygiene checks, BM25 retrieval benchmarking, and provenance round-trip verification.

---

## 2. Milestone-by-Milestone Progress

```
┌─────────────────────────────────────────────────────────────┐
│ Milestone 1: Backend Foundation & API Contracts             │ ✅ COMPLETE
│ - SQLAlchemy 2.0 + Alembic (SQLite dev / PostgreSQL prod)   │
│ - Curriculum, Assessment, Attempt, LearningEvent models     │
│ - 39 REST Endpoints, 17/17 tests passing                    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 2: Curriculum Ingestion Pipeline                  │ ✅ COMPLETE
│ - 86 GSEB official PDFs discovered & hashed (SHA-256)       │
│ - Page extraction, quality gates, deterministic cleaner     │
│ - Structure-aware chunking (418 chunks ingested)            │
│ - 23/23 tests passing                                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 2.5: Corpus Audit & OCR Benchmark                 │ ✅ COMPLETE (PASS)
│ - RapidOCR + pypdfium2 offline OCR (94.3% avg confidence)   │
│ - Multi-page TOC & /G<n> font glyph decoding (100% match)   │
│ - BM25 Lexical Retrieval Benchmark (Recall@5 = 100%, MRR 1.0)│
│ - 100% relational lineage (0 orphans, 0 duplicate chunks)   │
│ - 32/32 tests passing                                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Milestone 3: Embeddings, RAG & MCQ Generation               │ ⏳ UPCOMING
│ - Vector store integration (pgvector / Chroma)              │
│ - Hybrid Dense + Sparse BM25 retrieval                      │
│ - Provenance-grounded MCQ generation with distractor checks │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Subsystem Status

### 3.1 Database & Core Models (`backend/app/models/`)
- **Curriculum Hierarchy**:
  - `Standard` (Grade 9, 10, 11, 12)
  - `Subject` (Mathematics, Science, English, Social Science, etc.)
  - `Chapter` (Chapter number, title, page bounds)
  - `Topic` (Topic order, title, page bounds)
  - `LearningContent` (Text chunks with exact PDF page and source file traceability)
- **Assessment & Attempts**:
  - `MCQQuestion` (Question text, 4 options, correct answer, explanation, bloom taxonomy level)
  - `Assessment` (Standard, Subject, Chapter, Topic associations, duration, total marks)
  - `StudentAttempt` (Score, percentage, completion timestamp, duration)
  - `StudentAnswer` (Selected option, correctness, latency ms)
- **Research Substrate & Performance**:
  - `LearningEvent` (Immutable, append-only research stream with JSON payload for future forgetting curve training)
  - `TopicPerformance` (Application-level aggregate metrics: mastery score, stability, last review)
  - `ForgettingSignal` (Predicted retention, recommended review dates)
- **Users & Auth**:
  - `User`, `StudentProfile`, `TeacherProfile` with UUID foreign keys and unique constraints.

### 3.2 Ingestion & Audit Pipeline (`backend/app/ingestion/`)
- **`scanner.py`**:
  - Scans all 86 GSEB textbook PDFs across Standards 9–12.
  - Generates deterministic `doc_<sha256[:12]>` document identities.
  - Reconciles 100% of discovered PDFs against `dataset_manifest.json` and `dataset_inventory.csv`.
- **`pdf_extractor.py` & `cleaner.py`**:
  - Extracts text page-by-page preserving physical PDF page numbers (1-indexed).
  - Cleans typography, strips running headers/footers, removes control characters, normalizes whitespace.
  - Decodes custom font glyph mappings (`/G<n>`).
- **`structure.py` & `structure_auditor.py`**:
  - Detects chapters and subtopics via Table of Contents (TOC) and heading heuristics.
  - Multi-page TOC parsing resolves chapters across page boundaries.
  - Validated against ground-truth TOCs:
    - **Std-10 Mathematics**: 14 / 14 chapters detected (Real Numbers through Probability).
    - **Std-10 Science**: 13 / 13 chapters detected.
    - **Std-10 First Flight English**: 9 / 9 chapters detected.
- **`ocr/ocr_engine.py` & `ocr_benchmark.py`**:
  - Pure local offline OCR powered by `RapidOCR` (ONNX Runtime CPU) and `pypdfium2`.
  - Zero external daemons, zero cloud APIs, zero LLM dependencies.
  - Scanned textbook benchmark results:
    - *Std-10 Social Science*: **97.4%** confidence
    - *Std-10 Computer Studies*: **97.6%** confidence
    - *Std-11 Hornbill English*: **96.5%** confidence
    - *Std-9 Sanskrit*: **85.6%** confidence
    - **Overall Average**: **94.3%** confidence at **18.0 sec/page** on CPU.
- **`chunk_auditor.py`**:
  - Token size distribution: Min = 363, Avg = **594.6**, Median = **583**, P95 = 801 tokens.
  - Anomaly rate: **0.71%** (3/418 flagged, zero breaking defects).
  - Okapi BM25 Lexical Retrieval:
    - **Recall@1**: 100.0%
    - **Recall@5**: 100.0%
    - **Recall@10**: 100.0%
    - **MRR (Mean Reciprocal Rank)**: 1.000
- **`provenance_auditor.py`**:
  - **Relational Lineage**: 418 / 418 (100%) valid unbroken paths from Standard to Chunk.
  - **Orphan Records**: 0
  - **Duplicate Chunks**: 0
  - **Physical PDF Round-Trip Checks**: 25 / 25 sampled chunks verified directly against physical PDF pages.

---

## 4. Test Suite Summary

Total automated tests: **32 passed in ~35 seconds**.

| Test File | Test Count | Focus Area |
| :--- | :---: | :--- |
| `test_api_attempts.py` | 1 | Assessment generation & student attempt flow |
| `test_api_curriculum.py` | 2 | Hierarchy navigation & standard/subject creation |
| `test_api_mcqs.py` | 1 | MCQ lifecycle & duplicate prevention |
| `test_api_research.py` | 1 | Append-only learning event stream & research contracts |
| `test_duplicate_detection.py` | 3 | SHA-256 text hashing, exact & semantic deduplication |
| `test_ingestion_extractor_cleaner.py` | 2 | Page quality classification & text cleaning |
| `test_ingestion_pipeline_idempotency.py` | 1 | Idempotent DB mapping & provenance persistence |
| `test_ingestion_scanner.py` | 2 | 86-PDF discovery, hash stability & manifest reconciliation |
| `test_ingestion_structure_chunking.py` | 1 | Structure parser & structure-aware chunker |
| `test_integrity_and_research_contracts.py` | 4 | Immutability, DB constraints & forgetting signals |
| `test_learning_events.py` | 1 | Research event recording & aggregate metrics |
| `test_models.py` | 4 | User profiles, cascade behaviors & foreign keys |
| `test_ocr_engine_benchmark.py` | 4 | Levenshtein distance, CER/WER metrics & RapidOCR engine |
| `test_ocr_and_structure_auditors.py` | 2 | 86-PDF manifest reconciliation & TOC structure validation |
| `test_chunk_and_provenance_auditors.py` | 3 | BM25 retrieval, chunk hygiene & relational lineage |
| **Total** | **32** | **All 32 Green** |

---

## 5. Artifacts & Generated Reports

All audit artifacts and reports are persisted under `data/processed/reports/`:
- `corpus_quality_report.md` & `.json`: Master Milestone 2.5 verdict report.
- `ocr_benchmark_report.md` & `.json`: RapidOCR benchmark across scanned textbooks.
- `structure_audit.md` & `.json`: Ground-truth TOC validation report.
- `chunk_quality_report.md` & `.json`: Token distribution & BM25 retrieval benchmark.
- `provenance_audit.md` & `.json`: Relational lineage & physical PDF round-trip audit.

---

## 6. CLI Commands Reference

```bash
# Run complete test suite
python -m pytest backend/tests/ -v

# Run Master Milestone 2.5 Corpus Audit Suite
python -m backend.app.ingestion.pipeline --corpus-audit

# Run Individual Audits
python -m backend.app.ingestion.pipeline --ocr-audit
python -m backend.app.ingestion.pipeline --ocr-benchmark
python -m backend.app.ingestion.pipeline --structure-audit
python -m backend.app.ingestion.pipeline --chunk-audit
python -m backend.app.ingestion.pipeline --provenance-audit

# Standard Ingestion
python -m backend.app.ingestion.pipeline --input GSEB-Dataset --standard 10
python -m backend.app.ingestion.pipeline --input GSEB-Dataset --document "STD-10th/Std-10_Science_English Medium.pdf"
```

---

## 7. Next Milestone: Milestone 3 (Planned)

With Milestone 2.5 verified as **`PASS`** and the corpus confirmed **`VERIFIED_READY`**, the platform is primed for Milestone 3:
1. **Vector Indexing**: Generate dense embeddings for all 418 verified chunks.
2. **Hybrid Retrieval**: Combine dense semantic search with deterministic BM25 lexical search.
3. **Curriculum-Grounded MCQ Generation**: Generate syllabus-faithful MCQs with distractor validation and Bloom taxonomy tagging.
4. **Forgetting Prediction Integration**: Connect learning event logs to spaced repetition scheduling algorithms.
