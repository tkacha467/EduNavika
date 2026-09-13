import json
import os
import random
from backend.app.core.database import SessionLocal
from backend.app.models.content import LearningContent

def generate_ground_truth(output_path="data/processed/reports/ground_truth.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    db = SessionLocal()
    
    chunks = db.query(LearningContent).all()
    if not chunks:
        print("No chunks found in database.")
        return
        
    print(f"Found {len(chunks)} chunks in database.")
    
    # We will manually construct some queries based on the chunks text
    # But since we want to automate this script to just "have" a dataset,
    # I'll create 30 realistic-looking queries mapped to random chunks if I can't read them
    # Actually, it's better to fetch some chunks and print them so I can write them.
    # I'll just save a sample of chunks to a JSON file first.
    
    sample = random.sample(chunks, min(100, len(chunks)))
    sample_data = []
    for c in sample:
        sample_data.append({
            "chunk_id": c.chunk_identifier,
            "topic_id": c.topic_id,
            "text": c.content_text[:200]
        })
        
    with open("scripts/sample_chunks.json", "w") as f:
        json.dump(sample_data, f, indent=2)
        
    print("Saved sample chunks to scripts/sample_chunks.json")

if __name__ == "__main__":
    generate_ground_truth()
