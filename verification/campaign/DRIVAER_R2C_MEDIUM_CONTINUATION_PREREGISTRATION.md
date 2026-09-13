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

---

## AMENDMENT 1 — 2026-09-13, v1.1, PRE-COMPUTE. **THE CONTINUATION I REGISTERED CANNOT BE GRADED BY THE PATH I PINNED. THE RUN BECOMES A FRESH SOLVE FROM 0 AND THE FROZEN COMPARATOR IS NOT TOUCHED.**

**lines whose number changed above this section: 0**

**Version: 1.0 → 1.1.** Appended at the foot, per standing rule 6. Nothing above is edited;
struck text below is reproduced with its original wording so both readings stay visible.

### A1.1 LEGALITY — WHY THIS IS AN AMENDMENT AND NOT AN ADDENDUM

**No compute has occurred against this registration.** Standing rule 2 makes amendments legal
before first compute and confines changes to addenda only *after* it. **The condition, and how it
was checked:** the run directory this document governs is

> `verification/runs/navier_class/DRIVAER/r2c_medium_blended_R3`

and **it does not exist.** Checked at **2026-09-13T04:22:08Z** by `test -e` on that exact path
(false) and by `ls -d` on the same path, which returned *"No such file or directory"*. The four
sibling directories that do exist are `r2c_coarse_blended`, `r2c_coarse_blended_R2`,
`r2c_medium_blended` and `r2c_medium_blended_R2`; `_R3` is not among them. **No solver has been
started under this registration and no case has been staged for it.** Staging deliberately
follows this amendment's commit rather than preceding it, so that the absence asserted here is
still true at the moment it is frozen.

### A1.2 THE DEFECT, IN THE FROZEN DOCUMENT'S OWN GRADING PATH

§4 pins `cases/navier_class/DRIVAER/grade_drivaer.py`. That file, at **lines 241–244**, reads:

```python
n_exec = len(re.findall(r"ExecutionTime\s*=", logtxt))
want = round(endT / dt)
if n_exec != want:
    refuse(f"{case}: ExecutionTime count {n_exec} != round(endTime/deltaT)={want}")
```

A continuation from 2000 to 10000 writes a **new** `log.simpleFoam` holding **8,000**
`ExecutionTime` lines, against `want = round(10000/1) = 10000`. **8000 ≠ 10000, so the comparator
REFUSES (exit 2).** The run §1 registered would have consumed its full cost and produced nothing
gradeable. The registered launcher opens the log with `>`, not `>>`, so appending is not what
would have happened either.

**A second, independent blocker, and it is by design:** the registered launcher
`cases/navier_class/DRIVAER/mesh/launch_r2_solve.sh` refuses a pre-existing `0/` (*"a pre-existing
0/ defeats the age guard"*) and refuses any `[1-9]*` time directory. The continuation case holds
`0/`, `1750/`, `2000/` and `processor*/2000`. **The launcher cannot start a continuation, and it
is correct not to:** its `cp -r 0.orig 0` followed by `touch` is precisely what dates the rule-4
age guard. Using a different launcher would have been a second unregistered change.

### A1.3 WHAT CHANGES — ORIGINALS STRUCK, NOT REWRITTEN

**§1, struck:** ~~"`endTime` moves from **2000** to **10000**"~~ and ~~"continuing rather than
restarting also requires `startFrom` to move from `startTime` to `latestTime`"~~.

**§1, as amended:** the run is a **FRESH SOLVE FROM 0 TO 10000** in a newly staged case directory
`r2c_medium_blended_R3`. `startFrom` stays `startTime`, `startTime` stays `0`, `endTime` is
**10000**. Then `n_exec = 10000 = want`, and **the pinned comparator is not touched.** The
`startFrom latestTime` wrinkle §1 had to disclose **disappears entirely** — the amended shape is
simpler than the original, not more complicated.

Staging: `0.orig/`, `system/`, and `constant/` with `polyMesh`, `triSurface` and
`extendedFeatureEdgeMesh` symlinked to `r2_medium/constant/`, exactly as `r2c_medium_blended_R2`
was staged. **No `0/`, no `processor*`, no logs, no `postProcessing` carried over.** Ranks stay
**4** for the reason §1 already gives.

**§6, struck:** ~~"8,000 further iterations × 2.672 s × 4 ranks / 60 = **1,425 core-min**,
**$1.22 DERIVED**... Wall ≈ 5.94 h"~~.

**§6, as amended:** 10,000 iterations × 2.672 s × 4 ranks / 60 = **1,781 core-min**, **$1.52
DERIVED, NOT MEASURED** at $0.0513/core-h owner-stated; wall ≈ **7.42 h** at 4 ranks. **The
increase is 356 core-min and $0.30 derived, and it is the price of not editing a pinned
comparator.** The rate basis (2.672 s/iteration, measured on `r2c_medium_blended_R2`'s own 2000
iterations in 5344.56 s of `ExecutionTime` at 4 ranks) is unchanged.

**THE STRUCK COST FIGURE IS NOT REPLACED, IT IS RETIRED.** 1,425 core-min was the prediction for a
run that will now never happen; the entire worth of a cost prediction is that it preceded its run,
so it may not be quietly overwritten. **The calibration row owed to `docs/COST_CALIBRATION.md`
scores the ACTUAL against 1,781, and records that 1,425 was struck PRE-COMPUTE and why.** A reader
must be able to see both numbers and which one was live.

**UNCHANGED BY THIS AMENDMENT, and named so that is unambiguous:** `endTime` **10000**; the §2
residual-trajectory derivation and its Uy-binds-at-8,394 arithmetic; the §0 refusal of the
outlier-fitted 2671; the §5 falsifier; the §3 mesh non-conformance cap (max skewness 5.450 on 2
faces against MESH_STANDARD 4.0, STATED LIMITATION, never a credential); the §4 grading path and
its sha256. **No gate, threshold, cap or label moves.**

### A1.4 THE STRUCTURAL FINDING, WHICH IS LARGER THAN THIS CASE

**RULE 4's UNIT-STEP `ExecutionTime` CLAUSE MAKES ANY RESUME UNGRADEABLE BY A COMPARATOR THAT
IMPLEMENTS IT LITERALLY — AND THIS LAB'S COMPARATORS DO NOT AGREE ON HOW TO IMPLEMENT IT.**
Measured by reading the code, not inferred:

| form | where | behaviour on a resume |
|---|---|---|
| **A: `n_exec == endTime`** | `cases/navier_class/DRIVAER/grade_drivaer.py:242`; `verification/runs/M6I_runs/analyse_m6i.py:234`; `cases/M6SR/analyse_m6sr.py:1810` | **REFUSES.** A resumed log holds only the segment's lines. |
| **B: `n_exec == n_time`** | `cases/RANS_LES_closure_models/RC3_wu_ceiling_gate_validation/rc3_ceiling.py:1018`; `.../RC4_kaandorp_propagation_repair/rc4_score.py:239` | **ACCEPTS.** It tests the log's INTERNAL consistency and never compares to `endTime`. |

**Standing rule 4 itself supplies two forms and selects between them on `deltaT`** — the unit-step
form *"= endTime when deltaT=1"* and, for adaptive-`deltaT` runs, *"n_exec == steps written"*. **It
is SILENT on resume.** So a resumed run at FIXED `deltaT` falls into the unit-step branch and is
ungradeable by construction, in any territory using form A. That is the gap, and it is a rule
question, not a comparator bug: form B is not a laxer reading of form A, it is a different
quantity.

**THE LAB ALREADY KNEW AND FILED IT WHERE NO REGISTRATION AUTHOR WOULD LOOK.** The queue draft
`verification/runs/navier_class/DRIVAER/QUEUE_DRAFTS/DRIVAER-R2C-MEDIUM-BLENDED.draft.json` says,
in its own words: *"startFrom, endTime 2000 and deltaT 1 UNTOUCHED, so rule 4's ExecutionTime
count == 2000 is unaffected — **the very clause that makes a resume ungradeable**."* That sentence
was on disk before §1 of this document was drafted. **A finding recorded where the next reader
will not look is most of the way to not having been found**, and this amendment exists partly
because of where that sentence was filed.

### A1.5 WHAT THIS AMENDMENT DOES NOT CLAIM

It does not rule on which form is correct — that is a rule-4 question for verification and
ultimately for Sanaa, and a docket item is drafted separately. It does not alter any other
registration. It does not authorise editing `grade_drivaer.py`, whose sha256 §4 pins by name:
**retrofitting a guard or a resume branch into a pinned instrument is exactly what rule 6 exists
to prevent**, and the $0.30 above is what the lab pays instead.
