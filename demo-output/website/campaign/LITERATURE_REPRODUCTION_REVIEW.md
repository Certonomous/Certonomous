# Literature review for reproduction — four hard cases

Date: 2026-07-29 (UTC). No-compute task: read, search, write. No solver launched to produce
this document. Scope set by the standing brief: the NASA wall-mounted hump, eigenvalue/anisotropy
perturbation UQ corner convergence, discrete-adjoint conditioning for transonic shock flows, and
the cylinder Reynolds ladder above Re 3900.

**Purpose.** Not a summary of what these papers found. A test of whether we could rebuild their
number from what they actually published, for the specific cases this lab runs. Where a paper
withholds a quantity needed to reproduce it, that omission is recorded as the finding, not
smoothed over.

**Provenance discipline applied throughout.** Every citation below was either (a) fetched and
read directly this session — full text, not an abstract — or (b) marked **PAYWALLED /
abstract-only**, meaning only the publicly visible abstract or a search-result excerpt was seen,
and no claim beyond what that abstract literally states is asserted. A third category, **internal,
already read**, applies to one paper (Jiang & Cheng 2017) that a prior session in this lab fetched
and read in full, with detailed tables already reproduced in `F5a_cylinder_reynolds_ladder.md`;
that reading is reused here with attribution rather than re-done. Nothing below is inferred from a
title or a citation count.

---

## 1. The NASA wall-mounted hump

### What we have, restated

Our own converged `kOmegaSST` baseline (`F6a_nasa_hump.md`, 51,626-cell 2D mesh, `simpleFoam`
SIMPLEC, `residualControl` U/p/k 5e-7, omega 1e-10, converged in 1772 iterations): separation
`x/c=0.6544` (experiment 0.665, −1.6%), reattachment `x/c=1.2534` (experiment 1.100, +13.9%).
This matches NASA's own published SST result almost exactly (their SST: separation 0.654,
reattachment 1.25–1.27) — confirming our setup, not our physics.

### Sources read

**Cappelli, D. & Mansour, N.N., "Performance of Reynolds Averaged Navier-Stokes Models in
Predicting Separated Flows: Study of the Hump Flow Model Problem," NASA Ames Research
Center / ENSAE, AIAA paper, filed via NASA NTRS as 20130001741 (2013).** Full text read (26
pages, fetched via `ntrs.nasa.gov/api/citations/20130001741/downloads/20130001741.pdf`).

Runs OpenFOAM 2.1.1 `simpleFoam` with four RANS models (Spalart-Allmaras, k-ε, k-ω, k-ω-SST) on
the same baseline hump case our own F6a targets — the closest methodological cousin to our own
run in this whole review.

- **Mesh**: SA 336,000 cells (300 y-cells), k-ε 224,000 cells (200 y-cells), k-ω 336,000
  cells (500 y-cells), k-ω-SST 336,000 cells (500 y-cells). 2D (`empty` z-patch), near-wall
  grading factor 100–500× (cells near the lower wall 100–500× smaller than in the freestream).
- **Domain**: two inlet locations tested, `x/c=-6` and `x/c=-1`, explicitly to probe sensitivity;
  found to matter substantially for downstream recovery-region velocity profiles even though the
  underlying experiment (Greenblatt et al. 2004) is reported insensitive to inlet Re/Mach.
- **Boundary conditions**: two upper-wall treatments tested and compared — symmetry plane vs.
  viscous no-slip wall — found to change Cp prediction quality (viscous wall improves the SST
  match specifically). Inlet `k` and `epsilon`/`omega` are **not measured**, but estimated from
  an assumed 1.5% turbulence intensity and an assumed `nu_t/nu` ratio of 10–100 — a disclosed,
  non-measured input.
- **Convergence criterion: never stated.** Table 3 gives iteration counts (8,000–30,000
  depending on model) and wall-clock time, but no residual tolerance is reported anywhere in the
  paper, for any of the four models. This is the single largest reproducibility gap in an
  otherwise careful, disclosure-heavy paper — the same failure mode this lab's own D9/L-14/L-15
  register catalogued this week (iterations printed is not evidence of convergence reached).
- **Results (their Table 6)**: SA sep 0.667 / reattach 1.198; k-ε sep 0.669 / reattach **1.104**;
  k-ω sep 0.656 / reattach 1.196; k-ω-SST sep 0.656 / reattach 1.229; experiment sep 0.65–0.67 /
  reattach 1.11.
- **Why k-ε looks best, and why that is not good news for reproducibility**: the paper's own
  conclusion states plainly that k-ε's near-exact reattachment match is attributed to its
  *coarser* mesh (224,000 vs. 336,000 cells) producing more numerical viscosity, which happens
  to compensate for the shared linear-eddy-viscosity turbulent-shear-stress deficit: *"results
  obtained using a coarse mesh are closer to experimental data than those obtained with a fine
  mesh; this is a clear indication that the eddy viscosity is under-predicted by the models... the
  numerical viscosity of a coarse mesh causes an increase in mixing, so that the results are
  closer to the experiments, for the wrong reason."* Reproducing this paper's headline k-ε number
  requires reproducing its specific mesh error, not avoiding it — a genuine trap for anyone citing
  "k-ε gets the hump right" without also citing the mesh at which that happened.
- **Mechanism for the over-prediction, attributed to Rumsey's 2004/2008 NASA workshop findings and
  independently confirmed by this paper's own turbulent-shear-stress plot (their Fig. 29,
  Boussinesq-estimated `-u'v'` at x/c=0.8)**: all four models under-predict the magnitude of
  turbulent shear stress in the separated shear layer relative to experiment. This is stated as
  the community-accepted mechanism, not this paper's own discovery.

**Uzun, A. & Malik, M.R., "Wall-Resolved Large-Eddy Simulation of Flow Separation Over NASA
Wall-Mounted Hump," AIAA SciTech 2017 (AIAA 2017-0538), NASA NTRS 20170000736; expanded as
"Large-Eddy Simulation of Flow over a Wall-Mounted Hump with Separation and Reattachment," AIAA
Journal (2017/2018).** Full text of the conference version read (22 pages, fetched via
`ntrs.nasa.gov/api/citations/20170000736/downloads/20170000736.pdf`). This is the best-resolved
simulation of this case in the literature, and the only one found in this review that reproduces
the experiment without any turbulence-model correction.

- **Grid**: narrow-span (0.2c) case: ~210 million points on the hump domain + ~90 million points
  on an auxiliary flat-plate domain used only to generate turbulent inflow; wide-span (0.4c) case:
  ~420 million points, refined to ~850 million points (2–3× wall-normal refinement) in a follow-up
  study. Both cases resolve `Δx+≈25`, `Δz+≈12.5`, `Δy+≈0.8–1` out to `y+≈200`, coarsened 2× beyond.
- **Numerics**: 4th-order compact finite-difference scheme, 6th-order compact filtering for
  stability, overset grids with 6th-order Lagrangian interpolation, 2nd-order implicit
  (Beam-Warming) time advancement, static Vreman subgrid-scale model (coefficient 0.025); one
  wide-span variant re-run as implicit LES (no explicit SGS model) and found to do slightly
  better on peak Cf.
- **Domain**: hump leading edge at `x/c=0`, inlet `x/c=-2.14` (matching the experimental
  measurement station), region of interest to `x/c=1.6`, sponge zone to outflow at `x/c=4`. Top
  wall: **inviscid**, specially contoured to mimic the experimental end-plate blockage effect (a
  third distinct upper-boundary treatment, matching neither of Cappelli & Mansour's two).
- **A disclosed input-data ambiguity in the original experiment itself**: the experiment's
  reported inflow momentum-thickness Reynolds number (`Re_θ=7200` at `x/c=-2.14`) does not match
  *any* canonical flat-plate DNS/LES profile examined (5000 ≤ Re_θ ≤ 7000) when checked against
  the measured inflow skin friction; the authors conclude the experimental upstream boundary
  layer "is perhaps not precisely a flat-plate turbulent boundary layer" and proceed with
  `Re_θ=5000` (friction-matched) as a disclosed, unresolved choice — this is an omission in the
  *original experimental record*, not in this paper, but it caps how exactly *any* reproduction
  of this case, ours included, can match the true inflow.
- **A genuine numerical trap found and fixed**: the standard rescaling-recycling turbulent-inflow
  technique failed here specifically because acoustic disturbances reflect between the tunnel's
  top and bottom walls and become a trapped, self-reinforcing resonance that corrupts the
  synthetic inflow — fixed either by an auxiliary flat-plate simulation (narrow-span) or a
  damping/sponge term (wide-span, cheaper).
- **Averaging window disclosed and shown to matter**: narrow-span averaged over ~10 chord
  flow-through times; wide-span over ~30 — three times longer — and even so, the wide-span
  Reynolds-stress levels differ substantially from the narrow-span case despite near-identical
  reattachment location, which the authors call "puzzling" and leave unresolved.
- **Results**: narrow-span (0.2c) separation `x/c≈0.659` (exp. 0.665), **reattachment
  `x/c≈1.095` (exp. 1.11)** — within 1.5% of experiment, without any turbulence model. Wide-span
  (0.4c) at original resolution reattaches earlier than expected; refined-grid wide-span
  reattachment `x/c≈1.091`, close to the narrow-span value but the authors state "another level
  of [refinement] may be necessary," i.e., not fully grid-converged even at 850 million points.
- **A disclosed, uncorrected confound**: for cost reasons the wide-span case was run at
  `M=0.2` instead of the matched `M=0.1`, and the authors explicitly flag (citing a related
  backward-facing-step study, Li et al.) that higher Mach number is independently known to cause
  earlier reattachment via faster shear-layer bending — meaning part of the apparent
  span-sensitivity result may be an uncontrolled Mach-number confound, not a pure span effect.
  This is exactly the kind of undisclosed-variable risk a reproduction checklist should flag for.
- **A genuine physical effect both RANS and prior wall-modeled LES miss**: a relaminarization
  plateau in skin friction at `x/c≈0.1–0.2`, driven by the strong favorable pressure gradient
  over the front of the hump (acceleration parameter K peaks at ≈4.87×10⁻⁶, above the accepted
  critical threshold ≈3×10⁻⁶). This occurs upstream of separation and does not itself explain the
  reattachment over-prediction, but it demonstrates that even a well-resolved near-wall treatment
  is required to get the *upstream* boundary layer right before the separated-flow prediction can
  be trusted at all.
- **Prior best-resolved attempts, cited by this paper and not independently re-verified here**:
  Postl & Fasel's "coarse-grid" DNS (210 million points, span 0.142c) found the bubble length
  *larger* than experiment despite reasonable overall agreement — span truncation biases toward
  over-long bubbles even at DNS resolution. Yeh et al.'s WRLES (half the experimental Reynolds
  number, span 0.2c, 93 million points) found the bubble ~20% longer than experiment.

**NASA Turbulence Modeling Resource** (relocated 2026-02-24 from `turbmodels.larc.nasa.gov` to
`tmbwg.github.io/turbmodels/`), the site this lab's own F6a record already used and cites for its
SST comparison numbers (separation 0.654, reattachment 1.25–1.27 vs. experiment 0.665/1.100).
Treated here as already-verified per that record, not re-fetched independently this session
beyond confirming the domain relocation.

### Community consensus on the mechanism

Both independently-read sources, and the community record they both cite (Rumsey et al., 2004/2008
NASA CFD Validation Workshop papers), agree: linear eddy-viscosity RANS models under-predict
turbulent shear stress in the separating/reattaching shear layer, which lets the shear layer
persist too long before reattaching. No dissenting mechanism was found in either paper read. The
only approach found in this review that reproduces the experiment without a model-form correction
is wall-resolved LES at extreme cost (Uzun & Malik) — which is precisely why data-driven
closure-correction benchmarks (the one this lab already scores against) exist for this case.

### Reproduction checklist — NASA hump

| Item | Cappelli & Mansour (2013) | Uzun & Malik (2017/2018) | Our own F6a |
|---|---|---|---|
| Mesh count/topology, stated | Yes (224k–336k, 2D) | Yes (210M–850M, 3D) | Yes (51,626, 2D) |
| Near-wall resolution (y+ etc.) | Partial — grading ratio only, no y+ | Yes, explicit (y+≈0.8–1, x+≈25, z+≈12.5) | Not separately re-derived this session |
| Turbulence model AND variant | Model named, variant/blending unstated | N/A (LES, SGS model+coefficient stated) | Stock OpenFOAM kOmegaSST; separately confirmed inert vs. benchmark's custom library |
| Discretization schemes | Not stated (implied default) | Stated explicitly (4th-order compact + filter) | Inherited from benchmark's shipped `fvSchemes`, not independently re-audited here |
| Convergence criterion, and whether met | **Never stated — a fatal gap** | N/A for RANS; averaging window given instead (10 / 30 flow-times), shown to matter | Stated and met (`5e-7`/`1e-10`, 1772 iters) |
| Domain extent | Stated, two variants compared | Stated, matches to `x/c=-2.14` | Inherited from benchmark |
| Boundary conditions | Stated, two upper-wall variants compared | Stated, third distinct upper-wall treatment | Inherited from benchmark, not independently re-verified |
| What was averaged, over what window | N/A (steady) | Stated and shown to matter (10 vs. 30 flow-times insufficient to converge Reynolds stresses) | N/A (steady) |

### Ranked reproducibility

1. **Reproducible now, already done.** Cappelli & Mansour's k-ω-SST result — our own F6a matches
   NASA TMR's own SST number to 0.06%/within range, and lands in the same neighborhood as this
   paper's k-ω-SST (reattach 1.229 vs. our 1.2534). No further work needed.
2. **Not reproducible with what we have — cost, not omission.** Uzun & Malik's WRLES. The paper
   discloses everything needed; the blocker is that 210–850 million cells and a 4th-order compact
   scheme are roughly 4,000–16,500× our own hump mesh and a numerical method OpenFOAM does not
   implement. This is a capability gap on our side, not a paper defect.
3. **Reproducible only by reproducing the paper's own error.** Cappelli & Mansour's k-ε
   near-exact reattachment. The paper's own text says this number is mesh-error-dependent; citing
   "k-ε solves the hump" without also citing the specific under-resolved mesh at which that
   happened would misattribute a numerical accident to a modeling success.

---

## 2. Eigenvalue/anisotropy perturbation UQ — corner convergence

### What we found tonight

On the hump, the extremal corner states (`Delta→1`) do not converge: the flow fragments into
multiple separation/reattachment events and the SIMPLE iteration has no single fixed point to
find. Only `Delta=0.00` (baseline) and `Delta=0.05` genuinely converge; every tested point from
`Delta=0.10` through `0.75` fails its own residual gate, with severity tracking `Delta` almost
monotonically (`F6a_epistemic_band.md`).

### Sources read

**Framework origin — cited via the paper below, not independently re-fetched this session**:
Emory, M., Larsson, J. & Iaccarino, G., "Modeling of structural uncertainties in
Reynolds-averaged Navier-Stokes closures," *Physics of Fluids* 25(11):110822 (2013). This is the
paper that defines the eigenvalue-perturbation-toward-1C/2C/3C-corners method our own hump
channel 3 implements. **PAYWALLED — AIP Publishing.** Everything below about its content is
relayed through Heyse, Mishra & Iaccarino (2021), which describes and cites the framework
directly; this is flagged explicitly rather than presented as an independent reading of Emory et
al. itself.

**Heyse, J.F., Mishra, A.A. & Iaccarino, G., "Estimating RANS model uncertainty using machine
learning," Journal of the Global Power and Propulsion Society, Special Issue: Data-Driven
Modelling and High-Fidelity Simulations, pp. 1–14 (2021), DOI 10.33737/jgpps/134643.** Full text
read (14 pages, open access CC-BY 4.0, fetched via `journal.gpps.global`).

- Applies the **full-magnitude, data-free** corner perturbation (`Delta_B=1.0`, the true 1C/2C/3C
  corners, exactly our own method) on a planar asymmetric diffuser (Obi et al. 1993 / Buice &
  Eaton 1995, 2000 geometry: 10° expansion slope, channel width H → 4.7H, `Re=17,800` on inflow
  height, k-ε, OpenFOAM, 9,472-cell baseline mesh) and on a periodic wavy-wall channel (16,384
  cells, used only as training data for a later data-driven variant).
- **The full corners DO converge on this geometry**, at all three limiting states, to steady
  RANS. But not for free: quoted directly — *"the perturbations had an effect on the convergence
  of the solver, resulting in more iterations that had to be completed. While the data-driven
  perturbations took roughly the same amount of time for every case, the convergence difficulties
  were dependent on the particular limiting state."* Runtime for perturbed cases rose 2–3× over
  baseline. Which corner is hardest is case-dependent — the same asymmetry our own 1C/2C corners
  show on the hump.
- The data-driven (locally-moderated) variant introduced in this paper exists for an *accuracy*
  reason independent of convergence — full-domain `Delta_B=1.0` is explicitly called overly
  conservative ("targeting all possible extreme states of turbulence anisotropy without
  consideration of their plausibility") — but the convergence-cost finding above is separate and
  applies even to the full data-free method that did converge here.
- **This paper's geometry is a mild, gradual expansion-driven separation, not a sharp
  short-chord bubble like the hump.** No case in this paper is as aggressive as ours, and the
  paper does not report a failure to converge at all — a genuinely different outcome from ours on
  a genuinely different flow. This is an important, disclosed limit on how far this comparison
  can be pushed: it does not establish that full corners always converge, only that they did on
  this one, milder case.

**Matha, M. & Morsbach, C., "Improved self-consistency of the Reynolds stress tensor eigenspace
perturbation for Uncertainty Quantification," arXiv:2303.06149 (2023), German Aerospace Center
(DLR); also Physics of Fluids 35(6):065130.** Partial full text read (Introduction and framework
sections, fetched from arXiv PDF).

- **Direct quote, confirming the field-standard fix for hard convergence cases**: *"we focus on
  the motivation, implementation and effects of applying a moderation factor f, which serves to
  mitigate the amount of perturbation and aid numerical convergence of CFD solution [refs 22,23]
  (in some publications f is called under-relaxation factor)."* This paper's own citations 22/23
  for the origin of this practice were **not independently retrieved** this session — the claim
  is Matha & Morsbach's own characterization of prior, cited work, relayed here as such.
- This establishes, from an independent research group (DLR, not Stanford/the Emory lineage),
  that full-magnitude corner perturbations causing convergence failure in production CFD solvers
  is a **known, named problem** serious enough to have its own standard mitigation with its own
  name.
- The paper's own contribution is a *further* finding: naively combining eigenvector perturbation
  with a moderation factor `f` (applied only to eigenvalues) can produce a moderated Reynolds
  stress that is not linearly interpolated between baseline and the true corner — an internal
  inconsistency in at least one production implementation (DLR's TRACE solver). Practically: a
  published "moderated" UQ band at some `f<1` may not represent a well-defined fraction of the
  true corner uncertainty at all, on top of not representing the true corner itself.

### What this settles, and what it does not

The literature does document non-convergence of extremal eigenvalue-perturbation corners as a
known, named hazard — **settling the first half of tonight's open question**. The established
practitioner response is **not** to switch to unsteady/URANS solving (no source found in this
review reports doing that for the corners specifically); it is to weaken the perturbation
(the "moderation factor" / "under-relaxation factor") until a steady solution is achievable,
trading coverage of the true `Delta=1` corner for a number that will converge. **What is not
settled**: whether this generalizes to a case as short and aggressive as the hump. Every source
read here applies the method to gentler, longer separations (an asymmetric diffuser, a wavy
wall) that converge even at full strength. Our own finding — fragmentation starting as early as
`Delta=0.10` — may be a property of how thin and violent the hump's baseline bubble already is,
not evidence the method itself is broken. That distinction is not resolvable from the literature
found this session; it would require either finding a paper that applies eigenvalue perturbation
to a short-bubble separation like the hump specifically, or treating our own result as a new data
point for that open question.

### Reproduction checklist — eigenvalue perturbation UQ

| Item | Emory framework (as described by Heyse et al.) | Our own channel 3 |
|---|---|---|
| Perturbation magnitude actually achieved (`Delta_B` or moderation `f`) | Full `Delta_B=1.0` (data-free variant) | Swept `Delta=0–0.75`; only 0.00/0.05 converge |
| Steady or unsteady solver | Steady RANS throughout | Steady RANS (SIMPLE) throughout |
| Convergence criterion checked **per perturbed run**, not just baseline | Implicit — paper reports it converged, does not give the residual gate | Explicit, checked per point (`SIMPLE solution converged` string + per-field Initial residual vs. gate) |
| Corner-dependent convergence cost disclosed | Yes ("convergence difficulties were dependent on the particular limiting state") | Yes (1C/2C/3C differ; asymmetry documented) |
| Base-flow aggressiveness (mild diffuser vs. short bluff-body separation) stated as a variable | Not framed as a variable at all | Newly identified by us as the likely governing factor |

### Ranked reproducibility

1. **Reproducible now.** The field's own convergence-difficulty finding on a mild geometry
   (Heyse et al.'s diffuser) — consistent with, and now corroborated by, our own harder result on
   the hump.
2. **Not reproducible, and not attempted by anyone found in this review.** A full `Delta=1` corner
   on a short, sharp separation bubble like the hump. No paper read here runs this specific
   combination; our own record is, as far as this review can tell, the closest existing evidence
   on that exact question, not a reproduction of someone else's number.

---

## 3. Discrete adjoint conditioning for transonic, shock-containing flows

### What we found tonight

Our compressible transonic adjoint (`A3`, ONERA M6, M≈0.84) hits `PetscConvergedReason=-5`
(`DIVERGED_BREAKDOWN`) or OOM at every mesh size tested from 24,960 to 399,360 cells, while an
incompressible case (`naca0015_sail_coarse`) converges cleanly at 63,920 cells.

### Sources read

**Giles, M.B. & Pierce, N.A., "Analytic adjoint solutions for the quasi-one-dimensional Euler
equations," Journal of Fluid Mechanics 426:327–345 (2001).** Full text (intro + problem
formulation) read, fetched from the author's own Oxford page.

- Directly quoted from the abstract: *"For shocked flow, the derivation of the adjoint problem
  reveals that the adjoint variables are continuous with zero gradient at the shock, and that an
  internal adjoint boundary condition is required at the shock... This analysis reveals a
  logarithmic singularity at the sonic throat and confirms the expected properties at the
  shock."*
- **Our own reading of the implication, stated as inference, not the paper's own claim**: the
  true continuous adjoint is well-behaved *at* the shock itself; the analytically hard point is
  the *sonic* point, not the shock discontinuity. This paper is 1D and continuous-adjoint theory,
  not a 3D discrete-adjoint solver study — it establishes that transonic adjoint problems have a
  genuine, classical, well-documented mathematical singularity (at the sonic point), but it does
  not itself explain or predict a discrete linear-solver breakdown like ours; it names the
  underlying reason a transonic case is analytically harder than a fully subsonic one, without
  claiming that translates into a numerical-solver failure at any particular mesh size.

**Kenway, G.K.W., Mader, C.A., He, P. & Martins, J.R.R.A., "Effective Adjoint Approaches for
Computational Fluid Dynamics," Progress in Aerospace Sciences (2019, in press at time of
preprint), MDO Lab, University of Michigan.** Full text read (42 pages, preprint fetched from
`websites.umich.edu/~mdolaboratory`). **This is the single most load-bearing source in this
entire review**: written by the research group that develops ADflow and co-develops DAFoam — the
exact tool our own adjoint blocker is in.

- **General statement on 3D viscous adjoint conditioning (not shock-specific)**: *"the state
  Jacobian matrix that results from a 3D viscous turbulent flow solution is typically
  ill-conditioned, especially for realistic geometries with complex flow... therefore we need a
  strong preconditioner to improve the eigenvalue clustering."* This is presented as a routine,
  well-understood cost of any realistic 3D adjoint, solved by standard preconditioning — **not**
  singled out as a shock-specific hard case anywhere in this paper.
- **Standard preconditioning stack used by this same lab**: PETSc GMRES (Krylov) top-level
  solver; Additive Schwarz Method (1–2 levels of overlap) as global preconditioner; incomplete LU
  (ILU) factorization as local/sub-block preconditioner — **exactly the `PCASM`+`PCILU` stack our
  own A3 investigation found hardcoded in DAFoam's `DALinearEqn.C`**, confirming it is the
  standard, not an unusual, choice. This paper adds one lever our own investigation did not find
  exposed in DAFoam's `daOptions`: multiple **nested Richardson iterations**, both inside each
  ILU sub-block and around the outer ASM step, used specifically to allow a *lower* ILU fill
  level (1–2) while still converging, at much lower memory cost than raising the fill level. Quoted:
  *"the improvement in convergence rate outweighs the extra computational cost of Richardson
  iterations."*
- **On a real, shock-containing, comparable-Mach-number transonic wing (CRM, M=0.85, close to
  our A3's M≈0.84, 3,604,480 cells — about 9× our A3 fine mesh)**: ADflow's best (Jacobian-free)
  adjoint costs **87.2 GB peak, only 2.0× the flow solve's 44.6 GB**, and matches a complex-step
  reference to 11–13 significant digits. On the wing-body-tail configuration (10,358,373 cells,
  about 26× our A3 fine mesh), adjoint peak memory is 252.9 GB, again 2.0× the flow solve, and
  *"adjoint computation is faster than flow."* **This is direct, quantitative, literature evidence
  that a real transonic shock-containing adjoint does not inherently break down** — it converges
  cleanly, affordably, and at far larger mesh sizes than the one that breaks our own tool.
- **A direct, quantified, independent explanation for why DAFoam specifically is far more
  expensive than this**: *"DAFoam uses unstructured meshes and a heuristic coloring scheme with
  945 colors [vs. ADflow's structured-mesh analytical coloring at 162 colors], which results in
  an almost fivefold increase in computational cost for computing the preconditioner. Moreover,
  DAFoam uses a complex object-oriented code structure such that a single residual call could
  involve tens of subroutine levels and numerous intermediate variables. The residual stencil for
  the SIMPLE solver with Rhie–Chow interpolation is also much denser than that in ADflow. These
  two factors result in a large tape size and higher memory cost when performing reverse-mode
  AD."* Their own head-to-head benchmark (Table 10): DAFoam's own **best** ("Jacobian free",
  operator-overloading AD) mode costs **820% more peak memory and is 460% slower** than ADflow's
  best (Jacobian-free, source-code-transformation) mode on comparable problems — a gap the
  authors attribute entirely to code architecture, not to physics or Mach number. Our own A3 case
  uses DAFoam's compressible-solver `DAJacCon`-based explicit-coloring path, which sits closer
  to the even-more-expensive "AD Jacobian" variant in this paper's own taxonomy.

### What this settles

The claim "transonic/shock adjoints are a known hard case that breaks down" is **not supported**
by the literature found here as a blanket statement. What is well-documented and general (not
shock-specific) is that 3D viscous adjoints are routinely ill-conditioned and need strong
preconditioning — a solved, standard engineering problem, not a research frontier. The same
research group that builds DAFoam independently, quantitatively documents that DAFoam's specific
implementation costs 8–9× more memory than an efficient reference implementation on equivalent
problems, for architecture reasons (unstructured heuristic coloring, deep object-oriented call
stack, dense Rhie–Chow stencil) that have nothing to do with whether the flow has a shock. This
gives a strong, literature-supported, alternative explanation for our A3/A6 memory wall that does
not require invoking shocks at all. Our `DIVERGED_BREAKDOWN` finding is a separate, real
linear-solver-conditioning failure, consistent with Kenway et al.'s general statement that 3D
viscous Jacobians need strong preconditioning — but we have not yet tried the specific,
literature-precedented nested-Richardson lever their own team uses.

### Reproduction checklist — adjoint conditioning

| Item | Kenway et al. (2019), ADflow/DAFoam benchmark | Our own A3/ADJOINT_MEMORY_ENVELOPE |
|---|---|---|
| Mesh count AND topology (structured/overset vs. unstructured) | Stated, and shown to be a first-order cost driver (162 vs. 945 colors) | Stated (24,960–399,360 cells, unstructured) |
| Preconditioner family and ALL levels (global, local, Richardson wrapping) | Stated fully: ASM+ILU+nested Richardson | ASM+ILU only; Richardson-sweep lever not exposed/tried |
| Jacobian-free vs. explicit-Jacobian, and which AD mode | Stated explicitly, shown to be an 8–9× memory driver | DAJacCon explicit-coloring path (closer to the expensive variant) |
| Convergence criterion for the LINEAR solve specifically, and the actual solver return code | Reported to complex-step-verified digit counts | `PetscConvergedReason=-5` found and disclosed; a prior run's "Residual tolerance satisfied" message was independently shown to be a false-success pattern masking this same code |
| Peak memory reported per mesh size, as an explicit table | Yes | Yes (`ADJOINT_MEMORY_ENVELOPE.md`) — the rare case where we already meet this bar |

### Ranked reproducibility

1. **Reproducible in principle, not yet attempted.** The nested-Richardson-wrapped ASM+ILU
   preconditioner Kenway et al. use is a directly transferable, cheap, previously-untried lever
   for our own A3 blocker — see Proposal 1 below.
2. **Not reproducible with the current tool as configured.** ADflow's clean 87–253 GB scaling on
   9–26× larger transonic meshes. Blocked not by a paper omission but by DAFoam's own
   documented architecture cost (945-color heuristic coloring, deep call stack, dense stencil) —
   a tool-capability gap, quantified by the tool's own developers, not a reproduction failure on
   our part.

---

## 4. The cylinder Reynolds ladder above Re 3900

### What we have

Solid, internally-verified references at Re 1000 (2D and 3D DNS family, `F5a_cylinder_reynolds_ladder.md`)
and Re 3900 (running at time of writing). The open question: what is citable at Re 10,000 and
above, and where does 2D stop being defensible at all.

### Sources read

**Rao, A., Leontini, J.S., Thompson, M.C. & Hourigan, K., "Three-dimensionality of elliptical
cylinder wakes at low angles of incidence," Journal of Fluid Mechanics 825:245–283 (2017).** Full
text (introduction) read, fetched from Monash University's own repository
(`eng.monash.edu/lbe/Publications/2017/RaLeThHo-JFM-2017.pdf`).

- Directly confirms, with its own citation chain read alongside it: the 2D periodic wake
  transitions to a fully three-dimensional flow starting at **`Re≈190`**, via a long-wavelength
  (~4D) instability known as mode A, "first observed experimentally by Williamson (1988) and
  predicted numerically based on Floquet stability analysis by Barkley & Henderson (1996)." A
  second, shorter-wavelength (~0.8D) instability, mode B, appears at **`Re≈259`** by Floquet
  prediction (Barkley & Henderson 1996), occurring at lower Reynolds numbers in experiments
  "due to the instability mode becoming unstable on an already three-dimensional base flow."
- Barkley & Henderson (1996)'s own headline result, as characterized in this paper's own
  introduction and consistent with how it is cited throughout the wider literature searched this
  session: the 2D wake becomes absolutely linearly unstable to 3D perturbation at a precisely
  quantified critical Reynolds number, `Re_c≈188.5±1.0`. Barkley & Henderson (1996) itself
  (*Journal of Fluid Mechanics* 322:215–241) was **not independently fetched in full this
  session — PAYWALLED**; this specific number is relayed via Rao et al.'s own reading of it,
  which was read in full.

**Internal, already read this lab, reused here with attribution**: Jiang, H. & Cheng, L. (2017),
"Strouhal-Reynolds number relationship for flow past a circular cylinder," *Journal of Fluid
Mechanics* 832:170–188. Fetched and read in full by a prior session, per
`F5a_cylinder_reynolds_ladder.md`, which reproduces their Tables 1–3 (mesh design, 3D
mesh-dependence study at Re=1000) and cross-validates against Henderson (1997), Papaioannou et
al. (2006), Tong et al. (2015), Williamson & Brown (1998), and Norberg (1994). Not re-fetched by
this session; treated as already-verified.

**PAYWALLED — abstract-only, everything below is bounded strictly to what the visible abstract
states, per this task's own rule against inferring paper content from abstracts:**

- Dong, S. & Karniadakis, G.E., "DNS of flow past a stationary and oscillating cylinder at
  Re=10,000," *Journal of Fluids and Structures* 20(4):519–531 (2005). Abstract/search-result
  level only: DNS at Re=10,000 using a multilevel-type parallel spectral-element algorithm,
  ~300 million degrees of freedom. **This is exactly the Re=10,000 3D reference this ladder needs
  next and could not be verified further this session** — see Proposal 4.
- Dong, S., Karniadakis, G.E., Ekmekci, A. & Rockwell, D., "A combined direct numerical
  simulation–particle image velocimetry study of the turbulent near wake," *Journal of Fluid
  Mechanics* 569:185–207 (2006). Abstract directly quoted from search results: *"at higher
  Reynolds number, the lengths of both the wake bubble and the separating shear layer decreased
  substantially, with corresponding patterns of velocity fluctuations and Reynolds stress
  contracting towards the base of the cylinder, and elevated values of Reynolds stress at
  upstream locations in the separated layer indicating earlier onset of shear-layer transition."*
  Compares Re=3900/4000 against Re=10,000 directly by DNS+PIV — the single most relevant paper
  found for our own ladder's next rung, and the clearest candidate for follow-up access.
- Norberg, C., "Fluctuating lift on a circular cylinder: review and new measurements," *Journal
  of Fluids and Structures* 17(1):57–96 (2003). Abstract directly quoted, via Lund University's
  own publication record: covers Re≈47 to 2×10⁵; states "an approximate 10-fold increase in the
  sectional r.m.s. lift coefficient" between Re=1.6×10³ and 20×10³, "reflecting a fundamental
  flow state transition beginning around Re=5×10³" — i.e., the literature's own account places a
  genuine regime change squarely inside the gap between our Re=3900 rung and a Re=10,000 rung,
  independent of the dimensionality question.
- Ma, X., Karamanos, G.S. & Karniadakis, G.E., "Dynamics and low-dimensionality of a turbulent
  near wake," *Journal of Fluid Mechanics* 410:29–65 (2000). Search-result paraphrase only (not a
  verbatim abstract) — DNS/LES Re=500–5000, focused at Re=3900, reports two converged states
  (U-shape/V-shape mean velocity profile) about one diameter downstream. Flagged as lower
  confidence than the items above since only a paraphrase, not the abstract text itself, was
  seen.
- Williamson, C.H.K., "Vortex Dynamics in the Cylinder Wake," *Annual Review of Fluid Mechanics*
  28:477–539 (1996). Could not retrieve full text or even a verbatim abstract this session — cited
  here only as a title/venue/existence reference, as it appears in Rao et al. (2017)'s own
  citation list, not as independently read content.

### What this settles

The literature is unambiguous, and independently confirmed by full-text reading of a 2017 JFM
paper, that **2D loses any claim to representing the true wake at `Re≈190`, fully three-dimensional
by `Re≈260`** — one to two orders of magnitude below even our ladder's Re=1000 rung, let alone
Re=3900 or the Re=10,000+ rungs still to come. Our own ladder's decision to run pure 2D laminar at
every rung is, in this light, not "computing physically valid 2D flow" at any rung past ~260; it
is, exactly as the ladder's own methodology note already states, a deliberate instrument for
measuring the *size* of the dimensionality error, and the literature above supports that framing
rather than undermining it. Norberg's abstract independently places a real physical regime change
(the ~10× lift-coefficient jump) inside the Re=3900→10,000 gap our next rungs will cross — a
genuine physics change to attribute deviation to, separate from the 2D/3D question.

### Reproduction checklist — cylinder Reynolds ladder

| Item | Jiang & Cheng (2017), Re=1000, internal read | Dong & Karniadakis-type Re=10,000 (paywalled) |
|---|---|---|
| Mesh count/topology stated | Yes, precisely (their Tables 1, 3) | Abstract states DOF count (~300M) only; mesh topology not verified |
| Spanwise domain length / cell size (3D cases) | Yes, and shown to be the dominant sensitivity (`dz/D` >> `Lz/D`) | Not verified — full text not obtained |
| Convergence/averaging window | Reproduced in our own F5a record | Not verified |
| Turbulence treatment | DNS, no model | DNS, no model (per abstract) |
| Domain extent, boundary conditions | Stated | Not verified |

### Ranked reproducibility

1. **Reproducible now, already done.** Our own Re=1000 2D rung against Jiang & Cheng's 2D DNS
   family (matches to a few percent) and their 3D DNS family (deviates by the literature's own
   documented, mechanistically-explained amount).
2. **Blocked by access, not by omission.** Dong & Karniadakis (2005)'s Re=10,000 3D DNS — the
   paper appears, from its abstract, to disclose enough to attempt reproduction (DOF count,
   method), but full text was not obtainable this session. This is the review's single most
   actionable gap: it is a paywall problem, not a literature-quality problem.
3. **Not yet establishable at all from what was found.** A citable, quantitative account of
   exactly where above Re≈10⁵ the flow leaves the well-resolved-DNS/LES-tractable regime
   entirely and the literature becomes wind-tunnel-experiment-dominated. Consistent with, but not
   independently confirmed to the same standard as, the NASA hump's own Re=936,000 case already
   needing an 850-million-point WRLES to resolve well — suggesting the same wall applies here,
   but this was not directly verified for the cylinder in this session.

---

## Proposals

Each is falsifiable, costed against work already on disk or trivially cheap, and states what
would disprove it. None require new production compute beyond what is listed.

### Proposal 1 — test the nested-Richardson preconditioner lever on the A3 adjoint blocker

**Hypothesis.** The A3 coarse-mesh (99,840-cell) `DIVERGED_BREAKDOWN` is a preconditioner-strength
problem, not a hard shock-conditioning wall, and is fixable by wrapping the existing PETSc
ASM+ILU stack in nested Richardson iterations (outer around ASM, inner within each ILU sub-block)
— the exact recipe Kenway et al. (2019) report using on ADflow, a sibling tool built by the same
lab, to converge a comparable-Mach transonic shocked wing cleanly at 9–26× our mesh size — without
raising the memory cap.

**Cost.** Near-zero. The A3 coarse-mesh case is already staged and has already been run to this
exact failure point several times (`ADJOINT_MEMORY_ENVELOPE.md` Option 2, ~400–520 s per attempt).
This is a PETSc command-line-option experiment on an existing case, not a new mesh or new solve
class.

**What would disprove it.** `DIVERGED_BREAKDOWN` (`PetscConvergedReason=-5`) persists identically
with Richardson wrapping added, or the memory required to add it exceeds the already-tested 20 GB
cap. Either result would strengthen, not weaken, the case that this is a genuine numerical wall
rather than an untried lever — a useful negative result either way.

### Proposal 2 — check our own converged hump field against the literature's stated mechanism

**Hypothesis.** Per Cappelli & Mansour (2013) and the wider community consensus, our own already-
converged `kOmegaSST` hump solution should show Boussinesq-estimated turbulent shear stress
`-u'v'/Uinf^2` at `x/c=0.8` (the peak-bubble station both papers report on) measurably below the
published experimental peak, by roughly the same fractional shortfall as our reattachment
over-prediction (+13.9%).

**Cost.** Near-zero. A single post-processing extraction from the already-converged, already-on-
disk F6a field. No new solve.

**What would disprove it.** If our shear stress at `x/c=0.8` matches or exceeds the experimental
value, the literature's stated mechanism does not explain our own over-prediction, and the actual
cause would need to be re-opened as a genuinely open question rather than an assumed, textbook
one — itself a reportable finding.

### Proposal 3 — reframe the Delta=0.05 hump result as the field-standard "moderated corner," not an incomplete sweep

**Hypothesis.** Consistent with the field's own "moderation factor" practice (Matha & Morsbach
2023), our already-collected `Delta=0.05` result (reattachment 1.3077, +18.88% vs. experiment,
genuinely converged) should be reported as *the* field-standard-consistent bounded 1C-corner
estimate for this case, with the unreachable `Delta=1.0` corner explicitly reported as
non-existent/non-convergent rather than as a target we fell short of.

**Cost.** Zero — a documentation and framing change against already-collected data, not a new
run.

**What would disprove it.** If a closer reading of the "moderation factor" literature (which this
session could not fully verify — Matha & Morsbach's own cited sources 22/23 were not retrieved)
turns out to require a specific, non-arbitrary procedure for choosing `f` (rather than simply
reporting whatever `Delta` happens to converge), our `Delta=0.05` point would not qualify as a
literature-consistent moderated corner and this reframing should not be adopted without that
procedure.

### Proposal 4 — close the Re=10,000 access gap

**Hypothesis.** Dong, S. & Karniadakis, G.E. (2005), "DNS of flow past a stationary and
oscillating cylinder at Re=10,000," *Journal of Fluids and Structures* 20(4):519–531, and/or
Dong, Karniadakis, Ekmekci & Rockwell (2006), *J. Fluid Mech.* 569:185–207, are obtainable through
a channel not tried this session (institutional proxy, interlibrary loan, or an author's own
repository copy), and contain the mesh, domain, and force-coefficient tables this ladder's next
rung needs to grade against, exactly as Jiang & Cheng (2017) already did for Re=1000.

**Cost.** Access time only, not compute. Zero core-minutes.

**What would disprove it.** The papers remain unobtainable through every reasonable channel, in
which case the Re=10,000 rung would need to cite a different, obtainable reference instead (for
example, a more recent open-access paper that reproduces and re-tabulates the Dong & Karniadakis
Re=10,000 case, several of which this session's searches surfaced but did not independently
verify), and that substitution should be made explicit in the ladder's own record rather than
silently working around the gap.

---

## Bibliography

- Cappelli, D. & Mansour, N.N. "Performance of Reynolds Averaged Navier-Stokes Models in
  Predicting Separated Flows: Study of the Hump Flow Model Problem." NASA Ames Research Center /
  ENSAE. NASA NTRS 20130001741 (2013). Full text read.
- Uzun, A. & Malik, M.R. "Wall-Resolved Large-Eddy Simulation of Flow Separation Over NASA
  Wall-Mounted Hump." AIAA SciTech 2017 (AIAA 2017-0538). NASA NTRS 20170000736. Full text read.
  Expanded journal version: *AIAA Journal* (2017/2018), pp. 715–730 — not independently verified.
- NASA Turbulence Modeling Resource, "2D NASA Wall-Mounted Hump Separated Flow Validation Case,"
  `tmbwg.github.io/turbmodels/` (relocated from `turbmodels.larc.nasa.gov`, 2026-02-24). Reused
  from this lab's own prior verification (`F6a_nasa_hump.md`).
- Emory, M., Larsson, J. & Iaccarino, G. "Modeling of structural uncertainties in
  Reynolds-averaged Navier-Stokes closures." *Physics of Fluids* 25(11):110822 (2013). PAYWALLED
  — relayed via Heyse et al. (2021)'s description, not independently read.
- Heyse, J.F., Mishra, A.A. & Iaccarino, G. "Estimating RANS model uncertainty using machine
  learning." *J. Global Power and Propulsion Society*, Special Issue: Data-Driven Modelling and
  High-Fidelity Simulations, pp. 1–14 (2021). DOI 10.33737/jgpps/134643. Full text read (open
  access).
- Matha, M. & Morsbach, C. "Improved self-consistency of the Reynolds stress tensor eigenspace
  perturbation for Uncertainty Quantification." arXiv:2303.06149 (2023); also *Physics of Fluids*
  35(6):065130. Partial full text read (arXiv PDF).
- Giles, M.B. & Pierce, N.A. "Analytic adjoint solutions for the quasi-one-dimensional Euler
  equations." *Journal of Fluid Mechanics* 426:327–345 (2001). Full text (intro) read.
- Kenway, G.K.W., Mader, C.A., He, P. & Martins, J.R.R.A. "Effective Adjoint Approaches for
  Computational Fluid Dynamics." *Progress in Aerospace Sciences* (2019, in press at preprint
  time). MDO Lab, University of Michigan. Full text read (preprint).
- Rao, A., Leontini, J.S., Thompson, M.C. & Hourigan, K. "Three-dimensionality of elliptical
  cylinder wakes at low angles of incidence." *Journal of Fluid Mechanics* 825:245–283 (2017).
  Full text (introduction) read.
- Barkley, D. & Henderson, R.D. "Three-dimensional Floquet stability analysis of the wake of a
  circular cylinder." *Journal of Fluid Mechanics* 322:215–241 (1996). PAYWALLED — not
  independently read; the `Re_c≈188.5` result is relayed via Rao et al. (2017)'s own citation of
  it.
- Jiang, H. & Cheng, L. "Strouhal-Reynolds number relationship for flow past a circular
  cylinder." *Journal of Fluid Mechanics* 832:170–188 (2017). Full text read by a prior session
  in this lab; reused here with attribution, not re-fetched.
- Dong, S. & Karniadakis, G.E. "DNS of flow past a stationary and oscillating cylinder at
  Re=10,000." *Journal of Fluids and Structures* 20(4):519–531 (2005). PAYWALLED — abstract/
  search-result level only.
- Dong, S., Karniadakis, G.E., Ekmekci, A. & Rockwell, D. "A combined direct numerical
  simulation–particle image velocimetry study of the turbulent near wake." *Journal of Fluid
  Mechanics* 569:185–207 (2006). PAYWALLED — abstract directly quoted, no further content seen.
- Norberg, C. "Fluctuating lift on a circular cylinder: review and new measurements." *Journal of
  Fluids and Structures* 17(1):57–96 (2003). PAYWALLED — abstract directly quoted (via Lund
  University's publication record), no further content seen.
- Ma, X., Karamanos, G.S. & Karniadakis, G.E. "Dynamics and low-dimensionality of a turbulent
  near wake." *Journal of Fluid Mechanics* 410:29–65 (2000). PAYWALLED — search-result paraphrase
  only, flagged as lower confidence than the other paywalled entries above.
- Williamson, C.H.K. "Vortex Dynamics in the Cylinder Wake." *Annual Review of Fluid Mechanics*
  28:477–539 (1996). PAYWALLED — title/venue only, no abstract or content retrieved.
