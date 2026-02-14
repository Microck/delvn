from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any

from dateutil import parser

from models.unified_threat import ThreatIndicator, UnifiedThreat


def _to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _to_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value

    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    try:
        return parser.isoparse(text)
    except ValueError:
        try:
            return parser.parse(text)
        except (OverflowError, TypeError, ValueError):
            return None


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            unique_values.append(value)
    return unique_values


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None

    if parsed < 0 or parsed > 10:
        return None

    return parsed


def _nvd_cve_block(payload: dict[str, Any]) -> dict[str, Any]:
    cve_block = payload.get("cve")
    if isinstance(cve_block, dict):
        return cve_block
    return payload


def _nvd_summary(payload: dict[str, Any]) -> str:
    cve_block = _nvd_cve_block(payload)
    descriptions = cve_block.get("descriptions")
    if not isinstance(descriptions, list):
        return ""

    for description in descriptions:
        if not isinstance(description, dict):
            continue
        if description.get("lang") == "en":
            value = _to_str(description.get("value"))
            if value:
                return value

    for description in descriptions:
        if not isinstance(description, dict):
            continue
        value = _to_str(description.get("value"))
        if value:
            return value

    return ""


def _nvd_references(payload: dict[str, Any]) -> list[str]:
    cve_block = _nvd_cve_block(payload)
    references = cve_block.get("references")
    if not isinstance(references, list):
        return []

    urls = [
        _to_str(reference.get("url"))
        for reference in references
        if isinstance(reference, dict)
    ]
    return _unique(url for url in urls if url)


def _nvd_severity(payload: dict[str, Any]) -> float | None:
    cve_block = _nvd_cve_block(payload)
    metrics = cve_block.get("metrics")
    if not isinstance(metrics, dict):
        return _to_float(payload.get("severity"))

    metric_keys = ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2")
    for key in metric_keys:
        metric_list = metrics.get(key)
        if not isinstance(metric_list, list):
            continue

        for metric_item in metric_list:
            if not isinstance(metric_item, dict):
                continue

            cvss_data = metric_item.get("cvssData")
            if isinstance(cvss_data, dict):
                score = _to_float(cvss_data.get("baseScore"))
                if score is not None:
                    return score

            score = _to_float(metric_item.get("baseScore"))
            if score is not None:
                return score

    return _to_float(payload.get("severity"))


def _rss_tags(payload: dict[str, Any]) -> list[str]:
    tags_value = payload.get("tags")
    if not isinstance(tags_value, list):
        return []

    tags: list[str] = []
    for tag in tags_value:
        if isinstance(tag, dict):
            tags.append(_to_str(tag.get("term")))
            continue
        tags.append(_to_str(tag))

    return _unique([tag for tag in tags if tag])


def _rss_references(payload: dict[str, Any]) -> list[str]:
    references: list[str] = []

    link = _to_str(payload.get("link"))
    if link:
        references.append(link)

    links = payload.get("links")
    if isinstance(links, list):
        for link_entry in links:
            if not isinstance(link_entry, dict):
                continue
            href = _to_str(link_entry.get("href"))
            if href:
                references.append(href)

    return _unique(references)


def normalize_nvd_cve(payload: dict[str, Any]) -> UnifiedThreat:
    cve_block = _nvd_cve_block(payload)
    cve_id = _to_str(cve_block.get("id") or payload.get("id") or payload.get("cve_id"))
    if not cve_id:
        raise ValueError("NVD payload missing cve id")

    summary = _nvd_summary(payload)
    published_at = _to_datetime(
        payload.get("published")
        or cve_block.get("published")
        or payload.get("published_at")
    )
    observed_at = _to_datetime(
        payload.get("lastModified")
        or cve_block.get("lastModified")
        or payload.get("updated")
        or payload.get("observed_at")
    )

    return UnifiedThreat(
        id=f"nvd:{cve_id}",
        source="nvd",
        type="cve",
        title=cve_id,
        summary=summary or f"NVD record for {cve_id}",
        published_at=published_at,
        observed_at=observed_at,
        severity=_nvd_severity(payload),
        indicators=[ThreatIndicator(type="cve", value=cve_id)],
        tags=["cve"],
        references=_nvd_references(payload),
        raw=payload,
    )


def normalize_otx_indicator(payload: dict[str, Any]) -> UnifiedThreat:
    indicator_value = _to_str(
        payload.get("indicator") or payload.get("value") or payload.get("ioc")
    )
    if not indicator_value:
        raise ValueError("OTX payload missing indicator value")

    indicator_type = _to_str(
        payload.get("type") or payload.get("indicator_type") or "indicator"
    ).lower()

    title = _to_str(payload.get("title"))
    if not title:
        title = f"{indicator_type}: {indicator_value}"

    summary = _to_str(payload.get("description"))
    references: list[str] = []
    for field in ("url", "reference"):
        value = _to_str(payload.get(field))
        if value:
            references.append(value)

    reference_list = payload.get("references")
    if isinstance(reference_list, list):
        references.extend(_to_str(reference) for reference in reference_list)

    tags_value = payload.get("tags")
    tags: list[str] = [indicator_type]
    if isinstance(tags_value, list):
        tags.extend(_to_str(tag) for tag in tags_value)

    return UnifiedThreat(
        id=f"otx:{indicator_type}:{indicator_value}",
        source="otx",
        type="indicator",
        title=title,
        summary=summary,
        published_at=_to_datetime(
            payload.get("created") or payload.get("published_at")
        ),
        observed_at=_to_datetime(payload.get("modified") or payload.get("observed_at")),
        severity=_to_float(payload.get("severity") or payload.get("priority")),
        indicators=[ThreatIndicator(type=indicator_type, value=indicator_value)],
        tags=_unique([tag for tag in tags if tag]),
        references=_unique([reference for reference in references if reference]),
        raw=payload,
    )


def normalize_rss_item(payload: dict[str, Any]) -> UnifiedThreat:
    source = _to_str(payload.get("source") or payload.get("feed") or "rss")
    base_id = _to_str(payload.get("id") or payload.get("guid") or payload.get("link"))
    if not base_id:
        fingerprint = _to_str(payload.get("title") or payload.get("summary") or payload)
        base_id = sha256(fingerprint.encode("utf-8")).hexdigest()[:16]

    title = _to_str(payload.get("title") or "Untitled security item")
    summary = _to_str(payload.get("summary") or payload.get("description"))

    return UnifiedThreat(
        id=f"{source}:{base_id}",
        source=source,
        type="news",
        title=title,
        summary=summary,
        published_at=_to_datetime(
            payload.get("published") or payload.get("published_at")
        ),
        observed_at=_to_datetime(payload.get("updated") or payload.get("observed_at")),
        severity=_to_float(payload.get("severity")),
        indicators=[],
        tags=_rss_tags(payload),
        references=_rss_references(payload),
        raw=payload,
    )


__all__ = ["normalize_nvd_cve", "normalize_otx_indicator", "normalize_rss_item"]
