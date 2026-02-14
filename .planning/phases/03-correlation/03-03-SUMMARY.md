---
phase: 03-correlation
plan: 03
subsystem: api
tags: [correlation, cosmos-db, azure-ai-search, smoke-test]

# Dependency graph
requires:
  - phase: 03-correlation
    provides: correlation model + matcher/scoring and vector indexing/query primitives
provides:
  - Cosmos correlation persistence/query helpers for correlator workflows
  - Correlator agent orchestration that loads threats, indexes vectors, searches neighbors, and stores links
  - In-memory correlator smoke coverage proving matcher/scoring pipeline without live Azure
affects: [03-correlation, 04-prioritization-reporting]

# Tech tracking
tech-stack:
  added: [no new dependencies]
  patterns: [two-pass recency selection with _ts fallback, dependency-injected agent orchestration for offline verification]

key-files:
  created: [src/agents/correlator_agent.py, tests/test_correlator_smoke.py, .planning/phases/03-correlation/03-03-SUMMARY.md]
  modified: [src/storage/cosmos.py, .planning/STATE.md]

key-decisions:
  - "Prefer time-field recency queries (`observed_at`/`published_at`) with `_ts` fallback so mixed threat documents are still retrievable."
  - "Keep `run_correlation` resilient with per-threat error accounting and injectable stores to enable deterministic local smoke tests."

patterns-established:
  - "Correlator Loop Pattern: index batch once, then embed/query each threat and persist matcher-produced links with aggregate stats."
  - "Storage Helper Pattern: keep Cosmos read/write methods thin and idempotent around deterministic correlation IDs."

# Metrics
duration: 4 min
completed: 2026-02-14
---

# Phase 3 Plan 3: Correlator Agent Wiring Summary

**Correlator execution now reads recent threats, performs vector-neighbor matching, and persists scored `CorrelationLink` records through Cosmos storage helpers.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-14T07:25:09Z
- **Completed:** 2026-02-14T07:30:01Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Extended `CosmosStore` with correlation-specific upsert and query helpers needed by downstream reporting.
- Implemented `run_correlation()` to orchestrate threat loading, vector indexing/search, matcher conversion, and correlation persistence with stats.
- Added an in-memory smoke test proving matcher/scoring integration without calling live Azure services.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend Cosmos store with correlation upsert/query helpers** - `73f3af3` (feat)
2. **Task 2: Implement Correlator Agent (read -> index -> search -> link -> store)** - `1105fa5` (feat)
3. **Task 3: Add correlator smoke test (no live Azure calls)** - `52ba767` (test)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/storage/cosmos.py` - Adds `upsert_correlation`, `list_recent_threats`, and `list_correlations_for_threat` APIs.
- `src/agents/correlator_agent.py` - Adds `run_correlation()` batch orchestration and stats reporting.
- `tests/test_correlator_smoke.py` - Adds an offline, in-memory end-to-end smoke check for correlator flow.

## Decisions Made
- Ranked recent threats using available threat timestamps first (`observed_at`, then `published_at`) with `_ts` fallback to keep retrieval useful across mixed source payloads.
- Added optional store injection to `run_correlation` so orchestration can be exercised in tests without cloud credentials or live Azure resources.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- System `python3` environment did not resolve project modules (`ModuleNotFoundError: storage`), so verification used `/tmp/delvn-venv/bin/python` as instructed by execution context.

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required for this plan.

## Next Phase Readiness
- Correlation links are now persisted/queryable, enabling prioritization to consume historical link context.
- `run_correlation` returns operational stats (`threats_indexed`, `queries`, `links_created`, `stored`, `errors`) suitable for phase-4 reporting hooks.

---
*Phase: 03-correlation*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/storage/cosmos.py`
- Verified file exists: `src/agents/correlator_agent.py`
- Verified file exists: `tests/test_correlator_smoke.py`
- Verified file exists: `.planning/phases/03-correlation/03-03-SUMMARY.md`
- Verified commits exist: `73f3af3`, `1105fa5`, `52ba767`
