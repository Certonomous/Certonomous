# T3e — RESULTS. The question T3d could not answer is answered: **`|U|`'s non-convergence is DECAYING, not stalled** — at a factor of 0.850 per 2,000 iterations, measured on three consecutive pairs

**RUNG VERDICT: `GATE REACHED`.**

> Taken from the registered path and **not composed**: `analyse_t3e.py` (pin
> `850a7496…`) printed `RUNG T3e GATE REACHED`. `|U|` did **not** reach `tol = 1e-06`
> (`1.77017e-06`), **but P-1 HOLDS** — the non-convergence is decaying.
> **Under rule 5 clause (1) the level is not iteratively converged, so NO ladder row is graded
> from it.** `GATE REACHED` is a verdict about the *trend question this rung registered*, not a
> licence to grade the T3 ladder.

**Cost: 1,382.933 core-min against a POINT of 1,574.4 — ratio 0.8784, 12.2 % under, 29.3 % of the
4,723 cap.** T3d spent **4,723.200** and produced no graded row. **T3e spent 29 % of that and
answered the question.**

---

## 1. THE PHYSICS — THE PAYLOAD

| pair | `T` `field_range` | `T` `relative` | `T` state | `\|U\|` `field_range` | `\|U\|` `relative` | `\|U\|` state |
|---|---:|---:|---|---:|---:|---|
| (2000, 4000) | 50.2889 | 5.97097e-07 | `CONVERGED` | 11.0325 | **2.45109e-06** | `NOT_CONVERGED` |
| (4000, 6000) | 50.2889 | 5.14306e-07 | `CONVERGED` | 11.0325 | **2.08526e-06** | `NOT_CONVERGED` |
| (6000, 8000) | 50.2890 | 4.42715e-07 | `CONVERGED` | 11.0325 | **1.77017e-06** | `NOT_CONVERGED` |

**`|U|` IS STRICTLY DECAYING: 2.45109e-06 > 2.08526e-06 > 1.77017e-06.** **P-1 HITS.**

**The decay is geometric and remarkably steady: ratios 0.8507 and 0.8489, mean 0.8498 per 2,000
iterations.** Two independent intervals agreeing to **0.2 %** is what makes the trend a trend
rather than two points and a hope.

> **⚠ THE EXTRAPOLATION, LABELLED AS ONE AND NEVER AS A MEASUREMENT.** Holding that factor,
> `|U|` would reach `1e-06` in **~7,000 further iterations** (3.51 intervals). **This is an
> extrapolation from three points under an assumed geometric law. It is not measured, it is not
> gated, and no verdict rests on it.** The registration required it be stated in exactly these
> terms (§3), and a successor that runs 7,000 more iterations may find the factor drifts.

**`T` also decays and stays converged throughout** — 5.97e-07 → 5.14e-07 → 4.43e-07, every pair
below `tol`. **P-2 HITS.**

**The `field_range` is stable and non-zero on every pair and both fields** (50.289 K and 11.0325),
so **D-J1 never fires and could not have.** Every `convergence_state` above is emitted with its
denominator beside it — the discipline T3d's gate JSON would have omitted.

**What this settles.** T3d ended at `3.68937e-06` with **one** pair on disk, and whether that was a
plateau or a descent was undeterminable. **It was a descent.** The fine level is converging, slowly,
and the ladder's fine row is not lost — it is unfinished.

---

## 2. ⚠ P-3 IS FALSIFIED — AND MY OWN GRADER DOES NOT SCORE IT

**P-3 registered "no restart spike"**, with **F-3: a residual maximum above the seed value in any
solved field falsifies it.** Measured:

| field | first residual | maximum | spike |
|---|---:|---:|---|
| `T` | 4.788625e-09 | 4.788625e-09 | **NO** |
| `Ux` | 9.957551e-10 | 9.957551e-10 | **NO** |
| **`p_rgh`** | 4.810986e-10 | **9.613286e-10** | **YES — 2.0×** |
| `k` | 3.164856e-10 | 3.171633e-10 | YES — 1.002× |
| `omega` | 9.933710e-12 | 1.000335e-11 | YES — 1.01× |

**`p_rgh` exceeds its seed value by 2×, so P-3 IS FALSIFIED on its own registered falsifier.**
The excursion is tiny in absolute terms (9.6e-10) and decays, but **F-3 is written over the
*maximum*, not over its magnitude, and it is reported as it was registered.** T3d saw the same
shape at 5.6 %; T3e's is larger.

> ### **AND THE DEFECT IS MINE: `analyse_t3e.py` DOES NOT SCORE P-3.**
> The registration declares P-1, P-2 **and P-3**; the grader scores **P-1 and P-2 only.** The table
> above was measured **out-of-band, by hand, from `log.solve` — NOT by the registered path** — and
> is labelled that way rather than presented as a graded row.
>
> **THIS IS A NEW INSTANCE OF THE §2ap CLASS, IN A PAIR §2ap DOES NOT COVER.** §2ap rehearses
> **builder → grader** (can the consumer read the producer's output?). It does **not** rehearse
> **registration → grader** (does the grader score every prediction the registration declares?).
> **T3e's rehearsal passed all four legs and this still got through**, because no leg asked the
> question. **Reported upward as an extension candidate; not fixed here — the grader is pinned and
> the rung has fired.**

---

## 3. RULE 4 — THE MARKER WAS EARNED, THROUGH THE PRODUCER REGISTERED BEFORE COMPUTE

`python3 mark_done_t3.py --root T3_runs R_fy` → **`1/1 cases meet the strict completion rule`**,
exit 0, `DONE.R_fy` written. Recorded at `T3e_runs/T3e_MARK_DONE_R_fy_OUTPUT.txt`.

**This is D-2's repair working.** T3d had no registered producer and needed a charter ruling to
obtain one; **T3e registered `mark_done_t3.py` by name and git blob sha in §6, before compute**, and
the marker was simply earned. `STATUS.R_fy`: `rc=0`, `ranks=8`, `capped=no`, `checkmesh_rc=0`,
`core_min=1382.933`.

**All four pins verified byte-identical to HEAD at grading time** — `build_t3e.py` `478f6c1c…`,
`analyse_t3e.py` `850a7496…`, `launch_t3e.sh` `2e434475…`, `mark_done_t3.py` `5da28c73…`.
**The frozen files are the files that ran.**

---

## 4. D-3's REPAIR, PROVEN ON DISK

`purgeWrite 0` was registered so that a trend could be measured. **Four checkpoints survived —
`2000`, `4000`, `6000`, `8000` — giving the three consecutive pairs.** T3d's `purgeWrite 2` left
**one** pair and made the question unanswerable after 4,723 core-min. **The single setting is the
whole difference between a rung that answers and a rung that cannot.**

**Rule 3 control fired before any pair was classified:** a `1.234e-03 K` plant into the later
checkpoint moved the reader by `1.211736e-03` — **PLANT SEEN**. The zeros and near-zeros above come
from a reader shown able to see a non-zero.

---

## 5. RULE 5 — STATED BECAUSE IT CONSTRAINS EVERYTHING ABOVE

**NO ROACHE TRIPLE IS FORMED.** One mesh, one refinement. **No observed order, no GCI, no
Richardson extrapolate is computed, quoted or derivable, and EVERY NUMBER IN THIS RECORD CARRIES NO
DISCRETISATION BOUND AT ALL.** Clause (1) **is** reached and applied: the level is not iteratively
converged, so **no T3 ladder row is graded from it.**

---

## 6. RULE 12

**1,382.933 core-min actual** (`STATUS.R_fy`: 10,372 wall s × 8 ranks ÷ 60) against **POINT
1,574.4** — **ratio 0.8784**, **12.2 % under**, **29.3 %** of the 4,723 cap. **$1.1824 vs $1.3461,
both DERIVED at $0.0513/core-h, reported-by-owner, never measured.**

**Attribution: the basis was right and the residual is contention.** The POINT used T3d's own
measured `0.196800` core-min/iteration on this identical mesh; T3e ran at **0.172867**, 12.2 %
faster, on a box that was idle where T3d's was not. **Using the predecessor's own measured rate cut
the miss from T3d's 13.21 % (on `R_ff`'s saturated-box average) to 12.2 % — an improvement, but a
small one, because the remaining error is load and load is not in the basis.**

**NO WASTE.** One launch, `rc=0`, `capped=no`, nothing discarded, no retry. Nothing folded into the
ratio.

---

## 7. WHAT THIS DOES **NOT** ESTABLISH

- **It does not establish that `|U|` will reach `1e-06`.** It establishes that it is *descending*
  and at what rate over 8,000 iterations. The ~7,000-iteration figure is an **extrapolation**.
- **It grades no T3 ladder row.** Rule 5 clause (1) forbids it, and nothing here is a value for
  the backward-facing-step problem.
- **No discretisation bound exists on any number in this record.**
- **It is not a validation of any physics.** Nothing is compared to an experiment.
- **P-3's falsification was measured out-of-band**, not by the registered path (§2).

---

## 8. THE SUCCESSOR, AND WHAT §2an MAKES OF THIS

Under §2an a `GATE REACHED` with a measured decaying trend **routes forward, and the route is now
cheap and well-posed**: ~7,000 further iterations at the measured rate is **~1,210 core-min**, and
the decay factor gives a testable prediction rather than a hope. **A successor should register
that prediction — `|U|` reaches `1e-06` within N iterations at factor 0.850 ± a stated band — so
that a drift in the factor FALSIFIES it rather than merely disappointing it.**

**Two defects to carry, both mine:** the grader must score **every** registered prediction (§2), and
the §2ap rehearsal should be extended to the **registration → grader** pair, which no leg of T3e's
own four-leg rehearsal asked about.
