# T3g — grade the T3 ladder at `c = R_m`, `m = R_f`, **`f = R_fz`**: the first three-level Roache triple this ladder has ever had, at **ZERO SOLVER COMPUTE**

> **STATUS AT THIS COMMIT: DRAFT. NOT FROZEN. NOT GRADED. AUTHORISES NOTHING.**
> **No triple, no observed order, no GCI and no row value has been computed by anyone for this
> ladder at these three levels.** The grader has been **read as source** (its gate structure, its
> `ratios_from_ncells`, its six triple keys) and **has NOT been run on this data.** Freeze precedes
> grading, and the predictions below are made blind.

**Authored personally by `heat-transfer-supervisor`.** The `Agent` tool remains **DENIED** for this
team; the denial is disclosed, not routed around.

---

## 1. WHY THIS RUNG EXISTS NOW AND COULD NOT HAVE EXISTED BEFORE

The T3 ladder's fine level was ungradeable for two independent reasons, and **both are now gone**:

**(a) RULE 5 CLAUSE (1) — the fine level was not iteratively converged.** T3d left `|U|` at
`3.68937e-06` against `tol = 1e-06`. T3e proved the non-convergence was **decaying, not stalled**
(`GATE REACHED`). T3f drove it to **`8.99782e-07` — CONVERGED** (`PASS`). **Measured now, on all
three levels, both fields:**

| level | case | `T` state | `T` `relative` | `\|U\|` state | `\|U\|` `relative` |
|---|---|---|---:|---|---:|
| `c` | `R_m` | `CONVERGED` | 1.53525e-08 | `CONVERGED` | 8.75394e-09 |
| `m` | `R_f` | `CONVERGED` | 9.67949e-08 | `CONVERGED` | 7.79644e-08 |
| `f` | **`R_fz`** | `CONVERGED` | 2.41648e-07 | `CONVERGED` | **8.99782e-07** |

**(b) T3d's `CASE.txt` DEFECT — the grader could not read the fine level's inputs.**
`build_t3d.py` wrote `R_fx/CASE.txt` as prose; `analyse_t3.py:461-468` reads seven numeric keys and
refused on `H`. **`R_fz` was built by `build_t3f.py`, which writes the structured block, and is
READABLE.** Measured with the frozen `case_val` on all four cases: **`R_m` READABLE, `R_f`
READABLE, `R_fx` REFUSED, `R_fz` READABLE.** The defect is isolated to `R_fx` and **T3g routes
around it by using a level that does not carry it — not by repairing a frozen artifact.**

`DONE.R_m`, `DONE.R_f`, `DONE.R_fz` all present.

---

## 2. THE LADDER

`LADDER = {"c": "R_m", "m": "R_f", "f": "R_fz"}`. Cell counts **92,160 / 235,520 / 602,128**;
the grader derives `r21`, `r32` from `nCells` itself and **refuses if either is ≤ 1**.

⚠ **A REGISTERED ASYMMETRY, DECLARED RATHER THAN DISCOVERED.** `R_m` and `R_f` ran **20,000
iterations from scratch**; `R_fz` is the **fourth continuation** of `R_ff` (118,000 + 24,000 +
8,000 + 8,000 = 158,000 cumulative). **The three levels are therefore NOT equal in iteration
history.** That is admissible for a grid-convergence study **only because every level is
independently iteratively converged** (§1a), which is exactly what rule 5 clause (1) demands and
what §1 measures. **It is registered here so no reader mistakes it for an oversight, and a
successor that finds it material has this sentence to cite.**

---

## 3. PREDICTIONS — MADE BLIND, AND EVERY ONE FALSIFIABLE

**P-1 — the primary triple `St_peak` is `CONVERGING`.** **F-1: any other state
(`DIVERGENT`, `STAGNANT`, `OSCILLATORY`, `EXACT`) falsifies it**, and under rule 5 makes that row
`NOT A RESULT` whatever its value.

**P-2 — the observed order on `St_peak` lies in `[1.0, 3.0]`.** The discretisation is nominally
second order; the band is wide because a RANS peak quantity on a recirculating flow is not
guaranteed to show its formal order. **F-2: `p` outside `[1.0, 3.0]`, or not computable.**

**P-3 — at least THREE of the six triple keys** (`St_peak`, `x_peak_H`, `St_10H`, `St_20H`,
`x_R_H`, `Cf_15H`) **are `CONVERGING`.** **F-3: fewer than three.**

**P-4 — at least one registered graded row escapes `NOT A RESULT`**, i.e. reaches `PASS` or
`GATE FAIL`. **F-4: every row `NOT A RESULT`** — which would mean the ladder is still ungradeable
after 40,000 additional iterations, and is a finding worth having.

> **NOTHING HERE PREDICTS A `PASS` AGAINST THE REFERENCE.** Whether the measured Stanton peak
> agrees with Vogel & Eaton is **not** predicted: this rung's question is whether the ladder is
> *gradeable*, not whether the model is *right*. **A `GATE FAIL` against the reference would fully
> satisfy P-4 and is an honest completion.**

---

## 4. THE GATE

**The gate, its thresholds, its bands, its reference and its labels are `analyse_t3d.py`'s,
INHERITED UNCHANGED.** `analyse_t3g.py` differs from it in the **ladder's `f` entry, the output
filename and the rung label, and in nothing else** — and that is **delta-proved**, not asserted:
reversing the substitutions must reproduce `analyse_t3d.py` with **0 differing lines** (§6).

**RULE 5 APPLIES IN FULL AND IS NOT WAIVED.** A row whose triple is not `CONVERGING` is
**`NOT A RESULT`** whatever its value. **GCI at `Fs = 1.25`** via the grader's own `gci_unequal`
for unequal ratios; **no GCI is quoted where the three values are not monotone.** The gate can turn
a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse.

**All outcomes gradeable:** every graded row `PASS` → rung `PASS`; any `GATE FAIL` with no
`NOT A RESULT` → rung `GATE FAIL`; any `NOT A RESULT` → that row is `NOT A RESULT` and the rung is
reported by tally, following this family's standing convention (T24, T5b, T19b, T10aVF).

---

## 5. COST — RULE 12

**ZERO SOLVER CORE-MINUTES.** All three cases are complete and on disk; this rung runs one Python
grade. **POINT 0.5 core-min, CAP 1.5 core-min** (interpreter time on one core). **$0.0004
DERIVED** at $0.0513/core-h, reported-by-owner, never measured.

**The compute that made this possible is already spent and already calibrated elsewhere** — T3d
4,723.200, T3e 1,382.933, T3f 1,224.800 core-min, each with its own row. **T3g adds no compute and
duplicates no row.**

---

## 6. THE §2ap REHEARSAL — SCOPED TO WHAT IS ACTUALLY NEW

There is **no builder**: all three cases exist. The producer→consumer pair at risk is
**`CASE.txt` → grader**, and it is exactly the pair that killed T3d.

1. **READ** — the frozen `case_val` reads all seven keys from **each of the three ladder cases**,
   naming them. *(Driven pre-registration; `R_fx` REFUSED and `R_fz` READABLE, which is why the
   ladder moves.)*
2. **CORRUPTION** — a key removed from a **scratch copy** of a ladder case's `CASE.txt` makes the
   grader **REFUSE at exit 2**. Nothing in the real cases is touched.
3. **DELTA** — reversing the registered substitutions reproduces `analyse_t3d.py` byte-for-byte,
   **0 differing lines**.
4. **SELFTEST** — `analyse_t3g.py --selftest` passes, including the `DONE` refusal arm.

**§6.1 — the freeze.** §7 pins `analyse_t3g.py` by git blob sha. **Until that pin exists this
document authorises no grade.**

---

## 7. ARTIFACTS AND PINS

**NOT YET CUT.**

---

## 8. WHAT THIS DOCUMENT DOES **NOT** DO

- It **does not freeze**, and it **does not grade**. No triple, order, GCI or row value exists yet.
- It **does not move** any gate, threshold, band, reference or label; all are `analyse_t3d.py`'s.
- It **does not repair** `R_fx` or `build_t3d.py`. **T3d's `NOT A RESULT` stands and is not re-graded.**
- It **does not claim** the ladder will grade. **P-4 can lose, and its loss is a finding.**
- It **does not assert any verdict**; no term of rule 1's vocabulary is claimed for T3g.

---

## AMENDMENT 1 — 2026-09-06 — **T3g IS FROZEN. THE FOUR REHEARSAL LEGS PASSED AND §7's PIN IS CUT.**

**Appended by `heat-transfer-supervisor`. Lines whose number changed above this section: 0.**
**No gate, threshold, band, reference or label moves — all are `analyse_t3d.py`'s, inherited.**

**PRE-FREEZE CONDITION, CHECKED IN THE COMMITTING INVOCATION:** no `gate_t3g.json` exists; the
grader has not been run on the ladder; **no triple, observed order, GCI or row value has been
computed for these three levels by anyone.**

**§6's legs all PASSED.** **Leg 3 delta: 0 differing lines** on reversal. **Leg 4 selftest: PASS,
0 checks failed**, including the `DONE` refusal arm. **Leg 2 corruption: a plant removing `H`
from a scratch copy gave `rc = 2`, `REFUSE: H absent`** — the guard is alive.

⚠ **TWO DEFECTS THE REHEARSAL CAUGHT, BOTH MINE, RECORDED BECAUSE A CLEAN REHEARSAL LOG WOULD
HIDE THEM.** (1) The derived grader was first placed in `T3g_runs/` and could not import
`analyse_t3`, which lives in `T3_runs/` — `analyse_t3d.py` worked only because it sits beside
it. Fixed by placing `analyse_t3g.py` where its sibling lives, which also keeps the delta at 0.
(2) **My first corruption plant reported "GUARD IS DEAD". It was my test rig** — the scratch copy
excluded the time directories, so the grader failed earlier and never reached the guard.
**A PLANT NEEDS ITS OWN POSITIVE CONTROL: verify the harness REACHES the guard before concluding
the guard is dead.**

### §7 — THE PIN

| artifact | git blob SHA-1 |
|---|---|
| `verification/runs/T-family/T3_runs/analyse_t3g.py` | `4523fd047b759a179f1f54107063f2160e65143b` |

**§6.1's condition is met and this document is FROZEN.**
