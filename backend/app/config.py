import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5434/lenny_assistant"
    )

    # AI Defaults (can be overridden per session/request)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama3.1")
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "ollama")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "768"))

    # Provider Endpoints & Keys
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY", None)
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY", None)
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY", None)
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", None)
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY", None)

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
