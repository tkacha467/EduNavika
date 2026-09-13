import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
import json
import pypdfium2 as pdfium
from backend.app.ingestion.math.evaluator import MathEvaluator
from backend.app.ingestion.math.targeted_extractor import TargetedMathExtractor

with open("data/processed/reports/math_ground_truth_test.json", "r", encoding="utf-8") as f:
    gt_test = json.load(f)

extractor = TargetedMathExtractor()
evaluator = MathEvaluator("data/processed/reports/math_ground_truth_test.json")

sample_indices = [0, 4, 6, 8, 14, 21, 40, 58]

print("=" * 80)
print("REPRESENTATIVE FROZEN TEST CASES (TARGETED EXTRACTION)")
print("=" * 80)

for idx in sample_indices:
    page_data = gt_test[idx]
    doc_name = page_data["document"]
    pdf_path = os.path.join("GSEB-Dataset", doc_name)
    page_num = page_data["page"]
    
    target_res = extractor.extract_page(pdf_path, page_num)
    target_text = target_res.get("text", "")
    
    for item in page_data["items"]:
        item_res = evaluator.evaluate_formula(target_text, item)
        print(f"\n[Page {page_num} - {doc_name.split('/')[1][:25]}] Category: {item.get('category')}")
        print(f"  Ground Truth:  {item['latex']}")
        print(f"  Structural:    {item_res.get('structural_accuracy')} | Semantic: {item_res.get('semantic_accuracy')} | Symbol: {item_res.get('symbol_accuracy')}")
        print(f"  Fraction: {item_res.get('fraction_accuracy')} | Sub/Super: {item_res.get('subscript_superscript')} | Radical: {item_res.get('radical_accuracy')}")
