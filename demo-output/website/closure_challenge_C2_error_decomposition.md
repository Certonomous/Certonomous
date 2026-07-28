# C2 — Closure challenge error decomposition: where the deficit actually lives

Evidence record for night-queue item C2. All figures computed from
`demo-output/website/closure_challenge_trained_entry_round2.json`, which records
the single official scoring call. **Sanity check passed first:** recomputing the
8-case means from the per-case values reproduces the published overall figures
exactly — floor **0.1036**, entry **0.0741**. The decomposition is therefore
trustworthy.

---

## The headline: on 3 of 8 cases our correction is worse than doing nothing

| case | RANS floor | our entry | delta | vs floor |
| --- | --- | --- | --- | --- |
| alpha_15_13929_4048 | 0.1320 | 0.0501 | −0.0819 | **−62.0%** |
| alpha_15_13929_2024 | 0.2049 | 0.1011 | −0.1038 | **−50.7%** |
| alpha_05_4071_4048 | 0.0461 | 0.0723 | +0.0262 | **+56.8% WORSE** |
| alpha_05_4071_2024 | 0.0719 | 0.0974 | +0.0255 | **+35.5% WORSE** |
| AR_1_Ret_360 | 0.1288 | 0.0919 | −0.0369 | −28.6% |
| AR_3_Ret_360 | 0.1243 | 0.0862 | −0.0381 | −30.7% |
| AR_14_Ret_180 | 0.0590 | 0.0303 | −0.0287 | −48.6% |
| NASA_2DWMH | 0.0621 | 0.0632 | +0.0011 | **+1.8% WORSE** |

The overall win is real and large, but it is **carried entirely by five cases**
while three are actively degraded. The NASA_2DWMH regression was already known
and reported. **The two `alpha_05` regressions are larger by an order of
magnitude and are the real story.**

## The recoverable term is 1.7x our entire margin

| Quantity | Value |
| --- | --- |
| Combined damage on the three degraded cases | 0.0528 summed = **0.0066** on the 8-case mean |
| Score if the correction were withheld wherever it hurts | **0.0675** (vs 0.0741 now) |
| Our current margin over the rank-4 target (0.0779) | +0.0038 |
| **Recoverable term as a multiple of that margin** | **1.7x** |

Of the 0.0528 total damage, `alpha_05_4071_4048` and `alpha_05_4071_2024`
account for **0.0517 — 98% of it**. NASA_2DWMH contributes 0.0011 and is
essentially noise by comparison.

**Effort should target the alpha_05 periodic-hill regime and nothing else.**
Chasing the NASA hump would recover at most 2% of the available term.

## The pattern — first framing, then the correction to it

**My first reading was that this is an alpha-regime failure**, since within the
periodic-hill family the split looked clean: `alpha_15` gave the model's best
performance anywhere (−62.0%, −50.7%) and `alpha_05` its worst (+56.8%, +35.5%).

**That framing is wrong, and I am replacing it.** Two facts kill it:

1. **The training split already contains alpha_05 cases** — five of them
   (`alpha_05_10071_3036`, `alpha_05_4071_3036`, `alpha_05_7071_2024`,
   `alpha_05_7071_3036`, `alpha_05_7071_4048`), plus two more held out in
   validation. The model was *not* extrapolating into an unseen regime. It saw
   alpha_05 data, trained on it (per-case train MAE 0.0589–0.0719, unremarkable),
   and still degrades alpha_05 at test.
2. **NASA_2DWMH is not a periodic hill at all**, yet it sits in the same
   degraded group. An alpha-regime story cannot explain it.

### The framing that does hold: the model hurts where RANS was already good

Ordering the five PH-model cases by how bad the uncorrected baseline was:

| floor (RANS error) | delta | outcome |
| --- | --- | --- |
| 0.0461 | +0.0262 | HURT |
| 0.0621 (NASA_2DWMH) | +0.0011 | HURT |
| 0.0719 | +0.0255 | HURT |
| 0.1320 | −0.0819 | helped |
| 0.2049 | −0.1038 | helped |

**Clean separation with no overlap.** The PH model hurts for every floor
≤ 0.0719 and helps for every floor ≥ 0.1320 — a gap of 0.0601 with nothing in
it. Pearson r between floor and delta is **−0.9418**.

**Caveat stated plainly: n = 5.** A correlation of −0.94 on five points is
suggestive, not established. It is offered as the better hypothesis, not as a
result. What earns it precedence over the alpha framing is not the r value but
that it explains **all three** regressions with one mechanism — including the
one the alpha story cannot touch.

The duct model does **not** follow this rule: it helps at floor 0.0590. That is
consistent with the mechanism rather than against it — the duct model is applied
in-family, where it has genuine competence, whereas the PH model is being asked
to correct flows whose baseline error is already near the model's own noise
floor. **When there is little to fix, a correction can only add error.**

## The fix must be test-blind — stating this explicitly because the obvious move is cheating

The 0.0675 figure above is a **diagnostic, not a plan.** Selecting per-case
whether to apply the correction *on the basis of test scores* would be
test-truth-informed model selection — precisely the leakage this entry has so
far avoided, and the same discipline that led to the NASA hump regression being
reported rather than quietly fixed after the single official scoring call.
Taking that 0.0066 by inspection would invalidate the entry.

**The legitimate version** is a trust/domain criterion built and validated on
**training and validation cases only**, which declines to apply the correction
where the input features fall outside the training distribution. Concretely:

1. Characterise the feature distribution (the five Pope invariants, plus
   separation extent) over the alpha_15 *training* cases.
2. Build an in-distribution test — a simple density or convex-hull/Mahalanobis
   criterion is likely enough given the clean regime split.
3. Validate it on held-out *training-family* cases: it must flag the alpha_05
   regime as out-of-distribution **without ever consulting a test score**.
4. Only then apply it to the test set, in a single scoring call as before.

If step 3 fails — if no test-blind criterion separates the regimes — then the
honest outcome is that this correction's domain cannot be identified a priori,
and that is itself a publishable finding about the model class (Ladder B4).

## Recommended next action

Train a second, alpha_05-regime model on the alpha_05 *training* cases if such
cases exist in the training split. This is strictly better than gating, because
it recovers the term instead of merely declining to lose it — and it is
test-blind by construction. **Check first whether the training split actually
contains alpha_05-family cases;** if it does not, gating is the only honest
route and the recoverable term drops to "avoid the loss" rather than "win the
case".

## Evidence record

| Field | Value |
| --- | --- |
| Source | `closure_challenge_trained_entry_round2.json`, single official scoring call |
| Harness provenance | benchmark repo `deb91557...`, eval package `1c4e22c8...`, version 0.2.1, matches round 1 |
| Verification | 8-case means recomputed from per-case values; reproduce 0.1036 and 0.0741 exactly |
| Compute cost | none — arithmetic on an existing scored artifact, 0 core-min |
| Leakage status | **No new scoring call made.** This document reads an already-published result and does not touch ground truth. |
