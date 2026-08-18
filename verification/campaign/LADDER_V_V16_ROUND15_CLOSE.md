# Ladder V — V16, ROUND 15: THE CLOSING ROUND, by a NON-AUTHOR of every prior V16 round

**Verdict: V16 PASSES.**

**THE GUARD'S MEASURED FALSE-POSITIVE RATES ARE `20 of 28 (71%)` AND
`19 of 25 (76%)`, AND THIS PASS IS A PASS ON DISCLOSING THEM, NOT ON BEATING
THEM.** No threshold was ever pre-registered for this rung. Wherever this
verdict is recorded or cited, those two figures travel with it; a pass on
disclosure that hid the disclosed number would be the exact defect V16 exists
to prevent.

**This round was NOT belief-neutral.** R-VALUE's consecutive-neutral count stays
at **ZERO**.

---

## 0. FRAME, INDEPENDENCE, AND WHAT MOVED UNDER THIS ROUND

| field | value |
|---|---|
| measurement frame, pinned in argv for every cell | `04b9cc37` (round 14's own commit) |
| HEAD at write-up | `8c01202f`. `04b9cc37` confirmed an ancestor by `git merge-base --is-ancestor` |
| the graded artifact across that move | `scripts/self_audit.py` **byte-identical at `04b9cc37` and at `8c01202f`**, and byte-identical in the worktree, all three by content comparison. Every measurement below therefore stands at HEAD without re-running |
| subject records | round 14 `04b9cc37` (D314–D316), round 13 `b6974959`, the D308 repair `29ad0364`; rulings `bcad2bbc`, `04489465` — all confirmed ancestors before any cell |
| R-ISOLATE | **SATISFIED.** This agent authored no V16 round, no part of `scripts/self_audit.py`, no part of the D308 repair, and no part of the ledger row it repairs |
| `git status` | **read stale again**, exactly as the lab's own note predicts: it reported `LADDER_V_TRIPLE_VERIFICATION.md` as `MM` while a byte comparison of the worktree against `git show HEAD:` returned **identical**. The status was discarded; content comparison governed |

**Method.** `__pycache__` purged before every cell. Board re-derived by
`ast.literal_eval` on the `LIVE_BOARD` **assignment node** in
`sdk/scripts/probability_of_rank.py` — parsed, **never imported**. Plants by
line index, read back by slicing at that index. No figure below is quoted from
round 13, round 14, or the dispatch brief.

---

## 1. THE CRITERION'S PRECISION CLAUSE, QUOTED IN FULL

Read at `LADDER_V_TRIPLE_VERIFICATION.md:535–539`, section **V16 (A16)**, and
quoted **whole** — round 13 truncated in front of the counter-argument and
round 14 named that omission material. The emphasis is the criterion's own:

> **Precision is a requirement of this rung, not a nicety** — a guard that cries
> wolf gets switched off, and then it guards nothing — so the rung fails if the
> check does not state its false-positive rate against a measured corpus and
> name the senses of the word it excludes.

### 1.1 The counter-argument, stated at its strongest

**A rung whose criterion opens by declaring precision "a requirement of this
rung, not a nicety" cannot be satisfied by a guard that falsely faults roughly
three sentences in four.** On the disclosure reading the emphasised half does no
work whatever: a check stating *"my false-positive rate is 100%"* would pass, and
a criterion's own emphasis is not ordinarily decorative. Worse, the rationale
names a concrete harm — a guard that cries wolf gets switched off, and then it
guards nothing — and a guard at 71% and 76% **is** a guard that cries wolf. So
the disclosure reading passes the rung by defeating the purpose the rung states
for itself.

That is the argument. It is not weak, and it is why this section exists.

### 1.2 It is answered, on four grounds, and only the first is grammatical

**(i) The connector is "so", and the criterion marks rationale the same way
twice.** "P — R — **so** Q" makes Q the consequence and P the reason for it, and
only Q types a predicate that can be false: `the rung fails if the check **does
not state** its false-positive rate … and **name** the senses`. No threshold, no
ceiling, no comparator appears anywhere in the clause. This is not a reading
chosen to suit the measurement: **C5, the sibling clause added to the same
criterion by the same grade, is built identically** — *"the check must **declare**
what its patterns cannot phrase, measured on held-out sentences rather than
asserted, **because** a replacement whose stated reach is less honest than its
predecessor's is the failure V16 exists to fix."* Rationale on `because`,
operative condition a declaration. **Both of V16's performance-flavoured clauses
are, in their operative half, disclosure requirements, and V16's face marks the
rationale with a connective in both.** The grammar argument is structural to the
criterion, not convenient to the verdict.

**(ii) No threshold was ever pre-registered, and reading one in now is the
tuning V16 forbids.** C4 contains no number. Any bar — 50%, 20%, 5% — would be
chosen *after* 71% and 76% were on the table, which is choosing the pass
condition knowing the measurement. The rung's own history contains the matching
ruling in the other direction: widening `_RANK_WINDOW` fivefold so a control
would pass was refused **on the ground that it changes what counts as
evidence**. Inventing a bar at grading time changes what counts as passing. It
is the same move, and V16 is the rung that exists to refuse it.

**(iii) The rationale's harm is INVISIBILITY, and its remedy is therefore
publication.** Read what the rationale actually fears: not that the guard is
wrong, but that being wrong it *gets switched off, and then it guards nothing* —
a cost paid quietly by whoever disables it. The remedy for a quiet cost is a
loud one. Measured from `_place_precision_sentence()` at `04b9cc37` rather than
asserted: the check states **two** rates from **two independently built** sets,
names each set's builder and whether they were blind, names the corpus **3**
times and both source files, enumerates **ten** accepted false-positive shapes
with per-sample counts, and closes by saying **both sets are adversarial and not
representative, so neither is a corpus rate**. Nobody switches this guard off by
accident. Disclosure serves the rationale; a bar would not have.

**(iv) The decisive ground, and it comes from the counter-argument's own
premise.** If C4 were a performance requirement, **the cheapest way to pass V16
would be to shrink the denominator** — narrow which sentences the guard is
counted over until the rate falls. That is not hypothetical here; the check
measures it against itself and says so in terms:

> *"the ADMISSION RULE -- which sentences count toward a denominator at all --
> moves the spread between these two rows across a 5-to-24 point range … it
> drops 13 sentences the discriminator correctly clears out of the author's own
> denominator, all of them true negatives, moving this check's author's row from
> **49% to 71%** while leaving its numerator at 20."*

**A pass condition that the gradee can move by choosing an admission rule is not
a criterion.** The disclosure reading is invariant under exactly that move:
whatever admission rule is chosen, the rate must be stated *with* it, which is
what the check does. **The performance reading is the one that defeats V16's
purpose, and the disclosure reading is the one that protects it.**

### 1.3 What the ruling costs, recorded rather than buried

**The disclosure reading makes C4 satisfiable at any rate whatsoever, 100%
included.** That is a real defect **of the criterion as written**, and this round
does not pretend otherwise. The remedy is to amend V16's face to carry a
pre-registered bar for future grades — filed as a docket row, not read into the
text retroactively — because a criterion is amended forward and graded as
written. **RULING 1 STANDS: C4's operative condition is its disclosure clause.**

---

## 2. C4 AND C5 — RE-MEASURED AT `04b9cc37`

`_place_precision_sentence()` and `_place_reach_sentence()` called directly.

| clause | requirement | measured |
|---|---|---|
| C4 | **states** a false-positive rate | **`20 of 28 (71%)`** and **`19 of 25 (76%)`**, both verbatim, in a 5,733-character sentence |
| C4 | against a **measured corpus** | corpus named **3×** (`non-placement set`); both sets identified by builder, blindness, and source file (`campaign/V16_PRECISION_SET.py`, `campaign/V16_GRADE_ROUND7_PRECISION_SET.py`) |
| C4 | **names the senses it excludes** | verbatim — *"a **linear-algebra** subject whose head noun is not in `_PLACE_LINALG_NEAR` -- a kernel, a Gramian, a Laplacian, an array"*; all six tokens found |
| C5 | declares what its patterns cannot phrase | reach sentence, **1,610** characters |
| C5 | **measured on held-out sentences** | seven rate-shaped figures over three rule-A sets plus a rule-B row |
| C5 | measured **rather than asserted** | **4** `invented` clauses, each naming builder and blindness |

**Negative control:** a rate-shaped string that is not in the sentence
(`77 of 99 (78%)`) was searched for and **not** found, so the positives above are
not an artefact of a pattern that matches anything.

**C4 AND C5 SATISFIED.**

---

## 3. C1 — RULING 2 TESTED BY EXECUTION BEFORE BEING RECORDED

### 3.1 The board, re-derived by parse

```
LIVE_BOARD via ast.literal_eval on the assignment node -- module NOT imported
  published_overall  Yang .0580  Reissmann .0595  Wu .0624
                     Tian .0641  Liu .0737  Montoya .0779
  -> live ranks      yang 1, reissmann 2, wu 3, tian 4, liu 5, montoya 6

_published_board() -> {'reissmann': 1, 'wu': 2, 'liu': 3, 'montoya': 4}
frozen pin         -> deb91557184af3cb95f5190494ec52d8f2c6a0d1, dated 2026-05-04
'yang' on it False   'tian' on it False   ranks available [1, 2, 3, 4]
```

### 3.2 The extension experiment, driven exhaustively

Every rank the vocabulary admits was handed to `board_placement_faults`.
Controls: a wrong-vs-pin placement on Wu that must fault in **every**
configuration, and a nonsense-entrant placement that must stay silent in
**every** configuration.

| board handed to the guard | `rank-1 …, Yang` **TRUE of live** | `rank-6 …, Yang` **FALSE of live** | control (Wu, wrong) | negative | correct? |
|---|---|---|---|---|---|
| the pin as shipped | 0 | 0 | **1** | 0 | no — invisible both ways |
| + yang at **1**, his LIVE rank | **0** | **1** | **1** | 0 | **YES** |
| + yang at 2 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 3 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 4 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 5 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 6 (invented) | 1 ✗ | **0** ✗ | **1** | 0 | no — and it inverts |

**Exactly one value behaves correctly and it is the value that can only come
from the live board.** Round 14's table reproduces cell for cell under an
independently written harness. **The correct behaviour is uniquely determined by
the forbidden import.**

### 3.3 The third reading, re-run

The four entrants C1 indisputably covers, graded against the **live** board:

| sentence | true of live? | guard faults it? | correct? |
|---|---|---|---|
| `The rank-2 entry, Reissmann, Fang & Sandberg, …` | **yes** | **yes** | **no** |
| `The rank-1 entry, Reissmann, Fang & Sandberg, …` | no | no | **no** |
| `The rank-3 entry, Wu & Zhang, …` | **yes** | **yes** | **no** |
| `The rank-2 entry, Wu & Zhang, …` | no | no | **no** |
| `The rank-5 entry, Liu, Wang, Zhao & Xiao, …` | **yes** | **yes** | **no** |
| `The rank-3 entry, Liu, Wang, Zhao & Xiao, …` | no | no | **no** |
| `The rank-6 entry, Montoya, Oulghelou & Cinnella, …` | **yes** | **yes** | **no** |
| `The rank-4 entry, Montoya, Oulghelou & Cinnella, …` | no | no | **no** |

Negative control 0, recognition control 1. **Wrong in both directions for all
four**, 8 of 8.

### 3.4 THE RULING: C1 IS **VOID** UNDER `bcad2bbc`, AND VOID IS NOT SATISFIED

`bcad2bbc` verified at source: *"A criterion may not require more than the
maximum permitted action … so a per-sentence reading is void there rather than
strict."* `04489465` verified at source: *"It explicitly does NOT authorise
re-pointing the guard -- that trades a silent instrument for a loud wrong one."*

Of the three constructible readings, the widest and worst is §3.3's, and the
extension experiment shows the only configuration that behaves correctly is the
one the frozen pin forbids. **Where the only value that works is the forbidden
one, the criterion is void, not strict.** Ruling recorded: **C1 is VOID.**

**AND VOID DOES NOT MEAN SATISFIED.** C1 cannot block this rung, and **C1 may
not be cited as evidence that the guard is correct about entrant placements.**
On the live board the guard is wrong in both directions for every entrant C1
covers. That is recorded here so that the PASS cannot later be read as a finding
that the placement predicate works.

---

## 4. D308's DISCRIMINATING CELL, RE-RUN — AND THE FIGURE MOVED A FIFTH TIME

Rebuilt from scratch. **`scripts/self_audit.py` was never written to**: the
mutant was compiled from a string with `compile(src, "<the real path>", "exec")`
so `REPO = Path(__file__)…` resolved identically, and the file was asserted
byte-identical to HEAD by content comparison before and after every cell.
Plants went into a **seed file**, by line index, read back by slicing at that
index, restored from HEAD, and the restore verified by content comparison.
The control was asserted **GREEN first**, green defined as *the emitted figure
agreeing with a count classified independently by message shape* — never as
`returncode == 0`.

**RECOGNITION control, validated in isolation before anything was planted:** four
syntactically distinct placement forms, none a substring of another, **all four
fired**; a TRUE placement stayed silent; a nonsense-entrant placement stayed
silent. The plants are **semantic, not literal** — no string the guard searches
for was planted, only a wrong ordinal it had to recognise.

| cell | code | corpus | emitted rule-A | independently counted |
|---|---|---|---|---|
| **A** control | derived, as shipped | pristine | **61** | **61** |
| **B** | derived, as shipped | + 2 planted rule-A faults | **63** | **63** |
| **C** discriminating | **hardcoded literal `61`**, same digits | the **identical** 2 plants | **61** | **63** |

- **The derived figure tracked the mutation:** +2 emitted against +2 true.
- **The mutation killed the literal:** 0 emitted against +2 true. **The proof is
  not satisfied by a value that merely matches.**
- Rule-B stayed **15** in all three cells; the **struck negative control** planted
  alongside contributed nothing, so the delta was exactly the two live plants.

**THE FIGURE HAS NOW MOVED FIVE TIMES IN FOUR DAYS — 2 → 34 → 53 → 56 → 61 —
AND TWICE OF THOSE UNDER A GRADER SENT TO CHECK IT, WITH NOBODY EDITING THE
SENTENCE.** Round 14 derived **56** at `2daebd70`; this round derives **61** at
`04b9cc37`. **A literal would now be stale for the fifth time.** D308's central
argument — that this number must not be repaired with a number — is confirmed by
the number moving again under the grader who came to confirm it.

---

## 5. C2 AND C3

| clause | state at `04b9cc37` |
|---|---|
| C2 whole text, whitespace collapsed | **held** — implemented in `_place_flatten`/`_placements` and stated in the emitted frame |
| C3 guard + `test_rank_claim_surfaces.py` fire on the three founding defects | **held** — `test_rank_claim_surfaces.py`, `test_two_board_referents.py`, `test_fault_message_matches_rule.py`: **172 passed, 36 subtests passed, 0 failures**, 821s |

---

## 6. THE SCOPE RULING ON `test_two_board_referents.py`: **CONCLUSION SUSTAINED, GROUND OVERTURNED**

Round 14 ruled that module's stale docstring out of V16's scope on two legs.
This round was told to confirm or overturn, and did so by execution.

**LEG 1 IS REFUTED.** Round 14 rested on `scripts/self_audit.py:1749`,
`_VALUE_NOT_A_SURFACE = ("sdk/tests/",)` — *"a labelled test corpus is not a
claim surface"*. **That predicate belongs to a different check.** Measured from
source: neither `check_board_placement_words` nor `board_placement_faults`
references `_VALUE_NOT_A_SURFACE` at all, and **V16's own guard demonstrably does
sweep `sdk/tests/`** — of the 61 live rule-A faults at `04b9cc37`, **3 are on
`sdk/tests/test_two_board_referents.py` itself**. For V16's guard, `sdk/tests/`
**is** a claim surface. A predicate borrowed from a sibling check is not a
standing predicate for this one.

**LEG 2 STANDS, and it is sufficient on its own.** V16's criterion names
`sdk/tests/test_rank_claim_surfaces.py` and no other test module; measured, the
string `test_two_board_referents` does **not occur anywhere** in
`LADDER_V_TRIPLE_VERIFICATION.md`. No clause C1–C5 reaches that docstring.

**So the docstring is out of V16's scope because V16's criterion does not reach
it — not because a test file cannot carry a claim.** It remains a live stale
claim on a lab record, and it is filed, not repaired: a grader does not repair
what it grades.

---

## 7. THE INSTRUMENT CAUGHT ITSELF TWICE, AND BOTH ARE WORTH THE LINES

**(a) A missed variant, caught by the vocabulary control and not by inspection.**
The first sweep's needle `rule-A faults from 2 to 68` **cannot span an
intervening verb**, so it silently missed `rule-A faults **go** from 2 to 68` at
`scripts/self_audit.py:3777` — the is/was failure `control_kind.py` was written
about, reproduced live. The control returned **BROKEN** on that planted form and
the sweep was rebuilt before any figure from it was believed. Sites went
**9 → 13**.

**(b) Markdown emphasis is a third delimiter, and then its repair broke strike
classification.** `takes rule-A faults **from 2 to 68**` puts `**` between the
tokens and `**` is neither whitespace nor a hyphen, so `[-\s]{1,20}` cannot cross
it: sites went **13 → 18**, and the two recovered included
`sdk/tests/test_two_board_referents.py:25` itself. But blanking `~` alongside the
other emphasis markers **eats `~~` before strikes are classified**, and a first
strike pattern of `~~.+?~~` under `re.S` **paired a `~~` against one in a
different paragraph** and reported **`(D289)` as STRUCK on the ledger when it is
live** — a false negative that would have silently cancelled this round's own
repair. Caught by a strike-classifier control run **both ways** on the real row:
as shipped, D289 live = 1; with `(~~D289~~)` planted, D289 live = 0. Order is now
strikes → prefixes → emphasis, all offset-preserving, `^[ \t]*` never `^\s*`.

**Final control ledger for the staleness sweep, by `scripts/control_kind.py`
from evidence rather than a typed label: RECOGNITION** — 7 mutually independent
vocabulary forms and 4 wrap forms (plain, wrap, blockquote-wrap, hyphen-split),
all 11 found; 2 negative forms correctly rejected; struck negative at **zero**
gain after strike-blanking.

---

## 8. THE D316 REPAIR

`LADDER_V_TRIPLE_VERIFICATION.md`'s V16 row is repaired in place, append-only
register discipline preserved:

1. **`(D289)` struck in place → D303.** Measured, not inherited: D289 holds
   round-12 content. **The mechanism reproduced independently here** — hashing
   the first 400 characters of every docket row's content found exactly **three**
   content-duplicate pairs under distinct IDs: **D289↔D298, D290↔D299,
   D291↔D300**. That is the CAS's blind spot measured directly: **it asserts an
   ID is FREE and never that the CONTENT is new.**
2. **`(D291)` struck in place → D305.** Same cause.
3. **D265(b) advanced from open to CLOSED** at `29ad0364` / D308, re-proved in
   §4 here.

D302's strike reached `LADDER_V_V16_ROUND13.md` §7.3 and nowhere else. **An ID
citation is not a dated claim, so the round-13 block's frame anchor does not save
it** — D289 held round-12 content at `22e32c03` too.

**D315 is routed, not repaired.** `board_placement_faults`' docstring at
`scripts/self_audit.py:3796` reads *"at a price of clearing **two live
faults**"* — present tense, unanchored, against a live rule-A count of **61**,
~270 lines from the figure D308 repaired. Its anchored neighbour at `:3777`
(*"go from 2 to 68 … 1455 opened surfaces"*, `2026-08-14`, `48d3f05a`) is a dated
measurement and is not the finding. The discriminator returned **CANNOT_TELL**
and round 14 **did not promote it**, hand-adjudicating ASSERT with written
grounds; that adjudication is left standing and the row is routed to the
`self_audit.py` owner. **Not repaired here, and not by the agent closing the
rung.**

---

## 9. THE VERDICT

**V16 PASSES. Plain PASS.** Not "PASS WITH RESIDUALS", not "PASS WITH
EXCEPTIONS" — those labels are illegal in this lab and grades have been voided
for issuing them.

| clause | state at `04b9cc37` |
|---|---|
| C1 the placement predicate | **VOID** under `bcad2bbc` — cannot block, and **may not be cited as evidence the guard is correct** |
| C2 whole text, whitespace collapsed | **held** |
| C3 guard + `test_rank_claim_surfaces.py` on the three founding defects | **held** — 172 passed, 36 subtests, 0 failures |
| C4 rate stated, corpus named, excluded senses named | **SATISFIED at `20 of 28 (71%)` and `19 of 25 (76%)`** |
| C5 reach declared, measured on held-out sentences | **SATISFIED** |
| D265(b), the typed figure | **CLOSED** at `29ad0364`, re-proved by mutation at 61 → 63 |

**WHAT THIS PASS DOES NOT SAY.** It does not say the guard is precise: it falsely
faults **20 of 28** and **19 of 25**. It does not say the placement predicate
works: on the live board it is wrong in both directions for all four entrants C1
covers. It says the guard **discloses** what it costs and what it cannot reach,
measured, with its corpus and its excluded senses named — which is what V16's
criterion, read whole, requires.

---

## 10. NEUTRALITY, AND WHAT WOULD FALSIFY THIS ROUND

**NOT belief-neutral.** R-VALUE stays at **ZERO**. A reader who did not run this
round would afterwards believe things they did not before: that V16 closes, that
its close is a disclosure close at 71%/76%, that C1 is void rather than
satisfied, and that round 14's scope ruling was right for the wrong reason.

**What would falsify it, any one, executed:**

- Show `_place_precision_sentence()` at HEAD omitting a rate, its corpus, or the
  excluded sense; or `_place_reach_sentence()` omitting its measured rows.
- Produce a rank for Yang **derived from the benchmark README at `deb91557`** —
  that collapses §3 by making C1 satisfiable without re-pointing.
- Re-run §4 cell C and obtain an emitted figure that **moves** under the
  hardcoded literal.
- Show a pre-registration, dated before the first V16 grade, fixing a
  false-positive threshold for this rung. **That would reverse §1 and this
  verdict with it.**

---

## 11. WHAT THIS ROUND DID NOT DO

- **No guard was tuned.** No window, pattern, admission rule, board, severity or
  admission predicate was touched. `scripts/self_audit.py` was byte-identical to
  HEAD before and after every cell, by content comparison, and was **never
  written to at all**.
- **The scoring pin `deb91557` was not moved.** §3 is the argument for why it
  must not be.
- **D315 was routed, not repaired**, and `test_two_board_referents.py` was not
  touched.
- No solver ran. No scoring call was made; the ledger stood at **6**. Nothing was
  sent, uploaded, filed with an organiser or registered. Submissions remained
  **PARKED**.
