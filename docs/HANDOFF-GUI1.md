# Handoff — GUI-1 (branch feat/gui-core)

Overnight work on the control-room GUI + supporting backend emits. All commits on
`feat/gui-core`; 135 backend tests green before each commit. Started from main
`d57596c` (G1 paced transcript + live KPIs), which is built on, not duplicated.

## What landed (proven by screenshot in demo-output/gui-proof/)

### G8 — Valve visuals (was "No surface loaded" the whole run) — DONE
- `chief_engineer/geometry.py::valve_surface(angle)` — parametric three-leaflet
  valve, mirrors `wing_surface()` payload. Orifice widens/pinches with the
  opening angle (free-edge radius ∝ sin θ, same measure `effective_orifice_area`
  uses); a small render scale keeps the three leaflets legible even fully open.
- `server.py::_serve_geometry` — `/api/geometry?valve_angle=NN`.
- `workflows/valve_study.py` — emits `geometry.ready` per candidate angle
  (label "candidate valve — opening NN°") AND the winner again at conclusion, so
  the valve renders and the winning valve stays on screen after the run.
- Waveform figure: `chief_engineer/plot_theme.py::waveform_figure` — a
  publication-grade, **GUI-themed dark** systolic-waveform PNG (mathtext labels
  `$Q(t)$`, `$\alpha$`; three weighted phase points ringed + annotated; title,
  axes+units, legend, Womersley annotation). Emitted via the existing
  `announce_plot`/`plot.ready` path → leads the valve report.
- Proof: `g8_valve.png`.

### G2 / N1 — Progressive dashboard + dispatch panel — DONE
- Backend pacing (paces the PATH, never results; env-gated
  `CERTONOMOUS_SWEEP_PACE_MS`, 0 in CI): aircraft ~120 ms/candidate, valve
  ~550 ms — landscape points, the candidate geometry, and the dispatch slots land
  one by one.
- Dispatch panel (telemetry column): a live per-worker strip — slot number,
  current design, state (solving/done/lost, animated), header
  "N granted of M requested" (requested-vs-granted from the compute audit). Fed by
  a new `dispatch.update` event emitted from the aircraft screening loop +
  finalist solves and from `shape_optimization._solve_slot`.
- Proof: `g2_dispatch.png` (6 finalist workers caught mid-solve).

### G3 / G9 — Geometry viewport is the hero — DONE
- Layout resized: viewport is the widest, central column (300px / 1.5fr / 1.05fr)
  with a 320px min stage — no longer a thumbnail squeezed above the landscape.
- Landscape kept at its existing quality (axes/units/ticks/colorbar/legend/winner
  annotation intact) and now sits in an evidence row beside the new live trace.
- Proof: `g3_viewport_hero.png` (real VSPAERO-solved winning wing, 880 faces,
  dominating the frame; landscape + live trace below; full report beside — B4).

### A2 / G10 — Plots evolve live + publication-grade — PARTIAL (see gaps)
- **Live objective trace** (new): a streaming line + envelope canvas that grows as
  candidates land (`trace.point` event → `drawTrace`), with axes/units and a
  latest-value annotation. Wired for the aircraft (running best-L/D) and the valve
  (cycle-weighted loss with envelope). Visible in all three proofs.
- **Publication-grade PNG standard**: `plot_theme.py` gives dark GUI-matched
  figures with mathtext, wide (report-column) sizing, titled frame + legend +
  annotation. The valve waveform is built to this standard.

### B1 / B2 / B4 — Geometry persistence — DONE
- B1: the "renders here…" placeholder is now a single source of truth in
  `drawGeometry` (visible only when no mesh; strictly inside the stage — cannot
  overlay another panel/view).
- B2: geometry never disappears — wireframe through setup, painted on field
  landing, still visible while reading the report. A monotonic geometry token +
  one-tick burst coalesce fixes an out-of-order-fetch bug where a late finalist
  could overwrite the winner.
- B4: the completed still keeps geometry (painted) + evidence plots + report side
  by side; at completion the report comes forward while the centre column holds
  the body and plots.

### A1 — Transcript pace + recorded-pace — DONE
- Inter-entry spacing raised to ~1.5 s (was 650 ms).
- `PACE · READING / RECORDED` masthead toggle: recorded mode honours the real
  event timestamps (`p.at`), clamped to a watchable range, for replays.

### R1 — Display names — GRACEFUL FALLBACK (registry pending)
- Viewport labels prefer the event's human label (workflows already emit these);
  the raw-name fallback now strips extension/path and humanises. When GUI-2's
  `chief_engineer/display_names.py` lands on main, wire it in for uploaded
  surfaces (marked in code).

## New event contracts introduced (for other agents / the orchestrator)
- `dispatch.update` `{slot:int, state:"solving"|"done"|"lost", label:str, detail:str}`
- `trace.point` `{series:str, x, y, lo?, hi?, x_label, y_label, title, feasible?}`

## Screenshot / capture tooling (new)
- Static replay: `?static=1` dispatches the recorded snapshot with **no open SSE**
  (the streaming `/events` never closes, which deadlocks headless virtual time),
  so headless captures are deterministic. `&upto=N` freezes a mid-flight still.
  The snapshot parse **sanitises NaN/Infinity** (see backend note). This is a
  capture aid only — the live UI path is untouched.

## Gaps / not done (honest)
- **A2/G10 broader restyle**: the existing report PNGs (shape-optimization,
  geometry-study, uncertainty A/B in `monte_carlo.py`/`head_engineer.py`) are
  still the **light** theme, not the new dark `plot_theme` standard. Only the
  valve waveform is on the new standard. Restyling those is the next step (the
  "before/after same-mission report" acceptance is not yet met for those plots).
- **Live traces from the ensemble / geometry-study coefficient history** (the
  "envelope forming in real time" money shot from a real solve loop) are **not
  wired** — the trace infra + two workflow traces exist, but `run_ensemble`
  (monte_carlo) and geometry_study don't emit `trace.point` yet. Threading `emit`
  through `run_ensemble` is the clean follow-up (touches shared code — coordinate).
- **Full fan-out dispatch visual**: tonight the machine is loaded (4–5 other jobs
  hold cores) so the audit reports capacity 5, and the dispatch panel honestly
  shows "5 granted of 12 requested — staged". With free cores it shows the full
  12-wide fan-out. The panel + header are correct; only the live capacity number
  reflects load.

## Backend note to flag (not GUI-owned)
- VSPAERO finalist polars can contain **NaN** (`vspaero.polar` payload). Python
  serialises that as bare `NaN`, which is invalid JSON: the live SSE path drops
  the offending frame (per-frame try/catch) but any bulk `JSON.parse` of the
  snapshot fails. The GUI now sanitises on the static path; the real fix is to
  scrub NaN in the solver adapter before emit.

## Merge conflicts the orchestrator should expect
- `sdk/chief_engineer/control_room.html` — heavily edited (dispatch panel, live
  trace, evidence-row layout, viewport-hero grid, static-replay path, pace toggle,
  geometry seq guard). Likely conflicts with any other GUI agent touching this
  single file — merge by keeping all sections.
- `sdk/workflows/{aircraft_optimization,shape_optimization,valve_study}.py` —
  added `dispatch.update`/`trace.point` emits + pacing; backend agents may touch
  the same loops.
- `sdk/chief_engineer/geometry.py` (+valve_surface), `server.py` (valve_angle
  branch) — additive, low risk. `sdk/chief_engineer/plot_theme.py` — new file.
- Tests: `test_valve.py`, `test_aircraft_optimization.py`, `test_worker_recovery.py`
  gained assertions (the last: a clean slot now emits dispatch solving/done, not
  nothing).

## Commits (feat/gui-core, newest last)
1. G8/G2/G10 backend — valve surface + waveform, dispatch + trace events, pacing.
2. G2/G3/G8/G9 + B1/B2/B4 + A1/G10 GUI — viewport hero, dispatch panel, live trace.
3. GUI render-correctness — out-of-order geometry fix, TDZ on auto-resume.

---

# ROUND 2 — Sanaa's second feedback pass (all 8 items DONE)

Merged main (fast-forward, clean) then worked the 8 approved intents top to
bottom. Backend 175 tests green throughout. Proofs in
`demo-output/gui-proof/round2/`.

- **#1 Geometry too small — DONE.** `drawGeometry()` no longer uses a fixed
  0.42 fudge factor. It projects every vertex to the model plane, takes the
  projected bounding box, and scales so the body FILLS ~86% of the stage,
  centred. Works uniformly for wings, valve, cylinder, motorBike. Proof:
  `r2_valve_layout.png` (valve now dominates the frame).
- **#2 Bottom plots invisible — DONE.** Landscape and live-trace stack
  full-width at 320px canvas each; the viewport column scrolls (owner OK'd
  multi-page). Fully legible at 1920x1080. Proof: `r2_valve_layout.png`.
- **#3 Transcript/visual sync — DONE.** ALL viewport/evidence visual events
  (landscape + trace points, geometry + field swaps, dispatch updates, plots,
  result card) now drain through the SAME ordered paced queue as transcript
  entries (`enqueue(kind,p,ts)` / `drainReveal` / `APPLY` map). Exact emission
  order preserved via the envelope timestamp; narration and the picture it
  describes appear together. READING pace = 1.5s/entry, 240ms/visual; FAST =
  real inter-event timing.
- **#4 PACE toggle RECORDED→FAST — DONE.** Chip reads PACE·READING / PACE·FAST;
  FAST replays at real event timing.
- **#5 Presentation mode removed — DONE.** PRESENT button, present-bar,
  ?present=1, P-key, presenting CSS, and present()/togglePresent() all gone;
  pace chip restyled to a neutral `.chip-btn`. Layout verified clean without
  it. Runbook references stripped.
- **#6 Report PNGs still white (third-flag) — DONE.** `plot_theme.metric_label`
  added ($C_d$, $C_\ell$, $L/D$). Migrated ALL report generators to the dark
  GUI theme: `head_engineer.plot_with_envelope` and
  `monte_carlo.plot_convergence/plot_ab_comparison/plot_estimates` — panel
  palette, mathtext labels + $\pm\sigma$, LIVE/VALID/TREND colours, titled
  frame + legend, wide report-column sizing (11.4x4.6). Before/after (same real
  race.json ensemble) in `round2/before/` vs `round2/after/`.
- **#7 Live iterations — DONE.** geometry_study streams `trace.point` of the Cd
  coefficient marching over solver iterations with a rolling ±2σ envelope
  (`HeadEngineer.histories` exposes the full history from postprocess).
  `run_ensemble` gained an `emit` param: each completed sample streams the
  running mean + ±2·SEM band, so the envelope tightens live sample by sample
  (wired in uncertainty_reduction). Proof: `r2_geo_trace.png`.
- **#8 Directive truncation — DONE.** `#missionGoal` wraps to two lines and
  ellipsizes head-first with the FULL directive on hover (title attr set on
  launch AND resume/replay). Verified the full goal reaches routing untruncated
  (server passes the whole goal string to classify()).

## Round-2 merge risks
- `sdk/chief_engineer/control_room.html` — same single file the other GUI
  agents touch; round-2 rewrote the dispatch switch + queue drain, the
  drawGeometry projection, evidence-row CSS, and removed presentation mode.
  Conflicts likely with any concurrent edit — keep the unified queue and the
  auto-frame projection.
- `sdk/chief_engineer/monte_carlo.py` + `head_engineer.py` — plot generators
  restyled AND `run_ensemble`/`postprocess` signatures extended (added `emit`
  param / `histories` attr, both backward-compatible). A backend agent editing
  the same solve loops may conflict.
- `sdk/chief_engineer/plot_theme.py` — added `metric_label` (additive).
- `sdk/workflows/{geometry_study,uncertainty_reduction}.py` — added trace
  emission (additive).
