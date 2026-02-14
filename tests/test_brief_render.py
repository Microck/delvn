from __future__ import annotations

from datetime import datetime, timezone

from models.brief import ExecutiveBrief
from reporting.render import render_brief_md


def test_render_brief_md_includes_expected_sections() -> None:
    brief = ExecutiveBrief.model_validate(
        {
            "generated_at": datetime(2026, 2, 14, 18, 0, 0, tzinfo=timezone.utc),
            "stack_summary": "Products: Apache HTTP Server, PostgreSQL; Platforms: linux",
            "top_risks": [
                {
                    "headline": "Apache HTTP Server remote code execution",
                    "relevance": "HIGH",
                    "why_it_matters": "Exploit activity maps to the production web stack.",
                    "evidence": ["Product keyword match: apache http server"],
                    "recommended_actions": [
                        "Apply the latest upstream security patch."
                    ],
                }
            ],
            "notable_mentions": [
                {
                    "headline": "PostgreSQL extension denial-of-service",
                    "relevance": "MEDIUM",
                    "why_it_matters": "Database availability risk for customer workloads.",
                    "evidence": ["Product keyword match: postgresql"],
                    "recommended_actions": [
                        "Schedule remediation in next maintenance window."
                    ],
                }
            ],
        }
    )

    markdown = render_brief_md(brief)

    assert "# Executive Threat Brief" in markdown
    assert "## Stack Summary" in markdown
    assert "## Top Risks" in markdown
    assert "## Notable Mentions" in markdown
    assert "### 1. Apache HTTP Server remote code execution" in markdown
    assert (
        "- **Why it matters:** Exploit activity maps to the production web stack."
        in markdown
    )
    assert "- **Recommended actions:**" in markdown
