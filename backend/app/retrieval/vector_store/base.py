from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class VectorStore(ABC):
    @abstractmethod
    def add(self, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> None:
        """Add embeddings with their corresponding metadata (e.g., chunk_id) to the store."""
        pass

    @abstractmethod
    def search(self, query_embedding: np.ndarray, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for top_k most similar vectors.
        Returns a list of dicts containing at least 'chunk_id' and 'score'.
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist the vector store to disk."""
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        """Load the vector store from disk."""
        pass
