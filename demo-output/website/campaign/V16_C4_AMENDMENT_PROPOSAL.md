# PROPOSAL — amend V16's C4 forward, binding the BAR and the ADMISSION PREDICATE together

**STATUS: PROPOSAL. NOT APPLIED. NOT IN FORCE.**
Chief ruled 2026-08-16 that the amendment *should* be made, not that it *is* made.
**It changes a closed rung's face, so it requires Katie's approval before it binds.**

**FORWARD ONLY.** V16's `PASS` at `b2534057` stands on the criterion as it read
when graded. Amending a rung's face and applying it backwards is the retroactive
move W-3 exists to forbid. **This proposal governs future rounds and regrades
nothing.**

**Measured at frame `b2534057`** by the agent that closed the rung, a non-author
of V16, of `scripts/self_audit.py`, and of both precision sets.

---

## 1. THE DEFECT THIS REPAIRS, IN ONE LINE

**C4 as written is satisfiable at a false-positive rate of 100%.** Its operative
condition is *"the rung fails if the check does not **state** its false-positive
rate"*. A check stating *"my rate is 100%"* satisfies it. That was the correct
reading to grade under — no threshold was ever pre-registered, and inventing one
at grading time is the tuning V16's own history forbids — **and it is a defect of
the criterion, which is why this proposal exists.**

---

## 2. WHAT V16 WOULD HAVE GRADED UNDER A PERFORMANCE READING

Stated plainly so the owner can see exactly what the disclosure reading bought.

| | |
|---|---|
| rates as graded, admission predicate `_placements` | **`20 of 28 (71%)`** author set, **`19 of 25 (76%)`** grader set |
| verdict at any bar below 71% | **FAIL** |
| verdict at any bar in 71–75% | **FAIL** (the grader row still exceeds it) |
| lowest bar V16 would have met | **76%** — a bar permitting the guard to be **wrong more often than right** |

**UNDER A PERFORMANCE READING, V16 GRADES `FAIL`.** There is no bar a drafter
would plausibly have written that V16 meets. **That is what the disclosure
reading bought, and what this amendment would restore for future rounds.**

---

## 3. WHY A BAR ON THE RATE ALONE IS NOT A BAR — MEASURED, NOT ARGUED

The chief's ruling is that the amendment must bind the admission predicate too,
because a threshold on a gradee-chosen denominator is not a threshold. **This
round measured that rather than accepting it.** Both sets were driven through
their own `measure()` APIs, each with a live planted control that had to move the
count by exactly one and restore exactly:

```
author: (20, 28) -> plant (21, 29) -> restored (20, 28)    control FIRED
grader: (19, 25) -> plant (20, 25) -> restored (19, 25)    control FIRED
```

| set | admission A — `_placements` | admission B — raw pattern match | numerator |
|---|---|---|---|
| author (41 held) | **20 of 28 = 71%** | **20 of 41 = 49%** | **20 both ways** |
| grader (43 held) | **19 of 25 = 76%** | **19 of 26 = 73%** | **19 both ways** |

**THE SAME 20 ERRORS READ 71% OR 49% DEPENDING ONLY ON WHICH SENTENCES ARE
ADMITTED — a 23-point swing with the numerator untouched.** Driven across
candidate bars, the admission predicate **alone** flips the author row at every
bar in **50, 55, 60, 65, 70, 71%**. A criterion whose verdict is decided by a
choice the gradee makes is not a criterion — which is the same ground that
decided the disclosure reading in the first place, now applied to its own repair.

**AN IMPORTANT FAIRNESS POINT, and it is not decoration.** The lab chose the
**less** flattering predicate. Round 10 (D49) moved this figure from the loose
admission to `_placements`, taking the author's own row **49% → 71%** with its
numerator unmoved. **Nobody gamed this denominator; the lab tightened it against
its own interest.** The amendment exists to *lock a choice already made honestly*
so a future round cannot quietly unmake it — not to accuse anyone of having
moved it.

---

## 4. THE AMENDMENT, BOTH HALVES BOUND

### HALF ONE — the admission predicate. **PROPOSED FOR ADOPTION NOW.**

> C4's false-positive rate must be measured under a **named, committed admission
> predicate**, and the check must state that predicate beside the rate. The
> predicate in force is `len(_placements(text, names, board)) > 0` — the same
> predicate `board_placement_faults` is built on, so a row's numerator and its
> denominator come from one function and not two. **A round that changes the
> admission predicate must re-publish every historical row under the new
> predicate in the same commit, or the change is void.** A rate published without
> its admission predicate does not satisfy C4.

**Why this half is proposable today:** it invents nothing. The predicate already
exists, is already in force, was already chosen against the lab's own interest,
and is already recomputed from committed sentences by
`sdk/tests/test_rank_claim_surfaces.py`. Adopting it changes no measurement — it
removes a degree of freedom.

### HALF TWO — the numeric bar. **ABSTAINED. NO NUMBER IS PROPOSED.**

**I decline to propose a figure, and the abstention is the honest answer rather
than a deferral.** The chief's constraint was that the bar be justified, not
picked. Measured, no evidence in this lab supports any particular number:

1. **Both existing rate measurements are adversarial by construction and are
   explicitly not representative.** The check says so in its own sentence —
   *"BOTH SETS ARE ADVERSARIAL AND NOT REPRESENTATIVE, each weighted toward
   shapes that have already broken this guard, so neither is a corpus rate"*.
   **A sample built to break a guard cannot bound how often the guard breaks.**
2. **The two honest sets disagree by more than most candidate bars would
   separate:** 5 points apart under admission A and **24 points apart** under
   admission B. When two blind, independently built samples disagree by 24
   points, no third number drawn from them is a bound on anything.
3. **The corpus rate has never been adjudicated.** The live sweep carried **61**
   rule-A faults at frame `04b9cc37`; **not one has been classified true or
   false.** The one figure that could justify a bar does not exist.

**Proposing a number here would be inventing a threshold to fit a verdict — the
exact move this rung already refused when it declined to widen `_RANK_WINDOW`
fivefold so a control would pass.**

### HALF TWO, THE PROCEDURE THAT WOULD EARN A BAR

Proposed **in place of** a number, so the abstention has an exit:

1. Draw a sample from the **live corpus sweep** — the 61 rule-A faults, or a
   random sample of admitted sentences across the tracked corpus — **not** from
   either adversarial set.
2. Adjudicate each as true or false fault, **by an agent that authored neither
   the guard nor either precision set**, blind to the guard's patterns.
3. Publish that corpus rate with its admission predicate and its sampling frame.
4. **Only then** set the bar, from that figure, with the margin argued in the
   open.

**Until step 4, C4 keeps the disclosure reading — which is not a loophole while
half one is in force**, because a disclosed rate under a locked denominator is a
falsifiable claim, and a disclosed rate under a free denominator is not.

---

## 5. THE RATES THAT TRAVEL WITH THIS PROPOSAL

Required by the chief so that no future bar is read as describing today's guard:

> **The guard's measured false-positive rates at the time of this proposal are
> `20 of 28 (71%)` and `19 of 25 (76%)`, under admission predicate
> `_placements`, on two adversarial and explicitly unrepresentative sets. Under a
> performance reading V16 grades FAIL at these rates. The live corpus rate is
> UNMEASURED.**

---

## 6. WHAT THIS PROPOSAL DOES NOT DO

- **It does not regrade V16.** The `PASS` at `b2534057` stands on the criterion as
  it read when graded, and this proposal is forward-only.
- **It does not tune the guard.** No window, pattern, admission rule, board,
  severity or admission predicate was changed — half one *records* the predicate
  already in force.
- **It does not set a bar**, and says why rather than deferring silently.
- **It is not in force.** It goes to Katie for approval. Owner: Katie; routed by
  the chief's ruling of 2026-08-16.
