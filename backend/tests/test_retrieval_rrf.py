import pytest
from backend.app.retrieval.rrf import reciprocal_rank_fusion

def test_reciprocal_rank_fusion():
    list1 = [
        {"chunk_id": "c1", "score": 0.9, "metadata": {"topic": "math"}},
        {"chunk_id": "c2", "score": 0.8, "metadata": {"topic": "science"}}
    ]
    
    list2 = [
        {"chunk_id": "c2", "score": 0.85, "metadata": {"topic": "science"}},
        {"chunk_id": "c3", "score": 0.75, "metadata": {"topic": "history"}}
    ]
    
    # RRF(c1) = 1/(60+1) = 1/61 ~ 0.01639
    # RRF(c2) = 1/(60+2) + 1/(60+1) = 1/62 + 1/61 ~ 0.0325
    # RRF(c3) = 1/(60+2) = 1/62 ~ 0.0161
    
    fused = reciprocal_rank_fusion([list1, list2], k=60)
    
    assert len(fused) == 3
    assert fused[0]["chunk_id"] == "c2" # highest score
    assert fused[1]["chunk_id"] == "c1"
    assert fused[2]["chunk_id"] == "c3"
    
    # Check metadata preservation
    assert fused[0]["metadata"]["topic"] == "science"
