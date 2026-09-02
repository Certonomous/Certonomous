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
