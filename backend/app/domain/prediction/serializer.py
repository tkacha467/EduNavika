import json
import hashlib
import csv
import io
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from backend.app.domain.prediction.schemas import CausalDatasetMatrix
from backend.app.domain.prediction.diagnostics import DatasetDiagnostics


class DatasetSerializer:
    """
    Deterministic dataset serialization and reproducibility packaging engine.
    Ensures identical event sequences produce identical exported tables and hashes.
    """

    @classmethod
    def get_canonical_fieldnames(cls, dataset: CausalDatasetMatrix) -> List[str]:
        """Returns deterministic, fixed order of columns for tabular export."""
        base_columns = [
            "sample_id",
            "student_id",
            "topic_id",
            "cutoff_timestamp",
            "target_event_id",
            "target_timestamp",
            "lead_time_seconds",
            "target_correctness",
            "target_score",
            "target_response_time_ms",
            "target_event_type",
        ]
        if not dataset.samples:
            return base_columns

        # Collect and sort all feature columns deterministically
        sample_dict = dataset.samples[0].to_dict()
        feat_columns = sorted([k for k in sample_dict.keys() if k.startswith("feat_")])
        return base_columns + feat_columns

    @classmethod
    def export_csv_string(cls, dataset: CausalDatasetMatrix) -> str:
        """Serializes dataset to deterministic CSV string."""
        fieldnames = cls.get_canonical_fieldnames(dataset)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()

        # Sort samples deterministically
        sorted_samples = sorted(
            dataset.samples,
            key=lambda s: (s.cutoff_timestamp, s.student_id, s.topic_id, s.target_event_id)
        )

        for s in sorted_samples:
            row = s.to_dict()
            # Ensure None values are written as empty strings
            cleaned_row = {k: (row.get(k) if row.get(k) is not None else "") for k in fieldnames}
            writer.writerow(cleaned_row)

        return output.getvalue()

    @classmethod
    def compute_sha256(cls, content: str) -> str:
        """Computes SHA-256 hexadecimal digest of serialized content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def export_json(
        cls,
        dataset: CausalDatasetMatrix,
        diagnostics: Optional[DatasetDiagnostics] = None,
    ) -> Dict[str, Any]:
        """
        Creates a reproducible dataset package containing diagnostics,
        records, and cryptographic integrity hashes.
        """
        csv_repr = cls.export_csv_string(dataset)
        content_hash = cls.compute_sha256(csv_repr)

        if diagnostics is None:
            diagnostics = DatasetDiagnostics(dataset)

        sorted_samples = sorted(
            dataset.samples,
            key=lambda s: (s.cutoff_timestamp, s.student_id, s.topic_id, s.target_event_id)
        )

        return {
            "metadata": {
                "schema_version": "1.0",
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "content_sha256": content_hash,
                "total_samples": dataset.total_samples,
                "target_name": dataset.target_name,
            },
            "diagnostics": diagnostics.to_dict(),
            "records": [s.to_dict() for s in sorted_samples],
        }
