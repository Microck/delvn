---
phase: 03-correlation
plan: 01
subsystem: database
tags: [embeddings, azure-ai-search, vector-search, deterministic-fallback]

# Dependency graph
requires:
  - phase: 02-collection-agents
    provides: normalized `UnifiedThreat` documents with `content_text()` used for embedding/indexing
provides:
  - embedding client abstraction with deterministic hash fallback and optional Azure OpenAI integration
  - vector-ready SearchStore indexing via `index_threats` and nearest-neighbor retrieval via `vector_query`
  - smoke tests that lock embedding dimension and deterministic fallback behavior
affects: [03-correlation, 04-prioritization-reporting]

# Tech tracking
tech-stack:
  added: [no new dependencies]
  patterns: [settings-based embedding client selection, unified threat text to vector indexing pipeline]

key-files:
  created: [src/embeddings/__init__.py, src/embeddings/client.py, tests/test_embeddings_smoke.py, .planning/phases/03-correlation/03-01-SUMMARY.md]
  modified: [src/storage/search.py, .planning/STATE.md]

key-decisions:
  - "Default to deterministic hash embeddings and only use Azure OpenAI when all embedding env vars are present."
  - "Keep vector search results small and stable with `{id, source, type, score}` for direct correlator consumption."

patterns-established:
  - "Embedding Client Pattern: one `get_embedding_client()` selector chooses runtime implementation from settings."
  - "Vector Index Pattern: derive `content` from `UnifiedThreat.content_text()`, embed once, and upsert with `contentVector`."

# Metrics
duration: 5 min
completed: 2026-02-14
---

# Phase 3 Plan 1: Embedding and Vector Search Foundations Summary

**Embedding primitives now support deterministic local vectors and vector-ready Azure Search indexing so correlation can run even without Azure model credentials.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-14T07:08:52Z
- **Completed:** 2026-02-14T07:13:53Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Added `embeddings.client` with a protocol, deterministic hash embedding fallback, optional Azure OpenAI embedding client, and centralized selection logic.
- Extended `SearchStore` with threat vector indexing (`index_threats`) and nearest-neighbor retrieval (`vector_query`) while preserving existing Cosmos behavior.
- Added embedding smoke tests validating deterministic output and expected embedding dimensions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement EmbeddingClient with fallback hashing embeddings** - `85760d4` (feat)
2. **Task 2: Update SearchStore to upsert vectorized threat docs** - `7e16b96` (feat)
3. **Task 3: Add embedding smoke tests** - `4fd155c` (test)

**Plan metadata:** pending docs commit

## Files Created/Modified
- `src/embeddings/client.py` - Embedding client protocol plus deterministic and optional Azure implementations.
- `src/embeddings/__init__.py` - Embedding module exports for shared import surface.
- `src/storage/search.py` - Vector-aware threat indexing and similarity query APIs for correlation.
- `tests/test_embeddings_smoke.py` - Regression coverage for deterministic fallback and embedding dimensionality.

## Decisions Made
- Used deterministic hash embeddings as the default so correlation development and tests do not depend on cloud credentials.
- Kept vector query output minimal (`id`, `source`, `type`, `score`) to make downstream correlator logic straightforward.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required for this plan.

## Next Phase Readiness
- Correlator implementation can now embed normalized threats and fetch nearest-neighbor candidates through `SearchStore.vector_query`.
- Azure-backed embeddings can be enabled later by setting `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`.

---
*Phase: 03-correlation*
*Completed: 2026-02-14*

## Self-Check: PASSED

- Verified file exists: `src/embeddings/__init__.py`
- Verified file exists: `src/embeddings/client.py`
- Verified file exists: `src/storage/search.py`
- Verified file exists: `tests/test_embeddings_smoke.py`
- Verified file exists: `.planning/phases/03-correlation/03-01-SUMMARY.md`
- Verified commits exist: `85760d4`, `7e16b96`, `4fd155c`
