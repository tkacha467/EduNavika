from typing import List, Dict, Any, Optional
import numpy as np
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self):
        self.bm25 = None
        self.metadata: List[Dict[str, Any]] = []
        self.corpus_tokens: List[List[str]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Simple whitespace tokenization, could be extended with NLTK/spaCy if needed
        return text.lower().split()

    def add(self, texts: List[str], metadata: List[Dict[str, Any]]) -> None:
        if len(texts) != len(metadata):
            raise ValueError("Number of texts must match number of metadata items")
            
        new_tokens = [self._tokenize(text) for text in texts]
        self.corpus_tokens.extend(new_tokens)
        self.metadata.extend(metadata)
        
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search the BM25 index and optionally filter by metadata.
        """
        if not self.bm25:
            raise ValueError("BM25 index has not been built. Call add() first.")
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        
        # Filter logic
        valid_indices = set(range(len(self.metadata)))
        if filters:
            valid_indices = set()
            for idx, meta in enumerate(self.metadata):
                match = True
                for k, v in filters.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if match:
                    valid_indices.add(idx)
                    
        # Sort by scores descending
        top_indices = np.argsort(scores)[::-1]
        
        results = []
        for idx in top_indices:
            score = scores[idx]
            if score <= 0:
                break
            
            if idx not in valid_indices:
                continue
                
            meta = self.metadata[idx]
            
            results.append({
                "chunk_id": meta.get("chunk_id"),
                "score": float(score),
                "metadata": meta,
                "retrieval_method": "bm25"
            })
            
            if len(results) == top_k:
                break
                
        return results
