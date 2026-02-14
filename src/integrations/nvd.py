from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from common.http import get_json
from config.settings import get_settings

NVD_CVE_ENDPOINT = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_MAX_RESULTS_PER_PAGE = 2000


def _format_pub_start(pub_start: datetime) -> str:
    if pub_start.tzinfo is None:
        normalized = pub_start.replace(tzinfo=timezone.utc)
    else:
        normalized = pub_start.astimezone(timezone.utc)

    return normalized.strftime("%Y-%m-%dT%H:%M:%S.000")


def _build_headers() -> dict[str, str] | None:
    api_key = get_settings().NVD_API_KEY
    if not api_key:
        return None
    return {"apiKey": api_key}


def _to_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _minimal_cve_payload(vulnerability: dict[str, Any]) -> dict[str, Any] | None:
    cve = vulnerability.get("cve")
    if not isinstance(cve, dict):
        return None

    payload: dict[str, Any] = {"cve": cve}
    for field in ("published", "lastModified"):
        value = vulnerability.get(field)
        if value is not None:
            payload[field] = value

    return payload


def fetch_recent_cves(
    *,
    pub_start: datetime | None = None,
    results_per_page: int = 50,
) -> list[dict[str, Any]]:
    if results_per_page < 1:
        raise ValueError("results_per_page must be >= 1")
    if results_per_page > NVD_MAX_RESULTS_PER_PAGE:
        raise ValueError(
            f"results_per_page must be <= {NVD_MAX_RESULTS_PER_PAGE} for NVD API"
        )

    params: dict[str, Any] = {
        "startIndex": 0,
        "resultsPerPage": results_per_page,
    }
    if pub_start is not None:
        params["pubStartDate"] = _format_pub_start(pub_start)

    headers = _build_headers()
    start_index = 0
    cve_payloads: list[dict[str, Any]] = []

    while True:
        params["startIndex"] = start_index
        response = get_json(NVD_CVE_ENDPOINT, headers=headers, params=params)
        if not isinstance(response, dict):
            raise ValueError("Unexpected NVD response format")

        vulnerabilities = response.get("vulnerabilities")
        if not isinstance(vulnerabilities, list) or not vulnerabilities:
            break

        for vulnerability in vulnerabilities:
            if not isinstance(vulnerability, dict):
                continue

            payload = _minimal_cve_payload(vulnerability)
            if payload is not None:
                cve_payloads.append(payload)

        start_index += len(vulnerabilities)

        total_results = _to_int(response.get("totalResults"))
        if total_results is not None and start_index >= total_results:
            break
        if total_results is None and len(vulnerabilities) < results_per_page:
            break

    return cve_payloads


__all__ = ["fetch_recent_cves"]
