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
> **[SUPERSEDED 2026-08-08 — see the dated amendment at the end of this F5c section.]** The
> "4–12× reattachment error" below was an instrument sign-convention defect, not physics; the
> corrected reading is x_r/H ≈ 5.6 = −10.5% vs Driver–Seegmiller. The original text is retained
> unedited per the supersede-don't-delete convention.

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

### 2026-07-30 addendum — provenance trace on the "OOM with huge gradient blow-ups" claim

**Conclusion first, per instruction: the claim does not trace to any primary-source event — no kernel OOM-kill message, no solver FATAL/abort log, no commit — anywhere in this repository. F5c's real, documented failure (above) is a steady RANS solve that *converges numerically* (residuals reach 1e-5 to 1e-9 every rung) but lands on the wrong reattachment length and wanders under iteration count and algorithm choice. That is not a crash and not a memory event. The most probable origin of the OOM/gradient-blow-up description is a conflation with a different, adjacent case: B3 CBFS.**

**What would change this conclusion:** a dmesg/journalctl line or solver log showing an actual memory-allocation failure or OOM-killer signal timestamped against an F5c run, or a docket/commit entry that names F5c specifically in connection with memory exhaustion. None was found despite a repo-wide search (below); if one turns up later, this section is wrong and should be corrected, not defended.

**Search performed:**
- `git log`, every campaign `.md`, `NOT_PASSING_REGISTER.md`, `demo-output/website/agenda/docket.json`, `dmesg`/`journalctl`, and `sdk/chief_engineer/*.py` (server, router, agenda, fleet, docker_dafoam) for "F5c", "OOM", "out of memory", "backstep"/"backward-facing" — no hit connects F5c to memory exhaustion.
- The only two repo mentions of F5c outside this file (`F11_lid_driven_cavity_ladder.md:438`, `F11_runs/ladson_reference_note.md:79`) both describe it as "already-failed" / "consumed a full session and still did not reach a gate" — language that matches the reattachment-length finding above, with no mention of OOM or a blow-up.
- `sdk/workflows/backstep_case.py`: `STEP_LEVELS` tops out at 46,500 cells (coarse 9,050, medium 20,160, fine 46,500); `build_case()` is plain `simpleFoam`/SIMPLEC, no DAFoam/adjoint variant exists for this case in the repo. A mesh this size cannot plausibly exhaust the host's 30 GB.
- Extended-iteration divergence test (`f5c_extended_simplec20k`, coarse mesh, 20,000 iterations vs. the 8,000 already on record, PID 407308): the conclusion above was written, and committed, before this run finished — deliberately, so the run could corroborate rather than drive the finding. **Completed run, reported by the collector: exited 2026-07-30 04:55:48Z, verdict NOT_CONVERGED** — it ran to the full 20,000-iteration cap without ever printing `SIMPLE solution converged`. **RSS stayed flat at roughly 79 MB for the entire run, on a 30 GB box — no crash, no abort, no memory event of any kind.** These are two separate facts and neither should be read as the other: the run did not converge (consistent with, and extending, the non-monotonic wandering already on record at 2,000/8,000 iterations), and separately, twenty thousand iterations of the exact algorithm the OOM claim was attached to never came within three orders of magnitude of the box's memory capacity. This is corroborating evidence for the provenance conclusion below, not the basis for it — the conclusion was reached first from the log/commit/dmesg search and the run result was left to land afterward.

**The more likely origin, found in `NOT_PASSING_REGISTER.md` (GROUP 1: ADJOINT MEMORY WALL) and `demo-output/website/dafoam/DAFOAM_CASE_STATUS.md` (§B3):** this lab has a real, well-documented "adjoint memory wall" affecting several DAFoam adjoint cases on large meshes (A3 ONERA M6 fine/coarsened — confirmed OOM during Jacobian-coloring and again during the GMRES linear solve; naca0015_sail_medium and naca4412_wing_coarse — consistent truncation pattern; and **B3 CBFS field-inversion pilot — a *curved backward-facing step*, DAFoam `DASimpleFoam` adjoint case**, whose `check_totals` GMRES solve returns `PETSc KSPConvergedReason = -9` (DIVERGED_NANORINF — NaN/Inf detected before any GMRES progress), reproduced across 4 independent configurations). B3 is under active investigation this same session (`demo-output/website/dafoam/ladder-b/B3_work/CBFS/` has uncommitted changes as of this task). B3 CBFS genuinely combines both halves of the claim — memory exhaustion in the adjoint pipeline *and* NaN/Inf ("blow-up") gradients — on a case that shares the words "backward-facing step" with F5c but is otherwise unrelated: different geometry (curved vs. flat step), different solver (DAFoam adjoint vs. plain `simpleFoam`), different failure family (Group 1 memory wall vs. Group 3 solver convergence). A handoff note written late in a long session, referring to "the backward-facing-step case," has an obvious way to cross the two. That is the best-supported account of how the claim formed, though it is inference from the available records, not a recovered primary document — it is offered as the likely explanation, not asserted as proven provenance.

**Net effect on F5c's status:** unchanged from the verdict above (GATE NOT REACHED, reattachment length off by 4–12×, non-monotonic under SIMPLEC). The "OOM/gradient blow-up" framing should not be repeated for F5c going forward; if it needs a home, it belongs on B3 CBFS (`NOT_PASSING_REGISTER.md` §B3), where it is already correctly recorded.

### 2026-08-08 AMENDMENT — the "4–12× reattachment error" never existed: wallShearStress sign-convention defect, corrected reading x_r/H ≈ 5.6 (−10.5%)

**Ordered by the chief supervisor per entry 5 of
`demo-output/website/SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` (outcome block of
2026-08-08, commit df755b49), on the evidence of the inlet-development audit in
`demo-output/website/campaign/ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md` Task 1 (commit 6d806733).
The original text above is retained unedited; this amendment supersedes it — nothing is deleted.**

**The correction.** The "4–12× reattachment error" this record's Physics/Verdict sections are
built on was an instrument defect, not a flow result: the original F5c detector read OpenFOAM's
`wallShearStress` function object with the sign backwards. On a lower wall the object returns
τ_x **negative** under attached forward flow (`ssp = (−Sfp/magSfp) & Reffp` with
`Reff = −nuEff·devTwoSymm(grad(U))`), so the neg→pos crossing the detector called "reattachment
at 0.5–1.5H" was actually the downstream edge of the secondary corner eddy, and the "second,
unexplained separation at x/H ≈ 6–8 persisting to exit" was the real reattachment followed by
ordinary attached flow. This was proven at commit **fe121af2 (2026-07-31)** — nine days before
this amendment — by the archived **`sign_convention_control`** run (plain channel, no step:
attached forward flow, τ_x negative at all 100 wall faces,
`evidence/wallShearStress_bottomWall_iter322.raw`), and documented in
`sdk/workflows/backstep_case.py::parse_wall_raw`; neither this record nor the review was updated
at the time, which is the record-reconciliation failure the chief's review names.

**The corrected reading:** under the correct sign the same archived solutions reattach in the
≈5.6–8H crossing family this record had mislabelled as a "second separation" — the SIMPLEC coarse
case at **x_r/H ≈ 5.6, i.e. −10.5% versus Driver–Seegmiller's 6.26 ± 0.10** — inside the
documented linear-eddy-viscosity underprediction family, not 4–12× outside it. The evidence-record
table's x_r/H column and every deviation percentage above are readings of the mislabelled
corner-eddy crossing and are superseded accordingly; the pre-fix SIMPLEC "wandering"
(non-monotonic 1.07–1.49H) is, under the corrected sign, wandering of the corner-eddy edge — the
primary reattachment's own wander has not yet been measured cleanly.

**Arm retargeting (chief ruling, same entry):** the unsteady-probe arm (`f5c-unsteady-probe-run`)
**stays live but retargeted at the honest question** — a −10.5% steady miss with wander, not a
catastrophe. The equilibrium-k inlet repair (`--inlet-bl-turbulence`, built and unrun in
`backstep_case.py`) becomes its **cheap first leg**, and the arm's pre-registration **must be
rewritten against the corrected numbers before any launch**.

**2026-08-08 lever caveat (charter v1.5 §9, unverifiable-from-logs; ordered by the chief on the
dead-lever audit `DEAD_LEVER_AUDIT_2026-08-08.md`, 946e4a26).** The −10.5% corrected headline's
attribution to "the SIMPLEC coarse case" — and every SIMPLE-vs-SIMPLEC row in the diagnostic
table above — **cannot be verified from any runtime log, existing or possible**: (a) the six
original diagnostic runs' solver logs were never archived (`F5c_runs/` holds only
`sign_convention_control`; the extended run's case lived in a since-deleted scratchpad, see the
case path at `solve_registry/f5c_extended_simplec20k_20260730T042423Z.log:10`); (b) even a
surviving log could not prove it, because simpleFoam prints identical `SIMPLE:` banners whether
`fvSolution` sets `consistent yes` or not — OpenFOAM never echoes the flag. THE SWITCH YOU SET IS
NOT THE SWITCH THAT RAN: the algorithm attribution rests on this record's configuration
statements, not on log evidence, and this caveat travels on the −10.5% number's face. Binding on
the retargeted unsteady-probe arm (`f5c-unsteady-probe-run`): its rewritten pre-registration's
**first act must regenerate this number with provable levers** — archived case dirs, logs
retained, and the algorithm choice made log-provable (cat `fvSolution` into the run log at
launch, per the instrumentation proposal filed with the audit).

### 2026-08-10 AMENDMENT — the −10.5% is WITHDRAWN to *unmeasured*, and no F5c run has ever converged

**Ordered by the chief supervisor on the Stage A result
(`F5C_STAGE_A_RESULTS.md`, commit `27a94361`; pre-registration `3734270d` +
`d64565c1`; entry 4/5 rulings at `581bb9d8`). Three corrections, each a dated
amendment and never a revision — every word above is retained.**

#### Correction 1 — "deep numerical convergence" was never earned

The Feasibility section above states *"Solver runs to deep numerical convergence
(p, U, k, omega residuals 10⁻⁵–10⁻⁹) at every configuration tested"*, and the
2026-07-30 addendum repeats it as *"converges numerically (residuals reach 1e-5
to 1e-9 every rung)"*. **Both read the LINEAR solver's FINAL residuals. The
quantity that decides whether a SIMPLE solve has converged is the INITIAL
residual of each outer iteration, and it was never reported.** (This module's own
`control_dict` docstring names the trap: *"F5c's first pass reported 'converged'
off the linear solver's final residuals while the SIMPLE initial residuals were
still at 1e-3."*)

Measured for the first time, 2026-08-10, at the `residualControl` gate the case
sets for itself:

| run | iterations | p (gate 1e-5) | Uy (gate 1e-6) | Ux (gate 1e-6) | k (gate 1e-6) |
| --- | --- | --- | --- | --- | --- |
| A1 SIMPLEC | 2 000 | 2.48e-3 — **248×** off | 2.35e-3 — **2 352×** off | 1.08e-4 | 5.44e-4 |
| A2 SIMPLEC | 8 000 | 6.63e-4 — **66×** off | 8.47e-4 — **847×** off | 2.75e-5 | 1.12e-4 |
| A3 SIMPLE | 2 000 | 7.72e-3 — **772×** off | 1.75e-3 — **1 752×** off | 2.40e-4 | 4.06e-4 |

Quadrupling the iterations cut the residuals ~4× and left them two orders of
magnitude short. The archived 20 000-iteration run
(`solve_registry/f5c_extended_simplec20k`) never printed `SIMPLE solution
converged` either.

> **NO F5c RUN HAS EVER CONVERGED, at any iteration count up to 20 000.**

Every statement in this record built on the word *converged* — including *"a
converged answer that is wrong"* and *"this is not a numerical-convergence
failure"* — is superseded. It may be a numerical-convergence failure; nobody had
measured it.

#### Correction 2 — the −10.5% headline is WITHDRAWN to *unmeasured*

The 2026-08-08 amendment above states the corrected reading as **x_r/H ≈ 5.6,
−10.5% vs Driver–Seegmiller**. Stage A ran the configuration that number is
attributed to, with archived cases, retained logs and hash-bound levers, and
**M1 scores NOT REGENERATED**: the same SIMPLEC coarse case at 8 000 iterations
returns **x_r/H = 6.996**, which is **1.396 H** from 5.6 against a pre-registered
bar of 0.81 H, and **+11.7%** against the reference — an *over*-prediction, where
this closure is documented to *under*-predict.

**The 2 000-iteration leg does land at 5.564, and it does not rescue the number.**
That leg's own x_r history swings **6.56 H** across the second half of its run
(3.530 → 10.089). The 5.6 was one sample of a moving quantity at the iteration the
solver happened to stop, not a measurement of this case. Rescoring M1 onto the
agreeing leg after the fact is forbidden by L-44 and would be wrong on the data
anyway.

> **F5c has NO headline reattachment number.** The `x_r/H ≈ 5.6` and every
> `−10.5%` in this record and in `ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md` §Task 1
> are withdrawn to *unmeasured*.

What **survives** from the 2026-08-08 amendment, unaffected: the sign-convention
defect was real and is fixed; the archived `sign_convention_control` run still
proves the convention; and Stage A's two independent detectors (wall-Cf crossing
and the convention-free near-wall U_x sample) agree everywhere to within 0.04 H,
so nothing here is a detector artifact. **What died is the number, not the fix.**

#### Correction 3 — the review's framing, and where to read it

Review entry 5 of `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` has been
amended by the chief himself at `581bb9d8`. Its framing — *"converged solves
4–12× wrong on reattachment, wandering"* — has now lost **both** of its load
bearing words: *4–12×* died at `fe121af2` (sign convention), and *converged* dies
here. A reader arriving from either direction should follow the cross-reference:

| arriving at | go to |
| --- | --- |
| this record | review entry 5's outcome block (`581bb9d8`) |
| review entry 5 | this amendment, and `F5C_STAGE_A_RESULTS.md` |
| `backstep_case.py::parse_wall_raw` | this amendment (the `x/H ~ 5.6` in that docstring is the withdrawn number) |

#### What is NOT claimed by this amendment

No wander verdict, in either direction — chief policy for this case is that none
may be claimed from a `coarse` detector, and Stage A used only `coarse`. No claim
that the flow is or is not unsteady. The 6.26 ± 0.10 reference is untouched. The
docket item is **re-posed, not retired**: *you cannot ask whether a flow is
unsteady until the steady solve is shown able to converge.*

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
