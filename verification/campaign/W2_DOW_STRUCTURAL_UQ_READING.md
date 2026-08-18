# W2 reading — Dow and Wang, structural uncertainty as an inferred eddy-viscosity discrepancy field

Date: 2026-08-05 (UTC). **Zero compute** — three PDFs fetched, two read end to
end, one read in the two chapters it was fetched for, plus one arithmetic
check script. No solver ran, no mesh was built, nothing was fitted.

This is the reading behind Katie's directive to turn Eric Dow's MIT work into
an implementation program for the lab's uncertainty line. The program itself
is `W2_DOW_STRUCTURAL_UQ_PROGRAM.md`; this file is the source record it cites.
The dynamically-orthogonal scoping Katie asked for separately is
`W2_SAPSIS_DO_SCOPING.md`.

---

## 0. The artifacts, and what each tier permits

**Artifact A, the thesis.** Eric Alexander Dow, *Quantification of Structural
Uncertainties in RANS Turbulence Models*, **SM thesis**, MIT Department of
Aeronautics and Astronautics, submitted 18 August 2011, thesis supervisor
Qiqi Wang. DSpace handle `1721.1/68407`. 70 pages. **Tier: READ IN FULL** —
retrieved 2026-08-05 17:02 UTC from the DSpace bitstream, held at
`docs/papers/dow_mit_sm2011_structural_uncertainties_rans.pdf` with a text
extraction alongside, md5 `0c062cc35e859a661610db3fbcd66f2a`.

Two facts about the artifact that bear on what may be quoted from it. It is a
**Masters thesis, not a PhD thesis** — the title page reads "in partial
fulfillment of the requirements for the degree of Masters of Science", and the
lab's record should not promote it. And the DSpace copy is a **scan with OCR**,
carrying the MIT Document Services disclaimer of quality; two numbers in Table
4.2 are damaged by the extraction and are recovered by arithmetic in section 4
below rather than guessed.

**Artifact B, the companion paper.** Eric Dow and Qiqi Wang, *Quantification of
Structural Uncertainties in the k − ω Turbulence Model*, **AIAA Paper
2011-1762**, 52nd AIAA/ASME/ASCE/AHS/ASC Structures, Structural Dynamics and
Materials Conference, 4 to 7 April 2011, Denver, Colorado. 12 pages.
**Tier: READ IN FULL** — retrieved 2026-08-05 17:02 UTC from the authors' own
institutional copy at MIT, held at
`docs/papers/dow_wang_aiaa2011_1762_komega_structural_uncertainty.pdf`, md5
`b3899b09ed2546310056362710c38be3`.

**An availability finding worth recording, because it is the inverse of the
one this lab is used to.** `10.2514/6.2011-1762` is **closed** on both
Unpaywall and OpenAlex (checked 2026-08-05 17:13 UTC, `is_oa: false`,
`oa_status: closed`, zero open-access locations), and the paper is
nevertheless **publicly readable from the second author's own MIT page**,
HTTP 200. The index of that directory returns 403, so the file is reachable
only by exact name. The lab's `LIBRARY_ACCESS_LIST.md` item 1 records a case
where an author-hosted link was advertised and dead; this is the same
mechanism running the other way, and both say the same thing: **the aggregator
verdict and the author's own server are independent checks and neither
substitutes for the other.**

**Artifact C, the one that is genuinely closed.** Eric Dow and Qiqi Wang,
*Uncertainty Quantification of Structural Uncertainties in RANS Simulations of
Complex Flows*, **AIAA Paper 2011-3865**, 20th AIAA Computational Fluid
Dynamics Conference, 2011, doi `10.2514/6.2011-3865`. **Tier: NOT OBTAINED.**
Nothing is asserted from it anywhere in this reading or in the program, not
even from its title. Routes tried and failed, all 2026-08-05: Unpaywall on the
DOI (`is_oa: false`, `oa_status: closed`, zero open-access locations);
OpenAlex on the DOI (`any_repository_has_fulltext: false`, one location, the
AIAA landing page); Semantic Scholar on the DOI (`openAccessPdf.url` empty);
and four constructed filenames under the second author's MIT paper directory
that served artifact B, all HTTP 404. Filed to
`agenda/LIBRARY_ACCESS_LIST.md`.

**On the "inverse RANS with Gaussian random fields" paper Katie named as a
separate item:** searching for it returns artifacts A and C. The inverse-RANS
machinery and the Gaussian-random-field prior are **both inside artifact A**,
chapters 2 and 3, and artifact A is read in full, so nothing in the program is
blocked on finding a separate paper. No third Dow and Wang inverse-RANS paper
was found in the second author's OpenAlex record; his other 2011 to 2015 work
is compressor-blade robust design and tolerancing, and his own PhD thesis
(`1721.1/97351`, 2015) is *Robust design and tolerancing of compressor blades*,
a different subject. **There is no Dow PhD thesis on structural uncertainty to
fetch.** That is a finding, and it bounds how far this line was carried by its
own author.

---

## 1. Claim, source, where it applies

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| **The whole method is three steps**: an inverse modeling step that infers the eddy viscosity from DNS, a statistical modeling step that fits a random field to the inferred discrepancy, and a propagation step that samples it back through RANS. | A section 1.1.1; B section II. READ IN FULL. | The shape of any reproduction here. The three steps are separable and each has its own gate. | It is not a Bayesian posterior. There is no likelihood over the flow data and no posterior over the field; the inversion is a single deterministic optimum, and the statistics are fitted to that one optimum afterwards. Calling it Bayesian is a category error we should not make in our own write-ups. |
| **The inverse problem is `min over nu_T of \|\|u(nu_T) − U_DNS\|\|^2_L2 + eps\|\|grad nu_T\|\|^2_L2` subject to `nu_T >= 0`**, with the constraint removed by optimizing `log(nu_T)` and the transformed gradient `dJ/dlog(nu_T) = nu_T dJ/dnu_T`. | B equations (1) to (4); A sections 2.3.1 to 2.3.2 and 3.3. READ IN FULL. | Directly reusable as our objective. The log transform is the same trick our own beta bounds achieve by box constraints, and it is cheaper. | The regularizer is a **gradient-norm (total variation) penalty on the field**, not an L2 pull toward the baseline. It is a different prior from the one our beta inversion uses and from Wu and Zhang's, and it is doing a different job: it exists because the problem is genuinely ill-posed where the velocity gradient vanishes, not because a modeller wanted smoothness. |
| **Their objective uses the whole velocity field**, `U_DNS` everywhere in the domain, not sparse probes. | A section 2.3.1 objective; A section 4.5.1 comparison figures. READ IN FULL. | Any like-for-like reproduction of *their* result needs a full-field reference. | Our CBFS inversion targets a benchmark LES field, and Wu and Zhang's targets **30 randomly placed points**. Three different data densities, three different conditioning problems. A band derived from a 30-point inversion is not Dow's band. |
| **Regularization is not optional and its value is stated**: `eps = 1.0e-4`, chosen by increasing it until the optimized and DNS effective viscosity profiles agreed after 100 iterations. Without it the optimized `nu_T` oscillates from `y/delta = 0.4` outward, and those oscillations "do not significantly affect the computed velocity profile" but "will have a large impact on the statistical model". | A section 3.4.1; B section III.A. READ IN FULL. | The single most transferable warning in the thesis for us: **the inversion can be right on the objective and wrong on the field, and the statistical step consumes the field.** Any inversion we run for a UQ purpose needs a field-quality check separate from its objective value. | The number `1.0e-4` is theirs, on their non-dimensionalization, for a channel of half-width 1 with unit forcing. It is not a value to copy. |
| **Adjoint cost claim**: the sensitivity gradient with respect to every nodal value of `nu_T` costs "roughly twice the cost of solving the original PDE", one primal plus one adjoint solve, against `dim(m) + 1` primal solves for finite differences. | A section 2.3 closing; B section II.A.2. READ IN FULL. | The cost argument for our own program, and it is the one thing our stack has independently measured rather than assumed. | This is a **continuous** adjoint, derived by hand and discretized separately (A section 4.4). Ours is a discrete adjoint produced by operator-overloading AD. The two have different verification obligations: theirs needs the tangent-versus-finite-difference study they ran, ours needs the finite-difference-versus-adjoint study we ran. |
| **The straight-channel case is one-dimensional and the adjoint collapses to `d/dy((nu + nu_T) dû/dy) = −2(u − U_DNS)`, with `dJ/dnu_T = −(dû/dy)(du/dy)`**, solved by linear finite elements. Optimizer L-BFGS from NLopt. `J` falls from `6.3127e-1` to `4.6796e-6` in 100 iterations; peak velocity error falls from about 10 percent to about 1 percent. | B section III.A and equations (19) to (21); A sections 3.2 to 3.4.1. READ IN FULL. | A zero-CFD reproduction target. This entire case is a 1-D two-point boundary value problem with published DNS input; it needs no OpenFOAM, no mesh and no adjoint framework, and it reproduces a published objective trajectory. | It is a channel. Nothing about separation, curvature or a pressure gradient is tested by it, and the thesis says so by moving to chapter 4. |
| **DNS input for the channel is Moser, Kim and Mansour 1999**, `Re_tau` about 180, 395 and 590; `Re_tau = 180` corresponds to `Re` about 5,600 on the channel height. The DNS effective viscosity for comparison is a force balance, `nu_T,eff = [(1 − y/delta)^-1 partial U_DNS / partial y]^-1`. | B section III.A, equations (18) and (21); A section 3.4.1. READ IN FULL. | The reference data is public and standard, and the force-balance identity is a zero-compute check anyone can run on it. | The force-balance expression is the *reference* profile they compare the inversion against, not the inversion's target. The inversion targets the velocity. |
| **The statistical model is a zero-mean Gaussian random field on the LOG discrepancy**, `X = log(nu_T*) − log(nu_T^{k-omega})`, with a squared-exponential covariance. For the channel the covariance is written on `log(y)`: `cov(y_i, y_j) = sigma^2 exp(−(log y_i − log y_j)^2 / 2 lambda^2)`. Parameters by maximum likelihood, maximised at **`(sigma, lambda) = (0.1898, 0.1532)`**. | B section II.B, equation (14), and figure 4; A section 3.3.2 and figure 3-6. READ IN FULL. | The form we would fit: log-discrepancy, not discrepancy, so sampling cannot produce a negative viscosity. The MLE step is arithmetic on a covariance matrix and costs no CFD. | **The stationarity is in `log(y)`, not in `y`.** That is a wall-normal stretching chosen for a channel and it does not carry to a two-dimensional domain. Chapter 4 abandons it, and says why (next row). |
| **The MLE is regularised too**: a small error `e = 1e-6` is added on the diagonal (as `(e/nu_T*)^2`) because singular values of the covariance matrix reach zero and the log-likelihood is otherwise undefined. Decreasing `e` further does not move the estimate. | B section III.B, equation (23); A section 3.4.2. READ IN FULL. | Anyone implementing the MLE hits this on the first run. It is a nugget term, stated with its value and its insensitivity check. | The insensitivity claim is theirs, on their covariance matrix. Ours needs its own check. |
| **Propagation is plain Monte Carlo, 500 samples per Reynolds number**, with realizations drawn through a Karhunen-Loeve expansion of the covariance matrix, `X = sum_i sqrt(lambda_i) x_i(y) phi_i(theta)` with `phi_i ~ N(0,1)` independent. They state the intent to move to sparse-grid stochastic collocation later and do not do it here. | B section II.C, equation (17), and section III.C; A sections 3.3.3 and 3.4.3. READ IN FULL. | The propagation step is **500 primal solves with a prescribed viscosity field**, and prescribing `nu_T` means the turbulence transport equations are not solved at all (next row). That is what makes it affordable. | No polynomial chaos, no stochastic collocation and no reduced-order propagation is demonstrated anywhere in either artifact. Their comparison to polynomial chaos is a literature-review sentence about *other people's* work, not a measurement. Anyone citing Dow for "Monte Carlo beats polynomial chaos here" would be citing something that is not in the text. |
| **The propagation primal is cheaper than a RANS solve**: "Since the turbulent viscosity field is imposed for all but the initial optimization iteration, the full RANS equations need not be solved, and only the equations for the mean velocity and pressure fields must be computed." | B section II.A.2. READ IN FULL. | This is the sentence the whole cost estimate of a propagation campaign turns on, and it applies to the inversion iterations as well as to the Monte Carlo samples. | It is a claim about their solver architecture. Whether our stack can freeze the turbulence transport and solve momentum and pressure alone is a question about our solver, not about this paper, and the program treats it as an open engineering item rather than an inherited fact. |
| **Channel band verdict: the DNS profile "mostly falls within the 2σ error bars" at all three friction Reynolds numbers**, with the bands fitted at `Re_tau = 180` and applied unchanged at 395 and 590. Bands widen toward the centreline. | B section III.C and figure 5; A section 3.4.3 and figure 3-8. READ IN FULL. | This is the only successful band validation in either artifact, and it is a **held-out validation in Reynolds number**: the statistics are fitted at one `Re_tau` and tested at two others. That protocol is directly copyable. | "Mostly" is the authors' own word and neither artifact prints a coverage fraction. **There is no number here.** Any coverage percentage we ever quote must be ours, measured on our own runs, and never attributed to Dow. |
| **Two-dimensional extension: eight randomly generated channel geometries**, walls drawn from a Gaussian process with correlation `C(d) = exp(−d^2/(c_2 + c_1\|d\|))` conditioned to zero slope at inlet and outlet, simulated by the LU matrix factorization method of Davis 1987; periodic domain; DNS by CDP (incompressible, node-based finite volume, Crank-Nicolson), RANS by Joe (compressible, second-order finite volume, Wilcox k − ω), RANS meshes "roughly twice as coarse" as the DNS meshes; DNS averaged over 50,000 steps at `dt = 7.5e-?` and over spanwise slices and the centreline symmetry; laminar viscosity `2.0e-3`, unit body force. | A sections 4.2 and 4.3. READ IN FULL. | The recipe for a random-geometry family, and the reason the whole study is only eight samples: every sample needs its own DNS. | The DNS timestep exponent is illegible in the scan (`7.5 x 10^?`) and is **not reproduced here**. Omission recorded. So is the cell count of every mesh, the wall-clock cost of anything, and the number of spanwise slices: **not one computational cost appears anywhere in either artifact.** That absence is the single largest gap for an implementation program and it is why every cost in the program is anchored to our own measurements. |
| **The inversion absorbs 70.5 to 92.1 percent of the velocity discrepancy across the eight geometries**, measured as a change in the discrepancy norm; a typical inversion took "roughly 30 iterations" while tuning thousands of nodal values. | A Table 4.2 and section 4.5.2. READ IN FULL, and machine-checked, section 4 below. | The load-bearing number of the entire method: it is the evidence for the premise that model-form error can be *represented* as eddy-viscosity error. It is also our own inversion's sanity target — an inversion absorbing far less than this on a comparable case is telling us something about the case or the machinery. | The complement is not noise, and the thesis says so: the residual 8 to 30 percent is DNS averaging error, compressible-versus-incompressible solver mismatch, discretization differences, **and the Boussinesq alignment assumption itself**. That last one is the part no eddy-viscosity band can ever cover, and it is the honest ceiling on this whole approach. |
| **The 2-D discrepancy field is anisotropic and non-stationary**: streamwise correlation length near the wall much larger than wall-normal, largest magnitudes around the separation bump, magnitude going to zero at the wall and near the centreline where the shear strain rate is small. | A section 4.5.2 and figure 4-10. READ IN FULL. | Directly contradicts the stationary isotropic model of chapter 3 and is the reason chapter 4 changes the model. Our own CBFS discrepancy field can be tested for exactly these three properties at zero extra cost once an inversion exists. | The observation is on symmetric periodic random channels at one Reynolds number with one turbulence model. It is not a general claim about separated flows. |
| **The 2-D statistical model is therefore a scaled isotropic field, not a fitted anisotropic one**: an isotropic zero-mean Gaussian random field with squared-exponential covariance at correlation length **`lambda = 0.2`** is simulated on a uniform grid by Karhunen-Loeve, interpolated to the mesh, and then **scaled pointwise by a linear regression of log-discrepancy magnitude against the corrected strain-rate norm `\|\|S\|\|_2 (1 − exp(−d/d_0))`**, with `d` the wall distance and `d_0` the wall distance of the point where `\|\|S\|\|_2` is largest. The regression is constrained through the origin because the log-discrepancy must vanish at the wall. Symmetry about the channel centreline is then enforced by hand on every realization. | A section 4.5.3, figure 4-11 and figure 4-12. READ IN FULL. | This is the actual, complete recipe for a spatially varying prior conditioned on local RANS state, and every input to it (`\|\|S\|\|_2`, wall distance) is a field our solver already writes. It is implementable here without a single new physics model. | The correlation length 0.2 is **asserted, not fitted** — chapter 4 runs no maximum likelihood step, unlike chapter 3. The scaling regression is a fit to eight cases with one free slope. And the enforced symmetry is a property of their geometries, not of the method. |
| **The 2-D propagation, 500 Monte Carlo samples, produces bands that DO NOT contain the truth**: "The mean DNS x-velocity profiles typically fall outside the 2σ intervals, especially near the center of the channel. This means the estimated level of uncertainty in the turbulent viscosity is too low." The y-velocity profiles are "mostly contained". The stated cause is that the linear fit against the corrected strain-rate norm "is quite flat", so large-magnitude realizations are too unlikely. | A section 4.5.4 and figure 4-14; conclusions chapter 5. READ IN FULL. | **The headline result of the thesis is a failed band, disclosed by its author**, and it fails on the axis that matters to a certification lab: the band is too narrow, which is the unsafe direction. Anyone selling this method as ready should be shown chapter 5. | The failure is attributed to the *scaling model* (a flat one-parameter regression), not to the GRF idea, the inversion, or the propagation. That attribution is the author's and it is plausible, but it is one hypothesis and the thesis does not test it. It is a re-openable question and the program treats it as one. |
| **Stated future work, in the author's own order**: extend to 3-D; study transonic and supersonic; and — because the Reynolds stress and mean strain are not in general aligned — **model uncertainty in the Reynolds stress tensor rather than the eddy viscosity**, which "requires developing a statistical model for a tensor field rather than a scalar field". Also, the inverse fields could be used to improve models by correlating them with flow features. | A chapter 5. READ IN FULL. | The last two items are, respectively, the eigenvalue-perturbation and random-matrix family the lab has already touched, and field-inversion machine learning, which the lab has already read in full. **Dow's own next step is the line the field actually took.** | This is a 2011 statement of future work. It is not evidence about what those methods achieve, and it is not a citation for anything about them. |

---

## 2. How their inversion maps onto ours, stated exactly

Katie's question is what our field-inversion adjoint buys against Dow's
inverse step. Set the two side by side and the mapping is one substitution
plus one genuine difference.

| | Dow 2011 | This lab, 2026 |
| --- | --- | --- |
| Inferred field | `nu_T(x)` directly, at every node | `beta(x)`, a per-cell multiplier inside the SST omega equation |
| Relation to the eddy viscosity | `nu_T` **replaces** the turbulence model output; the transport equations are switched off during the optimization | `beta` **perturbs a term inside** the transport equations, which keep running |
| Positivity | enforced by optimizing `log(nu_T)` | enforced by box bounds on `beta` |
| Prior | total-variation penalty `eps\|\|grad nu_T\|\|^2` | L2 pull to `beta = 1` |
| Objective data | full DNS velocity field | benchmark LES velocity field |
| Gradient | hand-derived continuous adjoint, verified against a tangent solver and finite differences | discrete adjoint by operator-overloading AD, verified against finite differences |
| Optimizer | L-BFGS, NLopt | L-BFGS-B |

**The substitution.** Dow's discrepancy variable is `X = log(nu_T*) −
log(nu_T^{k-omega})`, and our inversion's natural discrepancy variable is
`log(beta)`. These are the same kind of object — a dimensionless log-ratio
field, zero where the model is right, positive where the model under-diffuses
— and both are chosen so that exponentiating a Gaussian sample cannot produce
a negative viscosity. **Every step downstream of the inversion in Dow's
program operates on that log field and does not care where it came from.** The
maximum likelihood fit, the Karhunen-Loeve sampling, the strain-rate scaling
and the Monte Carlo propagation are all indifferent to whether the log field
multiplies a viscosity or a destruction term. That is why Dow's steps 2 and 3
are runnable here today on top of machinery the lab already has, and it is the
central claim of the program document.

**The genuine difference, and it is not cosmetic.** Dow's `nu_T` is
*prescribed*: during the optimization the k − ω equations are not solved, so
the map from field to flow is one-way and the propagation samples are cheap
momentum-and-pressure solves. Our `beta` sits *inside* the omega equation, so
every sample is a full coupled RANS solve, and the model's own transport can
partly undo an imposed perturbation. Three consequences, all of which the
program prices:

1. **A Dow-style propagation on our stack costs a full primal per sample, not
   a reduced one.** Their cheapest step is our most expensive one.
2. **Our sampled field is not the same random variable as theirs.** Sampling
   `beta` and sampling `nu_T` produce different `nu_T` distributions, because
   the omega equation intervenes. A band from our sampling is a band on our
   perturbation, and the record must say so rather than calling it a Dow band.
3. **Their parameterization is richer than ours in the only sense that
   matters, the reachable set.** Both fields carry one degree of freedom per
   cell, so this is not about dimension. Dow's control *is* the quantity that
   acts on the momentum equation; ours is a coefficient in a transport equation
   that has to produce it, so ours is filtered by that equation's diffusion and,
   where the SST stress limiter binds, `nu_t = a1 k / max(a1 omega, F23 S)` has
   no algebraic dependence on omega at all. **This is why the reading treats
   our inverse step as partially established rather than working**: the
   gradient is verified and the price is measured, and the S1 CBFS descent has
   plateaued at about 0.09 percent of its data term against a 30 percent bar,
   which is exactly the symptom a control that cannot reach the answer would
   produce. The program document opens on this and proposes the experiment that
   tests it without an adjoint.
4. **Their ill-posedness argument transfers unchanged and is worth heeding.**
   Where the mean velocity gradient vanishes the objective is insensitive to
   the field, the gradient is identically zero there, and the inversion leaves
   junk in the field that the objective never sees. Our CBFS domain has such
   regions. **We have no total-variation regularizer**, and an L2 pull to
   `beta = 1` does not fix ill-posedness, it only biases the answer where the
   data is silent. This is a defect our inversion has today and it was found
   by reading, not by running.

---

## 3. What the alternatives Katie named actually get from these artifacts

Stated tightly, because the honest answer for three of the four is "not much,
and the record should not pretend otherwise".

- **Polynomial chaos.** Both artifacts mention it only in literature review,
  describing Platteeuw, Loeven and Bijl 2008 using probabilistic collocation
  on k − ε closure coefficients. **Neither Dow artifact implements or measures
  polynomial chaos.** Nothing here is a citation for its cost or accuracy.
  Artifact B's section II.C says they "plan to eventually implement" sparse-grid
  stochastic collocation. That is an intention, not a result.
- **Dynamically orthogonal field equations.** Not mentioned in either artifact.
  Scoped separately in `W2_SAPSIS_DO_SCOPING.md` from a primary source.
- **Data-driven surrogates.** Not present. The nearest thing in either artifact
  is chapter 4's linear regression of discrepancy magnitude against a corrected
  strain-rate norm, which is a one-parameter fit of a *scaling*, and chapter
  5's suggestion that inferred fields could be correlated with flow features to
  improve models. That suggestion, written in 2011, is field-inversion machine
  learning as the lab already has it read in full from Singh, Duraisamy and Wu
  and Zhang. **The lab's existing beta inversion is Dow's stated future work
  carried out by other people.**
- **Bayesian coefficient calibration.** Both artifacts position themselves
  against it explicitly and the argument is worth carrying: a Bayesian
  posterior over a handful of closure coefficients cannot express spatially
  varying model error, and its answer is sensitive to a prior nobody has
  information for. Artifact A section 1.2 makes this against Cheung and Moser;
  artifact B section I makes it against Oliver and Moser. This is the strongest
  *argued* claim in either artifact and it is an argument, not a measurement.

---

## 4. The arithmetic check, and the correction it produces

The load-bearing number is Table 4.2. Two of its sixteen cells are damaged by
the scan's OCR, and — separately — **the sentence that defines the table's last
column does not agree with the column.** Section 4.5.2 says the last column is
"the percentage change in the norm of the velocity discrepancy, i.e.
1 − J(vT)/J(v_k−ω)". `J` is defined in section 2.3.1 as a **squared** L2 norm,
so the formula as written is the change in the squared norm. The printed values
are not that. They are `1 − sqrt(J*/J_kω)`, the change in the norm itself,
which is what the sentence's words say and what its formula does not.

`sdk/scripts/dow_2011_table42_check.py` transcribes the table and checks it.
10 of 10 checks pass, zero compute:

- All six undamaged rows reproduce the printed percentage under the norm
  reading to within 0.04 percentage points, the last digit the table carries.
- Under the squared reading they miss it by up to 20.8 points. **The two
  readings are separated by this table, so the correction is a measurement and
  not an opinion.**
- Geometry 8's table cell reads `0.840` and the prose of section 4.5.2 reads
  `0.0840`. The prose value reproduces the printed 89.3 percent; the table
  value gives 66.2 percent. The table cell has lost a zero to the scan.
- Geometry 4's cell reads `0.0.117`. Read as `0.117` it gives 86.25 percent,
  which prints as the table's 86.3.

**What we carry forward, and how to say it.** *On Dow's eight random 2-D
channel geometries, an inferred eddy-viscosity field absorbs 70.5 to 92.1
percent of the RANS-to-DNS velocity discrepancy measured as a norm.* The same
table says 91.3 to 99.4 percent measured as energy. Both are true, they differ
by up to 29 points, and any use of either must say which. This is exactly the
L-28 arithmetic the lab already applies to digitised figures, arriving one
level up: **a ratio quoted without its power is not a number.**

---

## 5. Charter section 6 — which trigger fired

- **Trigger 1, a number on a case we can build: FIRED, twice.** The
  straight-channel inversion of artifact B is a 1-D two-point boundary value
  problem against public Moser, Kim and Mansour DNS with a published objective
  trajectory (`6.3127e-1` to `4.6796e-6` in 100 iterations) and a published MLE
  optimum (`0.1898, 0.1532`); it needs no CFD at all. And the discrepancy-field
  inversion has a directly comparable form on CBFS, where our adjoint is
  verified. Both are carried into the program and both are proposed.
- **Trigger 2, method admissibility expressible as thresholds: FIRED.** A band
  is admissible when it contains the truth on held-out data, and Dow's own
  chapter 4 fails that test while chapter 3 passes it. That is a threshold the
  lab can write down and score, and it is the second proposal.
- **Trigger 3, disagrees with one of our results: did not fire.** Nothing in
  either artifact contradicts a lab measurement. The nearest thing is that
  Dow's 2-D bands were too narrow while the lab's random-matrix study measured
  a band 5.1 times wider than the corner union it replaced — opposite failure
  directions on different methods and different cases, which is a coincidence
  of topic and not a disagreement.
- **Trigger 4, a limit case checkable at zero compute: FIRED and was checked.**
  Section 4. It produced a correction to how the thesis's headline ratio must
  be quoted, and recovered two OCR-damaged cells by arithmetic.

**In-sample check before any proposal was filed, per charter section 7's last
NEVER.** Dow's inversion cases are a periodic straight channel and eight
randomly generated periodic channel geometries. **None of them is one of the
closure challenge's eight scored test cases**, and neither artifact names a
scored case anywhere. The cases the program proposes to invert on are the
lab's own CBFS and the 1-D channel; CBFS is challenge *training*-family, not a
scored test case. No scored case is touched by anything in this reading.

---

## 6. Proposal obligations discharged

Two proposals filed by this reading, both in the agenda inbox:

- `w2-dow-discrepancy-field-inversion-with-grf-prior` — steps 1 and 2 of the
  Dow program on the case where our adjoint is verified, ending at a fitted
  covariance and a field-quality verdict, before any propagation is paid for.
- `w2-band-validation-does-the-propagated-band-contain-the-truth` — step 3 and
  the only question that decides whether the band is worth anything, run as a
  held-out test in the same shape as Dow's own Reynolds-number hold-out.

The program document states which further steps exist, what each would cost
against measured numbers, and which are not proposed yet and why.

---

## Related

- `docs/papers/dow_mit_sm2011_structural_uncertainties_rans.pdf` and `.txt` —
  artifact A.
- `docs/papers/dow_wang_aiaa2011_1762_komega_structural_uncertainty.pdf` and
  `.txt` — artifact B.
- `sdk/scripts/dow_2011_table42_check.py` — the arithmetic behind section 4.
- `demo-output/website/campaign/W2_DOW_STRUCTURAL_UQ_PROGRAM.md` — the program
  this reading exists to support.
- `demo-output/website/campaign/W2_SAPSIS_DO_SCOPING.md` — the
  dynamically-orthogonal scoping.
- `demo-output/website/agenda/LIBRARY_ACCESS_LIST.md` — where artifact C is
  filed.
