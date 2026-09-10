# PERMISSION: NOT_FROZEN — DRAFT

**A5P — U-BEND PRIMAL PLATEAU-BREAKING LADDER — PRE-REGISTRATION**

**Status:** DRAFT. Not committed, not frozen, not launched. Freezing and launch are
the dafoam-supervisor's acts, not this lane's.
**Author:** dafoam `lab-lane`, 2026-09-10, on the dafoam-supervisor's brief.
**Nothing here is filed, sent or posted anywhere** (`CLAUDE.md` rule 7).
**Frozen at the commit that adds this file.** No gate, threshold, cap or label below
may change after the first container starts (`CLAUDE.md` rule 2).

**Pre-compute amendment condition (rule 2, first bullet):** amendments are legal until
first compute. The condition is checked by the absence of the registered run root
`/home/ubuntu/certonomous-runs/A5P-ubend-plateau/`, which **does not exist at the time
of writing**.

**What this item is NOT.** It is not A5's grid triple. The triple's Case Protocol §5
gate — *"iterative error verified at least ten times smaller than the level-to-level
difference"* — cannot be met while the primal stagnates at `p initRes` ≈ 2e-04. A5's
triple stays **BLOCKED** until this ladder produces a configuration that converges.

---

## 1. THE PROBLEM, MEASURED

A5's U-bend primal reaches a stationary state of the outer iteration at which the
pressure equation's **initial** residual is not small and does not fall. Two
configurations, both measured, both stationary:

| configuration | `p initRes` at endTime | source artifact |
|---|---|---|
| stock `system/fvSolution` | **2.257624979593885e-04** at iter 1000 | `cases/dafoam/ladder-a/logs/A5_compute_totals_run1.log`, `Time = 1000` block (line 829 ff.) |
| stock, same run, iter 900 | 2.257624939542488e-04 | same log, `Time = 900` block (line 812 ff.) |
| tightened, endTime 1000 | **2.056814952601221e-04** | `cases/dafoam/ladder-a/logs/A5_compute_totals_tightened_endtime1000_run2.log`, final `Time = 1000` block |
| tightened, endTime 10000 | **2.056814952540850e-04** | `cases/dafoam/ladder-a/logs/A5_compute_totals_tightened_endtime10000_run1.log`, final `Time = 10000` block |

**The decisive number.** Between endTime **1000** and endTime **10000** of the
*tightened* configuration — a factor of ten in iterations — `p initRes` moved by a
relative **2.9e-11**, i.e. the two values agree to **11 significant figures**. This is
a fixed point of the iteration map, not under-iteration. Iterations are not a lever
and **no arm below adds any**.

*(Correction to the brief, on the record: the two STOCK samples at iterations 900 and
1000 agree to 8 significant figures and differ at the 9th, relative 1.8e-08 — they are
not bit-identical. The 11-significant-figure agreement is the TIGHTENED 1000-vs-10000
pair above. The conclusion is unchanged and in fact stronger, because it is
established across a 10× iteration extension rather than across 100 iterations.)*

**The largest residual is not `p`.** In the final iteration of both baselines the
maximum per-equation initial residual is **`nuTilda`**, and tightening made it
**worse** while making `p` better:

| equation | stock, iter 1000 | tightened, iter 10000 |
|---|---|---|
| U0 / U1 / U2 initRes | 1.7933e-06 / 5.0400e-06 / 1.2030e-05 | 2.2364e-06 / 5.5247e-06 / 1.5486e-05 |
| U **median** (N-D44's rule) | 5.0400e-06 | 5.5247e-06 |
| p | 2.2576e-04 | 2.0568e-04 |
| T | 1.5812e-05 | 1.8630e-05 |
| **nuTilda** | **2.6157e-04** | **3.6201e-04** |
| **`primalMaxRes` (N-D44 = max of the above)** | **2.6157e-04 (nuTilda)** | **3.6201e-04 (nuTilda)** |

`p` and `nuTilda` therefore are **not** stagnating for the same reason. This fact
generates arm **P4** and is reported beside every arm's `p` number.

Objective at the plateau (`TP1 − TP2`): stock **52.34521634**, tightened
**52.34517755** — a relative difference of **7.4e-07**. The objective is essentially
insensitive to the plateau, which is exactly why the plateau has never announced
itself as an error.

---

## 2. WHAT `fvSolution.tightened_2026-07-30` ALREADY TRIED — AND IS THEREFORE FORBIDDEN BELOW

Read in full at
`cases/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/system/fvSolution.tightened_2026-07-30`.
Its own header states its intent verbatim (lines 22–26):

> *"stock tutorial has no residualControl and runs a fixed 1000 steps regardless. Add
> residualControl so a genuinely converged primal can exit early, and see whether p/U
> (and T) can actually reach a much lower residual than the stock plateau (p initRes
> ~2.26e-4) given tighter inner solves."*

**Exact delta against the live `system/fvSolution`:**

| setting | live `fvSolution` | `fvSolution.tightened_2026-07-30` | status for this ladder |
|---|---|---|---|
| `SIMPLE/residualControl` | **absent** | `p U T nuTilda` all **1e-8** (lines 27–33) | **TRIED — EXHAUSTED** |
| `p` GAMG `relTol` | 0.1 | **0.01** (line 43) | **TRIED — EXHAUSTED** |
| `p` GAMG `tolerance` | 0 | **1e-10** (line 44) | **TRIED — EXHAUSTED** |
| `(U\|T\|e\|h\|nuTilda\|k\|omega\|epsilon)` `relTol` | 0.1 | **0.01** (line 56) | **TRIED — EXHAUSTED** |
| same, `tolerance` | 0 | **1e-10** (line 57) | **TRIED — EXHAUSTED** |
| same, `nSweeps` | 1 | **2** (line 58) | **TRIED — EXHAUSTED** |
| endTime | 1000 | 1000 → 5000 → 10000 all run | **TRIED — EXHAUSTED** |
| `SIMPLE/consistent` | `false` | **`false`** (line 20) | **NOT TRIED** → arm **P1** |
| `SIMPLE/nNonOrthogonalCorrectors` | 0 | **0** (line 21) | **NOT TRIED** → arm **P2** |
| `relaxationFactors/fields "(p\|p_rgh)"` | 0.30 | **0.30** (line 66) | **NOT TRIED** → arm **P3** |
| `relaxationFactors/equations` (U/T/nuTilda…) | 0.70 | **0.70** (line 70) | **NOT TRIED** → arm **P4** |
| `p` solver type | GAMG | **GAMG** (line 41) | not tried; **not** registered as an arm (§3.6) |
| `Phi` solver, `potentialFlow` block | relTol 0, tol 1e-6, 20 correctors | **unchanged** | irrelevant — `potentialFlow` only |

**What that attempt proved, and it is the load-bearing negative result of this item:**

1. Tightening the inner linear solves by one to two orders **moved the fixed point by
   8.9 %** (2.2576e-04 → 2.0568e-04) — less than one tenth of one order. Linear-solver
   truncation error is **not** the cause of the plateau.
2. `residualControl` at 1e-8 **never fired**: the endTime-10000 run executed all 10,000
   steps and printed `End`. Nothing in the outer loop ever came near 1e-8.
3. Extending 1000 → 10000 moved `p initRes` by relative **2.9e-11**.

**Binding consequence:** no arm below changes any inner-solver tolerance, `relTol`,
`nSweeps`, `residualControl`, or `endTime`. Those five levers are spent. An arm that
only adds iterations is not a lever and none is registered.

---

## 3. THE ARMS — ONE CHANGE PER RUN (Case Protocol §3)

### 3.0 The common baseline, identical in every arm

The baseline is the **tightened** configuration verbatim — because it is the
better-converged of the two measured states and because using it means every arm below
is a genuinely new lever stacked on an exhausted one, not a re-run of one.

- `system/fvSolution` = `fvSolution.tightened_2026-07-30`, byte-for-byte.
- `system/fvSchemes`, `system/blockMeshDict`, `constant/`, `0.orig/` = unchanged from
  `cases/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/`.
- `system/controlDict`: `endTime 5000` (**uniform across all five arms**, including the
  baseline arm P0, so it is part of the baseline and not a per-arm change). Justified
  by §2 item 3: 1000 vs 10000 has been measured to change nothing, so 5000 costs
  nothing and gives 6 printed decile samples.
- Driver: `runScript.py -task=run_model` — **primal only, no adjoint**
  (`runScript.py:37, 296–297`). The adjoint is not exercised by this item.
- `np = 4`, `scotch` (`system/decomposeParDict:18,20`). Mesh 4,800 hexahedra,
  max non-orthogonality 3.512°, max skewness 0.218.
- Printed-residual interval: DAFoam default (**100** — no `printInterval` key is set in
  `runScript.py`; verified by grep). The grader asserts ≥5 decile samples and refuses
  otherwise (§4.2), so a different image default degrades to a refusal, never to a
  silent weaker gate.

### 3.1 P0 — BASELINE REPRODUCTION (not a lever; a determinism control)

**Change from baseline: none.** P0 *is* the baseline.

**Predicted outcome, registered before the run:** at iteration 1000, `p initRes` =
**2.0568149526e-04** to ≥6 significant figures, and `nuTilda initRes` =
**3.6201075e-04** to ≥6 significant figures; `Bounding` count = **0**; the run reaches
`Time = 5000` and prints `End`.

**If P0 does not reproduce to 6 significant figures, the item's verdict is `BLOCKED`
(non-determinism) and no other arm is graded.** A ladder measured against an
irreproducible baseline is not a ladder.

### 3.2 P1 — SIMPLEC

**The one change:** `SIMPLE { consistent false; }` → `SIMPLE { consistent yes; }`.

**Why this can break a fixed point rather than iterate longer.** SIMPLE approximates
the velocity-correction operator by `A⁻¹` and **discards** the neighbour contribution;
SIMPLEC retains it as `(A − H1)⁻¹`, where `H1` is the sum of the off-diagonal
coefficients. These are two **different iteration maps** with **different fixed
points**. A state satisfying `x = G_SIMPLE(x)` at a nonzero pressure-equation residual
need not satisfy `x = G_SIMPLEC(x)`. This is an operator change, not more iterations,
and it targets exactly the approximation the §2 evidence has not ruled out — a
stationary state with a nonzero pressure residual that tighter linear solves cannot
reduce is the classical signature of the SIMPLE velocity-correction approximation, not
of linear-solver error.

**Predicted outcome:** **BREAK** — `p initRes` falls below 2.057e-05 within 5,000
iterations. This is registered as the most likely arm to succeed.

**Confound stated in advance:** SIMPLEC conventionally runs with `p` field relaxation
near 1.0; P1 holds it at 0.30 to keep the one-change rule. If P1 lands on a new plateau
that is a NEGATIVE result **for `consistent yes` at p-relaxation 0.30**, reported with
that qualifier. It does not license a second change inside P1.

### 3.3 P2 — NON-ORTHOGONAL CORRECTORS

**The one change:** `nNonOrthogonalCorrectors 0` → `2`.

**Why this can break a fixed point rather than iterate longer.**
`system/fvSchemes:48,53` set `laplacianSchemes default Gauss linear corrected` and
`snGradSchemes default corrected`, so the non-orthogonal part of the pressure Laplacian
is carried as an **explicit deferred correction**. With 0 correctors that term is
evaluated once from the previous iterate and never re-solved inside the iteration, so
the pressure equation actually solved is not the pressure equation whose residual is
reported. Two correctors re-solve the equation against its own updated correction —
again a different operator, not more outer sweeps.

**Predicted outcome:** **NO BREAK.** Max non-orthogonality is 3.512°, so the correction
term is small; I predict a new plateau within a factor of 2 of 2.0568e-04. **P2 is
registered as a deliberate discriminating negative**: it is the arm most likely to
fail, and its failure is what makes a P1 or P3 success attributable to the lever rather
than to any change at all. Registering a predicted failure is intentional.

### 3.4 P3 — PRESSURE FIELD RELAXATION

**The one change:** `relaxationFactors/fields "(p|p_rgh)" 0.30` → `0.70`.

**Why this can break a fixed point rather than iterate longer.** Under-relaxation drops
out of a true fixed point of the **exact** discrete equations, but it does **not** drop
out of the fixed point of the **approximated** SIMPLE map: the factor enters the
pressure-correction / momentum balance and shifts where that map's fixed point sits.
Changing it moves the fixed point; it does not merely change the rate of approach to
one. The direction (0.30 → 0.70, looser) is chosen because a heavily under-relaxed
pressure is the configuration in which the SIMPLE approximation error is largest
relative to the correction actually applied.

**Predicted outcome:** the plateau **moves by more than a factor of 2 but does not
break** — predicted new plateau in the range 5e-05 to 5e-04. A plateau that moves with
relaxation while 10× the iterations does nothing is itself decisive evidence that the
stagnation is a property of the map. That result is a `GATE FAIL` on this item's gate
and is reported as a **real finding with its measured shift**, not as nothing.

### 3.5 P4 — FROZEN TURBULENCE (DIAGNOSTIC ONLY)

**The one change:** the `relaxationFactors/equations` regex is split so that `nuTilda`
alone takes **0.0** — i.e. `"(U|T|e|h|k|epsilon|omega)" 0.70;` **plus**
`nuTilda 0.0;`. Every other equation keeps 0.70. This is one setting: `nuTilda`'s
relaxation.

**Why this can break a fixed point rather than iterate longer.** `nuTilda` is the
largest residual in the final iteration of **both** baselines (2.6157e-04 stock,
3.6201e-04 tightened) and under N-D44 it, not `p`, is what DAFoam accepts on. Tightening
made `p` better and `nuTilda` **worse** — direct evidence the two do not stagnate for
the same reason. Relaxation 0.0 freezes the eddy viscosity at its current field and
removes the SA equation from the coupled map entirely. If `p`'s plateau is sustained by
the turbulence equation, `p` breaks; if it is not, `p` stays put and the SA equation is
exonerated. Either outcome is information.

**Predicted outcome:** `p initRes` falls by at least one order (**BREAK on G1**).

**Registered in advance, and binding:** a BREAK on P4 is a **DIAGNOSTIC BREAK** and is
**never** a candidate configuration for A5's grid triple — a frozen-turbulence primal is
not the case A5 grades. This is registered now precisely so a P4 success cannot later be
quietly promoted into a production setting.

### 3.6 Levers considered and NOT registered

- **Changing the `p` solver (GAMG → PCG/DIC or PBiCGStab).** Untried, but §2 item 1
  showed the plateau is insensitive to how well the pressure system is solved by two
  orders of magnitude. A different solver for the same system is a fourth attempt at a
  lever already measured dead. Excluded on evidence, not on cost.
- **Changing `divSchemes`.** This would change the discrete equations, so a "break"
  would be a break on a different problem. Out of scope for a plateau ladder.
- **More iterations, in any form.** Forbidden by §2.

---

## 4. THE GATE, THE FALSIFIER, AND THE FIELD CHECK

All quantities below are read from the **arm's own log** at the iterations named. Every
threshold is a number fixed here, before any container starts.

### 4.1 G1 — the break threshold

`p` **initial** residual at `Time = 5000`, i.e. the value on the
`p initRes: <value> finalRes: … nIters: …` line inside the `Time = 5000` block:

> **G1 PASSES iff `p initRes(5000) ≤ 2.057e-05`.**

2.057e-05 is exactly **one order below the P0 baseline plateau 2.0568e-04**. It is
registered as an absolute number, not as a ratio computed after the fact.

### 4.2 G2 — still decreasing at the end

Decile = every printed `p initRes` sample at iteration ≥ **4500** (at the default
interval of 100 this is iterations 4500, 4600, 4700, 4800, 4900, 5000 — **6 samples**).
The grader **asserts at least 5 samples and refuses (exit 2) otherwise.**

> **G2 PASSES iff the decile sequence is monotonically non-increasing AND the decile
> spread `(max − min) / max` ≥ `1.0e-03`.**

**Why 1.0e-03 is the right number and where it comes from.** P0's own drift is
relative **2.9e-11** across a *ten-thousand*-iteration extension (§1). A spread of
1.0e-03 across 500 iterations is roughly **seven orders of magnitude** above anything
the plateau can produce. The threshold cannot be met by a plateau and can be met by any
genuinely converging arm.

> **BREAK = G1 AND G2.** Both, or the arm has not broken the plateau.

### 4.3 The falsifier — a NEW PLATEAU is a negative result and is reported as one

> An arm whose decile spread `(max − min) / max` is **< 1.0e-06** — i.e. whose `p
> initRes` agrees to ≥6 significant figures across the last 500 iterations — is
> declared **NEW PLATEAU** and recorded as a **`GATE FAIL` with its plateau value
> printed**.

**Registered responses that are FORBIDDEN on a new plateau:** extending `endTime`;
re-running the arm; combining the arm's lever with another arm's; tightening any inner
tolerance. Extending iterations is specifically forbidden because 1000 → 10000 has
already been measured to move the plateau by relative 2.9e-11. A new plateau is a
finding, is written down, and the ladder moves to the next arm.

### 4.4 The field-boundedness check, BESIDE the residual gate — N-D45 is binding

`N-D45` (`docs/NUMERICS_KNOWLEDGE.md:6844`): *a diverging field drives its own
normalised initial residual toward zero, so a residual gate alone cannot detect a
diverged field and will report its best number precisely when the solution is worst* —
measured on A4, which passed its acceptance test by 17,429× while `omega Residual
Norm2` stood at 1.13e+35 and `omega` was clipped at both bounds every iteration.

This item therefore carries the following **beside** G1/G2, evaluated on every arm.
**No arm's verdict is ever decided by the residual gate alone.**

| id | quantity | measured baseline | threshold |
|---|---|---|---|
| **F1** | count of `^Bounding ` lines in the whole arm log | **0** in both baselines (`A5_compute_totals_run1.log`, `A5_compute_totals_tightened_endtime10000_run1.log`) | **must be 0** |
| **F2** | every `Residual Norm2` printed at the end of the run — per-equation (U by component, p, T, nuTilda, phi) and `Total` | **PRESENT, 6 lines in every baseline log.** Tightened: `Total` **59.32395932**, worst per-equation `T` **43.50353041**, `p` 8.19651084, `nuTilda` 0.49137238, `phi` 0.04816628, `U` (28.35211938 24.90450438 11.63062438). Stock: `Total` **55.77601518**, worst `T` **41.16023525**. | **every value finite and ≤ 1.0e+04** (absolute). That ceiling sits **168× above** a healthy A5 and **31 orders below** A4's diverged `omega` of 1.13e+35 (N-D45). An **absent** reading is neither pass nor fail: it is recorded as a **failure**, because a check that did not run is not a pass. |
| **F3a** | `yPlus max` at the final iteration (printed every block) | P0 **55.325**; `yPlus min` P0 **1.8459** | `yPlus max ≤ 110.7` (2× P0) and `yPlus min > 0` |
| **F3b** | `nuTilda` field at `endTime`, read from disk | — | `min ≥ 0` and `max ≤ 1.0e+03 ×` P0's `max` |
| **F3c** | `\|U\|` max at `endTime`, read from disk | `U0 = 8.4 m/s` (`runScript.py:53`) | `≤ 84 m/s` (10 × U0) |
| **F3d** | `T` at `endTime`, read from disk | — | within `[250, 400]` K |
| **F4** | `TP1 − TP2` at the final iteration | P0 **52.34517755** | reported with its delta from P0. A delta > 1 % is a **FINDING** requiring the state to be inspected before the arm is called a success — not an automatic refusal, because a genuinely converged arm may legitimately move the objective. |

> **REGISTERED EXPLICITLY: an arm whose `p` residual improves while any field is being
> clipped — F1 count > 0 — is NOT A SUCCESS. That arm's verdict is `NOT A RESULT`, and
> the record prints its residual value directly beside its `Bounding` count, so the
> anti-correlation N-D45 names is visible on the face of the row.** The same applies to
> any F3 failure. A residual gate is never evaluated alone on this item.

### 4.5 initRes, never finalRes — N-D44

`N-D44` (`docs/NUMERICS_KNOWLEDGE.md:6695`): DAFoam's `Primal min residual` is the
**max over the per-equation INITIAL residuals** of the final outer iteration, U entering
by its **median** component; a comparator built on `finalRes` is structurally blind.

Every gate and every check above reads the **`initRes`** token. `finalRes` appears in no
gate. The grader carries a self-check: **it asserts that the string `finalRes` does not
occur in any gate-evaluating expression, and refuses (exit 2) if it does.**

Per N-D44's rule the grader also computes and **reports** `primalMaxRes` — max of
{U median, p, T, nuTilda} — for every arm, because that, not `p`, is what DAFoam accepts
on. In both baselines it is `nuTilda`. It is reported, not gated: this item's registered
gate is on `p`, per the supervisor's brief.

### 4.6 The planted-zero control on the grading reader (`CLAUDE.md` rule 3)

`a5p_grade.py` refuses to grade any arm until it has demonstrated, in the same
invocation, that its reader can see a non-zero through the **real** reading path:

1. **Plant A (residual).** Copy the arm log; locate the final `p initRes:` line **by
   line index** (not by regex-replace-all); rewrite that one line's value to the
   sentinel `PLANT_P = 7.654321e-09`; re-run the *identical* reading path on the planted
   copy. **Assert** the reader returns exactly `7.654321e-09` **and** that G1 flips from
   its unplanted verdict to `BREAK`. If the reader returns the unplanted value, or G1
   does not flip, **exit 2 and grade nothing.**
2. **Plant B (boundedness).** Copy the arm log; insert one line
   `Bounding nuTilda, min: -1.0000e-09 max: 1.0000e+00 average: 1.0000e-04` at a known
   index; re-run the identical F1 path. **Assert** the count goes `0 → 1` and that the
   arm's verdict flips to `NOT A RESULT`. If it does not, **exit 2 and grade nothing.**
3. **Must-be-absent control.** Assert that a sentinel token that appears in no log
   (`A5P_PLANT_MUST_BE_ABSENT`) returns a count of **0** through the same path — so a
   reader that returns 1 for everything is caught too.

Both plants are written to the scratch copy only; the arm log on disk is never modified.

---

## 5. TOLERANCES — READ FROM A5's OWN FILES, CARRIED FROM NOWHERE

`N-D43`'s rule is that both terms are read from **this case's own** files. Measured:

| script | `primalMinResTol` | `primalMinResTolDiff` | **accept floor (product)** | used by this item? |
|---|---|---|---|---|
| `runScript.py:59, 60` | `1e-8` | `1e7` | **0.1** | **YES — this item's driver** |
| `runScript_tightAdjoint.py:59, 60` | `1e-8` | `1e7` | 0.1 | no |
| `runScript_meshQualityConstraint_v2.py:40, 41` | `1e-8` | `1e5` | **1e-3** | no |

(paths relative to `cases/dafoam/ladder-a/A5_work/UBend_Channel_pressureloss/`)

**The accept floor varies within A5 by two orders of magnitude.** This item uses
`runScript.py`, so **its floor is 0.1**.

**Why the plateau never tripped a refusal, computed:** the binding quantity under N-D44
is `primalMaxRes = nuTilda initRes = 3.6201e-04` (tightened baseline). Against a floor
of 0.1 the run **passes DAFoam's own acceptance test by a factor of 276**. DAFoam had
no reason to complain, and did not. A floor of 0.1 sitting 276× above a plateau at
3.6e-04 is not a gate; it is an absence of one.

> **REGISTERED: the gate for this item is the one written in §4 — `p initRes ≤
> 2.057e-05` with the §4.2 decile condition — and NOT DAFoam's floor of 0.1.** DAFoam's
> acceptance banner is recorded in the row for provenance and carries no verdict.
>
> Consistency with Case Protocol §1 (*"solver tolerance strictly tighter than any gate
> that reads its output"* — the T23G2Rn2 rule): the **linear-solver** tolerances in the
> baseline are `1e-10` absolute / `0.01` relative on both `p` and the U-family, which
> are strictly tighter than the §4.1 gate of 2.057e-05 by five orders. Satisfied.

---

## 6. COST — ARITHMETIC FROM THE MEASURED ANCHOR

**Anchor (measured, from logs on disk):**

| what | value | artifact |
|---|---|---|
| stock, 4,800 cells, np=4, endTime 1000 | `ExecutionTime = 3.28 s` | `cases/dafoam/ladder-a/logs/A5_compute_totals_run1.log:844` |
| tightened, np=4, endTime 1000 | `ExecutionTime = 5.61 s` | `…tightened_endtime1000_run2.log`, final block |
| tightened, np=4, endTime 10000 | `ExecutionTime = 31.28 s` | `…tightened_endtime10000_run1.log`, final block |

**Marginal solver rate (tightened), derived from the last two rows:**
`(31.28 − 5.61) s / (10000 − 1000) it = 2.852e-03 s/it`, i.e. **2.85 s per 1000
iterations**. Fixed startup inside `ExecutionTime`: `5.61 − 2.85 = 2.76 s`.

**Per arm, endTime 5000:**
- solver: `2.76 + 5 × 2.85 = 17.0 s`
- container overhead (image start, `loadDAFoam.sh`, idwarp import, `decomposePar`,
  DASolver construction, field write at `writeInterval`), allowed generously: **63 s**
- **wall estimate: 80 s**; at 4 ranks → `80 × 4 / 60 =` **5.33 core-min per arm**

**Registered figures:**

| | core-min | derived $ at $0.0513/core-h |
|---|---|---|
| per arm, estimate | **5.5** | $0.0047 |
| per arm, **CAP** (3 × estimate, Case Protocol §1) | **16.5** | $0.0141 |
| ladder of 5 arms, estimate | **27.5** | **$0.0235** |
| ladder of 5 arms, **CAP** | **82.5** | **$0.0705** |

**`cost_basis`:** core-minutes derived from `ExecutionTime` in the two named logs ×
ranks ÷ 60 — **measured** for the anchor, **predicted** for the arms. The dollar column
is **DERIVED at the owner-stated rate $0.0513/core-h, never measured** — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Well under the $25
pre-authorisation.

**Cap behaviour.** An arm exceeding **16.5 core-min** is **stopped** and recorded
`NOT A RESULT`; the cap is not raised (`CLAUDE.md` rule 12). **The Case Protocol
charter's 3D budget-gate exemption is deliberately NOT invoked by this item** — the
whole ladder costs under 0.02 core-hours and an item this cheap has no need of an
exemption. Claiming one it does not need would be exactly the widening rule 9 forbids.

**Estimate-versus-actual calibration** (`CLAUDE.md` rule 12, Sanaa 2026-08-23): on
completion of the ladder, actual core-minutes per arm are summed from each arm's own
`ExecutionTime`, the ratio actual/predicted is stated per arm and for the ladder, the
gap is attributed (contention / waste / misprediction, waste named separately), and a
row is appended to `docs/COST_CALIBRATION.md`. The report is incomplete without it.

---

## 7. THE LAUNCH PATH

Every arm runs through the **repaired** launcher pattern, derived from
`cases/dafoam/ladder-a/A6/curriculum_D8G/d8g_run_arm.sh.DRAFT` — **not** the old D8R /
D6RF pattern, all 58 instances of which assert container state only.

**The launcher must carry a first-artifact launch witness. The registered witness is the
first `^ExecutionTime = ` line in the container's own stdout.** Its justification is
D8G's LA.0, inherited unchanged: `^ExecutionTime = ` is emitted only by an OpenFOAM
solver's time loop, it proves a **completed** first iteration rather than a call, and it
is the same token `CLAUDE.md` rule 4 already counts for completion.

**`^Time = ` is registered as a FORBIDDEN decoy pattern** and is never a witness:
measured on the D8R producer's own graded log, `decomposePar` prints `Time = 0` **583
lines before the solver's first completed step**. A launcher waiting on it would declare
LAUNCHED on `decomposePar`.

Inherited from the D8G draft, unmodified:

- refusal codes **88** (container exited before any witness), **89** (budget elapsed,
  still alive, no witness), **90** (the witness reader itself failed) — disjoint from
  every exit code this family's solver produces;
- `launched: false reason=[…]` written as a **token** in the ledger, with the grader
  reading the token, not the number alone;
- a refusal **kills the container** and **reads back** `.State.Running` — an unverified
  kill is not a kill (L-540);
- readers that **preserve stderr**, so "I could not look" is a third outcome and never
  collapses into "I looked and saw nothing";
- the pre-launch mtime capture **written to disk**, asserted non-empty, compared by
  **strict increase with no slack term**;
- a `G-FREEZE.0` guard: every constant this document must fix is written in the launcher
  as `__A5P_UNFROZEN__`, and the guard greps its own file, asserts its trip count, and
  refuses (exit 3) while any placeholder remains.

**Registered launch constants** (to be substituted at freeze):

| constant | value |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/A5P-ubend-plateau/` (**does not exist at drafting**) |
| forbidden roots | every existing `certonomous-runs` item root, so A5P can never write into another item's tree |
| ranks / cpuset | 4 / registered at freeze |
| in-container deadline `TMO` | **900 s** per arm |
| launch-witness budget | **180 s** — asserted a strict minority of `TMO` (180 < 450) |
| image + digest | **`dafoam/opt-packages:latest`** @ **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`** — pinned by **hash**; the version string is not the identity (`DAFOAM_CHARTER` §11). **Verified independently by the supervisor at freeze** from `docker images --digests --no-trunc`. **Honest caveat, carried rather than smoothed:** the DIGEST column and the IMAGE ID are the *same* string here, so this pin is the **local content hash**, not a registry manifest digest; `RepoDigests` agrees (`dafoam/opt-packages@sha256:9d45679d…`), and the launcher compares `.Id`. **Not the patched `dafoam-idwarp-rot:v1` that A5's D9 items use** — that patch is an idwarp *rotation* fix and this item is **primal-only**, so the stock image is the honest choice and the difference is registered here rather than discovered later. |
| staged-instrument md5 | `runScript.py` — `__A5P_UNFROZEN__MD5_RUNSCRIPT`, asserted by the launcher against the file it stages (`G-STAGED-MD5`). Measured on the live case: **`06fb0ed4228d9927992a12a2fb68055c`** |
| instrument md5s, recorded not self-checked | `a5p_run_arm.sh` and `a5p_grade.py` are hashed by the **supervisor** against the committed blob at freeze (rule 2). **A file cannot check its own md5** — writing the hash into the file changes it — so no self-md5 slot exists in the launcher. `a5p_grade.py` md5 as written: **`502fc073836164a92d3b1e85271a6ca2`** (also printable with `a5p_grade.py --md5`). `a5p_run_arm.sh` md5 changes when the freeze slots are substituted, so its post-substitution md5 is recorded here at the freeze commit. | **POST-SUBSTITUTION `a5p_run_arm.sh` md5, measured by the supervisor at the freeze commit: `148232a2f324fa2500557c6e4ce28271`.**

**Rule-4 completion, applied to this item:** an arm is done only if `rc = 0`, an `End`
line is present, the last `Time` equals `endTime` (5000), the `ExecutionTime` count
equals the number of printed steps, the fields at `endTime` are present, and every one
is **newer** than the arm's own staged `0/U` (the age datum, touched last at staging).
An arm failing any clause is **NOT A RESULT**, not a degraded result.

---

## 8. VERDICT MAPPING — FIXED VOCABULARY ONLY

| condition | verdict |
|---|---|
| P0 fails to reproduce §3.1 to 6 significant figures | **`BLOCKED`** — item void, no arm graded |
| an arm's launch is refused (88/89/90), or rule-4 completion fails | that arm **`NOT A RESULT`** |
| an arm has `Bounding` count > 0, or fails any F3 check | that arm **`NOT A RESULT`**, residual printed beside the count |
| an arm meets **G1 AND G2** with F1/F3 clean | that arm **`GATE REACHED`** — the plateau is breakable by that lever |
| an arm lands on a **new plateau** (decile spread < 1e-06) | that arm **`GATE FAIL`**, plateau value printed |
| an arm neither breaks nor plateaus (spread between 1e-06 and 1e-03) | that arm **`GATE FAIL`**, spread printed, labelled *indeterminate drift* |
| **no arm** reaches the gate | item **`GATE FAIL`**; A5's grid triple remains **`BLOCKED`** under Case Protocol §5 |
| P4 alone reaches the gate | item **`GATE REACHED (DIAGNOSTIC)`** — §3.5 binds: not a production configuration |

`PASS` is **not** available to this item. `PASS` is reserved for A5's grid-triple gate,
which this item does not attempt.

---

## 9. WHAT THIS ITEM DOES NOT ESTABLISH

Stated so no reader has to infer it.

- **The mechanism of the plateau is not proven and is not claimed.** §2 rules out linear
  -solver truncation and iteration count by measurement. It does not identify the cause.
  Each arm tests a **named hypothesis**; a break identifies a lever, not a mechanism.
- **`nuTilda`'s stagnation is not gated**, only reported. A `p` break with `nuTilda`
  still at ~3.6e-04 would be a partial result and must be reported as one.
- **No arm produces a graded A5 number.** The objective `TP1 − TP2` is recorded for
  drift only.
- **F2 is live, and an earlier draft of this document said the opposite.** A first pass
  asserted the `Residual Norm2` token was absent from both baselines and that F2 was
  therefore vacuous. That was **wrong**, and it was caught by running the grader against
  the real log rather than by re-reading the draft: the token is present **6 times in
  every baseline log** (`A5_compute_totals_run1.log:850–865`,
  `A5_compute_totals_tightened_endtime10000_run1.log:2396–2411`,
  and the endTime-1000 tightened run). F2 is a real gate with measured baselines,
  recorded above. The error is disclosed here rather than silently corrected, because
  the claim was load-bearing: it would have retired the one check that catches A4's
  failure mode.
- ~~**The image digest is not yet pinned** in this draft and must be at freeze.~~ **STRUCK AT FREEZE 2026-09-10: pinned above to `sha256:9d45679d…`, verified by the supervisor from the daemon, not from a record.**

---

*Draft ends. Nothing above has been committed, frozen, or launched by its author.*


---

## SUPERVISOR FREEZE STAMP — 2026-09-10, dafoam-supervisor

**THIS ITEM IS FROZEN AT THIS COMMIT. Gates, thresholds, predictions, falsifiers and caps above are closed.**

**Every freeze value was verified BY ME, from the machine, not taken from the lane's report:**

| value | verified how |
|---|---|
| `runScript.py` md5 `06fb0ed4228d9927992a12a2fb68055c` | my own `md5sum` on the live case file |
| image `dafoam/opt-packages:latest` @ `sha256:9d45679d…` | my own `docker images --digests --no-trunc` |
| run root `/home/ubuntu/certonomous-runs/A5P-ubend-plateau` | **CONFIRMED ABSENT** by my own `ls` — rule 2's "name the run directory that does not exist" |
| `a5p_grade.py` md5 `502fc073836164a92d3b1e85271a6ca2` | my own `md5sum`; also `--md5` |
| `a5p_run_arm.sh` md5 `148232a2f324fa2500557c6e4ce28271` | my own `md5sum` **after** substitution; `bash -n` clean |
| cpuset `12-15` | assigned by me at 22:49Z, load 7.80/16 with five foreign solvers live |

**§3 CHECK-1 ON `a5p_grade.py`, DISCHARGED BY ME PERSONALLY AND NOT BY READING ALONE** — the standard cfd's `7d7fcebf` mtime finding imposed tonight, that a launch/grading instrument's defect is only visible under execution:

- Clean `--selftest`: **35 passed, 0 failed, TRUE EXIT 0.**
- **MUTATION 1** — G1's threshold loosened `2.057e-05 → 1.0` so the gate could never fail: **33 passed, 2 failed, TRUE EXIT 1.** It bites.
- **MUTATION 2** — F2's ceiling broken `1.0e+04 → 1.0e+40` so the A4/`N-D45` mode would go uncaught: **34 passed, 1 failed, TRUE EXIT 1.** It bites.
- Forbidden-token self-check: gate region **160 lines, 0 occurrences** of `finalRes`, **and it detects an injected one** (`N-D44`).
- **A selftest that passes proves nothing until it is seen to fail. I saw it fail, twice, on two independent gates.**

**AN INSTRUMENT ERROR OF MY OWN, DISCLOSED BECAUSE IT NEARLY BECAME A FALSE ACCUSATION.** My first exit-code reading used `python3 … | tail -3` and then read `${PIPESTATUS[0]}` *after* the subshell — so it was measuring **`tail`**, not the grader, and returned **0 for both mutated runs**. I was one step from filing "this grader cannot refuse" against a grader that refuses correctly. It read `0` on the clean run too — **the right answer for the wrong reason**, which is exactly the vacuous control this lane had already caught in its own code an hour earlier. Re-measured with no pipe: 0 / 1 / 1. **A pipeline's exit status is the last command's, and an exit-code reader must itself be shown able to return non-zero.**

**WHAT THIS ITEM IS AND IS NOT.** It is a **plateau-breaking ladder**, not a grid-convergence study. It does **not** deliver mesh convergence and makes no GCI claim. It exists because A5's primal sits on a measured fixed point (`nuTilda` `primalMaxRes` 3.6201e-04, tightened pair agreeing to **2.9e-11 across a tenfold iteration extension**), and Case Protocol §5's ten-times rule cannot be asserted over that. **Freezing the 119.4 core-min A5 grid triple tonight would have registered a §5 gate I already knew could not be met — that is registering a failure and calling it a plan.** Clear the plateau here and the triple becomes registrable with a gate that can be met.

---

## ADDENDUM 1 — 2026-09-10, POST-COMPUTE. `A5P-LAUNCHER-DEF-1`: the runner invoked `mpirun` without `--allow-run-as-root` inside a `--user 0:0` container. **NO GATE, THRESHOLD, CAP, BAND, LABEL, PREDICTION OR COST MOVES.**

*lines whose number changed above this section: 0.*

**FIRST COMPUTE HAS OCCURRED** — a container ran and exited, so this lands as a **dated addendum** under rule 2 rather than as a pre-compute amendment, even though the arithmetic would have allowed the looser path. **The conservative reading costs nothing and is the one that keeps the freeze meaning something.**

**WHAT HAPPENED.** Arm `P0` launched at 22:56:50Z, container `23eb0f6199cf…`, and **exited after 5 s with `A5P_SOLVER_RC: 1`** and the message `mpirun has detected an attempt to run as root`. The runner's `:248` read `mpirun -np $RANKS python runScript.py -task=run_model`; the `d8r_run_arm.sh` reference it was derived from carries **`mpirun --allow-run-as-root`** at `:341-342`, and the flag was dropped in transcription. **Repaired at `:248` only.** This is an **infrastructure defect, not a numerics one**: no solver iteration ran, no residual was produced, no field was written and no gate was evaluated.

**AND THE ROW WAS NEVER AT RISK OF BEING BELIEVED, WHICH IS THE POINT WORTH RECORDING.** The launch assertion — on its **first real use** — refused:

`launched: false reason=[never_started_container_exited after 5s with no ^ExecutionTime = line; decomposePar_decoy_seen=no solver_call_seen=no] launch_rc=88`

and printed `A5P_LAUNCH_REFUSED arm=P0 rc=88 -- THE SOLVER'S FIRST ARTIFACT NEVER APPEARED. This row is NOT A RESULT and no grading may read it.` **A container-state poll of the kind every other launcher in this territory uses would have seen the container run and exit and would have handed its exit code onward as a result.** The `docker kill` read-back also behaved correctly, reporting `kill_failed(client_error)` with the daemon's own words preserved — `container … is not running` — because the container had already stopped. **Stderr was not swallowed, and that is why the reason is legible.**

**COST OF THE REFUSED ATTEMPT, charged not absorbed:** 5 s wall × 4 ranks = **0.333 core-min**, `$0.000285` **derived, not measured**. It is charged against the ladder's registered 82.5 core-min cap.

**VERDICT ON `P0` ATTEMPT 1: `NOT A RESULT`** — no solver started. `P0` is re-run under the repaired launcher; its determinism prediction and every gate above are untouched.
