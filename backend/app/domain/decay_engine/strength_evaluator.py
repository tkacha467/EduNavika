from typing import Dict, Any, Tuple
from backend.app.domain.constants import (
    EVIDENCE_STRENGTH_STRONG,
    EVIDENCE_STRENGTH_MODERATE,
    EVIDENCE_STRENGTH_WEAK,
)
from backend.app.domain.decay_engine.schemas import EvidenceProfile


class EvidenceStrengthEvaluator:
    """
    Derives categorical qualitative evidence strength (STRONG, MODERATE, WEAK)
    strictly from observable empirical evidence factors rather than arbitrary assignment.
    
    Observable factors evaluated:
    1. Number of prior attempts (prior attempt count / baseline observation volume)
    2. Baseline performance level
    3. Post-delay performance drop magnitude
    4. Inactive delay duration (elapsed days)
    5. Consistency of deterioration across post-delay trials
    6. Latency degradation (response time inflation)
    7. Prior mastery state evidence
    """

    @classmethod
    def evaluate(cls, profile: EvidenceProfile) -> Tuple[str, Dict[str, Any]]:
        points = 0
        breakdown = {}

        # 1. Prior Attempt Count / Baseline Observation Volume
        if profile.prior_attempts >= 6:
            points += 2
            breakdown["observation_volume"] = {"points": 2, "reason": f"High baseline attempt volume ({profile.prior_attempts})"}
        elif profile.prior_attempts >= 3:
            points += 1
            breakdown["observation_volume"] = {"points": 1, "reason": f"Adequate baseline attempt volume ({profile.prior_attempts})"}
        else:
            breakdown["observation_volume"] = {"points": 0, "reason": f"Minimal baseline attempt volume ({profile.prior_attempts})"}

        # 2. Performance Degradation Magnitude
        acc_drop = max(0.0, profile.baseline_accuracy - profile.post_delay_accuracy)
        if acc_drop >= 40.0:
            points += 2
            breakdown["accuracy_drop"] = {"points": 2, "drop_pct": acc_drop}
        elif acc_drop >= 20.0:
            points += 1
            breakdown["accuracy_drop"] = {"points": 1, "drop_pct": acc_drop}
        else:
            breakdown["accuracy_drop"] = {"points": 0, "drop_pct": acc_drop}

        # 3. Delay Duration
        if profile.delay_days >= 21.0:
            points += 2
            breakdown["delay_duration"] = {"points": 2, "days": profile.delay_days}
        elif profile.delay_days >= 14.0:
            points += 1
            breakdown["delay_duration"] = {"points": 1, "days": profile.delay_days}
        else:
            breakdown["delay_duration"] = {"points": 0, "days": profile.delay_days}

        # 4. Consistency Across Multiple Post-Delay Trials
        if profile.post_delay_attempts >= 2 and profile.post_delay_accuracy < 50.0:
            points += 1
            breakdown["consistency"] = {"points": 1, "reason": "Persistent post-delay deterioration across multiple trials"}
        else:
            breakdown["consistency"] = {"points": 0, "reason": "Single trial or non-persistent post-delay observation"}

        # 5. Prior Mastery State
        if profile.prior_mastery_state == "MASTERED":
            points += 1
            breakdown["prior_mastery"] = {"points": 1, "reason": "Deterioration from previously established MASTERED state"}
        else:
            breakdown["prior_mastery"] = {"points": 0, "state": profile.prior_mastery_state}

        # 6. Latency Evidence
        if profile.latency_ratio is not None and profile.latency_ratio >= 2.0:
            points += 1
            breakdown["latency"] = {"points": 1, "ratio": round(profile.latency_ratio, 2)}
        else:
            breakdown["latency"] = {"points": 0, "ratio": profile.latency_ratio}

        # 7. Consecutive Failures Indicator
        if profile.is_consecutive_failure and profile.consecutive_failures_count >= 2:
            points += 1
            breakdown["consecutive_failures"] = {"points": 1, "count": profile.consecutive_failures_count}

        # Categorical classification based on aggregate observable points
        if points >= 5:
            strength = EVIDENCE_STRENGTH_STRONG
        elif points >= 3:
            strength = EVIDENCE_STRENGTH_MODERATE
        else:
            strength = EVIDENCE_STRENGTH_WEAK

        audit_meta = {
            "total_evidence_points": points,
            "factor_breakdown": breakdown,
            "derived_strength": strength,
        }

        return strength, audit_meta
