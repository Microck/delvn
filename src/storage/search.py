from __future__ import annotations

from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from config.settings import Settings, get_settings
from embeddings.client import get_embedding_client
from models.unified_threat import UnifiedThreat


class SearchStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        endpoint = self._settings.SEARCH_ENDPOINT
        search_key = self._settings.SEARCH_KEY
        if not endpoint or not search_key:
            raise ValueError("SEARCH_ENDPOINT and SEARCH_KEY must be configured")

        self._endpoint = endpoint
        credential = AzureKeyCredential(search_key)
        self._index_client = SearchIndexClient(
            endpoint=self._endpoint,
            credential=credential,
        )
        self._credential = credential
        self._embedding_client = get_embedding_client(self._settings)
        self._search_clients: dict[str, SearchClient] = {}

    def ensure_index(
        self, index_name: str, *, embedding_dim: int | None = None
    ) -> None:
        vector_dim = embedding_dim or self._settings.EMBEDDING_DIM
        index = SearchIndex(
            name=index_name,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SimpleField(
                    name="source", type=SearchFieldDataType.String, filterable=True
                ),
                SimpleField(
                    name="type", type=SearchFieldDataType.String, filterable=True
                ),
                SimpleField(
                    name="published_at",
                    type=SearchFieldDataType.String,
                    filterable=True,
                ),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SearchField(
                    name="contentVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=vector_dim,
                    vector_search_profile_name="tf-vector-profile",
                ),
            ],
            vector_search=VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="tf-hnsw")],
                profiles=[
                    VectorSearchProfile(
                        name="tf-vector-profile",
                        algorithm_configuration_name="tf-hnsw",
                    )
                ],
            ),
        )
        self._index_client.create_or_update_index(index)
        self._search_clients[index_name] = self._build_search_client(index_name)

    def upsert_documents(
        self, docs: list[dict[str, Any]], index_name: str | None = None
    ) -> list[dict[str, Any]]:
        if not docs:
            return []

        target_index = index_name or self._settings.SEARCH_INDEX_THREATS
        client = self._get_search_client(target_index)
        results = client.merge_or_upload_documents(documents=docs)
        return [
            {
                "key": result.key,
                "status_code": result.status_code,
                "succeeded": result.succeeded,
                "error_message": result.error_message,
            }
            for result in results
        ]

    def search_text(
        self,
        query: str,
        *,
        top: int = 5,
        index_name: str | None = None,
    ) -> list[dict[str, Any]]:
        target_index = index_name or self._settings.SEARCH_INDEX_THREATS
        client = self._get_search_client(target_index)
        results = client.search(search_text=query, top=top)
        return [dict(item) for item in results]

    def index_threats(
        self,
        threats: list[UnifiedThreat],
        *,
        index_name: str | None = None,
    ) -> list[dict[str, Any]]:
        if not threats:
            return []

        target_index = index_name or self._settings.SEARCH_INDEX_THREATS
        if target_index not in self._search_clients:
            self.ensure_index(target_index)

        content_blocks = [threat.content_text() for threat in threats]
        vectors = self._embedding_client.embed(content_blocks)
        if len(vectors) != len(threats):
            raise ValueError("Embedding count mismatch: expected one vector per threat")

        docs: list[dict[str, Any]] = []
        for threat, content, vector in zip(
            threats, content_blocks, vectors, strict=True
        ):
            if len(vector) != self._settings.EMBEDDING_DIM:
                raise ValueError(
                    f"Embedding dimension mismatch for {threat.id}: "
                    f"expected {self._settings.EMBEDDING_DIM}, got {len(vector)}"
                )
            docs.append(
                {
                    "id": threat.id,
                    "source": threat.source,
                    "type": threat.type,
                    "published_at": (
                        threat.published_at.isoformat() if threat.published_at else None
                    ),
                    "content": content,
                    "contentVector": vector,
                }
            )

        return self.upsert_documents(docs, index_name=target_index)

    def vector_query(
        self,
        *,
        query_vector: list[float],
        top_k: int = 10,
        exclude_id: str | None = None,
        index_name: str | None = None,
    ) -> list[dict[str, Any]]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")
        if len(query_vector) != self._settings.EMBEDDING_DIM:
            raise ValueError(
                "query_vector length must match EMBEDDING_DIM "
                f"({self._settings.EMBEDDING_DIM})"
            )

        target_index = index_name or self._settings.SEARCH_INDEX_THREATS
        client = self._get_search_client(target_index)
        query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top_k,
            fields="contentVector",
        )
        filter_expression: str | None = None
        if exclude_id:
            escaped_id = exclude_id.replace("'", "''")
            filter_expression = f"id ne '{escaped_id}'"

        results = client.search(
            search_text=None,
            top=top_k,
            select=["id", "source", "type"],
            filter=filter_expression,
            vector_queries=[query],
        )
        hits: list[dict[str, Any]] = []
        for item in results:
            score = float(item.get("@search.score", 0.0))
            hits.append(
                {
                    "id": item.get("id"),
                    "source": item.get("source"),
                    "type": item.get("type"),
                    "score": score,
                }
            )
        return hits

    def _get_search_client(self, index_name: str) -> SearchClient:
        if index_name not in self._search_clients:
            self._search_clients[index_name] = self._build_search_client(index_name)
        return self._search_clients[index_name]

    def _build_search_client(self, index_name: str) -> SearchClient:
        return SearchClient(
            endpoint=self._endpoint,
            index_name=index_name,
            credential=self._credential,
        )
