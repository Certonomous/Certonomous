# V16 — GRADE ROUND 7 (the closing round, graded)

**Subject:** `64281b6b`. **Graded at:** `64281b6b` — ancestry OK, and the content diff over
`scripts/self_audit.py`, `campaign/V16_PRECISION_SET.py`, `campaign/V16_GRADE_ROUND6_PROBES.py`
and `sdk/tests/test_rank_claim_surfaces.py` is **empty (0 bytes)**, because `HEAD` *is* the
subject. Suite at the subject: **109 passed in 533.99s**.

> **Notation.** This file never writes a board surname next to an ordinal. `{e1}`..`{e4}` mean
> "the entrant the published board puts at rank 1..4". Docket D4 has caught five agents in five
> files by writing a rank claim as a literal into a record that the live guard then sweeps, and
> splitting a sentence into word tokens is *not* enough — the guard collapses whitespace and
> `_PLACE_CLAUSE` does not cut on a comma. As of `64281b6b` this file and
> `campaign/V16_GRADE_ROUND7_PRECISION_SET.py` both sweep clean, with a planted-fault positive
> control proving the sweep can see one.

---

## VERDICT: the rung does NOT close this round. Two MATERIAL findings.

Both are about the same thing, and it is the thing the rung's author named against itself. The
regressions are gone, the enumeration binds, L-76 is closed, and the probe counts are exactly
as reported — that work is sound and is not in question. What is in question is the **frame put
around the precision figure**, which is the one claim this rung now rests on.

---

## 1. THE INDEPENDENT PRECISION SET — the primary task

Built blind: `campaign/V16_PRECISION_SET.py` was not read, and neither were the `_place*`
pattern definitions, until after the sentences below were written and measured. The only inputs
were the ruling's problem statement and the entry-point signature.

**43 sentences in 11 classes.** Four classes (linear-algebra rank, dated history, quotation,
cross-sentence) are named in the ruling itself and so are *not* fully external; seven are the
grader's own taxonomy — reduced relative, idiom, ordinal-of-something-else, bibliography,
abbreviation, other-named-board, and negation/interrogative.

The author's admission rule is applied unchanged — only sentences in which a rule-A pattern
actually matches an expression enter the denominator, so the figure cannot be flattered by
sentences the guard never looks at. **18 of the 43 were not looked at and are excluded.**

| sample | built by | pattern list in hand? | falsely faults |
|---|---|---|---|
| the author's non-placement set | this check's author | **yes** | **20 of 41 (49%)** |
| the grader's non-placement set | an independent grader | **no** | **19 of 25 (76%)** |

**Fisher exact two-sided p = 0.040.** Wilson 95% intervals: grader 57–89%, author 34–64%. The
grader's *lower* bound sits above the author's point estimate. The divergence is real at the
conventional threshold, and it is 27 points wide.

**The split that says why**, and it is the sharpest number in this grade:

| classes | admitted | falsely faulted |
|---|---|---|
| the four the RULING names | 15 | 9 (60%) |
| the seven the GRADER invented | 10 | **10 (100%)** |

On shapes generated without the pattern list, the guard falsely faulted **every single
sentence it looked at.** That is L-74 measured rather than argued.

**Controls.** Six positive controls — plain wrong placements pinned on a named entrant, one of
them naming a position the board does not have — all faulted. Two *negative* controls —
**correct** placements — both stayed silent. The negative controls matter: positive controls
alone cannot distinguish a working guard from one wedged open, and a guard that faults
everything would score perfect recall and zero precision.

**Disjointness (R-ISOLATE part 2), asserted and not trusted.** Exact normalised overlap between
the two sets: **NONE**. Asserted by `test_the_author_and_grader_samples_are_disjoint`.
Diagnostic on template reuse (L-66): 5 shared 5-grams out of 330, **1.5%**, and all five sit in
two sentences — one of which is round 6's own probe, quoted verbatim in the ruling section the
grader had to read to get the problem statement. That contamination is disclosed rather than
hidden, and it is **measured, not waved away**: dropping both contaminated sentences gives
**17 of 23 (74%)**, still 25 points above the published figure. The finding does not depend on
them.

---

## 2. FINDINGS

### MATERIAL 1 — "a WORST CASE on hard sentences" is a false written claim

The generated verdict paragraph states, of 20 of 41:

> *THE SET IS ADVERSARIAL AND NOT REPRESENTATIVE — it is weighted toward the shapes that have
> already broken, so 20 of 41 is a WORST CASE on hard sentences and not a corpus rate.*

**Why it is material.** An outside reader takes "worst case" as a bound: *the guard's false-FAULT
rate on hard sentences does not get worse than this.* Another honest adversarial set, same board,
same admission rule, disjoint sentences, gives 76%. The hedge was written to stop a reader
overstating the number in the pessimistic direction; it is wrong in the **optimistic** direction,
which is the direction this rung exists to stop being wrong in.

This is not a shape the guard mis-handles — it is a **claim in the record that execution
falsifies**, which is L-76 exactly, and the ruling says plainly: *"A ruling that a claim may be
bounded is not a ruling that a claim may be false."* This rung has re-opened L-76 three times
already for absolutes of this kind. It is the fourth.

The lab's own reach paragraph already knows better. It says, of the recall figures, *"forty-odd
sentences is a small one and two honest sets disagree by twenty points"* — and it therefore
publishes **three** reach rows, each naming who built it and whether they were blind. The
precision figure publishes **one** row, from the least independent possible source, and calls it
a worst case. The fix is the design the author already used one screen higher.

### MATERIAL 2 — two false-FAULT shapes are neither counted nor named

The ruling permits a shape to stand **knowingly accepted** *provided it is counted in the figure
and named in the list*. That proviso is the entire basis on which the seven E2 shapes are allowed
to remain, and it is honoured for them. Two shapes found here are outside it:

- **negation and interrogative.** `{e1} is not ranked 3rd, whatever the mirror says.` and
  `Is {e2} really rank 1? The board says otherwise.` Both produce rule-A faults. The ordinal is
  denied or questioned, never asserted. No class in the nine describes this.
- **a placement on a different, explicitly named ranking, in the present tense.**
  `{e1} sits at position 2 in the citation ranking, not the closure board.` Rule-A fault. This is
  not `dated-history` — nothing about it is dated, and the sentence names the other board *and*
  disclaims this one in the same breath.

**Checked against the other list too, not just the enumeration.** The verdict line's numbered
`BLIND TO, LARGEST FIRST` list runs to nine items, and neither shape is in it. Item (9) is
*dated history* and covers only that; item (5) is scoped to rule B; item (6) is adjudication
proximity. There is **no item anywhere stating that the guard cannot tell which board a
placement refers to**, which is the more general gap the other-ranking sentence exposes.

**Why it is material.** The published text reads *"IN THESE SHAPES, every one of which is
KNOWINGLY ACCEPTED"*, which a reader takes as the inventory. Two of the nine-class enumeration's
own omissions are shapes a travelling submission document would plausibly contain — a citation
ranking, a denial — and a rule-A fault on a travelling surface is **FAIL severity** by the
guard's own reckoning. Neither is counted; neither is named.

**And the mechanism is worth more than the instances.**
`test_every_false_fault_class_is_counted_and_named` binds *tightly* — it is a dict equality in
both directions plus a sum, so a shape cannot be counted in the figure and left out of the list.
Verified by reading and by the numbers below. But **its denominator is the author's set**, so it
can only enforce the proviso over shapes the author already thought of. The proviso is
self-certifying one level up: the same L-74 circularity, moved from the figure to the test that
guards the figure. That is why an external set was the right thing to ask for.

### RESIDUALS

- **The two `ABBREV` false faults** (`{e2} et al. Rank 4 …`). Counted and named — the
  `abbreviation` class carries 2, and the author states the cost as exactly one added false FAULT
  bought against one recovered real placement. Counted and named is a residual by the ruling's own
  terms, and this grade does not reopen the rung for it.
- **The four `DATED`, three `QUOTED`, four `REDUCED` and two `LINALG` false faults** in the
  grader's set. All four classes are named in the enumeration with counts. Residual — they say the
  published figure is too small, not that the list is wrong, and finding 1 already carries that.
- **The precision row has no `blind` flag exposed in the table the way `_PLACE_REACH` does.**
  `_PLACE_PRECISION` carries the boolean and the generated sentence renders it honestly. Cosmetic.

---

## 3. THE OTHER VERIFICATIONS, ALL BY EXECUTION

**Enumeration binds and equals the measurement.** Declared
`{reduced-relative 4, linalg-head-unlisted 4, quotation 3, dated-history 3, abbreviation 2,
coordination 1, cross-sentence 1, idiom 1, bibliography 1}` — sum **20**. Measured per-class
breakdown over the committed sentences: **identical dict**, sum 20, equal to
`_PLACE_PRECISION[4]`. The test asserts dict equality *both ways* plus the sum, so a shape cannot
be counted in the figure and omitted from the list. **Binds, within its set** — see MATERIAL 2.

**Regression 1, structural boundary — fixed, controls hold.**

| control | expected | now |
|---|---|---|
| FB across a markdown heading / list item / table cell | silent | silent (×3) |
| FB control same gap, full stop present *(punctuated twin)* | silent | silent |
| FB control same gap, semicolon present *(punctuated twin)* | silent | silent |
| FB control round-5 FN, apposition | FAULT | FAULT |
| FB control round-5 FN, subordinate clause | FAULT | FAULT |

Both round-5 false negatives still fault, so the fallback was fixed and not deleted.

**Offsets provably unmoved — verified independently, not read.** Over **859 tracked `.md` and
`.py` surfaces**, `_place_flatten` and the plain collapse it replaced produce strings of
**identical length on every one** (0 mismatches), differing at 66,315 positions, **all of them a
newline standing where a space stood**. The claim is stronger than "no verdict moved" and it
holds.

**Regression 2, abbreviation period — fixed, controls hold.** The two real wrong placements after
`et al.` fault again (`E4 over-fix, abbreviation then a bare ordinal` / `… then an
ordinal-plus-noun`, both expected FAULT, both FAULT). Both `E4 control still binds` probes still
bind. All **six** round-5 boundary shapes stay silent. No over-fix: the guard still binds.

**L-76 — closed, and the corrected test reddens in both directions.** Mutation-tested, cache
cleared, control and mutant in the same invocation:

| cell | result |
|---|---|
| control, unmutated | **1 passed** |
| erase a falsified claim from the source | **1 failed** — *"was deleted rather than corrected; L-76 wants the falsified claim RECORDED"* |
| keep the claim, neutralise its falsification markers | **1 failed** — *"appears with no falsification beside it — it is being asserted again, not quoted"* |
| restored | **1 passed**, `git diff` clean |

The author's report that the *first* version of this test was itself wrong — asserting the
strings absent, which would have destroyed the record L-76 exists to keep — is correct, and the
corrected test closes both directions. This is the round's best piece of work.

**Probe counts — all four exact.**

| | reported | measured |
|---|---|---|
| round 6 disagreeing | 7 of 24 | **7 of 24** |
| round 5 disagreeing | 0 of 20 | **0 of 20** |
| author precision | 20 of 41 | **20 of 41**, controls missed 0 of 5 |
| recall rows | unchanged | `(45, 40→20)`, `(46, 37→14)`, `(45, →42)`, rule B `5 of 5` |

**The "knowingly accepted" proviso, verified where it is claimed.** All seven round-6
disagreements are E2 shapes — three reduced-relative, three linalg-head-off-the-list, one
coordinated subject. Each maps onto an enumeration class that carries a count
(`reduced-relative 4`, `linalg-head-unlisted 4`, `coordination 1`), and each is counted in the
20. **The proviso holds for all seven.** They are residuals, not findings, and this grade does
not reopen the rung for them.

---

## 4. R-VALUE VERDICT

**V16 does not close this round.** Per finding, *would this change what an outside reader
believes about the guard?*

- A reader told *"worst case 49% on adversarial sentences"* believes the guard's false-FAULT rate
  is bounded near half. An independent set says 76%, p = 0.040, with 100% on the classes the
  author had no hint of. **That changes the belief.** Material.
- A reader told *"in these shapes, every one of which is knowingly accepted"* believes the nine
  classes are the inventory. Two more shapes fault, uncounted and unnamed, one of them
  present-tense and plausible on a travelling surface. **That changes the belief.** Material.

Neither finding touches the guard's code, and neither is a regression. Both are about the frame
around a number, which is precisely what this rung chose as its closing condition — *"here is what
I cost, measured."* A cost stated too low is the one way that closing condition can fail, and it
failed in the specific direction the author predicted it would.

**The remedy is small and the author already owns the pattern for it.** Make `_PLACE_PRECISION`
a multi-row table exactly as `_PLACE_REACH` is, with the grader's row and its `blind=True` flag
beside the author's `blind=False`; delete the words "a WORST CASE" and let two disagreeing rows
say what one row cannot; and either enumerate the two new shapes with their counts or state that
the enumeration is scoped to the author's set. That is one round of work, and the round after it
should close.

**Note for the chief on the two-consecutive-rounds rule.** This grade is not clean, so it does
not supply the second of the two. But the finding is *not* the guard being newly wrong — it is
the guard's published cost being 27 points optimistic, discovered exactly where the author
pointed. A rung whose author names its weakest point and is then proved right about it is a rung
behaving correctly. Recommend one more author round scoped to the frame only, then a grade that
re-runs the set committed here — which now recomputes, so round 8 cannot go stale.

---

## 5. WHAT WAS FILED

- **`docs/DOCKET.md` D27** — the precision denominator is single-sourced and its "worst case"
  framing is falsified by an independent set.
- **`docs/DOCKET.md` D28** — the proviso's guard test is scoped to the author's own set, so it
  cannot see a shape the author never thought of.
- **`LESSONS.md` L-82** — a held-out set built by the party being measured understates the cost,
  and the size of the understatement is measurable by building a second one.
- **`campaign/V16_GRADE_ROUND7_PRECISION_SET.py`** — the set, its controls, and its measurement
  interface, recomputed by the suite rather than transcribed (L-79).
- **`sdk/tests/test_rank_claim_surfaces.py`** — `test_the_author_and_grader_samples_are_disjoint`
  and `test_the_grader_set_cannot_be_padded_or_wedged`.

**Suite: 111 passed** (109 at the subject, +2 added here).
