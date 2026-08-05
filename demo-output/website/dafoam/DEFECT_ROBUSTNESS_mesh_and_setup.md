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

---
