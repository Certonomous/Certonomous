# Run queue — `heat-transfer`

**Drop path for this team's entries:** `verification/queue/heat-transfer/`

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

## CORRECTION — 2026-08-27, heat-transfer supervisor: **THIS DROP PATH IS A LAUNCH BUTTON**

**Appended, never rewritten (`CLAUDE.md` rule 6). Lines whose number changed above this
section: 0.** Nothing below retires, widens or amends a standard or a gate threshold —
those are Sanaa's alone. This corrects a **statement of fact about a mechanism** which
has been overtaken by the code and the crontab.

**STRUCK — the section above headed "Nothing here launches anything", in particular:**
> ~~"There is no daemon, no scheduler, no watcher and no timer behind this directory."~~
> ~~"The queue is a **passive list of proposed launches**."~~
> ~~"This directory ships EMPTY ... The first real entries are Sanaa's to authorise personally."~~

**All three are FALSE as of 2026-08-26 and were false when 46 entries launched from here
overnight.** Measured by the supervisor at 2026-08-27, from the code and the crontab, not
reasoned from a document:

1. `scripts/queue_runner.py:223` scans this exact directory —
   `files = sorted(d.glob("*.json"), ...)` for every `team` in `TEAMS`, rooted at
   `verification/queue/`. A `.json` dropped here is picked up on the next tick.
2. `crontab -l` carries **`* * * * * /bin/bash .../scripts/queue_runner.sh`** plus an
   `@reboot` line. **The tick is one minute.** The daemon is live now (pid 856460; it was
   502797 until a 16:26:02Z restart — *an inherited pid is not a current reading*).
3. `queue_runner.py:461` reads `host = str(entry.get("host", "local"))` — **omission
   defaults to `local`, i.e. to THIS BOX.** The dangerous value is the default, which is
   the wrong way round for a safety field.
4. **Annotation does not confer inertness.** `scripts/queue_entry_check.py` runs five
   checks and **ignores every unrecognised key**. A `verdict_state: PENDING`, a
   `NOT AUTHORISED` in `enqueued_by`, a `# DO NOT RUN` — none of them is read by anything.
   Exactly three things keep an entry inert: it is **not in this directory** (a `held/`
   subdirectory works, and works only because the scan is `glob` and not `rglob` — one
   character); its `host` names another box; or **its own launcher refuses for itself**.
5. The only thing that delayed the 46 overnight launches was the runner's **busy
   ceiling** (`HELD ... busy {busy}% >= ceiling {ceiling}%`). That is a throttle, not a
   consent gate, and it clears by itself.

**WHAT THIS CHANGES FOR THE SUPERVISOR'S CHECK 4.** The section above is right that
enqueueing is not authorisation and that `SUPERVISION_CHARTER.md` §3 check 4 is the
supervisor's own. It is wrong about *when* that check must happen. Because the drop fires
within a minute, **check 4 is performed BEFORE the file enters this directory, never
after.** A lane that drops first and asks second has already launched. Draft entries live
in a case-local `queue_drafts/` directory or a `held/` subdirectory here — never as a
bare `.json` in this path.

**Provenance:** L-348, filed by the closure team 2026-08-27 after the same stale text
nearly fired a bulk drop; `docs/DOCKET.md` D535. This correction is the heat-transfer
drop path's own copy of that finding, placed where a lane about to enqueue will actually
read it. `docs/standards/QUEUE_ENTRY_STANDARD.md` carries the same stale description and
is **not** corrected here — it is not this team's document, and amending it is referred,
not taken.
