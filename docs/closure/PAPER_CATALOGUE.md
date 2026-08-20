# Closure-Modelling Paper Catalogue

Compiled by Sub-agent A (closure modelling team). Working corpus:
`/home/ubuntu/Certonomous/docs/papers/closure/`. The inventory of record is
`docs/papers/closure/MANIFEST.md`, **rewritten from title-page verification on
2026-08-20** (the pre-rewrite version is kept as `MANIFEST_OLD_UNVERIFIED.md`).
Papers still arriving from a rate-limited background fetch at the time of writing;
the manifest was re-derived at the end of this pass and its counts are authoritative
over any count stated in prose below.

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

### 0.1 What is on disk now (every one identity-verified)

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
| `Ling2016_tbnn_embedded_invariance.pdf` | Ling, Kurzawski & Templeton, "Reynolds Averaged Turbulence Modeling using Deep Neural Networks with Embedded Invariance" | Sandia preprint **SAND2016-7345J**, 17 pp — **preprint** (journal: J. Fluid Mech. 807:155-166) |
| `Gatski1996_handbook_chapter6.pdf` | Gatski, "6 Turbulent flows: model equations and solution methodology" — **identity established 2026-08-20 by rendering page 1; see §0.3** | **Book of record**: *Handbook of Computational Fluid Mechanics*, Academic Press 1996, ISBN 0-12-553010-2, pp. 339-414 |

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

**Corrected 2026-08-20.** `MANIFEST.md` has now been **rewritten from scratch** against page-1
title extraction of every file (top level and `_WRONG_RETRIEVALS/`). Every row carries the
verbatim printed title it was verified against and a status in
`{RETRIEVED-VERIFIED, WRONG-QUARANTINED, MISSING}`. The pre-rewrite file is preserved unchanged as
`MANIFEST_OLD_UNVERIFIED.md` so that the failure remains inspectable. **The manifest is now the
inventory of record; where this section and the manifest disagree, the manifest is right, because
it is regenerated by script (`S/verify_pdfs_A.py` + `S/build_manifest_A.py`) and this section is
prose.**

### 0.3 File present but not text-searchable — now identified by eye

| File | Status |
|---|---|
| `Gatski1996_handbook_chapter6.pdf` (was `Gatski1993_explicit_algebraic_stress.pdf`) | 77 pages, 300-dpi bitonal **scan with no text layer** (`pdftotext` yields 77 bytes). No `tesseract`/`ocrmypdf` on this host, so it cannot be OCR'd. **Identity resolved 2026-08-20** by rendering page 1 with `pdftoppm -png -r 90 -f 1 -l 1` and reading it: it is **Gatski, ch. 6 "Turbulent flows: model equations and solution methodology", *Handbook of Computational Fluid Mechanics*, Academic Press 1996, pp. 339-414**. It is **not** Gatski & Speziale (1993) *J. Fluid Mech.* 254:59-78, which remains **MISSING**. The chapter *is* catalogued (Category A), quoting from rendered page images with printed page numbers; PDF page = printed page - 338. |

### 0.4 Still not on disk

**Superseded — read `MANIFEST.md` for the live list.** As of the end of this pass the
still-missing intended papers are recorded there with status `MISSING` or `WRONG-QUARANTINED`,
and each has a `BLOCKED-ON-SOURCE` stub block at the end of this catalogue.

**Recovered since the audit was first written**: `Ling2016_tbnn_embedded_invariance.pdf`
(Sandia SAND2016-7345J preprint of the TBNN paper) — the gap that was called the most damaging one
is closed, and the TBNN block below is written from the file, not from memory.

Anything this catalogue says about a paper not on disk is tagged
**`SECOND-HAND-UNVERIFIED`** (stated from memory, no number quoted) or the block is marked
**`BLOCKED-ON-SOURCE`** (not written at all). No number is ever quoted from a file not on disk.

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

---

### `Smagorinsky1963_general_circulation.pdf`

- **Category**: E (primary — the origin of the Smagorinsky SGS model), A (secondary).
- **Version**: **Journal of record** — *Monthly Weather Review* 91(3), March 1963, pp. 99-164. Page/equation numbers authoritative.
- **Method (one line)**: A two-level baroclinic primitive-equation general-circulation model of the atmosphere, in which sub-grid-scale transfer of momentum and heat is parameterised by a **non-linear lateral diffusion whose exchange coefficient is proportional to the local horizontal rate of strain** — the eddy viscosity that the LES community later renamed the Smagorinsky model.
- **Data used**: None in the training sense. Comparison is to observed atmospheric general-circulation statistics (cited datasets, e.g. Buch).
- **Cases / flows**: One 60-day integration of a baroclinic atmosphere on a sphere bounded by "smooth zonal walls at the equator and at approximately 64 deg latitude", two internal wind levels, one temperature, static stability as a parameter (Abstract, p. 99). Initial condition: random temperature disturbances on a zonally symmetric baroclinically unstable state. There is **no Reynolds number** in this paper — it is a geophysical calculation.
- **Metric**: Zonal-mean velocity profile, angular-momentum and heat transports, energy-cycle period, energy-transformation budget.

**Headline result with numbers**

1. **The model itself (eqs. 4.22-4.24, p. 105)**. The lateral viscous force uses an exchange coefficient built from the **magnitude of the horizontal deformation tensor**
   `|D| = sqrt(D_T^2 + D_S^2)`, with tension strain `D_T = du/dx - dv/dy` and shearing strain `D_S = dv/dx + du/dy`,
   **"and k_2 ~ 0.28"** — this constant, printed immediately after eq. (4.24), is the original numerical value of what is now called the Smagorinsky constant. Lateral heat diffusion is forced in the same way (eq. 4.26).
2. **The generalisation to arbitrary grid scale, p. 150** — the sentence the LES field actually inherited: "if we can assume that the grid scale lies within an inertial sub-range, i.e., there is a net transfer of energy to higher wave numbers in the neighborhood of the grid scale, then we may express the exchange coefficient in the form **`(k_2 Delta)^2 |D|`, where `k_2 ~ 0.1-1.0`**, `Delta` is the grid size and `D` is the deformation measured on grid scale." **Note the quoted range spans an order of magnitude in `k_2`, i.e. two orders of magnitude in the eddy viscosity.** Smagorinsky supports the extrapolation by noting the same formulation worked "for numerical integrations on the convective scale [22], where the grid scale was more than **1000 times smaller**".
3. **Purpose of the term, stated plainly, p. 150**: "The purpose for the introduction of the small-scale lateral diffusion was to simulate the physically real net cascade of energy from the larger than grid-size scale to the smaller scales which have been truncated by the discrete differencing." Without it, "a systematic accumulation of available potential and kinetic energy by the non-linear cascade would occur in the highest allowable spectral component, yielding what has been termed by Phillips as a **'non-linear computational instability'**." **The model is introduced as a numerical-stability device with a physical justification, not the other way round.**
4. **Circulation results (Abstract, p. 99)**: baroclinic instability selects **zonal wave number 5 to 6**; the index/energy cycle has a period of **11 to 12 days for the first 40 days**, "then lengthening to **17 days** while diminishing in amplitude". The mean zonal velocity profile is "in good qualitative agreement with observation, **but too intense**". The profile is "no more than **5 percent super-geostrophic** poleward of the angular momentum maximum and no more than **2 percent sub-geostrophic** equatorward". Total zonal angular momentum is constant "to within **2 percent** irrespective of the phase of the index cycle" (also p. 145: variations "within +/- 2 percent of their mean").
5. **Dissipation partition disagrees with observation (p. 149)**: "our model requires that as much as **almost half of the total energy dissipation must occur in the barotropic component**, or that **only 20 percent occurs in connection with surface stresses**. This is in **sharp contrast to estimates made from observation.** It is not clear whether the model dissipation mechanism or the empirical estimates are at fault for the discrepancy."

**Stated limitations (author's own words)**

- **The key admission, Abstract p. 99**: "The lateral transfer of momentum and heat by the non-linear diffusion, which parametrically is supposed to simulate the action of motions of sub-grid scale, accounts for a significant portion of the total eddy transfer. Although no direct comparison with the corresponding transfer in the real atmosphere is available, **intuitively our small-scale diffusion appears to play too large a role.**"
- **A named structural casualty of over-diffusion (p. ~146)**: "It is quite possible that any stronger tendency for a **double jet structure** in our calculations may have been **wiped out by too great a small-scale lateral diffusion coefficient.**"
- p. 149: "It is significant to note that despite the good agreement with observation of the poleward large-scale lateral eddy transfer of heat and momentum, our model **requires a significant transfer by sub-grid scale motions. No comparison with the corresponding transfer in the real atmosphere is available.**"
- The effective static stability of 0.8 standard is judged "too large"; a reduction to 0.6 standard would reduce the equilibrium vertical shear and bring the zonal wind maximum "to about 30 m/s" (p. ~146). So the headline zonal-wind error is attributed to a *different* parameter than the diffusion constant, and the two are not disentangled.
- p. 150: "It is, of course, important to be aware of the **sensitivity of this model to the empirically prescribed parameters**... These parameters include the viscous coefficients, the heating function, the static stability, and the rotation rate. Experiments in which these parameters are varied **will be described in subsequent reports**" — i.e. **no sensitivity study is in this paper**.

**What it cannot see**

- **`k_2` is not measured, it is chosen.** The paper gives `k_2 ~ 0.28` for its own grid and a range `0.1-1.0` for the general case; there is no calibration procedure, no a-priori DNS comparison (DNS did not exist), and no held-out test. Every later "Smagorinsky constant" value (Lilly's `C_s ~ 0.18`, the `C_s = 0.1` needed in channel flow, Nicoud & Ducros's `C_w ~ 0.5`) is a re-derivation, not a refinement of this number.
- **Single run, single parameter set, 60 days.** No ensemble, no seed variation, no grid-refinement study, no parameter sweep (explicitly deferred to later papers).
- **The model's own author judged the SGS transfer too large and could not check it** — there was no reference sub-grid transfer to compare against. This is the earliest instance in the corpus of the recurring problem that a closure's *contribution* is unobservable even when the mean flow looks right.
- **No wall.** The domain is bounded by smooth zonal walls with a slip-type treatment; there is no viscous sublayer, so the paper says nothing about the `nu_t = O(y^3)` near-wall requirement that later dominates SGS modelling (see Nicoud & Ducros below).
- **No realisability, no Galilean-invariance discussion**, no statement of what the strain-based coefficient does in pure shear (where it is famously non-zero and spuriously dissipative — the defect Nicoud & Ducros later fix).
- Read for the LES lineage this is a **secondary source about itself**: the LES form `nu_t = (C_s Delta)^2 |S|` is a later re-reading of eq. (4.22) with `|D| -> |S|` in three dimensions. Nothing in the 1963 paper validates that three-dimensional reading.

---

### `Nicoud1999_WALE_sgs.pdf`

- **Category**: E (primary), A (secondary), F (tertiary — near-wall behaviour is the paper's point).
- **Version**: **Journal of record** — *Flow, Turbulence and Combustion* 62:183-200, 1999. Page/equation numbers authoritative.
- **Method (one line)**: Replace the Smagorinsky strain-magnitude operator with one built from the **traceless symmetric part of the square of the velocity gradient tensor**, `S^d_ij`, chosen so that the eddy viscosity is a rotational-and-strain invariant, vanishes identically in pure shear, and scales as `y^3` at a wall with **no damping function and no dynamic procedure**.
- **Data used**: Comte-Bellot & Corrsin (1971) decaying-grid-turbulence spectra; Eggels et al. (1994) pipe-flow PIV. Six homogeneous-isotropic-turbulence LES fields (two 64^3, plus 128^3) used to calibrate the constant.
- **Cases / flows and Re**:
  - Freely decaying isotropic turbulence, 32^3 LES grid initialised by filtering a 256^3 no-model run; Taylor-microscale Reynolds number of the target experiment **71.6-60.6** (p. 191).
  - **Turbulent pipe flow**, radius `R`, length `4R`, streamwise-periodic, **Mach ~ 0.25, bulk Reynolds number `Re_b = 10000`** on the diameter, **`R+ ~ 320`**. Hybrid unstructured mesh: hexahedra for `r > 0.7R`, prisms in the core; 200 points azimuthally, 40 streamwise, **240 000 nodes**; `dx+ ~ 28`, `dr+ ~ 2.1` at the wall, `R dtheta+ ~ 8.8` (p. 192).
- **Metric**: Energy spectra; mean velocity in wall units and fitted `kappa`, `C`; rms velocities; `nu_t/nu` vs wall distance; achieved mass flow rate / effective Reynolds number.

**Headline result with numbers**

1. **The model (eq. 13, p. 189)**:
   `nu_t = (C_w Delta)^2 * (S^d_ij S^d_ij)^(3/2) / [ (S_ij S_ij)^(5/2) + (S^d_ij S^d_ij)^(5/4) ]`
   with `S^d_ij = (1/2)(g^2_ij + g^2_ji) - (1/3) delta_ij g^2_kk` (eq. 10) and, expanded via Cayley-Hamilton (eq. 12),
   `S^d_ij S^d_ij = (1/6)(S^2 S^2 + Omega^2 Omega^2) + (2/3) S^2 Omega^2 + 2 IV_S`.
   **The denominator's second term exists purely for conditioning**: "the ratio `OP1/(S_ij S_ij)^(5/2)` is **not well conditioned numerically since the denominator can (locally) tend to zero while `OP1` remains finite**... The second term in `OP2` is negligible near a wall but it **avoids numerical instabilities** because `OP2` does not go to zero for pure shear or (ir)rotational strain" (p. 189). Consequence stated in the Conclusion (p. 197): "the model is numerically well conditioned: **the eddy-viscosity can neither be negative nor infinite.**"
2. **Zero eddy viscosity in pure shear (p. 189)**. For `g_ij = 0` except `g_12`: `S^2 = Omega^2 = 4 S_12` and `IV_S = -(1/2) S^2 S^2`, so **the invariant is exactly zero**. Hence "almost no eddy-viscosity would be produced in the case of a wall-bounded laminar flow (Poiseuille flow)... **This is a great advantage over the Smagorinsky model which is unable to reproduce the laminar to turbulent transition of such flow because the invariant `S_ij S_ij` is large in the case of pure shear.**"
3. **Constant calibration, and its grid dependence (Table I, p. 190, and p. 191)**. `C_w^2/C_s^2` measured on six HIT fields: **10.81, 10.52, 10.84, 10.55, 10.70, 11.27** — i.e. `C_w` in **0.55-0.60** for `C_s = 0.18`. But the a-posteriori best value on decaying HIT was **`C_w ~ 0.5` on a 32^3 grid and `C_w ~ 0.45` on a 48^3 grid**. Authors' comment: "**This dependence on the grid size is not surprising. It is a feature which is shared by all the models with a constant fixed a priori and promotes the derivation of a dynamic version of the WALE model.**" `C_w = 0.5` is used thereafter. **So the a-priori estimate (0.55-0.60) and the a-posteriori optimum (0.45-0.50) disagree by 10-25%, and the optimum moves with the grid.**
4. **The decisive pipe-flow numbers (pp. 195-196)**:
   | Model | Achieved mass flow rate | Effective `Re_b` (nominal 10000) | Fitted `kappa` | Fitted `C` |
   |---|---|---|---|---|
   | Classical Smagorinsky (`C_s ~ 0.18`) | — | — | — | — (**complete relaminarization**) |
   | Filtered Smagorinsky (`C_2 ~ 0.37`) | **85% of expected** | **~8500** | 0.39 | ~4.5 |
   | **WALE (`C_w = 0.5`)** | **correct bulk velocity** | **~10000** | **0.416** | **~5** |
   The relaminarization is a *direct* experiment: "the solution from the WALE model at `t ~ 85 R/U_b` has been used as an initial condition for a calculation performed with the Smagorinsky model and `C_s ~ 0.18`. The result is **complete relaminarization of the flow**, confirming the poor behaviour of the classical formulation without constant adjustment" (p. 194). **A 15% mass-flow error and a 15% effective-Reynolds-number error is the price of the wrong near-wall scaling.**
5. **Near-wall scaling verified (Fig. 7, p. 196)**: `nu_t` is measured to be `O(r^3)` near the pipe wall; in the sublayer `nu_t` is **two orders of magnitude smaller than the molecular viscosity**, so the authors note the residual departure from `r^3` "could most likely not have a measurable effect on the results". Both Smagorinsky variants "produce a large amount of eddy-viscosity at the wall". Crucially, **"the three models lead to similar eddy-viscosity in the core region of the pipe, where the turbulence is nearly isotropic"** — the models differ only where it matters.
6. **Transition is captured**: from a Poiseuille profile plus **0.1% white noise**, instabilities grow to `t ~ 75 R/U_b`, transition occurs, and both filtered-Smagorinsky and WALE peak in kinetic energy and `omega_max` at `t ~ 90 R/U_b`; statistics accumulated over `150 R/U_b` after `t ~ 300 R/U_b` (pp. 193-195).
7. **Design constraints stated explicitly (p. 186)** — a useful checklist for any learned SGS operator: invariant to any coordinate translation or rotation; assessable on any grid; a function of both strain and rotation rates; goes to zero at the wall without damping or dynamics. Cost: "the overhead is only a **few percents**" (p. 198).

**Stated limitations (authors' own words, Conclusion pp. 197-198)**

- "The WALE model appears to be promising but **needs to be tested in more complex cases** to assess its potential for different types of flow."
- "In the case of a **laminar flow with a more complex 3D velocity gradient, there is no evidence that the WALE model (or any other SGS model) will give a reasonable answer.**"
- "The proper asymptotic behaviour of the eddy-viscosity has been clearly shown for the case of a solid wall. **As yet, there is no evidence that the WALE model can produce good results in the case of a free surface or a transpiring wall.**"
- "Also, the **generalization of this model to compressible flows is nontrivial**" — despite the pipe case being run at M ~ 0.25 in a compressible code.
- On the constant: grid-dependence of the optimal `C_w` "promotes the derivation of a dynamic version of the WALE model" (p. 191) — i.e. the authors concede the fixed constant is a compromise.

**What it cannot see**

- **Two flows only** — decaying HIT and one pipe. No separated flow, no adverse pressure gradient, no anisotropic core, no complex geometry, despite the model being *motivated* by complex geometries. The claim "well suited for LES in complex geometries" is an argument from the model's locality, **not a demonstration**.
- **One Reynolds number for the pipe** (`Re_b = 10000`, `R+ ~ 320`) — very low for LES, and low enough that the sublayer is nearly resolved (`dr+ ~ 2.1`). Nothing here tests WALE at the high `Re` where SGS modelling actually carries the solution.
- **The `nu_t/nu` comparison in Fig. 7 is a-priori for the competitors**: the Smagorinsky and filtered-Smagorinsky curves "have been obtained by applying the corresponding operators to a turbulent field obtained with the WALE model" (p. 196). Only WALE's curve is self-consistent; the other two are evaluated on a field they did not produce.
- **The `kappa` and `C` values are read off a plot**, not fitted with a stated range or uncertainty. `kappa = 0.416` vs `0.39` is quoted to three digits from Fig. 5 with no error bar and no sensitivity to the fitting window.
- **No ensemble / seed uncertainty** — one transition realisation from one white-noise seed. Transition timing is notoriously seed-sensitive, yet `t ~ 75` and `t ~ 90 R/U_b` are quoted as if deterministic.
- **The pure-shear-zero property is a double-edged sword and the paper does not test the downside**: a model that produces zero SGS dissipation in pure shear will also under-dissipate in genuinely turbulent regions that happen to be locally shear-dominated. The authors argue from Wray & Hunt that shear zones dissipate less, but supply no measurement of the resulting SGS-dissipation error.
- **`Delta` is "in practice the size of the mesh"** (p. 186) with no discussion of anisotropic cells, and the pipe grid is strongly anisotropic (`dx+ ~ 28` vs `dr+ ~ 2.1`). The filter-width definition on such a mesh is unaddressed.

---

---

### `Gatski1996_handbook_chapter6.pdf`

- **Category**: A (primary). Secondary: B — it is the chapter that states the Gatski & Speziale (1993) explicit algebraic stress model (EASM) in closed form, which is the analytic ancestor of every learned tensor-basis closure in category B.
- **Version**: **Journal/book of record** — Thomas B. Gatski, ch. 6 "Turbulent flows: model equations and solution methodology", in *Handbook of Computational Fluid Mechanics*, Academic Press Ltd, 1996, ISBN 0-12-553010-2, **pp. 339-414** (77 PDF pages; PDF page = printed page - 338).
- **Provenance warning**: this file was uploaded, and the old manifest recorded it, as **Gatski & Speziale (1993), *J. Fluid Mech.* 254:59-78**. It is not that paper. Identity established by rendering PDF page 1 to PNG and reading it: the chapter title, author, table of contents (I Introduction 339, II Incompressible turbulent modelling 341, III Compressible turbulent modelling 376, IV Numerical solution of turbulent model equations 395, References 411) and the footer "HANDBOOK OF COMPUTATIONAL FLUID MECHANICS / ISBN 0-12-553010-2 / 1996 Academic Press Ltd".
- **The file has no text layer.** It is a 300-dpi bitonal scan (`pdftotext` returns 77 bytes for 77 pages). It **cannot be grepped, quoted by text search, or machine-checked**. Every quotation below was read off a rendered page image and the printed page number is stated so it can be re-rendered and re-checked (`pdftoppm -png -r 100 -f <printed-338> -l <printed-338>`).
- **Method (one line)**: a review chapter, not a new model — it sets out the RANS hierarchy (two-equation, second-moment, algebraic) and the pressure-strain closures, then derives the explicit algebraic stress relation, and closes with the numerical solution methodology (pressure-velocity and density-velocity based).
- **Data / cases / metric**: none of its own; it is expository.

**Content that this lane needs, with printed page numbers**

1. **The Boussinesq approximation as the chapter states it (printed p. 360, eq. 34)**: `tau_ij = (2/3) K delta_ij - 2 nu_t Sbar_ij`. The chapter notes it "can also be obtained formally from a simple continuum mechanics approach (Speziale, 1991) by assuming that the stress tensor `tau_ij` is a tensor function of the mean velocity gradient and by assuming **single turbulent length and time scales that are spectrally distinct from the larger mean scales**. This single-scale assumption is the underlying basis contained in all standard turbulent closure models that are discussed."
2. **The square-duct failure of isotropic eddy viscosity, stated as the canonical example (printed p. 360)**: "A simple square-duct flow is an ideal example. **The two-equation formulation with an isotropic eddy viscosity predicts no secondary streamline pattern**; however, as Figure 4 shows, the qualitatively correct pattern is clearly predicted by the Reynolds stress model **because of the proper accounting of the normal stress differences in the flow**." *This is the exact mechanism the lab's round-5 duct chain relies on: the linear Boussinesq stress cannot produce the corner secondary flow at all, so an untrained quadratic constitutive term (QCR2000) supplies structure that no amount of fitting a linear-stress baseline can.*
3. **Why implicit ASM is numerically dangerous (printed p. 362)** — the sentence the lab's explicit-vs-implicit question turns on: "Rodi (1976) was the first to implement an **implicit** algebraic relationship with the LRR model. It led to a **non-constant coefficient `C_mu`** in the eddy-viscosity definition (31) ... **At each iteration (time) step, an additional inner iteration is required to solve for the appropriate `tau_ij` component. This iterative process can cause solution divergence**, and increased numerical overhead because of the extensive matrix inversions required at the different iteration levels."
4. **The Gatski & Speziale (1993) EASM in closed form (printed p. 362, eqs. 38, 39, 39a-c)**: for two-dimensional mean flow,
   `tau_ij = (2/3) K delta_ij - nu_t* ( S*_ij + (K/eps)[ (S*_ik W*_kj + S*_jk W*_ki) - 2( S*_ik S*_kj - (1/3) S*_kl S*_kl delta_ij ) ] )`
   with `nu_t* = [ 6(1 + eta^2) alpha_1 / (3 + eta^2 + 6 zeta^2 eta^2 + 6 zeta^2) ] K^2/eps`,
   `eta = (K/eps)(S*_ij S*_ij)^(1/2)`, `zeta = (K/eps)(W*_ij W*_ij)^(1/2)`,
   `S*_ij = (1/2) g (2 - C_3) Sbar_ij`, `W*_ij = (1/2) g (2 - C_4) Wbar_ij`.
   The chapter states the provenance explicitly: "Gatski and Speziale (1993) have developed an **explicit** constitutive relationship for the Reynolds stress tensor **with the ideas of Pope (1975)**, who proposed a tensorial polynomial expansion. ... **A 10-term polynomial representation, applicable to three-dimensional flows, which is quartic in products of the strain-rate and rotation-rate tensors, is found.**"
   Note that `nu_t*` is an explicit rational function of the two invariants `eta` and `zeta` — i.e. `C_mu` is not constant but is *given in closed form*, which is exactly the object that Pope (1975) plotted in his Fig. 1 and that TBNN learns pointwise.

**Stated limitations (author's own words)**

- On multiscale closures (printed p. 360): "Attempts have been made at multiscale closures (e.g. Hanjalic *et al.* (1979) and Wilcox (1986) with moderate success); however, their usage has been generally confined to the originators."
- On the Boussinesq relation (printed p. 360): it "assumes an isotropic eddy viscosity that is unable to account for strong anisotropies in the turbulence and results in **poor predictions in flows with secondary motions**. In addition, **body forces such as an imposed rotational field are also not properly accounted for** with the Boussinesq relationship. Furthermore, ... **the pressure-strain correlation term has disappeared in the two-equation formulation, which precludes the effects of intercomponent transfer between `tau_ij` components**."

**What it cannot see**

- **It is a review; it validates nothing.** No case, no Reynolds number, no error metric is produced by this chapter itself.
- **It is not the Gatski & Speziale (1993) paper**, so the EASM's own derivation, its regularisation of the singular denominator, and its validation cases are *not* on disk. Any statement about how the 1993 EASM behaves in practice is `SECOND-HAND-UNVERIFIED` until that paper is retrieved.
- **The 3-D 10-term form is asserted, not written out here** — only the 2-D quadratic reduction (eq. 38) is printed. The 3-D coefficients that TBNN and SpaRTA learn are therefore not available from this file.
- **No text layer** means no automated citation checking is possible against it, and any future agent that greps the corpus will silently miss this file. That is itself a corpus risk worth carrying.
- 1996 vintage: nothing about data-driven closure, and its "numerical solution methodology" section predates the coupled-solver practice the lane now uses.

## Category B — Data-driven RANS

---

### `Wang_Wu_Xiao2017_pinn_reynolds_stress.pdf`

- **Category**: B (primary), D (secondary — the target is a *discrepancy*, framed as model-form uncertainty), X (tertiary — it contributes a 10-feature set and a feature-importance study).
- **Version**: **arXiv preprint 1606.07987v2** (27 Feb 2017). Journal version: Phys. Rev. Fluids 2, 034603. **All locations below are arXiv preprint page/Table/Figure numbers and may differ from the published article.**
- **Method (one line)**: Train a **random forest** to map ten Galilean-invariant mean-flow features `q` to the discrepancy between RANS-modelled and DNS Reynolds stresses, where the discrepancy is expressed in **six physically interpretable projections** — magnitude `log k`, anisotropy shape `(xi, eta)` in the Barycentric triangle, and three orientation angles `phi_1, phi_2, phi_3` — and apply the learned discrepancy to a new flow.
- **Data used**: DNS/LES of four training flows plus two test flows (arXiv preprint Table 2, p. 21):
  | Training flow | Re | Source |
  |---|---|---|
  | Periodic hills PH1400 | 1400 | DNS, Breuer et al. |
  | Periodic hills PH5600 | 5600 | DNS, Breuer et al. |
  | Wavy channel WC360 | 360 | DNS, Maass et al. |
  | Curved backward-facing step CS13200 | 13200 | LES, Bentaleb et al. |
  | Square duct | 2200, 2600, 2900 | DNS |
  DNS for PH1400/PH5600 is available **only on vertical lines at eight streamwise stations `x/H = 1..8`**; WC360 and CS13200 have full fields but "only the lower part of the channel is adequately resolved", so **only `y/H < 1.2` is used** (arXiv preprint p. 22).
- **Cases / flows (test) and Re**: (1) square duct at **Re = 3500** (trained on Re = 2200/2600/2900, same geometry); (2) periodic hills at **Re = 10595**, in two scenarios — **Scenario I** trained on the same geometry at lower Re (PH1400, PH5600); **Scenario II** trained on *different geometries* (WC360, CS13200).
- **Metric**: Reynolds-stress projections and components (`tau_yy`, `tau_zz`, `tau_xy`, `k`) compared to DNS on line profiles. **No velocity metric is reported anywhere.**

**Headline result with numbers**

1. **Square duct, Re = 3500 (arXiv preprint Figs. 4-5, pp. 19-20)**. Baseline is the **Launder-Gibson Reynolds-stress transport model** (not a linear eddy-viscosity model — chosen because "all the linear eddy viscosity models are not able to capture the mean flow features of the secondary motions"), `y+ < 1`, quarter-domain by symmetry. Result: RSTM **overestimates both `tau_yy` and `tau_zz` over the entire domain**, with the `tau_yy` error largest near the wall and the `tau_zz` error largest far from the wall, so **the normal-stress imbalance `tau_yy - tau_zz` — the actual driver of the secondary flow — is "pronouncedly inaccurate"**. After correction, "the PIML predictions **nearly overlap with the DNS results** for both `tau_yy` and `tau_zz`". In the Barycentric map at `y/H = 0.75` the corrected anisotropy is "**almost identical to the DNS data**".
   *No number is given for the improvement. The claims are "nearly overlap" / "almost identical", read off Figs. 4-5. There is no RMS error, no percentage, no table.*
2. **Periodic hills, Scenario I (same geometry, lower Re) — arXiv preprint Figs. 7-8, pp. 24-25**. Baseline is the **Launder-Sharma k-epsilon** model. The baseline "underestimates the turbulence intensity along the free shear at `y/H = 1`, especially near the leeward side of the hill (`x/H = 1 to 2`)" and "underestimate[s] the peak of `tau_xy` on the leeward hill side but overestimate[s] it on the windward hill side". Corrected: "the predicted TKE profiles (solid lines) **nearly overlap with the DNS results**". Again **no error metric**.
3. **Periodic hills, Scenario II (different geometries) — the honest result, arXiv preprint Figs. 9-10, pp. 26-27**. In the recirculation region (`x/H = 2` to `6`) the correction works. **But**: "the PIML-predicted TKE **does not show any improvement and even deteriorates compared to the baseline** results near the windward side of the hill (`x/H > 7`), where the flow starts to be contracted... the predicted TKE is **markedly overestimated at `x/H = 8`**." Same for shear stress: "At `x/H = 7` and `8`, the magnitudes of turbulent shear stresses are **overestimated**".
   **Diagnosed cause, stated by the authors (p. 26): "the flow features in the contraction region (`x/H > 7`) are not supported in the training set, since the contracted flow does not exist in the training flow CS13200 and is much weaker in the training flow WC360."** This is a clean, named **extrapolation failure with a physical explanation** — the most transferable finding in the paper.
4. **Feature set (arXiv preprint Table 1, pp. 9-10)** — ten features `q1..q10`: `q1` Q-criterion (excess rotation over strain), `q2` turbulence intensity, `q3` wall-distance-based Reynolds number `Re_d = C_mu sqrt(k) d / nu`, `q4` pressure gradient along streamline, `q5` turbulent time scale, `q6` pressure-stress ratio, `q7` non-orthogonality of velocity and its gradient, `q8` ratio of total to normal Reynolds stresses, `q9` ratio of convection to production of TKE, `q10` streamline curvature. Derived from Ling & Templeton's twelve, **minus** vortex stretching and two eddy-viscosity-related features, **plus** curvature.
   - **Invariance rule stated explicitly (p. 10)**: "the input and thus the obtained regression functions should be **Galilean-invariant**. Quantities that satisfy this requirement include all scalars and the invariants (e.g., norms) of vectors and tensors." Worked example: neither `U_k` nor `dP/dx_k` is Galilean-invariant alone, but their inner product is (feature `q4`).
   - **Normalisation** (p. 11): `q_beta = q_hat_beta / (|q_hat_beta| + |q*_beta|)` — a **bounded, saturating** normalisation, so every feature lies in `[-1, 1]`; `q3` alone is left raw because it is already dimensionless.
   - **Realisability** is handled by construction: the anisotropy target lives in the **Barycentric triangle**, "all realizable turbulences are enclosed in" it (p. 507 of the text stream, arXiv preprint §2.4), and the Barycentric map is preferred over the Lumley triangle because the mapping is linear in the eigenvalues.
   - **Wall distance `d` is the one non-local feature** — the authors flag it: features are local "with the distance `d` to nearest wall being a notable exception".
5. **Regressor settings (arXiv preprint p. 16)**: **`N_rf = 100` trees, `M = 6` features sampled per tree**, with cross-validation to choose them and "sensitivity analysis to ensure that the predictions are not sensitive to the parameter choices" (**no numbers for either given**).
6. **Feature importance (arXiv preprint Fig. 11, p. 28)**: for the anisotropy discrepancy `Delta eta` the dominant feature is **`q3`, the wall-distance-based Reynolds number**; for `Delta log k` it is **`q2`, turbulence intensity**. The authors caveat this: feature importance "has its limitation due to bias introduced under certain conditions".

**Stated limitations (authors' own words, arXiv preprint §4.2, pp. 29-30)**

- **The decisive one**: "The improvement of the RANS-predicted Reynolds stress is considered a viable and promising path toward obtaining better predictions of velocities and other quantities of interest. However, due to a few limitations of the current framework, **the improvement of the propagated velocities from the corrected Reynolds stress field can not be guaranteed.** **A small region with abnormal Reynolds stress corrections (e.g., non-smoothness or artificial peaks) can introduce large errors to the velocity predictions.** For example, the small wave-number variations in Reynolds stresses are visible in Fig. 10. **These fluctuations, despite being small in amplitude, can lead to abnormal behaviors in the divergence term** and thus in the predicted velocities."
- Three named causes (p. 29): (i) features in the prediction flow not supported by the training flows; (ii) "**the random forest regression used here only provides pointwise estimations but cannot consider the spatial information of the Reynolds stress field. Therefore, the smoothness of the prediction cannot be guaranteed**"; (iii) "it is possible that the input features are **not rich enough**, and thus the randomness in the ensemble of the trained decision trees is significant."
- Conclusion, p. 31: "a number of challenges need to be tackled before the improved Reynolds stresses can be used to predict **more accurate quantities of interests that are needed in engineering design (e.g., dra[g] and lift coefficients). This topic will be investigated in future research.**"
- On the choice of features (p. 12): "the choices of features and normalization factors **heavily rely on physical** [reasoning]" — the authors point to Ling, Jones & Templeton's invariant-basis approach as the systematic alternative they did not take.

**Internal inconsistency to be aware of**

The training Reynolds numbers for Scenario I are given as **Re = 1400 and 5600** in Table 2 (p. 21) and in §3.2.1, but as **"Re = 2800 and 5600"** in §3.2.2 (p. 25) and again in the Conclusion (p. 30). One of these is a typo and the paper does not resolve it. **If reproducing, use Table 2 (1400 and 5600) and say so.**

**What it cannot see**

- **This is an a-priori study end to end.** Every figure compares Reynolds stresses. **The corrected stresses are never substituted back into the momentum equation, and no velocity field, no separation-bubble length, no drag or lift is reported.** The authors say the velocity improvement "can not be guaranteed". Any claim that this method improves flow predictions is not supported by this paper.
- **Directly relevant to this lab**: the failure mode the authors name — small-amplitude, high-wavenumber noise in a pointwise-predicted stress field producing large errors through the **divergence** term — is the same mechanism behind the **~10% RMS `div(U)`** the lab recorded for its own post-hoc correction (`METHOD.md` §6). A pointwise regressor has no mechanism to enforce a divergence constraint or spatial smoothness, and both papers reach that wall independently.
- **No continuity or realisability check on the corrected field.** Realisability is guaranteed for the *anisotropy shape* by the Barycentric parameterisation, but there is no verification that the reconstructed tensor field is smooth, that the corrected momentum equation is well posed, or that `div(tau)` is bounded.
- **Train/test leakage risk is low but the split is weak.** In the square-duct case, training and test differ only in Reynolds number (2200/2600/2900 -> 3500, a factor of 1.6) *in the same geometry with the same solver and the same mesh family*. Scenario I likewise. **Only Scenario II is a genuine geometry generalisation test, and that is the one that fails in the contraction region.**
- **No seed or ensemble uncertainty.** A random forest has two stochastic sources (bootstrap and feature subsampling); results are from one forest. The claimed insensitivity to `N_rf` and `M` is asserted without numbers.
- **Two of three test configurations use a different baseline model** (Launder-Gibson RSTM for the duct, Launder-Sharma k-epsilon for the hills). The learned discrepancy is therefore **baseline-model-specific** — it encodes "the error of *this* model", not a property of turbulence. Nothing tests transfer of a discrepancy function across baseline models.
- **DNS truth for the hill cases exists only on 8 vertical lines**, so the "full-field" correction is trained and assessed on a sparse sample of the domain; the upper channel in Scenario II is excluded outright.
- **Square-duct Re is very low** (2200-3500 on bulk velocity and duct edge) — near the lower limit at which the secondary flow is turbulent at all. Nothing here tests the duct correction at engineering Re.

---

## Category B — Data-driven RANS (continued)

---

### `Ling2016_tbnn_embedded_invariance.pdf`

- **Category**: B (primary). Secondary: A — it is Pope (1975) §3 turned into a network architecture; X (tertiary — the 5-invariant input set is a feature-selection statement).
- **Version**: Sandia preprint **SAND2016-7345J**, dated 24 July 2016, 17 pp. Journal of record is *J. Fluid Mech.* 807:155-166. **Page/Table numbers below are the SAND preprint's printed page numbers and may differ from JFM.**
- **Method (one line)**: A deep network takes the five scalar invariants `lambda_1..lambda_5` of the RANS-computed, `k`/`epsilon`-normalised strain `S` and rotation `R`, emits ten scalar coefficients `g^(n)` from a 10-element final hidden layer, and multiplies them element-wise against a separate *tensor input layer* holding Pope's ten basis tensors `T^(1)..T^(10)`, summing in a merge layer to give the anisotropy `b_ij` — so the representation `b = sum g^(n)(lambda) T^(n)` is enforced by the architecture, not by the loss.
- **Data used**: a database of **9 flows**, each with both a RANS (k-epsilon + LEVM) solution and a DNS or well-resolved LES (preprint p. 8). **Training = 6 cases**: duct `Re_b = 3500`; channel `Re_tau = 590`; perpendicular jet in crossflow; inclined jet in crossflow; flow around a square cylinder; converging-diverging channel. **Validation = 1 case** (used only for Bayesian hyper-parameter optimisation): wall-mounted cube in crossflow, bulk `Re = 5000`. **Test = 2 cases**: duct `Re_b = 2000`; wavy wall `Re = 6850`. **The number of training points is not stated anywhere in the paper.**
- **Cases / flows and Re**: as above. A-posteriori propagation was done in Sandia's in-house RANS code **SIERRA Fuego**, with the predicted `b` entering "the momentum equations and in the turbulent kinetic energy production term" (preprint p. 12).
- **Metric**: RMSE of the anisotropy tensor `b_ij` against DNS (a-priori). A-posteriori results are secondary-flow vector plots and streamwise-velocity contours only.

**Headline result with numbers**

1. **Table I, preprint p. 11 — RMSE of `b` on the two held-out flows** (this is the paper's entire quantitative content):

   | Model | duct `Re_b = 2000` | wavy wall `Re = 6850` |
   |---|---|---|
   | LEVM | 0.23 | 0.18 |
   | QEVM (Craft cubic) | 0.18 | 0.11 |
   | **TBNN** | **0.13** | **0.08** |
   | plain MLP | 0.33 | 0.09 |

   Stated in the text as "**43% more accurate than the LEVM and 28% more accurate than the QEVM**" for the duct (p. 11) and "a **56% reduction** in error with respect to LEVM and a **27% reduction** with respect to QEVM" for the wavy wall (p. 12).
2. **The plain MLP is worse than the linear baseline on the duct** — 0.33 vs LEVM's 0.23. Feeding the nine raw components of `S` and `R` into a generic network and asking for `b` *degrades* the prediction relative to doing nothing. **This is the strongest single argument in the corpus for embedding the tensor basis rather than learning it**, and it is a within-paper controlled comparison (same data, same optimiser family, same hyper-parameter search).
3. **Architecture and hyper-parameters (exact)**: TBNN **8 hidden layers x 30 nodes**, learning rate **2.5e-7**, **stochastic** gradient descent with weights updated after each training point (chosen because of the multiplicative merge layer), leaky ReLU throughout (preprint pp. 4, 8). Baseline MLP **10 hidden layers x 10 nodes**, learning rate **2.5e-6**, mini-batch gradient descent (p. 6). Hyper-parameters (n layers, n nodes, learning rate) selected by Bayesian optimisation with the **Spearmint** package (p. 5). **Epochs, batch size, regularisation constants are not stated.**
4. **Invariance, exactly as claimed (preprint pp. 6-8)**: the basis is Pope's, written out in full — `lambda_1 = Tr(S^2)`, `lambda_2 = Tr(R^2)`, `lambda_3 = Tr(S^3)`, `lambda_4 = Tr(R^2 S)`, `lambda_5 = Tr(R^2 S^2)`, with `S` and `R` non-dimensionalised by `k` and `epsilon` "as suggested by Pope" (p. 4). The paper asserts "Any tensor `b` which satisfies this condition will automatically satisfy Galilean invariance" (p. 7) and "This innovative architecture ensures that Eq. 1 is satisfied, thereby guaranteeing the Galilean invariance of the network predictions" (p. 8). **The paper uses "rotational invariance" and "Galilean invariance" interchangeably in this passage. Reflectional invariance is not discussed at all.**
5. **Baseline QEVM** is the Craft cubic model, Eq. (3), p. 9, with coefficients **`C1 = -0.1`, `C2 = 0.1`, `C3 = 0.26`**.
6. **The LEVM predicts identically zero `b11, b22, b33, b12` in the duct** (p. 9) — the structural failure Pope (1975) p. 332 quantified, reappearing as the reason the duct is the test case.

**Stated limitations (authors' own words)**

- p. 13: "In this test case, then, while the TBNN provides improved secondary flow predictions, **it is still not able to correctly capture the strength and shape of the corner vortices.**"
- p. 13: "**TBNN predicts flow separation, though in a smaller region than the DNS.**"
- p. 12: "Notably, **the Reynolds stress anisotropy is not the only source of uncertainty in the RANS equations**, which also relies on approximate transport equations for `k` and `epsilon`."
- p. 15: "In order for this innovative approach to reach its full potential, **the TBNN needs to be trained and tested across a much broader set of flows.**"
- On classical nonlinear models, p. 2: "These non-linear models have not gained widespread usage because they do not give consistent performance improvement over the LEVM and **often lead to worsened convergence and stability properties.**"

**What it cannot see**

- **No a-posteriori error number exists.** Table I is a-priori. The propagated results (Figs. 6-7, pp. 13-14) are vector and contour plots with a reference arrow of length `U_b/10` and no error metric. Any claim that TBNN improves velocity *by X%* is not in this paper.
- **No realisability enforcement, no conditioning analysis, no discussion of the divergence or continuity of the corrected stress field, and no explicit-vs-implicit treatment.** The predicted `b` is inserted and the solver is run; nothing checks whether the RANS system remains well-conditioned. Contrast Wu 2018 and Kaandorp 2020 below, both of which found this to be the controlling issue.
- **The paper claims random forests "cannot easily enforce Galilean invariance for a tensor prediction" (p. 2). Kaandorp & Dwight 2020 refute this directly** by building a tensor-basis random forest that beats this TBNN on the same metric. Record the claim as superseded.
- **`ARCHITECTURE DISCREPANCY — RECORD, DO NOT RESOLVE`**: Kaandorp & Dwight 2020 (preprint pp. 16-17) state that *this* paper's TBNN has **10 hidden layers, learning rate 2.5e-5, Adam, mini-batch 1000**. The SAND preprint on this disk says **8 hidden layers x 30 nodes, learning rate 2.5e-7, per-point stochastic gradient descent**, and attributes 10 layers / 2.5e-6 to the *MLP baseline*. These cannot both describe the same network. The JFM published version may differ from the SAND preprint. **For any reproduction, quote the on-disk SAND numbers and state that Kaandorp's differ.**
- **No compute cost, no mesh sizes, no training-point count, no train/test split fractions, no seed variance.** One network, one result per case.
- **The 9-flow database is not distributed as an archive** and is not on this machine (see `cases/RANS_LES_closure_models/_common/FEASIBILITY.md` §1.1). The RMSE 0.13 is therefore **not a target this lab can hit or miss** — only the method reproduces, not the number.

---

### `Wu2018_physics_augmenting.pdf`

- **Category**: B (primary). Secondary: D (the learned object is a *discrepancy*, parameterised for UQ); X (it contributes the 47-invariant + 3-scalar feature set).
- **Version**: **arXiv preprint 1801.02762v4** (9 Sep 2018), 42 pp. Journal: *Phys. Rev. Fluids* 3:074602. **All locations below are arXiv preprint page/Table numbers.**
- **Method (one line)**: A random forest maps **50 normalised invariant mean-flow features** from a baseline RANS run to six rotationally invariant Reynolds-stress *discrepancy* components (`Delta log k`, `Delta xi`, `Delta eta`, and three orientation components `h1, h2, h3`), where the anisotropy is first **split into a linear (eddy-viscosity) part and a remainder**, `b = nu_t^L S + b_perp` (arXiv preprint Eq. 3, p. 7), with the *optimal* eddy viscosity obtained by projection, `nu_t^L = 2 (b:S)/(||S|| ||S||)` (Eq. 5, p. 7) — defined as `nu_t^L = argmin_{nu_t} ||b - nu_t S||_F` (Eq. 4) — so that the linear part can be treated **implicitly** in the momentum equation and only the remainder is an explicit source.
- **Data used**: DNS and one experiment; **three separate train/test pairs**, one training flow at a time (arXiv preprint Table 3, p. 18):
  | Case | Train | Test |
  |---|---|---|
  | 1 | square duct `Re = 2200` (Pinelli DNS) | square duct `Re = 3500` (Pinelli DNS) |
  | 2 | square duct `Re = 2200` | square duct `Re = 125000` (Gessner & Emery **experiment**) |
  | 3 | periodic hills `Re = 5600`, **steeper hill, hill width 0.8x the test geometry** | periodic hills `Re = 5600`, standard geometry |
  Baseline RANS: **Launder-Gibson Reynolds-stress transport** for the ducts, **Launder-Sharma k-epsilon** for the hills (p. 16). `y+` of the first cell centre kept **< 1**, no wall model (p. 18). "In this work, only one training flow is used at one time" (p. 15). **Number of training points and train/test split: not stated.**
- **Cases / flows and Re**: as above — a `Re` extrapolation of **57x** (2200 -> 125000) and a geometry transfer at fixed `Re`.
- **Metric**: velocity and Reynolds-stress **profiles**, plus one separation-bubble length. **There is no error table anywhere in this paper.**

**Headline result with numbers**

1. **The only hard a-posteriori number in the paper (arXiv preprint p. 29, periodic hills)**: DNS reverse flow "extends to `x/H = 4`"; baseline RANS reverse flow "ends approximately around `x/H = 3`"; the ML prediction "provides more accurate reverse flow, especially from `x/H = 1` to `x/H = 3`", with **over-prediction from `x/H = 3` to `x/H = 4`**. Everything else is a line or contour plot.
2. **The feature set, in full (arXiv preprint Table B.4, p. 36, and Table 2, p. 10)**: tensorial input set `Q = {S, Omega, grad p, grad k}`, with `grad p` and `grad k` first mapped to antisymmetric tensors (`A_p = -I x grad p_hat`, `A_k = -I x grad k_hat`, Eq. B.1, p. 35). The minimal integrity basis of that set has **47 invariants**, indexed in the paper by `(n_S, n_A)`: (1,0) -> 1-2; (0,1) -> 3-5; (1,1) -> 6-14; (0,2) -> 15-17; (1,2) -> 18-41; (0,3) -> 42; (1,3) -> 43-47. Plus **3 supplementary scalars**: `q1` wall-distance Reynolds number `min(sqrt(k) d/(50 nu), 2)` (left raw), `q2` turbulence intensity, `q3` `k/epsilon`. **Total = 50 features** (p. 13).
3. **Invariance, stated precisely (arXiv preprint p. 10)**: "**Our formulation has rotational invariance and Galilean invariance but not reflectional invariance.**" Reflection is deliberately sacrificed because the eigenvector-rotation output (a unit quaternion) has no reflection invariance. The proposed remedy is data augmentation, and the paper prices it: reflection would be "a **moderate two-fold increase**", whereas achieving 3-D rotational invariance by augmentation "required duplicating the training data in **1000 coordinate systems**, as is shown by Ling et al." (p. 13). **This is the clearest cost statement in the corpus for invariance-by-augmentation versus invariance-by-construction.**
4. **Normalisation (Eq. 8, p. 9)**: `alpha_hat = alpha / (|alpha| + |beta|)`, so every feature lies in `[-1, 1]`; normalisers (Table 1, p. 9) are `S -> epsilon/k`, `Omega -> ||Omega||`, `grad p -> rho |DU/Dt|`, `grad k -> epsilon/sqrt(k)`. **The Galilean invariance of the `rho |DU/Dt|` normaliser is proved in Appendix C** (Eqs. C.1-C.3, p. 37) — and the Acknowledgment (p. 33) records that "one of the reviewers pointed out the lack of Galilean invariance in two of the normalization constants in our manuscript, which we fixed during the revision." **An invariance defect survived to submission in the paper that makes invariance its selling point.**
5. **Regressor (arXiv preprint §2.4, p. 15)**: random forest as implemented in **R**; **max features = 7** (`floor(1 + log2 50)`); **300 trees**, chosen by watching the out-of-bag error. Code at `github.com/xiaoh/turbulence-modeling-PIML`.
6. **The propagation experiment — the paper's most valuable content (arXiv preprint §3.2, pp. 18-22)**. DNS Reynolds stresses are substituted into the solver, i.e. the *ideal* data-driven closure with zero modelling error. Square duct: explicit RSM treatment "agrees well with DNS data within most regions, except along the symmetry plane `y/h = 1`". **Periodic hills: "the solved mean velocity field does not agree with the DNS data by using Reynolds stress model with explicit treatment"** (p. 20, Fig. 4a); the eddy-viscosity form is better but "noticeable differences can still be observed" (Fig. 4b); **RSM with implicit treatment "has a much better agreement with DNS data"** (Fig. 4c). *A perfect stress field, inserted explicitly, produces a wrong velocity field. Inserted implicitly, it does not. That is the whole argument for the `nu_t^L` split.*
7. **Explicit vs implicit, defined by the authors (arXiv preprint p. 18)**: "The **explicit** treatment means that the modeled Reynolds stress is directly substituted into the RANS equations ... **merely updating the Reynolds stress explicitly based on the solved mean velocity would not improve the conditioning of the RANS equations.** ... The **implicit** treatment means that the modeled Reynolds stress implicitly depends on the strain rate through an optimized eddy viscosity. Such an implicit treatment would improve the conditioning ... since the optimized eddy viscosity **has impact upon the coefficient matrix of the discretized RANS equations and thus influences the condition number.**" Implementation: modified OpenFOAM `simpleFoam`, `tau^m = nu_t^L S + (tau - tau^L) + tr(tau)`, and "**The strain rate tensor S is treated implicitly in the modified flow solver**" (Appendix A, p. 35).
8. **Borrowed numbers on the ill-conditioning problem (arXiv preprint p. 3)**: Thompson et al. propagated DNS Reynolds stresses in channel flow over **`Re_tau = 180 to 5200`** and found the propagated mean velocities "deviate significantly", "especially ... at high Reynolds numbers (notably `Re_tau = 5200`)"; Poroseva reported discrepancies "for flows at Reynolds numbers as low as **`Re_tau = 395`**"; and "errors in DNS Reynolds stress are typically less than **0.5%**". **These are citations, not measurements made here.**
9. **The ad-hoc-blending criticism (arXiv preprint p. 4)**: Jakirlic-type `tau = alpha tau_RSM + (1-alpha) tau_LEM` is rejected because "the specification of a blending factor `alpha` is **largely ad hoc and lacks physical basis**". **No blending factor is used in this paper** — the implicit split is offered as the principled alternative. Note that Kaandorp 2020 below *does* use exactly such a blending factor and calls it ad hoc in the same words.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 26: "**However, it should be noted that the test flow is at Reynolds number `Re = 3500`, close to that of the training flow (`Re = 2200`). Therefore, the satisfactory predictive capability ... does not necessarily guarantee similar performance at a higher Reynolds number.**"
- p. 31: "To our knowledge, **most existing data-driven turbulence models, including the one presented in our work, are still in their infancy and have shown only limited predictive capabilities, typically in flows that are close to the training flows.**"
- p. 15: "**Because of the dependence of the trained machine learning function on the RANS model, we recommend the usage of the same RANS model for both the training flows and the flow to be predicted.**"
- p. 12: "it would be more elegant to include only objective inputs and output in the machine learning ... **Further work is needed in identifying such formulations**"; and "the different conventions of coordinate system handedness would lead to different machine learning inputs even with identical training and test flows."
- p. 27: "Although there is no significant improvement of results along the diagonal, it should be noted that the machine learning prediction ... **indeed corrects the baseline RANS simulated results towards the right direction.**"

**What it cannot see**

- **`FLAG F16` — this paper contains NO condition-number analysis and no condition-number values.** A full-text search for "condition number" returns exactly two narrative sentences, both on p. 3. The quantitative conditioning work (local condition-number function, its Reynolds-number dependence, why the matrix condition number fails to explain it) lives in the **separate** paper Wu, Xiao, Sun & Wang, *RANS equations with explicit data-driven Reynolds stress closure can be ill-conditioned*, arXiv:1803.05581 — which **has now been retrieved and is catalogued under Category D below**. Do not attribute condition numbers to this file.
- **No RMSE, no L2 error, no error table of any kind.** Every result is a profile plot. The lab cannot compare its own error numbers against this paper's, because this paper has none.
- **No realisability enforcement is discussed** (though the `Delta log k` parameterisation guarantees `k >= 0` and the barycentric `xi, eta` parameterisation bounds the eigenvalues). **Divergence/continuity of the corrected stress field: not discussed** — the same gap Wang, Wu & Xiao 2017 named as their controlling failure mode.
- **Baseline-model-specific by the authors' own recommendation.** The learned function encodes the error of *one* RANS model on *one* flow; the authors say to use the same model for training and prediction. Nothing tests transfer of a discrepancy across baseline models.
- **The `Re = 125000` extrapolation is validated against an experiment, not DNS**, so the "truth" carries experimental uncertainty that is not quantified here.
- **No mesh sizes, no CPU hours, no seed/ensemble variance.** Compute is stated qualitatively only: training "is less than the corresponding standard RANS simulation" and prediction is "negligible" (p. 15).

---

### `Schmelzer2020_algebraic_reynolds.pdf`

- **Category**: B (primary). Secondary: A — the output is a closed-form algebraic stress model, i.e. a *discovered* EASM in the Pope/Gatski-Speziale sense.
- **Version**: **arXiv preprint 1905.07510v2** (28 Feb 2020), 29 pp. Journal: *Flow, Turbulence and Combustion* 104:579-603. **All locations below are arXiv preprint page/Table numbers.**
- **DUPLICATE ON DISK (`FLAG F13`)**: `Schmelzer2020_sparta_sparse_symbolic_regression.pdf` is **byte-identical** to this file (sha256 `7aca1f9a1f40dc4c67c12f83f2c05fe85cecf6527e1107129bb831b68def1208` for both). One catalogue entry, one manifest row; see the report at the end of this document for the recommended filename.
- **Method (one line)**: Deterministic **sparse symbolic regression** (elastic-net model *selection* followed by ridge-regression coefficient *inference*) over a library of tensor-polynomial candidates, fitted to two additive corrections to k-omega SST that are first extracted from full-field LES/DNS by a procedure the authors call **k-corrective-frozen-RANS**: an anisotropy correction `b_ij = -(nu_t/k) S_ij + b^Delta_ij` (arXiv preprint Eq. 3, p. 5) and a **residual `R` in the k-equation** that also enters the omega-equation, `R = 2k b^R_ij d_j U_i` (Eq. 11, p. 8).
- **Data used**: full-field LES/DNS produced by other authors — **PH10595** periodic hills `Re = 10595` (Breuer LES, mesh 120 x 130), **CD12600** converging-diverging channel `Re = 12600` (Laval & Marquillie DNS, mesh 140 x 100), **CBFS13700** curved backward-facing step `Re = 13700` (Bentaleb LES, mesh 140 x 150). Extrapolation case: **PH37000**, periodic hills `Re = 37000`, Rapp & Manhart **experiment**. Data volume `K ~ 15000` points (p. 11). Cross-validation is **leave-one-case-out using CFD**, not point-wise.
- **Cases / flows and Re**: three separating flows at `Re` 10595-13700 plus one `Re = 37000` extrapolation.
- **Metric**: **normalised mean-squared velocity error `eps(U)/eps(U_0)`**, where `U_0` is the uncorrected k-omega SST baseline. This is the cleanest metric in the corpus: 1.0 = no improvement, 0.0 = perfect.

**Headline result with numbers**

1. **Table 1, arXiv preprint p. 6 — the frozen-field CEILING.** With `b^Delta_ij` and `R` injected as *static fields* (i.e. the best any model of this form could do), re-solved:

   | Case | `eps(U_i) x 1e-5` | **`eps(U_i)/eps(U_i^0)`** | `eps(tau_ij) x 1e-6` | `eps(tau_ij)/eps(tau_ij^0)` |
   |---|---|---|---|---|
   | PH10595 | 1.74 | **0.00165** | 36.7 | 0.1495 |
   | CD12600 | 31.4 | **0.0229** | 7.21 | 0.4781 |
   | CBFS13700 | 59.6 | **0.22703** | 1.34 | 0.4949 |

2. **Table 2, arXiv preprint p. 15 — the discovered sparse models, re-solved in OpenFOAM** (rank among all models tried, in parentheses):

   | Model | PH10595 | CD12600 | CBFS13700 |
   |---|---|---|---|
   | M(1) | (1.) **0.22287** | (19.) 0.21146 | (-) 0.30413 |
   | M(2) | (-) 0.38867 | (1.) **0.20828** | (26.) 0.40154 |
   | M(3) | (3.) 0.22744 | (-) 0.22422 | (1.) **0.30655** |

   Text, p. 20: "the best models correct the velocity **up to 5 times better** in mean-squared error than the k-omega SST baseline model." All three best models have `eps(U)/eps(U_0) < 0.5` (p. 21).
3. **The gap between the ceiling and the achievement is the number the lab should carry.** On PH10595 the frozen field reaches **0.00165** and the best *discovered* model reaches **0.22287** — the symbolic model recovers only about **1/135th** of the extractable correction, measured in normalised MSE. The authors say so: "This leaves still room for further improvement compared to the error using the frozen data sets, see Table 1" (p. 20). *On CBFS13700 the ceiling is 0.22703 and the best model is 0.30655 — there the model is close to the ceiling, and the ceiling itself is poor.*
4. **Basis truncation (arXiv preprint p. 6, Eqs. 9-10, p. 8)**: "**Only the first four base tensors and the first two invariants are used in this work**" — `T(1) = S`, `T(2) = SOmega - OmegaS`, `T(3) = S^2 - (1/3)delta tr(S^2)`, `T(4) = Omega^2 - (1/3)delta tr(Omega^2)`; `I1 = tr(S^2)`, `I2 = tr(Omega^2)`. Timescale `tau = 1/omega`.
5. **Library and regression hyper-parameters (exact)**: raw feature vector `B` of **16 functions** of `I1, I2` up to degree **6** (Eq. 12, p. 9); library `|C^Delta| ~ 64` candidates (16 functions x 4 base tensors). Elastic net (Eq. 20, p. 11) with **`rho` in {0.01, 0.1, 0.2, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0}** (9 values) and a **`lambda` vector of 100 log-spaced entries** from `lambda_0 = 1e-3 lambda_max` (Eq. 22); coordinate-descent solver. Ridge inference with Tikhonov parameter in **`0.01 < lambda_r < 0.1`** (p. 13; *the paper prints the inequality reversed*).
6. **Model counts (arXiv preprint pp. 14-16)**: sparse regression yielded **52, 114 and 136** distinct `b^Delta` models for PH10595, CBFS13700 and CD12600; **18 and 19** `R` models for CD12600 and PH10595, and **only three** for CBFS13700. The authors then "**in an ad-hoc way, hand-select** 5 models for `b^Delta` and 3 for `R`, except for CBFS13700 only 1" (p. 15), giving 23 (or 11) model combinations per training case and **35 to 47 CFD runs per test case**.
7. **The discovered models, in full (arXiv preprint Eqs. 25-27, p. 21)** — e.g. `M(1)_{b^Delta} = (24.94 I1^2 + 2.65 I2) T(1) + 2.96 T(2) + (2.49 I2 + 20.05) T(3) + (2.49 I1 + 14.93) T(4)`, `M(1)_R = 0.4 T(1)`. **These are three-to-ten-term closed-form expressions — the only models in the corpus that can be typed into a solver dictionary and read by a human.**
8. **Extrapolation (arXiv preprint Fig. 12, p. 26)**: on **PH37000** — 3.5x the training Reynolds number, against experiment — "the three models improve significantly compared to the baseline. Interestingly, the model `M(2)` is delivering the best fit of the data" (p. 22). **Numbers for this case are shown graphically only.**
9. **Cost (arXiv preprint p. 11)**: the model-selection step at `K ~ 15000` takes "of the order of **a minute on a standard consumer laptop**". The expensive part is the CFD cross-validation sweep, whose wall-clock is not stated.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 13: "the identified models are also **not guaranteed to converge a priori for any other test case outside the training set**."
- p. 13, the convergence rescue, quoted in full because it is a numerics fact: "Our efforts are based on an empirical observation, but **do not guarantee a well-behaving numerical setup under all conditions**. However, we have identified corrections of `b^Delta_ij` as the only contribution which can do harm to the convergence properties for the given test cases. Therefore, **if a model does not converge, we further decrease the coefficients by a factor `xi = 0.1`**, for the model correcting `b^Delta_ij` only. This **ad-hoc intervention** is sufficient to achieve convergence for the studied cases."
- p. 10, on why sparsity is a numerics requirement and not an aesthetic one: "Due to multi-collinearity between the candidates, `C_Delta` can be **ill-conditioned**, so that the coefficients may also display large differences in magnitude ... Such models are **unsuitable to be implemented in a CFD solver as they increase the numerical stiffness of the problem and impede convergence of the solution.**"
- p. 6 / p. 3: "The k-corrective-frozen-RANS approach **requires full-field data**" — it "is therefore very efficient, but also **limited to full-field data**."
- p. 21: "The magnitude of the Reynolds-stress component `tau_xy` is **underestimated on the curved surfaces of all test cases**. For PH10595 the models **fail to fit the complex spatial structure** especially within the separated shear-layer behind the hill and on the hill itself." And: "For CD12600, we observe a small recirculation zone as reported in the literature, but **too far downstream.**"
- p. 15: "**In an ad-hoc way, we hand-select** ..." (quoted above).

**What it cannot see**

- **The model-selection pipeline contains two hand steps.** Hand-selecting 5+3 models out of 52-136, and shrinking coefficients by 0.1 when CFD fails to converge, are both described by the authors as ad hoc. **The reported `eps(U)/eps(U_0)` numbers are therefore post-selection, and the selection used the a-posteriori CFD result.** There is no held-out flow that was never seen by the selection step except PH37000, whose result is graphical.
- **No Galilean/rotational/reflectional invariance claim is made for the discovered models.** The word "Galilean" appears once, in the literature review of Ling et al. (p. 3). Invariance is inherited implicitly from the Pope ansatz and is never checked.
- **No realisability treatment, no condition numbers, no divergence/continuity check** on the corrected field. The correction is additive to k-omega SST, so the linear Boussinesq term stays implicit by construction — but the paper never frames it that way and supplies no conditioning evidence.
- **Only four of Pope's ten tensors and two of the five invariants are used.** The model class is a 2-D-complete quadratic form; genuinely three-dimensional anisotropy (the duct corner problem) is outside it by construction, and no duct case is tested.
- **Three training flows, all separating, all 2-D, `Re` 10595-13700.** No duct, no jet, no boundary-layer-only case, no 3-D flow, no compressibility.
- **The CBFS ceiling is poor (0.227) and nobody explains why.** For that case the frozen field — the theoretical best — still leaves 23% of the baseline error, so the correction *form* (an algebraic `b^Delta` plus a k-equation residual) is inadequate there, independent of any regression.

---

### `Kaandorp2020_random_forests.pdf`

- **Category**: B (primary). Secondary: D (realisability analysis); X (three explicit feature sets, with an ablation).
- **Version**: **arXiv preprint 1810.08794v2** (17 Mar 2020), 58 pp. Journal: *Computers & Fluids* 202:104497. **All locations below are arXiv preprint page/Table numbers.**
- **Method (one line)**: A **Tensor Basis Random Forest (TBRF)** — a modified CART regression tree whose leaves store not a scalar but the **ten Pope coefficients `g^(m)`**, each obtained by solving a per-bin least-squares problem `g = (sum T_i^T T_i)^-1 (sum T_i^T b_i)` (arXiv preprint Eq. 11, p. 19), with split cost the Frobenius mismatch between the tensor-basis reconstruction and the DNS/LES `b`; the forest returns the **median** (not mean) over trees, the result is **Gaussian-smoothed**, and is then blended into a modified OpenFOAM SIMPLE solver.
- **Data used**: five flow families (arXiv preprint §3.1, pp. 27-28) — periodic hills (Breuer) at **five `Re` from 700 to 10595**; converging-diverging channel `Re = 12600`; curved backward-facing step `Re = 13700`; backward-facing step `Re = 5100` (Le et al. DNS); square ducts (Pinelli) — **sixteen datasets from `Re = 1100` to `Re = 3500`**. **All four reported cases train on PH5600 + PH10595 + CD12600 with `N_sample = 21,000`** (Table 2, p. 31). Hyper-parameters tuned on a validation set of PH2800 + SD3200 (p. 30). Baseline RANS closure: **k-omega** throughout.
- **Cases / flows and Re** (Table 2, p. 31): **C1** -> CBFS13700, 17 features; **C2** -> BFS5100, 17 features; **C3** -> SD3500, **5 features (FS1 only)**; **C4** -> SD3500, 17 features.
- **Metric**: RMSE of `b_ij` (a-priori); **reattachment length** and skin friction (a-posteriori).

**Headline result with numbers**

1. **Table 3, arXiv preprint p. 37 — square duct `Re = 3500`, RMSE of `[b]_ij`:**

   | Feature set | TBRF | TBNN |
   |---|---|---|
   | C3: 5 features (FS1, `S` and `R` only) | 0.0995 | **0.0871** |
   | C4: 17 features (FS1+FS2+FS3) | **0.0521** | 0.0681 |

   Going from 5 to 17 features cuts TBRF's error by **47.6%** and TBNN's by **21.8%**. **With the full feature set TBRF beats TBNN; with only the strain/rotation invariants it loses.** The authors' own reading (p. 36): "**the introduction of extra features has significantly more effect than the choice of neural-networks versus random-forests**". They add (p. 37) that of the 5 FS1 features, "**3 are approximately scaled versions of the other 2 - effectively reducing the input space to two dimensions.**" *This is the single most important result in Category B for a lab deciding where to spend effort: features, not model class.*
2. **Table 4, arXiv preprint p. 41 — backward-facing step `Re = 5100`, reattachment point `x/h`:**

   | | `x_reattach [x/h]` |
   |---|---|
   | RANS (k-omega baseline) | 5.45 |
   | **RANS + `b_TBRF`** | **6.32** |
   | DNS (Le et al. 1997) | 6.28 |
   | Experiment (Jovic & Driver 1994) | 6.0 +/- 0.15 |

   The corrected solve lands **0.6% beyond DNS** and **5.3% beyond the experimental mean** (just outside the experimental band). The baseline is **13.2% short of DNS**. **This is one of only two a-posteriori numbers in the whole corpus where a learned closure is compared to DNS on an integral quantity.** Skin friction: "the majority of results fall within the error bounds given by the experiment (**+/- 0.0005 `c_f`**)" (p. 41).
3. **Hyper-parameters (exact, arXiv preprint p. 30)**: **100 tensor-basis decision trees**; **11 of the 17 features** sampled per split; leaf minimum **9 samples**; regularisation **`Gamma = 1e-12`**. For C3 the trees were fully grown (one sample per leaf) and all features used. Split-value search by **Brent 1-d optimisation**, switching to brute force below **150 samples** in a bin (pp. 19-20). Features with **variance < 1e-4** were discarded (p. 30). Training complexity **O(N log^2 N)** (p. 7).
4. **The three feature sets (Table 1, p. 25)**: **FS1** = 6 invariants of `S` and `R`; **FS2** = 10 further invariants involving the antisymmetric map of `grad k`; **FS3** = 9 physically interpretable scalars (Q-criterion ratio, turbulence intensity, wall-distance Reynolds number, streamline pressure gradient, turbulent time scale, pressure-gradient-to-convection ratio, TKE-convection-to-production ratio, stress ratio, and a streamline-acceleration marker). **Invariance is stated honestly and unusually precisely**: the *output* is Galilean invariant by the tensor basis, but Table 1 marks four of the nine FS3 features with a dagger and states "**Features marked with † are rotationally invariant but not Galilean invariant**" — they are `k`, `u_k dp/dx_k`, `u_i dk/dx_i`, and `u_i u_j du_i/dx_j`. **Reflectional invariance is not discussed.**
5. **`FLAG F19` — the three numerical devices, all quantified, all called ad hoc by the authors:**
   - **Blending ceiling.** `tau ~ tau^ML(gamma) := (2/3)kI + 2k[(1-gamma) b^B + gamma b^ML]` (Eq. 15, p. 24), ramped as `gamma_n = gamma_max min(1, n/n_max)`. "**`gamma_max` was incremented in steps of 0.1 until the solver became unstable, yielding a value of `gamma_max = 0.8`**" (p. 26), and "`gamma_max >= 0.8` is achieved in all test-cases presented here". Authors: "**As this choice is ad hoc, further work related to this topic is necessary.**" *The learned correction is never applied at more than 80% strength.*
   - **Gaussian smoothing, and why.** "**Since the random forest is a piecewise constant approximation of `b`, and derivatives of `b` are needed in the N-S equation**, the predictions from the TBRF are smoothed spatially with a Gaussian filter, before they are propagated through the solver" — standard deviation **3 cell lengths** (p. 21). "**This filter width is an ad hoc choice**, and can possibly be adjusted more specifically for numerical stability in future work by looking at e.g. required condition numbers for the solver (see e.g. Wu et al. (2019))." *A pointwise regressor with no spatial correlation produces a field whose divergence is meaningless; the fix is a filter, chosen by hand.*
   - **Median, not mean.** "the values for the final predictions **do not have to lie in-between the values of the points used for training** ... this manifested during testing as **highly irregular and inconsistent predictions in small regions of the spatial domain**. Both pruning and regularization were applied ... **While regularization fixed the problem to some extent, it worsened predictions in certain regions** ... Instead, it proved to be more successful to take the **median** of the trees" (p. 57).
6. **Realisability, measured (arXiv preprint §2.2, pp. 9-11, and p. 35)**: the conditions are derived in full (eigenvalues and diagonal `b` components in `[-1/3, 2/3]`, off-diagonals in `[-1/2, 1/2]`). **No realisability constraint is imposed on either model.** Result: "In all our studies, we have **never observed unrealizable predictions from TBRF, despite no explicit realizability constraint being imposed**", whereas TBNN "slightly outperforms, **at the cost of some unrealizable predictions closest to the wall**" at `x/h = 10, 15, 19` on the BFS. **A random forest cannot leave the convex hull of its training targets in the way a network can; that is the mechanism, and it is a structural argument for forests over networks near walls.**
7. **Ill-conditioning, acknowledged and worked around (arXiv preprint p. 24)**: "Simply setting the prediction of the anisotropy tensor `b_ML` in the momentum equation **adversely affects the numerical stability of the solver**. As already shown in Wu et al. (2019), **treating the Reynolds stress as an explicit source term in the RANS equations can lead to an ill-conditioned model.**" And the trade-off, stated plainly (p. 26): "A **lower value for `gamma` means that the linear eddy viscosity assumption becomes more dominant, resulting in a more stable solution, but impairing the accuracy of the solved mean velocity**."
8. **The propagation ceiling is reported (arXiv preprint pp. 39-40)**: propagating `b_ij,DNS` itself "broadly reproduce[s] the DNS mean velocity ... with the **best fit near the wall (`z = 1`), and the worst near the channel centerline (`z = 0`)**. Subsequently approximating `b_ij,DNS` by `b_ij,TBRF` causes additional errors, but **these errors are of similar magnitude to the errors already made in the propagation.**" *The ML error and the propagation error are the same size — halving the ML error would buy little.*

**Stated limitations (authors' own words, arXiv preprint)**

- p. 9: "the approach here is **only tested for steady RANS flow cases. It is untested for unsteady flows.**"
- p. 8: "this is a **corrective approach, with a single ML prediction providing an updated solution** ... it is **not a replacement for a 'standard' turbulence model** ... Such an iterative approach would in theory also be conceivable ... However such ambitious approaches are currently untested, **it is unclear under what conditions the coupled system will converge, and whether the converged solution will resemble ground-truth.**"
- p. 9: "**The errors in the ground truth are assumed to be small here** ... and therefore not taken into account."
- p. 35: "Moving away from the wall into the shear layer TBRF **erroneously heads too far back towards the two-component boundary** ... **The reason for this is unclear** ... **Diagnostic tools are needed.**"
- p. 44: "**Only a number of idealized canonical flow cases were considered here** ... it would be interesting to see ... **how well the algorithm is able to extrapolate to higher Reynolds numbers.**"
- p. 21 and p. 26: the two "ad hoc" admissions quoted in item 5.

**What it cannot see**

- **No propagated velocity error metric.** The a-posteriori evidence is one reattachment length, one `c_f` band, and profile plots. There is no `eps(U)/eps(U_0)` equivalent, so this paper cannot be compared numerically against Schmelzer 2020.
- **RMSE is reported for the square duct only** (Table 3). CBFS and BFS anisotropy comparisons are barycentric-map figures with no numbers.
- **No condition numbers are computed** — the reference to them is forward-looking (p. 21). The `gamma_max = 0.8` ceiling is an empirical stability limit, not a conditioning measurement.
- **No mesh sizes, no CPU/GPU/wall-clock cost.** Only "mesh independence studies were performed" (p. 28).
- **Every reported case trains on the same three flows.** There is no study of how the result moves with the training set, and no `Re` extrapolation test (the authors name this as future work).
- **`FLAG F17`**: this paper's description of Ling et al.'s TBNN (10 layers, lr 2.5e-5, Adam, batch 1000) **contradicts the Ling SAND preprint on this disk** (8 layers x 30 nodes, lr 2.5e-7, per-point SGD). The TBNN column of Table 3 is therefore produced by *a* TBNN, but not demonstrably by *the* TBNN of the SAND preprint. Record; do not resolve.

---

### Weatheritt & Sandberg 2016 — GEP algebraic stress `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: Weatheritt, J. & Sandberg, R.D. (2016), *A novel evolutionary algorithm applied to algebraic modifications of the RANS stress-strain relationship*, J. Comput. Phys. 325:22-37. The file bearing this name in `_WRONG_RETRIEVALS/` is arXiv:1611.08830, *On the Distinction of Functional and Quality Requirements in Practice* (software engineering). JCP is paywalled and no open-access version has been located. **No numeric claim is made here.** Gene-expression programming is the third member of the symbolic-regression family alongside SpaRTA (Schmelzer 2020, above) and sparse linear regression; the catalogue notes its absence because it is the natural population-based control against SpaRTA's deterministic elastic net. Compute estimate and verdict: `_common/FEASIBILITY.md` §1.1 (BLOCKED on the source, not on compute).

---

## Category C — Field inversion + machine learning (FIML)

**Corpus status for this category is poor and the catalogue says so up front.** Of the four intended
papers, **one is on disk** (Singh, Medida & Duraisamy 2017). The three that define the method —
Parish & Duraisamy 2016 (the paradigm paper), Singh & Duraisamy 2016 (field inversion for functional
errors), and Holland, Baeder & Duraisamy 2019 (FIML with embedded networks) — are all
`WRONG-QUARANTINED` in `MANIFEST.md`. **The category is therefore catalogued from its downstream
application, not from its foundation**, and every structural statement about FIML below that is not
quoted from Singh 2017 comes from the review papers in Category R, which are on disk.

---

### `Singh2017_ml_airfoils.pdf`

- **Category**: C (primary). Secondary: B — the trained object is a model augmentation queried inside the solver; D (tertiary — the paper's ensemble-over-training-sets is an informal UQ).
- **Version**: **arXiv preprint 1608.03990v3**, 32 pp. Journal: *AIAA J.* 55(7):2215-2227. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: **Two stages.** (1) A **discrete-adjoint inverse problem** infers a spatially varying multiplier `beta(x)` on the **production term** of the Spalart-Allmaras equation, `D nu_tilde/Dt = beta(x) P - D + T` (arXiv preprint Eq. 2, p. 7), by minimising the mismatch to an **experimentally measured lift coefficient**. (2) A feed-forward network regresses `beta` from local non-dimensional flow features, and — the point of the paper — **"the mapping `beta(eta)` built during the training process is queried for input features at every iteration of the flow solver ... This process is repeated until convergence"** (p. 14). **The learned augmentation is inside the solver iteration and the flow is re-converged; it is not a post-processing correction.**
- **Data used**: **experiment, not DNS.** NREL wind-turbine airfoil reports for **S805, S809, S814** (Somers, NREL/SR-440-6917/6918/6919). The inversion target is the measured `C_l`; pressure measurements are available at some test points. Reynolds numbers **1e6, 2e6, 3e6**; **`Re = 3e6` is never in any training set** (Table II note, p. 20).
- **Cases / flows and Re**: the main predictive model **P** is trained on **S814 at `Re = 1e6` and `2e6` only** — chosen "because adverse pressure gradients are the largest" (p. 14) — and then applied to S805, S809 and S814 across all three Reynolds numbers and a wide `alpha` range including post-stall. Table II (p. 20) defines **eight** models trained on different airfoil/`Re` combinations. Solver: **ADTURNS**, cell-centred finite volume, compressible RANS, structured C-grid 291 x 111, 3rd-order MUSCL + Roe, D-ADI implicit; farfield 35 chords; 200 points on the airfoil surface; freestream `nu_t/nu = 3` (pp. 6-7). **Portability test in AcuSolve**, an unstructured Galerkin-least-squares commercial finite-element code (pp. 20-21).
- **Metric**: `C_l(alpha)`, `C_d(C_l)`, surface `C_p`. **There is no results table in this paper.**

**Headline result with numbers**

1. **The two — and only two — quantitative performance numbers in the entire paper:**
   - **Compute overhead (p. 22, verbatim)**: "This was confirmed to add **< 10% of additional compute time** compared to the baseline calculation."
   - **NASA wall-mounted hump, Appendix B (p. 31, verbatim)**: "the predicted length of the separation bubble was found be **15% more accurate** compared to the baseline solution."
   Everything else — the `C_l(alpha)` stall improvements of Figs. 12-14, the `C_p` matches of Figs. 15-17, the eight-model ensemble spread of Fig. 18, the AcuSolve portability of Fig. 19 — is **graphical only, with no error metric attached.**
2. **The inverse problem, exactly (arXiv preprint Eqs. 3-5, pp. 8-9)**: `min_beta [ (C_l,exp - C_l(beta))^2 + lambda sum_n (beta(x_n) - 1)^2 ]`, with **Tikhonov weight `lambda = 4e-4`**, and "The optimal solution was indeed confirmed to be **insensitive to order of magnitude variations in `lambda`**" (p. 9). Optimiser: **L-BFGS** with a discrete adjoint whose partials come from **Tapenade** automatic differentiation; the adjoint system is solved by pseudo-time stepping (Appendix A, p. 30).
3. **Why `beta` is a multiplier and not an additive source — a conditioning argument (p. 7, verbatim)**: "It is equivalent to adding a source term `delta(x) = (beta(x) - 1) P(x)`. **Inferring `beta`, however, leads to a better conditioned inverse problem, as `beta` is non-dimensional and has a simple initial value of unity.**" *This is a design choice made for the conditioning of the inverse problem, and it is the cheapest transferable idea in the paper.*
4. **Features (p. 12, verbatim)**: the candidate set is `{Omega_bar, chi, S/Omega, tau/tau_wall, P/D}` where `Omega_bar = d^2 Omega/(nu_hat + nu)` (Eq. 6, p. 11) and `chi = nu_hat/nu`. **The subset actually used in the final network is never stated as an explicit list**; the summary (p. 22) says only "locally non-dimensional flow quantities such as the ratio of eddy to kinematic viscosity, vorticity to strain-rate magnitude". Normalisation is by the local scales `nu + nu_hat` and wall distance `d`, with the explicit rationale (pp. 11-12) that dimensional quantities "may have different numeric values even when two flows are dynamically similar."
5. **Local non-dimensionalisation is what makes the model portable (pp. 20-21)**: the same trained network was embedded in **AcuSolve**, a completely different (unstructured, finite-element, dimensional) solver, and reproduced the improvement. **This is the only cross-solver portability demonstration in the corpus** — and it stands in direct opposition to Lozano-Duran & Bae 2023's conclusion (Category F) that their wall model "must be re-trained to yield accurate predictions in different flow solvers". *The difference is what was learned: a non-dimensional multiplier on a physical production term ports; a wall-stress model trained on one solver's own WMLES fields does not.*
6. **Network (p. 13, verbatim)**: "Typically, **3 layers and about 100 nodes** were employed with a **sigmoid** activation function. The **Fast Artificial Neural Network Library (FANN)** is used for this work." Trained by error back-propagation. Feature selection scored by "**sum squared error (SSE) on the validation set**" (p. 12) — **no SSE value is ever reported.**
7. **Convergence (p. 22, Fig. 20)**: "The NN-augmented model displays **comparable convergence characteristics to the baseline model**"; residuals fall from `1e-4` to `1e-11` over roughly 1000 iterations from a uniform freestream initial condition. **No clipping, under-relaxation, blending or smoothing of `beta` is used anywhere in the paper, and no convergence failure is reported.** *This is the only in-the-loop learned closure in the corpus that needed no stabiliser — and the reason is structural: `beta` multiplies an existing, already-stable production term rather than adding an explicit stress source.*
8. **SA constants used (Appendix C, p. 32)**: `c_b1 = 0.1355`, `sigma = 2/3`, `c_b2 = 0.622`, `kappa = 0.41`, `c_w1 = c_b1/kappa^2 + (1+c_b2)/sigma`, `c_w2 = 0.622`, `c_w3 = 2.0`, `c_v1 = 7.1`.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 20, the most important one: "**Fig. 18 shows that the quality of the NN-augmented model is sensitive to the selection of the training-data. In this work, the best model 'P' is selected by exploring several combinations of the data-sets.** This observation is subjected to the uncertainty involved with the intermediate steps (feature selection, machine learning algorithm, etc.)"
- p. 19: "**While this ensemble approach does not qualify as a formal uncertainty quantification technique**, it is nevertheless a useful test to ascertain the sensitivity of the model output to the training set."
- p. 23: "a more formal uncertainty quantification approach that takes into account the uncertainty in the data, variability of the training process and confidence in the baseline model **may be desirable**."
- p. 24, the design checklist — worth carrying verbatim: model augmentations should "a) include available experimental data ... **b) do not influence regions of the flow that are adequately represented by the baseline model (near-wall region in thin boundary layers), and c) do not degrade the convergence properties of the solver.**"
- p. 24: "**respecting realizability limits and invariance properties will be necessary to constrain the model, especially when the model is operating in an extrapolatory mode.**"
- p. 21, a caveat on their own portability claim: "It should be noted that the AcuSolve uses a variation of the SA model which corrects for the rotation and the curvature effects. These corrections are not used in the ADTURNS code and therefore **the solutions from these two codes are not expected to be identical, even for the baseline model.**"

**What it cannot see**

- **No error metric of any kind is reported for lift, drag, pressure or velocity.** The two numbers in item 1 are the whole quantitative content. A downstream summary that attaches a percentage to a `C_l` or `C_p` claim from this paper would be fabricating it.
- **No invariance is claimed or enforced.** The authors list it as future work. The features are local and non-dimensional but not built from an integrity basis, and no Galilean or rotational argument is made.
- **The best model was chosen by looking at the answer.** Model "P" was selected "by exploring several combinations of the data-sets" (p. 20) — the eight-model ensemble of Fig. 18 shows the spread that this selection collapsed, and the spread is not quantified.
- **No failure case is reported.** The authors state repeatedly that low-`alpha` accuracy is not degraded ("none of the NN-augmented predictions diverge from the base SA model at `alpha = 0` deg", p. 19). The drag claim is explicitly weakened to a trend: "the drag rise is predicted to occur at lower angles of attack than in the baseline model, **a trend that is qualitatively correct**" (p. 16).
- **Number of inverse problems, angles of attack, and training points: not stated.** "Full-field inversion was performed for each airfoil at different combinations of angles of attack and Reynolds number" (p. 14) is the whole description. The grid is 291 x 111, so a point count is *inferable* — **do not quote an inferred number as the paper's.**
- **Internal inconsistency**: the body text (p. 7) says the C-grid is "291 points in the wraparound direction and **111** in the wall-normal direction"; Fig. 11's legend (p. 16) says **291 x 131**. Both are as printed. If reproducing, state which you used.
- **No airfoil case is on disk here.** `_common/FEASIBILITY.md` §1.2 marks this **BLOCKED on data, not on the paper**: reproducing it means building an airfoil case set with experimental `C_l` from scratch.

---

### Parish & Duraisamy 2016 — the FIML paradigm `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: Parish, E.J. & Duraisamy, K. (2016), *A paradigm for data-driven predictive modeling using field inversion and machine learning*, J. Comput. Phys. 305:758-774. **This one deserves a note because of how the failure happened**: the file was uploaded by hand, and its title page reads *"ALmost EXact boundary conditions for transient Schrodinger-Poisson system"*, Bian, Pang, Tang & Arnold, **J. Comput. Phys. 313 (2016) 233-246** — right journal, right year, adjacent volume, wrong article. **A journal-and-year sanity check passed on a wrong document.** See LESSONS L-144. **No numeric claim is made here.**

### Singh & Duraisamy 2016 — field inversion for functional errors `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: Singh, A.P. & Duraisamy, K. (2016), *Using field inversion to quantify functional errors in turbulence closures*, Phys. Fluids 28:045110. The quarantined file is arXiv:1606.00678, a formal-methods paper. **No numeric claim is made here.** `_common/FEASIBILITY.md` §1.2 notes that when it arrives it is FEASIBLE only as a 1-D or 2-D variant with a hand-written adjoint, since OpenFOAM's `adjointOptimisationFoam` is shape-optimisation-oriented.

### Holland, Baeder & Duraisamy 2019 — FIML with embedded neural networks `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: AIAA Aviation Forum 2019-3200. The quarantined file is arXiv:1907.10711, a drop-fragmentation paper. **No numeric claim is made here.** This is the paper that closes the loop between the two FIML stages (inversion and regression) into a single optimisation — the "tightly coupled" or "integrated" form that Duraisamy 2021 gives as Eq. 9 (Category R below) and calls the only formulation that "**ensures full consistency between the learning and prediction environments.**" Its absence is the largest single hole in the corpus for this lane.

---

## Category D — Model-form uncertainty quantification

**Corpus status**: two of the five intended papers are on disk. The **eigenspace-perturbation**
lineage (Emory 2013, Iaccarino 2017) — the cheapest and most directly usable UQ method for this
lab, needing **no training at all** — is entirely `WRONG-QUARANTINED`. That is the most consequential
retrieval gap in the corpus after Holland 2019, because `_common/FEASIBILITY.md` §1.2 rates the
frozen-field envelope check at **< 1 core-hour** and the full 41-case perturbed sweep at ~60.

---

### `Wu2018_rans_explicit_closure_ill_conditioned.pdf` — **NEW ON DISK, `FLAG F16` RESOLVED**

- **Category**: D (primary — it is a model-*form* diagnostic). Secondary: B — it is the paper every data-driven RANS closure in Category B cites for the ill-conditioning result, and the one that supplies the numbers Wu 2018 (Category B) only gestures at.
- **PROVENANCE NOTE**: `VERIFICATION_FLAGS.md` **F16** recorded this paper as *not in the corpus* and instructed that it be added to the shelf. **It has since been retrieved and is on disk.** Identity verified 2026-08-20 by extracting page 1: the printed title reads *"RANS Equations with Explicit Data-Driven Reynolds Stress Closure Can Be Ill-Conditioned"*, Jin-Long Wu, Heng Xiao, Rui Sun (Virginia Tech) and Qiqi Wang (MIT), with the arXiv margin stamp **arXiv:1803.05581v3 [physics.flu-dyn] 10 Mar 2019**, 33 pp, typeset in the JFM template. **It is not yet a row in `MANIFEST.md`** — see the report at the end of this document.
- **Version**: **arXiv preprint 1803.05581v3** (10 Mar 2019), 33 pp. **All locations below are arXiv preprint page/Table/Figure numbers.**
- **Method (one line)**: **No model is trained and no turbulence model is used** — "Throughout this study, no turbulence models are used" (arXiv preprint p. 5). Instead, **exact DNS Reynolds stresses** are substituted into the RANS momentum equations as the ideal-limit stand-in for any data-driven closure, the equations are solved in OpenFOAM, and the resulting error amplification is diagnosed with a newly derived **local condition number function** `K(x)` built from the Green's function of the linearised RANS operator.
- **Data used**: DNS only, as *input* — channel flow from Lee & Moser (2015) at `Re_tau = 180, 550, 1000, 2000, 5200`; square duct at `Re_b = 3500` from Pinelli et al. (2010); periodic hills at `Re_b = 5600` from Breuer et al. (2009) plus two Incompact3d datasets (Table 2, p. 22).
- **Cases / flows and Re**: as above. Solver: **OpenFOAM**, finite volume, 2nd-order central differences for all terms except convection which uses 2nd-order upwind "to avoid the possible numerical instability when using central difference scheme for the convection term" (pp. 12-13); **convergence criterion 1e-8 absolute** on the momentum equations (p. 13). Channel cell counts `N = 36, 110, 200, 400, 1040` for the five `Re_tau`, first cell centre `y+ < 1`.
- **Metric**: `delta U_rms / U_rms^DNS` (Eqs. 3.1-3.2, p. 13); the local condition number `K_j` and its volume average `K_x`.

**Headline result with numbers**

1. **Table 1, arXiv preprint p. 4 — the number the whole data-driven RANS field rests on.** DNS Reynolds stresses substituted into the RANS equations and propagated:

   | `Re_tau` | 180 | 550 | 1000 | 2000 | **5200** |
   |---|---|---|---|---|---|
   | Error in turbulent shear stress, volume-averaged | 0.17% | 0.21% | 0.03% | 0.15% | **0.31%** |
   | Error in turbulent shear stress, maximum | 0.43% | 0.38% | 0.07% | 0.23% | **0.41%** |
   | Error in mean velocity, volume-averaged | 0.25% | 1.61% | 0.17% | 2.85% | **21.6%** |
   | Error in mean velocity, maximum | 0.36% | 2.70% | 0.25% | 5.48% | **35.1%** |

   **A stress field wrong by 0.31% produces a velocity field wrong by 21.6% on average and 35.1% at worst.** These are the authors' **own reproduction** of Thompson et al. (2016), not a citation: "we reproduced the two studies of solving for mean velocities by using the DNS Reynolds stresses obtained from Lee & Moser (2015), and the results are summarized in Table 1" (p. 3). The authors caution that the *stress* errors vary non-monotonically with `Re` and "such a coincidental trend should not be overly or literally interpreted", but that the *velocity* errors "clearly **increase monotonically** with the Reynolds number" (p. 4). Third-party caveat quoted on p. 3: large propagated errors have been reported "at Reynolds number as low as `Re_tau = 395` depending on the DNS data used (Poroseva 2017)".
2. **Why the textbook condition number fails — a clean negative result (arXiv preprint p. 7-8)**. The matrix condition number `K_A = ||A|| ||A^-1||` (Eq. 2.8) and the stress-scaled version `K_tau = K_A ||div tau||/||b||` (Eqs. 2.9-2.11) are "**more or less the same across all Reynolds numbers from `Re_tau = 180` to 5200**". Two reasons, both stated: (i) for channel flow the operator `A` comes only from the diffusion term, so **`K_A` is analytically `4n^2/pi^2` — a function of the mesh count `n` alone, independent of `nu` and `Re`** (p. 8); (ii) `alpha = ||div tau||/||b||` is `O(1)` at both `Re_tau = 180` and 5200. **And `K_A`'s mesh-dependence is itself disqualifying**: "The mesh dependency is highly undesirable as the condition number is to measure the conditioning property of turbulence models **at the PDE level, not any particular numerical discretization thereof**" (p. 8).
3. **The proposed metric, exactly (arXiv preprint Eqs. 2.13-2.19, pp. 9-11)**:
   `|delta u(x)|/U_inf <= K(x) ||div delta tau||_Omega / ||div tau||_Omega` (Eq. 2.13), with
   **`K(x) = ||G(x, xi)||_Omega ||div tau||_Omega / U_inf`** (Eq. 2.14), where `G` is the Green's function of the linearised RANS operator `L(u) = u_0 . grad u - nu grad^2 u` (Eq. 2.6). Discretely, **`K_j = ||r_j||_n ||div tau||_n / U_inf`** (Eq. 2.18) with `r_j` the `j`-th **row of `A^-1`**, and the volume average `K_x = sum_j K_j dV_j / V` (Eq. 2.19).
   **Cost**: each `K_j` needs one row of `A^-1`, obtained by solving `A^T r_j = I_j` — **`O(n log n)` per row with multigrid, `O(n^2 log n)` for the whole field**, "much lower than the complexity of `O(n^3)` for typical algorithms of matrix inversions" (p. 10). **Mesh-independence is proved (Appendix B, Eqs. B1-B8, pp. 27-28) and verified numerically over `Ny = 208, 416, 624, 832, 1040`** (Fig. 17, p. 29).
4. **`FLAG F19` — the explicit-vs-implicit conditioning result, which is the transferable engineering fact.**
   - **Explicit treatment** (Algorithm 1, p. 14 — `tau = tau^DNS` held fixed): "the local condition number of the flow at `Re_tau = 180` is of the order **`O(1)`**, while the local condition number of the flow at `Re_tau = 5200` is of the order **`O(10^2)`**" (p. 14).
   - **Implicit treatment** (Algorithm 2, p. 15 — `tau = 2 nu_t^m S(u^(i)) + tau_perp^DNS`, with the **optimal eddy viscosity** `nu_t^m(x) = argmin_{nu_t} ||tau^DNS - 2 nu_t(x) S^DNS||`, Eq. 2.22, projected from the DNS field): "the local condition number `K_j` is **significantly reduced** ... Although the local condition number of high Reynolds number is still greater than the one of low Reynolds number, **they are at the same order of magnitude for different Reynolds numbers**" (p. 16), and "**the volume-averaged local condition number stays at `O(1)`**" (p. 16, Fig. 8b).
   **`O(10^2)` explicit versus `O(1)` implicit at `Re_tau = 5200` is the entire quantitative content of the conditioning claim, and it is stated only as orders of magnitude — Figs. 4, 6, 7, 8 carry no printed values.**
5. **The velocity consequence (arXiv preprint p. 17, Fig. 9)**: at `Re_tau = 180` both treatments agree with DNS; at `Re_tau = 5200` "the error in mean velocity by using explicit treatment of Reynolds stress is **orders of magnitude higher** than the error of using implicit treatment". *Fig. 9d's abscissa spans 0-40% and Fig. 9c's spans 0-0.3% — those are axis ranges, not measurements.*
6. **The paradox, resolved (Appendix D, p. 31)**: the implicit and explicit runs use **nearly the same stress field** — "the difference between `u^imp` and `u^DNS` is about **0.1%**, and the difference between `tau^imp` and `tau^exp` should be at the similar level" — yet produce drastically different velocities. That is exactly what a large condition number means, and it is the single hardest percentage the implicit branch yields.
7. **Complex flows.** Square duct `Re_b = 3500`: explicit shows large `U_z` errors "in the region of the vertical symmetry plane and around the diagonal within the cross plane"; implicit gives "noticeable reduction of errors" (p. 18, Figs. 12-13; colourbars 0-0.5 for normalised error and 0-20 for `K_j`). **Periodic hills `Re = 5600` (p. 20, Fig. 15a): "the local condition number by using fixed Reynolds stress is of the order `O(10^2)` in most areas, indicating that the RANS equations are ill-conditioned in these regions"**; implicit gives "much smaller" values (Fig. 15b, colourbar 0-200).
8. **The most striking demonstration is entirely qualitative and should be quoted as such (arXiv preprint p. 20, Fig. 14)**: three near-identical periodic-hill DNS/LES Reynolds-stress fields (Table 2: Breuer LES 281x234x200 2nd-order; two Incompact3d DNS at 512x257x128 and 768x385x128, pseudo-spectral 6th-order) produce **visibly different** mean velocities. Dataset 2 "show[s] noticeable differences across the whole domain"; datasets 1 and 3 "agree better with DNS ... **but they are still different from each other**". Explanation offered (p. 23): "the cyclic boundary conditions of the inlet and outlet introduce a **strong correlation among errors** in the upper channel region." **No error metric is attached to this figure.**
9. **`FLAG F19` — an outright divergence, documented (Appendix C, pp. 29-30).** Algorithm 3 is the classic segregated RSTM coupling: `tau^(i) = nu_t^m (grad u^(i-1) + grad u^(i-1)^T) + tau_perp^DNS`, i.e. the stress lags one iteration. **Initialised with the DNS mean velocity**, so the starting error is small — yet "the value of `delta U_rms/U_rms^DNS` **increases rapidly** during the first several iteration steps ... the volume-averaged local condition number is at `O(10^2)` within the first three iteration steps, explaining the rapid growth of error ... **The error of the solved mean velocity grows rapidly and eventually leads to divergence of the simulation. Therefore, the solved mean velocity is not presented in this work since a converged solution was not achieved.**" *A closure that is exactly right, started from the exact answer, diverges because of how it is coupled.*
10. **The blending-factor verdict, which supersedes the ad-hoc practice of Category B (arXiv preprint pp. 23-24)**: "the choice of the blending factor is **largely ad hoc due to the lack of a quantitative method to evaluate the model conditioning**. A large blending factor improves the conditioning and stabilizes the solution ..., but it **impairs the accuracy** of the solved mean velocity, since the linear eddy viscosity assumption would be increasingly dominant. **The metric proposed in this work can assess the model conditioning with any given blending factor, and thus it is possible to choose a minimum blending factor that maintains good conditioning.**" *Kaandorp's `gamma_max = 0.8`, found by incrementing until the solver broke, is precisely the quantity this metric is designed to replace.*
11. **Other stabilisers named**: the optimal eddy viscosity "is **capped to be positive** for numerical stability" (p. 12). A tunable over-implicitisation is offered — increase `nu_t^m` by `Delta nu_t` and subtract the same from the nonlinear part — with the warning that "such a **purely numerical enhancement may introduce excessive errors** to iterative solvers when the chosen `Delta nu_t` is too large" (p. 16). **No value of `Delta nu_t` is given and no sweep is performed.** Two recommended stabilisations for practice (pp. 23-24): initialise from an eddy-viscosity-model solution, and use partial implicit treatment.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 18: "the mean velocity error is determined by **both** the local condition number **and** the error in Reynolds stress. Therefore, the spatial pattern of mean velocity error in Fig. 12 **can not be solely explained by** the local condition number in Fig. 13."
- p. 14: "the local condition number `K_j` assesses the relative error of solved mean velocity at a given point **with respect to the error in the whole Reynolds stress field, and not with respect to the error of Reynolds stress at the same given point.**"
- p. 30: "**The decrease of the condition number ... does not guarantee the decrease of the error in the mean velocity** in such a scenario ... the small condition number needs to be interpreted with caution when the source term in RANS equations changes during the simulation."
- p. 23: "**monolithic coupling is by no means a panacea** that guarantees well-conditioning and stability. The conditioning and stability ultimately depend on the characteristics of the turbulence model itself."
- p. 24: "for **non-differentiable models**, e.g., those based on random forests or other tree-based models (e.g., Wang et al. 2017), **a monolithic coupling is not straightforwardly viable.**" *This is a direct constraint on the TBRF of Kaandorp 2020 and the random forests of Wang 2017 and Wu 2018.*
- p. 2: "these data-driven Reynolds stress models **do not have explicit expressions for the Reynolds stress**, which make it difficult to treat the Reynolds stresses implicitly in the RANS equations to improve model conditioning."
- p. 6, scope: "we focus on the conditioning of **linearized** RANS equations ... the conditioning metrics studied here are **valid within each iteration**, even though the flow of concern may deviate from the linearized RANS equations."
- p. 18: "In practical applications, **the error of Reynolds stress is usually unknown**, and cautions should be exercised when regions with large local condition number exist."

**What it cannot see**

- **Almost all the conditioning results are orders of magnitude against unlabelled figures.** `O(1)` vs `O(10^2)` is the whole quantitative statement; Figs. 1, 4-8, 13, 15, 18 print no values. Table 1 is the paper's only numeric table of results.
- **`nu_t^m` is projected from the DNS field, not from a model.** The implicit treatment as demonstrated here uses the *optimal* eddy viscosity computed from the truth. A real closure must supply `nu_t^m` from its own prediction, and nothing here measures how much of the conditioning gain survives that substitution.
- **No turbulence model is solved.** `k` and `omega` transport, wall functions, and their errors are outside the experiment by construction. The paper isolates the propagation problem and says nothing about the coupled model problem.
- **Three flows, all canonical, all incompressible, all statistically 2-D or with one homogeneous direction.** No airfoil, no 3-D separation, no compressibility.
- **The condition number is an upper bound, not a prediction.** The authors say so twice (items above). A large `K` flags risk; it does not forecast the error.
- **It does not tell you what to do about a non-differentiable model** beyond noting that monolithic coupling is unavailable — which is the situation of half of Category B.

---

### `Xiao2016_model_uncertainties.pdf`

- **Category**: D (primary). Secondary: G — it is an **iterative, in-the-loop, re-solving** data-assimilation scheme, structurally closer to Category G than to a post-hoc UQ envelope.
- **Version**: **arXiv preprint 1508.06315v3**, 54 pp. Journal: *J. Comput. Phys.* 324:115-136. **All locations below are arXiv preprint page/Table/Figure numbers.**
- **Method (one line)**: The baseline RANS Reynolds stress is eigen-decomposed into magnitude `k`, shape `(xi, eta)` in the Barycentric map, and orientation `(v1, v2, v3)`; **discrepancy random fields on `k`, `xi`, `eta` only** (log-additive for `k`, Eqs. 2a-2c, p. 9) are expanded on a **Karhunen-Loeve basis** of a non-stationary squared-exponential Gaussian process and truncated to `m` modes; the KL coefficient vector is then inferred by an **iterative ensemble Kalman method with state augmentation** `x = [u, omega]^T`, where every iteration reconstructs `tau`, **re-solves the RANS momentum equations with that `tau` prescribed** (a modified solver, `tauFoam`, with no turbulence model solved), and Kalman-updates against sparse velocity observations.
- **Data used**: DNS as truth plus **synthetic sparse observations**. Periodic hills — Breuer et al. (2009), `Re_b = 2800`; square duct — Huser & Biringen (1993), `Re_b = 10320`. **18 velocity observation points** (hills) and **25** (duct, of which "only 13 ... are supplied effectively due to the diagonal symmetry"), each corrupted with Gaussian noise of **`sigma_obs` = 10% of the true mean value**, redrawn each iteration (Table 1, p. 21).
- **Cases / flows and Re**: two cases only. Baseline solver **OpenFOAM `simpleFoam`**, SIMPLE, collocated grid with Rhie-Chow, 2nd-order schemes, **Launder-Sharma low-Re k-epsilon** with near-wall refinement chosen deliberately "to avoid the complexity of using wall-functions" (p. 17).
- **Metric**: posterior mean and **95% credible intervals** of velocity, wall shear stress, reattachment point, TKE, and the normal-stress imbalance `tau_yy - tau_zz`.

**Headline result with numbers**

1. **Table 1, arXiv preprint p. 21 — the only table in the paper**, and the complete numerical specification:

   | | periodic hill | square duct |
   |---|---|---|
   | mesh (`nx` x `ny`) | 50 x 30 | 30 x 30 |
   | domain (`Lx` x `Ly` x `Lz`) | 9H x 3.306H x 0.1H | 0.4D x 0.5D x 0.5D |
   | `dx` x `dy` x `dz` in `y+` | 35 x [2, 65] x 850 | 24 x [1.4, 30] x [1.4, 30] |
   | first grid point in `y+` | ~1 | 0.7 |
   | ensemble size `N` | **60** | **60** |
   | fields given uncertainty | `xi, eta, k` | `xi, eta` |
   | KL modes `m` per field | **16** | **8** |
   | length scale | `H` | `0.1D` |
   | observations | 18 | 25 (13 effective) |
   | `sigma_obs` | 10% of truth | 10% of truth |

   *Internal inconsistency: Table 1 gives `Ly = 3.306H`; the Fig. 1 caption (p. 8) gives `Ly/H = 3.036`. Both as printed.*
2. **The cost ledger, stated exactly (arXiv preprint §5.1, p. 40)**: "each uncertainty quantification case involves **600 evaluations** of the forward RANS model `tauFoam`"; "each forward RANS evaluation is only **10%** as expensive as a baseline RANS simulation" (because it is initialised from the converged baseline and solves no turbulence transport); "the total computational cost ... is **60 times** as that of the baseline simulation"; and run on 60 cores in parallel, "the wall time ... is approximately the same as that of the baseline simulation, assuming the latter is run on a single core." **60x the cost of one RANS solve, for one case, buys a posterior with credible intervals. That is the price of model-form UQ, measured.**
3. **Convergence and sizing (arXiv preprint pp. 14, 19-20)**: convergence "is achieved when the two-norm of the misfit between the predictions and the observations falls below the noise level of the observations" — reached in **~10 iterations**. Ensemble sensitivity: "it was found that the inferred velocities and QoIs **do not vary if more than 30 samples are used**" (so `N = 60` is 2x the needed size). Mode-count rule: `m` chosen "such that the reconstructed field has at least **80% of the total variance** ... A rule of thumb is that a coverage ratio of 80% is adequate." Noise floor: "As long as the chosen noise level `sigma_obs` is larger than a threshold (**1% of truth** in this work), the inferred posterior means are not sensitive to this parameter."
4. **Prior construction (arXiv preprint p. 20, p. 32)**: non-stationary GP kernel `K(x,x') = sigma(x) sigma(x') exp(-|x-x'|^2/l^2)` (Eq. 4, p. 12) with the variance field built as **`sigma_0 = 0.2` everywhere plus `sigma_local = 0.5`** at hand-picked low-confidence locations — for the hills: hill crest, centre of the recirculation region, windward side of the hill, and the free shear layer downstream of the crest; for the duct: the lower-left corner, with RBF length scale `0.1D`. *The prior encodes where the modeller already believes the model is wrong; the method's performance is therefore not separable from that judgement.*
5. **Realisability by clipping, and its stated cost (arXiv preprint pp. 9-10)**: perturbed `(xi, eta)` are bounded to the square `[-1,1] x [-1,1]` (the Barycentric triangle mapped by bilinear shape functions, Appendix A, pp. 52-53). Authors: "Any perturbed state outside this range will be bounded to the edge of the square, which is **admittedly an ad hoc modeling choice**. As a result, **the prior may become non-Gaussian and the perturbation sample may deviate from zero-mean** if a large number of perturbations are bounded."
6. **Orientation is deliberately not perturbed, for stability — and the authors state the price (arXiv preprint p. 10)**: "**Perturbing the orientations of the modeled Reynolds stress tensor can potentially cause instability in the RANS momentum equation.** ... Consequently, **the assumed uncertainty space of Reynolds stresses may not contain the truth** because the true Reynolds stresses are likely to have different orientations from those of the RANS predictions." *A stability constraint that provably excludes the answer from the search space — the cleanest example in the corpus of numerics dictating epistemics.*
7. **Symmetry must be enforced by hand (arXiv preprint pp. 31-33)**: for the duct, "caution must be exercised to ensure that the perturbations ... have diagonal symmetry ... Otherwise, the posterior velocities may be asymmetric with respect to the diagonal." Implemented by retaining **only diagonally symmetric KL modes**.
8. **KL truncation is the smoothing mechanism (arXiv preprint p. 24)**: "a limited number of modes are retained in the KL expansion, which correspond to **very smooth fields** of Reynolds stress discrepancies." *Compare Kaandorp's Gaussian filter and Beck's eddy-viscosity projection — three different fields, three different papers, the same requirement that the correction be smooth enough to differentiate.*

**Stated limitations (authors' own words, arXiv preprint)**

- p. 45, the headline concession: "**A notable limitation is that the full Reynolds stress field inferred from this method is not accurate.** This is attributed to the high dimension of the Reynolds stress uncertainty space, the sparseness of the velocity observation data, and the **nonlinear, possibly even non-unique, mapping** between the Reynolds stresses and velocities as described by the RANS equations."
- p. 42: "our experience suggests that **the posterior mean of an arbitrarily chosen component or projection of the Reynolds stresses is not significantly more accurate than those of the baseline prediction.**" The mechanism is stated: only `div tau` enters the momentum equation, and extracting `tau_yy - tau_zz` is "a linear mapping described by a **rank deficient matrix**".
- p. 28: "in some regions the **95% credible intervals ... failed to cover the truth**, which indicates that the current method should still be used with caution when making high-consequence decisions. **The iterative ensemble Kalman method tends to underestimate uncertainties in the posterior distributions**, a difficulty shared by many other maximum likelihood estimators as well."
- p. 15: "As with many inverse problems, this problem is **intrinsically ill-posed** ... the amount of data is usually not sufficient to constrain the uncertainties ... **The forward model essentially provides the regularization of the ill-posedness.**"
- p. 15: "The ensemble Kalman-based uncertainty quantification scheme used here is **an approximate Bayesian method** ... It is **not expected to give posterior distributions with comparable accuracy** to those obtained from exact Bayesian schemes."
- p. 20: "**Increasing the number of modes increases the difficulty of the inference and may lead to deteriorated results** for a given amount of observation data." And p. 40: "While an overly small length scale would fail to make corrections to the regions without observation, **an overly large length scale would lead to spurious corrections.**"
- p. 44, on extrapolation: "**extreme caution must be exercised** and expert opinions must be consulted when using such an extrapolation method ..., since even a slight change of Reynolds number can lead to significant changes of flow characteristics. **Ultimately, the use of this assumption has to be the judgment of the user, which is clearly undesirable.**" And: "**Prediction of flows in a different geometry ... has achieved less successes.**"

**Failure cases, in the authors' own words**

- **Hill crest (arXiv preprint p. 27)**: "in the immediate vicinity of the hill crest, i.e., near `x/H = 0.5` and `x/H = 8.5`, the posterior ensemble is **similar to or even slightly deteriorated compared to the baseline** in terms of agreement with DNS data." Attributed to rapid spatial variation, small coherent-structure length scales, and no observations there.
- **Credible intervals (p. 28)**: "in some regions, e.g., between `0 < x/H < 1` and `8 < x/H < 9`, **the posterior credible interval does not improve or even deteriorate compared to the prior.**"
- **TKE (pp. 28-30)**: "the posterior mean of TKE is **not necessarily better than the baseline results at all locations**."
- **Duct, far from observations (p. 37)**: differences persist "especially in the regions far away from the observations (e.g., at `y/h = 1`)", and the inferred normal-stress imbalance is better at `y/h = 0.75` than at `y/h = 0.25` despite equal distance from the observation line — explained by the shorter flow length scale near the corner.

**What it cannot see**

- **There is no error table and no error metric anywhere for any flow field.** No RMSE, no L2 norm, no percentage improvement. **The only quantitative performance numbers in the paper are the computational-cost ratios of item 2.** Every accuracy claim — "significantly improved" velocities, the reattachment-point scatter of Fig. 7, the secondary-flow vectors of Fig. 14 — is graphical. **No reattachment length is printed for DNS, baseline, or posterior.**
- **This is calibration on the same case, not prediction.** Every ensemble member is re-solved, but there is **no held-out predictive test in this paper**; generalisation to a different `Re` or geometry is explicitly deferred to a companion paper (p. 44).
- **The truth is excluded from the search space by construction** (item 6) and the intervals are known to be too narrow (the ensemble Kalman under-dispersion admission). Both defects push in the same direction: **overconfidence**.
- **The prior is hand-designed** — four hand-picked high-variance locations on the hills, one on the duct. Nothing tests sensitivity of the posterior to that placement, and "no attempt was made to use optimal sensor placement" is stated in the sibling paper (de Zordo-Banliat 2023) as an open problem in the same lineage.
- **Two flows, both canonical, both low `Re`.** `Re_b = 2800` for the hills is below the 5600/10595 the rest of the corpus uses.
- **No ML in it.** Filed here because the lab's charter lists it under UQ; but its structure — re-solve, update, repeat — belongs with Category G.

---

### Emory, Larsson & Iaccarino 2013 — structural uncertainty by eigenvalue perturbation `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: *Modeling of structural uncertainties in Reynolds-averaged Navier-Stokes closures*, Phys. Fluids 25:110822. The quarantined file is arXiv:1303.1564, *The HAWC observatory as a GRB detector* (astro-ph). **No numeric claim is made here.** **This is the cheapest high-value missing item in the corpus**: `_common/FEASIBILITY.md` §1.2 rates the falsifiable a-priori question — *does the LES truth lie inside the 1c/2c/3c perturbation envelope?* — at **< 1 core-hour on frozen fields with no solve at all**, and a 3-case perturbed-solve demonstrator at ~5 core-hours. It needs **no training data and no ML**.

### Iaccarino, Mishra & Ghili 2017 — eigenspace perturbations `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: *Eigenspace perturbations for uncertainty estimation of single-point turbulence closures*, Phys. Rev. Fluids 2:024605. The quarantined file is arXiv:1705.09996, a dispersive-shock-wave paper. **No numeric claim is made here.** It extends Emory 2013 from eigenvalue to **eigenvector** perturbation — which is precisely the axis Xiao et al. 2016 (above, p. 10) declined to perturb on stability grounds, and precisely the axis they identify as the reason their posterior may not contain the truth. **The two papers together would close that loop and neither half of it is readable here.**

---

## Category E — LES subgrid-scale closures

`Smagorinsky1963_general_circulation.pdf` and `Nicoud1999_WALE_sgs.pdf` are the two analytical
members of this category and are catalogued **above under Category A**, where they sit alongside the
RANS foundations; their category codes there are E (primary) / A (secondary). This section covers
the four learned SGS closures on disk and records the analytical models that are missing.

---

### `Maulik_San2017_neural_deconvolution.pdf`

- **Category**: E (primary). Secondary: X — its cross-validation design (train on one perturbation level, test on three) is a transferable protocol.
- **Version**: **arXiv preprint 1706.00912v2**, 31 pp. Journal: *J. Fluid Mech.* 831:151-181. **All locations below are arXiv preprint page/Table numbers.**
- **Method (one line)**: A single-hidden-layer feed-forward network trained by **Extreme Learning Machine** (hidden weights fixed at small random values, output weights solved in closed form by a Moore-Penrose pseudo-inverse, Eq. 2.12, p. 4) maps a **local stencil of a perturbed coarse field** to the *true* coarse field at the stencil centre — "blind" deconvolution in the sense that **no filter kernel is assumed** — after which the subfilter stress is formed as `tau_ij = u_i_bar u_j_bar - u_i* u_j*` (Eq. 3.2, p. 5).
- **Data used**: three DNS/ILES datasets. **Kraichnan 2-D turbulence** `Re = 32,000`, DNS `2048^2` coarse-grained to `256^2` by taking every 8th point. **Taylor-Green / Kolmogorov 3-D** `Re = 1600`, DNS `512^3 -> 64^3`. **Stratified compressible turbulence** `512^3`, implicit LES of the inviscid Euler equations (infinite-`Re` limit), initial aggregate Mach **0.54** and **0.75**. Truth = the true coarse-grained field. Sample counts: **~65,000** (Kraichnan, p. 9); **~260,000 per network** (Kolmogorov, p. 10; three networks, one per velocity component). Spatial shifting could generate "up to 63 and 511 completely different data sets in two and three dimensions"; **four** are used — 1 training, 3 testing (p. 7).
- **Cases / flows and Re**: as above. Cross-validation grid (Table 1, p. 8): Gaussian filter radius `sigma = 1.0` for training, `1.0 / 1.1 / 0.9` for tests 1/2/3; noise amplitude `mu = 0.2` for training, `0.2 / 0.22 / 0.18` for tests.
- **Metric**: MSE of the recovered field; MSE of the six deviatoric subfilter-stress components.

**Headline result with numbers**

1. **Table 2, arXiv preprint p. 10 — Kraichnan 2-D, MSE of vorticity magnitude**: filtered `1.02e-2 / 1.14e-2 / 9.11e-3` -> deconvolved **`4.38e-3 / 5.73e-3 / 3.71e-3`** across the three test sets (a factor of ~2.3-2.5 reduction); noised `4.03e-2 / 4.88e-2 / 3.25e-2` -> regularised **`1.26e-2 / 1.38e-2 / 1.14e-2`** (a factor of ~3).
2. **Table 3, arXiv preprint p. 14 — Kolmogorov 3-D, MSE of the `z` velocity component**: filtered `9.56e-3 / 1.16e-2 / 8.10e-3` -> deconvolved **`3.57e-3 / 4.64e-3 / 3.04e-3`**.
3. **`FLAG` — Table 4, arXiv preprint p. 17 is where the paper's own baseline beats it.** Deviatoric subfilter-stress MSE (all `x 1e-5`) on the Kolmogorov case:

   | Model | `tau_11` | `tau_12` | `tau_13` | `tau_22` | `tau_32` | `tau_33` |
   |---|---|---|---|---|---|---|
   | **ANN** | 8.00 | 3.60 | 3.51 | 7.77 | 3.64 | 6.82 |
   | SS (scale similarity) | 6.76 | 5.62 | 5.91 | 6.76 | 5.91 | 7.95 |
   | AD1 (1 iteration) | 31.34 | 35.82 | 21.13 | 31.33 | 21.12 | 36.82 |
   | **AD3 (3 iterations)** | **2.46** | **1.69** | **1.82** | **2.46** | **1.83** | **2.91** |

   **Classical three-step approximate deconvolution beats the network on every single component, by a factor of about 3.** The authors concede it: "The AD3 approach can be seen to perform better (on average) than our proposed framework" (p. 16), noting AD3 is advantaged because "the specified filter utilized for the iterative deconvolution is the same as the one used for convolving the field" — i.e. AD3 knows the filter and the ANN does not, which is the whole premise.
4. **Table 6, arXiv preprint p. 25 — stratified turbulence, same metric, and here plain scale similarity beats the ANN on five of six components** (`x 1e-5`): ANN `6.02 / 2.60 / 3.12 / 3.82 / 1.82 / 5.15` vs SS `3.15 / 2.04 / 2.27 / 2.76 / 2.02 / 3.62`; AD3 wins everything at `2.01 / 1.18 / 1.29 / 1.60 / 1.12 / 2.05`. *The ANN wins only `tau_32`.*
5. **Filter extrapolation degrades measurably (arXiv preprint p. 13)**: test set 2 (`sigma = 1.1`, a **10% larger filter radius**) is worst everywhere — Kraichnan deconvolved `5.73e-3` vs `3.71e-3` for test 3; Kolmogorov `4.64e-3` vs `3.04e-3`. Author explanation: "**increasing the filter radius by 10% leads to some physical behavior that the framework has not fully been exposed to in training.**"
6. **Training cost is the paper's practical selling point**: **"of the order of 0.01 seconds"** for ~65,000 2-D samples (p. 9) and **"under 10 seconds"** for the three 3-D networks (p. 10) — because the ELM has no iterative optimiser at all. **Hardware is not stated.** Architecture: **100 neurons**, one hidden layer, Tan-Sigmoid, linear output with no output bias; inputs normalised to `[-1, 1]` "due to the fact that the Tan-Sigmoid activation function provides outputs between these limits" (p. 6).
7. **Inputs**: **9-point vorticity stencil** (2-D) or **27-point stencil** (3-D), centre plus immediate neighbours. **No invariance of any kind is claimed** — Galilean, rotational or reflectional. A full-text search finds "invariance" only in the titles of cited references.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 26: "**A natural follow-up to this investigation is to test our proposed approach in a fully a-posteriori analysis.** One of our primary goals in subsequent investigations is also to address the issue of sampling for training data."
- p. 27: "**a data-driven model is only as good as the data it has been trained on and can only reproduce physical behaviors similar to those it has seen in training.**"
- pp. 13-14: "**an accurate capture of the tails of the PDF of the true field remains elusive for this particular architecture.**"
- p. 28: "apart from its training data, **an ANN's performance is heavily dependent on its architecture**" — and no architecture sweep was performed.
- p. 27: "it is also important to develop **outlier identification systems for noisy data**."

**What it cannot see**

- **This is an a-priori study end to end, and the authors label every figure "A-priori results".** "these data sets are all generated from the same high fidelity solution field and correspond to a **perfectly a-priori analysis**" (p. 8). **The deconvolved field is never fed back into a solver and nothing is re-converged. There is no a-posteriori stability information in this paper at all.** Given Duraisamy 2021's finding that a-priori success is "neither a necessary nor a sufficient condition" (Category R), the MSE tables above bound nothing about deployment.
- **The transfer experiments carry no numbers.** `Re = 1600 -> Re = 5000` (Fig. 19, p. 26), `t = 15 -> t = 20` (Fig. 20), TGV -> stratified (Fig. 21) and stratified -> TGV (Fig. 22) are **all graphical**, as are every energy spectrum, PDF and inertial-range claim (`k^-3`, `k^-5/3`). The stated "aliasing error is successfully stabilized" (p. 10) has no metric.
- **The method loses to both of its classical baselines on the quantity that matters.** On subfilter stress, AD3 wins everywhere and scale similarity wins mostly (items 3-4). The paper's positive results are on *field recovery*, not on *stress*.
- **No condition number, rank, or regularisation parameter is reported for the Moore-Penrose pseudo-inverse** that constitutes the entire training procedure.
- **Two apparent typographical faults, reported as printed and not corrected**: (i) Table 3's regularisation entry for test set 3 reads `3.39e-2` noised -> **`7.58e-2`** regularised, i.e. the "regularised" error is *larger* than the input, contradicting the text on p. 14; `7.58e-3` is the obvious intent. (ii) The deconvolution half of **Table 5 (p. 23, stratified turbulence) is byte-identical to the regularisation half of Table 2 (p. 10, Kraichnan)** and carries the wrong column headers. **Anyone quoting Table 5 must check the PDF.**
- **Stratified-case sample count is not stated.**

---

### `Maulik2019_subgrid_2d_nn.pdf`

- **Category**: E (primary). Secondary: G — the network is evaluated inside the time-marching solver at every step, which is in-the-loop *deployment* (though the training is offline and a-priori).
- **Version**: **arXiv preprint 1808.02983v1**, 22 pp. Journal: *J. Fluid Mech.* 858:122-144. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: A fully connected network maps a **20-dimensional local input vector** to the scalar sub-grid vorticity source at that cell, and is deployed **pointwise at every explicit time step** of a `256^2` vorticity-streamfunction LES — with a **hardwired sign-based truncation applied before injection**: `Pi = Pi_tilde` if `(grad^2 omega_bar)(Pi_tilde) > 0`, **else `Pi = 0`** (arXiv preprint Eq. 2.4, p. 5).
- **Data used**: DNS of decaying 2-D Kraichnan turbulence at `2048^2`, Fourier cut-off filtered to `256^2`; truth is the exact filtered-DNS source `Pi = J(omega_bar, psi_bar) - J(omega, psi)_bar` (Eq. 1.5, p. 4). **`Re = 32,000` only** for training. **Five snapshots, `t = 0, 1, 2, 3, 4`**, described by the authors as "40000 space-time snapshots of DNS data ... (**0.0125% of total data**)" (p. 8). Split: **two-thirds training, one-third validation**. **The absolute number of training samples is not stated.**
- **Cases / flows and Re**: training and deployment at `Re = 32,000`; **deployment also at `Re = 64,000`, never trained on**; **24 ensemble-averaged simulations** with different random initial vorticity fields sharing one initial energy spectrum (Fig. 10, p. 14). Numerics: 2nd-order spatial discretisation, **Arakawa** kinetic-energy-conserving Jacobian, **3rd-order TVD Runge-Kutta**, spectrally accurate Poisson solver (p. 12); deployment to `t = 4`, extended to `t = 6` (Fig. 11).
- **Metric**: energy spectra, PDFs of `Pi`, vorticity fields. **There is no error metric in this paper.**

**Headline result with numbers**

1. **The input vector, exactly (arXiv preprint Eq. 2.2, p. 5)** — `R^20 -> R^1`: the **9-point stencil of vorticity** `omega_bar`, the **9-point stencil of streamfunction** `psi_bar`, **plus two eddy-viscosity kernels**, the Smagorinsky `|S_bar|` and the Leith `|grad omega_bar|` (Eq. 2.3, p. 5). *The two kernels are 2 of 20 inputs and they turn out to carry the model — see item 4.*
2. **Architecture search, and the trap it set (arXiv preprint pp. 7-8, Fig. 2)**: grid search plus 3-fold cross-validation in scikit-learn; depth swept **1 to 8 layers** at 50 neurons for 1000 epochs, then width swept **10 to 150** neurons at 2 layers. **Selected optimum: 2 hidden layers x 50 neurons**, trained for **5000 epochs** with **Adam** in TensorFlow, ReLU activations, MSE loss. Batch size, learning rate and weight initialisation are not stated.
3. **`FLAG F19` — the truncation, its justification, and its size.** Eq. 2.4 zeroes the predicted source wherever it would act as a negative eddy viscosity. Justification, verbatim (p. 5): "This ensures **numerical stability due to potentially negative eddy-viscosities** embedded in the source term prediction and may be considered to be an implicit assumption of Boussinesq hypothesis for functional sub-grid modelling." **Size of the intervention (p. 11): "roughly half of the predicted sub-grid terms are truncated"** — consistent with Piomelli et al. (1991) finding forward- and back-scatter "present in approximately equal amounts". Consequence, stated by the authors (p. 11): "Equation 2.4 **precludes the presence of a backscatter of enstrophy** for strict adherence to viscous stability requirements on the coarse-grained mesh." The alternative they considered and rejected: "one may also resort to some form of spatial averaging in an identifiable homogeneous direction as utilized by Germano et al. (1991). However, **the former was chosen to remove any dependency on model-forms or coefficient calculations**" (p. 5). *Half the learned model is discarded at run time to keep the solver stable — and the paper says so plainly.*
4. **`FLAG F19` / `F10`-class — the a-priori/a-posteriori dichotomy, which is this paper's real contribution (§5, arXiv preprint pp. 16-19).** Three controlled ablations, each showing a-priori loss is uninformative about deployment:
   - **Removing the two eddy-viscosity kernels (18-input map, Eq. 5.1, p. 16)**: a-priori training loss is essentially unchanged, but a-posteriori the model **fails** — "our a-posteriori deployment of this model ... displayed an **unconstrained behavior at the larger scales with the formation of non-physical large scale structures**" (pp. 16-17, Fig. 13). The authors conclude the kernels act as "an **implicit regularization** of our model" (p. 17).
   - **The grid-search "optimal" 2-layer network is beaten a-posteriori by a 5-layer network the grid search had rejected**: "the utilization of a deeper network actually leads to more accurate predictions of the Kraichnan turbulence spectrum ... **This despite the fact that the deeper network displays a great[er] mean-squared-error during the training phase (which was the root-cause of it being deemed ineligible in the hyper-parameter tuning)**" (p. 17, Fig. 15).
   - **A reduced 5-point stencil (12 inputs, Eq. 5.2, p. 18)**: "**While training errors are more or less similar, the reduced stencil fails** to capture the nonlinear relationship between the resolved and cut-off scales with consequent results on the statistical fidelity of the lower wavenumbers" (p. 18, Fig. 16) — though with 5 layers it recovers (Fig. 17).
   **In all three ablations the a-priori loss is flat and the a-posteriori behaviour changes qualitatively. A hyper-parameter search scored on training MSE selected the wrong architecture.**
5. **Baseline behaviour (arXiv preprint p. 12)**: static Smagorinsky and Leith with `C_s = C_l = 1.0` are "**over-dissipative** ... particularly at the lower (integral) wavenumbers"; the coefficient choice "is critical in the capture of the lower wavenumber fidelity". Coefficients swept: `C_s = 0.1, 0.3, 0.5, 0.8, 1.0` and `C_l = 0.2, 0.4, 0.6, 0.8, 1.0` (Fig. 4, p. 10). The no-model run shows "an expected accumulation of noise at grid cut-off wavenumbers".
6. **Deployment is stable** to `t = 4` and `t = 6` with the truncation in place; Fig. 12 (p. 15) shows "a significant reduction in noise can be visually ascertained" relative to the no-model run. **No divergence, no blow-up, no blending factor and no condition number is reported.**

**Stated limitations (authors' own words, arXiv preprint)**

- p. 19: "**The effect of realizability constraints and numerical errors often leads to unexpected a-posteriori performance and some form of lightweight deployment must be utilized for confirming model feasibility.**"
- p. 19: "**Again, the a-priori mean-squared-error is not indicative of the quality of a-posteriori prediction.**"
- p. 16: "This a-priori hyper-parameter selection is primarily devised on mean-squared-error minimization and is **susceptible to providing model architectures which are less resistant to over-fitting and more prone to extrapolation**."
- p. 11: "Studies are underway to extend some form of **dynamic localization of backscatter** to the current formulation along the lines of Ghosal et al. (1995)."
- p. 20: "**network-embedded symmetry-considerations are also being explored as a future enhancement for this research**" — i.e. no invariance is claimed.
- p. 20: "**Dataset pre-processing for outlier identification, not utilized in this study**, is also a potential avenue for improved a-posteriori performance." The work is framed as "the successful application of a **proof-of-concept**".

**What it cannot see**

- **This paper contains zero tables and zero tabulated error metrics.** The string "Table" does not appear in it. **Every result, including both headline failure modes, is a figure.** There is no spectral error, no L2 error, no MSE value for any deployment. **Do not attribute any error number to this paper.** (Training-loss values readable off the axes of Figs. 2, 13, 14, 17 are unlabelled-unit optimisation traces, not results.)
- **No normalisation and no invariance.** "all our variables in this study are non-dimensionalized at the stage of problem definition and **no further pre-processing is utilized**" (p. 5). Symmetry is future work.
- **Two-dimensional turbulence only.** 2-D turbulence has an inverse energy cascade and an enstrophy cascade; the sign-based truncation that stabilises it here is defined against `grad^2 omega_bar` and has no direct 3-D analogue.
- **One Reynolds number in training, one held-out.** `Re = 32,000 -> 64,000` is a factor of 2.
- **The truncation removes exactly the physics the model was built to capture.** Backscatter is the reason a learned closure could beat an eddy viscosity; zeroing half the predictions on a sign test converts the model into a positive-definite eddy viscosity with a learned magnitude. The authors are explicit that this is a stability compromise, not a modelling choice.

---

### `Beck2019_deep_neural_les.pdf`

- **Category**: E (primary). Secondary: G — the a-posteriori section is the corpus's cleanest statement of why a directly learned closure cannot be run.
- **Version**: **arXiv preprint 1806.04482v3**, 27 pp, typeset in the JFM template. Journal: *J. Comput. Phys.* 398:108910, under the **different title** "Deep neural networks for data-driven LES closure models". **All locations below are arXiv preprint page/Table numbers and will not match JCP.**
- **Method (one line)**: Learn the **exact discrete** LES closure — including the coarse-grid discretisation operator — by supervised residual-CNN regression from DNS of decaying homogeneous isotropic turbulence, then, because that closure cannot be run, **convert it into a pointwise eddy viscosity by a least-squares projection** and run *that*.
- **Data used**: **20 distinct DNS runs** of decaying homogeneous isotropic turbulence with randomised initial realisations and a fixed initial spectrum (Chasnov, Eq. 2.9, `s = 4`, `u_0^2 = 5`, `k_p = 4`), split **18 train / 1 validation / 1 hidden test**. **`Re_lambda ~ 180`**, `Ma = 0.1`, domain `[0, 2pi]^3`. DNS grid **64^3 elements at polynomial degree `N = 7` = `512^3` DOF**; LES grid coarsened **8x per direction to `8^3` elements at `N = 5`**. **Filter: L2-projection onto the polynomial space `P5` in each LES element** — an explicit, exactly defined DNS-to-LES operator. Sampling every `0.1 T*` over `T = 1.0` to `2.0 T*` (the self-similar decay window, fitted as `t^-2.2` versus Batchelor & Townsend's `5/2`). Training-set size stated only as factors: `n_runs = 18`, `n_samples = 11`, `n_elems = 8^3 = 512`, **augmented x3 by cyclic index shifting**. **The paper never multiplies these out.**
- **Cases / flows and Re**: one flow class, one `Re_lambda`.
- **Metric**: **cross-correlation** `CC(a,b) = cov(a,b)/sqrt(var a . var b)` (Eq. 2.12, p. 10) between predicted and true closure terms.

**Headline result with numbers**

1. **Table 1, arXiv preprint p. 11 — the baseline correlations, before any network.** Raw velocity to closure term: `CC = -0.0120, -0.0127, -0.0126` for the three components. Coarse-grid operator to closure term: `CC = 0.1894, 0.1793, 0.1787`. *The most informative single input feature carries under 19% correlation with the target.*
2. **Table 3, arXiv preprint p. 18 — network test-set cross-correlations `CC / CC_inner / CC_surf`** (inner = the `[1:p-2]^3` sub-block, surf = its complement):

   | Net | `CC_1` | `CC_inner,1` | `CC_surf,1` |
   |---|---|---|---|
   | RNN0 | 0.3477 | 0.7122 | 0.1491 |
   | RNN1 | 0.4148 | 0.7447 | 0.1642 |
   | RNN2 | 0.4433 | 0.7564 | 0.2059 |
   | RNN4 | 0.4706 | 0.7667 | 0.2539 |
   | **RNN8** | **0.4772** | 0.7637 | 0.2905 |
   | **MLP100** (Gamahara & Hattori reproduction) | **0.2543** | 0.6578 | 0.1174 |

   Abstract and conclusion state it as "**up to 47% and even 73% for the inner elements**". **The MLP baseline achieves "less than half" the residual network's correlation (p. 15).** The gain saturates for depth `d > 4` "due to overfitting and the limited amount of training data" (p. 19); overfitting for RNN8 begins after **~40,000 iterations**.
3. **Table 5, arXiv preprint p. 21 — feature ablation on RNN4** (`CC_1/CC_2/CC_3`): baseline `{u_i, R_tilde(F(U_i))}` **0.4706/0.4505/0.4499**; velocity only 0.3665/0.3825/0.3840; coarse operator only 0.3358/0.3066/0.3031; adding `rho, p, e` gives **0.4764/0.4609/0.4580** (a 1.2% relative gain for three extra fields); u-momentum alone 0.3913. *Neither input alone reaches the pair; the extra thermodynamic fields buy almost nothing.*
4. **`FLAG F10` — the direct closure is unstable, and the CFL number does not save it (arXiv preprint §4.3, pp. 22-24).** First, an energy check (Eq. 4.1, p. 22): the relative energy-contribution error `d_e` is **positive and of order `O(1e-1)` for all networks**, i.e. the predicted closures are net dissipative. **And they are still unusable**: Fig. 10 (left) shows RNN0/RNN2/RNN4 "are initially dissipative, [but] they **lack long-term stability as high frequency errors accumulate**"; Fig. 10 (right) sweeps **CFL = 0.5, 0.05, 0.005** and finds smaller time steps improve short-term agreement but "later on **stability issues ensued even for very small timesteps**". The stated root cause is structural: in the perfect-LES formulation the coarse-grid inviscid operator **cancels exactly**, so an *approximate* learned term leaves no stable numerical operator behind it.
5. **`FLAG F10` — the rescue, exactly (arXiv preprint Eq. 4.2, p. 23).** The learned closure is projected onto an eddy-viscosity form,
   `R_tilde(F(U_i)) - R(F(U_i)) ~ mu_ANN . R_tilde(F_visc(U_i, grad U_i))`,
   with `mu_ANN = L( [R_tilde(F(U_i)) - R(F(U_i))] / R_tilde(F_visc) )` where `L()` is a **linear least-squares fit with zero bias** over the three components, applied **at every time step and every grid point**, giving one scalar viscosity per point. **Limiter: `mu_ANN` in `[-mu_0, 20 mu_0]`** where `mu_0` is the physical viscosity. Without the limiter the model "introduces **noticeable backscatter**" in the spectra (Fig. 11 right, p. 23). **With it, the scheme is stable** and gives "close agreement to the filtered DNS data and compares favourably to a current state of the art for LES with DG schemes." A-posteriori baselines compared: filtered DNS, no-model LES, Smagorinsky `C_s = 0.05`, Smagorinsky `C_s = 0.17`, and the reference eddy viscosity `mu_OP`.
   *A closure with 47% correlation to the truth cannot be run; the same closure, projected onto a one-parameter positive-definite operator and clipped to a 21-fold range, can. The 47% is the a-priori result and the projection is the a-posteriori model, and they are not the same object.*
6. **Architecture (arXiv preprint §3.2, pp. 15-17)**: residual CNN, **isotropic 3-D kernel size 3**, feature maps `nf1 = 16`, `nf2 = 32`, ReLU only, batch normalisation on all residual-block inputs, output compression in three pointwise steps. Inputs `x in R^{6 x p x p x p}` with `p = N+1 = 6` (**216 points per element**) = the three coarse velocities plus the three components of the known coarse-grid operator; outputs are the three momentum closure terms only (density and energy closures neglected per Garnier et al., since the closure/flux ratio is 1-2 orders larger for momentum). Loss is an **LGL-quadrature-weighted squared error** (Eq. 3.4, p. 16) — the DG mass matrix re-applied as a loss weight. **Adam**, mini-batch **~250** re-randomised each epoch, exponential learning-rate decay, **~60,000 iterations = 50 epochs**. TensorFlow 1.7 on Nvidia K40c and P100 at HLRS.
7. **The data cost, which is the paper's own explanation of its ceiling (Remark I, p. 7)**: storing `U` and `R(F(U))` at `dt = 4e-5 T*` for `0.2 T*` requires **~55 TByte**.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 22: "**Despite this important property, it is unrealistic to assume that the learned terms can provide an accurate and stable closure in the sense of Eqn. 2.7.**"
- p. 22: "while the short-term behaviour of the models is indeed dissipative as long as the solution is close to `U_bar`, **a direct closure in the sense of Eqn. 2.7 is not practical.**"
- p. 5: "since the RHS depends on the unfiltered solution `U`, **application of this approach is limited to specifically designed test cases where prior DNS information is available at every LES time step** and temporal integration errors are assumed to be negligible."
- p. 19: "**the achievable gains in cross-correlation saturate asymptotically for `d > 4` due to overfitting and the limited amount of training data.**"
- p. 20: "For the inner points, CCs of over 0.7 can be learned from the data, while the **surface correlation is significantly weaker. This is likely due to the non-isotropy of the data and the filter kernel at the element boundaries.**"
- p. 24: "**the performance of the prediction is likely limited by the available amount of data used for training, rather than network architectures.**"
- p. 7: "Since the full DNS solution needs to be stored at a large number of time steps, these operations are **very expensive in terms of computational and storage costs.**"

**What it cannot see**

- **`FLAG F10`: there is no a-posteriori error metric anywhere.** All a-posteriori comparison (Figs. 10, 11) is graphical and qualitative — "close agreement", "compares favourably". **No L2 error, no percentage improvement over Smagorinsky.** The 47%/73% numbers are a-priori correlations and cannot be quoted as deployment accuracy.
- **`FLAG F10`: no parameter count for any network, and no numeric learning rate** — only "exponential decay learning rate adaptation". No stride, padding or boundary treatment for the convolutions. **The training is not reproducible from the paper.**
- **No GPU-hours, no wall-clock, no DNS core-hours.** Only the hardware names and the 55 TByte storage figure.
- **One flow, one Reynolds number, one filter, one coarsening ratio.** Decaying HIT at `Re_lambda ~ 180`, filtered by L2 projection, coarsened 8x. Nothing about walls, shear, anisotropy or inhomogeneity — and the paper's own weakest correlations are precisely at the element *surfaces*, which is where inhomogeneity lives.
- **Inconsistency to flag**: `RNN2` appears in Table 3 and Fig. 8 but is **absent from Table 2**, which lists only RNN0, RNN1, RNN4, RNN8 and MLP100.
- **The training-set size is never stated as a number**, only as three factors.

---

### `Sirignano2020_dpm_les.pdf`

- **Category**: E (primary), G (co-primary — this is an adjoint-trained, solver-embedded closure and belongs equally to the differentiable-learning category).
- **Version**: **arXiv preprint 1911.09145v1** (20 Nov 2019), 28 pp. Journal: *J. Comput. Phys.* 423:109811. **NOTE THE AUTHOR ORDER**: the preprint is **Freund, MacArt & Sirignano**; the journal version and the manifest give Sirignano, MacArt & Freund. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: Embed a deep network `h_theta` **inside** the discretised LES PDE, `du/dt = f_nu(u, u_x, u_xx) + h_theta(u, u_x, u_xx)` (Eq. 1.1, p. 2), and train it **a posteriori** by minimising trajectory mismatch to filtered DNS, with gradients obtained from **adjoint PDEs** accelerated by a **stochastic adjoint method (SAM)** that samples one (case, time-interval) pair per optimisation step (Eqs. 2.4-2.6, p. 5).
- **Data used**: six `N = 1024^3` DNS of decaying isotropic turbulence in a `L = 66.5` periodic cube (Table 2, p. 13), `Re_t,0 = 1749`, `Re_lambda ~ 162`, at six viscosities `mu/mu_0 = 0.50, 0.75, 1.00, 1.25, 1.50, 2.00` — **cases 1, 3, 6 train; cases 2, 4, 5 test**. **12 simulations total** (6 viscosities x 2 random phasings); the initial TKE dissipation rate varies by a **factor of 64** across them. **Filter: box filter, `Delta/dx_dns = 16`** for the production case (4 and 8 also analysed); LES grid `64^3`; filter width set equal to the grid spacing.
- **Cases / flows and Re**: one flow class (decaying isotropic turbulence), six viscosities. DNS with **NGA** (fractional step, 2nd-order central, staggered), initial CFL 0.4; adjoint training in a Python/PyTorch solver matching the NGA discretisation, with autodiff used only for `grad_theta h_theta`.
- **Metric**: resolved-TKE decay `k(t)/u_rms,0^2` and resolved energy spectra, both against filtered DNS.

**Headline result with numbers**

1. **`FLAG F9` — THERE ARE NO PERCENTAGE ERROR REDUCTIONS IN THIS PAPER.** A full-text `%` search returns exactly three hits: "36%" and "9.2%" (figure-caption energy fractions, pp. 9-10) and "almost 50%" (the network's share of LES cost, p. 21). **Every DPM-vs-Smagorinsky comparison — Figs. 5, 6, 7, 8 — is graphical and qualitative. No tabulated error, no L2 norm, no percentage improvement exists. Any "% better than dynamic Smagorinsky" figure attributed to this paper would be fabricated.** The strongest statement the text makes (p. 16) is: "**the DPM outperforms the widely-used Smagorinsky model, whether the coefficient is determined dynamically or fixed at `C_S = 0.18`**", and that DPM "correctly learns the normalized evolution despite not having been trained on these dissipation rates."
2. **The a-priori/a-posteriori comparison, and why it is the paper's core (arXiv preprint §5.5, pp. 18-19)**. An **identical architecture with identical inputs** was trained a-priori on the loss `J(theta) = ||h_theta(u_bar) - div tau^r||` (Eq. 5.8) and deployed. Result, verbatim: "**Figure 7 shows the poor predictive performance of the a priori-trained deep learning closure model for LES.**" The stated reason is mathematical, not empirical: "**optimization does not commute with a nonlinear function.**" *Same network, same features, same data — only the loss differs, and the a-priori version fails. This is the controlled experiment that Duraisamy 2021 and Sanderse 2024 cite as settling the question.*
3. **`FLAG F19` — the stability threshold is a network-size threshold, and it is stated as a number (arXiv preprint p. 21)**: "**`N_H >= 50` required for long-time (`t >= 1e-3`) stability for `D.(u) = 0` and `N_H >= 100` without this constraint (`D.(u) != 0`)**." And crucially: "**No stabilizing limiters were used**"; "We do not attempt to prove stability of the DPM models." Fig. 8 (p. 22) shows the failure directly: at `N_H = 5` the case "**has become unstable at this time**" and `N_H = 25` "is showing signs of **high-wavenumber divergence**" — while "**Even `N_H = 25` show better agreement with spectra than the Smagorinsky models.**" *A model can be simultaneously more accurate than Smagorinsky and unstable. Compare Beck 2019, which needed a limiter, and Maulik 2019, which needed a truncation; DPM instead needs a minimum capacity, because the closure is trained through the solver.*
4. **Architecture (arXiv preprint Eq. 5.7, pp. 15-16)**: a **gated/multiplicative MLP** (two multiplicative gate branches, not a CNN), tanh nonlinearity, Xavier initialisation, **`N_H = 200` hidden units per layer -> `d_theta = 248,418` parameters**. Inputs `z` are the velocity components and their **first and unmixed second derivatives at the grid point and at the six nearest neighbours**; inputs are normalised "by the **same set of constants for all cases**". Optimiser **RMSprop** with a "standard decaying learning rate magnitude schedule" (**no numeric learning rate given**). **Training rollout: 5 LES time steps = 50 DNS time steps** forward, then the adjoint backward over the same interval. Distributed across GPU nodes, one randomly selected training field per node.
5. **Galilean invariance is explicitly NOT enforced, and the authors flag it (arXiv preprint p. 15, verbatim)**: "**This selection does not strictly enforce Galilean invariance, but this was not found to be a challenge. The issue of Galilean invariance should be considered further, especially in regard to further extrapolation from the training data that we consider here.**" *The one paper in the corpus that trains through the solver is also the one that abandons invariance — and it says the two are linked through extrapolation.*
6. **Table 1, arXiv preprint p. 11 — discretisation error measured, not assumed.** With `delta u_1` the LES-minus-DNS velocity-gradient error normalised by `<|grad u_bar|>_dns`:

   | Filtering | `Delta/dx_dns` | `Delta/dx_les` | `<|delta u_1|>/<|grad u_bar|>` |
   |---|---|---|---|
   | Implicit | 8 | 8 | 0.601 |
   | Implicit | 16 | 16 | **0.854** |
   | Implicit | 32 | 32 | **1.076** |
   | Explicit | 32 | 16 | 0.654 |
   | Explicit | 32 | 8 | 0.325 |
   | Explicit | 32 | 4 | 0.141 |

   At `Delta/dx_dns = 32` with implicit filtering the discretisation error **exceeds the average velocity-gradient magnitude** (p. 11). *This is the quantitative case for why a learned LES closure must absorb the discretisation error — and why the same closure will not port to another grid.*
7. **Compute, measured (arXiv preprint Tables 4-6, pp. 21-23)**. Network evaluation on a `64^3` mesh, 1 AMD Interlagos core vs 1 NVIDIA K20X: `N_H = 200` takes **10.49 s** on CPU and **0.153 s** on GPU (**68.5x**); smaller nets 36-63x. Network evaluation is "**almost 50%** of the total LES cost". Per-step, single core, `64^3`: no-model LES **7.57 s** (Fortran) / **14.11 s** (Python); Smagorinsky `C_S = 0.18` **7.73/14.24**; dynamic Smagorinsky **8.44**; DPM `N_H = 200` **27.86** (Python). At comparable accuracy on a single node (Table 6): Smagorinsky at `128^3` on 16 Fortran cores **6.47 s/step**, dynamic Smagorinsky **6.73**, **DPM at `64^3` on a K20X 1.60 s/step** — "approximately **one-quarter** the cost" — and the non-divergence-free DPM variant **0.31 s/step**, "approximately **one-twentieth** of the legacy-solution cost."
8. **The filter-cost note (p. 16)**: "halving the filter increases the operation count by approximately **a factor of 16**."

**Stated limitations (authors' own words, arXiv preprint)**

- p. 21: "**We do not attempt to prove stability of the DPM models, which would likely be challenging.**"
- p. 13: "For simplicity, we only consider cases in which the **filter width and LES grid resolution are equivalent, which is common practice though it lacks significant theoretical basis**."
- p. 19: "**a priori training as designed in this example requires a full training-target description of the to-be-modeled `div tau^r`. This is readily available in DNS, though not generally.**"
- p. 20: "We do recognize that **less explicitly represented physics is likely to diminish the capacity for extrapolation**, and that some form of validation would be needed as for any model reduction, machine learning or otherwise."
- p. 20: "Our expectation, in this case, is **some lost capacity to extrapolate to flows that include an important non-zero mean pressure gradient.**"
- p. 24: "Extending to more complex Navier-Stokes turbulence flows is an obvious direction. **An important challenge here will be to obtain and use training sets with sufficiently rich variability to enable extrapolation to new configurations.**"

**What it cannot see**

- **`FLAG F9`: no error percentages, no error tables, no L2 norms.** Items 1 and 2 above. The paper's central claims are read off spectra and decay curves.
- **No numeric learning rate, no RMSprop hyper-parameters, no epoch or SGD-step count, no training wall-clock or GPU-hours, no node count.** Inference cost is measured in detail; training cost is not stated at all.
- **Isotropic turbulence only.** No wall, no shear, no mean pressure gradient — and the authors name the mean pressure gradient as the extrapolation they expect to fail.
- **No batch size for SAM** (it samples one pair per step by definition) and no convergence criterion beyond "Repeat until a convergence criterion satisfied" (Eq. 2.6).
- **The learned closure absorbs the discretisation error of one specific solver on one specific grid** — item 6 quantifies how large that error is. Nothing tests transfer to another discretisation, and the authors' own Table 1 implies it should not transfer.
- **No reattachment, no complex-flow validation** of any kind.

---

### `Guan2022_stable_aposteriori_les_cnn.pdf` — **ARRIVED MID-SESSION, title-verified**

- **Category**: E (primary). Secondary: G — it is the a-posteriori-stability paper of this category, and its finding sits directly against the differentiable-training remedies of Category G.
- **PROVENANCE**: this file landed on disk during this cataloguing pass (2026-08-20 20:51) and was **not** in the 32-PDF corpus the earlier passes worked from. Identity verified by extracting page 1: printed title *"Stable a posteriori LES of 2D turbulence using convolutional neural networks: Backscattering analysis and generalization to higher Re via transfer learning"*, Guan, Chattopadhyay, Subel & Hassanzadeh (Rice University), arXiv margin stamp **arXiv:2102.11400v1 [physics.flu-dyn] 22 Feb 2021**, 30 pp. `MANIFEST.md` lists this key as `MISSING`; **it is now RETRIEVED-VERIFIED and the manifest needs the row** — see the report at the end of this document.
- **Version**: **arXiv preprint 2102.11400v1**. Journal: *J. Comput. Phys.* 458:111090 (2022). **All locations below are arXiv preprint page/Table/Figure numbers and will not match JCP.**
- **Method (one line)**: A **10-hidden-layer fully convolutional network with no pooling or upsampling** maps the two whole-field resolved variables `(psi_bar, omega_bar)` on the `256^2` LES grid to the whole-field SGS forcing `Pi` on the same grid, and is coupled **in the loop, frozen** with a Fourier pseudo-spectral 2-D vorticity solver: each LES step normalises the solver's fields, pushes them through the offline-trained network, de-normalises by `sigma_Pi`, and injects the result as the SGS term of the filtered vorticity equation (arXiv preprint Eq. 3a, p. 4; pp. 13-14).
- **Data used**: filtered DNS of 2-D decaying homogeneous isotropic turbulence, doubly periodic `[0, 2pi]^2`, Fourier pseudo-spectral, AB2 + Crank-Nicolson, double precision. **DNS `N = 2048`** for `Re = 8000, 32000, 64000` and **`N = 3072`** for `Re = 128000`. **LES `N_LES = N_DNS/8`, `Delta_LES = 8 Delta_DNS`, `dt_LES = 10 dt_DNS` — a 640x reduction in degrees of freedom** (p. 5). **Filter: Gaussian applied as the spectral transfer function `G(k) = exp(-|k|^2 Delta_F^2/24)` (Eq. 5, p. 7) followed by spectral truncation at `k_c = pi/Delta_LES`, with `Delta_F = 2 Delta_LES`.** 15 independent DNS runs per `Re` from random initial conditions, sampled every `10 dt_DNS` over `t in [50 tau, 200 tau]`, split **8 train / 2 validation / 5 test**. Production model **`n_tr` = 50,000 samples**.
- **Cases / flows and Re**: `Re = 8000, 32000, 64000, 128000`; main analyses at `Re = 32000`.
- **Metric**: **a-priori correlation coefficient `c`**, computed separately over grid points of forward transfer and of backscatter.

**Headline result with numbers**

1. **`FLAG F19` — Table 2, arXiv preprint p. 13, is the most directly useful table in the entire corpus for the a-priori/a-posteriori question.** One network, one flow, one `Re`, one solver; the only variable is the number of training samples:

   | `n_tr` | 500 | 1000 | 10000 | 30000 | 50000 |
   |---|---|---|---|---|---|
   | `c` (a-priori correlation) | 0.78 +/- 0.05 | 0.83 +/- 0.04 | 0.90 +/- 0.04 | 0.92 +/- 0.04 | 0.93 +/- 0.03 |
   | `c` on forward transfer `T>0` | 0.78 | 0.86 | 0.93 | 0.95 | 0.96 |
   | `c` on **backscatter** `T<0` | **0.63** | 0.76 | 0.89 | 0.91 | **0.92** |
   | **a-posteriori fate (5 random ICs)** | **unstable** | **unstable** | **unphysical** | **stable** | **stable** |

   **A model with a-priori correlation 0.90 produces "noisy, unphysical flows for some initial conditions"; the same architecture at 0.92 is stable.** Verbatim, p. 12: "**Only simulations with `n_tr >= 30000` are found to lead to stable and accurate a posteriori LES-CNN for any initial condition.**" The authors give the empirical threshold explicitly (p. 13): "between **`c = 0.90` and `c = 0.92`**, or if `c_{T<0}` is a better metric, between **0.89 and 0.91**."
   *This is the quantitative version of what Beck & Kurz assert qualitatively (99.9% a-priori correlation still diverging) and what Duraisamy 2021 states as doctrine. It is also a warning about how narrow the margin is: a 2-point change in a correlation coefficient separates a usable model from an unusable one.*
2. **Table 1, arXiv preprint p. 11 — a-priori correlation at `Re = 32000`, over 100 identical test samples:**

   | | DSMAG | ANN (Maulik-type, local) | **CNN** |
   |---|---|---|---|
   | `c` | 0.55 +/- 0.06 | 0.86 +/- 0.02 | **0.93 +/- 0.03** |
   | `c` on forward transfer | 0.55 | 0.86 | **0.96** |
   | `c` on **backscatter** | **0 (exactly)** | 0.83 | **0.92** |

   **The dynamic Smagorinsky model's backscatter correlation is exactly zero by construction**, because positive clipping (`nu_e >= 0`) is applied. Model sizes: **CNN 927,041 parameters; ANN 3,651 parameters** (pp. 9-10).
3. **`FLAG F19` — the training-set size IS the stabiliser, and no other stabiliser is used (arXiv preprint p. 21, verbatim)**: the LES-CNN is stable and accurate "**without any need for post-processing or additional eddy viscosity**", and p. 13: "the backscattering can be accurately captured and the a posteriori LES can be stable **without any further post-processing if the training set is large enough.**" **No clipping, no smoothing, no blending, no realisability constraint, and no added eddy viscosity is applied to the CNN.** The authors' view of the alternative (p. 3): such fixes are "**ad-hoc components [that] often substantially take away the advantages gained from the non-parametric, data-driven approach.**"
   *Set this against the rest of the corpus: Beck 2019 needed an eddy-viscosity projection with a limiter; Maulik 2019 zeroed half its own predictions on a sign test; Kaandorp 2020 capped its correction at 80% and Gaussian-smoothed it; Xiao 2016 clipped to the realisability square. Guan et al. show that on this flow the same instability is curable by 30,000 training samples instead. That is a genuinely different diagnosis of the same symptom, and it is the strongest available argument that "ML closures are unstable" is partly a statement about dataset size.*
4. **The mechanism, and the numbers behind it (arXiv preprint p. 13)**: with `T = sgn(grad^2 omega_bar) . Pi` (Eq. 16, p. 11), `T < 0` is backscatter. **`c_{T<0}` is below `c_{T>0}` at every training-set size**, and the gap "declines from **0.15 to 0.04**" as `n_tr` grows. The instabilities at small `n_tr` are attributed to "the **disproportionally lower accuracy** of the CNNs in capturing backscattering when the training set is small" (Abstract, p. 1). **Controlled demonstration (Fig. 8, p. 17): applying the same backscatter-removal rule used for the ANN to the CNN makes it "excessively diffusive (with performance comparable to that of the LES-DSMAG)"** — i.e. the learned advantage *is* the backscatter, and clipping it away returns the model to its baseline. *Graphical; no number.*
5. **Transfer learning to higher `Re`, and what it costs (arXiv preprint §4.3-4.4, pp. 18-22)**: a CNN trained at **`Re = 8000`** and applied directly at `Re = 32000` or `64000` fails (spectra "substantially deviating ... near `k_c`", Fig. 9). The fix: **freeze the first 8 of 10 convolutional layers, re-train only the last 2**, initialised from the low-`Re` weights, using **`n_tr^TL = 500` samples = 1% of `n_tr`**. Result: accuracy "**as good as** that of the LES-CNN trained with `n_tr` samples" at the target `Re`, demonstrated at **4x, 8x and 16x** the training Reynolds number (`Re = 32000, 64000, 128000`). An encoder-decoder wrapper extends the same 8 frozen layers to a `512^2` grid, re-training **three** layers with the same 500 samples. **A 1% data budget buys a 16x `Re` extrapolation** — the cheapest generalisation result in the corpus.
6. **Architecture choice is tied to accuracy (arXiv preprint p. 9)**: "using a fully CNN (i.e. without an up/down sampling) is **a key** to training an accurate SGS model, consistent with earlier findings that **pooling layers may artificially change spatial correlations of the data**." Loss is MSE on the normalised target (Eq. 10, p. 9), optimiser **Adam** with mini-batch SGD, ReLU throughout except a linear final layer, convolutional depth 64, filter size 5x5. **Networks run in single precision**; double precision was tried and gave "no distinguishable enhancement in the a posteriori tests" (p. 9). Code at `github.com/envfluids/2D-DDP`.
7. **A-posteriori rollouts run from `t = 50 tau` to `t = 200 tau` — 150 `tau` — from 5 random initial conditions** (Fig. 5 caption, p. 14; Fig. 6 caption, p. 15). The baseline LES-ANN **without** post-processing is unstable, "leading to rapid increases in `E` and blow up" (p. 14); **with** the backscatter-removal post-processing it is stable but "excessively dissipative (even more than DSMAG)".

**Stated limitations (authors' own words, arXiv preprint)**

- p. 13, the honest framing of their own headline: "**there is no established a priori metric and threshold to know if a data-driven SGS model is well-trained and accurate enough to lead to stable and accurate a posteriori LES.** In this study, the threshold is empirically between `c = 0.90` and `c = 0.92` ... To be clear, **these are just empirical thresholds in this testcase, and such thresholds might be case-dependent.**"
- p. 13: "**we do not claim that all instabilities in other a posteriori LES runs using data-driven SGS models (reported in other studies) are due to similar inaccuracies that could be reduced by enriching the training set.**"
- p. 21: "**Why learning backscattering requires more data remains to be studied in future work.** This might be because backscattering is fundamentally harder to learn data drivenly, or because backscattering is less frequent than forward transfer, or both."
- p. 19: "**the number of layers to be re-trained and the number of samples used for re-training depend on the problem and require some trial and error** for the best performance."
- p. 22: "Beyond the obvious need to study the performance of the CNN-based SGS models and transfer learning in **more complex turbulent flows (e.g., 3D, wall turbulence, stratified)** ..."
- p. 22: "**Establishing a connection between accuracy in a priori tests and stability in a posteriori tests would also be substantially helpful.**"
- p. 22: "in this work (and in most other SGS modeling studies), an '**offline training**' strategy is used ... At least some of the issues related to stability could be potentially resolved ... by using an '**online training**' strategy."
- p. 14, on the comparator: "it is possible that increasing the number of training samples for the ANN also leads to a more accurate and perhaps a stable LES-ANN; however ... a comprehensive investigation of LES-ANN is **beyond the scope of this paper**."

**What it cannot see**

- **Every a-posteriori result is graphical.** Figs. 5 (energy decay), 6 (relative `L2` error), 7 (vorticity snapshots), 8 (spectra and PDFs), 9 and 12 (transfer-learning spectra) **print no numbers anywhere in the text.** There is **no a-posteriori error value, no decay rate, no blow-up time, no spectral error, and no correlation coefficient for any transfer-learning case.** The only quasi-numeric a-posteriori statement is that LES-DSMAG's vorticity PDF deviates "beyond +/-2 standard deviations" at the tails (pp. 16-17). **Do not attach a number to the transfer-learning accuracy claim — there is none.**
- **No learning rate, no batch size, no epoch count, no training wall-clock, no training hardware, and no ML framework is stated.** Only the solver's compute allocation is named. **The number of re-trained parameters in the transfer-learning step is not stated** — only "2 out of the 10 convolution layers".
- **The stability verdicts rest on 5 random initial conditions per training-set size** (Table 2 caption, p. 13) over a single rollout length. No longer-horizon test and no larger ensemble is reported.
- **No invariance or equivariance is claimed.** A full-text search finds only one forward-looking sentence about exploiting flow symmetries in data augmentation (p. 22). Translational equivariance is implicit in the convolution but is never claimed or tested.
- **The network's input is the entire domain.** `(psi_bar, omega_bar)` on the full `256^2` grid map to `Pi` on the full grid, so the model is **tied to one grid size** — which is exactly why the higher-resolution transfer needed an encoder-decoder wrapper rather than simply being applied.
- **Two-dimensional decaying turbulence only**, doubly periodic, no walls, no shear, no mean flow. Everything in items 1-5 is measured in a flow whose energy cascade runs the wrong way relative to 3-D turbulence.
- **Uncertainty carried forward**: the transfer-learning sections use a `512^2` LES grid (Figs. 11-12) without restating the coarsening ratio; `2048/512 = 4` and `3072/512 = 6`, neither of which is the 8x used elsewhere. **The paper does not state which applies. Treat the TL coarsening ratio as unverified.**

---

### Missing analytical and learned SGS models `[NOT ON DISK]`

All `BLOCKED-ON-SOURCE`. **No numeric claim is made for any of them.**

- **Germano, Piomelli, Moin & Cabot 1991**, *A dynamic subgrid-scale eddy viscosity model*, Phys. Fluids A 3(7):1760-1765 — `MISSING` in `MANIFEST.md`. The dynamic procedure is the control against which every learned SGS closure in this section is implicitly measured (Sirignano 2020 uses it as a baseline; Maulik 2019 cites its averaging as the alternative to their truncation). Distilled from background knowledge in `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` §9, which is explicitly tagged there.
- **Bardina, Ferziger & Reynolds 1980**, AIAA Paper 80-1357 — `MISSING`. The scale-similarity model, which is the `SS` baseline that beats the ANN on five of six stress components in Maulik & San 2017 Table 6.
- **Vreman 2004**, Phys. Fluids 16(10):3670-3681 — `WRONG-QUARANTINED` (the file was arXiv:physics/0409022, *Critical dimension of Spectral Triples*). AIP paywall, no arXiv version. `FOUNDATIONAL_MODELS_INVENTORY.md` §11 writes the model out from background knowledge **and flags four claims that must be checked against the real paper**, including whether the near-wall decay is `y^1` (worse than WALE's `y^3`) — a limitation the usual summaries omit.
- **Park & Choi 2021**, *Toward neural-network-based large eddy simulation: application to turbulent channel flow*, JFM 914:A16 — `WRONG-QUARANTINED` (the file was arXiv:1710.07195, a power-systems paper). **This is the wall-bounded learned-SGS case the corpus lacks entirely**: every learned SGS paper on disk is isotropic (Beck, Sirignano) or two-dimensional (both Mauliks).
- **Zanna & Bolton 2020**, *Data-driven equation discovery of ocean mesoscale closures*, GRL 47:e2020GL088376 — `MISSING`.

---

## Category F — Wall-modelled LES

---

### `Piomelli2002_wall_layer_models_les.pdf`

- **Category**: F (primary), R (secondary — it is a review), E (tertiary).
- **Version**: **Journal of record** — *Annu. Rev. Fluid Mech.* 34:349-374, 2002. Page numbers below are the printed folios and are authoritative.
- **Method (one line)**: A review that establishes the taxonomy of LES wall-layer models — equilibrium laws (§2.1), zonal/two-layer approaches (§2.2), and "other methods" (linear stochastic estimation, suboptimal control, §2.3) — and prices each against the cost of resolving the viscous layer.
- **Data used**: none of its own; it is expository.
- **Cases / flows and Re**: the cases it reviews — channel flow, backward-facing step (`Re_h = 28,000` and `Re_h = 5,100`), airfoil trailing edge, rotating channel, DES-as-wall-model channels at `180 <= Re_tau <= 80,000`.
- **Metric**: skin-friction coefficient `C_f`, mean velocity, grid-point counts and cost-scaling exponents.

**Headline result with numbers**

1. **The cost-scaling ledger (pp. 350-354)** — the numbers that justify the entire wall-modelling enterprise:

   | Quantity | Scaling | p. |
   |---|---|---|
   | DNS grid points, 3-D | `Nx Ny Nz ~ Re_L^(9/4)` | 350 |
   | Boundary-layer growth | `delta ~ Re^0.2` | 351 |
   | Resolved-LES outer layer, grid points | `~ Re^0.4` | 351 |
   | Chapman's outer-layer count | **2500 points per `delta^3`** | 351 |
   | Viscous-sublayer points (Chapman) | `~ C_f Re_L^2`, and with `C_f ~ Re_L^-0.2`, `~ Re_L^1.8` | 351 |
   | Number of time steps | `~ (Nx Ny Nz)^(1/3)`, so total cost `~ (Nx Ny Nz)^(4/3)` | 351-352 |
   | **Wall-resolved LES cost, outer layer** | **`~ Re^0.5`** | 352 |
   | **Wall-resolved LES cost, inner layer** | **`~ Re^2.4`** | 352 |
   | **WMLES cost (equilibrium BC)** | **`~ Re^0.5`** | 354 |
   | DES-as-wall-model cost | `~ Re_tau`, "roughly `Re_L^0.9`" | 366 |

   And the consequence, p. 351: at `Re_L = O(10^6)`, **99% of the grid points resolve an inner layer only 10% of `delta` thick.**
2. **The accuracy target, and the verdict (p. 370)**: "the mean skin-friction coefficient must be predicted accurately, perhaps **within 5%** of resolved calculations." Immediately followed by: "**Present models do not satisfy these requirements.**" (`FLAG F12`.)
3. **The DES-as-wall-model failure, quantified (p. 367)**: Nikitin et al. (2000) produce an unphysical "DES buffer layer"; at `Re_tau = 20,000` the spurious high-intercept log region "extends roughly between `3000 < y+ < 15,000`", and "These errors were reflected in the skin-friction coefficient, which was **underpredicted by approximately 15%** in most of the calculations." **Refining the grid at `Re_tau = 20,000` "did not result in significant improvements."**
4. **The two-layer model works where the equilibrium law fails (p. 360)**: Balaras et al. (1996) TLM validated for **`200 <= Re_tau <= 2000`**; equivalent to equilibrium BCs in plane channel but **significantly better in a square duct** (corners, where the log law is invalid) and in a rotating channel. TLM cost is "marginally higher" than equilibrium BCs because "Two one-dimensional problems are solved, and **no Poisson-equation inversion** is required."
5. **The rotating-channel failure is a numerics failure (p. 360)**: "the model based on the logarithmic law **failed entirely owing to numerical instability introduced by the logarithmic boundary condition**" — TLM succeeded on the same case.
6. **Named failure magnitudes**:
   - Backward-facing step, Cabot (1996), `Re_h = 28,000`, grid 146 x 97 x 96 downstream of the step ("only **10% fewer** points than the resolved calculation"): reattachment good, but "a **stronger backflow** (compared with the experimental data)" and **no corner eddy**; upstream development-region wall stress **30% lower than experiment** (p. 364). A "dynamic" `kappa` gave inner-layer viscosity "**lower by more than a factor of 2**" with only a small `C_f` improvement (p. 363).
   - Airfoil trailing edge with standard TLM: "the skin-friction coefficient was **too high even in the attached region**"; fixed only by a dynamic mixing-length constant giving inner-layer `nu_t` "**lower by a factor of approximately 3**" (pp. 364-365).
   - TLM in channel flow, Cabot (1995): intercept shifts from an imposed `B = 5.5` to `B ~ 5`, and "the error is quite small: **the maximum velocity is underestimated by approximately 3%**" (p. 361).
   - LSE / suboptimal control: Nicoud et al.'s control cost was "**approximately 20 times** that for the uncontrolled LES" (pp. 368-369), and Baggett et al. found LSE accuracy "**deteriorates significantly** when the grid is modified or when a different numerical scheme is used."
   - Deardorff (1970): **6720 grid nodes ~ 400 points per `delta^3`** — "six times less than the number of required points estimated by Chapman (1979)" — and the results "do not compare well with the experimental data of Laufer (1950)" (p. 355).
7. **The validity floor for the statistical assumption (p. 353)** — a grid criterion nobody quotes and everybody needs: the grid must be **~1500 wall units streamwise and 700 spanwise** for the instantaneous-vs-log-law rms difference to be `< 10%`. If the grid is fine (`dx+ ~ 100-200`, `dz+ ~ 50-100`) "**the statistical considerations on which wall-layer models are based fail**"; if `dx+ > 1000, dz+ > 500` with the first point at `y+ < 50`, aliasing errors "corrupt the velocity field." *There is a window, and both edges are failure modes.*
8. **The sign of the log-layer mismatch is not universal (p. 370)**: "in the DES calculations of Nikitin et al. (2000) the intercept of the logarithmic law was **too high**, whereas in calculations that used the logarithmic law the intercept could be **either too high** (Piomelli et al. 1989) **or too low** (Nicoud et al. 2001)."

**Stated limitations (authors' own words)**

- p. 370: "**No extensive tests of wall-layer models in complex configurations exist.**"
- p. 370: "Wall-layer models are **not very effective (in the formulations presently in use) at transferring information to the outer layer** and tend to be more accurate when the inner/outer-layer interaction is one-way, with the outer layer supplying the forcing."
- p. 370: "Even in simple flows, **there is no a priori reason to expect that the inner-layer logarithmic law enforced, implicitly or explicitly, by most models will match the one established by the resolved calculation in the outer flow.**"
- p. 371: "**At present, reliable predictions cannot be expected except for fairly simple configurations.**"
- p. 371: "**the use of low Reynolds-number data for this purpose may actually hamper the development of wall-layer models**" — because wall models are *more* accurate at high `Re`, where grids are necessarily coarse in all directions (p. 353).
- p. 356: "extension to complex flows is impractical because **it relies on the accuracy of the RANS approach**."
- p. 369, on optimal control: "even the specification of the 'exact' wall stress **may not be sufficient to match the second-order statistics** at the inner-outer layer interface."

**What it cannot see**

- **It is a review; it measures nothing itself.** No table of any kind exists in this paper (13 figures, zero tables). Every number above is quoted from a cited study.
- **No head-to-head model comparison.** Comparisons are narrative and figure-based, so the paper cannot rank equilibrium against zonal models on a common metric.
- **No log-layer mismatch expressed as `Delta u+`** — only the 15% `C_f` and 3% `U_max` figures and the `B = 5.5 -> 5` intercept shift.
- **Written in 2002**: no data-driven wall model exists in it. It supplies the acceptance criterion (5% `C_f`) that Bae 2022 and Lozano-Duran 2023 should be judged against, and the observation that the criterion was unmet then.
- **No compute cost in CPU-hours anywhere** — only the Fig. 1 "present capabilities" line, which is a **Pentium III 933 MHz workstation with 1 Gbyte of memory** (p. 352). Treat every cost statement in this paper as a scaling exponent, not a runtime.

---

### `Larsson2016_wall_stress.pdf`

- **Category**: F (primary), R (secondary).
- **Version**: **Journal of record** — Larsson, Kawai, Bodart & Bermejo-Moreno, *Large eddy simulation with modeled wall-stress: recent progress and future directions*, **Mech. Eng. Reviews (Bull. JSME) 3(1):15-00418, 2016** (J-STAGE open access). **Pagination warning**: the printed folios extract with a spurious "2" prefix (PDF p. 3 prints as "23", p. 11 as "211"). **All page citations below are PDF page numbers 1-23**, so that any re-check must render the PDF page, not search for a printed folio.
- **Method (one line)**: A review that (i) defines WMLES as "inner layer (`y/delta <~ 0.2`) modeled, outer layer resolved", (ii) splits the field into **hybrid LES/RANS** (LES defined only above an interface) versus **wall-stress models** (LES defined to `y = 0`, `tau_w` supplied as a boundary condition), and (iii) argues that the log-layer mismatch is a **numerical** error of the first off-wall cells rather than a modelling error.
- **Data used**: none of its own beyond the authors' previously published simulations; Fig. 9 re-presents a supersonic flat-plate grid-convergence study.
- **Cases / flows and Re**: channel flow; supersonic flat-plate boundary layer at **`Re_delta = 6.1e5` (`Re_theta = 5e4`)**; NACA0012 upper surface at 2.5 deg AoA for the cost table; shock/boundary-layer interaction at **`Re_theta ~ 50,000`**; transition sensor calibrated on DNS channels with **`Re_tau` from 180 to 2000**.
- **Metric**: grid-point counts, log-layer mismatch in `u+`, `C_f`.

**Headline result with numbers**

1. **`FLAG F11` — the log-layer mismatch is a numerics error, and this is the mechanism (p. 11).** Their grid criterion (Eq. 6) requires `dx_i <~ (C_i/N) y`. With a kinematic wall-damping constant `C_2 <~ 2` and a Nyquist requirement `N >~ 2`, **`C_2/N < 1`**, so the criterion is "**violated in the first LES grid-point, regardless of numerical accuracy in the LES**". Consequence, stated as an exclamation by the authors: "**even a 'perfect' wall-model in one numerical code would suffer from a log-layer mismatch if implemented in a different numerical code!**"
2. **The sign is code-dependent (p. 10)**: positive mismatch for "almost all versions of hybrid LES/RANS"; wall-stress models split — positive (Piomelli 1989; Kawai & Larsson 2012) versus negative (Cabot & Moin 1999; Nicoud 2001; Lee 2013; Bose & Moin 2014). The pattern: "**the studies with a negative mismatch has generally been for incompressible flow solved using a staggered grid, whereas most results with codes using a colocated grid and/or some degree of numerical dissipation have produced a positive mismatch.**"
3. **The fix, with its convergence thresholds (p. 11)**: set `h_wm ~ 0.2 delta` **independently of the grid**, then refine. **Converged results have zero log-layer mismatch.** Thresholds for their 6th-order compact scheme: **`dy <~ 0.33 h_wm`** and **`dx ~ dz <~ 0.8 h_wm`**; independently confirmed by Lee et al. (2013) with a very different method at **`dx <~ 0.6 h_wm`, `dy <~ 0.3 h_wm`, `dz <~ 0.4 h_wm`**. The demonstration is Fig. 9, p. 12: fixed `h_wm/delta = 0.055`, fixed `dx/delta = dz/delta = 0.042`, sweeping **`dy_w/h_wm = 1.0, 0.50, 0.33, 0.25, 0.20`**.
4. **The one hard percentage (p. 11, quoting Wu & Meyers 2013)**: a wall-tuned Smagorinsky constant "was found to reduce the log-layer mismatch error **from a typical 10-20% to only 5%** in their numerical tests." **Direct `C_f` consequence (p. 10)**: "Since the skin friction coefficient `c_f ~ U_inf^-2`, the log-layer mismatch error has a direct effect on the predicted skin friction."
5. **The error-cancellation warning — the most transferable sentence in the paper (p. 18)**: "note specifically that the results in Fig. 5 are best (smallest log-layer mismatch) for the **coarsest** grid", and "**a flawed model may produce 'perfect' results by introducing errors that exactly cancel those present in the outer layer LES. For example, since most codes/numerics produce a positive log-layer mismatch, any modeling modification that by itself would produce a negative mismatch will lead to 'improved' results.**"
6. **Cost scalings (pp. 2-3)**: wall-resolved LES outer layer is **independent of `Re_tau`**; the viscous layer and the overlap layer are both **`O(Re_tau^2)`**; **WMLES grid is independent of `Re_tau`**. Below **`Re_tau <~ 600`** WMLES saves "at most 50% of the grid points" — i.e. it is not worth doing. Against DES97, "**WMLES incurs a cost 10-100 times higher than DES97**" for `dx/delta = dz/delta >~ 0.5`.
7. **Resolution recipes (pp. 2-3)**: wall-resolved LES viscous layer `(dx+, dz+) ~ (40, 20)`, `dy+_w ~ 1`; outer layer `(dx/delta, dz/delta) ~ (0.08, 0.05)`. **WMLES recommendation: `(dx/delta, dy_w/delta, dz/delta) ~ (0.08, 0.02, 0.05)`, stretched linearly up to `y/delta = 0.2`.**
8. **Table 1, p. 4 — NACA0012 upper surface at 2.5 deg AoA, total grid points** (first number span `= 0.1c`; parenthesis span `= 2 delta_TE`):

   | | `Re_c = 1e6` | `Re_c = 1e7` | `Re_c = 1e8` | exponent `alpha` in `~ Re_c^alpha` |
   |---|---|---|---|---|
   | Inner layer (`y/delta < 0.2`) | 1.6e7 (9.3e6) | 1.9e9 (8.9e8) | 2.0e11 (7.7e10) | **2.05 (1.96)** |
   | Outer layer (`y/delta > 0.2`) | 3.3e7 (1.9e7) | 7.2e7 (3.3e7) | 2.5e8 (9.5e7) | **0.44 (0.35)** |
   | `Re_tau` at trailing edge | 1000 | 10000 | 70000 | — |

   Their counts exceed Choi & Moin (2012) "by about a **factor of 10** for the inner layer and a factor ranging from **1** to **40** for the outer layer" (p. 4), attributed to streamwise `delta` variation that flat-plate correlations miss. **The acknowledgment (p. 19) records that Spalart identified an error in the original manuscript's Table 1 and Fig. 2** — a published cost table was wrong and was corrected in review.
9. **Transition (pp. 11-13)**: "**Existing wall-modeled LES approaches ... cannot predict transition**: since the wall-model assumes fully developed turbulence, the wall-model predicts a high level of wall shear stress `tau_w` even in the laminar region." Concrete failure, Catalano et al. (2003) cylinder: "the wall-model predicted a turbulent boundary layer around the full cylinder, with the associated late separation and low coefficient of drag, **regardless of the Reynolds number**" — the drag crisis is not captured at all. Fix: the Bodart & Larsson (2012) sensor `s_w = <rho_w> k / <tau_w>`, calibrated `2.5 <~ s_w <~ 4.0` over `20 <~ y+ <~ 0.2 delta+` across DNS channels `Re_tau` 180-2000, with **`s_lim = 0.25`** working well.
10. **Non-equilibrium wall models: the negative verdict (`FLAG F11`, §4.3, p. 19)**. Kawai & Larsson (2013) computed a shock/boundary-layer interaction at `Re_theta ~ 50,000`; the non-equilibrium results agreed excellently with experiment, "**the results using an equilibrium wall-model were also within the experimental uncertainties.**" Conclusion: "combining the experimental uncertainties with the lack of proven grid-convergence in most studies, one must conclude that **there has not yet been a truly convincing and conclusive demonstration of any superiority of non-equilibrium over equilibrium wall-stress-models in LES.**" And the inconsistency that generates the bad ones (§3.4.2, p. 15): discarding convection while retaining the pressure gradient is "physically **inconsistent**" — in Catalano et al. (2003) "the computed skin friction coefficient was **overpredicted by a factor of 3** on the front side of the cylinder."
11. **Why the equilibrium assumption survives**: Hickel et al. (2012) found instantaneous convection almost perfectly balanced by instantaneous pressure gradient above **`y+ >~ 30-50`** (p. 14); Coleman et al. (2015) found that across **`dp+/dx+` from -0.02 to +0.02**, `u+(y+ = 50)` varies only from **~16 (favourable) to ~14 (adverse)** (p. 14).
12. **Hybrid LES/RANS grid pathology (Fig. 5, p. 6)**: channel flow, fixed `y_int/delta = 0.15`, refining `dx/delta` from 0.25 to 0.047 — "**the mean velocity profile actually becomes less accurate during grid-refinement.**" And forcing-based fixes are non-predictive (p. 7): the mismatch is "essentially a **linear function of the forcing amplitude**", so "the idea of using small-scale forcing in hybrid LES/RANS has a **robustness problem**."

**Stated limitations (authors' own words)**

- p. 11: "**the LES is necessarily inaccurate in the first grid-point, and thus the wall-model is necessarily fed inaccurate input from the LES** whenever we define the wall-model to start at the first LES grid-point."
- p. 18: "properly performed WMLES is not computationally cheap - it can be orders of magnitude cheaper than LES, but it is still **orders of magnitude more expensive than both DES97 and RANS**."
- p. 18: "using a wall-model in LES alleviates the need to resolve the inner layer, but **is not a license to poorly resolve the outer layer.**"
- p. 18: "**it is mandatory to test all wall-modeled LES approaches on different grids: both by refining the grid and by modifying the aspect ratio of the grid**", and "it would seem prudent to assume (until proven otherwise) that **every WMLES approach may be sensitive to the grid-spacing and the grid-anisotropy.**"
- p. 19: "**The obvious problem, of course, is that `h_wm` should be chosen as a fraction of the boundary layer thickness `delta`, which is unknown a priori.**"
- p. 19, on their own scalar-variance modelling: "Larsson et al. (2015) simply resorted to the (**somewhat desperate**) assumption of it having zero wall-normal gradient in the log-layer; surely one can do better than that."
- p. 6, on seamless hybrid methods: "**it is very difficult (or perhaps impossible?) to demonstrate grid-independence**, at least in the sense meant here."

**What it cannot see**

- **No CPU-hours, core-counts or wall-clock times anywhere.** Cost is expressed purely in grid points and scaling exponents. Any runtime inference from this paper is an inference.
- **No mesh sizes in points for the authors' own simulations** — Fig. 9 gives only non-dimensional spacings.
- **No head-to-head comparison table of specific wall models.** Table 1 is a grid-cost estimate and is the paper's only table.
- **No log-layer mismatch stated numerically as `Delta u+`** in the text; Fig. 6's axis spans roughly -1.5 to +1 but that is an axis, not a datum.
- **No `C_f` error percentage for the authors' own WMLES results** — the 10-20% -> 5% figure is quoted from Wu & Meyers 2013.
- **Extraction hazard**: Fig. 10's caption exponent extracts as `c_f = 0.664 Re_x^(1/2)`; the Blasius result is `Re_x^(-1/2)` and the sign collapsed in the PDF text layer. **Treat that exponent as unverified from the text.**

---

### `Bae2022_marl_wall_model.pdf`

- **Category**: F (primary). Secondary: G — the policy is trained **in the loop with the LES solver**, though by reinforcement learning rather than by differentiating through it.
- **Version**: **arXiv preprint 2106.11144v2** (1 Feb 2022), 22 pp. Journal: *Nature Communications* 13:1443. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: **Multi-agent reinforcement learning (SciMARL)** in which every RL step *is* a WMLES time step: agents are grid points on both channel walls sharing one policy, each observing a local state and emitting a **bounded multiplicative correction `a_n in [0.9, 1.1]`** applied as `tau_w^m(t_{n+1}) = a_n tau_w^m(t_n)`, with the wall stress entering the LES as a **wall eddy viscosity** boundary condition `nu_t|_w = (du/dy|_w)^-1 (tau_w^m/rho) - nu` (arXiv preprint Eq. 9, p. 15), chosen over a Neumann condition specifically to reduce log-layer mismatch.
- **Data used**: **no DNS data is used for training.** The reward needs only the *mean* wall stress. Reward (Eq. 8, p. 14) = incremental improvement in `|tau_w - tau_w^m|/tau_w` plus a bonus indicator when within **1%** of the true mean wall stress. Two state spaces: **VWM** (velocity-based: `u*`, `du*/dy*`, `y*` at `h_m`) and **LLWM** (log-law-based: `1/kappa_m` and `B_m` inferred at `h_m`), both non-dimensionalised by `nu` and the **modelled** instantaneous friction velocity — i.e. no a-priori knowledge of the true `u_tau`.
- **Cases / flows and Re**: training on **turbulent channel flow only, `Re_tau ~ 2000, 4200, 8000`**, sampled uniformly per episode, grid `d ~ 0.05 delta`, domain `2 pi delta x 2 delta x pi delta`, AMD subgrid model, 2nd-order staggered finite differences (pp. 13-15). Testing on channels at **`Re_tau` = 5200, 1e4, 2e4, 5e4, 1e5, 1e6** (Table 1, p. 16) — an extrapolation of up to **125x** beyond the largest training `Re_tau` — plus a held-out **spatially developing zero-pressure-gradient flat-plate boundary layer, `Re_theta = 1000 to 7000`** (p. 8).
- **Metric**: error in friction velocity / wall stress; wall-stress fluctuation cross-correlation; `C_f`.

**Headline result with numbers**

1. **The headline bound (arXiv preprint p. 7)**: for the LLWM, "the prediction error in the friction velocity is **less than 4%**" over `Re_tau = 5200` to `1e6`. The error **increases with Reynolds number**, and the results "are comparable to ... the equilibrium wall model (**EQWM**) up to `Re_tau ~ 1e5`."
2. **`FLAG F2` — that is the ONLY numeric accuracy statement in the paper.** The per-`Re` errors exist **only as Fig. 3**, whose ordinate spans -70% to +10%; **axis tick labels are not data.** Anyone wanting per-`Re` numbers must digitise the figure. The turbulent-boundary-layer result is stated as "comparable to the `C_f` from the empirical values [Schlichting]" (p. 8) — **no numeric error is given.**
3. **The in-distribution / out-of-distribution contrast, which is the paper's real finding (p. 7)**: the VWM state variables carry `(h_m)+` explicitly, and the model was trained over **`150 < (h_m)+ < 1200`**. "Cases at **`Re_tau = 2e4` and `5e4`** produce high errors as the `(h_m)+` is not within the trained range"; refining the grid so that `(h_m)+` re-enters the band makes "**errors decrease significantly**". Two VWM velocity profiles are **omitted from Fig. 4(a) because they lie outside the plotted range** (Fig. 4 caption, p. 7). **The LLWM state, by contrast, is `Re`-free by construction (it is a log-law intercept and slope), and it extrapolates 125x.** *The generalisation gap here is a property of the state variables, not of the learning algorithm — the same network, same reward, same solver.*
4. **Wall-stress fluctuations (Figs. 6-7, p. 9)**: LLWM gives a maximum cross-correlation coefficient of **~0.3** between `u'` at `h_m = 0.1 delta` and the modelled `tau_w'`, "which matches the expected correlation from DNS" (**DNS value 0.3**). The **EQWM is perfectly correlated (coefficient 1) by construction** — an algebraic wall model cannot produce a decorrelated fluctuating wall stress at all. *This is the one statistic on which the learned model is structurally right and the classical one is structurally wrong.*
5. **Training setup, exact (Methods, pp. 12-14)**: algorithm **V-RACER** with **ReF-ER** replay (library `smarties`); discount **`gamma = 0.995`**; ReF-ER **`C = 1.5`, `D = 0.05`**; **Adam, learning rate 1e-5**; batch **512**; replay memory **1e6**; **1e7 policy-gradient steps**; policy net **2 hidden layers x 128 units**, **softsign** activations with skip connections; agents spaced **`4 dx` x `4 dz`** on each wall; **O(1e5)** experiences per simulation; simulation advanced **`2 delta/u_tau`** per learning iteration with the model updated every time step; `h_m` **resampled every time step** in `[0.075 delta, 0.15 delta]`; initial wall stress deliberately set **+/-20% off**.
6. **`FLAG F19`-adjacent — the stabilisers are explicit and quantified.** The action is **hard-bounded to a multiplicative `[0.9, 1.1]`**; the reward contains a 1%-band bonus, which the authors describe as the stabiliser ("The agent behavior is rendered stable by providing additional reward if the predicted wall-shear stress is within 1% of the true value", p. 5); and on the training side **ReF-ER clips far-policy gradients to zero** (Eq. 6, p. 13) — "We found that ReF-ER with hyper-parameters `C = 1.5` and `D = 0.05` ... **stabilizes training**". A-posteriori channel tests ran for **`300 delta/u_tau`**, 150x the `2 delta/u_tau` training window, with **no reported instability**; TBL runs for **50 washout times**.
7. **Cost (p. 10)**: the LLWM at `Re_tau = 4200` was trained with **O(1e3) CPU-hours** and **< 1 GB** of storage. The supervised alternative — generating the DNS data — would need **O(1e7) CPU-hours** and **> 100 TB**. **A four-order-of-magnitude cost argument for reward-based over label-based training, and it is the strongest such statement in the corpus.** Inference: "an **order of magnitude faster** than the EQWM that solves an ODE at each time step."
8. **Discretisation sensitivity (p. 16)**: the wall-shear stress changes **~5%** when the sampling point `y` is placed on a grid point rather than a midpoint. *A 5% sensitivity to a discretisation choice, against a headline accuracy of 4%.*

**Stated limitations (authors' own words, arXiv preprint)**

- p. 7: "because the model is trained on a limited range of `(h_m)+` in the training set, **the extrapolation of this behavior to much larger values of `(h_m)+` may be challenging.**"
- p. 7: "**The error increases with Reynolds number**, most likely due to the high variation of the streamwise wall-normal gradient with increasing Reynolds number as well as the departure of `(h_m)+` from the trained range of values."
- p. 13: "**Because we use conventional reinforcement learning update rules in a multi-agent setting, single parameter updates are imprecise.**"
- p. 13: "we found that further reducing the number of agents per simulation **reduced the model's adaptability** and therefore exhibit slightly lower performance."
- p. 3, on prior supervised wall models: "**Due to the single-step cost function, the resultant neural network model is not trained to compensate for the systematic discrepancies between DNS and LES (or WMLES) and the compounding errors.**"

**What it cannot see**

- **`FLAG F2`: no per-`Re` error table exists.** Only the "<4%" bound and Table 1's case list are numeric.
- **No numeric TBL `C_f` error**, no seed variance (the paper asserts "consistent training progress regardless of the initial random seed" without numbers), no wall-clock for the 1e7 gradient steps, no agent count (only spacing), no episode count.
- **One flow class trains the model.** Everything is learned from plane channel flow. The only geometry generalisation test is a flat-plate TBL — still an attached, equilibrium, zero-pressure-gradient boundary layer. **Nothing here tests separation, adverse pressure gradient, curvature, or three-dimensionality**, which are exactly the regimes Piomelli & Balaras and Larsson et al. name as the unsolved ones.
- **The reward needs the true mean `tau_w`.** In channel flow that is available from the imposed pressure gradient; in a general geometry it is the unknown. The paper's "no DNS needed" claim is true for this flow class and is not obviously portable.
- **The 5% grid-placement sensitivity is larger than the 4% headline error**, and the paper does not decompose the two.
- **`Re_tau = 1e6` is not validated against anything.** There is no DNS or experiment at that `Re`; the comparison is to the EQWM and to empirical correlations.

---

### `LozanoDuran2023_wall_model.pdf`

- **Category**: F (primary). Secondary: B (a supervised classifier-plus-regressor closure), X (its confidence score is an out-of-distribution detector).
- **Version**: **arXiv preprint 2211.07879v3** (30 Apr 2023), 35 pp. Journal: *J. Fluid Mech.* 963:A35. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: A **building-block-flow wall model (BFWM)**: a softmax **classifier** over seven canonical "building-block" flows (Laminar, Freestream, ZPG, FPG, APG, Separation, Unsteady) plus **five predictor networks**, whose outputs are blended by the classification probabilities, `tau_w y1/(mu u1) = sum_i p_class^i tau_w^i y1/(mu u1)` (arXiv preprint Eq. 2.6, p. 12), and which additionally emits a **confidence score** `p_conf = d_s/d_i` measuring how far the input sits from the training manifold.
- **Data used**: a DNS database of **~500 simulations** across the five turbulent blocks, but — and this is the paper's methodological point — **the training data are not filtered DNS.** They are generated by **E-WMLES** in the same solver: `ESGS` (a subgrid correction forced on-the-fly so that `<u_i>_xz = <u_i^DNS>_xzt`) plus `EBC` (a wall boundary condition reproducing the DNS p.d.f. of `tau_w` by inverse probability integral transform), §2.5, pp. 10-11. **Solver and grid numerical errors are therefore baked into the labels by design** (requirement (v), p. 4).
- **Cases / flows and Re**: training blocks — Laminar Poiseuille `Re_tau = 5` to `1e4`; ZPG channel `Re_tau = 100` to `10,000`; FPG/APG/Separation Poiseuille-Couette with `Re_P` from `-1.2e3` to `+1.2e3` and `Re_U` from `5e3` to `2e4`; Unsteady channel with a sudden spanwise pressure gradient, `Re_tau = 100-1000`, `Pi = 5-100`. Validation — laminar BL; ZPG TBL; **turbulent pipe `Re_tau ~ 40,000`**; Poiseuille-Couette APG/FPG sweeps; unsteady channel; **NASA CRM High-Lift at `Re = 5.49e6`, `M = 0.20`, 30 million grid points, AoA 7 and 19 deg**; **NASA Juncture Flow at `Re = 2.4e6`, AoA 5 deg, five points per boundary-layer thickness**.
- **Metric**: **internal** wall-stress error (against the model's own consistent target) versus **total** wall-stress error (against DNS/experiment); classifier precision/recall; `C_L`, `C_D`, `C_M`.

**Headline result with numbers**

1. **Classifier confusion matrix (Fig. 5, p. 13)** — precision per predicted class: Freestream **100.0%**, Laminar **100.0%**, FPG **83.5%**, ZPG **85.2%**, APG **83.7%**, Separation **92.2%**, Unsteady **98.3%**. Recall per true class: Freestream 100.0%, Laminar 100.0%, FPG **98.1%**, ZPG **74.0%** (26.0% missed), APG 83.7%, Separation 92.0%, Unsteady 94.4%.
2. **The internal/total error split is the paper's most useful idea, and it is quantified everywhere:**
   - **Laminar BL (Fig. 8, p. 16)**: internal error **below 1% and decaying for BFWM**, versus EQWM **"always above 20%"**. Mean velocity profiles within 5% for all combinations.
   - **ZPG TBL (Fig. 9, pp. 17-18)**: internal error **below 0.5% (BFWM) vs about 2% (EQWM)** — but **total** error is comparable for both, **between 5% and 15%**, while mean velocity profiles deviate **10% to 30%** from DNS.
   - **Turbulent pipe `Re_tau ~ 40,000` (Fig. 10, pp. 18-19)**: internal errors **below 5%** at the coarsest grid for both models; **total** wall-stress error **4% to 12%** for both, "mildly improved accuracy for the BFWM". Explicit note of **non-monotonic convergence under grid refinement**.
   - **Unsteady channel, `Pi = 80`, `h/Delta = 10` (Fig. 13, pp. 20-22)**: internal errors **below 1% for all times** for BFWM; the EQWM misses the `tau_{w,x}` drop entirely and has **`gamma_{1w} = 0` by construction** (an algebraic wall model cannot produce a wall-stress direction that differs from the local velocity direction).
   *The pattern: the learned model is dramatically better on the error it was trained against, and roughly tied on the error the user cares about. The authors name the reason — see the limitation quoted below about SGS models.*
3. **The APG/Separation result is where the paper is most honest (Figs. 11-12, pp. 19-20)**: on total wall stress, "**EQWM appears more accurate but for the wrong reasons**" — the EQWM underpredicts `tau_w` while overpredicting near-wall velocity, and the two errors cancel. ZPG cases: both models below **3%**. FPG total error "rises from **5% to 20%** for increasing favourable pressure gradient" for both.
4. **Extrapolation (arXiv preprint pp. 18-19, 24)**: the pipe at `Re_tau ~ 40,000` is **four times above the ZPG training band** (`Re_tau <= 10,000`) and internal errors stay **< 5%** — "the BFWM successfully **extrapolates to high Reynolds numbers**". And the geometry statement: "**the BFWM has never 'seen' an aircraft-like flow** or been trained in a case that resembles an aerofoil or a wing" (p. 24), yet gives "moderate improvements" on the CRM High-Lift.
5. **`FLAG F2` — the aircraft results carry NO numbers.** On the NASA CRM High-Lift, DSM-BFWM gives "**moderate improvements**" over DSM-EQWM in `C_L`, `C_D`, `C_M`, "especially close to the stall", biggest gain in pitching moment, **with the explicit exception of `C_L` at low AoA where the EQWM is better** (attributed to error cancellation). **No numeric `C_L`/`C_D`/`C_M` error values are given — Fig. 15 is a plot.** Context baseline (p. 2): prior WMLES with "over **350 million** degrees of freedom" still fail to match experiment.
6. **The confidence score works as an OOD detector, and the paper tests it (Table 1, p. 29, NASA Juncture Flow)**:

   | | (a) fuselage | (b) juncture | (c) juncture / trailing edge |
   |---|---|---|---|
   | FPG | 12% | 0% | 0% |
   | ZPG | 88% | 41% | 13% |
   | APG | 0% | 52% | 31% |
   | Separation | 0% | 7% | 56% |
   | **Confidence** | **98%** | **82%** | **22%** |

   At the fuselage both models have "errors below **2%**". At the trailing-edge juncture the confidence collapses to 22% — and the diagnosed reason is a grid fact, not a model fact: the separation bubble is **0.3 delta** thick against a WMLES grid `Delta ~ 0.2 delta`, i.e. "**only one grid point across the separation bubble**" (p. 27). Low-confidence (<20%) regions in the CRM case: leading edges of nacelle/slats/flaps, wing-tip and wing-root separation.
7. **Training setup (exact, pp. 12-13)**: classifier **5 hidden layers x 20 neurons**, ReLU, softmax, trained with **BFGS**; predictors **5 hidden layers x 30 neurons**, tanh-sigmoid + ReLU, trained with **Bayesian-regularization backpropagation**; **80/20 train/test split where the test set contains entire cases at `Re` and `Pi` values absent from training**; training data length **10 eddy-turnover times** (Unsteady cases 0.5-2); **O(1,000)-10,000 snapshots per E-WMLES**; **data augmentation by rotating the mean-flow direction in 5-degree steps from -45 to +45 degrees**; CFL 0.5; grid resolutions `Delta = h/N` for `N = 5, 10, 20, 40, 80, 160, 380`. Reported sensitivity: "reducing the time length of the training data below **3 eddy-turnover times** significantly reduced the performance of the ANNs." **Learning rate, batch size, epochs and sample count are not stated.**
8. **Cost (p. 13)**: **~12 hours per ANN on 4x NVIDIA A100 40 GB**. Runtime overhead of BFWM over the algebraic EQWM: **1.1 to 1.3x**. *A learned wall model costs 10-30% more per step than an algebraic one — a real number the corpus otherwise lacks.*

**Stated limitations (authors' own words, arXiv preprint §5, pp. 28-30)**

- p. 29, the sentence that reframes the whole result: "**A key conclusion of this work is that the main limiting factor in the accuracy of the BFWM predictions originates from external modelling errors due to the poor performance of SGS models.**"
- p. 29: "**Consistency between the model and the numerical/gridding schemes is solver-dependent. As such, the BFWM must be re-trained to yield accurate predictions in different flow solvers.**"
- p. 28: "the identification of meaningful building-block flows and **the minimum number of blocks required to make accurate predictions remains an open question.** The present version of the model uses seven building blocks, which is **far from being representative** of the rich flow physics that might occur in all complex scenarios ... Additionally, **there is no specific mechanism in the BFWM to faithfully capture the laminar-to-turbulent transition.**"
- p. 28, on the confidence score: "**low confidence scores may still result in accurate wall stress predictions and vice versa. Moreover, the confidence score does not provide an error bound on the value of the prediction.**"
- p. 16: "**WMLES might not converge to the DNS solution with grid refinements until the grid is in the DNS-like regime**, when the contribution of the wall model is negligible."
- p. 30: "in our experience, **the model performance is mainly controlled by the physical assumptions rather than by the details of the neural network architecture at hand.**"
- p. 29: "Variables from past time steps were not included in the model input."

**What it cannot see**

- **`FLAG F2`: the two flagship aerodynamic cases produce no numbers.** CRM High-Lift and most of Figs. 8-13 are graphical. The only tabulated data are the confusion matrix and Table 1's classification percentages.
- **No a-posteriori run durations** (flow-through or eddy-turnover times) are stated for any validation case — only the *training* data length. A stability claim cannot be extracted.
- **No instability, no limiter, no clipping is reported anywhere.** The only clip in the paper is `p_conf <= 1`.
- **The model is solver-locked by construction.** Because the labels are generated by E-WMLES *in charLES*, the learned wall model absorbs charLES's numerics. The authors say it must be retrained for a different solver. **This is the exact converse of Larsson et al.'s finding that the log-layer mismatch is code-dependent — here the code-dependence is deliberately learned rather than removed.**
- **Learning rate, batch size, epochs, sample count, parameter count: none stated.** The training is not reproducible from the paper.
- **No seed variance, no error bars anywhere.**

---

### Bose & Park 2018 — WMLES review `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: Bose, S.T. & Park, G.I. (2018), *Wall-modeled large-eddy simulation for complex turbulent flows*, Annu. Rev. Fluid Mech. 50:535-561. The file bearing this name in `_WRONG_RETRIEVALS/` is arXiv:1701.04413, *Unified Models of Neutrinos, Flavour and CP Violation* (hep-ph). Annual Reviews is paywalled. **No numeric claim is made here.** The framing this review would have supplied is taken instead from Larsson et al. 2016 and Piomelli & Balaras 2002, both journal-of-record files on disk; see also `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` §13.5c.

---

### Yang, Zafar, Wang & Xiao 2019 — PINN wall model `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: Yang, X.I.A., Zafar, S., Wang, J.-X. & Xiao, H. (2019), *Predictive large-eddy-simulation wall modeling via physics-informed neural networks*, Phys. Rev. Fluids 4:034602. The file bearing this name in `_WRONG_RETRIEVALS/` is arXiv:1904.09208, *Mean Force Kinetic Theory* (plasma physics). **No numeric claim is made here.** Its place in the taxonomy — a physics-informed feature set for a wall model, sitting between the algebraic EQWM and the fully learned models of Bae 2022 and Lozano-Duran 2023 — is noted so the gap is visible. `_common/FEASIBILITY.md` §1.5 records that its a-priori part would be cheap here (< 1 core-hour) once the source arrives.

---

## Category G — Differentiable / solver-in-the-loop learning

`Sirignano2020_dpm_les.pdf` is the adjoint-trained member of this family and is catalogued
**above under Category E**, with category codes E (primary) / G (co-primary). The four papers below
are the ones whose *training* passes gradients through the solver.

---

### `Strofer2021_differentiable.pdf`

- **Category**: G (primary). Secondary: B — the learned object is Pope's ten `g^(n)` coefficients, so this is a TBNN trained by adjoint rather than by supervision.
- **Version**: **arXiv preprint 2104.04821v1** (10 Apr 2021), 10 pp, JFM template. Journal: *Theor. Appl. Mech. Lett.* 11:100280. **All locations below are arXiv preprint page numbers.**
- **`FLAG F1` — SCOPE WARNING, READ BEFORE CITING.** The file on disk is **v1**. It contains **no ensemble-Kalman method, no ensemble-Kalman-versus-adjoint comparison, and no cost expressed in forward-solve equivalents.** A text search of both the extract and the PDF for "kalman" returns **zero** hits. If a downstream document needs the EnKF-vs-adjoint comparison, it is in a different Stroefer/Xiao paper, **not this file.** Do not attribute one to it.
- **Method (one line)**: An **end-to-end differentiable** RANS-plus-network loop. A deep network maps the five scalar invariants of the normalised velocity gradient to the ten Pope coefficients `g^(i)`; the RANS equations are solved to convergence with those coefficients frozen; a **continuous adjoint** supplies `dJ/dtau`, network backpropagation supplies `dg/dw`, and the chain closes analytically through `dtau/dg^(i) = 2k T^(i)` (arXiv preprint Eq. 2.1, p. 3, and p. 5). The loss `J` is a mismatch in **velocity** — i.e. the model is trained from **indirect observations**, never from Reynolds-stress labels.
- **Data used**: **synthetic truth for two cases and DNS for the third.** §3.1 channel `Re = 10,000` — a **single point** of synthetic velocity, truth is a constant `g^(1)`. §3.2 square duct `Re = 3,500` — **full-field** synthetic velocity, truth is the **Shih quadratic k-epsilon model** written out in Eq. 3.1, p. 8. §3.3 periodic hills `Re = 5,600` — **four point measurements** of both velocity components, from the DNS of Xiao et al. (2020).
- **Cases / flows and Re**: as above. **Grid resolutions are not stated for any case.** Solver: segregated **SIMPLE**.
- **Metric**: **none.** See below.

**Headline result with numbers**

1. **`FLAG F1` — THIS PAPER REPORTS NO NUMERIC ERROR METRICS AT ALL.** There is no MSE, no percentage, no reduction factor anywhere in the text. The results are:
   - §3.1, Fig. 2 (p. 6): "The trained model not only results in the correct velocity field, but **the correct underlying model is learned**"; the caption states "The final (trained) results overlap with the truth and **the two are visually indistinguishable**."
   - §3.2, Figs. 3-4 (pp. 7-8): only **two** combinations of coefficients are learnable — `g^(1)` and `g^(2) - 0.5 g^(3) + 0.5 g^(4)` — and the latter "shows good agreement **only for the higher range** of scalar invariant `theta_1`".
   - §3.3 (p. 8): the trained linear model "closely predicts the true velocity in most of the flow **with the exception of the free shear layer in the leeward side of the hills**."
   **The catalogue metric for this paper is "none reported".**
2. **The synthetic-truth design is the paper's real contribution, and it is a falsifiability argument (arXiv preprint p. 8, verbatim)**: "**This shows the importance of using synthetic data to evaluate the ability of a training framework to learn the true underlying model when one exists rather than only comparing the quantities of interest.**" *If a framework cannot recover a closure that is known by construction to exist and to be representable, nothing else it reports means anything. `_common/FEASIBILITY.md` §1.4 rates this "the single cleanest falsifiable experiment in the entire list".*
3. **The identifiability result, which is a permanent constraint on indirect training (arXiv preprint p. 8)**: in the duct, only two coefficient combinations can be recovered from velocity data. The authors give the mechanism: "**the smaller scalar invariants corresponding to smaller velocity gradients and smaller magnitudes of the tensors `T`. The velocity field is therefore expected to be less sensitive to the value of the Reynolds stress in these regions.**" And separately: "The trained model **fails to predict the correct `tau_yz` in the center channel**, but this does not propagate to the predicted velocities." *A closure can be wrong in a way the observable cannot see. Training on velocity cannot fix what velocity does not constrain.*
4. **Convergence economics, stated as a ratio (arXiv preprint p. 8)**: "obtaining significant improvement in the velocity field requires only **a few tens of training steps** and only requires the coefficients to have roughly the correct order of magnitude. On the other hand obtaining better agreement of the scalar coefficients took **1-2 orders of magnitude more training steps** with diminishing returns in velocity improvement." *Getting the answer is 100x cheaper than getting the model.*
5. **`FLAG F19` — the implicit/explicit split, which is the numerics fix (arXiv preprint Eq. 2.4, p. 4, verbatim)**: the momentum equation is written
   `u.grad u - div(nu_eff grad u) - grad u . grad nu_eff + div(a_NL) + grad p* = s`, `div u = 0`,
   with **`nu_eff = nu - g^(1) k t_tau`**, `a_NL = 2k sum_{i=2..10} g^(i) T^(i)`, `p* = p + 2k/3`; "**the term `div(nu_eff grad u)` is treated implicitly.**" Justification, verbatim (p. 4): "**When solving the RANS equations, explicit treatment of the divergence of Reynolds stress can make the RANS equations ill-conditioned (Wu et al. 2019; Brener et al. 2021). We treat part of the linear term implicitly by use of an effective viscosity `nu_eff` which is easily obtained since with the integrity basis representation the linear term is learned independently.**" *The tensor-basis representation is not only an invariance device — it is what makes the implicit split available, because it isolates the linear coefficient. This is the cleanest statement of that connection in the corpus, and it is the same fix Wu 2018 (Category D) measures as `O(10^2) -> O(1)`.*
6. **`FLAG F19` — two further stabilisers, both stated (arXiv preprint p. 5)**:
   - **Initialisation**: "**The usual practice of random initialisation of the weights is not suitable in this case since it leads to divergence of the RANS solution.**" The fix is **pre-training to an existing closure** — laminar `g^(i) = 0` for the channel and hills, LEVM `g^(1) = -0.09` for the duct — with **noise deliberately added to the pre-training data** because "starting from very accurate constant values can make the network difficult to train". The authors note the side benefit: "This has the additional benefit of **embedding existing insight into the training by choosing an informed initial point in the parameter space**."
   - **The adjoint transpose convection term is deleted**: "When solving the adjoint equation using a segregated approach such as the SIMPLE algorithm used here, the adjoint transpose convection term `grad u_hat . u` is treated explicitly and **can result in instabilities** ... For this reason it is common to dampen or eliminate this term, and **here we eliminate it.**" *A term is dropped from the gradient because the solver cannot carry it. The gradient being optimised is therefore not the exact gradient, and the paper says so.*
7. **Hyper-parameters (exact)**: **Adam** with default settings and **learning rate 0.001**; general network **10 hidden layers x 10 neurons, ReLU**. Channel case: 1 input -> 1 output, **1021 trainable parameters**. Duct: 2 inputs -> 4 outputs. Hills: 1 input -> 1 output. Inputs are rescaled to **`[0, 1]` at every training step**. `k` and the turbulence timescale come from conventional transport equations with the TKE production modified to `P = tau : grad u`. **One full RANS solve per training step**; the invariants are updated from the previous solution and frozen within a step. **Batch size, epochs and iteration counts are not stated.**
8. **The one generalisation test (arXiv preprint p. 9, Fig. 6)**: trained on periodic hills at slope parameter **`alpha = 1` only**, tested at **`alpha = 0.5, 0.8, 1.2, 1.5`**. Result, verbatim and directional: "For the `alpha > 1.0` cases **the trained linear model outperforms the k-omega model in the entire flow**. For the `alpha < 1.0` cases the trained model results in better velocity predictions in some regions, particularly the upper channel, while **the k-omega model results in better velocities in the lower channel**." `alpha = 1.5` is milder separation than training; `alpha = 0.5` is massive separation. **Generalisation degrades in the direction of stronger separation, and there are no numbers.**

**Stated limitations (authors' own words, arXiv preprint)**

- p. 5: "**The usual practice of random initialisation of the weights is not suitable in this case since it leads to divergence of the RANS solution.**"
- p. 5: "the adjoint transpose convection term ... **can result in instabilities** ... **here we eliminate it.**"
- p. 8: "**The trained model fails to predict the correct `tau_yz` in the center channel**, but this does not propagate to the predicted velocities."
- p. 8: "The combination `g2 - 0.5g(3) + 0.5g(4)` **shows good agreement only for the higher range** of scalar invariant `theta_1`."
- p. 8: "The trained model is a spatially varying LEVM ... that closely predicts the true velocity in most of the flow **with the exception of the free shear layer in the leeward side of the hills.**"

**What it cannot see**

- **`FLAG F1`: no error metric, no MSE, no percentage, no reduction factor. The catalogue metric is "none reported".** Also absent: iteration/epoch counts, batch size, **grid resolutions for any case**, convergence criteria, compute cost of any kind (no CPU-hours, no wall-clock, no hardware, no forward-solve-equivalent count), validation protocol, and seed variance.
- **`FLAG F1`: no ensemble-Kalman comparison exists in this file.** The only method comparison is a one-sentence remark in the introduction (p. 2) that gradient-free genetic programming "may not be as efficient as gradient-descent methods".
- **Two of the three cases have synthetic truth.** That is deliberate and is the paper's strength for falsifiability, but it means **only the periodic-hill case tests the method against real turbulence**, on four point measurements.
- **Internal sign inconsistency**: §3.1 (p. 6) says the synthetic truth is "a constant `g^(1) = 0.09`", while §2.3 (p. 5) and §3.2/§3.3 use "a linear model with `g^(1) = -0.09`", and Fig. 2(a) plots `g^(1)` going negative. **Flagged as printed; not resolved here.**
- **The gradient is deliberately inexact** (item 6), so the optimisation is not solving the problem it states.
- **Steady RANS only.** "A-posteriori stability" here means convergence of a steady solve, not time-integration stability; nothing in this paper bears on rollout length.

---

### `Um2020_solver_loop.pdf`

- **Category**: G (primary). Secondary: R — its NON/PRE/SOL taxonomy is the reference framing the whole category now uses.
- **Version**: **arXiv preprint 2007.00016v2** (5 Jan 2021), 37 pp. Published: **NeurIPS 2020**. **All locations below are arXiv preprint page/Table numbers.**
- **Method (one line)**: A CNN correction operator `C(s|theta)` produces an **additive correction field** applied after every solver step, `s_tilde_{t+n} = (P_s C)^n (T r_t)`, and is trained by back-propagating through the differentiable PDE solver **`n-1` times** (arXiv preprint §2-3.1, pp. 4-5), where `n` is the **look-ahead / unrolled-step count** and is the paper's controlled variable.
- **Data used**: five scenarios, all self-generated (Table in §3, and Appendix B):
  | Scenario | Source grid | Reference grid | `Re` / parameters | Volume |
  |---|---|---|---|---|
  | 2-D unsteady wake | 32 x 64 | 128 x 256 | train `Re in {97.7, 195.3, 390.6, 781.3, 1562.5, 3125.0}`; **test `Re in {146.5, 293.0, 585.9, 1171.9, 2343.8}`** | 500 steps/case, ~98M reference cells |
  | Buoyancy-driven flow | 32 x 64 | 128 x 256 | train marker radius `r ~ U(0.1, 0.25)`; **test `U(0.05, 0.1)` and `U(0.2, 0.3)`** | 48 ICs x 1000 steps |
  | Forced advection-diffusion (Burgers) | 32 x 32 | 128 x 128 | 20 overlapping sine forcing modes | 10 sims x 200 steps |
  | CG solver | 64 x 64 | — | closed boundaries | 3k sims x 16 steps |
  | 3-D wake | 32 x 32 x 64 | 128 x 128 x 256 | train 8 `Re` in [58.6, 625.0]; **test 7 different `Re`**; validate on 3 more | 500 steps |
  The reference is **4x finer in each spatial direction** throughout. A **constant field encoding the Reynolds number** is an input for both wake cases.
- **Cases / flows and Re**: as above. **All test sets have parameter distributions differing from training** (§3.2, p. 5).
- **Metric**: **mean absolute error of velocity** against the downsampled reference, plus an L2 error of `u_x` in the frequency domain, plus CG iteration counts.

**Headline result with numbers**

1. **Table 1, arXiv preprint p. 7 — the headline comparison. MAE +/- std, and relative improvement over the uncorrected source simulation (SRC):**

   | Experiment | SRC | PRE | NON | SOL_s | **SOL** | PRE % | NON % | **SOL %** |
   |---|---|---|---|---|---|---|---|---|
   | Wake flow | 0.146+/-0.004 | 0.031+/-0.010 | 0.049+/-0.012 | 0.041+/-0.009 | **0.013+/-0.003** | 79% | 67% | **91%** |
   | Buoyancy | 1.590+/-1.033 | 1.373+/-0.985 | 1.080+/-0.658 | 0.944+/-0.614 | **0.620+/-0.390** | 19% | 29% | **60%** |
   | Adv.-diff. | 0.248+/-0.019 | 0.218+/-0.017 | 0.159+/-0.015 | **0.152+/-0.015** | 0.158+/-0.017 | 12% | 36% | 36% |
   | CG solver* | 121.6+/-13.44 | – | – | 79.03+/-10.02 | **29.59+/-14.83** | – | – | **76%** |
   | 3-D wake | 0.167+/-0.061 | – | 0.144+/-0.074 | – | **0.130+/-0.058** | – | 14% | **22%** |

   (*CG row is iterations to reach accuracy `1e-3`.) **NON** = plain supervised, no solver interaction — "most commonly applied supervised approaches use this variant". **PRE** = a pre-computed, time-regularised constrained-least-squares corrector. **SOL** = solver-in-the-loop.
2. **Table 2, arXiv preprint p. 21 — the look-ahead sweep, 2-D wake, MAE at 5 test `Re` over 500 steps:**

   | Model | SRC | NON | PRE_SR | PRE | SOL_4 | SOL_8 | SOL_16 | **SOL_32** |
   |---|---|---|---|---|---|---|---|---|
   | Regular (260,354 weights) | 0.146 | 0.049 | 0.036 | 0.031 | 0.041 | 0.031 | 0.023 | **0.013** |
   | Smaller (56,898 weights) | 0.146 | 0.092 | 0.083 | 0.059 | – | 0.042 | 0.035 | – |

   **The error falls monotonically with unrolled length: 0.041 -> 0.031 -> 0.023 -> 0.013 for `n = 4, 8, 16, 32`.** Frequency-domain L2 error of `u_x` behaves the same: 0.194 -> 0.128 -> 0.101 -> **0.051** (SRC 0.557). Fig. 5 caption (p. 19): "The SOL_32 reduces the error introduced by SRC by a **factor of 11.2** on average"; p. 19: SOL_32 with the larger model "reduces the MAE ... to **less than 9% (on average) of the error induced by the source simulation**."
3. **Table 3, arXiv preprint p. 26 — buoyancy, MAE over 10 test conditions x 300 steps**, showing the same monotone trend to much longer horizons: velocity SRC 1.590, NON 1.079, PRE 1.373, SOL_2 1.027, SOL_16 0.859, SOL_32 0.775, SOL_64 0.695, **SOL_128 0.620**. Marker `d`: 0.677 -> **0.391**. Look-ahead scaling (p. 8): 1-4 steps gives up to **40%**; **64** recurrent iterations gives "more than **54%**"; **128** gives **60%**.
4. **`FLAG F19` / F7-adjacent — the ablation that shows solver interaction is not the same as data augmentation.** Same table: injecting **noise** into a NON model at the best amplitude `sigma ~ 1e-4` gives **34.5%** improvement (a weaker perturbation gives 30.6%) versus SOL's **60.0%** (pp. 8, 24). And allowing a non-interacting model to evolve `n` steps *without* interaction is actively harmful: **NON_d4 MAE 3.196 versus SRC 1.590** — a factor of ~2 **worse than doing nothing** — with "NON_d8 significantly distorting the flow behavior, instead of improving it" (p. 24). *Noise is not a substitute for the solver; and a supervised model let loose on its own trajectory destroys the flow.*
5. **`FLAG F19` — the 3-D wake is where NON cannot be trained at all (arXiv preprint p. 33, verbatim)**: "we were **not able to train a stable NON version despite numerous tests**. While the models performed well for ca. **100 to 150 time steps**, small scale oscillations induced by the corrections accumulate and start to strongly distort the flow ... In contrast, the **SOL_16 version retains its stability over the course of long simulations with several hundred steps**." Fig. 26a: NON "performs well initially, even slightly surpassing SOL_16 around **frame 100**, [but] the errors quickly grow afterwards, eventually leading to a performance that is **worse than the source simulation**." *Note Table 6 (p. 34) shows the same in a statistic: the NON kinetic-energy frequency error **0.074 is worse than SRC's 0.0614**, while SOL_16 improves it to 0.058.*
6. **`FLAG F19` — the training-side instability and the curriculum that fixes it (arXiv preprint p. 8, verbatim)**: "Especially during the early stages of training, an inferred correction can overly distort the physical state. Performing time integration via the PDE then typically leads to **exponential increases of existing oscillations and a diverging calculation**. Hence, we found it important to **pre-train networks with small look-aheads (we usually use SOL_2 models), and then continue training with longer recurrent iterations** ... **we saw no specific gains** from, e.g., starting a SOL_32 training with a SOL_2 model versus a SOL_16 model." The 3-D model used exactly this: **200k iterations at SOL_8, then 100k at SOL_16**. **No gradient clipping and no limiter on the correction field is used anywhere.**
7. **Where more look-ahead stops helping, and why (arXiv preprint p. 6, p. 27, p. 31)**: on the **forced** advection-diffusion case the optimum is `n = 2` (MAE 0.148) and longer horizons are *worse* (SOL_4 0.152, SOL_8 0.158). Authors' explanation, verbatim (p. 6): "**Learned correction functions need to be able to anticipate future behavior to make high-quality corrections. The randomized forcing in this example severely limits the number of future steps that can accurately be predicted given one state.**" On the CG solver, "**more than 5 iterations lead to a slight increase in the required iterations**" (p. 31). *The useful unroll length is set by the predictability horizon of the physics, not by the optimiser.*
8. **Generalisation, measured (arXiv preprint p. 19)**: "**Despite a factor of 16 between the Reynolds numbers, there is no significant decrease in performance** across the different cases. Only the NON version exhibits slightly larger errors for higher Reynolds numbers ... the performance is largely uniform for the SOL versions." All buoyancy test simulations use "**an out-of-distribution parametrization of the initial conditions**" (p. 8).
9. **A physics-based loss is worse than a data loss here (arXiv preprint p. 6, Table 5, p. 32)**: on the CG solver, `SOL_DIV` (divergence-based physics loss) "requires **63% more steps** to reach a desired accuracy" than SOL. To reach `1e-2`, the CG solver needs "around **two steps** in conjunction with SOL_5, **nine steps** with NON, **28 steps** with SOL_DIV and **78 steps** starting from zero."
10. **Cost, measured (Appendix C, p. 35)**: hardware **Intel Xeon E5-1650 (12 vCores @ 3.60 GHz) + NVIDIA GTX 1080 Ti**. Training iteration times: buoyancy SOL_2 **0.21 s**, SOL_4 0.42 s, SOL_16 1.25 s; wake SOL_8 0.6 s, SOL_16 1.3 s, SOL_32 2.5 s. Inference, 3-D wake, 100 steps: reference **913.2 s** versus SOL_16 hybrid **13.3 s** — "**more than 68 times faster**". Buoyancy, 100 steps: CPU reference 5.79 s, source solver alone 0.476 s, SOL_128 network evaluation accumulating 0.43 s. Model sizes: wake **260,354**; buoyancy **35,954**; adv.-diff. **261,154**; CG U-Net **127,265**; **3-D wake 1,002,411**. Optimiser **Adam** throughout, learning rate `1e-4` for SOL/NON. **Three seeds per case for the 2-D wake** (p. 18).
11. **Model-size returns are flat (arXiv preprint p. 24)**: going above 100k weights (~3x regular) yields only **+3.6%**; a further **4x** increase yields only **+0.3%**; halving costs **-8.7%** or more.

**Stated limitations (authors' own words, arXiv preprint)**

- p. 8: "The training via differentiable physics **incurs an increased computational cost at training time**, as the PDE model has to be evaluated for `n` steps for each learning iteration, and the calculation of the gradients is typically of similar complexity as the evaluation of the PDE itself."
- p. 27: "**If ... external and unpredictable influences such as the randomized forcing terms dominate the behavior, the model has a reduced chance to predict the right correction function.**"
- p. 33: "This is a good example of the **undesirable shift of distributions for the inputs**: once the phase space trajectories produced by the hybrid method leave the distribution of the regular source states seen at training time, **the model fails to infer reasonable corrections.**"
- p. 16: "As both the deep neural network for `C` and likewise the PDE `P_s` are potentially **highly non-linear operators**, the corresponding coupled minimization problem ... **is challenging.**"
- p. 31: "**more than 5 iterations lead to a slight increase in the required iterations**. We assume that this behavior is potentially caused by evaluating the loss only for the final output of the `n` iterations."
- p. 35: "we believe these **performance results are preliminary**, and far from the speed-up that could be achieved in optimal settings."
- Broader Impact, p. 9: "there is a wide range of established tools, some of which still use COBOL and FORTRAN. Hence, **it will not be easy to integrate deep learning methods into the existing solving pipelines.**"

**What it cannot see**

- **No turbulence closure is learned.** The correction is a generic additive velocity field with no constitutive structure — no tensor basis, no eddy viscosity, no invariance. It absorbs discretisation error, not sub-grid physics, and the paper does not claim otherwise.
- **`Re <= 3125` in 2-D and `<= 625` in 3-D.** These are laminar-to-transitional wakes. Nothing here is turbulence at engineering `Re`, and the "wake flow" improvements should not be read as closure results.
- **No total training wall-clock or GPU-hours** — only per-iteration times. No memory footprint. No PRE pre-computation cost (described only as "relatively expensive").
- **The `SOL_s` entry for the buoyancy row of Table 1 (0.944) does not appear in Table 3**, whose SOL columns are 2/16/32/64/128. The shorter-look-ahead model there is unlabelled.
- **Fig. 4f/4g's per-`n` look-ahead sweep for the wake is graphical**; the numbers quoted in item 3 for buoyancy come from the text.
- **The learned correction is grid-locked.** Every experiment maps one fixed coarse grid to one fixed reference grid at 4x. Nothing tests a different coarsening ratio or a different discretisation.

---

### `Kochkov2021_ml_accelerated_cfd.pdf`

- **Category**: G (primary). Secondary: E — the LES variant learns a subgrid-scale-equivalent correction.
- **Version**: **arXiv preprint 2102.01010v1**, 13 pp. Journal: *PNAS* 118(21):e2101784118. **All locations below are arXiv preprint page/Table numbers.**
- **Method (one line)**: A JAX-differentiable finite-volume staggered-mesh 2-D incompressible solver in which a fully convolutional network emits, per cell, either **(a) learned interpolation (LI)** — constrained interpolation coefficients for the convective flux with `sum a_i = 1`, guaranteeing at least first-order accuracy — or **(b) learned correction (LC)**, an additive residual; **divergence, pressure projection and explicit Euler time stepping remain standard numerics**, and the loss is accumulated over **32 unrolled steps**.
- **Data used**: ground truth generated at `2048^2` or `4096^2` and **subsampled by a factor of 32 in each dimension and in time**; **32 trajectories of 4800 sequential steps** from different random initial conditions. Dataset sizes **12,200 slices** (decaying) to **34,770 slices** (forced). Each model trained **9 times** from different random initialisations.
- **Cases / flows and Re** (Table A1, p. 9): Kolmogorov flow `2048 -> 64` at `Re = 1000`; `4096 -> 128` at `Re = 4000`; a 2x-larger domain `4096 -> 128` at `Re = 1000`; decaying turbulence `2048 -> 64` at `Re = 1000`; and an **LES case at `Re = 1e5`** with Smagorinsky-Lilly ground truth at `C_s = 0.2`. Forcing `f = sin(4y) x_hat - 0.1 u`. CFL fixed at **0.5**.
- **Metric**: pointwise vorticity correlation over time, energy spectra, and a **stability fraction** — "the fraction of simulated velocity values that does not exceed the range of the training data" (p. 6).

**Headline result with numbers**

1. **`FLAG F6` — the headline, and the caveat that must travel with it (Abstract, p. 1; restated p. 7)**: the learned solver "matches the accuracy of an advanced numerical solver running at **8-10x finer resolution**, while performing the computation **40-80x faster**." **The DNS case, Fig. 2 (pp. 4-5): learned interpolation at `64 x 64` matches the pointwise accuracy of direct simulation at `2048 x 2048` — a 32x grid ratio, quoted as ~10x per dimension.** The LES case (Fig. 6, p. 8): "learned interpolation for LES still achieves an effective **8x upscaling**, corresponding to roughly **40x speedup**."
2. **The speed-up is derived, and the derivation is the part to carry (arXiv preprint p. 5)**: at grids `>= 256^2` the network achieves **12.5x higher FLOP throughput** than the baseline solver, so despite performing **150x more arithmetic operations** the ML solver is only **~12x slower at equal resolution**; a 10x gain in each of three dimensions (two space plus time via CFL) then gives **`10^3/12 ~ 80`**. Cost model (Eq. 2, p. 7): `T ~ (C_ML + C_physics)(N/K)^(d+1)` with **`C_ML/C_physics ~ 12`** currently, extrapolating to 3-D speed-ups of `1e3-1e4`. Benchmarked on **a single core of a Google Cloud TPU v4** (p. 5).
3. **`FLAG F6` — WHAT THE 40-80x IS MEASURED AGAINST.** The baseline is a **first-order-in-time explicit Euler** solver. List et al. 2022 (below) run the same class of experiment on a **second-order PISO** solver and obtain **~2-4x coarsening and 3.3-14.4x speed-up**, and attribute the gap explicitly to solver order (List, arXiv preprint p. 27). **These two headline numbers are not comparable and must never be quoted side by side without the solver order.**
4. **LI beats LC (arXiv preprint p. 6)**: learned interpolation gives **10x** effective upscaling versus learned correction's **8x** — "corresponds to about a factor of two in run-time". And even "a modest **4x** effective coarse-graining still corresponds to a **5x** computational speed-up" (p. 7).
5. **Generalisation, three tests (arXiv preprint pp. 5-6)**:
   - **Larger domain**: "essentially the exact same performance as on the training domain"; the improvement on a **2x** domain is "**identical** to that found on a smaller domain" (Appendix E, p. 10).
   - **Decaying (unforced) turbulence** with a model trained on forced Kolmogorov flow: "can match the accuracy of DNS running at **~7 times finer resolution**".
   - **Higher Reynolds number**: a new `Re = 4000` dataset; because the smallest eddy scales as `1/sqrt(Re)`, the `Re = 1000` model is reused simply by **halving the grid spacing**, and "our model achieves the accuracy of DNS running at **7 times finer resolution**".
   *Two of the three generalisations cost 3 units of effective resolution (10 -> 7) and neither required retraining.*
6. **The controlled comparison against black-box ML (arXiv preprint pp. 6-7, Fig. 5)**: ResNet and Encoder-Processor-Decoder baselines "exhibit **high sensitivity to random initialization and do not generalize well**, with much less consistent statistical accuracy and stability", while LI/LC show "a **narrow spread of model performance for different random initialization**" across the 9 seeds. *Nine seeds per model is the strongest seed protocol in the corpus, and the finding is that the physics-constrained hybrid is what makes the seed spread small.*
7. **Stability**: assessed at simulation time 50, "after about **7000 time integration steps**" (~14,000 for the more turbulent flow), with long evaluation trajectories of "tens of thousands of time steps" used "to verify that models remain stable". **No divergence of LI or LC is reported. All non-learned baselines are perfectly stable.**
8. **Hyper-parameters (exact)**: **Adam**, learning rate **1e-3**, `b1 = 0.9`, `b2 = 0.99`; loss is a cumulative pointwise MSE over the unrolled window; **32 unrolled steps**, with gradient checkpointing at each model step in some cases; interpolation stencil is a **4 x 4 patch** giving **15 unconstrained network outputs** per coefficient set, `N_out = 120` for LI and `N_out = 2` for LC. Baselines: EPD hidden size 64, ResNet hidden size 2. **Parameter count, batch size and epoch/iteration count are not stated.**

**Stated limitations (authors' own words, arXiv preprint)**

- p. 2: "**The methods we derive are equation specific, and require training a coarse resolution solver with high resolution ground truth simulations.**"
- p. 3, a result worth its own line: "**We also explored LC models restricted to take the form of classical closure models (e.g., flow-dependent effective tensor viscosity models), but the restrictions hurt model performance and stability.**" *This is direct counter-evidence to the constrain-the-model-form doctrine of Categories A and B, and Sanderse 2024 (Category R) cites exactly this kind of finding as evidence that the case for physics constraints is "rather thin".*
- p. 7: "**Further speed-ups, as required to capture the full range of turbulent flows, will require either more efficient representations for flows ... or being satisfied with statistical rather than pointwise accuracy** (e.g., as done in LES modeling)."
- p. 10: "Our experiments found accuracy was slightly improved by using larger neural networks, **but not sufficiently to justify the increased computational cost.**"
- p. 10: "**Due to computational limits, we were unable to run the simulations on the 16384 x 16384 grid for measuring accuracy**" — so the 8x-larger-domain point on the Fig. 1(a) Pareto frontier is an **extrapolation**, with accuracy taken from the 1x domain.

**What it cannot see**

- **Two-dimensional only.** The 3-D speed-up of `1e3-1e4` is an extrapolation of the cost model (Eq. 2), not a measurement.
- **No training wall-clock, no TPU-hours, no parameter count, no batch size, no epoch count.** The paper is precise about inference cost and silent about training cost.
- **The speed-up claim is a claim about accelerator throughput**, and `_common/FEASIBILITY.md` §1.4 records that on this lab's 16-CPU machine reproducing it "is meaningless ... and any attempt would be NOT A RESULT". Only the accuracy claim is reproducible here.
- **No numeric value is given for the time at which any model's vorticity correlation crosses 0.95** — that is read from Fig. 5's axis. Spectral errors are likewise figure-only (axes `1e7`-`1e9`).
- **The stability metric is a range check, not a norm bound**: "the fraction of simulated velocity values that does not exceed the range of the training data". A model can pass it while being wrong.
- **The LES ground truth is Smagorinsky at `C_s = 0.2`, not DNS.** For the `Re = 1e5` case the learned model is being trained to reproduce a closure model, so its errors are measured against a model, not against turbulence.

---

### `List2022_learned_turbulence.pdf`

- **Category**: G (primary). Secondary: E.
- **Version**: **arXiv preprint 2202.06988v2**, 40 pp. Journal: *J. Fluid Mech.* 949:A25. **All locations below are arXiv preprint page/Table numbers.**
- **Method (one line)**: A **differentiable second-order PISO** finite-volume solver (TensorFlow plus custom CUDA operators) in which a fully convolutional CNN reads the coarse-grid **velocity and pressure-gradient fields (4 channels)** and emits a **corrective forcing field (2 channels)** injected at PISO's **implicit predictor step** — so continuity is still satisfied — trained by back-propagating through `m` unrolled solver steps against downsampled DNS.
- **Data used**: three flows, each downsampled **8x in space AND 8x in time** (an effective `8^3 = 512` reduction):
  | Case | Domain | DNS grid | Coarse grid | `Re` |
  |---|---|---|---|---|
  | Isotropic decaying turbulence (IDT) | `(2pi, 2pi)` periodic | 1024 x 1024 | 128 x 128 | `Re = 126` initial -> `296` final |
  | Temporal mixing layer (TML) | `(40pi, 20pi)` | 1024 x 512 | 128 x 64 | `Re_dw = 250` |
  | Spatial mixing layer (SML) | `(256, 64)` | 2048 x 512 | 256 x 64 | `Re_dw = 500` |
  TML uses 3 simulations (2 train, 1 test) of 12,000 DNS steps; SML uses **5 training simulations** with different inlet perturbations and **32,000 samples** of the statistically steady state.
- **Cases / flows and Re**: as above. **All test sets are outside the training parameter range** — TML test perturbation `(a, w) = (9.0, 0.3)` versus training `(6.0, 0.7)` and `(3.3, 1.5)`; SML test inlet `(0.082, 0.018)` outside the five training pairs spanning `eps_1 = 0.075 ... 0.025`.
- **Metric**: **MSE of velocity** at a stated evaluation time, plus MSE of `k` and a spectral energy ratio.

**Headline result with numbers**

1. **`FLAG F7` — Table 1, arXiv preprint p. 9, IDT, MSE at `t_1 = 64 dt` and `t_2 = 512 dt`:**

   | Model | Loss | Unrolled steps | MSE @ `t_1` | MSE @ `t_2` |
   |---|---|---|---|---|
   | NoModel | – | – | 2.78e-3 | 0.057 |
   | LES (Smagorinsky) | – | – | 2.69e-3 | 0.051 |
   | **NN_sup,T (supervised, 1 step)** | `L_T` | 1 | 1.52e-3 | **0.369 (diverges)** |
   | NN_1,T | `L_T` | 1 | 1.65e-3 | 0.046 |
   | **NN_10** | `L_2` | 10 | 4.23e-4 | **0.018** |
   | NN_10,T | `L_T` | 10 | 4.25e-4 | 0.022 |
   | NN_30,T | `L_T` | 30 | **4.09e-4** | 0.021 |

   **The supervised one-step model is the best of all at `t_1` and 6.5x WORSE THAN NO MODEL AT ALL at `t_2` (0.369 vs 0.057).** The authors record the mechanism (p. 9): "the temporal advancement of the forward simulations greatly surpasses the unrolled training horizon, which leads to instabilities with the **supervised and 1-step model**, and ultimately to the **divergence of their simulations**" — the 1-step model was excluded from further evaluation. *This is the single most quotable a-priori/a-posteriori inversion in the corpus: the best short-horizon model is the worst long-horizon one, on the same test, in the same table.*
2. **Table 3, arXiv preprint p. 14, TML, MSE at `t_e = 512 dt` on test data**: NoModel **1.25e-3**; NN_10 (`L_2` only) 3.19e-4; NN_10,LT 3.31e-5; NN_30,LT 2.26e-5; **NN_60,LT 1.93e-5**. The best learned model is **64.8x better than no model**, and adding the composite loss to a 10-step model improves MSE by **9.6x** over `L_2` alone.
3. **Table 5, arXiv preprint p. 17, SML, MSE at `t_e = 1000 dt`**: NoModel **2.03e-2**; NN_10,LT 5.22e-3; NN_30,LT 3.66e-3; **NN_60,LT 2.98e-3** — "outperforms the no-model baseline by an order of magnitude" (**6.8x**).
4. **`FLAG F7` — the gradient sub-range study, which is the paper's central engineering result (§6, arXiv preprint p. 22).** The question is: over a 60-step unrolled rollout, how many of those steps should the gradient actually traverse?

   | 60-step model, gradient sub-range | TML MSE @ 512 dt (Table 6) | SML MSE @ 1000 dt (Table 7) |
   |---|---|---|
   | 10 | 2.36e-5 | **2.44e-3** |
   | 20 | 2.19e-5 | 2.73e-3 |
   | 30 | **1.93e-5** | 2.98e-3 |
   | **60 (full)** | **TRAINING UNSTABLE — no value** | **1.19e-2** |

   **Full 60-step back-propagation is training-unstable on TML and ~4x worse on SML** (1.19e-2 against 2.98e-3, i.e. barely better than the no-model 2.03e-2). Optimum sub-range **20-30 steps**; "a split into 2 subranges of 30 steps each performed best"; saturation "at **circa 60 steps, which coincides with the integral timescales**" (p. 24). **Explicitly contrasted with the standard ML remedy (p. 28): "This approach differs from the common practice in machine learning, where gradients of early evaluations of the neural network are usually discarded or re-scaled when gradient clipping is applied." No gradient clipping is used.**
   *Read together with Um 2020: Um found the useful unroll length is set by the predictability horizon; List finds the useful* gradient *length is set by one integral timescale, and that the two lengths differ — you can roll forward 60 steps while only differentiating through 20-30.*
5. **The loss ablation, Table 9, arXiv preprint p. 40** — four cumulative loss terms (`L_2` velocity; `L_E` log-spectral energy distance; `L_S` L1 rate-of-strain; `L_MS` multi-step mean-flow L1). On the statistically steady SML **every added term helps**, the full loss giving **~9.7x lower MSE(u) at `t_2`** than `L_2` alone (0.0025 vs 0.0243); on the two **transient** cases `L_MS` **hurts** (IDT `t_2` MSE rises from 0.166 to 0.182; TML from 2.15e-4 to 9.11e-4). *A loss term that encodes a statistically steady state damages a transient one, and the paper measures it.*
6. **`FLAG F19` — a-posteriori stability tied to unroll length, with a threshold (arXiv preprint pp. 19-20)**: on SML the forward run is **5000 dt = 36 periods of the slowest perturbation mode**, "orders of magnitude longer than what is seen by the models at training time". The **60-step model stays stable**; the **10-step model "develops instabilities after 500 dt, which is equivalent to one flow-through time"**; the 30-step model shows this "to a lesser extent"; the 60-step model "practically eliminates the instabilities". Purely data-driven non-differentiable models "produce undesirable solutions **within a few time steps**" (p. 17). The SML loss-ablation horizon was cut from 1000 to 500 dt because "**stability concerns limited the horizon**" (p. 40).
7. **`FLAG F6` — the speed-up, and why it is smaller than Kochkov's (§7, Table 8, arXiv preprint p. 26)**: the learned model "consistently outperforms simulations with a **2x higher resolution**", often on par with 4x. Quoted speed-ups: **3.3x** (IDT vs a 2x reference), **7.0x** (TML vs 3x), **3.7x** (SML vs 3x), and **14.4x** (TML matching a 4x simulation for several hundred steps). Network overhead over no-model at the same resolution is "**circa 10%**" — measured as IDT 0.071 vs 0.066 s/step, TML 0.156 vs 0.145, SML 1.815 vs 1.817. **The authors state the reason for the gap (p. 27): "While other works have reported even larger performance improvements [Kochkov et al., 2021], we believe that our measurements are representative of real-world scenarios with higher-order solvers."**
8. **Training cost, stated in the only currency that matters (arXiv preprint pp. 26-27)**: on one **GTX 1080Ti**, IDT **61 h**, TML **78 h**, SML **240 h** ("3 to 10 days") — equal to **[120, 118, 22] full-length DNS solves** respectively. *The learned model must be re-used at least 22-120 times before it repays its own training.*
9. **Hyper-parameters (exact)**: **7 convolutional layers**, kernels `[7, 5, 5, 3, 3, 1, 1]`, leaky ReLU, channel widths `[8, 8, 16, 32, 32, 32]`, 4 inputs -> 2 outputs, **~82,000 trainable parameters**, Glorot Normal init, zero-padded at non-periodic boundaries. **Adam**, `b1 = 0.9`, `b2 = 0.999`, learning rate **1e-5**, decay factor **0.4**. Curriculum: "models trained on **more than 10 steps were initialised from a pre-trained 10-step model**". Loss weights `(lambda_2, lambda_E, lambda_S, lambda_MS)`: IDT `(10, 5e-2, 1e-5, 0)`; TML `(100, 2, 5e-2, 0)`; SML `(50, 0.5, 2, 0.5)`. Smagorinsky baseline for IDT: `C_s = 0.008`, chosen from `[0.17, 0.08, 0.02, 0.008, 0.002]` by velocity MSE at 100 dt (`[12.21, 6.824, 4.320, 4.256, 4.364] x 1e-3`). **Batch size and epoch count are not stated.**

**Stated limitations (authors' own words, arXiv preprint)**

- p. 5, on invariance: "**any principles of the modelled physics, like Galilean invariance in the case of SGS-closure, must be learnt by the network itself. The choice of network inputs is by no means trivial, but shall not be further studied in this paper.**"
- p. 22, on why very long horizons fail: "**the flow field is uncorrelated to the DNS data for these long horizons, leading to a diffused learning signal** ... the longer runs used the same set of hyperparameters as determined for the shorter unrollments, [so] the long horizon runs could also profit from a broader hyperparameter search."
- p. 28: "our method has several limitations, such as the **initial one time cost to train the neural network** turbulence model. Also, **our tests have focused on regular, Cartesian grids.**"
- p. 27: "our comparisons are based on **GPU solvers**, and performance is likely to vary on CPU or mixed solvers."
- p. 37: "We found that the training procedure was stable for learning rates in the neighbourhood of that value, however **no extensive hyper-parameter tuning was performed.**"

**Failure cases, in the authors' own words**

- **SML early roll-up (arXiv preprint pp. 18-19)**: "Especially early stages of the mixing layer immediately after the first roll-up are modelled inaccurately. While all models show this behaviour, the delay in terms of momentum thickness is **more pronounced for the long unrollment 60-step model**"; and "a noticeable offset in the vorticity thickness around `x/d_w0 = 100` **for all models**".
- **Longer is not always better (arXiv preprint p. 22, Fig. 20)**: the **120-step model gives no improvement** over 60; "the mixing layer shift downstream of the first roll-up is **worse** in direct comparison"; and **180 and 240 steps "saw a reduced accuracy"**.
- **`L_2`-only models are unstable on TML** over long horizons and introduce nonphysical oscillations (p. 15).

**What it cannot see**

- **No invariance of any kind is enforced or checked** — the authors say so explicitly and decline to study it. The correction is a raw forcing field.
- **Two-dimensional only**, at `Re` 126-500. As with Um 2020, these are not engineering Reynolds numbers.
- **Batch size and epoch count are not stated**, nor the total DNS snapshot count for IDT and TML (only SML's 32,000).
- **The numbers behind Figs. 7-15 and 18-21 are figure-only.**
- **Cartesian grids only**, GPU solver only, one coarsening ratio (8x in space and time) throughout.
- **The model is trained against the *downsampled DNS trajectory*, so it absorbs both the closure error and the temporal-downsampling error, and the paper does not separate them.**

---

## Category H — Multi-model aggregation

---

### `deZordoBanliat2023_space_dependent_aggregation.pdf`

- **Category**: H (primary). Secondary: D (its predictive variance is a model-choice uncertainty measure); X (10-feature set).
- **Version**: **arXiv preprint 2301.09013v1**, 27 pp. Journal: *J. Comput. Phys.* 485:112114. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: **XMA (space-dependent model aggregation)** forms a per-cell convex combination of `N_M = 4` independently converged RANS solutions, `delta(eta*) = sum_m w_m(eta*) delta^(m)(eta*)`, where the weights are **not** Bayesian posterior probabilities and **not** mixture-of-experts gates but an **exponentially weighted average / sequential-model-aggregation cost** `g_m = exp(-0.5 (delta^(m)(eta_d) - delta_d)^2 / sigma^2)` (arXiv preprint Eq. 9, p. 7), normalised across models, with `g_m` regressed over a **10-dimensional flow-feature space by random forests** so the weights can be evaluated at unseen points and unseen scenarios (Eq. 17, p. 9).
- **Data used**: **the "truth" is SYNTHETIC.** It is a full field generated by an **EARSM k-kL model** (Wallin-Johansson anisotropy plus Smith k-kL transport), **not DNS and not LES.** The authors' reason, verbatim (p. 13): "High-fidelity DNS and LES simulations exist in the literature for this cascade ..., but unfortunately **only limited results from those datasets are publicly accessible.** This is why, for the aims of the present proof-of-concept study, we considered instead **synthetic data sets** generated through the reference EARSM k-kL model." **`FLAG F5`: every accuracy number in this paper is an agreement with another RANS model, not with turbulence.**
- **Cases / flows and Re**: a **NACA 65 V103-220 linear compressor cascade**, 2-D RANS at mid-span of a highly loaded axial-compressor stator, blade aspect ratio `h/l = 1.36`, at four inflow scenarios (Table 2, p. 11):

  | | S1 | S2 | S3 | S4 |
  |---|---|---|---|---|
  | `beta_1` | **36.99 deg** | 39.97 | 44.09 | 49.2 |
  | `Ma_1` | 0.654 | 0.674 | 0.666 | 0.65 |
  | `Re_1` | 302K | 302K | 298K | 289K |
  | `Tu` (%) | 2.9 | 3.3 | 3.2 | 3.5 |

  **S1 is the deliberate extrapolation case**: its incidence sits *below* the whole training range and is "a severely off-design angle of attack" (p. 14). Solver **elsA** (ONERA), cell-centred FV, Roe + 2nd-order MUSCL, 1st-order backward Euler with local time stepping, convergence = **6 orders of magnitude** residual drop; grid **6 matching blocks, 30,880 cells**, `y+ < 1.0` on both blade surfaces. **4 models x 4 scenarios = 16 baseline RANS runs.**
- **Component models aggregated (§3.3.1, p. 12)**: **Spalart-Allmaras**, **Wilcox k-omega (2006)**, **Launder-Sharma k-epsilon** (`C_mu = 0.09`), **Smith k-L**.
- **Metric**: MSE of four quantities of interest — velocity, pressure, skin friction, total pressure — **normalised by the worst component model** and presented as bar charts.

**Headline result with numbers**

1. **`FLAG F5` — THE ONLY NUMBER IN THE PAPER.** On the **S1 extrapolation** case (train on {S2, S3, S4}, predict S1), arXiv preprint p. 23: "**the MSE for the velocity is reduced by approximately 1/3 with respect to the best-performing baseline RANS model.**" That is the entire numeric content of the results. **Figs. 8 and 13 are bar charts with normalised axes spanning 0.0-1.2 and no printed values. There is no MSE table in this paper.** Do not attach a number to any other claim from it.
2. **The interpolation case, stated qualitatively (arXiv preprint p. 20, Fig. 8)**: training and predicting on S2, k-epsilon "is consistently less accurate than all other models for all QoI"; **XMA gives the most accurate prediction for 3 of the 4 quantities**, including three not used for training; **for skin friction XMA is worse than k-omega** but "still more accurate than all the other component models". Both the big-data (40,080 points) and scarce-data (820 points) variants improve results.
3. **`FLAG F5` — the structural failure mode, which is the transferable finding (arXiv preprint p. 17, verbatim)**: "In the upper part of the wake, **all models exhibit relative consensus on the wrong solution, a known limitation inherent to mixture models.** In such a case, the variances (a measure of model consensus) are also small and **do not encompass the reference** either." *A convex combination is confined to the convex hull of its components. When every component is wrong in the same direction, the aggregate is wrong and confident. This is a provable property of the method, not a tuning failure, and it is the exact analogue of Xiao et al. 2016's finding (Category D) that the true stress orientation lies outside the assumed uncertainty space.*
4. **The predictive variance is explicitly NOT a credible interval (arXiv preprint Eq. 13, p. 8, and p. 19, verbatim)**: `Var[delta(eta*)] = sum_m w_m (delta^(m) - E[delta])^2` measures **inter-model consensus** only — "**the error bars must not be interpreted as the region where the true solution possibly lies, but simply as a measure of the uncertainty in the choice of a best-performing model.**"
5. **The weights themselves are a diagnostic (arXiv preprint pp. 20-22)**: all four models converge to the uniform weight **1/4** in the potential-flow region — as they should, since all four agree there and the choice is immaterial. k-epsilon is systematically assigned the lowest weight near the blade and in the wake. **On the S1 extrapolation the weights are "less sharp ... i.e. the models are weighted more uniformly"** (p. 22) — which the authors flag as an explicit warning signal to the user that the prediction is extrapolating. *A method whose own weights announce when it is out of distribution.*
6. **Hyper-parameters (exact, arXiv preprint pp. 9-10)**: random forests (scikit-learn), **300 trees**, remaining three hyper-parameters by grid search with **K-fold, `K = 10`**; **one RF per component model, so 4 regressors**. The EWA learning rate `sigma` chosen by grid search, and "`sigma` has little influence on the model accuracy, provided the order of magnitude is correct". **A clipping guard**: an empirical lower bound `C` on the cost functions — **if all `g_m < C` at a point, the weights revert to uniform `1/4`** — with sensitivity showing no significant influence for `C in [0.001, 0.15]`; **`C = 0.001` retained**.
7. **Features (Table 1, p. 11)**: **10 features**, a subset of Ling & Templeton's — normalised Q-criterion, turbulence intensity, turbulent Reynolds number, streamline pressure gradient, turbulent-to-mean-strain time-scale ratio, viscosity ratio, pressure-normal-to-shear-stress ratio, velocity/velocity-gradient non-orthogonality marker, convection-to-production ratio of `k`, and total-to-normal Reynolds-stress ratio. **Each model's weight uses features computed from that model's own solution**, `w_m = w_m(eta^(m))`. **Spalart-Allmaras has no `k`, so "the feature is simply excluded from considerations"** (p. 10) — a per-model feature set, which is unusual and worth noting.
8. **Data volumes (arXiv preprint pp. 13-14, 20)**: "big data" = **40,080 points** (all mesh nodes, one scenario); "small data" = **820 points** (1 node in 8 in each mesh direction). Multi-scenario training on {S2,S3,S4}: **120,240** and **2,460**. The observed quantity that informs the weights is **total pressure only** — "the total pressure is the most informative quantity" (p. 13). Key finding: "**XMA_1 and XMA_2 lead to similar MSE on average, showing that the scarce data regime is already sufficient to properly inform the mixture**" (p. 23). *820 points from one scenario is enough. That is a cheap-instrumentation result.*

**Stated limitations (authors' own words, arXiv preprint)**

- p. 17: "**all models exhibit relative consensus on the wrong solution, a known limitation inherent to mixture models.**"
- p. 19: "**the error bars must not be interpreted as the region where the true solution possibly lies.**"
- p. 13: "**we considered instead synthetic data sets generated through the reference EARSM k-kL model**" (the DNS/LES access problem, quoted in full above).
- p. 14: "The data are uniformly distributed across the grid, and **no attempt was made to use optimal sensor placement (OSP) techniques or prior physical knowledge on the flow** ... Further research on optimal sensor placement is warranted."
- p. 20: "For the skin friction, XMA performs worse than k-omega, but is still more accurate than all the other component models. **The results could be improved in the future by improving the selection and placement of training data.**"
- p. 25: "The present XMA relies on '**on the shelf**' component turbulence models, **not specifically calibrated** for the configuration of interest."
- p. 10, on the per-model feature set: "some turbulence models, e.g. the Spalart-Allmaras model ..., do not provide estimates of the turbulent kinetic energy `k`. In such cases, the feature is simply excluded from considerations."
- p. 17-18, on scarce data: XMA_2 "**discriminates less well** well-performing from bad-performing models", giving larger variances — but "still provides improved performance overall ... **XMA prevents catastrophic loss of accuracy** with respect to the common-practice choice of a single (possibly wrong) RANS model."

**What it cannot see**

- **`FLAG F5`: there is no MSE table. One number ("approximately 1/3", velocity, S1) exists in the whole paper.** Figs. 8 and 13 are normalised bar charts. Per-QoI reductions cannot be quoted.
- **`FLAG F5`: the reference is a fifth RANS model, not DNS or LES.** Every "accuracy" statement means agreement with EARSM k-kL. The paper is a proof of concept for the *machinery*, and the authors say so. **A reproduction on real DNS/LES truth would be a genuinely different experiment, and this lab has that truth on disk** — see `_common/FEASIBILITY.md` §1.2, which rates the required 4-model solve sweep at ~50 core-hours and notes it is independently useful as an extension of `BASELINES.md`.
- **No a-posteriori stability question exists.** This is post-processing of converged steady solutions; there is no time integration, no divergence, no rollout. The only "clipping" analogue is the `C = 0.001` cost-function floor.
- **One geometry, four scenarios, one Reynolds number band (`Re_1` 289K-302K).** The extrapolation axis is incidence angle only.
- **No compute cost of any kind.** No CPU-hours, no RF training time, no CFD wall-clock. The optimised RF hyper-parameters and the chosen `sigma` are also not stated.
- **The method cannot outperform its best component where that component is wrong.** Item 3 is the formal statement; a corollary is that adding a *fifth, better* model would help more than any improvement to the weighting.

---

### Edeling, Cinnella & Dwight 2014 — Bayesian model-scenario averaging `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: *Predictive RANS simulations via Bayesian model-scenario averaging*, J. Comput. Phys. 275:65-91. The quarantined file is arXiv:1406.3360, a cosmology paper. **No numeric claim is made here.** `MANIFEST.md` files it under shelf **H**, and that is the right place: it is the **scenario-averaging** ancestor of de Zordo-Banliat's space-dependent aggregation, and de Zordo-Banliat positions XMA against exactly this lineage (BMA/BMSA weight by posterior model probabilities and "assign the same BMA weights ... throughout the spatial domain", arXiv preprint pp. 3-4). Its scenario set is boundary-layer experiments (the Coles-Wadcock / Clauser families), **which are also not on disk** — `_common/FEASIBILITY.md` §1.2 records it as blocked on both source and data.

---

## Category R — Reviews and perspectives

`Spalart2000_strategies_turbulence_modelling.pdf` is the fifth review in the corpus and is
catalogued **above under Category A** (codes A primary / R secondary), because its content is the
statement of the problem the other four review. Read in sequence, the four below are a **twenty-year
argument that converges on one conclusion**: an ML closure must be trained in the environment it
will be run in.

---

### `Duraisamy2019_turbulence_age_data.pdf`

- **Category**: R (primary), D (secondary — §4 is a UQ review).
- **Version**: **arXiv preprint 1804.00183v3**, 23 pp. Journal: *Annu. Rev. Fluid Mech.* 51:357-377. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: A review organised around **a hierarchy of modelling assumptions L1-L4** and a parallel **hierarchy of data usage**, arguing that data-driven work must be located precisely in both before it can be assessed.
- **Data used / cases / metric**: none. This is a taxonomy paper.

**Headline content**

1. **The L1-L4 hierarchy (§2, arXiv preprint pp. 3-4)** — the taxonomy this catalogue's categories map onto:
   - **L1**: uncertainties introduced by ensemble averaging itself, `<N(.)> != N(<.>)` (Eq. 1). "**fundamentally irrecoverable.**"
   - **L2**: the model *representation* relating macroscopic to microscopic state, `<N(.)> = N(<.>) + M(.)` with `M(.) = div tau` (Eqs. 2-3). "**Linear eddy viscosity models and algebraic stress models are examples of L2-level assumptions.**"
   - **L3**: the specific functional form `P(.)` inside the model (Eq. 4).
   - **L4**: the coefficients `c` (Eq. 5). "The choice of the `C_mu` coefficient in two-equation linear eddy viscosity models is a classical **L4** closure issue."
   *Mapping this catalogue onto it: Categories A and B change L2; SpaRTA and GEP change L3; field inversion (C) changes L3 via a spatial multiplier; classical calibration and Menter's hand-tuning change L4; and nothing in the corpus touches L1, which is by construction untouchable.*
2. **The data-usage hierarchy (§3, pp. 5-7)**: naive calibration `M = M(w; P(w); c_q)` (Eq. 7) -> statistical inference `M = M(w; P(w); c_theta) + delta + eps_theta` (Eq. 8) -> data-driven modelling `M = M(w; P(w); c(theta); delta(theta, eta); eps_theta)` (Eq. 9). The review restricts itself explicitly: "**In the present review, we focus on methods that embed the calibration inside the model**" (p. 8). Final recommended form (Eq. 13, p. 19) adds a learned functional form `P(w; theta)`, "**and we recommend the resulting predictions to be accompanied by explicit uncertainty estimates `q = M + eps_q`.**"
3. **`FLAG`-relevant — the data-model consistency passage, which is the single most cited paragraph in this corpus (§6, p. 18, verbatim)**: "**How to enforce data-model consistency?** If machine learning is applied directly on a dataset, a compounding problem is the consistency between the data and the models, i.e. **the difference between the learning environment (DNS) and the injection environment (RANS)**. It is well known that **even if DNS-computed quantities are used to completely replace specific terms in the RANS closure, the overall predictions will remain unsatisfactory** (Poroseva et al. 2016; Thompson et al. 2016) due to the assumptions and approximations at various levels in models, **compounded by the potential ill conditioning of the RANS equations (Wu et al. 2018c)**. Furthermore, **scale-providing variables such as the turbulent dissipation rate will be very different in the RANS and DNS context.** The addition of the inference step before the learning phase enforces consistency between the learning and prediction environment."
   *The "Wu et al. 2018c" reference is arXiv:1803.05581 — which is now on disk and catalogued under Category D, where its Table 1 supplies the numbers this sentence asserts.*
4. **Invariance guidance (arXiv preprint pp. 7, 15-16)**: "constraints such as symmetry properties or Galilean invariance **can be enforced in the definition of the candidate features**"; "An important aspect ... is to ensure the **objectivity and the rotational invariance** of the learned Reynolds stress models"; and the note that both **Euler angles and unit quaternions** have been used for stress orientation. On Ling et al.: their architecture learns the coefficients "with good predictive capability but **no explicit expression for the resulting model** (i.e. any stress evaluation requires the use of the original, calibrated neural network)."
5. **Non-locality is named as the open axis (p. 16)**: "These approaches only use **local** quantities to construct the set of features. In general, further work based on modeling **non-local, non-equilibrium** effects can expand the predictive capabilities ... Hamlington and Dahm (2008) used variables that account for non-local behavior through **streamline integration**, which provided an inspiring approach for choosing features."
6. **Realisability as the basis of UQ (§4.1, pp. 8-10)**: Eq. 10 gives the eigen-perturbation form `tau = tau^RANS + delta_tau = 2k(I/3 + V Lambda V^T)` with `Lambda = Lambda^RANS + delta_lambda`. The honest caveat (p. 9): "**In contrast to the strong constraint imposed by the realizability on the eigenvalues, the constraint on the turbulent kinetic energy is rather weak** - it only has to be pointwise non-negative. Furthermore, **the realizability condition does not give clear bounds on the eigenvectors.**" And on bounding generally (p. 8): "**it is difficult to envision that formal bounds can be derived for flow problems of practical engineering interest.**"
7. **Detection of model failure (§4.3, p. 11)**: marker functions (Gorlé et al.) and ML classifiers (Ling & Templeton) can flag where assumptions are violated, but "**Although these studies are useful to illustrate the failure of turbulence models there is no straightforward way to use the results for improving predictions.**"
8. **The five open questions (§6, pp. 17-19)**: (1) What data to use? — with a call for "formal **design-of-experiments** to drive further data-collection activities". (2) How to enforce data-model consistency? (item 3). (3) What to learn? — "**how many features are required? And what is the optimal choice** for broad application ...? These remain open questions". (4) What is the confidence in the predictions? — "The use of deep learning strategies and vast amount of data in the inference process **exacerbates this issue**." (5) What is the right balance between data and models? — "the possibility of discovering unknown equations and deriving accurate predictive models **purely from data remains an open question**." Plus the warning (p. 19): "**relying on machine learning alone, when dealing with large but finite amount of data, problem-specific/spurious laws might be discovered, resulting in very limited predictive value.**"

**What it cannot see**

- **This paper contains essentially no numbers.** A scan for percentages, Reynolds numbers, cost factors and cost-scaling exponents returns nothing in the body text. The only numerals of substance are structural: the 10-term tensor basis, the four L-layers, and the 1C/2C/3C realisability limit states. **DNS/LES/RANS cost-scaling exponents are not stated.**
- **It never uses the terms "a priori training" and "a posteriori training"** — it says "learning environment" and "injection environment". The vocabulary the rest of the field adopted comes from Duraisamy 2021 and Sanderse 2024.
- **It never says a coupled learned closure is *unstable* or *diverges*.** Its strongest word is "unsatisfactory", plus "potential ill conditioning". The instability claim enters the literature with Beck & Kurz 2021 and Sanderse 2024.
- **No solver-in-the-loop, no differentiable solver, no adjoint-based training** appears anywhere; nor does Mori-Zwanzig, energy conservation as a constraint, or any named out-of-distribution detector.
- **arXiv p. 11 is badly garbled in text extraction** — §4.3's sentences are interleaved line-by-line with an embedded figure. Quotations from that page were recovered by reading, and should be re-checked against the PDF before being quoted onward.

---

### `Duraisamy2021_perspectives_ml.pdf`

- **Category**: R (primary). Secondary: C — its Eqs. 7-9 are the formal definition of the FIML family, which the corpus otherwise cannot read (Category C is `BLOCKED-ON-SOURCE` at its foundation).
- **Version**: **arXiv preprint 2009.10675v3**, 25 pp. Journal: *Phys. Rev. Fluids* 6:050504. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: A two-axis perspective — **what is represented** (§III) crossed with **how it is trained** (§IV) — whose thesis, stated in the abstract, is that "**truly generalizable models require model-consistent training**".
- **Data used / cases / metric**: none.

**Headline content**

1. **`FLAG`-relevant — the training taxonomy, with equations (§IV, arXiv preprint pp. 8-13).** This is the definitional passage the whole field now cites:
   - **A-priori training**: `min_w L[delta, delta_m(eta; w)]` (Eq. 5), then embed: `R_a(q_m, s_m, delta_m(eta_m; w)) = 0` (Eq. 6).
   - **Field inversion**: `min_{delta_m^i} L[Y^i, Y_m^i(delta_m^i)]` **subject to** `R_a(...) = 0` (Eq. 7); then regress the inferred field: `min_w L[delta*_m, delta_m(eta*_m; w)]` (Eq. 8).
   - **Fully integrated / tightly coupled**: `min_w L[Y, Y_m(delta(eta_m; w))]` **subject to** `R_a(...) = 0` (Eq. 9) — one optimisation, the ML output fed into the model and the model output into the loss.
2. **The a-priori indictment, in three named mechanisms (arXiv preprint pp. 9-11).** The framing sentence (p. 9): "**a priori training establishes the consistency of the ML model with the DNS field, but does not guarantee consistency with the RANS or LES environment.**"
   - **Feature mismatch (p. 9)**: "During the training process, the coarse-grained features `eta` **from the DNS** are used as inputs ..., whereas in the prediction process, coarse-grained **model** features `eta_m` are used. Thus, for this approach to work well, the model has to predict the features `eta_m` very accurately ... **This is typically difficult to achieve** ... For instance, a feature `S k/eps` may not equal `S_m k_m/eps_m` because `k_m, eps_m` can be very different from `k, eps` even if `S_m` is close to `S`."
   - **Error accumulation (p. 10)**: "The neural network is trained (offline) to represent `u(t) = f_NN(u_bar(t); w)`, whereas when it is embedded in the solver, it predicts `f_NN(u_bar(t) + e(t); w)`. **As the error `e(t)` accumulates over time, the neural network is required to make predictions based on a field that is corrupted by error, which becomes futile** ... Such errors are typical of most practical LES computations because even though one attempts to model only the unresolved scales, **the scales that are barely larger than the filter size are often very poorly resolved.**"
   - **Balance between model terms (pp. 10-11), the strongest sentence in the paper**: "**It is well-recognized in the turbulence modeling community that successful a priori evaluation is neither a necessary (e.g. Smagorinsky model) nor a sufficient condition for successful predictive models.** ... [Raiesi et al.] concluded that **the use of exact values of the turbulent kinetic energy and dissipation rate in the modeled eddy-viscosity did not improve its performance.** Ref. [Thompson et al.] showed that **even substituting Reynolds stress fields from reputable DNS databases may not lead to satisfactory velocity fields.** Further, [Wu et al.] investigated potential conditioning problems that arise when explicitly trained ML models are injected into existing turbulence models."
   *Every one of those three references is now readable in this corpus: the Thompson result is Table 1 of `Wu2018_rans_explicit_closure_ill_conditioned.pdf` (Category D), and the conditioning paper is that same file.*
   Plus the practical constraint (p. 11): "**a full field of DNS data is required to train the model. Since DNS data will not be available in practical regimes, this is a major limitation.**"
3. **The recommended diagnostic, which is cheap and which nobody in the corpus runs (arXiv preprint p. 11, verbatim)**: "**For the purposes of generalization, it will be a good practice to ascertain the correlations between `eta` & `eta_m` (beyond `delta` & `delta_m`) such that the degree of loss in consistency can be monitored.**" *Correlate the DNS-derived features against the RANS-derived features, not just the targets. That is a one-line addition to any a-priori study and it directly measures the feature-mismatch mechanism of item 2.*
4. **What integrated training buys and costs (arXiv preprint p. 12)**: it "**ensures full consistency between the learning and prediction environments**", but "**model-consistent training involves large scale inverse problems, typically necessitating the use of adjoint-driven optimization** ... Given the **intrusive nature of adjoints**, this presents major challenges to development, and **has proven to be a barrier for researchers**." Trade-off: "one minor drawback of the integrated approach is that **features have to be selected before the inference**, whereas separation of the FI and ML stages yields more flexibility." Weakly coupled alternatives named (p. 13): "embedded learning", "iterative machine learning", "CFD-driven machine learning", "closed loop training".
5. **Feature-selection guidance, four rules (§V, arXiv preprint pp. 13-15)**: **local non-dimensionalisation** ("`S k/eps` ... offers a greater possibility to generalize across different configurations, when compared to global non-dimensionalization"); **invariance** ("ideal features should satisfy **rotational, reflectional and frame-invariance** properties. **This should apply to both the selected features and variables used for local non-dimensionalization**"); **local vs non-local** ("**Pressure-gradient-based features have also been used as a surrogate for non-local information**", and wall-distance and wall-stress measures "appear to be important"); and **data** — "**constructing a model with `d` features requires enough data to populate a `d`-dimensional feature space**", with the caveat that a 47-feature importance ranking may itself be biased by limited data.
6. **Constraints, four kinds (§VI, p. 15)**: on the ML **input** (restrict the feature manifold to satisfy invariances); on the ML **output** ("**realizability constraints could be enforced on `delta`**", and reflectional/rotational invariance "can be addressed - for instance - via data-augmentation"); on **observables of the physics model** (e.g. matching an integrated heat release even when local heat release is not in the loss); and **via Bayesian priors**. Framing: "The imposition of constraints can effectively **reduce the search space of ML models to lower dimensional manifolds consistent with the physics.**"
7. **The state-of-the-field verdict (arXiv preprint p. 18)**: "Several researchers have shown that ML-augmented modeling can offer improved predictions over classical models in problems that were either **part of the training dataset or in problems that are related to the training set** (e.g. an airfoil with a slightly different shape ...). **The goal of more generalizable models has, however, not been achieved.**" And the author's own stance (p. 17): "**ML-augmentation should be considered as just another tool in turbulence modeling.**"
8. **Identifiability, stated as a result (arXiv preprint p. 16)**: "A model-consistent perturbation to the Reynolds stress anisotropy tensor based on the mean velocity was found to yield **highly accurate mean velocity and Reynolds shear stress predictions, but the anisotropy was not predicted accurately.** This could indeed be remedied if the entire Reynolds stress tensor was used as the data." *The same identifiability limit Stroefer & Xiao 2021 hit in the duct (Category G).*

**What it cannot see**

- **No numbers.** No error percentages, no Reynolds numbers, no speed-up factors, no cost-scaling exponents. The only numerals are structural (47 features, 5 invariants, 10 basis tensors, `t* = 6.0` as the time a super-resolution prediction loses fine-scale structure).
- **It does not claim coupled learned closures blow up.** The instability it names is of the *adjoint*: "**chaoticity can lead to unstable adjoint solutions that require special treatment**" (p. 13). Forward-model divergence is described as error accumulation becoming "futile", not as blow-up.
- **Mori-Zwanzig appears only as a citation** (ref. [80] in a parenthesis about Markovian closures), with no discussion.
- **No named out-of-distribution detector** — only the feature-correlation monitoring of item 3.
- **No realisability guarantee or boundedness proof**, no energy-conservation constraint, no structure-preserving discretisation.

---

### `Beck2021_perspective_ml.pdf`

- **Category**: R (primary), E (secondary — its worked examples are LES closures).
- **Version**: **arXiv preprint 2010.12226v1** (Oct 2020), 37 pp. Journal: *GAMM-Mitteilungen* 44:e202100002. **All locations below are arXiv preprint page numbers.**
- **Method (one line)**: A perspective organised on **two orthogonal axes** — the *level* at which modelling occurs (parameter estimation / closure-term estimation / full-PDE modelling, §3, p. 23) and *what error is minimised* (Eq. 6, p. 8) — whose stated thesis is that "**consistency of the training data, the model, the underlying physics and the discretization is a key issue**".
- **Data used / cases / metric**: none of its own; it reports results from the authors' group and others.

**Headline content**

1. **`FLAG F19`-defining — the strongest a-priori/a-posteriori evidence in the corpus, and it is quantified (arXiv preprint pp. 25-26, verbatim)**: "For all filter types investigated, **the GRU networks were able to achieve 99.9% cross correlation in a priori tests** ... making the prediction and target **visually indistinguishable** ... These results suggest that the subgrid force terms can be predicted with near arbitrary precision ... **As stated above, a direct closure with these predicted terms suffers from instability due to exponential error growth, and is thus not the method of choice without any regularization.** ... **While the GRU predictions lead to a very accurate closure and thus LES solution at first, the LES solution diverges strongly soon after. This is a result of a data-model inconsistency and the non-linear error accumulation of the truncated equations.**"
   **A 99.9% a-priori correlation and a divergent simulation, in the same model.** Compare Guan 2022's Table 2 (Category E), where the stability threshold sits between correlations of 0.90 and 0.92 on a different flow with a different architecture — **the two results together say the threshold is not a universal number and cannot be read off an a-priori score.**
2. **The mechanism, generalised (arXiv preprint p. 25)**: instability "**stems from the unavoidable data-model inconsistency during inference as well as the error accumulation and self-driving error growth at high wavenumbers.** This can either be tackled by **removal of this energy through a dissipative mechanism** (essentially an additional model term) or **the projection of the closure term onto a stable basis with the desired properties**." *The second remedy cites Beck, Flad & Munz 2019 — i.e. the eddy-viscosity projection catalogued under Category E, whose limiter is `mu in [-mu_0, 20 mu_0]`.* Summary (p. 26): "direct estimation of the subgrid forces has a range of advantages over parameter estimation approaches. **However, without additional modeling or stabilization, it can lead to a diverging system in the long run.**"
3. **A comparator with numbers (arXiv preprint p. 25)**: a spatial MLP with "**approx. 500,000 parameters**" predicting the three subgrid-force components reports "**a priori correlations of over 90%** with the true subgrid force" and, "**In an a posteriori application of the subgrid force together with a dissipative regularization term their approach outperforms classical closure models.**" *Again: the a-posteriori success is contingent on the added regulariser, not on the correlation.*
4. **The remedy this paper advocates is neither solver-in-the-loop nor clipping — it is stability training (arXiv preprint p. 26, Fig. 11 caption p. 28)**: "**so-called stability training was used successfully to flatten the cost function to reduce its sensitivity to uncertainties in the inputs during inference. This results in much greater stability of the closure model and longer useful predictions.**" Mechanically: "random perturbations `Delta x` are applied to the input features. **An additional penalty term is then added to the loss function, which is proportional to the induced changes in the loss function**", preferring shallow minima to sharp ones. **Note: the terms "solver-in-the-loop", "differentiable solver", "adjoint" and "end-to-end" do not appear anywhere in this paper.** It is an October 2020 preprint and predates the consolidation.
5. **The training-inference consistency argument, with the subtlest point in the corpus (arXiv preprint pp. 10-11, verbatim)**: "**Even if the model predictions themselves are stable against disturbed inputs, their overall effect can be troublesome. For example, if the ML model predicts parameters in a closure model and the predictions themselves are reasonable and within range, the term the parameters are applied to can diverge from the training situation** (e.g. a velocity gradient from training (DNS data) [may] become vastly different from the one during prediction (RANS/LES solution))." *A perfectly bounded, perfectly sensible parameter prediction multiplying a diverged operand.*
6. **"Inclusive optimization" (arXiv preprint p. 11, verbatim)**: "**closure models must be considered on the level of the system of equations to be solved, not on a more fine-grained level** ... **just improving the prediction of certain effects or terms does not necessarily lead to better models. It is instead the interplay of the different terms that must be considered.**" The cited example is Larsson et al. 2016 — the wall-model review in Category F, whose "models that respect the overall balance of the physical effects have been shown to be superior".
7. **The one-to-many argument (arXiv preprint p. 25)**: "**For a given filter and thus coarse grained solution, an infinite number of associated fine scale fields and closure terms exist - thus, even exact closure terms should only be considered as means of the ensemble.**" *A deterministic regression is fitting the conditional mean of a one-to-many map, whether or not it says so.*
8. **The OOD recommendation, which is the most concrete in the corpus (arXiv preprint pp. 11-12, verbatim)**: "**a consistent fallback mechanism** in cases where the model is likely to fail. Even before that, **a means of measuring confidence in the model prediction should accompany any model - in its simplest form, this could be an estimate of the position of the input data in feature space and a comparison against the statistics gathered during training.** ... **The simplest case of generalization capability of an ML-augmented model should be at both limits of modeling: it should turn off in laminar flow and at the DNS resolution.**" *Two free asymptotic tests and a distance-in-feature-space confidence score. Lozano-Duran & Bae 2023 implement exactly the latter (`p_conf`, Category F) and report that it can be low while the answer is right and high while it is wrong.*
9. **Constraints are soft, and that is stated as a limitation (arXiv preprint p. 11)**: selecting training samples that share a property "**is not guaranteed during inference or for extrapolated inputs**"; adding the constraint to the loss "usually leads to increased stability of the model, but **again does not enforce the fulfillment of the constraint**"; and "**the relative importance of the respective constraints and the best way to enforce them remains an open challenge - not just for ML-based methods.**"
10. **The numbers this review does supply (arXiv preprint)**: DNS degrees-of-freedom scaling **`N ~ n_ppw^4 Re^3`** (Eq. 3, p. 4); the airfoil example is **NACA 64418, `Re_c = 1e6`, `Ma = 0.2`** (pp. 5-6); a learned eddy viscosity gives "a **saving in computational time by a factor of 2 to 8** compared to an application of the dynamic Smagorinsky model" (p. 24); PINN network sizes reach "**approx. 9 x 300^2 ~ 800,000** learnable parameters" (p. 28); and the cost-benefit rule (p. 14): "**if the costs of providing enough samples to lead to a converged ML model are orders of magnitude larger than using established no-ML models in the first place, there is no justification for going the ML route.**"
11. **The community call (arXiv preprint pp. 30-31)**: "**Such a database should contain a well-described training dataset, most likely from DNS, open to everyone, and a private test set for the blind evaluation of the proposed models. Setting up such a validation case and administering it should be approached as a community effort.**"

**What it cannot see**

- **No formal UQ** — no Bayesian networks, no ensembles, no posteriors. Its uncertainty content is the confidence-score recommendation of item 8 and the honest admission (p. 30) that "**ML introduces its own new level of hyperparameters, methods and uncertainties.**"
- **No Mori-Zwanzig, no memory-kernel formalism** — memory is handled architecturally (GRU/LSTM).
- **Realisability appears exactly once** (p. 11, as an example of a soft constraint).
- **No LES or RANS cost-scaling exponents** (only the DNS `Re^3` estimate). For those, Piomelli & Balaras 2002 and Larsson et al. 2016 (Category F) are the sources on disk.
- **It predates the differentiable-solver literature it would now have to engage with.** Read it alongside Sanderse 2024, which is four years later and treats a-posteriori learning as a full peer of a-priori.
- **No named OOD-detection algorithm** — the feature-space-position heuristic is a proposal, not a method.

---

### `Sanderse2024_ML_closure_models.pdf`

- **Category**: R (primary). Secondary: G — it is the review that defines the a-posteriori/solver-in-the-loop family and names its six synonyms.
- **Version**: **arXiv preprint 2403.02913v2**, 32 pp. **No journal version is recorded. All locations below are arXiv preprint page numbers.**
- **Method (one line)**: A review on **two orthogonal axes**, stated in the abstract: "**the different reduced model forms, distinguished by the degree to which they include known physics, and the different objectives of a priori and a posteriori learning**" — plus three further axes (discretisation, §5; physics constraints, §4; non-locality and Mori-Zwanzig, §7).
- **Data used / cases / metric**: none.

**Headline content**

1. **The reduced-model-form ladder (§2, arXiv preprint pp. 2-5)**, by decreasing known physics: full model -> **commutator error** `C(u, u_bar; mu) = F_bar(u; mu) - F(u_bar; mu)` (Eqs. 6-7) -> **closure form** `m_theta(v_bar) ~ C` added to the known operator (Eqs. 8-11) -> **generic evolution form** `G_theta = dv/dt + m_theta(v_bar)` ("fully learned", Eq. 12) -> **surrogate form** (DeepONet, FNO, LNO, GNO, CNO; Eq. 13). LES is the instantiation (§2.4, p. 5), with the caution that "even though the Reynolds-averaged Navier-Stokes equations (RANS) have a similar form, they feature a different reduction operator that leads to a **much larger commutator error**, and it should not be confused with LES."
2. **The a-priori/a-posteriori definitions, as equations (§3, arXiv preprint pp. 5-8)**: a-priori `L^prio = ||m_theta(u_bar; mu) - C(u, u_bar; mu)||^2` (Eq. 21) or generally `||G_theta(u_bar) - F_bar(u)||^2` (Eq. 22), with aliases "'direct approach', or 'offline mode'". A-posteriori `L^post` (Eq. 24) in two branches — **residual minimisation** `||G_theta(v_bar) - F_bar(u)||^2` or **solution-error minimisation** `||v_bar_theta - u_bar||^2`.
3. **`FLAG F19` — the a-priori failure mode, stated as a general law with its remedies enumerated (arXiv preprint p. 6, verbatim)**: "**A common problem is that even with a highly accurate operator fit, the solution `v_bar` can drift from the true solution `u_bar` or becomes unstable.** The issue is also known under the term **model-data inconsistency**, where the data used to train the closure models is not consistent with the environment in which the model will be run, e.g., due to discretization effects." And the mechanism: "**In turbulence, the instability is often associated with the concept of backscatter: energy transfer from the small scales back to the large scales.**"
   **The paper then lists, in one paragraph (p. 6), every stabiliser this catalogue has recorded independently** — and the mapping is exact:
   | Sanderse's remedy | Where this catalogue records it |
   |---|---|
   | "[58] reported unstable results and applied **clipping to limit backscatter**" | Maulik 2019, Eq. 2.4: half of all predictions zeroed (Category E) |
   | "**Beck et al. performed a projection of their neural-network closure model onto an eddy viscosity basis** to enforce stability" | Beck 2019, Eq. 4.2, limiter `[-mu_0, 20 mu_0]` (Category E) |
   | "**Kurz et al. performed 'stability training' by adding noise** to the training data" | Beck & Kurz 2021, Fig. 11 (this section) |
   | "**Rasp et al. proposed coupled online learning** in which the model is corrected by nudging with a high-fidelity model run in parallel" | §3.4, p. 9 |
   | "**Yuval et al. address the stability issue by employing random forests, which automatically respect energy conservation**" | Kaandorp 2020: "never observed unrealizable predictions from TBRF" (Category B) |
   | "**Guan et al. showed that increasing the size of the training set can give stable results**" | Guan 2022, Table 2: `n_tr` 10,000 unphysical -> 30,000 stable (Category E) |
   And the summary verdict (p. 7): "the main advantages of the a priori approach are the **relative ease of training (no differentiable solvers needed)** and the prospect of generalization and interpretability ... **However, the main disadvantage is that the solution of the reduced model is not part of the error metric, so that instability and drift can lead to inaccurate solutions.**"
4. **The a-posteriori family, with all its names (arXiv preprint pp. 7-8, verbatim)**: "**the approach is known under various other names, such as 'solver-in-the-loop', 'curriculum training', 'indirect approach', 'end-to-end learning', 'differentiable physics', and 'online learning'.**" Its cost: "**This makes the optimization problem more difficult to solve, and differentiable solvers are typically needed** ... **this requires that the code that solves `G_theta = 0` is differentiable, or that an adjoint solver is available.**" Its verdict (p. 8): "the main advantage ... is that one **directly targets the accurate approximation of `u_bar`** ... **This has been shown to improve stability compared to a priori learning.** ... **The approach implicitly corrects for spatial and/or temporal discretization errors, which can be desirable but can also limit application to different grids or time steps.**"
5. **`FLAG F7` — the unrolling trade-off, stated as the field's open question (arXiv preprint p. 8, verbatim)**: "**how many time steps are 'unrolled' in evaluating and back-propagating the loss function. Unrolling too few time steps gives only limited gains over a priori learning, while unrolling too many time steps is computationally expensive, has the danger of exploding or vanishing gradients, and can be unrealistic given that turbulent flows are chaotic, meaning that initially close trajectories are expected to diverge.** One strategy is to unroll predictions for a small number of the time steps and then only back-propagate to the last time step; this is called the **pushforward method**."
   *List et al. 2022 (Category G) measured exactly this: full 60-step back-propagation is training-unstable, the optimum sub-range is 20-30 steps, and the saturation point coincides with one integral timescale.*
6. **An escape from differentiability (arXiv preprint §6.1, pp. 15-16)**: "derivative-free optimization of neural network parameters (i.e., without back-propagation) has been achieved by means of a **modified ensemble Kalman filter and ensemble Kalman inversion**. **This can potentially mitigate the need for differentiable solvers in a posteriori learning.**" *This is the route Xiao et al. 2016 take for a UQ purpose (Category D), and it is the one route by which a non-differentiable model — a random forest, say, per Wu et al.'s objection in Category D — could still be trained a-posteriori.*
7. **Hard versus soft constraints, and why it matters for extrapolation (§4, arXiv preprint pp. 10-12)**: soft constraints (data augmentation, loss penalties) "are typically easier to construct"; **hard constraints "can guarantee constraint satisfaction during interpolation as well as extrapolation"** but require architecture design. TBNN is given as the exemplar (Eq. 29, pp. 11-12): "**by choosing the form (29), one has directly encoded the Galilean, rotational, and reflectional invariances of the stress tensor, independent of the neural network architecture or its parameters.**" *Note this attributes **reflectional** invariance to the Pope-basis form — which Wu 2018 explicitly disclaims for its own quaternion-output formulation (Category B). The two statements are about different outputs and both can hold; record the distinction.*
   The energy-conserving construction is named (p. 12): "**introduces an additional set of latent variables and specifies an explicit form of the closure (a combination of skew-symmetric and dissipative terms) to guarantee energy conservation and stability of the closure.**" And random forests are explained as structure-preserving (p. 12): "**random-forest predictions are obtained by averaging splits of data that come from the convex hull of the training data set. As long as the generated training data sets guarantee a particular symmetry or structure, the prediction of the dependent variable will also satisfy this property by design.**" *That is the mechanism behind Kaandorp's never-unrealisable TBRF.* With the caveat: "**for complicated properties that emerge from complex interactions between machine learning predictions and the numerical solver, such an approach may be incomplete.**"
8. **`FLAG`-worthy contrarian finding (§9.2, arXiv preprint p. 20, verbatim)**: "It is generally acknowledged that including known physics in data-driven methods is beneficial ... **However, the evidence that supports this claim is still rather thin, and some studies are pointing in the reverse direction. Restricting the reduced models to have a closure form or a particular known symmetry was limiting their performance in these cases.**" *Kochkov et al. 2021 report exactly this: "We also explored LC models restricted to take the form of classical closure models ..., but the restrictions hurt model performance and stability" (Category G, arXiv preprint p. 3). **This is a live disagreement in the corpus and the catalogue should not resolve it.***
9. **Mori-Zwanzig, the only formal treatment in the corpus (§7.1, arXiv preprint pp. 17-18)**: Liouville operator (Eq. 42), the MZ identity (Eq. 43) and Dyson's formula (Eq. 44), decomposing the closure into a **Markovian** term, a **noise** term, and a **memory** term. "**The MZ formalism is based on an exact reformulation of the original system and though almost never used in its full generality, it is a good starting point for approximations** ... it is able to address cases with **very short, moderate, or very long memories.**" Stability: "**except for special cases, it is difficult to guarantee the stability of reduced order models. A renormalized version of the MZ formalism has been introduced ..., which has allowed the stabilization of such models.**"
10. **Stability of hybrid models, stated as an open problem (§9.3, arXiv preprint p. 20, verbatim)**: "**The often black-box nature of the neural network component can hinder the study of stability properties of the hybrid model, and, even worse, can amplify the risk of catastrophic instabilities.** The problem of instabilities for coupled models has long been known and is not specific to the use of neural network closures. For neural network-based closures, **possible overfitting of the training data can exacerbate the instability problem.** Approaches like a posteriori learning ... **have shown promise. However, thorough investigation of the stability properties of such approaches is still an active research topic.**"
11. **The generalisation verdict (§9.1, p. 20)**: training for one parameter set and using it beyond "could be seen as the '**holy grail**' in closure modeling research. **However, this is currently out of reach in its generality.**" And on distribution shift (§9.5, p. 21): "**many data-driven methods ... are limited by errors resulting from distribution shifting when deployed on test data that is significantly different from the training data. Learning useful 'invariant' input features may assist with this but that is as yet a largely unsolved problem in machine learning.**"
12. **The benchmarking demand, which this lab should read as a specification (§9.5, arXiv preprint p. 21)**: "many papers consider **simplified PDE problems** as test cases, such as the Burgers' equation, the Kuramoto-Sivashinsky equation, the Lorenz '96 equations, or the incompressible Navier-Stokes equations on periodic domains with **low Reynolds numbers** ... **well-defined benchmarks, documented datasets, and relevant error metrics are of utmost importance.**" Plus the fair-comparison rule: "Researchers might be tempted to compare a neural-PDE solver against a classical PDE solver that is significantly more accurate and more expensive ... **a fair comparison should involve a Pareto front analysis.**"

**What it cannot see**

- **No quantitative result of any kind.** A full scan for percentages, Reynolds numbers, error magnitudes, speed-up factors and cost exponents returns nothing in the body. The only numerals are structural (10 basis tensors, 5 invariants, `M` degrees of freedom). **DNS/LES/RANS cost-scaling exponents are not stated.**
- **The literal phrase "structure-preserving" appears only in the Acknowledgements**, as the title of a funded project; the concept is carried by §4 "Physics-constrained learning".
- **No named out-of-distribution detector.** §9.5 states the problem and calls the only proposed mitigation "largely unsolved".
- **No conditioning or condition-number analysis of the coupled RANS/LES equations** — only ill-posedness of the *learning* inverse problem (p. 15). For the coupled-equation conditioning, the on-disk source is Category D's `Wu2018_rans_explicit_closure_ill_conditioned.pdf`.
- **No wall modelling** — Category F has no counterpart in this review.
- **It deliberately declines to recommend a training paradigm.** A-priori and a-posteriori are presented with symmetric advantage/disadvantage summaries. **Where Duraisamy 2021 says model-consistent training is required, Sanderse et al. say the two approaches trade off.** Record the disagreement.

---

## Category X — Feature selection and ML methodology

---

### `Guyon2003_feature_selection.pdf`

- **Category**: X (primary). No secondary — it contains no fluid mechanics at all, and that is why it is here: every feature-set decision in Categories B, C and H is an instance of a problem this paper had already characterised.
- **Version**: **Journal of record** — *J. Mach. Learn. Res.* 3:1157-1182, 2003. Page numbers below are the printed JMLR folios and are authoritative.
- **Method (one line)**: A survey establishing the three-way taxonomy of feature selection — **wrappers**, **filters**, **embedded methods** — together with a set of constructed two-variable Gaussian counter-examples that demolish the intuition that "select the individually most predictive variables" is a good strategy.
- **Data used**: none in the fluid sense. The illustrations are constructed 2-variable Gaussians (Fig. 1, p. 1163: `m = 100` examples per class, unit standard deviation, class centres at `(-1,-1)` and `(1,1)`; Fig. 2, p. 1164 adds intra-class covariance with perpendicular standard deviation `eps = 1/10`; Fig. 3b, p. 1165 is an XOR arrangement). Table 1 (p. 1178) lists 15 public datasets with **6 to 21,578 patterns** and **8 to 30,000 variables**.
- **Cases / flows and Re**: not applicable.
- **Metric**: not applicable.

**Headline result with numbers — the content this lane actually needs**

1. **The taxonomy, verbatim (p. 1166, §4)**: "**Wrappers** utilize the learning machine of interest as a black box to score subsets of variables according to their predictive power. **Filters** select subsets of variables as a pre-processing step, independently of the chosen predictor. **Embedded methods** perform variable selection in the process of training and are usually specific to given learning machines." Subset selection "is known to be **NP-hard**". Embedded methods "**make better use of the available data by not needing to split the training data into a training and validation set**; they reach a solution faster by avoiding retraining a predictor from scratch for every variable subset investigated" (p. 1167).
2. **`FLAG F8` — THE CHECK LIST IS AT THE END OF SECTION 1, pp. 1158-1159, NOT AT THE END OF THE PAPER.** Its own caveat comes first (footnote 2, p. 1158): "**We caution the reader that this check list is heuristic. The only recommendation that is almost surely valid is to try the simplest things first.**" The ten items, abbreviated but in the authors' order:
   1. "**Do you have domain knowledge?** If yes, construct a better set of 'ad hoc' features."
   2. "**Are your features commensurate?** If no, consider normalizing them."
   3. "**Do you suspect interdependence of features?** If yes, expand your feature set by constructing conjunctive features or products of features."
   4. "**Do you need to prune the input variables?** If no, construct disjunctive features or weighted sums of features."
   5. "**Do you need to assess features individually?** If yes, use a variable ranking method; **else, do it anyway to get baseline results.**"
   6. "**Do you need a predictor?** If no, stop."
   7. "**Do you suspect your data is 'dirty'?** If yes, detect the outlier examples using the top ranking variables ...; check and/or discard them."
   8. "**Do you know what to try first?** If no, use a linear predictor. Use a forward selection method with the 'probe' method as a stopping criterion or use the `l0`-norm embedded method ... **Can you match or improve performance with a smaller subset?** If yes, try a non-linear predictor with that subset."
   9. "**Do you have new ideas, time, computational resources, and enough examples?** If yes, compare several feature selection methods ... Use linear and non-linear predictors."
   10. "**Do you want a stable solution?** If yes, sub-sample your data and redo your analysis for several 'bootstraps'."
   *Item 1 is why Wu 2018's integrity basis exists. Item 2 is why every RANS feature set normalises. Item 8 is the protocol Kaandorp's FS1/FS2/FS3 ablation implements. Item 10 is what none of the closure papers do.*
3. **The four warnings about correlated and redundant features — each a bolded standalone conclusion in the original, and each with a direct fluid analogue:**
   - **§3.1, p. 1163: "Noise reduction and consequently better class separation may be obtained by adding variables that are presumably redundant. Variables that are independently and identically distributed are not truly redundant."** Quantified: rotating two i.i.d. variables by 45 degrees gives "a separation improvement by a factor `sqrt(2)`", and "by averaging `n` i.i.d. random variables we will obtain a reduction of standard deviation by a factor of `sqrt(n)`".
   - **§3.2, p. 1164: "Perfectly correlated variables are truly redundant in the sense that no additional information is gained by adding them."**
   - **§3.2, p. 1164: "Very high variable correlation (or anti-correlation) does not mean absence of variable complementarity."**
   - **§3.3, p. 1165: "a variable that is completely useless by itself can provide a significant performance improvement when taken with others"** and "**Two variables that are useless by themselves can be useful together.**"
   *Kaandorp & Dwight found (Category B) that 3 of their 5 FS1 features "are approximately scaled versions of the other 2 - effectively reducing the input space to two dimensions", which is §3.2's first warning measured in a turbulence feature set. And their 5 -> 17 feature jump cutting RMSE 47.6% is §3.3's warning realised.*
4. **Ranking is not subset selection (p. 1158, Introduction, verbatim)**: "**Selecting the most relevant variables is usually suboptimal for building a predictor, particularly if the variables are redundant. Conversely, a subset of useful variables may exclude many redundant, but relevant, variables.**" Restated at p. 1174: "some variables may have a **low rank because they are redundant and yet be highly relevant**." **This directly qualifies every feature-importance ranking in Categories B and C** — including Wang, Wu & Xiao 2017's Fig. 11 and the 47-feature ranking Duraisamy 2021 reproduces as its Fig. 3.
5. **Correlation criteria are linear-only (p. 1161, §2.2)**: "**Correlation criteria such as `R(i)` can only detect linear dependencies between variable and target.**" The suggested fixes are a non-linear fit or non-linear preprocessing (squaring, square root, log, inverse) before correlating. And on mutual information (p. 1162, §2.4): "The difficulty is that the densities ... are all unknown and are hard to estimate from data ... **The case of continuous variables (and possibly continuous targets) is the hardest**" — which is exactly the turbulence case.
6. **The significance test that closure papers do not run — the "probe" method (§6, p. 1173)**: introduce a **random variable** into the candidate set; "variables that have a relevance smaller or equal to that of the probe should be discarded". Bi et al. use **three fake variables drawn randomly from a Gaussian**; a non-parametric variant creates fakes "by randomly shuffling real variable vectors"; and as a halting criterion "one can place a threshold on the ratio `f_f/f_t`, which is an **upper bound on the fraction of falsely relevant variables** in the subset selected so far." *A one-line, near-free control that no paper in this corpus applies to a turbulence feature set.*
7. **Selection instability, and the bootstrap remedy (§7.1, p. 1174, verbatim)**: "Many methods of variable subset selection are **sensitive to small perturbations of the experimental conditions.** **If the data has redundant variables, different subsets of variables with identical predictive power may be obtained according to initial conditions of the algorithm, removal or addition of a few variables or training examples, or addition of noise.** ... one might find this variance undesirable because (i) variance is often the symptom of a 'bad' model that does not generalize well; (ii) **results are not reproducible**; and (iii) one subset fails to capture the 'whole picture'." Remedy: repeat the selection on bootstrap sub-samples and take the union, using appearance frequency as a relevance index.
8. **Forward versus backward (§7.4, p. 1175)**: "**weaker subsets are found by forward selection because the importance of variables is not assessed in the context of other variables not included yet** ... Still, **if for some reason we need to get down to a single variable, backward elimination will have gotten rid of the variable that works best on its own.**"
9. **The final recommendation (§8, p. 1179, verbatim)**: "Sophisticated wrapper or embedded methods improve predictor performance compared to simpler variable ranking methods like correlation methods, but **the improvements are not always significant: domains with large numbers of input variables suffer from the curse of dimensionality and multivariate methods may overfit the data.** ... **a unifying theoretical framework is lacking.** ... **we recommend using a linear predictor of your choice (e.g. a linear SVM) and select variables in two alternate ways: (1) with a variable ranking method using a correlation coefficient or mutual information; (2) with a nested subset selection method** performing forward or backward selection or with multiplicative updates."
10. **Scale context (pp. 1157-1160)**: microarray problems have "usually fewer than **100** examples ... the number of variables in the raw data ranges from **6000 to 60,000**"; as of 1997 "**few domains explored used more than 40 features**". Footnote 5, p. 1160: variable ranking's sample complexity "may be **logarithmic** in the number of irrelevant features, compared to a **power law** for 'wrapper' subset selection methods."

**Stated limitations (authors' own words)**

- Footnote 2, p. 1158: "**We caution the reader that this check list is heuristic. The only recommendation that is almost surely valid is to try the simplest things first.**"
- p. 1165, §3.3: "One concern about multivariate methods is that they are **prone to overfitting**. The problem is aggravated when the number of variables to select from is large compared to the number of examples ... **one may wonder whether one could potentially lose some valuable variables through that filtering process.**"
- p. 1179, §8: "**a unifying theoretical framework is lacking**" (quoted in full above).

**What it cannot see**

- **It is a 2003 machine-learning survey with no fluid mechanics, no PDE, no solver, and no notion that the features and the target are coupled through a differential equation.** Every warning above is about a *static* regression problem. In a closure the features are computed from the same solution the model perturbs, so a bad feature choice can change the flow that generates the features — a feedback path Guyon & Elisseeff never contemplate. **Duraisamy 2021's feature-mismatch mechanism (`S k/eps` computed from DNS is not `S_m k_m/eps_m` computed from RANS) is precisely this, and it has no counterpart here.**
- **No treatment of tensor-valued or invariance-constrained features.** The integrity-basis approach of Ling 2016 / Wu 2018 has no analogue in this survey; where the survey says "construct products of features" (check-list item 3), the turbulence literature says "construct the minimal integrity basis", and the second is a much stronger constraint.
- **No fluid-relevant sample sizes.** Its scale intuitions come from microarrays (100 examples, 60,000 variables) and text (millions of documents); turbulence closure sits at the opposite corner — `1e4`-`1e6` points, 5-50 features — where the curse-of-dimensionality warnings bite far less and the redundancy warnings bite far more.
- **No pre-registration or held-out-flow discipline.** The bootstrap-stability recommendation (item 7) is about subset stability under resampling, not about generalisation to a different geometry, which is the failure mode that actually kills closure models.

---

### Ling & Templeton 2015 — ML for regions of high RANS uncertainty `[NOT ON DISK]`

**`BLOCKED-ON-SOURCE`.** Intended: *Evaluation of machine learning algorithms for prediction of regions of high RANS uncertainty*, Phys. Fluids 27:085103. The quarantined file is arXiv:1509.08935, a Herschel dwarf-galaxy survey. **No numeric claim is made here.** Its absence matters more than its shelf code suggests: **it is the origin of the feature set that Wang/Wu/Xiao 2017 (10 features), Wu 2018 (3 supplementary scalars), Kaandorp 2020 (FS3, 9 features) and de Zordo-Banliat 2023 (10 features) all derive from**, and it is the source of the marker/classifier framing that Duraisamy et al. 2019 (Category R, p. 11) recommend as the route to detecting where a model is inadequate. The corpus therefore uses its feature set at second hand in four papers without being able to read its derivation. `_common/FEASIBILITY.md` §1.1 rates a reproduction at **< 0.5 core-hours** with classifier labels derived from the per-cell errors already in `BASELINES.md` — it is blocked entirely on the source.

---

# Catalogue completeness — counts as of this pass (2026-08-20)

## 1. Files on disk versus works catalogued

`docs/papers/closure/` holds **35 PDFs at top level**, but **two of them are byte-identical
aliases of files already present** (see §4 below), so the corpus is **33 distinct works, and this
catalogue now has one full block for each of the 33.**

| Code | Category | Full blocks written | Papers |
|---|---|---|---|
| **A** | Foundational analytical closures | **6** | Pope 1975; Menter 1994; Spalart 2000; Smagorinsky 1963; Nicoud & Ducros 1999; Gatski 1996 |
| **B** | Data-driven RANS | **5** | Wang/Wu/Xiao 2017; Ling 2016 (TBNN); Wu 2018 (PIML); Schmelzer 2020 (SpaRTA); Kaandorp 2020 (TBRF) |
| **C** | Field inversion + ML | **1** | Singh 2017 |
| **D** | Model-form UQ | **2** | Wu 2018 (ill-conditioning); Xiao 2016 (Bayesian/EnKF) |
| **E** | LES subgrid-scale | **5** | Maulik & San 2017; Maulik 2019; Beck 2019; Sirignano/Freund 2020; Guan 2022 |
| **F** | Wall-modelled LES | **4** | Piomelli & Balaras 2002; Larsson 2016; Bae 2022; Lozano-Duran 2023 |
| **G** | Differentiable / solver-in-the-loop | **4** | Stroefer 2021; Um 2020; Kochkov 2021; List 2022 |
| **H** | Multi-model aggregation | **1** | de Zordo-Banliat 2023 |
| **R** | Reviews / perspectives | **4** | Duraisamy 2019; Duraisamy 2021; Beck & Kurz 2021; Sanderse 2024 |
| **X** | Feature selection / ML methodology | **1** | Guyon & Elisseeff 2003 |
| | **TOTAL** | **33** | |

**Secondary category assignments** (each block states its own): Smagorinsky and Nicoud are E-primary
but sit physically in the A section; Sirignano 2020 is E/G co-primary and sits in E; Spalart 2000 is
A/R and sits in A. Counting by *primary* code rather than by section placement gives A 4, E 8,
R 5 — the table above counts by **section placement**, which is how the document reads.

## 2. Not on disk — stub blocks written, no numbers quoted

**16 intended papers have no verified PDF.** Every one has a `[NOT ON DISK]` /
`BLOCKED-ON-SOURCE` stub in the relevant section, and **not one numeric claim is attached to any of
them.**

| Code | Papers with stubs |
|---|---|
| A | Gatski & Speziale 1993 (covered inside the Gatski 1996 block, §0.3 of this document) |
| B | Weatheritt & Sandberg 2016 (GEP) |
| C | Parish & Duraisamy 2016; Singh & Duraisamy 2016; Holland 2019 |
| D | Emory 2013; Iaccarino 2017 |
| E | Germano 1991; Bardina 1980; Vreman 2004; Park & Choi 2021; Zanna & Bolton 2020 |
| F | Bose & Park 2018; Yang 2019 |
| H | Edeling 2014 |
| X | Ling & Templeton 2015 |

**The three gaps that cost the most, in order:**
1. **Holland 2019** — the integrated FIML formulation (Duraisamy 2021's Eq. 9), i.e. the only method
   the reviews say "ensures full consistency between the learning and prediction environments".
   Category C is catalogued from its application, not from its foundation.
2. **Emory 2013 + Iaccarino 2017** — eigenspace perturbation. `_common/FEASIBILITY.md` §1.2 prices
   the falsifiable a-priori question (*does the LES truth lie inside the envelope?*) at
   **< 1 core-hour on frozen fields, with no solve and no ML at all**. It is the cheapest
   high-value item in the whole programme and it is blocked purely on retrieval.
3. **Ling & Templeton 2015** — the origin of the feature set that **four** on-disk papers
   (Wang/Wu/Xiao 2017, Wu 2018, Kaandorp 2020, de Zordo-Banliat 2023) all derive from at second hand.

## 3. Cross-link: the CPU-reproducibility triage is NOT duplicated here

**Confirmed present and authoritative elsewhere.** The compute triage lives in
**`/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common/FEASIBILITY.md`**, which carries
a per-paper matrix (source status, headline number and its location, data needed versus data held,
model size, core-hour estimate, verdict) and a §2 "Compute summary" banding every paper into:

| Band | Content |
|---|---|
| **< 1 core-hour** | Ling 2016 TBNN (VARIANT), Wu 2018 RF, Wang 2017 RF, Schmelzer 2020 a-priori part, Emory/Iaccarino **frozen-field envelope check** |
| **1-20 core-hours** | Kaandorp 2020 TBRF (2-6), Schmelzer 2020 with a-posteriori re-solves (5-15), Emory/Iaccarino 3-case perturbed solves (~5), Um 2020 1-D/2-D VARIANT (2-10) |
| **20-120 core-hours** | de Zordo-Banliat 2023 multi-model sweep (~50), Emory/Iaccarino full 41-case sweep (~60), Beck 2019 at 64^3 (20-40), Kochkov 2021 accuracy-only VARIANT (20-60), Stroefer 2021 single case (10-50), Xiao 2016 reduced-ensemble EnKF (~120) |
| **At or over the 487-core-hour authorisation — STOP and cost first** | Xiao 2016 full EnKF (~450 for **one** case), Weatheritt 2016 GEP full sweep, Beck 2019 at published resolution, List 2022 full unroll sweep |
| **Not reproducible here at any meaningful scale** | Sirignano 2020 DPM, Bae 2022 SciMARL, Lozano-Duran 2023 BFWM, Kochkov 2021 *speed-up* claim |

**That file is the inventory of record for feasibility and compute; this catalogue is the inventory
of record for what each paper says.** Neither duplicates the other, and where they disagree on a
headline number, the paper block here quotes the page and the feasibility matrix quotes the same
page — both were written from the same title-verified PDFs.

**One consequence of this pass changes that file's counts**: `Wu2018_rans_explicit_closure_ill_conditioned.pdf`
and `Guan2022_stable_aposteriori_les_cnn.pdf` are now **VERIFIED-PDF** and were `BLOCKED-ON-SOURCE`
when the matrix was first written. `FEASIBILITY.md` has already been updated for Wu 2018; Guan 2022
still needs its row moved.

## 4. Two byte-identical duplicate pairs on disk

Both were found by `sha256sum` over the whole file, not by name similarity.

| Pair | sha256 (both members) | Recommendation |
|---|---|---|
| `Schmelzer2020_algebraic_reynolds.pdf` = `Schmelzer2020_sparta_sparse_symbolic_regression.pdf` | `7aca1f9a1f40dc4c67c12f83f2c05fe85cecf6527e1107129bb831b68def1208` | **Keep `Schmelzer2020_algebraic_reynolds.pdf`** — it is the name already carried by the `RETRIEVED-VERIFIED` row in `MANIFEST.md`, by `FEASIBILITY.md` §1.1, and by the catalogue block above. Record `..._sparta_sparse_symbolic_regression.pdf` as an **alias**, or delete it. |
| `Xiao2016_model_uncertainties.pdf` = `Xiao2016_bayesian_model_form_uncertainty.pdf` | `1577eabd0d5924146370256cbff8f37397d48953efd1e6589605b6583a40e739` | **Keep `Xiao2016_model_uncertainties.pdf`** — same reasoning: it is the `MANIFEST.md` row, the `FEASIBILITY.md` row, and the catalogue block. The second file arrived later in the same session. |

Both duplicates are **harmless to correctness and harmful to counting**: a naive file count reports
35 papers where there are 33 works, and a manifest with two rows for one document will eventually be
read as two independent sources for the same number. Neither pair is a retrieval *error* — both
members are the correct paper.
