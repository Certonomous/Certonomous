# A3 ONERA M6 transonicPCOption:1-ALONE arm (21,840-cell sweep mesh): PRE-REGISTRATION

Filed 2026-08-08T03:26Z by the DAFoam solver agent under the chief's same-session ruling 1
(follow-on to the sub-LU arm's not-evaluable result, `A3_SUBLU_RESULT.md` 0b4f3005): the
never-active transonic-PC lever SOLO, inside the record's ILU memory envelope. Docket lineage:
`a3-m6-vcoarse-adjoint-sub-lu-arm` (entry 8). Approved ~28 core-min. Committed BEFORE launch.

Ruling 2 is recorded here as it binds this arm's write-up: **sub-LU at np=8/16 is DEFERRED
behind this arm's answer.**

## 1. Case, config, and the single lever

Same case as `A3_SUBLU_SWEEP_PREREGISTRATION.md` (054d10b2) §1:
`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/`, 21,840 cells, checkMesh PASS on
record from that filing ("Mesh OK.", zero failed checks) — `constant/polyMesh` untouched by
every run since (runs write only time dirs), so the PASS stands. Script
`runScript_tpc1.py` = the archived `runScript.py` with the one functional change
`"transonicPCOption": 2 -> 1`; **`DAFOAM_SUBPC_TYPE` is NOT set** — stock ASM/ILU(0),
`natural`, `gmresRestart 200`, `gmresMaxIters 1000`, exactly the record `-5` configuration
with the transonic PC switched from dead code to live. Task `compute_totals`, 4 ranks.

Cold start, per the warm-start trap this campaign found (054d10b2 §8): the attempt-3
leftovers (`processor*/0.0001` and the overwritten warm `processor*/0`) are moved to
`_prior_state_backup_20260808/` and pristine uniform fields restored with
`decomposePar -fields` from the serial `0/` (verified byte-identical to `0.orig`), partition
and `dRdWColoring_4.bin` cache untouched. The launch log must show a cold primal (initial
`Time step continuity errors` at the ~1e-2 scale, primal wall comparable to a cold 1000-step
run, no pre-existing `0.0001`).

## 2. Activity proof (pre-declared)

The DAOption dump in the launch log must read `transonicPCOption 1;` (the record log reads
`2;` at its line 410). Semantics: `DAResidualRhoSimpleCFoam.C:172–176` — the PC-matrix
pressure equation drops `fvm::div(phid, p)`; `== 1` is the only live value for this solver
(the dead-code finding, prereg 12d3a7a3 §2). No sub-LU banner may appear (env unset); if one
appears, the arm is invalid and stops.

## 3. Memory guard (pre-declared)

This arm must sit inside the record's own envelope: 5,876.6 MiB aggregate for the identical
config at this size. Container cap `--memory=10g`. This arm should never approach the cap or
the 6 GB host floor; if it does — cgroup OOM, cap-grazing, or host MemAvailable < 6 GB — the
arm STOPS and the memory behavior is itself reported as a finding (an active transonic PC
changing the ILU memory footprint would be new information). Host at filing: load 6.17/16
cores, 29 GB available, swap clear, no other solver container running.

## 4. "Converged adjoint" (family standing criteria, unchanged)

From the raw log, never the wrapper's success line: CONVERGED = positive
`PetscConvergedReason` (2 = KSP_CONVERGED_RTOL) on BOTH the CD and CL solves; FAILED = any
negative reason on either (−5 the record signature; the denormal-residual false-success
counts as FAILED); crash/OOM before a reason prints = NOT EVALUABLE (the sub-LU arm's
precedent: a memory death is not a conditioning verdict), reported as such.

## 5. Outcome meanings — entry 8's two outcomes apply CLEANLY here for the first time

> If it converges, A3's ladder reopens and the DIVERGED_BREAKDOWN story gets its epilogue; if
> not, the conditioning wall is confirmed beyond the incompressible family.

- **Converges** → A3's ladder reopens, and the record's wall was at least partly the INACTIVE
  transonic PC: every archived M6 `-5` ran with the mitigation silently off.
- **DIVERGED_BREAKDOWN (or any negative reason) with the PC proven live** → the conditioning
  wall is real and confirmed on compressible M6 WITH the solver's own transonic mitigation
  on — the strongest form of entry 8's second outcome available inside this memory envelope
  (sub-LU untestable here per `A3_SUBLU_RESULT.md`; its np=8/16 variant deferred by ruling 2).

## 6. Mechanics and budget

`dafoam-subpclu:v1` image with env UNSET (env-off = stock toolchain behavior, the verified
regression property of the patched image), `--cpus=4 --memory=10g`, 4 ranks,
`runScript_tpc1.py -task compute_totals`, canonical `loadDAFoam.sh` invocation. Launch
setsid-detached via `run_arm_tpc1.sh`, self-ledger `.t0/.rc/.t1`, log
`tpc1_computetotals.log`, polled inline; explicit watch handoff if the agent's turn ends
mid-run. Budget ~28 core-min (record anchor 420 s x 4); measured spend reported against it.
Result: appended to `A3_SUBLU_RESULT.md`; docket entry updated inline, own entry only.
