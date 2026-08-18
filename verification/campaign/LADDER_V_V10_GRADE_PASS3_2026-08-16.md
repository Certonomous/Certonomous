# V10 — third non-author grade of 2026-08-16, against the repair at `fac54ab4`

**Verdict: `FAIL`.** One in-scope surface carried a live, unstruck, board-less
stale characterisation of the same class that reopened this rung at `f7170481`.

Graded at HEAD `678cb7e8` by a non-author of `fac54ab4`, of `f4f05b0f` and of
`f7170481` (independence from the untracked dispatch record, not from git — D130).
Every one of the five surfaces was read at the **landed blob** via
`git show <sha>:<path>`, never at the worktree. `git diff fac54ab4 678cb7e8` over all
eight non-CSV members returned **zero changed files**, so the grade held at both
trees. HEAD then advanced to `2daebd70` while this grade was being written, and
`git diff --name-only 678cb7e8 2daebd70` over all nineteen members plus
`probability_of_rank.py` and `closure_challenge_round5_qcr.json` returned **zero
files**, so the grade was re-verified to hold at the landing tree as well.

---

## 1. The criterion, quoted from where it was found

It had drifted to `:386-389` of `campaign/LADDER_V_TRIPLE_VERIFICATION.md` from
the `:359-362` older records cite. Quoted at HEAD:

> - **V10. Cross-surface number sweep**: closure.html, the Active Research board,
>   the wall, PRODUCT_LIST, and the submission package must all carry round-5
>   numbers with the same caveats — one inconsistent surface fails the rung (the
>   board was still showing round 3 at last report; that class of drift is what
>   this rung exists to catch).

Five surfaces, nineteen tracked members, one claim class (round-5 numbers **and
the caveats travelling with them** — board by entrant count *and* retrieval date,
the per-case placement, the best-on-board count, and the share belonging to our
own model), and **no tolerance**.

## 2. The arithmetic, re-derived rather than quoted

`LIVE_BOARD` was lifted from `sdk/scripts/probability_of_rank.py` by
`ast.literal_eval` over the parsed assignment node — **parsed, never imported** —
and joined to `official_test_harness_result.round5_per_case_full` in
`closure_challenge_round5_qcr.json`. Both read at HEAD.

| quantity | re-derived at `678cb7e8` |
|---|---|
| positions | 6 entrants + our row = **7** |
| per-case ranks, round 5 | **2, 2, 1, 1, 3, 4, 4, 7** of 7 |
| best-on-board, round 5 | **2 of 8** |
| earned by our own model | **0 of 8** |
| overall | 0.056647191704213645, **rank 1 of 7** |
| margin over Yang | **0.001365** (mean-of-eight basis, Yang 0.0580125) |
| margin over Yang | **0.001353** (against the published rounded 0.0580) |

**`AR_14_Ret_180`, the case the whole dispute turns on.** The live column, sorted:
Yang **0.0250** (the board minimum), Reissmann, Fang & Sandberg **0.0325**,
Wu & Zhang **0.0350**, Montoya 0.0487, Tian 0.0527, Liu 0.0548. Round 4's
**0.0325** therefore stood **2 of 7, tied with Reissmann for SECOND**, behind
Yang. Round 5's **0.035339** stood **4 of 7**. **There was never a best-on-board
tie to lose.** The best-on-board reading was true only of the superseded
four-entry board frozen at `deb91557`, on which Yang did not appear and on which
round 4's 0.0325 did stand **1 of 5, tied** — that board was re-derived here as
the control, from the same node, and it does place the claim at rank 1.

The two rank-1 cases were confirmed to be the RANS-identity rows rather than
argued to be: `rans_identity_floor_per_case` reads 0.0461 and 0.0719 against our
0.04610779 and 0.07186293, identical at the file's own write precision. **0 of 8
earned by the model** was therefore a measurement, not an inference.

Incidental figures carried by the surfaces were re-derived too: head-to-head we
took 4 of 8 from Yang and 4 of 8 from Reissmann, 7 of 8 from each of Liu and
Montoya; Tian held the live board minimum on **3** cases, we on **2**.

## 3. Instrument and controls

A whole-file sweep of **all nineteen tracked members** — none by line range.
Strike spans were blanked **in place**, preserving every byte offset, over three
mechanisms (`<s>`, `<del>`, markdown `~~…~~`), so the remainder kept its true
line numbers. **Every pattern was built with `\s+` and never a literal space.**

**And `\s+` was not enough, which this grade had to be told and then measured.**
A blockquote prefix breaks it: `>` is not whitespace, so a claim wrapping as
`rank 1\n> of the …` is invisible to a `\s+` pattern exactly as it is to a
literal-space one. Line-continuation prefixes — leading `>`, repeated `> >`, and
list markers — were therefore neutralised **for detection only**, by overwriting
them with spaces of **exactly the same length**, so every byte offset, line
number and strike span was preserved and the text quoted was never altered.

**The movement was the repair's own control.** Across the nineteen members the
live count moved **255 → 256**, and the single revealed site was
`DESCRIPTION_DOCUMENT.md:298`, matching `'rank 1\n> of the'` across a blockquote
prefix. It was opened and ruled **clean** — a correction record reading
*"**Reissmann, Fang & Sandberg are rank 2**, not rank 1. They were rank 1 of the
four-entry board frozen at `deb91557`"*, board identified in its own block and
true of the live board.

Final at HEAD: **330 raw / 256 live / 74 suppressed, 0 unexplained** — every
suppressed hit was located inside a genuine strike span, hit by hit. These
figures are this instrument's own population and are **not comparable** to any
other agent's (D49); only the strike parity and the unexplained count are.

**Control 1 — live positive, against the pre-repair tree.** The instrument,
unchanged, was run at `f4f05b0f`. It returned all six graded sites at their
graded lines: `:191`, `:291`, `:305`, `:350`/`:351`/`:353`, `:377`, `:507`. One
of those matches, `'the tie is\nlost'` at `:350`, was **wrapped across a real
line break in production data** — the strongest available proof that the `\s+`
discipline held.

**Control 2 — planted positive, by LINE INDEX and never by anchor string**, into
a scratchpad copy of `wall/wall.json` (no tracked path was written; D210). Two
mutually independent forms, neither a substring of the other:
`the tie was lost on that duct` (the inflected verb — the exact is/was case that
produced a false zero for a peer) and a wrapped `best-on-board` form. **Both were
read back from disk before any zero was believed**, and both fired.
`scripts/control_kind.py` classified the ledger **RECOGNITION**, derived from the
evidence rather than from a typed label, with the verdict
`ZERO_IS_A_MEASUREMENT`. A negative form, `the tea is lost`, was correctly
rejected.

**Control 3 — struck negative.** A planted `<s>a best-on-board tie for best was
lost</s>` produced three suppressed hits and **zero live**, each located inside a
genuine strike span.

**Control 4 — wrap-proof, planted.** Into a scratchpad copy of `benchmarks.html`
by line index, the phrase deliberately broken mid-way across a newline; read back
from disk; the pattern matched `'best-on-board\ntie'` across the break.

**Control 5 — blockquote-wrap, planted, and it reproduced the false zero before
it fixed it.** Into a scratchpad copy of `DESCRIPTION_DOCUMENT.md` by line index,
`best-on-board` / `tie on the AR_14 duct` split across a `>` continuation; read
back from disk. **Without** the prefix repair the planted form was **NOT FOUND**
— the false zero, reproduced deliberately on a file known to hold it. **With** the
repair it fired as `'best-on-board\n  tie'`, live count 32 → 34. All four earlier
controls were re-run under the repaired instrument and held unchanged:
`control_kind.py` still classified the ledger **RECOGNITION** with
`ZERO_IS_A_MEASUREMENT`, and the struck negative still returned zero live.

**A supplementary recogniser** (`board-best`, `best on the board`, `topped/led
the board`, `held the best`, `tie for …`, `beats all`) was run over all nineteen
members as a second, independent pattern family, under the same prefix repair,
and it independently returned **the same single blocker** —
`DESCRIPTION_DOCUMENT.md:112`, again as the wrapped match `'best on\nboard'`.

**One defect in this grader's own reporting, found and corrected before it was
believed:** a first dump of the live hits was piped through `head -220` and
silently truncated the submission package's list at 8 of 31, hiding `:185`. The
dump was re-run unpiped to a file and the count reconciled against the sweep's
own total before any adjudication was written.

## 4. The six repaired sites, each tested rather than accepted

All six were verified present at HEAD and each was tested on **both** halves of
D294 — whether the claim **travels with** its board, and whether it is **true
of** it — with the block taken to be the table cell, list item or heading itself.

| pre-repair | at HEAD | travels | true-of | ruling |
|---|---|---|---|---|
| `:191` table row | `:191-198` | board by entrant count + both retrieval dates + seven-row count, **inside the `<td>`** | round 4's 0.0325 = 2 of 7 tied with Reissmann, behind Yang 0.0250 | **repaired** |
| `:290-291` freeze bullet | `:297-305` | identifier inside the same span, not the adjacent block | same | **repaired** |
| `:305` pre-registration bullet | `:316-321` | in-block clarifier | the pre-registration claim itself was true and was left undisturbed; only the implied subject was corrected | **repaired** |
| `:350-353` warn box (D294's own site) | `:366-388` | heading and premise struck and restated in-block | the already-correct six-entry caveat below was left byte-undisturbed, as claimed | **repaired** |
| `:377` Spalart bullet | `:400-403` | board and date in the same sentence | same | **repaired** |
| `:507` results-table tag | `:533` | identifier inside the `<span class="tag">` | "the tie for SECOND" beside the tag's own correct "the live best 0.0250 is Yang's" | **repaired** |

**Strike parity**, audited independently at both trees: `closure.html` moved
**27/27 → 33/33**, depth never outside [0,1], final 0 — six pairs added, one per
site, exactly the movement claimed. **HTML nesting re-parsed** at both trees: **0
errors, nothing unclosed at EOF**, on `f4f05b0f` and on HEAD alike.

## 5. The four surviving live matches — adjudicated, not accepted

Four live matches of the phrase survived on `closure.html`, and the sweep found
exactly four: `:192`, `:197`, `:319`, `:373`. Each was opened and read.

- `:192` — *"there was no best-on-board tie to lose"* — refutation.
- `:197` — *"the tie for best was true only of the superseded **four**-entry board frozen at `deb91557`"* — a dating operator naming the board the claim was true of.
- `:319` — *"what it called a best-on-board tie was … a tie for **second**"* — the phrase named as another text's wording.
- `:373` — *"there was never a best-on-board tie to lose"* — refutation.

Each carries an explicit refuting or dating operator, and each carries its board
identifier inside its own block. Under the D238 ruling, quoting a claim in order
to strike, grade or refute it is not making the claim. **All four were ruled
mentions.** Two further stem matches at `:302` and `:403` were read and ruled the
same way for the same reason.

## 6. The blocker

**`demo-output/website/closure_challenge_submission_round5/DESCRIPTION_DOCUMENT.md:112-113`,
the submission package.** Live, unstruck, no board identifier of any kind:

> `AR_14_Ret_180` was best on
> board in round 4 by 0.00003 and **is not any more** (see disclosure 4).

**It is not struck.** The `~~…~~` span that opens at `:110` was measured to close
at offset 6306, mid-line at `:112`, immediately before this sentence. Verified by
printing the raw and the offset-preserving blanked line side by side: the strike
covers `…not 4.~~` and stops there.

**It is false of the live board.** "Best on board in round 4" was true only of
the four-entry `deb91557` clone. Against the six-entry board retrieved
2026-08-11T23:33Z, round 4's 0.0325 stood **2 of 7**, tied with Reissmann for
second, behind Yang's 0.0250. The `0.00003` it quotes is the four-entry margin
over Reissmann; against the live board the gap to the actual board minimum was
0.0075 in the other direction.

**It does not travel with its board.** Its block carries no entrant count and no
retrieval date. `(see disclosure 4)` is a cross-reference to §4 at `:163-166`,
**fifty-three lines away** — not merely the adjacent block, which D294 already
rules insufficient.

**It was reached by a characterisation pattern, not a number pattern**, and the
match `'best on\nboard'` was **wrapped across a line break** — both of the
failure modes this rung's own history names, in one site.

`scripts/use_mention_discriminator.py`, given the sentence and the character span
of the claim, returned **`CANNOT_TELL`**. That was **not promoted to `ASSERT`**.
It was hand-adjudicated an assertion, on written grounds:

1. The claim span carries no enclosure — not quoted, not in a code span, not
   struck, not attributed. The one code span in the sentence covers only the case
   identifier, which is the subject and not the claim.
2. The predicate is the document's own present assessment, *"and **is not any
   more**"*, with a forward cross-reference. That is the syntax of a document
   speaking in its own voice.
3. It sits immediately after a closing `~~` and was deliberately excluded from
   it. Everything the author disclaimed lies inside the span; this sentence was
   kept live.
4. It carries no refutation or dating operator at all — unlike every one of the
   four surviving matches on `closure.html`, and unlike `:166` and `:185` of this
   same file.

**It is the class that reopened this rung.** `ACTIVE_RESEARCH.md:29` read
*"AR_14's nominal best-on-board tie was lost as pre-accepted in writing
(+0.0029)"* and was ruled inside the class at `f7170481`. This sentence says the
same thing in different words, on a different surface, and carries no stale
number either — which is why a number-sweep returned a true zero on it.

**It is not protected history.** The banner directly above it, at `:99-108`,
declares in its own words that *"The original text is kept below, **struck**,
because the change in the board is itself disclosable."* What that banner
protects is the struck text. This sentence is outside the strike the banner
points at.

**And its own page contradicts it twice over.** The same section, nine lines
above at `:104`, states *"the count that belongs to our model is now ZERO of
8 — our model is best on no single case."* And this same document repaired the
identical claim correctly in **two** other places — `:166` and `:184-187` — each
time with an in-block parenthetical naming the four-entry `deb91557` clone the
tie was against and giving the six-entry placement beside it. `:112-113` is the
one instance the repair did not reach: the *"the repair stopped one line short"*
shape that `docs/PRODUCT_LIST.md:106-107` names as D93's own.

Under the criterion's no-tolerance clause, one inconsistent surface fails the
rung.

## 7. Everything else, clean by execution

`closure.html`, `ACTIVE_RESEARCH.md`, `benchmarks.html`, `benchmarks.json`,
`wall/wall.html`, `wall/wall.json`, `sdk/scripts/build_benchmarks.py`,
`docs/PRODUCT_LIST.md`, `MANIFEST.json`, the package `README.md` and all eight
prediction CSVs carried no live in-scope inconsistency. Every live hit was opened
and adjudicated rather than cleared by pattern. Notable ones read and ruled:

- `benchmarks.html:128-130` — *"a nominal 0.00003-level tie for best … **against
  that same superseded four-entry board**"*, with the six-entry correction in the
  next sentence of the same parenthetical. Travels and true-of. Clean.
- `benchmarks.html:88` and `:504-509` of the package — *"four of eight cases
  won"* re-derived as a **head-to-head** count against Yang: 4 of 8, correct.
- `closure.html:520` *"OUR MODEL LEADS"* and `:557` *"five cases where we lead"* —
  both inside quotation marks, both naming a defect that was corrected. Mentions.
- `closure.html:467` — Tian *"best on the board on three cases, two of them taken
  from us"*: re-derived, Tian held the live minimum on exactly 3. True.
- `ACTIVE_RESEARCH.md:29-41` — the `f7170481` repair verified in place, with the
  full caveat set in-block.
- All eight CSV hits were substrings of prediction floats.

## 8. `docs/PRODUCT_LIST.md:1810-1812` — D246, ruled explicitly

**Agreed: outside V10's claim class, and not repaired here.** All five grounds
were re-tested by execution rather than inherited:

1. Its round-5 numbers `0.046108` and `0.071863` were re-derived from
   `round5_per_case_full` and were correct and current at HEAD.
2. Its substance survived the board move: both beat all **six** live entrants,
   and `0.0569` was still the live minimum on `alpha_05_4071_4048` (Wu & Zhang).
   Only `0.0760` was superseded, by Yang's `0.0748`.
3. It sat under an explicit `### 2026-08-10 (night)` heading at `:1778` in a
   dated journal, the night before the board moved at 2026-08-11T23:33Z.
4. The decisive test, re-run: **`0.0748` occurred ZERO times in all 3,996 lines**
   of the file, so the same-page contradiction that killed C1 and C2 was absent.
5. The page's own binding rule at `:97-98` reaches surfaces that print *"rank
   1"*; `:1811` printed a comparison and no rank.

What stayed wrong with it — a board named by entrant count with no retrieval date
— remained D238's class in a second file and remained the chief's one ruling to
make. **This `FAIL` does not rest on it**: the rung failed on
`DESCRIPTION_DOCUMENT.md:112-113` and would have failed there whichever way D238
is ruled.

## 9. Constraints observed

No submission was sent, uploaded, registered or posted; no organiser was
contacted. No solver was launched. No scoring call was made and the ledger stood
at **6**, untouched. `dist/`, `demo-output/website/latex/`, `motorbike-video/`
and `LAPTOP_SHOOT.md` were not opened or written. Nothing was repaired by this
grader on any surface it graded. No tracked path was written by any control;
every plant went to a scratchpad copy. `__pycache__` was purged before
measurement.
