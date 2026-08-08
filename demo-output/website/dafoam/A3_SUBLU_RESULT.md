# A3 ONERA M6 vcoarse sub-LU + transonicPCOption arm — RESULT

Filed 2026-08-08 by the DAFoam solver agent. Pre-registration:
`A3_SUBLU_PREREGISTRATION.md`, commit `12d3a7a3f772615060d30dc59cc2c9b671780252`, committed
2026-08-08T02:29:17Z — BEFORE launch (t0 = 02:30:51Z, ordering below). Docket item:
`a3-m6-vcoarse-adjoint-sub-lu-arm` (entry 8 of `SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md`).

## Verdict up front

**NOT EVALUABLE AT THE VCOARSE RUNG — the pre-registered §4 branch fires; NEITHER entry-8
outcome is claimed.** The adjoint was never reached, the primal was never reached: DAFoam's own
mesh-quality gate rejected the archived vcoarse mesh, and the defect is congenital to the mesh
as generated on 2026-07-28 (proof below), not introduced by this arm's reconstruction. The
conditioning wall is NOT hereby confirmed, and the ladder is NOT reopened — the vcoarse rung of
the A3 ladder, as archived, has never been a runnable case. Per the arm's binding discipline
("stop and report what exists instead of improvising a different case"), no substitute mesh was
run.

## Launch evidence and spend

- Pre-reg commit `12d3a7a3` at 02:29:17Z; launch t0 = **1786156251** (02:30:51Z), setsid-detached
  `run_arm.sh` with the `.t0/.rc/.t1` self-ledger, container `a3_sublu_tpc1` on
  `dafoam-subpclu:v1`, `--cpus=4 --memory=10g`, `-e DAFOAM_SUBPC_TYPE=lu`, 4 ranks,
  `runScript_sublu_tpc1.py -task compute_totals` (the archived runScript with exactly one
  functional change, `transonicPCOption: 2 -> 1`).
- Ledger: `.rc = 1`, `.t1 = 1786156259` — **wall 8 s = 0.53 core-min of the 30 approved**
  (plus ~1 core-min of containerized reconstruction/verification: createPatch + decomposePar +
  standalone checkMesh). Pre-launch check: only the unrelated `s1wa_anchorw` S1 container
  running; nothing A3/M6.
- Log: `sublu_tpc1_computetotals.log` in the case dir
  `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/`.

## What the arm did accomplish: the archived "SEGV / corrupted-field-read" is diagnosed and repaired

`A3_onera_m6.md` attempts 7,8 recorded the vcoarse rung as a "new, unrelated, twice-reproduced
crash: SEGV / corrupted field read during `decomposePar` ... not diagnosed further." Diagnosis,
from the archived `check_totals_run1.log` itself plus this arm's reconstruction:

1. `autoPatch 60` on the 4x-coarsened mesh split the wing into more pieces than the tutorial
   `createPatchDict` (written for the 2x mesh's auto0–auto3) maps, leaving orphan patches
   `auto4` (176 faces — wing lower surface) and `auto5` (11 faces — blunt TE base), identified
   geometrically before the pre-reg was filed (prereg §1a).
2. `decomposePar` therefore failed CLEANLY (`Cannot find patchField entry for auto4`,
   `0/T/boundaryField`); the old wrapper launched the solver anyway against half-written
   `processor*` dirs — the SEGV was downstream noise. No field corruption existed
   (`0/` byte-identical to `0.orig`).
3. The pre-registered repair (createPatch merge of auto4+auto5 into `wing`, 390 wall faces;
   `system/createPatchDict.mergeOrphans`; `reconstruct_run1.log`) WORKED: decomposePar
   completed, all four ranks read their fields, `designSurfaces` resolved to the merged wing.
   The run got strictly past the July-28 failure point.

## The blocking finding: the archived vcoarse mesh is geometrically degenerate

DAFoam's mesh-quality gate aborted at `Checking mesh quality for time = 0` — **"Failed 5 mesh
checks"**, `AnalysisError: Mesh quality error!` on all ranks, rc=1 in 8 s:

```
***High aspect ratio cells found, Max aspect ratio: 2.077411150536182e+95, number of cells 25
***Zero or negative cell volume detected.  Minimum negative volume: -3.302747834736008e-09,
   Number of negative volume cells: 23
   Mesh non-orthogonality Max: 135.3184267607995 average: 15.89161144264677
***Number of non-orthogonality errors: 43.
***Error in face pyramids: 144 faces are incorrectly oriented.
***Max skewness = 55.37803803699632
```

Adversarial verification, per the standing doctrine (assume wrong until defended):

- **Independent instrument:** standalone `checkMesh -constant` (stock OpenFOAM utility, no
  DAFoam wrapper) reproduces every figure on the serial mesh — 25 high-aspect cells at
  2.0774e+95, 23 negative-volume cells at min −3.3027e−09, max non-orth 135.32, 144 wrong
  face pyramids, max skewness 55.38, "Failed 5 mesh checks".
- **Not introduced by the repair:** the stale July-28 processor dirs (preserved at
  `_stale_processor_dirs_run1/`, decomposed from the PRE-repair geometry before the old run
  died) carry the identical defect — offline divergence-theorem cell volumes computed from
  their raw polyMesh give **23 negative cells, min −3.302748e−09 (processor1), bit-identical
  to the current serial mesh**. `createPatch` relabelled boundary faces; the geometry was
  born broken.
- **Located:** all 23 negative-volume cells sit in one clump at the wing TIP trailing-edge
  corner (centroids x∈[1.1318,1.1449], y≈0, z∈[1.1934,1.1976]) — the pyHyp extrusion collapsed
  at the tip on the 4x-`cgns_utils coarsen` surface. Generator-owned pathology, the same tool
  family as the standing finding `GENERATOR_FINDING_pyhyp_aspect_ratio.md` (there: max aspect
  ratio worsens under REFINEMENT on NACA0012; here: outright cell inversion under extreme
  COARSENING on M6). The D3 sweep meshes (3x-coarsened surface, 21,840–79,560 cells) show the
  family's milder signature (max non-orth 61.5, no negative volumes) and DID pass the gate.

## KSP convergence history

None exists — no adjoint (and no primal) iteration was ever run. There is no KSP tail to
report; the log tail is the mesh-gate abort quoted above. Consequently the two levers were
never exercised: the sub-LU banner is absent because `DALinearEqn` was never reached (the env
WAS set — launch line in `run_arm.sh`), and `transonicPCOption: 1` sat un-echoed in the options
dict. **No claim about either lever's effect on the M6 conditioning wall can be made from this
arm.**

## Outcome per the pre-registered mapping

- Entry 8 verbatim: "If it converges, A3's ladder reopens and the DIVERGED_BREAKDOWN story gets
  its epilogue; if not, the conditioning wall is confirmed beyond the incompressible family."
- **Fired branch: prereg §4 not-evaluable** — the adjoint was never attempted, so neither
  outcome above fires. The docket entry closes as not-evaluable-at-vcoarse, with the standing
  question — does sub-LU + an ACTIVE transonic PC move the M6 `-5` wall? — still open and
  still worth its 30 core-min.

## What exists for a re-file (reported, not run — the chief's call, not this agent's)

1. `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/` — 21,840 cells, the cheapest
   archived M6 case that actually matches the proposal's own cost-basis sentence ("has run
   before and failed by breakdown rather than by walltime"): primal passes the gate, adjoint
   `-5` on record, mesh passes checkMesh's fatal checks. The two levers would carry over
   unchanged (env + one-line script edit).
2. Alternatively, regenerate a true vcoarse rung from a 3x-coarsened surface with more pyHyp
   layers, since 4x surface coarsening is now measured to break the generator.
3. The transonicPCOption no-op finding (prereg §2: every archived M6/A6 script's
   `"transonicPCOption": 2` is dead code for `DARhoSimpleCFoam` — only `== 1` exists in
   `DAResidualRhoSimpleCFoam.C:173`; `== 2` lives only in `DAResidualTurboFoam.C:176`) stands
   REGARDLESS of this arm's mesh outcome and retroactively annotates every archived M6 `-5`:
   none of them had an active transonic PC. It sharpens, and slightly cheapens, any re-file.

## Files

Case dir `/home/ubuntu/certonomous-runs/A3-onera-m6-adjoint-vcoarse/`: `run_arm.sh`,
`runScript_sublu_tpc1.py`, `system/createPatchDict.mergeOrphans`, `reconstruct_run1.log`,
`sublu_tpc1_computetotals.log`, ledger `.t0/.rc/.t1`, `_stale_processor_dirs_run1/` (preserved
pre-repair decomposition), archived `check_totals_run{1,2}.log` (untouched). Repo:
`A3_SUBLU_PREREGISTRATION.md` (12d3a7a3), this file.
