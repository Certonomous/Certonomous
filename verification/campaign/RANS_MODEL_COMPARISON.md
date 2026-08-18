# RANS turbulence-model comparison — is F6c/F7a fixable by model choice?

Date: 2026-07-28. Repo: `/home/ubuntu/Certonomous`. Machine-readable companion:
`RANS_MODEL_COMPARISON.json`. OpenFOAM v2606 (OpenCFD/ESI), native, no Docker.
All new runs: serial (1 rank), foreground, nothing left running. `MemAvailable`
checked before and after: ~30 GB free throughout (mega-batch + other agents
coexisting).

**The owner's question:** two campaign gates failed under kOmegaSST — F6c
(square duct, zero secondary flow vs DNS's 2.07–2.22%) and F7a (dam break,
+13.6% mean / +21.3% max surge-front error). Is either fixable by changing
turbulence model, or is it structural?

**Short answer: two different diagnoses.** F7a's failure has nothing to do
with turbulence-model choice — no turbulence model was active in that run.
F6c's failure is structural to the *class* of closure (linear/Boussinesq),
not a coefficient problem, and switching to a nonlinear model measurably
fixes the mechanism but not, on its own, the magnitude.

---

## F7a dam break — judged first, zero compute burned

Per the docket's own instruction: judge relevance before burning compute.

- **Checked directly:** `F7_runs/damBreak_MM_a2p25in_{coarse,medium,medium_closedbox}/constant/turbulenceProperties`
  in all three F7a cases reads:
  ```
  simulationType  laminar;
  ```
  **No RAS model — not kOmegaSST, not anything — was ever solved in F7a.**
  This is stated in the original F7 report too ("laminar model, consistent
  with the cited paper's own inviscid/laminar treatment") but is confirmed
  here directly from the case dictionaries, not inferred from prose.
- **Physical reasoning:** dam-break collapse over the timescale measured
  (T≈4–10 in Martin–Moyce units) is inertia/gravity-driven (Froude-scaled);
  physical Re≈4×10⁴ is high enough that the *bulk* collapse dynamics are set
  by pressure and gravity, not turbulent Reynolds stresses — the standard
  simplification in essentially all VOF dam-break validations in the
  literature.
- **The root cause was already correctly diagnosed in the F7 report** and is
  unrelated to closure modelling: mesh refinement a/8→a/20 *flipped the sign*
  of the front-position error (rules out under-resolution), BC choice
  (open-top vs closed-box) was A/B-tested and made no difference, and the
  error is concentrated at the thin near-wall leading edge — correlated with
  the near-wall probe height used to define the alpha=0.5 crossing on a VOF
  field. That is an interface-tracking/front-definition issue, not a
  turbulence-closure issue.

**Verdict: NOT APPLICABLE. Turbulence-model choice cannot fix or break F7a's
gate, because no turbulence model was active in the failing case.** 0
core-minutes spent — settled by reading files already on disk. No F7 CFD was
re-run.

---

## F6c square duct — prediction, stated before running

**Prediction (made before any new run in this sweep):** secondary flow of
the second kind in a straight non-circular duct is driven by anisotropy in
the cross-plane normal Reynolds stresses (τ_yy ≠ τ_zz). Every **linear
(Boussinesq)** eddy-viscosity model computes the Reynolds stress as an
isotropic function of mean strain (τ_ij = −2ν_t S_ij + (2/3)k δ_ij), which
has **zero** deviatoric normal-stress anisotropy in the duct cross-plane by
construction. **Linear models — SpalartAllmaras, kEpsilon, realizableKE,
kOmega, kOmegaSST — cannot produce this secondary flow, at any coefficient
setting, at any convergence level.** Only a **nonlinear** eddy-viscosity
model or a full **Reynolds-stress model (RSM)** has the structural capacity
to generate it. If every linear model gives exactly zero and a
nonlinear/RSM model gives something nonzero, that's a clean confirmation.

### Models available in this OpenFOAM v2606 box (checked before planning)

`$FOAM_ETC/caseDicts/turbulenceModels` was empty on this box; the model list
was instead confirmed via `strings` on `libincompressibleTurbulenceModels.so`
and `turbulentTransportModels.C`:

- **Linear:** SpalartAllmaras, kEpsilon, RNGkEpsilon, realizableKE,
  LaunderSharmaKE, kEpsilonPhitF, kOmega, kOmegaSST, kOmegaSSTSAS,
  kOmegaSSTLM, GEKO
- **Nonlinear:** LienCubicKE (cubic, Lien/Chen/Leschziner 1996 — the
  literature model developed and validated specifically on square-duct
  secondary flow), ShihQuadraticKE (quadratic)
- **Reynolds-stress (RSM):** LRR, SSG, EBRSM

### Case

- Reused **verbatim, no re-mesh**: `demo-output/website/dafoam/ladder-b/duct_baseline/AR_1_Ret_360`
  mesh, `transportProperties`, `fvSchemes`, `fvOptions` (`meanVelocityForce`),
  boundary conditions (B2, commit `e2c45ab`).
- 3,025 cells, quarter square duct (2 symmetry planes, exploiting the known
  8-fold symmetry of the secondary-flow pattern), streamwise-cyclic,
  wall-resolved, Re_τ=342, Re_b=5693, `simpleFoam`.
- **Scope:** only `AR_1_Ret_360` run in this sweep (not `AR_3_Ret_360`) to
  keep new compute minimal — the zero-vs-nonzero question doesn't depend on
  aspect ratio, and kOmegaSST already showed zero on *both* AR_1 and AR_3 in
  F6c.
- DNS reference: **2.22% U_bulk** (shipped `0/U_LES`, same mesh, per
  `F6c_duct_vs_dns.md`).
- For the k-ε-family models (kEpsilon, realizableKE, LienCubicKE) and
  SpalartAllmaras, added `0/epsilon` and `0/nuTilda` fields (not present in
  the SST baseline) with standard wall functions; kOmega reused the SST
  baseline's k/omega field set unchanged, only `RASModel` swapped.

### Results table

| Model | Formulation class | Secondary flow (% U_bulk) | % of DNS (2.22%) captured | Iterations | Core-min | Verdict |
|---|---|---|---|---|---|---|
| **kOmegaSST** (baseline, reused) | linear (Boussinesq) | 6.1e-16 | 0% | 456 | **0** (reused) | zero, as before |
| SpalartAllmaras | linear (Boussinesq) | 6.6e-16 | 0% | 354 | 0.081 | zero, machine precision |
| kEpsilon | linear (Boussinesq) | 5.5e-16 | 0% | 597 | 0.133 | zero, machine precision |
| realizableKE | linear (Boussinesq)† | 9.2e-16 | 0% | 2,921 | 0.757‡ | zero, machine precision |
| kOmega | linear (Boussinesq) | 7.9e-16 | 0% | 274 | 0.077 | zero, machine precision |
| **LienCubicKE** | **NONLINEAR** (cubic) | **0.174** | **7.85%** | 4,780 | 2.201‡ | **nonzero — prediction confirmed** |

† "realizable" refers to the C_μ blending formula satisfying realizability
constraints, **not** to a nonlinear stress-strain relation — realizableKE is
still an isotropic-normal-stress Boussinesq model.
‡ Core-minutes include failed/discarded attempts, reported honestly (see
below) — not just the successful run.

**All five linear models agree to the bit** (6.1–9.2 × 10⁻¹⁶ % U_bulk —
floating-point noise, not "small"). LienCubicKE's secondary flow (0.174%
U_bulk, max 0.48%) is **~9 orders of magnitude above the linear models** —
categorically different, not a convergence artifact.

### Convergence problems encountered (reported, not hidden)

Two models — **realizableKE** and **LienCubicKE** — crashed with a
floating-point divide-by-zero inside their C_μ / near-wall-damping
calculations at iteration 1, reproducibly, from both a uniform initial
condition and a warm-started (converged SpalartAllmaras field) initial
condition. Both were recovered with a **numerics-only** fix (not a physics
tune): `FOAM_SIGFPE` trapping disabled + momentum/turbulence
under-relaxation reduced (U 0.9→0.5, k/ε 0.8→0.4).

- For **LienCubicKE**, a first recovery attempt (trap off, default
  relaxation) "completed" 2,370 iterations and passed the k/ε residual gate,
  but was **rejected as untrustworthy**: `time step continuity errors: sum
  local` exploded to ~1,200–3,000 and never decayed — ~9 orders of magnitude
  worse than every other model's ~1e-13 — a numerically corrupted, not a
  converged, solution. This run was **discarded, not reported** as a result.
  Only the reduced-relaxation run (continuity residual ~8e-4, decaying, no
  NaN/Inf in the final field) is reported above.
- realizableKE's successful run has continuity residual ~1e-13 (as clean as
  the linear models) and secondary flow at machine-precision zero, confirming
  the prediction once a trustworthy solution was obtained.
- **Core-minutes reported above include the crashed/discarded attempts**,
  not just the successful run (realizableKE: 2 crashes + 1 success =
  0.757 core-min total; LienCubicKE: 2 crashes + 1 discarded unstable run +
  1 success = 2.201 core-min total).

This is itself a reportable finding: both cubic/realizable-family nonlinear
and near-realizable models are numerically fragile on this low-Re
wall-resolved mesh with OpenFOAM v2606 default settings — a robustness
issue orthogonal to the anisotropy question this sweep set out to answer.

### Models available but not run

**ShihQuadraticKE** (same nonlinear family as LienCubicKE) and **LRR / SSG /
EBRSM** (Reynolds-stress transport models) are all compiled into this
OpenFOAM v2606 build but were **not run** this session: ShihQuadraticKE was
skipped because LienCubicKE had already confirmed the prediction; the RSMs
need a transported symmetric-tensor `R` field and new wall boundary
conditions (materially more setup than the shared k-ε-family field set used
here) and were judged not worth the added compute once the qualitative
prediction was already confirmed. **RSMs are the literature-indicated next
step for closing more of the magnitude gap** (7.85% of DNS from LienCubicKE
alone is a start, not a finish).

---

## Verdict

- **F7a (dam break): NOT APPLICABLE.** No turbulence model was active in the
  failing case (laminar VOF). Turbulence-model choice is irrelevant here —
  the gate failure is a free-surface front-tracking/interface-definition
  issue, already correctly diagnosed in the original F7 report. **0
  core-minutes** spent confirming this.
- **F6c (square duct): FIXABLE IN KIND, NOT YET IN DEGREE.** Every linear
  (Boussinesq) RAS model tested — 5 of 5, including the original kOmegaSST
  baseline — gives secondary flow at floating-point zero. This is a
  structural property of the closure class, confirmed independently across
  five different models, not a tuning or convergence artifact. Swapping to
  a **nonlinear** closure (LienCubicKE) restores a genuinely nonzero
  secondary-flow field — the qualitative fix works, cleanly, exactly as
  predicted. But it only recovers **7.85%** of the DNS magnitude, so
  LienCubicKE alone would **not** pass the original F6c gate as-is.
- **IS THIS FIXABLE BY TURBULENCE-MODEL CHOICE — YES OR NO: YES, in
  mechanism; NOT YET, in magnitude.** The structural fix is to leave the
  linear-eddy-viscosity family entirely (any of SST/SA/kε/kω is a dead end,
  proven 5-for-5). **LienCubicKE demonstrates the mechanism works.** The
  recommended next model to try for magnitude is a full Reynolds-stress
  model (**SSG** or **EBRSM**, both available in this build, neither run
  this session) — RSMs solve the individual Reynolds stresses directly and
  are the standard next step in the literature for closing more of this
  gap, likely combined with (not necessarily replaced by) the data-driven
  closure correction this campaign is otherwise pursuing.

## Compute

- **Total new compute, this task: 3.25 core-minutes** (F6c sweep only; F7a
  judgement cost 0). All serial (1 MPI rank), well inside the 2–4 rank cap.
  Run strictly sequentially, one model at a time, foreground, nothing left
  running at any point.
- Breakdown: SpalartAllmaras 0.081, kEpsilon 0.133, realizableKE 0.757
  (incl. 2 crashes), kOmega 0.077, LienCubicKE 2.201 (incl. 2 crashes + 1
  discarded unstable run). kOmegaSST baseline: 0 (reused from B2/F6c per
  instructions).

## Evidence files

- This report: `demo-output/website/campaign/RANS_MODEL_COMPARISON.md`
- Machine-readable: `demo-output/website/campaign/RANS_MODEL_COMPARISON.json`
- Case files (mesh reused, not re-run): `demo-output/website/dafoam/rans_model_comparison/{SpalartAllmaras,kEpsilon,realizableKE,kOmega,LienCubicKE}/`
- Post-processing: `demo-output/website/dafoam/rans_model_comparison/collect_results.py`,
  `sweep_results.json`
- F6c baseline (reused, not re-run): `demo-output/website/dafoam/ladder-b/duct_baseline/AR_1_Ret_360/`,
  `demo-output/website/dafoam/f6c_duct_dns/F6c_duct_vs_dns.md`
- F7a evidence (read-only, confirms laminar): `demo-output/website/campaign/F7_runs/damBreak_MM_a2p25in_medium_closedbox/constant/turbulenceProperties`
