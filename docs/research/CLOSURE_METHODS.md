# ML-closure methods: a living taxonomy, organised by method class

Program M1, Certonomous closure-methods research. Reading and writing only —
no solver run, no compute launched to produce this document. Companion index:
`docs/NUMERICS_KNOWLEDGE.md` (pre-existing file in this repo; every source
cited below gets an indexed entry there under "Reading round M1", mapping
claim → source → the gate/evidence that would test it).

## Citation discipline (read this before trusting any entry below)

Every citation in this document was checked to resolve — via publisher page,
DOI, arXiv ID, or NASA ADS record — before being written down. None was typed
from memory alone. Each entry below is tagged with a verification tier:

- **(a) verified, primary source** — DOI/arXiv/publisher page confirmed to
  resolve, and either the full text was read (by this lab, this session or a
  prior rung — noted explicitly where that happened) or exact
  title/authors/venue/volume/pages were cross-confirmed against the
  publisher's or NASA ADS's own bibliographic record (not just a search
  engine's AI summary).
- **(b) secondary discussion only** — the work is referenced consistently
  across independent sources (e.g., cited in a verified paper's own reference
  list, or described in a review) but I did not resolve a DOI/arXiv ID
  directly, or could not obtain the full text myself.
- **(c) could not establish** — I went looking and could not pin down a
  citation solidly enough to print it. Named as a gap, not guessed.

Nothing in this document is tier (c) dressed up as (a) or (b). Where B1's
prior research rung (`demo-output/website/dafoam/ladder-b/B1_reproduction_plans.md`)
already did primary-source verification (including full-text reads) for a
closure-challenge-adjacent paper, that work is reused and credited rather
than re-done blind.

## Backbone review

**Duraisamy, K., Iaccarino, G., Xiao, H. "Turbulence Modeling in the Age of
Data." *Annual Review of Fluid Mechanics* 51 (2019): 357–377.**
DOI: `10.1146/annurev-fluid-010518-040547`. Open preprint: arXiv:1804.00183.
**Tier (a)** — resolves at Annual Reviews, ADS, and arXiv consistently. This
survey's own organizing spine — field inversion, invariant-embedded
regression, model-form UQ via eigenvalue perturbation, and the general
"correct the model vs. correct the answer" distinction — is the backbone this
taxonomy is built against. Every class below is placed relative to it.

---

## Class 1 — Field inversion + machine learning (FIML lineage)

**Core idea.** Solve an inverse (PDE-constrained, typically adjoint-driven)
problem to find a spatially varying corrective field that makes a RANS
solution match reference data on a set of training flows; then regress that
field against local, RANS-derivable features so the correction can be
predicted a priori on new flows without re-solving the inverse problem.

**What it corrects.** A model coefficient or source term *inside the
equations* — e.g., a multiplicative factor on a destruction term, or an
additive term in the turbulence transport equation. This is the field's
paradigm case of "corrects the model," not "corrects the answer": the learned
quantity re-enters the PDE and the flow is re-solved with it in the loop.

**Invariance properties.** Not automatic — depends on how the corrective
field is featurized before regression. If the regression uses raw,
dimensional, frame-dependent quantities, invariance is absent; the field
generally uses non-dimensional invariants (as in Class 2/3 feature sets) to
carry Galilean and rotational invariance by construction into the *regressor*,
though the underlying field-inversion step itself (the adjoint optimization)
has no invariance requirement — it operates case-by-case in physical
coordinates. Realizability is not automatically guaranteed unless the
correction is bounded by construction (e.g., the β(x) ≤ 4 cap used in Wu,
Zhang & Zhang below).

**Data needs.** Reference field(s) at every training cell/point (DNS, LES, or
dense experimental data — e.g. PIV) for the inverse problem; the downstream
regression needs only the same per-cell data already used for inversion, so
data density requirement is "dense on the training cases, none needed at
inference beyond the RANS solution itself."

**Reproducibility.** Adjoint solvers (DAFoam, SU2) are open source; case data
varies by paper (see entries).

### Entries

1. **Parish, E.J., Duraisamy, K. "A paradigm for data-driven predictive
   modeling using field inversion and machine learning." *Journal of
   Computational Physics* 305 (2016): 758–774.** DOI:
   `10.1016/j.jcp.2015.11.012`. **Tier (a)**, resolves at ScienceDirect and
   ADS. The foundational FIML paper: invert a corrective field through the
   adjoint on a small set of training flows, then learn its dependence on
   local features (a neural network or Gaussian process) so it generalizes
   without re-inverting. Corrects the model's production/destruction term.
   Invariance: not embedded by construction in the original paper: the
   correction is learned directly in the feature space chosen by the authors,
   with no explicit tensor-basis invariance layer. Data: field-inversion
   training requires dense reference data (their demonstration cases use
   synthetic/DNS-like reference fields); code was not independently confirmed
   public in this pass — not searched further because Class 1's public,
   maintained tooling is DAFoam (below), which this lab already runs.

2. **Singh, A.P., Duraisamy, K. "Using field inversion to quantify functional
   errors in turbulence closures." *Physics of Fluids* 28.4 (2016): 045110.**
   DOI: `10.1063/1.4947045`. **Tier (b)** — title/DOI/venue corroborated by
   consistent search-result text and by being cited as the algorithmic source
   in the Wu/Zhang/Zhang submission document B1 read directly; full text not
   independently fetched by this program. Cases reported (channel flow, flat
   plate) per B1's search-result-level check — flagged there as
   search-summary confidence, carried forward at the same tier here.

3. **Singh, A.P., Medida, S., Duraisamy, K. "Machine-Learning-Augmented
   Predictive Modeling of Turbulent Separated Flows over Airfoils." *AIAA
   Journal* 55.7 (2017): 2215–2227.** DOI: `10.2514/1.J055595`. Open preprint:
   arXiv:1608.03990. **Tier (a)** — B1 fetched and read the full 32-page arXiv
   text directly (`demo-output/website/dafoam/ladder-b/B1_reproduction_plans.md`,
   "Rejected/considered-and-set-aside candidates"). Learns a multiplicative
   correction to the SA production term via field inversion + neural network,
   demonstrated on S809-airfoil separated flow (no periodic-hill/duct/hump
   overlap with our benchmark — noted, not claimed otherwise).

4. **Wu, C., Zhang, S., Zhang, Y. "Development of a Generalizable Data-Driven
   Turbulence Model: Conditioned Field Inversion and Symbolic Regression."
   *AIAA Journal* 63.2 (2025): 687–706.** DOI: `10.2514/1.J064416`. Open
   preprint: arXiv:2402.16355. **Tier (a)** — B1 fetched the full 48-page
   arXiv PDF and the authors' own closure-challenge submission description
   document directly. Field-inverts β(x), a multiplicative correction on the
   SST ω-destruction term (bounded β(x) ≤ 4), via DAFoam's discrete adjoint on
   the CBFS training case only, then distills β(x) into a closed-form
   expression over 3 invariant features via symbolic regression (PySR). Scores
   rank 2 on the closure-challenge leaderboard (overall 0.0624), with **zero-
   shot generalization to the two square-duct test cases** — trained on CBFS,
   never seeing duct data, yet scoring 0.0455/0.0399 there. This is the
   paper our own Ladder B is attempting to reproduce (see M2 ordering below):
   B2 reproduced the CBFS baseline field to <1.5% agreement; B3's timed
   adjoint pilot is currently **blocked** on a PETSc `KSP_DIVERGED_NANORINF`
   at GMRES iteration 0, reproduced across four independent configuration
   changes (see `demo-output/website/dafoam/ladder-b/B3_duct_field_inversion.md`).
   **Reproducibility: code is DAFoam (public, MIT-licensed, `github.com/mdolab/dafoam`,
   the same tool this lab already runs); training data (CBFS LES) and test
   data (NASA-hump exp., Xiao PH dataset) are all public**, per B1's direct
   confirmation.

---

## Class 2 — Tensor-basis neural networks (TBNN)

**Core idea.** Represent the Reynolds-stress anisotropy tensor as a linear
combination of a finite integrity basis of tensor invariants (built from the
normalized strain-rate and rotation-rate tensors), with a neural network
predicting only the *scalar coefficients* of that basis from the basis's
scalar invariants. Because the basis itself is complete and frame-invariant
(Pope 1975's tensor-polynomial construction), the predicted anisotropy tensor
inherits Galilean and rotational invariance without the network ever seeing a
raw, frame-dependent quantity.

**What it corrects.** The Reynolds-stress anisotropy tensor directly (a
model-form quantity inside the RANS closure), not a scalar coefficient and
not a post-hoc velocity field.

**Invariance properties.** Galilean invariance: **guaranteed by
construction** (the invariant basis and its scalar coefficients are built
from strain/rotation invariants, which do not depend on the observer's
frame). Rotational invariance: **guaranteed by construction**, same
mechanism. Realizability: **not guaranteed by construction** in the original
formulation — the predicted anisotropy tensor can violate the physical
eigenvalue bounds unless a realizability-enforcing layer is added
post-hoc (a documented, active area of follow-up work, not covered by the
1996 base architecture). Units consistency: the invariants are
non-dimensionalized by a turbulence time/length scale, so the network
operates on dimensionless inputs by construction.

**Data needs.** Per-cell DNS or LES Reynolds-stress fields (the true
anisotropy tensor) plus the RANS-derivable strain/rotation fields, at every
training cell — a dense-field requirement, not a sparse-observation one.

**Reproducibility.** **Code is public**: Sandia National Laboratories
released the official TBNN implementation at `github.com/sandialabs/tbnn`
(BSD-3-Clause), confirmed via the repository's own description ("implements
the Tensor Basis Neural Network (TBNN) as described in Ling et al., Journal
of Fluid Mechanics, 2016"). This is a materially stronger reproducibility
posture than most classes in this taxonomy.

### Entry

**Ling, J., Kurzawski, A., Templeton, J. "Reynolds averaged turbulence
modelling using deep neural networks with embedded invariance." *Journal of
Fluid Mechanics* 807 (2016): 155–166.** DOI confirmed via ADS/OSTI record
(OSTI 1333570); volume/pages cross-confirmed at Cambridge Core. **Tier (a)**.
Demonstrated on duct-flow secondary currents and separated flow over a wavy
wall; the duct-flow demonstration case family is the same physical
configuration (secondary-flow-bearing square/rectangular ducts) as our own
benchmark's DUCT test family, though not confirmed to be the identical mesh
or Reynolds numbers as `AR_1_Ret_360`/`AR_3_Ret_360`/`AR_14_Ret_180` — flagged
as "same family, not confirmed same case" rather than asserted as a direct
overlap.

---

## Class 3 — Symbolic and sparse-regression closures

**Core idea.** Fit an explicit, human-readable algebraic expression for the
Reynolds-stress correction (or the full anisotropy tensor) from a library of
candidate invariant terms, using either sparsity-promoting regression
(elastic net / LASSO-style) or evolutionary symbolic search (gene-expression
programming), rather than a black-box network.

**What it corrects.** The Reynolds-stress anisotropy tensor (SpaRTA) or the
RANS stress–strain relationship directly (GEP) — inside-the-equations
corrections, same spine position as TBNN, but interpretable by construction:
the output is a formula, not a network's weights.

**Invariance properties.** Both entries below build their candidate term
library from the same kind of invariant tensor basis as Class 2 (products of
normalized strain/rotation tensors), so Galilean and rotational invariance
are **guaranteed by construction** through the choice of candidate library,
not learned. Realizability is not automatically guaranteed by either method's
base formulation, though the sparsity/interpretability of the result makes it
easier to inspect and bound post-hoc than a dense network's output. Units
consistency: guaranteed, since the candidate library is built from
non-dimensionalized invariants.

**Data needs.** Per-cell DNS/LES Reynolds-stress (and, for SpaRTA's frozen-
training variant, mean-flow and turbulence-quantity) fields at every training
cell — dense, like Class 2.

**Reproducibility.** SpaRTA's frozen-training code is public:
`github.com/shmlzr/general_earsm.git`, confirmed via search-result text
consistent with the paper's own GitHub link. GEP's original code was not
confirmed public in this pass — searches surfaced consistent descriptions of
its OpenFOAM integration and later CFD-driven extensions, and one search
result states "Richard Sandberg shared OpenFOAM code for comparison of
implementations in related research efforts" (not a standalone public
repository citation) — **tier (b)** on code availability, named as a gap
rather than guessed at.

### Entries

1. **Schmelzer, M., Dwight, R.P., Cinnella, P. "Discovery of Algebraic
   Reynolds-Stress Models Using Sparse Symbolic Regression." *Flow,
   Turbulence and Combustion* 104 (2020): 579–603.** DOI:
   `10.1007/s10494-019-00089-x`. Open preprint: arXiv:1905.07510. **Tier (a)**
   — resolves at Springer, ADS, TU Delft research portal, and arXiv
   consistently. SpaRTA: infers algebraic stress-anisotropy corrections from
   LES/DNS via elastic-net-regularized sparse regression over a tensor-
   polynomial candidate library. Demonstrated and cross-validated on periodic
   hills (Re=10595), a converging–diverging channel, and a curved
   backward-facing step — **periodic hills is the exact case family (though
   not necessarily the exact geometry/Re) of our own 4 PH test cases.**

2. **Weatheritt, J., Sandberg, R. "A novel evolutionary algorithm applied to
   algebraic modifications of the RANS stress-strain relationship." *Journal
   of Computational Physics* 325 (2016): 22–37.** DOI:
   `10.1016/j.jcp.2016.08.015`. **Tier (a)** — resolves at ScienceDirect/ACM
   DL consistently, title/authors/volume/pages cross-confirmed. Gene-
   expression programming applied directly to the stress–strain relationship
   (not a fixed tensor-polynomial library as in SpaRTA — GEP searches the
   space of algebraic expressions itself, a structurally different and more
   open-ended search than SpaRTA's sparse regression over a fixed basis).

---

## Class 4 — SGS/LES neural closures

**Core idea.** Predict the subgrid-scale (SGS) flux or stress directly from
resolved-field features (typically via local convolutional or fully-connected
networks operating on filtered/coarse-grid quantities), trained against the
"true" SGS term computed by filtering a fully resolved DNS field.

**What it corrects.** The subgrid flux — the unclosed term arising from
spatial filtering in LES, structurally distinct from the RANS Reynolds-stress
target of Classes 1–3.

**Invariance properties.** Neither entry below embeds Galilean/rotational
invariance into the network architecture by construction (unlike TBNN); both
rely on the network learning approximate invariance from data, or on the
convolutional/local-stencil architecture giving translation equivariance as a
structural byproduct — translation equivariance, not full Galilean/rotational
invariance, is the property actually built in. Realizability (e.g.,
dissipation sign / energy-transfer direction) is not guaranteed by
construction in either base formulation; a-posteriori numerical stability
when the closure is coupled back into a live LES solve is a known, separately
studied concern for this class (the closure can be accurate a priori and
still destabilize the coupled simulation).

**Data needs.** Filtered DNS fields (both resolved quantities and the exact
SGS term computed from filtering) at every training grid point — a dense-
field requirement, generated from homogeneous isotropic turbulence or
two-dimensional (Kraichnan) turbulence DNS in the entries below.

**Reproducibility.** Maulik et al.'s code is public:
`github.com/Romit-Maulik/ML_2D_Turbulence` (confirmed directly by URL in
search results). Beck et al.'s training pipeline was not confirmed public in
this pass (their DG solver FLEXI is separately open source, but a dedicated
public release of the paper's own training scripts/data was not verified) —
named as unconfirmed rather than assumed.

### Entries

1. **Beck, A., Flad, D., Munz, C.-D. "Deep neural networks for data-driven
   LES closure models." *Journal of Computational Physics* 398 (2019):
   108910.** DOI: `10.1016/j.jcp.2019.108910`. **Tier (a)** — resolves at
   ADS/ScienceDirect. Local-convolution-filter networks predict the "perfect"
   LES closure term (defined including the discretization operator itself,
   not just the continuous SGS term) from coarse-grid quantities, trained on
   decaying homogeneous isotropic turbulence DNS.

2. **Maulik, R., San, O., Rasheed, A., Vedula, P. "Subgrid modelling for
   two-dimensional turbulence using neural networks." *Journal of Fluid
   Mechanics* 858 (2019): 122–144.** DOI confirmed via Cambridge Core.
   **Tier (a)**. Note on authorship: the docket's phrasing "Maulik and San"
   most precisely names the earlier 2-author **Maulik, R., San, O. "A neural
   network approach for the blind deconvolution of turbulent flows." *Journal
   of Fluid Mechanics* 831 (2017): 151–181** (title/venue confirmed at
   Cambridge Core, **tier (a)** on bibliographic resolution, full text not
   read) — a deconvolution-based closure rather than direct flux regression.
   Both are reported here since they represent the same research lineage; the
   4-author 2019 JFM paper is the more directly comparable "predict the
   subgrid source term from resolved features" formulation matched against
   Beck et al. above.

---

## Class 5 — Model-form UQ by construction (eigenvalue/eigenvector perturbation)

**Core idea.** Instead of learning a point correction, perturb the
eigenvalues (anisotropy magnitude/shape, moved toward the limiting states of
the realizable barycentric triangle — one-component, two-component,
isotropic) and/or eigenvectors (orientation) of the modeled Reynolds-stress
tensor within physically realizable bounds, and propagate the perturbed
tensor through the RANS solve to produce an *envelope* of solutions rather
than a single corrected answer.

**What it corrects.** The Reynolds-stress anisotropy tensor's eigenstructure
— but the deliverable is a bound, not a point correction: this is the
taxonomy's one class whose stated purpose is honestly representing model-form
*uncertainty* rather than reducing model-form *error*.

**Invariance properties.** Realizability is **guaranteed by construction** —
this is the class's entire mechanism: perturbations are defined and clipped
within the barycentric realizability map, so the perturbed state cannot leave
the physically admissible set. Galilean and rotational invariance:
**guaranteed by construction**, since eigenvalues/eigenvectors of a properly
transforming tensor perturbed within an invariant map remain frame-
consistent. Units consistency: guaranteed, operating on the normalized
anisotropy tensor.

**Data needs.** **None required at inference time** — this is the
lowest-data-need class in the taxonomy. The perturbation bounds are set by
the realizability geometry itself, not fit to DNS/LES/experimental data
(though calibrating perturbation *magnitude* against data is an available
refinement, not a requirement of the base method). This is the class Xiao et
al.'s Bayesian extension below adds sparse-observation calibration to.

**Reproducibility.** The base method needs no trained model and no external
code release to reproduce — it is a deterministic eigendecomposition-and-
reproject algorithm applicable to any existing converged RANS solution,
implementable directly against fields this lab already has on disk.

### Entries

1. **Emory, M., Larsson, J., Iaccarino, G. "Modeling of structural
   uncertainties in Reynolds-averaged Navier-Stokes closures." *Physics of
   Fluids* 25.11 (2013): 110822.** DOI: `10.1063/1.4824659`. **Tier (a)** —
   resolves at AIP Publishing and ADS. Demonstrated on plane channel flow, a
   secondary-flow-bearing duct, and a transonic-bump shock/boundary-layer
   interaction — **the duct demonstration case is architecturally the same
   flow phenomenon (secondary flows in a non-circular duct) as our own DUCT
   test family**, though not confirmed to be the identical geometry.

2. **Iaccarino, G., Mishra, A.A., Ghili, S. "Eigenspace perturbations for
   uncertainty estimation of single-point turbulence closures." *Physical
   Review Fluids* 2.2 (2017): 024605.** DOI:
   `10.1103/PhysRevFluids.2.024605`. **Tier (a)** — resolves at APS
   Publishing directly. Refines and generalizes the eigenspace-perturbation
   machinery into a systematic single-point-closure uncertainty-estimation
   procedure.

3. **Xiao, H., Wu, J.-L., Wang, J.-X., Sun, R., Roy, C.J. "Quantifying and
   reducing model-form uncertainties in Reynolds-averaged Navier–Stokes
   equations: A data-driven, physics-informed Bayesian approach." *Journal of
   Computational Physics* 324 (2016): 115–136.** DOI:
   `10.1016/j.jcp.2016.05.038`. Open preprint: arXiv:1508.06315. **Tier (a)**
   — resolves at ScienceDirect, arXiv, and OSTI consistently. Sits at the
   Class 5/Class 6 boundary: it takes the eigenvalue-perturbation
   parameterization above as its base representation, then uses **sparse**
   observational data plus a Bayesian update (not a dense per-cell training
   set) to *narrow* the perturbation envelope toward the observed flow — the
   only entry in this taxonomy demonstrating "sparse observations, not a
   full field, sufficient." Placed here rather than in Class 6 because its
   deliverable remains an uncertainty-reduced physical-space representation
   built on the realizable eigenspace, not a general ensemble/hierarchical-
   surrogate architecture.

---

## Class 6 — Hybrids: NN-mean + GP-residual, model mixtures/BMA, sparse variational GPs

This class covers three related but distinct hybrid patterns the docket asked
for together; each gets its own reproducibility/data assessment since they
do not share a common pipeline.

### 6a. Neural-network mean with a Gaussian process on the residual

**Core idea.** Use a neural network (or another deterministic regressor) to
capture the bulk trend of a closure quantity, then place a GP — with its
closed-form posterior mean and variance — on the *residual* the network
leaves behind, so the combined model inherits the network's capacity and the
GP's calibrated epistemic-uncertainty estimate at each prediction point. Deep
kernel learning is the concrete architecture: an NN feature extractor feeds a
GP kernel operating in the learned feature space, rather than the raw input
space.

**What it corrects.** The LES closure term directly (deep-kernel variant
below), inside-the-equations like Class 4, but wrapped with an uncertainty
estimate the pure-network Class-4 methods lack by construction.

**Invariance properties.** Not guaranteed by construction in the entry below
— the deep kernel operates on whatever features the NN extractor is given;
no explicit invariant-basis layer is described. GP variance gives a
*calibration* signal (grows away from training data) that is a different
property from *symmetry* invariance and should not be conflated with it.

**Data needs.** Same dense per-cell requirement as Class 4 (its authors are
drawn from the same LES-closure research group as Beck et al. above).

**Reproducibility:** not independently confirmed public in this pass.

**Entry.** **Wenzel, T., Kurz, M., Beck, A., Santin, G., Haasdonk, B.
"Structured Deep Kernel Networks for Data-Driven Closure Terms of Turbulent
Flows." In *Large-Scale Scientific Computing* (LSSC 2021), Springer, 2022,
pp. 410–418.** DOI: `10.1007/978-3-030-97549-4_47`. Open preprint:
arXiv:2103.13655. **Tier (a)** — resolves at Springer, ACM DL, and ADS
consistently.

### 6b. Multi-model mixtures and Bayesian model averaging across closures

**Core idea.** Run several distinct turbulence-model formulations (or the
same model with several distinct calibrated coefficient sets) across several
calibration flow scenarios; combine their predictions via a Bayesian
posterior weighting (Bayesian Model-Scenario Averaging, BMSA) or a space-
dependent local-weight mixture, rather than trusting any one model/scenario
pairing everywhere.

**What it corrects.** Neither a field nor a single coefficient set — the
*ensemble weighting itself* is the learned object; the underlying models
remain unmodified equation sets, so this is squarely "corrects the model" in
the coarsest possible sense: which model to trust, where.

**Invariance properties.** Inherited entirely from whichever base RANS
closures are in the mixture — the averaging step itself introduces no new
frame-dependence, since it operates on scalar weights over already-frame-
consistent model outputs.

**Data needs.** Requires labeled calibration data (experimental boundary-
layer profiles in the entries below) at each calibration scenario, but *not*
dense per-cell fields — sparser than Classes 1–4, comparable in spirit to
Class 5's Bayesian-refinement entry above.

**Reproducibility.** Not independently confirmed public in this pass.

**Entries.**
1. **Edeling, W.N., Cinnella, P., Dwight, R.P., Bijl, H. "Bayesian estimates
   of parameter variability in the k−ε turbulence model." *Journal of
   Computational Physics* 258 (2014): 73–94.** DOI:
   `10.1016/j.jcp.2013.10.027`. **Tier (a)** — title/venue/volume/pages
   cross-confirmed via Semantic Scholar and ResearchGate records citing the
   ScienceDirect original; 13 separate Bayesian calibrations against measured
   boundary-layer profiles at different pressure gradients.
2. **Edeling, W.N., Cinnella, P., Dwight, R.P. "Predictive RANS simulations
   via Bayesian Model-Scenario Averaging." *Journal of Computational Physics*
   275 (2014): 65–91.** DOI: `10.1016/j.jcp.2014.06.046`. **Tier (a)** —
   consistent bibliographic record across ScienceDirect and Semantic
   Scholar. Combines multiple closure models and multiple calibration
   scenarios into one posterior-weighted predictive mixture with propagated
   uncertainty bounds.

### 6c. Sparse variational Gaussian processes as an uncertainty backbone

**Core idea.** Approximate an otherwise-intractable-at-scale GP posterior
with a small set of inducing points, optimizing a variational lower bound on
the marginal likelihood (Titsias) that can further be made stochastic and
mini-batchable for genuinely large datasets (Hensman et al.), so the GP's
calibrated mean+variance structure survives contact with per-cell-scale CFD
data volumes.

**What it corrects.** Not a fixed target on its own — this is
infrastructure, not a closure form. In the entry directly relevant to this
lab, it is applied as the closure mechanism itself for under-resolved 2-D
flow, targeting the truncation/discretization error left by coarse
resolution (a distinct target from the RANS-anisotropy or LES-SGS targets of
Classes 1–4).

**Invariance properties.** Whatever the chosen kernel and mean function
provide — not automatic; the GP machinery itself contributes calibrated
posterior variance, not symmetry invariance.

**Data needs.** The inducing-point/variational machinery exists specifically
to relax the "dense at every cell" requirement of a naive GP — sparse
inducing points summarize the training set, so this class scales toward
sparser data regimes better than a literal per-cell GP would, though it is
still typically trained on the same dense fields Classes 2–4 use, just fit
more cheaply.

**Reproducibility.** The two foundational method papers (Titsias; Hensman et
al.) are widely reimplemented in mature open-source GP libraries; not itself
a turbulence-specific code release.

**Entries.**
1. **Titsias, M. "Variational Learning of Inducing Variables in Sparse
   Gaussian Processes." *Proceedings of AISTATS 2009*, PMLR 5: 567–574.**
   **Tier (a)** — resolves directly at PMLR.
2. **Hensman, J., Fusi, N., Lawrence, N.D. "Gaussian Processes for Big
   Data." *Proceedings of UAI 2013*.** arXiv:1309.6835. **Tier (a)** —
   resolves at arXiv and is independently listed at Microsoft Research and
   Lancaster University's research repository.
3. **Mouzahir, S. (this project's own line of work) et al. "Sparse and Deep
   Gaussian Processes closure for 2-D fluids and ocean flows." MIT, OSM26.**
   **Tier (a)** — already present in this repo at
   `docs/papers/Mouzahir_et_all_OSM26_Sparse_GP_Closure.pdf` and already read
   and indexed in `docs/NUMERICS_KNOWLEDGE.md` ("Sparse Gaussian Processes
   closure ... targeting the truncation and discretisation error left by
   coarse resolution"). This is the direct, in-house representative of Class
   6c and the most immediately actionable Class-6 entry for this lab, since
   it is already read, already local, and already understood by the project
   owner.

---

## Class 7 — Generative and operator classes: honest assessment for closure use

The docket explicitly asked for a documented "not yet suitable because X"
verdict where warranted rather than padding this class to look ready. Having
searched specifically for closure-embedded (not merely surrogate/generative)
uses of both sub-classes, that verdict applies to both, with the specific
reasoning below.

### 7a. Diffusion / score-based generative models for turbulence fields

**What was found.** An active 2023–2026 literature exists — conditional
diffusion models for spatiotemporal turbulence generation, denoising
diffusion probabilistic models for airfoil-flow surrogate uncertainty
(published *AIAA Journal*, 2024, per search results), conditional flow
matching for near-wall turbulence generation, spectrally decomposed diffusion
models for "generative turbulence recovery," and diffusion models combined
with Fourier neural operators for autoregressive 3-D turbulence prediction.
**None of these were verified, in this pass, to be embedded as a corrective
term inside a RANS or LES equation set the way every entry in Classes 1–6
is** — every one found is a *field-generation or super-resolution surrogate*:
given some conditioning (a coarse field, a boundary condition, a flow
parameter), generate a plausible fine-scale field, evaluated against
generative-modeling metrics (spectral fidelity, distributional match) rather
than against a coupled-solver accuracy/stability gate.

**Verdict: not yet suitable for equation-embedded closure use, and the
specific gap is structural, not a maturity question that will resolve with
more papers.** A diffusion/score model's native operation is sampling a
plausible field consistent with a learned data distribution; it has no
built-in mechanism for guaranteeing the sampled correction, fed back into a
solver's source term, leaves conservation laws or realizability intact, and
none of the entries found in this search attach such a guarantee. This is a
different failure mode from "insufficient data" or "hasn't been tried" — it
is that the object this method class naturally produces (a sample from a
learned distribution) is not the object a closure needs (a term that
provably composes with a conservation law). This does not mean the class is
useless to this lab: it is a plausible fit for **super-resolution of sparse
experimental data into a training field for one of Classes 1–4**, which is a
data-preparation role, not a closure role, and should be labeled as such if
pursued.

**Reproducibility.** Not assessed further given the above verdict — no
individual paper was selected as a representative to check code/data
availability for, since none clears the closure bar this taxonomy is
organized around.

### 7b. Neural operators (Fourier Neural Operator, DeepONet)

**What was found.** The foundational method (Li et al., "Fourier Neural
Operator for Parametric Partial Differential Equations," ICLR 2021) is
widely applied as a fast *surrogate solver* for LES-scale turbulence
(large-eddy-simulation acceleration, long-horizon 3-D turbulence prediction),
not as a closure term inside an existing solver. The most directly relevant,
recent, and best-verified data point found is:

**Dehtyriov, D., MacArt, J.F., Sirignano, J. "Deep Learning-based Algebraic
Reynolds Stress Closures for RANS Simulations of Turbulent Flows."**
arXiv:2605.26358 (May 2026; revised June 2026). **Tier (a)** — resolves
directly at arXiv, full metadata fetched and confirmed. This paper explicitly
benchmarks DeepONet (and PINN-style residual learners) *against* a
physics-structured closure (their own DARSM, which embeds an algebraic
Reynolds-stress equation form directly rather than learning a free-form
operator) on **canonical square-duct and periodic-hill benchmarks — the same
flow families as our own DUCT and PH test cases** — and reports that DARSM
outperforms DeepONet and four other established ML baselines, with the
paper's own framing being that operator surrogates "avoid the PDE solver
entirely, forgoing the conservation, boundary condition, and coupling
structure it enforces" (search-summary-level paraphrase of the abstract's
framing, not a verbatim quote fetched from the full text — **tier (b)** on
this specific mechanistic explanation, tier (a) on the paper's existence,
authorship, and benchmark result itself).

**Verdict: not yet suitable as a general-purpose closure mechanism, for a
reason with the same shape as 7a's — a neural operator's native operation is
learning a map between full input and output *fields*, which is a surrogate-
solver role, not a term-inside-an-equation role.** Where a neural operator is
wrapped with enough physics-derived structure to produce a local, composable
correction (as DARSM does, by construction, rather than as a free operator),
it stops being "just" a neural operator and becomes closer to a Class 2/3
architecture with a neural-operator-flavored backbone. The pure operator-
surrogate form is better understood as a competing paradigm to RANS/LES
itself (replace the solve, don't correct it) than as a closure-method-class
member, and the one head-to-head, same-flow-family comparison found in this
search says it currently loses to physics-structured alternatives on exactly
our benchmark's flow families.

**Reproducibility.** Not assessed further, same reasoning as 7a.

---

## Where Certonomous sits in this taxonomy

Our closure-challenge entry
(`sdk/scripts/train_closure_periodic_hill_correction.py`,
`demo-output/website/closure_challenge_trained_entry.json`) predicts a
**post-hoc velocity-field correction**: target
`delta_U = U_LES - U_RANS` per mesh cell, from 7 per-cell features (Pope's 5
scalar invariants `I1..I5` of the (k/ε)-normalized strain-rate and rotation-
rate tensors, a wall-distance-based turbulent Reynolds number `Re_y =
sqrt(k)*walldist/(50*nu)`, and a turbulent/mean kinetic-energy ratio
`k/(k+0.5|U|^2)`), via three `HistGradientBoostingRegressor` models, one per
velocity component.

**This places us outside every class described above.** Classes 1–6 all
correct something that re-enters the governing equations before the flow is
(re-)solved — a source term, a coefficient, an anisotropy tensor, an
ensemble weight. Our correction is applied to an **already-converged RANS
velocity field, once, as a final post-processing step**. The corrected field
is not a solution of any PDE; nothing about our pipeline re-solves continuity
or momentum with the correction folded in. In the Duraisamy–Iaccarino–Xiao
backbone review's own vocabulary, this is the "correct the answer" family,
structurally distinct from every "correct the model" class this document
organizes.

**Structural consequences, stated explicitly:**

- **Galilean invariance: not guaranteed by construction.** The five Pope
  invariants and the two scalar ratios are themselves frame-invariant, so the
  *inputs* to our gradient-boosted trees carry the property — but
  `HistGradientBoostingRegressor` is an axis-aligned decision-tree ensemble
  with no architectural mechanism analogous to TBNN's tensor-basis
  multiplicative layer that would propagate that input invariance into a
  guaranteed *output* invariance. Any invariance the output empirically shows
  is learned, not structural.
- **Rotational invariance: same status — not guaranteed by construction**,
  for the same reason (invariant inputs, non-invariance-preserving
  regressor).
- **Realizability: not applicable/not guaranteed.** We correct a velocity
  field directly, not the Reynolds-stress tensor, so the anisotropy-
  realizability constraint that Classes 2, 3, and 5 build around does not
  even have a natural home in our formulation — there is no tensor whose
  eigenvalues we could check.
- **Units consistency:** maintained (our target and features are both
  dimensionally consistent, non-dimensional invariants plus a physical
  velocity correction), but this is bookkeeping, not an invariance guarantee.

**What this structurally predicts about transfer to unseen geometries**: a
class with no invariance guarantees built into the regressor, trained on
one flow family (periodic hills), has no structural reason to transfer its
corrective behavior to a geometrically different family (square ducts, the
NASA hump) — any transfer that occurs is an empirical accident of the
training distribution overlapping the test distribution in feature space,
not a property the architecture earns.

**Our measured behaviour is consistent with exactly this prediction.**
`demo-output/website/closure_challenge_C2_error_decomposition.md` documents
that our correction **hurts** on three of eight test cases — precisely the
three whose uncorrected RANS baseline was already the most accurate
(`alpha_05_4071_4048`, floor 0.0461, our entry 0.0723, +56.8% worse;
`alpha_05_4071_2024`, floor 0.0719, our entry 0.0974, +35.5% worse; and
`NASA_2DWMH`, a marginal +1.8% worse) — and **helps most** where the baseline
was worst (`alpha_15_13929_4048`: −62.0%; `alpha_15_13929_2024`: −50.7%).
Pearson r between the RANS-floor error and our correction's delta across the
five periodic-hill-model cases is −0.9418 (n=5, stated as suggestive, not
established, in the source document).

**Is this a fundamental property of the class, or a fixable artefact of our
implementation? Assessed honestly: both, in different measures.**

- **Fundamental to the class:** a post-hoc field correction with no
  invariance guarantee has no mechanism to *know* it is being asked to
  extrapolate outside its training distribution — it will produce a
  correction of similar magnitude to its training regime regardless of
  whether the input features are in-distribution, because nothing in a
  gradient-boosted-tree regressor is architected to attenuate its own output
  as inputs move away from training support (unlike, say, a GP, whose
  posterior variance grows explicitly with distance from training data —
  Class 6c's structural advantage, stated plainly as a comparison). This
  "helps where broken, hurts where fine" pattern is exactly what a
  distribution-blind corrector predicts when the correction's magnitude does
  not scale down as the thing being corrected shrinks.
- **Fixable in our implementation, specifically:** the C2 document's own
  proposed remedy — a test-blind, training/validation-only in-distribution
  gate that declines to apply the correction where input features fall
  outside the training support — is a bolt-on fix that does not require
  changing the method class, only adding the kind of distributional
  awareness a GP would supply natively. The C2 document is explicit that this
  must be validated on training/validation cases only, never against test
  scores, to avoid leakage; whether such a gate actually separates the
  regimes cleanly is stated there as unresolved, not yet attempted.

The honest bottom line: **the class's blindness to its own extrapolation is
structural and would recur on any new geometry unless a domain/trust gate is
added; but a domain/trust gate is a known, implementable, test-blind fix that
does not require abandoning the class**, and the diagnostic in C2 (a clean,
if small-n, separation between "floor error ≤ 0.07 → hurts" and "floor error
≥ 0.13 → helps") suggests such a gate is buildable.

---

## Knowledge index

Every source cited above is indexed in `docs/NUMERICS_KNOWLEDGE.md` under
"Reading round M1 — closure methods taxonomy" (added by this program), in the
claim → source → gate/evidence format that file already uses.

---

## M2 reproduction ordering

**Ranking basis**: (a) public reproducibility (code public? data public?
does our stack already run the tool?) and (b) expected transfer to the
challenge's three flow families — periodic hills, square ducts, NASA
wall-mounted hump — weighted toward families where this lab's own measured
deficit is largest (the square ducts: B1/C2 found `AR_1_Ret_360` and
`AR_3_Ret_360` are 62.9% combined of our deficit to the rank-2 leaderboard
entry).

**Already ordered and running, not re-ranked**: **Class 1 (FIML) on the NASA
hump is campaign family F6a** — the RANS baseline gate is done and passed
(`demo-output/website/dafoam/f6a_nasa_hump/F6a_nasa_hump.md`; separation
within 1.6% of NASA's experiment, matching NASA's own SST solution to 0.06%,
correctly reproducing the textbook +14% reattachment over-prediction the
closure literally exists to fix). **Class 1 (FIML) on the square duct is
Ladder B3, currently blocked** on `PETSc KSP_DIVERGED_NANORINF` at the first
GMRES iteration, reproduced across four independent configuration changes,
with the underlying paper (Wu, Zhang & Zhang) and tool (DAFoam) both
independently verified public and already running on our stack. Everything
below is ranked *against* these two anchors, not in place of them.

| Rank | Class | Representative | Public repro. | Expected transfer (PH / duct / hump) | Why here |
|---|---|---|---|---|---|
| — | 1 (FIML) | Wu, Zhang & Zhang / DAFoam | Code+data public, our stack | Duct: zero-shot verified by the paper itself (0.0455/0.0399); hump: also field-inverted in the lineage | **Already the campaign's top pick — F6a running, B3 blocked, not re-ranked.** |
| 1 | 5 (eigenvalue perturbation) | Emory/Larsson/Iaccarino + Iaccarino/Mishra/Ghili | **No trained model, no external code needed** — a deterministic eigendecomposition-and-reproject on RANS fields we already have converged, for all three families (PH, DUCT, hump all already have converged RANS baselines on disk) | Direct: the duct demonstration case in Emory et al. 2013 is architecturally our own DUCT family; a UQ *envelope*, not a point correction, is the right first move on a benchmark where we've now measured that a point correction actively hurts 3/8 cases | **Cheapest possible next step**: zero new training data, zero new adjoint infrastructure, immediately applicable to fields already computed this program (F6a's hump, B2's duct baseline, and our own PH cases). Delivers an honest uncertainty band rather than competing on the point-accuracy metric where we are structurally disadvantaged (see "Where Certonomous sits," above). |
| 2 | 6c (sparse variational GP) | Mouzahir & Lermusiaux (in-house) | Method papers (Titsias; Hensman et al.) have mature open-source implementations (GPflow, GPyTorch); the specific closure paper is already local and already read | Not yet demonstrated on this benchmark's specific families, but the paper's own target (truncation/discretization error under coarse resolution) is a close conceptual match to the periodic-hill and duct under-resolution regime | Directly actionable **because it is already in-house and already understood by the project owner** — the natural second move given rank 1's finding that we need an uncertainty-aware corrector, and this class's posterior-variance mechanism is the structural fix C2 flagged as missing from our current point-estimator. |
| 3 | 2 (TBNN) | Ling, Kurzawski, Templeton + `sandialabs/tbnn` | **Code public (Sandia, BSD-3-Clause)** — the strongest code-reproducibility posture of any trained-model class in this taxonomy | Duct-flow secondary currents is the paper's own demonstration case (same phenomenon as our DUCT family, geometry not confirmed identical); no confirmed hump/PH overlap | Ranked above other trained-model classes on code-reproducibility grounds alone, but below ranks 1–2 because it needs dense per-cell DNS/LES anisotropy-tensor training data we have not yet sourced for our specific duct cases, and requires a from-scratch training pipeline this lab hasn't built. |
| 4 | 3 (SpaRTA / symbolic regression) | Schmelzer, Dwight, Cinnella + `shmlzr/general_earsm` | Code public; periodic hills is a demonstrated training family | PH: direct family match; duct/hump: not demonstrated by the base paper | Below TBNN because SpaRTA's own demonstrated case set does not include the duct family where our deficit is largest, even though its PH overlap is arguably tighter than TBNN's. |
| 5 | 4 (SGS/LES neural closures) | Maulik, San, Rasheed, Vedula + `Romit-Maulik/ML_2D_Turbulence` | Code public | **Poor fit**: this is an LES subgrid-flux closure; our benchmark is RANS-only (periodic hills, ducts, hump are all RANS test cases in this challenge) | Ranked last among the reproducible classes specifically because the target quantity (SGS flux) does not exist in our benchmark's RANS-only evaluation — included for completeness of the ranking, not as a near-term pick. |
| — | 6a/6b (deep-kernel hybrid; BMA) | Wenzel et al.; Edeling/Cinnella/Dwight | Not confirmed public in this pass | Plausible but undemonstrated on our families | **Not ranked for near-term pursuit** — reproducibility unconfirmed, so the honest move is to say so rather than rank speculatively. |
| — | 7 (generative/operator) | — | N/A | N/A | **Not ranked at all**, per the Class 7 verdict above: the one same-family, same-flow, head-to-head comparison found (DARSM vs. DeepONet on square-duct and periodic-hill benchmarks) says the pure operator-surrogate form currently loses to physics-structured alternatives on exactly our flow families. Revisit if a future entry embeds enough physics structure to stop being "just" a generative/operator model. |

**One-line summary of the M2 logic**: don't compete on point-accuracy against
a structurally advantaged class (FIML, already running/blocked) with a
structurally disadvantaged one (our post-hoc corrector); instead, the
cheapest next real step is a zero-training-data uncertainty envelope
(eigenvalue perturbation) on fields we already have, followed by adopting the
in-house SVGP line of work to give our own future correction the
distribution-awareness this program's own error decomposition shows we are
currently missing.
