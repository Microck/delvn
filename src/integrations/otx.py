from __future__ import annotations

from typing import Any

import httpx

from common.http import get_json
from config.settings import get_settings

_OTX_SUBSCRIBED_PULSES_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"
_OTX_PUBLIC_PULSES_URL = "https://otx.alienvault.com/api/v1/pulses"


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return ""
    return str(value).strip()


def _optional_api_headers() -> dict[str, str] | None:
    settings = get_settings()
    if settings.OTX_API_KEY:
        return {"X-OTX-API-KEY": settings.OTX_API_KEY}
    return None


def _to_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    items: list[str] = []
    for entry in value:
        if isinstance(entry, dict):
            text = _as_text(
                entry.get("name")
                or entry.get("tag")
                or entry.get("term")
                or entry.get("value")
            )
        else:
            text = _as_text(entry)

        if text:
            items.append(text)

    return items


def _looks_like_indicator(payload: dict[str, Any]) -> bool:
    return any(payload.get(key) for key in ("indicator", "value", "ioc"))


def _extract_feed_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            return [item for item in results if isinstance(item, dict)]
        if _looks_like_indicator(payload):
            return [payload]

    return []


def _build_indicator_payload(
    indicator: dict[str, Any],
    *,
    pulse: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    indicator_value = _as_text(
        indicator.get("indicator") or indicator.get("value") or indicator.get("ioc")
    )
    if not indicator_value:
        return None

    payload = dict(indicator)
    payload.setdefault("indicator", indicator_value)

    if pulse is None:
        return payload

    pulse_name = _as_text(pulse.get("name"))
    if pulse_name and not _as_text(payload.get("title")):
        payload["title"] = pulse_name

    pulse_description = _as_text(pulse.get("description"))
    if pulse_description and not _as_text(payload.get("description")):
        payload["description"] = pulse_description

    pulse_created = _as_text(pulse.get("created"))
    if pulse_created and not _as_text(payload.get("created")):
        payload["created"] = pulse_created

    pulse_modified = _as_text(pulse.get("modified"))
    if pulse_modified and not _as_text(payload.get("modified")):
        payload["modified"] = pulse_modified

    pulse_permalink = _as_text(pulse.get("permalink"))
    if pulse_permalink and not _as_text(payload.get("url")):
        payload["url"] = pulse_permalink

    pulse_references = _to_string_list(pulse.get("references"))
    if pulse_references and not isinstance(payload.get("references"), list):
        payload["references"] = pulse_references

    pulse_tags = _to_string_list(pulse.get("tags"))
    if pulse_tags and not isinstance(payload.get("tags"), list):
        payload["tags"] = pulse_tags

    return payload


def _extract_indicators(payload: Any, *, limit: int) -> list[dict[str, Any]]:
    indicators: list[dict[str, Any]] = []

    for item in _extract_feed_items(payload):
        nested_indicators = item.get("indicators")
        if isinstance(nested_indicators, list):
            for indicator in nested_indicators:
                if not isinstance(indicator, dict):
                    continue
                normalized = _build_indicator_payload(indicator, pulse=item)
                if normalized is None:
                    continue
                indicators.append(normalized)
                if len(indicators) >= limit:
                    return indicators
            continue

        normalized = _build_indicator_payload(item)
        if normalized is None:
            continue
        indicators.append(normalized)
        if len(indicators) >= limit:
            return indicators

    return indicators


def fetch_recent_indicators(limit: int = 50) -> list[dict[str, Any]]:
    requested = max(1, limit)
    params = {"limit": requested}
    headers = _optional_api_headers()

    try:
        payload = get_json(_OTX_SUBSCRIBED_PULSES_URL, headers=headers, params=params)
    except httpx.HTTPStatusError as exc:
        if headers is not None or exc.response.status_code not in {401, 403}:
            raise
        payload = get_json(_OTX_PUBLIC_PULSES_URL, params=params)

    return _extract_indicators(payload, limit=requested)


__all__ = ["fetch_recent_indicators"]
