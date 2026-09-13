from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.app.retrieval.embeddings.base import EmbeddingModel

class SentenceTransformerModel(EmbeddingModel):
    def __init__(self, model_name: str, normalize_embeddings: bool = True):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.normalize_embeddings = normalize_embeddings

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_query(self, query: str) -> np.ndarray:
        # Some models expect specific prefixes for queries, but we'll use base configuration unless specified otherwise
        embedding = self.model.encode(
            query,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True
        )
        return embedding

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        embeddings = self.model.encode(
            documents,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True
        )
        return embeddings
