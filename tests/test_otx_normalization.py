from __future__ import annotations

import pytest

from normalization.normalize import normalize_otx_indicator


@pytest.mark.parametrize(
    ("payload", "indicator_type", "indicator_value"),
    [
        (
            {
                "type": "ip",
                "indicator": "203.0.113.10",
                "description": "Suspicious command-and-control endpoint",
            },
            "ip",
            "203.0.113.10",
        ),
        (
            {
                "type": "domain",
                "indicator": "malicious-example.org",
                "description": "Observed in phishing infrastructure",
            },
            "domain",
            "malicious-example.org",
        ),
        (
            {
                "type": "url",
                "indicator": "https://malicious.example/download",
                "description": "Used for malware payload delivery",
            },
            "url",
            "https://malicious.example/download",
        ),
    ],
)
def test_otx_indicator_normalization_for_common_indicator_types(
    payload: dict[str, str],
    indicator_type: str,
    indicator_value: str,
) -> None:
    threat = normalize_otx_indicator(payload)

    assert threat.id.startswith(f"otx:{indicator_type}:")
    assert len(threat.indicators) == 1
    assert {
        "type": threat.indicators[0].type,
        "value": threat.indicators[0].value,
    } == {
        "type": indicator_type,
        "value": indicator_value,
    }
