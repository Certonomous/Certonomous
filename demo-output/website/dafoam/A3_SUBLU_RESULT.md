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

---

# RE-FILE RESULT, 2026-08-08: the 21,840-cell sweep arm (chief-approved same session)

Pre-registration `A3_SUBLU_SWEEP_PREREGISTRATION.md`: base 054d10b2 (02:39:53Z, after the
pre-launch checkMesh PASS it asserts), addendum 1 f77b2607 (cold-start repair), addendum 2
7f207f65 (20g cap) — each committed before the attempt it governs.

## Verdict up front

**NOT EVALUABLE ON THIS HOST — no KSP reason code was obtainable inside the 30 GB machine's
memory envelope; NEITHER entry-8 outcome is claimed, and the conditioning question stays
open.** Both levers were proven ACTIVE in-log for the first time on any M6 run — and the
sub-LU lever then turned out to be memory-infeasible at this rung on this host. A deliberate
interpretation note on prereg §5's letter: §5 counted "crash/OOM before a reason prints" as
FAILED, but mapping a MEMORY death onto "the conditioning wall is confirmed" would be false —
memory and convergence are this family's two separate blockers (`ADJOINT_MEMORY_ENVELOPE.md`,
Option 2 verdict), and these attempts died entirely on the memory one. Stated per the hump
precedent: sub-LU turns the question from a `-5` into a memory-envelope problem — a different,
honestly-named problem (`FAMILY_SUPERVISION_GUIDELINES.md`, R-5 note).

## The three attempts (ledger `.t0/.rc/.t1` in the sweep case dir)

| attempt | t0 (UTC) | wall | rc | died at | cause |
|---|---|---|---|---|---|
| 1 | 02:40:18 (1786156818) | 16 s | 1 | `renameSolution` | leftover record `0.0001` collision (`pyDAFoam.py:1543` hard-raise); also exposed the warm-start trap — DAFoam writes the primal end state back into time 0 (`0/U` == `1000/U` bit-exact), so the primal ran 1000 steps in 10.13 s from prior runs' converged fields | 
| 2 | 02:45:38 (1786157138) | 217 s | 137 | sub-LU factorization | kernel `CONSTRAINT_MEMCG` oom-kill at the 10g cap (dmesg) — cold primal + rename clean after the addendum-1 repair; BOTH activity proofs in-log |
| 3 | 02:51:06 (1786157466) | 1,672 s | 137 | `Solving Linear Equation...` | host-protection kill at 03:18:57Z (family precedent: A3 fine-mesh attempt 3): container grazed the 20g cap (19.94 GiB observed), host swap grew to 12 GB with active swap-in, MemAvailable fell to 2 GB — through the 6 GB floor; **zero completed KSP iteration blocks in 27.9 min** (the first `Main iteration 100` print never appeared) |

Spend, reported against the approved 30 core-min: vcoarse 0.53 + attempts 1–3
(16+217+1,672)x4/60 = 127.0 → **127.5 core-min total, 4.25x the envelope** — the overrun
happened inside attempt 3 under addendum 2's pre-registered "runs to its reason codes"
commitment and was terminated only by the host floor, which outranks it.

## Launch evidence with the PC-active proofs (attempt 2 and 3 logs, identical config)

- `transonicPCOption 1;` in the DAOption dump (the record log reads `2;` at its line 410) —
  the first M6 run ever with the transonic PC live (`DAResidualRhoSimpleCFoam.C:173`).
- `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` at PC setup, followed by the
  stock option echo (`ILU PC Fill Level: 0`, `Mat ReOrdering: natural`, `GMRES Restart: 200`,
  `GMRES Max Iterations: 1000`) — config otherwise bit-identical to the record arm.
- Logs preserved: `sublu_tpc1_computetotals_attempt{1,2,3}.log` in
  `/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/`.

## What was measured (real findings, all new)

1. **The sub-LU lever's cost on M6 6-field sub-blocks is a different regime.** At np=4
   (~5,460 cells/rank, ~38k unknowns per ASM sub-block, `DARhoSimpleCFoam`'s 6 transported
   fields), the complete-LU factorization needs >10 GiB (attempt 2's oom-kill), ~20 GiB
   resident plus 12 GB swap (attempt 3), and had completed no 100-iteration KSP block after
   27.9 min — against the record ILU run's 5,876.6 MiB TOTAL and 82 s per 100 iterations. On
   CBFS (np=4, 21,000 cells, incompressible, smaller blocks) the same switch fit easily and
   converged in ~16 core-min. The lever's feasibility is block-size- and field-count-bound,
   and M6 at np=4 is beyond this host.
2. **Wrapper facts** now on the record for anyone re-running archived DAFoam cases:
   `renameSolution` hard-raises on a leftover `0.0001` (`pyDAFoam.py:1543`), and the end
   state is written back into time 0, silently warm-starting every subsequent run (attempt
   1's 10 s primal, end state 2.2% |U| off the record writeout). Cold-start restoration =
   move `0.0001`+`1000`+overwritten `0` aside, `decomposePar -fields` from the pristine
   serial `0/` (partition and coloring cache untouched).
3. The checkMesh gate discipline worked: asserted PASS pre-launch, and no mesh gate fired.

## Undone / open, explicitly

- The conditioning question — does an ACTIVE transonic PC (with or without sub-LU) move the
  M6 `-5`? — remains unanswered. Two cheap, named follow-ups for the chief, neither run
  (budget already 4.25x over): (a) **transonicPCOption:1 ALONE** on this case — stock ILU
  memory (5.9 GiB fits easily), record-anchored ~28 core-min, tests the never-active PC lever
  solo; (b) sub-LU at **np=8/np=16** — halving/quartering the ASM sub-block size attacks the
  LU fill superlinearly, though the Option-3 aggregate-memory lesson must be re-checked in
  the factorization-dominated regime.
- Case state preserved: attempt 3's writeout and overwritten time-0 left in place;
  `_prior_state_backup_20260808/` holds the record writeout and every prior state.
