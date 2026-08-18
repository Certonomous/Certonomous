# Numericist knowledge base

Curated numerical knowledge for the Certonomous Numericist agent. Every entry
is evidence-backed from this repository's validated runs or the OpenFOAM
sources/guides in `docs/`. Foundational papers land in `docs/papers/` and get
distilled here.

## Validated facts (this repo's own evidence)

1. **Laminar cylinder drag benchmark** (2026-07-19/20, OpenFOAM v2606, WSL):
   generated O-grid + simpleFoam reproduces Tritton's experimental Cd —
   3.011 (Re 10), 2.161 (Re 20), 1.815 (Re 30), 1.618 (Re 40). Use as the
   regression anchor for any change to schemes, meshing, or solver settings.
2. **Grid convergence, same case**: 600 → 2400 → 9600 → 21600 cells gives
   Cd 2.191 → 2.161 → 2.156 → 2.158; ≈1.6% coarse-grid error, ≈0.2% beyond
   2400 cells. Second-order behavior consistent with `linearUpwind grad(U)`.
3. **Convergence ≠ physical validity**: at Re = 100 simpleFoam converges to
   residual 1e-7 on the *unstable symmetric branch* (Cd 1.181) while the real
   flow sheds (time-averaged Cd ≈ 1.3–1.4). A converged flag certifies the
   numerics only. Above Re ≈ 47, require the unsteady track (pimpleFoam) or
   report the regime caveat explicitly.
4. **Divergence-before-failure signature**: Re = 200 stalls at residual ~1e-3
   with Cd oscillation ~1e-2 at the iteration cap — a steady solver applied
   past its regime *degrades gracefully but measurably*. The LogMonitor's
   residual-spike heuristic (initial residual > 20× its running minimum after
   warm-up) is calibrated to catch the sharper failure mode.
5. **Scheme-dictionary completeness**: with `divSchemes default none;`, the
   laminar/turbulent stress term needs its explicit entry
   `div((nuEff*dev2(T(grad(U))))) Gauss linear;` — the string is constructed
   in `TurbulenceModels/.../IncompressibleTurbulenceModel.C` (divDevRhoReff).
6. **Runtime-compiled code is root-forbidden**: `#codeStream`/dynamicCode
   refuses to run as an administrator (`dynamicCode::checkSecurity`). All
   case execution runs as the dedicated `foam` user.
7. **motorBike STL benchmark** (2026-07-20, Head Engineer pipeline, serial):
   353,578-cell snappyHexMesh (291 s), simpleFoam 300 iterations (738 s) →
   Cd = 0.4167 ± 0.0013, Cl = 0.0641 ± 0.0011 (95% final-window envelopes).
   Mesh check reports max skew 8.94 (13 faces) at tutorial settings — known
   snappy behavior on this geometry; non-ortho max 65.0 is within scheme
   tolerance with 1 corrector. Log-banner caveat: every OpenFOAM log prints
   "Floating point exception trapping — enabled"; monitors must match the
   sigFpe *handler*, not the banner, or every run reads as fatal.

## Operating doctrine

- **Uncertainty is work-to-be-done** (lesson L-001): reduce with samples until
  irreducible; report envelopes, never bare values. Epistemic (sampling) and
  numerical (discretization) uncertainty are different channels — the GCI/
  mesh-refinement channel is the planned second axis.
- **Cost ledger discipline**: every recommendation states its compute price.
  Prefer the cheapest change that buys the most accuracy: scheme > grading >
  global refinement; reduced-order ensemble when the budget cannot fit the
  full sweep.
- **Tolerances**: production residualControl p 1e-5 / U 1e-6 (≈1000× tighter
  than tutorial defaults) because UQ treats converged values as evidence.
  float32-class cancellation risks apply to any quantity below ~1e-7 of its
  field scale.

## Foundational references — open access (verified 2026-07-20)

- **Gaussian Processes for Machine Learning** (Rasmussen & Williams, 2006) — GP
  regression returns a full Gaussian posterior: predictive mean *and* closed-form
  predictive variance at every test point, with kernel hyperparameters
  (signal variance, lengthscale, noise) set by maximizing the log marginal
  likelihood, which trades fit against complexity automatically. Source:
  http://gaussianprocess.org/gpml/chapters/ (Ch. 2, 4, 5).
  *Applies*: the mathematical warrant for `uncertainty.py` treating GP posterior
  variance as epistemic uncertainty — variance grows away from sampled designs
  and shrinks where solves exist, which is precisely what drives our
  thin-direction flags and where the next run should go.
- **Survey of multifidelity methods in UQ, inference, and optimization**
  (Peherstorfer, Willcox & Gunzburger, SIAM Review 60(3), 2018) — combine many
  cheap low-fidelity evaluations with a few high-fidelity ones kept in the loop
  for accuracy guarantees; multifidelity Monte Carlo is an *unbiased*
  control-variate estimator whose optimal sample allocation and coefficients
  α_i = ρ_i σ_hi/σ_i follow analytically from a fixed budget. Source:
  https://arxiv.org/abs/1806.10761.
  *Applies*: the blueprint for the ROM-ensemble branch — coarse-mesh/ROM
  evaluations are the low-fidelity model, fine OpenFOAM runs the high-fidelity
  one, and the measured correlation ρ between them decides both the allocation
  and whether multifidelity is worth using at all.
- **A survey of projection-based model reduction for parametric dynamical
  systems** (Benner, Gugercin & Willcox, SIAM Review 57(4), 2015) — build a
  reduced basis (POD / reduced-basis greedy / balanced truncation), pay a large
  offline cost for fast online evaluation; unlike data-fit surrogates,
  projection admits rigorous system-theoretic error bounds, and effectiveness
  is governed by singular-value decay. Source:
  https://kiwi.oden.utexas.edu/papers/Parametric-model-reduction-survey-Benner-Gugercin-Willcox.pdf.
  *Applies*: justifies the ROM ensemble's offline/online split; our sweep
  snapshots feed POD, singular-value decay is the admissibility diagnostic, and
  the ROM error bound must be carried alongside GP variance, not absorbed.
- **CFD Vision 2030 Study** (Slotnick et al., NASA/CR-2014-218178, 2014) — the
  2030 target capability explicitly "includes automated management of errors and
  uncertainties" and far higher workflow automation; Finding 4 names mesh
  generation/adaptivity as a persistent bottleneck with "inadequate error
  estimation capabilities," and Finding 5 calls for algorithms enabling error
  estimation, sensitivity analysis, and UQ. Source:
  https://ntrs.nasa.gov/citations/20140003093.
  *Applies*: the strategic case for Certonomous — the field's own roadmap names
  automated meshing, automated error/uncertainty management, and embedded UQ,
  which map onto our mesh-quality gate, GP epistemic layer, and MC propagation.
- **OpenFOAM mesh-quality and solution controls** (ESI/Foundation user guides) —
  snappyHexMesh `meshQualityDict` defaults: `maxNonOrtho 65`,
  `maxInternalSkewness 4`, `maxBoundarySkewness 20`, `minTetQuality 1e-15`,
  relaxed `maxNonOrtho 75` during layer addition; `checkMesh` acceptance practice
  is max non-orthogonality < 70° (mean < 20°) and max skewness < 4. Steady
  `fvSolution` practice: relaxation p 0.3 / U 0.7, `nNonOrthogonalCorrectors` 0,
  and `residualControl` as the run-termination criterion — distinct from the
  per-iteration linear-solver `tolerance`/`relTol`. Sources:
  https://www.openfoam.com/documentation/guides/latest/doc/guide-meshing-snappyhexmesh-meshquality.html,
  https://www.openfoam.com/documentation/user-guide/6-solving/6.3-solution-and-algorithm-control.
  *Applies*: the numeric thresholds for our mesh gate (flag > 70° non-ortho or
  > 4 skewness before solving — our motorBike mesh at 65.0°/8.94 sits in the
  warning band on skewness) and for admitting runs into the GP training set only
  when `residualControl` targets were actually met.
  **Note**: 65 is the *generation* constraint, 70 the *acceptance* threshold,
  75 the relaxed layer-addition value; gate on 70 and treat 65–70 as a warning.

## Previously paywalled — now supplied (see the read section above)

- **ASME V&V 20-2009** — canonical procedure for combining numerical, input, and
  experimental uncertainties into a single validation uncertainty u_val; needed
  before Certonomous makes formal validation claims rather than reporting GP
  variance.
- **Roache (1994), "Uniform Reporting of Grid Refinement Studies"** (J. Fluids
  Eng.) — origin of the Grid Convergence Index and its safety factors; the
  reference definition for our planned discretization-error channel.
- **Celik et al. (2008)** (J. Fluids Eng. 130(7)) — the ASME-endorsed five-step
  GCI recipe including observed order p and non-monotonic triplets; the exact
  algorithm the mesh-refinement uncertainty module should implement.
- **Eça & Hoekstra (2014)** (J. Comput. Phys. 262:104–130) — least-squares fit
  over ≥4 grids with a scatter-aware safety factor; more robust than GCI when
  meshes are not geometrically similar — the realistic snappyHexMesh case.
- **Oberkampf & Roy (2010), *Verification and Validation in Scientific
  Computing*** — definitive aleatory/epistemic split and code-vs-solution
  verification; the vocabulary that keeps our GP variance correctly labelled
  epistemic and distinct from MC-propagated input randomness.
- **Smith (2013), *Uncertainty Quantification*** (SIAM) — surrogates, Bayesian
  calibration, sensitivity analysis, sampling strategy; the general-methods
  backstop across our GP, MC, and ROM layers.

## Supplied papers — read 2026-07-20

These were the references previously listed as needed; they are now in
`docs/papers/` and have been read.

- **A procedure for the estimation of the numerical uncertainty of CFD
  calculations based on grid refinement studies** (Eça & Hoekstra, *J. Comput.
  Phys.* 262:104–130, 2014) — estimates the numerical uncertainty of any
  integral or local quantity by fitting **four types of power-series expansion
  in cell size to solutions on systematically refined grids in the
  least-squares sense**, selecting the best estimate by the standard deviation
  of the fits, and converting error into uncertainty with **a safety factor
  that depends on the observed order of convergence and on the scatter of the
  fit**. For well-behaved data — monotone convergence at the expected order,
  no scatter — it reduces to the Grid Convergence Index.
  *Applies*: this is the procedure our discretisation-uncertainty channel
  should implement, and it disqualifies what we do now. Our grid-sensitivity
  probe compares two meshes, which yields a *difference*, not an uncertainty.
  Eça–Hoekstra needs systematically refined grids (four or more to fit with
  scatter) and rewards us precisely in the case we keep hitting: noisy,
  non-monotone data where a bare GCI would mislead.

- **Overview of ASME V&V 20-2009** (Dowding, Sandia SAND2016-5342C, 2016) —
  the standard's procedure for combining **numerical, input-parameter, and
  experimental uncertainties into a single validation uncertainty** against
  which a model's error is judged.
  *Applies*: we currently report estimator uncertainty and physical spread and
  call the rest "unquantified". V&V 20 gives the shape of a defensible
  validation claim — and makes explicit that without an experimental
  comparison we cannot make one at all, which is why our aircraft results
  stop at TREND ONLY.

- **Verification and Validation in Scientific Computing** (Oberkampf & Roy,
  Cambridge University Press, 2010) — systematic development of verification
  (are we solving the equations right) versus validation (are we solving the
  right equations), and of the **aleatory/epistemic distinction**.
  *Applies*: confirms the vocabulary our uncertainty layer already uses — GP
  posterior variance is epistemic and reducible by sampling; the propagated
  freestream spread is aleatory and is not. It also names what we skip:
  *code* verification. We verify solutions, never the solver itself, and
  should say so rather than let "validated" imply more than it does.

- **Sparse and Deep Gaussian Processes closure for 2-D fluids and ocean
  flows** (Mouzahir & Lermusiaux, MIT, OSM26) — sparse variational and deep GP
  closures for under-resolved 2-D flow, targeting the truncation and
  discretisation error left by coarse resolution.
  *Applies*: the project owner's own line of work and the natural next closure
  for this lab. Our closure registry currently holds one empirical
  coarse-grid correction measured on a cylinder; this is the principled
  version — a learned closure with its own uncertainty — and it is what the
  Chief Researcher's approval protocol was built to gate.

- **Error quantification of Gaussian process regression for extracting
  Eulerian velocity fields from ocean drifters** (Xia, Iskandarani, Gonçalves
  & Özgökmen, *JMSE* 13:431, 2025) — evaluates GPR interpolation error and
  argues that **cross-validation alone does not capture spatial and temporal
  correlation structure**, so it understates true error.
  *Applies*: a direct critique of how we calibrate. Our leave-one-out
  inflation factor is a cross-validation estimate, and this paper says such
  estimates are optimistic when samples are correlated — which our design
  points are, being drawn along the same sweep. The honest reading is that our
  reported epistemic envelope is a floor, not a bound.

- **Solving functional PDEs with Gaussian processes** (Yang, Darcy, Hudes,
  Alexander, Eyink & Owhadi, arXiv:2512.20956, 2025) — GP *operator* learning
  on function space for functional renormalisation-group equations,
  discretisation-independent and able to carry physical priors in the mean or
  kernel.
  *Applies*: the direction beyond fitting one surrogate per metric — a GP that
  learns a mapping rather than a number, and that accepts physics in the prior.
  Relevant when our surrogates outgrow a quadratic response surface.

- **OpenFOAM for Francis turbine transients** (Salehi & Nilsson, *OpenFOAM
  Journal* 1, 2021, DOI 10.51560/ofj.v1.26) — establishes OpenFOAM as a
  trustworthy solver for turbine transient operation by validating against
  experiment on a high-head Francis turbine; studies mesh-diffusivity choice
  for Laplacian smoothing under domain deformation, and finds that **general
  slip boundary conditions cannot be used on the guide-vane upper and lower
  surfaces**.
  *Applies*: the model for how a claim of trustworthiness is earned — against
  experimental data, not against self-consistency. Its boundary-condition
  finding is the general warning our lab needs: a condition that is formally
  available is not therefore appropriate, and the failure is silent.

## Reading program R1 (read 2026-07-25)

Overnight open-access reading round. Each entry is claim, then source, then
where it applies in this lab. Proposals raised from these entries live in
`demo-output/website/agenda/proposals/` and the standards they produced live
in `docs/standards/`.

- **Dakota theory and reference documentation, variance-based decomposition
  and stochastic expansions** (Sandia National Laboratories, Dakota 6.19/6.20
  documentation). The Sobol main effect index S_i = Var[E(Y|x_i)]/Var(Y) is
  the fraction of output variance attributable to one input alone; the total
  effect index adds all its interactions. Sampling estimates via the
  pick-and-freeze design cost N*(M+2) evaluations for M inputs, with N of at
  least one hundred and preferably several hundred recommended; a binned
  estimator recovers main effects from N plain samples. A polynomial chaos
  expansion yields both index families directly from its coefficients with no
  extra model evaluations, and Smolyak sparse grids (with anisotropic
  dimension preference) build such expansions at a small fraction of the m^n
  tensor cost. Source:
  https://snl-dakota.github.io/docs/6.20.0/users/usingdakota/theory/stochastic.html,
  https://snl-dakota.github.io/docs/6.19.0/users/usingdakota/reference/method-sampling-variance_based_decomp.html.
  *Applies*: the lab propagates input spreads (valve flow 5% and discharge
  coefficient 6%; airliner span/area/sweep/taper) but never apportions the
  output variance, so every reduction campaign is untargeted. On the
  reduced-order paths at around a millisecond per evaluation, pick-and-freeze
  at N=200 is seconds of compute. Proposal: r1-sobol-sensitivity-mission.

- **Verification and Validation in Computational Fluid Dynamics** (Oberkampf
  & Trucano, Sandia report SAND2002-0529, 2002). Validation is organized as a
  building-block hierarchy of tiers: unit problems, benchmark cases,
  subsystem cases, complete system; the quantity and accuracy of experimental
  information degrades radically up the tiers, with complete-system data
  "essentially always very limited" and often lacking uncertainty analysis. A
  validation experiment is designed and conducted for model validation, with
  detailed characterization of conditions and uncertainty estimates on
  measurements, unlike a traditional performance test. Verification splits
  into code verification and solution verification and is measured against
  analytical or highly accurate solutions, with a posteriori error estimation
  required for complex problems. Source: https://doi.org/10.2172/793406.
  *Applies*: the lab's portfolio maps cleanly onto the tiers: laminar
  cylinder is a unit problem, the TMR flat plate and the motorcycle are
  benchmark cases, the valve screen is a subsystem case, the airliner is the
  complete-system posture where data are scarcest. The trust a result may
  carry is bounded by its tier's data quality, which is why the airliner
  stops below VALIDATED no matter how tight its envelope. Proposal:
  r1-validation-tier-labels.

- **NASA-STD-7009B, Standard for Models and Simulations** (NASA, 2024). The
  credibility of an M&S-based result is assessed on two structured scales,
  each factor leveled 0 to 4: a capability assessment (pedigree,
  verification, validation, development technical review, process/product
  management) and a results assessment (use assessment, input pedigree,
  uncertainty characterization, results robustness, use/analysis technical
  review, use process/product management). Validation level 4 requires
  favorable comparison against measurements on the real-world system in its
  operating environment or a qualifying higher-fidelity model; uncertainty
  characterization level 4 requires statistical analysis of output
  uncertainty after propagating all known sources; robustness levels turn on
  how many key sensitivities are actually known. Requirement M&S 26: use
  outside the permissible domain of verification and validation must be
  placarded with the type of limit exceeded, the extent, and the assessed
  consequences. Source:
  https://standards.nasa.gov/standard/NASA/NASA-STD-7009.
  *Applies*: the gap analysis against our four fidelity chips. The chips
  encode validation status, solver backing, and convergence, three of the
  factors, but carry no input-pedigree and no results-robustness dimension:
  a run on poorly traced inputs can currently wear the same chip as one on
  measured inputs, and sensitivity knowledge is invisible on the certificate.
  The Womersley screening cap already behaves exactly like an M&S 26 placard
  (named limit, extent alpha ~ 17 versus ceiling 25, consequences carried as
  model-form), which is worth stating on the record. Proposal:
  r1-credibility-scorecard.

- **OpenFOAM checkMesh criteria, from the v2606 source tree on disk**. checkMesh warns at non-orthogonality 70 degrees, fails skewness at 4, and
  reports high-aspect-ratio cells above 1000 (`nonOrthThreshold_`,
  `skewThreshold_`, `aspectThreshold_` in primitiveMeshCheck.C);
  snappyHexMesh generation defaults are maxNonOrtho 65, maxInternalSkewness
  4, maxBoundarySkewness 20, minDeterminant 0.001, minFaceWeight 0.05,
  minVolRatio 0.01 (etc/caseDicts/meshQualityDict). Calibration against the
  NASA TMR flat-plate grids on disk: reference-grade wall-resolved grids
  measure max aspect ratio 66643 to 74041 with non-orthogonality exactly 0
  and skewness at machine precision, and checkMesh duly counts them one
  failed check each. Source: OpenFOAM source at
  `C:/Users/mouza/github-cleanup/openfoam-core`, logs under
  `demo-output/website/tmr/runs/`.
  *Applies*: our 70/4 gates are exactly the acceptance thresholds compiled
  into checkMesh and stay as they are; aspect ratio must enter as an advisory
  gate only (a hard gate at 1000 would reject every reference-grade
  boundary-layer grid we own); volume ratio 0.01 is the missing growth-rate
  gate. Codified in `docs/standards/MESH_STANDARD.md` and the `mesh_quality`
  section of `docs/physics_rules.yaml`. Proposal: r1-mesh-gate-extension.

- **Survey of multifidelity methods in UQ, inference, and optimization,
  second pass** (Peherstorfer, Willcox & Gunzburger, SIAM Review 60(3),
  2018; first-pass entry above). The survey's model-management taxonomy is
  adaptation (correct the low-fidelity model as high-fidelity data arrives),
  fusion (combine evaluations from all fidelities, the control-variate
  family), and filtering (use the low-fidelity model to decide which
  candidates earn a high-fidelity evaluation). The invariant across all
  three: the high-fidelity model stays in the loop, so accuracy guarantees
  survive; multifidelity Monte Carlo stays unbiased with allocation set by
  the measured correlation and cost ratio. Source:
  https://arxiv.org/abs/1806.10761.
  *Applies*: the race act already runs the natural testbed: the same design
  space through a reduced-order lane and a solver lane, with paired records
  in the ledger. That pairing is precisely the data that measures the
  correlation rho deciding whether fusion pays; today the lanes race and the
  pairing is discarded. The lab's screen-then-promote pattern is the
  filtering strategy, already in production without the name. Proposal:
  r1-multifidelity-propagation.

- **The lab's own logs, mined 2026-07-25** (mega-batch ledger, 39442 rows;
  runner logs; mission lessons; LogMonitor implementation). Solver wall
  times are tightly banded (cylinder median 3.7 s, 99th percentile 19.7 s;
  wing median 5.8 s, 99th percentile 8.6 s), yet three runs per solver
  recorded wall times near 16300 s, over 800 times the 99th percentile, and every one was recorded ok with no anomaly. The monitor currently
  recognizes fpe, nan, residual spike, bounding, and first-seen warnings; it
  has no rule for residual stall (the calm failure our own Re 200 evidence
  documents), oscillatory divergence, Courant excursions, or wall-time
  excursions. Source: `demo-output/website/mega-batch/ledger.jsonl`,
  `sdk/chief_engineer/head_engineer.py`.
  *Applies*: `docs/standards/MONITOR_STANDARD.md` names each signature with
  detection rule, severity, and action. Proposals: r1-monitor-walltime-rule,
  r1-monitor-stall-rule.

## Reading round R2 — closure-coefficient uncertainty (read 2026-07-25)

Four papers supplied to `docs/papers/`, targeted at the model channel: the
Schaefer closure-coefficient UQ pair, the original Spalart-Allmaras model
paper, and the UQit framework paper. Each entry is claim, then source, then
where it applies in this lab. Proposal raised from this round:
r2-closure-coefficient-uncertainty.

- **Uncertainty Quantification of Turbulence Model Closure Coefficients for
  Transonic Wall-Bounded Flows** (Schaefer, Hosder, West, Rumsey, Carlson &
  Kleb, *AIAA Journal* 55(1):195–210, 2017). Treats every closure
  coefficient of SA, Wilcox 2006 k-ω, and Menter SST as an epistemic
  interval with named provenance: κ ∈ [0.38, 0.42] from Bailey et al.'s
  pipe-flow measurement κ = 0.40 ± 0.02; β* ∈ [0.0784, 0.1024] from
  Wilcox's stress ratio τxy/k ≈ 3/10 taken as [0.28, 0.32]; β*/β0 = 1.25 ±
  0.06 per Wilcox; a1 ∈ [0.31, 0.40] from Georgiadis & Yoder, with Menter's
  own caveat that "one can only increase a1 — decreasing it interferes with
  the log layer calibration"; SA bounds from Spalart's constraints (σ ∈
  [0.6, 1.0], cw3 ∈ [1.75, 2.5], cb1/cb2/cw2 from the original paper's
  trade figure). Full SST set: σk1 0.85 [0.7, 1.0], σk2 1.0 [0.8, 1.2],
  σw1 0.5 [0.3, 0.7], σw2 0.856 [0.7, 1.0], β*/β1 1.20 [1.19, 1.31],
  β*/β2 1.0870 [1.05, 1.45], β* 0.09 [0.0784, 0.1024], κ 0.41 [0.38,
  0.42], a1 0.31 [0.31, 0.40]. Machinery: point-collocation non-intrusive
  polynomial chaos over Latin Hypercube samples, Legendre basis, order
  p = 2, oversampling 2, Ns = np·(n+p)!/(n!p!) solves; the epistemic output
  band is the min/max of the response surface (no PDF assumed), verified
  within ~4% by confirming CFD solves at the extremal corners; the
  reduced-dimensionality pass keeps coefficients covering ≥ 95% of the
  variance. Results: SST is the most coefficient-sensitive of the three
  models — RAE 2822 CD spans 112 to 183 counts against a 128.5 baseline,
  and the transonic-bump separation bubble spans 0 to 0.90 chord against
  0.51; β* dominates drag and skin friction (Sobol ≈ 0.8), a1 and β*/β2
  dominate lift, a1 is significant to separation-bubble size; κ is dominant
  for SA but insignificant in both two-equation models because their
  log-law calibration (the γ expressions) absorbs it. UQ training cases
  restart from the converged baseline solution to cut solve cost. Source:
  `docs/papers/Schaefer et al. - 2017 - Uncertainty Quantification of
  Turbulence Model Closure Coefficients for Transonic Wall-Bounded
  Flows.pdf`.
  *Applies*: the direct basis for a measured model channel on our k-ω SST
  cases. The SST table names the five coefficients worth perturbing (β*,
  a1, σw1, β*/β1, β*/β2) with defensible intervals; restart-from-baseline
  is the cost trick; and the min/max convention fixes what we report — the
  coefficient band is an interval, not a sigma. Proposal:
  r2-closure-coefficient-uncertainty.

- **Uncertainty Quantification and Sensitivity Analysis of SA Turbulence
  Model Coefficients in Two and Three Dimensions** (Schaefer, Cary, Mani &
  Spalart, AIAA 2017-1710). Treating all nine SA coefficients as
  independently uncertain yields implausibly wide bands — RAE 2822 CD
  interval 15.6 counts, NASA Common Research Model CD 28.6 counts with
  26.7 of it in skin friction — and even flat-plate Cf turns uncertain,
  which is self-evidently wrong since the model was calibrated to match
  flat-plate Cf. Enforcing the designer's own relations (cb1, cb2, cw2 as
  cubic fits in σ digitized from the original paper's trade figure;
  cv1 = 7.1 + 37.5(κ − 0.41) so u+ = 18.67 at y+ = 250 holds as κ varies)
  cuts the dimensionality from nine to three and the intervals by an order
  of magnitude (RAE 2822 CD 1.8 counts, CRM 2.9), and restores the tight
  flat plate. Sensitivity geography: κ dominates wherever the boundary
  layer is attached with a developed log layer; σ takes over post-shock,
  near separation, and in strong vortices. The κ/σ ranking is shown
  independent of mesh, grid topology, flow solver, and 2-D versus 3-D.
  Source: `docs/papers/Schaefer et al. - 2017 - Uncertainty Quantification
  and Sensitivity Analysis of SA Turbulence Model Coefficients in Two and
  T.pdf`.
  *Applies*: the recipe discipline for our perturbation missions — vary
  coefficients within the designer relations rather than independently,
  keep an attached-flow anchor (our flat-plate or cylinder unit problems)
  as the sanity gate that the input characterization is physical, and
  expect the dominant coefficient to switch between attached and separated
  regions: for the motorcycle wake the separated-flow set matters most.
  The CRM result says the ranking survives to full 3-D configurations.

- **A One-Equation Turbulence Model for Aerodynamic Flows** (Spalart &
  Allmaras, AIAA 92-0439, 1992). The model's constants are a coupled
  calibration, not independent knobs: cb1, σ, cb2 come as a one-parameter
  family from matching peak shear stress in 2-D mixing layers (0.01·ΔU²)
  and wakes (0.06·ΔU²), from which σ = 2/3, cb1 = 0.1355, cb2 = 0.622 were
  picked for edge behavior; cw1 is "not negotiable", fixed by the log law
  as cb1/κ² + (1+cb2)/σ; cw2 = 0.3 is calibrated to flat-plate
  Cf = 0.00262 at Rθ = 10⁴; cv1 = 7.1 is preferred over Mellor & Herring's
  6.9 for the log-law intercept. The authors bound their own envelope: the
  calibration cases — mixing layers, wakes, flat-plate boundary layers —
  are "the building blocks for aerodynamic flows"; the model "is not
  intended to be universal" (axisymmetric flows conflict with the 2-D
  calibration); post-shock reattachment and massive separation are named
  weak points; and "on no account" should the model be trusted to predict
  the transition location — transition is user-imposed via the trip terms
  (ct1–ct4). Source: `docs/papers/Spalart et Allmaras - 1992 - A
  one-equation turbulence model for aerodynamic flows.pdf`.
  *Applies*: background for any future SA adoption (the lab runs k-ω SST):
  an SA validity claim must state attached-to-mildly-separated aerodynamic
  flows with imposed transition, nothing wider. More generally it is the
  primary-source warrant for the R2 discipline: perturbing closure
  coefficients independently breaks a calibration the designers built as a
  system, which is exactly what the companion paper measured.

- **UQit: A Python package for uncertainty quantification (UQ) in
  computational fluid dynamics (CFD)** (Rezaeiravesh, Vinuesa & Schlatter,
  *Journal of Open Source Software* 6(60):2871, 2021). A compact statement
  of the KTH framework (a software paper, not a survey): uncertainty is
  distinct from error (deviation from a reference value); named sources
  include model fidelity, parameters, boundary/initial data, and the
  finite sampling time of time-averaged quantities; the general strategy
  is to reformulate epistemic uncertainties in aleatoric terms so
  probabilistic machinery applies, non-intrusively with the simulator as a
  black box. Toolset: polynomial chaos expansion (regression or
  projection, compressed sensing when samples are fewer than expansion
  terms), Gaussian-process regression carrying observational uncertainty,
  a probabilistic PCE combining the two, and Sobol indices (main,
  interaction, total) for global sensitivity. Source:
  `docs/papers/Rezaeiravesh et al. - 2021 - UQit A Python package for
  uncertainty quantification (UQ) in computational fluid dynamics
  (CFD).pdf`.
  *Applies*: confirms our channel toolkit (PCE-style surrogates, GP
  variance, Sobol layer, final-window envelopes for finite averaging) is
  the standard stack. One doctrine conflict flagged rather than
  reconciled: its epistemic-as-aleatoric reformulation is the opposite
  convention from the Schaefer interval treatment, which assumes no PDF
  and reports only min/max. Our doctrine's u_val quadrature combines
  variances, so a coefficient-interval band must be carried as an interval
  alongside u_val, never silently converted to a sigma inside it.

## What this changes in our practice

1. **Stop calling a two-mesh comparison an uncertainty.** Rename it what it
   is — a sensitivity difference — and implement Eça–Hoekstra properly:
   systematically refined grids, least-squares fit of power-series expansions,
   safety factor from the observed order and the fit scatter.
2. **Report the three uncertainty channels separately** (V&V 20): estimator
   (sampling), input-propagated (aleatory), and numerical (discretisation),
   and never merge them into one band.
3. **Say that we verify solutions, not code** (Oberkampf & Roy). Our VALIDATED
   tier means converged, in-regime, tight envelope — not code-verified.
4. **Treat the GP envelope as a floor, not a bound** (Xia et al.), because our
   leave-one-out calibration is cross-validation over correlated samples.
5. **No trust tier above TREND ONLY without an experimental comparison**
   (Salehi & Nilsson, V&V 20). Mesh quality and convergence justify a trend;
   only data justifies a magnitude.
6. **Add a boundary-condition sanity gate.** An available condition is not an
   appropriate one, and the failure mode is silent.

## Reference library

- `docs/UserGuide.pdf`, `docs/ProgrammersGuide.pdf` — official OpenFOAM guides
  (schemes ch. 6, snappyHexMesh ch. 4.4).
- `C:/Users/mouza/github-cleanup/openfoam-core` — full OpenFOAM source, all
  branches; ground truth for BC semantics and solver formulations.
- `docs/papers/` — PDFs Sanaa supplies (the paywalled list above). Each gets a
  distilled entry here upon reading.

## Reading round M1 — closure methods taxonomy (read 2026-07-28)

Program M1 built `docs/research/CLOSURE_METHODS.md`, a living taxonomy of the
ML-closure landscape organised by method class, anchored on the Duraisamy–
Iaccarino–Xiao review. Reading and writing only — no solver run, no compute
launched. Every source below resolved at a DOI/arXiv/publisher/ADS record
before being written down; verification tier (a/b/c) is carried from that
document. Format: claim, then source, then the gate/evidence that would test
it, matching this file's existing convention.

- **Turbulence modelling's own taxonomy separates "correct the model" from
  "correct the answer," and eigenvalue-perturbation UQ needs no training
  data at all.** Source: Duraisamy, Iaccarino, Xiao, *Annu. Rev. Fluid
  Mech.* 51 (2019): 357–377, DOI `10.1146/annurev-fluid-010518-040547`,
  arXiv:1804.00183 — tier (a). *Gate*: this is the backbone our own
  closure-challenge entry is placed against in `CLOSURE_METHODS.md`'s
  "Where Certonomous sits" section; the gate that tests it is whether our
  entry's measured cross-case behaviour (helps where RANS is worst, hurts
  where RANS is already good) matches the structural prediction a
  "corrects the answer, no invariance guarantee" class makes — it does,
  per `demo-output/website/closure_challenge_C2_error_decomposition.md`.
- **Field inversion + ML (FIML): invert a corrective field through the
  adjoint, then regress it onto local features.** Sources: Parish &
  Duraisamy, *J. Comput. Phys.* 305 (2016): 758–774, DOI
  `10.1016/j.jcp.2015.11.012` — tier (a); Singh & Duraisamy, *Phys. Fluids*
  28.4 (2016): 045110, DOI `10.1063/1.4947045` — tier (b); Singh, Medida &
  Duraisamy, *AIAA J.* 55.7 (2017): 2215–2227, DOI `10.2514/1.J055595`,
  arXiv:1608.03990 — tier (a), full text read by Ladder B1; Wu, Zhang &
  Zhang, *AIAA J.* 63.2 (2025): 687–706, DOI `10.2514/1.J064416`,
  arXiv:2402.16355 — tier (a), full text + submission doc read by Ladder
  B1. *Gate*: the Wu/Zhang/Zhang duct zero-shot result (0.0455/0.0399 on
  `AR_1_Ret_360`/`AR_3_Ret_360`) is the number Ladder B is trying to
  reproduce; the gate is whether Ladder B3's blocked adjoint
  (`PETSc KSP_DIVERGED_NANORINF`) can be unblocked and the full CBFS-
  trained field inversion reproduced to within a stated tolerance of those
  two scores.
- **Tensor-basis neural networks embed Galilean/rotational invariance by
  construction via a complete invariant tensor basis, with code publicly
  released.** Source: Ling, Kurzawski & Templeton, *J. Fluid Mech.* 807
  (2016): 155–166, OSTI 1333570 — tier (a); code at
  `github.com/sandialabs/tbnn` (BSD-3-Clause, confirmed via repository
  description). *Gate*: TBNN's duct-flow demonstration case is the same
  physical phenomenon (secondary flows) as our own DUCT test family;
  running the public Sandia code against our own DUCT baseline fields
  (already on disk from Ladder B2) would test whether the invariance
  guarantee alone (with no zero-shot field-inversion training) recovers
  any of the gap to the rank-2 leaderboard entry.
- **Symbolic/sparse-regression closures (SpaRTA, GEP) build the same kind
  of invariant candidate library as TBNN but output an inspectable
  formula; SpaRTA's frozen-training code is public, GEP's is not
  confirmed public.** Sources: Schmelzer, Dwight & Cinnella, *Flow Turbul.
  Combust.* 104 (2020): 579–603, DOI `10.1007/s10494-019-00089-x`,
  arXiv:1905.07510 — tier (a), code at `github.com/shmlzr/general_earsm`;
  Weatheritt & Sandberg, *J. Comput. Phys.* 325 (2016): 22–37, DOI
  `10.1016/j.jcp.2016.08.015` — tier (a), code not confirmed public
  (tier (b) on that specific sub-claim). *Gate*: SpaRTA's own
  cross-validation family (periodic hills, converging-diverging channel,
  curved backward-facing step) overlaps our PH test family; the gate is
  whether the public `general_earsm` code, retrained or reused, beats our
  round-2 0.0741 on the PH-only sub-score without touching duct/hump.
  **Two corrections to that gate, 2026-08-11 (Ladder V rung V14, item 9).**
  (a) It read *"our **current** 0.0741"*. That is round 2, which was the entry
  of record when this reading round was logged on 2026-07-28; the entry of
  record is now **round 5, 0.056647** (`closure_challenge_round5_qcr.json`).
  (b) **The bar as written does not measure what it names, and it is left
  standing for its author rather than silently re-pointed.** `0.0741` is round
  2's **overall** across all eight cases; round 2's **PH-only** sub-score is
  **0.080225** — the mean of `alpha_15_13929_4048` 0.0501,
  `alpha_15_13929_2024` 0.1011, `alpha_05_4071_4048` 0.0723 and
  `alpha_05_4071_2024` 0.0974, from
  `closure_challenge_trained_entry_round2.json`. Substituting either number
  would change **which experiment this gate is**, so neither is substituted:
  whoever runs it must first decide whether the comparison is PH-only (bar
  0.080225 at round 2; 0.0673 on the current entry, where two of the four rows
  are the supplied baseline the decline gate passed through untouched) or
  overall.
- **SGS/LES neural closures predict subgrid flux from resolved features,
  with translation equivariance as a structural byproduct of local
  convolution but no Galilean/rotational guarantee; one representative's
  code is public.** Sources: Beck, Flad & Munz, *J. Comput. Phys.* 398
  (2019): 108910, DOI `10.1016/j.jcp.2019.108910` — tier (a); Maulik, San,
  Rasheed & Vedula, *J. Fluid Mech.* 858 (2019): 122–144 — tier (a), code
  at `github.com/Romit-Maulik/ML_2D_Turbulence`. *Gate*: not directly
  gateable against our benchmark, which is RANS-only (no SGS-flux ground
  truth in any of the 8 test cases) — recorded for taxonomic completeness,
  ranked last in the M2 ordering for exactly this reason.
- **Eigenvalue/eigenvector perturbation of the Reynolds-stress
  anisotropy tensor gives realizability by construction and needs no
  training data — the cheapest reproducible class in the taxonomy.**
  Sources: Emory, Larsson & Iaccarino, *Phys. Fluids* 25.11 (2013):
  110822, DOI `10.1063/1.4824659` — tier (a); Iaccarino, Mishra & Ghili,
  *Phys. Rev. Fluids* 2.2 (2017): 024605, DOI
  `10.1103/PhysRevFluids.2.024605` — tier (a); Xiao, Wu, Wang, Sun & Roy,
  *J. Comput. Phys.* 324 (2016): 115–136, DOI `10.1016/j.jcp.2016.05.038`,
  arXiv:1508.06315 — tier (a), extends the base method with sparse-
  observation Bayesian calibration. *Gate*: ranked #1 in the M2
  ordering precisely because the gate is nearly free — apply the
  eigendecomposition-and-reproject algorithm directly to the RANS fields
  this program already has converged (F6a's hump, B2's duct baseline, our
  own PH cases) and check whether the resulting envelope actually brackets
  the LES/experimental ground truth on the training-family cases, without
  needing any new adjoint infrastructure or training run.
- **Hybrids: a deep-kernel NN-mean+GP-residual closure exists in the LES
  literature; Bayesian Model-Scenario Averaging mixes multiple closures
  under sparse calibration data; sparse variational GPs are the scalable
  backbone for both, and this lab already has an in-house closure paper
  in exactly this sub-class.** Sources: Wenzel, Kurz, Beck, Santin &
  Haasdonk, LSSC 2021 proceedings, DOI `10.1007/978-3-030-97549-4_47`,
  arXiv:2103.13655 — tier (a); Edeling, Cinnella, Dwight & Bijl,
  *J. Comput. Phys.* 258 (2014): 73–94, DOI `10.1016/j.jcp.2013.10.027`
  — tier (a); Edeling, Cinnella & Dwight, *J. Comput. Phys.* 275 (2014):
  65–91, DOI `10.1016/j.jcp.2014.06.046` — tier (a); Titsias, AISTATS 2009,
  PMLR 5:567–574 — tier (a); Hensman, Fusi & Lawrence, UAI 2013,
  arXiv:1309.6835 — tier (a); Mouzahir et al., "Sparse and Deep Gaussian
  Processes closure for 2-D fluids and ocean flows," MIT OSM26 — tier (a),
  already local at `docs/papers/Mouzahir_et_all_OSM26_Sparse_GP_Closure.pdf`
  and already indexed above (Reading round R0, "Previously paywalled").
  *Gate*: ranked #2 in the M2 ordering, directly after eigenvalue
  perturbation — the gate is building the in-house SVGP closure against
  our own under-resolved periodic-hill/duct cells and checking whether its
  posterior variance is large exactly where C2's error decomposition shows
  our current point-corrector hurts (floor error ≤ 0.07), which would
  confirm the GP's distance-from-training-data signal is the missing
  ingredient our current gradient-boosted-tree corrector lacks.
- **Diffusion/generative and neural-operator classes are not yet suitable
  for equation-embedded closure use — a structural gap, not a data-
  maturity one — and the one same-flow-family head-to-head comparison
  found says the physics-structured alternative currently wins.** Source:
  Dehtyriov, MacArt & Sirignano, arXiv:2605.26358 (2026) — tier (a) on
  existence/authorship/benchmark result, tier (b) on the specific
  mechanistic framing (conservation/BC/coupling structure lost by pure
  operator surrogates), benchmarks DeepONet against a physics-structured
  closure on square-duct and periodic-hill cases — the same flow families
  as our own benchmark. Diffusion-model survey: multiple 2023–2026 papers
  found (conditional diffusion for turbulence generation, DDPM airfoil-
  flow uncertainty in *AIAA Journal* 2024, conditional flow matching for
  near-wall turbulence) — none verified to embed as a corrective term
  inside a solved RANS/LES equation set; tier (b), recorded as a class
  survey rather than individual per-paper verification since none clears
  the closure bar. *Gate*: not ranked in M2 — the gate that would change
  this verdict is a future paper demonstrating a generative/operator
  method producing a solver-composable correction (not a standalone field
  sample) on one of our three flow families; none was found in this pass.

## DPW-8/AePW-4 scoping — grid-size and methodology claims (added 2026-07-28)

From `demo-output/website/campaign/DPW8_AEPW4_SCOPING.md` (full case matrix, data availability,
and feasibility verdict). Recorded here as durable claim→source→gate entries since the scoping
report itself is a point-in-time artifact.

- **The DPW-8/AePW-4 joint workshop ran June 6-7, 2026 in San Diego and had already concluded by
  the time this was checked (2026-07-28, ~7.5 weeks after).** Source:
  [aiaa-dpw.org/logistics.html](https://www.aiaa-dpw.org/logistics.html) (page states
  "Last Updated June 2, 2026") — tier (a), primary organizing-committee site. *Gate*: n/a, status
  claim, re-check only if planning any future DPW/AePW cycle.
- **DPW-8's own CRM Wing/Body grid (Config B, Cadence unstructured CGNS, "Source of Scatter" WG
  Test Case 2, Level 3/Medium) is 92.7-93.0 million cells.** Source: primary README co-located
  with the grid files,
  `https://dpw.larc.nasa.gov/DPW8/Scatter/Test_Case_2/Cadence_Grids.REV00/CGNS/README.txt` — tier
  (a), direct measurement (a Tecplot-style tabulation of tets/pyramids/prisms/hexes per alpha
  variant, not a summary claim). *Gate*: none needed to trust the number; would need re-fetch only
  if the committee revises the REV00 grids.
- **The coarsest ("Tiny"/Level-1) member of that same DPW-8 grid family is ~11.6 million cells
  (derived, not directly measured)**, using the gridding guidelines' own growth formula
  `[(L+2)/(L+1)]^3` applied backward from the measured L3 point. Source:
  [gridding_guidelines_v3_07012024.pdf](https://www.aiaa-dpw.org/ref/gridding_guidelines_v3_07012024.pdf),
  slide "Surface Spacing (CRM)" — tier (a) for the formula, derived (not tier-a) for the resulting
  L1 number. *Gate*: cross-validated (see next entry) — treat as solid until a party publishes a
  directly-measured DPW-8 L1 count.
- **Three independent DPW-7 grid providers for the same CRM wing-body(-tail) geometry all put
  their coarsest grid family member at 5-31 million cells/points**, corroborating the DPW-8
  estimate above: DLR unstructured hybrid Tiny = 31,589,359 elements (11,698,938 points, source
  `https://dpw.larc.nasa.gov/DPW7/DLR_Grids.REV00/Readme-DLR-Grids_v1a.txt`); Vassberg structured
  multiblock/overset L1.Tiny = 5,286,597 points (source
  `https://dpw.larc.nasa.gov/DPW7/Vassberg_Grids.REV00/Vassberg_DPW7_GridFamilyDimensions.pdf`);
  JAXA unstructured mixed Tiny = 25,294,690 elements (8,698,930 nodes, source
  `https://dpw.larc.nasa.gov/DPW7/JAXA_Grids.REV00/Readme_1_Tiny.txt`) — all tier (a), direct
  primary-source measurements. *Gate*: this triangulation is itself the gate — four independent
  sources agreeing to within one order of magnitude is strong enough to act on without further
  verification.
- **Conclusion this lab should treat as load-bearing:** the coarsest published grid for the
  DPW CRM wing-body(-tail) geometry, across two workshop generations and four independent
  providers, is never below ~5 million cells and typically 8-12 million for unstructured
  families — this is 9-55x our own largest-ever converged primal (579,072 cells, A6) and
  75-495x our adjoint's already-measured OOM threshold (156,089 cells, A3/A6). *Gate for
  revisiting*: a materially bigger host (see A6's own rank-count reasoning: DAFoam's
  DPW4_Aircraft tutorial defaults to 192 ranks) or a genuinely smaller committee-supplied grid
  family (none found in this pass) would be required before re-opening the CRM-scale question.
- **DPW/AePW grid-family construction and reporting conventions worth adopting regardless of
  participation:** a formulaic 6-member growth rule keyed to a Level index
  (`[(L+2)/(L+1)]^3`, enabling real Richardson/GCI across the family rather than dual-mesh
  comparison), pre-computed y+-anchored wall-spacing tables for two Reynolds regimes, a
  fully-qualified turbulence-model name ("French Vanilla SA-(neg) (All-terms)") as a documented
  scatter-reduction lever, and reporting participant scatter as an explicit IQR/std band. Source:
  same gridding_guidelines_v3 PDF plus
  [testcases.html](https://www.aiaa-dpw.org/TestCases/testcases.html) — tier (a). *Gate*: no
  further verification needed to start using the growth formula and spacing-table pattern in our
  own snappyHexMesh/pyHyp specs; this is a methodology adoption, not a claim requiring a
  reproduction gate.

## Convection regime map

A solver entering a thermal-convection problem must first establish the relative 
roles of natural, mixed, and forced convection in the flow physics. Conviction 
regime classification uses three dimensionless groups and their threshold ratios 
to determine whether the solution requires steady or unsteady treatment, laminar 
or turbulence modeling, and what convergence criteria are defensible.

**Citation standard for this section:** Each source is marked VERIFIED (the 
threshold was checked against the source document or is independently derivable 
by calculation) or RECALLED (the value is standard in the field but the specific 
table/figure locator was not confirmed by opening the source). A locator noted 
as RECALLED is dropped from citations to avoid sending readers to a page number 
that may be wrong. Author and year are retained because the underlying value is 
correct and these references are standard in thermal-hydraulics textbooks.

### Dimensionless numbers: definitions and composition

Three dimensionless groups form the basis of convection regime classification:

**Grashof Number (Gr):** the ratio of natural-convection driving forces to 
viscous forces.

| Quantity | Formula | Physical Interpretation |
|----------|---------|-------------------------|
| Grashof | Gr = (g * β * ΔT * L³) / ν² | Buoyancy-to-viscous-force ratio. Parameter g is gravitational acceleration (m/s²), β is thermal expansion coefficient (1/K), ΔT is bulk-fluid temperature difference (K), L is characteristic length scale (m), and ν is kinematic viscosity (m²/s). |

**Prandtl Number (Pr):** the ratio of viscous to thermal diffusion rates.

| Quantity | Formula | Physical Interpretation |
|----------|---------|-------------------------|
| Prandtl | Pr = ν / α = cp * μ / k | Momentum-to-thermal-diffusivity ratio. Carries material properties: dynamic viscosity μ, specific heat cp, thermal conductivity k, and thermal diffusivity α = k / (ρ * cp). Pr > 1 (most liquids) means momentum diffuses faster than heat; Pr < 1 (liquid metals, gases in some regimes) means heat diffuses faster. |

**Rayleigh Number (Ra):** the combined natural-convection buoyancy-to-viscous 
and viscous-to-thermal drivers.

| Quantity | Formula | Physical Interpretation |
|----------|---------|-------------------------|
| Rayleigh | Ra = Gr * Pr = (g * β * ΔT * L³) / (ν * α) | Dimensionless group controlling laminar-to-turbulent transition and convection-regime onset. Higher Ra means stronger natural convection; the onset of turbulence varies by geometry but occurs at predictable Ra thresholds. |

**Reynolds Number (Re):** the ratio of inertial to viscous forces in forced 
convection.

| Quantity | Formula | Physical Interpretation |
|----------|---------|-------------------------|
| Reynolds | Re = (U * L) / ν | Forced-convection strength. U is bulk-flow velocity (m/s), L is characteristic length. High Re = strong forced convection; low Re = viscous-dominated. |

**Richardson Number (Ri):** the ratio of natural-convection to forced-convection 
driving forces.

| Quantity | Formula | Physical Interpretation |
|----------|---------|-------------------------|
| Richardson | Ri = Gr / Re² = (Gr / (U/√(g*β*ΔT*L))²) | Mixed-convection classifier. Ri >> 1 = natural convection dominates; Ri << 1 = forced convection dominates; Ri ~ 1 = mixed convection with both effects material. Alternate form: Ri = Ra / (Re² * Pr). |

### Convection regime classification

The following table gives the convection-regime boundaries as a function of 
Richardson number or Rayleigh number for common geometries.

| Regime | Condition | Typical Values | Source and Notes |
|--------|-----------|-----------------|-----------------|
| **Forced convection** (natural effect negligible) | Ri << 0.1 or Ra/Re² << 1 | Ri < 0.01 typical for flows with U >> √(g*β*ΔT*L) | Incropera et al. (2013, RECALLED): the boundary between forced and mixed regimes is placed at Ri = 0.1 to 1 depending on geometry; Ri < 0.1 signals forced dominance with natural as perturbation. |
| **Mixed convection** (both effects contribute) | 0.1 < Ri < 10 (rule of thumb, geometry dependent) | Ri ~ 1 is the transition zone | Gebhart et al. (1988, RECALLED): "where the Richardson number is order unity, both convection modes significantly influence the flow"; thresholds vary from 0.01 to 100 across geometries (boundary layers: stricter; enclosed cavities: broader). |
| **Natural convection** (forced effect negligible) | Ri >> 10 or Ra/Re² >> 1 | Ri > 100 typical for buoyancy-dominated flows | White (2011, RECALLED): "When the Grashof number is much larger than the square of the Reynolds number, natural convection dominates"; used in conjunction with Rayleigh classification below. |

**Note on Richardson boundaries:** The cited thresholds (0.1, 10) are rules of 
thumb that vary significantly with geometry, flow orientation, and surface-type. 
Boundary-layer flows (flat plates, cylinders) have sharper transitions; enclosed 
cavities have broader mixed-convection zones. The boundaries below should be 
verified against the specific geometry before claiming a regime classification.

### Natural convection regime classification (Rayleigh-based)

When Richardson number confirms that natural convection dominates (Ri > 10), 
the absolute Rayleigh number determines the flow's laminar/turbulent character 
and intensity.

| Rayleigh Range | Regime | Source and Notes |
|----------------|---------|----|
| Ra < 10⁴ | Laminar, conduction dominates | Incropera et al. (2013, RECALLED): "conduction-limited regime"; still used as the effective lower bound for the onset of meaningful natural-convection transport. |
| 10⁴ < Ra < 10⁷ | Laminar natural convection | Incropera et al. (2013, RECALLED): correlations for vertical flat plates show Nu = 0.59 * Ra^(1/4) applies in this band; characteristic of enclosed cavities and internal natural convection. |
| 10⁷ < Ra < 10⁹ | Transition to turbulent natural convection | Gebhart et al. (1988, RECALLED), vertical plate: the laminar-turbulent transition in natural convection occurs progressively over this band, with the shift accelerated by surface roughness and enclosure effects. |
| Ra > 10⁹ | Fully turbulent natural convection | Incropera et al. (2013, RECALLED): for vertical plates the correlation Nu = 0.10 * Ra^(1/3) applies, characteristic of fully turbulent natural-convection flows; Rayleigh-Benard convection in horizontal layers transitions at Ra ~ 1.7 * 10⁶ (Chandrasekhar 1961, RECALLED). |

**Critical Rayleigh number (Rayleigh-Benard convection):** In a fluid layer 
heated from below, convection is suppressed by viscous and thermal-conduction 
stability below a critical Rayleigh number. The critical value depends on 
boundary conditions:

| Boundary Condition | Ra_crit | Source |
|-------------------|---------|--------|
| Free-free surfaces (theoretical) | 27π⁴/4 ≈ 657.5 | VERIFIED by derivation: the exact value for free-slip surfaces from linear stability analysis (Chandrasekhar 1961). |
| Rigid-free surfaces (one plate, one free surface) | 1100–1708 (range due to surface deformation effects) | Gebhart et al. (1988, RECALLED): "approximately 1100 for moderate constraints"; higher values account for surface-tension effects. |
| Rigid-rigid surfaces (both plates solid) | 1707.8–1708 | VERIFIED by direct calculation and standard reference: the exact value (1707.76) for perfectly rigid plates with no slip. Incropera et al. (2013, RECALLED) round to 1708 in practice. This is the most common laboratory case. |

### Transition to turbulence in natural convection

The Richardson and Rayleigh numbers interact to determine whether turbulent 
modeling is needed. The following thresholds are empirically established but 
geometry-dependent:

| Configuration | Laminar Threshold | Turbulent Onset | Source |
|------|------|------|------|
| Vertical flat plate, natural convection (Ra-based) | Ra < 10⁹ | Ra > 10⁹ | Incropera et al. (2013, RECALLED); Gebhart et al. (1988, RECALLED): the transition is spread rather than sharp and accelerates with surface roughness. |
| Horizontal cylinder, natural convection (Ra-based) | Ra < 10⁷ | Ra > 10⁷ | Incropera et al. (2013, RECALLED): empirical correlations given separately for the two regimes; the higher threshold for cylinders vs. plates reflects geometry. |
| Vertical channel (parallel plates), natural convection (modified Ra) | Ra_mod < 10⁴ | Ra_mod ~ 10⁴–10⁵ | Incropera et al. (2013, RECALLED): uses aspect ratio A = L/D (height-to-gap ratio) as Ra_mod = Ra * (D/L)^(4/5); higher aspect ratios shift the threshold lower. |
| Mixed convection (Ri ~ 0.1–10) | Typically laminar below combined Ra*Ri < 10⁵ | Empirical, case-specific | Gebhart et al. (1988, RECALLED): "no universal criterion; geometry-specific measurements required." Rule of thumb: if either natural or forced convection alone would be laminar, the mixed regime is often laminar unless Ri ~ 1 and both are independently turbulent. |

**Caveat on turbulence onset:** The Rayleigh thresholds cited above (10⁹ for 
plates, 10⁷ for cylinders) are best-fit values over experimental data, not 
sharp transitions. The actual onset occurs gradually over a Ra range of roughly 
0.5–1.5 times the tabulated value, depending on enclosure, boundary roughness, 
and initial conditions. Solver-level turbulence-model switching should use 
Ra thresholds as triggers for *when to validate* against a laminar baseline, 
not as hard cutoffs.

### Relationships and derived quantities

The Richardson and Rayleigh numbers are not independent; they relate the natural 
and forced convection measures:

| Relationship | Derivation | Use |
|------|------|------|
| Ri = Gr / Re² | Direct from definitions: Gr = (g*β*ΔT*L³)/ν², Re = (U*L)/ν, so Ri = Gr*ν²/((U*L)/ν)² = Gr/Re² | Mixed-convection classification without explicit Re and Gr; direct comparison of driving-force magnitudes. |
| Ra = Gr * Pr | Ra = (g*β*ΔT*L³)/(ν*α) and Gr*Pr = ((g*β*ΔT*L³)/ν²) * (ν/α) = (g*β*ΔT*L³)/(ν*α) | Establishes that natural-convection strength (Ra) couples Gr with the material's thermal diffusivity via Pr. |
| Ra = Ri * Re² * Pr | Follows from Ri = Ra/(Re²*Pr) by algebraic rearrangement | Expresses Rayleigh as a product of forced (Re), mixed (Ri), and material (Pr) effects; useful for examining sensitivity to each term. |
| Gr / Re² = Ra / (Re² * Pr) | Both equal Ri by construction | Confirms equivalence between the two Richardson forms; either can be used depending on which dimensional groups are immediately available. |

### Solver selection based on convection regime

| Regime Classification | Solver Characteristics | Source/Basis |
|------|------|------|
| Forced convection (Ri << 0.1) | Steady solver (simpleFoam, SIMPLE algorithm) generally adequate; PISO only if transient buoyancy-driven oscillations expected. Turbulence modeling chosen from forced-flow correlations without natural-convection corrections. | White (2011, RECALLED); Incropera et al. (2013, RECALLED): forced convection is inherently steady at moderate Re unless vortex shedding or separation is present. |
| Mixed convection (0.1 < Ri < 10) | Steady solver can diverge if natural convection introduces buoyancy-driven oscillations; unsteady solver (pimpleFoam) often safer despite cost. Turbulence model performance degrades; independent validation required. | Gebhart et al. (1988, RECALLED): "mixed convection introduces interaction effects not captured by treating the two modes independently." Standard RANS closures are calibrated to one dominant mode. |
| Natural convection (Ri >> 10) | Steady solver can diverge if Ra > 10⁸ or if the flow has any enclosed recirculation; unsteady solver preferred. Laminar-to-turbulent transition in Ra range 10⁷–10⁹ demands either laminar assumption with post-check or turbulence model activated at the appropriate Ra threshold. | Gebhart et al. (1988, RECALLED); Incropera et al. (2013, RECALLED): natural convection is intrinsically transient at high Ra (Rayleigh-Benard convection, vortex formation, oscillating plumes). |

## Open innovation directions (Numericist backlog)

- GCI-based discretization-error channel alongside the GP epistemic layer.
- Acquisition-driven sampling: spend the next cycle's budget where posterior
  spread is largest (the mission layer already flags thin directions).
- Closure-model registry with validity envelopes (feeds the Chief Researcher
  approval protocol in demo Part 2).
- Unsteady metrics: time-averaged coefficients + shedding amplitude/Strouhal
  as first-class mission metrics.

## Buoyant steady solves: convergence, closure and Boussinesq validity (added 2026-08-17, F14 rung K1a)

Everything in this section is **VERIFIED by measurement on this repository's own
cases** unless the row says otherwise. Where a value is standard in the field
but was not read from a source document here, it is marked RECALLED, following
the citation standard of the convection regime map above. Solver throughout:
`buoyantBoussinesqSimpleFoam`, OpenFOAM v2606; case class: sealed
two-dimensional differentially heated cavity, laminar, Ra 1e3 to 1e6.

### 1. `residualControl` is not a convergence criterion for a graded quantity

| Fact | Value | Basis |
|---|---|---|
| Rate at which an under-relaxed SIMPLE outer loop moves the smooth, domain-scale modes | falls off like **1/N²** with mesh count per direction | RECALLED as theory; **VERIFIED in consequence** — see the next two rows |
| Iteration factor to reach the same distance to the fixed point on a mesh refined 2× | about **4×** | VERIFIED, F14 K0c: every coarse mesh settled and every fine mesh did not, under identical relaxation and identical residual targets |
| Drift in the graded Nusselt number on fine meshes that **had met** `residualControl` | **2.19 %, 3.98 %, 4.67 %**, and **14.65 %** on a g = 0 twin, against a 0.02 % criterion | VERIFIED, `docs/campaigns/F14-cooling-ladder/K0c_runs/continue_cases.sh` docstring and `K0c_RESULTS.md` |
| Consequence if graded on residuals | at Ra = 1e3 the **fine** mesh reports **further** from the benchmark than its own **coarse** mesh: 1.0940 against 1.1191 | VERIFIED, same source |
| Clean demonstration | g = 0 twin, exact answer Nu = 1: read **1.328** after 3000 iterations with the core near its initial uniform 300 K, residuals nominal | VERIFIED |

**Practice.** Gate the peak-to-peak spread of the graded quantity over a
**fixed** iteration window, read from the running solver's own in-pass function
objects. Governed values in `docs/physics_rules.yaml` block `thermal`:
0.02 % over 400 outer iterations sampled every 50 (9 samples), refusing to score
below 9 samples. Implemented as `classify_monitor()` /
`--monitor-regex` in `scripts/check_convergence.py`.

Two alternatives are **refused**, both for measured reasons:
- **Endpoint difference over the window** — aliases against a case approaching
  steady state as a decaying oscillation. VERIFIED: one K0c case oscillates with
  a period of about 400 outer iterations, the same length as the window.
- **A fraction of the run (e.g. last quarter)** — loosens as a run is extended.
  VERIFIED: on `Ra1e3_m64` the last-quarter statistic reads **2.164275 %** where
  the fixed-window spread reads **0.002813 %**.

### 2. Boundary heat balance on a sealed case is very nearly an identity

| Fact | Value | Basis |
|---|---|---|
| Boundary imbalance on a sealed impermeable steady case at **iteration 10** | **0.0128 %** | VERIFIED, F14 K0b (capability rung) |
| Same, maximum over the whole run | never above **0.13 %** | VERIFIED, same |
| Converged sealed no-source case | **0.000000005 %**, net leak −5.960965e-14 W against 1.298878e-03 W of boundary traffic | VERIFIED, F14 K1c control `KC0_nosource` |
| Why | `div(phi,T)` integrates to zero over the domain (conservative flux, impermeable walls), so the boundary conduction terms are forced to sum to zero **at every iteration, converged or not** | VERIFIED by the numbers above; derivation standard |

**Practice.** A closure figure at or under tolerance on a sealed case is **not**
evidence the physics is right. It is reported and never counted as evidence for
a rung. `scripts/heat_balance.py` stamps `closure_is_identity_class` and says so
in words; `docs/physics_rules.yaml` carries
`heat_balance_closure_is_evidence_on_sealed_case: false`.

**What the check IS worth, narrowly:** wrong fluid properties, wrong patch
areas, a wrong sign convention, a patch omitted from the sum, any unaccounted
volumetric source or sink, and — the one regime where the balance is genuinely
not an identity — any domain with through-flow, where the advective enthalpy
flux is an independent contribution. ~~That advective path is **UNVALIDATED** in
this lab and is refused with exit 2 unless explicitly allowed.~~
**Superseded 2026-08-17 at rung KV1: the advective path is implemented and
validated. See §8 below.** The exit-2 refusal is retained deliberately, so the
struck sentence's second clause still holds. Note also that the struck sentence
overstated the old state in the same direction K2a §8 did: before KV1 the path
was not merely unvalidated, it was **not computed at all**, while the printed
report positively vouched for open-case ledgers as "a genuine constraint here".

### 3. Planted-source recovery IS convergence-sensitive — the contrast that makes §2 readable

Same script, same case, same field. Plant +5.000000000e-03 W as a uniform
volumetric source and audit at increasing iteration counts. VERIFIED, F14 K1c
control `KC4_identity_probe`:

| iteration | T equation initial residual | recovery error |
| ---: | ---: | ---: |
| 100 | 4.511e-03 | −24.139 % |
| 300 | 8.456e-05 | −0.66860 % |
| 500 | 2.101e-06 | −1.6706e-02 % |
| 1000 | 2.218e-10 | −1.7593e-06 % |
| 4000 | 3.486e-12 | **+2.3876e-09 %** |

The error tracks the residual across **seven decades**. This is the operational
test for whether any gate quantity is a measurement or an identity: evaluate it
on a deliberately unconverged field. If it is already at its final value, it is
an identity.

### 4. Detection floor of a closure check

| Fact | Value | Basis |
|---|---|---|
| Smallest source detectable at a 0.5 % tolerance on this case class | about **6.5 µW**, i.e. tolerance × boundary traffic (1.30e-03 W) | VERIFIED, F14 K1c: a planted 1.000e-05 W source gives 0.772869 % (FAIL); a planted 5.000e-06 W source gives 0.385690 % (PASS) |
| Linearity of the reported imbalance in the planted defect | plant ratio 2.000000 → measured imbalance ratio **2.003862** | VERIFIED, same pair |

**Practice.** A passing closure number does not mean there is no unaccounted
source; it means there is none larger than tolerance × boundary traffic. Quote
that floor beside the pass.

### 5. Boussinesq validity, in kelvin

| Fact | Value | Basis |
|---|---|---|
| Validity condition | β·ΔT ≪ 1; the working limit used here is **0.1** | RECALLED (standard statement of the approximation); the limit value is a lab convention recorded in `docs/physics_rules.yaml` |
| β for an ideal gas | 1/T_ref | VERIFIED by derivation |
| ΔT at which β·ΔT reaches 0.1, at T_ref = 300 K | **30.0000 K exactly** (30.000003 K at the cases' rounded β = 3.333333e-03 1/K) | VERIFIED by calculation from the case dictionaries |
| β·ΔT at ΔT = 40 K | **0.1333** | VERIFIED by calculation |
| Measured on the F14 capability rung K0a (ΔT = 10 K) | **3.333333e-02** — satisfied, by a factor of 3 | VERIFIED, `constant/transportProperties` and `0.orig/T` of that case |

**Practice, and this is the consequential row.** The limit is a **warning**, not
a hard gate: a violation does not make the arithmetic wrong, it means the
momentum equation being solved is no longer the one the problem has. **Any
buoyant rung run at a realistic temperature rise crosses this line**, because
30 K is inside the range these problems produce. Such a rung must either justify
Boussinesq explicitly or move to a compressible thermo solver.
`scripts/heat_balance.py` prints β·ΔT, the limit, and the ΔT at which the limit
is reached, on every run.

### 6. Turbulent Prandtl number

| Fact | Value | Basis |
|---|---|---|
| Relation | alphat = nut / Prt, so Prt sets every wall heat flux a turbulent thermal solve reports | VERIFIED by derivation |
| Value used across this lab's thermal cases | **0.85**, declared in each case's `constant/transportProperties` | VERIFIED by reading the case dictionaries |
| Status | a **modelling choice**, not a measured value. No case in this lab has measured or varied it | VERIFIED — no turbulent thermal case has been run |

**Practice.** Recorded per solve with its provenance (case dictionary, or the
`thermal.turbulent_prandtl_default` fallback), and recorded even on laminar
solves where alphat is identically zero and Prt does not enter the answer. A
reader cannot reconstruct it from anything else in a report, and "it did not
matter here" is a fact about this case, not the next one.

### 7. Two traps in the auditor itself, both measured

| Trap | Measurement | Rule |
|---|---|---|
| `grad(T)` written to disk and read back loses the `snGrad` boundary correction | integral n·grad(T) dA = 0.595629494 recomputed in-pass against **0.377856775** read back — **−36.6 %** | VERIFIED, F14 K0a. Recompute the gradient in the **same** postProcess pass as the surface integral. |
| An imbalance ratio whose denominator is floating-point residue | one adiabatic patch carrying **+7.94e-24 W** produced a reported imbalance of **6.25e+22 %** | VERIFIED, F14 K1c. Test that the denominator is the quantity the ratio claims to be measured against, not merely that it is non-zero. |

## Rack-row facility modelling (F14 rungs K2a/K2c, 2026-08-17)

Recorded at specification time, zero compute. Tier labels as elsewhere in this
file; READ IN SOURCE means the OpenFOAM v2606 source installed at
`/usr/lib/openfoam/openfoam2606/` was read this session at the cited path.

### 1. The rack/CRAC face-pair coupling exists as stock boundary conditions

The "rack = inlet face + outlet face with ΔT = P/(ṁ·cp)" abstraction needs no
coded BC in OpenFOAM v2606; both halves exist in the tree (READ IN SOURCE):

- **Boussinesq solvers** (T is a plain transported field, no thermo package):
  `outletMappedUniformInlet`
  (`src/finiteVolume/fields/fvPatchFields/derived/outletMappedUniformInlet/`)
  imposes φ_inlet = Σ f_i·φ_outlet,i + φ_offset,i, area-weighted average over
  the named outlet patches (`gWeightedAverage` over `magSf`). With the face
  pair's ṁ pinned by `flowRateOutletVelocity`/`flowRateInletVelocity`, setting
  `offset` = ΔT = P/(ṁ·cp) implements the abstraction with **no cp in the
  case** — ΔT is the primitive and P is derived for reporting only.
- **Compressible solvers** (`buoyantSimpleFoam` class):
  `outletMappedUniformInletHeatAddition`
  (`src/thermoTools/derivedFvPatchFields/outletMappedUniformInletHeatAddition/`)
  implements the formula literally: `operator==(clamp(averageOutletField +
  Q/totalPhiCp, TMin_, TMax_))` with `totalPhiCp = sumOutletPatchPhi *
  gAverage(Cpf)` from the thermo package — Q in watts is the primitive.
  **Trap, read in the same source: the TMin/TMax clamp (defaults 0/5000 K) is
  a silent limiter** — a runaway recirculation sits invisibly on the clamp
  unless TMax is set far above the physics-rules admissibility line and the
  domain span is monitored independently.

Supporting stock pieces, same tier: `flowRateOutletVelocity` (the "outlet with
imposed flow" half of the pair), `fixedFluxPressure`, and the incompressible
`alphatJayatillekeWallFunction`
(`src/TurbulenceModels/incompressible/.../alphatWallFunctions/`).

### 2. Recirculation amplifies the Boussinesq span beyond the rack ΔT

Derived (VERIFIED by calculation, three lines of steady mixing algebra): if a
fraction r of a rack's inlet air is recirculated exhaust, the rack-outlet
excess over supply is θ_out = ΔT_rack/(1−r), so the **domain** temperature
span the `thermal.boussinesq_beta_dT_max` limit binds is not ΔT_rack but at
least ΔT_rack/(1−r). At r = 1/3 a 20 K rack already puts 30.0 K in the domain
— the exact limit at TRef 300. Consequence, written into the K2a spec: the
a-priori parameter screen on ΔT_rack is necessary but not sufficient, and a
`fieldMinMax` span check on the solved field is mandatory on every Boussinesq
run of this module class.

### 3. Measured cell-iteration throughput of the lab's buoyant steady solver

From the committed K0c logs and COST.txt files (VERIFIED, this repo's own
runs; single core, `buoyantBoussinesqSimpleFoam`, 2D laminar, SIMPLE):
4.6e5 / 5.6e5 / 3.6e5 / 2.7e5 cell·iterations per core-second at 4.1k / 4.1k /
16.4k / 36.9k cells respectively — throughput falls with case size, so plan on
the large-case end. Iterations to meet the S13 monitor criterion ran 4,000–
7,900. The K2a cost estimate derates the 2.7e5 figure by an **assumed** ÷2.7
for 3D + SST (three velocity components, two turbulence equations, ~50% more
faces per cell) to a planning rate of 1.0e5 cell·iter/(core·s); the derate is
an engineering assumption awaiting its first 3D measurement, and every figure
built on it is labelled ESTIMATE.

### 4. What the one obtained rack-row facility primary establishes

Wibron, Ljung, Lundström (2018), *Energies* 11(3):644, READ IN FULL
(`docs/papers/wibron_ljung_lundstrom_2018_en11030644.{pdf,txt}`, CC-BY,
SHA-256 in the K2c spec; fetched via the Luleå DiVA repository after the
publisher host returned 403 to this box):

- The face-pair ("black box") rack abstraction with ΔT = q/(ṁ·c_p) — their
  Eq. (9) — reproduces measured rack-front temperatures within the ±1 °C
  sensor accuracy on all ten racks of a real hard-floor module, and is
  documented approximate at rack-back/near-face scale (2 of 10 back sensors
  outside bars; near-rack velocity profiles recover only 10–15 cm off the
  face, their Fig. 8). *Applies*: gate design for any face-pair module —
  grade room-level quantities, REPORT-ONLY the near-face ones (L-97).
- Steady RANS of the module class failed to converge in their hands
  ("difficulties converging due to fluctuations"); they used transient
  averaging over 600 s. *Applies*: cost planning and monitor expectations for
  any K2b solve.
- k–ε mispredicts the above-rack low-velocity regions; RSM and DES agree
  closely (their §4.4). k–ω SST is untested on this class in that paper.
- Grid-size floor, tier SECONDARY (their p. 10, attributing VanGilder et al.,
  which is NOT OBTAINED): results change little below ~15.2 cm cells but are
  not fully independent even at 2.5 cm.

### 5. Correction record for the convection regime map above (2026-08-17)

Four cells of the regime-map tables carried the same algebra misprint family;
all four are corrected in place this date (VERIFIED by calculation — the
section's own criterion for independently derivable statements): Ra
composition read `(g·β·ΔT·L³·α)/ν³` (that is Gr/Pr) where Gr·Pr =
`(g·β·ΔT·L³)/(ν·α)`; the Richardson alternate form and its two dependent
relationship rows read `Ri = Ra/(Re·Pr)` where dimensional consistency with
Ri = Gr/Re² requires `Ri = Ra/(Re²·Pr)`. Definitions of Gr, Pr, Re themselves
were correct. Blast radius, measured rather than assumed: `git grep` at HEAD
finds the misprinted forms nowhere outside this file, and the one regime table
computed from this map in the same commit window (F14 K2a §5) derives from the
Gr/Re/Pr definitions directly and is unaffected.

## Digitizing a published figure as a measurement (F14 rung K2c-A, 2026-08-17)

Recorded at addendum time, zero compute, no solver launched. Everything in this
section is **VERIFIED by measurement on this repository's own copy of the
source** unless a row says otherwise; the source is
`docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf`, SHA-256
`4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77`, and every
figure below is reproduced by
`python3 docs/campaigns/F14-cooling-ladder/digitize_wibron2018.py`.

### 1. Most journal plots are vector, and a vector plot is not a picture of the data

| Fact | Value | Basis |
|---|---|---|
| Fraction of this paper's figures that carry their data as PDF path operators rather than pixels | **4 of 10** figures, and all four of the ones a gate would grade (3, 6, 7, 8) | VERIFIED, F14 K2c-A: `pdfimages -list` reports no image object on pages 7, 10 or 11; pypdf reports `/Subtype /Form` for all seven objects on those pages. The six raster figures are the geometry views and the contour planes |
| What a Form XObject's content stream contains for a bar chart | the bar as an `re` operator whose height IS the value | VERIFIED, same |
| What it contains for a scatter marker | a closed 8-segment polygon (a circle drawn as an octagon), whose centre is exactly the mean of the vertex extrema | VERIFIED, same. Marker radius 30 raw units, vertices at 30 cos(45k degrees) |
| What it contains for a computed profile | a polyline, here 500 vertices sampled uniformly in the ordinate | VERIFIED, same |
| Coordinate precision written into the stream | 6 significant figures | VERIFIED, same. At this paper's scales that is 6.5e-5 deg C and 7e-6 m/s, i.e. below every other error |
| Axis calibration error from a least-squares fit of tick position against tick label value | **4.9e-7 deg C** on a 9-tick temperature axis; **5.8e-9 m/s** on a 4-tick velocity axis | VERIFIED, same. Tick marks are stroked segments planted on the plot box, so the calibration is read from geometry, not from label glyph positions |

**Consequence, and it is the whole reason this matters:** the usual dominant
digitisation errors (pixel-to-data scale, curve thickness, reader repeatability)
are **identically zero** on a vector figure, because there is no pixel stage, the
paths carry their own centrelines, and the extraction is deterministic. What is
left is primitive placement, and that is measurable. *Applies*: any literature
reference whose numbers live in figures. Check `/Subtype` before writing a pixel
digitiser.

### 2. The error that replaces them: marker placement, and it must be measured across figures

| Fact | Value | Basis |
|---|---|---|
| Experimental-marker centre coordinates in this paper's Figure 7 | every one of 34 coordinates an exact multiple of 5 raw units | VERIFIED, F14 K2c-A. The exporter quantised marker positions; polyline vertices in the same stream are not quantised |
| Disagreement between the same experimental point digitised from two different figures on different axis limits | **0.0060 m/s maximum, 0.0037 m/s rms** over 6 common points; 0.0043 m in height | VERIFIED, F14 K2c-A, control C6 |
| Disagreement between the same computed CURVE digitised from two different figures | **1.2e-5 m/s** maximum over 500 vertices | VERIFIED, F14 K2c-A, control C5 |

Markers are three orders of magnitude worse than curves in the same document.
*Applies*: quote a marker-derived reference at the cross-figure bound, not at the
stream's coordinate precision. Where a paper plots the same data twice, that
redundancy is the instrument that measures the error; where it does not, the
error is unmeasured and the reading is digitized-uncontrolled.

### 3. Three kinds of control, and only one of them establishes accuracy

| Control kind | Example on this primary | What it can and cannot catch |
|---|---|---|
| **Internal redundancy** | Figure 6 bar height against the midpoint of its own error-bar caps: agree to **6.5e-5 deg C** | Catches an extraction bug. **Cannot catch a systematic error common to both encodings**, so it must never be reported as the digitisation accuracy |
| **Cross-figure identity** | the fine-grid RSM profile plotted as both Figure 3a and Figure 7a: **1.2e-5 m/s** over 500 vertices | Catches calibration error, since the two panels have different axis limits. Also identifies which unlabelled grey curve is which model |
| **Text-stated value recovered from a figure** | the plus or minus 1 deg C sensor accuracy drawn as Figure 6's error bars (**recovered to 1.3e-7 deg C**); the 0.0521 m/s GCI band drawn in Figure 3b (**0.052073, error 2.7e-5**); the 3.150 m room height as Figure 7's height-axis limit (**error 2.9e-6 m**) | **This is the one that establishes accuracy**, because the reference did not come out of the same figure |

A fourth kind is worth naming because it caught the most: **a relation the paper
states in prose with tabulated inputs.** Here, Eq. (9)'s dT = q/(m_dot c_p) with
the Table 2 loads and face velocities forces (dT)(v)/q to be one constant across
racks, and it was, to **0.202 %** over 8 racks, which is **0.029 K** on a 13 K
rise. That residual is 460 times the internal redundancy figure, and it is the
one to adopt: it is the only control that carries the paper's own modelling
detail as well as the reading error. *Applies*: adopt the largest
control-established bound, not the flattering one.

### 4. The legend key is a data point unless you exclude it, and a box test is not enough

VERIFIED, F14 K2c-A, by having it happen: this paper's Figure 7 puts its legend
above the panels, where a plot-box membership test excludes it; Figure 8 puts its
legend **inside** the axes box, where the same test admits the legend's own
marker as a fourth measurement at 1.32 m/s and 0.19 m. The cross-figure control
of item 2 then read **0.84 m/s** instead of 0.0060, an inflation of 140 times,
and that is the only reason it was noticed. Two further traps in the same figure
family: a legend entry drawn as a marker has **no line sample**, so the bounding
box of the line keys misses it by one row pitch; and the legend text is emitted
into the stream **shifted by one entry** relative to the swatches, so reading
label-follows-swatch in stream order mislabels every curve. *Applies*: every
figure extractor. The control that caught it was cross-figure agreement, not
inspection.

### 5. What no control on a figure can reach

**Whether the value the authors plotted equals the value they measured.**
Rounding, averaging or transcription between instrument and figure is invisible
to all of the above. RECALLED as a general point, VERIFIED as a live one here:
this paper's Figure 6b back-side CFD bar for rack R6 implies a heat load near
5030 W under its own Eq. (9) and its own Table 2 flow, against the 1762 W Table 2
records for that rack, a residual of **9.1 K** where the other eight racks close
to 0.03 K. Something in that pairing is wrong and no reading of the figure can
say which. *Applies*: state the reading uncertainty as the uncertainty of reading
the figure, and say so in those words.

### 6. What the Wibron 2018 facility numbers are, once digitized

DIGITIZED, tier as recorded in `docs/campaigns/F14-cooling-ladder/K2c_DIGITIZATION_ADDENDUM.md` §4:

- Rack-front temperature at the 1.09 m sensor point, measured, **20.07 to 20.25
  deg C** across the 8 racks that carry a sensor, against CRAC supply of 19.7 to
  20.0 deg C. The whole cold aisle sat within 0.6 K of supply.
- Rack-back temperature, measured, **33.70 to 35.97 deg C** across the 7 racks
  that carry a sensor.
- Measured velocities at the five profile locations, **0.14 to 0.96 m/s**, all
  inside the anemometer's 0.05 to 1 m/s accuracy band.
- **Five sensor values are absent from the paper's own figures**: R5 and R6 on
  the front, R1, R5 and R6 on the back. The paper does not remark on it. A gate
  written from the paper's prose alone would have specified 10 racks and 20
  comparisons where only 15 exist.

## Open-domain thermal solves: the advective enthalpy flux and what its closure is worth (added 2026-08-17, F14 rung KV1)

Everything in this section is **VERIFIED by measurement on this repository's own
cases** unless the row says otherwise; RECALLED marks a value standard in the
field but not read from a source document here, following the citation standard
above. Solver: `buoyantBoussinesqSimpleFoam`, OpenFOAM v2606. Case class: a
two-dimensional straight duct, 0.30 x 0.05 m, 60 x 20 cells, laminar forced
convection at Re_H = 157, g = 0, one inlet and one outlet. **Three cases. That
is the entire population of open-domain thermal solves this lab has run, and no
rate or tolerance below is claimed to transfer beyond it.**

### 1. Computing the term against the solver's own flux, not against a normal you build

| Fact | Value | Basis |
|---|---|---|
| The advective boundary term the solver actually assembled | `sum_f T_f . phi_f` over the patch faces, with `phi` the conservative face flux and `T_f` the boundary field value | **VERIFIED** — reproduced to 12 figures by the plant recovery below |
| How to get it out of OpenFOAM | `surfaceFieldValue`, `operation weightedSum`, `fields (phi)`, `weightField T` on the patch | **VERIFIED**, v2606 |
| Why the weight lands on the boundary values and not on cell values | for a `volScalarField` on a patch, `getFieldValues` routes through `filterField`, which returns the patch's **boundaryField** | **VERIFIED** by reading `surfaceFieldValueTemplates.C` and confirmed numerically: the inlet's flux-weighted mean face temperature reads 305.0000000000002 K against a `fixedValue` of 305.0 |
| Building the flux geometrically instead, as `Sf & U_f` | not done, and not equivalent — it is a different number from the one `div(phi,T)` used | **RECALLED** as reasoning; not measured here |

### 2. `surfaceFieldValue` FAILS OPEN on a weighted operation, silently

| Fact | Value | Basis |
|---|---|---|
| Behaviour when `canWeight()` is false | falls through to the **unweighted** `gSum(values)` with nothing on stderr | **VERIFIED** — `surfaceFieldValueTemplates.C`, `case opWeightedSum`, the `else // Unweighted form` branch |
| Size of the resulting error | the advective term comes out smaller by a factor of the absolute temperature, so ~300x on air at 300 K | **VERIFIED** by mutation M5 |
| The invariant that catches it | `integral T phi / integral phi` is a flux-weighted mean FACE temperature and must lie inside the field's own T range. If the weight was dropped it is **exactly 1.0** | **VERIFIED** — the mutated run reports `1.000000e+00 K` against a field range of 304.967874..314.438667 K |

**Practice.** Never take a weighted `surfaceFieldValue` result on trust. Compute
the unweighted companion in the same pass and check the ratio against a physical
range. `scripts/heat_balance.py` refuses rather than reporting when it is out.

### 3. The plant recovery on an OPEN case

| Fact | Value | Basis |
|---|---|---|
| Planted volumetric source, `scalarSemiImplicitSource`, `volumeMode absolute` | 4.275222401345e-06 K.m3/s = **5.000e-03 W** at rho.cp = 1169.5298 J/m3/K | **VERIFIED**; identical to K0c C3's plant because the fluid is identical |
| Recovered net boundary flux | **-4.999999998798e-03 W**, error **+2.403e-08 %** | **VERIFIED**, against the governed 0.1 % |
| The same field set with the advective term ABSENT (conduction only) | -7.448816e-06 W — wrong by **99.85 %** | **VERIFIED** by re-running the pre-repair auditor |
| Comparison: K0c C3's SEALED planted-source recovery | -4.999996460e-03 W, error -7.08e-05 % | prior measurement, K0c |

The open-case recovery is three orders of magnitude tighter than the sealed one.
No mechanism is claimed for that; it is one case against one case.

### 4. The open-case closure IS convergence-sensitive — it is not a second identity

The same duct, one heated wall, no source, audited at eleven iteration counts
against the T equation's own initial residual read from the solver log:

| iteration | T initial residual | imbalance | exit |
|---:|---:|---:|---:|
| 20 | 8.011e-03 | **20.881167 %** | 1 |
| 40 | 3.166e-03 | 9.856046 % | 1 |
| 60 | 1.002e-03 | 3.184486 % | 1 |
| 80 | 1.886e-04 | 0.593174 % | 1 |
| 100 | 2.459e-05 | 0.069250 % | 0 |
| 120 | 5.150e-07 | 0.000889 % | 0 |
| 140 | 8.819e-09 | 0.000009 % | 0 |
| 201 | 4.346e-12 | 0.000000 % | 0 |

**VERIFIED.** Nine decades, and the exit code flips 1 -> 0 between iteration 80
and 100 where the percentage crosses the governed 0.5 % band. Set beside the
SEALED case, which reads 0.0128 % at iteration 10 and never rises above 0.13 %
at any iteration: the sealed number never approaches its own gate and the open
one crosses it. **That contrast is the evidence, not the argument.**

### 5. A term can be computed, correct, and still unfalsifiable on the wrong case

| Fact | Value | Basis |
|---|---|---|
| Adiabatic duct, inlet 305 K, no source | converges to exactly 305 K everywhere; `Q_adv(inlet)` = +0.146191 W, `Q_adv(outlet)` = -0.146191 W, **advective sum identically zero** | **VERIFIED** |
| Its closure | 0.0000 %, net 1.843e-12 W, exit 0 | **VERIFIED** |
| Its closure under a SIGN FLIP of the whole advective term | 0.0000 %, exit 0 — unchanged | **VERIFIED** |
| Its closure under the term SCALED BY TWO | 0.0000 %, exit 0 — unchanged | **VERIFIED** |
| The same mutations on a duct with a HEATED WALL (conduction in +0.0617726 W, advection out -0.0617726 W) | sign flipped **45.6605 %**, scaled by two **17.4433 %**, one open patch dropped **100.0000 %** — all FAIL | **VERIFIED** |

**Practice.** A validation case must have the term under test contributing a
NON-ZERO, non-self-cancelling amount to the graded quantity. Two independent
terms that must cancel each other is the shape that works; one term that cancels
against itself is the shape that does not.

### 6. The datum: invariant in the numerator, not in the denominator

| Fact | Value | Basis |
|---|---|---|
| Effect of the enthalpy datum on the NET | cancels exactly when boundary mass balances; here to within 1e-10 W | **VERIFIED** |
| Effect on the imbalance DENOMINATOR, `sum(Q > 0)` | 0.2079685 W at the case's `TRef` against **8.979442 W** at a 0 K datum — a factor of **43.2** | **VERIFIED** |
| What that does to a fixed 0.5 % tolerance | slack goes from 1.04e-03 W to **4.49e-02 W** at an unchanged printed threshold | **VERIFIED** |
| Whether any closure control detects it | **no.** The case still passes under a 0 K datum. It is the one advective error closure cannot catch | **VERIFIED** by mutation M4 |
| What one kelvin of datum error is worth in the ledger | `rho.cp.(net volumetric flux)`; zero iff mass balances, and reported per run as `advective.datum_sensitivity_W_per_K` | **VERIFIED** |

**Practice.** An enthalpy ledger over a boundary is meaningful only to the extent
that boundary conserves mass, and its PERCENTAGE is meaningful only relative to a
stated datum. Both are now governed: `heat_balance_advective_datum: TRef` and
`heat_balance_open_case_gates_mass_imbalance: true` in
`docs/physics_rules.yaml`, and an open case whose mass imbalance exceeds the same
tolerance is reported `ledger_complete: false` and cannot pass.

### 7. Regime and case-design notes for the next open thermal case

| Fact | Value | Basis |
|---|---|---|
| Inlet held AT the datum | inlet advective term is identically zero, no patch carries heat inward, and the imbalance ratio is UNDEFINED by the P1 rule — the closure cannot be tested at all | **VERIFIED**; this is why KV1's inlet runs at 305 K against a 300 K datum |
| Bulk temperature rise for a planted source | `dT = Q / (mdot.cp)` — 5.000e-03 W at 2.9035e-05 kg/s gives 0.171 K, and the solver's own `outletT` read 305.1830 against a predicted 305.171 | **VERIFIED** |
| Cost of a case in this class | 1200 cells, 201 SIMPLE iterations to `residualControl` 1e-9/1e-10, **0.0081 core-minutes** single core | **VERIFIED**, `KV1_runs/*/COST.txt` |
| `g = 0` on `buoyantBoussinesqSimpleFoam` | runs normally and reduces to forced convection; `Ra` is then reported as n/a rather than zero | **VERIFIED**; precedent K0c C1 |

### 8. What none of this establishes

- **Circulation.** A duct with one inlet and one outlet has no flow structure to
  get wrong. A solve whose flow field is entirely wrong still closes perfectly
  once converged, because closure tests conservation and not where the energy
  travelled. `MONITOR_STANDARD.md` **S16** exists to stop that inference.
- **Turbulent open flow.** `--allow-turbulent` remains uncalibrated.
- **Buoyant open flow.** Every case here runs at g = 0. A buoyant open case
  integrates the advective term against a `phi` the temperature field helped set,
  and nothing here speaks to it either way.
- **Compressible or variable-property flow.** The derivation assumes constant
  `rho` and `cp` throughout.

## Boussinesq validity, measured against a variable-density solver (added 2026-08-18, F14 rung K2e)

`docs/physics_rules.yaml` block `thermal` carries `boussinesq_beta_dT_max: 0.1`.
Until K2e that number was a fence: no rung had measured what crossing it costs.
K2e ran the K0c cavity under `buoyantBoussinesqSimpleFoam` and under stock
`buoyantSimpleFoam` across eleven values of `eps = beta.dT`, at **Ra held fixed
at 1e5**, on a 48²/96² pair. Everything here is **VERIFIED by measurement on
this repository's own cases** unless the row says otherwise. Full result and its
scope limits: `docs/campaigns/F14-cooling-ladder/K2e_RESULTS.md`. **Tier
SOLVER-BACKED: there is no experimental reference and both models could be wrong
together.**

Case class throughout: sealed two-dimensional differentially heated square
cavity, laminar, Ra = 1e5, Pr = 0.71, TRef 300 K, constant `mu` and `k`.

### 1. The divergence is not one number, because the two models separate at different ORDERS

| Fact | Value | Basis |
|---|---|---|
| Divergence of the hot-wall Nusselt number | **D = 6.355 · (beta.dT)^1.968 %**, worst residual 4.65 % over eps 0.05 to 0.40 | **VERIFIED**, F14 K2e, 11-point sweep, both meshes |
| Divergence of the peak horizontal velocity on the vertical mid-plane | **D = 24.91 · (beta.dT)^1.005 %**, worst residual 0.51 % | **VERIFIED**, same |
| Centro-symmetry defect of theta (zero under Boussinesq by construction) | **S_rms = 0.0831 · (beta.dT)^1.002** | **VERIFIED**, same |
| Dimensionless temperature at the cavity centre (zero under Boussinesq) | **theta_c = −0.0343 · (beta.dT)^0.999** | **VERIFIED**, same |
| Why the wall flux is second order and the rest first | the Boussinesq equations are exactly centro-symmetric on this cavity and the variable-density equations are not; the integral wall flux is protected to leading order by that symmetry, the flow structure is not | RECALLED as reasoning; **VERIFIED in consequence** by the four exponents above |
| Where each quantity first exceeds 1 % (Class A) or 0.005 dT (Class B) | `u_max*` at beta.dT ∈ **(0.0333, 0.0500]**; `S_rms` at **(0.0500, 0.0667]**; `theta_c` at **(0.100, 0.150]**; **`Nu_h` at (0.300, 0.400]** | **VERIFIED**, brackets not interpolated |
| At the standing limit `beta.dT = 0.1` exactly, 96² mesh | `Nu_h` **0.063 %**, `u_max*` **2.470 %**, `theta_c` **−0.00327**, `S_rms` **+0.00800** | **VERIFIED** |

**Practice.** A rung graded on **wall heat flux** has roughly a factor of four of
headroom in `beta.dT` beyond the standing 0.1 before it reaches 1 %. A rung
graded on **velocity or flow structure** crosses 1 % at about **half** of it.
Compute the admissible `beta.dT` from the law and the accuracy the rung needs;
do not read one scalar limit and assume it protects the quantity being graded.

### 2. Constructing like-with-like between the two solvers

| Fact | Value | Basis |
|---|---|---|
| Equation of state that makes the comparison a Taylor truncation and not a change of fluid | `equationOfState incompressiblePerfectGas` with fixed `pRef`: rho = pRef/(R.T), so beta_true = 1/T = **3.33333e-03 1/K at 300 K**, exactly the Boussinesq `beta` | **VERIFIED**, and the solver's own `rho min/max` log line matches pRef/(R.T) at the witnessed wall temperatures to 6 decimal places on all 15 cases |
| Why `perfectGas` is the wrong choice for a swept comparison in a SEALED cavity | its thermodynamic pressure moves to conserve mass, shifting rho_ref ~**1.4 %** and Ra ~**2.8 %** at dT = 120 K — the same order as the effect being measured | **VERIFIED** by derivation from ⟨1/T⟩ over the imposed range; `incompressiblePerfectGas` was used instead and holds Ra exactly fixed |
| Holding Ra fixed while sweeping dT | `nu(dT) = sqrt(g.beta.dT.L³.Pr/Ra)`; at dT = 1.088162239 K this returns **1.589461e-05**, K0c's own Ra = 1e5 value | **VERIFIED**, and it is the generator's self-check |
| Consequence, and it is the design's own falsifier | the non-dimensional Boussinesq problem depends only on (Ra, Pr), so its branch of every curve must be FLAT. Measured spread across the whole sweep: **2e-08 to 6e-08 %** on both meshes | **VERIFIED** |
| Measured floor on any residual datum or property mismatch (eps → 0 null test) | **0.097 % on Nu_h, 0.209 % on u_max*, 0.080 % on v_max***, at eps = 0.001 | **VERIFIED**; every separation reported clears it by ≥ 5× |
| Whether the two Nusselt definitions can differ | with `transport const` and constant `Pr`, `k` is constant, so the temperature-gradient Nusselt and the heat-flux Nusselt are the **same number** | **VERIFIED** by construction; there is no definitional choice to make |

### 3. Cost, and what a mesh check is worth

| Fact | Value | Basis |
|---|---|---|
| Cost of this case class, `buoyantBoussinesqSimpleFoam` | 48², 3000 iterations: **~0.14 core-min**; 96², 6000 iterations: **~1.24 core-min** | **VERIFIED**, `K2e_runs/*/COST.txt` |
| Cost of the same case under `buoyantSimpleFoam` | **1.7 to 2.2× the Boussinesq solve** at the same mesh and iteration count | **VERIFIED**, same source |
| Iterations to meet the governed 0.02 % peak-to-peak criterion, 48² | first met between **500** (0.305 %) and **750** (0.000160 %); flat at 0.000002 % from 1000 | **VERIFIED**, pilot solve |
| A divergence that is really discretisation error | `v_max*` (peak vertical velocity, horizontal mid-plane) moved **24 to 26 %** between the 48² and 96² meshes at every eps, while its eps-exponent stayed at 1.02 — right scaling, mesh-dependent amplitude | **VERIFIED**; it was struck from every K2e conclusion, and the five other quantities moved 0.4 to 5.3 % |

### 4. What none of this establishes

- **Nothing about a real gas's `mu(T)` and `k(T)`.** Both were held constant.
  Every coefficient above is a **lower bound** on the non-Boussinesq error.
- **Nothing about which model is right.** There is no experimental reference.
- **Nothing about a rack row.** Two-dimensional, laminar, steady, sealed, one
  Rayleigh number. The **exponents** are the part most likely to transfer,
  because they come from the structure of the expansion; the **coefficients** are
  properties of this case.

## The rack-row module, executed as a 2D slice (F14 rung K2b-pilot, 2026-08-18)

Everything in this block is from `K2b_PILOT_RESULTS.md` and the run tree at
`docs/campaigns/F14-cooling-ladder/K2b_runs/`. Seven single-core
`buoyantBoussinesqSimpleFoam` solves, k-ω SST, 46,400 and 104,400 cells. **This
is a capability rung: none of it is a validation of anything against a
measurement of a real room.**

### 1. `outletMappedUniformInlet` has two branches and the second one drops the offset

| Fact | Value | Basis |
|---|---|---|
| The averaging the BC applies in normal operation | **mass-flux**-weighted: `gSum(outletPhi*outletFld)/sumOutletPhi*fraction + offset` | **VERIFIED**, read in `updateCoeffs()` of `outletMappedUniformInletFvPatchField.txx`, v2606 |
| The condition selecting that branch | `gSum(phi) > SMALL` on the mapped **outlet** patch | **VERIFIED**, same source |
| What the `else` branch does | area-weighted `gWeightedAverage(magSf, outletFld)` **and appends no offset** | **VERIFIED**, same source |
| Consequence | a rack front face that loses net outflow silently hands the rear face the front face's own temperature; a rack adding no heat then reads exactly like a converged rack | **VERIFIED** by construction from the branch above |
| The control against it | `T̄(rack_out) − T̄_ṁ(rack_in)` printed by the running solver; reads ΔT on the live branch and **0 K** on the fallback | **VERIFIED**: −8.33e-05 % error on the converged balanced case (residual is the log's own 10-digit print precision) |
| K2a section 3.3 described the `else` branch as the normal one | corrected here; taking its stated remedy would move the graded quantity **0.403 K = 3.4 % of ΔT_rack** away from what the BC computes | **VERIFIED**, measured on `K2bP_under` |

### 2. The mass-flow-weighted and area-weighted face averages are NOT interchangeable on this geometry

| case | mass-weighted T_in | area-weighted T_in | difference, as % of ΔT_rack |
|---|---:|---:|---:|
| `K2bP_coarse` (contained) | 289.068443 K | 289.155745 K | **−0.73 %** |
| `K2bP_under` (r = 0.30) | 294.185416 K | 293.782445 K | **+3.36 %** |
| `K2bP_C1_g0` (g = 0) | 292.790573 K | 294.742765 K | **−16.27 %** |

**VERIFIED**, all three read from the solvers' own logs. The gap grows with face
non-uniformity, and on the forced-convection twin it reaches a sixth of the rack
rise. Any rack-inlet number quoted from this module class must say which average
it is.

### 3. Recirculation on a 2D slice comes from provisioning imbalance, and the spec's mixing relation holds to sub-percent

| Fact | Value | Basis |
|---|---|---|
| θ_in at balanced tile supply (100 % of rack demand) | **0.0057** — the slice is contained and θ **cannot move** | **VERIFIED**, `K2bP_coarse`, 9,000 iterations |
| θ_in at 70 % tile supply | **0.4321**, θ_out = 1.4326 | **VERIFIED**, `K2bP_under`, 5,000 iterations |
| Recirculated fraction from the solve, r = 1 − 1/θ_out | **0.3020** | **VERIFIED** |
| Independent a-priori prediction, r = (Qv_rack − Qv_tile)/Qv_rack | 0.3000 | **VERIFIED** by arithmetic; agreement **+0.67 %** |
| Effect of switching gravity off at the same provisioning | r falls to **0.2398** (−20.6 %): the measured r is a *thermal* mixing fraction, and without stratification the makeup air is a cooler blend | **VERIFIED**, `K2bP_C1_g0` |

**Design consequence for any later run of this module class.** A balanced,
contained, leak-free slice reports θ ≈ 0 for a reason that is a construction and
not a measurement. Build the recirculation source in deliberately — provisioning
imbalance, row-end effects, leakage — or the recirculation index is dead on
arrival, in the same way KV1b's advective sum was.

### 3b. Passing the scalar Boussinesq limit is not the same as being inside the model

Rung K2e (same day, `K2e_RESULTS.md`) measured that the two models separate at
different ORDERS: peak velocity **first order**, D = 24.91·(beta.dT)^1.005 %,
separating in the bracket beta.dT ∈ (0.0333, 0.0500]; Nusselt number **second
order**, D = 6.355·(beta.dT)^1.968 %. **K2b's graded quantities — theta and T_in
— are of the FIRST-order class** (flow structure), and this module has no wall
heat flux at all: every wall reads exactly 0 W. Measured beta.span on the K2b
cases: 0.0400, 0.0403, 0.0587, 0.0592, 0.0632, 0.0710 — **every case except the
two balanced ones runs past the bracket where K2e measured velocity separation
beginning**. K2e's law does **not** transfer as a number (laminar cavity at
Ra = 1e5 against a turbulent through-flow module at Ra ≈ 3e10) and is not quoted
as one; what transfers is the ordering. **Consequence for the next run of this
module class:** report beta.span against the 0.05 velocity bracket as well as
against the 0.1 scalar limit, or carry a compressible twin at one operating
point. VERIFIED as arithmetic on both rungs' own measured spans.

### 4. The Boussinesq admissibility line is a property of the LAYOUT, not of the rack

`thermal.boussinesq_beta_dT_max` = 0.1 is reached at ΔT_domain = 30.0 K at
TRef 300. With span = ΔT_rack/(1−r):

| measured r | ΔT_rack that puts the span exactly on 30.0 K | Basis |
|---:|---:|---|
| 0.0057 (contained) | **29.83 K** | **VERIFIED**, `K2bP_coarse` |
| 0.2398 (g = 0) | **22.81 K** | **VERIFIED**, `K2bP_C1_g0` |
| 0.3020 (70 % provisioned) | **20.94 K** | **VERIFIED**, `K2bP_under` |
| 0.3327 (70 % + 500 W room plant) | **20.02 K** | **VERIFIED**, `K2bP_C3_plant` |

So K2a's table — ΔT_rack ≤ 20 K admissible a priori, 20–30 K conditional, ≥30 K
refused — survives only just: at r = 0.3020 a 20.0 K rack sits at a 28.65 K span,
**β·span = 0.0955 against a limit of 0.1**, and the whole "conditional" band is
inadmissible. Measured spans, none breached: β·span 0.040228 (`K2bP_coarse`),
0.058756 final and **0.059231 at iteration 2,300** (`K2bP_under`, i.e. the worst
value was **mid-run**, which an end-of-run-only check would have missed), 0.069624
(`K2bP_C3_plant`).

### 5. S13 and the heat-balance closure are independent verdicts, measured failing in both directions

| case @ 5,000 | S13 on T_in (band 0.02 %) | closure (band 0.5 %) |
|---|---|---|
| `K2bP_coarse` | **PASS** 0.00136 % | **FAIL** 0.5244 % |
| `K2bP_under` | **FAIL** 0.34553 % | **PASS** 0.1272 % |

| `K2bP_fine` @ 1,500 | **PASS 0.00000 %** | **FAIL 2.6632 %** |

**VERIFIED**, all read from the same runs. The fine-mesh row is the sharpest: at
1,500 iterations T_in has not moved from its 289.000000 K initial value, so the
peak-to-peak spread is 1.0e-07 K and the criterion returns its best possible
score on a case five times further out of balance than the coarse mesh. On the
same case the offset readback errs by 0.000e+00 and the mass-versus-area
comparison by −0.0001 %, both because the rack face is still uniform — **a
best-possible reading produced by an undeveloped field, not by a converged one.**

Also measured on `K2bP_under`: the
window's **endpoint difference is 0.06764 %, five times smaller than the
peak-to-peak spread of 0.34553 %** — the aliasing `physics_rules.yaml` section 1
describes, now measured on this module class rather than inherited from K0c.
Steady SIMPLE does not converge on the recirculating case; K2a section 5 risk 1
pre-registered exactly that from the K2c primary's own report, and the pilot
reproduced it at 1/15 the cost of the 3D module.

### 6. The open-case closure on this geometry, and the instrument gap it was quoted through

| Fact | Value | Basis |
|---|---|---|
| Closure on `K2bP_under`, iterations 1,000 / 3,000 / 5,000 | 31.0420 % → 3.7812 % → **0.1272 %**, auditor exit flipping 1 → 0 across the 0.5 % band | **VERIFIED** |
| `scripts/heat_balance.py` on any k-ω SST case | **REFUSES, exit 2**, unless `--allow-turbulent`, whose path is uncalibrated and stamps the report UNVALIDATED | **VERIFIED**, measured (alphat max 1.047795e-02 m²/s) |
| KV1, the prerequisite K2a section 8 named for quoting a closure number | a **laminar** rung; it does not cover the turbulent path every K2b case needs | **VERIFIED** by reading KV1_RESULTS.md section 10 |
| What bounds the damage on THIS module | the uncalibrated path touches only the **conductive** rows; all five wall rows read exactly 0 (adiabatic), leaving total conduction at **5.5e-04 %** of the ledger on `K2bP_under` and **6.6e-05 %** on `K2bP_coarse` | **VERIFIED**, per-patch rows in the audit reports |
| What that bound does NOT cover | any variant of this module with a non-adiabatic envelope. K2a section 3.1 already records adiabatic walls as a modelling choice | statement of scope |

### 7. Cost, measured, and why the short probe mis-priced it

| case | cells | iterations | wall s | cell·iter/(core·s) |
|---|---:|---:|---:|---:|
| 100-iteration probe | 46,400 | 100 | 17.24 | **2.70e5** |
| `K2bP_coarse` | 46,400 | 5,000 | 444.76 | **5.22e5** |
| `K2bP_under` | 46,400 | 5,000 | 482.09 | **4.81e5** |
| `K2bP_C2_dT13` | 46,400 | 800 | 73.32 | **5.06e5** |
| `K2bP_C3b_noplant` | 46,400 | 800 | 72.50 | **5.12e5** |
| `K2bP_fine` | 104,400 | 1,500 | 399.37 | **3.92e5** |

**VERIFIED.** The probe is pessimistic by **1.9×** because mesh construction,
`wallDist` and the first matrix assembly are amortised over 100 iterations
instead of 5,000 — **a short probe is the wrong instrument for pricing a long
run.** Note also `K2bP_C1_g0` at 2.24e5, an outlier caused by eight other agents'
solves sharing the machine during that window, so the honest planning figure is
the **4.8e5** the repeated 46,400-cell cases agree on and not the best of them.
The 104,400-cell mesh runs 19 % slower per cell·iteration than the 46,400-cell
mesh — the same throughput-falls-with-case-size trend K0c measured across its
four meshes, and a reason any 3D figure built on 4.8e5 is optimistic.

Against section 3 of the block above: K2a's planning rate for the 3D module is
1.0e5 (2.7e5 derated ÷2.7). The 2D turbulent SST measurement is **4.8e5**, so
the base rate was 1.9× low and only the **derate** remains unmeasured. The
cheapest experiment that settles it is a 3D coarse mesh run for 200 iterations,
≈1.4 core-minutes.

### 8. y+ on the pilot meshes sits BELOW the wall-function band

Measured (`yPlus` function object, in-log, per patch, `K2bP_coarse` at 9,000):
per-patch averages **2.6 to 9.1**, maxima 8.8 to 26.9, minima as low as 0.217,
against K2a section 6's stated target band of **30–300**. At a 12.5 mm cell the
near-wall cell is far too fine for standard wall functions. OpenFOAM's
`nutkWallFunction` and `omegaWallFunction` blend continuously so the solve is
stable and nothing failed, but **the wall treatment the mesh delivers is not the
one the spec names**, and this is measured rather than assumed exactly because
the spec required it to be. On the 1.5×-refined mesh the per-patch averages fall
further, to **3.3–5.4**: **refining moves y+ away from the band, not toward it**,
so this is a wall-treatment decision and not something more cells will fix.

---

## Turbulent buoyant tall cavity, graded against a real experiment (added 2026-08-18, F14 rung K0c-T)

Source: `docs/campaigns/F14-cooling-ladder/K0cT_RESULTS.md` and its run tree.
Reference: ERCOFTAC Classic Collection Case 079, Betts and Bokhari, 2.18 x 0.076 m
tall cavity, Ra 0.86e6 and 1.43e6, PRIMARY DATA FILES in the repository. The
Nusselt reference for this case is **NOT OBTAINED** and every Nusselt figure below
is therefore a MEASUREMENT with nothing to compare it against.

**GATE FAIL: 8 of 18 graded rows.** Read every row below with that on its face.

### 1. Two eddy-viscosity RANS models BRACKET the measured core stratification, and neither is inside the band

| quantity | k-omega SST | LaunderSharmaKE | experiment | band | status |
|---|---:|---:|---:|---:|---|
| core stratification S, Ra 1.43e6 | **0.2353** | **0.0186** | **0.095 +/- 0.02** | 0.05 | **VERIFIED**, both FAIL |
| mid-height peak vertical velocity, m/s | 0.2211 | 0.1267 | 0.190 | 15 % | **VERIFIED**, both FAIL |
| peak LOCATION, mm from the cold plate | 4.35 | 3.77 | 5.0 | 5 mm | **VERIFIED**, both PASS |
| Nu_avg (UNGRADED, no reference) | 5.694 | 7.984 | *not obtained* | — | **VERIFIED** as a measurement only |

The two models differ by **0.217 in S**, which is **1.5x the whole deviation from
the experiment** and **29x the mesh difference**. Identical mesh, boundary
conditions and schemes; they differ in `constant/turbulenceProperties` and in the
k/epsilon versus k/omega field pair and in nothing else.

**What transfers:** on a weakly turbulent buoyant cavity the eddy-viscosity model
choice dominates core stratification, and it dominates it by more than the answer
itself. **Both models get the wall-layer structure right (peak location within
1.5 mm) and the core mixing wrong, in opposite directions.** A single-model
turbulent buoyant-cavity number carries a model uncertainty larger than the
quantity; quote two models or quote none.

**A Nusselt number from this case class carries a 40 % model-to-model spread**
(5.694 against 7.984) with no reference to adjudicate it. **VERIFIED**; it is why
the row is ungraded rather than merely uncertain.

### 2. The buoyancy production term in k is ABSENT from every incompressible OpenFOAM RAS model, and it is NOT the dominant error here

`buoyantKEpsilon` lives only in `src/TurbulenceModels/compressible/RAS/` and
cannot be selected by a solver constructing an `incompressible::turbulenceModel`,
which `buoyantBoussinesqSimpleFoam` does. **VERIFIED** by reading the installed
v2606 source.

Registered before the run: omitting `G_b = -beta g.grad(T) nut/Prt`, a SINK in a
stably stratified core, should bias S LOW. **FALSIFIED, and the disproof is
structural:** S came out HIGH for SST, and the two models — which lack the SAME
term — land on OPPOSITE sides of the reference. A term both are missing cannot
explain a 0.217 difference between them. **VERIFIED.**

### 3. Wall resolution, and an instrument that reports zero because it cannot see the quantity

| fact | value | basis |
|---|---|---|
| y+ at the first cell off the vertical plates, 64x192 mesh, first cell 0.125 mm | **0.189** (Ra 1.43e6), **0.156** (Ra 0.86e6) | **VERIFIED**, computed in the analyser from the solve's own near-wall velocity gradient |
| `yPlus` function object on the same case | **exactly 0 on every patch** | **VERIFIED**. It reports the WALL FUNCTION's own y+, and `nutLowReWallFunction` has none. A zero from a check that cannot see the quantity looks like a perfectly resolved wall |
| nut AT the wall under `nutLowReWallFunction` | **identically 0** on every patch | **VERIFIED** per case as `nut_wall_max` |
| consequence for the wall heat flux | alphaEff at the wall is molecular, uniform, = nu/Pr | **VERIFIED**; it is why the raw-cell and postProcess snGrad paths agree to 1e-06 to 1e-07 |

### 4. Cell Peclet number: the laminar rung's central scheme does NOT carry to a real cavity

The laminar de Vahl Davis rung ran `bounded Gauss linear` on both convection terms
because Pe_cell was below 2 everywhere. On a real 76 mm air cavity the vertical
cell Peclet number at the buoyancy velocity scale is **70 to 165**. **VERIFIED**,
printed at build time. Second-order LIMITED schemes were used instead
(`linearUpwind grad(U)`, `limitedLinear 1`) and the numerical diffusion bounded by
the mesh pair: D_mesh on S is 0.0075, **5 %** of the deviation being explained.

### 5. A COARSER mesh can be the unsteady one

At Ra 1.43e6 the **40x120** mesh never reaches steady state — 140 000 outer
iterations, peak-to-peak spread rising rather than falling — while the **64x192**
mesh converges to a fixed point with final U residuals ~4e-09. **VERIFIED.** The
cause is not established: a different solution branch and a coarse-mesh mode the
fine mesh damps are both live. **RECALLED-as-open, not resolved.**

Practical consequence: **a peak-to-peak convergence criterion evaluated on one
mesh says nothing about the other**, and a mesh pair whose coarse leg oscillates
is still usable if its oscillation amplitude is quoted beside the mesh
difference. Here the coarse leg's own spread on S is 0.000385 against a mesh
difference of 0.0075 — a factor of 19.

### 6. `residualControl` stopped three of nine cases early, and re-running past it changed nothing

T_hi_f, T_lo_f and M_hi_f_LS met their own residual targets at 6688, 6237 and
10 185 iterations. Removing the residual stop and running each to 40 000 moved
the graded S by **0.0000**. **VERIFIED.** The residual stop cost nothing on THIS
rung — and the coarse case in the same rung proves that is a measurement about
these three cases, not a general licence.

### 7. Cost of this case class

| fact | value | basis |
|---|---|---|
| `buoyantBoussinesqSimpleFoam` + kOmegaSST, single core, AMD EPYC 9R14 | **1.73e-06 to 1.84e-06 s per cell per iteration** | **VERIFIED**, two pilots at 4800 and 12288 cells agreeing to 6 % |
| whole nine-case rung: two graded mesh pairs, a model twin, a BC twin, three controls | **95.0 core-minutes** | **VERIFIED**, summed from the cases' own `COST.txt` |
| the two most expensive cases | **16.3 and 16.0 core-minutes**, and both are the coarse cases that were run to 140 000 iterations to establish that they never converge | **VERIFIED** |

**A negative convergence result is not cheap.** A third of this rung's compute
went on proving that two coarse cases do not reach steady state.

### 8. What none of this establishes

- **Nothing about the wall heat transfer.** The Nusselt reference is NOT OBTAINED.
  Every Nusselt figure here is a measurement against nothing.
- **Nothing about a second-moment closure.** Only two eddy-viscosity models were
  run. That the failure is an eddy-viscosity failure is an inference from the two
  of them landing on opposite sides, not a measurement of a third model.
- **Nothing about Prt.** It sat at the standing 0.85 default and was deliberately
  NOT tuned; tuning it toward the reference would have converted the validation
  into a calibration.
- **Nothing about three-dimensionality or the spanwise stations.** Two-dimensional
  at mid-span throughout.
- **Nothing above Ra 1.43e6, and nothing about a rack row.** One geometry, one
  aspect ratio, two Rayleigh numbers a factor of 1.66 apart.

### 9. The 3D derate, MEASURED (F14 rung K2b, 2026-08-18)

K2a section 10 priced the 3D module at 1.0e5 cell.iter/(core.s) -- 2.7e5 derated
by an **assumed** factor of 2.7 for "3D + turbulence". The assumption is now
replaced by a measurement.

| Fact | Value | Basis |
|---|---|---|
| 3D rate, full spec-default module: N = 4 racks, per-rack `outletMappedUniformInlet` face pairs, four tiles, ceiling return, k-omega SST, buoyancy on, 132,840 cells | **3.968e5 cell.iter/(core.s)** | **VERIFIED**, `K2b3D_probe`, 200 iterations in 66.96 s |
| the 2D turbulent SST rate on the same machine | 4.8e5 | **VERIFIED**, K2b's repeated 46,400-cell cases |
| **the real 3D + SST derate** | **1.21** | **VERIFIED** by division; K2a assumed **2.7**, pessimistic by 2.2x |
| K2a's planning rate against the measurement | **3.97x low** | **VERIFIED** |
| 3D graded pair + controls at the measured rate | **374-697 core-min** (was an unnarrowed 580-1,600) | **VERIFIED** arithmetic on the measured rate; the residual spread is the ITERATION COUNT, not the rate |

**Why the derate is so much smaller than assumed.** A block-structured hex mesh
has the same per-cell face count in 3D as in 2D once the `empty` pair is replaced
by real faces, and the two SST equations were already being solved in the 2D
case. The assumed 2.7 counted both as new work and neither was.

**What is still unmeasured, and it is now the dominant term.** The iteration
count. 9,000 for the coarse mesh comes from K2b's own pilot -- and even at 9,000
that case had not closed its heat balance, so it is a FLOOR. The fine mesh's
20,000 is the 1/N^2 inference and has never been measured on anything. That one
factor is the whole difference between 374 and 697 core-minutes.

### 10. A planted-source recovery control needs a case that meets S13

| Fact | Value | Basis |
|---|---|---|
| Recovery of a 500.000 W plant on the rack-row module, iterations 1,000-5,000 | 353.337, 406.290, 460.392, **536.469**, 466.300 W | **VERIFIED**, `K2bP_C3_plant` against its byte-identical no-plant twin |
| Behaviour | **reaches the plant and oscillates about it**; crosses 500 W between 3,000 and 4,000, overshoots +7.29 %, falls back to -6.74 % | **VERIFIED** |
| The no-plant twin's own ledger net over the same span | wanders **48.313 W peak-to-peak** (+7.134, -35.866, -36.975, +11.338 W) | **VERIFIED** |
| Governed recovery tolerance | 0.1 % of 500.000 W = **0.500 W** -- the noise floor is **97x** it | **VERIFIED** by division |
| Conclusion | the control is **not runnable to its governed tolerance on an unsteady open case**; more iterations do not help | **VERIFIED** by the trajectory |
| What it does establish | the ledger recovers a planted source on this geometry **to about 7 %**, from -68.89 % at 400 iterations | **VERIFIED** |
| The same control on a STEADY case | +2.40e-08 % | KV1a, **VERIFIED** there |

**The mechanism, stated because it is the transferable part.** The matched-twin
difference is supposed to cancel the ledger noise common to both twins. It does
not here, because a 500 W plant perturbs the flow enough that the two twins leave
the same PHASE of the same oscillation -- so the difference of two oscillating
ledgers is not the difference of their means. On a case that meets S13 there is
no oscillation and the cancellation is exact.

### 11. Sizing a planted control: three numbers, always together

Carried from K2b's own near-miss and stated as a procedure. Before running any
planted-source control, state the **plant**, the **ledger it sits in**, and the
**tolerance it is graded at**, and check two inequalities:

- plant / ledger must be large enough that the plant is visible: KV1a's 5 mW in
  this module's 4.914e+03 W ledger is **1.0e-06**, and an instrument returning
  exactly zero would have "recovered" it. **VERIFIED** by arithmetic.
- tolerance must exceed the case's own ledger noise: 0.500 W against a measured
  **48.313 W** floor is unreachable whatever the instrument does. **VERIFIED**.

K2b satisfied the first by re-sizing 5 mW -> 500 W and then failed the second,
which is why the control is reported as a 7 % recovery rather than as a pass.
