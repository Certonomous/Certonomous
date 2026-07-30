# NOT_PASSING_REGISTER

**Date compiled:** 2026-07-29  
**Scope:** Every case in the lab that did not pass, did not converge, or was never finished. Read-only survey; no solvers run, no compute launched to produce this document.

**Format:** case · what it was trying to show · how it failed (exact error, residual, percentage) · is the root cause known · what it would take to resolve · where the evidence lives.

**Tone:** Register of honest failures, read as an asset. State what happened. A documented failure with a named cause is a result.

---

---

## What moved on 2026-07-29 evening, after this register was compiled

The register below is kept as compiled. This section records what changed in the
hours after, because a failure register that silently absorbs its own resolutions
stops being a record of anything.

### Resolved

**The airfoil leading-edge shape derivative (Group 2).** Root cause found after
seven tested mechanisms, six refuted. The mesh warp's own linearisation is wrong
for opposing-direction combination shape variables: 108-149 percent error and a
flipped sign under a generic test seed, 634 percent under the real objective seed,
against a single-point control agreeing to 0.1-2.7 percent. The verdict INVERTS
the assumption the whole investigation was built on -- the finite-difference check
was right and the discrete adjoint was wrong. Two conditions, both measured: the
opposing-direction construction is necessary, and the error must overlap the
objective's own sensitivity field to reach a real gradient, which is why the
leading-edge mode is corrupted and the trailing-edge mode with identical
construction is clean. A fileable upstream defect report exists and is unfiled.

### Reclassified, which changes what a fix would cost

**Group 1 is not only a memory wall.** Measured this evening: the adjoint
completes at 63,920 cells and breaks down at 79,560 cells with over 4 GB of memory
headroom still unused, then breaks down again at 99,840. In this range the
CONVERGENCE limit binds before the MEMORY limit. A larger machine would not buy a
larger mesh. The group's "to resolve" column, which pointed at hardware, now
points at conditioning -- scaling, equilibration, or a different Krylov method,
none of which needs a purchase. The memory scaling law is still worth completing,
but it answers a conditional question: what box would be needed IF the numerical
problem were solved.

### Added 2026-07-30 — F4 SWBLI cylinder-flare warm-up: a hard case, five mechanisms eliminated, two real bugs fixed, unresolved

**New entry, Group 3.** `f4_swbli_warmup20` (Kussoy & Horstman M=7.05 cylinder-flare
SWBLI, θ=20° attached warm-up rung, ahead of the pre-registered θ=32.5°/35° gate)
crashed with SIGFPE, was diagnosed across a full session, and defeated the
investigation. Two genuine, independently-valuable bugs were found and fixed along
the way — a thermodynamic-model swap that silently dropped the only temperature
bound in the stack (`LESSONS.md` L-20), and an inverted mesh-grading direction in
`make_swbli_case.py` that left the wall ~86x too coarse (y+≈86 where the design
called for y+~1), invisible to `checkMesh` and affecting every future case built
from that generator. Five candidate mechanisms for the underlying, still-unbounded
energy defect were tested and eliminated on direct evidence: mesh cell quality,
inlet boundary-condition VALUES, local time-stepping, and (this update) farfield
boundary TREATMENT. See the full entry below and
`demo-output/website/campaign/F4_hypersonic_blunt_body.md` for the complete,
commit-by-commit record, including a self-caught and corrected process-monitoring
error (a `pgrep`-based completion check gave a false positive; caught by `ps`
before being reported, matching this project's own L-2/L-6/L-10). θ=32.5°/35°
remain correctly held; not gated.

### Added 2026-07-30 — F5c backward-facing step: register entry added, and a claimed OOM traced to a probable conflation with a different case

**New entry, Group 3** (this case was already investigated and written up in
`F5bc_unsteady_statistics.md` but had never been given a register entry — added
now). F5c (Driver & Seegmiller 1985 backward-facing step, `simpleFoam`, steady RANS)
converges numerically at every rung (residuals 1e-5 to 1e-9) but lands on a
reattachment length 4-12x off the reference and does not settle under mesh
refinement, wall treatment, or algorithm change -- the steady-RANS fixed-point
assumption itself is in question, not the mesh. Separately: this case had been
described elsewhere as "OOM with huge gradient blow-ups." A repo-wide provenance
search (git log, every campaign doc, the docket, dmesg/journalctl, the
chief_engineer source) found no kernel OOM message, solver abort log, or commit
that connects F5c to memory exhaustion -- only the same, already-documented
reattachment-length finding. The likely source of the confusion: **B3 CBFS**
(below), a *curved* backward-facing step and a genuine DAFoam adjoint case, which
really does combine both halves of the claim (confirmed-family OOM plus
`DIVERGED_NANORINF` NaN/Inf gradients) and shares enough of the name that a
handoff note referring to "the backward-facing-step case" has an obvious way to
cross the two. Full trace and elimination list in `F5bc_unsteady_statistics.md`,
"2026-07-30 addendum."

### Narrowed

**The U-bend gradient failure (Group 2)** was tested against the airfoil's
newly-found mechanism and CLEARED -- its variables are all single-point and its
sign-flipped components agree with a finite difference of the warp to 0.32-1.30
percent. It remains a genuine second defect with an unknown cause, now being
isolated link by link.

**The field-inversion adjoint failure (Group 3).** Two more mechanisms eliminated:
the converged state holds no non-finite value, verified cell by cell across every
field the adjoint reads; and the perturbation applied during Jacobian colouring is
additive-only, read from the single source site that applies it, so it cannot
drive turbulence quantities negative as had been proposed. A separate abort during
colouring validation was traced to a diagnostic script omitting a setup call, not
to the case. Four mechanisms now eliminated.

### Corrected

**The hump turbulence sweep (Group 3)** is complete: all four comparison models
now hold converged numbers. This FALSIFIED a pre-registered prediction of this
lab's own -- the narrow inter-model band was published as failing to contain the
experiment, and it only failed while one model sat short of its convergence gate.
Converged, that model crosses to the other side of the experimental value and the
narrow band contains it. All public surfaces were corrected the same evening.

**A cylinder rung recorded here as incomplete had in fact finished.** The note was
stale; the statistics were recomputed from the raw force file rather than from the
note.

### Added 2026-07-29 night session

**F9 pulsatile valve (`pulsatile_physio`) was also recorded stale, the same way.**
`f9_analysis.json` said "fewer than 2 full cycles available; periodicity not
established," dated from a mid-run snapshot at t=1.469. The actual run had
already finished its full 3 cycles (t=0→2.7) hours earlier — clean completion,
no crash, bounded Courant, continuity errors ~1e-10. Re-running the
already-written `analyze_f9.py` (zero core-minutes, pure post-processing)
shows periodicity established to 7.0e-7 relative drift and completes Gates
1–3: Gate 1 (quasi-steady limit) PASS at two independent alpha values
(−1.58%, +0.22%); Gate 3 (ROM comparison) confirms the session's own
pre-registered prediction in direction and order of magnitude (−94.0% vs.
predicted "far below, order 150–250 Pa"); Gate 2 (Womersley profile) FAILS
as a point comparison (20–414% error across phases and two alpha values) —
see the new Group 4 entry below for the cause. Full record:
`demo-output/website/campaign/F9_pulsatile_valve.md`.

### Added 2026-07-30 — public-surface audit: four new findings, three already fixed, one recorded here in full

A gate-checked audit of every quantitative claim on the public surfaces
(`benchmarks.html`, `ACTIVE_RESEARCH.md`, `D9_TALKING_POINTS.md`, `wall.json`,
`NINE_ACT_GATE_TABLE.md`) found, among other things, three claims that were
outright false on a filmed surface. Those three were corrected on the
surfaces themselves the same night, not routed through this register: the
ONERA M6 board row claiming PASS (its quoted 0.013–0.027 RMS was the
pressure-surface half of a two-sided comparison; the shock-carrying suction
surface ran 0.049–0.114 — cherry-picking the easier half and labelling it
PASS was a false claim, now removed and reconciled against this register's
own pre-existing "ONERA M6 Act — primal residual plateau" Group 3 entry,
which had it right all along); A4 Ahmed body's drag number (withdrawn from
the research board — the normalised omega residual collapsed to a fixed
value that read as converged while the raw residual statistics showed a
catastrophic blow-up, and the drag was computed from that state; the same
Initial-vs-Final residual misreading this register's own hump correction
above already found once tonight; the gradient claim for the same case
survives because it used a different, healthy coarse mesh — two claims had
been bundled under one COMPLETE label and only one failed; not filed as a
new entry here, since the correction lives on the surface itself and the
existing Group 1 A4 entry already covers the case for a different reason,
its fine-mesh adjoint never having been attempted); and A3's board row
(corrected to match this register's own existing Group 1/Group 3 A3
entries, which had it right all along).

The remainder — cases that were not outright false but were not disclosed,
or where the finding is not yet a verdict — are filed below, in full, per
this register's purpose. See new entries in Group 3 (NASA TMR bump-in-channel;
the seven wall.json calibration credentials; A6 CRM's unresolved raw
residual) and the new Group 6 (an unverifiable claim with no artifact
found). Full audit trail: this session's conversation record; no separate
write-up file was created beyond this register and the corrected surfaces.

### Added 2026-07-30 — R5 transonic adjoint conditioning: catastrophic failure fixed, convergence still not achieved

**Updates Group 1's A3 entry below, which predates this work and is now
incomplete on the conditioning question it left open.** Measured this session,
on the cheap 21,840-cell reproducer identified in `ADJOINT_MEMORY_ENVELOPE.md`:
a direct PETSc binary dump of the assembled preconditioner matrix
(`dRdWTPC`) shows a 12.5-order-of-magnitude row/column scale spread and a
14.5-order-of-magnitude diagonal spread — essentially the full dynamic range of
a double. Setting `normalizeResiduals: ["None"]` (default divides every
residual row by that cell's volume; this mesh family has 20-28% of cells
flagged "small determinant" in one concentrated region) changes
`PetscConvergedReason` from `-5` (`DIVERGED_BREAKDOWN`, residual collapsing to
denormal range, `~1e-308`–`~1e-310`) to `-3` (`DIVERGED_ITS`, residual
stagnates at a sane, non-denormal value) — reproduced independently on both
objectives (CD and CL run separately), with and without modified Gram-Schmidt
orthogonalization. A three-way false-positive/false-negative confusion during
this work was resolved by reading `DALinearEqn.C`'s own success-gate logic
directly: the `-5` runs' apparent "both objectives reported" completeness was
itself an artifact of the same denormal-collapse fooling the gate into printing
"solution finished" on a broken solve — not evidence the `-3` runs were
truncated (confirmed genuine: exact configured iteration counts reached, clean
deterministic shutdown, contrasted directly against a real truncated run
observed earlier in the same session). Two attempts to strengthen the
preconditioner enough to make the now-sane-but-stagnant baseline actually
converge (`pcFillLevel` 0→1; nested-Richardson-wrapped ASM+ILU per Kenway et
al. 2019, a previously-untried, already-exposed `daOptions` lever) both
reintroduced the identical `-5` collapse, landing exactly at the GMRES restart
recomputation boundary. Jacobian colouring count, checked retroactively across
the whole case family as a candidate discriminator (DAFoam's own authors report
945 colours vs. ADflow's 162 on a comparable case), does **not** separate
converging from diverging cases here — the converging incompressible sail case
needs more colours (1,999) than any diverging compressible case (1,233–1,391).
The queued follow-up measurement was then completed: the preconditioner
matrix's scale spread does **not** collapse under `normalizeResiduals=None`
(diagonal ratio 16.14 orders of magnitude, versus 14.17 on the default-
normalized baseline — worse, not better), so residual-volume scaling fixed
the specific collapse arithmetic without touching the underlying matrix
conditioning; a second, still-live layer of ill-conditioning remains, with
`normalizeStates`' single global per-field scalar (versus the mesh's
concentrated near-degenerate region) the leading unexamined candidate. **No
gradient has been obtained or verified at this mesh size, under any
configuration tried — nothing converged, so nothing was checked.** Full
record, all raw-log evidence: `demo-output/website/dafoam/R5_ADJOINT_CONDITIONING.md`.

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

**Count: 16 cases**

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

### F5c Backward-Facing Step — reattachment length 4-12x off, does not converge under refinement; claimed "OOM/gradient blow-up" not substantiated

- **What:** 2D backward-facing step (Driver & Seegmiller 1985), turbulent, steady `simpleFoam`. Six rungs: coarse/medium mesh, SIMPLE/SIMPLEC, 2,000-8,000 iterations, plus turbulence-level and top-wall-BC diagnostics.
- **How it failed:** Reattachment length x_r/H measured 0.49-1.49 against reference 6.26±0.10 (deviation -76% to -92%) across every rung. Every run's residuals converge cleanly (down to 1e-5 to 1e-9) — this is not a numerical-convergence failure, it is a converged answer that is wrong. Non-monotonic under iteration count alone (2,000 iters → 1.49H, 8,000 iters → 1.07H, same mesh/algorithm), which rules out "just needs more iterations."
- **Root cause:** Not identified. Leading (untested) hypothesis: the case is genuinely unsteady (bubble-flapping) and a steady SIMPLE/SIMPLEC fixed point is the wrong tool, not the mesh or turbulence closure — try `pimpleFoam` with time-averaging instead. Secondary, also untested: the uniform (non-boundary-layer-shaped) inlet k/omega profile.
- **Separately, a provenance finding:** this case has also been described as "recorded as OOM with huge gradient blow-ups." No evidence for that framing was found anywhere in this repository (see `F5bc_unsteady_statistics.md`, "2026-07-30 addendum," for the full search). F5c has no adjoint/DAFoam variant, its meshes (9,050-46,500 cells) cannot plausibly exhaust the host's memory, and an extended 20,000-iteration test showed flat ~80 MB RSS through iteration 7,371 with no divergence signature. The probable source of the claim is conflation with **B3 CBFS** below — a different, curved backward-facing-step case that is a genuine DAFoam adjoint run and genuinely does OOM and produce NaN/Inf (DIVERGED_NANORINF) gradients.
- **To resolve:** (a) `pimpleFoam` + time-averaging on the same geometry to test the genuine-unsteadiness hypothesis, or (b) vary the inlet turbulence profile shape (not just bulk level) against a real boundary-layer TKE profile.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F5bc_unsteady_statistics.md` (§F5c, including the 2026-07-30 provenance addendum).

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

### F8 UAE Phase VI wind turbine (MRF) — never converged, force still oscillating at endTime

- **What:** Family F8 (rotating machinery), NREL/NASA-Ames UAE Phase VI Sequence S wind turbine, whole-domain single-cellZone MRF (`simpleFoam`, k-omega... SA per `0/nuTilda`), 7 m/s inlet — the case's own comment names this "the low-speed attached-flow point," i.e. deliberately the easiest operating point in the sequence. Run to `endTime=1500` (SIMPLE pseudo-iterations), 4-rank decomposition.
- **How it failed:** `grep -c "SIMPLE solution converged" log.simpleFoam` returns **0** — checked this session per L-14/L-15 rather than eyeballing residual magnitude. The residuals themselves confirm it: p initial residual still ~0.38 at iteration 1500 (target 1e-4), U initial residuals 0.009-0.15. `postProcessing/bladeForces` force history is not merely slow to converge, it is actively oscillating with no visible decay through the observed window: Fx ranges 683-1064 N (~30% peak-to-peak) and Fy ranges -336 to +280 N — including sign reversals — across t=1000-1500, the back fifth of the run.
- **Root cause:** Not established, but the cheap discriminating test named below has now been run. Two live hypotheses, distinguished per L-3 as hypotheses and not findings: (a) a real physical mechanism (rotor-wake/tip-vortex unsteadiness) that a frozen-rotor steady MRF model cannot represent, which would mean this case needs a transient rotating approach (sliding mesh / AMI) instead of more steady iterations; (b) a numerics issue (under-relaxation, scheme choice) fixable within the existing steady MRF framework.
- **The P1 test was run (2026-07-30): extended `endTime` 1500 -> 3000, `startFrom` switched to `latestTime` (the original `startFrom startTime; startTime 0` would have silently re-solved from zero on a naive restart — checked and fixed before launch, verified genuinely resumed by reading `Time = 1524` seconds into the new log, not assumed from the launch message). Result: `grep -c "SIMPLE solution converged"` is still **0** at t=3000. The oscillation did not decay — it widened: Fx range over t=1500-2250 was 485-993 N (span 508); over t=2250-3000 it was 375-1104 N (span 729), a larger swing in the second half, not a smaller one. Fy swings -775 to +1276 N over the full extended window, wider than the -336 to +280 N range measured over the shorter original run. Doubling the iteration budget did not fix this and does not look like it is converging toward doing so — **evidence for hypothesis (a) over (b)**, a genuine unsteady rotor-wake mechanism a steady frozen-rotor MRF model cannot represent, though this does not yet distinguish "real physics" from "a numerical instability that has not saturated," and is reported as evidence, not proof.
- **Memory/resource note, for whoever runs the next iteration budget:** the extended run's total RSS across all 4 ranks was measured directly at ~588 MB — light, not a resource risk on this host, checked deliberately after an unrelated same-night incident (a different job's 4-rank adjoint solve pushed the host into swap) raised the question.
- **To resolve:** Since more steady iterations demonstrably do not help, the next test is qualitatively different, not merely longer: (c) transient rotating-frame approach (sliding mesh / AMI) to let the rotor wake actually be unsteady instead of iterating a frozen-rotor snapshot toward a "steady" state that this evidence suggests may not exist for this operating point; or (d) a numerics-only control (reduced under-relaxation, alternative scheme) run for a bounded window to check whether (b) can be ruled out as cheaply as (a) was tested here, before committing to the larger rebuild (c) would require.
- **Reference already found and citable, not yet applied:** Hand, M.M., Simms, D.A., Fingersh, L.J., Jager, D.W., Cotrell, J.R., Schreck, S., Larwood, S.M. (2001), *Unsteady Aerodynamics Experiment Phase VI: Wind Tunnel Test Configurations and Available Data Campaigns*, NREL/TP-500-29494 — publishes low-speed-shaft torque and root bending moment vs. wind speed for Sequence S, including this exact 7 m/s point. Per the campaign's hard rule (a gate needs its citable reference obtained BEFORE the run — already satisfied here, the reference existed before this session started, it just was never written down), this reference is ready to use once a converged (or a deliberately time-averaged unsteady) force number exists to compare against it.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F8_runs/phase6_mrf/` (`log.simpleFoam`, `postProcessing/bladeForces/0/force.dat`, `constant/MRFProperties`); extended run: `demo-output/website/solve_registry/f8_uae_phase6_mrf_extend_20260730T000056Z.log`.

### naca4412 Wing Mesh Ladder — non-monotonic

- **What:** 3D cambered wing NACA4412, resolved boundary layers, three mesh rungs (medium 263.4k → fine 645.3k → finer 1.85M cells).
- **How it failed:** Cd sequence: 0.0245 → 0.0183 → 0.0183. Cd drops 25% (medium→fine), then plateaus <1% (fine→finer). Cl swings back up 19% (fine→finer: 0.2095 → 0.2502). Finer rung fails mesh-quality gates (non-orthogonality 74.96° exceeds 70° limit) and degrades boundary-layer coverage (58.3% vs 94% on other rungs) — finer mesh is worse, not better. Fine rung (645k cells) passes both mesh gates and is graded; non-asymptotic ladder not grid-conclusive per Richardson. No observed-order fit on non-asymptotic data.
- **Root cause:** Finer mesh-generation recipe breakdown; castellated-level interaction (per LESSONS.md / naca4412_credential_repair.py notes). Not a solver issue; the meshes themselves diverged from monotonicity criterion.
- **To resolve:** (a) Revert finer rung to same mesh recipe as fine rung (no castellated-level jump), or (b) revert fine and finer to medium's recipe and re-run, or (c) accept fine rung as the final grid and report "grid convergence attempted but non-monotonic; results flagged SOLVER-BACKED".
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/naca4412_wing.json` (full grid_study section with all three rungs and mesh-quality details).

### F4 SWBLI cylinder-flare θ=20° warm-up — SIGFPE, then persistent unbounded energy defect, five mechanisms eliminated

- **What:** Family F4 stretch rung, Kussoy & Horstman (NASA TM 101075) M=7.05 axisymmetric cylinder-flare SWBLI, θ=20° attached warm-up ahead of the pre-registered θ=32.5°/35° gate. `rhoCentralFoam` + `kOmegaSST`, 29,700-cell axisymmetric wedge, isothermal wall.
- **How it failed:** Original run (`f4_swbli_warmup20`) died with **SIGFPE inside `libfluidThermophysicalModels.so`** at `t=6.42e-07s`, Courant numbers normal (0.24-0.3), no warning beforehand. No field write existed between `t=0` and the crash, so the crash site could not be localised from the crashed run's own artifacts alone — localisation required building an instrumented, bounded diagnostic solver (`rhoCentralFoamBounded`, a two-line diff from stock `rhoCentralFoam.C` clamping internal energy before each `thermo.correct()` call and logging where/how much it fires) and re-running under controlled conditions.
- **Two genuine bugs found and fixed along the way, independent of whether the case ever gates:**
  1. **Thermodynamic-model swap silently dropped the only T-bound in the stack.** The case was adapted from OpenFOAM's `biconic25-55Run35` tutorial (`thermo janaf`, real `Tlow`/`Thigh` clamping) but switched to `thermo hConst` for a reasonable, disclosed reason (adequate Cp for this non-reacting flow) — `hConstThermo::limit(T)` is a documented no-op, unlike `janafThermo::limit()`, and `rhoCentralFoam` never calls `fvOptions` on the energy field either, so nothing else backstopped it. See `LESSONS.md` L-20.
  2. **Mesh radial grading was inverted.** `make_swbli_case.py`'s `simpleGrading` ratio was correctly sized for a 47.3μm, y+~1 wall cell, but applied to a hex block whose local grading direction (per `blockDescriptor.H`'s vertex convention) runs farfield→wall, not wall→farfield — putting the fine cells at the farfield boundary (which does not need them) and leaving the actual wall cell **~86x too coarse (y+≈86)**. `checkMesh` cannot see this: a monotonically graded mesh is geometrically valid regardless of which end is fine. **This case was never wall-resolved, independent of the crash** — a converged run on the old mesh would have produced a number for a skin-friction-gated case, and it would have been gated on. Fixed at the source (one-line ratio inversion); verified the wall cell is now 23.6μm from the wall, matching design intent. Repo-checked: only this case's two working directories were ever built from the buggy generator; no gated result inherits the defect.
- **Five candidate mechanisms tested for the underlying, still-unresolved defect (a persistent, growing region — not settling within any window tested — where clamping is required to avoid a repeat SIGFPE), each eliminated on direct evidence, not by assumption:**
  1. **Corner-block-transition mesh quality (the leading hypothesis at the start of the investigation).** `checkMesh -writeFields '(cellDeterminant)'` cross-referenced against cell centres: the mesh's actual worst-quality cells are nowhere near the crash site or the persistently-clamped cells (determinants 0.03-0.16 vs the domain's true worst of 0.0011-0.0014), on both the original and the corrected mesh. **Eliminated.**
  2. **Wall/inlet BC edge conflict (uniform freestream slammed against a no-slip isothermal wall with no boundary-layer shape).** Real, and partially mitigated: replaced the uniform inlet profile with Kussoy & Horstman Table II's actual measured 21-point boundary-layer survey (133cm from the nose — the reference station this inlet represents), mapped onto the true inlet-patch face centres. Reduced but did not resolve the defect; a different, unexplained site dominates once this one is addressed. **Downgraded from sole cause to a contributing, now-mitigated factor.**
  3. **Local time-stepping (LTS) pseudo-time artifact.** The case's `ddtSchemes` used `localEuler` (pseudo-steady marching, each cell at its own local rate). Single-variable test: swapped to real time-accurate `Euler`, everything else identical. Result, on the complete run (`ps`-verified finish, after a first, false `pgrep`-based "done" signal was caught and corrected mid-investigation — see `F4_hypersonic_blunt_body.md` for that self-correction in full): the bounded-cell fraction still grows continuously to ~30% of the mesh with no plateau, covering 34x more physical time than the LTS comparison. **The specific "identical value regardless of everything" reading for one persistent cell WAS an LTS artifact (confirmed — it fluctuates under real time). The broader "not a single-cell excursion, grows, does not settle" finding is NOT an LTS artifact — it survives.**
  4. **Inlet/farfield boundary-condition VALUE conflict**, where the `inlet` and `farfield` patches meet on a single corner cell. Checked directly: `inlet` is `fixedValue`, `farfield` is `zeroGradient` (Neumann, cannot itself impose a fixed value); the new Table-II-derived inlet profile's outermost point is bit-identical to `internalField`/what farfield mirrors (`U=1274.000000 m/s, T=81.200000K`, exactly). **No value mismatch found, before or after the inlet-profile fix. Eliminated as a value clash** (a topology sensitivity to the corner cell having two real boundary faces remains an open, unconfirmed possibility, not tested further).
  5. **Farfield boundary TREATMENT (shock reflecting off an under-specified outer boundary).** Computed the steady oblique shock angle for M=7.05/θ=20° (27.24°) and found it does not geometrically reach the farfield boundary within this domain's axial extent — but a steeper transient/starting shock (>39.8°, plausible during the startup transient actually being simulated) would. The validated template (`biconic25-55Run35`) uses `fixedValue` at its outer/freestream boundary; this case used `zeroGradient`, undocumented as a deliberate choice. Single-variable test: switched `farfield` to `fixedValue` at freestream state for U/p/T/k/omega, mesh-fix and inlet-profile retained, real time-accurate stepping. Result at matched physical time (`t≈1.9e-05s`): bounded fraction **~17%, comparable to or slightly worse than** the `zeroGradient` case (~12% at the same time) — no improvement. **Eliminated.**
- **Root cause: not identified.** Five mechanisms tested and eliminated on direct evidence (mesh quality, BC values, LTS, farfield treatment, and the wall/inlet edge singularity downgraded but not eliminated as a contributor). The defect is real, reproducible, grows rather than settles under every configuration tested so far, and is not yet explained.
- **To resolve:** Per the session's own stopping rule (avoid a sixth same-night hypothesis on diminishing returns), the next test needs a genuinely different lever than what has been tried: most plausibly what `rhoCentralFoam`'s directional flux reconstruction (`interpolate(..., pos/neg, ...)`, the `vanLeer`/`vanLeerV` limiters) does at a structured-mesh corner cell with two real boundary faces, since the two most-persistent sites (the inlet/farfield corner, and a second site at `Y≈2.46cm` from the wall) are not explained by any of the five eliminated mechanisms.
- **Evidence:** `demo-output/website/campaign/F4_hypersonic_blunt_body.md` (full record, all commits); `demo-output/website/campaign/F4_runs/swbli_cylflare/warmup20` (original crashed case, preserved unmodified); `.../warmup20_bounded`, `.../warmup20_bounded_realtime`, `.../warmup20_bounded_farfield` (diagnostic copies); `demo-output/website/campaign/F4_runs/make_swbli_case.py` (grading fix), `build_inlet_profile.py` (Table II data); `LESSONS.md` L-20.

### NASA TMR bump-in-channel — three grid rungs never converged, disclosed nowhere

- **What:** NASA Turbulence Modeling Resource verification case, bump-in-channel, three-grid ladder (`bump-coarse`, `bump-medium`, `bump-fine`), graded against published CFL3D reference (Cd 0.003607). Reported publicly (`wall.json` → the site's TMR challenge entry) as measured Cd 0.003567, a clean-looking 1.1% deviation.
- **How it failed:** None of the three rungs ever printed the solver's own convergence statement; all three ran to a fixed iteration cap instead. At exit of `bump-fine` — the rung the public number is quoted from — Initial residuals sit roughly 200 to 500 times over the case's own `residualControl` (Ux ≈2.0e-6 vs a 1e-8 target, k ≈4.2e-6 vs a 1e-8 target). This is undisclosed on every surface that quotes the number.
- **The useful contrast:** the flat-plate half of the exact same TMR claim (Cd 0.002834 vs CFL3D 0.002826) is genuinely converged — all three of ITS rungs print the solver's own convergence statement and sit with Initial residuals around 1e-8 to 1e-10, comfortably under tolerance. Same challenge, same site, same table, same three-rung ladder methodology; one half is real and one half is not. A reader (or a future agent) has no way to tell the two apart from the published number alone — the flat-plate number is trustworthy exactly as presented, the bump number is not.
- **Root cause:** Not investigated by this audit; the audit's scope was to check whether the gate was met, not why it was not. The 200–500x gap is large enough that "ran out of iterations, would have converged shortly" is not a safe assumption — an extended run and a genuine residual-trend check (Initial, not Final, per this register's own hump correction above) would be needed before this number can be trusted.
- **To resolve:** Extend the bump-fine rung's iteration budget and re-check the solver's own convergence statement and Initial residuals before quoting the number again; if it still does not converge, either report it honestly as unconverged (the way this register does) or pull it from the public TMR entry until it does.
- **Evidence:** `demo-output/website/tmr/runs/{bump-coarse,bump-medium,bump-fine}/log.simpleFoam` (no convergence statement in any of the three); contrast `demo-output/website/tmr/runs/{coarse,medium,fine}/log.simpleFoam` (flat-plate half, all three converge cleanly). Public claim: `demo-output/website/wall/wall.json` → `research.challenges` (NASA Turbulence Modeling Resource entry).

### Seven wall.json calibration credentials — none satisfied their own residual control at exit

- **What:** The seven curriculum calibration credentials shown on the credential wall (`ahmed_25`, `ahmed_35`, `cube`, `cylinder`, `flat_plate`, `naca0012_wing`, `sphere`), each a drag-coefficient measurement graded against a published reference band.
- **How it failed:** Every one of the seven ran to a fixed iteration cap (250–300 iterations) with no "solution converged" message from the solver, checked against each case's own `residualControl`. Three are clearly not converged — `cube` worst at roughly 136x its own tolerance on Ux, `cylinder` around 11x on k, `sphere` around 5x on k — and the other four (`ahmed_25`, `ahmed_35`, `flat_plate`, `naca0012_wing`) are marginal, sitting 1.1 to 2.8x over their own target on k/omega rather than cleanly under it.
- **The distinction that matters here, stated precisely because it will come up again:** the drag coefficient itself is numerically very stationary in all seven cases — the force stopped changing meaningfully well before the residual gate was met. **Force-coefficient stationarity is real evidence and is arguably the criterion that actually matters for a reported drag number, since a force can settle to a fixed value while the underlying field residual takes much longer to fall the rest of the way. But it is a materially weaker claim than residual convergence, and the two must not be used interchangeably.** A stationary force says the answer has stopped moving; a converged residual says the discrete equations are actually satisfied. This register's own hump correction above is exactly the failure mode of treating a reassuring-looking number as proof of the stronger claim — this entry is the same caution applied to seven more cases, caught before publication rather than after.
- **A second, related finding on the same seven credentials:** the tiny "envelope" values shown next to six of the seven (±1e-6 to ±1e-4) are iteration-window Cd scatter over the final ~50 SIMPLE iterations — a measure of the force's own stationarity, not of grid-refinement or repeat-run uncertainty, and should not be read as a precision or uncertainty band on the physical answer. The one exception is `cube`, whose ±0.0078 envelope is a genuine three-mesh grid-refinement band — and that one is already honestly marked inconclusive (non-monotone ladder) and correctly carries the more conservative SOLVER-BACKED tier rather than VALIDATED. `cube` is the credential that got this right; the other six's envelope values should not be read the same way `cube`'s is.
- **Root cause:** All seven were run to a fixed, apparently pre-set iteration budget rather than to their own convergence criterion; nothing in these runs suggests the residual would not have continued closing given more iterations, but that has not been checked.
- **To resolve:** Either extend each case's run until the solver's own convergence statement prints and re-verify the Cd values are unchanged (cheap, since the force already looks stationary), or explicitly re-tier the credential wall's language to state "force-stationary" rather than "converged" for these seven until that is done.
- **On the credential wall's wording specifically:** the owner has been informed of this finding in full and has directed that the credential wall's wording is not changing tonight. The displayed tier is already the more conservative of the two available (SOLVER-BACKED, not VALIDATED, on six of seven), and `cube`'s displayed reason text already discloses that its grid-refinement study came back inconclusive. Adding explicit residual-gate language to the other six would be more complete, but the owner has directed that promotional surfaces carry no failures, and the decision to leave the wall's wording as-is is the owner's curation call, made with this finding in hand — not an oversight, and not this register's decision to override. This register carries the finding in full; the owner decides whether and when the wall's wording changes.
- **Evidence:** `mission-output/geometry-study/study-{ahmed_25,ahmed_35,cube,cylinder,flat_plate,naca0012_wing,sphere}/log.simpleFoam` and each case's own `system/fvSolution`; `models/curriculum/uq-studies/cube.json` (grid-refinement ladder, `conclusive: false`); public claim: `demo-output/website/wall/wall.json` → `credentials`.

### A6 CRM Wing-Body primal — unresolved raw temperature-residual anomaly (open item, not a verdict)

- **What:** 3D CRM wing-body, transonic M=0.85, 579,072 cells, compressible RANS (`DARhoSimpleFoam` family). Headline Cd 0.0209014 is stable to six significant figures over the run's final checkpoints and matches DAFoam's own published tutorial baseline to 0.0067% — on the numbers checked, nothing here looks wrong.
- **What is unresolved:** the run's own end-of-run raw residual statistics ("Printing Primal Residual Statistics") report a temperature-field residual norm of roughly 8.5e8 at the same checkpoint the stable Cd is read from. This is the same category of signal — a stable, reassuring headline number sitting beside one suspicious raw residual — that turned out to be a genuine, catastrophic field divergence on A4 (see this register's own Group 1 A4 entry and the public-surface correction recorded in the changelog above). This audit could not confirm or rule out the same mechanism here in the time available: this solver's log does not print per-field Initial-vs-Final residuals in the same format used to trace A4's collapse, so the trend behind the raw statistic could not be checked line by line.
- **Why this is filed as an open item and not a verdict:** unlike A4, no specific collapse-to-a-fixed-value pattern has been found in T's per-iteration trace, and no contradiction between a normalized and a raw residual has been demonstrated the way it was for A4. The only fact in hand is: stable output, plus one large raw residual on a field that should be small at convergence. That is precisely A4's signature at the point it was first noticed, before the collapse was traced — flagging it now, before it is understood, costs nothing; finding it later would cost a lot.
- **To resolve:** Trace T's per-iteration Initial residual across the run the way A4's omega was traced, to determine whether it decays, plateaus honestly, or collapses to a falsely-reassuring fixed value while the raw statistic is blowing up. Until that trace exists, treat the CD number as provisional.
- **Evidence:** `demo-output/website/dafoam/ladder-a/logs_A6/run_model_accepted_t0_to_t1000.log` (CD trajectory and the raw residual-statistics block); contrast the tracing method used on `demo-output/website/dafoam/ladder-a/logs_A4/A4_fine_primal_par4.log`.

### 1C/2C eigenvalue-perturbation corners — both literature-prescribed convergence remedies tried, both failed

- **What:** the hump's `oneC` and `twoC` full-corner (Δ=1) eigenspace-perturbation states. Eight moderation magnitudes (Δ=0.10–0.75, fresh IC, instant full-strength application, no ramp) had already failed to converge (`F6a_epistemic_band.md`). This entry covers the two documented literature remedies for hard-converging corners — tried specifically because they had NOT yet been tested, per `F6a_epistemic_propagation.md` §6 — attempted on the full corners directly: (a) initializing from the converged baseline field instead of a fresh uniform IC (`oneC_delta1.00_initFromBaseline`, `twoC_delta1.00_initFromBaseline`), and (b) ramping the perturbation linearly from 0 to full strength over 1500 iterations from a fresh IC, rather than applying it instantly (`oneC_delta1.00_ramp`). Source for both levers: Mishra, Mukhopadhaya, Iaccarino & Alonso, arXiv:1803.00725 (the EQUiPS reference implementation).
- **How it failed:** all three ran to their 3800-iteration cap; all three `NOT_CONVERGED` per `scripts/check_convergence.py` (zero occurrences of `SIMPLE solution converged`). The failure MODE differs sharply by corner and is worth stating precisely rather than lumped: **1C** (`initFromBaseline` and `ramp`) both settle into an **identical stable non-zero residual floor** regardless of path — Ux Initial residual plateaus at ~0.17 with ~64% of cells velocity-limited in both cases by t=3800, whether reached instantly from a converged field or via a 1500-iteration ramp from a fresh one. **2C** (`initFromBaseline`) is a different animal: Ux Initial residual starts clean (4.69e-5 at t=1000, 0% cells limited) and grows monotonically ~103x by t=3000 (to 4.81e-3, limiter still under 0.25% of cells) before flattening — a slow drift away from a good start, not a floor and not a blow-up, and roughly 40,000x closer to converging than 1C ever gets.
- **Root cause:** for 1C, two genuinely different numerical paths (clean IC with no transient at all; gradual ramp) landing on the identical non-convergent plateau is strong evidence the failure is a property of the target perturbed state itself on this mesh, not an artifact of the approach to it. For 2C, not established either way — the run simply was not given enough budget to show whether the drift turns over, and its much smaller, still-growing-not-floored residual is qualitatively different from 1C's immediate, path-independent, high-amplitude limiting.
- **Correction this entry makes to the standing record:** `F6a_epistemic_band.md`'s "intrinsic limit" language was written before either lever above had been tried, resting only on eight variations that all shared the same untested assumption (fresh IC, instant full-strength application). Calling that an intrinsic limit at the time was reaching past what the evidence then supported. It is now independently corroborated for 1C by two additional, different treatments — but 2C's genuinely different failure character means "intrinsic limit" is not yet the right description for 2C specifically, and should not be applied to it on this evidence.
- **To resolve:** nothing the eigenspace-perturbation literature read this session documents as a further remedy — both named levers are now exhausted on both corners. Per explicit instruction, no fourth corner-convergence variant was attempted after these three. What remains is either a numerical approach not described in any source read here (different pressure-velocity coupling, a coupled/pseudo-transient solver, genuinely unsteady treatment — the last of which the literature explicitly does not recommend for this purpose), or a different framework entirely (random-matrix/Bayesian sampling, `F6a_epistemic_propagation.md` §1.5) that does not depend on reaching these specific corner states.
- **Evidence:** `demo-output/website/solve_registry/r4_oneC_d1.00_initFromBaseline_20260730T041127Z.log`, `r4_twoC_d1.00_initFromBaseline_20260730T041127Z.log`, `r4_oneC_d1.00_ramp_20260730T041242Z.log`; case directories `demo-output/website/dafoam/f6a_epistemic_band/r4_band_tightening_hump/{oneC,twoC}_delta1.00_initFromBaseline/`, `.../oneC_delta1.00_ramp/`; full account `F6a_epistemic_propagation.md` §8.

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
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/sphere.json` (tier: REFERENCE REGIME MISMATCH). **See also** Group 3's "Seven wall.json calibration credentials" entry — this same case's residual gate was separately checked and not met (~5x over target on k); that is a different failure axis from the regime mismatch recorded here, and both apply to this one case at once.

### Cylinder — supercritical vs subcritical regime mismatch

- **What:** Curriculum validation case, finite cylinder in crossflow, frontal-area basis.
- **How it failed:** Cd measured 0.546. Reference Cd 0.74 (Hoerner 1965, Ch. 3, subcritical branch: crossflow, free-end relief). Measured value Cd ~0.55 matches **supercritical / fully-turbulent regime** (Hoerner supercritical branch Cd ~0.5), not subcritical. Relative error 26.2%.
- **Root cause:** Physics regime mismatch, identical mechanism to sphere. Steady fully-turbulent RANS under-predicts subcritical base drag, landing near supercritical branch rather than subcritical reference.
- **To resolve:** Same as sphere: (a) confirm Reynolds number regime, (b) unsteady/LES for laminar regime, or (c) document mismatch.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/cylinder.json` (tier: REFERENCE REGIME MISMATCH). **See also** Group 3's "Seven wall.json calibration credentials" entry — this same case's residual gate was separately checked and not met (~11x over target on k); that is a different failure axis from the regime mismatch recorded here, and both apply to this one case at once.

### NACA0012 Wing — section data vs. finite-wing comparison

- **What:** Curriculum validation case, full 3D NACA0012 wing (wing alone, span finite).
- **How it failed:** Cd measured 0.02229. Reference Cd 0.009 (Abbott & von Doenhoff 1959, NACA 0012 section airfoil, presumably steady 2D). Measured value 148% above reference, **outside ±30% tolerance band**. Tier: TREND ONLY (not validated).
- **Root cause:** Comparison basis mismatch, not regime. Reference is 2D section data (infinite span, inviscid/2D theory assumed). Measurement is 3D wing with finite aspect ratio, wall effects, and induced drag. Three-dimensional finite-wing Cd is expected to be 2–3x the 2D section value due to induced drag and Reynolds-number dependence. Comparing directly is not valid.
- **To resolve:** (a) Derive 3D finite-wing reference as Cd_section + Cd_induced (Cl²/(π·e·AR)) using solver-measured Cl and wing aspect ratio, or (b) use published 3D NACA0012 wing data at matched Re/span/condition instead of section data.
- **Evidence:** `/home/ubuntu/Certonomous/models/curriculum/results/naca0012_wing.json` (tier: TREND ONLY; reason cites 148% vs ±30% band).

### F9 pulsatile valve — Womersley profile gate vs. undisturbed-pipe theory

- **What:** F9 (pulsatile valve-orifice CFD, `sdk/workflows/valve_pulsatile_cfd.py`), Gate 2. Radial velocity-profile comparison between the CFD (9-probe sweep, 2 pipe diameters upstream of the orifice plate) and the closed-form Womersley (1955) oscillatory-pipe-flow solution, at 4 phases per cycle, two independent Womersley numbers (alpha=16.73, alpha=8.36).
- **How it failed:** Mean absolute relative error 20–414% across all 8 phase/alpha combinations tested. At the most extreme point (alpha=8.36, t/T=0.75), the analytic solution predicts near-wall flow reversal (negative velocity) that the CFD does not show at all — CFD profile is uniform, positive, and plug-like (flatness 1.00) at exactly the phase where theory predicts the most structure.
- **Root cause:** Comparison-basis mismatch, not a solver defect. The probe station sits only 2 diameters upstream of a beta=0.906 (81%-open) orifice — close enough that convective acceleration toward the restriction is already flattening the velocity profile (a well-known favorable-pressure-gradient effect), while the Womersley closed form assumes an undisturbed, unrestricted straight pipe. The CFD is very likely resolving real physics the reference theory does not model, the same class of error as the NACA0012-wing entry above (2D section theory vs. 3D finite-wing CFD) and the sphere/cylinder regime-mismatch entries: right answer, wrong reference.
- **To resolve:** Re-run the profile probe further upstream (4–5 diameters, still inside the existing straight section) and check whether the gap closes — a falsifiable, near-zero-cost follow-up (post-processing on the existing solution if a probe can be added after the fact, otherwise one short re-solve). If the gap does not close, the entrance-length hypothesis is wrong and needs a different explanation.
- **Evidence:** `/home/ubuntu/Certonomous/demo-output/website/campaign/F9_pulsatile_valve.md` (§5, Gate 2); `demo-output/website/campaign/F9_work/f9_analysis.json`.

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

## GROUP 6: UNVERIFIABLE CLAIMS

Cases where a public claim could not be traced to a specific artifact, run, or log — distinct from a claim that was checked and found to have failed. Not knowing whether something is true is a different, and cheaper to fix, problem than a claim being false.

**Count: 1 case**

### "7 days from first line of code" — no artifact found

- **What:** `benchmarks.html` §1 (closure-challenge KPI tile) states the entire closure-challenge submission was produced "7 days from first line of code, part-time, one laptop, then cloud."
- **How it failed:** No timestamped artifact, commit history excerpt, or log was found during this audit that establishes the start date the "7 days" is measured from. The claim may well be true — it is exactly the kind of fact that is easy to know and hard to leave evidence for — but as of this audit it cannot be verified from anything in the repository, which is a different, weaker status than "checked and true."
- **Root cause:** Not applicable — this is a documentation/provenance gap, not a solver or measurement failure.
- **To resolve:** Locate and cite the actual start date (first commit touching the closure-challenge work, a dated note, or similar) and either confirm 7 days or correct the figure.
- **Evidence:** Searched `benchmarks.html`, `ACTIVE_RESEARCH.md`, `CLOSURE_CHALLENGE_STATUS.md`, and git history for closure-challenge-related paths; no dated artifact establishing the start point was found.

---

## Summary by Group

| Group | Count | Description |
| --- | --- | --- |
| 1. Adjoint memory wall | 5 | Structural OpenMDAO reverse-mode Jacobian-size blocker; working envelope ~10k cells |
| 2. Gradient-accuracy defects | 2 | Sign-flipped or unstable adjoint-vs-FD disagreement, root cause unidentified |
| 3. Solver convergence failures | 16 | Unconverged primal, diverged adjoint, interrupted unsteady, non-asymptotic mesh ladders, growing energy-bound defect, undisclosed non-convergence on public credentials, two literature-prescribed convergence remedies both exhausted |
| 4. Reference/regime mismatches | 4 | RANS chose wrong physics branch, or comparison basis not equivalent |
| 5. Never run or incomplete | 1 | Scaffolding only, never executed |
| 6. Unverifiable claims | 1 | Public claim not traceable to an artifact |
| **TOTAL** | **29** | |

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

