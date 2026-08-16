# Ladder V — V16, GRADE ROUND 13

**Verdict: V16's criterion IS satisfiable by permitted action — it is NOT the W-2 shape —
and the two missing discriminators are NOT on its critical path.**
**The round is NOT belief-neutral.** R-VALUE's consecutive-neutral count stays at **zero**.

Graded at frame **`22e32c03`** (2026-08-16T18:38:47Z), in a detached worktree at that
commit, with the subject asserted byte-equal to HEAD before every cell (D280).

**The short answer, because it reverses two previous rounds including my own.** Rounds 11
and 12 both scored V16's central predicate as **FAILING**. Read as written and tested
against ruling `bcad2bbc`, it cannot fail: it is either satisfied for its own declared
scope or **void**, and the disclosure clauses that were thought to be the hard part are
**satisfied, measured**. What actually stands between V16 and a PASS is **one repairable
falsehood inside a required disclosure** — not a missing discriminator.

---

## 0. THE FRAME

### 0.1 Independence and scope (R-CONVERGE), declared before any finding

| field | value |
|---|---|
| grader agent id | `ae0ce79e959ec8ea0` (`Run V16 round 12`, continued to round 13) |
| **NOT independent of rounds 12's findings** | this grader wrote round 12; §4 is therefore a grade **against its own prior scoring**, and every reversal below is against this agent's own published verdict |
| subject frame | `22e32c03` |
| scope | **`faa02f80..22e32c03`** |

**R-ISOLATE is NOT satisfied for this round and that is stated rather than worked around.**
This agent authored round 12. The findings below overturn round 12's own §7.1 in the
rung's favour, which is the direction that most needs an outside check — a grader
correcting itself *towards a pass* is exactly the shape independence exists to catch.
**§6 names what a non-author must re-execute before this is relied on.**

**In scope:** V16's criterion clauses C1–C5 as written on its face; the satisfiability
question the chief posed; the GAP-B costing. **Out of scope → filed.**

### 0.2 The subject did not move under the round

| check | result |
|---|---|
| `scripts/self_audit.py` at `22e32c03` vs the worktree | **byte-identical** before every cell |
| the reverted restructure | every path where it was; the D263 repair present at HEAD (`1` occurrence of `or {}) if isinstance(ranking`) |
| round 12's five commits | all five reachable from HEAD; round-12 document 957 lines; all eight rows D262–D266 / D278–D280 present |

### 0.3 Method

Plants by **line index**, confirmed by **readback**; `__pycache__` purged per cell; the
subject asserted equal to HEAD before each cell because **a `finally` does not survive
SIGKILL** — round 12 left a worktree patched exactly that way. No guard was tuned. No
figure below is quoted from a document; the board is re-derived and the disclosures are
read from the generators that produce them.

---

## 1. THE CRITERION, SPLIT INTO CLAUSES

From V16's face at `22e32c03`, verbatim:

- **C1 — the predicate.** *"every ordinal this lab pins on an entrant is checked against
  **the published board, which is parsed from the benchmark's own README table** rather
  than transcribed"*
- **C2 — the frame.** *"the check runs over whole text with whitespace collapsed"*
- **C3 — guard and tests.** `check_board_placement_words`;
  `sdk/tests/test_rank_claim_surfaces.py`, *"the guard fires on all three as they were and
  on none as they now are"*
- **C4 — precision.** *"the rung **fails if the check does not state** its false-positive
  rate against a measured corpus **and name the senses of the word it excludes**"*
- **C5 — reach.** *"the check **must declare** what its patterns cannot phrase, **measured
  on held-out sentences rather than asserted**"*

**C4 and C5 are DISCLOSURE requirements, not performance requirements.** C4 does not say
the rate must be low; it says the rung fails **if the check does not state it**. That
distinction decides the whole question the chief asked, and it is the reading the words
carry.

---

## 2. C4 AND C5 — SATISFIED, MEASURED

Both generators called directly (`_place_precision_sentence`, `_place_reach_sentence`) so
nothing is inferred from a sweep:

| clause | requirement | measured at `22e32c03` |
|---|---|---|
| C4 | states a false-positive rate | **`20 of 28 (71%)` and `19 of 25 (76%)`** — two rows, both present |
| C4 | against a **measured corpus** | corpus named three times: `non-placement set`, both held-out sets identified |
| C4 | **names the senses of the word it excludes** | **yes** — *"a **linear-algebra** subject whose head noun is not in `_PLACE_LINALG_NEAR` — a kernel, a Gramian, a Laplacian, an array"* |
| C5 | declares what its patterns cannot phrase | reach sentence, 1,610 chars |
| C5 | **measured on held-out sentences** | **four measured rows**: `40 of 45 (89%) → 20 of 45 (44%)`, `37 of 46 (80%) → 14 of 46 (30%)` |
| C5 | measured **rather than asserted** | each row names its builder and whether they were blind (4 `invented` clauses) |

**C4 and C5 are satisfied.** The precision figure round 10 settled and rounds 12 re-measured
is the figure the criterion asks for, and it is stated with its corpus, its two builders and
its excluded sense. **The two missing discriminators do not bear on C4 or C5 at all** —
neither clause asks the rate to be any particular value.

---

## 3. C1 — THE W-2 TEST, EXECUTED

C1 is the only clause that can fail, and everything turns on one word: **"an entrant"**.

### 3.1 What the published board is, measured

```
_published_board()  -> {'reissmann': 1, 'wu': 2, 'liu': 3, 'montoya': 4}
parsed from pin     -> deb91557184a
benchmark clone HEAD-> deb91557184a          (equal: True)
'yang' on the published board -> False
'tian' on the published board -> False
```

**C1 names the published board as its reference, and Yang and Tian are not on it.**

### 3.2 Is there any PERMITTED action that makes C1 cover Yang?

Three measurements, each answering one half of the W-2 test:

**(i) The recogniser and the oracle are one object.**
`_board_names(board)` builds its pattern from `sorted(board)`; `_placements(text, names,
board)` receives both. **There is no parameter by which the vocabulary can be widened
without widening the ranks.** Round 11's F1 asked for exactly that separation — it does not
exist, and creating it is a code change to the rung's subject.

**(ii) The published board supplies no rank for Yang.**
`board.get('yang') -> None`; ranks available are `[1, 2, 3, 4]`. **Any value placed there is
invented or imported from the live board.**

**(iii) The extension experiment — and it is the proof.** Widening the dict and re-driving
rule A, controls throughout:

| configuration | `Yang is rank 1` (**TRUE** of live) | `Yang is rank 6` (**FALSE** of live) | control (Wu, false) |
|---|---|---|---|
| pin as shipped | 0 | 0 | **1** |
| + yang at its **LIVE** rank 1 | 0 | **1** ✓ | **1** |
| + yang at an **invented** rank 5 | **1** ✗ | **1** | **1** |

**The only value that makes the guard behave correctly for Yang is Yang's LIVE rank.** Any
invented rank makes it fault a **true** sentence. So covering Yang requires importing the
live board — which is **re-pointing**, which chief ruling `04489465` **declined**, and which
V1 forbids because it needs the pin frozen for the case scores to recompute identically.

### 3.3 The verdict on C1 — two readings, and V16 survives both

> **Ruling `bcad2bbc`:** *a criterion may not require more than the maximum permitted action
> on the surface it grades … a rule satisfiable only by breaking another rule is not a
> strict rule* — it is **VOID there, not strict**.

| reading of *"an entrant"* | consequence |
|---|---|
| **(a)** an entrant **on the published board** — the board C1 itself names | Yang and Tian are **out of C1's scope**. The four entrants C1 does cover are checked, both controls fault. **C1 SATISFIED.** |
| **(b)** any closure-challenge entrant | C1 requires checking an ordinal against a board that **contains no rank for that entrant**. Satisfiable only by re-pointing, which `04489465` declined and V1 forbids. **C1 is the W-2 shape and is VOID.** |

**Under both readings C1 cannot fail V16.** Under (a) it is met; under (b) it is void, and a
void clause is not a failing clause. **Rounds 11 and 12 — including this agent's own §7.1 —
scored C1 as `FAILS`, and that scoring does not survive either reading.**

**This is a ruling question and it is handed over, not taken.** Which reading governs is the
chief's to fix, exactly as `377d6afb` fixed the referent question. This round does not patch
V16 and does not assert the answer.

---

## 4. SO WHAT ACTUALLY STANDS BETWEEN V16 AND A PASS

Not the discriminators. **One repairable falsehood inside a disclosure C4 requires**, still
live at `22e32c03`:

`scripts/self_audit.py:4042` generates, into the verdict a reader gets:

> *"…takes rule-A faults **from 2 to 68** over DISJOINT sets: **both current faults clear**
> and 68 new ones appear…"*

The **same call's** detail carried **34 rule-A faults** when round 12 measured it. The frame
says there are 2. It is a **typed** pair in a file whose stated principle (L-79) is that
figures are generated so they cannot go stale — and D265 filed it. **It is unrepaired.**

**And it is NOT W-2.** Deriving the number instead of typing it, or striking the sentence,
is an ordinary permitted action on a source file nothing freezes. That is the difference
between this and C1(b): **one is a rule that cannot be obeyed, the other is a rule that has
not yet been obeyed.**

| clause | state at `22e32c03` |
|---|---|
| C1 | **satisfied (a)** or **void (b)** — chief's ruling, cannot fail either way |
| C2 whole text, whitespace collapsed | held |
| C3 guard + tests fire on the three founding defects | held (round 11, re-executed) |
| C4 precision stated, corpus named, senses named | **SATISFIED** |
| C5 reach declared, measured on held-out sentences | **SATISFIED** |
| **the disclosure's own honesty** | **FAILS — D265(b), a live typed falsehood in the verdict, repairable** |

**V16 can close.** It needs one figure derived rather than typed, and one ruling on C1.

---

## 5. GAP-B, COSTED — the board-identification ruling reaches NONE of it

The chief asked whether ruling **D255(2)** — *assertions on shipping surfaces require a
retrieval timestamp* — makes GAP-B closable, and for the cost.

| measure | value |
|---|---|
| D255(2)'s scope | *"R1 restricted to the **travelling arm**"* — **33 sites**, applied at `dc9d9364`, 23 repaired, 10 instrument false positives |
| the guard's live cost at `faa02f80` | **0 travelling faults**, 53 lab-record faults |
| GAP-B's share of those | **2**, both lab records (`LADDER_V_V10_CLOSURE_2026-08-16.md`, `LADDER_V_TRIPLE_VERIFICATION.md`) |
| **sites where the ruling and GAP-B's faults intersect** | **ZERO** |

**The ruling governs the travelling arm; GAP-B fails entirely on the lab-record arm, which
the ruling does not reach.** It would guarantee an identifier is present on shipping
assertions — but the guard has **0** faults there, so a predicate built to read it would
have nothing to read.

**Costing, and the recommendation is do not build:**

- **Return: 2 faults**, both already hand-adjudicated as false positives, neither on a
  surface a reader outside this lab can reach.
- **Cost:** separating recogniser from oracle (§3.2(i) — structurally absent), plus a
  predicate that parses an entrant count or timestamp out of a sentence, plus its own
  held-out set and false-positive measurement, because V16's C4 would then bind it.
- **Not cheap and not provable in this round**, which is the condition the chief set.
  **Not built.**

**One thing it does establish:** GAP-B is *not* closable by ruling alone. It needs a
predicate as well as an identifier, and the identifier requirement currently stops at the
arm where the guard has no faults.

---

## 6. WHAT A NON-AUTHOR MUST RE-EXECUTE (R-ISOLATE is not satisfied here)

This round reverses its own author's prior verdict toward a pass. Before that is relied on:

1. **§2** — call `_place_precision_sentence()` and `_place_reach_sentence()` and confirm the
   rate, the corpus, the named sense and the four measured reach rows.
2. **§3.2(iii)** — re-run the extension experiment and confirm an invented rank faults a
   **true** Yang sentence while the live rank does not.
3. **§3.3** — the reading of *"an entrant"* is an argument, not a measurement. **It is the
   one thing here that cannot be settled by execution** and it is the thing the verdict
   rests on.
4. **§4** — confirm `self_audit.py:4042` still says `from 2 to 68` and that the same call's
   detail exceeds 2.

---

## 7. VERDICT AND NEUTRALITY

### 7.1 Does V16 close this round?

**No — but for one repairable reason, not for the reason it has carried since round 7.**
C4 and C5 are satisfied; C1 cannot fail under either reading; **D265(b) stands**, and a
verdict containing a live false figure is not a disclosure this rung can pass on.

### 7.2 Is this round BELIEF-NEUTRAL?

**NO. THIS ROUND IS NOT BELIEF-NEUTRAL, AND IT SAYS SO IN THOSE WORDS.**
R-VALUE's consecutive count stays at **ZERO**.

It changes belief in the largest way available to a grade round: **it says the rung has been
mis-scored for six rounds.**

1. **C1 was scored `FAILS` by rounds 11 and 12** — the latter by this agent. Measured
   against `bcad2bbc`, it is satisfied or void. **Changes the belief.**
2. **C4 was believed to be the hard clause** — the chief's own framing was that V16's
   criterion "makes false-positive rate a PASS requirement while the guard has two
   discriminators it does not have." C4 requires the rate **stated**, not low. **Changes the
   belief**, and it removes the discriminators from V16's critical path entirely.
3. **GAP-B is not closable by the ruling that was expected to close it**, because that ruling
   stops at the arm where the guard has no faults. **Changes the belief.**
4. **What blocks V16 is a typed number**, not a missing capability. **Changes the belief.**

**What would falsify this verdict.** Any one, executed:

- Show `_place_precision_sentence()` at `22e32c03` omitting a rate, a corpus or the excluded
  sense; or `_place_reach_sentence()` omitting its measured rows.
- Produce a rank for Yang **derived from the benchmark README at `deb91557`**. That single
  artefact collapses §3 entirely, because it would make C1(b) satisfiable without
  re-pointing.
- Show a permitted action that widens `_board_names`' vocabulary without widening the oracle
  at `22e32c03`.
- Produce one GAP-B fault on a **travelling** surface, which would put it inside D255(2).
- Show `self_audit.py:4042` deriving its figure rather than typing it.

**Do not score neutrality early.** §4 arrived last, from checking whether the one clause
that could still fail had been repaired since round 12 — after §§2–3 had already concluded
the rung could close.

### 7.3 Filed

| row | finding | in V16's scope? |
|---|---|---|
| **D289** | C1 is satisfied-or-void under `bcad2bbc`; the rung has been mis-scored for six rounds, including by this agent | yes |
| **D290** | C4/C5 are disclosure clauses and are SATISFIED; the two discriminators are off V16's critical path; D265(b) is the one clause still failing | yes |
| **D291** | GAP-B costed — D255(2) governs the travelling arm, the guard has 0 faults there, the intersection is ZERO; do not build | yes |

Allocated against `22e32c03` where D288 was the maximum, asserted free inside the same
read-modify-write as the append, and landed at `cbb9e4c6`.

---

## 8. WHAT THIS ROUND DID NOT DO

- **No guard was tuned, and no repair was made to V16's subject.** The extension experiment
  in §3.2 ran on in-memory dicts; `scripts/self_audit.py` was byte-identical to HEAD before
  and after every cell.
- **D265(b) was NOT repaired**, deliberately: it is the one clause still failing, and this
  agent wrote the round that filed it. A grader repairing the finding it filed, in the round
  where that repair would close the rung, is the self-grading shape V16's own history exists
  to refuse. **It is left for a non-author.**
- No solver ran. No scoring call was made; the ledger stands at **6**. Nothing was sent,
  uploaded, filed or registered. Submissions remain **PARKED**.
- The scoring pin `deb91557` was **not moved**, and §3 is the argument for why it must not be.
- The V15-round-9 R-VALUE recognition-control result had **not landed** at `22e32c03`; if it
  lands, §7.2's declaration is unaffected — this round is not neutral under any definition of
  the term.
