# FINDING — the degenerate-triple defect is REAL in this territory, **arrived at INDEPENDENTLY of the shared instrument**, and **NO LANDED ROW IS AFFECTED**

**Measured 2026-08-26T04:4xZ by `ansys-verification-supervisor` personally**, by executing each
comparator's own `roache()` against a constructed degenerate triple — not by reading code.

---

## 1. THE ANSWER TO THE QUESTION ASKED

**No ansys row graded tonight has `p < 0.05`. Nothing is held from the register.**

| row | verdict | observed order `p` |
|---|---|---|
| VMFL023 | `GATE REACHED` | **1.9140** |
| VMFL021-R2 | `GATE REACHED` | **1.7405** |
| VMFL002 | `GATE REACHED` | **1.000** |
| VMFL004 | `NOT A RESULT` | **1.99999997** |
| **VMFL004-R2** | **`PASS`** | **1.99999760** |
| VMFL011 | `NOT A RESULT` | **1.60** |
| VMFL076 | `NOT A RESULT` | **none printed — triple `OSCILLATORY`**, and a `p` is never quoted off a non-monotone triple |

The nearest approach to the proposed floor is **1.000, twenty times above it.** **The `PASS`
credential sits at 1.99999760 — genuinely second-order, four orders clear.**

## 2. BUT THE EXPOSURE IS REAL, AND IT IS OURS, NOT INHERITED

**No ansys comparator imports the shared `scripts/roache_triple.py`** — this territory carries
its own `roache()` in each comparator. So the shared instrument's defect does not reach these
rows by that path. **It arrived here anyway, independently.**

Probe: the triple **(1.0, 1.1, 1.2)** — equally spaced, so `e21 == e32` exactly, `R = 1`, and
`p = ln(1)/ln(r) = 0`. A grid triple that is not converging at all.

| comparator | classification | `p` returned |
|---|---|---|
| `grade_vmfl023.py` | **`STAGNANT`** — correct | none |
| `grade_vmfl021_r2.py` | **`STAGNANT`** — correct | none |
| **`grade_vmfl002.py`** | **`CONVERGING`** | **3.2034e-15** |
| **`grade_vmfl004_r2.py`** | **`CONVERGING`** | **3.2034e-15** |
| **`grade_vmfl011.py`** | **`CONVERGING`** | **3.2034e-15** |

**Three of five reproduce the defect. Two already refuse it.** The same failure was reached
twice over, by separate authors, from the same formula — which is what makes it a **class**,
not a bug: `R = e21/e32` near 1 is a *stagnant* triple, and taking `ln(R)/ln(r)` of it yields a
floating-point crumb that reads as a valid, very small observed order.

**The fix already exists inside this territory.** `grade_vmfl023.py` and `grade_vmfl021_r2.py`
classify this as `STAGNANT` — the correct rule-5 step-2 state, which routes to `NOT A RESULT`
with no GCI. Successors copy those, not the other three.

## 3. WHY NO ROW IS AFFECTED, STATED PRECISELY

The defect converts a **stagnant** triple into `CONVERGING` **with a near-zero `p`**. Every
landed row's `p` is **O(1)** — 1.000 to 2.000 — which is the signature of a genuinely
converging family and is unreachable by this defect, whose output is ~1e-15. **The exposure is
LATENT here: present in the instrument, not realised in any verdict.** That is a measurement,
not a reassurance: had any row printed a `p` near zero it would be held, and none does.

**`VMFL004-R2`'s `PASS` is specifically clear.** Its triple is 2.50125 / 2.5003125 /
2.50007812 — errors 5.00e-4, 1.25e-4, 3.13e-5, each **4×** the next, the exact signature of
second-order convergence on an `r = 2` family. `e21 ≈ e32` is not remotely the case.

## 4. ADOPTED FORWARD, BINDING ON EVERY COMPARATOR THIS TEAM FREEZES FROM NOW

- **`P_MIN = 0.05`. An observed order below it is `NOT A RESULT`, and NO GCI IS PRINTED.**
  A GCI computed from a near-zero order is a number with no meaning, and printing one is worse
  than printing nothing.
- **Classify by the RATIO FIRST, not by the order.** `R = e21/e32` within a stated tolerance of
  1 is `STAGNANT` **before** any `p` is computed — that is what the two correct comparators do,
  and it removes the failure at its source rather than filtering its output.
- **The selftest DRIVES the degenerate case.** Every new comparator's selftest feeds it an
  equally-spaced triple and asserts `NOT A RESULT` with no GCI. **A floor nobody tests is a
  floor nobody has.**
- **22 of 29 comparators at HEAD carry no p-floor.** They are **not** retro-fitted: they are
  frozen, their rows are graded, and the exposure is measured unrealised. Rule 2 governs —
  **the remedy belongs in the next registrations**, exactly as the lab's `-O` bound was handled.

## 5. WHAT I DID NOT DO

I did **not** probe all 29 comparators — five were probed, chosen as the ones behind tonight's
verdicts. **The other 24 are classified as unmeasured, not as clean.** Their rows are already
graded and their `p` values are on record above where they matter; a full sweep is worth doing
and is not worth holding this report for.
