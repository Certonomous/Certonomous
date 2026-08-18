# Ladder A5 — U-bend internal-flow adjoint, pressure-loss objective

Date: 2026-07-28 (host time, AWS Linux, 16 vCPU / 32 GiB RAM instance)

## Case selection and adaptation (mandatory disclosure)

The brief pointed at `/home/ubuntu/dafoam-tutorials/UBend_CHT/` and instructed: inspect it,
and if it's CHT-only, look for an aero/pressure-loss variant, or adapt it, and say so explicitly.

`UBend_CHT` **is** CHT-only: its `runScript.py` builds a coupled `ScenarioAeroThermal` with a
`MeldThermalBuilder` (funtofem) joining a `DASimpleFoam` fluid domain to a `DAHeatTransferFoam`
solid domain, and its objective is `scalePL*(TP1-TP2) + scaleTM*Tmean` — pressure loss AND mean
outlet temperature, coupled. Its mesh also isn't generated locally: `preProcessing.sh` downloads
a prebuilt `CHT_ubend_mesh.zip` from a GitHub release. Standing this up correctly (funtofem +
MELD thermal coupling + two solvers + a download dependency) is real extra machinery this rung
does not need.

The tutorials repo ships a second, purpose-built case for exactly this situation:
`/home/ubuntu/dafoam-tutorials/UBend_Channel/` (commit `d3b7e38` in the tutorials repo, dated
2026-05-16). It is single-discipline (`ScenarioAerodynamic`, `DASimpleFoam` only, no thermal
solid domain, no funtofem), meshed locally with `blockMesh` (no download), and its stock
objective is already `scalePL*(TP1-TP2) + scaleHFX*HFX` — a weighted blend of pressure loss and
wall heat flux. **I used `UBend_Channel` as the aero/pressure-loss variant called for in the
brief, and adapted its objective to pure pressure loss** by replacing the weighted-sum `OBJ`
`ExecComp` (`val = scalePL*(TP1-TP2) + scaleHFX*HFX`) with `val = TP1 - TP2` and dropping the
`OBJ.HFX` connection (the `HFX` function is still computed by the solver — it's just no longer
part of the objective or adjoint). This is a one-line-of-substance change; everything else —
mesh (`blockMeshDict`), BCs (`0.orig/*`), solver options, FFD (`UBendDuctFFDSym.xyz`), and DV
setup — is byte-identical to the official tutorial. Working copy:
`demo-output/website/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/` (copied from the
tutorials repo, not a mutation of it). Solver `DASimpleFoam` (steady incompressible SIMPLE,
Spalart-Allmaras, RAS with wall functions). 4 MPI ranks throughout (matches the case's own
`decomposeParDict numberOfSubdomains 4`, within the 4-rank cap).

Docker: `dafoam/opt-packages:latest`, `--network=host --memory=10g`. Container OpenFOAM is
`v2506`; the case's `FoamFile` headers say `v1812` (an IOWarning about `convertToMeters` vs
`scale` fired during `blockMesh`, harmless) — noted because it plausibly explains part of the
baseline deviation reported below.

## Config hash

sha256 of the concatenation `runScript.py + system/fvSolution + system/fvSchemes`, taken from
the case as actually run (post-adaptation, before any run generated additional files):

```
36bd8442e7a1e3737d6b9e2567e0bfdb676631fb1f23938558b9a078b8b468b7
```

## Mesh

Generated in-container via `preProcessing.sh` (`blockMesh` + `renumberMesh`, both local, no
download). Measured from `log.meshGeneration`:

```
nPoints: 5967
nCells: 4800
nFaces: 15496
nInternalFaces: 13304
```

Patches: `inlet` (96 faces), `outlet` (96 faces), `ubend` (wall), `ubendup` (wall), `sym`
(symmetry plane — this is a half-model).

## Stage wall-time and core-minutes (measured, not estimated)

| stage | ranks | wall time | core-minutes | result |
|---|---|---|---|---|
| mesh preprocessing (`preProcessing.sh`) | 1 (serial) | ~1 s (00:52:00Z→00:52:01Z) | 0.02 | OK, 4800 cells |
| `compute_totals` (primal + adjoint + total derivs, all 6 DV groups) | 4 | 54 s (00:52:13Z→00:53:07Z) | 3.6 | OK |
| `check_totals` run1 (FD verify, of=OBJ.val wrt=shapexUpper, 27 comps, central, step=1e-4 abs) | 4 | 227 s (00:54:44Z→00:58:31Z) | 15.13 | OK (ran clean — no stale-`processorN` crash, see lesson) |
| diagnostic: `probe_driver.sh` nested-script attempt | 4 | ~1 s (00:59:32Z→00:59:33Z) | 0.07 | **FAILED — see lesson** |
| diagnostic: manual FD probe, idx0, +1e-4/+1e-3/+1e-2 & base | 4 | 68 s (00:59:45Z→01:00:53Z) | 4.53 | partial OK (negative-delta legs failed, see lesson) |
| diagnostic: manual FD probe, idx0, −1e-4/−1e-3/−1e-2 (retry) | 4 | 39 s (01:01:07Z→01:01:46Z) | 2.6 | OK |
| **total** | | **~390 s (~6.5 min)** | **~25.95 core-min** | |

## Primal convergence (from `compute_totals_run1.log`)

SIMPLE ran the full fixed `endTime = 1000` (no `residualControl` block in this case's
`fvSolution`; `SIMPLE: no convergence criteria found. Calculations will run for 1000 steps.` is
printed by OpenFOAM itself, unmodified from the official tutorial). Objective trajectory:

```
Time = 1     TP1: 2869.524210823638   TP2: 9.245003703993847
Time = 100   TP1: 87.96005291968729   TP2: 35.76444728119155
Time = 200   TP1: 88.12054694259008   TP2: 35.77317367564675
Time = 400   TP1: 88.11849246103276   TP2: 35.77314575494255
Time = 600   TP1: 88.11838177212337   TP2: 35.77316531829783
Time = 800   TP1: 88.11838265242606   TP2: 35.77316633668674
Time = 900   TP1: 88.11838266580405   TP2: 35.77316632783899
Time = 1000  TP1: 88.11838267130871   TP2: 35.7731663319629
```

TP1/TP2 are stable to 7-8 significant digits from iteration ~600 onward — the objective itself
has clearly converged. The *field* residuals (OpenFOAM's own per-equation `initRes`/`finalRes`,
and DAFoam's un-normalized `Printing Primal Residual Statistics` diagnostic) tell a more honest
story: they reach a **flat numerical fixed point**, not a monotone descent to
`primalMinResTol = 1e-8`:

```
p initRes (Time=900):  0.0002257624939542488   finalRes: 1.31146789379517e-05
p initRes (Time=1000): 0.0002257624979593885   finalRes: 1.311467703738508e-05
```

`p`'s `initRes` is unchanged to 10 significant figures between iterations 900 and 1000 — the
SIMPLE loop has reached a genuine fixed point of this case's default relaxation factors
(`p`: 0.30, `U`/`T`/`nuTilda`: 0.70, unmodified from the tutorial), not a stall that more
iterations would fix. This kind of small non-vanishing residual floor is a known characteristic
of steady RANS on U-bend/duct geometries with secondary (Dean-vortex) flow — not something this
rung introduced.

DAFoam's own field-residual-norm diagnostic (`Printing Primal Residual Statistics`, printed once
at the end of the primal, un-normalized, used internally for the adjoint RHS) at Time=1000:

```
U Residual Norm2: (25.549 24.010 10.625)
p Residual Norm2: 8.616
T Residual Norm2: 41.160
nuTilda Residual Norm2: 0.652
phi Residual Norm2: 0.065
Total Residual Norm2: 55.776
```

**Converged pressure-loss objective: TP1 − TP2 = 88.11838267130871 − 35.7731663319629 =
52.34521633934581** (kinematic pressure units, m²/s², i.e. `p/ρ` per OpenFOAM incompressible
convention). Reproduced bit-identically (`5.234521633934580e+01`) by the independent `-task
probe` baseline run (`probe_all_run1.log`), a cold-start-from-`0/` reproducibility check.

## Adjoint

GMRES/PETSc solved for both `TP1` and `TP2` adjoints in a single combined linear solve (shared
`d[R]/d[W]` system): **86 total iterations, `PetscConvergedReason: 2`** (converged), reaching
KSP residual norm `1.08e-4` from an initial `1.24e+01`. Total derivatives were computed for the
objective against all 6 design-variable groups (`shapexUpper/y/z`, `shapexLower/y/z`, 27
components each, 162 total). Full total-derivative dictionary is in
`compute_totals_run1.log`; `shapexUpper` (the group used for FD verification below):

```
d(OBJ.val)/d(shapexUpper) = [ 0.23711358, -0.43555559, -0.41765751,  1.96883727, -0.10505221,
                              -1.3953011 ,  1.61077383,  0.90578111, -0.84337258,  7.81935558,
                               4.80044882,  3.90871135, -4.43512493, -0.91203487,  0.55598334,
                             -13.86041673, -3.77483865, -0.62881205, -4.33825856, -0.94864214,
                               1.90894278, -1.78264732, -1.17260622, -2.25173312, -0.96908608,
                               0.74690602, -1.95653977]
```

## FD verification

`check_totals` known-trap check (per Ladder A1's finding): `processor0-3/` were present after
`compute_totals` (root-owned, container writes). `sudo rm -rf processor*` before `check_totals` —
this run had **no** `already exists, moving failed` crash; it completed clean on the first try.

`of=["OBJ.val"], wrt=["shapexUpper"]` (ONE total-derivative group, 27 shape components), central
FD, `step=1e-4`, `step_calc="abs"` — OpenMDAO's own summary:

```
Analytic Magnitude: 1.938364e+01
      Fd Magnitude: 3.340851e+01
Absolute Error (Jan - Jfd): 1.558097e+01  *
Relative Error (Jan - Jfd)/Jfd: 4.663773e-01  *   <- 46.6%, OpenMDAO flags this
```

Per-component breakdown (analytic vs. FD, relative error, sign):

| idx | analytic | FD (step=1e-4) | rel. err % | sign match |
|---|---|---|---|---|
| 0 | 0.23711 | 0.11014 | 115.3 | yes |
| 1 | -0.43556 | -0.46795 | 6.9 | yes |
| 2 | -0.41766 | -0.41319 | 1.1 | yes |
| 3 | 1.96884 | 0.70507 | 179.2 | yes |
| 4 | -0.10505 | -0.43988 | 76.1 | yes |
| 5 | -1.39530 | -1.21264 | 15.1 | yes |
| 6 | 1.61077 | 1.36334 | 18.1 | yes |
| 7 | 0.90578 | 1.32814 | 31.8 | yes |
| 8 | -0.84337 | 0.78391 | 207.6 | **NO (sign flip)** |
| 9 | 7.81936 | 11.56848 | 32.4 | yes |
| 10 | 4.80045 | 7.26987 | 34.0 | yes |
| 11 | 3.90871 | 8.17581 | 52.2 | yes |
| 12 | -4.43512 | -10.30518 | 57.0 | yes |
| 13 | -0.91203 | -1.25570 | 27.4 | yes |
| 14 | 0.55598 | 4.64655 | 88.0 | yes |
| 15 | -13.86042 | -24.27272 | 42.9 | yes |
| 16 | -3.77484 | -4.30296 | 12.3 | yes |
| 17 | -0.62881 | 2.90530 | 121.6 | **NO (sign flip)** |
| 18 | -4.33826 | -8.32702 | 47.9 | yes |
| 19 | -0.94864 | -0.35517 | 167.1 | yes |
| 20 | 1.90894 | 4.82274 | 60.4 | yes |
| 21 | -1.78265 | -3.07833 | 42.1 | yes |
| 22 | -1.17261 | -0.94309 | 24.3 | yes |
| 23 | -2.25173 | -1.37502 | 63.8 | yes |
| 24 | -0.96909 | -1.05939 | 8.5 | yes |
| 25 | 0.74691 | 0.76429 | 2.3 | yes |
| 26 | -1.95654 | -1.90572 | 2.7 | yes |

**5 of 27 components (idx 1, 2, 16, 24, 25) fall within the ≤12% band this lab calibrated on
the official unmodified NACA0012 shape-derivative case (Ladder A1). 22 of 27 do not, and 2
(idx 8, 17) flip sign entirely.**

### Step-size diagnostic (idx 0, manual `-task probe`, single-component central FD)

To find out whether this is ordinary small-step FD noise (which A1's NACA0012 case exhibited,
1-12%) that would shrink with a bigger step, I ran component 0 (`shapexUpper[0]`) at three step
sizes:

| step | OBJ(+step) | OBJ(-step) | central FD | analytic | rel. err % |
|---|---|---|---|---|---|
| 1e-4 | 52.34524387027182 | 52.34522044921939 | 0.1171 | 0.23711 | 50.6 |
| 1e-3 | 52.34534755468928 | 52.34509948237295 | 0.1240 | 0.23711 | 47.7 |
| 1e-2 | 52.34656274087725 | 52.34534566614248 | 0.0609 | 0.23711 | 74.3 |

The FD estimate does **not** monotonically converge toward the adjoint value as the step grows
from 1e-4 to 1e-2 (0.117 → 0.124 → 0.061) — it stays in the same wrong neighborhood, then moves
further away. That rules out "just too small a step, dominated by primal-residual noise" as the
*sole* explanation (a pure noise floor would show FD converging toward the true value as step
increases, before turning over into truncation error at even larger steps). Two candidate causes,
neither conclusively isolated within this rung's scope:

1. **Primal residual floor is the same order as the signal.** `p`'s field-residual plateau
   (`initRes` ≈ 2.26e-4, `T` residual norm 41.2) is comparable to or larger than several of the
   `OBJ.val` perturbation deltas being differenced (as small as ~2.3e-5 at step 1e-4) — a
   textbook setup for FD noise to dominate at small steps.
2. **Coarse mesh (4800 cells) / non-smooth mesh-warp response.** This is a 6-block structured
   mesh at fairly low resolution; a shape move at a single FFD control point near a block
   junction can plausibly produce a locally non-smooth volume-mesh deformation that a
   single global FD step size can't cleanly resolve, while the adjoint's linearization is exact
   about the (converged-enough) baseline state regardless.

I did not chase this further (root-causing which of the two dominates, or refining the mesh,
would be a separate investigation, and the brief says stop after FD verification — no
optimization, and by extension no case redesign).

## Result vs. reference

Stock (unmodified) `UBend_Channel/runScript.py` documents a baseline `CPL0 = 85.23 - 35.62 =
49.61` (its own weighted-objective normalization constant, presumably from the original
author's run). This run's TP1/TP2 at the same undeformed baseline shape:
**TP1 − TP2 = 52.345**, a **5.5% deviation** from `CPL0`. Plausible causes: the container's
OpenFOAM is `v2506`; the case's `FoamFile` headers (and the `convertToMeters` IOWarning at
`blockMesh` time) say `v1812` — a ~6-year solver-version gap in a case whose numerics
(GAMG tolerances, wall-function formulation defaults) are known to have shifted across that span.
5.5% is a modest, plausibly solver-version-driven baseline deviation, not evidence of a setup
error (the mesh, BCs, and `fvSolution`/`fvSchemes` were not touched).

## Blockers/lessons (documented, not hidden)

1. **`bash -lc './script.sh'` sourcing `loadDAFoam.sh` from a nested script file crashes.**
   `probe_driver.sh`, invoked as `bash -lc './probe_driver.sh'` inside the container, failed
   instantly with `pop_var_context: head of shell_variables not a function context` — an
   OpenFOAM `config.sh` / bash quirk when its `etc/bashrc` chain is sourced from inside a
   script invoked as a nested shell rather than inlined into the top-level `-lc` string.
   **Fix:** inline the whole loop directly into the single `bash -lc '...'` string passed to
   `docker run` (as done for the successful probe runs) instead of `source`-ing DAFoam and then
   calling out to a separate `.sh` file.
2. **argparse single-dash flags reject negative values.** `-probeDelta -1e-4` was parsed by
   Python's `argparse` as two separate (unrecognized) flags, not one flag with a negative
   argument (`error: argument -probeDelta: expected one argument`). **Fix:** use
   `-probeDelta=-1e-4` (equals-sign form), which argparse accepts unambiguously.
3. **`check_totals` known trap (from Ladder A1) did not recur this run** — `processor*` was
   removed with `sudo rm -rf processor*` before calling `check_totals`, and it completed clean.
   Confirms A1's lesson (clean `processor*` state between task invocations in the same case dir)
   generalizes to this case.

## Bottom line

- **Primal:** converged to a genuine numerical fixed point (objective stable to 7-8 significant
  digits over the last 400 SIMPLE iterations); field residuals plateau above `primalMinResTol`,
  a known characteristic of this case class, not a defect introduced here.
- **Adjoint:** computed successfully, GMRES converged (86 iters, `PetscConvergedReason: 2`),
  reproducible bit-for-bit across independent cold starts.
- **FD verification: does NOT cleanly pass.** Only 5/27 shape-gradient components land within
  this lab's previously-calibrated ≤12% band; 2 components flip sign; the aggregate
  vector-norm relative error is 46.6%. A step-size diagnostic on one component rules out "just
  needs a bigger FD step" as the fix. **This is reported as a documented, unresolved
  finding, not papered over as a pass** — the adjoint mechanics are demonstrably working
  (GMRES converges, results reproduce), but rigorous FD confidence in the shape-derivative
  gradient on this specific coarse mesh/case is not established by this rung's data.

**These numbers (46.6% aggregate, 5/27 within 12%, 2 sign flips, TP1=88.11838267130871,
TP2=35.7731663319629) are the as-measured result from the original run above and are left
unmodified.** The section below is a follow-up test of the primal-convergence hypothesis raised
after this record was first written; it does not change anything above.

---

## Addendum: primal-convergence hypothesis test (coordinator-directed)

**Hypothesis under test:** FD-vs-adjoint agreement is gated by primal convergence — the adjoint
is exact for the discrete *converged* state, but if the primal sits at a residual plateau, the
adjoint linearizes about a non-solution point while each FD-perturbed primal re-solves to a
slightly different point on the same non-converged manifold, producing FD noise no step size can
fix. Supporting observation offered: this case's `Total Residual Norm2 = 55.776` is dominated by
`T` at `41.16` — T is solved as part of the primal state but excluded from the objective/adjoint
(`addToAdjoint: False`), a carryover from this case's CHT lineage.

### Step 1 — attempt to converge the primal properly

**1a. More iterations alone (no other change).** Bumped `controlDict endTime` 1000 → 5000 and
reran `-task run_model`. Result: **residuals were unchanged to 10+ significant figures**
(`p initRes` = `0.00022576249734...` at both iteration 900-in-the-original-run and everywhere
from iteration ~600 through 5000 in this extended run; `Total Residual Norm2` identical,
`55.776...`). This is not a slow asymptote — it is a bit-for-bit-stable fixed point of the
discrete SIMPLE iteration reached well before iteration 1000. More iterations, alone, provably do
nothing here.

**1b. Tighter linear solves + `residualControl` + 10x more iterations.** Added a `SIMPLE
residualControl` block (`p`, `U`, `T`, `nuTilda` all `1e-8`, matching A1's convergence bar),
tightened the inner linear solvers (`p`: GAMG `relTol` 0.1→0.01, `tolerance` 0→1e-10; `U`/`T`/
`nuTilda`/etc: `smoothSolver` `relTol` 0.1→0.01, `tolerance` 0→1e-10, `nSweeps` 1→2), and raised
`endTime` to 10000 as a safety cap. This is a real deviation from the official tutorial's
`fvSolution`/`controlDict` — disclosed explicitly here, as instructed. `residualControl` **never
triggered** (ran the full 10000 iterations). Result at iteration 10000:

| field | stock (iter 1000, from original record) | tightened (iter 10000) | change |
|---|---|---|---|
| `p` initRes | 2.2576e-04 | 2.0568e-04 | -8.9% |
| `T` Residual Norm2 | 41.160 | 43.504 | **+5.7% (worse)** |
| `nuTilda` initRes (approx) | ~2.6e-4 (order) | 3.620e-04 | worse |
| `Total Residual Norm2` | 55.776 | 59.324 | **+6.4% (worse)** |

`primalMinResTol = 1e-8` was **not reached for `p`, `T`, or `nuTilda`** despite an order-of-
magnitude tighter inner solve and 10x the iterations. Tightening made the aggregate residual
metric slightly *worse*, not better — consistent with a genuine limit cycle (most plausibly
secondary Dean-vortex flow structures in this curved duct that a steady RANS/SIMPLE solver
cannot fully suppress on this 4800-cell mesh) rather than an under-resolved linear solve or an
under-iterated outer loop. **A1's `primalMinResTol=1e-8` bar was not achievable here with a
cheap settings change; the plateau is intrinsic to this case, not a defect in the run.**

On the T-specific mechanism proposed: for this case, momentum/pressure (`transportProperties`
has a constant `nu`, no T-dependent properties, no buoyancy) do not depend on `T` at all, and the
objective (`TP1`, `TP2` = functions of `p`, `U` only) does not depend on `T`. In exact arithmetic
this makes the reverse-mode adjoint row for `T` mathematically decoupled from the `U`/`p` rows
that matter for `OBJ.val` — `T`'s non-convergence has no analytic channel into this gradient. The
empirical result below is consistent with that: tightening `T`'s solve (and everything else) did
not improve FD/adjoint agreement, and `T`'s own residual got slightly *worse* under tightening,
not better, further undercutting "T is the blocker" as the dominant mechanism here. I did not
go further and literally remove/freeze the T equation (would require solver-level surgery beyond
a `fvSolution`/`controlDict` change, and the evidence in hand was already decisive — see Step 3).

Given 1a/1b showed 1000 vs. 10000 iterations produce the same fixed point, `endTime` was reverted
to `1000` (matching the original run's cost) for the head-to-head FD-verification rerun in Step 2,
keeping the tightened `residualControl`/solver-tolerance changes from 1b. New config hash
(`runScript.py` + tightened `system/fvSolution` + `system/fvSchemes`):
`ae476e6ca529f0e7d1e14b07644d90a67f69f1f10bd5e99a64454a98ad3b30f0`.

### Step 2 — re-run `compute_totals` + `check_totals`, same DVs, same FD step 1e-4

Same `of=["OBJ.val"], wrt=["shapexUpper"]`, central FD, `step=1e-4`, `step_calc="abs"` —
nothing else changed from the original run.

`compute_totals` (tightened, `endTime=1000`): `TP1=88.11834517951668`, `TP2=35.77316763274566`
→ pressure loss `52.34517754677102` (vs. original `52.34521633934581` — differs in the 6th
significant figure, i.e. the tightened settings nudge the solution by noise-level amounts, not a
materially different design point). Adjoint GMRES: 87 iterations, `PetscConvergedReason: 2`
(vs. 86 before) — essentially identical adjoint behavior.

`check_totals` at `endTime=10000` (tightened) was attempted first and **timed out at the 600s
foreground cap without finishing** — each of the 55 FD primal solves now costs ~10x more
(10000 vs. 1000 SIMPLE iterations), and the sweep needs ~35-40 minutes at that iteration count,
which doesn't fit a single foreground call. (Documented as a blocker below; log kept as
`A5_check_totals_tightened_endtime10000_TIMEDOUT_run1.log`, killed at `ExecutionTime = 587.37s`
mid-sweep.) Re-ran at `endTime=1000` (tightened solver tolerances only) instead — this is the
valid comparison, since Step 1 already proved 1000 vs. 10000 iterations make no difference to the
residual plateau. Completed in 280s.

### Step 3 — before/after comparison

| metric | original (stock `fvSolution`, iter 1000) | tightened (`residualControl` + tighter inner solves, iter 1000) | verdict |
|---|---|---|---|
| `p` initRes | 2.2576e-04 | 2.0568e-04 (measured at iter 10000, unchanged by iter 1000) | ~9% better, still nowhere near 1e-8 |
| `Total Residual Norm2` | 55.776 | 59.324 | **worse** |
| Analytic magnitude \|\|d(OBJ)/d(shapexUpper)\|\| | 19.384 | 19.387 | unchanged |
| FD magnitude | 33.409 | 33.239 | unchanged |
| **Aggregate relative error** | **46.64%** | **46.21%** | **no material change (Δ=0.4 pts)** |
| Components within ≤12% band | **5 / 27** | **4 / 27** | **slightly worse** |
| Sign flips | **2** (idx 8, 17) | **3** (idx 2, 8, 17) | **slightly worse** — idx 2 newly flips |

Per-component detail moved around noticeably component-by-component (e.g. idx 0's error dropped
115%→55%, but idx 1 jumped 6.9%→788% and idx 2 jumped 1.1%→1857% with a new sign flip), but the
*aggregate* picture — which is what the hypothesis predicts should improve — did not improve.

### Verdict: hypothesis REFUTED (for the convergence-tightening tested here)

Tightening the primal's `residualControl`/linear-solver tolerances by 1-2 orders of magnitude and
running 10x more iterations did **not** move `p`/`T`/`nuTilda` anywhere near A1's `1e-8` bar (the
plateau is a genuine fixed point of this case, confirmed by the bit-identical 1000-vs-5000-vs-10000
iteration residuals), and the resulting FD-vs-adjoint agreement is statistically the same as
before (46.6% → 46.2%), with the per-component picture (band membership, sign flips) getting
marginally *worse*, not better. **This rules out "primal convergence plateau alone explains the
FD gap" as this rung's answer.** The evidence points instead at the other candidate already
named in the original record: **coarse-mesh (4800-cell) / non-smooth mesh-warp response to
single-FFD-point shape perturbations**, compounded by a residual plateau that is itself likely a
genuine secondary-flow (Dean-vortex) limit cycle intrinsic to steady RANS on this U-bend
geometry at this resolution — not resolvable by tightening solver tolerances alone. A real test of
the mesh-resolution hypothesis (mesh refinement study, analogous to the NACA0012 case's own
3.65x-refinement follow-up referenced in Ladder A1) would be the natural next step, but that is
outside this rung's scope (no optimization / no new case redesign directed here).

**Lab-wide implication:** the clean rule the coordinator hypothesized — "no FD verification is
meaningful until the primal is converged" — is not established by this data as *sufficient*; a
non-converged primal is clearly not *ideal*, but this rung shows that pushing convergence harder
does not automatically fix FD/adjoint agreement, at least not on a case whose residual plateau
turns out to be a hard limit cycle rather than an under-iterated/under-tolerant solve. The
actionable version of the rule this rung supports: **check whether the residual plateau is a
genuine fixed point (extend iterations and re-tighten solver tolerances; if the residual doesn't
move, more of the same won't help) before spending FD-verification budget** — and if it is a hard
plateau, look to mesh resolution / geometry smoothness rather than solver tolerances.

### Additional blocker/lesson from this addendum

- **`check_totals` at 10x the primal iteration count does not fit the 600s foreground cap.**
  55 FD-sweep primal solves at `endTime=10000` needs ~35-40 minutes; killed by the Bash tool's
  10-minute timeout mid-sweep (`ExecutionTime = 587.37s` at kill time). **Fix used:** confirmed
  via the iteration-count diagnostic (Step 1a/1b) that 1000 vs. 10000 iterations reach the same
  fixed point, then reran the FD sweep at `endTime=1000` (tightened solver tolerances only) —
  valid because the residual plateau is iteration-count-independent here. General lesson for
  future rungs: before scaling up `endTime` for a `check_totals` sweep, do a cheap `run_model`-only
  check at the higher `endTime` first to confirm it's actually buying convergence, since the
  FD sweep's cost multiplies by the same factor per component.

## Addendum, 2026-07-29: tested against A1's confirmed `mesh.warpDeriv` root cause -- does NOT share it

A1 (NACA0012, this lab's other and longest-standing gradient-accuracy failure) had its idx6
sign-flip traced to a confirmed defect in `mesh.warpDeriv` (IDWarp's reverse-mode mesh-warp
derivative -- see `PROOF.md` §15), specific to an opposing-direction combination shape-mode
construction. Given A5's own signature -- aggregate 46.6%, 2 components sign-flipped (idx 8, 17),
step-independent, and getting WORSE under tighter primal convergence rather than better -- looks
superficially like A1's, this addendum tests directly whether it is the same mechanism.

**Parameterization check first, from `runScript.py` itself:** `shapexUpper` (the 27-component group
FD-checked above) is built via `self.geometry_aero.nom_addLocalDV(dvName="shapexUpper",
pointSelect=PS, axis="x")`. `nom_addLocalDV` is a thin wrapper (confirmed by reading it in the
`dafoam/opt-packages:latest` container) around `DVGeo.addLocalDV(dvName, axis=axis,
pointSelect=pointSelect)`: **one FFD point moving along one axis per DV, unconditionally.** There is
no opposing-direction, multi-point combination construction anywhere in this case's parameterization
-- unlike A1's `nom_addShapeFunctionDV`-based `shape` group, which defines idx6/idx7 as four FFD
points moving in two opposing pairs within a single DV. Every one of A5's 27 `shapexUpper`
components, including idx8 and idx17, is a single-station mode by A1's own classification.

**Direct test (new script, `probeWarpDerivA5.py`):** the same dot-product/adjoint-identity method
that confirmed A1's defect (`<w, dXv/dShape>_FD == <warpDeriv(w), dXs/dShape>_analytic`, pure
`DVGeo`+IDWarp geometry, no CFD, `--cpus=3 --memory=3g`, `mpirun -np 4` matching this case's own
`decomposeParDict`), run on idx8 and idx17 (2 random seeds each) against two controls, idx2 (1.1%
error in the real check above) and idx26 (2.7%):

| component | seed | FD_scalar | AN_scalar | rel_err | sign |
|---|---|---|---|---|---|
| idx2 (control) | 2026 | 41.2593 | 41.2625 | 0.0078% | agree |
| idx26 (control) | 2026 | 41.8169 | 41.8201 | 0.0075% | agree |
| idx8 (sign-flip in real check) | 2026 | 30.1271 | 30.0309 | 0.32% | agree |
| idx8 (sign-flip in real check) | 42 | 30.8182 | 30.7076 | 0.36% | agree |
| idx17 (sign-flip in real check) | 2026 | 28.8697 | 28.4947 | 1.30% | agree |
| idx17 (sign-flip in real check) | 42 | 29.8975 | 29.5167 | 1.27% | agree |

**No sign flip anywhere.** idx8/idx17 do show more disagreement than the controls (0.32-1.30% vs.
0.0075-0.0078%, a real, honestly-reported ~40-170x gap, not nothing) but this is categorically
different from A1 idx6/idx7's 108-149%, sign-flipped failure under the identical test.
**`mesh.warpDeriv` is not the cause of A5's idx8/idx17 defect.**

**Verdict: A1 and A5 do not share a root cause.** A5's defect remains unidentified, and the evidence
already in this document points toward the primal-convergence mechanism this addendum's own earlier
sections raised and could not fully resolve: the residual never approaches a real fixed point in the
1e-8 sense A1 achieves, and tightening it further makes the sign-flip count worse (2->3), the
opposite of what A1's decisive tightening test showed (4 orders of magnitude tighter changed nothing
for A1, ruling noise out there). This lab's two gradient-accuracy failures do not collapse to one
upstream cause; they are two separate defects that happen to share a coarse symptom profile
(step-independent, sign-flipped, aggregate FD disagreement) without sharing a mechanism.

Evidence: `probeWarpDerivA5.py` (new, this addendum) and 7 raw run logs
(`probewarpderiv_a5_idx2_np1_run1.log`, `probewarpderiv_a5_idx2_seed2026_np4_run1.log`,
`probewarpderiv_a5_idx26_seed2026_np4_run1.log`, `probewarpderiv_a5_idx8_seed2026_np4_run1.log`,
`probewarpderiv_a5_idx8_seed42_np4_run1.log`, `probewarpderiv_a5_idx17_seed2026_np4_run1.log`,
`probewarpderiv_a5_idx17_seed42_np4_run1.log`) in `demo-output/website/dafoam/`.

## Addendum, 2026-07-30: chain-link isolation (coordinator-directed) -- dF/dW and dR/dXv probes invalid (own bugs, found and fixed in prose), dR/dW closed as a units artifact, real defect still unidentified

With `mesh.warpDeriv` cleared (previous addendum), the coordinator asked for the same link-by-link
isolation that found A1's root cause, applied to A5's three remaining chain links: the objective's
dependence on state (`dF/dW`), the residual's dependence on mesh coordinates (`dR/dXv`), and the
residual's dependence on state (`dR/dW`) -- with the objective type (a two-patch pressure-difference on
a half-model with a symmetry plane) flagged as the first place to look.

**Method (`probeChainLinksA5.py`, new this session):** one real primal solve to get a converged baseline
`W0`, `Xv0`, then direct dot-product-identity tests of each link using `DASolver.evalFunctions()` /
`DASolver.getResiduals()` (pure post-processing/assembly calls, no re-solve) against
`DASolver.solverAD.calcJacTVecProduct()` (the exact function `DAFoamSolver`/`DAFoamFunctions` call in the
real adjoint chain). Two of the three links came back with self-inflicted bugs, caught before being
reported as findings:

- **`dF/dW`: invalid.** FD came back exactly `0.0` in all 12 measurements (2 functions x 2 seeds x 2
  steps). Traced into DAFoam's C++ source (`DASolver.C`): `evalFunctions()` calls `getTimeOpFuncVal()`,
  which reads a value from `functionTimeSteps_`, an array recorded DURING the primal solve's own time
  loop -- it never re-evaluates from the live state `setStates()` was used to perturb. The correct, live,
  single-evaluation call is `DASolver.solver.calcFunction(name)` (`DASolver::calcFunction`, confirmed
  in source to call `daFunction.calcFunction()` directly, no stored history) -- not yet re-run with the
  fix.
- **`dR/dXv`: invalid.** The Xv perturbation direction was generated independently per MPI rank. Mesh
  points on processor boundaries are physically duplicated across ranks and must receive an IDENTICAL
  perturbation; this test's did not, producing an inconsistent parallel mesh (1.23 million OpenFOAM
  `procBoundary2to3` face-area-mismatch warnings) and an FD side that DIVERGED under step refinement
  (h=1e-4 to 1e-5 changed the answer 20x -- the signature of an invalid mesh, not a real derivative). Log
  truncated from 4.2GB to a 10KB summary (`chainlinks_out_TRUNCATED.log`). Correct redesign: perturb Xv
  through an actual small FFD/warp-based direction (globally consistent by construction, the same
  technique used throughout this investigation's mesh-warp tests), not raw independent per-rank noise --
  not yet re-run.
- **`dR/dW`: real signal, but CLOSED as a units-convention artifact, not a defect.** The aggregate
  dot-product test showed AN 285-337x larger than FD, same sign, both seeds -- large enough (two orders
  of magnitude beyond anything else measured anywhere in this investigation: A1's worst ~150%, A5's own
  real check tops out at 208%) that the coordinator's rule applied: a discrepancy that size means the
  PROBE is the first suspect, not the code. Per the coordinator's discriminating test -- compute the
  ratio component-by-component rather than as an aggregate -- new script `probeA5DiagRatio.py` (serial,
  no MPI, sidesteps all parallel-consistency questions) tested 60 random DIAGONAL entries of `dR/dW`
  directly: `FD_i` via perturbing state component `i` alone and reading residual component `i` back
  (`getResiduals()`, no re-solve); `AN_i` via `calcJacTVecProduct` seeded with a one-hot vector at `i`
  (`product[i] = J[i,i]` exactly, since `product = J^T e_i`). **Result: 43 of 60 ratios landed on EXACTLY
  one of four values, each matching a state variable's own `normalizeStates` constant from this case's
  `daOptionsAero`** -- 23 rows at `8.400000` (=`U0`), 9 at `35.280000` (=`(U0^2)/2`), 7 at `0.001000`
  (=`nuTilda0`), 4 at `300.000000` (=`T0`) -- reproducing to 6 significant figures across dozens of
  physically unrelated cells and wildly different state magnitudes (`W0_i` ranging from -12 to +300).
  That precision and cross-cell consistency is the signature of an exact scaling convention, not noise:
  **`calcJacTVecProduct`'s `"residual"` output type returns values in NORMALIZED units (scaled by each
  state variable's own `normalizeStates` constant), while `DASolver.getResiduals()` returns RAW physical
  units.** Once that unit mismatch is accounted for, `dR/dW`'s diagonal agrees with the finite difference
  essentially exactly (the ratio's own consistency to 6 significant figures IS the agreement -- there is
  no leftover discrepancy once the units are reconciled). **This was always a probe artifact, not a
  gradient defect; `dR/dW` is CLOSED, not confirmed as A5's cause.** The remaining 17 of 60 sampled rows
  (small, non-clustered ratios, `AN_i` consistently near +-1.0 regardless of `FD_i`'s magnitude) are most
  consistent with the `surfaceScalarStates` (`phi`, face flux) block, whose residual is closer to an
  algebraic continuity identity than a PDE residual (a self-derivative near 1 by construction) -- flagged
  as understood-in-kind but not chased to a confirmed explanation this session.

**Net effect: none of the three remaining chain links has produced a confirmed A5 defect.** Two were
this session's own probe bugs (found, explained, fix identified for both, not yet re-run). The third
(`dR/dW`) looked like the strongest lead by a wide margin -- and is now closed as a units-convention
non-issue by the same component-wise-ratio technique that would have confirmed it as real had the
pattern been patternless instead of an exact 4-way constant split. **A5's real defect remains
unidentified.** Next steps, not yet done: re-run `dF/dW` with `calcFunction()` instead of
`evalFunctions()`; redesign `dR/dXv` with a globally-consistent perturbation direction; if both come back
clean too, the remaining candidates are the `phi`/`surfaceScalarStates` block specifically, or a defect
that only appears through the coupled multi-equation system (not visible in any single isolated link),
which would need a different kind of test than link-by-link isolation.

Evidence: `probeChainLinksA5.py`, `probeA5DiagRatio.py` (both new this session, in
`ladder-a/A5_work/UBend_Channel_pressureloss/`), `chainlinks_out_TRUNCATED.log`, `diagratio_out.log`.

## Addendum, 2026-07-30: symmetry-plane proximity test -- exonerated, no solve required

Every link in the chain (`mesh.warpDeriv`, `dF/dW`, `dR/dXv`, `dR/dW`) has now been isolated and either
refuted or invalidated-and-not-yet-confirmed (previous addendum) -- the coordinator's conclusion: if
every link is individually correct, the error is in how they combine, or in the solve between them, not
in a single Jacobian. Two untested candidates were raised: adjoint-solve accuracy (this session's next
test, below) and the symmetry plane specifically -- repeated three times as a standing hypothesis because
A5 is a half-model and this case's own `meshOptions["symmetryPlanes"]` is `[]` (confirmed both in the
ladder's adapted `runScript.py` AND in the untouched official tutorial -- an inherited omission, not a
ladder-introduced one). The specific, falsifiable test: **are idx8 and idx17 (the two sign-flipped
components) the design variables geometrically NEAREST the symmetry plane?**

This required no solve -- only the FFD control-point coordinates (already generated this session,
`probeFFDGeometry.py`) and the symmetry plane's actual location, confirmed directly from the mesh itself
(not assumed): parsed `constant/polyMesh/points.gz` + `faces.gz` for the `sym` patch (`boundary` file:
`type symmetry`, `startFace 14728`, `nFaces 600`) and found **every point on the `sym` patch sits at
`z = 0.0` exactly** (`x` spans the full `[0, 0.8445]`, `y` spans `[-0.0945, 0.0945]`, `z` is a single
value, confirmed a true flat symmetry plane at `z=0`). The domain's opposite z-extent (the outer wall,
`ubend`/`ubendup` patches) reaches `z=0.0375`.

Cross-referencing against the FFD grid (`pts.shape = (23, 3, 3)`, k-index 0/1/2 along z):

| k | FFD z | distance from symmetry plane | shapexUpper indices at this k (i=7..15) | any sign flip? |
|---|---|---|---|---|
| 0 | z=0.0 (**exactly the symmetry plane**) | 0 (ON the plane) | 0, 3, 6, 9, 12, 15, 18, 21, 24 | **no** (errors 8.5-179.2%, all same-sign) |
| 1 | z=0.010 | mid-span | 1, 4, 7, 10, 13, 16, 19, 22, 25 | **no** (errors 2.3-167.1%, all same-sign) |
| 2 | z=0.038 (**farthest FFD station from the plane**) | maximum | 2, 5, **8**, 11, 14, **17**, 20, 23, 26 | **yes -- both idx8 and idx17 are here** |

**Direct answer: no. idx8 and idx17 are not nearest the symmetry plane -- they are at k=2, the FFD
station FARTHEST from it (z=0.038 vs. the plane at z=0), tied for that same z-station with idx2 and
idx26, which are the TWO CLEANEST-AGREEING components in the entire 27-vector** (1.1% and 2.7%,
independently confirmed clean of the `mesh.warpDeriv` mechanism too in the previous addendum). The two
components literally sitting ON the symmetry plane (k=0, idx0/idx3/.../idx24) show no sign flips at all,
despite being exactly the points a `symmetryPlanes: []` omission in IDWarp's mesh-warp setup would be
expected to endanger first (nothing constrains them to stay on the plane during a shape perturbation).
**The symmetry-plane-proximity hypothesis is exonerated by this test, cleanly, per the coordinator's own
decision rule** ("if they are scattered elsewhere, the symmetry plane is exonerated") -- and more than
merely scattered, the flipped components sit at the opposite geometric extreme from the plane, sharing a
station with the two best-behaved DVs in the set. This is the third time this specific hypothesis has
been raised in this investigation and the first time it has been directly tested; it can be set aside.

Evidence: reused `ladder-a/A5_work/UBend_Channel_pressureloss/probeFFDGeometry.py`'s already-recorded
per-DV coordinate table (this document's earlier working notes) plus a new one-off parse of
`constant/polyMesh/{points,faces}.gz` for the `sym`/`ubendup` patch z-extents (not saved as a standalone
script -- a 30-line inline check, reported here in full).

## Addendum, 2026-07-30: adjoint-solve accuracy -- eliminated, tightening seven orders of magnitude moves the flagged components by under 1%

Second coordinator-directed test: is the discrete adjoint's own linear (GMRES) solve for psi converged
tightly enough that the total derivative it produces is trustworthy, independent of every individually-
correct Jacobian tested so far? Stock convergence was already on record (`adjEqnOption.gmresRelTol =
1e-5`): 86 iterations, `PetscConvergedReason: 2`, final KSP residual `1.08e-4` from an initial `1.24e1`
-- converged to its own specified relative tolerance normally, no red flag on its face, but the tolerance
itself had never been tightened and re-checked against the verification result.

New file `runScript_tightAdjoint.py` -- a single-line diff from `runScript.py`
(`gmresRelTol: 1e-5` -> `1e-12`), everything else byte-identical. Ran `-task compute_totals` (`np=4`,
`--cpus=4 --memory=6g`, launched via `scripts/launch_solve.sh` after `case_preflight.sh` passed clean).
**Adjoint converged to `PetscConvergedReason: 2` at 126 iterations (vs. 86 stock), final KSP residual
`8.05e-12` (vs. `1.08e-4` stock) -- roughly 10,000x tighter.**

| component | stock (`gmresRelTol=1e-5`) analytic | tightened (`1e-12`) analytic | change | established FD | still sign-flipped? |
|---|---|---|---|---|---|
| idx8 | -0.84337 | -0.84328122 | **0.0105%** | 0.78391 | **yes** |
| idx17 | -0.62881 | -0.63435973 | **0.8826%** | 2.90530 | **yes** |

**Tightening the adjoint's own linear solve by seven orders of magnitude (and its actual achieved
residual by four orders) moved idx8 by 0.01% and idx17 by 0.88% -- utterly negligible against the 207.6%
and 121.6% real disagreements, and BOTH components remain sign-flipped at the tightened tolerance.**
This eliminates adjoint-solve accuracy as A5's cause, cleanly: the total derivative is not a symptom of
an under-converged linear solve; it is a converged, reproducible, stable wrong answer.

Evidence: `runScript_tightAdjoint.py`, `tightadjoint_out.log` (both in
`ladder-a/A5_work/UBend_Channel_pressureloss/`).

## Addendum, 2026-07-30: on whether the three isolated links were tested truly in isolation

A parallel finding on A1 (a different session) showed that an EARLIER warpDeriv-vs-FD test there had an
unnoticed circularity: its FD side reached the mesh via `DVGeo.update(shape)` (composing the FFD
parameterization WITH the physical warp) and its analytic side dotted `warpDeriv(w)` against DVGeo's OWN
forward Jacobian `v = dXs/dShape_idx` (also a composition) -- so a "clean" result for a given component
proved only that the DOT PRODUCT of warpDeriv's error against that SPECIFIC v was small, not that
warpDeriv itself was correct; if the true defect lived in warpDeriv and its error happened to be
(nearly) orthogonal to a particular idx's v, the combined test would report "clean" for a genuinely
defective link. The fix that broke this open there was to perturb along `v` directly, bypassing
`DVGeo.update()` entirely, so the warp is exercised alone.

Checked this against each of A5's three link tests directly, because the same trap would equally
invalidate any of them:

- **`dR/dW` (`probeA5DiagRatio.py`):** `FD_i` perturbs the STATE `W` directly
  (`DASolver.setStates(W0 +/- h*e_i)`) and reads the residual straight back (`getResiduals()`) -- no
  DVGeo, no mesh warp, no adjacent operator anywhere in the FD path. `AN_i` calls
  `calcJacTVecProduct(stateVar -> residual)` on the SAME `W0`. Both sides operate on `W` as the direct,
  un-composed input. **Not the same trap.** The units-convention explanation is additionally protected
  from this specific failure mode by its own evidence: 43 of 60 diagonal samples, spanning dozens of
  physically unrelated cells and state magnitudes from -12 to +300, landed on exactly one of four values
  each matching a `normalizeStates` constant to 6 significant figures -- a coincidence that consistent
  and that precise is not explainable by an orthogonal-projection artifact, which would produce scatter,
  not four exact clusters.
- **`dF/dW` (invalid, bug already found and explained):** `FD` perturbs `W` directly and calls
  `evalFunctions()`/`getTimeOpFuncVal()` (the stale-history bug) -- not composed with any adjacent
  operator either; the bug that invalidated this test was unrelated (wrong API, not circularity). Will
  be re-run with `calcFunction()` -- still a direct, single-link test once fixed.
- **`dR/dXv` (invalid, bug already found and explained):** `FD` perturbed `Xv` DIRECTLY via
  `setVolCoords(Xv0 +/- h*dXv)`, bypassing `DVGeo`/`mesh.warpMesh()` entirely -- also not composed with
  an adjacent operator; its bug (per-rank-inconsistent perturbation breaking parallel mesh validity) is
  a different, already-diagnosed failure mode. The redesign already planned (perturb through an actual
  small FFD-warp-based direction, for global consistency) borrows a TRUSTED vector as a raw input the
  same way A1's fix did, and does not reintroduce the composition trap.

**Conclusion: none of A5's three NEW link tests (this session) shares A1's specific circularity.** All
three were constructed as direct injections into the link's own input space from the start, not as
compositions of two operators' outputs against each other. The dR/dW result stands. The real,
honestly-remaining gap is coverage, not circularity: dR/dW's diagonal-only sampling has not ruled out an
off-diagonal defect in that same Jacobian, and dF/dW and dR/dXv are still unvalidated pending their bug
fixes -- both real open items, tracked as such, not resolved by this check.

**But there is a FOURTH link, not from this session, that DOES share A1's exact structure: A5's own
`mesh.warpDeriv` clearance from the previous-session addendum.** That test (`probeWarpDerivA5.py`) used
precisely the composed pattern A1's original test used -- FD via `DVGeo.update(shape)` -> `warpMesh()`
(composing DVGeo's shape-to-surface map with the physical warp), analytic via `warpDeriv(w)` dotted
against DVGeo's own `totalSensitivityProd` (also a composition). By the same logic that reopened A1's
idx0/idx1, this clearance was untested for the DVGeo-nonlinearity ambiguity and needed the same
decomposition check before being trusted as ruling out `warpDeriv`.

**Ran it. New script `probeA5HandComposition.py`** -- A5's analog of the airfoil's
`probeHandComposition.py` Stage 2: perturbs surface coordinates directly along
`eta = dXs/dShape_idx` (DVGeo's own trusted Jacobian column), bypassing `DVGeo.update()` entirely on the
FD side, and separately confirms the ORIGINAL (`DVGeo.update()`-based) FD still matches this new
DVGeo-bypassing FD. Tested idx2/idx26 (controls) and idx8/idx17 (the sign-flipped components), 2 seeds
each, pure geometry (`np=1`, no CFD, 5.0s total):

| idx | seed | FD (via `DVGeo.update()`) | FD (direct `Xs`+`eta`, bypasses `DVGeo`) | DVGeo-nonlinearity rel. err | `warpDeriv` vs. direct-FD rel. err | established (composed test) |
|---|---|---|---|---|---|---|
| 2 (control) | 2026 | 36.4156188 | 36.4156188 | **1.18e-10** | **0.0082%** | 0.0078% |
| 2 (control) | 42 | 36.4992420 | 36.4992420 | **1.63e-10** | **0.0079%** | -- |
| 8 (FLIP in real check) | 2026 | 28.5864008 | 28.5864008 | **1.08e-10** | **0.44%** | 0.32% |
| 8 (FLIP in real check) | 42 | 30.1226563 | 30.1226563 | **9.78e-11** | **0.38%** | 0.36% |
| 17 (FLIP in real check) | 2026 | 26.5695254 | 26.5695255 | **4.76e-10** | **1.16%** | 1.30% |
| 17 (FLIP in real check) | 42 | 26.3408382 | 26.3408382 | **7.27e-10** | **1.08%** | 1.27% |
| 26 (control) | 2026 | 37.2758252 | 37.2758251 | **3.07e-9** | **0.0050%** | 0.0075% |
| 26 (control) | 42 | 36.6850588 | 36.6850586 | **3.85e-9** | **0.0077%** | -- |

**Two results, both clean:**

1. **DVGeo nonlinearity is ruled out decisively** -- the two FD methods agree to 9-10 significant
   figures (relative error `1e-9` to `1e-10`, essentially machine precision) for every component tested.
   `nom_addLocalDV`'s single-point, single-axis construction is, as expected, an extremely linear FFD
   operation for this case; unlike A1's `addShapeFunctionDV` combo modes, there was never much reason to
   suspect otherwise, and now it is confirmed rather than assumed.
2. **`mesh.warpDeriv`, tested in TRUE isolation (bypassing `DVGeo.update()` on the FD side, exactly the
   fix that reopened A1's idx0/idx1), reproduces the SAME small percentages as the original composed
   test** -- idx8: 0.38-0.44% (vs. 0.32-0.36% composed), idx17: 1.08-1.16% (vs. 1.27-1.30% composed),
   controls unchanged at ~0.005-0.008%. **Unlike A1's idx0/idx1, where true isolation revealed a LARGER,
   previously-masked warpDeriv error, A5's idx8/idx17 show no such reveal: the small disagreement was
   already the true, isolated warpDeriv linearization error, not an artifact of testing it combined with
   DVGeo's Jacobian.** A5's `mesh.warpDeriv` clearance is CONFIRMED, not merely unretracted -- it holds up
   under the exact scrutiny that overturned the equivalent A1 conclusion.

This closes the loop the coordinator's methodological point opened: every one of A5's now four
link-isolation tests (`mesh.warpDeriv`, `dF/dW`, `dR/dXv`, `dR/dW`) has been checked specifically for the
composition/circularity failure mode that caught out A1, and none carries it. A5's real defect remains
genuinely unidentified -- not because a link was mis-tested, but because it has not yet been found.

Evidence: `probeA5HandComposition.py`, `handcomp_a5_out.log` (both in
`ladder-a/A5_work/UBend_Channel_pressureloss/`).

## Addendum, 2026-07-30: off-diagonal dR/dW -- matvec test does not resolve cleanly; the units convention is richer than the diagonal test characterized, and that ambiguity, not a confirmed coupling defect, is the honest result

`probeA5DiagRatio.py` tested only DIAGONAL entries of `dR/dW`. Off-diagonals encode cell-to-cell and
field-to-field coupling; a defect confined there would produce exactly A5's symptom (locally correct
magnitudes, a globally wrong assembled total, sign flips only where coupling dominates). Coordinator's
directed test: a matvec dot-product identity (one random direction exercises every matrix entry at once)
rather than more diagonal sampling, with the diagonal test's own units correction applied first so the
285-337x factor cannot reappear disguised as a coupling defect.

**Method (`probeA5MatvecDrDW.py`):** `dW` dense/random across the full state vector (exercises coupling
into and out of every cell). `w_R` sparse, supported ONLY on the 43 indices whose row-scale `D_i` was
already confirmed exactly in the diagonal test (23 `U` rows at 8.4, 9 `p` rows at 35.28, 7 `nuTilda` rows
at 0.001, 4 `T` rows at 300), pre-divided by that `D_i` before being passed as `calcJacTVecProduct`'s
seed -- the correction that, if row-scaling is the WHOLE story, exactly cancels it. Three independent
seeds, serial, ~13s total.

**Result: the corrected matvec does NOT cleanly agree.** Relative error 150%, 227%, and 1252% across the
three seeds (vs. the uncorrected variant's 824x-2417x, confirming the correction is doing real work, just
not enough), with 2 of 3 seeds sign-flipped. Naively, this looks like the coordinator's second named
outcome ("matvec disagrees while diagonals agree -> the defect is in the coupling"). **Before accepting
that reading, a follow-up single-entry test was run to check whether the row-only correction model itself
is simply incomplete off-diagonal** (verified only ON the diagonal, where row and column indices coincide
and row-scaling and column-scaling are indistinguishable) -- because an incomplete correction model would
also produce exactly this kind of large, structured disagreement without any real coupling defect at all.

**`probeA5OffDiagSingle.py`:** took ONE full analytic row (`idx=2490`, a `U` row, `D_row=8.4`, confirmed
clean on the diagonal) via a single `calcJacTVecProduct(seed=e_2490)` call, and FD-checked its 6
largest-magnitude off-diagonal entries individually and directly (perturb one other state index at a
time, read residual 2490 back -- no aggregation, no ambiguity about which column contributed what):

| coupled column | column's state value | FD (raw physical) | AN (row-only corrected, `/D_row`) | `AN/FD` |
|---|---|---|---|---|
| col 1996 (nuTilda-like, `W0`=0.0287) | tiny | -129.702964 | -129.702964 | **1.000000** |
| col 3139 (nuTilda-like, `W0`=0.0243) | tiny | -91.5456374 | -91.5456374 | **1.000000** |
| col 1913 (nuTilda-like, `W0`=0.0279) | tiny | -78.6328462 | -78.6328462 | **1.000000** |
| col 1924 (p-like, `W0`=48.88) | O(10-100) | -104.266496 | -437.919283 | **4.200000** |
| col 3132 (p-like, `W0`=48.88) | O(10-100) | 65.7877115 | 276.308388 | **4.200000** |
| col 2492 (p-like, `W0`=48.88) | O(10-100) | 38.4787846 | 161.610895 | **4.200000** |

**The row-only correction is EXACT for the row's coupling to nuTilda-type columns (agreement to 12
significant figures, no further correction needed) but off by a further factor of exactly `4.200000`
-- reproduced to 6 decimal places across three independent p-type columns -- for the row's coupling to
pressure.** `4.2 = 35.28 / 8.4` (this row's `D_row` divided into the `p` variable's own `D_col`), or
equivalently `D_row / 2`. **This ratio is exact and reproduces across unrelated columns of the same
type -- the signature of a clean, deterministic convention, not noise or a genuine physics defect.** A
real coupling error would not produce a precise `4.200000` multiplier three separate times on unrelated
mesh locations; it would produce inconsistency. The most likely mundane explanation, not confirmed in the
time available: momentum-equation coupling to the pressure-gradient term in a SIMPLE-algorithm
discretization often carries its own structural scaling (e.g. related to the momentum equation's diagonal
coefficient, part of Rhie-Chow-style pressure-velocity coupling) that is a per-TERM feature of the
discretization's assembly, not captured by the overall per-VARIABLE `normalizeStates` convention the
diagonal test characterized.

**Honest conclusion: the matvec test's large disagreement is not evidence of a genuine off-diagonal
defect. It is evidence that the row-only correction model -- which explained the diagonal exactly,
because row and column coincide there -- does not fully describe the off-diagonal convention, which
appears to depend on BOTH the row's and the column's variable type in a way not fully characterized
within this session's scope.** This is a materially different, more honest result than either "off-
diagonal defect confirmed" or "dR/dW fully cleared" -- it is a specific, precisely-located open question
(what is the exact row/column joint scaling convention for `calcJacTVecProduct`'s residual output,
particularly for the momentum-pressure coupling term) that would need tracing into
`daResidual_.calcResiduals()`'s C++ assembly (specifically the `UEqn`/pressure-gradient term) to close,
not more probe-side measurement. **Per the coordinator's own standing instruction not to force a
verdict: dR/dW's off-diagonal structure is left as genuinely unresolved -- neither confirmed clean nor
confirmed defective -- rather than reading the uncorrected matvec gap as a finding it has not earned.**

Evidence: `probeA5MatvecDrDW.py`, `matvec_drdw_out.log`, `probeA5OffDiagSingle.py`, `offdiag_out.log`
(all in `ladder-a/A5_work/UBend_Channel_pressureloss/`).

## Addendum, 2026-07-30: the two-sided correction hypothesis -- stated for the record, NOT tested this session

The coordinator's reading of the `4.200000` result above: `4.2 = 35.28 / 8.4`, the ratio of the pressure
normalization to the velocity normalization -- both already identified by the diagonal test. On a
momentum row (own scale `D_row = 8.4`), an entry coupling to a pressure column needs the PRESSURE scale
rather than the row's. **Falsifiable hypothesis, to be tested empirically in a future session, not this
one:** a two-sided correction -- divide the raw analytic entry by the row's own `D_row`, then multiply by
the coupled column's `D_col` -- should collapse BOTH the `4.2` (row=`U`, col=`p`) and the `1.0` (row=`U`,
col=`nuTilda`) cases to unity simultaneously, and should bring the aggregate matvec into full agreement.
**If it does, the off-diagonal question closes and `dR/dW` is fully cleared. If it does not, there is
something left.**

**One thing worth recording alongside the hypothesis, from a zero-cost arithmetic check of the ALREADY-
MEASURED numbers above (no new compute run -- this is just re-reading the existing table, not a test of
the hypothesis, which per instruction is left for later):** the raw (uncorrected) multiplicative factor
observed for each case is `8.4` for the `nuTilda` coupling and `35.28` for the `p` coupling. Checked
against two candidate formulas using only numbers already in hand:

| candidate | predicted factor, `nuTilda` col (`D_col=0.001`) | predicted factor, `p` col (`D_col=35.28`) | matches measured (`8.4`, `35.28`)? |
|---|---|---|---|
| `D_row / D_col` | `8400` | `0.238` | no, neither |
| `D_col / D_row` | `0.000119` | `4.2` | only the `p` case, and only if compared to the ALREADY-row-corrected value (`4.2`), not the raw factor (`35.28`) |
| `max(D_row, D_col)` | `8.4` | `35.28` | **yes, both, exactly** |

This is not a refutation of the coordinator's hypothesis -- a genuine two-sided `row`/`column` correction
and a `max(D_row, D_col)` pattern are two different, both-plausible readings of the SAME two data points,
and two data points cannot distinguish a ratio-based rule from a max-based one in general (they can agree
by coincidence on exactly two samples and diverge on a third). It IS a flag for whoever runs the actual
test: verify the precise functional form empirically across more than two `(row-type, col-type)`
combinations before assuming the simple two-sided ratio holds everywhere -- the `nuTilda` case in
particular does not fit a `D_row/D_col` or `D_col/D_row` ratio formula against the raw measured factor,
only the `max()` reading does, across BOTH cases measured so far. Whichever functional form turns out to
be right, the coordinator's core structural insight -- correction depends on BOTH row and column type, not
row alone -- is exactly what the data shows and is the right next thing to test.

**Explicitly not tested this session, per instruction:** applying either candidate correction to the full
matvec and re-running `probeA5MatvecDrDW.py`/`probeA5OffDiagSingle.py`-style checks across more
`(row-type, col-type)` pairs to determine the true functional form and settle whether it resolves the
matvec's 150-1252% aggregate disagreement.

## Addendum, 2026-07-30: the two-sided correction, tested -- MAX confirmed over RATIO, dR/dW fully cleared

Owner approved finishing this. Tested both candidate formulas (`max(D_row, D_col)` and the ratio
`D_col/D_row`) against DIRECTLY, INDEPENDENTLY measured `(row, col)` pairs, not the magnitude-heuristic
classification used in the previous addendum's single-entry test.

**First attempt failed instructively and was fixed before drawing any conclusion.** Picking `(row, col)`
pairs by combining one representative row per type with arbitrary OTHER indices from the same 43-index
diagonal sample gave `raw_AN=0, FD=0` for all 16 pairs tested -- most cell pairs in a sparse
discretization simply do not couple directly, and two indices drawn independently at random from across
the whole 4800-cell mesh are very unlikely to be physical neighbors. Fixed by finding each test row's
OWN actual largest-magnitude off-diagonal entries first (guaranteed real, nonzero coupling), THEN
measuring `D_col` directly at those SPECIFIC columns via the same self-derivative diagonal trick
(`AN_ii/FD_ii`) rather than guessing from the column's raw state-value magnitude. This also caught and
corrected an error in the PREVIOUS addendum: one of the columns there was labeled "nuTilda-like" by
magnitude alone (`W0` was tiny); properly measured, its `D_col` is `8.400000` -- it is a near-zero `U`
component (plausible near a wall/stagnation region), not `nuTilda` at all. Its earlier "exact 1.0"
agreement was still correct, just for the coincidental reason that `max(8.4, 8.4) = 8.4` trivially equals
the row-only correction already applied, not because row-only correction is generally valid for
`U`-`nuTilda` coupling.

**`probeA5TwoSidedFormula.py`: 16 pairs, both formulas checked against each.** 13 of 16 pairs had cleanly
measured `D_col` (one of the 4 known constants); the other 3 involved a `phi`-like column whose own
diagonal is not a clean constant (the already-flagged, unresolved ~17/60 messy diagonal samples --
consistent, not a new problem). Of the 13 clean pairs, spanning `U`-`p`, `U`-`U`, `nuTilda`-`nuTilda`,
`nuTilda`-`U`, `p`-`p`, and `T`-`T` couplings:

| formula | result across 13 clean pairs |
|---|---|
| `max(D_row, D_col)` | **1.000000 exactly for 11 of 13; 0.999935 and 0.999995 for the remaining 2 (FD step noise, not formula error)** |
| ratio `raw_AN / D_row * D_col` | 0.001 to 148.176 to 70,559 -- wildly inconsistent, confirms the earlier zero-cost arithmetic flag: the simple ratio formula is wrong |

**The max hypothesis is confirmed, cleanly and unambiguously, exactly as the coordinator's instinct (and
the zero-cost cross-check recorded in the previous addendum) predicted over the literal ratio reading.**

**Applying it to the aggregate matvec required one more design step, recorded because it matters for
reading the result correctly: `max(D_row, D_col)` is NOT separable into a row-function times a
column-function (unlike a product or ratio), so it cannot be cancelled by pre-scaling `w_R` alone the way
the row-only diagonal correction could. It CAN be cancelled exactly, in closed form, if BOTH `w_R` and
`dW` are restricted to be TYPE-HOMOGENEOUS** (every nonzero component of each vector is the same variable
type) -- then `max(D_row, D_col)` is the same constant for every contributing `(row, col)` pair in the
sum, and dividing the whole scalar result by that one constant is exact. This trades "one fully dense
direction hits everything" for "one direction per type-pair, each still exercising every cross term
between every known index of type A and every known index of type B simultaneously" -- a necessary
consequence of `max()`'s structure, not a weaker test.

**`probeA5MatvecMaxCorrected.py`: all 10 unordered type-pairs from the 43 known indices (U/p/nuTilda/T),
2 seeds each, 20 matvecs total.** The 4 same-type pairs (the only ones with nonzero coupling among these
43 randomly-drawn indices -- cross-type pairs among this specific sparse sample happened to have no
direct physical adjacency, giving an uninformative `0 = 0` for all 6 cross-type pairs, correctly flagged
in the log but not a finding either way):

| type pair | seed | FD | AN (max-corrected) | rel. err. |
|---|---|---|---|---|
| `nuTilda`-`nuTilda` | 2026 | -3.77883641 | -3.77883639 | **5.4e-9** |
| `nuTilda`-`nuTilda` | 42 | 6.53796911 | 6.53796909 | **2.9e-9** |
| `U`-`U` | 2026 | -23708.3997 | -23708.4001 | **1.5e-8** |
| `U`-`U` | 42 | -17601.9247 | -17601.9233 | **8.1e-8** |
| `p`-`p` | 2026 | 148918.287 | 148918.287 | **3.4e-13** |
| `p`-`p` | 42 | -24275.0413 | -24275.0413 | **1.4e-12** |
| `T`-`T` | 2026 | 19446.7897 | 19446.7897 | **8.0e-12** |
| `T`-`T` | 42 | 46863.0522 | 46863.0522 | **3.9e-12** |

**Agreement to 3e-13 - 8e-8 relative error -- essentially machine precision, tighter than any other check
in this entire A5 investigation (and tighter than `mesh.warpDeriv`'s own confirmed-clean 0.008-1.16%
elsewhere in this document).** Combined with the 13 single-entry cross-type spot checks above (which
directly covered `U`-`p` coupling specifically, the pairing that produced the striking `4.2` factor, and
confirmed it collapses to `1.000000` under `max()`), this is decisive: **`dR/dW`, corrected for the now
fully-characterized `max(D_row, D_col)` convention, agrees with a true finite difference of the residual
to numerical precision, both on and off the diagonal. There is no coupling defect in `dR/dW`. The
Jacobian is fully cleared, in a materially stronger sense than diagonal sampling alone gave.**

**Outcome, stated per the coordinator's own decision rule:** the corrected matvec agrees -> `dR/dW` is
fully cleared -> the U-bend's remaining, still-unidentified defect (if it exists as a single-link
phenomenon at all) is now confined to the two links whose OWN probes had bugs and were never validly
run: `dF/dW` (needs `DASolver.solver.calcFunction()` instead of the stale-history `evalFunctions()`) and
`dR/dXv` (needs a globally-consistent perturbation direction instead of independent per-rank noise). Both
fixes were identified earlier this session and are unrun.

**Audit-row framing, updated per instruction:** A5's row should no longer read as a blanket
UNVERIFIABLE-CAUSE. Five links have now been examined: `mesh.warpDeriv` (confirmed clean, true isolation),
`dR/dW` diagonal AND off-diagonal (confirmed clean, machine precision), adjoint-solve accuracy
(eliminated), symmetry-plane proximity (exonerated). Two remain genuinely untested due to probe bugs, not
examined and cleared: `dF/dW`, `dR/dXv`. The honest row is no longer "cause unverifiable" in the
open-ended sense; it is "cause not yet found, narrowed to two specific, already-diagnosed, not-yet-rerun
tests" -- a materially smaller gap than existed at the start of this session.

Evidence: `probeA5TwoSidedFormula.py`, `twosided_out.log`, `probeA5MatvecMaxCorrected.py`,
`matvec_maxcorrected_out.log` (all in `ladder-a/A5_work/UBend_Channel_pressureloss/`).

## Addendum, 2026-07-30: the two remaining probe reruns -- one finds a new clean pattern, one shows genuine FD convergence

With `dR/dW` fully cleared, ran the two previously-diagnosed-but-unrun fixes.

### `dF/dW`, fixed: `probeA5FixedDFdW.py`

Fix: `DASolver.solver.calcFunction(name)` (live, single evaluation, confirmed in `DASolver.C` to call
`daFunction.calcFunction()` directly) in place of `evalFunctions()`/`getTimeOpFuncVal()` (the
stored-time-history getter that produced the earlier FD=0.0 bug). **Sanity check first: `calcFunction`
reproduces the converged baseline `TP1`/`TP2` to bit-for-bit precision against OpenMDAO's own values**
(`diff=0.000e+00` both) -- the fix works, the bug is gone, the test is now methodologically valid.

The result is not noise-level agreement, but it is not the earlier bug either -- it is a NEW, exact,
reproducible pattern: `TP1`'s relative error is `34.28000` and `TP2`'s is `7.400000`, IDENTICAL across
both random seeds (2026, 42) and both step sizes (1e-4, 1e-5) tested -- meaning `AN/FD = 35.28` for
`TP1` exactly and `AN/FD = 8.4` for `TP2` exactly, REGARDLESS of the perturbation direction. That
direction-independence is the same signature the `dR/dW` row-scaling had: a fixed per-FUNCTION constant,
not a direction-dependent physics effect. `35.28 = p0` and `8.4 = U0` -- both already-identified
`normalizeStates` constants -- but it is not obvious why `TP1` (inlet total pressure) would carry the
pressure constant while `TP2` (outlet total pressure, the SAME function type, `"totalPressure"`, just a
different patch) carries the velocity constant instead. **Not chased further this session** -- flagging a
concrete lead for whoever does: `pyDASolvers.pyx` exposes `getdFScaling(functionName, timeIdx=-1)`,
literally documented as "get the scaling factor for dF/d? derivative computation," never invoked in this
investigation. **This is reported precisely as measured, not smoothed into either "dF/dW is defective" or
"dF/dW is cleared" -- it is a new, exact, currently-unexplained convention, analogous in character (though
not yet confirmed in mechanism) to the `dR/dW` finding that turned out to be a units convention, not a
defect.**

### `dR/dXv`, fixed: `probeA5FixedDRdXv.py`

Fix: run SERIAL (`np=1`) instead of the earlier `np=4` with independent per-rank random perturbations.
With a single rank there is no processor boundary and therefore no possibility of the specific bug that
invalidated the earlier attempt (mesh points on processor boundaries needing identical perturbations
across ranks) -- simpler than constructing an FFD/warp-derived direction, and consistent with how every
other single-link test this session was run and cross-checked.

**Result: well-behaved, unlike the earlier broken version, which diverged 20x under step refinement.**
Here `AN` is (as expected for a single analytic evaluation) essentially step-independent, and `FD`
CONVERGES toward it as `h` shrinks from `1e-4` to `1e-5`:

| seed | FD (h=1e-4) | FD (h=1e-5) | AN (step-independent) | rel. err. (h=1e-4) | rel. err. (h=1e-5) |
|---|---|---|---|---|---|
| 2026 | 8.84e6 | 1.645e7 | 1.589e7 | 79.7% | **3.4%** |
| 42 | -2.67e7 | -4.96e7 | -5.02e7 | 88.3% | **1.2%** |
| 777 | 6.33e6 | 2.37e6 | 1.536e6 | 75.7% | 35.1% |

Two of three seeds land at 1.2-3.4% at the smaller step -- squarely in the range this investigation has
repeatedly treated as a plausibly-clean signature elsewhere (`mesh.warpDeriv`'s own confirmed-clean
0.008-1.16%, A1's healthy controls at 0.1-2.4%). The third (777) is still improving with refinement
(75.7%->35.1%) but has not reached that range yet. **This is genuine FD convergence behavior, not a fixed
multiplicative artifact (which would not change with `h` at all, as the `dR/dW` units-convention gap
never did) -- consistent with `dR/dXv` being clean, but not yet fully confirmed at this step size.**
Closing it with confidence would need a smaller `h` or a formal step-size sweep (the technique that
settled A1's own idx0/idx1 plateau question), not attempted this session for budget reasons.

**Where this leaves A5, precisely:** `mesh.warpDeriv`, `dR/dW` (diagonal and off-diagonal), adjoint-solve
accuracy, and symmetry-plane proximity are confirmed clean or eliminated. `dR/dXv`, now validly tested for
the first time, trends clean but is not fully confirmed at the step sizes tried. `dF/dW`, now validly
tested for the first time, shows a new, exact, currently-unexplained per-function scaling pattern that is
neither confirmed as a defect nor confirmed as a convention artifact -- the most concrete open lead in the
investigation, with `getdFScaling` named as the specific place to look next.

Evidence: `probeA5FixedDFdW.py`, `fixeddfdw_out.log`, `probeA5FixedDRdXv.py`, `fixeddrdxv_out.log` (all
in `ladder-a/A5_work/UBend_Channel_pressureloss/`).

## Addendum, 2026-07-31 (well W4): the warpDeriv clearance is RETRACTED. A5's defect is the same `mesh.warpDeriv` mis-linearization as A1's, and it was hidden by testing with a random seed

**This addendum overturns the 2026-07-29 addendum above ("tested against A1's confirmed
`mesh.warpDeriv` root cause -- does NOT share it") and the 2026-07-30 addendum that confirmed it
("A5's `mesh.warpDeriv` clearance is CONFIRMED, not merely unretracted"). Both conclusions were
wrong, for one specific and now-measured reason: every `mesh.warpDeriv` test ever run on A5 --
`probeWarpDerivA5.py` (seeds 2026, 42) and `probeA5HandComposition.py` (seeds 2026, 42) -- seeded
the dot-product identity with an ARBITRARY RANDOM vector on the volume-mesh output space. A1's own
record already says, in `PROOF.md` section 17, that this is exactly the test that gives a
misleading answer, and it says so from a measurement: under a random seed A1's idx6 and idx7 failed
identically (108-149%, both sign-flipped); under the real `dCD/dXv` seed they split apart exactly
along the line the real `check_totals` result draws (idx6 634% flipped, idx7 1.74% clean). A random
direction measures whether `warpDeriv`'s error is large SOMEWHERE. Only the real objective's own
seed measures whether that error reaches THIS gradient. A5's clearance was never repeated with the
real seed. It has now been, and it fails.**

### Note on case state before any of this ran

The case directory on disk was left in the **convergence-tightening variant** of `system/fvSolution`
(committed in `20dc8724`, the primal-convergence-hypothesis addendum): `residualControl` added, GAMG
`relTol` 0.1->0.01, `tolerance` 0->1e-10, `smoothSolver` `nSweeps` 1->2. That is not the
configuration the headline numbers at the top of this document (46.6%, 5/27, idx8/idx17 flips) came
from. The stock `fvSolution` was restored from commit `eb687c56` before any run below and verified
byte-identical to the untouched tutorial's (`/home/ubuntu/dafoam-tutorials/UBend_Channel/system/
fvSolution`); the tightened file is kept alongside as `system/fvSolution.tightened_2026-07-30`.
`system/controlDict` was already byte-identical to the tutorial's (`endTime 1000`). Confirmation
that the restore worked: the primal below reproduces this document's original converged values
**bit-for-bit** -- `TP1=8.811838267130871e+01`, `TP2=3.577316633196290e+01`,
`OBJ.val=5.234521633934580e+01` -- and the adjoint reproduces the original 27-component analytic
vector to all 8 printed digits (`0.23711358, -0.43555559, -0.41765751, 1.96883727, ...`).

### Test 1: `mesh.warpDeriv` under the real `d(OBJ.val)/dXv` seed

New script `probeA5RealSeed.py`, A5's analog of A1's `probeWarpDerivRealSeed.py` +
`probeHandComposition.py`, run as one script so all quantities come from one model instance and one
captured seed. It builds the exact `Top` model from `runScript.py` (all 6 DV groups, same
`daOptions`, same `meshOptions`, same `OBJ = TP1 - TP2` ExecComp), runs the real primal, runs ONE
real reverse-mode adjoint (`compute_totals(of=["OBJ.val"], wrt=["shapexUpper"])`), and captures the
real seed with a monkeypatched hook on `dafoam.mphys.mphys_dafoam.DAFoamWarper.compute_jacvec_product`
-- the literal `dxV` the real adjoint chain hands to `self.DASolver.mesh.warpDeriv(dxV)`. The hook
fired **exactly once** (`captured 1 rev-mode call(s)`, `||.||_2 = 5.81214119e+03`), so the captured
vector is unambiguously the one real vector used, not an average.

Three quantities per component, all with `w = w_real`:

```
AN       = <warpDeriv(w_real), dXs/dShape_idx>            (hand-composed chain)
FD_dvgeo = <w_real, [Xv(shape+h e) - Xv(shape-h e)]/2h>   (FD through DVGeo.update)
FD_xs    = <w_real, [Xv(xs0+h eta) - Xv(xs0-h eta)]/2h>   (FD with DVGeo BYPASSED)
```

`np=4` (matching this case's own `decomposeParDict`), `--cpus=4 --memory=6g`, 30 s wall
(08:23:06Z -> 08:23:36Z, 2026-07-31), preflight passed clean, `processor*` cleared first. Raw log:
`demo-output/website/dafoam/a5_realseed_np4_run1.log`.

| idx | AN = framework | FD_xs (real seed, `DVGeo` bypassed) | rel. err | sign | established `check_totals` rel. err | established sign |
|---|---|---|---|---|---|---|
| 2 (control) | -4.176575101804e-01 | -4.068801538845e-01 | **2.65%** | agree | 1.1% | agree |
| 3 | 1.968837269006e+00 | 7.086230595114e-01 | **177.84%** | agree | 179.2% | agree |
| 8 (FLIP) | -8.433725799274e-01 | 7.878983424005e-01 | **207.04%** | **FLIPPED** | 207.6% | **FLIPPED** |
| 15 (largest component) | -1.386041672615e+01 | -2.425642941732e+01 | **42.86%** | agree | 42.9% | agree |
| 17 (FLIP) | -6.288120537154e-01 | 2.913155666635e+00 | **121.59%** | **FLIPPED** | 121.6% | **FLIPPED** |
| 26 (control) | -1.956539769317e+00 | -1.899175267081e+00 | **3.02%** | agree | 2.7% | agree |

**A solve-free, pure-geometry test of one function reproduces the entire full-chain CFD+adjoint
`check_totals` disagreement, component by component, across a range spanning 2.6% to 207%, including
both sign flips, for all six components tested.** Under the random seeds used previously, idx8 and
idx17 measured 0.32-1.30% at this same link and were declared clean. Under the real seed they
measure 207% and 122%, sign-flipped. That is a 160x change in the measured error produced by nothing
but replacing an arbitrary direction with the objective's own.

Three further readings from the same run:

1. **Hand-composition equals the framework exactly.** `AN` (hand-composed by this script's own
   arithmetic from `warpDeriv(w_real)` and `DVGeo.totalSensitivityProd`) matches the framework's own
   `compute_totals` column to a relative difference of **0.0 to 2.1e-15** for every component. This
   is A1 `PROOF.md` section 21.1's Stage-1 test, repeated here: **OpenMDAO's multi-component linear
   solve performs the same chain-rule contraction a manual replay does. There is no bug in the
   assembly.** It also validates the seed capture -- a wrong or partial seed could not reproduce the
   framework's own answer to machine zero.
2. **`DVGeo` nonlinearity is excluded again, now under the real seed.** `FD_dvgeo` and `FD_xs`
   (the latter never calling `DVGeo.update()` at all) agree to `3.8e-8` - `1.2e-6` at `h=1e-4`. The
   disagreement is not the FFD parameterization; it is the warp.
3. **The independent cross-check A1's section 17.2 used, repeated here, passes.** `FD_xs` is a
   geometry-only quantity computed by a script that did not exist when this document's original
   `check_totals` sweep ran, at a different step size, by a different method. It nonetheless
   reproduces that sweep's measured FD column to **0.07% - 1.5%** for all six components:

   | idx | `FD_xs` (this run) | established `check_totals` FD (step=1e-4) | agreement |
   |---|---|---|---|
   | 2 | -0.40688 | -0.41319 | 1.5% |
   | 3 | 0.70862 | 0.70507 | 0.50% |
   | 8 | 0.78790 | 0.78391 | 0.51% |
   | 15 | -24.25643 | -24.27272 | 0.067% |
   | 17 | 2.91316 | 2.90530 | 0.27% |
   | 26 | -1.89918 | -1.90572 | 0.34% |

   Two independent measurements of "the true derivative", one requiring 55 primal re-solves and one
   requiring none, agree to within 1.5%. The framework's analytic answer is the outlier, by the same
   margin, for the same components.

**Step-size check (one of the two probe-failure signatures this investigation has been burned by):**
every component was run at `h=1e-4` and `h=1e-5`. The relative errors move by less than 0.03
percentage points between them (e.g. idx8: 207.0408% vs 207.0487%; idx17: 121.5853% vs 121.5879%).
**No step-size instability. Not a noise artifact.**

**Implausible-constant-ratio check (the other signature):** `AN/FD_xs` is -1.0704 (idx8), -0.2159
(idx17), 2.7784 (idx3), 0.5714 (idx15), 1.0265 (idx2), 1.0302 (idx26) -- six different values, none
matching this case's `normalizeStates` constants (8.4, 35.28, 1e-3, 300) or any other scaler in the
setup. **Not a units-convention artifact of the kind that closed the `dR/dW` lead.**

### Test 2: the two links either side of `warpDeriv`, so the localization is not by elimination alone

New script `probeA5DObjDXv.py`, serial (`np=1`), 08:25:55Z -> 08:28:10Z, log
`demo-output/website/dafoam/a5_dobjdxv_np1_run1.log`.

**`dXs/dShape` (Stage A): machine precision, componentwise.** `DVGeo.totalSensitivityProd`'s
analytic column vs a central FD of `DVGeo.update()`, compared **componentwise over all surface
points** rather than as a contracted scalar (a scalar dot product can hide a componentwise defect
that happens to be orthogonal to the contraction direction -- the exact failure mode that made A5's
original warpDeriv clearance wrong, so it is deliberately not repeated here):

| idx | h | max abs diff | max rel |
|---|---|---|---|
| 8 | 1e-4 | 1.085e-12 | **3.32e-12** |
| 8 | 5e-5 | 2.007e-12 | **6.13e-12** |
| 17 | 1e-4 | 1.048e-12 | **3.20e-12** |
| 17 | 5e-5 | 2.109e-12 | **6.44e-12** |
| 2 | 1e-4 | 9.064e-13 | **2.79e-12** |
| 2 | 5e-5 | 2.030e-12 | **6.24e-12** |

**`dObj/dXv` (Stage B): clean at the flagged components.** `AN = <w_real, delta_Xv>` against
`FD = [OBJ(Xv0 + h*delta_Xv) - OBJ(Xv0 - h*delta_Xv)] / 2h`, where each `OBJ()` is a **full nonlinear
primal re-solve at a directly-set volume mesh** (`DASolver.setVolCoords`), bypassing `DVGeo` and
IDWarp entirely on the FD side. The objective is read back two ways at every solve --
`solver.calcFunction()` (live) and `evalFunctions()` (the time-history getter that produced this
document's earlier retracted `dF/dW` bug) -- and they agreed to `0.000e+00` at all 14 solves, so that
ambiguity is closed rather than assumed away.

| idx | h | AN | FD (true re-solve) | rel. err | sign |
|---|---|---|---|---|---|
| 8 (FLIP) | 1e-4 | 7.870912e-01 | 7.940838e-01 | **0.88%** | agree |
| 8 (FLIP) | 5e-5 | 7.870927e-01 | 7.884142e-01 | **0.17%** | agree |
| 17 (FLIP) | 1e-4 | 2.912138e+00 | 2.931680e+00 | **0.67%** | agree |

### Two controls run on the probe itself, because the first sweep did NOT come back clean everywhere

The same sweep gave `rel_err = 56.7%` for idx17 at `h=5e-5` and 390% / 268% for idx2 at both steps.
Per the standing rule that a probe's own instability is the first suspect, two controls were run
before reporting anything.

**Control 1 -- the noise floor, measured rather than argued.** This document has hypothesized since
its first version that the residual plateau (`p initRes ~ 2.26e-4`) makes FD differencing noisy.
`probeA5NoiseFloor.py` tested it directly: re-solve the **identical, unperturbed** `Xv0` four times,
interleaved with scrambled solves so the warm-start path differs between repeats exactly as it does
in a real FD sweep (08:31:04Z -> 08:32:31Z, log `a5_noisefloor_np1_run1.log`):

```
A5NOISEFLOOR n=4 vals=[52.345227439913 52.345227439915 52.345227439912 52.345227439914]
             spread_max_min=2.849276e-12  std=1.034480e-12
             implied FD noise at h=1e-4 = 1.424638e-08
```

**The primal is reproducible to 2.8e-12, so the FD noise floor on the derivative is 1.4e-8.** That
is seven orders of magnitude too small to explain anything here. **The residual-plateau-noise
hypothesis, carried in this document since 2026-07-28 as candidate cause #1 and never measured, is
refuted by direct measurement.** The plateau is a genuine fixed point in the strongest sense: the
solver returns to the same 13 significant figures every time.

**Control 2 -- warm-start path dependence, found and corrected.** The four repeats above averaged
`52.345227439913` while OpenMDAO's own `run_model` gave `52.345216915593` -- a **reproducible**
offset of `1.05e-5`, not noise. Cause: in the sweep, each FD leg warm-starts from the *previous*
leg's converged state, so the `+` and `-` legs of a central difference travel different paths to
the limit cycle. `probeA5DObjDXvReset.py` resets every solve to the same captured baseline state
first (08:36:54Z -> 08:38:51Z, log `a5_dobjdxv_reset_np1_run1.log`). With the reset, the baseline
re-solve reproduces OpenMDAO to `-5.083e-10` (vs `1.052e-05` on the warm path), confirming the
diagnosis, and:

| idx | h | AN | FD (reset path) | rel. err | sign |
|---|---|---|---|---|---|
| 8 (FLIP) | 1e-4 | 7.870912e-01 | 8.004034e-01 | **1.66%** | agree |
| 8 (FLIP) | 5e-5 | 7.870927e-01 | 8.072198e-01 | **2.49%** | agree |
| 17 (FLIP) | 1e-4 | 2.912138e+00 | 2.882827e+00 | **1.02%** | agree |
| 17 (FLIP) | 5e-5 | 2.912078e+00 | 2.866879e+00 | **1.58%** | agree |
| 2 (control) | 1e-4 | -4.071165e-01 | -8.719458e-01 | 53.3% | agree |
| 2 (control) | 5e-5 | -4.071125e-01 | -1.297023e+00 | 68.6% | agree |

**idx8 and idx17 -- the two components the verdict rests on -- are stable and clean at 0.17-2.49%
across two step sizes AND two independent path protocols. That is the result being relied on.**

**idx2 is reported as a probe failure, not as a finding.** Its direct-`Xv` re-solve FD is
contaminated by an additive offset in the two-leg objective difference of ~+6.5e-5 (warm path) and
~-9e-5 (reset path) that is **constant in `h`** rather than scaling with it -- so it inflates the
relative error without bound as `h` shrinks, which is what the numbers show. A constant offset is
not a derivative error (a derivative error scales with `h` in the difference); it is a jump. Its
mechanism (most plausibly a discrete branch -- a limiter or wall-function switch -- toggling as soon
as the mesh moves along this particular direction) was not chased, and idx2's `dObj/dXv` is
therefore recorded as **not measurable by this probe**, neither clean nor defective. This does not
touch the verdict: idx2 is a control that agrees at 1.1% in the real `check_totals` and at 2.65% in
Test 1, and the verdict rests on idx8/idx17, where the probe is stable.

**Serial-vs-parallel cross-check, unplanned but worth recording:** Test 1 ran at `np=4` and Test 2
at `np=1`, on different partitionings, and the same quantity `<w_real, true dXv/dShape_8>` came out
`7.878983e-01` and `7.870912e-01` -- 0.10% apart -- while the framework's analytic answer was
`-8.433726e-01` and `-8.445469e-01` in the two runs. **The contradiction is present within a single
serial process, so it is not a decomposition artifact.**

### Verdict: same mechanism as A1, and the scope of the upstream bug is larger than filed

| link | test | result |
|---|---|---|
| `dXs/dShape` (DVGeo FFD Jacobian) | analytic column vs componentwise FD of `DVGeo.update` | **clean, 2.8e-12 - 6.4e-12** |
| `dXv/dXs` (`mesh.warpDeriv`) | dot-product identity, **real** `dOBJ/dXv` seed, `DVGeo` bypassed | **DEFECTIVE: 42.9% - 207%, two sign flips; reproduces the full-chain gap component-by-component** |
| `dObj/dXv` (state adjoint) | true re-solve FD at a directly-set `Xv` | **clean, 0.17-2.49% at idx8/idx17, two step sizes, two path protocols** |
| composition (OpenMDAO assembly) | hand-composed vs `compute_totals` | **exact, 0 - 2.1e-15** |

**A5's defect is the same defect as A1's: `mesh.warpDeriv` mis-linearizes the surface-to-volume mesh
warp. The lab has one upstream bug, not two.** The mechanism A1 established -- the defect reaches a
component's real gradient only where its location overlaps the objective's own `dObj/dXv`
sensitivity field -- is what hid it here: contracted against a random direction the error is
0.3-1.3%; contracted against the real pressure-loss adjoint's own sensitivity field it is 207%.

**What this adds to the upstream bug report's scope, all of it new:**

- **A second, unrelated geometry and flow regime.** A1 is an external 2D airfoil (`DASimpleFoam`,
  force objective, C-mesh from `pyHyp`). A5 is an internal 3D curved duct (`DASimpleFoam`,
  total-pressure-loss objective, 6-block `blockMesh` structured mesh, half-model with a symmetry
  plane). The bug is not a property of one mesh generator or one topology.
- **A different objective type.** A1's is a surface force integral; A5's is a difference of two
  total-pressure patch integrals at inlet and outlet -- an objective whose sensitivity field is
  distributed through the duct rather than concentrated at a stagnation point.
- **Plain single-point, single-axis design variables, with a SIGN FLIP.** A5's `shapexUpper` is
  built by `nom_addLocalDV(axis="x", pointSelect=PS)` -- one FFD control point moving along one axis
  per DV, unconditionally, with no opposing-direction or combination construction anywhere in the
  case. The upstream report currently says the sign-flipping failure requires the
  opposing-direction combination construction ("necessary for it to be large enough to flip sign, in
  the cases tested"). **A5 idx8 and idx17 are single-point single-axis DVs and they flip sign at
  207% and 122%. That qualification is now falsified and must be removed from the report.**
- **Symmetry-plane handling is not the discriminator.** This case runs `meshOptions
  ["symmetryPlanes"] = []` (an omission inherited from the official tutorial, not introduced here),
  A1 declares two. Both fail. The 2026-07-30 addendum above had already exonerated symmetry-plane
  proximity within A5 on geometric grounds; this is the cross-case version of the same point.

### What this addendum does NOT claim

- It does not explain *why* `warpDeriv` mis-linearizes, or where in IDWarp's reverse mode the error
  is. No IDWarp source was traced this session. The finding is that the function's output disagrees
  with a finite difference of the function it claims to differentiate.
- It does not revisit the earlier `dR/dW` work. That Jacobian was cleared to machine precision on
  and off the diagonal (2026-07-30 addendum) and nothing here contradicts it; it was simply not the
  defective link.
- It leaves the `dF/dW` scaling pattern (`AN/FD = 35.28` for `TP1`, `8.4` for `TP2`, exactly,
  direction-independent) **open and unexplained**. That test measured a different link with a
  different tool and its per-function constants are still uninterpreted; `getdFScaling` remains the
  named place to look. It is not needed for this verdict -- the `dObj/dXv` test above measures the
  composed objective sensitivity end-to-end against a true re-solve and finds it clean -- but it is
  not resolved by it either, and is left on the record as open.
- idx2's `dObj/dXv` measurement failed as described and is recorded as unmeasurable by that probe.

Evidence, all new this session (2026-07-31), all in
`ladder-a/A5_work/UBend_Channel_pressureloss/` unless noted:
`probeA5RealSeed.py`, `probeA5DObjDXv.py`, `probeA5NoiseFloor.py`, `probeA5DObjDXvReset.py`, and
four raw logs in `demo-output/website/dafoam/`: `a5_realseed_np4_run1.log`,
`a5_dobjdxv_np1_run1.log`, `a5_noisefloor_np1_run1.log`, `a5_dobjdxv_reset_np1_run1.log`.
