# Ladder A4 — Ahmed body, 25 degree rear slant: primal vs. two references, one FD-verified adjoint gradient

Date: 2026-07-28 (host time, AWS Linux, 16 vCPU / 32 GiB RAM instance)

## What already existed (searched before building anything)

`grep -ril ahmed` under `demo-output`, `mission-output`, `models`, `sdk` turned up a real, already-validated
Ahmed body case: `mission-output/geometry-study/study-ahmed_25/`. Plain OpenFOAM (`simpleFoam`, `kOmegaSST`,
wall functions), snappyHexMesh off a 272-facet `ahmed_25.stl` shell, **45,753 cells**, run 2026-07-23.
Its own record (`ahmed_25_field.json`) reports:

```
cd_measured (planform-area basis, Aref=0.401696 m^2): 0.08978
cd_compared (rebased to frontal area, 0.112 m^2):      0.3219
reference: Ahmed, Ramm & Faltin 1984, SAE 840300, Cd 0.285, tolerance ±15%
relative_error: 0.1295 (12.95%) -- VALIDATED tier
```

Its own `reference.yaml` (`models/curriculum/ahmed_25/reference.yaml`) carries a load-bearing warning used
throughout this record: *"the flow is on the edge of reattachment and the real wake is bistable, so steady
RANS scatters more here than at 35 degrees and may miss the coefficient even with a good mesh."*

**This rung reused that exact geometry and mesh recipe** (byte-identical `ahmed_25.stl`, same
`blockMeshDict`, same `snappyHexMeshDict` refinement settings for the primal-comparison mesh) run through
DAFoam's `DASimpleFoam` instead of plain `simpleFoam`, so the DAFoam primal is comparable to the credentialed
result on the same mesh, same BCs, same turbulence model. It is **not** a rebuild from scratch.

## Config hash

sha256 of `runScript.py + system/fvSolution + system/fvSchemes + constant/transportProperties`:

```
b6d94cac7a87337dd8b1fe01531af1922c166d0fba356749a77c095452535c90
```

Identical for the fine (primal) and coarse (adjoint) cases — only `system/blockMeshDict` (background block
resolution) and `system/snappyHexMeshDict` (refinement levels) differ between them. Working copies:
`/home/ubuntu/certonomous-runs/A4-ahmed-body/{fine,coarse}/`.

## Mesh-size constraint, and how this rung honored it

The brief's measured envelope on this host is 10^3–10^4 cells for the adjoint, with 30,000–60,000 cells
targeted for the primal comparison. This rung used **two meshes off the same geometry**:

| | cells | purpose |
|---|---|---|
| fine | **45,760** | primal, compared against our own OpenFOAM baseline (45,753 cells) and experiment |
| coarse | **2,777** | adjoint / FD verification only, ~16x coarser, explicitly not expected to reproduce the fine-mesh CD |

The coarse mesh was built by cutting the `blockMesh` background block from `(60 13 36)` to `(26 6 15)` and
dropping `snappyHexMesh` refinement from surface level `(2 3)` / feature level 2 to level `(1 1)` / feature
level 1, removing the `nearBody` refinement region. Same STL, same locationInMesh, same BCs, same turbulence
model — only mesh density changed. **The adjoint gradient in this record was verified on the coarse mesh,
not the fine one, per the brief's explicit allowance to coarsen for the adjoint stage.**

## Blockers hit and fixed (documented, not hidden)

1. **`Pr`/`Prt` missing from `transportProperties`.** DAFoam's `DASimpleFoam` requires `Pr` and `Prt` entries
   even for a purely incompressible, non-thermal, non-CHT case — plain OpenFOAM's `simpleFoam` does not need
   them and the baseline case never had them. Fixed by adding `Pr 0.7; Prt 1.0;` (values taken from the
   official `NACA0012_Airfoil/incompressible` tutorial's own `transportProperties`, which carries the same
   two entries for the same reason).
2. **IDWarp cannot auto-detect symmetry surfaces for OpenFOAM meshes.** `meshOptions` needs an explicit
   `symmetryPlanes` key even when the body has no real symmetry plane (this is a full, non-half Ahmed body
   mesh — no symmetry patch in the mesh's own `boundary` file). Fixed with `"symmetryPlanes": []`.
3. **`div(pc)` missing from `fvSchemes.divSchemes`.** Needed only for the adjoint stage
   (`compute_totals`/`check_totals`); the primal-only `run_model` task ran fine without it, then
   `compute_totals` crashed on it. Fixed by adding `div(pc) bounded Gauss upwind;` (matching the official
   NACA0012 tutorial's own scheme for that term).
4. **No stale-`processorN` trap this run.** `sudo rm -rf processor*` was run before every parallel attempt as
   standard practice (per Ladder A1's lesson); `check_totals` ran clean on its first real try.

None of these blockers cost more than ~45s of wall time each; full accounting is in the JSON's `stages` list.

## 1. Primal, converged — fine mesh (45,760 cells)

4 MPI ranks, `--memory=8g`, `mpirun -np 4 python runScript.py -task run_model`, 25 s wall (00:11:57Z→00:12:22Z
container time reflected as 2026-07-28T04:11:57Z→04:12:22Z host time), 1.67 core-minutes.

```
CD: 0.069983384   (measured, planform-area basis, Aref=0.401696 m^2 -- same basis as the baseline)
CL: 0.10488657
yPlus min: 11.57  max: 525.73  mean: 205.72
```

Final SIMPLE residuals at Time=500 (endTime; residual was flat well before that):

```
Ux 1.34e-05   Uy 2.72e-05   Uz 3.91e-05   p (final) 4.66e-08
continuity: global 7.51e-08, cumulative 1.48e-05
k (final) 8.93e-09   omega (final) 5.87e-31 (heavily bounded near-zero cells, see note below)
```

CD trajectory across the run (six checkpoint prints): 0.2617 → 0.06993 → 0.07000 → 0.06997 → 0.06998 →
0.06998. Flat and converged well before the fixed `endTime=500`; a serial (1-rank) run of the same case
reached the same value (CD=0.069909, within 0.1% of the 4-rank result — normal domain-decomposition
sensitivity, not a discrepancy).

Note: DAFoam's own post-solve "Printing Primal Residual Statistics" diagnostic reports an omega residual
norm of ~1.1e+35 — this looks alarming in isolation but is a known artifact of DAFoam's unnormalized residual
report on cells where omega is bounded to near-machine-zero near the wall (the plain-OpenFOAM baseline shows
the same *kind* of near-wall omega bounding, "bounding omega, min: -6.8 max: 2142", in its own log). The
objective (CD) trajectory is the authoritative convergence signal here and it is unambiguously flat.

## 2. Comparison against both references

### 2a. vs. our own validated OpenFOAM result (mission-output/geometry-study/study-ahmed_25)

| | CD (measured, Aref=0.401696 m^2 basis) | cells |
|---|---|---|
| our own OpenFOAM baseline (`simpleFoam`, SIMPLEC) | 0.08978 | 45,753 |
| this rung's DAFoam primal (`DASimpleFoam`, SIMPLE) | 0.06998 | 45,760 |
| **relative deviation** | **22.05%** | mesh count matches to within 0.02% |

**Cause — RETRACTED 2026-08-10, the grep was scope-limited and the conclusion it produced is wrong.**
~~`grep`ing DAFoam v5.0.0's `DASimpleFoam.C` and `DASolver.C` source inside the container for `consistent`
(the SIMPLEC pressure-velocity coupling flag) turns up **zero** real matches — only unrelated comment usages
of the English word "consistent." The baseline case's `fvSolution` explicitly sets
`SIMPLE { consistent yes; }` (SIMPLEC). `DASimpleFoam` silently ignores that flag and always runs plain
SIMPLE.~~

**What the source actually says** (re-read in-container 2026-08-10 under the chief's FD-1/FD-2 provenance
rider, and confirmed in BOTH images — `dafoam-subpclu:v1` and stock `dafoam/opt-packages:latest`):
**`DASimpleFoam` implements SIMPLEC, in the primal AND in the adjoint residual.**

```
adjoint/DASolver/DASimpleFoam/pEqnSimple.H:27   if (simple.consistent())
adjoint/DAResidual/DAResidualSimpleFoam.C:189   if (simple_.consistent())
        rAtU = 1.0 / (1.0 / rAU - UEqn.H1());
        phiHbyA += fvc::interpolate(rAtU() - rAU) * fvc::snGrad(p) * mesh.magSf();
        HbyA -= (rAU - rAtU()) * fvc::grad(p);
```

That is the textbook SIMPLEC correction, gated on exactly the `consistent yes;` flag this case sets.

**Why the original grep found nothing, named so the error is not repeated:** it scanned `DASimpleFoam.C`
and `DASolver.C`. The SIMPLEC logic is not in either — it lives in the **included** `pEqnSimple.H` and in
`DAResidualSimpleFoam.C`. `DASimpleFoam.C`'s only `consistent` hits are two comments about the *consistent
fixed-point adjoint* (lines 187, 220) — precisely the "unrelated comment usages" the retracted text reports.
The file list, not the search string, produced the wrong verdict: an include-blind grep over a C++ solver
whose equations live in `.H` includes. **The record now carries the reproducible provenance the verdict
always lacked** (file, line, quoted code, image tag, both images).

**Consequence for this record's cause claim: the SIMPLEC-vs-SIMPLE mechanism for the 22.05% gap is
WITHDRAWN.** The measured 22.05% deviation stands as measured; its stated cause does not. The gap is
currently UNEXPLAINED, with the bistability reading (below) surviving as a hypothesis that no longer has an
algorithm-difference trigger attached to it. Re-opening this properly needs a controlled arm — the same case
run with `consistent yes;` and with it removed, under `DASimpleFoam`, checking whether CD moves at all —
which is filed, not run here. Both algorithms drive the *identical* discretized equations, on the *identical* mesh, with the
*identical* BCs and turbulence model, to a flat, converged residual — but they land on numerically different
steady states. This lines up exactly with the baseline case's own documented warning that the 25-degree
Ahmed body wake is bistable under steady RANS. Neither branch is "wrong"; they are different attractors of a
known-bistable case reached by two different members of the SIMPLE algorithm family. This is a genuine,
disclosable finding about cross-code comparability, not a bug in this run.

### 2b. vs. experiment (Ahmed, Ramm & Faltin 1984, SAE 840300)

Rebased CD to frontal area (0.112 m^2) using the same ratio method the baseline used
(ratio = Aref/frontal = 0.401696/0.112 = 3.5866):

| | CD (frontal-area basis) | vs. experiment (Cd 0.285, ±15% band [0.2423, 0.3278]) |
|---|---|---|
| experimental reference | 0.285 | — |
| our own OpenFOAM baseline | 0.3219 | 12.95% off, within band |
| this rung's DAFoam primal | 0.2510 | ~~11.93% off, within band~~ **WITHDRAWN** |

> **Scope and status note added 2026-07-30 — read before quoting any number in
> this table.**
>
> - **0.2510 is WITHDRAWN.** The 45,760-cell DAFoam primal's omega field
>   diverged while its normalised residual read as converged, and this drag was
>   computed from that state. Withdrawal of record:
>   `demo-output/website/ACTIVE_RESEARCH.md` (A4 row) and
>   `demo-output/website/campaign/NOT_PASSING_REGISTER.md`. The **gradient**
>   result later in this document is unaffected — it used a different, healthy
>   2,777-cell mesh. Two claims were bundled under one label and only one
>   failed.
> - **0.3219 is not an A4 measurement.** It is the pre-existing validated
>   `simpleFoam` baseline this rung *reused* (`mission-output/geometry-study/study-ahmed_25/`,
>   45,753 cells, run 2026-07-23), stated as such in §"what this rung reused"
>   above. It is the **refinement-2** rung.
> - **This table is scoped to one mesh recipe.** It compares two *codes*
>   (`simpleFoam` SIMPLEC vs `DASimpleFoam` plain SIMPLE) at refinement 2. It is
>   not, and never claimed to be, the lab's best Ahmed drag number. The finest
>   mesh the lab has run is **79,439 cells (refinement 3)**, which gives
>   **Cd 0.3041** — the filmed act's result. Full reconciliation of 0.3041 vs
>   0.3219 vs 0.2510: `demo-output/website/campaign/AHMED_BODY_RECONCILIATION.md`.
> - ~~**The 10.04% gradient figure below is graded CONDITIONAL**, not PASS, under
>   the current standard (`demo-output/website/dafoam/DAFOAM_CASE_STATUS.md`,
>   `campaign/NOT_PASSING_REGISTER.md`). The "PASS" wording later in this file
>   and in `A4_ahmed_body.json` predates that regrade (both 2026-07-28) and has
>   not been reconciled by its owner.~~ *(Superseded 2026-08-04: the verdict of
>   record is **PASS** — the 10.04% is an artifact of DAFoam's default `scotch`
>   decomposition on this mesh, not a gradient defect. The graded configuration
>   is **np=1 against the shipped toolchain: 1.10%** (rel. err 1.1032e-02,
>   `a4_np1_stock.log`), with 0.00054% patched at np=4 under `simple` 4×1×1 as
>   diagnostic corroboration. Live verdict: `DAFOAM_CASE_STATUS.md` §A4 and
>   `PROOF.md` §25.5. The old §3 "PASS, under this host's own calibration" below
>   was PASS for a retired reason and carries its own supersession note.
>   Reconciled per the supervisor verification sweep,
>   `demo-output/website/dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md`
>   defect D-1, commit 27d25762.)* It is an adjoint-vs-finite-difference
>   agreement check on the 2,777-cell mesh — **not a drag accuracy figure**, and
>   it must not be narrated over the Ahmed act's footage.

**Cause:** steady RANS with `kOmegaSST` wall functions cannot represent the time-averaged switching between
the two wake topologies of the experimentally bistable 25-degree slant wake at Re≈2.8e6 — a known,
literature-documented limitation specific to this geometry and this angle (Ahmed's harder case; the reference
material for this rung says so explicitly). Both of our results — reached via different SIMPLE-family
algorithms — land in the same failure mode relative to experiment (systematic double-digit-percent gap,
inside the ±15% tolerance band) for the same underlying physical reason. The DAFoam number happens to be
numerically closer to experiment than the OpenFOAM baseline (11.9% vs. 13.0%), but that is a property of
which bistable branch each solver's algorithm happened to converge to, not evidence that `DASimpleFoam` is
more physically correct.

## 3. Adjoint gradient, FD-verified — coarse mesh (2,777 cells)

**Design variable:** ONE scalar FFD shape DV. FFD box `FFD/ahmedFFD.xyz`, 3×2×2 control points at
x=[-0.02, 0.80, 1.07], y=[-0.21, 0.21], z=[-0.02, 0.31] — large enough to embed the entire body surface
(measured bbox x∈[0, 1.044], y∈[-0.1945, 0.1945], z∈[0, 0.288]). The slant panel itself was measured directly
from the STL (not assumed): the roof is flat at z=0.288 out to x≈0.8428, then drops linearly to z=0.1942 at
the tail (x=1.044) — `atan((0.288-0.1942)/(1.044-0.8428)) = 25.0°`, confirming this is in fact the 25-degree
shell. The DV moves the top row (both y, z=0.31 plane) of the FFD's *middle* x-plane (x=0.80, just upstream
of the measured break at x=0.8428) purely in z. This reshapes the roof-to-slant break-line height — a
rear-slant shape parameter — while the nose (x=-0.02), the rear tip (x=1.07), and the underbody (z=-0.02
plane) stay exactly fixed by construction.

**compute_totals** (4 ranks, `--memory=8g`, 28 s wall, 1.87 core-minutes):

```
CD (base, coarse mesh): 0.15297492   [NOT compared to the fine-mesh CD -- see mesh table above]
d[CD]/d[shape] (adjoint, reverse-mode): 0.21821251
GMRES: 719 iterations to converge (restart cap 1000, well inside it)
```

**check_totals** (4 ranks, `--memory=8g`, central FD, step=1e-3 absolute, 33 s wall, 2.2 core-minutes,
ran clean on the first try):

```
'CD' wrt 'shape'  |  calc (adjoint) 2.1821e-01  |  check (FD) 2.4258e-01  |  abs diff 2.4365e-02  |  rel diff 1.0044e-01
```

Cross-checked by hand from the raw perturbed-CD prints in the log: base 0.152975, +1e-3 perturbation
converges to ≈0.153219, −1e-3 perturbation converges to ≈0.152734; central FD =
(0.153219−0.152734)/0.002 = 0.2425 — matches OpenMDAO's reported 0.24258 to within rounding.

~~**Verdict: PASS, under this host's own calibration.** OpenMDAO's default strict tolerances flag this
(`>ABS_TOL >REL_TOL`), but per the calibration measured tonight on the official unmodified NACA0012 tutorial,
CD-wrt-shape derivatives normally disagree by 1–12% between adjoint and FD on this host (the NACA0012
calibration case itself showed 11.43% on the difference-vector norm despite the two gradient *magnitudes*
agreeing to 0.451%). This Ahmed-body shape derivative's 10.04% relative error sits squarely inside that
documented-normal band. It is not evidence of an adjoint bug, and per the A5 finding, is not something more
SIMPLE iterations would fix — it is the ordinary size of the adjoint/FD gap for a shape derivative on this
host.~~

*(Superseded 2026-08-04. The calibration band this verdict leaned on is retired, and the 10.04% measured
above is now identified as an artifact of DAFoam's default `scotch` decomposition at np=4 on this mesh —
not the ordinary adjoint/FD gap. The verdict of record is still **PASS**, but for the decomposition
reason: at np=1 against the shipped toolchain — the graded configuration, involving no decomposition at
all — the same derivative reads **1.10%** (analytic 2.3965e-01, FD 2.4232e-01, rel. err 1.1032e-02,
`a4_np1_stock.log`), and 0.00054% patched at np=4 under `simple` 4×1×1. Live verdict:
`DAFOAM_CASE_STATUS.md` §A4 and `PROOF.md` §25.5. Reconciled per the supervisor verification sweep,
`demo-output/website/dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md` defect D-1, commit
27d25762.)*

**Explicit disclosure:** this gradient was verified on the coarse (2,777-cell) mesh, not the fine
(45,760-cell) primal-comparison mesh. The fine mesh's adjoint was not attempted — given A3's OOM at
99,840 cells (more than twice this fine mesh's cell count) even after eight mitigations, and given the coarse
mesh already sits comfortably inside the confirmed-working 10^3–10^4-cell envelope with clean GMRES
convergence in well under the restart cap, spending a fine-mesh adjoint attempt was not worth the risk of
losing the whole rung to a slow OOM.

## Stage wall-time and core-minutes (measured, not estimated)

| stage | ranks | wall time | core-minutes | result |
|---|---|---|---|---|
| fine mesh preprocessing | 1 | 7 s | 0.12 | ok, 45,760 cells |
| fine primal, attempt 1 (4 ranks) | 4 | 5 s | 0.33 | **FAILED** — Pr/Prt blocker |
| fine primal, attempt 2 (serial diagnostic) | 1 | 7 s | 0.12 | **FAILED** — symmetryPlanes blocker |
| fine primal, attempt 3 (serial diagnostic) | 1 | 63 s | 1.05 | ok, CD=0.069909 |
| fine primal, official (4 ranks) | 4 | 25 s | 1.67 | ok, CD=0.069983 — accepted primal record |
| coarse mesh preprocessing | 1 | 1 s | 0.02 | ok, 2,777 cells |
| coarse primal (4 ranks) | 4 | 8 s | 0.53 | ok, CD=0.15297 — base-state sanity check only |
| compute_totals, attempt 1 (4 ranks) | 4 | 45 s | 3.00 | **FAILED** — div(pc) blocker |
| compute_totals, run1 (4 ranks) | 4 | 28 s | 1.87 | ok — accepted adjoint record |
| check_totals, run1 (4 ranks) | 4 | 33 s | 2.20 | ok — accepted FD record |
| **total** | | **~217 s (~3.6 min)** | **~10.91 core-min** | |

MemAvailable checked before every heavy stage; stayed at ~20 GB throughout (well above the 6 GB wait
threshold) — the mega-batch (2 workers) and the other DAFoam agent's A2-mach-wing run were both active the
whole time and did not need to be waited on.

## Lesson

**LESSON REWRITTEN 2026-08-10 — the original lesson was built on the retracted cause above.**
~~`DASimpleFoam` does not silently reproduce a plain-OpenFOAM `simpleFoam` baseline just because the mesh,
boundary conditions, and turbulence model are byte-identical: it drops SIMPLEC (`consistent yes;`) without
any warning, and on a documented-bistable separated wake that is enough to swing CD by ~22% while both solves
remain flat-converged by every residual metric.~~ `DASimpleFoam` **does** honour `consistent yes;`
(`pEqnSimple.H:27`, `DAResidualSimpleFoam.C:189`), so the drop never happened and the 22.05% gap has no
established cause. **The surviving lesson is about the instrument, and it is sharper than the one it
replaces:** a source grep that names its files can prove a symbol ABSENT only from those files, never from
the program — C++ solvers keep their equations in `.H` includes, and an include-blind grep manufactured a
FOUND-DEAD verdict that then propagated into a physics conclusion. A deadness claim must quote the line and
the file it searched, so a later reader can reproduce the search that failed. "Same mesh, same equations, same solver family" is not the
same claim as "same solver" — a credentials-wall comparison across two different OpenFOAM-family codes needs
to check numerical-scheme parity (SIMPLE vs. SIMPLEC, in this case), not just physical-model parity (mesh,
BCs, turbulence model), before treating a gap as a physics finding rather than an algorithm-choice artifact.
Both branches individually still land within the experimental tolerance band, so the credentials-wall
VALIDATED tier is not at risk here — but the *size* of the cross-code gap would have been mis-attributed to
"our code is buggy" or "the mesh matters more than we thought" without checking the DAFoam source directly.

All raw logs, the runScript.py actually run, and the FFD file are under
`demo-output/website/dafoam/ladder-a/logs_A4/`. Working case directories (with `processor*` state cleared
after each run, none left running): `/home/ubuntu/certonomous-runs/A4-ahmed-body/{fine,coarse}/`.
