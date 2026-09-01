# T25R2 — 8-cell aviation battery module, **RESOLVED COOLING CHANNELS**, true transient conjugate, at **SANAA'S VOLUMETRIC LOADS** and at the numerics **MEASURED** by the T25RF probe: PRE-REGISTRATION

**Version 1.0. Written 2026-09-01T05:19Z (`date -u` at write) by a heat-transfer
`lab-lane` for `heat-transfer-supervisor`.**
Repository HEAD read at write: `239fd2ef7e906969ae9030e5c2e62258044826ab`
(peers commit constantly; the binding sha is this document's own commit).

**THIS DOCUMENT IS FROZEN BY ITS COMMIT SHA. NO COMPUTE OF ANY KIND HAS RUN FOR
THIS RUNG — NO SOLVER, NO `blockMesh`, NO `splitMeshRegions`, NO `checkMesh`, NO
STAGING, NO FEASIBILITY PROBE.**

**Rule 2's own pre-compute test, performed and shown.** The registered case root
is `verification/runs/T-family/T25R2_MODULE_runs/`. At write it holds **exactly
four files and no directory**:

```
analyse_t25R2.py   mark_done_t25R2.py   stage_t25R2.py   run_one_t25R2.sh
```

**`T25R2_L1`, `T25R2_L1_OC20`, `T25R2_L2` and `T25R2_L2_DT025` DO NOT EXIST**
(`ls -d .../T25R2_*` → *"No such file or directory"*, run by this lane at write).
Every gate, threshold, cap and label below was therefore fixed before the first
byte of this rung's compute, which is the entire evidentiary content of
`CLAUDE.md` rule 2.

Verdict vocabulary is fixed by `CLAUDE.md` rule 1 and is used nowhere loosely:
`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`.

---

## 0. WHAT THIS RUNG IS, WHY T25R IS GONE, AND WHAT NO READER MAY TAKE FROM IT

### 0.1 What it is, and what it inherits verbatim

T25R2 is the **replacement registration** for the resolved-channel aviation
battery module. **It inherits most of `docs/campaigns/T-family/T25R_PREREGISTRATION.md`
verbatim in substance**, because most of that document was right and rewriting a
correct clause for the sake of a new file is how a family loses a standard:

- **the geometry** (§2.1) — 8 cells, `Lx` 0.100 m, `Ly` 0.030 m, 3 mm gaps,
  7 **parallel** channels, module height 0.261 m, the 50 mm inlet and 100 mm
  exit plenums, adiabatic casing and cell ends;
- **the two mesh levels** (§2.2) — `r = 1.5` exactly in both resolved
  directions, 16,608 and 37,368 cells, cell-count ratio **2.2500 exactly**;
- **the wall layers** (§2.3) — `Re_Dh = 3200` disclosed transitional,
  `y(y⁺=1) = 2.587e-05 m`, first cell 5.175e-05 m at L1, per-cell expansion
  ≤ 1.15, the solid `Bi = 0.27` justification for no through-thickness layer;
- **the mesh quality gate** (§2.4) — `Mesh OK`, max non-orthogonality < 70,
  max skewness < 4, min cell volume > 0;
- **the time-step derivation** (§3.3) — `deltaT = 0.5 s` from the 60 s pulse
  edge and the lumped `τ`, **not** from a Courant number, with `Co ≈ 1600`
  reported and not controlled, and the "what is given up" paragraph;
- **`g = (0 0 0)` and the vacuous-Richardson disclosure** (§3.6);
- **the D1 / D2 / D3 criterion structure** and the §5.2 parallel-channel
  disclosure;
- **the energy-conservation gate** at 2.0 % with its planted +10 % source
  control (§6.2);
- **the strict completion rule** with the age guard on `0/module/T` (§6.4);
- **the nine instrument-admission clauses** (§7.1) and the six readers (§7.2);
- **the T20 citation, and the truth about it** (§6.1);
- **the honesty gate** (§0.3);
- **the refusal to compute an order from two points** (§0.2, §6.3).

**Four things change, and only four.** They are §4 (the load), §3.4 (the
numerics), §3.5 (the outer-loop gate) and §8 (the cost). Each has its own
section and its own justification, and each is forced by something measured
since 03:39Z rather than chosen.

### 0.2 ⚠ WHY T25R EXISTS NO MORE, AND WHY THIS IS NOT AN AMENDMENT

**`T25R_L1` IS `NOT A RESULT`.** Measured, from artifacts this lane read:

| clause | evidence |
|---|---|
| rc ≠ 0 | `T25R_MODULE_runs/T25R_L1/STATUS.T25R_L1` — `rc=134`, `wall_s=6`, `core_min=0.100`, `capped=no` |
| a fatal, and the last time far short of `endTime` | `T25R_L1/log.solve` — **one** `FOAM FATAL`, *"Negative initial temperature T0: -14.4619608928"*, last time **1.5** against `endTime` 900 |

Two clauses of §6.4 fired, and the run's own §3.5 gate failed **2 of the 2 steps
it reached**. `T25R_L2` and `T25R_L2_DT025` never launched.

**T25R's gates closed at its first compute** (`VERIFICATION_CHARTER.md` §2d.2,
§2i and T25R's own §10): the earliest build-compute artifact this lane can date
is `T25R_L1/log.blockMesh`, mtime **2026-09-01T04:06:31Z**. **After first
compute, a gate, threshold, cap or label cannot be changed by any route** — not
by amendment, not by addendum. Sanaa's 04:20Z loads change the registered source
term, which changes the energy gate's `E_gen`, the pulse dictionary and every
registered prediction; the T25RF probe's numerics change `nOuterCorrectors` and
therefore the cost model; and §3.5's threshold loses its calibration entirely.
**Those are gate-altering changes. They require a NEW registration, and this is
it.**

**T25R IS NOT EDITED.** `T25R_PREREGISTRATION.md`, `analyse_t25R.py`,
`mark_done_t25R.py` and `run_one_t25R.sh` are frozen and untouched by this rung
(`CLAUDE.md` rule 6). `T25R_L1`, `T25R_L2` and `T25R_L2_DT025` are **evidence**
and are read-only here; `stage_t25R2.py` hashes the source tree before and after
every copy and **refuses** if a single byte moved.

### 0.3 WHAT T25R2 INHERITS FROM T25R AND FROM T25RF: **NOTHING BUT TEXT**

- **No number from `T25R_L1` is a result here.** It is `NOT A RESULT`.
- **No number from T25RF is a result here.** T25RF is an **ungated feasibility
  rung** (`VERIFICATION_CHARTER.md` §2m); its own note states, clause 1, that it
  *"closes no gate belonging to any other registration"* and that a future T25R2
  *"freezes its own pre-registration and runs again"*. Its measurements
  **inform** §3.4, §3.5 and §8 of this document — that is what a feasibility
  rung is for — and **none of them is this rung's answer**.
- **T25RF did not consume this registration's first-compute event.** T25R2's
  first compute is its own staging, and it has not happened.

### 0.4 THE FIVE THINGS THIS RUNG DOES NOT PRODUCE

1. **NO ROACHE TRIPLE, NO GCI, NO OBSERVED ORDER — spatial or temporal.** Two
   mesh levels are **two points**. §6.3 registers the mesh pair and the step
   pair as **SENSITIVITY DIFFERENCES** and nothing else, and the comparator has
   no code path that computes an order (proved by token search in its own
   `--selftest`). **⚠ `T25R2_L1_OC20` IS NOT A THIRD MESH LEVEL.** It is L1's
   mesh at a different **sweep count**; it enters no sensitivity panel, and no
   order may be read from the L1 / L1_OC20 / L2 collection under any pretext.
   **This family's most repeated failure is smuggling an order out of two
   points. It does not happen here.**
2. **NO INHERITED PASS FROM T20.** See §6.1 — the T20 exact gate has **NOT
   discharged**; it is on record as `NOT A RESULT` on its own registered terms.
3. **NO TRANSIENT FLOW DYNAMICS.** §3.3, inherited verbatim.
4. **NO CELL-TO-CELL STREAMWISE ORDERING.** §5.2, inherited verbatim: the 7
   channels are **parallel** and no cell is downstream of another. **This is a
   disclosure, not a substitution**, and it remains flagged for Sanaa's ruling.
5. **NO ANISOTROPIC CONDUCTIVITY, NO LAMINAR-VS-SST MODEL-FORM BAND.** Deferred
   (§9).

### 0.5 THE HONESTY GATE, REGISTERED IN ADVANCE

- **SANAA'S RISE RULING IS BINDING AND IS THE FIRST CLAUSE OF THIS GATE**
  (verbatim, `etc/sessions/2026-09-01T0420Z_sanaa_battery_loads_and_overnight_priorities.md`):

  > *"The temperature rise is then whatever the physics gives; I am not
  > prescribing 'tens of kelvin', I am prescribing realistic heat density. **If
  > the result is 8 K, 8 K is the answer.**"*

  **NOTHING IN THIS RUNG IS TUNED TOWARD A TARGET.** The load is hers, given
  verbatim; the predictions of §4.3 are derived from it here, before the run, so
  that they cannot be fitted to it afterwards; and the measured rise is the
  deliverable whatever it is. That her illustrative 8 K falls inside the band
  her own basis implies (§4.3) is a **consequence of the basis**, not of any
  choice made after seeing it, and it is named here so no later reader mistakes
  agreement for tuning.
- **A partially converged transient is NEVER presented as complete.** A run that
  fails any clause of §6.4 is `NOT A RESULT`, and no figure, table or screen
  derived from it may carry a verdict word. There is no "roughly converged".
- **The 0.4 K feasibility run stays off every Act C screen**, and so does every
  T25RF arm and every T25R case.
- **The 600 core-min cap stands** and rule 12 stands with it: an overrun **stops
  the run**; it does not get a new budget.

---

## 1. THE REGISTERED RUN SET — FOUR RUNS, NAMED AND CLOSED

| id | mesh | `deltaT` | steps | `nOuterCorrectors` | purpose |
|---|---|---|---|---|---|
| `T25R2_L1` | L1 | 0.5 s | 1800 | **10** | coarse arm of the **mesh pair**; first arm of the **outer-loop gate** |
| `T25R2_L1_OC20` | L1 | 0.5 s | 1800 | **20** | second arm of the **outer-loop gate** (§3.5). Identical to `T25R2_L1` **in every other respect** |
| `T25R2_L2` | L2 | 0.5 s | 1800 | 10 | fine arm of the mesh pair; **primary reporting run** |
| `T25R2_L2_DT025` | L2 | 0.25 s | 3600 | 10 | second arm of the **step pair** |

**Four runs. No fifth.** Anything else is a different rung with its own
pre-registration. An L2 outer-loop arm and a third mesh level are **priced and
refused** at §8.5 and §8.6.

`case_root = /home/ubuntu/Certonomous/verification/runs/T-family/T25R2_MODULE_runs/`

---

## 2. GEOMETRY, MESH AND THE TWO LEVELS — **INHERITED, AND THE MESH IS REUSED**

### 2.1 Geometry — T25R §2.1, unchanged

8 cells; `Lx` 0.100 m (flow), `Ly` 0.030 m (thickness), depth 1.000 m **EMPTY**;
channel gap 0.003 m; **7 channels, all PARALLEL, flow in `+x`**; module height
0.261 m = 8×0.030 + 7×0.003; inlet plenum 0.050 m, exit plenum 0.100 m, total
channel length 0.250 m. Cell *i* occupies `y ∈ [(i−1)·0.033, (i−1)·0.033+0.030]`.
**Cells 1 and 8 have ONE channel face; cells 2–7 have TWO.** Casing faces
(`y=0`, `y=0.261`) and cell streamwise ends (`x=0`, `x=0.100`) are **adiabatic,
declared**.

### 2.2 The mesh levels — `r = 1.5`, unchanged

| | L1 | L2 |
|---|---|---|
| `NX` total per channel | 76 | 114 |
| `NY` across each 3 mm channel | **24** | **36** |
| `NY` across each 30 mm cell | 12 | 18 |
| fluid cells | 12,768 | 28,728 |
| solid cells | 3,840 | 8,640 |
| **total cells** | **16,608** | **37,368** |

**Cell-count ratio L2/L1 = 2.2500 exactly.** `Δx` in the cell zone is **2.5 mm**
at L1 and **1.6667 mm** at L2, which is why `Co ≈ 1600` at L1 and `≈ 2400` at
L2 — a fact §3.5 depends on and states.

### 2.3 Wall layers — T25R §2.3, unchanged

`Re_Dh = 3200` (transitional, **DISCLOSED**); Blasius `f = 0.042010`;
`τ_w = 0.4033 Pa`; `u_τ = 0.5798 m/s`; `y(y⁺=1) = 2.587e-05 m`; first cell
**5.175e-05 m** at L1 and `/1.5` at L2, so `y⁺ ≈ 1` at L1 and `≈ 0.67` at L2.
Symmetric double grading, 12 cells per half-channel at L1 and 18 at L2, per-cell
expansion ≤ 1.15. Solid cells uniform across thickness (`Bi = 0.27`), **a
choice, disclosed**.

### 2.4 Mesh quality gate — the thresholds are inherited **BLIND**, the values are **ALREADY KNOWN**, and that is disclosed

**REGISTERED, and unchanged from T25R §2.4:** `checkMesh` on each region of each
level must return **"Mesh OK"** with **zero** failures, **max non-orthogonality
< 70**, **max skewness < 4**, **min cell volume > 0**. A level failing any of
these is `NOT A RESULT` for every run on that level; the other level is
untouched.

> **⚠ THE DISCLOSURE THIS GATE OWES, AND IT IS NOT A SMALL ONE.** T25R2 **reuses
> meshes that T25R already built and already measured** (§2.5). **The thresholds
> above were frozen blind — at T25R's 03:39Z write, before any mesh existed —
> and are inherited unchanged. The MEASURED VALUES, however, are already on disk
> and this lane has read them.** They are, from
> `T25R_MODULE_runs/T25R_L{1,2,2_DT025}/log.checkMesh.{module,coolant}`:
> **`Mesh OK` on every region of every level, max non-orthogonality `0`
> (average 0), max skewness `1.33e-13`–`2.91e-13`, max cell openness ~1.6e-16.**
> Cell counts read from the same logs: L1 3840 + 12768 = **16,608**; L2 and
> L2_DT025 8640 + 28728 = **37,368** — exactly §2.2.
>
> **This gate therefore retains its FORCE and loses its BLINDNESS, and it would
> be dishonest to present it as a gate written without knowledge of its answer.**
> It still refuses a mesh that fails, it is still evaluated by the comparator on
> a `log.checkMesh` in the T25R2 case directory, and a failure still makes the
> level `NOT A RESULT`. What it is **not** is evidence that the lab could not
> have chosen the threshold to fit. The threshold's blindness rests on T25R's
> 03:39Z freeze, which is a real freeze, and this document points at it rather
> than claiming the credit a second time.

### 2.5 Meshing route — ⚠ **THE MESH IS REUSED, NOT REBUILT, AND THE REUSE IS PROVED**

**REGISTERED: T25R2 REUSES the meshes at
`verification/runs/T-family/T25R_MODULE_runs/T25R_L{1,2,2_DT025}` and DOES NOT
REBUILD THEM.** `T25R2_L1` and `T25R2_L1_OC20` both reuse `T25R_L1`.

**Three reasons, and each alone is sufficient:**

1. **The load changes no cell.** Sanaa's load enters as an `fvOptions`
   `scalarSemiImplicitSource` on `h` with `volumeMode specific` and
   `selectionMode all`. It touches no point, no face, no zone and no boundary. A
   rebuild would produce the same mesh.
2. **A rebuild costs build compute**, which under `VERIFICATION_CHARTER.md`
   §2d.2 **closes this registration's gates** — and §10 puts the supervisor's
   diff read *before* any compute for exactly that reason.
3. **A rebuild would put a live rule-6 referral on the critical path.**
   `build_t25R.py` differs from its committed blob and is under referral (§12.2).
   This lane does not run it, edit it, commit it or revert it.

**HOW THE REUSE IS VERIFIED — `stage_t25R2.py`, and it is a PROOF, not an
assertion.** For each case:

- every file under the source's `constant/` and `0.orig/` is **sha256-hashed**,
  the trees are copied, and the destination is hashed again: **identical file
  sets and identical digests, file for file, or REFUSE**;
- the **source tree is hashed a second time after the copy** and must be
  unchanged — the stager must be **incapable** of altering the evidence it
  reads, and a change is a REFUSAL naming `T25R_L1` as the record of the 04:09Z
  divergence;
- the **cell count is re-derived from `constant/<region>/polyMesh/owner`'s own
  header** and checked against §2.2's registered numbers, per region;
- `log.blockMesh`, `log.splitMeshRegions` and both `log.checkMesh.<region>` are
  copied so §2.4's gate has its evidence **inside** the T25R2 case directory;
- **nothing from the T25R run is copied**: not `0/`, not any time directory, not
  `log.solve`, not `STATUS.*`, not `postProcessing/`, not the abandoned
  `*.CELLZONES_FAILED*` logs. A `0` or a time directory in the destination is a
  **REFUSAL** (rule 4's age guard would be unevaluable).

**THE STAGER RUNS NOTHING, AND THAT IS A CHECKED PROPERTY.** It contains no
`subprocess`, no `os.system`, no `os.exec*`, no `os.popen`, no `os.spawn*` and
no `shutil.which` — its own `--selftest` proves this by token search over its
source. It **cannot** mesh and **cannot** solve.

**THE STAGER IS GRADED BY THE COMPARATOR, IN THE SAME INVOCATION.** After
writing, it calls `analyse_t25R2.numerics_check()`, `pulse_table_check()` and
`mesh_quality()` on what it just wrote. **It cannot stage a case the comparator
would refuse.**

**A CONFIRMATORY `checkMesh` IS PERMITTED AT STEP 3 AND IS COSTED** (§8.2). If
one is run on the staged copy its log replaces the copied one; §2.4's gate is
evaluated on whichever `log.checkMesh.<region>` sits in the T25R2 case
directory, so both routes are covered by the same registered gate.

---

## 3. NUMERICS — **MEASURED BY THE T25RF PROBE, NOT CHOSEN**

### 3.1–3.3 The time step — T25R §3.1–§3.3, inherited unchanged

The cost argument, the two independent reasons `max Co = 1` is a **choice** and
not a stability requirement on an implicit PIMPLE solver, the quasi-steady
framing (`L/U = 31.25 ms` against `τ ≈ 696 s` interior / 1392 s end — a factor
2.2e4), and the derivation of `deltaT = 0.5 s` from **(a)** the 60 s pulse edge
at 1 % (`dt ≤ 0.6 s`) and **(b)** the lumped exponential at 0.1 %
(`dt ≤ 1.39 s`), with **(a)** binding. `adjustTimeStep no`; `maxCo` is inert and
is **not written into `controlDict` at all**. `Co = U·dt/Δx = 8×0.5/0.0025 =
**1600** at L1` and **2400 at L2**, **reported, not controlled**. The "what is
given up / what survives intact" paragraph of T25R §3.3 stands verbatim.

**The lumped `τ` is unchanged by the new load**, because `τ = ρ c_p V/(hA)`
contains no `q`.

### 3.4 REGISTERED NUMERICS — **the T25RF arm A2T dictionaries, verbatim**

**⚠ THE MECHANISM IS REGISTERED HERE BECAUSE IT IS THE POINT, AND IT IS
TRANSFERABLE.** `T25R_L1` did not diverge because of its loads. It diverged
because of a **missing dictionary key**:

- `chtMultiRegionFoam.C:111` sets `finalIter = (oCorr == nOuterCorr-1)`;
  `fluid/solveFluid.H:3` calls `mesh.data().setFinalIteration(true)` for that
  sweep;
- `fvMatrix::relax()` (`src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C:1249`)
  resolves its relaxation key as `psi_.select(mesh.data().isFinalIteration())`;
- `GeometricField::select(bool)`
  (`src/OpenFOAM/fields/GeometricFields/GeometricField/GeometricField.C:1179`)
  returns **`name() + "Final"`** when that flag is set;
- **OpenFOAM keyword regexes match in FULL**, so T25R's `"(U|h|k|omega)"` **does
  not match `UFinal` or `hFinal`**. `UEqn.relax()` and `EEqn.relax()` found **no
  entry** on the final sweep and applied **no relaxation at all**;
- at `Co ≈ 1600` the `1/dt` term contributes almost nothing to the momentum
  diagonal, so that one unrelaxed sweep had **no diagonal dominance left to
  stabilise it**.

**CONFIRMED BY MEASUREMENT, not merely read at source.** T25RF arm **A0** ran
the identical case under **Sanaa's NEW loads** and reproduced the divergence to
the same three time steps, the same Courant sequence (1600 → 2643.9 → 77025.9)
and `T0 = -14.458` against the reference run's `-14.459`. **The divergence is
NUMERICAL, not load-driven.** Adding the `Final` keys — and nothing else — took
the identical case to `Time = 30` with `rc = 0`, `End` present, and continuity
`sum local` **falling** from 2.45e-3 to 4.57e-8 instead of climbing to 125.93.

**REGISTERED: arm A2T's dictionaries, committed at
`verification/runs/T-family/T25RF_runs/A2T/system/coolant/fvSolution` and
`.../A2T/system/fvSolution`, written out by `stage_t25R2.py`:**

| dictionary | registered content |
|---|---|
| `system/fvSolution` | `PIMPLE { nOuterCorrectors <10 or 20>; nNonOrthogonalCorrectors 0; }` — **10** for `T25R2_L1`, `T25R2_L2`, `T25R2_L2_DT025`; **20** for `T25R2_L1_OC20` |
| `system/coolant/fvSolution` `relaxationFactors` | `fields { p_rgh 0.3; p_rghFinal 0.3; }` `equations { U 0.7; UFinal 0.7; h 0.7; hFinal 0.7; k 0.7; kFinal 0.7; omega 0.7; omegaFinal 0.7; }` — **every `Final` key written LITERALLY** |
| `system/coolant/fvSolution` `solvers` | `"p_rgh.*"` GAMG, **`tolerance 1e-8`**, `relTol 0.01`, GaussSeidel; `p_rghFinal` `tolerance 1e-8`, `relTol 0`; `"(U\|h\|k\|omega)"` PBiCGStab/DILU `tolerance 1e-10` `relTol 0.01`; `"(U\|h\|k\|omega)Final"` `tolerance 1e-10` `relTol 0`; `rho` PCG/DIC 1e-8 |
| `system/coolant/fvSolution` `PIMPLE` | `momentumPredictor true; nCorrectors 2; nNonOrthogonalCorrectors 0;` — **`frozenFlow` left at its default `false`** |
| `system/module/fvSolution` | `h` PCG/DIC `tolerance 1e-12` `relTol 0`; `hFinal { $h; }`; `relaxationFactors { equations { h 1; } }` |

**`frozenFlow` IS AVAILABLE AND IS STILL DELIBERATELY NOT USED.** T25RF arm A3
was registered to reach for it **only if A1 and A2 both failed**. Both held, **A3
was never reached and never run**, and T25R §3.3's refusal of `frozenFlow`
stands untouched. **The flow field in this rung is solved, not imposed.**

**⚠ THE REGISTERED `p_rgh` TOLERANCE IS 1e-8, AND 1e-9 IS UNREACHABLE.**
Measured, T25RF addendum A2: **GAMG stalls at ~4.4e-9 on this system**; **266 of
600** `p_rgh` solves in the 5-sweep arm and **608 of 1200** in the 10-sweep arm
terminated at `maxIter` **1000** without reaching 1e-9, and the waste **grew as
the field settled** (A2's cost per step rose 1.60 s → 11.09 s). Relaxing one
digit gave last-sweep `Min/max T` at `Time = 30` of **292.985283351 /
294.125534239 K in BOTH arms — agreeing to 0.000e+00 K**, `maxIter`
terminations **608 → 0**, and total GAMG iterations **627,533 → 25,770, a 24.4×
reduction**. **Those 601,763 discarded iterations changed no digit of the
answer.** Under `CLAUDE.md` rule 12 that is **WASTE, named**, never absorbed into
a cost ratio.

**⚠ THE CRASH MECHANISM WAS A MISSING KEY, SO THE KEYS ARE VERIFIED IN THE
DICTIONARY THAT RAN.** `analyse_t25R2.numerics_check()` reads the case's own
`system/fvSolution` and `system/coolant/fvSolution` before grading anything and
**REFUSES (exit 2)** if:

- any of `p_rghFinal`, `UFinal`, `hFinal`, `kFinal`, `omegaFinal` is absent;
- any registered relaxation factor differs from the value above;
- any of those keys is written as a **quoted regex** — **refused even though a
  regex would match**, because the failure being guarded against is a pattern
  that *looks* like it matches and does not, and a check that had to
  re-implement OpenFOAM's regex resolution to decide would be the same reasoning
  that produced the bug. **The registered form is decidable by reading.**
- the `p_rgh` linear tolerance is not 1e-8;
- there is no top-level `PIMPLE` dict, or `nOuterCorrectors` is not the value
  §1 registers **for that case**.

This is `L-221`/`L-222` in its general form: **a lesson is not applied until
every call site asserts it.** A registration that wrote the missing key and then
graded a run without checking the key was there would have learned nothing.

**All other numerics are T25R §3.4's, unchanged:** `chtMultiRegionFoam`;
`adjustTimeStep no`; `endTime` 900 s; `writeControl runTime` / `writeInterval`
5 s; `writePrecision 12`; `Euler` in both regions, **declared first order in
time**; `bounded Gauss upwind` on `U` and `Gauss upwind` on `h,k,omega`,
**declared first order in space and a registered accuracy cost**;
`kOmegaSST` with `*LowRe` treatments; `g = (0 0 0)`; radiation **off**,
disclosed; solid `kappa` **isotropic 3.0 W/mK** with the DISCLOSE it demands;
air `rho` 1.2, `cp` 1005, `k` 0.026, `mu` 1.8e-5, `rhoConst`; solid `rho` 2500,
`cp` 1000.

### 3.5 ⚠ THE OUTER-LOOP GATE — **T25R's §3.5 IS INVALID AND IS REPLACED**

#### 3.5.1 Why the old gate is dead

T25R §3.5 gated on the **last-sweep initial residual < 1e-6** (fluid) and
**< 1e-8** (solid), with a 5.0 % step allowance. **That threshold was calibrated
for an UNRELAXED final sweep.** T25R's own frozen `fvSolution` comment says so
in terms: the final sweep is *"unrelaxed by omission, which is what makes the
last-sweep initial residual of section 3.5 a meaningful convergence measure
rather than a relaxation artefact"*.

**That deliberate choice is what crashed the run** (§3.4). Relaxing the final
sweep fixes the crash **and destroys the gate's calibration**: a relaxed final
sweep's initial residual is a relaxation artefact, exactly what the comment
warned of. **A threshold whose calibrating assumption has been removed is not a
threshold**, and carrying it forward would be a gate in name only.

#### 3.5.2 ⚠ RULED: THE CENSUS IS A REPORT. THE GATE IS SWEEP-COUNT INDEPENDENCE, IN KELVIN.

> **The last-sweep residual census is RETAINED AS A REPORT, with NO THRESHOLD
> ATTACHED and NO VERDICT DERIVABLE FROM IT.** The comparator prints the worst
> and final-step last-sweep initial residual for `p_rgh`, `Ux`, `Uy` and `h` and
> compares them against nothing. **The retired threshold is STRUCTURALLY ABSENT
> from `analyse_t25R2.py`**, and `--selftest` proves it from the parsed module
> (not from its text, so a comment naming the retired constant cannot make the
> proof pass or fail): the only module-level name carrying `RESID` is
> `RESID_REPORT_FIELDS`, and no `OUTER_FAIL` fraction is bound anywhere.
>
> **Two REFUSALS survive on the census, and they are EVIDENCE CHECKS, not
> gates.** A `log.solve` with **no** `Initial residual` lines, or one in which a
> registered census field never appears, would let the census print a zero it
> could not have seen — `CLAUDE.md` rule 3's failure mode — so both **REFUSE**.
>
> **THE OUTER LOOP IS GATED INSTEAD BY DEMONSTRATED SWEEP-COUNT INDEPENDENCE, IN
> KELVIN, between `T25R2_L1` (10 sweeps) and `T25R2_L1_OC20` (20 sweeps),
> identical in every other respect.**

#### 3.5.3 WHY THIS IS FORCED BY MEASUREMENT AND NOT BY PREFERENCE

T25RF addendum A2 §3, measured: arms A1 and A2 differ **only** in sweep count
(5 vs 10) and their trajectories **separate and keep separating** — max T
differing by **1.05e-3 K at t = 1 s, 3.47e-3 K at t = 10 s and 6.02e-3 K at
t = 30 s**, which is **0.53 % of the 1.13 K rise** and **48.8 % of the
`10 × PLANT = 1.234e-02 K` signal scale**, after only **3.3 % of the case
duration**, and **still growing when the probe ended**.

**WE THEREFORE DO NOT KNOW THAT 10 SWEEPS IS CONVERGED.** T25R2 **demonstrates
it rather than assuming it.** The probe supplies **no** replacement measure for
what T25R §3.5 used to do — its own §7 says so — and **this section is that
replacement.**

#### 3.5.4 THE THREE DELTAS, THEIR THRESHOLDS, AND THE ARITHMETIC BEHIND THEM

Let `Δ(X) = |X(T25R2_L1_OC20) − X(T25R2_L1)|`, both L1, both `deltaT 0.5`.

`PLANT = 1.234e-03 K` — the registered reader-control perturbation, the smallest
shift **every** reader in §7.1 is **proved** able to see. `10 × PLANT =
1.234e-02 K` — the **D3 floor**: the smallest within-cell signal this rung is
willing to call signal at all.

| id | quantity | threshold | why that number |
|---|---|---|---|
| **O1** | max over all 8 cells and **every written time `t > 0`** of `Δ(T_i(t))` — the absolute trajectory | **≤ 1.234e-02 K = 10 × PLANT** | a trajectory that moves by **more than the smallest gated signal** when the sweep count is doubled is not a trajectory this rung can report |
| **O2** | `Δ( min_i [T_dn(i) − T_up(i)] at t = 60 s )` — **the D3 quantity itself** | **≤ 1.234e-03 K = 1 × PLANT** | this is the number **D3 gates**, so its sweep-count uncertainty is held to **ten per cent of D3's own floor** — one order below the threshold it could otherwise flip. Deliberately the tightest of the three, because it is the only one attached to a kelvin gate |
| **O3** | max over `t ∈ {60, 900 s}` of `Δ(` coolant outlet area-mean `T)` — **the D2 quantity**, and Sanaa's headline | **≤ 1.234e-02 K = 10 × PLANT** | D2 is a strict **inequality** with no kelvin threshold of its own, so O3 is held at the signal scale rather than at PLANT |

**ALL THREE MUST HOLD.** `t = 0` is **excluded from O1 and registered as
excluded**: both arms stage the **same** `0.orig`, so a `t = 0` comparison is
identically zero by construction and would be a planted zero dressed as
agreement.

**THE VERDICT, AND ITS PROPAGATION, FROZEN HERE:**

- three deltas inside their thresholds ⇒ the outer-loop gate is **`PASS`**;
- any delta outside ⇒ **`GATE FAIL`**, with all three deltas and their
  thresholds printed **beside every number this rung produced**;
- **⚠ A `GATE FAIL` ON THIS GATE MAKES EVERY ROW OF THIS RUNG `NOT A RESULT`.**
  `CLAUDE.md` rule 5 clause (1): a level that is **not iteratively converged** is
  `NOT A RESULT` whatever its value says, and sweep-count dependence **is**
  outer-loop non-convergence. This is rule 5's own mechanism — *"the gate can
  only turn a PASS or GATE FAIL INTO NOT A RESULT, never the reverse"* — and
  this lane has no authority to weaken it. **The outer-loop gate's own verdict is
  `GATE FAIL`; the physics rows it voids are `NOT A RESULT`.**
- an OC arm that has **not run** ⇒ the gate is **`PENDING`** and every physics
  row is withheld as `PENDING`. `PENDING` is a **queue state** (rule 1) and
  **never softens a `GATE FAIL`**.
- an OC arm that **ran and failed §6.4** ⇒ the gate is `NOT A RESULT` and so is
  every row.

**⚠ THE GATE CANNOT BE SKIPPED BY GRADING ONE CASE.** The comparator evaluates it
from `T25R2_L1` / `T25R2_L1_OC20` **whatever is named on the command line**, and
its `--selftest` drives that path: grading `T25R2_L2` alone, with no OC arms on
disk, yields `PENDING` on the gate and `PENDING` on the row.

**⚠ THIS ARM IS BUILT SO THAT IT CAN FAIL, AND IF IT FAILS THAT IS A REAL
FINDING.** Nothing here assumes the 10-vs-20 gap will be smaller than the
measured 5-vs-10 gap. A `GATE FAIL` says **10 outer sweeps is not enough at
`Co ≈ 1600`** — precisely what the probe could not settle — and the rung reports
it in those words rather than as an instrument problem.

#### 3.5.5 REGISTERED SCOPE, AND ITS LIMIT

**The outer-loop arm runs at L1 ONLY.** A `PASS` demonstrates sweep-count
independence **at L1 and at L1's Courant number (≈1600 at `Δx` 2.5 mm)**. **L2
runs at `Δx` 1.6667 mm and therefore at `Co ≈ 2400`, where the outer loop
converges no faster, so THE GATE DOES NOT CERTIFY L2 AND IS NOT REPORTED AS
DOING SO** — the comparator prints this scope beside every L2 number.

**The FAILURE direction does transfer.** If 10 sweeps is not enough at
`Co ≈ 1600` it is not enough at `Co ≈ 2400`, which is why a `GATE FAIL` at L1
voids **every** row while a `PASS` carries its L1 scope attached. **An L2
outer-loop arm is priced and refused at §8.5.**

### 3.6 `g = (0 0 0)`, and the Richardson check declared **VACUOUS**

T25R §3.6, unchanged. `Gr = 257.2`; `Re² = 1.024e7`; **`Gr/Re² = 2.51e-05`**.
Forced convection dominates by four and a half orders of magnitude and
`rhoConst` removes buoyancy from the equations regardless of `g`. With
`g = (0 0 0)` registered, a `Ri < 0.1` criterion is **identically zero by
construction**, cannot fail and cannot inform; it is **NOT reported as a passing
check**. Buoyancy is **OFF**, its neglect is a **declared omission**, and
dominance rests on the `Gr/Re²` arithmetic, not on any check this rung runs.

---

## 4. THE HEAT LOAD — ⚠ **SANAA'S VOLUMETRIC RATE IS THE REGISTERED QUANTITY**

### 4.1 Her order, verbatim, and what it rejects

`etc/sessions/2026-09-01T0420Z_sanaa_battery_loads_and_overnight_priorities.md`,
`[SANAA-DIRECT]`, ~04:20Z:

> *"Battery loads: set the heat source as a volumetric rate from a real cell,
> **not a per-cell wattage on a unit-depth model**. Takeoff: q‴ ≈ 1×10⁵ W/m³
> (≈40–50 W in a 100×30×150 mm cell, 5–8C class); cruise ≈ 2.5×10⁴ W/m³. State
> the basis in the assumptions box. The temperature rise is then whatever the
> physics gives; I am not prescribing "tens of kelvin", I am prescribing
> realistic heat density. **If the result is 8 K, 8 K is the answer.**"*

**She rejects T25R §4.2's construction by name.** T25R derived **210.00 W per
cell** on a **unit-depth slab** from a 350 Wh/L energy density, a 5C rate and a
4 % heat fraction, and then divided to get `q'''`. **That chain is gone.** The
volumetric rate is now the **input**, not the output.

### 4.2 THE ASSUMPTIONS BOX — **`q'''` FIRST, EVERYTHING ELSE DERIVED**

| # | quantity | value | status |
|---|---|---|---|
| 1 | **`q'''_takeoff`, `0 ≤ t < 60 s`** | **1.0 × 10⁵ W/m³** | **REGISTERED. Sanaa's, verbatim.** |
| 2 | **`q'''_cruise`, `60 ≤ t ≤ 900 s`** | **2.5 × 10⁴ W/m³** | **REGISTERED. Sanaa's, verbatim.** |
| 3 | her basis | *"≈40–50 W in a 100×30×150 mm cell, 5–8C class"* | **HERS, quoted** |
| 4 | real cell volume | `0.100 × 0.030 × 0.150` = **4.500e-04 m³** | DERIVED from 3 |
| 5 | **her basis is self-consistent, checked here** | `45.0 W / 4.500e-04 m³` = **1.0000e5 W/m³**; her 40–50 W band spans **8.889e4 – 1.111e5 W/m³**, which **brackets** 1.0e5 | **VERIFIED by this lane** |
| 6 | cruise in the real cell | `2.5e4 × 4.500e-04` = **11.25 W** | DERIVED |
| 7 | `q'''_takeoff / q'''_cruise` | **4.00** | DERIVED (T25R's was 25) |

**⚠ THE SECTION IS IDENTICAL; ONLY THE DEPTH DIFFERS; AND A VOLUMETRIC RATE IS
DEPTH-INDEPENDENT.** Her cell's **100 × 30 mm section is exactly the registered
2-D section** (`CELL_LX = 0.100 m`, `CELL_LY = 0.030 m`, §2.1). The only
difference is depth: **0.150 m hers, 1.000 m the OpenFOAM unit depth**. Because
`q'''` is a **volumetric density**, it **transfers exactly, with no conversion at
all** — which is precisely why she asked for it in this form.

**THE DERIVED PER-CELL WATTAGE, LABELLED AS DERIVED EVERY TIME IT APPEARS.** On
the 2-D unit-depth model `V = 0.100 × 0.030 × 1.000 = 3.000e-03 m³`, so

```
P_takeoff = 1.0e5 × 3.000e-03 = 300.0 W per cell PER METRE OF DEPTH
P_cruise  = 2.5e4 × 3.000e-03 =  75.0 W per cell PER METRE OF DEPTH
```

**These two numbers are a normalisation artefact of the unit-depth model and are
NOT claims about a real cell.** In her real cell the same `q'''` is **45.0 W**
and **11.25 W**. **No per-cell wattage is an input anywhere in this rung**; the
`fvOptions` table carries `q'''` in W/m³ under `volumeMode specific`, and the
comparator refuses any table that does not.

### 4.3 THE PREDICTIONS THIS BASIS IMPLIES — **REGISTERED BEFORE THE RUN**

Every one re-derived independently by this lane and shown, so that none can be
fitted after the fact.

| # | prediction | arithmetic | value |
|---|---|---|---|
| 1 | **adiabatic bound on the 60 s pulse rise** | `1.0e5 × 60 / (2500 × 1000)` | **2.400 K** |
| 2 | **adiabatic bound on the full 900 s rise** | `(1.0e5×60 + 2.5e4×840) / 2.5e6 = 2.7e7 / 2.5e6` | **10.800 K** |
| 3 | **coolant outlet rise, takeoff, quasi-steady** | `8 × 300.0 / (0.20160 × 1005) = 2400 / 202.608` | **11.845 K** |
| 4 | **coolant outlet rise, cruise, quasi-steady** | `8 × 75.0 / 202.608 = 600 / 202.608` | **2.961 K** |
| 5 | **steady interior cell-to-air rise at cruise** | `75.0 / (53.9 × 0.2)` | **6.957 K** |
| 5b | the same for an **end** cell (`A = 0.1 m²/m`) | `75.0 / (53.9 × 0.1)` | **13.914 K** |
| 6 | **total generated energy over 900 s** | `8 × 3.000e-03 × (1.0e5×60 + 2.5e4×840) = 0.024 × 2.7e7` | **648,000 J** |
| 7 | `ṁ_total` | `1.2 × 8 × (0.003 × 1.0) × 7` | **0.20160 kg/s** |
| 8 | lumped `τ`, interior / end | `ρc_pV/(hA)` at `h = 53.9` | **695.7 s / 1391.5 s** |
| 9 | solid streamwise conduction length in 60 s | `√(αt)`, `α = 1.2e-6 m²/s` | **8.5 mm** |

**⚠ `h = 53.9 W/m²K` IS DITTUS–BOELTER, DECLARED-REPRESENTATIVE, AND NOT
MEASURED.** It appears in rows 5, 5b and 8 and **nowhere else**. **It is imposed
NOWHERE in the solve** — the entire point of resolving the channel is that the
solve computes its own heat transfer coefficient. Rows 1, 2, 3, 4, 6 and 7 are
**independent of `h` entirely**.

**REGISTERED PREDICTION, IN THE FORM RULE 2 REQUIRES.** The rise at the end of
the pulse (`t = 60 s`) will be **of order 2.0–2.4 K**, bounded above by row 1.
The rise at `t = 900 s` will be **of order 6–11 K**: bounded above by row 2 and,
for interior cells, approaching row 5 as `t/τ` grows (`τ_interior = 695.7 s <
900 s`; `τ_end = 1391.5 s > 900 s`, so the end cells are still on the
storage-dominated branch and are bounded by row 2). **The measured value is the
deliverable whatever it is.**

**⚠ THE "TENS OF KELVIN" PHYSICS, RESTATED HONESTLY AND NOW MOOT.** T25R §4.3
found that a 60 s pulse cannot produce tens of kelvin in a body with
`ρc_p = 2.5e6 J/m³K` at any defensible aviation C-rate. **That finding stands and
is unchanged by the higher load**: even at Sanaa's `q'''`, **the ceiling over the
whole 900 s, with no cooling whatsoever, is 10.800 K** — a two-digit rise is at
the very edge of physically possible and only in the strictly adiabatic limit.
**Her 04:20Z ruling supersedes the question**: she is prescribing **heat
density**, not `ΔT`, and *"if the result is 8 K, 8 K is the answer."* **Nothing
in this rung is tuned toward 8 K, toward 10 K, or toward anything.**

### 4.4 The pulse dictionary — the trap already paid for, kept

`scalarSemiImplicitSource` on the enthalpy field **`h`**, `volumeMode specific`,
`selectionMode all`, `Function1 table`. **Three v2606 facts, carried forward
verbatim from T25R §4.5:**

1. **The field is `h`, NOT `T`.** The solid energy equation is in enthalpy; an
   entry on `T` is **never matched and never applied**, and OpenFOAM emits one
   non-fatal warning and then converges cleanly to a **silently unheated**
   solid — exactly the failure `CLAUDE.md` rule 3 exists for.
2. **`injectionRate` does not exist at v2606**; the accepted forms are `sources`
   (2206+) or the legacy `injectionRateSuSp`.
3. **`volumeMode` is MANDATORY**; a missing key is a fatal read and the wrong
   mode is a **silent scale error by exactly the zone volume**. `specific` is
   registered, so the entered values are in W/m³.

**THE REGISTERED TABLE:**

```
    (  0.000  100000.000000)
    ( 59.999  100000.000000)
    ( 60.000   25000.000000)
    (900.000   25000.000000)
```

`Function1 table` defaults `interpolationScheme` to `linear`, so the two
breakpoints at the edge are the ends of a **1 ms ramp**, not a step. The ramp
**ends at 60.000**, so `t = 60` samples the **cruise** endpoint exactly, which is
where the directive pins it. **Registered condition, checked by the comparator on
every arm: no step time on that arm's `deltaT` falls strictly inside
`(59.999, 60.000)`.** Step times are integer multiples of 0.25 s; the nearest are
59.75 and 60.00, both outside. **A `deltaT` finer than 1 ms would sample the
ramp, and that is the condition under which this placement must be revisited.**
The comparator **refuses** a `deltaT` that violates it, **and refuses T25R's own
70000 / 2800 table** — a case still carrying the construction Sanaa rejected is
not this rung's case, and `--selftest` drives that refusal.

---

## 5. THE ACCEPTANCE CRITERION SANAA NAMED — T25R §5, unchanged

### 5.1 Her words

> *"Downstream cells must be able to run hotter than upstream ones."* — `6ad8f5b7`

### 5.2 ⚠ THE GEOMETRY DISCLOSURE, CARRIED FORWARD UNCHANGED

**In the registered geometry there is no cell-to-cell streamwise ordering.** The
8 cells are stacked in the **thickness** direction `y` and separated by **7
parallel channels**; every cell spans the same streamwise extent. **No cell is
downstream of another.** The **mechanism** she named — coolant heating along the
channel, making the solid hotter where the coolant is hotter — is real, is
resolvable, and is exactly what resolving the channel buys; in this geometry it
appears as a **within-cell streamwise gradient** and as an **outlet above
inlet**. **This is disclosed, not substituted. Flagged for her ruling; it does
not block launch.**

### 5.3 The registered criterion — **D1, D2, D3**, thresholds unchanged

`T_up(i)` = volume-average solid `T` of cell *i* over `x ∈ [0.000, 0.010]`;
`T_dn(i)` = the same over `x ∈ [0.090, 0.100]`; both at **`t = 60 s`** and both
on the **primary run `T25R2_L2`**.

| id | criterion | threshold | verdict on failure |
|---|---|---|---|
| **D1** | `T_dn(i) > T_up(i)` for **every** cell `i = 1..8` | strict, all 8 | **GATE FAIL** |
| **D2** | coolant area-weighted mean `T` at `outlet` > at `inlet`, at every written `t > 0` | strict, all 180 | **GATE FAIL** |
| **D3** | `min_i [ T_dn(i) − T_up(i) ] > 10 × PLANT` = **1.234e-02 K** | the signal must exceed ten times the registered reader-control perturbation, so it is not write-precision noise | **GATE FAIL** |

`PLANT = 1.234e-03 K`, **imported** from `scripts/roache_triple.py` and never
redefined (§7.1 clause 6).

**D1/D2/D3 are PASS-or-GATE-FAIL, not `NOT A RESULT`**: they ask a physical
question with a pre-registered threshold, and a `no` is an answer. **Only §6.4
completion, §2.4 mesh quality, §3.4's `numerics_check` refusal, §3.5's
outer-loop gate and §7.1 instrument admission can make a row `NOT A RESULT`.**

---

## 6. THE CHECK SET — each registered in advance

### 6.1 ⚠ THE T20 EXACT GATE — CITED HONESTLY, AND IT HAS **NOT** DISCHARGED

Unchanged from T25R §6.1. `T20_PREREGISTRATION.md:21` registers T20 as the **V
exact tier of Sanaa's CASE 4**, and it is the right machinery proof for this
rung. **IT HAS NOT PASSED.**
`verification/runs/T-family/T20_runs/T20_P10_CONDITION_iii_MEASUREMENT.md:9`
states verbatim: *"**T20 remains `NOT A RESULT` on its own registered terms**"*,
with condition (iii) PASSED and condition (c)/(ii) FAILED by measurement, under
the `DEAD_LEVER_AUDIT.md` §26.6 deadlock referred at
`docs/campaigns/T-family/T20_P10_REFERRAL_26_6_DEADLOCK.md`. **`T20_LC_P10` has
not run; zero core-minutes of solver compute.**

**REGISTERED CONSEQUENCE:** the T20 citation is a **POINTER**, not a discharged
proof; **T25R2 INHERITS NO `PASS` FROM T20**; the comparator prints this on its
own face on **every** invocation; and this does **not** block T25R2, whose §6.2
energy gate is an independent, self-contained check on the transient machinery
and is reported as **the** machinery evidence this rung actually carries.

### 6.2 Cumulative energy conservation over 900 s — **GATE**

```
E_gen  =  ΔE_solid  +  ΔE_fluid  +  ∫₀⁹⁰⁰ ṁ·c_p·(T_out − T_in) dt   +  R
```

- **`E_gen = 648,000 J`** (§4.3 row 6), computed from the **registered** `q'''(t)`
  and the volume **OpenFOAM itself measures and prints**
  (`cellSetOption.C:166-168`) — never a hand-typed volume.
- `ΔE_solid`, `ΔE_fluid` from the written fields at `t = 900`.
- The convected term is accumulated from `surfaceFieldValue` `weightedSum` of
  `phi·T` on `inlet` and `outlet`, written **every time step**. `phi` is the mass
  flux and is **negative on an inflow face**, so the two rows **add**.

**THRESHOLD, FROZEN: `|R| / E_gen ≤ 2.0 %`.** Outside ⇒ **`GATE FAIL`**, with
`R`, `E_gen` and all four terms printed.

**PLANTED CONTROL ON THE BALANCE INSTRUMENT.** The comparator re-computes
`E_gen` with the takeoff level scaled by **+10 %** and asserts the residual moves
by `0.10 × 1.0e5 × 60 × 0.024` = **14,400 J ± 1e-6 J** (T25R's was 10,080 J at
its lower load). **An instrument that does not move when the source moves is
refused (exit 2), not reported.** `--selftest` drives the ledger **both ways** —
a balanced forge PASSES at `|R|/E_gen` 5.1e-11 and a convected term 10 % wrong
FAILS at 8.68 % — because *a gate only ever shown failing has not been shown to
be a gate*.

### 6.3 Step-sensitivity and mesh-sensitivity panels — **REPORT, NOT GATE**

- **Step pair**: `T25R2_L2` (`dt` 0.5) vs `T25R2_L2_DT025` (`dt` 0.25), same mesh.
- **Mesh pair**: `T25R2_L1` vs `T25R2_L2`, same `dt`.
- **`T25R2_L1_OC20` ENTERS NEITHER PANEL.** It is a sweep-count arm, not a level.

Reported on each: signed and percentage difference in peak cell temperature, end
temperature, module spread, coolant outlet temperature and the minimum
within-cell streamwise difference. **NO observed order. NO GCI. NO Roache
classification.** The comparator prints, verbatim, on both panels: *"TWO POINTS.
NO LADDER IS REGISTERED. No observed order, no GCI and no Roache classification
is computed, quoted or quotable from this artifact."*

**Registered interpretive limit:** a small difference between two points is
**consistent with** convergence and is **not evidence of** it. The report says
so, in those words.

### 6.4 STRICT COMPLETION — `CLAUDE.md` rule 4, delegated and never reimplemented

Completion is decided by
**`verification/runs/T-family/T25R2_MODULE_runs/mark_done_t25R2.py`**, which is
**called** by the comparator and **never reimplemented inside it**. A run without
a `DONE.<case>` marker from that instrument is `NOT A RESULT` and its numbers are
not printed as results.

| conjunct | T25R2's registered form |
|---|---|
| 1. `rc = 0` | **DERIVED FROM `log.solve`** — exactly one `End`, zero `FOAM FATAL`, last time == `endTime`. `launcher_rc` is **NEVER** accepted as `rc`, **even at 0**: `setsid timeout cmd` exits 0 for every outcome, and the queue runner is measured to clobber `STATUS` |
| 2. `End` line | exactly one |
| 3. last time == `endTime` | `900` exactly, to 1e-9 |
| 4. fields present, **PER REGION** | `<endTime>/module/` : **`T`, `p`**.<br>`<endTime>/coolant/` : **`T`, `U`, `p`, `p_rgh`, `alphat`, `nut`, `k`, `omega`** |
| 5. `ExecutionTime` count | **1800 / 1800 / 1800 / 3600.** Rule 4's *"count == `endTime`"* is a **SHORTHAND literally true only at `deltaT = 1`**; the operative test is **count == REGISTERED STEP COUNT**, a **step-count identity**. Precedent inside this family: `T20_LC_c`, `endTime` 4500 at `deltaT` 6, 750 steps, 750 `ExecutionTime` lines. `adjustTimeStep` is **checked, not assumed**, because on an adaptive step the identity would not hold |
| 6. **the age guard** | **`0/module/T`**, not `0/T` — a multi-region case has no `0/T`. `run_one_t25R2.sh` `touch`es it **LAST**, immediately before the start block. **Every** field in conjunct 4, in **both** regions, must be **strictly newer** |
| 0. guard | the launcher and the stager **both refuse** a case where `0` or a time directory already exists |

**⚠ `T25R2_L1_OC20` IS NOT EXEMPT.** It carries the identical completion rule and
the identical 1800-step count — **sweeps are inside a step, not steps**. A gate
whose reference arm is allowed to be incomplete is not a gate, and
`--selftest` drives a truncated OC20 tail to `NOT DONE`.

`STATUS.<case>` lives **inside** the case directory. An **absent** `STATUS` is a
**REFUSAL (exit 2)**, never inferred from an `End` line (K0d L1).
**L-342 field classes:** PHYSICS-CRITICAL = the six conjuncts. INFRASTRUCTURE =
`wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`, `capped`, `solver` —
absent ⇒ **NOT MEASURED** and **reported**; it never voids a run (Sanaa's
universal rule 2026-08-26: **bookkeeping never voids physics**).

**THE STALE-MARKER RE-CHECK.** A `DONE.<case>` marker is **not** accepted on
sight: every conjunct is re-run and a marker whose case no longer satisfies them
is **removed**. A marker is a cache, never evidence.

**THE CAP IS A NAMED OUTCOME.** `capped=yes` or `rc=124` ⇒ that row is
`NOT A RESULT`, named as a **cap stop** under rule 12; it **does not get a new
budget**, the other rows are untouched, and the stop is its own finding, never
folded into the cost ratio.

---

## 7. INSTRUMENT ADMISSION — THE PLANTED-PERTURBATION CONTROLS

### 7.1 Every reader, no exceptions — the nine clauses, T25R §7.1 verbatim

1. **COPY FIRST** into `tempfile.mkdtemp()`, with a **REFUSAL** if the scratch
   path resolves **inside** the case. The case is **never written to**.
2. **NEGATIVE ARM at bitwise `0.0`, with NO tolerance.** A noisy reader is
   **refused**.
3. **POSITIVE ARM: a MEASURED magnitude ladder**, epsilon-free.
   `LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)`.
4. **REFUSE IF BLIND.**
5. **THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE:** `got >= PLANT*(1 − 1e-9)`.
   `analyse_t3.py:327`'s absolute form is **expressly not adopted**.
6. **`PLANT` IS IMPORTED, NEVER REDEFINED**, from `scripts/roache_triple.py`.
7. **Plants are written BY LINE INDEX**, inside a window taken from the field's
   **own header**. Nothing is located by value. A patch plant writes **every**
   face so the shift is **exactly** `mag`, never `mag/N`.
8. **The case bytes are compared before and after**; scratch is removed in a
   `finally`.
9. **`__pycache__` is cleared** before the control runs.

**A REFUSAL ON ANY READER MAKES THE WHOLE RUNG `NOT A RESULT`.**

### 7.2 The registered readers — every one carries a control

`read_cell_T`, `read_spread`, `read_updown`, `read_outlet_T`, `read_inlet_T`,
`read_energy`, planted exactly as T25R §7.2 registers them, including the
whole-module-cell plant that makes the volume-average shift **exactly `mag`**
rather than `mag/N`, and the **live negative arm** in which a single-cell plant
under a volume-average reader must **REFUSE**.

### 7.3 ⚠ NEW IN T25R2 — **THE OUTER-LOOP GATE CARRIES ITS OWN PLANTED CONTROL**

**Two identical arms would give three zeros, and a zero from a comparator not
shown able to see a non-zero is not evidence** (rule 3). §3.5's gate is therefore
driven in `--selftest` on forged arms carrying a **known** disagreement, and the
gate must report **exactly that number**: a planted 1.000000e-04 K shift is read
back as `O1 = 1.000000e-04 K` and `O3 = 1.000000e-04 K`, to 1e-12. The gate is
then driven to failure on O1 (a 5e-2 K shift), and driven to failure on **O2
alone** with O1 and O3 still passing — proving that **all three deltas are
required**, not any one of them.

### 7.4 ⚠ NEW IN T25R2 — **THE TRACEBACK TRAP IS CLOSED, AND THE CLOSURE IS DRIVEN**

**A comparator with zero `except` clauses lets an uncaught traceback leave the
interpreter with exit status 1 — which in this family's exit vocabulary is *"a
gate failed or a row is `NOT A RESULT`"*, i.e. a GRADED outcome. A crash would
then be indistinguishable from a measurement.** Both `analyse_t25R2.py` and
`mark_done_t25R2.py` wrap their entry point in a guard that re-raises
`SystemExit` untouched and converts **every** other uncaught exception into a
**REFUSAL (exit 2)**, printing the traceback. `--selftest` drives that path with
a **planted crash** rather than trusting a reading of it.

### 7.5 EVERY GUARD IS DRIVEN TO ITS REFUSAL BY MUTATION

`VERIFICATION_CHARTER.md` §2n.18: a supervisor's read of a control is **necessary
and not sufficient**; **a control not proved to fire is ceremony.**
`analyse_t25R2.py --selftest` runs **84 checks** and passes under both `python3`
and `python3 -O` (L-332); `mark_done_t25R2.py --selftest` and
`stage_t25R2.py --selftest` likewise. Among the negative arms driven by mutation:
a blind reader, a noisy reader, a single-cell plant under a volume-average
reader, a flat solid, a sub-threshold signal, an isothermal coolant, a ramp
straddling a step time, **the feasibility rung's 5000 W/m³ table**, **T25R's own
70000/2800 table**, **the T25R relaxation configuration itself**, each of the
five missing `Final` keys, a quoted-regex key, a wrong relaxation value, the
unreachable 1e-9 `p_rgh` tolerance, a missing top-level `PIMPLE`, a swapped
`nOuterCorrectors`, a log with no `Initial residual` lines, a census field absent
from the log, two `postProcessing` start-time directories, a mesh above each
quality threshold, a `checkMesh` log stating neither maximum, an uncommitted
pre-registration, an **edited** pre-registration, a truncated `ExecutionTime`
tail on the OC20 arm, and a planted interpreter crash.

---

## 8. COST — `CLAUDE.md` RULE 12

### 8.1 The basis is **MEASURED**, and its four caveats are carried, not buried

**MEASURED ANCHOR: T25RF arm A2T** — `T25RF_runs/A2T/STATUS.A2T`, `rc=0`,
`wall_s=31`, `ranks=1`, **`core_min=0.517`**, 60 steps at `nOuterCorrectors 10`
on the **L1 mesh (16,608 cells)**, at **Sanaa's loads**, with **exactly the
numerics §3.4 registers**. Split rates (T25RF addendum A2 §4, §6): **1.04
core-s/step developing (steps 1–20)** and **0.268 core-s/step settled
(steps 21–60)**.

> **Cell-sweep rate, derived: `31.02 / (60 × 10 × 16,608)` = 3.1130e-06 core-s
> per cell per outer sweep** — 0.549× T24's steady-SIMPLE 5.674e-06. Quoted for
> comparison only; the caps below are built on the split step rates.

**⚠ THE PROBE'S OWN FOUR CAVEATS, CARRIED INTO THIS TABLE VERBATIM:**

1. **It covers 30 s of a 900 s case — 3.3 % of the duration.**
2. **It stays entirely inside the takeoff branch**, so it **never prices the 60 s
   load step-down** or the 840 s cruise branch.
3. **Its settled rate is measured over 40 steps** at constant load.
4. **Wall-derived core-minutes were taken on a shared box** with other solvers
   running. (The GAMG iteration counts are free of that; the minutes are not.)

**THE PROBE'S EXTRAPOLATION IS ~8.3 core-min FOR 1800 STEPS AT L1, AND THIS
DOCUMENT DOES NOT PRICE AT 8.3.** The extrapolation is the **POINT**, and every
run carries an explicit margin and a **hard per-run cap** below.

### 8.2 The registered cost table — **POINT, MARGIN, HARD CAP, all shown**

**POINT arithmetic, shown because a cost nobody can check is not a cost:**

- `T25R2_L1` = `20 × 1.04 + 1780 × 0.268` = `20.8 + 477.04` = **497.84 core-s =
  8.30 core-min**.
- `T25R2_L1_OC20` = L1 × **2.18**, the **measured** sweep-doubling factor
  (T25RF A1 3.650 → A2 7.967 at 5 → 10 sweeps). This is **deliberately
  conservative**: 2.18 includes the `p_rgh` stall that A2T removes, and the clean
  model is ×2.00 = 16.60. **18.09 core-min.**
- `T25R2_L2` = L1 × **2.2500**, the exact cell-count ratio. **18.68 core-min.**
- `T25R2_L2_DT025` = L2 × **2**, twice the steps at the same per-step cost.
  **37.35 core-min.**

**MARGIN, COMPOSED AND NAMED — `×4` on the L1 arms, `×5` on the L2 arms:**

| term | factor | why |
|---|---|---|
| regime / new-stall risk over 870 s never probed | ×2.0 | GAMG stalled at 1e-9 as the field settled; 1e-8 has 4.4× margin on the measured floor, but the cruise branch is unpriced |
| settled rate measured over only 40 steps | ×1.5 | sample risk, caveat 3 |
| the probe priced 3.3 % of the duration | ×1.33 | caveat 1 |
| **L1 arms** | **×4** | 2.0 × 1.5 × 1.33 = 3.99 |
| **mesh-jump miss, MEASURED in this family at 31.4 %**, plus L2's higher `Co` | ×1.25 further | T25R §8.1 records the 31.4 % miss; the cell-count scaling does not capture `Co` 1600 → 2400 |
| **L2 arms** | **×5** | 4 × 1.25 |

| run | cells | steps | sweeps | **POINT (core-min)** | ×  | **HARD CAP** | `timeout_s` |
|---|---|---|---|---|---|---|---|
| `T25R2_L1` | 16,608 | 1,800 | 10 | **8.30** | 4 | **34** | **2040** |
| `T25R2_L1_OC20` | 16,608 | 1,800 | 20 | **18.09** | 4 | **73** | **4380** |
| `T25R2_L2` | 37,368 | 1,800 | 10 | **18.68** | 5 | **94** | **5640** |
| `T25R2_L2_DT025` | 37,368 | 3,600 | 10 | **37.35** | 5 | **187** | **11220** |
| **staging + a confirmatory `checkMesh`** (§2.5) | — | — | — | **0.50** | — | **2** | 600 |
| **TOTAL** | | | | **82.92** | | **390** | |

**AGAINST SANAA'S 600 core-min CAP: headroom 210 core-min at HARD CAP = 35.0 %.**

**Dollars, DERIVED and NOT MEASURED.** At **$0.0513/core-h**, c7a.4xlarge,
**owner-stated 2026-08-21/22** and corroborated at
`Xiao2016_EnKF/PREREGISTRATION.md:197`. The box **cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5), so **`cost_basis = REPORTED-BY-OWNER, NOT
MEASURED`**: POINT `82.92/60 × $0.0513` = **$0.0709**; HARD CAP
`390/60 × $0.0513` = **$0.3335**. Both under $25 and inside the 2026-08-21
blanket — **and still costed here, because a blanket is not a per-item read**
(rule 9).

**RULE 12 IS NOT DECORATION: AN OVERRUN STOPS THE RUN.** `timeout_s` is the hard
cap in wall-seconds at `ranks = 1`. A `timeout` kill leaves no `End` line and a
last time below `endTime`, so §6.4 conjuncts 1, 2 and 3 all fail and the row is
`NOT A RESULT` **by construction**. **It does not get a new budget** and it is
reported as a **cap stop**, never absorbed.

### 8.3 Wall-clock, and the registered launch order

| | sequential | 4 concurrent, `ranks = 1` each |
|---|---|---|
| **POINT** | 82.92 min = **1.38 h** | max = 37.35 min = **0.62 h** |
| **HARD CAP** | 390 min = **6.50 h** | max = 187 min = **3.12 h** |

Sanaa's *"let it run till it converges… I don't have a HARRRD deadline"*
(`7b9ae703`) is satisfied in every branch.

**REGISTERED LAUNCH ORDER: `T25R2_L1` first, then `T25R2_L1_OC20`.** L1 is the
cheapest arm and gives a **measured, same-solver, same-physics, same-numerics**
rate for the §8.7 calibration row; and **§3.5's gate cannot be evaluated until
both L1 arms are complete**, so nothing is gained by starting L2 before them.
**The registered caps do NOT move on that measurement** — gates close at first
compute.

### 8.4 Build compute is costed so it cannot be taken as a free action

`stage_t25R2.py` copies files and writes four dictionaries; it starts no
process (§2.5). A confirmatory `checkMesh` at step 3 is the only compute in that
step, and at 37,368 cells it is a fraction of a wall-second (the feasibility rung
measured `blockMesh` + `checkMesh` at **0.04 wall s** on 960 cells,
`T25_MESH_FACTS.json`). **POINT 0.50, HARD CAP 2.00 core-min** is generous by
orders of magnitude and is registered rather than treated as costless: **build
compute is compute**, and `VERIFICATION_CHARTER.md` §2d.2 closes gates at first
compute, **staging included**. That is why §10 puts the diff read first.

### 8.5 **AN L2 OUTER-LOOP ARM — PRICED, AND REFUSED**

The honest question §3.5.5 raises is whether the sweep-count gate should also run
at L2, where `Co ≈ 2400`. **It is priced here and it does not fit.**

| | `T25R2_L2_OC20` |
|---|---|
| POINT | 18.68 × 2.18 = **40.72 core-min** |
| HARD CAP at ×5 | **204 core-min** |
| **five-run total at HARD CAP** | **594 core-min** |
| **headroom against 600** | **6 core-min = 1.0 %** |

**REFUSED.** A 1 % headroom converts one misprediction into a stopped campaign,
and a cap stop on the *gate arm* would void the whole rung rather than one row.
**The consequence is disclosed instead of bought**: §3.5.5 registers that the
gate certifies L1 only, the comparator prints that scope beside every L2 number,
and the failure direction — which is the one that matters for safety — does
transfer.

### 8.6 **A THIRD MESH LEVEL — PRICED, MATERIALLY CHEAPER THAN AT 04:05Z, AND STILL NOT REGISTERED**

| | L3 |
|---|---|
| cells | 84,078 (exactly 2.25 × L2, 5.0625 × L1) |
| POINT, off T25R2's **measured** basis | **42.02 core-min** |
| HARD CAP at ×5 | **210 core-min** |
| **five-run total at HARD CAP** | **600 core-min** |
| **headroom against 600** | **0 core-min = 0.0 %** |

**RULED: L3 STAYS REFUSED, and the reasoning is the 04:05Z one, unchanged — the
extrapolation is from a 30 s probe on one branch, and a cap with no headroom
converts one misprediction into a stopped campaign.** A five-run set lands on
**exactly** the cap with **zero** headroom. **Two further independent reasons:**
the L3 mesh **does not exist**, and building it would require `build_t25R.py`,
which is under a **live rule-6 referral** (§12.2); and a third level added after
first compute cannot be retro-fitted to manufacture an order.

**⚠ BUT L3 IS NOW MATERIALLY MORE AFFORDABLE THAN WHEN IT WAS FIRST REFUSED, AND
IT IS THE STRONGEST CANDIDATE FOR THE SUCCESSOR RUNG.** T25R §8.5 priced it at
POINT **71.56** / HARD CAP **214.68** core-min off a **borrowed** T24 rate.
T25R2 prices it at POINT **42.02** — **41.3 % cheaper** — off a **measured**
rate on the same solver, same physics and same numerics. **The right route to a
genuine Roache triple is a separate later rung priced off T25R2's OWN measured
1800-step rate**, where a ×1.5 contingency is defensible and the whole triple
fits comfortably. **It is not registered here and no output of this rung may be
read as a step toward one.**

### 8.7 Estimate-versus-actual calibration — rule 12, mandatory

At **every process completion** — each run graded, and the rung closed — the
pre-registered estimate is compared with the actual. Actuals in **core-minutes
from `log.solve` `ExecutionTime` × ranks ÷ 60**; dollars **derived at
$0.0513/core-h and labelled derived-not-measured**. Each row states the **ratio
actual/predicted** and **attributes the gap** — contention, waste or
misprediction — with **waste named separately and never absorbed into the
ratio**. Rows land in **`docs/COST_CALIBRATION.md`** under that file's append
rules and the rule-10 private-index protocol. **A completion report without this
comparison is incomplete.**

**Registered in advance, so the calibration has something to test:** the T25RF
probe's own calibration measured the T25R cost model wrong by **7.3×–8.9×** on
arms A1/A2, **entirely attributable to the `p_rgh` stall** and not to contention;
with the stall removed, A2T came in at **0.86× the same model's prediction**.
**T25R2's POINT estimates are built on the post-stall rate, so a ratio far from
1.0 is itself the finding**, and it will be attributed rather than absorbed.

---

## 9. OUTPUTS — exactly what Sanaa ordered

**Fields** written at `t = 0, 30, 60, 120, 300, 900 s` (all multiples of the 5 s
write interval).

| # | output | gradeable? |
|---|---|---|
| 1 | solid `T` fields at the six times | `FEASIBILITY` (illustrative) |
| 2 | **all-8-cell** temperature histories, **pulse shaded** 0–60 s | `FEASIBILITY` |
| 3 | module spread `T_max − T_min` vs time | `FEASIBILITY` |
| 4 | **coolant outlet temperature vs time** | **GRADED** by D2 (§5.3) |
| 5 | per-cell table: peak `T`, time of peak, `T` at end of pulse, time to settle (`dT/dt < 0.01 K/s`) | `FEASIBILITY` for the values; the **within-cell streamwise** column is **GRADED** by D1/D3 |
| 6 | energy-conservation ledger, four terms + residual | **GRADED** by §6.2 |
| 7 | step-sensitivity panel | **REPORT ONLY**, no order, no GCI |
| 8 | mesh-sensitivity panel | **REPORT ONLY**, no order, no GCI |
| 9 | **outer-loop sweep-count independence, O1/O2/O3 in kelvin** | **GATE** by §3.5 |
| 10 | last-sweep residual census | **REPORT ONLY. NO THRESHOLD.** (§3.5.2) |

**PER-OUTPUT LABELLING IS MANDATORY.** Every number this rung emits carries
either a **GRADED** verdict from the fixed vocabulary or the tag
**`FEASIBILITY`** meaning *not gradeable, no gate exists for it, and none may be
invented after the fact*. **A number with neither label is a defect in the
report.**

**DEFERRED, and named so no reader assumes them:** anisotropic solid
conductivity; the laminar-vs-SST model-form band; the SOC-dependent source; 3-D;
the liquid cold plate; cell-to-cell conduction paths; a serial-channel geometry
(§5.2); a third mesh level (§8.6); an L2 outer-loop arm (§8.5).

---

## 10. THE ORDER OF OPERATIONS — REGISTERED, AND NOT NEGOTIABLE

`SUPERVISION_CHARTER.md` §3 reserves to the supervisor **personally**: the
confirmation that the pre-registration is **committed** before compute, and the
**diff read** of the measurement script. **Neither may be delegated, and a
relayed check is a summary, not a check.**

```
  1. COMMIT this document, the comparator, the completion
     instrument, the stager and the launcher.            <-- this lane, at §11
  2. THE SUPERVISOR'S PERSONAL DIFF READ AND
     PRE-REGISTRATION CHECK.                             <-- STOP. Not this lane.
  3. stage  (stage_t25R2.py; optional confirmatory checkMesh)  <-- only after 2
  4. launch (run_one_t25R2.sh, T25R2_L1 then T25R2_L1_OC20)    <-- only after 3
```

**NOTHING HAS BEEN STAGED AND NOTHING HAS BEEN LAUNCHED.**
`VERIFICATION_CHARTER.md` §2d.2 closes gates at **first compute — feasibility and
build compute included** — so **staging before the diff read would close the
gates of a comparator the supervisor has not yet accepted.** `stage_t25R2.py`
and `run_one_t25R2.sh` have **never been executed**, and the stager is
structurally incapable of starting a solver or a mesher (§2.5).

**Before first compute, amendments are legal** and **must state the condition and
how it was checked**. Three are open and all three must be decided at step 2:

- **§3.5 — the outer-loop gate's thresholds and its propagation rule.** Condition,
  checked: **no T25R2 case directory exists** under
  `verification/runs/T-family/T25R2_MODULE_runs/`, verified by this lane at write
  (the directory holds four files and no directory).
- **§8.5 — an L2 outer-loop arm.** Priced at 204 core-min hard cap, leaving 1.0 %
  headroom; **lab recommends no**, and the scope limit is disclosed instead.
- **§8.6 — L3.** Priced at 210 core-min hard cap, leaving 0.0 % headroom;
  **refused**, and named as the strongest candidate for the successor rung.

---

## 11. FREEZE

| artifact | path |
|---|---|
| this pre-registration | `docs/campaigns/T-family/T25R2_PREREGISTRATION.md` |
| comparator | `verification/runs/T-family/T25R2_MODULE_runs/analyse_t25R2.py` |
| completion instrument | `verification/runs/T-family/T25R2_MODULE_runs/mark_done_t25R2.py` |
| case stager (**never executed**) | `verification/runs/T-family/T25R2_MODULE_runs/stage_t25R2.py` |
| launcher (**never executed**) | `verification/runs/T-family/T25R2_MODULE_runs/run_one_t25R2.sh` |

**The grading path is fixed at this commit.** Before grading, the comparator
hashes this document against the committed blob and **refuses** if they differ —
verifying that *the frozen file is the file that ran* (`CLAUDE.md` rule 2;
`scripts/check_comparator_freeze.py`). `--selftest` drives both refusals: an
**uncommitted** document and an **edited** one.

**Frozen files are never edited.** Any departure lands as a **dated amendment
appended at the foot**, with a version bump and the assertion `lines whose number
changed above this section: 0`.

**`build_t25R.py` IS NOT IN THIS FREEZE TABLE AND IS NOT COMMITTED BY THIS
RUNG.** It belongs to T25R's freeze table, it is under a live rule-6 referral
(§12.2), and this lane does not touch it, run it, commit it or revert it.

**SUBMISSIONS PARKED** (rule 7). **Permanently private** (rule 8). Nothing here
is sent, filed, uploaded, registered, posted or commented anywhere outside this
box.

---

## 12. WHAT THIS LANE COULD NOT VERIFY

Stated plainly, because an honest gap is worth more than a confident guess.

### 12.1 The T25R verdict, and the two clauses it fired on

**`T25R_L1` is `NOT A RESULT`**, on two independent clauses of its own §6.4:
`STATUS.T25R_L1` carries **`rc=134`**, and `log.solve` carries **one
`FOAM FATAL`** — *"Negative initial temperature T0: -14.4619608928"* — with the
**last written time 1.5 against `endTime` 900**. Its own §3.5 gate failed **2 of
the 2 steps it reached**. This lane read both artifacts; it did not re-run the
T25R comparator against them, because the completion clauses are decisive on
their face and the case is closed.

### 12.2 ⚠ THE RULE-6 BREACH ON `build_t25R.py` — REFERRED, NOT REPAIRED

`build_t25R.py` is in **T25R §11's freeze table**. Measured by this lane:

- committed blob at HEAD: **`9683bced714b4b8f37b0c550e3bb8894fdd5e2b6`**
- working-tree blob: **`06a185d509be2f8ee12e5fc997d065cacab6f9e1`**
- **the two differ by 53 lines**, and the file's own comment cites
  **"prereg Amendment A1", WHICH DOES NOT EXIST** — T25R carries no amendment A1.

**The change itself was necessary and correct**: `splitMeshRegions -cellZones`
produced **15 disconnected domains and no `coolant` region** (the abandoned
`log.splitMeshRegions.CELLZONES_FAILED_15_DOMAINS` and
`log.checkMesh.coolant.CELLZONES_FAILED` are still on disk in `T25R_L1`), and
`-cellZonesOnly` is the right utility. **The builder grades nothing.** But **the
rule-6 disclosure was never written**, and a frozen file was edited in place with
a citation to a document that does not exist.

**REFERRED TO THE CHIEF AND TO VERIFICATION. This lane does not repair it, does
not write a retroactive amendment, does not commit it and does not revert it.**
T25R2 is structured so that the referral is **not on its critical path**: the
mesh is reused rather than rebuilt (§2.5), and the builder is not in T25R2's
freeze table (§11).

### 12.3 ⚠ TWO REAL DEFECTS FOUND IN THE FROZEN `analyse_t25R.py`, REPORTED AND NOT REPAIRED

Found by driving `grade()` end to end in T25R2's `--selftest`, which T25R's
selftest never did. Both are in `analyse_t25R.py:795-800`'s `mesh_quality`, and
**both fail on the REAL v2606 output** this lane read from
`T25R_MODULE_runs/T25R_L1/log.checkMesh.coolant`:

```
    Mesh non-orthogonality Max: 0 average: 0
    Max skewness = 1.66534018381e-13 OK.
```

1. **The non-orthogonality pattern requires `"Max non-orthogonality"`; v2606
   writes `"Mesh non-orthogonality Max:"`.** It matches **nothing**, falls back
   to `-1.0`, and the T25R comparator **REFUSES a perfectly good mesh**.
2. **The skewness character class `[\d.eE+]` EXCLUDES the minus sign**, so on a
   **negative exponent** it captures `"1.66534018381e"` and `float()` raises an
   **uncaught `ValueError`** — which in that file leaves **exit status 1**, i.e.
   a graded *"gate failed or NOT A RESULT"*. **That is the traceback trap exactly:
   a crash wearing a verdict's clothes.**

**Root cause, and it is the transferable part: T25R's forged `checkMesh` log was
written to match its own regex rather than to resemble the solver, and its
`grade()` was never driven end to end.** T25R2's forge writes the **real v2606
wording verbatim**, its `grade()` **is** driven end to end, `_checkmesh_max()`
parses **both** wordings, and a log stating neither maximum **REFUSES** rather
than assume a number it never read. **`analyse_t25R.py` is FROZEN and is NOT
EDITED (rule 6); the defect is reported here, not repaired in place.**

### 12.4 The three things the T25RF probe left unresolved — all still open

1. **Why the `h` outer loop plateaus rather than converging.** Measured: the
   last-sweep initial residual on `h` went 1.31e-4 at 5 sweeps to **5.79e-5** at
   10 — a 2.26× reduction for a 2.18× cost, i.e. **linear and slow**. Whether
   that is a coupling limit, a relaxation-factor artefact or the physical
   stiffness of the conjugate interface **is not known**, and this rung does not
   determine it.
2. **Whether the sweep-count gap saturates.** It **had not** at t = 30 s. §3.5's
   gate measures the 10-vs-20 gap over the **full 900 s** on the registered
   quantities, which is a direct test of the consequence — but it does **not**
   answer whether the gap saturates, and nothing here should be read as claiming
   it does.
3. **The probe supplied no replacement measure for what T25R §3.5 used to do —
   its own §7 says so in terms. §3.5 of this document IS that replacement, and
   this is stated plainly so no reader thinks the measure was inherited.**
   §3.5's thresholds are a **judgement tied to the PLANT scale**, argued in
   §3.5.4; they are **not** a measurement, and the L1-only scope of §3.5.5 is a
   real limitation, not a formality.

### 12.5 The mesh gate is no longer blind

**Disclosed in full at §2.4.** The §2.4 thresholds are inherited from T25R's
genuinely blind 03:39Z freeze; **the measured values are already on disk and this
lane read them before writing this document.** The gate keeps its force and loses
its blindness, and this document does not claim the credit twice.

### 12.6 The margin is a judgement, not a measurement

The **POINT** estimates of §8.2 rest on a **measured** rate (T25RF arm A2T, at
these exact numerics and these exact loads). **The ×4 and ×5 hard-cap factors are
a JUDGEMENT**, composed and named in §8.2 but not measured. The largest unpriced
risk is named there: **the probe never left the takeoff branch**, so the 60 s
step-down and the 840 s cruise branch are covered by margin rather than by
measurement.

### 12.7 The parallel-channel question is still Sanaa's to rule

Unchanged from T25R §12.6. **Sanaa's "downstream cells hotter than upstream"
cannot be tested cell-to-cell in the registered geometry** (§5.2). D1/D2/D3 test
the **mechanism** she named; whether that is what she meant is hers to rule, and
a serial-channel arrangement is a **different geometry and a different rung**.

### 12.8 The T20 exact gate has not discharged

Read at source (§6.1), but the `DEAD_LEVER_AUDIT.md` §26.6 deadlock is a **live
referral in another team's territory** and this lane did not adjudicate it.

<!-- END OF T25R2 PRE-REGISTRATION v1.0 -->

---

## Amendment A1 — 2026-09-01T05:32Z, **BEFORE ANY T25R2 COMPUTE**

**Lines whose number changed above this section: 0.**

**This document is now version 1.1.** The version is bumped **here, inside the
amendment**, and **not** by editing line 3 — editing the header would change a
line number above this section and falsify the assertion this amendment is
required to make. The `<!-- END OF ... v1.0 -->` marker above closes the **v1.0
body**, which is unaltered; v1.1 is that body **plus** this amendment.

Ordered by `heat-transfer-supervisor` at his §10 step 2 diff read, after he
personally confirmed the commit (`bb6e5761`, five files, document blob
`853cdb42` identical on disk and at HEAD, **no case directory**) and personally
drove `--selftest` under `python3` and `python3 -O` with caches cleared.

### A1.1 THE CONDITION, AND HOW IT WAS CHECKED

`CLAUDE.md` rule 2 permits amendments **before first compute** and requires the
condition and the check to be stated — *"name the run directory that does not
exist"*.

**Condition: NO T25R2 COMPUTE HAS RUN AND NO T25R2 RUN DIRECTORY EXISTS.**
**Checked at write:** `verification/runs/T-family/T25R2_MODULE_runs/` holds
**exactly four files and no directory** — `analyse_t25R2.py`,
`mark_done_t25R2.py`, `stage_t25R2.py`, `run_one_t25R2.sh` (the interpreter's
`__pycache__` is removed before every check);
**`T25R2_L1`, `T25R2_L1_OC20`, `T25R2_L2` and `T25R2_L2_DT025` DO NOT EXIST**
(`ls -d .../T25R2_*` → *"No such file or directory"*). No solver, no
`blockMesh`, no `splitMeshRegions`, no `checkMesh` and no staging has run.

### A1.2 ⚠ WHAT THIS AMENDMENT DOES **NOT** DO

**It alters NO gate, NO threshold, NO cap and NO label.** §3.5's three gated
deltas O1/O2/O3 keep their thresholds (`10×PLANT`, `1×PLANT`, `10×PLANT`)
unchanged, the propagation rule of §3.5.4 is unchanged, §8's costs and caps are
unchanged, and no output changes its GRADED / `FEASIBILITY` label. It **adds one
REPORT**.

### A1.3 THE REPORT, AND WHY IT IS OWED

**Doubling the sweeps once and finding agreement is the standard test, but it is
a SINGLE POINT.** A `PASS` on §3.5 could mean the outer loop has converged, or
could mean 10 and 20 sweeps sit close **while both are wrong**. The registration
as frozen cannot tell those apart, and the probe's own measurement is the reason
to worry: the 5-vs-10 gap was **still growing** when the probe ended.

**The number that settles it is already measured, and it is genuinely
like-for-like.** T25RF addendum A2 §3, on the **same mesh (L1)**, the **same
loads**, the **same relaxation** and at the **same instant**:

| sweeps compared | t = 1 s | t = 10 s | **t = 30 s** |
|---|---|---|---|
| **5 vs 10** (MEASURED, T25RF) | 1.05e-3 K | 3.47e-3 K | **6.02e-3 K** |
| **10 vs 20** (this rung) | — | — | **REPORTED HERE** |

**REGISTERED: `O1_t30` — O1 restricted to `t = 30 s` — is computed and printed
beside the probe's MEASURED 6.02e-3 K.**

- **smaller than 6.02e-3 K** ⇒ the sequence **5 → 10 → 20 is visibly
  converging** at that instant and the `PASS` means what it claims;
- **larger than 6.02e-3 K** ⇒ a reader sees that **immediately, EVEN ON A
  `PASS`**.

### A1.4 ⚠ **NO THRESHOLD IS ATTACHED, AND NONE MAY BE INFERRED**

The supervisor declined to register a number he had not justified, and **none is
registered here.** `O1_t30` is a **REPORT**, exactly as the last-sweep residual
census is (§3.5.2). It takes **no part** in the outer-loop gate's verdict:
`oc_independence()`'s `ok` is assembled from `O1_ok`, `O2_ok` and `O3_ok` on one
line and from nothing else.

**PROVED BY MUTATION, not asserted.** `--selftest` drives the case this report
exists for: **a 9.0e-3 K sweep-count disagreement PASSES O1** — it is below
`10×PLANT = 1.234e-2 K` — **and is LARGER than the probe's 5-vs-10 gap.** The
gate prints `PASS` and the report prints *"the sequence is NOT visibly
converging at t=30 s"*, **in the same invocation.** A second arm plants
1.000000e-04 K and the report reads it back at exactly that value and flags it
as smaller. A third arm proves by fragment-assembled token search that **no
threshold-shaped name is bound** for the report anywhere in the file.

`t = 30 s` is a registered write time (§9), so this costs nothing and adds no
field.

### A1.5 THE ARTIFACTS THIS AMENDMENT CHANGES, NAMED FOR AUDIT

| artifact | before | after |
|---|---|---|
| `analyse_t25R2.py` | committed blob **`9d419a7ce57501ed535fdfa8706d517780cb2914`** at `bb6e5761` | the blob committed with this amendment |
| `mark_done_t25R2.py`, `stage_t25R2.py`, `run_one_t25R2.sh` | **unchanged** | **unchanged** |
| §1–§12 of this document | **unchanged** | **unchanged** |

`analyse_t25R2.py --selftest` now runs **88 checks** (84 before this amendment)
and passes under both `python3` and `python3 -O` with caches cleared;
`mark_done_t25R2.py` and `stage_t25R2.py` are untouched and still pass.

### A1.6 ⚠ THE FIRST DRAFT OF A1.4's OWN CHECK WAS WRONG, AND IT IS DISCLOSED

The structural check that proves no threshold is bound **failed on its first
run — because its own search literals were inside the file it was searching.**
It reported `O1_t30_ok` and `PROBE_5V10_AT_T30_TOL` as "present" when the only
occurrence of either was **the check's own string**. It is now assembled from
fragments so it cannot match itself.

**This is recorded because it is the same failure as §12.3's**: *a control
derived from the thing it controls is not a control.* It was caught by running
the check rather than by reading it, which is §7.5's whole point.

### A1.7 §10 IS UNCHANGED AND STILL BINDING

```
  1. COMMIT this amendment and the comparator.          <-- this lane
  2. THE SUPERVISOR'S PERSONAL DIFF READ.               <-- DISCHARGED, and it
                                                            stays discharged
  3. stage + verify the mesh                            <-- only after 2
  4. launch T25R2_L1 FIRST, then STOP and calibrate     <-- only after 3
```

**Caps are unchanged and hard: 390 core-min total against 600. An overrun STOPS
the run and does not get a new budget** (rule 12). L3 stays refused (§8.6); an
L2 outer-loop arm stays refused (§8.5).

<!-- END OF T25R2 PRE-REGISTRATION v1.1 -->

---

## Addendum B1 — 2026-09-01, **AFTER FIRST COMPUTE. DISCLOSURE ONLY.**

**Lines whose number changed above this section: 0.**

### B1.0 ⚠ THIS IS AN ADDENDUM, NOT AN AMENDMENT, AND THE DIFFERENCE IS THE POINT

**First compute for T25R2 has happened** — staging at 2026-09-01T05:36Z, then
`T25R2_L1`'s launch at **05:37:55Z**. **Rule 2's pre-compute limb is closed.**
Amendment A1 was legal precisely because no run directory existed; that window
is gone and does not reopen.

**Under rule 2, changes now land only as dated addenda that CANNOT alter a gate,
threshold, cap or label.** Everything below is **disclosure and measurement**.
It alters **no** gate, **no** threshold, **no** cap and **no** label: O1/O2/O3
keep `10×PLANT` / `1×PLANT` / `10×PLANT`, §3.5's propagation is unchanged, §8's
POINT and HARD CAP figures are unchanged, D1/D2/D3 and §6.2 are untouched, and
**no output changes its GRADED / `FEASIBILITY` label.** **§12 itself is not
edited**; this addendum points at it. **The document is version 1.2.**

### B1.1 `T25R2_L1` IS COMPLETE. **`mark_done_t25R2.py` SAYS DONE.**

`mark_done_t25R2.py` is the authority on rule 4 and is not reimplemented.
Its verdict: **DONE — all six conjuncts hold.** Corroboration, re-measured off
the raw artefacts by `report_completion_t25R2.py` (which **decides nothing**):

| conjunct | measured |
|---|---|
| 1. `rc = 0` | **recorded, not inferred**: `.rc.T25R2_L1` = `0`, captured **inside** the detached wrapper; `STATUS.T25R2_L1` `rc=0`. `launcher_rc` was never accepted as `rc` |
| 2. `End` | **exactly 1**; **0** `FOAM FATAL` |
| 3. last time | **900**, from 181 written time directories |
| 4. fields | `module` `T,p`; `coolant` `T,U,p,p_rgh,alphat,nut,k,omega` — **missing: NONE** |
| 5. `ExecutionTime` | **1800**, == the registered 1800. A **step-count identity**, not a time-value identity |
| 6. age guard | reference `0/module/T`; **1810 field files** checked across **all 181 written times and both regions**; **tightest margin +15.957 s** (at `t=5 coolant/nut`); fields older than the reference: **NONE** |

**NOTHING IS GRADED.** D1/D2/D3, §6.2 and §3.5 belong to `analyse_t25R2.py`, the
outer-loop gate has **not** been evaluated, and **no physics number from this run
is a result.**

### B1.2 COST CALIBRATION — rule 12. **THE PREDICTION HELD, AND THE REASON IS NAMED**

| | value |
|---|---|
| **actual, solver** | `ExecutionTime 428.87 s × 1 rank ÷ 60` = **7.148 core-min** |
| actual, wall | `429 s` = 7.150 core-min |
| launch overhead, **named separately** | **0.002 core-min** — `0` staged from `0.orig`, the age touch, the launcher's 5 s poll. **Not waste**, and not in the ratio |
| **pre-registered POINT** (§8.2) | **8.30 core-min** |
| **RATIO actual/predicted** | **0.861** |
| HARD CAP | **34** core-min — **21.0 % used, 26.85 unspent**; `capped=no`, `rc=0` |
| dollars | **$0.0061**, **DERIVED, NOT MEASURED**, at $0.0513/core-h, `cost_basis = REPORTED-BY-OWNER` |

**ATTRIBUTION — MISPREDICTION, IN THE CONSERVATIVE DIRECTION, AND THE CAUSE IS
MEASURED.** §8.2's POINT extended the probe's **takeoff-branch** settled rate of
**0.268 core-s/step** across all 1800 steps. The probe **never priced cruise**
(§8.1 caveat 2). Measured here, split at the `t = 60 s` load step-down:

| branch | steps | measured rate |
|---|---|---|
| takeoff | 1–120 | **0.3751 core-s/step** |
| **cruise** | **121–1800** | **0.2285 core-s/step** |

**The run spends 93.3 % of its steps in cruise, which is 14.7 % cheaper per step
than the takeoff settled rate the POINT assumed.** That, and not luck, is the
whole of the 0.861. **A favourable ratio with an unexplained cause is not a
calibration row.**

**⚠ THE PROBE REPRODUCED, AND THIS IS THE STRONGEST THING IN THE ROW.** Over the
**same first 60 steps** the probe covered, at the same numerics, same mesh and
same loads, on a different day and a shared box:

| | probe A2T | `T25R2_L1` | ratio |
|---|---|---|---|
| steps 1–60 | 31.02 core-s (0.5170/step) | **31.79 core-s (0.5298/step)** | **1.025** |
| settled 21–60 | 0.268 core-s/step | **0.2715 core-s/step** | **1.013** |

**WASTE: ZERO, AND THE §3.4 TOLERANCE CLAIM IS NOW CONFIRMED AT FULL DURATION.**
The probe could only test the `p_rgh` stall over 30 s. Measured over the whole
900 s: **36,000 `p_rgh` GAMG solves, 65,949 total iterations, mean 1.83, max
548, and ZERO terminating at `maxIter` 1000.** The probe's 10-sweep arm at the
unreachable `1e-9` had **608 of 1200** stalling. **The registered `1e-8`
eliminates the stall over the full run, not merely over the probe's window.**

**CONTENTION: BOUNDED, NOT MEASURED, AND NOT IN THE RATIO.** Load 2.22 on 16
cores at launch, with `T23G_F` and dafoam `D19O` arm O-P live
(`LAUNCH_CONTEXT.T25R2_L1.txt`). The ratio uses `ExecutionTime`, the solver's own
CPU accounting. The 1.025 probe reproduction **bounds** any contention effect on
the comparable segment at about 2.5 %; that is an upper bound, **not** a
measurement of contention, and it is not subtracted from anything.

### B1.3 ⚠ A THIRD DEFECT IN T25R's RETIRED §3.5 GATE — IT WAS NEVER EVALUABLE

Established at v2606 by reading `T25R2_L1/log.solve`: the log carries **zero**
`Solving for solid region` lines. Under `Solving energy coupled regions` both
regions' enthalpy is **assembled and solved together**, emitting **one**
`Solving for h` line per outer sweep.

**T25R's `RESID_GATE` registered `coolant h < 1e-6` AND `module h < 1e-8` as
separate thresholds. There is no separate solid `h` residual on this solver, so
its comparator would have taken the single COUPLED residual and applied the
SOLID threshold of 1e-8 to it.** That gate was **never separately evaluable**.

**§3.5 was retired here because relaxing the final sweep destroyed its
calibration. It turns out it was also measuring something it could not
distinguish — so the replacement was NECESSARY, not merely convenient.**
This addendum is the disclosure §12 owes for that, and it is the supervisor's
finding to record, not this lane's alone.

### B1.4 ⚠ A FOURTH: THE RETIRED THRESHOLD WOULD HAVE FAILED THIS HEALTHY RUN

The §3.5.2 census, **a REPORT with no threshold**, measured on `T25R2_L1`:

| field | worst last-sweep initial residual | at the final step |
|---|---|---|
| `p_rgh` | **1.0219e-01** | 1.0589e-08 |
| `Ux` | 1.5225e-02 | 3.8756e-11 |
| `Uy` | 2.8532e-02 | 1.5171e-09 |
| `h` | 5.0344e-04 | 7.2984e-07 |

**Against T25R's retired 1e-6 / 1e-8 thresholds this complete, `rc = 0`, fully
converged run would have been `NOT A RESULT` on a large fraction of its steps.**
With the final sweep **relaxed**, the last-sweep initial residual is large early
in a strong transient **by construction** — which is precisely why the threshold
lost its meaning. **The census is reported and gated on nothing. This is
measured evidence that the retirement was correct.**

### B1.5 ⚠ A DEFECT IN `analyse_t25R2.py`, DISCLOSED AND **DELIBERATELY NOT REPAIRED**

**Found by invoking the comparator on `T25R2_L1` after `T25R2_L1_OC20` was
STAGED but not yet LAUNCHED.** §3.5.4 registers that an OC arm which *has not
run* makes the gate **`PENDING`**. The code delivers that only when the arm's
**directory is absent**; once staged, `mark_done`'s correct K0d-L1 rule — *an
absent `STATUS` is a REFUSAL* — fires first and the comparator exits **2
(REFUSE)** instead of reporting `PENDING`.

**ROOT CAUSE, AND IT IS THE NIGHT'S RECURRING CLASS AGAIN:** `--selftest` forged
"has not run" as *"no directory"*, but the real post-§10-step-3 state is
*"directory staged, no `STATUS`"*. **The fixture did not resemble the situation.**
That is the same failure as §12.3's forged `checkMesh` log and A1.6's
self-matching token check — the fourth instance this lane has produced or found.

**IT IS NOT REPAIRED, AND THAT IS A RULING THIS LANE DOES NOT MAKE ALONE.**
`VERIFICATION_CHARTER.md` §2d.1 permits a post-compute change on the grading path
only if all four conditions hold; conditions (3) and (4) presuppose published
numbers, and **there are none — the comparator printed no physics on either
path.** More decisively:

- **the state is transient and self-clearing.** It exists only between staging
  and launching an OC arm. The registered launch order removes it permanently.
- **the failure direction is silence.** It REFUSES; it cannot print a number,
  and a repair could only ever withhold *more*, never publish more.
- **nothing in the registered campaign reaches it** except an out-of-sequence
  read, which is exactly what produced it.

**REFERRED to the supervisor and to verification. A frozen grading path is not
edited after first compute for a transient condition on this lane's own
authority.** The limitation is disclosed here so no future reader mistakes the
refusal for a broken instrument.

### B1.6 ⚠ A LABEL HAZARD IN THIS RUN'S OWN LOG, REGISTERED FOR EVERY LATER READER

**Every `Min/max T` line in `log.solve` is the COOLANT region** — ten per step,
each following `Solving for fluid region coolant`. The solid prints none
(B1.3). The tell is that its minimum sits at **292.985 K, BELOW the 293 K
initial**, which a heated solid cannot do.

**The module temperature is read from
`postProcessing/module/module_minmax/0/fieldMinMax.dat` and from the written
fields, and from nowhere else.** Both this lane and the supervisor initially
quoted the coolant maximum as a module temperature; the error was caught before
it reached any record, and it is registered here so it cannot be made a third
time.

**And the deeper rule, which is the part worth keeping:** a **maximum** is by
construction the **least-cooled point in the body**, so a maximum approaching the
adiabatic bound is *expected* and **measures nothing whatever about how much heat
left**. The fraction that left is **§6.2's ledger**, from a reader carrying its
planted +10 % control, after the gate, on a completed run. **Nothing before then
is entitled to an opinion about it.**

### B1.7 ARTIFACTS

Run outputs stay **out of git**, as `T25R_MODULE_runs`' are, and are named by
absolute path so nothing is invisible for being large:

- `/home/ubuntu/Certonomous/verification/runs/T-family/T25R2_MODULE_runs/T25R2_L1/log.solve` (26 MB)
- `.../T25R2_L1/STATUS.T25R2_L1`, `.../T25R2_L1/.rc.T25R2_L1`
- `.../T25R2_L1/COMPLETION.T25R2_L1.txt`
- `.../T25R2_L1/postProcessing/{module/module_minmax,coolant/*}`
- `.../LAUNCH_CONTEXT.T25R2_L1.txt`, `.../DONE.T25R2_L1`
- committed: `report_completion_t25R2.py` — **grades nothing, decides nothing,
  and is NOT in §11's freeze table.**

**§10 is unchanged. Caps are unchanged and hard. L3 stays refused (§8.6); an L2
outer-loop arm stays refused (§8.5).**

<!-- END OF T25R2 PRE-REGISTRATION v1.2 -->

---

## Addendum B2 — 2026-09-01, **AFTER FIRST COMPUTE. DISCLOSURE ONLY.**

**Lines whose number changed above this section: 0.**
Alters no gate, no threshold, no cap and no label. **The document is v1.3.**

### B2.1 ⚠ THE DICTIONARY THAT CAUSED THE T25R DIVERGENCE WAS NEVER UNDER ITS FREEZE

Raised by `heat-transfer-supervisor` and **re-measured at source by this lane
rather than relayed** (`VERIFICATION_CHARTER.md` §2n.19):

```
git show HEAD:docs/campaigns/T-family/T25R_PREREGISTRATION.md | grep -ci relax
    ->  0
```

**The word does not occur anywhere in the frozen T25R pre-registration.** Its
§3.4 "Registered numerics" table registers the solver, `adjustTimeStep`,
`deltaT`, `endTime`, `writeControl`/`writeInterval`, `writePrecision`, both
regions' `ddtSchemes`, the `divSchemes`, `nOuterCorrectors`,
`nNonOrthogonalCorrectors`, `momentumPredictor`, `nCorrectors`, the turbulence
model, `g`, radiation, the solid `kappa` and every material property — **and
omits `relaxationFactors` entirely.**

**THAT IS THE FINDING, AND IT IS LARGER THAN THE COMMENT IT AROSE FROM.** The
missing `UFinal`/`hFinal` keys are the *sole* measured cause of the 04:09Z
divergence (§3.4, confirmed by T25RF arm A0 under the new loads). **A
"registered numerics" table that omits a dictionary able to silently change the
answer — or to destroy the run — is not a complete registration**, however
correct every line it does contain.

### B2.2 WHAT IS EX-ANTE HERE, AND WHAT IS NOT — THE TWO ARE DIFFERENT CLAIMS

- **The T25R §3.5 gate DESIGN is provably ex-ante and this addendum does not
  question it.** `T25R_PREREGISTRATION.md` was committed at **`1a7bae7c`,
  2026-09-01T04:02:04Z**; `T25R_L1` launched at **04:09:33Z**
  (`STATUS.T25R_L1`). **Seven minutes and twenty-nine seconds.** The gate was
  designed before the answer existed, which is what rule 2 exists to prove.
- **The claim that the unrelaxed final sweep was a DELIBERATE CHOICE SERVING
  that gate is NOT ex-ante-established.** It appears only in a comment inside
  `T25R_L1/system/coolant/fvSolution` — an **untracked** file in an untracked
  run directory, carrying **no commit and therefore no date**. It may well be
  true; **it is not evidenced**, and this rung does not rest on it in either
  direction. §3.5.1 quotes that comment as the *stated* rationale for the
  retired gate and this addendum records that its provenance cannot be dated.

**Nothing in T25R2 changes on either point.** §3.5's retirement rests on
measurement — the calibration argument, plus B1.3's never-evaluable coupled `h`
threshold and B1.4's healthy run that the retired threshold would have voided —
and on none of it does the comment's provenance bear.

### B2.3 WHAT T25R2 ALREADY DOES ABOUT IT, STATED AS THE SUCCESSOR'S ONE LINE

**§3.4 registers `relaxationFactors` explicitly — every one of the five `Final`
keys LITERALLY, with its value — and `numerics_check` REFUSES (exit 2) if the
case that actually ran does not carry them**, refuses a quoted regex that would
match, refuses a wrong value, refuses the wrong `nOuterCorrectors` and refuses
the unreachable `p_rgh` tolerance. `stage_t25R2.py` is graded by that same check
in the same invocation that writes the dictionary, so a case the comparator
would refuse **cannot be staged**. Measured on the real run: the check passed on
`T25R2_L1` before a single number was read (§B1.1).

> **T25R registered the numerics it thought mattered. T25R2 registers the ones
> that do, and verifies them against the case that actually ran.**

### B2.4 THE RECURRING CLASS, NOW AT FIVE

Every instance is the same shape — **a fixture, control or reference that did
not resemble the thing it stood for** — and **every one was caught by RUNNING it,
none by reading it**:

| # | instance |
|---|---|
| 1 | `analyse_t25R.py`'s forged `checkMesh` log written to match its own regex, hiding two parser defects (§12.3) |
| 2 | A1.6's structural check matching its own search literals |
| 3 | a presentation lane's tail check passing on a dropped tail whose words recurred elsewhere |
| 4 | B1.5's selftest forging "has not run" as *"no directory"* when the real state is *"staged, no `STATUS`"* |
| 5 | a temperature compared against a bound belonging to a **different body** (§B1.6) — the same failure with *body* in place of *fixture* |

**Referred to the chief as a candidate standing rule; not enacted here.** A rule
is Sanaa's under the freeze, and this rung enacts none.

<!-- END OF T25R2 PRE-REGISTRATION v1.3 -->

---

## Addendum B3 — 2026-09-01, **THE GATE HAS RUN. DISCLOSURE ONLY.**

**Lines whose number changed above this section: 0.**
Alters no gate, no threshold, no cap and no label — **the gate it records is the
one frozen at `bb6e5761` and it was applied unchanged.** **Document v1.4.**

### B3.1 §3.5 IS `GATE FAIL`. EVERY ROW OF THIS RUNG IS `NOT A RESULT`.

Full record: **`docs/campaigns/T-family/T25R2_RESULTS.md`**.

**O1 `PASS`** 1.199542e-03 K ≤ 1.234e-02 · **O2 `PASS`** 6.675809e-04 K ≤
1.234e-03 · **O3 `GATE FAIL`** **2.315190e-02 K** > 1.234e-02, at t = 60 s.
All three were required. **The propagation registered at §3.5.4 before any
compute stands, and no physics number was printed.**

Both arms are `DONE` on all six conjuncts, `rc = 0`, uncapped. **The runs are
sound; their numbers are not sweep-count independent, which is a different thing
and is what the rung was built to find out.** Amendment A1's report: the t = 30 s
solid gap is **5.208e-04 K against the probe's measured 6.02e-03 K** — smaller
by 11.6×, so the sequence 5 → 10 → 20 is visibly converging. **It gated nothing.**

### B3.2 ⚠ A LATENT INSTRUMENT DEFECT THAT WOULD HAVE VOIDED D2 — **REFERRED, NOT REPAIRED**

Found while characterising the O3 failure. `read_patch_T` accepts only a
`nonuniform List<scalar>` patch entry and **REFUSES** anything else, expressly
declining to fall back to `refValue` (§7.2). On the real staged case the coolant
**inlet** is written as

```
    inlet { type fixedValue; value uniform 293; }
```

— a `uniform` entry. **So `read_inlet_T` REFUSES on every written time, and D2
("outlet > inlet at every written `t > 0`") would have made the whole rung
`NOT A RESULT` on an instrument refusal even if §3.5 had passed.**

**ROOT CAUSE — THE NIGHT'S RECURRING CLASS, SIXTH INSTANCE, AND AGAIN THIS
LANE'S:** `--selftest` forged the inlet patch **with** a `nonuniform` value list,
so the reader was never exercised against the form OpenFOAM actually writes for a
uniform `fixedValue`. **The fixture did not resemble the situation.**

**NOT REPAIRED, on the same grounds §2d.1 and B1.5 establish and on one more:**
the grading path is frozen post-compute; conditions (3) and (4) presuppose
published numbers and **there are none**; the failure direction is a **REFUSAL**,
which withholds and cannot publish; and **the defect is now unreachable in this
rung**, because §3.5 fails first and D2 is never evaluated. **Referred to the
supervisor and to verification, and flagged as something a successor
registration must fix in its own comparator before it can grade D2 at all.**

### B3.3 THE HALT RECOMMENDATION

**`T25R2_L2` and `T25R2_L2_DT025` are staged, verified, and should NOT be
launched under this registration.** Their verdict is already registered as
`NOT A RESULT` by §3.5.4's propagation, they run at 10 sweeps at a **higher**
Courant number, and both sensitivity panels require two **graded** arms and would
print `PENDING` regardless. POINT cost of running them anyway: **56.03
core-min**. **Waste by construction, named rather than absorbed.**
**The decision is the supervisor's; §7 of the results document prices the
successor's levers off T25R2's own measured rates.**

Spent: **19.780 core-min of the 390 hard cap, 370.2 unspent**, $0.0169 derived.

<!-- END OF T25R2 PRE-REGISTRATION v1.4 -->
