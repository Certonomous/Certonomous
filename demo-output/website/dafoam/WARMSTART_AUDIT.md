# Silent warm-start audit (pydafoam time-0 overwrite) — verdict table

Executed 2026-08-08T22:50Z by the entry-8 solver agent under chief ruling 3 of the epilogue
(14d57c8e); proposal `pydafoam-silent-warmstart-state-hazard` (approved 846fb28d, as priced:
log forensics only, zero solver core-min). Hazard being audited: pyDAFoam writes the primal
end state back into the time-0 directory at run end (proven bit-identical `0/U` == `1000/U`,
prereg addendum f77b2607), silently warm-starting every subsequent run of the same case dir;
`renameSolution` (pyDAFoam.py:1543) additionally hard-raises on a leftover `0.0001`.

## Signature revision, disclosed before the verdicts

The proposal priced four signatures. Signature (a) — "warm primal an order of magnitude
faster" — is INVALID as priced: this campaign's own controlled pair shows cold and warm
primals BOTH take ~10 s on the 21,840-cell rung (the priced 10-s-vs-270-s contrast was
coloring-computation time, not primal time). The audit therefore rests on: **(b) the first
`Time step continuity errors` value** — validated discriminator, cold-from-uniform 0.597 vs
warm 0.0107 on the same case (55x), bit-reproducible across every cold run (six independent
cold starts all print `0.5969274433533561` to 16 digits); **(c) `Moving time X to 0.0001`
success/failure lines**; **(d) time-dir mtimes vs run windows**. Signature (b)'s
bit-reproducibility makes the cold verdicts below strong; its absence (lost logs) is what
produces INDETERMINATE, never a silent pass.

## Verdict table

| # | conclusion / record | runs audited | evidence | verdict |
|---|---|---|---|---|
| 1 | **B3/CBFS reordering 2x2 + ordering ladder** (rcm/natural x force/varianceU; `-9` vs `-3`/stagnation; PROOF §25.2–25.3, case-status B3 entry) | 9 solver logs, `W4-cbfs-reordering/`, 08-02 05:23–06:37 | each arm ran in its OWN staged case copy (`cbfs_rcm/`, `cbfs_natural/`, `cbfs_nd/`, `cbfs_1wd/`, `cbfs_qmd/`, `cbfs_dump/`, `cbfs_force_*/`); first continuity error bit-identical (`9.30211816115683e-06`) across all 9; every rename `1580 -> 0.0001` succeeded (impossible in a reused dir) | **COLD-CLEAN** (state-controlled: every arm from the identical start state; the 2x2's conclusion compares arms, and the arms are provably same-state) |
| 2 | **M6 reordering pair** (`rcm` reproduces `-9`... on M6: natural/rcm both `-5`; B3 entry mechanism text) | `W4-m6-reordering/m6_{natural,rcm}.log`, 08-02 | own case subdirs; both arms cold-from-uniform (`0.5969274433533561`); renames succeeded | **COLD-CLEAN** |
| 3 | **W4 sub-LU unblock** (regress `-9` vs sublu reason-2/667; the FD-verified CBFS beta gradient) | `W4-adjoint-pc-unblock/cbfs_{regress,sublu,beta}` logs, 08-04 | own case subdirs; first continuity error bit-identical across regress/sublu/beta; renames succeeded | **COLD-CLEAN** for the warm-start mechanism. (The SEPARATE, already-disclosed 0/U=0.72 inlet contamination of that record — a patchV-pilot overwrite, different mechanism — stands as recorded in the case-status B3 entry; this audit adds nothing to and subtracts nothing from that disclosure.) |
| 4 | **hump sub-LU arm** (removes `-9`, leaves slow Krylov vs memory envelope) | `hump_sublu_computetotals.log`, 08-04 | single run, own subdir, rename `109 -> 0.0001` succeeded (fresh dir); first-run-cold presumption | **COLD-CLEAN** (single-run record; no rerun existed to contaminate) |
| 5 | **D3 n15 sweep record `-5`** (the envelope's 21,840-cell anchor) | `run_opt5_onera_n15_21840.log`, 07-29 22:41 | FIRST run of the dir, cold-from-uniform signature, rename succeeded | **COLD-CLEAN** |
| 6 | **D3 n15 variant-lever nulls** (mgso, noresnorm, richardson x globalPC/localPC, fill1, bigbudget, cl_only, sparsify — "no lever moved the `-5`") | NO LOGS PRESERVED (lost with the interrupted session's scratchpad); `reports/runScript_*` n2 dirs prove the variants ran IN this one case dir after the record run | mechanism proven for this dir (the record run overwrote time-0 with its end state); every subsequent variant run was therefore warm-started (and each must have had `0.0001` cleaned to get past rename — cleaning that never touched time-0) | **WARM-CONTAMINATED (presumptive; formally INDETERMINATE — logs lost, mechanism certain).** Conclusion-class: KSP-behavior nulls at the `-5`. No live conclusion currently rests on them — the `-5` story has moved entirely to the transonicPCOption dead-code finding, and today's cold control reproduces the `-5` bit-identically — but if any variant null is ever cited again it needs a cold rerun first. **→ CLOSED 2026-08-10: RETIRED AS SUPERSEDED (chief ruling, scope B, 0 core-min).** All 11 arms carried the dead `transonicPCOption: 2`, so each null says only "this lever did not rescue a run whose preconditioner was off" — a true statement about a baseline no future run will use (the token alone explains their `-5`: negative control 551a7ba5 reproduces it bit-for-bit, and flipping it converges at two rungs, 11b90d25 / 4e982b4a). A cold rerun would certify nulls about a superseded configuration. **This row's cold-rerun-before-citation requirement is satisfied by never citing them** — retirement forecloses the citation the requirement was protecting against rather than licensing it with fresh logs. Reasoning in full: `D3_VARIANT_COLD_RERUN_PREREGISTRATION.md` §6. The levers themselves remain live as questions on the WORKING config (scope C triage, graded on iteration count). |
| 7 | **R5/M6 conditioning matrix dumps** (`dump_pmat_n15.dat` 07-29 23:15, `dump_amat_n15.dat`, `dump_pmat_noresnorm_n15.dat` — feeding the M6 "14.17 decades of diagonal spread" figure) | dump files' mtimes sit 34+ min AFTER the record run, same case dir; no dump-run log preserved | dumped matrices were assembled about the warm (end-state-overwritten) time-0 state, ~2%-of-|U|max off the record's own writeout | **WARM-CONTAMINATED (state), conclusion-class robust:** the cited figures are order-of-magnitude conditioning measurements (14 decades), insensitive to a 2% state drift — and linearizing about a converged state was the dumps' intent. Flagged for the chief's regrade discretion, expected no-action. |
| 8 | **CBFS dump matrices** (`cbfs_dump`, `cbfs_force_dump` — the 8.67-decade / exact-zero-pivot spilu offline mechanism) | logs 08-02 05:35 / 06:37 | own staged case copies, same bit-identical start state as every 2x2 arm, renames succeeded | **COLD-CLEAN** (same-state as the arms whose behavior they explain — which is exactly what the offline mechanism claim needs) |
| 9 | **This campaign's entry-8 chain** (record `-5` anchor, TPC1 convergence, negative control, FD PASS) | all logs preserved in `A3-onera-m6-sweep-n15_21840/` | every decisive run carries the in-log cold proof `0.5969274433533561` after an explicit `decomposePar -fields` restoration; the one warm run (sub-LU attempt 1) was caught, disclosed, and discarded in-session | **COLD-CLEAN by construction** |

> **Note on row 4's label, dated 2026-08-11 (hump-adjoint attempt audit; the audit's own
> COLD-CLEAN verdict is untouched).** Row 4 describes the hump sub-LU arm as "removes `-9`,
> leaves slow Krylov vs memory envelope". That label was inherited from the record being
> audited, and that record's causal half has since been withdrawn: the arm never produced a
> `KSPConvergedReason` (killed by `docker stop` at iteration 900), so neither "slow Krylov"
> nor "memory envelope" was measured — only "no convergence observed in the 900 iterations
> run". Read row 4 as **"removes `-9`; no reason code reached"**. The warm-start verdict is
> unaffected and stands. What this audit *did* establish about that arm is now load-bearing
> in the other direction: **"single run; no rerun existed to contaminate"** is the same fact
> as **"never reproduced"** — the hump has 11 recorded adjoint attempts and zero deliberate
> reproductions. See `ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5b.1, items M2 and M3.

## Summary

- **No standing record-grade conclusion is overturned.** The two WARM flags land on (6) lever
  nulls that nothing currently cites — with the honest caveat that they need cold reruns
  before ever being cited again — and (7) order-of-magnitude matrix measurements robust to
  the drift class, flagged for chief discretion.
- The staged-copy pattern (per-arm case subdirs, as the W4 studies did) is inherently immune
  to the hazard and is the recommended pattern for A/B arms going forward; sequential reruns
  in one case dir REQUIRE the cold-start restoration step (now in the family guidelines §8).
- Regrade decisions belong to the chief per the proposal's own terms; this audit rewrites no
  conclusion.
