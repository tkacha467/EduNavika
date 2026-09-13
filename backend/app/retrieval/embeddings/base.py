from abc import ABC, abstractmethod
from typing import List, Union, Tuple
import numpy as np

class EmbeddingModel(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of the embeddings."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query."""
        pass

    @abstractmethod
    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """Embed a list of documents/chunks."""
        pass
