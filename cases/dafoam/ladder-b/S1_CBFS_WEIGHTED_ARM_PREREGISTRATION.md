# S1 — weighted reinversion arm: pre-registration, staged per the d1b2c117 gate order

Item `s1-cbfs-weighted-reinversion-arm`, approved by chief ruling d1b2c117 at
**250 core-min hard cap**, gated in order: (A) masked-beta nonlocality control with a
stop-and-report trigger, (B) FD gate on the new objective configuration, (C)
pre-registered optimization. **Each part commits before its own solves run**; this
file grows by dated parts, never edited silently. Run root:
`/home/ubuntu/certonomous-runs/S1-cbfs-weighted-arm/` (own `ledger.csv`; case is a
copy of the REPAIRED reinversion case — benchmark inlet, `-primalTol 1e-8` protocol
throughout, `--cpus=2`, 4 ranks, strict queueing, setsid, per the standing
discipline).

## Part A — masked-beta nonlocality control (committed before the solve)

**Question:** does the achieved in-window fix ride on out-of-window beta through the
flow? Offline analysis could not rule it out (beta acts nonlocally); this is the one
solve that answers it, and per d1b2c117 it guards the remaining ~242 core-min.

**Construction, already on disk and verified:** `beta_masked.npy` = eval-16
`beta_final` where the serial cell (via the exact DV→serial permutation) lies in the
W2 support (window 0≤x/h≤6, 0≤y/h≤2, or y<0.5 anywhere), 1.0 elsewhere. 2,970 of
21,000 DVs keep their achieved values; 2,188 reset-to-1 cells had deviated by more
than 0.05 — the masked field is a real amputation, not a no-op.

**Protocol:** one fresh-container cold `run_model` at `-betafile beta_masked.npy
-primalTol 1e-8` (~8 core-min), fields written at 2500, reconstructed; R_W1 and R_W2
recomputed host-side against the repaired baseline (340 fields), identical arithmetic
to the offline variant.

**Prediction, stated now:** the window fix is mostly local — masked beta retains
**R_W1 ≥ 0.80** (achieved value to beat: 0.9494 with full beta; equal-weight varU will
of course regress toward baseline in y>2, which is expected and not the metric).

**Stop trigger, fixed now (d1b2c117 clause a):** proceed to Part B only if
**R_W1(masked) ≥ 0.70 AND R_W2(masked) ≥ 0.70**. Below either bar, the arm's premise
is weakened — the in-window fix rides on out-of-window beta — and the item STOPS with
the measurement reported to the chief before any further spend.

*Committed before the control solve runs. Parts B and C do not exist yet; they are
written only after the control verdict, each before its own solves.*

---

## Part A result (dated 2026-08-08 ~03:1x UTC) — control PASS, arm proceeds

One cold `run_model` at `beta_masked.npy`, 7.80 core-min (`log.maskctl`, converged
protocol as registered): **R_W1(masked) = 0.9458** against full-beta 0.9494 — the
window fix retains 99.6% of its reduction with every out-of-window deviation
amputated. R_W2(masked) = 0.9283 (vs 0.9468). Both far above the 0.70 stop trigger;
the prediction (≥ 0.80) is exceeded. Confirmatory detail: the y>2 error reverts
toward baseline (9.448 vs baseline 9.914; full beta had pushed it to 7.774) — the
out-of-window beta was serving the free channel and only the free channel. W2 hurt
census under masked beta: 1.01%. **The nonlocality concern is measured dead; the
optimization will warm-start from `beta_masked` (disclosed: L-BFGS-B curvature starts
cold — scipy carries no cross-process Hessian state).**

## Part B — FD gate on the weighted objective configuration (committed before its solves)

**The new objective, exactly:**

```
Jw_raw = 5319 * varUwin + 3591 * varUrec        (= sum of |U-UData|^2 over the W2 support)
```

- `varUwin`: DAFoam `variance`, mode=field, **source=boxToCell**, box min (0, 0, −1),
  max (6, 2, 1) — the G2 window, 1,773 cells (no cell centre sits on any box face;
  verified against the centres field).
- `varUrec`: same, box min (6, −1, −1), max (16, 0.5, 1) — the recovery-floor strip,
  1,197 cells. The two boxes are disjoint and their union is cell-for-cell the
  2,970-cell W2 support the masked control validated.
- Coefficients 5319/3591 = 3 x cell-count (the variance function divides by its
  nRefPoints = 3 per cell for a 3-component vector; the printed "Find N reference
  points" must show 5319 and 3591 or the item stops).
- Composition: an `om.ExecComp` sums the two function outputs into the single
  objective `Jw`; reverse mode seeds both partials into **one** state-adjoint RHS, so
  the per-eval cost stays one adjoint. This claim is not assumed — it is exactly what
  the FD gate verifies end-to-end, and the anchor's wall time is reported against the
  one-adjoint ~20 core-min basis.
- **Cross-check, fixed now:** the anchor's Jw_raw at beta=1 must reproduce the
  offline W2 baseline **27.4659** (host arithmetic on the same fields) to ~4 digits.

**FD protocol (the established discipline, unchanged):** anchor `compute_totals` of
Jw at beta=1, `-primalTol 1e-8` (~20 core-min); central differences h=0.05, fresh
container + cold reset per point, 3 components from the top of the weighted
gradient's |g| distribution, serial locations reported **via the exact permutation**
this time. **Bar: all three rel errs < 1%, zero sign flips; a miss stops the item
before the optimization spends anything.** Est: anchor ~20 + 6 primals ~48.

*Committed before any Part B solve. Part C is written after the FD verdict, before
any optimization eval.*

---

## Part B result (dated 2026-08-08 ~03:5x UTC) — FD gate PASS, every fixed check met

Anchor (`log.anchorw`, 16.83 core-min): reference-point prints **5319 and 3591
exactly**; **one** adjoint solve (reason 2, 676 iters, 344 s — the ExecComp
composition added no second solve, and the anchor came in UNDER the one-adjoint
~20 basis); **Jw_raw = 27.465931825190644 vs the fixed 27.4659 cross-check** (6
digits). FD at the amended protocol, serial locations via the exact permutation
(all three in the separated shear layer, ranks 1/4/10 of |g|):

| DV | serial cell (centre) | central FD | adjoint g[i] | rel err |
|---|---|---|---|---|
| 5363 | 187 (0.446, 0.995) | 2.446580640724e+00 | 2.447392936993e+00 | **0.033%** |
| 5491 | 471 (1.089, 0.900) | 1.696887479641e+00 | 1.696765133887e+00 | **0.007%** |
| 5361 | 185 (0.119, 1.018) | 1.213798837353e+00 | 1.214147250266e+00 | **0.029%** |

Zero sign flips, all under the 1% bar. Arm spend at this writing: **68.96 of 250.**

## Part C — the weighted optimization (committed before any optimization eval)

- **Warm start: `beta_masked`** (per Part A's disclosed decision). L-BFGS-B curvature
  starts cold; same optimizer settings and [0.2, 4.0] bounds as every S1 run.
- **Objective:** J = LQOI_w · Jw_raw + LL2 · Σ(beta−1)², LQOI_w =
  **1/27.465931825190644** (normalized Jw = 1 at beta = 1), **LL2 = 1e-5 kept**
  (disclosed: at the warm start the penalty term is 0.00245 against a QoI term of
  0.07170 — 3.4% of the warm-start QoI, inside a subordinate-prior regime; achieved
  fraction reported vs the 10–20% band as always).
- **Eval-1 control, fixed now:** the driver's first evaluation (at `beta_masked`)
  must reproduce Jw_raw = **1.9694433692980655** (host-side Σ_W2 from the maskctl
  fields) to ≥ 10 digits — same-protocol state reproduction, the control this arm's
  warm start admits.
- **Budget:** EVAL_CAP = 8, BUDGET_STOP = 238 (of the 250 hard cap; ~12 reserved for
  final write-out + audit), EVAL_EST = 20. Checkpoints and self-ledger unchanged from
  the S1 driver (driver deltas disclosed in the record with a diff).
- **Gates, fixed now:**
  - **G1w:** final normalized Jw ≤ **0.05320** — i.e. the weighted run must
    match-or-beat on the W2 support what the full equal-weight beta achieved there
    (R_W2 = 0.9468), starting from the amputated 0.07170. A retention floor is
    included: any final above the 0.07170 warm-start value is an outright fail.
  - **G2, the point of the arm:** > 50% of top-decile |beta_final − 1| cells (global
    ranking, all 21,000, same accounting as every S1 G2) inside the window
    0≤x/h≤6, 0≤y/h≤2 — the SAME bar the equal-weight run failed at 26.9%.
  - **Hurt cap (entry-7, carried forward):** on the final fields vs the repaired
    baseline, W2-support hurt < 10% of W2 gross reduction; y>2 relocation census
    reported loudly, no cap.
- **Prediction, stated now:** G2 passes — with the loss blind to y>2, the optimizer
  has no QoI incentive to grow deviations there, and the L2 prior actively shrinks
  the out-of-support remnant; top-decile membership should concentrate into the
  window and the recovery strip (window share predicted > 50%, recovery strip
  reported alongside).
- **W4 sparse-point registered variant:** defined (30-point probePoint grid, Ux), NOT
  run inside this arm unless the optimization closes with ≥ 30 core-min of headroom;
  if run, it is a re-grade of the SAME final beta under the variant loss, never a
  second optimization.
- A stop at plateau, cap, or budget is recorded as what it is (charter §4).

*Committed before the first optimization eval. Nothing below this line existed at
commit time.*

---

## Budget Amendment 1 — dated 2026-08-08 ~22:40 UTC, before the eval-8 completion launches (chief approval d66f82a5)

**Contention arithmetic, as required:** the 250-core-min budget bought 7 evaluations
of work plus ~16 core-min of the A3 arm's walltime — evals 1–2 billed 27.1 and 26.5
core-min against the 18.7–20.1 uncontended basis measured on evals 5–7 (ledger lines
eval001–eval007; the ledger bills cpus × wall with no contention discount, by
design). The descent rate held to the stop (−0.004/eval over the last three); the
shortfall is a billing artifact, which is the basis of the d66f82a5 approval.

**Material fact the approval could not have priced, disclosed before launch: the
driver is dead and "one more eval" does not exist at one eval's price.** The driver
completed via its BudgetStop exception at ~03:4xZ; the SciPy L-BFGS-B instance and
its 6 curvature pairs died with the process (no serialized state, as the equal-weight
prereg already disclosed for restarts), and the driver's own gradient-retention rule
(keep eval 1 and every 10th) deleted `grad_eval007`. The cheapest faithful
continuation is therefore a **warm restart from `beta_final` costing TWO
evaluations**: eval-8a re-anchors (J, g) at the stopped point (doubles as a control —
its Jw_raw must reproduce 1.5691341426975098 to all digits) and eval-8b takes the
step (steepest-descent-first under cold curvature, disclosed; both prior S1 restarts
accepted their first line-search trial).

**Amended numbers, fixed now:**
- EVAL_CAP = 2 (8a + 8b), **hard stop after 8b regardless of outcome**.
- Amended item cap: **278 core-min** (= 229.07 + 2 × 24 conservative under the
  current host load: a pytest suite and four vspaero workers hold load ~4; measured
  uncontended basis 18.7–20.1). No field write-out inside this amendment — the
  eval-8b beta checkpoint stays on disk and any write-out is a separate priced
  decision.
- **G1w grading, unchanged bar:** graded at the restart's last ACCEPTED iterate
  against the ORIGINAL ≤ 0.05320. If the line search rejects the single step (a
  third trial would breach the cap), the step is recorded unaccepted and **G1w
  stands FAILED at 0.05713** — no re-litigation.
- W1-only arm: launch decision held for the chief's go/no-go after this result
  (d66f82a5 item 3).

*Committed before eval-8a launches.*
