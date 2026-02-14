---
phase: 02-collection-agents
plan: 04
subsystem: api
tags: [rss, feedparser, normalization, cosmos, threat-intel]

# Dependency graph
requires:
  - phase: 02-collection-agents
    provides: unified threat schema and `normalize_rss_item` used by the news collector
provides:
  - RSS integration client that parses feed entries into raw item payloads
  - News collection agent that fetches, normalizes, and stores RSS threats
  - RSS normalization regression tests for ID prefix and searchable content text
affects: [03-correlation, 04-prioritization-reporting]

# Tech tracking
tech-stack:
  added: [no new dependencies]
  patterns: [environment-driven feed overrides, per-item ingestion stats with resilient error counting]

key-files:
  created: [src/integrations/rss.py, src/agents/news_agent.py, tests/test_rss_normalization.py, .planning/phases/02-collection-agents/02-04-SUMMARY.md]
  modified: [.planning/STATE.md]

key-decisions:
  - "Keep a short built-in feed list and allow `RSS_FEED_URLS` override so operators can change sources without code edits."
  - "Derive RSS source IDs from feed URL hostnames to preserve provenance while reusing unified normalization."

patterns-established:
  - "Collector Pattern: fetch raw integration payloads, normalize to `UnifiedThreat`, then upsert with consistent stats accounting."
  - "RSS Payload Pattern: retain raw title/link/summary/published keys and optional metadata (`guid`, `tags`, `links`) for normalization flexibility."

# Metrics
duration: 3 min
completed: 2026-02-14
---

# Phase 2 Plan 4: News Agent RSS Collection Summary

**RSS-powered news ingestion now fetches security feeds, normalizes entries into `UnifiedThreat`, and stores them in Cosmos with collection stats.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-14T06:54:55Z
- **Completed:** 2026-02-14T06:58:53Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Added a defensive RSS integration client using `feedparser` with tolerant handling of missing entry fields.
- Added a News Agent entrypoint (`run_news_collection`) with default security feeds, `RSS_FEED_URLS` override, normalization, and Cosmos upsert flow.
- Added RSS normalization tests covering stable `rss:` ID prefix behavior and `content_text()` composition.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add RSS integration client** - `0e71f94` (feat)
2. **Task 2: Implement News Agent (collect -> normalize -> store)** - `689b134` (feat)
3. **Task 3: Add RSS normalization tests** - `1b031a7` (test)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/integrations/rss.py` - RSS fetch/parsing helper returning raw-ish feed entries for normalization.
- `src/agents/news_agent.py` - News collection pipeline with feed selection, normalization, Cosmos upsert, and stats.
- `tests/test_rss_normalization.py` - Regression tests for RSS ID prefix and searchable content composition.

## Decisions Made
- Used a short default feed list and an env override (`RSS_FEED_URLS`) to keep source selection operationally configurable.
- Mapped feed source provenance from URL hostnames so normalized IDs reflect origin feed context.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used project virtualenv for verification commands**
- **Found during:** Task 1, Task 2, and Task 3 verification
- **Issue:** Workspace `python3` cannot resolve project packages (`integrations`, `agents`, `normalization`) without the project environment.
- **Fix:** Re-ran required verification commands using `/tmp/threat-fusion-venv/bin/python`.
- **Files modified:** None (execution environment only)
- **Verification:** Import checks and `/tmp/threat-fusion-venv/bin/python -m pytest -q` passed (17 tests).
- **Committed in:** N/A (runtime verification adjustment)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; deviation was only verification environment routing.

## Issues Encountered
- System interpreter package resolution differs from the project venv; using `/tmp/threat-fusion-venv` unblocked plan verification.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Collection layer now includes RSS as the third source with unified normalization output.
- Correlation/prioritization phases can consume stored RSS-derived `UnifiedThreat` documents alongside CVE and indicator data.

---
*Phase: 02-collection-agents*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/integrations/rss.py`
- Verified file exists: `src/agents/news_agent.py`
- Verified file exists: `tests/test_rss_normalization.py`
- Verified file exists: `.planning/phases/02-collection-agents/02-04-SUMMARY.md`
- Verified commits exist: `0e71f94`, `689b134`, `1b031a7`
