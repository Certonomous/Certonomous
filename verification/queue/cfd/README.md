# Run queue — `cfd`

**Drop path for this team's entries:** `verification/queue/cfd/`

One entry is **one JSON file** in this directory, named
`<CASE_ID>.json` (ASCII, no spaces). **This directory is a LAUNCH PATH, not a
list.** A live OS daemon polls it and launches from it — read
**"Dropping a file here ARMS A LAUNCH"** below before you copy anything in.
`scripts/queue_entry_check.py` validates an entry on demand and exits; it is the
same validator the daemon runs, but running it yourself launches nothing.

## ENQUEUEING IS NOT AUTHORISATION

`docs/charters/SUPERVISION_CHARTER.md` §3 gives each family supervisor four
checks that **may never be delegated**, the fourth being **"pre-registration
committed before compute"**. That check happens at **ENQUEUE** time and is the
supervisor's own, performed with their own eyes.

The validator's sha checks are a **second, mechanical guard — never a
replacement for the personal check.** **No entry in this directory has been
authorised by virtue of being here.** The rule and the mechanism point opposite
ways, and the mechanism does not wait: an unauthorised entry sitting here still
launches. So the timing is the whole of it.

**WHEN check 4 happens.** Adopted 2026-08-27 from the heat-transfer drop path's
own correction (`cfa68fe5`), **verbatim, so that one rule does not become two**:

> Because the drop fires within a minute, **check 4 is performed BEFORE the file
> enters this directory, never after.** A lane that drops first and asks second
> has already launched. Draft entries live in a case-local `queue_drafts/`
> directory or a `held/` subdirectory here — never as a bare `.json` in this path.

This is not a new rule and it widens nothing: it is what cfd already does — checks
1 and 4 were discharged on `F17c_KV40_FLOOR` before the enqueue was ordered, and on
`F22`, `F24` and `F25` before that. Stating the norm without the timing is what
invites a lane to drop first and check afterwards, by which point check 4 has
become an audit of a running solve rather than a gate before one.

## Dropping a file here ARMS A LAUNCH

**The drop path is a launch button** — closure's **L-348**, *"a drop path a
document calls passive is a launch button until the code says so"*. A live OS
daemon, `scripts/queue_runner.py --daemon`, polls **this exact directory** and
launches from it. Copying a validated entry in here is not a filing action: it
commits the box to a solve that spends real core-minutes against the entry's
registered cap. On an idle box that is the **next tick — under a minute**. On a
loaded box it waits at the busy ceiling, but it is **armed either way** and needs
no further human act to fire.

**Do not trust this paragraph — check.** The daemon writes its pid to
`verification/queue/runner.pid` (`queue_runner.py:1291`, `acquire_lock`), its ticks
to `verification/queue/runner.log`, and one row per launch to
`verification/queue/LAUNCH_LOG.tsv`. So
`kill -0 $(cat verification/queue/runner.pid)` answers *"is a daemon live"* in one
command, and answers it about **today** rather than about the day this file was
written. This document can go stale again; those three artifacts cannot. **A
reader who can verify does not need the document to stay true.**

**Cadence.** `--interval` defaults to **60 s** (`queue_runner.py:1280`), and every
tick that has entries to consider first measures the box over a **5 s** window
(`busy_percent`, `:175-177`) — so the observed cadence with a non-empty queue is
**~65 s** (read off `runner.log`: 19:11:43Z / 19:12:48Z / 19:13:53Z, 2026-08-27).
Cron runs `scripts/queue_runner.sh` every minute; that wrapper is idempotent and
the pidfile lock refuses a second copy (`:349-366`), so a runner that dies is back
within a minute and the drop path is armed again.

**At most ONE entry launches per tick**, across all six team queues together, and
only while the box is under its ceiling: `tick()` returns `"LAUNCHED"` immediately
after its single launch call (`:680-682`). The gates an entry must clear are
`busy % < 85` (`--busy-ceiling`, `:647-649`), `busy_cores + ranks <= 0.9 x ncpu`
(`--core-fraction`, `:650-655`) and `MemAvailable >= memory_floor_gb` (`:656-657`).
These are **throttles, not consent gates**: they change *when* a launch happens,
never *whether* it was authorised.

**A `HELD` entry is WAITING, not rejected.** It stays in this directory untouched
and is reconsidered every tick until it fits. `HELD` on the busy ceiling stops the
whole tick; `HELD` on core-fraction or on the memory floor is first-fit, so a
narrower entry queued behind a wide one still launches. **Nothing here is ever
deleted:** a launched entry is *moved* to `cfd/launched/`, and a launch record
superseded by a relaunch of the same `case_id` is *renamed*, not removed
(`archive_previous_records`, `:408-440`).

**An entry is consumed into `refused/` only when it is INVALID.** `move_refused()`
has exactly one production call site (`:637`), reached only where
`queue_entry_check.validate()` returned failures — a **permanent property of the
file**. A busy resource is a **transient property of the box** and has no path to
it: *a resource-busy condition is a WAIT, never a CONSUMPTION* (`:199-204`;
the GPU clause likewise, `:338-343`). So a file that has left this directory
either **launched** or was **invalid**. It was never discarded for being
inconvenient.

**`scripts/queue_entry_check.py` itself still launches nothing.** It starts no
child process other than read-only `git` (`cat-file`, `rev-parse`, `ls-tree`,
enforced by an allowlist), never writes to git, and returns as soon as it has
printed a verdict per entry. That was always true of the *validator*, and it was
never true of the *directory*.

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
| `enqueued_by` | string | who enqueued it, and therefore who owns the §3 check-4 record — **a declared, UNENFORCEABLE field: a statement of record, not a credential** (see below) |

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
5. **EXEC** — `cwd` must EXIST. The runner builds `cd '<cwd>' && <argv>` and
   `Popen(cwd=...)`, so an absent `cwd` would be recorded LAUNCHED and then die
   (`queue_entry_check.py:304-331`).
6. **RANKS** — `ranks >= 1`.

**`enqueued_by` IS NOT AND WILL NOT BE ENFORCED, and that is deliberate.** There is
nothing on this box to enforce it against: every commit and every process here shares
one Ubuntu identity, so a check comparing `enqueued_by` to anything available would
return PASS for **any** string an agent chose to write, while *looking* like an
authorisation control. A control that cannot fail is worse than an honest gap,
because a reader relies on it. Read the field as **a declaration of record** — it
says who is answerable for the §3 check 4 behind this entry — and never as proof that
they made it.

**`team` versus the directory it sits in is a REAL gap and is being closed.** The
runner iterates by directory (`queue_runner.py:389-395`), so an entry declaring one
team while sitting in another's path launches and is logged as the *directory's*
team — which corrupts verdict ownership and per-team queue depth. Specified at
`docs/standards/QUEUE_ENTRY_TEAM_BINDING.md`; the enforcement lands in
`queue_entry_check.py`, so a mismatch is a **validation failure** and therefore a
`refused/` outcome — a mismatched entry is INVALID, a permanent property of the file.

**Six checks, not five** — the registry is `CHECKS` at `queue_entry_check.py:343`;
count it there rather than here. Run by hand, every refusal exits `2` and names
the check that failed. Run by the **daemon**, the same failure list moves the
entry to `cfd/refused/` and writes `<CASE_ID>.REFUSED.txt` beside it — that is
the *only* way an entry leaves this directory without launching.

## Why this file was corrected IN PLACE, and heat-transfer's was appended to

**`CLAUDE.md` rule 6's append discipline exists because other records cite frozen
files BY LINE, and at least one citation sits inside an executable check — so moving
a line breaks a check.** This README is cited by no record at any line (checked
2026-08-27) and carries no version or amendment record, and its stale text was itself
the hazard. **For an uncited, non-frozen operational document whose wrong sentence is
the danger, the correction belongs at the point of use**: a reader who reads
"Nothing here launches anything" at the top and acts on it is not saved by a
correction sixty lines below. The struck text is quoted verbatim here and in the
correcting commit message, so the history survives without the hazard surviving with
it. A document that *is* cited by line takes heat-transfer's append shape instead —
that divergence is principled, not accidental.

## Standard

`docs/standards/QUEUE_ENTRY_STANDARD.md`. That document **creates** a
standard; it retires, widens and amends nothing. Retiring or widening a
standard or a gate threshold is **reserved to Sanaa**.

## Live state — this directory is NOT empty

Three sentences are **STRUCK 2026-08-27**, and they are struck for **two
different reasons that must not be confused**.

**STRUCK AS FALSE** — statements of fact the mechanism overtook:
> ~~"This directory ships EMPTY."~~
> ~~"No entry has been enqueued by the lane that built this substrate."~~

Both were written 2026-08-26T03:12Z, before the runner existed, and both were false
by 16:40Z the same day: `verification/queue/LAUNCH_LOG.tsv` carries **10 cfd
launches**, the first `F17_KV40` at 2026-08-26T16:40:52Z, and `cfd/launched/` holds
their records. Do not read a count off this line either — **read the directory**,
and read `runner.log` for what the daemon is doing with it right now.

**STRUCK AS SUPERSEDED BY THE AUTHORITY THAT SET IT** — a reservation to Sanaa:
> ~~"The first real entries are Sanaa's to authorise personally."~~

**Events do not retire rules.** That the lab has been launching without per-entry
personal authorisation is, on its own, evidence that the *practice* was in
violation — never that the *rule* lapsed. A sentence reserving something to Sanaa
is retired by **Sanaa**, and by nobody else at any level. It is struck here because
she superseded it herself, three times and by later date:

1. **2026-08-21** — *"all the teams have my approval for everything"* (the standing
   blanket, `CLAUDE.md` rule 12).
2. **`CLAUDE.md` rule 12** — runs under \$25 are **pre-authorised**, which is a
   standing grant precisely of the per-run consent this sentence reserved.
3. **2026-08-26 — the detached-runner ruling**, and this one is decisive: queues run
   as **OS daemons independent of agents**, and **idle compute is the failure**. A
   daemon that must pause for a personal authorisation per entry is not independent
   of agents and is not the thing she ordered. The two cannot coexist, and hers is
   the later and the more specific.

**A blanket is still not a per-item reading** (rule 9): what lapsed is the
*personal-authorisation-per-entry* requirement, not the supervisor's own §3 check 4,
which the section above hardens rather than relaxes.
