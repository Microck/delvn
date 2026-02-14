from __future__ import annotations

from typing import Any

from correlation.matcher import match_correlation_candidates
from embeddings.client import EmbeddingClient, get_embedding_client
from models.unified_threat import UnifiedThreat
from storage.cosmos import CosmosStore
from storage.search import SearchStore


def run_correlation(
    *,
    limit: int = 200,
    top_k: int = 8,
    min_confidence: float = 0.35,
    cosmos_store: CosmosStore | None = None,
    search_store: SearchStore | None = None,
) -> dict[str, int]:
    if limit <= 0:
        raise ValueError("limit must be greater than zero")
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    stats: dict[str, int] = {
        "threats_indexed": 0,
        "queries": 0,
        "links_created": 0,
        "stored": 0,
        "errors": 0,
    }

    try:
        store = cosmos_store or CosmosStore()
    except Exception:
        stats["errors"] += 1
        return stats

    try:
        threat_docs = store.list_recent_threats(limit=limit)
    except Exception:
        stats["errors"] += 1
        return stats

    threats = _to_unified_threats(threat_docs, stats=stats)
    if not threats:
        return stats

    try:
        vector_store = search_store or SearchStore()
    except Exception:
        stats["errors"] += 1
        return stats

    try:
        index_results = vector_store.index_threats(threats)
    except Exception:
        stats["errors"] += len(threats)
        return stats

    stats["threats_indexed"] = sum(
        1 for result in index_results if result.get("succeeded")
    )
    embedding_client = _resolve_embedding_client(vector_store)

    for threat in threats:
        try:
            vectors = embedding_client.embed([threat.content_text()])
            if not vectors:
                raise ValueError("Missing query vector")

            hits = vector_store.vector_query(
                query_vector=vectors[0],
                top_k=top_k,
                exclude_id=threat.id,
            )
        except Exception:
            stats["errors"] += 1
            continue

        stats["queries"] += 1
        links = match_correlation_candidates(
            threat,
            hits,
            min_confidence=min_confidence,
        )
        stats["links_created"] += len(links)

        for link in links:
            try:
                store.upsert_correlation(
                    link.model_dump(mode="json", exclude_none=True)
                )
            except Exception:
                stats["errors"] += 1
                continue
            stats["stored"] += 1

    return stats


def _to_unified_threats(
    docs: list[dict[str, Any]],
    *,
    stats: dict[str, int],
) -> list[UnifiedThreat]:
    threats: list[UnifiedThreat] = []
    for doc in docs:
        try:
            threat = UnifiedThreat.model_validate(doc)
        except Exception:
            stats["errors"] += 1
            continue
        threats.append(threat)
    return threats


def _resolve_embedding_client(search_store: SearchStore) -> EmbeddingClient:
    embedded_client = getattr(search_store, "_embedding_client", None)
    if embedded_client is not None:
        return embedded_client

    store_settings = getattr(search_store, "_settings", None)
    if store_settings is not None and hasattr(store_settings, "EMBEDDING_DIM"):
        return get_embedding_client(store_settings)
    return get_embedding_client()


__all__ = ["run_correlation"]
