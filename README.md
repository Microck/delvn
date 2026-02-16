# Delvn

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Delvn is a multi-agent cyber threat intelligence pipeline that turns noisy CVE, threat intel, and security news feeds into a prioritized executive brief tailored to your stack.

It is designed for triage: collect signals, correlate related activity, rank what matters, and generate a concise brief a human can act on.

## Features

- Multi-source collection (CVE, threat intel, security news)
- Correlation and prioritization based on a stack profile
- Markdown brief output for easy sharing
- Optional Azure integrations for storage and search

## Installation

Prereqs:
- Python 3.11+
- `uv`

```bash
uv sync --frozen
```

## Quick Start

Run the judge-safe demo path (no external writes):

```bash
uv run python demo/run_demo.py --dry-run
```

Run tests:

```bash
uv run pytest
```

## Usage

Live mode (requires Azure credentials):

```bash
uv run python demo/run_demo.py --live --config demo/config.yaml
```

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
