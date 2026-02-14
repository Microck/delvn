from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserStack(BaseModel):
    products: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @field_validator("products", "platforms", "exclude", "keywords", mode="before")
    @classmethod
    def _normalize_values(cls, value: Any) -> list[str]:
        if value is None:
            return []

        if isinstance(value, str):
            values = [value]
        elif isinstance(value, (list, tuple, set)):
            values = list(value)
        else:
            raise ValueError("Stack fields must be lists of strings.")

        deduped_values: list[str] = []
        seen_values: set[str] = set()
        for item in values:
            display_value = str(item).strip()
            if not display_value:
                continue

            match_value = display_value.lower()
            if match_value in seen_values:
                continue

            seen_values.add(match_value)
            deduped_values.append(display_value)

        return deduped_values

    def match_terms(self) -> set[str]:
        return {
            value.lower() for value in [*self.products, *self.platforms, *self.keywords]
        }

    def exclude_terms(self) -> set[str]:
        return {value.lower() for value in self.exclude}


def load_user_stack(path: str = "src/config/user_stack.yaml") -> UserStack:
    raw_config = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if raw_config is None:
        raw_config = {}

    if not isinstance(raw_config, dict):
        raise ValueError("User stack config must be a YAML mapping.")

    return UserStack.model_validate(raw_config)


__all__ = ["UserStack", "load_user_stack"]
