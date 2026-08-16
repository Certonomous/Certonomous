# Ladder V — V16, GRADE ROUND 14, by a NON-AUTHOR of every prior V16 round

**Verdict: round 13's substantive reversal SURVIVES a non-author's execution.**
**All five clauses C1–C5 were satisfied-or-void at frame `e71faf8b`, the D308 repair holds
under an independently built mutation proof, and V16 was PASSABLE at that frame.**
**This round did NOT close the rung**, for one reason that is an adjudication and not a
defect: which reading of C4 governs was a chief's ruling and was not taken here.

**This round was NOT belief-neutral.** R-VALUE's consecutive-neutral count stayed at
**ZERO**.

---

## 0. FRAME AND INDEPENDENCE

| field | value |
|---|---|
| subject rounds | round 13 `b6974959`, ledger `423abe1a`; the D308 repair `29ad0364` |
| ancestry asserted before any cell | `git merge-base --is-ancestor` returned 0 for `29ad0364`, `22e32c03`, `b6974959`, `423abe1a`, `bcad2bbc`, `04489465` |
| frames measured | `2daebd70` (mutation proof), `38cd036f` (staleness sweep), `e71faf8b` (final tree assertion) — HEAD moved five times under this round and every cell names the frame it ran at |
| R-ISOLATE | **SATISFIED.** This agent authored no V16 round, did not write `scripts/self_audit.py`, and did not write the D308 repair it re-executes. |
| `scripts/self_audit.py` | asserted byte-clean against HEAD **by content comparison**, before and after every cell (`cmp` against `git show HEAD:scripts/self_audit.py`, never `git status`) |
| `git status` | **read stale under concurrency exactly as the lab's own note predicts**: it reported `scripts/self_audit.py` as `MM` at a moment when content comparison against HEAD returned byte-identical. The status output was discarded and the content comparison governed. |

**Method.** `__pycache__` purged before every measurement. Plants by **line index**, read
back from disk before any figure was believed. Every board figure re-derived —
`ast.literal_eval` on the `LIVE_BOARD` assignment node in
`sdk/scripts/probability_of_rank.py`, the module never imported; `_published_board()`
called directly. No figure below was quoted from round 13 or from the dispatch brief.

---

## 1. THE CRITERION, QUOTED FROM ITS SOURCE

Round 13 quoted V16's clauses from V16's face. The face is
`demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md`, section **V16 (A16)**,
read here at HEAD rather than from round 13. Verbatim, and the emphasis is this round's:

> Therefore: **every ordinal this lab pins on an entrant is checked against the published
> board, which is parsed from the benchmark's own README table rather than transcribed**,
> and the check runs over **whole text with whitespace collapsed**. … Guard:
> `scripts/self_audit.py::check_board_placement_words`; tests:
> `sdk/tests/test_rank_claim_surfaces.py`, whose test set **is** the three defects: the
> guard fires on all three as they were and on none as they now are. **Precision is a
> requirement of this rung, not a nicety** — a guard that cries wolf gets switched off, and
> then it guards nothing — **so the rung fails if the check does not state its
> false-positive rate against a measured corpus and name the senses of the word it
> excludes.** **And its stated REACH is a requirement too, added 2026-08-11 by the first
> grade of this rung**: the check must declare what its patterns cannot phrase, measured on
> held-out sentences rather than asserted, because a replacement whose stated reach is less
> honest than its predecessor's is the failure V16 exists to fix.

**ROUND 13'S READING OF C4 IS THE READING THE WORDS CARRY, AND THE GRAMMAR IS THE
GROUND.** The only failure condition the clause types is `fails if the check does not
**state** its false-positive rate`. It does not type a threshold, a ceiling, or a
comparison. The chief's briefing — that C4 "makes false-positive rate a PASS requirement
while the guard has two discriminators it does not have" — is not what the sentence says.
**Round 13's correction of the chief stands.**

**AND ROUND 13 TRUNCATED ITS OWN QUOTATION AT THE POINT WHERE THE COUNTER-ARGUMENT LIVES,
WHICH IS RECORDED HERE BECAUSE IT IS THE ONE THING A READER WOULD WANT ANSWERED.** Round
13 §1 renders C4 as *"the rung fails if the check does not state its false-positive rate
against a measured corpus and name the senses of the word it excludes"* and drops the
clause immediately in front of it: ***"Precision is a requirement of this rung, not a
nicety — a guard that cries wolf gets switched off, and then it guards nothing"***. That
dropped clause is the strongest available argument for a performance reading, and round 13
neither quoted nor answered it. **It is answered here rather than dropped again:** the two
clauses are joined by **"so"**, which makes the precision statement the RATIONALE and the
disclosure the OPERATIVE CONDITION. A rationale does not create a second failure condition
the sentence declines to state. **The reversal survives the omission — but the omission was
material, because the rates the check states are 71% and 76%, and under the performance
reading V16 fails hard while under the disclosure reading it passes. The whole rung turns
on which reading governs, and that is a ruling, not a measurement.**

---

## 2. C4 AND C5 — RE-EXECUTED AT `e71faf8b`, CONFIRMED

`_place_precision_sentence()` and `_place_reach_sentence()` called directly, the module
loaded from source with `sys.modules` registered so nothing was inferred from a sweep.

| clause | requirement | measured, independently of round 13's figures |
|---|---|---|
| C4 | **states** a false-positive rate | **`20 of 28 (71%)` and `19 of 25 (76%)`**, two rows, both present in a 5,733-character sentence |
| C4 | against a **measured corpus** | the corpus is named **3** times (`non-placement set`); both sets identified by builder and by source file (`campaign/V16_PRECISION_SET.py`, `campaign/V16_GRADE_ROUND7_PRECISION_SET.py`) |
| C4 | **names the senses of the word it excludes** | present verbatim — *"a **linear-algebra** subject whose head noun is not in `_PLACE_LINALG_NEAR` -- a kernel, a Gramian, a Laplacian, an array"*; all five tokens found by search |
| C5 | declares what its patterns cannot phrase | reach sentence, **1,610** characters |
| C5 | **measured on held-out sentences** | seven rate-shaped figures across **three** rule-A sets plus a rule-B row: `40 of 45 (89%)` → `20 of 45 (44%)`, `37 of 46 (80%)` → `14 of 46 (30%)`, `42 of 45 (93%)`, `5 of 5` |
| C5 | measured **rather than asserted** | **4** `invented` clauses, each naming its builder and whether they were blind; `_PLACE_REACH` carries the builder and the blind flag per row |

**C4 AND C5 WERE SATISFIED AT `e71faf8b`.** Round 13's §2 is confirmed, and confirmed at a
frame six commits later than the one it measured.

**ONE RESIDUAL INSIDE C4, FOUND HERE AND NOT BY ROUND 13, AND IT DOES NOT DEFEAT THE
CLAUSE.** The precision sentence closes with its own disclaimer: *"BOTH SETS ARE
ADVERSARIAL AND NOT REPRESENTATIVE, each weighted toward shapes that have already broken
this guard, **so neither is a corpus rate**; the corpus rate is the live sweep this same
verdict reports"*. So the check states two rates and says in the same breath that neither
is a corpus rate, while C4 asks for a rate *"against a measured corpus"*. **Adjudicated
here rather than left to a reader:** C4 requires the corpus be MEASURED, not that it be
REPRESENTATIVE. Both sets are measured, committed, and recomputed from their own files by
`sdk/tests/test_rank_claim_surfaces.py`. **C4 is met.** The disclaimer is the check being
more honest than the clause requires, which is the direction C5's own rationale asks for.

---

## 3. C1 — RE-EXECUTED, AND ON A WIDER BASE THAN ROUND 13 TESTED

### 3.1 The board, re-derived

```
LIVE_BOARD          by ast.literal_eval on the assignment node, module NOT imported
  published_overall  Yang .0580  Reissmann .0595  Wu .0624  Tian .0641  Liu .0737  Montoya .0779
                     -> live ranks  yang 1, reissmann 2, wu 3, tian 4, liu 5, montoya 6

_published_board()  -> {'reissmann': 1, 'wu': 2, 'liu': 3, 'montoya': 4}
benchmark clone HEAD-> deb91557184af3cb95f5190494ec52d8f2c6a0d1
pin date            -> 2026-05-04
'yang' on it        -> False        board.get('yang') -> None
'tian' on it        -> False        ranks available   -> [1, 2, 3, 4]
```

### 3.2 The extension experiment, run EXHAUSTIVELY rather than at two points

Round 13 tested two candidate ranks for Yang — his live rank and one invented value. **This
round drove every value the vocabulary admits.** Controls: a wrong-vs-pin placement on Wu
that must fault in every configuration, and a nonsense-entrant placement that must stay
silent in every configuration.

| board handed to `board_placement_faults` | `rank-1 …, Yang` **TRUE of live** | `rank-6 …, Yang` **FALSE of live** | control (Wu, wrong) | negative | correct for Yang? |
|---|---|---|---|---|---|
| the pin as shipped | 0 | 0 | **1** | 0 | no — invisible both ways |
| + yang at **1**, his LIVE rank | **0** | **1** | **1** | 0 | **YES** |
| + yang at 2 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 3 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 4 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 5 (invented) | 1 ✗ | 1 | **1** | 0 | no |
| + yang at 6 (invented) | 1 ✗ | **0** ✗ | **1** | 0 | no — and it inverts |

**Of every value the board can hold, exactly one behaves correctly, and it is the value
that can only come from the live board.** Round 13's §3.2(iii) is confirmed and
strengthened: it is not that an invented rank happens to misfire, it is that **the correct
behaviour is uniquely determined by the forbidden import**.

**(i) The recogniser and the oracle are one object — confirmed from source, not argued.**
`_board_names(board)` returns `re.compile(r"\b(" + "|".join(re.escape(k) for k in
sorted(board)) + r")\b", re.I)` — the vocabulary IS the oracle's key set — and
`_placements(text, names, board)` receives both. **There is no parameter that widens one
without the other.** Round 11's F1 asked for a separation that does not exist.

**(ii) Re-pointing is forbidden by two independent instruments, both read at source.**
`04489465`'s own commit body: *"It explicitly does NOT authorise re-pointing the guard —
that trades a silent instrument for a loud wrong one."* And the guard's own emitted frame:
*"The pin is NOT stale and must not be moved (rung V1 needs the case scores to recompute
identically)."*

**(iii) Ruling `bcad2bbc` verified at source:** *"A criterion may not require more than the
maximum permitted action on the surface it grades … a per-sentence reading is void there
rather than strict."*

### 3.3 A THIRD ROUTE ROUND 13 DID NOT RUN, and it lands in the same place

Round 13's reading (a) — *entrant = an entrant on the board C1 names* — asserts that the
four entrants C1 does cover **are checked**. That is true only if *"the published board"*
means the frozen parse. **Chief ruling `04489465` says otherwise for a whole class of
claims:** *"the referent is fixed by the claim, not by the rung. Undated present-tense
claims grade against the live board; dated claims grade against the board they name."*
Driven at `e71faf8b`, on the four entrants C1 indisputably covers:

| sentence | true of the LIVE board? | guard faults it? | correct? |
|---|---|---|---|
| `The rank-2 entry, Reissmann, Fang & Sandberg, …` | **yes** | **yes** | **no** |
| `The rank-1 entry, Reissmann, Fang & Sandberg, …` | no | no | **no** |
| `The rank-3 entry, Wu & Zhang, …` | **yes** | **yes** | **no** |
| `The rank-2 entry, Wu & Zhang, …` | no | no | **no** |
| `The rank-5 entry, Liu, Wang, Zhao & Xiao, …` | **yes** | **yes** | **no** |
| `The rank-3 entry, Liu, Wang, Zhao & Xiao, …` | no | no | **no** |
| `The rank-6 entry, Montoya, Oulghelou & Cinnella, …` | **yes** | **yes** | **no** |
| `The rank-4 entry, Montoya, Oulghelou & Cinnella, …` | no | no | **no** |

Negative control 0, recognition control 1.

**The guard is wrong in BOTH directions against the live board for ALL FOUR entrants C1
covers, not only for the two it cannot see.** This does not defeat round 13 — it removes
the last way its conclusion could have been narrow. **A third reading exists** — *"the
published board" = the board as published today* — and under it C1 fails for six entrants
rather than two, is satisfiable only by re-pointing, and is therefore **VOID under
`bcad2bbc`** exactly as reading (b) is.

**C1 was SATISFIED-OR-VOID at `e71faf8b` under every one of the three readings that can be
constructed from its words. It could not fail the rung.** Round 13's §3.3 is confirmed on a
base one reading wider than it tested. **Which reading governs remains the chief's, and is
not taken here either.**

---

## 4. THE TWO DISCRIMINATOR GAPS — OFF THE CRITICAL PATH, AND MORE THAN THAT

Round 13 claimed the gaps do not bear on C4 or C5. **Confirmed, and the stronger statement
is available and is made here: both gaps are affirmatively DISCLOSED BY NAME, WITH COUNTS,
inside the very sentence C4 requires.** Read out of `_place_precision_sentence()` at
`e71faf8b`:

- **GAP-Q (use versus mention)** — *"quotation (3 author / 3 grader -- a wrong placement
  QUOTED in order to name or correct it. Rule A has an adjudication clause and rule B has
  none, **and neither reads intent**)"*, and again in the frame's blind list as *"(5) rule
  B cannot tell USING a phrase from QUOTING one."*
- **GAP-B (which board a sentence names)** — *"other-named-board (0 author / 2 grader -- a
  real placement on a DIFFERENT and explicitly named ranking … **This check reads WHETHER
  an ordinal is claimed, never WHICH board it is claimed on**, and naming the other ranking
  in the same sentence does not clear it)"*.

**A gap that is named, counted and published is not a gap the disclosure clauses can fail
on — it is the thing they exist to require.** Round 13's claim 3 is confirmed and its
ground is firmer than the one round 13 gave for it.

---

## 5. D308 — THE MUTATION PROOF, REBUILT AND RE-RUN INDEPENDENTLY

The repair at `29ad0364` was proved by its own author's harness. It was rebuilt here from
scratch, with a stronger control, and it reproduces.

**A safety improvement over the original method, stated because it matters.** The author
wrote the mutant into `scripts/self_audit.py` and restored it afterwards. This round
**never wrote to `scripts/self_audit.py` at all**: the mutated source was compiled from a
string with `compile(src, "<the real path>", "exec")` so that `REPO = Path(__file__)…`
resolved identically, and the file on disk was asserted byte-identical to HEAD before and
after by content comparison.

**The control was asserted GREEN before any mutation**, and green was defined as *the
emitted figure agreeing with a count classified independently by message shape*, never as
`returncode == 0`.

| cell | code | corpus | emitted rule-A | independently counted rule-A |
|---|---|---|---|---|
| **A** control | derived, as shipped | pristine | **56** | **56** |
| **B** | derived, as shipped | + 2 planted rule-A faults | **58** | **58** |
| **C** discriminating | **hardcoded literal `56`**, same digits | the **identical** 2 plants | **56** | **58** |

- **The derived figure tracked the mutation**: +2 emitted against +2 true.
- **The mutation killed the literal**: 0 emitted against +2 true. **The proof is not
  satisfied by a value that merely matches.**
- Rule-B stayed at 15 in all three cells, and the **struck negative control** planted
  alongside contributed nothing — the delta was exactly the two live plants.

**The control was RECOGNITION-grade, not reachability-only.** Four syntactically distinct
placement forms were validated in isolation first — `The rank-4 entry, Wu & Zhang's
SST-QCRC, …`; `Liu, Wang, Zhao & Xiao took second place …`; `Montoya, Oulghelou & Cinnella
ranked first …`; `Reissmann, Fang & Sandberg is the third-place entry` — all four faulted,
none is a substring of another, and **the plants are semantic rather than literal**: no
string the guard searches for was planted, only a wrong ordinal the guard had to recognise.
A TRUE placement (`Wu & Zhang's SST-QCRC is the rank-2 entry`) stayed silent and a
nonsense-entrant placement stayed silent.

**THE FIGURE MOVED AGAIN UNDER THIS ROUND, WITH NO REPAIR, AND THAT IS THE REPAIR'S BEST
EVIDENCE.** D308 derived **53** at `9cdb1851`. This round derived **56** at `2daebd70`.
Nobody edited the sentence between those frames. **A literal would have been stale for the
fourth time in three days; the interpolation was correct at both.** D308's central argument
— that this number must not be repaired with a number — is confirmed by the number moving
under the grader who came to check it.

**D308's other declarations, checked:**

| declaration | verified |
|---|---|
| 22 lines added, 5 removed, by content comparison | **yes** — `git diff 29ad0364^ 29ad0364` counts 22 added / 5 removed |
| nothing tuned: no window, pattern, admission rule, board, severity or admission predicate | **yes** — the whole diff is a comment block, `rule_a_faults = rule_b_faults = 0`, two `+=` accumulations, and the rewritten f-string |
| the historical pair kept but relabelled a dated measurement | **yes** — *"took … AS THAT TREE THEN STOOD"*, *"THAT PAIR IS A DATED MEASUREMENT AND NOT A LIVE FIGURE: only re-running the swap moves the 68, and this check does not run it"* |
| 0 failures across the three consuming modules | **yes** — `test_rank_claim_surfaces.py`, `test_two_board_referents.py`, `test_fault_message_matches_rule.py`: **172 passed, 36 subtests passed, 0 failures**, 804s |
| "217 tests" | **not reproduced as a count.** The suite reported 172 tests and 36 subtests at `e71faf8b`, against D308's 217 at `29ad0364`. The load-bearing half — **zero failures** — reproduced exactly. The discrepancy is recorded rather than reconciled, because a test count is not a claim this round was sent to grade and HEAD moved eleven commits between the two runs. |

**A trap reproduced live, and it is worth the line.** This round's first mutation attempt
was killed by a foreground timeout at 120s. **Its `finally:` clause did not run**, and the
seed file was left carrying the plant — detected by content comparison against
`git show HEAD:<path>`, restored, and the cell re-run under a longer budget. *A `finally`
does not survive a process kill* is not a maxim here; it happened, in this round, on the
first try.

---

## 6. THE VERDICT ON ROUND 13'S FOUR CLAIMS

| # | round 13's claim | non-author's ruling at `e71faf8b` |
|---|---|---|
| 1 | C4 and C5 are DISCLOSURE requirements and both are satisfied | **CONFIRMED** by execution and by the clause's grammar. **Residual:** round 13's quotation of C4 was truncated in front of the one clause that argues the other way, and that clause is answered in §1 here rather than dropped again. |
| 2 | C1 cannot fail under either reading; satisfied or VOID | **CONFIRMED, on a base one reading wider.** A third reading exists (§3.3) and it lands on VOID as well. The exhaustive extension experiment shows the only value that works is the forbidden one. |
| 3 | both discriminator gaps are off V16's critical path | **CONFIRMED, and stronger:** they are disclosed by name and by count inside C4's own sentence (§4). |
| 4 | what blocked the rung was one typed figure, not a missing capability | **CONFIRMED, and the figure is now derived.** The repair holds under an independently rebuilt mutation proof, and the figure moved 53 → 56 under this round with no edit (§5). |

---

## 7. IS THE RUNG PASSABLE?

**YES. At `e71faf8b` no clause of V16's criterion stood unsatisfied by any permitted
action, and the blocker round 13 named was closed by derivation and verified here by a
non-author.**

| clause | state at `e71faf8b` |
|---|---|
| C1 the predicate | **satisfied or VOID** under all three constructible readings — cannot fail |
| C2 whole text, whitespace collapsed | **held** — the emitted frame states it and the check implements it |
| C3 guard + `test_rank_claim_surfaces.py` fire on the three founding defects | **held** — 0 failures across the three consuming modules |
| C4 rate stated, corpus named, excluded senses named | **SATISFIED**, re-measured |
| C5 reach declared, measured on held-out sentences | **SATISFIED**, re-measured |
| D265(b), the typed figure | **CLOSED** at `29ad0364` / D308, re-proved here |

**THIS ROUND DID NOT CLOSE THE RUNG, AND THE REASON IS NOT A DEFECT.** Two questions on
V16's face are RULINGS and not measurements, and the same agent that cannot take them is
the one that raised them: **which reading of *"an entrant"* and of *"the published board"*
governs C1**, and **whether C4's operative condition is its disclosure clause or its
precision preamble**. §1 and §3.3 give the grounds and decline the ruling, as round 13
did and for the same reason. **A closer holding those rulings has no measured obstacle
left.**

---

## 8. FILED, NOT APPENDED (R-CONVERGE)

None of the following defeats a clause of V16's criterion, so none is appended to the live
rung.

**N1 — V16's LEDGER ROW STILL CITES THE PHANTOM ROWS, AND D302's STRIKE-IN-PLACE REPAIR
DID NOT REACH IT.** `LADDER_V_TRIPLE_VERIFICATION.md`'s V16 row, at HEAD, cites **`(D289)`**
for the C1 finding and **`(D291)`** for the GAP-B costing, **unstruck**. D302 records that
those IDs hold round-12 content and that round 13's real rows are D303–D305; the strike was
applied in `LADDER_V_V16_ROUND13.md` §7.3 and nowhere else. **The round-13 block's frame
anchor does not save this one**: an ID citation is not a dated claim — D289 held round-12
content at `22e32c03` too. **Owner: the author of D302's repair, or the chief.**

**N2 — THE D308 REPAIR LEFT THE SAME STALE FIGURE IN THE SAME FILE, ~270 LINES AWAY.**
`scripts/self_audit.py`'s `board_placement_faults` docstring reads *"…would therefore fault
50 correct dated records AND regrade the instrument against itself, **at a price of
clearing two live faults** -- which is not a repair."* **Present tense, no anchor, and the
live rule-A count derived at `2daebd70` was 56.** The same docstring carries *"rule-A
faults **go** from 2 to 68"* over *"the same 1455 opened surfaces"* — that one IS anchored
(`2026-08-14`, `48d3f05a`) and is a dated measurement; **the "two live faults" clause is
not anchored and is the finding.** Sixty lines below it, D308 repaired the emitted twin.
`use_mention_discriminator.classify` returned **CANNOT_TELL** (*"both stances present"*);
**hand-adjudicated ASSERT**, on the written ground that the clause is in the file's own
voice, is not enclosed, and the discriminator's MENTION evidence comes from an attribution
verb governing a *different* span. **Not repaired here — this round graded it.**

**N3 — `sdk/tests/test_two_board_referents.py`'s MODULE DOCSTRING IS STALE, AND IT IS
**OUT** OF V16's SCOPE.** It reads *"…across the tracked corpus (**1455 opened surfaces**),
swapping it to the live board takes rule-A faults from 2 to 68 over disjoint sets -- **both
current faults CLEAR**…"*. At `2daebd70` the sweep opened **1558** surfaces and carried
**56** rule-A faults. **The scope ruling, and it rests on the lab's own standing predicate
rather than on this round's judgement:** `scripts/self_audit.py:1749` defines
`_VALUE_NOT_A_SURFACE = ("sdk/tests/",)` — *"a labelled test corpus is not a claim
surface"* — and V16's face names `sdk/tests/test_rank_claim_surfaces.py` and no other test
module. The sentence is emitted by nothing, asserted by no test, and lives on a path the
lab excludes from claim surfaces by rule. **It is a live stale claim on a lab record and it
is FILED. It is not a V16 blocker, and it was not repaired here, because a grader does not
repair what it grades.**

**N4 — V16's LEDGER ROW RECORDS ITS BLOCKER AS OPEN WHEN IT IS CLOSED.** The same row states
*"`self_audit.py:4042` still emits … (D265(b), unrepaired…)"*. Repaired at `29ad0364`,
closed at D308. The clause sits inside a block that opens with its frame (`ROUND 13,
2026-08-16, frame 22e32c03`), so it is anchored and is **not** a W-5 violation — **it is a
ledger that has not been advanced.** It errs in the direction the ladder's own 2026-08-15
records-repair note names as *"least likely to be checked"*: the lab recorded as further
from green than it is. **Owner: the chief**, since advancing V16's row is a verdict entry
and this round declines to enter one.

**Instrument note, and it changed a result.** Two of these sites were reported ABSENT by a
first pass built with literal spaces, because the sentences wrap in source. Rebuilt with
`\s+` **and** with leading blockquote prefixes stripped for detection only, both appeared.
Demonstrated on a control rather than asserted: the form
`"> takes rule-A faults from\n> 2 to 68 over disjoint sets"` is **missed by `\s+` alone**
and **found** once `>` prefixes are stripped — `>` is not whitespace. The sweep's controls
were **RECOGNITION**-grade by `control_kind.py`'s definition (six distinct forms, none a
substring of another, all six fired) with a **struck negative control** that returned
nothing after strike-blanking.

---

## 9. NEUTRALITY, AND WHAT WOULD FALSIFY THIS ROUND

**THIS ROUND WAS NOT BELIEF-NEUTRAL.** R-VALUE's consecutive count stayed at **ZERO**. A
reader of the record who did not run this round would believe something different
afterwards: that round 13's reversal is confirmed rather than unconfirmed, that V16's last
measured blocker is closed and the closure is proved by a non-author, that C1 is
satisfied-or-void under a third reading nobody had run, and that four stale carriers of the
same sentence are still live on lab records.

**What would falsify it, any one, executed:**

- Show `_place_precision_sentence()` at HEAD omitting a rate, a corpus, or the excluded
  sense; or `_place_reach_sentence()` omitting its measured rows.
- Produce a rank for Yang **derived from the benchmark README at `deb91557`**. That single
  artefact collapses §3, because it makes C1 satisfiable without re-pointing.
- Show a permitted action that widens `_board_names`' vocabulary without widening the
  oracle.
- Re-run §5 cell C and obtain an emitted figure that MOVES under the hardcoded literal —
  that would show the mutation is not discriminating.
- Show the chief ruling that C4's operative condition is its precision preamble rather than
  its disclosure clause. **That does not falsify a measurement here; it changes the verdict
  in §7 to a FAIL, and it is the one input this round is missing.**

---

## 10. WHAT THIS ROUND DID NOT DO

- **No repair was made to anything graded.** N2 and N3 were found, adjudicated and filed
  unrepaired, deliberately.
- **No guard was tuned.** No window, pattern, admission rule, board, severity or admission
  predicate was touched. `scripts/self_audit.py` was byte-identical to HEAD before and
  after every cell, by content comparison.
- **The scoring pin `deb91557` was not moved**, and §3 is the argument for why it must not
  be.
- **V16's ledger row was not edited.** A grade round that files rather than appends does
  not write the rung's verdict cell.
- No solver ran. No scoring call was made; the ledger stood at **6**. Nothing was sent,
  uploaded, filed with an organiser or registered. Submissions remained **PARKED**.
