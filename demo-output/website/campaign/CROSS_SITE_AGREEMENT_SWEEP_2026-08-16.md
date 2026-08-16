# Cross-site agreement: characterisations struck on one surface and asserted on another

**ONE class of nine disagrees across live claim surfaces. It is the AR_14 best-on-board tie —
the same characterisation V10's repair struck in the submission package and on `closure.html`
— and it is still ASSERTED, unstruck, on four other claim surfaces. Eight classes agree, and
four of the five my instrument first flagged were its own artifacts, named below rather than
reported as findings.**

**No repairs were made and no rung was graded.** Several affected surfaces sit inside other
rungs' declared scope; R-CONVERGE forbids one pass closing two rungs, so the rung is named and
the decision is left to its grader. Swept 2026-08-16 at the pinned frame `8c01202f`. No solver
ran, no scoring call was made, the ledger stood at 6, nothing was sent, and `dist/`,
`demo-output/website/latex/`, `motorbike-video/` and `LAPTOP_SHOOT.md` were not written.

---

## 1. Why no existing instrument can see this class

Every checker this lab built grades a **site**: does this sentence carry a board identifier, is
this figure current, is this claim struck. **A defect that lives in the AGREEMENT between two
sites is invisible to all of them, because each site is individually fine.** The check
therefore runs over the **set**: collect every live instance of one characterisation across the
corpus, classify each instance's stance, and fail the **class** when the corpus asserts and
denies the same proposition unscoped.

**A characterisation is a claim about what happened, not a number** — *"the tie is gone"*,
*"we lead the board"*, *"is not any more"*. These carry **no stale literal**, which is why a
number sweep cannot find them and why `ACTIVE_RESEARCH.md:29` survived one and reopened V10.

## 2. The arm, and the floor

**Arm:** tracked blobs at `8c01202f` enumerated by `git ls-tree -r`, read in one
`git cat-file --batch`.

| | count |
|---|---|
| prose-bearing blobs **opened and scanned** | **1,883** ← the floor |
| enumerated non-symlink paths in that arm | 1,888 |
| symlinks skipped | 17 |
| binary / empty / undecodable / >4 MB | 5 |
| **non-prose extension, excluded and counted** | **18,854** |

**The exclusion is stated rather than silent.** A characterisation is prose; it cannot live in
a mesh file, a solver field or a prediction CSV. Scanning those with `[-\s]{1,20}` joiners is
where two earlier runs each spent ten minutes and returned nothing they could have returned.
**This is a FLOOR, not a population:** forms outside the nine class recognisers are not
counted, and the classes themselves were enumerated by hand.

## 3. Detection rules — all four, each learned by an instrument failing

1. **Continuation prefixes stripped with offsets preserved** — `>`, `> >` and list markers
   overwritten with spaces in place, same length, newlines untouched; every quotation comes
   from the unmodified text. Byte-length asserted per line and whole-text.
2. **`[-\s]{1,20}` joiners**, because a hyphen-split wrap (`best-on-\n> board`) defeats `\s+`
   *even after* the prefix repair.
3. **Sentence scope bounded on punctuation and paragraph breaks, NEVER on a bare newline.** A
   `\n` split severs the negator from *"there was **no** best-on-\nboard tie"* and reports a
   DENIAL as an ASSERTION — in this class, the error that **manufactures** a contradiction.
4. **Emphasis blanked offset-preservingly, and ONLY AFTER strike detection.** `**` is neither
   whitespace nor a hyphen, so `the **best-on-board tie** is gone` and a plain-text denial
   elsewhere would read as one instance rather than two. Reversing the order would eat `~~` and
   turn struck text into live text. `~~` is never blanked; `_` is never blanked, because this
   corpus's identifiers are full of it (`AR_14_Ret_180`).

### 3.1 Controls — planted by line index, read back by SLICING at that index

| control | result |
|---|---|
| plain | **FOUND** |
| wrap (newline) | **FOUND** |
| blockquote-wrap | **FOUND** |
| hyphen-split | **FOUND** |
| **emphasis-split** (`**best-on-board**`) | **FOUND** |
| **emphasis-mid** (`best **on** board`) | **FOUND** |
| negative (`a best seat in the house`) | **correctly rejected** |
| **struck negative** | **STRUCK**, zero gain to the asserted population |
| **ORDERING control** — emphasis *inside* a strike | **STRUCK** (LIVE here would prove emphasis was blanked before strike detection) |

**`scripts/control_kind.py` returned RECOGNITION** from the evidence, never a typed label:
*six mutually independent forms, all found; one negative correctly rejected.*

**Both false zeros were reproduced before they were fixed:** blockquote-wrap **NOT FOUND**
without the prefix repair and **FOUND** with it; hyphen-split likewise.

**And rule 3 was controlled against its own failure mode.** On the probe *"…so there was no\n
best-on-board tie on this AR_14 duct to lose."*, punctuation scope returns **DENIED_SCOPED**
and a bare-newline scope returns **ASSERTED_UNSCOPED** — the false contradiction, reproduced
deliberately.

### 3.2 Known-case validation on real production data

| frame | stances | verdict |
|---|---|---|
| `38cd036f` **pre-repair** | 2 DENIED_UNSCOPED, 1 ASSERTED_UNSCOPED, 1 ASSERTED_SCOPED | **CONTRADICTION**, naming `:173` and `:192` asserted against `:118-119` denied |
| **HEAD** post-repair | 2 DENIED_UNSCOPED, 2 STRUCK, 1 DENIED_SCOPED | **AGREES** |

**This instrument shares no code with the V10 fifth grader's and reaches the same two sites.**
That is a third independent recogniser over a third population (D49), not a corroboration by
construction.

---

## 4. Per class — never per site

**Two figures are reported for every class: the raw stance counts over all 1,883 blobs, and
the counts restricted to CLAIM SURFACES.** The restriction is D255's identity, not a policy —
*quoting a claim in order to strike, grade or refute it is not making the claim*. Almost every
raw hit lives in a grade document, a docket row or a test fixture that quotes the
characterisation in order to adjudicate it; counting those would manufacture a contradiction
out of the lab's own paperwork.

| class | raw A/D | on claim surfaces | verdict |
|---|---|---|---|
| **AR14_BEST_ON_BOARD_TIE** | 26 / 38 | **5 asserted, 5 denied surfaces** | **DISAGREES — real** |
| MODEL_IS_BEST_ON_SOME_CASE | 0 / 40 | 0 asserted | agrees |
| RANK_1_IS_OFFICIAL | 12 / 47 | 1 asserted | **artifact — see §5** |
| LEAD_IS_DECIDED | 0 / 87 | 0 asserted | agrees |
| RVALUE_CONDITION_NEVER_MET | 0 / 11 | 0 instances | agrees |
| WORST_CASE_ON_HARD_SENTENCES | 8 / 6 | **0 instances on claim surfaces** | agrees (lives only in grading records) |
| TWO_ROWS_DIFFER_ONLY_IN_BUILDER | 0 / 11 | 0 instances | agrees |
| NOTHING_TRAVELS_AFFECTED | 13 / 19 | 1 / 1 | **artifact — see §5** |
| AR14_TIE_WAS_FOR_SECOND | 19 / 5 | 3 / 1 | **artifact — see §5** |

**Three classes are notable for agreeing.** `MODEL_IS_BEST_ON_SOME_CASE` and
`LEAD_IS_DECIDED` return **zero** unscoped assertions anywhere in 1,883 blobs against 40 and 87
denials — the lab states *"best on no single case"* and *"not statistically decided"*
consistently, which is the treatment the failing class does not get.
`WORST_CASE_ON_HARD_SENTENCES` and `TWO_ROWS_DIFFER_ONLY_IN_BUILDER` survive **only inside
grading records**: both withdrawn absolutes were struck at their sources and now exist purely
as history, which is L-76 working.

---

## 5. THE ONE REAL DISAGREEMENT, and the surfaces named

**Class `AR14_BEST_ON_BOARD_TIE`: the corpus both denies and asserts that `AR_14_Ret_180` held
a best-on-board tie.** The denial side is the newly repaired material —
`DESCRIPTION_DOCUMENT.md:118-119` (*"was never best on board … there was no best-on-board tie
on this case to lose"*) and `closure.html`, which strikes the characterisation at five sites.
**The assertion side is four claim surfaces the repair never reached**, each opened by hand:

| surface | the live, unstruck assertion | inside which rung's criterion? |
|---|---|---|
| `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:617-621` | *"the pre-registration said … that round 4's 0.00003-level **best-on-board tie** on `AR_14_Ret_180` was put at risk"* — reported speech with no marker that the characterisation is now known false | **not** in V10's five |
| `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1239` | *"**The `AR_14_Ret_180` best-on-board margin collapsed from 0.0022 to 0.00003**"* — **carries a repair parenthetical on the next line**, so the identifier reached it and the characterisation did not: D294's shape exactly | **not** in V10's five |
| `demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1273` | *"at round 3 it was … and **best on board** on `AR_14_Ret_180`"* — the sentence's *"4th of 5"* implies the four-entry denominator but never names a board | **not** in V10's five |
| `demo-output/website/latex/closure_challenge_report.tex:860-862` | *"the rule freeze recorded that round 4's 0.00003-level **best-on-board lead** … was put at risk"* | **`.tex` is another rung's and a do-not-touch path here** |

**Re-derived, not quoted, so the disagreement is anchored to arithmetic rather than to a peer's
verdict:** `ast.literal_eval` on the `LIVE_BOARD` assignment node — parsed, never imported —
joined to `round5_per_case_full` and `round4_per_case` puts **Yang first at 0.0250** on
`AR_14_Ret_180`, round 4's `0.0325` at **2 of 7** tied with Reissmann, round 5's `0.035339` at
**4 of 7**. The best-on-board reading was true only of the superseded four-entry `deb91557`
clone.

**One flagged hit on a claim surface is a false positive and is excluded:**
`docs/PRODUCT_LIST.md:2413` names *"the best-on-board count against the per-case rank fields"*
as a **category of sentence that was traced**, asserting no value.

**I do not rule on any of these sites.** `PRODUCT_LIST.md` and the package are inside V10's
declared criterion; the `.tex` is inside another rung's and is a path this pass may not write.
**The class is filed; the rungs are named; their graders decide.**

### 5.1 The three classes my instrument flagged and I am NOT reporting as findings

Reported because a sweep that hides its own false positives has converted a range into a point
estimate.

- **`RANK_1_IS_OFFICIAL` — recogniser design error, mine.** Its `core` pattern matches the
  *caveat* phrases (`scored locally`, `unsubmitted`), so a surface **carrying** the caveat
  scores ASSERTED unless it also carries a negator. `CLOSURE_CHALLENGE_STATUS.md:647`'s table
  row reads *"ours, round 5 (UNSUBMITTED, scored locally…)"* — that is the disclosure, i.e. the
  **opposite** of the proposition. **No disagreement exists; the pattern is inverted.**
- **`AR14_TIE_WAS_FOR_SECOND` — rule 3's failure one level down.** `closure.html:196` reads
  *"what was … lost was a tie for second, **not** for best"*; the negator belongs to the
  neighbouring clause, and the sentence AGREES with the three it was scored against.
  **Sentence scope is not clause scope, and this instrument does not reach clauses.**
- **`NOTHING_TRAVELS_AFFECTED` — time-indexed facts, not contradictory ones.**
  `PRODUCT_LIST.md:3009` quotes a guard's verdict string inside a critique; `:3698` records a
  later clean run. Two true statements about two moments.

---

## 6. What this establishes, and what it does not

**Establishes:** the class the V10 blocker belonged to has **at least one further live
instance set**, spanning four claim surfaces the repair did not reach — so the repairing
agent's own generalisation was correct, and the check that finds it must run over the set.

**Does not establish:** that these four sites are defects. Three are reported speech or dated
history, and this lab has ruled repeatedly that a dated record which recomputes for its own
date is not stale. **Whether reported speech must carry the correction is a ruling, not a
measurement**, and it is not mine.

**Falsifiers.** The class verdict falls if a reader shows the four assertions are adequately
scoped by their own sentences — the scoping words are absent, so this is checkable in one pass.
The floor falls if a characterisation form exists outside the nine recognisers; the control is
RECOGNITION over six independent forms, which bounds that risk without removing it. And the
whole per-class method falls if D255's identity is narrowed, since 21 of the 26 raw assertions
in the failing class are grading records excluded under it.

---

*Swept 2026-08-16 at `8c01202f` by an agent that wrote none of the four surfaces named in §5.
Every figure re-derived by parsing an assignment node, never by importing a module and never by
quoting a document. Controls planted by line index into scratchpad copies and read back by
slicing at that index; RECOGNITION established by `scripts/control_kind.py`; both wrap false
zeros and rule 3's false contradiction reproduced before they were repaired. `__pycache__`
purged before measuring. No listing that was read was piped. Nothing repaired, no rung graded,
no guard tuned, no solver run, no scoring call made; the ledger stands at 6.*
