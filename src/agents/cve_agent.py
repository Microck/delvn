from __future__ import annotations

from datetime import datetime, timedelta, timezone

from integrations.nvd import fetch_recent_cves
from normalization.normalize import normalize_nvd_cve
from storage.cosmos import CosmosStore


def _default_pub_start() -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=1)


def run_cve_collection(
    *,
    pub_start: datetime | None = None,
    results_per_page: int = 50,
    store: CosmosStore | None = None,
) -> dict[str, int]:
    stats: dict[str, int] = {
        "fetched": 0,
        "normalized": 0,
        "stored": 0,
        "errors": 0,
    }

    if pub_start is None:
        pub_start = _default_pub_start()

    try:
        cve_payloads = fetch_recent_cves(
            pub_start=pub_start,
            results_per_page=results_per_page,
        )
    except Exception:
        stats["errors"] += 1
        return stats

    stats["fetched"] = len(cve_payloads)
    if not cve_payloads:
        return stats

    try:
        cosmos_store = store or CosmosStore()
    except Exception:
        stats["errors"] += stats["fetched"]
        return stats

    for payload in cve_payloads:
        try:
            threat = normalize_nvd_cve(payload)
        except Exception:
            stats["errors"] += 1
            continue

        stats["normalized"] += 1

        try:
            cosmos_store.upsert_threat(threat.model_dump(mode="json"))
        except Exception:
            stats["errors"] += 1
            continue

        stats["stored"] += 1

    return stats


__all__ = ["run_cve_collection"]
