from __future__ import annotations

from models.unified_threat import UnifiedThreat
from normalization.normalize import (
    normalize_nvd_cve,
    normalize_otx_indicator,
    normalize_rss_item,
)


def test_normalize_nvd_cve_returns_stable_unified_shape() -> None:
    payload = {
        "cve": {
            "id": "CVE-2026-1111",
            "descriptions": [
                {
                    "lang": "en",
                    "value": "Remote code execution in example appliance.",
                }
            ],
            "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8}}]},
            "references": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2026-1111"}],
        },
        "published": "2026-01-15T10:00:00Z",
        "lastModified": "2026-01-15T12:00:00Z",
    }

    threat = normalize_nvd_cve(payload)

    assert isinstance(threat, UnifiedThreat)
    assert threat.id == "nvd:CVE-2026-1111"
    assert threat.source == "nvd"
    assert threat.type == "cve"
    assert threat.title
    assert "CVE-2026-1111" in threat.content_text()


def test_normalize_otx_indicator_returns_stable_unified_shape() -> None:
    payload = {
        "type": "ip",
        "indicator": "1.2.3.4",
        "title": "Known C2 IP",
        "description": "Observed communicating with malware infrastructure.",
        "tags": ["malware", "c2"],
        "url": "https://otx.alienvault.com/indicator/ip/1.2.3.4",
        "created": "2026-01-20T10:30:00Z",
        "modified": "2026-01-21T08:45:00Z",
    }

    threat = normalize_otx_indicator(payload)

    assert isinstance(threat, UnifiedThreat)
    assert threat.id == "otx:ip:1.2.3.4"
    assert threat.source == "otx"
    assert threat.type == "indicator"
    assert threat.title
    assert "1.2.3.4" in threat.content_text()


def test_normalize_rss_item_returns_stable_unified_shape() -> None:
    payload = {
        "source": "bleepingcomputer",
        "guid": "bc-article-42",
        "title": "Security bulletin: active exploitation observed",
        "summary": "Attackers are exploiting CVE-2026-1111 in the wild.",
        "link": "https://www.bleepingcomputer.com/news/security/example-story/",
        "published": "2026-01-22T09:00:00Z",
        "updated": "2026-01-22T09:30:00Z",
        "tags": [{"term": "vulnerability"}, {"term": "exploitation"}],
    }

    threat = normalize_rss_item(payload)

    assert isinstance(threat, UnifiedThreat)
    assert threat.id == "bleepingcomputer:bc-article-42"
    assert threat.source == "bleepingcomputer"
    assert threat.type == "news"
    assert threat.title
    assert "CVE-2026-1111" in threat.content_text()
