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
