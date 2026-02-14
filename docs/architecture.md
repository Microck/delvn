# IntelMosaic Architecture

## Purpose

IntelMosaic is a batch-oriented, multi-agent cyber threat intelligence pipeline. It ingests signals from three source families, correlates related activity, prioritizes risk against a declared stack profile, and emits an executive markdown brief for security and leadership review.

## Components And Agent Roles

| Layer | Component | Responsibility | Primary Output |
| --- | --- | --- | --- |
| Ingestion | `cve_agent` | Pull recent CVEs from NVD, normalize vulnerability records | `UnifiedThreat` documents from NVD |
| Ingestion | `intel_agent` | Pull indicators from AlienVault OTX, normalize pulse/IOC data | `UnifiedThreat` documents from OTX |
| Ingestion | `news_agent` | Pull security RSS advisories and reports, normalize feed entries | `UnifiedThreat` documents from RSS |
| Correlation | `correlator_agent` | Embed threats, run vector similarity search, generate explainable links | `CorrelationLink` documents |
| Prioritization | `prioritizer_agent` | Score relevance against user stack (`products/platforms/keywords/exclude`) | Ranked threat list with relevance tiers |
| Reporting | `reporter_agent` | Convert ranked threats into executive-ready narrative entries | `ExecutiveBrief` payload + markdown |
| Orchestration | `demo/run_demo.py` | Run collect -> correlate -> prioritize -> report in one command | Console summary + markdown brief |

## End-To-End Flow

1. Collectors fetch source payloads and normalize them into `UnifiedThreat`.
2. Threats are upserted into Cosmos (`threats` container).
3. Correlator indexes threat text into Azure AI Search vectors.
4. Correlator queries nearest neighbors and emits `CorrelationLink` records.
5. Prioritizer loads stack config and scores each threat (`HIGH/MEDIUM/LOW/NONE`).
6. Reporter builds an `ExecutiveBrief` model from ranked entries.
7. Markdown renderer writes the final brief file (for demos: `docs/demo_brief.md`).

## Data Model Overview

### `UnifiedThreat`

Canonical cross-source threat object used throughout the pipeline.

- Identity: `id`, `source`, `type`
- Core context: `title`, `summary`, `published_at`, `observed_at`, `severity`
- Enrichment: `indicators[]`, `tags[]`, `references[]`
- Raw traceability: `raw` source payload

### `CorrelationLink`

Relationship object created by the correlator.

- Identity: `id` (`corr:{source_id}->{target_id}`)
- Endpoints: `source_id`, `target_id`
- Strength/context: `confidence`, optional `similarity`, `reasons[]`
- Audit field: `created_at`

### `ExecutiveBrief` (brief)

Structured output consumed by markdown rendering.

- `stack_summary`
- `top_risks[]` (`BriefEntry`)
- `notable_mentions[]` (`BriefEntry`)
- `generated_at`

## Storage And Indexing

### Azure Cosmos DB

- Database: `threat-fusion`
- Container: `threats` (partition key `/source`)
- Container: `correlations` (partition key `/id`)

### Azure AI Search

- Index: `threats`
- Key searchable fields: `id`, `source`, `type`, `published_at`, `content`
- Vector field: `contentVector` (default dimension: `EMBEDDING_DIM=1536`)
- Similarity engine: HNSW profile (`tf-vector-profile`)

## Failure Modes And Fallback Behavior

| Scenario | Current Behavior | Operational Impact |
| --- | --- | --- |
| Run without `--live` | `demo/run_demo.py` executes dry-run mode and performs no external calls/writes | Safe validation path for judges and local rehearsal |
| Missing live Azure env vars (`COSMOS_*`, `SEARCH_*`) | Runner blocks live execution and exits with explicit missing-variable list | Prevents partial destructive runs |
| Missing `NVD_API_KEY` | NVD requests run without API key | Lower anonymous quota, but pipeline remains functional |
| Missing `OTX_API_KEY` or OTX subscribed access denied | Integration falls back from subscribed endpoint to public pulses | Reduced intel depth, continued ingestion |
| API rate limiting/transient network issues (429/5xx/timeouts) | Shared HTTP client retries up to 5 attempts with exponential backoff | Improves resilience without custom retry logic per agent |
| Azure OpenAI embedding vars absent | Embedding client falls back to deterministic hash vectors | Correlation stays runnable in no-credential environments |
| Per-item normalization/storage errors | Agents increment error counters and continue processing remaining items | Partial progress preserved; failures surfaced in stage stats |
| Cosmos/Search unavailable during live run | Affected stage returns/raises errors and live run fails fast with context | No silent data loss; issue is visible immediately |

## Enterprise Value Story (How To Explain It)

IntelMosaic maps directly to a security operations workflow:

1. **Signal ingestion** from vulnerability, intel, and news channels.
2. **Correlation** to reduce isolated alert noise into linked threat narratives.
3. **Prioritization** by business-relevant stack footprint.
4. **Executive reporting** that turns technical findings into action-oriented outcomes.

This architecture is intentionally opinionated for demos: reproducible dry-runs, explicit live gates, and transparent failure accounting.
