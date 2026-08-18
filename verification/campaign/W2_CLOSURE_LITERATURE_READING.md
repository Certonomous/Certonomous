# W2 reading well - the data-driven closure lineage, read for reproduction

Date opened: 2026-07-30 (UTC). **Zero-compute task**: fetch, read, index, propose. No solver
was launched to produce this document, and none of the costs quoted below were measured by
this session.

**Scope.** The standing seed list for well W2: the field-inversion and machine-learning
lineage behind roadmap item 4A Stage 1, the tensor-basis network, sparse symbolic regression
for closure, the method at rank 2 on the closure challenge board, the age-of-data review,
subgrid-scale modelling, and eigenvalue perturbation.

**Provenance discipline** per `docs/charters/LITERATURE_CHARTER.md` section 2. Every source
below carries one of three tiers: **READ IN FULL** (full text fetched and read this session),
**PAYWALLED** (only what a metadata artifact or public abstract literally states), or
**INTERNAL** (a prior session in this lab read the full text and our own record holds the
extraction). Availability checks are reported with their actual answers, never assumed.
Papers that could not be fetched are on `docs/research/MIT_ACCESS_DOCKET.md` and nothing is
asserted about their contents.

**An omission is a finding.** Where a paper withholds a quantity needed to rebuild its result,
the omission is recorded as the outcome of the reading, not smoothed over and not filled in
from a similar paper.

---

## 0. The highest-priority paper, and why it is not below

**Parish, E.J. & Duraisamy, K., "A paradigm for data-driven predictive modeling using field
inversion and machine learning," *Journal of Computational Physics* 305:758-774 (2016), DOI
`10.1016/j.jcp.2015.11.012`.** **PAYWALLED.** Unpaywall returns `is_oa: false`; OpenAlex
returns `oa_status: "closed"` with `any_repository_has_fulltext: false`; the one
accepted-manuscript URL Semantic Scholar advertises as bronze OA returns HTTP 403; arXiv full
text search returns no preprint of it. All four checks were run 2026-07-30 and are logged in
full on the MIT-access docket.

**Nothing in this document is attributed to Parish & Duraisamy.** The FIML requirement
question the well was opened to answer is answered in section 3 below from two papers in the
same lineage that were read in full, and every number there carries the paper that states it.

---

## 1. Singh, Medida & Duraisamy - FIML on airfoils

**Singh, A.P., Medida, S. & Duraisamy, K., "Machine Learning-augmented Predictive Modeling of
Turbulent Separated Flows over Airfoils," arXiv:1608.03990v3 (dated 6 Nov 2016, cs.CE).**
**READ IN FULL** - PDF fetched from arXiv 2026-07-30, saved to
`docs/papers/singh_medida_duraisamy_1608.03990.pdf`, text extracted alongside it.
**Preprint, labelled as such.** Duraisamy is an author, so this is the FIML method applied by
its own originating group; it is not a third party's characterisation of Parish & Duraisamy.

### Claim, source, where it applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The inverse problem's dimension equals the mesh: "an optimal value of `beta` is sought at every discrete location in the computational domain", and "the number of parameters equals the number of control volumes `Nm`". | Singh, Medida & Duraisamy 2016, arXiv preprint, READ IN FULL, section III and Appendix A. | Any field inversion where the correction is a per-cell multiplier. This is the sizing rule for the design-variable count in 4A Stage 1. | It does not size the *application* mesh. The trained model is queried pointwise and carries no such dimension. |
| The correction enters as a multiplier on the SA production term, `Dv/Dt = beta(x) P - D + T`, and the authors state plainly that this "changes the entire balance of the model, (and need not be interpreted as merely a modification of the production term)", being equivalent to a source `delta(x) = (beta(x)-1) P(x)`. Inferring `beta` rather than `delta` is chosen because "`beta` is non-dimensional and has a simple initial value of unity", giving a better conditioned inverse problem. | Same, section III, Eq. 2. | Choosing the parameterisation for our own inversion: prefer a non-dimensional multiplier with prior 1 over an additive source. | It is stated for Spalart-Allmaras. The paper says the methodology "is applicable to both eddy viscosity and Reynolds stress models" but restricts its own work to SA. |
| An adjoint is *required*, not merely convenient: "Since the optimization problem is extremely high dimensional (as the number of parameters equals the number of control volumes `Nm`), an adjoint approach is required to efficiently compute gradients." The optimiser is quasi-Newton L-BFGS. | Same, Appendix A. | The adjoint capability gate for 4A Stage 1. Finite differences are ruled out by the authors themselves on dimensional grounds. | It does not say which adjoint implementation. Their Jacobians come from the Tapenade automatic-differentiation tool and the adjoint system is solved by pseudo time stepping. |
| The adjoint must reach *inside* the turbulence model. The gradient reduces to `dJ/dbeta = dJ/dbeta - psi_v P`, where `psi_v` "represents the adjoint variable corresponding to the working variable of the SA model". | Same, Appendix A, Eq. 12. | Our adjoint must differentiate the turbulence transport equation, not treat eddy viscosity as frozen. | A frozen-turbulence adjoint cannot produce this gradient at all. This is a hard capability requirement, not an accuracy refinement. |
| Field inversion succeeds on a *scalar integrated* observation. The inversions in this work use lift coefficient alone, Eq. 5, because "in the majority of experimental tests of flow over airfoils, the surface pressure is not measured". Lift-based and pressure-based inversion "were confirmed to lead to a similar solution", with near-wall `beta` features "almost identical". | Same, section III. | Cases where we have an integrated force but no field data. This substantially widens what the lab can invert against. | The agreement is stated for these airfoils, and the authors themselves flag "discrepancies in the post-stall region". |
| Tikhonov regularisation weight: "The entire set of inverse problems in this work is solved for the lift-based objective function (Eq. 5) with `lambda = 4e-4`", and "The optimal solution was indeed confirmed to be insensitive to order of magnitude variations in `lambda`." | Same, section III. | Picking a starting regularisation weight for a lift-objective inversion. | **This claim is contradicted by Wu, Zhang & Zhang - see section 2.** Do not carry the insensitivity claim into a different objective or a different case class without testing it. |
| Inversion mesh actually used: a C-grid with **291 points wraparound and 111 wall-normal**, 200 grid points on the airfoil surface, farfield at **35 chord lengths**, freestream eddy viscosity `nu_t/nu = 3`. Numerical errors at this resolution are stated low enough "to not obscure the treatment of turbulence modeling errors", verified by a grid convergence study. | Same, Discretization subsection. | The order of magnitude of an airfoil field-inversion mesh: order 3e4 points, not 1e6. | Compressible structured finite volume, MUSCL and Roe, D-ADI implicit. Not our unstructured incompressible stack. |
| Prediction-time cost of the trained augmentation is small: querying the network for `beta` at grid locations "was confirmed to add < 10% of additional compute time compared to the baseline calculation", and the augmented model showed "comparable convergence characteristics to the baseline". | Same, section V and Summary. | Pricing the *deployment* of a trained closure correction. | It prices the forward query only. It says nothing about the inversion. |
| Network size: "Typically, 3 layers and about 100 nodes were employed with a sigmoid activation". Training data was three S-series airfoils (S805, S809, S814) at `Re` in {1e6, 2e6, 3e6}; the headline model P was trained on **S814 alone** at `Re` 1e6 and 2e6 and tested on the other two airfoils. | Same, section IV and Table I. | Sizing a reconstruction network, and the training-to-test split that demonstrated generalisation. | The airfoils' experimental polars come from the open literature refs 52-54, which this session did not fetch. |

### The omission, recorded as the finding

**The paper reports no compute cost for the inversion, anywhere.** A search of the full text
for hours, seconds, processors, cores, CPU or wall clock returns nothing but false positives
("second-order", "second moment"). There is no optimisation iteration count for the L-BFGS
solves, no core count, and no wall time. The only compute number in the paper is the `< 10%`
*prediction* overhead, which prices the wrong thing entirely.

This is exactly the reproducibility gap this lab's own review recorded against Cappelli &
Mansour: careful and disclosure-heavy on every axis except the one a reader needs to schedule
the work. **A reader cannot budget FIML from this paper.**

### Reproduction trigger fired

Charter section 6, **trigger 3**: the paper disagrees with another we read this session. Singh
et al. state the inverted field is insensitive to order-of-magnitude changes in the
regularisation weight; Wu, Zhang & Zhang state that trial and error is needed to find a good
value and publish a tuning rule for it. One of those two will govern our own inversion, and
the disagreement is either a case-class difference, an objective-function difference, or one
of them being wrong. Proposal filed.

