import os
import hashlib
import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from backend.app.ingestion.schemas import DocumentIdentity


def compute_sha256(file_path: Path, buffer_size: int = 65536) -> str:
    """Computes SHA-256 hash of a file using chunked streaming."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def parse_standard_from_grade(grade_str: str) -> int:
    """Parses standard number from grade strings like 'STD-10th', 'STD-9th', 'STD-12th'."""
    match = re.search(r"(\d+)", grade_str)
    if match:
        return int(match.group(1))
    return 10  # Fallback


class DocumentScanner:
    """
    Recursively scans GSEB-Dataset for PDFs, computes deterministic SHA-256 hashes,
    and reconciles them with dataset_manifest.json and dataset_inventory.csv.
    """

    def __init__(self, dataset_dir: Path):
        self.dataset_dir = Path(dataset_dir).resolve()
        self.manifest_path = self.dataset_dir / "dataset_manifest.json"
        self.inventory_path = self.dataset_dir / "dataset_inventory.csv"
        self.manifest_data: Dict[str, Dict] = {}
        self.inventory_data: Dict[str, Dict] = {}
        self._load_authoritative_metadata()

    def _load_authoritative_metadata(self) -> None:
        """Loads dataset_manifest.json and dataset_inventory.csv if present."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    for item in manifest.get("textbooks", []):
                        rel = item.get("relative_path", "").replace("\\", "/").strip().lower()
                        self.manifest_data[rel] = item
                        # Also index by filename as secondary key
                        fn = item.get("filename", "").strip().lower()
                        if fn:
                            self.manifest_data[fn] = item
            except Exception as e:
                print(f"Warning: Failed to load manifest {self.manifest_path}: {e}")

        if self.inventory_path.exists():
            try:
                with open(self.inventory_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rel = row.get("relative_path", "").replace("\\", "/").strip().lower()
                        self.inventory_data[rel] = row
                        fn = row.get("filename", "").strip().lower()
                        if fn:
                            self.inventory_data[fn] = row
            except Exception as e:
                print(f"Warning: Failed to load inventory {self.inventory_path}: {e}")

    def scan(
        self,
        specific_document: Optional[str] = None,
        standard_filter: Optional[int] = None
    ) -> Tuple[List[DocumentIdentity], List[str]]:
        """
        Scans dataset directory, hashes files, matches metadata, and reports mismatches.
        """
        discovered_docs: List[DocumentIdentity] = []
        mismatches: List[str] = []

        if not self.dataset_dir.exists():
            raise FileNotFoundError(f"Dataset directory does not exist: {self.dataset_dir}")

        # 1. Discover physical PDF files
        pdf_paths: List[Path] = []
        if specific_document:
            target = (self.dataset_dir / specific_document).resolve()
            if not target.exists() and Path(specific_document).exists():
                target = Path(specific_document).resolve()
            if not target.exists() or not target.is_file() or target.suffix.lower() != ".pdf":
                raise FileNotFoundError(f"Specific PDF document not found: {specific_document}")
            pdf_paths = [target]
        else:
            for root, _, files in os.walk(self.dataset_dir):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        pdf_paths.append(Path(root) / file)

        pdf_paths.sort()

        # 2. Process each discovered PDF
        seen_manifest_keys = set()

        for path in pdf_paths:
            rel_path = path.relative_to(self.dataset_dir).as_posix()
            norm_rel = rel_path.lower()
            norm_fn = path.name.lower()

            # Lookup metadata in manifest and inventory
            meta = self.manifest_data.get(norm_rel) or self.manifest_data.get(norm_fn)
            inv = self.inventory_data.get(norm_rel) or self.inventory_data.get(norm_fn)

            if meta:
                seen_manifest_keys.add(norm_rel)
                seen_manifest_keys.add(norm_fn)
            else:
                mismatches.append(f"Discovered file not found in manifest: {rel_path}")

            # Compute deterministic hash & document ID
            file_hash = compute_sha256(path)
            doc_id = f"doc_{file_hash[:12]}"
            file_size = path.stat().st_size

            # Determine Standard
            grade_str = (meta.get("grade") if meta else None) or (inv.get("grade") if inv else None)
            if not grade_str:
                # Infer from path (e.g. STD-10th)
                for part in path.parts:
                    if "std-" in part.lower():
                        grade_str = part
                        break
            standard_num = parse_standard_from_grade(grade_str or "STD-10th")

            if standard_filter is not None and standard_num != standard_filter:
                continue

            # Determine Subject
            subject_str = (inv.get("subject") if inv else None) or (meta.get("subject") if meta else None)
            if not subject_str or subject_str.strip() in ["General / Elective", "UNKNOWN"]:
                # Clean up from filename
                clean_name = path.stem.replace("Std-", "").replace("Std_", "").replace("STD-", "").replace("_EnglishMedium", "").replace("_English Medium", "")
                subject_str = clean_name.replace("_", " ").strip()

            category_str = (meta.get("category") if meta else None) or (inv.get("category") if inv else "CORE_TEXTBOOK")
            relevance_str = (meta.get("curriculum_relevance") if meta else None) or (inv.get("curriculum_relevance") if inv else "HIGH")
            ocr_str = (meta.get("ocr_requirement") if meta else None) or (inv.get("ocr_requirement") if inv else "NONE")
            pages_val = (meta.get("num_pages") if meta else None) or (inv.get("num_pages") if inv else None)
            page_count = int(pages_val) if pages_val is not None else None

            doc_identity = DocumentIdentity(
                document_id=doc_id,
                relative_path=rel_path,
                filename=path.name,
                file_hash=file_hash,
                file_size_bytes=file_size,
                standard=standard_num,
                subject=subject_str.strip(),
                category=category_str,
                curriculum_relevance=relevance_str,
                ocr_requirement=ocr_str,
                page_count=page_count,
                manifest_matched=(meta is not None),
            )
            discovered_docs.append(doc_identity)

        # 3. Check for manifest entries missing from disk (when scanning all)
        if not specific_document and standard_filter is None:
            for manifest_rel, item in self.manifest_data.items():
                if "/" in manifest_rel and manifest_rel not in seen_manifest_keys:
                    fn = item.get("filename", "").lower()
        return discovered_docs, mismatches

    def scan_all(self) -> Tuple[List[DocumentIdentity], List[str]]:
        """Alias for scan() with no filters."""
        return self.scan()

    @property
    def manifest_docs(self) -> Dict[str, Dict]:
        return {k: v for k, v in self.manifest_data.items() if "/" in k}

