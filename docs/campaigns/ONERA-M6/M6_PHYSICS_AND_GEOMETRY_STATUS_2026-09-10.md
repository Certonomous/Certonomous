# ONERA M6 — where the physics was good, where it was not, and what the source actually says

**Date:** 2026-09-10. **Author:** cfd `lab-lane`, for the cfd-supervisor.
**Status:** factual note. **No verdict is issued here and none is changed here.**
Every number below cites an artifact still on disk, or says plainly that it does not.

---

## 1. THE ANSWER, IN ONE LINE

**The run where the physics was good is the N1 rung of M6CP1:**

```
verification/runs/M6CP1_runs/L2_N1/smoke/
```

**Its PRESSURE lift coefficient is `Cl_pressure = +0.191505`** — inside the
`[0.15, 0.45]` band that appears in M6CP1's own record (but see §4, which is a caveat
on that band, not on the number). **Everything that went wrong went wrong in the
VISCOUS loads.**

---

## 2. 🔴 NAME THE RUN PRECISELY — TWO CONFUSIONS TO AVOID

**This is the N1 rung, not the M0 baseline, and not the PRD case.**

| | run | pressure Cl at step 400 | against the `[0.15, 0.45]` band |
|---|---|---|---|
| ✅ **the good one** | `verification/runs/M6CP1_runs/L2_N1/smoke/` — **the N1 rung, `transonic yes`** | **+0.191505** | **INSIDE** |
| ❌ **not this one** | `verification/runs/M6CP1_runs/L2/smoke_M0_baseline/` — the M0 baseline | **+0.053689** | **BELOW** |

**Do not read "the M6 physics was fine" as a statement about the baseline.** At the same
step count the baseline's pressure Cl sits below the band. Only N1's is in it.

**And this is not the PRD result.** The Ergun agreement to **0.035 %** belongs to the
**PRD** porous-radiator case, on a sound mesh. **M6 is the case with the cusped mesh.**
The two are different cases, different families and different meshes, and the M6 story
is *"good pressure loads on a bad mesh"*, not *"a good result"*.

---

## 3. WHAT WAS GOOD AND WHAT WAS NOT

**Both figures below were re-derived by this lane tonight**, directly from
`L2_N1/smoke/400/p` and `constant/polyMesh`, by integrating pressure over the 1,560
faces of the `wing` patch and projecting onto the registered
`liftDir = (−0.053381689758760474, 0.9985741811195098, 0)` with the case's own
`rhoInf = 1.224978126`, `magUInf = 285.679356`, `Aref = 0.7532`
(`L2_N1/smoke/system/controlDict:45-53`):

| quantity | value | source |
|---|---|---|
| **pressure lift, N1** | **`Cl_pressure = +0.191505`** | re-derived from `400/p` |
| pressure drag, N1 | `Cd_pressure = +0.086867` | re-derived from `400/p` |
| **total drag, N1 (the runaway)** | **`Cd_total ≈ 1.52`** | `M6CP1_PREREGISTRATION.md:555` |
| pressure lift, M0 baseline | `+0.053689` | re-derived from `400/p` |

**So roughly 94 % of N1's drag is the viscous term, and the viscous term is an
artifact, not a measurement.** The pressure integral — the part of the solution that
carries the transonic shock structure and the loading — came out sane on a mesh that
was not.

**What was NOT good, all of it viscous or numerical:**

- **Cells reaching `5.1e10 m/s`** (`M6CP1_PREREGISTRATION.md` §A2.4).
- **The LTS time-scale field collapsed nine decades over 400 steps** — healthy at
  `1.486e-07 s` at t = 1, down to `8.584e-13 s` on N1 and ultimately `1e-16 s`
  (§A2.3). §4.4 of that registration had **registered that LTS owed a
  time-step-independence demonstration; it was never paid**, and this is what it would
  have caught.
- **`y+` maximum grew to `1.886e10`** while the **minimum held at 8.65 across every
  write** — the signature of a wall-shear artifact localised somewhere specific rather
  than a globally bad mesh.
- **The cause was the trailing edge.** M6CP1's TE closes to a single point with **zero
  cells across it** and a cusp half-angle of **60.9°, scale-invariant across three
  levels** — refinement never opened it (§A2.2).

---

## 4. TWO HONEST CAVEATS, BECAUSE THEY BEAR ON HOW MUCH THE +0.1915 IS WORTH

**(a) The pressure/viscous split had no artifact on disk until tonight.**
`L2_N1/smoke/postProcessing/forceCoeffs/0/coefficient.dat` carries **totals only** —
the `forceCoeffs` function object as configured writes no pressure/viscous
decomposition, and there is no `force.dat` in that tree. So `+0.1915` was of record
only in the prose of `M6CP1_PREREGISTRATION.md:554`, citing no file. **This lane
re-derived it from the field data and reproduces it to six significant figures
(0.191505), and reproduces the baseline's `+0.05368879024` as 0.053689.** The record's
numbers are sound. They simply had no re-derivable artifact behind them, and now the
method to re-derive them is written down here.

**(b) This lane could not locate a PRE-COMPUTE registration of the `[0.15, 0.45]`
band.** It appears exactly twice in `M6CP1_PREREGISTRATION.md`, at lines **554 and
805**, both times inside **Amendment 2**, which is post-compute, and both times
described as *"this registration's own band"*. It is **not** in §5 GATES, whose
registered gates are Gate P (Cp at seven span stations, ±0.02) and Gate G (the Roache
triple). Searching that document for `0.45`, `Cl_p`, `pressure lift` and
`lift coefficient` returns those two lines and nothing else.

**What follows from (b), and what does not.** It does **not** make `+0.191505` wrong —
the number is re-derived and solid. It means **the band it is being compared against
cannot be shown to have been frozen before the compute**, so the comparison should be
described as *"in the range this lab has used for the M6"* rather than as a gate
result. **This is referred to the cfd-supervisor as a finding; it is not ruled on
here.** The successor registration `M6C1_PREREGISTRATION.md` §5.3 declines to inherit
the band for exactly this reason.

---

## 5. IS THERE A SOLVE WITH USABLE PHYSICS ANYWHERE ELSE IN THE M6 FAMILY? — SURVEYED

Eight family trees under `verification/runs/` were checked for solved time directories
and for `End` lines, by named path:

| tree | solved time dirs | `End` lines belong to | solver binary found |
|---|---|---|---|
| `M6CP1_runs` | `L1/smoke/`, `L2/smoke_M0_baseline/`, **`L2_N1/smoke/`** — all `smoke*` | **a SOLVER** | **`rhoPimpleFoam`** |
| **`M6_OWN_FAMILY_runs`** | `L2/smoke_rhopimple_lts/500`, `L2/smoke_rhopimple_nnoc3/500`, `L2_arfix_diag/smoke_{n1a,n1c,n2a,n3b}/500` — all `smoke*` | **a SOLVER** | **`rhoPimpleFoam`** |
| `M6SR_runs` | none | meshers only — `checkMesh`, `decomposePar`, `log.mesh` | none |
| `M6I_runs` | none | meshers only — `checkMesh`, `plot3dToFoam` | none |
| `M6_LE_RESOLVED_runs` | none | meshers only — `checkMesh`, `plot3dToFoam`, `createPatch`, `renumberMesh`, `autoPatch` | none |
| `F13_ONERA_M6_runs` | none | meshers only — `checkMesh` | none |
| `RUNG1_M6_R2_runs` | none | meshers only — `checkMesh`, `plot3dToFoam`, `createPatch` | none |
| `M6S_runs` | none | **no `End` line at all** | none |

**The survey put to this lane was: "every `End` line in those trees belongs to a MESHER
and every solved time directory is a `smoke_*`." The result is a CONFIRMATION WITH ONE
CORRECTION:**

- ✅ **"Every solved time directory is a `smoke_*`" — HOLDS.** Every numeric time
  directory found across all eight trees sits under a `smoke*` parent. **There is no
  graded, non-smoke M6 solve anywhere in the lab.**
- 🔴 **"Every `End` line belongs to a mesher" — OVERTURNED for one tree.**
  **`M6_OWN_FAMILY_runs` holds solver `End` lines**: `log.rhoPimpleFoam` with `End=1`
  in `L2/smoke_rhopimple_lts` and `L2/smoke_rhopimple_nnoc3`, and `End=2` in
  `L2_arfix_diag/smoke_n1a`. It is a second tree with completed solver runs, not just
  M6CP1. *(This lane's own first pass missed them because its listing was truncated by
  a `head`; the correction is recorded rather than the first pass.)*
- **The named solver binary, in both trees, is `rhoPimpleFoam`.** No other solver binary
  appears in any of the eight.

**What this means for the question Sanaa asked.** The M6 family's only solves are smoke
runs, and the only one with a pressure load inside the lab's working range is
`M6CP1_runs/L2_N1/smoke/`. **`M6_OWN_FAMILY_runs`' completed smokes have not been read
for their pressure loads and may be worth the same treatment** — that is named here as
an open, cheap piece of work, not as a claim.

---

## 6. 🔴 THE FINDING THAT MATTERS MOST, AND IT IS ABOUT THE GEOMETRY, NOT THE SOLVER

**The ONERA M6 reference trailing edge is BLUNT, and this lab already had the number
on disk.**

`docs/papers/benchmark_test_cases/agard_1979_ar138_experimental_data_base.pdf` —
title-page verified as **AGARD Advisory Report No. 138, "EXPERIMENTAL DATA BASE FOR
COMPUTER PROGRAM ASSESSMENT", May 1979** — carries test case **B1, "Pressure
Distributions on the ONERA-M6-Wing at Transonic Mach Numbers", by V. Schmitt and
F. Charpin**. Its **Table B1-1** (page B1-7, PDF page 333) ends at:

```
x/l = 1.0000000      z/l = 0.0007052
```

and the lab's own digitisation, `models/onera_m6/agard_ar138_table_b1_1_section_
coordinates.dat`, ends at exactly the same two numbers.

The section is symmetric, so:

| | |
|---|---|
| **TE total thickness** | **0.141 % of local chord** (1.14 mm at the root, 0.64 mm at the tip) |
| model fabrication tolerance (source §2.3) | 0.15 mm — **the TE is 7.6× it at the root** |
| included wedge angle at the TE | **14.8°** |
| **M6CP1 as built** | **0 thickness, 0 cells across, included angle 121.8°** |

**So M6CP1's cusp was not a meshing infelicity. It was an unregistered departure from
the reference geometry, and the correct coordinate was sitting in a committed file in
this repository the whole time.** That is the finding the successor registration
`verification/campaign/M6C1_PREREGISTRATION.md` is built on.

**One defect in the lab's copy, disclosed:** the 1979 scan's **numeric tables did not
OCR**. The prose did; Table B1-1 and the Cp tables B1-2 onward survive in the `.txt`
sidecar as captions only. **There is no machine-readable AGARD Cp dataset in this
repository**, which means **M6CP1's Gate P — Cp at seven span stations, band ±0.02 —
could not have been graded from the lab's holdings.** The pages are legible and
renderable, so digitisation is feasible work, not a blocker. It is simply not done.

---

## 7. WHAT IS NOT CLAIMED HERE

- **No verdict is issued or changed.** M6CP1 remains parked `NOT A RESULT`.
- **`+0.191505` is not a validated result.** It is a pressure integral from an
  unconverged 400-step smoke on a mesh whose trailing edge departs from the reference.
  It is evidence that the pressure solution was sane, and nothing more.
- **No comparison to experiment is made**, because no machine-readable M6 experimental
  Cp data is on disk (§6).
