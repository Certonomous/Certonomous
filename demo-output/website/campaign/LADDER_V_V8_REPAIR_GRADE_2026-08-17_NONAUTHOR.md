# Ladder V — rung V8, grade of the `adff0697` repair, 2026-08-17 (non-author)

**Verdict: PASS.**

Owner: an agent that wrote none of the graded text, none of the repair under
test (`adff0697`), and none of the grade that ordered it
(`campaign/LADDER_V_V8_REVERIFICATION_2026-08-17.md`, `101079fd`).

**THIS RECORD IS LATE, AND THE LATENESS IS ITSELF A FINDING.** The grading was
performed and the `PASS` reached before this file existed. Nothing was committed
and no record was filed, so for a period the ladder cell correctly refused to
cite a verdict that had no artifact behind it — `4a207196` states exactly that,
and it was right to. **A verdict with no record is not a verdict, whoever reached
it**, which is the same standard this lab applies to a gate measured against a
reference that was never obtained. Filed as `D345`. Every measurement below was
re-executed at the frame in §0 before filing; none is transcribed from the
unrecorded round.

---

## 0. FRAME

| item | value |
|---|---|
| measurement frame | `32d4ae0d` (re-verification); first measured at `71879336` |
| graded set stability | `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` and `DESCRIPTION_DOCUMENT.md` are **byte-identical blobs** between `71879336` and `32d4ae0d`, verified by `git rev-parse <rev>:<path>`, so the earlier measurements carry forward |
| worktree | clean detached worktree, `git status --porcelain` = 0 entries |
| shared index | **never touched.** No `git add`, no `read-tree`, no bare commit. HEAD is the referent throughout; the index holds phantom entries and is never the frame |
| scoring calls | **zero.** Every figure is arithmetic over committed records |
| HEAD volatility | HEAD moved three times during measurement (`71879336` → `f40f6ef5` → `32d4ae0d`) under a live fleet. Each move was checked against the graded set rather than assumed away |

### R-CONVERGE — scope, adopted rather than re-cut

I adopted the `101079fd` round's declared scope **unchanged**, because re-cutting
a frame after seeing results is the failure R-CONVERGE exists to prevent:

1. **Artifacts:** the cover email (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §5) and
   the travelling package (`DESCRIPTION_DOCUMENT.md`, package `README.md`).
2. **Claims:** the blocking finding of `101079fd`, plus every quantitative or
   placement sentence in the graded set.
3. **Anything else → docket**, not appended to the rung.

That round ruled §5 **in frame**. I verified both of its grounds from source
rather than inheriting them: V8's own deliverable — *"A claims table: sentence →
artifact → verdict"* — **is** §5.2, and `LADDER_V_TRIPLE_VERIFICATION.md:502-503`
reads *"any text written during the ladder — by any pass, including fix passes —
must pass V8's claims table before the ladder goes green."* Both hold. Nothing
was added to the rung after grading; out-of-scope findings are `D345`–`D348`.

---

## 1. The criterion, quoted from source

`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md:339-344`:

> - **V8. Claims-language audit of the cover email + description document**: every quantitative
>   sentence maps to a named artifact; the banned-claims list enforced — no novelty claim on gated
>   correction (§7.4), no "comfortable" AR_14 lead (0.00003), no best-on-board counts that lean on
>   organizer-baseline rows (§4.7), no "official rank" language anywhere (local scoring stated
>   plainly), soft-adaptive-leakage disclosure present in the lab's own words (§4.3). A claims
>   table: sentence → artifact → verdict.

With the strengthening, amendment and recomputation note at `:345-381`: every
rank claim, internal or external, carries **P(rank 1)**, **its interval**, **its
board**, and the **not-decided pairs**.

Verdict vocabulary, `docs/charters/VERIFICATION_CHARTER.md:95-96`:

> **The verdict vocabulary is fixed.** Gate verdicts: PASS, GATE REACHED, GATE
> FAIL, NOT A RESULT, BLOCKED.

`PASS WITH RESIDUALS` and `PASS WITH EXCEPTIONS` are not in that list, were
withdrawn by ruling, and are not used here.

---

## 2. The aligned diff, re-derived — the `101079fd` finding CONFIRMED

Each side located by **its own heading line**, matched by pattern
`^>[-\s]{1,20}#{1,6}[-\s]{1,20}⛔` and asserted **unique** in each file, never by
line number. Joiners are `[-\s]{1,20}` throughout — never `\s+`, never a literal
space, because the banner wraps.

**Result, identical at `101079fd`, `71879336` and `32d4ae0d`: 3 of the 32 block
lines differ, at indices 0, 21 and 31.**

| index | role | old → new | declared? |
|---|---|---|---|
| 0 | heading | 82 → 62 B; `##` → `###`, text replaced | **yes** |
| 21 | `body21`, a table data row | 579 → 765 B | **no** — this was the finding |
| 31 | closer, blank → `>` | 0 → 1 B | **yes** |

**The table structure was derived from the block, not assumed:** header at index
13, separator at 14, **ten data rows at 15–24**. Index 21 is therefore
**row 7 of the ten**, first cell `§5.4, §5.2`. Confirmed against the brief's
statement and against the repaired text, both of which say "the seventh".

Body lines are indices 1–30 (thirty lines); only index 21 moved among them, so
**29 of 30 body lines matched** and **9 of 10 table rows matched**. Every
arithmetic sub-claim of the corrected certification checks out.

---

## 3. The pure-insertion claim, tested by execution rather than believed

The repair chose to correct the certification rather than revert index 21, on the
ground that `2cec44ee` was a **pure insertion**. That is a load-bearing claim: if
the commit had deleted or reworded anything, the reasoning that chose correction
over reversion fails and the verdict changes. **So it was rebuilt, not read.**

Method: take the longest common prefix and suffix of the old and new row, then
assert `prefix + inserted + suffix == new row` **byte for byte**, and separately
assert the deleted region is empty.

```
common prefix            397 B
common suffix            182 B
DELETED from old           0 B      ''
INSERTED into new        186 B      "*(figures as recorded at this banner's date
                                     against the four-entry board; the rule's live
                                     figures are 50% and 0–97% on the six-entry
                                     board — see §10's re-correction of 2026-08-12)* "
prefix + inserted + suffix == new row     True
PURE INSERTION (deleted region empty)     True
prefix + suffix == old row                True
```

579 + 186 = 765. **Nothing was deleted and nothing was reworded.** The same
decomposition holds for `514876b0 → 2cec44ee`, i.e. the row was untouched from
the ancestor through `2cec44ee~1`. **The repairer's central claim is confirmed by
execution, so the choice of correction over reversion stands.**

## 3.1 The commit walk — the certification was TRUE when written

All **16** commits touching the file across `e87650db^..HEAD` were replayed, each
one's block re-anchored on its own heading line and compared index by index
against `514876b0`:

- `2cec44ee` (2026-08-12 18:05:51Z) is the **only** commit to move any block line
  other than 0 and 31, and **no later commit touched index 21 again**.
- At `b65bdf01` (2026-08-11 02:42:53Z), where the struck clause was written, the
  block differed from `514876b0` at **indices 0 and 31 only** — so all thirty
  body lines were byte-identical and **the claim was true at the moment it was
  written**, then falsified the following day by a commit whose message named
  edits to §10 and to two rows *below* the banner and named no edit to the banner.

This is the substance of `D339`: the edit and the claim about it sat in different
registers, four lines apart, and nothing on the page joined them.

---

## 4. The board, re-derived — never quoted (defect class B4)

`sdk/scripts/probability_of_rank.py` re-run with `__pycache__` cleared, and the
per-case standings independently recomputed from `LIVE_BOARD` and the machine
record `closure_challenge_round5_qcr.json` rather than read across from any
sibling document.

| quantity | re-derived value |
|---|---|
| positions | **7** — six published entries plus ours |
| per-case ranks | **2, 2, 1, 1, 3, 4, 4, 7** of 7 |
| best-on-board | **2 of 8** — `alpha_05_4071_4048`, `alpha_05_4071_2024` |
| earned by our model | **0 of 8** — both sit in `unchanged_cases_sha256`, the organisers' own file passed through by the decline gate |
| overall | **0.056647191704213645**, **rank 1 of 7** |
| margin over Yang | **0.001365** |
| P(rank 1) | **50.2%**, 95% double-bootstrap band 0.2–96.9% → **0–97%** |
| not-decided pairs | **four** — Yang, Reissmann/Fang & Sandberg, Wu & Zhang, Tian/Buchanan/Hickel & Dwight |
| seed bound | script codes the rounded `0.0024` → **176%** of the margin; the precise `0.002419` → **177%** |

The seed-bound rounding is worth stating rather than smoothing: the shipped
figure of 177% is correct against `0.002419`, and a reader re-running the script
alone will get 176% from its coded constant.

---

## 5. The recogniser, its controls, and the zero that was not a result

### 5.1 Normalisation — blank delimiter classes, offsets preserved, in order

1. **strike spans** `~~…~~` — blanked **and tracked**, first;
2. **continuation prefixes** — leading indent, `>` blockquote markers, list bullets;
3. **emphasis** — `*` and backtick **only**. Never `~`, which class 1 owns; never
   `_`, which would corrupt `alpha_05_4071_4048` and `AR_14_Ret_180`.

Two buffers are produced and reconciled: strikes-preserved (so a struck claim can
be *seen and labelled*) and strikes-blanked (so struck text can never satisfy a
live claim's escorts). A span straddling a strike boundary is reported **MIXED**
rather than silently taken either way.

### 5.2 THE ZERO THAT WAS NOT A RESULT — recorded because it nearly passed

**The first build of this recogniser returned 0 sites across 2,014 files.** The
corpus is not clean; the instrument was broken. The cause:

```
[-\s]{1,20}?     is a LAZY quantifier, not an optional one
(?:[-\s]{1,20})? is the optional one
```

Written `J + "?"` intending "optional joiner", every joiner still demanded at
least one character, so `P(rank 1)` — with nothing between `P` and `(` — could
never match. **A zero taken as a result here would have been a clean-looking
false pass on the exact rung under audit**, and it would have been indistinguishable
from a compliant corpus. It was caught only because a zero was treated as a
trigger to build the recognition control rather than as a finding. Filed as `D347`.

A second defect was caught the same way: matching only the strikes-blanked buffer
made the STRUCK branch dead code, and matching only the strikes-preserved buffer
misread `P(rank 1) is ~~91%~~ **78.5%**` as a live 91% claim — label live, value
struck. Hence the two-buffer reconciliation in §5.1.

### 5.3 Known-site recall

Against an **independent** crude locator (raw text, no normalisation, generous
pattern), run over the two in-scope documents:

- crude locator: 23 mentions of a rank-1 probability;
- recogniser: **19 value-bearing sites**;
- the 4 not matched carry **no percentage at all** — they are rule statements, correctly not figures.

**Known-site recall: 19 of 19 value-bearing sites.**

### 5.4 Controls, with their kind stated

A zero requires a **RECOGNITION** control, not a reachability one. Plants were
inserted **by line index, never by anchor string**, into quiet neighbourhoods
(chosen as line offsets whose ±600-character window carries neither escort, so a
positive plant cannot be rescued by real surrounding text), in **both** in-scope
documents, and **every plant was read back from disk before the recogniser ran**.

| plant | kind | expected | result |
|---|---|---|---|
| P1 canonical bare `P(rank 1) = 50%` | POSITIVE | VIOLATION | PASS ×2 |
| P2 verb form `P(rank 1) is 50.2%` | POSITIVE | VIOLATION | PASS ×2 |
| P3 spelled out `probability of rank 1 of 50%` | POSITIVE | VIOLATION | PASS ×2 |
| P4 wrapped across a line + emphasis | POSITIVE | VIOLATION | PASS ×2 |
| P5 hyphen joiner `P(rank 1)-=-50%` | POSITIVE | VIOLATION | PASS ×2 |
| P6 interval present, board absent | POSITIVE | VIOLATION | PASS ×2 |
| P7 board present, interval absent | POSITIVE | VIOLATION | PASS ×2 |
| N1 `~~P(rank 1) = 50%~~` | **NEGATIVE — struck; must stay SILENT** | STRUCK | PASS ×2 |
| N2 figure + interval + board | **NEGATIVE — compliant; must not fire** | OK | PASS ×2 |

**Positive plants recognised: 14 of 14. Negative controls held: 4 of 4** — two
struck (which stayed silent) and two escorted-compliant (which did not fire).
The struck negative control is what proves class 1 of the normalisation is doing
work rather than the pattern merely failing.

### 5.5 In-scope result

Whole files swept, never enumerated ranges. **21 sites, 0 sustained violations.**
Two flags, both adjudicated by reading as recogniser false positives:

- `DESCRIPTION_DOCUMENT.md:281` — `65.4%`, the favourable seed-loading figure,
  whose own sentence concludes *"a seed we did not control moves the headline
  figure by thirty-one points"*;
- `DESCRIPTION_DOCUMENT.md:529` — `78.5%`, the leave-one-out figure for deleting
  `NASA_2DWMH`.

Both are **conditional sensitivity figures inside passages whose headline claims
at `:271` and `:453` carry interval and board**, and both exist to show the
standing is *not* settled — the opposite of the bare-probability defect the rule
prohibits. Neither is a standing rank claim. Neither was written by this repair.

Banned-claims legs, swept over whole files with the same normalisation: no
"comfortable" lead; no novelty claim on gated correction; and all **7** hits for
"official rank"/"official placement" are the **negated** required disclaimer
(*"not an official placement"*, *"Not an official rank"*) — a polarity limitation
of the sweep, not a defect in the text.

### 5.6 Independent corroboration

- `sdk/tests/test_rank_claim_surfaces.py` — **152 passed, 26 subtests passed**.
- `scripts/check_normative_clauses.py` — **VERDICT: PASS**, 1108 clauses examined,
  **0 graded false**, 1 UNDECIDABLE (the known `D119` residual at
  `LADDER_V_V13_CLOSEOUT.md:203`, already filed and out of this rung's scope).
- `scripts/check_verdict_cells.py` — 16 rows read, **0 FAIL**.

---

## 6. VERDICT: PASS

The single blocking finding of `101079fd` — the false byte-identity certification
— is repaired, and the repair is sound on every checkable point:

1. the corrected certification is **true at the graded frame by independent
   re-derivation**, on all of its arithmetic (3 of 32; indices 0, 21, 31; index 21
   = row 7 of ten; 29 of 30 body lines; 9 of 10 rows; 579 → 765 B);
2. the reasoning that chose **correction over reversion** rests on a
   pure-insertion claim **confirmed by rebuilding the bytes**, not by reading the
   commit message: 186 B in, **0 B out**;
3. reverting would indeed have reinstated an un-scoped four-entry mandate — the
   row **mandates** rather than narrates, and `W-4` forbids deleting a dated
   repair — so the repair's justification holds on its own terms;
4. no other leg of the rung fails, on the recogniser, on the banned-claims sweep,
   or on the lab's own three instruments.

No label outside the charter's fixed vocabulary is used, and no residual is
carried into the verdict word. The out-of-scope findings are **filed** as
`D345`–`D348`, not appended to this rung.

---

## 7. The instrument's named blind class

**PRIMARY: strikeout in rendered PDFs is invisible to text extraction.**

**Demonstrated by controlled experiment, because I first asserted this on
evidence that did not support it and the correction is the useful part.** A
minimal document was built with `pdflatex` and extracted with `pdftotext -layout`:

```
source :  Live claim: P(rank 1) = 50\%.
          \sout{Struck claim: P(rank 1) = 68\%.}
output :  Live claim: P(rank 1) = 50%. Struck claim: P(rank 1) = 68%.
```

The struck sentence extracts as plain text, carrying **no marker of any kind**.
The strike class — class 1 of §5.1, the entire basis on which this recogniser
stays silent — **does not exist on a rendered page**. Any PDF-surface audit is
strike-blind in both directions: it will read repaired text as live, and it
cannot tell a genuine violation from a struck one. Filed as `D346`.

**THE CORRECTION.** I initially reported the three flags this recogniser raised
on `demo-output/website/latex/closure_challenge_report.pdf` (rendered lines 254,
305, 739, each `P(rank 1) = 68%`) as "3 for 3 false positives from
strike-blindness", reasoning from the repaired `.tex`, which carries six `\sout{}`
68% sites and five live 50% sites. **That was wrong, and it was wrong in the
exact way this rung exists to catch: I inferred a mechanism instead of testing
whether it applied here.** Re-measured on the artifact itself:

| check on the rendered PDF | result |
|---|---|
| occurrences of `P(rank 1) = 50` | **0** |
| occurrences of `P(rank 1) = 68` | 6 |
| occurrences of `six-entry` or `Yang` | **0** |
| PDF last committed | `98a39662`, 2026-08-11 03:29Z |
| `.tex` repaired | `2cec44ee`, 2026-08-12 18:05Z |

The PDF contains none of the post-repair text. **It is a stale build that predates
the strikes entirely, so its 68% figures were never struck and the three flags
were TRUE POSITIVES, not false ones** — they restate `D115`, which already records
that artifact as a complete four-entry-board document. The blind class is real
and is now demonstrated on its own terms above; this artifact was simply not an
instance of it.

**Also named:**

- **Polarity blindness** in the banned-claims sweep — 7 of 7 "official rank" hits
  were negated disclaimers. The sweep finds vocabulary, not assertion.
- **Conditional versus headline claims** — a window-based escort test cannot tell
  *"P(rank 1) = 50%"* from *"delete this case and P(rank 1) is 78.5%"*. Both
  in-scope false positives are this class.
- **Fixed 600-character escort window** — an interval or board just outside it
  reads as absent.
- **Corpus reach: 2,014 of 13,968 tracked files.** Blind to 11,954: 8,049
  extensionless (OpenFOAM field files), 990 `.water`, 875 `.png` (**no OCR — an
  image-borne claim is invisible**), 436 `.log`, 122 `.gz`, 54 `.stl`. All 57
  PDFs were **rendered, never grepped**; the 7 lab-authored surfaces plus 3 lab
  posters initially misfiled as literature were rendered and are clean, leaving
  47 third-party papers unrendered as non-claim sources.
- **A count that self-corrected.** `git ls-tree | split()` reported 14,057 files
  and 56 PDFs; NUL-delimited it reports **13,968 and 57**, because `split()`
  breaks filenames containing spaces. The disagreement between two counts of the
  same thing was treated as a re-run trigger, not as a number to pick between.

---

## 8. Two live discrepancies — reported, NOT resolved

### 8.1 The charter says GATE FAIL; the rung cells say bare FAIL

**This figure is frame- and reading-dependent, and both must be stated or it is
not a measurement.** Rung rows are the 16 lines matching `^\| V\d+ `; "bare FAIL"
counts rows where `\bFAIL\b` survives after `GATE[-\s]{1,20}FAIL` is blanked.

| frame | reading | bare FAIL | GATE FAIL |
|---|---|---|---|
| `71879336` | whole row, strikes **kept** | **10** | **1** |
| `71879336` | whole row, strikes **blanked** | 6 | 1 |
| `71879336` | **verdict cell only**, strikes blanked | 6 | 1 |
| `32d4ae0d` | whole row, strikes **kept** | 11 | 2 |
| `32d4ae0d` | whole row, strikes **blanked** | 6 | 2 |
| `32d4ae0d` | **verdict cell only**, strikes blanked | 6 | 2 |

**The "10 bare FAIL, 1 GATE FAIL" figure carried in the unrecorded round was
whole-row with strikes KEPT, at frame `71879336`** — it does **not** reproduce
under strikes-blanked at that or any frame, and it no longer reproduces at all at
`32d4ae0d`, because `4a207196` rewrote eleven verdict cells in between. A
correction offered to me attributed that figure to the strikes-blanked reading
and gave 7 bare FAIL / 0 GATE FAIL on verdict cells alone; **neither number
reproduces under my extraction at either frame** (I get 6 and 1, then 6 and 2).
I record the disagreement with my method fully stated and **do not resolve it** —
it needs a single agreed definition of "the verdict cell" before any of these
numbers means anything. The substance stands either way: the charter's `GATE
FAIL` is a minority form in the ledger.

### 8.2 "row 22"

`LADDER_V_V8_REVERIFICATION_2026-08-17.md:182` says index 21 *"is row 22"*. Index
21 is the block's **22nd line** and the defect table's **7th of ten data rows**;
there is no row 22 in a ten-row table. The repaired text in the draft says *"the
seventh"* and is correct, so the loose wording is confined to that grade record.
**Reported, not resolved.**

---

## 9. Filed to the docket, not appended to this rung (R-CONVERGE)

| row | finding |
|---|---|
| `D345` | this record's own lateness — a grade reached and never filed, so the rung silently reverted to a stale verdict |
| `D346` | strikeout is invisible to `pdftotext`, so every PDF-surface audit is strike-blind — with the correction that my own first evidence for it was a stale build, not an instance |
| `D347` | the lazy-quantifier zero, filed as a defect class rather than as an instance |

**Four findings I carried were checked against the docket before filing and are
NOT filed, because each is already held by an open row** — and in two cases the
existing row is better than what I had:

- **Clause (d) of `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` reaches its board only
  by pointer.** Already `D341`, opened and read at frame `a5080f6e`, which states
  it more precisely than I did.
- **The withdrawn-label census.** Already `D342`, **which corrects my figure**: the
  "120 live occurrences" I carried was a **line** count, not an occurrence count,
  and it never separated use from mention. `D342` measures 153 occurrences on 121
  lines across 24 files — **49 uses, 104 mentions**. My re-measurement at
  `32d4ae0d` (160 / 123 / 24) is a third and differently-defined count and is
  superseded by `D342`'s split. Both in-scope documents are clean at **0** on
  every reading.
- **`check_normative_clauses.py`'s summary-line arithmetic.** Already `D343`.
- **`D339`'s remedy — no executable grades a byte-identity assertion.** Already
  `D344`, which declares the search over every check in `scripts/`. This is
  precisely what made a fourth hand re-derivation necessary here, and it is why
  this grade re-measured the bytes rather than citing the three rounds before it.
