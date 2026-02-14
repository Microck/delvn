from __future__ import annotations

from typing import Any

import feedparser


def _to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def fetch_feed(url: str) -> list[dict[str, Any]]:
    parsed = feedparser.parse(url)
    entries = getattr(parsed, "entries", []) or []
    items: list[dict[str, Any]] = []

    for entry in entries:
        item: dict[str, Any] = {
            "title": _to_text(entry.get("title")),
            "link": _to_text(entry.get("link")),
            "summary": _to_text(entry.get("summary") or entry.get("description")),
            "published": _to_text(
                entry.get("published") or entry.get("updated") or entry.get("pubDate")
            ),
        }

        guid = _to_text(entry.get("id") or entry.get("guid"))
        if guid:
            item["guid"] = guid

        updated = _to_text(entry.get("updated"))
        if updated:
            item["updated"] = updated

        tags = entry.get("tags")
        if isinstance(tags, list):
            item["tags"] = tags

        links = entry.get("links")
        if isinstance(links, list):
            item["links"] = links

        items.append(item)

    return items


__all__ = ["fetch_feed"]
