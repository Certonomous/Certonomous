# V15 round 5 — cross-surface number reconciliation for the V16 rung

**Verdict: the reach correction landed on the code and left its copies. Two
surfaces still publish a superseded headline as current; one earlier record
carries a withdrawn pairing unmarked; one carries a claim its own successor
overturns. The `.tex` / PDF pair is clean. Nothing that travels is affected.**

Read-only pass. I wrote this file and touched nothing else: `scripts/self_audit.py`
and its tests belong to the guard's author, and `docs/PRODUCT_LIST.md` and
`LESSONS.md` to the chief, all three being edited concurrently. Every finding
below is a report with an owner, not a fix.

---

## 0. Frame — the thing this lab keeps forgetting to state

| | |
|---|---|
| **Commit** | `038b36da` (2026-08-11T07:15:10Z). Working tree was clean but for `sdk/.filming-keepalive` when the sweep was taken |
| **Outside the frame** | by the time this was written the author had modified `scripts/self_audit.py`, `sdk/tests/test_rank_claim_surfaces.py` and `campaign/V16_AUTHOR_HELDOUT_SET.py` in the working tree. **Those edits are not in this reconciliation** — stated because a frame that goes stale inside its own pass is the failure this document is about, and I would rather say it than have it found. |
| **Benchmark board** | `deb91557`, parsed live: reissmann 1, wu 2, liu 3, montoya 4 |
| **Denominator** | **20,559** paths from `git ls-files`; **18,833** read as UTF-8 under 4 MB |
| **Excluded, counted** | 276 over 4 MB · 1,450 non-UTF-8 |
| **V16 surface set** | **14** files whose whole text matches the rung's own tokens |
| **Match method** | whole file, whitespace collapsed to single spaces, so a line break cannot hide a phrase (L-61) |
| **Tool** | Python over `git ls-files`. **Not `grep -r`**: `grep` here is a shell function running `ugrep --ignore-files`, which skips gitignored paths, and this repo tracks **6,938 files that are also gitignored** (L-75) |

**The V16 surface set, in full** — `LESSONS.md` ·
`demo-output/website/CLOSURE_CHALLENGE_STATUS.md` ·
`demo-output/website/benchmarks.html` ·
`campaign/LADDER_V_TRIPLE_VERIFICATION.md` · `campaign/V16_AUTHOR_HELDOUT_SET.py` ·
`campaign/V16_GRADE.md` · `campaign/V16_GRADE_HELDOUT_SETS.py` ·
`demo-output/website/closure_challenge_round5_qcr.json` ·
`demo-output/website/latex/closure_challenge_report.tex` ·
`docs/INSTRUMENT_INTEGRITY_LEDGER.md` · `docs/LEDGER_HEADLINE_AUDIT.md` ·
`docs/PRODUCT_LIST.md` · `scripts/self_audit.py` ·
`sdk/tests/test_rank_claim_surfaces.py`.

## 1. What everything must reconcile against

Recomputed live at `038b36da` from the committed sentence files, not read from
any record:

| figure | value now | recomputes? |
|---|---|---|
| grader's first set, current patterns | **20 of 45 (44%)** | yes, from `V16_GRADE_HELDOUT_SETS.py` |
| author's set, current patterns | **14 of 46 (30%)** | yes, from `V16_AUTHOR_HELDOUT_SET.py` |
| grader's adversarial set | **42 of 45 (93%)** | yes |
| adversarial positive controls missed | **0 of 3** | yes |
| rule B smoke test | **5 of 5** | **no — no committed sentences** |
| `before` column (two original patterns) | 40 of 45 · 37 of 46 | **no — history, marked as such** |
| pattern families | **11**, from `groupindex` | counted |
| board margin | **2 table blocks, 1 qualifies** | computed |

**The shipped verdict line, generated, reads:**

> *"HEADLINE, on ONE FIXED SET measured before and after so the two ends are
> comparable — the grader's first set … 40 of 45 (89%) missed became 20 of 45
> (44%)."*

It contains **no `53%`, no `96%`, no `24 of 45`, no `43 of 45`.** That is the
reference against which §2 and §3 are stale.

## 2. Item 1 — the retired "89% → 30%" pairing

**Not present anywhere as a live claim.** Four surfaces contain the string, and
every one is a retraction or a quotation of the retraction:

| surface | status |
|---|---|
| `scripts/self_audit.py` (module comment) | retraction record — *"the first published pair was '89% -> 30%', which is an OUTSIDE measurement…"* — **correct** |
| `campaign/LADDER_V_TRIPLE_VERIFICATION.md` | *"…originally published here as '80% → 30%' is withdrawn as a headline"* — **correct** |
| `campaign/V16_GRADE.md` | my own findings quoting it — **correct** |
| `docs/PRODUCT_LIST.md` line ~3470 (entry of 06:20) | *"Then nine families were added: **80% → 30% missed, with precision still exactly zero**"* — **a live restatement, unmarked at the point of claim.** The withdrawal is recorded three entries later. Owner: **chief** |

**Finding 2.1 — one unmarked survivor.** The chief's log is chronological, so the
supersession is discoverable, but a reader landing on that bullet reads the
withdrawn pairing as current. The remedy already exists in the same file: the
`111/421/63` line is struck **in place, with its reason**, which is the right
treatment and should be applied here.

## 3. Item 2 — every reach figure, everywhere it appears

**Finding 3.1 — this is the main finding. Two surfaces publish `89% → 53%` and
`96%` as the *current* headline. Both are superseded.** `53%` is 24 of 45 and
`96%` is 43 of 45: measurements of an **intermediate** guard, taken before rule B
was widened in `c663c774`. They are not history-that-cannot-be-recomputed — they
recompute today to **44%** and **93%** — so under this round's rule they are
plainly stale, not marked.

| surface | line | text | verdict | owner |
|---|---|---|---|---|
| `campaign/LADDER_V_TRIPLE_VERIFICATION.md` | 300–302 | *"the widened guard misses **53%** … the honest headline is … **89% → 53%** … gives 96%"* | **STALE** — should be 44% and 93% | guard's author |
| `docs/PRODUCT_LIST.md` | 3517, 3519 | *"put the widened guard at **53% missed** … **89% → 53%** on one fixed set"* | **STALE** | chief |
| `docs/PRODUCT_LIST.md` | 3555–3556 | *"the widened guard misses **53%**. The published headline is now that one fixed set measured at both ends — **89% → 53%** — with the adversarial set's **96%** beside it"* | **STALE, and it asserts currency** — *"is now"* is false against the shipped line | chief |
| `docs/PRODUCT_LIST.md` | 3596, 3598 | *"The headline is now like-for-like: **89% → 53%** … the adversarial **96%** … **generated from one provenance table, so it cannot drift**"* | **STALE, and the sentence claiming it cannot drift is the one that drifted** | chief |
| `campaign/V16_GRADE.md` §8 | — | `53%`, `96%` | **superseded and marked** — §9 carries an explicit before/after table naming both as stale. Marked in a later section, not adjacently | me → third party |
| `campaign/V16_GRADE_HELDOUT_SETS.py` | docstring | *"That table records **24 of 45** … re-measured … it is 20 of 45"* | **STALE IN A NEW WAY** — the table no longer records 24; my description of its state was overtaken by the author's fix | me → third party |
| `scripts/self_audit.py` `_PLACE_REACH` | — | 20 · 14 · 42 | **CURRENT**, and recomputed by test | — |
| `campaign/V16_AUTHOR_HELDOUT_SET.py` | — | no reach figures asserted | n/a | — |

**Finding 3.2 — the exact irony, stated because it is the reusable part.** The
sentence *"All of it generated from one provenance table, so it cannot drift"*
appears on a surface where the figure **had already drifted**. Generation
prevents drift **between the code's own surfaces**; it does nothing for prose
that copied the number out. That is the same one-level-short failure the author
recorded for the table itself, occurring one level further out.

**Finding 3.3 — `30%` is current but unattributed in one place.**
`sdk/tests/test_rank_claim_surfaces.py`'s class docstring reads *"measured at 89%
… and my own set at 80%, widened since to **30%** but never to nothing."* 30% is
still correct **for the author's 46**, but stated without its sample it reads as
the check's reach, which is the precise defect the pairing was withdrawn for.
Owner: guard's author. Not stale; under-attributed.

**Finding 3.4 — `5 of 5` cannot be reconciled and I am not going to pick a side.**
It has no committed sentences, so it cannot be recomputed; and it is not marked
as history, because it is presented as a current smoke test. It is neither
"agrees with what recomputes" nor "explicitly marked as history". It is the one
figure in this rung that is **unresolvable as recorded** — already open as
exception 3 of grade four, and repeated here because the reconciliation rule
catches it independently.

## 4. Item 3 — denominators and their frames

| figure | appears on | carries its filter? | carries its commit? |
|---|---|---|---|
| 1375 opened / 126 naming / 591 surveyed | live verdict line; `V16_GRADE.md` §10 | **yes** — the verdict states the selection rule in words | **no** — neither states the commit it was taken at |
| 503 → 573 placement expressions, 978 surfaces | `V16_GRADE.md` §8–§9; `PRODUCT_LIST.md` | partially — "tracked UTF-8 under 4 MB" | **no** |
| 974 files (rival-rule denominator) | `V16_GRADE.md` §3; `PRODUCT_LIST.md` | yes | **no** |
| **6,938** tracked-but-gitignored | `LADDER_V…md`; `V16_GRADE.md` §8.3; `PRODUCT_LIST.md` ×2 | **yes** — named as `git ls-files` vs `grep -r` | **no** |
| 111 / 421 / 63 | struck **in place with its reason** in `PRODUCT_LIST.md`; described as unreproducible in `LADDER_V…md` and `V16_GRADE.md` §2.4 | n/a — withdrawn | n/a |
| 36 absolutes / 17 surfaces | `LADDER_V…md`; `PRODUCT_LIST.md`; `V16_GRADE.md` §10.3 | **yes** — "docstrings, BASIS, REMEDIES, verdict line" | **no** |
| 22 tests / 21 failures | `LADDER_V…md`; `V16_GRADE.md` §2.3 | yes — isolated worktree at `862d2cff^` | **yes** |

**Finding 4.1 — every corpus figure in this rung states its filter and none
states its commit.** The counts move as the lab writes: the same rule returned
**503** at 03:47, **573** at 05:25 and **591** at 07:15. Any of those is right for
its moment and wrong for the others, and only one of the three citations
(the worktree one) names a moment. **This includes my own documents**, so it is a
finding against me as much as anyone. The verdict line is the good case and even
it is one field short: it prints the board's commit and not its own.

**Finding 4.2 — the 6,938 figure is sound and its frame is stated in words.**
`git ls-files` at `038b36da` reports 6,938 tracked-and-ignored paths; I
re-derived it this pass. The claim that the guard therefore does not inherit
L-75's blindness holds.

## 5. Item 4 — disagreements with the chief's record

Checked entry by entry against the code, my four grade sections, and live
recomputation. **The chief's grade-four entry is accurate**; I could not fault a
single one of its statements of my findings, including the ones against its own
earlier record. Four disagreements, in descending order:

**5.1 — `89% → 53%` and `96%` published as current, four places (lines 3517,
3519, 3555–3556, 3596, 3598).** Superseded by 44% and 93%. §3.1. This is the
same defect the chief's own next entry describes as *"the correction that lands
on one surface and leaves its copies"*.

**5.2 — *"All hold. No fourth absolute."* (line 3731) is overturned by the
immediately following entry**, which records *"THE L-76 PATTERN HELD A FOURTH
TIME."* Both entries are dated the same day; the earlier one carries no
supersession marker at the point of claim. A reader who lands on 3731 reads a
false statement about the current state. The chief's own `111/421/63` strike
shows the correct treatment.

**5.3 — *"the three `BaseException`s propagate exactly as documented"* (grade-four
entry) overstates by one.** The docstring names **two**: *"A `KeyboardInterrupt`
or a `SystemExit` still propagates, as it must."* `GeneratorExit` is consistent
with the claim's scoping to `Exception`, but it is not documented. My §10.1 said
"as documented" of the two and listed `GeneratorExit` separately, on the scoping
argument. Small, and it runs in the generous direction.

**5.4 — *"State: 1384 passed"* is unverified by me.** I ran only
`sdk/tests/test_rank_claim_surfaces.py` (**79 passed**, reproduced twice at 286s
and 287s), which matches the chief's "79 in the guard file". I did not run the
full suite and I am not going to assert a number I did not take. Recorded as
unchecked, not as disputed.

**What I checked and found correct in the chief's record:** the crash-boundary
account (16/16, scoped to `Exception`, the `__str__` construction declined); the
recompute-by-mutation account (20 → 19, restored byte-for-byte); all three open
exceptions of grade four, including the linear-algebra count of **four** digit
instances; the `111/421/63` strike and its reason; the L-75 confirmation; the
board-margin trade and its operational note; and the V15 routing summary.

## 6. Item 5 — the `.tex` sentence and its compiled PDF

**Both halves clean.**

| check | result |
|---|---|
| source sentence, whole-file whitespace collapsed | *"The published entry ranked second before round 5 — Wu & Zhang's SST-QCRC — carries the same untrained QCR2000 term."* |
| true against the parsed board? | **yes** — the board puts that entrant at rank 2 |
| guard faults on the `.tex` | **0 rule A, 0 rule B**; the expression is surveyed and bound correctly |
| `.tex` working tree vs `HEAD` | identical |
| PDF vs `HEAD` | identical; both last written by the same commit `98a39662` |
| PDF text extracted (`pdftotext`, 136,603 chars) | *"ranked second"* **present** · *"rank-2 entry"* **present** · **"rank-3 entry" absent** · **"runner-up" absent** |

**Finding 6.1 — the artifact carries the corrected text, not the pre-fix text.**
The two defect strings that were removed from the source in the V8 fix round are
absent from the compiled PDF, and the corrected forms are present. This is the
one place tonight where a corrected source and its built artifact agree, and it
is worth recording as the counter-example to the failure this round exists to
catch.

## 7. What needs changing, and who owns it

| # | change | owner | severity |
|---|---|---|---|
| 1 | `LADDER_V_TRIPLE_VERIFICATION.md` 300–302: `53%` → `44%`, `96%` → `93%`, or mark both as intermediate measurements | **guard's author** | the rung's own headline is wrong on the rung's own page |
| 2 | `PRODUCT_LIST.md` 3517/3519/3555–3556/3596/3598: same | **chief** | four copies, one of which asserts *"is now"* |
| 3 | `PRODUCT_LIST.md` ~3470: mark the `80% → 30%` restatement as withdrawn in place | **chief** | a withdrawn pairing reads as current |
| 4 | `PRODUCT_LIST.md` 3731: mark *"No fourth absolute"* as superseded in place | **chief** | overturned by the next entry |
| 5 | `V16_GRADE_HELDOUT_SETS.py` docstring: *"That table records 24 of 45"* no longer describes the table | **me → a third party** | my own stale description |
| 6 | `V16_GRADE.md` §8: an adjacent supersession note on `53%`/`96%` | **me → a third party** | marked, but only downstream |
| 7 | `test_rank_claim_surfaces.py` class docstring: attribute the `30%` to the author's 46 | **guard's author** | under-attributed, not stale |
| 8 | every corpus figure: add the commit it was taken at | **all three of us** | §4.1; systemic |
| 9 | `_PLACE_REACH_B` (`5 of 5`): commit its sentences or mark it unrecomputable | **guard's author** | already open as grade-four exception 3 |

**Nothing that travels is affected.** The submission package, `closure.html`, the
credentials wall, `benchmarks.html` and the `.tex`/PDF pair carry no stale reach
figure; every item above is a lab record or a code comment.

## 8. Found while not looking for it

- **The correction propagated backwards, not forwards.** `_PLACE_REACH` was
  corrected at `db096bb7` (06:56) and `LADDER_V…md` at 300–302 was written at
  `9f6d8a41` (06:04) — so the prose was *right when written* and the code moved
  under it. Every one of the six stale copies is that shape. **This is not a
  copy-paste failure; it is that the copies had no way to learn.** The
  fix that would actually close the class is the one already applied inside the
  code — generate the sentence — extended to the prose surfaces, e.g. a check
  that the rung text and the product record contain the string
  `_place_reach_sentence()` currently prints.
- **`docs/LEDGER_HEADLINE_AUDIT.md` is in the V16 surface set and nobody has
  mentioned it.** It matched on rung tokens. It belongs to another agent and I
  did not read past the match, per the write-boundary — but a headline audit that
  references V16 is a surface V15 should route to someone, and no list has
  included it.
- **`demo-output/website/closure_challenge_round5_qcr.json` and
  `benchmarks.html` are in the set too**, on `5 of 5` and board-rank strings.
  Both are case-level rank facts, not reach figures, and both agree with the
  board — but they are machine-read surfaces carrying placement language, and
  the guard's blind-spot list does not distinguish generated JSON from prose.
- **The three suite counts tell a consistent story and the first one carries its
  own caveat**: 35 → 57 → 70 → 79 in the guard file, and the chief's earliest
  entry already notes its full-suite total was *"taken from a tree eight agents
  were committing to"*. That caveat is the frame discipline §4.1 asks for, and it
  was applied once, early, by the chief, unprompted.

---

*Reconciled at `038b36da` by the agent that graded V16 four times and wrote none
of the guard, none of its tests, and none of the fixes. Read-only across the
repository; the only file written is this one. Items 5 and 6 above are defects in
my own documents and are routed away from me.*
