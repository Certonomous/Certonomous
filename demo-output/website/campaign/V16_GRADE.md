# V16 — independent grade of the placement guard

**Grade: PASS WITH EXCEPTIONS.**

Rung: **V16 (A16)**, `demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md`.
Subject: `scripts/self_audit.py::check_board_placement_words`, tests
`sdk/tests/test_rank_claim_surfaces.py`, built at `862d2cff`, rung text at
`147a68c6`, lessons at `ba5a8cbc`.

Graded 2026-08-11 by an agent that wrote none of it, under the ladder's rule that
no agent verifies work it produced. The builder declined to grade it and said so
in the status ledger; that is why this document exists.

**Nothing here was fixed.** Every finding below is reported and left standing, per
the brief and per this lab's rule that a fix authored in the same pass as the
finding destroys the record of which is which. `scripts/self_audit.py` and
`sdk/tests/test_rank_claim_surfaces.py` were not modified. All probe scripts were
written to a scratchpad outside the repo.

**Writing convention of this document**, borrowed from the test file it grades:
the defect strings are described rather than reproduced, and every illustrative
placement uses a placeholder entrant. A grade that reddens the guard it is
grading would be teaching the lab the lesson L-70 spent a night unlearning.

---

## 1. The headline, which I was not looking for

`demo-output/website/latex/closure_challenge_report.tex`, committed and in the
tree at grading time, contains this, with the line break exactly where it is:

> `The published entry ranked`
> `second before round 5 --- Wu \& Zhang's SST-QCRC --- carries the same untrained`
> `QCR2000 term`

That sentence is:

1. a **placement pinned on a named board entrant**;
2. **wrapped across a line break**, which is the failure mode this rung was
   opened for;
3. on the **LaTeX source of a compiled report** — the surface class the sibling
   guard's own blind-spot note calls out ("a claim living only in a built PDF is
   invisible here while its .tex source is not");
4. a **reworded sibling of defect A** — same subject, same claim, same clause
   about the same untrained term; and
5. **completely invisible to the new guard**, because `ranked second` is not in
   its pattern set.

It happens to be **correct** — Wu and Zhang are rank 2 on the published board, so
"ranked second before round 5" states the truth. That is luck, not the guard's
doing. Had a writer typed a different ordinal into that sentence, the guard would
have returned green.

This is **L-61 recurring one widening later.** The guard was moved off digits
onto two word-patterns, and the very next member of the same sentence family
arrived in a third pattern. It does not falsify the rung — the rung's claims are
about what the guard does, and it does them — but it is the reason the reach
statement in §6 matters more than any of the numbers.

---

## 2. Claim-by-claim verdicts

### Claim 1 — the board is parsed from the benchmark's own README, not transcribed

**VERDICT: VERIFIED**, and by a stronger test than the author's own.

The author's evidence is a synthetic two-row README in
`TheBoardIsParsedTests::test_a_different_board_gives_a_different_verdict`. I ran
the harder version: I took the **real** `~/closure-challenge-benchmark/README.md`
at `deb91557` and rewrote only the two rank digits, leaving every author cell,
column, score and link untouched.

| board | parsed | faults on one fixed probe sentence |
|---|---|---|
| real README | `reissmann 1, wu 2, liu 3, montoya 4` | **0** |
| same README, rank digits 1↔2 swapped | `reissmann 2, wu 1, liu 3, montoya 4` | **1** |

The same sentence flips clean→faulted on a one-digit edit to a file outside this
repository. A transcribed constant cannot do that. Traced in code: the board
comes from `_BOARD_ROW` over `(root / "README.md")` where `root` is
`$CLOSURE_BENCHMARK_DIR` or `~/closure-challenge-benchmark`; there is no board
literal anywhere in `self_audit.py`. `_pinned_board_commit()` likewise reads the
pinned SHA out of the travelling package rather than carrying it.

**But the ordinal vocabulary is a constant, and it is not derived from the board
it is checked against.** `_PLACE` and `_PLACE_WORD` cover 1–5 only. On a board
with six or more entrants the guard silently stops seeing placements past fifth:

| probe, on a synthetic 7-row board | rule A |
|---|---|
| `rank-2` pinned on the rank-6 entrant | **1 fault** |
| `rank-6` pinned on the rank-6 entrant's rival | **0 — not matched at all** |
| `sixth-place` pinned on a named entrant | **0 — not matched at all** |
| `seventh place` pinned on a named entrant | **0 — not matched at all** |

So claim 1 holds for the mapping and fails for the range: the guard is evidence
about *which rank an entrant holds* and a constant about *which ranks exist*. The
board grew from 3 rows to 4 during this campaign; a fifth competitor is not
hypothetical.

**Five further ways the parse breaks, none of them live today.** Each was run:

| attack | result |
|---|---|
| column header renamed `Rank`→`Position` | **survives** — the regex never reads the header |
| CRLF line endings | **survives** |
| README missing / clone absent | `None` → detector reports **OFF**, correct |
| author cells no longer markdown links | `None` → **OFF**, fails safe |
| rows indented, or rank column moved | `None` → **OFF**, fails safe |
| header row only, no entries | `None` → **OFF**, fails safe |
| **a second numbered-and-linked table later in the README** | **silently corrupts the board** — any `\| N \| [text` line anywhere in the file is read as a leaderboard row, last one wins; a decoy `Cases` table moved one entrant from rank 4 to rank 3 with no warning |
| **two entrants sharing a first-author surname** | **silently drops one** — the dict comprehension keys on surname, so a 2-row board parses to 1 entry and then faults a *correct* sentence |
| **a particle surname** (`van Dijk`) | keys the board on `van`, which then binds to every occurrence of that word in prose — a false-positive generator |
| **a surname that is an ordinary word** (`Best`) | same; verified firing on innocent prose |
| **a surname with an unbalanced regex metacharacter** (`Fox[a`, `Fox(`) | `re.error` — **an uncaught exception that takes down the whole `self_audit` run**, not a WARN and not an OFF |

The four OFF outcomes are the good half of this table: the detector's failure mode
is to announce it is off rather than to report an empty corpus, which is the
property the rung's precision requirement is really about. The three silent-
corruption rows and the one crash row are not live defects — today's README has
none of these shapes — but they are the difference between "parsed" and "parsed
defensively", and the parse currently has no assertion that what it read looks
like a leaderboard.

### Claim 2 — whole-text matching, with a control that is not vacuous

**VERDICT: VERIFIED, with the justification for it already retracted by its own
author and still standing on two surfaces.**

`_placements` collapses whitespace before matching; `WholeTextNotLinesTests`
asserts 1 fault whole-text against 0 line-bounded on a pair differing only in a
line break, and the 0 carries the message *"the control is void: a line-bounded
reader would have caught this too, so it proves nothing"*. I re-ran it: it passes
and the control is live, not vacuous. Good design, and the assertion-message
trick is the right general answer to a control that can quietly retire.

**The retraction.** The rung text in `LADDER_V_TRIPLE_VERIFICATION.md` and the
comment block in `self_audit.py` both justify whole-text matching by saying the
real parent instance in `CLOSURE_CHALLENGE_STATUS.md` breaks the line mid-phrase
and so *"a line-bounded reader is defeated by a reflow"*. I checked that against
the real pre-fix text at `c314b5d0^`:

| the real parent instance | faults |
|---|---|
| whole-text reader | 1 |
| line-bounded reader | **1** |

It is not defeated. The wrap in that sentence falls inside the entrant's name,
after the first-author surname the guard keys on, so the binding survives either
way. The author **found this and published it against its own interest** in
`docs/PRODUCT_LIST.md` — *"this guard keys on the first-author surname, so it
survives that wrap either way… the synthetic control is what proves whole-text
matters"* — which is the honest reading and is to its credit.

What was not done is propagate it. The superseded justification is still the live
text in the **shipped guard's own comment block** and in the **ladder's rung
definition**, which is the copy a future rule-author reads. Correct fact in the
lab record, superseded fact in the two places that travel to a reader: the
distribution failure this ladder keeps naming.

### Claim 3 — 20 of 21 tests fail against HEAD, verified in an isolated worktree

**VERDICT: VERIFIED IN SUBSTANCE, WRONG IN COUNT.**

Reproduced independently: `git worktree add --detach` at `862d2cff^`
(= `ded64e0c`), unmodified source, only the post-V16 test file copied in.

```
21 failed, 14 passed in 0.26s
```

Every failure is `AttributeError` on `check_board_placement_words`,
`board_placement_faults`, `_published_board`, `_placements`, `_BOARD_DIR_ENV` or
`_pinned_board_commit` — functions that did not exist. The one new test that
passes at HEAD is
`TheWordFormGuardTests::test_the_digit_guard_could_not_have_seen_any_of_them`,
and it passes because it asserts the old guard's blindness, which was true then
and is still true now. That is exactly as claimed.

**The count is off by one in both numbers.** `git diff 862d2cff^ 862d2cff` adds
**22** test methods, not 21; **21** of them fail at HEAD, not 20.
`TheWordFormGuardIsRegisteredTests` carries five tests and appears to have been
counted as four. The claim's structure — all but one fail, and the exception is
deliberate — survives intact; the arithmetic does not. Both the commit message
and the ladder's status ledger carry the wrong figure.

At HEAD today the full file is **35 passed** (13 pre-existing + 22 new).

### Claim 4 — false-positive rate 0 over a 111-file corpus, 421 expressions, 63 bound

**VERDICT: THE RATE IS VERIFIED. THE DENOMINATOR IS NOT REPRODUCIBLE.**

Re-derived rather than read, with my own corpus filter (tracked, UTF-8, under
4 MB, containing `rank` or `runner`, and — for the board corpus — also referencing
the leaderboard by entrant name or by the words *leaderboard*, *closure
challenge*, *published board*):

| frame | files | placement expressions | bound to an entrant | rule A faults | rule B faults |
|---|---|---|---|---|---|
| repo-wide, **at `862d2cff`** | 972 | 493 | 65 | 1 | 1 |
| my board corpus, **at `862d2cff`** | 122 | 434 | 64 | 1 | 1 |
| repo-wide, **today** | 974 | 503 | 70 | 1 | 1 |
| my board corpus, **today** | 122 | 442 | 69 | 1 | 1 |
| **author's stated board corpus** | **111** | **421** | **63** | **0** | **0** |

Three separate things here, and they get three separate verdicts.

**The rate itself: verified.** I read every one of the 974 repo-wide surfaces and
found exactly two faults, both in `docs/INSTRUMENT_INTEGRITY_LEDGER.md`, and both
are that file quoting the three defects in order to name them — the declared
use/mention class, correctly scoped to WARN. Outside that class, **zero false
positives on 503 placement expressions repo-wide**, which is a stronger frame than
the author's own corpus and a stronger result than claimed. The precision claim is
real and it is the part of this rung I would defend hardest.

**The denominator: not reproducible.** No record anywhere in the repo states how
the 111-file corpus was selected. I could not construct a filter that returns 111;
the nearest reasonable definitions return 122. The number is therefore a figure
without a method, in a rung whose own text requires the false-positive rate be
stated "against a **measured** corpus". The measurement is sound; the corpus is a
citation to a sweep whose selection rule was not written down. (A coincidence
worth one line and no more: `_travelling_names()` also returns exactly 111 names
today. I could not connect the two and do not assert they are related.)

**"Zero false positives" was already not true of the live tree at commit time.**
`INSTRUMENT_INTEGRITY_LEDGER.md` was committed at 03:10:47; the guard shipped at
03:18:55, and on its own tree at its own commit it returns **WARN with 2 lab-record
faults**, not PASS. The author states this plainly in `PRODUCT_LIST.md` ("it bit
within the hour, correctly") and I agree with that reading — a mention is not a
false positive under a rule that declares it cannot tell mention from use. But the
headline **0** and the live verdict **WARN** are not the same sentence, and the
one that travels is the headline.

**One more count that does not reconcile.** The commit message says the guard
"surveys 497 placement expressions repo-wide". Run against the committed state of
its own commit, the check's own frame line prints **493**. Four expressions'
worth of dirty working tree.

### Claim 5 — fires on all three defects as they were, and on none as they now are

**VERDICT: VERIFIED, and against the real text rather than the fixtures.**

The tests assemble their fixtures at run time, which is the right discipline but
means the tests prove the guard fires on *reconstructions*. I ran it on the actual
historical files out of `git show`:

| surface | revision | rule A | rule B |
|---|---|---|---|
| `…round5/DESCRIPTION_DOCUMENT.md` | before F1 (`c314b5d0^`) | **1** | **1** |
| `…round5/DESCRIPTION_DOCUMENT.md` | before F5 (`f4f2a3d6^`) | 0 | **1** |
| `…round5/DESCRIPTION_DOCUMENT.md` | HEAD | 0 | 0 |
| `CLOSURE_CHALLENGE_STATUS.md` (the parent) | before F1 | **1** | 0 |
| `CLOSURE_CHALLENGE_STATUS.md` | HEAD | 0 | 0 |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | before F1 | **1** | 0 |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` | HEAD | 0 | 0 |

All three fire as they were and none fires as it now is, on the real bytes. The
draft's instance is a **fourth** hit the claim does not enumerate — a placement
word bound to the rank-1 entrant, caught by rule A rather than rule B — and the
regression test does cover that file. Claim understated, not overstated.

### Claim 6 — severity scoped: WARN on a lab record, FAIL where a surface travels

**VERDICT: VERIFIED in behaviour; the travelling set is coarser than it reads.**

The scoping is real and correctly motivated by L-70: `check_board_placement_words`
buckets on `path.name in _travelling_names()`, returns FAIL if anything in the
travelling bucket faults, WARN if only lab records do, and reports both counts
either way. The live run returns WARN with the two ledger mentions and no
travelling fault, which is the right answer at the right severity.

**The set is matched by basename, not by path.** `_travelling_names()` returns 111
bare filenames drawn from shipping archive members and submission-package
contents; **65 tracked files outside any package share a name with one of them**,
including the repository's root `README.md`, `demo-surfaces/README.md`,
`docs/charters/README.md` and several others. For `closure.html` and `wall.html`
the classification is right for the wrong reason — they do travel, but via the
bundle, not via the name match. The error direction is **conservative**: it
upgrades WARN to FAIL, so it over-reports severity rather than under-reporting it,
which is the safe way for this to be wrong. It is still a name collision doing the
work of a provenance check, and one day a lab record will inherit a FAIL it did
not earn.

### Claim 7 — the amendment from 15 rungs to 16

**VERDICT: ACCURATE AND COMPLETE.** This was worth the look and it survives it.

`147a68c6` changes exactly three live statements and no others: the termination
rule's item 1 (`V1–V15` → `V1–**V16**`), the send gate (`all 15 rungs green` →
`all 16 rungs green (13 original + V14/V15, added 2026-08-10; + V16, added
2026-08-11)`), and the status-ledger row for V16. The termination-rule line
carries an inline note that it previously read V15, which is the right treatment —
a range that grows silently is how a gate stops gating, and this one does not grow
silently.

Swept the whole tree for residual `15 rungs` / `V1–V15` / `all 15` statements. One
match remains, `LADDER_V_V15_LADDER_TEXT_CLAIMS.md:235`, and it is a **quotation
inside a claims table**, attributed to Katie's `8ef715c1`, recording what the gate
said at that time. Correct to leave: it is a historical record of a claim, and the
ladder's own reopening rule exempts its reports. No other surface in the repo
states a rung count. Nothing else in `147a68c6` touches the gate.

---

## 3. L-66's test: the crudest rival rule

L-66 asks whether the corpus can tell a principled rule from a dumb one. The
author did not run this. I ran three rivals over the same 974 files, comparing
per-file fault counts against the shipped guard.

| rival | disagreements with the shipped guard |
|---|---|
| **R1** — identical matching machinery, board **typed in as a constant** | **0 of 974** |
| **R2** — crude literal: a digit-3 rank token within 40 chars of the rank-2 entrant's surname, plus one fixed comparative phrase | 5 of 974 |
| **R3** — the dumbest thing that works: two fixed substrings | 5 of 974 |

**R1 is the finding.** A hand-transcribed board and a parsed board produce
**identical verdicts on every file in this repository**. The corpus therefore
contains **no evidence whatsoever** for claim 1 — not because claim 1 is false, but
because a corpus scored against a board that has not changed cannot distinguish a
parse from a constant. Every argument for the parsed board's superiority is, on
corpus evidence alone, theoretical.

That is a scope statement and not a fault, and the reason is that the author
already did what L-66 prescribes as the remedy: **it constructed the
discriminating case.** The permuted-README test is precisely "go find or construct
the case the archive does not yet contain." So the correct sentence is: *the
guard's board-parsing is evidenced by one constructed case and by zero corpus
cases,* and the rung's write-ups should say the first half rather than pointing at
the corpus.

**R2 and R3 do disagree, and always in the same direction.** Both crude rivals
over-fire on files the shipped guard correctly clears — audit records that quote
the defect and state the truth beside it, cleared by rule A's 400-character
adjudication clause, and `self_audit.py`'s own comment block. So the corpus **does**
evidence the guard's precision advantage over a literal, on five files. It
evidences **no recall advantage at all**: there is not one file in this repository
where the shipped guard fires and a crude literal does not.

---

## 4. L-61's test: the held-out set, and the miss rate

L-61 asks whether a guard is anchored to the claim or to the spelling of the
examples that prompted it. The only held-out sample that exists is one nobody in
this repo has written, so I invented 45 placement expressions, each pinning a
**wrong** placement on a **named** board entrant. None is a paraphrase of the three
defects. Illustrative forms are shown with a placeholder entrant so that this
document does not itself become a defect.

**Miss rate: 40 of 45 — 89%.**
**Excluding the 5 the guard's own blind-spot list already claims: 35 of 40 — 88%.**

| family | example shape | caught |
|---|---|---|
| possessive ordinal | *"X and Y's third place on the board"* | **2 / 2** |
| hyphenated compound | *"the third-place-finishing X and Y entry"* | **1 / 1** |
| parenthetical, rank token | *"X and Y (rank 2) publish an overall of…"* | **1 / 1** |
| rule B, one fresh phrasing | *advantage over the* + ordinal + *-place entry* | **1 / 1** |
| parenthetical, bare ordinal | *"X and Y (3rd) carry the same term"* | 0 / 1 |
| written ordinal, no *rank*/*place* | *"the third entry, X and Y, runs…"* | 0 / 2 |
| verbal placement | *placed / finished / came / took* + ordinal | **0 / 4** |
| participle and verb | *"ranked third"*, *"rank second"*, *"third-ranked entry"* | **0 / 3** |
| numeric designator | *"No. 3"*, *"#3 is X and Y"* | 0 / 2 |
| position / slot | *"hold position 3"*, *"the board's third slot"* | 0 / 2 |
| bare ordinal predicate | *"are in third"*, *"third overall"*, *"third-best"* | 0 / 3 |
| structured rows | a markdown table row, a CSV row | 0 / 3 |
| medal and podium | *silver*, *bronze*, *on the podium at number two* | 0 / 3 |
| *top the board* | *"X and Y top the published board"* | 0 / 2 |
| ordinal as noun phrase | *"X and Y, the board's third"* | 0 / 1 |
| plural / list form | *"ranks two and three are X and Z"* | 0 / 1 |
| roman numeral | *"Rank III on the published board is…"* | 0 / 1 |
| non-English ordinal | a German placement sentence | 0 / 1 |
| rule B, other fresh phrasings | *beat the runner-up by…*, *clear of the second-place submission*, *the gap between us and the front-runner*, *over the leader* | **1 / 5** |
| *(declared blind)* relational comparatives | *ahead of*, *trails*, *next-best* | 0 / 3 |
| *(declared blind)* co-author naming | the second author's surname in place of the first | 0 / 2 |

The five hits are all cases where the invented text happens to contain
`rank <digit>`, `<ordinal>-place`, `runner-up` or `front-runner`. That is the whole
of the guard's reach. **The guard is anchored to two spellings of the claim, not to
the claim.** It is a strictly wider anchor than the digit guard it replaces — three
real defects prove that — but it is an anchor of the same kind, one widening along.

Two cautions on my own number, because a miss rate is only as good as its sample.
Some of my 45 are in registers this lab does not write (medals, German). Others are
squarely in its register — *ranked second*, *third overall*, *third-best*, a table
row — and **one of them is in the tree right now** (§1), which is the answer to
whether the invented set is fair. A live scan for placement-shaped expressions
outside the pattern set, bound to a board entrant, returns **three** real passages:
the report source in §1, and two source comments naming the rank-4 entrant as `#4`.
All three are correct today. None of them is checked by anything.

---

## 5. Blind-spot completeness

The rung fails if the check does not "name the senses of the word it excludes."
On **exclusions it is complete and it is good work**: `P(rank …)` as probability,
`rank N of 5` as the sibling guard's territory, linear-algebra rank restricted to
word numerals after the author caught its own over-broad version eating a correct
sentence, MPI rank, sentence boundaries, and the eleven measured idiom hits that
cut rule B down. Every one is an exclusion of a *sense*, never of a *surface*,
and the code says so in those words. `HomonymsOfTheWordTests` covers all of them
and I could not find a homonym class in the corpus that is unhandled.

On **reach**, the declared list is incomplete, and it is incomplete in the one
direction that matters.

| blind spot | in the frame line? | in BASIS? |
|---|---|---|
| relational comparatives (*ahead of, behind, trails, leads, next-best*) | yes | yes |
| entrant named by a co-author | yes | yes |
| non-UTF-8 surfaces | yes | yes |
| untracked files | yes | yes |
| archive members | yes | yes |
| dated history vs live claim | yes | yes |
| adjudication by 400-character proximity | **no** | yes |
| rule B cannot tell use from mention | **no** | yes |
| files over 4 MB (`_RANK_MAX_BYTES`) | **no** | **no** |
| **any placement phrased outside the two patterns** | **no** | **no** |
| **any board position past fifth** | **no** | **no** |

The last two are the exceptions that cost this rung a clean pass.

The **sibling** guard — the older, digit-anchored one this rung exists to
supersede — declares in its own BASIS: *"a rank claim phrased outside its patterns
(\"we top the board\")"*. The new guard **drops that admission**, while having the
same limitation at an 88% rate on held-out phrasing and at least one live instance
in the tree. A guard that widened its patterns also narrowed its statement of what
its patterns miss.

L-61's own words are the standard here: *"a caveat in a comment does not reach the
person reading the verdict — the verdict must carry its own reach, or the caveat is
decoration."* The frame line is the verdict's reach statement, it is well written,
and it currently reads as though relational comparatives were the largest
remaining slice of placement language. They are not. **Every non-relational
phrasing outside two regexes is a larger slice**, and it is the one a reader of the
green verdict will assume is covered. An under-stated blind-spot list is worse than
none, because the verdict line is read as coverage — which is the sentence in the
brief that sent me looking, and it is the sentence that lands.

---

## 6. Grade

**PASS WITH EXCEPTIONS.**

**What earns the PASS**, and it is earned rather than conceded:

- The board **is** parsed. Verified by permuting the real benchmark README, not
  a fixture, and by tracing every path in the code. No board literal exists.
- The false-positive rate **is** zero outside a declared and correctly-scoped
  class, re-derived over a frame wider than the one claimed — 503 expressions
  repo-wide, 2 faults, both mentions in one lab record.
- The tests **do** fail against unmodified HEAD in a genuinely isolated worktree,
  and the one that passes there passes for the stated reason.
- The guard **does** fire on all three defects as they were and on none as they
  now are, verified on the real historical bytes rather than the fixtures, plus a
  fourth instance the claim did not enumerate.
- Severity **is** scoped to what the surface does, and the reasoning behind it
  (L-70) is the single best thing in this rung.
- The control is live, the vacuity assertion is wired into the test, the homonym
  exclusions are senses and not surfaces, and the amendment to the gate's range is
  accurate, complete and self-declaring.
- Twice the author published a finding **against its own interest** — the
  retracted wrap justification, and the over-broad exclusion that ate a correct
  sentence. Both are in the record because it put them there, not because I found
  them.

**The exceptions**, in the order I would fix them:

1. **The declared blind-spot list omits the guard's dominant blind spot.** The
   frame line and BASIS say nothing about placements phrased outside the two
   patterns — an admission the sibling guard makes — nor about board positions
   past fifth. §5. This is the one that makes the green read as more than it is.
2. **A live, committed placement claim in an unreachable phrasing**, wrapped
   across a line break, on the LaTeX source of a shipping report, in the same
   sentence family as defect A. Correct by luck. §1.
3. **Three stated numbers do not reconcile**: 22 new tests and 21 failures, not
   21 and 20; 493 repo-wide expressions at the committed state, not 497; and the
   111/421/63 corpus is not reproducible from any recorded selection rule. §2.3,
   §2.4.
4. **A superseded justification still standing on two travelling surfaces** — the
   shipped code comment and the ladder rung definition both say a line-bounded
   reader is defeated by the real parent instance, which the author's own later
   finding shows it is not. §2.2.
5. **Board-parse robustness**: the ordinal vocabulary is a 1–5 constant not
   derived from the parsed board; a second numbered table in the README silently
   corrupts ranks; a shared first-author surname silently drops an entrant and
   then faults correct prose; an unbalanced regex metacharacter in a surname
   crashes the whole audit instead of reporting OFF. §2.1.
6. **The travelling set is matched by basename**, so 65 non-package files inherit
   the FAIL severity. Conservative direction, still a name collision doing a
   provenance check's job. §2.6.

None of the six falsifies a claim the rung makes. Four of them are the rung's own
stated numbers and stated reach failing to keep up with what its author already
knew. That is the shape of PASS WITH EXCEPTIONS rather than FAIL: **the instrument
is sound and its label overstates it.**

**Not required for the grade, but stated so it is not discovered later:** the
corpus cannot distinguish this guard's parsed board from a transcribed one (§3),
so no future report should cite the corpus as evidence for claim 1. Cite the
permutation test. It is the only evidence there is, and it is sufficient.

---

## 7. What I found that I was not looking for

- **§1's sentence.** I went looking for whether my invented phrasings were fair
  and found one of them already committed, in the same sentence family as the
  defect that opened the rung, on a report source. Not in scope for any claim
  above; it is the most important thing in this document.
- **The rival-rule result runs one way only.** There is no file in this
  repository where the shipped guard fires and a two-substring literal does not.
  The corpus evidences precision over a dumb rule and recall over nothing.
- **The guard's own comment block is the cleanest live demonstration of rule A's
  adjudication clause**, and it is not cited as one. `self_audit.py` quotes the
  defect and states the true rank nearby, and passes. That is a better use/mention
  argument than any of the prose about it.
- **`test_the_three_surfaces_fixed_on_2026_08_11_stay_fixed` silently `continue`s
  on a missing file** and only `skipTest`s on a missing clone. On a checkout
  without the website tree it reports a pass having asserted nothing about any of
  the three files. Not a defect in the guard; a soft spot in the one test that
  pins the actual regression.
- **The two remaining live faults are in `docs/INSTRUMENT_INTEGRITY_LEDGER.md`**,
  which another agent owns and which I was instructed to stay out of. They are
  correct behaviour, correctly scoped to WARN, and I have not touched them. Anyone
  reading a WARN from this check today should know that is what it is.

---

*Graded independently. No agent verifies work it produced; this grader produced
none of V16, and produced no fix for anything named above.*
