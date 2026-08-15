# Ladder V — V16, GRADE ROUND 11

**Verdict: V16 does NOT close this round, and the round is NOT belief-neutral.**
**Eight new material findings, four of them new shapes.** R-VALUE's consecutive-neutral
count stays at **zero**.

Graded at frame **`9dca4738`** (2026-08-15T20:54:47Z), in a detached worktree at that
commit, so that the concurrent *uncommitted* edits to `scripts/self_audit.py` could not be
mistaken for the state of record. HEAD moved to `e98e40fe` while this document was being
written; §0.3 states the drift and what it does and does not change.

---

## 0. THE FRAME

### 0.1 Independence — from the dispatch record, and not from git or from the lab's own check

Under R-ISOLATE the grader must not be an author of the subject. **Git cannot establish
that here** — one identity signs ~1,741 of 1,876 commits, auto-configured from username
and hostname — and **neither can the session container**, open since 2026-08-04.
**`scripts/check_rung_attribution.py` is not cited and must not be**: per D173 it has
emitted exactly one identity across 100% of its deployed life, all four real `Lab-Agent`
trailers are the same string, and running it with a closing commit against a graded one
returns `VERDICT: AUTHOR`. It names a *session*, not an agent.

What does establish it is the per-agent dispatch record at
`~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/`:

| field | value |
|---|---|
| this grader's agent id | `a00b47de0f60cc014` |
| `meta.json` description | `Run V16 round 11 grading` |
| first action | **2026-08-15 20:56Z** |
| newest commit in the subject at dispatch | `9dca4738`, **2026-08-15T20:54:47Z** |

Every commit in the graded range predates this agent's first action. The agents that built
the subject matter most are separately identified in the same directory and are not this
one: `a9e59fc3f0edda70c` (*"Fix empty-set PASS in the new checks"*), `a7b5e000524a53422`
(*"Implement the form-or-value declaration"*), `a77b4541f16e43978` (*"Repair the sixth
surface of rank claims"*).

**This evidence is untracked and per-machine (D130). No reader of this repository can
re-derive it.** It lives in a directory git does not see, on one box, and it will not
travel with the commit carrying this document. That is a defect of the lab's independence
apparatus, not of this round, and it is stated rather than worked around.

### 0.2 Scope, declared before any finding (R-CONVERGE)

V16's last graded round was **round 10**, commit `0c7b968d` (2026-08-12T16:13:12Z), whose
subject was `067caac0`. Scope is therefore **`0c7b968d..9dca4738`**, enumerated
mechanically before grading began:

| measure | count | how |
|---|---|---|
| commits in range | **197** | `git rev-list --count 0c7b968d..9dca4738` |
| files changed | **159** | `git diff --name-only … \| wc -l` |
| commits touching `scripts/self_audit.py` | **6** | `git log --format=%h … -- scripts/self_audit.py` |
| net lines into `scripts/self_audit.py` | **+2,625** | `git diff --stat` |
| new/changed rung test files | **4** (`test_rank_claim_values.py` +423, `test_two_board_referents.py` +330, `test_rank_claim_surfaces.py` +643, `test_fault_message_matches_rule.py`) | `git diff --stat` |
| new mutation harness | **185 lines** (`scripts/mutation_harness_rank_values.py`) | `git diff --stat` |
| docket rows added in range | **133** (52 → 185 distinct IDs, none removed) | `comm -13` over the two `^\| D…` ID sets |

**On the rung, in scope:** `check_board_placement_words` and its rule A/B core
`board_placement_faults`; the new sibling `check_rank_claim_values` (`847b4492`); the board
referents `_published_board`, `_ranking_board`, `_live_ranks`; the four test files above;
and V16's own face at `LADDER_V_TRIPLE_VERIFICATION.md:391-425` with its ledger rows at
`:816` and `:848`.

**Findings outside that boundary are FILED as append-only docket rows and are not appended
to the rung.** §5 lists them and says so for each.

### 0.3 Scope drift, measured

`git rev-list --count 0c7b968d..HEAD` returned **197** at 20:57Z and **200** at 21:10Z;
HEAD moved `9dca4738` → `e98e40fe` → `9393e267` inside the drafting window. Every count
here is stated at frame `9dca4738` unless it says otherwise.

**The ID space moved under this round, and the in-write assertion caught it.** The brief
said the highest docket ID was "at least D177". It was **D181** when this grader first read
`docs/DOCKET.md`, **D183** when the rows were drafted, and the write — which asserts each
target ID is free *inside* the same read-modify-write as the append — **aborted on
`D184 IS ALREADY ALLOCATED`**, another agent having taken D184–D186 in the seconds between
the check and the write. The rows were re-allocated to **D189–D194** and the second attempt
asserted clean against 188 existing IDs. This is the standing hazard, observed live; the
assertion is the reason it produced an abort rather than a collision.

### 0.4 Method, and what each count is a count of

- **Four arms, named per count.** This round measured the **tracked** arm by execution:
  20,701 paths from `_tracked_files()`, of which **18,974 were opened and decoded** and
  1,727 skipped as absent, a directory, or over the 4 MB cap. Enumeration used `git grep -a`
  where a text sweep was needed — plain `-I` skips 981 binary-marked files, 12 of which
  hold no NUL byte, and the shell's `grep` passes `-I` too. ~~**The untracked, gitignored
  and run-tree arms were NOT measured by this round, and no number is quoted for them.** The
  brief supplied ~1 / ~37,243 / a >2 MB run-tree set of 6,108-against-a-prior-10,526; none
  of those is inherited here, because every finding below is a property of the guard rather
  than of the corpus and none needs them. Saying "not measured" is the point of the rule.~~
  **Struck 2026-08-15 by this round's own author — see §9.** The sentence was true when
  written and false 66 minutes later: a four-arm census this round had itself dispatched
  returned after the round was committed, and **all four arms are measured**. The clause
  that survives is the second half: no finding below depends on any arm count, because every
  one is a property of the guard rather than of the corpus. §9 carries the numbers, what
  they corroborate, and the one new lead they produced.
- **`__pycache__` purged before every cell.** `PYTHONDONTWRITEBYTECODE=1` does not fix stale
  bytecode here; the directories are removed.
- **`/usr/bin/find`**, because `find` on this box is `bfs`.
- **No guard's silence is cited as evidence.** Where a guard is quoted, the quotation is
  reported as a fact *about the guard*, and the underlying question is re-derived
  independently. §4.8 is the case where the guard's own published number was checked and
  did not hold.
- **PDF claims are read visually.** §6 says exactly how, and corrects the premise this round
  was briefed with.

---

## 1. WHAT V16 REQUIRES, READ AS WRITTEN

From `LADDER_V_TRIPLE_VERIFICATION.md:391-425`:

1. **The predicate.** *"Every ordinal this lab pins on an entrant is checked against the
   published board, which is parsed from the benchmark's own README table rather than
   transcribed"*, over **whole text with whitespace collapsed**.
2. **The guard and its tests.** `scripts/self_audit.py::check_board_placement_words`;
   `sdk/tests/test_rank_claim_surfaces.py`, whose test set *is* the three founding defects.
3. **Precision is a pass requirement, not a nicety.** *"the rung fails if the check does not
   state its false-positive rate against a measured corpus and name the senses of the word
   it excludes."*
4. **Stated reach is a pass requirement too.** *"the check must declare what its patterns
   cannot phrase, measured on held-out sentences rather than asserted."*

Two chief rulings bear on this and are graded against, not around:

- **`04489465`** (2026-08-15T02:59:48Z) — *the referent is fixed by the claim, not by the
  rung. Undated present-tense claims grade against the live board; dated claims grade
  against the board they name.* It **explicitly declines to authorise re-pointing the
  guard** — *"that trades a silent instrument for a loud wrong one, 50 of the 68 new faults
  being correct dated records — so **until the dated-context discriminator exists**,
  criteria are graded by a reader and no grader may cite the guard's silence as evidence."*
- **`29452c51`** — **there is no strike stripper.** The only mechanism is
  `_PLACE_ADJUDICATED`, a 400-character proximity window.

---

## 2. THE THREE REFERENTS, EXECUTED

Read from the module rather than transcribed:

```
_published_board()  -> {'reissmann': 1, 'wu': 2, 'liu': 3, 'montoya': 4}     head deb91557
_ranking_board()    -> {'yang': 1, 'reissmann': 2, 'wu': 3, 'tian': 4,
                        'liu': 5, 'montoya': 6}
                       from campaign/BOARD_MOVED_2026-08-11.md, dated 2026-08-11
_live_ranks()       -> {'': 1, 'Yang': 2, 'Reissmann': 3, 'Wu': 4,
                        'Tian': 5, 'Liu': 6, 'Montoya': 7}          ('' is us)
```

Three referents, in one module, with **three different membership sets**. §4.1 and §4.7
both follow from the gap between the first and the third.

---

## 3. INHERITED FINDINGS, RE-EXECUTED RATHER THAN READ

Each was given to this round as established. Each was re-run. **All five held.**

### 3.1 D151 — the missing denominator predicate. **CONFIRMED, exactly.**

```
rule A on "Our entry is rank 1 of 5 on the closure challenge board."   -> 0 faults
rule A on "Our entry is rank 1 of 7 on the closure challenge board."   -> 0 faults
rule A on "The rank-3 entry, Wu & Zhang's SST-QCRC, uses a different
           closure."                          (positive control)      -> 1 fault
```

Rule A binds an ordinal to a **named published entrant**; a sentence placing *us* binds
nobody, `who is None`, and the loop continues. `_PLACE_OFN` then skips `^\s*of\s+\d` by
design. The receiving end now exists and works — §3.3.

### 3.2 D176 — the guard faults the repair. **CONFIRMED, and the misattribution reproduced.**

Correct **live-board** ordinals, one sentence each, rule A against the shipped pin:

| sentence (all TRUE of the live board) | rule A |
|---|---|
| Yang is rank 1 on the live board. | **0** |
| Reissmann is rank 2 on the live board. | **1** — *"'rank 2' is bound to Reissmann, whom the published board puts at rank 1"* |
| Wu & Zhang are rank 3 on the live board. | **1** |
| Tian is rank 4 on the live board. | **0** |
| Liu is rank 5 on the live board. | **1** |
| Montoya is rank 6 on the live board. | **1** |

Four correct statements faulted. The two that pass are the two the guard cannot see at all
(§4.1). Written as one six-ordinal table — the production shape D176 measured — rule A
returns **4 faults**.

**The wrong-entrant mechanism, reproduced directly.** D176 reports three of fourteen faults
naming the wrong entrant. Executed:

```
"Wu & Zhang were passed; Tian is rank 4 on the live board."
  -> 'rank 4' is bound to Wu, whom the published board puts at rank 2
```

The sentence places **Tian**. The fault names **Wu**. The subject walk steps left looking
for a name in `\b(liu|montoya|reissmann|wu)\b`, does not recognise `Tian`, and keeps walking
to the nearest name it does recognise. The same happens inside the six-ordinal table, where
`rank 4` — written immediately after the word `Tian` — is again reported against Wu.

**This is not a tuning defect. It is §4.1, and D176 recorded the symptom without the cause.**

### 3.3 `check_rank_claim_values` — the new predicate. **CONFIRMED SOUND on all three rules.**

`sdk/tests/test_rank_claim_values.py`: **27 tests, 14 subtests, all pass, 147.04s**
(`__pycache__` purged first). `scripts/mutation_harness_rank_values.py`: **control green,
all 8 mutants reddened their aimed tests** — M1 form-only grading, M2 denominator typed not
derived, M3 no dated-context discriminator, M4 banner swallowed by its own span, M5 the
empty set passes, M6 the strike masker dropped, M7 `comparable` graded without its ratio,
M8 the frozen pin not declined. **27 tests and 8 mutants, both verified by execution.**

Driven directly:

| input | verdict |
|---|---|
| `rank 1 of 5` (ours) | **FAULT** — *"the live board carries 6 entrants and our entry of record sorts to rank 1, so the claim is rank 1 of 7 counting us (or of 6 …)"* |
| `rank 1 of 7` (ours) | clean |
| `rank 1 of 6` (ours) | clean — both readings admissible |
| `We are rank 2 of 7 …` | **FAULT** — the numerator is graded too, not only the denominator |
| `Montoya is now rank 6 of 6 on the live board, not 4.` | clean — the case its docstring cites |
| `Montoya is now rank 2 of 6 …` | **FAULT**, correctly attributed to Montoya |
| `Yang is rank 4 of 6 …` | **FAULT**, correctly attributed to **Yang** |
| `Wu is rank 1 of 6 …` | **FAULT**, correctly attributed to Wu |
| `Reissmann is rank 2 of 6 …` | clean |
| `…our seed-uncertainty bound is comparable to the margin over the leader.` | **FAULT** — *"the bound is [177.12%, 178.82%] of the margin, so it EXCEEDS the margin it is called comparable to"* |

The third-party subject bind is correct: `_live_ranks()` is keyed by capitalised surname and
`_VALUE_OTHERS_SUBJECT` captures a capitalised name, so the two agree — the obvious
case-mismatch bug is **not** present. **The deferral D151 found dangling now has a receiving
end that does the thing** — and note the Yang row, which the sibling grades correctly and
rule A cannot see at all.

### 3.4 The unopenable archive. **CONFIRMED REPAIRED.**

`check_rank_claim_values` catches `(OSError, zipfile.BadZipFile)` and appends to `blind`,
with the defect named in the code: *"NOT a surface with empty text. That is how the sibling
swallowed an unreadable archive: an empty string makes no claim, makes no fault, and reads
on the report as a clean member."* The verdict ordering is `shipped` → `blind` → `internal`,
so **a shipped FAIL is no longer downgraded to a lab-record WARN by a corrupted zip**. The
old behaviour is gone. Mutant M5 pins the empty-set half.

### 3.5 The test that pins a repaired file at `([], [])`. **CONFIRMED as a class.**

`sdk/tests/test_rank_claim_surfaces.py::test_the_real_corpus_instances_stay_clean` (`:1026`)
asserts `([], [])` on two **real repository files** read from disk; D176 names `:2250` doing
the same for `CLOSURE_CHALLENGE_STATUS.md`. Any compliant strike-and-keep repair to a pinned
file reddens the suite until a pin-side ordinal is hand-written within 400 characters.
`test_the_real_corpus_instances_stay_clean` additionally carries `if not path.exists():
continue` — a silent skip that converts a deleted subject into a pass.

---

## 4. NEW MATERIAL FINDINGS

### 4.1 **F1 — Rule A cannot see the live leader. The pin supplies its names; the same module already holds the full roster.** *(NEW SHAPE)*

`_board_names(board)` compiles, at HEAD:

```
\b(liu|montoya|reissmann|wu)\b
```

Four names, from the **frozen scoring pin `deb91557`**. The live board has **six** entrants.
The two absent are **Yang, who is rank 1**, and **Tian, who is rank 4**. Executed, rule A
against the shipped configuration:

| sentence | true? | rule A |
|---|---|---|
| Yang is rank 6 on the live board. | **FALSE** (Yang is 1) | **0 faults** |
| Yang holds rank 3 on the published board. | **FALSE** | **0 faults** |
| Tian is rank 1 on the live board. | **FALSE** (Tian is 4) | **0 faults** |
| The rank-2 entry, Tian's model, leads the field. | **FALSE** | **0 faults** |
| The rank-2 entry, Wu's model, leads the field. | (control) | **1 fault** |

**Rule A is structurally incapable of faulting any ordinal pinned on Yang or Tian, true or
false.** Swap the name for a pinned one and the identical sentence faults.

**This is not D48 and not BLIND TO item 12.** Item 12 is about the pin's **age** — for the
four entrants the pin does carry, the ordinal is judged against a stale board and the error
runs both ways, but the sentence **is examined**. F1 is about the pin's **membership**: for
Yang and Tian no sentence is examined at all, in either direction. The guard's own "WHAT IT
CANNOT SEE" list runs to fourteen enumerated classes — including its nearest neighbour,
*"any entrant referred to by a co-author rather than the first author on their board row"* —
and does not contain this one.

**Why it is the worst possible omission for this rung.** V16 exists on the finding that *"a
wrong ordinal about a competitor is a rank claim about ourselves wearing a competitor's name,
and it is wrong in the direction that flatters us."* The competitor a lab most benefits from
misplacing is **the one ahead of it**. That is Yang. Rule A cannot see Yang.

**And the data is already in the process.** `_live_ranks()`, in the same file, returns seven
keys including `Yang` and `Tian`, and `check_rank_claim_values` uses it to grade third-party
placements about Yang correctly (§3.3). The two halves of one rung read two different rosters
from one module.

**F1 is also the cause of D176's misattribution** (§3.2): the subject walk skips the
unrecognised name and binds to the nearest recognised one. D176 filed the symptom.

**The remedy is explicitly not to move the pin.** The pin is correct and V1 needs it frozen.
F1 asks for the **recogniser's vocabulary**, which is a different list from the **oracle's**
ranks — see the shape statement in §7.2.

### 4.2 **F2 — The rung's precision requirement binds one guard, and the rung's function now runs across two.** *(NEW SHAPE)*

V16's face names one guard, `check_board_placement_words`, and makes two disclosures a **pass
requirement**: a stated false-positive rate against a measured corpus, and a stated reach
measured on held-out sentences.

`check_board_placement_words` satisfies both — `_PLACE_REACH`, `_PLACE_PRECISION` and
`_PLACE_FALSE_FAULT` are generated into the verdict and into BASIS over two held-out
non-placement sets (`campaign/V16_PRECISION_SET.py` and
`campaign/V16_GRADE_ROUND7_PRECISION_SET.py`), with the independent row the higher one.

`check_rank_claim_values` satisfies **neither**. Its `frame` string — read in full at
`scripts/self_audit.py:2050-2073` — reports surfaces considered, opened, skipped, decoded,
claims found, form-graded, value faults, ungraded passages, fixtures excluded, untriggered
surfaces, the board size, and the provenance of its arithmetic. **It states no false-positive
rate and names no held-out reach set.** Nor does the commit that built it (`847b4492`) claim
one.

Since `847b4492`, that check owns **the entire denominator predicate** — the thing D151 found
no instrument in this lab possessed, and the thing V16's own criterion sentence demands
("every ordinal this lab pins on an entrant"). So the half of the rung's criterion rebuilt
inside this scope carries none of the disclosure the rung makes a pass condition.

**The honest reading, stated as such.** V16's face names one guard, so on a literal reading
the requirement does not reach the sibling, and the rung is not failed *by this item alone*.
That is precisely the finding: **the criterion was written when one check did the work, the
work was split in two, and the requirement did not follow the function.** A pass requirement
a refactor can walk out of is an R-CONVERGE question, not a tuning question.

### 4.3 **F3 — Chief ruling `04489465` gated itself on a prerequisite that arrived the same day, and nothing recorded the arrival.** *(NEW SHAPE)*

Ruling `04489465` (2026-08-15T02:59:48Z) declines to re-point the guard at the live board on
a stated and falsifiable ground: *"until the **dated-context discriminator** exists, criteria
are graded by a reader"*, with the quantitative ground *"50 of the 68 new faults being correct
dated records."* The refusal has one named prerequisite and one number, and both are about the
same thing: dated records. A dated-context discriminator is exactly what removes them.

**The discriminator was built the same day, eighteen hours later, at `847b4492`**
(2026-08-15T20:26:59Z), by the commit that built `check_rank_claim_values`. Its own message
says so: *"THE DATED-CONTEXT DISCRIMINATOR … A section banner carrying a withdrawal verb AND
an ISO date exempts the section BELOW it. The date is required."* It lives at
`scripts/self_audit.py::_live_claim_text` (`:1529`), takes `(text, cdf)`, preserves offsets,
and is in production use by the sibling check. Mutant **M3** ("no dated-context
discriminator") reddens its aimed test, so the discriminator is not merely present but pinned.

**`board_placement_faults` does not call it, and `check_board_placement_words` passes raw
decoded text straight in** (`:3820`).

So the ruling's prerequisite has been met, in the same file, by another agent, and **no
surface records that it was met.** The ruling still reads as live and the guard still sits
un-repointed on a condition that has expired.

**The shape, which is the durable half:** *a ruling that gates itself on a prerequisite, with
nothing watching for the prerequisite's arrival.* The lab has met this exactly once before —
D48's addendum, *"THE LATENCY PREMISE HAS EXPIRED, AND WITH IT THIS ROW'S REASON FOR BEING
FILED RATHER THAN FIXED"* — and that expiry was caught by a human reading the row, not by
anything mechanical. Two instances, no mechanism.

§4.8 reports what the re-point would now actually cost, which is the measurement the ruling
could not make and this round could.

### 4.4 **F4 — The two halves of the rung disagree about what a live claim is, and rule A rejects the lab's own mandated repair idiom.**

The house rule is **strike-and-keep**: a superseded number is struck and left visible, never
deleted. The rung's own report source carries 35 such corrections in `\sout{}`.

Executed, one sentence per markup dialect, rule A raw against the masker its sibling runs
first:

| input | rule A on raw text | rule A after `_live_claim_text` |
|---|---|---|
| `\sout{The rank-3 entry, Wu \& Zhang's SST-QCRC}` (struck 2026-08-12) | **1 fault** | 0 |
| `~~The rank-3 entry, Wu & Zhang's SST-QCRC~~` (struck 2026-08-12) | **1 fault** | 0 |
| `<del>The rank-3 entry…</del>` struck 2026-08-12 | **1 fault** | 0 |
| `## Superseded 2026-08-12` + the same sentence below it | **1 fault** | 0 |

**Rule A faults all four. The masker clears all four.** `check_board_placement_words` applies
no masking at any level — it decodes bytes and calls `board_placement_faults` directly. Under
ruling `29452c51` there is no strike stripper, and the only mechanism is `_PLACE_ADJUDICATED`,
a 400-character proximity window, so every strike-and-keep correction of a wrong ordinal must
be silenced by hand-writing a *second*, pin-side placement inside 400 characters of the first.

**This is the mechanical cause of D176's "a compliant repair turned the suite red."** The
compliant repair was strike-and-keep; rule A cannot read a strike.

It is separable from the board-currency treadmill D48 priced. That treadmill is about *which
board*; this is about *whether the sentence is being asserted at all*.

**But the obvious remedy is unsafe, and §4.7 is why.** "Pipe rule A through `_live_claim_text`"
is the one-line fix this finding invites, and measured, it manufactures faults.

### 4.5 **F5 — Every one of the guard's live faults is self-referential, its sibling excludes exactly those surfaces by name, and the guard's own frame applies the concept only to a hypothetical.** *(NEW SHAPE)*

`check_board_placement_words()` run live at frame `9dca4738`, over 20,701 tracked paths, 1,504
opened, 167 naming an entrant, 983 placement expressions found:

> **`WARN` — every travelling surface agrees with the board; 29 lab record placement(s) do not.**

Tabulated by file (29 fault lines, 15 rule A and 14 rule B):

| file | faults | what it is |
|---|---|---|
| `docs/DOCKET.md` | 10 | docket rows **recording this guard's own defects** |
| `sdk/tests/test_fault_message_matches_rule.py` | 8 | **this guard's own test file** |
| `demo-output/website/campaign/LADDER_V_V15_ROUND7.md` | 3 | a round document **grading this guard** |
| `sdk/tests/test_two_board_referents.py` | 3 | **this guard's own test file** |
| `docs/INSTRUMENT_INTEGRITY_LEDGER.md` | 2 | the ledger row about this guard |
| `scripts/self_audit.py` | 2 | **this guard's own source comments** |
| `campaign/MARGIN_PRECISION_INTERVAL_2026-08-15.md` | 1 | a measurement record |

**Not one of the 29 is a claim this lab is making about the board.** Every one is a quotation
of the guard's own behaviour — in its own source, in its own fixtures, in the rows that
document its defects, and in the documents that grade it. The instrument is measuring its own
paperwork.

**Its sibling already solved this, by name.** `check_rank_claim_values` carries
`_VALUE_NOT_A_SURFACE = ("sdk/tests/",)` with the rationale written into the module — *"A
LABELLED TEST CORPUS IS NOT A CLAIM SURFACE, and this is a definition rather than a tuning. …
Faulting them is faulting the control."* — and prints the excluded count in its frame.
`check_board_placement_words` has no such exclusion and is right now reporting **11 faults
inside two of its own test files and 2 inside its own source**.

**And the guard already has the concept — it applies it only to a future it declined.** Its
generated frame says, of the re-point it did *not* make: *"18 of them inside its own held-out
sets and source, **where moving the binding moves the ruler with the sample**."* That sentence
is exactly right, and it is written about a hypothetical configuration while **29 of 29** such
faults are being reported from the shipped one, unremarked.

**What this does to V16's precision requirement.** The rung fails *"if the check does not state
its false-positive rate against a measured corpus."* The check states one, and it is honestly
measured — on held-out **sentences**. Its entire live production cost is a property of
**surface classes**, and a sentence-level precision figure cannot express it. The disclosure is
true and the reader is still misled: 29 faults read as 29 places the lab has misplaced an
entrant, and the correct number is **zero**.

### 4.6 **F6 — V16's own settlement is dated a day before the commit that made it, on two surfaces.**

`LADDER_V_TRIPLE_VERIFICATION.md:690` and the D48 row at `docs/DOCKET.md:241` both read:

> **[SETTLED 2026-08-11 by V16 round 10, subject `067caac0`. …]**

Executed with `git log -S` over `scripts/self_audit.py`, every artefact of that settlement
first appears at **`0c7b968d`, 2026-08-12T16:13:12Z**:

```
-S'_board_pin_date'                                            -> earliest 0c7b968d
-S'WHETHER ITS OWN BOARD IS STILL CURRENT'                     -> only     0c7b968d
-S'test_the_verdict_admits_it_cannot_tell_its_board_is_stale'  -> only     0c7b968d
```

Nothing of it exists at `067caac0` (2026-08-11T22:50:51Z). The settlement landed on
**2026-08-12**. The ledger row at `:816` is internally consistent and names `0c7b968d` as
round 10, so it dates the settlement correctly by implication while `:690` and D48 do not.

**The defect is not staleness, and that is why it is worth a row.** The date is not old; it is
**borrowed**. The settlement claim took its date from **the commit it graded** rather than from
**the act of settling**. That is the same family as D171's *"for three days"* — a date correctly
copied off the wrong event — and this lab has now produced it twice inside the same rung's
records. D171's ask already covers half the remedy (*a quotation carrying a commit is a claim
that must resolve at that commit*); extend it one step: **a claim carrying a date and a commit
must have the date agree with the commit.** Both halves are `git show`-checkable.

Consequence: `:816` uses the settlement to argue *"'self-graded' has been false since
2026-08-11"*. On the corrected date the sentence is off by one day, in the lab's own favour.
Small, and it is on the rung's own face.

### 4.7 **F7 — Offset-preserving masking and distance-based binding are incompatible: a masker built to REMOVE claims MANUFACTURES them.** *(NEW SHAPE)*

`_live_claim_text` blanks exempt regions **to spaces, preserving offsets**. Rule A binds by
**character distance** — `_PLACE_BIND = 40` for the subject walk, `_PLACE_ADJUDICATED = 400`
for the adjudication window. Blanking preserves *offsets* and destroys *separation*: prose that
held a name 200 characters away from an ordinal becomes 200 spaces, and the two become
adjacent.

Measured over the tracked corpus (18,974 surfaces opened), rule A at the **live** board, with
and without the masker:

| surface | live | live + mask | faults **created** by the mask |
|---|---|---|---|
| `campaign/LADDER_V_PASS3_COLD_2026-08-11.md` | 0 | **1** | 1 |
| `CLOSURE_EVALUATION_PROTOCOL.md` | 3 | **4** | **4** (all four are new; all three originals cleared) |
| `campaign/LADDER_V_TRIPLE_VERIFICATION.md` | 2 | **3** | 3 |

The created faults are legible and the mechanism is visible in each excerpt:

```
LADDER_V_PASS3_COLD:  "...Overall against Yang's (   §3.4): point rank 2, ... As scored: ,"
   -> 'rank 2' is bound to Yang           (blanking pulled the name into the 40-char window)

CLOSURE_EVALUATION_PROTOCOL: "| the paper linked from leaderboard rank 4 | | | 6 | Reissmann,"
   -> 'rank 4' is bound to Reissmann      (blanked TABLE CELLS collapsed two rows together)

LADDER_V_TRIPLE_VERIFICATION: "...are none of those: *  * — Wu & Zhang being **rank 2**..."
   -> 'rank 2' is bound to Wu             (the blanked quotation was what made it a quotation)
```

**So the aggregate is not a subset.** Re-pointing plus masking gives **40** faults where
re-pointing alone gives **79**, but the 40 are not 40 of the 79.

Two consequences, both load-bearing:

1. **F4's obvious remedy is unsafe as written.** Piping rule A through `_live_claim_text` does
   not simply subtract struck claims; on this corpus it invents at least eight faults across
   three files, three of them binding an ordinal to an entrant the sentence never mentions.
   The fix has to be a *separation-preserving* mask (delete-and-close, or a token barrier),
   not a blank-in-place one — and that is a different change from the one-liner.
2. **It bounds, and does not indict, the sibling.** Probed on both a struck third-party
   sentence and one of our own with a competitor's name behind a struck clause,
   `check_rank_claim_values` returned **0 faults** on each: `_VALUE_OTHERS_SUBJECT` requires
   the name adjacent to a copula and then `\s*$` immediately before the ordinal, so a run of
   blanks defeats the bind rather than forging it. The hazard is real for a **distance** bind
   and not demonstrated for an **adjacency** bind. Stated at that width rather than wider.

### 4.8 **F8 — The guard's own generated frame publishes a re-point cost that is stale by a factor of eight, and it is the number the chief ruling rests on.**

The frame line `check_board_placement_words` prints today reads:

> *"NOT re-pointed: the name-to-rank binding, deliberately — swapping it to the live board was
> measured across this corpus on 2026-08-14 and re-measured at `48d3f05a`, and **takes rule-A
> faults from 2 to 68** over DISJOINT sets … **50 of them dated records** this check cannot
> tell from a live claim (item 9) and 18 of them inside its own held-out sets and source."*

Re-measured today at frame `9dca4738`, over 18,974 opened tracked surfaces, `__pycache__`
purged, three configurations of rule A in one pass:

| configuration | faults | files |
|---|---|---|
| **PIN** — as shipped | **16** | 6 |
| **LIVE** — re-pointed, as the ruling contemplated | **79** | 33 |
| **LIVE + dated-context discriminator** — the ruling's own prerequisite, applied | **40** | 24 |

**The published "2" is now 16 — stale by a factor of eight.** The published "68" is now 79.
Both are generated into the verdict from a *typed* pair of constants describing a measurement
taken on 2026-08-14, in a file whose stated design principle is that figures are generated
rather than typed so they cannot go stale (L-79). That principle is applied to the pin's date
and entrant count in the same frame and not to these two numbers.

**And the ruling's quantitative ground does not survive.** *"50 of the 68 are correct dated
records"* implies a dated-context discriminator recovers roughly 74% of the re-point's cost.
Measured, `_live_claim_text` — which masks **more** than dated history, also clearing strikes,
quotations and code — clears **39 of 79, i.e. 49%**, leaving **40 faults standing**. Two
caveats stated rather than buried: the corpus moved between the two measurements (68 → 79), so
this is not like-for-like, and per F7 the post-mask set is not a subset. Neither caveat closes
the gap between 74% and 49%, and forty is not eighteen.

**What this means for the ruling.** Its condition has been met (§4.3) and its ground has not.
The correct conclusion is neither "re-point now" nor "the ruling stands": it is that **the
ruling's decision was made on a number nobody could check at the time and that can be checked
now**, and the answer is that re-pointing today still costs 40 faults rather than the ~18 its
own arithmetic implied. That is a live input to a decision the chief has reserved, and it did
not exist before this round.

---

## 5. FILED, NOT APPENDED TO THE RUNG (R-CONVERGE)

Found while grading V16, **outside its declared scope**, filed as docket rows and excluded
from the rung's verdict and from the new-material count.

- **The form/value census counted 34 checks where the tree holds 35, and the omitted one is
  `check_rank_claim_values`** — the check D174's own cited repair (`847b4492`) added.
  `len(self_audit.CHECKS)` by import is **35** at `847b4492`, `337dd62d`, `f2fa9cee` and
  `e98e40fe`, and **34** only at `82fb3d46`. The census graded the tree *before* its own cited
  repair and silently dropped a value-grader from the denominator. D174's B-count of 15 is
  independently reproduced; its membership takes two swaps
  (`check_fd_grades_current_standard` out, `check_declined_ladders_name_their_guard` in).
- **Empty selection is eighteen checks, not nine.** Re-derived by execution in throwaway
  repositories where the source exists, is non-empty, and the selector matches zero items; all
  eighteen returned `PASS`, each verdict recorded. Six are genuinely guarded
  (`ledger_integrity`, `ledger_stalls`, `bundle_drift`, `statistical_labels`,
  `fd_grades_current_standard`, and `withdrawn_numbers` by construction). This independently
  corroborates, by a different route and a different agent, the figure of 18 that the in-flight
  repair to `scripts/self_audit.py` states in its own D175 comment against D174's filed nine.
  **Two agents reaching the same 18 from opposite directions is the strongest single result in
  this round's supporting work, and it is not V16's.**
- **`check_cost_predictions` returns `INFO` unconditionally** and can never fault, so counting
  it among the value-graders overstates the graded set by one.
- **`scripts/self_audit.py` was dirty throughout this round**, carrying ~310 uncommitted lines
  from a concurrent agent implementing `_no_selection`. This round graded a detached worktree at
  `9dca4738` for that reason. The uncommitted hunks touch `check_closure_entry_of_record` and
  `_best_on_board_faults` — board-adjacent — but not `board_placement_faults`, `_placements`,
  `_board_names` or `_rank_value_faults`, so no finding in §3 or §4 turns on the difference.

---

## 6. THE PDF, AND A CORRECTION TO THIS ROUND'S OWN BRIEF

This round was briefed that *"`\sout{}` is strike-and-keep, so the withdrawn figures sit in the
text layer of a correctly repaired report exactly as they do in a stale one — 68% fourteen
times, 'rank 1 of 5' twice, in both. The only reliable read is visual."*

**The premise is true of the struck figures and false as a rule about the artifact**, and saying
so is worth more than the PDF finding itself — which is already **D91, D115, D145 and D177** and
is therefore **not counted as new here**.

The repair at `2cec44ee` did not only strike text. It **added** text: `rank 1 of 7`, `Yang`, the
six-entry board, and a new section *"The board moved on 2026-08-11"*. Counted in the shipped
`demo-output/website/latex/closure_challenge_report.pdf` with `pdftotext -layout`:

| token | in the shipped PDF |
|---|---|
| `68%` | **14** |
| `rank 1 of 5` | **2** |
| `rank 1 of 7` | **0** |
| `Yang` | **0** |
| `board moved on 2026-08-11` | **0** |

Absence of the additions is a **positive, text-layer discriminator** requiring no render. It is
**one-sided**, and that matters: absence proves the artifact stale; presence would *not* prove it
repaired, because `\sout{}` keeps both. The brief's rule is the right default and the wrong
universal.

**The visual read was done anyway, and is reported as the brief requires.** Page 1 was rendered
with `pdftoppm -png -r 110 -f 1 -l 1` and read as an image. It shows, in the Status box and again
in the Abstract, **`P(rank 1) = 68%`** and **`rank 1 of 5, scored locally`** set in **bold, with
no strikethrough rule anywhere on the page**, above a title block dated *7 August 2026*. That is
the pre-repair build, read directly rather than inferred.

**How every PDF claim in this document was read:** `pdftotext -layout` for enumeration and
counting; `pdftoppm` to PNG at 110 dpi with direct visual inspection for the strike/no-strike
determination, which the text layer cannot answer.

---

## 7. VERDICT

### 7.1 Does V16 close?

**No.**

| requirement, as written on V16's face | state |
|---|---|
| ordinals checked against a **parsed** board | **held** — the board is parsed, and driving a synthetic README moves the verdict |
| whole text, whitespace collapsed | **held** |
| **every ordinal this lab pins on an entrant** | **FAILS — F1.** Two of six live entrants, including the leader, are outside the recogniser's vocabulary in both directions |
| stated false-positive rate against a measured corpus | **held for the named guard; absent for the check that now owns half the criterion — F2.** And the rate it states cannot express its live cost — F5 |
| stated reach, measured on held-out sentences | held for the named guard; absent for the sibling — F2. The reach list's fourteen classes do not include F1 |
| generated-not-typed figures (L-79, the rung's own principle) | **FAILS — F8.** The re-point cost in the frame is typed and stale by 8× |
| conformance with ruling `04489465` | **unresolved on an expired ground — F3**, now measurable — F8 |
| conformance with the strike-and-keep house rule | **FAILS — F4**, and the obvious repair is unsafe — F7 |

### 7.2 Is this round BELIEF-NEUTRAL?

**No.**

**New material findings: 8** (F1–F8). **New shapes: 4.**

A round is neutral if it only executes or closes what was already known. This one *did* execute
five inherited findings — D151, D176, the value check with its 27 tests and 8 mutants, the
archive repair, and the `([], [])` pin — and all five held. Had it stopped there it would have
been neutral. It did not stop there.

Four of the eight are **shapes** rather than instances:

1. **F1 — split-referent vocabulary.** A guard whose **recogniser** and whose **oracle** are
   loaded from different sources. The pin supplies *who is an entrant*; the live record supplies
   *how many positions exist*; the sibling supplies *what everyone's rank is*. Nobody asked
   whether the first list was complete. The generalisation: when a check's recogniser and its
   oracle have different provenance, the difference is a **silent miss**, not a loud error — and
   **no precision or reach measurement can see it**, because both are computed over sentences the
   recogniser has already accepted.
2. **F2 — a pass requirement that a refactor walked out of.** The criterion named a check; the
   function was split; the requirement stayed with the name.
3. **F3 — a ruling that gates itself on a prerequisite, with nothing watching for the
   prerequisite's arrival.** Second instance in this rung's records; no mechanism after either.
   **F8 is its consequence**: the decision rested on a number nobody could check at the time, and
   when checked, it does not hold.
4. **F7 — offset-preserving masking versus distance-based binding.** A masker whose purpose is to
   remove claims manufactures them, because blanking preserves offsets and destroys separation.
   Measured, not argued: three files where the mask *adds* faults, including one where all four
   post-mask faults are new. **This shape invalidates the one-line remedy F4 invites**, which is
   why it is worth more than F4.

F5 is a shape too on one reading — a sentence-level precision figure cannot price a surface-class
cost — and is counted once, under F5. F4, F6 and F8 are material instances; F2 and F5 are
findings against the closing condition as written.

**What would falsify this verdict.** Any one of these, executed:

- **F1** — show rule A faulting a false ordinal pinned on Yang or Tian at frame `9dca4738`; or
  produce a surface, code comment or docket row written before 2026-08-15T20:56Z that names the
  pin-**membership** gap as distinct from the pin's **age** (D48 / item 12).
- **F2** — point to a false-positive rate or a held-out reach set stated by
  `check_rank_claim_values` in its verdict or BASIS. One `grep` settles it.
- **F3** — produce a surface recording that ruling `04489465`'s prerequisite was met; or show
  `_live_claim_text` is not the discriminator the ruling names, by showing it does not exempt a
  dated withdrawal banner (§4.4's fourth row is the test).
- **F4** — show `check_board_placement_words` masking struck text at any level.
- **F5** — re-run the check and get a fault on a surface that is not a record of the guard.
  Reproducible in 171–258 seconds.
- **F6** — produce an artefact of D48's disclosure settlement existing at or before `067caac0`.
- **F7** — show that the three mask-created faults are an artefact of this round's harness rather
  than of `_live_claim_text`; the three excerpts in §4.7 are quoted from the fault messages
  themselves and each names its bound entrant, so this needs the file, not an argument.
- **F8** — re-run the three-configuration sweep and get 2 / 68. The script is one pass over
  `_tracked_files()` calling `board_placement_faults` three times per surface.
- **The verdict as a whole** — show that three or more of F1–F8 were already recorded before this
  round. Each was checked against `git show HEAD:docs/DOCKET.md` before filing; the PDF finding
  **was** found already recorded (D91/D115/D145/D177) and is therefore excluded from the count,
  which is the discipline this falsifier asks for.

**Do not score neutrality early.** Round 10 was scored neutral and three new shapes appeared
within forty minutes. In this round F5 arrived from running the guard once, after the first four
findings were already written down, and F7 and F8 arrived from a sweep that had been launched to
settle a different question.

---

### 7.3 Docket rows filed by this round

| row | finding | in V16's scope? |
|---|---|---|
| **D189** | F1 — split-referent vocabulary; rule A cannot see Yang or Tian | yes |
| **D190** | F3 + F8 — `04489465`'s prerequisite met and unrecorded; the frame's `2 → 68` re-measured as `16 → 79`, and `40` after the discriminator | yes |
| **D191** | F7 — offset-preserving mask versus distance-based bind manufactures faults | yes |
| **D192** | F5 + F2 — 29 of 29 faults are records of the guard; the sibling excludes them by name; the precision requirement binds one of two checks | yes |
| **D193** | F6 — the borrowed date on V16's own face | yes |
| **D194** | the §5 items — D174's denominator is 35 not 34, empty selection is 18 not 9, `check_cost_predictions` cannot fault | **no — filed, not appended** |

**ANCHOR NOTE — the rows are in history under someone else's commit message.** All six
were written to `docs/DOCKET.md` at 21:2xZ and, before this round could commit them,
were swept into **`39c0e2bd`** — a commit by another agent whose message is about S6
items and `PRODUCT_LIST` and which names none of them (it also carries that agent's own
D184–D186). The single-step pathspec discipline protects *this round's commit* from
another agent's diff; it does not protect *this round's working-tree edit* from another
agent's `git add`. **So the docket rows and the round document that explains them are
carried by different commits, and the one carrying the rows does not mention them.** This
is the same class as `e933e31b`'s finding that authorship must travel in the artifact:
the rows themselves each name their frame, their date and their round, which is why the
attribution survives the sweep at all. Recorded rather than re-written, because
re-committing them would duplicate rows in an append-only register.

Two further defects of this round's own making, found by re-reading what was written:
**both new rows carrying a literal `|` broke their markdown table** — D189's
`\b(liu|montoya|reissmann|wu)\b` gave 8 cells and D191's quoted table-row excerpt gave 10,
where every other row has 5. Detected by counting `|`-delimited cells rather than by
looking, repaired by escaping, and re-verified with a split that ignores `\|`. A register
that is a markdown table has a mechanical well-formedness property and nothing checks it.

## 8. WHAT THIS ROUND DID NOT DO

- No solver ran. No scoring call was made; the ledger stands at **6**.
- Nothing was sent, uploaded, filed or registered. Submissions remain **PARKED**.
- The scoring pin `deb91557` was **not moved**, and F1's remedy is explicitly not to move it —
  the pin is correct and V1 needs it frozen. F1 asks for the recogniser's vocabulary, which is a
  different list from the oracle's ranks.
- Nothing under `dist/`, `demo-output/website/latex/`, `LAPTOP_SHOOT.md`, `motorbike-video/`,
  `.autostop-hold`, `scripts/self_audit.py`, `scripts/check_derived_figures.py`,
  `scripts/check_normative_clauses.py`, `docs/USING_THIS_LAB.md`, or any other agent's in-flight
  round document was written. `scripts/self_audit.py` was **read and executed**, never modified;
  all execution ran from a detached worktree at `9dca4738`, removed afterwards.
- The PDF was opened read-only and rendered into scratch. No PDF was written.
- **Note on the do-not-touch list**: it names `latex/*`, and per D181 no such path exists — the
  real prefix is `demo-output/website/latex/`. This round treated the intent as binding on the
  real path.

---

## 9. ADDENDUM 2026-08-15, by this round's own author — THE FOUR ARMS, MEASURED AFTER THE ROUND CLOSED

**Why this section exists, and it is the round's own defect first.** §0.4 said the
untracked, gitignored and run-tree arms *"were NOT measured by this round."* That was true
when written and **false 66 minutes later**. This round had itself dispatched a four-arm
census; it ran for 5,815 seconds and returned **after the round was committed at
`94419cc8`**. Writing a negative about my own coverage while work I had commissioned was
still in flight is the **D141 shape — a claim stale against another region of its own
document** — committed inside a round that files D193 against a borrowed date. It is struck
in §0.4 rather than rewritten, and the numbers are here.

**The verdict does not move. No finding F1–F8 depends on an arm count**; all eight are
properties of the guard, established by driving it directly. What follows is corroboration,
one correction to the record, and one new lead.

### 9.1 The board, corroborated by a route this round did not use

§2 read the boards out of `_published_board()` and `_ranking_board()`. The census went the
other way — to the file on disk — and agrees:

- The parser at `scripts/self_audit.py:3188` reads `$CLOSURE_BENCHMARK_DIR/README.md`;
  **`CLOSURE_BENCHMARK_DIR` is unset**, so it resolves to
  `/home/ubuntu/closure-challenge-benchmark/README.md`. Verified here directly:
  `git -C /home/ubuntu/closure-challenge-benchmark rev-parse HEAD` →
  **`deb91557184af3cb95f5190494ec52d8f2c6a0d1`**.
- That README states **four** entrants — Reissmann 0.0595, Wu 0.0624, Liu 0.0737,
  Montoya 0.0779 — yielding exactly the keys §2 read out of the parser.
- The six-entry live board (Yang 0.0580 … Tian 0.0641 …) lives in
  `sdk/scripts/probability_of_rank.py::LIVE_BOARD` and `BOARD_MOVED_2026-08-11.md`.

**So F1's premise is now established from both ends**: the four-name recogniser comes from a
file on disk pinned at `deb91557`, and Yang and Tian are absent from that file — not merely
absent from a dict this round happened to print.

### 9.2 The arm counts

| arm | frame | size | `rank N of M` | `rank-N entry` | board surnames |
|---|---|---|---|---|---|
| tracked | `e98e40fe` | 20,702 files | 53 f / 209 l | 35 f / 79 l | 213 f / 1,672 l (`-I`, all 12 surnames) |
| untracked | **volatile** | 1 → 4 → 1 | see §9.4 | | |
| gitignored | 22:33Z | 37,245 files / 37.9 MB | 92 f / 97 l | 2 f / 3 l | 11 f / 86 l (`-I`) |
| run tree | 21:08Z | 132,049 files / 75.8 GB | **0** | 1 f / 1 l | — |

**The run-tree >2 MB set is 6,108, confirmed by independent re-count** (60.67 GB; 125,941
files ≤2 MiB holding 15.12 GB). The brief's 10,526 is stale and the 6,108 it offered is
**measured rather than inherited**, which is what the rule asks. The unit matters: >2,000,000
decimal bytes gives 6,280.

**The run tree carries no rank claim at all.** Every `rank N` hit in 75.8 GB is an **MPI
rank** in a `checkTotals` log. The single genuine ordinal-on-entrant phrase in the whole
tree is `w3-qcr-duct/PREDICTION.md:16` — *"from Spalart 2000 as the rank-2 entry adopts
it"*. A 13-minute and an 18-minute prefilter pass to establish a near-empty set is the
honest cost of not inheriting a number.

### 9.3 The one new lead — and it sharpens F2 rather than adding to the count

The census flagged **`rank 2 of 0` ×2** as a possible defect. Run down here by execution:

```
_VALUE_BOARD_SIZE.search("seed, against a gap to rank 2 of 0.0030.")
  -> matches 'rank 2 of 0'   n='2'  v='0'
```

The real text at `demo-output/website/latex/closure_challenge_report.tex:1890` is *"against a
gap to **rank 2 of 0.0030**"* — where `of 0.0030` is a **margin**, not a denominator. The
`\b` after `\d{1,3}` falls between `0` and `.`, so the pattern reads the first digit of a
decimal as a board size.

**Live or latent? Latent, and exactly one gate deep.** Executed on the real file,
`check_rank_claim_values` returns one fault and it is a genuine best-on-board fault at
`:871`; the `rank 2 of 0` match produces nothing. The reason is **not** the strike masker —
`_live_claim_text` leaves the passage byte-identical — it is `_in_board_context` returning
`False`, a proximity window over board vocabulary. **Add the word "board" or "leaderboard"
within that window — entirely natural in a document about the leaderboard — and the check
faults a margin as a denominator on a shipped surface.**

**This does not become F9.** It is one instance of a class, it is latent, and the count
stays at **8**. What it does is give **F2** a demonstrated example rather than an argument:
the check that publishes **no false-positive rate** has a false-positive class reachable by
adding one common word. And independently, `RULE_O_DENOMINATOR_MEASUREMENT_2026-08-15.md:308`
— another agent's document, written concurrently — already names this same string as a parse
error and reports a **58.3% FP rate** for denominator matching. **That is F2's remedy
arriving from somewhere else while V16's own face still does not require it**, which is the
argument for attaching the requirement to the function rather than to a check's name.

### 9.4 The untracked arm contained this round's own draft — a methodological note

The census measured Arm 2 three times and got three answers: **1 file** at 20:58Z, **4** at
21:12Z, **1** at 22:33Z. The 21:12Z set included
`demo-output/website/campaign/LADDER_V_V16_ROUND11.md` — **this document, at 723 lines,
before it was committed** — alongside two other agents' uncommitted work.

Two things follow, and the second is the durable one:

1. **Arm 2 cannot be quoted without a timestamp.** A count of "~1 untracked file" is not a
   property of the repository; it is a property of the minute.
2. **The auditor's own draft was inside the corpus under audit.** For 34 minutes, a sweep of
   the untracked arm for rank claims would have returned this round's findings as corpus
   hits — including every probe sentence in §3.2 and §4.1, which are deliberately false
   statements about entrants written down to be faulted. That is F5's shape (*an instrument
   measuring its own paperwork*) reaching one level further out: **not the guard measuring
   its own test fixtures, but the audit measuring its own unfinished report.** The census
   noticed it; nothing mechanical would have.

### 9.5 What this addendum does and does not change

- **§0.4 is struck and corrected.** The round's coverage claim was wrong about itself.
- **§2, §4.1 corroborated** from the file on disk rather than the parser's return value.
- **The brief's run-tree figure is now measured**, twice, and 6,108 stands against 10,526.
- **F2 gains a demonstrated false positive**; the new-material count stays at **8** and the
  belief-neutral verdict stands at **NOT NEUTRAL**.
- **No falsifier in §7.2 is affected**; every one remains executable as written.
