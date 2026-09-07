# ⚠ THIS DIRECTORY IS NOT LIVE — DO NOT WRITE THE BOARD HERE

**The live lab board is `docs/LAB_STATE.md`** (the monolith), written **only** via the
guarded helper `cases/RANS_LES_closure_models/_common/commit_private.sh`, which carries
the **BOARD-CLOBBER GUARD** (it refuses any commit that drops a section or block).

This `docs/lab_state/` per-team-source system (`<team>.md` here + `scripts/merge_lab_state.py`
+ `scripts/merge_lab_state_cron.sh` + `scripts/check_board_source_writes.py`) was
**COMMITTED WITHOUT CUTOVER** on 2026-08-31 and is **DORMANT**.

- The `*.md` files in this directory are **UNTRACKED and STALE** (2026-08-31, *before* the
  2026-09-07 L-499 convergence of the monolith). **They are NOT the board.** Do not read
  them as a team's state and do not write your section into them. Reading a stale/empty
  source here already cost a team a stall.
- `merge_lab_state.py` **HARD-REFUSES every real invocation with rc 7** (a NOT-LIVE banner)
  until a deliberate, chief-sequenced cutover. `--selftest` remains exempt. The merge cron
  is **not installed**.
- **Cutover is not yet taken.** It is a deliberate human act — set
  `MERGE_LAB_STATE_CUTOVER_AUTHORIZED=1` **and** run `merge_lab_state.py --adopt` once —
  and it happens only after the chief approves the migration plan
  (see `docs/BOARD_MIGRATION_PROPOSAL.md`).

**Owner:** verification-supervisor (board hygiene). **Status recorded:** 2026-09-07.
