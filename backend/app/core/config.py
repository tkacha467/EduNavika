import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNavika API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Database
    ENV: str = Field(default="development")
    DATABASE_URL: str = Field(
        default="sqlite:///./edunavika.db",
        description="Database connection URL. SQLite is designated for local development and automated testing. PostgreSQL (e.g. postgresql://user:pass@host:5432/edunavika) is the production and research database hosting the longitudinal dataset."
    )
    
    # Security
    SECRET_KEY: str = Field(default="edunavika-insecure-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # On-Device SLM (Small Language Model) Inference
    EDUNAVIKA_LOCAL_MODEL_PATH: str = Field(
        default=os.getenv("EDUNAVIKA_LOCAL_MODEL_PATH", ""),
        description="Filesystem path to local GGUF model weights (e.g. D:/EduNavika/models/qwen2.5-0.5b-instruct-q4_k_m.gguf). If empty or invalid, system falls back to deterministic explanation engine."
    )
    LOCAL_LLM_N_THREADS: int = Field(
        default=4,
        description="Conservative CPU thread count for local GGUF inference on low-resource hardware"
    )
    LOCAL_LLM_N_CTX: int = Field(
        default=2048,
        description="Maximum context window for local on-device SLM inference"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
