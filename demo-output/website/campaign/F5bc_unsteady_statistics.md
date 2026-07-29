# F5b/F5c — Unsteady-Statistics Campaign Families

**Date:** 2026-07-29
**Scope:** Two of the six previously-unstarted priority families. F5c (backward-facing step) run first per instructions (steady-capable, cheaper, unambiguous gate). F5b (pitching-airfoil dynamic stall) run second (genuinely unsteady, moving mesh).

**Compute packing:** all runs single-rank (serial), 2D, modest meshes (2.4k–46.5k cells), sharing the box with a running mega-batch and three other agents. No run used more than 1 core; the 2–4 MPI-rank cap was never needed because these 2D meshes were cheap enough serially. MemAvailable checked before each heavy stage (28–29 GiB free throughout; never came close to the 6 GiB floor).

---

## F5c — Backward-Facing Step (Driver & Seegmiller 1985)

### Reference
Driver, D. M. and Seegmiller, H. L., "Features of a Reattaching Turbulent Shear Layer in Divergent Channel Flow," *AIAA Journal*, Vol. 23, No. 2, Feb. 1985, pp. 163–171. DOI: [10.2514/3.8890](https://doi.org/10.2514/3.8890). Case parameters retrieved from the primary source via the NASA Turbulence Modeling Resource mirror (tmbwg.github.io/turbmodels/backstep_val.html) and cross-checked against a second independent source describing the facility geometry, both fetched 2026-07-28/29.

**Exact published parameters used (not the task brief's rounded "~6.1" / "Re≈37,500"):**
- Expansion ratio (Y₀+H)/Y₀ = 1.125, i.e. upstream channel height Y₀ = 8H, downstream channel height 9H
- Re_H (step-height Reynolds number, reference velocity measured at x/H=−4 centerline) ≈ **36,000**
- Re_θ (inlet momentum-thickness Reynolds number) = 5,000
- Inlet boundary-layer thickness at x/H=−4: δ ≈ 1.5H
- Reference Mach number ≈ 0.128 (effectively incompressible)
- Facility: 1.0 m duct × 0.151 m wide × 0.101 m tall inlet section, 0.0127 m step (span/H ≈ 12, minimizing 3D corner effects — not eliminating them)
- **Measured reattachment length: x_r/H = 6.26 ± 0.10**

### Geometry / mesh
5→7-block structured hex, H=1 nondimensional. x ∈ [−4H, 0]: upstream channel (y ∈ [H,9H]). x ∈ [0,30H]: downstream channel (y ∈ [0,9H]), split at x=10H into near/far x-regions and at y=0.5H into two y-sub-blocks (see lesson below). Fully axis-aligned rectangular blocks → mesh non-orthogonality = 0 exactly (checkMesh confirms); only high aspect ratio near the wall (expected, unflagged as a real defect). Wall-normal first cell 4×10⁻⁴H (target y+<1, low-Re treatment on bottomWallUpstream/stepFace/bottomWallDownstream).

Inlet: 1/7-power-law turbulent boundary-layer profile (U=0 at y=H, U=U_ref for y−H≥1.5H) imposed via `codedFixedValue` exactly at x=−4H — the paper's own Uref reference station — rather than an assumed long development length. Freestream turbulence intensity/eddy-viscosity ratio are NOT published in the retrieved source; Tu=2%, μt/μ=10 used as a documented assumption (tested down to Tu=0.5%/ratio=1 with no material change — see diagnostics below).

Solver: `simpleFoam` (incompressible, steady RANS), kOmegaSST.

### Rungs reached: FEASIBILITY only. PHYSICS not established. GATE NOT REACHED.

**Feasibility — PASS.** Mesh builds cleanly at all tested levels (coarse 9,050 cells, medium 20,160 cells); checkMesh: 0 non-orthogonality, 0 skewness, only the expected high-aspect-ratio near-wall cells flagged (normal for a resolved boundary layer, not a defect). Solver runs to deep numerical convergence (p, U, k, omega residuals 10⁻⁵–10⁻⁹) at every configuration tested.

**Physics — NOT ESTABLISHED.** The qualitative separation signature is right at the corner (wall shear turns negative immediately downstream of the step, as expected), but the reattachment length is **not robust**: across six independent numerical configurations it lands in the range **0.5–1.5H**, roughly a factor of 4–12 short of the 6.26H reference — far beyond the ~15–20% under-prediction the task brief itself anticipated as the documented linear-eddy-viscosity deficiency. Every configuration also shows a **second, unexplained separation** re-appearing around x/H≈6–8 and persisting (with the sign of reversed flow) all the way to the domain exit at x=30H — a feature with no counterpart in the reference and not resolved within this session's budget.

### Diagnostics performed (each independently tested, each ruled out or found insufficient)

| # | Hypothesis tested | Test | Result |
|---|---|---|---|
| 1 | Mesh resolution | Coarse (9,050 cells) vs. medium (20,160 cells), same algorithm | x_r/H = 0.56 vs. 0.49 — consistent with each other, both wrong. **Ruled out as a resolution artifact.** |
| 2 | Shear-layer under-resolution at the step lip | Redesigned the y<H mesh from a single wall-clustered block to two fine-at-both-ends sub-blocks (5→7 blocks) | Grading quality fixed (per-cell ratios 1.08–1.24 everywhere), but x_r/H moved only 0.68→0.56 — same order. **Real defect, fixed, but not the dominant cause.** |
| 3 | Top-wall near-wall treatment (low-Re wall function misapplied at y+≈140, well outside validity) | Re-ran with topWall as slip | Crossing pattern essentially unchanged (reattach ≈0.5–1.4H, second separation ≈6H either way). **Ruled out.** |
| 4 | SIMPLE algorithm / relaxation | Plain SIMPLE (relax p=0.15, U=0.4) → 0.56–0.68H. SIMPLEC (consistent=yes, relax p=0.3, U=0.6) → 1.07–1.49H, **non-monotonic with iteration count** (2,000 iters: 1.49H; 8,000 iters: 1.07H) | SIMPLEC moved the number substantially (confirms algorithm/relaxation matters) but did not converge toward 6.26H as iterations increased — it wandered. **Not a simple convergence issue; suggestive of genuine low-frequency bubble-flapping unsteadiness (well documented in the BFS literature, e.g. Eaton & Johnston 1981; Kaltenbach et al. 1994 LES) that a fixed-point steady solve cannot represent**, forcing the algorithm onto different quasi-steady branches depending on path. |
| 5 | Freestream turbulence assumption | Tu=2%/μt/μ=10 vs. Tu=0.5%/μt/μ=1 | Crossing locations unchanged to within 0.1H. **Ruled out.** |

### Verdict
**GATE NOT REACHED — reported as a documented, unresolved finding, not a shipped result**, per the campaign's hard rule against shipping a failed gate as a pass. This is a genuinely different (and more severe) failure mode than the one the task brief anticipated ("linear eddy-viscosity RANS under-predicts, landing near 5–6H"): the deviation here is 4–12×, not 15–20%, and it does not converge under mesh refinement, wall-treatment correction, or algorithm change — it wanders. The leading remaining hypothesis (not tested within this session's budget) is that this specific case exhibits real low-frequency unsteadiness that needs an unsteady (pimpleFoam, time-averaged) solve rather than steady SIMPLE/SIMPLEC; a second candidate is the imposed *uniform* k/omega inlet profile (vs. a real turbulent boundary layer's near-wall TKE peak), which was never itself varied in shape, only in bulk level.

### Pressure-recovery distribution
Recorded (bottomWallDownstream Cp vs x/H) in `F5c_runs/*/pressure_profile.json` for every run; not reported as a validated result above given the reattachment-length finding — a pressure-recovery curve anchored to a wrong recirculation length would misrepresent the case. Available for inspection but explicitly not claimed as validated physics.

### Evidence record

| Rung | Config (mesh, algorithm) | Config hash | Cells | Iterations | Wall-time (s) | Core-min | x_r/H | Ref | Deviation |
|---|---|---|---|---|---|---|---|---|---|
| Feasibility/Physics | coarse, plain SIMPLE (relax p=0.15,U=0.4) | d64e08b4826f | 9,050 | 2,000 | 115.3 | 1.92 | 0.558 | 6.26±0.10 | −91.1% |
| Physics (mesh check) | medium, plain SIMPLE | 1d6e0c8ccfa7 | 20,160 | 3,500 | 418.3 | 6.97 | 0.492 | 6.26±0.10 | −92.1% |
| Diagnostic (algorithm) | coarse, SIMPLEC (relax p=0.3,U=0.6) | d64e08b4826f | 9,050 | 2,000 | 142.6 | 2.38 | 1.486 | 6.26±0.10 | −76.3% |
| Diagnostic (iteration count) | coarse, SIMPLEC | d64e08b4826f | 9,050 | 8,000 | 672.4 | 11.21 | 1.067 | 6.26±0.10 | −83.0% |
| Diagnostic (turbulence level) | coarse, SIMPLEC, Tu=0.5%/ratio=1 | d64e08b4826f | 9,050 | ~4,700 (residual-flat) | 154.7 | 2.58 | ~1.44 (crossing) | 6.26±0.10 | ~−77% |
| Diagnostic (top-wall BC) | coarse, SIMPLEC, slip top wall | d64e08b4826f | 9,050 | 2,000 | 110.7 | 1.85 | ~0.5 / second-sep ~6H | 6.26±0.10 | ~−92% |

**F5c total: 1,614 core-seconds = 26.9 core-minutes across 6 runs.**

**Lesson:** For a validation case this well-studied, a "gate value that won't converge under refinement, wall-treatment, or algorithm change" is itself the finding — it means the steady-RANS fixed-point assumption is the thing being violated, not the mesh or the closure constant. Worth carrying forward: try pimpleFoam + time-averaging on this exact case before spending more budget on steady-solver algorithm tuning.

---

## F5b — Pitching NACA 0012 Dynamic Stall

### Reference
McAlister, K. W., Carr, L. W., McCroskey, W. J., "Dynamic Stall Experiments on the NACA 0012 Airfoil," NASA TP-1100, January 1978 (NTRS 19780009057). Downloaded and parsed directly (OCR text of the primary source, not a secondary citation).

**Case gated against — their case "(e)", confirmed verbatim from the primary source:**
- α(t) = 15° + 10°·sin(ωt) (mean 15°, amplitude 10°)
- Reduced frequency k = ωc/(2U) = **0.15**
- Reynolds number Re = **2.5×10⁶** (held fixed across their whole test matrix, per their own Conclusions section: "...for the NACA 0012 airfoil at a Reynolds number of 2.5×10⁶")
- Mach number M ≈ 0.09 (low speed; run here as incompressible)
- Pitch axis: **quarter chord** (stated repeatedly — "pitched about its quarter-chord axis")
- Rig: chord 1.22 m, span 1.98 m → aspect ratio 1.62, chord/tunnel-width ratio 0.4 — the paper itself documents measurable 3D end effects and tested end plates to partially correct them.

**What TP-1100 does NOT give:** a digitized, machine-readable CL(α) time series for case (e). Its dynamic-stall results are scanned strip-chart figures (CN, CC, CM vs. time/azimuth), not tabulated numbers, for every (mean angle, amplitude, k) combination. The report's SUMMARY/CONCLUSIONS give only report-**wide** extreme bounds across the *entire* test matrix ("stall may be delayed by as much as Δ(ωt)=π/2 with loads reaching C_p=−30, C_L=3.5, C_D=1.5, C_M=−0.75") — not numbers specific to case (e). **Per the task's explicit fallback, this is reported as a computed hysteresis loop compared to TP-1100 only qualitatively — loop topology, delayed stall relative to the static value, and order-of-magnitude peak lift against the report-wide bound — not as a point-match quantitative gate**, because no citable phase-resolved point data for this exact case was found.

### Mesh / motion
Reuses `workflows.transonic_airfoil.transonic_blockmesh_dict` **unmodified** — the same analytic-NACA0012 C-grid O-topology already proven for the F2 transonic case — at 25-chord farfield, 25-chord wake, 8×10⁻⁶-chord first cell. Chosen over building a new AMI/rotating-zone mesh because it required no new topology.

**Motion: whole-mesh rigid rotation, not an AMI zone.** OpenFOAM's `dynamicMotionSolverFvMesh` + `motionSolver solidBody` + `solidBodyMotionFunction oscillatingRotatingMotion` rotates the *entire* mesh (no cellZone) about the quarter chord — chosen over pimpleDyMFoam-with-AMI because the farfield boundary sits 25 chords away in every direction, so its physical displacement under a ±10° rotation about a point 0.25c away is geometrically negligible relative to that standoff; the `freestreamVelocity`/`freestreamPressure` BC (fixed in the lab frame, not mesh-attached) stays valid throughout. The **mean** 15° incidence is realized by fixing the freestream velocity vector at 15° (not by mesh rotation); only the **±10° oscillation** is mesh motion — so net instantaneous incidence in the lab frame is exactly 15+10sin(ωt), matching the reference case.

Solver: `pimpleFoam` (incompressible, moving mesh), kOmegaSST. Re=2.5×10⁶ realized via ν=U·c/Re=4×10⁻⁷.

### Two real bugs found and fixed while building this case (documented, not hidden)
1. **`Entry 'pcorr' not found`** — pimpleFoam's moving-mesh flux correction needs its own `pcorr`/`pcorrFinal` solver block; the F5a cylinder's static-mesh `pimple_fv_solution()` never needed one. Added locally.
2. **Impulsive-start divergence** (CL momentarily reported in the tens of thousands over the first ~15 timesteps) — the same C-grid topology's extreme near-wall aspect ratio was already documented (F2 module) to diverge on an impulsive uniform start. Fixed by running `potentialFoam -writephi` before the PIMPLE march (irrotational field consistent with the t=0 incidence, since sin(0)=0 means α(0)=15°=α_mean exactly). After this fix, the same transient spike still appears in the raw Cl(t) signal for the first ~0.02 time units (a well-known, physically expected pressure-adjustment transient from any impulsive-like viscous start, not a divergence) and decays to physically sane values (Cl≈0.8 by t=1, α≈18°) — this transient window is excluded from all reported statistics below.

### Rungs

**Feasibility — PASS.** Coarse mesh (3,584 cells), t=0–1 (0.05 periods): mesh moves correctly under the prescribed rotation, solver survives the impulsive-start transient (after the potentialFoam fix), Courant number self-regulates to ~1.0 within ~20 steps and stays there, Cl settles to a physically plausible value (~0.8 at α≈18°, pre-stall). 1,473 steps, 85.1 s wall (coarse mesh, single core).

**Physics —** *[to be completed once the in-progress one-period run finishes; see below]*

**Gate —** *[qualitative comparison only, per the fallback above; to be completed]*

### Compute-cost comparison (unsteady vs. steady, comparable resolution)
F5b's coarse mesh (3,584 cells) is *smaller* than F5c's coarse mesh (9,050 cells), yet the unsteady pitching run to one period is running roughly **15–25× longer in wall-time** than the comparable steady BFS coarse run (115 s), driven entirely by the number of time steps needed to resolve the prescribed motion at a Courant-limited Δt — not by cell count. This is a direct, load-bearing answer to the owner's compute-cost question and is elaborated with final numbers below.

*(Section continues below once the physics/gate rungs are complete.)*
