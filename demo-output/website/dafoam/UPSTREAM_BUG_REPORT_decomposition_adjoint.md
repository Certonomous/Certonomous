# Bug report: the v5 matrix-free adjoint operator depends on the mesh decomposition — GMRES converges to 1e-6 on an operator that is not the transpose Jacobian, and the gradient error reaches 10% at np=4

**Status: NOT FILED ANYWHERE. No issue has been opened, no maintainer has been
contacted, nothing has been posted.** This document is prepared to be filed against
`mdolab/dafoam` (v5, matrix-free/JacobianFree adjoint). **Whether it is sent is
Katie's call, not the lab's.** No upstream report of a decomposition-dependent DAFoam
gradient exists — 63 recorded searches across 10 venues, all negative on point
(`LIAISON_RESEARCH_adjoint_conditioning.md`, 2026-08-04, and the full novelty sweep
`LIAISON_NOVELTY_SWEEP_decomposition_defect.md`, commit 3c74dc03: the word "scotch"
appears in zero issues and zero discussions in the project's history). The report
still needs the evidence standard below, because of what it claims about a shipped
default, not because it argues with a published number:

**Corrected 2026-08-05** (per `DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`, commit
bf6ac53b — all three method papers now READ IN FULL). An earlier revision of this
header said the toolchain's journal paper "reports average adjoint derivative error
under 0.1% at up to 1536 cores" and that this report, if filed, contradicts that
published claim. That characterization was wrong twice, and is withdrawn:

- **The <0.1% and the 1536 cores were never one measurement.** AIAA J 2020
  (He, Mader, Martins, Maki, DOI 10.2514/1.J058853, READ IN FULL) joins two
  disjoint experiments in its abstract: the 1536 cores is Table 2, a
  runtime-only scaling measurement on a 10.1M-cell structured mesh; the <0.1%
  is Table 3, an accuracy study on a 102,912-cell mesh at an **unstated** core
  count. "decompose", "processor" and "scotch" appear nowhere in the paper. No
  accuracy number at any stated core count exists in it.
- **Both published <0.1% figures attach to the v1 explicit FD-coloring Jacobian
  architecture** (C&F 2018 Tables 4–5; AIAA J 2020 Table 3, which explicitly
  defers the Jacobian-free approach to "future work") — not to the matrix-free
  reverse-AD operator this report measures. The operator family v5's
  `calcJacTVecProduct` descends from has exactly **one** published accuracy
  measurement, and it is serial by design (Kenway, Mader, He, Martins,
  PAS 2019, §5.1 + Conclusions, READ IN FULL): *"We do not have scalability
  data for the Jacobian-free (operator overloading) and the full-code AD
  (operator overloading) options because we run the adjoint computation only
  in serial in the ADODG Case 3 (Sec. 5.1)."*

This report therefore does not contradict a published measurement; **it fills a
hole the survey's own conclusions declare**, in a region the 2018 paper's §2.9
flags as accuracy-critical (*"essential for accurately computing the adjoint
derivative"* — full quote in "Why existing verification did not catch this"
below). That strengthens the report: it no longer argues against a peer-reviewed
number.

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

**Rewritten 2026-08-05 from the method papers read in full**
(`DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`, commit bf6ac53b; reading notes
`W2_DAFOAM_CAF2018_VERIFICATION_READING.md`,
`W2_DAFOAM_AIAAJ2020_VERIFICATION_READING.md`,
`W2_KENWAY_PAS2019_EFFECTIVE_ADJOINT_READING.md`, all READ IN FULL). The earlier
bullet here about "the published <0.1% multi-core verification" is superseded —
that verification never existed as one measurement (see the header correction).
What the papers' own protocols actually cover, line by line:

- **No paper ever varies the decomposition of anything.** Decomposition is not
  an experimental axis anywhere in the method-paper corpus — not at fixed np,
  not across np. The two papers that verify the v1 operator in (implied)
  parallel never state what the decomposition was (C&F 2018 §3.1; AIAA J 2020,
  "decompose"/"processor"/"scotch" absent). A single-decomposition test cannot
  see this defect even in principle.
- **The operator this defect lives in was verified once, serially, on purpose.**
  PAS 2019 §5.1: *"running the cases using one CPU core allows us to isolate
  the impact of parallel communication on the performance"*; Conclusions: the
  serial-only sentence quoted in the header. The matrix-free reverse-AD family
  entered the literature with its parallel behavior explicitly outside the data.
- **No verification anywhere in the corpus combines a refinement-interface mesh
  with a stated graph partitioning.** The one snappy-mesh gradient check
  (C&F 2018 Tables 4–5 — an Ahmed body, this report's geometry family:
  dCD/du0 to −0.00049% and four FFD components averaging <0.1%) is of the v1
  FD-assembled Jacobian at an unstated decomposition — an architecture built
  from evaluations of the true parallel residual with halo exchanges executed
  natively, in which a tape-recording defect cannot exist. If those runs were
  scotch-partitioned, the result is *consistent* with our measurements: our FD
  and primal columns are decomposition-robust too; only the v5 tape operator
  moves.
- **The delicate region was named by the authors themselves, for the
  architecture that handled it.** C&F 2018 §2.9, verbatim: *"when we perturb
  the velocity of a cell immediately next to an interprocessor boundary patch,
  we need to interpolate the perturbed velocity onto this boundary patch. This
  is done by calling U.correctBoundaryConditions() in OpenFOAM. ... Note that
  updating the boundary condition is essential for accurately computing the
  adjoint derivative."* In v1 that coupling is handled by *executing* the
  update per perturbation; in v5 the same coupling must be *recorded on the
  reverse tape*, and the cross-residual above localizes the defect to
  interface-cell rows of exactly that recorded coupling. It is not a tape
  caveat — the tape did not exist in 2018 — so this stays a bug report, not a
  known-limitation report; but the defect sits in a subsystem whose
  verification the papers explicitly scoped out, in a region their own earlier
  work flagged as accuracy-critical.
- **Tape-tool lineage:** even the one serial accuracy measurement of the
  operator family is of a different AD tool than what ships — PAS 2019
  benchmarked an operator-overloading implementation built on dco/c++, while
  the shipped v5 records its global tape with CoDiPack
  (`initializeGlobalADTape4dRdWT`). No published measurement of the shipped
  tape, serial or parallel, exists (`DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`,
  commit bf6ac53b: the v4/v5 rewrite has no archival method paper at all).

**Community record, added 2026-08-05** (novelty sweep
`LIAISON_NOVELTY_SWEEP_decomposition_defect.md`, commit 3c74dc03 — 63 recorded
searches across 10 venues, no prior report of a converged-wrong
decomposition-dependent gradient anywhere):

- The strongest near-miss is discussion mdolab/dafoam#946 (2026-02, with its
  2022 antecedent #379): a maintainer states, of the periodic-hill case, *"The
  PH case' derivatives are not accurate when running in parallel. You have to
  run it in serial."* — the only place in the community record where a DAFoam
  parallel derivative is said to be *wrong* rather than *slow*. It is scoped
  to periodic/coupled patches, names no mechanism, and #379 explicitly exempts
  ordinary cases ("other cases can run in parallel without an issue"). The
  case measured here has **no coupled patches**: plain processor boundaries —
  the configuration upstream lore says is safe.
- Where upstream does acknowledge decomposition affecting the adjoint
  (#885, #952; kahip support added 2025-12), it is strictly the *convergence
  rate* of the linear solve. Nobody reports, or checks, the converged gradient
  value against decomposition — while this report's KSP converges (reason 2,
  true-residual 1.7e-07) to a wrong solution, which is what the
  cross-residual measurement discriminates.
- The one time serial-vs-parallel gradient equality was checked upstream
  (#101/#102, 2021, v1-era), it passed; the reported discrepancy was an
  output-ordering artifact.
- Exposure: the defect's triggering configuration is the shipped default —
  `pyDAFoam.py` lines 590–591 (main @ `e77f0c0c`, fetched 2026-08-04):
  `self.decomposeParDict = {"method": "scotch", ...}` — and the docs give no
  decomposition guidance and make no parallel-consistency claim.

## The papers' own acceptance check, run on this case per decomposition (added 2026-08-05)

C&F 2018's historical acceptance check for this very geometry family is Table 4:
dCD/du0, the far-field velocity derivative, adjoint vs central FD with step-size
studies (READ IN FULL; `DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md`, commit
bf6ac53b). That check was run here, unmodified in substance, per decomposition,
via the lab's established `check_totals` protocol (central, abs steps) on the
same 2,777-cell A4 case. Staging required two disclosed edits, identical in both
arms: the runScript gains a v5 `patchVelocity` input on the farfield patch
([UMag, aoa], index 0 = u0 as the DV), and the farfield U BC is swapped
`freestreamVelocity` → `inletOutlet` (equivalent switching BC) because
`DAInputPatchVelocity::run` FatalErrors on any other patch type (read
in-container 2026-08-05). Prediction pre-registered before any run
(`/home/ubuntu/certonomous-runs/W4-a4-du0check/PREDICTION.md`): scotch dCD/du0
was predicted to FAIL its own FD at order 1–10%. Runs, logs and ledger:
`/home/ubuntu/certonomous-runs/W4-a4-du0check/` (12.20 core-min, --cpus=2).
Every row below is the adjoint total beside the same run's own central FD:

| run | decomposition | row | FD step (abs) | analytic | FD (same run) | rel. error |
|---|---|---|---|---|---|---|
| du0_np1 | np=1 | dCD/du0 | 1e-3 | 7.8376e-03 | 7.0414e-03 | 11.3% (step-study row: signal ΔCD ≈ 7.8e-6 sits at the primal's CD-repeatability floor at `primalMinResTol` 1e-4) |
| du0_np1 | np=1 | dCD/dshape | 1e-3 | 2.4033e-01 | 2.4055e-01 | 0.090% |
| du0_np1b | np=1 | dCD/du0 | 0.4 (1% of U0) | 7.8376e-03 | 7.5690e-03 | 3.55% |
| du0_np4scotch | np=4 `scotch` | dCD/du0 | 0.4 (1% of U0) | 7.8496e-03 | 7.5711e-03 | 3.68% |
| du0_np4scotch | np=4 `scotch` | dCD/dshape | 1e-3 | 2.4062e-01 | 2.4066e-01 | **0.019%** |

Baseline CD is decomposition-invariant here too (0.15228805 np=1 vs 0.15228863
scotch, 4e-6 relative). Two findings:

1. **dCD/du0 is decomposition-invariant on this case.** The analytic value moves
   0.15% between np=1 and np=4-scotch, the FD column 0.03%, and both
   decompositions sit at the same distance from their own FD (3.55% vs 3.68% —
   a decomposition-independent protocol floor of this loose-tolerance case, per
   the step-study row, not a partition effect; the paper's own <0.1% was
   obtained with tighter convergence and partials-step studies to 1e-8). The
   pre-registered prediction is **REFUTED**, and the pre-named alternative
   obtained: **the papers' Table-4-class check measures a derivative class the
   defect spares** — a maintainer re-running the historical acceptance check on
   the defect's own geometry and decomposition sees nothing.
2. **Unpredicted, and larger than the arm's question: in this staged
   configuration the shape-row defect does not fire under scotch.** Same mesh,
   same default scotch [4] partition, same step, same patched toolchain as the
   verified table above — and dCD/dshape reads 0.019% against its own FD where
   the established configuration reads **8.95%**. The scotch *analytic* moved
   2.2086e-01 → 2.4062e-01 (the FD barely moved, 2.4258e-01 → 2.4066e-01):
   under one of the two staging edits, the scotch adjoint became consistent.
   The two edits are confounded in this arm (farfield BC type; presence of a
   `patchVelocity` input in the recorded tape) and separating them is one
   ~3–5 core-min control (np=4-scotch, `inletOutlet` farfield, **no** patchV
   input) that this item's hard budget did not cover — named for the docket,
   not run. Either way the defect is now measured to be
   **configuration-sensitive at fixed mesh and partition**, and both candidate
   levers alter exactly what the global tape records at a boundary-condition
   update — consistent with the interface-coupling localization above and with
   §2.9's named-delicate region. For "why unnoticed" this is the strongest form
   yet: **on the defect's own case, at the defect's own decomposition, the
   papers' protocol configuration — far-field-velocity DV present,
   inletOutlet-family far field, exactly the C&F 2018 setup class — measures
   nothing worse than a benign FD floor.** The historical check misses the
   defect twice over: it never varies the decomposition, and the configuration
   it instantiates is one the defect spares.

Nothing here re-grades the established 8.95% scotch failure, which stands
supervisor-verified on its own configuration
(`VERIFICATION_A4_mechanism_supervisor_sweep.md`, commit 8e0a08bc); this section
adds the papers'-protocol row beside it and bounds where the defect shows.

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
`DISCRIMINATORS_A4_decomposition_mechanism.md`,
`PROOF.md` §25.5, `VERIFICATION_A4_decomposition_supervisor_sweep.md`,
`VERIFICATION_A4_mechanism_supervisor_sweep.md`,
`DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` (commit bf6ac53b),
`LIAISON_NOVELTY_SWEEP_decomposition_defect.md` (commit 3c74dc03), and the
papers'-protocol arm `/home/ubuntu/certonomous-runs/W4-a4-du0check/`
(`PREDICTION.md`, `ledger.txt`, logs; 2026-08-05).

## Addendum 2026-08-05: the defect reproduces on a second case — a deliberately controlled sibling of the first (breadth campaign, docket `w4-does-the-decomposition-defect-reach-other-cases`)

**Status unchanged: NOT FILED ANYWHERE.** Evidence:
`DEFECT_REACH_decomposition_cases.md`, run artifacts
`/home/ubuntu/certonomous-runs/W4-defect-reach/`.

**Corrected 2026-08-05** (per the reach-matrix supervisor sweep,
`demo-output/website/dafoam/VERIFICATION_reach_matrix_supervisor_sweep.md`,
commit 192c970c — the trigger claim CONFIRMED on all six audit axes, with one
evidential caveat this correction carries into the record). An earlier revision
of this addendum titled Ahmed-35 a "second, independently meshed case" and
called the 7-case BC survey a "perfect correlate" without stating its
confounds. Three amendments:

1. **Sibling, not stranger.** Ahmed-35 is A4's own recipe with only the STL
   swapped, and the kinship at the operator level is closer than "independently
   meshed" suggested: same 2,777-cell background mesh family, same 25,821-state
   serial system, and — measured by the sweep from the addressing files — the
   **same 328-face scotch cut hitting the same dominant serial cells**
   (338/407/275). That control is exactly what makes the "defect follows the
   cut" fingerprint meaningful, but as cross-case breadth the defect side of
   the 7-case survey is **one case family (n=1), not two independent
   geometries**. The reproduction evidence is real; the breadth evidence is
   narrower than the earlier wording implied.
2. **The second confound, stated plainly.** Across the survey's external-flow
   cases, `freestreamVelocity` is **perfectly anti-correlated with
   `patchVelocity` registration**: all three clean external-flow cases (A1, A2,
   sail) register a `patchVelocity` input, and neither defect case does — the
   pairing DAFoam's `DAInputPatchVelocity` FatalError branch forces. On the
   survey alone, "patchV registration suppresses the defect" fits the seven
   cases exactly as well as "the BC gates it." **Arm N9 breaks both
   confounds**: the within-case swap (inletOutlet farfield + no patchVelocity
   input, analytic print-identical to the patchV-registered arm on the same
   mesh and the same scotch partition) separates the BC from the registration
   with every other property held fixed. The causal weight of the trigger
   claim sits there; the cross-case survey is corroboration, not proof.
3. **"82% of the norm" misstated its own evidence.** The top cross-residual
   entry alone is 82% of ||r||; the top three together are 99.9%. Fixed in the
   bullet below.

- **Second reproducer** (a controlled sibling — see the 2026-08-05 correction
  above). An Ahmed 35-degree-slant body meshed by the same
  blockMesh+snappyHexMesh recipe (2,777 cells — the same background mesh family
  as the first case; refinement interfaces present, mesh points distinct): the
  converged np=4 `scotch` adjoint
  psi, mapped to serial ordering by the same integer-addressing protocol
  (duplicated-phi map validation 2.7e-15), leaves a true residual of **5.45x
  ||b|| under the np=1 operator** (np=1 control floor 3.98e-04), unchanged to six
  digits with the serial operator linearized at the scotch arm's own mapped
  state. Same localization signature: 13 of the top 15 entries on partition-
  interface cells, all `cellLevel` 0, the dominant entry alone carrying 82% of
  the norm (the three dominant entries together: 99.9%; phrasing corrected
  2026-08-05 per the reach-matrix sweep, commit 192c970c), each of the three
  touching exactly one foreign rank through exactly one processor
  face. One structural observation across the two cases (n=2, offered as a hint,
  not a claim): the large rows are a momentum component **tangential** to the
  offending processor face — x-momentum on y-normal faces (case 1), z-momentum
  on x-normal faces (case 2).
- **Severity at gradient level is case-dependent, which is why the defect
  hides.** On case 2 the same wrong-operator defect moves the analytic gradient
  only 1.4% (scotch) / 3.1% (simple 4x1x1) — the operator-residual magnitude
  (5.45 vs 0.33 of ||b||) does not even rank-order the gradient damage, because
  the damage is the contraction of the operator error with the objective's
  adjoint direction. A gradient that passes `check_totals` under one
  decomposition therefore certifies nothing about the parallel operator; on the
  first case that same contraction costs 8.95%.
- **Breadth of the clean side.** A conformal-blockMesh case (CBFS, 21,000 cells)
  with a 21,000-component volume-field DV is decomposition-invariant: gradient
  norms agree to 1.1e-04 across `scotch` vs `simple` at np=4, per-component
  1.5e-05-1.6e-04 at FD-verified cells, with the FD column measured under BOTH
  decompositions (0.085% / 0.055%). A 63,920-cell snappyHexMesh case
  (NACA0015 sail, np=3) was also checked under a second decomposition; see
  `DEFECT_REACH_decomposition_cases.md` for its row. On the first case, planar
  slabs of all three orientations at np=4 stay at 0.00054-0.52% and a 2x2x1
  corner decomposition reads 1.40%, against `scotch`'s 8.95% — and refinement-
  interface cut counts anticorrelate with the error (the 68-cut planar arm is
  the cleanest; the 4-cut scotch arms are the worst), on measurement at every
  new arm.

### Added 2026-08-05, N9 separating control (still NOT FILED): the gating ingredient is the `freestreamVelocity` farfield BC

The papers-protocol session found the defect ABSENT (shape row 0.019%) in a
configuration carrying two confounded edits (farfield U `freestreamVelocity` ->
`inletOutlet`, plus a registered `patchVelocity` input). The separating control
(`W4-defect-reach/a4_inletOutlet_scotch.log`, pre-registered prediction in
`DEFECT_REACH_decomposition_cases.md` N9, commit aa51ca08): same mesh, same
np=4 scotch partition, `inletOutlet` farfield, **no patchVelocity input
anywhere** — analytic dCD/dshape **2.4062e-01**, the no-defect class, identical
at printed precision to the patchV-registered arm's 2.4062e-01. So:

- the `patchVelocity` input registration is **inert** for the `dRdW^T` operator;
- the **`freestreamVelocity` BC in the recorded `updateStateBoundaryConditions`
  is necessary for the defect**: swap it for `inletOutlet` and the same scotch
  cut produces a clean gradient;
- across all seven cases measured in this lab, the correlate is factually
  perfect — the two cases with the operator defect (both Ahmed variants) carry
  `freestreamVelocity`; the five decomposition-clean cases (A1, A2, A5, CBFS,
  sail) carry `inletOutlet`/`fixedValue` U BCs, verified from each case's
  0.orig/U. **Qualified 2026-08-05** (reach-matrix supervisor sweep,
  `demo-output/website/dafoam/VERIFICATION_reach_matrix_supervisor_sweep.md`,
  commit 192c970c): the survey is confounded twice — the defect side is one
  case family, and the BC is perfectly anti-correlated with patchVelocity
  registration across the external-flow cases — so it corroborates but cannot
  alone carry the causal claim; the within-case N9 swap in this section is
  what carries it;
- the deposit site is unchanged (interior partition-interface momentum rows —
  on the 35-degree case the three dominant cross-residual cells are NOT
  farfield-adjacent), so the BC is an ingredient of the recorded computation
  whose reverse goes wrong at processor cuts, not the location of the error.

For the instrumented-rebuild proposal this narrows the first place to look to
the reverse-mode treatment of the freestream-family (flux-switching mixed) BC
update inside the global tape, in combination with processor-patch updates.
