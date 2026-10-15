# ARCHITECTURE_PRESENTATION.md
**Product:** EduNavika  
**Team:** Built by Team Varja  
**Topic:** Technical Architecture & Pedagogical Data Flow  

---

## 1. End-to-End Learning Loop Architecture

```
Student Attempt
      ↓
[1. Learning Event Recorder]
  - Immutable Event Ledger (Timestamp, Topic, Correctness, Latency, Hint Usage)
      ↓
[2. Knowledge Model Service]
  - Empirical 4-Pillar Profiling:
      * Mastery Level (Novice, Developing, Proficient, Mastered)
      * Rolling Longitudinal Accuracy (Recent vs Baseline)
      * Performance Trend (Improving, Stable, Declining)
      * Retention Risk / Forgetting Curve (Memory half-life modeling)
      ↓
[3. Recommendation & Adaptive Engine]
  - Selects Priority Topic & Difficulty Tier (Foundational, Guided, Application, Challenge)
      ↓
[4. Adaptive Practice Generator]
  - Formulates curriculum-aligned practice questions targeting specific weaknesses
      ↓
Student Submits Answer → Updated Learning Evidence Loop Continues
```

---

## 2. On-Device Explanation Engine Pipeline

```
Student Question ("I don't understand how to balance chemical equations")
      ↓
[1. Student Knowledge Profile]
  - Extracts current mastery tier (`NOVICE`) and recent error notes
      ↓
[2. Recommendation Context]
  - Priority: Foundational balancing rules
      ↓
[3. Topic-Scoped BM25 Curriculum Retrieval]
  - Local index of official GSEB Standard 10 Science textbook
  - Returns top-scoring paragraphs with verified page numbers (e.g. Pages 12, 17, 18)
      ↓
[4. Pedagogical Prompt Builder]
  - Constrains generation strictly to retrieved textbook text
  - Enforces structured JSON schema: Core Concept, Step-by-Step, Misconception, Quick Check
      ↓
[5. Local Quantized SLM Inference]
  - Model: Qwen2.5-0.5B-Instruct (GGUF Q4_K_M, 468 MB)
  - Engine: llama-cpp-python running CPU-only (4 threads, n_gpu_layers=0)
  - Performance: ~4.7s warm latency, ~61 tokens/sec
      ↓
[6. Structured Response & Citations]
  - Badged: ⚡ ON-DEVICE AI · Qwen2.5-0.5B-Instruct
  - Citations: STD-10 Science Pages 12, 17, 18
```

---

## 3. Dual-Engine Resilience & Fallback

```
                     On-Device Request
                             ↓
             Is local GGUF model available?
                   /                    \
                [YES]                  [NO]
                 /                        \
    [Primary Engine]             [Fallback Engine]
  Local Qwen2.5-0.5B            Deterministic Curriculum
  llama-cpp-python CPU          Rule-Based Grounded Engine
  ~4.7s inference               Instant 0ms, Zero RAM
  Badge: ⚡ ON-DEVICE AI        Badge: 🔒 OFFLINE FALLBACK
                 \                        /
                  \                      /
             Identical Structured Curriculum Output
             Verified Textbook Page Citations (12, 17, 18)
             Zero Crashes · Uninterrupted Learning
```

---

## 4. Optional Cloud Expansion Architecture

```
                       STUDENT INTERFACE
                               ↓
                        EDUNAVIKA CORE
                               ↓
             Is Internet Available & High-Bandwidth?
                   /                        \
                [NO / OFFLINE]            [YES / CONNECTED]
                 /                            \
      [DEFAULT ON-DEVICE LOOP]       [OPTIONAL CLOUD ADAPTER]
      * Qwen2.5-0.5B-Instruct        * Optional Cloud Model Endpoint
      * 100% Offline                 * (For high-bandwidth labs)
      * Zero API Cost                * NOTE: Core learning loop
      * Private by Design              does NOT depend on cloud.
```
