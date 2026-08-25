# D11-D′ — THE DICTIONARY RE-BUY — RESULTS

## 1. Verdict

**`NOT A RESULT`.** The frozen grader refused, exit 2, on
`artifact missing: …/D11P/omegaP/d11p_omegaP.json`.

Pre-registration frozen `25c735ff`.

## 2. What ran — and the half that worked is the finding

| stage | omega | task | rc | `OOMKilled` | core-min |
|---|---|---|---|---|---|
| `omegaP` | **300.0** | `compute_totals` | 1 | false | 0.1667 |
| `omega0` | **0.0** | `compute_totals` (primal **and adjoint**) | **0** | false | 0.1667 |
| `clean` | 0.0 | `run_model` | **0** | false | 0.1167 |
| `fdp` | 300.0 | `run_model` | 1 | false | 0.2000 |
| `fdm` | 300.0 | `run_model` | **2** | false | 0.1333 |

**The corrected `MRF { … }` dictionary is right.** DAFoam parses it, builds the zone, and
takes an **adjoint** through to `rc = 0`. The `Entry 'MRF' not found` fatal is gone and
never returned in any successor.

## 3. Crash triage

**Every failure is at `omega = 300 rad/s` and only there.** The steady SIMPLE primal
**STALLS** — continuity plateauing at `≈ 2.5e-4`, never reaching
`primalMinResTol = 1e-10` inside 2000 iterations — so DAFoam raises
`openmdao.core.analysis_error.AnalysisError: Primal solution failed!` and writes no JSON.
**It stalls; it does not diverge and it does not NaN.**

**That is the substrate refusing a 300 rad/s zone, not the capability being absent.** At
`r ≈ 0.02 m` a 300 rad/s zone drives `≈ 6 m/s` of tangential motion against a `10 m/s`
through-flow across an abrupt zone boundary — a harsh steady problem, and this lane's
choice of magnitude, not DAFoam's limitation.

**This measured fact outlives the probe** and is carried into D11's own
pre-registration: **a steady MRF-active `DASimpleFoam` substrate must be chosen so its
zone is physically appropriate to a rotating frame, or the case must be unsteady.**

## 4. Cost

**0.8334 core-min gross**, against a prediction of 1.2 and a cap of 5.0 (`0.694×` of
prediction, `0.167×` of cap; guard never fired). **= $0.000713 DERIVED, NOT MEASURED**.

**All 0.8334 core-min is NAMED WASTE** (`COMPUTE_BUDGET_CHARTER.md` §6) — no graded
quantity — netted off nothing, though it bought §3. Calibration row **C-69**.
