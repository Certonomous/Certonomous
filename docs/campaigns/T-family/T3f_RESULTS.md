# T3f — RESULTS. **`|U|` REACHED TOLERANCE.** The decay law held, the prediction landed within 2.5 % of its registered value — and the grader scored one prediction **vacuously**, which is a third layer of a defect class this team has now hit three times

**RUNG VERDICT: `PASS`.**

> From the registered path and **not composed**: `analyse_t3f.py` (pin `…`, verified byte-identical
> to HEAD at grading time) printed `RUNG T3f PASS -- |U| reached tol AND the decay law held in band`.

| | |
|---|---|
| **P-1** `\|U\|` reaches `≤ 1e-06` by `endTime` | **HIT** — final `8.99782e-07` |
| **P-2** decay factor stays in `[0.830, 0.870]` | **HIT** — ratios `0.8435`, `0.8416` |
| **P-3** `T` stays converged | **HIT** — `3.27e-07`, `2.81e-07`, `2.42e-07` |
| **P-4** no restart spike above 2.5× | ⚠ **SCORED VACUOUSLY — see §3. True value 2.3582, HIT, measured out-of-band** |

**Cost: 1,224.800 core-min against a POINT of 1,382.9 — ratio 0.8857, 29.5 % of the 4,148.7 cap.**

---

## 1. THE PHYSICS — `|U|` IS CONVERGED

| pair | `T` `relative` | `T` state | `\|U\|` `relative` | `\|U\|` state |
|---|---:|---|---:|---|
| (2000, 4000) | 3.27447e-07 | `CONVERGED` | 1.26755e-06 | `NOT_CONVERGED` |
| (4000, 6000) | 2.81371e-07 | `CONVERGED` | 1.06915e-06 | `NOT_CONVERGED` |
| **(6000, 8000)** | 2.41648e-07 | `CONVERGED` | **8.99782e-07** | **`CONVERGED`** |

**`field_range` is stable and non-zero on every pair and both fields** (50.289 K, 11.0325), so
**D-J1 never fires and could not have.**

> ### ⚡ **THE PREDICTION LANDED. `9.2318e-07` PREDICTED, `8.99782e-07` MEASURED — 2.5 % APART, ON A MARGIN OF 7.7 %.**
> §3 of the registration derived the prediction **before the run** from T3e's `1.77017e-06` at a
> mean factor of `0.8498`, and named the exact failure mode: **P-1 fails if the factor is ≥ 0.868.**
> The measured factors were **0.8435 and 0.8416** — slightly *faster* decay than T3e's, so P-1
> passed with room it was not guaranteed. **P-2 confirms the law held**: both ratios inside
> `[0.830, 0.870]`, and the two independent intervals agree to **0.2 %**, as T3e's did.
>
> **The decay is marginally faster than T3e measured (0.842 vs 0.850).** Recorded rather than
> smoothed: the factor is drifting slightly *downward*, which is the benign direction and which
> the registered band accommodated without being widened to do so.

**THE CHAIN IS COMPLETE.** `R_ff` (118,000) → T3d `R_fx` (+24,000) → T3e `R_fy` (+8,000) → T3f
`R_fz` (+8,000). **40,000 additional iterations, and the fine level's `|U|` is now iteratively
converged on the registered `tol = 1e-06`, with `T` converged throughout.**

**What that opens, stated carefully and NOT claimed here:** rule 5 clause (1) was the barrier that
made this level ungradeable. **It is now satisfied at this level.** Whether the T3 ladder's fine row
can be graded is a **separate question on a separate registered path** — `analyse_t3d.py`, which
refused on T3d's `CASE.txt` defect and has not been re-run. **No ladder row is graded here and none
is claimed.**

---

## 2. RULE 4, AND THE MARKER EARNED THROUGH A PRODUCER REGISTERED BEFORE COMPUTE

`python3 mark_done_t3.py --root T3_runs R_fz` → **`1/1 cases meet the strict completion rule`**,
exit 0. Recorded at `T3f_runs/T3f_MARK_DONE_R_fz_OUTPUT.txt` per §2ao condition 1.
`STATUS.R_fz`: `rc=0`, `capped=no`, **`reconstructpar_rc=0`** (required by §6, live because `R_fz`
ran decomposed on 8 ranks), `core_min=1224.800`. **All four pins byte-identical to HEAD at grading
time — the frozen files are the files that ran.** All four checkpoints survived under
`purgeWrite 0`. **Rule-3 control fired before any pair was classified:** a `1.234e-03 K` plant moved
the reader by `1.221848e-03` — **PLANT SEEN**.

---

## 3. ⚠ P-4 WAS SCORED **VACUOUSLY**, AND THE DEFECT IS MINE

**The grader printed `P-4 worst restart ratio 0.000 against 2.5 -> HIT`. That HIT is worthless.**

`score_spike()` returned **zero rows**. Its regex is `r"Solving for (\\w+),…"` — a raw string
holding a **literal backslash-w**, produced by heredoc escaping doubling the backslash when I wrote
the file. **`log.solve` contains 48,000 matching lines and the reader saw none of them.**
`max(…, default=0.0)` then returned `0.0`, and `0.0 ≤ 2.5` scored **HIT**.

> **THIS IS A ZERO FROM A READER NEVER SHOWN ABLE TO SEE A NON-ZERO — `CLAUDE.md` rule 3's exact
> prohibition — INSIDE THE PREDICTION I ADDED TO REPAIR A COVERAGE DEFECT.**

**THE TRUE VALUE, MEASURED OUT-OF-BAND AND NOT BY THE REGISTERED PATH:**

| field | first | max | ratio |
|---|---:|---:|---:|
| `T` | 2.603193e-09 | 2.603193e-09 | 1.0000 |
| `Ux` | 4.886879e-10 | 4.886879e-10 | 1.0000 |
| `Uy` | 2.875660e-10 | 2.875900e-10 | 1.0001 |
| **`p_rgh`** | 1.140420e-10 | 2.689360e-10 | **2.3582** |
| `k` | 1.536735e-10 | 1.537058e-10 | 1.0002 |
| `omega` | 9.994649e-12 | 1.000153e-11 | 1.0007 |

**Worst 2.3582 against the registered 2.5 — P-4's true answer is HIT, with 5.7 % of margin.**

**POSITIVE CONTROL ON THAT MEASUREMENT, because a number obtained after finding a broken reader
needs one:** the *same* corrected reader run on **`R_fy`** returns `p_rgh = 1.9982`, **reproducing
the 2.0× T3e recorded by a different route.** The reader is demonstrably able to see a spike.

**THE VACUOUS SCORE AND THE TRUE SCORE AGREE, AND THAT AGREEMENT IS LUCK.** Had `p_rgh` spiked 3×,
the grader would still have printed `HIT`. **A pass that would have been printed regardless of the
data is not evidence, whatever the data turned out to be.**

**⚠ AND A PHYSICS POINT INSIDE THE BOOKKEEPING ONE:** the restart spike **GREW from 2.00× (T3e) to
2.3582× (T3f)** on the identical case and procedure. The registered 2.5× threshold was set from
T3e's measured 2.0×; **the margin has narrowed from 25 % to 5.7 % in one continuation.** A further
continuation may breach it, and a successor should register that expectation rather than be
surprised by it.

### 3.1 THE VERDICT IS NOT CONTAMINATED — BY DESIGN, NOT BY LUCK

The grader folds **only P-1 and P-2** into the rung verdict (`p1 and p2 → PASS`) and prints
*"P-3 HIT, P-4 HIT — reported beside the verdict, not folded into it."* **Both P-1 and P-2 are
computed from the frozen readers on real field data and are genuinely measured. The `PASS` rests on
measured ground.** That insulation was a design choice in §4's outcome table, not an accident —
**but had P-4 been folded in, a broken reader would have decided a rung verdict.**

### 3.2 THE THIRD LAYER OF ONE DEFECT CLASS

| layer | pair | asks | instrument |
|---|---|---|---|
| 1 | **builder → grader** | can the consumer *read* the producer's output? | §2ap, legs 1–4 |
| 2 | **registration → grader** | does the grader *score* every registered prediction? | T3f leg 5 (D-4) |
| 3 | ⚡ **scorer → data** | does a scored prediction *read any data at all*? | **NOTHING** |

**Leg 5 verified that P-4 produced a verdict. It did not verify the verdict was derived from data.
A prediction can be fully "covered" and still be vacuous.** T3f's five-leg rehearsal passed and
this shipped anyway — **exactly as T3e's four-leg rehearsal passed and shipped the defect leg 5 was
built to catch.**

**The cure is the lab's oldest rule, applied one level down:** a scorer that can return a passing
value from an empty read must carry a **planted control proving it can see a non-zero**, exactly as
the field readers do. `score_spike` had none. **Routed upward as a §2ap extension candidate; NOT
fixed here — the grader is pinned and the rung has fired.**

---

## 4. RULE 5

**NO ROACHE TRIPLE IS FORMED.** One mesh, one refinement. **No observed order, no GCI, no
Richardson extrapolate is computed, quoted or derivable, and EVERY NUMBER IN THIS RECORD CARRIES NO
DISCRETISATION BOUND AT ALL.** Clause (1) is reached and applied.

---

## 5. RULE 12

**1,224.800 core-min actual** against **POINT 1,382.9** — **ratio 0.8857**, 11.4 % under, **29.5 %**
of the 4,148.7 cap. **$1.0472 vs $1.1824, both DERIVED at $0.0513/core-h, reported-by-owner, never
measured.**

**The basis lesson, third iteration, and it is converging:** T3d used `R_ff`'s saturated-box
whole-run average and missed by **13.21 %**; T3e used T3d's own measured rate and missed by
**12.2 %**; T3f used T3e's and missed by **11.4 %**. **Each step used the predecessor's own measured
rate on the identical mesh, and each shaved about a point off the error — the residual is load, and
load is not in the basis.** Stated in advance in §9 of the registration and confirmed here.

**NO WASTE.** One launch, `rc=0`, `capped=no`, nothing discarded, no retry.

---

## 6. WHAT THIS DOES **NOT** ESTABLISH

- **It grades no T3 ladder row.** The level is converged; whether the ladder's fine row can now be
  graded is a separate question on a separate registered path, and is not answered here.
- **No discretisation bound exists on any number in this record.**
- **P-4's registered-path score is VACUOUS** and the true value is out-of-band (§3).
- **It is not a validation of any physics.** Nothing is compared to an experiment.
- **It does not establish that the decay law extrapolates further.** Two rungs measured it over
  three pairs each; nothing here says it holds beyond `tol`.
