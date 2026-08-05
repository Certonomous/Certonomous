# W2 — Dow's structural-uncertainty program, priced against this lab's measured numbers

Date: 2026-08-05 (UTC). **Zero compute.** Nothing here ran a solver. Every cost
is either a measurement already on this lab's record, cited to the file that
holds it, or an arithmetic extrapolation of one, marked as such.

The reading behind this is `W2_DOW_STRUCTURAL_UQ_READING.md`. The scoping of
the alternative Katie named is `W2_SAPSIS_DO_SCOPING.md`. This document answers
the operational question only: **which of Dow's steps can we run today, which
need building, what does each cost, and what is worth proposing.**

---

## 0. The headline: Dow's parameterization is richer than ours, and that is a candidate explanation for the plateau

The S1 CBFS inversion has plateaued. The data term reached about 0.99908, a
**0.09 percent** reduction against a pre-registered bar of 30 percent, while
the gradient is finite-difference-verified on four cells at 0.021 to 0.199
percent and the optimizer descends. So the machinery is not the suspect. The
inverse step in this lab is therefore **partially established**: the gradient
is right, the price is measured, and the thing the optimizer is allowed to
change may not be able to buy what the objective is asking for.

Reading Dow against that plateau produces a specific, mechanical statement of
what is different, and it is not a matter of degree.

**Dow infers the eddy viscosity itself. We infer a multiplier on one source
term of one transport equation whose solution then produces the eddy
viscosity.** Three consequences, in order of how hard they are to argue with:

1. **There is a PDE between our control and the quantity that acts on the
   flow.** Dow's `nu_T(x)` enters the momentum equation directly and, during
   his optimization, the turbulence transport equations are not solved at all
   (AIAA 2011-1762 section II.A.2, READ IN FULL). Our `beta(x)` multiplies the
   production term of the omega equation; omega is then transported, diffused
   and coupled to k before anything reaches the momentum equation. **A
   per-cell control that must pass through a diffusion operator cannot produce
   an arbitrary per-cell response**, and the high-wavenumber content of beta is
   damped before it ever reaches `nu_T`.
2. **The SST stress limiter can cut the path outright.** The stock eddy
   viscosity is `nu_t = a1 k / max(a1 omega, F23 S)`, and this lab's own frozen
   solver implements exactly that formula. **Wherever the limiter binds, that
   is wherever `F23 S` exceeds `a1 omega`, `nu_t` has no algebraic dependence
   on omega at all.** A beta multiplier on the omega equation is, in those
   cells, acting on a variable that does not appear in the eddy viscosity. The
   dependence is not zero, because omega still appears in the k equation's
   dissipation term and k survives in the numerator, but the direct path is
   switched off precisely in the shear layer where the limiter is designed to
   bind and where the CBFS discrepancy lives. **This is checkable at zero
   compute** on the baseline fields already on disk: count the cells where
   `a1 omega < F23 S` and overlay them on the adjoint sensitivity map.
3. **Our prior biases where their prior regularizes.** Dow penalises the field's
   gradient norm because the inverse problem is genuinely ill-posed where the
   mean velocity gradient vanishes. We pull toward `beta = 1`. In the cells the
   objective cannot see, a total-variation term smooths and an L2 pull simply
   holds the answer at the prior, which is one more way for a descent to stall
   with nothing wrong anywhere.

**What may and may not be concluded from this.** It may be said that Dow's
parameterization is strictly richer, because his control is the field that acts
and ours is a coefficient in an equation that produces it, and richness here is
a statement about the reachable set rather than about dimension: both fields
carry one degree of freedom per cell. It may not yet be said that the
parameterization *is* the cause of the plateau. Dow's 70.5 to 92.1 percent
absorption and our 0.09 percent are on different geometries, different
reference data densities and different solvers, and a three-order gap between
two numbers that were never meant to be compared is a reason to run an
experiment, not a result.

**So the program's first proposal is that experiment, and this lab can already
run it without an adjoint at all.** The SpaRTA frozen machinery built earlier
this year extracts, from LES data on the CBFS mesh, both the eddy-viscosity-form
part of the model error and `bijDelta`, the residual anisotropy that no eddy
viscosity of any magnitude can represent. Propagating the correction with and
without `bijDelta` measures **Dow's absorption fraction on our own case, with
our own machinery, at about 34 core-min** — two propagations at the 15 to 16
core-min the regression rung measured for this case at 15,000 iterations under
load — and it does so independently of
whether any inversion ever converges. If the eddy-viscosity-form part alone
absorbs most of the CBFS velocity error, Dow's premise holds here and the beta
parameterization is the thing standing between us and it. If it does not, then
the premise itself fails on this case and no richer inversion would have
rescued it. **Both answers change what the lab does next**, which is what a
proposal is for.

---

## 1. The three steps, and the state of each one here

Dow's method is three separable steps. The lab's position on them is unusual
and worth stating in one line before the detail: **we already own the hardest
step and most of the third, and the step nobody has built is the cheapest one.**

| Dow's step | What it is | Our position today | Solver cost |
| --- | --- | --- | --- |
| **1. Inverse modeling** | Infer the eddy-viscosity field that best reproduces reference data, by adjoint-driven optimization | **PARTIALLY ESTABLISHED.** The CBFS adjoint converges, the gradient is verified against finite differences on four cells at 0.021 to 0.199 percent with one cell chosen independently by the supervisor sweep, and the optimizer descends. The data term has plateaued at about 0.99908, a 0.09 percent reduction against a 30 percent bar. Section 0 states the leading hypothesis and the experiment that tests it | 16.2 to 16.4 core-min per gradient at 4 ranks, measured twice by W4 and confirmed across the S1 run's own consecutive evaluations at 15.83 to 17.70 |
| **2. Statistical modeling** | Fit a Gaussian random field to the log discrepancy: covariance form, correlation length, magnitude scaling | **NOT BUILT, and it is the cheap one.** Every component exists in the F6d random-matrix sampler and needs a scalar-field variant, not a new method | **Zero solver cost.** Eigen-decomposition of a covariance on a coarse auxiliary mesh, plus a two-parameter likelihood maximisation |
| **3. Propagation** | Sample the field and push each realization through the primal | **MOSTLY BUILT.** The F6d ensemble builder, the OpenFOAM field injection path and the null test all exist and were verified before any sample ran | One primal per sample: 3.23 core-min median on the periodic hill, 4.76 on CBFS at 4 ranks, 5.57 on the hump serial |

Two consequences follow immediately and they set the whole program.

**The cost inversion.** In Dow's own work the propagation was cheap because the
turbulence transport equations were switched off during it: *"Since the
turbulent viscosity field is imposed for all but the initial optimization
iteration, the full RANS equations need not be solved, and only the equations
for the mean velocity and pressure fields must be computed"* (AIAA 2011-1762
section II.A.2, READ IN FULL). Our perturbation lives **inside** the omega
equation, so every one of our samples is a full coupled solve. **His cheapest
step is our most expensive one**, and any plan that inherits his sample counts
without re-pricing them is wrong by the ratio of those two things.

**The absorption premise is checkable here and has never been checked.** The
entire method rests on the claim that most of the RANS-to-truth velocity
discrepancy can be represented as eddy-viscosity discrepancy. Dow measured that
at **70.5 to 92.1 percent** as a norm across eight geometries (thesis Table
4.2, machine-checked at `sdk/scripts/dow_2011_table42_check.py`, 10 of 10). We
have never measured our own equivalent number on any case, and we now have an
inversion that could produce it.

---

## 2. What can run today, in the order the dependencies allow

### 2.1 Step 2 is runnable today and needs no solver at all

This is the finding that changes the program's shape. The Gaussian-random-field
machinery Dow's step 2 requires **already exists in this repository, verified
against fifteen of its source paper's own stated properties with zero
failures**, in `demo-output/website/dafoam/f6d_random_matrix_uq/rmt_sampler.py`:

- `build_kl_basis` solves the Fredholm eigenvalue problem by the Nystrom method
  on a structured auxiliary mesh, for an **anisotropic squared-exponential
  kernel** with separate streamwise and wall-normal length scales. Dow's
  covariance is the isotropic squared-exponential, which is that kernel with
  the two lengths equal.
- `KLBasis` carries the truncated expansion and the synthesis Dow writes as
  equation (17) of the paper and section 3.3.3 of the thesis.
- `build_interp_operator` interpolates from the auxiliary field mesh to the CFD
  mesh, which is exactly the step Dow's chapter 4 describes as *"interpolated
  to the mesh points of the channel grid"*.
- The OpenFOAM field write path exists and the whole chain was null-tested:
  propagating the unperturbed field reproduced the baseline reattachment to
  1e-4 in x/h.

**What is missing is small and is honest engineering, not research:** the
existing sampler produces a symmetric-tensor Reynolds-stress field, and Dow's
program needs a **scalar** log field. The KL basis, the interpolation operator,
the mesh reader and the writer are indifferent to that. Two things genuinely do
not exist: the **maximum likelihood fit** of the two covariance parameters to
an observed discrepancy field (Dow's chapter 3, arithmetic on a covariance
matrix), and the **strain-rate scaling regression** that turns a stationary
isotropic field into a non-stationary one (Dow's chapter 4, a one-parameter
constrained fit against fields our solver already writes).

**Cost: zero solver core-minutes.** The eigen-decomposition is a dense
symmetric problem on a coarse auxiliary mesh; F6d used a 50 by 30 mesh and 30
retained modes, capturing 98.95 percent of the variance.

### 2.2 Step 3 is runnable today on the periodic hill, at a measured price

F6d propagated 40 samples per dispersion setting through PH_Breuer at 15,600
cells and **measured** the cost per member rather than estimating it: 135.47
core-min for 40 members at the lower dispersion, 170.35 at the higher, median
member 3.23 and 4.48 core-min respectively, 394.79 core-min for the whole 96-run
study. That is the price of a Dow-style propagation on this box, already paid
once for a different sampler.

**A 40-member eddy-viscosity band on the periodic hill therefore costs about
130 core-min plus a baseline**, and it inherits an ensemble builder, an
injection path, a null test and an aggregation script that have all been run.

### 2.3 Step 1 runs, and its descent is the open question rather than its gradient

The CBFS inversion has run under the S1 pre-registration and plateaued. What is
established: the adjoint converges, the gradient is right, and the
per-evaluation cost is the most trustworthy number in the lab. What is not
established: that the descent can move the data term. The normalised data term
has fallen about 0.09 percent against a pre-registered gate of 30 percent,
while the field itself has moved substantially, reaching a beta of 0.735 in
places.

**That combination is the exact signature Dow warned about**, and reading it in
his words is what makes it legible rather than alarming. Thesis section 3.4.1:
where the mean velocity gradient vanishes, the objective is insensitive to the
field, the sensitivity is identically zero there, and the optimizer *"will
never change the value"* there while oscillations grow elsewhere in the null
space; the oscillations *"do not significantly affect the computed velocity
profile"* but *"will have a large impact on the statistical model"*. Our
inversion has the mirror image of his symptom — a field that moves while the
objective barely does — and it has **no total-variation regularizer at all**,
only an L2 pull toward one.

This is a defect found by reading rather than by running, and section 4 prices
the fix.

---

## 3. What needs building, with what it costs

Ordered by cost, cheapest first. Every solver cost is anchored to a measured
number from section 1's table; every zero is a claim that no solver runs.

| Item | What it is | Cost | Anchor |
| --- | --- | --- | --- |
| **B1. Scalar log-field sampler** | A scalar variant of the existing KL sampler: same kernel, same Nystrom solve, same interpolation operator, writing a `volScalarField` instead of a `volSymmTensorField` | **0 core-min** | The tensor path is 459 lines and verified; the scalar path is a subset of it |
| **B2. Maximum likelihood fit of the covariance** | Dow's chapter 3 step: maximise the log-likelihood over the process variance and the correlation length, with the nugget term he states | **0 core-min** | Dense symmetric arithmetic; Dow himself did it by evaluating the likelihood on a grid of parameter pairs |
| **B3. Total-variation regularizer in the inversion objective** | Dow's `eps` times the squared gradient norm of the field, added to the objective, with its sensitivity **computed directly and added to the adjoint gradient** rather than differentiated through the solver | **0 additional solver core-min per evaluation** | Both artifacts state the regularizer sensitivity is computed independently of the adjoint. Our driver already calls a fresh container per evaluation from a host-side optimizer, so the term and its gradient are host-side arithmetic on a field we already have |
| **B4. Strain-rate scaling regression** | Dow's chapter 4 step: regress log-discrepancy magnitude on the corrected strain-rate norm, constrained through the origin | **0 core-min** | Both inputs are fields the solver already writes |
| **B5. A 40-member propagation on the periodic hill** | Step 3, held out from wherever the statistics were fitted | **about 130 core-min** | F6d measured 135.47 core-min for 40 members at 15,600 cells |
| **B6. A 40-member propagation on CBFS** | Step 3 on the case the statistics came from, as an in-sample control | **about 190 core-min** | 4.76 core-min per cold primal at 4 ranks, derived from the W4 finite-difference sweep of nine primals in 642 s |
| **B7. Dow's cheap propagation mode** | Freezing the turbulence transport and solving momentum and pressure alone with a prescribed viscosity, which is what made his 500 samples affordable | **Unpriced, and deliberately so** | Nothing in this lab has measured it. It is a question about our solver, not about his paper, and pricing it from his sentence would be inventing a number |
| **B8. Dow's own 500-sample count** | Five hundred members, his number | **about 1,615 core-min on the periodic hill** | 3.23 core-min median member times 500. Recorded so the number is on the page, not because it is recommended |

**The total of everything that is not a propagation is zero solver
core-minutes.** That is the program's central practical claim: Dow's steps 2
and the regularizer fix cost nothing but attention, and the only thing that
costs core-minutes is sampling, which we have already priced by measurement.

---

## 4. Three things the reading changes about work already in flight

Stated separately from the proposals because they are corrections and
observations about existing items, not new work.

**4.1 The inversion has no ill-posedness regularizer, and the omission is
load-bearing for a UQ purpose.** The S1 objective carries an L2 pull toward
one. That is a *bias* term: it says the field should be near the baseline. It
is not a *smoothness* term and it does nothing about the null space Dow
identifies, where the objective cannot see the field at all. For a field
inversion whose output is a beta correction to be evaluated on its own terms
this is a defensible choice. **For a field inversion whose output feeds a
statistical model it is not**, and Dow states exactly why in one sentence. If
the CBFS field is ever going to be fitted as a random field, B3 is a
precondition, and B3 is free.

**4.2 The absorption fraction is a number we can and should produce.** Dow's
70.5 to 92.1 percent is the evidence for the premise under the whole method.
Our equivalent is one arithmetic step from the inversion's own recorded
objective history and it has never been computed. It also has a natural
falsifier already sitting on the record: the duct baseline predicts **exactly
zero secondary flow** against a DNS 2.07 to 2.22 percent, and no eddy-viscosity
field of any magnitude can produce secondary flow in a straight duct. So the
absorption fraction is expected to be high on a separated two-dimensional case
and structurally zero on the duct's secondary flow, and measuring both would
bound the method's domain from inside our own record.

**4.3 F6d already measured something this program must not re-learn the hard
way.** On the periodic hill, residual-gating an ensemble discarded exactly the
members nearest the truth: the twelve members failing the gate had mean
reattachment 5.556 against the truth's 4.6 to 4.7, while the twenty-eight
passing it averaged 6.695, and at the higher dispersion the gated subset stopped
containing the truth altogether while the ungated one still did. **Any
propagation this program runs reports the ungated ensemble, and reports the
gated one beside it if it reports it at all.** That is not a new rule; it is
F6d's rule, and this program adopts it unchanged.

---

## 5. What is proposed, and what is deliberately not

### Proposed

1. **`w2-dow-absorption-fraction-from-the-frozen-fields`.** Section 0's
   experiment. Measures how much of the CBFS velocity error an
   eddy-viscosity-form correction can absorb, against Dow's 70.5 to 92.1
   percent, using the frozen machinery and needing no adjoint. About 34
   core-min. **It is the first proposal because it decides whether the rest of
   this program has a premise.**
2. **`w2-dow-statistical-step-on-the-cbfs-discrepancy-field`.** Step 2 in full,
   on the field the S1 inversion produced, plus the ill-posedness diagnosis
   Dow's chapter 3 makes possible and the limiter-overlap count from section 0.
   Zero solver cost. It ends with a fitted covariance and a verdict on whether
   the field is fit-able at all.
3. **`w2-band-validation-on-a-held-out-case`.** Step 3 as a held-out test, on
   the periodic hill, with the coverage question stated as the gate. About 160
   core-min against a measured per-member cost. This is the only proposal that
   decides whether the band is worth anything.

### Not proposed, with the reason

- **Dow's 500-sample count.** Priced at B8 and not proposed. Forty members is
  what this lab has measured and what F6d found sufficient to place a band; five
  hundred is his number on his cheaper propagation, and adopting it would be
  spending 1,615 core-min to inherit a convention.
- **The frozen-turbulence propagation mode, B7.** Not proposed because it is
  unpriced, and a proposal with an invented cost is worse than no proposal.
  It is the right thing to scope if the band work continues.
- **Dynamically-orthogonal propagation.** Scoped and declined in
  `W2_SAPSIS_DO_SCOPING.md`, on the ground that our propagation problem has no
  time evolution in it for the method to track. The scoping carries its own
  falsifier.
- **Polynomial chaos as a replacement for sampling.** Not proposed here, and
  neither Dow artifact is evidence for or against it. The lab already holds a
  worked non-intrusive polynomial chaos design for closure coefficients on the
  flat plate whose sample set was never run, and that item is the place this
  question belongs, not here.
- **A Reynolds-stress tensor field instead of a scalar.** This is Dow's own
  stated next step and the lab has already gone there once, by a different
  route, and published the negative result. Re-opening it needs a reason that
  is not "Dow suggested it in 2011".
- **The 1-D channel reproduction of AIAA 2011-1762.** Tempting and cheap: no
  CFD, a two-point boundary value problem, and two published answers to hit,
  the objective falling from `6.3127e-1` to `4.6796e-6` in 100 iterations and
  the likelihood optimum at `(0.1898, 0.1532)`. Not proposed **yet** for one
  reason: the Moser, Kim and Mansour profiles are not on this box, so it opens
  with an external data fetch, and the instrument it would check is the same
  one proposal 2 exercises against a real field. If proposal 2's fitted
  covariance is ever doubted, this is the check that settles it, and it should
  be filed then rather than now.
- **Re-parameterizing the inversion onto the eddy viscosity directly.** This is
  what section 0's argument points at, and it is deliberately **not** proposed
  in this document. It is a solver change of the same class as the destruction
  term patch, its build time is unmeasured, and proposal 1 exists precisely to
  establish whether it would be worth paying for. Proposing the fix before the
  diagnosis is how a lab buys a capability it did not need.

---

## 6. The honest risks, stated before anything runs

- **R1. The inversion may not produce a discrepancy field worth fitting.** If
  the data term has not moved, the field that moved is in the objective's null
  space, and a covariance fitted to it describes our optimizer rather than the
  flow's model error. Proposal 1 is designed so that this outcome is a
  *result*, not a failure, and its diagnosis is the point.
- **R2. Our sampled field is not Dow's random variable.** He samples a viscosity
  that is imposed; we sample a coefficient inside a transport equation that
  then reacts. Bands from the two are not comparable and the record must never
  set them side by side as if they were.
- **R3. The reference data has a known bad region.** The CBFS truth fields carry
  an under-resolved top-wall strip filled by extrapolation, established by this
  lab's own forensics. Any all-cells objective or all-cells discrepancy
  statistic includes rows that are not truth, and both proposals must exclude
  or disclose them.
- **R4. Band width is not band quality.** F6d's random-matrix band contained the
  truth and was five times wider than a two-point deterministic union that also
  contained it. A wide band that contains the truth is not a success, and a
  narrow band that does not is a failure in the unsafe direction, which is
  precisely how Dow's own two-dimensional bands failed. Proposal 2's gate states
  both quantities.
- **R5. Cost model assumes four cpus are free.** Every per-member number here is
  a four-rank figure. The S1 pre-registration measured that oversubscribing four
  ranks onto two cpus billed 8.0 core-min against 6.1 for the same solve. An
  ensemble launched onto a busy box will cost more than this page says.

---

## Related

- `demo-output/website/campaign/W2_DOW_STRUCTURAL_UQ_READING.md` — the sources.
- `demo-output/website/campaign/W2_SAPSIS_DO_SCOPING.md` — the declined
  alternative.
- `demo-output/website/campaign/F6d_random_matrix_uq.md` — the machinery this
  program reuses and the negative result it must not re-learn.
- `demo-output/website/campaign/F6a_epistemic_band.md` — the deterministic band
  any probabilistic band is measured against.
- `demo-output/website/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` — the gradient
  and its price.
- `demo-output/website/dafoam/ladder-b/S1_CBFS_INVERSION_PREREGISTRATION.md` —
  the inversion this program consumes, including its amendment.
- `sdk/scripts/dow_2011_table42_check.py` — the absorption fractions, checked.
