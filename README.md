<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/brand/logo-horizontal-dark.svg">
  <img alt="Delvn" src="docs/brand/logo-horizontal.svg" width="640">
</picture>

# Threat Fusion (Delvn)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Delvn is a multi-agent cyber threat intelligence (CTI) pipeline that turns noisy CVE, threat intel, and security news feeds into a prioritized executive brief tailored to your stack.

It is designed for triage: collect signals, correlate related activity, rank what matters, and generate a concise brief a human can act on.

Built for the Microsoft AI Dev Days Hackathon 2026.

## What It Does

- Collects signals (CVE + intel + security news)
- Correlates related items into a single narrative
- Prioritizes against your stack profile
- Generates an executive-ready markdown brief

## Quickstart

Prereqs:
- Python 3.11+
- `uv`

```bash
uv sync --frozen
uv run python demo/run_demo.py --dry-run
```

Example output:
- `docs/example_brief.md`

## Installation

```bash
uv sync --frozen
```

## Usage

Demo (judge-safe):

```bash
uv run python demo/run_demo.py --dry-run
```

Live mode (requires Azure credentials):

```bash
uv run python demo/run_demo.py --live --config demo/config.yaml
```

## Configuration

### Stack Profile

Edit `demo/config.yaml`:
- `stack.products`
- `stack.platforms`
- `stack.keywords`
- `stack.exclude`

### Environment Variables

Required for `--live`:
- `COSMOS_ENDPOINT`
- `COSMOS_KEY`
- `SEARCH_ENDPOINT`
- `SEARCH_KEY`

Optional:
- `NVD_API_KEY`
- `OTX_API_KEY`
- `RSS_FEED_URLS`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

## Output

- Generated brief: `docs/demo_brief.md` (set by `run.report_output_path` in `demo/config.yaml`)
- Demo entrypoint: `demo/run_demo.py`

## Architecture

- High-level design: `docs/architecture.md`

## Development

TODO: add formatter/linter/typecheck commands and repo layout pointers.

## Testing

```bash
uv run pytest
```

## Documentation

- `docs/architecture.md`
- `docs/example_brief.md`

## Support

TODO: add Issues/Discussions link and a debugging checklist.

## Security

`--live` uses real credentials and may write to Azure resources.
Prefer `--dry-run` for evaluation.

## Contributing

Issues and pull requests are welcome.

## License

Apache-2.0 (see `LICENSE`).

## Releases

TODO: link to releases/changelog (or state that this is a hackathon prototype).

## Roadmap

TODO: add 3-5 bullets for near-term improvements.
