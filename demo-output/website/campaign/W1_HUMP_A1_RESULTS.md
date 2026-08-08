# W1 hump a1 limiter sensitivity — results

Run 2026-08-08 against `W1_HUMP_A1_PREREGISTRATION.md` (committed `d05b83c3`
before any solve). Item `f6a-hump-a1-limiter-sensitivity`. Registry:
`w1hump_a1_028_20260808T020440Z`, `w1hump_a1_034_20260808T020454Z`. Evidence
staged in `campaign/W1_hump_runs/{a1_028,a1_034}/`.

## Gate verdict: OUTCOME ONE — the limiter is a mechanism

| arm | a1 | convergence | separation x/c | reattachment x/c | Δreatt vs SST 1.2531 | material (bar 0.010)? |
| --- | --- | --- | --- | --- | --- | --- |
| a1_034 | 0.34 | **converged**, 1701 iterations | 0.6558 | **1.2033** | **−0.0498, toward experiment** | **YES — 5× the bar** |
| a1_028 | 0.28 | **UNCONVERGED at the 5000 cap — ungated** as registered | (0.6405) | (1.3595) | (+0.1064, away) | not gateable |

The registered outcome one requires at least one material arm: **met** by the
converged a1 = 0.34 arm. Raising the shear-stress limiter cap by 10% shortens
the bubble by 0.0498 x/c — the mis-scaled-stress hypothesis now has a
mechanism with a measured, signed sensitivity, not just the QCR-null
implication. It does not repair the gate: 1.2033 vs 1.100 is still **+9.4%**,
outside ±5% (prediction 3 held — the bias is bigger than a ±10% constant
sweep).

The a1 = 0.28 arm failed `residualControl` on the **omega clause alone**: at
iteration 5000 its initial residuals read Ux 4.8e-8, p 3.5e-7, k 5.8e-8 (all
under their 5e-7 targets) with omega at 8.6e-10 against 1e-10. Its numbers
are reported in parentheses, labelled, ungated (L-24); they are
directionally consistent with the converged curve and are not used in any
slope below.

## Reconciliation with the record this arm should have cited — and did not

Writing this file, the registry surfaced **prior a1 arms this lab already
ran**: the F6a diffusion study of 2026-08-01
(`F6a_DIFFUSION_RESULTS.md` §T1; registry `f6a_diff_SST_a1_040_…`,
`f6a_diff_SST_a1_025_…`) measured a1 = 0.40 (converged: reattachment
**1.1873**, −0.0661) and a1 = 0.25 (**NOT_CONVERGED at 10,324 iterations**,
residual floor, fragmented bubble; a bound only). Neither the review
entry-2 outcome block that ordered this arm nor this arm's own filed
proposal cited that record — a citation defect on both, recorded here,
dated 2026-08-08, per the correction conventions. The adversarial sweep
that found it is the registry grep that staged these entries.

What survives, and is sharpened, once the prior record is on the table:

| a1 | reattachment x/c | status | source |
| --- | --- | --- | --- |
| 0.25 | no gate-met scalar | NOT_CONVERGED (10,324 it) | diffusion study T1 |
| 0.28 | (1.3595) | UNCONVERGED (5,000 cap, omega clause) | this arm |
| 0.31 | 1.2531 | converged | executed SST leg |
| 0.34 | **1.2033** | converged | this arm |
| 0.40 | 1.1873 | converged | diffusion study T1 |

- The converged three-point curve is **monotone and sublinear**:
  d(reatt)/d(a1) ≈ **−1.66 per unit a1** on [0.31, 0.34] flattening to
  ≈ −0.27 on [0.34, 0.40] — the strong sensitivity sits immediately above
  the stock constant. This interior-point structure is this arm's genuinely
  new contribution; the sign itself was already on the record and this arm
  **confirms** rather than discovers it.
- The low-a1 convergence pathology is now **reproduced at a second value**:
  0.25 floored and fragmented, 0.28 stalls on omega with a still-coherent
  bubble — the pathology deepens continuously as a1 drops. Prediction 1
  ("both arms converge") was falsified by a behaviour the prior record had
  already exhibited; the pre-registration missed it for the same reason the
  proposal did.

## Predictions, scored clause-by-clause

1. Both arms converge — **FALSE** (a1_028 hit the cap on the omega clause;
   foreshadowed by the uncited 2026-08-01 record).
2. a1 = 0.34 material toward experiment, window −0.010 to −0.060 — **TRUE**
   (−0.0498). a1 = 0.28 material away — **not evaluable as gated** (arm
   unconverged); descriptive numbers consistent.
3. Neither arm repairs Gate P — **TRUE** on the converged arm (+9.4%).
4. Cost ≤ 12 — **FALSE**: measured **20.7 core-min** gross (a1_028 burned
   the full cap: 228.8 s × 4 = 15.25; a1_034 81.5 s × 4 = 5.43). Overrun
   factor 1.72, inside the charter's factor-3 grading; the un-priced term
   was, as the charter says it always is, the settling — of an arm whose
   settling behaviour was already in the record nobody cited.

## Where the question goes

The limiter is a live mechanism knob, so the omega-budget question does NOT
move upstream unexamined: the executed sequence now reads QCR null
(constitutive form exonerated) + a1 material (limited-stress magnitude
implicated, knob named, slope measured). The honest boundary: a1 is a
calibration constant, not a correction — 1.2033 is not a better model, and
no arm here is a recommendation (the diffusion study's standing disclosure
carries). The next falsifiable rung, if the chief wants one, is term-level:
which omega source term the limiter's effect is standing in for.
