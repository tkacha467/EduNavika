from typing import List, Dict, Any

def calculate_mrr(results: List[Dict[str, Any]], relevant_chunk_ids: List[str]) -> float:
    for rank, result in enumerate(results, start=1):
        if result["chunk_id"] in relevant_chunk_ids:
            return 1.0 / rank
    return 0.0

def calculate_recall_at_k(results: List[Dict[str, Any]], relevant_chunk_ids: List[str], k: int) -> float:
    top_k_results = results[:k]
    # Simple recall: 1 if ANY relevant chunk is in top_k, 0 otherwise
    for result in top_k_results:
        if result["chunk_id"] in relevant_chunk_ids:
            return 1.0
    return 0.0

class RetrievalEvaluator:
    def __init__(self):
        self.results = []
        
    def evaluate_query(self, query_id: str, query_type: str, results: List[Dict[str, Any]], relevant_chunk_ids: List[str]):
        if not relevant_chunk_ids:
            return # Skip unlabelled

        mrr = calculate_mrr(results, relevant_chunk_ids)
        r1 = calculate_recall_at_k(results, relevant_chunk_ids, 1)
        r5 = calculate_recall_at_k(results, relevant_chunk_ids, 5)
        r10 = calculate_recall_at_k(results, relevant_chunk_ids, 10)
        
        self.results.append({
            "query_id": query_id,
            "query_type": query_type,
            "mrr": mrr,
            "recall@1": r1,
            "recall@5": r5,
            "recall@10": r10
        })

    def get_summary(self) -> Dict[str, Any]:
        if not self.results:
            return {}
            
        n = len(self.results)
        return {
            "count": n,
            "mrr": sum(r["mrr"] for r in self.results) / n,
            "recall@1": sum(r["recall@1"] for r in self.results) / n,
            "recall@5": sum(r["recall@5"] for r in self.results) / n,
            "recall@10": sum(r["recall@10"] for r in self.results) / n
        }
        
    def get_summary_by_type(self) -> Dict[str, Dict[str, Any]]:
        types = set(r["query_type"] for r in self.results)
        summary = {}
        for qt in types:
            type_results = [r for r in self.results if r["query_type"] == qt]
            n = len(type_results)
            summary[qt] = {
                "count": n,
                "mrr": sum(r["mrr"] for r in type_results) / n,
                "recall@1": sum(r["recall@1"] for r in type_results) / n,
                "recall@5": sum(r["recall@5"] for r in type_results) / n,
                "recall@10": sum(r["recall@10"] for r in type_results) / n
            }
        return summary
