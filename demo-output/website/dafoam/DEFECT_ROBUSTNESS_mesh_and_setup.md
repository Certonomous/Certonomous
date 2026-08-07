# Robustness of the decomposition-adjoint defect: a second mesh family, mesh convergence, and setup invariance

**2026-08-05, well W4. Follow-up to the reach matrix
(`DEFECT_REACH_decomposition_cases.md`) directed by the reach-matrix supervisor
sweep (`VERIFICATION_reach_matrix_supervisor_sweep.md`, commit 192c970c), which
confirmed the trigger claim on all six audit axes and named the remaining
weakness: the defect side of the seven-case survey is one case family (n=1) —
both defective cases are the same 2,777-cell Ahmed background mesh with the
same 328-face scotch cut. Katie's questions this session answers: how many
cases support the claims; did we run mesh convergence on them; did we run the
checks that prove we are not just recording numerical defects of our own
setup?** Run artifacts: `/home/ubuntu/certonomous-runs/W4-defect-robustness/`
(per-arm dirs, logs, `ledger.txt`, drivers). Budget: 150 core-min, `--cpus=2`
(the box is shared with the S1 inversion), ledger charged wall x 2.

**Status at first commit: predictions pre-registered BEFORE any arm ran; the
commit timestamp is the witness. Results are appended below the marked line
and nothing above it is edited after registration.**

## What is on record (not rerun)

- Established defect (A4 coarse, 2,777-cell snappy Ahmed, `freestreamVelocity`
  farfield, patched IDWarp, `check_totals` step 1e-3 central abs): np=1 0.34%,
  np=2 scotch 0.26%, np=3 scotch 6.05%, np=4 scotch **8.95%** (analytic
  2.2086e-01 vs own-run FD 2.4258e-01), np=4 simple 4x1x1 0.00054%,
  `gmresRelTol` 1e-10 unchanged at 8.95% (811 iters, reason 2).
- N9 separating control: swap A4's farfield U BC `freestreamVelocity` ->
  `inletOutlet`, same mesh, same scotch [4] cut — analytic lands in the clean
  class (2.4062e-01); patchVelocity input registration measured inert.
- Trigger claim as it stands: freestream-family U BC in the recorded tape
  (necessary) x cut geometry (scotch np>=3 the catastrophic excitation on
  these meshes), damage on interior partition-interface momentum rows, priced
  by the objective contraction.
- The confound this session attacks: every defective measurement lives on ONE
  mesh family; no clean case even hosts the necessary BC, so BC-necessity has
  no second independent case and cut-geometry sufficiency is bracketed only
  within the Ahmed family. Mesh-convergence behavior of the defect: never
  measured. Setup-invariance (schemes, primal depth, Krylov restart) of the
  8.95%: only the `gmresRelTol` axis is on record.
- A1 NACA0012 record (the clean case borrowed for R1): 4,032-cell structured
  conformal airfoil mesh (no `cellLevel`), `inletOutlet` farfield, patchV
  registered, tight primal (`primalMinResTol` 1e-8); CD/shape vs own FD
  3.80e-04 (np=1) and 3.81e-04 (np=4 scotch), analytic magnitude 6.490496e-02
  vs 6.490495e-02 — decomposition-invariant on record
  (`W4-a1-rank/a1_np{1,4}.log`).

## Protocol constants (all arms)

`dafoam/opt-packages:latest`, patched IDWarp via
`-v W5-patch:/patch` + `PYTHONPATH` (provenance stamped in-log), `--cpus=2`,
`--memory=8g`, `check_totals` = step 1e-3, central, `step_calc="abs"` (the
verified-table protocol), scotch decompositions via the `decomposeParDict`
daOption or the shipped default. Error convention: OpenMDAO vector relative
error ||Jan - Jfd|| / ||Jfd|| as printed by `check_totals` (one convention
throughout, per the sweep's N8 note). Each arm scored HELD / NOT HELD exactly
as registered; no post-hoc bands.

## PRE-REGISTERED arms and predictions

### R1 — the mirror of N9: freestreamVelocity transplanted ONTO a clean case from a different mesh family

A1 NACA0012, structured conformal 4,032-cell mesh — a different mesh family
from the Ahmed background in every respect (structured extruded airfoil mesh,
no snappy castellation, no refinement interfaces). Where N9 removed the BC
from the defective case, R1 installs it on a clean one. Edits (mirroring the
papers-protocol arm in reverse, byte-minimal):

- `0.orig/U` (and `0/U`) `inout` patch: `inletOutlet` -> `freestreamVelocity`,
  `freestreamValue uniform (9.959800351 0.895754972 0)` — U0=10 at the case's
  own aoa0=5.13918623195176 deg, so the flow is unchanged from the record
  configuration.
- runScript: `patchV` removed everywhere (inputInfo, dvs output, connect,
  design var, feasible-design call) — the defect configuration registers no
  patchVelocity input, and N9 measured the registration inert anyway;
  `primalBC` loses its `U0` entry (the BC lives in `0.orig/U` alone, exactly
  as on A4); CD/CL `directionMode` `parallelToFlow` -> `fixedDirection` with
  direction [0.995980035095, 0.089575497163, 0] for CD and
  [-0.089575497163, 0.995980035095, 0] for CL (the same physical directions
  the record's parallelToFlow/normalToFlow evaluated at aoa0).

Arms: `a1fs_np1` (np=1) and `a1fs_np4scotch` (np=4, shipped-default scotch —
the same partitioner that is invariant on this mesh under `inletOutlet` in the
record), both `check_totals`.

**Registered prediction R1:** (i) np=1 control clean: CD/shape rel. err vs own
FD <= 0.5% (the case's own floor is 0.038% and the primal is tight at 1e-8);
(ii) **the defect FIRES on the second mesh family: np=4-scotch CD/shape rel.
err vs its own FD >= 2%, with the analytic shifted >= 2% from the np=1
analytic while the two FD columns agree to <= 0.5%.** Reasoning: BC-necessity
is measured (N9) and the reverse tape of the freestream-family BC update plus
a scotch cut is the named mechanism; scotch's cut on this anisotropic
structured graph is not an axis-planar slab, and planar-vs-jagged is the
modulation axis on record. Named alternative, registered as decisive either
way: if np=4-scotch instead reads <= 0.5% (the record floor), the trigger
needs a third ingredient beyond BC x scotch-cut (mesh family / cut topology),
the n=1-family confound SURVIVES on the defect side, and the upstream report
must say so. Gray zone 0.5-2%: scored NOT HELD, reported as an intermediate
excitation with the numbers. If the defect fires, contingent arm R1x
(cross-residual instrument on A1, budget permitting) is authorized; the
gradient-level result stands on its own either way.

### R2 — mesh convergence of the defect (A4 family, one uniform refinement level up)

New mesh `a4_medium`: A4 coarse recipe with the background `blockMeshDict`
block count doubled per axis, (26 6 15) -> (52 12 30), every other dict
byte-identical (same snappy refinement levels, same eMesh level, same STL) —
one uniform refinement level of the background the defect's mesh is built on;
expected ~8x cells (~15-25k), `cellLevel` interfaces present (gate: checkMesh
completes AND `cellLevel` in polyMesh). `controlDict` endTime 500 -> 1000
(disclosed: the finer mesh may need more SIMPLE iterations to reach
`primalMinResTol` 1e-4; identical in every arm of this mesh).

Arms: `a4med_np4scotch` (np=4 scotch, `check_totals` — analytic and own-run FD
in one log). np=1 control `a4med_np1` runs ONLY if the running budget total
projects under 110 core-min at that point (registered decision rule, budget
honesty; the scotch arm's own FD column is the primary reference either way).
FD-resolvability guard, registered: if the scotch arm's verdict lands in the
gray band (1-3%) OR the FD magnitude differs from the analytic np=1-class
value by > 20% (an a35-style unresolved-FD symptom), one FD step-check rerun
at h=3e-3 is authorized before scoring; otherwise no extra FD legs are bought.

**Registered prediction R2: the defect PERSISTS under refinement — np=4-scotch
CD/shape rel. err vs its own FD >= 3%.** Reasoning: the mechanism is a
property of the recorded reverse tape's processor-boundary treatment, not a
truncation-error artifact; refining the mesh changes the discrete operator but
not the tape's parallel structure, and the cut only gets longer (more
interface faces for the reverse halo accumulation to corrupt). Named
alternative: if the error instead reads <= 1%, the defect VANISHES under
refinement and the upstream report's claim must be re-scoped to
coarse/under-resolved meshes (a materially weaker claim — reported loudly).
Middle band 1-3%: persists-but-shrinks, reported as measured with the
step-check guard above. Secondary registered expectation: baseline CD0 stays
decomposition-invariant to <= 0.1% (it always has), and if np=1 runs, its rel.
err <= 1%.

### R3 — setup robustness: is the 8.95% a property of the operator or of our numerics?

A4 coarse, np=4 scotch, established configuration, ONE knob turned per arm;
everything else byte-identical to the verified-table arms (including step 1e-3
central FD in-run). The established result's reading is "converged wrong
answer" — the error should be invariant to every knob below.

- **R3a schemes** (`a4knob_schemes`): `div(phi,U)` `bounded Gauss linearUpwind
  limited` -> `bounded Gauss upwind`; `gradSchemes default Gauss linear` ->
  `cellLimited Gauss linear 1`. The discrete operator (and hence the true
  gradient, the analytic, and the FD) all legitimately move together; the
  invariant is the analytic-vs-own-FD error. **Prediction: the error stays in
  the large class, >= 4%** (the defect lives in the reverse tape of the
  parallel coupling, which every convection/gradient scheme feeds through the
  same processor-patch machinery). Named alternative: error <= 1% means the
  defect is scheme-specific — REOPENS the mechanism question, reported loudly.
- **R3b primal depth** (`a4knob_primal10`): `primalMinResTol` 1e-4 -> 1e-10
  with endTime 500 -> 2000 (the tolerance is not reachable on this
  wall-function case; the primal will run its full 2000 steps — deliberately
  4x the established primal length, i.e. the "converged wrong answer" is
  tested against a much deeper primal). **Prediction: rel. err in [7%, 11%]
  and analytic within 1% of 2.2086e-01.** Named alternative: a material move
  (error leaving the band) says the 8.95% carries a primal-convergence
  component — REOPENS the converged-wrong-answer reading, reported loudly.
- **R3c Krylov restart** (`a4knob_restart60`): `adjEqnOption` gains
  `"gmresRestart": 60` (shipped default 1000; the record solve took 590
  iterations, so restart-60 forces ~10 restart cycles where the record ran
  restart-free). **Prediction: analytic within 0.1% of 2.2086e-01 and rel.
  err within [8.6%, 9.3%]** (the record's gmresRelTol-1e-10 precedent:
  converged-wrong is tolerance- and restart-independent). Named alternative:
  any material move REOPENS the linear-algebra explanation, reported loudly.

### R4 (contingent, runs only if the running total projects <= 130 core-min after R1-R3) — the same-geometry hanging-node pair the reach record listed as untested in pair form

`a4_conformal`: A4 geometry, snappy recipe with surface/eMesh refinement
levels set to 0 so the castellation introduces NO `cellLevel` > 0 anywhere
(gate: max `cellLevel` = 0, i.e. no hanging-node interfaces on the mesh),
`freestreamVelocity` farfield unchanged, np=4 scotch `check_totals`.
**Prediction: the defect STILL FIRES — rel. err >= 2%** (the record's
localization already puts the residual on `cellLevel` 0 cells and
anticorrelates error with refinement-interface cut counts; hanging nodes are
context, not ingredient). Named alternative: clean (<= 0.5%) reinstates
refinement as a necessary ingredient — the trigger claim gains an axis.

## Budget plan

R1: ~3 + ~5 = 8. R2: mesh ~1, np4 ~35-60, np1 (conditional) ~25-45.
R3: ~5 + ~13 + ~5 = 23. R4 (contingent): ~12. R1x (contingent): ~12.
Planned spine ~70-95; hard cap 150; every run ledgered wall x cpus-cap in
`W4-defect-robustness/ledger.txt`; overruns stated, not hidden.

*(Results and verdicts follow after the runs; nothing below this line existed
at pre-registration commit time.)*

## AMENDMENT — R3a1 / R3a2, registered 2026-08-05 BEFORE their arms ran (commit history is the witness)

R3a came back **NOT HELD in the loud direction**: with `div(phi,U)` `bounded
Gauss upwind` and `gradSchemes default cellLimited Gauss linear 1`, on the same
A4 mesh and the same np=4 scotch partition where the established configuration
reads 8.95%, the analytic reads 3.0977e-01 against its own FD 3.0906e-01 —
**0.228%, the clean class** (and the adjoint KSP converges in 68 iterations
against the record's 590). The registered decision rule ("error <= 1% means the
defect is scheme-specific — REOPENS the mechanism question, reported loudly")
has fired. R3a turned TWO knobs in one arm, so it cannot say which; these two
arms separate them, exactly as N9 separated the BC from the patchV
registration.

- **R3a1** (`a4knob_divupwind`): `div(phi,U)` `bounded Gauss linearUpwind
  limited` -> `bounded Gauss upwind`, **gradSchemes untouched**. Everything
  else byte-identical to the established arm.
- **R3a2** (`a4knob_gradlim`): `gradSchemes default Gauss linear` ->
  `cellLimited Gauss linear 1`, **divSchemes untouched**.

**Registered prediction: R3a1 is CLEAN (rel. err <= 1%) and R3a2 is DIRTY
(rel. err >= 4%) — i.e. the convection scheme is the carrier, not the default
gradient scheme.** Reasoning: `linearUpwind limited` evaluates a limited cell
gradient of U and applies it as a face correction, so the residual's recorded
tape contains a gradient whose forward evaluation needs a halo exchange of
neighbour values AND whose reverse needs the transpose of that exchange —
precisely the inter-processor coupling the cross-residual localizes on. Plain
`upwind` needs no gradient in the convection term at all, so that coupling
leaves the tape. The `default` gradScheme, by contrast, feeds grad(p) and the
viscous/turbulence terms, which are present in both configurations either way.
Named alternatives, both decisive: if R3a2 is ALSO clean, the trigger is the
gradient-limiter family generally (any limited gradient in the tape), not the
convection scheme; if R3a1 is DIRTY, the convection scheme is innocent and
R3a2's gradient default carries it. Either way the trigger condition acquires a
third named ingredient and the upstream report must be rewritten around it.

Cost: ~6 core-min each; both inside the 150 cap with the R2/R3b/R4 spine
planned above.

## AMENDMENT 2 — R5, the operator-vs-contraction test, registered 2026-08-05 BEFORE its arms ran (supervisor-directed after the R3a result; commit history is the witness)

Both levers that clean this defect — the `freestreamVelocity` -> `inletOutlet`
BC swap (N9) and the `linearUpwind` -> `upwind` convection swap (R3a1) — have
so far been measured **only at gradient level**. L-36 is the standing warning
that a clean `check_totals` certifies a contraction, not an operator. The
decisive question is therefore: under each lever, does the **operator** error
collapse, or does the operator stay wrong while the objective's adjoint
direction stops seeing it?

Instrument: the discriminators session's own scripts, unmodified
(`W4-a4-discriminators/runScript_w4.py` tasks `w4_dump` / `w4_crossres`;
`build_maps.py` re-pathed only). Sign convention as amended there: the
instrument computes `Atpsi - b` for the system `A^T psi = -b`, so own-operator
lines print the degenerate `ratio=2.000000e+00` and the reported cross ratios
are the offline correction `res + 2b` from the dumped vectors. Map validated
before use by the script's own checks (duplicated processor-face phi copies at
machine zero; mapped primal states at reconvergence noise).

- **R5a (scheme lever)**: `upw_d_np1`, `upw_d_np4scotch` (`w4_dump`), then
  `upw_d_crossres` (`w4_crossres`, np=1) — A4 coarse with **only**
  `div(phi,U)` `bounded Gauss upwind` (the R3a1 edit), established
  `freestreamVelocity` BC, patched IDWarp.
- **R5b (BC lever)**: `io_d_np1`, `io_d_np4scotch`, `io_d_crossres` — A4 coarse
  with **only** the N9 `inletOutlet` farfield block (copied byte-wise from the
  N9 arm's `0.orig`), established `linearUpwind` schemes.

Reference values on record for the established configuration (same instrument,
same case, same np=4 scotch cut): cross-residual **329x ||b||**, np=1 control
floor **1.1e-04**.

**Registered prediction R5: BOTH levers collapse the operator error, not just
the contraction — R5a and R5b each read a cross-residual ratio <= 5x ||b||
(against the established 329x), with their np=1 controls at the ~1e-03-or-below
floor.** Reasoning: for the scheme lever, `linearUpwind limited` is the only
term in this residual that evaluates a cell gradient of U and applies it as a
face correction, so its forward evaluation needs a halo exchange of neighbour
values and its reverse needs the transpose of that exchange — remove the term
and the suspect coupling leaves the tape entirely; for the BC lever, N9's
mechanism reasoning put the defect in the recorded
`updateStateBoundaryConditions`, which is likewise removed from the tape by the
swap. **Named alternative, registered as the loud one:** if either lever leaves
the cross-residual >= 50x ||b|| while its gradient is clean, then that lever
does NOT fix the operator — it only rotates the objective's adjoint direction
away from the corrupted subspace, exactly L-36's failure mode, the operator is
still wrong for every other objective and DV on that case, and **the upstream
report's framing must change from "these configurations are safe" to "these
configurations hide it."** Intermediate 5-50x: reported as measured, scored NOT
HELD, with the partial-collapse reading stated.

Cost: ~13 core-min per lever (two dumps + one serial crossres each).

## AMENDMENT 3 — R6, the BRANCH hypothesis, registered 2026-08-05 BEFORE its arms ran (supervisor-directed; commit history is the witness)

Supervisor's cross-finding hypothesis, stated as given: **every defect this lab
has found in this toolchain is one class — a BRANCH recorded in a
differentiated path, whose selection is not correctly captured or not
consistent across processor boundaries.** The three instances: a slope limiter
(min/max selection over a stencil that reaches halo cells); `freestreamVelocity`
(inletOutlet-family logic switching on the sign of the face flux); and L-29's
IDWarp degenerate-rotation GUARD, differentiated to a hard zero.

**What the arms already on record answer, before spending anything** (checked,
per the instruction not to buy what is already bought):

- **Neither branch source alone suffices; each is necessary.** R3a1 keeps the
  `freestreamVelocity` branch and removes the limiter branch -> CLEAN
  (0.041%). N9 keeps the limiter branch (`linearUpwind limited` untouched) and
  removes the freestream branch -> CLEAN (2.4062e-01, the no-defect class).
  Same mesh, same np=4 scotch cut in both. So the defect requires BOTH recorded
  branches present; removing either one is sufficient to clean the gradient.
  That is a conjunction, and it is exactly what the branch hypothesis predicts
  if the damage needs a branch-carrying BC update AND a branch-carrying stencil
  operation to interact across the same processor faces.

**What is NOT yet separated, and what R6 buys.** R3a1 removed the limiter by
dropping to `bounded Gauss upwind` — which removes the limiter branch AND the
second-order gradient-correction term AND drops the scheme to first order.
Three edits in one word. Two arms separate them:

- **R6a** (`a4knob_divlinear`, the supervisor's proposed test):
  `div(phi,U)` -> `bounded Gauss linear` — second order, no gradient
  correction, **no limiter branch**.
- **R6b** (`a4knob_divlinupw_unlim`, the sharper test): `div(phi,U)`
  `bounded Gauss linearUpwind limited` -> `bounded Gauss linearUpwind
  default`. One word. Same scheme family, same order, the same
  gradient-correction term still evaluated and still needing a halo
  exchange — **the ONLY thing removed is the limiter branch**, because
  `default` names A4's unlimited `Gauss linear` gradScheme where `limited`
  names `cellLimited Gauss linear 1`.

**Registered prediction R6: the branch hypothesis holds — R6b is CLEAN (rel.
err vs its own FD <= 1%) and R6a is CLEAN (<= 1%).** R6b is the load-bearing
clause: it keeps the gradient-correction halo exchange and removes only the
min/max selection. **Named alternative, registered as the loud one: if R6b is
DIRTY (>= 4%) while R3a1 was clean, the limiter branch is NOT the carrier — the
second-order gradient-correction TERM is, branch or no branch, and the
supervisor's unifying hypothesis is REFUTED for this defect and must be
reported as refuted.** Intermediate 1-4%: scored NOT HELD, reported as partial.
A DIRTY R6a with a CLEAN R6b would say the scheme's order matters
independently, which would also weaken the hypothesis; that combination is
named here so it cannot be re-read favourably afterwards.

Cost: ~7 core-min each.

**R6b-control, registered 2026-08-05 BEFORE it ran.** R6b measured 0.849% —
inside the registered <= 1% clean band, but ~20x above the clean floor R3a1
(0.041%) and A1 (0.043%) sit at. Two readings are possible and they matter for
the mechanism: either 0.849% is this DISCRETIZATION's own FD floor (in which
case the limiter removal is a complete fix at gradient level), or it is a
surviving decomposition effect (in which case the limiter carries the
catastrophic part and something else carries a small remainder). The control:
`a4knob_divlinupw_unlim_np1` — the identical case at **np=1**, where no
partition exists and any residual error is the protocol floor alone.
**Registered prediction: the np=1 control reads within a factor 2 of 0.849%,
i.e. the 0.849% is the discretization's own floor and no decomposition effect
survives the limiter removal.** Named alternative: if np=1 reads <= 0.2%, a
real decomposition effect survives at ~0.8% (still 10x under the established
8.95%), and the record says the limiter is the catastrophic carrier but not the
whole story. Cost ~3 core-min.

## AMENDMENT 4 — R2b, registered 2026-08-05 BEFORE it ran (commit history is the witness)

R2 as registered could not be scored: on the refined mesh (19,619 cells) in the
established configuration, the np=4-scotch **adjoint does not converge at all**
— GMRES exhausts `gmresMaxIters` 1000 at KSP residual 1.7188e-02 with
`PetscConvergedReason: -3`, `solve_linear` raises, and the arm produces no
analytic to compare against its FD (`a4med_np4scotch.log`, rc=1, 33.60
core-min charged). Buying convergence by raising the iteration cap would cost
more than the remaining budget allows, and the registered FD-resolvability
guard was written for a gray-band error, not for a missing gradient.

R2b substitutes the refinement question the remaining budget CAN answer, and it
is the more informative one given R6: **`a4med_divlinupw_unlim`** — the same
19,619-cell refined mesh, np=4 scotch, with the single R6b edit (`div(phi,U)`
`bounded Gauss linearUpwind default`, limiter branch removed, gradient
correction retained).

**Registered prediction R2b: with the limiter branch removed the refined-mesh
adjoint CONVERGES (`PetscConvergedReason` 2, well inside 1000 iterations) and
its analytic agrees with its own FD to <= 2%.** Reasoning: on the coarse mesh
the same edit took the KSP from 590 iterations to 41 and the error from 8.95%
to 0.849%; if the limiter branch is the carrier of both the operator error and
the conditioning collapse, refinement should not resurrect either. Named
alternative, registered: if the refined arm ALSO fails to converge, the
conditioning collapse is a property of the refined mesh rather than of the
limiter, and the refinement axis stays unmeasured — reported as such, not
papered over. If it converges but reads >= 2%, the defect grows under
refinement even without the limiter, which would say the limiter is not the
whole carrier at finer resolution.

Cost ~20 core-min; with R4 this closes the session inside the 150 cap.

## AMENDMENT 5 — R7, the acquisition arm, registered 2026-08-07 BEFORE its arms ran (docket `w4-defect-acquisition-on-a-second-mesh-family`; commit history is the witness)

The scheme survey's named next experiment (item 3 of the survey section below),
now approved and claimed: install BOTH measured ingredients of the conjunction
on the clean structured NACA0012 and measure whether the case ACQUIRES the
defect. Staging (`run_a1lim_arm.sh`, extending `run_a1fs_arm.sh` — the R1 edit
set is inherited byte-identically and re-asserted in-driver):

- R1's edits verbatim: `0.orig/U`/`0/U` `inout` `inletOutlet` ->
  `freestreamVelocity` at the case's own aoa0; `patchV` stripped everywhere;
  `primalBC` loses `U0`; CD/CL forces to `fixedDirection` at the record's
  physical directions.
- THE new edit, A4's limited convection installed on A1's `fvSchemes`:
  `div(phi,U)` `bounded Gauss linearUpwindV grad(U)` -> `bounded Gauss
  linearUpwind limited`, and `gradSchemes` gains the entry `limited
  cellLimited Gauss linear 1` (the same token pair A4's defective
  configuration resolves). **Disclosed:** this edit swaps the V-form of the
  scheme as well as installing the limiter branch; the contingent control R7c
  below isolates the one word within the same family, exactly as R6b did on
  A4.
- A1's own `primalMinResTol` 1e-8 is left untouched — so a fired defect here
  simultaneously kills the loose-primal co-ingredient hypothesis (R3b's open
  confound), because this case has no loose primal.
- Arms: `a1lim_np1` (np=1) and `a1lim_np4scotch` (np=4, shipped-default
  scotch, verified in-log), both `check_totals` step 1e-3 central abs, patched
  IDWarp stamped in-log, `--cpus=2`.

**Registered prediction R7 (the conjunction hypothesis, limiter x
freestreamVelocity x cut): (i) np=1 control clean — CD/shape rel. err vs own
FD <= 0.5%; (ii) the defect ACQUIRES on the second mesh family — np=4-scotch
CD/shape rel. err vs its own FD >= 2%, with the analytic shifted >= 2% from
the np=1 analytic while the two FD columns agree to <= 0.5%.** Named
alternative, decisive per the docket gate: both arms <= 0.5% means the
conjunction is INSUFFICIENT off the Ahmed family — the trigger needs a
mesh-family/cut-topology axis after all, the n=1-family confound STANDS on the
defect side, and the upstream report must scope its reproducer to the Ahmed
family or a co-ingredient it carries. Gray zone 0.5–2%: scored NOT HELD,
reported as an intermediate excitation with the numbers. If the np=1 control
itself is dirty or the primal fails under the new scheme, the arm is reported
unmeasurable, not scored.

Contingent arms, authorized ONLY if clause (ii) fires:

- **R7c** (`a1limdef_np4scotch`): same case, `div(phi,U)` `bounded Gauss
  linearUpwind default` — the R6b one-word lever, np=4 scotch. Prediction:
  <= 0.5% (the limiter branch, not the `linearUpwindV` -> `linearUpwind`
  family change, carries the acquisition).
- **R7x** (`a1lim_d_np1`, `a1lim_d_np4scotch`, `a1lim_crossres`): the
  discriminators' dump/crossres instrument grafted into the staged A1
  runScript, method unmodified (`writeJacobians: ["adjointIndexing"]`; offline
  np4->np1 map by `build_maps_a1lim.py`, a re-pathed copy of
  `build_maps_upw.py` with its validation gates intact; sign convention as
  amended — own-operator lines print the degenerate `ratio=2.000000e+00`, the
  reported cross ratio is the offline correction `r = res + 2b`). Prediction:
  the mapped scotch psi leaves a cross-residual **>= 50x ||b||** under the
  serial operator (the wrong-operator class), with the np=1 control at
  <= 1e-3 x ||b||.

Cost basis: 2.6–3.1 core-min per A1 check arm (measured, R1); contingents ~9
more. Session hard cap 30 core-min against the docket estimate of 25.

## AMENDMENT 6 — R7f, registered 2026-08-07 AFTER the two R7 arms ran and BEFORE any further arm (commit history is the witness)

What triggered this: R7's registered escape clause fired in a direction no
registered band anticipated. Measured before this amendment was written (both
arms rc=0, full numbers in the results section below): the np=1 control reads
CD/shape **92.8%** against its own FD — dirty, so R7 cannot be scored against
its FD-relative bands — while the np=4-scotch arm reads the SAME analytic to
0.039% (vector), the SAME FD to 1e-6, the SAME 92.8% error, and the same
Krylov count (95/96 vs 96/97). Whatever broke agreement broke it identically
at both decompositions. Two separating arms, predictions registered before
either runs:

- **R7f1** (`a1lim_np1_h3e3`): byte-identical restage of `a1lim_np1` with the
  ONE edit `check_totals` step 1e-3 -> 3e-3 (the step-check magnitude the R2
  guard registered for exactly this symptom class — FD magnitude differing
  from the analytic by > 20%). **Prediction: the FD is NOT step-stable — the
  CD/shape FD vector at 3e-3 differs from the 1e-3 FD vector by >= 20%
  (vector-relative), i.e. the limiter has made this case's shape response
  kinked at the FD scale and the 93% is an unresolved-FD artifact, not a
  serial AD conviction.** Named alternative, the loud one: FD stable to
  <= 2% with the analytic unchanged means the limiter's SERIAL reverse tape
  is genuinely wrong at ~93% on this case — a decomposition-INDEPENDENT
  defect class this lab has not previously seen (every prior defect here
  vanished at np=1) — reported loudly and separately from the decomposition
  claim. Middle band 2–20%: partial step-dependence, scored NOT HELD,
  reported as measured.
- **R7f2** (`a1limdef_np1`): the R6b one-word lever at np=1 — `div(phi,U)`
  `bounded Gauss linearUpwind default` (unlimited; the V-form/family change
  of the R7 staging retained), step 1e-3. **Prediction: clean, CD/shape rel.
  err vs own FD <= 0.5% — the limiter word, not the `linearUpwindV` ->
  `linearUpwind` family change, carries the serial gap.** Named alternative:
  dirty means the family change itself broke serial agreement, the R7 staging
  does not isolate the limiter, and the acquisition verdict must be re-scoped
  to "A4's scheme pair transplanted", reported as such.

What needs NO new arm and is scored now, exactly once, on the
decomposition-invariance instrument (the instrument R1's clause (ii) already
used as a subclause): **the acquisition question itself.** Analytic
np=1-vs-np=4-scotch 3.9e-04 vector-relative (max component 0.20%, median
0.04%), FD columns 1e-6 apart, equal Krylov counts, `Decomposition method
scotch [4]` verified in-log. Whatever the 93% is, it is not
decomposition-borne: **the defect did NOT acquire on the second mesh family**,
and the docket gate's second branch (conjunction insufficient off the Ahmed
family; the n=1-family confound stands) obtains on this instrument, with the
FD-band caveat disclosed.

Cost: R7f1 ~6.5 core-min (measured, the limited np=1 arm), R7f2 ~3.5.
Running total 8.80 of the 30 cap.

---

# RESULTS

## R1 — the mirror of N9: the defect does NOT follow the BC to a different mesh family. Prediction NOT HELD; the named alternative obtains

Both arms staged by `run_a1fs_arm.sh` (the edits asserted in-script; the driver
aborts if any pattern is missing, and `grep -c patchVelocity` on the edited
runScript prints 0 in both driver logs). Patched IDWarp stamped in-log; the
np=4 arm's log reads `Decomposition method scotch [4]`.

| A1 + `freestreamVelocity` arm | CD/shape analytic | FD (own run) | rel. err | baseline CD |
|---|---|---|---|---|
| np=1 (`a1fs_np1.log`) | 6.433596e-02 | 6.432657e-02 | **4.2823e-04 (0.043%)** | 0.02198243 |
| np=4 scotch (`a1fs_np4scotch.log`) | 6.433595e-02 | 6.432654e-02 | **4.2792e-04 (0.043%)** | 0.02197816 |

- Clause (i) of the prediction **HELD** (np=1 control 0.043% <= 0.5%).
- Clause (ii) — the headline — **NOT HELD, and not marginally**: the np=4
  scotch analytic differs from the np=1 analytic by **1.55e-07 relative**
  (per-component over the 8 shape DVs: max 1.16e-05, median 6.4e-07), the two
  FD columns by 4.7e-07, and the CL/shape rows are identical to every printed
  digit (4.983140e+00 both, rel. err 1.83e-04 both). Baseline CD is invariant
  to 1.9e-04. Nothing moved.
- The registered named alternative therefore obtains, verbatim: **"the trigger
  needs a third ingredient beyond BC x scotch-cut (mesh family / cut
  topology), the n=1-family confound SURVIVES on the defect side, and the
  upstream report must say so."**
- The obvious escape — "A1's scotch cut is too benign to excite anything" — was
  closed at zero solver cost with the reach campaign's own `analyze_cuts.py`
  (unmodified) on this arm's `cellProcAddressing`: A1's np=4 scotch cut is
  **131 internal faces, of which 120 are oblique** (no axis-aligned normal to
  0.999) — a maximally jagged, mixed-orientation cut, the cut family the
  reach matrix identified as the catastrophic one. A4's own np=4 scotch cut,
  measured by the same script, is 328 faces (x 143 / y 7 / z 159 / oblique 19).
  A1's cut is jagged and the defect still does not appear.
- The BC transplant did land: baseline CD moved 0.52% from the record
  `inletOutlet`+patchV configuration (0.02198243 vs 0.02209812) — the same
  order as the 0.44% CD0 shift N9 measured going the other way on A4, so the
  case really is running the freestream-family BC, and running it cleanly.

**What R1 costs the trigger claim.** `freestreamVelocity` is now measured
**necessary but NOT sufficient**: installed on a clean case, with a jagged
scotch cut at the same rank count, it produces no defect at all. Every
defective measurement in this lab still lives on one 2,777-cell Ahmed
background mesh family. The reach sweep's n=1-family caveat is not repaired by
this session — it is **confirmed**, by the sharpest available test.

## R3a — the setup-robustness arm that was supposed to be a formality: the defect is SCHEME-GATED. Prediction NOT HELD, decision rule fired

`a4knob_schemes.log`, A4 coarse, np=4 scotch (`Decomposition method scotch
[4]`), `div(phi,U)` `bounded Gauss upwind` + `gradSchemes default cellLimited
Gauss linear 1`, everything else byte-identical to the established arm:

| arm | CD/shape analytic | FD (own run) | rel. err | CD0 | adjoint KSP |
|---|---|---|---|---|---|
| established (record) | 2.2086e-01 | 2.4258e-01 | **8.95%** | 0.1529749 | 590 iters, reason 2 |
| R3a schemes | 3.0977e-01 | 3.0906e-01 | **0.228%** | 0.1854378 | **68 iters**, reason 2 |

**Registered prediction (>= 4%) NOT HELD; the registered decision rule
("<= 1% ... REOPENS the mechanism question, reported loudly") FIRED.** The
discretization change is not small — CD0 rises 21% and the true gradient moves
from the 2.4e-01 class to the 3.1e-01 class — but the invariant under test is
each arm's analytic against its OWN FD in its OWN run, and by that invariant
the same mesh and the same scotch partition go from catastrophically wrong to
clean. The adjoint's conditioning collapses too: 68 Krylov iterations against
590.

Two knobs moved together here, so R3a alone convicts neither; the separating
arms R3a1/R3a2 were registered (commit above) before either ran.

## R3a1 / R3a2 — separating the two scheme knobs: the CONVECTION scheme is the carrier, the gradient default is a modulator

| arm | edit (one line of `fvSchemes`) | analytic | FD (own run) | rel. err | KSP iters |
|---|---|---|---|---|---|
| established (record) | — | 2.2086e-01 | 2.4258e-01 | **8.95%** | 590 |
| **R3a1** `a4knob_divupwind` | `div(phi,U)` -> `bounded Gauss upwind` | 2.7681e-01 | 2.7670e-01 | **0.041%** | 41 |
| **R3a2** `a4knob_gradlim` | `gradSchemes default` -> `cellLimited Gauss linear 1` | 3.1706e-01 | 3.2562e-01 | **2.63%** | 780 |

Each driver asserts that exactly one line moved (`diff` of the two files with
that line excluded must be empty, or the arm aborts).

- **R3a1 prediction HELD** (clean, 0.041% <= 1%). Swapping the convection
  scheme alone removes the defect completely — 0.041% is the same floor A1
  sits at.
- **R3a2 prediction NOT HELD as registered** (2.63% < the registered >= 4%),
  but the direction held: with the convection scheme untouched the defect is
  still present at **64x the clean floor**. What the default gradient scheme
  does is modulate the magnitude — limiting it takes 8.95% to 2.63% (3.4x)
  without curing anything.
- So the registered R3a1/R3a2 claim ("the convection scheme is the carrier,
  not the default gradient scheme") is **supported in its first half and
  qualified in its second**: the convection scheme gates the defect; the
  default gradient scheme is not innocent, it is a 3.4x modulator.

## R3c — Krylov restart: the arm does not produce a wrong answer, it produces NO answer. Prediction NOT HELD (by stall, not by shift)

`a4knob_restart60.log`, `"gmresRestart": 60` added to `adjEqnOption`
(everything else identical), np=4 scotch: GMRES stagnates at KSP residual
**2.5079e-02** and is still there at `gmresMaxIters` 1000 (2.507994e-02 at
iteration 900, 2.507895e-02 at 1000 — five digits of no progress over the last
100), so `solve_linear` raises `AnalysisError: Adjoint solution failed!` and
the arm exits rc=1 with no analytic to score.

**Registered prediction NOT HELD** (no analytic produced). The honest reading,
stated rather than spun: this is **not** a case of the converged answer moving
under a linear-algebra setting — the record's 1e-10 `gmresRelTol` arm already
showed the converged answer is tolerance-independent, and nothing here
contradicts it. What restart-60 shows is that the defective configuration's
adjoint operator is hard enough that a restarted GMRES stagnates completely
where the restart-free solve took 590 iterations — beside R3a's 68-iteration
solve on the clean-scheme configuration, the conditioning tracks the defect.
Recorded as a measured outcome of the registered arm, not reinterpreted into a
pass.

## R3b — primal depth: the arm is structurally unrunnable on this case, reported rather than dropped

`a4knob_primal10.log`, `primalMinResTol` 1e-10 with `endTime` 2000: DAFoam's
own convergence check treats "tolerance not reached at endTime" as a failure
and `solve_nonlinear` raises `AnalysisError: Primal solution failed!` before
any adjoint runs (rc=1, 1.53 core-min). The primal-depth axis therefore cannot
be probed by tightening `primalMinResTol` on this case at all — the knob is a
pass/fail gate, not a depth control.

This matters more than a failed arm usually would, because the zero-cost survey
this session ran across the seven cases found **`primalMinResTol` is a second
perfect correlate of the defect**, exactly as perfect as the BC: the two
defective cases (A4, Ahmed-35) both run 1e-4; all five clean cases run 1e-6 or
1e-8 (A1 1e-8, A2 1e-8, A5 1e-8, CBFS 1e-6, sail 1e-8, read from each case's
runScript). The cross-case survey therefore cannot separate "loose primal" from
"freestream BC" any more than it could separate the BC from the patchV
registration — and R3b was the within-case control that would have. **Recorded
as an open confound**, with the honest note that N9 (BC swapped at FIXED 1e-4)
already establishes BC-necessity within the case, so a loose primal cannot be
the whole story; whether it is a necessary co-ingredient is unmeasured.

A related zero-cost survey result, recorded because it kills a candidate before
anyone spends on it: **the turbulence model is NOT a correlate.** A4 and
Ahmed-35 are kOmegaSST — but so is CBFS, which is decomposition-clean; A1, A2,
A5 and the sail are SpalartAllmaras. kOmegaSST appears on both sides.

## R6 — the BRANCH hypothesis survives its sharpest test: it is the LIMITER, not the order and not the correction term. Both predictions HELD

Four convection schemes, same mesh, same np=4 scotch cut, same
`freestreamVelocity` BC, each judged against its own in-run FD:

| `div(phi,U)` | limiter branch? | 2nd order? | grad-correction term? | analytic | FD (own run) | rel. err | KSP iters |
|---|---|---|---|---|---|---|---|
| `linearUpwind limited` (established) | **YES** | yes | yes | 2.2086e-01 | 2.4258e-01 | **8.95%** | 590 |
| **`linearUpwind default`** (R6b) | **no** | yes | **yes** | 2.0572e-01 | 2.0399e-01 | **0.849%** | 41 |
| `Gauss linear` (R6a) | no | yes | no | 2.0299e-01 | 2.0267e-01 | **0.157%** | 223 |
| `upwind` (R3a1) | no | no | no | 2.7681e-01 | 2.7670e-01 | **0.041%** | 41 |

**R6b is the load-bearing row and its prediction HELD (0.849% <= 1%).** It is a
one-word edit: `limited` names A4's `cellLimited Gauss linear 1` gradScheme,
`default` names its unlimited `Gauss linear`. Same scheme family, same order,
the same gradient-correction term still evaluated and still requiring a halo
exchange — **the only thing removed is the min/max selection over the stencil**,
and the error falls by a factor of 10.5 while the adjoint's Krylov count falls
from 590 to 41. **R6a prediction HELD** (0.157%). The registered loud
alternative — R6b dirty, which would have refuted the hypothesis — did not
occur.

**R6b-control (np=1, same discretization): 1.6215e-04 = 0.016%.** The
registered prediction (np=1 within a factor 2 of 0.849%) is **NOT HELD**, and
the named alternative obtains: the discretization's own floor is 0.016%, so
something real survives at np=4. Reading the two rows together sharpens it
further: the **analytic is 2.0572e-01 at BOTH np=1 and np=4 scotch — identical
at all five printed digits** — while the FD column moves 2.0568e-01 -> 2.0399e-01
(0.82%). With the limiter branch removed, **the adjoint itself is
decomposition-invariant at printed precision**, and the surviving 0.849% is
dominated by an FD-column shift under decomposition, not by an analytic error.

So the ordering of the evidence is: the limiter branch carries the defect; the
gradient-correction term it feeds does not (R6b keeps the term and is clean);
the scheme's order does not (R6a is second order and clean). **The supervisor's
branch hypothesis passes the test that was registered to break it.**

## R5 — operator versus contraction: the two levers are NOT the same kind of fix, and one of them only hides the defect

Cross-residual instrument (discriminators' `w4_dump`/`w4_crossres`, maps rebuilt
per lever by `build_maps_upw.py` / `build_maps_io.py`, both re-pathed copies of
the reach campaign's `build_maps_a35.py`). Map validation printed by the scripts
themselves before use: duplicated processor-face phi copies agree at
**2.665e-15** (scheme lever) / **3.553e-15** (BC lever); mapped primal states
agree with np=1 at 2.55e-03 / 2.03e-03 (reconvergence noise); 328 duplicated
proc-face phi states in both, `n_np4 - n_np1 = 328` exactly. Sign correction
`r_true = res + 2b` applied offline as the amended convention requires (every
own-operator log line prints the degenerate `ratio=2.000000e+00`, confirming the
convention in-log).

True residual ||A^T psi + b|| under the **np=1 operator of each lever's own
configuration**, as a ratio to that configuration's ||b||:

| configuration (all np=4 `scotch`, same mesh, same cut) | gradient error | **operator cross-residual** | its own np=1 floor | ratio to floor |
|---|---|---|---|---|
| established (`freestreamVelocity` + `linearUpwind limited`) | 8.95% | **329x ||b||** (record) | 1.1e-04 | 3.0e+06 |
| **R5a — scheme lever** (`upwind`, BC kept) | 0.041% | **1.3548e-02 x ||b||** | 2.00e-06 | 6.8e+03 |
| **R5b — BC lever** (`inletOutlet`, limiter kept) | 0.019% (N9) | **1.0472e+00 x ||b||** | 6.40e-06 | 1.6e+05 |

**Registered prediction R5 (both levers <= 5x ||b||) HELD** — numerically, for
both. But the two rows are not the same result, and the record says so plainly:

- **The scheme lever fixes the operator.** 329x -> 0.0135x is a collapse by a
  factor of **24,300**. The np=4 analytic also matches np=1 to 2.5e-05
  (2.768136e-01 vs 2.768066e-01, `W4D` lines of the two dumps). Removing the
  limiter branch does not merely rotate the objective away from the damage; the
  damage is gone.
- **The BC lever does NOT fix the operator — it hides the defect.** At
  1.047x ||b|| the `inletOutlet` configuration's scotch adjoint still fails to
  satisfy its own serial adjoint system by a residual the size of the
  right-hand side itself, and **163,600x its own np=1 floor**. For scale, the
  reach campaign convicted the Ahmed-35 case of carrying the wrong-operator
  defect at **5.45x ||b||**; 1.05x is the same order of wrongness, and it sits
  underneath a `check_totals` that reads 0.019%. This is L-36's failure mode
  caught in the act: **the gradient is clean because the contraction is small,
  not because the operator is right.**
- Independent corroboration of N9 fell out of this arm for free: `io_d_np4scotch`
  prints `W4D framework_dCDdshape=2.406182395247966e-01` — the N9 record value
  to **all sixteen digits**, from a separately staged case dir and a different
  task.

## R4 — the same-geometry conformal-versus-refined pair, finally run: the defect fires WITHOUT hanging nodes. Prediction HELD

`a4_conformal_mesh`: A4's own recipe, same STL, same background `blockMesh`,
same `0.orig` (`freestreamVelocity`), same `fvSchemes` (limiter present) — with
the two snappy refinement levels dropped to 0. Result: **2,336 cells, `cellLevel`
uniformly 0** (the file reads `2336{0}` — OpenFOAM's uniform-list form; gate
passed), `Mesh OK`. Arm `a4conf_np4scotch`, np=4 scotch, `check_totals`:

| mesh | hanging nodes | analytic | FD (own run) | rel. err |
|---|---|---|---|---|
| A4 coarse (record) | 502 cells at `cellLevel` 1, 456 interface faces | 2.2086e-01 | 2.4258e-01 | 8.95% |
| **A4 conformal (R4)** | **none** | 1.8315e-01 | 1.8847e-01 | **2.82%** |

**Prediction HELD** (2.82% >= the registered 2%). The docket clause the reach
matrix had to report as "untested in pair form" — *"the hanging-node hypothesis
is either supported by a conformal-versus-refined pair on the same geometry or
reported as untested"* — is now **run and reported**: on the same geometry, with
refinement removed and nothing else changed, the defect is still there at 70x
the clean floor. Refinement interfaces are refuted as a necessary ingredient by
direct pairing, which is what the docket asked for; the reach matrix's
`cellLevel`-0 localization and cut-count anticorrelation said the same thing
indirectly, and now agree with a controlled pair.

(The magnitude drops from 8.95% to 2.82%. That is expected and carries no
mechanism claim: removing refinement changes the mesh, hence the scotch cut,
hence the contraction — the quantity the reach campaign already measured as
case-and-objective specific.)

**Consequence for the upstream report, stated as the session's most consequential
finding:** the previous framing — "`freestreamVelocity` is necessary for the
defect; with `inletOutlet` the same cut produces a clean operator" — is
**wrong in its second half and must be corrected**. `inletOutlet` produces a
clean *gradient* on this objective and a still-wrong *operator*. The
configurations this lab called safe are not safe; they are quiet.

## R2 / R2b — mesh convergence: the established configuration will not solve one level up

R2 as registered is **NOT SCORED — unmeasurable as staged.** New mesh
`a4_medium_mesh`: A4's `blockMeshDict` background doubled per axis
((26 6 15) -> (52 12 30)), every other dict byte-identical (the driver aborts
if `snappyHexMeshDict` differs), `endTime` 500 -> 1000 disclosed. Gate passed:
**19,619 cells, 1,040 at `cellLevel` 1**, `Mesh OK`. The np=4-scotch arm's
primal converged normally (CD 0.11399, U residuals at 1e-5), and then the
adjoint **failed**: GMRES exhausted `gmresMaxIters` 1000 at KSP residual
**1.7188e-02**, `PetscConvergedReason: -3`, `AnalysisError: Adjoint solution
failed!` (`a4med_np4scotch.log`, rc=1, 33.60 core-min). No analytic exists to
compare against the FD, so the registered R2 prediction cannot be scored
either way, and the registered FD-resolvability guard never applied.

That failure is itself a datum, and it rhymes with R3c: in the defective
configuration the np=4-scotch adjoint operator is badly enough conditioned that
a restarted GMRES stagnates on the coarse mesh (R3c) and an unrestarted one
stagnates on the refined mesh (R2). The clean-scheme arms converge in 38-68
iterations on the same coarse mesh.

**R2b — prediction HELD, on both clauses.** `a4med_divlinupw_unlim` (the same
19,619-cell refined mesh, np=4 scotch, one edit: `div(phi,U)` `bounded Gauss
linearUpwind default`): the adjoint **converges** — `PetscConvergedReason: 2`
at 149 iterations, where the limited configuration exhausted 1000 — and the
CD/shape analytic reads 7.2627e-02 vs its own FD 7.3195e-02 = **0.777%**
(<= the registered 2%). (The arm ran to completion under its detached driver
through the 2026-08-05 session kill; ledger line self-written 17:49:08Z,
rc=0.) So one uniform refinement level up: with the limiter branch present
there is NO adjoint solution at all; with it removed, the solve converges and
the error sits at 0.777% — the same scale as the coarse mesh's unlimited
0.849%, i.e. the small surviving effect neither vanishes nor grows under
refinement. (No np=1 control was bought on the refined mesh; on the coarse
precedent that residual is dominated by the FD column's decomposition shift,
not the analytic.)

## The seven-case scheme survey (zero solver cost): a THIRD perfect correlate, and it retro-explains R1's null

Read from each case's on-disk `system/fvSchemes` (CBFS's limiter tokens are
all inside comments; verified by reading the block):

| case | `div(phi,U)` | limiter branch in U-convection? | `freestreamVelocity`? | `primalMinResTol` | defect? |
|---|---|---|---|---|---|
| A4 | `bounded Gauss linearUpwind limited` (= `cellLimited Gauss linear 1`) | **YES** | YES | 1e-4 | **YES** |
| Ahmed-35 | same | **YES** | YES | 1e-4 | **YES** |
| A1 | `bounded Gauss linearUpwindV grad(U)`, gradSchemes `Gauss linear` | no | no (record) | 1e-8 | no |
| A1+fsV (R1, this session) | same unlimited scheme | no | **YES** | 1e-8 | **no** |
| A2 | `linearUpwindV grad(U)`, unlimited | no | no | 1e-8 | no |
| A5 | `linearUpwindV grad(U)`, unlimited | no | no | 1e-8 | no |
| CBFS | `linearUpwind grad(U)`, unlimited | no | no | 1e-6 | no |
| sail | `linearUpwindV grad(U)`, unlimited | no | no | 1e-8 | no |

Three things this table does:

1. **It retro-explains R1's null.** The mirror arm installed the BC on A1 but
   A1's convection gradient is UNLIMITED — under the branch hypothesis
   (limiter x BC x cut) the R1 arm was missing a necessary ingredient, and its
   clean result is exactly what the hypothesis predicts. The "third axis" R1's
   named alternative demanded is not mesh family after all: it is the limiter,
   identified within-case by R6 and consistent cross-case here.
2. **It is a third perfect correlate, and the same honesty applies as to the
   first two:** limited-scheme, `freestreamVelocity`, and loose
   `primalMinResTol` all separate the seven cases identically, so the survey
   alone cannot rank them. What breaks the symmetry is the within-case
   controls: N9 (BC swapped alone -> clean gradient) and R6b (limiter removed
   alone -> operator fixed, R5a) are both measured on A4; the primal-tolerance
   lever has no within-case control (R3b, structurally unrunnable). The causal
   weight sits on the within-case arms; the survey corroborates.
3. **The still-missing experiment is now precisely one arm:** A1 with
   `freestreamVelocity` AND `cellLimited` convection (both ingredients
   installed on the clean structured mesh). If the conjunction is right, that
   arm goes dirty and the defect finally has a second mesh family; if it stays
   clean, the Ahmed background mesh (or its loose primal) is still carrying
   something. Registered here as the named next arm, NOT run in this session
   (budget: 128.28 of 150 used at the point of writing; the arm needs a
   np=1+np=4 pair plus, if it fires, a cross-residual — beyond what remains).

## What this session changes about the trigger claim

1. **The n=1-family confound did NOT die — it is confirmed.** R1 is the
   sharpest available test of BC-necessity-as-sufficiency and it came back
   null: `freestreamVelocity` installed on a structured conformal NACA0012,
   with a jagged 4-rank scotch cut (120 of 131 cut faces oblique), leaves the
   analytic invariant to 1.55e-07. Every defective measurement in this lab
   still lives on one Ahmed background-mesh family. The BC is **necessary but
   not sufficient**, now by measurement rather than by the absence of a test.
2. **The missing ingredient is named, and it is not the mesh family: it is a
   BRANCH in the differentiated path.** The limiter in `linearUpwind limited`
   gates the defect (R6b: remove only the min/max selection and 8.95% -> 0.849%
   with the analytic decomposition-invariant at printed precision, KSP 590 ->
   41), and the seven-case scheme survey above shows the limiter separates the
   defective cases from the clean ones perfectly — including retro-explaining
   R1's own null.
3. **Refinement interfaces are refuted by a controlled pair, not just by
   localization** (R4: same geometry, hanging nodes removed, defect still
   fires at 2.82%).
4. **A clean gradient is not a clean operator, and this session caught the
   difference in the act.** The BC lever leaves the operator wrong at
   1.047x ||b|| (163,600x its own floor) under a `check_totals` reading
   0.019%; the scheme lever collapses the operator error 24,300x. The lab's
   own L-36 predicted exactly this and it is now measured on the two levers
   that matter for what gets told upstream.
5. **Two cross-case correlates remain confounded and are recorded as such:**
   `primalMinResTol` (1e-4 on both defective cases, 1e-6/1e-8 on all five
   clean ones) could not be separated within-case because DAFoam treats a
   tightened `primalMinResTol` as a pass/fail gate (R3b); and the turbulence
   model is eliminated (kOmegaSST sits on both sides).
6. **The limit of what this session establishes, stated plainly.** Every arm
   that moved the defect is a within-case control on A4 (one mesh, one
   geometry); the cross-case scheme survey corroborates but is a third
   confounded correlate. The branch hypothesis is NOT yet supported by a
   second case that ACQUIRES the defect when the limiter and the BC are both
   installed — that arm (A1 + `freestreamVelocity` + `cellLimited` convection)
   is the named next experiment, and it was deliberately not improvised here:
   it was not in any registered edit set and the budget does not cover its
   full pair-plus-crossres protocol.

## Scored predictions, all of this session's arms

| arm | registered prediction | outcome |
|---|---|---|
| R1 np=1 control | <= 0.5% vs own FD | **HELD** (0.043%) |
| R1 np=4 scotch | defect fires: >= 2% vs own FD, analytic shift >= 2% | **NOT HELD** (0.043%; analytic shift 1.6e-07) — named alternative obtains: third ingredient required; the scheme survey then named it |
| R2 | defect persists under refinement: >= 3% | **NOT SCORED — unmeasurable**: adjoint diverges (reason -3 at 1000 iters); reported as the finding |
| R2b | refined mesh, limiter removed: converges AND <= 2% | **HELD** (reason 2, 149 iters; 0.777%) |
| R3a (two knobs) | error stays >= 4% | **NOT HELD** (0.228%) — decision rule fired, R3a1/R3a2 registered |
| R3a1 (convection only) | clean <= 1% | **HELD** (0.041%) |
| R3a2 (gradient default only) | dirty >= 4% | **NOT HELD** (2.63% — still 64x the floor; direction held, magnitude under the band: the gradient default is a 3.4x modulator, not the gate) |
| R3b (primal 1e-10) | error in [7%, 11%] | **NOT SCORED — unmeasurable**: DAFoam treats unreached primalMinResTol as primal FAILURE; knob is a gate, not a depth control; the primal-tolerance confound stays open and is recorded |
| R3c (gmresRestart 60) | analytic within 0.1%, error in [8.6%, 9.3%] | **NOT HELD (by stall)**: GMRES stagnates at 2.51e-02, no answer produced |
| R4 (conformal same-geometry) | defect still fires >= 2% | **HELD** (2.82%) |
| R5a (scheme lever, operator level) | crossres <= 5x \|\|b\|\| | **HELD** (0.0135x; collapse by 24,300x — the lever FIXES the operator) |
| R5b (BC lever, operator level) | crossres <= 5x \|\|b\|\| | **HELD numerically (1.047x), loud in substance**: 163,600x its own floor — the lever HIDES the defect, L-36's mode measured in the act |
| R6a (`Gauss linear`) | clean <= 1% | **HELD** (0.157%) |
| R6b (`linearUpwind default`) | clean <= 1% (load-bearing branch clause) | **HELD** (0.849%) |
| R6b-control (np=1) | within factor 2 of 0.849% | **NOT HELD** (0.016%) — named alternative obtains: a small real decomposition effect (~0.8%, FD-column-dominated) survives the limiter removal |

Every score is against the registered wording, committed before the arm ran
(25f52868, 671f40bb, c22b0f00, b0aa6102, 4ea782e3); none was reworded after
measurement.

## Cost ledger (wall x cpus-cap, per `W4-defect-robustness/ledger.txt`)

21 ledger lines, re-summed: **128.28 core-min of the 150 budgeted.** The two
largest lines are the two refined-mesh arms (33.60 failed-adjoint scotch arm —
charged in full, stated, its failure is a datum; 19.83 for R2b). Zero-cost
items (the seven-case scheme/BC/tolerance/turbulence surveys, the A1 cut
classification, both cross-residual sign corrections, the two map rebuilds)
were offline python on on-disk artifacts. The 2026-08-05 session was killed by
the weekly usage limit twice (~17:20Z, ~17:45Z) and the box was power-cycled
before 2026-08-07; the one arm then in flight (R2b) ran to completion under
its detached driver — no solver core-minutes were lost to either kill. One
accounting confession: an aborted mistaken launch of the conformal arm under
the wrong driver cost ~10 s of container start-up before it was killed; it
never reached the solver and is not ledgered.


