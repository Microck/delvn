from __future__ import annotations

from typing import Any

from azure.cosmos import CosmosClient, PartitionKey, exceptions

from config.settings import Settings, get_settings


class CosmosStore:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        if not self._settings.COSMOS_ENDPOINT or not self._settings.COSMOS_KEY:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be configured")

        self._client = CosmosClient(
            url=self._settings.COSMOS_ENDPOINT,
            credential=self._settings.COSMOS_KEY,
        )
        self._database_client: Any | None = None
        self._threats_container: Any | None = None
        self._correlations_container: Any | None = None

    def ensure_database_and_containers(self) -> None:
        self._database_client = self._client.create_database_if_not_exists(
            id=self._settings.COSMOS_DATABASE
        )
        self._threats_container = self._database_client.create_container_if_not_exists(
            id=self._settings.COSMOS_CONTAINER_THREATS,
            partition_key=PartitionKey(path="/source"),
        )
        self._correlations_container = (
            self._database_client.create_container_if_not_exists(
                id=self._settings.COSMOS_CONTAINER_CORRELATIONS,
                partition_key=PartitionKey(path="/id"),
            )
        )

    def upsert_threat(self, doc: dict[str, Any]) -> dict[str, Any]:
        self._validate_threat_document(doc)
        container = self._get_threats_container()
        return container.upsert_item(doc)

    def get_threat(self, id: str, partition_key: str) -> dict[str, Any] | None:
        container = self._get_threats_container()
        try:
            return container.read_item(item=id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def _get_threats_container(self) -> Any:
        if self._threats_container is None:
            self.ensure_database_and_containers()
        return self._threats_container

    @staticmethod
    def _validate_threat_document(doc: dict[str, Any]) -> None:
        required_fields = ("id", "source", "type", "title", "raw")
        missing = [field for field in required_fields if not doc.get(field)]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Threat document missing required fields: {joined}")
