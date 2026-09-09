# SUP_BOOSTER Case-3 EXACT-tier (E1) — RUN VERDICT: NOT A RESULT

**Verdict: `NOT A RESULT`** (fixed vocabulary, rule 1). Graded 2026-09-09 against the frozen
pre-registration `SUP_BOOSTER_E1_PREREGISTRATION.md` (freeze commit `c8510ff7`) by the frozen
pinned grader `grade_sup_booster.py` (blob `3c8d418a`). Triage verified first-hand by the
cfd-supervisor (§3 check-2). **The frozen E1 grader and mesh are NOT edited (rule 6);**
remediation is the pre-registered successor SUP_BOOSTER E2.

## Two independent grounds for NOT A RESULT (both verified)

1. **The frozen grader REFUSED (exit 2)** at the Gate C2 shock-angle locator:
   `graded/fine/15000: shock fit intercept 0.2792 not near apex (>5% L)`. The
   density-gradient locator (max |Δρ/Δr|) is fooled by near-wall mesh clustering
   (`GR_RADIAL=12`): the tiny near-wall `dr` inflates |Δρ/Δr| on small compression-region
   wiggles at r≈0.20–0.27 (roughly flat across x), so the fitted line is not apex-anchored.
   The apex guard correctly caught the spurious line and refused — refuse-not-degrade working
   as designed, not a physics failure.
2. **The Gate C1 (cone-surface Cp) Roache triple is DIVERGENT** (rule 5): apparent order
   p≈7.5, outside the admissible (0.1, 6.0). The fine grid moved *away* from the
   coarse/medium trend, so no CONVERGING triple and no GCI — `NOT A RESULT` whatever the
   value.

## Numbers (all three levels: rc 0, End, last Time == endTime 15000, iteratively plateaued)

| level | nCells | cone-surface Cp | dev vs TM 0.202248 |
|---|---|---|---|
| coarse | 6,000 | 0.202503 | +0.13% |
| medium | 13,500 | 0.202668 | +0.21% |
| fine | 30,375 | 0.206154 | +1.93% |

- Roache C1: **DIVERGENT**, p≈7.5 (fine value diverges from the coarse/medium trend).
- Gate C2 shock angle: **not measurable** by the frozen locator (refused).

## The physics is corroborated (this is an honest NOT A RESULT, not a physics failure)

- Independent raw-density diagnostic at x=0.597: the conical shock sits at r≈0.40–0.415;
  the Taylor-Maccoll prediction is r = 0.597·tan(33.9147°) = **0.401**. Shock angle correct.
- Cone-surface Cp is within **0.13–0.21%** of the exact TM reference (0.202248) at the
  coarse and medium levels; TM couples β↔Cp, so a correct Cp corroborates a correct shock.
- The frozen EXACT reference (`tm_reference_M2p0_tc15.json`, ODE grid-independent to 1e-13)
  and the base method are sound. The failure is instrument robustness (shock locator + a
  radial-grading choice that adds fine-grid near-wall noise), not the model or the reference.

## Cost

Graded triple measured **30.85 core-min** (coarse 243 + medium 501 + fine 1107 s wall, serial
1-rank; no stall, gross == cleaned) vs the 90 core-min cap (ratio 0.343). $0.0264 derived (not
measured, $0.0513/core-h). Recorded in `docs/COST_CALIBRATION.md`.

## Successor

**SUP_BOOSTER E2** (§2bc fix-until-runs — a diagnosed, pre-registered, costed successor, not
a blind retry and not a silent edit to frozen E1): a fresh pre-registration + a new grader
with a shock locator robust to near-wall clustering + a gentler radial grading so the fine Cp
triple is asymptotic/CONVERGING. Keeps the EXACT TM reference and the E1 gate bands (C1
±0.010, C2 ±1.0°, Celik Fs=1.25). See `SUP_BOOSTER_E2_PREREGISTRATION.md`.

*Artifacts:* graded runs `verification/runs/navier_class/SUP_BOOSTER/graded/{coarse,medium,fine}/`
(rc.solve, log.rhoCentralFoam, STATUS, time dirs to 15000); refuse text
`.../graded/verdict_stdout.txt`; frozen prereg `SUP_BOOSTER_E1_PREREGISTRATION.md` (`c8510ff7`);
frozen grader `verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster.py` (`3c8d418a`).
