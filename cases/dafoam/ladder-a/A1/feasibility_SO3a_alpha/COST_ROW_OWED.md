# SO-3aF calibration row — OWED AND UNFILEABLE, with the blocker MEASURED

**NOT FILED.** This row is owed to `docs/COST_CALIBRATION.md` under CLAUDE.md
rule 12's estimate-versus-actual duty. It is not filed, and the reason is stated
here so the next agent lands it in one call instead of re-deriving the blocker.

## The blocker is NOT the one the brief anticipated

The brief expected `scripts/append_record.py` to still refuse this record at
**exit 7** (the D549 shape audit over the strikes at `docs/COST_CALIBRATION.md:304`
and `:306`). **That refusal is CLEARED.** Measured 2026-08-31 by this lane:

    scripts/append_record.py --path docs/COST_CALIBRATION.md \
        --rows <this row> --allocate-id --dry-run
    -> VERDICT: OK,  exit 0

The `--allocate-id` path sanctioned by Sanaa's 2026-08-31 plumbing freeze mints a
timestamp+hash id and the shape audit passes. So the historical blocker is gone.

## The live blocker, measured here

`append_record.py` states a precondition on its own allocation path, verbatim from
its output:

> Allocation must NOT be enabled on a record until that module reads
> `tool_id_pattern(path)` alongside `RECORDS[path]`; this module cannot enforce
> that and says so rather than assuming it.

**That precondition is UNMET.** `scripts/check_record_reconciliation.py` (mtime
2026-08-28, i.e. it predates the freeze) imports
`from append_record import RECORDS, parse_ids, split_id` — and **not**
`tool_id_pattern`. Every id it parses comes from the legacy pattern
`^\|\s*(?:\*\*|~~)*\s*(C-\d+)\s*(?:~~|\*\*)*\s*\|`.

A tool-allocated id has the form `C-20260831T163117.393947Z-9b2f7090`. After
`C-20260831` comes `T`, not a cell close, so **the legacy pattern does not match
it.** The reconciler would therefore not see this row at all — its unlanded-work
and duplicate reports would silently skip it.

**Zero tool-allocated ids are currently landed in any guarded record**
(`COST_CALIBRATION.md`, `DOCKET.md`, `LESSONS.md`, `NUMERICS_KNOWLEDGE.md`: 0, 0,
0, 0). This row would be the FIRST, in a five-team shared ledger, invisible to the
guard that exists to catch exactly the duplicate/unlanded failure that ledger
already carries a struck `C-215` row for. **Filing it would be worse than not
filing it**, so it is not filed.

## Why this lane did not simply clear the blocker

- **Teaching the reconciler `tool_id_pattern` is not this lane's to do.**
  `append_record.py` names the owner: *verification-supervisor*, assigned
  2026-08-28, guarding four lab-wide registers. Editing a shared cross-team guard
  from a dafoam feasibility lane is precisely the shape the escalation charter
  forbids.
- **A legacy sequential `C-NNN` id is not an escape hatch.** Sanaa's plumbing
  freeze rules counters dead ("no sequential numbers anywhere"), and the stale-tail
  hazard is what produced the struck duplicate in the first place.
- **Hand-appending around the tool is forbidden outright.**

## What unblocks it

One change, by verification: `check_record_reconciliation.py` reads
`tool_id_pattern(path)` alongside `RECORDS[path]`. The moment that lands, the row
below goes in with `--allocate-id` in a single call. No id is reserved or named
here — the id is whatever the tool mints inside the landing invocation.

## The row, ready to land

| id | date | team | process | predicted (core-min) | actual (core-min) | ratio | attribution | dollars |
|---|---|---|---|---|---|---|---|---|
| {{ALLOCATE_ID}} | 2026-08-31 | dafoam | SO-3aF alpha-multipoint feasibility sweep — 3 cold primals at np=1 in one container | 1.5 | 0.5833 | 0.389 | OVER-prediction of COLD START, not of work. Estimate assumed ~15 s per cold primal plus ~15 s container start; the whole three-point sweep took 35 s of container wall. Like-for-like anchor for a later alpha sweep on this mesh at np=1: ~11.7 s per cold primal INCLUDING amortised container start, against the 3.755 s warm anchor — cold is ~3x warm here, not the 4x assumed. Waste 0.000 core-min, named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and never absorbed into the ratio | $0.0005 **DERIVED, NOT MEASURED** at the recorded $0.0513/core-h; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |

Cost figures cite `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility/STATUS.SO3aF`
(`wall_s=35 ranks=1 core_min=0.5833 cap_core_min=8.0`, `rc=0 source=docker_inspect_ExitCode
oom_killed=false`) and the 1.5 core-min estimate in the queue entry.

---

## CLOSED 2026-08-31 — THE ROW IS FILED, AND THE BLOCKER ABOVE WAS ALREADY DEAD WHEN THIS FILE WAS READ

**APPENDED, not rewritten — every line above stands as written and was true when written.** The row above is **LANDED** in `docs/COST_CALIBRATION.md` as **`C-20260831T164216.179599Z-19ea8c16`**, minted by `scripts/append_record.py --allocate-id` inside the landing invocation, asserted to appear EXACTLY ONCE at HEAD.

**The live blocker this file names is cleared, and it was cleared by measurement rather than by inheritance.** §"The live blocker" reasons from `check_record_reconciliation.py`'s import list that the module reads only the legacy pattern. It now imports `ANCHORED_TOOL_ID`, `is_tool_id` and `parse_record_ids`, and `parse_record_ids` reads BOTH id spaces. Driven against the real production path with controls both directions: a tool-allocated id already landed in this ledger IS seen, exactly once; a fabricated tool id is NOT seen; a tool id planted into the real corpus IS seen and disappears when removed. The reconciler's own report reads **TOOL-ALLOCATED: 1 committed, 1 in the working copy**. **No shared guard was edited to achieve this** — it had already been taught, by its owner.

**One thing this file got right and is worth keeping:** it declined to hand-append around the tool and declined to mint a legacy sequential id. Both refusals were correct, and the row landed the way this file said it should — in a single `--allocate-id` call, with no id reserved or named in advance.

**A separate red is disclosed rather than left for the next reader to rediscover:** `check_record_reconciliation.py --path docs/COST_CALIBRATION.md` returns **rc 4, VERDICT FAIL**, on **DUPLICATE IDS — committed `C-217` / worktree `C-217`**. That is **closure's** row, closure is stood down, and it is neither caused by this row nor cleared by it; an append-only record accepts an append while another team's duplicate stands. Untouched and reported.
