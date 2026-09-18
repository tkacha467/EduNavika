import os
import random
import pymupdf  # PyMuPDF
import pypdf
import pypdfium2 as pdfium
from sqlalchemy.orm import joinedload
from backend.app.core.database import SessionLocal
from backend.app.models import LearningContent
from backend.app.models import Topic, Chapter, Subject, Standard

def get_pypdf_text(pdf_path: str, page_num: int) -> str:
    try:
        reader = pypdf.PdfReader(pdf_path)
        # page_num in our DB is likely 1-indexed based on standard PDF numbering, 
        # but let's assume it's 1-indexed and convert to 0-indexed.
        if page_num > len(reader.pages):
            return "Page out of bounds"
        page = reader.pages[page_num - 1]
        return page.extract_text()
    except Exception as e:
        return f"Error: {e}"

def get_pymupdf_text(pdf_path: str, page_num: int) -> str:
    try:
        doc = pymupdf.open(pdf_path)
        if page_num > len(doc):
            return "Page out of bounds"
        page = doc[page_num - 1]
        return page.get_text()
    except Exception as e:
        return f"Error: {e}"

def get_pypdfium2_text(pdf_path: str, page_num: int) -> str:
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        if page_num > len(pdf):
            return "Page out of bounds"
        page = pdf[page_num - 1]
        textpage = page.get_textpage()
        return textpage.get_text_bounded()
    except Exception as e:
        return f"Error: {e}"

def generate_benchmark():
    db = SessionLocal()
    
    # Recreate the exact same 30 chunks from M4.1
    chunks = db.query(LearningContent).join(Topic).join(Chapter).join(Subject).join(Standard).filter(
        Subject.name.in_(["Mathematics", "Science & Technology"])
    ).options(
        joinedload(LearningContent.topic)
        .joinedload(Topic.chapter)
        .joinedload(Chapter.subject)
        .joinedload(Subject.standard)
    ).all()
    
    math_indicators = ["x²", "√", "∑", "π", "sin", "cos", "tan", "equation", "formula", "+", "=", "theta", "theorem", "fraction"]
    candidate_chunks = []
    for c in chunks:
        if any(ind in c.content_text.lower() for ind in math_indicators):
            candidate_chunks.append(c)
            
    random.seed(42)
    sampled = random.sample(candidate_chunks, min(30, len(candidate_chunks)))
    
    report_lines = [
        "# Milestone 4.1.1: Mathematical Extraction Benchmark",
        "Evaluating PDF extractors on 30 failed math pages to determine semantic preservation.",
        "\n---"
    ]
    
    data_dir = "GSEB-Dataset"
    
    for i, c in enumerate(sampled, start=1):
        pdf_path = os.path.join(data_dir, c.source_document)
        page_num = c.source_page
        
        report_lines.append(f"## Sample {i} [CHUNK_ID: {c.chunk_identifier}]")
        report_lines.append(f"**Document:** {c.source_document} | **Page:** {page_num}\n")
        
        if not os.path.exists(pdf_path):
            report_lines.append(f"*(PDF {pdf_path} not found locally for testing)*\n")
            continue
            
        pypdf_text = get_pypdf_text(pdf_path, page_num)
        pymupdf_text = get_pymupdf_text(pdf_path, page_num)
        pdfium_text = get_pypdfium2_text(pdf_path, page_num)
        
        report_lines.append("### 1. PyMuPDF (fitz)")
        report_lines.append("```text")
        report_lines.append(pymupdf_text.strip())
        report_lines.append("```\n")
        
        report_lines.append("### 2. pypdf (Native)")
        report_lines.append("```text")
        report_lines.append(pypdf_text.strip())
        report_lines.append("```\n")
        
        report_lines.append("### 3. pypdfium2 (Current)")
        report_lines.append("```text")
        report_lines.append(pdfium_text.strip())
        report_lines.append("```\n")
        
        report_lines.append("---\n")
        
    out_path = "data/processed/reports/math_extraction_benchmark.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Generated Benchmark Report at {out_path}")

if __name__ == "__main__":
    generate_benchmark()
