# Prior art for the decline gate — literature review

**Prepared 2026-07-31.** Commissioned to answer one question before the entry claims
anything: **has the lab's actual contribution already been published?**

The contribution under examination is not the corrector. It is this:

> a correction whose application is **gated by a classifier that sees only the
> uncorrected solve and never the truth**, and which **refuses to act where acting
> would do harm**.

**Every citation below was fetched and checked. Author lists, DOIs and journal
references were read off the publisher or arXiv record, not recalled.** Where a claim
about a paper's method could not be verified from an accessible source, it is marked
unverified rather than asserted.

---

## 1. The verdict

**This is not novel as a class. It is a recombination, and one specific element of it
appears to be unpublished. The entry must claim the second, not the first.**

Three separate literatures already contain the ingredients:

| Ingredient | Already published? | Closest work |
| --- | --- | --- |
| Predict where RANS is unreliable, from RANS-only inputs | **Yes, since 2015** | Ling & Templeton 2015 |
| Estimate a data-driven closure's confidence *before* trusting it, from feature-space distance | **Yes, since 2017** | Wu, Wang, Xiao & Ling 2017 |
| Apply a learned correction **only** in classifier-selected regions | **Yes** | Steiner, Dwight & Viré 2022; Buchanan, Lăcătuş, West & Dwight 2025 |
| Protect the baseline by switching the correction off where the baseline is already good | **Yes** | conditioned field inversion (shield function) |
| Abstain / reject when the model is likely wrong | **Yes, since the 1970s**, as a general ML idea | reject-option and selective-prediction literature |
| Gate at the level of the **whole case**, deciding to submit the *uncorrected* baseline field for an entire flow | **Not found** | — |

**So: the "do-no-harm gate" is a known idea in turbulence closure, well enough
established that the Closure Challenge's own co-authors have published two variants of
it. What the lab did differently is the granularity and the direction of the decision.**

---

## 2. What is unambiguously prior art

### 2.1 Ling & Templeton 2015 — classifiers on RANS-only inputs that mark where RANS fails

Julia Ling, Jeremy Templeton, *Evaluation of machine learning algorithms for prediction
of regions of high Reynolds averaged Navier Stokes uncertainty*, **Physics of Fluids 27,
085103 (2015)**. Record: <https://www.osti.gov/pages/biblio/1235329>

Support vector machines, Adaboost decision trees and random forests are trained on a
database of canonical flows with validated DNS/LES, and classify RANS results
**point-by-point** as high or low uncertainty. Separate classifiers are built for three
specific RANS assumption breakdowns — eddy-viscosity isotropy, Boussinesq linearity, and
eddy-viscosity non-negativity. The paper reports that the classifiers generalise to
flows substantially different from the training flows.

**This is the ancestor of the lab's gate.** Training uses high-fidelity truth;
classification at prediction time uses RANS-available quantities. That is exactly the
lab's arrangement. The difference is that Ling & Templeton flag *where RANS is
uncertain*; they do not use the flag to withhold a correction.

**Confirmed and now load-bearing downstream (2026-08-05).** The method-priority review
(`CLOSURE_METHOD_PRIORITY_REVIEW.md` §4.2, commit `d84b649f`) re-fetched this abstract
from the same OSTI record and quotes it verbatim: the algorithms "were used to classify
RANS results on a point-by-point basis as having either high or low uncertainty".
**[ABSTRACT READ.]** This section had the identify-versus-control distinction right;
two downstream documents had lost it by compressing four papers into one
"classifier-controlled corrections" list. Both are now corrected in place —
`CLOSURE_METHODS_COMPARISON.md` §3.1 and `latex/closure_challenge_report.tex` §2.2 —
and both point back here.

### 2.2 Wu, Wang, Xiao & Ling 2017 — a priori confidence from feature-space distance

Jin-Long Wu, Jian-Xun Wang, Heng Xiao, Julia Ling, *A Priori Assessment of Prediction
Confidence for Data-Driven Turbulence Modeling*, **Flow, Turbulence and Combustion 99,
25 (2017)**, DOI [10.1007/s10494-017-9807-0](https://doi.org/10.1007/s10494-017-9807-0),
arXiv [1607.04563](https://arxiv.org/abs/1607.04563).

Defines a quantitative measure of distance in feature space between the training flows
and the flow to be predicted — Mahalanobis distance and a kernel-density-estimate
distance — and shows the prediction error of the Reynolds-stress anisotropy is
positively correlated with both. KDE distance is reported as the better estimator of the
two.

**This is the lab's "predicted baseline error" idea, published nine years earlier**, in
the form of an extrapolation metric rather than a fitted regressor. It is *a priori* in
exactly the sense the lab means: computed before, and without, any truth for the new
flow.

### 2.3 Steiner, Dwight & Viré 2022 — the closest published method

J. Steiner, R. Dwight, A. Viré, *Classifying regions of high model error within a
data-driven RANS closure: Application to wind turbine wakes*. arXiv
[2106.15593](https://arxiv.org/abs/2106.15593); published in **Flow, Turbulence and
Combustion (2022)**, DOI
[10.1007/s10494-022-00346-6](https://doi.org/10.1007/s10494-022-00346-6).

Verbatim from the abstract:

> "However experience suggests that closure model corrections need be made only in
> limited regions -- e.g. in the near-wake of wind turbines and not in the majority of
> the flow. A parsimonious model therefore must find a middle ground between precise
> corrections in the wake, and zero corrections elsewhere. We attempt to resolve this
> impasse by introducing a classifier to identify regions needing correction, and only
> fit and apply our model correction there. We observe that such a classifier **(which
> must be computed only from RANS-available quantities)** is straightforward to
> construct, and accurate in operation."

**Read that parenthesis carefully. It is the lab's own design constraint, stated as a
requirement, in 2021.** The classifier trains on LES reference data and reads only
RANS-available quantities at prediction time. The correction is fit *and applied* only
where the classifier fires.

Two differences remain, and they are the whole of the lab's remaining claim:

1. **Granularity.** Steiner et al. classify **cells/regions inside one flow**. The lab's
   gate classifies **an entire case**, and its "off" state means the submitted field for
   that whole flow is the unmodified RANS solve.
2. **Direction.** Steiner et al. identify where correction **is needed** — a positive
   marking, motivated by parsimony (fewer terms, simpler models). The lab's gate
   identifies where correction **would do harm** — a refusal, motivated by the baseline
   already being better than the corrector.

These are real differences. They are also *smaller than they look*: a region classifier
that fires nowhere in a flow is operationally a case-level decline. No paper found
reports that outcome or discusses it.

### 2.4 Buchanan, Lăcătuş, West & Dwight 2025 — and note who wrote it

Tyler Buchanan, Monica Lăcătuş, Alastair West, Richard P. Dwight, *Data-Driven RANS
Closures Using a Relative Importance Term Analysis Based Classifier for 2D and 3D
Separated Flows*, **Computers and Fluids 305, 106899 (2025)**, DOI
[10.1016/j.compfluid.2025.106899](https://doi.org/10.1016/j.compfluid.2025.106899),
arXiv [2504.06758](https://arxiv.org/abs/2504.06758).

Verbatim from the abstract: *"Our approach introduces a physics-based binary classifier
that systematically identifies separated shear layers requiring correction by analyzing
the relative magnitudes of terms in the turbulence kinetic energy equation ... our model
demonstrates significant improvements in predicting separation dynamics while
maintaining baseline performance and fully attached flows."*

Here the gate is a **physics-based** binary classifier — term-magnitude ratios in the
k-equation — rather than a fitted one, so it needs no training truth at all. The
stated goal, *maintaining baseline performance* where the baseline is fine, is the
lab's "do no harm" in the authors' own words.

> **FULL TEXT READ 2026-08-02.** This entry was written from the abstract, because the
> Computers & Fluids full text is paywalled. The arXiv version is not, and nobody had
> fetched it. `https://arxiv.org/html/2504.06758v1`, HTTP 200, read end to end; author
> list and journal reference confirmed on `arxiv.org/abs/2504.06758` (*Computers and
> Fluids* (2025)). **Everything this section inferred from the abstract holds, and the
> full text makes the distinctions sharper rather than softer.**
>
> **RITA is per-cell and physics-keyed, and it classifies flow regions, not cases.**
> Section 2.2, verbatim: *"RITA serves as a physics-based classification method designed
> to isolate flow phenomena, in this case, shear layers, based on the relative importance
> of terms in the k-equation of the k−ω SST model."* Its primary indicator is
> ϕ_{P_k/D_k} = |D_k| / (|P_k| + |D_k|), with two companions built the same way from
> convection and diffusion; the operative threshold is stated as *"in shear layers,
> ϕ_{P_k/D_k} consistently falls below 0.55, compared to boundary layer regions where
> destruction dominates (exceeding 0.55) and free-stream regions where this ratio
> approaches 1.0 due to minimal production."*
>
> **All three of the distinctions the lab claims for its own gate survive contact with
> the full text, and can now be stated against read wording rather than an abstract:**
> RITA selects **regions within a case**, where the lab's gate selects **whole cases**;
> RITA keys on **local term ratios of the baseline's own k-equation**, where the lab's
> gate is **fitted to predict the baseline's error** from training truth; and RITA's
> "off" state means **the unmodified SST model applies in that region of an otherwise
> corrected solve**, where the lab's "off" state means **the uncorrected field is what
> gets submitted for that case**. None of that makes the lab's gate novel — §2 of this
> document already settles that it is not — but the entry may now describe how it
> differs without guessing.
>
> **A fact with a direct consequence for us, and it is about our discipline, not their
> conduct.** Section 2.4 and Table 2: the paper's training set is three 2D separated
> flows — **the NASA wall-mounted hump (Re_h = 9.3×10⁵, 5.1×10⁴ cells, reference data
> Uzun and Malik)**, the periodic hill, and the curved backward-facing step. The hump is
> a **scored test case of the Closure Challenge**, and its cell count is the same
> 51,626-cell case the challenge ships. There is nothing improper in that: the paper is
> its own work, published in its own venue, and no challenge rule reaches it.
>
> **But it closes a route for us.** Appendix D of that paper publishes the model
> coefficients. Borrowing them, warm-starting from them, or calibrating anything of ours
> against that model's hump behaviour would make our entry **indirectly trained on a
> test case** — the correction would carry information from the hump's high-fidelity
> field through their fit. Under the challenge's one strict rule, and under the lab's own
> stricter standard that nothing it fits, inverts or calibrates on may be a scored case,
> **that model is off limits to this entry, and it is off limits precisely because it is
> the best-matched prior art we have found.** Recorded here so that the temptation is
> written down before anyone feels it.

#### The firewall, discharged as a compliance FACT (Ladder V Pass 2, rung V9, 2026-08-11)

The paragraph above is a *prohibition*, written before the pull was felt. This is the
*fact* that discharges it, so the entry can state compliance rather than only intent. It
is stated as a chronology, because chronology is the only form of this claim that cannot
be argued with:

| fact | evidence |
|---|---|
| The shipped `NASA_2DWMH` prediction is byte-identical across rounds 3, 4 and 5 | round-5 CSV `sha256 cf8e023c7b8f…`, `filecmp` against `closure_challenge_submission_round4/test/` — identical; §0f records the case as unchanged, Δ = 0 |
| That prediction was written **before** this paper was mentioned in the repository at all | the round-3 entry landed at `cb0694d1` / `f5c98f96` (2026-07-29); the CSV last moved at `fe121af2` (2026-07-31T06:53Z). The first commit anywhere in this repository containing the string `2504.06758` is `92840d8c` (2026-07-31T23:13Z) — **16 h later**, and abstract-only |
| It was written **three days before** the paper was read in full | full text read at `15530f97` (2026-08-02T05:30Z), whose own subject line records the outcome: *"reading it closes a route rather than opening one"* |
| No Appendix-D coefficient, and no artifact of that model, exists anywhere in this repository | `grep -rniE "buchanan\|RITA\|2504\.06758\|lacatus"` over the tree returns **zero hits in any executable file**. The three apparent code hits (`sdk/chief_engineer/uq.py`, `sdk/chief_engineer/openfoam.py`, `sdk/scripts/closure_eval_battery/build_master_table.py`) are substring matches inside the word *autho**rita**tive*. Every real hit is prose in a record |
| The round-5 duct change carries nothing from it either | the only new coefficient in the entry is `Ccr1 = 0.3`, Spalart (2000)'s published QCR2000 constant; nothing is fitted (Ladder V rung V5, `303247bb`) |

**One use of the paper does touch the hump, and it is disclosed rather than denied.**
`closure_challenge_C6_hump_decision.md` cites this paper for the hump's Reynolds number
(Re_h = 9.3×10⁵, their §2.4 / Table 2) — a **property of the benchmark's own test case**,
not a coefficient and not an output of their model. It was used to argue that CBFS is
*not* a close donor for the hump, i.e. to **close** Route B, which was then withdrawn.
Nothing from that citation entered any submitted field: the hump prediction it concerned
is the same bytes it was three days before the paper was opened.

**Verdict: the firewall holds, and it holds by date rather than by assurance.**

> **This matters for how the entry is written.** **Tyler Buchanan and Richard Dwight are
> both co-authors of the Closure Challenge paper itself** (McConkey, Buchanan, Smidt,
> Bodner, Dwight, Cinnella, arXiv [2603.28884](https://arxiv.org/abs/2603.28884)).
> Richard Dwight is additionally a co-author of Steiner et al. 2022 and of SpaRTA
> (Schmelzer, Dwight & Cinnella, *Flow, Turbulence and Combustion* 104, 579–603, DOI
> [10.1007/s10494-019-00089-x](https://doi.org/10.1007/s10494-019-00089-x)). **The
> people who will read our submission have published the nearest prior art twice.**
> An entry that presents selective, classifier-gated correction as its own invention
> will be read by the inventors. Cite them.

### 2.5 Conditioned field inversion — a hand-designed do-no-harm shield

*Development of a Generalizable Data-Driven Turbulence Model: Conditioned Field
Inversion and Symbolic Regression*, **AIAA Journal**, DOI
[10.2514/1.J064416](https://arc.aiaa.org/doi/10.2514/1.J064416). The correction factor
in the SST model is multiplied by a shield function that is off inside the attached
boundary layer and on elsewhere, so the model reduces exactly to baseline SST where the
baseline is trusted.

**Author list not verified** — the publisher page was not accessible without
authentication and no open version was confirmed. Cite by title and DOI, or verify
before naming authors.

This is the same objective reached without any classifier: a hand-designed geometric
gate rather than a learned one. It is worth citing precisely because it shows the
"protect the baseline" goal is standard, and that the interesting question is only *how*
the gate is decided.

### 2.6 Mondrian forests — knowing when the prediction is untrustworthy

Ashley Scillitoe, Pranay Seshadri, Mark Girolami, *Uncertainty Quantification for
Data-driven Turbulence Modelling with Mondrian Forests*, **Journal of Computational
Physics (2021)**, DOI
[10.1016/j.jcp.2021.110116](https://doi.org/10.1016/j.jcp.2021.110116), arXiv
[2003.01968](https://arxiv.org/abs/2003.01968). Replaces random forests with Mondrian
forests to obtain principled predictive uncertainty, reported to be large where the
training data is not representative — an in-situ out-of-distribution signal.

Supplies the *uncertainty* half without the *decision* half: it tells you the prediction
is untrustworthy; it does not withhold it.

### 2.7 Progressive Mixture-of-Experts — routing, and the road not taken

Haoyu Ji, Yinhang Luo, Hanyu Zhou, Yaomin Zhao, *Progressive Mixture-of-Experts with
autoencoder routing for continual RANS turbulence modelling*, arXiv
[2601.09305](https://arxiv.org/abs/2601.09305) (January 2026, revised May 2026).

An autoencoder router reads local flow features **extracted from a baseline RANS
calculation**, marks a point as recognised when its reconstruction error is below the
99.9th-percentile training threshold, aggregates a **global per-flow confidence** as the
fraction of recognised points, and routes the flow to the expert with maximum
confidence.

**That aggregation step is the case-level gate the lab built, arrived at independently.**
The difference is what happens next: when the maximum confidence falls below the
acceptance threshold, PMoE declares the flow unknown and **spawns a new expert** — it
expands rather than abstains. There is **no fallback to the uncorrected baseline**.

**This is the single most important citation for the entry**, because it is the one
paper found that computes a whole-flow confidence from the cheap solve alone, and it
still does not do the thing the lab's gate does with it.

**Tier upgraded 2026-08-05: [READ IN FULL].** The 2026-07-31 reading of this section
was re-checked against the fetched HTML text rather than carried forward, per
`docs/charters/LITERATURE_CHARTER.md` §7, by the method-priority review
(`CLOSURE_METHOD_PRIORITY_REVIEW.md` §2.2, commit `d84b649f`). **Our record was right**,
and the paper's own words are now on our record rather than our paraphrase of them:
"The global confidence level p_k of expert k regarding the current flow is defined as
the relative frequency of recognised points"; and "When the maximum confidence p_𝒦
exceeds a threshold of T_accept = 90%, the expert E_𝒦 will be activated. Conversely, if
p_𝒦 falls below T_accept, the flow is deemed unknown, which triggers the continual
learning process." The low-confidence branch initialises and trains a new expert. **There
is no branch that submits the uncorrected baseline.**

### 2.8 The general ML framing the entry should borrow

Abstaining, rejecting and selective prediction are a mature area of machine learning
with their own vocabulary. *Machine learning with a reject option: a survey*, **Machine
Learning (2024)**, DOI
[10.1007/s10994-024-06534-x](https://dl.acm.org/doi/abs/10.1007/s10994-024-06534-x),
arXiv [2107.11277](https://arxiv.org/abs/2107.11277), traces the idea to classification
work in the 1970s.

The lab's gate is a **selective regressor with a reject option, where rejection falls
back to a physics baseline rather than to a human**. Naming it in that established
vocabulary is more honest and more useful than presenting it as new machinery.

---

## 3. What this means for what the entry may claim

**Delete any claim of a novel method class.** The following would be false:

- ~~"a novel confidence-gated correction framework"~~ — Steiner et al. 2022, Buchanan et al. 2025
- ~~"the first use of a RANS-only classifier to control a data-driven correction"~~ — Ling & Templeton 2015 for the classifier, Steiner et al. 2022 for the control
- ~~"novel a priori applicability estimation"~~ — Wu et al. 2017

**What survives, and it is narrow and worth saying precisely:**

1. **Case-level refusal with baseline fallback.** No located work decides, for a whole
   flow, to submit the *uncorrected* field on the grounds that correcting it would be
   worse. The nearest — PMoE — computes the whole-flow confidence but responds by
   adding an expert, never by declining.
2. **The gate is trained to predict the BASELINE's error, not the corrector's
   confidence.** Prior work asks "is this flow like my training data?" (Wu et al.,
   Scillitoe et al., PMoE) or "is RANS locally violating an assumption?" (Ling &
   Templeton, Steiner et al., Buchanan et al.). The lab's gate asks a different
   question: *how large is the baseline's error going to be?* — and declines when the
   answer is "small", because a small baseline error is what a corrector cannot beat.
   That framing was not found in the located literature.
3. **The refusal is reported as a result, not hidden.** Two of the entry's five
   best-on-board cases are cases where the method declined to act. No leaderboard
   convention exists for that, and disclosing it is a contribution to how such
   benchmarks are read.

**Recommended one-sentence framing for the submission:**

> Classifier-gated selective correction is established — we follow Ling & Templeton
> (2015), Wu et al. (2017), Steiner et al. (2022) and Buchanan et al. (2025) — and our
> contribution is to move the gate from the cell to the whole case, to train it on the
> *baseline's* error rather than on distribution shift, and to let its "off" state mean
> submitting the uncorrected RANS field and saying so.

**This is a reproduction with a modification, not an invention.** That is a weaker claim
than the record previously implied by saying nothing, and it is the true one.

---

## 4. Search record and limits

Terms run: do-no-harm correction; selective application of turbulence closure
correction; applicability estimation; trust region for data-driven closure;
confidence-gated model correction; out-of-distribution detection for turbulence closure;
abstention / reject option in turbulence modelling; error estimator deciding whether a
correction improves a case; safeguard / fallback to baseline; machine-learned turbulence
model selection and recommendation; forward from SpaRTA and TBNN.

**Limits, stated so a reader can judge coverage.** This was a targeted search of open
web and arXiv, not a systematic review. ~~Two paywalled items could not be opened
(Computers & Fluids and AIAA Journal full texts) and are cited from verified metadata
plus abstracts only.~~ **Updated 2026-08-02: one of the two is now read in full.** The
Computers & Fluids item, Buchanan, Lăcătuş, West & Dwight 2025, has an open arXiv
version at `2504.06758` which nobody had fetched; it was read end to end and §2.4 above
now quotes its methodology section rather than its abstract. **One paywalled item
remains** — the AIAA Journal full text at DOI 10.2514/1.J064416, §2.5 — still cited by
title and DOI only, with its author list still unverified and therefore still unnamed.
One further candidate, *Error Quantification for the Assessment of
Data-Driven Turbulence Models* (Flow, Turbulence and Combustion, DOI
10.1007/s10494-022-00321-1), **is deliberately not cited**: the DOI resolves but the
author list and abstract could not be retrieved, and the standing rule is that an
unverifiable citation does not ship. Anyone extending this review should start there,
and with forward citations of Steiner et al. 2022.

**Absence of evidence is reported as absence of evidence.** "Not found" above means not
found by this search. It does not mean it does not exist.
