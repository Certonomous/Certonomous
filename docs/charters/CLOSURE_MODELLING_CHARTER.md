# Certonomous Closure Modelling Charter

Version 1.0, dated 2026-08-20. Governs every data-driven turbulence closure this lab
trains, scores, reproduces or reports: RANS anisotropy models, field inversion, LES
subgrid-scale models, wall models, differentiable and solver-in-the-loop training, and the
uncertainty and aggregation methods filed beside them. It binds the four case directories
under `cases/RANS_LES_closure_models/`, the corpus under `docs/papers/closure/`, and any
closure claim that reaches a record, a certificate or a camera surface.

It is the **eleventh** charter — the tenth was `FILING_CHARTER.md`, whose adoption on
2026-08-18 was never reflected in `README.md` §1 (see §21.2). It exists because the first phase of closure work produced, in one
week, a model that could have scored **PASS** while being unphysical on an eighth of the
domain; a preregistration corrected by inventing a falsifier after the fact; a task budgeted
at 20 core-hours that the lab had already completed nineteen days earlier; and a source file
destroyed by a second agent writing to a path a first agent already owned. Every clause
below names the thing that earned it.

## 1. The line

> **A closure is not a result until it has been re-solved, and a score against a baseline a
> constant can beat is not an evaluation.**

Two clauses because this charter guards two different failures, and the lab has now
committed both. The first is the a-priori score reported as if it settled something: the map
from Reynolds-stress anisotropy to velocity runs through the momentum balance, is not
monotone, and has been measured to amplify a **0.31%** stress error into a **35.1%** velocity
error. The second is the baseline that cannot lose: the mean training anisotropy tensor,
fitted to nothing, **beats k-omega SST on 8 of 8 held-out cases**, so "we beat the RANS
baseline on `b`" is a sentence with no content.

---

# PART I — WHAT MAKES A CLOSURE RESULT

## 2. A-posteriori validation is mandatory; an a-priori score is labelled, and alone it is NOT A RESULT

> **No claim that a closure improves a flow may be made from an a-priori score. An a-priori
> score is reported with the words "a-priori" attached, and a directory that stops there
> states that stopping as a scope decision with the reason, never as a property of the
> method.**

**Why this is a bright line and not a preference.** `Wu2018_rans_explicit_closure_ill_conditioned.pdf`
(arXiv:1803.05581v3, Table 1, arXiv preprint p. 4) substitutes **exact DNS Reynolds stresses**
into the RANS momentum equations and propagates them. At `Re_tau = 5200` a stress field with
**0.31%** volume-averaged error yields a velocity field with **21.6%** volume-averaged and
**35.1%** maximum error. The stress errors do not grow with Reynolds number; the velocity
errors do, monotonically. **A perfect closure, coupled explicitly, produces a wrong flow.**

Two more, from the corpus:

- Duraisamy 2021 (arXiv preprint p. 10): "**successful a priori evaluation is neither a
  necessary nor a sufficient condition for successful predictive models.**"
- Beck & Kurz 2021 (arXiv preprint p. 26): a GRU closure reaching "**99.9% cross correlation
  in a priori tests**" whose "**LES solution diverges strongly soon after**".

**OpenFOAM v2606 is installed and `simpleFoam` runs on this machine.** A-posteriori
propagation is therefore available for every RANS case in the benchmark. **A-priori-only is a
scope choice, and it is written down as one.** `Wu2018_PIML_RF/RESULTS.md` does this correctly
and is the worked example:

> "**This is an a-priori result.** No velocity field was produced and nothing was re-solved.
> … so this is a scope decision, not a capability limit."

and, in its own "what it cannot see":

> "**It cannot see whether any of this survives being re-solved.** The map from `b` to `U`
> runs through the momentum balance and is not monotone; a model that cuts the anisotropy
> error by 2-5x can still produce a worse velocity field or fail to converge."

**What is forbidden.** Reporting an a-priori `b_rms` improvement as an improvement in
prediction. Comparing an a-priori number in this lab against a published a-posteriori number.
Describing a-priori-only work with any verdict word from section 12 other than the ones
qualified by "a-priori".

**Cross-reference, not duplication.** `VERIFICATION_CHARTER.md` §1 already says a result
without a retained evidence record is not a result. This clause adds what "done" means for a
closure specifically.

## 3. The baseline is the train-mean tensor, and it is named in the preregistration

> **Every model that predicts `b_ij` is scored against the TRAIN-MEAN constant tensor, not
> against k-omega SST. Both columns are quoted, per case, on the same cell mask. For a
> velocity claim the baseline is uncorrected RANS. The preregistration names the baseline
> before the run.**

**The measurement that earned it.** `_common/BASELINES.md` §6.4 computes the mean `b_LES` over
the 23 Phase-3 training cases and uses it as a **constant prediction everywhere, with no
inputs and nothing fitted beyond an arithmetic mean**:

```
b_mean =  [  0.1756  -0.0382   0.0018 ]
          [ -0.0382  -0.1479  -0.0006 ]
          [  0.0018  -0.0006  -0.0276 ]
```

Pooled over all 8 strict TEST cases (152,520 cells): **train-mean 0.3183, k-omega SST 0.4138,
`b = 0` 0.4234.** **The constant beats SST on 8 of 8.** On the ducts the margin is large
(0.4036 against 0.5799 on `AR_14_Ret_180`) because SST's `b` there is not merely inaccurate
but structurally wrong.

`Ling2016_TBNN/RESULTS.md` §5 states the consequence in the form this charter adopts:

> "**"Beats SST on `b_rms`" is a very low bar**, and any data-driven closure paper reporting
> only that comparison has not shown much. … the supervisor should treat a method that beats
> B1 but not B3 as having produced nothing."

**This is `VERIFICATION_CHARTER.md` §2c instantiated for closure.** §2c already requires that
a GRADE row separate the hypothesis from "a registered trivial baseline of that hypothesis".
**The train-mean tensor is that registered trivial baseline for anisotropy**, and this clause
fixes it by name so no future preregistration has to re-derive which baseline is trivial.

**Known defect in the provenance, recorded rather than papered over.** `BASELINES.md` §6.4 says
the mean is over **341,717** cells; both `RESULTS.md` files say **342,014** training cells,
same 23 cases. **The 297-cell discrepancy is unreconciled.** It does not move the pooled
figures at four decimals, and it is flagged here so the next person does not discover it as a
surprise.

## 4. Realisability is a GATE, and the preregistration states the fraction at which it fails

> **Any preregistration for a model predicting `b_ij` carries a realisability clause in its
> verdict ladder, with a numeric violating-fraction threshold and a norm threshold, frozen
> before the run. Reporting realisability without gating on it is forbidden.**

**The incident, 2026-08-20.** `Ling2016_TBNN/PREREGISTRATION.md` carried four baselines, three
acceptance criteria, an explicit falsifier and a departures section. It required realisability
to be **reported**. It never **gated** on it. The trained TBNN put

| seed | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| test cells outside the barycentric triangle | **15.34%** | 9.84% | **6.47%** | 14.79% | 9.10% |

against **0.79%** for the LES/DNS truth and **0.10%** for k-omega SST, and reached
`||b||_F` of order **1.48e+07** on the NASA hump against the realisable maximum
`sqrt(2/3) = 0.8165`. **That model met criteria (i) and (ii) at 7 of 8 and was on track for a
PASS.** A model unphysical on an eighth of the domain would have been recorded as a success.

**The wording to adopt, frozen before the next run** (from `Ling2016_TBNN/RESULTS.md` §0, and
L-185):

> **NOT A RESULT** if the predicted `b` is non-realisable in more than **3x** the truth's own
> violation fraction on the same cells, or if `max ||b||_F` exceeds `sqrt(2/3)` by more than a
> factor of **2**, regardless of RMSE.

**Realisability is a correctness requirement, not an accuracy claim.** Sanderse et al. 2024
(arXiv preprint p. 20) record that the evidence that physics constraints improve accuracy is
"**rather thin**", with some studies pointing the other way. This charter gates on
realisability because an unphysical field is not a prediction, **not** because constraining it
is expected to lower the error.

**A forest is not safer than a network here, and the lab measured it.** TBRF on the same split
violates on **10.2% / 11.4% / 10.6%** (three seeds) and the 17-feature arm on **9.66%** —
against the TBNN's 6.47-15.34%. `Ling2016_TBNN/RESULTS.md`: "**A forest with bounded leaf
values is no safer here than a network.**" Do not assume the model class buys realisability.

**Generalise (L-185).** *Every quantity a preregistration asks you to report is a candidate
criterion.* For each one ask: what value of this would make me disbelieve the result? If such
a value exists it belongs in the ladder. If it does not, ask why it is being reported.

## 5. Extrapolation is detected by three instruments, all three registered

> **Every closure deployment reports (a) a distance statistic of the test features from the
> training cloud, (b) the per-cell rank of the tensor basis on the training data where a
> tensor basis is used, and (c) the two asymptotic tests. A case beyond the training envelope
> is labelled OUT-OF-FAMILY and its score is not pooled with in-family scores.**

**(a) Distance statistic.** `Ling2016_TBNN/RESULTS.md` §7(a) reports, per case, the median and
p99 Mahalanobis distance against a training p99 of **8.56**, and the fraction of test cells
beyond it. Seven cases sit at **0.00-0.70%**. `NASA_2DWMH` sits at **13.17%**, with a p99 of
**58.03** against the training **8.56**. `Wu2018_PIML_RF/RESULTS.md` §6 reports the same
instrument on its own split and finds E1's test p99 is **3,500x** its training p99.
**The instrument fired before the failure was diagnosed, on both models.**

**(b) Basis rank — the mechanism, and it is specific to tensor-basis models.** Pope's basis
collapses to three tensors in two dimensions (Pope 1975, JFM 72(2), p. 335), and every case in
this benchmark is a statistically two-dimensional mean flow. **Measured per case**, the mean
per-cell rank of the ten tensors runs **3.089 to 3.988** — `basis_rank_mean` in
`/home/ubuntu/closure-data/kaandorp_tbrf/results.json` under `baselines.<case>` — against
`T`-norms spanning seven orders of magnitude
(`15.4, 3.5e3, 1.0e3, 1.0e3, 2.0e2, 5.3e5, 8.4e7, 8.4e7, 4.9e7, 1.4e6`). **Coefficients
`g^(5..10)` are therefore unconstrained by the training data and multiply non-zero
`T^(5..10)` the moment a three-dimensional flow is presented.** An independent reproduction by
a second agent, with different feature sets and a different split, reproduced the blow-up:
hump values **136 / 282 / 174** over three seeds.

> **Provenance defect, recorded 2026-08-20, and this clause is why it was found.** Three
> records — `Ling2016_TBNN/RESULTS.md` §7b, `Wu2018_PIML_RF/RESULTS.md` §9 and
> `_common/FEASIBILITY.md` F2 — state a pooled rank of "**3.24 on average, never above 5**"
> and attribute it to `Kaandorp2020_TBRF/train_log.json`. **That file does not exist.** The
> only `train_log.json` in the tree is `Wu2018_PIML_RF/train_log.json`, which has no rank key.
> The per-case figures above are the measurement that does exist and can be re-derived. **3.24
> is not contradicted and is not currently supported; it is repeated in three places from a
> pointer that resolves nowhere**, which is precisely the shape §15 forbids for papers and
> which applies no less to the lab's own artefacts. Do not quote 3.24 until it has a live
> source.
This lab's own TBRF gives **197.3** (seed range **136.2-282.1**) and its 17-feature arm
**208.6** — all against the realisable bound of **0.8165**. **Two implementations, two feature
sets and two splits give the same failure, which makes it a property of the model class.**

`Ling2016_TBNN/RESULTS.md` §7b states the consequence this charter adopts:

> "**A benchmark of 2-D flows cannot test the claim that ten tensors are what these methods
> need.** Everything above is a result for a three-tensor model."

**(c) The two asymptotic tests** (Beck & Kurz 2021, arXiv preprint pp. 11-12): the model must
**switch off in laminar flow** and **switch off at DNS resolution**. Both are free to run and
**no paper in the 33-work corpus reports either.** A closure in this lab reports both.

**The honesty floor.** Sanderse et al. 2024 (arXiv preprint p. 21) record distribution shift as
"**largely unsolved**" with no detector proposed. **This lab measures the shift and reports it.
It does not claim to have solved it**, and no clause here may be cited as evidence that an
out-of-family prediction is trustworthy.

## 6. Feature invariance is verified over the whole composition, by a unit test

> **A model claiming Galilean, rotational or reflectional invariance carries a mechanical
> test: apply a boost and a rotation to a frozen field, recompute every input AND every
> normaliser, and require the output to transform correctly. The claim attaches to the
> composition — features, normalisers, basis, output map — or it is not made.**

**Why the composition and not the basis.** Wu, Xiao & Paterson 2018 is built on a 47-invariant
minimal integrity basis and its subject is invariance. Its Acknowledgment (arXiv preprint
p. 33) reads:

> "**one of the reviewers pointed out the lack of Galilean invariance in two of the
> normalization constants in our manuscript, which we fixed during the revision.**"

**The defect was not in the basis. It was in the normalisers dividing it, and it reached
submission.** Invariance is a property of a composition, and it is conventional to prove it
for the piece one designed and inherit it for the rest. The normalisers are the piece nobody
designs.

**The one group that audits its own inputs publishes the failures.** Kaandorp & Dwight 2020,
Table 1 (arXiv preprint p. 25), marks four of nine physically-motivated features with a dagger:
"**Features marked with † are rotationally invariant but not Galilean invariant**" — `k`,
`u_k dp/dx_k`, `u_i dk/dx_i`, `u_i u_j du_i/dx_j`. The output is invariant by the tensor basis;
four inputs are not; both facts are on the same page.

**What the test costs**: seconds, on a frozen field already on disk. **What it is not**: a
claim about accuracy — see §4's note on Sanderse.

**Recorded limit.** `Ling2016_TBNN/RESULTS.md` §6: "**Embedding the tensor basis buys Galilean
invariance and buys nothing else**: `b = sum g^(n) T^(n)` is unbounded, and nothing in the
architecture constrains the eigenvalues." Invariance and realisability are separate clauses
because they are separate properties.

## 7. Continuity: every post-hoc correction reports RMS div(U)

> **A correction applied to a velocity field without re-solving reports volume-weighted RMS
> `div(U)` relative to the field's own gradient scale, beside its accuracy number. Omitting
> that measurement is below the floor this lab has already published against itself.**

**The floor is our own entry.** `Certonomous_closure_challenge/description/METHOD.md` §6.2:

| Field | RMS div(U) relative to gradient scale |
|---|---|
| corrected hill `alpha_15_13929_4048` | **10.5%** |
| corrected hill `alpha_15_13929_2024` | **9.7%** |
| corrected hump | 0.66% |
| the underlying RANS | 0.08 to 0.47% |

with the sentence that sets the standard:

> "Entrants who re-solve get about 0 by construction. **We measured our departure and publish
> it.**"

**A lab that has published a 10.5% continuity violation against itself cannot accept a
closure record that is silent about continuity.** That is the whole argument for the clause.

**Mechanism, from the corpus.** Wang, Wu & Xiao 2017 (arXiv preprint p. 29) name why a
pointwise regressor produces this: "**A small region with abnormal Reynolds stress corrections
… can introduce large errors to the velocity predictions** … **These fluctuations, despite
being small in amplitude, can lead to abnormal behaviors in the divergence term.**" Only
`div tau` enters the momentum equation; a model scored on `tau` is scored one derivative away
from the quantity that acts.

**Not applicable is a legitimate answer and is stated.** `Wu2018_PIML_RF/RESULTS.md` records
"No continuity check is applicable" because it produced no velocity field. That is the correct
form: the row exists and says why it is empty.

## 8. Seeds: at least three, spread reported, and a margin must exceed it

> **Any stochastic closure result runs at least 3 seeds and reports mean and spread. A claimed
> margin over a baseline that does not exceed the seed spread is reported as within noise, and
> may not be stated as an improvement.**

**Worked, from the lab's own records.** `Wu2018_PIML_RF/RESULTS.md` runs 5 seeds and reports a
per-case spread of **0.0004 to 0.0031**; on `NASA_2DWMH` "the margin over SST is -0.022 and the
spread is 0.003", so the loss is real and outside noise, and is reported as a loss. The TBNN
runs 5 seeds with spread **0.0029-0.0090** on the in-domain cases and **3.71e+07** on the hump
— **a spread larger than most models' entire error is itself the finding.**

**The lab has already published this discipline against its own competition entry.**
`METHOD.md` §6.3 carries a one-seed bound of **0.002419** against a live margin of **0.001365**,
i.e. **179%** of the margin, and states: "**First on the point estimate; not first within
noise**", with "**179% is the figure to carry**, and it is the worse of the two."

**Cross-reference.** `docs/UNCERTAINTY-DOCTRINE.md` owns the three channels. This clause fixes
the minimum seed count for closure work and the rule that the margin must clear the spread.

---

# PART II — HOW A REPRODUCTION IS GRADED

## 9. Reproduction versus variant

> **A REPRODUCTION uses the paper's case, its data, its architecture and its metric. Anything
> else is a VARIANT. The label goes in `PREREGISTRATION.md` and `RESULTS.md`, with every
> departure listed. A VARIANT can never PASS the paper's number; it can only pass its own
> preregistered claims.**

**The instance.** Ling, Kurzawski & Templeton's headline is `b` RMSE **0.13** on duct flow at
`Re_b = 2000` (their Table I, p. 11). **None of their nine flows is on this machine.**
`Ling2016_TBNN/RESULTS.md` §1 handles it correctly: that number "**is not a target here and was
never treated as one.**" The work is a variant of the method on this benchmark's cases, and it
says so.

**`_common/FEASIBILITY.md` already carries the per-paper verdicts**
(`FEASIBLE`, `FEASIBLE-AS-LABELLED-VARIANT`, `BLOCKED`), and this clause makes the label
binding on the record rather than advisory in the matrix.

**Departures are listed, not summarised.** `Ling2016_TBNN/RESULTS.md` §8 lists learning rate
(paper 2.5e-7 for the TBNN and 2.5e-6 for the MLP, ours 1e-3), batch size, epoch cap, the
Durbin time-scale bound and the `beta* = 0.09` convention, each with its source page.

**Thread count is a departure.** Same file, §9: "**0.78 s per epoch at 4 threads against 49.4 s
at 16** — a factor of **63**, and the reason the sweep took about an hour instead of the
**66 hours** the first configuration was on track for. … **Anyone repeating this must pin the
thread count.**"

## 10. Train, validation and test disjointness is asserted in code, and every score is labelled IN-FAMILY or OUT-OF-FAMILY

> **Disjointness is enforced by an assertion that runs, not by a description. Every reported
> score carries an in-family or out-of-family label against the training set, and the two are
> never pooled into one headline.**

**Disjointness, done right.** `Wu2018_PIML_RF/RESULTS.md` §2 reports `train=23 val=5 test=8`,
group counts `13/3/6`, and cell counts **train 342,014, validation 77,611, test 152,634** of
641,652 with truth, plus **567 cells** dropped as non-finite — "**it is 0.09% of the valid
set**". `METHOD.md` §6.7 records the same discipline on the competition entry: "**Train,
validation and test disjointness is enforced by assertions.**"

**Family labelling, and why pooling hides the failure.** On the TBNN's eight test cases the
seven in-family cases score **0.1105 to 0.2364**; the one out-of-family case, `NASA_2DWMH`,
scores **1.48e+07**. `Ling2016_TBNN/RESULTS.md` §7b states the ground for the label: the hump
"is out-of-family in every respect — a different flow class, a Reynolds number **170x** the
hills', and the only stagnation region in the set", and the strong scores "**are all on the
duct cases**" — for example `AR_1_Ret_360`, where the 5-invariant TBRF scores **0.1157**
(3-seed range **0.1150-0.1165**) against SST's **0.5972** and the train-mean's **0.4221**.
**A single pooled mean over those eight numbers is not a summary of anything.**

**The subtler trap, and it is recorded because the lab hit it.**
`Wu2018_PIML_RF/RESULTS.md` §9:

> "**`alpha_05_7071_*` appears in E1's training set and in E2's test set.** The two experiments
> are internally disjoint but are not independent of each other; **E2's numbers must not be
> read as a second confirmation of E1's.**"

**Two experiments can each be internally clean and still not be two experiments.**

**Cross-reference.** `VERIFICATION_CHARTER.md` §11 owns the rule that nothing fitted may be a
scored case of a benchmark the lab reports against, and `LITERATURE_CHARTER.md` §7 owns its
intake side. This clause adds the family label and the assertion requirement.

## 11. Preregistration is frozen; departures are appended in a dated section, never edited in

> **The preregistration is frozen before results exist. A ladder is scored as written, even
> when the ladder is wrong. Departures and corrections are appended to `RESULTS.md` under a
> dated heading; the preregistration itself is never edited after the run.**

**The incident, 2026-08-20, and it is the sharpest thing in this charter.** An earlier draft of
`Ling2016_TBNN/RESULTS.md` recorded **GATE FAIL** on a falsifier reading "model output must
remain a physically meaningful anisotropy". **That clause is not in the preregistration. It
was written into the results after the realisability numbers were seen.** The correction, kept
in place rather than edited away:

> "**Correction, 2026-08-20.** … That is precisely the move L-179 … warns against — moving the
> goalposts after the fact, **even in the direction of being harsher** — and it is corrected
> here rather than quietly edited away."

**Why harsher is not safer** (L-185): "**a preregistration that can be tightened after the fact
can be loosened after the fact, and the reader has no way to tell which happened.**"

**The three-step remedy this charter adopts**, verbatim from L-185:

1. **Score the run on the ladder as written, even when the ladder is wrong.** The honest
   verdict was PENDING, not GATE FAIL.
2. **Then say the ladder was wrong, in the results, as a finding about the preregistration.**
   "A model that is unphysical on an eighth of the domain can score a PASS here" is a more
   useful sentence than a retro-fitted failure.
3. **Fix it in the NEXT preregistration, with the wording frozen before the next run.**

**And the tell, which is the part that generalises:** the author of that file "had written
L-179 — *write the falsifier so it can fire on the paper's own control* — an hour before
breaking it. **Writing the lesson is not the same as being governed by it.**"

**Cross-reference.** `VERIFICATION_CHARTER.md` §2b already rules that a preregistration
amendment is legal only while there is no answer to tune to, and §2d that a comparator is
frozen before its cases can answer it. This clause is the closure lane's instance and adds the
"score the wrong ladder as written" step.

## 12. The verdict vocabulary is fixed, and a verdict is only valid against a registered falsifier

> **The permitted verdicts are: `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`,
> `BLOCKED`, `PENDING`. No other word grades a closure run. A verdict is valid only against a
> falsifier that was in the preregistration before the run.**

Definitions as this lane uses them:

| Verdict | Meaning |
|---|---|
| `PASS` | Every registered acceptance criterion met, on the ladder as written. |
| `GATE REACHED` | A registered intermediate threshold met; the full ladder is not yet answered. |
| `GATE FAIL` | A registered criterion or falsifier fired. **Only a registered one.** |
| `NOT A RESULT` | The run produced numbers that do not bear on the question — a broken instrument, an identity gated as a control, an unphysical field under §4, or an a-priori score offered as a prediction claim. |
| `BLOCKED` | Cannot proceed: source, data or compute. Names which, and the acquisition path. |
| `PENDING` | A registered criterion's control has not landed. Not a failure and not a pass. |

**`NOT OBTAINED` is not in this list and is not a verdict.** `VERIFICATION_CHARTER.md` §6b owns
it: it is a statement about a *document*, carries four fields, and changes no tier by itself.
A closure record blocked on a paper says `BLOCKED` in its verdict line and `NOT OBTAINED`
against the reference.

**The lane already corrected itself once on this and the correction is the precedent** (§11).
A stale contradicting line survives in `Ling2016_TBNN/RESULTS.md` §0 — it still reads "It is a
**GATE FAIL** on the realisability falsifier" against the headline **PENDING** at line 11.
**The headline is the verdict; §0's line is stale and is scheduled for correction, not
quotation.** The same file disagrees with itself on seed counts ("the four completed seeds"
against "**All 5 seeds complete**"). **A record that grades itself in two places will
eventually be quoted from the wrong one.**

**Cross-reference.** `VERIFICATION_CHARTER.md` §6 (labels are claims), §6a (the referent travels
with the verdict), §2a (a gate declares its own failure mode at creation, and an identity may
be reported but never gated on) and §8 (failed gates ship as documented failures) all bind here
unchanged.

---

# PART III — HOW THE LANE OPERATES

## 13. Prior-art check before any reproduction, and a gate names the artefact that closes it

> **Before writing code for a named paper, search `verification/campaign/`, `cases/` and
> `research/` for the paper's name, its method's name and its case names. A gate that says
> "reproduce X" is closed by naming the artefact that satisfies it, never by re-running X.**

**Three occurrences, nineteen days.** `verification/campaign/W5_SPARTA_GATE_STATUS.md` is
titled "**W5 SpaRTA escalations — the gate both items demand was met three days before they
were worked**", and records: "**No solver was launched under either item, and that is the
finding, not a shortfall.**" Two docket items, both budgeted at 60 core-min, were closed at
**0** core-min because the run they demanded had already happened on 2026-08-01
(`w2-sparta-frozen-rans-cbfs`, created **two hours before** the first escalation was filed).

Then it happened again. L-182: a third agent was budgeted **20 core-hours** to reproduce SpaRTA,
wrote and compiled an entire OpenFOAM application, and then found **twenty run directories**
and a solver validated to **6e-15**, total prior cost **2.7 core-hours**. "**A search costing
about two minutes replaced a task budgeted at twenty core-hours.**"

**The diagnosis, from W5:** "**nothing links a gate to the record that satisfies it**", and
"The docket had no claim mechanism, so nothing marked the rung as about-to-be-worked."

**The structural half, and it is this lane's to fix (L-182):** "**Nothing in
`cases/RANS_LES_closure_models/` or `docs/closure/` pointed at
`verification/campaign/W2_SPARTA_*`; the closure work tree and the verification campaign tree
do not cross-reference, and the collision lives in that gap.**"

> **Therefore: `cases/RANS_LES_closure_models/<case>/RESULTS.md` names any campaign artefact
> that already answers its question, and `docs/closure/README.md` carries the map. A closure
> case directory that does not cross-reference the campaign tree is incomplete.**

`Schmelzer2020_SpaRTA/RESULTS.md` is the model: its verdict line reads "**PASS** at the ceiling
gate and **PASS** on the discovered-model gate — **reported from an EXISTING lab reproduction,
not from a new run**", and its first finding is "**The headline finding of this task is not a
number. It is that this reproduction had already been done.**"

**Report prior art as a finding, not as an embarrassment** (L-182). **And delete your own
duplicate, recording the deletion** (L-183): "**Sunk cost is not a reason to ship a duplicate;
silence about the sunk cost is a reason to distrust the record.**"

## 14. Shared-directory writes: check the path, and carry the recovery chain

> **Before writing to any path inside a shared case directory, test whether the path exists.
> A directory two agents have been told about is shared by definition. A recovered file is
> recorded as recovered, with its recovery route.**

**The incident, 2026-08-20.** Two sub-agents were assigned the same paper one hour apart after
a harness restart. The first created `tbrf.py` at **20:50:27Z**; the second wrote its own
implementation to the same path at **20:54:57Z**. `INCIDENT_tbrf_overwrite_2026-08-20.md`
records the sequence and its correction.

**The mechanical rule.** The `Write` tool says "created" or "updated" and that signal is read.
**A heredoc `>` says nothing**, so a shared-directory write uses `set -o noclobber` or an
explicit `[ -e f ]` test.

**Recovery is possible more often than it looks, and the search is for the bytes.** "**When a
file is lost, search every transcript for the bytes themselves** — a class name, a distinctive
comment, a constant — not for the tool that might have written it. Heredocs, `Edit` calls,
`sed -i` invocations and `cat` outputs all carry source." The first search failed; "the search
that succeeded took one grep."

**The disclosure rule, and the incident file demonstrates both halves.** It first asserted the
original was "**NOT RECOVERABLE**", then carried a **SUPERVISOR CORRECTION** repudiating that,
then recorded the chain: recovered file **6800 bytes** against **6799** extracted, a one-byte
trailing-newline difference; re-patched file now **7478 bytes**. And the honest limit:

> "the earlier statement "no subsequent edits found in transcripts" was **incomplete** — the
> transcript search missed the in-place patch. **Byte-identity with the destroyed file is
> therefore asserted only on the author's word plus the training score matching its run log.**"

> **Write the chain down — body hash, semantics of the writing tool, search for later edits —
> rather than either asserting byte-identity bare or refusing to assert it when the evidence
> is in hand.**

**A superseded module raises on import** so nothing silently runs the wrong model under the old
name.

## 15. The corpus: cite only from a title-verified PDF, and detect duplicates by hash

> **A paper is cited only from a PDF whose printed title page has been read and matched.
> Duplicates are found by grouping verified files by sha256. A number is never stated from
> memory; where the source is absent the record says `BLOCKED-ON-SOURCE` or `PENDING-MIT` and
> states no number.**

**L-144** earned the first half: 30 of the original 42 files were unrelated papers, each a
valid, hash-stable PDF whose manifest row certified the wrong document. **L-145** earned the
second: title verification tests identity and cannot test multiplicity, and six byte-identical
second copies passed every guard L-144 installed.

**The live instruments.** `docs/papers/closure/MANIFEST.md` carries the verification rule, the
33 canonical works with script-generated hashes, the 6 duplicates, the 30 quarantined wrong
retrievals kept as evidence, and the **16 PENDING-MIT** titles with DOIs for an institutional
pull. Duplicates re-derive with:

```
sha256sum docs/papers/closure/*.pdf docs/papers/closure/_DUPLICATES/*.pdf | sort | uniq -w64 -d
```

**The corpus is a live dependency (L-163).** Two papers arrived mid-task on 2026-08-20 —
`Wu2018_rans_explicit_closure_ill_conditioned.pdf` and `Guan2022_stable_aposteriori_les_cnn.pdf`
— and **both changed conclusions in documents already written.** A sentence of the form "X is
not on disk" carries a date and points at `MANIFEST.md` as the live authority.

**Provenance tiers are the literature charter's** (`LITERATURE_CHARTER.md` §2: READ IN FULL /
PAYWALLED, abstract-only / INTERNAL, already read; and "**there is no fourth tier for 'well
known', 'standard result' or 'widely reported'**"). This clause adds the closure lane's own
failure mode: a title-verified file is a necessary condition for a citation, not a sufficient
one for a count.

## 16. "What it cannot see" is a mandatory section

> **Every `RESULTS.md` in `cases/RANS_LES_closure_models/` and every paper block in
> `PAPER_CATALOGUE.md` carries a section headed with what the work cannot see. A record
> without one is incomplete and is returned.**

The section states what the result does not bear on: the quantity not measured, the flow class
not tested, the coupling not attempted, the uncertainty not propagated. It is not a disclaimer
and it is not modesty; it is the part of the record that stops a reader inferring a claim the
work does not support.

**The worked example is `Wu2018_PIML_RF/RESULTS.md` §9**, which is where the two most
load-bearing sentences in that file live — the a-posteriori limit quoted in §2 above, and the
E1/E2 non-independence quoted in §10.

**It is also what makes the paper corpus usable.** Every one of the 33 blocks in
`PAPER_CATALOGUE.md` carries one, and it is where the corpus records that five on-disk papers
report **no numeric error metric at all** for the thing they are about.

## 17. How lessons and numerics facts are filed

> **Lesson drafts go to the session scratchpad. The supervisor reviews and appends them to
> `docs/LESSONS.md` with the next `L-` number. Numerics facts go to
> `docs/NUMERICS_KNOWLEDGE.md`. A sub-agent never appends to either live file.**

The route is: draft to `scratchpad/lessons_<lane>.md` and `scratchpad/numerics_<lane>.md`;
supervisor reviews; supervisor appends and commits. Closure Phase 1-2 filed **L-145 to L-169**
this way.

**Numbering discipline.** Block count, distinct-number count and highest number are three
different figures and `docs/charters/README.md` §5 already explains why. Re-derive; do not
carry a count.

**A numerics fact carries its basis**, in the vocabulary the closure drafts adopted:
`PAPER-VERIFIED` (read from a title-verified PDF at the stated location), `PAPER-GRAPHICAL`
(the paper plots it and prints no number), `NOT STATED`. **A fact whose basis is
`PAPER-GRAPHICAL` may be described and may not be quoted as a number.**

## 18. Compute: 487 core-hours pre-authorised; above it, stop and cost it

> **Closure work under 487 core-hours is pre-authorised. A projected spend at or above that
> figure stops and is costed before launch. Every run is bounded and checkpointed, because the
> lab cannot kill a run it has started.**

**The authorisation.** `_common/FEASIBILITY.md` §2 bands every paper in the corpus against this
figure and names what sits at the edge: **Xiao 2016's full EnKF at ~450 core-hours for one
case** was flagged and not run; **Sirignano 2020 DPM, Bae 2022 SciMARL, Lozano-Duran 2023 BFWM
and Kochkov 2021's speed-up claim** are recorded as not reproducible here at any meaningful
scale. `Kaandorp2020_TBRF/PREREGISTRATION.md` cites the same 487-core-hour pre-authorisation
when justifying its depth and sample caps.

**Bounded and checkpointed, because kill is unavailable.** `Ling2016_TBNN` runs under a hard cap
of **400 epochs** with a checkpoint every **25 epochs**. That is the shape every closure run
takes. **L-140** is the reason: `writeInterval == endTime` converts every interruption into a
total loss rather than a proportional one, and the lab lost an 85%-complete run that way.

**Estimates are labelled as estimates.** `_common/FEASIBILITY.md` says so of itself: "Nothing in
this file has been timed yet; every core-hour number is an estimate and is labelled as one."
Measured costs replace them: Wu 2018 RF measured **245.4 s, ~0.3 core-hours on 4 threads**; the
SpaRTA rungs measured **27.7 of 60** and **137 of 180 core-min**.

**Cross-reference.** `COMPUTE_BUDGET_CHARTER.md` owns the unit, the gross-versus-cleaned honesty
rule, and the auto-stop contract — including that the box powers off after 30 minutes of
idleness as measured by a `pgrep` over solver names, and that **the control room does not count
as activity**. Nothing here weakens any of it.

## 19. Submissions are parked; nothing leaves the machine

> **No closure result, prediction set, model or manuscript leaves this machine. Submitting,
> uploading, registering or sending anything is Sanaa's decision alone and is taken by her.**

This is not a technical control and is not stated as one. It is the standing instruction the
lane runs under, and it is written here so that no agent has to infer it from silence.
`METHOD.md` §6.7 records the current state of the competition entry against this rule: "**Six**
prediction sets have ever been scored, on a self-imposed ledger. **No third party has yet
re-derived the trained-case CSVs.**"

---

# 20. Enforcement

**Written from what exists, not from intent.** Where nothing checks a clause this section says
so, because `LITERATURE_CHARTER.md` §8 is right that saying so is more useful than implying
otherwise.

| Clause | What checks it today |
|---|---|
| §3 baseline | `_common/trainmean_baseline.py` -> `trainmean_baseline.json`. Nothing is fitted; re-running reproduces it. **Automatic: no.** A reviewer checks the baseline column is present. |
| §5(a) distance statistic | Computed and tabled by both landed `RESULTS.md` files. **No script enforces its presence.** |
| §5(b) basis rank | Measured per case as `basis_rank_mean` in `/home/ubuntu/closure-data/kaandorp_tbrf/results.json`. **No script enforces its presence, and the pooled 3.24 figure quoted in three records has a dangling provenance pointer — see §5(b).** |
| §10 disjointness | **Yes** — assertions in the case code, and `sdk/scripts/closure_in_sample_gate.py` for the benchmark-leakage half, which returned `PASS` before and after each SpaRTA rung. |
| §12 vocabulary | **Nothing.** A grep for the six tokens across `cases/RANS_LES_closure_models/**/RESULTS.md` would catch a stray word and does not exist. **Proposed, not built.** |
| §15 corpus | **Yes, partly** — `MANIFEST.md` is script-regenerated, and the `uniq -w64 -d` duplicate sweep is one line. Title verification is manual by construction. |
| §15 filing | `scripts/check_filing.py` R8/R9. **See §21 — it could not see this corpus at all.** |
| §16 "what it cannot see" | **Nothing.** A heading grep would work and does not exist. |
| §18 compute | `COMPUTE_BUDGET_CHARTER.md` §4's auto-stop is installed and real. The 487-hour ceiling is honoured by hand. |

**Four clauses have no enforcement and are marked so.** A clause nobody can fail is a
preference, and this table is where that gets admitted rather than discovered.

---

# 21. Changes to other charters

**One change was required, and it is a gap rather than a contradiction.**

## 21.1 `FILING_CHARTER.md` R8/R9 — the rule was right and could not see the corpus

R8 requires "a matching `.txt` sidecar" for every paper and states "**a PDF and its sidecar
always travel together**". R9 in `scripts/check_filing.py` enforces it, and its own comment
explains the cost of a missing sidecar: a lane sweeping the library for prior art "**MISSED ALL
THREE AERODYNAMIC STATEMENTS**" of the thing it was looking for, because "the sweep returned a
clean zero and the zero meant nothing."

**Measured 2026-08-20**: `docs/papers/closure/` held **33 PDFs and 0 sidecars**. Every other
topic directory under `docs/papers/` matched exactly — 3/3, 4/4, 9/9, 7/7, 12/12, 1/1, 5/5,
4/4, 8/8, 3/3. **The closure corpus was the only one out of compliance, and
`check_filing.py` reported zero violations against it.**

**The mechanism, and it is R9's own failure mode one level up.** `docs/papers/closure/.gitignore`
contains `*.pdf`, so no closure PDF is git-tracked; `check_filing.py` enumerates via
`git ls-tree -r HEAD`; therefore the check could not see a single one of the 33 files it was
written to check. **A rule that cannot see its population reports a clean zero, which is the
exact defect R9 exists to prevent.**

**What was done.** The 33 sidecars were generated with `pdftotext <file.pdf> <file.txt>`, the
command R9's message names. `Gatski1996_handbook_chapter6.txt` is **77 bytes** — that file is a
300-dpi scan with no text layer, and the near-empty sidecar is the honest signal that it needs
OCR before it can be searched.

**No charter sentence was rewritten.** R8's prose is correct as written and R9's logic is
correct as written; the defect is that the enumerator and the ignore rule disagree about what
is in scope. **Two candidate repairs, neither taken here because neither is this charter's to
take:**

> **PROPOSAL.** Nobody has ruled on this. Written so there is something to argue with.
>
> **(a)** `check_filing.py` enumerates PDFs from the filesystem rather than from `git ls-tree`
> for directories carrying a `*.pdf` ignore rule, so untracked-but-present corpora are in
> scope. **(b)** Or `FILING_CHARTER.md` R8 states explicitly that the sidecar requirement
> applies to untracked paper corpora too, and the check gains a filesystem pass for them.
> **(a) is preferred**: it fixes the instrument rather than restating the rule the instrument
> already failed to apply.

**No other charter sentence was contradicted by the closure work.** Three were checked closely
and each holds as written: `VERIFICATION_CHARTER.md` §2c's trivial-baseline rule (§3 above is
its closure instance, not a competitor), §2b's amendment rule (§11 above adds a step and
weakens nothing), and §11's in-sample rule (§10 above adds a family label on top of it).

## 21.2 `docs/charters/README.md` §1 — the count was already stale before this charter

§1 reads "**The nine**" and gives the re-derive command `ls docs/charters/*_CHARTER.md | wc -l`.
**That command returned 10 before this file was written**, because `FILING_CHARTER.md` was
adopted 2026-08-18 and was never added to §1's table or its count. With this charter it returns
**11**.

**This is §5's own warning arriving at §1.** §5 says of `LESSONS.md`: "Do not read it cold, and
**do not carry a count of it in any index**", and gives commands instead of a figure. §1 carries
a hand-maintained count of a directory that grows, and it drifted within two days. **A count in
an index schedules its own next correction** — which is the sentence §5 already contains, about
a different file.

**README.md §1 has been updated**: title to "The eleven", both missing rows added, and a dated
note recording that the nine-to-ten step happened at `FILING_CHARTER.md`'s adoption and went
undisclosed at the time.

---

# 22. Related

| Document | What it owns that this charter does not |
|---|---|
| [`VERIFICATION_CHARTER.md`](VERIFICATION_CHARTER.md) | What counts as done; gate versus reference (§2); the identity test (§2a); preregistration amendment (§2b); the discrimination test and registered trivial baselines (§2c); comparator freezing (§2d); labels as claims (§6, §6a); `NOT OBTAINED` (§6b); in-sample versus generalization (§11). |
| [`LITERATURE_CHARTER.md`](LITERATURE_CHARTER.md) | Zero fabricated citations; provenance tiers (§2); figures count as text; the in-sample intake rule (§7). |
| [`COMPUTE_BUDGET_CHARTER.md`](COMPUTE_BUDGET_CHARTER.md) | The core-hour unit and its honesty rule; per-rung budgets; the auto-stop contract. |
| [`SUPERVISION_CHARTER.md`](SUPERVISION_CHARTER.md) | Who supervises what; the four checks a supervisor performs personally; model designation. |
| [`FILING_CHARTER.md`](FILING_CHARTER.md) | Where files go and what they are called; R8/R9 for papers and sidecars. |
| [`RESULT_PRIORITY_CHARTER.md`](RESULT_PRIORITY_CHARTER.md) | When two methods validate different quantities, the declared ordering picks and the trade is recorded. |
| `docs/closure/README.md` | The lane's map: what exists, in what order to read it, and the current verdict of every case. |
| `docs/papers/closure/MANIFEST.md` | The corpus of record: 33 canonical works, 6 duplicates, 30 quarantined, 16 PENDING-MIT. |
| `cases/RANS_LES_closure_models/_common/BASELINES.md` | The baseline numbers, including §6.4's train-mean tensor. |
| `cases/RANS_LES_closure_models/_common/FEASIBILITY.md` | Per-paper reproducibility verdicts and core-hour estimates. |
| `docs/UNCERTAINTY-DOCTRINE.md` | The three uncertainty channels and their recipes. |

# 23. Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-20 | First issue. Written after Phase 1-2 of the closure programme produced the realisability-gate hole (§4), the invented falsifier (§11), the third duplicate SpaRTA task in nineteen days (§13) and the `tbrf.py` overwrite (§14). Clauses trace to `LESSONS.md` L-140, L-144, L-145, L-163, L-168, L-179, L-182 through L-185, to the title-verified corpus under `docs/papers/closure/`, and to the lab's own measurements in `_common/BASELINES.md` §6.4 and `Certonomous_closure_challenge/description/METHOD.md` §6. Records one gap in `FILING_CHARTER.md`'s enforcement (§21.1) and one stale count in `README.md` §1 (§21.2). |
