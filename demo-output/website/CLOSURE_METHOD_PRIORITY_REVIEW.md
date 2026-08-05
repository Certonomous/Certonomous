# Closure-challenge method — priority and novelty review

**Prepared 2026-08-05.** Katie's brief: verify by literature review that the
closure-challenge method was **not** unknowingly copied from prior work —
establish priority honestly, or find the priors we must cite. Governed by
`docs/charters/LITERATURE_CHARTER.md` (zero fabricated citations; every claim
carries a provenance tier) and `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md`
(every query recorded, negatives counted, §5a's countable-negative rule for a
novelty claim).

**Read first, as instructed**: `CLOSURE_METHODS_COMPARISON.md` (commit
`ac2f37ee`) and `CLOSURE_CHALLENGE_STATUS.md`. Also read before searching:
`CLOSURE_CHALLENGE_PRIOR_ART.md` (the lab's 2026-07-31 gate-only review),
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §7.4,
`closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md`, and
`latex/closure_challenge_report.tex` §§2.1–2.3.

**Discipline of this pass.** Web **read-only**; nothing posted, nothing
submitted, no account created. **Zero compute; zero solver runs; zero
`score()` calls; no test-case file opened.** No source is cited that was not
fetched in this session or already read in full by a prior recorded session.
27 searches and 20 page fetches are logged in §6, including the six fetches
that failed and the one that returned the wrong paper.

**Provenance tiers used** (charter §2, plus two this pass needed):

| Tier | Meaning |
| --- | --- |
| **READ IN FULL** | Full text fetched and read this session. |
| **ABSTRACT READ** | The publisher/arXiv abstract was fetched and quoted verbatim this session. Nothing beyond its literal sentences is asserted. |
| **METADATA ONLY** | Bibliographic record fetched and confirmed; abstract not obtained verbatim. Only the metadata and the tool-summarised gist is used, and it is labelled as such. |
| **INTERNAL, already read** | A prior lab session read the full text and reproduced it in our record; attributed to that file. |
| **SEARCH EXCERPT — NOT CITED** | Appeared in a search result only. Recorded in §6 as a lead. **Never used as the basis of a claim.** |

---

## 1. The verdicts, at a glance

| # | Element | Verdict | Closest prior | Distance |
| --- | --- | --- | --- | --- |
| 1 | Post-hoc velocity-field correction trained on baseline features, no re-solve | **PRIOR-EXISTS** | Hanna, Dinh, Youngblood & Bolotnov 2017/2019 (CG-CFD error prediction) | **Very close.** Same architecture (surrogate predicts the cheap solve's local error from the cheap solve's own local features; add it back; never re-solve). Different error source, different field. |
| 2 | Per-case do-no-harm decline gate, "off" = submit raw RANS | **NO-PRIOR-FOUND** for the combination; **PRIOR-EXISTS** for every component | Ji, Luo, Zhou & Zhao 2026 (PMoE) for whole-flow confidence; Buchanan et al. 2025 / Steiner et al. 2022 for classifier-controlled correction | Narrow but real. Confirmed against the *fetched* PMoE text this session: its low-confidence branch **expands** (spawns an expert), never falls back to the baseline. |
| 3 | Pre-registered scoring discipline, self-imposed single-call ledger | **PRIOR-EXISTS**, and this is the element our records cite least | Blum & Hardt 2015 (the Ladder); NeurIPS Pre-registration in ML workshops 2020/2021 | **Small.** The ideas — adaptive-overfitting from repeated holdout queries, and freezing an analysis plan before results — are both established and named. Our delta is that the discipline is **submitter-imposed on a benchmark that imposes none**. |
| 4 | Regime-restricted retraining under a pre-declared hurt cap (R5 NO-GO) | **PRIOR-EXISTS** as a concept; **NO-PRIOR-FOUND** as a turbulence-closure instance | Thomas, Theocharous & Ghavamzadeh 2015 (high-confidence policy improvement); pre-specified non-inferiority margins | **Moderate.** The "only adopt if certified not worse than the baseline" rule is a named idea in two other fields. Ours is the same rule at per-case granularity, but with a **hand-chosen** cap where those literatures derive one. |

**One-sentence answer to Katie's question.** Nothing was copied — every element
was arrived at from our own case evidence, and the searches below found no
document we had read and reproduced. But **element 1 has a close prior we do
not cite anywhere**, and elements 3 and 4 have well-named priors in
neighbouring fields that our records do not name either. The combination of
2+3+4 as practised remains unlocated. **The honest claim is a recombination
with one genuinely unlocated component (element 2's case-level baseline
fallback), not an invention.**

---

## 2. Element by element

### 2.1 Element 1 — post-hoc velocity-field correction, no re-solve

**What we claim it is.** `CLOSURE_CHALLENGE_STATUS.md` §4 and
`latex/closure_challenge_report.tex` §2.1: target
`δU = U_LES − U_RANS` per mesh cell, learned from seven or eight per-cell
features of the converged baseline RANS field, applied once as a final
post-processing step; nothing re-enters the governing equations.

**VERDICT: PRIOR-EXISTS.** The architecture is published, twice over — once in
CFD and once, much earlier, as a general statistical practice.

**Closest prior, and it is close.**

> Botros N. Hanna, Nam T. Dinh, Robert W. Youngblood, Igor A. Bolotnov,
> *Coarse-Grid Computational Fluid Dynamic (CG-CFD) Error Prediction using
> Machine Learning*, arXiv:1710.09105 (submitted 25 October 2017).
> **[ABSTRACT READ, fetched 2026-08-05.]** Journal version: *Machine-learning
> based error prediction approach for coarse-grid Computational Fluid Dynamics
> (CG-CFD)*, **Progress in Nuclear Energy 118 (2019), 103140**, DOI
> [10.1016/j.pnucene.2019.103140] — metadata confirmed at OSTI record 1692047
> this session; **that record states "Not Available" for the abstract**, so
> nothing is asserted from the journal version beyond its existence and
> bibliographic details. **[METADATA ONLY.]**

Verbatim from the arXiv abstract, fetched this session:

> "Hence, a method is suggested to produce a surrogate model that predicts the
> CG-CFD local errors to correct the variables of interest. Given high-fidelity
> data, a surrogate model is trained to predict the CG-CFD local errors as a
> function of the coarse grid local features. ML regression algorithms are
> utilized to construct a surrogate model that relates the local error and the
> coarse grid features."

Map that onto ours, term for term: *cheap simulation* = the shipped k-ω SST
solve; *local error* = `δU = U_LES − U_RANS`; *coarse grid local features* =
our seven Pope invariants plus `Re_y`, `tke_ratio`; *correct the variables of
interest* = add `δU` to the submitted field. **The sentence "a surrogate model
is trained to predict the [baseline] local errors as a function of the
[baseline's own] local features" is our method statement with two words
swapped.** They also test transfer to unseen Reynolds numbers and unseen grid
sizes, which is the generalization axis the challenge scores.

**Where it applies to us**: as the citation for the *method class* — learned
local-error correction of a cheap CFD solve, applied without re-solving.
**Where it does not**: the error they correct is **discretization error from
grid coarsening on a lid-driven cubic cavity**, not turbulence-closure error on
separated and secondary flows; their abstract states no decline gate, no
case-level decision, and no benchmark-submission discipline. It is a prior for
element 1 alone.

**Deeper prior, at the level of the idea rather than the implementation.**

> Marc C. Kennedy, Anthony O'Hagan, *Bayesian Calibration of Computer Models*,
> **J. R. Statist. Soc. B 63(3) (2001), 425–464**. Metadata confirmed on the
> Oxford Academic record this session; the abstract page returned a summary
> rather than verbatim text, and the Ohio State PDF copy was unreadable to the
> fetch tool. **[METADATA ONLY.]** What may be asserted from what was
> retrieved: the paper's stated contribution includes correcting the model by
> identifying discrepancy between observed data and the model's own best
> predictions ("model inadequacy" is one of the record's own keywords).

This is the statistical ancestor of "add a learned discrepancy term to a
simulator's output instead of changing the simulator." Cite it as lineage, not
as method — we did not read its full text.

**Lead not cited**: Glahn & Lowry's 1972 *Model Output Statistics* is the
oldest form of this idea (statistical post-processing of numerical model
output). The AMS page returned **HTTP 403** and the Semantic Scholar page
returned empty content, so **no Glahn & Lowry citation ships from this pass**.
Recorded in §6 so the next reader starts there rather than re-deriving it.

**What the search did NOT find, and this matters.** Across six queries aimed
squarely at the turbulence literature (§6 rows 1, 3, 4, 16, 21, 22), **every
located data-driven RANS correction that produces a velocity field does so by
putting something back into the equations and re-solving.** Checked
individually rather than by title:

- **Wang, Wu & Xiao**, *Phys. Rev. Fluids* 2, 034603 (2017),
  arXiv:1606.07987 — **[ABSTRACT READ]**: predicts *Reynolds-stress*
  discrepancies from mean-flow features, then propagates them through the
  solver to obtain velocity.
- **Luther & Jenny**, *Non-Linear Super-Stencils for Turbulence Model
  Corrections*, arXiv:2411.16493 (2024/2025) — **[ABSTRACT READ]**, verbatim:
  "a fully connected neural network that learns a mapping from the local mean
  flow field to **a corrective force term, which is added to a standard RANS
  solver**". Intrusive; re-solved.
- **Diez Sanhueza, Smit, Peeters & Pecnik**, arXiv:2210.15384 —
  **[ABSTRACT READ]**: the "correction" in its abstract is applied to the ML
  model's own outputs during training, not to a computed flow solution.

So `CLOSURE_METHODS_COMPARISON.md`'s row *"Re-solved with correction: no —
unique among the five"* is not only true of the five entrants; **within the
data-driven RANS closure literature swept here, we found no other instance
either.** The prior that exists is outside turbulence closure. That is a
stronger and more interesting statement than the one we currently make, and it
is also the reason the Hanna citation is owed: it shows we did not invent the
class, only its application here.

**One prior we should cite in our own favour, which we currently do not.**

> Jin-Long Wu, Heng Xiao, Rui Sun, Qiqi Wang, *Reynolds-averaged
> Navier–Stokes equations with explicit data-driven Reynolds stress closure can
> be ill-conditioned*, **J. Fluid Mech. 869 (2019), 553–586**, arXiv:1803.05581.
> **[ABSTRACT READ, fetched 2026-08-05]** — verbatim opening: "Reynolds-averaged
> Navier–Stokes (RANS) simulations with turbulence closure models continue to
> play important roles in industrial flow simulations. However, the commonly
> used linear eddy viscosity models are intrinsically unable to handle flows
> with non-equilibrium turbulence."

The arXiv record's own summary of the result — Reynolds-stress errors below
0.5% producing velocity errors up to 35% — is the published reason why
correcting velocity *directly* sidesteps a real conditioning problem that every
entrant above us has to survive. **Where it applies**: as principled support in
§2.1 for why the method class is defensible rather than merely cheap. **Where
it does not**: it says nothing about our conservation gap (audit finding G2) and
must not be used to soften it. And per charter §7, the 0.5%/35% figures are
quoted here as the arXiv record's stated result, **not** as a number we read off
the paper's own tables; anyone citing them in a shipped document should fetch
the paper and read the table first.

### 2.2 Element 2 — the per-case do-no-harm decline gate

**VERDICT: NO-PRIOR-FOUND for the specific form. PRIOR-EXISTS for every
component of it.** This pass confirms `CLOSURE_CHALLENGE_PRIOR_ART.md`'s
2026-07-31 conclusion and adds two things it did not have: the general-ML
vocabulary verified first-hand, and the PMoE fallback question settled against
the fetched text.

**Settled this session, from the source rather than from our own note.**
`CLOSURE_CHALLENGE_PRIOR_ART.md` §2.7 claims PMoE aggregates a whole-flow
confidence and responds to low confidence by expanding rather than declining.
Charter §7 forbids carrying a citation forward without re-checking it, so it was
re-fetched:

> Haoyu Ji, Yinhang Luo, Hanyu Zhou, Yaomin Zhao, *Progressive
> Mixture-of-Experts with autoencoder routing for continual RANS turbulence
> modelling*, arXiv:2601.09305v1, 14 January 2026. **[READ IN FULL — HTML
> version fetched 2026-08-05.]** Verbatim: "The global confidence level p_k of
> expert k regarding the current flow is defined as the relative frequency of
> recognised points"; and "When the maximum confidence p_𝒦 exceeds a threshold
> of T_accept = 90%, the expert E_𝒦 will be activated. Conversely, if p_𝒦 falls
> below T_accept, the flow is deemed unknown, which triggers the continual
> learning process."

**Our record was right.** PMoE computes exactly our quantity — a whole-flow
confidence from the baseline field alone — and its low-confidence branch
initialises and trains a new expert. **There is no branch that submits the
uncorrected baseline.** That is the single closest published approach to
element 2 and it stops one step short.

**The general-ML framing, verified rather than inherited.** Our gate is a
*selective regressor with a reject option*. That literature is mature:
`CLOSURE_CHALLENGE_PRIOR_ART.md` §2.8 already cites the reject-option survey
(DOI 10.1007/s10994-024-06534-x, arXiv:2107.11277) **[INTERNAL, already read]**.
This pass's queries (§6 rows 12, 23) surfaced the regression-with-rejection and
learning-to-defer branches. **In every located formulation, rejection defers to
a human, to an external expert, or to an abstain symbol at a stated cost.**
None defers to a *physics baseline that is itself a valid submission*. That is
the unlocated part, and it is exactly what our records already claim.

**Ling & Templeton is prior art for the classifier, not for the control — and
two of our documents blur this.** Verbatim from the OSTI record of Ling &
Templeton (*Phys. Fluids* 27, 085103, 2015), fetched this session
**[ABSTRACT READ]**:

> "The algorithms were trained on a database of canonical flow configurations
> for which validated direct numerical simulation or large eddy simulation
> results were available, and were used to classify RANS results on a
> point-by-point basis as having either high or low uncertainty, based on the
> breakdown of specific RANS modeling assumptions."

The abstract flags uncertain regions. It does not gate, withhold, or control a
correction — `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.1 states this correctly
("they do not use the flag to withhold a correction"); two downstream documents
lost the distinction. See §4.2.

**Where element 2's distinctions stand after this pass** — unchanged from
`CLOSURE_CHALLENGE_PRIOR_ART.md` §3, now with the PMoE half re-verified:
case-level granularity; the gate predicts the **baseline's** error rather than
distribution shift; "off" means the uncorrected field **is** the submission.

### 2.3 Element 3 — pre-registered scoring discipline and the self-imposed ledger

**VERDICT: PRIOR-EXISTS, comfortably. This is the element where our documents
name the fewest priors, and the one where a referee is most likely to know the
literature by name.**

The problem our ledger addresses has a name and a canonical paper:

> Avrim Blum, Moritz Hardt, *The Ladder: A Reliable Leaderboard for Machine
> Learning Competitions*, arXiv:1502.04585 (16 February 2015); ICML 2015,
> PMLR 37. **[ABSTRACT READ, fetched 2026-08-05.]** Verbatim: "What makes this
> estimation problem particularly challenging is its sequential and adaptive
> nature. As participants are allowed to repeatedly evaluate their submissions
> on the leaderboard, they may begin to overfit to the holdout data that
> supports the leaderboard. ... Existing approaches therefore often resort to
> poorly understood heuristics such as **limiting the bit precision of answers
> and the rate of re-submission**."

Read that last clause against our own practice. **Our five-call ledger is, in
Blum & Hardt's own words, one of the "poorly understood heuristics" — rate
limiting — applied by the submitter to itself.** They say it is a heuristic and
build a principled alternative. We should say the same about ours before a
reviewer does. This does not weaken the discipline; it correctly prices it as
harm reduction rather than a guarantee, and it is squarely on the side of the
qualification the round-4 record already carries about cross-round adaptive
leakage (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §5.3.3).

The freeze-the-plan-before-results half also has a named venue in our own field
of practice:

> **NeurIPS 2020 Workshop on Pre-registration in Machine Learning**, PMLR
> Volume 148, held virtually 11 December 2020; editors Luca Bertinetto, João F.
> Henriques, Samuel Albanie, Michela Paganini, Gül Varol. Volume title, date and
> editor list confirmed on the PMLR volume page this session.
> **[METADATA ONLY.]** A second edition exists as PMLR Volume 181 (NeurIPS
> 2021) — recorded from the same publisher listing, same tier.

Adjacent and worth one sentence rather than a paragraph: registered reports and
pre-specified analysis plans in the life sciences, and the ADEMP-PreReg template
for simulation studies, both surfaced in §6 row 8 as **[SEARCH EXCERPT — NOT
CITED]**; and blind CFD validation challenges where predictions are submitted
before the experimental data is released (the VT-NASA BeVERLI challenge, §6 row
7, same tier). Neither is cited here because neither was fetched.

**Our delta, stated precisely.** The challenge imposes no submission limit and
its README instructs submitters to preview their score
(`CLOSURE_CHALLENGE_STATUS.md` §5, §0e). Pre-registration and query budgeting
are established as *organiser-side* mechanisms and as *reviewer-side* publishing
models. **What we did not find is a case of an entrant imposing either on
itself, unasked, and publishing the ledger.** That is a disclosure practice, not
a method, and it should be claimed as one.

### 2.4 Element 4 — regime-restricted retraining under a pre-declared hurt cap

**VERDICT: PRIOR-EXISTS as a concept, in two other fields. NO-PRIOR-FOUND as a
turbulence-closure instance.**

The rule "adopt the retrained model only if it is certified not to be worse than
the incumbent" is a named research problem:

> Philip Thomas, Georgios Theocharous, Mohammad Ghavamzadeh, *High Confidence
> Policy Improvement*, **Proc. 32nd ICML, PMLR 37, 2380–2388 (2015)**.
> **[ABSTRACT READ, fetched from the PMLR record 2026-08-05.]** Verbatim: "We
> present a batch reinforcement learning (RL) algorithm that provides
> probabilistic guarantees about the quality of each policy that it proposes,
> and which has no hyper-parameter that requires expert tuning. Specifically,
> the user may select any performance lower-bound and confidence level and our
> algorithm will ensure that the probability that it returns a policy with
> performance below the lower bound is at most the specified confidence level."

That is the R5 gate's logic — a pre-declared floor, and a refusal to deploy when
the floor is not met — with two differences that cut **against** us:

1. **Their bound is probabilistic and user-parameterised; our +0.010 per-case
   hurt cap is a single hand-chosen number with no stated derivation.**
   `closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md` §3 declares the cap
   before the deltas exist, which is the part that matters for leakage — but it
   never says *why 0.010*. This is `LITERATURE_CHARTER.md` §6 trigger 2 (a
   method whose admissibility could be written as thresholds) and it forces a
   proposal; filed, see §7.
2. Thomas et al.'s guarantee is about the *aggregate*; our cap is *per-case*,
   which is stricter and is the reason R5 failed on one case while improving on
   eight of ten.

The same shape appears twice more. The ML-systems literature calls a retrained
model's regression on previously-correct instances a **negative flip**, and
constrains it directly (backward-compatible weight interpolation,
arXiv:2301.10546; MUSCLE, arXiv:2407.09435 — both **[SEARCH EXCERPT — NOT
CITED]**, listed in §6 row 10 as leads). Clinical trials pre-specify a
**non-inferiority margin** in the protocol precisely so it cannot be chosen
after the data (§6 row 24, same tier). **Our per-case hurt cap is a
non-inferiority margin under another name.** Naming it that way is more honest
and more legible than presenting it as bespoke.

**The countable negative.** Query 11 (§6) aimed directly at a turbulence-closure
instance of a pre-declared degradation cap and returned **zero** — the located
turbulence work discusses catastrophic forgetting and out-of-distribution
degradation as *phenomena*, never as a pre-declared acceptance criterion that
can veto a deployment. Combined with the four-entrant absence already recorded
in `CLOSURE_METHODS_COMPARISON.md` §3.1, element 4 is unlocated in this field.

---

## 3. The closest prior found, named once

**Hanna, Dinh, Youngblood & Bolotnov (2017 arXiv / 2019 *Progress in Nuclear
Energy*).** Nothing else located in 27 searches comes as close to any single
element of our method. It is close enough that a referee who knows the
nuclear-thermal-hydraulics ML literature would recognise our element 1 on sight,
and close enough that **not citing it would read as either ignorance or
concealment.** It is also far enough away — different error source, different
flow, no gate, no submission discipline — that citing it costs us nothing we
were entitled to keep.

Second-closest, and it is the one that matters for the *interesting* claim:
**Ji, Luo, Zhou & Zhao (PMoE, arXiv:2601.09305)**, which computes our exact
whole-flow confidence quantity and then does something else with it.

---

## 4. Novelty phrasing audit — sentences named, corrections proposed, nothing silently fixed

Per the brief: where a prior is close enough that our phrasing overstates, the
sentence is named and the correction stated. **Nothing below has been edited.**

### 4.1 Overstatement by silence — element 1 carries no citation anywhere

**The sentence**, `latex/closure_challenge_report.tex` lines 231–235 (and its
twin at `CLOSURE_CHALLENGE_STATUS.md` §4):

> "**Nothing re-enters the governing equations and nothing is re-solved with the
> correction folded in.** In the Duraisamy--Iaccarino--Xiao taxonomy this is the
> ``correct the answer'' family, structurally distinct from FIML, TBNN, SpaRTA
> and eigenvalue perturbation, all of which correct something inside the
> equations before re-solving"

**What is wrong with it.** Every clause is true. But it places our method in a
taxonomy, names four families we are *not*, and cites **no prior work for the
family we are in** — the only supporting reference is our own
`docs/research/CLOSURE_METHODS.md`. A reader reaches the end of §2.1 having been
told what the method is not, and never told that anyone has done it before. That
is origination by omission, and `LITERATURE_CHARTER.md` §3 ("an omission is a
finding") and `docs/standards/INNOVATION_STANDARD.md` stage 1 (a literature
basis on the record before a method is admitted) both reach it.

**The correction owed** — an addition, not a retraction: after "correct the
answer" family, add that learned local-error correction of a cheap CFD solve,
applied without re-solving, is itself established — Hanna et al. — and that the
statistical form goes back to model-discrepancy calibration (Kennedy & O'Hagan
2001, cited as lineage at METADATA ONLY tier). **What survives, and should be
stated in the same breath**: within the data-driven RANS-closure literature swept
here, no other instance of a *velocity-field* post-hoc correction was located, so
the application to turbulence closure is ours even though the class is not.

**Second, smaller issue in the same passage.** The Duraisamy–Iaccarino–Xiao
taxonomy is invoked by name with no citation. The review exists — *Turbulence
Modeling in the Age of Data*, **Annual Review of Fluid Mechanics 51 (2019),
357–377** — but this pass reached only the Annual Reviews landing page and a
scholar-lookup stub (§6 row 15), **not the text**, so the tier available today is
METADATA ONLY and the review's own words for that family have not been read by
anyone in this lab. Either fetch it and quote the family name, or attribute the
phrase to our own `docs/research/CLOSURE_METHODS.md` as a paraphrase. Do not
leave a named taxonomy uncited.

### 4.2 Mis-attribution — Ling & Templeton credited with control they did not exercise

**The sentences.** `CLOSURE_METHODS_COMPARISON.md` §3.1:

> "Ling & Templeton 2015, Steiner et al. 2022, Buchanan et al. 2025 (RITA;
> co-authored by the challenge's own authors) are established prior art for
> **classifier-controlled corrections**"

and `latex/closure_challenge_report.tex` line 294:

> "**Classifier-controlled data-driven corrections are established:** Ling \&
> Templeton, \emph{Phys.\ Fluids} 27, 085103 (2015); Wu, Wang, Xiao \& Ling ...;
> Steiner, Dwight \& Vir\'e ...; and Buchanan ..."

**What is wrong with it.** Ling & Templeton's abstract, quoted verbatim in §2.2
above, describes classification of RANS results as high or low uncertainty. It
controls no correction. Wu, Wang, Xiao & Ling 2017 likewise supplies an *a
priori* confidence measure, not a control. Grouping four papers under
"classifier-controlled corrections" credits two of them with a mechanism they did
not report — the precise failure `LITERATURE_CHARTER.md` §7 names ("attribute a
mechanism to a source that reported a correlation"). `CLOSURE_CHALLENGE_PRIOR_ART.md`
§2.1 gets this right; the two downstream documents lost it when they compressed
the list.

**The correction owed.** Split the list in both places:

> Classifiers on RANS-only inputs that *identify* where the baseline is
> unreliable are established (Ling & Templeton 2015; Wu, Wang, Xiao & Ling
> 2017); *using such a classifier to control where a data-driven correction is
> fitted and applied* is established separately (Steiner, Dwight & Viré 2022;
> Buchanan, Lăcătuş, West & Dwight 2025).

Note this correction makes our own position **more** defensible, not less: it
shows we know which paper did which thing.

### 4.3 Sentences checked and found sound — no correction owed

- `CLOSURE_METHODS_COMPARISON.md` §3.1, "Re-solved with correction: **no —
  unique among the five**", and its LaTeX twin. Correctly scoped to the board.
  This pass found no counterexample in the wider closure literature either, so
  the scoping is conservative rather than generous.
- `CLOSURE_METHODS_COMPARISON.md` §3.1's closing paragraph, which explicitly
  limits the uniqueness claim to "unique **among the five entries on this
  board**, not in the literature". Exactly right; it is the model the other
  documents should follow.
- `latex/closure_challenge_report.tex` §2.2's bullet "**It is not novel, and the
  nearest prior art is by the challenge's own authors.**" Sound, and it is the
  reason the report survives this review as well as it does.
- `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §7.4's "Any sentence presenting
  confidence-gated correction as novel must be struck." Still holds; still no
  such sentence found, on `closure.html` or elsewhere (re-grepped this session).
- `closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md` — makes no novelty
  claim at all. Its gap is the underived cap (§2.4), not overstatement.

**Soft flag, no correction demanded.** `latex/closure_challenge_report.tex`
line 268: "The **distinguishing component** of the entry is a case-level decline
gate." Distinguishing among the five, which the surrounding table establishes —
and the bullet twelve lines later says plainly that it is not novel. A reader who
stops at line 268 could take it more broadly. If one word is spent, "the
distinguishing component **of this entry among the five**" removes the ambiguity.

---

## 5. Citations we now owe, and exactly where each belongs

| # | Citation | Tier available today | Where it belongs | What it is for |
| --- | --- | --- | --- | --- |
| C1 | Hanna, Dinh, Youngblood & Bolotnov, arXiv:1710.09105 (2017); *Prog. Nucl. Energy* **118** (2019) 103140, DOI 10.1016/j.pnucene.2019.103140 | ABSTRACT READ (arXiv) / METADATA ONLY (journal) | **`latex/closure_challenge_report.tex` §2.1**, at the "correct the answer" sentence — **mandatory**. **`CLOSURE_CHALLENGE_STATUS.md` §4**, same sentence. **Submission draft §5.1 / method statement** — the description document is what the challenge's authors read. | The prior for element 1's method class. Cite with the delta stated: their error source is grid coarsening, ours is closure. |
| C2 | Kennedy & O'Hagan, *J. R. Statist. Soc. B* **63**(3) (2001) 425–464 | METADATA ONLY | **`latex/closure_challenge_report.tex` §2.1**, one clause, as lineage. Optional in the submission draft. | Establishes that adding a learned discrepancy to a simulator's output, rather than changing the simulator, is a 25-year-old statistical practice. **Do not quote its text** until someone reads it. |
| C3 | Wu, Xiao, Sun & Wang, *J. Fluid Mech.* **869** (2019) 553–586, arXiv:1803.05581 | ABSTRACT READ | **`latex/closure_challenge_report.tex` §2.1** and **§2.4 ("costs of this method class")**; **submission draft**, in the paragraph defending the method class. | The one prior that argues *for* us: propagating stress corrections through the RANS equations is ill-conditioned, so correcting velocity directly avoids a real published hazard. Must not be used to soften the G2 conservation gap. |
| C4 | Blum & Hardt, arXiv:1502.04585 (2015), ICML/PMLR 37 | ABSTRACT READ | **`latex/closure_challenge_report.tex` §2.3 (Pre-registration)**; **`CLOSURE_CHALLENGE_STATUS.md` §5** at the scoring-call ledger; **submission draft §5.3.3**, beside the cross-round adaptive-leakage disclosure. | Names the problem the ledger addresses (adaptive overfitting of a holdout under repeated queries) and prices our answer honestly as a rate-limiting heuristic, in the source's own words. |
| C5 | NeurIPS Workshop on Pre-registration in Machine Learning, PMLR **148** (2020) and **181** (2021) | METADATA ONLY | **`latex/closure_challenge_report.tex` §2.3**, one sentence. | Shows pre-registration in ML is an established practice with a venue, so our §2.3 reads as adopting a known discipline rather than inventing one. |
| C6 | Thomas, Theocharous & Ghavamzadeh, *Proc. 32nd ICML*, PMLR **37** (2015) 2380–2388 | ABSTRACT READ | **`closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md` §3**, beside the GO/NO-GO rules; **`latex/closure_challenge_report.tex` §"The pre-registration that said no"**. | Names the rule (deploy only if certified not worse than the incumbent) and exposes that our +0.010 cap is undERived where theirs is parameterised — which is the honest framing and the source of the proposal in §7. |
| C7 | Ji, Luo, Zhou & Zhao, arXiv:2601.09305 (2026) | **READ IN FULL** (this session) | **`CLOSURE_CHALLENGE_PRIOR_ART.md` §2.7** — upgrade its tier from the 2026-07-31 reading to READ IN FULL with the two verbatim quotes in §2.2 above; **`latex/closure_challenge_report.tex` §2.2**, where element 2's distinction is claimed. | The nearest miss on element 2. Quoting its expand-don't-decline branch verbatim is the strongest available support for our narrow claim. |
| C8 | Duraisamy, Iaccarino & Xiao, *Annu. Rev. Fluid Mech.* **51** (2019) 357–377 | METADATA ONLY — **not yet read by this lab** | **`latex/closure_challenge_report.tex` §2.1**, where the taxonomy is already invoked by name without a reference. | Closes an uncited named-taxonomy reference. **Fetch and read before quoting the family name**; otherwise attribute the phrase to our own `docs/research/CLOSURE_METHODS.md`. |

**Already owed and already paid** — no action, listed so the ledger is complete:
Ling & Templeton 2015, Wu/Wang/Xiao/Ling 2017, Steiner/Dwight/Viré 2022,
Buchanan/Lăcătuş/West/Dwight 2025, the reject-option survey, Scillitoe et al.
2021, and the conditioned-field-inversion AIAA item are all carried in
`CLOSURE_CHALLENGE_PRIOR_ART.md` and reach the LaTeX report §2.2 and submission
draft §7.4. **The one correction they need is the §4.2 split**, not a new source.

---

## 6. Query log

All 2026-08-05 (UTC), web read-only. **Hit** = at least one on-point document
located. **NEGATIVE** = no document performing the specific thing sought; this
is the countable-negative form `PROBLEM_RESEARCH_PROTOCOL.md` §5a requires.

### 6.1 Searches (27)

| # | Element | Query | Outcome |
| --- | --- | --- | --- |
| 1 | 1 | machine learning correction RANS velocity field non-intrusive without re-solving post-processing | Hit (class-level); **NEGATIVE** for a post-hoc *velocity* correction in RANS closure — all located CFD hits intrusive |
| 2 | 1 | machine learning error prediction coarse grid CFD correction Hanna Dinh | **Hit — the closest prior (C1)** |
| 3 | 1 | "discrepancy" machine learning RANS mean velocity field correction trained "post-hoc" OR "a posteriori" OR "output" turbulence LES | **NEGATIVE** — every hit propagates a stress/source correction through the solver |
| 4 | 1 | neural network predicts mean velocity correction "delta U" RANS LES difference regression cell features no propagation | **NEGATIVE** — hits are corrective *force* terms added to the solver |
| 5 | 1 | super-resolution machine learning mapping RANS mean flow to LES DNS mean flow direct field-to-field turbulence | Off-target (image-style SR of instantaneous fields, not a mean-field correction); **NEGATIVE** for our form |
| 6 | 3 | pre-registration machine learning benchmark leaderboard "adaptive overfitting" limited test set queries ladder Blum Hardt | **Hit (C4)** |
| 7 | 3 | blind prediction challenge CFD turbulence workshop submissions before data release validation "blind test" | Hit — VT-NASA BeVERLI blind validation challenge. **Lead only, not fetched, NOT CITED** |
| 8 | 3 | preregistration computational science simulation study "registered report" analysis plan frozen before results | Hit — registered reports, ADEMP-PreReg. **Leads only, not fetched, NOT CITED** |
| 9 | 4 | safe policy improvement baseline guarantee "high confidence" Thomas reinforcement learning do not underperform behavior policy | **Hit (C6)**; also SPIBB as a lead |
| 10 | 4 | machine learning model update backward compatibility negative flip regression constraint no instance worse | Hit — negative-flip / backward-compatibility line. **Leads only, not fetched, NOT CITED** |
| 11 | 4 | turbulence closure retraining "worst case" degradation cap pre-declared acceptance criterion data-driven model "no case" worse | **NEGATIVE** — degradation appears as a phenomenon, never as a pre-declared veto criterion |
| 12 | 2 | selective prediction abstention surrogate model scientific machine learning fall back to physics-based model when uncertain | **NEGATIVE** for fallback to a physics baseline; abstention literature confirmed as mature |
| 13 | 2 | classifier selects turbulence model per flow case machine learning "model selection" RANS automatically choose between baseline and data-driven | **NEGATIVE** for a per-case baseline/corrected choice |
| 14 | 1 | Kennedy O'Hagan 2001 Bayesian calibration computer models discrepancy function output correction | **Hit (C2)** |
| 15 | 1 | Duraisamy Iaccarino Xiao "Turbulence Modeling in the Age of Data" Annual Review 2019 taxonomy | Metadata located; **full text not reached** (C8 stays METADATA ONLY) |
| 16 | 1 | "velocity field" correction machine learning applied "as a post-processing step" RANS "no additional solve" OR "without additional simulation" turbulence benchmark | **NEGATIVE** — all located corrections re-enter the equations |
| 17 | 3 | "pre-registration" machine learning research NeurIPS 2020 workshop proposal Albanie preregistering | **Hit (C5)** |
| 18 | 1 | Glahn Lowry 1972 "Model Output Statistics" objective weather forecasting regression numerical model output | Lead located; **both primary records failed to fetch (see 6.2) — NOT CITED** |
| 19 | 1 | McConkey Yee Lien machine learning turbulence "predicting" mean velocity field data-driven curated dataset evaluation | **NEGATIVE** — the challenge steward's own line predicts anisotropy and propagates it; no post-hoc velocity correction |
| 20 | 1 | Wu Xiao Sun Wang "RANS equations with explicit data-driven Reynolds stress closure can be ill-conditioned" JFM 2019 | **Hit (C3)** |
| 21 | 1 | "one-time post-processing step" machine learning discrepancy baseline solution turbulence random forest | **NEGATIVE** — the phrase does not resolve to a turbulence source; nearest genuine hits are weather MOS post-processing |
| 22 | 1 | data-driven correction applied directly to converged RANS mean velocity field "without solving" momentum equations turbulence machine learning periodic hill | **NEGATIVE** — surfaced NLSS (intrusive, confirmed by fetch) |
| 23 | 2 | "learning to defer" OR "reject option" regression fallback to numerical solver surrogate CFD when model unreliable | **NEGATIVE** for the CFD/physics-baseline fallback; deferral targets are humans or abstain symbols |
| 24 | 4 | non-inferiority margin pre-specified stopping rule clinical trial protocol prevents post hoc analysis | Hit (concept: pre-specified margin). **Leads only, not fetched, NOT CITED** |
| 25 | 2 | arXiv 2601.09305 Progressive Mixture-of-Experts autoencoder routing continual RANS turbulence modelling confidence | Hit — located the full text for the fetch below |
| 26 | 2 | turbulence machine learning benchmark entry "submitted the baseline" declined correction whole case abstain leaderboard RANS | **NEGATIVE** — no benchmark entry located that submits the uncorrected baseline by decision |
| 27 | 4 | Thomas Theocharous Ghavamzadeh "High Confidence Policy Improvement" ICML 2015 proceedings abstract | Hit — located the PMLR record for the fetch below |

**Negatives counted: 13** across four elements, over the venues open-web search
reaches (arXiv, publisher records, OSTI, PMLR, journal indexes). Added to the
twelve-term sweep already recorded in `CLOSURE_CHALLENGE_PRIOR_ART.md` §4, the
citable form is: **no prior report of a case-level decline gate whose "off"
state submits the uncorrected baseline was found under 13 recorded negative
searches this session plus the 2026-07-31 sweep, across arXiv, publisher
records and OSTI, as of 2026-08-05.**

### 6.2 Fetches (20; 6 failed or unusable, recorded per charter §2)

| Target | Result |
| --- | --- |
| arxiv.org/abs/1710.09105 | **OK** — abstract quoted verbatim (C1) |
| osti.gov/pages/biblio/1692047 | **OK** — journal metadata; record states abstract "Not Available" |
| osti.gov/pages/biblio/1235329 | **OK** — Ling & Templeton abstract quoted verbatim |
| arxiv.org/abs/1606.07987 | **OK** — Wang/Wu/Xiao; confirmed stress-discrepancy + propagation |
| arxiv.org/abs/2411.16493 | **OK** — Luther & Jenny abstract verbatim; confirmed intrusive |
| arxiv.org/abs/2210.15384 | **OK** — Diez Sanhueza et al.; confirmed not a post-hoc field correction |
| arxiv.org/html/2601.09305v1 | **OK — READ IN FULL**; two verbatim quotes (C7) |
| arxiv.org/abs/1502.04585 | **OK** — Blum & Hardt abstract verbatim (C4) |
| arxiv.org/abs/1803.05581 | **OK** — Wu/Xiao/Sun/Wang abstract opening verbatim (C3) |
| proceedings.mlr.press/v148/ | **OK** — volume title, date, editor list (C5) |
| proceedings.mlr.press/v37/thomas15.html | **OK** — abstract verbatim (C6) |
| academic.oup.com/jrsssb/…/425/7083367 | **PARTIAL** — metadata confirmed; abstract returned as summary, not verbatim (C2 capped at METADATA ONLY) |
| arxiv.org/abs/2603.28884 | **OK** — challenge preprint abstract verbatim; **confirms the preprint states no submission limit, no blind protocol, no decline mechanism** |
| arxiv.org/abs/2408.02688 | **PARTIAL/UNUSABLE** — abstract truncated at 125 chars, author string garbled. **NOT CITED**; recorded as a lead (non-intrusive corrections to under-resolved simulations, climate/QG) |
| journals.ametsoc.org (Glahn & Lowry 1972) | **FAILED — HTTP 403** |
| semanticscholar.org (Glahn & Lowry 1972) | **FAILED — empty content returned** |
| nature.com/articles/s42005-025-02149-3 | **FAILED — 303 redirect to an auth host**; the arXiv version was fetched instead |
| asc.ohio-state.edu/…/KennedyOHagan.pdf | **FAILED — PDF unreadable to the fetch tool** |
| people.cs.umass.edu/~pthomas/papers/Thomas2015b.pdf | **FAILED — PDF unreadable**; recovered via the PMLR record instead |
| arxiv.org/abs/1509.01813 | **WRONG PAPER** — the arXiv ID guessed for Ling & Templeton resolves to an unrelated mathematics paper. Recorded because a guessed identifier is exactly how a fabricated citation is born; the correct route was the OSTI record. |

---

## 7. Limits, charter triggers, and the proposal this reading owes

**Limits, stated so coverage can be judged.** This was a targeted open-web and
arXiv sweep, not a systematic review, and it inherits
`CLOSURE_CHALLENGE_PRIOR_ART.md`'s limits. No paywalled full text was opened.
Four of the eight owed citations are ABSTRACT READ and three are METADATA ONLY —
**none of the new priors has been read in full by this lab**, and any sentence
that leans harder on one than its tier permits is a defect. Where forward
citations of Steiner et al. 2022 and of Hanna et al. 2019 would be the obvious
next sweep, they were not run.

**Absence of evidence is reported as absence of evidence.** "NO-PRIOR-FOUND"
means not found by the 27 searches in §6. It is not a claim that no such work
exists, and no document of ours should upgrade it to one.

**`LITERATURE_CHARTER.md` §6 triggers, each checked by name:**

- **Trigger 1 (a number on a case we can build): does not fire.** Hanna et al.'s
  lid-driven cubic cavity is buildable but grades discretization error, not a
  closure-relevant quantity this lab's wall reports.
- **Trigger 2 (a method whose admissibility could be written as thresholds):
  FIRES.** Thomas et al. 2015 parameterises the deploy/decline bound by a stated
  performance floor and confidence level; the pre-specified non-inferiority
  margin is the same discipline in another field. **Our R5 hurt cap of +0.010 is
  hand-chosen and its pre-registration never states a derivation.** Proposal
  filed: `demo-output/website/agenda/proposals/w8-a-hurt-cap-that-states-where-it-came-from.json`.
- **Trigger 3 (a paper disagrees with one of our results): does not fire.** No
  located source contradicts a measured number of ours. Wu et al. 2019 *supports*
  our method class; it does not contest a result.
- **Trigger 4 (a limit case checkable at zero compute): does not fire.** No
  correlation with a stated design range was taken from any source.

**`LITERATURE_CHARTER.md` §7, last NEVER — in-sample reproduction.** Checked
explicitly. **None of the eight owed citations proposes a method to reproduce on
a scored case.** C1 (Hanna et al.) would reproduce on a lid-driven cavity, which
is not in the benchmark. C3, C4, C5, C6 and C8 are framing and discipline
citations with no fit step. C7 (PMoE) would, if reproduced, need training data —
**and it is not proposed for reproduction here**, precisely so that the question
of which flows it would fit on does not arise unasked. The standing constraint
from `CLOSURE_CHALLENGE_PRIOR_ART.md` §2.4 — that Buchanan et al.'s published
coefficients are off limits because they trained on `NASA_2DWMH` — is unchanged
and unweakened by this pass.

**Nothing in this document changes the entry of record.** Round 4 (0.0654)
stands; no prediction set was created, altered or scored; the in-sample and
test-blind guards were never approached.
