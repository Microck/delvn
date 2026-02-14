---
phase: 02-collection-agents
plan: 03
subsystem: api
tags: [otx, threat-intel, normalization, cosmos, python]

# Dependency graph
requires:
  - phase: 02-01
    provides: unified threat schema and `normalize_otx_indicator` used by the intel collector pipeline
provides:
  - OTX integration client for fetching recent indicator payloads
  - Intel agent pipeline that fetches, normalizes, and upserts unified threat docs
  - OTX normalization coverage for ip/domain/url indicator payloads
affects: [02-04, 03-correlation]

# Tech tracking
tech-stack:
  added: [no new dependencies]
  patterns: [optional API-key request headers, fetch-normalize-store collector flow]

key-files:
  created: [src/integrations/otx.py, src/agents/intel_agent.py, tests/test_otx_normalization.py, .planning/phases/02-collection-agents/02-03-SUMMARY.md]
  modified: [.planning/STATE.md]

key-decisions:
  - "Use OTX subscribed pulse feed with authenticated header support and a public-feed fallback when no API key is configured."
  - "Keep Intel agent batch-oriented with per-record error accounting while preserving normalized payload writes to Cosmos."

patterns-established:
  - "Collector Pipeline Pattern: integration fetcher returns raw-ish source payloads consumed by a pure normalizer before storage upsert."
  - "Stats Contract Pattern: collection entrypoints return `{fetched, normalized, stored, errors}` for run-level observability."

# Metrics
duration: 5 min
completed: 2026-02-14
---

# Phase 2 Plan 3: Intel Agent (OTX) Summary

**An OTX-backed Intel Agent that fetches recent indicators, normalizes them to `UnifiedThreat`, and upserts to Cosmos with deterministic batch stats.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-14T06:55:06Z
- **Completed:** 2026-02-14T07:00:22Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Added `fetch_recent_indicators(limit=50)` in the OTX integration layer using shared HTTP helpers and optional `X-OTX-API-KEY` auth.
- Added `run_intel_collection()` as the Intel Agent entrypoint with fetch -> normalize -> Cosmos upsert orchestration and stats output.
- Added OTX normalization tests for `ip`, `domain`, and `url` payloads asserting stable id prefixes and `{type, value}` indicator shape.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add OTX integration client** - `4844cdd` (feat)
2. **Task 2: Implement Intel Agent (collect -> normalize -> store)** - `c920963` (feat)
3. **Task 3: Add OTX normalization tests for indicator types** - `d13205a` (test)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/integrations/otx.py` - OTX feed client that emits raw-ish indicator payloads suitable for normalization.
- `src/agents/intel_agent.py` - Batch Intel collector that normalizes OTX indicators and writes unified threat docs to Cosmos.
- `tests/test_otx_normalization.py` - Coverage for ip/domain/url indicator normalization stability.

## Decisions Made
- Chose pulse-feed flattening in the integration client so downstream normalization sees simple indicator dictionaries.
- Kept collector storage failures non-fatal per item, counting errors while continuing the batch.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Switched verification commands to project virtualenv**
- **Found during:** Task 1, Task 2, Task 3 verification
- **Issue:** Workspace `python3` could not resolve `src/` packages (`integrations`, `agents`, `normalization`) during imports/tests.
- **Fix:** Re-ran all verification commands with `/tmp/delvn-venv/bin/python`.
- **Files modified:** None (execution environment only)
- **Verification:** `/tmp/delvn-venv/bin/python -m pytest -q` passed (20 tests).
- **Committed in:** N/A (runtime-only adjustment)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; only verification runtime path changed.

## Authentication Gates

None.

## Issues Encountered

- System interpreter import path did not include `src/`; using the project virtualenv resolved all import checks and test execution.

## User Setup Required

- Optional but recommended: set `OTX_API_KEY` to authenticate OTX requests and maximize indicator feed access.

## Next Phase Readiness

- OTX collection is now wired into the shared normalization/storage path expected by correlation.
- Ready for remaining collection plans and downstream correlation logic that depends on `UnifiedThreat` indicator records.

---
*Phase: 02-collection-agents*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/integrations/otx.py`
- Verified file exists: `src/agents/intel_agent.py`
- Verified file exists: `tests/test_otx_normalization.py`
- Verified file exists: `.planning/phases/02-collection-agents/02-03-SUMMARY.md`
- Verified commits exist: `4844cdd`, `c920963`, `d13205a`
