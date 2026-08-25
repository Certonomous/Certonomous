# F4 CONVERSION — TWO RULINGS: **THE CAP CROSSING, AND WHICH QUANTITY A CAP GOVERNS**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **ZERO COMPUTE.** Evidence: `d4308dde` (`RESULTS.md`), `1b0bcdcc`
(calibration **C-91**), `3e82e989` (frozen pre-registration).

**Under Sanaa's 2026-08-25 directive a cap is a RUNAWAY GUARD: a crossing is
reported to the supervisor and the supervisor decides.** This is that decision.

---

## 1. RULING 1 — **THE CROSSING IS RECORDED AS A CROSSING. NOT EXTENDED, NOT ABSORBED, NOT RETROSPECTIVELY AUTHORISED.**

**Measured 24.1108 core-min against a hard cap of 24.0 — over by 0.1108, 0.46 %.**

**The run's results STAND.** Rule 12's remedy is *"an overrun **stops the run**; it
does not get a new budget"* — and **a run that has already finished cannot be
stopped.** No clause voids a completed, graded result for a 0.46 % overrun, and I
am not inventing one.

**But the lane's own framing is right and I am adopting it verbatim: it crossed on
the final accounting after the ninth case finished, and THAT IS TIMING, NOT
MITIGATION.** The crossing is not excused by having been undetectable. **A ledger
that shows a crossing which was *ruled* is worth more than one that shows no
crossing because nobody looked.**

**AND THE OVERRUN IS LARGER THAN 0.46 %, WHICH CUTS AGAINST ME AND IS THEREFORE
SAID FIRST.** **F4C-Q2**: mesh-generation and sampling clocks were never captured.
**So 24.1108 is a LOWER BOUND on gross spend, not the spend** — and it is not the
same quantity as the 14.66 core-min basis the prediction was built on. **The true
crossing is strictly worse than the figure I am ruling on.**

### 1.1 THE REAL DEFECT IS NOT THE 0.46 %. IT IS THAT THE CAP COULD NOT HAVE STOPPED ANYTHING.

`rerun_f4.py` totals wall time **after the last case returns**. So the cap was
evaluable **exactly once, at a moment when every core-minute had already been
spent.**

> **A cap that can only be evaluated after the final case is not a runaway guard.
> It is a post-hoc audit wearing a guard's name.**

**Sanaa's directive made caps runaway guards specifically so a runaway could be
STOPPED.** This one could not have stopped a runaway of any size — 0.46 % or
400 %. **That, not the 0.1108 core-min, is the finding.**

**BINDING ON EVERY cfd PRE-REGISTRATION FROM THIS DATE:** the cap is checked
**incrementally, after each case or each rung completes**, against the running
total, with the launcher **halting and reporting** on a crossing. **A cap only
totalled at the end is registered as a post-hoc audit and MUST say so in the
document**, so nobody mistakes it for a guard.

## 2. RULING 2 — **F4C-Q1: THE CAP GOVERNS WALL × RANKS ÷ 60. FULL STOP.**

Two instruments, two quantities, one cap:

| instrument | quantity | total | vs 24.0 |
|---|---|---|---|
| `rerun_f4.py` (launcher) | **wall seconds × ranks ÷ 60** | **24.1108** | **CROSSED** |
| `grade_f4.py` (grader) | the solver's own final `ExecutionTime` ÷ 60 | 22.3098 | not crossed |

> **Standing rule 12 defines the unit: "core-minutes (wall s × ranks ÷ 60)".
> `ExecutionTime` IS NOT WALL TIME** — it is the solver's internal accounting and
> **excludes process startup, mesh generation and sampling.** **The registered
> quantity is wall. The cap is CROSSED.**

**Taking 22.3098 because it sits under the cap is the fitting rule 2 exists to
prevent** — choosing between two available numbers *after seeing which one passes*.
**It would be the same move as raising a cap after seeing which rows it refused,
and I refuse it for the same reason.** The lane refused it first and was right.

**NEITHER INSTRUMENT IS DEFECTIVE. THE PRE-REGISTRATION IS.** Both measured their
own quantity correctly; **the frozen document never said which quantity the cap
governs**, and that ambiguity is what let two defensible numbers disagree about a
gate. **Not repairable post-compute — rule 2 closed that door when the first case
ran.** It is registered as **F4C-Q1** and it is **mine to close in the successor
registration**, not the lane's.

**BINDING ON EVERY cfd PRE-REGISTRATION FROM THIS DATE:**
1. **State the cap's quantity explicitly — wall × ranks ÷ 60 — in the document.**
2. **Any `ExecutionTime` figure is reported as a SECONDARY diagnostic, labelled as
   such, and never compared to a cap.**
3. **Capture mesh, sampling and startup clocks**, so the gross figure is a
   measurement and not a lower bound (F4C-Q2).
4. Dollars remain **DERIVED, NOT MEASURED** — the box cannot read its own billing.

## 3. THE CALIBRATION GAP IS PARTLY MINE, AND I AM NOT LEAVING IT ON THE LANE

**C-91 ratio 1.389.** The lane took a **1.15 contention uplift from a reported load
of 3.70**. **The box was at 11.14 at launch and reached 15.05.**

**I gave it that 3.70.** I wrote *"load 3.70/16 with ~12 idle"* and *"Box has
room"* into its brief, and by the time it fired, **Sanaa's saturation directive had
done exactly what it was meant to do and the box was full.** **The lane predicted
from a stale figure because its supervisor handed it one.**

> **A cost basis must be conditioned on the load AT LAUNCH, measured by the
> launcher in its own invocation — never on the load when the estimate was written,
> and never on a figure relayed from a supervisor's brief.**

**Binding on every cfd pre-registration from this date**, and it is the seventh
correction to this supervisor today. **Waste 0.0, correctly named separately and
not absorbed into the ratio.**

## 4. THE VERDICTS, VERIFIED BY ME FROM `RESULTS.md` RATHER THAN RELAYED

**8 `NOT A RESULT`, 1 `CONVERGING`, 0 `PASS`, 0 `GATE FAIL`.**

**The single most important row in this campaign:** all three `G-F4-2` deviations
fall **INSIDE** their registered bands — **+2.0644 % < 3.1747 %, +2.3327 % <
3.2005 %, +0.7007 % < 3.2728 %** — **and are `NOT A RESULT` anyway**, because rule
5 forbids a band verdict on a non-converging triple.

> **The gate turned a would-be `PASS` INTO a `NOT A RESULT` — the only direction
> rule 5 permits, and precisely the direction the 2026-07-28 record went the other
> way on.**

**`G-F4-3-M8.0` is `CONVERGING` at observed order 3.1905, GCI 0.0831 % at
Fs = 1.25** — **a real, quantified convergence statement replacing a `PASS` that
was graded against an em-dash.**

**The solver is REPRODUCIBLE.** Standoff `0.448538 / 0.434503 / 0.418129` against
the recorded `0.4485 / 0.4345 / 0.4181`; Cp RMS `3.9096 / 3.9087 / 3.8685 %`
against `3.91 / 3.91 / 3.87 %`. **Nothing about F4's physics has been shown wrong.
What fails is the LADDER**, and the old record's own diagnosis — *"a genuine,
resolution-dependent systematic bias in the peak-density-gradient detector
itself"* — **is confirmed. The detector, not the flow, is what moves.**

**This vindicates my ruling of `54ae328e` exactly as written: their numbers stand;
their gate never existed.** And it vindicates the constraint I registered **before
this fired** — that rule 5 could only make Gate 1 worse, and that **a conversion
returning `NOT A RESULT` would be the conversion WORKING.** It returned eight.

**The pre-compute check-1 catch paid for itself here:** four of the nine landed
**below `endTime`** — the identical pattern — and **under the defective
`t_last ≥ endTime` clause those four would have been reported `NOT A RESULT` for
an instrument reason**, inside a campaign that returned eight `NOT A RESULT`s for
**real** ones. **The two would have been indistinguishable in the record.**

## 5. THE PREDICTION MISS, RECORDED AS A MISS

**8 of 9.** The miss: G-F4-3-M6.0 predicted *"monotone and may converge"*, returned
**`DIVERGENT`, p = −0.1342**. **The lane's own words: it read monotonicity as
convergence, and they are not the same thing.** **A monotone sequence with a
negative observed order is monotone in the wrong direction** — the increments grow.
**Registering a prediction that can be scored wrong, and scoring it wrong out loud,
is what makes the other eight worth anything.**

## 6. THREE PROCESS NOTES THAT EARNED THEIR PLACE

1. **The log-path assertion earned its keep**: `check-ignore` confirmed **all 45
   logs** would otherwise have been **silently dropped** by `.gitignore`. The
   primary evidence of a nine-case campaign, saved by an assertion.
2. **The insertions-only assertion caught a broken ledger write and stopped a bad
   commit.**
3. **Rule 11's id race bit THREE TIMES IN ONE LANE** — the max moved **C-87 →
   C-90** while it worked, so the row landed **C-91, not the C-88 first derived.**
   **Fourth independent corroboration today** that an id must be re-derived by hand
   inside the committing invocation.

## 7. STANDING

**Gate 3 / SWBLI stays `BLOCKED`** on Sanaa's unmade event-1/event-2 ruling.
**Zero solvers running; the 2026-07-28 tree has zero modifications** — the
production-tree guard held.
