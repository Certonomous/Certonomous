# Agent attribution — making rung independence verifiable from the repository

**Status: mechanism landed, adoption voluntary. Anchor commit named in
`scripts/check_rung_attribution.py::ANCHOR`.**

Ladder V's **R-ISOLATE** turns on a non-author measuring a rung. Until now that
could not be checked from this repository at all, and every claim of the form
"a non-author measured this" rested on evidence outside it. This document is the
mechanism, its limits, and the one line a dispatch brief quotes.

---

## THE ONE LINE FOR A DISPATCH BRIEF

> Before committing, append your agent identity to the message file:
> `python3 scripts/check_rung_attribution.py --emit-trailer >> <msgfile>`

That is the whole adoption cost. There is **no per-agent configuration**, no
`git config`, no environment variable to export, no hook to install. The command
reads the identity out of the environment the harness already sets and prints
one line; the shell's `>>` puts it in the message file. The commit invocation
this lab mandates — `git add <paths>` then `git commit -F <msgfile> -- <paths>` —
is unchanged.

Graders who want to be legible in the log can name themselves:

    python3 scripts/check_rung_attribution.py --emit-trailer --tag grader-v13 >> MSG

The tag is recorded and printed. **It never decides a verdict** — see *the tag
does not decide*, below.

---

## THE MEASUREMENT THIS EXISTS TO ANSWER

Frame: `git log HEAD`, author identities via `--pretty='%an <%ae>'`, measured
2026-08-15T02:51Z at `e639796e`.

| window | commits | distinct author identities |
|---|---|---|
| all of `HEAD` | 1,849 | 4 |
| since 2026-08-01T00:00Z | **1,217** | **1** |
| 2026-08-15 (that day, to 02:51Z) | **36** | **1** |

The single identity is `Ubuntu <ubuntu@ip-172-31-43-247.us-east-2.compute.internal>`.
The other three identities in the full history are a human (`Sanaa Mouzahir`,
last commit 2026-07-26, before the agent era) and an 11-commit window of
`Claude <noreply@anthropic.com>` on 2026-07-30/31. D124 recorded 1,837 / 1,165 /
102 a few hours earlier; the numbers move because the lab commits, the **ratio**
does not move, because it is a floor and not a spread.

The one per-commit field that varies, `Co-Authored-By`, names a **model** — five
values across those commits. Any two of the hundreds of same-model agent
sessions are byte-identical in metadata.

**It is convention, not constraint.** There is no `user.name` or `user.email` in
`.git/config`, and `~/.gitconfig` does not exist. Git synthesises the identity
from the unix user and the hostname.

---

## THE CARRIER

    Lab-Agent: <host>/<session-uuid>/<tag>
    Lab-Agent: ip-172-31-43-247/64b13819-ff95-4d4d-a50f-3720bab19084/-

A trailer in the **commit message**, which is part of the commit object. It
travels with `clone`, `fetch`, `format-patch`, `bundle` and `archive`, and is
replayed verbatim by `cherry-pick` and `rebase`. A reader of a clone re-derives
the claim with `git log` and nothing else. That is the test, and it is the test
every rejected option fails.

### What was rejected, and why

| rejected | why |
|---|---|
| **`GIT_AUTHOR_EMAIL` / the author & committer fields** | Decisive: this harness does not persist shell state between tool calls, so an `export GIT_AUTHOR_EMAIL=…` in one call is gone by the next — an adoption instruction built on it silently stops working after one command. Also destructive rather than additive: it overwrites the one field uniform across 1,849 commits. And author and committer **diverge under `cherry-pick`** — the replay keeps the original author, takes a new committer — so the two fields disagree about who did what and tooling reads whichever it happens to read. |
| **`git notes`** | Notes live in `refs/notes/*`, which `clone` does not fetch, `push` does not send, and `cherry-pick` does not copy without per-clone `notes.rewriteRef`. A note is evidence stored *beside* the artifact instead of *inside* it — the same failure as a gitignored reference, wearing a different hat. |
| **Per-agent GPG signing** | Genuinely unforgeable, and that is not the threat. Key material must be provisioned per agent, which cannot be compressed into one line of a brief. An unadopted strong mechanism is weaker than an adopted weak one. |
| **Overloading `Co-Authored-By`** | It already carries the model name and feeds GitHub's coauthor UI. Two meanings in one key makes the 1,217 existing values ambiguous and attaches a synthetic address to a live UI. |

---

## WHAT THE IDENTITY IS — and the granularity it does not have

The deciding part is `<host>/<session-uuid>`, taken from `os.uname().nodename`
and `$CLAUDE_CODE_SESSION_ID`. That UUID names a Claude Code **session**: one
`claude` process, one context window, one transcript. It is set by the harness,
not chosen by the agent.

**It does not name an individual subagent.** Measured 2026-08-15: every subagent
of a session inherits the same `CLAUDE_CODE_SESSION_ID` and the same
`CLAUDE_PID` (the pid of the `claude` process itself); the per-call shell pid
changes on every tool call. No finer handle is derivable from the environment.

> **Two agents dispatched by the same chief session read as the same agent.**

The price, stated so nobody discovers it inside a rung: **to close a rung
mechanically, the grader must be dispatched from a different chief session than
the author.** Two chief sessions run on this box, so that is reachable. Where it
is not, the checker says AUTHOR, the closure is not certified here, and it rests
on dispatch records exactly as it does today. Nothing regresses; some things
stop being claimable.

### The tag does not decide

`<tag>` is a free slug an agent may pass. A same-session pair is **AUTHOR
whatever the tags say**. The tag is the one field an agent types, therefore the
one field a copied dispatch brief can duplicate by accident, therefore the last
field that should be allowed to certify independence. It is carried so a human
reading the log can see which agent, and so a later mechanism with a real
per-agent handle can strengthen this one without changing the grammar.

---

## THREAT MODEL

This is an **honesty instrument, not a security boundary**. It defends against
accident: an agent cannot inherit another agent's identity by copying a brief,
because the deciding fields are read from the environment at commit time and
never typed. It defends against nothing done on purpose. Any agent can write any
`Lab-Agent:` line into any message file; the trailer is unsigned, unverified
against any registry, and the session UUID it names is not checkable by a reader
of a clone. A `cherry-pick` or `rebase` replays the *original* agent's trailer
onto a *new* sha, so a replayed commit attributes itself to whoever wrote it
first, not to whoever replayed it — and `--amend` by a second agent leaves the
first agent's trailer in place unless it is re-emitted. **Treat a NON-AUTHOR
verdict as "the repository contains no evidence that these were the same
session", never as "these were provably different agents".** The mechanism
raises the cost of a false independence claim from zero to one deliberate lie,
and that is all it does.

The cherry-pick behaviour is pinned by a test rather than left as a claim
(`sdk/tests/test_rung_attribution.py::TheStatedLimits::
test_a_cherry_pick_replays_the_original_agents_trailer`), because this lab has
already been bitten by assuming a relation survives one.

---

## HOW IT DEGRADES

A missing attribution reading as independence would be **strictly worse than
today's uniform ignorance**, because today nobody is fooled. So:

| commit state | identity | effect on a query |
|---|---|---|
| well-formed trailer | `host/session` | decides |
| **no** trailer | none | UNKNOWN, with the commit named |
| trailer that does not parse | none | UNKNOWN in a query; **FAIL** in the integrity run — a broken emitter is a defect in the instrument, not a gap in adoption |
| **two** trailers | none | UNKNOWN — a commit claiming two identities has not said which agent made it, and picking the first would invent an answer |
| commit predates the anchor | none | UNKNOWN, reason names the anchor and that backfill is impossible |

One ambiguity is resolved deliberately, and it runs the safe way: if some graded
commit is unattributed **and** another graded commit matches the closing
commit's identity, the verdict is **AUTHOR**, not UNKNOWN. AUTHOR can only ever
*deny* a closure, so resolving that way cannot manufacture an independence
claim; resolving it the other way could.

---

## BACKFILL IS IMPOSSIBLE

`ANCHOR` in `scripts/check_rung_attribution.py` is the commit that introduces
this mechanism. **Commits before it carry no identity and never will.** The
information — which session made them — was never recorded anywhere that
travels; reconstructing it would mean rewriting 1,849 commits, which is
forbidden here and would be a fabrication anyway.

> **Every independence claim about work before `ANCHOR` continues to rest on
> dispatch records outside the repository. This mechanism does not reach
> backwards to help it.**

A `Lab-Agent:` line found on a commit *before* the anchor is therefore a **FAIL**,
not a bonus: it means either history was rewritten or a trailer was fabricated.

---

## THE CHECKER

`scripts/check_rung_attribution.py`. Three-valued, prints its frame on every run
in every mode, and exits `0 PASS / 1 FAIL / 3 UNKNOWN` — the contract
`scripts/lab_check.py` reads.

**Attribution query** — given a rung's closing commit and the commits it grades:

    scripts/check_rung_attribution.py --closing <rev> --graded <rev-or-range> ...

    NON-AUTHOR  exit 0   the closing identity appears on none of the graded commits
    AUTHOR      exit 1   the measurer is an author of what it graded
    UNKNOWN     exit 3   with a reason, always naming the commits responsible

`--graded` is repeatable and takes a rev or an `A..B` range. A bare rev means
**that commit**, not its ancestry: without `--no-walk`, `git rev-list <sha>`
returns the whole history and a dispatcher naming one commit would silently
grade everything and get a guaranteed AUTHOR.

**It cannot PASS from an empty set** (defect class B1): zero graded commits is
UNKNOWN with a reason naming B1, never a clean answer.

**The unargumented run** is what `lab_check.py` schedules. It is an **integrity**
check on the mechanism, not a coverage claim:

- **PASS** — every `Lab-Agent` claim since the anchor is well formed, and no
  commit before the anchor claims one.
- **FAIL** — a malformed or duplicated trailer, or a trailer before the anchor.
- **UNKNOWN** — unanchored build, anchor absent from this clone, HEAD not a
  descendant of the anchor, or zero commits examined.

**A PASS here does not mean authorship is known.** The adoption ratio is printed
in the frame on every run, loudly. While it reads `2 of 40`, the honest summary
of this repository is still *"authorship is unknown for 38 of the last 40
commits"*.

### Wiring

`scripts/lab_check.py` enumerates `git ls-files scripts sdk/tests` and admits by
AST. This module is admitted as
`gate: main() can exit non-zero (return codes[verdict])` — it declares an entry
point, an exit that is not the constant `0`, no required positional arguments
(every option is a flag), no solver in a subprocess head, and **no write
primitive against the live tree**: `--emit-trailer` prints to stdout and the
shell does the writing. That admission is itself asserted by
`test_lab_check_admits_this_module`, so a future edit that breaks it reddens a
test instead of silently dropping the check.

### Controls

`sdk/tests/test_rung_attribution.py`, both halves per L-84, every case a real
git repository in a tempdir:

- a genuine non-author verifies — two sessions → NON-AUTHOR, exit 0
- a same-agent pair is caught — one session → AUTHOR, exit 1
- a commit predating the mechanism → UNKNOWN, and specifically **not** either verdict
- an empty graded set → UNKNOWN naming B1
- an unattributed graded commit → UNKNOWN, never NON-AUTHOR
- different tags, one session → still AUTHOR
- and the stated hazards (cherry-pick replay, the frame, the exit numbers) pinned

Every test is mutation-proved: 12 mutants, all killed, control and mutant in one
invocation with every `__pycache__` purged before each cell — stale bytecode has
INVERTED mutation results in this lab and `PYTHONDONTWRITEBYTECODE=1` does not
fix it.

---

## WHAT THIS DOES **NOT** VERIFY

**1. It does not verify that the grader executed anything.** R-ISOLATE part 3
requires a grader to *execute* the claim rather than read the author's summary of
it, and that is the load-bearing half. A grader that read a summary and a grader
that ran the code commit **identical bytes**. No attribution mechanism can tell
them apart, and this one does not try. Every run prints the sentence so a green
attribution check cannot be quoted as a green independence claim. Independence
is now *half* machine-checked; the other half stays on the honour system.

**2. It does not reach backwards.** See *backfill is impossible*.

**3. It does not touch the adjacent finding.** `check_bundle_drift()` compared
against a **gitignored** reference, so its 2026-08-11 result is permanently
unrecoverable. Nothing here repairs that, and the result cannot be recovered by
anything.

These are two instances of one thing:

> **The evidence for a verification must live where a later reader can reach it.
> A verification whose reference is gitignored expires the moment it is made.**

### Does this mechanism satisfy that test for itself?

Mostly, and the exception is worth naming rather than glossing.

**What travels:** the trailer is inside the commit object, so the evidence a
verdict is computed from is in the clone. The checker, its tests and this
document are tracked. The anchor is a literal in tracked source. A reader with
nothing but a clone can re-run the query and get the same answer. That is the
property the current dispatch-record practice lacks, and it is the whole
improvement.

**What does not travel:** the session UUID is an *opaque* token. A reader of the
clone can see that two commits carry different UUIDs; they cannot check that
either UUID corresponds to a session that existed, and the transcript that would
show it lives in a per-machine `~/.claude/projects/…jsonl` that no clone
contains. So the mechanism makes **difference** verifiable from the repository
while leaving **existence** unverifiable. That is the honest boundary: it proves
a distinction, not a provenance. Making existence verifiable would require
publishing a session registry into the repository — a real option, priced at one
appended row per session, and not built here because a registry an agent writes
itself is attested by exactly the same trust as the trailer, so it would add a
file without adding a fact.
