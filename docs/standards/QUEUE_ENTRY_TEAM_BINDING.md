# Queue entry — TEAM BINDING

**Status: SPEC, FROZEN AT ITS COMMIT. No code exists yet.** This document is written
**before** the implementation precisely so the implementation cannot be shaped to pass its
own test (`CLAUDE.md` rule 2's discipline applied to tooling). The commit that lands this
file is the freeze; the code that follows cites that sha, and any departure from what is
written here is a dated amendment at the foot, never an edit above it (rule 6).

**Owner:** cfd-supervisor (`scripts/queue_entry_check.py` is cfd tooling).
**Provenance:** found by cfd lane Q on 2026-08-27 while repairing the false
"nothing here launches anything" section of `verification/queue/cfd/README.md`
(commit `67553248`); ruled a real defect and ordered specified-before-coded by the
cfd-supervisor the same day. Sibling rulings: `QUEUE_ENTRY_VALIDATOR_RULINGS.md`
(R-AGE-CWD, which added the `EXEC` check by the same route).

**This document CREATES an invariant for a validator. It retires nothing, widens nothing
and amends no gate threshold.** It **tightens** what `scripts/queue_entry_check.py` will
refuse.

> **REFERRAL, NOT A DECISION — for the chief.** `docs/standards/QUEUE_ENTRY_STANDARD.md`
> enumerates the entry contract. Whether adding a sixth-plus refusal to the validator
> constitutes an **amendment to that standard** — which is **Sanaa's alone** — or a
> tooling ruling of the kind `QUEUE_ENTRY_VALIDATOR_RULINGS.md` already carries, is not
> cfd's call to make for the lab. The `EXEC` check landed by the rulings route and is the
> live precedent. **This spec is written; the code does not land until that is ruled.**

---

## 1. The invariant

**An entry's `team` field MUST equal the team directory it sits in.**

Formally: for an entry file at `verification/queue/<dir>/<CASE_ID>.json` where `<dir>` is
one of the six team directories, `entry["team"] == "<dir>"`. Any other value is a
**validation failure**.

## 2. Why — the defect, measured

The runner does not read `team` when deciding what to launch. It **iterates by directory**:
`list_entries()` at `scripts/queue_runner.py:387-395` walks `for team in TEAMS: d = root /
team` and globs `d.glob("*.json")`, and `tick()` at `:626-634` carries that directory's name
as the team for everything it does — the round-robin cursor, the `LAUNCH_LOG.tsv` row, the
`<team>/launched/` destination.

So an entry declaring `"team": "closure"` dropped into `verification/queue/cfd/` **launches
normally and is recorded as cfd's**. Nothing anywhere catches it: `check_schema`
(`queue_entry_check.py:154-155`) checks only that `team` is *one of the six*, never which
one, and every unrecognised key is ignored (L-348 limb 1).

**Consequence, and why this is worth code rather than a note.** The mislabelled entry
corrupts (a) **verdict ownership** — whose supervisor's §3 check 4 stands behind the run —
and (b) **queue depth per team**, one of the four headline metrics Sanaa named. *A metric
that can be silently wrong is worse than one that is absent*, because a reader relies on it.

## 3. Where it is enforced, and why there and nowhere else

**Enforcement site: `scripts/queue_entry_check.py`, inside the failure list that
`validate()` returns.** Not `load_entry()`, and this is not a stylistic choice — it is
forced by both production call sites:

| call site | code | consequence |
|---|---|---|
| the daemon | `queue_runner.py:633-635` — `entry, fails = qec.load_entry(path)` then `if entry is not None: fails = qec.validate(entry, REPO)` | `validate()`'s list **overwrites** `load_entry()`'s |
| the CLI | `queue_entry_check.py` `main()` — the same two lines | same overwrite |

Today that overwrite is harmless, because `load_entry()` returns `(obj, [])` on every path
where `obj` is not `None` (`:401-412`). **A team-binding failure raised from `load_entry()`
would therefore be silently discarded by both callers.** It goes in `validate()`.

**Enforcement at validation time is the correct outcome shape.** A `team`/directory
mismatch is a **permanent property of the file**, so the entry is **INVALID**, so
`move_refused()` consuming it into `<team>/refused/` is right — the same distinction the
runner already draws in its own words at `queue_runner.py:199-204`: *a resource-busy
condition is a WAIT, never a CONSUMPTION*. A mismatched entry is not waiting for anything.
It will never become valid where it lies.

**Rejected sites, with the reason each was rejected:**

- **Stamping the containing directory onto the entry dict in `load_entry()`** so a
  conventional `(entry, root)` check could read it: rejected on measurement.
  `queue_runner.py:475` does `meta = dict(entry)` and persists it as the launched record —
  a stamped key would be written into every completion record on disk.
- **Enforcing in the runner instead of the validator:** rejected. It would make the
  mismatch a runner-side skip rather than a validator refusal, so `queue_entry_check.py`
  run by hand — the thing a supervisor runs *before* dropping — would still say ACCEPTED.
  The check must fire at the moment it can still prevent the drop.

## 4. What the runner does with it

**Nothing new.** The runner already calls `qec.validate()` every tick and already routes a
non-empty failure list to `move_refused()` (`queue_runner.py:636-639`). A mismatched entry
therefore lands in `<team>/refused/` with `<CASE_ID>.REFUSED.txt` naming the check, on the
first tick after it is dropped — **no change to `queue_runner.py` is required or permitted
by this spec.** The runner keeps iterating by directory; the invariant is what makes that
iteration honest.

## 5. Required properties of the implementation

These are non-negotiable and each is a control in §6.

- **P1 — one failure list.** The check's output reaches both call sites through
  `validate()`'s return value.
- **P2 — a caller that cannot supply the containing directory FAILS LOUDLY.** The
  containing path becomes a **required** parameter, so an existing or future caller that
  omits it raises `TypeError` at the call. It must **never** default to "skip the check".
  A check that silently passes when its input is missing is a zero from a reader not shown
  able to see a non-zero (standing rule 3).
- **P3 — no double-reporting.** The binding check fires only where `SCHEMA` has already
  established that `team` is a string in `TEAMS`. A missing or out-of-roster `team` is
  SCHEMA's refusal and must produce exactly one failure, not two.
- **P4 — the refusal names both sides.** The message prints the declared team and the
  directory, so the fix is obvious from the message alone.
- **P5 — no `assert` carries any of it** (L-332); every refusal is a `raise` or a return
  into the failure list, and `--selftest` keeps its zero-`ast.Assert` property.

**P6 — the out-of-queue case, PROPOSED, NOT DECIDED.** The CLI is documented as runnable on
arbitrary paths (`python3 scripts/queue_entry_check.py <files>`), which is how a supervisor
checks a **draft** that is deliberately *not* in the drop path — the very workflow the cfd
and heat-transfer READMEs now tell lanes to use. Proposal: when the containing directory is
**not** one of the six team directories under the queue root, the check emits an explicit
**`TEAM-BINDING: NOT BOUND (<path> is outside verification/queue/<team>/)`** note in the
verdict and does **not** refuse. The note is printed, never silent — an exemption nobody can
see is a hole. The daemon never reaches this branch, because it only ever validates files it
globbed out of a team directory. **This is the one open design question in this spec and it
is referred to the cfd-supervisor, not taken.**

## 6. Controls — `--selftest`, planted, with mutations that must flip

A guard that has never been shown able to fail is not known to work. Every control below is
planted in a scratch root; nothing real is touched.

| # | control | plant | required outcome |
|---|---|---|---|
| **C1** | **MATCH ACCEPTED** | valid entry, `team: "cfd"`, in `<scratch>/cfd/` | **no** `TEAM-BINDING` failure — guards against a check that refuses everything |
| **C2** | **MISMATCH REFUSED** *(the mandatory planted failure)* | identical entry, `team: "closure"`, in `<scratch>/cfd/` | **REFUSED**; failure string contains `TEAM-BINDING`, `closure` and `cfd` |
| **C3** | **MUTATION OF C2** | `CHECKS["TEAM-BINDING"]` replaced by a no-op, C2 re-run | C2 **FLIPS to accepted**. If it does not flip, C2 never tested the check and the selftest **FAILS** |
| **C4** | **BLIND READER REFUSES** | `validate()` called without the containing path | raises loudly (`TypeError`); **no** silent pass |
| **C5** | **MUTATION OF C4** | the path parameter given a default that skips the check | C4 **FLIPS** — the entry validates clean, proving C4 tested the loudness and not merely the happy path |
| **C6** | **NO DOUBLE REPORT** | entry with `team` **absent**, in `<scratch>/cfd/` | exactly **one** failure mentioning `team`, from `SCHEMA`; no `TEAM-BINDING` failure |
| **C7** | **NOT BOUND IS PRINTED** *(only if §5 P6 is ruled in)* | valid entry in `<scratch>/queue_drafts/` | not refused, **and** the verdict contains `TEAM-BINDING: NOT BOUND` |
| **C8** | **MUTATION OF C7** | the NOT-BOUND note suppressed | C7 **FLIPS** — proving the note is what C7 read, not the absence of a refusal |
| **C9** | **END TO END THROUGH THE DAEMON** | mismatched entry in a scratch queue root, one `tick()` | entry is **moved to `<team>/refused/`**, `REFUSED.txt` written, **nothing launched**, and `LAUNCH_LOG.tsv` unchanged |
| **C10** | **AST SELF-CHECK UNBROKEN** | the instrument parses itself | still **zero** `ast.Assert` nodes (L-332) |

## 7. Blast radius — MEASURED BEFORE ANY CODE EXISTS

Measured 2026-08-27T~19:2xZ by reading every `*.json` in all six drop paths and parsing
`team` out of each. **Not inherited from any report** — L-348 limb 2: a capacity or state
reading has a shelf life and an inherited one is not current.

| directory | live entries in the drop path | mismatched |
|---|---|---|
| `verification/queue/cfd/` | 4 | **0** |
| `verification/queue/heat-transfer/` | 4 | **0** |
| `verification/queue/dafoam/` | 7 | **0** |
| `verification/queue/closure/` | 1 | **0** |
| `verification/queue/ansys-verification/` | 0 | **0** |
| `verification/queue/verification/` | 0 | **0** |
| **total** | **16** | **0** |

Also swept, for information: **88** records under the six `launched/` directories — **0**
mismatched; **0** records under any `refused/` directory (none exists yet).

**Therefore the change refuses nothing that is currently queued, and invalidates no
completed launch.** Had the count been non-zero, the existing mismatched entry would have
been a **finding** — a run whose verdict ownership is already wrong — and not a cleanup.

**RE-MEASUREMENT IS MANDATORY.** This table dates from before the code was written. The
implementing lane **re-runs the sweep in the same shell invocation that lands the code** and
records the fresh count in the commit message. A count that was zero twenty minutes ago is
not a count that is zero now: the drop path is live and every team can write to it.

## 8. What this spec does NOT do

- It does **not** enforce `enqueued_by`, and no future clause here will. Every commit and
  every process on this box shares one Ubuntu identity, so a check comparing `enqueued_by`
  to anything available would return PASS for any string an agent chose to write while
  *looking* like an authorisation control. **`enqueued_by` is a declared, unenforceable
  field — a statement of record, not a credential.** An honest gap beats a control that
  cannot fail.
- It does **not** change `scripts/queue_runner.py`.
- It does **not** touch any other team's queue directory, README or entries.
- It sends nothing anywhere (`CLAUDE.md` rule 7).

---

## AMENDMENT 1 — 2026-08-27, v1.0 → v1.1. Approved by the cfd-supervisor, all four items.

**Appended, never rewritten (`CLAUDE.md` rule 6). Lines whose number changed above this
section: 0.** The header above still reads *"No code exists yet"*; that was true at the
freeze `b23b5638` and is superseded here — the code lands in the same commit as this
amendment.

**The rule-2 condition, and how it was checked.** Amendments before first compute are legal
and must name the condition. **Nothing has run off this spec.** No entry was validated by it,
no solver launched under it, and at the moment of amending, the implementation did not exist
— which is itself the evidence: **the falsification was found BY implementing, before any
code was committed.** Verified by the cfd-supervisor personally, not relayed.

### 1. §4 corrected — one argument at `queue_runner.py:635`, and nothing else

**STRUCK from §4:**
> ~~"no change to `queue_runner.py` is required or permitted by this spec."~~

That sentence is **false and was falsified by its own implementation.** §5 P2 requires
`entry_path` to be a required parameter of `validate()`; the daemon is a caller and is the
only party that knows the path; therefore the daemon must pass it. Three escapes were
examined and each rejected for cause: deriving the path in `load_entry()` (both callers
overwrite its failure list — §3); a module-level "last loaded path" (binds the wrong path the
moment two files are validated); and defaulting `entry_path` to `None` (the silent skip P2
exists to forbid, and it would leave the **daemon** — the one caller that can still be wrong
— as the only caller never checked).

**REPLACED BY, and this is the whole of the permitted edit:** the runner's **behaviour,
mechanism and refusal routing are unchanged**. The single permitted change to
`scripts/queue_runner.py` is **at the `qec.validate()` call, passing the entry path as one
additional argument** — no new branch, no new state, no new call, no other line. Any further
edit to that file is outside this spec and requires its own amendment. *(An amendment that
widens beyond the defect that forced it is how a freeze becomes decorative.)*

### 2. `--require-binding` added

Printed-never-silent is honoured by a human reading a line. `--require-binding` makes the
same condition machine-checkable:

- **Without the flag:** unchanged — rc 0, `NOT CHECKED` printed. The draft workflow is
  untouched.
- **With the flag:** an entry not in a team drop directory is **REFUSED**, non-zero rc.
- **The cfd enqueue procedure uses `--require-binding` on the QUEUED copy, in the team
  directory, after the copy — that run is the validation that counts.** The pre-drop check on
  the case copy remains a draft check and says in terms that it did not check binding.

Two controls added: **C11** (unbound entry refused with the flag, accepted without it) and
**C12** (its mutation — the clause no-opped, which must make C11 fail).

### 3. C7's expected string: `NOT BOUND` → `NOT CHECKED`

**`NOT BOUND` describes the entry's state; `NOT CHECKED` describes the limit of our
knowledge** — and the planted-zero principle is about knowledge, not state. A reader seeing
`NOT BOUND` may reasonably conclude the tool looked and found no binding required. A reader
seeing `NOT CHECKED` cannot. The indented block naming what was not checked, and where it
will be, is kept.

### 4. §5 P6 ruled IN, on the supervisor's reasoning, which supersedes the lane's

The lane's argument was that the daemon never reaches the unbound branch. **The governing
reason is stronger and is recorded as the ruling:** if the CLI refused on a path outside the
six team directories, it would force every lane to **copy first and validate after** — that
is, to validate only once the launch is already armed. That inverts the safe order and
directly contradicts the check-4-before-the-drop wording adopted into the team READMEs. **A
refusal there would turn a safety improvement into a safety regression.** So: rc 0, no
refusal, outside the six directories — with `NOT CHECKED` printed loudly and
`--require-binding` available to make it bite.

### 5. FOUND WHILE IMPLEMENTING, recorded because a control caught it

`containing_team_dir()` recognises the path shape §1 specifies — `.../verification/queue/
<team>/`. **A queue root of any other shape is therefore UNBOUND, silently.** This was not
reasoned: the first draft of control **C9** used a scratch root named `c9root/cfd/`, and the
mismatched entry **LAUNCHED**. C9 now asserts the recognised shape as a precondition so it
cannot pass vacuously.

**Production is unaffected** — `queue_runner.DEFAULT_ROOT` is
`<repo>/verification/queue` and cron passes no `--root`, so every live tick is bound. **The
gap is real but confined to a non-default `--root`**, which today only the runner's own
selftest uses. **Not fixed here, because fixing it means relaxing §1's path shape, which is a
change to the invariant and not to its implementation.** Referred to the cfd-supervisor as a
follow-up: either bind on `parent.name in TEAMS` alone, or have the runner tell the validator
what its root is.
