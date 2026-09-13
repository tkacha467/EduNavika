# Retrieval module
from .embeddings import get_embedding_model, EmbeddingModel
from .vector_store import VectorStore, FAISSStore, PGVectorStore
from .lexical.bm25 import BM25Retriever
from .dense import DenseRetriever
from .hybrid import HybridRetriever
from .rrf import reciprocal_rank_fusion
from .evaluation import RetrievalEvaluator, calculate_mrr, calculate_recall_at_k
from .service import RetrievalService, RetrievalResult
