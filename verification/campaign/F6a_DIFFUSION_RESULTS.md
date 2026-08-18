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

## T1 second arm completed, and T1 is scored: NOT FALSIFIED

The a1=0.25 run was extended to 10,324 iterations (2.7x the r4 sweep's cap)
before ruling: Ux Initial residual floor 1.6e-3–2.6e-3 across the entire run
with no decaying trend, fragmented wall trace at every one of ten
checkpoints, outermost closure wandering 1.375–1.412 (±1.3% — fails the SA
plateau bar), interior structure reorganizing between checkpoints. Stopped
gracefully (`stopAt writeNow`, final write t=10324); checker verdict
NOT_CONVERGED (`f6a_diff_SST_a1_025_20260801T001506Z.log/.done`). **No
gate-met scalar exists at a1=0.25.** Descriptive extraction from its final
written state (starred, unconverged, excluded from all correlations): peak
|R_xz|/Uinf² = 0.007838 — 40% below baseline.

Scoring T1 against the pre-registered falsifier:

| a1 | peak\|R_xz\|/Uinf² | reattachment x/c | status |
| --- | --- | --- | --- |
| 0.25 | 0.007838* | no steady value; outermost closure 1.375–1.412*, always ABOVE baseline's 1.2534 | NOT converged (floor + fragmentation) |
| 0.31 | 0.013153 | 1.2534 | gate-met |
| 0.40 | 0.015107 | 1.1873 | gate-met (1702 iter) |

- Wrong-direction? **No** — a1 up moved reattachment down (−0.0661), a1 down
  moved every observable state up (>+0.12 at every checkpoint).
- Swing < 0.005? **No** — the converged pair alone spans 0.0661, 6.6x the
  significance bar; the fragmented low arm only widens it.
- Non-monotonic? **No**, on the evidence available — with the honest caveat
  that the a1=0.25 point contributes a bound ("longer than baseline, by a
  lot"), not a number.

**T1 verdict: H survives its within-SST causal probe decisively.** The
shear-stress limiter coefficient moves the hump bubble exactly the way the
diffusion hypothesis says it must, in both directions, with the stress
metric moving in lockstep (0.0078* → 0.0132 → 0.0151). And the low arm adds
an unplanned, physically interesting echo of the r4 finding: suppressing
shear-layer transport far enough doesn't just lengthen the steady bubble, it
destroys the steady solution altogether — weakened turbulent diffusion is
destabilizing for this flow's steady-state representation regardless of
which direction the experiment lies in.

Standing disclosure, repeated: neither a1 variant is a model recommendation;
0.25/0.40 were fixed in the pre-registration before any result was read.

## T2, corrected in-flight: every RSM failure above traced to ONE root cause — the R initial field was non-realizable

Chronology kept honest: after LRR's three failures were recorded above, SSG
and EBRSM were attempted and failed the same way — and two of those failures
exposed a **new trap for this project's own settle standard**, worth its own
paragraph before the root cause.

**SSG "converged" twice, and both are false gates.**
`f6a_diff_SSG_20260801T004155Z.log` printed `SIMPLE solution converged in 381
iterations`; `f6a_diff_SSG_v2_20260801T004417Z.log` (epsilonWallFunction
lowReCorrection added) printed it at 239. In both, the final iterations show
epsilon bounding with averages of 1e33–1e34 (v1) and 1e24 (v2) — a fully
diverged epsilon field — while Ux/Uz/p Initial residuals sit at machine zero
(1e-16–1e-18, `No Iterations 0`): the momentum update had frozen, and
`residualControl` sampled a quiet iteration of an oscillating, unphysical
state. The wall trace at the "converged" state is 22+ Cf sign crossings
including spurious ones at x/c −2.0 and −0.49. **The `SIMPLE solution
converged` string and the string-based checker verdict are both satisfied by
this state; only the physical read (`hump_gate_analysis.py`, bounding lines)
catches it.** This is a third distinct gate-trap signature for the estate
(after Final-vs-Initial L-14 and wrong-field D5): *converged-string on a
diverged state*. Neither SSG "result" is a result.

**EBRSM attempt 1** (`f6a_diff_EBRSM_20260801T004539Z.log`, low-Re wall BCs
per the v2606 planeChannel tutorial): epsilon → 9.1e49, dead at iteration 12.

**The root cause, then.** Checked the R field all these runs were initialized
from (built by `postProcess -func R` on kEpsilon's converged t=2000 state):
**it is non-realizable.** Negative normal stresses in 12.39% of cells (Rxx
min −20.5 m²/s²), 4.88% (Rzz), 1.36% (Ryy), and on 18 of 83 inlet faces of
the fixedValue inlet profile — the documented over-strain defect of linear
EVM stress reconstruction, R = (2/3)k·I − 2·nut·S. Every "LRR/SSG/EBRSM
failure" above was therefore feeding the stress-transport equations a
Reynolds stress no velocity field can have — the same pathology class the
L-26 sign-error audit measured, arrived at by a different door. **None of the
six attempts above was actually testing the turbulence model**, exactly the
shape of the L-26 lesson ("the three attempts §8 counted were never running
the method"), which is why the three-treatments rule is correctly reopened
here rather than violated.

**Fix (blind to the answer):** `0/R` rebuilt as the strictly realizable
isotropic state (2/3)k·I from the same converged k field (floor 1e-8),
inlet profile likewise; anisotropy left to regenerate from each model's own
transport. Documented in each case's `0/R` header. First clean run (LRR v4,
`f6a_diff_LRR_v4_20260801T004731Z.log`): no epsilon bounding at all through
500+ iterations, all residuals decaying — the instability is gone with the
IC defect, on the numerics that had already failed twice without it.

## T2: LRR on the realizable IC — a characterized limit cycle, not a gate-met value

`f6a_diff_LRR_v4_20260801T004731Z.log` (conservative-ladder numerics: SIMPLE,
p 0.3, U 0.5, R/eps 0.2, first-order R/eps convection). With the realizable
IC the epsilon catastrophe is gone: clean monotone decay for ~3,900
iterations, Ux Initial reaching 1.10e-6 (2.2x over gate) with a single clean
bubble. Then, as the model's own anisotropy finished developing, recurring
epsilon-bounding bursts set in (~every 100–500 iterations from iter ~3,894
onward, 700+ events by 12,354) and the run entered a stable limit cycle
rather than a fixed point: reattachment at t=6000..12000 checkpoints reads
1.2668, 1.2724, 1.2682, 1.2620, 1.2587, 1.2611, 1.2636 — oscillating about
**mean 1.2647, envelope ±0.007 (±0.55%)**, single bubble at 6 of 7
checkpoints, transiently double-crossed mid-burst. Stopped gracefully with
`stopAt writeNow` at 12,354; checker verdict NOT_CONVERGED, reported exactly
so. This exceeds the SA plateau precedent's 0.3% stability bar, so **1.2647
is a starred, characterized oscillation mean — not a converged prediction,
and it enters no gate-met claim.** Physically it echoes the record's standing
reading: a stress state this far off the eddy-viscosity manifold has no
steady fixed point on this mesh — but here the cycle is tight enough to
characterize instead of fragmenting into noise.

Shear metric across the last four written states (10000, 11000, 12000,
12354): peak|R_xz|/Uinf² = **0.013801 ± 0.0001** — essentially stationary
across the cycle even as reattachment wobbles, between kOmegaSST's 0.0132
and kEpsilon's 0.0159. Note the pairing (starred): slightly MORE stress
than SST, slightly LONGER mean bubble — a mild inversion against H's
cross-model monotonicity, carried into T2 scoring as such.

## T2: SSG genuinely converges on the realizable IC — the first settled Reynolds-stress closure on the hump

`f6a_diff_SSG_v3_20260801T011637Z.log`: `CONVERGED: solver printed 'SIMPLE
solution converged in 22559 iterations'` — a real gate this time, checked
against the same standard that exposed its two earlier false gates: zero
`bounding epsilon` events in the entire log, every field's Initial residual
under its control (R components decayed monotonically at ~x0.85/1000
iterations for 20k+ iterations; endTime was proactively extended 30000→60000
at iter ~14,000 when extrapolation showed the cap would truncate — extension
of the same kind as kOmega's, no other change), and a single clean bubble.
BCs at the channel-1 family standard (the v2 lowReCorrection was reverted —
the blowups were the IC's fault, not the wall treatment's).

| quantity | SSG | context |
| --- | --- | --- |
| separation x/c | 0.6664 | experiment 0.6650: −0.2%, closest separation of any model in the study |
| reattachment x/c | **1.1630** | **+5.72%** vs experiment; between kEpsilon (+3.97%) and SA (+9.65%) |
| peak\|R_xz\|/Uinf² | 0.011122 (0.007852, 0.011439, 0.014076) | below SST's 0.013153 |

kEpsilon (1.1437, +3.97%) remains the closest single check —
`D9_TALKING_POINTS.md` unaffected.

Interim T2 with SSG (n=6 gate-met+SA set): Spearman rho = **−0.600**;
including the a1=0.40 variant as the labeled secondary set (n=7): **−0.679**.
SSG itself is a rank inversion against H (less stress than SST, much shorter
bubble) — its stress-anisotropy transport evidently does work its scalar
peak-stress metric does not capture. Final scoring waits on EBRSM.

## Run ledger (appended as runs settle)

- 2026-08-01T00:04Z `f6a_diff_SST_control` — CONVERGED 1795 iter, 0.6544 / 1.2534. Template gate passed.
- 2026-08-01T00:10Z `f6a_diff_SST_a1_040` — CONVERGED 1702 iter, 0.6562 / 1.1873. Metric extracted.
- 2026-08-01T00:15Z `f6a_diff_SST_a1_025` — live; residual floor + fragmented bubble through 5,000 iterations (see above).
