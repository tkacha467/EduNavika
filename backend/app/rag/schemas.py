from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class MCQDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MCQGenerationRequest(BaseModel):
    grade: int = Field(..., ge=1, le=12, description="GSEB grade level (1-12)")
    subject: str = Field(..., min_length=1, description="Subject name")
    chapter: Optional[str] = Field(None, description="Specific chapter name")
    topic: Optional[str] = Field(None, description="Specific topic name")
    difficulty: MCQDifficulty = Field(..., description="Target difficulty")
    count: int = Field(..., ge=1, le=20, description="Number of MCQs to generate (1-20)")

class GeneratedMCQ(BaseModel):
    question: str = Field(..., min_length=5, description="The question text")
    options: List[str] = Field(..., description="Exactly 4 options")
    correct_option: int = Field(..., ge=0, le=3, description="0-indexed correct option")
    explanation: str = Field(..., min_length=5, description="Explanation for the correct answer")
    difficulty: MCQDifficulty
    subject: str
    chapter: str
    topic: str
    source_chunks: List[str] = Field(..., min_length=1, description="List of chunk IDs supporting this MCQ")

    @field_validator("options")
    def validate_options_length(cls, v):
        if len(v) != 4:
            raise ValueError("Exactly 4 options must be provided")
        return v
        
    @field_validator("options")
    def validate_options_not_empty(cls, v):
        for opt in v:
            if not opt.strip():
                raise ValueError("Options cannot be empty strings")
        return v

class MCQBatchResponse(BaseModel):
    mcqs: List[GeneratedMCQ] = Field(..., description="List of generated MCQs")
    
    # We don't strictly validate len(mcqs) == request.count at the Pydantic level 
    # since this schema doesn't know the request, but the StructuralValidator will enforce it.
