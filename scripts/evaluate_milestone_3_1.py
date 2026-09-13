import json
import os
import argparse
from typing import List, Dict, Any

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

def evaluate(model_name: str, gt_path: str, output_path: str):
    print(f"Starting evaluation using model: {model_name}")
    
    # 1. Load Ground Truth
    if not os.path.exists(gt_path):
        print(f"Ground truth file not found at {gt_path}")
        return
        
    with open(gt_path, "r") as f:
        ground_truth = json.load(f)
        
    print(f"Loaded {len(ground_truth)} queries from ground truth.")
    
    # 2. Load Chunks
    db = SessionLocal()
    chunks = db.query(LearningContent).all()
    if not chunks:
        print("No chunks found in database.")
        return
        
    texts = [c.content_text for c in chunks]
    metadata = [{"chunk_id": c.chunk_identifier, "topic_id": c.topic_id} for c in chunks]
    print(f"Loaded {len(chunks)} chunks from database.")

    # 3. Initialize Retrievers
    print("Initializing BM25...")
    bm25 = BM25Retriever()
    bm25.add(texts, metadata)
    
    print(f"Initializing Dense Retriever with {model_name}...")
    embedding_model = get_embedding_model({"provider": "sentence-transformers", "model": model_name})
    vector_store = FAISSStore(dimension=embedding_model.dimension, use_cosine_similarity=True)
    dense = DenseRetriever(embedding_model, vector_store)
    dense.add(texts, metadata)
    
    print("Initializing Hybrid Retriever...")
    hybrid = HybridRetriever(bm25, dense)
    
    # 4. Evaluate
    print("Evaluating BM25...")
    eval_bm25 = RetrievalEvaluator()
    for item in ground_truth:
        res = bm25.search(item["query"], top_k=10)
        eval_bm25.evaluate_query(item["query_id"], item["query_type"], res, item["relevant_chunk_ids"])
        
    print("Evaluating Dense...")
    eval_dense = RetrievalEvaluator()
    for item in ground_truth:
        res = dense.search(item["query"], top_k=10)
        eval_dense.evaluate_query(item["query_id"], item["query_type"], res, item["relevant_chunk_ids"])
        
    print("Evaluating Hybrid...")
    eval_hybrid = RetrievalEvaluator()
    for item in ground_truth:
        res = hybrid.search(item["query"], top_k=10)
        eval_hybrid.evaluate_query(item["query_id"], item["query_type"], res, item["relevant_chunk_ids"])
        
    # 5. Generate Report
    report = {
        "model": model_name,
        "corpus_size": len(chunks),
        "queries": len(ground_truth),
        "metrics": {
            "BM25": eval_bm25.get_summary(),
            "Dense": eval_dense.get_summary(),
            "Hybrid": eval_hybrid.get_summary()
        },
        "metrics_by_type": {
            "BM25": eval_bm25.get_summary_by_type(),
            "Dense": eval_dense.get_summary_by_type(),
            "Hybrid": eval_hybrid.get_summary_by_type()
        }
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\nEvaluation Complete! Report saved to {output_path}")
    print(json.dumps(report["metrics"], indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate retrieval models for Milestone 3.1")
    parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2", help="Sentence Transformer model name")
    parser.add_argument("--gt", type=str, default="data/processed/reports/ground_truth.json", help="Ground truth JSON path")
    parser.add_argument("--out", type=str, default="data/processed/reports/evaluation_results.json", help="Output JSON path")
    
    args = parser.parse_args()
    evaluate(args.model, args.gt, args.out)
