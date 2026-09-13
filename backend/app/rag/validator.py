import json
from typing import List, Tuple
from backend.app.rag.schemas import MCQBatchResponse, GeneratedMCQ

class StructuralValidator:
    """
    Layer A: Structural Validation
    Validates JSON integrity, schema adherence, option constraints, and strict provenance subset mapping.
    """
    def validate(self, llm_output: str, allowed_chunk_ids: List[str], expected_count: int) -> Tuple[bool, str, MCQBatchResponse]:
        try:
            data = json.loads(llm_output)
            # Pydantic validates basic types, 4 options, not empty, correct_option bounds
            batch = MCQBatchResponse.model_validate(data)
        except Exception as e:
            return False, f"JSON/Schema validation failed: {str(e)}", None
            
        if len(batch.mcqs) != expected_count:
            return False, f"Expected {expected_count} MCQs, got {len(batch.mcqs)}", None
            
        # Strict provenance subset validation
        allowed_set = set(allowed_chunk_ids)
        for i, mcq in enumerate(batch.mcqs):
            for chunk_id in mcq.source_chunks:
                if chunk_id not in allowed_set:
                    return False, f"MCQ {i} cites unauthorized chunk_id: {chunk_id}", None
                    
        return True, "Success", batch

class SemanticValidator:
    """
    Layer B: Grounding/Content Validation (Stub for M4.0)
    Ensures correct answers are supported, explanations are faithful, and no hallucinations exist.
    """
    def validate(self, batch: MCQBatchResponse, context_string: str) -> Tuple[bool, str]:
        # For Milestone 4.0, we assume structural validation is enough to pass the contract.
        # Deep semantic validation requires a cross-encoder or a strong judge LLM.
        return True, "Semantic validation not implemented in M4.0"
