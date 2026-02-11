from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    # Cosmos DB
    cosmos_endpoint: str | None = None
    cosmos_key: str | None = None
    cosmos_database: str = "threat-fusion"
    cosmos_container_threats: str = "threats"
    cosmos_container_correlations: str = "correlations"

    # Azure AI Search
    search_endpoint: str | None = None
    search_key: str | None = None
    search_index_threats: str = "threats"

    # Embeddings
    embedding_dim: int = 1536

    # Source API keys (optional)
    nvd_api_key: str | None = None
    otx_api_key: str | None = None

    # Foundry / Azure OpenAI (optional; Phase 1 uses mock-friendly scaffolding)
    foundry_endpoint: str | None = None
    foundry_api_key: str | None = None

    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_embedding_deployment: str | None = None
    azure_openai_api_version: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
