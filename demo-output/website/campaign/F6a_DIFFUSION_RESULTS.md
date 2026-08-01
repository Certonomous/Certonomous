# F6a — the k-SST diffusion hypothesis: results

Scored against `F6a_DIFFUSION_PREREGISTRATION.md` (committed 4ec43da4 BEFORE
any run in this study executed). This file is appended per-model as runs
settle; nothing below is edited after being written except via dated
correction notes, per this project's record practice.

All new runs: `/home/ubuntu/certonomous-runs/F6a_diffusion/`, launched via
`scripts/launch_solve.sh`, gates checked with `scripts/check_convergence.py`
(Initial residuals, `SIMPLE solution converged` string), separation and
reattachment read by Cf sign change with the same `hump_gate_analysis.py` as
every rung of the act. Experiment: separation 0.6650, reattachment 1.1000.

## Template-validity gate: PASSED, exactly

The T1 control — stock kOmegaSST rebuilt in a fresh case cloned from the
channel-1 kOmega template (model switched, nothing else) — was required to
reproduce the recorded baseline 1.2534 within ±0.005 before any sensitivity
run counted.

| run | log | verdict | iterations | separation x/c | reattachment x/c |
| --- | --- | --- | --- | --- | --- |
| kOmegaSST control (a1=0.31 default) | `solve_registry/f6a_diff_SST_control_20260801T000426Z.log` | CONVERGED (checker: "solver printed 'SIMPLE solution converged in 1795 iterations'") | 1795 | 0.6544 | 1.2534 |

Identical to the recorded baseline (0.6544 / 1.2534, also 1795 iterations —
`F6a_epistemic_band.md`, r4 Delta=0.00 control). The clone is the baseline.

## T2 metric, existing gate-met models (extracted before any new model finished)

Pre-registered metric: peak |R_xz| on vertical lines at x/c = 0.8, 0.9, 1.0,
averaged over the three stations, normalized by Uinf² = (34.62531106959954)².
R generated with `simpleFoam -postProcess -func R` on copies of the converged
cases under `certonomous-runs/F6a_diffusion/extract/` (published case dirs
untouched); sampled with `postProcess -func shearLines` (type `uniform`, 600
points — the .org `lineCell` type in the dormant singleGraph dicts does not
exist in v2606). Analysis: `certonomous-runs/F6a_diffusion/analyze_shear.py`,
output `shear_metric_results.json`.

| model | source time dir | reattachment x/c | peak\|R_xz\|/Uinf² (x/c 0.8, 0.9, 1.0) | mean |
| --- | --- | --- | --- | --- |
| kOmega | `channel1_rans_sweep/kOmega/22211` | 1.0717 | 0.017529, 0.022374, 0.026625 | **0.022176** |
| kEpsilon | `channel1_rans_sweep/kEpsilon/2000` | 1.1437 | 0.011982, 0.015834, 0.019867 | **0.015895** |
| kOmegaSST | `r4_band_tightening_hump/oneC_delta0.00/1795` | 1.2534 | 0.011362, 0.013955, 0.014141 | **0.013153** |
| realizableKE | `channel1_rans_sweep/realizableKE/1901` | 1.2503 | 0.007894, 0.010068, 0.012348 | **0.010103** |
| SpalartAllmaras* | `channel1_rans_sweep/SpalartAllmaras/4200` | 1.2061 | 0.007138, 0.008943, 0.010348 | **0.008810** |

\* SA carries its documented residual-floor caveat (gate not formally met,
QoI stable — `F6a_epistemic_band.md`). Its R_xz = −2·nut·S_xz is exact for
the metric even though SA carries no transported k (the k-dependent part of
R is diagonal only, as pre-registered).

Provisional reading, NOT scored until the model set is complete: the two
models that sustain the most shear-layer stress (kOmega, kEpsilon) predict
the two shortest bubbles, and realizableKE — whose variable-Cmu formulation
also suppresses nut at high strain — indeed shows a stress level BELOW
SST's, as H required of it. SA is the visible outlier (lowest stress, but
mid-pack bubble). Spearman rho over these five: −0.600. Scoring waits for
the full set per the pre-registration.

## Run ledger (appended as runs settle)

- 2026-08-01T00:04Z `f6a_diff_SST_control` — CONVERGED 1795 iter, 0.6544 / 1.2534. Template gate passed.
- 2026-08-01T00:10Z `f6a_diff_SST_a1_040` — launched (a1=0.40 confirmed in solver's own printCoeffs banner).
