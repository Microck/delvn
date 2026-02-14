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

from config.settings import Settings, get_settings


class SearchStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        if not self._settings.SEARCH_ENDPOINT or not self._settings.SEARCH_KEY:
            raise ValueError("SEARCH_ENDPOINT and SEARCH_KEY must be configured")

        credential = AzureKeyCredential(self._settings.SEARCH_KEY)
        self._index_client = SearchIndexClient(
            endpoint=self._settings.SEARCH_ENDPOINT,
            credential=credential,
        )
        self._credential = credential
        self._search_clients: dict[str, SearchClient] = {}

    def ensure_index(self, index_name: str, *, embedding_dim: int) -> None:
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
                    vector_search_dimensions=embedding_dim,
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
        return [result.as_dict() for result in results]

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

    def _get_search_client(self, index_name: str) -> SearchClient:
        if index_name not in self._search_clients:
            self._search_clients[index_name] = self._build_search_client(index_name)
        return self._search_clients[index_name]

    def _build_search_client(self, index_name: str) -> SearchClient:
        return SearchClient(
            endpoint=self._settings.SEARCH_ENDPOINT,
            index_name=index_name,
            credential=self._credential,
        )
