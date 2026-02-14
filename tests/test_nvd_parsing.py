from __future__ import annotations

from normalization.normalize import normalize_nvd_cve


def _nvd_payload() -> dict[str, object]:
    return {
        "cve": {
            "id": "CVE-2026-4242",
            "descriptions": [
                {
                    "lang": "en",
                    "value": "Privilege escalation in sample package manager.",
                }
            ],
            "metrics": {
                "cvssMetricV31": [{"cvssData": {"baseScore": 8.7}}],
            },
        },
        "published": "2026-02-10T10:00:00Z",
        "lastModified": "2026-02-12T09:00:00Z",
    }


def test_normalize_nvd_extracts_cve_id_and_description() -> None:
    threat = normalize_nvd_cve(_nvd_payload())

    assert threat.id == "nvd:CVE-2026-4242"
    assert threat.title == "CVE-2026-4242"
    assert threat.summary == "Privilege escalation in sample package manager."


def test_normalize_nvd_extracts_numeric_severity() -> None:
    threat = normalize_nvd_cve(_nvd_payload())

    assert threat.severity is not None
    assert 0.0 <= threat.severity <= 10.0
    assert threat.severity == 8.7


def test_normalized_content_text_contains_cve_id() -> None:
    threat = normalize_nvd_cve(_nvd_payload())

    assert "CVE-2026-4242" in threat.content_text()
