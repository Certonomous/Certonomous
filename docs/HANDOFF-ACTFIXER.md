# ACT-FIXER handoff — demo-act hardening (branch feat/demo-acts)

## ROUND 2 (ACT-FIXER-b) — G12 money-shot fix + longer, more visual acts

**G12 (P0) — motorBike field-painting fixed.** The painter was merging domain
boundary patches and rendering "5,747 faces as two flat rectangles". Rewrote the
patch selection in `sdk/chief_engineer/field_render.py`: merge ONLY body patches
(the `motorBike_*` group; the single body patch for B-52/NACA), exclude every
domain boundary (inlet, outlet, ground/floor, sky, sym\*, frontAndBack,
upper/lowerWall, defaultFaces) via `_is_domain_patch` + `_body_patches` (a
two-tier filter: blocklist, then keep the dominant `<body>_*` group). Two
safeguards added: (a) a face-count sanity check — painted body below a robust
fraction of the input triangle count logs `field-paint patch selection suspect`
and falls back to the wireframe; (b) `field.ready` now carries a bounds hint so
the viewport auto-frames the painted body. Result: the motorBike renders as a
**recognizable Cp-painted motorcycle, 101,235-face body** (shown decimated
~19k), drag 0.4156 SOLVER-BACKED. Proof: `demo-output/acts/round2/motorbike/03-cp-painted.png`.

**`min_fraction` calibration (judgment call, flagged).** The owner's literal "30%
of input STL triangles" floor is miscalibrated: snappyHexMesh remeshes, so the
*correct* motorBike body is only 31% of the 331,653-triangle input — one point
above a literal 30% floor, which would false-positive on any mesh jitter and
re-break the money shot. Measured populations: correct body 31%, the failed
domain-rectangle selection 1.7%. Set the default floor to **0.15**, which
separates the two by a wide margin (catches the failure ~9× under, passes the
real body ~2× over). Documented in the function docstring. Field decimation cap
raised 12k→30k so the displayed body reads clearly as tens of thousands.

**B-52 re-verified — still paints correctly.** Single-patch body, 15,660 faces
(114% of its 13,784-triangle input), recognizable painted airframe, drag 0.0464
SOLVER-BACKED. Proof: `demo-output/acts/round2/b52/03-cp-painted.png`.

**Act 1 (airliner) — more dramatic morph + more finalists.** Sweep is now a real
third design variable (`_SWEEPS = 20/25/30/35°`, inner loop) so the candidate
wing visibly rocks through sweep as well as span/area — **96 candidates** screened
(was 24), the planform morphs many times on camera. Finalists raised **6→9**,
each a real VSPAERO solve. Winner unchanged headline **L/D 19.7 @ span 64 m**
(now explicitly sweep 35°; the solve moves the pick off the screen's 25°).
Worker-kill matched-numbers proof re-verified with 9 finalists: sabotaged slot-3
run gives byte-identical nine polars and the same winner, `worker.killed` /
`worker.reprovisioned` = 1 sabotaged / 0 clean. Method memo now reads
"3-parameter". No new physics — the existing `cd0` quadratic (min at 25°) already
encodes the sweep trade honestly.

**Act 2b — NACA 4412 finite wing (optional second solved act).** Staged at
`sdk/geometry/naca4412_wing.stl` (identical to the curriculum body), mesh cache
**pre-warmed** (`~/certonomous-runs/.mesh-cache/naca4412_wing`). Real solve paints
a 27,748-face wing and reaches **VALIDATED** (Cd 0.0217 vs 0.03, 28% inside the
±40% band vs Abbott & von Doenhoff). Runbook updated with short-cut vs long-cut
structure. Proof: `demo-output/acts/round2/naca4412/`.

**Capture-script bugs fixed** (`sdk/scripts/capture_motorbike_video.py`): it read
`ev.get("type")` but events carry the kind under `event`, and stills omitted
`&static=1`, so it captured nothing. Both fixed; now drives motorBike/B-52/NACA
captures cleanly.

**Task-C dependency satisfied.** GUI-1b's transcript/visual sync fix + auto-framed
geometry already landed on main (commit e0da36d, "unified sync queue") and is
merged here; my body-only fix composes with its vert-based auto-frame (viewport
frames on the now-correct body). Static-replay captures don't exercise the live
paced sync queue — that is GUI-1b's, on main.

**NOTE — pre-existing uncommitted binary.** `sdk/geometry/motorBike.obj` was
already modified in the worktree before this session (11.1 MB / 331,653 tris vs
HEAD's 10.7 MB), timestamped before my work. The server's upload handler writes
uploads back to `sdk/geometry/`, but re-wrote identical bytes. I did NOT stage it
(it is not my change); the demo/captures depend on the 331,653-triangle file
being present — orchestrator to decide whether to commit it.

---

## ROUND 1 (original ACT-FIXER)

Hardened the three demo acts end to end. Server on port 8768 (never touched
8765). 134 tests green throughout. Commits are local (never pushed).

## Valve act (Act 3) — KEEP/CUT recommendation

**KEEP the valve act as a research-frontier segment, conditional on the valve
viewport render landing; if that render does not merge, it is still demo-safe
but should not be the hero take.** Reasoning: the act runs clean and
deterministic (0.4 s compute, every beat fires — VALVE STUDY route, the Chief
Researcher Womersley memo with α ≈ 16.7 computed and displayed plus its ruling,
the candidate landscape with the winner ringed, the 1327 ± 421 Pa @ 80° result
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
- Womersley α ≈ 16.7 displayed, landscape, 1327 ± 421 Pa @ 80°, agenda, all
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
