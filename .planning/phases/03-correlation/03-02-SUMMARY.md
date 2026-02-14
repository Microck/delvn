---
phase: 03-correlation
plan: 02
subsystem: api
tags: [correlation, scoring, matcher, pydantic]

# Dependency graph
requires:
  - phase: 03-correlation
    provides: vector hit contract (`id`, `source`, `type`, `score`) and embedding-backed search pipeline
provides:
  - `CorrelationLink` model with deterministic IDs, bounded confidence, and explainable reasons
  - `score_correlation` confidence function weighted by similarity with shared-term boosts and same-source penalty
  - matcher that converts vector hits to scored correlation links using token + CVE + IOC overlap
affects: [03-correlation, 04-prioritization-reporting]

# Tech tracking
tech-stack:
  added: [no new dependencies]
  patterns: [explainable confidence scoring, regex-assisted shared-term extraction for candidate matching]

key-files:
  created: [src/models/correlation.py, src/correlation/__init__.py, src/correlation/scoring.py, src/correlation/matcher.py, tests/test_correlation_scoring.py, .planning/phases/03-correlation/03-02-SUMMARY.md]
  modified: [.planning/STATE.md]

key-decisions:
  - "Treat vector similarity as the primary confidence signal with capped shared-term boosts to keep scoring monotonic and explainable."
  - "Matcher computes overlap from available hit text plus explicit CVE/IOC extraction so links remain explainable even with minimal vector-hit payloads."

patterns-established:
  - "Correlation ID Pattern: derive deterministic IDs as `corr:{source_id}->{target_id}` for idempotent storage."
  - "Explainability Pattern: always emit score reasons and append concrete overlap evidence (CVE/IOC/token samples)."

# Metrics
duration: 5 min
completed: 2026-02-14
---

# Phase 3 Plan 2: Correlation Link Model and Matcher Summary

**Correlation candidates now convert vector similarity hits into deterministic, explainable `CorrelationLink` records with confidence scoring and overlap-based reasoning.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-14T07:17:04Z
- **Completed:** 2026-02-14T07:22:17Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Added a dedicated correlation model with deterministic IDs, bounded confidence, and optional raw similarity tracking.
- Implemented confidence scoring that prioritizes similarity, boosts shared terms, and lightly penalizes same-source matches.
- Implemented matcher logic that transforms vector hits into ranked `CorrelationLink` objects with token/CVE/IOC overlap evidence.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add correlation link model** - `b56ddcb` (feat)
2. **Task 2: Implement scoring + candidate matcher** - `3af8200` (feat)
3. **Task 3: Add tests for scoring behavior and reasons** - `7d1878f` (test)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/models/correlation.py` - Defines `CorrelationLink` and deterministic correlation-ID generation.
- `src/correlation/scoring.py` - Provides `score_correlation` with explainable confidence reasons and clamping.
- `src/correlation/matcher.py` - Converts vector hits into ranked `CorrelationLink` outputs using shared-term analysis.
- `src/correlation/__init__.py` - Exposes scoring and matcher entry points.
- `tests/test_correlation_scoring.py` - Covers monotonic scoring, shared-term reason boosts, and confidence clamping.

## Decisions Made
- Weighted confidence around similarity first (85%), with capped shared-term boosts and a same-source penalty to avoid over-linking same-feed items.
- Parsed overlap from both generic tokens and explicit CVE/IOC patterns so reasons remain useful even when vector hits are sparse.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required for this plan.

## Next Phase Readiness
- Correlator implementation can now consume `match_correlation_candidates` and persist deterministic `CorrelationLink` objects.
- Scoring behavior is regression-covered and ready for in-memory correlator smoke testing in 03-03.

---
*Phase: 03-correlation*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/models/correlation.py`
- Verified file exists: `src/correlation/__init__.py`
- Verified file exists: `src/correlation/scoring.py`
- Verified file exists: `src/correlation/matcher.py`
- Verified file exists: `tests/test_correlation_scoring.py`
- Verified file exists: `.planning/phases/03-correlation/03-02-SUMMARY.md`
- Verified commits exist: `b56ddcb`, `3af8200`, `7d1878f`
