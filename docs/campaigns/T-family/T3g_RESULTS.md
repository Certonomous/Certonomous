# T3g — RESULTS. The T3 ladder now has its **first three-level Roache triple, 5 of 6 keys `CONVERGING`** — and behind the convergence barrier the chain removed sits a **reference barrier that was there all along**

**RUNG VERDICT: `BLOCKED`** — on a **named missing capability: the Vogel & Eaton 1985 primary
reference was NOT OBTAINED.**

> Tally from the registered path, not composed: **`PASS` 0 · `GATE FAIL` 0 · `NOT A RESULT` 1 ·
> `BLOCKED` 3 · `REPORTED` 0.** Three of the four graded rows carry
> `[reference NOT OBTAINED: Vogel and Eaton 1985 primary not held]`. **`BLOCKED` is the honest
> label under rule 1 because the missing thing is named and is a capability, not a defect in the
> measurement.**

**Cost: ZERO solver core-minutes** — one Python grade over cases already on disk.

---

## 1. THE LADDER GRADED, AND THAT IS THE THING THAT CHANGED

`r21 = 1.5989`, `r32 = 1.5986` over 92,160 / 235,520 / 602,128 cells. **The ladder refines and the
grader confirmed it rather than being told.**

| row | key | triple (c, m, f) | grid state | `p` | GCI | verdict |
|---|---|---|---|---:|---:|---|
| **G1** | `St_peak` | 0.00343791, 0.00350859, 0.00356233 | **CONVERGING** | **0.585** | 5.975 % | `BLOCKED` |
| **G2** | `x_peak_H` | 6.13516, 6.1412, 6.13833 | **OSCILLATORY** | — | — | `NOT A RESULT` |
| **G3** | `St_10H` | 0.00304705, 0.00310443, 0.00314654 | **CONVERGING** | **0.660** | 4.608 % | `BLOCKED` |
| **G4** | `St_20H` | 0.0022961, 0.00233824, 0.002369 | **CONVERGING** | **0.672** | 4.379 % | `BLOCKED` |
| **M1** | `x_R_H` | 7.01011, 6.98336, 6.9623 | **CONVERGING** | 0.510 | — | `REPORTED` |

**All six triple keys: 5 of 6 `CONVERGING`** (`St_peak`, `St_10H`, `St_20H`, `x_R_H`, `Cf_15H`);
`x_peak_H` alone is `OSCILLATORY`.

**This ladder has never had a three-level triple before.** T3d, T3e and T3f existed to remove rule 5
clause (1) as a barrier, and they did: every level is independently converged on both fields, and
the grid triples formed.

---

## 2. PREDICTIONS — TWO HIT, TWO MISSED, AND THE MISSES ARE THE INFORMATIVE ONES

| | prediction | result |
|---|---|---|
| **P-1** | `St_peak` triple is `CONVERGING` | **HIT** |
| **P-2** | observed order on `St_peak` in `[1.0, 3.0]` | ⚠ **MISS — `p = 0.585`. FALSIFIED.** |
| **P-3** | ≥ 3 of 6 triple keys `CONVERGING` | **HIT — 5 of 6** |
| **P-4** | ≥ 1 graded row reaches `PASS` or `GATE FAIL` | ⚠ **MISS — 0 did.** |

> ### ⚡ **P-2's FALSIFICATION IS THE PHYSICS RESULT OF THIS RUNG.**
> **Every observed order is between 0.51 and 0.67 — sub-first-order, on a nominally second-order
> discretisation.** `St_peak` 0.585, `St_10H` 0.660, `St_20H` 0.672, `x_R_H` 0.510. The registered
> band `[1.0, 3.0]` was already wide, and **the measurement is not near its lower edge — it is
> roughly half of it.** GCI accordingly runs **4.4 – 6.0 %**, which is large for a three-level
> ladder spanning a 6.5× cell-count range.
>
> **The band was chosen before the run and it is not being widened after it.** A ladder whose
> observed order is ~0.6 is telling us something about the discretisation, the turbulence closure's
> mesh sensitivity, or the confound in §3 — and which of those it is, this rung does not determine.

**P-4's miss is not a failure of the ladder.** No row reached `PASS` or `GATE FAIL` because three
rows never reached their band at all — **the reference was not there to compare against** (§4).

---

## 3. ⚠ THE TRIPLE CARRIES ONE NON-MESH DIFFERENCE, AND THE GRADER QUOTES IT ON EVERY ROW

Verbatim from the graded output:

> `CAVEAT R_fz and R_ff ran decomposed (8 ranks, simple (8 1 1)); R_m and R_f ran serial. The
> triple carries ONE non-mesh difference, floating-point summation order (F15 RULING 2,
> T3_R_FF_PREREGISTRATION.md §5). Quoted on every row.`

**This is a registered, pre-existing confound, not something T3g introduced** — it entered when
`R_ff` was run decomposed. **It is material to §2's finding:** a sub-first-order observed order on a
triple whose fine level differs from its coarse levels in summation order is **not cleanly
attributable to mesh refinement alone.** The grader carries the caveat on every row rather than in a
footnote, which is why it is repeated here rather than softened.

**A successor that wants a clean order must run the coarse levels decomposed too** — that is a
registered design question, not a repair, and it is not attempted here.

---

## 4. ⚡ THE BARRIER BEHIND THE BARRIER — AND IT WAS THERE ALL ALONG

**Three of four graded rows are `BLOCKED` on `reference NOT OBTAINED: Vogel and Eaton 1985 primary
not held` (`T3_PREREGISTRATION.md` §2).** The ladder is now grid-converged and **still cannot be
compared to anything**, because the primary reference has never been acquired.

> **THIS IS §2ap.1's LESSON RECURRING AT LADDER SCALE, AND IT IS THE MOST IMPORTANT SENTENCE IN
> THIS RECORD:** *"A registration can carry two independent fatal defects, and the outer one hides
> the inner one until it is resolved. **Clearing a blocker is not evidence that a case is
> gradeable.**"*
>
> T3d → T3e → T3f spent **7,330.933 core-minutes** removing the **convergence** barrier. Behind it
> sat a **reference-acquisition** barrier that no amount of iteration could touch. **The work was
> not wasted — the ladder genuinely converged, 5 of 6 triples formed, and the observed order is now
> a measured number where before it did not exist — but it did not reach the gate it was aimed at,
> and the reason was never going to yield to compute.**

**On Sanaa's desk, as a named capability request:** the **Vogel & Eaton 1985 primary** for the
heated backward-facing step. **Same class as K0d's Blay 1992** — a missing paper, not a missing
solver, and therefore **not** in the OpenFOAM-exemption class of her 2026-09-04 order.

---

## 5. RULE 5, APPLIED AND NOT WAIVED

Clause (1) is satisfied at all three levels — that is what the chain bought. Clause (2) then fired
on `x_peak_H`: **`OSCILLATORY` → `NOT A RESULT` whatever its value**, and no band is armed on it.
**GCI is quoted only on the `CONVERGING` rows**, at `Fs = 1.25` via the grader's `gci_unequal` for
unequal ratios. **No GCI is quoted for `x_peak_H`.** The gate turned no `PASS` or `GATE FAIL` into
`NOT A RESULT` and could not have done the reverse.

---

## 6. RULE 12

**ZERO solver core-minutes.** POINT 0.5, actual ≈ 0.4 core-min of interpreter time; **$0.0004
DERIVED** at $0.0513/core-h, reported-by-owner, never measured. **No calibration row is filed:** a
ratio on 0.4 core-min of Python against a 0.5 estimate is noise, not a calibration datum, and
entering it would dilute a ledger whose purpose is solver-cost prediction. **The compute that made
this rung possible is already recorded** — T3d `C-…a636135b`, T3e `C-…a5e0172b`, T3f
`C-…ed39a6ab`.

---

## 7. WHAT THIS DOES **NOT** ESTABLISH

- **It does not compare the model to experiment.** Three rows are `BLOCKED` for exactly that reason.
- **It does not establish the discretisation order of the scheme.** It measures the *observed* order
  of this ladder, on a triple carrying the §3 confound.
- **It does not repair `R_fx` or `build_t3d.py`.** T3d's `NOT A RESULT` stands.
- **It does not claim the ladder is finished.** It is grid-converged and reference-blocked.
- **No `PASS` is claimed anywhere in this record.**

---

## 8. WHAT THE CHAIN ACTUALLY BOUGHT, STATED PLAINLY

Before T3d: the fine level was not converged, its `CASE.txt` was unreadable by the grader, and **no
triple existed at all.** After T3g: **all three levels converged, 5 of 6 triples formed and
`CONVERGING`, observed orders and GCIs measured for the first time, and the remaining barrier
identified and named.** The ladder moved from *ungradeable for unknown reasons* to *grid-converged
and blocked on one named, acquirable thing.* **That is progress, and it is not a `PASS`.**
