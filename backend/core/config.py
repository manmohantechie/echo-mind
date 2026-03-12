from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"

    # Database
    database_url: str = "postgresql://echomind:echomind@localhost:5432/echomind"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "echomind_docs"

    # App
    app_secret_key: str = "change-me"
    app_env: str = "development"
    app_port: int = 8000
    allowed_origins: str = "http://localhost:3000"

    # Upload
    max_upload_size_mb: int = 20
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_results: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
