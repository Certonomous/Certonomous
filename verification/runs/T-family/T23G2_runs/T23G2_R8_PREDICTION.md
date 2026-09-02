# T23G2 — REPAIR `R8`: THE PREDICTION, WRITTEN BEFORE THE REPAIR WAS MADE

**Written 2026-09-02 by a `heat-transfer` lane, BEFORE `g_ratio` was edited and
BEFORE the post-repair capture was produced.** A judgement recorded in advance is
a prediction; the same judgement made afterwards is a rationalisation. This file
exists so the second cannot be mistaken for the first.

**Nothing in this file grades anything. No solver was launched.**

---

## 1. THE COST, PRE-REGISTERED — `CLAUDE.md` RULE 12

| item | value |
|---|---|
| **pre-registered solver compute** | **0 core-min** |
| **pre-registered cost** | **$0.00** |
| `cost_basis` | **NOT APPLICABLE — no solver compute is incurred.** Every invocation is a read of artifacts already on disk under `verification/runs/T-family/T23G2_runs/`. |
| pre-registered invocation count | **5** — one reproduction control, one pre-repair baseline capture, one post-repair capture, one gate positive control, one mutation demonstration |
| pre-registered cap | **any solver launch at all is an overrun and stops the work.** `R8` is a comparator change graded over existing fields; there is no case to run. |

Wall time of a comparator invocation is single-rank and under two minutes, which
rounds to **0.0 core-min** at the lab's unit. Actual-versus-predicted is compared
in `T23G2_RESULTS.md`'s `R8` amendment, per rule 12's calibration clause.

---

## 2. THE REPRODUCTION CONTROL — RUN FIRST, AND IT DID **NOT** REPRODUCE BYTE-IDENTICALLY

Before `g_ratio` was touched, the **unrepaired** comparator was re-run over
`verification/runs/T-family/T23G2_runs` and diffed against
`T23G2_GRADE_POST_R7.out`. **The diff is NOT empty** `[MEASURED]`, and the cause is
established rather than assumed.

### 2.1 The capture convention, which is not drift

`T23G2_GRADE_POST_R7.out` is stdout **plus a trailing `EXIT_CODE=3` line** appended
by the capturing shell. A raw stdout redirect therefore differs from it by that one
line. The convention is reproduced here — every capture in this repair carries the
same trailing line — and it is named so it is not later read as a missing line.

### 2.2 The one genuine hunk, and it is somebody else's committed work

```
   docs/campaigns/T-family/T23G2_PREREGISTRATION.md
-      post-repair (working tree) : b2721aaad40124c2aeb85055aee716fb35805764
-      pre-registration (frozen)  : b2721aaad40124c2aeb85055aee716fb35805764   IDENTICAL
+      post-repair (working tree) : 0b597ba9544819552b085c93a67520c443bbc274
+      pre-registration (frozen)  : b2721aaad40124c2aeb85055aee716fb35805764   DIFFERS
```

**CAUSE, MEASURED AND NAMED: commit `b1d9070c`, `T23G2_PREREGISTRATION` v1.3
`ADDENDUM A3`**, landed after `R7`'s capture was taken at 23:01Z. It corrects §7's
comparator **path text** to the path the comparator actually occupies — the repair
`VERIFICATION_CHARTER.md` §2d.4.2 and §2d.9.2 expressly licensed, *"you repair the
record to match reality, never reality to match the record."* Measured against the
freeze commit `976776f4`: **112 lines inserted, 0 deleted** — a pure append. The
addendum's own head line states **gates 0, thresholds 0, caps 0, labels 0**, and a
grep of its added lines for `ORDER_BAND`, `RATIO_MIN`, `BAND_Q1`, `threshold` and
`cap` returns only that self-declaration.

**IT IS INSPECTED, NOT REVERTED** (`CLAUDE.md` rule 10). It is a peer's committed,
licensed work and `R8` leaves it exactly where it is.

### 2.3 What that costs, and what replaces it

`T23G2_GRADE_POST_R7.out` **cannot be reproduced byte-identically today**, and no
`R8` capture can be diffed against it cleanly. **So the baseline for `R8` is not
`R7`'s capture; it is a fresh pre-repair capture taken from today's tree**, with the
unrepaired comparator, immediately before the edit:

| capture | file | sha256 |
|---|---|---|
| `R7`'s post-repair capture, 23:01Z | `T23G2_GRADE_POST_R7.out` | `dc79492b765a5c7a473119a47ec1364303a7cce420ff42098e6a395adfecc99a` |
| **`R8`'s pre-repair baseline, today's tree** | `T23G2_GRADE_PRE_R8.out` | `39f4fce40686f53b337ea1d34f8140d50a073868f7c9d959bc70d7812f163e34` |

Diffed against each other these two differ in **exactly one hunk, the four lines
quoted at §2.2, and in nothing else** `[MEASURED]` — every gate line, every value,
every verdict and the exit code are byte-identical. **That is what re-establishes
attribution:** the pre-versus-post diff below is taken against a capture produced by
the same unrepaired code over the same tree that `R8` will run on.

### ⚠ 2.4 THE BRIEFED DIFF CONDITION IS ALREADY FALSE BEFORE `R8` EXISTS, AND IS RESTATED

The lane was briefed to assert the post-repair diff moves **only** the `G-RATIO`
lines and the comparator's own blob line. **Against `T23G2_GRADE_POST_R7.out` that
condition is unsatisfiable and would have been unsatisfiable had `R8` never been
written**, because a third line — the pre-registration's blob — moved for a reason
that has nothing to do with this repair. This is `VERIFICATION_CHARTER.md` §2q.1's
exact shape: *a stop condition names in advance the mechanical consequences that do
not count as drift.* The condition is therefore restated against the baseline that
makes it meaningful, and both diffs are published.

---

## 3. THE PREDICTED DIFF — `T23G2_GRADE_PRE_R8.out` → `T23G2_GRADE_POST_R8.out`

**Predicted before the repaired comparator was run. Three hunks, and every one is
declared here.**

### PREDICTED HUNK 1 — capture line 13. **Mechanical. Its NON-movement is the finding.**

```
-      post-repair (working tree) : d2187518bc3b257d6305db7ac4a4f3c06b746f39
+      post-repair (working tree) : <a value that is NOT d2187518…>
```

`grading_path_shas()` at `analyse_t23g2.py:1020` runs `git hash-object` on the
**working-tree** file. Editing `g_ratio` changes that file's blob, and the `R2`
recorder exists to print it. **A recorder blind to an edit of its own file would be
worthless, so this line MUST move; if it does not, the finding is the recorder, not
the repair.** The `pre-registration (frozen)` column beside it stays
`cc723d6f65245674f7d80c51de55fe986549477a` and stays `DIFFERS`. Carries no verdict,
no value, no gate, no band, no threshold.

### PREDICTED HUNK 2 — capture lines 98–103. **The six `G-RATIO` per-quantity cells.**

Six lines, `Q1`…`Q6`, each keeping every printed number and changing only its
trailing verdict word:

```
-  Q1  plateau PLAT/PLAT/PLAT | finest iterative change 0.000000e+00, smallest inter-level difference 6.751504e-01, ratio inf (needs >= 10)  PASS
+  Q1  plateau PLAT/PLAT/PLAT | finest iterative change 0.000000e+00, smallest inter-level difference 6.751504e-01, ratio inf (needs >= 10)  NOT A RESULT
```

**PREDICTED: no number moves.** The finest iterative change stays `0.000000e+00` on
all six; the smallest inter-level differences stay `6.751504e-01`, `6.678506e-01`,
`6.708475e-01`, `6.664925e-01`, `2.652514e-05`, `6.676643e-01`; the printed ratio
stays `inf`; `needs >= 10` stays, because `RATIO_MIN = 10.0` is untouched. Predicted
new lines: an explanation block naming **both** ruled grounds, the voided level
`T23G2_L2`, and the fact that the band is untouched.

### PREDICTED HUNK 3 — capture line 104. **The `G-RATIO` summary cell.**

```
-  G-PLATEAU: PASS    G-RATIO: PASS
+  G-PLATEAU: PASS    G-RATIO: NOT A RESULT
```

**`G-PLATEAU` is predicted UNCHANGED at `PASS`** — `R8` touches `g_ratio` and the
`G-RATIO` rollup only.

### PREDICTED: NOTHING ELSE MOVES

- `RUNG VERDICT: NOT A RESULT` — **unchanged**, and `EXIT_CODE=3` — **unchanged**.
  The rollup already carried `NOT A RESULT` from `G-CONV` `GATE FAIL`, `G-YPLUS`
  `GATE FAIL`, five rows voided at rule 5 step (a) and `G-ORDER` `NOT A RESULT`
  under `R7` — every one established before `R8` existed. **`R8` moves a cell, not
  the rung.**
- `G-ORDER` — unchanged at `NOT A RESULT`, `p(Q4) = 0.6111` still printed.
- `A2.1`'s `p(Q4) = 0.6111, p(Q1) = 0.6148, spread = 0.0036` — unchanged.
- The `T23G2_PREREGISTRATION.md` blob line — unchanged between these two captures;
  its movement is confined to §2.2 above.

**Any fourth hunk, or any movement in a number, a band, the rung verdict or the exit
code, is a STOP-AND-REPORT condition and is not to be explained after the fact.**

---

## 4. WHAT `R8` IS PREDICTED TO CHANGE IN THE CODE

`docs/campaigns/T-family/analyse_t23g2.py`, `g_ratio` and its single call site.
Predicted **strictly restrictive**: `PASS`/`GATE FAIL` → `NOT A RESULT` only, never
the reverse. Predicted untouched: `RATIO_MIN = 10.0` at `:106`, the registered
meaning of `G-RATIO`, every other gate, and `T23G2_PREREGISTRATION.md`. Predicted
new criteria, thresholds and state names: **0**.

---

## 5. THE POSITIVE CONTROL — PREDICTED RESULTS, BEFORE IT WAS WRITTEN

`VERIFICATION_CHARTER.md` §2p.3(e), ruled at commit `c4007e42`: every restrictive
repair carries a positive control driven through the **production** path.

| control | predicted |
|---|---|
| as-measured `T23G2_L2 NOT CONVERGED` | `NOT A RESULT` |
| **plant — all levels `CONVERGED`/`PLATEAUED`, non-zero iterative change, ratio above `RATIO_MIN`** | **`PASS`** |
| **plant — all levels converged, ratio BELOW `RATIO_MIN`** | **`GATE FAIL`** |
| plant — all levels converged, iterative change exactly `0.0` | `NOT A RESULT` (the degenerate-path ground alone) |
| plateau limb alone | `NOT A RESULT` |
| iterative states never supplied | refusal |
| exact zero with no planted-zero control | refusal (`R5`, unchanged) |

**And the control must itself be shown to fail when the shipped `g_ratio` is
mutated**, or the control is the §2p.7 limb-(d) defect it was built to exclude.
`__pycache__` is cleared between every run.
