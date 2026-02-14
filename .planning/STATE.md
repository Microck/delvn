# IntelMosaic - Project State

## Current Position

Phase: 5 of 5 (Demo & Submit)
Plan: 2 of 3
Status: In progress
Last activity: 2026-02-14 - Completed 05-02-PLAN.md
Progress: ███████████████░ 94% (15/16 plans complete)

## Phase Status

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 1 | Foundation | Complete | 3/3 plans complete |
| 2 | Collection Agents | Complete | 4/4 plans complete |
| 3 | Correlation | Complete | 3/3 plans complete |
| 4 | Prioritization & Reporting | Complete | 3/3 plans complete |
| 5 | Demo & Submit | In progress | 2/3 plans complete |

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
| 03-03 | Query recent threats by available business timestamps (`observed_at`/`published_at`) with `_ts` fallback | Keeps correlator retrieval robust across mixed-source threat documents |
| 03-03 | Allow `run_correlation` dependency injection for Cosmos/Search stores | Enables deterministic in-memory smoke validation without requiring live Azure connectivity |
| 04-01 | Preserve first-seen stack value casing while deduping case-insensitively | Keeps user-facing config display intact while matching remains normalized and deterministic |
| 04-01 | Default missing user stack sections to empty lists | Allows partial YAML configs to load into a typed object without caller-side fallbacks |
| 04-02 | Use product keywords as strong relevance signals and weak stack terms as fallback | Keeps prioritization explainable while reducing false-positive HIGH scores |
| 04-02 | Return prioritizer output as structured ranked data (not report prose) | Preserves separation between prioritization logic and reporting generation in next plan |
| 04-03 | Keep `run_reporting()` deterministic and accept optional precomputed prioritization output | Supports reproducible demos/tests without requiring live Cosmos dependencies |
| 04-03 | Split reporting into model, renderer, and agent orchestration layers | Keeps formatting logic reusable and isolates orchestration from presentation concerns |
| 05-01 | Require explicit `--live` plus Azure env checks before running collectors/stores | Prevents destructive demo runs and avoids accidental external calls in judging environments |
| 05-01 | Default demo execution path to dry-run behavior | Keeps demo rehearsals repeatable and safe when credentials are unavailable |
| 05-02 | Lead README setup with dry-run first and explicit live step | Minimizes judge friction while preserving safe, repeatable execution by default |
| 05-02 | Document architecture with agent-role mapping and fallback matrix | Makes enterprise value and resiliency story explicit for reviewers |

## Blockers/Concerns Carried Forward

- None.

## Recent Activity

| Date | Activity |
|------|----------|
| 2026-02-14 | Completed 05-02 judge-facing README + architecture reference docs |
| 2026-02-14 | Completed 05-01 demo config + safe runner + sample brief + dry-run verification |
| 2026-02-14 | Completed 04-03 reporter agent + markdown renderer + brief rendering tests |
| 2026-02-14 | Completed 04-02 prioritizer agent orchestration + stack relevance scoring + prioritization tests |
| 2026-02-14 | Completed 04-01 user stack YAML config + typed loader + normalization tests |
| 2026-02-14 | Completed 03-03 correlator agent orchestration + Cosmos correlation helpers + in-memory correlator smoke test |
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

- Last session: 2026-02-14T19:40:41Z
- Stopped at: Completed 05-02-PLAN.md
- Resume from: `.planning/phases/05-demo-submit/05-03-PLAN.md`

*Last updated: 2026-02-14*
