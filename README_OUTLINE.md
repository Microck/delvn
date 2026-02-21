# README_OUTLINE (top-readme workflow)

ASSUMPTIONS I'M MAKING:
1. Apply mode is ON, so `README.md` will be modified ONLY inside a single `<!-- top-readme: begin -->` ... `<!-- top-readme: end -->` marker block.
2. The primary audience is hackathon judges + engineers running a safe demo locally.
3. This is an app/pipeline (not a reusable library), so Quickstart/Config/Output matter more than an API reference.
→ Correct me now or I'll proceed with these.

Target: `projects/threat-fusion`
Apply mode: ON

## Project Signals (detected)

- README: `README.md`
- Python: `pyproject.toml` (project name: `delvn`, requires Python `>=3.11`)
- Package manager/runtime: `uv` (lockfile: `uv.lock`)
- Demo entrypoint: `demo/run_demo.py`
- Demo config: `demo/config.yaml`
- Docs: `docs/architecture.md`, `docs/example_brief.md`
- License: `LICENSE` (Apache-2.0 per README)

## 1) Current README Headings (verbatim order)

- # Threat Fusion (Delvn)
- ## What You Get
- ## Installation
- ## Quick Start
- ## Usage
- ## Configure Your Stack Profile
- ## How It Works
- ## Configuration
- ## Documentation
- ## Output
- ## Security
- ## Contributing
- ## License

## 2) Recommended README Outline (top-starred repo pattern, specialized)

- # Threat Fusion (Delvn)
- ## What It Does
- ## Quickstart
- ## Installation
- ## Usage
- ## Configuration
- ### Stack Profile
- ### Environment Variables
- ## Output
- ## Architecture
- ## Development
- ## Testing
- ## Documentation
- ## Support
- ## Security
- ## Contributing
- ## License
- ## Releases
- ## Roadmap

## 3) Mapping: Current -> Recommended Section

| Current heading | Map to recommended |
| --- | --- |
| Threat Fusion (Delvn) | Threat Fusion (Delvn) |
| What You Get | What It Does |
| Installation | Installation |
| Quick Start | Quickstart |
| Usage | Usage |
| Configure Your Stack Profile | Configuration -> Stack Profile |
| How It Works | Architecture |
| Configuration | Configuration -> Environment Variables |
| Documentation | Documentation |
| Output | Output |
| Security | Security |
| Contributing | Contributing |
| License | License |

## 4) Missing / Weak Sections Checklist

- Development: marker block will add a heading; fill in formatter/linter/typecheck + repo layout.
- Testing: marker block will add a heading; add a skimmable test command + test selection.
- Support: marker block will add a heading; link to issue tracker/discussions (if applicable).
- Releases: marker block will add a heading; link to changelog or GitHub Releases (if applicable).
- Roadmap: marker block will add a heading; add 3-5 near-term bullets.

## 5) Apply Mode Plan (non-destructive)

- Insert a single `top-readme` marker block near the top of `README.md` (after the intro).
- Inside the marker block, add ONLY missing headings: Development, Testing, Support, Releases, Roadmap.
- Prefer links to existing files where possible (e.g., `pyproject.toml`, `tests/`).

## 6) Ready-to-Copy README Skeleton (tailored; placeholders ok)

```md
# Threat Fusion (Delvn)

Delvn is a multi-agent cyber threat intelligence (CTI) pipeline that turns noisy CVE, threat intel, and security news feeds into a prioritized executive brief tailored to your stack.

## What It Does

- Collects signals (CVE + intel + security news)
- Correlates related activity into a single narrative
- Prioritizes against your stack profile
- Generates an executive-ready markdown brief

## Quickstart

Prereqs:
- Python 3.11+
- uv

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

TODO:
- Add formatter/linter/typecheck commands (project uses ruff/mypy via `pyproject.toml`)
- Document repo layout and where the "agent" implementations live

## Testing

```bash
uv run pytest
```

## Documentation

- `docs/architecture.md`
- `docs/example_brief.md`

## Support

TODO: Link to issue tracker / discussions and add basic debugging info checklist.

## Security

`--live` uses real credentials and may write to Azure resources. Prefer `--dry-run` for evaluation.

## Contributing

Issues and pull requests are welcome.

## License

Apache-2.0 (see `LICENSE`).

## Releases

TODO: Point to releases/changelog (or state that this is a hackathon prototype).

## Roadmap

TODO: Add 3-5 bullets for near-term improvements.
```
