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

## Open innovation directions (Numericist backlog)

- GCI-based discretization-error channel alongside the GP epistemic layer.
- Acquisition-driven sampling: spend the next cycle's budget where posterior
  spread is largest (the mission layer already flags thin directions).
- Closure-model registry with validity envelopes (feeds the Chief Researcher
  approval protocol in demo Part 2).
- Unsteady metrics: time-averaged coefficients + shedding amplitude/Strouhal
  as first-class mission metrics.
