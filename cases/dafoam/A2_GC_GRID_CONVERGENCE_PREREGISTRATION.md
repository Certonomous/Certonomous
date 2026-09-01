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

---

# AMENDMENT 1 — 2026-09-01T16:24:47Z — PRE-COMPUTE, before the solver starts

**Version 1.0 -> 1.1. Lines whose number changed above this section: 0.**

**The condition, and how it was checked.** This amendment is legal because **no
compute has been spent on this item**. Checked at 16:24:47Z: the run root
`/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence` **does not exist**,
and a search for `*A2*GC*` and `*a2gc*` under `certonomous-runs/` returns **zero
directories**. The absence was read against a positive control — the reader was
shown able to see `/home/ubuntu/certonomous-runs/A2-mach-wing`, which does exist.
Gates, thresholds, caps and the p-band of §1-§12 are **unchanged** by this
amendment; it adds two labellings and supersedes one md5.

## A1.1 The supervisor's condition 1, answered honestly rather than assumed

The supervisor required written confirmation that a `BLOCKED` L3 cannot yield a p,
and required me to say so if it was **not** already registered rather than treat
his sentence as the registration. **Three of the four clauses were already
registered and enforced; the fourth was not.**

| clause | status at v1.0 |
|---|---|
| no p is reported when a level does not stand | **REGISTERED** — the order block is guarded on all three levels standing |
| no GCI is quoted | **REGISTERED** — GCI is computed only inside the monotone branch |
| no fall-back to two levels | **REGISTERED** — structurally; no two-level path exists anywhere in the grader |
| a failed L3 labels the triple **`BLOCKED`** | **NOT REGISTERED** — v1.0 would have labelled it `NOT A RESULT` |

**Registered now, at v1.1:**

- A level that fails for a **RESOURCE** reason is **`BLOCKED`**, not
  `NOT A RESULT`. The two are different findings: `BLOCKED` says the box could not
  run it; `NOT A RESULT` says it ran and the answer does not stand. The
  classification is read from the stage's own artifacts — `overrun=YES-RUN-STOPPED`
  in its `cost.txt` (rule 12: an overrun stops the run, it does not get a new
  budget), or rc 137/143 or a kill line in its container log — **not inferred from
  rc alone**.
- When fewer than three levels stand, the grader emits an explicit
  **`order/triple`** row carrying `BLOCKED` if any member was blocked, `PENDING` if
  members simply never ran, else `NOT A RESULT`, with **no p and no GCI**.

**Demonstrated before this amendment was committed**, on synthetic run roots: L3
OOM-killed -> item `BLOCKED`, p `None`, GCI `None`; L3 cap overrun -> item
`BLOCKED`, p `None`, GCI `None`; L3 never ran -> item `PENDING`, p `None`, GCI
`None`; all three levels standing -> item `PASS`, p recovered as 2.000.

## A1.2 The supervisor's condition 2 — the p-band framing, registered in advance

**The band stays at p in [1.5, 2.5].** It is not widened. Choosing `[0.5, 1.5]`
after reading the schemes would be selecting the band that makes this case pass,
which is the exact thing a pre-registration exists to prevent.

**Registered in advance, so it is not argued afterwards:** if p lands in 1.0-1.4
as §5.1 predicts, **that result is a finding about the BAND'S KEYING, not about
the wing.** Sanaa's §0 keys the band to *"the scheme's formal order"*; `[1.5, 2.5]`
is her parenthetical example **for a second-order scheme**. This scheme set is
**mixed** — `bounded Gauss upwind` on `nuTilda` and `h` is first order — so a p
near 1.2 would be the wing converging at the order its own numerics actually
carry, not the wing failing to converge.

**This framing must travel with the number.** A `GATE FAIL` on this band reported
without it will be read as "the wing failed its grid convergence study", which
would be false. The open doctrine question — *for a mixed-order scheme set, which
formal order keys the band* — is on Sanaa's desk via the supervisor. **The run does
not wait on her answer**, and no agent may resolve it by moving the band.

## A1.3 Superseded md5

The grader changed to carry A1.1. §9's row for it is **struck and replaced**;
every other row in §9 stands unchanged.

| file | md5 |
|---|---|
| ~~`cases/dafoam/a2gc_grade.py` — `3b1a6e7dcbdecf8676ac95e0cef70ea4`~~ **STRUCK** | superseded by A1.1 |
| `cases/dafoam/a2gc_grade.py` (v1.1) | **`f360f6b0cfbaee7029775ad8453c13f5`** |

The birth register is unchanged and was re-run after the edit: **9 declared, 9
born, 7 zero-passing, refusal path 9 of 9.**

---

# AMENDMENT 2 — 2026-09-01T16:27:34Z — PRE-COMPUTE, driver repair

**Version 1.1 -> 1.2. Lines whose number changed above this section: 0.**

**Condition, and how it was checked.** Still **no compute spent**. Run root
`/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence` checked **absent** at
2026-09-01T16:27:34Z, read against the same positive control as Amendment 1. **No gate, threshold,
cap, band or label changes.** This amendment records a repair to the launcher and
re-pins its md5.

**Three defects found by dry-running the launcher against a stubbed `docker` in
scratch, before any solver ran.** The rule-4 guard refuses a level directory that
already exists, so a buggy first launch would have blocked its own retry — which
is why the dry run happened first.

1. **`rc` would have read 0 for every outcome.** `solve.sh` ended on an
   `echo`, so the script's exit status was the echo's, not `mpirun`'s. This is
   the same class of trap as `setsid timeout cmd` returning 0 regardless. A
   diverged or OOM-killed primal would have been recorded `rc=0` and graded as a
   standing value. **Repaired:** `rc` is captured next to `mpirun` and the
   script exits with it.
2. **The container name was invalid.** `--name "a2gc_${LEVEL}_\$\$"` produced a
   literal `$$`, which Docker rejects — every launch would have failed, and the
   placement gate that greps for a running `a2gc_` container would have been
   testing a name that never existed. **Repaired.**
3. **The peak-RSS read depended on the cgroup version mounted.** It read
   `/sys/fs/cgroup/memory.peak` (v2 only). Peak RSS is the anchor Stage M exists
   to measure and the basis of the L2 BLOCKED prediction in §7, so a silent zero
   there would have cost the item its memory anchor. **Repaired:** an in-container
   sampler sums `VmRSS` across all processes every 2 s and keeps the maximum,
   independent of cgroup layout.

The container stage is now written to `stage.sh` on disk rather than squeezed
into a `bash -lc` string, so rc is captured beside the command that produced it.

**One disclosure that is not a defect.** Levels run at **np = 12** (cpuset 4-15),
while the published baseline ran at **np = 4**. Consistency ACROSS the three levels
is what an order study requires, and it holds. But this family has a **known
decomposition sensitivity** (`DEFECT_REACH_decomposition_cases.md` names A2 at
38,304 cells, scotch vs simple at np=4), so **L1's CD is reported against the
published np=4 value 0.02962051221 as a disclosed reproduction check, not assumed
to match.** Any difference is reported, never absorbed.

## Superseded md5

| file | md5 |
|---|---|
| ~~`cases/dafoam/run_a2gc.sh` — `bd2e764ba92d7707539c900c7e1a91f6`~~ **STRUCK** | superseded by this amendment |
| `cases/dafoam/run_a2gc.sh` (v1.2) | **`f3baba360a50c8b7592d0a50142d5e28`** |

---

# RESULTS ADDENDUM — 2026-09-01T16:52:14Z — after first compute

**Version 1.2 -> 1.3. Lines whose number changed above this section: 0.**
Gates, thresholds, caps, the p-band and every label of §1-§12 are **UNCHANGED**.
This addendum records measurements and **alters nothing that could be graded**.

## R1. L1 — measured, and reproduced bit-identically on two independent runs

| quantity | L1 measured (np=12) | reference | agreement |
|---|---|---|---|
| cells | **38,304** | 38,304 predicted | **exact** — similar at L1 |
| CD at fixed CL | **0.02961982052** | 0.02962051221 published (np=4) | **0.00234 %** |
| CL | **0.4999996084** | 0.500 target | \|CL-0.5\| = **3.92e-07** vs 5e-4 -> trim **PASS** |
| AoA (solved-for) | **4.326120747 deg** | 4.32612781 deg published | **7.06e-06 deg** |
| y+ min/max/mean | **67.17 / 1281.52 / 321.63** | 68.79 / 1266.55 / 321.95 recorded | confirms wall-modelled |
| worst `initRes` | **7.1566e-06** | registered gate 1e-8 | **GATE FAIL** (see R4) |
| worst `finalRes` | 4.2364e-07 | — | the linear-solve residual, not the gate |

**Reproduction control, unplanned and free:** runs `L1_attempt3_CAPSTOP` and `L1`
returned CD, CL and AoA **identical to every printed digit** — 0.02961982052 /
0.4999996084 / 4.326120747. Two independent container launches, same answer.

## R2. The cost anchor was in the WRONG UNIT, and the correction is 20x

An earlier reading of this run divided cumulative `ExecutionTime` by a primal
count and reported "38.1 core-min per cold primal". **That is wrong and is
recorded as wrong.** `Time = 1` occurs **six** times in L1's log — six primal
solves — and `ExecutionTime` is a **cumulative process clock that never resets
across them**. Dividing it by a primal count produces a number that means nothing.

**The transferable quantity is s/SIMPLE-iteration**, measured per solve:

| solve | iterations | ExecutionTime span | s/iter (np=12) | core-s/iter |
|---|---|---|---|---|
| 1 (cold) | 1000 | 72.26 s | 0.07233 | 0.868 |
| 2 | 1000 | 9.34 s | 0.00935 | 0.112 |
| 3 | 1000 | 9.55 s | 0.00956 | 0.115 |
| 4 | 1000 | 9.44 s | 0.00945 | 0.113 |
| 5 | 1000 | 53.77 s | 0.05382 | 0.646 |
| 6 | 1000 | 29.01 s | 0.02904 | 0.349 |

**Warm steady-state rate: 0.00945 s/iteration at np=12 on 38,304 cells
(0.1134 core-s/iteration)** — solves 2-4 agree to within 2 %. A 1000-iteration
primal is therefore **1.89 core-min**, not 38.

## R3. THE ADJOINT INSIDE THE TRIM IS THE COST DRIVER, AND THE GRADED QUANTITY DOES NOT NEED IT

The primal work in the completing run totalled **54.71 s** of `ExecutionTime`.
The run nonetheless hit a 450 s wall cap, **inside an adjoint GMRES solve**
(`Solving Linear Equation... 272.79 s`, `Main iteration 100 KSP Residual norm
3.399e-07 318.01 s`), with 12 Jacobian-coloring mentions in the log.

`optFuncs.findFeasibleDesign` is a **gradient-based** trim: it converged in 2
iterations and the adjoint it needs then dominates the level's wall time.

**The graded quantity — CD at fixed CL — does not require an adjoint.** A
primal-only secant trim on incidence obtains it in ~4 primals. On the R2 rate
that is **~7.6 core-min at L1, ~60 at L2, ~484 at L3**: the whole ladder for
**~550 core-min**, comfortably inside the frozen 7,000 ceiling.

**This changes the standing of the primal-only-trim successor: it is not a
fallback, it is the correct instrument.** It also removes the adjoint from the
critical path, which is the same wall §7 predicted would block L2.

**An earlier projection of ~19,000 core-min for L3 is WITHDRAWN.** It chained the
wrong-unit per-primal rate through a per-level factor and was wrong by roughly
25x. No decision should rest on it.

## R4. What is NOT measured, stated plainly

- **The iterative-to-discretisation ratio (GATE I) is UNCOMPUTABLE from one
  level.** It needs Delta_mesh, which needs a second level. L1's own
  `delta_iter` is measured — **CD swing 3.84e-07 over the last 13 of 66
  evaluations, and bit-identical across the last 5** — but the ratio is not
  reported, and is not guessed.
- **No p and no GCI.** One level stands. Three are the minimum, per §A1.1.
- **L1 did not emit its `GC_RESULT` line**: both completing runs were killed by
  their cap during the post-trim adjoint, after the trim had converged and after
  CD/CL/AoA were printed. The values in R1 are read from the solver's own printed
  output, which is the same source the grader parses.
- **Peak RSS is bounded, not pinned.** The in-container sampler reports
  **11,885 MiB aggregate `VmRSS` summed over 12 ranks, which double-counts
  shared pages**. The trustworthy bound is the container cap: it ran under
  **6g without an OOM kill, so true peak <= 6 GB.** The M6-family law predicts
  **9.2 GB** at this cell count, so **the law OVER-predicts this family by at
  least 1.5x** — L2's 53.5 GB projection is correspondingly softer, though still
  above the ~28 GB available.

## R5. Cost — rule 12 calibration

| attempt | core-min | outcome |
|---|---|---|
| attempt 1 | 0.08 | `set -u` broke the OpenFOAM bashrc — **waste, infrastructure** |
| attempt 2 | 1.76 | mpirun root guard — **waste, infrastructure** |
| attempt 3 | 61.83 | cap-stopped; physics landed |
| attempt 4 | 91.99 | cap-stopped; physics reproduced identically |
| **total** | **155.66** | |

Predicted for Stage M + L1: **25**. **Ratio actual/predicted 6.23x.**
**Waste named separately and never absorbed: 1.84 core-min** (infrastructure).

**Gap attribution, three causes, separated:** (i) the per-primal cost basis was in
the wrong unit (R2) — the dominant cause; (ii) **the adjoint inside the trim was
never costed at all** (R3) — it is most of the wall time and §10 does not mention
it; (iii) 1.84 core-min of infrastructure waste. No contention (box otherwise
idle); the caps fired exactly as registered and stopped the run both times.

Dollars **DERIVED, NOT MEASURED**: 155.66 core-min = 2.594 core-h -> **$0.1331**
at $0.0513/core-h, **reported-by-owner**. **0 GPU-h.**

## R6. Standing

**L1: the graded quantity is measured and reproduced; its registered residual gate
`initRes <= 1e-8` reads GATE FAIL at 7.16e-06.** Per §A1.2's framing and the
supervisor's ruling (d), that is reported **as an instrument-proxy finding**, and
**no gate moves on our reading of her sentence.** L2 and L3 are **not run under
this item.** A2-GC stands at **PENDING for the triple** — one level of three — and
runs no further here.
