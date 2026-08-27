# M2 — THE k-EPSILON FAMILY ON THE CLOSURE CHALLENGE BENCHMARK MESHES
## PRE-REGISTRATION — 2 arms x 39 cases = 78 runs

**Drafted 2026-08-27 by a closure drafting lane on the closure supervisor's
dispatch, and revised the same day by a second lane (§13).** At the moment each
lane finished, the run root `/home/ubuntu/closure-data/m2_kepsilon_family/` was
verified ABSENT (`ls` returned `No such file or directory`), so **0.000
core-minutes existed in this rung's tree** and `VERIFICATION_CHARTER.md` §2b
amendments were legal throughout the drafting — which is the authority for §13.
No solver, no `blockMesh` and no `checkMesh` was run by either lane, and nothing
was written into `verification/queue/closure/`.

**This document does not state its own freeze status, deliberately (L-354).** A
freeze changes a sha and never the prose that claims not to be frozen; a banner
that says `NOT FROZEN` is a lie the moment it is committed, and one such banner
here additionally made both queue entries unparseable as JSON. **The freeze
state is carried by two things that render themselves: whether this file has a
commit sha, and whether the queue entries' `prereg_commit` field still reads the
literal `PENDING_SUPERVISOR_FREEZE`** — which is the one string that must stay,
because it cannot pass a queue entry's COMMIT-EXISTS check and so nothing here
can launch by accident.

**The freeze is the supervisor's, personally.** `SUPERVISION_CHARTER.md` §3
check 4 may not be delegated; no lane performed it and no lane claims it.

**Written under Sanaa's FREEZE-AHEAD >= 3 directive**
(`etc/sessions/2026-08-27T1654Z_sanaa_standing_directives.md` §2). This is the
third of the three registrations closure owes, beside `G1_grid_triple` and
`M1_multimodel_sweep`.

**M2 exists because M1 cut these two arms.** `M1_multimodel_sweep`'s §2 cuts
`kEpsilon` and `LaunderSharmaKE` on the ground that *the epsilon wall boundary
condition is not established from source*, and the feasibility memo
`cases/RANS_LES_closure_models/_common/MULTIMODEL_SWEEP_FEASIBILITY_DRAFT.md`
(849 lines at HEAD, docket **D536**) records the same gap in its own words at
lines 283-286 and 303-308. **§2 of this document closes that gap from the
source and from a measurement, and §12 records what the closing does not
cover.** M1 and M2 share no run root, no staged tree and no grading path.

---

## 1. THE QUESTION

> **The Launder-Sharma low-Reynolds k-epsilon model transports a modified
> dissipation. Standard k-epsilon does not. On 39 wall-resolved benchmark meshes,
> does each model's near-wall dissipation come out where its own source code says
> it must — and how far apart do the two members of the k-epsilon family put the
> velocity field when everything except the closure is held identical?**

The rung's primary claim is **not** an accuracy claim against DNS. It is a claim
about the wall treatment, and it is a claim this lane can be wrong about: §2
derives two boundary conditions from OpenFOAM v2606 source, and §6 turns that
derivation into a gate that fails loudly if the derivation is wrong. That is the
whole point. A model sweep whose wall treatment was guessed produces numbers
nobody can defend; this rung either establishes the wall treatment or reports
that it could not.

### 1.1 Three things this rung does not claim

1. **It does not claim either arm is accurate.** There is no null arm here (M1
   owns the `kOmegaSST_null` calibration). Absolute agreement with the shipped
   `*_LES` reference fields is **REPORTED**, never gated — see §7.
2. **It does not claim a grid-converged answer.** One mesh per case. **Standing
   rule 5 does not apply to any row in this rung**: there is no grid triple, no
   refinement ratio, no observed order and **no GCI is computed or quoted
   anywhere**. A reader looking for Roache gating here will not find it, and its
   absence is by design, not by omission.
3. **It does not claim the two arms bracket the model-form uncertainty.** Two
   members of one family is a family, not a bracket.

---

## 2. THE WALL TREATMENT, SETTLED FROM SOURCE AND FROM A MEASUREMENT

This section is the evidentiary content of the rung. Everything is cited to
OpenFOAM v2606 source under
`/usr/lib/openfoam/openfoam2606/src/TurbulenceModels/turbulenceModels/` by
file and line, or to a number this lane measured from the shipped mesh and
shipped converged fields.

### 2.1 What each model reads, and what it actually transports

Both models `MUST_READ` a field named **`epsilon`**:

| model | file:line | IOobject name |
|---|---|---|
| `kEpsilon` | `RAS/kEpsilon/kEpsilon.C:219` | `epsilon` |
| `LaunderSharmaKE` | `RAS/LaunderSharmaKE/LaunderSharmaKE.C:188` | `epsilon` |

**The names are the same. The variables are not.** In `LaunderSharmaKE` the
turbulent-kinetic-energy sink is

```
LaunderSharmaKE.C:292      - fvm::Sp(alpha*rho*(epsilon_ + D)/k_, k_)
LaunderSharmaKE.C:254      volScalarField D(2.0*this->nu()*magSqr(fvc::grad(sqrt(k_))));
```

so the true dissipation is `eps_true = epsilon_ + D` with
`D = 2 nu |grad(sqrt(k))|^2`. The transported field is therefore the **modified
(isotropic) dissipation** written `epsilonTilda` in Launder & Sharma (1974) and
stored in OpenFOAM under the file name `epsilon`. In `kEpsilon` there is no `D`
term anywhere in the file and the sink is the bare `epsilon_/k_`
(`kEpsilon.C:392`); the transported field is the **true dissipation**.

**This is the whole of the wall-BC question**, and the feasibility memo did not
have it: the memo's §3.1 table records both models as reading `epsilon` and
stops there. Two files with the same name hold two different physical
quantities, and they take different wall boundary conditions for that reason
alone.

### 2.2 `LaunderSharmaKE`: the wall value of the transported field is exactly zero

`D` exists precisely so that the transported variable vanishes at the wall. At a
no-slip wall the exact near-wall limit of the true dissipation is
`eps_true -> 2 nu (d sqrt(k) / dy)^2`, which is `D` evaluated at the wall; hence
`epsilon_|wall = eps_true|wall - D|wall = 0`. **Zero is derived, not invented,
and it is the only value consistent with the model's own k-equation as written
at `LaunderSharmaKE.C:292`.**

Corroborating the low-Re reading, both damping functions are functions of the
turbulence Reynolds number `Rt = k^2/(nu*epsilon)` and are viscous-sublayer
constructs that do no work unless the sublayer is resolved:

```
LaunderSharmaKE.C:45   fMu = exp(-3.4/sqr(1 + sqr(k_)/(this->nu()*epsilon_)/50.0))
LaunderSharmaKE.C:54   f2  = 1 - 0.3*exp(-min(sqr(sqr(k_)/(this->nu()*epsilon_)), 50))
LaunderSharmaKE.C:61   nut_ = Cmu_*fMu()*sqr(k_)/epsilon_
```

**REGISTERED BC (`LaunderSharmaKE` arm), all wall patches, all 39 cases:**

```
type            fixedValue;
value           uniform 0;
```

**Numerical safety of the zero, checked in source and registered in advance.**
`bound(epsilon_, epsilonMin_)` (`LaunderSharmaKE.C:200`, `:281`) reduces over the
boundary field as well as the internal field — `min` on a `GeometricField` is
`UNARY_REDUCTION_FUNCTION_WITH_BOUNDARY`
(`OpenFOAM/fields/GeometricFields/GeometricField/GeometricFieldFunctions.C:468`)
— and raises the boundary to `epsilonMin_` at
`finiteVolume/cfdTools/general/bound/bound.C:59`. `epsilonMin_` defaults to
`SMALL` (`RAS/RASModel/RASModel.C:83-92`). So the constructor's `bound` call
lifts the wall value from `0` to `SMALL` **once**, after which `min` is no longer
below the bound and the call is inert; the divisions at `:45`, `:54` and `:61`
never see a zero denominator. **Registered prediction: exactly one `bounding
epsilon` line attributable to the wall zero, at construction, not one per
iteration.** If the log shows a `bounding epsilon` line on most iterations, that
is a finding about this reading and §6 gate G-D2 records it.

### 2.3 `kEpsilon`: no such transformation exists, so the treatment must come from the wall function — and the measurement selects its branch

Standard k-epsilon has no `D` term, so `epsilon|wall` is the true dissipation and
is **not** zero; it has no closed constant value. v2606 supplies the value in
`epsilonWallFunction`, which does not set a patch value at all but **fixes
epsilon in the wall-adjacent cells** by matrix manipulation:

```
epsilonWallFunctionFvPatchScalarField.C:593   matrix.setValues(patch().faceCells(), patchInternalField());
kEpsilon.C:358                                epsilon_.boundaryFieldRef().updateCoeffs();   // "Update epsilon and G at the wall"
kEpsilon.C:378                                epsEqn.ref().boundaryManipulate(epsilon_.boundaryFieldRef());
```

The value it fixes has two branches:

```
epsilonWallFunctionFvPatchScalarField.C:212-219   epsilonVis = 2*k_P*nu_w / y_P^2        (viscous sublayer)
epsilonWallFunctionFvPatchScalarField.C:222-229   epsilonLog = Cmu^0.75 * k_P^1.5/(kappa*y_P)   (inertial sublayer)
epsilonWallFunctionFvPatchScalarField.C:237       if (lowReCorrection_ && yPlus(facei) < yPlusLam) -> epsilonVis
epsilonWallFunctionFvPatchScalarField.C:333       G is added ONLY where (!lowReCorrection_ || yPlus > yPlusLam)
```

with the default blender `STEPWISE` (`:408`), `lowReCorrection` defaulting to
**`false`** (`:368`, `:409`), and the test quantity being the **k-based**

```
epsilonWallFunctionFvPatchScalarField.C:203-209   yPlus = Cmu^0.25 * y_P * sqrt(k_P) / nu_w
```

against `yPlusLam = calcYPlusLam(kappa=0.41, E=9.8) = 11.53`
(`wallFunctionCoefficients.C:61-64`).

`epsilonVis = 2 nu k / y^2` is the exact viscous-sublayer asymptote of the
dissipation. **It is OpenFOAM's own source-coded expression, not a value this
lane chose.** What this lane must choose is the flag `lowReCorrection`, and §2.4
shows the choice is settled by measurement rather than by any comparison with a
reference.

**REGISTERED BC (`kEpsilon` arm), all wall patches, all 39 cases:**

```
type            epsilonWallFunction;
lowReCorrection true;
value           uniform 1e-15;
```

(`value` is a placeholder that `updateCoeffs` overwrites every iteration;
`1e-15` is written so the file is never a source of a number.)

### 2.4 THE MEASUREMENT: these meshes are wall-resolved, and every wall face is below `yPlusLam`

The feasibility memo **inferred** wall-resolution from boundary-condition types
and said so honestly (`MULTIMODEL_SWEEP_FEASIBILITY_DRAFT.md:208-210`: *"I did
not compute y+; that reading is from the boundary-condition types, not from a
measurement."*). **This lane computed it**, with no compute: the cases ship cell
centres (`0/C`) and converged wall shear stress (`<ref>/wallShearStress`), so
`y_P`, `u_tau`, `y+` and the k-based `y*` follow from arithmetic on files
already on disk.

Method: `constant/polyMesh/{points,faces,owner,neighbour,boundary}` parsed
directly; face centres and areas by OpenFOAM's fan-triangulation algorithm; cell
centroids by OpenFOAM's pyramid decomposition; `y_P = |n_hat . (C_owner - C_f)|`.
Two independent estimators of `y+` were computed:

* **route 1**, from the shipped converged `wallShearStress`
  (dimensions `[0 2 -2 0 0 0 0]`, i.e. kinematic): `y+ = y_P sqrt(|tau_w|)/nu`;
* **route 2**, OpenFOAM's own wall-resolved expression
  `functionObjects/field/yPlus/yPlus.C:161-167`,
  `y+ = d sqrt(nuEff |snGrad(U)|)/nu`, with `nuEff = nu` because
  `nutLowReWallFunction::calcNut()` returns zero
  (`nutLowReWallFunctionFvPatchScalarField.C:38-42`).

**Instrument control.** The parser's cell centroids were checked against the
shipped `0/C` field on every case that ships one: **maximum absolute error
5.5e-14 m**, i.e. 2.4e-15 of the domain span. The two `y+` routes agree to a
median relative difference of ~1e-6.

| family | cases | `y+` median | `y+` max | k-based `y*` max |
|---|---|---|---|---|
| `CBFS13700` | 1 | 4.08 (lower) / 4.36 (upper) | **6.47** | 3.77 |
| `PH_Breuer` | 1 | 1.03 / 1.26 | 2.10 | 0.11 |
| `Parm_PH_29` hills (5 sampled, one per alpha family) | 29 | 0.41 – 0.75 | 1.33 | 0.032 |
| `DUCT` (all 8, both wall patches) | 8 | 0.057 – 0.097 | 0.11 | ~1e-4 |

**GLOBAL MAXIMUM k-based `y*` over every wall face probed on the shipped
CONVERGED fields: 3.77, against `yPlusLam = 11.53`.**

**And the census, on all 39, from the shipped INITIAL fields.** `stage_m2.py`
recomputes `y*` for every one of the 39 cases at staging time — from `0/k`,
which is the field the solver starts from and therefore the field that selects
the branch on iteration 1 — and **refuses any case whose maximum `y*` reaches
`yPlusLam`**. Measured over all 39, read-only, nothing written:

| | |
|---|---|
| worst case | `CBFS13700` |
| worst `y*` on the shipped IC, all 39 | **5.2016** |
| median over the 39 case maxima | 0.00295 |
| minimum | 0.001373 |
| cases at or above `yPlusLam = 11.53` | **NONE** |

The IC figure (5.20) is larger than the converged figure (3.77) because the
shipped `0/k` is a uniform guess, not a solution. **Both are below `yPlusLam`,
with a margin of 2.22x at the worst face of the worst case on the worse of the
two bases.** The branch is therefore selected on iteration 1 and on the answer,
and the check is a guard in the staging path rather than a claim in prose.

Three consequences, all registered before compute:

1. **`lowReCorrection true` is selected by the measurement, not by agreement
   with any reference.** Sanaa's §3 ANTI-GAMING clause is satisfied on its own
   terms: the alternative (`lowReCorrection false`, OpenFOAM's default) applies
   the **log-layer** expression `epsilonLog` at `y* = 0.0001 .. 3.77`, which is
   outside the log law by construction and is wrong for a reason that has
   nothing to do with what the answer comes out as.
2. **A conventional high-Re wall function is not available on these meshes at
   all.** `y+ <= 6.5` everywhere; a wall function wants the first cell at
   `y+ >~ 30`. This is a property of the shipped grids and is not negotiable by
   this rung.
3. **`CBFS13700` is the family's outlier and is flagged in advance.** At
   `y+ ~ 4.1` (max 6.5) its first cell sits in the buffer layer — resolved
   enough that a wall function is invalid, coarse enough that a low-Re model's
   damping functions are being asked to work on about a quarter of the sublayer
   resolution they were calibrated on. **`CBFS13700` rows in both arms carry the
   `NEAR-WALL-MARGINAL` chip** (§7.4). This is declared here, before the run,
   not discovered in the results.

### 2.5 The 29 hills' shipped `0/epsilon` is not evidence, and is overridden

The memo (`:284-285`) treats the 29 hills' shipped `0/epsilon` —
`epsilonWallFunction` with `value uniform 14.855` — as the one precedent
available. **Measured, it is not a precedent:**

* the hills run `kOmegaSST` (`constant/turbulenceProperties`), which
  `MUST_READ`s `k` and `omega` only. **The shipped `0/epsilon` is never read by
  the shipped solve.** It is an inert leftover, not a considered configuration.
* its `internalField` is `uniform 1.5e-12` — a placeholder, not a dissipation
  field;
* `14.855` is the **same number on all 29 hills**, which differ in geometry
  (`alpha` 0.5 to 1.5) and in Reynolds number;
* the boundary line is written `type epsilonWallFunction; // fixedValue;` — the
  author left the alternative commented out in the file.
* it carries no `lowReCorrection`, so it would take the **log-layer** branch at
  a measured `y* <= 0.032`.

**REGISTERED: `0/epsilon` is constructed identically on all 39 cases and the
hills' shipped file is overridden in the staged copy.** The alternative —
honouring the shipped file on 29 cases and constructing it on 10 — would make
the hills' wall treatment differ from every other case in the sweep and confound
the arm comparison with a staging difference. **The shipped file is recorded, not
silently dropped**: `stage_m2.py` writes the original's sha256, its
`internalField` and its wall entries into `staging_manifest.json` for every hill
before overwriting the staged copy. **The benchmark tree itself is never
written to** (§4.1).

### 2.6 The internal field: `epsilon = Cmu k omega`, and it is derivable on all 39

`epsilon = Cmu * k * omega`, `Cmu = 0.09`, is OpenFOAM's own definitional
relation inside the k-omega family, not a fit. It is applied cell-by-cell to the
case's own shipped `0/k` and `0/omega`, and face-by-face on every non-wall,
non-constraint patch that carries a value. On the 29 hills that already ship a
(placeholder) `0/epsilon`, the same construction is used, per §2.5.

`Cmu = 0.09` is the default in **both** models (`kEpsilon.H:36`,
`LaunderSharmaKE.H:55`), so the construction is arm-independent and the two arms
start from a byte-identical `0.orig/epsilon` internal field. Only the wall
entries differ, and that difference is the rung's subject.

---

## 3. THE ARMS, THE CASES, AND THE EXCLUSION

| arm id | `RASModel` | epsilon wall BC | source authority |
|---|---|---|---|
| `kEpsilon` | `kEpsilon` | `epsilonWallFunction; lowReCorrection true;` | §2.3, §2.4 |
| `LaunderSharmaKE` | `LaunderSharmaKE` | `fixedValue uniform 0` | §2.2 |

`twoLayerTreatment` is left at its **default `false`** on the `kEpsilon` arm.
v2606's `kEpsilon` does ship a two-layer wall treatment for low-Re grids
(`kEpsilon.H:26-29, :42-54`; `kEpsilon.C:48-72`; Jongen & Marx 1997), and it is
arguably the source-documented way to run standard k-epsilon on a mesh like
these. **It is a different model, and turning it on would be a third arm, not a
setting.** It is named here as an identified and deliberately untaken option so
that a later rung can take it without appearing to have discovered it after
seeing M2's numbers.

**`nut` is not touched on either arm.** `nutLowReWallFunction` returns zero at
the wall (`nutLowReWallFunctionFvPatchScalarField.C:38-42`), which is what both
arms need: the `LaunderSharmaKE` arm because it integrates to the wall, the
`kEpsilon` arm because `epsilonWallFunction`'s `lowReCorrection` branch adds no
production in the same cells (`:333`). **No `0/nut` file is written by staging.**

**Cases: the same 39 as M1.** `NASA_2DWMH` is excluded, for two reasons already
measured and recorded in the feasibility memo (`:162-164`): its
`constant/turbulenceProperties` names `AugmentedkOmegaSST`, which is not in
v2606 and whose library `libfrozenIncompressibleTurbulenceModels.so` is absent;
and its `0/nut` is the unexpanded `internalField uniform $nut;`. `NASA_2DWMH`
is **`BLOCKED`**, with that verdict recorded and not re-litigated here.

39 cases: `CBFS13700`, `PH_Breuer`, 29 `Parm_PH_29` hills, 8 `DUCT` cases.
**Total 590,026 cells**, measured from the `nCells:` note in each case's
`constant/polyMesh/owner`.

---

## 4. STAGING

### 4.1 The benchmark tree is read-only, and staging proves it

`/home/ubuntu/closure-challenge-benchmark/data/` is **never written**. Before
and after staging, `stage_m2.py` records a sha256 over every source file it
read and **refuses (`sys.exit(2)`) if any source sha changed**. The staged run
root is `/home/ubuntu/closure-data/m2_kepsilon_family/<arm>/<CASE_ID>/`.

### 4.2 `0.orig/` and NO `0/`

Staging writes initial fields to **`0.orig/`** and creates **no `0/`
directory**, because `AGE-GUARD` counts `0` as a numeric time directory
(`verification/runs/T-family/T5_runs/run_one_t5.sh:128-130`). `run_m2.sh` copies
`0.orig/` to `0/` as its **last** action before launching the solver, so `0/T`'s
analogue here — `0/k` — is the newest file in the case at launch and dates the
run allowed to produce the answer. A staged case that already contains `0/` or
any numeric time directory is **refused**, not cleaned.

### 4.3 The complete registered difference from the shipped case

Exactly five file classes change. Anything else differing is gate G-B failing.

| # | file | change | free parameters |
|---|---|---|---|
| 1 | `constant/turbulenceProperties` | `RASModel` -> the arm's model | 0 |
| 2 | `0.orig/epsilon` | written; internal `Cmu*k*omega`; wall entry per arm (§2.2/§2.3) | 0 |
| 3 | `system/fvSolution` `solvers` | `epsilon` block added **as a verbatim copy of that case's own `omega` block** | **0** |
| 4 | `system/fvSolution` `relaxationFactors` | `epsilon` entry added **equal to that case's own `omega` factor** | **0** |
| 5 | `system/fvSolution` `SIMPLE/residualControl` | `epsilon` entry **inserted** at that case's own `omega` tolerance; the `omega` entry is **left in place**, never deleted (standing rule 14's shape: insert with an assert, never replace) | **0** |
| 6 | `0.orig/epsilon`, the 8 `DUCT` cases only | the shipped `0/k` and `0/omega` carry `internalField uniform $kInlet;` and `uniform $omegaInlet;` — **unexpanded OpenFOAM dictionary variables** — defined in those same files as `kInlet 0.02;` and `omegaInlet 10.0;`. Staging **resolves the lookup** and records the token, its definition and the resolved value in `staging_manifest.json` for every affected case. A `$VAR` with no definition is a **refusal**, never a guess. | **0** |

**Every one of the six has zero free parameters.**

**Measured, and not anticipated by the feasibility memo:** the memo flags
`NASA_2DWMH`'s `0/nut` as *"the one case of 40"* carrying an unexpanded
variable. That is true of `nut`. It is **not** true of the class: **all 8 ducts**
ship `$kInlet` in `0/k` and `$omegaInlet` in `0/omega`, and their `0/U` carries a
`#calc` directive as well. Any staging that transcribed these fields as numbers
without resolving the lookup would have failed at the first case. Items 3-5 are mirrors of the
case's own omega channel; nothing in them was chosen, and nothing in them could
have been chosen differently to move an answer.

**`system/fvSchemes` is byte-identical. `system/controlDict` changes only
`endTime` (§5). `0.orig/{U,p,k,omega,nut}` and `constant/polyMesh/` are
byte-identical copies.**

### 4.4 Items 3 and 5 are fatal, not cosmetic — measured

Inventory of all 39 cases (measured by this lane, `system/fvSolution` and
`system/fvSchemes` parsed with comments stripped):

| group | n | ships `0/epsilon` | has `solvers{epsilon}` | has `relax{epsilon}` | `div(phi,epsilon)` | `residualControl` |
|---|---|---|---|---|---|---|
| `CBFS13700` | 1 | no | **yes** | **yes** | **ABSENT -> `default`** | `p 1e-15;` (unreachable) |
| `PH_Breuer` | 1 | no | **yes** | no | **ABSENT -> `default`** | `p 1e-15;` (unreachable) |
| `Parm_PH_29` hills | 29 | yes (inert, §2.5) | **no** | no | `Gauss upwind` | none (a bare `convergence 1e-8;` that `simpleControl` does not read) |
| `DUCT` | 8 | no | **no** | no | `$turbulence` = `bounded Gauss linearUpwind limited` | `k 5e-6; omega 1e-10;` |

* **Item 3 is fatal on 37 of 39.** `solve(epsEqn)` looks the field up in
  `fvSolution.solvers`; a missing entry is a `FatalIOError` at the first
  iteration, not a warning.
* **Item 5 reaches the 8 ducts only.** `CBFS13700` and `PH_Breuer` carry a
  `residualControl` of `p 1e-15;` with **no `omega` entry to mirror**, so
  nothing is inserted and their `residualControl` is left byte-unchanged; their
  `p 1e-15` is unreachable in practice and both run to `endTime`. The 29 hills
  have no `residualControl` at all — their `SIMPLE { convergence 1e-8; }` is not
  a key `simpleControl` reads — so they too run to `endTime`. **Item 5 is fatal
  to the meaning of the 8 ducts.** Verified in source:
  `simpleControl::criteriaSatisfied` (`simpleControl.C:59-88`) iterates over
  `mesh_.data().solverPerformanceDict()` — the fields **actually solved** — and
  checks only those with a matching `residualControl` entry. Under `kEpsilon`,
  `omega` is never solved, so the ducts' `omega 1e-10` entry is silently never
  consulted and **SIMPLE would declare convergence on `k` alone**, terminating
  early and writing a field that satisfies the completion rule and means
  nothing. The same source reading also proves the **leftover `omega` entry is
  inert and safe**, which is why it is inserted beside rather than replaced.

### 4.5 The measured scheme hazard, scoped and NOT fixed

`div(phi,epsilon)` is **absent on exactly 2 of 39** — `CBFS13700` and
`PH_Breuer` — where it falls through to `divSchemes { default Gauss linear; }`:
**unbounded central differencing on the dissipation equation**, while the
sibling scalar `k` in the same two files gets `(bounded) Gauss linearUpwind
grad(U)`. The other 37 ship it explicitly (`Gauss upwind` on the hills,
`bounded Gauss linearUpwind limited` on the ducts). This is narrower than the
dispatch anticipated and than the memo implies, and it is measured, not assumed.

**REGISTERED: `fvSchemes` is not edited.** The remedy, if it is needed, is a
separately pre-registered rung and nothing else:

> **M2R (registered here, before compute, and not run as part of M2).** If
> either arm on `CBFS13700` or `PH_Breuer` fails to converge, or bounds
> `epsilon` on more than 1% of iterations after the first 100, the **only**
> permitted follow-up is a new frozen registration whose single change is
> `div(phi,epsilon) := div(phi,k)` copied verbatim from the same case's own
> `fvSchemes`. **Not a parameter hunt, not a scheme search, and not a choice
> made by looking at which scheme agrees better with the reference** (Sanaa §3
> ANTI-GAMING). M2's own verdict for those two cases stands as recorded
> whatever M2R later shows.

Predicting the failure mode here, before compute, is what stops M2R from being a
post-hoc rescue.

### 4.6 `libs` lines are never removed

`alpha_15_10929_2024/system/controlDict:18` carries a `libs` line its 28
siblings do not. **Staging copies `controlDict` and edits only `endTime`; no
`libs` line is removed, reordered or tidied on any case** (standing rule 14).
`stage_m2.py` asserts that the staged `controlDict`'s `libs` lines are a
byte-identical multiset of the source's, and refuses otherwise.

### 4.7 Known v2606 incompatibilities in the shipped dictionaries

Measured and registered so that neither is read as a run failure: the hills'
`controlDict` carries `writeCompression uncompressed;`, which v2606 rejects with
`Unknown compression specifier 'uncompressed'`; and the shipped `.org` cases'
`#includeFunc` entries for `residuals` and `singleGraph_x0` do not resolve
against v2606's etc paths. **Grading therefore never depends on a function
object and parses the solver log instead.** `stage_m2.py` rewrites
`writeCompression uncompressed` to `off` and records the rewrite in the manifest
as a sixth, dictionary-syntax-only change (no numerical content).

---

## 5. THE ITERATION BUDGET

**`endTime = 20000` on all 39 cases and both arms, `deltaT 1`, steady
`simpleFoam`.** Basis, measured by this lane from the shipped reference time
directory names:

| | |
|---|---|
| shipped `kOmegaSST` runs that converged on their own `residualControl` | the 8 ducts, at **334, 405, 1109, 1540, 2428, 3636, 5125, 7009** iterations |
| slowest of those | **7,009** (`AR_14_Ret_180`) |
| shipped runs that never converged | `CBFS13700` (30,000, `p 1e-15` unreachable), `PH_Breuer` (10,000), the 29 hills (20,000, no `residualControl` read) |

20,000 is **2.85x** the slowest measured convergence of the shipped model on any
case in the sweep, and it makes every arm's budget identical so that no case's
result can be an artefact of a longer budget.

**Honest gap, registered:** *the convergence behaviour of `kEpsilon` and
`LaunderSharmaKE` on these meshes has never been measured on this box.* 20,000
is a budget transferred from a different model. **Hitting the cap is a recorded
outcome class (`CAP-REACHED`), not a failure and not a silent pass** — see §6
G-E and §7.4.

---

## 6. GATES, CONTROLS AND THRESHOLDS — FROZEN BEFORE ANY RUN

Ordering is strict: **G-A, then G-B, then G-C, then G-D, then G-E.** A gate can
only turn a row into `NOT A RESULT` or `BLOCKED`; it can never turn one into a
`PASS`.

### G-A — PLANTED-ZERO CONTROL (standing rule 3). Refuses, does not warn.

`grade_m2.py` copies one real `<endTime>/epsilon` file **to disk** in its own
scratch directory, writes `PLANT = 1.234e-03` into it **by line index**, re-reads
it **from disk** through the same reader every other number in the rung goes
through, and requires the planted value back to 1e-12 relative.

* **An in-memory plant does not satisfy this gate and is not used.** The file is
  written, closed, and re-opened.
* The gate also plants into a **wall patch entry** and into an **internal-field
  entry**, because the rung's primary gate reads both, and a reader that can see
  one and not the other would pass a single-site plant.
* On failure: `sys.exit(2)`. **Every row in the rung becomes `NOT A RESULT`**,
  because a reader not shown able to see a non-zero cannot certify a zero — and
  the `LaunderSharmaKE` arm's registered wall value *is* zero, which makes this
  rung one where a blind reader would produce a confident, wrong `PASS`.

### G-B — STAGING EQUIVALENCE. The staged tree differs only where §4.3 says.

For every case and arm, a sha256 manifest of the staged tree against the shipped
tree. The set of differing paths must equal the registered set exactly — no
extra file, no missing file. Any difference outside the set: that case-arm is
`NOT A RESULT`.

**Planted-failure proof (L-314), shipped with the check:** the selftest mutates
one byte of a staged file that is registered as identical, runs the control, and
**requires it to flip to failure**; then mutates the check itself to a no-op and
requires the selftest to notice. Both directions, or the selftest fails.

### G-C — STRICT COMPLETION + AGE GUARD (standing rule 4). All-or-nothing.

A run is done only if **all** hold:

1. `rc = 0`;
2. an `End` line in the log;
3. **last written time directory == `endTime`**, or the log carries
   `SIMPLE solution converged in N iterations` with the last time == `N`;
4. fields present at that time: **`U p k epsilon nut phi`**;
5. `ExecutionTime` line count consistent with the iteration count reached;
6. **every field at that time NEWER than the case's own `0/k`** — the age guard.

Failing any clause: the run is **not done**. The grader **refuses (exit 2)
rather than degrading** the row to a weaker claim.

**L-342, physics against infrastructure.** `rc`, the `STATUS` file, the
`ExecutionTime` count and the log's `End` line are **INFRASTRUCTURE**. A missing
or unreadable `STATUS`/`rc` record makes clause 1 **`NOT MEASURED`** and, per
Sanaa's 2026-08-27 §0 ruling R-RC, **only when the other four physics clauses
hold**; it can never void intact physics fields. The written fields, their
values and their timestamps are **PHYSICS**. The grader prints the two classes
in separate columns and never lets an infrastructure gap delete a physics row.
Clause 3's ExecutionTime-line count is INFRASTRUCTURE for the same reason
`VMFLGPU001` AMENDMENT 4 had to reclassify it.

### G-D — PRIMARY. The wall treatment must come out where §2 says it must.

This is the rung's own claim, and it is reference-free: it is checked against
**analytic expressions from the OpenFOAM source**, not against DNS.

**G-D1 — `kEpsilon` arm.** In every wall-adjacent cell of every wall patch, the
converged `epsilon` must equal `epsilonVis = 2 nu k_P / y_P^2`
(`epsilonWallFunctionFvPatchScalarField.C:212-219`), because
`manipulateMatrix` (`:593`) **fixes** it there by `setValues`.

* **Registered band: relative deviation <= 1e-6 on >= 99.9% of wall-adjacent
  cells, and <= 1e-3 on 100% of them.** `setValues` imposes the value exactly;
  the band allows only for ASCII write precision (`writePrecision 15`) and for
  `cornerWeights` at cells touching two wall patches.
* The grader additionally asserts, from the measured `y*` of the converged
  field, that **`y* < 11.53` on 100% of wall faces** — i.e. that the branch §2.4
  selected on the *shipped* field is still the branch selected on the *converged*
  one. If the converged solution pushes any face above `yPlusLam`, that case is
  `NOT A RESULT`, because the registered wall treatment was chosen on a premise
  the answer then violated.
* **Outside the band -> `GATE FAIL`, and the failure is a finding about §2.3,
  reported as such.**

**G-D2 — `LaunderSharmaKE` arm.** Two conditions:

* the wall patch value of `epsilon` is `0` or has been lifted to `epsilonMin`:
  **`|epsilon|wall| <= 1e-12` on 100% of wall faces**; and
* the near-wall balance is non-degenerate: the true dissipation
  `eps_true = epsilon + D` with `D = 2 nu |grad(sqrt(k))|^2` must be
  **strictly positive at the wall on >= 99% of wall faces**, i.e. `D|wall > 0`.
  A field where `D` is also zero at the wall is a dead solve wearing a correct
  boundary condition, and this is the clause that catches it.
* The grader also counts `bounding epsilon` lines in the log and reports them
  against §2.2's registered prediction of **one, at construction**. More than 1%
  of iterations: the row keeps its verdict but carries the chip
  `BOUNDING-EPSILON`, and §2.2's reading is recorded as **not confirmed**.

**Verdict mapping for G-D:** inside the band -> `PASS` for that case-arm's wall
claim; outside -> `GATE FAIL`; G-A/G-B/G-C unsatisfied -> `NOT A RESULT`
regardless of the number.

### G-E — ITERATIVE CONVERGENCE, per case-arm, reported not gated.

Recorded from the log for every run: final initial-residual per solved field;
whether `SIMPLE solution converged` appeared; iteration count reached; and
whether `endTime` was hit. A run that reaches `endTime` without converging is
labelled **`CAP-REACHED`** and its G-D verdict still stands (the wall treatment
is imposed every iteration, so it is testable on a capped field), but **every
§7 secondary from that run is `REPORTED` only** and enters no census (Sanaa
§0 ruling D534).

### 6.1 L-332 — no refusal is an `assert`

**No refusal in `grade_m2.py` or `stage_m2.py` is written as `assert`.** Every
one is an explicit `if ...: sys.exit(2)`. The selftest:

1. clears `__pycache__` (a stale one inverts mutation tests);
2. runs the full refusal battery under **`python3 -O`** and requires **every
   refusal still to fire**;
3. **parses its own AST** for `ast.Assert` nodes in both files and requires the
   count to be **zero**;
4. **proves the AST counter can count** by parsing a planted source string
   containing exactly two `assert` statements and requiring the counter to
   return 2. A counter never shown able to return non-zero is a planted zero of
   its own.

### 6.2 L-314 — every guard ships its planted-failure proof

For each of G-A, G-B, G-C and G-D the selftest mutates the guard to a no-op and
requires the corresponding control to **flip**. A guard whose mutation does not
flip the control is reported and the rung does not run.

---

## 7. FUNCTIONALS AND WHAT IS AND IS NOT GATED

### 7.1 PRIMARY — the wall-treatment claim of §6 G-D. Gated. Reference-free.

### 7.2 SECONDARY-A — arm separation. **REPORTED, not gated.**

Per case, the normalised L2 difference between the two arms' velocity fields,
volume-weighted:
`S = ||U_kEpsilon - U_LaunderSharmaKE||_V / ||U_LaunderSharmaKE||_V`, plus the
same for `k`. This is the sweep's actual output and it needs no reference data.
It is **REPORTED** because with no null arm in this rung the separation cannot
be attributed between model form and staging, and a number that cannot be
attributed is not gated. **D534 applies: `REPORTED` is a row class, not a
verdict, and these rows are excluded from every census.**

### 7.3 SECONDARY-B — distance from the shipped reference. **REPORTED, not gated.**

Per case, the same normalised L2 distance from each arm to the shipped `*_LES`
field where one is shipped. **Explicitly not a gate, and no band is registered
for it.** Gating accuracy here would be an accuracy verdict on an instrument
whose calibration lives in a different rung (M1's `kOmegaSST_null`, gate G2).
**M2's absolute readings become defensible only if and when M1's null arm has
passed**; that dependency is stated here rather than assumed.

### 7.4 Chips carried on rows, declared before the run

| chip | condition | declared in |
|---|---|---|
| `NEAR-WALL-MARGINAL` | `CBFS13700`, both arms — `y+ ~ 4.1`, max 6.5 | §2.4 |
| `HIGH-RE-MODEL-ON-RESOLVED-MESH` | every `kEpsilon` row | §7.5 |
| `CAP-REACHED` | reached `endTime` without `residualControl` | §6 G-E |
| `BOUNDING-EPSILON` | `bounding epsilon` on > 1% of iterations | §6 G-D2 |
| `SCHEME-FALLTHROUGH` | `CBFS13700`, `PH_Breuer` — `div(phi,epsilon)` on `default Gauss linear` | §4.5 |

### 7.5 THE DECLARED MODEL-FORM LIMITATION OF THE `kEpsilon` ARM

**Standard `kEpsilon` is a high-Reynolds-number model calibrated for use with
wall functions, and §2.4 measured these meshes at `y+ <= 6.5`. The `kEpsilon`
arm is therefore a model applied outside its own calibration range by
construction. It will run, and it will produce a number, and that number's
near-wall content is not defensible as physics.**

This is stated here, before compute, as a **known property of the arm** —
`VERIFICATION_CHARTER.md`'s bright line, and the difference between a declared
model-form limitation and a defect discovered in the results. It is also the
reason the family needs both arms: **`LaunderSharmaKE` is the arm that makes
this a k-epsilon family comparison rather than a straw man**, and any reading of
M2 that quotes the `kEpsilon` arm without this paragraph is a misreading.

Every `kEpsilon` row carries the chip `HIGH-RE-MODEL-ON-RESOLVED-MESH`.

---

## 8. COST. Measured basis, and the box cannot read its own billing.

**Rate.** `3.30e-06` s per cell-iteration, serial, **measured on this box**,
envelope `2.39e-06` to `4.01e-06`
(`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/RESULTS.md:393-396`).

**Work.** 590,026 cells (measured, §3) x 20,000 iterations x 2 arms
= **2.360104e10 cell-iterations**.

| basis | rate [s] | wall [s] @ ranks 1 | core-min |
|---|---|---|---|
| envelope low | 2.39e-06 | 56,406 | 940.1 |
| **measured point** | **3.30e-06** | **77,883** | **1,298.1** |
| envelope high | 4.01e-06 | 94,640 | 1,577.3 |

**REGISTERED ESTIMATE: `cost_core_min_estimate = 1298.1`** (per arm 649.0).
**REGISTERED CAP: `cap_core_min_registered = 2600.0`** (per arm 1300.0), which
is **2.00x** the estimate. The cap is a runaway guard, not a target, and the
2.00x is not the envelope: the envelope top alone is 1.215x, and the remaining
margin covers **work this lane could not measure** — `LaunderSharmaKE` evaluates
`fvc::magSqrGradGrad(U)` (`LaunderSharmaKE.C:253`) and `fvc::grad(sqrt(k_))`
(`:254`) every iteration, which `kOmegaSST` does not, and **no per-iteration
cost for either k-epsilon model has ever been measured on this box.** The rate
above is a k-omega-family rate transferred to a k-epsilon family.

**Overrun stops the run** (standing rule 12); it does not get a new budget.
`run_m2.sh` carries the same cap and prints `CAP AGREES <n>` at preflight so
that a launcher/grader disagreement is caught before compute rather than after.

**Per-case-arm caps**, `cells x 20000 x 3.30e-06 / 60 x 2`:

| case class | cells | estimate [core-min] | per-run cap [core-min] |
|---|---|---|---|
| `CBFS13700` | 21,000 | 23.10 | 46.20 |
| `PH_Breuer`, each hill | 15,600 | 17.16 | 34.32 |
| smallest duct `AR_1_Ret_180` | 2,209 | 2.43 | 4.86 |
| largest duct `AR_14_Ret_180` | 31,819 | 35.00 | 70.00 |

**Dollars are DERIVED, not measured.** At the owner-stated `$0.0513/core-h`
(`COMPUTE_BUDGET_CHARTER.md` §5: this box cannot read its own billing, so any
cost from it is **reported-by-owner, not measured**): estimate 21.635 core-h ->
**$1.11 derived**; cap 43.333 core-h -> **$2.22 derived**. Both are inside
`CLOSURE_MODELLING_CHARTER.md` §18's 487 core-h pre-authorisation and inside the
$25/run pre-authorisation, **and are costed here anyway** — a blanket is not a
per-item read (standing rule 9).

**Estimate-versus-actual calibration is owed at completion** (standing rule 12,
Sanaa 2026-08-23). `run_m2.sh` writes wall seconds and ranks per case-arm into
`STATUS`; `grade_m2.py` emits the actual/predicted ratio per case-arm and for
the rung, attributes the gap between contention, waste and misprediction with
**waste named separately and never absorbed into the ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6), and the row lands in `docs/COST_CALIBRATION.md`
under that file's append rules and the rule-10 private-index protocol. **A
completion report for M2 without that comparison is incomplete.**

**Ranks: 1.** Per-case-one-rank is embarrassingly parallel with no
communication; the smallest duct at 2,209 cells would be far below the
10^4–10^5 cells-per-rank range where domain decomposition pays, and the box is
already oversubscribed, so minimising per-case wall time by adding ranks would
reduce total throughput.

**`memory_floor_gb: 1.0` is an ALLOWANCE, not a measurement.** The largest case
is 31,819 cells; field arithmetic gives a few tens of MB of solution data.
**`simpleFoam`'s own footprint was not measured — this lane is forbidden to
launch a solver.** `run_m2.sh` captures real `MaxRSS` per case-arm via
`/usr/bin/time -v` into `mem_time.txt`, which turns this allowance into a
reading for the next registration.

---

## 9. HEADLINE METRICS (Sanaa §2)

Every M2 report carries: CPU %, GPU %, closure queue depth, and idle-minutes per
resource. M2 uses **no GPU**; its GPU % is 0 by construction and is reported as
such rather than omitted.

---

## 10. THE GRADING PATH IS FIXED AT THE FREEZE

`grade_m2.py` and `stage_m2.py` are frozen at the pre-registration commit. Before
grading, the runner hashes the on-disk files against the committed blobs and
**refuses if either differs** — `VERIFICATION_CHARTER.md` §2d and
`scripts/check_comparator_freeze.py`. A repair after first compute is legal only
under the §2d.1 four-condition exception, lands as a dated addendum, and cannot
alter a gate, threshold, cap or label.

---

## 11. FILES

| path | role |
|---|---|
| `cases/RANS_LES_closure_models/M2_kepsilon_family/PREREGISTRATION.md` | this document |
| `cases/RANS_LES_closure_models/M2_kepsilon_family/stage_m2.py` | staging; read-only against the benchmark tree |
| `cases/RANS_LES_closure_models/M2_kepsilon_family/run_m2.sh` | launcher; writes `STATUS` at exit |
| `cases/RANS_LES_closure_models/M2_kepsilon_family/grade_m2.py` | comparator; all gates; `--selftest` |
| `cases/RANS_LES_closure_models/M2_kepsilon_family/QUEUE_ENTRIES_DRAFT/` | two draft entries, `prereg_commit = PENDING_SUPERVISOR_FREEZE` |

---

## 12. WHAT IT CANNOT SEE

`CLOSURE_MODELLING_CHARTER.md` §16. Written before the run, and the items are
the ones that would most embarrass this rung if a reader found them first.

1. **The wall treatment is settled, but it is not unique.** §2.3 selects
   `epsilonWallFunction` with `lowReCorrection true` under the **default
   `STEPWISE` blender**. v2606 offers four other blenders — `BINOMIAL`,
   `MAX`, `EXPONENTIAL`, `TANH` (`epsilonWallFunctionFvPatchScalarField.C:253`,
   `:269`, `:281`, `:301`) — which blend the viscous and log expressions
   *without* consulting `lowReCorrection` and would give a different near-wall
   `epsilon`. **This rung does not measure how different.** The registered
   choice is defended as the default blender plus one flag whose branch the
   measurement fixes, not as the only defensible configuration.
2. **`twoLayerTreatment` is not run.** §3 names it and leaves it. If the
   `kEpsilon` arm behaves badly, this rung cannot say whether the two-layer
   treatment would have fixed it.
3. **No null arm.** M2 cannot separate model form from staging on its own
   evidence. §7.2 and §7.3 are `REPORTED` for exactly this reason, and §7.3
   states the dependency on M1's G2 explicitly.
4. **`y+` was sampled, not censused.** All 8 ducts and both `CBFS13700` walls
   and both `PH_Breuer` walls were computed; of the 29 hills, **5 were computed
   — one per `alpha` family** (`alpha_05`, `alpha_075`, `alpha_10`, `alpha_125`,
   `alpha_15`). The other 24 hills are asserted wall-resolved by family
   similarity and identical cell count (15,600), **not measured.**
   `stage_m2.py` computes `y*` on **all 39** at staging time and refuses any
   case whose maximum `y*` reaches `yPlusLam`, which converts this gap into a
   check rather than leaving it an assumption.
5. **The convergence budget is transferred, not measured.** 20,000 comes from
   `kOmegaSST` behaviour. Neither k-epsilon model's convergence rate on these
   meshes has ever been measured on this box (§5).
6. **The cost rate is transferred, not measured.** 3.30 us/cell-iteration is a
   k-omega-family measurement. `LaunderSharmaKE`'s extra second-derivative work
   is unquantified (§8).
7. **`epsilon = Cmu k omega` is a definitional conversion, not an equilibrium
   claim.** It is exact as a change of variable and carries no guarantee that the
   resulting field is a good initial condition for either model. A slow start or
   an early transient is a property of the IC, not of the closure, and this rung
   cannot separate the two.
8. **The 29 hills' overridden `0/epsilon` is recorded but its effect is not
   measured.** §2.5 argues the shipped file is inert. This rung does not run a
   hill with the shipped file to prove it.
9. **`NASA_2DWMH` is `BLOCKED`, so the sweep has no wall-mounted-hump case**,
   and no statement about hump flows can be read out of M2.
10. **`div(phi,epsilon)` falls to unbounded central differencing on 2 of 39
    cases and this rung does not fix it** (§4.5). If those two rows misbehave,
    M2 reports the misbehaviour; it does not diagnose it.
11. **Neither `y+` estimator measured the sublayer profile.** Both use the
    first cell only. Whether 10–15 cells sit below `y+ = 20` — the practical
    requirement for a low-Re model — was **not** computed, on any case.
12. **The staging path's own defects are the ones it found; there may be
    others it did not.** Writing this rung's checks surfaced three real faults
    in this lane's first drafts, each caught by a control rather than by
    reading: a planted-zero control that overwrote a list's **count** instead of
    a value (and so read back nothing); a dictionary search that matched a
    **commented-out** `epsilon` block in `CBFS13700`'s `fvSolution` and reported
    a `residualControl` entry that does not exist; and a field reader blind to
    OpenFOAM **quoted regex patch keys**, which every duct uses
    (`"(wallTop|wallSide)"`). All three are fixed and each now carries a
    planted-failure proof. **The honest reading is that a fourth of the same kind
    may remain**, and the controls, not this paragraph, are what would catch it.
13. **`D` in gate G-D2 is an ESTIMATE, not `fvc::grad`.** The grader forms
    `d(sqrt k)/dn` as a one-sided wall-normal difference
    `(sqrt(k_P) - sqrt(k_w))/y_P`. That is adequate for the registered test
    (*is `D` strictly positive?*) and is **not** adequate to quote a value of
    `D`, and the grader labels it `D_med_ESTIMATE` wherever it prints it.
14. **This lane did not run anything.** Every number above is from source, from
    shipped files, or from arithmetic on them. No solver, no `blockMesh`, no
    `checkMesh`, no staging, no queue entry.

---

## 13. AMENDMENTS BEFORE FIRST COMPUTE — 2026-08-27, second drafting lane

**Legality.** `VERIFICATION_CHARTER.md` §2b and standing rule 2: *before first
compute, amendments are legal and must state the condition and how it was
checked.* **The condition is that the registered run root
`/home/ubuntu/closure-data/m2_kepsilon_family/` does not exist.** How it was
checked: `ls -d` on that path returned `No such file or directory`, before and
after every action recorded below. **No solver, no `blockMesh`, no `checkMesh`
was run by this lane, and nothing was written into
`verification/queue/closure/`.** Staging WAS exercised, for verification only,
into a scratch directory outside the repository and outside the run root; that
tree was deleted after audit and the registered run root remains absent.

Each amendment below is a **correction of a transcription of OpenFOAM source or
of a shipped dictionary**. **No gate, no threshold, no cap and no label is
changed by any of them**, and none was selected by looking at any reference
datum (`NONCONVERGENCE_STANDARD.md` §2.3, absolute).

### AMENDMENT 1 — G-D1 predicted the wrong quantity on the 8 `DUCT` cases

**Defect.** §6 G-D1 and `grade_m2.py:gate_d1_kepsilon` predicted the
wall-adjacent `epsilon` as the bare per-face `epsilonVis = 2 nu k_P / y_P^2`.
The source does not store that. It **accumulates over every wall face a cell
owns, weighted by `cornerWeights = 1/(wall faces on that cell)`**:

```
epsilonWallFunctionFvPatchScalarField.C:110   ++weights[faceCell];
epsilonWallFunctionFvPatchScalarField.C:120   cornerWeights_[patchi] = 1.0/wf.patchInternalField();
epsilonWallFunctionFvPatchScalarField.C:240   epsilon0[faceCells[facei]] += cornerWeights[facei]*epsilonVis(facei);
```

and then fixes the accumulated **cell** value by `setValues` (`:593`). For a
cell owning one wall face the two agree exactly. For a cell owning two they do
not.

**Measured, on the shipped meshes, no solver.** Exactly **8 of the 39** cases
contain a cell owning two wall faces — **all 8 `DUCT` cases, one such cell
each**; `CBFS13700`, `PH_Breuer` and all 29 hills contain none. On the two
square ducts the two faces are symmetric and the deviation is **exactly 0**. On
the six non-square ducts the two faces' `y_P` differ by ~2.5 %, and the
deviation the old predictor would have reported is:

| case | wall faces | corner faces | rel. deviation | old `frac_loose` |
|---|---|---|---|---|
| `AR_1_Ret_180` | 94 | 2 | 0 | 1.000000 |
| `AR_1_Ret_360` | 110 | 2 | 0 | 1.000000 |
| `AR_3_Ret_180` | 188 | 2 | 1.836e-02 | 0.989362 |
| `AR_3_Ret_360` | 216 | 2 | 1.990e-02 | 0.990741 |
| `AR_5_Ret_180` | 282 | 2 | 2.207e-02 | 0.992908 |
| `AR_7_Ret_180` | 376 | 2 | 2.366e-02 | 0.994681 |
| `AR_10_Ret_180` | 517 | 2 | 2.486e-02 | 0.996132 |
| `AR_14_Ret_180` | 724 | 2 | 2.540e-02 | 0.997238 |

G-D1 requires `frac_loose >= 1.000`. **Six of the eight ducts would therefore
have returned `GATE FAIL` on both arms — 12 of the 78 rows — for a reason that
is arithmetic, not physics, and whatever the solver did.** §6 G-D1's own prose
already said the band existed to allow for `cornerWeights`; the band did not,
and the fix is to the transcription and not to the band.

**Amendment.** `gate_d1_kepsilon` now forms the prediction the way the source
does: `pred_cell = (sum over the cell's wall faces of epsilonVis) / (count)`,
compared per face against the cell it belongs to. **The bands `1e-6` on
`>= 99.9 %` and `1e-3` on `100 %` are UNCHANGED.** The gate reports
`n_wall_faces_on_corner_cells` and `cornerWeights_applied` so a reader can see
where the correction bit. It remains reference-free.

**Planted-failure proof (L-314), both directions, `python3 -O`:** a synthetic
corner cell owning two wall faces of unequal `y_P` — the cornerWeights-averaged
field is detected as correct (`frac_tight = 1.000`, corner faces = 2); the naive
per-face field flips the control to `frac_tight = frac_loose = 0.5`; and with no
corner cell present the correction is inert (`cornerWeights_applied = False`).

### AMENDMENT 2 — `endTime = 20000` was not a write time on `CBFS13700`

**Defect.** §5 registers `endTime = 20000` on all 39 and `stage_m2.py` rewrote
`endTime` alone. `writeControl timeStep` writes only where
`timeIndex % writeInterval == 0`. Measured on the shipped `system/controlDict`
of all 39:

| group | `writeInterval` | 20000 a write time? |
|---|---|---|
| 29 hills | `4000` | yes |
| `PH_Breuer` | `10000` | yes |
| 8 `DUCT` | `$endTime` — the dictionary variable, so it tracks the rewrite | yes |
| **`CBFS13700`** | **`30000`** | **NO** |

`CBFS13700` would have run its full 20,000 iterations on both arms and **written
no field at `endTime`**; §6 G-C's fields clause would then have scored it
`NOT A RESULT` on a run that did everything right, at a cost of **2 x 23.10 =
46.20 core-min of certain waste**, on the one case carrying both the
`NEAR-WALL-MARGINAL` and `SCHEME-FALLTHROUGH` chips. Corroboration from the
shipped tree: `CBFS/` holds time directories `0` and `30000` and nothing between.

**Amendment.** Staging now checks, per case, that the registered `endTime` is a
multiple of the shipped `writeInterval`, and where it is not, rewrites
`writeInterval` to **the registered `ENDTIME` itself** — **zero free
parameters**, the shipped value recorded in `staging_manifest.json`, and a
second check that **refuses (`sys.exit(2)`)** if any staged case still fails.
Measured over all 39 after the amendment: **rewritten on exactly one case,
`CBFS13700`, `30000 -> 20000`.** This is bookkeeping — it changes **what is
saved to disk**, never what is computed — and it is the seventh registered
staging change, listed here beside §4.3's six.

**Planted-failure proof (L-314), both directions, `python3 -O`:** the guard
fires on a `CBFS13700`-shaped `writeInterval 30000` against `endTime 20000`; is
quiet on `4000`, on `10000` and on `$endTime`; ignores a **commented-out**
`writeInterval`; and goes quiet again once the rewrite is applied.

### CORRECTION 1 — §4.7's `#includeFunc` reading was half right, and the half
that matters is now verified

§4.7 states that the shipped `#includeFunc` entries *"do not resolve against
v2606's etc paths"*. Measured: **every `#includeFunc` name used by the 39
resolves in the SHIPPED tree**, because `functionObjectList::findDict` searches
`<system>/<name>` **first** and each case ships its own
`system/{residuals,convergenceProbes,singleGraph_x0..x8}`. They fail in the
**STAGED** tree, because staging copies only
`system/{fvSchemes,fvSolution,controlDict}`. §4.7's conclusion stands and its
reason is now correct.

**The load-bearing fact, and it is verified in source:** an unresolvable
`#includeFunc` is **NOT fatal**. `functionObjectList::readFunctionObject` emits
`WarningInFunction << "Cannot find functionObject file " << funcName` and
`return false`. **All 39 cases carry `#includeFunc residuals`**, so had this
been fatal the whole rung would have died at iteration 0 on every case. It is a
warning, the solve continues, and §6's grading parses the solver log rather
than any function object — as §4.7 already required.

### WHAT THESE AMENDMENTS DO NOT REACH

They correct two transcriptions and one reason. They do not touch §2's wall-BC
derivation, §5's iteration budget, §6's gates, bands, thresholds or labels, §8's
estimate or cap, or §12's list of what this rung cannot see. **§12.12 said a
fourth fault of the same kind might remain and be caught by a control rather
than by reading. Two were; this paragraph is not a claim that there is no
fifth.**

### AMENDMENT 3 — the launcher could not have reached a solver

**Two defects at the queue-runner interface, both measured 2026-08-27, both
guaranteeing zero compute rather than wrong compute.**

**(a) No OpenFOAM environment.** `scripts/queue_runner.py:460-463` launches
`setsid nohup bash -c "cd '<cwd>' && <argv> ..."` and passes its own environment
through unchanged. Measured on the live daemon (pid 1120800): **`WM_PROJECT_DIR`
is not set and `openfoam` is not on its `PATH`.** The draft `run_m2.sh` sourced
nothing and refused if `simpleFoam` was missing, so it would have refused at
preflight on every launch.

The repair is G1's, and G1 paid for it: **under `set -u`, sourcing
`/usr/lib/openfoam/openfoam2606/etc/bashrc` is FATAL AND SILENT.** Its line 184
dereferences `$FOAM_MODULE_APPBIN $FOAM_MODULE_LIBBIN` unbound; under nounset in
a non-interactive shell the shell dies there, before any trap, any `echo` or any
`STATUS` write. G1's first launch died exactly this way at
**2026-08-27T17:28:58Z**.

**Reproduced by this lane, both directions, in a stripped environment:**

* the original shape — `set -u`, source, output to `/dev/null` — produced **no
  output at all and rc 127**, with the marker `echo` after the source never
  reached;
* the amended shape — nounset lifted for the source alone, restored immediately,
  diagnostics kept in `_logs/log.foamenv` — returned **rc 0** with `simpleFoam`
  resolved to
  `platforms/linux64GccDPInt32Opt/bin/simpleFoam`.

**Amendment.** `run_m2.sh` now sources the bashrc itself in that shape, records
`FOAMENV rc` as INFRASTRUCTURE (L-342 — the binding check is the `command -v`
test, never the source's rc), and **refuses if `simpleFoam` is still absent
afterwards**.

**(b) The declared `cwd` did not exist.** Both draft entries named
`cwd = /home/ubuntu/closure-data/m2_kepsilon_family` — the registered run root,
which §2b requires to be ABSENT until launch. The runner's inner command begins
`cd '<cwd>' &&`, so `cd` would fail, `&&` would short-circuit, the launcher
would never run and the only record would be `launcher_rc=1`. **Amendment: `cwd`
is the run root's existing PARENT `/home/ubuntu/closure-data`**; the run root is
passed as `argv[2]` and created by `run_m2.sh` with `mkdir -p`, so it stays
absent until launch. (G1's entry names an existing `cwd`; M2's did not.)

### VERIFIED, NOT AMENDED — three source readings this lane checked rather than trusted

1. **`epsilonWallFunction`'s constants.** `lowReCorrection` defaults to `false`
   (`:368`, `:409`), the blender defaults to `STEPWISE` (`:408`), the branch test
   is `lowReCorrection_ && yPlus(facei) < yPlusLam` (`:237`), and
   `yPlusLam(kappa=0.41, E=9.8)` evaluates to **11.5301**. §2.3 and §2.4 stand.
2. **`LaunderSharmaKE` transports a different variable from `kEpsilon`.**
   `LaunderSharmaKE.C:254` defines `D = 2 nu |grad sqrt(k)|^2` and `:292` makes
   the k-sink `(epsilon_ + D)/k_`; **`kEpsilon.C` contains no `D` term at all**
   (zero occurrences). §2.1 and §2.2 stand.
3. **A converged stop still writes.** `simpleControl::loop` calls
   `runTime.writeAndEnd()` on convergence, and `Time::writeAndEnd`
   (`TimeIO.C:600-606`) sets `stopAt_ = saWriteNow` and calls `writeNow()`,
   which writes **regardless of `writeInterval`**. §6 G-C's acceptance of a
   converged stop is therefore not a hole, and AMENDMENT 2's
   `writeInterval := endTime` cannot suppress an early-stop write.

Independently re-measured by this lane and **matching §2.4 and §3 exactly**:
the y* census over all 39 (**worst 5.2016 on `CBFS13700`, median 0.002949,
minimum 0.001373, none at or above 11.53**); the shipped `0/epsilon` census
(**29 of the 39 ship one, all of them `Parm_PH_29` hills, all 29 carrying the
identical `internalField uniform 1.5e-12` and the identical wall
`value uniform 14.855` across 29 different geometries and Reynolds numbers, with
`// fixedValue;` left commented beside the type** — §2.5's "not a precedent"
reading is confirmed on the disk); and `epsilon = Cmu k omega` reproduced on the
staged `0.orig/epsilon` to **max relative error 0.000e+00** on a hill, a duct and
`CBFS13700` (every shipped `0/k` and `0/omega` is uniform, so the conversion is
exact).

### CORRECTION 2 — §8's envelope LOW end is not in the record it cites

Standing rule 12: *a cost is never called measured unless a record backs it.*
§8 states the rate envelope as **`2.39e-06` to `4.01e-06`** s per cell-iteration,
citing `Kaandorp2020_TBRF/aposteriori/RESULTS.md:393-396`. **`2.39e-06` does not
appear anywhere in that file.** What the file supplies is six measured
`s/iteration` figures beside their cell counts, from which six per-cell-iteration
rates follow:

| row | cells | s/iteration | s per cell-iteration |
|---|---|---|---|
| `CBFS13700__NULL` | 21,000 | 0.06114 | **2.911e-06** (fastest in the record) |
| `CBFS13700__TRUTH/MEANB/ML` | 21,000 | 0.06951 | **3.310e-06** |
| `AR_1_Ret_360` stock | 3,025 | 0.010814 | 3.575e-06 |
| `AR_3_Ret_360` stock | 8,748 | 0.035079 | 4.010e-06 |
| `AR_1_Ret_360` injected | 3,025 | 0.012296 | 4.065e-06 |
| `AR_3_Ret_360__ML*` | 8,748 | 0.03989 | **4.560e-06** (slowest in the record) |

**The registered point rate 3.30e-06 is sound and is now better attributed**: it
is `CBFS13700`'s own measured 3.310e-06 — the largest and most representative
case in the cited record. **The registered estimate `1298.1` and the registered
cap `2600.0` are UNCHANGED.** Only the envelope's stated ends are corrected:

| basis | rate | core-min, both arms | vs the 1298.1 estimate |
|---|---|---|---|
| slowest in the record | 4.560e-06 | **1,793.6** | 1.382x |
| registered point | 3.300e-06 | 1,298.1 | 1.000x |
| fastest in the record | 2.911e-06 | 1,145.2 | 0.882x |

**The cap survives the correction with margin: 2600.0 is 1.45x the
slowest-in-record figure**, and the record's own `x1.137` injected-versus-stock
multiplier — the closest thing on this box to `LaunderSharmaKE`'s extra
`fvc::magSqrGradGrad(U)` and `fvc::grad(sqrt(k))` work — puts the point estimate
at 1,475.9 core-min, still inside the cap. **The honest reading is that the
registered estimate sits near the fast end of what the record supports and may
under-predict by up to ~38 %; the cap is what protects the rung, and an overrun
stops the run rather than buying more (standing rule 12).** §12's item 6 already
declared the rate transferred rather than measured for these models; this
correction narrows what "transferred" was transferred from.

---

## AMENDMENTS 4-6 — closure-supervisor rulings, 2026-08-27, before first compute

Same legality and same condition as §13: `/home/ubuntu/closure-data/m2_kepsilon_family/`
verified ABSENT before and after. These three are the **supervisor's** rulings,
not a lane's findings, and they were issued after he read `grade_m2.py:169-170`,
`grade_g1.py:502-505` (frozen at `03be2015`) and `stage_m1.py:255`/`:484`
(frozen at `7b00b3ec`) as diffs rather than taking a lane's account of them.

### AMENDMENT 4 (RULING 1) — `ExecutionTime` is a hard equality, in `phys`

**What was wrong.** The draft graded the `ExecutionTime` count as
`'ok' if nexec >= float(last) * 0.5` — **a 50 % tolerance on a clause standing
rule 4 states as an equality**, assigned into the `phys` dict. The drafting
lane's own report described this as "classified INFRASTRUCTURE and reported, not
gating"; **the code did no such thing**, and the report and the instrument
disagreed about which had been built. It was caught by the supervisor reading
the lines.

**A band chosen before this lab had ever seen the count is a band chosen to
avoid an outcome not yet met.** M2 adopts G1's frozen shape: equality against
the registered `endTime`, in `phys`, **gating**, carrying G1's note verbatim in
spirit — *if the cause is a solver that prints extra lines, it is triaged by the
supervisor, never reclassified here.* `completion_ok` now requires it, and P7 is
assigned on **every** path, including the no-time-directory path where the draft
returned before setting it.

**Planted-failure proof, both directions, `python3 -O`:** one line short of
`endTime` fails; **one line over also fails** (it is an equality, not a `>=`);
a real case with 3 `ExecutionTime` lines against `endTime = 20000` is not `ok`;
and an AST-scoped detector confirms the `0.5` band is gone from the **grading
path**, with the detector itself proven able to fire on planted source. (That
detector had to be scoped: its first form matched its own literal and reported a
false FAIL — the same self-matching trap this file's GCI detector already paid
for.)

### AMENDMENT 5 (RULING 2) — `residualControl` is EMPTIED; M2 runs to `endTime`

**This supersedes §4.3 item 5 and the operative half of §4.4.** M1 is frozen at
`7b00b3ec`; `stage_m1.py:255` empties every `residualControl` sub-dictionary and
`:484` **refuses** if a staged `fvSolution` still carries a non-empty one. **M1
and M2 cover the same eight `DUCT` cases.** Two rungs in one family taking
opposite readings of one standing rule on the same cases is indefensible, and it
would be closure's fault, not the rule's. **Relaxing standing rule 4 is reserved
to Sanaa; a supervisor who softens a clause because a rung is inconvenient has
retired a standard.** The compliant path exists, M1 walked it, and it costs only
compute.

**Registered.** `stage_m2.py` empties every `residualControl` block, records the
shipped bodies in `staging_manifest.json` first, and **refuses (`sys.exit(2)`)**
if any staged `fvSolution` still carries a non-empty one. `grade_m2.py` drops
the converged-stop alternative: `last time == endTime` is the literal test, and
a `SIMPLE solution converged` line is now recorded as
**`early_stop_FINDING`** — evidence the emptying failed — and fails completion.
It is a finding, never an excuse.

**VERIFIED AND SUPERSEDED, retained because they are why this ruling is safe.**
§4.4's source reading — `simpleControl::criteriaSatisfied` (`simpleControl.C:59-88`)
iterates only the fields actually solved, so under `kEpsilon` the ducts' `omega`
entry is never consulted and SIMPLE would have declared convergence on `k`
alone — is **correct, and moot**: with no criterion there is nothing to be
incomplete. §13's `Time::writeAndEnd` reading (`TimeIO.C:600-606`) is likewise
correct and moot: with no early stop there is no early write to protect.
Neither is deleted; both are the evidence that emptying loses nothing.

**A defect this ruling's own control caught.** The emptier was first written in
M1's exact shape, which **returns as soon as it meets an already-empty block**.
M1's cases carry one `residualControl` each so it never bit there; M2's control
plants a file with two blocks and it failed immediately. The emptier now steps
past an empty block and scans on. **It was caught by a control, not by reading**,
and M1's line is worth a look for the same reason.

### AMENDMENT 6 (RULING 3) — the `NOT FROZEN` banners are removed (L-354)

L-354: **a freeze changes a sha and never the prose that says "NOT FROZEN"**,
measured three times in closure territory on 2026-08-27. This document's banner
was the fourth instance and the worst, because the identical banner on both
queue entries made them **unparseable as JSON** — the validator could never have
read either entry at all. **Six instances were found on disk**, not the two the
ruling named: this file, `run_m2.sh` (where it displaced the shebang to line 2),
`grade_m2.py`, `stage_m2.py` and both `.json` entries. **All six are removed**,
and both entries now parse natively. The present-tense `NOT FROZEN. NOT
COMMITTED. NOT ENQUEUED.` prose in this document's own opening is replaced by a
dated statement of what each lane did, plus the rule that **freeze state is
carried by things that render themselves** — this file's commit sha, and the
queue entries' `prereg_commit`. `PENDING_SUPERVISOR_FREEZE` **stays**: it is the
one string that must, because it cannot pass a COMMIT-EXISTS check.

### THE COST AFTER RULING 2 — waste named separately, never absorbed

**The registered estimate does not move.** §8 already charged every one of the
39 the full 20,000 iterations on both arms, so `cost_core_min_estimate = 1298.1`
and `cap_core_min_registered = 2600.0` are **unchanged**. What changes is that
the ducts' unproductive iterations are now **certain** rather than avoided, so
they are named.

**Named waste: 173.6 core-min, 13.4 % of the rung estimate** — the eight ducts
run past the iteration at which the shipped `kOmegaSST` solve met its own
`residualControl`, priced at the registered 3.30e-06 s/cell-iteration across
both arms. Per case, from each duct's shipped time directory:

| duct | cells | shipped convergence | waste [core-min] | unproductive |
|---|---|---|---|---|
| `AR_1_Ret_180` | 2,209 | 334 | 4.78 | 98.3 % |
| `AR_1_Ret_360` | 3,025 | 405 | 6.52 | 98.0 % |
| `AR_3_Ret_180` | 6,627 | 1,109 | 13.77 | 94.5 % |
| `AR_3_Ret_360` | 8,748 | 1,540 | 17.76 | 92.3 % |
| `AR_5_Ret_180` | 11,045 | 2,428 | 21.35 | 87.9 % |
| `AR_7_Ret_180` | 15,463 | 3,636 | 27.83 | 81.8 % |
| `AR_10_Ret_180` | 22,090 | 5,125 | 36.14 | 74.4 % |
| `AR_14_Ret_180` | 31,819 | 7,009 | 45.47 | 65.0 % |
| **total** | | | **173.6** | |

`COMPUTE_BUDGET_CHARTER.md` §6: **this figure is reported beside the
actual/predicted ratio and is never folded into it.** `grade_m2.py`'s cost row
carries it under its own key. As dollars, **DERIVED and reported-by-owner, not
measured**: $0.15 of the rung's $1.11.

**Two honest caveats.** The convergence iterations are `kOmegaSST`'s, not
k-epsilon's, so the true waste is unknown and this is the best available
estimate — it is *not* a measurement, and §12.5 already declared the budget
transferred. And it is not pure waste: it is what standing rule 4 costs when it
is honoured rather than softened, which is the trade the ruling makes knowingly.

**The cap holds with margin.** 2600.0 is **2.00x** the estimate and **1.45x**
the 1,793.7 core-min the slowest rate in the cited record would produce (whose
own named duct waste would be 239.9 core-min). **No trimming of the cap was
needed and none was done.**
