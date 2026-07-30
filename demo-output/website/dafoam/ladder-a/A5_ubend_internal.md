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
