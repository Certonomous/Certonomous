# DAFoam case status — every case run so far

Date compiled: 2026-07-28. Read-only survey; no solvers run, no compute launched to
produce this document. Sources: `ladder-a/` (A1–A6 + `A_stepsize_study`), `ladder-b/`
(B1–B3), `PROOF.md` (prior-session root-cause work on A1's shape derivatives),
`ACTIVE_RESEARCH.md` (consolidated FD table / cross-rung findings), and `work_sail/` +
`work_wing/` (pre-ladder cases from before the ladder was formalised).

**Current FD grading standard (applied uniformly below, including to cases graded under
the old band):** PASS at ≤5% aggregate **and** no flagged component; CONDITIONAL 5–15%;
FAIL above 15% **or** any sign-flipped/unstable component regardless of aggregate. The
earlier "1–12% is normal" band (inferred from A1 alone) is retired.

---

## Ladder A — DAFoam verification/reproduction ladder

### A1 — NACA0012 incompressible airfoil (official DAFoam tutorial)
- Re ≈ 6.7×10⁵ (U0=10 m/s, chord=1.0 m, ν=1.5e-5 m²/s — computed from the case's own stated values, not printed directly). Incompressible, low-speed, turbulent (Spalart-Allmaras), wall-function RANS. **Steady. 2D** (extruded 1-cell-thick). Solver `DASimpleFoam`.
- Mesh: 4,032 cells. Cost: **3.51 core-min** total (mesh 0.08, `compute_totals` 1.30, `check_totals` run1 FAILED (stale-processor trap) 0.33, `check_totals` run2 accepted 1.80).
- Primal: converged, residual 9.646e-09 vs 1e-8 tolerance. CD=0.0209105, CL=0.4987653.
- Adjoint: attempted, GMRES/PETSc converged (164/165 iterations, `PetscConvergedReason: 2`).
- FD verification (step=1e-3, central): CD/patchV 0.23% — **PASS**. CL/patchV 0.23% — **PASS**. CL/shape 1.67% — **PASS**. Geometric constraints wrt shape 4e-14–1e-10 — **PASS** (machine precision). **CD/shape 11.43% aggregate, but per-component: idx6 (LE combo mode) is sign-flipped and confirmed real** (not an FD artifact — see cross-rung finding 2 below, and `PROOF.md` §8.2/§12). **Verdict on CD/shape: FAIL** under the current standard (sign-flipped component overrides the 5–15%-would-be-CONDITIONAL aggregate). idx0/idx1 (interior LE-adjacent stations) also carry a real, step-independent 9–16% error each. idx2,3,4,5,7 (mid-chord/aft/TE) agree to 1.5–6.4% and are not in question.
- This is the most deeply investigated case in the ladder: `PROOF.md` (prior session) traced the defect to the leading edge via mesh refinement (3.65x, disagreement survives/worsens) and ruled out the frozen-wall-distance mechanism as the cause (confirmed to exist, but measured to contribute exactly zero to either the adjoint or the FD estimate). A 2026-07-29 session (`PROOF.md` §13) tested and killed a fourth candidate: a discrete wall-function branch-crossing mechanism (SA wall-treatment's `max(0, ...)` clip on `nutw`, the only genuine hard branch in DAFoam's actual differentiated `nutUSpaldingWallFunctionFvPatchScalarFieldDF` source). Direct measurement of the converged wing-patch `nutw` array at baseline and at idx6/idx4 ±1e-4 (5 fresh single-shot processes, off-disk field read, cross-validated to reproduce the case's own established idx6/idx4 FD values) found **zero branch crossings for idx6 and zero for the idx4 control** — every wall face, at every configuration, sits ~400x above the clip floor and moves by well under 0.2% under the perturbation. Prediction did not hold; mechanism refuted, not just unconfirmed. The same session then tested a fifth candidate (`PROOF.md` §14): idx6's FFD combo-mode (opposite-direction LE/mirror-point motion) pinching leading-edge cells asymmetrically between the plus and minus FD evaluations. Reused the same 5 configurations; measured LE-localized wall-adjacent cell volumes (`postProcess -func writeCellVolumes` + owner-cell mapping, indexed identically to the `nutw` array) and DAFoam's own `DACheckMesh` global report. idx6 does visibly move LE cells more than idx4 (trivially — idx6 is the LE mode, idx4 is not), but that motion is clean, linear, and antisymmetric between plus/minus to **0.013%** (idx6, at the LE) vs. **0.048%** (idx4, at its own station) — idx6's own response is *more* symmetric, not less. No cell volume anywhere in any of the 5 configurations goes negative or near-zero (minimum 2.254e-07 across all configs, stable to 6 significant figures under perturbation). `DACheckMesh` reports "Mesh OK" at all 5. Both remaining named candidates (combo-mode pinching, and negative/near-degenerate LE cell volumes under perturbation) are refuted by this same measurement — not merely untested. **Root cause identified after six refuted mechanisms** (FD/tolerance noise, FFD/DVGeo Jacobian convention, coarse-mesh discretization, frozen wall-distance, wall-function branch-crossing, combo-mode mesh pinching) **and a seventh, confirmed** (`PROOF.md` §15): every mechanism through the sixth assumed the adjoint was clean and something was corrupting the finite-difference check; this one inverts that. DAFoam's real adjoint gets its mesh sensitivity from exactly one call, `mesh.warpDeriv` (`DAFoamWarper.compute_jacvec_product`, confirmed `useAD.mode="reverse"` is this case's default and is never overridden), while `check_totals`' finite difference never touches that function at all — it just re-warps the mesh at `shape±h` and differences the result. Tested `warpDeriv` directly against a finite difference of the actual warp via the standard adjoint/dot-product identity (`work/NACA0012_Airfoil_Incompressible/probeWarpDeriv.py`, no CFD, pure `DVGeo`+IDWarp geometry), for idx6 and idx4, across 2 random seeds, 2 step sizes, both serial and the trusted 4-rank parallel configuration (8 valid runs total; one early parallel attempt was discarded after being caught as invalid — an `mpirun -np 3` vs. a 4-way-fixed `decomposeParDict` mismatch). **idx4 (control) agrees to 0.1–2.4% in every configuration, sign always correct. idx6 (suspect) disagrees by 108–149% and is SIGN-FLIPPED (FD positive, `warpDeriv` negative) in every one of 4 independent configurations.** Step-independence is exact in the strongest sense available: `warpDeriv`'s output is bit-identical across step sizes (it is a single analytic evaluation, not an FD), and the FD side itself barely moves (0.01% over a full decade of h) — so the disagreement is a fixed gap between two converged numbers, not a resolution artifact. This triangulates with, not against, sections 13–14: those sections already showed idx6's actual warped mesh (what the FD side is built from) is smooth, clean, and non-degenerate — consistent with the warp being fine and only its own linearization (`warpDeriv`, separate code) being wrong. **Verdict: the finite-difference check_totals result for idx6 was right; the discrete adjoint was wrong.** Not yet established: why `warpDeriv` misbehaves specifically for a combination mode and not single-station modes (not traced into IDWarp source), and whether idx0/idx1 share this same mechanism (not tested, scoped to idx6/idx4 only per instruction).

### A2 — MACH Tutorial Wing, aero-only variant (deviation disclosed: docs page shows only the aerostructural script; the repo's own aero-only `runScript_AeroOnly.py` was used instead)
- Mach ≈0.3, Re ≈30×10⁶ (per the tutorial's own spec page). Compressible, transonic-adjacent, turbulent (SA), wall-function RANS. **Steady. 3D** wing. Solver `DARhoSimpleFoam`.
- Mesh: 38,304 cells. Cost: **692.5 core-min total** (485.3 useful + 207.1 wasted on a failed attempt).
- Primal: converged, CD=0.02772949, CL=0.4775878, stable to 8+ sig figs.
- Adjoint: attempted, `compute_totals` OK (32.7 core-min). First `check_totals` attempt **FAILED** — OOM-killed by a cgroup memory cap during host contention, then the host itself rebooted mid-run (infrastructure failure, not a gradient issue; 207.1 core-min lost, no partial FD table recoverable). Second attempt succeeded (210.2 core-min).
- FD verification (105 DVs: 96 shape + 7 twist + 2 patchV): CD/shape 1.71%, CL/shape 1.17%, CD/twist 0.39%, CL/twist 1.12%, CD/patchV 0.02%, CL/patchV 0.0015%, all geometric constraints at machine precision. **No flagged/sign-flipped components. Verdict: PASS**, comfortably.
- Follow-on: `run_driver` (IPOPT) optimization time-boxed to 60 min, terminated cleanly mid-run (not converged to IPOPT's own tolerance). 47 major iterations, **28.3% drag reduction at matched CL=0.5**, reported as an honest partial/time-boxed result.

### A3 — ONERA M6 transonic wing
- Flow condition deliberately changed from the tutorial default (disclosed): U0 285→291.6 m/s, aoa 2.75°→3.06°, to match the citable AGARD/NASA-TMR Case 2308 validation target (M=0.84, α=3.06°). Achieved M_inf=0.839968. Re ≈1.5×10⁷ (from the tutorial's stock viscosity; ~28% above the experimental Re=11.72×10⁶, not corrected, flagged as secondary). Compressible, transonic, shock-containing, turbulent (SA), wall-function RANS. **Steady. 3D** wing. Solver `DARhoSimpleCFoam`.
- Mesh: 399,360 cells (fine, for the primal/Cp comparison). Cost through 3 primal attempts: ~127.5 core-min (1 FAILED against DAFoam's own relaxed gate, 1 passed the relaxed gate, 1 accepted).
- Primal: **accepted** — CD=0.02299556, CL=0.31311589. Strict `primalMaxRes<1e-8` message never printed (shock cells never reach machine-zero residual — textbook behavior for this case class, not treated as non-convergence).
- Cp validated against AGARD AR-138/NASA-TMR Case 2308 (public reference data fetched, not invented): pressure surface RMS 0.013–0.027, suction surface (shock-carrying) RMS 0.049–0.114; CFD shock sits aft of experiment by 0.02–0.10 x/c at 6 of 7 span stations — attributed to numerical/mesh diffusion on a modest 399k-cell mesh, not a solver defect.
- **Adjoint: BLOCKED — this is the case named explicitly in the brief.** Failure mode, precisely: 8 independent mitigations tried and ruled out across fine (399,360 cells), coarse (99,840 cells), and vcoarse (24,960 cells) meshes — 12g/18g container memory caps, 4-rank/2-rank decomposition, GMRES restart 1000→200, ILU fill level 1→0. Fine mesh OOM'd during dRdW Jacobian-coloring setup (reproduced twice). Coarsened 4x to 99,840 cells: coloring succeeded, but OOM recurred later during the GMRES linear solve itself; reducing GMRES restart and reducing ILU fill level each only moved the OOM one pipeline stage later, never eliminated it (one variant hit `PetscConvergedReason -5`, DIVERGED_BREAKDOWN, immediately before the next OOM). vcoarse mesh hit an unrelated SEGV/corrupted-field-read crash during `decomposePar`, not diagnosed further. **Root cause: OpenMDAO's reverse-mode total-derivative sweep for any requested `of=CD` unavoidably builds a mesh-sized `d[residuals]/d[vol_coords]` Jacobian block regardless of the requested `wrt=`** — structural, not fixable by mesh coarsening alone. No FD verification exists for this case; none was possible.

### A4 — Ahmed body, 25° rear slant
- Re ≈2.8×10⁶ (frontal-area basis, matches Ahmed/Ramm/Faltin 1984). Incompressible, separated/bistable wake, turbulent (SA on the DAFoam side; the OpenFOAM cross-check baseline used k-omega-SST/SIMPLEC), wall-function RANS. **Steady. 3D**. Solver `DASimpleFoam`.
- Two meshes used, disclosed: fine (45,760 cells) for the primal comparison; coarse (2,777 cells, ~16x coarser) for the adjoint/FD stage only — explicit use of the brief's allowance to coarsen for the gradient stage. Cost: **10.9 core-min total** (fine primal 1.67 + adjoint-stage setup/attempts + `compute_totals` 1.87 + `check_totals` 2.20, plus blocker/diagnostic runs).
- Primal (fine mesh): converged, CD=0.06998, yPlus mean 205.7. vs. own prior OpenFOAM baseline on the identical mesh/BCs: 22.05% deviation — traced to `DASimpleFoam` silently dropping SIMPLEC (`consistent yes`) and landing on a different branch of this geometry's known-bistable wake, not a bug. vs. experiment (frontal-area rebased): DAFoam 0.2510 (11.93% off, within the ±15% band); OpenFOAM baseline 0.3219 (12.95% off, within band). Both branches validated within tolerance.
- Adjoint (coarse mesh, ONE scalar shape DV — the FFD roof/slant break-line height): `compute_totals` OK, GMRES 719 iterations. `check_totals`: adjoint 0.21821, FD 0.24258, **relative error 10.04%**, single scalar DV (no vector-norm dilution possible), no sign flip.
- **Verdict: was PASS under the retired 1–12% band. Under the current standard, this is a single component at 10.04%: CONDITIONAL** (5–15% band, no flag). **This is the verdict change the brief calls out explicitly** — A4's own record and `A_stepsize_study.md` both independently reason the downgrade: with n=1 DV it cannot hide behind a healthy vector norm the way A1's aggregate does, and 10.04% sits inside the range A1's genuinely-defective single components (idx0/idx1, 9–16%) occupy, not inside the harness-sound 2.5–5% floor A1's own well-behaved components established. **Fine-mesh adjoint was never attempted** (deliberately, given A3's OOM at more than twice this fine mesh's cell count).

### A5 — U-Bend Channel, pressure-loss objective (adapted case, disclosed: `UBend_CHT` is CHT-only and requires funtofem+MELD; `UBend_Channel` was used instead and its stock weighted objective `scalePL*(TP1-TP2)+scaleHFX*HFX` was reduced to pure pressure loss `TP1-TP2`)
- Internal duct flow (U-bend channel), turbulent (SA), wall-function RANS; Reynolds number not computed in the record (inlet U=8.4 m/s, ν=1.5e-5 m²/s, hydraulic diameter not confirmed in the sources read). **Steady. 3D half-model** (one symmetry plane). Solver `DASimpleFoam`, 4 ranks.
- Mesh: 4,800 cells. Cost: **~26.0 core-min** across primal+adjoint+FD+diagnostics.
- Primal: objective (TP1−TP2) stable to 7–8 sig figs from iteration ~600, but field residuals (`p` initRes ≈2.26e-4) plateau at a **genuine fixed point**, not `1e-8` — confirmed by a follow-on addendum that extended iterations 1000→5000→10000 and tightened `residualControl`/inner-solver tolerances by 1–2 orders of magnitude: residuals were **bit-identical**, ruling out under-iteration. Converged pressure loss = 52.34521633934581 (5.5% off the tutorial's own stock baseline constant, plausibly a ~6-year OpenFOAM solver-version gap, not a setup error).
- Adjoint: GMRES converged (86 iterations, `PetscConvergedReason: 2`), reproducible bit-for-bit.
- FD verification (`of=OBJ.val`, `wrt=shapexUpper`, 27 components): **aggregate 46.6%, only 5/27 within the 12% (old) band, 2 components sign-flipped (idx 8, 17)**. A step-size diagnostic on idx0 ruled out "just needs a bigger step" (FD did not converge toward the adjoint as step grew 1e-4→1e-2). A follow-on primal-convergence-tightening test (this rung's own addendum) **refuted** the hypothesis that the residual plateau explains the gap: tightening made the aggregate error and sign-flip count *worse*, not better (46.64%→46.21%, 5/27→4/27 within band, 2→3 sign flips).
- **Verdict: FAIL**, unambiguously — both by aggregate (>15%) and by sign-flipped components, independent of each other.

### A6 — CRM Wing (wing-alone; DPW4_Aircraft wing-body-tail rejected on time-box grounds, disclosed)
- Mach 0.850 (from case thermophysical state), CL target 0.5. Compressible, transonic, turbulent (SA), wall-function RANS. **Steady. 3D** wing (no fuselage/tail — real, disclosed scope reduction from a true CRM/DPW wing-body case). Solver `DARhoSimpleCFoam`.
- Mesh: 579,072 cells, `checkMesh` clean. Cost: **~38.4 core-min** across 3 primal attempts (2 discarded — 1 orphaned-and-corrupted by a process/timeout mishap, 1 failed reading the corrupted checkpoint).
- Primal (accepted, attempt 3): **converged on every field below `primalMinResTol=1e-8`** (tighter than A3's ambiguous shock-plateau case). CD=0.0209014, CL=0.5000146 — matches DAFoam's own published tutorial baseline (CD=0.02090) to **0.0067%**.
- **Adjoint: not attempted, per explicit instruction.** This mesh (579,072 cells) is 1.45x A3's already-OOM'ing fine mesh and 5.8x A3's already-OOM'ing coarsened mesh — the same structural memory wall applies, not a new stretch goal that ran out of time.

### A_stepsize_study — diagnostic on A1's `check_totals` step size (not a case; folded into cross-rung finding 2 below)

---

## Ladder B — closure-literature reproduction via DAFoam adjoint field inversion

### B1 — reproduction-plan research (no compute)
- **Research and planning only — no solver runs, no compute launched.** Ranked 3 candidate FIML-lineage papers for reproducing a closure correction via DAFoam's own adjoint; Pick 1 (Wu, Zhang & Zhang, AIAA J 2025 / arXiv:2402.16355) scores 0.0624 on the benchmark's own 8 test cases using literally DAFoam's discrete adjoint to invert a field correction on the SST destruction term, trained on CBFS and generalized zero-shot to the duct cases. Cost estimate for the field-inversion step: **[ESTIMATE, not measured]** 140–420 core-minutes, explicitly flagged as needing a timed pilot before committing — B3 below is that pilot.

### B2 — square-duct + CBFS uncorrected-RANS baseline (**not a DAFoam run** — plain OpenFOAM `simpleFoam`/`kOmegaSST`; included because it is the disclosed prerequisite B3 depends on)
- `AR_1_Ret_360` (3,025 cells, Re_τ=342, Re_b=5693) and `AR_3_Ret_360` (8,748 cells, Re_τ=336, Re_b=5817): internal periodic square-duct flow, turbulent (k-omega-SST), **steady, 3D** (quarter-duct, 2 symmetry planes). Reproduced the benchmark's own baseline field to **0.16%** and **0.64%** deviation from the published floor (0.023%/0.09% field-vs-field scaled MAE). Cost: 0.13 + 1.27 core-min.
- `CBFS` (curved backward-facing step, 21,000 cells, 2D separated flow, k-omega-SST, steady, run to a fixed 30,000-iteration `endTime` by the case's own design): reproduced to 0.068% field-vs-field agreement. Cost: 29.5 core-min.
- **Verdict: PASS/reproduced**, with 2 disclosed deviations (a missing custom frozen-turbulence library, substituted with stock SST — measured as effectively inert at <0.1% field agreement but not verified against the library's own source; an OpenFOAM Foundation-vs-ESI fork mismatch, worth 10–13% in iteration count but only 0.02–0.09% in the converged field) and one real blocker flagged forward to B3: the CBFS LES reference fields (`0/U_LES` etc.) use `#include`-macro'd dictionaries that the field parser (`Ofpp`) silently fails on, returning `None` with no exception.

### B3 — CBFS field-inversion pilot (DAFoam `DASimpleFoam`, the actual DAFoam work in Ladder B)
- Internal 2D separated flow (curved backward-facing step), turbulent (k-omega-SST), **steady, 2D**. 21,000 cells.
- **Stage 1 (macro-expanding LES-field reader): DONE, verified.** Fixed B2's flagged silent-`None` bug, and found a second, more dangerous bug: a duplicate-key shadowing issue in `0/p_LES` that a naive fix would have turned into a silently-*wrong* (not missing) value. Both verified with round-trip and negative-control tests.
- **Stage 2 (DASimpleFoam primal on CBFS): DONE.** After fixing 3 disclosed case-setup issues (missing `Pr`/`Prt`; 2D `empty` patch not supported by IDWarp, converted to `symmetry`; a `useWallFunction` override that was tried, then rejected after measurement showed it silently changed the physics — 19% field deviation), primal converged to `primalMinResTol=1e-6` (1223 iterations) and matched B2's independently-run plain-OpenFOAM baseline to **0.087% (U), 0.23% (p), 1.41% (k), 1.20% (omega)** scaled MAE.
- **Stage 3 (timed adjoint pilot): BLOCKED — this is the case named explicitly in the brief.** Design variable substituted, disclosed: inlet patchVelocity stood in for the paper's real β(x) field DV (building the custom turbulence-model library was out of scope). Failure mode, precisely: the discrete-adjoint GMRES solve returns **PETSc `KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at iteration 0** — NaN/Inf detected before any GMRES progress. Reproduced identically across 4 independent configurations: 2 primal convergence levels (1e-4, 1e-6), 2 objective types (a custom field-variance loss and a standard force/CD objective already known to work in this lab's naca0012 case), and 2 ILU fill levels (1, 4). Mesh quality checked and ruled out (`DACheckMesh`: max AR 14.76, max non-orthogonality 33.3°, max skewness 0.26, all "OK"). **Root cause not resolved within this rung's budget** — reported as an open blocker, not routed around. A separate, second silent-failure trap was also found and fixed en route: `DAFunctionVariance` hardcodes reading its reference data from folder `"0"` regardless of `startFrom`, so a `startFrom=latestTime` run silently produced a fake all-zero objective/gradient (caught by checking the printed value, not trusting "success").
- **Stage 4 (full CBFS field inversion): DID NOT RUN**, correctly gated by Stage 3's unresolved blocker, per the docket's own instruction.
- No GMRES-iteration cost was ever measured (the solver never completed one iteration), so B1's 140–420 core-minute estimate for a full inversion **cannot be confirmed or refuted** by this rung.

---

## Pre-ladder cases (`work_sail/`, `work_wing/` — before the ladder was formalised)

### naca0015_sail_coarse
- Re ≈6.0×10⁶ (U0=75 m/s, lRef=1.2 m, ν=1.5e-5 m²/s — computed from stated case parameters). Incompressible, high-speed-relative-to-the-other-cases, turbulent (SA), wall-function RANS. **Steady. 3D** (a NACA0015-section sail/foil), AoA=5°. Solver `DASimpleFoam`, 3 ranks.
- Mesh: 63,920 cells (checkMesh reports 1,912 concave cells flagged but not blocking). Cost: **≈64.5 core-min** (runmodel 0.25, `compute_totals` ≈49.5, `check_totals` ≈14.75).
- Primal: converged, residual 9.81e-09 vs 1e-8. CD=0.033031, CL=0.180995.
- Adjoint: attempted, completed (GMRES 60–62 iterations, `PetscConvergedReason: 2`).
- FD verification: CD/patchV 0.017%, CL/patchV 0.032%, CD/shape **4.52%**, CL/shape 0.53%, `geometry.volcon`/shape ≈7e-14 (machine precision). All 8 raw shape-derivative components checked by hand: adjoint and FD agree in sign on every one — **no flagged/sign-flipped components**.
- **Verdict: PASS**, cleanly (≤5% aggregate, no flags) — better-behaved than the official NACA0012 tutorial (A1) on the same class of derivative.

### naca0015_sail_medium
- Same geometry/flow condition as sail_coarse (Re ≈6.0×10⁶, U0=75 m/s, AoA=5°, SA, steady, 3D). Solver `DASimpleFoam`, 3 ranks.
- Mesh: 156,089 cells (3,215 concave cells flagged). Cost so far: runmodel 1.01 core-min; `check_totals` **≈33.2 core-min, wasted/incomplete**.
- Primal: converged, residual 9.26e-09 vs 1e-8. CD=0.028912, CL=0.185974.
- Adjoint: `check_totals` was launched; primal re-solves inside it completed, but the log **ends abruptly mid-`dRdW` Jacobian-coloring sweep** (last entry: "ColorSweep: 1000, number of uncolored: 53543"), with no completion message, no derivatives printed, and no explicit error/OOM message captured in the log. **No FD result exists for this mesh.**
- **Verdict: BLOCKED/incomplete** — the truncation pattern (dies partway through coloring on a mesh roughly 4x A1's size, no compute_totals log even present separately) is consistent with the same memory/process-limit family documented for A3, though this specific log does not itself confirm OOM as the cause.

### naca0015_sail_full
- Case files exist (`Allclean.sh`, `preProcessing.sh`, `runScript.py`, `0.orig/`, `FFD/`, `constant/`, `system/`) but **no run logs of any kind exist in this directory** — no `logMeshCheck.txt`, no `runmodel_*.log`, no `compute_totals`/`check_totals` logs. **This case was set up but never run.** No mesh count, no primal, no adjoint, nothing to report beyond "case scaffolding present."

### naca4412_wing_coarse
- Re ≈1.0×10⁶ (U0=15 m/s, lRef=1.0003 m, ν=1.5e-5 m²/s — computed from stated case parameters). Incompressible, turbulent (SA), wall-function RANS. **Steady. 3D**, genuine full-span wing (no symmetry plane, unlike the half-model U-bend). Cambered NACA4412 section, AoA=0° (still produces lift). Solver `DASimpleFoam`, 4 ranks.
- Mesh: 337,334 cells (19,600 concave cells flagged, not blocking). Two primal attempts **FAILED first**: "Leading edge radius points are too far from the leading edge point to form a circle" — an FFD/geometry-parameterization setup error, fixed before the accepted run (fix mechanism not detailed in the surviving logs beyond the two failed attempts being superseded).
- Primal (accepted, 3rd attempt): converged, residual 9.92e-09 vs 1e-8. CD=0.024906, CL=0.244554. Cost: ≈4.2 core-min (63s wall, 4 ranks).
- Adjoint: `compute_totals` was launched and **re-ran the primal to the same converged state** (matches the accepted runmodel numbers, confirming the same case), then began the reverse-mode sweep — the log **stops abruptly** after two lines ("Computing d[CD]/d[aero_states]^T * psi 63.67 s", "Computing d[CD]/d[aero_vol_coords]^T * psi 64.58 s"), with no completion, no printed derivatives, no error message. Cost before cutoff: ≈4.3 core-min. **No adjoint result, no `check_totals`, no FD verification exists for this case.**
- **Verdict: primal PASS/converged and validated against no external reference in this record (none checked here); adjoint BLOCKED/incomplete**, same pattern as sail_medium — a large-ish mesh (337k cells, well above A1/A5's working 4k–5k-cell envelope and close to A3's already-OOM'ing 399k/99.8k meshes) whose adjoint stage silently stops before completing, with no captured OOM/error message to confirm cause.

### naca4412_wing_check
- A `checkMesh`-only directory (337,334 cells, matching `naca4412_wing_coarse`'s mesh) — mesh generated and quality-checked, no solver run at all. Included for completeness; contributes no primal/adjoint result.

---

## Cross-rung finding 1: the adjoint memory wall on this host

**Working envelope for a DAFoam adjoint on this instance is order 10³–10⁴ cells, not 10⁵.**

| rung | cells | adjoint outcome |
| --- | --- | --- |
| A1 NACA0012 | 4,032 | works, FD verified |
| A5 U-bend | 4,800 | works, GMRES converged (86 iter) |
| naca0015_sail_coarse | 63,920 | works, FD verified (PASS) |
| naca0015_sail_medium | 156,089 | **stalls/dies mid-coloring, no result** |
| naca4412_wing_coarse | 337,334 | **stalls/dies mid-adjoint-setup, no result** |
| A3 ONERA M6 (fine) | 399,360 | **OOM** during Jacobian-coloring setup |
| A3 ONERA M6 (coarsened) | 99,840 | **still OOM**, later pipeline stage |

Eight independent mitigations were tried on A3 and ruled out: 12g/18g container memory
caps, 4-rank/2-rank decomposition, GMRES restart 1000→200, ILU fill level 1→0. The
2-rank attempt drove host `MemAvailable` to 1.77 GB and was killed manually rather than
left to run. Root cause (A3, confirmed): OpenMDAO's reverse-mode sweep for any requested
total derivative unavoidably builds a mesh-sized `d[residuals]/d[vol_coords]` Jacobian
block — structural, not something mesh coarsening alone escapes (a 4x cell cut on A3
only moved the OOM one pipeline stage later). The naca0015_sail_medium and
naca4412_wing_coarse incomplete adjoint logs (156k and 337k cells respectively) are
consistent with this same wall, though neither log captured an explicit OOM message to
confirm the mechanism directly.

**Consequence: A3's adjoint and A6's adjoint (not attempted) are both blocked by this
same wall.** A genuine matrix-free path exists (`adjUseColoring=False`) but trades memory
for an unmeasured runtime cost and was not attempted anywhere in this ladder.

## Cross-rung finding 2: is the airfoil shape-derivative disagreement real, or a check artefact?

**`A_stepsize_study.md`'s conclusion: predominantly real, not a step-size artefact.**
Swept A1's `check_totals` FD step across 8 decades (1e-8 to 1e-1) on `CD wrt shape` (8
FFD components):

- Below step 1e-4: roundoff-dominated, error rises steeply (11.5%→95%) — expected.
- Above step 3e-2: primal solver itself fails to converge (idx6 stalls at 5e-2; total
  failure at 1e-1).
- **The well-converged plateau (1e-4 to 3e-2) is noisy and non-monotonic** (11.4%→10.5%→
  8.9%→4.3%→9.8%), swinging by nearly 3x on the exact same case purely from step choice —
  proof the aggregate vector-norm percentage alone is a fragile grading statistic.
- **Excluding idx0, idx1, idx6: dead flat at 2.5–3.0% across the entire plateau**, cosine
  similarity 0.99998 — the harness and adjoint are sound for 5 of 8 components.
- **idx6 alone accounts for 82.7% of the squared-error norm** and never stabilizes at any
  step tested (sign-flipped, unstable) — reproducing `PROOF.md`'s independently-derived
  82.7% to 4–5 significant figures, from a different script, different session.
- idx0 and idx1 carry a stable ~9–16% disagreement across three decades of step size —
  not shrinking, so not a step-size artefact by definition.

**Which components carry it:** idx0, idx1 (the two interior FFD stations nearest the
leading edge) and idx6 (the leading-edge combo mode itself) — localized exactly at the
airfoil's highest-curvature region. `PROOF.md`'s independent, deeper investigation
(different session, `primalMinResTol` tightened to 1e-12, four orders of magnitude
tighter than A1's 1e-8) reached the same localization and the same conclusion by a
different, more decisive route: a genuine FD plateau opens (varying only 0.02–0.08%
across 3–5 decades of step, at signal-to-noise ratios from the hundreds to the tens of
millions) and **the adjoint sits outside that plateau** for all three components — this
is not a resolution/noise-floor problem, it is a real disagreement. `PROOF.md` also
tested and **refuted** the leading candidate mechanism (DAFoam's `forceMeshWaveFrozen`
omitting d(wallDistance)/d(shape) from the adjoint): measured directly via
`getOFField("yWall",...)` across 9 independent runs spanning a 500x range of shape
perturbations, `yWall` never moves — both the adjoint and every possible FD computation
in this installation differentiate the *same* frozen field, so this omission cannot be
the source of the gap. **Root cause identified in a later session (`PROOF.md` §15): `mesh.warpDeriv`, the reverse-mode mesh-warp derivative the real adjoint calls, is confirmed wrong (sign-flipped, 108–149% relative error) for idx6 specifically, while agreeing to 0.1–2.4% for a healthy control (idx4) — see the A1 entry above for the full result. For idx6, it is the adjoint that was wrong, not the finite-difference check.**

**New grading standard this finding produced (both `A_stepsize_study.md` and
`ACTIVE_RESEARCH.md` state it identically):** do not grade on the aggregate vector-norm
percentage alone; report per-component/cosine agreement; flag any component whose FD
value changes sign or moves by >50% of its own magnitude across one decade of step. PASS
≤5% with zero flagged components; CONDITIONAL 5–15%; FAIL >15% or any flagged component
regardless of aggregate.

---

## Explicitly blocked, stated plainly

- **A3's adjoint is blocked.** Precise failure mode: OOM during either dRdW
  Jacobian-coloring construction (fine mesh, 399,360 cells) or the GMRES linear solve
  itself (coarsened mesh, 99,840 cells), after 8 disclosed and independently-ruled-out
  mitigations (memory caps, rank counts, GMRES restart size, ILU fill level). Root cause:
  a mesh-sized `d[residuals]/d[vol_coords]` Jacobian block is built unconditionally by
  OpenMDAO's reverse-mode sweep for any requested total derivative, regardless of the
  requested `wrt=`. No fix was found or applied within this ladder; A6 was consequently
  never attempted for the same structural reason, on a still-larger mesh.
- **B3's field inversion is blocked.** Precise failure mode: the discrete-adjoint GMRES
  solve returns PETSc `KSPConvergedReason = -9` (`DIVERGED_NANORINF`) at iteration 0 —
  NaN/Inf detected before a single GMRES iteration completes. Reproduced identically
  across 4 independent configuration changes (2 primal tolerances, 2 objective types, 2
  ILU fill levels); mesh quality independently ruled out as the cause. Root cause not
  identified within this rung's time budget. Stage 4 (the actual field inversion) was
  correctly never attempted as a result.
- **naca0015_sail_medium's adjoint is incomplete.** The `check_totals` log ends mid-way
  through Jacobian coloring with no completion or error message; no FD result exists.
- **naca4412_wing_coarse's adjoint is incomplete.** The `compute_totals` log ends two
  lines into the reverse-mode sweep with no completion or error message; no FD result
  exists.
- **naca0015_sail_full was never run at all** — case scaffolding only.
