# Bug report: the v5 matrix-free adjoint operator depends on the mesh decomposition — GMRES converges to 1e-6 on an operator that is not the transpose Jacobian, and the gradient error reaches 10% at np=4

**Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been
contacted, nothing has been posted.** This document is prepared to be filed against
`mdolab/dafoam` (v5, matrix-free/JacobianFree adjoint). **Whether it is sent is
Katie's call, not the lab's.** No upstream report of a decomposition-dependent DAFoam
gradient exists (issue and discussion searches recorded in
`LIAISON_RESEARCH_adjoint_conditioning.md`, 2026-08-04, all negative), and the
toolchain's journal paper reports average adjoint derivative error under 0.1% at up
to 1536 cores — this report, if filed, contradicts that published claim on a
measured case and therefore needs the evidence standard below.

## Summary

On a 2,777-cell OpenFOAM case (Ahmed body, `DASimpleFoam`, kOmegaSST, one FFD shape
variable), `check_totals` gives, on the same mesh, same runScript, same container,
with **only the decomposition varied**:

| configuration | analytic dCD/dshape | FD (same run) | rel. error |
|---|---|---|---|
| np=1 | 2.4150e-01 | 2.4232e-01 | 0.34% |
| np=2 | 2.4118e-01 | 2.4182e-01 | 0.26% |
| np=4, `scotch` (default) | 2.2086e-01 | 2.4258e-01 | **8.95%** |
| np=4, `simple` 4x1x1 | 2.4220e-01 | 2.4220e-01 | 0.00054% |
| np=4, `simple` 1x4x1 | 2.4379e-01 | 2.4265e-01 | 0.47% |
| np=4, `scotch`, `gmresRelTol` 1e-10 | 2.2086e-01 | 2.4258e-01 | 8.95% (unchanged, 811 iters, reason 2) |

The converged baseline CD is invariant to five significant figures across all
configurations (0.15296979-0.15297237), the FD column varies 0.36%, and the RHS
dFdW is invariant to 5e-06 when mapped across decompositions. Only the adjoint
solution moves. (Numbers measured with a locally patched IDWarp to remove the
independent `getRotationMatrix3d` degenerate-branch defect of `idwarp#57`; the
decomposition effect exists stock too — stock scotch reads 10.04%, stock simple
4x1x1 reads 0.76%.)

## The discriminating measurement: the converged scotch adjoint does not satisfy the serial adjoint system

Dump the converged adjoint psi at np=4 `scotch`, permute it to the np=1 state
ordering using `cellProcAddressing`/`faceProcAddressing` (sign carried for flipped
faces) plus the `writeJacobians: ["adjointIndexing"]` maps, and evaluate the true
residual under the **serial** operator with DAFoam's own
`solverAD.calcJacTVecProduct` (state -> residual, reverse):

| psi from | ||dRdW^T psi + dFdW|| under the np=1 operator | ratio to ||dFdW|| |
|---|---|---|
| np=1 (control) | 2.1e-05 | 1.1e-04 |
| np=4 `scotch` | **6.0e+01** | **3.3e+02** |
| np=4 `simple` 4x1x1 | 1.7e-02 | 9.4e-02 |

Yet the scotch KSP itself finishes at true-residual 1.7e-07 on its own operator
(`PetscConvergedReason: 2`, right-preconditioned GMRES, unpreconditioned norm). The
same vector, evaluated under the serial operator and under the scotch-decomposed
operator, gives residuals five orders of magnitude apart: **the two operators are
different linear maps.** The linear solver is doing its job on the wrong system,
which is why no tolerance, restart, or preconditioner setting changes the answer.

**Added 2026-08-04** (per the mechanism supervisor sweep,
`demo-output/website/dafoam/VERIFICATION_A4_mechanism_supervisor_sweep.md`, commit
8e0a08bc): nor is the scotch operator the exact adjoint of an
equivalent-but-different parallel discretization — such an adjoint would match the
finite difference of its own decomposed discretization, and it does not: the FD
column in the table above is computed per run inside each arm's own
`check_totals`, so the scotch analytic 2.2086e-01 disagrees by 8.95% with its own
decomposition's FD of 2.4258e-01.

Controls closed before this claim:

- **Linearization state.** Re-evaluating the cross-residual with the serial operator
  linearized at the scotch arm's own (mapped) converged state leaves it unchanged to
  the printed six digits (6.004094e+01 at either state); the reconverged-primal
  state difference contributes at the 1e-03 level (the np=1 control moves from
  1.14e-04 to 1.0e-03 of ||b|| under the same state swap).
  The `simple` arm's state differs *more* from np=1 than scotch's does (2.8e-03 vs
  2.0e-03 relative) and its cross-residual is 3,500x smaller.
- **Mapping.** The permutation is integer addressing, not coordinate matching; the
  duplicated processor-face phi states of the primal agree across the map to
  2.7e-15, and replacing the psi duplicate-average by either copy moves the
  cross-residual by at most 9.1e-03.
- **RHS.** dFdW mapped across decompositions is invariant to 4.8e-06 relative.
- **Coloring/preconditioner.** In the JacobianFree path the coloring builds only
  `dRdWTPC`, and a wrong PC cannot move a right-preconditioned GMRES solution
  converged in the unpreconditioned norm (`DALinearEqn.C:170,313`) — which this
  solve was (reason 2, true-residual 1.7e-07). A confirmatory coloring-off run
  could not be completed: see the usability note below.

## Localization

The cross-residual against the serial operator concentrates in the **x-momentum rows
of partition-interface cells**: 13 of the 15 entries with |r| > 0.5 sit on cells
owning a scotch processor face (the other 2 at graph distance 1), largest entry
42.2. The same instrument on `simple` 4x1x1 maxes at 0.0084 on its own interface
cells. The worst cells touch exactly one foreign rank through exactly one processor
face — this is not a many-rank corner effect — and the error depends strongly on cut
orientation/shape: x-normal planar cuts are clean (0.00054%), y-normal planar cuts
read 0.47%, scotch's jagged mixed-orientation boundary reads 8.95%. The adjoint
solution norm itself inflates 16.5x under scotch (pressure and z-momentum blocks) at
identical RHS norm.

Because the KSP shell operator (`dRdWTMatVecMultFunction`, global CoDiPack tape
recorded by `initializeGlobalADTape4dRdWT`: register state inputs ->
`updateStateBoundaryConditions` -> `calcResiduals` -> register residual outputs) and
the `calcJacTVecProduct` path agree with each other on the scotch arm while both
disagree with the serial operator, the defect is common to the recorded reverse
tape, i.e. in the reverse-AD treatment of the inter-processor (halo/processor-patch)
coupling of the residual evaluation, not in one call site, not in the coloring, not
in the linear algebra. We have not traced it to a line; that requires an
instrumented rebuild of `libDASolver.so`.

## Why existing verification did not catch this

- `check_totals` at np=1 or on planar `simple` decompositions of conformal meshes
  reads 0.1-1% — three further cases in this lab (structured/conformal meshes,
  np=4 scotch) are decomposition-invariant at the 1e-04 level. The effect needs a
  partition boundary shape that excites it; scotch on a snappyHexMesh-style mesh
  did, planar cuts on the same mesh did not. A test matrix that never varies the
  decomposition at fixed np cannot see it, and a wrong gradient that is *consistent
  under the tested decomposition* passes any single-decomposition dot-product test.
- The published <0.1% multi-core verification would not catch an operator defect
  whose magnitude depends on partition geometry if its cases/partitions sit in the
  benign regime the lab's own conformal-mesh cases occupy.

## Usability finding, separate but adjacent

`adjUseColoring: False` **hard-crashes the v5 mphys Krylov path by construction**:
`solve_linear` skips `runColoring()` when the option is False, but `calcdRdWT`
unconditionally calls `readJacConColoring()`, which reads a never-written file and
aborts in `DAColoring::validateColoring` (`DAColoring.C:1021`). The identity-coloring
fallback exists only inside `calcJacConColoring`, reachable only via `runColoring()`.
Workaround attempted here: call `DASolver.solver.runColoring()` explicitly before
`compute_totals` with the option False — the identity coloring is then accepted
(`nJacConColors` = nGlobalAdjointStates), but the per-column FD assembly is
memory-unbounded in practice: on a 2,777-cell case (colored path: <2 GiB) it
thrashed an 8 GiB container cap and then a 20 GiB cap, the second attempt dying
*after* all 26,149 column evaluations completed, consistent with the
connectivity-unrestricted FD columns of an elliptically coupled residual being
nearly dense. As shipped, `adjUseColoring: False` is effectively unusable in the
v5 Krylov path.

## Reproduction protocol (what a maintainer needs)

1. Any case showing decomposition sensitivity in `check_totals` (this lab's is a
   2,777-cell Ahmed body; np=1 vs np=4-scotch analytic gradients differ 9.4%).
2. The cross-residual harness — pure DAFoam public API, no rebuild:
   dump psi (`DAFoamSolver.psi`), states, and dFdW per decomposition; write
   `writeJacobians: ["adjointIndexing"]`; map with
   `cellProcAddressing`/`faceProcAddressing`; evaluate
   `solverAD.calcJacTVecProduct(state->residual)` at np=1 with the mapped psi.
   Scripts in this lab: `W4-a4-discriminators/runScript_w4.py` (tasks `w4_dump`,
   `w4_crossres`, `w4_crossres2`), `build_maps.py`, `analyze_mats.py`.
3. Environment: `dafoam/opt-packages:latest` (dafoam 5.0.0, OpenFOAM v2506),
   full logs and per-arm case dirs under
   `/home/ubuntu/certonomous-runs/W4-a4-discriminators/`.

## Submission readiness

| requirement | state |
|---|---|
| Reproducer on a stock upstream tutorial (outside this lab's tree) | **NOT DONE.** The measured case is lab-built (its mesh recipe and case dirs are archived and shippable, but it is not an official tutorial). A tutorial-based reproducer should vary `decomposeParDict` daOption on an official case before filing. |
| Mechanism to a line | **NOT DONE** — subsystem-level only (parallel reverse tape); line-level needs an instrumented rebuild. |
| Discriminating instrument a maintainer can run | **Done** (cross-residual protocol above, public API only). |
| Independent verification of the phenomenon | **Done** — adversarial supervisor sweep with an independent re-run reproducing a table cell to every printed digit (`VERIFICATION_A4_decomposition_supervisor_sweep.md`). |

Evidence record behind this report:
`DISCRIMINATORS_A4_decomposition_mechanism.md` (this session),
`PROOF.md` §25.5, `VERIFICATION_A4_decomposition_supervisor_sweep.md`.
