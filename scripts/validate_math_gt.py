"""
Milestone 4.3.2: Math Ground Truth Integrity Validator
Enforces 14 structural, domain, and cryptographic invariants on the ground truth datasets.
"""

import os
import sys
import json
import hashlib
import pymupdf

def validate_math_gt():
    gt_dir = "data/processed/reports"
    master_path = os.path.join(gt_dir, "math_ground_truth.json")
    dev_path = os.path.join(gt_dir, "math_ground_truth_dev.json")
    test_path = os.path.join(gt_dir, "math_ground_truth_test.json")
    manifest_path = os.path.join(gt_dir, "test_manifest.json")

    print("Running Milestone 4.3.2 Ground Truth Validation...")
    errors = []

    # Check 0: File existence
    for p in [master_path, dev_path, test_path, manifest_path]:
        if not os.path.exists(p):
            errors.append(f"Missing required file: {p}")
    if errors:
        for err in errors:
            print(f"FAIL: {err}")
        return False

    with open(master_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)
    with open(dev_path, "r", encoding="utf-8") as f:
        dev_data = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    # 1. Total formula items >= 100
    all_items = [it for r in master_data for it in r.get("items", [])]
    if len(all_items) < 100:
        errors.append(f"Invariant 1 Failed: Formula count {len(all_items)} < 100")
    else:
        print(f"PASS Invariant 1: Formula count = {len(all_items)} (>= 100)")

    # 2. Total unique pages >= 80
    unique_pages = set((r["document"], r["page"]) for r in master_data)
    if len(unique_pages) < 80:
        errors.append(f"Invariant 2 Failed: Unique pages {len(unique_pages)} < 80")
    else:
        print(f"PASS Invariant 2: Unique pages = {len(unique_pages)} (>= 80)")

    # 3. >= 50 dev formulas and >= 50 test formulas
    dev_items = [it for r in dev_data for it in r.get("items", [])]
    test_items = [it for r in test_data for it in r.get("items", [])]
    if len(dev_items) < 50:
        errors.append(f"Invariant 3 Failed: DEV formula count {len(dev_items)} < 50")
    if len(test_items) < 50:
        errors.append(f"Invariant 3 Failed: TEST formula count {len(test_items)} < 50")
    if len(dev_items) >= 50 and len(test_items) >= 50:
        print(f"PASS Invariant 3: DEV formulas = {len(dev_items)}, TEST formulas = {len(test_items)} (both >= 50)")

    # 4. No duplicate formula IDs
    seen_ids = set()
    dup_ids = set()
    for it in all_items:
        fid = it.get("id")
        if fid in seen_ids:
            dup_ids.add(fid)
        seen_ids.add(fid)
    if dup_ids:
        errors.append(f"Invariant 4 Failed: Duplicate formula IDs found: {dup_ids}")
    else:
        print("PASS Invariant 4: Zero duplicate formula IDs")

    # 5. No duplicate (document, page, item_id)
    seen_keys = set()
    dup_keys = set()
    for r in master_data:
        doc = r["document"]
        p = r["page"]
        for it in r.get("items", []):
            key = (doc, p, it.get("id"))
            if key in seen_keys:
                dup_keys.add(key)
            seen_keys.add(key)
    if dup_keys:
        errors.append(f"Invariant 5 Failed: Duplicate (document, page, item_id) keys: {dup_keys}")
    else:
        print("PASS Invariant 5: Benchmark unique key (document, page, item_id) verified")

    # 6. Physical document existence & page bounds
    cached_docs = {}
    for r in master_data:
        rel_path = r["document"]
        full_path = os.path.join("GSEB-Dataset", rel_path)
        if not os.path.exists(full_path):
            errors.append(f"Invariant 6 Failed: Document {full_path} not found on disk")
            continue
        if full_path not in cached_docs:
            try:
                cached_docs[full_path] = len(pymupdf.open(full_path))
            except Exception as e:
                errors.append(f"Invariant 6 Failed: Error opening {full_path}: {e}")
                continue
        max_p = cached_docs[full_path]
        if r["page"] < 1 or r["page"] > max_p:
            errors.append(f"Invariant 6 Failed: Page {r['page']} out of bounds for {rel_path} (1..{max_p})")
    print(f"PASS Invariant 6: All document paths exist and pages are within physical PDF bounds")

    # 7. Valid non-empty chapter
    empty_chapters = [r for r in master_data if not r.get("chapter")]
    if empty_chapters:
        errors.append(f"Invariant 7 Failed: {len(empty_chapters)} records have empty chapter")
    else:
        print(f"PASS Invariant 7: All records have non-empty chapter annotations")

    # 8. Valid category taxonomy
    valid_categories = {"ALGEBRA", "GEOMETRY", "TRIGONOMETRY", "PHYSICS", "CHEMICAL", "NUMERIC_EXPRESSION"}
    invalid_cats = [it for it in all_items if it.get("category") not in valid_categories]
    if invalid_cats:
        errors.append(f"Invariant 8 Failed: Invalid categories found: {[it.get('category') for it in invalid_cats]}")
    else:
        print(f"PASS Invariant 8: 100% of formulas mapped to valid categories")

    # 9. Valid split values
    invalid_splits = [r for r in master_data if r.get("split") not in ("dev", "test")]
    if invalid_splits:
        errors.append(f"Invariant 9 Failed: {len(invalid_splits)} records have invalid split")
    else:
        print(f"PASS Invariant 9: All split tags are 'dev' or 'test'")

    # 10. Strict page-level split isolation
    dev_pages = set((r["document"], r["page"]) for r in dev_data)
    test_pages = set((r["document"], r["page"]) for r in test_data)
    overlap = dev_pages.intersection(test_pages)
    if overlap:
        errors.append(f"Invariant 10 Failed: Page overlap between DEV and TEST: {overlap}")
    else:
        print(f"PASS Invariant 10: Strict page-level split isolation (0 page overlap)")

    # 11. Core categories represented in both splits
    core_cats = {"ALGEBRA", "GEOMETRY", "TRIGONOMETRY", "PHYSICS"}
    dev_core = set(it["category"] for it in dev_items if it["category"] in core_cats)
    test_core = set(it["category"] for it in test_items if it["category"] in core_cats)
    if dev_core != core_cats:
        errors.append(f"Invariant 11 Failed: DEV missing core categories: {core_cats - dev_core}")
    if test_core != core_cats:
        errors.append(f"Invariant 11 Failed: TEST missing core categories: {core_cats - test_core}")
    if dev_core == core_cats and test_core == core_cats:
        print(f"PASS Invariant 11: All 4 core categories present in both DEV and TEST")

    # 12. Valid non-empty LaTeX
    empty_latex = [it for it in all_items if not it.get("latex") or len(it["latex"].strip()) == 0]
    if empty_latex:
        errors.append(f"Invariant 12 Failed: {len(empty_latex)} items have empty LaTeX")
    else:
        print(f"PASS Invariant 12: 100% of formulas have non-empty LaTeX strings")

    # 13. Structural flag consistency checks
    flag_inconsistencies = []
    for it in all_items:
        lx = it.get("latex", "")
        if it.get("has_fraction") and "\\frac" not in lx and "/" not in lx:
            flag_inconsistencies.append((it["id"], "has_fraction is True but no fraction found in latex"))
        if it.get("has_superscript") and "^" not in lx and "²" not in lx and "³" not in lx:
            flag_inconsistencies.append((it["id"], "has_superscript is True but no ^ found in latex"))
        if it.get("has_subscript") and "_" not in lx and "₁" not in lx and "₂" not in lx:
            flag_inconsistencies.append((it["id"], "has_subscript is True but no _ found in latex"))
    if flag_inconsistencies:
        errors.append(f"Invariant 13 Failed: {len(flag_inconsistencies)} structural flag inconsistencies: {flag_inconsistencies[:3]}")
    else:
        print("PASS Invariant 13: Structural flags are fully consistent with LaTeX markup")

    # 14. Test manifest cryptographic SHA-256 match
    with open(test_path, "rb") as f:
        actual_test_hash = hashlib.sha256(f.read()).hexdigest()
    manifest_hash = manifest_data.get("sha256")
    if actual_test_hash != manifest_hash:
        errors.append(f"Invariant 14 Failed: Test file hash {actual_test_hash} != manifest hash {manifest_hash}")
    else:
        print(f"PASS Invariant 14: Test manifest SHA-256 verified ({actual_test_hash})")

    if errors:
        print(f"\nVALIDATION FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  ❌ {err}")
        return False

    print("\n==================================================")
    print("ALL 14 GROUND TRUTH INVARIANTS PASSED SUCCESSFULLY!")
    print("==================================================")
    return True

if __name__ == "__main__":
    success = validate_math_gt()
    sys.exit(0 if success else 1)
