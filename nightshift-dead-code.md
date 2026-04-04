# Nightshift: Dead Code Analysis

**Repo:** Microck/delvn
**Date:** 2026-04-04
**Agent:** Nightshift v3 (GLM 5.1)

## Summary

Delvn is a fairly clean Python codebase with **36 source files** and **13 test files**. The analysis found minimal dead code. Two configuration fields are unreferenced, one model module is unused in production code, and there is minor utility duplication.

## Findings

### P2 — Unused Configuration Fields

**File:** `src/config/settings.py` (lines 28-29)

```python
FOUNDRY_ENDPOINT: str | None = None
FOUNDRY_API_KEY: str | None = None
```

These fields are defined in the `Settings` model but never referenced anywhere in `src/`. No integration, agent, or storage module reads them. They appear to be remnants of a planned integration that was never implemented.

**Action:** Remove both fields from `Settings` and any corresponding `.env` documentation.

### P2 — Unused Threat Models in Production Path

**File:** `src/models/threat.py` (66 lines)

The module defines `ThreatBase`, `CVEThreat`, `IndicatorThreat`, `CampaignThreat`, `IndicatorType`, and `ThreatType`. These are re-exported via `src/models/__init__.py` but only imported in `tests/test_threat_model.py`. The production pipeline uses `UnifiedThreat` from `src/models/unified_threat.py` exclusively.

**Status:** Not strictly dead (tests exist), but the production code never uses these models. The normalization layer (`src/normalization/normalize.py`) directly constructs `UnifiedThreat` instances without intermediate typed models.

**Action:** Consider merging the typed models into `UnifiedThreat` or documenting them as "schema reference only" to prevent confusion.

### P3 — Duplicated Utility Functions

The following private helper functions are duplicated across modules:

| Function | Files |
|----------|-------|
| `_to_text(value)` | `rss.py:8`, `correlation/matcher.py:154` |
| `_to_float(value)` | `correlation/matcher.py:162`, `normalization/normalize.py:50` (different signature: returns `float | None`) |
| `_to_str(value)` / `_as_text(value)` | `normalization/normalize.py:12`, `integrations/otx.py:14`, `integrations/rss.py:8` |

**Status:** Not dead code, but violates DRY. The implementations are identical.

**Action:** Extract to `src/common/text.py` or `src/common/coerce.py` and import from there.

### P3 — No Dead Functions Found

All `__all__` exports are referenced. No commented-out code blocks. No unreachable branches. All imports are used.

## Positive Observations

- Clean `__all__` exports on every module
- Consistent error handling pattern (try/except with stats counters)
- Good test coverage for core logic (normalization, correlation, prioritization)
- No stale dependencies or unused imports detected

## Metrics

| Metric | Value |
|--------|-------|
| Source files | 36 |
| Test files | 13 |
| Dead functions | 0 |
| Dead config fields | 2 (FOUNDRY_*) |
| Unused model exports | 6 (threat.py types) |
| Duplicated helpers | 3 patterns |
| Commented-out code | 0 blocks |
