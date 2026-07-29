# NOT_PASSING_REGISTER

**Date compiled:** 2026-07-29  
**Scope:** Every case in the lab that did not pass, did not converge, or was never finished. Read-only survey; no solvers run, no compute launched to produce this document.

**Format:** case · what it was trying to show · how it failed (exact error, residual, percentage) · is the root cause known · what it would take to resolve · where the evidence lives.

**Tone:** Register of honest failures, read as an asset. State what happened. A documented failure with a named cause is a result.

---

## GROUP 1: ADJOINT MEMORY WALL

Structural architectural block: OpenMDAO's reverse-mode sweep builds a mesh-sized `d[residuals]/d[vol_coords]` Jacobian unconditionally for any requested total derivative, regardless of the requested `wrt=` argument. This block grows with mesh size and is not escapable by mesh coarsening alone (8 independent mitigations tried and ruled out on A3: memory caps 12g/18g, rank decomposition 4/2, GMRES restart reduction, ILU fill level reduction). The working envelope on this host is approximately 10³–10⁴ cells for DAFoam adjoints; the failure boundary lies between 63,920 cells (naca0015_sail_coarse, succeeds) and 99,840 cells (A3 coarse, OOM).

**Count: 5 cases**

### A3 ONERA M6 Transonic Wing — adjoint primal blocked

- **What:** 3D transonic wing, M=0.84, Re~1.5e7, steady RANS. Primal converged (CD=0.02299556, CL=0.31311589). Adjoint intended to verify shape/patchV gradients, gate is Cp distribution vs AGARD AR-138 (not evaluated).
- **How it failed:** dRdW Jacobian-coloring construction (fine mesh, 399,360 cells) OOM'd at 12g and 18g container caps. Mesh coarsened 4x (99,840 cells): coloring succeeded but GMRES linear solve OOM'd at 8g, moved the peak one pipeline stage later at 18g (never completed linearly). Two unrelated attempts at vcoarse mesh (24,960 cells) hit SEGV during `decomposePar`.
- **Root cause:** Structural. Confirmed: OpenMDAO reverse-mode total-derivative pipeline for requested `of=CD` builds full mesh-sized Jacobian block `d[residuals]/d[vol_coords]` regardless of `wrt=` (shape, patchV, twist). Per DAJacCon.C, this block is unavoidable. No gradient verification exists for this case; none was possible.
- **To resolve:** Either (a) matrix-free adjoint via `adjUseColoring=False` (attempted on A1 at 4,032 cells: fails outright in preconditioner validation when no cached coloring file exists, and coarse/OOM cases never produce one to cache), or (b) upgrade host hardware to ≥18g sustained peak (provisional pending Options 3-5 measurement in ADJOINT_MEMORY_ENVELOPE.md), or (c) abandon transonic 3D adjoints on this architecture.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§A3, cross-rung finding 1); `ADJOINT_MEMORY_ENVELOPE.md` (Option 1-2, Options 3-5 still in flight).

### A6 CRM Wing-Body — adjoint not attempted

- **What:** 3D wing, Mach 0.850, Re matched to tutorial, steady RANS, 579,072 cells. Primal converged (CD=0.0209014, CL=0.5000146, 0.0067% from DAFoam's own published baseline).
- **How it failed:** Adjoint not attempted per explicit instruction. Mesh (579,072 cells) is 1.45x A3's already-OOM'ing fine mesh (399,360) and 5.8x A3's coarsened-but-still-failing mesh (99,840). Same structural memory wall applies.
- **Root cause:** Structural, inherited from A3.
- **To resolve:** Same as A3 (hardware, matrix-free path, or architecture change).
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§A6).

### A4 Ahmed Body — fine-mesh adjoint not attempted

- **What:** 3D Ahmed body, 25° slant, Re~2.8e6, steady RANS. Adjoint on coarse mesh (2,777 cells): CD/shape 10.04%, single scalar DV, CONDITIONAL under current grading standard.
- **How it failed:** Fine-mesh adjoint (45,760 cells for primal comparison) was deliberately never attempted. The coarse-mesh adjoint succeeded but lies at the boundary of concern; fine-mesh was gated by known OOM risk from larger predecessor cases (A3 at 399k cells).
- **Root cause:** Structural, same memory wall. Fine-mesh would likely hit it (45.76k cells is well above 63.92k working envelope but within realm of concern).
- **To resolve:** Same as A3.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§A4).

### naca0015 Sail Medium — adjoint incomplete

- **What:** 3D NACA0015 section sail, Re~6.0e6, incompressible RANS. Primal converged (CD=0.028912, CL=0.185974). Adjoint `check_totals` stage launched.
- **How it failed:** Log ends abruptly mid-Jacobian-coloring sweep ("ColorSweep: 1000, number of uncolored: 53543"), no completion message, no error/OOM message captured. 156,089 cells, consistent with memory wall between 63,920 (works) and 99,840 (fails). No FD result exists.
- **Root cause:** Highly likely OOM, pattern identical to A3, but log did not capture explicit message (per LESSONS.md L-4: absence of error message is not absence of the error; process limit hit before journald could allocate).
- **To resolve:** Hardware upgrade or matrix-free path.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§naca0015_sail_medium, cross-rung finding 1).

### naca4412 Wing Coarse — adjoint incomplete

- **What:** 3D NACA4412 wing, Re~1.0e6, incompressible RANS, 337,334 cells. Primal converged (CD=0.024906, CL=0.244554).
- **How it failed:** `compute_totals` re-ran primal (confirmed converged state), then reverse-mode sweep began. Log stops after two lines ("Computing d[CD]/d[aero_states]^T * psi 63.67 s", "Computing d[CD]/d[aero_vol_coords]^T * psi 64.58 s"), no completion, no derivatives, no error message. 337,334 cells, large-ish mesh well above working envelope. No `check_totals` or FD exists.
- **Root cause:** Highly likely OOM, same pattern as sail_medium (large mesh, process limit hit before error logged).
- **To resolve:** Hardware upgrade or matrix-free path.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§naca4412_wing_coarse, cross-rung finding 1).

## GROUP 3: SOLVER CONVERGENCE FAILURES

Cases where the solver either did not converge to its own gate, diverged during an adjoint solve, failed to complete within a session, or exhibited non-monotonic grid convergence. Includes discrete solver divergence, unsteady runs interrupted mid-window, and mesh-refinement ladders that do not asymptote.

**Count: 10 cases**

### ONERA M6 Act — primal residual plateau

- **What:** 3D transonic wing, F1, M=0.84, Re~1.5e7, 399,360 cells. Flow physics steady RANS transonic shock. 3000 iterations, 595 s.
- **How it failed:** Final residual 1.01765521962937e-06 **did not satisfy prescribed tolerance 1e-08**. Turbulence residual (nuTilda) reached ~1.0e-6 at ~25% of run, stayed fixed (factor 0.997 change over final third = genuine fixed point, not slow convergence). Every other equation satisfied: U1 6.99e-08, U2 8.99e-08, he 2.72e-7, p 3.73e-7. Only nuTilda blocking. Wall resolution straddling buffer layer: yPlus min 5.21, max 103.5, mean 33.8 (too coarse for viscous sublayer, too fine for clean wall function). DAFoam refused run at residual gate before field write; `0/` on disk, no `3000/` field. Gate not relaxed (no certification of a failed primal).
- **Root cause:** Leading hypothesis is wall resolution / turbulence treatment mismatch (yPlus buffer-layer straddling), but not tested (would require mesh with wall spacing chosen for one treatment or the other). Not a solver bug; solved every iteration given, then refused.
- **To resolve:** (a) Re-mesh with either resolved boundary layer (y+ <1) or wall-function-appropriate resolution (y+ >30), or (b) try alternative turbulence model (k-omega, realizableKE) on same mesh and see if it converges.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/A3_onera_m6_plateau.md`.

### B3 CBFS Field Inversion — adjoint DIVERGED_NANORINF

- **What:** 2D curved backward-facing step, turbulent k-omega-SST, steady RANS, 21,000 cells. Primal stage complete (U, p, k, omega all converged). Adjoint stage 3 (timed pilot): discrete-adjoint GMRES solve.
- **How it failed:** GMRES returns `PETSc KSPConvergedReason = -9` (**DIVERGED_NANORINF**) at iteration 0—NaN/Inf detected before any GMRES progress. Reproduced identically across 4 independent configurations: primal tolerances 1e-4 and 1e-6, objectives "custom field-variance loss" and "standard force/CD", ILU fill levels 1 and 4. Mesh quality independently verified (DACheckMesh: max AR 14.76, max non-orthogonality 33.3°, max skewness 0.26, all "OK").
- **Root cause:** Not identified within rung budget. Per the case's own notes, a second silent failure was found en route (DAFunctionVariance hardcodes reading reference data from folder "0" regardless of startFrom, silently producing fake all-zero objective/gradient if startFrom=latestTime). That was fixed, but the NaN/Inf persists.
- **To resolve:** (a) PETSc KSP debug output / matrix inspection (check preconditioner matrix conditioning, detect if Jacobian assembly produces inf/NaN entries), or (b) alternative preconditioner or solver family, or (c) test on a simpler 2D RANS adjoint case to isolate whether issue is k-omega-SST specific or mesh/geometry specific.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§B3, Stage 3).

### F5a Cylinder Re=2000 — incomplete, 63% of window

- **What:** 2D unsteady cylinder wake, Re=2000, intended window t=90 seconds, 2D URANS.
- **How it failed:** Run reached t=56.7 of 90 (63% complete) before host restart. Stopped mid-run. Statistics at 56.7 not gated (convergence verification requires full window). Cd_mean 1.5221, Cl_rms 1.1217, St 0.2341 recorded but not certified.
- **Root cause:** Infrastructure (host restart), not case-specific.
- **To resolve:** Resume or re-run. Re=2000 is incomplete; no result.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F5a_cylinder_reynolds_ladder.md`.

### D9 NASA Hump — three turbulence models, two incomplete / one unconverged

#### kOmega variant — unconverged

- **What:** 2D wall-mounted hump, Re_c=936k, k-omega-SST turbulence model.
- **How it failed:** Final k residual ~2.8e-6 **did not meet residual gate 5e-7**. Unconverged.
- **Root cause:** Model choice or mesh; not investigated.
- **To resolve:** Try finer mesh or alternative model (kOmegaSST already attempted; try realizableKE, SA).
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F6a_epistemic_band.md`.

#### kEpsilon variant — incomplete

- **What:** Same geometry and flow as kOmega, k-epsilon model.
- **How it failed:** Case directory exists, but no converged time directory on disk. Did not complete.
- **Root cause:** Infrastructure / process limit / timeout.
- **To resolve:** Re-run with longer time-box or larger resource allocation.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F6a_epistemic_band.md`.

#### realizableKE variant — incomplete

- **What:** Same geometry and flow as kOmega, realizableKE model.
- **How it failed:** Case directory exists, but no converged time directory on disk. Did not complete.
- **Root cause:** Infrastructure / process limit / timeout.
- **To resolve:** Re-run with longer time-box or larger resource allocation.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F6a_epistemic_band.md`.

### F7a Dam Break — front-position gate fail

- **What:** 2D free-surface unsteady transient, dam break / column collapse, inviscid treatment, VOF interface-capturing method.
- **How it failed:** Surge front position Z(T) mean deviation +13.6%, max 21.3%, monotonically diverging from reference (not oscillating around zero). Coarse mesh (dx=a/8) undershoots −13.2%, sign-flipped vs medium mesh (dx=a/20) overshoot — refinement flipped sign rather than converging, disqualifying under-resolution as sole cause (per LESSONS.md L-8 sign-flip protocol). Cause identified: VOF numerical smearing of thin, fast-moving leading edge. Leading edge not vertical at tested resolutions; single alpha=0.5 probe height at first cell above floor is not mesh-independent definition.
- **Root cause:** VOF method limitation on captured interface definition. Not a meshing issue alone; refined mesh worsened it.
- **To resolve:** (a) 3+-mesh Richardson study with isosurface-based front extraction (not single-cell-height probe), or (b) level-set or sharp-interface method.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/CAMPAIGN_STATUS.md` (§F7a). Ladder blocked at (b) Wigley hull and (c) Workshop hull per hard rule: do not start next rung until previous passes gate.

### Ahmed Body & B-52 Refinement Ladders — non-asymptotic

#### Ahmed_25 mesh ladder

- **What:** 3D Ahmed body, 25° slant, three mesh rungs (coarse 20.6k → medium 45.8k → production 79.4k cells) evaluated for grid convergence and extrapolated drag.
- **How it failed:** Cd values: 0.101 → 0.090 → 0.085. Richardson-extrapolated value falls **outside the measured range**. Ladder not in asymptotic convergence regime; no reliable extrapolation. Observed order 1.95 suggests asymptotic range not yet reached at coarse end.
- **Root cause:** Mesh rungs start in non-asymptotic regime; finer rungs needed to find Richardson plateau.
- **To resolve:** Extend ladder to finer mesh (100k–150k cells) and re-fit convergence order across fine half of ladder.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/uq-studies/ahmed_25.json`.

#### B-52 mesh ladder

- **What:** 3D B-52 geometry, six mesh rungs spanning 40.7k to 331k cells. Rungs coarse/medium used nearBody refinement level 1 (max cell level 3); intermediate/production/fine-uq/finer2 used level 2 (level 4). Only {intermediate 135.8k, production 193.9k, fine-uq 255.4k, finer2 331.0k} share same recipe and are grid-convergence-comparable.
- **How it failed:** Cd sequence (using valid family only): 0.0491 → 0.0472 → 0.0496 → 0.0523. **Successive increments GROW with refinement instead of shrinking** — oscillatory, non-monotonic. Observed order 2.25. Ladder explicitly documented as "not in the asymptotic range, conservative band, largest spread times 1.25". Non-grid-conclusive; results marked SOLVER-BACKED not VALIDATED.
- **Root cause:** Mesh rungs still in pre-asymptotic regime; oscillation suggests possible interaction between nearBody shell level 2 refinement and background blockMesh boundary-layer growth across the refinement sequence.
- **To resolve:** (a) Larger, finer meshes (500k–1M) to reach asymptotic range, or (b) controlled ablation study: fix nearBody level at 2 for all rungs and vary only background blockMesh density.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/uq-studies/b52.json`.

### naca4412 Wing Mesh Ladder — non-monotonic

- **What:** 3D cambered wing NACA4412, resolved boundary layers, three mesh rungs (medium 263.4k → fine 645.3k → finer 1.85M cells).
- **How it failed:** Cd sequence: 0.0245 → 0.0183 → 0.0183. Cd drops 25% (medium→fine), then plateaus <1% (fine→finer). Cl swings back up 19% (fine→finer: 0.2095 → 0.2502). Finer rung fails mesh-quality gates (non-orthogonality 74.96° exceeds 70° limit) and degrades boundary-layer coverage (58.3% vs 94% on other rungs) — finer mesh is worse, not better. Fine rung (645k cells) passes both mesh gates and is graded; non-asymptotic ladder not grid-conclusive per Richardson. No observed-order fit on non-asymptotic data.
- **Root cause:** Finer mesh-generation recipe breakdown; castellated-level interaction (per LESSONS.md / naca4412_credential_repair.py notes). Not a solver issue; the meshes themselves diverged from monotonicity criterion.
- **To resolve:** (a) Revert finer rung to same mesh recipe as fine rung (no castellated-level jump), or (b) revert fine and finer to medium's recipe and re-run, or (c) accept fine rung as the final grid and report "grid convergence attempted but non-monotonic; results flagged SOLVER-BACKED".
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/naca4412_wing.json` (full grid_study section with all three rungs and mesh-quality details).

---

## GROUP 2: GRADIENT-ACCURACY DEFECTS

Cases where the discrete adjoint disagrees with finite-difference verification, with sign-flipped or unstable components. These are not solver failures; the adjoint converges. The disagreement is real, reproduced across multiple step sizes, and the root cause is not yet identified.

**Count: 2 cases**

### A1 NACA0012 Incompressible Airfoil — shape-derivative sign flip

- **What:** 2D NACA0012, Re~6.7e5, incompressible, steady RANS, 4,032 cells. Primal converged (CD=0.0209105, CL=0.4987653, residual 9.646e-09). Adjoint converged (GMRES 164/165 iterations, PetscConvergedReason: 2). FD verification intended across 8 FFD shape components.
- **How it failed:** FD verification CD/shape shows 11.43% aggregate error. Per-component breakdown (A_stepsize_study.md, cost-free step-size sweep 1e-8 to 1e-1): idx0 and idx1 (interior LE-adjacent stations) stable 9–16% disagreement across 3 decades of step size (not shrinking with step, so not roundoff-dominated). idx6 (leading-edge combo mode) **sign-flipped and confirmed real** (not FD artifact; verified via independent higher-precision run in PROOF.md). Stable FD plateau exists (2.5–3% for well-behaved components, cosine similarity 0.99998), but adjoint sits outside plateau for idx0, idx1, idx6. idx6 alone accounts for 82.7% of squared-error norm, reproducing PROOF.md's independent calculation to 4–5 sig figs.
- **Root cause:** Unknown. Candidates ruled out: under-iteration of primal (converged at 1e-9), frozen-wall-distance mechanism (measured direct y_wall perturbation across 500x shape range, confirmed zero change), step-size/roundoff issues (FD plateau is clean and stable; adjoint sits outside it). Leading edge mesh refinement (3.65x) did not shrink disagreement; error survives/worsens. Mechanism remains unidentified.
- **To resolve:** (a) Localized mesh refinement at LE or (b) independent adjoint implementation / automatic differentiation verification or (c) DAFoam source-level audit of LE-adjacent shape-derivative chain (FFD→mesh→residual Jacobian).
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§A1, cross-rung findings 1-2); `demo-output/website/dafoam/PROOF.md`; `demo-output/website/dafoam/ACTIVE_RESEARCH.md` (FD table, cross-rung analysis).

### A5 U-Bend Channel — pressure-loss multi-component sign flip

- **What:** Internal 3D half-channel, turbulent (SA), steady RANS, 4,800 cells. Primal plateaus at genuine fixed point (p residual 2.26e-4, not under-iteration; tightening tolerances and extending iterations 1000→5000→10000 produced bit-identical residuals). Objective pressure loss TP1−TP2 stable 5–8 sig figs. Adjoint converged (GMRES 86 iterations, PetscConvergedReason: 2). FD verification across 27 shape components.
- **How it failed:** FD aggregate 46.6% (well above 15% FAIL threshold). 2 of 27 components **sign-flipped** (idx 8, idx 17). Only 5/27 within the old 12% tolerant band. Step-size diagnostic on idx0 ruled out "needs bigger step" (FD did not converge toward adjoint as step grew 1e-4→1e-2). Follow-on test: tightening primal convergence (residualControl, solver tolerances, endTime 1000→10000) made aggregate error and sign-flip count **worse** (46.64%→46.21% aggregate, 5/27 within band→4/27, sign flips 2→3). The primal plateau is a genuine fixed point of the curved duct's secondary-flow structure, not resolvable by iteration budget alone.
- **Root cause:** Unknown. The curved duct's secondary-flow physics may be unresolvable on a coarse steady solve (primal plateau ~10,000 iterations suggests the iteration space has exhausted). Possible: (a) mesh too coarse to resolve Prandtl secondary-flow structures that the objective gradient depends on, or (b) steady-RANS-specific deficiency in adjoint linearization of secondary flows.
- **To resolve:** (a) Mesh refinement in duct-corner/secondary-flow regions and re-run full FD sweep or (b) adjoint verification on a different 3D duct case with resolved secondary flow or (c) switched to time-averaged unsteady RANS to resolve secondary-flow transients.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§A5); `demo-output/website/dafoam/ACTIVE_RESEARCH.md`.

---

## GROUP 4: REFERENCE/REGIME MISMATCHES

Cases where the CFD result lies in a different physical regime than the reference data, or the comparison basis is not equivalent (e.g., section data vs. finite wing). The solver converged and produced a result, but the result is incomparable to the reference used for validation.

**Count: 3 cases**

### Sphere — supercritical vs subcritical regime mismatch

- **What:** Curriculum validation case, sphere drag coefficient, frontal-area basis.
- **How it failed:** Cd measured 0.0948. Reference Cd 0.47 (Achenbach 1972 / Schlichting, subcritical branch: laminar separation, wide wake). Measured value Cd ~0.09 matches **supercritical regime** (post-drag-crisis, Achenbach supercritical branch Cd 0.07–0.10), not subcritical. Relative error 79.8%.
- **Root cause:** Physics regime mismatch. Steady fully-turbulent RANS delays boundary-layer separation and reproduces the post-drag-crisis wake, so the coefficient reads supercritical even when the solve Reynolds number is nominally subcritical. Not a solver defect; the model has chosen the wrong branch of the drag-coefficient curve.
- **To resolve:** (a) Run at a Reynolds number firmly in supercritical regime (Re > 5e5), or (b) switch to time-resolved unsteady or LES to capture laminar-separation physics, or (c) accept as a documented regime mismatch and do not claim validation against subcritical reference.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/sphere.json` (tier: REFERENCE REGIME MISMATCH).

### Cylinder — supercritical vs subcritical regime mismatch

- **What:** Curriculum validation case, finite cylinder in crossflow, frontal-area basis.
- **How it failed:** Cd measured 0.546. Reference Cd 0.74 (Hoerner 1965, Ch. 3, subcritical branch: crossflow, free-end relief). Measured value Cd ~0.55 matches **supercritical / fully-turbulent regime** (Hoerner supercritical branch Cd ~0.5), not subcritical. Relative error 26.2%.
- **Root cause:** Physics regime mismatch, identical mechanism to sphere. Steady fully-turbulent RANS under-predicts subcritical base drag, landing near supercritical branch rather than subcritical reference.
- **To resolve:** Same as sphere: (a) confirm Reynolds number regime, (b) unsteady/LES for laminar regime, or (c) document mismatch.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/cylinder.json` (tier: REFERENCE REGIME MISMATCH).

### NACA0012 Wing — section data vs. finite-wing comparison

- **What:** Curriculum validation case, full 3D NACA0012 wing (wing alone, span finite).
- **How it failed:** Cd measured 0.02229. Reference Cd 0.009 (Abbott & von Doenhoff 1959, NACA 0012 section airfoil, presumably steady 2D). Measured value 148% above reference, **outside ±30% tolerance band**. Tier: TREND ONLY (not validated).
- **Root cause:** Comparison basis mismatch, not regime. Reference is 2D section data (infinite span, inviscid/2D theory assumed). Measurement is 3D wing with finite aspect ratio, wall effects, and induced drag. Three-dimensional finite-wing Cd is expected to be 2–3x the 2D section value due to induced drag and Reynolds-number dependence. Comparing directly is not valid.
- **To resolve:** (a) Derive 3D finite-wing reference as Cd_section + Cd_induced (Cl²/(π·e·AR)) using solver-measured Cl and wing aspect ratio, or (b) use published 3D NACA0012 wing data at matched Re/span/condition instead of section data.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/naca0012_wing.json` (tier: TREND ONLY; reason cites 148% vs ±30% band).

---

## GROUP 5: NEVER RUN OR INCOMPLETE

Cases where the case was set up but never executed, or intermediate stages were not completed.

**Count: 1 case**

### naca0015 Sail Full — scaffolding only, never run

- **What:** 3D NACA0015 sail geometry, intended for incompressible RANS.
- **How it failed:** Case files exist (Allclean.sh, preProcessing.sh, runScript.py, 0.orig/, FFD/, constant/, system/), but **no run logs of any kind exist in this directory**—no logMeshCheck.txt, no runmodel logs, no compute_totals/check_totals logs. This case was set up but never run. No mesh count, no primal, no adjoint, nothing to report beyond scaffolding present.
- **Root cause:** Not executed (intention unclear; possible out-of-scope, deprioritized, or time-boxed away).
- **To resolve:** Run the case (full ladder: coarse → medium → fine) if in-scope, or remove from repository if not.
- **Evidence:** Directory `/home/ubuntu/Certonomous/demo-output/website/dafoam/ladder-a/work_sail/naca0015_sail_full/` contains setup but no logs.

---

## Summary by Group

| Group | Count | Description |
| --- | --- | --- |
| 1. Adjoint memory wall | 5 | Structural OpenMDAO reverse-mode Jacobian-size blocker; working envelope ~10k cells |
| 2. Gradient-accuracy defects | 2 | Sign-flipped or unstable adjoint-vs-FD disagreement, root cause unidentified |
| 3. Solver convergence failures | 10 | Unconverged primal, diverged adjoint, interrupted unsteady, non-asymptotic mesh ladders |
| 4. Reference/regime mismatches | 3 | RANS chose wrong physics branch, or comparison basis not equivalent |
| 5. Never run or incomplete | 1 | Scaffolding only, never executed |
| **TOTAL** | **21** | |

---

## Cases Resolved and Not Included

The following cases ran, converged, and were validated or documented as intended, so they are NOT in this register:

- **A2 MACH Tutorial Wing**: PASS, 1.71%–1.17% across shape/twist/patchV derivatives.
- **naca0015 Sail Coarse**: PASS, 4.52% shape derivative, no sign flips.
- **F3 Supersonic Exact-Theory (wedge/cone/diamond)**: All gates PASS, 0.01–2.1% accuracy.
- **F5a Cylinder Re=100**: PASS, Strouhal 0.1578 vs 0.1589 reference, 0.77%.
- **F6a NASA Hump**: GATE REACHED, reattachment +13.95% contained by model-form epistemic band (expected SST bias).
- **F6c Duct secondary flow**: GATE FAIL documented and shipped as structural linear-eddy-viscosity deficiency (RANS cannot produce Prandtl secondary flow by design).
- **Nine-Act validation suite**: 8 of 9 acts PASS (cylinder, wedge, cone, diamond, ahmed, hump, CRM). ONERA M6 primal alone UNCONVERGED (included in Group 3).
- **Curriculum mesh ladders (validated cases)**: ahmed_25, flat_plate, cube all VALIDATED within their reference bands.

