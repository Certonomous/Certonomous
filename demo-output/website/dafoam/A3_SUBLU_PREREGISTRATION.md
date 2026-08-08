# A3 ONERA M6 vcoarse adjoint — sub-LU + transonicPCOption arm: PRE-REGISTRATION

Filed 2026-08-08T02:30Z by the DAFoam solver agent executing the approved diagnostic of
`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` entry 8 (docket item
`a3-m6-vcoarse-adjoint-sub-lu-arm`, approved, ~30 core-min). Committed BEFORE any solver
compute is launched; the result record (`A3_SUBLU_RESULT.md`) will cite this file's commit hash.

## 1. The exact case and mesh

The archived vcoarse rung of the A3 ladder, in place:
`/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/` — **24,960 cells** (polyMesh owner
note `nPoints:26520 nCells:24960 nFaces:76358`), the 4x-`cgns_utils coarsen` pass of
`m6_surfaceMesh_fine.cgns` extruded by `genWingMesh.py`/pyHyp, exactly as `preProcessing.sh` in
that directory built it on 2026-07-28. Flow condition as archived (M=0.84, alpha=3.06,
U0=291.6, T0=300K — the A3 ladder's AGARD 2308 matching, documented in the runScript header).
Solver `DARhoSimpleCFoam`, 4 MPI ranks, `primalMinResTol=1e-6`, adjoint options as archived:
`gmresRelTol 1e-4, pcFillLevel 0, jacMatReOrdering natural, gmresRestart 200, adjPCLag 5,
adjStateOrdering cell`. Objectives needing adjoint solves: CD (objective) and CL (constraint) —
two KSP solves per `compute_totals`.

### 1a. Reconstruction step, pre-registered (the arm's first act, diagnosed before this filing)

The archived vcoarse arm never reached its adjoint — and the record's "SEGV / corrupted-field
read during decomposePar, not diagnosed further" (A3_onera_m6.md attempts 7,8) is now diagnosed
from the archived `check_totals_run1.log` itself: `decomposePar` failed CLEANLY with
`Cannot find patchField entry for auto4` (`0/T/boundaryField` line 26), and the wrapper then
launched the solver anyway against half-written `processor*` dirs; the SEGV cascade was
downstream noise, not field corruption (`0/` is byte-identical to `0.orig`; all polyMesh .gz
pass `gzip -t`).

Root cause: `autoPatch 60` on the 4x-coarsened mesh split the wing surface into more auto
patches than the tutorial's `createPatchDict` (written for the 2x mesh's auto0–auto3) maps.
Two orphans remain in `constant/polyMesh/boundary`: `auto4` (176 faces) and `auto5` (11 faces).
Geometric identification (face centroids/normals computed from points.gz/faces.gz before this
filing): `auto4` = wing LOWER surface (bbox x[0.042,1.139] y[−0.038,−0.001] z[0.042,1.198],
mean |n| ≈ (0.11, 0.99, 0.06)); `auto5` = blunt trailing-edge base (bbox x[0.819,1.140],
y ≈ 0 — the symmetric M6 section's TE — mean |n| ≈ (0.96, 0, 0.27)). Both are wing wall faces.

Pre-registered repair, the minimal reconstruction and nothing else: `createPatch -overwrite`
merging `wing + auto4 + auto5` into patch `wing` (type wall), giving a 3-patch boundary
(wing 390 faces, inout 390, sym 2176) that the archived `0.orig` boundaryFields (`"wing.*"`,
`inout`, `sym`) already cover. Stale half-written `processor*` dirs are moved aside to
`_stale_processor_dirs_run1/` (preserved, not deleted). This is bookkeeping repair of the
archived case to what its own pipeline intended — not a different case.

## 2. The levers and their provenance

1. **`DAFOAM_SUBPC_TYPE=lu`** — the ASM sub-block complete-LU switch, run on the patched image
   `dafoam-subpclu:v1` (image present, verified). Provenance: the lab's own env-gated rebuild at
   the hard-coded `PCILU` (`DALinearEqn.C:277–285` in the image's source tree;
   `subpclu_patch/DALinearEqn_subpclu.patch`; `ladder-b/W4_ADJOINT_PC_UNBLOCK.md`; verification
   sweep commit 9c19ccc8). Guard, per `FAMILY_SUPERVISION_GUIDELINES.md`: the run log MUST show
   `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` before any sub-LU claim is made.
2. **`transonicPCOption: 1`** — the liaison's lead 1.5
   (`LIAISON_RESEARCH_adjoint_conditioning.md`): the official DAFoam transonic NACA0012 tutorial
   sets `"transonicPCOption": 1` (verified in the local tutorials clone,
   `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/transonic/runScript.py` line 73). Semantics
   from the image's source, `DAResidualRhoSimpleCFoam.C:172–176`: when assembling the PC matrix
   only, drop the `fvm::div(phid, p)` term from the pressure equation — deliberate PC
   simplification toward diagonal dominance.
   **Disclosed sharpening of the lead, found during this filing:** the archived M6 scripts (fine,
   coarse, vcoarse, A6, and every D3 sweep variant) all set `"transonicPCOption": 2` — which is a
   **silent no-op for `DARhoSimpleCFoam`**: the only live branch in
   `DAResidualRhoSimpleCFoam.C` is `== 1` (line 173); a `== 2` branch exists only in
   `DAResidualTurboFoam.C:176` (a different solver). So the liaison's "apparently never set
   here" is right in effect: the transonic PC simplification has never been ACTIVE on any of
   our M6 runs. The lever here is 2→1, i.e. inactive→active.

The run script is `runScript_sublu_tpc1.py`, a copy of the archived `runScript.py` with exactly
one functional change: `"transonicPCOption": 2` → `"transonicPCOption": 1` (plus a header note).
Task: `compute_totals` (primal + one adjoint solve per response). The sub-LU lever enters via
the environment, zero script change, exactly as in the CBFS record arm.

## 3. One combined arm, not two — and why

The discipline allowed sub-LU-only first if separating the levers were cheap. It is not: each
arm re-runs the primal (1000 SIMPLE steps), the Jacobian coloring, and PC assembly — the
dominant costs. The nearest archived family anchor (21,840-cell sweep arm: 420 s wall x 4 ranks
= 28 core-min) is already the entire 30 core-min budget for a SINGLE arm at this size. The
approved diagnostic as filed (entry 8, and the docket gate: "with the sub-preconditioner set to
LU and the transonic preconditioner option set as the official transonic tutorial sets it") is
the combined arm; the combined arm is what runs.

## 4. What "converged adjoint" means (the family's standing KSP criteria)

From the raw solver log, NOT the wrapper's `Residual tolerance satisfied` line (the recorded
false-success pattern: `PetscConvergedReason: -5` with a denormal residual still prints that
line — caught twice in this family, `ADJOINT_MEMORY_ENVELOPE.md` Options 2 and 4):

- **CONVERGED** = `PetscConvergedReason` POSITIVE (2, `KSP_CONVERGED_RTOL`, is the family's
  recorded success code) on **BOTH** adjoint solves (CD and CL), grep'd from the full log.
- **FAILED** = any negative reason code on either solve (−5 DIVERGED_BREAKDOWN is this family's
  standing signature; −9, −3, or any other negative code also counts as failed), or OOM/crash
  before a reason code is printed.
- The sub-LU banner (lever 1 guard) and a `transonicPCOption` = 1 echo in the case's runtime
  options must both be verified in/for the run before either verdict is claimed.

Branch pre-registered for a primal that fails its own gate (this exact 24,960-cell mesh has
never completed a primal; nearest family points: 21,840 cells passed the gate, 10,920 did not):
if the primal fails DAFoam's own tolerance gate and the adjoint is never attempted, the arm is
**NOT EVALUABLE at this rung** — neither outcome below fires, the result records the primal
residuals, and the docket entry closes as not-evaluable-at-vcoarse rather than as either verdict.

## 5. The two outcome meanings, from entry 8 verbatim

> If it converges, A3's ladder reopens and the DIVERGED_BREAKDOWN story gets its epilogue; if
> not, the conditioning wall is confirmed beyond the incompressible family.

- **Converges** (per §4) → A3's ladder reopens and the DIVERGED_BREAKDOWN story gets its
  epilogue.
- **Fails** (per §4) → the conditioning wall is confirmed beyond the incompressible family.

## 6. Run mechanics and budget

- Image `dafoam-subpclu:v1`, `--cpus=4 --memory=10g` (predicted ~6.5 GB from the family's
  memory law 1.2125 x cells^0.8485 at 24,960 cells; proposal predicted 6.0), 4 ranks,
  `mpirun --allow-run-as-root -np 4 python runScript_sublu_tpc1.py -task compute_totals`,
  `source /home/dafoamuser/dafoam/loadDAFoam.sh` — the canonical family invocation
  (`W4-adjoint-pc-unblock/run_cbfs_sublu.sh`).
- Launched setsid-detached with the self-ledger convention: `.t0` (epoch at start), `.rc`
  (exit code), `.t1` (epoch at end) written inside the case dir; the log is
  `sublu_tpc1_computetotals.log`. Polled inline; no monitors, no background waiters.
- Budget: 30 core-min approved. Measured spend = wall x 4 ranks, reported against the 30.
- Pre-launch checks (done at filing time, re-checked at launch): no A3/M6 process or container
  running (`pgrep`, `docker ps` — only the unrelated `s1wa_anchorw` S1 container is up).

Result record: `demo-output/website/dafoam/A3_SUBLU_RESULT.md`; docket entry
`a3-m6-vcoarse-adjoint-sub-lu-arm` closed with the outcome inline, own-entry edit only.
