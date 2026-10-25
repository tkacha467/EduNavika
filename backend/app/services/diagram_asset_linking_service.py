"""
Diagram Asset Linking Service
EduNavika Milestone 5.8 - Manifest-Driven Asset Linking & Verification

Connects extracted vector diagram assets from extraction manifests to
question stems and options for the ingestion pipeline. Enforces strict
path-traversal protection, SHA-256 cryptographic checksum verification,
role-based association (stem vs option), and idempotency.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Canonical approved static asset directory relative to EduNavika repo root
APPROVED_ASSET_PREFIX = "backend/static/assets"
DEFAULT_WEB_URL_PREFIX = "/static"


class AssetLinkingError(Exception):
    """Raised when an asset mapping or integrity violation occurs."""
    pass


class DiagramAssetLinkingService:
    """
    Validates manifest files and links diagram assets to question and option records.
    """

    def __init__(self, repo_root: Optional[Path] = None, approved_asset_root: Optional[Path] = None):
        if repo_root is None:
            # Default to EduSens repo root (two levels up from backend/app/services)
            self.repo_root = Path(__file__).resolve().parent.parent.parent.parent
        else:
            self.repo_root = Path(repo_root).resolve()

        if approved_asset_root is None:
            self.approved_asset_root = (self.repo_root / APPROVED_ASSET_PREFIX).resolve()
        else:
            self.approved_asset_root = Path(approved_asset_root).resolve()

    def validate_manifest_structure(self, manifest: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates the schema and required fields of an extraction manifest.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        if not isinstance(manifest, dict):
            return False, ["Manifest root must be a JSON object"]

        if "manifest_version" not in manifest:
            errors.append("Missing required field 'manifest_version'")

        assets = manifest.get("assets")
        if not isinstance(assets, list):
            errors.append("Manifest must contain an 'assets' list")
            return False, errors

        required_asset_fields = [
            "asset_id",
            "exam_code",
            "exam_year",
            "paper_code",
            "question_number",
            "asset_role",
            "source_pdf_identifier",
            "source_pdf_sha256",
            "output_relative_path",
            "output_sha256",
        ]

        seen_asset_ids = set()
        for idx, asset in enumerate(assets):
            if not isinstance(asset, dict):
                errors.append(f"Asset at index {idx} must be a JSON object")
                continue

            for field in required_asset_fields:
                if field not in asset or asset[field] is None:
                    errors.append(f"Asset at index {idx} ({asset.get('asset_id', 'unknown')}) missing required field: {field}")

            asset_id = asset.get("asset_id")
            if asset_id:
                if asset_id in seen_asset_ids:
                    errors.append(f"Duplicate asset_id in manifest: {asset_id}")
                seen_asset_ids.add(asset_id)

            role = asset.get("asset_role")
            if role not in ("stem", "option"):
                errors.append(f"Asset {asset_id}: invalid asset_role '{role}'. Must be 'stem' or 'option'")

            if role == "option":
                opt_key = asset.get("option_key")
                if not opt_key or str(opt_key).strip() == "":
                    errors.append(f"Asset {asset_id}: asset_role is 'option' but 'option_key' is missing or empty")

        return len(errors) == 0, errors

    def resolve_and_verify_asset_path(self, relative_path: str) -> Tuple[bool, Optional[Path], Optional[str]]:
        """
        Validates that an asset relative path resides strictly within the approved asset directory,
        rejecting path traversal sequences and absolute paths.
        Returns (is_safe, resolved_path, error_message).
        """
        if not relative_path or not isinstance(relative_path, str):
            return False, None, "Asset path must be a non-empty string"

        # Reject path traversal tokens
        normalized_str = relative_path.replace("\\", "/")
        if ".." in normalized_str or normalized_str.startswith("/"):
            return False, None, f"Security violation: path traversal sequence detected in '{relative_path}'"

        target_path = (self.repo_root / relative_path).resolve()

        # Enforce boundary check against approved asset root
        try:
            target_path.relative_to(self.approved_asset_root)
        except ValueError:
            return False, None, (
                f"Security violation: resolved path '{target_path}' is outside approved asset root "
                f"'{self.approved_asset_root}'"
            )

        return True, target_path, None

    def verify_asset_checksum(self, asset_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Verifies that the target file exists on disk and its SHA-256 matches the manifest checksum.
        """
        rel_path = asset_dict.get("output_relative_path", "")
        expected_sha = asset_dict.get("output_sha256", "").lower().strip()

        is_safe, file_path, err = self.resolve_and_verify_asset_path(rel_path)
        if not is_safe or file_path is None:
            return False, err

        if not file_path.is_file():
            return False, f"Asset file not found on disk at: {file_path}"

        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        actual_sha = hasher.hexdigest().lower()

        if actual_sha != expected_sha:
            return False, (
                f"Checksum mismatch for asset '{asset_dict.get('asset_id')}': "
                f"expected {expected_sha}, got {actual_sha}"
            )

        return True, None

    def convert_path_to_web_url(self, relative_path: str, url_prefix: str = DEFAULT_WEB_URL_PREFIX) -> str:
        """
        Converts a repository-relative path inside backend/static to a web-accessible static URL.
        Example: 'backend/static/assets/diagrams/neet_2021/q4.png' -> '/static/assets/diagrams/neet_2021/q4.png'
        """
        norm = relative_path.replace("\\", "/").strip("/")
        if norm.startswith("backend/static/"):
            norm = norm[len("backend/static/"):]
        elif norm.startswith("static/"):
            norm = norm[len("static/"):]
        return f"{url_prefix.rstrip('/')}/{norm}"

    def build_asset_index(
        self,
        manifest: Dict[str, Any],
        verify_checksums: bool = True,
    ) -> Tuple[Dict[Tuple[str, int, str, int], Dict[str, Any]], List[str]]:
        """
        Parses manifest and returns a mapping:
        (exam_code, exam_year, paper_code, question_number) -> {
            "stem": asset_dict or None,
            "options": { "A": asset_dict, "B": ... },
            "all_assets": [asset_dict, ...],
        }
        along with any validation or integrity errors encountered.
        """
        errors = []
        is_valid, schema_errors = self.validate_manifest_structure(manifest)
        if not is_valid:
            return {}, schema_errors

        index: Dict[Tuple[str, int, str, int], Dict[str, Any]] = {}

        for asset in manifest.get("assets", []):
            asset_id = asset.get("asset_id")
            key = (
                asset["exam_code"].upper(),
                int(asset["exam_year"]),
                str(asset["paper_code"]).upper(),
                int(asset["question_number"]),
            )

            if verify_checksums:
                ok, c_err = self.verify_asset_checksum(asset)
                if not ok:
                    errors.append(f"Asset '{asset_id}': {c_err}")
                    continue

            if key not in index:
                index[key] = {
                    "stem": None,
                    "options": {},
                    "all_assets": [],
                }

            role = asset["asset_role"]
            if role == "stem":
                if index[key]["stem"] is not None:
                    errors.append(
                        f"Conflicting stem diagram assets for question {key}: "
                        f"'{index[key]['stem']['asset_id']}' vs '{asset_id}'"
                    )
                else:
                    index[key]["stem"] = asset
            elif role == "option":
                opt_key = str(asset.get("option_key", "")).strip().upper()
                if opt_key in index[key]["options"]:
                    errors.append(
                        f"Conflicting option '{opt_key}' diagram assets for question {key}: "
                        f"'{index[key]['options'][opt_key]['asset_id']}' vs '{asset_id}'"
                    )
                else:
                    index[key]["options"][opt_key] = asset

            index[key]["all_assets"].append(asset)

        return index, errors

    def link_assets_to_question(
        self,
        question_dict: Dict[str, Any],
        exam_code: str,
        exam_year: int,
        paper_code: str,
        asset_index: Dict[Tuple[str, int, str, int], Dict[str, Any]],
        url_prefix: str = DEFAULT_WEB_URL_PREFIX,
    ) -> Dict[str, Any]:
        """
        Pure function: attaches diagram_asset_url to the question dictionary and its options
        if matching validated assets exist in the asset index.
        Returns linking summary with status.
        """
        q_num = question_dict.get("paper_question_number") or question_dict.get("question_number")
        if q_num is None:
            return {
                "linked": False,
                "reason": "Missing question_number in question data",
                "stem_linked": False,
                "options_linked_count": 0,
            }

        key = (exam_code.upper(), int(exam_year), str(paper_code).upper(), int(q_num))
        assets_for_q = asset_index.get(key)

        if not assets_for_q:
            return {
                "linked": False,
                "reason": f"No assets registered for question {key}",
                "stem_linked": False,
                "options_linked_count": 0,
            }

        stem_linked = False
        stem_asset = assets_for_q.get("stem")
        if stem_asset:
            rel_path = stem_asset["output_relative_path"]
            web_url = self.convert_path_to_web_url(rel_path, url_prefix=url_prefix)
            question_dict["diagram_asset_url"] = web_url
            question_dict["stem_asset_id"] = stem_asset.get("asset_id")
            stem_linked = True

        options_linked_count = 0
        opt_assets = assets_for_q.get("options", {})
        if opt_assets and "options" in question_dict:
            for opt in question_dict["options"]:
                opt_key = str(opt.get("option_key", "")).strip().upper()
                if opt_key in opt_assets:
                    matched_asset = opt_assets[opt_key]
                    rel_path = matched_asset["output_relative_path"]
                    web_url = self.convert_path_to_web_url(rel_path, url_prefix=url_prefix)
                    opt["diagram_asset_url"] = web_url
                    opt["asset_id"] = matched_asset.get("asset_id")
                    options_linked_count += 1

        return {
            "linked": stem_linked or (options_linked_count > 0),
            "stem_linked": stem_linked,
            "options_linked_count": options_linked_count,
            "total_assets_available": len(assets_for_q.get("all_assets", [])),
        }
