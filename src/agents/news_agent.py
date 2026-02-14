from __future__ import annotations

import os
from urllib.parse import urlparse

from integrations.rss import fetch_feed
from normalization.normalize import normalize_rss_item
from storage.cosmos import CosmosStore

DEFAULT_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
]


def _resolve_feeds() -> list[str]:
    override = os.getenv("RSS_FEED_URLS", "")
    if not override:
        return DEFAULT_FEEDS.copy()

    feeds = [feed.strip() for feed in override.split(",") if feed.strip()]
    if feeds:
        return feeds
    return DEFAULT_FEEDS.copy()


def _feed_source(url: str) -> str:
    source = urlparse(url).netloc.strip().lower()
    if source.startswith("www."):
        source = source[4:]
    if not source:
        return "rss"
    return source.replace(":", "-")


def run_news_collection() -> dict[str, int]:
    feeds = _resolve_feeds()
    stats = {
        "feeds": len(feeds),
        "fetched": 0,
        "normalized": 0,
        "stored": 0,
        "errors": 0,
    }

    store = CosmosStore()

    for feed_url in feeds:
        try:
            items = fetch_feed(feed_url)
        except Exception:
            stats["errors"] += 1
            continue

        stats["fetched"] += len(items)
        source = _feed_source(feed_url)

        for item in items:
            payload = dict(item)
            payload.setdefault("source", source)

            try:
                normalized = normalize_rss_item(payload)
                stats["normalized"] += 1
                store.upsert_threat(normalized.model_dump(mode="json"))
                stats["stored"] += 1
            except Exception:
                stats["errors"] += 1

    return stats


__all__ = ["DEFAULT_FEEDS", "run_news_collection"]
