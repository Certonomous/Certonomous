# DRAFT PROPOSAL — NOT ADOPTED

**Status: DRAFT PROPOSAL. NOT ADOPTED. NOTHING HERE IS IN FORCE.** Adoption is
Sanaa's alone. The `CLAUDE.md` rule-10 text in §3 is **quoted as proposed wording
only**: this document does not change `CLAUDE.md`, any charter, or any `.claude/`
configuration, and the lane that wrote it changed none of them. It reaches Sanaa's
desk through the chief.

**Subject.** Two clauses `CLAUDE.md` rule 10 does not currently carry: (a) that the
shared git index is not a valid instrument in this repository, and (b) that an
append-only shared record is built from its HEAD blob, never from the worktree copy.

**Relationship to the proposal already on the desk — read them together, they do not
compete.** `docs/BOARD_BASE_RULE_PROPOSAL.md` §2 already proposes a rule-10 bullet
constraining the **base** of a shared-file commit. That proposal is scoped to
`docs/LAB_STATE.md` and to its `## <team>` section structure, and it addresses the
**write** side only. This one generalises the base constraint to the lab's other
shared append-only records and adds the **read** side, which no proposal on the desk
covers. **If only one is adopted, `BOARD_BASE_RULE_PROPOSAL.md` §2 is the one that
fixes measured reverts;** this document's §3 is the wider statement of the same
mechanism. They could reasonably be merged into a single bullet before adoption.

**Filing note.** `docs/<TOPIC>_PROPOSAL.md` is the lab's established location — six
precedents on disk and `check_filing.py` rule R2 (`docs/*.md` is UPPER_SNAKE).

---

## 1. Why this is structural rather than an incident

Rule 10 mandates the private-index protocol, which **by design never writes the
shared index**. Every file the lab commits therefore widens the gap between the
shared index and HEAD by one entry. The decay is the protocol working as intended,
and it accelerates with the lab's commit rate: it is fastest exactly when the lab is
busiest. **Measured tonight, the rate does not merely correlate with the commit rate — it
equals it, line for line:** across 9 peer commits the tree gained 672 insertions against 3
deletions, and the staged-deletion count grew by **669 = 672 − 3**. Every line any team
lands becomes a staged deletion in the shared index the moment it lands. `L-92` established this in 2026-08 with a one-way asymmetry (477 paths
present at HEAD and absent from the index, **zero** the other way) — a gap running
one way only is not recorded deletions, it is landed work the index never heard about.

**Clearing the index is a treadmill and is not the mitigation.** The chief cleared it
on 2026-08-24 (443 staged deletions, 63 staged modifications) and the gap reopened
within the same session. The chief has ruled that it will not be cleared again, on
the ground that a clear buys **false confidence** — it makes `git status` briefly look
trustworthy, which is the worst thing to leave on the box. **A cleared index is not a
safe index; it is a recently cleared one** — and reading 8 puts a number on "recently":
**minutes, not hours.** The figure belongs in the record as a rate against **commit
activity**, never as a duration, because a quiet lab would give a flattering and misleading
number.

## 2. The measurements this proposal rests on

All taken 2026-08-25 by one records lane, each with the HEAD sha it was taken at,
because the quantity is time-varying (see the last row).

| # | Reading | Measured |
|---|---|---|
| 1 | Shared index vs HEAD, entry counts | **11,067 vs 11,090** at HEAD `e471b657`, 00:22:35Z |
| 2 | Staged content vs HEAD | **38 paths — 23 deletions, 15 modifications; 439 insertions vs 12,435 deletions** at HEAD `dcf7b9be`. Rule 10 cites a measured 402-line reversion across six files; this is ~30x that |
| 3 | What a bare `git commit` would have deleted | 22 files present at HEAD **and correct on disk**, including two frozen pre-registrations (`cases/ansys_verification/VMFL051/PREREGISTRATION.md` 669 lines, `verification/campaign/F11_CONVERSION_PREREGISTRATION.md` 790) and `docs/COVERAGE_MATRIX.md` (984) |
| 4 | Phantom status rows, sampled directly | 8 of 8 sampled `D ` (staged-deletion) rows were **present at HEAD and present on disk**; 2 of 6 sampled `MM` rows were **byte-identical to the HEAD blob** |
| 5 | `docs/LESSONS.md` worktree vs HEAD | **41 lesson ids** at HEAD absent from disk, **0** the other way; max `L-263` on disk vs `L-304` at HEAD; 655,485 vs 768,432 bytes; disk a strict byte-prefix. HEAD `e471b657`, 00:22:35Z |
| 6 | `docs/COST_CALIBRATION.md` | worktree max `C-48` vs HEAD `C-49`; the **shared-index blob** was further behind still at `C-47` (163,546 bytes) |
| 8 | **Decay RATE**, one lane's timed pair, index untouched both times | 00:25:33Z HEAD `dcf7b9be` → 00:29:30Z HEAD `55983881`: **3 min 57 s, 9 peer commits**; staged paths 38→40, staged deletions 12,435→**13,104 (+669)**; index entries **11,067 both times**; HEAD tree 11,090→11,092, gap **23→25**. **≈ 74 further staged deletions per peer commit** |
| 9 | `docs/NUMERICS_KNOWLEDGE.md` — a third ledger, a third territory | worktree **254,652 bytes vs HEAD 312,617**, and the worktree copy **does not contain `N-T8` at all** (HEAD: 2 occurrences) |
| 7 | **Non-stationarity** — the reading that changes what a "figure" means | `docs/DOCKET.md` measured twice, one pattern, minutes apart: **31 ids behind** at 00:25:19Z (HEAD `dcf7b9be`), then **byte-identical to HEAD** at 00:26Z (HEAD `04325b6b`). `docs/COST_CALIBRATION.md` measured equal-length and then unequal **inside adjacent commands**, HEAD having moved mid-measurement |

Reading 7 is the one that justifies the wording "re-read inside the committing shell
invocation" rather than "recently": the divergence changes **size and direction**
within minutes, so a base captured one tool call earlier is already unproven.

**Two live demonstrations, disclosed rather than smoothed over.** (a) The lesson this
proposal accompanies was drafted against a HEAD whose maximum lesson id was `L-304` and
landed as **`L-307`** — two peers landed lessons in between. The id was correct only
because it was re-derived inside the committing invocation. (b) That same `L-307` commit
added 102 lines to `docs/LESSONS.md` and left **no shared-index entry whatever** (11,067
entries before and after, while HEAD tree entries rose): **the lane writing the lesson
about the mechanism widened the gap by writing it.**

## 3. Proposed `CLAUDE.md` rule 10 amendment — exact text, two sentences

To be inserted as a new bullet in rule 10 (*Git — the working tree is shared…*),
after the private-index protocol bullet. **Proposed wording, NOT IN FORCE:**

> - **The shared index is not an instrument here — the private-index protocol never
>   writes it, so its gap to HEAD grows with every commit the lab makes; ask HEAD
>   directly instead (`git cat-file -e HEAD:<path>` for existence, `git show
>   HEAD:<path>` for content, `git ls-tree -r HEAD <dir>` for the tracked set, a
>   `diff` of `git show HEAD:<path>` against the worktree file for change), and treat
>   `git status`, `git diff HEAD` and `git ls-files` as reporting a per-moment scratch
>   state no reader of this repository will ever see.** **Every edit to a shared
>   append-only record — `docs/LESSONS.md`, `docs/DOCKET.md`, `docs/COST_CALIBRATION.md`,
>   `docs/LAB_STATE.md` — is built on the base returned by `git show HEAD:<path>`
>   re-read **inside the committing shell invocation**, never on the worktree copy,
>   which is stale by design and whose divergence from HEAD changes size and direction
>   within minutes.**

Three properties of this wording are deliberate. It **names the replacement
instruments** rather than only forbidding the bad one, so an agent following it is
not left without a method. It constrains **the base**, not the write-back, so it does
not mandate fast-forwarding the worktree and therefore cannot destroy a peer's
uncommitted tail. And it says **"inside the committing shell invocation"**, which
reading 7 shows is the clause that actually binds — "recently" would not have caught
the `L-304`→`L-307` drift above.

## 4. What this proposal does NOT claim

- **It does not propose clearing, repairing or gating the index.** Inspect, never
  revert; the index is the chief's call.
- **It changes no gate, threshold, cap or label**, and touches no frozen file.
- **It is partly redundant with what is already written down**, and that is stated
  rather than hidden: the read side is `L-92` and `L-294`, the write side is `L-253`,
  and `docs/COST_CALIBRATION.md:40-52` already carries the per-file warning in its own
  header. `L-307` (2026-08-25) consolidates them and adds the non-stationarity finding.
  **The gap this addresses is one of PLACEMENT, not of discovery** — none of it is in
  `CLAUDE.md`, where every agent in the lab reads. Checked and found NOT to overlap:
  `L-305`, whose subject is per-item **disposition** in a drafts file and in which
  `git status` appears only as a subordinate clause.
- **No instrument is proposed and none is built.** A checker that enforced this would
  itself need a planted control, and — per `L-307` — a passing control would prove
  only that it sees what it measures.

## 5. Honest limits of the evidence

- Readings 1–7 are **single-lane measurements** taken over a live tree under six
  concurrently committing supervisors. Each carries its HEAD sha; none is reproducible
  at a later HEAD, by construction.
- The chief's account included two figures this lane **could not confirm**: a
  `docs/COST_CALIBRATION.md` worktree size of 19,991 bytes (measured 168,635 at every
  reading taken here) and a docket misdiagnosis of "47 lines behind HEAD" where the
  worktree was in fact AHEAD. **No claim in this document rests on either**; a
  documented docket misreading of a different shape and figure does exist at
  `docs/LAB_STATE.md` (disk 849 lines vs HEAD 876, 27 ids missing from disk).
- A suggestion offered with reading 8 — that mechanical drift could not account for the
  new whole file or the 669 lines, so the bulk was a separate category of "fresh
  staleness" — **is not supported by the measurement and is not carried here**: 669 =
  672 − 3 exactly, so mechanical widening and peers' commits are one cause described
  twice, not two additive ones. Stated because it makes §1 stronger, not weaker.
- A reported docket divergence of "550 rows at HEAD against 519 in the worktree" was
  **550 against 550** when re-measured with one pattern over both sides; the 519 was a
  `D`-only count set against an all-letter count. This document uses only figures
  measured with one pattern applied to both sides.
