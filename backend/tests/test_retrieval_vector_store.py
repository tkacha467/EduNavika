import pytest
import numpy as np
from backend.app.retrieval.vector_store.faiss_store import FAISSStore

def test_faiss_store_add_and_search():
    dimension = 4
    store = FAISSStore(dimension=dimension, use_cosine_similarity=True)
    
    # 3 vectors of dimension 4
    vectors = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.707, 0.707, 0.0, 0.0]
    ], dtype=np.float32)
    
    metadata = [
        {"chunk_id": "c1", "topic": "math"},
        {"chunk_id": "c2", "topic": "science"},
        {"chunk_id": "c3", "topic": "math"}
    ]
    
    store.add(vectors, metadata)
    
    # Search with a query similar to c1
    query = np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)
    results = store.search(query, top_k=2)
    
    assert len(results) == 2
    assert results[0]["chunk_id"] == "c1"
    assert results[0]["score"] > 0.99
    
    # Search with metadata filter
    results_filtered = store.search(query, top_k=2, filters={"topic": "science"})
    assert len(results_filtered) == 1
    assert results_filtered[0]["chunk_id"] == "c2"
