# S1 — objective repaired, and the reinversion moves: G1 passes at −74.2%, G2 fails at 26.9%, and the residual loss now names the reference, not the inlet

Date: 2026-08-07 to 2026-08-08 UTC, two session kills spanned (§8). Item
`s1-cbfs-objective-repair-and-reinversion` (claimed 197edde6; pre-registration
committed before any solve, amendment before launch — `S1_CBFS_REINVERSION_PREREGISTRATION.md`).
Parent diagnosis: `S1_CBFS_INVERSION_RESULT.md`. Evidence:
`/home/ubuntu/certonomous-runs/S1-cbfs-reinversion/` (repaired case, driver, per-eval
logs, `ledger.csv`, `J_history_main.csv`, beta checkpoints, reconstructed final fields
at `cbfs_inv/2500/`). **Total cost: 424.80 core-min against the 450 hard cap.**

## Headline, in the order the evidence forces

1. **The inlet diagnosis was right, graded on its pre-stated prediction.** Restoring
   the benchmark's own inlet profile (Ux 0.72-uniform → 0.202→1.005 profile, bulk
   0.914922; Uz noise columns byte-identical before and after — the overwrite
   fingerprint re-confirmed at repair time) collapsed the beta=1 baseline
   **24.8x**: 1.5279278906359758e-02 → 6.1509017109920479e-04, against the
   pre-registered "< 7.6e-3" (P1). Inlet-adjacent bulk ratio RANS/LES went from
   1.272 to **1.0005**. The y>2 free-channel loss share fell 85.1% → 25.6% (P2), the
   physics window rose 3.7% → 41.2%.
2. **G1 PASSES, decisively.** The normalized QoI term fell to **0.25846573** against
   the ≤ 0.70 bar — a **74.2% reduction** in 16 evaluations, where the corrupted
   objective managed 0.149% in 17. Same machinery, same optimizer, same term: the
   500x difference in achievable descent is the measure of what the inlet defect had
   been costing.
3. **G2 FAILS, recorded without softening.** 26.9% of the top-decile |beta−1| cells
   sit in the declared window (0≤x/h≤6, 0≤y/h≤2) against the >50% bar (3.2x the 8.4%
   base rate). The correction is real but not majority-localized: 39.6% of top-decile
   cells sit upstream (x<0), 31.5% at y>2.
4. **Where the inversion acted and where it could not (final vs repaired-baseline
   fields):** window error **−94.9%**, near-wall y<0.5 error **−95.9%**, y>2
   free-channel error only **−21.6%** — so the remaining loss is 77.6% free-channel.
   The floor is no longer the inlet (ratio 1.0005) and no longer the window (0.81 of
   38.75 baseline units remain there): what beta-on-omega-production cannot remove now
   lives in the trivially-matched upper channel, i.e. reference-vs-RANS mismatch at
   the LES interpolation level, not closure physics in the separated region.
5. **A protocol defect was found and fixed mid-item, disclosed by dated amendment
   before the inversion launched:** at the pre-declared primalMinResTol 1e-6 the
   repaired case's cold primal stops at the first tolerance crossing (iters 383–458)
   and central FD misses the adjoint by a systematic fd/adj ≈ 0.7 on all three cells
   (25.9–32.2%). One discriminating pair at 1e-8 collapsed the error 25.9% → 0.032%.
   Every run of the item then ran at `-primalTol 1e-8`. **FD re-verification at the
   amended protocol: 0.032% / 0.115% / 0.009%, zero sign flips** — the sub-LU adjoint
   is re-anchored on the repaired objective (cells 5363 step crest, 5428 downstream
   recovery, 5491 upstream channel; anchor gradient ‖g‖ = 1.2218e-4, 8.4x the
   corrupted objective's).

## 1. What ran

Pre-registered configuration as amended: repaired case at
`S1-cbfs-reinversion/cbfs_inv/` (corrupted case left untouched as evidence), host-side
SciPy L-BFGS-B (maxcor 10, maxls 8, ftol 1e-10, gtol 1e-6, bounds [0.2, 4.0]), fresh
`dafoam-subpclu:v1` container per evaluation (`DAFOAM_SUBPC_TYPE=lu`, 4 ranks,
`--cpus=2`, cold reset, cold start, `-primalTol 1e-8`),
J = 1.6257778891393064e+03 · varianceU + 1e-5 · Σ(beta−1)², beta on the SST omega
**production** term (21,000 DVs). Production-term-labeled: nothing here is comparable
to Wu/Zhang's destruction-term numbers (C2, R6). Driver deltas vs the failed run's
file are listed exhaustively in Amendment 1 §E; optimizer and checkpoint mechanics
byte-identical.

## 2. Trajectory (J_history_main.csv, complete at the checkpoints that moved)

| eval | varianceU | J_qoi (norm.) | penalty | J | beta min/max | ‖g‖₂ |
|---|---|---|---|---|---|---|
| 1 (control) | 6.1509017109920479e-04 | 1.00000000 | 0 | 1.00000000 | 1.000/1.000 | 1.986e-01 |
| 2 | 5.8974012093119795e-04 | 0.95878645 | 3.9e-07 | 0.95878684 | 0.934/1.002 | 2.168e-01 |
| 4 | 4.3853497934766451e-04 | 0.71296047 | 1.64e-05 | 0.71297691 | 0.562/1.011 | 2.199e-01 |
| 6 | 2.8361218940837173e-04 | 0.46109043 | 1.50e-04 | 0.46123999 | 0.200/1.037 | 1.765e-02 |
| 11 | 2.1794354060933769e-04 | 0.35432779 | 7.70e-04 | 0.35509801 | 0.200/1.847 | 1.568e-02 |
| 12 | 1.7664811384922332e-04 | 0.28719060 | 2.42e-03 | 0.28961238 | 0.200/3.234 | 8.966e-03 |
| 13 | 1.6939686758161472e-04 | 0.27540168 | 3.38e-03 | 0.27878610 | 0.200/3.685 | 3.383e-02 |
| 16 | 1.5897973285391003e-04 | 0.25846573 | 4.09e-03 | 0.26255989 | 0.200/4.000 | 6.780e-03 |

Descent was still active at the stop (J fell 1.6% over the last accepted step; ‖g‖
6.8e-3 vs gtol 1e-6). **The run was stopped by the driver's own pre-registered budget
guard after eval 16 (416.70 + 22 projected > 435), not by the optimizer's test:
recorded budget-capped, not converged** (charter §4). 11 accepted L-BFGS-B iterations,
every adjoint converged (reason 2), monotone accepted-J descent.

Controls: eval-1 reproduced the anchor8 baseline varianceU **bit-identically** and the
anchor8 gradient with **max abs diff exactly 0**. The final-state control (fresh cold
process at `beta_final`) reproduced eval 16's varianceU to all digits
(1.5897973285391003e-04) and wrote the fields the audit reads (`cbfs_inv/2500/`,
`writeCellCentres`, field-vs-DV sorted max diff 5.1e-15).

## 3. Gate verdicts

| act | gate | measured | verdict |
|---|---|---|---|
| repair | P1: beta=1 varU < 7.6e-3 | 6.151e-4 (24.8x collapse) | **PASS** |
| repair | P2: y>2 loss share < 50% at baseline | 25.6% | **PASS** |
| FD re-anchor | 3 components < 1%, no sign flips | 0.032% / 0.115% / 0.009% | **PASS** (after the 1e-6 protocol defect was fixed by amendment; the 1e-6 miss is on the record) |
| reinversion | G1: J_qoi ≤ 0.70 within budget | **0.25847** (−74.2%) | **GATE PASS** |
| reinversion | G2: >50% top-decile \|beta−1\| in window | 26.9% (3.2x base rate) | **GATE FAIL** |
| eval-1 control | reproduce anchor8 + gradient | bit-identical, diff 0.0 | PASS |
| final-state control | cold reproduction of final J | all-digits match | PASS |

Reported with no gate attached, per the prereg: **224 cells pinned** (223 low at 0.2,
1 high at 4.0 — the failed run had zero; the lower bound is active where the optimizer
wants production shut off harder than the pre-declared floor allows); **penalty =
1.58%** of post-optimization QoI error against Wu/Zhang's 10–20% band (the 1e-5
one-shot re-tune kept the prior subordinate — measured rms|beta−1| = 0.1396, 8.5x the
failed run's — but the fraction still lands under their band; a trial-and-error tune
remains unaffordable in-cap and the number is disclosed as achieved); qualitative sign
expectation **held** — 75.6% of top-decile cells moved below 1, the nu_t-raising
direction, the production-term mirror of Wu/Zhang's beta>1 on destruction; mean beta
in the window 0.8296.

## 4. Reading the G2 fail with the loss geography in hand

The failed run's G2 fail was an artifact of a defective loss. This one is a finding:

- The inversion **did** fix the window: 94.9% of the separated-region error and 95.9%
  of the near-wall error are gone. beta-on-production works there, in the
  nu_t-raising direction the physics expects.
- ~~The top-decile |beta−1| cells scatter (39.6% upstream, 31.5% upper channel) because
  the optimizer, having largely exhausted the window signal, spends its late
  iterations chasing the **77.6% of residual loss that now sits at y>2** — error at
  the reference-interpolation level that an interior omega-production beta moves only
  weakly (−21.6% there, at the cost of large upstream deviations).~~

  > **[AMENDED 2026-08-11, commit `a8401614`. The scatter is real; the mechanism above is
  > refuted by execution, and the original is retained struck rather than rewritten.]**
  >
  > **The geography is a property of the baseline adjoint, present before any optimisation.**
  > Scoring the published G2 definition on `grad_eval001.npy` **alone** — an evaluation-1
  > array confirmed unperturbed (penalty exactly 0.0, beta_min = beta_max = 1.000000) and
  > containing **no inversion result at all** — returns **35.38%**, with **45.8% of its top
  > decile upstream**. The baseline *loss* does not have that shape: **8.0% upstream**,
  > against 41.2% of the loss in-window on 8.44% of cells. Confirmed on a second independent
  > baseline gradient (31.19%, rho = +0.945 between the two maps) and under cell-size
  > normalisation.
  >
  > **The "late iterations" the mechanism above rests on did not happen.** The accepted
  > iterate satisfies `beta = 1 - 1.0 * g(beta=1)` to a max residual of **1.110e-16**, with
  > the step length measured — not fitted — at exactly 1. The field is one gradient step from
  > the baseline, so there is no late-iteration search to attribute the scatter to.
  >
  > **What may be said instead:** the correction's geography carries no information that is
  > not already in the baseline sensitivity map, so **G2 is scoring the adjoint rather than
  > the closure**, and the upstream deposition **may not be cited as a physics result about
  > where model-form error lives.**
  >
  > **What is NOT established, stated because the tempting conclusion overreaches.** This does
  > not refute the physical reading. The adjoint is loud upstream *because* upstream beta
  > propagates into the downstream loss — which is the very mechanism a physical reading
  > posits, so the two are not cleanly separable by this measurement and cannot be. What is
  > established is narrower and firmer than either story.
  >
  > **A fourth, independent reason the >50% bar was unreachable:** the top decile of the
  > per-cell **baseline loss** is only **32.71%** in-window. No loss-following correction can
  > clear 50%. The achieved 26.86% is **82% of the achievable ceiling**, and the operative
  > ceiling is 32.71% — not the window's 41.2% loss share.
  >
  > Evidence and reproduction scripts: `S1_SENSITIVITY_VS_ERROR.md`, commit `7224e89a`.
  > Zero solver compute; every array named with the evaluation it came from.
- The SST shear-stress limiter overlap **grew** with the correction: the limiter now
  binds on 24.8% of all cells (7.7% at beta=1 in the corrupted state) and on **51.6%
  of the top-decile cells** — lowering omega production raises k/omega, which is
  exactly the regime where nu_t = a1·k/(F23·S) takes over and the production lever
  weakens. The Dow-style parameterization question (beta on nu_t directly) stays live
  and is now supported by two independent measurements.

## 5. What this item establishes

- **A production-term beta CAN move a well-posed CBFS velocity loss** — the question
  the defective objective masked. −74.2% in 15 optimization evaluations, still
  descending at the cap.
- The repaired case, its 1e-8 protocol, the re-anchored gradient, and a beta field
  that removes ~95% of the separated-region error are on disk and reproducible
  bit-for-bit.
- The residual-loss floor has moved from "our inlet is wrong" to "the all-cells
  variance objective grades free-channel interpolation mismatch" — which is an
  argument, quantified, for Wu/Zhang's own sparse-points-in-the-separation-region
  loss as the next objective variant, and it is measured, not speculated.

**For Stage 2 — leakage position, stated explicitly:** CBFS is the benchmark's
field-inversion TRAINING case; the loss reads only CBFS's own LES (`0/UData`);
nothing scored was touched at any point. `beta_final` is therefore **training-legal**
as Stage 2 input. But the pre-registration tied Stage 2 hand-off to "if gates pass",
and G2 failed: the field's correction is real in the window (where Stage 2 would
harvest beta(features) pairs) yet 73.1% of its strongest deviations sit outside it,
partly chasing reference-level error. **Whether Stage 2 trains on this field, on its
window-restricted subset, or waits for a sparse-point re-run is a supervisor call —
this record hands over the field with its geography measured and takes no
generalization position.**

## 6. Follow-ups this run points at (filed as candidates, not self-approved)

1. **Sparse-point separation-region loss** (Wu/Zhang's own): removes the y>2
   free-channel term that both runs' G2 verdicts foundered on. The probePoint
   DAFunction would need its own FD gate first.
2. **w3-beta-on-omega-destruction-model-patch** (spec ready): term-parity, now on a
   repaired objective — the comparison this lab could not make before.
3. **Dow-style nu_t-discrepancy parameterization**: the limiter-overlap measurement
   (49.5% on the corrupted state, 51.6% here, base rate tripling under correction) is
   two-for-two in flagging the production hook's structural weakness in exactly the
   cells that matter.

## 7. Ledger (ledger.csv, every line START/END epochs)

| stage | core-min |
|---|---|
| stage A: re-baseline primal + reconstruct (P1/P2 graded) | 1.73 |
| stage B: FD anchor at 1e-6 (superseded, disclosed) | 15.13 |
| stage C: FD sweep at 1e-6 — the miss that bought the diagnosis | 8.84 |
| tol-1e-8 diagnostic (base + one pair) | 20.84 |
| stage B2: anchor8 + remaining FD pairs at 1e-8 | 50.03 |
| evaluations 1–16 (fresh-container compute_totals at 1e-8, --cpus=2) | 320.13 |
| final-state cold control + write-out + centres | 8.10 |
| **total vs 450 hard cap** | **424.80** |

Post-processing (loss geography, G2, limiter masks, penalty fraction) was host-side
arithmetic on written fields, zero solver compute.

## 8. Continuity note

Two kills spanned this item: 2026-08-07 ~22:20Z (credit exhaustion — the setsid driver
kept stepping straight through it; reattached at 22:39Z with the ledger reconciling to
the digit) and 2026-08-08 ~00:50Z (credit exhaustion again — by which time the driver
had **already finished on its own budget guard** and written `beta_final.npy`; the
resume found a completed run, not a casualty). Pre-registration-first plus
out-of-process execution plus per-eval checkpoints again made recovery a file read.

## Related

- `S1_CBFS_REINVERSION_PREREGISTRATION.md` (prereg + Amendment 1: the repair diff,
  P1/P2, the FD protocol defect and fix, gate numbers, driver deltas)
- `S1_CBFS_INVERSION_RESULT.md` (the failed run and the diagnosis this item executed)
- `W4_ADJOINT_PC_UNBLOCK.md` (the adjoint capability; §5c correction addendum)
- `W2_WU_ZHANG_DESTRUCTION_FIML_READING.md` (loss conventions; the w3 spec)

---

## Correction addendum — dated 2026-08-08 (weighted-loss variant prep)

The FD cell "neighborhood" labels in headline item 5 and §3's context ("step crest /
downstream recovery / upstream channel", cells 5363/5428/5491) are **wrong**: they
applied serial-order cell centres to DV-order indices. The exact DV→serial
permutation (recovered from `cellProcAddressing`, verified to 5.1e-15 against the
written beta field) places all three components in the **separated shear layer just
downstream of the crest** — serial cells 187/330/471 at (0.446, 0.995),
(0.930, 0.926), (1.089, 0.900). The FD **measurements stand unchanged** (perturbation
and gradient share the same DV indexing; 0.032%/0.115%/0.009%, no sign flips); what
is retracted is the "three distinct mesh neighborhoods" spread claim — the verified
components are the |g| ranks 1, 5, 4, clustered where the top of the gradient
distribution physically lives. The same mislabeling caveat plausibly applies to
W4 §5d's cell labels on the corrupted objective (flagged to W4's owner, not edited
here). Every loss-geography, G2, and limiter audit in this document is unaffected:
those were computed on written serial-order fields with serial centres throughout.
Full detail: `S1_CBFS_WEIGHTED_LOSS_VARIANT.md` §0b.
