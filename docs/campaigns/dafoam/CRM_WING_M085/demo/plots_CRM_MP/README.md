# CRM wing, Mach 0.85 — act folder

**RUN.** The published DAFoam `CRM_Wing` tutorial, **M = 0.8497** (U₀ 295 m/s,
T₀ 300 K), `DARhoSimpleCFoam`, wall functions, **579,072 cells**, FFD
`FFD/wingFFD.xyz`. Run root
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/`. The figures here
come from `MP_R2_20260914T011050Z.log` (six converged primals), the three case
directories `MP_R2/mp04|mp05|mp06`, and `DECOMP_SWEEP_ROLLUP.json`.

**🔴 THE OPTIMISATION IS `PENDING`. NO DESIGN ITERATION HAS EVER COMPLETED.** Every
figure in this folder is the **baseline** geometry at three trimmed lift conditions.
Nothing here is optimised, improved, or a before/after. The adjoint is running now.

---

## Baseline drag at the three lift conditions — `baseline_drag_three_conditions.png`

**PROBLEM.** A multipoint design needs to know what the *unmodified* wing costs at each
lift condition it will be asked to fly. Without that, any later "improvement" has no
floor to be measured from.

**SOLUTION.** Three primals of one geometry, each trimmed to its own lift target, run
to 2,000 iterations and converged.

**RESULT.** `C_D` = **0.016173887409** at `C_L` 0.400, **0.020901505417** at 0.500,
**0.028235978333** at 0.600 — a **74.6 % drag spread** across the three conditions.
The middle condition is the tutorial's own operating point, and it lands **0.0072 %**
from DAFoam's published **0.02090**, which is drawn on the tile.
*Artifacts:* `baseline_drag_three_conditions.csv`, `MP_R2_20260914T011050Z.log`.

## Trimmed angle of attack — `trimmed_alpha.png`

**PROBLEM.** The three conditions differ only in lift. Something has to absorb that
difference, and if it is not the geometry then it is the attitude.

**SOLUTION.** Each condition is trimmed to its target by its own angle of attack, with
the geometry held identical across all three.

**RESULT.** **1.32496937°, 2.11023869°, 2.88211463°** — a 1.56° spread carrying the
whole 0.4 → 0.6 lift range on one unchanged wing. Each of the three is asserted to
appear in the run's own log before it is drawn. *The common starting angle of
2.11031707° belongs to `MP_R1` and appears zero times in this log, so it is not drawn
on this tile.*
*Artifacts:* `trimmed_alpha.csv`, `MP_R2_20260914T011050Z.log`.

## Decomposition study — `decomposition_study.png`

**PROBLEM.** The same physical problem, split across a different number of ranks,
should give the same answer. If it does not, every number downstream is suspect.

**SOLUTION.** The identical primal at 8, 20 and 28 ranks, each graded against DAFoam's
own residual threshold of **1.0e-06**.

**RESULT.** **20 ranks passes and is bit-identical between positions**
(`4.265593605364853e-08`). **8 and 28 ranks both exceed the threshold at position 2** —
`1.981968888016819e-06` and `1.757696578179007e-06`. Two identical physical problems,
three rank counts, and only one of them reproduces itself.
*Artifacts:* `decomposition_study.csv`, `DECOMP_SWEEP_ROLLUP.json`, `DECOMP_N*_GRADE.json`.

## C_D history — `cd_history.png`

**PROBLEM.** A converged drag number is worth nothing if the run was still moving when
it was read.

**SOLUTION.** `C_D` at every checkpoint the solver wrote, for all three conditions on
one set of axes, with the published value drawn.

**RESULT.** All three are flat well before 2,000 iterations and the three curves never
cross — the drag ordering is established early and holds. **The history is 21
checkpoints, not 2,000 points**: the log records `Time = 1, 100, 200 … 2000`, and
nothing is interpolated up to look denser than the record is.
*Artifacts:* `cd_history.csv`, `MP_R2_20260914T011050Z.log`.

## C_L history — `cl_history.png`

**PROBLEM.** The lift targets are a constraint, not an outcome. Whether the trim
actually held has to be visible.

**SOLUTION.** `C_L` against iteration for the three conditions, with all three target
lines drawn.

**RESULT.** Each condition sits on its own line: **0.4000005652, 0.5000003589,
0.5999953648** — within **6e-7, 4e-7 and 5e-6** of 0.400, 0.500 and 0.600. The trim
holds to better than one part in a hundred thousand.
*Artifacts:* `cl_history.csv`, `MP_R2_20260914T011050Z.log`.

## Residuals — `residuals.png`, `residuals_cl0{4,5,6}_f{10,25,50,75,100}.png`

**PROBLEM.** "It converged" is a claim, and a single end-state figure shows where a run
*finished*, not that it *descended*.

**SOLUTION.** Six equations — `U_x, U_y, U_z, h_e, ν̃, p` — cut at 10, 25, 50, 75 and
100 % of each primal, **on one set of pinned axes per condition** so the frames can be
stepped through.

**RESULT.** Every equation falls monotonically and flattens; the frame series shows the
descent rather than asserting it. Without pinned axes each frame autoscales to its own
data and the descent becomes invisible — which is why the axes are fixed.
*Artifacts:* `residuals_cl0*.csv`, `MP_R2_20260914T011050Z.log`.

---

## Geometry and field panels

`crm_mesh_wing.png`, `crm_mesh_symmetry.png`, and the three wall-pressure panels
`crm_p_cl0{4,5,6}.png` — same camera, one shared colour range across the three so they
compare, bar titled from the field's own `dimensions` header. **See `SIDECAR.md`** for
their provenance and for the one thing a reader must know about them: `cl06`'s
converged field is stored under the time name **`0.0001`**, not `2000`, because the
adjoint reset the solver clock and renamed the directory — the field itself is the same
converged state, written once and untouched since.

## Verdict

**`PENDING`.** Baseline established and verified against the published result; the
optimisation has not yet completed a design iteration. `SIDECAR.md` carries the full
provenance, every artifact path, and what is not built.
