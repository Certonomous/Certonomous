# Ladder V — V10, fifth non-author grade, 2026-08-16

**Frame pinned in argv: `e71faf8b`** (the repair under grade). HEAD advanced to `04b9cc37`
during the write-up; `git merge-base --is-ancestor e71faf8b 04b9cc37` returned true and
`git diff --name-only e71faf8b 04b9cc37` over every criterion surface plus
`sdk/scripts/probability_of_rank.py` and `closure_challenge_round5_qcr.json` returned
**zero files**, so the grade held at both trees. The agreement check was additionally
re-run at `04b9cc37` and returned the same result.

**Verdict: `PASS`.**

Written by an agent that authored no part of V10 — no grade, no repair, no reopen, no
closure record (independence from the untracked dispatch record, not from git — D130).

---

## 1. The criterion, quoted from where it was found

`campaign/LADDER_V_TRIPLE_VERIFICATION.md:385-389` at `e71faf8b` (older records cite
`:359-362`; the drift the brief predicted to `:386-389` measured to `:385-389`):

> - **V10. Cross-surface number sweep**: closure.html, the Active Research board, the wall,
>   PRODUCT_LIST, and the submission package must all carry round-5 numbers with the same
>   caveats — one inconsistent surface fails the rung (the board was still showing round 3
>   at last report; that class of drift is what this rung exists to catch).

---

## 2. Arithmetic re-derived, never quoted

`ast.literal_eval` over the **parsed `LIVE_BOARD` assignment node** in
`sdk/scripts/probability_of_rank.py` — parsed, never imported — joined to
`official_test_harness_result.round5_per_case_full` and `.round4_per_case` in
`demo-output/website/closure_challenge_round5_qcr.json`. Tie membership derived by
**equality test**, never by reading.

**A JOIN FAULT WAS CAUGHT BY ASSERTION BEFORE IT WAS BELIEVED.** The first derivation
treated `LIVE_BOARD["entrants"]` as per-case *dicts*; they are positional *lists*, and the
join silently produced a one-element field, ranks `1,1,1,1,1,1,1,1` and a
**best-on-board of 8 of 8**. The corrected pass parses the `CASES` assignment node as well
and asserts `list(round5_per_case_full) == CASES` and `len(vector) == len(CASES)` for every
entrant before any figure is formed.

Per-case, live six-entry board plus our entry = seven positions:

| case | ours (round 5) | rank | board leader |
|---|---|---|---|
| `alpha_15_13929_4048` | 0.050105 | **2 of 7** | Tian, Buchanan, Hickel & Dwight 0.0432 |
| `alpha_15_13929_2024` | 0.101112 | **2 of 7** | Tian, Buchanan, Hickel & Dwight 0.0998 |
| `alpha_05_4071_4048` | 0.046108 | **1 of 7** | ours |
| `alpha_05_4071_2024` | 0.071863 | **1 of 7** | ours |
| `AR_1_Ret_360` | 0.045470 | **3 of 7** | Yang 0.0291 |
| `AR_3_Ret_360` | 0.039982 | **4 of 7** | Yang 0.0311 |
| `AR_14_Ret_180` | 0.035339 | **4 of 7** | Yang 0.0250 |
| `NASA_2DWMH` | 0.063198 | **7 of 7** | Tian, Buchanan, Hickel & Dwight 0.0294 |

Ranks **2,2,1,1,3,4,4,7**. Best-on-board **2 of 8**, and **0 of 8 earned by our model** —
the two survivors were confirmed against `rans_identity_floor_per_case` rather than
inferred: `0.046108` rounds to the floor's `0.0461` and `0.071863` to `0.0719`, and both
cases appear in `unchanged_cases_sha256`, so the board minimum on each is the organisers'
own supplied field.

`AR_14_Ret_180`, the case the rung turned on:

- live best is **Yang at 0.0250**;
- round 4's **0.0325 stood 2 of 7, tied with Reissmann, Fang & Sandberg** — tie membership
  returned by equality test, not read;
- round 5's **0.035339 stands 4 of 7**, tied with nobody;
- on the four-entry `deb91557` clone (rebuilt by re-applying the source's own exclusion set,
  `Yang` and `Tian, Buchanan, Hickel & Dwight` removed, **Yang absent confirmed**) round 4's
  `0.0325` was **1 of 5 and tied with Reissmann for best**. **The best-on-board reading was
  true only there.**

Overall `0.056647191704213645`, **rank 1 of 7**. Margin over Yang **0.0013653** on the
mean-of-eight basis and **0.0013528** against the published rounded `0.0580` — both
admissible, both reproduced.

Two package figures re-derived incidentally and both correct: `:386`'s per-case list
`0.0501 / 0.1011 / 0.0461 / 0.0719 / 0.0455 / 0.0400 / 0.0353 / 0.0632` matched the derived
values to 4 dp on all eight, and `:532`'s sub-precision ties `0.00003` and `0.00008`
reproduced as `AR_1` 0.0000296 and `AR_3` 0.0000820 against Wu & Zhang.

---

## 3. The agreement check, re-run independently on both blobs

Reimplemented rather than re-executed: the check below shares no code with the repair's.
It extracts every live occurrence of the characterisation family, bounds each one's scope
**on sentence punctuation and paragraph breaks and never on a bare `\n`**, classifies
ASSERT or DENY/SCOPED, and fails if the document does both.

| blob | raw | live | struck | ASSERTED | DENIED/SCOPED | result |
|---|---|---|---|---|---|---|
| `deb57c99` (pre-repair) | 5 | 5 | 0 | **`:192`** | `:118`, `:119`, `:173` | **CONTRADICTION** |
| `e71faf8b` (landed) | 7 | 5 | 2 | **none** | `:118`, `:119`, `:173`, `:194` | **AGREES** |
| `04b9cc37` (HEAD after) | 7 | 5 | 2 | **none** | `:118`, `:119`, `:173`, `:194` | **AGREES** |

The pre-repair CONTRADICTION reproduced independently and named `:192`. This check scored
pre-repair `:173` DENY rather than ASSERT, because its parenthetical already carried
*"the same correction"*; that makes this instrument **weaker** than the repair's at `:173`
and it still returned CONTRADICTION. Both instruments agree the pre-repair document
asserted P and ¬P, and both name `:192`.

All seven raw occurrences at `e71faf8b` reconciled hit by hit, **0 unexplained**:
`:97` LIVE, `:118` LIVE, `:119` LIVE, `:173` STRUCK, `:173` LIVE, `:192` STRUCK, `:194` LIVE.
The repair reported *"3 struck occurrences"* against this instrument's **2**; that is a
population difference between two recognisers (D49) over **suppressed** items, and the
verdict turns on live unnegated assertions, which measured **0** under both.

`:97` was excluded as a **heading**, on the standing ruling in §5 below and not to reach a
result — with `:97` counted as a proposition the landed blob would read CONTRADICTION, and
that is stated here rather than buried.

**A DEFECT IN THIS GRADER'S OWN HEADING DETECTOR WAS CAUGHT AND FIXED.** `^\s*#{1,6}\s`
under `re.MULTILINE` lets `\s*` consume the **preceding newline**, so a heading preceded by
a blank line was reported one line early and `:97` was never excluded. Bounded to
`^[ \t]*#{1,6}[ \t]` and re-run. Same family as the wrap defect: a whitespace class that
crosses a line boundary it was never meant to cross.

---

## 4. The two repaired sites, each tested on BOTH halves of D294

D294: *a caveat-adjacency test grades whether a claim **travels with** its board and is
silent on whether it is **true of** it.* Both halves must hold, and a table cell, list item,
heading and `<span>` are each their own block.

**`:173`** — block computed as the **list item** at lines `170-173`.
Text: *"0.0325 → 0.0353, ~~the best-on-board tie~~ **the tie for second** gone"*.

**`:192`** — block computed as the **paragraph** at lines `191-198`.
Text: *"its 0.00003 ~~best-on-board tie~~ **tie for second** is lost."*

Half (a), identifiers found **in-block** at both sites (measured, on the
emphasis-blanked view — `**six**-entry` defeats a `[-\s]` joiner otherwise):
four-entry `deb91557` clone **YES**; six-entry board **YES**; retrieval date
`2026-08-11T23:33Z` **YES**; re-verification date `2026-08-14T21:01Z` **YES**; live leader
`Yang's 0.0250` **YES**; round-4 placement `2 of 7` **YES**; round-5 placement `4 of 7`
**YES**. Seven of seven, both blocks.

Half (b), **true of that board**: the replacement reads *"tie for second"*, and round 4's
`0.0325` was re-derived as **2 of 7 tied with Reissmann** and round 5's `0.035339` as
**4 of 7**. The `0.00003` at `:192` was traced to its source rather than accepted —
`ACTIVE_RESEARCH.md:677-678` and `CLOSURE_CHALLENGE_STATUS.md:454` both record our
unrounded round-4 value as `0.0324698` against Reissmann's published `0.0325`, a difference
of `0.0000302`. **Both halves hold at both sites.**

The parenthetical's *"the tie was against the four-entry `deb91557` clone … and the
best-on-board reading was true only there"* was checked rather than read past: on the clone
the round-4 field's minimum **was** `0.0325` and **was** held jointly by our entry and
Reissmann, so a tie for best existed there and nowhere else. True as written.

`closure.html:302` does not carry the exact `<s>a best-on-board tie</s> <b>a tie for
second</b>` string the repair's message cites; the pattern is real and in that file at
`:192` and `:403`. A citation slip in a commit message, not a defect in the repair.

---

## 5. The three standing items, ruled explicitly

**5.1 `docs/PRODUCT_LIST.md:1810-1812`, ruled outside the claim class (D246). AGREED**, all
five grounds re-tested by execution and none inherited: `0.046108` and `0.071863` re-derived
correct and current; both still beat all **six** live entrants, with `0.0569` still the live
minimum on `alpha_05_4071_4048` and `0.0760` superseded by `0.0748` on `alpha_05_4071_2024`;
the `### 2026-08-10 (night)` heading measured at `:1778`, above the line and before the
board move; **`0.0748` occurred ZERO times in all 3,996 lines**, so the same-page
contradiction that killed C1/C2 was absent; and `:1811` prints a comparison and no rank.

**5.2 `DESCRIPTION_DOCUMENT.md:97` deliberately left. AGREED.** The line is the markdown
heading `### 2. Best-on-board count, stated with its own qualification` — a noun phrase
naming a section, with no predicate. `use_mention_discriminator.classify` returned
**`CANNOT_TELL`** (*"no evidence either way — silence is not an assertion"*) and **was not
promoted**; hand-adjudicated on the written ground that **neither half of D294 has a
truth-bearer to bind to**: there is no proposition to travel with a board and none to be
true or false of one. The strongest objection — that a reader infers a nonzero count — is
answered by the text seven lines below it, which states the count belonging to our model is
**ZERO of 8**.

**5.3 The surviving live matches on `closure.html`. AGREED, and this sweep found seven** on
the same family (the earlier four and ten were different recognisers over different
populations — D49). Every one was opened rather than cleared by pattern: `:124` (*"The
best-on-board count fell with the board"*, with `<s>4 of 8</s> → 2 of 8` against the
six-entry board in the same block), `:192` (struck, then *"struck 2026-08-16: there was no
best-on-board tie to lose"* with both dates and `2nd of 7` inside the same `<td>`), `:302`,
`:319`, `:373`, `:381` and `:403` — each carrying a refuting or dating operator **and** an
in-block board identifier. **None asserts a live board standing.** `ACTIVE_RESEARCH.md`
returned five, all clean on the same test, including `:680`'s *"Best-on-board 5 of 8,
unchanged"*, which sits under the `**Round 4 (2026-07-31) *(superseded …)*` header and is
followed **on its own line** by the four-entry attribution and the six-entry correction to
`2 of 8`.

---

## 6. Controls: six, planted by line index, read back by slicing at that index

Every control was planted into a **scratchpad copy of real `e71faf8b` bytes** (no tracked
path written — D210), inserted **by line index** at index 300, and **read back by slicing at
that index and asserting byte-equality with the planted lines** before any count was
believed; the bytes before and after the plant were asserted identical to the original as
well.

| control | form | gain WITH the rule | gain WITHOUT |
|---|---|---|---|
| A plain | `The best-on-board tie was lost on that duct.` | **+1** | +1 |
| B wrap | `best-on-board` / newline / `tie` | **+1** | +1 |
| C blockquote-wrap | `> … best-on-board` / `> tie was lost` | **+1** | **0 — reproduces the false zero** |
| D hyphen-split | `best-on-` / newline / `board tie` | **+1** | +1 |
| E struck negative | `~~The best-on-board tie was lost…~~` | **0** | 0 |
| F emphasis-split | `beats **all four** published entries` | **+1** | **0 — reproduces a second false zero** |
| NEG | `The best on bench tea was lost on that duct.` | **0 (correctly rejected)** | 0 |

`scripts/control_kind.py`, fed the **measured** fired/not-fired booleans and never a typed
label, returned **`CONTROL KIND: RECOGNITION`** — *"4 mutually independent forms in the
vocabulary of 'best-on-board tie / lost / round-4 duct', all found; 1 negative form correctly
rejected"*.

**CONTROL F IS A FINDING ABOUT THIS GRADER'S OWN INSTRUMENT, and it is the reason a real
site was seen at all.** The first board-size sweep returned **0 live hits** on the
submission package. That zero was false: `:92` reads `beats **all four** published entries`,
and `**` is not whitespace and not a hyphen, so a `[-\s]{1,20}` joiner — the rule as it
stood this morning — cannot cross it. Fixed by an **offset-preserving emphasis blank**
(`**`, `*`, `_`, backticks, `<b>`/`<strong>`/`<em>` overwritten with spaces in place, same
length, newlines untouched), applied **after** strike detection because `~~` is a strike
marker. The sweep then returned **3**. **This is the same defect as the blockquote wrap,
in a third delimiter, found by a grader who had read the warning about it forty minutes
earlier. Knowing the trap did not protect this sweep; only the readback did.**

Two listings that were read were re-run **unpiped**; no count in this record came through a
pipe, and no exit code of a piped command was gated on or reported.

---

## 7. The document checked over the SET, and the surfaces over the set of surfaces

Run over the whole criterion set rather than site by site, on the characterisation family,
whole files and never enumerated line ranges:

| surface | raw | live | struck | unexplained | live defect |
|---|---|---|---|---|---|
| `closure.html` | 11 | 7 | 4 | 0 | none |
| `ACTIVE_RESEARCH.md` | 8 | 5 | 3 | 0 | none |
| `benchmarks.html` | 0 | 0 | 0 | 0 | none |
| `wall/wall.html`, `wall/wall.json`, `benchmarks.json` | 0 | 0 | 0 | 0 | none |
| `docs/PRODUCT_LIST.md` | 12 | 11 | 1 | 0 | none |
| `DESCRIPTION_DOCUMENT.md` | 7 | 5 | 2 | 0 | none |
| package `README.md`, `MANIFEST.json`, 8 CSVs | 0 | 0 | 0 | 0 | none |

All 11 package members were enumerated by `git ls-tree -r --name-only` and swept, the eight
prediction CSVs included rather than argued about. A **second, independent pattern family**
over `AR_14`, `0.0325`, `0.0353`, `0.00003`, tie-and-lead vocabulary returned **20 live
hits in 11 distinct sentences** on the package, every one opened: all either carry the
six-entry board with both dates and the correct placements, or are struck-and-replaced with
full caveats, or are the verbatim frozen rule-freeze quotation at `:148`, or are plain
correct round-5 numbers. **No live unnegated assertion of the characterisation survives
anywhere on the criterion set.**

Four `PRODUCT_LIST` sites classified `CANNOT_TELL` or `ASSERT` by the discriminator and
**none was promoted**; each was hand-adjudicated with written grounds: `:126` reports a
defect in another document and corrects it in the same sentence (*"states a … count of 4 of
8 **that is 2 of 8 on the live board**"*); `:2413` names a **category** of sentence that was
traced and states no count; `:2509`'s claim text sits inside quotation marks and its own
clause is about a **generator** being executed rather than about a board standing; `:2645`
sits under the dated heading `### 2026-08-11 — V8 still FAILS` and records a past
verification act.

**Since the third grade's tree `678cb7e8`, `git diff --name-only` over every criterion
surface returned exactly one file: `DESCRIPTION_DOCUMENT.md`.** The other surfaces are
byte-identical to the trees at which two prior grades cleared them, and were re-swept here
independently rather than inherited, with the same result.

---

## 8. Filed, not appended — out of scope, and repaired by nobody here

**F1 — `DESCRIPTION_DOCUMENT.md:92`, `beats **all four** published entries`, live and
undated in the package's disclosure section. RULED NOT A V10 BLOCKER, and the grounds are
given because the ruling is close.** Both halves of D294 hold: half (a), the sentence names
its board **by entrant count**, which the fourth grade ruled in this same rung to be *"the
lab's own admissible identifier form"*; half (b), it is **true by execution of both
boards** — the supplied baseline `0.0461` beats the clone's `0.0606 / 0.0569 / 0.0613 /
0.0591` and the live six `0.0645 / 0.0606 / 0.0569 / 0.0744 / 0.0613 / 0.0591`, and `0.0719`
beats `0.0760 / 0.0848 / 0.0769 / 0.0882` and the live `0.0748 / 0.0760 / 0.0848 / 0.0960 /
0.0769 / 0.0882`. **Every V10 blocker in this rung's history was FALSE of the live board;
this one is true of both.** There is also **no cross-surface inconsistency to fail on**: every
surface carrying this claim — `PRODUCT_LIST.md:1787`, `:1811`, `:2511` and this line —
carries it identically as *"four"*, and no criterion surface states it with *"six"*.

**What is genuinely wrong with it is D238's class**: a board named by count with **no
retrieval date**, which the V10 closure explicitly parked (*"if D238 rules an incomplete
board identifier on a kept dated figure to be a V10 inconsistency, the rung reopens on
exactly one line, `PRODUCT_LIST.md:1811`"*) and on which the reopen then landed **"and not
on that line."** Failing V10 here would reverse D246 and reopen `:1811` by the same stroke —
a chief's boundary ruling, not a grader's. **Filed for that ruling.** It differs from
`:1811` in one respect worth recording: it sits in an **undated, live, forward-facing
disclosure section** rather than a dated journal, and its own page states a six-entry board
eight lines below at `:99-104` and again at `:449`, so D246's third and fourth grounds do
**not** transfer to it. That is the strongest case against this ruling and it is stated here
rather than omitted.

**F2 — `CLOSURE_CHALLENGE_STATUS.md:454` and `:781`, out of scope by surface.** The
criterion names five surfaces and this document is none of them; the reopen repaired its
`:1269` voluntarily. `:781` classifies **MENTION** (positionally set off — blockquote) and
`:454` **CANNOT_TELL**, neither promoted. Recorded for the file's owner, not appended to
this rung.

---

## 9. Verdict

**`PASS`.**

The criterion's test is *one inconsistent surface fails the rung*. At `e71faf8b` and again
at `04b9cc37`, no criterion surface carries a live unnegated assertion of the
`AR_14_Ret_180` best-on-board characterisation; the submission package's two remaining
sites were struck to *"tie for second"* and both hold on **both** halves of D294 with seven
in-block identifiers each; the document was checked over the **SET** and returned
**AGREES** where the pre-repair blob returned **CONTRADICTION** under the same instrument;
and the package now states what `closure.html` states — *there was no best-on-board tie to
lose; what was lost was a tie for second*.

Mechanically, every claim the repair made was re-measured and held: file **571 → 573**
lines; `~~` markers **40 → 44**, even on both blobs, final depth **0**, zero `<s>` and zero
`<del>`; `README.md` and `MANIFEST.json` at **0** family occurrences and all eight
prediction CSVs at **0**.

**Nothing was repaired by this grader.** F1 and F2 were filed and left in place.
