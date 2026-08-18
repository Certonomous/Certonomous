# F6b periodic hills, QCR2000 arm — results

Run 2026-08-08 against `F6b_QCR_PREREGISTRATION.md` (committed `d05b83c3`
before any solve). Item `f6b-qcr2000-on-the-hills` (review entry 1).
Registry: `f6b_medium_qcr2000_20260808T020454Z`. Case:
`campaign/F6b_runs/medium_qcr2000/` — the verified F6b medium rung
(15,600 cells, Gate V 0.043%), `kOmegaSSTQCR` the single change.

**Deviation note, dated 2026-08-08:** the pre-registration's §1 said "same
4 ranks"; the medium rung's own `decomposeParDict` says — and its verdict
run used — **2 ranks**. The run followed the rung's own instrument
(2 ranks), and the pre-registration's misstatement is recorded here rather
than silently matched. No other clause is affected.

**Convergence:** `SIMPLE solution converged in 6177 iterations` on the
registered `residualControl` (1e-6). The registered 12,000 cap earned its
sizing: the inherited 6,000 cap — which the SST rung cleared by 3
iterations — would have guillotined this arm at 6,000 unconverged. No S12
fallback was needed.

## Gate verdict: OUTCOME N — the null generalises

| quantity | SST (verdict rung) | SST+QCR2000 (this arm) | Δ | bar |
| --- | --- | --- | --- | --- |
| separation x/h | 0.2604 | 0.2652 | +0.0048 | (not gated) |
| reattachment x/h | 7.6472 | **7.6814** | **+0.0342, away from the band** | 0.10 |

|Δ| = 0.034 < 0.10, and the movement is marginally *away* from the
4.21–4.7 literature band: **outcome N** exactly as registered. The +72%
reattachment FAIL stands untouched by the constitutive term. Prediction 2
held; the falsification branch it dared (P or R) did not occur.

## What this decides for review entries 1 and 2

The ducts-vs-hump separation **generalises to APG separation**. The
two-leg question is now a three-leg answer, all on the same untrained
QCR2000 library:

| leg | flow class | QCR2000 effect |
| --- | --- | --- |
| ducts (round 5) | secondary flow of the second kind | decisive (0.0811→0.0455, 0.0775→0.0400) |
| hump (challenge conditions) | 2D separation bubble | null (+0.0022 x/c, away) |
| **hills (this arm)** | 2D APG separation, +72% FAIL | **null (+0.034 x/h, away)** |

Class-level statement, now earned: **QCR2000 resurrects what Boussinesq
structurally cannot represent — normal-stress-anisotropy-driven secondary
flow — and does not touch separated-shear-layer bubble length on either 2D
separated leg.** The constitutive route is closed for the separated-flow
class on this record; the stress-magnitude route is open and now carries a
mechanism: the concurrent a1 arm (`W1_HUMP_A1_RESULTS.md`) measured
d(reatt)/d(a1) ≈ −1.66 per unit a1 on the hump — including the
reconciliation with the 2026-08-01 diffusion-study points the ordering
review had not cited. Entry 1's remaining open diagnostic on the hills is
the model-form matrix (`f6b-model-form-matrix-on-the-hills`, proposed, 35);
the finest-rung non-convergence successor stands unchanged.

## Predictions, scored clause-by-clause

1. Converges within 12,000 — **TRUE** (6,177).
2. Outcome N, |Δ| < 0.10 — **TRUE** (+0.034).
3. Cost ≤ 15 — **TRUE**: **9.17 core-min** gross (275.2 s wall × 2 ranks)
   vs the item's 12 approved; basis: wall × ranks, direct measurement.

## Cost and session accounting (P-6.2 basis labels)

| item | approved | measured (gross, wall × ranks) |
| --- | --- | --- |
| `f6b-qcr2000-on-the-hills` | 12 | **9.17** |
| `f6a-hump-a1-limiter-sensitivity` | 12 | 20.68 (graded in its own record) |
| session total vs the 45 hard cap | — | ≈ 43 of 45 |

**Dated citation note, 2026-08-08 (Ladder V rung V5; additive only):** the
QCR2000 term named throughout is Spalart, P. R., "Strategies for turbulence
modelling and simulations," *Int. J. Heat Fluid Flow* **21**(3), 252–263
(2000); `Ccr1 = 0.3` is that paper's published constant, untouched.
