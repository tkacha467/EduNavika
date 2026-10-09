# ARCHITECTURE.md
**Product:** EduNavika  
**Team:** Built by Team Varja  
**System Architecture:** On-Device Personalized Learning & Curriculum Retrieval  

---

## 1. System Architecture Diagram

```
+---------------------------------------------------------------------------------+
|                                STUDENT INTERFACE                                 |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   |   EduNavika Web Application (Vite + TypeScript SPA, Responsive UI)      |   |
|   |   - Topbar "● On-Device Ready" Status Indicator                         |   |
|   |   - Hero "Personalized Learning Path" (Live 4-Pillars Knowledge Card)   |   |
|   |   - Adaptive Practice Runner (Tiered Delivery & Feedback Loop)          |   |
|   |   - EduNavika AI Assistant Drawer (Structured Explanations & Citations) |   |
|   +-------------------------------------------------------------------------+   |
+----------------------------------------+----------------------------------------+
                                         |
                                         | REST API (Localhost / LAN)
                                         v
+---------------------------------------------------------------------------------+
|                         EDUNAVIKA BACKEND CORE (FastAPI)                        |
|                                                                                 |
|   +-------------------------------------------------------------------------+   |
|   | 1. KNOWLEDGE & PERSONALIZATION LAYER                                    |   |
|   |    - Learning Event Recorder (Immutable Interaction Ledger)             |   |
|   |    - Topic Knowledge Model (Mastery, Accuracy, Trend, Response Latency) |   |
|   |    - Retention & Forgetting Signal Engine (Half-life Decay Modeling)    |   |
|   |    - Adaptive Recommendation Engine (Topic & Difficulty Selection)      |   |
|   +------------------------------------+------------------------------------+   |
|                                        |                                        |
|                                        v                                        |
|   +-------------------------------------------------------------------------+   |
|   | 2. CURRICULUM KNOWLEDGE LAYER                                           |   |
|   |    - Topic-Scoped BM25 Local Content Retrieval                          |   |
|   |    - Official GSEB/NCERT Standard 10 Science Textbook Ingestion         |   |
|   |    - Provenance & Page Tracking (Preserves Exact Document & Page Ref)   |   |
|   +------------------------------------+------------------------------------+   |
|                                        |                                        |
|                                        v                                        |
|   +-------------------------------------------------------------------------+   |
|   | 3. INFERENCE & EXPLANATION ENGINE (DUAL-ENGINE RESILIENCE)              |   |
|   |                                                                         |   |
|   |    [PRIMARY] On-Device SLM (Local Inference)                           |   |
|   |    * Engine: llama-cpp-python (CPU-Only, n_gpu_layers=0)                |   |
|   |    * Model: Qwen2.5-0.5B-Instruct GGUF Q4_K_M (468.6 MB)                |   |
|   |    * Latency: ~4.7s warm on 4 CPU threads (61 tok/s)                    |   |
|   |    * Prompt Builder: Grounded in Retrieved Textbook Excerpts            |   |
|   |    * Structured Output: Core Concept, Step-by-Step, Misconception, Check|   |
|   |                                                                         |   |
|   |    [FALLBACK] Deterministic Curriculum Engine                           |   |
|   |    * Instant Zero-RAM Rule-Based Remediation                            |   |
|   |    * Automatically engaged on low memory, missing model, or error       |   |
|   |    * Displays "🔒 OFFLINE FALLBACK (Curriculum Engine)"                 |   |
|   |                                                                         |   |
|   |    [OPTIONAL FUTURE EXTENSION] Cloud LLM Adapter                        |   |
|   |    * (Optional cloud provider integration for connected schools)        |   |
|   |    * NOTE: EduNavika's core learning loop does NOT depend on cloud.     |   |
|   +-------------------------------------------------------------------------+   |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
+---------------------------------------------------------------------------------+
|                           LOCAL DATA & STORAGE LAYER                            |
|                                                                                 |
|   - SQLite Database (`backend/edunavika.db`): Zero-Network Data Persistence    |
|   - GGUF Weights (`models/qwen2.5-0.5b-instruct-q4_k_m.gguf`): Quantized Model  |
|   - Textbook Chunks (`learning_contents` table): NCERT/GSEB Aligned            |
+---------------------------------------------------------------------------------+
```

---

## 2. The Adaptive Learning Causal Chain

```
   Student Action (Practice Attempt)
              ↓
   Learning Event Recorded (Timestamp, Correctness, Latency, Topic)
              ↓
   Knowledge Profile Updated (Mastery Tier, Rolling Accuracy, Trend)
              ↓
   Forgetting Engine Evaluates Decay (Calculates Retention Risk)
              ↓
   Adaptive Recommendation Engine Selects Next Step
   ├── If Weak / Novice → Foundational Tier & Specific Concept Focus
   └── If Proficient   → Application Tier & Spaced Retention Review
              ↓
   Curriculum Retrieval Fetches Relevant Textbook Chunks (Pages 12, 17, 18)
              ↓
   On-Device SLM Generates Targeted Explanation Grounded in Retrieved Text
```
