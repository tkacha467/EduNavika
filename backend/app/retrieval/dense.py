from typing import List, Dict, Any, Optional
from backend.app.retrieval.embeddings.base import EmbeddingModel
from backend.app.retrieval.vector_store.base import VectorStore

class DenseRetriever:
    def __init__(self, embedding_model: EmbeddingModel, vector_store: VectorStore):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def add(self, texts: List[str], metadata: List[Dict[str, Any]]) -> None:
        if len(texts) != len(metadata):
            raise ValueError("Number of texts must match number of metadata items")
            
        embeddings = self.embedding_model.embed_documents(texts)
        self.vector_store.add(embeddings, metadata)

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k, filters)
        return results
