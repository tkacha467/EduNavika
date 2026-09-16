import os
import sys
import time
import json
import argparse
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any

from backend.app.core.database import SessionLocal
from backend.app.ingestion.schemas import (
    DocumentIdentity,
    DocumentDiagnostic,
    IngestionSummaryReport,
    PageQualityStatus,
)
from backend.app.ingestion.scanner import DocumentScanner
from backend.app.ingestion.metadata import MetadataExtractor
from backend.app.ingestion.pdf_extractor import PDFExtractor
from backend.app.ingestion.quality import PageQualityAnalyzer
from backend.app.ingestion.cleaner import DeterministicCleaner
from backend.app.ingestion.structure import StructureParser
from backend.app.ingestion.chunker import StructureAwareChunker
from backend.app.ingestion.mapper import DatabaseCurriculumMapper
from backend.app.ingestion.validator import IngestionValidator


class IngestionPipeline:
    """
    Production-grade curriculum ingestion orchestrator for GSEB textbooks.
    Provides:
    - Incremental processing using SHA-256 hash tracking
    - Single document and standard-level filtering
    - Memory-efficient document-by-document processing
    - Isolated error handling (failure on 1 PDF does not crash the entire batch)
    - Full dry-run mode (no DB modification)
    - Intermediate artifact emission to data/processed/
    """

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path = Path("data/processed"),
        dry_run: bool = False,
        force: bool = False,
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.force = force

        # Subdirectories for intermediate artifacts
        self.docs_dir = self.output_dir / "documents"
        self.pages_dir = self.output_dir / "pages"
        self.struct_dir = self.output_dir / "structure"
        self.chunks_dir = self.output_dir / "chunks"
        self.reports_dir = self.output_dir / "reports"

        for d in [self.docs_dir, self.pages_dir, self.struct_dir, self.chunks_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.hash_store_path = self.output_dir / ".processed_hashes.json"
        self.processed_hashes: Dict[str, str] = self._load_hashes()

        # Components
        self.scanner = DocumentScanner(self.input_dir)
        self.quality_analyzer = PageQualityAnalyzer()
        self.cleaner = DeterministicCleaner()
        self.structure_parser = StructureParser()
        self.chunker = StructureAwareChunker()
        self.validator = IngestionValidator(self.reports_dir)

    def _load_hashes(self) -> Dict[str, str]:
        if self.hash_store_path.exists():
            try:
                with open(self.hash_store_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_hashes(self):
        try:
            with open(self.hash_store_path, "w", encoding="utf-8") as f:
                json.dump(self.processed_hashes, f, indent=2)
        except Exception:
            pass

    def run(
        self,
        document_filter: Optional[str] = None,
        standard_filter: Optional[int] = None,
    ) -> IngestionSummaryReport:
        start_time = time.time()
        print(f"[PIPELINE] Starting ingestion run (dry_run={self.dry_run}, force={self.force})...")

        # 1. Scan documents (pass filters directly to scanner to avoid hashing unaffected files)
        all_docs, mismatches = self.scanner.scan(
            specific_document=document_filter,
            standard_filter=standard_filter,
        )
        print(f"[PIPELINE] Selected {len(all_docs)} PDFs for processing", flush=True)

        target_docs = all_docs

        summary = IngestionSummaryReport(
            total_pdfs_discovered=len(all_docs),
            total_pdfs_expected_from_manifest=len(self.scanner.manifest_docs),
            manifest_mismatches=mismatches,
        )

        db = None
        if not self.dry_run:
            db = SessionLocal()
            mapper = DatabaseCurriculumMapper(db)

        try:
            for doc in target_docs:
                diag = self._process_single_document(doc, mapper if not self.dry_run else None)
                summary.document_diagnostics.append(diag)

                # Aggregate metrics
                if diag.status == "SUCCESS":
                    summary.successfully_processed_pdfs += 1
                elif diag.status == "SKIPPED":
                    summary.skipped_unchanged_pdfs += 1
                else:
                    summary.failed_pdfs += 1

                summary.total_pages += diag.total_pages
                summary.pages_extracted += diag.extracted_pages
                summary.pages_needing_ocr += diag.ocr_required_pages
                summary.low_quality_pages += diag.low_quality_pages
                summary.chapters_detected += diag.chapters_detected
                summary.topics_detected += diag.topics_detected
                summary.ambiguous_topics += diag.ambiguous_topics
                summary.chunks_generated += diag.chunks_generated
                summary.chunks_inserted += diag.chunks_inserted
                summary.warnings.extend(diag.warnings)
                summary.errors.extend(diag.errors)

        finally:
            if db:
                db.close()

        summary.processing_duration_seconds = round(time.time() - start_time, 2)
        if not self.dry_run:
            self._save_hashes()

        # Write reports
        json_path, md_path = self.validator.write_reports(summary)
        print(f"[PIPELINE] Finished run in {summary.processing_duration_seconds}s")
        print(f"[PIPELINE] Reports written to:\n  {json_path}\n  {md_path}")

        return summary

    def _process_single_document(
        self,
        doc: DocumentIdentity,
        mapper: Optional[DatabaseCurriculumMapper],
    ) -> DocumentDiagnostic:
        diag = DocumentDiagnostic(
            document_id=doc.document_id,
            relative_path=doc.relative_path,
            filename=doc.filename,
        )

        # Check incremental hash
        if not self.force and not self.dry_run:
            prev_hash = self.processed_hashes.get(doc.document_id)
            if prev_hash == doc.file_hash:
                print(f"[DOC] Skipping unchanged document: {doc.filename}")
                diag.status = "SKIPPED"
                return diag

        print(f"[DOC] Processing {doc.filename} (Std {doc.standard} - {doc.subject})...")
        full_pdf_path = self.input_dir / doc.relative_path

        try:
            # 1. Page extraction
            extracted_pages = PDFExtractor.extract_pages(
                full_pdf_path, doc.document_id, self.quality_analyzer
            )
            diag.total_pages = len(extracted_pages)

            # 2. Quality analysis tally
            for p in extracted_pages:
                if p.quality_status == PageQualityStatus.EXTRACTED:
                    diag.extracted_pages += 1
                elif p.quality_status == PageQualityStatus.NEEDS_OCR:
                    diag.ocr_required_pages += 1
                elif p.quality_status == PageQualityStatus.LOW_QUALITY:
                    diag.low_quality_pages += 1
                elif p.quality_status == PageQualityStatus.EMPTY:
                    diag.empty_pages += 1

            # 3. Text cleaning
            cleaned_pages = [self.cleaner.clean_page(p) for p in extracted_pages]

            # 4. Structure parsing
            chapters = self.structure_parser.parse_structure(cleaned_pages)
            diag.chapters_detected = len(chapters)
            diag.topics_detected = sum(len(c.topics) for c in chapters)

            # 5. Structure-aware chunking
            chunks = self.chunker.chunk_document(doc, cleaned_pages, chapters)
            diag.chunks_generated = len(chunks)

            # 6. Database mapping (if not dry run)
            if not self.dry_run and mapper:
                inserted, skipped = mapper.persist_chunks(doc, chapters, chunks)
                diag.chunks_inserted = inserted
                self.processed_hashes[doc.document_id] = doc.file_hash
            else:
                diag.chunks_inserted = 0

            # 7. Write intermediate JSON / JSONL artifacts for auditability
            self._write_intermediate_artifacts(doc, extracted_pages, chapters, chunks)

            diag.status = "SUCCESS"

        except Exception as e:
            err_msg = f"Failed processing {doc.filename}: {str(e)}"
            diag.status = "FAILED"
            diag.errors.append(err_msg)
            print(f"[ERROR] {err_msg}")
            traceback.print_exc()

        return diag

    def _write_intermediate_artifacts(
        self,
        doc: DocumentIdentity,
        pages: list,
        chapters: list,
        chunks: list,
    ):
        base_name = f"{doc.document_id}_{Path(doc.filename).stem}"

        # 1. Structure JSON
        struct_file = self.struct_dir / f"{base_name}_structure.json"
        with open(struct_file, "w", encoding="utf-8") as f:
            json.dump([c.model_dump(mode="json") for c in chapters], f, indent=2, ensure_ascii=False)

        # 2. Chunks JSONL
        chunks_file = self.chunks_dir / f"{base_name}_chunks.jsonl"
        with open(chunks_file, "w", encoding="utf-8") as f:
            for chk in chunks:
                f.write(json.dumps(chk.model_dump(mode="json"), ensure_ascii=False) + "\n")


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EduNavika GSEB Curriculum Ingestion Pipeline (Milestone 2)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=str,
        default="GSEB-Dataset",
        help="Path to GSEB-Dataset folder containing Standard subdirectories",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed",
        help="Directory to save intermediate artifacts and reports",
    )
    parser.add_argument(
        "--document",
        type=str,
        default=None,
        help="Filter by specific document relative path or filename",
    )
    parser.add_argument(
        "--standard",
        type=int,
        choices=[9, 10, 11, 12],
        default=None,
        help="Filter by specific Standard (9, 10, 11, or 12)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery, extraction, structure, and chunking without database commits",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing even if document hash has not changed",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate and print comprehensive quality report",
    )
    # Milestone 2.5 Audit Switches
    parser.add_argument(
        "--ocr-audit",
        action="store_true",
        help="Run Phase 2 OCR Coverage Audit across all 86 GSEB PDF documents",
    )
    parser.add_argument(
        "--ocr-benchmark",
        action="store_true",
        help="Run Phase 3 Offline OCR Benchmark across representative scanned textbooks",
    )
    parser.add_argument(
        "--structure-audit",
        action="store_true",
        help="Run Phase 4 Structure Audit against ground-truth TOCs",
    )
    parser.add_argument(
        "--chunk-audit",
        action="store_true",
        help="Run Phase 5 Chunk Quality and BM25 Lexical Retrieval Audit",
    )
    parser.add_argument(
        "--provenance-audit",
        action="store_true",
        help="Run Phase 6 Curriculum Lineage and Physical Source Provenance Audit",
    )
    parser.add_argument(
        "--corpus-audit",
        action="store_true",
        help="Run complete Milestone 2.5 master corpus audit suite and render final verdict",
    )
    parser.add_argument(
        "--event-audit",
        action="store_true",
        help="Run Milestone 8 LearningEvent telemetry coverage and data-quality audit",
    )
    parser.add_argument(
        "--target-audit",
        action="store_true",
        help="Run Milestone 9 real longitudinal data readiness and Target A validation audit",
    )
    return parser


def main():
    parser = build_cli()
    args = parser.parse_args()

    reports_dir = Path(args.output) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Handle independent audit switches
    if getattr(args, "event_audit", False):
        from backend.app.domain.prediction.audit import LearningEventAuditor
        print("[AUDIT] Running LearningEvent Telemetry Coverage & Data-Quality Audit...")
        auditor = LearningEventAuditor(output_dir=reports_dir)
        rep = auditor.run_audit()
        print(f"[AUDIT] Status: {rep['verdict']} | Total Events: {rep['total_events']} | Active Students: {rep['unique_students_with_events']} | Violations: {rep['data_quality_violations']['total_violations']}")
        return

    if getattr(args, "target_audit", False):
        from backend.app.domain.prediction.target_validator import TargetValidityAuditor
        print("[AUDIT] Running Milestone 9 Real Data Readiness & Target Validity Audit...")
        auditor = TargetValidityAuditor(output_dir=reports_dir)
        rep = auditor.run_audit()
        target_info = rep["target_a_analysis"]
        print(f"[AUDIT] Verdict: {rep['verdict']} | Valid Target A Pairs: {target_info['valid_observations_count']} | Total Evaluative Events: {rep['evaluative_events_count']}")
        return

    if args.ocr_audit:
        from backend.app.ingestion.ocr.ocr_auditor import OCRAuditor

        print("[AUDIT] Running OCR Coverage Audit across 86 PDFs...")
        auditor = OCRAuditor(dataset_dir=Path(args.input), output_dir=reports_dir)
        rep = auditor.run_audit()
        print(f"[AUDIT] Completed: {rep.total_documents} documents ({rep.total_pages} pages). Text-dominant: {rep.text_dominant_documents}, Hybrid: {rep.hybrid_documents}, OCR-required: {rep.ocr_required_documents}.")
        return

    if args.ocr_benchmark:
        from backend.app.ingestion.ocr.ocr_benchmark import OCRBenchmark
        print("[AUDIT] Running OCR Benchmark on representative scanned textbooks...")
        bench = OCRBenchmark(dataset_dir=Path(args.input), output_dir=reports_dir)
        rep = bench.run_benchmark()
        print(f"[AUDIT] Status: {rep.quality_gate_status} | Speed: {rep.overall_sec_per_page}s/page | Avg Conf: {rep.overall_avg_confidence * 100:.1f}%")
        return

    if args.structure_audit:
        from backend.app.ingestion.structure_auditor import StructureAuditor
        print("[AUDIT] Running Structure Audit on representative textbooks...")
        auditor = StructureAuditor(dataset_dir=Path(args.input), output_dir=reports_dir)
        rep = auditor.audit_representative_books()
        print(f"[AUDIT] Total: {rep.total_audited} | PASS: {rep.passed_count} | REVIEW: {rep.review_count} | FAIL: {rep.failed_count}")
        return

    if args.chunk_audit:
        from backend.app.ingestion.chunk_auditor import ChunkAuditor
        print("[AUDIT] Running Chunk Quality & BM25 Lexical Retrieval Audit...")
        auditor = ChunkAuditor(output_dir=reports_dir)
        rep = auditor.run_audit()
        print(f"[AUDIT] Status: {rep.quality_gate_status} | Chunks: {rep.total_chunks_evaluated} | Avg Tok: {rep.avg_tokens} | R@5: {rep.recall_at_5 * 100:.1f}% | MRR: {rep.mrr}")
        return

    if args.provenance_audit:
        from backend.app.ingestion.provenance_auditor import ProvenanceAuditor
        print("[AUDIT] Running Provenance & Relational Lineage Audit...")
        auditor = ProvenanceAuditor(dataset_dir=Path(args.input), output_dir=reports_dir)
        rep = auditor.run_audit()
        print(f"[AUDIT] Status: {rep.quality_gate_status} | Lineage: {rep.valid_lineage_count}/{rep.total_learning_contents} | Verified: {rep.source_verification_passed}/{rep.sampled_for_source_verification} | Integrity: {rep.provenance_integrity_score * 100:.1f}%")
        return

    if args.corpus_audit:
        from backend.app.ingestion.corpus_auditor import CorpusAuditor
        print("[AUDIT] Running Master Milestone 2.5 Corpus Audit Suite...")
        auditor = CorpusAuditor(dataset_dir=Path(args.input), output_dir=reports_dir)
        rep = auditor.run_full_corpus_audit()
        print("\n" + "=" * 60)
        print(f"MILESTONE 2.5 FINAL VERDICT: {rep.verdict.decision} (Confidence: {rep.verdict.confidence_score * 100:.1f}%)")
        print(f"RAG Readiness Status: {rep.verdict.rag_readiness_status}")
        print("=" * 60)
        print(rep.verdict.summary)
        print("=" * 60)
        return

    # Standard Ingestion Pipeline Run
    pipeline = IngestionPipeline(
        input_dir=Path(args.input),
        output_dir=Path(args.output),
        dry_run=args.dry_run,
        force=args.force,
    )

    summary = pipeline.run(
        document_filter=args.document,
        standard_filter=args.standard,
    )

    print("\n" + "=" * 60)
    print("INGESTION SUMMARY RESULT")
    print("=" * 60)
    print(f"Processed PDFs: {summary.successfully_processed_pdfs} / {summary.total_pdfs_discovered}")
    print(f"Failed PDFs:    {summary.failed_pdfs}")
    print(f"Total Pages:    {summary.total_pages} (Needing OCR: {summary.pages_needing_ocr})")
    print(f"Chapters:       {summary.chapters_detected}")
    print(f"Topics:         {summary.topics_detected}")
    print(f"Chunks:         {summary.chunks_generated}")
    print(f"DB Inserts:     {summary.chunks_inserted}")
    print(f"Duration:       {summary.processing_duration_seconds}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
