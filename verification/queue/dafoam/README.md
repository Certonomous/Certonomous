# Run queue — `dafoam`

**Drop path for this team's entries:** `verification/queue/dafoam/`

One entry is **one JSON file** in this directory, named
`<CASE_ID>.json` (ASCII, no spaces). The queue is a **passive list of
proposed launches**. It is read by
`scripts/queue_entry_check.py`, which validates entries and exits.

## ENQUEUEING IS NOT AUTHORISATION

`docs/charters/SUPERVISION_CHARTER.md` §3 gives each family supervisor four
checks that **may never be delegated**, the fourth being **"pre-registration
committed before compute"**. That check happens at **ENQUEUE** time and is the
supervisor's own, performed with their own eyes.

The validator's sha checks are a **second, mechanical guard — never a
replacement for the personal check.** **No entry in this directory has been
authorised by virtue of being here.** A file here is a proposal on a list; the
launch decision, and the personal check behind it, live outside this tree.

## Nothing here launches anything

There is no daemon, no scheduler, no watcher and no timer behind this
directory. `scripts/queue_entry_check.py` starts no child process other than
read-only `git` (`cat-file`, `rev-parse`, `ls-tree`, enforced by an
allowlist), never writes to git, and returns as soon as it has printed a
verdict per entry.

## Required fields — the validator REFUSES an entry missing any of them

| field | type | meaning |
|---|---|---|
| `team` | string | one of cfd, heat-transfer, ansys-verification, closure, dafoam, verification |
| `case_id` | string | the case/rung identifier this launch belongs to |
| `prereg_commit` | string | **full 40-hex sha** of the commit that froze the pre-registration |
| `prereg_path` | string | repository-relative path of the pre-registration **at that commit** |
| `launch_cmd` | list of strings | **argv list, never a shell string** |
| `cwd` | string | **absolute** path of the case directory the argv would run in |
| `ranks` | int | MPI ranks, `>= 1` |
| `cost_core_min_estimate` | number | pre-registered cost in **core-minutes** (wall s × ranks ÷ 60) |
| `cost_basis` | string | must state **derived / reported-by-owner, not measured** — this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| `memory_floor_gb` | number | RAM the case needs, GB |
| `enqueued_by` | string | who enqueued it, and therefore who owns the §3 check-4 record |

## Validation, and what each refusal means

1. **SCHEMA** — every field present, types correct, `launch_cmd` an argv
   list, `cwd` absolute, `cost_basis` honest about its origin.
2. **COMMIT-EXISTS** — `git cat-file -e <prereg_commit>`. The commit must exist.
3. **PREREG-AT-COMMIT** — `git cat-file -e <prereg_commit>:<prereg_path>`.
   The document must exist **at that sha**. A sha with no document at it is the
   laundering shape.
4. **AGE-GUARD** — standing rule 4. Refused if `cwd` already contains `0/`
   or any numeric time directory. A run is never launched into a tree that
   already holds an answer.
5. **RANKS** — `ranks >= 1`.

Every refusal exits `2` and names the check that failed.

## Standard

`docs/standards/QUEUE_ENTRY_STANDARD.md`. That document **creates** a
standard; it retires, widens and amends nothing. Retiring or widening a
standard or a gate threshold is **reserved to Sanaa**.

## This directory ships EMPTY

No entry has been enqueued by the lane that built this substrate. The first
real entries are Sanaa's to authorise personally.
