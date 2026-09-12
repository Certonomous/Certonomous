# dafoam case state — 2026-09-12, resume record

Minimum needed to restart when the fleet next turns on. Case / state / next action.

## FILMABLE NOW — priority 1, already on disk

**A3 ONERA M6 transonic primal** — `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/`
399,360 cells. CD **0.0229963**, CL **0.3130102**. `End` present, converged
(p initRes descends to 1.31e-06, GAMG 5-6 iters — healthy, not stalled).
**Validated against ONERA M6 experiment at the 7 canonical spanwise stations**
(0.20/0.44/0.65/0.80/0.90/0.96/0.99), upper and lower surfaces:

| station | upper Cp RMS dev | lower Cp RMS dev |
|---|---|---|
| 0.20 | 0.0741 | 0.0196 |
| 0.44 | 0.0662 | 0.0128 |
| 0.65 | 0.0814 | 0.0153 |
| 0.80 | 0.0799 | 0.0165 |
| 0.90 | 0.0704 | 0.0265 |
| 0.96 | 0.0491 | 0.0129 |
| 0.99 | 0.1139 | 0.0149 |

Lower surface 0.013–0.027 throughout; upper surface 0.049–0.114, the larger
deviations sitting in the shock region, which is where they belong on a
transonic wing. **Results saved:** VTK at time 6000 (69 MB), `postProcessing/
wingPatchSample/6000`, `cp_comparison.json`, and **nine renders already made**
in `renders_A3_demo/` — Cp upper/lower/planform/LE, Mach spanwise slices,
sonic surface, Cp stations vs experiment, shock position vs experiment.
**CORRECTION (same session, found by a lane after I wrote the line above):** the
raw FIELDS are **gone** — later `check_totals` runs at np=2 overwrote the validated
np=4 `Time = 6000` state, and the processor dirs now hold only `0` and `629`.
`system/controlDict` now reads `endTime 1500`. What survives is the VTK, the wing
patch sample, `cp_comparison.json`, the nine renders, and `run_model_run3.log`
intact (CD 0.0229956, CL 0.3131159, p 3.744179e-07, all six equations below 1e-06,
`End`, last `Time = 6000`). **So: FILMABLE today, but NOT restartable and NOT
re-postprocessable.** My earlier line "none to make it showable" was right about
showing and wrong about the case being live.
**Next action: rerun it — c2 surface, N=65, 399,360 cells, np=4, 81.4 core-min,
settings UNTOUCHED (it converged with `nNonOrth 0` and relax_p 1.0; changing them
would discard the one controlled experiment we have).**

## RUNNING

**A3GC L2** — `/home/ubuntu/certonomous-runs/A3GC-L2/`, pid 2467075/2467121, np=8.
798,720 cells, Time 700/6000, decelerating (5.3 → 33 s/step), lands 09-13/09-14.
p flat ~1.0e-03 against a 1e-06 floor. Predicted to miss its floor; prediction
registered before it lands. Not stopped.
**Next: let it land, grade with the frozen grader (md5 73dbe368934956700da87e5a1f44ea0c).**

**A3GC L1 stage 1** (mesh gen) — pid 2649997/2655085/2656601, np=1, 6,389,760 cells
target, pyHyp extrude. Unmeasured risk: 4 GiB container ceiling vs plot3dToFoam.
**Next: let it finish; the mesh is a durable artifact.**

## FAILED, CAUSE KNOWN, FIX KNOWN

**A3GC L3** — NOT A RESULT. Complete (rc=0, End, Time 6000 = endTime), CD 0.0297798,
CL 0.3033918, but p stalls at 2.29e-05, 22.9x above its 1e-06 floor.
**CAUSE (controlled experiment, both cases on disk):** the anchor above is the
SAME c2 surface with **64** wall-normal layers and converges to 3.744e-07; L3 is
the same surface with **16** layers and stalls. `fvSolution` byte-identical.
PREREG Sec.2.6 pins `s0`=1e-4 and `marchDist`=12.0, so layer count alone sets the
growth ratio: **r = 2.0880 (L3), 1.4006 (L2), 1.1674 (anchor)** — and the three
levels are therefore **not a geometrically similar family**, which is a structural
defect in the registered triple independent of any stall.
**FIX: 64 layers, never 16; surfaces c0/c1/c2 only (Sec.2.4 excludes c3 — it
collapses the TE to zero thickness, a different body).** Second lever, measured
next door in A2/D6RF10: `SIMPLEC + nNonOrth 12 + relax_p 0.70` gave a binding
field PASS; A3GC runs `nNonOrth 0` and relax_p 1.0 on a 72 deg mesh.

## BLOCKED

**D8G (A6 grid triple)** — grading-path repair DENIED TWICE by the permission
system (Security Weaken). A path needing no denied change exists (one literal in
`d8g_run_arm.sh:222`'s `cap_core_min()`), but it moves a registered cap and needs
a dated addendum. **Next: supervisor ruling + the addendum, or a permission rule
from Sanaa.** No agent's word substitutes for the permission system.

## IN FLIGHT

- **A2/D6RF10 R2** — died `rc=124`, a timeout at **96% of its deadline**, unmeasured
  for three campaigns. Removing that clock kill is compliance with Sanaa's NO-CAP
  ruling (`6f3abf8a3`), not a gate change. **Next: relaunch, grade, done.**
- **Multipoint optimisation** — she asked for it by name; a lane is establishing
  which item has run and driving the closest to completion.
- **A3GC-R2 registration** — parked behind priority 1. Grader diff read and returned
  with three defects (log10 crashes instead of refusing; no planted control on the
  new dense reader; demoted G-RES limb must print RECORDED-NOT-GATED). Recorded in
  `7b7478288`, pick up whenever.


---

# UPDATE 04:10Z — four runs live, one armed. Read this block first.

| case | state | next action |
|---|---|---|
| **A3GC-AR1** (M6, 399,360 cells, np=4) | **RUNNING, CONVERGED.** Time 1700/6000, p = **3.7287e-07** against a 1e-06 gate — reproduces the validated anchor's 3.744179e-07. 74 core-min. Frozen `3d416043b`. | let it reach endTime 6000 (rule 4), grade with `a3gc_grade.py` md5 `73dbe368…` UNCHANGED, then render |
| **D6R2** (A2 wing, **3D transonic MULTIPOINT OPT** — the one Sanaa named) | **RUNNING CLEAN.** Time 800, 120.7 core-min, **0 primal failures**. Frozen `17eb2a260` at 03:33:00Z vs arm age datum 03:36:01Z. Lands ~12:00Z. | grade on the frozen path; `d6r2_verdict_bounds.sh` appends the two charter limbs into the comparator's own block |
| **D6RF11** (A2 FD probe under the R3 config) | **FROZEN `e21e748b2` (grader in the SAME commit), ARMED, HOLDING** on AR1's pid 2766682 being gone — a process, not a clock. Zero core-min burned. | fires automatically when AR1 clears |
| **A3GC L2** | running, Time 900/6000, p flat ~1.0e-03 vs a 1e-06 floor | let it land; predicted to miss its floor |
| **A3GC L1 stage 1** | running, pyHyp extrude, 128.7 core-min, log block-buffered (`LOG-FROZEN-BUT-CPU-BUSY-NOT-A-STALL`) | let it finish |
| **SO3** (A1 NACA0012 multipoint) | **COMPLETE, PASS, DEMO SHEET BUILT.** 2D. | **nothing. Do not re-run it.** |

## The two findings that outrank the runs

1. **A3GC's stall was the wall-normal growth ratio.** 16 layers force r = 2.0880 and the primal freezes at 2.29e-05; the **same surface** at 64 layers (r = 1.1674) converges to 3.73e-07. Identical `fvSolution`, and **identical checkMesh metrics to every printed digit** — max AR 222.3549, max non-orth 61.1581, max skewness 1.4408. **`checkMesh` is structurally blind to this**: it never reports expansion ratio.
2. **The 3D adjoint ladder has ONE blocker** (`docs/dafoam/ADJOINT_BLOCKER_ONE_ROOT_CAUSE_2026-09-12.md`, `ff2821356`): the primal plateaus **1.32× above its own accept floor**, so no FD sample can be taken, so **no 3D gradient here is a result**. Fix measured by D6RF10-R3. **D6RF11 is the run that would produce this territory's first 3D FD row.**

## Standing refusals — do not quietly undo these

- **Never loosen `primalMinResTolDiff`.** It clears the floor by moving the floor. Refused four times here.
- **Never build an A3GC family on the `c3` surface.** §2.4: it collapses the TE to zero thickness — a different body.
- **Never adopt a run into a family frozen after it started** (rule 2).
- **D6R2 and D6RF11 are PATCHED ROW ONLY** and their gradients are **unverified** — not verdicts *about DAFoam* (charter two-row rule + FD bright line).

## Blocked on Sanaa

**D6RF10 R2** — one diff raising a cap 96→300 core-min and adding an opt-in re-fire root. Two agents refused under two different classifier reasons. Work preserved modified-and-unstaged at `cases/dafoam/ladder-a/A2/curriculum_D6RF10/{PREREGISTRATION.md, d6rf10_run_arm.sh, d6rf10_autograde.sh}`. **D8G** — same shape, denied twice.
