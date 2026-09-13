import pytest
import json
from backend.app.rag.schemas import MCQGenerationRequest, MCQDifficulty, MCQBatchResponse, GeneratedMCQ
from backend.app.rag.context_builder import ContextBuilder
from backend.app.rag.validator import StructuralValidator
from backend.app.retrieval.service import RetrievalResult

def test_mcq_generation_request_validation():
    # Valid
    req = MCQGenerationRequest(
        grade=10, 
        subject="Science", 
        difficulty=MCQDifficulty.MEDIUM,
        count=5
    )
    assert req.grade == 10
    
    # Invalid count
    with pytest.raises(ValueError):
        MCQGenerationRequest(grade=10, subject="Math", difficulty="easy", count=25)

def test_context_builder_budgeting():
    builder = ContextBuilder(max_tokens=50) # Very small budget (approx 200 chars)
    
    r1 = RetrievalResult(
        chunk_id="chk_1", score=1.0, rank=1, content="This is a short chunk.", retrieval_method="dense"
    )
    r2 = RetrievalResult(
        chunk_id="chk_2", score=0.9, rank=2, content="This is a very very very very long chunk that should definitely exceed the small token budget we just set for this test case because we want to see if it truncates properly.", retrieval_method="dense"
    )
    
    context, allowed = builder.build_context([r1, r2])
    
    # Should only include chk_1 because chk_2 pushes it over budget
    assert "chk_1" in allowed
    assert "chk_2" not in allowed
    assert "[CHUNK_ID: chk_1]" in context
    assert "[CHUNK_ID: chk_2]" not in context

def test_structural_validator():
    validator = StructuralValidator()
    
    valid_json = json.dumps({
        "mcqs": [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Rome"],
                "correct_option": 2,
                "explanation": "Paris is the capital.",
                "difficulty": "easy",
                "subject": "Geography",
                "chapter": "Europe",
                "topic": "France",
                "source_chunks": ["chk_123"]
            }
        ]
    })
    
    # 1. Valid test
    is_valid, msg, batch = validator.validate(valid_json, ["chk_123", "chk_456"], 1)
    assert is_valid is True
    assert batch.mcqs[0].correct_option == 2
    
    # 2. Invalid count
    is_valid, msg, batch = validator.validate(valid_json, ["chk_123"], 2)
    assert is_valid is False
    assert "Expected 2 MCQs" in msg
    
    # 3. Unauthorized chunk ID
    is_valid, msg, batch = validator.validate(valid_json, ["chk_999"], 1)
    assert is_valid is False
    assert "unauthorized chunk_id" in msg
    
    # 4. Invalid options length
    invalid_options = json.dumps({
        "mcqs": [
            {
                "question": "Q?",
                "options": ["A", "B"], # only 2
                "correct_option": 0,
                "explanation": "Exp",
                "difficulty": "easy",
                "subject": "S",
                "chapter": "C",
                "topic": "T",
                "source_chunks": ["chk_123"]
            }
        ]
    })
    is_valid, msg, batch = validator.validate(invalid_options, ["chk_123"], 1)
    assert is_valid is False
    assert "JSON/Schema validation failed" in msg
