# DRAFT -- NOT FROZEN, NOT COMMITTED, NO COMPUTE AUTHORISED

**Multi-model solve sweep on the Closure Challenge benchmark meshes — feasibility
measurement.**

Written by a closure scoping lane on the closure supervisor's dispatch,
2026-08-27. **This is a feasibility measurement, not a proposal to run and not a
pre-registration.** No solver was started by this lane, no queue entry was
written, nothing was committed and no git index was touched. Every number below
either cites a file and line on disk or is labelled an extrapolation.

Motivating row: `_common/FEASIBILITY.md:77`, the **de Zordo-Banliat, Dergham,
Merle & Cinnella 2023** entry (space-dependent model aggregation,
arXiv:2301.09013v1), which needs *"several different turbulence models solved on
the same case"* and records the sweep as **FEASIBLE** at *"4 models x 41 cases x
~0.3 core-hours = ~50"*. This memo tests that prose against the disk.

---

## 0. Headline

The sweep is **constructible today**, but three of the four substitute models
cannot be set up from the shipped files alone, and one of them cannot be started
at all from the shipped initial condition. The FEASIBILITY.md case count is wrong
by one and its core-hour figure is, by accident, close to right.

| question | answer |
|---|---|
| usable OpenFOAM cases on disk | **40**, not 41 |
| all four substitute models present in the installed OpenFOAM | **yes**, v2606 |
| models runnable with **no** new `0/` field | `kOmega` **only** |
| models needing a **derived** `0/` field | `kEpsilon`, `LaunderSharmaKE` (epsilon on 11 of 40) |
| models needing an **invented** initial condition | `SpalartAllmaras` — see §3.4, this is the load-bearing finding |
| cost, 5 arms x 40 cases at a uniform 20 000-iteration cap | **58.8 core-h point / 71.5 core-h cap** (extrapolated from 4 measured rates) |
| against the charter's 487 core-h pre-authorisation (`CLOSURE_MODELLING_CHARTER.md:592`) | **12–15 %** |
| ranks per queue entry | **1** — see §5 |

---

## 1. The case inventory — 40, not 41

**Method.** `find /home/ubuntu/closure-challenge-benchmark -type d -name polyMesh`
over the un-ignored disk (not `grep -r`, which is `ugrep` here and honours ignore
files). For each hit the case root is `dirname(dirname(polyMesh))`; cell counts
are read from the `note` string in the header of `constant/polyMesh/owner`, and
that note was **corroborated against the first integer of
`constant/polyMesh/points`** on six cases — `nPoints` in the note matched the
points-list length in every one, so the notes are current rather than inherited.

**40 case roots carry `constant/polyMesh`, `0/`, `system/` and
`constant/turbulenceProperties`. All 40 carry all four. None is missing any.**

| family | cases | cells each | family cells |
|---|---|---|---|
| `Parm_PH_29` parametric hills | 29 | 15 600 | 452 400 |
| `PH_Breuer` periodic hill | 1 | 15 600 | 15 600 |
| `CBFS` curved backward-facing step (`CBFS13700`) | 1 | 21 000 | 21 000 |
| `NASA_2DWMH` wall-mounted hump | 1 | 51 626 | 51 626 |
| `DUCT` square/rectangular ducts | 8 | 2 209 – 31 819 | 101 026 |
| **total** | **40** | | **641 652** |

Ducts individually: `AR_1_Ret_180` 2 209, `AR_1_Ret_360` 3 025, `AR_3_Ret_180`
6 627, `AR_3_Ret_360` 8 748, `AR_5_Ret_180` 11 045, `AR_7_Ret_180` 15 463,
`AR_10_Ret_180` 22 090, `AR_14_Ret_180` 31 819.

All 29 `Parm_PH_29` hills share one mesh topology: every one reports
`nPoints:31702  nCells:15600  nFaces:62650  nInternalFaces:30950` in its own
`owner` note. The `_2024 / _3036 / _4048` suffixes are **not** mesh resolutions —
they index the parametric family, not the grid.

### 1.1 Reconciliation with the two prose counts

* **`_common/BASELINES.md:266-267`** states *"29x15600 + 101026 (ducts) + 15600 +
  21000 + 51626 = **641,652** across **40 cases**"*. **BASELINES.md is correct.**
  Its arithmetic reproduces exactly, and its duct subtotal 101 026 is the sum of
  the eight per-case counts above.
* **`_common/FEASIBILITY.md:77`** says *"4 models x **41 cases**"*. **That figure
  is wrong by one.** There is no 41st case root on disk. The likeliest origin is
  a miscount of the hill family (29, not 30) or an inclusion of
  `data/evaluation_points/`, which holds **8** `*_points.csv` scoring files and
  no mesh. The same "41-case sweep" phrasing recurs at `FEASIBILITY.md:116` for
  the Emory/Iaccarino row and is wrong there for the same reason.
* The 3-D cases named in the benchmark README (wing-body junction, Ahmed body,
  FAITH hill, 3-D duct meshes) are **not in the local clone** — already recorded
  at `BASELINES.md:317-318`, and confirmed here: `data/` has no such directory.

**Nothing in the inventory blocks the sweep.** Every case has a mesh, an initial
field set, a system dictionary set and a turbulence dictionary.

---

## 2. What the shipped k-omega SST setup actually is

Representative case: **`/home/ubuntu/closure-challenge-benchmark/data/CBFS`**
(21 000 cells). Established by reading the files; **the case was not run.**

### 2.1 It is not a template — it already holds an answer

`data/CBFS/` contains `0/` **and** `30000/`. The same is true of every one of the
40: each ships its own converged time directory (`10000` for `PH_Breuer`, `2000`
for `NASA_2DWMH`, `20000` for the hills, `334`–`7009` for the ducts). Two
consequences:

1. **Nothing may be run in place.** `QUEUE_ENTRY_STANDARD.md` §4 check 4 refuses a
   `cwd` that already contains `0/` or any numeric time directory, and standing
   rule 4's age guard could not be evaluated against a tree that already holds an
   answer. See §6.
2. `system/controlDict` says `startFrom latestTime`. Staged naively **with** the
   time directory, a run would restart from 30 000 rather than from zero and
   write nothing. The staging step must drop time directories and pin
   `startFrom startTime; startTime 0;`.

### 2.2 The solver binary is not named in the shipped CBFS `controlDict`

`data/CBFS/system/controlDict` carries **no `application` entry**. The lab's own
measured runs on these meshes name it explicitly: every `log.run` under
`/home/ubuntu/closure-data/aposteriori/kaandorp/` reports `Exec : simpleFoam
-case .` and `nProcs : 1`, on `Build : _481094f-20260618 OPENFOAM=2606
version=2606`. The 29 hills **do** name it —
`Parm_PH_29/.../system/controlDict` line 20 reads `application simpleFoam;//`.
**The solver is `simpleFoam`,** steady-state incompressible SIMPLE.

### 2.3 `constant/turbulenceProperties` — quoted

`data/CBFS/constant/turbulenceProperties`, verbatim below the header:

    simulationType RAS;

    RAS
    {

        RASModel        kOmegaSST;
        turbulence      on;
        printCoeffs     on;
        //baseline        true;



    }

39 of the 40 cases name `kOmegaSST` this way. **The exception is
`NASA_2DWMH`**, whose `constant/turbulenceProperties` names **`AugmentedkOmegaSST`**
with `omegaMin 0.1;` and `baseline true;`. That model does not exist in OpenFOAM
v2606; it comes from `libfrozenIncompressibleTurbulenceModels.so`, which
**is not present anywhere on this box** (`find / -name
'libfrozenIncompressibleTurbulenceModels*'` returns nothing). So the NASA case
**cannot be re-run in its shipped configuration here at all** — a fact that the
multi-model sweep incidentally removes, because every arm of the sweep replaces
`RASModel` with a model that *is* installed.

### 2.4 The `libs` line, and why it is not fatal

Eleven cases (`CBFS`, `PH_Breuer`, `NASA_2DWMH`, all 8 ducts) plus exactly one
hill carry `libs ( "libfrozenIncompressibleTurbulenceModels.so" );` in
`system/controlDict`. The library is absent. In v2606 that is a **warning, not a
fatal error**: `src/OpenFOAM/db/dynamicLibrary/dlLibraryTable/dlLibraryTable.C:185-190`
takes the `!ptr` branch and emits *"Could not load "* through `WarningInFunction`
/ `InfoErr`, then returns a null pointer; no `FatalError` is raised. So a staged
case keeps running with the line present.

**Standing rule 14 applies here and is easy to get wrong:** `libs` entries are
*inserted with an assert, never replaced*. The staging step must **not delete**
that line to tidy the case up.

### 2.5 The one heterogeneous hill

`Parm_PH_29/alpha_15/alpha_15_10929_2024/system/controlDict:18` carries the
`libs (...)` line; its 28 siblings do not. `diff` against
`alpha_15_10929_3036/system/controlDict` shows that single added line and nothing
else. A bulk staging script that assumes the 29 hills are byte-identical in
`system/` is wrong on this one file.

### 2.6 `system/controlDict` — the run-control numbers, and they are **not uniform**

| family | `endTime` | `deltaT` | `writeInterval` | `startFrom` | working convergence control |
|---|---|---|---|---|---|
| `CBFS` | 30 000 | 1 | 30 000 | `latestTime` | `residualControl { p 1e-15; }` — unreachable |
| `PH_Breuer` | 10 000 | 1 | 10 000 | `latestTime` | none read by v2606 |
| `NASA_2DWMH` | 2 000 | 1 | `$endTime` | `latestTime` | — |
| `Parm_PH_29` (29) | 20 000 | 1 | 4 000 | `latestTime` | **`convergence 1e-8;`** — see below |
| `DUCT` (8) | **500 000** | 1 | `$endTime` | `latestTime` | `residualControl { k 5e-6; omega 1e-10; }` |

Two traps in that table:

* The hills' `SIMPLE { convergence 1e-8; }` is **not a v2606 keyword**. v2606's
  SIMPLE control reads a `residualControl` sub-dictionary; a bare `convergence`
  entry is silently ignored. The hills therefore have **no working convergence
  criterion** and run to `endTime` 20 000 unconditionally.
* The ducts' `endTime` is **500 000**. Their shipped time directories (334, 405,
  1 109, 1 540, 2 428, 3 636, 5 125, 7 009) show `residualControl` firing early
  under kOmegaSST — but that criterion names **`omega`**, a field three of the
  four substitute models do not solve. Under `kEpsilon` or `SpalartAllmaras` the
  criterion collapses to whatever remains, and if it is never met the run goes to
  **half a million iterations**. On `AR_14_Ret_180` that is ~875 core-min for a
  single entry. **This is the single largest cost risk in the sweep and it is
  entirely a dictionary artefact.** §4 costs the sweep only under a uniform cap.

### 2.7 Boundary conditions, CBFS

| field | `internalField` | `bottomWall` / `topWall` | `inlet` | `outlet` | `frontAndBack` |
|---|---|---|---|---|---|
| `U` | `uniform (0.72 0 0)` | `fixedValue (0 0 0)` (CBFS ships an explicit zero vector, not `noSlip`) | `fixedValue`, non-uniform 150-entry profile | | `empty` |
| `p` | `uniform 0` | `zeroGradient` | `zeroGradient` | `fixedValue`, non-uniform 150-entry profile | `empty` |
| `k` | `uniform 0.00668` | `fixedValue uniform 1e-15` | `fixedValue`, 150-entry profile | | `empty` |
| `omega` | `uniform 0.11` | `omegaWallFunction`, `value uniform 1000` | `fixedValue`, 150-entry profile | | `empty` |
| `nut` | `uniform 0` | `nutLowReWallFunction`, `value uniform 0` | `calculated uniform 1e-15` | `calculated uniform 1e-15` | `empty` |

`k` pinned to 1e-15 at the wall and `nut` on `nutLowReWallFunction` are the
signature of a **wall-resolved (integrate-to-the-wall) mesh**. *I did not compute
y+; that reading is from the boundary-condition types, not from a measurement.*
The ducts use the same combination on `wallTop`/`wallSide`, with `cyclic`
inflow/outflow and `symmetry` on the two symmetry planes, and are driven by a
`meanVelocityForce` fvOption. The hills are `cyclic` streamwise with an
`empty` spanwise pair and the same `meanVelocityForce`. `NASA_2DWMH` is the odd
one out again: it uses **`nutUSpaldingWallFunction`** on `bottom`.

`transportProperties` is Newtonian throughout; CBFS carries
`nu [0 2 -1 0 0 0 0] 7.299270072992701e-05` (`Re_H = 13700`); the hills carry
`nu ... 0.0001786` (`Re_H = 5600`); the ducts get `nu` and `Re_b` by
`#include "../caseDef"` — see §6.3, that include is a staging landmine.

### 2.8 `fvSchemes` and `fvSolution`, CBFS

`fvSchemes`: `ddtSchemes default steadyState`; `gradSchemes default Gauss
linear`; `divSchemes default Gauss linear` with `div(phi,U)`, `div(phi,k)` and
`div(phi,omega)` each `Gauss linearUpwind grad(U)`; `laplacianSchemes default
Gauss linear corrected`; `snGradSchemes default corrected`; and
`wallDist { method meshWave; }` — present in all five archetypes checked, which
matters because `SpalartAllmaras` needs a wall distance just as `kOmegaSST` does.

`fvSolution`: `p` on GAMG (`tolerance 1e-12`, `relTol 0.001`, GaussSeidel
smoother, `nCellsInCoarsestLevel 50`); `U`, `k`, `omega` **and `epsilon`** on
PBiCG/DILU at `tolerance 1e-09`, `relTol 0.1`; a `nuTilda` block exists but is
**commented out inside a `/* ... */`**. `SIMPLE { nNonOrthogonalCorrectors 1;
pRefPoint (0.5 1 0); pRefValue 1; residualControl { p 1e-15; } }`.
`relaxationFactors`: `p 0.5, U 0.5, k 0.7, omega 0.7, epsilon 0.7`.

---

## 3. The substitution question

### 3.0 All four models are installed

`ls /usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/RAS/`
lists `kEpsilon`, `kOmega`, `SpalartAllmaras`, `LaunderSharmaKE` alongside
`kOmegaSST`, `RNGkEpsilon`, `realizableKE`, `LRR`, `SSG`, `EBRSM`, `GEKO`,
`kEpsilonPhitF`, `kOmegaSSTLM`, `kOmegaSSTSAS`. **No model has to be written.**

### 3.1 What each model MUST_READ, from the source

| model | required `0/` fields | source citation |
|---|---|---|
| `kOmega` | `k`, `omega` | `RAS/kOmega/kOmega.C:133`, `:145` (`IOobject::MUST_READ`) |
| `kEpsilon` | `k`, `epsilon` | `RAS/kEpsilon/kEpsilon.C:210`, `:222` |
| `LaunderSharmaKE` | `k`, `epsilon` | `RAS/LaunderSharmaKE/LaunderSharmaKE.C:180`, `:193` |
| `SpalartAllmaras` | **`nuTilda`** | `Base/SpalartAllmaras/SpalartAllmarasBase.C:316-323` |

### 3.2 What the 40 cases actually ship

* `k`, `omega`, `nut`, `U`, `p` — **all 40**.
* `epsilon` — **29 of 40**, exactly the `Parm_PH_29` hills. The 11 without it are
  `CBFS`, `PH_Breuer`, `NASA_2DWMH` and the 8 ducts.
* `nuTilda` — **0 of 40**. `find` over the whole clone returns no file of that
  name.

### 3.3 Model by model, concretely

**`kOmega` (Wilcox) — clean. Nothing must be invented.**
`k` and `omega` are shipped on all 40 with the right wall treatment
(`omegaWallFunction`, `k` fixed near zero, `nut` on `nutLowReWallFunction`). A
`solvers { omega { ... } }` entry exists in every archetype checked. `div(phi,omega)`
is explicit on CBFS, `PH_Breuer`, `NASA_2DWMH` and the ducts; on the 29 hills it
is **absent** and falls to `divSchemes default Gauss linear` — but that is
already how the shipped kOmegaSST hills run, so it is the shipped condition and
not a new risk introduced by the substitution. **`kOmega` is a
turbulenceProperties-only change on all 40 cases.**

**`kEpsilon` — one derived field, one added solver entry, one honest model-form defect.**
1. `0/epsilon` must be constructed for the **11** cases that lack it. The relation
   is `epsilon = Cmu * k * omega` with `Cmu = 0.09` — this is OpenFOAM's own
   definitional conversion inside the k-omega family, not a fit. **Derivable from
   what is shipped, not invented.**
2. The **wall boundary condition** for `epsilon` on those 11 is **not** derivable.
   The 29 hills that ship `epsilon` use `epsilonWallFunction` with
   `value uniform 14.855`; nothing in the other 11 dictates a choice.
   **`epsilonWallFunction` vs `fixedValue` is a modelling choice and belongs in a
   pre-registration, not in a staging script.**
3. A `solvers { epsilon { ... } }` block exists on **CBFS and `PH_Breuer` only**.
   It is **absent** on the 8 ducts (which have `p`, `"(U|k)"`, `omega`), on
   `NASA_2DWMH`, and on the 29 hills (`p`, `pFinal`, `U`, `k`, `omega`). A missing
   solver block for a solved field is **fatal at run time**, not a warning.
   Likewise `relaxationFactors epsilon` exists on CBFS only.
4. **The honest defect.** Standard `kEpsilon` is a high-Reynolds-number model
   calibrated for use with wall functions. These meshes are wall-resolved (§2.7).
   The arm will *run*, and it will produce a number, but its near-wall answer is a
   model applied outside its own calibration range. **That must be stated in the
   pre-registration as a known property of the arm, not discovered in the
   results.** It is also, arguably, exactly the kind of model-form error the
   de Zordo-Banliat aggregation is meant to weight down — which makes it useful,
   but only if it is declared.

**`LaunderSharmaKE` — same field and dictionary work; the physically apt low-Re
k-epsilon.** Identical requirements to `kEpsilon` (items 1-3 above). Unlike
`kEpsilon` it carries low-Re damping functions and is the appropriate k-epsilon
variant for a wall-resolved mesh, so it is the arm that makes the k-epsilon
family a fair comparator rather than a straw man. *I did not read this model's
recommended wall boundary condition out of the source; the epsilon wall BC for
this arm is unsettled by this memo and must be fixed in the pre-registration.*

**`SpalartAllmaras` — the load-bearing one. See §3.4.**

### 3.4 SpalartAllmaras cannot be started from what is shipped

`nuTilda` is shipped on **no** case. Two candidate routes, and both have a
problem that must be surfaced before, not after, a run.

**Route A — invert the shipped `nut`.** The SA constitutive relation is in the
source: `nut = nuTilda * fv1(chi)`, `chi = nuTilda/nu`, `fv1 = chi^3/(chi^3 +
Cv1^3)` (`SpalartAllmarasBase.C:44`, `:55`, `:166`), with `Cv1 = 7.1`
(`SpalartAllmaras.H:77`). That is strictly monotone in `nuTilda`, so the
inversion is unique and solvable per cell by bisection. **Derivable, not
invented.**

**But it inverts to zero.** Every case ships `0/nut` with
`internalField uniform 0` — verified on a hill, on CBFS and on a duct. Inverting
zero gives `nuTilda = 0` in every cell, and **`nuTilda = 0` is a fixed point of
the SA transport equation**: production is proportional to `nuTilda`, so a field
of exact zeros never leaves zero. **Route A from `0/nut` yields a dead solve, not
a laminar one — it yields a run that terminates cleanly, writes fields, satisfies
the completion rule, and means nothing.** That is the shape standing rule 3
exists to catch, arriving through the initial condition rather than through a
reader.

**Route B — invert the *converged* `nut` in each case's shipped time directory**
(`CBFS/30000/nut`, `hills/20000/nut`, etc., all `nonuniform List<scalar>`). This
gives a live field, but it is a **warm start from the kOmegaSST answer**, which
biases the SA arm toward SST and destroys the independence the whole sweep is
for.

**Route C — the standard freestream value, `nuTilda = 3*nu` (or 5*nu) uniform.**
This is the textbook SA initialisation and is what most practitioners would do.
**It is an invented initial condition.** Naming it here rather than burying it in
a staging script is the point of this section: *the SA arm's initial condition is
a modelling choice with no defensible derivation from the shipped files, and it
must be written into a pre-registration with its value fixed, or the SA arm is
not a measurement.*

Further `SpalartAllmaras` work items:
* **`solvers { nuTilda { ... } }` exists nowhere** — commented out on CBFS,
  absent elsewhere. Must be added; fatal otherwise.
* **`div(phi,nuTilda)` exists nowhere** and would fall to `divSchemes default
  Gauss linear` — unbounded central differencing on a positive-definite
  transported scalar, which can drive `nuTilda` negative. `bounded Gauss
  linearUpwind` or `Gauss upwind` is the sane choice; **it is a choice and must be
  registered.** (The 29 hills already carry a `relaxationFactors nuTilda` entry,
  uncommented, left over from an earlier setup.)
* **`nut` wall BC is fine unchanged.** `nutLowReWallFunction::calcNut()` returns
  `tmp<scalarField>::New(patch().size(), Zero)`
  (`lnInclude/nutLowReWallFunctionFvPatchScalarField.C:38-42`) — a model-agnostic
  zero, with no dependence on `k`. **Verified by reading the body**, because a
  name is not a behaviour.
* `nuTilda` wall BC: `fixedValue uniform 0` is standard. Also a registered choice.

### 3.5 Summary table — what must change beyond `constant/turbulenceProperties`

| | `kOmega` | `kEpsilon` | `LaunderSharmaKE` | `SpalartAllmaras` |
|---|---|---|---|---|
| new `0/` field | none | `epsilon` on **11** cases | `epsilon` on **11** cases | **`nuTilda` on all 40** |
| field derivable from shipped data? | n/a | **yes**, `Cmu*k*omega` | **yes**, `Cmu*k*omega` | inverts to **zero** — see §3.4 |
| new `0/` wall BC choice | none | **yes** (epsilon) | **yes** (epsilon) | **yes** (nuTilda) |
| `fvSolution` `solvers` entry to add | none | on **38** of 40 | on **38** of 40 | on **40** of 40 |
| `fvSolution` `relaxationFactors` entry | none | on 39 of 40 | on 39 of 40 | on 11 of 40 |
| `fvSchemes` `div(phi,·)` to add | none (falls to default on hills, as shipped) | present on 11, default on 29 | same | **absent everywhere** |
| `SIMPLE residualControl` still valid? | yes | **no** — names `omega` | **no** | **no** |
| invented IC required? | **no** | no | no | **YES** |

---

## 4. Cost — measured anchors, and what is extrapolated from them

### 4.1 What is MEASURED

Four independent rates, all serial (`nProcs : 1`), all `simpleFoam` on
OpenFOAM v2606 on this box, all on **these exact meshes**:

| case | cells | s/iteration | µs per cell-iteration | source |
|---|---|---|---|---|
| `AR_1_Ret_360` | 3 025 | **0.010814** stock | 3.575 | `Kaandorp2020_TBRF/aposteriori/RESULTS.md:393` |
| `AR_3_Ret_360` | 8 748 | **0.035079** stock | 4.010 | same file, `:394` |
| `CBFS13700` | 21 000 | **0.069512** injected | 3.310 | same file, `:395-396` (`CBFS13700__TRUTHR`) |
| `alpha_10_9000_3036` | 15 600 | **0.037242 – 0.048116** | 2.387 – 3.084 | `/home/ubuntu/closure-data/aposteriori/kaandorp/alpha_10_9000_3036__EIG_*/log.run`, 5 000 `ExecutionTime` lines against 186.21 – 240.58 s |

Corroboration from a fifth log: `CBFS13700__NULL/log.run` shows 884
`ExecutionTime` lines and a final `ExecutionTime = 68.95 s` → 0.078 s/iteration →
3.714 µs per cell-iteration. The lane-level accounting is at
`RESULTS.md:773-785`: **13 158.8 solver wall s = 219.313 core-min** for that
lane's rows at ranks 1, with `RESULTS.md:770-771` stating *"All solves serial:
`nProcs : 1` in every `log.run`, `OMP_NUM_THREADS=1` set by the driver, so
**ranks = 1** and core-minutes = wall-seconds ÷ 60."*

**Measured envelope: 2.39 – 4.01 µs per cell-iteration, serial.** I use **3.3**
as the point rate and **4.01** as the conservative rate.

**One measured outlier, deliberately excluded.**
`/home/ubuntu/closure-data/xiao/G0_sst_alpha_10_9000_3036/log.run` shows 8 000
iterations in 26.21 s = 0.21 µs per cell-iteration, ~15x faster than any other
row. Its header reads `Create mesh for time = 20000` — it is a **restart from an
already-converged field**, where every linear solve meets tolerance in its
minimum sweeps. It is a real measurement of a warm continuation and **not** a
rate for a sweep that must move the solution. Using it would understate the sweep
by an order of magnitude.

### 4.2 What is EXTRAPOLATED

The model is **core-min = cells x iterations x rate / 60**, linear in both cells
and iterations, at ranks = 1. Linearity in cells is supported across a 7x cell
range (3 025 → 21 000) by the four anchors above, which span only 2.39–4.01
µs/cell-it. **It is an extrapolation, not a measurement**, and it is untested
above 21 000 cells — `AR_14_Ret_180` (31 819) and `NASA_2DWMH` (51 626) are
outside the measured range and their rows below are the least trustworthy.

**Iteration count is the dominant uncertainty, not the rate.** A model that fails
to converge runs to the cap; a model that converges early costs a fraction. The
figures below charge **every** entry at the cap, which is the honest planning
number and an overestimate for the arms that converge.

### 4.3 Per case, per model, at a uniform 20 000-iteration cap and 3.3 µs/cell-it

| case | cells | core-min per model-case |
|---|---|---|
| `AR_1_Ret_180` | 2 209 | 2.43 |
| `AR_1_Ret_360` | 3 025 | 3.33 |
| `AR_3_Ret_180` | 6 627 | 7.29 |
| `AR_3_Ret_360` | 8 748 | 9.62 |
| `AR_5_Ret_180` | 11 045 | 12.15 |
| `AR_7_Ret_180` | 15 463 | 17.01 |
| any `Parm_PH_29` hill, and `PH_Breuer` | 15 600 | 17.16 |
| `CBFS13700` | 21 000 | 23.10 |
| `AR_10_Ret_180` | 22 090 | 24.30 |
| `AR_14_Ret_180` | 31 819 | 35.00 |
| `NASA_2DWMH` | 51 626 | 56.79 |

### 4.4 Totals

Per model, all 40 cases, 641 652 cells x 20 000 iterations:

| rate basis | core-min per model | core-h per model | x4 models | x5 arms (incl. SST null) |
|---|---|---|---|---|
| 2.387 µs (measured floor) | 510.5 | 8.51 | **34.0 core-h** | **42.5 core-h** |
| **3.30 µs (point)** | **705.8** | **11.76** | **47.1 core-h** | **58.8 core-h** |
| 4.01 µs (measured ceiling) | 857.7 | 14.29 | **57.2 core-h** | **71.5 core-h** |

**The fifth arm is not padding.** Re-solving `kOmegaSST` in the identical staged
harness, and checking it reproduces the shipped `30000/`-directory field, is this
sweep's planted control: it is the only thing that shows the harness can produce
a *known* answer before it is trusted with four unknown ones. Without it a
uniform result across four arms is indistinguishable from a staging bug.

**FEASIBILITY.md:77's "~50 core-hours" is close to right**, and closer than its
own arithmetic deserves: its `4 x 41 x 0.3 core-h` uses a per-case rate of 0.3
core-h = 18 core-min, against a measured mean over the 40 cases of 17.6 core-min
at the 20 000-iteration cap. The case count is wrong and the rate was not derived
from measurement, but the total lands within 6 %.

### 4.5 The cap is doing all the work — the shipped `endTime` figures do not

Charging each family at its **shipped** `endTime` (§2.6) instead:

| family | shipped iterations | core-min per model |
|---|---|---|
| 29 hills | 20 000 | 497.6 |
| `PH_Breuer` | 10 000 | 8.6 |
| `CBFS` | 30 000 | 34.6 |
| `NASA_2DWMH` | 2 000 | 5.7 |
| **8 ducts** | **500 000** | **2 778.2** |
| **total per model** | | **3 324.8 core-min = 55.4 core-h** |

**x4 = 221.7 core-h, x5 = 277 core-h** — 45–57 % of the entire 487 core-h
pre-authorisation, with **84 % of it spent on eight duct cases** because of one
`endTime` line. **A uniform iteration cap is not an optimisation here; it is the
difference between a 59-core-hour sweep and a 277-core-hour one**, and it is the
first thing any pre-registration for this sweep must fix.

### 4.6 Cost basis honesty

All figures above are in **core-minutes**, the lab's measured unit. Any dollar
figure derived from them uses the owner-stated **c7a.4xlarge at $0.0513/core-h**
and is **derived, not measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). At the 58.8 core-h point figure that is **$3.02
derived**. Under $25, and so inside the 2026-08-21 blanket — *and still costed
here, because a blanket is not a per-item read* (standing rule 9).

---

## 5. Parallel or serial — serial, 1 rank per entry

### 5.1 What the disk says

* **Every measured run on these meshes was serial.** All 31 `log.run` files under
  `/home/ubuntu/closure-data/aposteriori/kaandorp/` report `nProcs : 1`, as does
  `/home/ubuntu/closure-data/xiao/G0_sst/log.run`.
  `Kaandorp2020_TBRF/aposteriori/RESULTS.md:390-391` states it as a property of
  the lane: *"All solves in this lane are **serial** (`simpleFoam -case .`,
  `nProcs : 1`, `OMP_NUM_THREADS=1`)"*.
* **`decomposeParDict` is present but unused.** The ducts ship
  `numberOfSubdomains 4; method scotch;`, the hills `numberOfSubdomains 8; method
  scotch;`, and `PH_Breuer` and `NASA_2DWMH` each ship one. **`CBFS` ships none.**
  No `processor*` directory exists anywhere in the clone. The dictionaries are
  inherited from whoever generated the benchmark, not evidence of a parallel run
  here.

### 5.2 The recommendation, and the reasoning behind it

**One rank per entry (`ranks: 1`), many concurrent entries.**

1. **Total work is fixed.** The sweep is ~2 823 core-min (point). Running entries
   one-per-core is embarrassingly parallel with no communication, so wall time
   falls as `total / concurrency` at ~100 % efficiency in core-minutes. MPI
   decomposition of a single case cannot beat that; it can only lose to it.
2. **These meshes are far too small to decompose.** 15 600 cells over the shipped
   8 subdomains is **1 950 cells per rank**; the smallest duct over its shipped 4
   is **552**. OpenFOAM's SIMPLE loop amortises halo exchange and the GAMG
   coarse-level global reductions only at roughly 10⁴–10⁵ cells per rank. Below
   ~2 000 cells per rank the communication dominates and **core-minutes go up**
   for the same answer — the wall clock might fall, but the box's throughput
   falls with it.
3. **The box is already oversubscribed, so wall time per entry is the wrong
   objective anyway.** Read at the time of writing: `nproc` = **16**;
   `/proc/loadavg` = **18.86 17.20 15.79** — the 1-minute load already exceeds the
   core count, with `icoFoam`, five `buoyantBoussinesq*` ranks and four `python`
   processes at ~99 % CPU. Under contention, minimising core-minutes *is*
   maximising throughput; minimising per-case wall time by adding ranks actively
   harms every other team.
4. **Memory, not cores, is the nearer ceiling.** `free -g` reads **30 GB total,
   20 used, ~9 available**. A 15 600-cell serial `simpleFoam` is small, but I
   **did not measure** a resident-set size for these cases, so any
   `memory_floor_gb` in an entry must be labelled *estimated, not measured*.
   A defensible placeholder: **1.0 GB** for cases up to 32 k cells and **2.0 GB**
   for `NASA_2DWMH`.

**Honest limitation.** There is **no parallel run of these cases on disk**, so the
"serial is better" conclusion is **reasoned from cells-per-rank and from the
fixed total work, not measured**. If the supervisor wants it measured, the cheap
experiment is one case (`AR_14_Ret_180`, the largest duct) at ranks 1 / 2 / 4 for
a few hundred iterations each — a few core-minutes total — and that experiment
would itself need a pre-registration if its numbers are to be cited.

**Concurrency is a runner property, not an entry property.** Nothing in
`QUEUE_ENTRY_STANDARD.md` gives entries an ordering or a concurrency semantic —
§6 says so explicitly: *"It does not schedule, order, prioritise or start
anything."* Each entry declares `ranks: 1` and the launch policy decides how many
run at once.

---

## 6. Run-root layout and the age-guard constraint

### 6.1 The constraint, quoted

`docs/standards/QUEUE_ENTRY_STANDARD.md` §4, check 4 (`AGE-GUARD`):

> refuse if `cwd` is absent, or already contains `0/` or any numeric time
> directory (`0`, `0.1`, `250`, `1e-05`)

with the reason given as standing rule 4: *"a pre-existing time directory makes
that unprovable for the run that would follow. A run is never launched into a
tree that already holds an answer."*

**`0` is itself a numeric time directory.** So a valid staged case **must not have
a `0/` directory at enqueue time** — even though an OpenFOAM case cannot start
without one. The lab already has the resolution: the fields are staged as
**`0.orig/`**, and the launcher creates `0/` from it as its first act.
`verification/runs/T-family/T5_runs/run_one_t5.sh:128-130` does exactly this and
**refuses** if `0.orig` is missing; the accepted heat-transfer entry
`verification/queue/heat-transfer/T5_S_m.json` records the state as
`"age_guard": "0.orig present; NO 0/ and NO numeric time directory"`.

### 6.2 Proposed layout — outside the git repository

Run outputs never live beside the prose describing them, and this data is far too
large for git:

    /home/ubuntu/closure-data/multimodel_sweep/
      <ARM>/<CASE_ID>/
        0.orig/          <- the armed initial fields; NEVER 0/
        constant/
          polyMesh/
          transportProperties
          turbulenceProperties       <- the ONLY per-arm physics edit
        system/
        caseDef                      <- ducts and NASA_2DWMH only; see 6.3
      _staging/
        stage_multimodel.py          <- the staging step
        STAGING_MANIFEST.json        <- what it copied, per case, with hashes

`<ARM>` in `{ kOmegaSST_null, kOmega, kEpsilon, LaunderSharmaKE, SpalartAllmaras }`.
`<CASE_ID>` flattens the benchmark path: `CBFS13700`, `PH_Breuer`, `NASA_2DWMH`,
`AR_1_Ret_360` … , `alpha_10_9000_3036` … .

Each entry's `cwd` is `/home/ubuntu/closure-data/multimodel_sweep/<ARM>/<CASE_ID>`.
It **exists**, contains `constant/`, `system/` and `0.orig/`, and contains **no
`0/` and no numeric time directory** — so check 4 passes and the age guard is
evaluable afterwards, because `0/T`-equivalent (`0/U`) is created by the
launcher, after which every field at `endTime` is necessarily newer.

**Entry count: 5 arms x 40 cases = 200 entries** (160 if the SST null is dropped,
which §4.4 argues against).

### 6.3 What the staging step must copy — exactly

Per `(arm, case)`, from `/home/ubuntu/closure-challenge-benchmark/data/<case>`:

1. **`constant/polyMesh/`** — `points faces owner neighbour boundary`, **and**
   `cellZones faceZones pointZones` where present (hills and ducts have them;
   CBFS has a `sets/` directory instead and `PH_Breuer` has both). Copy the
   directory wholesale rather than an enumerated file list.
2. **`constant/transportProperties`** verbatim.
3. **`constant/turbulenceProperties`** — the **only** physics file rewritten:
   `RASModel <ARM>`, everything else preserved. For the `kOmegaSST_null` arm it is
   copied byte-for-byte, except on `NASA_2DWMH`, where `AugmentedkOmegaSST` must
   become `kOmegaSST` because the augmenting library does not exist on this box
   (§2.3) — **that substitution is itself a registered deviation**, not a fix.
4. **`constant/C Cx Cy Cz V`** — the ducts ship these as constant fields. Copy
   them or drop them, but do it **uniformly across all 40 and all 5 arms**, and
   record the choice; an inconsistency here becomes a phantom arm-to-arm
   difference.
5. **`caseDef`** — `DUCT/<case>/caseDef` and `NASA_2DWMH/caseDef`. **This is the
   staging landmine.** `system/fvOptions` contains `#include "../caseDef"`, which
   resolves relative to `system/`, i.e. to the case root. Staging `system/` and
   `constant/` without `caseDef` produces a case that fails at read time on all
   nine of those cases. The hills have no `caseDef` and need none.
6. **`system/`** — everything, including `fvOptions` (the `meanVelocityForce`
   that drives the ducts and hills; without it the periodic cases have no
   forcing), the `#includeFunc` sampling dictionaries named in `controlDict`, and
   `topoSetDict` / `blockMeshDict` where present. Three files are then patched:
   * **`controlDict`**: `startFrom startTime; startTime 0;` (replacing
     `latestTime`, §2.1); a **uniform** `endTime` (the cap, §4.5);
     `writeInterval` equal to `endTime` so fields exist at `endTime`;
     `purgeWrite 0`; `application simpleFoam;` inserted where absent.
     **The `libs (...)` line is left in place** — standing rule 14: `libs` entries
     are inserted with an assert, never replaced, and never quietly deleted.
   * **`fvSolution`**: add the arm's missing `solvers` block (`epsilon` on 38
     cases for the two k-epsilon arms, `nuTilda` on all 40 for SA) and its
     `relaxationFactors` entry; replace the model-specific `residualControl`
     (§2.6) with a **model-uniform** criterion, since a criterion naming `omega`
     silently changes meaning across arms.
   * **`fvSchemes`**: add `div(phi,nuTilda)` for the SA arm. Leave everything
     else alone.
7. **`0/` → `0.orig/`**, with three edits:
   * **keep** `U p k omega nut`;
   * **drop** the truth fields `U_LES k_LES p_LES tauij_LES`, the geometry fields
     `C Cx Cy Cz`, the `uniform/` sub-directory (it carries time-index state),
     and `interpolatedFields/` / `inletOutletFields/` where the run does not need
     them — **but only if nothing in the staged `system/` `#include`s them**;
   * **add** the arm's own field: `epsilon` (derived, §3.3) or `nuTilda`
     (registered IC, §3.4).
8. **Copy no numeric time directory.** Not `30000/`, not `20000/`, not `405/`.
   This is what makes check 4 pass and what keeps the SST null honest.

### 6.4 Staging runs before enqueue, and writes a manifest

The staging step is **not a solver launch** and needs no queue entry. It must
finish, and its output must be verified, **before** any entry is written — an
entry whose `cwd` does not yet exist is refused at check 4 anyway. The manifest
should record, per staged case: the source path, the file list copied, a hash of
each patched dictionary, the cell count read back from the staged
`constant/polyMesh/owner`, and an explicit assertion that `0/` is absent and no
numeric time directory exists. **A staging script that reports success without
having read those things back off disk is the shape standing rule 3 refuses.**

---

## 7. What this sweep would and would not establish

*(This section is written to `CLOSURE_MODELLING_CHARTER.md` §16 — "what it cannot
see" is mandatory and a record without one is returned.)*

### 7.1 What it establishes

A **model-form spread**: for each of 40 flows, four or five converged RANS fields
that differ **only** in the closure, on an identical mesh, with identical
numerics, identical forcing and identical boundary conditions. That spread is a
real, reusable measurement, and it is the input the de Zordo-Banliat aggregation
requires and the lab does not currently have. It also extends `BASELINES.md`,
which today records **one** closure's error against LES/DNS and would then record
four or five.

### 7.2 What it cannot see

**A spread is not an error, and this sweep on its own is not a validation.**
Four models disagreeing tells you the answer is closure-sensitive; it does not
tell you which one is right, or that any of them is. The disagreement could be
large where all four are accurate and small where all four are wrong in the same
direction — linear eddy-viscosity models share a constitutive assumption, so
their errors are **correlated, not independent**, and their spread systematically
**understates** the true model-form uncertainty. Three of the four arms are
Boussinesq models; the spread has no access to the anisotropy that
`BASELINES.md` §5 records as the dominant error on the ducts, where *"the
secondary flow a linear model cannot make"* is exactly the failure all four arms
share.

**The LES/DNS truth on these meshes is the only thing that turns the spread into a
validation** — and it is already on disk (`U_LES k_LES tauij_LES`, and `p_LES` on
CBFS and `PH_Breuer`), which is what makes the sweep worth doing. But that means
the *validation* content of this work is entirely in the comparison against
truth, and **not** in the spread itself. A record that reports the spread and
calls it uncertainty would be claiming something the work does not support.

**Further limits, named rather than implied:**
* **No grid dependence, and therefore no GCI, and therefore no Roache gating.**
  One mesh per case is shipped; the sweep produces a single grid level. Standing
  rule 5 does not even apply, because there is no triple. Any discretisation error
  in the shipped meshes is common to all arms and invisible to the spread.
* **No iterative-convergence claim is free.** Under a uniform iteration cap some
  arms will converge and some will be capped. A capped arm's contribution to the
  spread is contaminated by its convergence state, and the two are not separable
  after the fact. Every row must carry its own convergence state beside its value.
* **The SA arm's initial condition is a choice, not a datum** (§3.4). Its result
  is conditional on that choice, and a different registered `nuTilda` seed gives a
  different SA field.
* **The `kEpsilon` arm is a high-Re model on a wall-resolved mesh** (§3.3). Its
  near-wall answer is outside its calibration range by construction.
* **`NASA_2DWMH` is not the shipped configuration** in any arm, because its
  shipped model does not exist on this box (§2.3). Its rows are a different case
  from the one the benchmark's own baseline describes.
* **Nothing here bears on the de Zordo-Banliat *aggregation*.** This sweep would
  generate the aggregation's inputs. Whether a random forest can learn useful
  per-cell weights from them is a separate question with a separate gate.
* **Nothing here bears on unsteady, separated-transient or 3-D flows.** The clone
  has none (`BASELINES.md:317-318`).

### 7.3 What could legitimately be pre-registered — and what could not

**Could be:**
1. **A completion/harness gate.** "All 200 entries reach `endTime` or a registered
   convergence criterion, satisfy the strict completion rule including the age
   guard, and write `U p k nut` plus the arm's own field." Binary, decidable,
   and it is the gate this sweep most needs.
2. **A null-arm identity gate.** "The `kOmegaSST_null` arm reproduces each case's
   shipped converged field to a pre-registered tolerance in relative L2 on `U`."
   This is the sweep's planted control and its threshold must be fixed **before**
   staging, because it is the only check that can distinguish a staging bug from a
   closure effect. (An honest caveat: the null arm re-solves under a *changed*
   `controlDict` and a *changed* `residualControl`, so exact identity is not the
   right expectation — the tolerance must be set to the convergence level, not to
   machine epsilon.)
3. **A per-case error gate against truth**, in `BASELINES.md`'s own metric, with a
   band per arm fixed in advance — e.g. "`LaunderSharmaKE` `U_rms` on the eight
   held-out cases lies within X of the SST row". Legitimate because the truth
   exists on disk and the metric is already defined and already computed once.
4. **A spread-magnitude gate, stated as a spread and never as an uncertainty** —
   e.g. "the four-arm inter-model standard deviation of `U` exceeds Y % of bulk on
   at least Z of the 40 cases". This is a statement about model sensitivity and
   nothing more, and its wording must say so.

**Could NOT be:**
* **Any gate calling the inter-model spread a model-form *uncertainty*, or
  calibrating a confidence interval from it.** The arms are not independent
  (§7.2); a spread over correlated Boussinesq models is a lower bound of unknown
  tightness, and a gate that treats it as an interval would be asserting exactly
  what the work cannot see.
* **Any gate on grid convergence, GCI or observed order.** No triple exists.
* **Any ranking of the four models as "best" without truth.** With truth it is a
  measurement; without it, it is an opinion with a number attached.
* **Any gate on the de Zordo-Banliat aggregation's accuracy.** That needs the RF
  and its own pre-registration; this sweep would only produce its features.
* **Any gate whose threshold is chosen after the staging step has run.** Standing
  rule 2 — the freeze is the document's entire evidentiary content.

---

## 8. Open items a pre-registration would have to settle

1. The **uniform iteration cap** (§4.5) — without it the ducts alone are 2 778
   core-min per arm.
2. The **model-uniform convergence criterion**, replacing an `omega`-named
   `residualControl` that changes meaning across arms (§2.6).
3. The **`epsilon` wall BC** on the 11 cases that ship no `epsilon` (§3.3).
4. The **`nuTilda` initial condition** for the SA arm — value, and which of routes
   A/B/C (§3.4). This is the one item on the list with no defensible derivation
   from the shipped files.
5. The **`div(phi,nuTilda)` scheme** (§3.4).
6. Whether the **`kOmegaSST` null arm** is in scope (§4.4 argues it must be).
7. The **`NASA_2DWMH` model substitution** as a declared deviation (§2.3, §6.3).
8. Whether **cold start from `0/`** or **warm start from the shipped converged
   field** — a bias question, not a cost question (§3.4 route B).
9. The **`constant/C Cx Cy Cz V`** copy decision, uniform across all 200 entries
   (§6.3 item 4).

---

## 9. What this lane did not do, and could not verify

* **Nothing was run.** No solver, no `checkMesh`, no `blockMesh`, no staging. No
  queue entry was written. Nothing was committed; no git index was touched.
* **Cell counts are read from `constant/polyMesh/owner` header notes**,
  corroborated against the `points` list length on six cases. They are **not**
  from `checkMesh`, which would require running it.
* **y+ was not computed** on any case. §2.7's "wall-resolved" reading is inferred
  from boundary-condition types, not measured.
* **No parallel run of these cases exists on disk**, so §5's serial
  recommendation is reasoned, not measured.
* **Per-case memory was not measured**; the `memory_floor_gb` values suggested in
  §5.2 are estimates and must be labelled as such in any entry.
* **`LaunderSharmaKE`'s recommended `epsilon` wall BC was not established from
  source** (§3.3); it is left as an open item.
* **The 2.39–4.01 µs/cell-iteration envelope is measured only between 3 025 and
  21 000 cells.** The `AR_14_Ret_180` and `NASA_2DWMH` cost rows are outside it.
* **Iteration counts to convergence for the four substitute models are unknown.**
  Every cost figure here charges the cap. That is deliberately conservative and it
  is not a prediction of what the models will actually need.

**Verdict on the question asked: the sweep is CONSTRUCTIBLE and COSTABLE today**
— 40 cases, 5 arms, 200 entries, **58.8 core-h point / 71.5 core-h cap**,
serial, 1 rank per entry, staged to
`/home/ubuntu/closure-data/multimodel_sweep/<ARM>/<CASE_ID>` with `0.orig/` and
no `0/`. **It is not authorised, not pre-registered and not enqueued by this
memo**, and item 4 of §8 — the SA initial condition — must be settled in a
pre-registration before any of it is staged.

---

## 10. Provenance of the load-bearing numbers (added 2026-08-27, under the fleet stop-order on the shared scratchpad)

**This lane wrote nothing to the scratchpad at any point in this task.** The
shared-scratchpad overwrite hazard could not have touched these figures: there was
no scratch intermediate to overwrite. Every number in §1 and §4 was read from disk
inside the same invocation that reported it.

Under the stop-order's third rule — *a generated file is asserted on CONTENT, never
on a line count or a size* — the whole load-bearing set was **re-derived from
scratch in one shell invocation** after the memo was written, and matched:

| re-derived | method | result |
|---|---|---|
| case count | `find`-enumerated afresh; each hit required `0/` + `system/` + `constant/turbulenceProperties` | **40**, 0 structural failures |
| cell counts | `owner` header note, **cross-checked on all 40** against the integer length of that mesh's own `points` file | **0 mismatches**; total **641 652** |
| family subtotals | accumulated during the same enumeration | hills 452 400, ducts 101 026, NASA 51 626, CBFS 21 000, PH_Breuer 15 600 |
| `epsilon` census | re-enumerated, not read back from any list | **29** of 40 |
| `nuTilda` census | `find` re-run | **0** files |
| per-iteration rates | `ExecutionTime` line count and final value re-extracted from each `log.run` | 2.387 – 4.010 µs/cell-iteration, as §4.1 |
| serial claim | every `nProcs` line across all kaandorp logs, deduplicated | the only distinct value is `nProcs : 1` |
| the four quoted `RESULTS.md` rates | matched as **literal strings** (`0.010814 s/iteration`, `0.035079 s/iteration`, `0.069512 s/iteration`, `13 158.8`, `219.313`), not by line number | all present |
| `BASELINES.md` 40-case claim | literal-string match on `across **40 cases**` | present |
| `FEASIBILITY.md` 41-case error | literal-string match on `4 models x 41 cases` | present — the error reported in §1.1 is still in the file |
| cost totals | recomputed from the freshly enumerated 641 652, not from the earlier arithmetic | 42.5 / **58.8** / 71.5 core-h at the three rates |

Line-number citations elsewhere in this memo are convenience references. Where a
citation is load-bearing it is also matched on content, per the table above.
