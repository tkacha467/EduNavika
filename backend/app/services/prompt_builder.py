from typing import List, Optional
from backend.app.schemas.knowledge_profile import TopicKnowledgeProfile
from backend.app.schemas.recommendation import TopicRecommendation
from backend.app.schemas.retrieval import RetrievedContentItem


class ExplanationPromptBuilder:
    """
    Dedicated prompt builder for on-device SLM (Qwen2.5-0.5B-Instruct).
    Constructs highly structured, curriculum-grounded prompts adhering to the local SLM instruction format.
    Does NOT include full database or full textbook dumps — includes strictly bounded context.
    """

    SYSTEM_INSTRUCTION = """You are EduNavika's on-device learning assistant running locally on a student's personal computer.
Your mission is to teach the requested topic adapting strictly to the student's mastery level and ground your explanation exclusively on the supplied textbook curriculum context.

STRICT INSTRUCTIONS:
1. Teach at the student's current mastery level (e.g., Novice needs simple analogies; Proficient needs exam application).
2. Ground your facts strictly on the provided CURRICULUM CONTEXT. Do NOT invent curriculum facts or hallucinate outside the syllabus.
3. If the context does not contain sufficient information, state that clearly.
4. Keep the explanation concise, pedagogical, and clear.
5. Do NOT repeat sentences or list items. Every step must be distinct, non-repeating, and under 25 words.
6. Do NOT output stray markdown asterisks (**) or bullet repetition loops.
7. Provide:
   - CORE CONCEPT: Explain the key idea in plain language.
   - STEP BY STEP: 2-3 structured learning steps.
   - COMMON MISCONCEPTION: One frequent mistake students make.
   - QUICK CHECK: One question with expected key concept.
   - NEXT ACTION: One immediate practical exercise to practice.
"""


    @classmethod
    def build_prompt(
        cls,
        topic_title: str,
        knowledge_profile: TopicKnowledgeProfile,
        recommendation: Optional[TopicRecommendation],
        retrieved_contexts: List[RetrievedContentItem],
        student_query: Optional[str] = None,
        recent_error_notes: Optional[List[str]] = None,
    ) -> str:
        """
        Builds the complete prompt separating:
        1. STUDENT PROFILE
        2. RECOMMENDATION
        3. CURRICULUM CONTEXT
        4. STUDENT QUESTION
        """
        # Section 1: Student Profile
        mastery_str = knowledge_profile.mastery_level.value if hasattr(knowledge_profile.mastery_level, "value") else str(knowledge_profile.mastery_level)
        trend_str = knowledge_profile.trend.value if hasattr(knowledge_profile.trend, "value") else str(knowledge_profile.trend)
        risk_str = knowledge_profile.retention_risk.value if hasattr(knowledge_profile.retention_risk, "value") else str(knowledge_profile.retention_risk)

        profile_lines = [
            f"- Topic: {topic_title}",
            f"- Mastery Level: {mastery_str}",
            f"- Accuracy: {knowledge_profile.accuracy:.1f}%",
        ]
        if knowledge_profile.recent_accuracy is not None:
            profile_lines.append(f"- Recent Accuracy: {knowledge_profile.recent_accuracy:.1f}%")
        profile_lines.append(f"- Performance Trend: {trend_str}")
        profile_lines.append(f"- Retention/Forgetting Risk: {risk_str}")

        # Pedagogical Explanation Depth Guidance
        if mastery_str in ("NOVICE", "UNASSESSED") or knowledge_profile.accuracy < 50.0:
            profile_lines.append("- Pedagogical Approach: FOUNDATIONAL REMEDIATION (Use simple language, intuitive everyday analogies, step-by-step worked reasoning, and unpack elementary rules).")
        elif mastery_str == "DEVELOPING" or knowledge_profile.accuracy < 70.0:
            profile_lines.append("- Pedagogical Approach: GUIDED STRENGTHENING (Reinforce core principles, introduce multi-step problem solving, and highlight common procedural errors).")
        elif mastery_str == "PROFICIENT" or knowledge_profile.accuracy < 85.0:
            profile_lines.append("- Pedagogical Approach: ADVANCED APPLICATION (Provide concise conceptual reasoning, emphasize board-exam question patterns, and explore chemical conditions).")
        else:
            profile_lines.append("- Pedagogical Approach: SYNTHESIS & MASTERY (Offer rapid high-level synthesis, cross-chapter concept connections, and challenging board-exam extensions).")

        if recent_error_notes:
            profile_lines.append(f"- Recent Struggling Areas: {', '.join(recent_error_notes)}")

        student_profile_sec = "\n".join(profile_lines)

        # Section 2: Recommendation
        if recommendation:
            rec_action_str = recommendation.action.value if hasattr(recommendation.action, "value") else str(recommendation.action)
            rec_prio_str = recommendation.priority.value if hasattr(recommendation.priority, "value") else str(recommendation.priority)
            rec_sec = f"- Recommended Action: {rec_action_str} (Priority: {rec_prio_str})\n- Reason: {recommendation.reason}"
        else:
            rec_sec = f"- Recommended Action: PRACTICE\n- Reason: Standard review for {topic_title}"

        # Section 3: Curriculum Context (Top grounded chunks only, with page citations)
        if retrieved_contexts:
            context_chunks = []
            for i, ctx in enumerate(retrieved_contexts[:3], 1):
                page_info = f" [Textbook Page {ctx.source_page}]" if ctx.source_page else ""
                clean_snippet = " ".join(ctx.content_text.split()[:120])
                context_chunks.append(f"Excerpt {i}{page_info}:\n\"{clean_snippet}\"")
            curriculum_sec = "\n\n".join(context_chunks)
        else:
            curriculum_sec = f"Standard NCERT / GSEB Class 10 Syllabus for {topic_title}."

        # Section 4: Student Query
        user_query = student_query.strip() if student_query and student_query.strip() else f"Please explain {topic_title} step by step."

        prompt = f"""=== STUDENT PROFILE ===
{student_profile_sec}

=== RECOMMENDATION ===
{rec_sec}

=== CURRICULUM CONTEXT ===
{curriculum_sec}

=== STUDENT QUESTION ===
{user_query}
"""
        return prompt
