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

| Screen number | Value | Source | Status |
|---|---|---|---|
| Estimate ("Estimating this run at 240.0 core-minutes before it starts"; the numericist's "Predicted cost ... 240 core-minutes") | 240.0 core-min | `time_box_min` (60) x 60 s x `mpi_ranks` (4) / 60, both from the graded records (`A2_optimization_history.json`, `A2_mach_tutorial_wing.json`); the box was committed before launch (`time_box_evidence`: start marker vs driver-log mtime, elapsed 3600 s) | derived from the committed box, real |
| Computed cost ("Actual cost 240.1 core-minutes"; the shared comparison line "0.0% above the estimate") | 240.1 core-min | `process_wall_s` = 3600.794 s x 4 ranks / 60 = 240.05, from `A2_replay_series.json` | measured, gross |
| The within-5% close ("the two agree to a part in a thousand") | 0.04% apart as displayed (240.1 vs 240.0) | the two rows above | derived; agreement is by construction — the stop rule ends the run at its box, so the box priced the run |
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

### Remaining (designs verified against the code, nothing edited yet)

1. **Sync (item 1), mission act** `sdk/workflows/adjoint_optimization.py`:
   measured on the filmed events (m-8b8899f9ba9f): 48+48 wing frames burst
   in 3 s (`_FRAME_PACE_S` = 60 ms via CERTONOMOUS_SWEEP_PACE_MS) so the
   page's paced reveal drains after the act ends; `workers=4` appears in ONE
   roster.update (set_workers at :1442, cleared :1485). Fix: set_workers(
   RANKS,...) at the gradient-grading beat (~:1203) through the end of the
   inboard pass (~:1638); thin the shown frames to iters 0,6,...,42,47 with
   a ~1.2 s beat so emission paces the display. Demo act already carries
   worker_census on stage.begin (meshing/feasibility/solving = 4).
2. **Item 2 publication:** mission `show()` (:903) currently emits canvas
   JSON tessellations (`field.ready`/`geometry.ready` -> triangle canvas);
   switch to `mesh.panel` payloads with the pre-rendered PNGs copied into
   the mission out dir, url `/api/plot/<out.name>/<png>` --
   `loadMeshPanel` (control_room.html:3029) accepts url/label/caption and
   null counts, and sets paraviewOwned. Demo act: publish wing-frame panels
   at the matching majors inside `ActDSequencer._stage_solving`'s schedule
   loop (adjoint_act.py ~:1660), payload label per iteration, caption
   verbatim. CAPTION COLLISION to flag: her wall-patch caption vs her
   "keep exactly as is" MESH_CAPTION ("chosen for speed; ...") on mission
   frames -- proposal: MESH_CAPTION stays the caption, wall-patch sentence
   spoken once by the numericist; needs her eye.
3. **Item 3 volume cut:** `scripts/render_thermal_paraview.py` mesh_panels
   REFUSES when slice polygons != cell count (built for one-cell-thick
   meshes; the wing sym-plane slice gives ~1,672 polys vs 38,304 cells).
   Insert (never replace) `--slice-at FLOAT` + `--expect-slice-polys INT`;
   sym patch holds 1,672 faces. Render `A2_wing_grid_volume_cut.png`,
   caption verbatim "the volume mesh at the symmetry plane, wall layers
   resolved."; declare "volume_cut" in rendered_panels and publish it from
   an ActDSequencer._stage_meshing override (the generic `_panel` path
   already resolves `{case}_volume_cut.png`).
4. **Item 4 totals:** ship "Optimization total: 240.1 core-minutes, 60.0
   minutes wall at 4 ranks." -- reconciles exactly as her 0610Z rule
   (core-min = wall x workers; predicted wall 240.0/4 = 60.0). The
   coordinator's "on the screen's own paced clock" reading would force a
   fabricated 80 core-minutes and is REFUSED (ElapsedClock contract: the
   clock override never covers the cost; rule 12). This supersedes the
   standing "box duration not printed" directive by her newer explicit
   template -- flag to her. Also align solve.end `core_min_measured`
   round(...,2) -> round(...,1) (adjoint_act.py ~:1698). Mission act total
   uses the same measured pair; COST_OPT 240.4 (run accounting) stays
   internal, difference named. Gradient-cost table = adjoint_optimization
   :544-548 (32.7 vs 210.2 core-min) -- reconcile wording, not numbers.
5. **Cd canonicalization:** one helper reading history baseline; use it in
   the decomposition table row (adjoint_act ~:1105), closing rows .8f ->
   .6f (~:1344-1363), mission :1616 already history. Report the pick.
6. **GPU routing TODO:** `demo_mode.gpu_routing_lines` HAS landed; replace
   the local sentence in adjoint_act gates beat with
   gpu_routing_lines(mechanism) where the mechanism carries THIS act's real
   system size `_actd.ADJOINT_STATES` = **349,348** unknowns (read, never
   typed), keeping her sentence's content.
7. **Item 6 sentence shortening:** not started; longest offenders are the
   mission `_narrate` lines and adjoint_act assumption/results bullets.
