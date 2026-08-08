# S1 — weighted reinversion arm: both gates FAIL as registered, the mechanism does exactly what the loss says, and the split names the next decision precisely

Date: 2026-08-08 UTC, one session kill spanned (the setsid driver completed on its
own budget guard through it — third time this doctrine has paid). Item
`s1-cbfs-weighted-reinversion-arm`, approved d1b2c117, executed strictly in the gate
order (A control → B FD → C optimization), pre-reg commits 33f18095 / 06aeb417 /
8d817b2b before each step's solves. Evidence:
`/home/ubuntu/certonomous-runs/S1-cbfs-weighted-arm/` (masked control, weighted
anchor, FD logs, driver, per-eval logs, `ledger.csv`, final fields at
`cbfs_inv/2500/`). **Total: 229.07 core-min of the 250 hard cap.**

## Gate ledger, in execution order

| gate | measured | verdict |
|---|---|---|
| A — masked-beta nonlocality control (stop bar R ≥ 0.70; prediction ≥ 0.80) | R_W1 0.9458, R_W2 0.9283 — 99.6% of the window fix survives amputation of every out-of-window deviation | **PASS** |
| B — refpoint prints 5319/3591; Jw cross-check 27.4659; FD 3 comps < 1% | exact / 27.465931825190644 / 0.033%, 0.007%, 0.029%, no sign flips, ONE adjoint (676 iters, reason 2) | **PASS** |
| C eval-1 control (Jw_raw = host-side 1.9694433692980655 to ≥10 digits) | reldiff exactly 0.0 | PASS |
| C final-state control (cold reproduction of eval-7 Jw) | 1.5691341426975098, all digits | PASS |
| **C — G1w: normalized Jw ≤ 0.05320** | **0.05713** (warm start 0.07170; retention floor cleared, −20.3%) | **GATE FAIL** |
| **C — G2: > 50% top-decile \|beta−1\| in window** | **42.7%** (equal-weight run: 26.9%) | **GATE FAIL** |
| C — hurt cap: W2 hurt < 10% of gross | 1.33% | PASS |

Trajectory (J_history_main.csv, complete): 0.07170 → 0.07116 → 0.06698 → 0.06502 →
0.06107 → 0.06042 → **0.05713** over 7 evaluations, 6 accepted iterations,
**stopped by the driver's own budget guard (220.53 + 20 projected > 238), still
descending at ~0.004/eval**. The first two evaluations ran concurrently with the A3
arm and billed 27.1 and 26.5 core-min against the 18.9 uncontended basis — the
contention cost (~16 core-min) is exactly the missing 8th evaluation. Recorded
budget-capped, not converged (charter §4).

## Reading the two fails together — the finding

1. **G1w missed by 7.4% relative with one evaluation unpurchased.** Linear
   extrapolation of the last three steps puts eval 8 at ~0.053, on the bar. This is
   a budget verdict, not a structure verdict — and it is recorded as FAIL because
   the bar was the bar.
2. **G2 rose 26.9% → 42.7% and the correction moved exactly where the loss looks:**
   top-decile membership is now **79.7% inside the W2 support** (42.7% window +
   37.0% recovery strip), **0.0% at y>2** (was 31.5%), 14.5% upstream (was 39.6%).
   The y>2 free-channel error sits at the masked-control level (9.48 vs baseline
   9.91) — the weighted loss abandoned the reference-level mismatch as designed, and
   its relocation there collapsed (hurt 0.57 vs the equal-weight run's 1.15).
   **The pre-registered prediction (window share > 50%) was WRONG, graded as such:**
   the recovery-floor strip is inside the loss support, it held 30% of the W2 error
   at the warm start, and the optimizer legitimately spent its late effort there —
   effort G2's window-only accounting does not count.
3. Sign expectation, strongest yet: **92.3%** of top-decile cells below 1
   (nu_t-raising); 212 cells pinned at 0.2, none at 4.0; rms|beta−1| = 0.1111.
4. Equal-weight varU at the weighted optimum: 1.911e-4 — within 20% of the
   equal-weight run's 1.590e-4 while never optimizing for 74% of the domain. The
   window R at the weighted optimum is 0.9385 (vs 0.9494 full equal-weight beta).

**What the arm establishes:** localization follows the loss support cell-for-cell
(79.7% vs the 14.1% support base rate), the free-channel pathology is gone, and the
window answer survives every control. What it does not establish: a G2 pass under
the window-only accounting — that would require either the 8th-eval completion
(G1w's question) plus further window concentration, or a W1-only (window-only-loss)
arm whose support matches G2's accounting term-for-term.

## Decision handed to the chief (nothing filed beyond this record)

- **Option 1 — completion:** ~28 core-min over cap buys eval 8 + write-out and
  decides G1w cleanly; G2 under window-only accounting would likely remain 40s%.
- **Option 2 — W1-only arm:** the FD-gated machinery, boxes, driver, and warm-start
  protocol are all built; a window-only loss is a one-box config, and its G2 is
  apples-to-apples with the bar. ~150 core-min class.
- **Option 3 — rule on the accounting:** the entry-12 outcome closed G2-bar
  *revisions*; whether "79.7% in the loss support, 0% in the free channel" already
  answers the localization question the bar exists to ask is a supervisor reading,
  not a bar change. Stage 2 remains held either way (ruling 3 conditions training on
  gates PASSING; they did not).

## Regularization provenance (for the S1-with-priors line, per CAPABILITY_STRATEGY 47e52caa)

Every lambda this family has used, with grounds and achieved posteriors-relevant
fractions, in one place:

| run | lambda_QoI | lambda_L2 | ground | achieved penalty / QoI_post |
|---|---|---|---|---|
| equal-weight (corrupted) | 65.448 = 1/1.5279e-2 | 1e-4 | Wu/Zhang band top, pre-declared | 0.057% (plateau was the penalty balance: \|g_pen\|/\|g_QoI\| 0.998) |
| equal-weight (repaired) | 1625.78 = 1/6.1509e-4 | 1e-5 | 10x cut, disclosed reasoning in prereg §5 | 1.58% |
| weighted arm | 1/27.46593 (raw Σd² over W2) | 1e-5 kept | part C prereg; 3.4% of warm-start QoI | 4.54% |

All three runs sit below Wu/Zhang's 10–20% convention; the L2-to-1 prior in a
Bayesian reading is a Gaussian prior on beta with precision 2·lambda_L2/sigma², and
the plateau-balance measurement from the corrupted run (gradient cancellation at
rms 0.0165) is a direct observation of where that prior's pull equals the likelihood
gradient — the calibration point a posterior-uncertainty treatment should reproduce.
Bounds [0.2, 4.0] truncate the prior; 212–224 cells sit on the lower bound in every
converged field (the posterior mass the truncation hides). Full lineage:
`S1_CBFS_INVERSION_PREREGISTRATION.md` §2, `S1_CBFS_REINVERSION_PREREGISTRATION.md`
§5 / Amendment 1 §D, `S1_CBFS_WEIGHTED_ARM_PREREGISTRATION.md` Part C.

## Ledger (ledger.csv, START/END epochs per line)

| stage | core-min |
|---|---|
| A: masked control + reconstruct | 7.83 |
| B: source-inspection greps (manual line) | 0.50 |
| B: weighted anchor (compute_totals) | 16.83 |
| B: FD sweep, 6 primals | 43.80 |
| C: evaluations 1–7 (evals 1–2 contended with A3, 27.1/26.5) | 151.57 |
| C: final-state control + write-out + centres | 8.54 |
| **total vs 250 hard cap** | **229.07** |

## Continuity

One session-limit kill (~03:40Z) landed mid-optimization; the setsid driver ran to
its own budget stop unattended and the resume found `DRIVER DONE` and a complete
checkpoint train. Reconciliation was, again, a file read.

## Related

- `S1_CBFS_WEIGHTED_ARM_PREREGISTRATION.md` (parts A/B/C, each committed pre-solve)
- `S1_CBFS_WEIGHTED_LOSS_VARIANT.md` (the offline verdict this arm tested in the flow)
- `S1_CBFS_REINVERSION_RESULT.md`, `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` entry 12

---

## Addendum — dated 2026-08-08 ~23:0x UTC: the eval-8 completion (budget amendment 1, b0e31fa5; chief approval d66f82a5)

The approved completion ran as amended: warm restart from `beta_final`, two
evaluations, hard stop, **267.07 core-min against the amended 278 cap**.

- **Eval 8a (re-anchor/control):** Jw_raw = 1.5691341426975098 — reproduces the
  final-state control to **all digits, reldiff exactly 0.0**; ‖g‖ = 8.453e-3 matches
  the eval-7 record.
- **Eval 8b (the step):** ACCEPTED, J_qoi **0.05713020 → 0.05710277** (−2.7e-5).
- **G1w: FAIL, final** — 0.05710 against the original ≤ 0.05320 bar, graded at the
  restart's last accepted iterate per the amendment's no-relitigation clause.

**Read honestly, both ways.** The −0.004/eval extrapolation that motivated the
completion did NOT materialize: the restart's first step is steepest descent under
cold curvature (the amendment disclosed exactly this), and it bought 150x less than
the live optimizer's recent steps. What a live 8th evaluation with six curvature
pairs would have achieved is now unmeasurable — the kill destroyed that state — so
the record says: **G1w failed at every state actually reachable within the approved
budgets, and the budget-limited hypothesis for G1w is UNRESOLVABLE as posed, not
vindicated.** The arm's standing conclusions are unchanged: localization is
answered (d66f82a5 item 1), the W1-only arm decision is the chief's go/no-go with
this number in hand, Stage 2 stays held.

`beta_final_ext.npy` (the accepted eval-8b iterate) is on disk, unwritten to fields
per the amendment; a field write-out is a separate ~8.5 core-min decision if wanted.
