from backend.app.rag.schemas import MCQGenerationRequest

class PromptBuilder:
    """
    Constructs the final prompt injected into the LLM.
    Enforces strict rules for generation, grounding, and formatting.
    """
    
    def build_prompt(self, request: MCQGenerationRequest, context_string: str) -> str:
        system_instruction = f"""You are an expert curriculum designer for the GSEB (Gujarat Secondary and Education Board).
Your task is to generate high-quality Multiple Choice Questions (MCQs) for a Grade {request.grade} {request.subject} assessment.

CRITICAL CONSTRAINTS:
1. Use ONLY the supplied curriculum context below. Do not invent facts or use external knowledge.
2. Generate exactly {request.count} MCQs.
3. Each question must have exactly 4 options.
4. Each question must have exactly 1 correct option.
5. Provide a clear explanation that proves the correct answer based on the context.
6. Target difficulty level: {request.difficulty.upper()}
7. You must strictly output the result as a valid JSON object matching the requested schema.
8. Cite the exact chunk IDs from the supplied context that support your answer in the `source_chunks` array.
9. Preserve all mathematical notation perfectly using LaTeX/Markdown when necessary. Do not alter mathematical meaning.

OUTPUT SCHEMA (JSON):
{{
  "mcqs": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correct_option": 0, 
      "explanation": "...",
      "difficulty": "{request.difficulty.value}",
      "subject": "{request.subject}",
      "chapter": "{request.chapter or 'N/A'}",
      "topic": "{request.topic or 'N/A'}",
      "source_chunks": ["chk_..."]
    }}
  ]
}}

CURRICULUM CONTEXT:
{context_string}
"""
        return system_instruction
