from __future__ import annotations

from normalization.normalize import normalize_rss_item


def test_normalize_rss_item_uses_stable_rss_prefix() -> None:
    payload = {
        "guid": "security-story-42",
        "title": "Active exploitation in enterprise VPN appliances",
        "summary": "Researchers observed exploitation attempts over the past 24 hours.",
        "link": "https://example.com/security-story-42",
    }

    threat = normalize_rss_item(payload)

    assert threat.id.startswith("rss:")
    assert threat.source == "rss"


def test_normalize_rss_item_content_text_contains_title_and_summary() -> None:
    payload = {
        "title": "New ransomware campaign targets managed file transfer",
        "summary": "Operators are chaining an auth bypass with remote code execution.",
        "link": "https://example.com/security-story-43",
    }

    threat = normalize_rss_item(payload)
    content_text = threat.content_text()

    assert payload["title"] in content_text
    assert payload["summary"] in content_text
