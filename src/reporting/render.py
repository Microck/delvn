from __future__ import annotations

from datetime import datetime, timezone

from models.brief import BriefEntry, ExecutiveBrief


def render_brief_md(brief: ExecutiveBrief) -> str:
    lines: list[str] = [
        "# Executive Threat Brief",
        "",
        f"_Generated: {_format_timestamp(brief.generated_at)}_",
        "",
        "## Stack Summary",
        "",
        brief.stack_summary,
        "",
        "## Top Risks",
        "",
    ]

    if brief.top_risks:
        for index, entry in enumerate(brief.top_risks, start=1):
            lines.extend(_render_entry(index, entry))
    else:
        lines.append("- No HIGH or MEDIUM risks were identified.")
        lines.append("")

    lines.extend(["## Notable Mentions", ""])
    if brief.notable_mentions:
        for index, entry in enumerate(brief.notable_mentions, start=1):
            lines.extend(_render_entry(index, entry))
    else:
        lines.append("- No additional notable threats.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_markdown(brief: ExecutiveBrief) -> str:
    return render_brief_md(brief)


def _render_entry(index: int, entry: BriefEntry) -> list[str]:
    lines = [
        f"### {index}. {entry.headline}",
        "",
        f"- **Relevance:** {entry.relevance}",
        f"- **Why it matters:** {entry.why_it_matters}",
    ]

    if entry.evidence:
        lines.append("- **Evidence:**")
        lines.extend(f"  - {item}" for item in entry.evidence)
    else:
        lines.append("- **Evidence:** None provided")

    if entry.recommended_actions:
        lines.append("- **Recommended actions:**")
        lines.extend(f"  - {item}" for item in entry.recommended_actions)
    else:
        lines.append("- **Recommended actions:** None provided")

    lines.append("")
    return lines


def _format_timestamp(value: datetime) -> str:
    normalized = value
    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=timezone.utc)

    return (
        normalized.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


__all__ = ["render_brief_md", "render_markdown"]
