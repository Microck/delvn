---
phase: 02-collection-agents
plan: 01
subsystem: api
tags: [pydantic, normalization, threat-intel, nvd, otx, rss]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: base package scaffold and existing threat model conventions used by the unified model
provides:
  - Unified threat schema shared by all collectors
  - Deterministic source-specific normalizers returning `UnifiedThreat`
  - Representative normalization tests to lock output stability
affects: [02-02, 02-03, 02-04, 03-correlation]

# Tech tracking
tech-stack:
  added: [no new dependencies]
  patterns: [source-prefixed IDs for normalization, pure functions for source-to-unified mapping]

key-files:
  created: [src/models/unified_threat.py, src/agents/__init__.py, src/integrations/__init__.py, src/normalization/__init__.py, src/normalization/normalize.py, tests/test_normalization.py, .planning/phases/02-collection-agents/02-01-SUMMARY.md]
  modified: [.planning/STATE.md]

key-decisions:
  - "Represent IOC material as a dedicated `ThreatIndicator` list so all sources share the same indicator shape."
  - "Normalize IDs with stable source prefixes (`nvd:`, `otx:`, `rss source:`) to preserve origin identity while keeping one unified schema."

patterns-established:
  - "Normalization Pattern: each source gets a deterministic, side-effect-free function returning `UnifiedThreat`."
  - "Search Content Pattern: `content_text()` composes core identity, summary, indicators, tags, and references for embeddings/search."

# Metrics
duration: 4 min
completed: 2026-02-14
---

# Phase 2 Plan 1: Unified Threat Normalization Summary

**A shared `UnifiedThreat` model with deterministic NVD/OTX/RSS normalization functions so collection agents produce one correlation-ready shape.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-14T06:46:51Z
- **Completed:** 2026-02-14T06:51:30Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Added `UnifiedThreat` and `ThreatIndicator` Pydantic models with required unified fields and `content_text()` helper.
- Added pure, deterministic normalizers for NVD CVEs, OTX indicators, and RSS items under a shared normalization package.
- Added representative tests that assert stable identity fields and searchable content across all three normalizers.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement UnifiedThreat model** - `d973dbd` (feat)
2. **Task 2: Create normalization helpers** - `2c553e9` (feat)
3. **Task 3: Add normalization tests with representative samples** - `7744ae8` (test)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/models/unified_threat.py` - Unified threat schema and searchable content helper.
- `src/agents/__init__.py` - Agent package initializer for clean imports in later plans.
- `src/integrations/__init__.py` - Integration package initializer for clean imports in later plans.
- `src/normalization/__init__.py` - Normalization package exports.
- `src/normalization/normalize.py` - Source-specific pure normalization functions to `UnifiedThreat`.
- `tests/test_normalization.py` - Stable normalization behavior coverage for NVD/OTX/RSS samples.

## Decisions Made
- Used one unified schema (`id/source/type/title/summary/time/severity/indicators/tags/references/raw`) for all collector outputs to remove per-source branching later.
- Kept normalizers side-effect free so storage and orchestration stay inside agent layers.
- Included source identity directly in normalized IDs so cross-source correlation can group while preserving provenance.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used project virtualenv for verification commands**
- **Found during:** Task 1 and Task 3 verification
- **Issue:** System `python3` in this workspace cannot import `src/` packages directly (`models`, `normalization`) without editable install context.
- **Fix:** Executed verification commands with `/tmp/delvn-venv/bin/python`, which has the project import path configured.
- **Files modified:** None (execution environment only)
- **Verification:** `/tmp/delvn-venv/bin/python -m pytest -q` passed (12 tests).
- **Committed in:** N/A (environment/runtime adjustment)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; deviation only affected command runtime environment.

## Issues Encountered
- System interpreter package resolution differs from project virtualenv; using `/tmp/delvn-venv/bin/python` unblocked verification without code changes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Unified normalization layer is ready for collector implementations in `02-02`, `02-03`, and `02-04`.
- Correlation phase can now assume a single threat shape across sources.

---
*Phase: 02-collection-agents*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/models/unified_threat.py`
- Verified file exists: `src/agents/__init__.py`
- Verified file exists: `src/integrations/__init__.py`
- Verified file exists: `src/normalization/__init__.py`
- Verified file exists: `src/normalization/normalize.py`
- Verified file exists: `tests/test_normalization.py`
- Verified file exists: `.planning/phases/02-collection-agents/02-01-SUMMARY.md`
- Verified commits exist: `d973dbd`, `2c553e9`, `7744ae8`
