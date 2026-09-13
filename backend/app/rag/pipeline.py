from typing import Tuple, Optional
from backend.app.rag.schemas import MCQGenerationRequest, MCQBatchResponse
from backend.app.rag.retriever import RAGRetriever
from backend.app.rag.context_builder import ContextBuilder
from backend.app.rag.prompt_builder import PromptBuilder
from backend.app.rag.generator import LLMGenerator
from backend.app.rag.validator import StructuralValidator, SemanticValidator

class MCQGenerationPipeline:
    def __init__(
        self, 
        retriever: RAGRetriever,
        generator: LLMGenerator,
        context_builder: ContextBuilder,
        prompt_builder: PromptBuilder,
        structural_validator: StructuralValidator,
        semantic_validator: SemanticValidator
    ):
        self.retriever = retriever
        self.generator = generator
        self.context_builder = context_builder
        self.prompt_builder = prompt_builder
        self.structural_validator = structural_validator
        self.semantic_validator = semantic_validator

    def generate(self, request: MCQGenerationRequest) -> Tuple[bool, str, Optional[MCQBatchResponse]]:
        # 1. Retrieval
        raw_chunks = self.retriever.fetch_context(request)
        if not raw_chunks:
            return False, "Retrieval returned no context for the requested curriculum filters.", None
            
        # 2. Context Construction
        context_string, allowed_chunk_ids = self.context_builder.build_context(raw_chunks)
        if not allowed_chunk_ids:
            return False, "Failed to build context within token budget.", None
            
        # 3. Prompt Formulation
        prompt = self.prompt_builder.build_prompt(request, context_string)
        
        # 4. Generation
        try:
            llm_output = self.generator.generate(prompt)
        except Exception as e:
            return False, f"LLM Generation failed: {str(e)}", None
            
        # 5. Structural Validation
        is_valid_struct, struct_msg, batch = self.structural_validator.validate(
            llm_output, allowed_chunk_ids, request.count
        )
        if not is_valid_struct:
            return False, struct_msg, None
            
        # 6. Grounding Validation
        is_valid_sem, sem_msg = self.semantic_validator.validate(batch, context_string)
        if not is_valid_sem:
            return False, sem_msg, None
            
        return True, "Success", batch
