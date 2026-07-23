# HANDOFF — RACE-GUI (feat/race-gui)

## Status: race is a real in-GUI act; capture kit generalized to all five videos

The race is no longer a still-only benchmark — it is a routed mission with a
live split-screen race view, both paths real and timed, and a finish card that
shows only THIS run's measured numbers. The motorBike capture script is now a
five-video kit.

## What shipped

### Part 1 — the race as an in-GUI act

- **`sdk/workflows/race_study.py`** — routed mission wrapping the
  `race_benchmark` machinery (same NACA 4412 wing, same solver, same math).
  Two lanes run CONCURRENTLY:
  - LEFT full Monte-Carlo: `RACE_MC_SAMPLES` Reynolds samples × 11 alphas, every
    point a direct VSPAERO solve (no interpolation).
  - RIGHT reduced-order: 4 real anchors → fitted quadratic surface → 1 real
    confirmation solve. Same objective, same ±0.5° tolerance.
  - **Compute treaty:** four-slot cap, split evenly two-per-lane
    (`MC_WORKERS=2`, `ROM_WORKERS=2`), each lane on its own reserved pool. The
    even split is what makes the race deterministic — the reduced-order lane
    wins on solve count alone, never because it was handed more of the box. When
    a lane finishes, its slots fall idle (total in flight only ever drops).
  - Emits `race.init`, per-lane `trace.point` (series `mc`/`rom`), `race.lane`
    (done/total/elapsed_s/state), `race.curve` (fitted surface), `race.result`
    (measured speedup + agreement), plus `result.verdict`, `agenda.updated`,
    `report.ready` and the full chief transcript.
- **Router** (`sdk/chief_engineer/router.py`) — new `race-comparison` intent.
  Fires on a contest frame (race / head-to-head / versus / "against the
  reduced-order" / "both timed" / "measured speedup") reinforced by the method
  pair (Monte-Carlo + reduced-order/surrogate). Registered to
  `workflows.race_study`. Guarded so a plain Monte-Carlo UQ request does NOT
  hijack the race route (test-enforced).
- **GUI** (`sdk/chief_engineer/control_room.html`) — split-screen race view.
  On `race.init` the centre stage becomes two lanes (FULL MONTE-CARLO |
  REDUCED-ORDER), each with its own growing L/D-vs-α polar (nominal-Reynolds
  line for MC; anchors + fitted surface + ringed confirmation for ROM), a
  solves-done/total progress bar, a live ticking elapsed clock, and a FINISHED
  flag. The finish card shows measured core-minutes both lanes, wall times, the
  measured speedup, and the agreement statement. Scoped to the race view; the
  single-objective trace box is untouched for other missions. Replay-safe
  (`?static=1&upto=<seq>` renders any mid-flight frame deterministically).

### Part 2 — five-video capture kit

- **`sdk/scripts/capture_video.py`** — generalizes `capture_motorbike_video.py`
  to all five acts: `airplane` (B-52 + b52.stl), `motorbike`, `valve`,
  `optimization` (airliner), `race`. `--video all|fast|<name>`. It POSTs the
  act's directive on your port, watches the event stream, records each beat's
  event SEQUENCE, then shoots deterministic `?static=1&upto=<seq>` frames after
  the mission completes (no headless-Chrome/SSE race, no solver contention).
  Writes numbered stills + `shotlist.md` (per-beat narration ≤14 words, no
  em-dashes) + `capture-manifest.json` into `demo-output/website/<video>/`.
  - **Fix carried:** the old motorBike triggers keyed on `ev.get("type")`, but
    persisted events use `event` — they would never have fired. The kit keys on
    `ev.get("event")`.
  - **Headless lesson:** live (`?mission=`, SSE) stills do not render reliably
    under headless Chrome — that is why the codebase has the synchronous
    `?static=1` path. The kit uses `static + upto` exclusively.

## Measured live race (from a real GUI run on this box)

RACE_MC_SAMPLES=5, four-slot cap split 2+2, box shared with other jobs:

| lane | real solves | core-min | wall | peak |
|---|---|---|---|---|
| full Monte-Carlo | 55 | (measured) | (measured) | L/D ≈ 18.13 ± 0.04 at 0° |
| reduced-order | 5 | (measured) | (measured) | L/D ≈ 18.14 at 0° |

The two paths agree to ~0.1%. The speedup card shows only what the run
measured; it scales with RACE_MC_SAMPLES and box load. An earlier single-pool
run (before the reserved-slot fix) measured 55 solves / 17.9 core-min / 74.5 s
MC vs 5 solves / 1.9 core-min / 11.1 s ROM → 9.2× core-min, 6.7× wall, agree
0.1%. The measured numbers in `demo-output/website/race-gui/capture-manifest.json`
and the mission's `race.json`-equivalent events are the record of the captured
run. The fuller 8-sample benchmark (21.5× / 29.8× under load) stays in
`demo-output/website/race/benchmarks.md` (BG-1).

## Captures produced

- `demo-output/website/race-gui/` — `01-start`, `02-mid-mc-grinding`,
  `03-reduced-order-finished`, `04-finish` + `shotlist.md` + manifest.
- (fast acts) `demo-output/website/valve/`, `.../optimization/` — run via
  `python sdk/scripts/capture_video.py --video fast`.
- Ready-to-run, not yet captured this shift: `--video motorbike` (pre-warm the
  mesh cache first) and `--video airplane` (B-52 cold snapped mesh ≈ 8 min —
  run if the night allows).

## Run / verify

```
cd sdk
CHIEF_ADAPTER=openfoam OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606" \
  OPENVSP_RUN_PREFIX="wsl -d Ubuntu --" CHIEF_ENGINEER_PORT=8772 \
  RACE_MC_SAMPLES=5 python -m chief_engineer.server
# then, from repo root:
python sdk/scripts/capture_video.py --video race --port 8772
python -m unittest discover tests    # (in sdk/) all green
```

## Coordination / merge notes

- GUI changes are scoped to the race view (new `#raceView`, race.* handlers,
  `state.race`); the shared trace/landscape/geometry machinery is untouched, so
  this merges cleanly alongside the `feat/gui-core` event-pacing work. Merge main
  mid-shift to pick up their sync; re-check `drawRace()` against any queue
  changes.
- No changes to port 8765 or its server invocation.

## Known gaps / next

- Speedup magnitude depends on RACE_MC_SAMPLES and box load; for the website
  headline use the 8-sample benchmark (BG-1), and let the live act's card carry
  the run-of-the-moment number.
- `--video motorbike` / `--video airplane` not captured this shift (solve-bound
  / cold-mesh); kit is ready.
