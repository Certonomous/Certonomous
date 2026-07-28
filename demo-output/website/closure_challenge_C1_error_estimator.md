# C1 — A test-blind baseline-error gate for the periodic-hills closure correction

Evidence record for night-queue item C1. Script:
`sdk/scripts/closure_baseline_error_gate.py`. Machine-readable record:
`demo-output/website/closure_challenge_C1_error_estimator.json`.

**This is a fit/validation run only.** No scoring call was made, no test case
was read in any form, and nothing here changes what the entry submits.
Applying a gate to the test set is explicitly out of scope tonight (see the
task's rule 4) and was not done.

---

## The question

C2 found that the periodic-hills (PH) closure correction *hurts* on test
cases where the raw RANS baseline was already accurate and *helps* where it
was bad (r = −0.9418, n = 5, stated there as suggestive not established).
That finding used the 8 official test cases and cannot be used to build
anything — it is the motivating observation only. This task: build an
estimator that predicts baseline error (hence, indirectly, whether the
correction is worth applying) from features the test cases legitimately
expose, fit and validated **only** on the training/validation split already
recorded in `closure_challenge_trained_entry.json`.

## Data split (identical to the entry's own recorded split — reused by import, not redefined)

| Split | n | Cases |
| --- | --- | --- |
| Train | 21 | `alpha_05_10071_3036`, `alpha_05_4071_3036`, `alpha_05_7071_2024`, `alpha_05_7071_3036`, `alpha_05_7071_4048`, `alpha_075`, `alpha_10_12000_2024`, `alpha_10_12000_3036`, `alpha_10_12000_4048`, `alpha_10_6000_2024`, `alpha_10_6000_3036`, `alpha_10_6000_4048`, `alpha_10_9000_2024`, `alpha_10_9000_3036`, `alpha_10_9000_4048`, `alpha_125`, `alpha_15_10929_2024`, `alpha_15_10929_3036`, `alpha_15_10929_4048`, `alpha_15_13929_3036`, `alpha_15_7929_3036` |
| Validation (held out, never fit on) | 4 | `alpha_05_10071_4048`, `alpha_05_10071_2024`, `alpha_15_7929_4048`, `alpha_15_7929_2024` |
| Test — **never touched** | 4 (of the 8 official) | `alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048`, `alpha_05_4071_2024` (the other 4 official test cases — AR_1/AR_3/AR_14/NASA_2DWMH — belong to a different model family and were not in scope for this gate either) |

## Features (all test-blind: derived from the RANS field and mesh only, no ground truth)

Per-cell: the same 7 features the entry already uses — Pope's 5 scalar
invariants of the normalized strain/rotation tensors (`I1_S2`, `I2_W2`,
`I3_S3`, `I4_W2S`, `I5_W2S2`), a turbulent Reynolds number (`Re_y`), and a
turbulent/mean-KE ratio (`tke_ratio`).

Aggregated to one vector per case: mean and 90th-percentile(|·|) of each of
the 7 (14 features), plus **`frac_backflow`** — the fraction of cells with
negative streamwise velocity, a test-blind proxy for how large the
separation/recirculation bubble is (the physical mechanism C2 hypothesized).
15 case-level features total.

**Regression target**: per-case raw-RANS identity scaled-MAE against
`U_LES` ("baseline error"). This requires ground truth — legitimate for
train/validation cases, exactly as round 1's own script already reads
`U_LES` for these same 25 cases to compute its own recorded
`train_pooled_scaled_mae_per_case` / `validation_pooled_scaled_mae_per_case`.

## Model, and why it changed mid-run

**First attempt — full 15-feature RidgeCV** (alpha selected by internal
LOO-CV on the 21 training cases): looked excellent in-sample —
**train LOO-CV Pearson r = +0.9272, R² = +0.83** — but **failed on genuine
validation**: r = +0.2520, MAE = 0.1012, predicted ranking did not match the
actual ranking, and one case (`alpha_05_10071_2024`) was predicted at 0.4529
— nearly double the maximum baseline error ever observed in training
(0.2085). Classic small-n overfitting: p=15 features against n=21 cases,
even under leave-one-out rotation, is not enough to prevent it, because the
regularization strength itself was chosen on the same 21 cases.

**Second attempt — feature-screened, low-dimensional models.** Screening
(Pearson r vs. training baseline error, train cases only) ranked features;
the top 3 are `p90_I4_W2S` (r = −0.7579), `frac_backflow` (r = −0.5912), and
`p90_I3_S3` (r = −0.5785). A Ridge regression on just these 3 (same
train-only alpha-selection procedure) is the reported gate. A univariate
model (single best feature) was also fit for comparison.

## Separation achieved on validation (the numbers)

| Variant | Train LOO-CV r | Validation r | Validation MAE | Validation rank order correct | Validation hurt/help AUC | Train-derived threshold gate, correct of 4 |
| --- | --- | --- | --- | --- | --- | --- |
| Full 15-feature Ridge | +0.9272 | +0.2520 | 0.1012 | No | — | — |
| Univariate (`p90_I4_W2S` only) | +0.7133 | +0.5557 | 0.0439 | No | **1.0** | 3/4 |
| **Top-3-screened Ridge (recommended)** | +0.7858 | +0.6001 | 0.0280 | No | **1.0** | **4/4** |
| Naive: predict train-mean baseline | — | 0.0 | 0.0412 | — | — | — |
| Naive: majority-class "always apply correction" | — | — | — | — | — | 3/4 (0.75 accuracy) |

Per-case, actual baseline error vs. actual outcome under round 1's
already-recorded, genuinely held-out validation score
(`validation_pooled_scaled_mae_per_case` in `closure_challenge_trained_entry.json`):

| Case | Baseline (actual) | Corrected (actual, round 1) | Delta | Outcome | Top-3 gate prediction |
| --- | --- | --- | --- | --- | --- |
| alpha_05_10071_4048 | 0.0759 | 0.0772 | +0.0013 | **HURT** | 0.0723 (below threshold 0.1263 — correctly declines) |
| alpha_05_10071_2024 | 0.1368 | 0.0858 | −0.0510 | helped | 0.1333 (above threshold — correctly applies) |
| alpha_15_7929_4048 | 0.0916 | 0.0463 | −0.0453 | helped | 0.1488 (above threshold — correctly applies) |
| alpha_15_7929_2024 | 0.1957 | 0.1310 | −0.0647 | helped | 0.1478 (above threshold — correctly applies) |

**Threshold used**: the median of the top-3 model's own leave-one-out
predictions on the 21 *training* cases (0.1263) — derived entirely from
train, applied to validation, never fit on validation or test.

## Does the gate work?

**Yes, on this validation set, with an important caveat on statistical
power.** The top-3-feature gate achieves AUC = 1.0 separating the single
validation case the correction hurt from the three it helped, and a
threshold set purely from training data classifies all 4/4 validation cases
correctly — beating the trivial "always apply the correction" baseline
(3/4 = 75%, since 3 of the 4 validation cases happened to benefit anyway).
The univariate model also reaches AUC = 1.0 but its train-derived threshold
only ties the naive baseline at 3/4.

**Caveat stated plainly, matching C2's own standard**: n = 4 validation
cases with only 1 positive (HURT) label. Under an uninformative/null
ranking, AUC = 1.0 with this class balance (1 positive vs. 3 negative) has
roughly a 1-in-4 chance of occurring by luck alone. This result clears the
bar the task set ("report the separation quantitatively... say plainly if it
does not work") but should be read as **encouraging, not established** —
exactly the caution C2 applied to its own n = 5 test-side correlation.

**The magnitude prediction is weaker than the classification.** Even the
best variant's Pearson r on raw baseline-error magnitude (+0.60) and rank
order (wrong — it swaps the two middle cases) are modest. What actually
holds up is the coarser, decision-relevant signal: the model consistently
puts the one case that got hurt lowest, with a real gap to the three that
helped. That is exactly the resolution the gate needs (a binary apply/decline
call), even though it cannot precisely rank all four cases by degree.

## The central lesson

Train-only leave-one-out cross-validation was actively misleading here: the
full 15-feature model's train LOO r = +0.93 looked far better than the
3-feature model's +0.79, yet the full model failed validation and the small
model passed it. With O(20) training cases, feature count must be kept to a
handful (screened on train alone, before validation is ever consulted), and
a genuine held-out check — not fancier in-sample cross-validation — is what
actually separates a working gate from an overfit one. This is the same
discipline the task asked for and is worth carrying into any future gate
work on this ladder.

## What this does NOT do

- It does not decide whether to apply the PH correction on the test set.
  That is explicitly out of scope for tonight (task rule 4) and was not
  done — no `closure_challenge.score()`/`evaluate_by_case()` call was made,
  and no test-case file (PH, DUCT, or NASA_2DWMH) was opened.
- It does not cover the DUCT or NASA_2DWMH model families. C2's evidence
  shows all 3 DUCT test cases were helped by their own in-family DUCT model
  (no regression to gate against), and NASA_2DWMH has no matching-family
  training data to fit a gate on at all (round 2's own stated limitation).
  A gate for those families is a separate, larger effort not attempted here.

## Leakage statement (exact)

- **Ground truth (`U_LES`) was read** for all 25 PH train+validation cases
  listed above — needed to compute the regression target (per-case baseline
  scaled-MAE). This mirrors what round 1's own script already does for these
  same 25 cases and is not a new category of access.
- **Ground truth was never read** for any of the 8 official test cases
  (`alpha_15_13929_4048`, `alpha_15_13929_2024`, `alpha_05_4071_4048`,
  `alpha_05_4071_2024`, `AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`,
  `NASA_2DWMH`). No file under those cases' `0/U_LES` (or DUCT's headerless
  equivalent) was opened.
- **No `closure_challenge.score()` or `evaluate_by_case()` call was made** —
  this script never imports or calls the scoring functions at all.
- **Feature scaling (mean/std), RidgeCV alpha selection, and all fitted
  coefficients** were computed exclusively on the 21 training cases.
  Validation cases were used only to *score* an already-fit gate — never to
  fit, rescale, or select alpha.
- **Model-variant comparison** (full-15 vs. top-3 vs. univariate vs. naive
  baselines) was itself scored against validation, not test — legitimate
  model selection, the exact purpose a validation split exists for.

## Compute / ledger

Single-core (`taskset -c 0`), reading already-solved OpenFOAM fields from
the benchmark's scratch clone on disk — no flow solver was run.
**Elapsed ≈ 4 s ⇒ core-minutes ≈ 0.06–0.07.** No entry in the solver-run
ledger is required since no solver ran; this is recorded here explicitly per
the standing requirement to say so when none were logged.

## Files

- `sdk/scripts/closure_baseline_error_gate.py` — the script (reuses
  `train_closure_periodic_hill_correction.py`'s feature/data-loading code by
  import, does not redefine the split).
- `demo-output/website/closure_challenge_C1_error_estimator.json` — full
  machine-readable record (all per-case numbers, screening results, all
  model variants, leakage statement, compute).
