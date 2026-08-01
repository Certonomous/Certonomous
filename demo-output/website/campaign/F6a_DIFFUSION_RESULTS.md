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

## T1, first arm: a1 = 0.40 — CONVERGED, bubble shortens, stress rises

`solve_registry/f6a_diff_SST_a1_040_20260801T001014Z.log`: checker verdict
`CONVERGED: solver printed 'SIMPLE solution converged in 1702 iterations'`.
The solver's own printCoeffs banner confirms `a1 0.4` with every other
coefficient stock. Single clean bubble.

| quantity | a1=0.31 (control) | a1=0.40 | shift |
| --- | --- | --- | --- |
| separation x/c | 0.6544 | 0.6562 | +0.0018 |
| reattachment x/c | 1.2534 | **1.1873** | **−0.0661** |
| peak\|R_xz\|/Uinf² (0.8/0.9/1.0c mean) | 0.013153 | **0.015107** (0.012223, 0.015520, 0.017579) | +15% |

Raising the limiter cap raised the shear-layer stress AND shortened the
bubble by 0.066 — 6.6x the pre-registered 0.01 significance bar, in the
direction H predicts, with separation nearly unmoved (the documented
onset-easy/recovery-hard pattern again). **Disclosed again: this is a
sensitivity result. 1.1873 is not a better model; a1=0.40 was not chosen for
where it lands.**

## T1, second arm: a1 = 0.25 — interim (2026-08-01T00:25Z, run live)

`solve_registry/f6a_diff_SST_a1_025_20260801T001506Z.log`. Through 5,000
iterations: Ux Initial residual oscillates 1.6e-3–2.6e-3 with no decaying
trend (0.0018 at ~500 → 0.0025 at ~5000), p 0.015–0.05 — the residual-floor
signature this record knows from the r4 moderation sweep, not a slow
transient. The wall trace is FRAGMENTED at every checkpoint (6–10 Cf sign
crossings; a short bubble near x/c 0.61–0.68 plus a long downstream
separation whose final closure wanders 1.378–1.404 across t=1000..5000
checkpoints). Weaker shear-layer diffusion pushes the flow toward a longer,
multi-cell, apparently unsteady separation with no steady fixed point —
directionally consistent with H, but NOT a gate-met scalar, and per the
standing rule it will not be placed on any curve as one. Run continues; a
floor verdict needs the standard evidence window (≥2000 further iterations)
before ruling.

## T2: LRR does not converge on this mesh — recorded as a failure (L-22), three attempts

All three attempts initialized from kEpsilon's converged t=2000 field (the
documented multi-stage restart), R built isotropically-consistently from that
same field via `postProcess -func R`, wall functions matching the channel-1
family (kqRWallFunction on R, epsilonWallFunction, nutUSpalding; mesh y+ avg
2.0). Ladder, most aggressive to most conservative:

| attempt | numerics | outcome | log |
| --- | --- | --- | --- |
| 1 | SIMPLEC (`consistent yes`), U 0.9, R/eps relax 0.3, turbulence convection `bounded Gauss linearUpwind limited` (= channel-1 standard) | epsilon bounding negative from iteration 1, max → 4.1e13 by iter ~11, SIGFPE in DILU preconditioner at iter 12 | `f6a_diff_LRR_20260801T003703Z.log` |
| 2 | plain SIMPLE, p 0.3, U 0.7, R/eps 0.3, same schemes | epsilon → 3.7e72 by iter ~19, Ux Initial residual ~1, killed by FPE | `f6a_diff_LRR_v2_20260801T003919Z.log` |
| 3 | plain SIMPLE, p 0.3, U 0.5, R/eps 0.2, R/eps convection first-order `bounded Gauss upwind` | epsilon → 9.9e18, died by iter ~139 | `f6a_diff_LRR_v3b_20260801T004053Z.log` (the `_v3_` log preceding it is an environment-sourcing misfire, `nohup: failed to run command 'simpleFoam'`, no solver ran) |

Divergence is in the epsilon/R system itself (epsilon goes negative
immediately and explodes), not the pressure coupling — it survived the move
off SIMPLEC unchanged. Consistent with LRR's wall-reflection formulation
meeting first-cell strain at y+≈2, where epsilonWallFunction is outside its
validity; the EVMs' calmer production forms coped on this same mesh,
realizableKE (the closest EVM analogue with a strain-sensitive coefficient)
also needed rescue here, and D5 already scored "at least one RSM will need
relaxation tuning or fail outright" as CORRECT on the duct. Per the standing
three-treatments rule, no fourth attempt; the failure is the result.

## Run ledger (appended as runs settle)

- 2026-08-01T00:04Z `f6a_diff_SST_control` — CONVERGED 1795 iter, 0.6544 / 1.2534. Template gate passed.
- 2026-08-01T00:10Z `f6a_diff_SST_a1_040` — CONVERGED 1702 iter, 0.6562 / 1.1873. Metric extracted.
- 2026-08-01T00:15Z `f6a_diff_SST_a1_025` — live; residual floor + fragmented bubble through 5,000 iterations (see above).
