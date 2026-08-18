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

## 7. THE REPORTED-SPEECH RULING, AND WHAT MEASURING ITS PREDICATE DID TO THE ROUTING

**The ruling, recorded so the next sweep of this class does not re-derive it** (chief,
2026-08-16):

> **Reported speech is not an assertion.** *"On 2026-08-07 we claimed a best-on-board tie"* is
> a true statement about what was claimed, and under D238/D255 it does not assert the tie. As a
> matter of **truth** it needs no correction.
>
> **But V10's criterion is "the same caveats", not "the same truth values",** and that clause
> decides it:
> - **On a TRAVELLING surface, reported speech MUST carry the correction.** A reader outside
>   the lab meeting *"we claimed a best-on-board tie"* with no withdrawal beside it takes the
>   tie as fact whatever the sentence's grammatical mood. **This is a caveats failure, not a
>   truth failure, and is recorded as such.**
> - **On a lab record, reported speech stands without the correction.** The record's job is to
>   say what was said; forcing a correction into every historical mention would make the record
>   unable to describe its own history — unsatisfiable by construction.

### 7.1 I measured the predicate instead of inheriting it, and three of four routings change

The ruling turns entirely on *does this surface travel*. That was **derived, not assumed**, by
the same two derivations `self_audit._travelling_names` uses — the member names of every
shipping archive plus the contents of every submission-package directory — reimplemented
rather than imported. **One archive, `dist/certonomous-demo.zip`, 103 members; 111 travelling
basenames**, controlled both ways (`DESCRIPTION_DOCUMENT.md` **travels: True**; `LESSONS.md`
**travels: False**).

| surface | in the travelling set? |
|---|---|
| `CLOSURE_CHALLENGE_STATUS.md` | **NO — lab record** |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | **NO — lab record** |
| `latex/closure_challenge_report.tex` (and its `.pdf`) | **NO — lab record** |
| *control:* `DESCRIPTION_DOCUMENT.md` | yes |
| *control:* `closure.html` | yes |
| *control:* `LESSONS.md` | no |

~~**So under the ruling exactly as written, all four sites are lab records and reported speech
stands at every one of them. No correction is required anywhere.**~~ That is the opposite of the
routing the ruling anticipated for three of the four, and it is reported rather than smoothed.

> **[SUPERSEDED 2026-08-16 by the chief ruling in §8, and struck rather than deleted because
> the measurement that produced it is unchanged and is what forced the ruling.** The
> *measurement* stands: none of the four is in `_travelling_names()`. What changed is the
> *definition*: **travelling now means packed OR staged-to-send**, so three of the four are
> travelling after all and two need corrections. Leaving this conclusion live beside §8 would
> be the exact cross-site disagreement this document was written to find.]**

### 7.2 AND THE PREDICATE IS WRONG FOR TWO OF THEM — which is the real finding here

`_travelling_names()` is a **snapshot of what is currently packed**. It therefore cannot see a
document whose entire purpose is to *become* the thing that is sent, and the lab's own records
say both of these in its own words:

- **`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` is the send-package.**
  `closure_challenge_round5_qcr.json:213` calls it *"Katie's send-package"* and records that
  *"Items 6-7 (author names, Katie's proofread and approval) remain the only things between the
  package and the steward."* The file's own first lines read *"draft package … This document
  exists to be proofread."* **A draft is pre-travelling, and the binary has no third state.**
- **`latex/closure_challenge_report.pdf` is called SHIPPED by the docket** (D243, in those
  words), while the predicate classifies it as a lab record because it is packed in neither
  route.

**Directionally this is the worst way for the predicate to be wrong:** the two surfaces whose
content is *destined for an outside reader* are the two it marks safest, so a rule that keys
correction-required off this predicate exempts exactly the sites that most need the caveat.

### 7.3 Routing — surface, travel status, rung, and who may act

| # | site | travels? | rung whose criterion covers it | who may act |
|---|---|---|---|---|
| 1 | `CLOSURE_CHALLENGE_STATUS.md:617-621` | **no**, measured | **none** — not among V10's five | **a non-author of that file.** Under the ruling: reported speech **stands**. Filed for the record, no repair owed |
| 2 | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1239` | **no** by predicate, **but it is the send-package** | **none** — not among V10's five | **a non-author of that file, plus the chief** on whether a draft counts as travelling. `:1239` carries its repair parenthetical on the *next line*, which is D294's shape and fails half (b) whichever way the travel question is ruled |
| 3 | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1273` | as above | none | as above |
| 4 | `latex/closure_challenge_report.tex:860-862` | **no** by predicate; its `.pdf` is called **shipped** in the docket | another rung's `.tex`/PDF arm, **not V10's** | **the `latex/` owner only.** `latex/` is never-touch here and the fix is a **rebuild, not an edit** |

**And where R-CONVERGE kept this pass out, it was right.** `docs/PRODUCT_LIST.md` and the
submission package sit inside **V10's** declared criterion, and **V10 closed PASS at
`700d2f08`** — so any live site there is a **reopening question for a non-author grader**, not
a repair available to this pass. Named, not decided.

### 7.4 One rule to add beside the four delimiter classes (D309's standing rule)

**SENTENCE SCOPE IS NOT CLAUSE SCOPE.** A detector that bounds scope at the sentence still
attaches a negator to the wrong proposition inside it: *"what was lost was a tie for second,
**not** for best"* is an AGREEMENT with *"the tie was for second"*, and this instrument scored
it a denial. **That is rule 3's failure one level down**, it was found by this sweep failing
against itself, and in this class the error runs in the direction that **manufactures** a
disagreement. It belongs with the four delimiter classes as the fifth thing a wrap-safe
recogniser must handle, and no instrument in this lab reaches it today.

---

## 8. THE RULING AS ISSUED, AND THE FINAL ROUTING

> **[CHIEF RULING 2026-08-16, on the question §7.2 routed.] A document whose only remaining
> gate is the owner's proofread IS TRAVELLING for the purpose of the caveats clause.
> TRAVELLING = PACKED **or** STAGED-TO-SEND.**
>
> **Ground 1 — the clause protects a reader outside this lab.** A send-package one approval
> away from leaving will reach that reader carrying whatever it says now, so **the moment of
> correction must precede the gate, not follow it.** A rule attaching the caveat only after
> packing corrects the document after the only person who could have caught it has approved it.
>
> **Ground 2 — `_travelling_names()` measures the present, not the intent**, and using it as
> the *definition* inverts the rule's purpose. It exempts precisely the documents most likely
> to be read externally. **A predicate that marks the send-package safest is not a definition
> of travelling; it is a measurement of packing.**
>
> **Ground 3 — the asymmetry decides it.** Erring toward *travelling* costs a redundant caveat
> on a lab record. Erring the other way **ships an uncorrected claim to an outside reader.**
> Where a binary has no third state, the error must fall on the recoverable side.
>
> **NOT RULED:** `_travelling_names()` is **not** widened by fiat. The predicate is an
> instrument, and changing it changes every verdict that has ever cited it. The gap is filed as
> a finding and the instrument change is routed to the fleet **as a proposal**.

### 8.1 Final routing — two repairs, neither of them this pass's to make

| site | status under the ruling | who may act |
|---|---|---|
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1239` | **TRAVELLING — correction required.** It also fails **either way**: the repair parenthetical sits on the *next line*, which is D294 half (b) regardless of travel status | **a non-author of these sites** |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md:1273` | **TRAVELLING — correction required** | **a non-author of these sites** |
| `latex/closure_challenge_report.tex:860-862` | **TRAVELLING — correction required**, and the fix is a **REBUILD, not an edit**; joins the `dist/` decision already before Katie | **the `latex/` owner alone** |
| `CLOSURE_CHALLENGE_STATUS.md:617-621` | **not travelling under either reading — reported speech STANDS**, no repair owed | filed for the record only |

**This pass made none of these repairs and graded no rung.**

### 8.2 The instrument gap, measured, and routed as a PROPOSAL rather than a change

**The gap:** `_travelling_names()` derives from shipping-archive members plus
submission-package directories, so it classifies **by what is currently packed** and has no
state for *staged-to-send*. **It misclassifies exactly two surfaces**, both named by the lab's
own records: `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (*"Katie's send-package"*,
`closure_challenge_round5_qcr.json:213`) and `latex/closure_challenge_report.pdf` (called
**SHIPPED** at D243).

**The blast radius, measured rather than asserted, because that is why this is a proposal:**

- **Three checks consume it**, resolved from the call sites by walking the AST rather than by
  reading: `check_rank_claim_surfaces`, `check_rank_claim_values`, `check_board_placement_words`
  (`scripts/self_audit.py:1209`, `:2162`, `:3964`). Widening the predicate moves the
  **FAIL/WARN severity split** in all three.
- **34 tracked files cite the travelling/lab-record distinction in prose**, 24 of them campaign
  grade and ladder records — i.e. evidence already relied on by closed rungs.
- **Two test files install doubles for it** (`sdk/tests/test_rank_claim_surfaces.py`,
  `test_rank_claim_values.py`), so a change has a ready harness.

**One distinction the proposal must carry, and it narrows the risk:** **V14's criterion names
`dist/` for its SEARCH FRAME, not for severity** — *"across tracked files, built artifacts, and
shipping archives including `dist/`"* (`LADDER_V_TRIPLE_VERIFICATION.md:409-416`). Widening
`_travelling_names()` changes **what severity a fault is reported at**, not **what gets
searched**, so V14's frame is untouched by it. **That is stated as a bound on the blast radius
and is not a ruling on V14**, which is not this pass's.

### 8.3 The fifth delimiter, recorded beside D309's standing rule

**SENTENCE SCOPE IS NOT CLAUSE SCOPE.** *"what was lost was a tie for second, **not** for
best"* is an **agreement** with *"the tie was for second"*, and this sweep's instrument scored
it a **denial**, because the negator attaches to a neighbouring clause **inside the same
sentence**. It is **rule 3's failure one level down**; it was found by the sweep failing
against itself; and **for an agreement checker it runs in the dangerous direction — it
manufactures a disagreement rather than hiding one.**

**No instrument in this lab reaches it today.** **The control it needs is a sentence carrying
two clauses of opposite polarity** — planted, read back, and required to classify each clause
separately; a single-polarity control cannot distinguish a clause-scoped detector from a
sentence-scoped one and would pass either.

---

*Swept 2026-08-16 at `8c01202f` by an agent that wrote none of the four surfaces named in §5.
Every figure re-derived by parsing an assignment node, never by importing a module and never by
quoting a document. Controls planted by line index into scratchpad copies and read back by
slicing at that index; RECOGNITION established by `scripts/control_kind.py`; both wrap false
zeros and rule 3's false contradiction reproduced before they were repaired. `__pycache__`
purged before measuring. No listing that was read was piped. Nothing repaired, no rung graded,
no guard tuned, no solver run, no scoring call made; the ledger stands at 6.*
