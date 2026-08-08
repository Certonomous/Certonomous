# W1 hump at challenge conditions + QCR2000 arm — results

Run 2026-08-07, against `W1_HUMP_CHALLENGE_PREREGISTRATION.md` (committed
`74797a57` before any solve). Items: `w1-hump-challenge-conditions`
(repriced 60 → 6 by dated docket correction, same commit line) and
`f6a-hump-qcr-arm-on-the-challenge-run` (8 marginal, run under the
negative-verdict review's §2 pre-approval). Solves: native openfoam2606
`simpleFoam`, 4 MPI ranks each, setsid, registry entries
`w1hump_challenge_sst_20260807T224139Z` and
`w1hump_challenge_sstqcr_20260807T224152Z`. Run dirs
`/home/ubuntu/certonomous-runs/w1-hump-challenge/{sst,sst_qcr}`; staged
evidence `campaign/W1_hump_runs/`.

Mesh-standard note (guidelines §2.1): the shipped 51,626-cell challenge
mesh, unchanged from F6a, whose record carries its provenance and
cross-checks; no new mesh was built, so F6a's mesh record governs. Both legs
converged on the shipped `residualControl` (U/p/k 5e-7, omega 1e-10): SST in
1922 iterations, SST+QCR in 1637 — the cap (5000) never engaged, so the
convergence criterion is the registered one, not a watcher number.

## Gate V — verification: PASS

| quantity | fresh SST leg | F6a reference | Δ | tol |
| --- | --- | --- | --- | --- |
| separation x/c | 0.65442 | 0.6544 | +0.0000 | ±0.005 |
| reattachment x/c | 1.25314 | 1.2534 | −0.0003 | ±0.005 |

Both inside NASA's own published SST window as well (sep ≈ 0.654; reatt
1.25–1.27). The pipeline reproduces the verified answer; physics sentences
below are earned.

## Gate P — physics vs CFDVAL2004 (±5%, pre-registered)

| leg | separation x/c (exp 0.665) | verdict | reattachment x/c (exp 1.100) | verdict |
| --- | --- | --- | --- | --- |
| SST | 0.6544 (**−1.59%**) | PASS | 1.2531 (**+13.92%**) | **FAIL** |
| SST+QCR2000 | 0.6538 (**−1.68%**) | PASS | 1.2553 (**+14.12%**) | **FAIL** |

The reattachment FAIL on a verified pipeline is the result the
pre-registration predicted: the documented linear-eddy-viscosity
bubble-length bias, now confirmed at the challenge conditions on both
constitutive forms.

## QCR arm — outcome two, exactly as the materiality bar defines it

Single change between legs: `kOmegaSSTQCR` (the round-5 duct library). Bar:
material = moves reattachment **toward** 1.100 by > 0.010 x/c.

| quantity | SST | SST+QCR | Δ (QCR − SST) |
| --- | --- | --- | --- |
| separation x/c | 0.6544 | 0.6538 | −0.0006 |
| reattachment x/c | 1.2531 | 1.2553 | **+0.0022** (away from experiment) |
| bubble length x/c | 0.5987 | 0.6015 | +0.0028 (+0.5%) |

**Verdict: outcome two.** The QCR2000 constitutive term does not touch the
hump's bubble length (+0.0022, below the 0.010 bar and in the wrong
direction). The constitutive/anisotropy route is ruled out on this leg; the
deficit is in the separated-shear-layer stress magnitude — the omega budget
— per the review's own dichotomy.

### The cross-leg comparison (the arm's deliverable)

| leg | flow class | QCR2000 effect | reading |
| --- | --- | --- | --- |
| ducts (round 5, on record) | secondary flow of the second kind | AR_1 0.0811→0.0455, AR_3 0.0775→0.0400 — large | anisotropy IS the missing physics; QCR resurrects it |
| **hump (this run)** | 2D separated shear layer / bubble | reatt +0.0022 x/c — null | anisotropy is NOT the missing physics; shear-stress magnitude is |
| hills (`f6b-qcr2000-on-the-hills`, approved 12) | 2D separated shear layer, APG | **pending — not yet run** | the two-leg pattern's second leg; this row must come from its own pre-registered run, not from this one |

The pattern so far is clean: QCR2000 repairs what Boussinesq structurally
cannot represent (normal-stress anisotropy driving secondary flow) and does
nothing for what Boussinesq mis-scales (turbulent shear stress in a
separated layer). If the hills arm lands the same way, that is one sentence
for the class; the hills row stays empty until its own run says so.

**Dated addendum, 2026-08-08:** the hills arm has now run its own
registration (`F6b_QCR_PREREGISTRATION.md`, results `F6b_QCR_RESULTS.md`):
**outcome N, +0.034 x/h away from the band against a 0.10 bar** — the
pending cell above resolves to null and the class sentence is earned. The
row above is left as written per the correction conventions.

## Predictions, scored clause-by-clause

1. Gate V within ±0.005 — **TRUE** (0.0000 / 0.0003).
2. SST Gate P: separation PASS at −1% to −2%, reattachment FAIL at +12% to
   +16% — **TRUE on all clauses** (−1.59%, +13.92%).
3. QCR outcome two, |Δreatt| < 0.03 and < 0.010 — **TRUE** (0.0022).
4. Cost: SST ≤ 6, QCR ≤ 8 — **TRUE** (5.58, 4.71).

## Cost (measured vs approved; basis labels per P-6.2)

| item | approved | measured | basis |
| --- | --- | --- | --- |
| SST leg (`w1-hump-challenge-conditions`, repriced) | 6 | **5.58** core-min (83.68 s wall × 4 ranks) | gross, wall × ranks, direct measurement; no ledger rows, no stall cleaning applicable |
| QCR arm (`f6a-hump-qcr-arm-on-the-challenge-run`) | 8 | **4.71** core-min (70.59 s wall × 4) | gross, same rule |
| decompose/reconstruct/extraction | — | < 0.3 core-min | gross, same rule |
| **total** | **14** | **~10.6** | |

The repricing verdict on itself: the corrected 6 was right (5.58 measured,
within the factor-3 rule); the original 60 would have been wrong by 10.8×.

## Docket

- `w1-hump-challenge-conditions`: gate reached, both gates decided —
  closable as done (outcome recorded on the entry).
- `f6a-hump-qcr-arm-on-the-challenge-run`: executed with the challenge run
  per its own contingency clause; outcome two recorded; the cross-leg table
  above is the deliverable, with the hills cell honestly pending.
