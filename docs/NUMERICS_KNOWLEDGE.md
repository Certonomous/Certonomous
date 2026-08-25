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
  already local at `docs/papers/gaussian_processes_roms/mouzahir_lermusiaux_2026_osm26_closure.pdf`
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


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf` | `docs/papers/data_center_indoor_airflow/wibron_ljung_lundstrom_2018_en11030644.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.


## Closure-modelling numerics — appended 2026-08-20 (closure team, reviewed by supervisor)

Drafted from title-verified PDFs in docs/papers/closure/; nothing below was reproduced on this machine unless a section says so. Basis tags: PAPER-VERIFIED / PAPER-GRAPHICAL / NOT STATED.

## Data-driven closures: conditioning, coupling and a-posteriori stability (added 2026-08-20)

### 1. Substituting an exact Reynolds-stress field does not give an exact velocity field, and the error grows with Reynolds number

Wu, Xiao, Sun & Wang, *RANS Equations with Explicit Data-Driven Reynolds Stress Closure Can Be
Ill-Conditioned*, **arXiv:1803.05581v3**, `docs/papers/closure/Wu2018_rans_explicit_closure_ill_conditioned.pdf`.
DNS Reynolds stresses from Lee & Moser (2015) substituted into the RANS momentum equations and
propagated in OpenFOAM; **no turbulence model is solved**; convergence criterion **1e-8 absolute**;
2nd-order central differences except 2nd-order upwind on convection "to avoid the possible numerical
instability when using central difference scheme for the convection term" (arXiv preprint pp. 12-13).

| `Re_tau` | 180 | 550 | 1000 | 2000 | 5200 | Basis |
|---|---|---|---|---|---|---|
| Cells `N` (non-uniform, first cell `y+ < 1`) | 36 | 110 | 200 | 400 | 1040 | **PAPER-VERIFIED**, p. 13 |
| Shear-stress error, volume-averaged | 0.17% | 0.21% | 0.03% | 0.15% | **0.31%** | **PAPER-VERIFIED**, Table 1, p. 4 |
| Shear-stress error, maximum | 0.43% | 0.38% | 0.07% | 0.23% | 0.41% | **PAPER-VERIFIED**, Table 1 |
| **Mean-velocity error, volume-averaged** | 0.25% | 1.61% | 0.17% | 2.85% | **21.6%** | **PAPER-VERIFIED**, Table 1 |
| **Mean-velocity error, maximum** | 0.36% | 2.70% | 0.25% | 5.48% | **35.1%** | **PAPER-VERIFIED**, Table 1 |

**Stress errors are non-monotonic in `Re` and the authors warn against reading the trend** ("such a
coincidental trend should not be overly or literally interpreted", p. 4). **Velocity errors "clearly
increase monotonically with the Reynolds number."** Third-party caveat quoted on p. 3: large
propagated errors have been reported "at Reynolds number as low as **`Re_tau = 395`** depending on
the DNS data used".

**Consequence for this lab.** An a-priori improvement in a Reynolds-stress metric bounds nothing about
the re-solved flow. Since `simpleFoam` is installed, every closure experiment here states whether it
was re-solved; if not, it is labelled a-priori.

### 2. The textbook matrix condition number cannot see this, and it is mesh-dependent

Same paper. For plane channel flow the convection term vanishes, so the operator `A` comes only from
diffusion, and:

| Fact | Value | Basis |
|---|---|---|
| Matrix condition number `K_A = \|\|A\|\| \|\|A^-1\|\|` for the 1-D channel diffusion operator | **`4 n^2 / pi^2`** — a function of mesh count `n` alone, **independent of `nu` and `Re`** | **PAPER-VERIFIED**, Eq. 2.12 and p. 8 |
| Stress-scaled version `K_tau = K_A \|\|div tau\|\|/\|\|b\|\|` across `Re_tau = 180 to 5200` | "**more or less the same across all Reynolds numbers**" | **PAPER-VERIFIED**, p. 7 |
| `alpha = \|\|div tau\|\|/\|\|b\|\|` at both `Re_tau = 180` and 5200 | `O(1)` | **PAPER-VERIFIED**, p. 7 |
| Numeric values of `K_A` and `alpha` | **NOT STATED** — Fig. 1 is graphical | **PAPER-GRAPHICAL** |

Authors' rejection of the metric (p. 8): "**The mesh dependency is highly undesirable as the condition
number is to measure the conditioning property of turbulence models at the PDE level, not any
particular numerical discretization thereof.**"

### 3. The local condition number: definition, cost, and the one number it produces

Same paper. Built from the Green's function of the linearised RANS operator `L(u) = u_0 . grad u - nu grad^2 u`.

| Item | Value | Basis |
|---|---|---|
| Bound | `\|delta u(x)\|/U_inf <= K(x) \|\|div delta tau\|\|_Omega / \|\|div tau\|\|_Omega` | **PAPER-VERIFIED**, Eq. 2.13, p. 9 |
| Definition | `K(x) = \|\|G(x, xi)\|\|_Omega \|\|div tau\|\|_Omega / U_inf` | **PAPER-VERIFIED**, Eq. 2.14, p. 9 |
| Discrete form | `K_j = \|\|r_j\|\|_n \|\|div tau\|\|_n / U_inf`, `r_j` = the `j`-th **row of `A^-1`** | **PAPER-VERIFIED**, Eq. 2.18, p. 10 |
| Volume average | `K_x = sum_j K_j dV_j / V` | **PAPER-VERIFIED**, Eq. 2.19, p. 11 |
| **Cost** | one row of `A^-1` per point via `A^T r_j = I_j`: **`O(n log n)` per row with multigrid, `O(n^2 log n)` for the field** — "much lower than the complexity of `O(n^3)` for typical algorithms of matrix inversions" | **PAPER-VERIFIED**, p. 10 |
| **Mesh independence** | proved (Eqs. B1-B8, pp. 27-28); verified numerically over `Ny = 208, 416, 624, 832, 1040` | **PAPER-VERIFIED**, Fig. 17, p. 29 |

**The headline conditioning result, and it is stated only as orders of magnitude:**

| Coupling | Local condition number, channel `Re_tau = 5200` | Basis |
|---|---|---|
| **Explicit** (`tau` a fixed source term, Algorithm 1) | **`O(10^2)`** (at `Re_tau = 180` it is `O(1)`) | **PAPER-VERIFIED**, p. 14 |
| **Implicit** (`tau = 2 nu_t^m S(u^(i)) + tau_perp`, Algorithm 2) | "**at the same order of magnitude for different Reynolds numbers**"; volume-averaged "**stays at `O(1)`**" | **PAPER-VERIFIED**, p. 16 |
| Periodic hills `Re = 5600`, explicit | "**of the order `O(10^2)` in most areas**" | **PAPER-VERIFIED**, p. 20 |
| Figures 4, 6, 7, 8, 13, 15, 18 | print no values | **PAPER-GRAPHICAL** |

**The optimal eddy viscosity used in the implicit branch is
`nu_t^m(x) = argmin_{nu_t} ||tau^DNS - 2 nu_t(x) S^DNS||`** (Eq. 2.22, p. 11) — **projected from the
DNS field, not from a model.** A real closure must supply it from its own prediction, and the paper
does not measure how much of the gain survives that substitution.

### 4. The implicit/explicit split is the conditioning fix, and three papers implement it differently

| Implementation | Form | Basis |
|---|---|---|
| **Wu, Xiao & Paterson 2018** (`Wu2018_physics_augmenting.pdf`) | `b = nu_t^L S + b_perp` with `nu_t^L = 2 (b:S)/(\|\|S\|\|\|\|S\|\|)` (Eq. 5, p. 7), defined as `argmin_{nu_t} \|\|b - nu_t S\|\|_F` (Eq. 4). Solver: modified `simpleFoam`, `tau^m = nu_t^L S + (tau - tau^L) + tr(tau)`, "**The strain rate tensor S is treated implicitly in the modified flow solver**" | **PAPER-VERIFIED**, arXiv preprint Appendix A, p. 35 |
| **Stroefer & Xiao 2021** (`Strofer2021_differentiable.pdf`) | `u.grad u - div(nu_eff grad u) - grad u . grad nu_eff + div(a_NL) + grad p* = s`, with **`nu_eff = nu - g^(1) k t_tau`**, `a_NL = 2k sum_{i=2..10} g^(i) T^(i)`, `p* = p + 2k/3`; "**the term `div(nu_eff grad u)` is treated implicitly**" | **PAPER-VERIFIED**, arXiv preprint Eq. 2.4, p. 4 |
| Their stated reason | "**explicit treatment of the divergence of Reynolds stress can make the RANS equations ill-conditioned (Wu et al. 2019; Brener et al. 2021). We treat part of the linear term implicitly by use of an effective viscosity `nu_eff` which is easily obtained since with the integrity basis representation the linear term is learned independently.**" | **PAPER-VERIFIED**, arXiv preprint p. 4 |

**Note the dependency**: the implicit split is available *because* the tensor-basis representation
isolates the linear coefficient. A closure that predicts `b` as an opaque tensor cannot perform it.

**And the limit stated by Wu et al. 2018 (arXiv:1803.05581, p. 12)**: "In the extreme (albeit
unlikely) situation where [the] Reynolds stress tensor is orthogonal to the strain rate tensor (i.e.,
optimal eddy viscosity is zero across the flow domain), **the conditioning with implicit treatment and
explicit treatment would be equivalent.**"

### 5. Divergence, documented: a lagged-stress segregated coupling started from the exact answer

Wu et al. 2018, Appendix C, arXiv preprint pp. 29-30. Algorithm 3 is the classic segregated
Reynolds-stress-transport coupling, `tau^(i) = nu_t^m (grad u^(i-1) + grad u^(i-1)^T) + tau_perp^DNS`.

| Fact | Value | Basis |
|---|---|---|
| Initial condition | **the DNS mean velocity** (so the starting error is small) | **PAPER-VERIFIED**, p. 30 |
| Behaviour | `delta U_rms/U_rms^DNS` "**increases rapidly** during the first several iteration steps" | **PAPER-VERIFIED**, p. 30 |
| Volume-averaged local condition number, first three iterations | **`O(10^2)`** | **PAPER-VERIFIED**, p. 30 |
| Outcome | "**The error of the solved mean velocity grows rapidly and eventually leads to divergence of the simulation. Therefore, the solved mean velocity is not presented in this work since a converged solution was not achieved.**" | **PAPER-VERIFIED**, p. 30 |
| Caveat the authors attach | "**The decrease of the condition number ... does not guarantee the decrease of the error in the mean velocity** in such a scenario ... the small condition number needs to be interpreted with caution when the source term in RANS equations changes during the simulation." | **PAPER-VERIFIED**, p. 30 |

**Recommended stabilisations, from the same paper (pp. 23-24)**: (1) initialise from an
eddy-viscosity-model solution; (2) use partial implicit treatment. **Their diagnosis of the mechanism:
"the error can be amplified within each iteration ..., which is carried over to the Reynolds stresses
in the next iteration step and further amplified."**

### 6. Blending factors: three papers, one procedure, and the criterion that should replace it

| Paper | Device | Value and how it was obtained | Basis |
|---|---|---|---|
| **Kaandorp & Dwight 2020** | `tau = (2/3)kI + 2k[(1-gamma) b^B + gamma b^ML]` (Eq. 15), ramped `gamma_n = gamma_max min(1, n/n_max)` | "**`gamma_max` was incremented in steps of 0.1 until the solver became unstable, yielding a value of `gamma_max = 0.8`**"; "**As this choice is ad hoc, further work related to this topic is necessary.**" `n_max` is **NOT STATED**. | **PAPER-VERIFIED**, arXiv preprint p. 26 |
| Its stated trade-off | — | "A **lower value for `gamma` means that the linear eddy viscosity assumption becomes more dominant, resulting in a more stable solution, but impairing the accuracy of the solved mean velocity**" | **PAPER-VERIFIED**, p. 26 |
| **Wu, Xiao & Paterson 2018** | rejects blending outright | "the specification of a blending factor `alpha` is **largely ad hoc and lacks physical basis**" — uses the implicit split instead, **no blending factor at all** | **PAPER-VERIFIED**, arXiv preprint p. 4 |
| **Wu, Xiao, Sun & Wang 2018** | supplies the criterion | "**The metric proposed in this work can assess the model conditioning with any given blending factor, and thus it is possible to choose a minimum blending factor that maintains good conditioning.**" | **PAPER-VERIFIED**, arXiv:1803.05581 pp. 23-24 |
| **de Zordo-Banliat 2023** | cost-function floor, not a blend | if all `g_m < C` the weights revert to uniform `1/N_M = 1/4`; **`C = 0.001`**, insensitive over `C in [0.001, 0.15]` | **PAPER-VERIFIED**, arXiv preprint p. 9 |
| **Xiao et al. 2016** | over-implicitisation, considered and priced | increase `nu_t^m` by `Delta nu_t` and subtract it from the nonlinear part; "such a **purely numerical enhancement may introduce excessive errors** to iterative solvers when the chosen `Delta nu_t` is too large". **No value of `Delta nu_t` is given and no sweep is performed.** | **PAPER-VERIFIED**, arXiv:1803.05581 p. 16 |

### 7. A pointwise regressor's output must be smoothed before it can be differentiated

| Fact | Value | Basis |
|---|---|---|
| Why | "**Since the random forest is a piecewise constant approximation of `b`, and derivatives of `b` are needed in the N-S equation**, the predictions from the TBRF are smoothed spatially with a Gaussian filter, before they are propagated through the solver" | **PAPER-VERIFIED**, Kaandorp, arXiv preprint p. 21 |
| Filter width | Gaussian, **standard deviation 3 cell lengths** | **PAPER-VERIFIED**, p. 21 |
| Its status | "**This filter width is an ad hoc choice**, and can possibly be adjusted more specifically for numerical stability in future work by looking at e.g. **required condition numbers for the solver**" | **PAPER-VERIFIED**, p. 21 |
| Why the raw field is rough | "The TBRF algorithm has **no explicit spatial correlation** in the predictions since these are based on local features of the flow" | **PAPER-VERIFIED**, p. 21 |
| Aggregation choice, for the same reason | prediction is the **median** over trees, **not the mean**, because coefficient prediction means "**the values for the final predictions do not have to lie in-between the values of the points used for training**", which "manifested during testing as **highly irregular and inconsistent predictions in small regions of the spatial domain**" | **PAPER-VERIFIED**, p. 57 |

**The same requirement reached independently.** Wang, Wu & Xiao 2017 (arXiv preprint p. 29): "**A small
region with abnormal Reynolds stress corrections (e.g., non-smoothness or artificial peaks) can
introduce large errors to the velocity predictions** ... **These fluctuations, despite being small in
amplitude, can lead to abnormal behaviors in the divergence term** and thus in the predicted
velocities", because "**the random forest regression used here only provides pointwise estimations but
cannot consider the spatial information ... Therefore, the smoothness of the prediction cannot be
guaranteed.**"

**Two other smoothing mechanisms in the same corpus, serving the same purpose:** Xiao et al. 2016
truncate to **16 (hills) / 8 (duct) Karhunen-Loeve modes**, chosen for "**at least 80% of the total
variance**", which "correspond to **very smooth fields**" (arXiv preprint pp. 20-24); Schmelzer et al.
2020 enforce sparsity for an explicitly numerical reason — models with large coefficients "are
**unsuitable to be implemented in a CFD solver as they increase the numerical stiffness of the problem
and impede convergence of the solution**" (arXiv preprint p. 10).

### 8. Direct learned LES closures are unstable at any CFL, and the eddy-viscosity projection is the rescue

Beck, Flad & Munz, `Beck2019_deep_neural_les.pdf`, **arXiv:1806.04482v3**. Decaying homogeneous
isotropic turbulence, `Re_lambda ~ 180`, DNS `64^3` elements at `N = 7` (`512^3` DOF) coarsened **8x
per direction** to `8^3` elements at `N = 5`; filter is an **L2 projection onto `P5` per element**;
kinetic-energy-preserving DGSEM, low-dissipation Roe, CFL ~ 0.2 with 3rd-order Adams-Bashforth.

| Fact | Value | Basis |
|---|---|---|
| Energy check first | relative energy-contribution error `d_e > 0` and **`O(1e-1)` for all networks** — the learned closures are net dissipative | **PAPER-VERIFIED**, Eq. 4.1, arXiv preprint p. 22 |
| Direct closure behaviour | "initially dissipative, [but] they **lack long-term stability as high frequency errors accumulate**" | **PAPER-VERIFIED**, Fig. 10, p. 22 |
| **CFL sweep** | **0.5, 0.05 and 0.005** tested; smaller steps improve short-term agreement but "later on **stability issues ensued even for very small timesteps**" | **PAPER-VERIFIED**, p. 22 |
| **Root cause, structural** | in the perfect-LES formulation the coarse-grid inviscid operator **cancels exactly**, so an approximate learned term leaves **no stable numerical operator** | **PAPER-VERIFIED**, p. 22 |
| Authors' verdict | "**it is unrealistic to assume that the learned terms can provide an accurate and stable closure**"; "a direct closure ... **is not practical**" | **PAPER-VERIFIED**, p. 22 |
| **The rescue** | `R_tilde(F(U_i)) - R(F(U_i)) ~ mu_ANN . R_tilde(F_visc(U_i, grad U_i))`, with `mu_ANN = L(.)` a **linear least-squares fit with zero bias** over the three components, applied **at every time step and every grid point** | **PAPER-VERIFIED**, Eq. 4.2, p. 23 |
| **Limiter** | **`mu_ANN in [-mu_0, 20 mu_0]`** (`mu_0` = physical viscosity). Without it the model "introduces **noticeable backscatter**" in the spectra | **PAPER-VERIFIED**, p. 23, Fig. 11 |
| Result | both `mu_OP` and `mu_ANN` give a **stable** scheme; limited version gives "close agreement to the filtered DNS data" | **PAPER-VERIFIED**, p. 23 |
| A-posteriori error metric | **NOT STATED** — all a-posteriori comparison is graphical | **PAPER-GRAPHICAL** |
| Parameter count, numeric learning rate | **NOT STATED** | — |
| Data-storage cost of the approach | `U` and `R(F(U))` at `dt = 4e-5 T*` for `0.2 T*` needs **~55 TByte** | **PAPER-VERIFIED**, Remark I, p. 7 |

**A-priori correlations for context** (Table 3, p. 18): best network `CC = 0.477` overall,
**0.767 on inner element points**, versus **0.254** for a single-hidden-layer MLP baseline; the most
informative single input feature (the known coarse-grid operator) correlates with the target at
**0.189**, and raw velocity at **-0.012** (Table 1, p. 11).

### 9. Four other stabilisers for learned closures, each with its measured size

| Paper | Device | Size / threshold | Basis |
|---|---|---|---|
| **Maulik et al. 2019** (2-D SGS) | hardwired sign truncation `Pi = 0` wherever `(grad^2 omega_bar)(Pi_tilde) <= 0` (Eq. 2.4, p. 5) | "**roughly half of the predicted sub-grid terms are truncated**"; it "**precludes the presence of a backscatter of enstrophy**" | **PAPER-VERIFIED**, arXiv preprint pp. 5, 11 |
| **Sirignano/Freund 2020** (DPM) | **none** — "**No stabilizing limiters were used**" | but requires **`N_H >= 50`** hidden units for long-time (`t >= 1e-3`) stability with the divergence-free constraint, **`>= 100`** without. At `N_H = 5` the run "**has become unstable at this time**"; `N_H = 25` shows "**signs of high-wavenumber divergence**" | **PAPER-VERIFIED**, arXiv preprint pp. 21-22 |
| **Guan et al. 2022** (2-D CNN SGS) | **none** — stable "**without any need for post-processing or additional eddy viscosity**" | but requires **`n_tr >= 30,000`** training samples; at 10,000 the a-posteriori LES is "**unphysical**", at 500-1000 it **blows up** | **PAPER-VERIFIED**, arXiv preprint Table 2, p. 13 |
| **Schmelzer et al. 2020** (SpaRTA) | coefficient shrinkage on convergence failure | "if a model does not converge, we further decrease the coefficients by a factor **`xi = 0.1`**, for the model correcting `b^Delta_ij` only. **This ad-hoc intervention** is sufficient to achieve convergence for the studied cases." | **PAPER-VERIFIED**, arXiv preprint p. 13 |
| **Stroefer & Xiao 2021** | pre-training, and a deleted adjoint term | "**The usual practice of random initialisation of the weights is not suitable in this case since it leads to divergence of the RANS solution**"; and the adjoint transpose convection term `grad u_hat . u` "**can result in instabilities** ... **here we eliminate it**" | **PAPER-VERIFIED**, arXiv preprint p. 5 |
| **Bae & Koumoutsakos 2022** | bounded action + reward bonus + gradient clipping | action hard-bounded to a multiplicative **`[0.9, 1.1]`**; reward bonus if within **1%** of the true mean wall stress; **ReF-ER clips far-policy gradients to zero**, `C = 1.5`, `D = 0.05` | **PAPER-VERIFIED**, arXiv preprint pp. 5, 13 |
| **Xiao et al. 2016** | realisability clip | perturbed `(xi, eta)` bounded to `[-1,1]^2`; "**admittedly an ad hoc modeling choice.** As a result, **the prior may become non-Gaussian and the perturbation sample may deviate from zero-mean** if a large number of perturbations are bounded"; and the optimal eddy viscosity elsewhere is "**capped to be positive for numerical stability**" | **PAPER-VERIFIED**, arXiv preprint pp. 9-10; arXiv:1803.05581 p. 12 |

### 10. The a-priori correlation at which an LES closure becomes stable is a property of the case, not a number

| Source | A-priori score | A-posteriori outcome | Basis |
|---|---|---|---|
| Guan 2022, `n_tr = 10,000` | correlation **0.90** (backscatter points **0.89**) | **unphysical** flows for some initial conditions | **PAPER-VERIFIED**, Table 2, arXiv preprint p. 13 |
| Guan 2022, `n_tr = 30,000` | **0.92** (backscatter **0.91**) | **stable** | **PAPER-VERIFIED**, Table 2 |
| Guan 2022's own stated threshold | "between **`c = 0.90` and `c = 0.92`**, or if `c_{T<0}` is a better metric, between **0.89 and 0.91**" — and "**these are just empirical thresholds in this testcase, and such thresholds might be case-dependent**" | | **PAPER-VERIFIED**, p. 13 |
| Beck & Kurz 2021, GRU closure | "**99.9% cross correlation in a priori tests**" | "the **LES solution diverges strongly soon after**" | **PAPER-VERIFIED**, arXiv preprint p. 26 |
| Guan 2022's a-posteriori rollout | `t = 50 tau` to `t = 200 tau`, **5 random initial conditions** | | **PAPER-VERIFIED**, Figs. 5-6, pp. 14-15 |

**Do not carry a correlation threshold between problems.** The two rows above are 0.92 and 0.999 for
opposite outcomes.

**And the backscatter numbers behind Guan's mechanism** (Table 1, arXiv preprint p. 11), a-priori
correlation computed separately on forward-transfer and backscatter points: dynamic Smagorinsky with
positive clipping **0.55 / 0 exactly**; local ANN with sign truncation **0.86 / 0.83**; CNN with no
clipping **0.96 / 0.92**. **Applying the truncation rule to the CNN makes it "excessively diffusive
(with performance comparable to that of the LES-DSMAG)"** (Fig. 8, p. 17, **PAPER-GRAPHICAL**).

### 11. Unrolled-step count and gradient sub-range are different quantities with different optima

List, Chen & Thuerey, `List2022_learned_turbulence.pdf`, **arXiv:2202.06988v2**. Differentiable
**second-order PISO** solver; correction injected at the **implicit predictor step** so continuity is
still satisfied; downsampling **8x in space and 8x in time**.

**Gradient sub-range within a 60-step rollout** (Tables 6-7, arXiv preprint p. 22):

| Sub-range | Temporal mixing layer, MSE @ 512 dt | Spatial mixing layer, MSE @ 1000 dt | Basis |
|---|---|---|---|
| 10 | 2.36e-5 | **2.44e-3** | **PAPER-VERIFIED** |
| 20 | 2.19e-5 | 2.73e-3 | **PAPER-VERIFIED** |
| 30 | **1.93e-5** | 2.98e-3 | **PAPER-VERIFIED** |
| **60 (full)** | **training unstable — no value reported** | **1.19e-2** | **PAPER-VERIFIED** |

Optimum **20-30 steps**; "a split into 2 subranges of 30 steps each performed best"; saturation "at
**circa 60 steps, which coincides with the integral timescales**" (p. 24). **No gradient clipping is
used**, and the authors contrast their approach with it explicitly (p. 28).

**Forward horizon, same paper (Table 1, p. 9)**: a supervised 1-step model has the **best** MSE at
`t_1 = 64 dt` (1.52e-3) and **0.369 at `t_2 = 512 dt`, having diverged — 6.5x worse than the no-model
baseline of 0.057.** The 10-step solver-in-the-loop model is **0.018** at `t_2`.

**Forward-horizon optimum is set by predictability, not by the optimiser.** Um et al. 2020 find
monotone improvement to `n = 128` on buoyancy (40% -> 54% -> 60%) but an optimum of **`n = 2`** on a
randomly forced Burgers case, because "**the randomized forcing in this example severely limits the
number of future steps that can accurately be predicted given one state**" (arXiv preprint p. 6). List
find **no improvement at 120** and **reduced accuracy at 180 and 240** (p. 22).

**The curriculum that makes long unrolls trainable** (Um, arXiv preprint p. 8): "an inferred
correction can overly distort the physical state. Performing time integration via the PDE then
typically leads to **exponential increases of existing oscillations and a diverging calculation**.
Hence, we found it important to **pre-train networks with small look-aheads (we usually use SOL_2
models), and then continue training with longer recurrent iterations**." Their 3-D model: **200k
iterations at SOL_8, then 100k at SOL_16.**

### 12. Coarsening and speed-up claims are only comparable at equal solver order

| Paper | Solver | Effective coarsening | Speed-up | Basis |
|---|---|---|---|---|
| **Kochkov et al. 2021** | **first-order-in-time explicit Euler**, 2-D finite volume, JAX | **8-10x per spatial dimension** | **40-80x** | **PAPER-VERIFIED**, Abstract p. 1, p. 7 |
| **List et al. 2022** | **second-order PISO** | "consistently outperforms simulations with a **2x higher resolution**", often on par with 4x | **3.3x** (IDT), **7.0x** (TML), **3.7x** (SML), **14.4x** (TML matching 4x for several hundred steps) | **PAPER-VERIFIED**, arXiv preprint pp. 26-27 |
| List's own explanation of the gap | "**While other works have reported even larger performance improvements [Kochkov et al., 2021], we believe that our measurements are representative of real-world scenarios with higher-order solvers.**" | | | **PAPER-VERIFIED**, p. 27 |

**Kochkov's speed-up is derived, and the derivation is the transferable part** (arXiv preprint p. 5):
at grids `>= 256^2` the network achieves **12.5x higher FLOP throughput** than the baseline solver, so
despite **150x more arithmetic operations** the ML solver is only **~12x slower at equal resolution**;
a 10x gain in each of three dimensions (two space plus time via CFL) gives **`10^3/12 ~ 80`**. Cost
model `T ~ (C_ML + C_physics)(N/K)^(d+1)` with **`C_ML/C_physics ~ 12`** (Eq. 2, p. 7). Benchmarked on
**one core of a Google Cloud TPU v4**.

**Never quote the two headline numbers side by side without the solver order.** `FEASIBILITY.md` §1.4
additionally records that on this lab's 16-CPU machine the *speed-up* claim is not reproducible at all
and any attempt would be NOT A RESULT; only the accuracy claim is reproducible here.

**Overheads, measured**: List's network costs "**circa 10%**" over no-model at the same resolution
(0.071 vs 0.066 s/step for IDT). Sirignano's network evaluation is "**almost 50%** of the total LES
cost" (arXiv preprint p. 21). Lozano-Duran's wall model is **1.1 to 1.3x** the cost of the algebraic
equilibrium wall model (arXiv preprint p. 13).

### 13. Training cost, in the only units that decide anything

| Paper | Cost | In units of the thing it replaces | Basis |
|---|---|---|---|
| **List et al. 2022** | 61 h, 78 h, 240 h on one GTX 1080Ti | **[120, 118, 22] full-length DNS solves** | **PAPER-VERIFIED**, arXiv preprint pp. 26-27 |
| **Bae & Koumoutsakos 2022** | `O(1e3)` CPU-hours, **< 1 GB** storage | versus `O(1e7)` CPU-hours and **> 100 TB** to generate the equivalent DNS training data | **PAPER-VERIFIED**, arXiv preprint p. 10 |
| **Xiao et al. 2016** | **600** forward RANS evaluations, each **10%** of a baseline solve | **60x one baseline RANS solve**, per case; on 60 cores the wall time equals one single-core baseline solve | **PAPER-VERIFIED**, arXiv preprint p. 40 |
| **Lozano-Duran & Bae 2023** | **~12 h per ANN on 4x NVIDIA A100 40 GB** | not converted | **PAPER-VERIFIED**, arXiv preprint p. 13 |
| **Schmelzer et al. 2020** | model selection at `K ~ 15000` points: "**of the order of a minute on a standard consumer laptop**" | the CFD cross-validation sweep (35-47 runs per test case) is the real cost and is **NOT STATED** | **PAPER-VERIFIED**, arXiv preprint p. 11 |
| **Beck et al. 2019** | GPU-hours **NOT STATED**; storage **~55 TByte** | data-bound, by the authors' own conclusion | **PAPER-VERIFIED**, p. 7, p. 24 |
| **Kochkov et al. 2021** | training wall-clock **NOT STATED** | — | — |

### 14. Wall models: the log-layer mismatch is a numerics error of the first off-wall cells

Larsson, Kawai, Bodart & Bermejo-Moreno, `Larsson2016_wall_stress.pdf`, **journal of record**,
Mech. Eng. Reviews 3(1):15-00418. **Pagination hazard**: the printed folios extract with a spurious
"2" prefix (PDF p. 3 prints as "23"), so **all citations below are PDF page numbers**.

| Fact | Value | Basis |
|---|---|---|
| Grid criterion | `dx_i <~ (C_i/N) y` (Eq. 6) | **PAPER-VERIFIED**, pp. 10-11 |
| Why it is always violated at the wall | kinematic wall damping gives `C_2 <~ 2` and Nyquist gives `N >~ 2`, so **`C_2/N < 1`** and the criterion is "**violated in the first LES grid-point, regardless of numerical accuracy in the LES**" | **PAPER-VERIFIED**, p. 11 |
| Consequence | "**even a 'perfect' wall-model in one numerical code would suffer from a log-layer mismatch if implemented in a different numerical code!**" | **PAPER-VERIFIED**, p. 11 |
| **Sign is code-dependent** | negative "generally ... for incompressible flow solved using a **staggered** grid"; positive for "codes using a **colocated** grid and/or some degree of numerical dissipation" | **PAPER-VERIFIED**, p. 10 |
| **The fix** | set **`h_wm ~ 0.2 delta` independently of the grid**, then refine. **Converged results have zero log-layer mismatch.** | **PAPER-VERIFIED**, p. 11 |
| Convergence thresholds (6th-order compact) | **`dy <~ 0.33 h_wm`**, **`dx ~ dz <~ 0.8 h_wm`** | **PAPER-VERIFIED**, p. 11 |
| Independently confirmed (different method) | `dx <~ 0.6 h_wm`, `dy <~ 0.3 h_wm`, `dz <~ 0.4 h_wm` | **PAPER-VERIFIED**, p. 11 |
| Demonstration case | supersonic flat plate `Re_delta = 6.1e5` (`Re_theta = 5e4`), fixed `h_wm/delta = 0.055`, fixed `dx/delta = dz/delta = 0.042`, sweeping `dy_w/h_wm = 1.0, 0.50, 0.33, 0.25, 0.20` | **PAPER-VERIFIED**, Fig. 9, p. 12 |
| Error size (quoted from Wu & Meyers 2013) | a wall-tuned Smagorinsky constant reduced the mismatch "**from a typical 10-20% to only 5%**" | **PAPER-VERIFIED**, p. 11 |
| Direct `C_f` link | "`c_f ~ U_inf^-2`, [so] the log-layer mismatch error has a **direct effect on the predicted skin friction**" | **PAPER-VERIFIED**, p. 10 |
| **The cancellation trap** | "the results in Fig. 5 are best (smallest log-layer mismatch) for the **coarsest** grid", and "**a flawed model may produce 'perfect' results by introducing errors that exactly cancel those present in the outer layer LES.**" | **PAPER-VERIFIED**, p. 18 |
| Grid-refinement pathology (hybrid LES/RANS) | channel, fixed `y_int/delta = 0.15`, refining `dx/delta` 0.25 -> 0.047: "**the mean velocity profile actually becomes less accurate during grid-refinement.**" | **PAPER-VERIFIED**, Fig. 5, p. 6 |
| Mandatory practice | "**it is mandatory to test all wall-modeled LES approaches on different grids: both by refining the grid and by modifying the aspect ratio of the grid.**" | **PAPER-VERIFIED**, p. 18 |

**Resolution recipes (pp. 2-3)**: wall-resolved LES viscous layer `(dx+, dz+) ~ (40, 20)`,
`dy+_w ~ 1`; outer layer `(dx/delta, dz/delta) ~ (0.08, 0.05)`. **WMLES recommendation:
`(dx/delta, dy_w/delta, dz/delta) ~ (0.08, 0.02, 0.05)`, stretched linearly to `y/delta = 0.2`.**

**Cost scalings (pp. 2-3)**: wall-resolved LES outer layer **independent of `Re_tau`**; viscous and
overlap layers **`O(Re_tau^2)`**; **WMLES grid independent of `Re_tau`**; below **`Re_tau <~ 600`**
WMLES saves "at most 50% of the grid points" — i.e. it is not worth doing. **"WMLES incurs a cost
10-100 times higher than DES97"** for `dx/delta = dz/delta >~ 0.5`.

**Acceptance criterion, from Piomelli & Balaras 2002** (Annu. Rev. Fluid Mech. 34, journal of record,
p. 370): "the mean skin-friction coefficient must be predicted accurately, perhaps **within 5%** of
resolved calculations", followed immediately by "**Present models do not satisfy these requirements.**"
Their cost exponents (pp. 351-354): wall-resolved LES **inner layer `~ Re^2.4`**, **outer layer
`~ Re^0.5`**, **WMLES with equilibrium BCs `~ Re^0.5`**; and at `Re_L = O(1e6)`, **99% of the grid
points resolve an inner layer only 10% of `delta` thick**.

**A wall-model numerical instability, recorded**: Piomelli & Balaras p. 360 — in a rotating channel
"the model based on the logarithmic law **failed entirely owing to numerical instability introduced by
the logarithmic boundary condition**", while the two-layer model succeeded on the same case.

### 15. Two wall-model implementation details worth carrying

| Fact | Value | Basis |
|---|---|---|
| Wall stress imposed as an **eddy viscosity**, not a Neumann condition | `nu_t\|_w = (du/dy\|_w)^-1 (tau_w^m/rho) - nu`, "chosen over Neumann BC **to reduce log-layer mismatch**" | **PAPER-VERIFIED**, Bae & Koumoutsakos, arXiv preprint Eq. 9, p. 15 |
| Sensitivity of `tau_w` to the sampling-point placement | wall-shear stress changes **~5%** when `y` is placed on a grid point rather than a midpoint — **against a headline model accuracy of <4%** | **PAPER-VERIFIED**, arXiv preprint p. 16 |
| Non-monotonic grid convergence, reported and unexplained | pipe at `Re_tau ~ 40,000`, both models | **PAPER-VERIFIED**, Lozano-Duran, arXiv preprint pp. 18-19 |
| Convergence caveat | "**WMLES might not converge to the DNS solution with grid refinements until the grid is in the DNS-like regime**, when the contribution of the wall model is negligible" | **PAPER-VERIFIED**, arXiv preprint p. 16 |

### 16. What none of this establishes

- **Nothing here has been run on this machine.** Every value is the paper's own, read from a
  title-verified PDF at the location named. `FEASIBILITY.md` records which are reproducible here and
  at what cost; none has been attempted.
- **The conditioning results are orders of magnitude, not measurements.** `O(1)` versus `O(10^2)` is
  the entire quantitative content of §3; Figs. 1, 4-8, 13, 15 and 18 of arXiv:1803.05581 print no
  values. Table 1 (§1) is that paper's only numeric results table.
- **The implicit-treatment demonstration uses an eddy viscosity projected from the DNS field**, not
  from a model (§3). How much of the conditioning gain survives a modelled `nu_t^m` is unmeasured.
- **Several a-posteriori claims here have no number attached and are marked PAPER-GRAPHICAL.** Beck
  2019 has no a-posteriori error metric; Sirignano 2020 has no percentage against Smagorinsky
  anywhere; Guan 2022's a-posteriori and transfer-learning results are figure-only; Bae 2022's
  per-`Re` errors exist only as a plot.
- **The condition number is an upper bound, not a forecast.** Wu et al. state it twice: the velocity
  error depends on both the condition number and the stress error, so "the spatial pattern of mean
  velocity error ... **can not be solely explained by** the local condition number" (arXiv preprint
  p. 18); and a falling condition number "**does not guarantee the decrease of the error in the mean
  velocity**" when the source term changes during the simulation (p. 30).
- **Every flow in §§1-13 is canonical, incompressible and at low-to-moderate Reynolds number.** The
  wall-model results of §§14-15 are the only entries touching engineering `Re`.


## Closure-modelling numerics, measured on this machine — appended 2026-08-20 (Lane B, reviewed by supervisor)


---

**N-B1. `beta*` and `C_mu` are the same constant with two provenances that agree.**
`beta* = 0.09` in Menter's SST set [VERIFIED-PDF: Menter 1994, AIAA J. 32(8),
eq. (A4), p. 1603] is `C_mu` from the equilibrium log layer, `(-<u'v'>/k)^2` with
`k/u_tau^2 ~ 3.3`. `beta_2 = 0.0828` is exactly `beta* (C_e2 - 1) = 0.09 x 0.92`,
i.e. the k-epsilon decay constant transformed into omega form. `sigma_omega2 =
0.856` is fixed by requiring `gamma_2 = C_e1 - 1 = 0.44`; it is **not** `1/sigma_e`.
Checked by hand: `0.0828/0.09 - 0.856 x 0.41^2/0.3 = 0.9200 - 0.4796 = 0.4404`.

**N-B2. Menter's `a1` limiter uses the VORTICITY magnitude, not the strain-rate
magnitude.** "where `Omega` is the absolute value of the vorticity"
[VERIFIED-PDF: Menter 1994, p. 1604, eq. (A14)]. OpenFOAM's `kOmegaSST` and most
other codes use `sqrt(2 S_ij S_ij)`. This is a real, usually undocumented,
departure from the published model, active wherever strain and rotation differ.
Any "SST" number must say which was used.

**N-B3. The `a1` limiter is a realisability constraint, and it is load-bearing.**
`a1 = 0.31 < 1/3` caps `(nu_t/k) lambda_max(S)`, which is exactly the linear-model
realisability bound. Measured on the Closure Challenge benchmark
(`_common/sst_baseline_metrics.py`): the limiter is active on **18-33% of cells**
in all 40 cases; with it, `b_RANS` is realisable in 100% of hill/duct/step cells;
without it (counterfactual at frozen `k`, `omega`) the ratio reaches **262** and
**11.5% of cells** are non-realisable on the NASA hump - and only 0.16-0.53 on
every case without a stagnation region.

**N-B4. PyTorch on this box: 16 threads is ~63x SLOWER than 4 on small batches.**
Measured, 342,014-sample epoch, 8x30 MLP + a 10-tensor `einsum` merge:
`threads=16, batch=4096` -> **49.4 s/epoch**; `threads=4, batch=4096` -> **0.78 s**;
`threads=1, batch=4096` -> 0.90 s; `threads=8, batch=32768` -> **0.39 s**.
Thread-pool contention on sub-millisecond GEMMs dominates completely.
**Default to `torch.set_num_threads(4)` and batches >= 8192 for anything of this
shape on this machine**, and parallelise over seeds/models instead of within a
GEMM. This single setting was worth a factor of 63 in wall clock; without it the
TBNN sweep was on track for 66 hours instead of about one.

**N-B5. The Pope tensor basis spans ~7 orders of magnitude and the high-order
tensors are numerically dangerous.** On the benchmark training set the RMS
Frobenius norms of `T^(1..10)` are
`1.5e1, 3.5e3, 1.0e3, 1.0e3, 2.0e2, 5.3e5, 8.4e7, 8.4e7, 4.9e7, 1.4e6`.
Rescaling each `T^(n)` to unit training RMS is an exact reparametrisation of the
coefficients `g^(n)` and costs nothing, but it does **not** bound the model on
unseen flows: `b = sum g^(n) T^(n)` is unbounded, and on the NASA wall-mounted
hump - the only benchmark case with a stagnation region - a trained TBNN produced
`||b||` of order **1e7** and a tensor-basis random forest on the same split
produced order **1e2**, against a realisable maximum of 0.8165.

**N-B6. The published TBRF ridge parameter is unusable on a rank-deficient basis.**
Kaandorp & Dwight's `Gamma = 1e-12` [VERIFIED-PDF: arXiv:1810.08794v2, p. 30],
applied to a basis of numerical rank 3-4 (see N-B10), returns coefficients of
order `1/Gamma` along the null directions: measured *training* `b_rms` **0.81**,
worse than predicting `b = 0` (0.33). Replacing the ridge solve with a symmetric
eigendecomposition that inverts only eigenvalues above `1e-8 lambda_max` moved
training error to **0.13** with no other change.

**N-B7. OpenFOAM v2606 is installed and functional on this machine**
(`/usr/lib/openfoam/openfoam2606`, `source etc/bashrc`, `simpleFoam` runs).
A-posteriori (re-solved) propagation of a learned closure is therefore available.
Any Phase-3 result that stops at a-priori scoring is making a scope choice, not
hitting a capability limit, and must say so in those words.

**N-B8. The benchmark has 40 cases and 641,652 cells with truth, not 41 and
641,662.** `sst_baseline_metrics.json` contains 40 case entries; summing them
gives 29 x 15600 (hills) + 101,026 (8 ducts) + 15,600 + 21,000 + 51,626 =
641,652. `BASELINES.md` prose says "41 benchmark cases" and "641,662" in two
places. The tables are right; the prose count is off by one case and ten cells.
`make_baselines_md.py` generates that prose, so the fix belongs there.

**N-B9. Smagorinsky's own constant, located.** `k_H = 0.28` appears twice in
Smagorinsky 1963 [VERIFIED-PDF]: in the text on **printed p. 105**, immediately
after eq. (4.24), and in the "Parameters of the numerical model" box on
**printed p. 164** under "Small-scale eddy diffusion / Lateral". His
`k ~ 0.1-1.0` disclaimer is on **printed p. 150**, not 149; von Karman's constant
0.4 is in the notation list on **printed p. 162**. Earlier drafts of the
inventory cited pp. 149 and 163; both were off by one page and are corrected.

**N-B10. Per-cell rank of Pope's ten-tensor basis on this benchmark: 3.24.**
Measured over 5,000 random training cells as the number of singular values of the
flattened 10x9 tensor stack above `1e-8 sigma_max`: **3,814 cells at rank 3,
1,185 at rank 4, 1 at rank 5, none above.** Expected, because every benchmark
case is a statistically 2-D mean flow and Pope states the basis collapses to
three tensors in two dimensions [VERIFIED-PDF: Pope 1975, JFM 72(2), p. 335]. One
line of numpy; it should be run before any tensor-basis reproduction.

*[Provenance repaired 2026-08-22.]* **Source:
`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/train_log.json`**, keys
`basis_rank_mean` = **3.2374** and `basis_rank_hist` =
`[0, 0, 0, 3814, 1185, 1, 0, 0, 0, 0, 0]` - exactly the histogram above. **That
file exists on disk but is untracked in git** (the whole `Kaandorp2020_TBRF/`
directory is untracked, as `INCIDENT_tbrf_overwrite_2026-08-20.md` also records),
which is why `git ls-files`, `git log -S` and every grep of the committed tree
report the pointer as dead. It is not dead; it is uncommitted. It is written by
`Kaandorp2020_TBRF/run_tbrf.py` (the block at lines 63-72) and is deterministic -
`np.random.default_rng(0).choice(train_cells, 5000, replace=False)`, tolerance
`1e-8 sigma_max` - and was produced by the same run as the TBRF checkpoints in
`/home/ubuntu/closure-data/tbrf/` (both 2026-08-20 22:19-22:20), so the number is
regenerable rather than merely remembered. **3.24 is a pooled-sample statistic**
over 5,000 randomly drawn training cells, which the duct family (the lowest-rank
cases) pulls down. The **case-mean** statistic is a different number, **3.738**
(case means 3.006-3.987), measured independently in
`cases/RANS_LES_closure_models/_common/features/FS2_DEGENERACY_REPORT.md` sec. 4.
Both are computable and correct; they must not be quoted interchangeably. The
bound both agree on, and the one that carries the argument, is **never above 5**.

**N-B11. A constant tensor beats k-omega SST on the a-priori anisotropy metric,
on all 8 strict TEST cases.** The mean `b_LES` over the 342,014 training cells,
predicted everywhere with no inputs, gives `b_rms` 0.2258-0.4221 against SST's
0.2889-0.5972. "Beats the RANS baseline on `b_ij`" is a bar a constant clears,
and every a-priori closure claim on this benchmark should be scored against that
constant as well as against SST.

**N-B12. Corrected page citations** found while auditing the inventory against
verified PDFs: Piomelli & Balaras 2002 - the "simplest approach to relate the
wall stress" derivation is on printed **p. 354** (not 353), the wall-model
lineage runs **pp. 354-358**, and section 2.2 "Zonal Approaches" starts on
**p. 359** (not 357). Kaandorp & Dwight 2020 - Table 2 is on preprint **p. 31**,
Table 3 on **p. 37**, Table 4 on **p. 41** (hyper-parameters p. 30).

**N-B13. The k-corrective-frozen-RANS extraction on PH10595 is exact, and I
verified it independently from the written fields.** Schmelzer et al.'s eq. (3),
`b_data_ij = -(nu_t/k) S_ij + b^Delta_ij`, evaluated on the 15,600 cells of
`verification/runs/W2_sparta_runs/ph_frozen/1492` using OpenFOAM's own written
`grad(U)`, closes to **relative L2 8.771e-14**, median cellwise `9.8e-15`, max
`1.5e-12`. Using this directory's finite-difference gradient
(`of_read.structured_gradient`) instead gives `3.7e-3` — that difference is the
gradient reconstruction error and nothing else, and it is consistent with the
0.47-0.96% interior figure in `BASELINES.md` sec. 1. **Useful pattern: an
extraction that satisfies an algebraic identity can be audited from its written
output alone, without re-running the solver.**

**N-B14. The SpaRTA correction is the same size as the field it corrects, on both
cases.** RMS `||b^Delta||_F` against RMS `||b_data||_F`: PH10595 **0.27919 /
0.29699 = 0.94**; CBFS13700 **0.32781 / 0.35332 = 0.93**. RMS `R` = 0.0588
(mean 0.0223) on PH, 0.00658 (mean 0.00153) on CBFS. A "correction" that is 93-94%
of the signal is not a perturbation, and any argument that treats the discovered
model as a small algebraic tweak to k-omega SST should be read against those
ratios. Both extractions verify against their defining identity to 8.8e-14 (PH)
and 1.7e-13 (CBFS) relative L2 — see N-B13.

**N-B15. A published coefficient can be unreachable by the published method.**
The lab's discovery campaign recovered SpaRTA's functional form for `R` exactly
(`T1` on both cases) and matched the PH coefficient to **0.66%** (1.39917 against
1.39), but on CBFS obtained **0.544787** against a published **0.93**, with the
recorded rider that *0.93 is unreachable at any `lambda_r >= 0` from these fields
(OLS bound 0.594)*. That is a bound, not a tuning shortfall: no setting of the
regularisation reaches the published value. When a reproduction can prove a
target is out of reach of the stated procedure, that bound is the result.

**N-B16. OpenFOAM v2606 builds user applications on this box.** `g++ 13.3.0`,
`wmake` from `/usr/lib/openfoam/openfoam2606/etc/bashrc`, user binaries land in
`$FOAM_USER_APPBIN` = `/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin`.
A single-file solver compiles and links in about a minute. Two gotchas cost time:
`Foam::sqrt(double)` is ambiguous against `Foam::sqrt(dimensionedScalar)` — use
`::sqrt` for plain doubles — and `bound()` needs `#include "bound.H"`.

**N-B17. Seed spread as a cheap extrapolation detector.** The 17-feature
tensor-basis forest, two seeds, on the Closure Challenge test cases: in-domain the
two seeds agree to **0.0001-0.0013** in `b_rms` (four significant figures); on the
one out-of-family case they differ by a **factor of 2.3** (208.6 against 471.4).
The collapse in reproducibility localises the extrapolation without any reference
to the training distribution, and it agrees with the pre-registered Mahalanobis
statistic (13.2% of that case's cells beyond the training 99th percentile, against
0.00-0.70% on every other test case). **Two independent, near-free diagnostics,
same answer — run both.**

**N-B18. Scoring a model from its `best_state` checkpoint mid-run is legitimate
and should be labelled with the epoch and the patience counter.** The MLP control
here was scored at epoch 300 of <= 400 with 14 epochs since its last improvement
against a patience of 60. Stating those three numbers lets a reader bound the
error: a converged control could only have been better, which in this case would
have widened the gap on the criterion the model already failed and narrowed the
margins it won. Checkpoint-scoring without those numbers is not interpretable.

**N-B19. Model ranking reverses between interpolation and extrapolation.** On the
same split, the same metric and the same eight cases, the ordering of four
anisotropy models is exactly inverted between the seven in-domain cases and the
one out-of-family case: the plain MLP is worst on all seven and best on the
eighth by four to seven orders of magnitude (0.3664 against 197, 340 and 1.48e+07).
**Never rank closure models on a pooled error across a test set that mixes
interpolation and extrapolation** — the pooled number is whichever regime has the
larger magnitude, and here that is a single case out of eight.

**N-B20. Name your cell masks; two counts that differ by 0.09% are not a typo.**
Two training-cell counts circulated in this programme, 342,014 and 341,717, and
looked like a discrepancy. They are different quantities: the first is the
**LES-only** mask (`k_LES` above the anisotropy floor, so `b_LES` is defined) —
correct for any model that never touches `b_RANS`; the second additionally
requires a finite `b_RANS`. Every one of the 567 cells separating them across the
40 cases is a non-finite `b_RANS`, because `b_RANS = tau_RANS/(2 k_RANS) - I/3`
is undefined where the converged RANS `k` underflows although `k_LES` does not
(5-52 cells on 34 of the 40 cases). The extended features and `b_LES` contribute
none. Fix adopted: the masks are returned as `valid_les_only` and `valid` from
`_common/score_prediction.py`, and every file that quotes a cell count now names
the mask. **A bare cell count is not a specification.**

**N-D = DAFoam-team numerics facts, opened 2026-08-21** after N-B21..N-B25 collided
with a concurrent closure-team append (commit `79a73944`); numbers are re-derived at
filing time, never carried in a document.

**N-D1. A DAFoam discrete adjoint that returns `KSPConvergedReason -9` at iteration 0
is an exact zero pivot in the ASM sub-block ILU, and no shift catches it.** Measured on
a 21,000-cell wall-resolved separated `kOmegaSST` case (CBFS) and a 51,626-cell one (NASA
hump). `dRdWTPC` is 210,592 x 210,592 with **13,710,468** nonzeros, **zero** zero-rows,
zero zero-columns and zero zero-diagonal entries; `‖b‖₂ = 7.091590452305e-04`, equal to the
printed iteration-0 GMRES residual to all 13 digits because `KSPSetNormType` is
`KSP_NORM_UNPRECONDITIONED`. `scipy.sparse.linalg.spilu` returns **`Factor is exactly
singular`** at every drop tolerance swept (1e-2/fill 3, 1e-3/fill 5, 1e-4/fill 5,
1e-5/fill 10); `splu` — complete, with partial pivoting — **solves at every pivot
threshold** (`‖Ax−b‖/‖b‖` = 2.3769e-10 / 6.4063e-12 / 2.535461e-12). Diagonal magnitude
spread is **8.67 decades**, against **14.17** for a transonic family that fails differently,
so a conditioning story does not explain it. **The failure is factor growth, not a small
pivot**, which is why `MAT_SHIFT_NONZERO` is already on and insufficient, why raising the
zero-pivot threshold six decades to 1e-8 still returns `-9`, and why `pcFillLevel` 4 also
returns `-9`: **fill adds fill, not pivoting**. Switching the sub-block PC to complete LU
gives `PetscConvergedReason: 2` in **667** iterations. The `-9` persists at **np = 1**, so
it is not a decomposition effect.

**N-D2. Complete-LU sub-blocks cost 24-28x the matrix's own nonzeros, and for a
21,000-cell adjoint that is 9.044 GiB, not the 22 GiB that had been assumed.** Offline,
`nnz(L+U)` for the whole 210,592² operator measures **3.22e+08 to 3.90e+08** against the
matrix's 13,710,468 — the ratio quoted as *"roughly 3 GB on a 21,000-cell case"*. In-solver
at np = 4 with `DAFOAM_SUBPC_TYPE=lu`, the measured **peak RSS is 9.044 GiB** for a
21,000-design-variable `compute_totals` (primal + one adjoint), inside a **12 GiB**
container cap, sampled at 5 s by `docker stats`; a primal-only `run_model` on the same case
peaks at **1.444 GiB**. The earlier runs of this configuration were given a 22 GiB cap and
never measured what they used, so 22 GiB had been carried as if it were a requirement.
**On a shared box `docker stats` reports every container: the raw maximum in the same log
was 9.786 GiB and belonged to another lane.** Cost of the converged adjoint: **272 s at
np = 4** against a control that fails in 82 s — about **3.3x the wall time of failing**.

**N-D3. On this stack the finite-difference plateau is a per-component property, and the
vector norm can dip where no component supports it.** A 4,032-cell case, 8 FFD shape design
variables, central differences, one step varying: full-vector relative error reads
**94.95 / 52.88 / 17.64 / 12.27 / 11.52 / 11.43 / 10.47 / 8.94 / 4.28 / 9.83 %** at
1e-8 / 1e-7 / 1e-6 / 1e-5 / 1e-4 / 1e-3 / 5e-3 / 1e-2 / 2e-2 / 3e-2, and the **primal fails
to converge at 5e-2 and 1e-1**. The 4.28 % point at 2e-2 is a single unstable component
crossing, not a minimum. Excluding the three flagged components: **dead flat at 2.5-3.0 %
from 1e-4 to 3e-2, cosine 0.99998**. One component carries **82.7 %** of the squared-error
norm at the original step. Registered wrong-step control on the same case: **132.75 %** at
1e-8 where the graded step reads 0.038 %. And a loose primal tolerance, not the step, can
own the disagreement: three per-cell probes read **25.9 / 32.0 / 32.2 %** at
`primalMinResTol 1e-6` and **0.032 %** at 1e-8, a systematic `fd/adj ~ 0.7` that no step
sweep would have diagnosed.

**N-D4. A tightly-coupled MPI job pinned to a `cpuset` degrades 21.5x under unpinned
co-tenants, and the degradation is entirely in the clock.** Measured this session: a 4-rank
DAFoam `run_model` whose registered basis is **71 s** took **1,529 s** while the host
carried 20-25 unpinned `simpleFoam` processes from another family at load average 11-12,
with `docker stats` reporting the container at **300 % CPU** throughout. Iteration count
(1,580), objective (`1.5279278906359758e-02`, bit-identical to the archive) and every
residual digit were unaffected. Mechanism: Open MPI spin-waits, so a rank descheduled by a
co-tenant stalls the others at full apparent CPU, and a GAMG pressure solve issues on the
order of a hundred global reductions per SIMPLE iteration. **`--cpuset-cpus` constrains
where a container's threads may run, not who else may run there.** Two corollaries: budget
in core-minutes from a *quiet-box* basis and record the overrun, and **never read a rate off
a block-buffered redirected log** — the same run looked ~400x slow by line-growth and was
21.5x slow by its own wall time.

**N-D5. Three DAFoam images on this box report identical version strings and differ only
in one file; the md5 is the identity.** All report DAFoam **5.0.0**, OpenFOAM **v2506**,
PETSc **3.15.5**, IDWarp **2.6.2**. `src/adjoint/DALinearEqn/DALinearEqn.C`:
stock `f6a89e33b0f4772a0563cb0c8633ac48`, **507** lines, 0 `DAFOAM_SUBPC_TYPE`;
`subpclu:v1` `89e71ca2db5d80c06b1eda070ffc7a1b`, **526**, 3; `kspopts:v1`
`96f5762819e33efbdaad34181a214082`, **534**, 3, `KSPSetFromOptions` moved from line 138 to
**351**; `subpclu:v2` `5b3159f88dbefcf7c52bd888401d097f`, **539**, 4. The patched IDWarp is
worse: it is **not in any image**, is injected by bind-mount and `PYTHONPATH`, changes the
reverse derivative by seven orders of magnitude, and **still reports `2.6.2`** — its
`libidwarp.so` is `85f59e87253e0a71a813f64ca6e4c425` against stock
`f0fcb488e0e98156575cd19548e91663`, **both 491,344 bytes**. Match a number to a build by
hash and image ID, never by a version string, and note that `strcmp(env, "lu")` is an exact
match so `LU`, `Lu`, `lu ` or `superlu` run stock silently — assert the banner in the log.


## Closure-modelling numerics from the Kaandorp 2020 TBRF reproduction — appended 2026-08-20 (CLOSURE-REPRO, reviewed by supervisor)

## The Pope tensor basis is rank-3 to rank-4 on every flow in this benchmark, and that is where a tensor-basis model's extrapolation error comes from

Pope's integrity basis has 10 tensors `T^(1..10)`, so a tensor-basis model fits 10
coefficients `g^(m)` per leaf/sample. **The 10 flattened basis tensors do not span
10 dimensions on real data.** Measured here as the mean numerical rank (tol
`1e-8 * max|T|`) of the 9x10 matrix `[T^(1) ... T^(10)]` at a cell, averaged over
a 500-cell sample per case:

| case | mean rank of the 10-tensor basis at a cell |
|---|---|
| `AR_1_Ret_360` (square duct) | **3.089** |
| `AR_1_Ret_180` (square duct) | **3.09** |
| `CBFS13700` (curved step) | **3.99** |
| periodic hills | **3.82 - 3.98** |

Pope's own statement that a 2-D mean flow needs only `T^(1..4)` is confirmed, and
the ducts are *worse*, not better, despite being geometrically 3-D: their mean
flow is 2-D in the cross-plane with a single dominant streamwise gradient.

Two consequences, both measured:

1. **Six of the ten fitted coefficients are unconstrained by the training data.**
   With Kaandorp's regularisation `Gamma = 1e-12` the ridge does nothing at these
   magnitudes, and the least-squares solution wanders freely in the null space.
   Over all leaves of a 100-tree forest: `median |g| = 2.6e-5`, `p99 |g| = 3.4e4`,
   `max |g| = 4.0e6`. Nine orders between the median and the 99th percentile.
2. **Those coefficients are harmless in-distribution and catastrophic out of it**,
   because the null directions differ between the training flow and the
   prediction flow. Frobenius norms of the individual basis tensors, p99 over cells:

   | | `T^(1)` | `T^(2)` | `T^(6)` | `T^(7)` | `T^(8)` | `T^(9)` |
   |---|---|---|---|---|---|---|
   | training pool (hills) | 34.6 | 1.69e3 | 4.15e4 | **1.02e6** | 1.02e6 | 5.86e5 |
   | `AR_1_Ret_360` (duct) | 223 | 7.02e4 | 1.11e7 | **1.74e9** | 1.74e9 | 1.01e9 |

   Three decades of extrapolation in `T^(7..9)`, multiplied by coefficients that
   the training data never pinned down.

**Practical rule.** Any model of the form `b = sum_m g^(m)(features) T^(m)` must
either (a) report the numerical rank of `T` on the *prediction* case, (b) fit `g`
in a basis truncated to that rank, or (c) regularise `g` at a magnitude that is
meaningful relative to `sum T^T T` — `Gamma = 1e-12` against normal-equation
entries of order `1e4` is `Gamma = 0`. Doing none of these produces a model that
is excellent in-sample and unbounded out of it, which is exactly what was measured.

## An RMS on a closure prediction hides the failure mode; report the distribution

The preregistered metric was `b_rms_F = sqrt(mean ||b_pred - b_LES||_F^2)`, the
convention of `_common/BASELINES.md`. On `CBFS13700`, the 16-feature TBRF gives
(percentiles are 5-seed means of the per-seed percentiles):

| statistic of `||b_pred - b_LES||_F` | value |
|---|---|
| median | **0.170** (SST's own `b_rms` is 0.319) |
| p90 | 3.40 |
| p99 | 153.9 |
| max | 1.24e3 (single seed) |
| **RMS (the reported metric)** | **47.68** (5-seed mean; the single seed shown above gives 37.96) |

The median cell is *better than the industrial closure it is meant to replace*;
the RMS is 156x worse. The two statements are about the same prediction. The
mechanism is visible in one further number: **15.0 % of the predicted cells
violate the hard bound `||b||_F <= sqrt(2/3) = 0.8165`**, which no realisable
Reynolds stress can violate. Rescaling those cells onto the bound (a post-hoc
projection, not a model) drops the RMS from 47.68 to **0.567**; on the held-out
duct `AR_1_Ret_360` the same rescaling takes 6.38 to **0.411**.

Report the median, p90, p99 and the fraction over `sqrt(2/3)` next to any
anisotropy RMS. An RMS alone cannot distinguish a uniformly mediocre model from a
good model with an unbounded tail, and only the second one diverges when you put
it in a solver.

## Durbin's time-scale bound is not Reynolds-similar and must not be applied across cases of different physical scale

`_common/tensor_basis.py` bounds the turbulent time scale as
`T = max(k/eps, 6 sqrt(nu/eps))` (Durbin). For the tensor-basis normalisation
`S_hat = T * S`, that bound is **not** a small correction:

| case | fraction of cells where the Durbin bound is the active branch | `k/eps` p99 | `T` actually used, p99 |
|---|---|---|---|
| `PHLL10595` | 8.85 % | 16.5 | 16.5 |
| `alpha_15_13929_4048` | 11.3 % | 31.7 | 31.7 |
| `CBFS13700` | **45.97 %** | 170.4 | **4045** (24x) |
| `AR_1_Ret_360` | **71.77 %** | 2.27e-4 | 5.34e-3 -- max 0.559 (**2500x**) |

`k/eps` is Reynolds-similar: it is a ratio of the flow's own quantities and its
invariants are dimensionless whatever the units. `6 sqrt(nu/eps)` is not: it
introduces `nu` explicitly, so it scales with the case's physical size and
Reynolds number. The hills are non-dimensional (`H = 1`, `nu = 1.786e-4`); the
ducts are dimensional (`h = 1 mm`, `nu = 1.5e-5`). Applying the bound to both puts
their normalised strain tensors in different regimes and **destroys the very
similarity a tensor-basis feature set exists to exploit**.

The bound is correct for its own purpose — preventing `T -> 0` at a wall where `k
-> 0` at finite `eps`. It is wrong wherever `k` and `eps` vanish together, because
then `6 sqrt(nu/eps) -> infinity` while `k/eps` stays finite. Kaandorp's eq. (7)
uses `k/eps` with no bound and is right to.

**The effect was isolated by rerunning the identical pipeline with the bound
removed**, same seeds, same splits, same code. On the strictly held-out square
duct `AR_1_Ret_360`, the 16-feature TBRF's held-out anisotropy error goes from
`b_rms_F = 6.382 +/- 2.110` (bound on) to **`0.3160 +/- 0.0080`** (bound off) --
from 10.9x worse than the k-omega SST baseline (0.5843) to **45.9 % better** than
it. The extrapolation statistic moves with it: the Mahalanobis p95 of the duct's
feature vectors against the training cloud falls from **36.00** to **6.20**,
against a training-sample p95 of 6.59. One `np.maximum` in a shared helper module
was the difference between a model that extrapolates and one that does not.

## Storing an anisotropy tensor as float32 fabricates realisability violations

`b_LES` on `CBFS13700` has **4.60 % of cells sitting exactly on an edge of the
barycentric triangle** — minimum barycentric coordinate exactly `0.0` in float64.
Round-tripping through float32 moves them to `-2.98e-8`, and a zero-tolerance
Schumann realisability test then reports 4.60 % of the *reference DNS/LES data* as
unrealisable. It is not; the same data in float64 reports 0.00000 %.

Any realisability fraction quoted from a float32 array needs a tolerance above
`3e-8`. This run uses `tol = 1e-7`, which is six orders below any physically
meaningful violation and clears the float32 floor. `BASELINES.md` sec. 5 computes
in float64 and is unaffected; its CBFS truth row (0.0000) is the correct one.

## Wall distance from `polyMesh` wall patches: exact in the median, 0.5 % in L2

The `DUCT`, `PH_Breuer` and `CBFS` cases ship no `walldist`. Computing it as the
distance from each cell centre to the nearest face centre **or vertex** of a
patch of `type wall`, and checking against the `walldist` OpenFOAM itself wrote on
the 29 hills:

* median cellwise relative error **2e-15 to 1e-14** — machine precision,
* relative L2 over the whole field **0.055 % to 0.47 %**,
* worst absolute error 0.004 to 0.049 hill-heights,

i.e. exact everywhere except a handful of cells where the true nearest point on a
wall face is neither its centre nor one of its vertices. Good enough for a
wall-distance Reynolds number; not good enough for a `y+`-critical quantity
without refining the target point set.

## Cost, measured

100 tensor-basis decision trees on 21,000 samples x 16 features, 10x10
least-squares at every candidate split, exact brute-force threshold search below
2048 samples per node and 128 quantile candidates above it, `min_samples_leaf = 9`:
**85 s wall on 16 cores** (~0.38 core-hours per forest), 1817 leaves per tree.
Fully grown (`min_samples_leaf = 1`): 127 s, 13,201 leaves per tree. The prefix-sum
trick — accumulating `A_i = That_i^T That_i` and `c_i = That_i^T bhat_i` once per
sample and taking a cumulative sum over the feature-sorted order — makes an exact
brute-force split search cheaper than the paper's Brent 1-D search and removes the
paper's own 150-sample fallback threshold entirely.


## A-posteriori propagation of a b-only correction — appended 2026-08-21 (Lane B, reviewed by supervisor)

**N-B22. Injecting an anisotropy made the duct solve converge ~60x faster in
iterations, and that is not evidence of accuracy.** Same solver, same mesh, same
start field, same stopping rule (all of U, p, k, omega initial residuals < 1e-6),
`AR_1_Ret_360` (3,025 cells):

| configuration | iterations to the same stopping rule | wall s |
|---|---|---|
| NULL (zero correction) | **> 30,000** (still running at cap check) | -- |
| TRUTH (`b_LES - b_RANS`) | **528** | 7 |
| MEAN (constant tensor) | 1,427 | 17 |
| ML seed 0 / 1 / 2 | **523 / 527 / 522** | 8 / 8 / 7 |

Mechanism, and the reason it is not a quality signal: a linear eddy-viscosity
model produces a secondary flow that is identically zero to machine precision
(`BASELINES.md` sec. 4), so in the NULL run OpenFOAM normalises the cross-plane
momentum residuals by a field of magnitude ~1e-16 and the normalised `Uy`/`Uz`
residuals sit at O(0.3) with nothing to converge *to*. Any non-zero `bijDelta`
gives the cross-plane equations a real source, a real scale, and therefore a
real residual that can fall below 1e-6.

**What cannot be concluded:** that the corrected model is better conditioned, more
accurate, or cheaper in general. TRUTH and ML converge in nearly the same number
of iterations (528 vs 523) while being very different fields, so iteration count
here measures *whether the residual normaliser is non-degenerate*, not solution
quality. Report iteration counts per configuration, and never let "converged
faster" stand in for "converged to something better" - the `U_rms` column is the
only one that answers that.

**N-B23. Quote both comparators for an a-posteriori row: the shipped baseline and
your own zero-correction run.** They are not the same number. The shipped duct
fields stopped on a `residualControl` listing only `k` and `omega`
(`k 5e-6; omega 1e-10;`), leaving streamwise momentum at an initial residual of
1.6e-3 (`AR_1_Ret_360`) and 9.3e-4 (`AR_3_Ret_360`) - one to three orders short of
the 1e-6 used for every configuration here. Scoring an injected run against the
shipped field silently credits (or debits) the model with the benchmark's own
convergence gap. Fix: run NULL under the identical solver, mesh copy and stopping
rule, use it as the comparator, and report `NULL - BASE` once as a named quantity.

**N-B24. Injecting an anisotropy correction with no k-correction collapses the
transported turbulent kinetic energy, and the velocity field gets worse even when
the anisotropy is exactly right.** Measured, `kOmegaSSTCorrected` with
`bijDelta = b_LES - b_RANS` and `kDeficit = 0`:

| Case | `k` mean, baseline SST | `k` mean, truth-injected | ratio to baseline | ratio to `k_LES` |
|---|---|---|---|---|
| `AR_1_Ret_360` (duct) | 26.68 | **8.74** | **0.33** | 0.20 |
| `CBFS13700` | 0.00302 | 0.00275 | 0.91 | 0.68 |

Mechanism: the model realises `tau = 2k(b_lin + b^Delta)` with `k` from the
current iterate, and the `k`-equation production is
`P_k = -2k(b_lin + b^Delta):grad(U)`. Injecting `b^Delta` changes production with
nothing to balance it, so `k` finds a new and much lower equilibrium; the
realised stress is then scaled by that factor no matter how good `b^Delta` is.
Consequence measured on all three cases: `b_rms` against the LES improves by a
factor of **23** (0.5833 -> 0.0251 on the duct) while `U_rms` **worsens by
57-63%**.

The control that isolates it: the same solver and the same injection path, given
**both** corrections (`b^Delta` and `R`), reaches the published `eps(U)/eps(U_0)` = 0.00165 on (the lab's own W2 measurement: 0.003331; still ~300x) [dated correction 2026-08-21: originally quoted '0.0017' as the lab's own number] -
PH10595 (`verification/campaign/W2_SPARTA_FROZEN_CBFS.md`). The path is sound;
the `b`-only configuration is what fails - and `b`-only is all a model that
predicts `b_ij` alone can supply. **Any a-posteriori plan for a `b_ij`-only
closure must either carry a k-correction or freeze `k`, and must say which.**

**N-B25. The duct secondary flow is recovered from a structural zero, and that is
independent of the velocity getting worse.** Injecting `b^Delta` moves the duct
in-plane velocity from **0.0000%** of bulk (machine zero, as a linear
eddy-viscosity model requires) to **0.365%** with the true anisotropy and
**0.330-0.356%** with the learned one, against a DNS **1.508%** - about 24% of
the true magnitude, from nothing. Reported because it is the one thing in this
lane that worked exactly as the literature promises, and because it shows the
injection path is wired correctly: a bug would not produce a physically-shaped
secondary flow of the right sign and order.


## Kaandorp a-posteriori: the broken b-only path, the div(U) instrument floor, and the b+R control — appended 2026-08-21 (Lane 1, reviewed by supervisor)

## N-K1. The Pope tensor basis is rank 3 to 4 on every flow in this benchmark, and that is where a tensor-basis model's extrapolation error comes from

Pope's integrity basis has 10 tensors, so a tensor-basis model fits 10
coefficients `g^(m)`. **The 10 flattened basis tensors do not span 10
dimensions on real data.** Mean numerical rank of the 9x10 matrix
`[T^(1) ... T^(10)]` at a cell (tol `1e-8 max|T|`, 500-cell sample):

| case | mean rank |
|---|---|
| `AR_1_Ret_360` (square duct) | **3.089** |
| `AR_1_Ret_180` (square duct) | 3.09 |
| `CBFS13700` (curved step) | 3.988 |
| periodic hills | 3.82 - 3.98 |

A sibling reproduction with different code and a different split measured 3.24
over its own pool: independent agreement.

Consequences, both measured. (1) Six of ten coefficients are unconstrained, and
Kaandorp's `Gamma` = 1e-12 does nothing against normal-equation entries of order
1e4: over all leaves of a 100-tree forest, `median |g|` = 2.6e-5,
`p99 |g|` = 3.4e4, `max |g|` = 4.0e6. (2) They then multiply basis tensors three
decades outside their training range — `||T^(7)||_F` p99 is **1.02e6** in the
training pool and **1.74e9** on the duct.

**Rule.** Any model `b = sum_m g^(m)(features) T^(m)` must report the numerical
rank of `T` on the *prediction* case, or truncate the basis to that rank, or
regularise at a magnitude meaningful relative to `sum T^T T`. `Gamma` = 1e-12
against `1e4` is `Gamma` = 0.

## N-K2. An RMS on a closure prediction hides the failure mode; report the distribution

On `CBFS13700` the 16-feature TBRF's error field: median **0.170**, p90 **3.40**,
p99 **153.9**, RMS **47.68** — against an SST `b_rms` of 0.319. The median cell
beats the industrial closure; the RMS is 156x worse. The tail is **15.0 % of
cells** violating `||b||_F <= sqrt(2/3) = 0.8165`, which no realisable Reynolds
stress can violate. Rescaling only those cells onto the bound takes the RMS to
**0.567** (and 6.38 to **0.411** on the held-out duct). Report median, p90, p99
and the over-bound fraction beside any anisotropy RMS.

**Median-over-trees is worth four orders of magnitude.** Same forests, mean over
trees instead of Kaandorp's median: `AR_1_Ret_360` **67,860** vs 6.382,
`CBFS13700` **256** vs 47.68. Their sec. 2.5 aggregation choice is not stylistic.

## N-K3. Durbin's time-scale bound is not Reynolds-similar and must not be applied across cases of different physical scale

`T = max(k/eps, 6 sqrt(nu/eps))`. For the tensor-basis normalisation
`S_hat = T S` that bound is not a small correction:

| case | fraction of cells where the Durbin branch is active | `k/eps` p99 | `T` used, p99 |
|---|---|---|---|
| `PHLL10595` | 8.85 % | 16.5 | 16.5 |
| `alpha_15_13929_4048` | 11.3 % | 31.7 | 31.7 |
| `CBFS13700` | **45.97 %** | 170.4 | **4045** (24x) |
| `AR_1_Ret_360` | **71.77 %** | 2.27e-4 | max 0.559 (**2500x**) |

`k/eps = 1/(0.09 omega)` is Reynolds-similar; `6 sqrt(nu/eps)` carries `nu`
explicitly and is not. The hills are non-dimensional (`H` = 1,
`nu` = 1.786e-4), the ducts are meshed in millimetres (`h` = 1 mm,
`nu` = 1.5e-5). Removing the bound moved the held-out duct from
`b_rms_F` **6.382 ± 2.110** to **0.3160 ± 0.0080**, and the feature-space
Mahalanobis p95 from **36.00** to **6.20** against a training p95 of 6.59.

## N-K4. Storing an anisotropy tensor as float32 fabricates realisability violations

`b_LES` on `CBFS13700` has **4.60 % of cells sitting exactly on an edge of the
barycentric triangle** in float64 (min coordinate exactly 0.0). A float32
round-trip moves them to **-2.98e-8**, and a zero-tolerance Schumann test then
reports 4.60 % of the *reference LES data* as unrealisable. Use `tol >= 1e-7`.

## N-K5. Wall distance from `polyMesh` wall patches: exact in the median, 0.5 % in L2

Distance from each cell centre to the nearest face centre **or vertex** of a
`type wall` patch, checked against the `walldist` OpenFOAM wrote on the 29 hills:
median cellwise relative error **2e-15 to 1e-14**, relative L2 **0.055-0.47 %**,
worst absolute 0.004-0.049 `H`.

## N-K6. Cost of an exact tensor-basis decision tree

100 TBDTs on 21,000 samples x 16 features, 10x10 least squares at every candidate
split: **85 s wall on 16 cores** (~0.38 core-hours per forest), 1817 leaves per
tree; fully grown (`min_leaf` = 1) 127 s and 13,201 leaves. Accumulating
`A_i = That_i^T That_i` and `c_i = That_i^T bhat_i` once per sample and taking a
cumulative sum over the feature-sorted order makes an **exact brute-force**
threshold search cheaper than the paper's Brent 1-D search, and removes their
150-sample fallback entirely.

---

# SECTION B — a-posteriori injection lane (`RESULTS.md` in this directory)

## N-K7. `kOmegaSSTCorrected` with zero corrections is bit-identical to stock `kOmegaSST`

Registered gate G0a: run stock `kOmegaSST` and `kOmegaSSTCorrected` with
`bijDelta = 0`, `kDeficit = 0`, `bScale = RScale = 1` from the same shipped start
for the same 200 iterations. Measured relative L2 difference in `U`:
**0.0 exactly** (`AR_1_Ret_360`, 3025 cells, 3.9 s vs 4.0 s). The gate was
registered at 1e-10; the answer is round-off-free.

**Do not phrase this gate as "re-solve to convergence and compare to the shipped
field".** The shipped benchmark fields are not converged to 1e-10 — restarting
the converged `AR_1_Ret_360` solution gives an initial `Ux` residual of
**1.8e-5** — so any further iteration moves `U` by far more than 1e-10 for
reasons unrelated to the correction terms, and that form of the gate fails on a
correct solver. Compare two solvers over an identical trajectory instead.

## N-K8. Injecting `b^Delta` without `R` collapses `k`, and inverts the propagation ceiling

Registered choice: `kDeficit` (R) = 0, because the TBRF predicts `b` only.
Measured consequence on `AR_1_Ret_360`, mean `k`:

| configuration | mean `k` | mean `nu_t` | `U_rms` |
|---|---|---|---|
| LES truth | **43.42** | — | 0 |
| shipped k-omega SST | 26.68 | 6.65e-5 | 0.1985 |
| zero-correction control (30,000 it) | 26.71 | 6.65e-5 | 0.19874 |
| **truth `b`, R = 0** | **8.74** | 2.88e-5 | **0.3215** |
| train-mean `b`, R = 0 | **0.128** | **4.03e+7** | 0.6826 |
| TBRF `b`, R = 0 (seed 0) | 5.25 | 1.96e-5 | 0.2594 |
| **truth `b` AND `R`** (frozen extraction) | — | — | **0.00341** |

Injecting `b^Delta` changes k-production by `Gextra = -2 k (b^Delta : grad U)`,
strongly negative here. With no `R` to balance it `k` collapses, `nu_t` follows,
and the momentum correction `2 k b^Delta` shrinks toward zero simultaneously —
so the "true anisotropy" injection ends up **62 % worse than the baseline it was
meant to bound**. With `R` extracted by `kCorrectiveFrozenFoam` and propagated
alongside, the same case gives `U_rms` = **0.00341**, a **98.3 % reduction**.

`b^Delta` and `R` are not two independent corrections you can take one of. A
`b`-only learned closure that is propagated needs its own k-equation treatment
(Kaandorp's "modified k-equation") or it will be graded against a ceiling that is
below its own baseline.

## N-K9. A residual-based convergence criterion fails on a periodic duct driven by a source term

`AR_1_Ret_360` is streamwise-periodic with a `meanVelocityForce`. After **30,000
iterations** of the zero-correction control the initial residuals are:

| field | initial residual at iteration 30,000 |
|---|---|
| `p` | **0.144** |
| `Ux` | **8.4e-16** |
| RMS `div(U)` / gradient scale | **6.1e-18** |

The field has not moved (`U_rms` 0.19874 against the published SST 0.1985) and
`p` is *converged*: the cross-plane pressure is nearly uniform, so OpenFOAM's
residual normaliser divides by a near-zero scale. Two related traps in the same
case: the baseline has `Uy, Uz ~ 0`, so their initial residuals are **O(0.3) at
restart with zero corrections**; and a solver that stops at first satisfaction of
`residualControl` can never exhibit a criterion phrased as "sustained for 100
iterations".

Use field movement between checkpoints as the primary convergence measure for any
flow whose driving pressure gradient is a source term rather than a boundary
condition, and read the zero-correction control's residuals before registering a
criterion.

## N-K10. Continuity, re-solved, against this lab's own published post-hoc figure

Volume-weighted RMS `div(U)` normalised by the field's own gradient scale:

| configuration (`AR_1_Ret_360`) | RMS `div(U)` / gradient scale |
|---|---|
| zero-correction control | **6.1e-18** |
| train-mean `b` injection | 4.0e-5 |
| truth `b` injection | 1.1e-4 |
| truth `b` **and** `R` | 1.7e-4 |
| TBRF `b` injection (3 seeds) | 3.1e-4 to 3.8e-4 |
| **lab's published post-hoc correction** (`METHOD.md` §6.2) | **10.5 %** and **9.7 %** |

Re-solving buys between **2.5e4x** and **1.7e16x** on continuity. Charter §22.2's
"continuity by construction" is not a figure of speech; it is five to sixteen
orders of magnitude, and the cheapest way to earn it is to put the correction
inside the equations rather than on top of the answer.

## DAFoam-team numerics, continued — appended 2026-08-21 by Lane B

**Placement note.** The `N-D` block proper sits above, ending with `N-D5`. This entry is
appended at end-of-file rather than inserted after `N-D5` because the closure team is
committing into this file concurrently — the file grew 2,555 -> 2,732 lines during this
session — and an in-place insert is not an append-only edit. The id is re-derived by
command, never quoted: `grep -o 'N-D[0-9]*\.' docs/NUMERICS_KNOWLEDGE.md | sort -n | tail -1`.

**N-D6. An exactly singular incomplete factorization is not reachable by any shift,
fill or pivot tolerance, and the log banner that seems to prove otherwise is emitted by
the caller.** Measured on CBFS, 21,000 cells, `dRdWTPC` 210,592 x 210,592 with
**13,710,468** nonzeros, np = 4, ASM + sub-block ILU, image `dafoam-kspopts:v1`
(`d9d2aed02e36`) — the build in which PETSc runtime options are *not* discarded.
Five arms, each with `-ksp_view`:

| `PETSC_OPTIONS` | deployed sub-PC | iterations | reason |
|---|---|---|---|
| control, none | `type: ilu`, `1 level of fill`, `[NONZERO]`, zero-pivot tol `2.22045e-14` | 0 | **-9** |
| `-sub_pc_factor_shift_type nonzero` | **identical to control** | 0 | **-9** |
| ` + -sub_pc_factor_shift_amount 1e-10` | **identical to control** | 0 | **-9** |
| ` + -sub_pc_factor_shift_amount 1e-8` | **identical to control** | 0 | **-9** |
| `-sub_pc_factor_levels 2` | **identical to control — dump still reads `1 level of fill`** | 0 | **-9** |

Iteration-0 residual `7.091590452305e-04` to all 13 digits in all five, and the whole
`-ksp_view` region is byte-identical across arms apart from wall-clock stamps. PETSc emitted
**no** unused-option warning: the options were consumed at `KSPSetUp` and then **overwritten**
by the application's own `PCASMGetSubKSP` loop, which calls `PCFactorSetShiftType`,
`PCFactorSetShiftAmount` and `PCFactorSetLevels` per block afterwards. **Last write wins, and
the application writes last.**

**Two numbers to carry.** (i) The banner `using diagonal shift to prevent zero pivot
[NONZERO]` appears in the **control**, which set no shift option — it is the application's
own `MAT_SHIFT_NONZERO`, so its presence proves nothing about whether a command-line shift
landed. The discriminating tell is a requested value the application also sets to something
*different*: fill level 2 requested, `1 level of fill` deployed. (ii) The one factor option
the application never sets, `zeropivot`, **does** reach the deployed factor — verified
visible in `PCView` at `1e-08`, six decades up — and still returns `-9`.

**Mechanism, reproduced with no DAFoam and no PETSc in the loop:**
`scipy.sparse.linalg.spilu` on the dumped matrix raises `RuntimeError: Factor is exactly
singular` at drop_tol/fill of 1e-2/3, 1e-3/5, 1e-4/5 and 1e-5/10 — the whole strength axis —
while `splu` solves at every `diag_pivot_thresh` (residual 2.3769e-10, 6.4063e-12,
2.535461e-12). The matrix has **0 zero rows, 0 zero columns, 0 zero diagonal entries** and a
diagonal spread of only **log10 8.67** (against 14.17 on a case that fails for a different
reason), so this is not ill-conditioning either.

**The rule: a shift, a drop tolerance and extra fill all perturb an incomplete factorization.
If the factor is *exactly* singular rather than *nearly* singular, none of them is the right
lever, and a sweep over them buys a closed axis, not a fix.** Complete factorization with
pivoting is what works — `splu` offline, `PCLU` in-solver — and in this stack that costs a
source rebuild: 0 iterations / `-9` becomes **667 iterations / `reason 2`**.


## Xiao 2016 harness: the continuity-estimator floor across seven fields, and the clip-fraction diagnostic — appended 2026-08-21 (Xiao lane, reviewed by supervisor)

## N-X1. The structured-gradient divergence estimator floors at ~1e-2 on curved benchmark meshes — calibrate before registering a continuity tolerance

`of_read.structured_gradient` is exact to round-off where there is no streamwise
derivative to discretise, and three decades short where the mesh is curved.
Measured on fields whose divergence is already known to be zero:

| mesh | field | RMS `div(U)` / gradient scale |
|---|---|---|
| `AR_1_Ret_360` duct (cross-plane) | shipped converged SST | **4.5e-18** |
| `AR_3_Ret_360` duct | shipped converged SST | **1.2e-17** |
| `CBFS13700` curved step | shipped converged SST | **5.2e-03** |
| `CBFS13700` | interpolated LES truth | **4.3e-03** |
| **`PH_Breuer` periodic hill** | **shipped converged SST** | **9.45e-03** |
| **`PH_Breuer`** | **interpolated LES truth** | **5.90e-03** |
| `alpha_10_9000_3036` hill, forward model reproducing the SST stress | — | 7.60e-03 |

Both reference fields on every curved mesh sit at the same order, which is the
signature of an estimator floor rather than a field property. **An absolute
continuity threshold below ~1e-2 is unmeasurable on these meshes.**

Registered generalisation, accepted for this lab's closure lanes: use
**OpenFOAM's own `time step continuity errors : sum local`** from the solver log
as the primary continuity measure — it is flux-consistent and exact to round-off
for a converged SIMPLE solve — and report the structured-gradient value as a
**ratio to the shipped baseline's own value on that mesh**, with a healthy band of
`[0.5, 2.0]`, rather than against any absolute number.

## N-X2. Prescribing the true Reynolds stress explicitly diverges on a separated hill at benchmark Reynolds numbers, and the clip fraction is the diagnostic

Forward model: `tau_model = (2/3)k I − 2 nu_t S + 2k b^Delta` with
`b^Delta = b_target + (nu_t/k)S`, so `tau_model = tau_target` exactly at
convergence while the linear part stays implicit. Outer deferred-correction loop
on `S`. Identity-verified: prescribing the baseline SST stress returns the
baseline `U_rms` to **1e-4** at both Reynolds numbers tested.

Prescribing the **LES truth** stress:

| `Re_H` | implicit viscosity | `U_rms` (baseline for that case) | outer loop | `nu_t^L` clipped |
|---|---|---|---|---|
| 10595 | frozen baseline SST `nu_t` | 0.29799 (0.1565) | oscillating | n/a |
| 10595 | optimal `nu_t^L` clipped ≥ 0 | **3.8815** | **diverging** | **47.0 %** |
| 5600 | frozen baseline SST `nu_t` | 0.31210 (0.1556) | slowly decaying, 9 % at outer 6 | n/a |
| 5600 | optimal `nu_t^L` clipped ≥ 0 | 0.47467 | oscillating | **23.9 %** |

`nu_t^L = −⟨tau_dev : S⟩/(2⟨S : S⟩)` is Wu, Sun, Xiao & Wang's conditioning fix,
and **applying it made the `Re` = 10595 case thirteen times worse**. The number
that explains it is the clip count, not the error: nearly half the domain wants a
**negative** eddy viscosity against the true stress, clipping at zero is forced
for stability, and it removes the implicit stabilisation precisely in the shear
layer that sets the solution.

Halving the Reynolds number halves the clip fraction (47.0 % → 23.9 %) and
improves the optimal-projection error 8.2x, but leaves the best configuration
**8.7x above its acceptance gate** — no better relative to the gate than at twice
the `Re`. Xiao et al. (2016) ran this propagation at `Re_b` = 2800 on **1,500
cells**; these attempts were 15,600 cells at 3.78x and 2.0x that `Re`.

**By contrast, the same case propagates correctly when the correction carries `R`
as well as `b^Delta`:** `U_rms` = **0.009319** on PH10595 against a 0.1565
baseline (94.0 % reduction), independently reproducing the W2 SpaRTA record's
`eps(U)/eps(U_0)` = 0.003331 to 3 %. The explicit-stress route and the
`b^Delta`+`R` route differ by two orders of magnitude on identical data.

## N-X3. Cost of a prescribed-stress forward evaluation on a 15,600-cell hill

Single core, outer deferred-correction to `max|dU|/|U| < 1e-5`: **4 outer
iterations, 1,624 SIMPLE iterations, 99.7 s = 0.0277 core-hours** when it
converges; **6 outer x 2,000 = 967.6 s = 0.269 core-hours** at the registered caps
when it does not. A 60-member, 10-iteration ensemble is therefore **16.6 to 161.3
core-hours** — a band, not a number, because it is bounded by caps rather than by
a convergence guarantee, and the honest costing says so.

**N-D7. Three ways to measure a decomposition effect that is not there, and the numbers each
one produces.** Measured 2026-08-21 on CBFS, 21,000 cells, DAFoam + `PCLU` sub-blocks,
comparing `scotch`, `simple (4 1 1)` and serial np=1 against each other
(`cases/dafoam/ladder-b/B3/decomposition_np4/RESULTS.md`). **The true answer is that the
gradient is decomposition-invariant at ~1e-04**: 1.680861e-04 (scotch vs serial),
1.415579e-04 (simple vs serial), 1.132033e-04 (simple vs scotch), all PASS against a <1e-3
band, all landing exactly on the "invariant at ~1e-04" a prior reach matrix predicted.
**Each of the three errors below produces a confident wrong answer instead.**

**(i) Setting the partitioner by editing `system/decomposeParDict` does nothing, silently.**
`pyDAFoam._writeDecomposeParDict()` (`pyDAFoam.py:2212`, called from `:1463`) **rewrites that
file on every run** from `daOptions["decomposeParDict"]`, default
`{"method": "scotch", "simpleCoeffs": {"n": [2,2,1]}}`. An arm staged by editing the file ran
`scotch` and returned `reason 2`, **667** iterations, objective `1.5279278906359758e-02` and
`‖g‖ 1.4558046603e-05` — **bit-identical to the scotch reference in every digit**. On a case
whose registered prediction is *invariant*, that is precisely the answer that gets believed.
**Set it in `daOptions`, and read the decomposition back out of the arm's own directory
afterwards.** A second tell: the three partitionings have **different cold-start continuity
errors** (`9.30211816115683e-06` scotch / `1.19187582101953e-05` simple / `1.12896526821488e-05`
serial) and stop at **1580 / 1582 / 1584** primal iterations — an arm matching the reference's
cold start to all 15 digits did not repartition.

**(ii) Comparing distributed-ordered gradients without the permutation inflates the answer
9,977x.** The per-cell DV index is a distributed ordering (rank-concatenated local cells; DV
index k -> serial cell `cellProcAddressing_r[c]`). Same two vectors, same norm:
**unmapped 1.412254e+00 = 141.2 % (GATE FAIL), mapped 1.415579e-04 = 0.01416 % (PASS)**;
they differ in **20,930 of 21,000** positions. **This is a headline-grade false positive** —
it would have moved the case out of the clean column and put a cloud over every gradient
downstream of it. Assert the permutation is a bijection onto `0..N-1` in code, not in review.

**(iii) A reused Jacobian-coloring file is the one that fails safely.**
`dRdWColoring_<nranks>.bin` is keyed on **rank count only**, so a coloring computed under
`scotch` loads happily under `simple`. DAFoam validates it and **aborts** —
`Conflicting Colors Found!`, `DAColoring/DAColoring.C:1021`, `row: 105370 col1: 52784
col2: 52785 color: 0` — rather than returning a wrong Jacobian. Delete
`dRdWColoring_*.bin` whenever the decomposition changes.

**A fourth number worth carrying, about the ASM rather than the errors: removing the block
boundaries is worth 4.09x in Krylov iterations.** Serial np=1 with `PCLU` over the whole
210,592² operator converges in **163** iterations against **667** at np=4 under `scotch` and
**766** under `simple` — and its predicted 10-14 GiB peak never materialised, the cap was never
approached, because a single ASM block with PETSc's own LU is not the same object as an offline
SuperLU factorization of the same matrix.

**And the gate that was wrong: "objective bit-identical" is only defensible between runs that
share a decomposition.** Across np=1/4 and across two partitioners the objectives spread
**1.9e-07** (`1.5279275989724403e-02` / `1.5279278906359758e-02` / `1.5279278602317540e-02`),
because the primal stops on a **1e-06 residual tolerance**, not at a fixed point, and the
parallel reduction tree differs. That is ~3 decades below where the graded gradient rows sit
and is reconvergence noise, not a finding — but it was registered as bit-identical, so it is
recorded as **GATE FAIL and a missed prediction** rather than rewritten after the fact.

**N-D8. A4 Ahmed body, np=1, `dCD/dshape`, the complete 2×3 table.** Measured 2026-08-22
(`cases/dafoam/ladder-a/A4/shipped_optimisation_np1/RESULTS.md`). Baseline: **1.1032 %** shipped,
**0.33929 %** patched (`3.392911e-03`, hash-certified on `dafoam-idwarp-rot:v1`). Optimised design
(`shape = −0.05`): **0.3112 %** shipped, **0.4936 %** patched. The two endpoint *analytic* gradients
are `0.21410204` / `0.21410121` — 3.9e-06 apart — while the two *FD references* differ by 1.83e-03;
the endpoint rows are not a toolchain comparison (L-229). The rotation defect's effect on the
analytic gradient falls from **1.85e-03 (0.766 %)** at `shape=0` to **8.3e-07 (0.00039 %)** at
`shape=−0.05`, ≈2,000×: regime 1 decays with deformation, and regime 2 does not replace it above
≈4e-06 relative on this DV. Also: at an active bound IPOPT's dual infeasibility is `∇f − z_L` and
certifies convergence on a ~1 %-wrong gradient — convergence at a bound is a weak toolchain
discriminator.

**N-D9. A2 MACH wing, 96 shape DVs, what sits under the passing aggregates.** Zero compute,
2026-08-22 (`cases/dafoam/ladder-a/A2/per_component_table/RESULTS.md`). Shipped `CD` 1.7138 %
hides 7 components beyond 15 % (max −360.75 % at idx18); shipped `CL` 1.1652 % hides idx15 at
−80.20 %; patched `CL` is 96/96 within 5 %; patched `CD` 0.0506 % carries one sign flip, idx46,
`+2.27367571e-06` vs `−2.52460969e-06`. The bind-mounted `W5-patch/idwarp/libidwarp.so` is md5
`85f59e87…`, the same binary `dafoam-idwarp-rot:v1` ships, so bind-mount-era patched rows are
same-stack but self-certify only where the run printed the hash.

**N-D10. Single-rank contention inflation on this box.** At host load ~20 (12 foreign single-rank
solvers on 16 cores) a DAFoam np=1 container at `--cpus=1` runs **1.104×** slower on an identical
work marker (`dRdWTPC: 800 of 1087`, 53.77 s vs 48.69 s). The 18–21× inflation measured on np=4
arms is the Open-MPI spin-wait and does not exist at one rank.

## T-family numerics, measured on this machine — appended 2026-08-22 (T-family lane, reviewed by supervisor)

## N-T1. The shared `gci()` prints the Richardson extrapolate with the wrong sign on every row

`analyse_t9a.gci()` forms `e21 = f_m − f_f` and returns
`richardson = f_f + e21/(r^p − 1)`; Roache's extrapolate is
`f_f + (f_f − f_m)/(r^p − 1)`. **The instrument that shows it grades nothing.**
R0's triple falls monotonically **20.425588 → 20.069440 → 19.854991**, so its
limit must lie below 19.854991 — and the comparator prints **20.179541**, above
the fine value, back toward the coarse. With the sign corrected the five T9a
extrapolates are **19.5304 W/m²** (+0.142 % from exact), **348.77941 K**
(−1.68 mK), **300.02447 K** (+0.10 mK), **0.833179** (−0.0069 %) and
**0.752394** (+0.0022 %) (`T9a_RESULTS.md` §8.1).

**The `richardson` field is stored in the printed grid-triple dict and read by
no verdict; the GCI uses `|e21|` and is unaffected**, so no published number
moves either way. T9a-D's own selftest puts the two side by side on T9a's R0
triple: frozen `analyse_t9a.gci()` **20.179541**, sign-correct instrument
**19.530441**, **GCI band 2.0432503592470312 % — identical** in both
(`T9aD_RESULTS.md` §7).

**The repair is carried as a new instrument, not as an edit.** T10a inherited
the shared `gci()` **unedited** and stores the corrected values alongside as
`richardson_corrected` — landing at 6484.988 / −3267.594 / −1253.959 /
−1963.534, within **0.001–0.063 %** of exact on all four box rows — while "the
triple dict's `richardson` field carries the sign defect T9a §8.1 already
recorded in the shared `gci()`, unedited, on no grading path"
(`T10a_RESULTS.md` §1.1). `analyse_t9aD.py` carries **its own** sign-correct
`gci()`, written before any `D_*` case existed, with the frozen
`analyse_t9a.gci()` imported and **not called on any T9a-D row**; T10a-R
declares the sign-corrected Richardson as **NEW INSTRUMENT 1**, graded on row
RX5 against `[0, 0.100]` %. A repair cannot change a number a verdict depends
on, so it belongs in the next comparator and not in the frozen one.

## N-T2. A CONVERGING Roache triple can arm a band narrower than the finest level's actual error — and the same quantity's next triple arms one 11× too wide

The Roache GCI reads the observed order from **successive differences**. When
the level errors are ~first order **and slowing**, the differences fall faster
than the errors, `p` reads high, and the band closes under the remaining error.
Two independent instances, then the inverse.

| triple | armed band | actual deviation of finest | observed `p` | level-error ratios | verdict |
| --- | ---: | ---: | ---: | --- | --- |
| T9a **R1**, interface-1 `T`, c/m/f | **0.92 mK** (0.000263 %) | **2.41 mK** (0.00069 %) | 1.738 | 1.63 then 1.38 | GATE FAIL, 2.63 bands outside |
| T10a **B1**, box ceiling `q`, c/m/f | **0.07676 %** | **0.12463 %** (4.070 W/m²) | 1.480 | 1.66, 1.50 | GATE FAIL, 1.62 bands outside |
| T9a-D **B0/B2**, same `T` as R1, m/f/x | *(none armed)* | **1.54 mK** | **0.130, STAGNANT** | 1.57 | **NOT A RESULT** |

**T9a R1.** Interface-1 temperature moved 2.10 then 0.93 mK per refinement
(ratio 2.264, `p` = 1.738), arming 0.92 mK, while against exact the three
levels are off by **−5.43 / −3.33 / −2.41 mK** — shrinking at roughly first
order and then slower, not at the `p` = 1.74 the differences imply
(`T9a_RESULTS.md` §1.1). **T10a B1.** The ceiling triple moves 4.045 then
2.017 W/m² (ratio 2.005, `p` = 1.480) and arms 0.077 %, while the level errors
are **−10.13 / −6.09 / −4.07 W/m²** (ratios 1.66, 1.50), roughly first order
(`T10a_RESULTS.md` §1.1).

**And the fourth level makes the band worse, not better.** Adding level `x`
(145 cells), the error continues down cleanly — `e1` goes
−3.335 → −2.409 → **−1.538 mK**, ratios 1.384 then 1.566, still first order —
but the successive *differences* are −0.926 then −0.871 mK, barely shrinking,
so the m/f/x triple reads **`p` = 0.130, STAGNANT** and by the registered rule
**no band may be armed**. Had one been armed anyway it would have been
**17.21 mK against a 1.54 mK error: 11× too WIDE** (`T9aD_RESULTS.md` §2.2).

**Same quantity, same solver, same error mechanism, same first-order error
sequence** — −5.43 / −3.34 / −2.41 / −1.54 mK, ratios 1.63 / 1.38 / 1.57 —
**and the band lands on opposite sides of the truth by an order of magnitude
depending on which three of the four levels you feed it**: 2.6× too narrow on
c/m/f, 11× too wide on m/f/x. The band is not measuring the error; it is
measuring how the differences happen to sit. (T9a §1.1 prints the second level
as −3.33 mK and T9a-D's four-level sequence as −3.34; the discrepancy is the
last printed place and changes nothing.)

## N-T3. `laplacian(DT,T) Gauss harmonic corrected` on a 1-D orthogonal mesh with the jump on a face is the exact series conductance, at any spacing ratio

The corrected harmonic face conductance reduces to

```
k_f/d = 1 / ( dx_P/(2 k_P) + dx_N/(2 k_N) )
```

**which is the series resistance of the two half-cells, exactly, for any
spacing ratio.** Measured: every harmonic level reproduces the closed form
**to all nine printed digits, on the 35-cell coarse mesh included** —
`D_A_c` (35 cells) returns `q″` **19.502681619** at **+0.0000000 %** and
`T_i1` **348.781082399** at **+0.0000000** deviation. T9a-D's interface 2 does
*not* have equal spacing either side at any level (`dx`
**0.0019608 | 0.0015385** at level `f`) and is reproduced to round-off anyway;
unequal spacing was flagged in pre-registration as a place a residual might
survive, and it does not (`T9aD_RESULTS.md` §2.1).

**What the arithmetic mean costs.** The frozen `Gauss linear` face conductivity
at the 0.8 | 0.04 interface is the arithmetic **0.42 W/mK** against the series
value **0.0762**, and at 0.04 | 16 it is **8.02** against **0.0798**. The
resistance those two faces fail to charge, at level `f`:

| contrast | interface 1 | interface 2 | total | fraction of `ΣR` | measured `q″` excess |
| --- | ---: | ---: | ---: | ---: | ---: |
| 400× | 2.090e-02 | 2.173e-02 | 4.263e-02 | **1.663 %** | **1.806 %** |
| 40× | 4.150e-04 | 2.050e-03 | 2.465e-03 | **0.786 %** | **0.879 %** |

**The mechanism predicts the measured flux excess to about 12 % of itself at
both contrasts, from nothing but the two face conductivities.**

**A flux-continuous interface-`T` reconstruction cancels most of it — but only
where the contrast is large.** Reconstructing the interface temperature from
flux continuity rather than reading the face value:

| contrast | before | after | error cancelled | weight on the high-`k` cell |
| --- | ---: | ---: | ---: | ---: |
| 400× | −22.02 mK | **−2.41 mK** | **89.1 %** | **95.3 %** |
| 40× | −87.57 mK | **−64.99 mK** | **25.8 %** | **67.1 %** |

At a 400× contrast the reconstruction is 95 % determined by the high-`k` cell
and **cancels 89 % of the flux error**; at 40× the weights even out and the
cancellation **collapses from 89 % to 26 %**. Reducing the contrast 400× → 40×
therefore *grew* the R1 error by 27–31× (−5.43 / −3.34 / −2.41 mK →
−168.06 / −104.16 / −64.99 mK), the opposite of what the directive predicted:
the relative flux error did fall, but only by **2.05×, not 10×**
(1.806 % → 0.879 %), because at 400× the two interfaces contribute the missing
resistance almost equally (49 % / 51 %) while at 40× interface 2 is **still a
40× jump** and supplies **83.2 %** of the deficit.

## N-T4. `viewFactorsGen`'s row-sum defect on the enclosing sphere does not refine with the mesh, and it is not a quadrature-tolerance artefact

Measured at build under held-fixed quadrature settings, the **outer-sphere raw
row-sum defect is 4.77 / 4.27 / 4.47 % at c/m/f** — a defect that does not
shrink with the mesh — while over the same ladder the **inner-sphere rows
converge, 0.48 → 0.30 → 0.11 %**, and the faceting deficit converges O(h²)
(**−0.538 → −0.211 → −0.080 %**) (`T10a_RESULTS.md` §1.1). A ladder in which
the geometric error terms shrink while the dominant matrix defect stays fixed
produces exactly what was observed: **both sphere triples DIVERGENT** — S0's
successive differences +0.729 then +3.362 W/m², S1's +0.953 then +2.261 — no
band armed, **NOT A RESULT**, with the finest levels at **−1.60 %** (inner) and
**+7.02 %** (outer) from exact.

**The attribution lever fires cleanly.** The comparator's own radiosity solve on
the written `F` **reproduces the solver to ≤ 8.2e-15** on every sphere case:
Python-on-`F` == solver != exact means **the view factors are wrong, not the
assembly**.

**And it is not the quadrature tolerance.** A `GaussQuadTol` 0.001 twin — ten
times tighter — **moves every row by at most 0.006 %**, orders below every
armed band, so the registered quadrature-floor gate fired nowhere.

**The cleanest single number is the control that was registered as zero.** The
solved **uniform-300 K box** was registered as "every flux 0 by symmetry"; the
solver returns **max |qr| = 13.95 W/m² against σT⁴ = 459.3 W/m² — 3.0 %**,
which is the raw row-sum defect of the written `F` (**1.9–3.0 %** on those
patches) passing straight through, since a uniform enclosure's `qr` is
`(Σ_j F_ij − 1)·σT⁴` per face. The control is MET regardless, and the figure
independently confirms that the graded rows' errors live in the view-factor
matrix.

The dedicated characterisation arm **T10a-VF is in progress** and nothing from
it is folded in here; every number above is T10a's own.

## N-T5. Serial `buoyantBoussinesqSimpleFoam` throughput on this box falls ~4.9× with cell count, against a planning figure that assumed 19 %

`nProcs = 1` on every case, serial, with the box shared with the DAFoam and
closure teams throughout, so wall includes contention and is an upper bound on
solver time (`T3_RESULTS.md` §9):

| case | cells | cell-it/core-s |
| --- | ---: | ---: |
| W_m | 28 160 | **3.78e5** |
| R_c | 36 000 | 2.20e5 |
| C_lam_m | 92 160 | 1.79e5 |
| D_m | 79 360 | 1.50e5 |
| R_m | 92 160 | 1.16e5 |
| P_m | 92 160 | 1.16e5 |
| O_m | 128 000 | 9.56e4 |
| R_f | 235 520 | **7.73e4** |

**Throughput falls by 4.9× from the smallest case to the largest — far more
than the "about 19 % slower above 100 k cells" the plan allowed for.** The
correct planning model for a 2D turbulent case on this box is not a constant
rate but one that degrades steeply with cell count, most likely on cache
residency. `R_f` was expected to take 3.3 h uncontended or ~6.7 h at the
smoke-test rate, and took **16.9 h**; the rung as a whole spent
**145 157 core-seconds = 40.3214 core-hours = 2.0685 USD**, **3.71×** its own
prediction and 8.3 % of the 25 USD ceiling. **Fitting the two endpoints gives
`rate ∝ N^(−0.747)`**, carried forward as Model A,
`rate = 7.73e4 (N/2.355e5)^(−0.747)` (`T5_PREREGISTRATION_DRAFT.md` §11).

**The extension re-measured itself against those rates and came in 1.36× over.**
`T3_EXT1_AMENDMENT.md` §10: revised cost from measured rate **108.3 core-hours
= USD 5.56** against the §5 prediction of **79.55 core-h / USD 4.08** — well
inside both the 10× stop threshold and the binding remaining-ceiling stop.
Every case ran **15–41 % slower than predicted**, and the amendment names the
contention: the closure team's `fs3_select.py` at **~291 % CPU, about 3 cores**,
so **12 + 3 ≈ 15 of 16 cores committed**. The eight extension solvers were
nonetheless each holding **95–97.5 % of a core** — not starved. The slowdown is
memory-bandwidth and cache contention, and its signature is that the
degradation is **worst on the largest mesh** (`R_f`, 235 520 cells, **1.41×**)
and **mildest on the smallest** (`D_m`, 79 360 cells, **1.15×**) — the same
mechanism §9 found, not a scheduling problem.

## N-T6. Iterative non-convergence and energy imbalance are one quantity, and the exception has a mechanism

Over the **five DECAYING cases** of T3 the least-squares fit is

> `imbalance % = 10^7.982 × (T residual)^1.308`,  **`R² = 0.986`**

across three decades of residual and 2.6 decades of imbalance, with `R_f`
(`3.984e−06`, **8.2340 %**) the top point and on the line
(`T3_EXT1_AMENDMENT.md` §4).

**The two low-level STALLED cases sit far below that line**: the fit predicts
30 % for `R_c` (observed **0.074 %**, **400× below**) and 0.88 % for `W_m`
(observed **0.0082 %**, **107× below**). That separation is the finding, and
the mechanism is storage. A steady energy balance assumes no storage term; a
case whose residual is *marching one way* still has one — the field is
systematically accumulating enthalpy — and the budget fails to close in
proportion. A case in a *stationary limit cycle* oscillates about a fixed mean
and carries **no net storage**, so its budget closes even though its residual is
large: `R_c`'s `T` residual (**1.059e−05**) is **2.7× larger than `R_f`'s** and
yet it closes **111× better**.

**Residual magnitude alone does not predict imbalance; residual magnitude in a
case that is still moving does, at `R²` = 0.986.** Report only: `R_f`'s 8.23 %
is consistent with non-convergence and is not evidence of a mesh,
discretisation or boundary-condition fault on the fine level.

## N-T7. A CONVERGING triple is a step-ratio test, and a fine-level deviation smaller than the coarse-to-fine drift is a passing value on a divergent triple

**The rule, stated as a step ratio.** A CONVERGING `(m, f, x)` triple requires
`p >= 0.5`, i.e. **the x-to-f step has fallen to at most `1.6^-0.5 = 0.79` of
the f-to-m step**; it does **not** mean a limit has been reached
(`T1b_L4_AMENDMENT.md` §3.3 and the amendment rule). With the step repeated
exactly, `e32/e21 = 1`, `p = 0.000`, and `gci()` classes that DIVERGENT. The
amendment turned that into four pre-registered thresholds — `Nu_x <= 32.24` at
1e4 (step `<= 0.62`), `<= 73.86` at 3e4 (`<= 1.38`), `<= 189.08` at 1e5
(`<= 3.31`), `<= 456.76` at 3e5 (`<= 7.51`) — and predicted **NO at all four
Reynolds numbers**, because **no `Re` had yet shown a step ratio below 0.995**
(ratios 1.108, 1.073, 1.028, 0.995) and the step tracks the first-cell `y+` of
the low-`Re` `kOmegaSST` wall treatment (**1.53 → 0.97 → 0.61 → 0.39** across
the four levels) rather than an asymptotic range.

**Why that matters, from attempt 2's own rows.** Every `Nu` row PASSED —
31.619 against 30.907 (**2.305 %** inside 2.844 %), 72.480 against 73.684
(**1.635 %** inside 3.885 %), 185.771 against 190.398 (**2.430 %** inside
5.334 %), 449.255 against 456.723 (**1.635 %** inside 5.749 %) — on triples
that are **DIVERGENT** (`p` = −0.219, −0.150, −0.059) or **STAGNANT**
(`p` = +0.010). `Nu` rises by a near-constant step per 1.6× refinement at every
`Re` (**+0.71 / +0.79, +1.63 / +1.75, +4.08 / +4.19, +9.54 / +9.49**), and
**the fine deviations (2.305 / 1.635 / 2.430 / 1.635 %) are all smaller than
the coarse-to-fine drift (4.98 / 4.89 / 4.66 / 4.42 %)** — so each PASS is a
statement about the finest mesh built, not about a limit
(`T1b_RESULTS.md` §8). **A deviation smaller than the drift is the tell.**

**N-D11. The `dRdW` colouring is structurally bigger at fewer ranks, and it is the term that
decides whether a DAFoam adjoint arm fits its cap.** Measured 2026-08-22 on ONERA M6 rung 2,
42,120 cells, `dafoam-idwarp-rot:v1`, against the archived np=4 run of the same mesh
(`cases/dafoam/ladder-a/A3/rung2_patched_idwarp_np4/`). `nUniqueCols` **381,558 (np=1) vs
125,870 (np=4) = 3.03×** on an identical matrix (`AllNonZeros` 0.99×); seconds per 100
`ColorSweep` **42.91 vs 12.28 = 3.49×**; decoloured per sweep 397.4 vs 405.0 = **0.98×**, so
per-sweep efficiency is unchanged and the cost is entirely the graph's size. The distance-2
graph is built per partition, so at one rank it is global. Projected colouring cost at np=1:
4,074 s CPU = 67.9 core-min idle / 138.6 contended, against 30.13 core-min measured at np=4 with
a warm cache. `dRdWColoring_<nranks>.bin` is np-keyed, so the move also discards the cache.

**N-D12. The pyDAFoam cold-start continuity signature is np-specific and must not be carried
across decompositions.** ONERA M6 rung 2, 42,120 cells, 2026-08-22: `sum local` reads
**0.6833296303785072** at np=4 (`scotch`) and **0.7019005906092856** at np=1, **+2.72 %** — a
second-significant-figure difference between two provably cold starts. The cause is ordering:
the quantity is evaluated *after* the first pressure solve, which is decomposition-dependent
(`p` finalRes `0.07800447749249334` vs `0.08167211255002443`). **The np-invariant cold-start
discriminator is `initRes ≈ 1`** — a warm start reads ~55× *below* it, not above. This puts
`FAMILY_SUPERVISION_GUIDELINES.md` §8 item 2 (use the continuity signature to prove a cold
start) in the same collision `DAFOAM_CHARTER.md` §5 already names for FD references: a
signature is only a signature within one rank count.

**N-D13. A peak-to-peak from three samples is a biased noise estimator, and DAFoam's
`printInterval` hides the bias.** A6 N=16's FD noise floor rested on η = 9.00e-06 taken from
**three** CD samples, because `printInterval` defaults to 100. At `printInterval` 10 — numerically
inert, since `DASolver.C:124` calls `calcAllFunctions(printToScreen_)` every iteration and the flag
gates only the `Info` output — the same 200-iteration window reads **1.0910e-05, 21 % larger**, and
the floor at step 1e-3 moves `4.5043e-03` → `5.4550e-03`. The estimator cannot see excursions
between samples and its bias grows as the sampling interval approaches the oscillation period.
Every FD noise floor computed from a DAFoam log at default `printInterval` carries it; the fix costs
nothing. (Measured 2026-08-22, `A6/rung_n16_fixed_reference/RESULTS.md`.)

**N-D14. A6 N=16's primal is a residual limit cycle, and iteration count is the worst available
lever on it.** `primalMaxRes` (`nuTilda initRes`) sits within ±4 % of 5.9e-06 from iteration 100 to
1000 and reads **5.6999e-06 at 6000** — 6× the compute for a 3.5 % residual improvement, with
"satisfied the prescribed tolerance" appearing **zero** times. The objective's peak-to-peak does not
decay monotonically either: **1.0910e-05 (t=1000) → 1.7117e-05 (2000) → 1.2906e-05 (4000) →
6.0874e-06 (6000)** — it rises 57 % before falling and ends only 1.8× better for 6× the cost.
DAFoam's shipped `primalMinResTolDiff 1e2` guard correctly refuses the run at every iteration count,
which is why the predecessor's inherited widening to 1e4 must not be carried forward silently.

**N-D15. The FD instrument's solve-to-solve noise and the within-run wobble are different
quantities, and they differed 2.47× here.** Two back-to-back `run_model` calls at an identical A6
N=16 design point give CD `0.03506349413916734` and `0.035065704525484256`, δ_repeat =
**2.2104e-06**, against a within-run 200-iteration peak-to-peak of **1.0910e-05**. Central FD
differences two **solves**, not two points of one solve, and a warm restart lands near the same
limit-cycle phase. Which one is the right denominator decides whether a marginal component is
gradeable, so it is fixed in the pre-registration before the run, never after (L-233). The first call
also reproduces the predecessor's cold baseline bit-for-bit across items, images and days.

**N-D16. DAFoam's forward-AD build does not reproduce the plain build's primal on
`DARhoSimpleCFoam`, and `libDASolverADF.so` is md5-identical across all this lab's images.** Cold,
same mesh and `daOptions`: momentum `finalRes` bit-identical; `he` `finalRes` diverges at the 8th
significant figure (`0.06128002514528321` plain vs `0.06128001402295498` ADF); the GAMG pressure
solve stops at **5 sweeps instead of 7**; cumulative continuity is 10× worse
(`-0.00504349133910657` vs `-0.05058272456310364`); CD at iteration 1 is 13.5 % low; every state is
**NaN within 10 iterations**. Warm-started from a converged state it survives 13 iterations, during
which the tangent converges **monotonically onto the adjoint to 0.600 %**, then diverges — so the
failure is the ADF primal's stability, not the AD derivative machinery. md5
`44538ed4ac157ecb5dbb6850cf4bde64` on both `dafoam/opt-packages:latest` and
`dafoam-idwarp-rot:v1`: a **shipped-toolchain** property, measured on the patched row. Defect-class
candidate, **NOT FILED**, novelty not established.

**N-D17. A DAFoam primal can print "satisfied the prescribed tolerance" having satisfied nothing,
and `-10000000000` is the tell.** `DASolver.C:188` exits on
`(primalMaxRes < primalMinResTol) && (timeIndex > primalMinIters)`, with `primalMaxRes`
re-initialised to `-1e10` at `DASolver.C:222` and `primalMinIters` defaulting to 1
(`pyDAFoam.py:639`). Where `primalMaxRes` is not updated on the first step the guard reduces to the
iteration counter and the run announces convergence at iteration 2, printing **"Minimal residual
-10000000000 satisfied the prescribed tolerance 1e-08"**. Same diagnosability class as the prepared
D-C; any A6-family arm must set `primalMinIters` to its `endTime` to avoid it.


## R4 SpaRTA-class build numerics — appended 2026-08-22 (R4 BUILD lane, reviewed by supervisor)

Measured under the frozen preregistration of D443/D444 (`cases/RANS_LES_closure_models/R4_sparta_build/PREREGISTRATION.md`, sha256 `05844430…cbbe8`). Continues the closure/SpaRTA **N-B** series, whose N-B13 and N-B14 carry the earlier frozen-extraction facts these entries extend.

**N-B26. The k-corrective-frozen-RANS extraction reproduces bit for bit, and the
reproduction is the check that the rebuild is sound.** Rebuilt independently
from the benchmark's own fields, `PHLL10595` and `CBFS13700` return
`0/{U,k,tauij,omega,nut}` **byte-identical** to
`verification/runs/W2_sparta_runs/{ph,cbfs}_frozen`, settle at the W2 record's
own iterations, and write `bijDelta`, `kDeficit`, `bijData`, `U`, `k`, `omega`
and `nut` **byte-identical** at `1492/` and `354/`. A rebuild that differed in
any input, boundary condition or dictionary could not do that.
Source: `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §2.1.

**N-B27. The frozen `omega` equation carries an explicit source divided by
`nu_t`, and the shipped hills carry `nu_t` down to 5.55e-12.**
`kOmegaSSTFrozen.C` builds `gamma*(PkLim + Rterm)/max(nut, 1e-12)`. Where `nu_t`
is at that floor the source is amplified by up to **1e11**, `omega` is driven
negative, and `bound(omega, omegaMin)` replaces those cells with a local average
**every iteration**. Consequence, measured on the 21 `Parm_PH_29` training
hills: **13 sit in a limit cycle** whose residual is identical to fifteen
significant figures at iteration 5000 and at iteration 20000
(`initRes = 4.21656145422043e-04`, `max rel domega = 0.105158858322751`), so
**extending the backstop is useless**; **2 report a false convergence** after
being clipped flat; **6 converge and never bound `omega` once**. The four ducts,
`PHLL10595` and `CBFS13700` never bound it either.
Repairs tested and **all four failed**: flooring `k_LES <= 0` cells at
`1e-4 x mean k_LES` with isotropic `tau`; the same at `1e-2 x mean k_LES`;
inserting the `div(phi,omega) Gauss linearUpwind grad(U)` scheme the hills alone
omit; and quadrupling the backstop.
Source: `R4_sparta_build/RESULTS.md` §2.3.

**N-B28. The 21 `Parm_PH_29` hills are the only benchmark family whose
`system/fvSchemes` declares no `div(phi,omega)`.** It falls through to
`default Gauss linear` — unbounded central differencing on the `omega`
convection term — while `PHLL10595` uses `bounded Gauss linearUpwind grad(U)`,
`CBFS13700` uses `Gauss linearUpwind grad(U)` and the ducts use
`bounded Gauss linearUpwind limited`. The hills also declare `div(phi,epsilon)`,
a k-epsilon leftover, which no `kOmegaSST` run reads. **Inserting the missing
scheme does not by itself fix the frozen extraction** (N-B27), so it is recorded
as a defect in the shipped cases, not as the cause.

**N-B29. Every one of the 21 hills carries cells with `k_LES <= 0`; no other
training family does.** 7 to 51 cells per hill, 0.045 %–0.33 % of the mesh,
minimum `k_LES` from −2.5e−04 to −6.8e−03; the ducts, `PHLL10595` and
`CBFS13700` carry none. **The trap is that `bound(k, kMin)` inside the model
replaces them with a small POSITIVE number**, so a `k > 0` mask on the field the
solver *writes* cannot find them, and `b^Delta` there reaches `O(1e5)` — an RMS
`||b^Delta||_F` of **35,478** on `alpha_10_12000_4048` against ~0.3 on every
other case. The mask must be taken on the **shipped** `0/k`.
Source: `R4_sparta_build/RESULTS.md` §2.3, §3.3.

**N-B30. The exact duct tensor-basis degeneracy is a property of the linear-EVM
RANS field, not of the frozen field a SpaRTA regression fits.** On
`AR_1_Ret_180`, over all 2,209 cells:

| field | `\|\|T3+T4\|\|/\|\|T3\|\|` median | p99 | `\|I1+I2\|/\|I1\|` median | per-cell rank of `{T1..T4}` |
|---|---|---|---|---|
| baseline RANS | 2.7398e-17 | 6.4084e-16 | 0.000e+00 | **3.000** (2209/2209 at rank 3) |
| frozen (`U = U_LES`) | 1.2779e-02 | 4.6889e-01 | 7.0405e-05 | **3.965** (2132/2209 at rank 4) |

Frozen per-cell rank on all four training ducts: 3.965, 3.977, 3.978, 3.977. A
linear EVM produces no duct secondary flow, so `S^2 + Omega^2` is isotropic and
the deviatoric parts cancel exactly (the same fact L-219 states from the
anisotropy side); the DNS mean flow has secondary motion and they do not.
Source: `R4_sparta_build/RESULTS.md` §3.2.

**N-B31. `R` spans eight orders of magnitude across the training families, so a
pooled fit on the raw quantity is a duct fit.** RMS `kDeficit`: **0.0066**
(`CBFS13700`), 0.0346–0.0625 (hills), 0.0588 (`PHLL10595`), **1.61e+06–1.70e+06**
(the four ducts, whose bulk velocity is ~37.5 m/s on a 1 mm half-height). The
non-dimensionaliser used here is the case median of `k*omega`, a physical scale
of the same dimensions taken from the frozen fields and not from the target; one
positive constant per case leaves every fitted coefficient unchanged.
Source: `R4_sparta_build/RESULTS.md` §3.4.

**N-B32. `kOmegaSSTSparta` implements T1–T3 only and a term registered with
`n = 4` silently evaluates as T3.** `kOmegaSSTSparta.C` builds `T1 = S`,
`T2 = SW − WS`, `T3 = S² − I tr(S²)/3` and dispatches
`n == 1 ? T1 : n == 2 ? T2 : T3`. There is no bounds check and no warning.
**Reported to the owner of `sdk/`.** Any writer of `RTerms`/`bDeltaTerms` should
assert `n in (1,2,3)` before the dictionary is written; `build_aposteriori.py`
does.

**N-B33. On this training set the T1–T3 restriction costs nothing.** The
`b^Delta` model fitted on T1–T3 generalises **better** across families than the
unconstrained T1–T4 fit — leave-one-family-out MSE **0.0156199** against
**0.0158092** — the two agreeing exactly on `T2` and `I2 T2` and differing only
by `+5.0391 T3` against `−6.7275 T4`.
Source: `R4_sparta_build/MODEL.md`.

**N-B34. IC1: the symbolic model the solver evaluates is the one the record
states.** An independent Python evaluation of the frozen term sets against
`kOmegaSSTSparta`'s own `writeInitialCorrections` fields agrees to **5.08e-13**
relative L2 on `bijDelta` and **3.97e-12** on `kDeficit`, over all 12 cases —
the ascii `writePrecision 15` round-trip floor.
Source: `R4_sparta_build/artefacts/ic1_discovered.json`.

**N-D18. The IDWarp `getRotationMatrix3d` patch is NOT monotonically beneficial: on a case where
the shipped gradient is already right, it makes every warp-crossing row worse.** Measured
2026-08-22 on ONERA M6 sweep rung 2 (42,120 cells, np=4 `scotch`, `DARhoSimpleCFoam`,
`transonicPCOption 1`, `dafoam-idwarp-rot:v1` vs the archived SHIPPED-equivalent arm), against an
FD reference that is **bit-identical between the two images**:
`CD/shape[115]` **0.0172 % → 0.1586 %** (9.21×), `CD/twist[1]` **0.2740 % → 0.9279 %** (3.39×),
while `CD/patchV[1]` — the one row that does **not** cross `warpDeriv` — is **bit-identical**
(0.0077 % both, analytic `7.90292882576689e-03` unchanged to every digit). Patch effect on the
full 120-component shape row: **1.469586 % in L2**, 120/120 components moved, with **three
analytic-vs-analytic sign flips** (idx 12, 13, 24 — 0.097 %, 0.598 %, 0.120 % of the row's largest
entry; no FD exists at those indices, so they carry no verdict). Compare A1/A2/A5, where the same
patch removed **97–99.5 %** of the error. `CD/twist` moves **0.6593 %** here against **0.664 %** on
A6's N=16 rung — two cases, two meshes, agreeing to three significant figures. **The reading:**
where the shipped gradient is already correct to ~1 part in 5,800, there is no error for the patch
to remove and its own approximation dominates. Adoption of a patched toolchain is therefore
**case-dependent, not global** — and that is an owner's decision, not a lane's.

**N-D19. A6 N=16's nine-component gradient table is complete: eight graded at 1.0432%, one structurally ungradeable**


Measured 2026-08-22, `dafoam-idwarp-rot:v1`, 41,760 cells, np=1, `endTime 1000`,
`primalMinResTolDiff 1.0e4`, `primalMinIters 1000`, `printInterval 10`, central FD, `η = 1.0910e-05`,
clearance `C = |J|·2s/η`, graded only where `C ≥ 5` at the graded step and the two registered steps
agree within 10%.

| DV, idx | adjoint | FD (graded step) | rel err | `C` | plateau |
|---|---|---|---|---|---|
| `patchV` 0 | `+7.334000e-04` | `+7.375983890e-04` @ 3e-1 | 0.569% | 40.56× | 0.59% |
| `patchV` 1 | `+9.016840e-03` | `+8.932878291e-03` @ 3e-2 | 0.940% | 49.13× | 0.58% |
| `twist` 0 | `-2.100900e-03` | `-2.137369846e-03` @ 1e-1 | 1.706% | 39.18× | 4.17% |
| `twist` 1 | `-1.750730e-03` | `-1.774854641e-03` @ 1e-1 | 1.359% | 32.54× | 0.37% |
| `twist` 2 | `-1.469450e-03` | `-1.444417199e-03` @ 1e-1 | 1.733% | 26.48× | 3.65% |
| `twist` 3 | `-1.010980e-03` | `-9.929378034e-04` @ 1e-1 | 1.817% | 18.20× | 0.78% |
| `twist` 4 | `-6.277000e-04` | `-6.212861219e-04` @ 1e-1 | 1.032% | 11.39× | 2.31% |
| `twist` 5 | `-3.797300e-04` | `-3.782595043e-04` @ 2e-1 | 0.389% | 13.87× | 2.83% |
| **`twist` 6** | `-1.361900e-04` | **none at any feasible step** | — | max **2.42×** | **83.53%** |

**Vector-relative error `‖J_an − J_fd‖ / ‖J_fd‖` over the eight graded = 1.0432%, zero sign flips**;
the three previously-verified components alone reproduce the published **1.0099%**; the same eight
read at their lower registered step give **1.2921%**. `twist` idx6 is flagged and excluded by name —
`|J|` = 1.362e-04 is too small for any feasible step to lift over the floor, and the only remaining
lever is `η` itself. The predecessor's readings at the noise-dominated `1e-3` were **82.786%,
3.290%, 340.703%, 57.618%, 67.927%, 159.347%, 57.061%, 90.166%, 105.256%**. The adjoint never moved.
(`cases/dafoam/ladder-a/A6/rung_n16_remaining_components/RESULTS.md`, 39.15 core-min.)

**N-D20. A clearance bar is a floor, not a target — a component just above `C = 5` is marginal even when its plateau passes**


Across the five A6 N=16 components graded 2026-08-22, **every one improved as clearance rose**, and
the two whose lower step sat nearest the `C ≥ 5` bar improved the most: `twist` idx5 went **3.316%
at C 6.74× → 0.389% at C 13.87×** (8.5× better), `twist` idx2 **5.588% at C 7.65× → 1.733% at
C 26.48×** (3.2× better), against `twist` idx1's **0.996% at C 9.73× → 1.359% at C 32.54×** (flat).
**Clearing `C ≥ 5` makes a component gradeable; it does not make it converged.** The pre-registration
had attributed `twist` idx5's expected error to **truncation** at its larger step and widened its
band to 15% for that reason; the measurement shows the opposite — it was still **noise**-limited at
the smaller step. The prediction HIT and its stated mechanism was wrong, which is recorded as a
defect in the reasoning. **Read a component within ~2× of the bar as marginal and report its value at
both steps.**

**N-D21. FD steps can be sized mechanically from the stored `|J|` and `η` before the run, and the proxy predicted the measured clearance to within 8% on ten of ten**


A6 N=16, 2026-08-22, first use. Rule, registered before any value existed: per component, `s_lo` =
smallest rung of a fixed ladder with predicted `C = |J_adj|·2s/η ≥ 5`; `s_hi` = smallest rung at ratio
≥ 2; graded step is the higher-clearance one, **never selected on agreement**. It chose four different
pairs across five components spanning **4.6×** in `|J|` — `{3e-2,1e-1}`, `{3e-2,1e-1}`, `{5e-2,1e-1}`,
`{1e-1,2e-1}`, `{1e-1,3e-1}` — which no single hand-picked pair could have covered. **All ten
registered steps cleared `C ≥ 5` on the measurement** (smallest 5.83× against a predicted 5.75×),
**all five plateaued** (worst 3.65% against a registered 10%), **none was flagged**.
**The limitation, stated because it is the rule's own blind spot:** it sizes the step from
`|J_adj|` — the quantity under test. Here the adjoint proved right, so the proxy was good; on a rung
where the adjoint is wrong by an order of magnitude the rule would register steps that cannot grade.
**That failure mode is unmeasured.**

**N-B35. The negative frozen-`omega` source is universal, not a hill
pathology.** With the R5C per-iteration counter live, `nNegSourceCells` reaches
**476–2,274** cells on **all 27** training cases — including `PHLL10595` (476
even on the converged legacy run) and `CBFS13700`, the two cases the W2 record
validates. R4's clipping appeared only on hills because only there does the
negative source meet `nut` at the `1e-12` floor (N-B27); the sign itself is
everywhere.
Source: `R5C_omega_repair/artefacts/r5c_grading.json` (G1c rows).

**N-B36. The Patankar-split `omega` source shares the legacy fixed point in
practice, and moves the stopping point where it damps.** Eleven of twelve
R4-COMPLETE cases settle at the **identical** iteration under the split source
and reproduce `kDeficit`/`bijDelta` to **1e-7–1e-11** relative L2; the twelfth
(`alpha_10_12000_4048`) settles **37 % earlier** and lands **1.1848e-04** away
— a broad drift (largest cell 0.08 % of the squared error), not a local defect.
Clipping is removed on 22 of 27 (zero `bound(omega)` events; the five remaining
clip 5–29 iterations against R4's 5,000), and 10 of R4's 15 INCOMPLETE hills
become COMPLETE under the strict six-condition rule.
Source: `R5C_omega_repair/RESULTS.md` §2, §5.

**N-B37. `initRes(1)` on the frozen-`omega` extraction measures the initial
guess, not the run.** The initial condition is the baseline SST `omega` field —
a good guess on most cases — so `initRes(1)` spans **4.7e-05 – 0.56** with only
**3 of 27** at O(1e-1), while `initRes(convergedAt)` is `1e-9`–`1e-13` on all
27 (the settle criterion already enforces `< 1e-8`). A registered residual-fall
ratio of `1e6` therefore rejected R4's own W2-validated `PHLL10595` at
**9.167e5**. Any future fall criterion on this family must be absolute, or must
bound distance to the fixed point directly.
Source: `R5C_omega_repair/RESULTS.md` §6.2.


**N-B38. A feature clipped at a constant is invisible to a range-coverage
check above the clip — the training maximum IS the clip.** The FS1 library's
wall-distance Reynolds number is `q1_wallRe = min(sqrt(k) d / (50 nu), 2)`
(`_common/features/FEATURE_LIBRARY.md:178`, `:174` before `01430485`), and it
**saturates**: over the 40-case, 641,652-cell library its pooled statistics are
`max = 2.0`, `p99 = 2.0`, **`p50 = 2.0`** — more than half of all cells sit
exactly on the bound. An FS5 test-vs-training range check on that column
therefore **cannot report an above-maximum excursion for any test cell**,
whatever the underlying physics, because the training maximum is the clip;
only below-minimum excursions stay visible. This is the exact axis the round-5
diagnostic named: the `Re_y` extrapolation trap was measured on the
**unclipped** `sqrt(k) d/(50 nu)` at **1.85x and 2.07x** its trained maximum on
two ducts (`research/closure/md/CLOSURE_CHALLENGE_STATUS.md`:418-423), and the
FS5 sweep as built would not have seen it. **Bounded by construction is not the
same as bounded by the data**, and a coverage instrument reports the second
while a clip supplies the first. Whether the library's other bounded features
(the Wu/Kaandorp `q = q_raw/(|q_raw| + |q_norm|)` block, bounded in `[-1,1]`)
also saturate on training data is **unmeasured** — saturation, not
boundedness, is what destroys visibility, and only `q1_wallRe` was measured
here. No R4 number is affected: `q1_wallRe` is not among the selected features
of `MODEL.md`.
Source: `/home/ubuntu/closure-data/features/fs2_audit.json` (key `per_feature`,
`q1_wallRe`); `R4_sparta_build/COVERAGE.md` §6.
**N-D22. The NASA hump assembled `dRdWTPC` (51,626 cells, 517,240 adjoint states) is structurally nonsingular but extreme in diagonal spread.** 33,662,810 nnz
(65.08 per row); zero zero-rows, zero zero-cols, zero zero-diagonal entries; diagonal
absolute spread **13.01 decades** against CBFS's 8.67 and the M6 family's 14.17. The `cfVar`
adjoint RHS is nonzero on **2,165 of 517,240** entries (0.42 %), against CBFS `varianceU`'s
29.92 %. `‖b‖₂ = 1.094138002900e+00`, equal to the solver's printed iteration-0 residual to 13
digits — the dumped system is the real system (`PROOF.md:2717-2720`'s check, passed on the hump).
From W4 M1+M2 (`64479072` §3a, §4; dump verified on disk at
`W4-m1m2-hump-conditioning/hump_dump/`). The singular-or-not verdict itself is **PENDING**: these
are operator statistics, not the registered `splu`/`spilu` instrument, and no verdict is drawn
from them.

**N-D23. The ASM sub-block complete-LU factorization costs ≈ 100 s wall at np=4 on the hump case.** A6 printed its iteration-0 residual at **174.97 s** with
`DAFOAM_SUBPC_TYPE=lu`; the two 2026-08-23 stock arms printed the bit-identical residual at
**73.83 s** and **73.71 s** with everything else held (W4 M1+M2, `64479072` §2). This is also why
`W4_ADJOINT_PC_UNBLOCK.md` §5b.1's 11.7 core-min pre-solve price over-priced a stock arm by
~40 %: the price was measured with the LU factors in it.
**N-B39. `singular_value_ratio_first_to_last` of a rank-deficient standardised
feature matrix is BLAS-thread-dependent rounding noise — an exact-identity gate
over it is meaningless without a pinned environment.** The FS2 audit publishes
`s[0]/s[-1]` per family; on the rank-deficient matrices (POOLED rank 100/110,
duct 96/110) `s[-1]` is analytically zero, so the figure reports the
rounding-noise floor (~1e-15 relative to `s[0]` ≈ 7.5e2), not a property of the
data. Measured under D476's gate A3 (`7e973ba8`): repeat runs are bit-identical
— deterministic per environment — but the figure tracks `OPENBLAS_NUM_THREADS`.
On `hump` with the matrix held fixed, `s[0]` agrees to 15 digits and the rank
stays 100 at every thread count while the ratio spans 1.75e17→3.31e18;
threads=4 reproduces the pre-D476 baseline exactly, threads=16 the new run.
Every other audit value was exactly identical across the regeneration. A3
stands **GATE FAIL**, unloosened; pinning was NOT adopted — converting a failed
gate to a pass by changing how the instrument runs is unregistered
pass-engineering. Referred to verification: whether `s[0]/s[-1]` of a singular
matrix should be published at all (it is infinite in exact arithmetic;
`s[0]/s[r-1]` over the retained rank measures something), and whether audit
instruments should pin BLAS threads so exact-identity gates mean something on
this box. Sibling closure of N-B38's "unmeasured" clause, same commit:
`q1_wallRe` `frac_at_max` = **0.5784** over 641,652 pooled cells — the clip at
2 is the MODAL value and the unclipped p50 (2.994) already exceeds it; only
`I3_trW2__A/B` saturate otherwise (analytically −0.25, already flagged
near-constant, not a discovery).
Source: `cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`;
`/home/ubuntu/closure-data/D476_A3_triage/`; commit `7e973ba8`.
**N-D24. CBFS B3 decomposition peak RSS, measured under a 12 GiB cap: np=1 is the LARGER arm on both instruments — kernel 11.133 GiB / tree 11.503 GiB serial vs kernel 8.000 GiB / tree 9.719 GiB at np=4.** The registered falsifiable claim (that decomposition inflates peak memory) is **falsified in the registered direction** (M4 GATE FAIL as graded). Attribution is per-pid: one serial `python` at VmHWM 11.487 GiB versus four np=4 ranks at ≤ 2.453 GiB each — the adjoint's memory concentrates in a rank, and splitting ranks splits it. The np=4 kernel peak sits **114,688 bytes above the 8 GiB band floor** (8,590,049,280 B — flagged margin, not rounded away). Serial ran part of its arm at host MemAvailable 7.25 GiB (min 7,598,900 kB) — below the 12 GiB launch gate, above the 4 GiB mid-run floor, and produced the graded headline: direct measured input to the MemAvailable-floor question on Sanaa's desk. All peaks are under-cap readings (L-258). Source: `cases/dafoam/ladder-b/B3/decomposition_peak_rss/` (prereg `d062aace` + Addenda 1–3), `/home/ubuntu/certonomous-runs/B3-decomposition-peakrss/peak_rss.json`; identity M0 PASS 18/18 both arms.

**N-D25. The rotation-patch gradient effect is not uniformly signed even within one case: the same unchanged library that degraded A3 `shape[115]` 9.2084× at rung 2 improves it 2.42× at rung 1 — the delta tracks the sign and size of the SHIPPED error, not the patch.** Rung 1 measured (np=4, FD reference bit-identical across patched/shipped/archived — all three pairings): shipped rel-err 0.9273 % (error −1.141009e-03), patched 0.3826 % (ratio 0.4126); rung 2 had shipped error +2.2401e-05 with the patch making it 9.2084× worse. Within rung 1 itself the split repeats: `twist[1]` moved 0.5510 % toward zero while `shape[5]` moved 9.0905 % **away** (R1-P9 SPLIT) — so no general directional claim about the patch survives measurement in either direction. 0 sign flips at rung 1 (rung 2 had 3); L2 of the patched-vs-shipped gradient delta 0.940327 % with 120/120 components differing. Third measured leg of the R11 adoption evidence (with N-D18 and A4's patch-immaterial row): adoption is case- AND rung-dependent. Source: `cases/dafoam/ladder-a/A3/rung1_patched_idwarp_np4/` (prereg `5d8e2f52`), `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/`.

**N-D26. Image equivalence, measured bit-for-bit: the literal `dafoam/opt-packages:latest` reproduces the archived `dafoam-subpclu:v1`-env-unset A3 rung-1 row exactly — 16/16 perturbed CD values, 8/8 FD estimates, both baselines and the repeat drift.** This closes the previously untested ‡ equivalence that carries every SHIPPED-equivalent row on the A3 sweep ladder: those rows now rest on a measured bit-identity at rung 1 rather than an inference. The hash remains the identity — this equivalence is a measured fact about these two images' contents on this case, not a rule about tags. Source: `/home/ubuntu/certonomous-runs/P4-a3-rung1-patched/` (R1-P6), grader `cases/dafoam/ladder-a/A3/rung1_patched_idwarp_np4/analyse_r1.py` (committed before running, planted control live).

**N-D27. The NASA hump's incomplete factorization is singular at all four registered `spilu` settings — the CBFS signature reproduced on a second case — and its complete factorization does not fit in 20 GiB.** Assembled `dRdWTPC`, 517,240 states, 33,662,810 nnz (N-D22): `scipy.sparse.linalg.spilu` raises `Factor is exactly singular` at `drop_tol` 1e-2/1e-3/1e-4/1e-5 with `fill_factor` 3/5/5/10 — 4 of 4, matching CBFS's 4 of 4 (`PROOF.md` §25.3). `splu(diag_pivot_thresh=0)` was killed by a 20.0 GiB cgroup cap without completing (peak right-censored at exactly 21,474,836,480 B), against CBFS's complete LU finishing inside 10 GiB at 3.22e8 nnz(L+U). Source: `cases/dafoam/ladder-b/W4_O2_REBUY_RESULTS.md` §2–§3, log `W4-m1m2-hump-conditioning/logs/o2_rebuy_hump_lu_20260823T211207Z.log`. **The singular-vs-merely-slow verdict (frozen §3 of `c8254a4a`) remains `PENDING`**: the incomplete factorization's singularity is measured; the complete factorization's behaviour is not.
**N-B40. Ling's SGD rate under full-batch updates is inert on the TBNN and
sufficient for the MLP.** 200,000 full-batch SGD updates at lr 2.5e-7 move the
8×30 TBNN's train loss by 12–36 % and its validation `b_rms` from 3.0–9.6 to
3.0–7.1 (seed 1's best epoch is epoch 0); at 2.5e-6 the 10×10 MLP trains from
0.49–1.09 to 0.30–0.37 and is still descending at the cap. The paper's own
updates were per training point (sidecar l.131–132) — ~3.4e5× more per epoch.
Source: `Ling2016_TBNN/gpu/RESULTS.md` §2, `hist_tbnn_s*.csv`, `hist_mlp_s*.csv`.

**N-B41. The architecture optimum is flat, and the search re-selects the
CPU lane's recipe.** 100 TPE trials over depth 2–12, width 5–100, four
activations, batch {8192, 65536, full}, lr 1e-7–1e-2 (Adam, 400 epochs, 3 seeds,
VAL only) return 9×77 LeakyReLU(0.01), **batch 8192, lr 1.023e-3** — the CPU
lane's batch and learning rate to three figures — with validation 0.1595 (5
seeds, spread 0.0035) against the frozen 8×30's 0.1646 (spread 0.0073): inside
the spread, so the paper's 8×30 is not shown suboptimal on this data.
Source: `status_armb_search.json`, `../train_log.json`; `RESULTS.md` §3.

**N-B42. Low RMSE and high non-realisability coexist on the ducts.** The
ARM-B network scores 0.109–0.121 on the three held-out ducts (train-mean
0.39–0.42) while violating the barycentric triangle on 24.7–46.4 % of those
cells for three of five seeds (0.5–1.2 % and 6.1–6.8 % for the other two) at
`max ‖b‖_F` 0.76–0.83 — inside the norm bound, outside the triangle. On the
out-of-family `NASA_2DWMH` every seed violates on 10.1–12.1 % with `‖b‖_F` to
9.4e8. The truth violates on 0.79 %, SST on 0.10 %, the MLP on 0.00 %.
Source: per-case `realisability_violation` over `pred_armb_s*.npz`; `RESULTS.md` §2.

**N-D28. A1's patched adjoint does not degrade at a converged constrained optimum.** A1 NACA0012 (4,032 cells, np=1, `dafoam-idwarp-rot:v1`), at the design point IPOPT reached after 11 majors (curriculum D1, `b10260a0` §5): the endpoint analytic gradient agrees with central differences at **0.0525 % (`shape[6]`)**, **0.1638 % (`shape[1]`)**, **0.1229 % (`shape[5]`)**, **0.2553 % (`patchV[1]`)**, zero sign flips, vector-relative **0.11479 %** over the four graded components, steps `3e-4` / `3e-3` chosen from endpoint `|J_adj|` and η alone. `shape[6]` — the LE combo mode reading 640.3696 % sign-flipped on the shipped image at baseline and 1.1888 % patched at baseline — reads 0.0525 % here, a 23× improvement over its own patched baseline. `DAFOAM_CHARTER.md` §9's warning (*a gradient verified at iteration 0 is not verified at iteration 47*) is **not** borne out on this case at this design point; the two columns are read at different steps (baseline 1e-3, endpoint 3e-4), both inside A1's measured plateau, and the comparison claims no more. **Patched-row fact only:** the shipped companion at the same design point was BLOCKED (arm C), so no toolchain comparison is carried.

**N-D29. A1's η is a plateau reading and the window is the whole measurement.** Cold np=1 baseline primal exiting on `primalMinResTol 1e-8`: peak-to-peak of `CD` over the last 5 printed samples (t = 400…435, `printInterval 10`) is **1.957350e-08**, reproduced to every printed digit across two independent cold starts (`668ce997` §16). The same case's last-200-iteration, 20-sample peak-to-peak (A6's definition, N-D13) reads **7.824305e-06 — 400× larger** — because A1's tolerance exit makes its final 200 iterations a convergence tail, not a plateau, where A6's fixed `endTime 1000` made them a plateau. **The same formula measures noise on one case and convergence on the other; η is a property of a configuration, never of a case.** Measured consequence: at the endpoint the A6-window reading would have driven `shape[6]` below `C ≥ 5` at every admissible rung and flagged it; the registered plateau reading cleared it at 283.1.

**N-D30. Swapping `GAMG` for `smoothSolver`/`GaussSeidel`/`nSweeps 1` on `p` in a transonic `DARhoSimpleCFoam` case removes the forward-AD build's NaN and makes BOTH builds' continuity error worse — and leaves the 8th-significant-figure `he finalRes` difference between the builds exactly as it was.** Measured on the CRM wing, `transonicPCOption 1`, np=1, `endTime 10`, `primalMinIters 1000000`, one variable changed: five lines in the `"(p|p_rgh|G)"` block of `system/fvSolution`, the two arms' `fvSolution` files otherwise byte-identical. **Pressure sweeps explode**: `p nIters` at `Time = 1` goes 5 → **206** (forward-AD build) and 7 → **425** (plain build), summed over the ten iterations **878** and **5021** — the two builds' sweep counts end **219 apart** where they had been 2 apart under `GAMG`. **First-iteration cumulative continuity magnitude rises in both**: forward-AD `0.05058272456310364` → `0.08515074416090457` (**×1.683**), plain `0.00504349133910657` → `0.08794505498506013` (**×17.437**), so the between-build ratio `r = |cum_F|/|cum_P|` falls `10.029307` → **`0.968227`** (÷10.36). **The fall is the control's error growing, not the AD arm's error shrinking** — the honest reading is that under `smoothSolver` both builds converge on each other **at a worse absolute level** and the AD difference stops being the dominant term because a larger common term dominates both; it is not a claim that `smoothSolver` is the better pressure solver here. **The NaN goes**: the forward-AD arm that printed `FWDAD_DERIV: nan` with 14 NaN tokens under `GAMG` completes ten iterations with **0 NaN tokens** and prints `0.002552003248356442`; the plain control completes with `rc=0` and a finite `PROBE_CD: 0.025518939045363655`. **The AD difference does not go**: `he finalRes` is `0.06128001402295498` (forward-AD) against `0.06128002514528321` (plain) under **both** solvers, unchanged in every digit — not amplified, not removed. All ten validity strings (`U0/U1/U2 finalRes`, `he initRes`, `he finalRes`, both arms) are bit-identical to their `GAMG` references, so the solver swap perturbs nothing the validity gate reads. **Neither arm is a converged solve** — both are 10-iteration probes by construction, final `Total Residual Norm2` `5.78e11` and `1.33e10`, outside every registered observable. Source: `cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §4, §5a, §5b (prereg frozen `538c9f51`, comparator sha256 `239c1764…be7e94` hash-checked against the committed blob at grading); `GRADE_sweep1.txt`, `fsm.log`, `psm.log` in `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/`.

**N-D31. `libDASolverADF.so`'s in-container path, measured rather than guessed: `/home/dafoamuser/dafoam/OpenFOAM/sharedLibs/libDASolverADF.so` in `dafoam-idwarp-rot:v1`, md5 `44538ed4ac157ecb5dbb6850cf4bde64`, and it is the ONLY file of that name on the whole container filesystem.** Established by an in-container `find / -name 'libDASolverADF.so' -type f | xargs -r md5sum`, which returned exactly one line (`A4_FIND_LINES: 1`). The pre-registration deliberately declined to guess the path — no container had been opened at the freeze — and wrote the assertion as the `find` itself; the `find` resolved it. The md5 matches D460 §4's byte-identity to `dafoam/opt-packages:latest`, so this is one library shipped on both images. Siblings `libDASolverADR.so` and `libDASolver.so` sit in the same directory, and **`/proc/<pid>/maps` sampling of a live arm distinguishes which one it loaded**: `LOADED_DASOLVER: libDASolver.so libDASolverADR.so` for the plain build, `libDASolver.so libDASolverADF.so` for the forward-AD build, from the identical reader in the identical launcher. That pairing is what turned the previously bare "ADF must be ABSENT in the control" assertion into a planted-zero control with a positive leg (`CLAUDE.md` rule 3). Source: `cases/dafoam/d460_sweep1_solver_family/RESULTS.md` §1a, §2a, §2b; `ledger.txt` in `/home/ubuntu/certonomous-runs/D460-sweep1-solver-family/`.
**N-D32. The patched-IDWarp CD adjoint residual path is bit-identical to the SHIPPED-equivalent ‡ path on all 11 printed checkpoints, iterations 0–1000, in a STAGNATING regime — A3 rung 3, 79,560 cells, np=4, `transonicPCOption 1`.** Total residual reduction through iteration 1000 is **1.3133×** (`2.121343646203e-02` → `1.615247229756e-02`), flat from iteration 200: relative change **2.239e-03** over iterations 200→1000 and **1.446e-06** over 900→1000. Container peak aggregate RSS, stopped at iteration 1000: **11.680 GiB** against a 16 GiB cap — within **0.030 GiB (+0.26 %)** of the shipped arm's complete measured peak of 11.65 GiB. With rung 2's 11/11 on a **converging** solve, this is the second regime and the second instance of *the rotation patch enters strictly after the Krylov solve*. **Two rungs of one case; not a generalisation.** The arm printed **no `PetscConvergedReason`** — the terminal `-3` at 4000 iterations is the SHIPPED run's measured value carried across by the bit-identity, which is what the registered word "inherited" means in the verdict `GATE FAIL (adjoint, inherited)`. Source: `cases/dafoam/ladder-a/A3/rung3_patched_idwarp_np4_attempt2/RESULTS.md` §2.1, §3; prereg frozen `606930b4` + Amendment 1 `8a0b440d`; graded `8871acf3`.

**N-D33. A3 rung 3's memory and preconditioner envelope, measured rather than projected: host `MemAvailable` minimum 15.2871 GiB over 87 samples at 5 s against an 8.0 GiB floor, 0 strikes; preconditioner assembly completes at `ExecutionTime` 170.76 s and the Krylov solve begins at 171.41 s.** 79,560 cells, np=4, warm colouring cache, `dafoam-idwarp-rot:v1`. The `dRdWTPC` assembly runs **1355 colours** (`dRdWTPC` 0→1354) and consumes those first ~171 s before a single Krylov iteration is taken — so at this rung the preconditioner, not the solve, sets the floor on any adjoint arm's minimum spend. The 25.0 GiB launch-gate limb opened on **poll 1** at 27.19 GiB with 13 free cores, and the realised contention factor was **1.1955×** against a 1.7× point measured on a contended box (L-278). Source: same file §2.1, §5, §7; `ledger.txt`, `rss_patched.txt` in the run root.
**N-D34. An adjoint on a COLD-staged DAFoam case buys the `dRdW` colouring, and a mid-run adjoint anchor under-prices it by roughly 2.5× — measured on A1 NACA0012, np=1, `dafoam/opt-packages:latest`.** Mid-run adjoint (arm O's log, elapsed `273.19 s → 281.77 s`): **8.58 s**. Cold first adjoint on the same case at the same design point: **≈ 23 s**, of which **14.47 s is `Calculating dRdW Coloring... Completed!`, stated by the log itself**, not inferred. **Pricing rule that follows: an adjoint on a cold-staged case is `mid-run adjoint anchor + the colouring cost`, and the colouring is READ FROM A LOG LINE, never estimated.** Conversely and in the opposite direction, a cold primal at an **already-converged** design point is ~3× cheaper than one at an arbitrary deformed point (**≈ 6 s** measured against **20 s** registered) because the injected vector is already the optimum and the primal converges in ~60 iterations from `0/`. The two errors are **+14 s and −14 s** and nearly cancelled: the item's headline ratio **0.915×** would have read ~0.77× or ~1.06× had either occurred alone, so **the headline is the least informative number in that record**. Source: `cases/dafoam/ladder-a/A1/curriculum_D1_Cprime/RESULTS.md` §10, §10.1; run-root `ledger.txt`; `docs/COST_CALIBRATION.md` C-31.

**N-D35. A cross-run analytic-gradient comparison between two containers has a RESOLUTION FLOOR set by the primal state difference, and `patchV` measures that floor.** A1 NACA0012, np=1, arm O's converged design vector injected into a cold shipped-image solve: `|CD_A − CD_B| = 9.23e-09` between the cold single solve and the warm major-11 endpoint at the **same** design vector. The `patchV[1]` component — which never crosses `warpDeriv` (IG-2) and was **bit-identical across the two images at the undeformed baseline** — nonetheless differs by **1.69e-06 relative** across the two runs. Because that component cannot carry a warp-derivative defect, its cross-run difference **is** the floor. **Consequence, and it is a reporting rule: any claimed toolchain difference below ~`1e-5` relative in such a comparison is AT THE FLOOR and must be reported as an UPPER BOUND, never as a resolved value.** The shipped-vs-patched analytic difference at this design point is `5.16e-08` absolute / `2.80e-06` relative — inside the floor, hence reported as an upper bound (against a predicted `6.76e-03` / 640 % carried from the baseline, five orders of magnitude out). Source: same file §2, §3, §6; graded `5bec45b7`.

## N-AV1. The Ansys Fluid Dynamics Verification Manual describes itself as verification, NOT validation: one mesh, one model, one scenario, a 3 % accuracy goal, and cases that may not be grid-independent

**Family note.** `N-AV*` is the ansys-verification team's numerics family
(ANSYS_VERIFICATION_CHARTER §7). Everything below is quoted from the manual
sidecar
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
(VM2026R1, March 2026), with the manual's own printed page numbers.

**§1.2 Expected Results (p. 4), verbatim (the "Important" box):** *"It should be
noted that these are not validation cases of the models presented. The test cases
are single instance simulations using one mesh, one turbulence model, and one
scenario of the model."* And, on grid independence (p. 4): *"An attempt has been
made to present a test case and results that are grid-independent. If test
results are not grid-independent, it is due to the need to limit the run time for
the test to be in the manual. Improved results can be obtained in some cases by
refining the mesh, but this requires longer solution times."*

**§1.3 References (p. 5), verbatim:** *"The goal for the test cases contained in
this manual was to have results accuracy within 3% of the target solution."*

**§1.4 Verification and Validation (p. 5), verbatim:** *"The test cases provided
in this manual are a single instance, using one mesh, one turbulence model, and
one scenario for the model. They are not validation cases of the models presented
since they do not provide, nor attempt to provide, the necessary methodology on
how to arrive at the presented results. The intent of these cases is to provide a
means to verify that you are obtaining the same results in your computing
environment as ANSYS obtained in its computing environment."*

**Two consequences for this lab.** (1) A register `PASS` on any of these cases
validates the **lab's own solver against a reference value**, not a physical
model — the manual explicitly disclaims model validation, so credential wording
must not claim more. (2) The manual's own accuracy goal is **3 %** and its cases
**may not be grid-independent** (grid independence is sacrificed to run time by
the manual's own statement); therefore a lab **CONVERGING Roache triple** with a
GCI is **new information the manual does not itself provide**, and a lab band
tighter than 3 % is a stronger claim than the manual makes.

## N-AV2. VMFL001's analytical tangential-velocity field is independent of viscosity and density, so a wrong μ passes the velocity gate — the μ-sensitive check is the wall torque, for which the manual prints no reference

**The fact.** For steady laminar flow between a rotating inner cylinder and a
stationary outer cylinder (VMFL001, p. 15), the closed-form tangential velocity
`v_θ(r) = Ω r_i²/(r_o²−r_i²)·(r_o²/r − r)` depends **only** on the geometry
(`r_i = 17.8 mm`, `r_o = 46.28 mm`) and the inner-wall angular velocity
(`Ω = 1 rad/s`). It contains **neither μ nor ρ**: the creeping annular solution
is set by the boundary conditions, and μ and ρ cancel out of the velocity field
entirely. **A lab run with the wrong viscosity (or the wrong density) still
reproduces the exact velocity profile and passes the manual's velocity gate.**

**The μ-sensitive diagnostic (lab-added; no manual reference).** The quantity
that does see μ is the viscous torque per unit axial length on the inner
cylinder, `M'/L = 4π μ Ω r_i² r_o²/(r_o²−r_i²)`. At the manual's
`μ = 0.0002 kg/m·s` this is **9.345533e-7 N·m/m** (linear in μ, independent of ρ).
**The manual prints no target for it** — it is a lab-added control that would
catch a μ error the velocity gate cannot see. Any lab report on VMFL001 that
claims to have exercised the viscosity must cite this torque, not the velocity.

## N-AV3. VMFL001 printed-target rounding: the manual's four-figure Targets deviate from the exact solution by −0.133 / −0.319 / +0.187 / +1.148 % at r = 20/25/30/35 mm

**The fact.** Evaluating the exact `v_θ(r)` (N-AV2) at the manual's four radii
and comparing with the manual's **printed Target** column (Table .01.1, p. 16):

| r (mm) | exact v_θ (m/s) | printed Target | (Target−exact)/exact |
|---|---|---|---|
| 20 | 0.0151201 | 0.0151 | **−0.133 %** |
| 25 | 0.0105331 | 0.0105 | **−0.319 %** |
| 30 | 0.0071868 | 0.0072 | **+0.187 %** |
| 35 | 0.0045478 | 0.0046 | **+1.148 %** |

The r = 35 mm target is +1.148 % from exact from four-figure rounding alone.
Ansys Fluent's own reported value there, **0.0045**, is **−1.05 %** from exact —
i.e. closer to the exact solution than the printed target is — yet the manual's
Ratio column reads it as **0.978** (CFX 0.976). See L-280: a tolerance drawn
from the Ratio column is set against a rounded target, not the reference. The lab
gates against the printed Target (the manual's reproducibility claim) and prints
these four exact-formula deviations beside the gated values.

## N-AV4. OpenFOAM v2606 `sets` (`type cloud`, `setFormat raw`) writes `postProcessing/<fo>/<time>/<setName>_<fields alphabetical>.xy` with NO header — set name FIRST, not field first

**The fact.** The `sets` function object in OpenFOAM **v2606**, configured with
`type sets` / `setFormat raw` and a set of `type cloud`, writes one file per
time directory per set, named:

    postProcessing/<functionObjectName>/<time>/<setName>_<field><_field...>.xy

- **the SET NAME comes first**, then the fields, joined by `_`;
- **the fields appear in ALPHABETICAL order**, not in the order they are listed in
  the `fields (...)` entry — `fields (p U)` and `fields (U p)` both give `_p_U`;
- **there is NO `#` comment header** of any kind — the file's first line is data;
- columns are **`x y z`** and then the fields in that same alphabetical order, each
  contributing its component count: a scalar 1 column, a vector 3.

So `functions { radialProbes { type sets; setFormat raw; fields (p U);
sets { gateAxis { type cloud; ... } } } }` at time 3000 produces
`postProcessing/radialProbes/3000/gateAxis_p_U.xy` with **7 columns**:
`x y z p Ux Uy Uz`.

**The measurement that shows it.** VMFL001 run 1, all three levels. The L3 file's
first row, verbatim from disk:

    0.02 	0 	0.0025 	2.92410904085e-05 	-1.25945914166e-09 	0.0151084998672 	1.14918639546e-24

read as x = 0.02 m, y = 0, z = 0.0025 m, p = 2.924e-05, then `U` = (−1.259e-09,
0.01510850, 1.149e-24) — `U_y` dominant on the +x axis, which is what a tangential
velocity must look like there, and `U_z` at round-off in a one-cell-thick planar
case. Four rows, one per sampled radius, no header line. Identical layout in
`gateAxis_p_U.xy` and `azimuthCheck_p_U.xy` at all three levels.

**Why it is written down.** A comparator frozen expecting `U_gateAxis.*` **with** a
`#` header — the plausible and wrong belief — refuses to find its file and the rung
is lost. That happened here: `grade_vmfl001.py` refused exit 2 and VMFL001 run 1 is
`NOT A RESULT`. The general lesson is `L-288`; this entry is the specific fact so
the next comparator in this lab is written against the producer instead of against a
belief about it.

**Scope, stated honestly.** Measured on **v2606** only, `setFormat raw`,
`type cloud`, `interpolationScheme cellPoint`, in a 2D planar case. The alphabetical
ordering and the missing header were **observed, not read out of the source**; other
`setFormat` values (`csv`, `vtk`, `gnuplot`) are not covered by this entry and other
OpenFOAM versions are not either. The `probes` function object, by contrast, **does**
write `#` header lines — the two function objects differ, which is part of the trap.

*Artifacts:* `verification/runs/ansys_verification/VMFL001/L*/postProcessing/
radialProbes/3000/{gateAxis,azimuthCheck}_p_U.xy` and, for the contrasting `probes`
header, `.../L*/postProcessing/gateProbes/0/U`, committed `ae30f914`;
`.../GRADING_VMFL001.stdout.txt` (the refusal);
`cases/ansys_verification/VMFL001/RESULTS.md` §3.

## N-AV5. VMFL001 laminar `simpleFoam` at `p 0.3 / U 0.7`: 3000 iterations reach Ux initial residual 4.7e-14 at 1,024 cells, 1.5e-12 at 4,096 and only 1.2e-6 at 16,384 — the fixed-iteration residual degrades sharply and NOT by a constant factor

**The fact, as measured.** Steady laminar `simpleFoam`, the VMFL001 annulus
(R_i = 17.8 mm, R_o = 46.28 mm, ω = 1 rad/s, ν = 2e-4 m²/s), full 360° planar mesh,
central schemes, `p` GAMG / `U` smoothSolver, relaxation **`p 0.3` / `U 0.7`**, no
`residualControl`, **`endTime = 3000` iterations at every level**. Initial residual
at the **final** iteration, and peak-to-peak of the per-iteration v_θ(35 mm) probe
over the last 600 iterations:

| level | cells | Ux | Uy | p | plateau ptp (m/s) |
|---|---|---|---|---|---|
| 16 × 64 | 1,024 | 4.69187e-14 | 4.56645e-14 | 6.50871e-11 | 1.00e-14 |
| 32 × 128 | 4,096 | 1.48771e-12 | 1.48751e-12 | 4.85296e-11 | 1.27e-11 |
| 64 × 256 | 16,384 | 1.19876e-06 | 1.19876e-06 | 2.89185e-06 | 2.77178e-05 |

**The degradation is not one number, and the entry refuses to average it.** Each
step is a 4× increase in cells (2× in each direction). The Ux residual at fixed
iteration count rises by **≈ 32×** from 1,024 → 4,096 cells and by **≈ 8.0 × 10⁵×**
from 4,096 → 16,384. Quoting a single "≈10⁶-fold per 4× cells" would describe only
the second step; the honest statement is that the degradation **accelerates**, and
that the finest level is the only one that fails a 1e-6 criterion. The plateau ptp
tells the same story with different arithmetic: 1.00e-14 → 1.27e-11 (≈ 1.3e3×) →
2.77e-05 (≈ 2.2e6×).

**Mechanism: UNTESTED, and named only as a candidate.** The expected cause is that
SIMPLE's convergence rate depends on the mesh through the pressure solve and the
relaxation, so a fixed iteration budget buys less convergence as cells grow. That is
**not measured here** — this run varied cells and held relaxation, solver tolerances
and iteration count fixed, so it cannot separate the pressure-solve contribution
from the relaxation's. **No iteration-count-to-convergence curve was recorded**, and
none is inferred. What is measured is the table above.

**Consequence, which is the reason to record it.** VMFL001 run 1 registered a single
`endTime = 3000` across its grid triple and an iterative-convergence clause of
< 1e-6 at every level. L1 and L2 pass by 8 and 6 orders of magnitude; **L3, the
level the gate is defined on, fails**, and the rung is `NOT A RESULT` under
CLAUDE.md rule 5 step 1 before the triple is classified. The planning figure for the
next VMFL001 freeze: **3,000 iterations is not enough at 16,384 cells at this
relaxation** — size the budget for the finest level or stop on a residual criterion.
The general rule is `L-289`.

**Scope.** One case, one solver, one relaxation pair, one scheme set, three meshes,
`endTime` fixed. Do not read it as a law about `simpleFoam`; read it as this
configuration's measured numbers and as a warning about fixed iteration budgets
across a refinement study.

*Artifacts:* `verification/runs/ansys_verification/VMFL001/L*/log.simpleFoam` (final
`Time = 3000` block) and `.../L*/postProcessing/gateProbes/0/U` (3,000 rows each,
probe 3 = r = 35 mm), committed `ae30f914`;
`cases/ansys_verification/VMFL001/PREREGISTRATION.md` §6 (solver settings) and §7
(the frozen clauses); `cases/ansys_verification/VMFL001/RESULTS.md` §4.

**N-D36. Two optimizers one CLI token apart on the same NLP reach designs 33.259 % apart in relative L2 while their objectives agree to 0.7381 % — on the A1 NACA0012 lift-constrained drag NLP the objective is NEAR-FLAT along the direction that separates them.** Measured, A1 NACA0012, np=1, byte-identical `d1_opt_runScript.py`, `dafoam-idwarp-rot:v1`: IPOPT reached `CD = 0.017527899854535338` in 11 majors; SLSQP reached `CD = 0.017657273` in 13 iterations (`Inform 0`). Gate `AB1` (objective) **PASS** at `|ΔCD|/CD_A = 0.7381 %` inside its registered 1.0 %; gate `AB2` (design vector) **GATE FAIL** at `‖Δshape‖₂/‖shape_A‖₂ = 33.259 %` against a registered 10.0 % and `‖Δshape‖_∞ = 1.9379e-02` against `8.0e-03`, with `|ΔAoA| = 0.2428°` **inside** its 0.25° band — so the divergence is in the FFD shape modes, not in angle of attack. Both arms satisfied their own per-arm gates (endpoint FD worst 0.2553 % arm A / 0.2485 % arm B, 4/4 components, **zero sign flips**), so neither design is an unconverged artefact. **This is an ALGORITHM/CONDITIONING fact and is never to be read as an aerodynamic claim**: nothing here says which design is better, and two algorithms reaching two points is not evidence that either is a local rather than a global optimum. **Consequence for band-setting: an optimiser's own final step norm does not bound the spread of two optimizers' optima (`L-296`)** — the AB2 band was built on IPOPT's `‖d‖ = 6.09e-03` / 6.486 % basis and was missed by 5.1×. Source: `cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md` §6; raw `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/ab_report_20260824T180411Z_1530445.json`; prereg frozen `03580b8f` (bands at §6.2, P8 at :618).

**N-D37. `ParOpt` ships in `dafoam-idwarp-rot:v1` WITHOUT its compiled extension and does not import; `SNOPT` and `NLPQLP` are absent — this box has NO importable trust-region optimizer.** Measured by a 2 s × 1 rank image probe (**0.0333 core-min**, rc 0) on the graded image, `pyoptsparse 2.10.1` at `/home/dafoamuser/dafoam/packages/miniconda3/lib/python3.10/site-packages/pyoptsparse/`. `ParOpt` (a trust-region interior-point method) is present as a package directory `pyParOpt/` **with no compiled `.so`** and fails to import; `SNOPT` (licensed) and `NLPQLP` fail on absent compiled modules. The compiled extensions actually present are `pyipoptcore`, `slsqp`, `psqp`, `conmin`, `nsga2`. **Instantiable set: `IPOPT`, `SLSQP`, `PSQP`, `CONMIN`, `NSGA2`, `ALPSO`** — of which IPOPT is line-search interior-point and SLSQP is line-search active-set SQP, so **every available method is a line-search method**. This is the A6 forward-AD precedent's shape: a "supported" capability that does not run. **Consequence, and it is a planning rule: any curriculum or ladder row promising trust-region behaviour is `NOT DELIVERED BY CONSTRUCTION` until someone decides to build the extension, and that decision is not a lane's.** Curriculum D2's row is the first to carry that label; the narrowing is on Sanaa's desk as a supervisor NOTICE and is **not read into the 2026-08-21 blanket** (`CLAUDE.md` rule 9). Nothing about building `ParOpt` was run, costed or prepared. Source: `cases/dafoam/ladder-a/A1/curriculum_D2/PREREGISTRATION.md` (disclosed on its first screen, frozen `03580b8f`) and `RESULTS.md` §1, §9.1, §10.4.

**N-D38. A1 at np=1 on `dafoam-idwarp-rot:v1` is bit-reproducible across SESSIONS through a whole optimisation — five identity rows measured EXACTLY `0.0`, not merely inside `1e-9`.** Gate `AB5`, graded **before** arm B was launched: arm A reproduced curriculum D1's arm O **exactly** — `CD_feasible`, `CD`, `CL`, all eight `shape` modes, `AoA` and the major-iteration count identical to the last printed digit — from a **freshly staged case, in a different session, 2 h later, on a box carrying a concurrent lane**. This is **stronger than A4 §3.2's 1.8e-07 same-optimizer figure** and stronger than the cold-primal bit-identity D1 §3 measured, because it holds through **11 optimiser majors, ~12 primal solves and `findFeasibleDesign`**, not through a single evaluation. **Practical use: an A/B on this case does not need a repeat arm to establish its own reproducibility floor — the floor is zero**, and any measured A/B difference is therefore entirely attributable to the varied factor. **Scope:** this case, this image, np=1, this script; it is not a claim about DAFoam reproducibility in general and says nothing about np>1. Source: `cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md` §3; `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/ab5_20260824T175746Z_1524887.json` (reproduced identically in `ab_report_20260824T180411Z_1530445.json`).

**N-D39. The OpenMDAO `debug_print` block count exceeds the optimizer's own reported function-evaluation count by exactly 1, and the offset is optimizer-independent.** Measured 13 = 12 + 1 for IPOPT **twice** (curriculum D1 arm O and D2 arm A) and 16 = 15 + 1 for SLSQP (`NFUNC` read from `opt_SLSQP.txt`). The `+1` is a property of the **driver's printing**, not of either optimizer. **Use: when counting primal evaluations from a log's `debug_print` blocks for costing, subtract one — or read the optimizer's own counter instead, which is the better instrument because it is the optimizer's.** Source: `cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md` §8, §9.1; `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/armA_20260824T175746Z_1524887.log`, `armB/opt_SLSQP.txt`.

**N-D40. pyOptSparse SLSQP's converged termination on this box prints `Inform 0` with `Optimization terminated successfully.` under an `Exit Status` header, and `opt_SLSQP.txt` closes with `ITER = <n>`, `NUMBER OF FUNC-CALLS: NFUNC = <n>`, `NUMBER OF GRAD-CALLS: NGRAD = <n>`.** Measured on D2 arm B: `Inform 0`, `ITER = 13`, `NFUNC = 15`, `NGRAD = 14`. **This wording had never been printed in this lab before** — every prior optimisation row was IPOPT, whose success string is `Optimal Solution Found`. D2's convergence gate therefore keyed on the **numeric `Inform` code** rather than on the string, precisely because the string was unknown at freeze time; the strings are recorded here so the next item can key on them if it chooses. **Rule this supports: when an unfamiliar tool's success wording is not known at freeze time, gate on its numeric status code and record the wording afterwards — never register a string match you have not seen printed.** Source: `cases/dafoam/ladder-a/A1/curriculum_D2/RESULTS.md` §5, §9.1; `/home/ubuntu/certonomous-runs/CURRICULUM-D2-a1-optimizer-ab/armB/opt_SLSQP.txt`, `armB_20260824T180411Z_1530445.log`.

**N-D41. An mphys DVGeo discipline registered with `nom_add_discipline_coords` is addressed as `"x_<discipline>0"`, never `"<discipline>"`, and `DVGeo.update()` takes THAT key.** pyGeo's `mphys_dvgeo.py`, method `nom_add_discipline_coords(self, discipline, points=None)`, builds the point-set name as `"x_%s0" % discipline`: the else-branch calls `self.nom_addPointSet(points, "x_%s0" % discipline, add_output=False)` and the component declares `add_input("x_%s_in" % discipline)` / `add_output("x_%s0" % discipline)`. **With `discipline="aero"` the registered key is `"x_aero0"`, and `"aero"` is embedded nowhere** — which is also why the mphys wiring pattern reads `self.connect("mesh.x_aero0", "geometry.x_aero_in")` and `self.connect("geometry.x_aero0", "scenario1.x_aero")`. **Consequence, measured:** `dvg.update("aero")` raises `KeyError: 'aero'` from `pyBlock.getAttachedPoints` at `pyBlock.py:745` (`self.embeddedVolumes[ptSetName]`), reached from `DVGeo.py:2012`; the correct call is `dvg.update("x_aero0")`. Measured on the D3 attempt-2 Stage-G producer, image `dafoam-idwarp-rot:v1`, DAFoam v5.0.0, np = 1, 2,777-cell A4 Ahmed-25 mesh, traceback at `/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/geom.log:472-481`. **This closes the half that `curriculum_D3_attempt2/RESULTS.md` §9.2 left open** — that entry established that `"aero"` is *not* the key and said in terms that it did not establish what the key *is*. **Rule this supports:** a wrapper that composes a registration key from an argument is not addressed by the argument; read the composer, not the call site. **Provenance limit, stated: `VERIFY`.** The source read is the dafoam-supervisor's own, 2026-08-24, of a copy extracted from a DAFoam image to a temporary location that no repository document may cite (`CLAUDE.md` rule 13, L-186); the **durable in-image citation is `PENDING`** — no lane on this box could reach the docker socket to record the absolute in-image path and the image ID (`DAFOAM_CHARTER.md` §6: the hash is the identity, not the tag), and `find / -name mphys_dvgeo.py` returns zero hits on the host because pyGeo is installed only inside the images. **The completed row must show md5 `e3ee130ac86bc524d6296132fae7695f`, size 25,180 bytes, mtime 2026-05-04 at a named absolute path inside a named image ID.** The *consequence* limb — the `KeyError` and its traceback — is durably cited above and does not depend on that. Source: `cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/RESULTS.md` AMENDMENT 1 §A1.2 and §A1.2.1; `.../d3_runScript.py:253` (the defect) and `:155-157` (the mphys connect pattern).

## N-AV6. Richardson extrapolation of a CONVERGING second-order triple lands on the analytic solution three orders finer than the finest grid — VMFL001-R2 hits White §3-2.3 to 3.7 ppm without ever seeing the formula

**The fact, as measured.** VMFL001-R2, v_θ at r = 35 mm, grid family refined by
exactly 2 in each direction (16 × 64 → 32 × 128 → 64 × 256 cells), laminar
`simpleFoam`, all three levels iteratively converged and plateaued:

| level | cells | v_θ(35 mm), m/s |
|---|---|---|
| coarse `L1_16x64` | 1,024 | **0.0045145840** |
| medium `L2_32x128` | 4,096 | **0.0045395745** |
| fine `L3_64x256` | 16,384 | **0.0045457781** |

`R = d21/d32 = 0.2482366` ⇒ **`CONVERGING`**; observed order **p = 2.0102**;
**GCI_fine (Fs = 1.25) = 5.632839e-04 = 0.0563 %**. R ≈ 1/4 and p ≈ 2 on a family
refined by 2 is the formal second order of the frozen `fvSchemes` recovered to
0.5 %.

**The extrapolation beats its own finest grid by three orders of magnitude.**
Richardson extrapolated value **0.00454782654 m/s** against the exact White §3-2.3
value **0.00454780952 m/s** — a difference of **1.70e-11 m/s = 0.000374 %**, while
**the fine grid itself is 0.0447 % off**. Ratio ≈ 120×. The extrapolation is
computed from the three lab values and the refinement ratio **only**; it never sees
the analytic formula, so the agreement is a genuine test of the discretisation's
asymptotic behaviour and not a fit. Read it as: on a clean second-order triple in
the asymptotic range, the *extrapolant* is the accurate number and the finest grid
is merely the best input to it.

**The gate context, recorded with it.** The manual's printed target at 35 mm is
**0.0046 m/s** where the exact value is **0.00454781** — the manual's own
four-figure rounding is worth **1.148 %**. The lab's deviation from that printed
target is **1.179 %**, so **97 % of the gate deviation at 35 mm is the manual's
rounding**, not this lab's solver: against the exact formula the same value deviates
by **0.0447 %**. **The frozen 2 % gate held with the lab 0.045 % from exact.** This
is the quantitative form of `N-AV3` and the reason a printed-target gate must be
sized against the printing, not against the physics.

**Residual-decay extrapolation, same rung, also held.** The R2 freeze predicted L3's
iteration budget from a log-linear fit to run 1's `Ux` initial residual over
iterations 2,000 → 3,000: slope **−9.6065e-04 decades/iteration**, predicting
**≈ 1.57e-09 at iteration 6,000**. Measured at 6,000: **1.61027e-09** —
**ratio 1.026**, a 2.6 % miss on a two-decade extrapolation across 3,000 iterations.
A residual decay that is log-linear over a 1,000-iteration window stayed log-linear
over the next 3,000 here; that is a usable planning instrument for sizing an
`endTime`, and it was used exactly that way before compute.

**Scope.** One case, one quantity, one triple, one solver. The three-orders result
requires all of: `CONVERGING` state, monotone values, observed order close to
formal, and an exact solution to check against — VMFL001 has all four, which is
rare. Nothing here licenses quoting an extrapolant where the triple is not
`CONVERGING` (CLAUDE.md rule 5 forbids it) or where the three values are not
monotone.

*Artifacts:* `cases/ansys_verification/VMFL001/R2/RESULTS.md` §3 and §4 (the gate
table, the Roache table, the extrapolant);
`verification/runs/ansys_verification/VMFL001/R2/L*/postProcessing/radialProbes/<endTime>/gateAxis_p_U.xy`
(the three sampled values) and
`.../R2/L3_64x256/log.simpleFoam` (`Ux` initial residual 1.61026505382e-09 at
`Time = 6000`), committed `fd2321ef`;
`cases/ansys_verification/VMFL001/R2/PREREGISTRATION.md` §3.2 (the frozen
residual-decay fit and its 1.57e-09 prediction), frozen at blob `c6b4a7c4`;
manual sidecar
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt`
Table .01.1 (printed target 0.0046 at r = 35 mm).

**N-T8. A Richardson extrapolate is the one grid-convergence output whose SIGN a key-presence selftest cannot catch, and four independent implementations in this lab got it wrong the same way.** `f_ext = f_f + (f_f - f_m)/(r^p - 1)`; written with `e21 = f_m - f_f` that is `f_f - e21/den`, and `f_f + e21/den` reflects the limit through the finest value onto the coarse side. **Wrong by construction, right-looking on every printout**: the value has the right magnitude, the right units and a plausible position between the levels, and `GCI` (which takes `|e21|`) and the observed order `p` are both sign-independent, so every neighbouring number stays correct. Defective: `T-family/T1_runs/analyse_t1c.py:337`, `T-family/T3_runs/analyse_t3.py:384`, `T-family/T9a_runs/analyse_t9a.py:241`, and — independently written, not shared code — `F14-cooling-ladder/K0cG_runs/analyse_k0cg.py:107` and `K0cX_runs/grid_convergence.py:106`. Correct: `K0b_*/analyse_k0b_mesh.py:319`, `T9a_runs/analyse_t9aD.py:129`, `E4_runs/analyse_e4a.py:128`, `T10a_runs/analyse_t10a.py:611`, `T10aR_runs/analyse_t10aR.py:146`. **THE STANDING RULE, adopted 2026-08-24: every T-family and F14 comparator's `--selftest` must carry a VALUE-checking Richardson control — a synthetic power-law triple `f_k = f_ex + A (r^p)^k` whose limit `f_ex` is known by construction, asserted to 1e-12 relative — and not merely a check that the key exists.** `analyse_t1c.py`'s and `analyse_t3.py`'s frozen selftests check **existence only**, which is why the defect survived every run of both; `K0cG`/`K0cX` carry no Richardson control at all. Already satisfying the class, at a looser tolerance: `E4_runs/analyse_e4a.py:759-764`, control **"corrected vs frozen (sign-defect) Richardson"** (1e-8 relative, and it asserts the frozen form is *worse*), repeated by `E4a2_runs/analyse_e4a2.py:575-577`; `T10aR_runs/analyse_t10aR.py:383-406`, four controls including **"richardson_corrected recovers the exact value of a clean power law"** and **"the shared gci's own richardson carries the registered SIGN DEFECT"**; `analyse_t9aD.py:214-242`. **A second, free check that needs no synthetic case:** the two forms satisfy `frozen + corrected == 2 f_fine` exactly, so any comparator printing both can assert the identity on real data — verified on T10a (`-3271.6099514453667` + `-3267.5943548617456` = 2 × `-3269.602153153556`, its own fine value) and on E4a2 R1 (`1.506878761e-07` + `1.497435362e-07` = 2 × `1.502157061e-07`, its own G1 fine `Q`). **No verdict in this lab was ever a function of a Richardson value** — the T-family trace of 2026-08-24 read the grading operands of every consuming comparator and found the extrapolate display-only everywhere (`analyse_t1c.py:446-470`, `analyse_t9a.py:409-441`, `analyse_dts.py:944`, `analyse_dts_p.py:639`, `grid_convergence.py`, `analyse_k0cg.py:142`) — but seven published numbers moved when the sign was corrected, one of them materially (T1c's constant-`q″` h→0 excess, +0.0748 % → +0.0013 %). Source: `CROSS_TEAM_GATE_AUDIT.md` §66/§72; `T9a_RESULTS.md` §8 item 1; `verification/runs/T-family/T3_runs/analyse_t3.ADDENDUM_2026-08-24_richardson_sign.md` and `T1_runs/analyse_t1c.ADDENDUM_2026-08-24_richardson_sign.md` (full trace and citer lists).

## N-AV7. A small GCI is a statement about grid convergence ONLY — it does not license the claim that a residual deviation from a reference is numerical; VMFL005 is CONVERGING at 0.05 % GCI yet extrapolates 0.54 % AWAY from the exact value

**The fact, as measured.** VMFL005 (Poiseuille, exact Hagen–Poiseuille 10.24 Pa) and
VMFL001-R2 (rotating cylinders, exact White §3-2.3) are, on their face, identical
strength: both `PASS`, both grid triples `CONVERGING`, both observed order p ≈ 2, both
GCI_fine ≈ 0.05 %. They behave OPPOSITELY under Richardson extrapolation, and that
pairing is the whole force of the entry:

| case | fine-grid dev vs exact | GCI_fine | dev / GCI | Richardson extrapolate | extrapolate dev vs exact |
|---|---|---|---|---|---|
| VMFL001-R2 (`N-AV6`) | 0.0447 % | 0.0563 % | 0.79 | 0.0045478265 m/s | **3.7 ppm** — lands ON exact |
| VMFL005 | 0.4979 % | 0.0502 % | **9.92** | 10.295119 Pa | **0.5383 %** — *further* than the fine grid |

For VMFL005 the deviation from the analytic reference is **9.92× the fine-grid
discretisation uncertainty**, and grid refinement moves the answer *away* from exact:
the extrapolate 10.295119 Pa is 0.5383 % above 10.24 Pa, against the fine level's
0.4979 %. Roughly **90 %** of the residual deviation is a modelling/setup signature,
not discretisation error.

**The rule.** A converging Roache triple with a small GCI certifies only that the
answer has stopped moving with mesh — grid convergence, nothing more. It does NOT
certify that the code converges to the *exact* solution, nor that a residual deviation
from a reference is numerical and will shrink with refinement. That claim requires the
extrapolate to LAND on the reference (VMFL001-R2, 3.7 ppm), and it must be checked, not
assumed — VMFL005 is genuinely CONVERGING and lands 0.54 % away. A team scoring a
code-verification column off a small GCI alone would score VMFL005 as fully verified
and be wrong. See `N-AV6` (the case where the extrapolate does land) and `N-AV9` (one
arithmetically quantified contributor to VMFL005's gap). The open mechanism is docket
`D512`.

*Artifacts:* `cases/ansys_verification/VMFL005/RESULTS.md` §5;
`verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json`
(`triple.state=CONVERGING`, `triple.p=1.9340642225610707`,
`triple.gci_fine=5.021172780104668e-04`, `triple.f_extrapolated=10.29511921045573`),
committed `90ee8d80`; `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`
row #3.

## N-AV8. A gate-EXCLUDED null channel is excluded at the FREEZE and still PRINTED, never silently dropped — VMFL005's wedge `Uz` is the out-of-plane direction the wedge constrains rather than solves

**The fact, as measured.** On an OpenFOAM axisymmetric wedge, the z-component of
velocity is the out-of-plane direction the wedge transformation constrains rather than
solves; its solution is identically zero to round-off. VMFL005's final `Uz` initial
residuals are **1.85e-02 / 8.82e-03 / 2.54e-03** at L1/L2/L3 — three to five orders
above the gated `Ux`/`Uy`/`p` channels (worst gated 9.49e-08) — because a *relative*
initial residual normalised by a vanishing scale carries no information. It falls
monotonically with refinement (7.3× coarse→fine), consistent with a round-off-scale
quantity and NOT with a physical residual.

**The method point, which is the reason this is recorded.** `Uz` was excluded from the
convergence gate **by the pre-registration, before any number was seen**, and it is
**printed beside the verdict rather than dropped**. Excluding a channel silently would
be worse than printing it: a reader cannot audit an exclusion they cannot see. The
discipline generalises — every case with a null or non-physical channel names the
exclusion in the freeze and prints the channel's values anyway.

*Artifacts:* `cases/ansys_verification/VMFL005/RESULTS.md` §2.3;
`verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json`
(`iterative_convergence.L*.uz_final_residual`), committed `90ee8d80`;
`cases/ansys_verification/VMFL005/PREREGISTRATION.md` (the frozen exclusion).

## N-AV9. An OpenFOAM axisymmetric WEDGE under-represents the true circular cross-section by sin(t)/t (0.127 % at t = 5°), a MODELLING bias grid refinement does not remove — carry it in the error budget of every axisymmetric case run against an exact target

**The fact.** An OpenFOAM wedge cell is a flat-sided triangle, not a circular sector.
For total included angle `t`, the modelled cross-section area is `½ R² sin(t)` against
the true sector `½ R² t`, short by the factor **`sin(t)/t`**. At `t = 5°`
(`= 0.08726646259971647` rad): **`sin(t)/t = 0.9987312439537492`**, an area deficit of
**0.1268756 %**. This is a property of the mesh, not of the reader: for VMFL005 the
modelled L3 inlet-patch area `½ R² sin(t) = 6.809042402160794e-08 m²` matches the
solver's own monitor-header area `6.809042402188e-08 m²` to eleven significant figures.

**Effect on VMFL005's dP, both readings honestly.** VMFL005's fine-grid dP deviates
0.4979 % from exact while GCI_fine is only 0.0502 % — 90 % of the deviation is not
discretisation error (`N-AV7`). The wedge area deficit is one arithmetically checkable
contributor:
- fixed volumetric flow (dP ∝ R⁻⁴, effective-radius deficit `√(sin t/t)`): dP inflated
  by `(sin t/t)⁻² = +0.2542349500671337 %` — **51.06 %** of the 0.4979 %;
- fixed mean velocity (dP ∝ R⁻², as the imposed inlet profile suggests): dP inflated
  by `(sin t/t)⁻¹ = +0.1270 %` — **25.5 %**.

So the wedge geometry is a **candidate mechanism accounting for a quarter to a half**
of the deviation, and it is **NOT the resolution** — the remaining candidates in
VMFL005 RESULTS §5.3 stay open (docket `D512`).

**The forward-looking rule, which is why this is recorded.** The deficit is
**independent of radial and axial refinement** — the error lives in the AZIMUTHAL
representation, which the wedge holds fixed at one cell of angle `t` while the Roache
triple refines only r and x — so it is a MODELLING error a converging triple carries
to its extrapolate rather than removes. **Every axisymmetric wedge case this team runs
from here carries `1 − sin(t)/t` as a known modelling bias in its error budget**
(VMFL002, VMFL007, VMFL028, VMFL036, VMFL044, VMFL058, VMFL073, VMFL076). Mitigation:
use a **smaller wedge angle** (the deficit is `O(t²)`: `1 − sin(t)/t ≈ t²/6`, so 1° cuts
it ≈ 25×), or **carry the deficit explicitly** in the pre-registration's error budget so
a converging-triple `PASS` is not mistaken for convergence to the exact value.

*Artifacts:* `cases/ansys_verification/VMFL005/RESULTS.md` §5.3;
`verification/runs/ansys_verification/VMFL005/L3_400x40/postProcessing/pInletMonitor/0/surfaceFieldValue.dat`
(monitor-header area `6.809042402188e-08 m²`), committed `90ee8d80`;
`cases/ansys_verification/VMFL005/case/system/blockMeshDict.template` and
`.../constant/polyMesh/boundary` (`wedge1`/`wedge2`, `type wedge`, half-angle 2.5°);
the arithmetic in `docs/ansys_verification/COVERAGE_ROWS.md`.

## N-C1. A snappyHexMesh LEVEL step is not a grid refinement — the `ahmed_25` ladder's rung 2→3 holds the background block byte-identical, and the representative `h` it reports exists nowhere in the mesh

**Family note.** `N-C*` is the cfd team's numerics family, opened 2026-08-25 on the
precedent of `N-D` (*"N-D = DAFoam-team numerics facts, opened 2026-08-21"*, above),
so that cfd-team appends cannot collide with a concurrent closure-, thermal-,
DAFoam- or ansys-team append. Numbers are re-derived at filing time and never
carried in a document.

Measured 2026-08-25 from the three rungs' own dictionaries and `polyMesh` notes,
**ZERO COMPUTE** — no mesher and no solver was run to establish any figure here.

| rung | `nCells` | `blockMeshDict` `blocks` | background cells | `refinementSurfaces body` | `eMesh` | `refinementRegions nearBody` | `addLayers` |
|---|---:|---|---:|---|---:|---|---|
| coarse | 20,621 | `(42 9 25)` | 9,450 | `level (2 3)` | 2 | `levels ((1e15 1))` | `false` |
| medium | 45,753 | `(60 13 36)` | 28,080 | `level (2 3)` | 2 | `levels ((1e15 1))` | `false` |
| production | 79,439 | `(60 13 36)` | 28,080 | `level (3 4)` | 3 | `levels ((1e15 2))` | `false` |

**Two byte-level identities, checked with `cmp` after newline normalisation, are the
whole finding.** The **coarse and medium `snappyHexMeshDict` are byte-identical** — the
recipe is held fixed across gap 1. The **medium and production `blockMeshDict` are
byte-identical**, vertices included — the background is held fixed across gap 2. Coarse
and medium `blockMeshDict` differ on **line 26 alone**, the `hex` entry, so gap 1's
domain box is unchanged and its background scales `(42 9 25) → (60 13 36)`, a factor
**2.9714** in background cells (linear 1.4286 / 1.4444 / 1.4400, cube-root-equivalent
1.4373). **One triple, two different refinement mechanisms, joined mid-ladder.**

**The ratios, from the cell counts at `dim = 3`.** `r21 = (79439/45753)^(1/3) =`
**1.2019**, `r32 = (45753/20621)^(1/3) =` **1.3043**, `|r21 − r32| = 0.1024`. **`r21` is
below the `r ≥ 1.3` floor** — and it is below it *because* that gap spent its refinement
on a local level step instead of on the background, which is the arithmetic tell of the
recipe fork rather than a separate defect.

**What the reported `h` means at gap 2, and this is the numerics content.**
`h = (N_ref/N)**(1/dim)` (`scripts/roache_triple.py:200`) is a volume-average spacing,
and it is a *spacing* only under uniform refinement. Across gap 2 the far field does not
change at all — same 28,080-cell background, same box — while the surface layer splits
by a factor 2 locally. The `h` the convention returns is therefore an average of two
spacings that both exist in the mesh and **is neither of them**: no region of the
production mesh has the spacing its ladder entry reports. Every quantity built on that
`h` — `r`, `p`, the GCI, the Richardson extrapolate — inherits it.

**And no guard in the lab sees it.** `models/curriculum/uq-studies/ahmed_25.json` fits
this triple to `observed_order` **1.95** at `dim` 3 in an `order_window` of [0.5, 2.5],
`monotone` true. **Four of five guards PASS** — `distinct_rungs`, `monotone`,
`order_window`, `increment_trend`. The one failure, `extrapolation_sanity`, fires for an
unrelated reason (`richardson_extrapolated` 0.07327589152491365 falls outside the
measured range 0.08481–0.10099) and is not looking at the recipe. Neither is
`scripts/roache_triple.py`, whose own docstring at `:123-127` states the limit
explicitly: *"whether the three values came from the same case setup. It grades numbers.
… The caller establishes similarity; this file cannot."* So the ladder's protection here
is **accidental**: had `extrapolation_sanity` passed, a recipe-forked triple would read
conclusive at a textbook second-order number.

**Structural identity with a case the lab already named.** This is
`VERIFICATION_CHARTER.md` §3.2's second NACA 4412 ladder — *"coarse and medium are both
`level (2 3)` and differ only in background block density; production alone is
`level (3 4)`"* — rung for rung, in a second family. The 35° sibling
`models/curriculum/uq-studies/ahmed_35.json` (20,425 / 45,813 / 79,778, `r21` 1.2030,
`r32` 1.3093, `observed_order` 3.169) carries the same shape. The NACA ladder was caught
because `p = 10.467` blew the window; **`ahmed_25` was not caught because `p = 1.95`
looked right**, which is the practical difference between a rule that is checkable and a
rule that is checked. §3.2's rule 3 — *"a recipe audit precedes an order"* — has no
mechanised checker, and its absence is what this entry prices.

**The admissibility rule this registers** (lesson `L-303`): a 3-D ladder is a Roache
ladder only if the background `blocks` tuple scales at every gap with `vertices`
unchanged, and `refinementSurfaces` / `eMesh` / `refinementRegions` levels, `addLayers`
and `addLayersControls` are identical across every rung. The compliance artifact is a
per-rung **mesh birth certificate** carrying the block tuple and its product, the vertex
hash, the full snappy level tuple, `addLayers`, `nCells` from that rung's own
`constant/polyMesh/owner` note, and the `dim` established from its own boundary file.
Fail the recipe clause and the ladder is **NOT A RESULT**, not a caveated value.

Source: `mission-output/geometry-study/study-ahmed_25/case/system/{blockMeshDict,snappyHexMeshDict}`;
`mission-output/ahmed-body/act7-ahmed_25/case/system/{blockMeshDict,snappyHexMeshDict}`;
`/home/ubuntu/certonomous-runs/study-ahmed_25-coarse-40aacb/system/` and its
`constant/polyMesh/owner` note (`nCells:20621`; outside git per `docs/LOCATIONS.md`);
`mission-output/*/log.checkMesh:39` (45,753 and 79,439);
`models/curriculum/uq-studies/ahmed_25.json`, `.../ahmed_35.json`;
`verification/campaign/AHMED_BODY_RECONCILIATION.md`;
`verification/campaign/3D_CAMPAIGN_CASE_SELECTION_MEMO.md` §2.3–§2.4;
`scripts/roache_triple.py:123-127`, `:200`; `docs/charters/VERIFICATION_CHARTER.md` §3.2.

---

## FAMILY INDEX — regenerated 2026-08-25 (supersedes any earlier FAMILY INDEX block above)

**How to read this file.** `docs/NUMERICS_KNOWLEDGE.md` is **APPEND-ONLY** and
**PHYSICALLY CHRONOLOGICAL**: entries land at the foot in the order they were written,
**never grouped by family**, because records across the repository cite this file **by
line number** — one of them inside a **frozen** pre-registration
(`cases/dafoam/ladder-a/A4/curriculum_D3/PREREGISTRATION.md:69` → `NUMERICS_KNOWLEDGE.md:3250-3257`)
— and reordering would break every one (CLAUDE.md rule 6). **IDs are per-series**
(`scripts/append_record.py` is series-aware: `N-B26` follows `N-B25` whatever the N-T
tail is at); **bytes are append-only**.

**This index carries NO line numbers** — they go stale on the next append and a stale
index is worse than none. Find any entry by grepping its id. Both heading styles exist
(`## N-<FAM>n.` and `**N-<FAM>n.`), so the locator is, e.g.:
`grep -nE '^(## |\*\*)N-AV[0-9]' docs/NUMERICS_KNOWLEDGE.md`.

**This index is REGENERATED by appending a fresh superseding block at the foot, never
by editing the block above it.** The **lowest** FAMILY INDEX block in the file is the
authoritative one; any block above it is historical. Ids are listed in id order so a
**gap is visible** (e.g. N-B has no `N-B21`).

| Family | Gloss (approximate; the entries themselves are authoritative) | Ids (id order) |
|---|---|---|
| N-AV | Ansys Fluid Dynamics Verification Manual — VMFL cases reproduced in the lab's own solvers as pre-registered verdicts (this team) | N-AV1, N-AV2, N-AV3, N-AV4, N-AV5, N-AV6, N-AV7, N-AV8, N-AV9, N-AV10, N-AV11 |
| N-B | Closure line (RANS/LES): β-field correction, feature-library, clip-repair and injection numerics | N-B1, N-B2, N-B3, N-B4, N-B5, N-B6, N-B7, N-B8, N-B9, N-B10, N-B11, N-B12, N-B13, N-B14, N-B15, N-B16, N-B17, N-B18, N-B19, N-B20, N-B22, N-B23, N-B24, N-B25, N-B26, N-B27, N-B28, N-B29, N-B30, N-B31, N-B32, N-B33, N-B34, N-B35, N-B36, N-B37, N-B38, N-B39, N-B40, N-B41, N-B42 |
| N-C | General CFD meshing: snappyHexMesh / grid-family facts (a LEVEL step is not a grid refinement) | N-C1 |
| N-D | DAFoam adjoint & optimisation: primal/adjoint solver behaviour, gradient verification, optimiser and cost numerics | N-D1, N-D2, N-D3, N-D4, N-D5, N-D6, N-D7, N-D8, N-D9, N-D10, N-D11, N-D12, N-D13, N-D14, N-D15, N-D16, N-D17, N-D18, N-D19, N-D20, N-D21, N-D22, N-D23, N-D24, N-D25, N-D26, N-D27, N-D28, N-D29, N-D30, N-D31, N-D32, N-D33, N-D34, N-D35, N-D36, N-D37, N-D38, N-D39, N-D40, N-D41 |
| N-K | Data-driven closure benchmark numerics: Pope tensor-basis rank, TBNN / SpaRTA conditioning | N-K1, N-K2, N-K3, N-K4, N-K5, N-K6, N-K7, N-K8, N-K9, N-K10 |
| N-T | T-family heat-transfer ladder: GCI / Richardson, thermal grid-convergence numerics | N-T1, N-T2, N-T3, N-T4, N-T5, N-T6, N-T7, N-T8 |
| N-X | Cross-cutting V&V numerics: estimators and tolerances general to verification | N-X1, N-X2, N-X3 |

**Families: 7. Total entries: 115.** Counts are re-derivable by the grep above; this line is diagnostic, not authoritative.

**Lines whose number changed above this section: 0.**


---

## FOOT AMENDMENT — 2026-08-25T02:44:28Z — `ansys-verification`, from VMFL003 (run 1)

**Lines whose NUMBER changed above this section: 0.** **Lines whose CONTENT changed:
exactly TWO, both AGGREGATE cells that a child row obliges to move** (CLAUDE.md rule 10
posture; `verification/runs/ansys_verification/append_guards.py::check_aggregates_moved`):

| line | was | now |
|---|---|---|
| 4062 | `… N-AV8, N-AV9 |` | `… N-AV8, N-AV9, N-AV10, N-AV11 |` |
| 4070 | `Total entries: 113.` | `Total entries: 115.` |

**Proven, not asserted:** with those two lines removed, the prior file and this file's
prefix are byte-identical and positionally unchanged — sha256 `0dcbd45c7d52a7c092c3aa4e8431bfe6852bf0c9941f4adfb00dd3bafc2d07b4`.
Ids re-derived from the tail **inside the committing invocation** (rule 11, `L-313`):
the maximum existing `N-AV` was **9**, never a count.

**ADDENDUM to N-AV9 — 2026-08-25, from VMFL003 (turbulent pipe, Re = 13 692) — A SCOPE
CORRECTION: the +0.25 % Δp consequence above is LAMINAR-ONLY and DOES NOT TRANSFER.**
Recorded as an addendum to this entry rather than a new id, because it corrects the
scope of a figure already stated here.

**The geometric facts above are regime-independent and are re-confirmed exactly.**
VMFL003 re-derived them independently, at the same 5° total angle, inside
`grade_vmfl003.py --selftest`: cross-sectional area ratio `sin(2α)/(2α)` at α = 2.5° is
`0.9987312439537492`, deficit **0.1268756046250763 %** — **reproducing this entry's own
recorded constant digit for digit**. New here: the **wetted (wall) area** ratio is
`sin(α)/α = 0.9996827203920081`, deficit **0.03172796079918827 %**, and the ratio of the
two is **exactly `sec α`**, since `sin(2α)/2 = sin α cos α`.

**WHAT DOES NOT TRANSFER, and why — the defect being corrected.** This entry's Δp
consequence of **+0.2542349500671337 %** is `(sin t/t)^-2`, derived for **VMFL005:
LAMINAR flow at FIXED VOLUMETRIC Q**, where Hagen–Poiseuille's **R⁻⁴** scaling squares
the area deficit. **Turbulent pipe Δp does not scale as R⁻⁴ and VMFL003 does not fix Q**
— its inlet fixes a **velocity** (uniform 50 m/s). Importing +0.25 % into a turbulent,
fixed-U case would **over-state the term by ≈ 2.6×** and would be exactly the defect of
quoting one case's figure inside another case's justification. **Each figure below is
labelled with the regime it belongs to, and none is valid outside it.**

| regime | what is held fixed | Δp bias factor | value |
|---|---|---|---|
| **LAMINAR** (VMFL005) | volumetric **Q** | `(sin t/t)^-2` | **+0.2542349500671337 %** |
| **LAMINAR** | mean **U** | `(sin t/t)^-1` | +0.1270367849608793 % |
| **TURBULENT** (VMFL003) | mean **U**, τ_w fixed | `sec α` | **+0.09526851633199218 %** |
| **TURBULENT** | mean **U**, f responding | `sec α · (cos α)^-n` | **+0.1196374 %** |

**THE TURBULENT TRANSFER IS A BOUNDED ESTIMATE, NOT A FACT, and the derivation is shown
so it can be checked rather than believed.** Two independent routes give the same
leading term:

1. **Force balance.** For fixed wall shear τ_w, the streamwise balance
   `Δp · A_cross = τ_w · A_wall` gives
   `Δp_modelled/Δp_true = (A_wall/A_cross)_ratio = (sin α/α)/(sin 2α/2α) = sec α`
   ⇒ **+0.09526851633199218 %**.
2. **Hydraulic diameter.** The wedge's front/back are `wedge` (symmetry, no shear), so
   only the outer face is wetted: `D_h = 4·(½R² sin t)/(2R sin(t/2)) = D cos α`, i.e.
   **D_h is LOW by 0.09517784181422018 %**. With `Δp = f (L/D_h) ½ρU²` at fixed U, the
   `1/D_h` factor contributes the same **`sec α`**.

**Route 2 adds a second-order term route 1 cannot see**, and it is what makes this a
**band rather than a point**: `Re_h = U D_h/ν` is also low by 0.0952 %, and `f` responds.
The local logarithmic slope of the Colebrook `f` at Re = 13 691.740248127866 is
**`n = -dln f/dln Re = 0.255625048426263`** (computed, not assumed), giving
`f(Re cos α)/f(Re) = 1.000243456811933`, i.e. **+0.024346 %**. A Blasius `n = 0.25`
closes to +0.1190998 %, so the bound is tight and not sensitive to the choice of `n`.

> **BOUNDED ESTIMATE, TURBULENT SMOOTH PIPE, FIXED MEAN VELOCITY, 5° wedge:
> Δp is biased HIGH by +0.095 % … +0.120 %.** The lower edge holds τ_w fixed; the
> upper edge lets `f` respond to the hydraulic-diameter deficit. **It is one-signed and
> AZIMUTHAL — no axial or radial refinement removes it** — and it scales as `α²/2`, so
> halving the wedge angle quarters it.

**Honest limits of this estimate.** It is a *geometric* bias computed from exact
mesh arithmetic and a correlation's own Re-sensitivity; it is **not** a measurement of
what OpenFOAM's wedge discretisation actually did, and no run isolated it. On VMFL003 it
is **≈ 0.1 % against a measured 4.34 % gate deviation — about 2 % of the discrepancy**,
so it neither explains nor materially offsets that case's outcome. VMFL003's error
budget carried the **leading** term (+0.0953 %); the upper edge would raise its linear
worst case from ≈ 0.98 % to ≈ 1.01 %, **changing no gate, band or verdict**.
Source: `cases/ansys_verification/VMFL003/{PREREGISTRATION.md §7b, RESULTS.md}`,
`grade_vmfl003.py --selftest` (60 checks, 0 failures).

## N-AV10. A ratio-2 RADIAL grid triple cannot coexist with a standard wall function below R⁺ ≈ 600 (pipe: Re ≈ 21 252) — refine AXIALLY and hold N_r fixed; VMFL003 did, and the wall treatment stayed identical to 1.4e−4 across all three levels

**The constraint, derived before any run and then confirmed by it.** A standard wall
function (`nutkWallFunction`, the OpenFOAM analogue of Fluent's and CFX's standard) is
valid only with the first cell centre in the log layer: **y⁺ ≳ 30** at the bottom and
**y/R ≲ 0.2** at the top, so the admissible window is **y⁺ ∈ [30, 0.2 R⁺]**. A
three-level ratio-2 family spans a factor of **4** in y⁺. It fits only if
**0.2 R⁺/30 ≥ 4**, i.e. **R⁺ ≥ 600**. For a pipe, `R⁺ = (Re/2)√(f/8)`, which puts the
threshold at **Re ≈ 21 252** (f = 0.02551 there). **No grading rescues a case below it:**
with N_r uniform radial cells the first centre sits at `R/(2N_r)`, so y⁺ = R⁺/(2N_r) and
more radial resolution always means *lower* y⁺ — δ₁ < R/N_r always.

**VMFL003 (Re = 13 691.740248127866, R⁺ = 408.3503397076439) is below the threshold**;
its admissible window was y⁺ ∈ [30, 81.67], a factor of only **2.72 < 4**, mapping to
**N_r ∈ [2.50, 6.81]**. The design forced by this: **hold N_r = 5 fixed across the whole
Roache triple and refine axially by 2.**

**MEASURED, and the design worked exactly as intended.** Mean wall y⁺ at endTime across
the three levels: **37.60534067864 / 37.60077854753 / 37.60014411059** — a relative
spread of **1.4e−4**. The wall treatment was therefore *identical* at every level, so
the triple measured axial discretisation and **not** a wall-function regime change. All
three sat mid-band against a declared [25, 65] clause.

**THE PRICE, and it is the part to carry forward: such a GCI bounds the AXIAL channel
ONLY, and on VMFL003 that channel was negligible while the invisible one was not.** The
axial level-to-level differences were **0.161 Pa and 2.006 Pa on 20 800 Pa (7.8 ppm)**,
while a declared wall-treatment ladder at fixed N_x = 500 and N_r = 3/4/5/6 (y⁺ 60.02 →
31.66) moved Δp across **1.7356 %** — **a factor of ≈ 2200 larger than the channel the
GCI can see, and 70 % of that case's whole 2.5 % gate band.** **A small GCI on such a
family is not evidence of grid independence and must never be reported as if it were.**
Run a declared wall-treatment ladder beside the triple and print its spread next to the
GCI. Source: `cases/ansys_verification/VMFL003/{PREREGISTRATION.md §4.2–§4.4, RESULTS.md
§3–§5}`, `verification/runs/ansys_verification/VMFL003/GRADING_VMFL003.json`.

## N-AV11. OpenFOAM v2606 `simpleFoam` + `kEpsilon` + `nutkWallFunction` UNDER-predicts developed smooth-pipe friction by 4.63 % at Re = 13 692 — a one-signed model bias 3.6× the band that both Ansys codes pass

**The measurement.** VMFL003 reproduced the manual's turbulent pipe (Re = 13 691.74,
L/D = 500, standard k-ε coefficients written out explicitly, not defaulted). At the
finest level, converged to **7.8 ppm** between the two finest grids:

| quantity | lab | reference | deviation |
|---|---|---|---|
| **f_dev**, developed region, entrance and BC effects removed | **0.027147309070475995** | Colebrook **0.028464169573919965** | **−4.626379490974265 %** |
| Δp inlet→outlet | **20 800.824487444752 Pa** | manual target **21 744 Pa** | **−4.337635727351215 %** |
| Δp inlet→outlet | same | exact Colebrook **21 792.879830032474 Pa** | **−4.552199389548252 %** |

**It is the MODEL, and three separate arguments close off the alternatives.** (i) The
axial discretisation channel is **7.8 ppm** — three orders below the deviation. (ii) The
gap between f_dev (−4.626 %) and Δp (−4.338 %) is **+0.29 %**, which lands inside the
independently pre-registered entrance excess of **+0.28 … 0.70 %** — so the entrance
treatment behaved as budgeted and is not hiding it. (iii) The wedge azimuthal bias is
**+0.10 %** (`N-AV9` addendum) and is the wrong sign to help. **After every declared
systematic (≈ 0.98 % worst case, linear) the residual is ≈ −4.3 %, one-signed and
unattributed.**

**Why this is worth a numerics entry rather than a case footnote.** The manual's own two
implementations of the *same* stated model differ by only **1.210428 %** on this exact
case (Fluent 21 480 Pa, CFX 21 740 Pa), and the lab's 2.5 % band was deliberately built
wide enough to pass **both**. **The lab missed that band by 3.6×.** So the difference is
not the ordinary inter-code spread of correctly-implemented k-ε: something in this
lab's wall treatment differs in kind. **The suspect is named and NOT claimed** — no
second wall function was run, and `nutUSpaldingWallFunction` was deliberately declined
before the run as a different treatment from the manual's. **Any turbulent VMFL case
this lab grades on `nutkWallFunction` should carry this −4.6 % friction bias as a
known, one-signed, unexplained prior until a case isolates it.**
Source: `cases/ansys_verification/VMFL003/RESULTS.md` §2–§3,
`verification/runs/ansys_verification/VMFL003/GRADING_VMFL003.json`.

## N-AV12. A NORMALISED RESIDUAL IS BLIND TO COHERENT DIVERGENCE: VMFL007's pressure residual sat unremarkably in [0.157, 0.587] for 9 000 iterations while the time-step continuity error reached 3.316e+105 — a convergence clause built only on normalised residuals cannot tell a converged solution from a diverged one

**THE TRANSFERABLE FACT, first, because it bears on every case this lab grades on
residuals.** OpenFOAM normalises a linear-system residual by a factor built from the
current field, so the reported "initial residual" is a statement about the residual
**relative to the current solution scale**. That makes it **scale-invariant**, and
scale-invariance is exactly blindness to **uniform growth of the scale itself**. If a
solution diverges *coherently* — every component inflating together, the field keeping
its shape while its magnitude runs away — the numerator and the denominator grow in step
and **the printed residual does not move**. A convergence clause built ONLY on
normalised residuals therefore **cannot distinguish a converged solution from one that
has diverged by a hundred orders of magnitude**. It is not that the criterion was set too
loose. It is that the quantity it reads does not carry the information.

**THE MEASUREMENT.** VMFL007 run 1, level L2_50x50, `simpleFoam`, 9 065 iterations,
log `verification/runs/ansys_verification/VMFL007/L2_50x50/log.simpleFoam`:

| Channel | Over iterations 66 … 9 064 | Reading |
|---|---|---|
| `Solving for p, Initial residual` | min **0.156521242061**, max **0.587117756129** | flat, unremarkable, never approaches a tolerance |
| `time step continuity errors : sum local` | first > 1e+10 at iteration **777**; first > 1e+100 at iteration **8608**; peak **3.31641662696e+105** | 105 orders of magnitude of divergence |

The two channels are printed **on adjacent lines of the same iteration**. At the final
two iterations the pressure initial residual reads **0.420006388219** and
**0.382828288013** — values a reader would call "chugging along" — while `sum local`
on those same iterations reads **3.25440128362e+105** and **3.02219858509e+105**. The
run then died: `Foam::sigFpe::sigHandler` at log line 81658, core dumped, last
`Time = 9065` of an `endTime` of 10000. **Nine thousand iterations of a flat residual
concealed a divergence of over a hundred orders of magnitude, and this lab's
convergence clause could not see it.**

**3.316e+105 IS THE LARGEST MAGNITUDE ANYWHERE IN THAT LOG.** Established by scanning
every number in all 5 804 059 bytes of it in exponent form and taking the maximum
absolute value, not by grepping a channel that was expected to be large.

**THE CHEAP COMPANION CHECK THAT WOULD HAVE SEEN IT: AN ABSOLUTE BOUND.** A bound on the
solution itself, or on the continuity error, is **not normalised** and therefore is not
blind to the growth of the scale. It costs one comparison per iteration against a number
fixed before the run. Either channel would have fired here at iteration ~777, some
8 288 iterations and one core dump before the run actually stopped. This is exactly what
VMFL007-R2's frozen criterion now carries as **`C-BOUNDED`**
(`cases/ansys_verification/VMFL007_R2/PREREGISTRATION.md`, frozen at `141185ad`): a
residual criterion is paired with an absolute bound, and the pair is the criterion.
**Any case this lab grades on residuals alone inherits this blindness until it carries
an absolute channel beside them.**

**HONESTY NOTE — ONE FIGURE AND ONE MECHANISM ARE NOT CONFIRMED, AND ARE RECORDED AS
UNCONFIRMED RATHER THAN LAUNDERED INTO THIS ENTRY.**
- A lane reported the divergence peak as **6.03e+211**. That figure **could not be
  reproduced**: the string does not occur in the log, and **no value in the e+2xx decade
  occurs anywhere in it**. The peak is recorded here at **3.31641662696e+105**, the
  figure that was verified. 6.03e+211 is **not** carried forward.
- The same lane cited a double-overflow threshold of **1.341e+154** as the SIGFPE
  mechanism. That threshold is arithmetically right for what it describes —
  `sqrt(DBL_MAX)` = **1.340781e+154**, the magnitude beyond which squaring a double
  overflows — but **3.316e+105 is below it**, so **the printed values do not confirm
  that mechanism**. It is recorded as a **CANDIDATE only**. It is not disproven either:
  `sum local` is a summed diagnostic, not the largest field value resident in memory, so
  an unprinted intermediate could still have crossed the threshold. **What is
  established is the SIGFPE and the 105-order divergence; the specific overflowing
  operation is NOT established and must not be quoted as though it were.**

Source: `verification/runs/ansys_verification/VMFL007/L2_50x50/log.simpleFoam`
(lines 81594–81658 for the terminal continuity errors and the `sigFpe` handler);
`cases/ansys_verification/VMFL007_R2/PREREGISTRATION.md` for `C-BOUNDED`.

---

## cfd-team numerics from Ekaterinaris 2005 — appended 2026-08-25 (cfd supervisor, read personally)

**Source, title-page verified by this supervisor rather than relayed** (standing rule 15,
L-144). The file on disk is `docs/standards/High_order_grid_convergence.pdf`, sha256
`dd5b10cacaed3b08a81fc4b283de44da5b1a6d41151b6a7fd514468e279f035a`. Its **filename names a
subject it does not have.** Title page and embedded PDF metadata agree:

> *High-order accurate, low numerical diffusion methods for aerodynamics.*
> John A. Ekaterinaris, FORTH/IACM, Heraklion, Crete.
> **Progress in Aerospace Sciences 41 (2005) 192–300**, Elsevier, `doi:10.1016/j.paerosci.2005.03.003`.

Full provenance, including the count evidence, is at
`docs/standards/High_order_grid_convergence_PROVENANCE.md` (landed `01fcb3d8`). Three
independent title-page verifications now agree: cfd's at `01fcb3d8`, heat-transfer's at
`docs/campaigns/T-family/STANDARDS_INTAKE_RULING_2026-08-25.md`, and this supervisor's own,
re-derived from the PDF and the sidecar in this session.

**THE STANDING PROHIBITION, restated here because this is the file a numerics lane reads.**
Measured over the full 66,033-word text with **word-boundary discriminators**: `Roache` **0**,
`GCI` **0**, `Richardson` **0**, `grid refinement` **0**, `mesh refinement` **0**,
`verification` **0**. **No grid-convergence, GCI, Richardson-extrapolation or verification
lesson may be sourced to this document by any team.** A record of the form *"the
grid-convergence literature says X, per `High_order_grid_convergence.pdf`"* would be a
fabrication. `docs/standards/MESH_STANDARD.md` §9's three-level ruling comes from Sanaa and
from Roache and owes this paper **nothing**.

The naive substring `roache` returns **17** hits. **Every one of them is the substring inside
`app-roache-s`** — re-derived independently in this session, unique contexts inspected. A grep
over a document is not an enumeration instrument unless it carries a discriminator.

**A SECOND DISCRIMINATOR TRAP IN THE SAME FILE, found while verifying the quotes below.**
The `.txt` sidecar carries **Elsevier's typographic ligatures** — `fi`, `fl`, `ff`, `ffi`, `ffl`
are single code points, not letter pairs. Every quotation in the entries below is transcribed
here with those ligatures **normalised to ASCII**, and each was verified against the sidecar
**only after normalisation**. A plain `grep` for `"turbulent flows"` over the sidecar returns
**zero** and the phrase is on the page. **A future reader who cannot find one of these quotes
by grep has not caught this record in an error — they have hit the ligatures.** Normalise
before you search.

---

## N-C2. Second-order numerical diffusion of vorticity is a SCHEME limitation, not a mesh limitation — and it is the standing candidate for this lab's worst Cp row

Ekaterinaris 2005 states the deficiency as its motivating thesis, in the abstract, p. 192:

> *"The main deficiency of widely available, second-order accurate methods for the accurate
> computation of these flows is the numerical diffusion of vorticity to unacceptable levels."*

"These flows" are the vortex-dominated ones the paper names immediately before: *"the vorticity
in the flow field and the wake of swept wings at an incidence and rotor blades largely
determines the distribution of loading."* Term frequencies in the text, word-boundary counted:
`WENO` 160, `shock` 89, `vortex` 62, `limiter` 37, `vorticity` 20, `numerical diffusion` 6,
`tip vortex` 5.

**Where this bites in this lab — and the in-house number is a LEAD, NOT EVIDENCE.** `F1`
(ONERA M6) is a swept wing at incidence, run with OpenFOAM's second-order finite-volume
discretization, and its **η = 0.99 station is the worst Cp row cfd has** — recomputed by a cfd
lane from `cases/dafoam/ladder-a/logs_A3/cp_comparison.json` and recorded at
`verification/campaign/F1_CP_PROVENANCE_2026-08-25.md:25` as **RMS 0.1139, bias +0.0652**.
η = 0.99 is the wingtip-vortex station.

**THAT NUMBER IS ATTACHED TO A CELL THAT NOW READS `NOT A RESULT`, and this entry says so
rather than quoting it as though it were graded.** `verification/campaign/CAMPAIGN_STATUS.md:453`
was moved from `GATE REACHED` to **`NOT A RESULT`** on 2026-08-25, on the ground that *"the
reference values are not held on this box"* — the solve is untouched, the **reference** is what
failed. So 0.1139 is a comparison against a reference this lab cannot show it holds. **It is a
lead for where to look, and it is not admissible as evidence for anything.** What survives
independently of it is the **mechanism**: on a swept wing at incidence, a second-order code's
largest Cp error is *expected* at the tip station, and Ekaterinaris gives that expectation a
named cause that is not the mesh.

**The standing in-house explanation for that station has been mesh-diffusion smearing. This
paper says the same physical error has a scheme component that a second-order code carries at
any mesh density.**

**THE CONSEQUENCE FOR GATING, and it is the part that matters.** A GCI computed at a
vortex-core station measures the **mesh** contribution to an error whose **scheme** contribution
does not refine away at the same rate. A three-level family can therefore be perfectly
`CONVERGING`, print a small GCI, and still sit outside the true error — because the quantity the
triple is converging in is not the whole of the discrepancy against experiment. **This is
`N-T2`'s failure mode arriving by a different route** (*"a CONVERGING Roache triple can arm a
band narrower than the finest level's actual error"*), and it is a reason to state, beside any
tip-vortex or vortex-core row, that its GCI bounds mesh error only.

**WHAT THIS ENTRY DOES NOT DO.** It does not move `F1`'s verdict, does not touch
`CAMPAIGN_STATUS.md`, and does not retire or widen any gate. It records a mechanism and a
caveat. **Whether `VERIFICATION_CHARTER.md` should carry the vortex-core GCI caveat as a
clause is the verification team's ruling, not cfd's** — referred, not decided here.

---

## N-C3. This paper's implicit-scheme and multigrid sections do NOT transfer to `rhoSimpleFoam`'s pressure equation — recorded as a NEGATIVE so the next lane does not re-mine it

cfd has an open convergence problem: F12's admission gate B, where the pressure residual
converges in neither of two runs and floors far above its `1e-06` target. The paper was read
against that problem **because Sanaa's directive of 2026-08-25 says to read it first where a
team has bumped into numerical convergence issues.** The honest result is that **it offers no
relief**, and the reason is structural rather than a matter of not looking hard enough:

- **§2.3.2 "Implicit schemes" (p. 202)** is about **time-marching**: the approximately factored
  Beam–Warming algorithm with Newton-type subiterations to eliminate linearization and
  factorization error, Steger–Warming flux-vector splitting on the right-hand side, and the
  Yoon–Jameson unfactored LU-SGS scheme extended by Zhang and Wang with **dual time-stepping**.
  Every one of these is a **density-based, method-of-lines** construction for high-order finite
  differences and finite volumes on the compressible Euler/NS equations.
- **§2.3.3 "Time accurate solutions with multigrid" (p. 202)** introduces a **pseudo-time**
  variable and drives Eq. (2.14) to steady state with **a multistage Runge–Kutta method that
  performs the role of the smoother in the multigrid process.** That is **FAS multigrid on the
  nonlinear residual of a dual-time formulation.**

`rhoSimpleFoam` is a **pressure-based segregated SIMPLE** solver, and OpenFOAM's `GAMG` is
**algebraic** multigrid applied to the **linear** pressure system. **Different object, different
equation, different failure modes.** Neither section names a pressure-correction equation, a
SIMPLE-family algorithm, or an algebraic multigrid; `preconditioning` appears **once** in
66,033 words, `GMRES` **three** times, `line relaxation` and `ADI` **zero** times.

**THE ONE CLAIM THAT DOES TRANSFER, stated narrowly because it is narrow.** Of the high-order
compact implicit LHS operator, §2.3.2 reports that

> *"it yields accurate solutions of time dependent problems with fewer subiterations and
> converges faster to the steady state [90]."*

The transferable content is the **attribution**: steady-state convergence *rate* is a property
of the **implicit operator and its linearization**, not only of the mesh or of the tolerance
asked for. In OpenFOAM terms that points at relaxation and the corrector structure before it
points at the mesh. **That is consistent with what cfd's own gate-B probe already measured** —
`verification/campaign/F12_GATE_B_RULING_2026-08-25.md` — where the mechanism was shown to fire
(a 400-cell arm printed `SIMPLE solution converged in 14 iterations`) and the apparent floor was
traced to a first-solve versus last-solve reading of the log, not to an unsatisfiable gate.

**So: gate B gets NO relief from this paper, and this entry exists to stop the next lane
spending an hour discovering that.** A negative result about a source is still a result about
the source.

---

## N-C4. Raising scheme order to cure a diffusion problem buys an instability unless a filter or limiter comes with it

§3, opening paragraph, p. 203:

> *"For nonlinear problems, straightforward application of high-order accurate central
> difference schemes is not possible, because the spurious modes that develop from the
> unresolvable by the numerical discretization high-frequency modes lead to instabilities."*

and immediately after:

> *"Rai and Moin [96] found that high-order upwind schemes are more promising to simulate
> turbulent flows. However, early attempts to apply high-order finite differences were often
> frustrated because of lack of robustness of the proposed high-order (FD) schemes compared to
> spectral methods."*

The paper's entire apparatus of **spectral-type filters (§3.5)**, **characteristic-based ACM
filters (§3.6)**, **ENO/WENO ACM filters (§3.6.1)** and **DG limiting (§5.6, §5.7)** exists to
pay for the order it buys. `limiter` occurs **37** times.

**Where this bites in this lab.** N-C2 gives cfd a standing motive to reach for a
higher-order convection scheme at vortex-dominated stations. **This entry is the price tag.**
Two in-house data points sit squarely in this territory and neither is a counterexample:
`DPW8_V2`'s L4 arm B was a `linearUpwind`→`upwind` swap, i.e. a move *down* in order taken for
boundedness, and its bounded-ness legs still failed
(`verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md`); F12's rung-1 crash was **not**
an FPE but **OpenFOAM's own negative-temperature range check** firing — an unboundedness, which
is the symptom class this section describes (`ed050ff1`, F12 crash triage AMENDMENT 1, in which
this supervisor struck his own earlier mechanism).

**Operational reading for cfd lanes.** A scheme-order change is a **change of experiment**, not
a tuning knob. Under standing rule 2 it cannot be made inside a fired pre-registration at all.
Where one is registered before compute, it is registered **together with the boundedness
apparatus that pays for it**, and the pre-registration says which one — not as a lever to be
swapped when the first arm misbehaves.

---

---

## N-AV9 COMPANION — the wedge CENTROID bias. **Found by the heat-transfer T8 lane; confirmed independently here and swept across the ansys-verification wedge corpus, 2026-08-25.**

**Finder credit: the heat-transfer team's T8 lane.** This is recorded **beside N-AV9, not as
a new family** — N-AV9 is the wedge *area* bias, this is the wedge *centroid* bias, and they
are the same defect family: **two geometric biases of the wedge that grid refinement does not
remove, because each is a property of the cell SHAPE, not its size.**

### The fact

**OpenFOAM's cell centre is the VOLUME CENTROID, not the arithmetic mid-radius.** For a
wedge/annular-sector cell spanning `[r1, r2]`:

    r_centroid = (2/3) * (r2^3 - r1^3) / (r2^2 - r1^2)

**Confirmed independently by this team** against the T8 lane's measured mesh values:

| cell | this team's formula | T8's measurement |
|---|---|---|
| axis-adjacent `[0, dr]` | **(2/3)·dr** exactly | 0.016651 vs predicted 0.016667 |
| next out `[dr, 2dr]` | **(14/9)·dr** exactly | 0.038852 vs predicted 0.038889 |
| **ratio** | **exactly 7/3** | — |

**Mid-radius arithmetic predicts a ratio of 3. The true ratio is 7/3.** Any axis
extrapolation whose precondition is `r2 = 3*r1` is therefore false on every wedge mesh
OpenFOAM builds; the correct axis extrapolation is `(49*f1 - 9*f2)/40`, not `(9*f1 - f2)/8`.

### Why it survived a green instrument — the part worth learning

**T8's comparator passed 69 selftest checks and both negative arms, and none could have caught
this**, because **the synthetic fixture placed cell centres at `(j+1/2)dr`, making the
comparator's precondition true by construction.** Fixture and instrument agreed because they
shared one wrong assumption. **That is L-321 at the mesh level.** The rule it yields:

> **A geometric quantity must be READ BACK from the mesh OpenFOAM actually wrote — never
> constructed in the fixture from the same spec the instrument assumes.** A selftest that
> builds the geometry it is testing is checking arithmetic, not geometry.

### THE SWEEP OF THIS TEAM'S WEDGE CORPUS — done by the supervisor personally

15 ansys-verification cases reference `wedge`; 21 comparators exist. **Result: exactly one
exposure, and it is a diagnostic, not a gate. No verdict changes.**

**NOT EXPOSED — and for a reason worth copying:**
- **VMFL036** (live at the time of the sweep) — carries N-AV9 explicitly, and **reads its
  wedge areas back off the mesh** via `polymesh_area.py` (points and faces, to 1 part in 1e8),
  checks the axis patch has **zero** area, and verifies the mesh half-angle from the actual
  point coordinates. Its `Cd` is a **face-based surface integral over the sphere patch** — it
  never reads an axis-adjacent cell value and never extrapolates to the axis.
- **VMFL021 / VMFL022** (live at the time of the sweep) — the gate is a **ratio of two mass
  flows on the same wedge slice**, with `A_out = 0.5*r2^2*sin(theta)` computed exactly from
  geometry. **The wedge-slice factor cancels in the ratio** and no cell-centre radius enters.
- **VMFL005, VMFL051** — patch/volume integrals via `surfaceFieldValue` / `volFieldValue`;
  no constructed radii.

**EXPOSED — VMFL003, `grade_vmfl003.py`:**

    YPLUS_PRED = 40.835033970764385   # first cell centre, NR = 5, uniform
    :780  ck(abs(YPLUS_PRED - (R_PIPE / 5 / 2) * U_TAU / NU) < 1e-9, "y+ at NR=5")

**`R_PIPE/5/2` is mid-radius arithmetic, and the selftest asserts the constant equals its own
construction — the exact T8 pattern, fixture and instrument sharing one wrong assumption.**

Measured correction for that mesh (R = 0.002 m, NR = 5 uniform, wall cell `[1.6e-3, 2.0e-3]`):

| | value |
|---|---|
| assumed wall distance (mid-radius) | 2.000000e-4 m |
| **true volume-centroid wall distance** | **1.925926e-4 m** |
| ratio true/assumed | **26/27 = 0.9629630** |
| frozen `YPLUS_PRED` | 40.835034 |
| **true y+** | **39.322625** |
| **error** | **3.7037 % HIGH** |

**IMPACT: NONE ON THE VERDICT.** `YPLUS_PRED` is a **predicted diagnostic**, printed beside
the measured value; the gate applies the frozen one-way band `[25, 65]` to the **measured**
`yPlus`, which OpenFOAM computes from the true centroid. **Both 40.835 and 39.323 sit inside
that band**, so VMFL003's recorded verdict is unaffected and is **not** reopened. The constant
is wrong by 3.7 % and **its selftest can never detect that**, which is the finding.

**Standing instruction for this team, effective now:** any comparator that reads an
axis-adjacent value, extrapolates to the axis, or needs a cell-centre radius **reads it back
from OpenFOAM's own `C` field or from the written mesh geometry — never constructs it from
`nr`, `dr`, or `(j+1/2)`.** Where a fixture must supply geometry, the fixture reads the same
written mesh; it does not build one.
