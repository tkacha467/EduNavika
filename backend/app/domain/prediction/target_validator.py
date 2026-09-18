import os
import sys
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models import LearningEvent, EventType
from backend.app.domain.prediction.extractor import PointInTimeFeatureExtractor, _ensure_utc
from backend.app.domain.prediction.sampling import ObservationSampler, RejectionReason
from backend.app.domain.prediction.diagnostics import _percentile, _distribution_stats


class TargetValidityAuditor:
    """
    Research-grade validation layer that audits real persisted LearningEvents
    to determine whether 'Target A — next evaluative event correctness' is
    empirically observable, and whether it measures immediate retrieval vs.
    delayed retention/forgetting.
    """

    def __init__(self, output_dir: Path = Path("data/processed/reports")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def audit(
        self,
        db: Optional[Session] = None,
        events: Optional[List[LearningEvent]] = None,
    ) -> Dict[str, Any]:
        close_session = False
        if events is None:
            if db is None:
                db = SessionLocal()
                close_session = True
            events = db.query(LearningEvent).order_by(LearningEvent.timestamp.asc()).all()

        try:
            return self._analyze_events(events)
        finally:
            if close_session and db:
                db.close()

    def _analyze_events(self, events: List[LearningEvent]) -> Dict[str, Any]:
        total_events = len(events)
        now_iso = datetime.now(timezone.utc).isoformat()

        # -------------------------------------------------------------
        # 1. Empirical Readiness: Empty Database Check
        # -------------------------------------------------------------
        if total_events == 0:
            result = {
                "timestamp": now_iso,
                "verdict": "DATA_NOT_YET_OBSERVABLE",
                "status_message": (
                    "Empirical target validation impossible: persistent database contains 0 LearningEvent records. "
                    "No real longitudinal student interactions have been recorded yet."
                ),
                "total_events": 0,
                "unique_students": 0,
                "unique_topics": 0,
                "evaluative_events_count": 0,
                "events_by_type": {et.value: 0 for et in EventType},
                "students_with_longitudinal_history": 0,
                "topics_with_repeated_interactions": 0,
                "target_a_analysis": {
                    "valid_observations_count": 0,
                    "rejected_observations_count": 0,
                    "positive_target_count": 0,
                    "negative_target_count": 0,
                    "class_balance": None,
                    "cold_start_percentage": 0.0,
                    "sufficient_history_percentage": 0.0,
                },
                "lead_time_taxonomy": {
                    "immediate_count": 0,
                    "short_delay_count": 0,
                    "medium_spaced_count": 0,
                    "long_spaced_count": 0,
                    "immediate_fraction": 0.0,
                    "session_effects_warning": False,
                },
                "scientific_target_classification": {
                    "future_retrieval_predictions_count": 0,
                    "delayed_retention_predictions_count": 0,
                    "can_model_forgetting": False,
                    "scientific_distinction": (
                        "Target A measures next-attempt correctness. When lead time is short (< 24h), "
                        "it reflects immediate working-memory retrieval, NOT long-term retention decay."
                    ),
                },
                "actionable_requirements": [
                    "Deploy EduNavika learning flows (Study, Practice, Assessments, Revision, Review) to active students.",
                    "Collect repeated practice attempts on the same topic separated by >= 24 hours to observe genuine retention.",
                    "Execute scheduled spaced revisions (REVISION events) across Standards 9–12.",
                ],
            }
            self._save_reports(result)
            return result

        # -------------------------------------------------------------
        # 2. General Dataset Inspection
        # -------------------------------------------------------------
        events_by_type: Dict[str, int] = defaultdict(int)
        by_student: Dict[str, List[LearningEvent]] = defaultdict(list)
        by_student_topic: Dict[Tuple[str, str], List[LearningEvent]] = defaultdict(list)
        evaluative_count = 0

        for e in events:
            etype_str = e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
            events_by_type[etype_str] += 1
            by_student[e.student_id].append(e)
            by_student_topic[(e.student_id, e.topic_id)].append(e)
            if e.correctness is not None:
                evaluative_count += 1

        # Check longitudinal spans per student (> 24 hours)
        students_longitudinal = 0
        for sid, s_evs in by_student.items():
            if len(s_evs) >= 2:
                t_min = _ensure_utc(min(e.timestamp for e in s_evs))
                t_max = _ensure_utc(max(e.timestamp for e in s_evs))
                if (t_max - t_min).total_seconds() >= 86400.0:
                    students_longitudinal += 1

        # Repeated topic interactions
        repeated_pairs = sum(1 for st_evs in by_student_topic.values() if len(st_evs) >= 2)

        # -------------------------------------------------------------
        # 3. Observation Sampling & Target A Validation
        # -------------------------------------------------------------
        sampler = ObservationSampler()
        dataset, audit = sampler.sample_observations(events)

        valid_count = dataset.total_samples
        rejected_count = audit.rejected_samples_count

        pos_count = dataset.positive_target_count
        neg_count = dataset.negative_target_count
        class_bal = dataset.positive_rate if valid_count > 0 else None

        cold_starts = sum(1 for s in dataset.samples if s.features.is_first_topic_attempt)
        cold_start_pct = round((cold_starts / valid_count) * 100.0, 2) if valid_count > 0 else 0.0

        sufficient_history = sum(1 for s in dataset.samples if s.features.cumulative_topic_attempts >= 2)
        sufficient_history_pct = round((sufficient_history / valid_count) * 100.0, 2) if valid_count > 0 else 0.0

        # Observations per student & topic
        stud_obs_counts = defaultdict(int)
        top_obs_counts = defaultdict(int)
        lead_times_sec = []

        for s in dataset.samples:
            stud_obs_counts[s.student_id] += 1
            top_obs_counts[s.topic_id] += 1
            lead_times_sec.append(s.lead_time_seconds)

        obs_per_student = _distribution_stats(list(stud_obs_counts.values()))
        obs_per_topic = _distribution_stats(list(top_obs_counts.values()))

        # -------------------------------------------------------------
        # 4. Lead Time Taxonomy: Immediate vs. Spaced Retention
        # -------------------------------------------------------------
        # Immediate / Intra-session: < 10 mins (600s)
        # Short delay: 10 mins to 24h (600s to 86400s)
        # Medium spaced: 1 to 7 days (86400s to 604800s)
        # Long spaced: >= 7 days (>= 604800s)
        imm_count = sum(1 for lt in lead_times_sec if lt < 600.0)
        short_count = sum(1 for lt in lead_times_sec if 600.0 <= lt < 86400.0)
        med_count = sum(1 for lt in lead_times_sec if 86400.0 <= lt < 604800.0)
        long_count = sum(1 for lt in lead_times_sec if lt >= 604800.0)

        imm_fraction = round(imm_count / valid_count, 4) if valid_count > 0 else 0.0
        session_effects_warning = imm_fraction > 0.50

        # Scientific classification: retrieval vs retention
        future_retrieval_count = imm_count + short_count
        delayed_retention_count = med_count + long_count
        can_model_forgetting = delayed_retention_count >= 10

        # Verdict logic
        if valid_count == 0:
            verdict = "INSUFFICIENT_EVALUATIVE_TRANSITIONS"
            msg = "Events exist but no valid evaluative transitions could be formed."
        elif delayed_retention_count == 0 and future_retrieval_count > 0:
            verdict = "IMMEDIATE_RETRIEVAL_ONLY_NO_FORGETTING_DATA"
            msg = (
                f"Target A is 100% immediate/intra-session ({future_retrieval_count} observations < 24h). "
                "Suitable for immediate retrieval prediction, but CANNOT be used to claim knowledge forgetting."
            )
        elif not can_model_forgetting:
            verdict = "SPARSE_RETENTION_DATA"
            msg = f"Observed {delayed_retention_count} spaced observations (>= 24h). Insufficient for statistically robust retention decay modeling."
        else:
            verdict = "RETENTION_TARGET_OBSERVABLE"
            msg = f"Empirically verified: {delayed_retention_count} spaced observations (>= 24h) support valid delayed retention modeling."

        # Percentiles
        sorted_lts = sorted(lead_times_sec) if lead_times_sec else [0.0]
        n_lts = len(sorted_lts)
        med_lt = sorted_lts[n_lts // 2] if n_lts % 2 == 1 else (sorted_lts[n_lts // 2 - 1] + sorted_lts[n_lts // 2]) / 2.0

        lead_dist = {
            "min_sec": round(sorted_lts[0], 2),
            "p25_sec": round(_percentile(sorted_lts, 25.0), 2),
            "median_sec": round(med_lt, 2),
            "p75_sec": round(_percentile(sorted_lts, 75.0), 2),
            "max_sec": round(sorted_lts[-1], 2),
        }

        result = {
            "timestamp": now_iso,
            "verdict": verdict,
            "status_message": msg,
            "total_events": total_events,
            "events_by_type": dict(events_by_type),
            "evaluative_events_count": evaluative_count,
            "unique_students": len(by_student),
            "unique_topics": len({e.topic_id for e in events}),
            "students_with_longitudinal_history": students_longitudinal,
            "topics_with_repeated_interactions": repeated_pairs,
            "target_a_analysis": {
                "valid_observations_count": valid_count,
                "rejected_observations_count": rejected_count,
                "rejections_breakdown": dict(audit.rejections_by_reason),
                "positive_target_count": pos_count,
                "negative_target_count": neg_count,
                "class_balance": class_bal,
                "cold_start_count": cold_starts,
                "cold_start_percentage": cold_start_pct,
                "sufficient_history_count": sufficient_history,
                "sufficient_history_percentage": sufficient_history_pct,
                "observations_per_student": obs_per_student,
                "observations_per_topic": obs_per_topic,
            },
            "lead_time_taxonomy": {
                "immediate_count": imm_count,
                "short_delay_count": short_count,
                "medium_spaced_count": med_count,
                "long_spaced_count": long_count,
                "percentiles": lead_dist,
                "immediate_fraction": imm_fraction,
                "session_effects_warning": session_effects_warning,
            },
            "scientific_target_classification": {
                "future_retrieval_predictions_count": future_retrieval_count,
                "delayed_retention_predictions_count": delayed_retention_count,
                "can_model_forgetting": can_model_forgetting,
                "scientific_distinction": (
                    "CRITICAL RESEARCH SAFEGUARD: Target A (next evaluative event correctness) "
                    "measures immediate retrieval accuracy when lead time is short (< 24h). "
                    "It must NOT be claimed to measure knowledge decay/forgetting unless "
                    "evaluated across spaced delays (>= 1-7 days)."
                ),
            },
            "actionable_requirements": [
                "Continue logging real student activity across the 5 instrumented telemetry flows.",
                "Ensure spaced practice intervals (e.g. revision scheduled at 1, 3, 7 days) to build long-term retention observations.",
            ],
        }

        self._save_reports(result)
        return result

    def _save_reports(self, report: Dict[str, Any]):
        json_path = self.output_dir / "target_validity_report.json"
        md_path = self.output_dir / "target_validity_report.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        md_content = self._generate_markdown(report)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        t_a = report["target_a_analysis"]
        lt = report["lead_time_taxonomy"]
        sc = report["scientific_target_classification"]
        class_balance_str = f"{t_a['class_balance'] * 100:.1f}%" if t_a.get("class_balance") is not None else "N/A"

        md = [
            "# Milestone 9 — Real Longitudinal Data Acquisition & Target Validity Report\n\n",
            f"- **Target Audit Verdict**: **`{report['verdict']}`**\n",
            f"- **Audit Timestamp**: `{report['timestamp']}`\n",
            f"- **Status**: {report['status_message']}\n\n",
            "---\n\n",
            "## 1. Empirical Database Footprint\n\n",
            f"- **Total LearningEvents in DB**: **{report['total_events']}**\n",
            f"- **Evaluative Events**: {report['evaluative_events_count']}\n",
            f"- **Unique Active Students**: {report['unique_students']}\n",
            f"- **Unique Active Topics**: {report['unique_topics']}\n",
            f"- **Students with Longitudinal History (> 24h)**: {report['students_with_longitudinal_history']}\n",
            f"- **Student-Topic Pairs with Repeated Interactions**: {report['topics_with_repeated_interactions']}\n\n",
            "---\n\n",
            "## 2. Target A (Next-Attempt Correctness) Validity\n\n",
            f"- **Valid Observations**: **{t_a['valid_observations_count']}**\n",
            f"- **Rejected Candidate Observations**: {t_a['rejected_observations_count']}\n",
            f"- **Positive (Correct) Targets**: {t_a['positive_target_count']}\n",
            f"- **Negative (Incorrect) Targets**: {t_a['negative_target_count']}\n",
            f"- **Class Balance (Positive Rate)**: {class_balance_str}\n",
            f"- **Cold-Start Rate**: {t_a['cold_start_percentage']}%\n",
            f"- **Observations with >= 2 Prior Topic Attempts**: {t_a['sufficient_history_percentage']}%\n\n",
            "---\n\n",
            "## 3. Lead Time Taxonomy: Immediate Retrieval vs. Delayed Retention\n\n",
            f"> [!IMPORTANT]\n> **Scientific Distinction**: {sc['scientific_distinction']}\n\n",
            f"- **Immediate (< 10 minutes)**: {lt['immediate_count']} ({lt['immediate_fraction'] * 100:.1f}% of observations)\n",
            f"- **Short Delay (10 mins to 24 hours)**: {lt['short_delay_count']}\n",
            f"- **Medium Spaced Delay (1 to 7 days)**: {lt['medium_spaced_count']}\n",
            f"- **Long Spaced Delay (>= 7 days)**: {lt['long_spaced_count']}\n",
            f"- **Session Effects Warning**: **{'ACTIVE (Target A is dominated by intra-session attempts)' if lt['session_effects_warning'] else 'INACTIVE'}**\n\n",
            f"- **Future Retrieval Prediction Candidates (< 24h)**: {sc['future_retrieval_predictions_count']}\n",
            f"- **Delayed Retention Prediction Candidates (>= 24h)**: {sc['delayed_retention_predictions_count']}\n",
            f"- **Statistically Observable Forgetting Model Support**: **{'YES' if sc['can_model_forgetting'] else 'NO (Requires spaced real events)'}**\n\n",
            "---\n\n",
            "## 4. Actionable Next Requirements\n\n",
        ]
        for req in report["actionable_requirements"]:
            md.append(f"- {req}\n")

        return "".join(md)

    run_audit = audit


def main():
    auditor = TargetValidityAuditor()
    rep = auditor.audit()
    print("=" * 65)
    print("MILESTONE 9: REAL DATA ACQUISITION & TARGET VALIDITY AUDIT")
    print("=" * 65)
    print(f"Verdict:              {rep['verdict']}")
    print(f"Total Events in DB:   {rep['total_events']}")
    print(f"Status:               {rep['status_message']}")
    if rep['total_events'] > 0:
        print(f"Valid Target A Obs:   {rep['target_a_analysis']['valid_observations_count']}")
        print(f"Immediate (<10m):     {rep['lead_time_taxonomy']['immediate_count']}")
        print(f"Delayed Spaced (>=24h): {rep['scientific_target_classification']['delayed_retention_predictions_count']}")
    print("=" * 65)


if __name__ == "__main__":
    main()
