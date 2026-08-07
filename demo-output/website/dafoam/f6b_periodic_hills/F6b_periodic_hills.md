# F6b — Periodic hills, staged RANS baseline vs the ERCOFTAC/Breuer LES reference

Date: 2026-07-29. Family F6 (Certonomous hard-case campaign), sub-family b —
the last unstarted piece of the closure-aligned family (F6a NASA hump and
F6c duct-vs-DNS were gated in the prior session; F6b was time-boxed out).
Machine-readable companion: `F6b_periodic_hills.json` (in this directory;
written 2026-07-30 — see "Evidence files"). Fresh work: no prior
rung existed for this case. No fitting, tuning, or selection against any
test-case ground truth occurred anywhere in this work.

## Headline result

**GATE REACHED, 2026-07-30.** Stock kOmegaSST on the shipped `PH_Breuer` mesh
reattaches at **x/h = 7.6439** against the Fröhlich et al. (2005) LES reference
of **4.6-4.7** — an **over-prediction of the recirculation length by +63% to
+66%** (the "~64%" used as shorthand throughout this record and downstream is
the midpoint of that band, 7.64391457 / 4.65 − 1 = 64.4%; it is derived and
rounded, and no value `64` appears in `gate_result.json` or `gate_analysis.py`).
Separation is essentially right (**x/h = 0.2590** vs ~0.2). Mean-velocity
profiles at the case's own nine stations carry a scaled MAE of **12.5%**
against the shipped LES field.

**The pre-registered prediction is FALSIFIED, in the direction the prediction
itself flagged as uncertain.** `PREDICTION_before_run.md` expected reattachment
"somewhere in x/h ~ 4-6" and expected linear eddy-viscosity models to
UNDER-predict the recirculation length (reattach too early), explicitly
labelling that "a recollection, not a citation." The measured result is the
opposite sign and outside the predicted window: SST over-predicts, as it did on
the F6a NASA hump. The prediction file is left unedited, as it says it will be.

## Which Reynolds number and configuration this gates against

Case: `PH_Breuer`, the benchmark's own shipped OpenFOAM case
(`/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer/`), confirmed by
direct inspection to be the classic ERCOFTAC/Breuer periodic-hill geometry:

- Domain `Lx = 9h`, `Ly = 3.035h` (h = nondimensional hill height = 1),
  cyclic streamwise boundary condition, mean flow driven by a
  `meanVelocityForce` fvOption holding `Ubar = 0.72`.
- `nu = 9.438414346389807e-05`, with an explicit source-code comment
  `Re_H=10595` in `constant/transportProperties` — `Re_H = Ubar * h / nu`.
  *Correction, 2026-08-07 (Cases family supervisor):* that identity is false —
  0.72/9.438e-05 = 7628, not 10595. The case IS at the canonical Re_H:
  `meanVelocityForce` holds the domain-mean velocity at 0.72, and the
  literature's Re_H is built on the bulk velocity through the constricted
  crest section, measured at 0.9982 from the converged medium field of the
  2026-08-05 in-house ladder, giving Re_H = 10,576 (within 0.2% of 10,595).
  Full derivation and both numbers: `campaign/F6b_ERCOFTAC_RESULTS.md` §1b,
  which indicts this line and the 2026-08-05 pre-registration together. The
  original text above is left in place per the correction convention.
- Mesh: 15,600 cells, 2D (`frontAndBack` empty), `bottomWall`/`topWall` = 120
  faces each.
- 9 standard sampling stations `x0..x8` at `x/h = 0, 1, 2, ..., 8` (the
  case's own `system/singleGraph_x*` — these are the stations used
  throughout the periodic-hill RANS/LES literature).
- This geometry, domain size, and `Re_H=10595` match Fröhlich, Mellen, Rodi,
  Temmerman & Leschziner (2005), "Highly resolved large-eddy simulation of
  separated flow in a channel with streamwise periodic constrictions," *J.
  Fluid Mech.* 526, 19-66 — the reference LES dataset hosted by both
  ERCOFTAC (UFR 3-30, kbwiki.ercoftac.org) and NASA's Turbulence Modeling
  Resource (`tmbwg.github.io/turbmodels/Other_LES_Data/2dhill_periodic.html`,
  cited by the benchmark's own README as the periodic-hill Re=10595 data
  source). Fetched live this session, not recalled from memory: **separation
  near `x/h=0.2`, reattachment near `x/h=4.6-4.7`**.
- The case ships its own converged `U_LES`/`k_LES`/`p_LES`/`tauij_LES`
  fields on the identical mesh (same lineage), which is what the profile
  comparison below uses directly (no re-interpolation error from a
  different mesh).

Turbulence model: the case's own `constant/turbulenceProperties` already
declares stock `kOmegaSST` — unlike F6a/F6c, **no custom-library
substitution was needed** this time.

## Case setup / deviations from the shipped case, documented with cause

1. `controlDict` requested `libs ("libfrozenIncompressibleTurbulenceModels.so")`,
   not distributed in the public benchmark clone. Dropped — the case does
   not request the `baseline`/`Augmented` model variant that library
   supports; the forward `kOmegaSST` solve does not need it.
2. `#includeFunc residuals` dropped: `caseDicts/postProcessing/numerical/
   residuals.cfg` does not exist at that path in this box's OpenFOAM v2606
   (same finding as F6a/F6c). Residuals read directly from the solver log
   instead.
3. `singleGraph_x0..x8`'s `setConfig { type lineCell; }` is not a valid
   sample type in v2606 (`Unknown sample type lineCell` — valid types
   listed by the solver: `midPoint`, `uniform`, etc.). Changed to
   `midPoint`, the closest equivalent (line sampling through cell centres).
4. `wallShearStress` + a `bottomWall` patch surface sampler reinstated as
   **inline** function-object definitions in `controlDict` (same pattern as
   F6a) so both execute in sequence at each write time.
5. `decomposeParDict` shipped `numberOfSubdomains 8`; reduced to 4 to match
   this campaign's rank cap.
6. `Cf` sign convention: `wallShearStress` reports the traction the fluid
   exerts on the wall (negative of conventional skin friction); as in F6a,
   `Cf = -wallShearStress_x / (0.5 * Ubar^2)` used throughout.

## Rungs

| rung | log | outcome |
| --- | --- | --- |
| feasibility | `solve_registry/f6b_feasibility_20260729T035528Z.log` | **FAIL** — `FOAM FATAL IO ERROR`, `Unknown sample type lineCell` in `system/singleGraph_x0/sets`; fixed by the `midPoint` substitution recorded above |
| feasibility (2) | `solve_registry/f6b_feasibility2_20260729T035612Z.log` | PASS |
| physics | `solve_registry/f6b_physics_20260729T035647Z.log` | PASS |
| gate | `solve_registry/f6b_gate_20260729T035745Z.log` | 10,000 iterations, 4 ranks, 03:57:45 -> 04:06:16 UTC = 511 s wall, **34.1 core-minutes** |

## Gate

### Convergence — and a gate-checker false negative, diagnosed rather than overridden

`scripts/check_convergence.py demo-output/website/solve_registry/f6b_gate_20260729T035745Z.log`
returns **NOT_CONVERGED** (signature 3: the solver never printed
`SIMPLE solution converged`). **That verdict is a false negative on this case,
and the reason is in the case's own dictionary**: `system/fvSolution` line 82
sets `residualControl { p 1e-15; }`. 1e-15 is below anything a GAMG pressure
solve reaches on this mesh, so simpleFoam can never print its convergence
sentence, and the checker — correctly, by its own rules — refuses to infer
convergence without it. This is a **sibling of L-21, not L-21 itself** —
corrected 2026-07-30. L-21 names a `residualControl` entry pointing at a field
the model does not transport; here `p` *is* transported and the tolerance is
simply unreachable. Identical outward symptom (no convergence sentence), but a
different cause and a different fix, so they must not be conflated.

The convergence evidence is therefore the residual history itself, read
directly from the gate log (initial residuals, the column the gate would test):

| iteration | Ux | Uy | p | k | omega |
| --- | --- | --- | --- | --- | --- |
| 1000 | 5.54e-4 | 1.39e-3 | 4.45e-3 | 1.06e-3 | 2.15e-5 |
| 3000 | 1.90e-5 | 7.28e-5 | 1.23e-4 | 4.27e-5 | 5.94e-7 |
| 5000 | 1.45e-6 | 1.21e-6 | 3.50e-6 | 4.11e-6 | 4.35e-8 |
| 7000 | 1.24e-7 | 8.47e-8 | 2.40e-7 | 2.73e-7 | 4.28e-9 |
| 9000 | 1.18e-8 | 8.51e-9 | 2.92e-8 | 2.87e-8 | 8.86e-10 |
| **10000** | **3.60e-9** | **2.52e-9** | **1.35e-8** | **8.94e-9** | **8.94e-10** |

Monotone across four decades and flat over the last 1,000 iterations.

**Independent corroboration, which is what actually settles it.** The benchmark
ships its own converged kOmegaSST solution for this case
(`/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer/10000/`). Our solve
reproduces it to **five significant figures** on the gate quantity:

| | separation x/h | reattachment x/h |
| --- | --- | --- |
| benchmark's shipped RANS | 0.2590151 | 7.6438953 |
| our own solve, reconstructed | 0.2589993 | **7.6439146** |

### Gate result

| quantity | our solve | reference | deviation |
| --- | --- | --- | --- |
| separation x/h | 0.2590 | ~0.2 (Fröhlich et al. 2005) | +0.059 in x/h |
| reattachment x/h | **7.6439** | **4.6-4.7** (Fröhlich et al. 2005) | **+63% to +66%** |
| station-profile scaled MAE of \|U\| vs the shipped LES field | 12.51% (shipped/serial pipeline) · 12.95% (our 4-rank run) | — | — |

*Column-label correction, 2026-07-30:* the 12.51% belongs in this table but not
under a bare "our solve" heading. `gate_result.json`'s
`our_solve.profile_scaled_mae_vs_LES.overall_percent` is literally `null` — the
station loop at `gate_analysis.py:94` looks for `line_U.xy` while this run wrote
`line_k_nut_omega_p_U.xy`, so it found nothing and returned an empty dict
without erroring. 12.51% is therefore the *shipped* pipeline's number; this
campaign's own field measures 12.95%
(`f6d_random_matrix_uq/aggregate_result.json`). The note below already explained
the two figures; the table header did not.

Reference: Fröhlich, J., Mellen, C.P., Rodi, W., Temmerman, L. & Leschziner,
M.A. (2005), "Highly resolved large-eddy simulation of separated flow in a
channel with streamwise periodic constrictions," *J. Fluid Mech.* **526**,
19-66; the LES dataset hosted by ERCOFTAC (UFR 3-30) and NASA TMR, and the
source the benchmark's own README names for this case.

A note on the profile metric for anyone comparing numbers across records: the
12.51% figure is computed on the *shipped* (and, equivalently, on a serial)
sampling pipeline. Our own 4-rank parallel run of the identical field gives
12.95% for the same physics — the difference is line-sampling across processor
boundaries, not a different answer. Downstream work
(`campaign/F6d_random_matrix_uq.md`) uses the serial pipeline throughout,
because its ensemble members are serial.

## Verdict

**GATE REACHED.** The case is set up correctly, the baseline is converged on
its own residual evidence and independently reproduces the benchmark's shipped
solution to five significant figures, and the model-form error it exposes is
large and one-sided: kOmegaSST over-predicts the periodic-hill recirculation
length by ~64%. That is a *useful* gate result — a large, unambiguous,
well-referenced closure error on a cheap 15,600-cell case is exactly what a
model-form uncertainty study needs, and this baseline is what
`campaign/F6d_random_matrix_uq.md` builds on.

The pre-registered prediction was falsified on both the magnitude and the sign
of the error. It is left in place, unedited.

## Evidence files

- This report: `demo-output/website/dafoam/f6b_periodic_hills/F6b_periodic_hills.md`
- Machine-readable: `demo-output/website/dafoam/f6b_periodic_hills/F6b_periodic_hills.json`

  *Citation correction, 2026-07-30.* These two lines previously pointed at
  `demo-output/website/campaign/F6b_periodic_hills.md` and `.json`. Neither path
  existed: this report has always lived under `dafoam/f6b_periodic_hills/`, and
  the `.json` companion promised at the top of this file **had never been
  written at all**. The `.json` has now been produced from this case's own
  primary evidence (`gate_result.json`, the four `solve_registry` logs, the
  case dictionaries, and the pre-run prediction file) and both paths are
  corrected above. No number changed. Recorded because a record citing a
  nonexistent artifact is the failure mode LESSONS L-22 exists to prevent.
- Prediction written before any run: `demo-output/website/dafoam/f6b_periodic_hills/PREDICTION_before_run.md`
- Case working directory: `demo-output/website/dafoam/f6b_periodic_hills/case_breuer_re10595/`
- Analysis: `case_breuer_re10595/gate_analysis.py`, `case_breuer_re10595/foam_io.py`,
  `case_breuer_re10595/gate_result.json`
