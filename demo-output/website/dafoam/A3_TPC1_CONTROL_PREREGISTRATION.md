# A3 negative-control arm — record configuration rerun (transonicPCOption 2): PRE-REGISTRATION

Filed 2026-08-08T22:28Z by the DAFoam solver agent, resuming chief ruling 1 of the entry-8
epilogue (14d57c8e) after the 03:40Z session-limit fleet kill (paper trail verified on resume:
no control pre-registration existed in git; nothing solver-side ran between 03:40Z and this
filing — docker ps and pgrep clean, host since rebooted, up 10 min at check). Approved ~30
core-min. Committed BEFORE launch.

## 1. Purpose — the one remaining confound on "one token was the wall"

The TPC1-alone arm (prereg 13c244cd, result 11b90d25) converged both M6 adjoint solves where
the record run produced double DIVERGED_BREAKDOWN, with one token changed. The remaining
confound: host/state drift since the record run (2026-07-29/30) — the record `-5` was never
reproduced on TODAY'S host under this campaign's cold-start repair. This control reruns the
RECORD configuration under conditions bit-identical to the converged arm except the token.

## 2. Configuration

Same case (`/home/ubuntu/certonomous-runs/A3-onera-m6-sweep-n15_21840/`, 21,840 cells,
checkMesh PASS standing from 054d10b2 — polyMesh untouched since), same partition, same
`dRdWColoring_4.bin` cache, same image `dafoam-subpclu:v1` with `DAFOAM_SUBPC_TYPE` UNSET,
same `--cpus=4 --memory=10g`, 4 ranks, task `compute_totals`, cold-started by the standing
repair (move the TPC1 arm's `0.0001` writeout and overwritten warm `processor*/0` to the
backup dir; `decomposePar -fields` from the pristine serial `0/`). Script: the archived
`runScript.py` itself — the record script, `"transonicPCOption": 2`, zero edits. The full
diff between this arm's script and the converged arm's `runScript_tpc1.py` is the single
token (verified: one line, `2` vs `1`).

Activity/identity proofs required in the log: DAOption dump reads `transonicPCOption 2;`
(matching the record log's line 410), NO sub-LU banner, cold primal (initial continuity error
at the ~0.6 scale from uniform), no pre-existing `0.0001`. Memory guard as in 13c244cd §3
(record ILU envelope 5,876.6 MiB; never approach the cap or floor — this configuration
completed at 5.9 GiB on record). Host at filing: fresh boot, idle (load 0.25, 29 GB
available); S1 and Cases agents resuming concurrently — load re-checked at launch.

## 3. Pre-registered expectation (the record signature, quantitative)

From `run_opt5_onera_n15_21840.log`, the record `-5` on this exact case:

- Solve 1: stall plateau at the **2.12e−02** scale (2.120880199369e−02 at iteration 0,
  2.111512927865e−02 still at 300), terminal denormal (6.467896765713e−310),
  `Total iterations: 400. PetscConvergedReason: -5`.
- Solve 2: stall plateau at the **1.8391e−01** scale (1.839195903440e−01 / 1.839160961071e−01),
  terminal denormal (3.945602898014e−308), `Total iterations: 600. PetscConvergedReason: -5`.

Expectation: this control reproduces the stall-and-breakdown signature — negative reason on
both solves, plateaus at those values (the converged arm already showed today's linearization
state matches the record's to four digits at solve-2 start).

## 4. Interpretation, pre-stated both ways (binding, the chief's words)

- **Control FAILS as expected** (stall at 1.8391...e−01 / DIVERGED_BREAKDOWN) → **causation
  nailed**: on one host, one day, one cold-start protocol, one case state, the only difference
  between double-`-5` and double-reason-2 is `transonicPCOption` 2 vs 1.
- **Control CONVERGES** → **the token story is wrong; the finding reverts to open** — the
  TPC1 arm's convergence would be attributable to host/state/toolchain drift, not the PC
  option, and this will be said as loudly as the claim was made, in the result record, the
  docket entry, and the report to the chief.
- Control dies without a reason code (crash/OOM) → control not evaluable; the confound stands
  unclosed; no causal claim strengthens; reported as such.

Note on expectation asymmetry, stated for honesty: the record `-5` ran on the 2026-07-29 host
before this campaign's repairs, warm-start state unaudited (it was the FIRST run of the case,
so presumptively cold); this control is the first record-config run under today's fully
controlled conditions. A reproduction is expected but not guaranteed, which is exactly why
the arm exists.

## 5. Mechanics

`run_arm_ctrl.sh`, setsid-detached, self-ledger `.t0/.rc/.t1`, log `ctrl_computetotals.log`,
polled inline (explicit watch handoff if the turn ends mid-run). Budget ~30 core-min (record
anchor: both `-5` solves inside ~420 s wall x 4). Result: appended to `A3_SUBLU_RESULT.md`;
docket entry `a3-m6-vcoarse-adjoint-sub-lu-arm` updated inline, own entry only.
