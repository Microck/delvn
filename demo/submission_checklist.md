# ThreatFusion Submission Checklist

Use this checklist to confirm consistency across submission artifacts before final packaging.

## 1) README consistency checks

- [ ] `README.md` quickstart commands run as written.
- [ ] README includes both safe and live demo paths:
  - `python3 demo/run_demo.py --dry-run`
  - `python3 demo/run_demo.py --live`
- [ ] README output references match real artifact paths.
- [ ] README architecture/source notes match current implementation scope.

Suggested local checks:

```bash
rg -n "run_demo.py|--dry-run|--live|docs/example_brief.md" README.md
```

## 2) Example brief consistency checks

- [ ] `docs/example_brief.md` exists.
- [ ] Brief structure is still aligned with current reporter output sections.
- [ ] Brief contains at least one correlation link example and one priority callout.
- [ ] Any screenshots/snippets used in submission match this file.

Suggested local checks:

```bash
test -f docs/example_brief.md
rg -n "Correlation|HIGH|Priority|Recommended" docs/example_brief.md
```

## 3) Demo runner contract checks

- [ ] `demo/run_demo.py` supports `--dry-run` (required for judging environments).
- [ ] Dry-run path is non-destructive and completes without external writes.
- [ ] Live path behavior is documented and gated clearly.

Suggested local checks:

```bash
python3 demo/run_demo.py --help | rg -- "--dry-run|--live"
python3 demo/run_demo.py --dry-run
```

## 4) Final demo video (DEMO-02)

- [ ] Hosted video URL: <paste link here>
- [ ] Confirm video duration is in the target 1:50-2:10 window.
- [ ] Confirm playback sanity: clear narration, no visible secrets, and full flow (config -> run -> brief evidence) is captured.
- [ ] Optional (if committing the binary): confirm `demo/video.mp4` exists and matches the hosted video.

Suggested local checks (optional):

```bash
# Optional local artifact check
test -f demo/video.mp4 || true

# Optional duration sanity (if ffprobe is available)
command -v ffprobe >/dev/null && ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 demo/video.mp4
```

## 5) Submission packaging checklist

- [ ] Include `README.md`.
- [ ] Include `docs/architecture.md`.
- [ ] Include `docs/example_brief.md`.
- [ ] Include `demo/config.yaml`.
- [ ] Include `demo/run_demo.py`.
- [ ] Include `demo/recording_checklist.md`.
- [ ] Include the hosted demo video URL in submission text (see section 4).
- [ ] Optional: if you choose to commit the binary, include `demo/video.mp4` (skip if size limits apply).
- [ ] Confirm all links and paths in submission text resolve correctly.
- [ ] Confirm no secrets, keys, or sensitive logs are packaged.

## 6) Final handoff sanity

- [ ] Repo state is consistent with what judges will run.
- [ ] Commands are copy-pasteable on a clean environment.
- [ ] Submission narrative matches the recorded flow.
