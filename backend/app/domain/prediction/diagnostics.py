from typing import List, Dict, Any, Optional
from collections import defaultdict
import math

from backend.app.domain.prediction.schemas import CausalDatasetMatrix, DatasetSample


def _percentile(data: List[float], p: float) -> float:
    """Computes p-th percentile (0 <= p <= 100) on sorted list."""
    if not data:
        return 0.0
    sorted_d = sorted(data)
    idx = (len(sorted_d) - 1) * (p / 100.0)
    floor_idx = math.floor(idx)
    ceil_idx = math.ceil(idx)
    if floor_idx == ceil_idx:
        return sorted_d[int(idx)]
    return round(sorted_d[floor_idx] * (ceil_idx - idx) + sorted_d[ceil_idx] * (idx - floor_idx), 4)


def _distribution_stats(counts: List[int]) -> Dict[str, float]:
    """Computes min, max, mean, median for integer counts."""
    if not counts:
        return {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}
    sorted_c = sorted(counts)
    n = len(sorted_c)
    mid = n // 2
    med = float(sorted_c[mid]) if n % 2 == 1 else round((sorted_c[mid - 1] + sorted_c[mid]) / 2.0, 2)
    return {
        "min": float(sorted_c[0]),
        "max": float(sorted_c[-1]),
        "mean": round(sum(sorted_c) / n, 2),
        "median": med,
    }


class DatasetDiagnostics:
    """
    Computes rigorous dataset-quality metrics and diagnostic profiles
    for a CausalDatasetMatrix.
    """

    def __init__(self, dataset: CausalDatasetMatrix):
        self.dataset = dataset
        self.samples = dataset.samples
        self.total_observations: int = len(self.samples)
        self.has_data: bool = self.total_observations > 0

        if not self.has_data:
            self.unique_students = 0
            self.unique_topics = 0
            self.positive_target_count = 0
            self.negative_target_count = 0
            self.class_balance = None
            self.observations_per_student = {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}
            self.observations_per_topic = {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}
            self.lead_time_distribution = {
                "min_sec": 0.0,
                "max_sec": 0.0,
                "mean_sec": 0.0,
                "median_sec": 0.0,
                "p25_sec": 0.0,
                "p75_sec": 0.0,
            }
            self.cold_start_proportion = 0.0
            self.missing_feature_rates: Dict[str, float] = {}
            self.dataset_status_message = (
                "Dataset unavailable because no real longitudinal observations exist yet. "
                "The development DB currently has 0 student events."
            )
            return

        # Entity counts
        student_counts: Dict[str, int] = defaultdict(int)
        topic_counts: Dict[str, int] = defaultdict(int)
        lead_times: List[float] = []
        cold_starts: int = 0
        feature_missing_counts: Dict[str, int] = defaultdict(int)

        pos_count = 0
        neg_count = 0

        for s in self.samples:
            student_counts[s.student_id] += 1
            topic_counts[s.topic_id] += 1
            lead_times.append(s.lead_time_seconds)

            if s.target_correctness == 1:
                pos_count += 1
            else:
                neg_count += 1

            if s.features.is_first_topic_attempt:
                cold_starts += 1

            # Track missingness across all features
            flat_feat = s.features.to_flat_feature_dict()
            for feat_name, feat_val in flat_feat.items():
                if feat_val is None:
                    feature_missing_counts[feat_name] += 1

        self.unique_students = len(student_counts)
        self.unique_topics = len(topic_counts)
        self.positive_target_count = pos_count
        self.negative_target_count = neg_count
        self.class_balance = round(pos_count / self.total_observations, 4)

        self.observations_per_student = _distribution_stats(list(student_counts.values()))
        self.observations_per_topic = _distribution_stats(list(topic_counts.values()))

        # Lead time percentiles
        sorted_leads = sorted(lead_times)
        n_lead = len(sorted_leads)
        mid_lead = n_lead // 2
        med_lead = float(sorted_leads[mid_lead]) if n_lead % 2 == 1 else round((sorted_leads[mid_lead - 1] + sorted_leads[mid_lead]) / 2.0, 4)

        self.lead_time_distribution = {
            "min_sec": round(sorted_leads[0], 4),
            "max_sec": round(sorted_leads[-1], 4),
            "mean_sec": round(sum(sorted_leads) / n_lead, 4),
            "median_sec": med_lead,
            "p25_sec": _percentile(sorted_leads, 25.0),
            "p75_sec": _percentile(sorted_leads, 75.0),
        }

        self.cold_start_proportion = round(cold_starts / self.total_observations, 4)

        # Missing rates
        all_features = list(self.samples[0].features.to_flat_feature_dict().keys())
        self.missing_feature_rates = {
            k: round(feature_missing_counts[k] / self.total_observations, 4)
            for k in sorted(all_features)
        }

        self.dataset_status_message = (
            f"Dataset contains {self.total_observations} valid longitudinal observations "
            f"across {self.unique_students} students and {self.unique_topics} topics."
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_data": self.has_data,
            "status_message": self.dataset_status_message,
            "total_observations": self.total_observations,
            "unique_students": self.unique_students,
            "unique_topics": self.unique_topics,
            "positive_target_count": self.positive_target_count,
            "negative_target_count": self.negative_target_count,
            "class_balance": self.class_balance,
            "observations_per_student": self.observations_per_student,
            "observations_per_topic": self.observations_per_topic,
            "lead_time_distribution": self.lead_time_distribution,
            "cold_start_proportion": self.cold_start_proportion,
            "missing_feature_rates": self.missing_feature_rates,
        }

    def to_markdown(self) -> str:
        """Formats diagnostics as a clean markdown summary table."""
        if not self.has_data:
            return (
                "### Dataset Diagnostics Report\n\n"
                f"> [!NOTE]\n> **Status**: {self.dataset_status_message}\n"
            )

        md = [
            "### Dataset Diagnostics & Quality Profile\n\n",
            f"- **Total Observations**: {self.total_observations}\n",
            f"- **Unique Students**: {self.unique_students}\n",
            f"- **Unique Topics**: {self.unique_topics}\n",
            f"- **Class Balance**: {self.positive_target_count} Positive / {self.negative_target_count} Negative (Positive Rate: {self.class_balance * 100:.2f}%)\n",
            f"- **Cold-Start Proportion**: {self.cold_start_proportion * 100:.2f}%\n\n",
            "#### Distributions\n",
            f"- **Observations per Student**: Min={self.observations_per_student['min']}, Median={self.observations_per_student['median']}, Mean={self.observations_per_student['mean']}, Max={self.observations_per_student['max']}\n",
            f"- **Observations per Topic**: Min={self.observations_per_topic['min']}, Median={self.observations_per_topic['median']}, Mean={self.observations_per_topic['mean']}, Max={self.observations_per_topic['max']}\n",
            f"- **Lead Time (seconds)**: Min={self.lead_time_distribution['min_sec']}s, Median={self.lead_time_distribution['median_sec']}s, P75={self.lead_time_distribution['p75_sec']}s, Max={self.lead_time_distribution['max_sec']}s\n",
        ]
        return "".join(md)
