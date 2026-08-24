# PROVENANCE — `HEATBALANCE_400.{json,txt}` and `HEATBALANCE_800.{json,txt}`

**Written 2026-08-24T16:29:04Z. These four files were restored to this directory
from HEAD on 2026-08-24 under the chief's ruling on docket row D477. Zero HEAD
bytes changed by that restore; the four blobs on disk hash identically to HEAD.**

## They are first-pass artifacts, and the case around them is not their case

These two report pairs were produced by the **800-iteration first pass** of
`K2bP_C3_plant`, not by the 5,000-iteration run whose time directories sit beside
them today. The frozen tree says so: `system/controlDict` at commit `fa2c8bb0`
reads `endTime 800`, `writeInterval 400`, so `400/` and `800/` were the only two
time directories that pass ever wrote, and its `COST.txt` at the same commit reads
`iterations 800`, `wall_clock_s 66.179954585`, `core_minutes 1.1029`. Both report
pairs were committed at **`fa2c8bb0`, 2026-08-18T04:24:55Z**.

The case was then rebuilt **in place** at 2026-08-18T04:28:59Z for the re-run to
5,000 iterations (`CASE.txt`, `SEED.txt`, `0.orig/*`, `system/*`, `constant/*` all
carry that mtime; `0/` was created at 04:28:59.190). `run_k2b.sh:57` —
`for d in [1-9]*; do [ -d "$d" ] && rm -rf "$d"; done` — removed `400/` and `800/`
at the start of that re-run. That glob does not match `HEATBALANCE_*`, so it is
not what removed these four files.

## The clearing window, and what is not known

The four files were removed from the worktree between **2026-08-18T04:24:55Z**
(committed, therefore on disk) and **2026-08-18T04:43:00.8Z**. The upper bound is
this directory's own mtime, which equals the birth time of `HEATBALANCE_5000.json`
and has not moved since: no entry has been created or unlinked here after that
instant. The removal was never staged, so HEAD kept the files and the disk did not.

**The exact command is unrecoverable.** There is no session log before
2026-08-23 and no shell-history match. Two sub-mechanisms fit the window and
cannot be discriminated: a post-re-run audit invoked at 400/800 against times that
no longer existed (`scripts/heat_balance.py:631-632` deletes its `--json` target
up front and unconditionally, then refuses), or a manual clear of the superseded
reports before the 1000–5000 re-audit.

**D390 is the mechanism class, but it was mis-mapped onto these blobs.** D390
describes no-ledger stubs that were "cleared and re-run rather than committed" —
a *later* generation of files wearing these names. The files here carry full
ledgers. The rung's frozen reproduction recipe audits this case at
**1000 2000 3000 4000 5000 only** (`docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md:1004`),
so a faithful replay reproduces the disk state seen before this restore.

## What they back

| time | net (this case) | imbalance | no-plant twin net | recovered |
|---:|---:|---:|---:|---:|
| 400 | −1.517859e+02 W | 3.0912 % FAIL | +3.764241e+00 W | **155.550141 W** |
| 800 | −3.072705e+02 W | 6.2563 % FAIL | +8.296449e+00 W | **315.566949 W** |

Those are D381's published 155.55 W and 315.57 W against the planted 500.000 W,
and the −68.89 % baseline D388 quotes. The twin ledgers are in
`../K2bP_C3b_noplant/`, with the same note.
