# EduNavika — Curriculum Ingestion Architecture (Milestone 2)

## 1. Dataset Structure
The Gujarat Secondary and Higher Secondary Education Board (GSEB) English-medium curriculum dataset is organized under `GSEB-Dataset/` with Standards 9th through 12th:
```text
GSEB-Dataset/
├── STD-9th/    (11 PDFs)
├── STD-10th/   (12 PDFs)
├── STD-11th/   (31 PDFs)
└── STD-12th/   (32 PDFs)
Total: Exactly 86 PDF files
```

## 2. Manifest & Inventory Reconciliation
The pipeline treats `GSEB-Dataset/dataset_manifest.json` and `dataset_inventory.csv` as the primary authorities for:
- Standard (Grade 9–12)
- Subject classification
- Category (`CORE_TEXTBOOK`, `SUPPLEMENTARY_TEXTBOOK`, `REFERENCE/OTHER`)
- Curriculum relevance (`HIGH`, `MEDIUM`, `LOW`)
- Expected page count & OCR flags (`NONE`, `HYBRID`, `REQUIRED`)

`DocumentScanner` hashes all discovered files via SHA-256 and reconciles them against manifest entries, detecting missing or mismatched files.

## 3. Deterministic Document Identity
Each PDF receives a deterministic identifier:
```text
doc_<sha256[:12]>
```
The exact same PDF content always produces the same identity. If source bytes change, a new hash reflects the new document version.

## 4. Metadata Extraction
Extracted metadata includes:
- Source path & filename
- File size (bytes) and SHA-256 digest
- Authoritative manifest grade, subject, category
- Embedded PDF metadata (title, author, creator, producer, creation date) without overriding manifest curriculum truths.

## 5. Page-Level Extraction
Extraction never concatenates whole books into monolithic strings. The unit of extraction is:
```text
PDF -> Page
```
Each page record preserves:
- `document_id`
- `pdf_page_number` (1-indexed physical PDF index)
- `printed_page_number` (null unless reliably detected)
- `raw_text`
- `extraction_method` (e.g. `pypdf`)
- Character count, word count, alphabetic ratio, whitespace ratio
- Quality status (`EXTRACTED`, `LOW_QUALITY`, `NEEDS_OCR`, `EMPTY`)

## 6. PDF Page vs. Printed Textbook Page
Physical PDF page numbers and textbook printed page numbers differ due to prefaces, cover art, Roman numeral preliminaries, and inserts.
- Physical page is stored in `LearningContent.source_page` and chunk metadata `pdf_page_start`/`pdf_page_end`.
- Printed page is recorded in metadata only when an exact header/footer printed page number is identified; it is never guessed.

## 7. Extraction Quality Analysis & OCR Detection
`PageQualityAnalyzer` conservatively evaluates:
- `character_count` (< 20 chars -> flagged `NEEDS_OCR`)
- `alphabetic_ratio` (< 0.45 -> flagged `LOW_QUALITY`)
- `whitespace_ratio` (> 0.85 -> flagged `LOW_QUALITY`)
Scanned or image-only pages are identified and reported as `NEEDS_OCR` without running expensive external OCR blindly during baseline ingestion.

## 8. Deterministic Text Cleaning
`DeterministicCleaner` performs lossless, semantic-preserving cleaning:
- Font glyph translation (e.g. decoding `/G83/G111` escape sequences to Unicode characters within safe range)
- Unicode NFKC normalization
- Line ending normalization (`\r\n` -> `\n`)
- Hyphenated line-break repair (`reac-\ntion` -> `reaction`)
- Internal whitespace normalization while preserving paragraph structures
- Conservative header/footer suppression without deleting raw text.

## 9. Curriculum Structure Detection
`StructureParser` identifies:
1. **Table of Contents (TOC)**: Scans introductory pages for `Chapter X Title Page` or `1. Title Page` patterns.
2. **Page Offset Alignment**: Dynamically computes the physical PDF offset where Chapter 1 appears to map TOC entries to physical PDF pages.
3. **Fallback Page Heading Scan**: Detects prominent chapter headers (`CHAPTER 1`, `1. Chemical Reactions`, `1CHAPTER`).
4. **Subsections & Topics**: Identifies section patterns (`1.1`, `2.1`) within chapter page boundaries.
5. **Conservative Integrity**: NEVER invents fake topics. If no subsections exist, a primary chapter-level topic is created and flagged appropriately.

## 10. Structure-Aware Chunking
`StructureAwareChunker` groups content adhering to curriculum boundaries:
- Target size: ~500 to 800 tokens (~2000 to 3200 characters)
- Paragraph, heading, definition, example, and formula boundaries are preserved without mid-sentence truncation.
- Generates reproducible, deterministic chunk IDs: `chk_<sha256[:16]>` computed from `document_id + chapter + topic + page_range + content`.
- Classifies content types deterministically: `TEXT`, `EXAMPLE`, `DEFINITION`, `FORMULA`, `EXPLANATION`.

## 11. Database Mapping & Complete Provenance
`DatabaseCurriculumMapper` maps chunks into the normalized Milestone 1 hierarchy:
```text
Standard -> Subject -> Chapter -> Topic -> LearningContent
```
Every `LearningContent` record retains full traceability:
- `topic_id`: Foreign key to normalized Topic
- `source_document`: Relative path of source PDF
- `source_page`: Physical PDF page index
- `source_reference`: Document name and page range
- `chunk_identifier`: Deterministic chunk ID
- `content_metadata`: JSON dictionary containing heading path, token count, page ranges, and file hash.

## 12. Idempotency & Incremental Ingestion
- Checks existing `chunk_identifier` and unique constraints before inserting.
- Running ingestion repeatedly produces 0 duplicate records.
- Incremental hash tracking (`.processed_hashes.json`) skips unchanged PDFs in 0.05s.
- Supports `--force` to reprocess while safely preserving database integrity.

## 13. CLI Interface
```bash
# Help
python -m backend.app.ingestion.pipeline --help

# Single document dry-run
python -m backend.app.ingestion.pipeline --input GSEB-Dataset --document "STD-10th/Std-10_Science_English Medium.pdf" --dry-run

# Single document database ingestion
python -m backend.app.ingestion.pipeline --input GSEB-Dataset --document "STD-10th/Std-10_Science_English Medium.pdf"

# Standard-level filtering
python -m backend.app.ingestion.pipeline --input GSEB-Dataset --standard 10

# Force reprocessing
python -m backend.app.ingestion.pipeline --input GSEB-Dataset --document "STD-10th/Std-10_Science_English Medium.pdf" --force
```

## 14. Validation Reports & Artifacts
The pipeline outputs intermediate artifacts to `data/processed/`:
- `data/processed/structure/*_structure.json`
- `data/processed/chunks/*_chunks.jsonl`
- `data/processed/reports/ingestion_report.json`
- `data/processed/reports/ingestion_report.md`

## 15. Milestone 2.5: Corpus Audit, Offline OCR Benchmark & Structure Validation

Milestone 2.5 provides automated audit tooling to independently verify the GSEB curriculum corpus before RAG retrieval, vector search, or MCQ generation are introduced.

### Audit Dimensions
1. **OCR Coverage & Reconciliation (`--ocr-audit`)**:
   - Reconciles all 86 official GSEB PDFs against manifest & inventory.
   - Categorizes PDFs into TEXT_DOMINANT, HYBRID, and OCR_REQUIRED.
   - Identifies vector-stream outlines vs embedded rasters vs native fonts.
2. **Offline OCR Benchmark (`--ocr-benchmark`)**:
   - High-fidelity PDF page rasterization via `pypdfium2`.
   - Local, offline OCR inference using `RapidOCR` with ONNX Runtime (CPU).
   - Zero external daemons, zero cloud API calls, zero LLM dependencies.
   - Benchmarked across representative scanned textbooks (Social Science, Computer Studies, Sanskrit, Hornbill English) with >94% average confidence.
3. **Structure & TOC Parsing (`--structure-audit`)**:
   - Audits chapter and topic extraction against ground-truth Tables of Contents.
   - Multi-page TOC parsing and font glyph normalization (`/G<n>` resolution).
   - Std-10 Maths: 14/14 chapters detected (Real Numbers through Probability).
   - Std-10 First Flight: 9/9 chapters detected.
4. **Chunk Quality & BM25 Lexical Retrieval (`--chunk-audit`)**:
   - Token size distribution and outlier detection (400–800 token target).
   - Contamination checks (header/footer stripping, control character cleaning).
   - Deterministic Okapi BM25 retrieval benchmark across curated curriculum queries (Recall@5 = 100%, MRR = 1.0).
5. **Lineage & Provenance Round-Trip Check (`--provenance-audit`)**:
   - Validates unbroken relational hierarchy: `Standard -> Subject -> Chapter -> Topic -> LearningContent`.
   - Checks for orphaned records, broken foreign keys, and duplicate chunk IDs (0 duplicates, 0 orphans).
   - Performs physical PDF page round-trip checks to verify chunk authenticity.

### CLI Audit Usage
```bash
# Run individual audits
python -m backend.app.ingestion.pipeline --ocr-audit
python -m backend.app.ingestion.pipeline --ocr-benchmark
python -m backend.app.ingestion.pipeline --structure-audit
python -m backend.app.ingestion.pipeline --chunk-audit
python -m backend.app.ingestion.pipeline --provenance-audit

# Run comprehensive master audit suite and generate final milestone report
python -m backend.app.ingestion.pipeline --corpus-audit
```

