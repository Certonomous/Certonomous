# C6. Can the NASA hump be improved at all?

`c6-nasa-hump-the-only-last-place`. Decided 2026-08-01 on evidence already on
this box. **No solver was run, no model was trained, and no scoring call was
made.** This document answers the decision half of the proposal and stops
there, because every yes it reaches spends compute.

**The short answer: the hump is improvable, the standing record says it is
not, and the standing record is wrong.**

---

## 1. What was believed

`CLOSURE_CHALLENGE_STATUS.md` lines 283 to 288 carry the lab's position:

> No action is available for `NASA_2DWMH` regardless of this flag: no
> alternative training-family model exists for it, its correction choice was
> pre-registered before its test score was ever seen (round 2), and revisiting
> that choice now, having already seen the outcome, would itself be exactly the
> test-truth-informed model selection the leakage rule forbids.

The same sentence appears in `sdk/scripts/closure_criterion_on_test_features.py`
line 224 and, in shorter form, in `closure_challenge_trained_entry_round2.json`
line 102.

Two claims are welded together there. The first is false. The second is sound
and is the only thing keeping the case shut.

## 2. The false claim: "no alternative training-family model exists"

The benchmark's own split table, `closure-challenge-benchmark/README.md`
lines 71 to 77, has **three** flows with a single parametric variation, and it
did not put them on the same side:

| Flow | Training | Validation | Test |
| --- | --- | --- | --- |
| CBFS13700 | yes | | |
| PHLL10595 | yes | | |
| NASAHUMP | | | yes |

`CBFS13700` is the curved backward-facing step: a two-dimensional, smooth-wall
flow that separates and reattaches, and the benchmark ships it as **training**
data with its `0/U_LES`, `0/k_LES`, `0/p_LES` and `0/tauij_LES` fields.

The hump is a two-dimensional, smooth-wall separation bubble. CBFS is the
nearest flow to it anywhere in this benchmark, and it is legal to fit on.

**The pre-registered argument never considered it.** The argument is written out
in `sdk/scripts/train_closure_extended_correction.py` lines 27 to 40, and it is
a two-way comparison:

> periodic-hills (separated/reattaching shear layer over curved geometry) is
> physically closer to a wall-mounted-hump separation bubble than the DUCT
> family (attached secondary-flow-dominated, non-separating) is

Periodic hills against ducts. CBFS is not named, not rejected, not mentioned.
The choice was defended against the worse of two candidates while the better
third sat in the training set unused.

Nor do the rules require a matching family. `README.md` line 65: **"you are
free to use your own training/validation data"**, and line 67 calls the split
**"suggested"**. The one strict rule, line 63, is scoped to the test cases:
training or validating on any of them withdraws the submission.

So "no alternative training-family model exists" is not a fact about the
benchmark. It is a fact about which two candidates somebody compared.

## 3. What is genuinely off limits

The hump's high-fidelity fields **are** in the clone, at
`closure-challenge-benchmark/data/NASA_2DWMH/0/{U_LES,k_LES,tauij_LES}`, 51,626
cells each. `0/U_LES` is not merely test data, it is the answer key:
`scripts/extract_test_data.py` lines 65 to 67 read exactly that file, subsample
it to 1,000 points, and write it into `ground_truth_test.npz`, which is what
`score()` grades against. Fitting, feature selection, gate calibration or a
hyperparameter choice touching it is fitting on the key.

The eval package states the bound in its strictest form
(`closure-challenge-pkg/README.md` line 113): **"you cannot use them during
training in any way."**

## 4. The claim that does hold, and what it costs

The second half of the standing position stands: the hump's per-case score is
already known. Round 2 spent one legitimate call and it came back 0.0632
against an uncorrected floor of 0.0621. Anyone choosing a model for the hump
today has seen that number. Selection after the fact is the same shape as the
shortcut this lab refused twice, and the benchmark's sanction for the harder
version of it is automatic withdrawal.

That constrains **how** either route may be taken. It does not make the case
unimprovable, and the record should not say that it does.

## 5. Two legal routes, priced but not taken

### Route A. Decline to correct the hump. No training, no new model.

The lab already owns a decline criterion that reads only the cheap solve, and
it already flags this case from RANS-derived features with no ground truth read
(`sdk/scripts/closure_criterion_on_test_features.py`): **NASA_2DWMH is outside
the periodic-hill model's training range on all 15 features simultaneously.**

`closure_challenge_tau_normalization_audit.json`, measured 2026-07-29, says why
and says it is algebraic rather than a property of this mesh:

* every Pope invariant scales as a power of `tau = 1/(Cmu*omega)`, verified to
  5.8e-16 relative error over an eight-decade omega sweep, with a fitted
  log-log slope of -2.0000 against a predicted -2.0000 for I1;
* **20.0 percent** of the hump's cells are affected. `I1` reaches 4.26e8, with
  a p90 of 23,298.9;
* **0 of 32** non-test cases the lab holds have a single affected cell, against
  **1 of 8** test cases. Ducts and hills are enclosed flows with no freestream
  for `k` to collapse in while `omega` does not.

Under a floored timescale, itself mirroring the strain-rate limiter already
inside SST's own eddy viscosity, the hump's `I1` p90 falls to 0.5 and the
affected fraction to zero, and that alternative was checked on training data
alone.

**Effect if declined:** the hump ships its floor, 0.0632 becomes 0.0621. The
overall is a mean over the eight scored cases, so that is 0.0011 divided by
eight, and the entry goes from its harness-reported 0.0654314 to 0.0652939.
**0.00014 on the entry, and it does not move the rank:** Wu sits at 0.0624 and
Reissmann at 0.0595.

**Cost: zero compute.** It is a re-emission of the entry with one case
uncorrected.

**The honest objection, stated rather than argued away.** The criterion fires
on a *global covariate shift*, which is not the mechanism the decline gate was
proven on. The proven mechanism is the ducts' algebraically forced zero in
`I3_S3` and `I4_W2S`, and the same script says so at line 220: the hump's
outcome, +0.0011, is mild, and the proven mechanism would have predicted worse.
Declining on a criterion that fires for a different reason than the one it was
validated for is a weaker act than it looks.

### Route B. Train on CBFS13700 and pre-register the whole thing first.

Legal under README lines 63 to 67. Physically the closest flow in the benchmark
to the hump. Never evaluated.

**Cost: compute, and it is not priced here.** A fit plus a scoring call, and
this document does not launch either. It also needs the thing route A does not:
a pre-registration written and frozen before anything is scored, stating the
model, the features, the selection rule and the commitment to ship whatever
comes out. Without that, it is selection by somebody who has seen the score.

## 6. A citation in the entry that nobody on this box can check

While settling the above, one sentence in the lab's own draft failed to
resolve. `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` lines 69 to 73 attribute a
permission to the preprint:

> "You can train on similar flows to the test cases (for example, different
> parametric variations of the periodic hills case)."

**That sentence does not appear in the benchmark clone, in the eval package, or
anywhere under this repository, and no copy of the preprint is on this
machine.** The README's own wording carries the same permission by a different
route, so the argument does not fall over; but the quotation is unverified
where it stands, and the whole physical argument for borrowing the periodic
hills model leans on it. It should be checked against the preprint or replaced
with the README lines quoted in section 2, which are on disk and can be read.

## 7. The decision

1. **The hump is not unimprovable, and it is not unimprovable "without outside
   data" either.** The better candidate is inside the benchmark, on the
   training side, and was never compared against.
2. **The standing sentence "no action is available for `NASA_2DWMH`
   regardless" is withdrawn.** Two actions are available. What is genuinely
   constrained is who may choose between them, and when.
3. **Neither is taken here.** Route A costs nothing and rests on a criterion
   firing for a mechanism it was not proven on. Route B costs compute and is
   worthless without a pre-registration written before it runs.
4. **The unverified quotation in the submission draft is the one item on this
   page that should not wait.** A novelty claim resting on an unread source is
   the defect this lab already has a proposal open about.

## 8. Evidence

| Claim | Where |
| --- | --- |
| Hump is test-only; CBFS and PHLL10595 are training | `closure-challenge-benchmark/README.md` lines 71 to 77 |
| Only strict rule, and the freedom to bring your own training data | same, lines 63 to 67 |
| "cannot use them during training in any way" | `closure-challenge-pkg/README.md` line 113 |
| `0/U_LES` is the scoring key | `closure-challenge-benchmark/scripts/extract_test_data.py` lines 65 to 67 |
| Pre-registered argument compares PH against DUCT only | `sdk/scripts/train_closure_extended_correction.py` lines 27 to 40 |
| Hump outside PH training range on all 15 features | `sdk/scripts/closure_criterion_on_test_features.py` |
| tau degeneracy algebraic; 20.0 percent of hump cells; 0 of 32 non-test cases | `demo-output/website/closure_challenge_tau_normalization_audit.json` |
| Round 4 per-case scores and the floor | `demo-output/website/closure_challenge_trained_entry_round4_duct.json` |
| Standing "no action available" position | `demo-output/website/CLOSURE_CHALLENGE_STATUS.md` lines 283 to 288 |
| Unverified preprint quotation | `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` lines 69 to 73 |
