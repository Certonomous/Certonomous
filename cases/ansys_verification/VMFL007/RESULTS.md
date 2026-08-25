# VMFL007 run 1 — RESULTS — `NOT A RESULT`, tier `NOT HELD`

**Case:** VMFL007 — Non-Newtonian Flow in a Pipe — Ansys Fluid Dynamics
Verification Manual, Release 2026 R1, **printed page 29**.
**Pre-registration frozen at `48f7a9bf930fbd06bf23ba4b6469754f879cb74e`,
2026-08-25T16:51:56Z** — before any solver started.
**Comparator frozen at `23091132`, blob `9a727216a73eedcdfbeff2b40c0f5a8f65db65e6`.**
**Run root:** `verification/runs/ansys_verification/VMFL007/`.
**Record written by `ansys-lane-opus`; the verdict and tier are the
`ansys-verification-supervisor`'s rulings, made after its personal crash triage
(`SUPERVISION_CHARTER` §3 check 2, non-delegable).**

---

## 1. THE VERDICT

> ### **`NOT A RESULT`. TIER: `NOT HELD`.**
> ### **NO NUMBER WAS PRODUCED. The case did not converge — it DIVERGED, by 143 decades.**

**Spend: 6.2666 core-minutes of a frozen 60 core-minute cap. The cap never bit.**

**The comparator was never run to grade.** It did not need to be: the frozen
pre-registration's own iterative-convergence clause (§8.2) and `CLAUDE.md` rule 5
step 1 both refuse this run before any triple is formed, and rule 5 permits the
gate to turn a result **into** `NOT A RESULT` and never the reverse.

---

## 2. WHAT RAN

| level | cells | rc | wall s | core-min | iterations reached | outcome |
|---|---|---|---|---|---|---|
| `L1_25x25` | 625 | **0** | 233 | **3.8833** | **10 000 of 10 000** | completed; `End` line written |
| `L2_50x50` | 2 500 | **136** | 143 | **2.3833** | **9 065 of 10 000** | **SIGFPE**, core dumped |
| `L3_100x100` | 10 000 | — | — | — | — | **never launched** — the launcher aborts the whole run on a non-zero rc |
| | | | **376** | **6.2666** | | against a **60 core-min** cap |

Sources: `L1_25x25/RUN_RC.txt`, `L2_50x50/RUN_RC.txt` (both carry
`prereg_sha = 48f7a9bf930fbd06bf23ba4b6469754f879cb74e`), and the two
`log.simpleFoam` files.

**The L2 crash, from the stack trace in `L2_50x50/log.simpleFoam`:** `SIGFPE`
inside **`Foam::GAMGSolver::scale`**, reached through `GAMGSolver::Vcycle` →
`GAMGSolver::solve` → `fvMatrix<double>::solveSegregated`, at **`Time = 9065`**,
after the three `smoothSolver` momentum solves of that iteration and inside the
pressure solve.

---

## 3. THE FINDING THAT MATTERS IS NOT THE CRASH

> ### **`rc = 0` PLUS AN `End` LINE IS NOT CONVERGENCE, AND `L1`'S CLEAN COMPLETION IS HOLLOW.**

`L1_25x25` satisfied every clause of `CLAUDE.md` rule 4 that a launcher can
observe — it exited `0`, wrote `End`, and reached `Time = 10000`. **It had also
diverged by 143 decades.**

### 3.1 The gate channel — measured

`postProcessing/pInlet/0/surfaceFieldValue.dat`, `areaAverage(p)` on the inlet
patch, **kinematic** (m²/s²); the physical value is **60.52196938383448**:

| iteration | `areaAverage(p)|inlet` [m²/s²] |
|---|---|
| 1 | **3.022488374470e+04** — already **499×** the physical value |
| 5 | **−2.944123528861e+03** — *sign-reversed* |
| 2 000 | 8.230493799978e+34 |
| 4 000 | 3.335042792582e+63 |
| 6 000 | 1.251790473612e+88 |
| 8 000 | 3.054561935821e+117 |
| **10 000** | **9.449536950130e+144** |

Monotone growth of roughly **1.4 decades per 100 iterations** from about
iteration 900 onward. `L2_50x50` behaves identically and **faster**, reaching
**6.034959177466e+211** at iteration 9064, its last recorded value.

### 3.2 The continuity error — measured

`time step continuity errors : sum local`, `L1_25x25`:

| iteration | 1 | 2 | 3 | 1 000 | 5 000 | 10 000 |
|---|---|---|---|---|---|---|
| value | **0.0832213752667** | **162.401798376** | **685.538668204** | 3.386e+09 | 2.591e+36 | **1.04772404566e+72** |

> **THE DIVERGENCE BEGINS AT ITERATION 2** — three decades in two iterations,
> while the viscosity field is still physical and the pressure matrix still
> well-conditioned. `L2_50x50` reaches **3.02219858509e+105** by its last
> complete iteration.

### 3.3 THE VISCOSITY FIELD COLLAPSED ONTO ITS `nuMin` FLOOR — and this is the amplifier

`postProcessing/{nuMinAll,nuMaxAll}/0/volFieldValue.dat`:

| iteration | `nuMax` (whole domain) | `nuMin` (whole domain) |
|---|---|---|
| 1 | 1.919475666097e−01 | 1.711566542501e−05 |
| 4 | 3.879812381484e−04 | 9.377257215064e−07 |
| 500 | 9.937321971832e−07 | 1.0e−08 |
| **904 → 10 000** | **1.000000000000e−08** | **1.000000000000e−08** |

> **From iteration 904 on `L1` (and 715 on `L2`) EVERY CELL IN THE DOMAIN sits on
> the `nuMin` floor of 1e−08 — a value 4 298× BELOW the physical wall viscosity
> of 4.298435325556426e−05 m²/s.** Reaching that floor requires a shear rate of
> **1e10 s⁻¹** against the physical wall value of **8 800 s⁻¹**, a factor of
> **1.14e6**.

**This is a positive-feedback amplifier, and naming the direction matters.** A
shear-thinning power law (`n = 0.4`, `ν ∝ γ̇^−0.6`) responds to a growing velocity
error by **reducing** viscosity. Less viscosity means less damping, which grows
the error further, until the clip catches it — and the clip is 4 298× too low to
damp anything. **The floor did not cause the divergence; it removed the only
mechanism that could have arrested it.**

### 3.4 THE `nuMax` CEILING NEVER BOUND — the supervisor's refutation, CONFIRMED BY DIRECT MEASUREMENT

The supervisor raised, and then refuted against itself, the concern that the
`nuMax = 1.0` ceiling binds on the axis, since `ν` diverges as shear → 0 and a
pipe axis has zero shear by symmetry. **Its refutation stands and is now measured
rather than estimated.** `ν = nuMax = 1.0` requires **γ̇ < 4.64159e−4 s⁻¹**
(re-derived here independently; the supervisor's 4.64e−4 confirmed), and the
`nuMaxAll` monitor records **ZERO iterations at the ceiling on either level**,
across all 10 000 and 9 065 iterations respectively. **The predecessor lane's
claim that the ceiling never binds is correct, and it is read off the artifact.**
**Do not "fix" a clip that is not binding.**

### 3.5 THE RESIDUAL CHANNEL WAS BLIND — and this is a fact about the instrument

Final initial residuals at iteration 10 000 on `L1`: **`p = 0.384379448697`**,
**`Ux = 0.0500746645232`**. Across the whole run `p` oscillates in ≈**[0.15,
0.46]** and `Ux` in ≈**[0.042, 0.072]**. **Neither ever descends.**

> **AND NEITHER COULD.** OpenFOAM normalises the initial residual by a factor
> built from the field's own magnitude, so **the reported ratio is
> SCALE-INVARIANT**: a solution growing by 143 decades holds a *bounded*
> normalised residual throughout. **The residual channel was never going to show
> this divergence, whatever the case did.** The channels that did show it are the
> **gate monitor** (`pInlet`) and the **viscosity monitor** (`nuMaxAll`) — both
> registered in the frozen `controlDict.template` before compute.

**There is no `nan`, no `inf` and no bounding message anywhere.** Measured: a
case-insensitive sweep for `nan|inf|bounding` returns **0** hits in `L1`'s
**90 076**-line log and the same in `L2`'s **81 671** lines. **OpenFOAM's SIMPLE
loop printed no warning of any kind while the solution grew 143 decades.**

### 3.6 THE `SIGFPE` IS AN OVERFLOW SYMPTOM, NOT A LINEAR-SOLVER DEFECT

`L2`'s `areaAverage(p)|inlet` reached **6.034959177466e+211** at iteration 9064.
A **squared** quantity overflows an IEEE double (max 1.7976931348623157e+308)
above **1.341e+154**. `GAMGSolver::scale` forms inner products of the correction
field — exactly such squares.

**The crash site is simply where the first product of two enormous numbers
happens to be formed.** Any solver forming an inner product would have died
somewhere in its own inner loop. **This bounds the leading diagnosis handed to
this lane** — *"GAMG's agglomeration degrades on strongly varying coefficients"*,
correctly labelled *consistent-with, not established* — **and the trajectory is
not consistent with it: from iteration 904 the coefficient field is UNIFORM at
1e−08, so GAMG is solving a CONSTANT-coefficient Laplacian for the last 8 161
iterations before it dies.**

### 3.7 WHAT WAS **NOT** WRONG — the inlet, measured and exonerated

The inlet boundary condition held **exactly constant** for all 10 000 iterations
and is not implicated:

| channel | measured | registered / expected | agreement |
|---|---|---|---|
| `UmaxInlet` | **3.142847411860 m/s**, unchanged every iteration | 3.142857142857143 | **−3.096e−06 relative** — mesh quadrature on 25 radial cells |
| `QInlet` | **−2.728573539857e−08 m³/s**, unchanged every iteration | −2.727076956241e−08 (= 2 m/s × sector area) | **+0.0549 %** — the inlet-quadrature term the frozen registration predicted at *"+0.06 % at L1"* |

**The frozen registration's §9.5 two-channel inlet assert therefore PASSES.** The
mean is 2 m/s and the shape is the power-law profile, not a uniform inlet. **The
divergence is interior.**

---

## 4. THE INSTRUMENT WOULD HAVE WORKED — the case never gave it anything to grade

**The frozen comparator was sound and would have refused correctly.** Three of its
clauses each independently refuse this run:

1. **The `S13` plateau clause (§8.2, PRIMARY):** `9.449536950130e+144` is not a
   plateau by any normalisation.
2. **The residual backstop (§8.2, SECONDARY):** `p = 0.384` against a frozen
   `≤ 1e−4`, missed by **3 843×**.
3. **The planted-zero control (§9.6, rule 3):** frozen with an **absolute**
   `PLANT_DAT_TOL = 1e−12`. On a series of magnitude 1e+144 the 1.234e−3 plant is
   below the floating-point resolution of the value it is added to, so the
   read-back delta is exactly `0.0` and `|0 − 1.234e−3| > 1e−12` **refuses**.
   **The control is correctly shaped and would have fired.** *(A value-relative
   tolerance would have waved it through — a defect the R2 lane found in its own
   first draft and repaired before freezing. Run 1's frozen artifact does not
   have it.)*

**`CLAUDE.md` rule 5 step 1 is decisive on its own:** no level was iteratively
converged, so the row is `NOT A RESULT` before any triple is formed.

---

## 5. TIER: `NOT HELD` — the supervisor's ruling, and why it is right

**`NOT HELD`, not the softer `GATE REACHED`.** `GATE REACHED` requires a
believable measurement missing one column. **There is no measurement here at
all** — no triple, no observed order, no GCI, no plateau statistic, no Δp worth
quoting. This is the same shape as VMFL045 run 1 and VMFL001 run 1, both ruled
`NOT HELD` for the same reason: **nothing was measured, so there is nothing to
hold.** The `V` column would have been available (the reference is closed-form);
it is unearned because no number exists to compare.

---

## 6. COST CALIBRATION (`CLAUDE.md` rule 12, charter §5.7)

**Ledger row: `docs/COST_CALIBRATION.md`.**

| | |
|---|---|
| predicted (frozen §10) | **15 core-min**, whole triple |
| **actual, MEASURED from `RUN_RC.txt`** | **6.2666 core-min** (L1 3.8833 + L2 2.3833) |
| naive ratio | **0.4178** — **MISLEADING and labelled so: only 1.91 of 3 levels ran** |
| **like-for-like on L1** | predicted share **0.7143** core-min vs **3.8833** measured → **ratio 5.4366** |
| like-for-like on L2 (to 9 065) | predicted share **2.5900** vs **2.3833** → **ratio 0.9202** |
| **full triple projected at the measured L1 rate** | **81.55 core-min → the frozen estimate was low by 5.44×** |
| cap | 60 core-min. **Never bit.** Spend was **10.4 %** of it |
| derived dollars | **$0.00536** at $0.0513/core-h — **DERIVED, not measured** |
| waste | **2.3833 core-min** — L2's crashed run produced no usable field. **Named separately and NOT absorbed into the ratio** (`COMPUTE_BUDGET_CHARTER` §6) |

**Attribution — misprediction, and the model itself is invalid here.** The frozen
estimate used **2.115e−6 core-s per cell-iteration** (from VMFL001) **× 4**. The
measured L1 rate is **3.728e−5**, **4.4066×** the assumed figure. **But the rate
is not scale-invariant on this case:** L2 measured **6.309983e−6 core-s per
cell-iteration**, **5.9081× cheaper than L1 at 4× the cells** — which is why the
two like-for-like ratios (5.44 and 0.92) disagree so violently. **Cost per outer
iteration is the count of inner linear-solver sweeps, and on a diverging solve
that count wanders.** A per-cell-iteration rate is not a valid basis for this
case, and VMFL007-R2 does not use one.

**Contention, named and never subtracted.** `CONTENTION.txt` records at launch
(2026-08-25T16:57:33Z) **loadavg 9.32 on 16 cores** with five co-resident
solvers. Contention raises serial wall time, so **6.2666 core-min is GROSS** and
the clean figure is unknown — no measurement of the contention's size was taken.

---

## 7. WHAT THIS RUN COULD NOT VERIFY

1. **The cause of the divergence.** Measured that it begins at iteration 2;
   **not established why.**
2. **Whether the linear solver contributes.** That is `VMFL007-R2`'s registered
   question and it is **not answered here**.
3. **Whether the 73 under-determined cells contribute.** Their existence is
   measured (`VMFL007_R2/mesh/birth_certificate_L1.json`); their effect is not.
4. **The size of the contention effect.**
5. **`L3_100x100` behaviour** — never launched.

---

## 8. WHAT HAPPENS NEXT

**`VMFL007-R2`** — `cases/ansys_verification/VMFL007_R2/PREREGISTRATION.md`,
machinery at **`1387b89f`** — registers a **six-arm linear-solver /
preconditioner slate**, executing Sanaa's rule 2. **Run 1's tree, its
pre-registration and its comparator are PRESERVED and are not edited, cleared or
re-labelled by it.** R2 is single-grid and its own case-level ceiling is
`NOT A RESULT`; it seeks no credential.

**R2 predicts, before compute, that no arm will converge** and names the
candidates that would then take over: the **convection scheme** (`div(phi,U)
bounded Gauss linear` — unbounded central at an axial cell-Péclet of **186 / 93 /
46.5** against a limit of **2**, where the lab's own **passing** case on the same
geometry, VMFL005, upwinded *"because of the high cell Peclet number"*), the
**relaxation factors**, and the **mesh**.

---

## 9. Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-25 | Created at close-out. Verdict `NOT A RESULT`, tier `NOT HELD` (the supervisor's rulings). Every figure re-measured in this lane from the artifacts named beside it rather than inherited from the triage brief. |
