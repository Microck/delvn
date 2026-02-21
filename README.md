# Threat Fusion (Delvn)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Delvn is a multi-agent cyber threat intelligence (CTI) pipeline that turns noisy CVE, threat intel, and security news feeds into a prioritized executive brief tailored to your stack.

It is designed for triage: collect signals, correlate related activity, rank what matters, and generate a concise brief a human can act on.

Built for the Microsoft AI Dev Days Hackathon 2026.

<!-- top-readme: begin -->

## Development

- [`pyproject.toml`](pyproject.toml)

## Testing

- [`tests/`](tests/)

## Support

## Releases

## Roadmap

<!-- top-readme: end -->

## What You Get

- Multi-source collection (NVD CVEs, AlienVault OTX intel, security RSS)
- Correlation that links related activity into a single narrative
- Prioritization against a stack profile (products/platforms/keywords/exclude)
- Executive markdown brief output (easy to paste into tickets, email, docs)
- Optional Azure backing services (Cosmos DB + Azure AI Search)

## Installation

Prereqs:
- Python 3.11+
- `uv`

```bash
uv sync --frozen
```

## Quick Start

Run the judge-safe demo path (no external APIs and no Azure writes):

```bash
uv run python demo/run_demo.py --dry-run
```

Want to see what the final artifact looks like?

- Example brief: `docs/example_brief.md`

Run tests:

```bash
uv run pytest
```

## Usage

Live mode (requires Azure credentials):

```bash
uv run python demo/run_demo.py --live --config demo/config.yaml
```

## Configure Your Stack Profile

Edit `demo/config.yaml`:

- `stack.products`: primary technologies you run (used as the strongest signal)
- `stack.platforms`: environment keywords (e.g., Linux)
- `stack.keywords`: extra terms you want to boost
- `stack.exclude`: terms to down-rank

This config is intentionally small so you can tweak it during a demo.

## How It Works

1. Collect signals (CVE + intel + news) into a canonical `UnifiedThreat` record.
2. Correlate related items via embeddings + similarity search (hash-vector fallback keeps demos runnable without model creds).
3. Prioritize by relevance to your declared stack.
4. Generate an executive markdown brief.

## Configuration

Required env vars for `--live`:

- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `SEARCH_ENDPOINT`
- `SEARCH_KEY`

Optional env vars:

- `NVD_API_KEY` (higher NVD throughput)
- `OTX_API_KEY`
- `RSS_FEED_URLS` (comma-separated)
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

If Azure OpenAI embedding variables are not set, the correlator uses a deterministic hash embedding fallback so the pipeline stays runnable.

## Documentation

- Architecture: `docs/architecture.md`
- Example brief: `docs/example_brief.md`

## Output

- Generated live brief: `docs/demo_brief.md` (configured in `demo/config.yaml`)
- Demo runner entrypoint: `demo/run_demo.py`

## Security

`--live` uses real credentials and may write to Azure resources.
Prefer `--dry-run` when evaluating the pipeline.

## Contributing

Issues and pull requests are welcome.

## License

Apache-2.0 (see `LICENSE`).
