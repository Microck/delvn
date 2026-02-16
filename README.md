# Delvn

Delvn is a multi-agent cyber threat intelligence pipeline that turns noisy CVE, threat intel, and security news feeds into a prioritized executive brief tailored to your stack.

Built for: Microsoft AI Dev Days Hackathon 2026
Categories: Best Enterprise Solution, Best Multi-Agent System
Demo video: <paste hosted link>

## Quickstart

Judge-safe (no Azure writes):

```bash
uv sync --frozen
uv run python demo/run_demo.py --dry-run
uv run pytest
```

Live mode (requires Azure credentials):

```bash
uv run python demo/run_demo.py --live --config demo/config.yaml
```

## Why This Matters

- Reduces alert fatigue by filtering threat data against your actual stack.
- Connects isolated signals (CVE, IOC, campaign/news) into explainable links.
- Produces a demo-ready brief without custom dashboards.

## Architecture At A Glance

```text
NVD API + OTX + RSS -> collector agents -> UnifiedThreat
  -> (optional) Cosmos + AI Search -> correlator -> links
  -> prioritizer (stack YAML) -> reporter -> markdown brief
```

For deeper component details, see `docs/architecture.md`.

## Prerequisites

- Python 3.11+
- `uv` (reproducible installs via `uv.lock`)

Required env vars for `--live`:

- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `SEARCH_ENDPOINT`
- `SEARCH_KEY`

Optional env vars:

- `NVD_API_KEY` (higher NVD throughput)
- `OTX_API_KEY` (subscribed OTX pulses)
- `RSS_FEED_URLS` (comma-separated feed override)
- Azure OpenAI embedding vars (optional)

If embedding variables are not set, the correlator uses a deterministic hash embedding fallback so the pipeline stays runnable.

## Data Sources And Scope Notes

Sources:

- NVD CVE API
- AlienVault OTX
- RSS security feeds

Scope constraints for v1:

- Batch workflow (not real-time alerting)
- No SIEM integration
- Three source families only
- Informational prioritization/reporting (no automated blocking)

## Output Paths

- Generated live brief: `docs/demo_brief.md` (configured in `demo/config.yaml`)
- Committed sample brief for judges: `docs/example_brief.md`
- Demo runner entrypoint: `demo/run_demo.py`

## Verification

```bash
uv run pytest
```

## Safety

- Prefer `--dry-run` when judging.
- `--live` uses real credentials and may write to Azure resources.

## License

Apache-2.0 (see `LICENSE`).
