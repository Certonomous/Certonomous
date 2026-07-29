# F6b — Periodic hills, staged RANS baseline vs the ERCOFTAC/Breuer LES reference

Date: 2026-07-29. Family F6 (Certonomous hard-case campaign), sub-family b —
the last unstarted piece of the closure-aligned family (F6a NASA hump and
F6c duct-vs-DNS were gated in the prior session; F6b was time-boxed out).
Machine-readable companion: `F6b_periodic_hills.json`. Fresh work: no prior
rung existed for this case. No fitting, tuning, or selection against any
test-case ground truth occurred anywhere in this work.

## Headline result

DRAFT — filled in after gate rung completes.

## Which Reynolds number and configuration this gates against

Case: `PH_Breuer`, the benchmark's own shipped OpenFOAM case
(`/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer/`), confirmed by
direct inspection to be the classic ERCOFTAC/Breuer periodic-hill geometry:

- Domain `Lx = 9h`, `Ly = 3.035h` (h = nondimensional hill height = 1),
  cyclic streamwise boundary condition, mean flow driven by a
  `meanVelocityForce` fvOption holding `Ubar = 0.72`.
- `nu = 9.438414346389807e-05`, with an explicit source-code comment
  `Re_H=10595` in `constant/transportProperties` — `Re_H = Ubar * h / nu`.
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

DRAFT — filled in after gate rung completes (feasibility/physics already
run; timings to be inserted).

## Gate

DRAFT — filled in after gate rung completes.

## Verdict

DRAFT.

## Evidence files

- This report: `demo-output/website/campaign/F6b_periodic_hills.md`
- Machine-readable: `demo-output/website/campaign/F6b_periodic_hills.json`
- Prediction written before any run: `demo-output/website/dafoam/f6b_periodic_hills/PREDICTION_before_run.md`
- Case working directory: `demo-output/website/dafoam/f6b_periodic_hills/case_breuer_re10595/`
- Analysis: `case_breuer_re10595/gate_analysis.py`, `case_breuer_re10595/foam_io.py`,
  `case_breuer_re10595/gate_result.json`
