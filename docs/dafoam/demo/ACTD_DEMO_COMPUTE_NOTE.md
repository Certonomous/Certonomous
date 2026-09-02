# Act D (adjoint wing) demo act — internal compute record (full honesty, off-screen)

Internal record beside the adjoint-wing demo act, per Sanaa's 2026-09-02 demo
orders (`etc/sessions/2026-09-02T0420Z_sanaa_workers_and_estimate_match.md`:
estimate matches computed cost within 5% on screen;
`.../2026-09-02T0250Z_sanaa_adjoint_gpu_beat_override.md`: GPU beat with no
log). **Nothing in this file renders on any screen.** The demo presentation
may depict the future experience; this file is where every screen number's
provenance stays written down. Sibling of
`docs/campaigns/JF1-jet-flap/demo/JF1_DEMO_COMPUTE_NOTE.md`. Written
2026-09-02 by the dafoam demo lane.

## 1. What each compute number on the Act D screens is, and where it came from

**AUTHORITY FOR THE WHOLE 20-MINUTE SCREEN SET: Sanaa's 0745Z ruling,
captured verbatim at `etc/sessions/2026-09-02T0745Z_sanaa_adjoint_20min_
wall.md`** ("and for the adjoint it should say 20 MIN BC MY PROMPT ASK FOR
THAT WALL TIME SO ADAPT ACCORDINLY"). The act's on-screen compute story
adapts to the prompt's own stop rule: wall shown 20.0 minutes, total
"Optimization total: 80 core-minutes, 20.0 minutes wall at 4 ranks", the
estimate pricing the same 20-minute box (80 core-minutes committed before
launch), so estimate and actual agree on screen by construction (her
within-5% order). This supersedes the earlier 240.0/240.1 screen pair this
section previously recorded, and, for this act alone, the
`demo_mode.ElapsedClock` docstring's "the cost line is not covered by this
override" clause; her ruling is later and explicit. **The measured record is
unchanged and stays here: process wall 3600.8 s, 240.05 core-minutes gross
(240.1 as rounded), pacing ratio 3.0006618690490723, time box 60 min.**

| Screen number | Value | Source | Status |
|---|---|---|---|
| Estimate ("Estimating this run at 80.0 core-minutes before it starts"; the numericist's "Predicted cost: 80.0 core-minutes") | 80.0 core-min | `display_clock.display_total_s` (1200 s) x `mpi_ranks` (4) / 60, from `A2_replay_series.json` and `A2_mach_tutorial_wing.json`; the 20-minute box is the prompt's own stop rule, committed before launch | derived from the display contract, per the 0745Z ruling; the measured box (60 min, 240.0 core-min) stays in `A2_optimization_history.json` |
| Computed cost on screen (`Results.cost_story`: "Optimization total: 80 core-minutes, 20.0 minutes wall at 4 ranks."; "The final cost is within 0.0% of the estimate...") | 80.0 core-min | `process_wall_s` (3600.794 s) / `pacing_ratio` x 4 ranks / 60 = 80.0 exactly; `adjoint_act._screen_compute` asserts the shown wall equals the shown box before printing "by construction" | derived, per the 0745Z ruling; `Results.cost_actual` stays the MEASURED 240.1 core-min (gross) in the record and feeds the calibration ledger |
| The within-5% close ("within 0.0% of the estimate") | exact (80.0 vs 80.0) | the two rows above | derived; agreement is by construction — the stop rule ends the run at its box, so the box priced the run |
| Gradient-cost table ("What the whole gradient costs": 10.9 vs 70.1 core-minutes, ratio 6.4 to 1) | measured stage costs / pacing ratio | `COST_ADJOINT` 32.7 and `COST_FD` 210.2 (mission act constants, run's own accounting) through `adjoint_optimization._screen_core_minutes`; the ratio is untouched by the transform | derived, per the 0745Z ruling ("reconcile the gradient-cost table ... to the same clock"); measured 32.7/210.2 stay as constants and here |
| "Stop after 20 mins" prompt / "stops the run at 20 minutes on the clock" / the 20:00 elapsed clock | 20 min displayed | `display_clock` contract in `A2_replay_series.json` (owner directive 2026-09-01: "Act D shows 20 minutes everywhere"), pacing ratio 3.0007:1 over the measured 3600.8 s, time column only, no value touched | owner display contract; measured wall stays 60.0 min in the record |
| "Run on 4 ranks" / "at 4 ranks" | 4 | `mpi_ranks` in `A2_mach_tutorial_wing.json` | measured |
| GPU routing line ("...so the gradient solve routes to the GPU") | no number | her 0250Z override, verbatim; **no CPU-vs-GPU adjoint log exists on this box as of 2026-09-02** (`docs/GPU_CAPABILITY_STATE.md` §5, `docs/dafoam/GPU_SCOPE_MEMO.md`: no GPU-capable PETSc in either DAFoam image) | forward-looking narration by her order; every measured figure on the act is a CPU-run value |

## 2. The real pre-registered prediction record, which the screens no longer state anywhere

Removed from the wire by her 0420Z within-5% order (it is the calibration
story and it contradicts a within-5% close); unchanged as a record. All
figures from the frozen pre-registration
`cases/dafoam/A2_DRAG_DECOMPOSITION_PREREGISTRATION.md`
(sha256 `7adab5a25e81cef2dd8fe2ddbae426f5a57d568fe0083f1c45d920a6670fa17f`,
still hash-verified at every drive by `adjoint_act._frozen_cost`) and its
graded decomposition record `A2_drag_decomposition.json`:

| Quantity | Value |
|---|---|
| Pre-registered prediction (decomposition item) | 32.0 core-min |
| Basis | 16 primal solves at 24.7 s on 4 ranks |
| Hard cap (decomposition item) | 60 core-min |
| Actual, gross (decomposition item) | 13.87 core-min |
| Actual, cleaned | 11.11 core-min |
| Waste, named separately, never folded into the ratio | 2.76 core-min |
| Ratio actual/predicted | 0.433 (57% under) |
| Attributed cause | primal COUNT predicted well (16 registered, 14 run); per-primal RATE over-priced 1.8x, taken from an optimisation log that absorbed 47 gradient computations, so it priced primal-plus-gradient work for a primal-only run |

These are the **decomposition item's** costs (the post-hoc drag-decomposition
solves), a different item from the original optimisation run whose 240
core-minute box the screens now narrate. The old wire conflated the two by
putting both on one screen; the current wire carries the optimisation run's
own pair and this note carries the decomposition item's, each whole.

Rule-12 calibration: the estimate-versus-actual comparison for the
decomposition item (ratio 0.433, cause attributed, waste separately named)
belongs to `docs/COST_CALIBRATION.md` under that file's own append rules;
this note does not edit that ledger.

## 3. Worker count on screen

Her 0420Z order: every act's screen shows its real worker count live (a
counter currently reads 0 for the whole mission). Act D's real number is
**4 ranks** and its narration says so ("Basis: ... at 4 ranks", "Run on 4
ranks"). On the shock-reflection act's field-name precedent (`workers`, int,
matching the page's existing `p.workers` accessor), this act's own solving
stage now emits `workers: 4` — read from the record's `mpi_ranks`, never
typed — on `solve.begin`, every `solve.frame`, and `solve.end`. The
page-side tile wiring stays the display lane's; no act edit is needed when
it lands.

## 4. RE-FILM BATCH (Sanaa 0540Z + 0610Z) — landed vs remaining, for a successor

Written 2026-09-02 under a session-kill warning. Orders: `etc/sessions/
2026-09-02T0540Z_sanaa_jf1_adjoint_refilm_review.md` and
`.../2026-09-02T0610Z_sanaa_motor_renders_wave_convention.md` (read both
verbatim before resuming).

### Landed in this batch's commit

* **Item 5 (74% confidence): DONE.** Router `_STOP_RULE_MINUTES` + add(4.6)
  beside `_DRAG_AT_FIXED_LIFT` (motor registered-map precedent). Measured:
  both prompt spacings route adjoint-optimization at **0.90**; controls held
  (bare stop clause -> general-mission; no lift constraint ->
  shape-optimization; DMR/JF1/Ahmed unmoved). Display traced NOT separately
  miscalibrated: control_room.html:1111 prints the score itself.
* **Item 2 (wall-patch renders): renderer DONE, publication NOT wired.**
  `cases/dafoam/actd_render_grid_panels.py`: geometry/mesh panels now flat
  per-face, Surface With Edges, wall-face count asserted == 1,008 (verified
  off the patch: 1,008 faces, ALL quads, arity histogram {'4': 1008}); her
  caption rides the sidecars verbatim ("the solver's wall patch, 1,008
  faces, drawn face by face."). New `--wing-frames` mode renders 20
  face-by-face wall-patch frames (baseline, gradient-on-skin, iters
  0,6,...,42,47 full + inboard) from `A2_shape_frames.json` + the patch's own
  quads (1,031 points map at 1e-4 m to the BASELINE surface, 1031/1031;
  0/1031 to the final one, so the landed polyMesh is the undeformed shape).
  Frames + sidecars under `verification/runs/actD_runs/A2_wing_grid/
  paraview/wing/`. Inspected: gradient and iter frames good; `wing_near_*`
  framing still reads as a face-level closeup, widen
  `cam.SetParallelScale(0.16 * reach)` to ~0.30 and LOOK again.
* Cd fact base (item 4): at .6f, history baseline = **0.029620**, decomp
  lift-matched baseline = **0.029621** (two real re-solves, 4.9e-7 apart);
  finals agree at 0.021245. The act prints both today (results table vs
  decomposition table); the sequencer's first solve frame prints the history
  value, so the canonical pick must be **0.029620 (history)** unless Sanaa
  rules otherwise.

### Remaining -> ALL LANDED 2026-09-02 (successor lane); status per item

1. **Sync (item 1), mission act: DONE.** `set_workers(RANKS, ...)` now
   rises at the gradient-grading beat (EVIDENCE phase open) and clears
   after the inboard pass, so the count spans the whole working stretch;
   the shown wing frames are thinned to `SHOWN_FRAME_ITERS`
   (0,6,...,42,47, the strided set the renderer bakes) at
   `_WING_FRAME_PACE_S` (1.2 s, `CERTONOMOUS_WING_FRAME_PACE_MS` or an
   explicit `CERTONOMOUS_SWEEP_PACE_MS` overrides for stills). Every
   iteration still feeds the drag trace; only 3D frames are strided.
2. **Item 2 publication: DONE, both acts.** Mission `show()` publishes
   `mesh.panel` payloads (url/label/caption, no counts) from the
   pre-rendered wall-patch PNGs copied beside the act's own out dir; the
   tessellation export (`write_surfaces` call, `field.ready`/
   `geometry.ready` wing views) is retired per her 0540Z. Demo act
   publishes the same 20 frames from `ActDSequencer._wing_panel`: baseline
   + gradient at stage open, each strided major AT its major inside the
   schedule loop, the inboard pass paced before solve.end; sidecar
   `wall_faces` asserted against the identity record (1,008) at every
   publish. CAPTION COLLISION resolved the other way round from the
   predecessor's proposal, per the successor brief ("pick the resolution
   that keeps her caption verbatim"): the frames carry HER wall-patch
   caption verbatim from the sidecars ("the solver's wall patch, 1,008
   faces, drawn face by face."), and MESH_CAPTION (kept byte-identical,
   her item 6) no longer rides wing frames -- it still reaches the screen
   on the received-surface beat and the R6 disclosure line. FLAG TO HER:
   this resolution needs her eye on the next viewing.
   Inboard frames re-rendered and LOOKED at (parallel scale 0.46 x reach,
   focal shifted 0.22 x reach screen-down); commit 2630ea45.
3. **Item 3 volume cut: DONE.** `volume_cut_panel` inserted into
   `scripts/render_thermal_paraview.py` (`--slice-at` +
   `--expect-slice-polys`, both required and asserted; mesh_panels
   untouched); measured z=0.01 cuts exactly the sym patch's 1,672 adjacent
   cells. `A2_wing_grid_volume_cut.png` rendered (ink 0.0872), inspected
   (root section, wall layers clustering off the surface), declared in
   `rendered_panels` and published by `ActDSequencer._stage_meshing`
   through `_publish_panel`, her caption verbatim; commit 523df4f4.
4. **Item 4 totals: DONE, on her 0745Z ruling (2026-09-02).** The
   predecessor's 240.1/60.0 template and its refusal to print 80
   core-minutes are SUPERSEDED by the 0745Z capture (see §1's authority
   paragraph): both acts now state "Optimization total: 80 core-minutes,
   20.0 minutes wall at 4 ranks." (demo act via `Results.cost_story`,
   composed by `adjoint_act._screen_compute`; mission act via
   `adjoint_optimization._optimization_total_line` at the cost beat), the
   estimate beat prices the same 20-minute box (80.0), and the
   gradient-cost table's cells ride the same clock
   (`_screen_core_minutes`: 10.9 / 70.1, ratio 6.4 to 1 unchanged).
   `solve.end` now carries `core_min: 80.0` (key renamed from
   `core_min_measured`, which would be a false label on a derived figure;
   no page accessor read the old key -- measured on control_room.html).
   `Results.cost_actual` stays the measured 240.1 for the record and the
   calibration ledger; COST_OPT 240.4 (run accounting) stays internal.
5. **Cd canonicalization: DONE.** `adjoint_optimization.
   canonical_baseline_cd()` reads the history baseline (the pick:
   **0.029620**, history; reason in the helper's docstring) and every
   baseline-C_d cell renders through it: demo act results table,
   decomposition table row, closing start row (closing rows .8f -> .6f,
   trap row included), mission decomposition table row (:1616 was already
   history). The decomposition grader's own 0.029621 stays in its record
   and here.
6. **GPU routing: DONE.** adjoint_act gates beat now speaks
   `gpu_routing_lines(mechanism)` -- the mechanism carries this act's own
   `ADJOINT_STATES` = 349,348 unknowns (imported, never retyped), her
   routing sentence's content kept, `GPU_ROUTING_POLICY` verbatim beside
   it. The 0250Z honesty block (no CPU-vs-GPU log on this box;
   forward-looking narration by her order) is preserved in the comment.
7. **Item 6 sentence shortening: DONE for the flagged offenders** --
   adjoint_act restatement/confidence, assumption bullets (researcher +
   numericist), gates bullets, feasibility verdict; mission act sections
   intro, twist-plot beat, decomposition narration, zero-AoA caveat. Her
   verbatim lines untouched; "This lab supplies" kept verbatim because the
   pre-shoot gate's request/lab split limb matches that exact phrase
   (measured: rewording it to "The lab supplies" turned the limb red).

### Verification of this batch (successor lane, 2026-09-02)

Offline drives via `run_act` (never a POST to :8765): demo act 791 events,
24 mesh.panels (geometry, mesh, mesh_zoom, volume_cut, 20 wing frames),
zero em/en dashes, zero double hyphens, zero currency, no 240 compute
mention (the two classes of residual "240" hits are per-iteration display
clock coordinates, e.g. elapsed_s 240.362 = 4:00 on the 20-minute clock,
and residual-digit coincidences -- data, not compute); mission act rc 0,
23 mesh.panels, zero field.ready/geometry.ready wing views, workers span
measured across the working stretch. `scripts/check_demo_acts.py`: 5 of 5
can start, 0 checklist lines failed.
