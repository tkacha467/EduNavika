from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMGenerator(ABC):
    """
    Abstract interface for LLM Generators.
    Ensures the RAG pipeline is decoupled from any specific model provider.
    """
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Receives the final prompt and returns the generated text (JSON string).
        """
        pass

class OllamaGenerator(LLMGenerator):
    """
    Concrete implementation for local Ollama models.
    """
    
    def __init__(self, model_name: str = "gemma", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        
    def generate(self, prompt: str) -> str:
        """
        Calls the Ollama API to generate a response.
        For M4.0, we just return a mocked string or raise NotImplementedError
        since we are purely testing contracts, not executing the LLM yet.
        """
        raise NotImplementedError("LLM Execution is disabled for Milestone 4.0 Contract Testing.")
