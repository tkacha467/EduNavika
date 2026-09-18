from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from backend.app.models import LearningEvent
from backend.app.models import TopicPerformance
from backend.app.domain.decay_engine.schemas import (
    DecayDetectionConfig,
    EvidenceProfile,
    DecaySignalDraft,
)
from backend.app.domain.decay_engine.strength_evaluator import EvidenceStrengthEvaluator
from backend.app.domain.decay_engine.deduplication import SignalDeduplicator


class LongitudinalDecayDetector:
    """
    Analyzes chronologically ordered student interaction sequences (LearningEvent)
    to detect heuristic operational evidence of temporal performance decay.
    
    IMPORTANT: Thresholds applied here represent heuristic operational definitions
    for automated triage, NOT scientifically proven cognitive constants.
    """

    def __init__(self, config: Optional[DecayDetectionConfig] = None):
        self.config = config or DecayDetectionConfig()

    def detect_for_topic(
        self,
        student_id: str,
        topic_id: str,
        events: List[LearningEvent],
        topic_perf: Optional[TopicPerformance] = None,
        all_student_events: Optional[List[LearningEvent]] = None,
    ) -> List[DecaySignalDraft]:
        """
        Evaluates topic events chronologically to detect decay signatures.
        """
        # Filter for relevant events with correctness or response time
        topic_events = [
            e for e in sorted(events, key=lambda x: x.timestamp)
            if e.topic_id == topic_id and e.correctness is not None
        ]

        if len(topic_events) < (self.config.min_prior_attempts + 1):
            return []

        signals: List[DecaySignalDraft] = []

        # Find temporal gaps >= min_delay_days between consecutive events
        # We check from earliest to latest
        for i in range(len(topic_events) - 1):
            prior_events = topic_events[: i + 1]
            later_events = topic_events[i + 1 :]

            if len(prior_events) < self.config.min_prior_attempts:
                continue

            last_prior_time = prior_events[-1].timestamp
            first_later_time = later_events[0].timestamp

            # Time gap in days
            gap_seconds = (first_later_time - last_prior_time).total_seconds()
            gap_days = gap_seconds / 86400.0

            if gap_days < self.config.min_delay_days:
                continue

            # We found a significant temporal gap. Evaluate baseline vs post-delay
            prior_correct = sum(1 for e in prior_events if e.correctness is True)
            baseline_acc = round((prior_correct / len(prior_events)) * 100.0, 2)

            later_correct = sum(1 for e in later_events if e.correctness is True)
            later_acc = round((later_correct / len(later_events)) * 100.0, 2)

            prior_latencies = [e.response_time_ms for e in prior_events if e.response_time_ms and e.response_time_ms > 0]
            later_latencies = [e.response_time_ms for e in later_events if e.response_time_ms and e.response_time_ms > 0]

            baseline_avg_lat = round(sum(prior_latencies) / len(prior_latencies), 2) if prior_latencies else None
            later_avg_lat = round(sum(later_latencies) / len(later_latencies), 2) if later_latencies else None
            lat_ratio = None
            if baseline_avg_lat and later_avg_lat and baseline_avg_lat > 0:
                lat_ratio = round(later_avg_lat / baseline_avg_lat, 2)

            # Extract non-causal observational metadata during the delay window
            obs_intervening_count = 0
            obs_intervening_topics = []
            if all_student_events:
                intervening = [
                    e for e in all_student_events
                    if last_prior_time < e.timestamp < first_later_time and e.topic_id != topic_id
                ]
                obs_intervening_count = len(intervening)
                obs_intervening_topics = sorted(list({e.topic_id for e in intervening}))

            prior_mastery = topic_perf.mastery_state if topic_perf else "UNASSESSED"

            # Check consecutive failure in post-delay
            is_consecutive_fail = False
            consecutive_fail_count = 0
            for e in later_events:
                if e.correctness is False:
                    consecutive_fail_count += 1
                else:
                    break
            if consecutive_fail_count >= self.config.consecutive_failures_threshold:
                is_consecutive_fail = True

            latest_event_iso = later_events[-1].timestamp.isoformat()

            # --- Signature 1: ACCURACY_DROP_POST_DELAY ---
            if (
                baseline_acc >= self.config.baseline_accuracy_min
                and later_acc <= self.config.post_delay_accuracy_max
            ):
                profile = EvidenceProfile(
                    prior_attempts=len(prior_events),
                    baseline_accuracy=baseline_acc,
                    post_delay_attempts=len(later_events),
                    post_delay_accuracy=later_acc,
                    delay_days=round(gap_days, 1),
                    baseline_avg_latency_ms=baseline_avg_lat,
                    post_delay_avg_latency_ms=later_avg_lat,
                    latency_ratio=lat_ratio,
                    prior_mastery_state=prior_mastery,
                    is_consecutive_failure=is_consecutive_fail,
                    consecutive_failures_count=consecutive_fail_count,
                    observational_intervening_activities=obs_intervening_count,
                    observational_intervening_topics=obs_intervening_topics,
                )
                strength, audit_meta = EvidenceStrengthEvaluator.evaluate(profile)

                fingerprint = SignalDeduplicator.generate_fingerprint(
                    student_id, topic_id, "ACCURACY_DROP_POST_DELAY", latest_event_iso
                )

                signals.append(
                    DecaySignalDraft(
                        student_id=student_id,
                        topic_id=topic_id,
                        evidence_type="ACCURACY_DROP_POST_DELAY",
                        evidence_strength=strength,
                        prior_performance_reference={
                            "attempts": len(prior_events),
                            "accuracy": baseline_acc,
                            "last_timestamp": last_prior_time.isoformat(),
                            "avg_latency_ms": baseline_avg_lat,
                            "mastery_state": prior_mastery,
                        },
                        later_performance_reference={
                            "attempts": len(later_events),
                            "accuracy": later_acc,
                            "first_timestamp": first_later_time.isoformat(),
                            "latest_timestamp": latest_event_iso,
                            "avg_latency_ms": later_avg_lat,
                        },
                        evidence_metadata={
                            "days_elapsed": round(gap_days, 1),
                            "operational_definition": "Heuristic operational criteria: baseline_acc >= 70% with delay >= 7d and post_delay_acc <= 60%",
                            "strength_derivation": audit_meta,
                            "observational_context": {
                                "intervening_activities_count": obs_intervening_count,
                                "intervening_topics_count": len(obs_intervening_topics),
                                "disclaimer": "Observational metadata only. Not claimed as causal factor of decay.",
                            },
                            "episode_fingerprint": fingerprint,
                            "latest_event_iso": latest_event_iso,
                        },
                        detected_at=datetime.now(timezone.utc),
                        episode_fingerprint=fingerprint,
                    )
                )

            # --- Signature 2: LATENCY_SPIKE_POST_DELAY ---
            elif (
                lat_ratio is not None
                and lat_ratio >= self.config.latency_spike_ratio_threshold
                and baseline_acc >= 70.0
                and later_acc >= 70.0  # Maintained accuracy but with severe effort/retrieval slowing
            ):
                profile = EvidenceProfile(
                    prior_attempts=len(prior_events),
                    baseline_accuracy=baseline_acc,
                    post_delay_attempts=len(later_events),
                    post_delay_accuracy=later_acc,
                    delay_days=round(gap_days, 1),
                    baseline_avg_latency_ms=baseline_avg_lat,
                    post_delay_avg_latency_ms=later_avg_lat,
                    latency_ratio=lat_ratio,
                    prior_mastery_state=prior_mastery,
                    is_consecutive_failure=False,
                    consecutive_failures_count=0,
                    observational_intervening_activities=obs_intervening_count,
                    observational_intervening_topics=obs_intervening_topics,
                )
                strength, audit_meta = EvidenceStrengthEvaluator.evaluate(profile)
                fingerprint = SignalDeduplicator.generate_fingerprint(
                    student_id, topic_id, "LATENCY_SPIKE_POST_DELAY", latest_event_iso
                )

                signals.append(
                    DecaySignalDraft(
                        student_id=student_id,
                        topic_id=topic_id,
                        evidence_type="LATENCY_SPIKE_POST_DELAY",
                        evidence_strength=strength,
                        prior_performance_reference={
                            "attempts": len(prior_events),
                            "accuracy": baseline_acc,
                            "avg_latency_ms": baseline_avg_lat,
                        },
                        later_performance_reference={
                            "attempts": len(later_events),
                            "accuracy": later_acc,
                            "avg_latency_ms": later_avg_lat,
                            "latency_ratio": lat_ratio,
                        },
                        evidence_metadata={
                            "days_elapsed": round(gap_days, 1),
                            "operational_definition": "Heuristic operational criteria: latency_ratio >= 2.0x after delay >= 7d",
                            "strength_derivation": audit_meta,
                            "episode_fingerprint": fingerprint,
                            "latest_event_iso": latest_event_iso,
                        },
                        detected_at=datetime.now(timezone.utc),
                        episode_fingerprint=fingerprint,
                    )
                )

            # --- Signature 3: CONSECUTIVE_POST_MASTERY_FAILURES ---
            elif (
                prior_mastery == "MASTERED"
                and is_consecutive_fail
            ):
                profile = EvidenceProfile(
                    prior_attempts=len(prior_events),
                    baseline_accuracy=baseline_acc,
                    post_delay_attempts=len(later_events),
                    post_delay_accuracy=later_acc,
                    delay_days=round(gap_days, 1),
                    prior_mastery_state="MASTERED",
                    is_consecutive_failure=True,
                    consecutive_failures_count=consecutive_fail_count,
                    observational_intervening_activities=obs_intervening_count,
                    observational_intervening_topics=obs_intervening_topics,
                )
                strength, audit_meta = EvidenceStrengthEvaluator.evaluate(profile)
                fingerprint = SignalDeduplicator.generate_fingerprint(
                    student_id, topic_id, "CONSECUTIVE_POST_MASTERY_FAILURES", latest_event_iso
                )

                signals.append(
                    DecaySignalDraft(
                        student_id=student_id,
                        topic_id=topic_id,
                        evidence_type="CONSECUTIVE_POST_MASTERY_FAILURES",
                        evidence_strength=strength,
                        prior_performance_reference={
                            "attempts": len(prior_events),
                            "accuracy": baseline_acc,
                            "mastery_state": "MASTERED",
                        },
                        later_performance_reference={
                            "consecutive_failures": consecutive_fail_count,
                            "post_delay_accuracy": later_acc,
                        },
                        evidence_metadata={
                            "days_elapsed": round(gap_days, 1),
                            "operational_definition": "Heuristic operational criteria: >=2 consecutive failures after MASTERED status",
                            "strength_derivation": audit_meta,
                            "episode_fingerprint": fingerprint,
                            "latest_event_iso": latest_event_iso,
                        },
                        detected_at=datetime.now(timezone.utc),
                        episode_fingerprint=fingerprint,
                    )
                )

        return signals
