# W2 reading well, part 2 — the two open rungs: TBNN and SpaRTA

Date opened: 2026-07-31 (UTC). **Zero-compute task**: fetch, read, index, propose. No solver
was launched to produce this document. Every cost quoted below carries the run it was measured
from, and no cost is extrapolated from a run that is broken or superseded.

**Why this file is separate from `W2_CLOSURE_LITERATURE_READING.md`.** That document is open
and its section numbering is in use by another hand (it carries forward references to sections
2 and 3 that were not present when this session read it). Appending here avoids renumbering
somebody else's live file. This is the same well, the same charter, the same tiers.

**Scope.** Roadmap M2 names a reproduction ladder — field inversion, then TBNN, then SpaRTA.
Field inversion is proven and FD-verified on this lab's own hardware at 2.67%. These are the
next two rungs, and neither paper had been read into the knowledge store: both appeared in
`docs/research/CLOSURE_METHODS.md` at metadata tier only, indexed from CrossRef records and
search-result text, with no claim sourced to a full text.

**Provenance discipline** per `docs/charters/LITERATURE_CHARTER.md` section 2. Both papers
below are **READ IN FULL**. Neither needed MIT access. Availability checks are reported with
their actual answers.

**An omission is a finding.** Where a paper withholds a quantity needed to rebuild its result,
the omission is the outcome of the reading, not something to smooth over.

---

## 1. Ling, Kurzawski & Templeton — the tensor-basis neural network

**Ling, J., Kurzawski, A. & Templeton, J., "Reynolds averaged turbulence modelling using deep
neural networks with embedded invariance," *Journal of Fluid Mechanics* 807:155–166 (2016),
DOI `10.1017/jfm.2016.615`.** **READ IN FULL** — the Sandia accepted manuscript
**SAND2016-7345J**, dated 24 July 2016, fetched from OSTI (record 1333570) and held at
`docs/papers/ling_kurzawski_templeton_jfm2016_osti1333570.pdf` with its text extraction
alongside. Unpaywall reports `is_oa: true` for the DOI with a repository copy at OSTI.
**No MIT access required**; the row was already closed on `docs/research/MIT_ACCESS_DOCKET.md`
on 2026-07-30, and this session is the one that read the fetched text.

**Version labelled.** This is the accepted manuscript, not the Cambridge version of record.
Every quotation below is from that manuscript. Where a page or equation is cited it is the
manuscript's own numbering.

### Claim, source, where it applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The architecture's whole content is one multiplicative output layer: the network predicts the ten scalar coefficients `g(n)` of Pope's integrity basis, and the Merge Output Layer "performs element-wise multiplication between the outputs of the Final Hidden Layer and the Tensor Input Layer and then sums the result to give the final prediction for b". Invariance is structural — "Any tensor b which satisfies this condition will automatically satisfy Galilean invariance." | Ling, Kurzawski & Templeton 2016, SAND2016-7345J, READ IN FULL, section II.B and Eq. 1. | Any closure that must be frame-indifferent by construction rather than by training. The whole trick is one layer; it is a small change to a standard MLP, not a new training algorithm. | The basis is Pope's 1975 result for **incompressible** flow as a function of **only S and R**. A closure needing wall distance, pressure gradient or history is outside this representation. |
| The basis is exactly ten tensors `T(1)...T(10)` and five invariants `λ1...λ5`, listed in the paper's Eq. 2, with `λ1 = Tr(S²)`, `λ2 = Tr(R²)`, `λ3 = Tr(S³)`, `λ4 = Tr(R²S)`, `λ5 = Tr(R²S²)`. Finiteness comes from Cayley–Hamilton: "higher order products of these two tensors can be reduced to a linear combination of this tensor basis". | Same, section II.B, Eq. 2. | Building the tensor and invariant input layers. This is the exact same basis SpaRTA uses (section 2 below), so the two rungs share a feature pipeline. | For a **two-dimensional** flow the basis degenerates. Ling states it obliquely — on the wavy-wall test case "b13 and b23 are not shown because they are identically zero in this 2-D test case." SpaRTA states the reduction explicitly and uses three tensors and two invariants. Do not build a ten-tensor pipeline for a 2-D case and expect ten independent columns. |
| Network size, stated exactly. TBNN: "the number of hidden layers was set to 8, with 30 nodes per hidden layer. The learning rate was 2.5e-7." MLP baseline: "10 hidden layers, each with 10 nodes, and the learning rate was 2.5e-6." Activation is leaky ReLU throughout. Hyper-parameters were chosen by Bayesian optimisation using the Spearmint package, scored on a **separate validation flow**. | Same, sections II, II.A, II.B. | Sizing a TBNN reproduction. These are small networks — 8×30 is CPU-scale, no GPU implied. | The learning rates are tied to their normalisation and their optimiser. TBNN used **stochastic** gradient descent, one point at a time, "to facilitate the implementation of a multiplicative layer"; the MLP used mini-batch. A modern autodiff framework backpropagates through a multiplicative layer without difficulty, so this constraint is an artefact of their 2016 implementation, not a requirement. |
| Inputs are RANS-derived, outputs are high-fidelity: "The RANS data, obtained using the k−ε model with a Linear Eddy Viscosity Model for the Reynolds stresses, were used as the inputs to the neural networks. The high fidelity data were used to provide the truth labels for the Reynolds stress anisotropy". Output is `b_ij = u'_i u'_j / 2k − (1/3)δ_ij`. | Same, sections II and III. | The feature/label contract. Note the base model is **k−ε**, not k−ω SST. | The closure-challenge benchmark ships k−ω SST baselines, not k−ε. A reproduction on benchmark data changes the base model, and the invariants are non-dimensionalised by k and ε — a k−ω SST port must form ε from `β* k ω` or work in ω directly. The paper does not cover that substitution. |
| Nine flows, named and split. **Training (6):** duct flow at `Re_b = 3500`; channel flow at `Re_τ = 590`; a perpendicular jet in crossflow; an inclined jet in crossflow; flow around a square cylinder; flow through a converging–diverging channel. **Validation (1):** wall-mounted cube in crossflow at bulk `Re = 5000`. **Test (2):** duct flow at `Re_b = 2000` and flow over a wavy wall at `Re = 6850`. | Same, section III. | The experiment design that is worth copying: hold out one flow for hyper-parameters and two for reporting, and make one held-out case a **Reynolds-number** extrapolation of a training flow and the other a **geometry** extrapolation. That is precisely the closure challenge's own stated design philosophy. | **None of these nine datasets is in this repo.** See the omission below. |
| The only quantitative result is a priori RMSE on `b`, Table I: duct — LEVM 0.23, QEVM 0.18, **TBNN 0.13**, MLP 0.33; wavy wall — LEVM 0.18, QEVM 0.11, **TBNN 0.08**, MLP 0.09. Stated in words: TBNN is "43% more accurate than the LEVM and 28% more accurate than the QEVM" on the duct, and gives "a 56% reduction in error with respect to LEVM and a 27% reduction in error with respect to QEVM" on the wavy wall. | Same, section IV.A, Table I. | The numbers a reproduction would have to hit. They are RMSE on the anisotropy tensor, a priori, on the two test flows. | They are **not** velocity errors and **not** benchmark scores. Table I is the paper's only table. |
| Embedding invariance is what buys the accuracy, and the paper's own control proves it: the MLP, given the nine raw components of S and R and nothing else, scores **0.33** on the duct — worse than the LEVM's 0.23. "The MLP, on the other hand, completely fails to predict the anisotropy in this configuration." | Same, section IV.A and Table I. | The justification for paying the architectural cost. An un-constrained network on the same data is worse than the linear model it is meant to replace. | The MLP is a deliberately weak control (9 raw components, no invariants, 10×10). It is not evidence against feature-engineered scalar-invariant networks generally. |
| A posteriori propagation is a solver modification in two places: the predicted `b` was "implemented in an in-house RANS solver, SIERRA Fuego, in the momentum equations and in the turbulent kinetic energy production term." The paper also runs a **DNS-b** control — true DNS anisotropy in the same solver — which "represents the upper performance limit of an improved Reynolds stress anisotropy model." | Same, section IV.B. | The DNS-b control is the single most transferable idea in the paper for this lab: it separates the closure error you are attacking from the k and ε transport-equation error you are not. Any propagation study here should run it. | Fuego is not available. The modification must be rebuilt in OpenFOAM. |
| The a posteriori result is **honest and partial**. On the duct, "The TBNN, on the other hand, over-predicts the strength of these vortices, with incorrect counter-rotating vortices forming near the center of the channel." On the wavy wall, "TBNN predicts flow separation, though in a smaller region than the DNS." The DNS-b control itself "slightly over-predicts the strength of the corner vortices". | Same, section IV.B, Figs. 6 and 7. | Calibrating expectations. Best-case anisotropy does not give best-case velocity, because k and ε are still modelled. | These are qualitative readings of contour and vector plots. No a posteriori error number is published — see below. |
| The authors state their own uncertainty position: "the TBNN needs to be trained and tested across a much broader set of flows… testing across more flows will enable uncertainty analysis for the TBNN predictions." | Same, section V. | Read as: **no uncertainty analysis was performed.** A reproduction claiming error bars is adding something the paper does not have. | — |

### The omissions, recorded as the findings

**(a) No compute cost is reported anywhere in the paper.** A search of the full text for CPU,
core, hour, wall clock, processor, GPU, training time and node-hour returns nothing but false
positives ("second RANS", "secondary flows"). There is no training time, no core count, no
epoch count, and no cost for the Spearmint Bayesian hyper-parameter search — which, since it
sweeps layers, nodes and learning rate, is plausibly the dominant expense and is the one
number a reader would need most. **A reader cannot budget a TBNN from this paper.** This is
the identical gap this lab recorded against Singh, Medida & Duraisamy and against Cappelli &
Mansour. Three for three in this lineage.

**(b) No training-set size.** The number of data points is never given, for any of the nine
flows or in total. Since the network is trained pointwise, that is the size of the problem.

**(c) No data-access route for any of the nine flows.** Each is given a literature citation
and nothing more. Two of the six training flows — the jets in crossflow (refs 24, 25) and the
square cylinder (refs 26, 27, the latter a Sandia technical report) — are Sandia and Stanford
internal simulations with no public archive named. **The paper's own training database cannot
be assembled from the paper.**

**(d) No mesh-transfer statement.** RANS inputs and DNS labels live on different grids, and the
paper never says how the label field was brought onto the RANS points, or the reverse.

**(e) No a posteriori error metric.** Table I is a priori only. Figures 6 and 7 are contour and
vector plots read in prose. There is no published number for the velocity field that a
propagation reproduction could be scored against.

### Verdict on reproducibility, and the in-sample question

**Ling's published result is not reproducible in this lab, because of (c).** Table I's four
numbers are RMSE against two specific test flows — duct at `Re_b = 2000` (Pinelli et al.) and a
wavy wall at `Re = 6850` — trained on six flows of which at least two have no public archive
named in the paper. This is the documented "nothing directly reproducible here because X"
that the standing permission asks for, and X is the training database, not the method.

**The architecture is reproducible, and the code is public.** Sandia released the reference
implementation at `github.com/sandialabs/tbnn` (BSD-3-Clause), already recorded in
`docs/research/CLOSURE_METHODS.md`. What is missing is data, not method.

**In-sample verdict on the training data a TBNN reproduction here would actually use.**
The only dense per-cell anisotropy labels this lab holds are the closure-challenge benchmark's
own `U_LES`, `k_LES` and `tauij_LES` fields, which ship inside each case directory. Checked
this session against the benchmark clone:

| Benchmark case | Cells | Role in benchmark | Scored? |
| --- | --- | --- | --- |
| `DUCT/AR_1_Ret_180` | 2,209 | suggested training | no |
| `DUCT/AR_3_Ret_180` | 6,627 | suggested training | no |
| `DUCT/AR_5_Ret_180` | 11,045 | suggested training | no |
| `DUCT/AR_10_Ret_180` | 22,090 | suggested training | no |
| `DUCT/AR_7_Ret_180` | 15,463 | suggested validation | no |
| `DUCT/AR_1_Ret_360` | 3,025 | **test** | **yes** |
| `DUCT/AR_3_Ret_360` | 8,748 | **test** | **yes** |
| `DUCT/AR_14_Ret_180` | 31,819 | **test** | **yes** |

The scored list is not retyped here from the README; it is the list
`sdk/scripts/closure_in_sample_gate.py` derives and cross-checks, run this session, which
returned eight scored cases and `PASS` on the current tree.

**The verdict: training a TBNN on `AR_1/3/5/10_Ret_180` with `AR_7_Ret_180` held for
hyper-parameters is out of sample.** Those five are training and validation cases, none is
scored, and the three scored duct cases are never opened. That is a legitimate submission
route under the benchmark's one strict rule.

**And it happens to be Ling's own experiment, transposed.** Ling trained on a duct at
`Re_b = 3500` and tested on a duct at `Re_b = 2000` — a Reynolds-number generalisation within
one geometry family. `AR_1_Ret_360` is the same experiment: the aspect ratio is in the training
set, the Reynolds number is not. `AR_14_Ret_180` is the harder one — `Re_τ = 180` is in the
training set but aspect ratio 14 is outside the trained range of 1 to 10, so it is an
**extrapolation, not an interpolation**, and should be predicted to be the worst of the three.

**One caveat that must not be lost.** The duct is three-dimensional and its secondary flow is
the whole point; all ten of Pope's tensors are live. This is the one place where TBNN is
strictly more expressive than SpaRTA as published, since SpaRTA restricts itself to the 2-D
reduction (section 2). It is also the benchmark family where this lab's deficit to rank two is
largest. Those two facts point the same way.

### Reproduction proposal filed

`w2-tbnn-duct-reynolds-generalisation` on `demo-output/website/agenda/docket.json`. It
reproduces Ling's **architecture and experiment design** on benchmark duct training data, and
states in its own text that it does **not** reproduce Table I, because the data for Table I
cannot be assembled.

---

## 2. Schmelzer, Dwight & Cinnella — SpaRTA

**Schmelzer, M., Dwight, R.P. & Cinnella, P., "Discovery of Algebraic Reynolds-Stress Models
Using Sparse Symbolic Regression," *Flow, Turbulence and Combustion* 104:579–603 (2020), DOI
`10.1007/s10494-019-00089-x`.** **READ IN FULL** — the **published version of record**, fetched
2026-07-31 from the Springer open-access PDF endpoint and held at
`docs/papers/schmelzer_dwight_cinnella_ftac2020_s10494-019-00089-x.pdf` with its text
extraction alongside. Received 2 May 2019, accepted 2 October 2019, published online
17 December 2019.

**Availability checks run, and their answers.** CrossRef on the DOI returns the article under
two `creativecommons.org/licenses/by/4.0` licence records. Unpaywall returns `is_oa: true`,
`oa_status: "hybrid"`, with four locations: the Springer published version, an arXiv
submitted version at `arxiv.org/pdf/1905.07510`, TU Delft, and HAL. **The published version
was taken in preference to the preprint**, so unlike section 1 this reading is of the version
of record and no preprint caveat attaches to it. The article's own text states: "This article
is distributed under the terms of the Creative Commons Attribution 4.0 International License."
**No MIT access required.**

### Claim, source, where it applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| **The load-bearing claim for this lab: SpaRTA's data-extraction step needs no adjoint and no optimiser.** k-corrective-frozen-RANS solves the ω transport equation passively with `Ui`, `k` and `bij` frozen at their high-fidelity values, and takes the residual of the k equation as the correction `R`. "For the cases studied the solver reaches convergence after a few hundred iterations." The authors contrast it directly with field inversion: that "method is built upon a computationally-intensive optimisation problem, whereas k-corrective-frozen-RANS only requires a single equation to be solved." | Schmelzer, Dwight & Cinnella 2020, published version, READ IN FULL, section 2.1. | **This rung is not blocked by the adjoint conditioning problem, because it never forms an adjoint.** Everything in the lab's blocker record about `warpDeriv`, gradient conditioning and the missing closure-relevant inversion case is irrelevant to SpaRTA's step 1. | It is "limited to full-field data". Field inversion works from sparse observations — Singh, Medida & Duraisamy inverted on lift coefficient alone. SpaRTA cannot. The trade is: no optimiser, but you must have `Ui`, `k` and `τij` everywhere. |
| Two additive corrections, not one, and this is the paper's stated novelty: "we identify not only a correction of the stress-strain relation, but also one for the turbulent transport equations". `b_ij = −(ν_t/k) S_ij + b_ij^Δ` (Eq. 3), and `R` enters both transport equations, added to `P_k` in Eq. 4 and carried into the ω equation as `(γ/ν_t)(P_k + R)` in Eq. 5. | Same, section 2.1, Eqs. 3–5. | The exact solver modification a reproduction must make: two source terms in a k-ω SST solver, both read as static fields for the validation step. | The k production is bounded by Menter's limiter, `P_k = min(−2k(b°+b^Δ)∂_j U_i, 10 β* ω k)` (Eq. 6). A reproduction that omits the limiter is not reproducing this. |
| **The headline result is counter-intuitive and is the single most useful thing in the paper: the `R` correction alone is what works.** "for the set of models, only providing a correction for `b_ij^Δ`, not all lead to an improvement of the resulting velocity field. In contrast to that, if only a correction for `R` is deployed, the result is a consistent, substantial improvement across all test cases. Using both a model for `b_ij^Δ` and `R` only provides a minor additional improvement for some cases. For the test case CBFS13700 using both corrections leads to a detrimental effect". | Same, section 5. | Sequencing a reproduction: build the transport-equation correction first, and only then the stress-strain correction. The cheap half of the method carries the result. | Stated for three 2-D separating flows. Nothing here says `R`-only would suffice for the duct's secondary flow, which is an anisotropy phenomenon by construction and which `R` cannot generate. |
| Two of the three selected models have **no** `b^Δ` term at all and one scalar coefficient each: `M_R^(1) = 0.39 T_ij^(1)` (Eq. 22) and `M_R^(3) = 0.93 T_ij^(1)` (Eq. 24). The third is `M_{b^Δ}^(2) = 0.1 T^(1) + 4.09 T^(2)` with `M_R^(2) = 1.39 T^(1)` (Eq. 23). The paper's summary: "To correct the velocity prediction sufficiently only a slight modification of the baseline k-ω SST model is necessary. A model for `R` using a scalar times `T_ij^(1)` is sufficient for the given test cases." | Same, section 5, Eqs. 22–24 and Table 2. | These are three numbers, publishable in a sentence and implementable in an afternoon. They are also the most checkable reproduction target in either paper. | `T^(1)` is `S_ij` scaled by the timescale `τ = 1/ω`, so `R = 2k b^R_ij ∂_j U_i` with `b^R ∝ S` is a production multiplier in disguise. The physical mechanism the authors identify is that positive `R` raises `P_k`, raises eddy viscosity, raises shear stress and shortens the recirculation bubble. |
| Quantitative targets, published. **Table 1** — mean-squared error of the reconstructed field with `b^Δ` and `R` added as static fields, normalised by the baseline: PH10595 `ε(Ui)/ε(Ui°) = 0.00165` and `ε(τij)/ε(τij°) = 0.1495`; CD12600 `0.0229` and `0.4781`; **CBFS13700 `0.22703` and `0.4949`**. **Table 2** — best model normalised velocity error per case, e.g. `M(1)` on PH10595 at `0.17166` and `M(3)` on CBFS13700 at `0.32062`. | Same, sections 2.1 and 5, Tables 1 and 2. | Table 1 is the reproduction gate for step 1 on its own, before any regression is written. It asks only: does your frozen extraction, propagated back through the solver, recover the LES mean flow? | Table 1's PH10595 velocity figure of 0.00165 is three orders below the baseline; CBFS13700's 0.22703 is only a factor of four. The method's own reconstruction quality varies by case by two orders of magnitude, and CBFS is the hard one. |
| **The paper does report its compute cost for the regression, and it is trivial**: "The duration for the model selection step given the number of data points K ∼ 15000 is of the order of a minute on a standard consumer laptop." | Same, section 3.2. | Budgeting the discovery. Elastic net over a 100 × 9 grid of `(λ, ρ)` on a ~48-column library is a laptop-minute. | It prices **only** the model selection step. See the omission below — the cross-validation is not priced, and it is four orders of magnitude larger. |
| The candidate library is fully specified and small. Raw features are the two nonzero invariants `I1 = S_mn S_nm` and `I2 = Ω_mn Ω_nm`; the 16-entry vector `B` of their products is given in full in Eq. 13; each entry multiplies each of three base tensors, giving `|C_Δ| ≈ 48`. A candidate is discarded "if it contains values with a magnitude larger than 10^5". Model selection is elastic net (Eq. 17) over `ρ = [0.01, 0.1, 0.2, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0]` and 100 log-spaced `λ` down to `10^-3 λ_max`; coefficient inference is a separate Ridge regression (Eq. 20) with `0.01 < λ_r < 0.1`. | Same, sections 3.1–3.3, Eqs. 13, 17–20. | Everything needed to rebuild the regression without seeing their code. This is a materially better disclosure posture than Ling's. | The `λ_r` range is empirical and the authors say so plainly: "Our efforts are based on an empirical observation, but do not guarantee a well-behaving numerical setup under all conditions." |
| **Two dimensions only.** "In the following, we only consider two-dimensional flow cases, for which the first three base tensors form a linear independent basis and only the first two invariants are nonzero." Basis is `T^(1) = S`, `T^(2) = SΩ − ΩS`, `T^(3) = S² − (1/3)δ Tr(S²)`. | Same, section 2.2, Eqs. 10–11. | Periodic hills, converging–diverging channel, curved backward-facing step, the NASA hump — the 2-D families. | **The duct is out.** SpaRTA as published cannot represent a duct's secondary flow, which needs the higher tensors. This is the exact complement of TBNN's position in section 1, and it is why the two rungs are not substitutes. |
| Cross-validation is done **in CFD**, not on the training residual, and deliberately: "For the purpose of CFD a true validation of the models can only be performed once they are implemented in a solver and applied to a test case… we select a wide spectrum of models varying in accuracy and complexity… instead of a single one." A model is discarded if it fails to converge. | Same, sections 3.2, 3.3 and 5. | The methodological point worth stealing: a low training residual does not survive contact with a solver, and the paper found that "the best model per test case is not always identified on the associated training data". | It costs what it costs — see the omission. |
| True prediction outside the training range works: the three models applied to periodic hills at `Re = 37000`, against Rapp & Manhart's experiment, "improve significantly compared to the baseline", and "the models `M(2)` and `M(3)` are providing a better fit of the data than `M(1)`, which was performing better on the lower Re case." | Same, section 5, Fig. 13. | Evidence that a model fitted at one Reynolds number transfers up a factor of 3.5 in the same geometry. | Rank order among the models **inverts** between the training Re and the prediction Re. Selecting a model on training-case rank does not select the best extrapolator. |
| Honest negative results are reported. On CD12600 "we observe a small recirculation zone as reported in the literature using `M(1)`, but too far down-stream. However, while the baseline k-ω SST drastically over-predicts this zone, `M(2)` and `M(3)` ignore it entirely." And the paper concedes to its competitors: "using more complex function approximators from the machine learning toolbox, e.g. neural networks or random forest, more details of the flow can be captured, e.g. on the hill's crest of PH10595, which are missed by SpaRTA." | Same, sections 5 and 6. | Reading the ladder honestly: SpaRTA is the cheap, interpretable, robust rung, not the accurate one. | — |
| An acknowledged inconsistency, stated by the authors and not buried: treating `b^Δ` and `R` separately means "energy is not conserved, because Eq. 12 has no corresponding part in the momentum equation". They note others violate it too and that fixing it "improves the predictive performance", but that a joint fit "requires a multi-objective version of the deterministic symbolic regression detailed below, which is beyond the scope of this paper." | Same, section 2.2. | A named, open defect in the published method — the obvious place a reproduction could contribute something rather than only re-measure. | — |

### The omission, recorded as the finding

**The paper prices the cheap step and not the expensive one.** The regression is priced to the
minute. The cross-validation is not priced at all, and the paper states its size in the same
breath: "all models are applied to the three test cases, which requires 61, 48 and 75
simulations for the cases PH10595, CD12600 and CBFS13700 respectively." That is **184 CFD
simulations**, and no wall time, core count or hardware is given for any of them.

This lab can put a number on it, because it has run that exact case on this exact mesh.
Ladder-B rung B2 ran the benchmark's CBFS case, 21,000 cells, k-ω SST, serially on this box:
**1,753.3 s CPU / 1,770 s wall, 29.5 core-minutes**, converged field agreeing with the
benchmark's own shipped baseline to 0.068% scaled MAE. At that rate the CBFS column of the
cross-validation alone is **75 × 29.5 ≈ 2,213 core-minutes, about 37 core-hours**. So the
honest cost profile of SpaRTA is a **one-minute regression wrapped in a thirty-seven-core-hour
validation**, and the paper reports only the minute. Recorded because this lab has just been
burned by a proposal priced off the wrong run.

### The finding that changes what this lab can do next

**SpaRTA's demonstration meshes and this lab's benchmark data are the same objects.** The paper
states the CBFS mesh is "140 × 150 cells" and the periodic-hills mesh "120 × 130 cells". The
closure-challenge clone's `data/CBFS/constant/polyMesh/owner` header reads `nCells: 21000`,
which is 140 × 150 exactly; `data/PH_Breuer` reads `nCells:15600`, which is 120 × 130 exactly.
The benchmark ships SpaRTA's own case setups.

And it ships the training signal. Each case directory carries `0/U_LES`, `0/k_LES` and
`0/tauij_LES` alongside the k-ω SST baseline — precisely the `Ui`, `k` and `τij` full fields
that k-corrective-frozen-RANS consumes, on the same mesh, with no interpolation needed.

**One known blocker, and why it does not bite here.** Rung B2 recorded that CBFS's `0/U_LES`,
`0/k_LES` and `0/tauij_LES` are assembled from `#include`-macro'd dictionaries under
`0/interpolatedFields/`, and that the `Ofpp` Python reader "cannot resolve these macros — it
silently returns `None` rather than erroring". That blocker is specific to the **Python-side**
reader. k-corrective-frozen-RANS runs **inside OpenFOAM**, whose own dictionary parser expands
`#include` natively — the field is read by the solver, not by Ofpp. A SpaRTA step-1
reproduction therefore steps around B2's blocker rather than inheriting it. Any *scoring* or
plotting done in Python afterwards still needs `foamDictionary` or `postProcess` to
pre-resolve, exactly as B2 flagged.

### In-sample verdict on SpaRTA's training data

Checked against the clone's README table and against the derived list from
`sdk/scripts/closure_in_sample_gate.py`, run this session:

| SpaRTA's own case | Available here? | Role in benchmark | Scored? |
| --- | --- | --- | --- |
| PH10595 (Breuer LES) | **yes**, `data/PH_Breuer`, 15,600 cells | training (single variation) | **no** |
| CBFS13700 (Bentaleb LES) | **yes**, `data/CBFS`, 21,000 cells | training (single variation) | **no** |
| CD12600 (Laval & Marquillie DNS) | **no** — not shipped with the benchmark | not in the benchmark | n/a |
| PH37000 (Rapp & Manhart experiment) | **no** — not shipped | not in the benchmark | n/a |

**Verdict: clean. Not in sample, and not marginally so.** Two of SpaRTA's three training cases
are in the tree, and both are cases the benchmark itself designates as *training*. Neither is
one of the eight scored cases. A SpaRTA reproduction on `CBFS` and `PH_Breuer` touches no test
truth at any point, which is a stronger position than the lab's field-inversion line, whose
stated target was blocked partly by this very rule.

**What is missing is the third case, not permission.** A faithful three-case reproduction needs
CD12600, the Laval & Marquillie converging–diverging channel DNS, which the benchmark does not
ship. That is a data-sourcing task, not a leakage question, and it is not on the critical path:
the paper's own cross-validation found that "the data of CD12600 and CBFS13700 provide models,
which are well performing on all test cases", so CBFS alone still yields a transferable model.

### The two rungs are complements, not alternatives

Worth stating because `docs/research/CLOSURE_METHODS.md` currently ranks them against each
other on code-availability grounds, before either had been read:

- **SpaRTA is 2-D by its own restriction and its demonstrated cases are the separated-flow
  family** — periodic hills, curved backward-facing step. In benchmark terms that is the PHLL
  and hump side of the board, and the training data is in the tree.
- **TBNN carries all ten of Pope's tensors and its demonstrated case is a duct** — the 3-D
  secondary-flow family, where this lab's deficit to rank two is largest, and where SpaRTA's
  published ansatz cannot represent the physics at all.

They divide the board. Running both is not redundancy.

### Reproduction proposal filed

`w2-sparta-frozen-rans-cbfs` on `demo-output/website/agenda/docket.json`. It is scoped to
**step 1 only** — k-corrective-frozen-RANS on CBFS13700, propagated back as static fields —
because that step has a published number to hit (Table 1's CBFS row, `0.22703` and `0.4949`),
needs no adjoint, and settles whether the extraction works before 37 core-hours of
cross-validation is committed to.

---

## Papers to add to the W2 seed list, from what these two cite

Named here as **leads only**. Nothing below has been fetched or read, and no claim anywhere in
this lab's records is sourced to any of them.

1. **Pope, S.B., "A more general effective-viscosity hypothesis," *J. Fluid Mech.* 72:331
   (1975).** The ten-tensor integrity basis. **Both** papers rest on it — Ling's Eq. 1–2 and
   SpaRTA's Eq. 9–11 are the same result. It is the only shared foundation of the two rungs and
   the lab has read neither it nor a substitute. Highest priority of this list.
2. **Weatheritt, J. & Sandberg, R.D. (2016, *JCP* 325:22; 2017, *IJHFF* 68).** SpaRTA is
   explicitly built as the deterministic answer to their GEP method, and SpaRTA's
   frozen-RANS is "an extension of the method introduced in" the 2017 paper. Reading SpaRTA
   without them leaves the frozen-RANS lineage sourced second-hand.
3. **Zhao, Y., Akolekar, H.D., Weatheritt, J., Michelassi, V. & Sandberg, R.D.,
   "Turbulence model development using CFD-driven machine learning," arXiv:1902.09075 (2019).**
   SpaRTA names it as the approach that puts CFD *inside* the model search, which "increases
   the costs of the model search drastically" but yields better convergence. That trade is
   exactly the 37-core-hour question above.
4. **Duraisamy, K., Iaccarino, G. & Xiao, H., "Turbulence modeling in the age of data,"
   *Annu. Rev. Fluid Mech.* 51 (2019).** Already on the standing W2 seed list; both papers cite
   it as the field review.
5. **Ling, J., Jones, R. & Templeton, J., *JCP* 318:22 (2016).** Ling's own predecessor, the
   invariant-feature-set result that motivated the TBNN. Cited as ref 18 for the claim that
   embedding invariance is what buys the accuracy.
6. **Breuer, M., Peller, N., Rapp, C. & Manhart, M., *Computers and Fluids* 38(2):433 (2009)**
   and **Bentaleb, Y., Lardeau, S. & Leschziner, M.A., *J. Turbulence* 13(4) (2012).** The
   sources of the LES fields shipped in `data/PH_Breuer` and `data/CBFS`. Reading them is how
   the lab would learn what the shipped truth fields actually are, rather than trusting the
   benchmark's re-packaging of them.
7. **Laval, J.-P. & Marquillie, M. (2011), converging–diverging channel DNS.** The one SpaRTA
   case not in the tree. Reading it is a prerequisite to sourcing the data.

## MIT-access list

**Empty for this session.** Both target papers were fetched by this lab without institutional
access — Ling from the OSTI repository copy of Sandia accepted manuscript SAND2016-7345J, and
SpaRTA as the CC-BY published version of record from Springer. `docs/research/MIT_ACCESS_DOCKET.md`
gains a closed row for SpaRTA and its one open row, Parish & Duraisamy (2016), is unchanged.
