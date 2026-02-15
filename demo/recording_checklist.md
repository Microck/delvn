# ThreatFusion Demo Recording Checklist

Use this checklist to record a polished 2-minute end-to-end demo quickly and consistently.

## 1) Preflight (before recording)

- [ ] Open repo root in terminal and confirm working tree is clean enough for demo.
- [ ] Confirm `demo/config.yaml` is present and uses the demo stack (Apache, PostgreSQL, React).
- [ ] Confirm terminal font size is readable (at least 16px equivalent) and window width is comfortable.
- [ ] Close unrelated apps/tabs and hide notifications.
- [ ] Keep one editor tab ready for `docs/example_brief.md`.
- [ ] Decide run mode:
  - Safe mode for judging: `python3 demo/run_demo.py --dry-run`
  - Live mode (only if env is configured): `python3 demo/run_demo.py --live --config demo/config.yaml`

## 2) On-screen flow (target: ~2:00)

### 0:00-0:20 Intro and demo config

- [ ] State the goal: collect -> correlate -> prioritize -> report in one flow.
- [ ] Open `demo/config.yaml`.
- [ ] Highlight stack values: Apache, PostgreSQL, React.

### 0:20-0:55 Safe execution path

- [ ] Run: `python3 demo/run_demo.py --dry-run`.
- [ ] Call out that this path is non-destructive and judge-safe.

### 0:55-1:25 Live execution (optional)

- [ ] If environment is ready, run: `python3 demo/run_demo.py --live --config demo/config.yaml`.
- [ ] If not configured, explicitly state that dry-run is the default fallback.

### 1:25-1:50 Output walkthrough

- [ ] Open `docs/example_brief.md`.
- [ ] Highlight exactly one correlation link example.
- [ ] Highlight exactly one `HIGH` priority item and why it matters.

### 1:50-2:00 Closing

- [ ] Restate business value: fast signal triage with stack-aware prioritization.
- [ ] Mention that artifacts are reproducible from repo docs.

## 3) Export requirements

- [ ] Format: MP4
- [ ] Target duration: about 2:00 (acceptable range 1:50-2:10)
- [ ] Resolution: 1080p preferred (720p minimum)
- [ ] Audio: clear narration, no clipping
- [ ] Output file path (local): `demo/video.mp4` (optional to commit; hosted URL is fine for submission)

## 4) Final QA before upload

- [ ] Verify text is readable in full-screen playback.
- [ ] Verify commands and file paths are visible when spoken.
- [ ] Verify no secrets or private tokens appear on screen.
- [ ] Verify exported file opens successfully in a media player.
