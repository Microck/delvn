# Delvn (Threat Fusion) - Test & Smoke Checklist

Goal: run the exact checks needed before recording the submission video and submitting.

## 0) Repo sanity

```bash
cd projects/delvn
git status --porcelain
```

Expected: no output.

## 1) Install deps (uv)

```bash
cd projects/delvn
uv sync --frozen
```

## 2) Automated tests

```bash
cd projects/delvn
uv run pytest -q
```

## 3) Demo smoke (judge-safe dry-run)

```bash
cd projects/delvn
uv run python demo/run_demo.py --dry-run
```

Expected: completes without external writes/calls and produces a brief artifact.

## 4) Optional: live run (writes to Azure)

Only do this if you intentionally want to exercise live Cosmos/Search.

```bash
cd projects/delvn

export COSMOS_ENDPOINT=...
export COSMOS_KEY=...
export SEARCH_ENDPOINT=...
export SEARCH_KEY=...

uv run python demo/run_demo.py --live --config demo/config.yaml
```

## 5) Submission artifacts

- README: `README.md`
- Architecture diagram: `docs/architecture.svg` (source: `docs/architecture.mmd`)
- Detailed architecture write-up: `docs/architecture.md`
- Example output: `docs/example_brief.md`
- Submission checklist: `demo/submission_checklist.md`
- Recording checklist: `demo/recording_checklist.md`
- Optional local video artifact: `demo/video.mp4`
