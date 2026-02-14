from __future__ import annotations

import pytest
from pydantic import ValidationError

from models.threat import (
    CampaignThreat,
    CVEThreat,
    IndicatorThreat,
    IndicatorType,
    ThreatType,
)


def _base_fields(threat_id: str, *, source: str = "unit") -> dict[str, object]:
    return {
        "id": threat_id,
        "source": source,
        "title": "Example threat",
        "raw": {"payload": "sample"},
    }


def test_valid_cve_threat() -> None:
    threat = CVEThreat(
        **_base_fields("cve:CVE-2025-1234", source="nvd"),
        cve_id="CVE-2025-1234",
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        references=["https://nvd.nist.gov/vuln/detail/CVE-2025-1234"],
    )

    assert threat.type is ThreatType.CVE
    assert threat.cve_id == "CVE-2025-1234"


def test_valid_indicator_threat() -> None:
    threat = IndicatorThreat(
        **_base_fields("otx:indicator:1.2.3.4", source="otx"),
        indicator="1.2.3.4",
        indicator_type=IndicatorType.IP,
        tags=["ioc"],
    )

    assert threat.type is ThreatType.INDICATOR
    assert threat.indicator_type is IndicatorType.IP


def test_valid_campaign_threat() -> None:
    threat = CampaignThreat(
        **_base_fields("rss:campaign:storm-001", source="rss"),
        campaign="Storm-001",
        aliases=["APT-Example"],
    )

    assert threat.type is ThreatType.CAMPAIGN
    assert threat.aliases == ["APT-Example"]


@pytest.mark.parametrize("severity", [-0.1, 10.1])
def test_invalid_severity_rejected(severity: float) -> None:
    with pytest.raises(ValidationError):
        IndicatorThreat(
            **_base_fields("otx:indicator:bad-severity", source="otx"),
            indicator="bad.example",
            indicator_type=IndicatorType.DOMAIN,
            severity=severity,
        )


def test_id_prefixes_are_stable() -> None:
    cve = CVEThreat(
        **_base_fields("cve:CVE-2025-1000", source="nvd"), cve_id="CVE-2025-1000"
    )
    indicator = IndicatorThreat(
        **_base_fields("otx:indicator:1.2.3.4", source="otx"),
        indicator="1.2.3.4",
        indicator_type=IndicatorType.IP,
    )
    campaign = CampaignThreat(
        **_base_fields("rss:campaign:cluster-7", source="rss"),
        campaign="Cluster-7",
    )

    assert cve.id.startswith("cve:")
    assert indicator.id.startswith("otx:indicator:")
    assert campaign.id.startswith("rss:campaign:")


def test_references_defaults_and_type() -> None:
    default_refs_threat = IndicatorThreat(
        **_base_fields("otx:indicator:domain-example", source="otx"),
        indicator="example.org",
        indicator_type=IndicatorType.DOMAIN,
    )
    explicit_refs_threat = IndicatorThreat(
        **_base_fields("otx:indicator:url-example", source="otx"),
        indicator="https://example.org",
        indicator_type=IndicatorType.URL,
        references=["https://example.org/report", "https://otx.alienvault.com"],
    )

    assert default_refs_threat.references == []
    assert explicit_refs_threat.references == [
        "https://example.org/report",
        "https://otx.alienvault.com",
    ]
    assert all(
        isinstance(reference, str) for reference in explicit_refs_threat.references
    )
