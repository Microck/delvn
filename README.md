# IntelMosaic (Threat Fusion)

IntelMosaic is a multi-agent cyber threat intelligence pipeline that turns noisy CVE, threat intel, and security news feeds into a prioritized executive brief tailored to your stack. It is designed for fast enterprise triage: collect signals, correlate related activity, rank what matters, and generate a concise brief leadership can act on.

## Why This Matters

- Reduces alert fatigue by filtering threat data against your actual stack.
- Connects isolated signals (CVE, IOC, campaign/news) into explainable links.
- Produces a demo-ready brief (`docs/demo_brief.md`) without custom dashboards.

## Architecture At A Glance

```text
NVD API           AlienVault OTX           Security RSS Feeds
   |                   |                          |
   +-------------------+--------------------------+
                           |
                 Collector Agents (CVE/Intel/News)
                           |
                     UnifiedThreat records
                           |
      +-----------------------------------------------+
      | Azure Cosmos DB (threats container)           |
      | Azure AI Search (vector index: threats)       |
      +-----------------------------------------------+
                           |
                     Correlator Agent
                           |
                 CorrelationLink records
                           |
      +-----------------------------------------------+
      | Azure Cosmos DB (correlations container)      |
      +-----------------------------------------------+
                           |
        Prioritizer Agent (uses stack profile from YAML)
                           |
                      Reporter Agent
                           |
           Markdown brief output + narration summary
```

For deeper component details, see `docs/architecture.md`.

## Prerequisites

- Python 3.11+
- A virtual environment tool (`venv` is used below)
- Azure resources for live mode:
  - Azure Cosmos DB endpoint + key
  - Azure AI Search endpoint + key

Required environment variables for `--live`:

- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `SEARCH_ENDPOINT`
- `SEARCH_KEY`

Optional environment variables:

- `NVD_API_KEY` (higher NVD throughput)
- `OTX_API_KEY` (subscribed OTX pulses)
- `RSS_FEED_URLS` (comma-separated feed override)
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

If Azure OpenAI embedding variables are not set, the correlator uses a deterministic hash embedding fallback so the pipeline stays runnable.

## Quickstart

1. Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

2. Create or update `.env` with your live credentials.

```env
COSMOS_ENDPOINT=https://<your-cosmos-account>.documents.azure.com:443/
COSMOS_KEY=<your-cosmos-key>
SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
SEARCH_KEY=<your-search-key>

# Optional
NVD_API_KEY=<optional>
OTX_API_KEY=<optional>
```

3. Validate pipeline orchestration safely (no external calls, no Azure writes).

```bash
python demo/run_demo.py --dry-run
```

4. Run the live pipeline (collect -> correlate -> prioritize -> report).

```bash
python demo/run_demo.py --live --config demo/config.yaml
```

## Data Sources And Scope Notes

- **NVD CVE API:** Vulnerability records and metadata.
- **AlienVault OTX:** Indicators and pulse context (falls back to public pulses when no API key is available).
- **RSS Security Feeds:** Defaults include BleepingComputer, The Hacker News, and CISA advisories.

Scope constraints for this demo:

- Batch workflow (not real-time alerting)
- No SIEM integration in v1
- Three source families only (NVD, OTX, RSS)
- Informational prioritization/reporting, not automated blocking

## Output Paths

- Generated live brief: `docs/demo_brief.md` (configured in `demo/config.yaml`)
- Committed sample brief for judges: `docs/example_brief.md`
- Demo runner entrypoint: `demo/run_demo.py`
