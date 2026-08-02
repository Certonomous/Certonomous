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
the clone's own `extract_test_data.py` (`closure-challenge-benchmark/scripts/`)
at lines 65 to 67 reads exactly that file, subsamples
it to 1,000 points, and writes it into `ground_truth_test.npz`, which is what
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

> **MEASURED 2026-08-02, and this section argued from the wrong quantity.**
> Record: `closure_challenge_cbfs_donor_coverage.json`, produced by
> `sdk/scripts/closure_cbfs_donor_coverage.py`. Zero scoring calls, no model
> fitted, and **no ground-truth file of the hump opened** — `0/U_LES`,
> `0/k_LES` and `0/tauij_LES` are named in the script so a reader can grep for
> them and confirm. 51,626 hump cells from the RANS field and mesh alone.
>
> **The argument above is entirely about flow topology.** Both flows are
> two-dimensional, smooth-walled, separating and reattaching, so CBFS is
> "physically the closest flow in the benchmark to the hump". That is true and
> it is not the quantity that decides anything. **The mechanism this lab has
> actually proven binds its models is feature extrapolation** — round 4
> established that `Re_y` reaches 1.85× and 2.07× its trained maximum on the
> two ducts the entry trails and 0.90× on the one it leads, and a
> gradient-boosted tree cannot extrapolate. Topological similarity was never
> checked against that, and this section should have checked it.
>
> **What the measurement says. Both donors extrapolate on the hump, on all
> seven features.** Not five, not most: 7 of 7 for the periodic hills and 7 of
> 7 for CBFS. That independently reproduces the "outside the training range on
> all 15 features simultaneously" finding of section 5 through a different
> aggregation, and it means Route B does not escape the problem, it only
> changes which corner of it the model sits in.
>
> | feature | share of hump cells outside PH range | outside CBFS range | better donor |
> | --- | --- | --- | --- |
> | `I1_S2` | 0.2075 | 0.2058 | CBFS |
> | `I2_W2` | 0.0912 | 0.1124 | PH |
> | `I3_S3` | 0.1994 | 0.1882 | CBFS |
> | `I4_W2S` | 0.1568 | 0.1399 | CBFS |
> | `I5_W2S2` | 0.1815 | 0.1803 | CBFS |
> | **`Re_y`** | **0.1823** | **0.2615** | **PH** |
> | `tke_ratio` | 0.2697 | 0.0004 | CBFS |
>
> **CBFS covers the hump better on 5 of 7 features, and worse on the one that
> has already cost this lab score.** It is dramatically better on `tke_ratio`
> — 0.04% of hump cells outside its range against 27% outside the periodic
> hills' — which is a real point in its favour and is what the topological
> argument was groping toward. But on `Re_y` it is the worse donor by every
> measure taken: 26.2% of hump cells outside its range against 18.2%, a ceiling
> of 30.25 against 38.08, and a p99 reaching 7.24 donor half-ranges past its
> edge against 5.55. **The one dimension on which round 4 demonstrated, with
> scores, that extrapolation costs this entry points is the dimension on which
> the proposed better donor is worse.**
>
> **The comparison is biased toward the periodic hills and CBFS still wins most
> of it, which makes the `Re_y` result harder rather than easier to dismiss.**
> A donor's hard [min, max] hull can only widen with more data, and the
> periodic-hill donor is **327,600 cells across 21 cases against CBFS's 21,000
> across one — 15.6 times larger.** CBFS beating it on five features from a
> fifteenth of the data is a genuine signal about flow similarity. Losing on
> `Re_y` anyway is a genuine signal about Reynolds number.
>
> **And the Reynolds numbers are not close, on either side.** The benchmark
> states CBFS's as `Re_H=13700` in its own `transportProperties`; it states
> none for the hump, which is recorded as absent rather than filled in. The
> nearest read source that gives one is Buchanan, Lăcătuş, West & Dwight 2025
> (arXiv 2504.06758, §2.4 and Table 2, read 2026-08-02), which trains on this
> same hump and puts it at **Re_h = 9.3×10⁵**, describing what distinguishes it
> as *"high Reynolds number effects such as thin turbulent boundary layers and
> smooth-surface separation under adverse pressure gradients"*, against its
> periodic hill at 1.0×10⁴ and its CBFS at 1.3×10⁴. **CBFS and the periodic
> hills sit within a factor of about 1.4 of each other and roughly seventy
> times below the hump.** Swapping one for the other does not move the entry
> toward the hump's regime; it moves sideways.
>
> **Revised verdict on Route B, and it is neither the yes this section implied
> nor a no.** The route is legal, the withdrawal in section 7 stands, and CBFS
> genuinely is the closer flow. But **it cannot be shown to beat 0.0621 on
> validation evidence alone, because no legal held-out flow in this benchmark
> is at the hump's Reynolds number** — every non-test separating flow it ships
> is within a factor of about two of 10⁴. Route B would be a fit on 21,000
> cells, trading better invariant coverage for worse coverage on the known
> failure axis, evaluated on nothing that resembles the target regime, and then
> scored once against a case whose result we already know. **That is not a
> pre-registration that could be honoured; it is a coin flip with a paper
> trail.** It is not taken, and the reason has changed from "it costs compute"
> to "the evidence that would justify it does not exist inside this benchmark."

## 6. A citation in the entry that nobody on this box could check — now checked

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

> **RESOLVED 2026-08-02. The quotation is verified verbatim and it stands.**
> The preprint was retrieved from `https://arxiv.org/html/2603.28884v1` (HTTP
> 200, 05:14 UTC) — an arXiv identifier needing no library, which is why this
> was the item on the reading list to do first. The sentence is in **Section
> 2.1, *Test cases***, immediately after *"The test cases cannot be used in any
> way at training time."* Both sentences match the draft character for
> character.
>
> **This section's own diagnosis was right and its inference was wrong.** The
> sentence genuinely is nowhere on this machine, and that was correctly
> reported; what did not follow, and was never asserted here, is that it does
> not exist. The permission the compliance argument leans on was granted in the
> exact words attributed to it.
>
> **Route B is therefore permitted by the preprint as well as by the README.**
> Section 5's Route B — train on `CBFS13700`, a training-side flow, and predict
> the hump — is now backed by the challenge authors' own explicit statement that
> training on flows similar to the test cases is allowed, and not only by the
> README's more general "you are free to use your own training/validation data".
> Nothing about the cost or the pre-registration requirement in Route B changes.
>
> Full audit of every other quotation in the draft:
> `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §9.

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
   **Updated 2026-08-02, after measuring rather than arguing:** Route B is
   worse than unproven, it is unprovable from inside this benchmark. Both
   donors extrapolate on the hump on 7 of 7 features; CBFS covers better on 5
   of them and **worse on `Re_y`, the one axis whose extrapolation has already
   cost this entry score**; and no legal held-out flow here sits anywhere near
   the hump's Reynolds number, which the nearest read source puts about seventy
   times above both candidate donors. **The premise "CBFS is the better donor"
   is not refuted, but it is not what the numbers say either, and the section
   that argued it argued from topology instead of from the mechanism this lab
   had already proven.** Section 5, Route B.
4. ~~**The unverified quotation in the submission draft is the one item on this
   page that should not wait.**~~ **CLOSED 2026-08-02: verified verbatim, in
   Section 2.1 of the preprint.** It did not wait, and it came back upheld. See
   section 6.

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
| ~~Unverified~~ **verified** preprint quotation, §2.1 *Test cases* | `arxiv.org/html/2603.28884v1`, retrieved 2026-08-02; audit at `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §9 |
| Preprint misstates α on two of the four PH test cases (says 1.5, benchmark names say 0.5) | same, §2.1, against `closure-challenge-benchmark/README.md` test column |
| Submission route is email, confirmed by a second independent source | `arxiv.org/html/2603.28884v1` §2.2: *"As of March 2026, submissions are via email."* |
