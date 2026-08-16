# Ladder V — R-VALUE re-grade of the eight silent rounds

**Verdict: NO rung closes. R-VALUE stays at ZERO, and it now stands on a second and
independent leg. Every one of the eight rounds that never used the words was graded on what
its findings DID, and every one of the eight returned at least one finding that changes what
a reader believes. The 49% → 71% move in V16 round 10 is ruled NOT belief-neutral, explicitly
and on stated ground.**

**Grader:** an agent that wrote no round document, no rung, no grade, and no earlier R-VALUE
probe on this ladder. Re-graded 2026-08-16 at repo HEAD `9cdb1851`. Read-only across the
repository except this file and one docket row. No solver ran, no scoring call was made, the
ledger stood at 6 at `9cdb1851`, and nothing was sent, uploaded or registered.

**The frame did not move under this grade, and that was checked rather than assumed.** HEAD
advanced from `9cdb1851` to `74caabcd` while it was written (four commits). `git diff --stat`
over every file any figure here was derived from — `scripts/self_audit.py`,
`sdk/scripts/probability_of_rank.py`, `demo-output/website/closure_challenge_round5_qcr.json`,
`LESSONS.md`, `V16_GRADE.md` and `V15_ROUND5_NUMBER_RECONCILIATION.md` — is **empty** across
that range, so every measurement below holds at `74caabcd` as well as at the commit it names.

**This is an R-CONVERGE grade and its outcome label is a plain PASS-shaped ruling on a
question, not a rung verdict.** It closes no rung and promotes none. The one finding it
produced outside V16's declared closing condition was FILED as a docket row, not appended to
a rung.

---

## 0. The question, and why a text sweep could not answer it

R-VALUE, as written in `LADDER_V_TRIPLE_VERIFICATION.md` §"THE CONVERGENCE RULE" at
`9cdb1851`:

> **R-VALUE.** Each grade round records what it found and what it cost. When **two consecutive
> rounds return only findings that would not change an external reader's belief**, the rung
> closes as **PASS WITH RESIDUALS**, and the residuals become docket items.

`ad5473e0` established, at recognition strength, that **no round ever ASSERTED** neutrality —
a 12-form control frozen and hashed before any pattern was written, 117 hits over 36 tracked
round/grade documents and every commit message, **ASSERT 0**. That measurement was not
disputed here and was not re-run.

**It answers a narrower question than the rule asks.** R-VALUE's condition is on what a
round's FINDINGS DO. A round whose findings were in fact neutral and which never used the
vocabulary satisfies the rule and is invisible to any declaration sweep, however good its
control. `docs/DOCKET.md` D292 (landed `ad5473e0`) routed exactly that residue to a
non-author. This document is that re-grade.

**The bar held throughout, stated before the first candidate was opened.** A round was
belief-neutral only if running it changed nothing anyone believed: no defect found, no figure
moved, no claim withdrawn, no verdict altered. **Finding nothing is not the same as finding
nothing that mattered.** A finding that is true but inconsequential had to be named and
argued; a figure anyone had published, moved, was decisive against neutrality. R-VALUE's word
is **"only"**, so a single belief-changing finding is fatal to a round.

### 0.1 What was graded, and from what

Eight rounds carry no neutrality language, in five places. Each was established from **its own
commits and artifacts**, never from a later summary of it — several summaries in this lab were
measured wrong this week, two of them the chief's.

| rung | round | the entire record | how it was read |
|---|---|---|---|
| V16 | 1 | `V16_GRADE.md` §§1–7 | document |
| V16 | 2 | `V16_GRADE.md` §8 | document |
| V16 | 3 | `V16_GRADE.md` §9 | document |
| V16 | 4 | `V16_GRADE.md` §10 | document |
| V16 | 8 | **commit `5e4a0cc5` only — no document** | the diff |
| V16 | 9 | **commit `067caac0` only — no document** | the diff |
| V16 | 10 | **commit `0c7b968d` only — no document** | the diff |
| V15 | 5 | `V15_ROUND5_NUMBER_RECONCILIATION.md`, `1b0433eb` | document |

### 0.2 The board, re-derived rather than quoted

Re-derived at `9cdb1851` by `ast.literal_eval` on the `LIVE_BOARD` assignment node in
`sdk/scripts/probability_of_rank.py` — parsed, never imported — joined to
`demo-output/website/closure_challenge_round5_qcr.json`
`official_test_harness_result.round5_per_case_full`. **Seven positions** counting our own row.
Per-case ranks in file order **2, 2, 1, 1, 3, 4, 4, 7 of 7**; **best on board 2 of 8**, and
both survivors are the two rows the decline gate passed through as the organisers' own
unmodified RANS field, so **0 of 8 is earned by our model**. Overall **rank 1 of 7** at
0.056647 against Yang's 0.058013, **margin 0.001365**; the 0.002419 truth-free seed bound is
**177%** of that margin. Nothing in this grade depends on any of it, and it was recomputed
because a grade that quotes the board has not checked the board.

---

## 1. THE HARD CASE — V16 round 10 and the 49% → 71% move

**RULING: NOT BELIEF-NEUTRAL.** This is the judgement the previous instrument declined
(D292's remedy column, `ad5473e0`), and it is decided here rather than routed again.

### 1.1 What round 10 actually did, from its diff

`0c7b968d`, subject `067caac0`, six files. It settled D49 by choosing **one** admission
predicate — `_placements` — for **both** precision rows, after round 9 measured them as
scored under two. The reason recorded in the diff was structural rather than preferential:
`board_placement_faults`, whose output **is** the numerator, was itself built on `_placements`,
so under the raw-match rule the numerator and the denominator came from two different
functions and thirteen sentences sat in a denominator they were structurally incapable of
entering.

**Re-derived at `9cdb1851`, not read**, by `ast.literal_eval` over the `_PLACE_PRECISION` and
`_PLACE_ADMISSION` assignment nodes in `scripts/self_audit.py`:

| row | builder | blind | set holds | scored | falsely faulted | rate |
|---|---|---|---|---|---|---|
| author's non-placement set | this check's author | no | 41 | **28** | 20 | **71.4%** |
| grader's non-placement set | independent grader | yes | 43 | **25** | 19 | **76.0%** |

and the sensitivity table the round installed in place of the struck absolute:

| admission rule | author | grader | spread | Fisher two-sided |
|---|---|---|---|---|
| `_placements` everywhere — **in use at `9cdb1851`** | 20/28 = 71.4% | 19/25 = 76.0% | **4.6 pts** | **p = 0.763** |
| raw rule-A match everywhere | 20/41 = 48.8% | 19/26 = 73.1% | 24.3 pts | p = 0.075 |
| the pairing published until `0c7b968d` | 20/41 = 48.8% | 19/25 = 76.0% | 27.2 pts | **p = 0.040** |

All three p-values were recomputed here from the counts by an exact hypergeometric two-sided
test written for this grade, and all three reproduce D49's figures to the digit. **The move is
20 of 41 (48.78%) → 20 of 28 (71.43%) = 22.65 points**, numerator unmoved at 20.

### 1.2 The ruling, and its six grounds

**1. A published figure moved 22.65 points.** R-VALUE's plainest disqualifier. The figure was
published in the guard's generated verdict and in `LADDER_V_TRIPLE_VERIFICATION.md`, where
`0c7b968d` struck the old sentence and wrote the new one in place.

**2. It is the rung's CLOSING figure.** V16's declared closing condition is that the guard
**state what it costs**. This figure is that cost. A 22-point move in the number a rung closes
on is the most belief-relevant thing a grade round of that rung can produce; if this is
neutral, nothing is.

**3. It moved in the direction that rules out the easy dismissal.** A reader who believed the
guard falsely faults roughly half the hard sentences it examines was left believing it falsely
faults **roughly seven in ten**. Those are different beliefs about the same instrument, and
the instrument is the one that gates every rank claim this lab publishes at FAIL severity on
a travelling surface.

**4. It was not the only belief-changing thing the round returned, and "only" is R-VALUE's
word.** Round 10 also (a) struck an absolute sitting in the reader-facing generated verdict —
*"the two here differ in that variable and in nothing else"* — the rung's **fifth** withdrawn
absolute; (b) replaced the headline 27-point builder spread with a **5-point** spread and a
declaration that the builder effect is **confounded** with the admission rule across a 5-to-24
point range; and (c) put both denominators and both set sizes in front of a reader for the
first time, the grader's 43 having sat beside its 25 nowhere for three rounds.

**5. THE COUNTER-ARGUMENT, STATED AT ITS STRONGEST AND REJECTED.** The best case for
neutrality is that **the numerator did not move**: 20 falsely faulted sentences before, 20
after, all thirteen dropped sentences true negatives, and the guard's behaviour byte-identical
across the round. On that reading round 10 relabelled a denominator and no fact about the
world changed.

It fails because **R-VALUE asks what a READER would believe, not what the CODE would do.** A
published rate is a claim, not a behaviour, and changing the denominator of a published rate
changes the claim even when it changes no behaviour — which is precisely why the round was
worth running. The round's own record argues this against itself: it recorded the choice as
**"the less flattering"** one and named the row it worsens as the author's own. A round cannot
coherently claim its choice cost it something and also be neutral about the cost.

**6. And a round is not neutral because its own commit message lists what it did not touch.**
`0c7b968d` enumerates unchanged recall figures, an unchanged class enumeration and unchanged
per-class counts. That is a correct scope statement and it is not a neutrality claim. The
things it left alone are not evidence about the things it moved.

### 1.3 The circulating claim — corrected, and its premise measured

*"Round 10 was neutral"* has circulated twice: `LADDER_V_V16_ROUND11.md:712` and
`LADDER_V_V15_ROUND8.md:619`. Both were read in full context here. **Both are warnings against
declaring neutrality early, not findings** — each is the second clause of a sentence beginning
*"Do not score neutrality early"* / *"Do not score the next round neutral early"*. The chief's
correction at `LADDER_V_TRIPLE_VERIFICATION.md` is upheld, and measured rather than agreed
with.

**Measured with `scripts/use_mention_discriminator.py` (`79e52dfa`), claim span passed
explicitly as its API requires:**

| site | claim span | verdict |
|---|---|---|
| `LADDER_V_V16_ROUND11.md:712` | `Round 10 was scored neutral` | **CANNOT_TELL** — no evidence either way |
| `LADDER_V_V15_ROUND8.md:619` | `Round 10 of V16 was scored neutral` | **CANNOT_TELL** — no evidence either way |
| the chief's quotation of it | `round 10 was neutral` | **MENTION** — positional: the claim itself is enclosed in quotation marks |

**None is ASSERT, and CANNOT_TELL is never ASSERT.** One operator note worth carrying: passing
the span *including* the surrounding quotation marks returns CANNOT_TELL for the third row
too, because the claim is then not *inside* the quotes. The span must be the claim, not the
claim plus its delimiters.

**AND THE WARNINGS' OWN FACTUAL CLAUSE HAS NO SOURCE — a new finding.** Both state as fact
that round 10 *was scored* neutral by someone. A sweep was built for the third-person
question — does any record say **of** a round, by number, that it was neutral, found nothing,
or returned nothing that moves a reader — over **2,120 units**: every tracked ladder, grade,
docket, lessons and product document at HEAD by `git ls-files`, read from `git show HEAD:`
blobs rather than a possibly-dirty worktree, plus every commit message from `git log --all`.

**The control was RECOGNITION, not reachability**, and was classified as such by
`scripts/control_kind.py`, which derives the kind from the evidence and refuses a caller's
label: **six mutually independent paraphrases** in the vocabulary a lab record would use,
frozen and hashed (sha256 `c824349024858f2adbc88b48cde0a7d0add0909b3531dee9db8259a5294abb7e`)
before the sweep was pointed at the corpus, planted **by line index** into the real bytes of
`LADDER_V_V16_ROUND11.md` at HEAD and read back through the sweep's own reader — **6 of 6
found** — with **two negative forms correctly rejected**, one of them a NOT-neutral
declaration and one an unrelated sense of *neutral*. No form is a substring of another, which
is the is/was case the module exists for.

**Result: 6 NEGATED, 2 provisional SCORED_NEUTRAL, 1 WARNING_NOT_A_SCORE, 2 MENTION.** The
sweep is **not a zero**, and it is reported as what it is: `control_kind.verdict_for(2)`
returned `NOT_A_ZERO`, so no zero-strength claim is made from it. Both provisional hits were
adjudicated by hand and are false positives of my classifier — one is the chief's quotation of
the claim *in order to refute it*, one is a commit subject about ledger bookkeeping. **No
record anywhere scores round 10, or any round, neutral.** The warnings' advice was sound; the
factual clause they carried was not, and it is what the chief inherited and repeated.

---

## 2. V16 ROUND 9 — the round whose entire tracked footprint is one docket row

**RULING: NOT BELIEF-NEUTRAL**, and of the three silent V16 rounds this is the one whose
neutrality was most plausible before it was read, because `067caac0` changed exactly **one
line of one file**.

The line is docket row **D49**, and it is read here rather than summarised. What round 9
established, executed at `be36e22f`:

- The generated verdict — the surface an outside reader meets — **asserted** *"the two here
  differ in that variable and in nothing else"* and *"the same admission rule applies to
  both"*. **Two different predicates implemented that one rule.** The absolute is false, and
  it is the rung's fifth.
- The author's 41 drop to **28** under the grader's predicate, losing thirteen sentences the
  guard examines and correctly clears — 8 `linalg-head-listed`, 1 `coordination`, 4 `homonym`
  — all true negatives, numerator unmoved at 20. The grader's 26 raw matches drop to 25.
- **The published pairing is the only one of four combinations that is not internally
  consistent, it is the one that maximises the gap, and it is the one that produced the
  p = 0.040 a chief ruling at `02e941c4` cited.** Recomputed independently here (§1.1): the
  consistent alternatives give 4.6 points at p = 0.763 and 24.3 points at p = 0.075.

**A round that shows a published significance figure to be an artefact of the pairing that
produced it has changed belief**, and it did so about a number a ruling had already been
built on. One docket row is a small footprint and a large finding; the footprint is not the
measure.

---

## 3. V16 ROUND 8 — `5e4a0cc5`

**RULING: NOT BELIEF-NEUTRAL.** Four things, read from the diff across
`V16_PRECISION_SET.py`, `scripts/self_audit.py` and `sdk/tests/test_rank_claim_surfaces.py`:

1. **An absolute was withdrawn.** *"So the figure is a WORST CASE on hard sentences, not a
   rate over the corpus"* was struck in both places it stood, quoted beside its falsification
   rather than deleted (L-76), and added to `_FALSIFIED` so reinstating it reddens the suite.
   It was the rung's **fourth** withdrawn absolute, and it had failed in the **optimistic**
   direction — the one the rung exists to stop being wrong in.
2. **`_PLACE_PRECISION` became a two-row table** publishing a **27-point disagreement**
   between the author's row and an independent grader's, each naming its builder and its
   blindness. One row measured by the party being measured had been a self-report, not a cost.
3. **Two false-FAULT shapes that were counted nowhere and named nowhere became counted and
   named** — `other-named-board` (the guard reads *whether* an ordinal is claimed and never
   *which* board it is claimed on) and `negated-or-questioned` (rule A tests neither polarity
   nor mood), **2 of 2 admitted sentences faulting apiece**, added as BLIND TO items 10 and 11.
   Filed as **D46**.
4. **The test guarding the figure stopped being scored by its own author.**
   `test_every_false_fault_class_is_counted_and_named` had computed both sides over the
   author's own set, so a test whose whole subject is *"every class is counted and named"*
   could only ever see classes the author had already thought of. Filed as **D47**, and the
   two classes in (3) exist because the re-binding found them.

Two previously invisible failure shapes on a guard whose rule-A fault is FAIL severity on a
travelling surface, plus a withdrawn absolute, is not a neutral round under any reading.

---

## 4. V16 ROUNDS 1–4 — `V16_GRADE.md`

These four are the ladder's **only other run of consecutive silent rounds**, and therefore the
other place a closure could have hidden. Each was read from its own section, and each returned
findings the round itself labelled exceptions.

**Round 1 (§§1–7). NOT NEUTRAL.** It found, unlooked-for, a placement pinned on a named board
entrant, **wrapped across a line break**, in `demo-output/website/latex/closure_challenge_report.tex`
— the exact failure mode the rung was opened for, on the LaTeX source of a compiled report,
and **completely invisible to the new guard** because `ranked second` was not in its pattern
set. The document records that the sentence happens to be true, and that this is luck rather
than the guard's doing. Six exceptions beside it.

**Round 2 (§8). NOT NEUTRAL.** Five of six exceptions closed, two new ones opened, and E4 is
decisive on its own: the published recall figure is **one sample's**. A blind set built by a
different agent measured **53%** missed against the author's **30%**, and the frame quoted the
*outside* measurement of the superseded version beside the *inside* measurement of the shipped
one, so a published improvement reading **11% → 70%** is **11% → 47%** measured on one set
held constant. A published improvement figure cut by a third changes belief.

**Round 3 (§9). NOT NEUTRAL.** Both commissioned exceptions closed and **two new ones arrived,
neither of them what the round was sent to check** — `_published_board` documented as *"NEVER
raises"* and raising, a non-UTF-8 README taking down the entire `self_audit` run through an
uncaught `UnicodeDecodeError`; and the reach table stale against its own generator.

**Round 4 (§10). NOT NEUTRAL.** Three findings, the smallest set of the four and still not
zero: **a defect in the guard's own logic returns PASS** — a per-surface `except Exception`
drops the documents it cannot read and reports *"all 0 placement expression(s) agree with the
published board"* while the status stays green; **a false statement about the corpus was
holding a homonym exclusion open** — linear-algebra `rank` **is** written as a digit here,
twice, verified, and three sentences of plausible lab prose produce false positives; and one
published figure still had no committed inputs, under a comment saying it could not happen
again.

**Four consecutive rounds, four non-neutral verdicts. No pair exists in this block.**

---

## 5. V15 ROUND 5 — `V15_ROUND5_NUMBER_RECONCILIATION.md`, `1b0433eb`

**RULING: NOT BELIEF-NEUTRAL**, and the argument for the other verdict is stated first because
it is the second-best one in this grade.

**What it did.** A read-only cross-surface reconciliation at `038b36da` over a stated frame —
20,559 tracked paths, 18,833 read as UTF-8 under 4 MB, matched whole-file with whitespace
collapsed, explicitly **not** with the shell `grep` because that is `ugrep --ignore-files` and
this repo tracks 6,938 gitignored paths. It returned **nine owned change-items**, of which:

- **the rung's own headline was wrong on the rung's own page** —
  `LADDER_V_TRIPLE_VERIFICATION.md:300–302` publishing 53% and 96% where the generator
  recomputed 44% and 93%;
- **four further copies in `docs/PRODUCT_LIST.md`**, one of them asserting *"is now"*, and one
  inside a sentence generated from a provenance table and therefore believed unable to drift;
- a **withdrawn** 89→30 pairing surviving as a live restatement in one place;
- *"All hold. No fourth absolute."* **overturned by the entry immediately following it**, with
  no marker at the point of claim;
- and the mechanism: **the correction propagated backwards.** `_PLACE_REACH` was corrected at
  `db096bb7` (06:56) and the prose at `9f6d8a41` (06:04), so the prose was right when written
  and the code moved under it. *"This is not a copy-paste failure; it is that the copies had
  no way to learn."*

Two of the nine were defects in the round author's own documents and were routed away from
them.

**THE ARGUMENT FOR NEUTRALITY, and it is the round's own words.** The document states
**"Nothing that travels is affected"** — the submission package, `closure.html`, the
credentials wall, `benchmarks.html` and the `.tex`/PDF pair carried no stale reach figure, and
every item is a lab record or a code comment. If *"external reader"* means a reader outside
this lab, nobody outside saw anything move.

**REJECTED, on three grounds.**

**(a) The reading is self-defeating.** R-VALUE's *"external reader"* means a reader external to
the round — anyone who did not run it — not a reader external to the lab. On the narrow
reading almost every finding in this ladder's entire history lands on a lab record, and
R-VALUE would have closed every rung at round two. **A rule that ends a gate must not be read
so that the gate closes on its own first pair.** The ladder's own practice confirms the wide
reading: V16 round 11 self-declared NOT belief-neutral on findings that were **all** lab
records, and V16 round 12 (D264) measured the guard's live cost as 48 lab records and called
itself not neutral on them.

**(b) It fails even on the narrow reading.** *"The rung's own headline is wrong on the rung's
own page"* is the round's own severity text for item 1, and `LADDER_V_TRIPLE_VERIFICATION.md`
is the rung's claim-bearing surface. Two figures on it moved, 53%→44% and 96%→93%.

**(c) A round that finds a defect in its own author's record has found something.** Items 5
and 6 were exactly that, and were routed to a third party for that reason.

### 5.1 Consecutiveness — V15 round 5 has no candidate neighbour

V15's grade rounds are 1, 2, 4, 5, 6, 7, 8, 9. **Round 3 is a FIX round, not a grade round** —
round 4's title is *"is round 3's output clean?"* — so it is outside R-VALUE, which speaks of
grade rounds. Round 5's neighbours are therefore grade rounds 4 and 6:

- **Round 4** (`LADDER_V_V15_ROUND4.md`) found **seven new failures in round 3's own output**,
  measured at `d7d51974`, against a termination rule demanding zero.
- **Round 6** (`LADDER_V_V15_ROUND6.md`) opens *"The verdict the termination rule asks for is
  a number, and it is not zero."*

So even had round 5 been neutral, **no consecutive pair existed on V15.**

---

## 6. THE OUTCOME

### 6.1 No rung closes

| rung | run of consecutive silent rounds | verdicts | pair? |
|---|---|---|---|
| V16 | 1, 2, 3, 4 | NOT / NOT / NOT / NOT | **no** |
| V16 | 8, 9, 10 | NOT / NOT / NOT | **no** |
| V15 | 5 (isolated) | NOT | **no** — and both neighbours found failures |

Those two V16 blocks are the ladder's **only** runs of consecutive rounds that could have been
neutral without saying so; every other round in V15 and V16 self-declares NOT neutral, and a
round that declares itself not neutral while returning findings is not a candidate.

**R-VALUE stays at ZERO, and the bound is now two-legged:**

1. **No round ever ASSERTED belief-neutrality** — `ad5473e0`, at recognition strength, over
   declarations.
2. **No silent round WAS belief-neutral** — this document, graded on findings rather than
   text, at every one of the eight rounds individually rather than only at the pairing.

Leg 2 does not depend on leg 1, and neither is a text search for a token. What remains outside
both is only this: a grading judgement is a judgement, and §1.2 and §5 state the grounds so
they can be attacked rather than merely disagreed with.

### 6.2 Falsifiers, named so this grade can be overturned cheaply

- **§1 falls** if a reader shows that a 22.65-point move in a rung's own published closing
  figure leaves an external reader's belief unchanged. The ground to attack is §1.2 item 5 —
  the numerator did not move.
- **§5 falls** if the chief rules that R-VALUE's *"external reader"* means a reader outside
  the lab. That ruling would also make V16 rounds 11 and 12 neutral against their own
  self-declarations, and is therefore larger than this rung.
- **§4 falls** if any two adjacent of V16 rounds 1–4 are shown to have returned only
  inconsequential findings; §2/§3 likewise for 8–10.
- **The whole grade falls** if a ninth silent round exists that this enumeration missed. The
  enumeration is §0.1 and its route is stated there.

### 6.3 What this grade did NOT establish

It graded eight rounds. It did **not** re-grade the rounds that self-declare NOT neutral,
because a round asserting a verdict against itself, with findings on the page, needs no
grader to agree. It makes no ruling on any rung's terminal state, on `PASS WITH RESIDUALS`
entitlement (D227), or on V16's closure — round 13 at `b6974959` established that V16's
central clause was satisfied or void and that the rung was blocked by one typed figure, and
nothing here touches that.

---

## 7. FILED, NOT APPENDED — one finding outside V16's declared scope

Found while grading §1 and §2, and **filed as a docket row rather than appended to a rung**,
per R-CONVERGE:

**`LESSONS.md` L-82 carries three statements that V16 rounds 9 and 10 falsified, in the present
tense, with no supersession marker** — measured at `9cdb1851`:

1. *"the guard **falsely faults 20 of 41 (49%)**"*. At `9cdb1851` `_PLACE_PRECISION` publishes
   **20 of 28 (71.4%)** for that row, re-derived here by `ast.literal_eval`. Restated a second
   time in the same lesson as *"The author's 49% is not a property of the guard."*
2. *"measured **19 of 25 (76%)** under the author's own admission rule, **unchanged**"*. The
   `unchanged` clause is exactly what D49 falsified and what `0c7b968d` struck-and-kept inside
   `V16_PRECISION_SET.py`: the grader's set admitted on `_placements` and the author's on a raw
   match.
3. *"Fisher exact two-sided **p = 0.040**"*. Recomputed here: that value belongs to the one
   pairing of four that is not internally consistent. Under the rule in use at `9cdb1851` the
   figure is **p = 0.763**.

**Why it is not merely stale.** L-82's rule — *any figure a lab publishes about its own cost
carries the provenance of the sample it was measured on* — is derived from the 27-point spread,
and that spread is 4.6 points under the rule the lab now uses. The lesson's conclusion survives
on other grounds; the numbers under it do not. **This is L-82's own lesson happening to L-82,
and it is the shape V15 round 5 filed nine times: the correction landed on the code and the
copies had no way to learn.**

`LESSONS.md` is not V16's subject and not inside any rung's declared closing condition, so it
is filed. Docket row **D297**, landed `74caabcd`. This grade itself is docket row **D296**,
landed in the same commit; neither row closes, promotes or re-opens a rung.

**Its disposition is docket row `D301`, landed `b327c8ce`, and the call is made there rather
than left to the owner: RESTATE — not struck, not withdrawn.** Not withdrawn because L-82's
conclusion is not falsified (the grader's rate exceeds the author's under **both** rules in
`_PLACE_ADMISSION`, 71.4% vs 76.0% and 48.8% vs 73.1%, which is what keeps the *"worst case"*
strike standing). Not struck because L-76 strikes what execution has **falsified**, and these
three are **superseded** — the distinction D58 drew for an unsourced date. **And the
restatement owes more than three digits:** L-82's rule names one variable, the provenance of
the sample; D49 established a second of comparable size that the lesson never names, the
**admission predicate**, confounded with the first and worth 5-to-24 points on its own. So
L-82's promise that the distrust is *"quantifiable for the price of one more sample"* is
incomplete as written — **L-82's own worked example is the counter-example to L-82's own
remedy.**

---

## 8. THE RULING §5 ASKED FOR, AND WHAT EXECUTION DID TO IT

§6.2 named the chief's ruling on *"external reader"* as the one call that could overturn §5.
It was made and recorded in `LADDER_V_TRIPLE_VERIFICATION.md` at `678cb7e8`: **"external
reader" means external to the ROUND, not external to the LAB**, which upholds §5 and decides
against V15 round 5's *"Nothing that travels is affected"*.

**The ruling's three grounds were tested by execution rather than accepted, and one of them
did not survive as worded.** The travelling-name set was **derived**, not listed, by the same
two derivations `self_audit._travelling_names` uses — shipping archive members plus the
submission package directories — **reimplemented rather than imported**, so a stale
`__pycache__` could not invert the result: **111 names**, 0 unopened archives, controlled in
both directions (`DESCRIPTION_DOCUMENT.md` travels: **True**; `LESSONS.md` travels:
**False**). Every V15 and V16 grade round was then marked narrow-neutral if its own record —
document, or commit message where the commit **is** the record — names no travelling file at
all.

| rung | rounds that name no travelling surface | consecutive pairs under the NARROW reading |
|---|---|---|
| **V16** | 5, 6, 7, 8, 9, 10, 13 | **(5,6) (6,7) (7,8) (8,9) (9,10)** — five |
| **V15** | none | **none** |

**GROUND 1's CONCLUSION IS CONFIRMED AND ITS WORDING IS REFUTED.** The ruling said R-VALUE
*"would have closed every rung at round two"*. Measured: **V16 would have closed at rounds 5
and 6**, and four more times after that — worse than "round two", because it fires repeatedly
on a rung that took thirteen rounds. But **V15 returns zero pairs**, so *"every rung"* is
false as written. The self-defeat is real and its scope is V16.

**THE INSTRUMENT IS SOUND IN ONE DIRECTION ONLY, AND THAT IS WHY THE REFUTATION IS PARTIAL
RATHER THAN TOTAL.** A round whose record never *names* a travelling file cannot have a
finding on one, so every NARROW-NEUTRAL verdict is established; a round that cites one may
merely be listing its frame, so *"cites travelling"* is **INDETERMINATE**, not *"has a
travelling finding"*. **V15 is therefore undetermined by this instrument, not shown safe under
the narrow reading.** The test was also deliberately biased **against** ground 1 — every path
a document cites was treated as a finding site, which over-counts travelling surfaces — so
the five V16 pairs survive an instrument built to suppress them.

**GROUND 2 SURVIVED INTACT, after two false positives were resolved by hand.** Basename
matching flagged round 11 and round 12 as citing travelling surfaces. Both were read:

- Round 11's `README.md` is `$CLOSURE_BENCHMARK_DIR/README.md`, i.e.
  `/home/ubuntu/closure-challenge-benchmark/README.md` — the benchmark clone the board is
  parsed from, **not a lab claim surface**. (`LADDER_V_V16_ROUND11.md:789–791`.)
- Round 12's `dist/…/closure.html:341` sits inside the section headed *"Found while grading
  V16, **outside its declared scope**, filed as docket rows and excluded from the rung's
  verdict and from the new-material count"*, and its other two hits sit in a *"nothing was
  written to"* list. **Round 12's five material findings are lab records without exception.**

So both rounds self-declared NOT belief-neutral on findings that were entirely lab records,
exactly as ground 2 states. **This is the ladder's own practice contradicting the narrow
reading, and it is now measured rather than recalled.**

**GROUND 3 needs no measurement and got one anyway on its single factual premise:** V15's
subject **is** the lab's own verification records — round 1 is titled *"the ladder's own text
re-enters the claims table"*. Under the narrow reading, rotting a verification record would be
belief-neutral, which makes V15 unfalsifiable. A rule cannot exempt the thing it exists to
check.

**A LIMITATION OF THE GUARD, NOT ONLY OF THIS TEST, MET WHILE RUNNING IT.**
`_travelling_names()` classifies by **basename**, so the submission package's `README.md`
makes *every* `README.md` in every citation look travelling — including the benchmark clone's,
which is the one file in this lab that must never be read as a lab claim surface. That is why
ground 2 needed two hand resolutions. It is noted here and **not filed**, because it is a
property of a peer-held instrument that this grade did not measure at scale and would be
re-finding rather than finding.

---

*Graded 2026-08-16 at `9cdb1851` by a non-author. Every figure in §0.2 and §1.1 was re-derived
by parsing an assignment node, never by importing a module and never by quoting a brief, a
docket row or a commit message. The recognition control in §1.3 was frozen and hashed before
the corpus was swept and classified by `scripts/control_kind.py`, which refuses to promote a
reachability control; its sweep returned two hits and is reported as `NOT_A_ZERO` rather than
as a certified absence. No rung was closed, no rung was promoted, no guard was tuned, no
solver ran, no scoring call was made, the ledger stood at 6, and nothing was sent, uploaded or
registered.*
