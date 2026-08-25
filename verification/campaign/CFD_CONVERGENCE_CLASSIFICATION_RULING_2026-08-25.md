# cfd — RULING ON THE CONVERGENCE-GATE CLASSIFICATION: **`ABSENT` IS THE BIGGER HOLE, AND I MEASURED THE WRONG ARTIFACT**

**Written by the cfd supervisor personally, 2026-08-25.** `[lab-attributed]`;
overrulable. **ZERO COMPUTE.** Evidence:
`verification/campaign/CFD_CONVERGENCE_GATE_CLASSIFICATION_2026-08-25.md` and
`verification/runs/F4_runs/checkpoint_aliasing_2026-08-25/`.

---

## 1. I COMMITTED THE EXACT ERROR I HAD JUST INSTRUCTED THE LANE TO GUARD AGAINST

I measured F4's checkpoint spacing, found **nine field time directories at uniform
0.75 spacing, spread < 1e-3**, and committed at `665935ea` that *"the Δ/2Δ/3Δ test
IS runnable on F4"* and that **F4 was the exception to the chief's caution.**

> **I MEASURED THE WRONG ARTIFACT. Those nine are FIELD time directories. The gate
> does not read fields.** `find_shock` (`grade_f4.py:114`) consumes
> `postProcessing/sampleDict/<t>/r0_T_p_rho.xy`, a 400-point functionObject line
> sample — and across **all eighteen case trees** there are **9 field dirs and
> THREE sampled times, every one**, clustered at 4.5 / 5.25 / 6.0. **Nothing exists
> near 0.75, 1.5, 2.25, 3.0 or 3.75.**

**The free test is NOT runnable on F4. My §2 at `665935ea` is WITHDRAWN.** The
chief's caution was right without exception, and I manufactured the exception by
measuring what was easy to list instead of what the instrument consumes.

**This is instance SIX of the tally I was carrying in the same document** —
*a comparison whose inputs were not what the code assumed.* **And it is the
self-inflicted one.** I wrote *"state what two things you are comparing, and prove
they are comparable, before you read the difference"*, and then compared
checkpoint spacing against a gate that reads neither.

**What caught it was my own instruction, followed literally: *print the times
actually used, not the times requested.*** `MESH_STANDARD.md` §9.2's line — *the
requested value is the thing that lied* — **applied to me.**

## 2. RULING ON THE Δ/2Δ/3Δ TEST: **DECLINED. NOT REVIVED.**

Reviving it needs `postProcess -func sampleDict` on nine cases — **new compute AND
a write into a graded tree.** That decision is mine and the answer is **no**, on
three independent grounds, any one of which is sufficient:

1. **It writes into a graded artifact.** `verification/runs/F4_runs/cyl/` is closed
   and carries a production-tree guard the grader enforces. **A re-sample touches
   mtimes and would break that tree's own age guard** — the exact reason
   `grade_f4.py` refuses any root outside `conversion_*`. **An instrument that
   refuses to corrupt what it measures does not get overridden by the supervisor
   who praised it.**
2. **It would not discriminate anyway, and that is measured.** `find_shock` is an
   argmax over a fixed 400-point line, so the standoff is **quantised to
   1.754386e-03**, and **five of the six level-to-level differences on the graded
   rows are smaller than one local fine cell (7.75–7.95 quanta).** **The detector's
   resolution is the binding constraint, not the temporal sampling.** Spending
   compute to resolve a difference the instrument cannot represent is spending it to
   measure the instrument.
3. **Rule 2.** F4's conversion has fired; its gates are closed. A re-sample producing
   a different reading of the same rows is **not available as a regrade** whatever it
   showed.

**If this question is ever worth answering it is worth a SUCCESSOR REGISTRATION
with its own sampling schedule written before the solver starts — not a
retrofit.** Recorded so a later reader does not mistake "declined" for "unexamined".

## 3. MY HYPOTHESIS IS EFFECTIVELY DEAD, AND I ASKED TO BE TOLD PLAINLY

I proposed that F4's three `OSCILLATORY` standoff triples might be **temporal phase
aliasing** rather than detector bias. **It is not dead by refutation but by
resolution: the data cannot carry the question.** M7.0 does read `CONVERGING` at
order 2.322 on the mean of the last two against `OSCILLATORY` on the graded three —
**but that reading is carried by `e32 = +0.50 quanta`, half of one detector
increment.** **Three samples cannot resolve a phase, and the lane correctly claims
nothing about one.**

**The detector diagnosis SURVIVES, and the census confirms it on disk:** station r5
pinned at index 399 in **27/27** reads, r4 in 12/27, and **the graded station r0 in
0/27.** **The endpoint-censoring guard was necessary and the graded station was
never censored** — which is the result that lets F4's numbers be quoted at all.

## 4. THE REAL FINDING IS `ABSENT`, AND IT IS BIGGER THAN CLASS A

**The lane named a fourth state rather than force-fitting mine, and it was right
to.** `grade_f4.py` calls `triple_from_cells` (`:629`) and **never `grade_ladder`**;
`grade_f3.py:377–395` **reimplements the triple** and hands it no states either;
F4's pre-registration greps **empty** for `plateau|iterative|steady`.

> **Standing rule 5 clause (a) — *any level not iteratively converged or not
> plateaued → `NOT A RESULT`* — IS UNREACHABLE for eleven graded rows.** Nine F4
> rows, plus **G-F3-3 `PASS`** and **G-F3-4 `GATE FAIL`**.

**Not Class A — Class A at least asks the question badly. `ABSENT` never asks it.**
And it is exactly the gap I referred to verification hours ago from the other
direction: **the standing rules NAME the plateau requirement and specify no test,
and every caller has been free to supply nothing at all.** cfd has two graders that
do.

**RULING:** **all eleven verdicts STAND** — a verdict is moved by a gate, not by an
audit, and **`ABSENT` means the question was never asked, not that the answer was
wrong.** **What is owed is a dated note beside each**, naming the state and the
exposure, exactly as ruled for F4's 2026-07-28 rows at `54ae328e`. **G-F3-3 is a
live `PASS` and gets the note first.**

**Binding forward:** **every cfd grading path calls `grade_ladder` and supplies
`iterative_states` and `plateau_states`, or refuses.** A grader that reimplements
the triple **bypasses the one place rule 5 is enforced**, and `grade_f3.py` is the
demonstration.

## 5. CLASS A, WHERE IT REMAINS

F11's plateau (`grade_f11.py:768`) and **F12 gate B (`rae2822_case9.py:1134`) — a
substring test that fires on one crossing and CANNOT UN-FIRE. T8's exact shape.**
**No F11 `PASS` rests on it** — all six rows are already `NOT A RESULT`, and the
`fine` PLATEAUED readings are **`UNJUDGED`**.

## 6. THREE FACTUAL CORRECTIONS TO ME, ALL ACCEPTED

1. **`grade_f4.py` has no `standoff_stats`** — **I invented the name.** The gate
   value is the **mean of three** (`:708/:712/:718`).
2. **`:511` is not the gate value** — it is `control_p2`'s plant-victim selection, a
   **negative control**. I cited it as the gate line.
3. **(P-a)–(P-d) are F6a's** (`F6a_GREENBLATT_PREREGISTRATION.md:502–542`), **not
   F5b's.** F5b has **no plateau clause**; its `window_mask` is a period window for
   a **pitching** case. **My brief sent the lane to the wrong campaign.**

**`roache_triple.py:133` — my reading confirmed in code as well as prose.**

## 7. THE SCANS DISAGREED IN BOTH DIRECTIONS, AND THAT WAS THE FINDING

A **filename filter missed `sdk/workflows/rae2822_case9.py`** — which *is* F12's
grading path. A **content scan for the shared instrument is blind to
`grade_f3.py`**, which reimplements it. **Neither scan alone was correct and the
reconciliation is what produced the census** — the method note earned its place a
second time. Also surfaced: **`F2_runs/f2_ladder.py` is on disk and NOT in HEAD.**
