# A2-GC — MACH Tutorial Wing grid convergence — PRE-REGISTRATION (frozen, NOT launched)

Filed 2026-09-01, dafoam lane, against Sanaa's SANAA-DIRECT of 2026-09-01T1545Z
(`etc/sessions/2026-09-01T1545Z_sanaa_convergence_prerequisite_doctrine.md`),
§0 (the automatic convergence study, lab-wide doctrine) and §5 bullet 5:

> *"Convergence study for the wing: build L2 (~100k) and L3 (~300k) from the same
> script as the 38k baseline; CD at fixed CL on all three; p and GCI; gradient
> verification repeated on L2. The optimization result carries the band. This is
> hours of compute, not minutes; run it."*

**NO COMPUTE HAS BEEN SPENT ON THIS ITEM AND NONE WILL BE UNTIL THE SUPERVISOR
GIVES THE LAUNCH GO.** The run root asserted absent in §9 does not exist at
freeze time, and the absence was read against a positive control.

**Nothing in this item is filed, sent, uploaded, registered, posted or commented**
(`CLAUDE.md` rule 7).

---

## 1. Ground truth established before anything was designed

The supervisor's brief required the baseline be established, not assumed. It was.

| claim | verified | source |
|---|---|---|
| the "38k baseline" is the A2 MACH Tutorial Wing at **38,304 cells** | yes | `cases/dafoam/ladder-a/A2_mesh_time.json` (`measured_cells: 38304`); `verification/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md:214`; `drive_actd_demo_mode.py:229` asserts `"38304 cells"` on the Act D screen |
| a **single parametric script** builds it | yes | the tutorial's `preProcessing.sh` -> `cgns_utils coarsen` -> `genWingMesh.py` (pyHyp) -> `plot3dToFoam` -> `autoPatch` -> `createPatch` -> `renumberMesh` |
| the pipeline is **reproducible** | yes | D14M rebuilt it and graded `PASS` on identity, non-ortho, skew and reproduction (`cases/dafoam/ladder-a/A2/curriculum_D14/RESULTS.md`) |
| the mesh decomposes as **1008 surface faces x 38 cell layers** | yes | `logMeshGeneration.txt` in D14M's run root: `Total Faces: 1008`, pyHyp `N: 39`, `Mesh region0 size: 38304`. 1008 x 38 = 38,304 exactly |
| the case is **wall-modelled, not wall-resolved** | yes | y+ min/max/mean **68.79 / 1266.55 / 321.95** (`cases/dafoam/PROOF.md:2523`) |
| the schemes are **NOT uniformly second order** | yes | `system/fvSchemes`: `div(phi,U)` is `linearUpwindV` (2nd), but `div(phi,e)`, `div(phi,h)` and **`div(phi,nuTilda)`** are `bounded Gauss upwind` (**1st**) |

### 1.1 The finding that constrains the whole study: the refinement ratio is quantized

`cgns_utils coarsen` **halves** and `cgns_utils refine` **doubles** along i/j/k;
neither accepts an arbitrary ratio (`cgns_utils refine --help`: *"Refine a grid
uniformly"*, `--axes` selects axes, not a factor). Probed read-only against
`dafoam/opt-packages:latest` on 2026-09-01; no solver ran.

Surface-mesh node counts across the ladder, read from the files themselves:

| surface op | total nodes | implied faces |
|---|---|---|
| `coarsen` x1 (what the baseline ran) | 1,215 | 1,008 (confirmed in the pyHyp log) |
| as downloaded | 4,437 | 4,032 |
| `refine` x1 | 16,929 | 16,128 |

Node ratios 3.65 and 3.81 approach 4 from below exactly as an exact factor-4 face
refinement with duplicated block-interface nodes must.

**Consequence, stated plainly because it changes what Sanaa asked for.** From the
same script the achievable uniform refinement ratio is a **power of 2**. r = 2.000
is the only value inside her band [1.5, 2.0]. The reachable levels containing the
38,304-cell baseline are **4,788 / 38,304 / 306,432 / 2,451,456**. **There is no
~100k level on this ladder.** Her "~300k" target is met almost exactly (306,432);
her "~100k" is not reachable at r in [1.5, 2.0] without either a non-uniform
refinement (which her own §0 forbids) or a different surface generator (which
"the same script" forbids). This item takes the r-band as binding and reports the
cell counts that follow, rather than hitting the cell counts and breaking the band.

---

## 2. The family — frozen in `a2gc_levels.json`

md5 **`5bfefe8bc9b6ef3324efcc795d5b23ab`**.

| level | surface op | faces | pyHyp `N` | cell layers | cells | `s0` | role |
|---|---|---|---|---|---|---|---|
| L0 | `coarsen` x2 | 252 | 20 | 19 | 4,788 | 2.0e-3 | reserve, not graded |
| **L1** | `coarsen` x1 | 1,008 | 39 | 38 | **38,304** | 1.0e-3 | coarse; **IS the published baseline** |
| **L2** | as downloaded | 4,032 | 77 | 76 | **306,432** | 5.0e-4 | middle; gradient verification here |
| **L3** | `refine` x1 | 16,128 | 153 | 152 | **2,451,456** | 2.5e-4 | fine |

**r = 2.000 exactly in every direction.** `marchDist = 300.0` is identical on
every level. Exactly two integers change per level (the `cgns_utils` op and
pyHyp's `N`) plus `s0` scaled by 1/r — that is the whole difference, and
`run_a2gc.sh` applies it with `sed` on the one generator file.

**Similarity is asserted, not assumed** (the F28 lesson): consecutive cell-count
ratio 8.000, face ratio 4, layer ratio 2, `s0` ratio 2, identical `marchDist`.
`a2gc_grade.py` refuses a level whose **measured** cell count differs from the
predicted one — that row becomes `NOT A RESULT` with the reason "the family is
not similar".

**One similarity subtlety recorded before the run, because a naive check would
get it backwards.** pyHyp's reported *Grid Ratio* is **not** expected to be
identical across levels, and a similarity test demanding that would be wrong.
Holding `marchDist` fixed while halving `s0` and doubling the layer count means
each cell splits in two, driving the geometric growth ratio g -> ~sqrt(g):
**1.3562 measured at L1, ~1.165 predicted at L2, ~1.079 at L3.** What must hold
is the same topology reaching the same `marchDist` with a layer count scaled by
exactly r. F28's defect was an **unscaled layer count and a cell-volume jump**,
not a graded growth ratio changing under refinement. Max cell-to-cell volume
growth is measured and reported per level regardless.

---

## 3. The graded quantity, and how the trim is done

**CD of the BASELINE wing (twist = 0, shape = 0) at fixed CL = 0.5**, on all
three levels.

**Fixed CL, not fixed alpha.** Incidence is the trim variable —
`patchV[1]`, the angle of attack — trimmed by the case's **own** routine,
`optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"],
targets=[0.5], designVarsComp=[1])` (`runScript_AeroOnly.py:241`). That is the
same routine that produced the published lift-matched baseline and the A2
decomposition's row `B1`, which it trimmed to `|CL - 0.5| = 5.29e-07`.

The AoA at which CL = 0.5 is reached **will differ between levels**. That is
expected and correct: at fixed lift, incidence is a solved-for output, not an
input. It is reported per level.

**Trim tolerance: |CL - 0.5| <= 5e-4 per level.** A level that misses it is
**`BLOCKED`** and reported as such — never estimated, never interpolated.

**Geometry control (rule 3, geometry side).** The driver block reads `twist` and
`shape` back out of the problem and **raises** if either exceeds 1e-12. A study
of the baseline wing that silently ran the optimised wing would be a wrong answer
that looks right.

---

## 4. GATE I — the iterative-convergence clause, as a gate and not a note

Sanaa's §0 clause 2, which she names as the one most often skipped:

> *"the iterative change in the graded quantity must be at least 10x smaller than
> the difference between consecutive mesh levels. If it is not, the observed order
> is noise, not discretisation."*

Registered operationally:

- **delta_iter(level)** = max - min of CD over the **last 20% of iterations** of
  that level's trimmed primal.
- **Delta_mesh(level)** = the smaller of the |CD| differences to its adjacent
  level(s).
- **GATE I: Delta_mesh / delta_iter >= 10.0**, reported explicitly per level.
- A level failing GATE I makes the observed-order row **`NOT A RESULT`** —
  "iterative noise, not discretisation" — whatever p says.

**Residual target 1e-8**, and the metric is named precisely because the obvious
choice is the wrong one. `GC_RESID` reports the worst **`initRes`** across the six
transported equations (`U0 U1 U2 he p nuTilda`) on the final primal iteration.
**`initRes` is the nonlinear residual — the quantity `primalMinResTol = 1.0e-8`
is compared against. `finalRes` is that iteration's linear-solve residual and is a
different quantity.** Both are recorded; **the gate is on `initRes`**. This
matters for reading the existing record: the A2 decomposition's reported "worst
final residual 4.15e-07 to 6.02e-07" are `finalRes` values and are **not**
evidence that those primals converged to 5e-7. The parser is the one already
proven on that run (`cases/dafoam/grade_a2_decomposition.py:32-34`).

**A missing history is not a satisfied gate.** If `cd_history.json` is absent or
empty, `delta_iter` is unmeasured and GATE I is `PENDING`, never passed. And
**G-HIST**: the history's last sample must equal the level's reported CD to 1e-6
relative, or the history is discarded — a series on a different scaling would
corrupt the GATE I ratio silently.

---

## 5. Observed order, GCI, and the acceptance band

Order of operations is fixed by `CLAUDE.md` rule 5 and is enforced in code:

1. **Classify the triple first** — `CONVERGING` / `DIVERGENT` / `STAGNANT` /
   `OSCILLATORY` / `EXACT`. A non-`CONVERGING` triple is **`NOT A RESULT`**
   whatever its value, with the values printed beside it.
2. **No GCI is quoted when the three values are not monotone.**
3. Only then p against its band, with **GCI at Fs = 1.25**.

Because r is **constant** at 2.000 by construction, the closed form applies and
no fixed-point iteration is needed: p = ln|eps_21/eps_32| / ln r.

**Acceptance band: p in [1.5, 2.5]**, exactly as Sanaa set it in §0 clause 3.
It is registered as she wrote it and is **not** silently widened to suit this case.

### 5.1 A competing prediction, registered before any compute

**I predict p will land BELOW 1.5, most likely in 1.0–1.4**, because
`div(phi,nuTilda)` and `div(phi,h)` are **first-order upwind** and the turbulent
viscosity field feeds CD directly. The scheme set is mixed, so the formal order of
CD on this case is bounded below by 1 and is not cleanly 2.

If that happens it is a **`GATE FAIL`** against the registered band, the §0 step-4
escalation runs in full, and the scheme order is the **first-ranked** candidate
cause — **named here, before the solver starts, so it cannot be offered afterwards
as an explanation invented to fit the answer.** The second-ranked candidate is the
wall-treatment regime (§6). If p lands inside [1.5, 2.5] this prediction is a
**miss** and is recorded as one.

The honest remedy if the schemes are confirmed as the cause is a scheme-uniform
re-run as a **separate successor item** — it changes the case away from the one
the published numbers belong to, so it is not an edit to this one.

---

## 6. Wall treatment — what actually binds, and the registered risk

Sanaa's §0 clause 1 ends *"y+ stays under 1 on every level **where the case is
wall-resolved**"*. **This case is wall-modelled** (y+ mean 321.95 measured), so
that clause does not bind and y+ gates nothing here. y+ is measured and reported
on every level anyway; it is `a_zero_here_could_pass_a_gate: false` in the birth
register precisely because nothing turns on it.

**What binds instead is wall-treatment REGIME consistency across the family**,
because a family whose wall treatment changes character between levels cannot
produce a clean observed order.

| level | y+ min | y+ mean | y+ max | status |
|---|---|---|---|---|
| L1 | 68.79 | 321.95 | 1266.55 | **measured** (`PROOF.md:2523`) |
| L2 | ~34.4 | ~161 | ~633 | predicted (y+ falls by r) |
| L3 | ~17.2 | ~80.5 | ~317 | predicted |

**Registered risk: L3's minimum y+ is predicted at ~17, inside the buffer layer.**
The case uses Spalding's law (`nutUSpaldingWallFunction`), a single smooth formula
deliberately valid across all y+ regimes with **no hard regime switch**
(`PROOF.md:981-982`) — which is why this is a disclosed risk and not a
disqualification. It is the **second-ranked** candidate cause if p misses.

---

## 7. Gradient verification on L2 — registered with a falsifiable prediction

Sanaa asks for gradient verification repeated on L2. L2 is 306,432 cells.

The lab's **measured** adjoint memory law, fit within one controlled family
(identical surface mesh, only extrusion count varying; measured at 21,840 /
42,120 / 79,560 cells), is

> **memory (MiB) = 1.2125 x cells^0.8485**, R^2 = 0.9992
> — `cases/dafoam/ADJOINT_MEMORY_ENVELOPE.md:427`

| cells | extrapolated adjoint peak |
|---|---|
| 38,304 (L1) | **9.2 GB** |
| 306,432 (L2) | **53.5 GB** |
| 2,451,456 (L3) | 312 GB |

The box has **30 GB total, ~28 GB MemAvailable**.

**REGISTERED PREDICTION: the L2 adjoint will exceed available memory and the
gradient verification on L2 will be `BLOCKED`.** This prediction is registered
rather than acted on, and **the attempt is still made**, because refusing Sanaa's
requirement on an extrapolation would be weaker than testing it:

- **Stage M anchors the law to A2's own family first** — one `compute_totals` at
  L1 (38,304), peak RSS measured from the cgroup. If A2's measured point sits well
  below the law's 9.2 GB, the law is refit on it and L2 is re-predicted.
- The L2 attempt is then made, capped at 120 core-min. **If it completes, my
  extrapolation was wrong and that is the finding I report.**
- **If it is BLOCKED**, the registered fallback is gradient verification repeated
  on **L1 at 1e-8 `initRes`** — which the published G-03 row was **not** — reported
  as a **partial** satisfaction of Sanaa's requirement with the shortfall named.
  **It is not silently substituted for what she asked for.**

---

## 8. Escalation when p misses the band — §0 step 4, including what this box cannot do

| step | registered action |
|---|---|
| (a) re-check iterative convergence on the finest level | re-run L3 with the iteration cap doubled; re-measure delta_iter and the GATE I ratio |
| (b) verify similarity | the §2 table (cell/face/layer/`s0`/`marchDist` ratios), the growth-ratio note, the y+ regime table, and the max cell-to-cell volume-growth histogram — **the F28 lesson** |
| (c) a fourth, finer level at the same r | **L4 = 19,611,648 cells. REGISTERED IN ADVANCE AS `BLOCKED` ON THIS INSTANCE** — 64x L3's memory and wall time on a 16-core / 30 GB box |
| (d) repeat up to two more levels | **likewise `BLOCKED`** |

**This is registered before the run rather than discovered after it, because a
promise the box cannot keep is worse than a disclosed limit.** The only other
level available is **L0 = 4,788**, which shifts the window **coarser** — the
opposite of what §0 step 4(c) asks for. If it is used, it is reported as a
**disclosed deviation from §0**, never presented as satisfying it.

---

## 9. Instrument, frozen; run root asserted absent

| file | md5 |
|---|---|
| `cases/dafoam/a2gc_grade.py` | **`3b1a6e7dcbdecf8676ac95e0cef70ea4`** |
| `cases/dafoam/a2gc_levels.json` | **`5bfefe8bc9b6ef3324efcc795d5b23ab`** |
| `cases/dafoam/a2gc_driver_block.py` | **`ecd5d4eb9b71e628658c52e305276d5d`** |
| `cases/dafoam/run_a2gc.sh` | **`bd2e764ba92d7707539c900c7e1a91f6`** |
| pristine `runScript_AeroOnly.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` (`PROOF.md:2512`) |

`run_a2gc.sh` asserts every one of these before any solver starts and exits 2 on
a mismatch. The level driver is the **pristine script plus a disclosed appended
block**; `driver_vs_pristine.diff` is written beside every level.

> **The run root `/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence` DOES
> NOT EXIST at freeze time.** Read 2026-09-01, and the reader was shown able to see
> a directory that does exist (`/home/ubuntu/certonomous-runs/A2-mach-wing`)
> — a planted positive control on the absence check itself.

`run_a2gc.sh` re-asserts the level directory absent immediately before launch and
refuses (exit 2) if it exists (rule 4 guard).

**Placement (registered):** `cpuset 4-15` (12 of 16 cores, leaving 0-3 for peers),
`np = 12`. The launcher **refuses (exit 3)** if `MemAvailable` is below
`MEM_LIMIT + 3 GB`, or if any `a2gc_` container is already running.

**`MEM_LIMIT` is sized from measurement, not inherited.** The inherited `20g` is
not used. Stage M measures the L1 primal's peak RSS from the cgroup; each later
stage's limit is set from that anchor. The registered starting values are L1 `6g`,
L2 `14g`, L3 `26g`, and **Stage M's measurement replaces them before L2 or L3
launches**.

---

## 10. Cost — rule 12, with measured and extrapolated figures separated

**MEASURED basis:**

| quantity | value | source |
|---|---|---|
| primal at 38,304 cells, np=4 | **13.6–15.4 s** solver time each (~0.97 core-min) | `A2_DRAG_DECOMPOSITION_PREREGISTRATION.md` §R6; `/home/ubuntu/certonomous-runs/ACTD-a2-decomposition/cost.txt` (`wall_s=208 core_min=13.87`, 14 primals) |
| mesh build at 38,304 | 0.533 s pyHyp; 8.02 s full pipeline | D14M `logMeshGeneration.txt`; `ladder-a/A2_mesh_time.json` |
| trim cost | ~4 primals (row B1) | same run |
| adjoint memory law | MiB = 1.2125 x cells^0.8485, R^2 0.9992 | `ADJOINT_MEMORY_ENVELOPE.md:427` |

**EXTRAPOLATED, labelled as such.** The softest figure is the cost of reaching
`initRes` 1e-8, which no run on this case has yet done — **Stage M measures it,
and it is the reason Stage M exists.** Assumed 3x the iteration count of the
~5e-7 `finalRes` runs; per-level factor 16 (cells x8, iterations x2).

| stage | core-min | cap | basis |
|---|---|---|---|
| Stage M (L1 to 1e-8 + one `compute_totals` for the memory anchor) | 10 | **30** | measured primal x extrapolated iteration factor |
| L1 trim + primal | 15 | **60** | extrapolated |
| L2 mesh + trim + primal | 242 | **500** | extrapolated |
| L2 adjoint attempt (predicted to be BLOCKED) | 40 | **120** | extrapolated |
| L3 mesh + trim + primal | 3,860 | **6,000** | extrapolated |
| **item total** | **~4,167** | **item ceiling 7,000** | |

**An overrun STOPS the run; it does not get a new budget.** `run_a2gc.sh`
converts each cap to a wall-clock `timeout` at np=12 and writes
`overrun=YES-RUN-STOPPED` into the stage's own `cost.txt`.

Wall time at np=12: **~5.8 hours** for the whole item — consistent with Sanaa's
"hours of compute, not minutes".

**Dollars DERIVED, NOT MEASURED:** 4,167 core-min = 69.5 core-h -> **$3.56**;
ceiling 7,000 core-min = 116.7 core-h -> **$5.99**. At $0.0513/core-h
c7a.4xlarge, **reported-by-owner** (Sanaa 2026-08-21/22) — the box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **GPU: 0 GPU-h**, none registered
and none used.

Rule 12's calibration clause applies at completion: predicted against actual, in
core-minutes, with the ratio stated and the gap attributed, landing as a row in
`docs/COST_CALIBRATION.md`.

---

## 11. Planted-zero controls — rule 3

`a2gc_grade.py` runs a **birth register** at grade time, before anything is read.
Every reader is pushed a known planted perturbation **through the real reader
function** and must be shown able to see it; a reader that cannot **refuses,
exit 2**, and the register is emitted into the graded JSON.

**Demonstrated 2026-09-01 (`a2gc_grade.py --selftest`, rc 0): 9 readers declared,
9 born, 7 of them zero-passing** — `read_cd`, `read_cl`, `read_cells`,
`read_residual`, `read_vol_growth`, `read_iter_delta`, `read_mesh_delta`; y+ and
peak-RSS gate nothing and are marked as not zero-passing.

**The control on the control.** A register never shown able to refuse is not
evidence either. Each of the 9 readers is blinded in turn to a zero-returning stub
and the register **must** refuse on that reader: **demonstrated, 9 of 9.**

The highest-value plant is `read_iter_delta`: a `delta_iter` stuck at zero would
pass GATE I trivially and hand back an observed order that is pure iterative noise
dressed as discretisation — exactly the failure §0 clause 2 was written against.

**The grader was also exercised end to end on eight synthetic run roots before
freezing** (p=2 tight -> `PASS`; p=1.3 tight -> `GATE FAIL`; p=2 with loose
iteration -> `NOT A RESULT`; oscillatory -> `NOT A RESULT` with no GCI quoted;
history missing -> `NOT A RESULT`; history on a wrong scaling -> `NOT A RESULT`;
residual 5e-7 -> `GATE FAIL`; wrong cell count -> `NOT A RESULT`). The Roache math
was verified against analytic triples, recovering p = 1.000, 1.300 and 2.000
exactly and classifying all five non-converging cases correctly.

### 11.1 Composition — and a defect deliberately not inherited

`compose_row` returns **both** `verdict_before_ceiling` and the capped `verdict`.
`compose_item` composes from **`verdict_before_ceiling`**, so an item-level
ceiling can actually fire.

This is the second defect measured in D19M's `compose_item` on 2026-09-01: there
`compose_row` returned the already-capped token and `compose_item` read it, so the
item-level ceiling was structurally unable to fire. **It is not inherited here.**
A fired row ceiling is separately folded in as a **floor**, so the item can never
read less severe than a row whose ceiling did fire.

---

## 12. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`
only. **The band goes on every number** (§0 clause 5). A gate can only turn a
`PASS` or `GATE FAIL` **into** a `NOT A RESULT`, never the reverse.
