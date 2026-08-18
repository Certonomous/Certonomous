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

**Addendum, same standards, new session.** Section 5 below was added in a follow-up no-compute
session (read/search/write only; no solver launched, matching the four live production jobs running
at the time — including a 15-hour 3D cylinder rung — untouched) to answer four literature questions
raised by the Re 3900 rung's own finding that its mean recirculation bubble had vanished. The same
provenance discipline applies: PAYWALLED sources are marked as such, Unpaywall/DOI checks are
reported explicitly rather than assumed, and two figures (not just extracted text) were fetched and
read directly where the paper's own prose did not carry the needed data.

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
  which was read in full. **RELAYED, NOT VERIFIED** *(tier label added 2026-08-05 per the
  citation-tier audit; the relay chain and what may be done with the number are stated in the
  source list at the foot of this file, Barkley & Henderson entry)*: what this record verifies is
  that Rao et al. state the figure, not that Barkley & Henderson print it.

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

## 5. Loss of the 2D mean recirculation bubble at Re 3900 — four questions from tonight's result

### What we found tonight, restated

`F5a_cylinder_reynolds_ladder.md`'s Re 3900 rung finds no sign change of the time-mean centreline
streamwise velocity anywhere in the probed range — the same definition Parnaudeau et al. (2008)
state explicitly for `Lr` — while the raw (non-averaged) centreline signal reverses sign 34-39% of
the time near the base, with excursions past -1.0. Re 1000 and Re 2000, probed with the identical
method, both show a genuine, shrinking mean bubble (0.397D, 0.254D). Extrapolating those two points
predicts ~0.165D at Re 3900; the measurement is zero, not a smaller positive number. This session's
task: no compute, read/search/write only, to find out whether this is a reproduction of a known
result or a new one, and to check it is not an artifact of a documented, unrelated 2D deficit.

### Q1 — has anyone published the 2D mean bubble being lost above some Re?

**No paper found this session states, as its own finding, "the 2D time-mean recirculation bubble
disappears above Reynolds number X" for the plain circular cylinder.** The search was not
exhaustive — several likely-relevant titles were paywalled and could not be read (below) — so this
is reported as "not found," not as "does not exist."

The closest bracketing evidence:

**Singh, S.P. & Mittal, S., "Flow past a Cylinder: Shear Layer Instability and Drag Crisis,"
*International Journal for Numerical Methods in Fluids* 47(1):75-98 (2005).** Full text read (41
pages, the authors' own accepted manuscript, freely self-archived at
`home.iitk.ac.in/~smittal/publi_&_present/sm_journals/drag_crisis.pdf` — not paywalled). This is a
pure 2D DNS (stabilized finite-element, unsteady incompressible Navier-Stokes, no turbulence model)
run from Re=100 to Re=10^7, sampling Re=100, 2000, **3900**, 7000, 10^4, 3.2x10^4, 10^5, 10^6, 10^7
— the closest methodological cousin to our own ladder found in this entire review, and the only
source found that runs pure 2D at exactly Re=3900.

- Their own text, quoted: *"as the three dimensional features in the flow become increasingly
  important, the two-dimensional computations over predict the mean drag and base suction
  coefficient for 2x10^3 < Re < 3.2x10^4"* — a range that brackets our Re 3900 rung directly — and
  *"Mittal and Balachander have suggested that the higher value of the drag coefficient for the 2D
  simulations is caused due to higher level of Reynolds stresses resulting in a shorter formation
  length behind the bluff body."*
- Their Figure 13 (time-averaged streamlines) is discussed explicitly in text only for Re=2000,
  10^5 and 10^6 — quoted: *"the Re = 2000 flow is associated with two recirculation zones on each
  half of the cylinder. However, they are located away from the surface of the cylinder and the
  speed of flow in these regions is relatively small."* **Re=3900 is not among the Reynolds numbers
  discussed for Figure 13** — the one rung that would have directly confirmed or refuted our own
  finding is the one their own streamline discussion skips.
- **The figure was fetched and read directly, per this task's own standard, since it carries data
  the extracted text does not.** Figure 5 (time-averaged vorticity field and Reynolds stresses,
  `u'u'`, `v'v'`, `u'v'`, for each sampled Re) shows, at Re=3900, a compact structure immediately
  behind the cylinder visually similar in extent to the Re=2000 panel next to it. **This cannot be
  read as confirming or refuting our own finding**: vorticity contours describe circulation and
  shear, not the sign of the mean streamwise velocity on the centreline — the specific quantity our
  own `Lr` gate depends on — and no streamwise-velocity centreline profile for Re=3900 is plotted
  anywhere in this paper. Stated as an open, unresolved tension, not a contradiction: the nearest
  precedent found stops exactly one rung short of the comparison needed and uses a different field.

**A related but distinct, independently-confirmed fact**, read in full: **Scott, L.R. & Durst, R.,
"Chaotic dynamics of two-dimensional flows around a cylinder," arXiv:2311.07698 (2023).** Full text
read (open access, 27 pages, `arxiv.org/pdf/2311.07698`). Pure 2D DNS (pressure-robust finite
elements, IMEX time-stepping), Re up to ~10^4, using drag/lift time series (Lyapunov exponent,
correlation with a fitted periodic signal, fractal dimension of the drag/lift attractor) rather than
any wake-length metric. Quoted directly: *"the vortex shedding in the Karman vortex street is
periodic, beginning around Reynolds number 50... and continuing this periodicity up to Reynolds
number 200. Moreover, our results indicate that this periodicity noticeably begins to break down as
early as Reynolds number 250"*; and, from the abstract, *"a vibrational resonance in the cylinder
would be unlikely for Reynolds numbers greater than 1000, where the drag/lift behavior is fully
chaotic."* This is a **different quantity** than our `Lr` (global force-signal periodicity, not a
local mean-velocity wake length) — it neither confirms nor measures bubble loss — but it
independently establishes, from a different code, method and research group than either our own
ladder or Singh & Mittal, that a pure 2D-constrained cylinder wake's overall dynamics are already
**fully chaotic by Re>1000**, i.e. well below our Re 3900 rung. A wake whose forcing signal is
already established in the literature to be chaotic by Re~1000 is a plausible host for a mean
quantity that later, at some higher Re, tips over from "small but present" to "erased by asymmetric
excursions" — consistent with, but not a citation for, our own finding.

**Verdict on Q1: apparently novel, not previously reported as far as this session could determine,
bracketed on one side by a directly comparable but incomplete precedent (Singh & Mittal skip the
one rung that mattered) and on the other by independent confirmation that the host dynamics are
already chaotic well before this Re.** This should be reported as a new result, not a reproduction.

### Q2 — is 2D mean Lr reported anywhere in this Re range, matched against 3D at the same Re?

**No source found this session reports 2D `Lr` and 3D `Lr` side by side at a matched Re anywhere in
1000-3900**, beyond what our own ladder already has on record (the Jiang & Cheng 2017 Re=1000
cross-check, and the Fig. 6 `Lf`-based ratio check already logged in `F5a_cylinder_reynolds_ladder.md`,
which found the 2D/3D gap widening rather than holding at a fixed ratio). The brief's own warning —
that Jiang & Cheng's Fig. 6 plots `Lf`, formation length, not `Lr` — is repeated here deliberately,
because two more sources found this session make exactly the same substitution and had to be read
carefully to avoid re-making the error the brief flagged:

**Mittal, R. & Balachandar, S., "Effect of three-dimensionality on the lift and drag of nominally
two-dimensional cylinders," *Physics of Fluids* 7(8):1841-1865 (1995).** **PAYWALLED** — confirmed
via Unpaywall on DOI `10.1063/1.868500` (`is_oa: false`, no repository copy); a direct fetch of
AIP's own PDF link was blocked by a Cloudflare challenge page, not a genuine document. Everything
below is relayed via independent secondary summaries (search-result synthesis of the paper's own
abstract and citing literature), not the full text, and is bounded to what those summaries state.
Decomposes a 3D DNS velocity field into a spanwise-mean component and a 3D remnant, solves the
pressure-Poisson equation for each separately, and attributes the 2D-vs-3D force discrepancy to
differences in the near-wake pressure/Reynolds-stress field; reported numbers are for **Re=525**
(16% higher `Cd`, 88% higher lift peak-to-valley in 2D vs 3D — **RELAYED, NOT VERIFIED**; tier
label and relay chain corrected 2026-08-05 in the note directly below, and the two percentages
may not be used as measured values) — a useful confirmation that the same
over-prediction mechanism operates at low Re, but not a same-Re comparison at 3900 and not a
reported `Lr` value at all (the mechanism is stated in terms of Reynolds-stress concentration and
formation length, `Lf`-type language, not `Lr`).

> **Correction 2026-08-05 — the two numbers above are RELAYED, NOT VERIFIED, and the tier is
> printed here rather than left to the paragraph.** Flagged by
> `sdk/scripts/citation_tier_audit.py` (checker landed at commit `c3033a36`) under its adopted
> rule "a quantity asserted beside a tier below READ IN FULL", which reads
> `docs/charters/LITERATURE_CHARTER.md` §2's tier table and §7's first NEVER. **Tier:
> PAYWALLED, abstract-and-secondary-summary only.** **Relay chain, named:** the 16% higher `Cd`
> and 88% higher lift peak-to-valley at Re=525 were not read off Mittal & Balachandar's own text,
> tables or figures by anyone in this lab; they reached this record through search-result
> synthesis of the paper's abstract and of citing literature, which is a secondary
> characterisation of a source — the thing §4 of the charter's allowed-sources list ranks last
> and warns is the most common way a wrong number propagates. **The numbers are kept, not
> deleted**, because deleting them would lose the lead; they may not be used as measured values,
> compared against any number of ours, or reproduced to these significant figures until someone
> reads the paper. Queued for library access:
> `demo-output/website/agenda/LIBRARY_ACCESS_LIST.md` item 8.

**Balachandar, S., Mittal, R. & Najjar, F.M., "Properties of the mean recirculation region in the
wakes of two-dimensional bluff bodies," *Journal of Fluid Mechanics* 351:167-199 (1997).**
**PAYWALLED** — confirmed via Unpaywall on DOI `10.1017/s0022112097007179` (`is_oa: false`);
ResearchGate returned HTTP 403. The abstract (obtained via Crossref's public metadata record, not
the paper itself — marked explicitly as abstract-only) states the paper studies the "time- and
span-averaged mean wake recirculation region... wake bubble" across **ten cases spanning
Re=250-140,000** (circular/elliptic/square cylinders and a normal plate), drawing on the authors'
own DNS at lower Re and LES/experiment (including Cantwell & Coles 1983) at higher Re, and states
plainly that **the mean recirculation region is present in all ten cases**. **This is the one
finding in this whole review that would, if it includes an unmodelled 2D case at a matched Re, cut
directly against our own result** — but the abstract's own phrase "span-averaged" strongly implies
the low-Re entries are 3D (or otherwise turbulence-resolving) datasets rather than our own
un-modelled 2D-laminar configuration, and this cannot be resolved without the paywalled full text.
**Recorded as an open, unresolved gap, not papered over**: see Proposal 6.

**Verdict on Q2: no matched-Re 2D-vs-3D `Lr` comparison exists in the literature found this
session for 1000<Re<3900.** The literature that does exist in this Re-adjacent space (Mittal &
Balachandar 1995 at Re=525; Balachandar/Mittal/Najjar 1997's broader Re=250-140,000 survey) reports
the mechanism (near-body Reynolds-stress concentration, shorter `Lf`) rather than the specific
`Lr` quantity, and the one source whose own claim ("bubble present in all ten cases") is in tension
with ours cannot be checked past its abstract. This is exactly the situation the brief warned could
undercut the finding — a possible fixed or worsening 2D-vs-3D deficit rather than a genuine
transition — and it is **not resolved** by what this session could read; it is a real, live
uncertainty, not a settled point in either direction.

### Q3 — is there a standard way to measure recirculation length when the mean has no closed bubble?

**Yes, in a form directly applicable here, and it does not require calling the quantity
unmeasurable.**

**Gerrard, J.H., "The mechanics of the formation region of vortices behind bluff bodies," *Journal
of Fluid Mechanics* 25:401-413 (1966).** **PAYWALLED** — relayed via independent secondary summaries
only, not the full text. Introduces the **formation length `Lf`**, defined as the streamwise
distance from the body to the midpoint between the two off-axis peaks of streamwise-velocity r.m.s.
fluctuation — a quantity built entirely from second-moment statistics of the fluctuating field, not
from the sign of the mean velocity. Because it only requires that the shear layers exist and
fluctuate (which our own data plainly shows they do — the 34-39% reversal-frequency numbers already
on record in `F5a_cylinder_reynolds_ladder.md` **are** fluctuation statistics), `Lf` stays
well-defined exactly where `Lr` breaks down. This is not a proposal to invent a new metric; it is a
60-year-old, field-standard practice, independently corroborated by two sources read in full this
session: Singh & Mittal (2005, above, citing Mittal & Balachandar's own "shorter formation length"
mechanism) and Jiang & Cheng (2017, read by a prior session per `F5a_cylinder_reynolds_ladder.md`,
whose own Fig. 6 already plots 2D and 3D `Lf`-Re curves to Re=1000).

**Simpson, R.L., "Turbulent Boundary-Layer Separation," *Annual Review of Fluid Mechanics*
21:205-234 (1989).** Full text read directly (freely hosted PDF, Virginia Tech's own institutional
archive, `archive.aoe.vt.edu/simpson/aoe6154/Simp_Sep_AnnuRev_1989.pdf` — confirmed open, pages read
as rendered images since the file is a scanned reprint). Establishes a field-standard alternative
**principle** — not the same metric, but the same underlying idea our own data already supports —
for exactly this kind of situation: classify the separation state by the **fraction of time
backflow occurs**, not by the sign of the time-mean alone. Quoted directly: *"It is too narrow a
view to use vanishing surface shearing stress or flow reversal as the criterion for separation...
For steady free-stream two-dimensional flows on streamlined surfaces, separation begins
intermittently at a given location... At progressively farther downstream locations, the fraction
of time that the flow moves downstream is progressively less."* The paper's own quantitative scale,
based on the fraction of time `gamma_pu` the flow moves downstream at a **wall** location:
**incipient detachment** (`gamma_pu=0.99`, 1% backflow time), **intermittent transitory
detachment** (`gamma_pu=0.80`, 20%), **transitory detachment** (`gamma_pu=0.50`, 50% — quoted,
*"found... to coincide with a zero value for the time-averaged wall shear stress"*), and
**detachment** (where the mean wall shear stress itself reaches zero, coinciding with TD in
available data). **This framework's established domain is a single separation location along a
wall-bounded shear flow — not a near-wake centreline recirculation length, which is a streamwise
extent, a different geometric question.** No paper found this session applies Simpson's specific
percentage-of-reversal-time scale to a wake bubble length. Its relevance here is as **precedent for
the principle**, not as a ready-made formula: the field already accepts, and has for decades, that
reversal probability is more physically fundamental than the sign of a single averaged number, in
exactly the situation (large-amplitude, high-frequency near-wall/near-wake unsteadiness) our Re
3900 rung is in.

**Two low-cost, falsifiable next steps follow directly and are written up as Proposals 5 and 6
below** — one is a direct application of an established metric (`Lf`) to data already on disk; the
other is our own candidate extension of Simpson's principle (explicitly flagged as our own idea, not
a literature citation) to a wake-length setting.

### Q4 — is 2D bubble loss connected in the literature to the absence of the spanwise instability?

**No single source found this session states this causal chain as its own conclusion.** What
exists is two independently-verified, adjacent facts, and a synthesis connecting them that is
offered here explicitly as this lab's own inference, not as anyone's published claim.

**Fact 1 (already established in this review, Section 4, reused with attribution)**: the real,
3D-permitted cylinder wake becomes absolutely linearly unstable to a spanwise (mode A) perturbation
at `Re~188.5` (Barkley & Henderson 1996, PAYWALLED, relayed via Rao et al. 2017, read in full by a
prior session), with the shorter-wavelength mode B following by `Re~259-260`. Both are far below
Re=3900.

**Fact 2**: **Karniadakis, G.E. & Triantafyllou, G.S., "Three-dimensional dynamics and transition to
turbulence in the wake of bluff objects," *Journal of Fluid Mechanics* 238:1-30 (1992).**
**PAYWALLED** — confirmed via Unpaywall-style DOI check was not separately run, but a direct fetch
attempt of the paper itself failed and no repository copy was located; the abstract below was
obtained via Crossref's public metadata record (not the paper), and is quoted in full rather than
paraphrased so nothing beyond what it literally states is asserted: *"The wakes of bluff objects...
undergo a 'fast' transition, from a laminar two-dimensional state at Reynolds number 200 to a
turbulent state at Reynolds number 400... the wake first becomes three-dimensional, as a result of a
secondary instability of the two-dimensional vortex street [at] a Reynolds number close to 200...
At higher Reynolds numbers the three-dimensional flow oscillation undergoes a period-doubling
bifurcation... Further increases of the Reynolds number result in a cascade of period-doubling
bifurcations, which create a chaotic state in the flow at a Reynolds number of about 500."*
**This is a 3D DNS of the real transition process** — the chaos it documents is the natural,
physical route the real (3D-permitted) wake takes into turbulence, not a study of what happens when
a solver is artificially confined to 2D. It should not be read as being about 2D simulation
artifacts; it is about the real flow.

**The synthesis (this lab's own inference, stated as such):** Fact 2 shows the real wake's own
transition to chaos is driven by, and inseparable from, the spanwise (3D) instabilities of Fact 1 —
the period-doubling cascade K&T describe IS the mode-A/mode-B competition playing out in time. A
solve with no spanwise direction at all cannot have that specific route to chaos, yet Scott & Durst
(Q1, above, full text read) independently show a purely 2D-confined wake becomes chaotic anyway, by
a different mechanism, at a broadly similar Re (250-1000). One plausible reading — not established
by any single source, offered here as a hypothesis to test, not a finding to cite — is that the
real wake's spanwise instability gives its chaotic energy somewhere to go (a third dimension to
shed vorticity into, keeping the span-averaged mean orderly enough to sustain a stable bubble out to
Re=140,000, per the Balachandar/Mittal/Najjar 1997 abstract above), while a 2D-confined wake's
chaos has nowhere to go but back into the two components of velocity the solve actually has,
eventually growing large enough (per our own measured forward-excursion growth, 0.22->0.52->0.81
from Re 1000->2000->3900, already on record in `F5a_cylinder_reynolds_ladder.md`) to erase the mean
bubble outright. **This is exactly the falsifiable mechanism Proposal 6 below is designed to
pressure-test**, not a claim being advanced as settled.

The field's own standard account of *why* 2D over-predicts forces generally — spanwise phase
decorrelation suppressing the coherent shedding signal in 3D but not in 2D (already used at this
ladder's own Re=1000 gate, citing Jiang & Cheng 2017) — explains a **quantitative** over-prediction.
No source found this session extends that same account to a **qualitative**, topology-changing claim
(bubble present vs. absent) the way our own Re 3900 finding requires.

### What this section settles, and what it leaves open

**Settled**: this appears to be a genuinely new observation, not a reproduction of a published
result (Q1). A field-standard alternative metric exists and should be computed rather than reporting
"unmeasurable" (Q3, `Lf`). No source found connects bubble loss to the absent spanwise instability as
its own stated conclusion — the connection offered here is this lab's own inference, disprovable, and
should be labelled as such wherever this finding is written up elsewhere (Q4).

**Open, honestly**: whether 2D `Lr` is always a fixed or worsening fraction of 3D `Lr` in this Re
range such that Re=3900 is merely where a long-standing deficit reaches zero, rather than a genuine
qualitative transition (Q2) — the one source found in tension with our own result
(Balachandar/Mittal/Najjar 1997) could not be read past its abstract, and this is recorded as a real
gap in this review's coverage, not resolved by inference or by the direction of the other evidence.

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

### Proposal 5 — compute formation length `Lf` from the already-collected Re 3900 probe data

**Hypothesis.** Even though `Lr` (mean-velocity sign change) is inapplicable at Re 3900, the
field-standard alternative `Lf` (Gerrard 1966: streamwise distance to the midpoint between the two
off-axis peaks of streamwise-velocity r.m.s. fluctuation) is well-defined from the same raw
`probesCenterline` series already on disk from the completed run, since it depends only on the
fluctuating field, which our own reversal-frequency numbers (34-39%) already prove is well-resolved.
This would replace "NOT MEASURABLE BY THIS METRIC" with an actual number, directly comparable to
Jiang & Cheng's own 2D/3D `Lf`-Re curve (already read, their Fig. 6) extended past Re=1000, and to
Singh & Mittal's (2005) "shorter formation length" mechanism.

**Cost.** Near-zero. A post-processing script over data already written to disk (the same probe
fan `F5a_cylinder_reynolds_ladder.md` already used for the `Lr` measurement, off-axis rather than
centreline stations). No new solve, no new core-minutes.

**What would disprove it.** If the off-axis r.m.s. profile has no clear double peak (e.g. it is
flat, or single-peaked on the centreline) at Re 3900, `Lf` is not well-defined either at this rung,
and that would itself be a stronger, more specific finding than "unmeasurable" — it would mean the
near-wake has lost coherent shear-layer roll-up entirely, not just a stable mean bubble.

### Proposal 6 — test the median-based (`P(u<0)=0.5`) recirculation length against the mean-based one

**Hypothesis.** Adapting Simpson's (1989) reversal-time-fraction principle (established for
wall-bounded boundary-layer separation, not previously found applied to a wake bubble length — this
adaptation is this lab's own idea, not a literature citation) to the centreline probe fan already
collected at all three completed rungs: define a median-based `Lr_50`, the downstream distance at
which the *probability* of reversed flow crosses 50%, rather than the *mean* crossing zero. At Re
1000 and Re 2000, where the velocity distribution is presumably close to symmetric/unimodal, `Lr_50`
should coincide closely with the already-measured `Lr` (0.397D, 0.254D) — a check on whether the new
metric is consistent with the old one where both apply. At Re 3900, `Lr_50` may or may not be
defined depending on whether reversal probability crosses 50% anywhere in the probed range; the
existing 34-39% reversal-frequency numbers near the base suggest it may not (they are below 50%),
which would itself be informative — a quantified answer ("reversal probability peaks at X%, never
reaching the 50% a median-based bubble would need") rather than a binary "not found."

**Cost.** Near-zero. Same raw probe series as Proposal 5, all three completed rungs, no new solve.

**What would disprove it.** If `Lr_50` and the existing mean-based `Lr` disagree substantially at Re
1000/2000 (where both are defined), the median-based metric is not simply confirming the existing
gate and would need its own justification before being trusted at Re 3900 — a genuine risk this
proposal states up front rather than discovering after the fact.

### Proposal 7 — resolve the Balachandar/Mittal/Najjar (1997) tension via full-text access

**Hypothesis.** Balachandar, Mittal & Najjar (1997) state, per their abstract only (Section 5, Q2
above), that a mean recirculation region is present in all ten of their cases spanning Re=250 to
140,000 — in apparent tension with our own no-bubble finding at Re=3900. Institutional or
interlibrary access to the full text (Cambridge Core, DOI `10.1017/s0022112097007179`) would reveal
whether any of their ten cases is an un-modelled, pure-2D case (as opposed to 3D or span-averaged
turbulence-resolving data) at a Reynolds number in or near our own ladder's range, which is the one
piece of information the abstract does not resolve and this session could not access.

**Cost.** Access time only, not compute. Zero core-minutes. Batches naturally with Proposal 4's
existing Dong & Karniadakis / Wang (2010) access requests, since all three sit behind the same class
of paywall.

**What would disprove it.** If access is obtained and none of the ten cases is a pure 2D-laminar
case in our Re range, the apparent tension dissolves on its own (the paper was never describing our
configuration) and this should be recorded plainly rather than left as an open flag indefinitely.

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
  circular cylinder." *Journal of Fluid Mechanics* 322:215–241 (1996). **Tier: PAYWALLED, not
  independently read** — the `Re_c≈188.5±1.0` and the mode-B `Re≈259` figures are **RELAYED, NOT
  VERIFIED**. *Correction 2026-08-05, flagged by `sdk/scripts/citation_tier_audit.py` (commit
  `c3033a36`) under its "quantity asserted at a below-full tier" rule:* **the relay chain is
  Barkley & Henderson (1996) → Rao, Leontini, Thompson & Hourigan (2017) §1 → this record**, i.e.
  another paper's characterisation of a third paper, which `docs/charters/LITERATURE_CHARTER.md`
  §4 names as the most tempting and most common way a wrong number propagates. Rao et al. was
  read in full here, so what is verified is *that Rao et al. state it*, not that Barkley &
  Henderson print it, and not the ±1.0. **The numbers stay** — they bracket our Re=3900 rung by
  more than an order of magnitude, so no conclusion of ours turns on their third digit — and they
  may not be quoted as read, refined, or set beside a measurement of ours until the paper is
  opened. Queued for library access:
  `demo-output/website/agenda/LIBRARY_ACCESS_LIST.md` item 9.
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
- Singh, S.P. & Mittal, S. "Flow past a Cylinder: Shear Layer Instability and Drag Crisis."
  *International Journal for Numerical Methods in Fluids* 47(1):75–98 (2005). Full text read (41
  pages, authors' own self-archived accepted manuscript, not paywalled). Figures 4, 5, 6 and 13
  fetched and read directly as page images, not just extracted text, per this task's own standard.
- Scott, L.R. & Durst, R. "Chaotic dynamics of two-dimensional flows around a cylinder."
  arXiv:2311.07698 (2023). Full text read (27 pages, open access).
- Simpson, R.L. "Turbulent Boundary-Layer Separation." *Annual Review of Fluid Mechanics*
  21:205–234 (1989). Full text read (freely hosted PDF, Virginia Tech institutional archive,
  pages read as rendered images).
- Gerrard, J.H. "The mechanics of the formation region of vortices behind bluff bodies." *Journal
  of Fluid Mechanics* 25:401–413 (1966). PAYWALLED — relayed via independent secondary summaries
  only, not independently read.
- Mittal, R. & Balachandar, S. "Effect of three-dimensionality on the lift and drag of nominally
  two-dimensional cylinders." *Physics of Fluids* 7(8):1841–1865 (1995). PAYWALLED — confirmed via
  Unpaywall (DOI `10.1063/1.868500`, `is_oa: false`); a direct AIP PDF fetch returned a Cloudflare
  challenge page, not the document. Relayed via independent secondary summaries only.
- Balachandar, S., Mittal, R. & Najjar, F.M. "Properties of the mean recirculation region in the
  wakes of two-dimensional bluff bodies." *Journal of Fluid Mechanics* 351:167–199 (1997).
  PAYWALLED — confirmed via Unpaywall (DOI `10.1017/s0022112097007179`, `is_oa: false`); abstract
  obtained via Crossref's public metadata record and quoted, not the paper itself.
- Karniadakis, G.E. & Triantafyllou, G.S. "Three-dimensional dynamics and transition to
  turbulence in the wake of bluff objects." *Journal of Fluid Mechanics* 238:1–30 (1992).
  PAYWALLED — no repository copy located; abstract obtained via Crossref's public metadata record
  and quoted in full, not the paper itself.
- Karniadakis, G.E. & Triantafyllou, G.S. "Frequency selection and asymptotic states in laminar
  wakes." *Journal of Fluid Mechanics* 199:441–469 (1989). PAYWALLED — confirmed via Unpaywall
  (DOI `10.1017/s0022112089000431`, `is_oa: false`); referenced by title/venue only via secondary
  search results, no abstract independently verified. Not cited as a source of any specific claim
  in Section 5 above.
- Braza, M., Chassaing, P. & Ha Minh, H. "Numerical study and physical analysis of the pressure
  and velocity fields in the near wake of a circular cylinder." *Journal of Fluid Mechanics*
  165:79–130 (1986). PAYWALLED — confirmed via Unpaywall (DOI `10.1017/s0022112086003014`,
  `is_oa: false`); title/venue only, no content read or cited above.
