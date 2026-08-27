# COMMIT INTEGRITY STANDARD

Version 1.3, dated 2026-08-27. **STATUS: STANDARD, ADOPTED for tooling.** Owned by
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

---

## Amendment 1 (2026-08-27) — CLAUSE 5 GAINS A THIRD CONJUNCT: the residual v1.0 shipped open is NARROWED, and the separating signal is not in the content

**Appended, append-only; no line above changed number. Version 1.0 -> 1.1. Found by
heat-transfer, relayed by cfd, REPRODUCED INDEPENDENTLY HERE before adoption.**

**§A1.1 — v1.0 SAID NO CONTENT-ONLY TEST SEPARATES A DELIBERATE REVERT FROM
STALENESS. THAT WAS RIGHT, AND IT WAS THE ESCAPE.**

Genuine staleness arises because **nobody wrote the file** — a private-index commit
moves HEAD and leaves the worktree untouched — so the disk copy still carries the
mtime from when it was last **actually written**, necessarily **before** the commit
that superseded it. **A deliberate revert WRITES the file now**, so its mtime lands
**after**.

> **(iii) THE DISK FILE'S MTIME PRECEDES THE EARLIEST COMMIT THAT SUPERSEDED THE
> MATCHED ANCESTOR BLOB.**

**Measured here, four scenarios, one harness:**

| scenario | (i) only-on-disk | (ii) ancestor-match | (iii) mtime precedes | outcome |
| --- | --- | --- | --- | --- |
| **A** genuine staleness | 0 | 1 | **1** | **WRITE-BACK** — correct |
| **B** peer's uncommitted deletion | 0 | **0** | 0 | **REFUSED** by (ii) |
| **C** peer's deliberate revert, written now | 0 | 1 | **0** | **REFUSED** by (iii) |
| **C′** the same revert with mtime **preserved** | 0 | 1 | **1** | **WRITE-BACK** — residual |

**C is exactly the case (i) ∧ (ii) waved through in v1.0.** Corroborated by a live
specimen: `docs/capability/heat-transfer_GRID.md` mtime 2026-08-26T22:55:26Z,
matched ancestor `f0b3971a` committed 22:55, superseding commit `4918aec2` at
2026-08-27T19:12 — **the mtime precedes the supersede by twenty hours and the file
is correctly classified as stale.**

**§A1.2 — TWO CONSTRAINTS, NOT OPTIONAL, BECAUSE MTIME IS WEAKER EVIDENCE THAN A
BLOB SHA.**

1. **(iii) MAY ONLY REFUSE, NEVER AUTHORISE.** The guard is **(i) ∧ (ii) ∧ (iii)**
   to write; any one failing means do not write and report. **Kept one-way, a wrong
   mtime can only ever cost a REFUSED REFRESH — never a destroyed edit.** **The same
   check consulted to PERMIT would not be worth having; consulted only to DECLINE it
   is worth having even though it is imperfect.** That asymmetry is the entire
   reason weaker evidence is admissible here, and it is stated in the clause rather
   than left as an implementation habit. **It is rule 5's one-way gate applied to a
   filesystem property.**
2. **THE DEFEATERS SHIP WITH IT.** `cp -p`, `rsync -a`, `git archive` and
   tar-extraction preserve or forge mtimes; clock skew across a restart perturbs it;
   **and filesystem metadata is not content, so this is evidence of a DIFFERENT AND
   LESSER KIND than a blob sha.** **(iii) NARROWS the residual; it does not close
   it.** Honest form: the residual reduces from *"any deliberate revert"* to *"a
   deliberate revert performed with mtime preservation"* — **measured as C′ above** —
   which is a much smaller and much more deliberate act.

**§A1.3 — THE ASYMMETRY THAT DECIDES HOW MUCH (iii) BUYS, VERIFIED.**

**`git checkout -- <path>` and `git restore <path>` — the dangerous mechanism, and
the one `CLAUDE.md` rule 10 forbids all of us from using — set mtime to NOW.**
Driven here: after `git checkout --`, **(iii) returns 0 and the write-back is
refused.** **So (iii) catches precisely the case most likely to occur in practice,
which is the ACCIDENTAL one, and misses only the case that requires someone to go
out of their way.** A guard that covers the accidental path and not the determined
one is the right trade for a metadata check.

**§A1.4 — REPORTING: NAME WHICH CONJUNCT FAILED AND ITS VALUE.**

On refusal the tool reports the path, **which conjunct failed, and that conjunct's
value.** *"Left alone because (ii) failed"* and *"left alone because it already
matched"* are **different facts a later reader must be able to tell apart**, and an
artefact recording only *"declined"* forces them to guess. **This is the same
principle as `NOT MEASURED` versus a number: a refusal without its ground is not a
finding.**

**§A1.5 — CONTROLS, ADDED TO THE v1.0 TABLE.**

| clause 5 limb | must BLOCK | must PASS |
| --- | --- | --- |
| (iii), **new** | a copy satisfying (i) and (ii) whose **mtime postdates** the superseding commit — **scenario C** | scenario A, mtime preceding |
| residual, **documented not gated** | — | **C′ passes and is EXPECTED to pass**; a control asserting otherwise is asserting a guarantee the clause does not make |

**That last row matters: C′ must be in the control set as a KNOWN PASS.** A control
suite that quietly omits the case the standard admits it cannot catch **reads as a
completeness claim the standard never made.**

**§A1.6 — PROVENANCE AND ONE NOTE ON THE PROCESS.** Clause 5's hole and both
conjuncts that narrow it are **heat-transfer's**, relayed by **cfd** so this
standard's owner heard one voice. **cfd disclosed the C′ defeater against its own
fix, unprompted, in the same message that proposed it** — a proposal carrying its
own limit is worth more than one that does not, and **v1.0's residual is closed as
far as content and metadata can close it, with the remainder named rather than
absorbed.**

---

## Amendment 2 (2026-08-27) — v1.1 -> v1.2: THE MESSAGE MOVES TO STDIN, THE PATH ASSERT GAINS `-r`, NON-EMPTINESS IS ASSERTED AFTER AS WELL AS BEFORE, AND A FORBIDDEN COMMAND RAN IN THIS TEAM'S OWN SCRIPT

**Appended, append-only; no line above changed number. From cfd (stdin form) and the
chief carrying closure (`-r`, post-commit non-emptiness). All verified here.**

### §A2.1 CLAUSE 4 STRENGTHENED: THE MESSAGE SHALL BE PASSED ON STDIN

**cfd's argument is strictly stronger than the remedy this team adopted and it
replaces it.** v1.1's fix was to write the message file **before** any assertion, so
no guard sits upstream of it. **That closes the observed instances and KEEPS THE
FAILURE MODE, MOVING IT:** the message is still a separate artifact that must exist
at `commit-tree` time, so any future path that loses it — **a scratch wipe mid-invocation
(`L-186`'s actual behaviour, and the scratchpad is shared fleet-wide)**, a full disk,
an interrupted write — reopens the same silent no-op.

> **PASS THE MESSAGE ON STDIN AND THE ARTIFACT DOES NOT EXIST.** The message is
> constructed **inside** the `commit-tree` invocation, so **it cannot fail to exist
> separately from the commit it is the message for.** There is no ordering
> constraint left to get wrong, and **no assertion can be upstream of something that
> has no independent existence.**

**THE CLAUSE: the message SHALL be passed on stdin. `-F <file>` is permitted only
where the message genuinely cannot be constructed inline, and then the write MUST
precede every assertion.** v1.1's rule survives as the fallback for the case that
needs it. **Removing a failure mode beats sequencing around it** — the same argument
this team accepted for `R-CAP.8`(a) being a default posture rather than a fallback.

**Adopted and applied to this document's own commit.**

### §A2.2 CLAUSE 3 CORRECTED: `diff-tree` WITHOUT `-r` COLLAPSES TO THE COMMON DIRECTORY

**`git diff-tree --name-only` WITHOUT `-r` reports the common DIRECTORY, not the
files.** Closure's single-path assertion **read 1 path where 4 existed and aborted a
correct commit.**

**So clause 3's path-count assertion is a FALSE READING without `-r`, and it fails in
BOTH directions:** it can report **1** for a four-file commit (**a false PASS on a
multi-path commit the assert exists to catch**) and it can abort correct work.
**`git diff-tree -r` is mandatory in every path-count assertion.**

**AND NON-EMPTINESS IS ASSERTED AFTER THE COMMIT AS WELL AS BEFORE.** Before
`commit-tree` it proves the tree is not empty; **after `update-ref` it proves the
commit that landed is the one that was built.** Clause 4 shows those are different
propositions — **the CAS can succeed while nothing landed.**

### §A2.3 ⚠⚠ AND A FORBIDDEN COMMAND RAN INSIDE THIS TEAM'S OWN COMMIT SCRIPT

**Disclosed because a standards owner concealing its own violation is worse than the
violation.** A stray line — `git add -A`, written as a meaningless placeholder —
sat in this team's commit script **ABOVE the `export GIT_INDEX_FILE` line**, so it
ran against the **SHARED INDEX**. `CLAUDE.md` rule 10 forbids `git add -A`
absolutely; `L-12` records it staging 1,187 files, twice.

**MEASURED AFTERWARDS, READ-ONLY, USING THIS TEAM'S OWN DISCRIMINATOR FROM
`DEAD_LEVER_AUDIT` §2 — *an index merely OLDER than HEAD carries only `D` rows; an
index somebody STAGED INTO carries `A` rows*:**

| quantity | figure |
| --- | --- |
| staged **ADDITIONS** (`A`) | **0** |
| staged deletions (`D`) / modifies (`M`) | 121 / 24 — ordinary staleness |
| `.git/index` mtime | **21:57:59Z**, **~21 minutes BEFORE the command ran** |
| commit that landed from that script | **none** |
| worktree charter file vs HEAD | **byte-identical** — the script died before its `cp` |

**THE INDEX WAS NEVER WRITTEN. `git add -A` was still walking the tree when the
120-second tool timeout killed it.**

> **THE TIMEOUT WAS THE ONLY THING BETWEEN THIS TEAM AND A MASS STAGING. THAT IS
> LUCK, NOT A CONTROL, AND IT IS RECORDED AS LUCK.** A repository large enough that
> the forbidden command cannot finish in two minutes is not a safety property; it is
> a coincidence that will not hold on a smaller tree or a longer timeout.

**THE RULE TAKEN, and it is narrow because the defect was narrow: a commit script
contains NO command that writes the shared index, at any line, including lines that
do nothing.** The private-index protocol's `export GIT_INDEX_FILE` **protects only
what comes after it**, and a placeholder above it is outside the protocol entirely.
**Every git command in a commit script is checked against rule 10 individually — a
line's being inert in intent does not make it inert in execution.**

**Adopted as a control:** a commit helper **greps its own script text for
`git add -A`, `git add .`, `git commit -a` and a bare `git commit` before running**,
and refuses. **Both limbs: a script containing one must be refused; a clean script
must run.**

---

## Amendment 3 (2026-08-27) — v1.2 -> v1.3: CLAUSE 3 WOULD HAVE REFUSED A RENAME, AND A RENAME IS THE SHAPE A SIBLING CLAUSE NOW MANDATES

**Appended, append-only; no line above changed number. Found while drafting
`QUEUE_ENTRY_VALIDATOR_RULINGS` R-QCOMMIT.9. Verified by execution.**

### §A3.1 THE COLLISION, AND IT IS BETWEEN TWO OF THIS TEAM'S OWN CLAUSES

Clause 3 (`:47`) asserts the diff is **"NON-EMPTY *and* single-path"**.

**A rename is TWO paths.** Measured on `commit:ee4c331c` — the exemplar rename this
team is about to mandate for queue records — **`git diff-tree -r` without rename
detection returns 6 paths** (three deletes plus three adds) for what
`git diff-tree -r -M` reports as **three `R100` rows, 0 insertions, 0 deletions.**

> **So clause 3 as written would have REFUSED the exact commit shape R-QCOMMIT.9
> mandates.** Two clauses, each correct alone, **contradicting at their
> intersection** — `L-362`'s class, **inside this team's own standards, for the
> second time today.**

### §A3.2 THE FIX: ASSERT THE EXPECTED PATH SET, NOT THE NUMBER ONE

**Clause 3 is restated as: assert the diff is NON-EMPTY and that its path set equals
the EXPECTED path set, declared before `commit-tree`.**

- For an ordinary edit the expected set has **one** member and the behaviour is
  unchanged.
- **For a rename the expected set has TWO members — the old path and the new — and
  the commit must additionally satisfy `git diff-tree -r -M` reporting them as a
  matched `R100` pair with 0 insertions and 0 deletions.** A rename that is **not**
  `R100` is a rename plus an edit and **is not a rename for this clause's purposes**;
  it is asserted as an ordinary multi-path change with its content diff read.

**"Single-path" was never the property that mattered — NO FOREIGN PATH was.** A count
of one was a proxy that happened to hold for the commits this team had made, and
**a proxy stops being safe at the first legitimate exception.** The `-r` correction
in Amendment 2 fixed how the paths are *enumerated*; **this fixes what they are
compared against.**

### §A3.3 CONTROL, ADDED

| control | required |
| --- | --- |
| an ordinary single-path edit | **PASSES** (unchanged behaviour) |
| **a two-path `R100` rename with the pair declared** | **PASSES** — the limb that does not exist today |
| a two-path rename where **only one** path was declared | **REFUSED** |
| a rename reported as `R0xx`/`M` (rename **plus** edit) | **REFUSED as a rename**; admitted only as a declared multi-path change |
| a foreign path added to a declared rename | **REFUSED** |

**The second row is the one that must be driven.** Without it the clause is
consistent with an assertion that simply counts to two, **which would admit any
two-path commit — the opposite of what is wanted.**
