from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

import httpx

from config.settings import Settings, get_settings

DEFAULT_AZURE_OPENAI_API_VERSION = "2024-02-01"


class EmbeddingClient(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass(slots=True)
class DeterministicHashEmbeddingClient:
    dim: int

    def __post_init__(self) -> None:
        if self.dim <= 0:
            raise ValueError("Embedding dimension must be greater than zero")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        values: list[float] = []
        block = 0
        while len(values) < self.dim:
            digest = hashlib.sha256(f"{text}|{block}".encode("utf-8")).digest()
            for idx in range(0, len(digest), 4):
                raw = int.from_bytes(digest[idx : idx + 4], "big")
                values.append((raw / 0xFFFFFFFF) * 2.0 - 1.0)
                if len(values) == self.dim:
                    break
            block += 1
        return values


class AzureOpenAIEmbeddingClient:
    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str = DEFAULT_AZURE_OPENAI_API_VERSION,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._deployment = deployment
        self._api_version = api_version
        self._timeout_seconds = timeout_seconds

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = httpx.post(
            url=(
                f"{self._endpoint}/openai/deployments/{self._deployment}/embeddings"
                f"?api-version={self._api_version}"
            ),
            headers={"api-key": self._api_key, "Content-Type": "application/json"},
            json={"input": texts},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        payload = response.json()
        items = payload.get("data", [])
        ordered = sorted(items, key=lambda item: item.get("index", 0))
        return [item["embedding"] for item in ordered]


def get_embedding_client(settings: Settings | None = None) -> EmbeddingClient:
    current_settings = settings or get_settings()

    has_azure_config = all(
        (
            current_settings.AZURE_OPENAI_ENDPOINT,
            current_settings.AZURE_OPENAI_API_KEY,
            current_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        )
    )
    if has_azure_config:
        return AzureOpenAIEmbeddingClient(
            endpoint=current_settings.AZURE_OPENAI_ENDPOINT or "",
            api_key=current_settings.AZURE_OPENAI_API_KEY or "",
            deployment=current_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT or "",
            api_version=(
                current_settings.AZURE_OPENAI_API_VERSION
                or DEFAULT_AZURE_OPENAI_API_VERSION
            ),
        )

    return DeterministicHashEmbeddingClient(dim=current_settings.EMBEDDING_DIM)
