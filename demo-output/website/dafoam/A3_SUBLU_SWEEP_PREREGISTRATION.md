# A3 ONERA M6 sub-LU + transonicPCOption arm, RE-FILE on the 21,840-cell sweep mesh: PRE-REGISTRATION

Filed 2026-08-08T02:39Z by the DAFoam solver agent, under the chief's same-session approval of
re-file candidate 1 from `A3_SUBLU_RESULT.md` (commit 54a2f2ff): the vcoarse rung proved
congenitally unrunnable, so the approved entry-8 diagnostic
(`SUPERVISOR_NEGATIVE_VERDICT_REVIEW_2026-08-07.md` entry 8, docket
`a3-m6-vcoarse-adjoint-sub-lu-arm`) moves to the cheapest archived M6 case that actually
matches the proposal's cost basis. Same ~30 core-min envelope; the vcoarse arm's 0.53 core-min
counts inside it. Committed BEFORE launch; supersedes nothing in
`A3_SUBLU_PREREGISTRATION.md` (12d3a7a3) except the case identity — levers, KSP criteria, and
outcome mapping carry over unchanged and are restated here so this file stands alone.

## 1. Case identity

`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/` — **21,840 cells**, the D3
envelope sweep's N=15 point (3x-coarsened `m6_surfaceMesh_fine.cgns` surface, pyHyp 15
extrusion layers, `ADJOINT_MEMORY_ENVELOPE.md` Option 4). Same flow condition and runScript
family as the whole A3 ladder (M=0.84, alpha=3.06, `DARhoSimpleCFoam`, `primalMinResTol 1e-6`,
`adjEqnOption {gmresRelTol 1e-4, pcFillLevel 0, jacMatReOrdering natural, gmresRestart 200}`;
the sweep `runScript.py` is line-identical to the vcoarse one outside comments). State as
archived: 4-rank decomposition in place from the record run; coloring cache
`dRdWColoring_4.bin` (2026-07-29) reused bit-identical to the record arm; `controlDict` has
`startFrom startTime; startTime 0`, so the leftover `0.0001` writeout dirs in `processor*` are
inert and are left untouched. **No orphan-autoPatch layer exists on this case** (boundary is
already exactly wing 1560 / inout 1560 / sym 952 — checked before filing; no repair needed).

## 2. checkMesh PASS, asserted pre-launch (run BEFORE this pre-reg was committed)

Standalone `checkMesh -constant` on the archived mesh, this session, stock utility in the
`dafoam-subpclu:v1` container: **"Mesh OK."** — zero failed checks. Max aspect ratio 608.2
(OK), min volume 1.4139e−10 (positive, OK), max non-orthogonality 61.49 / average 14.99 (OK),
face pyramids OK, max skewness 1.44 (OK). The vcoarse failure mode cannot fire twice.

## 3. The baseline this arm re-probes

The record `-5` on THIS case, `run_opt5_onera_n15_21840.log`: both adjoint solves
`PetscConvergedReason: -5` — 400 iterations / 328.22 s and 600 iterations / 409.44 s, the
second stalling near 1.84e−01 for hundreds of iterations before the terminal denormal
(3.945602898014e−308). That run had stock sub-ILU and `transonicPCOption 2;` echoed in its
DAOption dump (log line 410) — dead code for `DARhoSimpleCFoam`.

**Interpretation note, binding:** this arm is the FIRST probe of the M6 conditioning wall with
the transonic preconditioner actually ACTIVE (option 1, the only live value in
`DAResidualRhoSimpleCFoam.C:173`, per the dead-code finding of prereg 12d3a7a3 §2), stacked
with the ASM sub-block complete-LU switch. Every archived M6 `-5`, this case's record included,
ran with the transonic PC silently off.

## 4. Levers, provenance, and the in-log activity proofs (pre-declared)

1. `DAFOAM_SUBPC_TYPE=lu` on `dafoam-subpclu:v1` (`DALinearEqn.C:277–285`;
   `ladder-b/W4_ADJOINT_PC_UNBLOCK.md`; sweep 9c19ccc8). PROOF REQUIRED in the launch log:
   `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU`.
2. `transonicPCOption: 1` (liaison lead 1.5; official transonic NACA0012 tutorial line 73;
   semantics `DAResidualRhoSimpleCFoam.C:172–176` — drop `fvm::div(phid,p)` from the PC
   pressure equation). PROOF REQUIRED in the launch log: the DAOption dump line reads
   `transonicPCOption 1;` (where the record log reads `2;`).

Script: `runScript_sublu_tpc1.py` in the sweep dir — copy of the archived `runScript.py` with
exactly one functional change, `"transonicPCOption": 2 -> 1`. Task `compute_totals` (primal +
one adjoint solve per response: CD, CL). Combined arm, as approved; the cost argument of
prereg 12d3a7a3 §3 carries over.

## 5. "Converged adjoint" (unchanged from 12d3a7a3 §4)

From the raw solver log, never the wrapper's success line: CONVERGED = positive
`PetscConvergedReason` (2 = KSP_CONVERGED_RTOL is the family's success code) on BOTH the CD
and CL solves; FAILED = any negative reason on either solve (−5 the standing signature; −3,
−9, or any other negative code counts; the denormal-residual false-success pattern counts as
FAILED), or crash/OOM before a reason prints. Both §4 activity proofs must be verified before
either verdict is claimed. Pre-registered branch retained: if the primal fails its own gate
(it passed on record at this rung), the arm is NOT EVALUABLE here and neither outcome fires.

## 6. The two outcome meanings, from entry 8 verbatim

> If it converges, A3's ladder reopens and the DIVERGED_BREAKDOWN story gets its epilogue; if
> not, the conditioning wall is confirmed beyond the incompressible family.

- **Converges** (per §5) → A3's ladder reopens and the DIVERGED_BREAKDOWN story gets its
  epilogue.
- **Fails** (per §5) → the conditioning wall is confirmed beyond the incompressible family —
  now with the strengthened meaning that it stands even with the transonic PC active and
  complete-LU sub-blocks, the two known unblocks tested together.

## 7. Mechanics and budget

`dafoam-subpclu:v1`, `--cpus=4 --memory=10g` (record agg peak 5,876.6 MiB at this size),
4 ranks, `mpirun --allow-run-as-root -np 4 python runScript_sublu_tpc1.py -task
compute_totals`, canonical `loadDAFoam.sh` invocation. Launch setsid-detached via
`run_arm.sh` in the sweep dir with the `.t0/.rc/.t1` self-ledger; log
`sublu_tpc1_computetotals.log`; polled inline, no monitors or background waiters. Budget:
29.47 core-min remain of the approved 30 (record anchor for this case: 420 s wall x 4 = 28
core-min). Pre-launch process check re-run at launch. Result: appended to
`A3_SUBLU_RESULT.md`; docket `a3-m6-vcoarse-adjoint-sub-lu-arm` outcome updated inline,
own entry only.

## 8. Addendum, 2026-08-08T02:52Z — §1's "inert" claim FALSIFIED by launch attempt 1; repair and relaunch, pre-registered before attempt 2

Attempt 1 (t0 1786156818 = 02:40:18Z, ledger rc=1 at t1 1786156834, 16 s = 1.07 core-min)
died before the adjoint KSP, and taught two things about the archived case state that §1 got
wrong:

1. **The leftover `0.0001` dirs are NOT inert.** DAFoam's `renameSolution`
   (`pyDAFoam.py:1543`) moves the fresh primal writeout (time 1000) to `0.0001` before the
   adjoint solve and hard-raises `"0.0001 already exists, moving failed!"` when the record
   run's writeout is still there. This is what killed attempt 1.
2. **DAFoam writes the primal end state back into time 0** — after attempt 1,
   `processor0/0/U` is bit-identical to `processor0/1000/U`. Every variant run since the
   record run did the same, so attempt 1's primal started WARM (converged fields at time 0):
   1000 steps in 10.13 s vs the record's cold-start ~270 s, ending at a state that differs
   from the record writeout by up to 2.2% of |U|max (two near-converged plateaus of the same
   flow). A warm start is NOT the record arm's condition.

Repair, applied before attempt 2 and preserving everything: `processor*/0.0001` (the record
writeout), `processor*/1000` and the overwritten `processor*/0` moved to
`_prior_state_backup_20260808/`; pristine uniform initial fields restored with
`decomposePar -fields` onto the UNTOUCHED partition (serial `0/` verified byte-identical to
`0.orig` first; the decomposition and the `dRdWColoring_4.bin` cache are exactly the record
run's — apples-to-apples preserved). Attempt 2 is therefore the record arm cold-start plus
the two levers, nothing else. Attempt 1's log is preserved as
`sublu_tpc1_computetotals_attempt1.log`. Spend so far against the 30 core-min: 0.53 (vcoarse)
+ 1.07 (attempt 1) = 1.60. Everything else in this pre-registration is unchanged.
