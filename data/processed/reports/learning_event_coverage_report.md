# LearningEvent Telemetry Coverage & Data-Quality Audit Report

- **Quality Gate Verdict**: **`PASS`**
- **Audit Timestamp**: `2026-09-18T15:03:55.408545+00:00`
- **Total LearningEvents Audited**: **5**

---

## 1. Event Type Distribution

| Event Type | Description | Actual Event Count |
| :--- | :--- | :---: |
| `LEARN` | Content chunk reading / study session | **1** |
| `PRACTICE` | Formative question problem-solving | **1** |
| `MCQ_ATTEMPT` | Formal assessment item submission | **1** |
| `REVISION` | Scheduled spaced-repetition retrieval | **1** |
| `REVIEW` | Post-attempt review / solution inspection | **1** |
| **Total** | **All Longitudinal Events** | **5** |

---

## 2. Coverage & Entity Footprint

- **Active Students with Telemetry**: 1 / 1 (100.0%)
- **Active Topics with Telemetry**: 1 / 1 (100.0%)
- **Distinct Learning Sessions**: 0
- **Distinct Assessment Attempts**: 0

---

## 3. Data-Quality & Contract Violations

| Violation Check | Severity | Violations Detected |
| :--- | :---: | :---: |
| Negative Latency (`response_time_ms < 0`) | CRITICAL | 0 |
| Negative Score (`score < 0`) | CRITICAL | 0 |
| Missing Evaluative Correctness (`PRACTICE/MCQ/REVISION` null) | HIGH | 0 |
| Invalid `LEARN` Correctness (`LEARN` has correctness) | HIGH | 0 |
| Timestamp Duplicates (Identical student, topic, type, time) | MEDIUM | 0 |
| Orphan Student Foreign Keys | CRITICAL | 0 |
| Orphan Topic Foreign Keys | CRITICAL | 0 |
| Extreme Latency (> 180s, flagged for winsorization) | INFO | 0 |
| **Total Violations** | — | **0** |

---

## 4. Empirical Status Note

`PASS`: Zero data-quality violations detected across all recorded LearningEvents.
