# Sharding the docket — one file per row. **PROPOSED, GATED, NOT EXECUTED.**

Filed 2026-08-14 against `docs/DOCKET.md` at `9daef4c9`.

**Status: this is a design plus its measurement, deliberately not a migration.**
The reason is in §5 and it is the same reason §7's repo reorganization is blocked: the
change is a large mechanical rewrite of the one file every agent in the fleet is appending
to, and doing it during is how you lose the thing you were protecting. Three concurrent
sessions had rows in flight in that file while this document was being written.

---

## 1. The defect, stated precisely

`docs/DOCKET.md` is one markdown file whose rows are appended by every agent. This lab's
commit rule is single-step pathspec — `git add <paths>` then `git commit -F <msg> -- <the
same paths>` — and **a pathspec commit carries whatever is in the WORKTREE for that path.**
It cannot carry half a file.

So when two agents have the docket open at once, whichever commits first sweeps the other's
in-flight rows into its own commit. Nothing is lost and the append-only rule holds. What
breaks is **attribution**: the commit message describes one agent's work and the commit
contains two agents'. Git history then misreports who wrote what, permanently, because
commit messages are immutable.

**Pathspec granularity is the whole cause.** No amount of care at the agent level fixes it.
The two agents who hit it today both handled it correctly and both flagged it, and it
happened anyway.

## 2. Measured, at `9daef4c9`

Frame: `git log --follow -- docs/DOCKET.md`, 64 commits touch the file. A docket row is one
markdown line, so an *edit* to a row emits a `+| D<n> |` line exactly like a *filing* does —
counting `+` lines counts edits as filings and inflates the answer roughly threefold. An ID
is filed in the first commit where its row appears; every later `+` on it is an edit.

| quantity | value |
|---|---|
| commits touching the docket | 64 |
| commits **filing** at least one new row | 36 |
| distinct rows ever filed | 80 (84 at the time of writing; the fleet is live) |
| commits filing ≥1 row their message does not name | **7 / 36** |
| rows filed without being named in their commit message | **14 / 80** |

**Those 14 are not 14 instances of the defect, and reporting them as such would be the
error this lab keeps catching.** Adjudicated:

- **9** (`D1`–`D9`, at `d5ca4695`, `7d9e4c51`, `6a2b3ea2`, `71a39c07`) predate the
  convention of citing IDs in commit messages at all. The first message to name an ID is
  `281a6dc9` ("D29-D31"). Their attribution is correct; only the ID is absent.
- **1** (`D60` at `f5f7126e`) is described in full in its own message, which is entirely
  about the round-5 dead-lever audit that D60 *is*. Correct attribution, uncited ID.
- **2 are genuine, undisclosed sweeps:**
  - `a8d6a33a` — the message says *"Seven docket entries from the round-6 claims audit"* and
    enumerates D32–D38. The diff files **nine**, D32–D40. **The message states a count its
    own diff contradicts**, which is the cleanest available signature.
  - `d6fafcf3` — message names only D77; the diff files D75, D76 and D77.
- **1 more was swept and correctly DISCLOSED**, so it is not a defect and is the model for
  §6: `c2ee8764` files D71–D74, names D72/D73/D74, and its body says plainly *"docs/DOCKET.md
  already carried an uncommitted D71 from a concurrent agent… a single-step pathspec commit
  of this file necessarily includes it. Kept intact per the append-only rule."*

**So the measured rate of the actual defect is 2 undisclosed sweeps in 36 filing commits.**
It is real, structural and worth fixing. It is not epidemic, and a fix priced for an
epidemic would be its own defect.

**A fourth instance was observed live rather than in history.** While this document was
being written, `docs/DOCKET.md` carried **D80, D81 and D82 — three complete rows, 7,793
bytes — uncommitted in the worktree from another session.** See §7.

## 3. The shape proposed

One file per row, table generated:

```
docs/docket/D0001.md          front-matter: id, filed, rung, owner, status
docs/docket/D0002.md          body: the finding, where found, what settles it
...
docs/DOCKET.md                GENERATED — header prose + the table, assembled from the shards
scripts/docket_build.py       the generator; also a --check mode that fails if the
                              committed table does not match the shards
```

Two agents filing at once then touch two different files. `git add docs/docket/D0083.md`
carries D0083 and nothing else. **The contention does not get managed; it stops existing**,
because pathspec granularity finally matches authorship granularity.

Zero-padding to four digits is deliberate: `D0079.md` sorts correctly in every tool without
a natural-sort dependency, while the ID itself stays `D79` everywhere it is cited.

## 4. What it costs — stated, because a proposal that hides its cost is not a proposal

1. **A generator, and a fourth place the truth can live.** `docs/DOCKET.md` becomes derived.
   If anyone hand-edits it the edit is silently destroyed on the next build, or worse,
   survives and diverges. This is mandatory, not optional: `docket_build.py --check` must be
   a `lab_check.py` gate that FAILs when the committed table does not reproduce from the
   shards. Without that gate the migration makes things worse, not better.
2. **~84 files created and one 279 KB file rewritten**, in a tree with live writers.
3. **Every reader of the docket changes.** `grep` over one file becomes a walk over a
   directory. Anything citing `DOCKET.md:<line>` breaks — measured: **8 line-anchored
   references**, at `LADDER_V_V15_ROUND6.md:409,433,445` and inside D42/D43/D44's own text.
   These are the only citations sharding can break, and they must be rewritten to cite IDs
   rather than line numbers *before* the move.
4. **The `D19-D20 note` row and the ID map in the header are not rows** and need hand
   placement in the generated header.

## 5. Why it is gated rather than done

The release conditions, modelled on §7's, which is blocked for exactly this reason:

1. **No agent holding uncommitted rows in `docs/DOCKET.md`.** Mechanically checkable:
   `git diff --quiet -- docs/DOCKET.md`. This was **false** the whole time this document was
   written.
2. One dedicated agent, one branch, one quiet window. Not a background task.
3. `scripts/docket_build.py` written, and its `--check` mode admitted by `lab_check.py`,
   **before** any shard is created.
4. The 8 line-anchored references from §4.3 rewritten to ID citations first, in their own
   commit.
5. `scripts/docket_citation_guard.py` PASSing before and after, with the citation inventory
   diffed and shown identical (§6).

**The migration is safe to do only when nobody is writing, and the whole point of the
migration is that people are always writing.** That is not a paradox — it is a scheduling
constraint, and the honest answer is a gate rather than a heroic merge.

## 6. Preservation — W-4, absolutely

**Nothing is renumbered. Nothing is reused. No ID changes meaning.** `D0079.md` contains the
row that is `D79` today, byte for byte. The migration is a `git mv`-shaped rearrangement of
where text lives, never of what an ID means.

This matters more here than anywhere else in the repo. Under W-4 the ID space cannot be
repaired retroactively, and **D43 is the standing record of what renumbering costs**: two
pointers in `V16_GRADE_ROUND5.md` that used to dangle now resolve *silently, to unrelated
live defects*. An independent sweep of the tracked tree at `7108825b` found **7 live
mis-resolving citations** of that class and **0 dangling ones** — including two D43 does not
list (`S1_PRIORS_PREREGISTRATION.md:608`, and a `D51` pointer whose intended row was never
filed at all).

The proof obligation is discharged mechanically, not by argument:
`scripts/docket_citation_guard.py` dumps every cue-qualified `D<n>` citation with its
resolution. The set before the migration and the set after must be identical. If one
citation changes resolution, the migration is wrong and is reverted.

## 7. What was rejected, and why

**An allocator** — a script that atomically claims the next free ID and writes a stub row,
so an agent cites an ID it already owns. Rejected on three counts. It **does not fix the
sweep problem at all**, which is the primary defect. To claim an ID it must *write into
`docs/DOCKET.md`*, i.e. perform exactly the contended write, and two allocators racing both
read max=82 and both write D83 unless a lock is added. And `lab_check.py` would skip it as
write-capable, so it could never be scheduled. Most decisively, **it is unnecessary**: the
guard reads the *working tree*, so writing your row before you cite it already gives you a
resolvable ID you own, with no new machinery. The row is the claim.

**A commit-time attribution check** — refuse a docket commit whose diff adds rows the
message does not name. Rejected *as a gate*, and this is the closest call. It would be
permanently red on the 14 historical rows of §2, whose commits are immutable and can never
be made green — D3's unclearable-floor shape, where a reader cannot tell a standing WARN
from a new one. Scoping it to a baseline date makes it maintainable but adds a floor to
manage. And it is a workaround for a shape that §3 deletes outright: once rows are separate
files, a commit *cannot* contain another author's row, so there is nothing to check. The
interim discipline is §8 instead, which costs nothing and is already demonstrated working.

**Doing the migration now.** Rejected per §5.

## 8. The interim discipline, until §3 lands

Costs nothing, needs no code, and `c2ee8764` already demonstrates it:

- **Allocate by writing the row, then cite it.** Never cite an ID you have not written a row
  for — that is reserving a number by citation, and a stranger will take it. The guard
  enforces this and passes on the legitimate case, because it reads the worktree.
- **Before committing `docs/DOCKET.md`, diff it against `HEAD` and read what you are about
  to carry.** `git diff HEAD -- docs/DOCKET.md`. Note that plain `git status` reads stale
  under concurrency here.
- **If you are carrying another agent's rows, say so in the commit message, by ID.** Both
  texts stand, nothing is renumbered, and the message is widened to match its contents.
  Attribution is then correct even though the commit is not clean.
