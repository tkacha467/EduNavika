import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models import LearningEvent, EventType
from backend.app.models import StudentProfile
from backend.app.models import Topic


class LearningEventAuditor:
    """
    Audits actual LearningEvent records in persistent storage for:
    1. Coverage across all 5 event types (LEARN, PRACTICE, MCQ_ATTEMPT, REVISION, REVIEW).
    2. Student and curriculum topic coverage rates.
    3. Rigorous data-quality violations (negative latency/score, semantic mismatches, duplicates, orphans).
    """

    def __init__(self, output_dir: Path = Path("data/processed/reports")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_audit(self, db: Optional[Session] = None) -> Dict[str, Any]:
        close_session = False
        if db is None:
            db = SessionLocal()
            close_session = True

        try:
            # 1. Fetch all LearningEvent records
            events = db.query(LearningEvent).all()
            total_events = len(events)

            # DB Totals
            total_students_in_db = db.query(StudentProfile).count()
            total_topics_in_db = db.query(Topic).count()

            # Event type distribution
            type_counts: Dict[str, int] = {et.value: 0 for et in EventType}
            student_ids = set()
            topic_ids = set()
            session_ids = set()
            attempt_ids = set()

            # Violation buckets
            negative_latency_count = 0
            negative_score_count = 0
            missing_eval_correctness_count = 0
            invalid_learn_correctness_count = 0
            extreme_latency_count = 0
            orphan_student_count = 0
            orphan_topic_count = 0
            timestamp_duplicates_count = 0

            seen_event_keys = set()

            # Student and Topic existence sets for fast orphan check
            valid_student_ids = {s.id for s in db.query(StudentProfile.id).all()}
            valid_topic_ids = {t.id for t in db.query(Topic.id).all()}

            evaluative_types = {EventType.PRACTICE, EventType.MCQ_ATTEMPT, EventType.REVISION}

            for ev in events:
                etype_str = ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type)
                type_counts[etype_str] = type_counts.get(etype_str, 0) + 1

                student_ids.add(ev.student_id)
                topic_ids.add(ev.topic_id)
                if ev.session_id:
                    session_ids.add(ev.session_id)
                if ev.attempt_id:
                    attempt_ids.add(ev.attempt_id)

                # Orphan checks
                if ev.student_id not in valid_student_ids:
                    orphan_student_count += 1
                if ev.topic_id not in valid_topic_ids:
                    orphan_topic_count += 1

                # Value constraint violations
                if ev.response_time_ms is not None and ev.response_time_ms < 0:
                    negative_latency_count += 1
                if ev.response_time_ms is not None and ev.response_time_ms > 180000:
                    extreme_latency_count += 1
                if ev.score is not None and ev.score < 0:
                    negative_score_count += 1

                # Semantic consistency violations
                if ev.event_type in evaluative_types and ev.correctness is None:
                    missing_eval_correctness_count += 1
                if ev.event_type == EventType.LEARN and ev.correctness is not None:
                    invalid_learn_correctness_count += 1

                # Duplicate check: same (student, topic, event_type, timestamp)
                key = (ev.student_id, ev.topic_id, etype_str, ev.timestamp.isoformat() if ev.timestamp else "")
                if key in seen_event_keys:
                    timestamp_duplicates_count += 1
                else:
                    seen_event_keys.add(key)

            total_violations = (
                negative_latency_count
                + negative_score_count
                + missing_eval_correctness_count
                + invalid_learn_correctness_count
                + orphan_student_count
                + orphan_topic_count
                + timestamp_duplicates_count
            )

            topic_coverage_rate = round(len(topic_ids) / total_topics_in_db, 4) if total_topics_in_db > 0 else 0.0
            student_coverage_rate = round(len(student_ids) / total_students_in_db, 4) if total_students_in_db > 0 else 0.0

            verdict = "PASS" if total_violations == 0 else "FAIL"

            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "verdict": verdict,
                "total_events": total_events,
                "event_type_distribution": type_counts,
                "unique_students_with_events": len(student_ids),
                "unique_topics_with_events": len(topic_ids),
                "unique_sessions": len(session_ids),
                "unique_assessment_attempts": len(attempt_ids),
                "database_coverage": {
                    "total_students_in_db": total_students_in_db,
                    "student_coverage_rate": student_coverage_rate,
                    "total_topics_in_db": total_topics_in_db,
                    "topic_coverage_rate": topic_coverage_rate,
                },
                "data_quality_violations": {
                    "total_violations": total_violations,
                    "negative_latency_violations": negative_latency_count,
                    "negative_score_violations": negative_score_count,
                    "missing_evaluative_correctness": missing_eval_correctness_count,
                    "invalid_learn_correctness": invalid_learn_correctness_count,
                    "extreme_latency_count": extreme_latency_count,
                    "timestamp_duplicates": timestamp_duplicates_count,
                    "orphan_student_records": orphan_student_count,
                    "orphan_topic_records": orphan_topic_count,
                },
            }

            self._save_report(report)
            return report

        finally:
            if close_session:
                db.close()

    def _save_report(self, report: Dict[str, Any]):
        json_path = self.output_dir / "learning_event_coverage_report.json"
        md_path = self.output_dir / "learning_event_coverage_report.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        md_content = self._generate_markdown(report)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        dist = report["event_type_distribution"]
        viol = report["data_quality_violations"]
        cov = report["database_coverage"]

        return f"""# LearningEvent Telemetry Coverage & Data-Quality Audit Report

- **Quality Gate Verdict**: **`{report['verdict']}`**
- **Audit Timestamp**: `{report['timestamp']}`
- **Total LearningEvents Audited**: **{report['total_events']}**

---

## 1. Event Type Distribution

| Event Type | Description | Actual Event Count |
| :--- | :--- | :---: |
| `LEARN` | Content chunk reading / study session | **{dist.get('LEARN', 0)}** |
| `PRACTICE` | Formative question problem-solving | **{dist.get('PRACTICE', 0)}** |
| `MCQ_ATTEMPT` | Formal assessment item submission | **{dist.get('MCQ_ATTEMPT', 0)}** |
| `REVISION` | Scheduled spaced-repetition retrieval | **{dist.get('REVISION', 0)}** |
| `REVIEW` | Post-attempt review / solution inspection | **{dist.get('REVIEW', 0)}** |
| **Total** | **All Longitudinal Events** | **{report['total_events']}** |

---

## 2. Coverage & Entity Footprint

- **Active Students with Telemetry**: {report['unique_students_with_events']} / {cov['total_students_in_db']} ({cov['student_coverage_rate'] * 100:.1f}%)
- **Active Topics with Telemetry**: {report['unique_topics_with_events']} / {cov['total_topics_in_db']} ({cov['topic_coverage_rate'] * 100:.1f}%)
- **Distinct Learning Sessions**: {report['unique_sessions']}
- **Distinct Assessment Attempts**: {report['unique_assessment_attempts']}

---

## 3. Data-Quality & Contract Violations

| Violation Check | Severity | Violations Detected |
| :--- | :---: | :---: |
| Negative Latency (`response_time_ms < 0`) | CRITICAL | {viol['negative_latency_violations']} |
| Negative Score (`score < 0`) | CRITICAL | {viol['negative_score_violations']} |
| Missing Evaluative Correctness (`PRACTICE/MCQ/REVISION` null) | HIGH | {viol['missing_evaluative_correctness']} |
| Invalid `LEARN` Correctness (`LEARN` has correctness) | HIGH | {viol['invalid_learn_correctness']} |
| Timestamp Duplicates (Identical student, topic, type, time) | MEDIUM | {viol['timestamp_duplicates']} |
| Orphan Student Foreign Keys | CRITICAL | {viol['orphan_student_records']} |
| Orphan Topic Foreign Keys | CRITICAL | {viol['orphan_topic_records']} |
| Extreme Latency (> 180s, flagged for winsorization) | INFO | {viol['extreme_latency_count']} |
| **Total Violations** | — | **{viol['total_violations']}** |

---

## 4. Empirical Status Note

{"`PASS`: Zero data-quality violations detected across all recorded LearningEvents." if report['verdict'] == 'PASS' and report['total_events'] > 0 else ("`EMPTY`: Database currently contains 0 LearningEvent records. No data-quality violations detected." if report['total_events'] == 0 else "`FAIL`: Data-quality violations detected in telemetry stream.")}
"""


def main():
    auditor = LearningEventAuditor()
    rep = auditor.run_audit()
    print("=" * 60)
    print("LEARNING EVENT TELEMETRY AUDIT")
    print("=" * 60)
    print(f"Verdict:        {rep['verdict']}")
    print(f"Total Events:   {rep['total_events']}")
    print(f"Distribution:   {rep['event_type_distribution']}")
    print(f"Violations:     {rep['data_quality_violations']['total_violations']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
