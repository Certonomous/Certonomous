# T25R5 — **A LINEAR-SOLVER TUNING PROBE FOR THE T25 COOLANT PRESSURE EQUATION.** PRE-REGISTRATION

**Drafted 2026-09-02 by a heat-transfer `lab-lane`. UNCOMMITTED WORKING DRAFT.
NOTHING HAS BEEN RUN UNDER THIS REGISTRATION. NO SOLVER HAS BEEN LAUNCHED, NO
RANK, NO STAGING.** The next action is the supervisor's diff-read and commit, not
a launch. Until this file is committed it has **no evidentiary content whatever**
(rule 2: the freeze *is* the evidence).

**SCOPE, AND IT IS NARROW.** This registers a probe of the **linear solver
configuration** for `p_rgh` in the coolant region. It changes **no physics, no
mesh, no boundary condition, no time-step schedule, no decomposition, no
convergence criterion, no gate, no threshold, no band, no label and no ceiling**
belonging to T25R4 or any predecessor. §2 states that as an executable check, not
as a promise.

Verdict vocabulary is `CLAUDE.md` rule 1's and is used nowhere loosely.

---

## 0. ⚠ THE STATE THIS PROBE STARTS FROM — **CORRECTED AGAINST THE BOARD, FROM DISK**

Three things the resume board records about T25R4 are **not what the artifacts on
disk say**, and a successor must not inherit the board's version.

### 0.1 `G-P`'s verdict is `NOT A RESULT`. The ladder gate refused at step 1, not step 4.

`verification/runs/T-family/T25R4_MODULE_runs/GP_VERDICT.json` records
`"verdict": "NOT A RESULT"`, `"ratio": null`, and the notes
`P1: rc=124`, `P2: rc=124`, `P3: rc=124` with `48/100`, `41/100`, `43/100`
registered steps. All three probes were **stopped by their registered `timeout`**
(rc 124 is `timeout`'s), none reached its 100 steps.

That is exactly the branch T25R4 Amendment A2.1 registered in advance: *"if any
probe level fails to complete its 100 steps, or its rc is non-zero … `G-P` is
`NOT A RESULT` and the ladder does not launch."*

`ladder_gate_t25R4.py` therefore refuses inside `read_verdict()` — verdict is not
literally `PASS` — and **exits 3 before `price()` is ever called** (verified by
running it read-only: `--run S2` → exit 3, message *"G-P verdict is 'NOT A
RESULT', not PASS"*). **The cost ceiling was never the operative refusal.** The
priced total is a hypothetical the gate never computes.

**And it refused twice, on two different limbs of the same default-deny.** The
six `STATUS.queue.T25R4_*` files record `launcher_rc=3` at 18:24:05Z with
*"G-P verdict artifact … DOES NOT EXIST. Default-deny: the absence of a gate
result is not a pass"* — `GP_VERDICT.json` was not written until 18:43:07Z.
Re-run today, the same gate refuses on the verdict's **value**. **No ladder
compute has occurred:**
`.../T25R4_MODULE_runs/{S1,S2,S3,T2,T4,W30}/` hold staged inputs only —
`0.orig/`, `constant/`, `system/` — with **no `0/`, no time directory, no
`processor*/` and no `log.solve*` in any of the six.**

### 0.2 The hypothetical ladder price is **230,704 core-min**, not 200,212.

Reproduced by hand from A1.1's frozen formula and `GP_VERDICT.json`'s
`s_per_step`:

| run | level | N steps | SWEEP | POINT core-min | CAP (×4) |
|---|---|---|---|---|---|
| S1 | L1 | 11,800 | 1.0 | 1,881.6 | 7,526.4 |
| S2 | L2 | 11,800 | 1.0 | 5,037.8 | 20,151.3 |
| S3 | L3 | 11,800 | 1.0 | 10,453.9 | 41,815.5 |
| T2 | L2 | 23,600 | 1.0 | 10,075.7 | 40,302.7 |
| T4 | L2 | 47,200 | 1.0 | 20,151.3 | 80,605.3 |
| W30 | L2 | 11,800 | 2.0 | 10,075.7 | 40,302.7 |
| **total** | | | | **57,676** | **230,704** |

**×11.535 above the A1.3 ceiling of 20,000 core-min.** ($197.25 derived at
$0.0513/core-h — derived, not measured, `cost_basis = REPORTED-BY-OWNER`.)

**A separate finding, reported and not acted on here:** `GP_VERDICT.json`'s
`s_per_step` values are `ExecutionTime / actual steps` (229.62/48, 525.13/41,
1142.84/43). A1.1 froze `r(L) = ExecutionTime_final(L) / 100`. The grade script's
divisor is the more honest one, but it is **not the frozen one**. It is moot
today because the verdict is `NOT A RESULT` and the field is never consumed — it
would stop being moot the moment a future `G-P` returned `PASS`. **Referred to
the supervisor; this lane does not edit a frozen document.**

### 0.3 ⛔ The mesh-independence the board reports **is an artefact of `maxIter`, and the criterion is still mesh-dependent by ×10.67**

This is the finding that matters most, and it is measured, not argued.

GAMG's `maxIter` is unset in the case and therefore **1000**
(`lduMatrixSolver.C:180`, `lduMatrix::defaultMaxIter`). Measured over the three
probe logs `.../T25R4_MODULE_runs/P{1,2,3}/log.solve.legA`:

| | L1 (16,608) | L2 (37,368) | L3 (84,078) |
|---|---|---|---|
| `p_rgh` solves logged | 1,462 | 1,244 | 1,317 |
| **mean iterations, ALL solves** | **382.92** | **443.58** | **435.04** |
| solves terminating at `maxIter` 1000 | **537 (36.7 %)** | **354 (28.5 %)** | **213 (16.2 %)** |
| median iterations | 32.5 | 256 | 330 |

The board's ratio of 1.16 (`443.58 / 382.92`; the board's quoted *values*
382.9 / 383.6 / 356.7 do not appear in `GP_VERDICT.json`, which carries
382.9145 / 443.5844 / 435.0448) is computed over a population **one sixth to one
third of which is pinned at the 1000-iteration ceiling.** The ceiling is what
makes the three levels look alike.

**Restricted to the solves the criterion could actually be met on** — definition
and its frozen number at §3.2 — the picture inverts:

| feasible-solve population | L1 | L2 | L3 |
|---|---|---|---|
| n (share of all solves) | 931 (63.7 %) | 901 (72.4 %) | 1,111 (84.4 %) |
| **mean GAMG iterations** | **30.96** | **231.76** | **330.29** |
| median iterations | 13 | 133 | 318 |
| median reduction achieved | ×110.3 | ×100.7 | ×100.9 |
| **implied per-iteration convergence factor** | **0.664** | **0.966** | **0.986** |

> **max/min = 330.29 / 30.96 = ×10.67. `G-P`'s registered threshold is 3.0.
> Had the probes run to completion, `G-P` would have been decided on a ratio that
> `maxIter` had flattened.** T25R4's fix cut the T25R3 defect from ×1,233 to
> ×10.67 — a large, real improvement — **and it did not reach the gate it
> registered.**

### 0.4 The stall floor is real, is ~×5,000 above the registered floor, and was already on record

The 1,104 solves that terminate at `maxIter` do not fail randomly. Their final
residuals cluster in a band that is almost a single number:

| | L1 | L2 | L3 |
|---|---|---|---|
| stalled-solve final residual, **full range** | 4.257e-09 … 5.079e-09 | 6.448e-09 … 3.661e-04 | 9.947e-09 … 1.031e-08 |
| **minimum final residual reached by ANY solve** | **4.2567e-09** | **6.4477e-09** | **9.9471e-09** |
| median reduction those solves achieved | ×5.26 | ×11.96 | ×26.96 |
| mean iterations, solves below the floor | **1000.0** | **1000.0** | **1000.0** |

**On all three levels, every single solve whose ×100 target lies at or below the
floor runs the full 1000 iterations — 531/531, 343/343, 206/206. Not a tendency;
a law.**

The floor **scales with the refinement ratio, not with cell count**: measured
×1.44 (L1→L2) and ×1.54 (L2→L3) against a cell-count ratio of ×2.2500 and
`r_eff = 1.5000`. Consistent with a floor set by round-off in a term carrying
1/h (a face flux or gradient); **this lane cannot separate that from the other
candidate mechanisms using the logs alone and does not claim to.**

**L2's wide band is a SECOND failure mode — real, and 1.1 % of one level.**
L2's range runs to 3.661e-04 while L1's and L3's are tight, which raises the
question whether some pinning is genuine non-convergence far from the floor
rather than the floor itself. **Checked, and the answer is quantitative:** taking
"within ×10 of that level's minimum final residual" as the floor band,
**L1 is 537/537 (100 %) in-band, L3 is 213/213 (100 %), and L2 is 350/354
(98.9 %).** The **four** exceptions on L2 have final residuals 8.859e-05 …
3.661e-04, initial residuals 2.244e-02 … 9.305e-02, achieved ×182 median — they
were asked for `p_rghFinal`'s ×1000 and ran out of iterations at ×182 — and
**all four occur at t = 0.02 and t = 0.04, the first two steps of the start-up
transient.**

> **So there ARE two failure modes, and they are not comparable in weight: the
> floor accounts for 1,100 of the 1,104 pinned solves (99.6 %), and
> running-out-of-iterations-far-from-converged accounts for 4 (0.36 %), on one
> level, in the first two time steps.** Recorded at its true weight rather than
> promoted to a co-equal mechanism, and §1.2's single-mechanism reading stands
> for 99.6 % of the pinned population. *(Raised by the supervisor's check-1 read;
> verified by this lane before writing, and its weight is the part that was not
> visible from the band ranges alone.)*

**This floor was already measured and already written down**, in
`docs/campaigns/T-family/T25RF_FEASIBILITY_NOTE.md` §4 (*"GAMG stalls at ~4.4e-9
on this system"*, 266/600 and 608/1200 solves at `maxIter`), and it is quoted in
the comment block of the very file T25R4 registered —
`.../P1/system/coolant/fvSolution:29-36`. T25RF further measured that relaxing
past the floor removed **601,763 GAMG iterations (×24.4)** and changed the
last-sweep `Min/max T` at `Time = 30` by **0.000e+00 K**.

> **T25R4 §1.2 proved its `tolerance 1e-13` floor never binds. It is right, and
> it is the wrong floor.** The binding floor is the system's own ~4.5e-9…1.0e-8,
> four to five orders above the registered one. Setting `relTol 1e-3` on
> `p_rghFinal` places the final-sweep target below that floor for a growing share
> of solves as the field settles — **on all three levels the last observed time
> step has 100 % of its `p_rgh` solves at `maxIter`** (L1 22/22, L2 14/14,
> L3 27/27) — which is precisely the waste T25RF had already removed once.

**None of §0 edits, strikes or amends T25R4. It is a reading of committed
artifacts, filed with its successor.**

---

## 1. THE DIAGNOSIS THIS PROBE TESTS — **the multigrid is not multigridding, and the mesh says why**

Measured from disk, `.../P1/system/coolant/fvSolution:37-49`, byte-identical
across P1/P2/P3 (`md5 e7bc4944caa48d7c3a59f83d7a4e3525` on all three):

```
    "p_rgh.*"  { solver GAMG; smoother GaussSeidel; tolerance 1e-13; relTol 0.01; }
    p_rghFinal { $p_rgh;      tolerance 1e-13;      relTol 1e-3; }
```

**Every other GAMG key is absent, so every other GAMG key is at its v2606
default**, read from source, not recalled:

| key | value in force | source |
|---|---|---|
| `agglomerator` | `faceAreaPair` | `GAMGAgglomeration.C:343` |
| `nCellsInCoarsestLevel` | **10** | `GAMGAgglomeration.C:263` |
| `mergeLevels` | 1 | `GAMGAgglomeration.C` |
| `cacheAgglomeration` | `true` | `GAMGSolver.C:80` |
| `nPreSweeps` | **0** | `GAMGSolver.C:72` |
| `nPostSweeps` | 2 | `GAMGSolver.C:75` |
| `nFinestSweeps` | 2 | `GAMGSolver.C:78` |
| `interpolateCorrection` | `false` | `GAMGSolver.C:81` |
| `scaleCorrection` | `true` (matrix is symmetric) | `GAMGSolver.C:82` |
| `directSolveCoarsest` | `false` | `GAMGSolver.C:83` |
| `maxIter` | **1000** | `lduMatrixSolver.C:180` |

Other equations, same file: `U`,`h`,`k`,`omega` are `PBiCGStab`/`DILU`,
`tolerance 1e-10`, `relTol 0.01`, with `Final` at `relTol 0` (lines 51-63);
`rho` is `PCG`/`DIC` (lines 20-27); the module region is `PCG`/`DIC`,
`tolerance 1e-12`, `relTol 0` (`.../P1/system/module/fvSolution:20-27`). **All
of these are measured at 0.36–1.30 mean iterations per solve on every level and
are not a cost term.** They are not touched by this probe.

### 1.1 What the brief's leading suspect turned out to be

**`nCellsInCoarsestLevel` is not too large — it is 10, the smallest sensible
value.** The hypothesis that "the coarse solve is not actually coarse" is
**refused by the source default**, and this lane records that its own brief's
first suspect did not survive contact with the file.

### 1.2 What the measurement points at instead

The `p_rgh` matrix is symmetric and, with a `fixedValue` outlet
(`.../P1/0/coolant/p_rgh`), **non-singular** — the pure-Neumann pathology is
ruled out.

**The coolant mesh has `Max aspect ratio = 96.62`**
(`verification/runs/T-family/T25R_MODULE_runs/T25R_L2/log.checkMesh.coolant`;
identical to 10 figures on the L1 log, so the family holds anisotropy fixed under
refinement), with `Mesh non-orthogonality Max: 0`.

That is a strongly anisotropic Poisson operator being smoothed by
**`GaussSeidel`, a point smoother**. A point smoother does not damp error in the
weakly-coupled direction, the restriction operator is fed error that is not
smooth, the coarse-grid correction contributes little, and multigrid degrades to
the rate of its own smoother. The measured signature matches that account
exactly and quantitatively:

- **the per-iteration convergence factor gets WORSE as the mesh refines** —
  0.664 → 0.966 → 0.986. A working multigrid's factor is **mesh-independent**;
  a point smoother's is `1 − O(h²)`, which for these meshes is ~0.97–0.99.
- **`relTol 0.01` needs 13 / 133 / 318 median iterations.** A healthy GAMG
  V-cycle runs at 0.05–0.2 per cycle and reaches ×100 in **2–3**. The measured
  method is **50–150× off multigrid** and is arithmetically indistinguishable
  from plain Gauss-Seidel on L2 and L3.

**What this lane can conclude from the artifacts:** the coarse-grid correction is
contributing little or nothing on L2 and L3; the configuration is entirely
default apart from the smoother name; the mesh is anisotropic at 96.6; the stall
floor is real and level-dependent.
**What it cannot conclude:** *which* of the smoother, the agglomeration, the
absence of pre-sweeps or the un-interpolated correction is responsible — the logs
carry no per-level GAMG diagnostics — and whether the stall floor is round-off,
the conjugate-interface coupling, or the `fixedFluxPressure` update. **§3's arms
are chosen so that the answer is measured rather than asserted, and §3.1 carries a
control that can prove the multigrid is worthless independently of any tuning
success.**

---

## 2. ⛔ WHAT IS UNCHANGED — **AS AN EXECUTABLE CHECK, NOT A PROMISE**

Every arm below is staged from the **same case, same mesh, same `0/`, same
`constant/`, same `system/` as the T25R4 probe**, and differs from the T25R4
baseline **only inside the `"p_rgh.*"` and `p_rghFinal` solver blocks, and only in
keys that are not `tolerance` and not `relTol`.**

**UNCHANGED, and each is checked by `verify_arm_t25R5.py`, which REFUSES (exit 2)
on any mismatch:**

- **the `p_rgh` convergence criterion** — `tolerance 1e-13` on `"p_rgh.*"` and on
  `p_rghFinal`; `relTol 0.01` on `"p_rgh.*"`; `relTol 1e-3` on `p_rghFinal`.
  **These four values are asserted literally in every arm.** A swapped tolerance
  would make the whole probe meaningless while leaving every other check green.
- **every other solver block** — `rho`, `(U|h|k|omega)`, their `Final` variants,
  and the whole module-region `fvSolution` — asserted byte-identical to T25R4's.
- **the `PIMPLE` blocks** (`nOuterCorrectors 15`, `nCorrectors 2`,
  `nNonOrthogonalCorrectors 0`, `momentumPredictor true`) and **the whole
  `relaxationFactors` block** including every literal `Final` key — asserted
  byte-identical. (`relaxationFactors` is the T25R_L1 divergence fix; it is not
  touched.)
- **the mesh** (24/36/54 family, `r_eff = 1.5000`), the ramps, `deltaT 0.02`,
  `adjustTimeStep no`, the field tuple, and **Addendum D1's `manual`
  decomposition at the shared plane x = 0.050 m, 2 ranks.**
- **`--bind-to none`** on every `mpirun`, per T25R4 §4 / L-431. It changes no
  number and the rate measurement is meaningless without it.
- **`writePrecision 12`**, `writeCompression off`, `runTimeModifiable false`.

**CHANGED, and this is the complete list:** `solver`, `smoother`,
`preconditioner`, `agglomerator`, `nCellsInCoarsestLevel`, `mergeLevels`,
`nPreSweeps`, `nPostSweeps`, `interpolateCorrection`, `cacheAgglomeration` inside
the two `p_rgh` blocks; and, in the `controlDict` only, `endTime 0.8` with
`writeControl timeStep; writeInterval 40;` so that exactly one field write lands
at the probe's end.

> **NO GATE, THRESHOLD, BAND, LABEL OR CEILING OF T25R4 IS TOUCHED BY THIS
> DOCUMENT.** `G-P`, `G-I`, `G-S`, `G-T`, τ = 1.000e-01 K, the 1.234e-02 K second
> tier, Amendment A1's binding 1.000e-02 K, the Roache band `p ∈ [0.5, 1.5]`,
> `Fs = 1.25` and the A1.3 ceiling of 20,000 core-min all stand exactly as
> committed at blob `3ce4dcdff251bf42ec1e5c7f075a6b01fc5d1e4d`. This probe
> produces a **measurement about a linear solver**. It does not grade physics, it
> does not clear a ladder, and it cannot promote anything.

---

## 3. ⚡ THE PREDICTIONS — **REGISTERED FIRST, AND EACH CAN LOSE**

### 3.1 The arms

Baseline **`B0`** is T25R4's configuration exactly. It is **re-run rather than
read off P2**, because the T25R4 probes wrote **no field time directories at all**
(`writeControl runTime; writeInterval 5;` against `endTime 2` — the first write
would have been at t = 5; only `0/` and `0.orig/` exist on disk), so there is
nothing to compare a candidate's fields against.

| arm | change, relative to `B0`, inside the two `p_rgh` blocks only | what it isolates |
|---|---|---|
| `B0` | *(none — T25R4 as registered)* | the baseline, and the §3.5 reproducibility control |
| `C1` | `smoother DICGaussSeidel;` | **one lever**: is the point smoother the whole story? |
| `C2` | `C1` + `nPreSweeps 1;` | is restriction being fed unsmoothed error? |
| `C3` | `C2` + `nCellsInCoarsestLevel 200; interpolateCorrection true;` | is a deep hierarchy on AR-96.6 cells producing bad coarse operators? |
| `C4` | `solver PCG; preconditioner GAMG { smoother DICGaussSeidel; nPreSweeps 1; nCellsInCoarsestLevel 200; agglomerator faceAreaPair; mergeLevels 1; cacheAgglomeration true; }` | the standard remedy when GAMG plateaus: Krylov acceleration of the modes MG leaves |
| `C5` | `solver PCG; preconditioner DIC;` — **no multigrid at all** | **the control.** If `C5` matches or beats `B0`, the coarse-grid correction is provably worth nothing on this system, and §1.2's diagnosis is confirmed without any tuning having to succeed. |
| `D0` | `relTol 0.5` on both blocks — **DIAGNOSTIC ONLY** | the pressure share of per-step cost (§3.4). **`D0` PRODUCES NO PHYSICS.** Its fields are never compared, never cited, and are deleted after its `ExecutionTime` is read. |

All smoothers and preconditioners named are present in this build
(`/usr/lib/openfoam/openfoam2606/src/OpenFOAM/matrices/lduMatrix/smoothers/`:
`DIC DICGaussSeidel DILU DILUGaussSeidel FDIC GaussSeidel nonBlockingGaussSeidel
symGaussSeidel`; `.../preconditioners/`: `DIC DILU FDIC GAMG diagonal none`).

Every arm runs **40 time steps** (`endTime 0.8`, dt 0.02) from the identical `0/`.
40 is chosen because it is the largest count all three T25R4 probe logs reached
(49 / 42 / 44 steps), so the arms sit inside a regime the baseline is already
measured over, and because the stall fraction rises from 0 % at step 1 to 100 %
by the last observed step — 40 steps spans both regimes.

### 3.2 ⚠ `FEASIBLE` — frozen here, before any arm exists, because it is the gate's denominator

> A logged line `GAMG:  Solving for p_rgh, Initial residual = I, …` is
> **FEASIBLE** iff **`I > 6.500e-07`** on L2, **`I > 4.500e-07`** on L1,
> **`I > 1.000e-06`** on L3.

Each is `100 ×` that level's measured stall floor (4.5e-09 / 6.5e-09 / 1.0e-08,
§0.4), i.e. the solves whose `relTol 0.01` target sits at or above a residual the
arithmetic can actually reach. A solve below the threshold is asking for
something no configuration can deliver, and including it measures `maxIter`, not
the solver.

**These three numbers are frozen at this document's commit and are read from
T25R4's committed probe logs. They are not re-derived from T25R5's own output.**
Counts of feasible and infeasible solves are reported per arm so that a shifted
population is visible rather than silent.

### 3.2a ⚠ THE FEASIBLE POPULATION IS ITSELF MILDLY CENSORED — DISCLOSED, NOT SILENT

Of the feasible solves, a few are **themselves** pinned at `maxIter` 1000:
**6 / 11 / 7 on L1 / L2 / L3 — 0.64 % / 1.22 % / 0.63 %** of each feasible
population. On L2 those 11 solves carry 11,000 of the 208,816 feasible iterations,
**~5.3 % of the iteration mass** that forms the gate's denominator.

This does not invalidate the gate and its direction is favourable to honesty:
a censored baseline is **too low**, so it biases **against** an arm being credited
with a speed-up, never for. But §3.2 requires a shifted population to be visible,
and the same standard applies to the baseline's own. **The counts are stated here,
before any arm runs, and are reported again per arm.**

### 3.2b THE GATE'S DENOMINATOR — 40-step and whole-log are the SAME NUMBER, and why

`G-T5`'s 231.76 (§3.3, §5.1) and §3.5's reproducibility target must be the same
population, since the arms run 40 steps and P2 reached 41. **Measured over
T25R4's committed logs, the whole-log and first-40-step means of iterations per
feasible solve are identical to every digit reported:**

| | L1 | L2 | L3 |
|---|---|---|---|
| whole log (49 / 42 / 44 steps) | **30.9570** (n=931) | **231.7636** (n=901) | **330.2916** (n=1111) |
| first 40 steps only | **30.9570** (n=931) | **231.7636** (n=901) | **330.2916** (n=1111) |
| difference | 0.0000 (+0.000 %) | 0.0000 (+0.000 %) | 0.0000 (+0.000 %) |

They coincide because **steps 41 and beyond contribute ZERO feasible solves on
every level** — by step 41 the field has settled far enough that every `p_rgh`
solve's initial residual has fallen below the feasibility threshold. That is
§0.4's story arriving from a second direction, and it is why 40 steps is the right
span: **the entire feasible population lives inside it.**

> **REGISTERED: `G-T5`'s denominator is the mean iterations per feasible solve
> over `p_rgh` solves occurring in TIME STEPS 1–40, and the frozen baseline value
> is 231.7636 on L2. The threshold 46.35 (= 231.7636 / 5.00) needs no
> re-derivation because the two populations coincide.** §3.5's reproducibility
> control uses the same steps-1–40 population, and its per-level targets are
> 30.9570 / 231.7636 / 330.2916.

### 3.3 The predictions

**`P-1` — THE ONE THE PROBE TURNS ON.** At least one arm among `C1…C5`, on **L2**
over steps 1–40 from the identical `0/`, reduces the **mean GAMG iterations per
FEASIBLE `p_rgh` solve** from the measured T25R4 baseline of **231.76** to
**≤ 46.35** — a **≥ 5.00×** reduction — while passing the §4 equivalence control.
*LOSES if no arm reaches 46.35.*

**`P-2` — THE FLOOR IS NOT CONFIGURATIONAL.** No arm's **minimum logged `p_rgh`
final residual on L2** falls below **6.4477e-10** (one tenth of the measured
baseline minimum, 6.4477e-09).
*This lane predicts `P-2` HOLDS. It LOSES if any arm gets below — and that would
be the better outcome, because it would mean the floor is a property of the
configuration and T25R4's criterion could be made reachable.*

**`P-3` — MESH-INDEPENDENCE, SCORED, NOT GATING.** With the stage-2 winner, the
mean iterations per feasible solve across L1/L2/L3 has **max/min ≤ 3.0** —
T25R4's own `G-P` threshold, quoted unchanged and not re-registered here.
Ground: a working multigrid has a mesh-independent iteration count; the measured
baseline spread is **×10.67**. *LOSES if the winner's spread exceeds 3.0.*

**`P-4` — AND THIS LANE EXPECTS TO BE RIGHT, WHICH IS THE BAD NEWS.** A 5×
reduction is **not sufficient** to bring the six-run ladder inside the A1.3
ceiling. Arithmetic, and it does not depend on which arm wins:

> The ladder needs a **wall-time factor of 230,704 / 20,000 = ×11.535**.
> If the `p_rgh` solve is a fraction `s` of per-step wall cost, then even an
> **infinitely fast** pressure solve gives at most `1/(1−s)`.
> **`1/(1−s) ≥ 11.535` requires `s ≥ 0.9133`.**
>
> **UNLESS THE PRESSURE SOLVE IS AT LEAST 91.33 % OF PER-STEP WALL COST, NO
> LINEAR-SOLVER TUNING OF ANY KIND CAN BRING THIS LADDER INSIDE 20,000
> CORE-MINUTES.** `P-4` predicts `s < 0.9133`.
> *LOSES if `D0` measures `s_est ≥ 0.9133`.
> WINS only if `s_upper < 0.9133`.
> Otherwise `P-4` IS NOT SETTLED — see §3.4a, which registers the estimator's
> bias, its direction, and the fact that it favours this prediction.*

That bound is why `D0` exists and why **`D0` runs first** (§6).

### 3.4 `D0`, and what it measures

`s = 1 − (ExecutionTime(D0) / ExecutionTime(B0_L2))`, both over exactly 40 steps
on L2 with everything but the two `relTol` values identical. `D0`'s answer is a
**timing**, and its fields are physics-invalid by construction. **`D0` is never
cited for a temperature, a flux, an order, a band or a gate**, and its
`processor*/` and time directories are removed once its `ExecutionTime` is read.

Inferred, and labelled as inferred rather than measured: `p_rgh` accounts for
~13,300 GAMG iterations per L2 step (443.58 × 30 solves) against ~60 PBiCGStab
iterations for `U`,`h`,`k`,`omega` combined, so `s` is expected to be large. **An
iteration count is not a timing and this probe does not treat it as one.**

### 3.4a ⛔ `D0`'s ESTIMATOR IS BIASED, THE BIAS FAVOURS THIS LANE'S OWN PREDICTION, AND THAT IS WHY IT IS REGISTERED HERE

**`relTol 0.5` does not make the pressure solve free.** `D0` still performs one or
two GAMG iterations on each of its 30 `p_rgh` solves per step, so

```
    T(D0)  =  T_other + T_p_residual ,   T_p_residual > 0
    T(B0)  =  T_other + T_p
    s_est  =  1 - T(D0)/T(B0)  =  s_true - T_p_residual/T(B0)   <   s_true
```

> **`s_est` IS A STRICT LOWER BOUND ON THE TRUE PRESSURE SHARE.**

**The consequence is ASYMMETRIC and is registered as asymmetric:**

- **`s_est ≥ 0.9133` is CONCLUSIVE.** A lower bound crossing the threshold means
  the true share crossed it. **`P-4` LOSES.**
- **`s_est < 0.9133` is NOT on its own conclusive that `s_true < 0.9133`**, and
  **does NOT establish `P-4`**, and does **NOT** establish the claim *"no tuning
  can rescue this ladder"*. Registered as such **before** the measurement exists.

**What it takes to establish `P-4` AFFIRMATIVELY.** `D0`'s own log reports its
mean `p_rgh` iterations `i_D0` against `B0`'s `i_B0`. **Assuming — and this is an
assumption, stated as one, not a measurement — that per-step pressure cost is
approximately proportional to GAMG iteration count**, the residual pressure time
is `T_p_residual ≈ T_p × (i_D0 / i_B0)`, giving the companion **upper** bound

```
    s_upper  =  s_est / ( 1 - i_D0 / i_B0 )
```

> **`P-4` IS ESTABLISHED AFFIRMATIVELY ONLY IF `s_upper < 0.9133`** — i.e. only
> when **both** bounds fall below the threshold.
> **If `s_est < 0.9133 ≤ s_upper`, the registered outcome is a third one:
> `P-4` IS NOT SETTLED BY `D0`.** Not a loss, not a win, and it may not be
> reported as either. The pressure share is then bracketed, both bounds are
> quoted with the proportionality assumption named, and settling it needs a
> timing instrument this probe does not have.

**Why this is in the registration and not in the results.** The bias runs **toward
the outcome this lane wrote down as its expectation** (`P-4`, §3.3). An estimator
that leans the author's way, undisclosed, is exactly what prediction-first
registration exists to prevent; disclosed, bounded, and with the affirmative
condition frozen before the number exists, it is usable. **This amendment was
required by the supervisor's check-1 read of the draft, against this lane's own
prediction, and is recorded as his catch rather than absorbed.**

### 3.5 The reproducibility control on `B0`

`B0_L1`, `B0_L2`, `B0_L3` re-run T25R4's configuration and must reproduce the
first 40 steps of `.../P{1,2,3}/log.solve.legA`. **Mean iterations per feasible
solve over steps 1–40 must agree with the T25R4 log's own first-40-step value to
within ±2 %.** Iteration counts are deterministic at fixed rank count and fixed
decomposition, so ±2 % is generous and a failure is meaningful: it would mean the
staging is not the staging that produced T25R4's probe.

**A `B0` reproducibility failure on any level makes the whole probe `NOT A
RESULT`.** The exact deviation is reported on every level whether it passes or not.

---

## 4. ⛔ THE EQUIVALENCE CONTROL — **a solver change that moves the answer is a defect, not a speedup**

Each arm writes fields once, at t = 0.8 (`writeControl timeStep; writeInterval
40;`), reconstructed with `reconstructPar -allRegions`. The time directory is
located **by numeric value with a tolerance of 1e-6 s**, per T25R4 Amendment
A2.2, and **an ambiguous match REFUSES rather than choosing**.

`compare_arms_t25R5.py` compares each arm against `B0` **at the same level**,
cell-by-cell, in file order:

| field | region | quantity | threshold |
|---|---|---|---|
| `T` | coolant **and** module | `max abs` difference over all cells | **DISQUALIFYING at > 1.000e-03 K** |
| `p_rgh` | coolant | `max abs` difference | **DISQUALIFYING at > 1.0 Pa** |
| `U` | coolant | `max abs` component difference | reported; disqualifying at > 1.0e-03 m/s |
| `k`, `omega`, `nut`, `alphat`, `p` | coolant | `max abs` difference | **reported, gating nothing** |

**Why 1.000e-03 K.** Amendment A1's binding iterative requirement, carried
forward into T25R4 §3.1, is **1.000e-02 K**. A change to the linear solver is
allowed at most **one tenth** of the quantity the campaign's own iterative gate
is measured in, and it sits an order below T25RF's registered within-cell signal
of 1.234e-02 K. **A configuration that moves T by as much as a tenth of the
iterative-convergence requirement is contaminating the quantity `G-I` gates on,
and is a defect however fast it is.**

**Why 1.0 Pa.** 1e-5 relative on a 1e5 Pa field. It exists so that an arm cannot
pass on temperature alone while carrying a grossly different pressure field.

### 4.1 ⚡ THE PLANTED-ZERO CONTROL — rule 3, and the comparator REFUSES without it

Before any real comparison, and **on every invocation**, `compare_arms_t25R5.py`:

1. copies `B0`'s reconstructed `T` for **both** regions to a scratch working copy;
2. plants `PLANT = 1.234e-03 K` into **two** cells — **index 0 and index n−1** —
   so a reader that only inspects the head, or only the tail, is caught;
3. runs **its own** max-|Δ| reader over the planted copy against the unplanted
   original;
4. **REFUSES (exit 2) unless the reader returns exactly 1.234e-03 K, to 1e-12
   relative, for BOTH plants, in BOTH regions.**

`PLANT = 1.234e-03 K` is **above** the 1.000e-03 K disqualifying threshold, so
the control proves not merely that the reader can *see* a difference but that
**the gate can FIRE**. A zero from a reader not shown able to see 1.234e-03 K is
not evidence (rule 3), and `writePrecision 12` at T ≈ 293 K resolves it with
seven figures to spare.

The comparator additionally **REFUSES** on: a missing time directory; a missing
field file; differing cell counts between the two sides; any non-finite value;
or a `0/` state that is not byte-identical between the two arms.

### 4.2 THE DISQUALIFICATION RULE — an arm's iteration count is not eligible if any of these holds

**`E1`** `max|ΔT|` over coolant ∪ module cells at t = 0.8 exceeds 1.000e-03 K.
**`E2`** `max|Δp_rgh|` over coolant cells exceeds 1.0 Pa.
**`E3`** the arm did not reach 40 steps with `rc = 0` inside its registered
timeout. *(An arm slower than 1.5× baseline is disqualified by definition — see
§5 — so its timeout kill IS the measurement, not waste.)*
**`E4`** any registered field at t = 0.8 is absent or contains a non-finite value.
**`E5`** the §4.1 planted-zero control refuses.
**`E6`** `verify_arm_t25R5.py` finds **any** difference from `B0`'s dictionaries
outside the permitted key set of §2 — in particular any change to `tolerance`,
to either `relTol`, to `PIMPLE`, to `relaxationFactors`, to another equation's
solver block, to the module region, to the mesh, or to `0/`.

**A disqualified arm's speed is not reported as a speed-up anywhere.** It is
reported as `DISQUALIFIED`, with which of `E1…E6` fired and the measured value
that fired it.

---

## 5. THE GATE, THE THRESHOLD, THE CAP AND THE LABEL — **all four fixed here, before any run**

### 5.1 `G-T5`

> **`G-T5` PASSES iff at least one arm among `{C1, C2, C3, C4, C5}` is NOT
> DISQUALIFIED under §4.2 and achieves a mean of ≤ 46.35 GAMG iterations per
> FEASIBLE `p_rgh` solve on L2 over steps 1–40** — a ≥ 5.00× reduction from the
> measured T25R4 baseline of 231.76.

**Labels, and only these:**

- **`G-T5` PASS** → the tuning hypothesis is supported at 5×. The winner goes to
  stage 2. **NO LADDER LAUNCHES ON THIS RESULT.** A ladder needs a new
  registration, and whether one is written is the supervisor's call and, where it
  touches the A1.3 ceiling, Sanaa's.
- **`G-T5` GATE FAIL** → the tuning hypothesis is not supported at 5×. The best
  measured factor is reported with its arm. §7 is then the disposition.
- **`NOT A RESULT`** → if no arm completes; or `B0` fails §3.5's reproducibility
  control on any level; or the §4.1 planted-zero control refuses; or `D0` cannot
  be read.

**Why 5.00× and not 2× or 20×.** The measured gap to a healthy multigrid is
50–150× (§1.2), so 5× is a **modest fraction of what the diagnosis predicts** and
a configuration that cannot manage it has not found the mechanism. And 5× is the
smallest factor that would be worth carrying into a new registration: below it,
the ladder arithmetic of `P-4` is not moved at all. **It is registered before any
arm exists and this lane does not claim it is the right number, only that it is
frozen and reasoned.**

### 5.2 The cost — priced from **MEASURED** T25R4 rates, arithmetic shown

Rates are `GP_VERDICT.json`'s `s_per_step`, measured at 2 ranks with
`--bind-to none` under **the criterion that will actually run**: L1 **4.78375**,
L2 **12.808049**, L3 **26.577674** s/step. **These are measured, not
extrapolated** — the error that cost T25R3 19–33× was extrapolating a rate from a
solver that was not running.

```
  POINT(arm)   = 40 steps x r(L) x 2 ranks / 60           [core-min]
  timeout_s    = 1.5 x 40 x r(L)          (rounded up)    [an arm slower than
                                                           1.5x baseline is
                                                           DISQUALIFIED by E3]
  CAP(arm)     = timeout_s x 2 / 60                       [core-min]
```

| level | r(L) s/step | 40-step wall s | **POINT** core-min | `timeout_s` | **CAP** core-min |
|---|---|---|---|---|---|
| L1 | 4.78375 | 191.35 | **6.378** | **290** | **9.667** |
| L2 | 12.808049 | 512.32 | **17.077** | **770** | **25.667** |
| L3 | 26.577674 | 1063.11 | **35.437** | **1600** | **53.333** |

| stage | arms | level | POINT | CAP |
|---|---|---|---|---|
| 0 | `D0` | L2 | 17.08 | 25.67 |
| 1 | `B0`, `C1`, `C2`, `C3`, `C4`, `C5` (6) | L2 | 102.46 | 154.00 |
| 2 | `B0`, winner (2) | L1 | 12.76 | 19.33 |
| 2 | `B0`, winner (2) | L3 | 70.87 | 106.67 |
| — | staging: 11 × `decomposePar`, serial, 20 s allowance | — | 3.67 | 3.67 |
| **TOTAL** | **11 runs** | | **206.84** | **309.34** |

> **⛔ REGISTERED CEILING: 320 CORE-MINUTES ACROSS THE WHOLE PROBE. AN OVERRUN
> STOPS THE RUN; IT DOES NOT GET A NEW BUDGET (rule 12).**

**320 core-min = $0.274 at $0.0513/core-h — DERIVED, NOT MEASURED**,
`cost_basis = REPORTED-BY-OWNER`; this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). Inside the $25 pre-authorisation by a factor of 91.

**A ×1.5 cap margin, not ×4, and the reason is stated:** unlike T25R4's probe,
this one's baseline rate is measured **under the exact criterion and mesh that
will run**, and the arms are hunting a *speed-up*. A margin above 1.5 would be
buying room for outcomes the probe defines as failures.

### 5.3 ⛔ THIS DOCUMENT DOES NOT WIDEN THE A1.3 CEILING AND DOES NOT ASK TO

**T25R4 Amendment A1.3's ceiling of 20,000 core-minutes stands exactly as
committed.** This probe's 320 core-min is its **own** cost under its **own**
registration; it is not drawn against A1.3 and it does not extend it.

**Retiring or widening a registered ceiling is reserved to Sanaa
(`CLAUDE.md`, FIRST-ACTION RULE).** No result of this probe — including a `G-T5`
PASS — authorises the ladder to launch, re-prices it, or moves that number by one
core-minute. **A blanket authorisation is not a per-item reading, and approval of
this probe is approval of its 320 core-min cap and of nothing else (rule 9).**

---

## 6. ORDER OF OPERATIONS — REGISTERED, AND NOT NEGOTIABLE

1. **This document is committed.**
2. **The supervisor reads it, and reads the arm dictionaries as a DIFF against
   `.../P1/system/coolant/fvSolution`.** Undelegable. **No solver launches before
   this step completes.**
3. **`D0` runs first.** It brackets `P-4` at 25.67 core-min. **Both `s_est` and
   `s_upper` are computed per §3.4a and reported to the supervisor BEFORE stage 1
   launches**, together with which of the three registered outcomes holds
   (`P-4` loses / `P-4` wins / `P-4` not settled). If `s_upper < 0.9133`, the
   ladder cannot be rescued by tuning at any speed-up — the probe is then still
   worth running for the diagnosis and for a successor registration, but it is
   worth running **knowing that**, not discovering it afterwards. **`s_est <
   0.9133` alone does not license that statement** and may not be reported as
   though it did.
4. Stage 1: `B0` then `C1…C5` on L2. `verify_arm_t25R5.py` refuses any arm whose
   dictionaries differ outside §2's permitted key set.
5. `B0`'s §3.5 reproducibility control. **A failure stops the probe:
   `NOT A RESULT`.**
6. §4's equivalence control on every arm, planted-zero control first.
   §4.2 disqualifications applied **before** any iteration count is compared.
7. **Evaluate `G-T5`.**
8. Stage 2 **only** if `G-T5` PASSES: the winner and `B0` on L1 and L3; score
   `P-3`.
9. Report. **The probe ends at a report. It does not launch a ladder, amend
   T25R4, or price anything.**

---

## 7. ⚠ IF THE TUNING HYPOTHESIS IS WRONG — the disposition, registered in advance so it cannot be improvised

Registered here because a disposition chosen after seeing the answer is not a
disposition, it is a rationalisation.

**Case A — `G-T5` GATE FAIL, and `C5` (no multigrid) is no worse than `B0`.**
Then ~330 iterations is close to intrinsic for this operator at this criterion
with the tools in this build, and **multigrid is measurably contributing nothing
on this mesh.** The cost is not a tuning defect; it is what an anisotropic
pressure Poisson solve on an AR-96.6 mesh costs at ×100 per solve. **There is no
cheap answer and this document will not manufacture one.** The ladder is then
outside 20,000 core-min for a physical reason, and the live options — none of
which this lane may take — are: fewer or shorter ladder runs; a less anisotropic
mesh family (which restarts the Roache triple); a differently registered
criterion; or Sanaa widening the ceiling.

**Case B — `G-T5` GATE FAIL, but `C5` is much worse than `B0`.** Multigrid *is*
helping and is simply badly tuned in a way none of `C1…C4` found. The finding is
reported and the next probe is a wider sweep — but it is a **new registration**
with its own frozen gate, not an extension of this one.

**Case C — `G-T5` PASS but `P-4` also holds (`s_upper < 0.9133`).** This lane's
expected outcome. **A real 5×+ speed-up that still cannot bring the ladder inside
20,000 core-min**, because the bound of §3.3 is on the *step*, not the solve.
The correct report is exactly that: a genuine solver improvement, correctly
measured, that does not by itself change the ladder's disposition. **It must not
be reported as having rescued the ladder.**

**Case C′ — `P-4` NOT SETTLED (`s_est < 0.9133 ≤ s_upper`).** Registered as a
distinct outcome so it cannot be quietly collapsed into Case C, which is the
direction this lane's own prediction leans. The pressure share is **bracketed,
not determined**; both bounds are reported with §3.4a's proportionality
assumption named; and **no statement of the form "tuning cannot rescue the
ladder" may be made.** Whether to build a timing instrument that would settle it
is the supervisor's call, not this document's.

**Case D — `G-T5` PASS and `s ≥ 0.9133`.** The only branch in which tuning alone
could put the ladder inside the ceiling. Even then: **the ladder does not launch
on this document.** It needs a new registration, a re-priced formula, and the
supervisor's diff-read.

**In every case the stall of §0.4 remains**, and it is a criterion question, not
a tuning question: `p_rghFinal`'s `relTol 1e-3` asks for a reduction the
arithmetic cannot deliver on a growing share of solves. **This probe does not
touch it, because it is registered.** It is named here so that a successor finds
it stated rather than rediscovers it a third time.

---

## 8. THE RUN DIRECTORIES — **NAMED, AND THEY DO NOT EXIST**

Rule 2's pre-compute limb requires the condition to be stated and how it was
checked. **Checked at drafting, 2026-09-02:
`ls -d /home/ubuntu/Certonomous/verification/runs/T-family/T25R5*` returns
`No such file or directory`. Not one of the following exists:**

```
verification/runs/T-family/T25R5_LINSOLVER_runs/
    D0_L2/
    B0_L2/  C1_L2/  C2_L2/  C3_L2/  C4_L2/  C5_L2/
    B0_L1/  X_L1/          (X = the stage-1 winner, named at stage 2)
    B0_L3/  X_L3/
    verify_arm_t25R5.py  compare_arms_t25R5.py  grade_t25R5.py
    stage_t25R5.py  run_one_t25R5.sh
    GT5_VERDICT.json
```

**No compute of any kind has been performed under this registration.** The
measurements in §0 and §1 are readings of T25R4's **committed** artifacts — its
pre-registration at blob `3ce4dcdff251bf42ec1e5c7f075a6b01fc5d1e4d`, its three
probe logs, `GP_VERDICT.json`, the `fvSolution` files, `log.checkMesh.coolant`,
and the OpenFOAM v2606 source — and not of anything this probe produced.

---

## 9. FREEZE

Frozen at this document's commit. **Before first compute** amendments are legal
and must state the condition and how it was checked; **after first compute the
gates are closed** and changes land only as dated addenda that cannot alter a
gate, threshold, cap or label. `grade_t25R5.py` hashes this document against the
committed blob and **REFUSES on a mismatch**.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

---

## 10. WHAT THIS LANE COULD NOT VERIFY

1. **No arm has been run.** Every number in §0, §1 and §5.2 is measured on
   T25R4's logs under the T25R4 configuration. The arms' costs are *predicted*
   from those rates, and an arm could be slower — which is why every arm carries
   its own timeout and why §4.2's `E3` makes the timeout a verdict rather than a
   waste.
2. **The mechanism behind the stall floor is not identified.** Round-off in a
   1/h term is *consistent* with the measured ×1.44 / ×1.54 scaling against
   `r_eff = 1.5000`, and this lane cannot separate it from the conjugate-interface
   coupling or the `fixedFluxPressure` update using the logs alone. `P-2` is the
   registered test of whether it is configurational at all.
3. **The pressure share `s` is inferred, not measured, and `D0` BRACKETS it
   rather than determining it.** §3.4 infers it is large from iteration counts;
   **an iteration count is not a timing.** `D0`'s `s_est` is a strict **lower**
   bound (§3.4a); its companion `s_upper` rests on an **assumed** proportionality
   between pressure cost and GAMG iteration count, which this lane has not
   verified and cannot verify without a timing instrument this probe does not
   build. **`P-4` may therefore end unsettled, and §7 Case C′ registers that
   outcome in advance.**
4. **`nCellsInCoarsestLevel 200` in `C3`/`C4` is a judgement.** It is not derived;
   it is a value large enough to make the hierarchy materially shallower than the
   default 10 on all three meshes. This lane cannot claim it is the right number.
5. **`G-T5`'s 5.00× and `P-3`'s reuse of 3.0 are judgements**, registered before
   any arm exists. `P-3` quotes T25R4's `G-P` threshold rather than inventing one,
   which is a choice about comparability, not a proof that 3.0 is correct.
6. **`checkMesh` was not re-run** — no compute was permitted. `Max aspect ratio =
   96.62` is read from `.../T25R_MODULE_runs/T25R_L2/log.checkMesh.coolant` and
   corroborated to ten figures on the T25R2 L1 log. It is the same 24/36/54
   family; **this lane did not verify by execution that the T25R4 probe meshes
   carry that number**, only that they are the family that does.
7. **§0.2's `s_per_step` divergence from A1.1's frozen formula is reported and
   not repaired.** Repairing another rung's frozen document is not this lane's to
   do, and is referred to the supervisor.
8. **The baseline denominator is itself mildly censored** (§3.2a: 6 / 11 / 7
   feasible solves are pinned at `maxIter`, ~5.3 % of L2's iteration mass). The
   direction is favourable — a censored baseline biases against crediting an arm —
   but it is a known impurity in `G-T5`'s denominator, not an absent one.
9. **The four high-residual pinned solves on L2** (§0.4) are a genuine second
   failure mode this lane's §1.2 reading does not explain. They are 0.36 % of the
   pinned population and confined to t = 0.02 and 0.04. **Recorded, not
   explained.**

### 10.1 PROVENANCE OF THIS VERSION

Drafted by a heat-transfer `lab-lane`; **§3.2a, §3.2b, §3.4a, §7 Case C′ and
§0.4's two-mode paragraph were added on the heat-transfer supervisor's check-1
read of the draft, before any commit and before any compute.** §3.4a in
particular is his catch **against this lane's own registered prediction**, and it
is recorded as his rather than absorbed. He independently reproduced §0.3's
central measurements before accepting them, and his alternative "unpinned-only"
definition of the feasible population gives 24.67 / 222.27 / 326.05 against this
lane's 30.96 / 231.76 / 330.29 — **two different definitions reaching the same
conclusion**, which is stronger corroboration than agreement on one definition
would have been. **`G-T5` is frozen on this lane's definition (§3.2), which is the
one stated here.**

---

**NOTHING IN THIS DOCUMENT HAS RUN. THIS FILE IS UNCOMMITTED. THE NEXT ACTION IS
THE SUPERVISOR'S DIFF-READ AND COMMIT, NOT A LAUNCH.**

<!-- END OF T25R5 PRE-REGISTRATION v1.0 (DRAFT, UNCOMMITTED) -->

---

## Amendment A1 — 2026-09-02T~21:17Z, **BEFORE ANY T25R5 COMPUTE.** `B0_L2` moves to stage 0, because §6 step 3 as registered could not execute; and `s_upper`'s iteration ratio is frozen

**Version v1.1. Lines whose number changed above this section: 0.**

**THE CONDITION UNDER WHICH THIS AMENDMENT IS LEGAL, AND HOW IT WAS CHECKED.**
Rule 2 permits an amendment **before first compute**. **Re-measured inside the
invocation that commits this amendment, at 2026-09-02T21:16:53Z, and not copied
from anyone's report:** `ls -d
/home/ubuntu/Certonomous/verification/runs/T-family/T25R5_LINSOLVER_runs` returns
`No such file or directory`, and `find .../verification/runs/T-family -maxdepth 1
-name 'T25R5*'` returns **0** paths. **No `0/`, no time directory, no
`processor*/`, no `log.*`, no run directory of any kind exists under this
registration. There has been no first compute and the gates are open.**

*(Housekeeping: the v1.0 trailer above still reads "THIS FILE IS UNCOMMITTED".
That was true when written and is now false — v1.0 is committed at
`9d9547931cef56168ec019c3b3a4c2add899a5de`, blob
`c336dd8bb6b442502b1eb3ce0b72bb2d625023d9`. Rule 6 forbids editing it; the
correction is recorded here instead.)*

### A1.1 ⛔ THE DEFECT — §6 STEP 3 IS NOT EXECUTABLE AS REGISTERED

§6 step 3 registers that `D0` runs **first** and that **both** `s_est` and
`s_upper` are computed and reported **before stage 1 launches**. But §3.4 defines

```
    s_est = 1 - ExecutionTime(D0) / ExecutionTime(B0_L2)
```

and §3.4a's companion bound needs `i_B0` — **and §5.2 places `B0` in stage 1.**
**Neither bound can be computed before the run they are ratios against has
happened.** As registered, step 3 cannot be performed, and §6's "brackets `P-4`
at 25.67 core-min" understates the true cost of bracketing it.

**Found by the heat-transfer supervisor's check-4 read. Recorded as his, not
absorbed.**

### A1.2 THE RESOLUTION — `B0_L2` MOVES INTO STAGE 0. **NO COST IS ADDED.**

Stage 1 already contained `B0_L2`. This moves that spend **earlier in the order**;
it does not create any.

| stage | arms | level | POINT core-min | CAP core-min |
|---|---|---|---|---|
| **0** | **`D0`, `B0_L2`** (2) | L2 | **34.15** | **51.33** |
| **1** | **`C1`, `C2`, `C3`, `C4`, `C5`** (5) | L2 | **85.38** | **128.33** |
| 2 | `B0`, winner (2) | L1 | 12.76 | 19.33 |
| 2 | `B0`, winner (2) | L3 | 70.87 | 106.67 |
| — | staging: 11 × `decomposePar`, serial, 20 s allowance | — | 3.67 | 3.67 |
| **TOTAL** | **11 runs, unchanged** | | **206.83** | **309.33** |

**Identical to §5.2's totals to rounding (206.84 / 309.34), and the run count is
unchanged at 11.** **⛔ THE REGISTERED CEILING OF 320 CORE-MINUTES IS UNCHANGED
AND IS NOT WIDENED BY THIS AMENDMENT.** `G-T5`, its threshold of 46.35, the
frozen denominator 231.7636, `P-1`…`P-4`, the equivalence thresholds, `E1`–`E6`
and every label are **untouched**.

**§6 step 3's cost figure is corrected from 25.67 to `CAP` 51.33 core-min
(`POINT` 34.15)** — the true cost of bracketing `P-4`.

**AND IT STRICTLY IMPROVES THE DESIGN, which is why it is the right resolution
rather than merely a legal one.** §3.5's L2 reproducibility control compares
`B0_L2` against T25R4's P2 log, and §6 step 5 makes a reproducibility failure
**`NOT A RESULT` for the whole probe**. With `B0_L2` in stage 0, **that control
is evaluated before the five `C`-arms are paid for** instead of after. A staging
defect that voids the probe is now caught at 51.33 core-min rather than at 179.66.

**REGISTERED ORDER, replacing §6 steps 3–4:**

> **3.** Stage 0: `D0` **and** `B0_L2`. Evaluate §3.5's L2 reproducibility control
> **first** — a failure stops the probe at `NOT A RESULT` and stage 1 does not
> launch. Then compute `s_est` **and** `s_upper` per §3.4a and A1.3, and report
> both to the supervisor, **with which of the three registered outcomes holds**
> (`P-4` loses / `P-4` wins / `P-4` not settled), **before stage 1 launches.**
> **4.** Stage 1: `C1`…`C5` on L2.

### A1.3 ⚠ `i_D0` AND `i_B0` ARE FROZEN AS **ALL-SOLVES** MEANS, AND THE REASON IS THAT `s_upper` IS A COST RATIO

§3.4a wrote *"mean `p_rgh` iterations"* without saying which population. On the
baseline the two candidates differ by nearly ×2 — **443.58 over all solves against
231.76 over feasible solves** — and `s_upper = s_est / (1 − i_D0/i_B0)` depends on
the choice. **Frozen here, before either number exists:**

> **`i_D0` and `i_B0` are the mean GAMG iterations per `p_rgh` solve over ALL
> logged `p_rgh` solves in time steps 1–40 — NOT the feasible subset.**

**Why all-solves is the correct population and the feasible subset would be
wrong here.** `s_upper` rests on the assumption that pressure wall time is
proportional to GAMG iterations **performed**. Every iteration costs wall time
whether or not its solve was feasible, and the 1,000-iteration pinned solves cost
the most of all. Both runs perform 30 `p_rgh` solves per step over 40 steps, so
the ratio of all-solves means **is** the ratio of total iterations — exactly the
quantity the proportionality assumption is about. **The feasible restriction of
§3.2 exists for `G-T5`, which measures solver QUALITY; `s_upper` is a COST ratio
and must count the work actually done.**

**Expected magnitude, stated so it cannot be presented as a discovery.** At
`relTol 0.5`, `i_D0` should be ~1–2 against `i_B0` ~443, so `i_D0/i_B0` ~0.003–0.005
and the correction `1/(1 − i_D0/i_B0)` ~1.004 — **a bracket roughly 0.4 % wide.**
That is a reason to freeze the definition now rather than a reason it does not
matter: a bound whose population is chosen after its inputs are known is not a
bound.

### A1.4 ⛔ THE OTHER RESOLUTION IS REFUSED, AND THE REFUSAL IS REGISTERED

**Using T25R4's `P2` log as `D0`'s timing baseline is REFUSED.** `P2` ran on
2026-09-01 under that day's box load; **an `ExecutionTime` ratio taken across two
runs a day apart under different contention is not a measurement of pressure
share**, it is a measurement of contention. §3.1 already refused to read `B0`'s
**fields** off `P2`; **the refusal applies harder to a timing**, because a field
is deterministic and a wall time is not. `s_est` and `s_upper` are computed only
from `D0` and `B0_L2` run in the same stage on the same box.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

<!-- END OF T25R5 PRE-REGISTRATION v1.1 -->

---

## Amendment A2 — 2026-09-02T~21:26Z, **BEFORE ANY T25R5 COMPUTE.** `C5` cannot support the inference §3.1 registered on it; the coarse-grid claim moves to `C4` vs `C5`

**Version v1.2. Lines whose number changed above this section: 0.**

**LEGALITY, RE-MEASURED IN THE COMMITTING INVOCATION AT 2026-09-02T21:26:01Z, not
copied from any report:** `find verification/runs/T-family/T25R5_LINSOLVER_runs
\( -name '0' -o -name 'processor*' -o -name 'log.*' -o -name '.rc.*' \)` returns
**0** paths. The run tree holds the seven arm dictionaries and the verifier and
**nothing else — no case tree, no `0/`, no `constant/`, no `system/`, no
`processor*/`, no log, no rc file.** **No first compute. Rule 2's pre-compute limb
governs and the gates are open.**

**THE ARMS DO NOT CHANGE. Not one byte of any `fvSolution` is altered by this
amendment.** What changes is **what may be concluded** from a comparison — which
is exactly the clause that becomes unamendable the moment a solver starts.

### A2.1 ⛔ THE CONFOUND — `C5` vs `B0` CHANGES TWO VARIABLES, SO IT IS NOT A CONTROL

§3.1 registers `C5` as *"the control. If `C5` matches or beats `B0`, the
coarse-grid correction is provably worth nothing on this system."*
**That does not follow, and "provably" is the wrong word.**

`B0` is **standalone GAMG with a `GaussSeidel` smoother**. `C5` is **PCG with a
`DIC` preconditioner**. Going from one to the other **removes the multigrid AND
adds Krylov acceleration in the same step.** If `C5` wins, at least two
explanations survive:

1. the coarse-grid correction was contributing nothing; **or**
2. **Krylov acceleration is what this system was missing** — which is a live
   hypothesis here precisely because §1.2 measured a per-iteration factor that
   degrades with mesh, the signature a Krylov method is built to attack.

**A comparison that moves two variables is not a control.** Found by the
heat-transfer supervisor's §6 step-2 diff-read. Recorded as his.

### A2.2 ⚡ THE CLEAN ISOLATION IS ALREADY IN THE ARM SET — `C4` vs `C5`

`C4` is **PCG + GAMG preconditioner**; `C5` is **PCG + DIC preconditioner**.
**Same outer Krylov solver, same tolerance, same `relTol`, same mesh, same
everything — differing ONLY in whether the preconditioner carries a coarse-grid
correction.** That is the one-variable contrast, and it costs nothing extra
because both arms are already staged and already priced.

**And it tests multigrid at its best case here**, since `C4`'s GAMG
preconditioner is the tuned one (`DICGaussSeidel`, `nPreSweeps 1`,
`nCellsInCoarsestLevel 200`) rather than the registered default. **A control that
tests the weakest version of the thing it is trying to exonerate is not a fair
test.**

**Let `R = I(C5) / I(C4)`**, both being mean GAMG/PCG iterations per **FEASIBLE**
`p_rgh` solve on L2 over steps 1–40, per §3.2's frozen thresholds. **Frozen here,
before either number exists:**

| outcome | condition | what may be concluded |
|---|---|---|
| **coarse-grid correction contributes NOTHING measurable** | **`R ≤ 1.5`** | §1.2's reading is supported: the coarse-grid correction is not doing the work multigrid exists to do, even when tuned and Krylov-wrapped |
| **coarse-grid correction IS contributing** | **`R ≥ 3.0`** | **the OPPOSITE finding, and it is registered as reachable.** Multigrid works here once properly preconditioned, and §1.2's diagnosis is wrong about the mechanism |
| **NOT SETTLED** | **`1.5 < R < 3.0`** | the correction contributes something, and not enough to call either way. **Reported as unsettled, and neither conclusion may be drawn.** |
| **the GAMG preconditioner is a NET COST** | **`R < 1.0`** | reported as such, plainly |

**Why 1.5 and 3.0.** Iteration counts here are deterministic at fixed rank count
and decomposition, so neither bound is absorbing run-to-run noise. **1.5**: a
coarse-grid correction that buys less than half is not doing the job multigrid
exists for — mesh-independent convergence — which is an order-of-magnitude
effect, not a 40 % one. **3.0**: a factor of three is a real contribution by any
reading and is the same number `P-3` and T25R4's `G-P` already use for
"materially different". **Both are registered before the numbers exist and this
lane does not claim they are the right numbers, only that they are frozen and
reasoned.**

**THE INFERENCE IS UNAVAILABLE IF EITHER ARM IS DISQUALIFIED.** If `C4` or `C5`
fails any of `E1`–`E6` (§4.2), `R` is **not computed and not reported as a
bound** — a ratio between a valid arm and an invalid one is not a measurement.

### A2.3 WHAT `C5` vs `B0` MAY STILL BE CITED FOR — **DOWNGRADED TO WHAT IT CAN CARRY**

> **`C5` beating `B0` establishes ONLY this: a Krylov method with a cheap
> preconditioner outperforms THE REGISTERED STANDALONE GAMG CONFIGURATION on this
> system.** That is a statement about **a configuration**, not about multigrid.

**§1.2's diagnosis may NOT be called "confirmed" by `C5` vs `B0` alone**, and the
word "provably" is withdrawn from §3.1's description of `C5`. The conclusion
§3.1 reached for is now carried by A2.2's `R`, and by nothing else.

**This amendment alters no gate, no threshold, no cap, no label and no ceiling.**
`G-T5` and its 46.35, the frozen denominator 231.7636, `P-1`…`P-4`, `E1`–`E6`,
the equivalence thresholds, the 320 core-min ceiling and A1's stage table are all
untouched. **`R` is a REPORTED, SCORED inference, and it gates nothing** — the
same standing `P-3` has.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

<!-- END OF T25R5 PRE-REGISTRATION v1.2 -->

---

## Addendum D1 — 2026-09-02T~22:05Z, **AFTER FIRST COMPUTE.** The re-run protocol, and three expected values registered so the re-run can LOSE

**Version v1.3. Lines whose number changed above this section: 0.**

⚠ **THIS IS AN ADDENDUM, NOT AN AMENDMENT.** First compute on this probe occurred
at **2026-09-02T21:33:07Z**, so the gates are CLOSED (rule 2). **This addendum
alters NO gate, NO threshold, NO cap and NO label.** `G-T5` stays at
`≤ 46.3527` iterations per feasible solve, the frozen denominator stays
`231.7636`, `E1`–`E6` stay exactly as registered, A2's `R` bands stay `1.5`/`3.0`,
and the §5.2 ceiling stays **320 core-min**. What it adds is a **protocol** and a
**new refusal condition**, both of which can only make the probe stricter.

### D1.1 ⛔ `C2` AND `C3` ARE DISQUALIFIED. THE RULING IS FINAL AND THE NUMBERS ARE NOT BANKED

`C2_L2` (rc 124, 38/40 steps) and `C3_L2` (rc 124, 37/40 steps) fired **`E3` and
`E4`**. They are **DISQUALIFIED**.

> **`C2`'s 44.6504 — a 5.19× reduction that CLEARS `G-T5` — IS NOT A SPEED-UP, IS
> NOT ELIGIBLE, AND IS NEVER REPORTED AS ONE.**

**A registered disqualifier that fires only when we dislike the result is not a
disqualifier.** `C2` is the case that tests whether this one is real: it is the
single arm that clears the gate, and it is the one thrown out. `E4` is the
substantive half — a capped arm wrote no fields at `t = 0.8`, so **there is no
equivalence check, and an uncertified 5.19× may be a different answer rather than
a faster one.**

**The disqualified attempts and their numbers stay on the record permanently.
Nothing is deleted, nothing is overwritten, and `STAGE1_BATCH1_RESULT.json`
stands.**

### D1.2 THE CAUSE WAS A STAGING DEFECT, SO THE QUESTION IS UNMEASURED — NOT ANSWERED

`B0_L2` ran 2-way with `D0`, and `D0` finished in 42 s of `B0`'s 516 s, so the
**baseline effectively had the box to itself**. `C1`/`C2`/`C3` were then batched
**3-way against each other for their whole duration**, on top of the live `ansys`
and `JF1` campaigns. Measured iteration throughput: **B0 984/s, C1 480/s,
C2 396/s, C3 362/s**. `C1` performed 4.15× **fewer** iterations per feasible solve
than `B0` and still took 727 s against `B0`'s 516 s.

**Honest limit on that claim:** per-iteration cost is **not** equal across
configurations — a `DICGaussSeidel` sweep costs more than a plain `GaussSeidel`
sweep — so **part of the throughput drop is genuine and this lane cannot separate
the two from these runs.**

**The defect was this lane's, introduced after the gates closed. Disqualifying a
contaminated attempt does not oblige the lab to leave the question unmeasured; it
obliges the lab never to bank the contaminated number.**

### D1.3 THE PROTOCOL — **ONE ARM AT A TIME, AND `C1` IS RE-RUN TOO**

1. **`C1`, `C2`, `C3` are re-run and `C4`, `C5` are run — five arms, ONE AT A
   TIME.** No two arms of this probe run concurrently. Each is launched only after
   the previous one's `rc` file exists.
2. **⛔ `C1` IS RE-RUN, AND THAT IS NOT OPTIONAL.** `C1` completed, so there is a
   temptation to keep it and re-run only what failed. **Refused.** `C1`'s 4.15×
   was measured under 3-way contention while the baseline ran effectively alone;
   comparing a clean `C2` against a contended `C1` **rebuilds the same confound
   one level up.** Every arm is measured under one protocol or the comparison is
   not a comparison.
3. Cap **25.667 core-min per arm** (`timeout 770 s`), unchanged. Five arms =
   **128.33 core-min**. Spent to date **89.133**; worst case cumulative
   **217.47**, inside the registered 320.
4. Full rule 4 on every arm; **§4.1's planted zero first on every invocation**;
   §4.2 applied **before** any iteration count is compared.

### D1.4 ⚡ THE CONTROL THAT MAKES THIS A MEASUREMENT AND NOT A RETRY — **REGISTERED BEFORE THE RE-RUN**

Iteration counts are **deterministic** at fixed rank count and fixed
decomposition. §3.5 proved it bit-for-bit: `B0_L2` reproduced T25R4's `P2` at
**231.7636 against 231.7636**, same 901 feasible solves, same 310 pinned, same
minimum residual. **Therefore a re-run under corrected conditions must reproduce
the capped attempt's iteration counts EXACTLY — the contention changed the wall
clock, and it cannot have changed the arithmetic.**

**REGISTERED NOW, BEFORE THE RE-RUN, FROM THE DISQUALIFIED ATTEMPTS' LOGS:**

| arm | feasible solves | **Σ iterations (exact integer)** | mean per feasible solve |
|---|---|---|---|
| `C1` | **901** | **50,281** | **55.8057713651** |
| `C2` | **901** | **40,230** | **44.6503884573** |
| `C3` | **901** | **42,293** | **46.9400665927** |

> **⛔ IF A RE-RUN'S FEASIBLE-SOLVE COUNT IS NOT EXACTLY 901, OR ITS ITERATION SUM
> IS NOT EXACTLY THE INTEGER ABOVE, THAT IS A DEFECT AND THE PROBE STOPS AS
> `NOT A RESULT`. It does not get quietly re-measured.**

The integer sums are registered alongside the means because an integer is
unambiguous and cannot be argued about at the last decimal place.

**THIS IS WHAT CONVERTS "RE-RUNNING THE ARM I LIKED" INTO "REPRODUCING A
DETERMINISTIC QUANTITY UNDER CORRECTED CONDITIONS".** The re-run is made
falsifiable against a number already in hand, and it can lose. **`C4` and `C5`
have no such expectation registered, because they have never run — and that
asymmetry is stated rather than hidden.**

**Corroboration this rests on, arriving from a third independent direction:**
`B0`, `C1`, `C2` and `C3` all carry **exactly 901** feasible solves despite
running 40, 40, 38 and 37 steps. The gate's measurement population was
**complete even in the capped arms**, because feasible solves stop occurring
around step 30 (§3.2b). That strengthens the reproduction requirement rather
than excusing it.

### D1.5 COST ATTRIBUTION — THE CONTAMINATED BATCH IS **WASTE, NAMED**

**The 70.533 core-min spent on `C1`/`C2`/`C3` under 3-way contention is WASTE
CAUSED BY THIS LANE.** It is named as waste and is **never folded into an
actual/predicted ratio** (`COMPUTE_BUDGET_CHARTER` §6, rule 12). It bought one
usable equivalence result (`C1`'s, which held at 8.0e-09 K) and two disqualified
attempts.

### D1.6 THE STANDING REPORTING CONDITION IS REAFFIRMED AND UNCHANGED

**No report of this probe may state or imply that the ladder is rescuable without
quoting the 20.9×–156.8× requirement in the same breath as the measured factor.**
The best **eligible** factor to date is `C1`'s 4.15×, below the 5.00× gate; even
the **disqualified** 5.19× is four to thirty times short of what the ladder needs.
**Nothing in the re-run changes that arithmetic.**

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

<!-- END OF T25R5 PRE-REGISTRATION v1.3 -->

---

## Addendum D2 — 2026-09-02T~23:05Z, **AFTER STAGE 1.** D1.6's reporting condition is RETRACTED as misleading, and the reproduction control's first use is recorded against its author

**Version v1.4. Lines whose number changed above this section: 0.**
Addendum, not amendment: gates closed at 21:33:07Z. **Alters no gate, no threshold,
no cap, no label.** `G-T5` PASS on `C4` stands, A2's `R` band stands, `E1`–`E6`
stand, the 320 core-min ceiling stands.

### D2.1 ⚡ D1.6's STANDING REPORTING CONDITION IS RETRACTED — IT MISLEADS IN THE OPPOSITE DIRECTION

D1.6 required every report to quote *"the ladder needs 20.9×–156.8×"* beside any
measured factor. **That range is a required PRESSURE-SOLVE factor. The required
WALL factor is 11.5352× (230,704 / 20,000 core-min). They are different
quantities.** Quoting the pressure-solve range next to a measured **wall** factor
reads as *"still hopeless"* when the measurement says otherwise. **The condition
was written to stop over-claiming and had begun to enforce under-claiming.**

**Retracted by the heat-transfer supervisor after stage 1. Replaced, verbatim,
with what the evidence supports and no more:**

> *"On 40 ramp steps at L2, `C5` measured **13.56×** wall against a required
> **11.5352×**, and `C4` measured **11.37×**. This does NOT establish that the
> ladder fits inside 20,000 core-minutes: the measurement covers 40 of the
> ladder's 11,800–47,200 steps, it is the **ramp and not the soak**, and no
> extrapolation is established. The pressure-share bracket [20.9, 156.8] was a
> required PRESSURE-SOLVE factor and must not be quoted beside a wall factor."*

The lane's inference — that `B0`-type configurations stall more as the field
settles, so `C5`'s margin would likely **grow** — **stays labelled an inference
and is not banked.**

### D2.2 THE REPRODUCTION CONTROL WORKED AGAINST ITS AUTHOR ON ITS FIRST USE

Recorded plainly because it is the strongest evidence in this probe for the
instrument itself.

This lane reported that contention it had introduced caused `C2` and `C3` to
cap-stop. **The supervisor authorised the re-run partly on that explanation. The
re-run destroyed it:** `C1` contended/alone is **1.085×**, and **`C2` and `C3`
capped again running ALONE** (rc 124, 39 and 38 steps). `E3` and `E4` stand on
their own merits.

> **The ruling was right for a reason its author did not have, and the only
> reason the lab knows that is D1.4 — the control that required the numbers to be
> registered BEFORE the re-run. It falsified the claim of the person who wrote
> it, on its first use.** All three arms reproduced their registered integers
> exactly (901/50,281, 901/40,230, 901/42,293) across 40, 39 and 38 steps under
> different conditions, so the reproduction is not in doubt and the falsification
> is not an artefact.

### D2.3 STAGE 2 RUNS THE REGISTERED WINNER — **`C4`, NOT `C5`**

`C5` has the better wall factor (13.56× against `C4`'s 11.37×). **`C5` is NOT the
`G-T5` winner and is NOT substituted.** §6 step 8 says *"the winner"*; `G-T5`'s
winner is `C4` at 60.11×; **`C4` runs.**

> **Swapping in `C5` because the lab now prefers its metric would be choosing the
> arm after seeing the data — the exact move this probe exists to prevent, at the
> last step, on an otherwise clean result.**

`B0` and `C4` on **L1** and **L3**, one arm at a time per D1.3. Caps unchanged:
L1 9.667 core-min each (`timeout 290 s`), L3 53.333 each (`timeout 1600 s`);
stage 2 total **126.00**. Spent 163.290; **worst case 289.29 of 320 — 30.71
core-min of headroom, which is tight. An overrun STOPS the run (rule 12); nothing
is extended.** `P-3` is scored as registered (max/min ≤ 3.0 across L1/L2/L3),
using §3.2's frozen per-level feasibility thresholds **4.500e-07 / 6.500e-07 /
1.000e-06**.

**§5.1 STILL BINDS: NO LADDER LAUNCHES ON THIS RESULT, whatever `P-3` says.** What
comes next — whether a successor gate is written on WALL COST rather than
iterations, and whether the win survives the soak rather than the ramp — **is a
new registration with its own cost, and where it touches the A1.3 ceiling it is
Sanaa's.** It is not drafted here; this probe ends at a report (§6 step 9).

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

<!-- END OF T25R5 PRE-REGISTRATION v1.4 -->

---

## Addendum D3 — 2026-09-02T~23:30Z. **THE PROBE IS CLOSED.** What it established, and the one thing it did NOT

**Version v1.5. Lines whose number changed above this section: 0.**
Addendum. **Alters no gate, no threshold, no cap, no label.** `G-T5` PASS on `C4`
stands; `P-3` LOSES at 6.7452; A2's `R` = 20.4545 stands; `P-2` LOSES; `E1`–`E6`
stand; the 320 core-min ceiling stands. **Nothing launched and nothing launches
(§5.1).**

### D3.1 WHAT THE PROBE ESTABLISHED

- **`G-T5` PASSES** on `C4` (PCG + tuned GAMG preconditioner) at **60.11×**,
  equivalence holding to `max|ΔT| = 2.4e-08 K` against a `1.0e-03 K` threshold.
- **`P-2` LOSES**, and it was registered as the better outcome. **The stall floor
  was CONFIGURATIONAL, not arithmetic** — §0.4's round-off-in-a-1/h-term
  attribution was **wrong**. Both Krylov arms show **zero** pinned solves against
  `B0`'s 310.
- **A2's `R` = 20.4545 ≥ 3.0** — the coarse-grid correction **is** contributing.
  **§1.2 was wrong about the mechanism:** the defect was never that multigrid does
  nothing, it was **GAMG used as a standalone solver, which stalls.**
- **`P-3` LOSES**: `C4`'s spread is **6.7452** against 3.0 — a real improvement on
  the re-measured baseline's 10.6694, and outside the gate.
- **⚡ THE WIN DECAYS WITH MESH REFINEMENT: 9.67× (L1), 11.37× (L2), 5.24× (L3)**,
  and it decays hardest exactly where the ladder's cost lives — `S3` at L3 is the
  costliest run. Carrying the measured factors through A1.1's frozen pricing gives
  **Σ CAP 24,709 core-min against the 20,000 ceiling — a ×1.24 breach on the most
  favourable reading available.** A number that fails **even with the assumptions
  stacked in its favour** is a stronger negative than one that fails on neutral
  assumptions.
- **Five bit-for-bit baseline reproductions** (`B0_L1`↔`P1`, `B0_L2`↔`P2`,
  `B0_L3`↔`P3`, and `C1`/`C2`/`C3` against D1.4's registered integers).

### D3.2 ⛔ THE ONE THING THIS PROBE DID **NOT** ESTABLISH — **`C5` AT L3 IS UNMEASURED**

> **`C5` WAS NEVER RUN AT L1 OR L3. ITS BEHAVIOUR AT THE LEVEL THAT DOMINATES
> LADDER COST IS *UNMEASURED*, NOT ANSWERED.**

`C5` (PCG + `DIC`, no multigrid) had the **best** L2 wall factor — **13.56×**,
**above** the required 11.5352× — and stage 2 correctly ran **`C4`**, the
registered `G-T5` winner, rather than the arm the lab had come to prefer (D2.3).
That was the right call and it leaves a real gap.

**So what is established is that `C4`'s advantage decays with refinement. It is
NOT established that `C5`'s does.** The arm with the best measured wall factor has
never been measured at the level that dominates ladder cost.

> **A READER MUST NOT INFER FROM D3.1 THAT THE LADDER IS DEAD FOR EVERY
> CONFIGURATION. On this arithmetic it is dead FOR `C4`. For `C5` at L3 the
> question is UNMEASURED.**

Not a defect and not a task: naming an unmeasured question at closure is what
stops it being silently converted into a settled negative.

### D3.3 TWO INSTRUMENT DISCLOSURES, RECORDED RATHER THAN LEFT IN A MESSAGE

1. **`compare_arms_t25R5.py` hardcoded the arm to `_L2`**, so a caller comparing
   `C4` against `B0_L1` compared **two different meshes**. **It did no damage for
   one reason only: the comparator REFUSED on differing cell counts** — the
   default-deny design catching an error its caller made, not one its author
   anticipated. **A refusal that saves you is evidence the refusal was worth
   building.** Repaired: it now takes `--level` and infers it from the base case's
   suffix.
2. **A diagnostic print rendered a minimum residual of `4.2567e-09` as `"0.0"`**
   through `round(v, 4)`. **A displayed zero that was not a real zero**, in a lab
   whose rule 3 exists for exactly that. There are no zeros in that log — 1,200
   solves, all positive — and the committed scorer formats `%.3e`, so nothing
   downstream consumed it. **It is known to be harmless only because it was
   checked rather than reasoned past.** Companion to **L-439**, whose subject is a
   tolerance below the noise floor; this one is a *formatter* below the noise
   floor.

### D3.4 COST — FINAL, rule 12

| item | core-min |
|---|---|
| stage 0 (`D0`, `B0_L2`) | 18.600 |
| stage 1 contaminated batch — **WASTE, CAUSED BY THIS LANE** | **70.533** |
| stage 1 clean (5 arms, sequential) | 74.157 |
| stage 2 (4 arms, sequential) | 44.233 |
| **cumulative** | **207.523** of the **320** registered ceiling |

**$0.1774 — DERIVED, NOT MEASURED**, at $0.0513/core-h,
`cost_basis = REPORTED-BY-OWNER`; the box cannot read its own billing. **The
70.533 core-min of waste is named and is folded into no actual/predicted ratio**
(`COMPUTE_BUDGET_CHARTER` §6).

### D3.5 CLOSURE

**The probe ends at a report (§6 step 9). No ladder launches (§5.1). Nothing is
staged for a successor.** The successor question — a gate written on **wall cost**
rather than iterations, whether the win survives the **soak** rather than the
ramp, and whether **`C5`'s L3 behaviour differs from `C4`'s** — is a **new
registration** with its own cost, drafted by the supervisor; where it touches the
A1.3 ceiling it is **Sanaa's**.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

<!-- END OF T25R5 PRE-REGISTRATION v1.5 — PROBE CLOSED -->
