from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, model_validator


def build_correlation_id(source_id: str, target_id: str) -> str:
    return f"corr:{source_id}->{target_id}"


class CorrelationLink(BaseModel):
    id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    similarity: float | None = None

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def _populate_id(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data

        if data.get("id"):
            return data

        source_id = data.get("source_id")
        target_id = data.get("target_id")
        if not isinstance(source_id, str) or not isinstance(target_id, str):
            return data

        hydrated = dict(data)
        hydrated["id"] = build_correlation_id(source_id, target_id)
        return hydrated


__all__ = ["CorrelationLink", "build_correlation_id"]
