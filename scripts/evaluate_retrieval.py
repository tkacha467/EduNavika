import json
import os
import time
from typing import List, Dict, Any

from sqlalchemy.orm import joinedload
from backend.app.core.database import SessionLocal
from backend.app.models.content import LearningContent
from backend.app.retrieval import (
    get_embedding_model,
    FAISSStore,
    BM25Retriever,
    DenseRetriever,
    HybridRetriever,
    RetrievalEvaluator
)

def evaluate_retriever(name: str, retriever: Any, ground_truth: List[Dict], top_k: int = 10) -> Dict:
    evaluator = RetrievalEvaluator()
    start_time = time.time()
    failures = []
    
    for item in ground_truth:
        query = item["query"]
        expected = item["expected_chunk_ids"]
        if not expected:
            continue
            
        results = retriever.search(query, top_k=top_k)
        evaluator.evaluate_query(item["query_id"], item["query_type"], results, expected)
        
        # Failure analysis
        retrieved_ids = [r["chunk_id"] for r in results]
        found = False
        for exp in expected:
            if exp in retrieved_ids:
                found = True
                break
                
        if not found:
            top_3 = results[:3] if results else []
            failures.append({
                "query": query,
                "query_type": item["query_type"],
                "expected": expected,
                "retrieved_1": top_3[0]["chunk_id"] if len(top_3) > 0 else None,
                "retrieved_2": top_3[1]["chunk_id"] if len(top_3) > 1 else None,
                "retrieved_3": top_3[2]["chunk_id"] if len(top_3) > 2 else None,
                "failure_reason": determine_failure_reason(item["query_type"], name)
            })
            
    latency = time.time() - start_time
    summary = evaluator.get_summary()
    summary["latency_s"] = latency
    return {"summary": summary, "failures": failures}

def determine_failure_reason(query_type: str, retriever_name: str) -> str:
    if retriever_name == "BM25" and query_type in ["Conceptual", "Explanation", "Multi-concept"]:
        return "SEMANTIC_FAILURE"
    if retriever_name == "Dense" and query_type in ["Exact factual", "Formula", "Terminology-heavy"]:
        return "LEXICAL_FAILURE"
    return "AMBIGUITY"

def run_hardened_evaluation():
    print("Starting Hardened Retrieval Evaluation (Milestone 3.2)")
    
    gt_path = "data/processed/reports/hardened_ground_truth.json"
    if not os.path.exists(gt_path):
        print(f"Ground truth file not found at {gt_path}. Generate it first.")
        return
        
    with open(gt_path, "r") as f:
        ground_truth = json.load(f)
        
    print(f"Loaded {len(ground_truth)} queries.")
    
    db = SessionLocal()
    # Eagerly load curriculum hierarchy to populate provenance
    chunks = db.query(LearningContent).options(
        joinedload(LearningContent.topic)
        .joinedload(Topic.chapter)
        .joinedload(Chapter.subject)
        .joinedload(Subject.standard)
    ).all()
    
    if not chunks:
        print("No chunks found in DB.")
        return
        
    texts = []
    metadata = []
    for c in chunks:
        texts.append(c.content_text)
        meta = {
            "chunk_id": c.chunk_identifier,
            "content": c.content_text,
            "topic_id": c.topic_id,
            "source_document": c.source_document,
            "source_page": c.source_page,
            "source_reference": c.source_reference
        }
        if c.topic:
            meta["topic"] = c.topic.title
            if c.topic.chapter:
                meta["chapter"] = c.topic.chapter.title
                if c.topic.chapter.subject:
                    meta["subject"] = c.topic.chapter.subject.name
                    if c.topic.chapter.subject.standard:
                        meta["standard"] = c.topic.chapter.subject.standard.grade_number
        metadata.append(meta)
        
    print(f"Loaded {len(chunks)} chunks with full provenance.")

    # 1. Initialize BM25
    print("Initializing BM25...")
    bm25 = BM25Retriever()
    bm25.add(texts, metadata)
    
    # 2. Initialize BGE-small Dense
    model_name = "BAAI/bge-small-en-v1.5"
    print(f"Initializing Dense Retriever with {model_name}...")
    embedding_model = get_embedding_model({"provider": "sentence-transformers", "model": model_name})
    vector_store = FAISSStore(dimension=embedding_model.dimension, use_cosine_similarity=True)
    dense = DenseRetriever(embedding_model, vector_store)
    dense.add(texts, metadata)
    
    # 3. Initialize Hybrid
    print("Initializing Hybrid Retriever...")
    hybrid = HybridRetriever(bm25, dense)
    
    print("\n--- Running Evaluations ---")
    bm25_res = evaluate_retriever("BM25", bm25, ground_truth)
    print("BM25 Evaluation complete.")
    dense_res = evaluate_retriever("Dense", dense, ground_truth)
    print("Dense Evaluation complete.")
    hybrid_res = evaluate_retriever("Hybrid", hybrid, ground_truth)
    print("Hybrid Evaluation complete.")
    
    # Generate Output
    report = {
        "BM25": bm25_res,
        "Dense": dense_res,
        "Hybrid": hybrid_res
    }
    
    out_path = "data/processed/reports/retrieval_benchmark_3_2.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\nReport saved to {out_path}")
    
    # Print formatted markdown table
    print("\n| Retriever | MRR | R@1 | R@5 | R@10 | Latency (s) |")
    print("|---|---|---|---|---|---|")
    
    def fmt(m):
        return f"{m.get('mrr', 0):.3f} | {m.get('recall@1', 0)*100:.1f}% | {m.get('recall@5', 0)*100:.1f}% | {m.get('recall@10', 0)*100:.1f}% | {m.get('latency_s', 0):.2f}"
        
    print(f"| BM25 | {fmt(bm25_res['summary'])} |")
    print(f"| BGE-small + FAISS | {fmt(dense_res['summary'])} |")
    print(f"| BM25 + BGE + RRF | {fmt(hybrid_res['summary'])} |")

if __name__ == "__main__":
    from backend.app.models.curriculum import Topic, Chapter, Subject, Standard
    run_hardened_evaluation()
