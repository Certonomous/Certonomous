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

---

## Amendment 4 (2026-08-30) — v1.3 -> v1.4: CLAUSE 2's "AND AGAIN AFTER" IS TAUTOLOGICAL FOR AN OBJECT-BASED HELPER, AND WRITING IT ANYWAY PLANTS THE DEFECT THIS STANDARD EXISTS TO REMOVE

**Appended at the foot, append-only. Nothing above is edited, struck, widened or narrowed.
`lines whose number changed above this section: 0`.** Raised as a **referral** by a verification
lane auditing `cases/RANS_LES_closure_models/_common/commit_private.sh`, and **ruled here by the
standard's owner**. The lane declined to write the assertion and said why rather than quietly
skipping it; **that was the right call and this amendment ratifies it, with one correction to its
reasoning.**

### §A4.1 THE REFERRAL, AND THE HALF OF IT THAT IS RIGHT

Clause 2 requires `deletions == 0` asserted numerically **before `commit-tree`** *and again* after
`update-ref`. A helper that performs its post-landing verify over **`$OLD..$NEW`** — its own two
commit objects — **cannot fail the second assertion.** A commit object is content-addressed and
**immutable**: `$NEW`'s tree cannot have become a different tree between `commit-tree` and the
line after `update-ref`, so the second count compares **the same two trees** as the first and is
**tautologically equal**.

**The lane is right, and the consequence is sharper than "harmless duplication":** written as an
`if`, it is **AN ASSERTION THAT CANNOT FAIL IN THE SCENARIO IT EXISTS TO CATCH** — the defect class
named in `L-404`, in a standard whose own Amendment 2 and Amendment 3 exist to remove instances of
it. **Complying with the clause literally would have committed the defect the clause is for.**

### §A4.2 THE CORRECTION: THE CLAUSE IS NOT WRONG, IT IS UNDER-SPECIFIED — TWO DIFFERENT PROPOSITIONS WEAR ONE SENTENCE

Applying `MONITOR_STANDARD` v1.13's test — **name the proposition the instrument actually
evaluates** — the two counts evaluate **different sentences**, and Clause 2 as written does not say
which the second one is:

| | proposition |
|---|---|
| **(a) over `$OLD..$NEW`** | *"does MY COMMIT OBJECT delete anything?"* — **immutable, so asking twice is asking once** |
| **(b) over `HEAD~1..HEAD`** | *"does the BRANCH'S NEWEST COMMIT delete anything?"* — **NOT tautological: the ref can move** |

**Clause 2's "and again" was written against form (b)** — standing rule 10's own post-commit
`git diff HEAD~1 HEAD --stat`, which re-reads **through the ref**. That form is genuinely
falsifiable, and it is how `C-185` was saved.

**But form (b) has a defect of its own that this referral exposes, and it is the more dangerous
one: WHEN A PEER COMMITS ON TOP BETWEEN THE CAS AND THE READ-BACK, `HEAD~1..HEAD` DESCRIBES THE
PEER'S COMMIT, NOT YOURS.** The verify then prints a clean, plausible, entirely truthful stat line
**about somebody else's work**, and the committer reads it as confirmation of their own. **A
verification that silently changes its subject is worse than one that is tautological**, because
the tautology is merely uninformative while this one is *affirmatively misleading*. Driven by the
lane as a real post-CAS race, not a mock.

### §A4.3 THE RULING

**Clause 2's post-`update-ref` obligation is DISCHARGED BY EITHER FORM, and the helper MUST NAME
WHICH IT USED:**

1. **A numeric deletion count over the range that actually describes what landed on the branch**
   (form (b)), **provided the helper first asserts that its own commit is the branch tip** — if it
   is not, this range is not about the committer's work and must not be reported as though it were;
   **or**
2. **A REACHABILITY assertion — that `$NEW` is the branch tip or an ancestor of it — plus the
   pre-`commit-tree` count**, with the post-landing count **REPORTED AND NOT RE-ASSERTED**, and the
   verify taken over **`$OLD..$NEW`** so it describes the committer's own change and nobody else's.

**Form 2 is PREFERRED.** Reachability is the **only** property that can change after `update-ref`,
so it is the only load-bearing post-landing question — and unlike the deletion re-count it is
**killable**, which the lane demonstrated: an `update-ref` returning 0 without moving the ref
(`L-382`'s silent no-op) is caught by reachability and **cannot** be caught by any object-existence
or object-content check, because the orphan resolves perfectly.

**WHAT IS NOT WEAKENED, AND THIS IS THE HALF THAT MUST NOT BE READ AWAY: the PRE-`commit-tree`
count is UNTOUCHED and remains mandatory.** It is the assertion that actually refuses a stale tree
before anything lands. **Nothing in this amendment permits omitting it**, and a helper that drops
the pre-count while citing this amendment for the post-count has inverted the ruling.

### §A4.4 A CLAUSE MAY NOT DEMAND AN UNFALSIFIABLE ASSERTION — GENERAL, AND IT BINDS THIS FILE

**Any clause in this standard that would require an assertion whose subject cannot change between
the two evaluations is, to that extent, requiring theatre.** The test is `MONITOR_STANDARD`
v1.13's: **name the proposition, then ask what could make it false.** *"Nothing"* is not a strong
assertion, it is an absent one. **Where a clause's literal reading yields such an assertion, the
obligation is discharged by the nearest falsifiable question about the same hazard, and the record
says which was asked and why** — as this amendment does.

**Provenance and honesty about who found it:** raised by a verification lane against a helper in
**closure's** tree; **the lane did not edit the standard and did not rule** — it referred, which is
the correct routing for a document it does not own. **No gate, threshold, cap or label moves in
this amendment**; Clauses 1, 3, 4 and every prior amendment are untouched.

| amendment record | **v1.4** |
|---|---|
| clauses added | **0** |
| existing clauses altered, widened or narrowed | **0** (Clause 2 is **specified**, not narrowed: the pre-count is unchanged and mandatory) |
| gate values changed | **0** |
| discharge forms named for Clause 2's post-`update-ref` half | **2**, with form 2 preferred |
| **lines whose number changed above this section** | **0** |


---

## Amendment 5 (2026-08-30) — v1.4 -> v1.5: A SHARED BOARD'S WORKTREE COPY CAN BE **BEHIND** HEAD, AND APPENDING TO IT DELETES A PEER'S WORK **UNDER YOUR OWN COMMIT MESSAGE**

**Appended at the foot, append-only. Nothing above is edited, struck, widened or narrowed.
`lines whose number changed above this section: 0`.** Raised by a **heat-transfer** lane that hit
the condition **live at commit time** on `docs/LAB_STATE.md`; **the remedy below was re-driven
independently by this supervisor before being written**, including the false-positive limb that
decides which form of the assertion is admissible.

### §A5.1 THE HAZARD, AND WHY IT IS THE DANGEROUS DIRECTION

A shared record — `docs/LAB_STATE.md` above all, which is **the lab's only handoff channel between
sessions** — is edited by six teams. A supervisor who opens the **worktree copy**, appends a block
and commits **has published whatever that copy was missing as a deletion, under their own message.**

Measured live by the raising lane: the worktree copy was **98 lines behind HEAD**, missing a
**landed** peer block. **Committing it would have deleted that block**, and the commit would have
read as an ordinary board update by its author.

**A worktree that is AHEAD of HEAD is the ordinary condition** — it is your own unlanded work.
**A worktree that is BEHIND HEAD is the hazard**, and the two are indistinguishable without asking.

### §A5.2 WHY EVERY GUARD ALREADY IN THIS STANDARD MISSES IT

- **The path-set assertion passes, CORRECTLY.** The board **is** a path you legitimately touched.
  The loss is **inside** it. Amendment 3's *"assert the expected path set"* is answering a different
  question, and answering it right.
- **`git status` DOES NOT TELL YOU THE DIRECTION, and on this box it is worse than silent.**
  Measured by this supervisor at 2026-08-30T23:5xZ on the real repository: `git status --porcelain
  docs/LAB_STATE.md` reported **`MM`** while `git hash-object` and `git rev-parse HEAD:` returned
  **the same blob `bc22d6ff…`** — **the file was BYTE-IDENTICAL to HEAD and status called it
  modified in both index and worktree.** A reader taking `M` as evidence of anything about
  direction is reading noise. (`MONITOR_STANDARD` v1.13 §4: the shared index misreports **stably**.)
- **Clause 2's deletion count does not settle it**, because whether `deletions == 0` speaks of
  **PATHS** or of **LINES** is an **OPEN REFERRAL** (`R3_COMMIT_RENAME_MODE_PREREGISTRATION.md` P1,
  status `BLOCKED`). **This amendment does not resolve that referral and does not need to** — the
  assertion below is a **byte identity** and is correct under either reading.

### §A5.3 THE CLAUSE

**Before appending to any shared record, and in the SAME shell invocation that pins `H`:**

**(1) BUILD FORWARD FROM `H`, NEVER FROM THE WORKTREE COPY.** The base bytes are
`git show "$H:<path>"` — **the same pinned `H` used for `read-tree`, for the `-p` parent and for
the CAS old-value.** Reading HEAD a second time can **straddle a peer's commit**, which
reintroduces the hazard through the door built to close it.

**(2) ASSERT PURE INSERTION, CONTENT-INDEPENDENTLY.** With `head` the bytes from (1), `block` the
appended bytes and `i` the insertion offset:

    result[:i] + result[i+len(block):]  ==  head        # EXACTLY, as bytes

**Removing the appended block from the result must reproduce the HEAD bytes exactly.** This is a
statement about **bytes**, not about lines, counts, headings or tokens, so it holds for any block
and any record and cannot be argued with.

**(3) REPORT THE STALE DIRECTION.** Compare the worktree copy against `git show "$H:<path>"` and
state which way it differs. **BEHIND must be disclosed in the commit message**; AHEAD is ordinary.

### §A5.4 THE FORM THAT IS **NOT** ADMISSIBLE, AND IT WAS MEASURED, NOT REASONED

An **occurrence-count** assertion — *"every token/heading present in HEAD is still present"* —
**HAS A MEASURED FALSE POSITIVE, and it refuses the write that a good board update most often is.**
Driven by this supervisor in a throwaway repository, three limbs, all behaving:

| limb | condition | occurrence-count | **pure-insertion (byte)** |
|---|---|---|---|
| **A (+)** | built from a worktree **3 lines behind** HEAD | fires | **FIRES — and names the 3 peer lines that would have been deleted** |
| **B (−)** | built from HEAD, ordinary append | passes | **SILENT** |
| **C (−)** | the block **legitimately QUOTES a peer's heading** | **WRONGLY REFUSES** | **CORRECTLY ACCEPTS** |

**Limb C is the whole reason the clause specifies the byte form.** Quoting a peer's heading is what
a supervisor does when ruling on that peer's work — **this very standard's amendments do it
repeatedly** — so an occurrence-count guard would refuse precisely the most careful writes, and
would then be switched off for being noisy. **A guard that cries wolf on good behaviour does not
survive contact with the people it guards**, and the byte form costs nothing extra to compute.

### §A5.5 THE GENERAL RULE

> **Before appending to a shared record, ask WHICH DIRECTION your copy is stale in. `git status`
> will not tell you, and on this box it will actively mislead you. Build forward from a pinned
> `git show H:<path>`, and prove the write is a pure insertion by SUBTRACTING THE BLOCK AND
> COMPARING BYTES — never by counting what survived.**

**Provenance and scope.** Raised by heat-transfer from a live near-miss on `docs/LAB_STATE.md`;
**the remedy is theirs and the three limbs above are this supervisor's independent re-drive.** The
form is not hypothetical: **this team's eight board writes on 2026-08-30 were all built from
`git show HEAD:docs/LAB_STATE.md` with the §A5.3(2) assertion**, which is why none of them touched
a peer's block on a night when six teams were committing. **No gate, threshold, cap or label moves
in this amendment.** Clauses 1–4 and Amendments 1–4 are untouched.

| amendment record | **v1.5** |
|---|---|
| clauses added | **1** (§A5.3, three parts) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** |
| assertion forms REFUSED, with a measured counter-example | **1** (occurrence-count, limb C) |
| open referrals resolved | **0** — Clause 2's PATH-vs-LINE question stays `BLOCKED` and untouched |
| **lines whose number changed above this section** | **0** |


---

## Amendment 6 (2026-08-31) — v1.5 -> v1.6: **§A5.3 GAINS A PART 4 — THE BOARD WRITE AND ITS COMMIT ARE ONE INVOCATION.** v1.5 closed the STALE-COPY hole and left a WINDOW open

**Appended at the foot, append-only. Nothing above is edited, struck, widened or narrowed.
`lines whose number changed above this section: 0`.** Raised by heat-transfer from a **live loss**
(their D583), and the loss is **measured, not hypothetical**: a **13,512-byte** block was appended
to `docs/LAB_STATE.md` and recorded in the provenance ledger, and it now exists **at no sha and not
on disk.**

### §A6.1 THE WINDOW v1.5 LEFT OPEN, AND IT IS THE MIRROR OF THE ONE IT CLOSED

**v1.5 §A5.3 makes the WRITE safe:** build forward from a pinned `git show "$H:<path>"`, assert
pure insertion by byte subtraction. **A supervisor doing exactly that is still exposed**, because
between their **write** and their **commit** a peer may — **correctly, following v1.5** — rebuild
the same shared record from the **HEAD blob**, which does not contain the uncommitted block.
**The peer's write is flawless and destroys it anyway.**

**v1.5 protects the record from a stale writer. §A6 protects a correct writer from the record.**
The two are the same window seen from opposite ends, and **v1.5 read only one end.**

### §A6.2 WHY THE LOSS IS UNRECOVERABLE, AND WHY THAT MATTERS TO THE CHECKER

An uncommitted block destroyed this way **existed at no sha, ever.** There is nothing to
`git show`, no reflog entry, no stash. **The provenance ledger's row survives, because the ledger
was committed** — so a checker comparing recorded bytes against HEAD sees a row whose block is
absent and **cannot distinguish it from an ordinary uncommitted file.**

**`scripts/check_harness.py` now distinguishes three states rather than two** — block at HEAD;
block absent from HEAD but **present on disk** (a *recoverable* orphan: commit it); block absent
from **both** (**`LOST`**, reported and **never gated**, because **a red that no action can clear
has only one exit, which is switching the clause off**). **Supersession alone does not cover this:
a board block's heading carries a TIMESTAMP, so a re-landed block has a DIFFERENT heading and can
never retire the one it replaced.**

### §A6.3 THE CLAUSE

**§A5.3 gains a fourth part:**

> **(4) THE WRITE AND ITS COMMIT ARE ONE SHELL INVOCATION.** Build from the pinned `H`, assert pure
> insertion, `read-tree` at that same `H`, `write-tree`, `commit-tree -p $H`, CAS, and verify —
> **without returning to the caller in between.** A shared record must not sit written-but-
> uncommitted across a tool boundary, because **a peer's correct rebuild will destroy it and
> nothing will be recoverable.**

**This is the same discipline rule 10 already imposes for a different reason** — HEAD is captured
**once** for `read-tree`, the assertion and `-p`, **all in one shell invocation**, because a lane
can move HEAD between two bash calls (`L-223`). **§A6.3 extends the invocation to cover the WRITE
as well as the index work.** One boundary, not two.

**Practical note, so this is not read as forbidding drafting:** compose the block into a **file**
first — that is `append_block.py`'s existing shape and it costs nothing. **What may not straddle a
tool boundary is the interval between the shared record on disk carrying your block and that block
being committed.**

### §A6.4 SCOPE

Applies to **any record several teams write** — `docs/LAB_STATE.md` above all, and equally
`docs/LESSONS.md`, `docs/DOCKET.md`, `docs/COST_CALIBRATION.md` and the shared audits. **It does
not apply to a file inside one team's own territory**, where no peer rebuilds underneath the
author. **No gate, threshold, cap or label moves.** Clauses 1–4 and Amendments 1–5 are untouched.

| amendment record | **v1.6** |
|---|---|
| clauses added | **1** (§A5.3 part 4) |
| existing clauses altered, widened or narrowed | **0** (§A5.3 parts 1–3 stand verbatim) |
| gate values changed | **0** |
| measured losses behind this clause | **1** (13,512 bytes, `docs/LAB_STATE.md`, heat-transfer D583) |
| **lines whose number changed above this section** | **0** |

