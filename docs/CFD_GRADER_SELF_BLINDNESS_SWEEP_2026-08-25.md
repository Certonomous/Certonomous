# cfd sweep — grader self-blindness probes, 2026-08-25

**REPORT ONLY. NOTHING REPAIRED. NO §2d EVENT OPENED.** Every repair on a fired case is the
supervisor's ruling, one at a time.

**Instrument:** `scripts/check_grader_self_blindness.py` (Probe A = L-322 shape, divergent
dict schema on one container; Probe B = L-321 shape, fixture and checker sharing a route).
Selftest 4/4 — each probe shown able to **fire** on a planted defect and to **stay quiet** on
its clean counterpart.

**Scope:** cfd territory — `verification/runs/`, `verification/campaign/`, `cases/`,
`scripts/`, excluding T-family, F14-cooling-ladder, THERMAL_K0_runs, RANS_LES_closure_models
and dafoam.

**Coverage: 211 Python files. 204 clean. 4 ERROR files. 4 WARN files. 0 unparseable.**

## ERROR — a branch omits a key that IS read elsewhere (armed crash), or fixture and checker share a route

| # | file | finding | status |
| --- | --- | --- | --- |
| 1 | `F3_runs/conversion_2026-08-24/grade_f3.py` | `report['runs']` at L482/L487; `core_s` read at L602 | **ALREADY FIRED** — this is the crash that made F3 `NOT A RESULT`. §2d addendum ruled open; **not repaired by this lane** |
| 2 | `F11_runs/conversion_2026-08-25/rerun_f11.py` | `ledger['runs']` at L953/L964/L1021; `cost_basis`, `predicted_core_s`, `ranks`, `wall_cap_s` read at L571–L574 | **ARMED, NOT FIRED.** Hard blocker registered at `conversion_2026-08-25/DO_NOT_RERUN_rerun_f11.md`; fix is a mandatory pre-compute item in the next F11 registration |
| 3 | `F6b_runs/relax_invariance.py` | `out['arms']` at L66/L73; **`profile_scaled_mae_overall_percent`, `reattachment_x_over_h`, `separation_x_over_h` read at L103, L107, L109, L135, L136** | **NEW. ARMED.** The case has run (`relax_invariance.json`, `gate_result.json`, six arm directories on disk). Not triaged by this lane |
| 4 | `F9_work/f9_criteria.py` | **TWO instances**: `out['stationarity']` at L604/L608 and `out['cycle_convergence']` at L644/L648; **`status` read at L816 and L826 in both cases** | **NEW. ARMED.** The case has run (`f9_criteria.json`, `f9_analysis.json` on disk). Not triaged by this lane |

**Findings 3 and 4 are new and were found by the instrument, not by reading.** Neither has
been triaged, neither is repaired, and neither is claimed to have produced a wrong answer —
**an armed latent crash is not evidence that anything already graded is wrong.** What it means
is that a future execution taking the short branch raises instead of grading.

## WARN — divergent schema, but no consumer reads the divergent key today

`F3_runs/conversion_2026-08-24/grade_f3.py` (its `report['gates']` PENDING branches),
`F3_runs/conversion_2026-08-24/rerun_f3.py`, `F5c_runs/run_a4.py`,
`F5c_runs/run_stage_a.py`.

**A WARN is not harmless — it is the same defect one consumer away from becoming an ERROR.**

## A coverage gap in this sweep, stated rather than left to be found

**`verification/runs/F5b_runs/analyse_f5b_physics.py` was scanned in its WORKING-TREE state
(blob `277463b1`), which carries a half-applied repair** — its fixture was switched to `%g`
formatting, so **Probe B no longer fires on the copy that was scanned.** Probe B **does**
fire on the **committed copy at HEAD** (`6c6d34d0`, the stage-2 freeze) — L1197 fixture /
L772 checker — and **that is the artifact that cost F5b its verdict.** The working-tree file
is under a permission decision on Sanaa's desk and was not touched for this sweep. **Read the
sweep as covering 210 files in their committed state and one in a modified state.**

## What the instrument does NOT claim

From its own docstring, kept verbatim: *neither probe is a proof of correctness. They are
cheap static smells for two shapes that have each cost a graded run. A clean report is not a
guarantee; a flag is a thing to go and look at.* **204 clean files are 204 files with no
smell of these two shapes — not 204 correct graders.**
