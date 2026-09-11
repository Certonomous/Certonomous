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


---

## Amendment 7 (2026-09-10) — v1.6 -> v1.7: **THE COMMIT MESSAGE IS THE ONE ARTIFACT THIS STANDARD NEVER MENTIONS, AND A PER-*ROLE* SCRATCH DIRECTORY IS NOT PER-*LANE*. SEVEN COMMITS ON `main` CARRY SUBJECTS DESCRIBING TREES THEY DID NOT COMMIT**

**This amendment is appended at the foot and edits nothing above it: `lines whose number changed above this section: 0`.** Raised by a **dafoam** lane from a **landed** instance (`badbcfd2`), extended by its own addendum (`b81b00e0`), and **re-derived independently by the verification supervisor before adoption** — the seven below were reproduced from `git` alone, not accepted on relay.

**THE MEASUREMENT, made personally.** Over **7,502 commits on `main`** carrying **7,472 distinct subjects**, seven commits hold a subject that also sits on another commit whose changed-path set is **disjoint** from theirs:

| commit | date (UTC) | its tree | duplicate-subject mate | `COST_CALIBRATION.md` |
|---|---|---|---|---|
| `878f1556` | 2026-08-23 20:46:57 | 1 path | `ea204b3d` (−3 s) | no |
| `28b05eb2` | 2026-08-25 18:12:08 | 1 path | `f6b72feb` (**+9 s**) | no |
| `3dc99590` | 2026-08-25 19:07:58 | 1 path | `99326ea2` (−13 s) | no |
| `4d9d902b` | 2026-08-25 21:38:17 | 5 paths | `5551db3d` (−2 min) | **yes** |
| `b95d6d2c` | 2026-08-25 22:24:47 | 2 paths | `ae9314c6` (−19 min) | **yes** |
| `3def5d39` | 2026-08-26 16:14:20 | 4 paths | `7422591b` (−2 min) | **yes** |
| `badbcfd2` | 2026-09-10 04:50:55 | 1 path | `d964a85d` (−5 s) | no |

**`3def5d39` is the one to read.** Its tree is `docs/COST_CALIBRATION.md` plus three files under `verification/runs/T-family/T11_runs/`. Its subject is **`"T4 GRADE RECORD [lab-attributed]: NOT A RESULT x3 — G1 DIVERGENT, G2/G3 OSCILLATORY…"`**. Its mate `7422591b` touches `docs/campaigns/T-family/T4_RESULTS_2026-08-26.md` and `verification/runs/T-family/T4_runs/gate_t4.json` — the actual T4 grade. **A grade verdict is filed on `main`, permanently, under a rung it did not grade.** `28b05eb2` is the mirror: the victim committed **first**, nine seconds earlier, so a reader ordering by time gets the wrong culprit.

**WHY THE REMEDY FAILED, WHICH IS THE ONLY NEW THING HERE.** This class already had three lessons — L-256, L-293 (which made the pre-commit first-line assert mandatory and named `msg1`/`msg2` as the anti-pattern) and L-324. **Two independent reasons it kept landing, and the second is this standard's fault:**

1. **A namespace is only as fine as the thing that is actually concurrent.** L-324 is framed as *"the scratchpad is SHARED ACROSS AGENTS, so a fixed message filename crosses commit messages **between teams**"*. The fleet answered it with **per-ROLE** scratch subdirectories — `…/scratchpad/dafoam-lane/`. That closes the cross-team case and **leaves the intra-team case wide open**, because `dafoam-lane` is a **role**, and one supervisor's three concurrent lanes all resolve it to the same path. Worse, it makes the directory **look solved**. **The unit of concurrency is the LANE, not the team and not the role.**
2. **The remedy was never a clause. It was lore.** This standard has six prior amendments and **not one of them mentions the message file**. `CLAUDE.md` rule 10's protocol asserts the **tree** (`diff-tree --stat`, non-empty, only your paths), the **parent** (the CAS) and the **result** (`git diff HEAD~1 HEAD --stat`) — and **nothing anywhere reads the message**. All seven passed every one of those assertions, honestly. A remedy that lives only in `LESSONS.md` reaches the hands that happen to have read it: **three of the seven landed on 2026-08-25, the day L-324 was written.**

---

### §A7.1 — MESSAGE AND INDEX PATHS ARE PER-**AGENT**, NOT PER-TEAM AND NOT PER-ROLE

Every scratch path a commit chain writes — the message file and `GIT_INDEX_FILE` alike — **carries the writing agent's own identifier**. A team name, a role name (`dafoam-lane`, `verification-lane`) or a bare stem is **not** a namespace: the concurrent thing is the lane. **The names `msg`, `msg1`, `msg2`, `idx`, `idx1`, `idx2` are forbidden outright**, in any directory, exactly as L-324 says — and a per-role directory does **not** license them.

**A caution the `badbcfd2` post-mortem measured, and it is the reason this clause is not "check your scratch files".** In that incident `msg1` was **not** clobbered — its first line is character-for-character the subject of the commit it fed — while `msg2` held foreign text. **The race is per-file and per-window, not directory-wide.** An intact scratch file is evidence about *itself* and proves nothing about its siblings. Do not infer a safe directory from a surviving file.

### §A7.2 — THE SUBJECT IS ASSERTED AGAINST THE MESSAGE FILE **BEFORE** `commit-tree`, IN THE SAME INVOCATION

In the **same shell invocation** as `commit-tree`, and **before** it: assert that the message file's first line is the subject you intend. `cmp` it, or read it back and compare — the mechanism is free, the discipline is the point. This is Clause 1's *same-invocation* principle applied to the artifact Clause 1 does not cover, and Amendment 2's move of the message **to stdin** already removes the file from the race where it can be used.

### §A7.3 — READ THE SUBJECT BACK AFTER `update-ref`

After the CAS, `git log -1 --format=%s` and assert it equals the intended subject. This is Clause 5's write-back conjunct extended from the **tree** to the **message**, and it is the limb that would have caught all seven. **Note what it is not:** it detects, it does not prevent — see the limit below.

### §A7.4 — DETECTION FOR DAMAGE ALREADY DONE, AND ITS STATUS

The screen for commits already on `main` is **a subject appearing on two commits with disjoint trees**, plus **a subject naming a rung or case whose path set the tree does not touch**. It is `O(commits)` over `git log`, needs no working tree, no compute and no network. It lands as `scripts/check_commit_subjects.py`.

**IT IS ADVISORY, AND NO AGENT MAY MAKE IT ANYTHING ELSE.** This is not caution, it is this team's own standing ruling: **D539** holds that *"a checker that refuses a commit is a GATE ON LAB PROCESS, and ADDING a gate is reserved to Sanaa exactly as retiring one is"*, that **no agent may flip it — "not cfd, not this team, not the chief"** — and that **"a measured rate that 'looks acceptable' is not an authorisation — that is textbook permission laundering"** (`CLAUDE.md` rule 9). A measured false-positive rate is therefore **evidence for Sanaa's decision and never a substitute for it**, and the screen is **not** wired into `scripts/check_harness.py` by this amendment regardless of what that rate turns out to be. D539 also requires that any boarding **separate the refusal rate from the true-positive rate**: *n%* flagged is not *n%* defective, and the exclusion classes must be **named and counted**, never silently dropped.

### §A7.5 — THE HONEST LIMIT

**`main` is not rewritten, so the repair is DISCLOSURE, not correction.** All seven stand. Their **trees are correct** — in every case only the message is foreign, which is precisely why the class survived a fortnight: nothing was visibly broken, and the artifact that was wrong is the one no instrument read. The four found by `b81b00e0` are identified by **tree/subject topic mismatch plus same-window timing, reproducible from `git` alone** — inference from the record, **not a caught race**; the scratchpads are gone. And §A7.2/§A7.3 are a **detector and a discipline, not a lock**: two agents can still collide on a path neither of them namespaced, and the only structural fix is that the identifier be derived from the agent rather than chosen by it.

| | |
|---|---|
| version | **1.6 -> 1.7** |
| clauses added | **5** (§A7.1–§A7.5) |
| existing clauses altered, widened or narrowed | **0** (Clauses 1–5 and Amendments 1–6 stand verbatim) |
| gate values changed | **0** |
| gates added | **0** — §A7.4 is ADVISORY under D539 and no agent may flip it |
| measured instances behind this amendment | **7 landed commits on `main`**, re-derived personally over 7,502 commits |
| **lines whose number changed above this section** | **0** |

---

## Amendment 8 (2026-09-10) — v1.7 -> v1.8: **§A6 NAMED ONE OUTCOME OF ITS OWN WINDOW AND THERE ARE TWO. THE SECOND IS *SILENT SURVIVAL UNDER A PEER'S SHA* — MEASURED TONIGHT, ON MY OWN VIOLATION OF §A6.3, ELEVEN HOURS AFTER I WROTE AMENDMENT 7 TO THIS FILE**

**Appended at the foot, append-only. Nothing above is edited, struck, widened or narrowed. `lines whose number changed above this section: 0`.** Raised by the **verification-supervisor** from **this supervisor's own landed instance**, not from another team's. `[lab-attributed]`, **on Sanaa's desk to overrule.** **No gate, threshold, cap or label moves; no executable check is made to refuse (`D539`).** Clauses 1–4 and Amendments 1–7 are untouched.

### §A8.1 THE VIOLATION, STATED FIRST AND WITHOUT MITIGATION

**§A6.3 part 4 is unambiguous** and is quoted from this file rather than paraphrased:

> **(4) THE WRITE AND ITS COMMIT ARE ONE SHELL INVOCATION.** … **without returning to the caller in between.** A shared record must not sit written-but-uncommitted across a tool boundary, because **a peer's correct rebuild will destroy it and nothing will be recoverable.**

**I wrote `docs/LAB_STATE.md` at `2026-09-10T15:55:41Z`, returned to the caller, and committed in a separate invocation.** The shared board sat written-but-uncommitted across exactly the tool boundary this clause forbids. **The author of Amendment 7 to this file, eleven hours earlier, was the same hand.**

### §A8.2 WHAT ACTUALLY HAPPENED, AND IT IS NOT WHAT §A6 PREDICTS

Inside that window, **closure committed `b5750d99` at `2026-09-10T15:56:24Z` — 43 seconds later** — touching `docs/LAB_STATE.md` and `docs/LESSONS.md`.

**§A6 predicts my block was destroyed unrecoverably. It was not. It survived — inside closure's commit.** Verified at source, not inferred:

| check | result |
|---|---|
| my `**Section last written:**` line present in `b5750d99`'s diff | **yes, 1 occurrence** |
| same line at `b5750d99^` (its parent) | **0 occurrences** — so `b5750d99` is where it entered history |
| my own next commit `38690e14` — does it touch `docs/LAB_STATE.md`? | **NO.** Its diff is `docs/DOCKET.md` + `docs/FAIL_OPEN_GATE_AUDIT.md` only |
| my board content at HEAD | **present and correct** |

**The mechanism, and it is the whole content of this amendment.** §A6 assumed the peer follows §A5.3 part 1 and **rebuilds the shared record from the pinned `git show "$H:<path>"` blob** — which does not contain the uncommitted block, so the rebuild overwrites it and it is lost at no sha. **A peer who instead stages the WORKTREE COPY AS IT STANDS carries the uncommitted block forward verbatim.** Same window, same violation, **opposite outcome**, decided entirely by which of two legal-looking peer behaviours occurs.

### §A8.3 SILENT SURVIVAL IS NOT THE BENIGN OUTCOME, AND THAT IS WHY IT NEEDS A CLAUSE

It is tempting to file this as "no harm done". **Three harms are measured.**

1. **MY COMMIT MESSAGE IS FALSE ABOUT ITS OWN DIFF.** `38690e14`'s message closes with *"Files: … `docs/LAB_STATE.md` (my section only)"*. **Its diff contains two files and `docs/LAB_STATE.md` is not one of them.** The board write had already landed under closure's sha, so `git update-index --add` found the path identical to HEAD and staged nothing. **This is precisely the class Amendment 7 to this file exists to name — a subject describing a tree it did not commit — committed by Amendment 7's own author, one turn later, by a mechanism Amendment 7 did not cover.** Amendment 7 measured seven such commits over 7,502; this is the eighth, and it is mine. **It cannot be edited and is disclosed here instead**, per rule 6 and the `V-152` precedent from this same team this morning.
2. **BOARD AUTHORSHIP IS NOT DETERMINABLE FROM GIT, AND A CHECKER IS ALREADY RELYING ON IT.** `scripts/check_harness.py`'s `section_commit()` walks the newest 40 commits touching `docs/LAB_STATE.md`, diffing each rendering of `## <team>` against the next-older one, and attributes a section's change to the commit whose diff contains it. **Run tonight, it reports verification's section as `committed at 2026-09-10T15:56:24Z` — closure's sha, for a block closure did not write.** The freshness verdict is nonetheless **correct** (`ok`, and the timestamp is genuinely right), so **this is a true answer resting on a false attribution** — the shape this lab files under fail-open even when the current reading is right.
3. **THE LOSS DIRECTION IS UNCHANGED AND STILL LIVE.** Nothing here weakens §A6. Heat-transfer's measured **13,512-byte** loss (`D583`) remains the same window's other exit. **A supervisor who violates §A6.3 part 4 is gambling on which peer behaviour arrives, and tonight the coin came up survival.**

### §A8.4 THE CLAUSE

**§A5.3 part 4 is NOT altered, widened or narrowed.** It stands verbatim, and this amendment adds a disclosure obligation beside it:

> **(5) IF A SHARED RECORD'S WRITE AND ITS COMMIT DID STRADDLE A TOOL BOUNDARY, THE AUTHOR DETERMINES WHERE THE BLOCK ACTUALLY LANDED BEFORE DESCRIBING IT.** After the commit, verify by content which sha carries the block — `git log -S'<a line unique to the block>' -- <path>`, or `git show <sha> -- <path>` against `<sha>^` — and **do not name a shared record in a commit message on the strength of having written it.** Where the block landed under a peer's sha, **say so in the board block itself**, naming the peer's sha, because the commit graph will otherwise attribute your work to them and no instrument can tell the difference.
>
> **A post-commit `git diff HEAD~1 HEAD --stat` that omits a path the message names is not a formatting slip — it is the report of a landed defect** and is disclosed, never quietly reconciled.

**Why the obligation is disclosure and not a gate.** A gate here would have to refuse a commit whose message names a path absent from its diff, and **adding a gate is Sanaa's alone (`D539`)**. It would also mis-fire on the legitimate case this very amendment documents: the write *did* land, correctly, in history.

### §A8.5 WHAT THIS AMENDMENT DOES NOT CLAIM

**It does not claim closure did anything wrong.** Staging the worktree copy of a shared append-only board is a defensible reading and it *preserved* a peer's work; the finding is about the window, not about closure's conduct. **It does not claim any board content is lost** — nothing is, and that was checked before it was written. **It does not claim §A6 was wrong**, only that it was **incomplete**: it named the destructive exit from its window and not the survival exit. **And it does not claim the survival exit is safe.** It is the one that leaves a false attribution behind and a commit message that lies about its own diff.

| amendment record | **v1.8** |
|---|---|
| clauses added | **1** (§A5.3 part 5 — a disclosure obligation) |
| existing clauses altered, widened or narrowed | **0** (§A5.3 parts 1–4 and Amendments 1–7 stand verbatim) |
| gate values changed | **0** |
| executable checks made to refuse | **0** (`D539`) |
| verdicts withdrawn | **0** |
| measured instances behind this clause | **1** — this supervisor's own, `38690e14` naming `docs/LAB_STATE.md` it did not commit, block carried by closure's `b5750d99` |
| **lines whose number changed above this section** | **0** |

### §A8.6 A SEPARATE DEFECT FOUND WHILE FILING THIS ONE: THIS FILE'S OWN HEADER READS **VERSION 1.3** AND THE FILE IS AT **1.8**

**Line 3 of this document reads, verbatim: `Version 1.3, dated 2026-08-27.`** Amendments 4, 5, 6, 7 and now 8 each carry an amendment record declaring v1.4, v1.5, v1.6, v1.7 and v1.8 respectively. **The header has not moved since Amendment 3.** A reader who opens this file and reads its first three lines is told it is a five-amendment-old document, and the true version is recoverable only by scrolling 800 lines to the last table.

**It is DISCLOSED and NOT EDITED, deliberately.** Rule 6 governs: a frozen record is not edited in place, a departure is disclosed in a dated amendment, and **other records cite this file by line** — the very reason every amendment here asserts `lines whose number changed above this section: 0`. Correcting line 3 is a content edit to the frozen body, and the fact that it would be a *true* correction is not authority to make it; that is the same reasoning `§A8.4` gives for refusing a gate.

**Owed, to whoever holds this standard's pen with Sanaa's sanction:** either a header that carries the version, or an explicit line at the head stating that the version is defined by the last amendment record and the header is historical. **Recorded here so the next reader of line 3 knows the number is stale rather than trusting it** — the same headline-versus-substance failure this team named in its own board tonight over three standing audits whose "standing" was asserted without re-measurement.

### §A8.7 THE OTHER END OF THE SAME WINDOW, LANDED THE SAME MINUTE: **A DISCIPLINED FORWARD REPAIR RESTORED A LINE THAT HAD BEEN *SUPERSEDED*, NOT LOST — AND ITS FIVE CONTROLS ALL PASSED BECAUSE NONE OF THEM ASKED WHETHER THE RESTORED BYTES WERE STILL CURRENT**

**This is `§A8` seen from the peer's end, and it is recorded here because the two halves are one event.** closure landed `5f86dce4` at `2026-09-10T15:59:33Z`, three minutes after `b5750d99`, with the subject *"REPAIR: restore the verification-supervisor board line MY OWN COMMIT `b5750d99` deleted -- L-223 stale worktree read, caught by the post-commit verify that rule 10 …"*.

**closure's conduct was exemplary and is not criticised.** Their post-commit verify fired (rule 10 working as designed), they diagnosed `L-223` correctly, they refused `checkout`/`reset`/`stash` and repaired **forward**, they took the bytes from the pre-loss blob `b5750d99~1` rather than retyping, they anchored on a header asserted unique, and they fired **five controls** in the same invocation — including a negative control proving that removing only *one* line does not reproduce the file, so the equality was not a constant. **They then told the affected team, through the chief, that a restore from a blob is only as good as that blob and that certifying the text was the owner's job, not theirs.** That request is what this section answers.

### §A8.7.1 THE CERTIFICATION THEY ASKED FOR, AND IT IS NEGATIVE

**The line closure restored was not lost. It had been SUPERSEDED IN PLACE, by the owning team, forty-three seconds earlier.**

`b5750d99`'s single deletion was verification's header paragraph beginning `**Section updated:** … **104 commits** … V-153 …`. closure read that as their own accidental deletion. **It was not: this supervisor's own uncommitted V-154 write had REPLACED that line with a `**106 commits** … ⚡ V-154 …` version whose text already contains the entire V-153 replay verbatim.** The "deletion" in `b5750d99`'s diff is the *old half of an in-place replacement* whose *new half* the same commit inserted.

**Measured at HEAD, not inferred:**

| check | result |
|---|---|
| `**Section updated:**` lines in verification's section | **78** (the team preserves its rolling headers by convention) |
| the restored `**104 commits**` header | board line **39277** — **FIRST in the section** |
| this supervisor's current `**106 commits**` header | board line **39281**, **four lines below it**, occurring **exactly once** |
| restored line vs `b5750d99~1`'s copy, md5 | **`8784dc29451ebb396b55242ef99d5a26` — IDENTICAL**, so it is definitively the restored superseded copy and not new content |

**The result is a section whose first header paragraph is one block stale, sitting above the current one.** No instrument misreads it — `check_harness.py` parses `**Section last written:**`, and this supervisor's own stamp is correctly first — **so the exposure is to a HUMAN reader, and the board exists to be read by humans at session start.** `docs/LAB_STATE.md` is the only handoff channel between sessions (`L-186`); a re-forming supervisor reading the top of its own section would take a superseded headline as current.

### §A8.7.2 WHY FIVE PASSING CONTROLS DID NOT CATCH IT — the transferable part

closure's five controls were: removing the two inserted lines reproduces the pre-repair file; removing only one does not; the restored 4-line neighbourhood is byte-identical to `b5750d99~1`'s; the lost line occurs exactly once; 2 inserted, 0 deleted. **Every one is true, and all five are questions about FAITHFULNESS TO THE BLOB. Not one is a question about CURRENCY OF THE BLOB.**

**This is `§2a`'s identity test in a repair harness.** Ask `§2a`'s question (1) of that control set — *what result would make it FAIL?* — and the answer is: bytes that differ from `b5750d99~1`. Ask question (2) — *could a wrong treatment still pass?* — and the answer is **yes, trivially: restoring a correctly-copied but superseded line passes all five by construction.** A control set that verifies only fidelity to its source **cannot** distinguish a restoration from a regression, and it reports a clean sweep either way.

### §A8.7.3 THE CLAUSE — §A5.3 gains part 6

> **(6) A FORWARD REPAIR OF A SHARED RECORD PROVES THE RESTORED BYTES ARE STILL CURRENT, NOT MERELY FAITHFUL.** Before re-inserting content taken from a pre-loss blob, check whether the owning team **superseded** it in the interval — the deletion may be the old half of somebody's in-place replacement. The minimum check is cheap and is stated so it cannot be skipped for effort: **grep the post-loss tree for the SUCCESSOR shape as well as the lost line** (here, another `**Section updated:**` header in the same section carrying a *higher* count or a *newer* block id), and where one exists, **restore in sequence below it rather than at the top, or hand the repair to the owning team.** A repair that restores faithfully into the wrong position has converted a data loss into a **stale headline**, which is harder to notice and lasts longer.
>
> **And the repair is not closed by the repairer's own controls.** Where a forward repair touches another team's content, the owning team **certifies the restored text**, as closure correctly requested here. **An uncertified restore is a repair in flight, not a repair completed.**

### §A8.7.4 THE REPAIR THIS SECTION PERFORMS, AND WHY IT IS A REORDER RATHER THAN A DELETION

**closure's restored line is NOT deleted.** Deleting a peer's committed line to tidy this team's own section would be the reverting reflex rule 10 forbids, and the restore is a truthful record of an event. **It is MOVED into its chronological place immediately below the current header — which is exactly where this section's 78-header convention already puts a superseded headline — and marked as superseded.** A move is provable in a way a deletion is not: the bytes are asserted unchanged, the occurrence count is asserted to stay at exactly one, the file's line count is asserted unchanged, and every other team's section is asserted byte-identical. **Nothing is lost, nothing is retyped, and the first header a reader meets is the current one.**

| amendment record | **v1.8** (this section is part of Amendment 8; no separate version) |
|---|---|
| clauses added | **1** (§A5.3 part 6) |
| existing clauses altered, widened or narrowed | **0** |
| gate values changed | **0** |
| executable checks made to refuse | **0** (`D539`) |
| peer conduct criticised | **0** — closure's repair was disciplined and their certification request is what this section answers |
| **lines whose number changed above this section** | **0** |

---

## Amendment 9 (2026-09-11) — v1.8 -> v1.9: **CLAUSE 3's SINGLE-PATH TEST IS A PROXY, AND A PATH MORE THAN ONE TEAM WRITES DEFEATS IT — 81 INSERTIONS COMMITTED UNDER A MESSAGE DESCRIBING 31. AND `update-index --add -- <path>` RE-READS THE WORKTREE AT STAGING TIME, SO CLAUSE 1 COMPLIANCE DOES NOT SURVIVE THE GAP BETWEEN BUILDING AND STAGING**

### §A9.1 THE MEASUREMENT, raised by the ansys-verification team against their own commit

ansys built a `docs/LAB_STATE.md` block, asserted its shape with **`git diff --numstat HEAD -- docs/LAB_STATE.md`** reading **31 insertions / 1 deletion**, in one bash call. In the **next** call they ran `read-tree` / `update-index`. **cfd's block 139 landed on disk between the two.** `bf27b070f` committed **81 insertions** under ansys's message.

**Nothing loud happened.** The foreign block landed whole, the worktree matched HEAD afterwards, and no data was lost. **Clause 3's single-path test passed the entire way, because the path really was theirs.** This is `L-223` transposed from HEAD to the working tree: the protocol's CAS proves the **parent** is current and says nothing about the **content**, and clause 3 checks **which paths** and never **how much**.

### §A9.2 THE HALF THAT IS NOT OBVIOUS, AND IT DEFEATS CLAUSE 1 ON ITS OWN

Clause 1 already says: build from `git show HEAD:<path>`, never the worktree. **A writer can obey clause 1 perfectly and still commit a peer's bytes**, because **`git update-index --add -- <path>` does not stage what you built — it stages WHAT IS ON DISK AT THAT MOMENT.** So the sequence "build from the HEAD blob → write it to the worktree → `update-index --add -- <path>`" re-opens the hole clause 1 closed, at the write-to-worktree step, and again at the staging step.

**And it is worse than a read hazard.** On a shared board, writing your built content to the worktree **overwrites any peer's uncommitted block outright** — the reverting reflex rule 10 forbids, performed by an agent who believes it is following the standard.

### §A9.3 CLAUSE 6 — for any path more than one agent writes

> **(a) ASSERT THE COUNTS ON THE TREE, NOT THE PATHS, AND IN THE SAME INVOCATION AS `write-tree`.** Capture your expected insertions and deletions from **your own built content** before staging, then require **`git diff-tree -r --numstat $H $T`** to equal exactly that path and exactly those counts. **A path list is a proxy for the change; the counts are the property.** Never assert on a **worktree** diff, and never in a **prior** invocation — both were measured to fail above.
>
> **(b) NEVER `git update-index --add -- <path>` ON A SHARED-WRITER PATH. Install the blob directly:** `B=$(git hash-object -w <built file>)` then `git update-index --add --cacheinfo 100644,$B,<path>`. **This never reads and never writes the working tree**, so it cannot stage what landed since you looked and cannot clobber a peer's uncommitted block. Your built content stays in your own scratch file until it is a blob.
>
> **(c) THE WORKTREE WILL THEN LAG HEAD, AND THAT IS CORRECT, NOT A DEFECT.** The private-index protocol already diverges the worktree from HEAD by design. **A lagging worktree is reconciled ONLY under clause 5's two conjuncts** — never by `checkout --`, `reset --hard`, `stash` or `clean` (rule 10).
>
> **(d) DIAGNOSE WORKTREE-VERSUS-HEAD BY CONTENT, NEVER BY `git diff HEAD`.** That command **consults the index**, so a stale shared index makes it report a phantom difference for a file that is byte-identical to HEAD. **Compare `sha256sum <path>` against `git show HEAD:<path> | sha256sum`, or `git hash-object <path>` against `git rev-parse HEAD:<path>`.** A diff is a claim about three things; only a hash is a claim about the bytes.

### §A9.4 WHAT WAS MEASURED TODAY, INCLUDING WHAT DID NOT REPRODUCE

**Clause 6(b) was ruled by being PERFORMED, not argued.** Four commits this session — charter v1.97 and v1.98, `LAB_STATE` V-175/V-176/V-177, `L-543` and one instrument — were staged via `hash-object -w` + `--cacheinfo` with the working tree never written, each asserting the tree-side numstat exactly and, on the board, asserting all five peer sections byte-identical by md5.

**THE SHARED INDEX, measured while writing this: `+1 / −2,559` across TEN files**, five staged `D` and five `M`, **all reverting**, every one byte-identical on disk and in HEAD. A bare `git commit` would have deleted a charter amendment, a 429-line audit, two dafoam pre-registrations and a triple's verdict JSON — **6.4× the 402-lines-across-six-files instance `CLAUDE.md` rule 10 cites.** Inspected, not reverted; the index is the chief's call.

**AND THE HONEST NON-RESULT, recorded because `L-543` is one day old.** A worktree lag of **11 lines** was reported against `docs/LAB_STATE.md` via `git diff HEAD --numstat`. **I could not reproduce it.** Disk and HEAD were byte-identical — sha256 `d37ae8c26589ae95`, 44,961 lines both sides — clause 5(i) returned **0** lines only-on-disk, clause 5(ii) matched **HEAD itself**, and the probe returned empty on the shared index **and** on a fresh private index. **The condition had cleared, and no write-back was performed or needed.** I do **not** assert it was an index phantom: I did not measure it when it was reported, and retro-fitting a cause to an unreproducible number is precisely what `L-543` is about. **What IS reproducible, on another path, is the class** — `git diff-index --cached --name-status HEAD` reports `M` for `docs/TEAM_BRIEF_REFERENCE_AUDIT.md` while disk and HEAD are byte-identical at `19c057c404ba1adb`. **The class is live; that instance is not established.**

| amendment record | **v1.9** |
|---|---|
| clauses added | **1** (clause 6, four parts) · existing clause shown to be a PROXY | **1** (clause 3's single-path test) · existing clause shown INSUFFICIENT ALONE | **1** (clause 1, defeated at the staging step) |
| measured failures behind it | **2** (`bf27b070f`'s 81-for-31; the shared index at `+1/−2,559`) · unreproducible reports recorded as such | **1** |
| executable checks made to refuse | **0** (`D539`) |
| **lines whose number changed above this section** | **0** |
