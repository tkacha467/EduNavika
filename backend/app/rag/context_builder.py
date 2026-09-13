from typing import List, Dict, Any, Tuple
from backend.app.retrieval.service import RetrievalResult

class ContextBuilder:
    """
    Constructs a deterministic, token-budgeted prompt context from retrieved chunks.
    Ensures only authorized provenance is injected into the LLM.
    """
    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.chars_per_token = 4 # Rough heuristic

    def build_context(self, results: List[RetrievalResult]) -> Tuple[str, List[str]]:
        """
        Takes retrieved results and builds a text string for the LLM.
        Returns the formatted context string and the list of chunk_ids that were actually included.
        """
        included_chunks = []
        seen_chunks = set()
        
        context_parts = []
        current_tokens = 0
        
        # We assume results are pre-sorted by rank
        for result in results:
            if result.chunk_id in seen_chunks:
                continue
                
            seen_chunks.add(result.chunk_id)
            
            # Format chunk with strict provenance framing
            chunk_text = f"[CHUNK_ID: {result.chunk_id}]\n"
            if result.standard:
                chunk_text += f"Grade: {result.standard}\n"
            if result.subject:
                chunk_text += f"Subject: {result.subject}\n"
            if result.chapter:
                chunk_text += f"Chapter: {result.chapter}\n"
            if result.source_page:
                chunk_text += f"Page: {result.source_page}\n"
                
            chunk_text += f"\nCONTENT:\n{result.content}\n"
            chunk_text += "-" * 40 + "\n"
            
            # Token budget check
            estimated_tokens = len(chunk_text) // self.chars_per_token
            if current_tokens + estimated_tokens > self.max_tokens:
                # Stop including chunks once we hit the token budget
                break
                
            context_parts.append(chunk_text)
            included_chunks.append(result.chunk_id)
            current_tokens += estimated_tokens
            
        final_context_string = "\n".join(context_parts)
        return final_context_string, included_chunks
