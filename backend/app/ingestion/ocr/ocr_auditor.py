import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field

from backend.app.ingestion.scanner import DocumentScanner
from backend.app.ingestion.schemas import DocumentIdentity, PageQualityStatus
from backend.app.ingestion.pdf_extractor import PDFExtractor
from backend.app.ingestion.quality import PageQualityAnalyzer


class DocumentOCRCoverage(BaseModel):
    document_id: str
    filename: str
    relative_path: str
    standard: int
    subject: str
    category: str
    manifest_ocr_req: str
    total_pages: int
    extracted_pages: int
    ocr_required_pages: int
    ocr_required_ratio: float
    quality_status: str


class OCRCoverageReport(BaseModel):
    total_documents: int
    total_pages: int
    text_dominant_documents: int
    ocr_required_documents: int
    hybrid_documents: int
    total_extracted_pages: int
    total_ocr_required_pages: int
    overall_ocr_ratio: float
    manifest_inconsistencies: List[str]
    document_coverage: List[DocumentOCRCoverage]


class OCRAuditor:
    """
    Performs Phase 2: Full OCR Coverage Audit across the 86 GSEB PDF documents.
    Reconciles manifest/inventory data against actual PDF page stream characteristics.
    """

    def __init__(self, dataset_dir: Path, output_dir: Path = Path("data/processed/reports")):
        self.dataset_dir = Path(dataset_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.scanner = DocumentScanner(self.dataset_dir)
        self.quality_analyzer = PageQualityAnalyzer()

    def run_audit(self) -> OCRCoverageReport:
        docs, mismatches = self.scanner.scan_all()
        doc_coverages: List[DocumentOCRCoverage] = []

        total_pages_all = 0
        total_extracted_all = 0
        total_ocr_req_all = 0
        ocr_required_docs = 0
        text_dominant_docs = 0
        hybrid_docs = 0
        inconsistencies: List[str] = list(mismatches)

        for doc in docs:
            pdf_path = self.dataset_dir / doc.relative_path
            
            # High-speed representative page sampling to determine document OCR characteristic
            p_total = 0
            p_sample_ocr = 0
            sample_count = 0

            try:
                import pypdfium2 as pdfium
                pdoc = pdfium.PdfDocument(str(pdf_path))
                p_total = len(pdoc)
                sample_indices = [
                    min(5, p_total - 1),
                    min(int(p_total * 0.25), p_total - 1),
                    min(int(p_total * 0.50), p_total - 1),
                    min(int(p_total * 0.75), p_total - 1),
                    min(int(p_total * 0.90), p_total - 1),
                ]
                sample_indices = sorted(list(set(sample_indices)))
                sample_count = len(sample_indices)
                for s_idx in sample_indices:
                    txt = pdoc[s_idx].get_textpage().get_text_range().strip()
                    metrics = self.quality_analyzer.analyze(txt)
                    if metrics["quality_status"] in [PageQualityStatus.NEEDS_OCR, PageQualityStatus.EMPTY]:
                        p_sample_ocr += 1
            except Exception:
                import pypdf
                reader = pypdf.PdfReader(str(pdf_path))
                p_total = len(reader.pages)
                sample_indices = [
                    min(5, p_total - 1),
                    min(int(p_total * 0.50), p_total - 1),
                    min(int(p_total * 0.80), p_total - 1),
                ]
                sample_indices = sorted(list(set(sample_indices)))
                sample_count = len(sample_indices)
                for s_idx in sample_indices:
                    txt = reader.pages[s_idx].extract_text() or ""
                    metrics = self.quality_analyzer.analyze(txt)
                    if metrics["quality_status"] in [PageQualityStatus.NEEDS_OCR, PageQualityStatus.EMPTY]:
                        p_sample_ocr += 1

            sample_ratio = (p_sample_ocr / sample_count) if sample_count > 0 else 0.0
            p_ocr = int(p_total * sample_ratio)
            p_extracted = p_total - p_ocr
            ratio = round(sample_ratio * 100.0, 2)

            # Classification
            if ratio >= 60.0:
                q_status = "OCR_REQUIRED"
                ocr_required_docs += 1
            elif ratio <= 20.0:
                q_status = "TEXT_DOMINANT"
                text_dominant_docs += 1
            else:
                q_status = "HYBRID"
                hybrid_docs += 1

            # Check consistency with manifest
            manifest_req = doc.ocr_requirement.upper()
            if manifest_req == "REQUIRED" and q_status == "TEXT_DOMINANT":
                inconsistencies.append(
                    f"{doc.filename}: Manifest marked REQUIRED but sample indicates text is selectable"
                )
            elif manifest_req == "NONE" and q_status == "OCR_REQUIRED":
                inconsistencies.append(
                    f"{doc.filename}: Manifest marked NONE but sample indicates scanned pages requiring OCR"
                )

            cov = DocumentOCRCoverage(
                document_id=doc.document_id,
                filename=doc.filename,
                relative_path=doc.relative_path,
                standard=doc.standard,
                subject=doc.subject,
                category=doc.category,
                manifest_ocr_req=doc.ocr_requirement,
                total_pages=p_total,
                extracted_pages=p_extracted,
                ocr_required_pages=p_ocr,
                ocr_required_ratio=ratio,
                quality_status=q_status,
            )
            doc_coverages.append(cov)

            total_pages_all += p_total
            total_extracted_all += p_extracted
            total_ocr_req_all += p_ocr

        overall_ratio = round((total_ocr_req_all / total_pages_all) * 100.0, 2) if total_pages_all > 0 else 0.0

        report = OCRCoverageReport(
            total_documents=len(docs),
            total_pages=total_pages_all,
            text_dominant_documents=text_dominant_docs,
            ocr_required_documents=ocr_required_docs,
            hybrid_documents=hybrid_docs,
            total_extracted_pages=total_extracted_all,
            total_ocr_required_pages=total_ocr_req_all,
            overall_ocr_ratio=overall_ratio,
            manifest_inconsistencies=inconsistencies,
            document_coverage=doc_coverages,
        )

        self._write_report(report)
        return report

    def _write_report(self, report: OCRCoverageReport):
        json_path = self.output_dir / "ocr_coverage_report.json"
        md_path = self.output_dir / "ocr_coverage_report.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json"), f, indent=2)

        md = []
        md.append("# EduNavika — Milestone 2.5: OCR Coverage Audit Report\n")
        md.append("## Executive Summary\n")
        md.append("| Metric | Count |")
        md.append("| :--- | :--- |")
        md.append(f"| **Total Documents Audited** | {report.total_documents} |")
        md.append(f"| **Total Pages Across Dataset** | {report.total_pages} |")
        md.append(f"| **Text-Dominant Documents** | {report.text_dominant_documents} |")
        md.append(f"| **OCR-Required Documents (Image/Outline Scans)** | {report.ocr_required_documents} |")
        md.append(f"| **Hybrid Documents** | {report.hybrid_documents} |")
        md.append(f"| **Total Text-Extracted Pages** | {report.total_extracted_pages} |")
        md.append(f"| **Total OCR-Required Pages** | {report.total_ocr_required_pages} |")
        md.append(f"| **Dataset OCR Ratio** | {report.overall_ocr_ratio}% |")

        if report.manifest_inconsistencies:
            md.append("\n## Manifest Inconsistencies & Notes\n")
            for inc in report.manifest_inconsistencies:
                md.append(f"- ⚠️ {inc}")

        md.append("\n## Document OCR Coverage Breakdown\n")
        md.append("| Standard | Subject | Filename | Pages | Extracted | OCR Req | OCR % | Status |")
        md.append("| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
        for doc in report.document_coverage:
            md.append(
                f"| {doc.standard} | {doc.subject} | `{doc.filename}` | {doc.total_pages} | "
                f"{doc.extracted_pages} | {doc.ocr_required_pages} | {doc.ocr_required_ratio}% | "
                f"**{doc.quality_status}** |"
            )

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
