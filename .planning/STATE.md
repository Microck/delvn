# IntelMosaic - Project State

## Current Position

Phase: 3 of 5 (Correlation)
Plan: 2 of 3
Status: In progress
Last activity: 2026-02-14 - Completed 03-02-PLAN.md
Progress: █████████░░░░░░░ 56% (9/16 plans complete)

## Phase Status

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 1 | Foundation | Complete | 3/3 plans complete |
| 2 | Collection Agents | Complete | 4/4 plans complete |
| 3 | Correlation | In Progress | 2/3 plans complete |
| 4 | Prioritization & Reporting | Not Started | 0/3 plans complete |
| 5 | Demo & Submit | Not Started | 0/3 plans complete |

## Decisions

| Phase | Decision | Rationale |
|-------|----------|-----------|
| 01-01 | Use uppercase `Settings` fields mirroring env variable names | Keeps config contract explicit for later plans and runtime operators |
| 01-01 | Keep shared HTTP API minimal (`build_client`, `get_json`) | Avoids premature abstraction while centralizing defaults/retries |
| 01-01 | Verify with `/tmp/threat-fusion-venv` instead of system pip | Unblocks execution in a PEP 668 managed Python environment |
| 01-02 | Require `id/source/type/title/raw` in `ThreatBase` and keep enrichment fields optional | Enforces ingestion identity invariants without making collectors brittle |
| 01-02 | Constrain subtype `type` values with `Literal` and normalize `indicator_type` enum | Prevents cross-type payload drift before correlation and storage |
| 01-03 | Use `/source` as threats partition key and `/id` for correlations bootstrap | Simplifies threat writes while ensuring both containers are provisioned for downstream plans |
| 01-03 | Keep Cosmos/Search wrappers thin and settings-driven | Delivers required storage behavior without premature service abstractions |
| 01-03 | Make smoke runner skip-safe and env-gated | Allows local no-credential verification while enabling live cloud checks when configured |
| 02-01 | Introduce `UnifiedThreat` + `ThreatIndicator` as the single collector output schema | Ensures downstream correlation/prioritization can operate without source-specific branching |
| 02-01 | Use source-prefixed normalized IDs and pure normalization functions | Preserves source provenance and keeps normalization deterministic/testable |
| 02-02 | Keep NVD integration output minimal (`cve`, `published`, `lastModified`) | Reuses existing `normalize_nvd_cve` contract and avoids duplicating mapping logic |
| 02-02 | Return batch stats with per-record error accounting in CVE agent | Preserves ingestion progress while exposing normalization/storage failures |
| 02-03 | Use OTX pulse feed flattening to produce normalization-ready indicator payloads | Keeps collector output close to `normalize_otx_indicator` expectations while preserving pulse context |
| 02-03 | Keep Intel collection batch resilient with per-item error accounting | Allows partial progress during normalization/storage failures without aborting full runs |
| 02-04 | Keep a short built-in security feed list with `RSS_FEED_URLS` override | Allows source updates without code changes while preserving sane defaults |
| 02-04 | Derive RSS source labels from feed hostnames before normalization | Retains feed provenance in stored IDs while reusing unified RSS mapping |
| 03-01 | Default embeddings to deterministic hash fallback and only use Azure OpenAI when all embedding env vars are present | Keeps correlation development unblocked without cloud credentials while enabling live embeddings when configured |
| 03-01 | Return minimal vector hits (`id`, `source`, `type`, `score`) from SearchStore | Gives correlator a stable similarity contract without leaking storage-specific payload noise |
| 03-02 | Weight confidence primarily by vector similarity with capped shared-term boosts and same-source penalty | Preserves monotonic, explainable scoring while reducing self-correlation dominance |
| 03-02 | Build matcher overlap from token, CVE, and IOC extraction over available hit text fields | Produces concrete link reasons even when vector results contain sparse metadata |

## Blockers/Concerns Carried Forward

- None.

## Recent Activity

| Date | Activity |
|------|----------|
| 2026-02-14 | Completed 03-02 correlation link model + scoring + matcher + scoring tests |
| 2026-02-14 | Completed 03-01 embedding client abstraction + vector search indexing + embedding smoke tests |
| 2026-02-14 | Completed 02-03 OTX integration + Intel agent pipeline + normalization tests |
| 2026-02-14 | Completed 02-04 RSS integration + News agent pipeline + normalization tests |
| 2026-02-14 | Completed 02-02 NVD integration + CVE agent pipeline + parsing tests |
| 2026-02-14 | Completed 02-01 unified threat model + normalization layer + tests |
| 2026-02-14 | Completed 01-03 storage adapters + Azure smoke tooling |
| 2026-02-14 | Completed 01-02 threat data model and invariant tests |
| 2026-02-14 | Completed 01-01 foundation scaffold (settings + HTTP helpers + smoke test) |

## Session Continuity

- Last session: 2026-02-14T07:22:17Z
- Stopped at: Completed 03-02-PLAN.md
- Resume from: `.planning/phases/03-correlation/03-03-PLAN.md`

*Last updated: 2026-02-14*
