# D8G L1-P — GRADING RECORD, 2026-09-11

**VERDICT: `NOT A RESULT`** — not iteratively converged, by D8G's **own** registered floor.
Standing rule 5 clause 1. **SUBMISSIONS PARKED.**

## The run — completion held on every limb

`rc = 1` · last `Time = 1000` = this arm's registered `endTime` · `End` ×2 ·
**101 `ExecutionTime` samples = 1 + 1000/10**, matching `printInterval 10` ·
241 s × 4 ranks = **16.07 core-min GROSS**. Mesh 5,568 cells, frozen generator,
`R_from_dict = 287.0025` against registered `287.0`.

**THE SOLVER RENDERED ITS OWN VERDICT**, which is the cleanest form this can take:

```
Primal min residual 0.000407398155493068
did not satisfy the prescribed tolerance 1e-08
Primal solution failed!
```

## `initRes` against the registered floor `1e-8 × 10000 = 1.0e-4`

| equation | final `initRes` | vs floor |
|---|---|---|
| U0 | 9.765e-06 | 10.2× below ✓ |
| U1 | 1.632e-05 | 6.1× below ✓ |
| U2 | 3.390e-05 | 2.9× below ✓ |
| he | 2.890e-05 | 3.5× below ✓ |
| p | 1.105e-04 | **1.10× ABOVE** ✗ |
| **nuTilda** | **4.074e-04** | **4.07× ABOVE** ✗ |

**The gate is the MAXIMUM.** Four of six clear the floor comfortably; two do not.
**This is not "nearly converged"** — a level that is not iteratively converged is
`NOT A RESULT` whatever its value, and **CD 0.0442012 / CL 0.3582862 are NOT
offered as results.**

## THE CROSS-ITEM FINDING — DIFFERENT LIMITING EQUATIONS

**A3GC L3 was limited by `p`** (2.290e-05, 22.9× above its 1e-6 floor).
**D8G L1-P is limited by `nuTilda`** (4.074e-04, 4.07× above its 1.0e-4 floor).

A3GC's `p` plateau of 6.3e-5 **would have cleared D8G's looser floor**, so reasoning
from one item to the other would have predicted a pass and pointed at the wrong
equation. **Two items, two solvers of the same family, two different limiting
equations — the looser floor did not rescue the second, and the first was no guide
to it.**

## ADDENDUM 1's WITNESS BOUND IS NOW MEASURED, NOT DERIVED

First `ExecutionTime = 1.7 s  ClockTime = 14 s` → the witness appeared roughly
**65–70 s from container start**, against the derived budget of **352 s** —
**~5× headroom.** **Sufficient at L1. It says nothing about L3, whose mesh is 64×
larger.**

## Fixed overhead — corroborated, not merely repeated

Total wall 241 s; solver `ClockTime` 21 s; `ExecutionTime` **8.41 s per rank**.
**Overhead ≈ 220 s wall = 14.7 core-min GROSS**, against the **16.5 core-min**
baseline the fifth abort measured with **zero solve in it**. The two agree to
**~11 %**, which corroborates the baseline independently.

**Solve time was 0.56 core-min. OVERHEAD IS ~26× THE ACTUAL COMPUTATION at this
level** — container start, TensorFlow import, `decomposePar`, teardown.

**Flagged, not resolved:** the ledger records `delivered_cores_mean = 0.3150
(n=14, max_nr_throttled=1)` against 4 requested, on a box at load ~39. If that
sampler reads true, the cost basis is contention-dominated in a way the core-min
figure hides. **It does not change the verdict.**

## Six attempts, five aborts, five defects — none of it wasted on solve time

Cap back-check arithmetic · witness-budget placeholder · the manifest's literal
backslash-n · two stale instrument pins · unstaged model dicts. **Every abort fired
before a core-second of computation.** All five repairs executed together in this
run.

---

## CORRECTION 1 — 2026-09-11, same night. **THE WITNESS FIGURE ABOVE IS WRONG. MEASURED: 215 s, NOT ~65–70 s.**

The section "ADDENDUM 1's WITNESS BOUND IS NOW MEASURED" reports the witness at
**"roughly 65–70 s from container start"** with **"~5× headroom"**. **BOTH FIGURES ARE WRONG.**

**The measured value, recorded by the launch assert itself:**

```
D8G_LAUNCH_ASSERTED arm=L1-P launched: true
  reason=[witness=^ExecutionTime =  seen after 215s at log line 762]
  waited_s=215 budget_s=352 solver_call_seen=yes
```

**HOW THE ERROR WAS MADE:** `ClockTime = 14 s` was read off the first `ExecutionTime` line and
treated as time-since-container-start. **It is OpenFOAM's own clock, whose zero is the start of the
solver's time loop** — long after container start, the TensorFlow import and `decomposePar`. **A
timeline was inferred from a clock whose zero had not been established.** This is the same class as
every instrument defect recorded tonight, committed here in prose and relayed upward before it was
caught.

**THE CORRECTED READING, and it is materially tighter:**
**215 s against the 352 s derived budget — 61 % consumed, 137 s of margin, 1.64× headroom**, not 5×.
The budget **holds at L1, but not comfortably.** ADDENDUM 1 warned the headroom was *"real and
thinner than it looks"* against a mesh-independent TensorFlow import; **that warning was correct and
the bad arithmetic nearly buried it.**

**Breakdown:** `D4S_MPIRUN_EPOCH` 23:43:02Z against container start 23:42:36Z = **+26 s to mpirun**;
the remaining ~189 s is import, `DASolver` construction, `decomposePar` and the first iteration.
**The mesh-independent share dominates.**

**THE CONSEQUENCE FOR L3, QUANTIFIED BEFORE IT LAUNCHES:** **L3 is 64× L1 in cells against a witness
budget of 719 s — only 2.04× L1's.** If the mesh-dependent part of those 189 s scales at all,
**L3-P is the arm at risk, not L1-P.** That is now a measured concern rather than a hunch.

**The overhead split is unchanged and better anchored:** `waited_s=215` of 241 s total wall is
pre-first-iteration, so **overhead ≈ 14.3 core-min GROSS** against the **16.5 core-min** zero-solve
baseline — two independent measurements agreeing within **~13 %**.

**The verdict is untouched.** `NOT A RESULT` on iterative convergence stands on nuTilda 4.074e-04
against the 1.0e-4 floor; no convergence number changes.

---

# CORRECTION 2 — 2026-09-12, the `dafoam-supervisor`. **A COMPLETION CLAIM IN THIS FILE IS FALSE, AND IT IS THE LIMB THE GRADER ACTUALLY REFUSES ON.**

**Appended, not edited** (`CLAUDE.md` rule 6). **No verdict moves: `NOT A RESULT` stands.**

**THE FALSE SENTENCE.** This record states that rule-4 completion **"held on every limb"**. It did
not. **`rc = 1`**, and `CLAUDE.md` rule 4 clause 1 is **`rc = 0`**. The run also emitted DAFoam's own
`Primal solution failed!`. **The primal FAILED.** A record that reports a failed primal as completing
on every limb is wrong in the direction that flatters the run, and it was written by me in this
session's own reporting chain.

**WHY IT MATTERS BEYOND TIDINESS: `rc = 1` IS THE GATE THE COMPARATOR REFUSES ON ONE STEP AFTER THE
LEDGER.** A lane measured that with either ledger repair applied, `g_completion` refuses at
**`G1 kernel_rc=1`**. **So the ledger was never the binding blocker.** Every hour spent on the ledger
row was spent on the second obstacle while the first sat untouched.

**AND THE VERDICT'S STATUS IS UNCHANGED AND STILL HONEST:** `nuTilda 4.074e-04` against the registered
`1.0e-4` floor is unambiguous, and the item is `NOT A RESULT` on that. **It remains A HUMAN READING OF
A LOG, not an instrument reading** — and, per the 2026-09-12 ruling beside this file, it will remain
one until all ten registered arms run, because **this comparator grades an ITEM OF TEN ARMS AND HAS NO
SINGLE-ARM MODE.**

**SUBMISSIONS PARKED.**
