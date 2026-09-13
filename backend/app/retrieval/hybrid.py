from typing import List, Dict, Any, Optional
from backend.app.retrieval.lexical.bm25 import BM25Retriever
from backend.app.retrieval.dense import DenseRetriever
from backend.app.retrieval.rrf import reciprocal_rank_fusion

class HybridRetriever:
    def __init__(self, lexical_retriever: BM25Retriever, dense_retriever: DenseRetriever):
        self.lexical = lexical_retriever
        self.dense = dense_retriever

    def add(self, texts: List[str], metadata: List[Dict[str, Any]]) -> None:
        self.lexical.add(texts, metadata)
        self.dense.add(texts, metadata)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Fetch more results from sub-systems to improve fusion quality
        fetch_k = max(top_k * 2, 20)
        
        lexical_results = self.lexical.search(query, top_k=fetch_k, filters=filters)
        dense_results = self.dense.search(query, top_k=fetch_k, filters=filters)
        
        fused_results = reciprocal_rank_fusion([lexical_results, dense_results], k=60)
        
        return fused_results[:top_k]
