import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')
import json
import pypdfium2 as pdfium
from backend.app.ingestion.math.evaluator import MathEvaluator
from backend.app.ingestion.math.normalizer import CanonicalLaTeXNormalizer
from backend.app.ingestion.math.targeted_extractor import TargetedMathExtractor

with open("data/processed/reports/math_ground_truth_test.json", "r", encoding="utf-8") as f:
    test_gt = json.load(f)

extractor = TargetedMathExtractor()
evaluator = MathEvaluator("data/processed/reports/math_ground_truth_test.json")
normalizer = CanonicalLaTeXNormalizer()

# Target types:
# 1. Fraction: Page 67 S_n = n/2[2a + (n-1)d] or Page 119 midpoint
# 2. Radical: Page 35 x^2 - 3 = (x - \sqrt{3})(x + \sqrt{3})
# 3. Superscript: Page 35 (x^2)
# 4. Subscript: Page 140 a_n = a + (n-1)d
# 5. Trigonometric: Page 43 \sin \theta
# 6. Geometry: Page 132 or Page 146
# 7. Physics: Page 186 Q = I t
# 8. Multi-line / long: Page 119
# 9. Difficult/corrupted: Page 40 (triple fraction a1/a2 = b1/b2 = c1/c2)
# 10. Diagnostic: Page 18 (chemical reaction 3Fe + 4H2O -> Fe3O4 + 4H2) or Page 40 (numeric 4+5=9)

selected_targets = [
    {"label": "1. FRACTION", "page": 67, "item_idx": 0},
    {"label": "2. RADICAL", "page": 35, "item_idx": 0},
    {"label": "3. SUPERSCRIPT", "page": 35, "item_idx": 0},
    {"label": "4. SUBSCRIPT", "page": 140, "item_idx": 0},
    {"label": "5. TRIGONOMETRIC", "page": 43, "item_idx": 0},
    {"label": "6. GEOMETRY", "page": 119, "item_idx": 0},
    {"label": "7. PHYSICS", "page": 186, "item_idx": 0},
    {"label": "8. MULTI-LINE EQUATION", "page": 171, "item_idx": 0},
    {"label": "9. DIFFICULT/CORRUPTED", "page": 40, "item_idx": 0},
    {"label": "10. DIAGNOSTIC (CHEMICAL)", "page": 18, "item_idx": 0},
    {"label": "11. DIAGNOSTIC (NUMERIC)", "page": 40, "item_idx": 1},
]

print("=== STEP 8: REPRESENTATIVE TEST FORMULA MANUAL AUDIT ===")

for t in selected_targets:
    p_num = t["page"]
    page_rec = next((r for r in test_gt if r["page"] == p_num), None)
    if not page_rec:
        continue
    items = page_rec["items"]
    if t["item_idx"] >= len(items):
        continue
    item = items[t["item_idx"]]
    
    doc_name = page_rec["document"]
    pdf_path = os.path.join("GSEB-Dataset", doc_name)
    
    target_res = extractor.extract_page(pdf_path, p_num)
    target_text = target_res.get("text", "")
    
    # Get recovered formula snippet if available
    recovered = target_res.get("recovered_formulas", [])
    rec_latex_list = [r["canonical_latex"] for r in recovered]
    
    eval_res = evaluator.evaluate_formula(target_text, item)
    
    # Baseline text for comparison
    base_text = target_res.get("baseline_text", "")
    
    print(f"\n[{t['label']}] (Doc: {doc_name.split('/')[1][:22]}, Page: {p_num}) Category: {item.get('category')}")
    print(f"  Ground Truth LaTeX: {item['latex']}")
    print(f"  Raw Baseline Text:  {base_text[:80].strip()}...")
    print(f"  Extracted Crop OCR: {' | '.join([r['raw_ocr'] for r in recovered]) if recovered else 'None'}")
    print(f"  Normalized LaTeX:   {' | '.join(rec_latex_list) if rec_latex_list else 'None'}")
    print(f"  Exact Result:       {eval_res.get('exact_match')}")
    print(f"  Structural Result:  {eval_res.get('structural_accuracy')} (Fractions: {eval_res.get('fraction_accuracy')}, Sub/Super: {eval_res.get('subscript_superscript')}, Radical: {eval_res.get('radical_accuracy')})")
    print(f"  Semantic Result:    {eval_res.get('semantic_accuracy')}")
