# T11 — transient conduction, plane wall, Bi = 1, Fo_end = 0.2 — RESULTS (EXACT tier)

**Rung verdict, as printed by the frozen comparator: `PASS` ×3 (G1, G2, G3), every triple CONVERGING, planted-zero control PASS.** V-column only (analytic reference; no experimental band exists at this tier). Record written 2026-08-26T21:01:27Z by the heat-transfer supervisor from the on-disk grade artefacts; every number below is the comparator's printed word (`verification/runs/T-family/T11_runs/grade_t11.log`, `gate_t11.json` blob `f71207c3`), none is the supervisor's.

Pre-registration: `docs/campaigns/T-family/T11_PREREGISTRATION.md` (frozen `ca9aad86`; AMENDMENT 1 `352aef0d` pre-first-compute, `P_MIN` 0.5 ruled `[lab-attributed]`; AMENDMENT 2 `f5f67de7` post-compute disclosure-only, control C-T wrapper). Comparator `analyse_t11.py` blob `ca391ddf` = the AMENDMENT 1 freeze (`ca391ddf`). Cost row `C-118` (`6becf266`), control C-T `C-121` (`3def5d39`).

**Why this record is late.** The grade ran and the verdicts were boarded at 16:11Z 2026-08-26 (LAB_STATE heat-transfer §2, certonomous-70), the ledger rows were committed, but the run tree, the gate file and the grade log were never committed — a ledger row is not an evidence record (verification supervisor's audit, 2026-08-26 ~21:05Z). This commit lands them; nothing is re-graded and nothing in the gate file is edited.

## Completion (rule 4, strict) — three levels DONE
| level | STATUS rc | wall s | steps | worst final residual | DONE |
|---|---|---|---|---|---|
| T11_PW_c | 0 | see `STATUS.T11_PW_c` | 40 000 | 3.01e-17 | `DONE.T11_PW_c` |
| T11_PW_m | 0 | see `STATUS.T11_PW_m` | 40 000 | 5.28e-17 | `DONE.T11_PW_m` |
| T11_PW_f | 0 | see `STATUS.T11_PW_f` | 40 000 | 3.19e-16 | `DONE.T11_PW_f` |

Reference verified before comparison (route B, independent): PDE residual 4.16e-07, insulated face 2.72e-06, Robin face 4.89e-06, initial 4.88e-06, mean-vs-quadrature 2.48e-15 — all within tolerance.

## Planted-zero control (rule 3) — PASS
Plant 1.234e-03 at line 24, recovered 1.234e-03; negative arm 0; demonstrated detection floor 1e-07 (ladder 1 → 1e-07 recovered at every decade).

## Graded rows — band ±1e-4 relative, r = 2, Fs = 1.25
| row | quantity | reference | fine | rel dev | triple (c, m, f) | state | p | GCI | utilisation | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| G1 | θ_mean (stored energy) | 0.8515954577 | 0.8515962820 | +9.679e-07 | 0.8515991988, 0.8515968654, 0.8515962820 | CONVERGING | 2.000 | 2.85e-07 | 0.97 % | **PASS** |
| G2 | θ at x* = 0 (centreplane) | 0.9506417785 | 0.9506413850 | −4.139e-07 | 0.9506572225, 0.9506445525, 0.9506413850 | CONVERGING | 2.000 | 1.39e-06 | 0.41 % | **PASS** |
| G3 | θ at x* = 1 (convective face) | 0.6433907845 | 0.6433948285 | +6.285e-06 | 0.6434213622, 0.6434001216, 0.6433948285 | CONVERGING | 2.005 | 3.41e-06 | 6.3 % | **PASS** |

Richardson extrapolations are REPORTED ONLY in `gate_t11.json`, never graded. The AMENDMENT 1 floor (`P_MIN` 0.5) fired on no row.

## Control C-T (P3) — CORRECT
`deltaT` halved at level f (`T11_PW_f_CT`, wrapper `run_one_t11_ct.sh`, AMENDMENT 2): θ_mean 0.851595967 vs 0.851596282, ΔG1 = −3.149e-07 = 0.37 % of the band; P3 (< 10 %) CORRECT; the halved step moved f toward the exact value (rel dev 9.68e-07 → 5.98e-07). Read through the frozen `analyse_t11.read_theta` (`read_ct_t11.py`, `read_ct_t11.log`).

## Cost (rule 12)
Ladder 0.050 core-min measured vs POINT 0.123 (ratio 0.41, overhead-dominated below ~1e3 cells), waste 0, $0.00004 derived, not measured — `C-118`. C-T 0.050 core-min, ratio 0.36 — `C-121`.

## What this earns, and what it does not
Capability-grid cell **conduction · laminar (n/a) · 1-D plane wall solved on a 2-D OpenFOAM mesh**: CAN DO on an analytic reference — three PASS rows, three CONVERGING triples at p ≈ 2, GCI ≤ 3.4e-06, planted control seen at 1e-07. It earns nothing conjugate, nothing convective, nothing 3-D, and the EXACT tier carries no experimental band (tier definition remains Sanaa's). Disclosure carried: `mark_done_t11.py` makes `capped` a completion conjunct (L-342 audit `6812b444`; never fired — every STATUS carried it); forward-only.

## Files landed with this record
`T11_runs/`: instruments (`analyse_t11.py`, `exact_t11.py`, `build_t11.py`, `mark_done_t11.py`, `launch_t11.sh`, `run_one_t11.sh`, `run_one_t11_ct.sh`, `read_ct_t11.py`), `gate_t11.json`, `grade_t11.log`, `read_ct_t11.log`, `STATUS.*`, `DONE.*`, launch logs, and the four case trees **except each case's `log.solve` (> 1 MB text, over the repository's 1 MB text limit; on disk, cited by path, not committed).**
