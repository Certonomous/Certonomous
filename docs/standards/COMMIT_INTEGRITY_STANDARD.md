# COMMIT INTEGRITY STANDARD

Version 1.0, dated 2026-08-27. **STATUS: STANDARD, ADOPTED for tooling.** Owned by
the verification team. Written on cfd's referral, carrying heat-transfer's finding.

**SCOPE, and it is the first thing a reader must have.** These five clauses are a
specification for **commit HELPER TOOLING**. They **do NOT amend `CLAUDE.md` rule
10** — rule 10's wording is Sanaa's, and clause 4 below is a **measured defect IN
it** which sits on her desk as recommended-and-not-adopted. Implement these as
behaviour **strictly stronger** than rule 10 and never in tension with it. **Where
a clause here would refuse something rule 10 permits, that is a referral to the
verification team and not a judgement call inside the tooling.**

**Why this document exists.** Every clause below was paid for by a measured
failure **this day**, most of them by the teams that then reported them. None is a
precaution.

---

## Clause 1 — SOURCE: build from the HEAD blob, in the same invocation

New content is built from **`git show HEAD:<path>`** captured in the **same shell
invocation** as the commit. **Never from the worktree copy.**

**Ground.** Under the private-index protocol the worktree is behind HEAD **most of
the time, by design** — `commit-tree` and `update-ref` advance the branch and never
touch `.git/index` or the working copy. An append built from disk therefore deletes
every row a peer landed since the worktree last matched HEAD. `L-381`.

**And the invocation matters for a second reason:** shell environment does **not**
persist between an agent's Bash calls, so a protocol split across two calls runs
its git commands against the **shared** index.

## Clause 2 — DELETIONS ASSERTED AS A NUMBER, BEFORE AND AFTER

Assert **`deletions == 0`** numerically before `commit-tree` **and again** after
`update-ref`. Not by reading a stat line.

**THE HAZARD IS PLAUSIBILITY, NOT INVISIBILITY.** The post-commit stat *does* show
the loss — measured instances read `+1/−37`, `+1/−39`, `+3/−2`. **`+3/−2` and
`+1/−1` read as an ordinary edit, and a human reviewing a stat line passes them.**
A numeric assertion cannot be persuaded by plausibility. This is what actually
saved `C-185`.

## Clause 3 — NON-EMPTY, SINGLE-PATH

Assert the diff is **NON-EMPTY** *and* single-path **before** `commit-tree`.

**Ground.** An empty tree passes a foreign-path check trivially, and
`git diff-tree --stat` **prints nothing** for an empty diff — which reads exactly
like a clean run. The one diff that must never commit is the one the guard cannot
see. `L-379`.

## Clause 4 — THE SHA IS ASSERTED AND THE ARGUMENTS ARE QUOTED

Require the new commit sha to match **`^[0-9a-f]{40}$`** before `update-ref`,
**and QUOTE both arguments**: `git update-ref refs/heads/main "$C" "$H"`.
**Pass commit messages by STDIN rather than `-F <path>`.**

**Ground, measured in a throwaway repository.** `C=$(git commit-tree … -F msg)`
returns **empty** whenever `commit-tree` fails — a missing message file, a killed
process, a full disk. The protocol's own line
`git update-ref refs/heads/main $C $H` then **collapses, unquoted, to the
two-argument form `git update-ref refs/heads/main <H>`, WHICH SUCCEEDS AS A
NO-OP**:

- **`CAS OK` prints.**
- **HEAD is unchanged.**
- **The mandated post-commit `git diff HEAD~1 HEAD --stat` prints the PREVIOUS
  commit's diff** — one file, one insertion — **reading exactly like a successful
  landing.**

**All three of rule 10's success signals fire on a commit that never happened.**
`L-382`. **Either fix alone is sufficient; take both** — the quoting is free and
the assertion says why.

**Two instances, both from agents who thought they were careful.** The verification
team's own assertion **fired on its own commit**, two minutes after being written,
because an earlier guard in the same script exited before the heredoc writing the
message had run. The cfd team used the unquoted form in **four** commits this
session and was saved by an `|| exit` it **happened to have** rather than by
anything the protocol required. **Every long commit script has that shape.**

## Clause 5 — WRITE-BACK: BOTH CONJUNCTS, AND (ii) IS THE ONE THAT MATTERS

Before writing a committed blob back to the worktree, require **BOTH**:

- **(i)** lines present **ONLY ON DISK**, relative to the new HEAD content, **== 0**; **and**
- **(ii)** the **disk blob matches some blob that PATH held at an earlier commit**.

If either fails: **DO NOT WRITE. Report the path and the count, and stop.**
`CLAUDE.md` rule 10 already settles the rest — an unexpected change is
**INSPECTED, NEVER REVERTED**, and a peer's uncommitted work is not the
committer's to resolve.

**WHY (i) ALONE IS NOT ENOUGH — demonstrated, not argued.** Reproduced
independently by the verification team in a throwaway repository, driving all three
limbs:

| scenario | (i) only-on-disk | (ii) matches an ancestor blob | verdict |
| --- | --- | --- | --- |
| **A — genuine staleness**, disk holds an earlier committed state | **0** | **1** | write back; safe |
| **B — a peer's UNCOMMITTED DELETION**, disk = HEAD minus a line they removed | **0** | **0** | **BLOCK** |
| **C — a peer's uncommitted deliberate REVERT** | **0** | **1** | writes back — **known residual** |

**In scenario B the peer ADDED nothing, so (i) is 0, the guard passes, and the
write-back SILENTLY RESTORES THE LINE THEY DELETED. The deletion IS their work.**
By content alone it is indistinguishable from ordinary staleness.

**(ii) is what separates STALENESS from LOCAL EDITING.** A stale copy is *by
definition* a state the file genuinely held at an earlier commit, so it matches a
historical blob byte-for-byte. **A locally-edited copy — including one edited only
by DELETION — matches none.**

**Implementation, kept cheap:** hash the disk copy once with `git hash-object`,
then walk **`git rev-list --all -- <path>`** — bounded by commits touching that
path, not by all history — newest-first, comparing `git rev-parse <rev>:<path>`,
and stop at the first match.

**KNOWN RESIDUAL, NAMED HERE RATHER THAN DISCOVERED LATER BY SOMEONE IT BITES.**
Scenario C — a peer who deliberately reverts a file to an older committed state and
has not yet committed that revert — **passes both conjuncts, and the write-back
undoes them.** Confirmed byte-identical to scenario A in reproduction: **there is
no content-only test that separates "reverted deliberately" from "stale". Only the
peer knows.** Judged acceptable because it is far rarer than the deletion case, and
**stated as a limit of the clause rather than as an argument against it.**

**AND THE PRINCIPLE UNDER BOTH CONJUNCTS.** This guard makes the loss-free
precondition an **EXECUTED CHECK** rather than a property of how carefully the
paths were chosen. A 21-path refresh was called loss-free this day because a
careful reader saw a pure-deletion diff. **That judgement was correct and a careful
reader is not a control.** **(ii) is the half that was doing the work in that
judgement all along.**

---

## Two general rules these clauses depend on

**G1 — DO NOT RELAX AN INVARIANT TO MAKE A TEST PASS; MAKE THE TEST EXERCISE WHAT
PRODUCTION DOES.** Every clause above ships with a planted failure that drives
**the path production takes**. A control whose scenario uses a root shape or an
entry point production never takes **has not tested the clause**. Same family as a
plant taken from the search rather than from the artefact (`L-363`), and this is
the sharper statement because it names the tempting repair.

**G2 — `HEAD~1` IS REFUSED OUTRIGHT** in any before/after comparison. Anchor on the
commit's true parent, **`git rev-parse <sha>^`**.

**Ground.** Five peer commits landed underneath a lane; `HEAD~1` was already the
amended blob; **the lane compared a file with itself and got a confident,
meaningless match.** In this repository `HEAD~1` is a moving target and a check
anchored on it **silently becomes a tautology**. **Clause 4's lying post-commit
verify is the SAME FAILURE** — it is `git diff HEAD~1 HEAD --stat` reporting a
landing that did not happen. **Two symptoms, one cause.**

---

## Controls required before any clause gates anything

**Both limbs on each, per `VERIFICATION_CHARTER` v1.13. A guard shown only to
reject is not shown to discriminate.**

| clause | must BLOCK | must PASS |
| --- | --- | --- |
| 2 | a stale disk copy missing a peer's row, naming the count | a current copy |
| 3 | an empty tree | a genuine single-path diff |
| 4 | an empty sha — **driven by actually removing the message file**, because that is how production reaches it, never by assigning `C=""` | a real 40-hex sha |
| 5 | only-on-disk > 0, naming the count | a copy satisfying **both** conjuncts, verified byte-identical after write-back |
| **5 (new limb, and the one that matters)** | **only-on-disk == 0 but matching NO ancestor blob** | — |

## Provenance

Clause 4 and the `L-382` measurement: verification. Clause 5's guarded form and
G1/G2: cfd. **Clause 5's hole and the (ii) conjunct that closes it: heat-transfer**,
relayed by cfd so the standard's owner heard one voice — **that arrangement is
noted because it worked.** Reproduced independently by verification before adoption.

The tooling is cfd's to implement. **The diff comes to the verification supervisor
before it gates anything, and that read is not delegated** (`SUPERVISION_CHARTER`
§3 check 1: an instrument change without a supervisor's read is an uncalibrated
instrument).
