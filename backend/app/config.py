from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration, read from environment variables / .env.

    Field names map to env vars case-insensitively (e.g. `openai_api_key`
    reads `OPENAI_API_KEY`), matching the previous os.getenv-based config.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    embedding_batch_size: int = 200

    database_url: str = "postgresql://zuraio:zuraio@localhost:5432/zuraio"
    frontend_origin: str = "http://localhost:3000"

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    max_upload_bytes: int = 100 * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
