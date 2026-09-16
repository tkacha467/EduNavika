from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.learning_event import LearningEvent
from backend.app.models.curriculum import Topic
from backend.app.domain.enums import EventType
from backend.app.domain.prediction.schemas import PointInTimeFeatures


def _ensure_utc(dt: datetime) -> datetime:
    """Ensures datetime object has UTC timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class PointInTimeFeatureExtractor:
    """
    Derives point-safe historical learning features strictly from
    LearningEvent records where timestamp <= cutoff_timestamp.
    
    INVARIANTS:
    1. NEVER accesses TopicPerformance, ForgettingSignal, or RevisionPlan.
    2. NEVER processes events with timestamp > cutoff_timestamp.
    3. Explicitly flags missing values rather than silently hiding them.
    4. Deterministic: identical input events produce identical feature vectors.
    """

    @classmethod
    def extract(
        cls,
        student_id: str,
        topic_id: str,
        cutoff_timestamp: datetime,
        events: List[LearningEvent],
        curriculum_meta: Optional[Dict[str, Any]] = None,
        db: Optional[Session] = None,
        ewma_alpha: float = 0.3,
        max_latency_ms: int = 180000,
    ) -> PointInTimeFeatures:
        """
        Extracts point-in-time features from an in-memory event list.
        """
        cutoff_utc = _ensure_utc(cutoff_timestamp)

        # 1. Filter events strictly by student_id and timestamp <= cutoff
        past_events = [
            e for e in events
            if e.student_id == student_id and _ensure_utc(e.timestamp) <= cutoff_utc
        ]
        # Strict deterministic chronological sort
        past_events.sort(key=lambda e: (_ensure_utc(e.timestamp), getattr(e, "created_at", _ensure_utc(e.timestamp)), getattr(e, "id", "")))

        # 2. Topic vs Global partitions
        topic_events = [e for e in past_events if e.topic_id == topic_id]
        evaluative_topic_events = [e for e in topic_events if e.correctness is not None]
        evaluative_global_events = [e for e in past_events if e.correctness is not None]

        # --- 3. Temporal Spacing & Recency ---
        delta_t_topic_days = None
        delta_t_topic_seconds = None
        has_prior_topic = len(topic_events) > 0

        if has_prior_topic:
            last_topic_dt = _ensure_utc(topic_events[-1].timestamp)
            delta_sec = max(0.0, (cutoff_utc - last_topic_dt).total_seconds())
            delta_t_topic_seconds = round(delta_sec, 2)
            delta_t_topic_days = round(delta_sec / 86400.0, 4)

        # Success recency
        correct_topic_events = [e for e in evaluative_topic_events if e.correctness is True]
        delta_t_success_days = None
        has_prior_success = len(correct_topic_events) > 0
        if has_prior_success:
            last_success_dt = _ensure_utc(correct_topic_events[-1].timestamp)
            delta_sec_succ = max(0.0, (cutoff_utc - last_success_dt).total_seconds())
            delta_t_success_days = round(delta_sec_succ / 86400.0, 4)

        # Global recency
        delta_t_global_days = None
        has_prior_global = len(past_events) > 0
        if has_prior_global:
            last_global_dt = _ensure_utc(past_events[-1].timestamp)
            delta_sec_glob = max(0.0, (cutoff_utc - last_global_dt).total_seconds())
            delta_t_global_days = round(delta_sec_glob / 86400.0, 4)

        # --- 4. Cumulative Exposure & Volume ---
        cum_topic_attempts = len(evaluative_topic_events)
        cum_topic_exposures = len(topic_events)
        cum_topic_correct = len(correct_topic_events)
        cum_revision = sum(1 for e in topic_events if e.event_type in (EventType.REVISION, "REVISION"))
        cum_practice = sum(1 for e in topic_events if e.event_type in (EventType.PRACTICE, "PRACTICE"))
        cum_mcq = sum(1 for e in topic_events if e.event_type in (EventType.MCQ_ATTEMPT, "MCQ_ATTEMPT"))
        cum_global_attempts = len(evaluative_global_events)
        cum_global_exposures = len(past_events)

        # --- 5. Historical Accuracy ---
        topic_acc = None
        topic_acc_missing = True
        if cum_topic_attempts > 0:
            topic_acc = round((cum_topic_correct / cum_topic_attempts) * 100.0, 2)
            topic_acc_missing = False

        global_acc = None
        global_acc_missing = True
        if cum_global_attempts > 0:
            global_correct = sum(1 for e in evaluative_global_events if e.correctness is True)
            global_acc = round((global_correct / cum_global_attempts) * 100.0, 2)
            global_acc_missing = False

        # --- 6. EWMA Accuracy ---
        ewma_acc = None
        ewma_acc_missing = True
        if evaluative_topic_events:
            ewma_val = 100.0 if evaluative_topic_events[0].correctness is True else 0.0
            for e in evaluative_topic_events[1:]:
                c_val = 100.0 if e.correctness is True else 0.0
                ewma_val = (ewma_alpha * c_val) + ((1.0 - ewma_alpha) * ewma_val)
            ewma_acc = round(ewma_val, 2)
            ewma_acc_missing = False

        # --- 7. Response Time Statistics & Trend ---
        latencies: List[float] = []
        winsorized_count = 0
        for e in evaluative_topic_events:
            if e.response_time_ms is not None and e.response_time_ms > 0:
                if e.response_time_ms > max_latency_ms:
                    latencies.append(float(max_latency_ms))
                    winsorized_count += 1
                else:
                    latencies.append(float(e.response_time_ms))

        mean_lat = None
        median_lat = None
        last_lat = None
        lat_trend_ratio = None
        lat_missing = True

        if latencies:
            lat_missing = False
            mean_lat = round(sum(latencies) / len(latencies), 2)
            sorted_lats = sorted(latencies)
            n_l = len(sorted_lats)
            mid = n_l // 2
            if n_l % 2 == 1:
                median_lat = float(sorted_lats[mid])
            else:
                median_lat = round((sorted_lats[mid - 1] + sorted_lats[mid]) / 2.0, 2)
            last_lat = float(latencies[-1])
            lat_trend_ratio = round(last_lat / mean_lat, 3) if mean_lat > 0 else 1.0

        # --- 8. Hint Usage ---
        cum_hints = sum(1 for e in evaluative_topic_events if e.hint_used is True)
        hint_rate = None
        last_hint = None
        hint_missing = True
        if cum_topic_attempts > 0:
            hint_missing = False
            hint_rate = round(cum_hints / cum_topic_attempts, 4)
            last_hint = bool(evaluative_topic_events[-1].hint_used)

        # --- 9. Intervening Activity (Cognitive Interference) ---
        intervening_count = 0
        intervening_topics = 0
        intervening_eval = 0
        is_first_attempt = (cum_topic_attempts == 0)

        if has_prior_topic:
            last_topic_dt = _ensure_utc(topic_events[-1].timestamp)
            intervening = [
                e for e in past_events
                if _ensure_utc(e.timestamp) > last_topic_dt and e.topic_id != topic_id
            ]
            intervening_count = len(intervening)
            intervening_topics = len({e.topic_id for e in intervening})
            intervening_eval = sum(1 for e in intervening if e.correctness is not None)

        # --- 10. Static Curriculum Context ---
        grade_lvl = None
        subj_code = None
        chap_num = None
        top_order = None
        curr_missing = True

        if curriculum_meta:
            grade_lvl = curriculum_meta.get("grade_level")
            subj_code = curriculum_meta.get("subject_code")
            chap_num = curriculum_meta.get("chapter_number")
            top_order = curriculum_meta.get("topic_order")
            curr_missing = False
        elif db is not None:
            topic_record = db.query(Topic).filter(Topic.id == topic_id).first()
            if topic_record:
                top_order = topic_record.topic_order
                if topic_record.chapter:
                    chap_num = topic_record.chapter.chapter_number
                    if topic_record.chapter.subject:
                        subj_code = topic_record.chapter.subject.code
                        if topic_record.chapter.subject.standard:
                            grade_lvl = topic_record.chapter.subject.standard.grade_number
                curr_missing = False

        return PointInTimeFeatures(
            student_id=student_id,
            topic_id=topic_id,
            cutoff_timestamp=cutoff_utc,
            delta_t_topic_days=delta_t_topic_days,
            delta_t_topic_seconds=delta_t_topic_seconds,
            has_prior_topic_interaction=has_prior_topic,
            delta_t_success_days=delta_t_success_days,
            has_prior_topic_success=has_prior_success,
            delta_t_global_days=delta_t_global_days,
            has_prior_global_interaction=has_prior_global,
            cumulative_topic_attempts=cum_topic_attempts,
            cumulative_topic_exposures=cum_topic_exposures,
            cumulative_topic_correct_count=cum_topic_correct,
            cumulative_revision_count=cum_revision,
            cumulative_practice_count=cum_practice,
            cumulative_mcq_attempt_count=cum_mcq,
            cumulative_global_attempts=cum_global_attempts,
            cumulative_global_exposures=cum_global_exposures,
            cumulative_topic_accuracy=topic_acc,
            topic_accuracy_is_missing=topic_acc_missing,
            cumulative_global_accuracy=global_acc,
            global_accuracy_is_missing=global_acc_missing,
            ewma_topic_accuracy=ewma_acc,
            ewma_accuracy_is_missing=ewma_acc_missing,
            ewma_alpha=ewma_alpha,
            mean_response_time_ms=mean_lat,
            median_response_time_ms=median_lat,
            last_response_time_ms=last_lat,
            latency_trend_ratio=lat_trend_ratio,
            latency_is_missing=lat_missing,
            latency_winsorized_count=winsorized_count,
            cumulative_hint_count=cum_hints,
            hint_rate=hint_rate,
            last_attempt_hint_used=last_hint,
            hint_data_is_missing=hint_missing,
            intervening_event_count=intervening_count,
            intervening_distinct_topics_count=intervening_topics,
            intervening_evaluative_count=intervening_eval,
            is_first_topic_attempt=is_first_attempt,
            grade_level=grade_lvl,
            subject_code=subj_code,
            chapter_number=chap_num,
            topic_order=top_order,
            curriculum_context_is_missing=curr_missing,
        )

    @classmethod
    def extract_from_db(
        cls,
        db: Session,
        student_id: str,
        topic_id: str,
        cutoff_timestamp: datetime,
        ewma_alpha: float = 0.3,
        max_latency_ms: int = 180000,
    ) -> PointInTimeFeatures:
        """
        Database query helper.
        Queries ONLY the append-only LearningEvent table where timestamp <= cutoff.
        NEVER queries TopicPerformance or other live state tables.
        """
        cutoff_utc = _ensure_utc(cutoff_timestamp)

        events = (
            db.query(LearningEvent)
            .filter(
                LearningEvent.student_id == student_id,
                LearningEvent.timestamp <= cutoff_utc,
            )
            .order_by(LearningEvent.timestamp.asc(), LearningEvent.created_at.asc())
            .all()
        )

        return cls.extract(
            student_id=student_id,
            topic_id=topic_id,
            cutoff_timestamp=cutoff_utc,
            events=events,
            db=db,
            ewma_alpha=ewma_alpha,
            max_latency_ms=max_latency_ms,
        )
