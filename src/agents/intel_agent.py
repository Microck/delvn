from __future__ import annotations

from integrations.otx import fetch_recent_indicators
from normalization.normalize import normalize_otx_indicator
from storage.cosmos import CosmosStore


def run_intel_collection(*, limit: int = 50) -> dict[str, int]:
    stats: dict[str, int] = {
        "fetched": 0,
        "normalized": 0,
        "stored": 0,
        "errors": 0,
    }

    try:
        payloads = fetch_recent_indicators(limit=limit)
    except Exception:
        stats["errors"] += 1
        return stats

    stats["fetched"] = len(payloads)

    try:
        store = CosmosStore()
    except Exception:
        store = None
        stats["errors"] += 1

    for payload in payloads:
        try:
            threat = normalize_otx_indicator(payload)
        except Exception:
            stats["errors"] += 1
            continue

        stats["normalized"] += 1

        if store is None:
            continue

        try:
            stored_doc = threat.model_dump(mode="json", exclude_none=True)
            store.upsert_threat(stored_doc)
            stats["stored"] += 1
        except Exception:
            stats["errors"] += 1

    return stats


__all__ = ["run_intel_collection"]
