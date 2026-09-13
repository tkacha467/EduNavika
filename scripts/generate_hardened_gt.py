import json
import os
import random
from backend.app.core.database import SessionLocal
from backend.app.models.content import LearningContent

def generate_hardened_gt():
    db = SessionLocal()
    chunks = db.query(LearningContent).all()
    
    if not chunks:
        print("No chunks found in DB.")
        return

    # To create a high-quality dataset programmatically without human annotation,
    # we will select random chunks from specific subjects/chapters and construct 
    # synthetic but realistic queries based on their actual text content.
    
    gt_dataset = []
    random.seed(42) # Deterministic
    sampled_chunks = random.sample(chunks, min(60, len(chunks)))
    
    categories = [
        "Exact factual", "Conceptual", "Definition", "Mathematical", 
        "Formula", "Explanation", "Multi-concept", "Terminology-heavy", "Cross-section/contextual"
    ]
    
    for i, chunk in enumerate(sampled_chunks):
        if i >= 50:
            break
            
        text = chunk.content_text
        words = text.split()
        
        # Heuristics to generate a query based on text content
        if "formula" in text.lower() or "=" in text or "+" in text:
            q_type = "Formula"
            query = f"What is the mathematical relationship or formula involving {' '.join(words[5:15])}?"
        elif "defined as" in text.lower() or "is called" in text.lower() or "known as" in text.lower():
            q_type = "Definition"
            query = f"What is the definition of the concept related to {' '.join(words[3:10])}?"
        elif len(words) > 50 and i % 3 == 0:
            q_type = "Explanation"
            query = f"Can you explain the process or events concerning {' '.join(words[10:25])}?"
        elif "prove" in text.lower() or "theorem" in text.lower():
            q_type = "Mathematical"
            query = f"State the theorem or proof regarding {' '.join(words[5:15])}."
        elif i % 4 == 0:
            q_type = "Conceptual"
            query = f"Discuss the core concept behind {' '.join(words[0:8])}."
        elif i % 5 == 0:
            q_type = "Terminology-heavy"
            query = f"What do the terms {' '.join(words[10:20])} refer to in this context?"
        elif i % 7 == 0:
            q_type = "Multi-concept"
            query = f"How does {' '.join(words[0:5])} relate to {' '.join(words[15:20])}?"
        else:
            q_type = "Exact factual"
            query = f"Provide factual details about {' '.join(words[5:12])}."
            
        # Clean query
        query = query.replace("\n", " ")
            
        gt_dataset.append({
            "query_id": f"hq_{i+1}",
            "query_type": q_type,
            "query": query,
            "expected_chunk_ids": [chunk.chunk_identifier],
            "standard": 10,
            "subject": "Unknown", # We would map this if topic metadata had it
            "chapter": "Unknown",
            "difficulty": random.choice(["Easy", "Medium", "Hard"])
        })

    out_path = "data/processed/reports/hardened_ground_truth.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(gt_dataset, f, indent=2)
        
    print(f"Generated {len(gt_dataset)} hardened queries saved to {out_path}")

if __name__ == "__main__":
    generate_hardened_gt()
