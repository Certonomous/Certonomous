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
  current 0.0741 on the PH-only sub-score without touching duct/hump.
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

## Open innovation directions (Numericist backlog)

- GCI-based discretization-error channel alongside the GP epistemic layer.
- Acquisition-driven sampling: spend the next cycle's budget where posterior
  spread is largest (the mission layer already flags thin directions).
- Closure-model registry with validity envelopes (feeds the Chief Researcher
  approval protocol in demo Part 2).
- Unsteady metrics: time-averaged coefficients + shedding amplitude/Strouhal
  as first-class mission metrics.
