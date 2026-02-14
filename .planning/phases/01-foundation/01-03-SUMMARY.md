---
phase: 01-foundation
plan: 03
subsystem: database
tags: [azure-cosmos, azure-search, azure-openai, smoke-tests, storage]

# Dependency graph
requires:
  - phase: 01-01
    provides: typed settings and Python package scaffold used by storage wrappers
provides:
  - Cosmos DB storage wrapper for threat CRUD and container bootstrap
  - Azure AI Search wrapper with index bootstrap for text + vector fields
  - Skip-safe Azure smoke script for Cosmos/Search/Foundry checks
  - Foundry infra placeholder config tracked in repo
affects: [01-02, 02-collection-agents, 03-correlation]

# Tech tracking
tech-stack:
  added: [azure-cosmos usage, azure-search-documents usage, httpx embedding smoke request]
  patterns: [settings-driven storage clients, bootstrap-on-demand containers/index, env-gated smoke execution]

key-files:
  created: [src/storage/__init__.py, src/storage/cosmos.py, src/storage/search.py, scripts/smoke_azure_storage.py, infra/foundry_config.yaml, tests/test_storage_clients_smoke.py, .planning/phases/01-foundation/01-03-SUMMARY.md]
  modified: [src/storage/__init__.py]

key-decisions:
  - "Use `/source` partition key for threats and `/id` for correlations to keep threat writes simple while allowing correlation bootstrap."
  - "Keep wrappers thin and settings-driven (no framework abstraction) so agents can call storage APIs directly."
  - "Make smoke runner skip-safe when env vars are absent and only execute live calls when credentials are provided."

patterns-established:
  - "Storage Pattern: wrapper classes own ensure/bootstrap + CRUD/search helpers with explicit required env checks."
  - "Smoke Pattern: runtime environment gates for optional cloud checks while preserving zero-failure local execution."

# Metrics
duration: 6 min
completed: 2026-02-14
---

# Phase 1 Plan 3: Azure Storage Adapters Summary

**Cosmos threat persistence and Azure AI Search index/bootstrap wrappers with an optional live smoke runner for Cosmos/Search/Foundry connectivity.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-02-14T06:28:45Z
- **Completed:** 2026-02-14T06:35:32Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Added `CosmosStore` with container bootstrap, required threat shape validation, and upsert/read helpers.
- Added `SearchStore` with index bootstrap (text + vector schema), document upsert, and basic text search.
- Added `infra/foundry_config.yaml`, import-only storage smoke test, and a non-destructive smoke runner for live Azure checks.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement Cosmos DB threat store wrapper** - `b73e3a4` (feat)
2. **Task 2: Implement Azure AI Search wrapper with index bootstrap** - `0a123f8` (feat)
3. **Task 3: Add infra placeholders + optional live smoke script + import-only smoke tests** - `90b3440` (feat)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/storage/__init__.py` - Storage package export for Cosmos wrapper.
- `src/storage/cosmos.py` - Cosmos DB wrapper with ensure/bootstrap and threat CRUD helpers.
- `src/storage/search.py` - Search wrapper with vector-capable index definition and text query helper.
- `infra/foundry_config.yaml` - Placeholder Azure resource naming config for infra/foundry setup.
- `scripts/smoke_azure_storage.py` - Skip-safe smoke runner for Cosmos/Search and optional OpenAI embeddings.
- `tests/test_storage_clients_smoke.py` - Import-only smoke coverage for storage client modules.

## Decisions Made
- Kept both storage wrappers intentionally small and direct to match plan constraints and avoid premature abstraction.
- Used HNSW vector search profile and `contentVector` field at bootstrap time so Phase 3 can add vector queries without index redesign.
- Added retry polling in search smoke verification to absorb indexing latency before asserting query visibility.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used project virtualenv for verification commands**
- **Found during:** Task 1/Task 3 verification
- **Issue:** System `python3` in this workspace cannot import `src/` packages directly (`storage`, `models`) without editable install.
- **Fix:** Ran verification commands using `/tmp/threat-fusion-venv/bin/python` where editable install is already configured.
- **Files modified:** None (execution environment only)
- **Verification:** `/tmp/threat-fusion-venv/bin/python -m pytest -q` passed (9 tests).
- **Committed in:** N/A (environment/runtime adjustment)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change; deviation only affected how verification commands were executed.

## Issues Encountered
- `python3 -m pytest -q` fails in system interpreter due import path/package resolution in this managed environment; project virtualenv verification passed and was used consistently.

## User Setup Required

External Azure credentials are needed for live smoke checks:
- `COSMOS_ENDPOINT`, `COSMOS_KEY`
- `SEARCH_ENDPOINT`, `SEARCH_KEY`
- Optional embeddings check: `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`

## Next Phase Readiness
- Storage adapters and smoke harness are ready for downstream agents.
- Foundation phase is complete (plans 01-01, 01-02, and 01-03).
- Ready to start `.planning/phases/02-collection-agents/02-01-PLAN.md`.

---
*Phase: 01-foundation*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/storage/cosmos.py`
- Verified file exists: `src/storage/search.py`
- Verified file exists: `infra/foundry_config.yaml`
- Verified file exists: `scripts/smoke_azure_storage.py`
- Verified file exists: `tests/test_storage_clients_smoke.py`
- Verified file exists: `.planning/phases/01-foundation/01-03-SUMMARY.md`
- Verified commits exist: `b73e3a4`, `0a123f8`, `90b3440`
