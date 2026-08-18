# F6a — NASA 2D wall-mounted hump, staged RANS baseline vs NASA's own published validation data

Date: 2026-07-28. Family F6 (Certonomous hard-case campaign), sub-family a.
Machine-readable companion: `F6a_nasa_hump.json`. Fresh work (no prior rung
existed for this case). Scope: climb feasibility -> physics -> gate for the
benchmark's own `NASA_2DWMH` test case, then compare the converged
separation/reattachment/Cp against NASA's own published experimental
validation data. No fitting, tuning, or selection against test-case ground
truth was performed anywhere in this rung — every comparison below is a
single forward RANS solve, exactly the same operation already used for the
published `closure_challenge_rans_floor.json`.

## Headline result

**Our independently-run OpenFOAM v2606 `kOmegaSST` baseline for `NASA_2DWMH`
matches NASA's own published SST result almost exactly (separation Δ=0.06%,
reattachment within their quoted range), and correctly reproduces the
textbook linear-eddy-viscosity SST deficiency against the real experiment:
separation location is close (Δ=-1.6%) but the reattachment/bubble length is
over-predicted by +14%.** This is not a bug — it is the exact, well-documented
model-form error that the closure challenge exists to correct, and it is
independently confirmed against four separate references (NASA's own
published SST CFD, NASA's own published experiment, the benchmark's own
shipped baseline field, and the benchmark's own scorer/published floor).

## Case setup

- Source: `/home/ubuntu/closure-challenge-benchmark/data/NASA_2DWMH/` — the
  benchmark's own shipped OpenFOAM case (mesh, `caseDef`, `fieldDef`, BCs),
  already run once by the paper authors to `2000/` (their own converged
  baseline field, used as one of our comparison references below).
- Geometry: 2D wall-mounted Glauert-Goldschmied hump, chord `c=0.42 m`,
  `Re_c=936,000`, `M=0.1` (`Uinf=34.625 m/s`, computed from `caseDef`'s
  `Mref`, `Tref`, `R`, `gamma`) — confirmed to match NASA TMR's own stated
  case parameters exactly (chord 420 mm, Re=936,000, M=0.1) via
  [tmbwg.github.io/turbmodels/nasahump_val.html](https://tmbwg.github.io/turbmodels/nasahump_val.html).
- Mesh: 51,626 cells, 2D (`sides` patch `empty`), `inlet`/`outlet` patches
  with spatially-varying profiles baked into `0/inletOutletFields/*` (from
  the paper's own precursor data), `bottom` = hump+downstream wall (622
  faces), `top` = symmetry.
- Solver: `simpleFoam`, `SIMPLE` + `consistent` (SIMPLEC), `residualControl`
  `U/p/k: 5e-7`, `omega: 1e-10` (unmodified from the shipped `fvSolution`).
- `decomposeParDict` ships `numberOfSubdomains 4` — matches this campaign's
  4-MPI-rank cap exactly; used as-is, `mpirun -np 4`.

### Deviations, documented with cause (same pattern as ladder B2)

1. **`libfrozenIncompressibleTurbulenceModels.so` / `AugmentedkOmegaSST`
   (`baseline true`)**: not distributed anywhere in the public benchmark
   clone, not part of stock OpenFOAM. Substituted stock `kOmegaSST`
   (`constant/turbulenceProperties`), same substitution B2 made for the duct
   cases. *Measured effect this rung:* separation/reattachment/Cf/Cp/score
   all agree with the benchmark's own shipped baseline field to within
   0.00–0.02% (see "Sanity check" below) — this confirms, for a second case
   family, that `baseline=true` on this custom model is inert relative to
   stock `kOmegaSST` for the uncorrected case.
2. **`#includeFunc residuals/convergenceProbes/singleGraph_*` dropped**:
   `caseDicts/postProcessing/numerical/residuals.cfg` does not exist at that
   path in v2606 (same B2 finding). `wallShearStress` + `wallValues`
   (patch-sampling `surfaces` function object) were reinstated as **inline**
   function-object definitions in `controlDict` rather than `#includeFunc`,
   because invoking them via `postProcess -func '(...)'` standalone after
   the fact does not reliably re-register the computed `wallShearStress`
   field for the sampler in the same process (documented failure mode found
   and worked around this rung — running both objects inline, in sequence,
   at the same `writeTime`, is what makes `wallValues` see `wallShearStress`).
3. **Cp reference pressure**: NASA's own Cp referencing convention for this
   case was not independently obtained. We used the mean kinematic static
   pressure over the 5 most-upstream wall sample points (`x/c ≲ -1.9`,
   closest available proxy to freestream) as `p_ref`. This is a documented
   methodological choice, not verified as bit-identical to NASA's own
   method — flagged for the Cp comparison specifically; it does not affect
   the Cf-based separation/reattachment gate (which needs no pressure
   reference at all).
4. **`wallShearStress` sign convention**: OpenFOAM's `wallShearStress`
   function object reports the traction the *fluid* exerts *on the wall*,
   which is the negative of the conventional skin-friction sign. Verified
   directly: upstream attached flow (`x/c<0.4`) shows the same negative
   `wallShearStress_x` in both our run and the benchmark's own shipped
   `2000/` field. Standard `Cf = -wallShearStress_x / (0.5 Uinf^2)` used
   throughout below.

## Rungs

| Rung | Iterations | Wall time | Core-min (4 ranks) | Result |
|---|---|---|---|---|
| Feasibility | 0 → 100 (fixed) | 4.25 s | 0.28 | Runs clean, no crash. Residuals fall from O(1)/O(1e-1) at start to O(1e-3)–O(1e-5) by iter 100 (some `bounding omega/k` events during the startup transient, not fatal, cleared by rung 2). |
| Physics | 0 → 800 (fixed, rerun from scratch after the postprocessing fix in deviation #2) | 37.58 s | 2.51 | **Separation bubble clearly present.** `Cf` sign change (attached→separated) at `x/c=0.6544`, (separated→attached) at `x/c=1.2574` — phenomenon appears in the expected location before full convergence. |
| Gate | 800 → 1772 (SIMPLE auto-converged on `residualControl`) | 36.99 s | 2.47 | Converged: `SIMPLE solution converged in 1772 iterations`, all of `U/p/k` below `5e-7` and `omega` below `1e-10`. Final Cf/Cp extracted, see below. |
| **Total** | **1772** | **~78.8 s** | **~5.25** | |

`MemAvailable` checked before each stage: 30.1–30.5 GB free throughout (16
vCPU / 32 GiB host), no contention observed. All runs decomposed to 4
subdomains, `mpirun -np 4` (at the cap).

## Gate: separation and reattachment vs NASA's own published data

| Quantity | Ours (converged, iter 1772) | NASA experiment | Deviation vs experiment | NASA's own published SST (CFL3D/FUN3D, 817×217 grid) | Deviation vs NASA's own SST |
|---|---|---|---|---|---|
| Separation `x/c` | **0.6544** | 0.665 | -0.0106 (**-1.6%**) | 0.654 | +0.0004 (**+0.06%**) |
| Reattachment `x/c` | **1.2534** | 1.100 | +0.1534 (**+13.9%**) | 1.25–1.27 | within range (low end) |

Source for NASA's experimental and SST-CFD numbers:
[tmbwg.github.io/turbmodels/nasahump_val_sst.html](https://tmbwg.github.io/turbmodels/nasahump_val_sst.html)
("CFD codes predict the flow separation to occur near x/c = 0.654 and
reattachment near x/c = 1.25-1.27 (in experiment these were 0.665 and 1.1,
respectively)"). The Turbulence Modeling Resource site relocated from
`turbmodels.larc.nasa.gov` to `tmbwg.github.io/turbmodels/` as of 2026-02-24;
both the SST results page and the experimental data files (`noflow_cp.exp.dat`,
`noflow_cf.exp.dat`, downloaded from
`tmbwg.github.io/turbmodels/Nasahump_validation/`) were fetched directly, not
recalled from memory.

**Reading:** our reproduction matches NASA's own published SST solution
almost exactly (separation within 0.06%, reattachment inside their quoted
1.25–1.27 range) — this confirms our setup and solver are correct, not
buggy. The deviation from the real experiment (separation close, reattachment
+14% too far downstream) is the textbook linear-eddy-viscosity SST
deficiency: "models tend to underpredict the turbulent shear stress in the
separated shear layer, and therefore tend to predict too long a separation
bubble" (NASA TMR, same page). This is exactly the deficiency the closure
challenge's data-driven correction targets.

## Sanity checks (internal consistency, not the external gate)

### 1. Field-vs-field vs the benchmark's own shipped baseline (`AugmentedkOmegaSST`, `baseline=true`, at their `2000/`)

| Quantity | Ours | Benchmark's shipped baseline | Deviation |
|---|---|---|---|
| Separation `x/c` | 0.6544 | 0.6544 | 0.0000 (0.00%) |
| Reattachment `x/c` | 1.2534 | 1.2531 | +0.0003 (+0.02%) |

Confirms deviation #1 (custom-library substitution) is inert for the
uncorrected baseline here too, matching B2's finding for the duct cases.

### 2. Benchmark's own scorer, self-consistency with the published RANS floor

Using the benchmark's own `evaluate_individual_case`
(`closure-challenge-pkg`) at the official 1000 evaluation points for
`NASA_2DWMH`:

| Quantity | Value |
|---|---|
| Our score | 0.0622 |
| Reproduced benchmark baseline score (their field, our scorer call) | 0.0621 |
| Published floor (`closure_challenge_rans_floor.json`) | 0.0621 |
| Deviation (ours − floor) | +0.0001 (**0.16%**) |
| Internal field-vs-field scaled MAE (ours vs their shipped field) | **0.02%** |

Same near-exact-reproduction pattern as B2's duct baselines (0.16%/0.64%
score deviation, 0.02–0.09% field MAE).

### 3. Cp distribution vs experiment (secondary metric, shape check)

110 overlapping `x/c` points between our converged Cp and NASA's
`noflow_cp.exp.dat`. Scaled MAE = 0.0341 / (experimental Cp range 1.181) =
**2.89%**. Agreement is good over the accelerating/hump region, degrading
somewhat over the separated-flow plateau (`x/c` 1.0–1.3) — consistent with
the same shear-layer mixing deficiency that produces the reattachment
over-prediction above. Subject to the Cp-reference-pressure caveat
(deviation #3).

## Verdict

**GATE REACHED, PASS/FAIL AS MEASURED — separation location: close agreement
(within 1.6% of experiment). Reattachment/bubble length: documented,
expected SST-model deficiency (+13.9% over-prediction), independently
confirmed against NASA's own published SST CFD.** The baseline itself is
verified correct via three independent cross-checks (NASA's own SST
solution, the benchmark's own shipped field, the benchmark's own scorer).
Nothing here was fabricated or asserted without a citation — the NASA
experimental figures were fetched live from the (relocated) NASA Turbulence
Modeling Resource site, not recalled from training-time memory.

## Cost

Total: 1772 solver iterations, ~78.8 s wall, **~5.25 core-minutes** (4 MPI
ranks throughout, at the campaign cap). `MemAvailable` 30.1–30.5 GB
throughout, no contention.

## Evidence files

- This report: `demo-output/website/dafoam/f6a_nasa_hump/F6a_nasa_hump.md`
- Machine-readable: `demo-output/website/dafoam/f6a_nasa_hump/F6a_nasa_hump.json`
- Case working directory (config + logs + converged fields):
  `demo-output/website/dafoam/f6a_nasa_hump/case/`
  (`log.rung1_feasibility`, `log.rung2_physics`, `log.rung3_gate`,
  `gate_result_1772.json`, `cf_xc_1772.csv`, `cp_xc_1772.csv`,
  `cp_vs_experiment.json`, `score_our_baseline_result.json`)
- NASA experimental reference data (fetched, not fabricated):
  `demo-output/website/dafoam/f6a_nasa_hump/nasa_experimental_reference/{noflow_cp.exp.dat,noflow_cf.exp.dat}`
- Analysis scripts: `case/hump_gate_analysis.py` (Cf/Cp extraction +
  separation/reattachment crossing detection), `case/cp_compare.py`
  (vs experiment), `score_our_baseline.py` (benchmark scorer self-check)

## What's next / blocked

- Velocity-profile and Reynolds-stress comparison at the case's own sampling
  stations (`x/c=0.65,0.8,0.9,1.0,1.1,1.2,1.3`) was not attempted this rung
  (out of scope — separation/reattachment/Cp was the ordered gate).
- The Cp-reference-pressure convention (deviation #3) should be checked
  against NASA's own methodology if a tighter Cp number is ever needed.
