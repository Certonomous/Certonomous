# PROPOSAL — NOT ADOPTED

**Status:** PROPOSAL. Nothing here is in force. Adoption is Sanaa's, and the
`CLAUDE.md` amendment in §2 is quoted as proposed text only — this document does
not change `CLAUDE.md`, any charter, or any `.claude/` configuration, and the
author of this document changed none of them.

**Subject:** the base a shared-board commit is built against, and the four
silent section reverts of 2026-08-23 that the absence of such a rule produced.

**Filing note.** This is `docs/<TOPIC>_PROPOSAL.md`, the lab's established
location for an infrastructure proposal document — five precedents on disk
(`docs/PHASE2_STRUCTURE_PROPOSAL.md`, `docs/GITIGNORE_PROPOSAL.md`,
`docs/REGISTERED_DELIVERABLES_CHECK_PROPOSAL.md`,
`docs/DOCKET_SHARDING_PROPOSAL.md`, `docs/CREDENTIALS_VIEW_PROPOSAL.md`) and
`check_filing.py` rule R2 (`docs/*.md` is UPPER_SNAKE). A `docs/proposals/`
directory was requested in the dispatch; it does not exist, is registered in no
filing rule, and creating it would put a sixth proposal somewhere the other five
are not. Filed to the established location instead, as the dispatch permitted.

---

## 1. The mechanism, in one paragraph

`docs/LAB_STATE.md` is one file carrying one `## <team>` section for each of five
teams that write it concurrently. The shared-board rule in force routes every
board commit through `git show $H:docs/LAB_STATE.md` → `git hash-object -w` →
`git update-index --cacheinfo` in a private index — a path that writes the commit
and **never the worktree file**. `scripts/lab_state_section.py` enforces that
directly: its line 71 refuses to run without `--out`, with the message *"the
shared worktree copy is never written (chief's rule, 2026-08-22)"*. The
consequence is that the file on disk is **stale by design in every section whose
last committer conformed**, and fresh only in sections whose last committer broke
the rule. It is therefore a mixed-vintage artifact that is nobody's coherent
output. Measured 2026-08-23T19:55:53Z at HEAD `890bfa7f`: the worktree copy
matched **no commit in the file's entire history** — simultaneously *ahead* of
HEAD in `## closure` and `## cfd`, equal in four sections, and carrying a
`## verification` section that existed in no commit at all. Any committer whose
base for the other sections is not re-derived from `$H` at commit time silently
reverts them.

The asymmetry is the sting: **the rule destroys the work of exactly the teams
that follow it.** The victims of incidents 1 and 2 below (dafoam, heat-transfer)
are the two documented conformers; the sections of non-conforming teams stayed
fresh on disk and survived.

This is not a new discovery in this lab. `docs/USING_THIS_LAB.md:1111-1118`
already states it verbatim for the other shared records — *"every private-index
commit widens the gap between HEAD and the worktree, monotonically, and nothing
in the repository reports it … silently reverts every private-index row landed
since the worktree last matched HEAD"* — and lines 1120-1138 make a reconciliation
check a precondition of editing them. Two such checks exist
(`check_docket_reconciliation.py`, `check_record_reconciliation.py`); their
registered paths are `docs/DOCKET.md`, `docs/LESSONS.md` and
`docs/NUMERICS_KNOWLEDGE.md`. **`docs/LAB_STATE.md` is registered in none of
them.** Likewise **L-245** already names the assertion — *"On a shared
multi-section file, 'only my paths' is not 'only my content' — assert your hunks
fall inside your own section before update-index"* — and every one of the four
incidents changed a foreign section, so every one was inside that lesson's reach.
The lesson was filed and never instrumented. This is L-240's own lesson
recurring: *a repair that lives only in the prose of an incident report is a
description of one, not a repair.*

A contributing factor worth stating plainly: the shared-board rule is written
down at `docs/LAB_STATE.md:283` **inside dafoam's own board section**, marked
*"Carried in every lane brief"* — dafoam's lane briefs — plus `harness/README.md:127`,
`.claude/skills/form-teams/SKILL.md:114`, and a docstring in
`scripts/check_harness.py:120-134`. It is **not in `CLAUDE.md` rule 10**, where
every agent in the lab reads it.

---

## 2. Proposed `CLAUDE.md` rule 10 amendment — exact text

To be inserted as a new bullet in rule 10 (*Git — the working tree is shared…*),
after the private-index protocol bullet. **Proposed wording, not in force:**

> - **A shared multi-section file is committed against its own COMMITTED base,
>   re-derived at commit time.** For `docs/LAB_STATE.md` the blob you commit must
>   be **byte-identical to `git show $H:docs/LAB_STATE.md` outside your own
>   `## <team>` section**, where `$H` is the same rev you pass to `commit-tree -p`
>   and to the CAS. Re-derive it **in the same shell invocation as the commit** — a
>   base captured when you started drafting is stale by the time you land, and the
>   **worktree copy is stale by design**, because the private-index path never
>   writes it. `scripts/lab_state_section.py --team <t> --rev $H --out <scratch>`
>   asserts exactly this (its lines 34-46). Then verify after:
>   `git diff HEAD~1 HEAD -- docs/LAB_STATE.md` must show hunks **inside your own
>   section only**. Reverting a peer's section is not cured by noticing it later.
>   *(L-245. Four measured reverts on 2026-08-23: `d97ed4c9`, `070da305`,
>   `890bfa7f`, `4932a7c3`.)*

Two properties of this wording are deliberate. It constrains **the base**, not
the write-back, so it does not reintroduce the overwrite disease of §4. And it
names **`$H` at commit time**, which is the clause incidents 3 and 4 actually
violated — both had a perfectly good `git show` base that was simply *old*.

---

## 3. The four incidents

Each was established by byte-exact reconstruction: the offending blob was rebuilt
from candidate sources and hashed against the real blob. Section content was
compared per `## ` section, never by line-level diff — a lesson from this
investigation, recorded in §6.

**Incident 1 — `d97ed4c9`, 2026-08-23 19:39:18Z, verification's first owner-written
board fill.** It reverted `## dafoam` to the vintage of `6c6de745`
(2026-08-22 21:01:45Z): the worktree's dafoam section had not been physically
written for roughly 22.5 hours, because dafoam adopted `lab_state_section.py` at
`8294c589` on 2026-08-22 and never wrote the worktree again. Dafoam's `70c605f0`
revision (19:36:57Z) existed only in git. Caught by the committer's own
post-commit verify — the L-223 shape, which is why that step is not optional —
and repaired verbatim at `6ae77c79` (19:40:28Z).

**Incident 2 — `070da305`, 19:48:08Z, cfd's open-families triage.** Byte-exact:
`070da305` == its parent `baa32076` with `## heat-transfer` swapped back to
`b9a78483`, plus a new `## cfd` section; rebuilt blob `0f65e0f1` equals the real
blob. The committed file held a **fresh** `## verification` section (`baa32076`,
19:47:46Z) beside a **stale** `## heat-transfer` section (`cdb5cc0b` vintage,
19:27:03Z). No commit in history holds that pair, which proves the base was
assembled from at least two sources rather than read from `$H`. The 33 reverted
lines were heat-transfer's 19:45Z revision (`c7dc6add`), recording the
strict-completion-rule verification of eight finished runs. Repaired verbatim at
`40984dac` (19:50:12Z).

**Incident 3 — `890bfa7f`, 19:56:05Z, verification's cross-team audit pass 3.**
Byte-exact: `890bfa7f` == `0bbe62dc` — **the committer's own previous board
commit, five minutes old** — plus its new `## verification` section; rebuilt blob
`98b2c237` equals the real blob. It reverted **two teams at once**, `## closure`
and `## cfd`. This is the incident that refutes the worktree framing: its base was
not the worktree at all, and the worktree was at that moment *newer* than the base
in both reverted sections. The committer's own repair commit `54f53bbb`
(19:59:28Z) independently reaches the same conclusion in its subject line —
*"it committed a STALE scratch blob"*. cfd's section was restored at `537a52d5`
(20:00:28Z) and closure's subsequently; both verified back at HEAD as of
2026-08-23T20:05Z.

**Incident 4 — `4932a7c3`, 19:59:46Z, dafoam's board commit** (*"two-session split
confirmed, W4 M1+M2 launch authorised…"*). The largest: it changed **all five**
team sections, 352 insertions against 355 deletions, of which four were foreign —
`## closure`, `## heat-transfer`, `## cfd`, `## verification`. Its own
`## dafoam` fill was legitimate. Unlike incidents 1–3 it did not restore an
identifiable older vintage of the foreign sections; it wrote text for them that
appears in no other commit, which is why a revert-detector keyed on "equals an
older version" does not flag it and a foreign-section detector does. All four
foreign sections were restored by their owners' subsequent commits; verified at
HEAD 2026-08-23T20:05Z, no content outstanding.

**Live defect found by `check_board_reconciliation.py` on its first real run,
2026-08-23T20:08Z, and not yet repaired at that reading.** HEAD carries a
**doubled `## cfd` heading** (two consecutive `## cfd` lines, HEAD lines 490-491),
introduced by `fe065ca6` (20:04:38Z) and persisting through five subsequent
commits. This is a live booby-trap for the sanctioned helper: `lab_state_section.py`'s
`split()` (lines 25-32) takes the **first** `^## cfd$` match and ends at the
**next** `^## ` line — which is the duplicate heading immediately below. The span
it would replace is therefore the **empty two lines between the two headings**,
leaving the real cfd content stranded beneath, addressable by no section name.
Its internal assert at line 45 would still pass, because the split is
self-consistent — it simply addresses the wrong span. The next cfd board commit
through the approved path would write into a null section.

**Open reconciliation, same reading.** The worktree's `## verification` section
matched no commit in the file's history — unlanded work, someone's uncommitted
draft. Attribution belongs to verification; recorded here as open, not assigned.

---

## 4. P3 — the write-back option, and why it is declined

The obvious fix is *"after any private-index board commit, also write the
committed content to the worktree file."* **This proposal declines it in that
form.**

It is the instruction that already stood in this repository and was struck for
cause. `docs/USING_THIS_LAB.md:1069-1093` quotes it under a strikethrough,
preserved per L-32:

> `# AND THEN, once the CAS has succeeded, this step is part of the protocol:`
> `# write your row into the WORKTREE copy too, inserted in numeric order by ID.`

Executed as a plain overwrite it destroyed unrecoverable bytes — **D369**, applied
at `12b7ed42` to `docs/LESSONS.md`, where `cmp` reported *"EOF on - after byte
313171"* and those trailing bytes are gone. It then **fired a second time** at
**D461**, reissued verbatim by the supervisor enforcing the protocol, across all
three append-only records. The lab's own summary of the residual risk is worth
repeating: *"No loss was detected, and that is not the same as no loss"* — every
instrument used to rule it out was an ID-set check, and D369's actual loss was
bytes matching no ID regex.

The board makes this worse, not better, because it has no ID vocabulary at all: a
section is prose, so an ID-set check cannot even be built for it, and the only
detector of a lost paragraph is a byte comparison against a version somebody
thought to keep. And the hazard is live rather than theoretical — at
2026-08-23T20:08Z the worktree held a `## verification` section present in no
commit. A naive write-back at that instant would have destroyed it.

Two further objections:

1. **It would not have prevented incidents 3 or 4.** Both were built on a stale
   *committed* base, not on the worktree. Writing the worktree after every commit
   leaves that failure mode untouched.
2. **If adopted at all it must be a MERGE with a refusal**, i.e.
   `scripts/append_record.py`'s shape generalised to section-structured files:
   rebuild as HEAD's blob plus the author's own section, and *refuse* (exit 2)
   if the worktree disagrees with the committed blob inside that blob's own
   bytes. That is strictly more machinery than §2 plus the two checks, and it
   still does not fix incidents 3 and 4.

---

## 5. What is proposed, in priority order

| # | Item | Catches | Status |
|---|---|---|---|
| P4 | the `CLAUDE.md` rule-10 base constraint in §2 | all four, at the cause | **proposed here; Sanaa's call** |
| P1 | `scripts/check_board_sections.py --at <sha>` | all four, post-hoc (verified 4/4) | **built, committed, wired into nothing** |
| P2 | `scripts/check_board_reconciliation.py` | worktree drift, before an edit | **built, committed, wired into nothing** |
| P3 | write the worktree after every board commit | incidents 1-2 only | **declined — see §4** |

P4 and P1 are complementary and the recommendation is to take them together: P4
states the rule where every agent reads it, P1 makes it checkable afterwards, and
L-240 is explicit that prose alone is not a repair. P2 is cheap and fits existing
law verbatim — it is the sibling `USING_THIS_LAB.md:1120` already mandates for the
other three shared records.

**Honest limits of P1 and P2, stated because they matter to any adoption
decision:**

- P1 **cannot verify that a `Lab-Team:` trailer is truthful.** Every commit in
  this repository carries one `Ubuntu` identity, so team attribution is not
  derivable from git and must be *declared*. The trailer makes the claim
  reviewable; it does not make it verified. Its `--team` flag, for auditing
  commits that predate the trailer, prints itself as REVIEWER-ASSERTED for the
  same reason.
- P1 is **post-hoc**. It grades a commit that already landed and blocks nothing.
- P2 **cannot see a stale base held in an agent's scratch directory or context** —
  it would have read PASS on incident 3.
- Neither is wired into `check_harness.py`, any hook, or any gate. Wiring them in
  is a separate decision and is not taken here.
- The `Board-Repair:` escape in P1 is an *escape*: a commit that declares it is
  believed. `6ae77c79` and `40984dac` are both real repairs that had to write a
  foreign section, so the escape is necessary; it is also the obvious way to
  defeat the check, and it is deliberately narrow — a `Board-Repair:` naming no
  incident is refused.

---

## 6. Method note, and one correction to this author's own earlier finding

Section content must be compared **per `## ` section, byte-for-byte**, never by
line-level set difference. In the course of this investigation a line-level
comparison of incident 4 reported 22 lines of `## heat-transfer` still missing
from HEAD, including a verbatim Sanaa directive. A content-level check of the
distinctive phrases showed the directive **present at HEAD**: the section had been
reflowed, so identical prose occupied different line breaks and the set difference
over-reported. The corrected finding is recorded in §3 and no restoration was
owed. Stated here rather than quietly dropped, because a false report of a lost
Sanaa directive is exactly the kind of confident error the lab's checks exist to
prevent, and it was produced by the author of those checks.

---

## 7. Records this proposal would owe

Not filed by this document, and not by its author. Proposed for routing by the
chief to the owning team's helper flow:

- **A lesson** on the mechanism: *a private-index protocol that never writes the
  worktree makes the worktree stale BY DESIGN, and selectively destroys the work
  of the teams that follow it* — with the byte-exact reconstruction of `890bfa7f`
  as the evidence that the stale base need not be the worktree at all.
- **L-245 instrumentation closure**: L-245 is filed and, until these two scripts,
  uninstrumented. Per rule 14 a lesson is not applied until every call site
  asserts it; `check_board_sections.py` is the assert, and the docket row should
  record that it gates nothing yet.
- **A docket row** for the live doubled `## cfd` heading at HEAD (§3), owner cfd,
  with the `lab_state_section.py` null-section consequence stated.
- **A docket row** for the open `## verification` worktree reconciliation (§3).
- **A docket row** for the adoption decision on §2, owner Sanaa.
