# Closure-Modelling Paper Catalogue

Compiled by Sub-agent A (closure modelling team). Working corpus:
`/home/ubuntu/Certonomous/docs/papers/closure/` (42 PDFs + MANIFEST.md).

---

## 0. READ THIS FIRST — CORPUS PROVENANCE AUDIT (2026-08-20)

**Before cataloguing anything I verified the identity of every PDF by extracting page 1
and comparing the paper's own printed title/journal line against the MANIFEST claim.
30 of the 42 files are unrelated papers.**

The failure mode: the retrieval agent that built MANIFEST.md *guessed* arXiv identifiers.
Each guessed ID resolves to a real arXiv paper — just not the intended one — so the
download succeeded, the sha256 was computed over the wrong file, and the manifest
row now *certifies* the wrong document. The manifest is internally consistent and
externally false. Nothing in this catalogue is derived from a file whose printed
title I have not personally matched.

### 0.1 What is on disk now (30 PDFs, every one identity-verified by me)

I re-retrieved the recoverable papers myself. Method: query the arXiv API by author+title, or try a
candidate identifier directly, **download the PDF, extract page 1, and accept the file only if the
paper's own printed title matches**. Nothing below was accepted on the strength of an identifier alone.

| File | Verified identity (read off page 1) | Version authority |
|---|---|---|
| `Pope1975_effective_viscosity_hypothesis.pdf` | Pope, "A more general effective-viscosity hypothesis" | **Journal of record**: J. Fluid Mech. 72(2):331-340 |
| `Spalart2000_strategies_turbulence_modelling.pdf` | Spalart, "Strategies for turbulence modelling and simulations" | **Journal of record**: Int. J. Heat Fluid Flow 21:252-263 |
| `Menter1994_sst_two_equation.pdf` | Menter, "Two-Equation Eddy-Viscosity Turbulence Models for Engineering Applications" | **Journal of record**: AIAA J. 32(8):1598-1605 |
| `Smagorinsky1963_general_circulation.pdf` | Smagorinsky, "General Circulation Experiments with the Primitive Equations I" | **Journal of record**: Mon. Wea. Rev. 91(3) |
| `Nicoud1999_WALE_sgs.pdf` | Nicoud & Ducros, "Subgrid-Scale Stress Modelling Based on the Square of the Velocity Gradient Tensor" | **Journal of record**: Flow Turbul. Combust. 62:183-200 |
| `Piomelli2002_wall_layer_models_les.pdf` | Piomelli & Balaras, "Wall-layer models for large-eddy simulations" | **Journal of record**: Annu. Rev. Fluid Mech. 34:349-374 |
| `Larsson2016_wall_stress.pdf` | Larsson, Kawai, Bodart & Bermejo-Moreno, "Large eddy simulation with modeled wall-stress" | **Journal of record**: Bull. JSME, Mech. Eng. Reviews 3(1), 2016 (J-STAGE open access) |
| `Guyon2003_feature_selection.pdf` | Guyon & Elisseeff, "An Introduction to Variable and Feature Selection" | **Journal of record**: JMLR 3:1157-1182 |
| `Wang_Wu_Xiao2017_pinn_reynolds_stress.pdf` | Wang, Wu & Xiao, "A Physics Informed Machine Learning Approach for Reconstructing Reynolds Stress Modeling Discrepancies Based on DNS Data" | arXiv:1606.07987v2 — **preprint** (journal: Phys. Rev. Fluids 2, 034603) |
| `Wu2018_physics_augmenting.pdf` | Wu, Xiao & Paterson, "Physics-Informed Machine Learning Approach for Augmenting Turbulence Models: A Comprehensive Framework" | arXiv:1801.02762v4 — **preprint** (journal: Phys. Rev. Fluids 3, 074602) |
| `Schmelzer2020_algebraic_reynolds.pdf` | Schmelzer, Dwight & Cinnella, "Discovery of Algebraic Reynolds-Stress Models Using Sparse Symbolic Regression" | arXiv:1905.07510v2 — **preprint** (journal: Flow Turbul. Combust. 104:579-603) |
| `Kaandorp2020_random_forests.pdf` | Kaandorp & Dwight, "Data-Driven Modelling of the Reynolds Stress Tensor using Random Forests with Invariance" | arXiv:1810.08794v2 — **preprint** (journal: Computers & Fluids 202:104497) |
| `Xiao2016_model_uncertainties.pdf` | Xiao, Wu, Wang, Sun & Roy, "Quantifying and Reducing Model-Form Uncertainties in RANS Simulations: A Data-Driven, Physics-Based Bayesian Approach" | arXiv:1508.06315v3 — **preprint** (journal: J. Comput. Phys. 324:115-136) |
| `Singh2017_ml_airfoils.pdf` | Singh, Medida & Duraisamy, "Machine Learning-augmented Predictive Modeling of Turbulent Separated Flows over Airfoils" | arXiv:1608.03990v3 — **preprint** (journal: AIAA J. 55(7):2215-2227) |
| `Beck2019_deep_neural_les.pdf` | Beck, Flad & Munz, "Deep Neural Networks for Data-Driven Turbulence Models" | arXiv:1806.04482 — **preprint**; note the **preprint title differs from the journal title** ("Deep neural networks for data-driven LES closure models", J. Comput. Phys. 398:108910) |
| `Maulik_San2017_neural_deconvolution.pdf` | Maulik & San, "A neural network approach for the blind deconvolution of turbulent flows" | arXiv:1706.00912v2 — **preprint** (journal: J. Fluid Mech. 831:151-181) |
| `Maulik2019_subgrid_2d_nn.pdf` | Maulik, San, Rasheed & Vedula, "Sub-grid modelling for two-dimensional turbulence using neural networks" | arXiv:1808.02983v1 — **preprint** (journal: J. Fluid Mech. 858:122-144) |
| `Sirignano2020_dpm_les.pdf` | Freund, MacArt & Sirignano, "DPM: A deep learning PDE augmentation method (with application to large-eddy simulation)" | arXiv:1911.09145v1 — **preprint**. **Note the author order on the preprint is Freund, MacArt, Sirignano**, not the "Sirignano, MacArt & Freund" of the manifest. |
| `Bae2022_marl_wall_model.pdf` | Bae & Koumoutsakos, "Scientific multi-agent reinforcement learning for wall-models of turbulent flows" | arXiv:2106.11144v2 — **preprint** (journal: Nature Communications 13:1443) |
| `LozanoDuran2023_wall_model.pdf` | Lozano-Duran & Bae, "Machine learning building-block-flow wall model for large-eddy simulation" | arXiv:2211.07879v3 — **preprint** (journal: J. Fluid Mech. 963:A35) |
| `Strofer2021_differentiable.pdf` | Stroefer & Xiao, "End-to-end differentiable learning of turbulence models from indirect observations" | arXiv:2104.04821v1 — **preprint** (journal: Theor. Appl. Mech. Lett. 11:100280) |
| `Um2020_solver_loop.pdf` | Um, Brand, Fei, Holl & Thuerey, "Solver-in-the-Loop: Learning from Differentiable Physics to Interact with Iterative PDE-Solvers" | arXiv:2007.00016v2 — **preprint** (NeurIPS 2020) |
| `List2022_learned_turbulence.pdf` | List, Chen & Thuerey, "Learned Turbulence Modelling with Differentiable Fluid Solvers: Physics-based Loss-functions and Optimisation Horizons" | arXiv:2202.06988v2 — **preprint** (journal: J. Fluid Mech. 949:A25) |
| `Kochkov2021_ml_accelerated_cfd.pdf` | Kochkov, Smith, Alieva, Wang, Brenner & Hoyer, "Machine learning accelerated computational fluid dynamics" | arXiv:2102.01010v1 — **preprint** (journal: PNAS 118(21) e2101784118) |
| `deZordoBanliat2023_space_dependent_aggregation.pdf` | de Zordo-Banliat, Dergham, Merle & Cinnella, "Space-dependent turbulence model aggregation using machine learning" | arXiv:2301.09013v1 — **preprint** |
| `Duraisamy2019_turbulence_age_data.pdf` | Duraisamy, Iaccarino & Xiao, "Turbulence Modeling in the Age of Data" | arXiv:1804.00183v3 — **preprint** (journal: Annu. Rev. Fluid Mech. 51:357-377) |
| `Duraisamy2021_perspectives_ml.pdf` | Duraisamy, "Perspectives on Machine Learning-augmented RANS and LES Models of Turbulence" | arXiv:2009.10675v3 — **preprint** (journal: Phys. Rev. Fluids 6:050504) |
| `Beck2021_perspective_ml.pdf` | Beck & Kurz, "A Perspective on Machine Learning Methods in Turbulence Modelling" | arXiv:2010.12226v1 — **preprint** (journal: GAMM-Mitteilungen 44:e202100002) |
| `Sanderse2024_ML_closure_models.pdf` | Sanderse, Stinis, Maulik & Ahmed, "Scientific Machine Learning for Closure Models in Multiscale Problems: A Review" | arXiv:2403.02913v2 — **preprint** |
| `Gatski1996_handbook_chapter6.pdf` | **IDENTITY NOT ESTABLISHED — unreadable, see §0.3** | — |

### 0.2 What was wrong, and why the manifest cannot be trusted

The retrieval agent that produced `MANIFEST.md` *guessed* arXiv identifiers. Each guessed identifier
resolves to a real but unrelated arXiv paper, so the download succeeded, the sha256 was computed over
the wrong file, and the manifest row now **certifies the wrong document**. The manifest is internally
consistent and externally false. **30 of the original 42 files were unrelated papers.** A sample of
what was actually in them:

| Filename claimed to be | Actually contained |
|---|---|
| Ling, Kurzawski & Templeton 2016 (TBNN) | arXiv:1606.01151 "Using Neural Generative Models to Release Synthetic Twitter Corpora" (cs.CL) |
| Wu, Xiao & Paterson 2018 | arXiv:1708.08690 "The Bishop-Phelps-Bollobas property for numerical radius" (math.FA) |
| Schmelzer, Dwight & Cinnella 2020 | arXiv:1907.01883 "Numerical homogenization for nonlinear strongly monotone problems" (math.NA) |
| Bose & Park 2018 (WMLES review) | arXiv:1701.04413 "Unified Models of Neutrinos, Flavour and CP Violation" (hep-ph) |
| Lozano-Duran & Bae 2023 | arXiv:2105.14103 "An Attention Free Transformer" (Apple, cs.LG) |
| Vreman 2004 | arXiv:physics/0409022 "Critical dimension of Spectral Triples" |
| Emory, Larsson & Iaccarino 2013 | arXiv:1303.1564 "The HAWC observatory as a GRB detector" (astro-ph) |
| Parish & Duraisamy 2016 (JCP 305:758-774) | Bian, Pang, Tang & Arnold, "ALmost EXact boundary conditions for transient Schrodinger-Poisson system", **JCP 313:233-246** — right journal, wrong article |

plus the same failure for Beck2019, Beck2021, Duraisamy2021, Edeling2014, Holland2019, Iaccarino2017,
Kaandorp2020, Larsson2016, Ling2015, List2022, Maulik2017, Maulik&San2017, Park2021, Singh2016,
Singh2017, Sirignano2020, Strofer2021, Um2020, Weatheritt2016, Wang/Wu/Xiao2017, Xiao2016, Yang2019.

**`MANIFEST.md` has not been corrected and its "RETRIEVED PAPERS" table is still the wrong-file table.
Treat §0.1 above, not the manifest, as the inventory of record until the supervisor rewrites it.**

### 0.3 File present but unreadable

| File | Problem |
|---|---|
| `Gatski1996_handbook_chapter6.pdf` (was `Gatski1993_explicit_algebraic_stress.pdf`) | 77 pages, 300-dpi bitonal CCITT **scan with no text layer** (`pdftotext` yields 77 bytes). PDF Subject field is `p39_62`, Creator `HP Digital Sender 8100C`, created 2002-11-01. Page count and the `p39_62` tag are inconsistent with the ~20-page Gatski & Speziale (1993) *J. Fluid Mech.* 254:59-78 paper; this is a scanned handbook/lecture-note chapter. No `tesseract`/`ocrmypdf`/`gs` on this host, so it cannot be OCR'd here. **Not catalogued. Gatski & Speziale (1993) is treated as [NOT ON DISK].** |

### 0.4 Still not on disk

Recoverable-in-principle but not obtained: **Ling, Kurzawski & Templeton (2016) — the TBNN paper**
(no arXiv twin located; J. Fluid Mech. 807:155-166), Ling & Templeton (2015), Weatheritt & Sandberg
(2016) GEP, Singh & Duraisamy (2016), Holland, Baeder & Duraisamy (2019), Emory, Larsson & Iaccarino
(2013), Iaccarino, Mishra & Ghili (2017), Vreman (2004), Park & Choi (2021), Bose & Park (2018),
Yang, Zafar, Wang & Xiao (2019), Edeling, Cinnella & Dwight (2014), Parish & Duraisamy (2016),
Bardina, Ferziger & Reynolds (1980), Germano, Piomelli, Moin & Cabot (1991), Gatski & Speziale (1993).

**The absence of Ling et al. (2016) is the most damaging gap** — it is the origin paper for
tensor-basis neural networks and the direct ancestor of most of category B. Where the method-classes
inventory must refer to it, it is tagged `[NOT ON DISK — from memory, unverified]` and carries no
quoted numbers.

### 0.5 Consequence for this catalogue

Sections below catalogue **only** verified files. Papers the lane needs but which are not on disk in
verified form are **not summarised as though they had been read**; they appear only under the
`[NOT ON DISK]` tag with no numeric claims attached.

---

## Category key

| Code | Meaning |
|---|---|
| A | Foundational analytical closures (Boussinesq, EASM, QCR, SST, SA, Smagorinsky, Vreman) |
| B | Data-driven RANS (TBNN, random forests, symbolic/SpaRTA, GEP) |
| C | Field inversion + machine learning (FIML) |
| D | Model-form UQ (eigenspace perturbation, Bayesian) |
| E | LES subgrid-scale closures (Smagorinsky, dynamic, WALE, Vreman, NN-SGS, deconvolution) |
| F | Wall-modelled LES |
| G | Differentiable / solver-in-the-loop learning |
| H | Multi-model aggregation |
| R | Reviews / perspectives |
| X | Feature selection / ML methodology |

## Version caveat

Files marked "arXiv preprint" above are preprints. **Page, equation, section, figure and
table numbers quoted from them are the arXiv preprint's numbering and may differ from the
published version.** Every such citation below is written explicitly as
"arXiv preprint p./eq./Fig./Table". Files marked "journal of record" are the published
article and their numbering is authoritative; those citations are written plainly.

---

## Category A — Foundational analytical closures

---

### `Pope1975_effective_viscosity_hypothesis.pdf`

- **Category**: A (primary). Secondary: B — this is the tensor-basis origin paper that TBNN (Ling et al. 2016) and every tensor-basis ML closure since is built on.
- **Version**: **Journal of record** — *J. Fluid Mech.* (1975) vol. 72, part 2, pp. 331-340. Page/equation numbers below are authoritative, not preprint numbering.
- **Method (one line)**: Argues that any effective-viscosity hypothesis (Reynolds stress a function of strain rate, rotation rate and two scalars) must, by the Cayley-Hamilton theorem, reduce to a *finite* tensor polynomial in the normalised strain `s` and rotation `w`; then evaluates the polynomial's scalar coefficients for 2-D flow from the Launder-Reece-Rodi Reynolds-stress equations via Rodi's algebraic-stress approximation.
- **Data used**: None (analytical). The only empirical numbers quoted are Champagne, Harris & Corrsin (1970) nearly-homogeneous shear-flow measurements.
- **Cases / flows**: Nearly-homogeneous high-Reynolds-number shear flow; simple unidirectional shear (`U1` the only non-zero mean velocity, `x2` the only direction of variation), p. 336. No Re is stated — the derivation is explicitly a *high-Reynolds-number* argument (p. 333: two scaling parameters suffice "only at high Reynolds numbers, when any influence of the laminar viscosity may be excluded").
- **Metric**: Anisotropy components `a_ij = u_i u_j / k - (2/3) delta_ij`.

**Headline result with numbers**

1. **Finite basis (p. 334-335)**. In three dimensions there are exactly **10 linearly independent symmetric traceless tensors T1..T10 and 5 independent invariants** `{s^2}, {w^2}, {s^3}, {w^2 s}, {w^2 s^2}`. In two dimensions there are exactly **3 tensors** — `T0 = (1/3)I3 - (1/2)I2`, `T1 = s`, `T2 = sw - ws` — **and 2 non-zero invariants** `{s^2}` and `{w^2}`. This is eq. (3.6)/(3.7), p. 335. *This is the 10-term / 5-invariant basis that TBNN uses verbatim.*
2. **Quantitative failure of the isotropic-viscosity (Boussinesq) hypothesis (p. 332)**. In nearly homogeneous shear flow Champagne, Harris & Corrsin (1970) measured
   `a11 = 0.3, a22 = -0.18, a33 = -0.12, a12 = 0.33`.
   The isotropic-viscosity assumption (eq. 1.2) predicts **at best** `a11 = a22 = a33 = 0, a12 = 0.33`.
   So Boussinesq reproduces the shear stress exactly and **gets all three normal-stress anisotropies wrong by their full magnitude** (0.3, -0.18, -0.12 -> 0, 0, 0). Pope, p. 332: "the mechanism that causes the inequality of the normal stresses cannot be accounted for with an isotropic-viscosity hypothesis."
3. **Which coefficient does what (p. 336)**. For the simple shear flow: `a11 = -(1/3)G0 - (1/4)G2 (k/eps)^2 U1,2^2`, `a22 = -(1/3)G0 + (1/4)G2 (k/eps)^2 U1,2^2`, `a33 = (2/3)G0`, `a12 = (1/2)G1 (k/eps) U1,2`, `a13 = a23 = 0`. Hence **G1 alone sets the shear stress; G0 and G2 alone set the normal-stress splitting.** Setting `G0 = G2 = 0` (i.e. Boussinesq) forces zero normal-stress anisotropy — result 2 restated structurally.
4. **C_mu is not a constant**. Eq. (4.4) makes `C_mu` a function of the two invariants via `sigma = ((1/2){s^2})^(1/2)` and `Omega = (-(1/2){w^2})^(1/2)`; Fig. 1 (p. 337) plots `C_mu(sigma, Omega)`. Pope notes (p. 337) that Prandtl-Kolmogorov (`C_mu = const`), Bradshaw-Ferriss-Atwell (`C_mu ~ 1/sigma`) and Rodi (1972) all lack **any dependence on the rotation invariant Omega**, which "is tantamount to assuming that the Reynolds stresses are materially indifferent; that is, to assuming that the Reynolds stresses are unaffected by solid-body rotations", and is "most likely responsible for the short-comings of these isotropic-viscosity hypotheses in predicting flows with streamline curvature."
5. Constants from Launder, Reece & Rodi (1975) used in eq. (4.2): `C1 = 1.5`, `C2 = 0.4` (p. 335). Coefficients `b1 = 4/5`(as printed `b, = A`, OCR-degraded), `b2 = (1/12)(5 - 9 C2)`, `b3 = (1/11)(7 C2 + 1)`, `g = (C1 + P/eps - 1)^{-1}` (eq. 4.2 block, p. 335).

**Stated limitations (author's own words, p. 337)**

- "While the proposed effective-viscosity hypothesis has advantages over isotropic hypotheses, **its predictions are identical to those of the algebraic stress model** and it has the disadvantage of being **restricted to two-dimensional flows. (The three-dimensional form is so intractable as to be of no value.)**"
- Validity conditions, stated as a theorem-like restriction (p. 333): "for a **high Reynolds number nearly homogeneous flow**, the Reynolds stresses are uniquely related to the rates of strain and two independent scaling parameters, **provided that all macroscales are proportional and that the boundary conditions affect only the scaling parameters**."
- p. 333: homogeneity of the rates of strain is a *necessary* condition for the effective-viscosity approach to be valid at all; and "The fact that tau_t and tau_s are independent in any real flow situation means that the flow cannot be homogeneous and consequently some transport of Reynolds stresses occurs" — i.e. the hypothesis is *never exactly* valid in a real flow.
- Claimed compensating advantages (p. 337): keeping the stress-strain relation inside the differential equation **increases numerical stability**, and the simultaneous algebraic-stress equations need not be solved.

**What it cannot see**

- **No a-posteriori test whatsoever.** There is not one CFD solution in the paper. The only comparison to data is the four-number anisotropy check in §1 against a single homogeneous-shear experiment.
- **Single flow, single state.** The "validation" is one nearly-homogeneous shear flow. Nothing about separation, adverse pressure gradient, secondary motion, or wall-bounded anisotropy near a wall.
- **No Reynolds-number sweep**; the theory *assumes* Re -> infinity and explicitly excludes laminar-viscosity influence, so it says nothing about low-Re or near-wall regions where `nu` matters.
- **The 3-D coefficient problem is left open** — the paper supplies the 10-tensor basis but evaluates coefficients only in 2-D. Every 3-D user of this basis (including TBNN) has to *learn or model* the ten `G_lambda`, and Pope himself judged the analytic 3-D route worthless. **This is exactly the gap ML closures claim to fill, and the catalogue should read TBNN as "learn Pope's G_lambda from data" rather than as a new representation.**
- **Realisability is asserted, not proved.** The abstract claims "the complete Reynolds-stress tensor is realistically modelled"; there is no check that eq. (4.3) keeps `a` inside the Lumley realisability triangle for arbitrary `(sigma, Omega)`.
- No uncertainty quantification, no sensitivity of `C_mu` to the LRR constants `C1, C2` (which are themselves calibrated), and no statement of what happens when `P/eps` in `g = (C1 + P/eps - 1)^{-1}` approaches the pole.

---

### `Menter1994_sst_two_equation.pdf`

- **Category**: A (primary). No secondary — but note this model is the **baseline RANS in the Closure Challenge benchmark on disk** (`/home/ubuntu/closure-challenge-benchmark/`, k-omega SST), so its documented failure modes are the failure modes the lab's corrections are trying to fix.
- **Version**: **Journal of record** — *AIAA Journal* Vol. 32, No. 8, August 1994, pp. 1598-1605. Page/equation/figure numbers authoritative.
- **Method (one line)**: Blend Wilcox k-omega (near wall, where it needs no damping functions and is freestream-robust) with a k-omega-transformed standard k-epsilon (wake region and free shear, where k-omega's freestream sensitivity bites) via a wall-distance blending function `F1` — that is the BSL model; then redefine the eddy viscosity as `nu_t = a1 k / max(a1 omega, Omega F2)` (eq. A16/eq. 12) so that Bradshaw's `tau = a1 k` relation is enforced inside boundary layers — that is the SST model.
- **Data used**: No training data in the ML sense. Model constants are **hand-tuned**; the paper is explicit about this. Validation is against five published experiments.
- **Cases / flows and Re**:
  - Flat-plate ZPG boundary layer (freestream-sensitivity study), p. 1601.
  - **Driver's adverse-pressure-gradient separating flow**: boundary layer on a circular cylinder, diverging tunnel walls + wall suction; **inflow Re = 2.8e5 based on cylinder diameter D = 140 mm**; grid 60x3x60, checked against 100x3x100 (p. 1601).
  - **Backward-facing step** (Driver & Seegmiller): grid 120x120, checked against 90x90 and 240x240 (p. 1602).
  - **NACA 4412 airfoil at 13.87 deg incidence, Re_c = 1.52e6** (Coles & Wadcock data); grid 241x61 (p. 1603).
  - **Axisymmetric transonic bump / shock-boundary-layer interaction (Bachalo & Johnson), M = 0.925**; grid 150x3x80, checked against 129x3x60 and 180x3x100 (p. 1603).
- **Metric**: `C_p`, `C_f`, velocity profiles, turbulent shear-stress profiles, `nu_t(max)/(u_e delta*)`, reattachment length.

**Headline result with numbers**

1. **Freestream sensitivity of the original k-omega, quantified (Fig. 1, p. 1601)**: reducing the freestream `omega_f` by **four orders of magnitude** (with `k_f` reduced to hold `nu_t,freestream` fixed) changes the original Wilcox k-omega **eddy viscosity by almost 100%**. The BSL model gives **identical results for both freestream values**. Menter, p. 1601: "The strong sensitivity of the original model to omega_f is clearly unacceptable."
2. **Backward-facing step reattachment length (p. 1603, discussion of Fig. 7)** — the single hardest number in the paper:
   | Model | Reattachment length (step heights) |
   |---|---|
   | k-omega SST | **6.5** |
   | k-omega BSL | 5.9 |
   | k-omega original | 6.4 |
   | Jones-Launder k-epsilon | 5.5 |
   | **Experiment** | **about 6.4** |
   So SST errs +1.6%, original k-omega ~0%, BSL -7.8%, k-epsilon -14%. Note the **original k-omega matches the experiment at least as well as SST on this metric** — SST's advantage is elsewhere.
3. **Adverse pressure gradient is where SST wins** (Figs. 2-6, pp. 1601-1602). On Driver's flow the SST model "predicts the largest amount of separation, whereas the JL model stays firmly attached" (p. 1602); the JL k-epsilon "predicts significantly higher shear-stress levels than the other models in the region where separation is approached" (p. 1603). On `nu_t(max)/(u_e delta*)` (Fig. 6) the k-epsilon model "falls only barely below the value of **0.0168** recommended by Clauser for equilibrium boundary layers ... and thereby **fails to account for the nonequilibrium effects altogether**" (p. 1603).
4. **Mechanism of the SST limiter (eq. 10-12, pp. 1600-1601)**: for a conventional two-equation model the shear stress obeys `tau = rho a1 k sqrt(Production/Dissipation)`. "In adverse pressure gradient flows the ratio of production to dissipation can be significantly larger than one, as found from the experimental data of Driver, and therefore Eq. (11) leads to an **overprediction of tau**." The `max()` limiter caps `nu_t` so `tau = a1 k` holds wherever `Omega > a1 omega`.
5. **NACA 4412 freestream test (Fig. 9, p. 1603)**: raising `omega_f` by a factor of **about fifty** changed the SST result only marginally, but changed the original k-omega result "significantly"; the original k-omega with high `omega_f` collapses onto the BSL curve. Menter: "This example clearly shows the dangers of using the original k-omega model for industrial applications." Notably the **original k-omega predicts velocity profiles even further from experiment than the Jones-Launder k-epsilon** on this case.
6. **Constants (Appendix, eqs. A4-A5, p. 1604)**: set 1 (Wilcox) `sigma_k1 = 0.5, sigma_omega1 = 0.5, beta1 = 0.0750`; set 2 (k-epsilon) `sigma_k2 = 1.0, sigma_omega2 = 0.856, beta2 = 0.0828`; shared `beta* = 0.09, kappa = 0.41`; blend `phi = F1 phi1 + (1 - F1) phi2` (eq. A3). The alternative two-layer variant (eq. 13, p. 1600) sets `F1 = 0` for `y+ > 70`.

**Stated limitations (author's own words)**

- **The whole paper is declared empirical.** Introduction, p. 1598: "It has been the author's experience that **small changes (5-10%) in modeling constants can lead to a significant improvement (or deterioration) of model predictions. None of the available theoretical tools (dimensional analysis, asymptotic expansion theory, use of DNS data, RNG theory, rapid distortion theory, etc.) can provide constants to that degree of accuracy.**" Conclusions, p. 1603: "Two new turbulence models have been developed **on a strictly empirical basis** ... Both models have been **carefully fine tuned**."
- **Post-reattachment recovery is not fixed** (p. 1603): "**All models fail to capture the relaxation downstream of reattachment correctly.** The results of Ref. 19 show that this is also true for a more complex model which accounts for anisotropy effects."
- **3-D is untested** (Conclusions, p. 1603): "An early version of the SST model has been tested for complex three-dimensional flows in Ref. 24 ... but **significantly more testing in three-dimensional flows will be necessary**."
- Menter concedes k-omega "does not correctly predict the asymptotic behavior of the turbulence as it approaches the wall" and "does not accurately represent the k and e distribution in agreement with DNS data" (p. 1598), arguing this does not matter because "the main (and often the only) information the mean flow solver gets from the turbulence model is the eddy viscosity."
- The Samuel-Joubert APG case was judged **insufficiently discriminating** (p. 1601): "It appears that the Samuel-Joubert flow does not pose a sufficiently strong challenge to the models."

**What it cannot see**

- **Still a linear eddy-viscosity model**: SST changes the *magnitude* of `nu_t`, not the *form* of the stress-strain relation. By Pope (1975) p. 336 it therefore predicts `a11 = a22 = a33 = 0` — **zero normal-stress anisotropy** — everywhere. It cannot represent secondary flow of the second kind (square-duct corner vortices) at all, which is precisely one of the Closure Challenge benchmark cases on disk.
- **No 3-D validation** in the paper (the author says so). All five cases are 2-D or axisymmetric; the "3-D" grids quoted (60x3x60, 150x3x80) have **3 cells in the spanwise direction** — they are 2-D calculations in a 3-D code.
- **Single Reynolds number per case**; no Re sweep, so nothing is known about Re-extrapolation of the tuned constants.
- **No uncertainty statement.** The constants are hand-tuned to these five flows; there is no cross-validation, no held-out flow, and no error bar. Menter's own 5-10%-sensitivity remark means the reported agreement is not separable from the tuning.
- **`F1` and `F2` depend on wall distance `y`**, so the model is ill-defined in flows with no unambiguous wall (free shear away from walls is handled, but multi-body/near-wake geometries inherit the shortest-distance convention, p. 1600).
- **The blending is a switch, not a theory**: there is no derivation showing that a `tanh`-blended combination of two calibrated models is itself consistent (e.g. realisable, or asymptotically correct in the blend region). The paper does not claim there is.
- No check that the `max()` limiter in eq. (12) is differentiable-safe or that it does not introduce limit cycles; the paper reports only that the models "have proven to be very stable" (p. 1603) without a metric.

---

### `Spalart2000_strategies_turbulence_modelling.pdf`

- **Category**: A (primary), R (secondary — it is a strategy/perspective paper, not a new model).
- **Version**: **Journal of record** — *Int. J. Heat and Fluid Flow* 21 (2000) 252-263. Page numbers authoritative.
- **Method (one line)**: A taxonomy and cost projection for every level of turbulence prediction from steady RANS to DNS for a full aircraft/turbine/car, with grid-point and time-step estimates and calendar-year projections for when each becomes affordable.
- **Data used**: None (it is an assessment paper); estimates are derived from resolution requirements and Moore's-law extrapolation.
- **Cases / flows**: Notional full-configuration aerodynamics (complete airplane, turbine, car); airfoil/wing boundary layers.
- **Metric**: Grid points, time steps, and "ready-in-year" estimates.

**Headline result with numbers**

1. **Table 1, p. 260 — the cost/readiness ledger.** This is the paper's central artefact. Columns are: aim of grid refinement, unsteady?, Re-dependence of grid count, "3/2D"?, empiricism, grid points, time steps, readiness year.

   | Name | Aim | Unsteady | Re-dep. | 3/2D | Empiricism | Grid | Steps | Ready |
   |---|---|---|---|---|---|---|---|---|
   | 2DURANS | Numerical | Yes | Weak | No | Strong | 10^5 | 10^3.5 | 1980 |
   | 3DRANS | Numerical | No | Weak | No | Strong | 10^7 | 10^3 | 1990 |
   | 3DURANS | Numerical | Yes | Weak | No | Strong | 10^7 | 10^3.5 | 1995 |
   | DES | Hybrid | Yes | Weak | Yes | Strong | 10^8 | 10^4 | 2000 |
   | LES | Hybrid | Yes | Weak | Yes | Weak | 10^11.5 | 10^6.7 | **2045** |
   | QDNS | Physical | Yes | Strong | Yes | Weak | 10^15 | 10^7.3 | **2070** |
   | DNS | Numerical | Yes | Strong | Yes | None | 10^16 | 10^7.7 | **2080** |

   Assumptions (p. 260): target is a full airliner or car; DNS estimate uses grid patches of `Dx x Dz = 100` wall units and **chord Reynolds number about 7e7**; LES estimate is `10^11` for a clean wing scaled up; readiness assumes **computer power grows by a factor of 5 every five years** and that "a very expensive problem today costs about **10^15 floating-point operations**". "Readiness" means Grand-Challenge-possible, not routine industrial use.
   **Consequence Spalart draws, Abstract and p. 261: "For several decades, practical methods will necessarily be RANS, possibly unsteady, or RANS/LES hybrids, pure LES being unaffordable."**

2. **The QCR precursor, with its calibration and its failure, in one paragraph (pp. 253-254).** Spalart adds to the S-A linear stress `tau_ij` the nonlinear term
   `tau*_ij = tau_ij - c_nl1 (O_ik tau_jk + O_jk tau_ik)`, with `O_ik = (d_k U_i - d_i U_k)/sqrt(d_n U_m d_n U_m)` the normalised rotation tensor.
   - **`c_nl1 = 0.3`**, "calibrated in the outer region of a simple boundary layer, by requiring a fair level of anisotropy `u'^2 > w'^2 > v'^2`".
   - **Square duct result (Fig. 1, p. 254): "flow is induced towards the corners, and the skin friction is much closer to experiment (Gessner et al., 1991)"** — a one-equation eddy-viscosity model made to produce secondary flow of the second kind.
   - **But: "other flows such as 3D wall jets have led to negative results (A.N. Secundov, personal communication, 1999)."**
   - And the author's own caveat: "The `c_nl1` term must also be considered as **very preliminary**, in the sense that **it uses only one of the many quadratic combinations of strain and vorticity**. Also note that it is **fully empirical**, instead of being derived from a more complex model; we simply selected the most intuitively attractive combination. **A systematic optimisation has not been performed.**"
   *This is the single most useful precedent in the corpus for a lab building a corrective anisotropy term: a 1-parameter quadratic correction, calibrated on one flow, that fixed square ducts and broke 3D wall jets.*

3. **Circular cylinder at Re = 5e4 — drag coefficient across strategies (Fig. 4 discussion, p. 258)**:
   | Method | C_d |
   |---|---|
   | Steady RANS | ~0.9 (too low) |
   | URANS | ~1.7 (much too high) |
   | DES, coarse grid | 1.05 |
   | DES, fine grid | 1.32 |
   | **Experiment** | **1.2** |
   Note the DES answer straddles the experiment and **moves by 26% under grid refinement** — Spalart says plainly "grid effects are still present".
4. **URANS phase-averaging is not well posed (Fig. 2, p. 256)**: for the circular cylinder "The peak lift coefficient, **five cycles apart in the same flow, can easily vary by a factor of 2.**" His analogy: "this type of averaging would amount to averaging a number of human beings that walk by and do not have the same height. **The average is not a human body.**"
5. **QDNS is not really a model (p. 257)**: near-wall LES resolves the streaks, SGS stresses are the same order as viscous stresses, and streamwise spacing rises only "from 20 in DNS to 50 in QDNS, at best". "Typically, the saving in computer time is a **factor of 10**, roughly equivalent to a Reynolds-number increase by the modest factor **10^(1/4)**; this is **hardly worth the empiricism**."
6. **Channel DES at Re_tau = 2000** (Wasistho & Squires, Fig. 5, p. 259): coarse grid `64 x 64 x 32`, fine grid `128 x 128 x 64`, domain `2 pi x 2 x pi`. "the additive constant C in the logarithmic law is not very accurate due to a **'buffer layer' between the region in which the stress is modelled and the region in which it is resolved**... **The finer grid does not strongly improve the shift.**" Doubling resolution transfers a large amount of stress from modelled `nu_t (u_y + v_x)` to resolved `-uv`, yet "**the mean velocity changes little**" — two deeply different states with nearly the same mean.
7. **Sensitivity asymmetry (p. 260)**: "A **20% change of the Smagorinsky constant** in a well-resolved LES is **minor**, but a **20% change in the Karman constant** is **not**."
8. **S-A internals worth knowing (Appendix A, p. 261)**: the diffusion term "is not conservative for the eddy-viscosity; instead it **conserves the eddy-viscosity raised to the power 1.622**"; production uses **vorticity** rather than strain rate; the wall-destruction term depends on wall distance `d`. Calibrated on Challenge-I thin shear flows only: "**Challenge II was not considered.**"

**Stated limitations (author's own words)**

- **The central verdict, p. 255**: "At the risk of minimising the work of fellow modellers, the author deems it **unlikely that a RANS model, even complex and costly, will provide the accuracy needed in the variety of separated and vortical flows we need to predict.**"
- **On eddy-viscosity models, p. 254**: "There is little dispute that the **ultimate potential of eddy-viscosity models does not include separated flows over 3D geometries**... The models are just too simple and replete with empiricism, and are **trained in such a small pool of simple shear flows, that they have no deep reason to generalize to complex flows.**"
- **Hunt's (1990) escape clause, quoted approvingly on p. 254** — the reason bad models often look fine: "in most flows ... where the duration of a distortion is smaller than the intrinsic time scale of the turbulence, there is insufficient time for the turbulence to affect the mean flow and therefore **an erroneous turbulence model has little effect on the mean flow**." Spalart's gloss: a simple model can "**get credit**" for a new flow "merely because the Reynolds stresses it generates in the complex regions are not damaging; usually, **it is just as well if the stresses are too weak.**"
- **Realisability, p. 253**: "note that the **common one-equation models are far from giving realisable Reynolds-stress tensors**" — and he tried realisable versions but "found the effect **too weak** to justify a widespread modification of codes and testing campaign."
- **Galilean invariance, p. 255**: "**streamline curvature is not a Galilean invariant** (Spalart and Shur, 1997), and therefore Zeman's model for that flow is **not application-ready**."
- **Galilean invariance again, p. 257**, on running LES with no SGS model at all and letting an upwind scheme supply the dissipation: "**Galilean invariance is broken by the asymmetric schemes.**"
- **Grid refinement does not rescue a RANS/URANS model, p. 260**: "in URANS, **no amount of grid refinement will override the influence of the empirical content of the turbulence model.**"
- On the maturity of LES (p. 259): at a workshop on simple sharp-cornered geometries "the conclusions were **particularly mixed, and did not make LES or even QDNS appear very mature**"; for a cylinder at Re of a few thousand, Breuer "was disappointed with the results of both SGS-model improvements, **and grid refinement**"; "We also know from personal communications of at least two studies which their authors did not consider successful enough to publish." (**Publication-bias disclosure — worth flagging in LESSONS.**)
- On his own readiness dates (p. 260): "Such predictions are **not without risk**."

**What it cannot see**

- **This is an opinion-and-estimate paper, not a measurement paper.** Table 1's grid counts are order-of-magnitude judgements ("based on current practice"), the readiness years hinge on one hardware-growth rule of thumb, and Spalart says so. Nothing in Table 1 is a reproducible number; **do not quote a readiness year as a result.**
- **The one piece of original modelling (the `c_nl1` term) is validated on exactly one flow (square duct) with one figure and no error bars**, and the counter-evidence (3D wall jets) is cited only as a personal communication with no data at all. It is uncheckable.
- **No Re sweep, no seed/ensemble uncertainty, no grid-convergence study** is presented as such; the only convergence information is the cylinder `C_d` pair (1.05 -> 1.32) and the channel DES pair, both of which show the answer *moving*, not converging.
- **Written in 2000.** The projections predate GPUs, and predate the entire data-driven closure literature that the rest of this catalogue covers — Spalart's premise is that the empirical content stays hand-tuned. Read it as the statement of the problem that categories B/C/G claim to solve, not as an assessment of them.
- The DES-in-channel result (item 6) is explicitly outside DES's design intent ("such an application was not designed for and is not natural", p. 259), so its log-layer mismatch is not a fair indictment of DES in its own domain.
