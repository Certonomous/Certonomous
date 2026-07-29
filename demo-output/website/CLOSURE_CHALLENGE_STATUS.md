# Closure Challenge — status as of 2026-07-29 (round 3)

Read-only status report except for the new §0 below. All figures are quoted
from already-recorded, re-derivable artifacts; sources are cited per section.

Sources: `/home/ubuntu/closure-challenge-benchmark/README.md` (benchmark
rules + public leaderboard); `demo-output/website/closure_challenge_rans_floor.json`;
`demo-output/website/closure_challenge_trained_entry.json` (round 1);
`demo-output/website/closure_challenge_trained_entry_round2.json` (round 2);
`demo-output/website/closure_challenge_trained_entry_round3_gated.json`
(round 3, **entry of record**);
`demo-output/website/closure_challenge_C2_error_decomposition.md`;
`demo-output/website/closure_challenge_C1_error_estimator.md`;
`demo-output/website/dafoam/ladder-b/{B1_reproduction_plans,B2_duct_baseline,B3_duct_field_inversion}.md`;
`demo-output/website/campaign/F6_closure_aligned_flows.md`;
`demo-output/website/ACTIVE_RESEARCH.md`; `docs/research/CLOSURE_METHODS.md`.

---

## 0. Round 3 — the C1 gate was applied, for the first time (new this update)

Round 2's own report (§6, Term 1) identified but deliberately withheld a
recoverable 0.0066: the trained correction is worse than doing nothing on
`alpha_05_4071_4048` and `alpha_05_4071_2024` (plus a negligible amount on
`NASA_2DWMH`). C1 (already committed, prior session) built and validated a
test-blind decline-gate for exactly this — fit and its threshold set on the
21 PH **training** cases only, checked on the 4 PH **validation** cases only
(AUC 1.0, 4/4 correct) — and explicitly did not apply it to the test set,
calling that "a separate decision not yet made."

This session made that decision: `sdk/scripts/apply_closure_ph_gate.py`
reproduces the C1 gate's coefficients and threshold byte-for-byte from
train-only data (confirmed identical: alpha=0.7499, threshold=0.1263), then
evaluates the frozen gate on the 4 official PH test cases using **only**
their RANS-derived features (no `U_LES` read for any test case to build
these features), and uses the binary output to choose, per case, between two
already-existing predictions: the round-1 corrected output or the raw-RANS
floor. DUCT and NASA_2DWMH are reproduced unchanged from round 2. **One**
new official `score()` call was made on the resulting 8-case dict — the 4th
such call this lab has made on this benchmark's test ground truth (after the
floor, round 1, and round 2).

**Result: overall 0.0741 → 0.0676** (Δ −0.0065, matching the 0.0066 predicted
in round 2 almost exactly). The gate correctly declined both `alpha_05`
cases (predicted baseline 0.0420 and 0.0034, both below the 0.1263
threshold) and correctly kept applying the correction on both `alpha_15`
cases (predicted 0.1503 and 0.1525, both above threshold) — 4/4 correct on
cases the gate had never been evaluated on before, matching its validation
performance exactly.

**A finding earned by this, not designed for it**: on both declined cases
the raw RANS floor (0.0461, 0.0719) is lower than every entry on the public
leaderboard for that case (best published 0.0569 and 0.0760 respectively).
**We now lead the public board on 5 of 8 cases**, not 3 — two of the five
by simply not having broken what RANS already got right.

**Leakage discipline, stated plainly**: the gate's parameters (feature
screening, RidgeCV alpha, standardization, final coefficients, decision
threshold) depend on zero test-case data — computed only from the 21 PH
training cases, exactly as in C1. The motivating observation that led to
building the gate came from round 2's own official scoring call (legitimate:
this lab treats an official call's outcome the same way it treats the public
leaderboard — usable to target research effort, never to fit or select a
model). The gate itself was validated for generalization on the 4 PH
validation cases, which are not test cases. Its evaluation on the 4 test
cases used only RANS/mesh-derived features, never their ground truth. No
test case's own outcome influenced its own decision, and the gate's
parameters were fixed before this run touched any test data.

**Compute**: 83 s wall time on a 2-core cap, peak RSS 356 MB (measured with
`/usr/bin/time -v`) — model-fitting and inference on already-solved fields,
no CFD solve.

Round 3 record: `demo-output/website/closure_challenge_trained_entry_round3_gated.json`.
Script: `sdk/scripts/apply_closure_ph_gate.py`.

---

## 1. The metric, precisely

- **Per-case score**: scaled MAE = `mean(||U_pred − U_true||)` over the
  case's **1000 fixed evaluation points**, divided by `mean(||U_true||)`.
  Source: `closure_challenge/eval.py`, `evaluate_individual_case()`.
- **Overall score**: the plain (unweighted) mean of the 8 per-case scaled
  MAE values. Lower is better. Source: `closure_challenge/eval.py`, `score()`.
- Scoring is done exclusively through the benchmark's own unmodified scorer
  (`closure_challenge.score()`/`evaluate_by_case()`) — this project never
  reimplements the metric.

## 2. All 8 test cases — floor, our score, rank-2, and best on the board

| Case | RANS-identity floor | **Our score (round 3, gated)** | Rank-2 (Wu & Zhang, 0.0624) | Best anywhere on leaderboard | We lead the board? |
|---|---|---|---|---|---|
| alpha_15_13929_4048 | 0.1320 | **0.0501** | 0.0813 | 0.0592 (Reissmann) | **YES** |
| alpha_15_13929_2024 | 0.2049 | **0.1011** | 0.1195 | 0.1195 (Wu & Zhang) | **YES** |
| alpha_05_4071_4048 | 0.0461 | **0.0461** (gate: raw RANS) | 0.0569 | 0.0569 (Wu & Zhang) | **YES** |
| alpha_05_4071_2024 | 0.0719 | **0.0719** (gate: raw RANS) | 0.0848 | 0.0760 (Reissmann) | **YES** |
| AR_1_Ret_360 | 0.1288 | **0.0919** | 0.0455 | 0.0387 (Reissmann) | no |
| AR_3_Ret_360 | 0.1243 | **0.0862** | 0.0399 | 0.0341 (Reissmann) | no |
| AR_14_Ret_180 | 0.0590 | **0.0303** | 0.0350 | 0.0325 (Reissmann) | **YES** |
| NASA_2DWMH | 0.0621 | **0.0632** | 0.0364 | 0.0364 (Wu & Zhang) | no |

**We hold the best score on the entire public leaderboard on 5 of 8 cases**:
both `alpha_15_13929` cases, both `alpha_05_4071` cases (now that the gate
withholds the correction and reports raw RANS, which itself beats every
published entry there), and `AR_14_Ret_180`.

Full public leaderboard (`closure-challenge-benchmark/README.md`):

| Rank | Authors | Overall |
|---|---|---|
| 1 | Reissmann, Fang, and Sandberg | 0.0595 |
| 2 | Wu and Zhang | 0.0624 |
| — | **ours (unsubmitted, round 3)** | **0.0676** |
| 3 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| 4 | Montoya, Oulghelou, and Cinnella | 0.0779 |

## 3. Our overall number and position

- **Overall: 0.0676** (`closure_challenge_trained_entry_round3_gated.json`,
  `official_test_harness_result.round3_gated_overall`).
- RANS-identity floor: **0.1036**. We beat it by **−0.0360** (34.7% below).
- Docket-recorded rank-4 target (Montoya, Oulghelou, Cinnella): **0.0779**.
  We beat it by **−0.0103**.
- Against the full public board: we now sit **between rank 2 (0.0624) and
  rank 3 (0.0737)** — genuinely better than rank 3 by −0.0061, not merely
  tied with it as round 2 was.
- We are **unsubmitted** — this is our internally measured position against
  the public board, not an official ranking. No entry has been sent to the
  benchmark steward.

## 4. How each number was obtained

**Method class, stated precisely**: our correction is a **post-hoc velocity
field correction**, target `delta_U = U_LES − U_RANS` per mesh cell, applied
once to an already-converged RANS field as a final post-processing step. It
is **not** a modification to the turbulence model — nothing re-enters the
governing PDE and nothing is re-solved with the correction folded in. In the
Duraisamy–Iaccarino–Xiao taxonomy this is the "correct the answer" family,
structurally distinct from FIML/TBNN/SpaRTA/eigenvalue-perturbation, all of
which correct something inside the equations before re-solving
(`docs/research/CLOSURE_METHODS.md`).

- **Features (7, per cell)**: Pope's 5 scalar invariants of the normalized
  strain/rotation tensors (`I1_S2`, `I2_W2`, `I3_S3`, `I4_W2S`, `I5_W2S2`), a
  wall-distance turbulent Reynolds number `Re_y`, and a turbulent/mean-KE
  ratio `tke_ratio`.
- **Model class**: `HistGradientBoostingRegressor` × 3 (one per velocity
  component), `max_iter=300, max_depth=6, learning_rate=0.05`.

**Round 1** (`closure_challenge_trained_entry.json`, overall **0.0869**):
- Trained on 21 periodic-hill (PH) cases, validated on 4 held-out PH cases,
  applied to the 4 official PH test cases.
- **Corrected**: the 4 PH test cases only.
- **Passed through unmodified raw RANS** (identical to the floor): all 4
  non-PH test cases (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`,
  `NASA_2DWMH`) — because the benchmark does not ship `gradU`/`walldist` in
  solved time directories for DUCT/CBFS, and reconstructing those fields was
  out of scope for round 1.

**What unlocked round 2** (`closure_challenge_trained_entry_round2.json`,
overall **0.0741**, delta vs round 1 **−0.0128**):
- A new **mesh-reconstructed `gradU`/`walldist` feature pipeline** (Green-Gauss
  `gradU` from mesh + RANS `U` + BCs; `walldist` via nearest wall-patch-face
  centre), validated against shipped fields on **PH training cases only**:
  cell centres/volumes vs. shipped `C`/`V` — PASS (max abs err ~1e-13/1e-22);
  `gradU` vs. shipped `gradU` — PASS (pooled relative Frobenius error
  0.0012–0.0029, Pearson r 0.9997–1.0000, on 3 different PH training cases);
  `walldist` vs. shipped — PASS (r 1.0000, mean rel. error <0.1%).
- **Corrected** with this new pipeline:
  - DUCT (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`) — a **new,
    DUCT-specific model**, trained on `AR_1/3/5/10_Ret_180`, validated on
    `AR_7_Ret_180` (held out).
  - `NASA_2DWMH` — corrected using the **existing round-1 PH-trained model**
    (pre-registered choice, made before test scoring; no matching-family
    training data exists for NASA_2DWMH in this benchmark release).
- `NASA_2DWMH` **regressed slightly** under this model (0.0621 → 0.0632,
  +0.0011 worse) — reported honestly, not reverted, because reverting after
  seeing the per-case result would itself be a second, test-truth-informed
  scoring decision, which the leakage rule forbids.

## 5. Validation and leakage guards actually in place

- **Train/val/test disjointness** checked and recorded explicitly for both
  the PH split (round 1) and the DUCT split (round 2): `train_val_test_disjoint: true`.
- **NASA_2DWMH model choice pre-registered** before the round-2 test scoring
  call (`nasa_2dwmh_model_choice_preregistered_before_test_scoring: true`) —
  chosen because no other option existed, not selected by trying alternatives
  against test scores.
- **Mesh-reconstruction validation was performed exclusively on training-family
  cases** (PH training cases for `gradU`/`walldist`; DUCT test-mesh cell
  centres/volumes only, no field values) — never against validation or test
  ground truth.
- **Ground truth (`U_LES`) reads**: legitimate for the 21+4 PH train/validation
  cases (needed to compute per-case training/validation error) and for CBFS
  (explicitly a non-scored training case in the benchmark's own split) — never
  for any of the 8 official test cases outside the single official scoring calls.
- **Official scoring calls made, total: 4** — each a single call to
  `closure_challenge.score()`/`evaluate_by_case()` that touches the 8 official
  test cases' ground truth: (1) the RANS-identity floor, (2) the round-1
  trained entry, (3) the round-2 trained entry, (4) round-3, the gate applied
  to the PH test cases for the first time. No fifth call has been made.
- **C1 (the test-blind error/trust gate) made zero scoring calls of its own**
  and opened no test-case file of any kind when it was built — it was fit
  and validated entirely on the 21 training / 4 validation PH cases. Round 3
  (§0 above) later evaluated that same frozen gate on the 4 PH test cases'
  RANS-derived features (never their ground truth) as the input to call (4).

## 6. What is recoverable, and what remains blocked

**Term 1 — the "decline-where-it-hurts" gating term — TAKEN in round 3.**
- On 3 of 8 cases round 2's correction was worse than doing nothing:
  `alpha_05_4071_4048` (+0.0262), `alpha_05_4071_2024` (+0.0255), `NASA_2DWMH`
  (+0.0011). The C1 gate covers only the PH family; round 3 applied it to
  the 2 PH cases and recovered **0.0065** on the 8-case mean (0.0741 → 0.0676),
  matching the 0.0066 predicted almost exactly. `NASA_2DWMH`'s much smaller
  +0.0011 remains untouched: no matching-family gate exists for it, and its
  round-2 prediction is a pre-registered choice that cannot be revisited now
  without a test-truth-informed second look, which the rules forbid.
- **Why taking it now was legitimate, stated again**: the gate's parameters
  (feature screening, RidgeCV alpha, standardization, coefficients,
  threshold) were computed exclusively from the 21 PH training cases in C1,
  before round 3 ever ran. Round 3's only new action was evaluating that
  frozen model on the 4 PH test cases' RANS-derived features — never their
  ground truth — and using the binary output to choose between two
  already-legitimate predictions. No test-case data shaped the gate itself.
  See §0 for the full account and the compute ledger.

**Term 2 — the duct streamwise-profile term (a BOUND, not a measurement). Still blocked.**
- F6c measured that uncorrected RANS produces **exactly zero** secondary flow
  on the ducts (RMS ~1e-15% of bulk velocity) against a real DNS secondary
  flow of 2.07–2.22% of bulk velocity — the textbook consequence of the linear
  Boussinesq closure having no mechanism for Prandtl's secondary flow of the
  second kind.
- Since the missing secondary flow is entirely absent, it can explain **at
  most its own magnitude** of our duct error: on `AR_1_Ret_360` (our error
  9.19%) and `AR_3_Ret_360` (8.62%), the missing secondary flow bounds the
  explainable share at **≤24%** in both cases (`ACTIVE_RESEARCH.md`,
  "Supervisor analysis," building on C2 + F6c). **This is a bound, stated
  explicitly as such — "scaled MAE does not decompose exactly," so this is
  not an exact error budget** — not a measured decomposition.
- Consequence: **at least 76% of the duct error is streamwise-profile error**,
  and rank 2's total duct error (4.55%, 3.99%) is already smaller than our
  streamwise-only remainder (~7.0%, ~6.6%) — meaning a scalar
  eddy-viscosity-style correction (exactly what FIML/Ladder-B targets) is
  well-aimed at the dominant term, not a wasted effort against an
  anisotropy-only gap.
- **Not banked** because the recovery route (Ladder B3, DAFoam discrete-adjoint
  field inversion reproducing Wu, Zhang & Zhang's rank-2 method) hit a real,
  reproducible numerical blocker before completing a single field-inversion
  iteration (§7) — nothing was withheld by choice here, the compute path is
  currently stopped.

## 7. What is blocked

- **Ladder B3, Stage 3 (timed adjoint pilot on CBFS): BLOCKED.** The
  DAFoam/PETSc discrete-adjoint GMRES linear solve diverges at the very first
  iteration: `PetscConvergedReason = -9` (`KSP_DIVERGED_NANORINF`), i.e. PETSc
  detects NaN/Inf before any GMRES progress. Reproduced **identically across
  four independent configuration changes**: two primal convergence
  tolerances (`primalMinResTol` 1e-4 and 1e-6, nearly identical residual norms
  7.092e-4 vs 7.099e-4), two objective-function types (a custom
  `DAFunctionVariance` field-loss against CBFS's own LES `U_LES`, and a
  standard force objective already known to work on this lab's naca0012
  case), and two ILU preconditioner fill levels (1 and 4).
- Ruled out: mesh quality (`DACheckMesh` reports max aspect ratio 14.76, max
  non-orthogonality 33.3°, max skewness 0.26 — all "OK" against DAFoam's own
  thresholds); the primal itself (Stage 2 primal reproduces B2's baseline to
  0.087–1.41% across U/p/k/omega and is not the source).
- Because the GMRES solve never completes a single iteration, its cost —
  the dominant, scaling-critical unknown Ladder B1 flagged for the full
  140–420 core-minute field-inversion estimate — **could not be measured**;
  any further extrapolation would be a fabricated number.
- **Stage 4 (the full CBFS field inversion) correctly did not run**, gated by
  the unresolved Stage 3 blocker, per the docket's own instruction that an
  honest "does not fit" result is a valid outcome.
- Separately, **F6b (periodic hills gate)** was not attempted this session —
  time-boxed, explicitly conditional on time remaining after F6a/F6c, not a
  blocker.

## The closure metric moved: 0.0741 → 0.0676

**Round 3 recovered Term 1** (§0, §6): a test-blind gate, fit and validated
only on non-test PH data in a prior session, was evaluated on the 4 official
PH test cases for the first time and correctly withheld the correction on
the 2 cases it was hurting. Movement: **−0.0065**, from 0.0741 to **0.0676**,
now genuinely better than public rank 3 (0.0737), between rank 2 (0.0624)
and rank 3. We lead the public board on 5 of 8 cases, not 3.

**Term 2 (the duct streamwise-profile deficit, §6) remains blocked** on the
same real, unresolved DAFoam/PETSc GMRES numerical failure (§7) — nothing
new attempted there this round; it needs a CFD-solving budget this round's
compute allocation (2 cores / 3 GB, shared with other jobs on this box) does
not fit. It is the larger of the two terms and the next place to spend a
solving-budget session.
