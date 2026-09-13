from typing import List, Dict, Any

def reciprocal_rank_fusion(
    results_lists: List[List[Dict[str, Any]]], 
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Combines multiple ranked lists using Reciprocal Rank Fusion.
    RRF(d) = Σ 1 / (k + rank_i(d))
    
    Each result list should contain dictionaries with at least a 'chunk_id' and 'metadata' key.
    """
    rrf_scores: Dict[str, float] = {}
    metadata_map: Dict[str, Dict[str, Any]] = {}
    
    for results in results_lists:
        for rank, result in enumerate(results, start=1):
            chunk_id = result["chunk_id"]
            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = 0.0
                metadata_map[chunk_id] = result.get("metadata", {})
                
            rrf_scores[chunk_id] += 1.0 / (k + rank)
            
    # Sort by RRF score descending
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    fused_results = []
    for chunk_id, score in sorted_items:
        fused_results.append({
            "chunk_id": chunk_id,
            "score": score,
            "metadata": metadata_map[chunk_id],
            "retrieval_method": "hybrid"
        })
        
    return fused_results
