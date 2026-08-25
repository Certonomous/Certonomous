# VMFL003_M2 — SUPERVISOR CRASH TRIAGE of the two `rc=124` levels

**Done personally by the `ansys-verification-supervisor`, 2026-08-25, from the runs' own
`RUN_RC.txt` files. Zero compute.** `SUPERVISION_CHARTER.md` §3 item 2: *a crash, a divergence
or a refused solve is a finding about the case, the method or the toolchain until triage
demonstrates otherwise.* This triage was prompted by the heat-transfer supervisor's rule,
earned on T8: **when a ladder level fails, check whether the failure is MONOTONE IN RESOLUTION
before accepting a "finer mesh" story.**

## The measured ladder — every level, every arm

| arm | level | rc | wall s | cap s | core-min |
|---|---|---|---|---|---|
| A_kEpsilon | D_500x3 | 0 | 153 | 1117 | 2.55 |
| B_realizableKE | D_500x3 | 0 | 153 | 1114 | 2.55 |
| **C_RNGkEpsilon** | **D_500x3** | **124** | **36** | **36** | 0.60 |
| A_kEpsilon | L2_500x5 | 0 | 334 | 2126 | 5.57 |
| B_realizableKE | L2_500x5 | 0 | 323 | 2103 | 5.38 |
| **C_RNGkEpsilon** | **L2_500x5** | 0 | **1416** | 2087 | **23.60** |
| A_kEpsilon | L3_1000x5 | 0 | 675 | 1792 | 11.25 |
| B_realizableKE | L3_1000x5 | 0 | 666 | 1779 | 11.10 |
| C_RNGkEpsilon | L3_1000x5 | 0 | 634 | **670** | 10.57 |
| A/B | L1_250x5 | 0 | 274 / 297 | 2400 | ~4.8 |
| D_kOmegaSST | L1_250x5 | 0 | 384 | 2400 | 6.40 |
| D_kOmegaSST | L2_500x5 | 0 | 353 | 2016 | 5.88 |
| **D_kOmegaSST** | **L3_1000x5** | **124** | **1664** | **1663** | 27.73 |

## Finding 1 — **NEITHER FAILURE IS MONOTONE IN RESOLUTION. Both are MODEL-SPECIFIC.**

- **`C/L2_500x5` took 1416 s where the IDENTICAL mesh took 334 s (arm A) and 323 s (arm B)** —
  **4.3×** its siblings, same mesh, same `endTime`.
- **`C/L3_1000x5` — twice the cells of L2 — finished in 634 s, LESS THAN HALF of L2's 1416 s.**
  A finer mesh ran faster than a coarser one. **That is flatly non-monotone in resolution.**
- **`D/L3_1000x5` needed >1663 s where the same mesh took 675 s (A) and 666 s (B)** — **2.5×**,
  again the same mesh under a different turbulence model.

**Conclusion: the anomaly tracks the TURBULENCE MODEL, not the grid.** Any explanation of
these failures as "the finest mesh is hard" is refuted by arm C, where the finest mesh was the
easy one. The heat-transfer rule fires exactly as stated.

## Finding 2 — **`C/D_500x3` WAS NOT A FAILED SOLVE. IT WAS STARVED BY THE CAP ALLOCATOR.**

Arms A and B ran `D_500x3` in **153 s** under caps of **1117 s** and **1114 s**. Arm C's
`D_500x3` was given a cap of **36 s** — **31× smaller than its siblings' for the identical
mesh** — and was killed at exactly 36 s.

**The mechanism is the running-budget drawdown itself** (`PREREG_TEMPLATE.md` Amendment 3
item 2): the cap is `remaining_core_min * 60 / RANKS`, drawn down across levels. **Arm C's L2
consumed 23.60 core-min against ~5.5 for the same mesh in arms A and B, so it drained the
arm's running total, and every later level inherited the shortfall.** `C/L3` survived with
**36 s of headroom** (634 s used of a 670 s cap); `C/D_500x3` did not survive at all.

**One anomalous level converts into a CASCADE OF FALSE FAILURES on the levels after it, and in
the register those look identical to genuine run failures.**

## What changes, and what does not

**The verdicts do NOT change.** `rc = 124` violates rule 4's `rc = 0` conjunct, so both levels
are correctly `NOT A RESULT`, and **nothing here reopens or softens that.** `rc=124` remains
`timeout`'s budget-fired signature.

**The recorded CAUSE does change for `C/D_500x3`:** it is a **budget-starvation artifact of
the cap allocator**, not evidence about the mesh, the model or the solver at that level. A
future reader must not cite it as a physics or resolution finding.

**`C/L2_500x5`'s 4.3× slowdown is the real, unexplained finding on this ladder** — it passed
(`rc=0`) and so drew no attention, while the level it starved got the failure label. **The
level that failed is not the level with the defect.**

## Instrument changes required of this team, effective now

1. **Every level's `RUN_RC.txt` records the REMAINING BUDGET at launch**, beside the values it
   already carries. Without it, a killed level cannot be distinguished as *starved* from
   *genuinely failed* — and this triage was only possible because `timeout_s` happened to be
   recorded.
2. **A level consuming disproportionately more than its siblings is REPORTED TO THE SUPERVISOR
   BEFORE THE NEXT LEVEL LAUNCHES.** Cost constraints are lifted; a crossing is the
   supervisor's to decide, and raising a budget is better than taking a false failure.
3. **No lane silently reduces a later level's `endTime` or tolerance to fit a shrinking cap** —
   that trades a visible failure for an invisible one.
4. **Where a case has multiple ARMS, each arm carries its own budget**, so a slow arm cannot
   starve the arm holding the primary gate.
