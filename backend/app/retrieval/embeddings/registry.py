from typing import Dict, Any, Optional
from backend.app.retrieval.embeddings.base import EmbeddingModel
from backend.app.retrieval.embeddings.sentence_transformer import SentenceTransformerModel

class EmbeddingRegistry:
    _models: Dict[str, EmbeddingModel] = {}

    @classmethod
    def get_model(cls, provider: str, model_name: str, **kwargs) -> EmbeddingModel:
        registry_key = f"{provider}::{model_name}"
        if registry_key not in cls._models:
            if provider == "sentence-transformers":
                cls._models[registry_key] = SentenceTransformerModel(model_name, **kwargs)
            else:
                raise ValueError(f"Unknown embedding provider: {provider}")
        return cls._models[registry_key]

def get_embedding_model(config: Dict[str, Any]) -> EmbeddingModel:
    provider = config.get("provider", "sentence-transformers")
    model_name = config.get("model")
    if not model_name:
        raise ValueError("Model name must be provided in config")
    
    # Optional kwargs
    kwargs = {k: v for k, v in config.items() if k not in ["provider", "model"]}
    return EmbeddingRegistry.get_model(provider, model_name, **kwargs)
