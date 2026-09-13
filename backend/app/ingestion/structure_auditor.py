import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

from backend.app.ingestion.schemas import ChapterCandidate, CleanedPage, PageQualityStatus
from backend.app.ingestion.cleaner import DeterministicCleaner
from backend.app.ingestion.structure import StructureParser
import pypdf


class AuditedDocumentStructure(BaseModel):
    document_name: str
    relative_path: str
    expected_chapters: int
    detected_chapters: int
    expected_topics_approx: str
    detected_topics: int
    status: str  # PASS, REVIEW, FAIL
    diagnostic_notes: List[str]
    chapters: List[Dict[str, Any]]


class StructureAuditReport(BaseModel):
    total_audited: int
    passed_count: int
    review_count: int
    failed_count: int
    documents: List[AuditedDocumentStructure]


class StructureAuditor:
    """
    Performs Phase 5: Structure Audit.
    Compares textbook ground-truth Table of Contents against parser-detected chapters & topics.
    Validates page range continuity and detects under-detection / over-detection.
    """

    def __init__(self, dataset_dir: Path, output_dir: Path = Path("data/processed/reports")):
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cleaner = DeterministicCleaner()
        self.parser = StructureParser()

    def audit_representative_books(self) -> StructureAuditReport:
        # Define representative test set across subjects and standards
        test_books = [
            {
                "name": "Std-10 Science",
                "rel_path": "STD-10/Std-10_Science_English Medium.pdf",
                "expected_chapters": 13,
                "expected_topics_str": "~15-25",
            },
            {
                "name": "Std-10 First Flight English",
                "rel_path": "STD-10/Std-10_First Flight_EnglishMedium.pdf",
                "expected_chapters": 9,
                "expected_topics_str": "~9-15",
            },
            {
                "name": "Std-10 Mathematics",
                "rel_path": "STD-10/Std-10_Maths_EnglishMedium.pdf",
                "expected_chapters": 14,
                "expected_topics_str": "~35-50",
            },
        ]

        audited_docs: List[AuditedDocumentStructure] = []

        for book in test_books:
            full_path = self.dataset_dir / book["rel_path"]
            if not full_path.exists():
                continue

            cpages: List[CleanedPage] = []
            use_pypdf = False
            try:
                import pypdfium2 as pdfium
                doc = pdfium.PdfDocument(str(full_path))
                sample = "".join(doc[i].get_textpage().get_text_range() or "" for i in range(min(12, len(doc))))
                alpha = sum(1 for c in sample if c.isalpha()) / max(1, len(sample))
                if alpha < 0.25:
                    use_pypdf = True
                else:
                    for i in range(min(25, len(doc))):
                        raw = doc[i].get_textpage().get_text_range() or ""
                        cleaned, _, _ = self.cleaner.clean_text(raw)
                        cpages.append(
                            CleanedPage(
                                document_id="audit_doc",
                                pdf_page_number=i + 1,
                                cleaned_text=cleaned,
                                quality_status=PageQualityStatus.EXTRACTED,
                            )
                        )
            except Exception:
                use_pypdf = True

            if use_pypdf:
                reader = pypdf.PdfReader(str(full_path))
                for i in range(min(25, len(reader.pages))):
                    raw = reader.pages[i].extract_text() or ""
                    cleaned, _, _ = self.cleaner.clean_text(raw)
                    cpages.append(
                        CleanedPage(
                            document_id="audit_doc",
                            pdf_page_number=i + 1,
                            cleaned_text=cleaned,
                            quality_status=PageQualityStatus.EXTRACTED,
                        )
                    )

            detected_chs = self.parser.parse_structure(cpages)
            det_ch_count = len(detected_chs)
            det_top_count = sum(len(c.topics) for c in detected_chs)

            notes: List[str] = []
            exp_ch = book["expected_chapters"]

            # Evaluate match
            if det_ch_count == exp_ch:
                status = "PASS"
                notes.append(f"Exact chapter count match: {det_ch_count}/{exp_ch} chapters detected.")
            elif abs(det_ch_count - exp_ch) <= 1:
                status = "PASS"
                notes.append(f"Near-exact chapter count: {det_ch_count} detected (expected {exp_ch}).")
            elif det_ch_count > 1 and det_ch_count >= exp_ch * 0.7:
                status = "REVIEW"
                notes.append(f"Partial chapter detection: {det_ch_count} detected (expected {exp_ch}).")
            else:
                status = "FAIL"
                notes.append(f"Severe under-detection: {det_ch_count} detected (expected {exp_ch}).")

            # Page continuity check
            prev_end = 0
            for c in detected_chs:
                if c.start_pdf_page > c.end_pdf_page:
                    status = "REVIEW"
                    notes.append(f"Chapter {c.chapter_number} invalid bounds: {c.start_pdf_page} > {c.end_pdf_page}")
                if prev_end > 0 and c.start_pdf_page < prev_end:
                    status = "REVIEW"
                    notes.append(f"Chapter {c.chapter_number} overlaps preceding chapter ({c.start_pdf_page} < {prev_end})")
                prev_end = c.end_pdf_page

            ch_summaries = [
                {
                    "chapter_number": c.chapter_number,
                    "chapter_title": c.chapter_title,
                    "pages": f"pp. {c.start_pdf_page}-{c.end_pdf_page}",
                    "topics_count": len(c.topics),
                }
                for c in detected_chs
            ]

            audited_docs.append(
                AuditedDocumentStructure(
                    document_name=book["name"],
                    relative_path=book["rel_path"],
                    expected_chapters=exp_ch,
                    detected_chapters=det_ch_count,
                    expected_topics_approx=book["expected_topics_str"],
                    detected_topics=det_top_count,
                    status=status,
                    diagnostic_notes=notes,
                    chapters=ch_summaries,
                )
            )

        passed = sum(1 for d in audited_docs if d.status == "PASS")
        review = sum(1 for d in audited_docs if d.status == "REVIEW")
        failed = sum(1 for d in audited_docs if d.status == "FAIL")

        report = StructureAuditReport(
            total_audited=len(audited_docs),
            passed_count=passed,
            review_count=review,
            failed_count=failed,
            documents=audited_docs,
        )

        self._write_report(report)
        return report

    def _write_report(self, report: StructureAuditReport):
        json_path = self.output_dir / "structure_audit.json"
        md_path = self.output_dir / "structure_audit.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json"), f, indent=2)

        md = []
        md.append("# EduNavika — Milestone 2.5: Structure Audit Report\n")
        md.append("## Executive Summary\n")
        md.append("| Metric | Value |")
        md.append("| :--- | :--- |")
        md.append(f"| **Documents Audited** | {report.total_audited} |")
        md.append(f"| **PASS Count** | {report.passed_count} |")
        md.append(f"| **REVIEW Count** | {report.review_count} |")
        md.append(f"| **FAIL Count** | {report.failed_count} |")

        md.append("\n## Document Structure Audit Table\n")
        md.append("| Document | Expected Chs | Detected Chs | Exp Topics | Det Topics | Status |")
        md.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
        for doc in report.documents:
            md.append(
                f"| `{doc.document_name}` | {doc.expected_chapters} | {doc.detected_chapters} | "
                f"{doc.expected_topics_approx} | {doc.detected_topics} | **{doc.status}** |"
            )

        md.append("\n## Detailed Document Diagnostics\n")
        for doc in report.documents:
            md.append(f"### {doc.document_name} (`{doc.status}`)\n")
            for note in doc.diagnostic_notes:
                md.append(f"- {note}")
            md.append("\n**Detected Chapters:**\n")
            for ch in doc.chapters:
                md.append(f"- Ch {ch['chapter_number']}: {ch['chapter_title']} ({ch['pages']}) — {ch['topics_count']} topics")
            md.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
