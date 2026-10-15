# JUDGE_TALKING_POINTS.md
**Product:** EduNavika  
**Team:** Built by Team Varja  
**Positioning:** On-Device Personalized Learning Assistant for School Education  

---

### Q1. What problem are you solving?
**Answer:** Millions of school students across India lack continuous high-speed internet and cannot afford recurring subscription fees for cloud AI tutors. Furthermore, schools cannot risk transmitting minor student learning records to third-party cloud servers. EduNavika provides an on-device personalized learning assistant that tracks empirical mastery, adapts practice, and explains concepts privately without cloud dependence.

### Q2. Why not ChatGPT?
**Answer:**
1. **Curriculum Grounding:** ChatGPT answers from broad internet pre-training without state board syllabus alignment. EduNavika retrieves and cites exact paragraphs from official GSEB/NCERT textbooks (*e.g., STD-10 Science Pages 12, 17, 18*).
2. **Longitudinal Student Memory:** ChatGPT is stateless per chat session. EduNavika maintains a persistent `LearningEvent` ledger to compute memory decay and guide revision.
3. **Zero Connectivity & Zero API Costs:** Runs CPU-only on local devices, costing ₹0 in cloud API tokens.

### Q3. Why use a 0.5B parameter model?
**Answer:** `Qwen2.5-0.5B-Instruct` quantized to GGUF `Q4_K_M` occupies only 468.6 MB of storage and ~550 MB of RAM. It fits comfortably on low-resource budget PCs and school lab desktops, executing in ~4.7 seconds on standard CPUs without requiring expensive NVIDIA GPUs.

### Q4. Isn't a 0.5B model too small to be smart?
**Answer:** When asked to answer broad encyclopedic trivia, small models hallucinate. However, EduNavika uses **Retrieval-Augmented Generation (RAG)**: the local BM25 retriever fetches verified paragraphs from the textbook and injects them into the prompt. The 0.5B model's task is constrained to reading comprehension, step-by-step formatting, and pedagogical synthesis, which it performs accurately and quickly.

### Q5. Why not use a cloud LLM?
**Answer:** Cloud LLMs fail when school broadband drops, incur recurring per-token subscription costs that public schools cannot sustain, and expose student evaluation data to external cloud networks.

### Q6. What happens without internet?
**Answer:** 100% of the demonstration loop works offline. Local SQLite stores student attempts, local BM25 indexes the curriculum textbooks, and quantized GGUF weights execute inference on the CPU.

### Q7. How do you personalize learning?
**Answer:** Through an empirical 4-pillar **Student Knowledge Model** per topic tracking:
- **Mastery Level:** (Novice, Developing, Proficient, Mastered)
- **Rolling Longitudinal Accuracy:** (Recent attempts vs baseline)
- **Performance Trend:** (Improving, Stable, Declining)
- **Retention Risk / Forgetting Curve:** (Memory decay calculated from elapsed time and response latencies)

### Q8. How do you calculate mastery?
**Answer:** We evaluate evidence thresholds:
- *Novice:* Accuracy < 50% or fewer than 3 attempts.
- *Developing:* Accuracy 50%–69% with $\ge 3$ attempts.
- *Proficient:* Accuracy 70%–84% with $\ge 3$ attempts.
- *Mastered:* Accuracy $\ge 85\%$ with $\ge 5$ attempts.

### Q9. How do you identify weak areas?
**Answer:** Every interaction records an immutable `LearningEvent`. The decay engine aggregates rolling accuracy, tracks time elapsed, and raises `ForgettingSignals` when performance declines or a topic goes unrevised.

### Q10. How does forgetting/retention work?
**Answer:** Based on Ebbinghaus forgetting dynamics: stability is calculated from prior consecutive successes, and retention drops exponentially with time elapsed. If retention falls below the critical threshold, EduNavika flags high retention risk and schedules spaced revision.

### Q11. How do recommendations change?
**Answer:** If a student gets a question wrong, their rolling accuracy drops and their trend updates to Declining. The recommendation engine immediately shifts difficulty to `FOUNDATIONAL` and targets the specific missed sub-concept. When accuracy recovers, difficulty advances to `APPLICATION`.

### Q12. How do you prevent hallucination?
**Answer:**
1. System prompt strictly constrains answers to provided curriculum context.
2. Structured output parsing enforces rigid sections (Core concept, Step-by-step, Common misconception, Quick check).
3. If retrieval fails or returns insufficient context, the system defaults to the deterministic curriculum engine.

### Q13. How is curriculum grounding done?
**Answer:** Official GSEB Standard 10 Science textbooks are chunked with exact page numbers and indexed via topic-scoped BM25. Top chunks are injected into the prompt and cited explicitly.

### Q14. What happens if the local model fails?
**Answer:** EduNavika features a dual-engine architecture. If the local model encounters an Out-Of-Memory (OOM) condition or is disabled, the system automatically falls back to the **Deterministic Curriculum Engine**, displaying **`🔒 OFFLINE FALLBACK`** with full textbook provenance and zero crash.

### Q15. What makes this scalable?
**Answer:** Because the application is self-contained and lightweight (~550 MB RAM, ~468 MB disk), it can be deployed on existing school computer labs or bundled onto offline USB drives without new infrastructure. Alternatively, one local teacher desktop can act as a local LAN edge server for the classroom.

### Q16. How is student privacy protected?
**Answer:** All database records, user profiles, and AI queries remain in local storage (`edunavika.db`). No telemetry, prompt data, or student records are transmitted over the internet.

### Q17. What is the latency?
**Answer:** On standard commodity x86_64 CPU (4 threads, zero GPU):
- Cold / first-run inference: ~6.65 seconds
- Warm inference: **~3.8 – 5.5 seconds** (Average: ~4.7 seconds)
- Generation speed: **~61 tokens per second**, outperforming human reading speed.

### Q18. What hardware is required?
**Answer:** Any standard budget PC or laptop with 4 CPU threads and at least 1 GB of available RAM. No dedicated GPU or NPU is required.

### Q19. Can cloud APIs be used?
**Answer:** Yes. Cloud LLM providers can be integrated as an optional enhancement layer for school labs with high-speed internet. However, **EduNavika's core learning loop does not depend on cloud inference**.

### Q20. What would you build next?
**Answer:** 
1. Ingest remaining Grade 10 subjects (Mathematics, Social Science, English) into the BM25 retrieval index.
2. Multilingual local speech-to-text and text-to-speech for regional Indian languages (Gujarati, Hindi) on device.
3. Teacher classroom aggregation dashboard that synchronizes locally over school Wi-Fi without internet.
