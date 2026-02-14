from __future__ import annotations

import re
from typing import Any, Iterable

from correlation.scoring import score_correlation
from models.correlation import CorrelationLink
from models.unified_threat import UnifiedThreat

TOKEN_PATTERN = re.compile(r"\b[a-z0-9][a-z0-9._:/-]{2,}\b", re.IGNORECASE)
CVE_PATTERN = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
HASH_PATTERN = re.compile(r"\b[a-f0-9]{32,64}\b", re.IGNORECASE)
DOMAIN_PATTERN = re.compile(
    r"\b[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+\b",
    re.IGNORECASE,
)


def match_correlation_candidates(
    source: UnifiedThreat,
    vector_hits: list[dict[str, Any]],
    *,
    min_confidence: float = 0.0,
) -> list[CorrelationLink]:
    source_text = source.content_text()
    source_terms = _extract_terms(source_text)
    source_cves = _extract_cves(source_text)
    source_iocs = _extract_iocs(source_text)

    threshold = max(0.0, min(1.0, min_confidence))
    links_by_target: dict[str, CorrelationLink] = {}

    for hit in vector_hits:
        target_id = _to_text(hit.get("id"))
        if not target_id or target_id == source.id:
            continue

        hit_text = _hit_content_text(hit)
        target_terms = _extract_terms(hit_text)
        target_cves = _extract_cves(hit_text)
        target_iocs = _extract_iocs(hit_text)

        shared_term_count, shared_reasons = _shared_term_details(
            source_terms=source_terms,
            target_terms=target_terms,
            source_cves=source_cves,
            target_cves=target_cves,
            source_iocs=source_iocs,
            target_iocs=target_iocs,
        )

        similarity = _to_float(hit.get("score"))
        same_source = _to_text(hit.get("source")).lower() == source.source.lower()
        confidence, reasons = score_correlation(
            similarity=similarity,
            shared_terms=shared_term_count,
            same_source=same_source,
        )
        reasons.extend(shared_reasons)

        if confidence < threshold:
            continue

        link = CorrelationLink(
            source_id=source.id,
            target_id=target_id,
            confidence=confidence,
            reasons=reasons,
            similarity=similarity,
        )
        existing = links_by_target.get(target_id)
        if existing is None or link.confidence > existing.confidence:
            links_by_target[target_id] = link

    return sorted(
        links_by_target.values(),
        key=lambda correlation_link: correlation_link.confidence,
        reverse=True,
    )


def _shared_term_details(
    *,
    source_terms: set[str],
    target_terms: set[str],
    source_cves: set[str],
    target_cves: set[str],
    source_iocs: set[str],
    target_iocs: set[str],
) -> tuple[int, list[str]]:
    token_overlap = source_terms & target_terms
    cve_overlap = source_cves & target_cves
    ioc_overlap = source_iocs & target_iocs

    normalized_overlap = set(token_overlap)
    normalized_overlap.update(term.lower() for term in cve_overlap)
    normalized_overlap.update(term.lower() for term in ioc_overlap)

    reasons: list[str] = []
    if cve_overlap:
        reasons.append("Shared CVE identifiers: " + ", ".join(sorted(cve_overlap)[:3]))
    if ioc_overlap:
        reasons.append("Shared IOCs: " + ", ".join(sorted(ioc_overlap)[:3]))
    if token_overlap and not (cve_overlap or ioc_overlap):
        reasons.append("Token overlap: " + ", ".join(sorted(token_overlap)[:3]))

    return len(normalized_overlap), reasons


def _hit_content_text(hit: dict[str, Any]) -> str:
    values = [_to_text(value) for value in _iter_hit_values(hit)]
    return "\n".join(value for value in values if value)


def _iter_hit_values(hit: dict[str, Any]) -> Iterable[Any]:
    for key in ("id", "source", "type", "title", "summary", "content"):
        value = hit.get(key)
        if value:
            yield value

    for key in ("tags", "references"):
        value = hit.get(key)
        if isinstance(value, list):
            yield from value

    indicators = hit.get("indicators")
    if isinstance(indicators, list):
        for indicator in indicators:
            if isinstance(indicator, dict):
                yield indicator.get("type")
                yield indicator.get("value")
            else:
                yield indicator


def _extract_terms(text: str) -> set[str]:
    return {match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)}


def _extract_cves(text: str) -> set[str]:
    return {match.group(0).upper() for match in CVE_PATTERN.finditer(text)}


def _extract_iocs(text: str) -> set[str]:
    iocs: set[str] = set()
    for pattern in (URL_PATTERN, IPV4_PATTERN, HASH_PATTERN, DOMAIN_PATTERN):
        iocs.update(match.group(0).lower() for match in pattern.finditer(text))
    return iocs


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


__all__ = ["match_correlation_candidates"]
