from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ThreatType(str, Enum):
    CVE = "cve"
    INDICATOR = "indicator"
    CAMPAIGN = "campaign"


class IndicatorType(str, Enum):
    DOMAIN = "domain"
    IP = "ip"
    URL = "url"
    HASH = "hash"
    EMAIL = "email"


class ThreatBase(BaseModel):
    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    type: ThreatType
    title: str = Field(min_length=1)
    description: str | None = None
    published_at: datetime | None = None
    observed_at: datetime | None = None
    severity: float | None = Field(default=None, ge=0.0, le=10.0)
    references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    raw: dict[str, Any]

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class CVEThreat(ThreatBase):
    type: Literal[ThreatType.CVE] = ThreatType.CVE
    cve_id: str = Field(min_length=1)
    cvss_vector: str | None = None
    cwe: list[str] | None = None


class IndicatorThreat(ThreatBase):
    type: Literal[ThreatType.INDICATOR] = ThreatType.INDICATOR
    indicator: str = Field(min_length=1)
    indicator_type: IndicatorType


class CampaignThreat(ThreatBase):
    type: Literal[ThreatType.CAMPAIGN] = ThreatType.CAMPAIGN
    campaign: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)


__all__ = [
    "CampaignThreat",
    "CVEThreat",
    "IndicatorThreat",
    "IndicatorType",
    "ThreatBase",
    "ThreatType",
]
