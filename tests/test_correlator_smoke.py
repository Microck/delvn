from __future__ import annotations

from typing import Any

from agents.correlator_agent import run_correlation


class _InMemoryCosmosStore:
    def __init__(self, threats: list[dict[str, Any]]) -> None:
        self._threats = threats
        self.correlations: list[dict[str, Any]] = []

    def list_recent_threats(self, limit: int = 200) -> list[dict[str, Any]]:
        return self._threats[:limit]

    def upsert_correlation(self, link: dict[str, Any]) -> dict[str, Any]:
        self.correlations.append(link)
        return link


class _InMemoryEmbeddingClient:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), 1.0, 0.5, 0.25] for text in texts]


class _InMemorySearchStore:
    def __init__(self, hits_by_source_id: dict[str, list[dict[str, Any]]]) -> None:
        self._embedding_client = _InMemoryEmbeddingClient()
        self._hits_by_source_id = hits_by_source_id
        self.indexed: list[str] = []

    def index_threats(self, threats: list[Any]) -> list[dict[str, Any]]:
        self.indexed = [threat.id for threat in threats]
        return [
            {"key": threat.id, "status_code": 200, "succeeded": True}
            for threat in threats
        ]

    def vector_query(
        self,
        *,
        query_vector: list[float],
        top_k: int = 10,
        exclude_id: str | None = None,
        index_name: str | None = None,
    ) -> list[dict[str, Any]]:
        del query_vector, index_name
        if not exclude_id:
            return []
        return self._hits_by_source_id.get(exclude_id, [])[:top_k]


def test_correlator_pipeline_runs_without_live_azure() -> None:
    threats = [
        {
            "id": "nvd:CVE-2026-0001",
            "source": "nvd",
            "type": "cve",
            "title": "CVE-2026-0001",
            "summary": "Remote code execution used in active exploit campaigns.",
            "published_at": "2026-02-10T09:00:00Z",
            "indicators": [{"type": "cve", "value": "CVE-2026-0001"}],
            "tags": ["rce", "exploit"],
            "references": ["https://nvd.nist.gov/vuln/detail/CVE-2026-0001"],
            "raw": {"source": "nvd"},
        },
        {
            "id": "otx:ipv4:1.2.3.4",
            "source": "otx",
            "type": "indicator",
            "title": "Exploit traffic from 1.2.3.4",
            "summary": "Observed exploitation for CVE-2026-0001 from malware C2.",
            "published_at": "2026-02-10T10:00:00Z",
            "indicators": [
                {"type": "ipv4", "value": "1.2.3.4"},
                {"type": "cve", "value": "CVE-2026-0001"},
            ],
            "tags": ["malware", "c2"],
            "references": ["https://otx.alienvault.com/indicator/ipv4/1.2.3.4"],
            "raw": {"source": "otx"},
        },
    ]
    hits_by_source_id = {
        "nvd:CVE-2026-0001": [
            {
                "id": "otx:ipv4:1.2.3.4",
                "source": "otx",
                "type": "indicator",
                "score": 0.91,
                "title": "Exploit traffic from 1.2.3.4",
                "summary": "Observed exploitation for CVE-2026-0001 from malware C2.",
                "content": "CVE-2026-0001 1.2.3.4 exploit malware",
            }
        ],
        "otx:ipv4:1.2.3.4": [
            {
                "id": "nvd:CVE-2026-0001",
                "source": "nvd",
                "type": "cve",
                "score": 0.84,
                "title": "CVE-2026-0001",
                "summary": "Remote code execution used in active exploit campaigns.",
                "content": "CVE-2026-0001 exploit campaign",
            }
        ],
    }

    cosmos_store = _InMemoryCosmosStore(threats)
    search_store = _InMemorySearchStore(hits_by_source_id)

    stats = run_correlation(
        cosmos_store=cosmos_store,
        search_store=search_store,
        min_confidence=0.2,
    )

    assert stats["threats_indexed"] == 2
    assert stats["queries"] == 2
    assert stats["links_created"] >= 2
    assert stats["stored"] == stats["links_created"]
    assert stats["errors"] == 0
    assert len(cosmos_store.correlations) == stats["stored"]
    assert any(
        "Shared CVE identifiers" in reason
        for link in cosmos_store.correlations
        for reason in link.get("reasons", [])
    )
