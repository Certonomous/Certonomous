# DRIVAER r2c_medium_blended — CONTINUATION TO A REGISTERED endTime

**Status: DRAFT, NOT COMMITTED, NOT LAUNCHED.** Written 2026-09-13 by a cfd `lab-lane` on the
cfd-supervisor's instruction. **No solver has been started against this document.** The
supervisor's `SUPERVISION_CHARTER` §3 check — pre-registration **committed** before compute —
is the supervisor's personally and has not been performed at the time of writing.

Worktree HEAD at drafting: `a3fe48897a0b6bfc40e85a1d79a2ace378e76fdf`

---

## 0. 🔴 THE INSTRUCTION I WAS GIVEN CANNOT BE CARRIED OUT AS WORDED, AND THAT IS THE MOST IMPORTANT LINE IN THIS DOCUMENT

I was told to derive the new `endTime` from the **observed decay rate of the Cd plateau
excursion**. **There is no observed decay.** Measured, on the run's own
`postProcessing/forceCoeffs1/0/coefficient.dat`:

| trailing 200-sample window ending at iteration | Cd excursion_rel |
|---|---|
| 600 | 0.022491 |
| 800 | 0.023746 |
| 1000 | 0.018173 |
| 1200 | 0.034761 |
| 1400 | 0.021845 |
| 1600 | 0.037289 |
| 1800 | 0.023674 |
| **2000 (the graded point)** | **0.009578** |

Swept every 50 iterations over [400, 2000] — 33 windows — the graded endpoint's value of
**0.009578 ranks 1 of 33. It is the single lowest excursion in the entire run.** The median is
0.023674 and the maximum is 0.039933 at iteration 1150.

A log-linear fit over all 33 windows gives slope **−1.432e-04 per iteration, standard error
1.127e-04, t = −1.270**, 95 % CI **[−3.642e-04, +7.775e-05] — which contains zero.** The implied
decay is a factor of 0.867 per 1000 iterations, i.e. **not distinguishable from no decay at all.**

**Fitting only the last four windows [1400, 2000] gives a clean-looking −1.464e-03/iteration and
an answer of "endTime 2671". That number is an artifact of the outlier at the right-hand end and
this document registers it as REFUSED.** It is exactly the failure the frozen grader warns about
in its own output: *"(max−min) over the window is set by the tails, so ONE BLIP DOMINATES IT.
Separate genuine drift from a single outlier."* It is also the same shape as the MRF_R2 finding
already on this lab's record — a graded stopping point that ranks 1 of 41 in its own locality —
except that there the outlier was the **worst** point and here it is the **best**, which makes it
more dangerous, because it flatters the run.

**So the endTime below is NOT derived from the Cd excursion. It is derived from the residual
trajectory, which does decay, monotonically and measurably.**

## 1. THE ONE REGISTERED CHANGE

`endTime` moves from **2000** to **10000**. Nothing else in `system/` moves: no scheme, no
relaxation, no solver tolerance, no `fvSolution`, no `fvSchemes`, no mesh, **and not the rank
count** — the run stays at **4 ranks** with the same `decomposeParDict`, because changing the
decomposition changes the partition and this lab has already recorded a scotch-decomposition
artifact on force coefficients. Idle cores are not a reason to move it.

**Disclosed honestly rather than hidden under "one change":** continuing rather than restarting
also requires `startFrom` to move from `startTime` to `latestTime`. That is the mechanical
meaning of "continue", not a second physics change; it is named here so no reader finds an
unregistered dictionary edit later. `processor{0..3}/2000/` exist, so the restart needs no
re-decomposition.

## 2. THE ARITHMETIC THAT PRODUCED 10000

Gate A1's residual limb is `res_tol = 1e-4` on every equation. Log-linear fit of
ln(initial residual) against iteration over the last 1000 iterations (1000 → 2000), per equation:

| equation | residual at 2000 | slope /iteration | iterations per decade | iteration at which it reaches 1e-4 |
|---|---|---|---|---|
| Ux | 8.467e-05 | −5.664e-04 | 4,065 | already inside |
| **Uy** | **2.778e-03** | **−5.160e-04** | **4,462** | **8,394 ← binding** |
| Uz | 6.051e-04 | −5.130e-04 | 4,488 | 5,407 |
| p | 1.296e-03 | −4.026e-04 | 5,719 | 8,116 |
| omega | 1.083e-04 | −2.367e-05 | 97,295 | 6,563 |
| k | 1.388e-04 | −2.322e-04 | 9,918 | 3,572 |

**Uy binds at 8,394.** Margin is taken on the **extrapolated increment**, not on the total:
2000 + 1.25 × (8394 − 2000) = 9,993, rounded up to the next 500 → **10000**. The margin is 25 %
because the fit extrapolates 3.2× beyond the fitted window and a log-linear residual fit is a
lower bound on the effort when a solver stiffens.

## 3. WHAT THIS RUN MAY AND MAY NOT CLAIM

- **It cannot produce a credential, however well it converges.** `log.checkMeshFull` measures
  **max skewness 5.450 on 2 faces** against `docs/standards/MESH_STANDARD.md`'s threshold of
  **4.0** (the coarse siblings measure 4.782 on 1 face). The mesh is **NON-CONFORMING** and the
  frozen grader already emits `credential_eligible: false` with a CLAIM CAP. **Running longer
  fixes Gate A1 and cannot fix the mesh.** Every number this run produces is a **STATED
  LIMITATION** row and may never be entered in a matrix as HOLDS or GATE REACHED.
- **A converged Cd is still not agreement with DrivAerML.** Gate A2's band [0.15, 0.6] is a
  gross-error diagnostic, not a validation gate; `Cd_ref = 0.2758368` is **NOT GATED AGAINST**.
  A reader who finds a converged Cd here and reports it as agreement has misread this document.
- **No Roache triple, no observed order, no GCI.** The family is two-level (592,877 / 3,060,269)
  and Gate G is deliberately unregistered because y+ varies ~2.5× across the levels, so an order
  taken off it would measure the wall model rather than the grid.

## 4. GRADING PATH — PINNED

`cases/navier_class/DRIVAER/grade_drivaer.py`, sha256
`6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7`, verified byte-identical to
the blob at HEAD `a3fe48897a0b6bfc40e85a1d79a2ace378e76fdf` at drafting. Invocation, exactly:

```
python3 cases/navier_class/DRIVAER/grade_drivaer.py --stage-a \
  --levels medium=<case> \
  --reference verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json \
  --report <case>/GRADE_STAGE_A_medium.json
```

The grader **REFUSES (exit 2)** on a malformed call rather than degrading; that refusal is the
correct behaviour and is not to be worked around. Its three planted controls (field reader into
`<t>/p`, Cd reader, Cl reader) must all report `passed: true` or the result is **NOT A RESULT**.

## 5. THE REGISTERED FALSIFIER — WRITTEN BEFORE THE RUN, WHICH IS THE POINT

**Prediction: the residual limb will clear and the Cd plateau limb will NOT.** If at iteration
10000 the residuals are inside 1e-4 on every equation **and** the Cd excursion over the trailing
200-sample window is still of order 0.02 — i.e. within the [0.009578, 0.039933] envelope this run
already exhibited over 33 windows — then **the plateau criterion is UNSATISFIABLE under a steady
SIMPLE treatment of this case, and that is a FINDING TO REPORT, NOT A FAIL TO RECORD.**

Supporting evidence for that prediction, measured now: over the last 400 Cd samples the signal
reverses direction on **14.3 %** of steps (a monotone approach would be ~0 %, white noise ~67 %) —
a slowly wandering signal, not a converging one, on a notchback with a separated wake. If the
falsifier fires, the successor is an unsteady treatment, **not a larger endTime**, and this
document forbids simply registering a bigger number a third time.

## 6. COST

**Basis, MEASURED on this exact case:** 2000 iterations in 5344.56 s of `ExecutionTime` at
4 ranks = **2.672 s/iteration**.

8,000 further iterations × 2.672 s × 4 ranks / 60 = **1,425 core-min**, **$1.22 DERIVED, NOT
MEASURED** at the owner-stated $0.0513/core-h; the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5). Wall ≈ 5.94 h at 4 ranks.

**No cap is registered** — Sanaa's directive #17, 2026-09-12: no run is stopped by a time or
budget cap. This figure is a **calibration prediction to be scored** under standing rule 12 at
completion, never a kill. The basis rate was measured on a box carrying other load; if the box is
quieter the actual will come in under and the ratio is what the calibration row records.

## 7. FREEZE

Frozen at the commit adding this file, before any compute at this `endTime`. No band, threshold,
condition, cap or label above may be altered afterwards; departures land as dated addenda at the
foot that strike the original legibly and cannot move a gate.
