# ACT-FIXER handoff — demo-act hardening (branch feat/demo-acts)

Hardened the three demo acts end to end. Server on port 8768 (never touched
8765). 134 tests green throughout. Commits are local (never pushed).

## Valve act (Act 3) — KEEP/CUT recommendation

**KEEP the valve act as a research-frontier segment, conditional on the valve
viewport render landing; if that render does not merge, it is still demo-safe
but should not be the hero take.** Reasoning: the act runs clean and
deterministic (0.4 s compute, every beat fires — VALVE STUDY route, the Chief
Researcher Womersley memo with α ≈ 16.7 computed and displayed plus its ruling,
the candidate landscape with the winner ringed, the 1345 ± 421 Pa @ 80° result
card at TREND ONLY, all three V&V-20 channels with specific notes, and the
3-entry research agenda), and it reads *well* on camera — the Womersley
reasoning is the most distinctive science moment in the demo. Its one weak spot
is the viewport: it currently shows the honest placeholder "the mission's
surface renders here — painted by the solved field once it lands / No surface
loaded", because the valve geometry render is being built by a parallel GUI
agent and **has not merged into this branch** (per orders, noted as a
dependency, not counted against the act). Acts 1 and 2 both show live geometry
in the viewport, so until the valve render merges the valve is the only act with
an empty viewport — that is the sole reason to hold it back from the hero cut,
not any defect in the act itself. Decision rule for demo day: valve render
merged → KEEP in the main sequence; not merged → keep as an optional
"research frontier" beat (the Womersley memo carries it) or CUT to
motorBike + optimization per the fallback plan.

## Per-act status

### Act 1 — airliner L/D optimization — GREEN
- Prompt: "Optimize the L/D of an airliner for 300 passengers, 6000 km range,
  take-off at 85 m/s, landing at 72 m/s".
- All beats verified live + replay: VSPAERO badge at plan, streaming digest,
  landscape skeleton → points landing, candidate wings cycling, **6 real
  OpenVSP 3.51.1 vortex-lattice polars in parallel**, winner **L/D 19.7 @ span
  64 m** ringed + annotated, result card, figures-first report, filled agenda,
  HUMAN TOUCHPOINTS · 1.
- **Determinism:** 5+ full passes — identical six solved polars, winner 19.7
  every run, all beats present, all three V&V-20 channels noted. No flakes.
- **Measured compute:** ~10 s uncontended (six real solves).
- Captures: `demo-output/acts/act1/act1_0{1..5}_*.png`.

### Act 2 — motorBike pressure field — GREEN (solve-bound; parallel lever documented)
- Prompt: "Show me the pressure field on this motorbike." + surface motorBike.obj.
- Beats verified: OPENFOAM badge, surface rendered, measurement-not-optimisation
  memo, **mesh-quality gate with real numbers (353,578 cells, non-ortho 65,
  skew 8.94)**, mesh cache reuse, live steady solve, Cp-painted body + drag with
  envelope + certificate (from the completed warm run).
- **Mesh cache implemented + measured:** the snapped mesh caches per body and is
  reused on later runs, removing the ~374 s snappyHexMesh from the on-camera
  run. Warm solve: 300 iterations serial ≈ 4.5 min on a quiet box; force settled
  by ~iteration 120 so 300 is a converged, honest window (the run now honours the
  iteration count it reports). `CERTONOMOUS_SOLVE_RANKS=6` runs it in parallel to
  fit the ~2-min slot.
- Captures: `demo-output/acts/act2/`.

### Act 3 — valve — GREEN except viewport (external dependency; see recommendation)
- Womersley α ≈ 16.7 displayed, landscape, 1345 ± 421 Pa @ 80°, agenda, all
  three channels. Captures: `demo-output/acts/act3/act3_0{1..3}_*.png`.

## Worker-kill relocation (v3-N3: no toy bodies on camera)
Moved the worker-kill resilience beat off the cylinder sweep onto **Act 1's real
VSPAERO finalist wings**. Each finalist solves on a kill-checkable worker slot
(mirrors shape_optimization). A sabotaged slot-3 run gives byte-identical solved
polars and the same winner (L/D 19.7) as a clean run; `worker.killed` /
`worker.reprovisioned` = 1 sabotaged, 0 clean. Proven both by direct workflow
invocation and live on the server. The cylinder machinery stays in the repo for
CI tests only.

## Flakes / bugs fixed (behavior)
- **Worker-kill on a toy body** → relocated to the airliner wing (content rule).
- **All three V&V-20 channels**: the input channel used a generic placeholder
  note; added an `input_note` seam and a specific, act-appropriate note in all
  three demo acts (G11).
- **motorBike iteration mismatch**: the familiar path ran the tutorial's 500
  iterations while the report claimed 300 — now sets endTime to the stated count
  so the report describes the run that actually happened.
- **No mesh reuse**: every run re-meshed cold (~6 min) — added a per-body mesh
  cache so warm runs skip snappyHexMesh.

## Known dependencies / notes for the orchestrator
- **Valve viewport render** — external GUI agent, not merged here (see above).
- **display_names.py registry** (B-52 / motorBike friendly labels) — GUI-2's;
  not on this branch yet. Captures still show "motorBike" / "motorBike.obj" as
  the label, not a raw path — no raw filename leaks, but the friendly registry
  labels will improve them once merged.
- **Professional directive prompts** (v2-E1) — GUI-2 is rewriting the runbook
  prompt set; verified with the current prompts, will re-verify routing once the
  new prompts land on main.
- **Parallel warm-solve wall-time** could not be cleanly measured on build night
  — a concurrent compute agent saturated all 14 cores (load ~13). Parallel
  stages validated individually; re-measure on the quiet demo box.

## Test count / commits
- 134 tests green. New code guarded; default behavior (serial solve) unchanged
  and fully tested. Commits on feat/demo-acts (local only).
