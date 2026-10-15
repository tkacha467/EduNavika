"""
EduNavika Milestone 4 — Textbook Corpus Inspection Script.
Calculates SHA-256 hashes, page counts, and structural metadata for the 13 preserved science textbooks.
"""

import hashlib
from pathlib import Path
from pypdf import PdfReader

TEXTBOOK_FILES = [
    # Std 11 Science (6 files)
    ("GSEB-Dataset/STD-11th/SCIENCE/Std-11_Physics Part 1_English Medium.pdf", 11, "Physics", "Part 1"),
    ("GSEB-Dataset/STD-11th/SCIENCE/Std-11_Physics Part 2_English Medium.pdf", 11, "Physics", "Part 2"),
    ("GSEB-Dataset/STD-11th/SCIENCE/Std-11_Chemistry Part-1_English Medium.pdf", 11, "Chemistry", "Part 1"),
    ("GSEB-Dataset/STD-11th/SCIENCE/Std-11_Chemistry Part-2_English Medium.pdf", 11, "Chemistry", "Part 2"),
    ("GSEB-Dataset/STD-11th/SCIENCE/Std-11_Maths_EnglishMedium.pdf", 11, "Mathematics", "Single Volume"),
    ("GSEB-Dataset/STD-11th/SCIENCE/Std-11_Bilology_EnglishMedium.pdf", 11, "Biology", "Single Volume"),

    # Std 12 Science (7 files)
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12_Physics Part-1_English Medium.pdf", 12, "Physics", "Part 1"),
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12_Physics Part-2_English Medium.pdf", 12, "Physics", "Part 2"),
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12_Chemistry Part-1_EnglishMedium.pdf", 12, "Chemistry", "Part 1"),
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12 Chemistry Part-2_EnglishMedium.pdf", 12, "Chemistry", "Part 2"),
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12_Maths-Part1_EnglishMedium.pdf", 12, "Mathematics", "Part 1"),
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12_Maths-Part2_EnglishMedium.pdf", 12, "Mathematics", "Part 2"),
    ("GSEB-Dataset/STD-12th/SCIENCE/Std-12_Biology_EnglishMedium.pdf", 12, "Biology", "Single Volume"),
]

def inspect_corpus():
    print(f"{'Filename':<45} | {'Std':<4} | {'Subject':<12} | {'Pages':<6} | {'Size (MB)':<10} | {'SHA-256 (first 16)'}")
    print("-" * 105)

    for rel_path, std, subj, part in TEXTBOOK_FILES:
        p = Path(rel_path)
        assert p.exists(), f"File missing: {p}"
        size_mb = round(p.stat().st_size / (1024 * 1024), 2)

        # Hash
        h = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        sha = h.hexdigest()

        # Pages
        reader = PdfReader(str(p))
        pages = len(reader.pages)

        print(f"{p.name:<45} | {std:<4} | {subj:<12} | {pages:<6} | {size_mb:<10} | {sha[:16]}...")

if __name__ == "__main__":
    inspect_corpus()
