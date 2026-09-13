# EduNavika — Machine Learning & Research Data Foundation

## 1. Executive Research Mandate

The primary scientific goal of EduNavika is to model and predict student memory retention, concept mastery, and cognitive decay in secondary school curricula (GSEB English-Medium Standards 9–12).

To achieve research-grade validity:
1. **Never substitute invented mathematical formulas for empirical evidence.**
2. **Never store only lossy aggregated metrics (e.g. `accuracy = 72%`).**
3. **Never introduce future outcome leakage into training features.**
4. **Preserve full curriculum provenance from the original GSEB textbook corpus.**
5. **Enforce `LearningEvent` as the authoritative source of truth for all ML research.**

---

## 2. Research Data Architecture: `LearningEvent` as the Sole Source of Truth

The EduNavika research pipeline strictly enforces the following data flow:

```
┌────────────────────────────────────────────────────────┐
│                  Student Interaction                   │
│        (Practice, Assessment, Reading, Review)         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             LearningEvent (Raw Observation)            │
│  - IMMUTABLE, APPEND-ONLY, LONGITUDINAL LOG            │
│  - AUTHORITATIVE SOURCE OF TRUTH                       │
│  - Granular: exact latency ms, hints, attempts, scores │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Temporal Feature Engineering               │
│  - Point-in-time reconstruction at cutoff time t       │
│  - Spacing intervals, latency trends, error dynamics   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Research Machine Learning Dataset          │
│  - Reconstructed from raw events with zero leakage     │
│  - Supports feature definition updates over time       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│      Empirical Retention Targets & Baseline Models     │
│  - Supervised labels observed in window [t, t + Δ]     │
│  - Cognitive modeling & knowledge tracing              │
└────────────────────────────────────────────────────────┘
```

### Critical Architectural Rule:
**ML research datasets MUST be reconstructed from raw `LearningEvent` records, NOT from `TopicPerformance`.**

```text
CORRECT RESEARCH PIPELINE:
LearningEvent ──► Feature Engineering ──► Research ML Dataset

INCORRECT / PROHIBITED:
LearningEvent ──► TopicPerformance ──► Research ML Dataset
```

### Why Raw Events Must Remain Available:
1. **Recomputability**: In educational data mining, feature definitions evolve constantly (e.g. changing sliding window sizes from 5 to 10 attempts, switching from arithmetic mean latency to exponential decay weighting). If only aggregates were stored, historical feature recomputation would be impossible.
2. **Sequence Sensitivity**: Knowledge tracing (BKT, DKT, AKT) requires the exact sequence of attempts $x_1, x_2, \dots, x_n$. Aggregations erase sequence order.
3. **Temporal Precision**: Decay modeling requires exact millisecond/second timestamps between consecutive study and recall episodes to calculate true spacing curves.

---

## 3. Application Evidence Aggregation: `TopicPerformance`

EduNavika maintains a clear separation between the **research evidence substrate** and the **application operational cache**:

```
┌────────────────────────────────────────────────────────┐
│             Raw Event Log (LearningEvent)              │
│  - Immutable, append-only, temporally ordered          │
│  - Authoritative source of truth for ML datasets       │
└───────────────────────────┬────────────────────────────┘
                            │ Maintained atomically on event write
                            ▼
┌────────────────────────────────────────────────────────┐
│       Evidence Aggregation (TopicPerformance)          │
│  - Application-facing operational cache                │
│  - Powers low-latency teacher/student dashboards       │
│  - Discrete heuristic state: UNASSESSED / NOVICE /     │
│    PRACTICING / MASTERED                               │
│  - NOT the research-grade mastery estimator            │
└────────────────────────────────────────────────────────┘
```

### Status of `mastery_state`:
- `TopicPerformance.mastery_state` is an **application-level display heuristic** (`UNASSESSED`, `NOVICE`, `PRACTICING`, `MASTERED`) designed for dashboard rendering.
- It is **NOT** a calibrated cognitive model or research-grade mastery estimator.
- **No pseudo-mathematical formulas** (e.g. `accuracy × practice_count` or arbitrary decay multipliers) are implemented.
- True mastery and latent knowledge states will be inferred by validated educational data mining models (e.g. Item Response Theory, Bayesian Knowledge Tracing) trained directly on `LearningEvent` sequences in future milestones.

---

## 4. `ForgettingSignal`: Empirical Evidence, NOT a Fake Probability

### The Pitfall of Invented Decay Curves
A pervasive flaw in naive educational software is assigning an arbitrary retention probability formula:
$$\hat{P}(\text{forget}) = 1 - e^{-t / S}$$
without empirical ground truth calibration, curriculum difficulty adjustments, or student-specific cognitive validation.

### The EduNavika Evidence Approach
In EduNavika, a `ForgettingSignal` is strictly an **empirical evidence representation**:
```text
evidence_type:                "ACCURACY_DROP_POST_INTERVAL"
evidence_strength:            "STRONG"  -- Categorical qualitative level (WEAK, MODERATE, STRONG). NOT A PROBABILITY.
prior_performance_reference:  {"accuracy": 100.0, "consecutive_success": 5, "last_date": "2026-08-01"}
later_performance_reference:  {"accuracy": 0.0, "latency_ms": 22400, "current_date": "2026-08-22"}
evidence_metadata:            {"days_elapsed": 21, "intervening_activities": 0}
```

- **No calibrated probability claim**: `evidence_strength` indicates whether the divergence meets qualitative evidentiary thresholds, not a mathematical likelihood.
- **Ground truth preservation**: Preserves the observable contrast between prior mastery and subsequent degradation, providing raw target candidate labels for subsequent ML evaluation.

---

## 5. Storage & Database Tier Separation

The system maintains a clean database separation:

| Tier | Technology | Purpose |
|---|---|---|
| **Development & CI/CD** | **SQLite** | Fast, zero-dependency local development and isolated in-memory automated test execution (`StaticPool`, `PRAGMA foreign_keys = ON;`). |
| **Production & Research** | **PostgreSQL** | Authoritative production hosting, high-throughput concurrent logging of `LearningEvent` streams, analytical queries, and longitudinal research exports. |

All SQLAlchemy 2.0 models maintain strict cross-dialect compatibility:
- Universal UUID representation (`String(36)`).
- Dialect-agnostic `JSON` types (SQLite `json` / PostgreSQL `JSONB`).
- Native enums (`SQLEnum`).
- Timezone-aware UTC timestamps (`DateTime(timezone=True)`).
- Explicit `CheckConstraint` and `UniqueConstraint` enforcement.

---

## 6. Strict Data Leakage Prevention Rules

When constructing longitudinal training sets from `LearningEvent`, the feature pipeline enforces strict temporal barriers:

```
Observation Window [t_0, t]             Prediction Target Window [t, t + Δ]
├─── Event 1 ─── Event 2 ─── Event 3 ───┤ ─── Future Attempt 1 ─── Future Attempt 2 ───┤
▲                                       ▲
Features extracted ONLY from events     Target labels (success / failure / latency)
strictly BEFORE or AT time t.           derived ONLY from events occurring in [t, t + Δ].
```

### Prohibited Leakage Rules:
1. **No Future Performance Leakage**: An assessment completed at $t_1 > t$ cannot be utilized in feature extraction for predictions at time $t$.
2. **No Global Lifetime Aggregation**: Cumulative student statistics must be bounded at cutoff time $t$, not computed over the complete lifespan of the database.
3. **No Retrospective Teacher Actions**: Teacher interventions (`teacher_actions`) logged after $t$ must not be visible to models predicting retention at $t$.

---

## 7. Future Feature Engineering Roadmap (Milestone 4+)

Derived exclusively from the immutable `LearningEvent` event stream:

| Feature Name | Computation from `LearningEvent` | Cognitive Meaning |
|---|---|---|
| `recency_days` | $t - \max(timestamp_{prior})$ | Elapsed time since last practice |
| `practice_count_30d` | $\text{count}(events \text{ where } t - 30d \le timestamp \le t)$ | Recent practice frequency |
| `short_term_accuracy` | $\text{mean}(correctness \text{ over last 5 attempts})$ | Immediate working memory state |
| `accuracy_trend` | Slope of linear regression over last 10 attempts | Mastery trajectory |
| `response_time_ratio` | $\text{mean}(latency_{\text{recent}}) / \text{mean}(latency_{\text{historical}})$ | Processing fluency vs. cognitive hesitation |
| `hint_request_rate` | $\sum hint\_used / \text{total attempts}$ | Scaffold dependency |
| `spacing_intervals` | Array of $\Delta t$ between consecutive successful sessions | Spacing effect representation |
| `cross_topic_transfer` | Performance on prerequisite topics in same chapter | Conceptual foundation strength |
