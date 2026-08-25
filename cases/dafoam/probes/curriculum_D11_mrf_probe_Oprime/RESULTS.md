# D11-O′ — THE OMEGA RE-BUY — RESULTS

## 1. Verdict

**`NOT A RESULT`.** The frozen grader refused, exit 2, on
`artifact missing: …/D11O/fdm/d11o_fdm.json`.

Pre-registration frozen `a35ca242`.

## 2. What ran — four of five, including both stages that had to solve

| stage | omega | task | rc | core-min | `TPIn` |
|---|---|---|---|---|---|
| `omegaP` | **30.0** | `compute_totals` (primal **and adjoint**) | **0** | 0.1500 | `1.1859858226134654` |
| `omega0` | 0.0 | `compute_totals` | **0** | 0.1833 | `1.183671978501559` |
| `clean` | 0.0 | `run_model` | **0** | 0.1167 | — |
| `fdp` | 30.0 | `run_model`, `+1.0e-3` | **0** | 0.1167 | `1.1862164207660815` |
| `fdm` | 30.0 | `run_model`, `−1.0e-3` | **2** | 0.1333 | — |

**The `omega = 30.0` primal CONVERGED**, and the MRF-active adjoint returned
`d(TPIn)/d(patchV) = [0.23058711100900367, −0.000136601190978386]` — finite and
non-zero. None of that is graded here: the frozen grader needs all five artifacts.

## 3. The registered hard stop did NOT fire

D11-O′ §0 registered: *"If the `omega = 30.0` primal also fails to converge … THERE IS
NO FOURTH ATTEMPT."* **The clause is a conditional and its antecedent is false — the
primal converged.** Its stated reason, *"Reducing omega again"*, also fails to reach the
successor, which does not touch `omega`. Both readings are checkable on the page.

## 4. Crash triage — the defect that had survived three attempts

`fdm` exited **2**, not 1. `rc = 1` is DAFoam's `AnalysisError`; `rc = 2` is `argparse`:

> `usage: d11o_run_script.py`
> `d11o_run_script.py: error: argument -uOffset: expected one argument`

**`argparse` treats `-1.0e-3` as an option flag**, not a value: its negative-number
matcher accepts `-1` and `-0.001` but **not exponent notation**. The negative FD
half-step was therefore never passed in **any** of the three D11 attempts, and in
attempt one that `rc = 2` sat unexamined beside four `rc = 1`s.

## 5. Cost

**0.7167 core-min gross**, prediction 1.0, cap 5.0 (`0.717×` of prediction; guard never
fired). **= $0.000613 DERIVED, NOT MEASURED**. **All of it NAMED WASTE** (§6) — no graded
quantity — netted off nothing. Calibration row **C-69**.
