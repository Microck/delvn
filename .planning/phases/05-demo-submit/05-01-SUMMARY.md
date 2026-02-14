---
phase: 05-demo-submit
plan: 01
subsystem: demo
tags: [demo, python, pipeline, yaml, reporting]

# Dependency graph
requires:
  - phase: 04-prioritization-reporting
    provides: agent entrypoints for prioritization and markdown reporting
provides:
  - demo config with stack and runtime parameters
  - single script entrypoint for collect -> correlate -> prioritize -> report
  - representative executive brief markdown for screenshots and README usage
affects: [05-02, 05-03, README, demo-video]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - dry-run default path with explicit --live gate for destructive actions
    - YAML-driven demo runtime parameters and stack profile

key-files:
  created:
    - demo/config.yaml
    - demo/run_demo.py
    - docs/example_brief.md
  modified: []

key-decisions:
  - "Require explicit --live plus Azure environment checks before running external calls or Azure writes."
  - "Default execution mode to --dry-run behavior for judge-safe and repeatable demos."

patterns-established:
  - "Demo runner creates temporary stack YAML from demo config and passes it to prioritizer/reporter."
  - "Demo summary output includes stage counts and top brief headlines for quick narration."

# Metrics
duration: 21 min
completed: 2026-02-14
---

# Phase 5 Plan 1: Demo Runner Assets Summary

**Single demo runner now orchestrates collectors through reporting with a non-destructive dry-run path and explicit live gating.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-02-14T19:12:05Z
- **Completed:** 2026-02-14T19:33:10Z
- **Tasks:** 4
- **Files modified:** 3

## Accomplishments
- Added a compact, on-screen-friendly demo config for Apache/PostgreSQL/React and key runtime knobs.
- Implemented `demo/run_demo.py` to run collect -> correlate -> prioritize -> report in live mode while keeping `--dry-run` non-destructive.
- Added `docs/example_brief.md` with realistic executive brief structure and content for demo and README screenshots.
- Verified `python3 demo/run_demo.py --dry-run` exits successfully and prints the full planned flow.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add demo config** - `bf25905` (feat)
2. **Task 2: Implement demo runner script** - `6213be3` (feat)
3. **Task 3: Generate sample executive brief markdown** - `27b3dea` (docs)
4. **Task 4: Verify dry-run execution** - `ef39d02` (chore)

**Plan metadata:** pending (created after SUMMARY/STATE updates because `commit_docs=true`)

## Files Created/Modified
- `demo/config.yaml` - Demo stack profile and pipeline runtime parameters.
- `demo/run_demo.py` - CLI runner with dry-run safety, live gate checks, and end-to-end orchestration.
- `docs/example_brief.md` - Representative executive brief output for submission artifacts.

## Decisions Made
- Live mode now requires both `--live` and required Azure environment variables before pipeline execution.
- Dry-run is the default behavior path so validation is safe in judging or no-credential environments.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] System pip install blocked by externally managed environment (PEP 668)**
- **Found during:** Task 1 (Add demo config)
- **Issue:** The plan's verification command `python3 -m pip install -e .` failed in this environment because system Python disallows global package installs.
- **Fix:** Switched verification install/check commands to the project virtual environment (`.venv/bin/python ...`) and continued execution.
- **Files modified:** None
- **Verification:** `.venv/bin/python -m pip install -e . && .venv/bin/python -c "import pathlib, yaml; yaml.safe_load(pathlib.Path('demo/config.yaml').read_text())"`
- **Committed in:** `bf25905` (task commit context)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope creep; adjustment was execution-environment only and did not alter deliverables.

## Authentication Gates

None.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration was required for this plan's deliverables.

## Next Phase Readiness

- Ready for `05-02-PLAN.md` with demo assets and safe runner now in place.
- No blockers carried forward.

## Self-Check: PASSED

- Verified required artifacts exist on disk.
- Verified task commit hashes exist in git history.

---
*Phase: 05-demo-submit*
*Completed: 2026-02-14*
