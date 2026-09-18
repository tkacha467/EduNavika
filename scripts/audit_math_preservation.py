import json
import os
from sqlalchemy.orm import joinedload
from backend.app.core.database import SessionLocal
from backend.app.models import LearningContent
from backend.app.models import Topic, Chapter, Subject, Standard

def extract_math_chunks():
    db = SessionLocal()
    
    # We deliberately target Mathematics and Science chunks for M4.1 audit
    chunks = db.query(LearningContent).join(Topic).join(Chapter).join(Subject).join(Standard).filter(
        Subject.name.in_(["Mathematics", "Science & Technology"])
    ).options(
        joinedload(LearningContent.topic)
        .joinedload(Topic.chapter)
        .joinedload(Chapter.subject)
        .joinedload(Subject.standard)
    ).all()
    
    # Filter for chunks containing potential mathematical symbols or terms
    math_indicators = ["x²", "√", "∑", "π", "sin", "cos", "tan", "equation", "formula", "+", "=", "theta", "theorem", "fraction"]
    
    candidate_chunks = []
    for c in chunks:
        text_lower = c.content_text.lower()
        if any(ind in text_lower for ind in math_indicators):
            candidate_chunks.append(c)
            
    # Sample up to 30 chunks for manual audit
    import random
    random.seed(42)
    sampled = random.sample(candidate_chunks, min(30, len(candidate_chunks)))
    
    report_lines = [
        "# Milestone 4.1: Mathematical Preservation Audit",
        "## Rubric",
        "- **PASS**: Mathematical expressions retain their meaning.",
        "- **REVIEW**: Minor formatting issues but semantic meaning remains intact.",
        "- **FAIL**: Expressions are corrupted enough that MCQ generation could produce incorrect mathematics.",
        "\n---"
    ]
    
    for i, c in enumerate(sampled, start=1):
        subject = c.topic.chapter.subject.name if c.topic and c.topic.chapter else "Unknown"
        chapter = c.topic.chapter.title if c.topic and c.topic.chapter else "Unknown"
        
        report_lines.append(f"### Sample {i} [CHUNK_ID: {c.chunk_identifier}]")
        report_lines.append(f"**Subject:** {subject} | **Chapter:** {chapter}")
        report_lines.append(f"**Source Document:** {c.source_document} | **Page:** {c.source_page}")
        report_lines.append("\n**Extracted Content:**")
        report_lines.append("```text")
        report_lines.append(c.content_text.strip())
        report_lines.append("```")
        report_lines.append("**STATUS (PASS/REVIEW/FAIL):** ___________________\n")
        report_lines.append("---\n")
        
    out_path = "data/processed/reports/math_preservation_audit.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    print(f"Generated Mathematical Preservation Audit report with {len(sampled)} samples at {out_path}")

if __name__ == "__main__":
    extract_math_chunks()
