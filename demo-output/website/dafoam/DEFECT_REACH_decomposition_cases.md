# How far does the decomposition-adjoint defect reach? A breadth matrix across cases, meshes, and cuts

**2026-08-04, well W4. Docket items `w4-does-the-decomposition-defect-reach-other-cases`
(120 core-min) and `w4-decomposition-invariance-is-a-gate` (60), both approved under
Katie's blanket approval 2026-08-04 and claimed by this session.** Builds on the
verified phenomenon (`VERIFICATION_A4_decomposition_supervisor_sweep.md`), the named
mechanism (`DISCRIMINATORS_A4_decomposition_mechanism.md` + its 2026-08-04
amendments), and the mechanism sweep
(`VERIFICATION_A4_mechanism_supervisor_sweep.md`). Purpose: run cases that SHOULD and
SHOULD NOT show the defect, so the trigger condition is bracketed by measurement
rather than asserted from one case. Run artifacts:
`/home/ubuntu/certonomous-runs/W4-defect-reach/` (per-arm dirs, logs, `ledger.txt`,
drivers).

**Status: predictions pre-registered BEFORE their runs — N1-N7 at commit 99f5d41d
(2026-08-04 18:35Z), N8 at commit b8ea85c4 (2026-08-05 15:13Z) — and unedited
since; results appended below the marked line.** The campaign spans two sessions:
the 2026-08-04 session was killed by a session limit mid-collection and the box
was power-cycled overnight; every 2026-08-04 arm nevertheless ran to completion
under its detached driver (see the cost ledger's accounting note).

## What is already on record (folded in, not rerun)

From the verified np-sweep table (`VERIFICATION_A4_decomposition_supervisor_sweep.md`
Axis 1, all patched-IDWarp, A4 coarse 2,777-cell snappy mesh WITH refinement
interfaces, single shape DV, analytic-vs-own-run-FD):

| arm | log | analytic | FD | rel. err |
|---|---|---|---|---|
| np=1 | `a4_np1_patched.log` | 2.4150e-01 | 2.4232e-01 | 0.34% |
| np=2 scotch | `a4_np2_patched.log` | 2.4118e-01 | 2.4182e-01 | **0.26%** |
| np=3 scotch | `a4_np3_patched.log` | 2.5641e-01 | 2.4178e-01 | **6.05%** |
| np=4 scotch | `a4_np4_patched.log` | 2.2086e-01 | 2.4258e-01 | **8.95%** |
| np=4 simple 4x1x1 | `a4_np4_simple4x1x1.log` | 2.4220e-01 | 2.4220e-01 | 0.00054% |
| np=4 simple 1x4x1 | `a4_np4_simple1x4x1.log` | 2.4379e-01 | 2.4265e-01 | 0.47% |

Three record facts this matrix leans on:

1. **The np=2-clean / np=3-dirty contrast is itself evidence.** scotch at np=2 (0.26%)
   sits at the np=1 floor; scotch at np=3 (6.05%, analytic HIGH where np=4's is LOW)
   is catastrophic. Rank count per se is not the trigger (np=4 simple is clean);
   what changes from np=2 to np=3 is the shape/orientation of scotch's cut.
2. **The deliberate "cut through the refinement region" discriminator is already on
   record, backwards:** `simple` 4x1x1 cuts **68** refinement-interface faces (17x
   more than scotch's 4) and is the CLEANEST configuration (0.00054%), and the
   mechanism record's localization puts all 15 large cross-residual entries on
   `cellLevel` 0 cells away from refinement interfaces. "Partition cut touching a
   refinement interface" is refuted as the trigger; it does not need a new run.
3. Decomposition-invariant so far: A1 (4,032-cell structured/conformal airfoil,
   np=1 vs np=4), A2 (38,304-cell conformal wing, scotch vs simple at np=4), A5
   (4,800-cell conformal U-bend, scotch vs simple at np=4) — all at the 1e-04-ish
   level. Every clean case is conformal; the only dirty case (A4) is the only
   snappy-refined mesh tested. That confound is what this matrix breaks.

## The new arms and their PRE-REGISTERED predictions

Hypothesis under test, from the mechanism record's localization (worst cells on
y-normal scotch processor faces; x-normal slabs clean; jagged mixed-orientation
scotch cut catastrophic): **the defect is a property of the parallel reverse-AD
operator's treatment of processor-boundary coupling whose magnitude depends on the
cut's shape/orientation relative to the flow, and it is excited by the cut
geometries scotch produces on snappy-refined meshes — not by refinement interfaces
per se, not by rank count, not by one specific mesh.**

| arm | case / mesh | decomposition | protocol | prediction (registered before running) |
|---|---|---|---|---|
| N1 | A4 (snappy+refinement, 2,777 cells) | np=4 `simple` 1x1x4 (z-normal slabs) | `check_totals`, patched IDWarp | rel. err in **[0.05%, 1.5%]** — same order as y-normal's 0.47%, far below scotch's 8.95%: planar slabs of any orientation are benign-to-moderate |
| N2 | A4 | np=4 `simple` 2x2x1 (x+y planar cuts, 4-rank corner line) | `check_totals` | rel. err **<= 1%** (roughly the x- and y-slab scales combined). Registered decision rule: if > 2%, "scotch-style jaggedness required" is REFUTED — mixed-orientation planar cuts with corners suffice |
| N3 | **Ahmed-35** — NEW second snappy-refined case: ahmed_35.stl (same frame, bbox identical), meshed by A4's own recipe (blockMesh+snappy, cellLevel interfaces present) | np=1 | `check_totals` | control: rel. err **<= 1.5%** (the np=1 floor of this case class) |
| N4 | Ahmed-35 | np=4 `scotch` | `check_totals` | **DEFECT APPEARS: rel. err >= 2%**, and the analytic differs from N3's analytic by >= 2% while the FD column stays within ~0.5% of N3's. This is the headline prediction: the defect travels with (snappy-refined mesh x scotch cut), not with A4's particular mesh. If instead N4 is clean (<1%), the trigger is narrower than hypothesized (specific to A4's cut geometry) and the record says so |
| N5 | Ahmed-35 | np=4 `simple` 4x1x1 (x-normal slabs) | `check_totals` | clean: rel. err **<= 1%** regardless of N4's outcome |
| N6 | **CBFS** (21,000-cell conformal blockMesh — `constant/polyMesh` carries NO cellLevel — beta-field DVs, 21,000 components, `varianceU` objective, `dafoam-subpclu:v1` + `DAFOAM_SUBPC_TYPE=lu` exactly as the record arm) | np=4 `simple` 4x1x1 vs the np=4 `scotch` RECORD arm (`W4-adjoint-pc-unblock/cbfs_beta`, FD at 3 cells on record: 0.085% / 0.059% / 0.199%) | `compute_totals`; both arms' gradient vectors mapped to serial cell ordering via each arm's own `cellProcAddressing` (rank-concatenation convention verified before use) | **decomposition-invariant**: mapped analytic agrees at the three recorded FD cells to **<= 1%** per component, vector norms to <= 2%. Conformal mesh + different DV type (volume field, not shape) both stay clean |
| N7 (contingent — runs only if N4 fires) | Ahmed-35 | scotch psi vs np=1 operator | the cross-residual instrument of the discriminators session (`W4-a4-discriminators/runScript_w4.py` tasks `w4_dump`/`w4_crossres`, `build_maps.py`), sign convention **A^T psi = -b**: the instrument computes `Atpsi - b`, so own-operator logs print the degenerate `ratio=2.0` and the reported numbers are exact offline corrections `res + 2b` from the dumped vectors — stated per the amended M1 caption | cross-residual **>= 10x ||b||** under the np=1 operator, concentrated on momentum rows of partition-interface cells; np=1 control at its ~1e-04-ish floor |

**N8 (added 2026-08-05 15:12Z, registered BEFORE the arm ran; commit history is the
witness).** During the survey for the invariance-gate item, the last unchecked
published gradient turned out to be `naca0015_sail_coarse` (np=3, published PASS,
patched-regrade 0.0246% CD/shape) — and its `constant/polyMesh` carries
`cellLevel`: it is a snappyHexMesh-refined mesh, which falsifies the docket
rationale's premise that "A4 is the only case in either ladder carrying
snappyHexMesh hanging-node refinement" (the pre-ladder sail is snappy too, 63,920
cells, 23x A4's size). Arm N8: sail check_totals, patched IDWarp, np=3 `simple`
3x1x1 vs the np=3 `scotch` record (`W5-regrade/sail_patched_checktotals.log`).
Prediction: **decomposition-invariant at the graded level — CD/shape aggregate
rel. err vs its own FD stays <= 0.5%, and the analytic shape components shift <= 1%
from the scotch-arm record**; registered on the grounds that the sail's own-FD
agreement at 0.0246% under scotch already bounds any operator-error contraction
into THIS objective as tiny, and FD is decomposition-invariant to ~0.4% on the A4
precedent. If instead the analytic shifts > 1%, the published sail PASS is
decomposition-lucky and the defect reaches a fourth case at gradient level.

Scoring discipline: each prediction is scored HELD / NOT HELD / NOT SCORED exactly
as written above; no post-hoc bands.

**N8, added 2026-08-05 BEFORE its arm ran** (all N1-N7 arms were complete by then;
this arm was identified while surveying the graded-gradient inventory for the gate
item): **naca0015_sail_coarse** — the lab's THIRD snappyHexMesh case (63,920 cells,
`constant/polyMesh` carries `cellLevel`), whose published PASS gradient was measured
at np=3 `scotch` and carries its own FD column there (stock 4.52%; patched-IDWarp
corroboration 0.0246%, CD/shape analytic 2.042422e-01 vs FD 2.042324e-01,
`W5-regrade/sail_patched_checktotals.log`). New arm: np=3 `simple` 3x1x1, patched
IDWarp, `check_totals`. Pre-registered prediction: **decomposition-invariant at the
graded configuration's own scale — CD/shape rel. err vs its own FD <= 0.5%, and the
analytic within 1% of the scotch-arm analytic 2.042422e-01.** Reasoning: scotch at
np=3 on this snappy mesh already matches its own FD to 2.5e-04, so whatever operator
error exists there contracts to nothing against this objective; slabs are the benign
cut family on every case measured so far. A large simple-arm error would REFUTE
"planar slabs are benign" on a bigger snappy case.

## Budget

180 core-min combined across the two items. Planned: N1+N2 ~12, Ahmed-35 mesh ~1,
N3 ~4, N4+N5 ~12, N6 ~16, N7 (contingent) ~12; total ~45-60 planned, the rest is
reserve for the contingent instrument and any arm that needs a rerun. All runs
ledgered wall x cpus-cap in `W4-defect-reach/ledger.txt`; overruns stated.

*(Results and verdict sections follow after the runs; nothing below this line
existed at pre-registration commit time.)*

---

# RESULTS (2026-08-04/05)

Two session interruptions occurred mid-campaign (the 2026-08-04 session limit at
~18:53Z, and a Claude Code process death at ~15:08Z on 2026-08-05, plus an
overnight box power-cycle between them). **Zero solver core-minutes were lost to
either:** every launched arm runs detached inside its docker container and
self-ledgers on exit, so all 16 pre-kill ledger entries carry rc=0 with complete
logs and dumps; recovery each time was pure inventory. The interrupted work was
polling, not solving.

## N1/N2 — A4, the two new cut orientations, with the cut classifier

`check_totals`, patched IDWarp, np=4, same protocol as the verified table
(`run_a4_arm.sh`, logs `a4_simple1x1x4.log` / `a4_simple2x2x1.log`). The cut
classifier (`analyze_cuts.py`) was validated by exactly reproducing the record's
scotch-cuts-4 / simple-4x1x1-cuts-68 refinement-interface counts before use.

| arm | analytic | FD (own run) | rel. err | cut faces (x/y/z/oblique) | ref.-interface faces cut |
|---|---|---|---|---|---|
| np=2 scotch *(record)* | 2.4118e-01 | 2.4182e-01 | 0.26% | 128 (80/1/30/17) | 0 |
| np=3 scotch *(record)* | 2.5641e-01 | 2.4178e-01 | **6.05%** | 248 (160/6/74/8) | 4 |
| np=4 scotch *(record)* | 2.2086e-01 | 2.4258e-01 | **8.95%** | 328 (143/7/159/19) | 4 |
| np=4 simple 4x1x1 *(record)* | 2.4220e-01 | 2.4220e-01 | 0.00054% | 406 (328/25/31/22) | 68 |
| np=4 simple 1x4x1 *(record)* | 2.4379e-01 | 2.4265e-01 | 0.47% | y-slabs | — |
| **np=4 simple 1x1x4 (N1, new)** | 2.4368e-01 | 2.4241e-01 | **0.52%** | 624 (41/54/465/64) | 48 |
| **np=4 simple 2x2x1 (N2, new)** | 2.4605e-01 | 2.4265e-01 | **1.40%** | 594 (127/447/12/8) | 48 |

- **N1 prediction ([0.05%, 1.5%]): HELD.** z-normal slabs land at 0.52%, the same
  order as y-normal's 0.47% — every planar-slab orientation is now measured, all
  benign-to-moderate.
- **N2 prediction (<= 1%): NOT HELD — measured 1.40%.** The registered decision
  rule ("> 2% refutes jaggedness-required") did **not** fire. Two orthogonal
  planar cuts plus a 4-rank corner line cost more than any single slab (1.40% vs
  0.00054-0.52%) but remain 6x below scotch-np4 — intermediate, exactly the gap
  the rule left open.
- The refinement-interface anticorrelation **sharpens**: the two cleanest arms cut
  48 and 68 refinement-interface faces; the two dirtiest cut 4 and 4 (np=2's
  clean scotch cuts 0). Partition cuts through refinement interfaces are not the
  trigger — fifth and sixth data points, same direction as the record.

## N3/N4/N5 — Ahmed-35: the second snappy-refined case

New case built by A4's own recipe on `ahmed_35.stl` (same coordinate frame, bbox
identical to ahmed_25; roof-break at x=0.8621 = 222 mm x cos 35 deg from the tail
— genuinely the 35-degree shell; mesh points differ from A4's; 2,777 cells by
castellation coincidence, 502 cellLevel-1 cells, 456 refinement-interface faces).
`check_totals`, patched IDWarp (`stage_ahmed35.sh`, `run_a35_arm.sh`).

| arm | analytic dCD/dshape | FD (h=1e-3, own run) | rel. err vs own FD | analytic shift vs np=1 |
|---|---|---|---|---|
| np=1 | 2.991577e-01 | 1.7826e-01 | 67.8% | — |
| np=4 scotch | 2.951008e-01 | 1.7745e-01 | 66.3% | **-1.36%** |
| np=4 simple 4x1x1 | 2.897808e-01 | 1.7838e-01 | 62.5% | **-3.14%** |

Baseline CD is decomposition-invariant to **1.2e-05 relative**
(0.1643336/0.1643332/0.1643316); all GMRES solves reason 2 (448/536/537 iters).

**The FD column on this case is NOT resolved, and the predictions keyed to it are
scored against that fact.** The np=1 FD step sweep (`run_a35_step.sh`) reads
1.7826e-01 (h=1e-3) -> 1.9774e-01 (3e-3) -> 2.4702e-01 (1e-2): monotonically
step-dependent, rising toward the analytic 2.9916e-01 with no plateau anywhere —
while the primal's CD tail still drifts at ~6e-4 relative at `primalMinResTol
1e-4` (the 35-degree slant is the massively-separated regime; A4's 25-degree FD
resolved cleanly at the identical protocol). At h=1e-3 the central CD difference
(~3.6e-4) sits barely above that drift. **This case cannot grade analytic-vs-FD
at the established protocol**; what it measures cleanly is the analytic's
decomposition dependence: a 1.4-3.1% spread — 30-300x the conformal cases'
invariance level, 3-6x below A4's 8.7-10% spread.

- **N3 (np=1 control <= 1.5%): NOT HELD** — 67.8% at the protocol step, but the
  instrument failed, not necessarily the adjoint: the FD never resolved. Whether
  the np=1 analytic is also wrong on this case is NOT established either way.
- **N4 (defect appears: rel. err >= 2% AND analytic shift >= 2%): NOT HELD as
  registered** — the rel.-err clause is unscoreable against an unresolved FD, and
  the decomposition-shift clause measured 1.36%, under the registered 2%.
- **N5 (simple 4x1x1 <= 1%): NOT HELD** — 62.5% against the unresolved FD; and
  the simple analytic shifted 3.14%, MORE than scotch's 1.36% — the opposite
  ordering from A4.

## N7 — the cross-residual instrument convicts the a35 scotch operator anyway

Same protocol as the mechanism record (`run_a35_dump.sh` -> `w4_dump` at
np=1/scotch/simple; `build_maps_a35.py` maps validated on duplicated proc-face phi
at **2.7e-15 / 3.6e-15**, mapped primal vs np=1 at 8.5e-04 / 2.3e-03 reconvergence
noise; `a35_d_crossres[2]`). Sign convention stated per the amended M1 caption:
the `w4_crossres` instrument computes `Atpsi - b` while the system is
**A^T psi = -b**, so own-operator log lines print the degenerate
`ratio=2.000000e+00` and the table below is the exact offline correction
`res + 2b` recomputed from the dumped vectors (`w4x_res_*.npy`); the
`w4_crossres2` task has the sign right natively and its log matches these numbers
digit for digit.

| psi from | ||A^T psi + b|| under np=1 operator, ratio to ||b||=0.17873 | same, linearized at the scotch arm's own mapped state |
|---|---|---|
| np=1 (control) | **3.984e-04** | 1.915e-03 |
| np=4 scotch | **5.446e+00** | **5.446e+00** (5.446299 -> 5.446301, unchanged to six digits) |
| np=4 simple 4x1x1 | 3.308e-01 | 3.308e-01 |

- **The scotch parallel operator differs from the serial operator on this case
  too**: 5.45x ||b||, 1.4e+04x the np=1 floor, unchanged to six digits under the
  state swap (state confound closed exactly as on A4).
- **Localization reproduces the A4 signature on different rows**: 97.28/97.34 of
  the scotch residual norm sits in **U2 (z-momentum) rows**; 13 of the top 15
  entries sit on scotch partition-interface cells, ALL cellLevel 0; the three
  dominant cells (|r| = 0.79, 0.40, 0.40) each touch exactly ONE foreign rank
  through exactly ONE **x-normal** processor face. On A4 it was U0 rows on
  y-normal faces: **the affected momentum component tracks the cut, not the
  case** — consistent with the halo-exchange reverse-AD candidate surface.
- simple 4x1x1 leaves 0.331 of ||b|| (830x the floor, 16x under scotch), top
  entries also interface cells (8/10). Note ||psi|| here DEFLATES under np=4
  (0.0580 np=1 -> 0.0304 scotch / 0.0244 simple) — A4's 16.5x inflation is a
  case-level symptom, not part of the defect's signature.
- **N7 prediction: NOT HELD on the registered magnitude clause — 5.45x measured
  against the registered ">= 10x"** (missed by ~2x; the qualitative content, four
  orders above the floor and interface-localized momentum rows, is exactly what
  was predicted; scored strictly anyway). The localization and control clauses
  HELD.
- **The decoupling finding (new, and the matrix's sharpest lesson):** operator
  corruption and gradient damage do not scale together. a35-scotch's operator
  residual is 16x larger than a35-simple's, yet its analytic gradient shift is
  2.3x SMALLER (1.36% vs 3.14%); A4-simple-4x1x1 carries 0.094 of ||b|| operator
  residual and a 0.00054% gradient error. What the wrong operator costs the
  gradient depends on how its error contracts against the objective's adjoint
  direction — so a clean `check_totals` at one decomposition certifies nothing
  about the operator, only about that contraction.

## N6 — CBFS: conformal mesh, 21,000-component field DV, decomposition-invariant

`run_cbfs_arm.sh` (np=4 simple 4x1x1, `dafoam-subpclu:v1` + `DAFOAM_SUBPC_TYPE=lu`
— the record arm's exact environment; the sub-PC switch cannot move a
right-preconditioned GMRES solution converged in the unpreconditioned norm) vs the
np=4 scotch RECORD arm (`W4-adjoint-pc-unblock/cbfs_beta`). Both gradients mapped
to serial cell ordering by each arm's own `cellProcAddressing` (exact permutations;
DAFoam's non-distributed field-DV ordering is rank-offset concatenation of local
cells, verified in the shipped container source, `DAInputField.C`
`globalSelectedCellNumbering_.toGlobal`). `analyze_cbfs.py`:

- gradient norms 1.455805e-05 (scotch) vs 1.455849e-05 (simple); **norm of the
  difference 1.13e-04 of ||g||**; max single-entry diff 3.8e-04 of max|g|.
- at the three FD-verified record cells: rel. diffs **1.5e-05 / 8.7e-05 /
  8.0e-05**; top-20 |g| cells max 1.6e-04.
- converged objective invariant to **2.0e-08** (1.5279278906e-02 vs
  1.5279278602e-02); adjoint reason 2 both (667 vs 766 iters).
- **FD column at BOTH decompositions** (gate clause): scotch record cell 5491
  (serial 471) FD 1.914384790951e-06 vs analytic 1.916018813330e-06 = 0.085%;
  this session ran the same central difference (+-0.05, fresh primals, S1
  protocol) at the SIMPLE decomposition's own index for serial cell 471
  (`cbfs_fd_s471_[pm].log`): FD 1.914932450456e-06 vs analytic 1.915989822176e-06
  = **0.055%**.
- **N6 prediction: HELD**, with two-to-four orders of margin. A volume-field DV
  type (not shape) on a conformal mesh is clean under scotch-vs-simple at np=4.

## N8 — sail (third snappy case): RESULT_PLACEHOLDER_N8

## N9 — which of the two confounded edits gates the defect off? (registered 2026-08-05 ~15:40Z, BEFORE the arm ran)

Supervisor-directed fold-in from the papers-protocol session
(`W4-a4-du0check/RESULTS.md`, commit c3061eaa): in the papers-protocol
configuration — farfield U BC `freestreamVelocity` -> `inletOutlet` AND a
`patchVelocity` input registered, the two edits forced together by
`DAInputPatchVelocity`'s FatalError branch — **the established A4 scotch shape
defect does not fire**: dCD/dshape 0.019% vs its own FD on the same mesh and
np=4 scotch partition that reads 8.95% in the established configuration. Exactly
two edits differ; that session named but could not afford the separating
control. This arm runs it: A4 coarse, np=4 scotch, **inletOutlet farfield, NO
patchVelocity input anywhere** (the only 0.orig difference vs the established
case is the U farfield BC block, verified by diff), original `runScript_w4.py`,
task `w4_totals` (analytic only — the established analytic values 2.2086e-01
(defect) vs 2.42e-01-class (no defect) are separated by 9%, far beyond every
FD/baseline shift in this campaign).

**Pre-registered prediction: the defect does NOT fire — analytic dCD/dshape
lands in the 2.40-2.43e-01 class, i.e. the `freestreamVelocity` farfield BC is
the gating edit, not the patchVelocity input registration.** Reasoning: the
defective object is the recorded reverse tape of `dRdW^T`
(`initializeGlobalADTape4dRdWT`: register STATE inputs ->
`updateStateBoundaryConditions` -> `calcResiduals`). Registering an extra
`inputInfo` input adds an independent leaf used by total-derivative seeding but
does not change the recorded state->residual computation that A^T reverses;
swapping the farfield BC type changes exactly that recorded computation
(`updateStateBoundaryConditions`), and `freestreamVelocity` is the switching
BC whose reverse sweep is the plausible parallel-inconsistency carrier. Named
alternative: if the analytic instead reads ~2.21e-01 (defect present), the BC
is innocent and the patchV INPUT REGISTRATION suppresses the defect — which
would point the mechanism at the tape's input-registration stage instead.

RESULT_PLACEHOLDER_N9

## What the pattern now supports about the trigger condition

1. **The defect is real and reaches beyond A4 at the operator level.** On a second
   snappy-refined geometry (Ahmed-35), the scotch-np=4 parallel reverse-AD
   operator provably differs from the serial operator (cross-residual 5.45x ||b||,
   state-controlled, interface-localized momentum rows) — same subsystem, same
   signature, different case.
2. **Its gradient-level cost is case- and contraction-dependent, from 0.00054% to
   8.95%.** A4-scotch pays 8.95%; a35-scotch pays only ~1.4%; conformal cases pay
   1e-04-level. The operator error is the invariant; the gradient damage is not.
3. **Conformal meshes stay clean under every decomposition tested** — A1, A2, A5
   (record) and now CBFS with a 21,000-component field DV (1.1e-04 invariance,
   FD-anchored at both decompositions).
4. **Refinement-interface cuts are anticorrelated with the defect** (48/68-cut
   slab arms clean, 0/4-cut scotch arms dirty; every large cross-residual entry
   on both cases sits on cellLevel-0 cells). The hanging-node-CUT hypothesis
   stays refuted; what snappy meshes contribute is evidently the irregular cut
   GEOMETRY scotch produces on them, not the refinement interfaces themselves.
5. **Rank count is not the trigger** (np=2 scotch clean at 0.26%, np=3 scotch
   dirty at 6.05%, np=4 slabs clean); **planar slabs of every orientation are
   benign-to-moderate on A4** (x 0.00054%, y 0.47%, z 0.52%), **mixed-orientation
   planar cuts with corners are intermediate** (1.40%), and **scotch's jagged
   cuts are the catastrophic family** (6.05%, 8.95%) — on A4. On a35 the scotch
   cut's gradient cost is mild even though its operator error is large.
6. **Practical rule the matrix supports:** a multi-rank DAFoam v5 gradient is
   trustworthy only with its own-run FD column at its own decomposition (that
   check catches the defect wherever it has gradient-level effect — A4-scotch
   failed it), or on a decomposition-invariance check when FD is unavailable;
   and on massively-separated cases (a35) the FD protocol itself can fail to
   resolve, leaving invariance as the only usable instrument.

## Scored predictions (strict)

| arm | prediction | score |
|---|---|---|
| N1 | A4 z-slabs in [0.05%, 1.5%] | **HELD** (0.52%) |
| N2 | A4 2x2x1 <= 1% | **NOT HELD** (1.40%); >2% decision rule not fired |
| N3 | a35 np=1 control <= 1.5% | **NOT HELD** (67.8% vs an FD the step sweep then showed unresolved) |
| N4 | a35 scotch: rel err >= 2% AND analytic shift >= 2% | **NOT HELD** (shift 1.36%; rel-err clause unscoreable, FD unresolved) |
| N5 | a35 simple <= 1% | **NOT HELD** (62.5% vs unresolved FD; shift 3.14%) |
| N6 | CBFS invariant (<=1% at FD cells, <=2% norm) | **HELD** (1.5e-05..1.6e-04) |
| N7 | a35 crossres >= 10x ||b||, interface momentum rows, np1 at floor | **magnitude NOT HELD** (5.45x, not 10x); localization + control clauses HELD |
| N8 | sail slab arm at graded scale (<=0.5% vs own FD, <=1% analytic shift) | SCORE_PLACEHOLDER_N8 |

Five of eight registered predictions missed in whole or in part, and the record
keeps them as written: the a35 miss cluster (N3/N4/N5) is the finding that the
case class breaks the FD instrument, and the N7 magnitude miss is a real 2x
overprediction of the operator residual's size on the new case.

## Cost ledger

All runs at `--cpus=2` (shared box), ledger = wall x 2, `W4-defect-reach/ledger.txt`:

| block | arms | core-min |
|---|---|---|
| A4 new orientations (N1, N2) | 2 | 9.70 |
| Ahmed-35 mesh + check_totals x3 + step sweep x2 | 6 | 24.14 |
| Ahmed-35 instrument (3 dumps + crossres + crossres2) | 5 | 14.53 |
| CBFS (compute_totals + 2 FD primals) | 3 | 29.10 |
| sail arm (N8) | 1 | LEDGER_PLACEHOLDER_N8 |
| **total** | | **TOTAL_PLACEHOLDER of 180 budgeted** |

Zero-solver-cost items: cut classification, maps, cross-residual corrections,
gradient comparisons (arithmetic on dumps); two container source-greps
(`DAInputField.C`, seconds, no solve). Killed-arm waste across both session
kills: **zero** (all arms detached and self-ledgered; both kills interrupted
polling only). The np=2/np=3/np=4 A4 record rows and the CBFS scotch arm were
reused from their records at zero new cost, as directed.

---

# RESULTS (2026-08-04 arms; assembled 2026-08-05 after a session kill — see the cost section)

## A4, the orientation axis completed (N1, N2)

Both new arms, patched IDWarp, np=4, `check_totals` (`a4_simple1x1x4.log`,
`a4_simple2x2x1.log`), beside the record rows:

| A4 arm | analytic | FD (own run) | rel. err | analytic shift vs np=1 (2.4150e-01) |
|---|---|---|---|---|
| simple 4x1x1 (record) | 2.4220e-01 | 2.4220e-01 | 0.00054% | +0.29% |
| simple 1x4x1 (record) | 2.4379e-01 | 2.4265e-01 | 0.47% | +0.95% |
| **simple 1x1x4 (N1)** | 2.4368e-01 | 2.4241e-01 | **0.52%** | +0.90% |
| **simple 2x2x1 (N2)** | 2.4605e-01 | 2.4265e-01 | **1.40%** | +1.88% |
| scotch np=3 (record) | 2.5641e-01 | 2.4178e-01 | 6.05% | +6.17% |
| scotch np=4 (record) | 2.2086e-01 | 2.4258e-01 | 8.95% | -8.55% |

- **N1 prediction HELD** (0.52% inside [0.05%, 1.5%]). Planar slabs of ALL three
  orientations are now measured: x 0.00054%, y 0.47%, z 0.52% — every one at least
  17x below scotch's 8.95%.
- **N2 prediction NOT HELD as registered** (1.40% > the registered <= 1%), but the
  registered decision rule did NOT fire (1.40% < 2%): two orthogonal planar cuts
  plus a 4-rank corner line land between the slab scale and far below scotch.
  "Scotch-style jaggedness required for the catastrophic regime" survives, weakened:
  corners/mixed orientation buy a factor ~3 over slabs, not the factor ~17 to scotch.
- Partition-cut classification (`analyze_cuts.py`, validated by reproducing the
  record's scotch=4 / simple411=68 cut-refinement-interface counts exactly):
  N1 cuts 624 faces (465 z-normal) of which 48 cross refinement interfaces; N2 cuts
  594 (447 y-normal, 127 x) with 48 on refinement interfaces; scotch np=3 cuts 248
  (4 on refinement), scotch np=4 cuts 328 (4 on refinement). **Refinement-interface
  cut count anticorrelates with error again** (68-cut arm cleanest, 4-cut arms
  worst), and no per-orientation face count predicts the error either (np=3's cut is
  160 x-normal + 74 z-normal + 8 oblique and reads 6.05%; N1's is 465 z-normal and
  reads 0.52%).

## Ahmed-35, the second snappy-refined case (N3, N4, N5) — and what its FD can and cannot say

The case built cleanly from A4's own recipe with only the STL swapped
(`stage_ahmed35.sh`; ahmed_35.stl bbox identical to ahmed_25.stl, roof-slant break
at x=0.8621 vs 0.8428 = the 35-degree shell; **2,777 cells — same count as A4 by
castellation coincidence, mesh points differ** — 502 cells at `cellLevel` 1, 456
refinement-interface faces). Baseline CD0 across the three decompositions:
1.6433363e-01 / 1.6433319e-01 / 1.6433161e-01 — **invariant to 1.2e-05 relative.**
All adjoints `PetscConvergedReason: 2`.

| Ahmed-35 arm | analytic (full precision from `w4_dump`) | FD h=1e-3 (own run) | rel. err vs own FD | analytic shift vs np=1 |
|---|---|---|---|---|
| np=1 (N3) | 2.991577132586644e-01 | 1.7826e-01 | 67.8% | — |
| np=4 scotch (N4) | 2.951007825593213e-01 | 1.7745e-01 | 66.3% | **-1.36%** |
| np=4 simple 4x1x1 (N5) | 2.897808022479100e-01 | 1.7838e-01 | 62.5% | **-3.13%** |

**The FD column on this case is NOT step-resolved, and the 62-68% figures are
therefore not gradient grades.** The np=1 FD step sweep (`a35_np1_h3e-3.log`,
`a35_np1_h1e-2.log`) reads 1.7826e-01 (h=1e-3), 1.9774e-01 (h=3e-3), 2.4702e-01
(h=1e-2) — monotone in h with no asymptotic band, where A4's own sweep had a
resolved Richardson-consistent band at these same steps. The case's converged CD
tail still drifts ~6e-4 relative (35-degree slant = the massively separated side of
the Ahmed drag crisis, on 2,777 cells at `primalMinResTol` 1e-4), which puts the
h=1e-3 central difference's noise floor at ~28% of the FD value. **Scores: N3 NOT
HELD, N4 NOT HELD as registered (the analytic-shift clause read 1.36%, under the
registered 2%), N5 NOT HELD as registered** — all three failing through the same
cause: this case cannot grade analytic-vs-FD at the established protocol, a
case-quality finding this record reports rather than papers over. What the case CAN
measure, cleanly, is decomposition-invariance of the analytic — CD0 invariant to
1.2e-05 while the analytic spans **3.1%** (np=1 high, scotch -1.36%, simple411
-3.13%) — 30-300x the conformal cases' invariance level, 3x under A4's span.
By the invariance gate this case is **NOT decomposition-invariant, reported as the
finding.**

## Ahmed-35 cross-residual (N7): the wrong-operator defect IS present on the second snappy case

Instrument: the discriminators session's own scripts, unmodified
(`runScript_w4.py` tasks `w4_dump`/`w4_crossres`/`w4_crossres2`; `build_maps_a35.py`
= `build_maps.py` with paths switched). Map validated exactly as before: duplicated
processor-face phi copies agree at **2.7e-15** (scotch) / **3.6e-15** (simple);
mapped primal states agree with np=1 at 8.5e-04 / 2.3e-03 (reconvergence noise).
Sign convention stated per the amended M1 caption: the `w4_crossres` instrument
computes `Atpsi - b` where the system is `A^T psi = -b`, so its own-operator log
lines print the degenerate `ratio=2.000000e+00`; the numbers below are the exact
offline correction `res + 2b` recomputed from the dumped vectors
(`a35_d_crossres/w4x_res_*.npy` + `w4x_b_np1.npy`, saved as `r_true_*.npy`), and
`w4_crossres2` (sign already correct in-task) reproduces them in-log.

True residual ||A^T psi + b|| under the **np=1 operator**, ||b|| = 1.787288e-01
(`a35_d_crossres.log`, sign-corrected; state-controlled values from
`a35_d_crossres2.log` in parentheses):

| psi from | ratio to \|\|b\|\| | state-controlled (linearized at scotch's own mapped state) | \|\|psi\|\| |
|---|---|---|---|
| np=1 control | **3.984e-04** | (1.92e-03) | 5.804e-02 |
| np=4 scotch | **5.446e+00** | (**5.446e+00**, unchanged to 6 digits) | 3.042e-02 |
| np=4 simple 4x1x1 | **3.308e-01** | (3.308e-01) | 2.440e-02 |

- **The scotch psi does not satisfy the serial adjoint system: 5.45x ||b||, 13,700x
  the np=1 floor**, unchanged to six digits when the serial operator is linearized
  at the scotch arm's own mapped state (the state confound contributes at 1e-03,
  same as on A4). The wrong-parallel-operator defect is therefore **reproduced on a
  second, independently meshed snappy case.** N7's registered >= 10x clause is
  **NOT HELD** (5.45x measured — same order, below the named threshold); the
  localization and control clauses **HELD**.
- **Localization, same signature, different components:** 13 of the top 15 |r|
  entries sit on scotch partition-interface cells, ALL at `cellLevel` 0, and the
  three dominant entries (|r| = 0.794, 0.397, 0.397 — 82% of the norm) each touch
  exactly ONE foreign rank through exactly ONE processor face. On A4 the error
  lived in x-momentum rows on y-normal processor faces; here it lives in
  **z-momentum (U2) rows on x-normal processor faces** — in both cases the affected
  momentum component is TANGENTIAL to the offending processor face (n=2
  observation, recorded for the upstream report, not overclaimed).
- The simple411 psi reads 0.331 of ||b|| (830x the floor, 16x under scotch), 8 of
  its top 10 entries on its own interface cells — same continuum the mechanism
  sweep noted on A4 (every np=4 operator differs measurably from serial; the cut
  decides the magnitude).
- **Gradient damage does not track operator-residual size.** A4: 329x ||b|| ->
  8.95% gradient error. Ahmed-35: 5.4x -> 1.36% analytic shift, while simple411 at
  0.33x shifts 3.13% — and on A4, simple411 at 0.094x shifted 0.00054%. What
  reaches dCD/dshape is the contraction of the operator error with this
  case-and-objective's adjoint direction, so **a clean gradient under one
  decomposition certifies nothing about the operator** (it did not on A4 either:
  that is L-35's point, now measured across cases). Also unlike A4 (psi inflated
  16.5x under scotch), the a35 psi norm DEFLATES under both np=4 arms — the
  defect's expression in ||psi|| is case-dependent too.

## CBFS (N6): conformal mesh + field DVs, decomposition-invariant — prediction HELD with orders to spare

New arm `cbfs_simple411` (np=4 simple 4x1x1, `dafoam-subpclu:v1` +
`DAFOAM_SUBPC_TYPE=lu` exactly as the record arm; sub-PC only, cannot move a
right-preconditioned GMRES solution converged in the unpreconditioned norm; KSP
reason 2 at 766 iters vs the record's 667). Gradients mapped to serial cell
ordering via each arm's `cellProcAddressing` — the exact convention was first
confirmed in the shipped container source (`DAInputField.C`: non-distributed field
inputs index by `globalIndex` = rank-offset concatenation of local cells), and both
maps verified as exact permutations. Objective converged value:
1.5279278602e-02 vs the record's 1.5279278906e-02 — **invariant to 2.0e-08.**

| quantity | scotch (record) vs simple411 (new) |
|---|---|
| gradient vector norm | 1.455805e-05 vs 1.455849e-05 (**1.13e-04 relative diff**) |
| record FD cell 5491 -> serial 471 | 1.916018813330e-06 vs 1.915989822176e-06 (**1.5e-05**) |
| record FD cell 6740 -> serial 3280 | 1.678653382471e-06 vs 1.678799692163e-06 (8.7e-05) |
| record FD cell 12486 -> serial 3702 | 1.469472928907e-06 vs 1.469590238668e-06 (8.0e-05) |
| top-20 \|g\| cells | max rel diff 1.58e-04, median 4.0e-05 |

FD columns at BOTH decompositions (gate requirement): scotch on record (0.085% /
0.059% / 0.199%, `W4_ADJOINT_PC_UNBLOCK.md`); this session added the simple-arm
central difference at the strongest record cell — the perturbation built at the
SIMPLE arm's own global index for serial cell 471 (index 5371, decomposition
orderings differ) — giving FD 1.914932450456e-06 vs analytic 1.915989822176e-06 =
**0.055%** (`cbfs_fd_s471_p.log`/`_m.log`). **N6 HELD**: a conformal-mesh case with
a 21,000-component volume-field DV (a different DV type from every prior arm) is
decomposition-invariant 2-4 orders below the registered thresholds.

## Sail (N8): RESULT_PLACEHOLDER

## Scored predictions, all eight

| arm | registered prediction | outcome |
|---|---|---|
| N1 | A4 z-slabs rel. err in [0.05%, 1.5%] | **HELD** (0.52%) |
| N2 | A4 2x2x1 <= 1%; decision rule at > 2% | **NOT HELD** (1.40%); decision rule not fired — jaggedness-required survives, weakened |
| N3 | Ahmed-35 np=1 control <= 1.5% | **NOT HELD** (67.8% — traced to an unresolved FD, not to the adjoint; see its section) |
| N4 | defect appears: rel. err >= 2% AND analytic shift >= 2% | **NOT HELD as registered** (analytic shift 1.36% < 2%; the rel.-err clause is unmeasurable against an unresolved FD) |
| N5 | Ahmed-35 simple411 <= 1% | **NOT HELD** (same unresolved-FD cause; analytic shift -3.13%) |
| N6 | CBFS decomposition-invariant (<= 1% cells, <= 2% norm) | **HELD** (1.5e-05-1.6e-04; norm 1.1e-04) |
| N7 | cross-residual >= 10x \|\|b\|\|; interface-momentum localization; np=1 floor control | threshold clause **NOT HELD** (5.45x — same order, under the named 10x); localization and control clauses **HELD** |
| N8 | sail decomposition-invariant (<= 0.5% vs own FD; <= 1% analytic shift) | N8_SCORE_PLACEHOLDER |

## What the pattern now supports about the trigger condition

1. **The wrong-parallel-operator defect is not a property of one mesh.** It is now
   measured, by the same instrument with the same validation standard, on two
   independently meshed snappyHexMesh cases: scotch-np=4 psi leaves 329x ||b|| (A4)
   and 5.45x ||b|| (Ahmed-35) under the serial operator, both state-controlled to
   six digits, both localized to single-foreign-face partition-interface cells at
   `cellLevel` 0.
2. **Refinement interfaces are exonerated as the trigger, now on three independent
   measurements**: cut-count anticorrelation (68-cut planar arm cleanest on A4, its
   48-cut z- and corner-arms at 0.5-1.4%), `cellLevel` 0 localization on A4, and
   `cellLevel` 0 localization again on Ahmed-35. What refinement plausibly does is
   set up the cell-size/shape context scotch's partitioner then cuts through; the
   hanging nodes themselves are not where the residual lives. The docket's named
   conformal-vs-refined pair on the same geometry was NOT run (reported as
   untested in that form) — it is superseded by the localization evidence, which
   tests the hypothesis on the defect's own cells rather than by case pairing.
3. **Rank count is not the trigger; planar cuts of any orientation are benign to
   moderate; scotch's cut geometry is the catastrophic excitation on A4.** The full
   A4 axis now reads: np=2 scotch 0.26%, np=3 scotch 6.05%, np=4 scotch 8.95%,
   np=4 planar slabs 0.00054-0.52% (x/y/z), np=4 2x2x1 corners 1.40%.
4. **Gradient-level severity decouples from operator-level severity** — the single
   most consequential fact for anyone relying on `check_totals`: A4 scotch
   329x -> 8.95% gradient error; a35 scotch 5.45x -> 1.36%; a35 simple411
   0.33x -> 3.13%; A4 simple411 0.094x -> 0.00054%. The damage is the contraction
   of the operator error with the case-and-objective's own adjoint direction. **A
   clean check_totals under one decomposition is not evidence of a clean operator,
   and decomposition-invariance testing (this campaign's other docket item) is
   exactly the cheap instrument that sees what check_totals cannot.** Recorded as
   **LESSONS L-36** (already on file citing this campaign's numbers; no duplicate
   entry added by this session).
5. **The clean side is broad**: conformal meshes are decomposition-invariant at the
   1e-04 level across four cases (A1, A2, A5, and now CBFS — the latter with a
   21,000-component field DV, a different DV type), SAIL_CLAUSE_PLACEHOLDER
6. **A cross-case structural hint for the mechanism** (n=2, not overclaimed): the
   dominant cross-residual rows are the momentum component TANGENTIAL to the
   offending processor face (A4: x-momentum on y-normal faces; a35: z-momentum on
   x-normal faces) — consistent with the reverse-AD halo-exchange candidate surface
   the mechanism record names, and a concrete thing an instrumented rebuild should
   look at first.

Separate case-quality finding, recorded: **the Ahmed-35 coarse case cannot grade
gradients by the established FD protocol at all** (steady kOmegaSST on 2,777 cells
in the massively separated 35-degree regime: FD monotone in h with no asymptotic
band, CD tail drift ~6e-4). Any future gradient work on this geometry needs a finer
mesh or a tighter primal before FD means anything.

## Cost ledger (wall x cpus-cap, per `W4-defect-reach/ledger.txt`)

| arm | task | wall | core-min |
|---|---|---|---|
| a35_mesh | meshgen | 2 s | 0.07 |
| a35_np1 (N3) | check_totals | 88 s | 2.93 |
| a4_simple1x1x4 (N1) | check_totals | 143 s | 4.77 |
| a4_simple2x2x1 (N2) | check_totals | 148 s | 4.93 |
| a35_np4scotch (N4) | check_totals | 143 s | 4.77 |
| a35_np4simple411 (N5) | check_totals | 145 s | 4.83 |
| a35_np1_h3e-3 | check_totals (FD step) | 173 s | 5.77 |
| a35_np1_h1e-2 | check_totals (FD step) | 173 s | 5.77 |
| cbfs_simple411 (N6) | compute_totals | 600 s | 20.00 |
| a35_d_np1 (N7) | w4_dump | 103 s | 3.43 |
| a35_d_np4simple (N7) | w4_dump | 148 s | 4.93 |
| a35_d_np4scotch (N7) | w4_dump | 155 s | 5.17 |
| a35_d_crossres (N7) | w4_crossres | 22 s | 0.73 |
| a35_d_crossres2 (N7) | w4_crossres2 | 8 s | 0.27 |
| cbfs_fd_s471_p (N6) | run_model FD | 136 s | 4.53 |
| cbfs_fd_s471_m (N6) | run_model FD | 137 s | 4.57 |
| sail_simple311 (N8) | check_totals | SAIL_WALL | SAIL_CM |
| **total** | | | **TOTAL_CM of 180 budgeted (120 + 60)** |

Accounting notes, stated rather than hidden: (1) the 2026-08-04 session was killed
by a session limit at ~18:53Z mid-campaign — **no solver core-minutes were lost**:
all twelve arms then in flight or queued ran to completion under their detached
drivers (rc=0, ledger lines self-written 18:44-18:56Z), and the overnight box
power-off found nothing running; the 2026-08-05 resume added only the offline
analysis, the two crossres container runs, the CBFS FD pair, and N8. (2) Four
static source-lookup container invocations (DAInputField.C convention, mphys file
locations) ran outside the ledger at zero solver cost, ~30 s wall total, <= 1
core-min even charged at full cap. (3) The A4 np=2/np=3 rows and the entire scotch
side of CBFS and the sail were REUSED from the record, not rerun — that reuse is
what a 17-arm matrix under 180 core-min is made of.

## Docket gates, clause by clause

**`w4-does-the-decomposition-defect-reach-other-cases`** — gate: *"Each case tested
is either decomposition-invariant or is not, with its own analytic and FD columns
cited at both decompositions; and the hanging-node hypothesis is either supported
by a conformal-versus-refined pair on the same geometry or reported as untested."*

- A4: NOT invariant (record + this session's two new arms, every row with its own
  in-run FD).
- Ahmed-35: NOT invariant (3.1% analytic span; analytic and FD cited at all three
  decompositions, with the FD honestly reported unresolved — and the
  wrong-operator conviction supplied by the cross-residual instrument instead).
- CBFS: invariant (analytic at both decompositions; FD at both decompositions:
  0.085% record / 0.055% this session).
- Sail: SAIL_GATE_PLACEHOLDER
- Hanging-node hypothesis: the same-geometry conformal-vs-refined pair was NOT run
  — reported as untested in that form, and the hypothesis is refuted on stronger,
  direct evidence (localization at `cellLevel` 0 on both defective cases;
  cut-count anticorrelation on every arm).

**`w4-decomposition-invariance-is-a-gate`** — gate: *"Every graded gradient
reproduces under a second decomposition, or the disagreement is reported as the
finding."* Survey of every graded/published DAFoam gradient in the lab: A1 —
invariant (record); A2 — invariant (record); A4 — NOT, reported, it IS the finding
(record); A5 — invariant (record); CBFS beta — invariant (this session); NACA0015
sail coarse — SAIL_GATE2_PLACEHOLDER; naca4412 and sail_medium/sail_full — **no
graded gradient exists to check** (adjoints blocked/incomplete per
`DAFOAM_CASE_STATUS.md`), so there is nothing this gate applies to. One boundary
case noted honestly: the NASA-hump beta-field gradient from the pc-unblock session
(FD-verified at 3 cells under its single decomposition) has not been re-run under a
second decomposition; its mesh is conformal and CBFS — same DV type, same solver
path — is now measured invariant, but that is an expectation, not a measurement,
and it is recorded here as the one unchecked entry.
