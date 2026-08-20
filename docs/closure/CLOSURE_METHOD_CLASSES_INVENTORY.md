# Closure method classes: inputs, invariance, solver coupling, training, and how each one fails

Companion to `PAPER_CATALOGUE.md` (what each paper says) and
`FOUNDATIONAL_MODELS_INVENTORY.md` (what each classical model is). **This document is organised by
method class rather than by paper**, and its job is to answer four questions for each class:

1. What goes in, and **how is invariance handled** — by construction, by augmentation, or not at all?
2. **How is it coupled to the solver** — post-hoc, in-the-loop, or re-solved; explicit or implicit?
3. **What was actually validated** — a-priori (against a stress or flux field) or a-posteriori
   (against a re-solved flow), and over what horizon?
4. **How does it fail, by what mechanism, and with what number as evidence?**

## Rules this document obeys

- **Every number carries its paper and its location.** Where the source is an arXiv preprint the
  citation says "arXiv preprint p./Table/Eq.", because preprint and journal numbering differ.
- **Where a paper reports no number, this document says "none reported" and stops.** It does not
  substitute a plausible one. Five papers in the corpus have no numeric error metric at all
  (Stroefer 2021, Sirignano 2020, Wu 2018, Maulik 2019, Singh 2017 for its flow fields), and that
  fact is itself a finding recorded below.
- **Statements about papers not on disk are marked `BLOCKED-ON-SOURCE` and carry no numbers.**
- Source status for every file: `docs/papers/closure/MANIFEST.md`. Compute feasibility for every
  method: `cases/RANS_LES_closure_models/_common/FEASIBILITY.md`.

---

# 0. The three axes that actually separate these methods

Before the class-by-class treatment, three distinctions do most of the explanatory work, and every
one of them is measured somewhere in the corpus.

## 0.1 Axis 1 — where invariance comes from

| Route | Cost | Guarantee | Corpus evidence |
|---|---|---|---|
| **By construction** (tensor integrity basis) | Free at inference; constrains the hypothesis class | Exact, for any weights | Ling 2016, Kaandorp 2020, Schmelzer 2020, Stroefer 2021 |
| **By augmentation** (replicate data in rotated frames) | **1000x data for 3-D rotational invariance; 2x for reflection** — Wu 2018, arXiv preprint p. 13 | Approximate, and only where data was augmented | Wu 2018 (declines it for rotation, proposes it for reflection) |
| **By local non-dimensionalisation only** | Free | Galilean invariance of *scalars* only; nothing tensorial | Singh 2017, Wang/Wu/Xiao 2017 |
| **Not at all** | Free | None | Sirignano 2020 (explicitly), List 2022 (explicitly), both Maulik papers, Guan 2022, Um 2020, Kochkov 2021 |

**The one controlled experiment on this axis is Ling 2016 Table I (preprint p. 11)**: the same data,
the same hyper-parameter search, a plain MLP on the nine raw components of `S` and `R` versus a
tensor-basis network. Duct `b` RMSE **MLP 0.33 versus TBNN 0.13**, against a linear-eddy-viscosity
baseline of **0.23**. **The unconstrained network is worse than doing nothing.** On the wavy wall
the same comparison is MLP 0.09 versus TBNN 0.08 — nearly tied. *Invariance-by-construction is worth
a factor of 2.5 on the three-dimensional case and almost nothing on the two-dimensional one, which
is what one would expect if its value is in constraining the extra degrees of freedom that 3-D
anisotropy opens up.*

**And the counter-evidence, which is live and unresolved.** Kochkov et al. 2021 (arXiv preprint
p. 3): "**We also explored LC models restricted to take the form of classical closure models (e.g.,
flow-dependent effective tensor viscosity models), but the restrictions hurt model performance and
stability.**" Sanderse et al. 2024 generalise this (arXiv preprint p. 20): "**the evidence that
supports this claim is still rather thin, and some studies are pointing in the reverse direction.
Restricting the reduced models to have a closure form or a particular known symmetry was limiting
their performance in these cases.**" **This document records the disagreement and does not resolve
it.** The two sides are not obviously talking about the same thing: Ling constrains a *constitutive
relation* in a steady RANS solve; Kochkov constrains a *numerical flux correction* in an unsteady
2-D solver.

## 0.2 Axis 2 — how the closure enters the momentum equation

This is the axis with the hardest number in the corpus behind it.

**Wu, Xiao, Sun & Wang, arXiv:1803.05581v3, Table 1, arXiv preprint p. 4.** DNS Reynolds stresses —
error **0.31%** — substituted into the RANS equations at `Re_tau = 5200` give mean velocities with
**21.6% volume-averaged and 35.1% maximum error**. At `Re_tau = 180` the same exercise gives 0.25%
and 0.36%. **The velocity error grows monotonically with `Re` while the stress error does not.**

The diagnosis is the **local condition number** `K(x) = ||G(x,xi)||_Omega ||div tau||_Omega / U_inf`
(their Eq. 2.14, arXiv preprint p. 9), built from the Green's function of the linearised RANS
operator, computable in `O(n^2 log n)` and **provably mesh-independent** (their Appendix B) — unlike
the textbook matrix condition number, which for channel flow is analytically `4n^2/pi^2`, a function
of mesh count alone (their p. 8).

| Coupling | Local condition number at `Re_tau = 5200` | Source |
|---|---|---|
| **Explicit** — `tau` as a fixed source term | **`O(10^2)`** | arXiv preprint p. 14 |
| **Implicit** — linear part absorbed into an optimal eddy viscosity `nu_t^m`, remainder explicit | **`O(1)`** (volume-averaged) | arXiv preprint p. 16 |
| **Explicit with strain-rate dependence** — stress lagged one iteration | `O(10^2)` in the first three iterations -> **DIVERGES** | Appendix C, arXiv preprint p. 30 |

The third row is the one to remember: **initialised with the exact DNS mean velocity**, the segregated
lagged-stress coupling still "leads to divergence of the simulation. Therefore, the solved mean
velocity is not presented in this work since a converged solution was not achieved."

**Every RANS method in this document sits somewhere on this axis, and where it sits predicts its
stability better than anything about its regressor:**

| Method | Coupling | Stabiliser needed |
|---|---|---|
| Wu 2018 PIML | **implicit** `nu_t^L` split, `S` treated implicitly | **none reported** |
| Stroefer 2021 | **implicit** `nu_eff = nu - g^(1) k t_tau`, nonlinear part explicit | pre-training (random init diverges); adjoint transpose term deleted |
| Schmelzer 2020 SpaRTA | additive correction to k-omega SST, so the linear term stays implicit by construction | coefficients shrunk by **0.1** when CFD fails to converge |
| Kaandorp 2020 TBRF | **explicit** `b_ML` blended against Boussinesq | **`gamma_max = 0.8` ceiling** + Gaussian smoothing `sigma = 3` cells |
| Ling 2016 TBNN | **explicit** `b` into momentum and `k`-production | none discussed; no conditioning analysis |
| Singh 2017 FIML | **multiplier on an existing production term** — the stress form never changes | **none needed**; convergence "comparable to the baseline" |

*Singh 2017's placement is the cheapest insight in this document. A multiplier `beta(x)` on the SA
production term cannot make the momentum equation ill-conditioned, because it never touches the
stress-strain relation. The authors chose it for the conditioning of the **inverse** problem
("`beta` is non-dimensional and has a simple initial value of unity", arXiv preprint p. 7) and got
forward-problem conditioning for free.*

## 0.3 Axis 3 — what the training loss can see

| | A-priori | A-posteriori |
|---|---|---|
| Loss is a mismatch in | the closure term / stress / flux | the **solved** flow |
| Needs | full-field DNS labels | a differentiable solver, an adjoint, or a derivative-free optimiser |
| Cost | one regression | one solve (steady) or `n` unrolled steps (unsteady) **per gradient step** |
| Failure mode | the solved flow drifts or diverges | expensive; gradients explode over long chaotic horizons |

**The three controlled experiments that settle the direction of this axis** — same architecture,
same features, same data, only the loss changed:

1. **Sirignano/Freund 2020, Fig. 7 (arXiv preprint p. 19)**: an identically architected network
   trained a-priori on `||h_theta - div tau^r||` shows "**poor predictive performance**" when
   deployed, while the adjoint-trained one outperforms both fixed and dynamic Smagorinsky. The
   authors' reason is mathematical, not empirical: "**optimization does not commute with a nonlinear
   function.**" **No percentages exist in this paper — the comparison is graphical.**
2. **List, Chen & Thuerey 2022, Table 1 (arXiv preprint p. 9)**: the supervised one-step model has
   **the best short-horizon MSE of any model** (1.52e-3 at `t_1`) and is **6.5x worse than using no
   model at all** at `t_2` (0.369 versus NoModel 0.057), where it has diverged. The 10-step
   solver-in-the-loop model is 0.018 at `t_2` — **20x better than the supervised one at the same time
   in the same table.**
3. **Um et al. 2020, Table 1 (arXiv preprint p. 7)**: NON (supervised, no interaction) versus SOL
   (solver-in-the-loop) on five problems: wake 67% versus **91%**; buoyancy 29% versus **60%**; CG
   solver — versus **76%**; 3-D wake 14% versus **22%**. And in 3-D, "we were **not able to train a
   stable NON version despite numerous tests**" (arXiv preprint p. 33).

**But the axis is not one-directional, and Guan 2022 is the counter-example that matters.** On 2-D
decaying turbulence, a purely **offline (a-priori) trained** CNN is stable and accurate with **no
post-processing, no clipping, no added eddy viscosity** — provided the training set is large enough
(Table 2, arXiv preprint p. 13):

| `n_tr` | 500 | 1000 | 10000 | 30000 | 50000 |
|---|---|---|---|---|---|
| a-priori correlation `c` | 0.78 | 0.83 | 0.90 | 0.92 | 0.93 |
| a-posteriori fate (5 ICs) | **unstable** | **unstable** | **unphysical** | **stable** | **stable** |

**And Beck & Kurz 2021 is the counter-counter-example**: a GRU closure reaching "**99.9% cross
correlation in a priori tests**" still "**diverges strongly soon after**" in deployment (arXiv
preprint p. 26). **Guan's threshold sits between correlations of 0.90 and 0.92; Beck & Kurz's model
fails at 0.999. There is no universal a-priori threshold, and Guan et al. say so themselves**
(arXiv preprint p. 13): "**these are just empirical thresholds in this testcase, and such thresholds
might be case-dependent.**"

---

# 1. Analytical closures (Boussinesq, EASM/QCR, SST, SA, Smagorinsky, WALE, Vreman)

Detailed treatment: `FOUNDATIONAL_MODELS_INVENTORY.md`. Summarised here only as the **control** every
learned method must beat.

- **Inputs and features**: pointwise `S`, `Omega`, wall distance `d`, and one or two transported
  scalars. **Invariance**: exact by construction — the models are written as tensor functions of
  tensor arguments. Pope 1975 (JFM 72(2), p. 334-335) proves the basis is **finite**: exactly **10
  independent tensors and 5 invariants** in 3-D; **3 tensors and 2 invariants** in 2-D.
- **Solver coupling**: **implicit by construction.** `nu_t` multiplies `grad u` inside the diffusion
  operator, so it enters the coefficient matrix. This is why classical RANS is robust and why the
  conditioning problem of §0.2 is a *data-driven* problem, not a turbulence-modelling problem.
- **Training**: hand calibration. Menter 1994 (AIAA J. 32(8), p. 1598) is unusually honest:
  "**small changes (5-10%) in modeling constants can lead to a significant improvement (or
  deterioration) of model predictions. None of the available theoretical tools ... can provide
  constants to that degree of accuracy.**"
- **Validation**: a-posteriori always — these models were only ever assessed by running them.
- **Flow classes it works for**: attached and mildly separated 2-D shear flow. Menter's own backward-
  facing-step table (AIAA J. p. 1603): reattachment SST **6.5**, original k-omega 6.4, BSL 5.9,
  Jones-Launder k-epsilon 5.5, **experiment ~6.4**.
- **Flow classes it cannot do at all, with the mechanism**: any flow driven by **normal-stress
  anisotropy**. Pope 1975 p. 332 measures it: in nearly homogeneous shear, experiment gives
  `a11 = 0.3, a22 = -0.18, a33 = -0.12, a12 = 0.33`, and the isotropic-viscosity hypothesis predicts
  **at best** `a11 = a22 = a33 = 0` with `a12 = 0.33`. **The shear stress is exact and all three
  normal anisotropies are wrong by their full magnitude.** Gatski 1996 (printed p. 360) states the
  consequence: "**The two-equation formulation with an isotropic eddy viscosity predicts no secondary
  streamline pattern**" in a square duct.
- **The one-parameter fix, and its cost**: Spalart 2000 (IJHFF 21, pp. 253-254) adds a single
  quadratic term with **`c_nl1 = 0.3`**, "calibrated in the outer region of a simple boundary layer".
  It fixes the square duct — "the skin friction is much closer to experiment" — and **"other flows
  such as 3D wall jets have led to negative results"**. The author's own verdict: "**very
  preliminary** ... **it uses only one of the many quadratic combinations of strain and vorticity**
  ... **A systematic optimisation has not been performed.**" *This is the precedent every corrective
  anisotropy term in §3 is repeating: one flow fixed, another broken, no systematic search.*

---

# 2. Field inversion + machine learning (FIML)

**Corpus status: `BLOCKED-ON-SOURCE` at its foundation.** Parish & Duraisamy 2016, Singh & Duraisamy
2016 and Holland 2019 are all quarantined; only **Singh, Medida & Duraisamy 2017** is on disk. The
formal definition below is taken from **Duraisamy 2021 (arXiv preprint pp. 11-12)**, which is on disk.

## 2.1 What it is

Two stages, with equations from Duraisamy 2021:
- **Stage 1, field inversion**: `min_{delta_m} L[Y, Y_m(delta_m)]` **subject to**
  `R_a(q_m, s_m, delta_m) = 0` (Eq. 7). Infer a *spatial field* of model discrepancy that makes the
  model reproduce an observation.
- **Stage 2, learning**: `min_w L[delta*_m, delta_m(eta*_m; w)]` (Eq. 8). Regress that field onto
  local features.
- **Integrated form (Eq. 9)**: do both in one optimisation. This "**ensures full consistency between
  the learning and prediction environments**" — and is the formulation the corpus cannot read,
  because Holland 2019 is quarantined.

## 2.2 Inputs, features and invariance

**Singh 2017, arXiv preprint p. 12**, candidate set `{Omega_bar, chi, S/Omega, tau/tau_wall, P/D}`
with `Omega_bar = d^2 Omega/(nu_hat + nu)` and `chi = nu_hat/nu`. **The subset actually used is never
stated as a list.** Normalisation is by the *local* scales `nu + nu_hat` and wall distance `d`, with
the stated rationale (pp. 11-12) that dimensional quantities "may have different numeric values even
when two flows are dynamically similar."

**Invariance handling: NONE claimed or enforced.** The authors list it as future work
(arXiv preprint p. 24): "**respecting realizability limits and invariance properties will be
necessary to constrain the model, especially when the model is operating in an extrapolatory mode.**"
The features are scalars, so Galilean invariance is inherited, but no rotational or reflectional
argument is made and no integrity basis is used.

## 2.3 Solver coupling — the distinguishing feature of this class

**In-the-loop and iterative, and the paper says so exactly (arXiv preprint p. 14)**: "the mapping
`beta(eta)` built during the training process is **queried for input features at every iteration of
the flow solver** to obtain outputs which are embedded into the predictive model. **This process is
repeated until convergence.**"

**And the target is a multiplier on an existing production term** — `D nu_tilde/Dt = beta(x) P - D + T`
(Eq. 2, p. 7) — not a stress source. Consequence, measured: "The NN-augmented model displays
**comparable convergence characteristics to the baseline model**" (p. 22), and **no clipping,
under-relaxation, blending or smoothing appears anywhere in the paper.** *It is the only in-the-loop
learned closure in the corpus that needed no stabiliser, and §0.2 explains why.*

## 2.4 Training

Inverse loss `min_beta [(C_l,exp - C_l(beta))^2 + lambda sum (beta(x_n) - 1)^2]` with **Tikhonov
`lambda = 4e-4`**, "insensitive to order of magnitude variations" (p. 9). Optimiser **L-BFGS** with a
discrete adjoint differentiated by **Tapenade**, the adjoint solved by pseudo-time stepping. The
regressor is "**typically 3 layers and about 100 nodes** ... sigmoid ... **FANN**" (p. 13).
**Learning rate, epochs, regularisation and split sizes are not stated.**

**Truth is experimental lift, not DNS.** NREL S805/S809/S814 airfoil reports, `Re = 1e6, 2e6, 3e6`,
with **`Re = 3e6` never in any training set.**

## 2.5 A-priori versus a-posteriori

**A-posteriori only, and in two solvers.** Every reported result is a converged, augmented RANS
solution. The model was additionally embedded in **AcuSolve**, an unstructured commercial
finite-element code, and reproduced the improvement (pp. 20-21).

## 2.6 Strengths

- **It trains from sparse, indirect, experimental data.** A single measured `C_l` per condition is
  enough to infer a full field. Nothing else in the corpus can learn from that little.
- **It is the only demonstrated cross-solver-portable learned closure in the corpus** (§2.5). The
  authors attribute this to local non-dimensionalisation.
- **Cheap at inference: "< 10% of additional compute time compared to the baseline calculation"**
  (p. 22).
- **The augmentation target is chosen for conditioning** (§0.2), and it works.

## 2.7 Weaknesses and failure mechanisms

- **The paper reports no error metric for any flow field.** Its only two numbers are the "<10%"
  overhead and "**the predicted length of the separation bubble was found be 15% more accurate**"
  on the NASA hump (Appendix B, p. 31). Everything else — every `C_l(alpha)`, every `C_p` — is a
  figure. **Do not attach a number to a Singh 2017 accuracy claim.**
- **Training-set sensitivity is the acknowledged soft spot (p. 20)**: "**the quality of the
  NN-augmented model is sensitive to the selection of the training-data. In this work, the best
  model 'P' is selected by exploring several combinations of the data-sets.**" The eight-model
  ensemble of Fig. 18 shows the spread; **the spread is not quantified.**
- **The augmentation is model-specific and term-specific.** It multiplies the SA production term. It
  says nothing about a two-equation model, and nothing about the stress *form*.
- **Adjoints are the barrier.** Duraisamy 2021, p. 12: "**Given the intrusive nature of adjoints,
  this presents major challenges to development, and has proven to be a barrier for researchers to
  develop model-consistent ML augmentations.**"

## 2.8 Flow classes

**Works**: 2-D airfoils through stall, at Reynolds numbers spanning 1e6-3e6, including a `Re` never
trained on, and a separated wall-mounted hump. **Untested**: 3-D, internal flow, secondary flow,
anything without an experimental integral quantity to invert against. **Reproducibility here**:
`FEASIBILITY.md` §1.2 marks it **BLOCKED on data, not on the paper** — no airfoil case with
experimental `C_l` is on disk, and building one is a separate project.

---

# 3. ML-augmented RANS: tensor-basis and symbolic families

Three sub-families that share a target — the Reynolds-stress anisotropy `b` — and differ in the
hypothesis class.

## 3.1 Inputs, features and invariance, side by side

| | Ling 2016 TBNN | Wu 2018 PIML-RF | Kaandorp 2020 TBRF | Schmelzer 2020 SpaRTA |
|---|---|---|---|---|
| **Features** | 5 invariants of `S`, `R` | **50**: 47-invariant minimal integrity basis of `{S, Omega, grad p, grad k}` + 3 scalars | **17**: FS1 (6 invariants of `S`,`R`) + FS2 (10 with `grad k`) + FS3 (9 physical scalars) | **2 invariants only**: `I1 = tr(S^2)`, `I2 = tr(Omega^2)` |
| **Basis** | Pope's **10** tensors, all of them | linear/nonlinear split `b = nu_t^L S + b_perp` | Pope's **10** tensors | Pope's **first 4** tensors only |
| **Normalisation** | `S`, `R` by `k` and `eps` | `alpha_hat = alpha/(\|alpha\| + \|beta\|)` -> every feature in `[-1,1]` | `S`, `R` by `k/eps`; `grad k` by `sqrt(k)/eps` | timescale `tau = 1/omega` |
| **Galilean** | claimed by construction | **claimed and proved** for the `rho\|DU/Dt\|` normaliser (Appendix C) | **output yes; 4 of 9 FS3 features flagged NOT Galilean-invariant** | not claimed |
| **Rotational** | claimed (used interchangeably with Galilean) | claimed | claimed | inherited implicitly |
| **Reflectional** | **not discussed** | **explicitly NOT satisfied** — sacrificed for the quaternion output | **not discussed** | not discussed |

**Three things are worth extracting from that table.**

1. **Kaandorp & Dwight are the only authors who audit their own feature set for invariance and
   report the failures.** Table 1 (arXiv preprint p. 25) marks four of nine FS3 features with a
   dagger: "**Features marked with † are rotationally invariant but not Galilean invariant**" — they
   are `k`, `u_k dp/dx_k`, `u_i dk/dx_i`, and `u_i u_j du_i/dx_j`. Everyone else claims invariance
   for the whole pipeline.
2. **Wu et al. price invariance-by-augmentation and reject it** (arXiv preprint p. 13): reflection
   would be "a **moderate two-fold increase**"; 3-D rotational invariance by augmentation "required
   duplicating the training data in **1000 coordinate systems**".
3. **An invariance defect survived to submission in the paper whose subject is invariance.**
   Wu 2018 Acknowledgment, p. 33: "**one of the reviewers pointed out the lack of Galilean invariance
   in two of the normalization constants in our manuscript, which we fixed during the revision.**"

## 3.2 The result that should govern effort allocation

**Kaandorp & Dwight 2020, Table 3, arXiv preprint p. 37** — square duct `Re = 3500`, `b` RMSE:

| Feature set | TBRF | TBNN |
|---|---|---|
| 5 features (FS1: `S`, `R` only) | 0.0995 | **0.0871** |
| 17 features (FS1+FS2+FS3) | **0.0521** | 0.0681 |

**Adding features cuts TBRF's error by 47.6% and TBNN's by 21.8%. Swapping the model class changes
the winner but not the magnitude.** The authors' own reading (p. 36): "**the introduction of extra
features has significantly more effect than the choice of neural-networks versus random-forests.**"
And the diagnosis of why FS1 is so weak (p. 37): of its five features, "**3 are approximately scaled
versions of the other 2 - effectively reducing the input space to two dimensions**" — which is
Guyon & Elisseeff's §3.2 warning ("**Perfectly correlated variables are truly redundant**",
JMLR 3, p. 1164) measured in a turbulence feature set.

## 3.3 Solver coupling and the stabiliser each family needs

| Method | Coupling | Stabiliser, with its number |
|---|---|---|
| **TBNN** (Ling 2016) | explicit `b` into momentum + `k`-production, SIERRA Fuego | **none discussed**; no conditioning analysis; no realisability enforcement |
| **PIML-RF** (Wu 2018) | **implicit**: `tau^m = nu_t^L S + (tau - tau^L) + tr(tau)`, "**S is treated implicitly**" (Appendix A, p. 35) | **no blending factor used** — the split is offered as the principled alternative to ad-hoc blending |
| **TBRF** (Kaandorp 2020) | explicit `b_ML` blended: `tau = (2/3)kI + 2k[(1-gamma) b^B + gamma b^ML]` | **`gamma_max = 0.8`**, found by "**incrementing in steps of 0.1 until the solver became unstable**" (p. 26); **Gaussian smoothing `sigma = 3` cells**; **median over trees, not mean** |
| **SpaRTA** (Schmelzer 2020) | additive correction to k-omega SST + a `k`-equation residual | **coefficients shrunk by `xi = 0.1` whenever CFD fails to converge** (p. 13) |

**The three TBRF devices are worth stating as mechanisms, because each is a general property of the
regressor and not a tuning accident.**

- **Why smoothing is needed at all (arXiv preprint p. 21, verbatim)**: "**Since the random forest is
  a piecewise constant approximation of `b`, and derivatives of `b` are needed in the N-S equation**,
  the predictions from the TBRF are smoothed spatially with a Gaussian filter ... The TBRF algorithm
  has **no explicit spatial correlation** in the predictions since these are based on local features."
  *A pointwise regressor of any kind produces a field whose derivative is not controlled. This is
  the same wall Wang, Wu & Xiao 2017 hit (arXiv preprint p. 29): "**A small region with abnormal
  Reynolds stress corrections (e.g., non-smoothness or artificial peaks) can introduce large errors
  to the velocity predictions ... These fluctuations, despite being small in amplitude, can lead to
  abnormal behaviors in the divergence term.**"*
- **Why the blending ceiling exists**: "Simply setting the prediction of the anisotropy tensor
  `b_ML` in the momentum equation **adversely affects the numerical stability of the solver**"
  (p. 24) — the explicit-source ill-conditioning of §0.2 — and "**A lower value for `gamma` means
  that the linear eddy viscosity assumption becomes more dominant, resulting in a more stable
  solution, but impairing the accuracy**" (p. 26). **Wu et al. 2019 later state that the local
  condition number is exactly the tool for choosing this factor** (arXiv:1803.05581, pp. 23-24):
  "it is possible to choose **a minimum blending factor that maintains good conditioning**."
- **Why the median and not the mean (p. 57)**: TBRF predicts *coefficients*, not the output, so
  "**the values for the final predictions do not have to lie in-between the values of the points used
  for training** ... this manifested during testing as **highly irregular and inconsistent
  predictions in small regions of the spatial domain**."

## 3.4 Realisability — a structural difference between forests and networks

**Kaandorp 2020, arXiv preprint p. 35, on the same data with the same basis**: "In all our studies,
we have **never observed unrealizable predictions from TBRF, despite no explicit realizability
constraint being imposed on the method**", whereas the TBNN "slightly outperforms, **at the cost of
some unrealizable predictions closest to the wall**".

**The mechanism, stated independently by Sanderse et al. 2024 (arXiv preprint p. 12)**:
"**random-forest predictions are obtained by averaging splits of data that come from the convex hull
of the training data set. As long as the generated training data sets guarantee a particular symmetry
or structure, the prediction of the dependent variable will also satisfy this property by design.**"
With the caveat that follows immediately: "**for complicated properties that emerge from complex
interactions between machine learning predictions and the numerical solver, such an approach may be
incomplete.**"

*Note the tension with §3.3: the same convex-hull property that guarantees realisability for a
standard forest is **broken** by the tensor-basis modification, because TBRF outputs coefficients
rather than the tensor. Kaandorp report both facts — realisability never violated in practice, and
predictions able to leave the training range in principle — three pages apart.*

## 3.5 A-priori versus a-posteriori, per method

| Method | A-priori metric | A-posteriori metric | Gap |
|---|---|---|---|
| Ling 2016 | `b` RMSE, Table I | **none numeric** — vector and contour plots only | Cannot connect the 43% `b` improvement to any flow quantity |
| Wu 2018 | none | **none numeric** — one separation-bubble extent in prose | No error table of any kind exists in the paper |
| Kaandorp 2020 | `b` RMSE, Table 3 | **reattachment `x/h`, Table 4**: RANS 5.45, TBRF **6.32**, DNS 6.28, expt 6.0+/-0.15 | The only a-priori-to-a-posteriori link in the family |
| Schmelzer 2020 | frozen-field MSE, Table 1 | **`eps(U)/eps(U_0)`, Table 2** | Both, on the same normalised metric — the cleanest in the corpus |

**Schmelzer's two tables together give the ceiling and the achievement**, and the gap is the finding:

| Case | Frozen-field ceiling `eps(U)/eps(U_0)` (Table 1, arXiv preprint p. 6) | Best discovered model (Table 2, p. 15) |
|---|---|---|
| PH10595 | **0.00165** | **0.22287** |
| CD12600 | 0.0229 | 0.20828 |
| CBFS13700 | 0.22703 | 0.30655 |

**On periodic hills the extractable correction would reduce the velocity error by a factor of ~600,
and the best sparse symbolic model achieves a factor of ~4.5.** The authors: "This leaves still room
for further improvement compared to the error using the frozen data sets" (p. 20). **On the curved
backward-facing step the ceiling itself is poor (0.227), so the correction *form* — an algebraic
`b^Delta` plus a `k`-residual — is inadequate there regardless of the regression.**

**Kaandorp's propagation ceiling says the same thing differently** (arXiv preprint pp. 39-40):
propagating `b_ij,DNS` itself already misses, and "**Subsequently approximating `b_ij,DNS` by
`b_ij,TBRF` causes additional errors, but these errors are of similar magnitude to the errors already
made in the propagation.**" *The ML error and the propagation error are the same size. Halving the ML
error would buy roughly nothing.*

## 3.6 Strengths

- **The tensor basis is a genuine free lunch on 3-D anisotropy** (§0.1) and it is what makes the
  implicit split of §0.2 available, because the linear coefficient is learned separately
  (Stroefer 2021, arXiv preprint p. 4).
- **Symbolic regression produces models a human can read and a solver can compile.** Schmelzer's
  `M(1)` is four terms (Eq. 25, arXiv preprint p. 21). Model selection costs "of the order of **a
  minute on a standard consumer laptop**" at `K ~ 15000` points (p. 11).
- **Forests are cheap, robust to initialisation, and structurally realisable** (§3.4). Training
  complexity `O(N log^2 N)`; "**Unlike training neural networks, this procedure is fast, robust,
  easy to implement, and independent of any starting guess**" (Kaandorp, p. 56).
- **Kaandorp's BFS reattachment is the corpus's best evidence that a learned anisotropy improves an
  integral quantity**: baseline 13.2% short of DNS, corrected 0.6% beyond it.

## 3.7 Weaknesses and failure mechanisms, each with its evidence

- **Extrapolation fails where the features are unsupported, and the mechanism is nameable.**
  Wang, Wu & Xiao 2017, Scenario II (arXiv preprint p. 26): trained on a wavy channel and a curved
  step, tested on periodic hills, the TKE prediction "**does not show any improvement and even
  deteriorates compared to the baseline** ... near the windward side of the hill (`x/H > 7`)".
  Diagnosis, in the authors' words: "**the flow features in the contraction region are not supported
  in the training set, since the contracted flow does not exist in the training flow CS13200 and is
  much weaker in the training flow WC360.**"
- **The learned function encodes the error of one baseline model.** Wu 2018, p. 15: "**Because of the
  dependence of the trained machine learning function on the RANS model, we recommend the usage of
  the same RANS model for both the training flows and the flow to be predicted.**" Nothing in the
  corpus tests discrepancy transfer across baseline models.
- **`Re` extrapolation is barely tested.** Wu 2018, p. 26: "the test flow is at `Re = 3500`, close
  to that of the training flow (`Re = 2200`). Therefore, the satisfactory predictive capability ...
  **does not necessarily guarantee similar performance at a higher Reynolds number.**" Kaandorp names
  it as future work (p. 44).
- **Model selection touches the answer.** Schmelzer hand-selects 5 `b^Delta` and 3 `R` models from
  52-136 candidates "**in an ad-hoc way**" (p. 15), then runs **35 to 47 CFD simulations per test
  case** and reports the best. The reported `eps(U)/eps(U_0)` numbers are post-selection.
- **Truncation limits the class.** SpaRTA uses **4 of 10 tensors and 2 of 5 invariants** — a
  2-D-complete quadratic form. **No duct case is tested**, and the duct is precisely where the extra
  tensors are needed.
- **The field's own summary**, Wu 2018 p. 31: "**most existing data-driven turbulence models,
  including the one presented in our work, are still in their infancy and have shown only limited
  predictive capabilities, typically in flows that are close to the training flows.**"

## 3.8 Flow classes

| Flow class | Works? | Evidence |
|---|---|---|
| Square duct / secondary flow of the second kind | **Partly.** TBNN improves `b` RMSE 43% but "**is still not able to correctly capture the strength and shape of the corner vortices**" (Ling, p. 13); TBRF at 17 features reaches `b` RMSE 0.0521 | Ling Table I; Kaandorp Table 3 |
| 2-D separation (hills, curved step, BFS) | **Yes, measurably.** `eps(U)/eps(U_0)` down to 0.208-0.306; BFS reattachment 5.45 -> 6.32 against DNS 6.28 | Schmelzer Table 2; Kaandorp Table 4 |
| Geometry transfer at fixed `Re` | **Partly, and it fails in the unsupported region** | Wang/Wu/Xiao Scenario II |
| `Re` extrapolation | **Untested to unknown.** Largest tested step is 2200 -> 125000 against an *experiment*, reported graphically | Wu 2018 Case 2 |
| Unsteady RANS | **No.** "It is **untested for unsteady flows**" | Kaandorp, p. 9 |
| 3-D complex geometry | **No case in the corpus** | — |

---

# 4. End-to-end differentiable and solver-in-the-loop learning

## 4.1 Inputs, features and invariance — the class's weakest axis

| | Stroefer 2021 | Um 2020 | Kochkov 2021 | List 2022 | Sirignano 2020 |
|---|---|---|---|---|---|
| **Inputs** | 5 invariants of the normalised velocity gradient | velocity state (+ marker density; + a constant `Re` field) | velocity field | **velocity and pressure gradient, 4 channels** | velocity + first and unmixed second derivatives at the point and **6 nearest neighbours** |
| **Output** | Pope's **10** `g^(i)` | additive velocity correction | interpolation coefficients (LI) or additive residual (LC) | **corrective forcing field, 2 channels** | `h_theta`, a derivative operator on the network output |
| **Invariance** | **exact, by the tensor basis** | none | none (LI constrains `sum a_i = 1` for **accuracy**, not invariance) | **none — and stated**: "any principles of the modelled physics, like Galilean invariance ..., **must be learnt by the network itself**" (p. 5) | **none — and stated**: "**does not strictly enforce Galilean invariance, but this was not found to be a challenge**" (p. 15) |

**Only one member of this class embeds invariance, and it is the only member that targets a
constitutive relation.** The other four learn a *numerical correction* — a forcing, a flux
interpolation, an additive residual — which is a different object with no invariance requirement of
the same kind. **This is exactly the distinction that makes the §0.1 disagreement between Ling and
Kochkov less contradictory than it looks.**

Sirignano et al. attach a prediction to their own omission (arXiv preprint p. 15): "**The issue of
Galilean invariance should be considered further, especially in regard to further extrapolation from
the training data.**"

## 4.2 Solver coupling — this class *is* its coupling

- **Stroefer 2021**: steady RANS **re-solved to convergence every training step**; continuous adjoint
  for `dJ/dtau`; **implicit `nu_eff = nu - g^(1) k t_tau`** with the nonlinear part explicit
  (Eq. 2.4, arXiv preprint p. 4).
- **Um 2020**: correction applied **after every solver step**, gradients back-propagated through the
  PDE `n-1` times.
- **Kochkov 2021**: network inside the flux computation; **divergence, pressure projection and time
  stepping remain standard numerics**; loss over **32 unrolled steps**.
- **List 2022**: correction injected at **PISO's implicit predictor step**, "so continuity is still
  satisfied".
- **Sirignano 2020**: network inside the discretised PDE; **adjoint PDEs** for the gradient, with a
  stochastic sampling of (case, interval) pairs; **5 LES steps forward, then the adjoint backward**.

## 4.3 Training — the unroll-length question, answered three ways

| Paper | Unrolled steps used | Finding |
|---|---|---|
| Kochkov 2021 | **32** | no sweep reported |
| Um 2020 | 2 to 128 | **monotone improvement** on the wake and buoyancy cases (buoyancy 40% at `n<=4`, 54% at 64, **60% at 128**); **but the optimum is `n = 2` on the randomly forced Burgers case** |
| List 2022 | 1, 10, 30, 60, 120 (and 180, 240 explored) | **60 helps; 120 gives no improvement; 180 and 240 reduce accuracy** |

**And List separates two lengths that everyone else conflates: how far you roll forward, and how far
the gradient travels.** Their §6 (arXiv preprint p. 22), on a 60-step rollout:

| Gradient sub-range | TML MSE @ 512 dt | SML MSE @ 1000 dt |
|---|---|---|
| 10 | 2.36e-5 | **2.44e-3** |
| 20 | 2.19e-5 | 2.73e-3 |
| 30 | **1.93e-5** | 2.98e-3 |
| **60 (full)** | **training unstable — no value** | **1.19e-2** |

**Full 60-step back-propagation is training-unstable on one case and ~4x worse on the other** (and
1.19e-2 is barely better than the no-model 2.03e-2). Optimum **20-30 steps**, with saturation "at
**circa 60 steps, which coincides with the integral timescales**" (p. 24). **Explicitly contrasted
with the standard remedy (p. 28): "This approach differs from the common practice in machine
learning, where gradients of early evaluations ... are usually discarded or re-scaled when gradient
clipping is applied." No gradient clipping is used.**

**Sanderse et al. 2024 state the general form of the trade-off (arXiv preprint p. 8)**: "**Unrolling
too few time steps gives only limited gains over a priori learning, while unrolling too many time
steps is computationally expensive, has the danger of exploding or vanishing gradients, and can be
unrealistic given that turbulent flows are chaotic.**"

**And the curriculum that makes long unrolls trainable (Um 2020, arXiv preprint p. 8, verbatim)**:
"Especially during the early stages of training, an inferred correction can overly distort the
physical state. Performing time integration via the PDE then typically leads to **exponential
increases of existing oscillations and a diverging calculation**. Hence, we found it important to
**pre-train networks with small look-aheads (we usually use SOL_2 models), and then continue training
with longer recurrent iterations**." Both Um (SOL_8 for 200k iterations, then SOL_16 for 100k) and
List ("models trained on more than 10 steps were initialised from a pre-trained 10-step model") use
it.

## 4.4 A-priori versus a-posteriori

**This class is a-posteriori by construction.** Its distinctive evidence is what happens to the
a-priori alternative under identical conditions — the three controlled experiments of §0.3.

## 4.5 Strengths

- **It is the only class with demonstrated long-horizon stability where the supervised alternative
  has none.** Um 2020, 3-D wake: "we were **not able to train a stable NON version despite numerous
  tests**"; SOL_16 "**retains its stability over the course of long simulations with several hundred
  steps**" (arXiv preprint p. 33).
- **It absorbs discretisation error, which the a-priori target cannot represent.** Sirignano's
  Table 1 (arXiv preprint p. 11) measures how big that error is: at `Delta/dx_dns = 32` with implicit
  filtering, the LES-versus-DNS velocity-gradient error is **1.076 times the mean velocity-gradient
  magnitude** — larger than the quantity itself.
- **Large, measured speed-ups.** Kochkov **40-80x**; Um **68x** on the 3-D wake at inference; List
  **3.3-14.4x**; Sirignano **~4x to ~20x** per step at comparable accuracy.
- **Generalisation across `Re` is unusually good and repeatedly measured.** Um: "**Despite a factor
  of 16 between the Reynolds numbers, there is no significant decrease in performance**". Kochkov:
  the `Re = 1000` model reused at `Re = 4000` by halving the grid spacing still gives **7x** effective
  resolution.

## 4.6 Weaknesses and failure mechanisms

- **`FLAG F6` — the headline speed-up depends on the baseline solver's order, and the two headline
  numbers in this class are not comparable.** Kochkov: **8-10x coarsening / 40-80x speed-up** on a
  **first-order-in-time explicit Euler** solver. List: **~2-4x effective resolution / 3.3-14.4x
  speed-up** on a **second-order PISO** solver, with the authors' own explanation (arXiv preprint
  p. 27): "**While other works have reported even larger performance improvements [Kochkov et al.,
  2021], we believe that our measurements are representative of real-world scenarios with
  higher-order solvers.**" **Never quote the two side by side without the solver order.**
- **Training cost is the real price, and List is the only paper that states it in a comparable unit**
  (arXiv preprint pp. 26-27): **61 h, 78 h and 240 h on one GTX 1080Ti**, equal to
  **[120, 118, 22] full-length DNS solves**. *The model must be re-used 22-120 times to repay its own
  training.*
- **The learned correction is locked to its grid and time step.** Sanderse et al., arXiv preprint
  p. 8: "**The approach implicitly corrects for spatial and/or temporal discretization errors, which
  can be desirable but can also limit application to different grids or time steps.**" Every paper in
  this class uses exactly one coarsening ratio throughout.
- **Predictability sets the useful horizon.** Um 2020, p. 6: "**The randomized forcing in this
  example severely limits the number of future steps that can accurately be predicted given one
  state.**" Their forced-Burgers optimum is `n = 2`.
- **Distribution shift kills it when it kills it.** Um 2020, p. 33: "**once the phase space
  trajectories produced by the hybrid method leave the distribution of the regular source states seen
  at training time, the model fails to infer reasonable corrections.**"
- **The gradient may be deliberately inexact.** Stroefer 2021 deletes the adjoint transpose
  convection term because it "**can result in instabilities**" under SIMPLE (arXiv preprint p. 5).
- **Random initialisation diverges the solver.** Stroefer 2021, p. 5: "**The usual practice of random
  initialisation of the weights is not suitable in this case since it leads to divergence of the RANS
  solution.**" Fixed by pre-training to an existing closure, with noise added to the pre-training
  data.
- **Adjoints of chaotic systems are themselves unstable.** Duraisamy 2021, p. 13: "**chaoticity can
  lead to unstable adjoint solutions that require special treatment.**"
- **Identifiability bounds what indirect training can learn.** Stroefer 2021, arXiv preprint p. 8:
  only two combinations of the duct's coefficients are recoverable from velocity data, because "the
  velocity field is expected to be **less sensitive to the value of the Reynolds stress** in these
  regions"; and "**The trained model fails to predict the correct `tau_yz` in the center channel, but
  this does not propagate to the predicted velocities.**" Getting the flow right and getting the
  model right are different objectives, and the paper prices the difference: **"a few tens of
  training steps" for the velocity versus "1-2 orders of magnitude more training steps" for the
  coefficients** (p. 8).
- **Reynolds numbers in this class are low.** Um: `Re <= 3125` (2-D), `<= 625` (3-D). List:
  `Re = 126-500`. Kochkov: `Re = 1000-4000` plus one LES case at `1e5` whose *ground truth is a
  Smagorinsky model*, not DNS.

## 4.7 Flow classes

| Flow class | Works? | Evidence |
|---|---|---|
| 2-D forced/decaying turbulence | **Yes** | Kochkov 8-10x; List IDT MSE 0.057 -> 0.018 |
| 2-D mixing layers | **Yes, an order of magnitude** | List TML 64.8x, SML 6.8x versus no model |
| 3-D wake, laminar-transitional | **Yes, modestly (22%)**, and it is the only stable option | Um Table 6 |
| Randomly forced systems | **Poorly — long unrolls stop helping** | Um Burgers, optimum `n = 2` |
| Steady RANS from indirect data | **Recovers a known closure; degrades toward stronger separation** | Stroefer `alpha` sweep |
| Engineering `Re` | **No case in the corpus** | — |
| Non-Cartesian grids | **No.** "our tests have focused on regular, Cartesian grids" | List, p. 28 |

---

# 5. Model-form UQ: eigenspace perturbation and Bayesian/EnKF

## 5.1 Two sub-families, one of them unreadable here

- **Eigenspace / eigenvalue perturbation** (Emory 2013; Iaccarino 2017) — **both
  `WRONG-QUARANTINED`.** The method is described only through Duraisamy et al. 2019 (arXiv preprint
  Eq. 10, p. 9): `tau = tau^RANS + delta_tau = 2k(I/3 + V Lambda V^T)` with
  `Lambda = Lambda^RANS + delta_lambda`, perturbing toward the 1C/2C/3C corners of the barycentric
  triangle. **No training, no ML, and `FEASIBILITY.md` §1.2 prices the frozen-field envelope check at
  < 1 core-hour.** No numbers are quoted here because no verified PDF exists.
- **Bayesian / ensemble-Kalman inference** (Xiao 2016) — on disk.

## 5.2 Inputs, features, invariance — Xiao 2016

**There are no ML features.** The inference is over Karhunen-Loeve coefficients of discrepancy random
fields, not a regression on flow features.

**Invariance is handled by choosing what to perturb**: `tau` is eigen-decomposed into magnitude `k`,
shape `(xi, eta)` in the barycentric map, and orientation `(v1, v2, v3)`, and **uncertainty is
injected into the invariants only**. **Realisability is enforced by clipping** `(xi, eta)` to the
square `[-1,1]^2` — and the authors state the cost (arXiv preprint pp. 9-10): "**admittedly an ad hoc
modeling choice. As a result, the prior may become non-Gaussian and the perturbation sample may
deviate from zero-mean if a large number of perturbations are bounded.**"

**And the orientation is left unperturbed for a numerics reason, with an epistemic consequence the
authors spell out (arXiv preprint p. 10, verbatim)**: "**Perturbing the orientations of the modeled
Reynolds stress tensor can potentially cause instability in the RANS momentum equation** ...
Consequently, **the assumed uncertainty space of Reynolds stresses may not contain the truth** because
the true Reynolds stresses are likely to have different orientations from those of the RANS
predictions."

*That is the cleanest example in the corpus of a numerical constraint determining an epistemic one:
a stability concern provably excludes the answer from the search space. And the missing eigenvector
axis is exactly what Iaccarino 2017 adds — the half of the loop the corpus cannot read.*

## 5.3 Solver coupling and training

**In-the-loop, iterative, re-solving.** Each of ~10 iterations reconstructs `tau` from the KL
coefficients, **re-solves the RANS momentum equations with `tau` prescribed** (`tauFoam`, no
turbulence model solved), and Kalman-updates against sparse velocity observations.

**Sizing rules, all stated with numbers (Table 1, arXiv preprint p. 21; pp. 19-20)**:
**ensemble `N = 60`** ("the inferred velocities and QoIs **do not vary if more than 30 samples are
used**"); **`m = 16` KL modes** per field for the hills, **8** for the duct, chosen so "the
reconstructed field has **at least 80% of the total variance**"; observation noise **`sigma_obs` =
10% of truth**, with the floor "**As long as the chosen noise level is larger than a threshold (1% of
truth), the inferred posterior means are not sensitive to this parameter**"; and convergence when
"the two-norm of the misfit ... falls below the noise level of the observations".

**Cost, stated exactly (§5.1, arXiv preprint p. 40)**: **600 forward RANS evaluations per case**,
each "**only 10% as expensive as a baseline RANS simulation**", giving "**the total computational
cost ... 60 times as that of the baseline simulation**" — and on 60 cores, "the wall time ... is
approximately the same as that of the baseline simulation ... run on a single core."

## 5.4 A-priori versus a-posteriori

**Every ensemble member is re-solved, so the method is a-posteriori by construction — but there is
no held-out predictive test in this paper.** It is calibration on the same case; generalisation is
deferred to a companion paper (p. 44).

## 5.5 Strengths

- **It produces a distribution, not a point.** Nothing else in this document does.
- **It works from very sparse data**: 18 observation points on the hills, 13 effective on the duct.
- **It is measured in a currency a lab can plan against**: 60 baseline-solve-equivalents per case.
- **Realisability is guaranteed by the parameterisation**, not hoped for.

## 5.6 Weaknesses and failure mechanisms

- **The inferred stress field is not accurate, and the authors lead with it (arXiv preprint p. 45)**:
  "**A notable limitation is that the full Reynolds stress field inferred from this method is not
  accurate.** This is attributed to the high dimension of the Reynolds stress uncertainty space, the
  sparseness of the velocity observation data, and the **nonlinear, possibly even non-unique, mapping
  between the Reynolds stresses and velocities.**" And p. 42: "**the posterior mean of an arbitrarily
  chosen component or projection of the Reynolds stresses is not significantly more accurate than
  those of the baseline prediction.**" **Mechanism**: only `div tau` enters the momentum equation, and
  extracting `tau_yy - tau_zz` is "a linear mapping described by a **rank deficient matrix**".
  *This is the same identifiability wall Stroefer 2021 hit from the other direction (§4.6).*
- **The intervals are too narrow, and they know it (p. 28)**: "**the 95% credible intervals ... failed
  to cover the truth**, which indicates that the current method should still be used with caution
  when making high-consequence decisions. **The iterative ensemble Kalman method tends to
  underestimate uncertainties in the posterior distributions.**"
- **Two defects push the same way.** The truth may lie outside the search space (§5.2) *and* the
  posterior is over-confident (above). **Both errors are in the direction of overconfidence.**
- **It gets worse in the regions with no data**: "in the immediate vicinity of the hill crest ... the
  posterior ensemble is **similar to or even slightly deteriorated compared to the baseline**"
  (p. 27), and "the posterior credible interval **does not improve or even deteriorate compared to
  the prior**" between `0 < x/H < 1` and `8 < x/H < 9` (p. 28). TKE is "**not necessarily better than
  the baseline results at all locations**".
- **The prior is hand-designed** — `sigma_0 = 0.2` everywhere plus `sigma_local = 0.5` at four
  hand-picked locations on the hills and one on the duct. The result is not separable from that
  judgement, and no sensitivity to the placement is reported.
- **No error metric for any flow field exists in the paper.** The only quantitative performance
  numbers are the cost ratios.

## 5.7 Flow classes

**Tested**: periodic hills `Re_b = 2800`, square duct `Re_b = 10320` — both canonical, both low `Re`,
both with a homogeneous direction. **Untested**: everything else, and the authors are explicit
(p. 44): "**extreme caution must be exercised** ... even a slight change of Reynolds number can lead
to significant changes of flow characteristics. **Ultimately, the use of this assumption has to be
the judgment of the user, which is clearly undesirable.**" And: "**Prediction of flows in a different
geometry ... has achieved less successes.**"

---

# 6. Multi-model aggregation

## 6.1 What it is, and what makes it different

**de Zordo-Banliat 2023 (XMA)**: a **per-cell convex combination** of `N_M = 4` independently
converged RANS solutions, `delta(eta*) = sum_m w_m(eta*) delta^(m)(eta*)`, with weights from an
**exponentially weighted average cost** `g_m = exp(-0.5 (delta^(m) - delta_d)^2/sigma^2)` regressed
over a **10-dimensional feature space by random forests**.

**It is the only class that does not modify a turbulence model at all.** It runs four of them and
decides, per cell, whom to believe.

## 6.2 Inputs, features, invariance

**10 features**, a subset of Ling & Templeton's, computed **from each model's own solution** —
`w_m = w_m(eta^(m))`, a per-model feature set. **Invariance is not discussed anywhere.** A notable
practical consequence (arXiv preprint p. 10): "**Spalart-Allmaras ... do[es] not provide estimates of
the turbulent kinetic energy `k`. In such cases, the feature is simply excluded from
considerations.**" *The feature vector differs in dimension between component models.*

## 6.3 Solver coupling, training, inference

**No coupling at all.** This is post-processing of converged steady solutions; there is no time
integration, no re-solve, no divergence risk. The only clipping analogue is a cost-function floor:
if all `g_m < C` at a point, the weights revert to uniform `1/4`, with `C = 0.001` retained after a
sensitivity sweep over `[0.001, 0.15]`.

**Training**: 300 trees per model (4 regressors), grid search with 10-fold cross-validation.
**Data**: "big" = **40,080 points** (all mesh nodes, one scenario) versus "small" = **820 points**
(1 node in 8 per direction). Observed quantity: **total pressure only**.

## 6.4 A-priori versus a-posteriori

**Neither, in the usual sense** — the component solutions are already a-posteriori, and the
aggregation never re-enters a solver.

## 6.5 Strengths

- **Cheap and safe.** "**XMA prevents catastrophic loss of accuracy** with respect to the
  common-practice choice of a single (possibly wrong) RANS model" (arXiv preprint pp. 17-18).
- **The scarce-data regime suffices**: "**XMA_1 and XMA_2 lead to similar MSE on average, showing
  that the scarce data regime is already sufficient to properly inform the mixture**" (p. 23).
  **820 points from one scenario.**
- **The weights are a built-in out-of-distribution alarm.** On the extrapolation scenario they become
  "**less sharp** ... i.e. the models are weighted more uniformly" (p. 22) — the method announces its
  own uncertainty about model choice without being asked.
- **It reuses existing, uncalibrated, shipped turbulence models.** No new model is trained.

## 6.6 Weaknesses and failure mechanisms

- **`FLAG F5` — the structural ceiling, and it is provable, not empirical (arXiv preprint p. 17,
  verbatim)**: "In the upper part of the wake, **all models exhibit relative consensus on the wrong
  solution, a known limitation inherent to mixture models.** In such a case, the variances (a measure
  of model consensus) are also small and **do not encompass the reference** either." **A convex
  combination cannot leave the convex hull of its components. When all four are wrong the same way,
  the aggregate is wrong and confident.**
- **The variance is not a credible interval and the authors forbid reading it as one (p. 19)**:
  "**the error bars must not be interpreted as the region where the true solution possibly lies, but
  simply as a measure of the uncertainty in the choice of a best-performing model.**"
- **`FLAG F5` — the "truth" is synthetic.** It is an EARSM k-kL field, not DNS or LES, because "**only
  limited results from those datasets are publicly accessible**" (p. 13). **Every accuracy claim is
  agreement with a fifth RANS model.**
- **`FLAG F5` — one number exists in the whole paper**: on the S1 extrapolation, "**the MSE for the
  velocity is reduced by approximately 1/3 with respect to the best-performing baseline RANS
  model**" (p. 23). Figs. 8 and 13 are normalised bar charts with no printed values.
- **It loses on a quantity it was not trained on**: for skin friction "XMA performs worse than
  k-omega" (p. 20) — the weights were informed by total pressure only.

## 6.7 Flow classes

**Tested**: one geometry (NACA 65 V103-220 compressor cascade), four incidences, `Re_1 ~ 3e5`.
**Extrapolation axis**: incidence only. **Untested**: everything else. **Reproducibility here is
unusually attractive**: `FEASIBILITY.md` §1.2 rates the required 4-model solve sweep at **~50
core-hours** and notes it is independently useful as an extension of `BASELINES.md` — and this lab
has **real LES/DNS truth on disk**, so a reproduction would be a strictly stronger experiment than
the paper's.

---

# 7. Learned LES subgrid-scale closures

## 7.1 Inputs, features, invariance

| | Maulik & San 2017 | Maulik 2019 | Beck 2019 | Sirignano 2020 | Guan 2022 |
|---|---|---|---|---|---|
| **Input** | 9-pt (2-D) / 27-pt (3-D) stencil of the perturbed coarse field | **20-D**: 9-pt `omega_bar` + 9-pt `psi_bar` + `\|S_bar\|` + `\|grad omega_bar\|` | `6 x 6^3` = coarse velocities + **the known coarse-grid operator** | velocity + 1st and unmixed 2nd derivatives at the point and 6 neighbours | **the entire `256^2` field** of `(psi_bar, omega_bar)` |
| **Output** | deconvolved field, then `tau_ij` | scalar SGS vorticity source `Pi` | the 3 momentum closure terms | `h_theta` | full-field `Pi` |
| **Normalisation** | to `[-1,1]` for the Tan-Sigmoid | **none** — "no further pre-processing is utilized" | LGL-quadrature-weighted loss | one constant set for all cases | divide by `sigma` of each field |
| **Invariance** | **none claimed** | **none** — "network-embedded symmetry-considerations are ... a future enhancement" | not claimed | **explicitly not enforced** | **none claimed**; symmetry augmentation is future work |

**Not one learned SGS closure in the corpus embeds an invariance.** Where the RANS family has the
Pope basis, the LES family has nothing equivalent in use — and every author lists it as future work.

**Beck 2019's input choice is the exception worth copying**: it feeds in **the known coarse-grid
operator `R_tilde(F(U_bar))`** alongside the velocities. Table 1 (arXiv preprint p. 11) shows why —
raw velocity correlates with the target at **-0.012**, the coarse operator at **0.189**. The feature
ablation (Table 5, p. 21) shows neither alone reaches the pair (0.3665 velocity-only, 0.3358
operator-only, **0.4706** both).

## 7.2 Solver coupling, and the stabiliser each one needs

**This is the sharpest table in this document, because five papers hit the same instability and each
fixed it a different way.**

| Paper | Coupling | Stabiliser | Its size |
|---|---|---|---|
| **Maulik & San 2017** | **none — a-priori only** | n/a | The deconvolved field never enters a solver |
| **Maulik 2019** | in-the-loop, pointwise, every step | **hardwired sign truncation**: `Pi = 0` wherever `(grad^2 omega_bar)(Pi_tilde) <= 0` | "**roughly half of the predicted sub-grid terms are truncated**" (p. 11) |
| **Beck 2019** | direct closure **is unstable**; deployed instead as a projected eddy viscosity | **least-squares projection onto an eddy-viscosity basis, every step and every point**, with limiter | `mu_ANN in [-mu_0, 20 mu_0]` |
| **Sirignano 2020** | inside the PDE, adjoint-trained | **none — "No stabilizing limiters were used"** | but requires **`N_H >= 50`** (div-free) or **`>= 100`** hidden units for long-time stability |
| **Guan 2022** | in-the-loop, frozen network | **none — no clipping, no smoothing, no added eddy viscosity** | requires **`n_tr >= 30,000`** training samples |

**Beck 2019 is the cleanest statement of the underlying problem (arXiv preprint pp. 22-23).** Even
though the learned closure is net dissipative — the relative energy-contribution error is positive
and `O(1e-1)` for every network — the direct closure "**lack[s] long-term stability as high frequency
errors accumulate**", and reducing the time step does not help: at **CFL = 0.5, 0.05 and 0.005**,
"**stability issues ensued even for very small timesteps**". The structural reason is that in the
perfect-LES formulation the coarse-grid inviscid operator **cancels exactly**, so an approximate
learned term leaves **no stable numerical operator behind it**. *The fix is not a better network; it
is a different mathematical object.*

**And Maulik 2019 states plainly what its truncation costs**: it "**precludes the presence of a
backscatter of enstrophy** for strict adherence to viscous stability requirements on the
coarse-grained mesh" (p. 11). **Zeroing half the predictions on a sign test converts a learned
closure into a positive-definite eddy viscosity with a learned magnitude — i.e. into the thing it was
meant to improve on.**

**Guan 2022 measures exactly that trade.** Table 1 (arXiv preprint p. 11), a-priori correlation on
backscatter points: **DSMAG with positive clipping = 0 exactly; ANN with the same sign-truncation =
0.83; CNN with no clipping = 0.92**. And the controlled demonstration (Fig. 8, p. 17): applying the
truncation rule to the CNN makes it "**excessively diffusive (with performance comparable to that of
the LES-DSMAG)**". **The learned advantage *is* the backscatter, and clipping removes it.**

## 7.3 A-priori versus a-posteriori — the class's defining evidence

| Paper | A-priori | A-posteriori | The gap, as the authors state it |
|---|---|---|---|
| Maulik & San 2017 | 6 tables of MSE | **none — never coupled to a solver** | "**A natural follow-up ... is to test our proposed approach in a fully a-posteriori analysis**" (p. 26) |
| Maulik 2019 | PDF comparison | in-the-loop to `t = 4` and `t = 6` | "**Again, the a-priori mean-squared-error is not indicative of the quality of a-posteriori prediction**" (p. 19) |
| Beck 2019 | `CC` up to **0.477** (0.767 inner) | **none numeric — graphical only** | "**it is unrealistic to assume that the learned terms can provide an accurate and stable closure**" (p. 22) |
| Sirignano 2020 | one comparison run | adjoint-trained by construction | "**Figure 7 shows the poor predictive performance of the a priori-trained ... model**" (p. 19) |
| Guan 2022 | `c` = 0.78 to 0.93 | 150 `tau` from 5 ICs | "**there is no established a priori metric and threshold**" (p. 13) |

**Maulik 2019's three ablations are the best-controlled demonstration in the corpus that a-priori
loss is uninformative (arXiv preprint §5, pp. 16-19):**
1. **Removing the two eddy-viscosity kernels** (20 inputs -> 18) leaves the training loss "more or
   less" unchanged, and a-posteriori produces "**unconstrained behavior at the larger scales with the
   formation of non-physical large scale structures**".
2. **The grid-search-optimal 2-layer network is beaten a-posteriori by a 5-layer network the search
   had rejected** — "**This despite the fact that the deeper network displays a great[er]
   mean-squared-error during the training phase (which was the root-cause of it being deemed
   ineligible in the hyper-parameter tuning).**"
3. **A reduced 5-point stencil**: "**While training errors are more or less similar, the reduced
   stencil fails** to capture the nonlinear relationship between the resolved and cut-off scales."

**In all three, the training loss is flat and the deployment behaviour changes qualitatively. A
hyper-parameter search scored on training MSE selected the wrong architecture.**

## 7.4 Strengths

- **The a-priori ceiling is high.** Beck 2019 reaches `CC ~ 0.73` on inner elements; Beck & Kurz 2021
  report a GRU at **99.9%**; Guan 2022 reaches **0.93**.
- **Where it is trained through the solver, it beats the classical models.** Sirignano 2020: "**the
  DPM outperforms the widely-used Smagorinsky model, whether the coefficient is determined
  dynamically or fixed at `C_S = 0.18`**" — though **no percentage exists** (`FLAG F9`).
- **Guan 2022's transfer learning is the cheapest generalisation result in the corpus**: freeze 8 of
  10 convolutional layers, re-train 2 with **500 samples = 1% of the training set**, and reach
  accuracy "**as good as**" a model trained from scratch at **4x, 8x and 16x** the training `Re`.
- **Sirignano's inference cost is competitive**: DPM at `64^3` on one K20X is **1.60 s/step** versus
  Smagorinsky at `128^3` on 16 cores at **6.47 s/step** for comparable accuracy — "approximately
  **one-quarter** the cost".

## 7.5 Weaknesses and failure mechanisms

- **The class routinely loses to its own classical baselines on the quantity that matters.**
  Maulik & San 2017, Table 4 (arXiv preprint p. 17), Kolmogorov subfilter-stress MSE (`x 1e-5`):
  **ANN 8.00 / 3.60 / 3.51 / 7.77 / 3.64 / 6.82** versus **AD3 (3-step approximate deconvolution)
  2.46 / 1.69 / 1.82 / 2.46 / 1.83 / 2.91** — AD3 wins **every component by ~3x**. And on the
  stratified case (Table 6, p. 25), plain **scale similarity beats the ANN on five of six
  components.** The authors concede it (p. 16).
- **`FLAG F9` / `F10` — a-posteriori error metrics are largely absent.** Sirignano 2020 has **no
  percentage error reductions anywhere** (a full `%` search returns three hits, none of them
  results). Beck 2019 has **no a-posteriori error metric, no parameter count and no numeric learning
  rate**. Maulik 2019 has **zero tables** — the string "Table" does not appear in it. Guan 2022's
  a-posteriori results and all transfer-learning results are **figure-only**.
- **Stability is bought, and each currency has a price**: clipping costs backscatter (Maulik 2019,
  Guan 2022's controlled test); projection costs the learned structure (Beck 2019); capacity costs
  compute (Sirignano's `N_H >= 50`); data costs 30,000 samples (Guan 2022).
- **Everything is isotropic or two-dimensional.** Beck and Sirignano are decaying HIT; both Mauliks
  and Guan are 2-D. **`_WRONG_RETRIEVALS/Park2021_neural_les.pdf` — the wall-bounded channel case — is
  `WRONG-QUARANTINED`, so the corpus contains no learned SGS closure in a wall-bounded flow.**
- **The closure absorbs the discretisation, so it does not port.** Sirignano's Table 1 measures the
  discretisation error at `Delta/dx = 32` as **larger than the mean velocity gradient itself**.
  Guan 2022's network takes the whole `256^2` field as input and needed an encoder-decoder wrapper
  just to run at `512^2`.
- **Data cost is severe.** Beck 2019, Remark I (p. 7): storing `U` and `R(F(U))` for `0.2 T*` needs
  **~55 TByte**. Their own conclusion (p. 24): "**the performance of the prediction is likely limited
  by the available amount of data used for training, rather than network architectures.**"

## 7.6 Flow classes

| Flow class | Works? | Evidence |
|---|---|---|
| Decaying homogeneous isotropic turbulence | **A-priori yes; a-posteriori only after projection** | Beck 2019 `CC` 0.477/0.767; instability at all CFL |
| Decaying isotropic, adjoint-trained | **Yes, beats both Smagorinsky variants** — no number | Sirignano Figs. 5-8 |
| 2-D Kraichnan turbulence | **Yes, with truncation or with enough data** | Maulik 2019; Guan 2022 Table 2 |
| 3-D subfilter stress, a-priori | **No — loses to AD3 and often to scale similarity** | Maulik & San Tables 4, 6 |
| Wall-bounded LES | **No case on disk** | Park & Choi 2021 quarantined |
| Compressible / stratified | **Tested a-priori only, and it loses to AD3** | Maulik & San Table 6 |

---

# 8. Learned wall models

## 8.1 The constraint every wall model must satisfy first

**Before any learned wall model is assessed, Larsson et al. 2016 sets the acceptance criterion, and
it is a statement about numerics, not modelling (`FLAG F11`).**

With a kinematic wall-damping constant `C_2 <~ 2` and a Nyquist requirement `N >~ 2`, their grid
criterion `dx_i <~ (C_i/N) y` gives `C_2/N < 1`, so it is "**violated in the first LES grid-point,
regardless of numerical accuracy in the LES**" (PDF p. 11). Consequence, in the authors' own
exclamation: "**even a 'perfect' wall-model in one numerical code would suffer from a log-layer
mismatch if implemented in a different numerical code!**"

**The sign is set by the host code** (PDF p. 10): negative mismatch "generally ... for incompressible
flow solved using a staggered grid", positive for "codes using a colocated grid and/or some degree of
numerical dissipation".

**The fix, with thresholds** (PDF p. 11): hold `h_wm ~ 0.2 delta` **independently of the grid**, then
refine — **converged results have zero log-layer mismatch** at `dy <~ 0.33 h_wm` and
`dx ~ dz <~ 0.8 h_wm` (6th-order compact), independently confirmed at `dx <~ 0.6`, `dy <~ 0.3`,
`dz <~ 0.4 h_wm` by a very different method.

**And the trap (PDF p. 18)**: "the results in Fig. 5 are best (smallest log-layer mismatch) for the
**coarsest** grid", and "**a flawed model may produce 'perfect' results by introducing errors that
exactly cancel those present in the outer layer LES. For example, since most codes/numerics produce a
positive log-layer mismatch, any modeling modification that by itself would produce a negative
mismatch will lead to 'improved' results.**"

**`FEASIBILITY.md` §1.5 turns this into a lab rule: any wall-model comparison here that does not hold
`h_wm` fixed and show grid convergence at `h_wm` measures the code, not the model.**

**And the accuracy target, from Piomelli & Balaras 2002 (Annu. Rev. Fluid Mech. 34, p. 370)**: "the
mean skin-friction coefficient must be predicted accurately, perhaps **within 5%** of resolved
calculations", immediately followed by "**Present models do not satisfy these requirements.**"

## 8.2 Inputs, features, invariance

| | Bae 2022 (SciMARL) | Lozano-Duran 2023 (BFWM) |
|---|---|---|
| **State / input** | **VWM**: `u*`, `du*/dy*`, `y*` at `h_m`. **LLWM**: `1/kappa_m`, `B_m` — a log-law slope and intercept | **6 non-dimensional groups from a two-point wall-normal stencil**: `u1 y1/nu`, `u2 y2/nu`, `gamma_12`, `a1 y1^3/nu^2`, `gammadot_1 y1^2/nu`, `k1/k_m1` |
| **Non-dimensionalisation** | by `nu` and the **modelled** instantaneous friction velocity — no a-priori knowledge of the true `u_tau` | by `nu`, `y1`, `mu`, and an exponential time average for `k1/k_m1` |
| **Output** | bounded multiplier `a_n in [0.9, 1.1]` on `tau_w` | `tau_w y1/(mu u1)`, `gamma_1w`, 7 class probabilities, and a **confidence score** |
| **Invariance** | not discussed | not discussed; **data augmented by rotating the mean-flow direction in 5-degree steps from -45 to +45 deg** |

**The one result on this axis is Bae 2022's, and it is about state variables, not architecture
(arXiv preprint p. 7).** Same network, same reward, same solver, two state spaces:
- **LLWM** — a log-law slope and intercept, **dimensionless and `Re`-free by construction** —
  extrapolates from a training set of `Re_tau in {2000, 4200, 8000}` to **`Re_tau = 1e6`**, a factor
  of **125**, with "the prediction error in the friction velocity ... **less than 4%**".
- **VWM** — whose state carries `(h_m)+` explicitly, trained over `150 < (h_m)+ < 1200` — fails once
  `(h_m)+` leaves that band: "Cases at `Re_tau = 2e4` and `5e4` produce high errors as the `(h_m)+`
  is not within the trained range", and refining the grid to bring `(h_m)+` back into the band makes
  "**errors decrease significantly**".
**Two velocity profiles are omitted from Fig. 4(a) because they lie outside the plotted range.**

*Choosing a state variable that is invariant to the quantity you want to extrapolate over is worth
more than any architecture choice in this document.*

## 8.3 Solver coupling and training

- **Bae 2022**: **RL in the loop — each RL step is a WMLES time step.** `tau_w` enters as a **wall
  eddy viscosity** boundary condition `nu_t|_w = (du/dy|_w)^-1 (tau_w^m/rho) - nu` (Eq. 9), "chosen
  over a Neumann BC **to reduce log-layer mismatch**". Reward = incremental improvement plus a bonus
  for being within **1%** of the true mean wall stress; **no DNS data is needed for training.**
  V-RACER + ReF-ER, `gamma = 0.995`, Adam `1e-5`, batch 512, replay `1e6`, **`1e7` policy-gradient
  steps**, policy net 2 x 128 with softsign and skip connections.
- **Lozano-Duran 2023**: **supervised, frozen, applied as a wall-flux boundary condition** — but the
  training data are **not filtered DNS**. They are generated by E-WMLES in the same solver (charLES),
  so **the solver's own numerical and gridding errors are deliberately learned**. Classifier trained
  by BFGS; predictors by Bayesian-regularization backpropagation; **80/20 split where the test set
  holds entire cases at unseen `Re` and `Pi`**; **~12 h per ANN on 4x A100**.

## 8.4 A-priori versus a-posteriori

**Both papers are a-posteriori throughout** — every reported result is a WMLES run. Bae's channel
tests run **300 `delta/u_tau`**, 150x the training window, with no reported instability; the boundary
layer runs 50 washout times. **Lozano-Duran's a-posteriori run durations are never stated.**

## 8.5 Strengths

- **Bae's cost argument is the strongest in the corpus for reward-based over label-based training**
  (arXiv preprint p. 10): the LLWM at `Re_tau = 4200` trained with **`O(1e3)` CPU-hours and < 1 GB**;
  generating the equivalent DNS would need **`O(1e7)` CPU-hours and > 100 TB**. **Four orders of
  magnitude.** Inference is "an **order of magnitude faster** than the EQWM that solves an ODE at each
  time step".
- **Bae's learned model is structurally right where the classical one is structurally wrong**: the
  wall-stress fluctuation cross-correlation is **~0.3, matching DNS's 0.3**, while "**the EQWM is
  perfectly correlated**" (coefficient 1) by construction.
- **Lozano-Duran's internal/total error split is a genuine methodological advance** — it separates
  the wall model's own error from the SGS model's, and the numbers show why that matters (§8.6).
- **The confidence score is a working OOD detector.** At the NASA Juncture trailing edge it collapses
  to **22%**, and the diagnosed cause is a grid fact: the separation bubble is `0.3 delta` thick
  against `Delta ~ 0.2 delta`, i.e. "**only one grid point across the separation bubble**".
- **Overhead is small and measured**: BFWM is **1.1 to 1.3x** the cost of the algebraic EQWM.

## 8.6 Weaknesses and failure mechanisms

- **The learned model wins the error it was trained on and ties on the error the user cares about.**
  Lozano-Duran, ZPG TBL (arXiv preprint pp. 17-18): **internal** wall-stress error **below 0.5%**
  (BFWM) versus **~2%** (EQWM), but **total** error **5-15% for both**, with mean velocity profiles
  deviating **10-30%** from DNS. The authors name the reason (p. 29): "**A key conclusion of this work
  is that the main limiting factor in the accuracy of the BFWM predictions originates from external
  modelling errors due to the poor performance of SGS models.**"
- **Error cancellation makes the worse model look better.** On APG/Separation, "**EQWM appears more
  accurate but for the wrong reasons**" — it underpredicts `tau_w` while overpredicting near-wall
  velocity. Same on CRM `C_L` at low incidence. *This is Larsson's warning (§8.1) reappearing as a
  measurement.*
- **Solver lock-in.** Lozano-Duran, p. 29: "**Consistency between the model and the numerical/gridding
  schemes is solver-dependent. As such, the BFWM must be re-trained to yield accurate predictions in
  different flow solvers.**" *Directly opposite to Singh 2017's cross-solver portability (§2.6) — and
  the difference is what was learned: a non-dimensional multiplier on a physical term ports; a wall
  model trained on one solver's own WMLES fields does not.*
- **`FLAG F2` — the flagship results carry no numbers.** Bae's per-`Re` errors exist **only as
  Fig. 3** (ordinate -70% to +10%); the TBL `C_f` is "comparable to the empirical values" with **no
  numeric error**. Lozano-Duran's NASA CRM High-Lift `C_L`/`C_D`/`C_M` improvements are "**moderate**"
  with **no numeric values** — Fig. 15 is a plot.
- **Discretisation sensitivity can exceed the headline accuracy.** Bae, p. 16: the wall-shear stress
  changes **~5%** when the sampling point is placed on a grid point rather than a midpoint — against a
  headline accuracy of **<4%**. The paper does not decompose the two.
- **Non-monotonic grid convergence is reported and not explained** (Lozano-Duran, pipe case), and:
  "**WMLES might not converge to the DNS solution with grid refinements until the grid is in the
  DNS-like regime**, when the contribution of the wall model is negligible" (p. 16).
- **The confidence score has no error bound**: "**low confidence scores may still result in accurate
  wall stress predictions and vice versa**" (p. 28).
- **Neither model can do transition.** Larsson (PDF pp. 11-13): "Existing wall-modeled LES approaches
  ... **cannot predict transition**", with the cylinder drag crisis missed "**regardless of the
  Reynolds number**". Lozano-Duran concedes it directly (p. 28): "**there is no specific mechanism in
  the BFWM to faithfully capture the laminar-to-turbulent transition.**"
- **Reproducibility here is nil.** `FEASIBILITY.md` §1.5: both are **BLOCKED on compute and data** —
  no LES capability is configured on this machine, and a channel WMLES at `Re_tau = 2000` alone is
  50-200 core-hours per case.

## 8.7 Flow classes

| Flow class | Bae 2022 | Lozano-Duran 2023 |
|---|---|---|
| Plane channel | **trained on it**; <4% over `Re_tau` 5200-1e6 | internal <0.5%, total 5-15% |
| ZPG flat-plate BL | **held out** — "comparable" `C_f`, no number | interpolates across `Re` and grid |
| Pipe at `Re_tau ~ 40,000` | not tested | **extrapolates**, internal <5% |
| Favourable pressure gradient | not tested | total error rises **5% -> 20%** with increasing FPG |
| Adverse pressure gradient / separation | **not tested** | BFWM better internally; **EQWM better in total, by cancellation** |
| Unsteady (spanwise pressure gradient) | not tested | internal **<1% at all times**; EQWM misses it entirely |
| Full aircraft (CRM High-Lift, Juncture) | not tested | "**moderate improvements**", **no numbers**; confidence 22% in separation |
| Transition | **cannot** | **cannot** |

---

# 9. Comparison table across all classes

Read down the invariance column first: it is the axis on which the classes differ most and agree
least.

| Class | Inputs | **Invariance handling** | Solver coupling | Training data & loss | Validation done | Headline number, with location | Its stabiliser | Fails on |
|---|---|---|---|---|---|---|---|---|
| **1. Analytical** | `S`, `Omega`, `d`, 1-2 scalars | **Exact by construction** (Pope: 10 tensors, 5 invariants in 3-D) | **Implicit** — `nu_t` in the coefficient matrix | hand calibration on 5 flows | a-posteriori only | BFS reattachment SST **6.5** vs expt **~6.4** (Menter, AIAA J. p. 1603) | none needed | normal-stress anisotropy: predicts `a11=a22=a33=0` (Pope, JFM p. 332) |
| **2. FIML** | 5 candidate local scalars; subset never stated | **None claimed**; local non-dimensionalisation only | **In-the-loop, iterative**; multiplier on the SA production term | experimental `C_l`; adjoint + Tikhonov `lambda = 4e-4` | a-posteriori, in **two solvers** | separation-bubble length **15% more accurate** (Singh, arXiv preprint p. 31) | **none needed** | training-set selection sensitivity, unquantified (p. 20) |
| **3a. TBNN** | 5 invariants of `S`,`R` | **By construction**; reflection not discussed | explicit `b` | 6 flows; `b` MSE | a-priori numeric; a-posteriori **graphical** | `b` RMSE duct **0.13** vs LEVM 0.23 (Table I, p. 11) | **none** — no conditioning analysis | corner-vortex strength/shape (p. 13); unrealisable `b` near the wall (Kaandorp p. 35) |
| **3b. TBRF** | **17 features**, 4 of 9 flagged not Galilean-invariant | **By construction for the output**, audited for the inputs | explicit, **blended** | PH+CD, `N = 21,000` | **both** | `b` RMSE **0.0521** (17 feat.); BFS reattach **6.32** vs DNS 6.28 (Tables 3, 4) | **`gamma_max = 0.8`**; Gaussian `sigma = 3` cells; median-of-trees | untested unsteady (p. 9); shear-layer barycentric excursion "**reason unclear**" (p. 35) |
| **3c. SpaRTA** | **2 invariants, 4 tensors** | Inherited implicitly; **not claimed** | additive to k-omega SST | 3 separating flows, `K ~ 15000`; elastic net + ridge | **both, same metric** | `eps(U)/eps(U_0)` **0.208-0.306** vs ceiling 0.00165-0.227 (Tables 1, 2) | **coefficients x 0.1 on convergence failure** | no duct; hand-selected models; CBFS ceiling itself poor |
| **3d. PIML-RF** | **50 features** (47-invariant basis + 3) | **Galilean + rotational yes; reflectional explicitly NO** | **Implicit `nu_t^L` split** | one flow at a time; RF 300 trees | a-posteriori, **graphical** | **no error table exists** | none needed | `Re` extrapolation untested (p. 26) |
| **4. Differentiable / SITL** | raw fields (except Stroefer) | **None, except Stroefer's tensor basis** | **in the loop, `n` unrolled steps** | downsampled DNS; MSE + spectral/strain terms | **a-posteriori by construction** | SOL **91%** vs NON 67% (Um Table 1); List 60-step MSE **1.93e-5** vs no-model 1.25e-3 | curriculum (short unroll first); **gradient sub-range 20-30 steps** | randomly forced systems; grid lock-in; `Re <= 3125` |
| **5. UQ (Bayesian/EnKF)** | none (KL coefficients) | **By parameterisation** — invariants perturbed, orientation not | **in the loop, re-solving**, ~10 iterations | 18-25 sparse velocity points, `sigma_obs` 10% | a-posteriori; **no held-out test** | **60x** a baseline solve per case (p. 40) | **clip `(xi,eta)` to `[-1,1]^2`**; 16/8 KL modes | truth may lie outside the space (p. 10); intervals too narrow (p. 28) |
| **5b. Eigenspace perturbation** | none | by realisability | perturbed re-solves | none — no training | `BLOCKED-ON-SOURCE` | **no number quoted** | n/a | unreadable here |
| **6. Aggregation** | 10 features, **per-model** | **Not discussed** | **none** — post-processing | 820-40,080 points, total pressure only | neither | velocity MSE **~1/3** better on extrapolation (p. 23) | cost floor `C = 0.001` -> uniform weights | **consensus on the wrong answer** (p. 17); synthetic truth |
| **7. LES-SGS-ML** | stencils, or the whole field | **None, in any paper** | a-priori only / in-the-loop / projected | filtered DNS; MSE or correlation | **both, and they disagree** | `CC` **0.477/0.767** (Beck Table 3); Guan `c` 0.90 unstable -> 0.92 stable (Table 2) | truncation (half the field) / eddy-viscosity projection + limiter / `N_H >= 50` / `n_tr >= 30,000` | loses to AD3 by 3x a-priori (Maulik & San Table 4); **no wall-bounded case on disk** |
| **8. Wall-model-ML** | wall-normal stencil or log-law state | **Not discussed**; Bae's LLWM state is `Re`-free **by physics** | in-the-loop (RL) / frozen BC | channel only (Bae); E-WMLES fields (LD) | a-posteriori | **<4%** `u_tau` over 125x `Re` extrapolation (Bae p. 7) | action clipped `[0.9, 1.1]`; 1% reward bonus; ReF-ER gradient clipping | transition (both); solver lock-in (LD p. 29); `(h_m)+` band (Bae VWM) |

---

# 10. Which flow classes are covered, and which are not

| Flow class | Covered by | With what evidence | Gap |
|---|---|---|---|
| **Plane channel** | wall models; Wu 2018 ill-conditioning | Bae <4% over `Re_tau` 5200-1e6; Table 1's 0.31% -> 35.1% | — |
| **Square duct / secondary flow** | TBNN, TBRF, Wu 2018, Xiao 2016, Stroefer | `b` RMSE 0.13 / 0.0521; Xiao's `tau_yy - tau_zz` | **No a-posteriori velocity error number anywhere for a duct** |
| **2-D separation (hills, CBFS, BFS)** | SpaRTA, TBRF, Wang 2017, Xiao 2016, Wu 2018 | `eps(U)/eps(U_0)` 0.208-0.306; reattachment 6.32 vs 6.28 | Best-covered class in the corpus |
| **Airfoil through stall** | Singh 2017 only | one number: 15% on a hump bubble | `BLOCKED on data` here |
| **Compressor cascade** | de Zordo-Banliat only | one number: ~1/3 velocity MSE | truth is synthetic |
| **Decaying isotropic turbulence** | Beck, Sirignano | `CC` 0.477; Smagorinsky beaten, **no number** | no a-posteriori metric in either |
| **2-D Kraichnan turbulence** | Maulik 2019, Guan 2022, Kochkov, List | Guan's stability table; Kochkov 8-10x | 2-D cascade is not 3-D |
| **Mixing layers** | List 2022 | TML 64.8x, SML 6.8x vs no model | `Re <= 500` |
| **Wall-bounded LES with a learned SGS model** | **NOTHING** | — | **Park & Choi 2021 quarantined. This is the corpus's biggest physics gap.** |
| **Transition** | **NOTHING** | Larsson: wall models "cannot predict transition"; LD: "no specific mechanism" | — |
| **3-D complex geometry** | Lozano-Duran only, **graphically** | CRM/Juncture, "moderate", no numbers | — |
| **Compressible / shocks** | Larsson's SBLI discussion only | equilibrium model "within the experimental uncertainties" | no learned closure |
| **Unsteady RANS** | **NOTHING** | Kaandorp: "untested for unsteady flows" | — |
| **Engineering `Re` for any learned method** | **NOTHING except the wall models** | Bae to `Re_tau = 1e6`; LD to `Re = 5.49e6` | Every RANS and SGS learned closure sits at `Re <~ 1.3e5` |

---

# 11. What this document cannot see

- **It is built from 33 papers, 16 of which the corpus's intended list also names but cannot supply.**
  Category C is catalogued without its three foundational papers; Category D without its entire
  eigenspace-perturbation half; Category E without the wall-bounded case and without Germano,
  Bardina or Vreman. **Statements about method classes are therefore statements about the papers on
  disk, not about the literature.**
- **Five on-disk papers report no numeric error metric at all** — Stroefer 2021, Sirignano 2020,
  Wu 2018, Maulik 2019, and Singh 2017 for its flow fields. Every comparison in §9 that involves them
  is qualitative on their side, and this document says so at each occurrence rather than filling the
  cell.
- **Nothing here has been reproduced.** Every number is the paper's own, read from a title-verified
  PDF. `FEASIBILITY.md` records which of them could be tested on this machine and at what cost; none
  has been.
- **The cross-paper comparisons are not like-for-like.** Different flows, different Reynolds numbers,
  different baselines, different metrics, different solvers. The `b` RMSE of Ling's duct at
  `Re_b = 2000` and Kaandorp's duct at `Re = 3500` are not the same measurement, and neither is
  comparable to Schmelzer's normalised velocity MSE.
- **Two live disagreements are recorded and left open**: whether physics constraints help or hurt
  (§0.1, Ling versus Kochkov/Sanderse), and whether model-consistent training is required or merely
  one option (Duraisamy 2021 versus Sanderse 2024).
- **One architecture discrepancy is recorded and deliberately not resolved**: Kaandorp 2020 describes
  Ling's TBNN as 10 layers / lr 2.5e-5 / Adam / batch 1000; the Ling SAND preprint on disk says
  8 layers x 30 nodes / lr 2.5e-7 / per-point SGD. **For any reproduction, use the on-disk numbers and
  state that Kaandorp's differ.**
- **The corpus is still moving.** Two papers arrived during the writing of this document
  (`Wu2018_rans_explicit_closure_ill_conditioned.pdf`, `Guan2022_stable_aposteriori_les_cnn.pdf`),
  and both changed conclusions in it. Anything written here should be re-checked against
  `MANIFEST.md` at the next phase boundary.
