import os
import faiss
import numpy as np
import json
from typing import List, Dict, Any, Optional
from backend.app.retrieval.vector_store.base import VectorStore

class FAISSStore(VectorStore):
    def __init__(self, dimension: int, use_cosine_similarity: bool = True):
        self.dimension = dimension
        self.use_cosine_similarity = use_cosine_similarity
        
        if use_cosine_similarity:
            self.index = faiss.IndexFlatIP(dimension) # Inner product (requires normalized vectors for cosine similarity)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            
        self.metadata: List[Dict[str, Any]] = []

    def add(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata items")
        
        # Assume embeddings are already normalized if using cosine similarity
        self.index.add(embeddings)
        self.metadata.extend(metadata)

    def search(self, query_embedding: np.ndarray, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # query_embedding shape should be (1, dim)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
            
        # If we have filters, we need to retrieve more results and filter them post-retrieval
        # because FAISS IndexFlatIP doesn't support metadata filtering natively.
        search_k = top_k
        if filters:
            # Retrieve a larger pool to allow for post-filtering
            search_k = min(self.index.ntotal, max(top_k * 10, self.index.ntotal))

        distances, indices = self.index.search(query_embedding, search_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
            
            meta = self.metadata[idx]
            
            # Post-filtering
            if filters:
                match = True
                for k, v in filters.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
            
            # Similarity score calculation (Inner product is already cosine similarity if normalized)
            score = float(distances[0][i])
            if not self.use_cosine_similarity:
                score = 1.0 / (1.0 + score) # Convert L2 to a similarity score

            results.append({
                "chunk_id": meta.get("chunk_id"),
                "score": score,
                "metadata": meta,
                "retrieval_method": "dense"
            })
            
            if len(results) == top_k:
                break
                
        return results

    def save(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)
        faiss.write_index(self.index, os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(self.metadata, f)

    def load(self, path: str) -> None:
        self.index = faiss.read_index(os.path.join(path, "index.faiss"))
        with open(os.path.join(path, "metadata.json"), "r") as f:
            self.metadata = json.load(f)
        self.dimension = self.index.d
