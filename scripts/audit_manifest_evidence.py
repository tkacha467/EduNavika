import json
from pathlib import Path

manifest_path = Path("data/manifests/canonical_curriculum_manifest.json")
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print("=== PARTIAL, TEXTBOOK_ONLY, and HUMAN_REVIEW TOPICS ===")
for std in manifest["standards"]:
    for subj in std["subjects"]:
        for ch in subj["chapters"]:
            for t in ch["topics"]:
                status = t.get("exam_verification_status") or t.get("mapping_status")
print("\n=== SUBJECT-LEVEL EXAM APPLICABILITY BREAKDOWN ===")
subject_counts = {}
for std in manifest["standards"]:
    for subj in std["subjects"]:
        scode = subj["code"]
        if scode not in subject_counts:
            subject_counts[scode] = {"total": 0, "JEE_MAIN": 0, "JEE_ADVANCED": 0, "NEET_UG": 0}
        for ch in subj["chapters"]:
            for t in ch["topics"]:
                subject_counts[scode]["total"] += 1
                status = t.get("exam_verification_status") or t.get("mapping_status")
                if status in ("NEEDS_HUMAN_REVIEW", "UNVERIFIED", "UNRESOLVED", "AMBIGUOUS", "VERIFIED_TEXTBOOK_ONLY"):
                    continue
                for ex in t.get("applicable_exams", []):
                    if ex in subject_counts[scode]:
                        subject_counts[scode][ex] += 1

print(f"{'Subject Code':<14} | {'Total':<6} | {'JEE Main':<10} | {'JEE Adv':<10} | {'NEET UG':<10}")
print("-" * 60)
for scode, counts in sorted(subject_counts.items()):
    print(f"{scode:<14} | {counts['total']:<6} | {counts['JEE_MAIN']:<10} | {counts['JEE_ADVANCED']:<10} | {counts['NEET_UG']:<10}")
