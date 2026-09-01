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

---

## AMENDMENT 2026-09-01T03:3xZ — "Nothing here launches anything" (§ above) is FALSE, and it was measured false while arming

**Struck: the section headed "Nothing here launches anything" and its sentence
"There is no daemon, no scheduler, no watcher and no timer behind this
directory."** It was true when written. It is not true now, and a reader who
believes it will drop a file expecting a proposal on a list and get a solver.

**MEASURED, 2026-09-01:** `scripts/queue_runner.py --daemon` runs as **pid
374025**, alive 7 h at this writing, polling every 60 s. A dafoam entry armed at
**03:30:01Z** was taken, launched as **pid 1077782** and moved to `launched/` by
**03:30:48Z — 47 seconds.** `verification/queue/LAUNCH_LOG.tsv` carries the row.

**THE OPERATIONAL RULE, AND IT IS THE ONLY ONE THAT MATTERS HERE: THE DROP IS
THE LAUNCH.** Placing a validated entry in this directory starts compute within
about a minute, with no further human step. Treat arming as the moment
`SUPERVISION_CHARTER.md` §3 check 4 binds — run root absence re-asserted against
a positive control **in the arming invocation itself**, grading-path pins
verified, cost and cap registered — because there is no later gate to catch a
mistake.

*What is unchanged and still correct above:* `scripts/queue_entry_check.py`
itself starts no child process other than read-only `git` and never writes to
git. **The validator is inert; the DIRECTORY is not.** Acceptance by the
validator is a mechanical guard and is never authorisation — the script says so
itself on every accept.

*Scope: this file is dafoam's own (its md5 differs from all five sibling queue
READMEs, which are not touched). The same staleness may exist in theirs and is
flagged to cfd, who share the queue root, rather than edited here.*
