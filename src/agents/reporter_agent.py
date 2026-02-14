from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.prioritizer_agent import run_prioritization
from models.brief import BriefEntry, ExecutiveBrief
from reporting.render import render_brief_md
from storage.cosmos import CosmosStore

_HIGH_MEDIUM = {"HIGH", "MEDIUM"}


def run_reporting(
    *,
    stack_path: str = "src/config/user_stack.yaml",
    limit: int = 200,
    include_correlations: bool = True,
    top_risk_count: int = 5,
    notable_count: int = 3,
    output_path: str | None = None,
    prioritization_output: dict[str, Any] | None = None,
    cosmos_store: CosmosStore | None = None,
) -> dict[str, Any]:
    data = prioritization_output
    if data is None:
        data = run_prioritization(
            stack_path=stack_path,
            limit=limit,
            include_correlations=include_correlations,
            cosmos_store=cosmos_store,
        )

    ranked = _ranked_entries(data)
    max_top = max(3, min(5, top_risk_count))
    top_candidates = [entry for entry in ranked if _relevance(entry) in _HIGH_MEDIUM]
    top_risk_entries = top_candidates[:max_top]

    used_ids = {_threat_id(entry) for entry in top_risk_entries if _threat_id(entry)}
    mention_cap = max(0, notable_count)
    notable_entries = [entry for entry in ranked if _threat_id(entry) not in used_ids][
        :mention_cap
    ]

    brief_payload: dict[str, Any] = {
        "stack_summary": _stack_summary(data.get("stack", {})),
        "top_risks": [_to_brief_entry(entry) for entry in top_risk_entries],
        "notable_mentions": [_to_brief_entry(entry) for entry in notable_entries],
    }

    generated_at = data.get("generated_at")
    if generated_at:
        brief_payload["generated_at"] = generated_at

    brief = ExecutiveBrief.model_validate(brief_payload)
    markdown = render_brief_md(brief)

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")

    return {
        "brief": brief.model_dump(mode="json"),
        "markdown": markdown,
        "stats": data.get("stats", {}),
        "output_path": output_path,
    }


def _ranked_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = payload.get("ranked_threats", [])
    if not isinstance(ranked, list):
        return []
    return [entry for entry in ranked if isinstance(entry, dict)]


def _to_brief_entry(entry: dict[str, Any]) -> BriefEntry:
    threat = entry.get("threat", {})
    if not isinstance(threat, dict):
        threat = {}

    relevance = _relevance(entry)
    reasons = _string_list(entry.get("reasons"))
    severity = _severity(entry)
    correlation_count = _correlation_count(entry)

    evidence = reasons[:3]
    if severity > 0:
        evidence.append(f"Reported severity: {severity:.1f}/10")
    if correlation_count > 0:
        evidence.append(f"Related correlations found: {correlation_count}")

    references = _string_list(threat.get("references"))[:2]
    evidence.extend(f"Reference: {reference}" for reference in references)

    why_it_matters = _why_it_matters(
        relevance=relevance,
        reasons=reasons,
        severity=severity,
        correlation_count=correlation_count,
    )

    return BriefEntry.model_validate(
        {
            "headline": _headline(threat),
            "relevance": relevance,
            "why_it_matters": why_it_matters,
            "evidence": evidence,
            "recommended_actions": _recommended_actions(relevance),
        }
    )


def _stack_summary(raw_stack: Any) -> str:
    if not isinstance(raw_stack, dict):
        return "No stack profile configured."

    products = _string_list(raw_stack.get("products"))
    platforms = _string_list(raw_stack.get("platforms"))
    keywords = _string_list(raw_stack.get("keywords"))
    exclude = _string_list(raw_stack.get("exclude"))

    parts: list[str] = []
    if products:
        parts.append(f"Products: {', '.join(products)}")
    if platforms:
        parts.append(f"Platforms: {', '.join(platforms)}")
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords)}")
    if exclude:
        parts.append(f"Excluded: {', '.join(exclude)}")

    if not parts:
        return "No stack profile configured."
    return "; ".join(parts)


def _headline(threat: dict[str, Any]) -> str:
    title = str(threat.get("title", "")).strip()
    if title:
        return title

    fallback_id = str(threat.get("id", "")).strip()
    if fallback_id:
        return fallback_id

    return "Untitled threat"


def _relevance(entry: dict[str, Any]) -> str:
    raw_relevance = str(entry.get("relevance", "NONE")).strip().upper()
    if raw_relevance:
        return raw_relevance
    return "NONE"


def _why_it_matters(
    *,
    relevance: str,
    reasons: list[str],
    severity: float,
    correlation_count: int,
) -> str:
    parts: list[str] = []
    if reasons:
        parts.append(reasons[0].rstrip("."))
    else:
        parts.append(f"Ranked {relevance} for the configured stack")

    if severity > 0:
        parts.append(f"severity is {severity:.1f}/10")
    if correlation_count > 0:
        parts.append(f"linked to {correlation_count} related threats")

    return ". ".join(parts) + "."


def _recommended_actions(relevance: str) -> list[str]:
    if relevance == "HIGH":
        return [
            "Confirm exposure on affected production systems within 24 hours.",
            "Apply available patches or temporary mitigations.",
            "Increase monitoring and incident response readiness for this threat path.",
        ]

    if relevance == "MEDIUM":
        return [
            "Schedule remediation in the next maintenance window.",
            "Review detection coverage for related indicators and CVEs.",
            "Track remediation status in the security backlog.",
        ]

    return [
        "Monitor for relevance changes as new stack context or exploit data appears.",
        "Keep this item available as supporting intelligence.",
    ]


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        values: list[Any] = [value]
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        return []

    normalized: list[str] = []
    for item in values:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def _severity(entry: dict[str, Any]) -> float:
    raw = entry.get("severity")
    if raw is None:
        threat = entry.get("threat", {})
        if isinstance(threat, dict):
            raw = threat.get("severity")

    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _correlation_count(entry: dict[str, Any]) -> int:
    raw = entry.get("correlation_count", 0)
    try:
        count = int(raw)
    except (TypeError, ValueError):
        return 0
    return max(0, count)


def _threat_id(entry: dict[str, Any]) -> str:
    threat = entry.get("threat", {})
    if not isinstance(threat, dict):
        return ""
    return str(threat.get("id", "")).strip()


__all__ = ["run_reporting"]
