# Ladder V — V10 re-grade at HEAD, by a non-author

**Verdict: `FAIL`.**

Frame: HEAD `9cdb1851`. Graded against the **landed blobs** (`git show HEAD:<path>`),
never the worktree, because V10 grades what travels. Independence is from the
untracked dispatch record and **not** from git: every commit in this repository
carries one Ubuntu identity, so no reader of this repository can re-derive it
(D130). I authored none of `c2cd83bf`, `f7170481`, `1fc1f639`, nor any V10 grade
or repair.

---

## 1. V10's scope, in my words

The criterion is at `campaign/LADDER_V_TRIPLE_VERIFICATION.md:386-389`. (My
dispatch cited `:359-362`; at HEAD those lines are V8 amendment prose. The
reference had drifted and the criterion was located by content instead.)

> **V10. Cross-surface number sweep**: closure.html, the Active Research board,
> the wall, PRODUCT_LIST, and the submission package must all carry round-5
> numbers with the same caveats — one inconsistent surface fails the rung (the
> board was still showing round 3 at last report; that class of drift is what
> this rung exists to catch).

In my words, three clauses and each does work:

1. **FIVE SURFACES, nineteen tracked members.** `closure.html`;
   `ACTIVE_RESEARCH.md`; the wall (`benchmarks.html`, `benchmarks.json`,
   `wall/wall.html`, `wall/wall.json`, `sdk/scripts/build_benchmarks.py`);
   `docs/PRODUCT_LIST.md`; the submission package
   (`DESCRIPTION_DOCUMENT.md`, `MANIFEST.json`, `README.md`, and eight
   prediction CSVs). All nineteen were swept whole, none by line range.
2. **ONE CLAIM CLASS: round-5 numbers AND THE CAVEATS TRAVELLING WITH THEM.**
   The caveats are not decoration and this rung is where they are enforced: the
   board named by **entrant count and retrieval date**, the per-case placement,
   the best-on-board count, and the share of it belonging to our own model. A
   surface that carries a correct number with the wrong caveat, or with none,
   is inconsistent with a surface that carries both.
3. **NO TOLERANCE.** One inconsistent surface fails the rung. There is no
   "mostly", no residual, and no exception; the R-CONVERGE outcome vocabulary
   here is a plain `PASS` or a plain `FAIL`.

---

## 2. The board, re-derived — never quoted

`LIVE_BOARD` read by `ast.literal_eval` over the parsed source of
`sdk/scripts/probability_of_rank.py` (**parsed, never imported**), joined to
`round5_per_case_full` in `closure_challenge_round5_qcr.json`.

| quantity | re-derived |
|---|---|
| positions | 6 entrants + our row = **7** |
| per-case ranks | **2, 2, 1, 1, 3, 4, 4, 7** of 7 |
| best-on-board | **2 of 8** |
| earned by our model | **0 of 8** |
| overall | 0.056647191704213645, **rank 1 of 7** |
| margin over Yang | **0.001365** (mean-of-eight basis) |

Two independent confirmations that this is the board and not a transcription:
`round5_overall_full` in the QCR record equals my computed mean of the eight
case values exactly, and the two best-on-board cases
(`alpha_05_4071_4048`, `alpha_05_4071_2024`) are precisely the two where our
score **equals the RANS identity floor** — which is why 0 of 8 belongs to our
model, derived rather than repeated.

**On the margin, a precision note that matters.** From `LIVE_BOARD`'s
`published_overall` (Yang `0.0580`, stored at 4 dp) the margin computes to
`0.001353`. On the mean-of-eight basis — Yang's eight case values mean to
`0.0580125`, the same basis our own overall uses — it is `0.001365`. Both are
correct on their stated basis and the corpus records both; a grader taking one
without the basis would file a false finding. `0.002878` is likewise **correct**
as our margin over Reissmann on the mean-of-eight basis (`0.059525 − 0.056647`),
which is why the three `closure.html` sites carrying it are not faults.

**AR_14, the case this turns on.** Round 4's `0.0325` **tied Reissmann's
`0.0325`** and stood **2 of 7**, behind **Yang's `0.0250`**. Round 5's
`0.035339` stands **4 of 7**. **There was never a best-on-board tie to lose.**

---

## 3. The instrument, and why its zeros are worth anything

`c2cd83bf` returned a true zero on a false page because its recogniser was eight
stale **literals** and fourteen **phrases**, and the clause that reopened the
rung carries no stale literal, no ordinal, and none of the fourteen. **A stale
characterisation carries no stale number.** So the recogniser here is built over
the claim's VOCABULARY, every pattern assembled by joining words on `\s+` and
never on a literal space, applied to whole files.

**Controls are RECOGNITION-grade, and `scripts/control_kind.py` decided that —
not me.** Six mutually independent forms of the reopening clause were planted by
**line index** into `wall/wall.json` and **read back before the run**:
original inflection; present tense (`is gone` for `was lost`); reordered
passive; **wrapped across a line break inside the phrase**; a paraphrase
(`our model leads the entire public leaderboard`); and a spelled ordinal
(`rank 1 of five`). Each was planted **alone** and its own gain measured, so
"this form fired" is a measurement and not an inference from a shared total.

```
planted forms fired : 6/6
negative forms held : True   (<s>…</s> and ~~…~~ both correctly rejected)
control_kind.py     : RECOGNITION
   6 mutually independent forms ... all found; 2 negative form(s) correctly rejected
baseline 7 -> all forms planted 17
```

**Live positive control against the pre-repair tree.** The same instrument,
unchanged, run on `f7170481^`, fires on the graded blocker at its graded line —
`ACTIVE_RESEARCH.md:29`, `tie was lost` — so its zeros on the repaired tree are
measurements and not silence.

**Use-versus-mention.** `scripts/use_mention_discriminator.py` grades whether a
sentence ASSERTS a claim or quotes it to correct it. **`CANNOT_TELL` is never
read as `ASSERT`**; every one was opened by hand and adjudicated, and this grade
says which.

### The raw-vs-blanked reconciliation (the over-blanking control)

Strike-stripping can hide a live claim as easily as it reveals one, so every
suppressed hit was reconciled against a genuine strike span, hit by hit:

| member | raw | live | suppressed | `<s>` | `~~` |
|---|---|---|---|---|---|
| closure.html | 40 | 27 | 13 | 27/27 | 0 |
| ACTIVE_RESEARCH.md | 37 | 23 | 14 | 0/0 | 52 (even) |
| benchmarks.html | 11 | 4 | 7 | 16/16 | 0 |
| benchmarks.json | 8 | 8 | 0 | 0/0 | 0 |
| wall.html | 0 | 0 | 0 | 0/0 | 0 |
| wall.json | 8 | 8 | 0 | 0/0 | 0 |
| build_benchmarks.py | 11 | 10 | 1 | 0/0 | 2 (even) |
| PRODUCT_LIST.md | 45 | 38 | 7 | 0/0 | 56 (even) |
| DESCRIPTION_DOCUMENT.md | 28 | 25 | 3 | 0/0 | 40 (even) |
| MANIFEST.json / README.md | 0 | 0 | 0 | — | — |
| **TOTAL** | **188** | **143** | **45** | | |

**Every one of the 45 suppressed hits sits inside a genuine strike span; 0
unexplained.** Strike parity is even in all eleven members and `<s>` balances
27/27 and 16/16. The blanking is not hiding a live claim.

---

## 4. THE BLOCKERS — `closure.html`, two live instances

A sweep of the tie characterisation across all five surfaces returns **six live
instances**. Four carry a six-entry board identifier within twelve lines. **Two
carry none, and both are on `closure.html`.**

### B1 — `closure.html:190-191`, the round-5 row of the scoring-call table

```html
<tr class="us"><td>5</td><td class="n">0.0566</td><td>the untrained QCR physics term …</td>
    <td>a best-on-board tie put at risk in writing before the call — lost, and left standing</td></tr>
```

Live, unstruck, in the page's own voice, in the row whose own cells are the
**round-5** number `0.0566`. It asserts a best-on-board tie that **never
existed** on the live six-entry board. Its enclosing block is `:181-192` and
contains **no board identifier at all**; the nearest is **51 lines away** and
outside the block. Under the chief's referent ruling an undated, present-tense
claim is graded against the **live** board, and against that board it is false.

The discriminator returned `CANNOT_TELL` here — table markup leaves no
linguistic cue — so it was **adjudicated by hand and is recorded as such**: the
cell is not quoted, not attributed, not set off, not struck, and its sibling
cells in rows 2–4 state facts in the page's own voice. It asserts.

**B1 alone fails the rung.**

### B2 — `closure.html:290-291`, the pre-registration freeze bullet

> The duct where we held a
> best-on-board tie got **no exemption** …

Live, unstruck, `ASSERT` by the discriminator, and **wrapped across a line
break inside the phrase** — which is why a literal-space recogniser misses it
and why every pattern here is built with `\s+`. Enclosing block `:285-294`
carries no board identifier; nearest is 31 lines away, outside the block.

**The strongest case against my own finding, stated and then answered:** the
bullet opens *"Committed 2026-08-05, before any solve"*, and on 2026-08-05 the
live board was the four-entry one, where `0.0325` **did** tie Reissmann's
`0.0325` for the minimum. So the sentence is arguably true of its own date. I
still count it, on the page's own rule: **a commit anchor or a bare date is not
an admissible board identifier** — a board is named by entrant count and
retrieval date or it is not named — and the identical clause on
`ACTIVE_RESEARCH.md` and on the submission package has now been repaired to
carry exactly that. The surfaces therefore do not carry *the same caveats*.
**The verdict does not depend on B2; B1 stands alone.**

### Not a blocker — `closure.html:350-351`

The same characterisation, but the six-entry correction is **inside its own
block** (`:350-365`), five lines below, naming the board by entrant count and
retrieval date and attaching **4th of 7**, **2 of 8** and **zero of 8 ours**.
It carries the caveats and is consistent with its sibling surfaces. The
uncorrected word `best-on-board` in its tie sentence is a real residual and is
**filed, not appended**.

### Clean on execution

`ACTIVE_RESEARCH.md` (both reopening sites repaired and correct: round 4 `2 of
7` tied with Reissmann behind Yang's `0.0250`, round 5 `4 of 7`),
`benchmarks.html`, `benchmarks.json`, `wall/wall.html`, `wall/wall.json`,
`build_benchmarks.py`, the submission package, and the eight CSVs. Two peer
repairs landed after my sweep frame and were **re-derived rather than trusted**:
`ACTIVE_RESEARCH.md:680`'s round-4 count (`5 of 8` four-entry → `2 of 8`
six-entry) and `DESCRIPTION_DOCUMENT.md:166`'s board identifier (`2 of 7` →
`4 of 7`) both reproduce exactly from the data.

Every live `P(rank 1)` statement on all five surfaces carries its interval or
its not-decided companion; three that first read bare resolved on opening
(`PRODUCT_LIST.md:67`'s interval sits at `:86`, in the same bullet).

---

## 5. The ruling I was asked to make explicitly — `docs/PRODUCT_LIST.md:1810-1812`

> on exactly the two cases the train-only gate DECLINED, the supplied baseline
> beats all four published entries (0.046108 vs 0.0569; 0.071863 vs 0.0760).

**Ruling: OUTSIDE the claim class. It does not fail the rung. Not repaired by
me.** Five grounds, each measured here:

1. **Its round-5 numbers are correct and current.** `0.046108` and `0.071863`
   are exactly `round5_per_case_full`'s values for the two cases.
2. **Its substance survives the board move.** Both still beat every one of the
   six live entrants (`0.046108 < 0.0569`; `0.071863 < 0.0748`). These are
   exactly the 2-of-8 best-on-board cases I derived. Only the comparand
   `0.0760` and the count *four* are stale; the finding is still true.
3. **It is superseded history, not superseding text** — the discriminator's
   `ASSERT` notwithstanding, which grades stance and not time-scope. Its
   governing heading is `### 2026-08-10 (night)` at `:1778`, in a
   reverse-chronological journal, predating the board move of 2026-08-11T23:33Z.
4. **It is protected history by the test the reopening itself used.** `:29` was
   ruled *not* protected because its own paragraph had been repaired
   `1 of 5`→`1 of 7`. I measured the governing block `1778-1813`: it carries
   **no in-place dated repair at all** and no mention of the six-entry board.
5. **The page does not contradict itself on its own face.** `0.0748` occurs
   **zero** times in the entire file, so the same-page pattern that made C1 and
   C2 blockers is absent — and the page's *live* statement at `:105-115` already
   says best-on-board is **2 of the 8** with **zero of the 8** ours, which is
   what I derived. The page's own rule at `:96-100` binds surfaces printing
   **"rank 1"**; `:1811` prints a comparison and no rank.

What stays wrong with it — a board named by count with no retrieval date — is
D238's class in a second file and is already filed as **D246**. Not re-filed,
not repaired.

---

## 6. Verdict

**`FAIL`**, on `closure.html:190-191` (independently sufficient) and
`closure.html:290-291`.

**I repaired nothing I graded.** The repair is routed to the owner of
`demo-output/website/closure.html`. The full live set is six instances; four
already comply; the two blockers and the `:351` residual are named above with
their block boundaries, so the repair does not need to re-derive them.

A re-grade after that repair is owed by a non-author of it and of this document.
