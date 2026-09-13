import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

from backend.app.ingestion.schemas import (
    DocumentDiagnostic,
    IngestionSummaryReport,
)


class IngestionValidator:
    """
    Compiles detailed corpus execution metrics, validates quality constraints,
    and produces machine-readable JSON reports (ingestion_report.json)
    and human-readable Markdown reports (ingestion_report.md).
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_reports(self, summary: IngestionSummaryReport) -> Tuple[Path, Path]:
        json_path = self.output_dir / "ingestion_report.json"
        md_path = self.output_dir / "ingestion_report.md"

        # 1. Write JSON report
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

        # 2. Write Markdown report
        md_content = self.generate_markdown(summary)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        return json_path, md_path

    def generate_markdown(self, summary: IngestionSummaryReport) -> str:
        md = []
        md.append("# EduNavika — Curriculum Ingestion & Provenance Report")
        md.append(f"\n*Generated: {summary.timestamp.isoformat()}* | *Duration: {summary.processing_duration_seconds:.2f}s*\n")

        md.append("## Executive Summary\n")
        md.append("| Metric | Value |")
        md.append("| :--- | :--- |")
        md.append(f"| **Total PDFs Discovered** | {summary.total_pdfs_discovered} |")
        md.append(f"| **PDFs Expected from Manifest** | {summary.total_pdfs_expected_from_manifest} |")
        md.append(f"| **Manifest Mismatches** | {len(summary.manifest_mismatches)} |")
        md.append(f"| **Successfully Processed PDFs** | {summary.successfully_processed_pdfs} |")
        md.append(f"| **Failed PDFs** | {summary.failed_pdfs} |")
        md.append(f"| **Skipped Unchanged PDFs** | {summary.skipped_unchanged_pdfs} |")
        md.append(f"| **Total Pages Processed** | {summary.total_pages} |")
        md.append(f"| **Pages Extracted** | {summary.pages_extracted} |")
        md.append(f"| **Pages Needing OCR** | {summary.pages_needing_ocr} |")
        md.append(f"| **Low Quality Pages** | {summary.low_quality_pages} |")
        md.append(f"| **Total Math Pages Detected** | {summary.total_math_pages} |")
        md.append(f"| **Math-Heavy Pages** | {summary.total_math_heavy_pages} |")
        md.append(f"| **Corrupted Math Chunks (Blocked from RAG)** | {summary.total_corrupted_math_chunks} |")
        md.append(f"| **Chapters Detected** | {summary.chapters_detected} |")
        md.append(f"| **Topics Detected** | {summary.topics_detected} |")
        md.append(f"| **Ambiguous Topics** | {summary.ambiguous_topics} |")
        md.append(f"| **Chunks Generated** | {summary.chunks_generated} |")
        md.append(f"| **LearningContent Inserted** | {summary.chunks_inserted} |")
        md.append(f"| **Duplicate Chunks Skipped** | {summary.duplicate_chunks_skipped} |")

        if summary.manifest_mismatches:
            md.append("\n## Manifest Mismatches\n")
            for mismatch in summary.manifest_mismatches:
                md.append(f"- {mismatch}")

        if summary.document_diagnostics:
            md.append("\n## Per-Document Diagnostics\n")
            md.append("| Document | Pages | Extracted | OCR Req | Low Qual | Chapters | Topics | Chunks | Inserts | Status |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for diag in summary.document_diagnostics:
                md.append(
                    f"| `{diag.filename}` | {diag.total_pages} | {diag.extracted_pages} | "
                    f"{diag.ocr_required_pages} | {diag.low_quality_pages} | {diag.chapters_detected} | "
                    f"{diag.topics_detected} | {diag.chunks_generated} | {diag.chunks_inserted} | "
                    f"**{diag.status}** |"
                )

        if summary.warnings:
            md.append("\n## Warnings\n")
            for w in summary.warnings:
                md.append(f"- ⚠️ {w}")

        if summary.errors:
            md.append("\n## Errors\n")
            for e in summary.errors:
                md.append(f"- ❌ {e}")

        md.append("\n---\n*Report compiled deterministically by EduNavika Milestone 2 Ingestion Validator.*\n")
        return "\n".join(md)


class TuplePaths:
    def __init__(self, json_path: Path, md_path: Path):
        self.json_path = json_path
        self.md_path = md_path
