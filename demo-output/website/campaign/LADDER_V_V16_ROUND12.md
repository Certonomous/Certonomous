# Ladder V — V16, GRADE ROUND 12

**Verdict: V16 does NOT close this round, and the round is NOT belief-neutral.**
**Five new material findings, three of them new shapes.** R-VALUE's consecutive-neutral
count stays at **zero**.

Graded at frame **`fdfc3eba`** (2026-08-16T17:27:09Z), in a detached worktree at that
commit, because nine tracked files were dirty in the main checkout — including
`LADDER_V_TRIPLE_VERIFICATION.md`, which is one of the surfaces this round sweeps.
`scripts/self_audit.py` itself was byte-clean against HEAD (`git diff HEAD --` empty), so
the subject was not in flight; the worktree isolates the *corpus*, not the guard.

**The round was dispatched on a premise, and the premise is false for this rung.** The
brief held that `567c7aa6` moved the rank-claim guard, so *"a precision or reach figure for
the guard measured before `567c7aa6` is measured against a different guard."* Measured:
`567c7aa6` changed exactly three module-level names and **none of them is reachable from
`check_board_placement_words`**. §3 is that measurement and §5.1 is what the misrouting
means, which is more interesting than the answer.

---

## 0. THE FRAME

### 0.1 Independence — from the dispatch record, and not from git

Under R-ISOLATE the grader must not be an author of the subject. **Git cannot establish
that here**: one Ubuntu identity signs essentially the whole history, and
`scripts/check_rung_attribution.py` names a *session*, not an agent (D173). What
establishes it is the per-agent dispatch record at
`~/.claude/projects/-home-ubuntu-Certonomous/64b13819-…/subagents/`:

| field | value |
|---|---|
| this grader's agent id | `ae0ce79e959ec8ea0` |
| `meta.json` description | `Run V16 round 12` |
| first action | **2026-08-16T17:27:13Z** |
| newest commit in the subject at dispatch | `fdfc3eba`, **2026-08-16T17:27:09Z** |

Every commit in the graded range predates this agent's first action — the margin on the
newest is **four seconds**, which is stated rather than rounded up, and the two commits
that matter most to this round's findings (`567c7aa6` at 17:13:02Z, `c2cd83bf` at
17:25:49Z) predate it by 14 minutes and 84 seconds respectively.

**This evidence is untracked and per-machine (D130).** No reader of this repository can
re-derive it; it will not travel with the commit carrying this document. That is a defect
of the lab's independence apparatus, not of this round, and it is stated rather than
worked around.

### 0.2 Scope, declared before any finding (R-CONVERGE)

V16's last graded round was **round 11**, whose frame was `9dca4738`. Scope is therefore
**`9dca4738..fdfc3eba`**, enumerated mechanically before grading began:

| measure | count | how |
|---|---|---|
| commits in range | **71** | `git rev-list --count 9dca4738..fdfc3eba` |
| files changed | **81** | `git diff --name-only … \| wc -l` |
| commits touching `scripts/self_audit.py` | **5** | `git log --format=%h … -- scripts/self_audit.py` |
| net lines into `scripts/self_audit.py` | **+1,292 / −36** | `git diff --stat 9dca4738 fdfc3eba --` |
| module-level names in it whose source changed at `567c7aa6` | **3** | AST diff, §3.2 |
| docket IDs **at frame `fdfc3eba`** | **248 distinct**, min D1, max D249, one gap (D188) | `^\| *[*~]*D(\d+)` over `git show fdfc3eba:docs/DOCKET.md` |

No docket-row TOTAL is quoted anywhere in this document as a standalone figure: the count
above is stated with the regex that produced it and with its frame, because bold and struck
IDs match or fail to match depending on the pattern, and two regexes give two answers.

**On the rung, in scope:** `check_board_placement_words` and its rule A/B core
`board_placement_faults`; the sibling `check_rank_claim_values`; the board referents
`_published_board`, `_ranking_board`, `_live_ranks`; the blind-spot derivation
`_blind_placement_binding` / `BLIND_DERIVED` / `_derived_blind_spot`; the two held-out
precision sets; and V16's own face and ledger row.

**Findings outside that boundary are FILED as append-only docket rows and are not appended
to the rung.** §6 lists them and says so for each.

### 0.3 Method, and the controls every count here rests on

Three false zeros were measured in this lab in the preceding day, all inside instruments
built to hunt this exact class. This round's controls are therefore stated before its
numbers:

- **Every plant is made BY LINE INDEX, never by anchor string**, and **confirmed by
  readback from disk after the write and before the run**. §3.1 is the control table.
- **A struck negative control is included**: a plant that lands, is confirmed present, and
  must NOT move the figure. It did not.
- **No zero is reported without a live control.** The precision measurement's own positive
  controls (5 author, 4 grader "must fault" sentences) are reported beside every figure,
  and the two "must stay silent" controls beside them.
- **`__pycache__` purged before every cell.** `PYTHONDONTWRITEBYTECODE` does not fix stale
  bytecode here; the directories are removed.
- **The board is re-derived, never quoted** (defect class B4) — §2.
- **`git grep -a`** where a text sweep was needed; the interactive `grep` is
  `ugrep --ignore-files` and a shell function besides.
- **No guard's silence is cited as evidence.** Where the guard is quoted, the quotation is
  reported as a fact *about the guard* and the underlying question is re-derived.

### 0.4 Scope drift, measured — and the ID space moved under this round exactly as it moved under round 11

HEAD advanced **`fdfc3eba` → `b917f56d`** while this document was being written: **18
commits** in roughly 26 minutes. Every number in this document is stated at frame
`fdfc3eba` unless it says otherwise, and one thing was re-checked rather than assumed:

- **`scripts/self_audit.py` was NOT touched in `fdfc3eba..b917f56d`** (`git log --oneline …
  -- scripts/self_audit.py` empty), so **every measurement in §3, §4 and §5 still holds at
  the later HEAD.** The guard did not move under the round that was grading it.
- **The V16 ledger row was byte-identical across the drift** — only its line number moved,
  980 → 1007, as the file grew by 30 lines. Verified by extracting the row from both
  commits and comparing, not by trusting the line number.

**The docket ID space moved under this round TWICE, and the in-write assertion caught it
both times.** The rows were allocated three times before they landed:

| attempt | chosen against | block | outcome |
|---|---|---|---|
| 1 | `fdfc3eba`, max D249 | **D250–D254** | **taken** — another agent held D250–D258 by the time the rows were ready |
| 2 | `b917f56d`, max D258 | **D259–D263** | **taken** — D259–D261 were allocated in the minutes it took to write the commit message |
| 3 | `9ea438fb`, max D261 | **D262–D266** | **landed**, at `995e8547` |

The compare-and-swap asserts each target ID free *inside the same read-modify-write as the
append*, against HEAD's own blob and never against the worktree copy, so both collisions
produced an abort rather than a duplicate. **This is the standing hazard, observed live
twice in one round** — and a sibling commit inside the very same drift window,
`38844271`, is titled *"The docket IDs my grade named were claimed by another agent between
choosing them and landing them, so the grade cites three rows that are not the three that
exist."* **That is the failure this round avoided only by re-reading the register
immediately before writing, and then rewriting this document to the IDs that actually
landed rather than the ones it had planned.** The re-read is not optional, and neither is
the rewrite: a round document naming a block it did not get is the same defect as the
commit above, one step later.

### 0.5 What this round did NOT measure

The untracked, gitignored and run-tree arms were not swept by this round, and no number is
quoted for them. Every finding below is a property of the guard, established by driving it
directly, and none depends on an arm count. Saying "not measured" is the point of the rule
— and it is said here rather than 66 minutes late, which is the correction round 11 had to
make against itself in its own §9.

---

## 1. WHAT V16 REQUIRES, READ AS WRITTEN

From `LADDER_V_TRIPLE_VERIFICATION.md`, V16's face:

1. **The predicate.** *"Every ordinal this lab pins on an entrant is checked against the
   published board, which is parsed from the benchmark's own README table rather than
   transcribed"*, over **whole text with whitespace collapsed**.
2. **The guard and its tests.** `scripts/self_audit.py::check_board_placement_words`;
   `sdk/tests/test_rank_claim_surfaces.py`.
3. **Precision is a pass requirement, not a nicety** — *"the rung fails if the check does
   not state its false-positive rate against a measured corpus and name the senses of the
   word it excludes."*
4. **Stated REACH is a pass requirement too** — *"the check must declare what its patterns
   cannot phrase, measured on held-out sentences rather than asserted, because a
   replacement whose stated reach is less honest than its predecessor's is the failure V16
   exists to fix."*

Requirement 4 is the one this round turns on, in both directions: §5.2 finds the guard
**more** honest than round 11 credited it, and §5.3 finds the mechanism carrying that
honesty **unable to run** when its evidence goes missing.

---

## 2. GROUND TRUTH, RE-DERIVED RATHER THAN QUOTED

`ast.literal_eval` on the `LIVE_BOARD` assignment node in
`sdk/scripts/probability_of_rank.py` — the module is **not imported** — joined to
`official_test_harness_result.round5_per_case_full` in
`demo-output/website/closure_challenge_round5_qcr.json`:

```
entrants 6  ->  7 positions counting us
per-case ranks   2,2,1,1,3,4,4,7  of 7
best-on-board    2 of 8            (earned by our model: 0 of 8)
overall rank     1 of 7
```

This reproduces the brief's ground truth on every ordinal. **One figure did not
reproduce, and it is a distinction rather than a disagreement.** The brief gives the
margin as `0.001365`. Re-derived:

| margin basis | value | seed bound 0.002419 as % |
|---|---|---|
| `published_overall['Yang']` − ours | **0.00135281** | 178.81% |
| mean of Yang's eight per-case values − ours | **0.00136531** | 177.18% |

Both are admissible and the guard itself publishes the pair as an interval — its own frame
reads *"[177.12%, 178.82%] over **3** admissible margin bases"*. A bare `margin 0.001365`
names neither basis and is the smaller-looking of the two. Filed, out of scope — §6.

The three referents, read from the module at HEAD rather than transcribed:

```
_published_board() -> {'reissmann':1,'wu':2,'liu':3,'montoya':4}   pin deb91557
_ranking_board()   -> {'yang':1,'reissmann':2,'wu':3,'tian':4,'liu':5,'montoya':6}
_live_ranks()      -> {'':1,'Yang':2,'Reissmann':3,'Wu':4,'Tian':5,'Liu':6,'Montoya':7}
```

Three referents, three membership sets, one module — unchanged from round 11 §2.

---

## 3. THE ASSIGNED QUESTION: DOES ROUND 10's 71% STILL HOLD AT HEAD?

### 3.1 It holds, at `fdfc3eba`, measured by execution with a live plant control

Both held-out sets were driven directly against `board_placement_faults` at HEAD under the
one admission predicate round 10 settled on (`_placements`), rather than read off
`_PLACE_PRECISION`:

| row | admitted | falsely faulted | rate | positive controls missed |
|---|---|---|---|---|
| author (`campaign/V16_PRECISION_SET.py`, holds 41) | **28** | **20** | **71.4%** | 0 of 5 |
| grader (`campaign/V16_GRADE_ROUND7_PRECISION_SET.py`, holds 43) | **25** | **19** | **76.0%** | 0 of 4, 0 silent controls faulted |

**Spread 5 points**, exactly as round 10 settled it. Under the superseded raw-match rule
the author's row is 20 of 41 = 48.8%, reproducing the 49% that rule used to publish. The
pad check (`matches_a_pattern`) returns empty: no sentence in the author's set is one the
guard never looks at.

**The figure is invariant across every commit that moved the guard since round 10.**
Measured at each, with the three files materialised by `git show` rather than checked out:

| commit | date | author | grader |
|---|---|---|---|
| `0c7b968d` (round 10's settlement) | 2026-08-12T16:13:12Z | 20/28 71.4% | 19/25 76.0% |
| `1449557a`, `d2d6bd6c`, `e01dfdf6`, `9af7e2d3` | 08-12 → 08-15 | 20/28 71.4% | 19/25 76.0% |
| `847b4492`, `fb30e00f`, `0a3e82d7`, `f4c531cb`, `49b36e57` | 2026-08-15 | 20/28 71.4% | 19/25 76.0% |
| **`567c7aa6`** | 2026-08-16T17:13:02Z | **20/28 71.4%** | **19/25 76.0%** |
| **`fdfc3eba` (HEAD)** | 2026-08-16T17:27:09Z | **20/28 71.4%** | **19/25 76.0%** |

**A flat line across twelve commits is the shape a false zero takes, so the instrument was
controlled before the line was believed.** Plants by line index into HEAD's
`scripts/self_audit.py`, each confirmed by readback from disk before the run:

| plant | line | readback | author row | verdict |
|---|---|---|---|---|
| BASELINE | — | — | 20/28 71.4% | baseline |
| `_PLACE_BIND = 40` → `400` | 3067 | `_PLACE_BIND = 400` | **25/28 89.3%** | **LIVE** (+17.9 pts) |
| `_PLACE_BIND = 40` → `4` | 3067 | `_PLACE_BIND = 4` | **11/28 39.3%** | **LIVE** (−32.1 pts) |
| `_PLACE_OVER = 5` → `0` | 2383 | `_PLACE_OVER = 0` | 20/28 71.4% | did not move the rows (moved a grader control 0→1) |
| `_PLACE_ADJUDICATED = 400` → `100000` | 3068 | `_PLACE_ADJUDICATED = 100000` | 20/28 71.4% | did not move |
| **N1 struck negative control** — a comment line | 3069 | `# ROUND12 STRUCK NEGATIVE CONTROL: …` | 20/28 71.4% | **correct: planted, confirmed, unmoved** |

Two plants move the figure by 18 and 32 points. **The instrument is live and the flat line
is a real invariance.** The two that did not move it are reported rather than dropped:
`_PLACE_ADJUDICATED` moves nothing because no admitted sentence in either set carries a
second, pin-side placement anywhere in it, and `_PLACE_OVER` governs recall rather than
false faults — it moved a *positive control*, which is the arm it belongs to.

### 3.2 `567c7aa6` does not reach V16's guard — measured as a call closure, not read off the diff

The transitive callee closure of each entry point was built over the module AST at HEAD and
intersected with the module-level names whose source text differs `49b36e57..567c7aa6`.
**That commit changed exactly three names:** `_BEST_COUNT`, `_BEST_SOFT_WRAP`,
`_blind_best_on_board`.

| entry point | names reached | touched by `567c7aa6` |
|---|---|---|
| **`check_board_placement_words`** | 67 | **NONE** |
| **`board_placement_faults`** | 30 | **NONE** |
| `_blind_placement_binding` | 17 | NONE |
| `check_rank_claim_values` | 54 | `_BEST_COUNT`, `_BEST_SOFT_WRAP` |
| `check_closure_entry_of_record` | 26 | `_BEST_COUNT`, `_BEST_SOFT_WRAP` |
| `_best_on_board_faults` | 12 | `_BEST_COUNT`, `_BEST_SOFT_WRAP` |

**So the answer to the question this round was sent to settle is: round 10's 71% holds at
HEAD `fdfc3eba`, it was never at risk from `567c7aa6`, and it is measured against the same
guard round 10 measured.** The soft-wrap widening and the digit-boundary guard
`(?![.,]\d)` land in `_BEST_COUNT`, which V16's named guard does not call. The brief's
warning was correct in general and wrong about this rung — and §5.1 is why that is a
finding rather than a footnote.

---

## 4. INHERITED FINDINGS, RE-EXECUTED RATHER THAN READ

Round 11 left eight findings. Four were re-executed at HEAD; **three held, one changed
sign.**

### 4.1 F1's BEHAVIOURAL half — **CONFIRMED at HEAD.**

Rule A driven directly at `fdfc3eba`, one sentence each:

| sentence | true? | rule A |
|---|---|---|
| Yang is rank 6 on the live board. | FALSE (Yang is 1) | **0 faults** |
| The rank-3 entry, Yang's model, leads the field. | FALSE | **0 faults** |
| Tian is rank 1 on the live board. | FALSE (Tian is 4) | **0 faults** |
| The rank-2 entry, Tian's model, leads the field. | FALSE | **0 faults** |
| **CONTROL** — The rank-2 entry, Liu's model, leads the field. | — | **1 fault** |
| **CONTROL** — The rank-3 entry, Wu & Zhang's SST-QCRC… | — | **1 fault** |

Two live controls fault; four false ordinals on Yang and Tian do not. **Rule A remains
structurally incapable of faulting any ordinal pinned on the board's leader.** F1's
behavioural half stands, and V16's predicate row still fails on it.

**F1's DISCLOSURE half does not stand — see §5.2, which is this round's principal finding.**

### 4.2 F2 — the sibling states no precision and no reach. **CONFIRMED, by F2's own falsifier.**

Round 11's falsifier read: *"point to a false-positive rate or a held-out reach set stated
by `check_rank_claim_values` in its verdict or BASIS. One `grep` settles it."* Executed —
the check was run live at HEAD and its generated `frame` (1,236 characters) counted:

| token | occurrences in the sibling's frame |
|---|---|
| `false-positive` / `false positive` | **0** |
| `precision` / `PRECISION` | **0** |
| `held-out` | **0** |
| `reach` / `REACH` | **0** |
| `BLIND TO` | **0** |

There is no `_VALUE_PRECISION`, `_VALUE_REACH` or `_VALUE_FALSE_FAULT` in the module at
HEAD. **F2 is unrepaired**, and §5.1 sharpens it into a demonstrated cost.

### 4.3 F5 — **CHANGED SIGN. Its own falsifier is now SATISFIED.** See §5.4.

### 4.4 F8 — the typed re-point cost. **CONFIRMED, and now falsifiable from one run.** See §5.5.

---

## 5. NEW MATERIAL FINDINGS

### 5.1 **G1 — F2's cost, demonstrated on a live dispatch: the rung names a CHECK, the work follows the FUNCTION, and a correct warning routed to the wrong guard.** *(NEW SHAPE)*

Round 11's F2 argued that V16's precision and reach requirements name
`check_board_placement_words`, that the criterion's *function* was split across two checks
at `847b4492`, and that **a pass requirement a refactor can walk out of is an R-CONVERGE
question**. It was argued rather than demonstrated, and round 11 said so.

It is now demonstrated, and the demonstration is this round's own dispatch. The brief
reasoned, correctly, that *the rank-claim guard moved tonight, therefore V16's precision
and reach figures must be re-measured against the new guard.* Every clause of that is true
of the thing that moved. **But the thing that moved is `check_rank_claim_values` and
`check_closure_entry_of_record` (§3.2), and the figures V16 makes a pass requirement belong
to `check_board_placement_words`, which did not move.** The warning arrived at the rung
whose numbers were safe and did not arrive at the check whose numbers do not exist.

**The shape, which is the durable half:** *when a rung's pass criterion is attached to a
check's NAME and the criterion's function is later split, every downstream reader — human
or brief — inherits the misrouting, and the misrouting is invisible because both checks are
in the same file and both are about rank claims.*

And the direction of the error is the expensive one. `567c7aa6`'s own message reports that
it measured the widened rule on the travelling arm and found *"false positives holding at
0"*. **That is a false-positive measurement, taken on the check that publishes none, and it
was written into a commit message rather than into the check's verdict** — where
`_PLACE_PRECISION` would have put it for the sibling. The number exists. It does not reach
a reader of the report, because the requirement that would have made it reach one is
attached to the other check's name.

### 5.2 **G2 — Round 11's F1 disclosure half was already false at round 11's own frame: the guard states the Yang gap, in a second reader-facing channel the grade did not read.** *(NEW SHAPE)*

Round 11's F1 was scored as a NEW SHAPE on two claims:

> *"The guard's own 'WHAT IT CANNOT SEE' list runs to fourteen enumerated classes — …— and
> does not contain this one."* … §7.1: *"The reach list's fourteen classes do not include
> F1."*

and its own falsifier invited exactly this rebuttal:

> *"produce a surface, code comment or docket row written before 2026-08-15T20:56Z that
> names the pin-**membership** gap as distinct from the pin's **age** (D48 / item 12)."*

**Executed.** `scripts/self_audit.py::_blind_placement_binding` was introduced at
**`9af7e2d3`, 2026-08-15T19:31:04Z — 85 minutes before round 11's first action** — and
`git show 9dca4738:scripts/self_audit.py` contains it. Driven at three frames through the
reader's own code path (`BASIS` + `_derived_blind_spot`, as `self_audit.py:8639-8645`
prints it), with the board referents held fixed because both are unchanged across the whole
range:

| frame | date | the line a reader gets |
|---|---|---|
| `9af7e2d3` | 2026-08-15T19:31:04Z | names tian ✓ yang ✓ CURRENT LEADER ✓ |
| **`9dca4738`** — **round 11's own frame** | 2026-08-15T20:54:47Z | **names tian ✓ yang ✓ CURRENT LEADER ✓** |
| `fdfc3eba` (HEAD) | 2026-08-16T17:27:09Z | names tian ✓ yang ✓ CURRENT LEADER ✓ |

The line, verbatim, at round 11's frame:

> **BLIND TO (measured now):** …*"And **NO sentence about tian, yang can be faulted by rule
> A**: the identity binding is built from the 4-entry scoring pin and those 2 entrant(s)
> are **not in it** — and **yang is the board's CURRENT LEADER**, so in the shipping
> configuration this check cannot fault any sentence about the entrant in first place."*

That names the pin's **membership** (*"not in it"*), distinguishes it from the pin's
**age** (item 12, *"WHETHER ITS OWN BOARD IS STILL CURRENT"*, a separate item in the same
report), and flags the leader. **F1's falsifier is satisfied on its own terms.**

**Why round 11 missed it, and this is the durable half.** The report prints **two**
blind-spot lines per check, from two different sources:

- `BLIND TO:` — the **typed** half, `BASIS[name][2]`, whose enumeration is the "(1)…(12)"
  list carried in the check's `frame`. Round 11 read this one. It does not name Yang.
- `BLIND TO (measured now):` — the **derived** half, `BLIND_DERIVED[name]()` via
  `_derived_blind_spot`. Round 11 did not read this one. It names Yang.

Round 11 inspected the check's `frame` string and the enumerated list, found no Yang, and
concluded the guard had not disclosed the gap. **The guard had disclosed it, generated
rather than typed — which is the L-79 discipline V16 itself mandates — in the channel built
for exactly that purpose.** The commit that built it is titled *"Thirty blind spots the
audit had written down and never once shown anybody"*; the mechanism it added to show them
is the one the next grade did not look at.

**Consequences, stated at their true width:**

- V16's requirement 4 (stated reach) is **satisfied for the named guard on this class**.
  Round 11's §7.1 row *"The reach list's fourteen classes do not include F1"* is
  **falsified**.
- Round 11's F1 **survives as a behavioural finding** (§4.1) and V16's predicate row still
  fails on it. What is falsified is the disclosure half and the NEW SHAPE status.
- Round 11's new-shape count drops from **4 to 3** and its material count from **8 to 7**.
- **This is round 11's own F5 shape reaching one level further out.** F5 was *an instrument
  measuring its own paperwork*. This is *an audit of an instrument reading one of the
  instrument's two disclosure channels and reporting the silence of the other as the
  instrument's silence.* A grader that reads a check's `frame` is reading a summary, and
  R-ISOLATE part 3 says a grader executes rather than reads a summary — the summary here
  belonged to the subject, not to a person, which is why it did not look like one.

### 5.3 **G3 — The B1 guard inside the blind-spot derivation is UNREACHABLE in every way its evidence can go missing.** *(NEW SHAPE)*

`_blind_placement_binding` carries an explicit, carefully argued guard against defect class
B1 — *the empty set is not agreement*:

```python
try:
    board, _ = _published_board()
    ranking = _ranking_board()
except Exception:
    return ("which entrants the identity binding covers could not be read, …")
live = dict(ranking[0]) if isinstance(ranking, tuple) else dict(ranking or {})
# THE EMPTY SET IS NOT AGREEMENT (defect class B1). An unreadable or empty
# ranking referent makes `unreachable` empty, and the sentence "every live
# entrant is in the identity binding" is then TRUE AND VACUOUS …
if not live:
    verdict = ("the ranking referent is EMPTY or unreadable, so this check "
               "cannot say whom it is unable to fault -- and that is NOT "
               "the same as being able to fault everybody")
```

**`_ranking_board()` does not raise when its referent is unreadable — it returns
`(None, message)`.** So the `except` never fires, and `dict(ranking[0])` is `dict(None)`,
which raises `TypeError` on the line **before** `if not live:` is evaluated.

Driven at HEAD with the referent path varied through `$CERTONOMOUS_RANKING_RECORD`,
positive control first:

| configuration | `_ranking_board()` | `_blind_placement_binding()` | B1 branch reached? |
|---|---|---|---|
| **POSITIVE CONTROL** — real referent | 6 entrants | OK, names tian/yang/LEADER | n/a (correct path) |
| A — referent path missing | `(None, 'not readable at …')` | **raises `TypeError`** | **NO** |
| B — referent file empty | `(None, '0 table(s) … satisfy')` | **raises `TypeError`** | **NO** |
| C — referent present, no board table | `(None, '0 table(s) … satisfy')` | **raises `TypeError`** | **NO** |

**The B1 sentence is dead code. It cannot be reached by any of the three ways its own
evidence goes missing.**

**The finding is bounded, and the bound is stated rather than buried.** This is *not*
fail-open. The consumer `_derived_blind_spot` catches, and a reader gets:

> *"the extent of this blind spot could not be measured (TypeError: 'NoneType' object is
> not iterable); it is not thereby smaller"*

which is honest, and `check_board_placement_words` itself returns **WARN with 48 faults in
all four configurations** — the check's verdict does not move at all. So the cost is that
the reader is told a *type error* instead of the sentence written for them, and the
specific claim *"that is NOT the same as being able to fault everybody"* never reaches
anybody.

**The shape:** *a guard written against a failure mode, defeated by its own dependency's
error CONVENTION — the dependency reports failure in its return value, and the guard was
written as though it reported failure by raising.* The `except Exception` above it proves
the author expected the raising convention. Nothing tested the branch, because testing it
requires making the referent unreadable, which is the one state no fixture had.

### 5.4 **G4 — F5 has changed sign: the guard's live faults are no longer all records of the guard, and the two that are not are TRUE of the live board.**

Round 11 ran the guard and found **29** lab-record faults across 7 files, and made a strong
claim about all of them:

> *"**Not one of the 29 is a claim this lab is making about the board.** Every one is a
> quotation of the guard's own behaviour… The instrument is measuring its own paperwork."*

with the falsifier: *"F5 — re-run the check and get a fault on a surface that is not a
record of the guard."*

**Re-run at HEAD, in the clean worktree: `WARN — every travelling surface agrees with the
board; 48 lab record placement(s) do not.** 34 rule A, 14 rule B, across 10 files:

| file | round 11 | HEAD | what it is |
|---|---|---|---|
| `docs/DOCKET.md` | 10 | **14** | rows recording this guard's defects |
| `campaign/LADDER_V_V16_ROUND11.md` | — | **13** | **round 11's own document** |
| `sdk/tests/test_fault_message_matches_rule.py` | 8 | 8 | the guard's own test file |
| `campaign/LADDER_V_V15_ROUND7.md` | 3 | 3 | a round grading this guard |
| `sdk/tests/test_two_board_referents.py` | 3 | 3 | the guard's own test file |
| `docs/INSTRUMENT_INTEGRITY_LEDGER.md` | 2 | 2 | the ledger row about this guard |
| `scripts/self_audit.py` | 2 | 2 | the guard's own source comments |
| `campaign/MARGIN_PRECISION_INTERVAL_2026-08-15.md` | 1 | 1 | a measurement record |
| **`LADDER_V_TRIPLE_VERIFICATION.md`** | — | **1** | **the ladder's V10 narrative** |
| **`LADDER_V_V10_CLOSURE_2026-08-16.md`** | — | **1** | **V10's closure document** |

**The falsifier is satisfied.** Two faults now sit on surfaces that are not records of this
guard, and both are the same claim:

```
LADDER_V_TRIPLE_VERIFICATION.md: 'placed 2nd' is bound to Reissmann, whom the published
  board puts at rank 1:  "…those are Reissmann's duct values, and Reissmann placed
  2nd/2nd/2nd of seven; the live duct leader was Yang…"

LADDER_V_V10_CLOSURE_2026-08-16.md: 'placed 2nd' is bound to Reissmann …:
  "…duct leader was Yang at 0.0291 / 0.0311 / 0.0250; Reissmann placed 2nd, 2nd and 2nd
   of seven at 0.0387 / 0.0341 / 0.0325…"
```

**Both statements are TRUE**, re-derived here from `LIVE_BOARD` joined to
`round5_per_case_full` rather than taken from the documents:

| duct case | live order (7 positions) | Reissmann | leader |
|---|---|---|---|
| `AR_1_Ret_360` | Yang, Reissmann, US, Wu, Tian, Liu, Montoya | **2nd of 7** | Yang |
| `AR_3_Ret_360` | Yang, Reissmann, Wu, US, Tian, Liu, Montoya | **2nd of 7** | Yang |
| `AR_14_Ret_180` | Yang, Reissmann, Wu, US, Montoya, Tian, Liu | **2nd of 7** | Yang |

This is D176's shape — *the guard faults the correct repair* — but it has left the guard's
own paperwork and landed on **the document that closed rung V10 tonight** (`c2cd83bf`,
2026-08-16T17:25:49Z, 84 seconds before this round's first action) and on **the ladder
ledger itself**. A correct, live-board, third-party placement written by a rung closure is
now a fault on V16's guard.

**What this does to V16's precision requirement, restated.** Round 11's reading was that
the guard's stated sentence-level rate cannot express a cost that is a property of *surface
classes*, and that the true count of real misplacements was **zero**. At HEAD the count of
real misplacements is still zero — but the count of **correct claims faulted on a
non-guard, rung-closing surface** is now **two**, and the direction is the expensive one
V16 names: *"a guard that cries wolf gets switched off, and then it guards nothing."*

**And the recursion is measured.** 19 faults were added since round 11. **18 of the 19 are
round 11's own paperwork** — 13 in its document, 4 in the docket rows it filed, 1 in the
ledger. Round 11's §9.4 noticed its own draft sitting inside the corpus under audit while
untracked and called it *"F5's shape reaching one level further out"*. It is now tracked,
committed, and swept: **grading this guard is the largest single generator of this guard's
live fault count.**

### 5.5 **G5 — F8 is now falsifiable from a SINGLE run: the guard's frame and the guard's detail contradict each other inside one execution.**

Round 11's F8 found the frame's re-point cost typed and stale, and had to run a
three-configuration sweep over 18,974 surfaces to prove it. It does not need one any more.

The frame `check_board_placement_words` printed in the run at §5.4 still reads:

> *"swapping it to the live board … **takes rule-A faults from 2 to 68** over DISJOINT
> sets: **both current faults clear** and 68 new ones appear…"*

The **same `Result` object**, from the **same call**, carries a detail list containing
**34 rule-A faults**. The frame says there are 2; the detail shows 34. No re-point, no
second configuration, no separate harness: **one call, and its two halves disagree by a
factor of 17.**

Round 11 measured this number as 16 at `9dca4738`; at HEAD it is 34, and it grew by exactly
the paperwork of §5.4. The constants are typed into a file whose stated design principle
(L-79) is that figures are generated so they cannot go stale, and that principle is applied
to the pin's date and entrant count **in the same sentence**.

**Why this is worth its own row rather than a note on F8.** F8's remedy was scored as
expensive because verifying it needed a corpus sweep. It does not: an assertion that the
frame's "current faults" figure equals `len([f for f in detail if rule A])` is a
same-object, same-call invariant, and it would have reddened at 16, at 34, and at every
value in between.

---

## 6. FILED, NOT APPENDED TO THE RUNG (R-CONVERGE)

Found while grading V16, **outside its declared scope**, filed as docket rows and excluded
from the rung's verdict and from the new-material count.

- **The margin has three admissible bases and a bare figure names none of them.** §2: the
  `published_overall` basis gives 0.00135281, the per-case-mean basis 0.00136531, and the
  guard's own frame reports the seed bound as *"[177.12%, 178.82%] over 3 admissible margin
  bases"*. A record quoting `margin 0.001365` is quoting one basis of three without saying
  which, and it is the one that makes the seed bound look smaller relative to the margin.
  This is a ground-truth-quoting hazard of the same family as B4, not a V16 defect.
- **`check_rank_claim_values` is FAIL at HEAD** — *"4 claim(s) on surfaces that TRAVEL state
  a value the board contradicts (27 more on lab records)"*, the first being
  `dist/certonomous-demo.zip!…/closure.html:341` claiming `3rd of 5`. This is the sibling's
  own live state, not V16's rung, and `567c7aa6` already records the shipping-archive arm.
  Noted so the count is on the record; not appended.

---

## 7. VERDICT

### 7.1 Does V16 close?

**No.**

| requirement, as written on V16's face | state at `fdfc3eba` |
|---|---|
| ordinals checked against a **parsed** board | **held** |
| whole text, whitespace collapsed | **held** |
| **every ordinal this lab pins on an entrant** | **FAILS.** Rule A cannot fault Yang or Tian in either direction — re-executed at HEAD with two live controls (§4.1) |
| stated false-positive rate against a measured corpus | **held for the named guard** — 71.4% / 76.0% re-measured by execution with a live plant control (§3.1); **absent for the check that owns half the criterion (§4.2)**; and the rate cannot express the cost §5.4 measures |
| stated reach, measured on held-out sentences | **held for the named guard, INCLUDING the Yang/Tian class** (§5.2 — this row moves in the rung's favour) — **but the mechanism that carries it cannot run when its referent is unreadable (§5.3)** |
| generated-not-typed figures (L-79, the rung's own principle) | **FAILS — §5.5.** The frame's re-point cost is typed and now contradicted by its own call's detail, 2 against 34 |
| conformance with the strike-and-keep house rule | **FAILS** — round 11's F4/F7 untouched in this range and not re-executed here |

### 7.2 Is this round BELIEF-NEUTRAL?

**NO. THIS ROUND IS NOT BELIEF-NEUTRAL, AND IT SAYS SO IN THOSE WORDS.**

**New material findings: 5** (G1–G5). **New shapes: 3** (G1, G2, G3).

A round is neutral if it only executes or closes what was already known. This one did
execute four inherited findings — F1's behavioural half, F2, F5 and F8 — and it also
answered the question it was dispatched to answer with a plain, controlled *yes* (§3: the
71% holds). **Had it stopped there it would have been neutral, and it would have said so.**
It did not stop there.

Per finding, *would this change what an outside reader believes?*

1. **G1** — a reader told V16's precision requirement is a live constraint on the rank-claim
   guard believes the requirement follows the work. It follows a **name**, and this round's
   own dispatch inherited the misrouting. **Changes the belief.**
2. **G2** — a reader of round 11 believes the guard is silent about being unable to see the
   board's leader. **It is not silent, and it was not silent at round 11's own frame.** This
   is the one finding that moves in the *rung's favour*, and it is the most important one in
   the round, because it means a grade round asserted a disclosure gap that did not exist.
   **Changes the belief.**
3. **G3** — a reader of `_blind_placement_binding` believes its B1 guard protects the
   disclosure when the referent goes missing. It cannot run. **Changes the belief.**
4. **G4** — a reader of round 11 believes 100% of the guard's live cost is its own
   paperwork. Two faults now sit on the document that closed V10, and both statements are
   true of the live board. **Changes the belief.**
5. **G5** — a reader believes F8 needs a corpus sweep to demonstrate. It needs one call.
   **Changes the belief.**

**What would falsify this verdict.** Any one of these, executed:

- **G1** — show `_BEST_COUNT` or `_BEST_SOFT_WRAP` in the callee closure of
  `check_board_placement_words` at `fdfc3eba`; or show `_PLACE_PRECISION` moving across
  `49b36e57..567c7aa6`. The closure script is 60 lines of `ast` and the precision harness
  runs in seconds per commit.
- **G2** — show that `_derived_blind_spot("check_board_placement_words")` at `9dca4738`
  does **not** name yang and tian, or that `self_audit.py:8639-8645` does not print it.
  Both are one execution; the board referents are unchanged across the range, verified by
  `git log -- <path>`.
- **G3** — reach the string *"the ranking referent is EMPTY or unreadable"* by any
  configuration of `$CERTONOMOUS_RANKING_RECORD`. Three were tried and a positive control
  passed.
- **G4** — show the `LADDER_V_V10_CLOSURE_2026-08-16.md` fault is a record of the guard
  rather than a claim about the board; or show *"Reissmann placed 2nd, 2nd and 2nd of
  seven"* is false of the live board. The second needs `LIVE_BOARD` joined to
  `round5_per_case_full`, which is in §2 and §5.4.
- **G5** — re-run `check_board_placement_words` and get a frame saying 2 alongside a detail
  list of 2 rule-A faults.
- **The verdict as a whole** — show that three or more of G1–G5 were recorded before
  2026-08-16T17:27:13Z. Each was checked against `git show HEAD:docs/DOCKET.md` before
  filing.

**Do not score neutrality early.** G4 and G5 both arrived from a single live run of the
guard that had been launched to settle §4.2, after the first three findings were written
down; G3 arrived from a `TypeError` in a throwaway harness built for §5.2. And G2 was
nearly filed backwards: the first reading of the reach closure showed
`check_board_placement_words` does **not** call `_blind_placement_binding`, which would have
*confirmed* round 11's F1. It was the registry at `self_audit.py:7534` — a dict entry, not a
call — that the closure walker could not see, and only executing the reader's print path
settled it. **An AST call-graph is a summary too.**

### 7.3 Docket rows filed by this round

| row | finding | in V16's scope? |
|---|---|---|
| **D262** | G2 — the guard's derived blind-spot channel already named the Yang gap at round 11's frame; round 11's F1 disclosure half is falsified | yes |
| **D263** | G3 — the B1 branch in `_blind_placement_binding` is unreachable in all three referent-failure modes | yes |
| **D264** | G4 — the guard's live cost 29 → 48; two faults on the V10 closure narrative, both true of the live board; 18 of 19 new faults are round 11's own paperwork | yes |
| **D265** | G1 + G5 — a pass requirement bound to a check's NAME misroutes a correct warning; and the frame's typed re-point cost is contradicted by its own call's detail, 2 against 34 | yes |
| **D266** | the §6 items — the margin's three admissible bases; `check_rank_claim_values` FAIL at HEAD | **no — filed, not appended** |

---

## 8. WHAT THIS ROUND DID NOT DO

- No solver ran. No scoring call was made; the ledger stands at **6**.
- Nothing was sent, uploaded, filed or registered. Submissions remain **PARKED**.
- The scoring pin `deb91557` was **not moved**, and nothing here asks for it to be.
- `scripts/self_audit.py` was **read and executed, never modified.** Every plant in §3.1 was
  made on a copy materialised by `git show` into a temporary directory and destroyed after
  the measurement; the repository copy was byte-clean against HEAD before this round and is
  byte-clean after it.
- Nothing was written under `dist/`, `demo-output/website/latex/`, `motorbike-video/`,
  `LAPTOP_SHOOT.md`, `scripts/lab_check.py`, `scripts/check_rung_attribution.py`,
  `scripts/check_docket_reconciliation.py`, `sdk/tests/`,
  `sdk/chief_engineer/exec_bits.py`, `docs/AGENT_ATTRIBUTION.md`,
  `docs/USING_THIS_LAB.md`, `docs/PRODUCT_LIST.md`, `demo-output/website/closure.html`,
  `demo-output/website/benchmarks.html`, or the V5, V10, V12 and V15-round-9 records.
  `sdk/tests/test_blind_spots_are_printed.py` and `sdk/tests/test_rank_claim_surfaces.py`
  were **read** to locate the print path and the admission predicate, and not run or
  modified.
- The detached worktree at `fdfc3eba` was removed after the measurements.
- **No PDF claim is made by this round.** None was opened, so none is reported — round 11's
  §6 stands unamended.
