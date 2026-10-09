# EduNavika — On-Device Personalized Learning Assistant
**Built by Team Varja**  
*Hackathon Submission & Project Documentation*

---

## 1. The Problem
Millions of school students in India and emerging regions lack consistent, high-speed internet connectivity. They attend schools with constrained infrastructure and cannot afford recurring subscription fees for cloud AI services. Simultaneously, schools cannot risk transmitting minor students' data, learning records, and evaluation metrics to external cloud APIs. As a result, students are left with static, one-size-fits-all textbooks and generic question banks that fail to address individual learning gaps.

## 2. The Solution
**EduNavika** is an **on-device personalized learning assistant** that understands what an individual student knows, identifies what concept they need next, provides curriculum-grounded step-by-step explanations, and dynamically adapts practice difficulty. It runs **100% locally on low-resource hardware** without constant internet connectivity.

## 3. Key Innovations
- **Longitudinal Student Knowledge Model:** Beyond one-off chat queries, EduNavika records timestamped `LearningEvents` to model empirical mastery, rolling accuracy, performance trends, and forgetting curves.
- **On-Device Small Language Model (SLM):** Uses `Qwen2.5-0.5B-Instruct` quantized to GGUF `Q4_K_M` running CPU-only (~468 MB), delivering private, responsive AI explanations on commodity hardware.
- **Curriculum-Grounded Retrieval:** Topic-scoped BM25 search over official Gujarat State Board (GSEB) and NCERT Standard 10 Science textbooks. The AI answers strictly from retrieved curriculum paragraphs and cites exact textbook page numbers.
- **Dual-Engine Offline Fallback:** If the local model cannot be loaded or system resources are restricted, EduNavika transitions seamlessly to a rule-based deterministic curriculum engine. Zero crashes, zero blank screens.

---

## 4. System Architecture

```
Student Attempt / Query
          ↓
EduNavika Frontend (Vite + TypeScript SPA)
          ↓
FastAPI Backend (Localhost / LAN Server)
          ├── 1. Knowledge Model & Decay Engine (Mastery, Accuracy, Forgetting Signals)
          ├── 2. Adaptive Recommendation Engine (Topic Selection & Difficulty Tiering)
          ├── 3. Topic-Scoped BM25 Curriculum Retrieval (Official GSEB Textbooks)
          └── 4. Dual Explanation Engine:
                  ├── [Primary] Local Qwen2.5-0.5B-Instruct (llama-cpp-python CPU-only)
                  └── [Fallback] Deterministic Curriculum Engine
          ↓
Local SQLite Storage (`edunavika.db`) & Model Weights (`models/qwen2.5-0.5b-instruct-q4_k_m.gguf`)
```

> **Note on Cloud Connectivity:** EduNavika is **offline-first**. Cloud inference can be added as an optional adapter when high-speed connectivity is available, but the core learning loop does not depend on cloud inference.

---

## 5. The Personalization & Adaptive Practice Loop
1. **Student Attempts a Question:** Intentionally or unintentionally makes a mistake.
2. **Learning Event Persisted:** Accuracy, timestamp, latency, and hint usage are recorded.
3. **Knowledge Model Recomputes:**
   - Mastery is evaluated (Novice, Developing, Proficient, Mastered).
   - Rolling recent accuracy drops; trend updates.
   - Forgetting risks and specific missed sub-concepts are flagged.
4. **Practice Adapts:** The next practice set shifts down to `FOUNDATIONAL` difficulty and isolates the exact missed concept.
5. **On-Device AI Remediation:** The student can ask EduNavika AI, which formulates a targeted explanation grounded in official textbook pages.

---

## 6. Real Performance Benchmark (CPU-Only)
Verified on standard commodity x86_64 CPU (4 threads, zero GPU acceleration, `n_gpu_layers=0`):
- **Model Size:** 468.64 MB (GGUF Q4_K_M)
- **RAM Footprint:** ~550 MB during active inference
- **Cold / First-Run Latency:** ~6.65 seconds
- **Warm Latency:** ~3.8 – 5.5 seconds (Average: **4.71 seconds**)
- **Generation Speed:** **~61.05 tokens per second**
- **External API Calls:** Exactly 0.

---

## 7. Technology Stack
- **Frontend:** TypeScript, Vite, Modern Responsive Web Components, CSS Grid & Flexbox
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Local AI Inference:** `llama-cpp-python`, `Qwen2.5-0.5B-Instruct` (GGUF Q4_K_M)
- **Curriculum Search:** Rank-BM25 local search over tokenized GSEB Standard 10 textbooks

---

## 8. Quick Start / Demo Instructions

### Prerequisites
- Python 3.11 with virtual environment installed at `.venv`
- Node.js 18+

### Setup & Launch
1. Ensure `.env` is configured:
   ```env
   ENV=development
   DATABASE_URL=sqlite:///./edunavika.db
   EDUNAVIKA_LOCAL_MODEL_PATH=D:\EduNavika\models\qwen2.5-0.5b-instruct-q4_k_m.gguf
   LOCAL_LLM_N_THREADS=4
   LOCAL_LLM_N_CTX=2048
   ```
2. Start the Backend:
   ```powershell
   & "D:\EduNavika\.venv\Scripts\uvicorn.exe" backend.app.main:app --port 8000
   ```
3. Start the Frontend:
   ```powershell
   npm --prefix frontend run dev
   ```
4. Access `http://localhost:5173` and follow [`DEMO_CHECKLIST.md`](./DEMO_CHECKLIST.md) for the 5-minute judge walkthrough.
