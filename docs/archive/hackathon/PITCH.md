# PITCH.md — EduNavika
**Team:** Built by Team Varja  
**Core Positioning:** An on-device personalized learning assistant.

---

## 30-SECOND ELEVATOR PITCH

> *"Judges, when students get a math or science question wrong today, they're either handed a generic answer key or blocked by a chatbot that needs constant internet and expensive cloud APIs.  
> We built **EduNavika**—an on-device personalized learning assistant.  
> It tracks what a student actually knows, predicts forgetting curves, adapts practice difficulty, and explains concepts step-by-step using a local AI model grounded directly in state textbooks.  
> It runs 100% on the device on CPU, protects student privacy, and costs zero rupees in cloud API bills."*

---

## 60-SECOND HACKATHON PITCH

> *"Every student learns differently. But in Indian schools, learning materials are static, and generic AI chatbots suffer from two fatal flaws: they require constant high-speed internet that rural and tier-2 schools don't have, and they risk exposing minor students' learning data to third-party cloud servers.  
>  
> Introducing **EduNavika**, built by Team Varja.  
> EduNavika is an on-device personalized learning assistant. When a student attempts a question, EduNavika updates an empirical knowledge model—tracking mastery, accuracy trends, and memory decay.  
>  
> If a student struggles with balancing chemical equations, EduNavika doesn't just give the answer. It adapts practice difficulty to their foundational level, retrieves official textbook paragraphs from Standard 10 GSEB science, and uses an on-device small language model—Qwen2.5-0.5B—to generate structured, step-by-step explanations citing exact textbook page numbers.  
>  
> It runs entirely on commodity CPU hardware in under 5 seconds, works completely offline, and costs schools zero ongoing cloud fees. EduNavika makes personalized education truly private, accessible, and resilient."*

---

## 2-MINUTE DEEP DIVE PITCH

> *"Respected judges, consider two Standard 10 students. One student understands chemical reactions but consistently forgets equation coefficients under test pressure. Another student fundamentally doesn't know why atoms must balance. In existing classroom setups, both receive the exact same chapter quiz. Generic cloud chatbots are not the solution: they are stateless, they hallucinate, they require uninterrupted broadband, and they cost thousands of dollars in cloud token fees that government and budget schools cannot afford.  
>  
> Team Varja built **EduNavika** to bridge this gap.  
>  
> EduNavika is an **on-device personalized learning assistant** built on three foundational pillars:  
>  
> First, **Empirical Personalization**: Every quiz answer, hint click, and response latency is captured in an immutable learning event ledger. Our decay engine models memory half-lives to detect when a student is at risk of forgetting a concept before an exam. Practice difficulty dynamically adapts between Foundational, Guided, and Application tiers.  
>  
> Second, **Strict Curriculum Grounding**: EduNavika never answers from an unrestricted web knowledge base. We use local BM25 retrieval across official GSEB Standard 10 textbooks. Every explanation is anchored in verified syllabus material and cites exact textbook page numbers.  
>  
> Third, **Privacy-Preserving On-Device AI**: Powered by a quantized 468 MB small language model—Qwen2.5-0.5B—EduNavika runs local CPU inference in ~4.7 seconds at 61 tokens per second. Student data never leaves the hardware. And if the device has restricted memory, our dual-engine architecture engages a deterministic curriculum engine so learning never halts.  
>  
> Cloud APIs can be added as an optional adapter when high-speed internet exists, but EduNavika's core learning loop does not depend on cloud inference.  
>  
> EduNavika closes the loop between what a student gets wrong, what the system learns about that student, what they should practice next, and how the concept is explained. Thank you!"*
