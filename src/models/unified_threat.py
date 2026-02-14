from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ThreatIndicator(BaseModel):
    type: str = Field(min_length=1)
    value: str = Field(min_length=1)

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class UnifiedThreat(BaseModel):
    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = ""
    published_at: datetime | None = None
    observed_at: datetime | None = None
    severity: float | None = Field(default=None, ge=0.0, le=10.0)
    indicators: list[ThreatIndicator] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    raw: dict[str, Any]

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    def content_text(self) -> str:
        parts: list[str] = [self.id, self.title]
        if self.summary:
            parts.append(self.summary)

        for indicator in self.indicators:
            parts.append(indicator.type)
            parts.append(indicator.value)

        parts.extend(self.tags)
        parts.extend(self.references)

        return "\n".join(part for part in parts if part)


__all__ = ["ThreatIndicator", "UnifiedThreat"]
