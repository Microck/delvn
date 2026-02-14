from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class BriefEntry(BaseModel):
    headline: str = Field(min_length=1)
    relevance: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class ExecutiveBrief(BaseModel):
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    stack_summary: str = Field(min_length=1)
    top_risks: list[BriefEntry] = Field(default_factory=list)
    notable_mentions: list[BriefEntry] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


__all__ = ["BriefEntry", "ExecutiveBrief"]
