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
