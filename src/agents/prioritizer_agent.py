from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from config.user_stack import load_user_stack
from models.unified_threat import UnifiedThreat
from prioritization.scoring import Relevance, score_relevance
from storage.cosmos import CosmosStore


def run_prioritization(
    *,
    stack_path: str = "src/config/user_stack.yaml",
    limit: int = 200,
    include_correlations: bool = True,
    cosmos_store: CosmosStore | None = None,
) -> dict[str, Any]:
    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    stack = load_user_stack(stack_path)
    stats: dict[str, int] = {
        "total": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "none": 0,
        "errors": 0,
    }
    result: dict[str, Any] = {
        "stack": stack.model_dump(),
        "ranked_threats": [],
        "stats": stats,
    }

    try:
        store = cosmos_store or CosmosStore()
        threat_docs = store.list_recent_threats(limit=limit)
    except Exception:
        stats["errors"] += 1
        return result

    ranked_threats: list[dict[str, Any]] = []
    for threat_doc in threat_docs:
        try:
            threat = UnifiedThreat.model_validate(threat_doc)
        except Exception:
            stats["errors"] += 1
            continue

        relevance, reasons = score_relevance(threat, stack)
        correlations: list[dict[str, Any]] = []
        if include_correlations:
            try:
                correlations = store.list_correlations_for_threat(threat.id)
            except Exception:
                stats["errors"] += 1

        ranked_threats.append(
            {
                "threat": threat.model_dump(mode="json", exclude_none=True),
                "relevance": relevance.value,
                "reasons": reasons,
                "severity": threat.severity if threat.severity is not None else 0.0,
                "correlation_count": len(correlations),
                "correlations": correlations,
            }
        )
        stats["total"] += 1
        stats[relevance.value.lower()] += 1

    ranked_threats.sort(key=_rank_key)
    result["ranked_threats"] = ranked_threats
    result["generated_at"] = _iso_now()
    return result


def _rank_key(entry: dict[str, Any]) -> tuple[int, float, str]:
    relevance_order = {
        Relevance.HIGH.value: 0,
        Relevance.MEDIUM.value: 1,
        Relevance.LOW.value: 2,
        Relevance.NONE.value: 3,
    }

    threat = entry.get("threat", {})
    threat_id = str(threat.get("id", ""))
    severity = float(entry.get("severity", 0.0))
    relevance = str(entry.get("relevance", Relevance.NONE.value))

    return relevance_order.get(relevance, 99), -severity, threat_id


def _iso_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


__all__ = ["run_prioritization"]
