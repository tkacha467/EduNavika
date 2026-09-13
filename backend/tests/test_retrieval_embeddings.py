import pytest
import numpy as np
from backend.app.retrieval.embeddings.registry import get_embedding_model

def test_sentence_transformer_model():
    model = get_embedding_model({"provider": "sentence-transformers", "model": "all-MiniLM-L6-v2"})
    
    # Test dimension
    assert model.dimension == 384
    
    # Test single query embedding
    query_emb = model.embed_query("This is a test query.")
    assert isinstance(query_emb, np.ndarray)
    assert query_emb.shape == (384,)
    
    # Test document embeddings
    docs = ["This is doc 1.", "This is doc 2."]
    doc_embs = model.embed_documents(docs)
    assert isinstance(doc_embs, np.ndarray)
    assert doc_embs.shape == (2, 384)
