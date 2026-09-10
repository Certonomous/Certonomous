# A2-GC-P — MACH Tutorial Wing grid convergence, primal-only trim — PRE-REGISTRATION

## PERMISSION: NOT_FROZEN

**This document is NOT frozen. The freeze is the dafoam supervisor's act, not
this lane's.** Nothing here is a licence to launch. Version 0.1, drafted
2026-09-10T04:08:32Z by a dafoam lane, in a window in which the box is
saturated (load ~24 on 16 vCPUs, twelve foreign-family solvers at ~99 % CPU,
D6RF10 R3 live under a deadline) and **no A2-GC-P compute is possible or
attempted**.

**NO COMPUTE HAS BEEN SPENT ON THIS ITEM.** The run root asserted absent in §11
did not exist at 2026-09-10T04:08:32Z and the absence was read against a
positive control.

**Nothing in this item is filed, sent, uploaded, registered, posted or
commented** (`CLAUDE.md` rule 7).

**While this document carries `PERMISSION: NOT_FROZEN`, amendments to it are
ordinary edits, not rule-2 amendments.** From the moment the supervisor freezes
it by sha, `CLAUDE.md` rule 2 governs: pre-compute amendments must state the
condition and how it was checked; post-compute changes are dated addenda that
cannot alter a gate, a threshold, a cap or a label.

---

## 1. Why this is a SUCCESSOR and not an addendum to A2-GC

The parent item is
`cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md` (frozen; committed blob
`784cacde7cbd8eba61cf11c4f4cee9d6916c80b4` at the HEAD read on 2026-09-10).

It **cap-stopped**. Its L1 stage's own cost record,
`/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/cost.txt`, reads
verbatim:

```
wall_s=460.0 core_min=91.99 cap_core_min=90 overrun=YES-RUN-STOPPED
```

and `/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/RC` reads
`124` — the `timeout` exit code, i.e. the registered cap firing exactly as
registered. L2 and L3 were never built.

`CLAUDE.md` rule 12: **an overrun stops the run; it does not get a new budget.**
`CLAUDE.md` rule 2 and `VERIFICATION_CHARTER.md` §2b clause 2: **after first
compute, gates are closed** — changes land only as dated addenda that *cannot
alter a gate, a threshold, a cap or a label.* A2-GC has had first compute
(four attempts, 155.66 core-min, its own §R5). **Re-costing it is therefore
illegal on two independent grounds**, and no addendum to it can authorise the
ladder to run.

**A successor pre-registration is the only legal route**, and under it **L1 must
be re-run**: L1's published values belong to the parent's instrument, not to
this one, and a triple whose coarse member was produced by a different driver is
not a triple.

**Nothing in the parent is edited by this document** (`CLAUDE.md` rule 6). One
defect found in the parent's instrument set while reading it is reported to the
supervisor and recorded, not repaired, in §9.4.

---

## 2. What the parent's own record supplies, verified and quoted

Both readings below were verified against the frozen file rather than taken from
a brief. They are quoted, not paraphrased.

### 2.1 The rate anchor — parent §R2 (`A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:559-581`)

The parent's §R2 heading is *"The cost anchor was in the WRONG UNIT, and the
correction is 20x"*, and its finding, verbatim at `:578-581`:

> **Warm steady-state rate: 0.00945 s/iteration at np=12 on 38,304 cells
> (0.1134 core-s/iteration)** — solves 2-4 agree to within 2 %. A 1000-iteration
> primal is therefore **1.89 core-min**, not 38.

The same table (`:569-576`) also records, and this document does **not** drop it,
that the **cold** primal ran at **0.07233 s/iteration (0.868 core-s/iteration)**
— 7.65× the warm rate. §8 costs the cold primal separately; the earlier
"~38 core-min per primal" anchor is dead and is not repeated here.

### 2.2 The cost driver — parent §R3 (`:582-603`)

Heading, verbatim: *"THE ADJOINT INSIDE THE TRIM IS THE COST DRIVER, AND THE
GRADED QUANTITY DOES NOT NEED IT"*. Load-bearing lines:

> The primal work in the completing run totalled **54.71 s** of `ExecutionTime`.
> The run nonetheless hit a 450 s wall cap, **inside an adjoint GMRES solve**
> (`Solving Linear Equation... 272.79 s`, `Main iteration 100 KSP Residual norm
> 3.399e-07 318.01 s`), with 12 Jacobian-coloring mentions in the log.
>
> `optFuncs.findFeasibleDesign` is a **gradient-based** trim: it converged in 2
> iterations and the adjoint it needs then dominates the level's wall time.
>
> **The graded quantity — CD at fixed CL — does not require an adjoint.** A
> primal-only secant trim on incidence obtains it in ~4 primals.

**Independently corroborated from the run's own bytes, not from the prose.**
`/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/level.log` carries
exactly **five distinct** incidence settings across six `Setting UMag` lines:

```
AoA = 4 degs
AoA = 4.001 degs
AoA = 4.321108342 degs
AoA = 4.322108342 degs
AoA = 4.326120747 degs
```

The `+0.001 deg` pairs are the derivative bumps a **gradient-based** trim needs.
A secant trim needs none of them: it takes its slope from the two evaluations it
has already paid for. **That is the mechanism, read off the producer's own
output.**

**Where this document departs from §R3, and why.** §R3's *"~7.6 core-min at L1,
~60 at L2, ~484 at L3 … the whole ladder for ~550 core-min"* applies the **warm**
rate to every primal, and it carries no **cold** first primal — which costs
**7.65× the warm rate** by that same section's own table. §8 re-costs the ladder
with the cold primal in it and lands at **1,632 core-min estimated**, not 550.
**This is a correction in the conservative direction and it is stated up front so
nobody reconciles the two figures afterwards.** It remains far inside the parent's frozen 7,000 core-min
ceiling.

---

## 3. The family — the parent's frozen level spec, reused BYTE-FOR-BYTE

`cases/dafoam/a2gc_levels.json`, md5 **`5bfefe8bc9b6ef3324efcc795d5b23ab`** —
**verified on disk and against `HEAD` (blob
`97115c5c86bd51bf3d45f01534d558eb39ef3fc5`) on 2026-09-10.** It is a *level
specification*, not a grading rule; it is reused unchanged and this item re-pins
the same md5.

| level | surface op | faces | pyHyp `N` | layers | cells | `s0` | role |
|---|---|---|---|---|---|---|---|
| L0 | `coarsen` ×2 | 252 | 20 | 19 | 4,788 | 2.0e-3 | reserve, **not graded** |
| **L1** | `coarsen` ×1 | 1,008 | 39 | 38 | **38,304** | 1.0e-3 | coarse |
| **L2** | as downloaded | 4,032 | 77 | 76 | **306,432** | 5.0e-4 | middle |
| **L3** | `refine` ×1 | 16,128 | 153 | 152 | **2,451,456** | 2.5e-4 | fine |

- **r = 2.000 exactly**, in every direction, on every consecutive pair.
- **`marchDist = 300.0` is identical on every level** (`march_dist_all_levels:
  300.0` in the frozen JSON).
- Consecutive ratios asserted, not assumed: cells **8.000**, faces **4**, layers
  **2**, `s0` **2**.
- pyHyp's reported *Grid Ratio* is **not** expected to be constant across levels
  (1.3562 measured at L1, ~1.165 predicted at L2, ~1.079 at L3) and a similarity
  test demanding constancy would be wrong — the frozen JSON's
  `_growth_ratio_note` states why and this item inherits it.
- The graded triple is **L1, L2, L3**. L0 is not in it.

**A level whose MEASURED cell count differs from the predicted count above is
`NOT A RESULT`, reason "the family is not similar".** Threshold: exact integer
equality.

---

## 4. The graded quantity, and the primal-only secant trim

**GRADED QUANTITY: CD of the BASELINE wing (twist = 0, shape = 0) at fixed
CL = 0.500, on all three levels.**

Incidence is the trim variable, not an input. The AoA at which CL = 0.5 is
reached **differs between levels**; that is correct and it is reported per level.

**Geometry control, inherited from parent §3.** The driver reads `twist` and
`shape` back out of the problem and **raises** if either exceeds `1e-12`. A study
of the baseline wing that silently ran the optimised wing would be a wrong answer
that looks right.

### 4.1 The trim, specified to the point of implementation

`optFuncs.findFeasibleDesign` is **not used**. It is replaced by a primal-only
secant iteration on incidence. Every constant below is a registered threshold.

| symbol | value | note |
|---|---|---|
| `CL_TARGET` | **0.500** | parent §3, unchanged |
| `TRIM_TOL` | **5.0e-4** on \|CL − CL_TARGET\| | parent §3, **unchanged and deliberately not widened** |
| `ALPHA0` | **4.0 deg** | the pristine script's own `aoa0`; its primal is the one the pristine chain already runs |
| `A_SEED` | **0.10 per degree** | **SEED ONLY.** Used once, to place evaluation 2. It is never reported as a lift slope and never enters a graded number. From evaluation 3 the slope is the measured secant slope. |
| `N_SECANT_MAX` | **8** primal evaluations per level | including evaluation 1 |
| `N_TRIM` | **1,000** SIMPLE iterations per trim evaluation | |
| `N_FINAL` | **1,000** SIMPLE iterations (the case's own `endTime`) | the graded primal's planned length |
| `N_FINAL_MAX` | **4,000** SIMPLE iterations, every level | **safety ceiling only.** It is NOT a plan: §6.2 shows the solver stops at its accept floor long before this, so buying iterations buys nothing. The ceiling exists so a pathological level cannot silently consume its cap. |
| `STEP_MAX_DEG` | **2.0 deg** | per-update step limiter |
| `ALPHA_BOUNDS` | **[0.0, 10.0] deg** | |
| `DEN_MIN` | **1.0e-9** | secant denominator floor |

**The iteration.** With `a` = incidence in degrees and `c` = the CL that
evaluation returned:

- evaluation 1: `a_1 = ALPHA0`
- evaluation 2: `a_2 = a_1 + (CL_TARGET − c_1) / A_SEED`
- evaluation k+1: `a_{k+1} = a_k + (CL_TARGET − c_k)·(a_k − a_{k−1}) / (c_k − c_{k−1})`

**Convergence criterion:** the loop stops at the first evaluation with
`|c_k − CL_TARGET| <= TRIM_TOL`. `a* = a_k`.

**What happens if the secant does not converge — every path ends in a LABEL, and
none of them ends in an estimate.** All five are recorded in the level's
`trim_record.json` and reported:

| guard | condition | outcome |
|---|---|---|
| **G-CAP** | `N_SECANT_MAX` evaluations reached without meeting `TRIM_TOL` | level **`BLOCKED`**, reason `trim_cap`. **Never estimated, never interpolated** — parent §3's rule, inherited verbatim. |
| **G-DEN** | `\|c_k − c_{k−1}\| < DEN_MIN` | level **`BLOCKED`**, reason `secant_denominator_degenerate`. The division is refused, not attempted. |
| **G-BOUND** | an update leaves `ALPHA_BOUNDS`; it is clipped to the bound and the clip recorded. It BLOCKS on **either** limb: **(a)** the clip leaves incidence **unmoved** (`a_next == a_k`), or **(b)** **two consecutive clips at the same bound** | level **`BLOCKED`**, reason `alpha_bound`. |
| **G-STEP** | `\|Δa\| > STEP_MAX_DEG`; the step is clipped to `STEP_MAX_DEG` and the clip recorded | **not** a failure. Clips are reported; a level that converges after a clip is a normal convergence. |
| **G-NAN** | a non-finite `a` or `c` | level **`BLOCKED`**, reason `non_finite`. |

**Limb (a) of G-BOUND was added because the suite that exercises it found the
guard reaching for the wrong label.** With limb (b) alone, an incidence pinned at
a bound produces the same CL twice and **G-DEN** fires first on a zero
denominator — a truthful label, but the wrong one: the trim did not stall on a
degenerate secant, it ran out of incidence. Measured on the G-BOUND suite before
the limb existed, and recorded here rather than tidied.

**A `BLOCKED` level means fewer than three levels stand, and therefore NO `p` and
NO GCI** (§5, and parent §A1.1 inherited).

### 4.2 The graded primal is a SEPARATE, LONGER run, and its CL is re-checked

The trim evaluations run at `N_TRIM` = 1,000 iterations. **The graded primal is
then run once at `a*`, warm-started from the trimmed state, under the case's own
unmodified stopping rule (`primalMinResTol 1.0e-8`, `primalMinResTolDiff 1e3` —
neither is touched, §6.2), with `N_FINAL_MAX` as a safety ceiling.** CD, CL and
AoA are read **only** from that graded primal. The trim evaluations' CD values
are recorded and are never graded.

**Registered re-check, and a registered prediction with it.** The graded primal's
**own** CL is re-checked against `TRIM_TOL`. A miss makes the level **`BLOCKED`**,
reason `graded_primal_cl_drift` — **and the trim is NOT re-entered on the graded
primal**, because re-trimming the run that produces the graded number is tuning
the answer.

**PREDICTION, registered before compute: the re-check passes on all three
levels.** Ground: parent §R4 records L1's CD *"bit-identical across the last 5 of
66 evaluations"* with a swing of `3.84e-07` over the last 13 — CL is settled well
before 1,000 iterations at L1. **If the re-check fails, that prediction is a miss
and is recorded as one**, and the likely cause named in advance is that CL
settles more slowly at L2/L3 than at L1.

---

## 5. Roache triple gating — `CLAUDE.md` rule 5, IN FULL

The order of operations is fixed and is not negotiable. It is stated here in full
rather than by reference, because it is the clause this item most depends on.

1. **A level that is not iteratively converged or not plateaued makes the row
   `NOT A RESULT`** — before the triple is looked at. Instrumented by GATE R
   (§6.2) and GATE I (§6.3).
2. **Classify the triple FIRST.** `CONVERGING` / `DIVERGENT` / `STAGNANT` /
   `OSCILLATORY` / `EXACT`, from `eps_21 = f2 − f1`, `eps_32 = f3 − f2`,
   `R = eps_32 / eps_21`:
   - `eps_21 == 0` and `eps_32 == 0` → `EXACT`
   - either `eps` == 0 → `STAGNANT`
   - `R < 0` → `OSCILLATORY`
   - `R >= 1` → `DIVERGENT`
   - else → `CONVERGING`
3. **A triple that is not `CONVERGING` is `NOT A RESULT`, whatever its value.**
   The three CD values, both `eps` and the classification are printed beside it.
4. **NO GCI IS QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE.** No exception, no
   diagnostic-only variant, no footnote form.
5. Only a `CONVERGING` triple reaches the band. Because `r` is **constant** at
   2.000 by construction (§3), the closed form applies and no fixed-point
   iteration is used: `p = ln|eps_21 / eps_32| / ln r`.
6. **GCI at Fs = 1.25**, on the fine pair:
   `GCI_fine = Fs · |(f3 − f2)/f3| / (r^p − 1)`.
7. `p` inside the registered band → **`PASS`**; outside → **`GATE FAIL`**; GCI
   printed in both cases.
8. **A gate can only turn a `PASS` or a `GATE FAIL` INTO a `NOT A RESULT`, never
   the reverse.**
9. **There is no two-level fallback.** Three levels are the minimum for an
   observed order. If fewer than three stand, the item emits an explicit
   `order/triple` row carrying **`BLOCKED`** if any member was blocked,
   **`PENDING`** if members simply never ran, else **`NOT A RESULT`** — with
   **no `p` and no GCI**. (Parent §A1.1, inherited.)

**ACCEPTANCE BAND: `p` in [1.5, 2.5].** Registered exactly as Sanaa set it in her
SS0 clause 3 and **not widened to suit this case**.

**Competing prediction, registered before compute, inherited from parent §5.1 and
restated here so it binds this item too:** `p` will land **BELOW 1.5, most likely
in 1.0–1.4**, because `div(phi,nuTilda)` and `div(phi,h)` are `bounded Gauss
upwind` — **first order** — and the turbulent-viscosity field feeds CD directly.
If that happens it is a **`GATE FAIL`** against the registered band. The
**first-ranked** candidate cause is the scheme order; the **second-ranked** is the
wall-treatment regime (§7.1). Both are named here, before any solver starts, so
neither can be offered afterwards as an explanation invented to fit the answer.
If `p` lands inside [1.5, 2.5] this prediction is a **miss** and is recorded as
one.

**The framing that travels with a `GATE FAIL` on this band** (parent §A1.2,
inherited): Sanaa keys the band to *the scheme's formal order*, and [1.5, 2.5] is
her parenthetical example **for a second-order scheme**. This scheme set is
**mixed**. A `p` near 1.2 would be the wing converging at the order its own
numerics carry. **A `GATE FAIL` reported without that sentence would be read as
"the wing failed its grid convergence study", which would be false.** The open
doctrine question — for a mixed-order scheme set, which formal order keys the
band — is Sanaa's, and **no agent may resolve it by moving the band.**

---

## 6. The gates, with thresholds and failure modes declared (`VERIFICATION_CHARTER.md` §2a)

Each gate answers §2a's two questions on its own face.

### 6.1 GATE C — completion, similarity and trim

| clause | threshold |
|---|---|
| stage `rc` | `== 0` |
| measured cell count | `==` the §3 predicted count, exactly |
| trim | `\|CL − 0.500\| <= 5.0e-4` on the **graded** primal |
| CD present | a non-zero CD read from the graded primal's own printed output |

- **Fails if:** any clause misses.
- **Could a wrong treatment still pass?** Yes — a run of the *optimised* wing
  would satisfy all four. **That is why the geometry control of §4 is also gated**
  and raises on `|twist|` or `|shape|` > 1e-12.
- **Failure class, read from the stage's own artifacts and never inferred from
  `rc` alone** (parent §A1.1, inherited): `overrun=YES-RUN-STOPPED` in the
  stage's `cost.txt`, or `rc` 137/143, or a kill line in the container log →
  **`BLOCKED`** (the box could not run it). Otherwise → **`NOT A RESULT`** (it
  ran and the answer does not stand).

### 6.2 GATE R — the absolute residual gate, and the reading this item takes

**Metric:** the worst **`initRes`** across the six transported equations
(`U0 U1 U2 he p nuTilda`) on the **final iteration of the graded primal**.
**Threshold: `<= 1.0e-8`.**

**`initRes` is the nonlinear residual — the quantity `primalMinResTol = 1.0e-8`
is compared against. `finalRes` is that iteration's linear-solve residual and is a
different quantity.** Both are recorded; **the gate is on `initRes`.** (Parent §4,
inherited, including its warning that the A2 decomposition's *"4.15e-07 to
6.02e-07"* are `finalRes` values and are **not** evidence of a converged primal.)

**THE READING THIS ITEM TAKES, AND THE AMBIGUITY IT DISCLOSES RATHER THAN
RESOLVES.** `CLAUDE.md` rule 5 clause (1) says *"any level not iteratively
converged **or not plateaued**"* — two tests. It is genuinely open whether GATE R
is the first of them.

- **The parent's frozen comparator took the LOOSER reading:** in
  `cases/dafoam/a2gc_grade.py`, the residual row is a separate `compose_row` and
  only GATE I ceilings the order row (`noise = any(not v for v in
  iter_gate.values())`).
- **THIS ITEM REGISTERS THE STRICTER READING, FAIL-CLOSED: a level failing GATE R
  is not iteratively converged, rule 5 clause (1) fires, and the `order/roache`
  row is ceilinged to `NOT A RESULT` — with no `p` and no GCI.**
- **The stricter reading is chosen because the answer is already partly known.**
  Inheriting the parent's looser reading *now*, with L1's `7.1566e-06` on the
  record, would be selecting the reading that lets this item report a `p`. A
  pre-registration resolves its own ambiguity **against** itself.
- **This is a doctrine question and this lane is not entitled to settle it.** If
  the supervisor or Sanaa rules the looser reading, that ruling is a **legal
  pre-compute amendment** under rule 2 provided it lands **before** the run root
  of §11 exists and names that absence as its condition. It may not land
  afterwards.

**GATE R AT 1e-8 IS STRUCTURALLY UNREACHABLE ON THIS CASE, AND THE MECHANISM IS
NAMED HERE BEFORE ANY SOLVER STARTS — NOT OFFERED AFTERWARDS AS AN EXCUSE.**

DAFoam accepts a primal — and stops it — at **`primalMinResTol ×
primalMinResTolDiff`**, which is also its **hard-fail gate**. This is not this
lane's inference; it is on the lab record twice:

- `verification/campaign/A2_ACCEPT_FLOOR_BINDING_FIELD_RULING_2026-09-08.md:74`
  names *"the accept floor (`primalMinResTol × primalMinResTolDiff = 1.0e-05`)"*
  and records it frozen **UNMOVED in either direction** by
  `d6rf7_accept_floor_control.py`.
- `cases/dafoam/A3_FD3_PREREGISTRATION.md:16-18` sets `primalMinResTolDiff` to
  `1.0e4` explicitly to keep *"DAFoam's hard-fail gate at the record's effective
  1e-4 so an unreachable 1e-8 target reports a shallow plateau instead of
  fabricating a crash."*

The pristine `runScript_AeroOnly.py:36-37` carries **`primalMinResTol: 1.0e-8`**
and **`primalMinResTolDiff: 1e3`**. **The accept floor on this case is therefore
`1.0e-5`.** The parent's L1 measured worst `initRes` **7.1566e-06** — *below the
floor*. **That primal was ACCEPTED at the floor; it did not plateau and it was
not truncated.** No iteration count reaches 1e-8 with the stock option set,
because the solver stops first.

**`primalMinResTolDiff` IS NOT TOUCHED BY THIS ITEM.** Tightening it to make the
gate reachable would move DAFoam's hard-fail gate onto 1e-8 and convert every
shallow plateau into a fabricated crash — the exact failure A3's registered
discipline exists to avoid — and the accept floor is frozen UNMOVED by a standing
control. **The gate does not move either.** Both stay where they are and the
consequence is reported.

**REGISTERED PREDICTION, before compute: GATE R reads `GATE FAIL` on all three
levels, at roughly 1e-6 to 1e-5 — the accept floor, not a plateau.** If any level
returns `initRes <= 1e-8`, this prediction is a **miss** and is recorded as one.

**GATE R-FLOOR — a GUARD row, counted toward NO verdict** (`VERIFICATION_CHARTER`
§2c: the guard exemption holds only while the row is counted toward nothing).
Threshold: worst `initRes` **<= 1.0e-5**, the accept floor itself. It separates
two facts the gate above cannot: *the solver accepted this primal by its own
criterion* versus *my iteration ceiling truncated it*. A level that hits
`N_FINAL_MAX` before the floor is a **truncated** primal and is a different
finding from an accepted one.

**What all this means for the verdict, said in advance:** GATE R failing on any
level makes that level not iteratively converged, rule 5 clause (1) fires, the
`order/roache` row is **`NOT A RESULT`**, and the item verdict is
**`NOT A RESULT`**. **This item is registered in the expectation that that is its
outcome**, and it is registered anyway, because it still returns:

1. **three measured CD values on a demonstrably similar family** with their GATE I
   ratio — which nothing on this box currently has; and
2. **the first direct measurement, at three refinement levels, of where this
   primal actually stops and why** — the question the parent's Stage M existed to
   ask and never asked, because it cap-stopped first.

**THE REMEDY IS ALREADY OWED AND IS NAMED, NOT INVENTED HERE.** The 2026-09-08
ruling states it: *"dafoam owes a numerics fix that drives the outer/SIMPLE loop
to convergence … more outer iterations, relaxation/`nOuterCorrectors` changes, or
a stronger pressure linear solver/preconditioner, registered as a successor with
the gate, threshold and floor UNCHANGED."* **That successor is NOT attempted
inside this item.** A `GATE FAIL` here is a **waypoint**, not a terminus, and the
record says so on its face.

### 6.3 GATE I — iterative change against the mesh step (Sanaa's SS0 clause 2)

> *"the iterative change in the graded quantity must be at least 10x smaller than
> the difference between consecutive mesh levels. If it is not, the observed order
> is noise, not discretisation."*

- **`delta_iter(level)`** = max − min of CD over the **last 20 %** of the graded
  primal's CD samples.
- **`Delta_mesh(level)`** = the smaller of the `|CD|` differences to its adjacent
  level(s).
- **THRESHOLD: `Delta_mesh / delta_iter >= 10.0`**, reported explicitly per level.
- A level failing GATE I ceilings the `order/roache` row to **`NOT A RESULT`** —
  *"iterative noise, not discretisation"* — whatever `p` says.
- **A missing history is NOT a satisfied gate.** If the CD series is absent or
  empty, `delta_iter` is unmeasured and GATE I is **`PENDING`**, never passed.
- **Could a wrong treatment still pass?** Yes, in one specific way: a
  `delta_iter` stuck at zero makes the ratio infinite and passes GATE I
  trivially. **That is the highest-value planted-zero control in this item** and
  it is armed (§10).

**IMPROVEMENT OVER THE PARENT, registered as a change and not slipped in.** The
parent's driver built the CD history from the stock OpenFOAM `forceCoeffs`
`coefficient.dat`, then **rescaled** it onto DAFoam's CD by a factor asserted into
`[0.5, 2.0]` (parent `a2gc_driver_block.py`, and its `G-HIST` guard). **This item
does not rescale anything.** The history is the solver's own printed `CD:` lines
— the identical quantity the graded number is read from. Verified against real
producer bytes: `A2-GC-wing-grid-convergence/L1/level.log` carries **66** `CD:`
lines and **66** `CL:` lines, and the last of each is `0.02961982052` /
`0.4999996084`, **reproducing the parent's own published §R1 values exactly.**
The `G-HIST` scaling guard is therefore **retired as unnecessary**, not weakened:
there is no scaling left to guard.

### 6.4 GATE S — similarity, the F28 lesson

Cell / face / layer / `s0` ratios and identical `marchDist` per §3, plus the
**max cell-to-cell volume growth** measured and reported per level from
`checkMesh -allGeometry`. A cell-count mismatch is `NOT A RESULT` (§3).

---

## 7. The two registered risks, as predictions with their consequences stated in advance

### 7.1 L3's minimum y+ is predicted at ~17 — inside the buffer layer

This case is **wall-modelled, not wall-resolved**: y+ min/max/mean
**68.79 / 1266.55 / 321.95** measured at L1 (`cases/dafoam/PROOF.md:2523`), and
reproduced by the parent's own L1 run at **67.17 / 1281.52 / 321.63**. Sanaa's
SS0 clause 1 ends *"where the case is wall-resolved"*, so **y+ gates nothing about
wall resolution here**. What binds instead is **wall-treatment REGIME consistency
across the family**.

| level | y+ min | y+ mean | y+ max | status |
|---|---|---|---|---|
| L1 | 68.79 | 321.95 | 1266.55 | **measured** |
| L2 | ~34.4 | ~161 | ~633 | predicted (y+ falls by r) |
| L3 | **~17.2** | ~80.5 | ~317 | **predicted** |

**WHAT IT MEANS FOR THE VERDICT IF IT LANDS — stated before compute:**

- **~17 does NOT disqualify L3.** The case uses Spalding's law
  (`nutUSpaldingWallFunction`), a single smooth formula deliberately valid across
  all y+ regimes with **no hard regime switch** (`cases/dafoam/PROOF.md:981-982`).
  It is a **disclosed risk**, and it is the **second-ranked** candidate cause if
  `p` misses its band (§5).
- **A NEW THRESHOLD, registered here because the parent left it implicit:** if
  L3's **measured** minimum y+ falls **below 5.0** — the viscous sublayer, a
  regime L1 and L2 are nowhere near — then the family's wall treatment has changed
  character between levels, the similarity assertion of §3 fails on the wall
  limb, and **L3 is `NOT A RESULT` on similarity**, which makes the
  `order/triple` row `NOT A RESULT` with **no `p` and no GCI**.
- **PREDICTION: min y+ at L3 lands at 17 ± 5 and this threshold does NOT fire.**
  If it fires, the prediction is a miss and is recorded as one.

### 7.2 L4 is already registered `BLOCKED` on this instance

Inherited verbatim from parent §8 (`:266`):

> **L4 = 19,611,648 cells. REGISTERED IN ADVANCE AS `BLOCKED` ON THIS INSTANCE** —
> 64x L3's memory and wall time on a 16-core / 30 GB box

**WHAT IT MEANS FOR THE VERDICT IF IT LANDS — stated before compute.** If `p`
misses the band, Sanaa's SS0 step-4 escalation runs. Step 4(a) (re-check
iterative convergence on the finest level) and step 4(b) (verify similarity) are
**available and will be executed**. Step 4(c) — *a fourth, finer level at the same
r* — is **UNAVAILABLE on this instance**, and so is step 4(d).

Therefore: **a `GATE FAIL` on `p` in this item ships with its escalation marked
PARTIALLY EXECUTED and the shortfall named on its face** — never as a completed
escalation. The only other level on the ladder is **L0 = 4,788**, which shifts the
window **coarser**, the opposite of what step 4(c) asks; if it is used it is
reported as a **disclosed deviation from SS0**, never as satisfying it.
**A promise the box cannot keep is worse than a disclosed limit.**

### 7.3 A THIRD risk this item adds, because the parent's memory anchor does not cover it

**L2 and L3 PRIMAL peak RSS are NOT MEASURED, and nothing on record bounds them.**
The parent's only RSS reading (§R4) is **11,885 MiB aggregate `VmRSS` summed over
12 ranks, which double-counts shared pages**, for a run that **included the
adjoint** — and its trustworthy form is only *"it ran under 6g without an OOM
kill, so true peak <= 6 GB"*. This item removes the adjoint entirely, so **that
bound says nothing useful about a primal-only run at 2.45 M cells.**

**Registered:**
- L1's stage measures **primal-only** peak RSS with the in-container sampler
  (aggregate `VmRSS` across all processes every 2 s, maximum retained —
  independent of cgroup version). It is reported with its **double-counting
  caveat attached**, and the trustworthy figure is the container cap it ran under
  without an OOM kill.
- **L2's and L3's `MEM_LIMIT` are set from that measured L1 anchor by
  linear-in-cells scaling BEFORE either launches.** The inherited `14g` / `26g`
  are starting values only and are replaced by the measurement.
- **If the scaled prediction for a level exceeds `MemAvailable − 3 GB`, that
  level is `BLOCKED` in advance and is NOT attempted.** A `BLOCKED` L3 means
  fewer than three levels stand → `order/triple` **`BLOCKED`**, **no `p`, no
  GCI** (§5 clause 9).
- The launcher refuses (exit 3) if `MemAvailable < MEM_LIMIT + 3 GB`, or if any
  `a2gcp_` container is already running.

---

## 8. Cost — `CLAUDE.md` rule 12

**Basis, and which half is measured.**

| quantity | value | status | source |
|---|---|---|---|
| warm SIMPLE rate, np=12, 38,304 cells | **0.1134 core-s/iteration** | **MEASURED** | parent §R2:578-581 |
| cold SIMPLE rate, np=12, 38,304 cells | **0.868 core-s/iteration** | **MEASURED** | parent §R2:569-576, solve 1 |
| mesh build at 38,304 | 0.533 s pyHyp; 8.02 s full pipeline | **MEASURED** | D14M `logMeshGeneration.txt`; `ladder-a/A2_mesh_time.json` |
| trim length | ~4 primal evaluations | **MEASURED** | parent row B1 |
| per-level cost factor | **×8** (cells ×8, iteration count held) | **EXTRAPOLATED** | |

**Registered plan and caps, at np = 12 on cpuset 4-15:**

Per level: **4 primal evaluations** (1 cold + 3 warm) at `N_TRIM` = 1,000
iterations, then **one warm graded primal** at `N_FINAL` = 1,000 (ceiling 4,000).
Worst case is `N_SECANT_MAX` = 8 evaluations plus a 4,000-iteration graded primal.

| level | mesh | **estimate (core-min)** | **worst under registered maxima** | **CAP** |
|---|---|---|---|---|
| L1 | 1 | **23.0** | 36.3 | **90** |
| L2 | 3 | **179.2** | 285.1 | **600** |
| L3 | 20 | **1,429.7** | 2,276.4 | **3,000** |
| | | **ITEM ESTIMATE 1,632** | **2,598 worst-under-plan** | sum of caps 3,690 |

**CUMULATIVE CAP: 3,300 core-minutes, AND IT STOPS THE LADDER.** It is set
deliberately **below the sum of the per-level caps (3,690)** so that it actually
bites rather than decorating the table. Operationally: **before launching any
level, the launcher sums `core_min` across every existing level `cost.txt` and
refuses (exit 4) if `cumulative + this level's cap > 3,300`.** An overrun **stops
the run; it does not get a new budget.** Each level's `timeout` is derived from
its cap as `cap_core_min × 60 / 12` wall seconds, and `overrun=YES-RUN-STOPPED`
is written into that level's own `cost.txt`.

**A DEFECT IN THE PARENT'S CAP MECHANICS THAT THIS ITEM DOES NOT INHERIT.**
`cases/dafoam/run_a2gc.sh` applies the SAME `CAP_WALL_S` as a `timeout` to the
mesh stage **and again** to the solve stage, so a level could spend up to **2×**
its registered cap while every check reported the cap as honoured. **This item's
launcher splits one wall budget across the stages and never re-arms it.**

**Wall time at np = 12:** estimate **2.27 h**; at the cumulative cap **4.58 h**.

**DOLLARS — DERIVED, NOT MEASURED.** At **$0.0513/core-h**, c7a.4xlarge,
**reported-by-owner** (Sanaa 2026-08-21/22): **the box cannot read its own
billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so no figure here is a measurement of
spend.

- estimate **1,632 core-min = 27.20 core-h → $1.40 (DERIVED)**
- cumulative cap **3,300 core-min = 55.00 core-h → $2.82 (DERIVED)**

Both are under the $25 pre-authorisation. **A blanket authorisation is not a
per-item reading** (rule 9): this item is costed on its own face regardless.

**GPU: 0 GPU-h.** None registered, none used. GPU spend sits outside the
2026-08-21 blanket and none is sought here.

**Rule 12 calibration clause applies at completion:** predicted against actual, in
core-minutes, ratio stated, gap attributed (contention / waste / misprediction,
waste named separately and never absorbed), landing as a row in
`docs/COST_CALIBRATION.md`.

---

## 9. The instrument — what carries over, what changes, what is authored

### 9.1 Carries over UNCHANGED

| artifact | md5 | disposition |
|---|---|---|
| `cases/dafoam/a2gc_levels.json` | `5bfefe8bc9b6ef3324efcc795d5b23ab` | **reused byte-for-byte**, re-pinned here; verified on disk and at `HEAD` blob `97115c5c86bd51bf3d45f01534d558eb39ef3fc5` |
| pristine `runScript_AeroOnly.py` | `2906d52a5dbed2bacbaeaf85a37d3fe8` | verified on disk 2026-09-10; the level driver is this file plus a disclosed appended block, with `driver_vs_pristine.diff` written beside every level |

The following **logic** in `cases/dafoam/a2gc_grade.py` (md5
`f360f6b0cfbaee7029775ad8453c13f5`) carries over unchanged in substance:
`classify_triple`, `observed_order`, `gci_fine`, `compose_row` /`compose_item`
with `verdict_before_ceiling` read by the item (the D19M defect deliberately not
inherited), the `SEVERITY` map with `PENDING` below `GATE FAIL`, the
resource-vs-numerical failure classification, and the birth-register /
refusal-path pattern.

**That grader is live at `HEAD`, not merely asserted:** `a2gc_grade.py
--selftest` was run on 2026-09-10 and returned rc 0 with *"REFUSAL PATH
DEMONSTRATED: blinding each of the 9 readers in turn made the register refuse,
9/9"*.

### 9.2 MUST change — enumerated so a reader can check the diff

1. **The trim.** `optFuncs.findFeasibleDesign` out; the §4 secant in.
   `a2gc_driver_block.py` (md5 `ecd5d4eb9b71e628658c52e305276d5d`) is **not**
   reused.
2. **The readers.** The parent reads a `GC_RESULT` line **that no A2-GC run has
   ever emitted** (parent §R4: *"L1 did not emit its `GC_RESULT` line"* — both
   completing runs were killed by their cap during the post-trim adjoint). This
   item reads the solver's **own** printed `CD:` / `CL:` / `Setting UMag … AoA =`
   lines, which **do** exist in real producer output. See §10.
3. **The CD history.** No `forceCoeffs` rescale, no `G-HIST` scaling guard (§6.3).
4. **GATE R's ceiling.** Registered ON in this item, fail-closed (§6.2) — the
   parent's comparator has it OFF.
5. **New rows:** the trim record (`trim_record.json`: evaluations, guards fired,
   clips), and L3's min-y+ similarity threshold of §7.1.
6. **Caps.** §8's per-level and cumulative caps replace the parent's entirely, and
   the cumulative one stops the ladder.
7. **Launcher.** New run root, one wall budget split across stages (§8), a
   cumulative-cap refusal, and — see §9.4 — **it must assert its OWN md5**.

### 9.3 What this lane authored in this turn, and what it did NOT

**AUTHORED, and it is a MEASUREMENT script — read it as a diff:**

| file | md5 at drafting |
|---|---|
| `cases/dafoam/a2gcp_secant.py` | **`594ec4fe904fab5737448e7b79c6fa1e`** |
| `cases/dafoam/a2gcp_driver_block.py` | **`516cdb0e636e768328d378109e380b5a`** |

- **`cases/dafoam/a2gcp_secant.py`** — the trim's pure core (secant update and
  all five guards), the disk readers, the rule-3 birth register with its
  refusal-path control, and `--selftest`. **It has no DAFoam, OpenMDAO, MPI or
  OpenFOAM import and runs standalone**, which is what lets its selftest run
  **before any solver** rather than only inside the container.
- **`cases/dafoam/a2gcp_driver_block.py`** — the block appended to the pristine
  script. It calls `a2gcp_secant.preflight()` **before the first trim
  evaluation**, asserts the baseline geometry, drives the secant with
  `prob.run_model()` as the evaluator, writes `trim_record.json`, then runs the
  single graded primal and re-checks its CL.

**Two defects the selftests found in the authored code before it went anywhere
near a solver, recorded rather than tidied:**

1. The `read_iter_delta` witness demanded the planted swing equal the plant
   exactly. The real series carries its own swing (`3.8385e-07`), so the planted
   swing is plant-plus-that and the register **refused** — correctly. Repaired by
   giving the witness a falsifiable *predicate* instead of a constant, so the
   control never recomputes what the reader computes.
2. **G-BOUND reached for the wrong label.** With only the "two consecutive clips"
   limb, an incidence pinned at a bound returns the same CL twice and **G-DEN**
   fires first on a zero denominator — truthful, but wrong: the trim ran out of
   incidence, it did not stall on a degenerate secant. Repaired by adding the
   no-movement limb (§4.1), and the registered guard text was moved with the
   code, not left behind.

**NOT AUTHORED — specified above, still to be written:**

- **`cases/dafoam/a2gcp_grade.py`** — the successor comparator. §9.2 enumerates
  every difference from `a2gc_grade.py`; it is a derivation, not a fresh design.
- **`cases/dafoam/run_a2gcp.sh`** — the launcher, including the split wall
  budget, the cumulative-cap refusal, the rule-4 absent-directory guard, the
  placement gate, and the self-md5 assertion of §9.4.

**Neither of the two authored files has been exercised against a solver, because
no solver may run in this window.** Their selftests are the only demonstration
that exists, and the record says so.

### 9.4 A DEFECT IN THE PARENT'S INSTRUMENT SET — reported, NOT repaired

**`cases/dafoam/run_a2gc.sh` no longer matches the md5 the frozen parent pins
for it.** The parent's AMENDMENT 2 pins `f3baba360a50c8b7592d0a50142d5e28`. The
file on disk and at `HEAD` is **`e7008a7a1bdf0e55ec8bad8e2b8742d4`**. The change
landed in commit `d48dd7e6` (2026-09-02T05:00:34Z, *"emergency snapshot before
subscription switch"*), after the frozen state in `b02537f5`.

The two hunks are the `--allow-run-as-root` mpirun flag and moving `set -u` to
after `loadDAFoam.sh` — i.e. the repairs for the parent's own recorded attempt-1
`ENVFAIL` and attempt-2 `MPIROOT` waste. They are **off the grading path** (no
band, reference, row definition, verdict rule, discrimination test or mutation
control is touched), so `VERIFICATION_CHARTER.md` §2d permits them — **but §2d
requires a dated disclosure naming what was added, when, and which findings rest
on it, and no such disclosure exists.**

**Contributing cause:** `run_a2gc.sh` asserts the md5 of the grader, the level
spec, the driver block and the pristine script — **and never its own.** Its own
drift is unpoliced by construction.

**This lane does not touch the parent** (`CLAUDE.md` rule 6). Two things follow
for this item, and only they are actioned here:

1. **`run_a2gcp.sh` MUST assert its own md5 against a value pinned in this
   document**, refusing (exit 2) on a mismatch.
2. Every md5 this document pins is **verified against `HEAD`, not only against
   the working tree**, at freeze time.

---

## 10. Planted-zero controls — `CLAUDE.md` rule 3 and `VERIFICATION_CHARTER.md` §2j

**No instrument grades anything until it has been shown able to see a planted
non-zero through the real code path.** `PLANT = 1.234e-03`, the lab's standing
plant constant.

**§2j's operative phrase is "through the real code path", and the test is: who
WROTE the bytes the control reads?** This item answers it as strongly as the
evidence on disk allows, and states the residue plainly.

**LIMB 1 — REAL PRODUCER BYTES (satisfies §2j).** The birth register reads
`/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/level.log` —
**104,762 bytes written by the real DAFoam/OpenFOAM stack** — through the real
readers, and asserts the clean reading reproduces the parent's own published
values:

| reader | clean reading from real bytes | parent §R1 |
|---|---|---|
| `read_cd` | **0.02961982052** | 0.02961982052 |
| `read_cl` | **0.4999996084** | 0.4999996084 |
| `read_aoa` | **4.326120747 deg** | 4.326120747 deg |
| `read_cd_series` | **66 samples** | 66 evaluations |

The plant is then applied **into those same real bytes** and each reader must see
it and must **not** return the clean value. **A reader that cannot see its plant
REFUSES, exit 2.**

**This artifact is a REQUIRED RETAINED ARTIFACT of this item.** If it is deleted,
LIMB 1 cannot run, and the selftest **refuses** rather than skipping.
`VERIFICATION_CHARTER.md` §9: retained under the campaign, not left in scratch.

**LIMB 2 — THE CONTROL ON THE CONTROL.** A register never shown able to **refuse**
is not evidence either. Each reader is blinded in turn to a zero-returning stub
and the register **must** refuse on that reader, every time, through the real code
path. Where blinding a *series* reader also blinds the readers derived from it,
the dependency is **declared** (`read_cd_series` → `read_cd`, `read_iter_delta`;
`read_cl_series` → `read_cl`) rather than papered over by accepting any refusal
at all, which would weaken LIMB 2 to *"something went wrong somewhere"*.

**DEMONSTRATED, 2026-09-10, `a2gcp_secant.py --selftest`, rc 0:**

- **7 readers declared, 7 born, 7 zero-passing**;
- **6 of the 7 exercised on REAL producer bytes** — the 104,762-byte
  `A2-GC-wing-grid-convergence/L1/level.log`;
- **refusal path 7 of 7** — blinding each reader in turn made the register refuse;
- **an absent producer artifact REFUSES rather than skipping**, exercised
  explicitly;
- **9 secant suites passed**, including all four `BLOCKED` guard paths (G-DEN,
  G-BOUND, G-CAP, G-NAN), the G-STEP limiter, the recovery of the parent's own
  measured **4.326120747 deg** from an anchored model, and the registered trivial
  baseline (§2c / `DAFOAM_CHARTER` §4): **a one-evaluation no-move trim must NOT
  converge**, else convergence would not be evidence that the secant did anything.
- **NO SOLVER RAN.**

**THE RESIDUE, STATED RATHER THAN GLOSSED.** `trim_record.json` has **no real
producer bytes anywhere on this box** — no A2-GC-P run has ever written one. Its
reader's control is on **producer-shaped** bytes written by the test harness,
which is exactly the condition §2j names as insufficient. **The full §2j
demonstration for `read_trim_record` is therefore OWED, and is registered as a
PRECONDITION: L2 and L3 may not be graded until the register has been re-run
against L1's own emitted `trim_record.json`.** Until then any `trim_record`
reading is `PENDING`, not `PASS`.

**THE HIGHEST-VALUE PLANT IN THIS ITEM is `read_iter_delta`.** A `delta_iter`
stuck at zero passes GATE I trivially and hands back an observed order that is
pure iterative noise dressed as discretisation — exactly the failure Sanaa's SS0
clause 2 was written against. It is planted, and its zero-passing status is
declared `true` in the register.

**`read_yplus`, `read_peak_rss`, `read_cells`, `read_residual` and
`read_vol_growth` LIVE IN THE GRADER, WHICH IS NOT AUTHORED YET (§9.3), SO THEY
ARE NOT IN THE DEMONSTRATION ABOVE.** They are registered here so the grader's
author cannot quietly drop one: each must be born on real producer bytes before
it grades. `read_yplus` and `read_peak_rss` are declared
`a_zero_here_could_pass_a_gate: false` — **except** that a zero y+ WOULD trip
L3's min-y+ threshold of §7.1, reading as *below* 5.0 and making L3
`NOT A RESULT`. **That is fail-closed and is left fail-closed**, and it is
declared as such rather than quietly excluded from the register.

---

## 11. Run root asserted ABSENT, against a positive control

> **The run root `/home/ubuntu/certonomous-runs/A2-GC-P-wing-grid-convergence`
> DOES NOT EXIST.** Read at **2026-09-10T04:08:32Z**. A glob for `*A2-GC-P*` and
> `*a2gcp*` under `/home/ubuntu/certonomous-runs/` returns **zero** directories.
> **The reader was shown able to see a directory that DOES exist** —
> `/home/ubuntu/certonomous-runs/A2-mach-wing` — a planted positive control on
> the absence check itself.

`run_a2gcp.sh` re-asserts the level directory absent immediately before launch and
**refuses (exit 2) if it exists** — the `CLAUDE.md` rule-4 guard: a guard refuses
a case where `0` or a time directory already exists, because a pre-existing tree
means the answer may predate the run allowed to produce it.

**Placement, registered:** `cpuset 4-15` (12 of 16 cores, leaving 0-3 for peers),
`np = 12`. **The box is currently saturated and NOTHING LAUNCHES until it drains**
— the launcher's own placement gate (§7.3) enforces this independently of any
agent's judgement.

**Decomposition disclosure** (`DAFOAM_CHARTER.md` §5): every level runs at
**np = 12** with the case's own default decomposition, while the published
baseline ran at **np = 4**. Consistency ACROSS the three levels is what an order
study requires, and it holds. But this family has a **known decomposition
sensitivity** (`DEFECT_REACH_decomposition_cases.md` names A2 at 38,304 cells,
scotch vs simple at np=4), so **L1's CD is reported against the published np=4
value 0.02962051221 as a disclosed reproduction check, not assumed to match.** Any
difference is reported, never absorbed. **The decomposition method and
`numberOfSubdomains` travel in the same table as every number.**

---

## 12. Verdict vocabulary

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`
only. `PENDING` is a queue state and **never softens a `GATE FAIL`**. The band
goes on every number. **A gate can only turn a `PASS` or a `GATE FAIL` INTO a
`NOT A RESULT`, never the reverse.**

**This item's own standing at the moment of drafting: `PENDING` — not frozen, not
launched, zero core-minutes spent.**
