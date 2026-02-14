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

    def upsert_correlation(self, link: dict[str, Any]) -> dict[str, Any]:
        self._validate_correlation_document(link)
        container = self._get_correlations_container()
        return container.upsert_item(link)

    def get_threat(self, id: str, partition_key: str) -> dict[str, Any] | None:
        container = self._get_threats_container()
        try:
            return container.read_item(item=id, partition_key=partition_key)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def list_recent_threats(self, limit: int = 200) -> list[dict[str, Any]]:
        if limit <= 0:
            return []

        normalized_limit = int(limit)
        container = self._get_threats_container()
        threats: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for time_field in ("observed_at", "published_at"):
            query = (
                f"SELECT TOP {normalized_limit} * FROM c "
                f"WHERE IS_DEFINED(c.{time_field}) AND IS_STRING(c.{time_field}) "
                f"ORDER BY c.{time_field} DESC"
            )
            for threat in self._query_items(container, query):
                threat_id = threat.get("id")
                if isinstance(threat_id, str):
                    if threat_id in seen_ids:
                        continue
                    seen_ids.add(threat_id)
                threats.append(threat)
                if len(threats) >= normalized_limit:
                    return threats

        fallback_query = f"SELECT TOP {normalized_limit} * FROM c ORDER BY c._ts DESC"
        for threat in self._query_items(container, fallback_query):
            threat_id = threat.get("id")
            if isinstance(threat_id, str):
                if threat_id in seen_ids:
                    continue
                seen_ids.add(threat_id)
            threats.append(threat)
            if len(threats) >= normalized_limit:
                break

        return threats

    def list_correlations_for_threat(self, threat_id: str) -> list[dict[str, Any]]:
        if not threat_id:
            return []

        container = self._get_correlations_container()
        query = (
            "SELECT * FROM c WHERE c.source_id = @threat_id OR c.target_id = @threat_id"
        )
        return self._query_items(
            container,
            query,
            parameters=[{"name": "@threat_id", "value": threat_id}],
        )

    def _get_threats_container(self) -> Any:
        if self._threats_container is None:
            self.ensure_database_and_containers()
        return self._threats_container

    def _get_correlations_container(self) -> Any:
        if self._correlations_container is None:
            self.ensure_database_and_containers()
        return self._correlations_container

    @staticmethod
    def _query_items(
        container: Any,
        query: str,
        *,
        parameters: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        iterator = container.query_items(
            query=query,
            parameters=parameters or [],
            enable_cross_partition_query=True,
        )
        return [dict(item) for item in iterator]

    @staticmethod
    def _validate_threat_document(doc: dict[str, Any]) -> None:
        required_fields = ("id", "source", "type", "title", "raw")
        missing = [field for field in required_fields if not doc.get(field)]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Threat document missing required fields: {joined}")

    @staticmethod
    def _validate_correlation_document(doc: dict[str, Any]) -> None:
        required_fields = ("id", "source_id", "target_id", "confidence")
        missing: list[str] = []
        for field in required_fields:
            value = doc.get(field)
            if value is None:
                missing.append(field)
                continue
            if isinstance(value, str) and not value.strip():
                missing.append(field)

        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Correlation document missing required fields: {joined}")

        try:
            float(doc["confidence"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Correlation confidence must be numeric") from exc
