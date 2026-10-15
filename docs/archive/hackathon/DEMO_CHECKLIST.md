# DEMO_CHECKLIST.md
**Product:** EduNavika  
**Team:** Built by Team Varja  
**Target Scenario:** Grade 10 GSEB Science — Chemical Reactions & Equations  

---

## 1. PRE-DEMO CHECKLIST (Run 10 Minutes Before Presentation)

- [ ] **Backend Environment Verified:**
  - Python virtual environment is activated (`.venv`).
  - `.env` file exists and contains `EDUNAVIKA_LOCAL_MODEL_PATH=D:\EduNavika\models\qwen2.5-0.5b-instruct-q4_k_m.gguf`.
  - Database file exists: `backend/edunavika.db` (500+ KB).
  - Model weight exists: `models/qwen2.5-0.5b-instruct-q4_k_m.gguf` (468.64 MB).
- [ ] **Servers Started:**
  - Backend running: `uvicorn backend.app.main:app --port 8000` (returns 200 on `/docs`).
  - Frontend running: `npm --prefix frontend run dev` (or served from `dist/` on port 5173/3000).
- [ ] **Warm-up Local SLM Once:**
  - Open AI panel and trigger a quick prompt to pre-allocate model weights into RAM cache.
  - Verifies warm inference runs in ~4.7 seconds on CPU.
- [ ] **Student Account Live:**
  - Login as Demo Student (`e09699dd-0c64-44cc-82ef-ab41a832e072`).
  - Verify Hero card displays **Chemical Reactions and Equations** with Mastery `NOVICE`.
- [ ] **Browser Prepared:**
  - Open browser at `http://localhost:5173`.
  - Check browser console is clean (zero breaking unhandled exceptions).
  - Verify topbar indicator shows `● On-Device Ready`.

---

## 2. 5-MINUTE HACKATHON LIVE DEMO SCRIPT

### ⏱️ 0:00 – 0:30 | Introduction & Privacy Vision
- **Say:** *"Judges, this is EduNavika, built by Team Varja. We built EduNavika to solve a fundamental barrier in Indian school education: personalized learning without depending on continuous internet or costly cloud APIs."*
- **Action:** Point to the top bar: **`● On-Device Ready`**.
- **Key point:** *"Everything you see today—the student knowledge model, the adaptive recommendations, and the AI explanation model—runs locally on this device."*

### ⏱️ 0:30 – 1:15 | The Personalized Learning Path (Hero)
- **Say:** *"Instead of throwing generic question banks at students, EduNavika models what the student knows across 4 empirical dimensions."*
- **Action:** Point to the Hero card: **YOUR PERSONALIZED LEARNING PATH**.
- **Highlight:**
  - Topic: **Chemical Reactions and Equations** (Standard 10 GSEB Science).
  - 4 Pillars: **Mastery** (`NOVICE`), **Recent Accuracy** (`80.0%`), **Retention Risk** (`MODERATE`), **Trend** (`IMPROVING`).
  - Pedagogical explanation: *"Why this topic? Mastery is NOVICE with 80% accuracy — targeting foundational concepts."*
  - Textbook Provenance: *STD-10 Science Pages 12–15*.

### ⏱️ 1:15 – 2:00 | Adaptive Practice & Wrong-Answer Adaptation
- **Say:** *"Let's launch practice. Notice how the difficulty adapts."*
- **Action:** Click **Practice Now**.
- **Highlight:** Target Tier is **FOUNDATIONAL** based on the knowledge model.
- **Action:** Intentionally answer Question 1 incorrectly (select an incorrect option and click **Submit Answer**).
- **Highlight:** 
  - Immediate pedagogical feedback: *"Not quite. Notice that the correct principle is 'To satisfy the law of conservation of mass' (Textbook Page 14)."*
  - **Knowledge Model Adaptation Card:** Explains that the error was recorded in local memory, the rolling accuracy was updated, and the system targets this exact concept for remediation.

### ⏱️ 2:00 – 3:30 | Ask EduNavika AI (Local On-Device SLM)
- **Say:** *"Now the student is confused about balancing equations. Let's ask our on-device assistant for help."*
- **Action:** Click **"Ask EduNavika AI to explain this"** (or click the quick demo prompt: *"I don't understand how to balance chemical equations"*).
- **Highlight:**
  - Watch the live generation on CPU.
  - Badge: **`⚡ ON-DEVICE AI · Qwen2.5-0.5B-Instruct`** with live generation latency.
  - **Curriculum Grounding:** Explicitly shows *STD-10 Science (Page 17 · Page 18)*.
  - Structured sections:
    1. *Why this explanation?* (Tailored to student's NOVICE level).
    2. *Core Concept* (Drawing boxes, counting atoms).
    3. *Step-by-Step Understanding*.
    4. *Misconception to avoid*.
    5. *Quick Concept Check*.
- **Key point:** *"Notice there was no internet call, no OpenAI API key, and no cloud server. The SLM synthesized retrieved textbook chunks right on this CPU at ~60 tokens per second."*

### ⏱️ 3:30 – 4:15 | Resilience & Offline Fallback
- **Say:** *"What if this runs on a low-end school computer without enough RAM for the model?"*
- **Highlight:** EduNavika includes a built-in **Deterministic Curriculum Fallback**. If the local model is missing or disabled, the system transitions gracefully to **`🔒 OFFLINE FALLBACK (Curriculum Engine)`**—preserving the exact same textbook citations and structured learning without crashing.

### ⏱️ 4:15 – 5:00 | Closed-Loop Progress & Conclusion
- **Action:** Return to practice, select the correct answer on the next question, and submit.
- **Highlight:** Accuracy recovers, the learning curve advances, and the next practice set recalculates.
- **Closing statement:** *"EduNavika is private by design, offline-capable, curriculum-grounded, and personalized. Thank you!"*
