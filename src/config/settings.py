from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    COSMOS_ENDPOINT: str | None = None
    COSMOS_KEY: str | None = None
    COSMOS_DATABASE: str = "delvn"
    COSMOS_CONTAINER_THREATS: str = "threats"
    COSMOS_CONTAINER_CORRELATIONS: str = "correlations"

    SEARCH_ENDPOINT: str | None = None
    SEARCH_KEY: str | None = None
    SEARCH_INDEX_THREATS: str = "threats"

    EMBEDDING_DIM: int = Field(default=1536)

    NVD_API_KEY: str | None = None
    OTX_API_KEY: str | None = None

    FOUNDRY_ENDPOINT: str | None = None
    FOUNDRY_API_KEY: str | None = None

    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str | None = None
    AZURE_OPENAI_API_VERSION: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
