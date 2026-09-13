# D6R3 — FIX PRE-REGISTRATION: ARMS `FIX_RELTOL1` AND `FIX_NONGAMG1`

DRAFT. Nothing sent, filed, uploaded, registered, posted or commented outside this box (rule 7).
Committed **before any compute for either arm** (rule 2). Two arms, one document, both frozen
together; neither launches before the commit that carries this file.

- Run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/`
- Arm dirs: `FIX_RELTOL1/`, `FIX_NONGAMG1/` — both refused by `G-COLD` if they already exist.
- Producer: the **FROZEN** `d6r3_opt_runScript.py`, md5 `efc3e62699690edd32e4ee910aad09c8`,
  **unedited**, in the **published** point order (`cl04`, `cl05`, `cl06`). Task `run_model`.
- Grading path, fixed at this commit: `d6r3_fix_grade.py`. Its self-test — a planted one-digit
  mutation the reader is shown able to report, a NEGATIVE control in which the published-`relTol`
  `P0` log is refused by IC-2, and a POSITIVE control in which the ordinal signature must read
  `PERSISTS` on a log that measurably has it — is `D6R3_FIX_GRADE_SELFTEST.log`, run before this
  freeze. **A reader that cannot say `PERSISTS` on `P0` may not be believed when it says
  `VANISHED` on `FIX_NONGAMG1` (rule 3).**
- Staging instrument, fixed at this commit: `d6r3_fix_stage_fvsolution.py`; its self-test with
  three planted refusals is `D6R3_FIX_STAGE_SELFTEST.log`, run before this freeze.
- Launcher, fixed at this commit: `d6r3_fix_arm.sh`. Its `G-PREREG` guard hashes this file, the
  stager, the grader and itself against the committed `HEAD` blobs and **refuses to launch** if
  any on-disk copy is not the committed one — the frozen file is verified to *be* the file that
  ran (rule 2).

## 0. WHAT IS NOT TOUCHED — the one move this family may never make

`primalMinResTol` stays **1.0e-8**. `primalMinResTolDiff` stays **100**. `endTime` stays **2000**.
`deltaT`, `fvSchemes`, `relaxationFactors`, the mesh, the decomposition, `0.orig`, the three
condition dirs and the `forces` observer block are all **unchanged from arm `P0`**. **No
convergence criterion is loosened in either arm.** The direction of both changes is the opposite
one: make the pressure linear solve *more* converged, or remove the state that makes it
order-dependent. A staged `relTol` that is not strictly tighter than the published `0.1` is
**refused** by the staging instrument (`d6r3_fix_stage_fvsolution.py`, DIRECTION ASSERT).

## 1. The measured basis — established by `DIAG_ORDER1` and `DIAG_AGGLOM1`, not re-opened here

The defect is **ordinal**: in one multipoint job the **second** scenario instance builds a
different GAMG coarse-grid hierarchy from the first on a **bit-identical fine mesh** (GAMG level-0
row identical in every printed column: `20681/20887` cells, `2.882/2.896` faces per cell,
`9/14` interfaces, profile `8.579e+06`), and every one of levels 1–10 differs. Consequence chain,
every link measured: identical staged files → byte-identical resolved `DAOption` dumps →
identical fine mesh → step-1 `U0 U1 U2 he` identical to 16 digits → **`p initRes` identical to 16
digits** (same matrix, same RHS) → different hierarchy → **24 vs 21 V-cycles at the published
`relTol 0.1`** → a differently partially-converged `p` → the whole SIMPLE trajectory diverges.

The two facts that decide this fix:

1. **It is a residual-FLOOR defect, not a wrong answer.** `CD` agrees to 5–6 figures across
   positions — `0.02090109066417552` (position 1, `cl04`) against `0.02090262569125358`
   (position 2, `cl05`). The physics is right; DAFoam's convergence *test* is what fails.
2. **The floor is set by the pressure solve's partial convergence at `relTol 0.1`.**

Failure arithmetic, from the resolved dumps in `P0_20260913T190426Z.log` (`primalMinResTol
1e-08` at :1018, `primalMinResTolDiff 100` at :1189) and the `Time = 2000` blocks:

| | position 1 (`cl04`) | position 2 (`cl05`) |
|---|---|---|
| `p initRes` at t=2000 | `5.678212567273067e-08` | `1.757696578179007e-06` |
| max residual at t=2000 | `nuTilda 1.194718885139746e-07` | `p 1.757696578179007e-06` |
| multiple of `primalMinResTol` | **11.947×** | **175.770×** |
| test `maxRes > 100 × 1e-8 = 1.0e-06` | passes | **FAILS** → `Primal solution failed!` |

## 2. The V-cycle model, validated at four independent measured points

Model: at a given step the GAMG solve contracts the residual by a constant factor `f` per V-cycle,
so `nIters(relTol) = ln(relTol)/ln(f)`, rounded up. `f` is measured per step as
`(finalRes/initRes)^(1/nIters)` from the printed lines.

| measured point | `f` | `ln(0.1)/ln(f)` | rounded up | **printed `nIters`** |
|---|---|---|---|---|
| inst 1, step 1 | `0.907533700193993` | 23.7320 | 24 | **24** |
| inst 2, step 1 | `0.8949737232844844` | 20.7513 | 21 | **21** |
| inst 1, floor (t=2000) | `0.3131825530200823` | 1.9833 | 2 | **2** |
| inst 2, floor (t=2000) | `0.7096512428294509` | 6.7134 | 7 | **7** |

**Four for four, to the exact printed integer.** The model is therefore used, not assumed.

Its first consequence is the cost law: since `nIters(r)/nIters(0.1) = ln(r)/ln(0.1)` with `f`
cancelling, **tightening `relTol` multiplies every `p` solve's V-cycle count by the same factor at
every step, whatever that step's convergence rate.**

## 3. THE `relTol` VALUE, AND THE ARITHMETIC THAT CHOSE IT

Three measured inputs, one stated model, one stated safety factor that is itself a measurement.

**(a) The reduction the gate demands.** Position 2 must reach the residual level position 1 has
already demonstrated to be safe:

    R = maxRes(pos 2) / maxRes(pos 1)
      = 1.757696578179007e-06 / 1.194718885139746e-07
      = 14.712219

**(b) The response model.** The floor is where the outer SIMPLE map stops contracting because of
what the linear solve leaves behind; to first order the stagnation level is proportional to the
fraction left behind, i.e. **floor ∝ relTol**. This is a *model*, and §5 writes out what
falsifies it. Under it alone, `r ≤ 0.1 / 14.712219 = 6.7969e-03`.

**(c) The safety factor, measured not invented.** The response is carried by the very solver whose
contraction is the weaker of the two. Instance 2's hierarchy needs

    S = ln(0.3131825530200823) / ln(0.7096512428294509) = 3.384931

times as many V-cycles as instance 1's for the same residual reduction at the floor. The demand in
(a) is computed against instance 1's demonstrated level, so it is discounted by exactly that
measured penalty.

**(d) The value.**

    relTol = 0.1 / (R × S) = 0.1 / (14.712219 × 3.384931) = 2.008039e-03

**STAGED VALUE: `relTol 2.008e-03`** — the computed `2.008039e-03` truncated to four significant
figures, which is very slightly *tighter* than computed, never looser.

**(e) A second, independent model agrees.** At position 2's floor the outer iteration re-amplifies
what the solve leaves by `A = 1.757696578179007e-06 / 1.593157385282847e-07 = 11.0327868069792`
per step. At the published `relTol`, `A × 0.1 = 1.103` — the outer map is at or past **neutral
stability**, which is why it parks instead of converging. At the staged value `A × r = 0.02215`,
a strictly contracting map whose stagnation level is within **2.3 %** of its asymptote (against
`8.1 %` at `6.797e-03`, and divergent at `0.1`). The two models are built on different measured
quantities and both say `2.008e-03` is sufficient with margin.

**(f) What it costs.** V-cycle multiplier `= ln(2.008e-03)/ln(0.1) = 2.697228`, uniform.

## 4. PREDICTIONS — frozen before either run, in digits

### 4.1 Instrument controls (checked FIRST; each can void its arm to `NOT A RESULT`)

**A correction to the brief, stated plainly rather than obeyed.** The control that served the two
diagnostic arms — *instance 1 must reproduce `P00` bit-for-bit at step 1* — **cannot hold for
either arm here and is retired for these arms by necessity**: both arms change the `p` linear
solve, so instance 1's step-1 `p finalRes` and `nIters` **must** move, and an arm that reproduced
them would be an arm whose change never reached the solver. It is replaced by the strictly
checkable invariant it implies, which is stronger because it also reads the change back:

- **IC-1 — upstream invariance.** At `Time = 1`, for **every** instance, these must be
  bit-identical to `P00_20260913T192711Z.log`'s step-1 block, because nothing upstream of the `p`
  linear solve has seen either change at step 1:
  `U0 initRes: 0.9999999999999968 finalRes: 0.0944846591692384 nIters: 2`
  `U1 initRes: 1 finalRes: 0.01212907860710623 nIters: 2`
  `U2 initRes: 1 finalRes: 0.09448777862426254 nIters: 2`
  `he initRes: 0.999999999993853 finalRes: 0.08587891623171072 nIters: 2`
  and `p initRes: 0.9999999999942178`. Any movement in those digits means the change reached
  something it must not have reached → **`NOT A RESULT`**.
- **IC-2 — the change is read back (planted-control discipline, rule 3).** The plant is the staged
  `fvSolution` line; the read-back is the printed `nIters`. `FIX_RELTOL1` must print step-1 `p
  nIters` **strictly greater than 24** (inst 1) and **strictly greater than 21** (inst 2), and
  step-1 `p finalRes` **strictly smaller** than `0.09743304254827717` / `0.09727830036032596`.
  If the reader prints `24` and `21` the plant was invisible, the staged file never reached the
  solver, and the arm is **`NOT A RESULT`** — not a `GATE FAIL`. If `finalRes` went **up**, the
  change went the wrong way → **`NOT A RESULT`**.
- **IC-3 — physics unchanged.** Converged `CD` at `cl04` must agree with `0.02090109066417552` to
  at least 4 significant figures. A fix that moves the answer is not a fix → **`NOT A RESULT`**.
- **IC-4 — completion.** `rc = 0` and the last printed `Time` is `2000` for every instance that
  starts. A crossing of the cost bound is REPORTED and the arm graded `NOT A RESULT` (directive
  #17: no run is stopped by a cap).

### 4.2 `FIX_RELTOL1` — the producer arm (deviation **D2**)

One staged change from arm `P0`: in `system/fvSolution`, block `"(p|p_rgh|G)"`,
`relTol 0.1;` → `relTol 2.008e-03;`. **Reason:** the measured floor is set by that solve's partial
convergence; tightening it lowers the achievable floor for *both* positions. Inert consequence,
disclosed: the `Phi` block expands `$p` and so inherits the tightened value before overriding
`relTol 0;` — and `Phi` is never solved (`potentialFlow` is absent from `daOptions`; zero `Phi`
solver lines in 2.6 MB of `P0` log across three instances, from a reader that prints 126 `p`
solver lines).

Predicted step-1 `p`, from §2's validated model:

| | predicted `nIters` | predicted `finalRes` | published |
|---|---|---|---|
| inst 1 | **65** (64.011 → ⌈⌉) | ≈ `1.824e-03`, and `< 2.008039e-03` | 24 / `0.09743304254827717` |
| inst 2 | **56** (55.971 → ⌈⌉) | ≈ `2.002e-03`, and `< 2.008039e-03` | 21 / `0.09727830036032596` |

Predicted floors at `Time = 2000`, in digits:

- **Position 2 (`cl05`) `p initRes` ≤ `1.0e-07`**, central estimate `3.53e-08`
  (`1.757696578179007e-06 × 2.008e-03/0.1`), i.e. **≤ 10× `primalMinResTol`**, against `175.770×`
  measured.
- **Position 2 max residual over all fields < `1.0e-06`** — the gate. (Its next-highest field at
  t=2000 today is `U1 5.914538099672111e-07`; that elevation is itself downstream of the
  under-converged `p` and is predicted to fall with it. If it does **not**, §5 says what that
  means.)
- **Position 1 (`cl04`) max residual in `[1.0e-08, 3.0e-07]`**, still `nuTilda`-limited near
  `1.194718885139746e-07`. Tightening `p`'s `relTol` does not touch `nuTilda`'s `smoothSolver`,
  so position 1 is not predicted to improve much — it does not need to.
- **Position 3 (`cl06`), which has never run, max residual < `1.0e-06`.**

**VERDICT RULE.** `PASS` iff IC-1..IC-4 hold **and** `run_model` completes all three points with
`rc = 0` and no `Primal solution failed!` **and** every instance's max residual at `Time = 2000`
is `< 1.0e-06`. Otherwise `GATE FAIL` (the fix did not work) or `NOT A RESULT` (an instrument
control failed). **If `PASS`, multipoint `P0` relaunches on this `fvSolution` and nothing else
changes.**

### 4.3 `FIX_NONGAMG1` — the mechanism control (deviation **D3**)

One staged change from arm `P0`: in the same block, `solver GAMG;` → `solver PBiCGStab;` and
`smoother GaussSeidel;` → `preconditioner diagonal;`. **`relTol` stays at the published `0.1`** —
this arm changes the solver and nothing else, so that a difference is attributable. **Reason:**
`PBiCGStab` with a `diagonal` preconditioner carries **no process-static agglomeration state**;
`diagonal` is chosen over `DIC`/`DILU` because it is valid for a symmetric *and* an asymmetric
matrix, and this `p` matrix's symmetry under `DARhoSimpleCFoam` is not established here — an
unsuitable pairing would abort instance 1 and waste the arm, and that risk is disclosed rather
than run into.

The hypothesis under test is the one `DIAG_AGGLOM1` named but could not adopt:
`pairGAMGAgglomeration.H:63`'s `static bool forward_` — one value per **process**, shared by every
mesh, flipped at every level (`pairGAMGAgglomerate.C:333`).

- **H-REMOVE (mechanism confirmed by removal).** With no agglomeration in the process, instance 1
  and instance 2 print step-1 `p finalRes` and `nIters` **identical to all 16 printed digits**,
  and the ordinal signature vanishes. Reading: process-static agglomeration state is the carrier.
- **H-REMOVE-DEAD.** The two instances still differ at step 1. Reading: **the agglomeration
  attribution is wrong**, the carrier is some other process-level state, and this lane will say so
  loudly and withdraw `forward_` as the named hypothesis.
- Outcome vocabulary for this arm: `GATE REACHED` (H-REMOVE or H-REMOVE-DEAD decided) or
  `NOT A RESULT` (an instrument control fails, or the solver pairing aborts). This arm produces
  **no verdict about D6R3 physics** and is not the fix; it is the isolating measurement
  `DIAG_AGGLOM1` could not make.
- Secondary, recorded but not gating: whether the job then completes all three points.
- If `nIters` reaches `1000` (OpenFOAM's default `maxIter`) the solve stopped on the iteration cap
  rather than on `relTol`; the ordinality comparison is still valid, the cost figure is not.

## 5. WHAT FALSIFIES THE DIAGNOSIS — written down before the runs

- **`FIX_RELTOL1` is `GATE FAIL`** (position 2 still floors ≥ `1.0e-06` with IC-1/IC-2 passing):
  the floor is **not** set by the pressure linear solve's tolerance, §3(b)'s linear response is
  wrong, and the final link of the `DIAG_AGGLOM1` chain — *different hierarchy → differently
  partially-converged `p` → elevated floor* — does not carry. That is a loud correction and will
  be reported as one, not buried.
- **Position 2's `p` falls but `U1` does not** (max residual stays ≥ `1.0e-06` on a momentum
  field): the momentum floors are **not** downstream of the pressure floor, and a second,
  independent floor mechanism exists that this diagnosis never saw.
- **`FIX_NONGAMG1` is H-REMOVE-DEAD**: `forward_` and process-static agglomeration state are
  **not** the carrier, and the `DIAG_AGGLOM1` addendum's named-not-adopted hypothesis is retired.
- **IC-2 fails with `nIters` unchanged at 24/21**: the staged `fvSolution` never reached the
  solver, and every number in that arm is about a run that did not carry the change.

## 6. COST — costed here, before launch (rule 12)

Measured anchors, from `ledger.txt`: `P0` (2 instances, aborted) `637 s` / **`297.267 core-min`**
at 28 ranks; `DIAG_AGGLOM1` (2 instances) `558 s` / **`260.400 core-min`**; `P00` (1 instance, no
`forces` block) `333 s` / **`155.400 core-min`**. Per-instance solve ≈ `255 s`, setup ≈ `120 s`.

- **`FIX_RELTOL1`**: 3 instances (all predicted to complete) at a `2.697×` `p`-V-cycle multiplier.
  With `p` taken as ≈ 60 % of step cost: `120 + 3 × 255 × (1 + 1.697 × 0.6) ≈ 1665 s` →
  **predicted 780 core-min**; upper bound at `p` = 100 % of step cost, `120 + 3 × 688 = 2184 s` →
  **1050 core-min**.
- **`FIX_NONGAMG1`**: iteration count for `PBiCGStab`+`diagonal` on this matrix is **not
  predictable from anything measured here** and is stated as such. **Predicted 600 core-min**,
  upper bound **1500 core-min** (3 instances at 3× the baseline solve).
- **Total predicted 1380 core-min**, upper bound **2550 core-min**. Derived dollars at the
  owner-stated `c7a.4xlarge $0.0513/core-h`: **$1.18 predicted, $2.18 upper bound — derived, not
  measured** (the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5).
- **Directive #17: no run is stopped by a time or budget cap.** A crossing is REPORTED and the arm
  graded `NOT A RESULT`.
- **Cores.** `min(free, 96 − 48 − 20) = 28` ranks, per-core idle measured over a 5 s window at
  launch (cores ≥ 85 % idle only, because `G-CORES` on loadavg cannot tell an allocated core from
  a busy one — a named gap already on this lab's record). The reserved 48-core propeller lane and
  20-core DrivAer lane are **not** overlapped; honoured by hand. The two arms run **sequentially**
  — 2 × 28 + 48 + 20 = 124 > 96 — `FIX_RELTOL1` first, because it is the one the owner is
  waiting on.
- Estimate-vs-actual rows owed to `docs/COST_CALIBRATION.md` at completion of each arm (rule 12).

## 7. WHAT IS NOT FILED

Process-static agglomeration state making multi-mesh results order-dependent is upstream
**OpenFOAM v2506** behaviour, not our wrapper — but our multipoint construction is what made the
process plural. It is recorded as a finding note and **`NOT FILED`**. **SUBMISSIONS ARE PARKED
(rule 7); filing is Sanaa's decision alone and is taken by her.** No agent's message is her
consent. The four upstream classes stay `NOT FILED`.

---

## ADDENDUM 1 — 2026-09-13 — RESULT, ARM `FIX_RELTOL1`. **THE FIX DOES NOT WORK, AND IT IS WORSE THAN THE BASELINE.**
## No gate, threshold, cap or label above is altered by this addendum. Originals stand as written.

Log `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/FIX_RELTOL1_20260913T202543Z.log`.
Freeze sha `ff271fd0205b11aa60119f2f1c6e732b16456689`; `G-PREREG` verified this file, the stager, the
grader and the launcher against their committed `HEAD` blobs before the container started.
Ledger row `D6R3_FIX_ROW arm=FIX_RELTOL1 rc=1 wall_s=720 ranks=28 core_min=336.000`.

### 1. VERDICT, from the grading path frozen at the pre-registration commit: **`NOT A RESULT`**

`d6r3_fix_grade.py` passed 7 of 9 checks and failed two: **IC-3** (`CD(cl04)` printed
`0.02090512806637335` against the registered `0.02090109066417552` — they differ in the fourth
significant figure) and **IC-4** (`rc = 1`).

**IC-4 IS DEFECTIVE AS REGISTERED, AND THE DEFECT IS THIS LANE'S.** `rc = 0` cannot serve as an
instrument control in an arm whose *predicted failure mode* is a non-zero `rc`: DAFoam raises
`AnalysisError("Primal solution failed!")` exactly when the gate is missed, so IC-4 converts every
`GATE FAIL` into a `NOT A RESULT` and makes the `GATE FAIL` branch of §4.2 unreachable. IC-3 has the
same shape of flaw: it compares a converged `CD` against the `CD` of a primal that **did not
converge**, where no agreement is owed. **Both are disclosed, neither is repaired here**: a gate is
closed at first compute (rule 2), the verdict stands as the frozen path returned it, and a
re-grading of this arm to a friendlier label after seeing the answer is precisely the move the
freeze exists to prevent.

### 2. WHAT WAS MEASURED — and it is decisive whatever the label

The instrument controls that were sound all passed, so the numbers below are about the arm that
was registered:

- **IC-1 held bit-for-bit.** At `Time = 1`, instance 1 printed `U0 initRes: 0.9999999999999968
  finalRes: 0.0944846591692384 nIters: 2`, `U1 initRes: 1 finalRes: 0.01212907860710623 nIters: 2`,
  `U2 initRes: 1 finalRes: 0.09448777862426254 nIters: 2`, `he initRes: 0.999999999993853 finalRes:
  0.08587891623171072 nIters: 2` and `p initRes: 0.9999999999942178` — every digit the registration
  demanded. Nothing upstream of the `p` solve moved.
- **IC-2 held: the change reached the solver and was read back.** Step-1 `p finalRes
  0.001998751422359818` (registered: `< 2.008039e-03`) at `nIters 320` (registered: `> 24`).

**The gate, measured.** Instance 1 (`cl04`, position 1) at `Time = 2000`:

| field | `initRes` | multiple of `primalMinResTol` |
|---|---|---|
| U0 | `2.929055550529289e-07` | 29.3× |
| U1 | `2.584843663213218e-06` | 258.5× |
| U2 | `1.138165293022058e-06` | 113.8× |
| he | `1.197023710292814e-06` | 119.7× |
| **p** | **`7.600678874731434e-06`** | **760.07×** |
| nuTilda | `2.001527779331585e-07` | 20.0× |

`Primal solution failed!` was raised at **`cl04`** — **position 1, the position that PASSED at the
published `relTol`**. The job aborted there, so **position 2 and position 3 never ran** and this arm
produces **no** position-2 floor.

**THE RESPONSE IS INVERTED, NOT MERELY NON-LINEAR.** Against the baseline `P0`/`P00` position-1
floor (`p 5.678212567273067e-08`, max `nuTilda 1.194718885139746e-07` = 11.95×):

- `p` floor **raised by 133.86×** (`7.600678874731434e-06 / 5.678212567273067e-08`);
- max residual **raised by 63.62×** (`7.600678874731434e-06 / 1.194718885139746e-07`), carrying
  position 1 from **11.95×** to **760.07×**, across the `100×` threshold.

The registered prediction was position-2 `p ≤ 1.0e-07` with position 1 staying in
`[1.0e-08, 3.0e-07]`. Position 1 came in at `7.6e-06` — **25× above the top of its own predicted
band**, in the wrong direction.

**It is a parked state, not a slow decay.** From `Time = 800` to `Time = 2000` instance 1's `p
initRes` ranges over `7.010002e-06` to `7.600679e-06` — an **8.43 % spread across 1200 steps** —
while `nIters` sits at 39–44. The outer loop is sitting on a level, not approaching one.

### 3. §5's FIRST FALSIFIER IS TRIGGERED — said loudly, as registered

§5 wrote: *"`FIX_RELTOL1` is `GATE FAIL` (position 2 still floors ≥ 1.0e-06 with IC-1/IC-2 passing):
the floor is not set by the pressure linear solve's tolerance, §3(b)'s linear response is wrong."*
**The measurement is stronger than the falsifier anticipated.** The floor *is* controlled by the
pressure linear solve's tolerance — tightening it moved the floor by two orders of magnitude — but
**the sign is opposite to §3(b)'s model**. `floor ∝ relTol` is **WRONG**, and so is the reading it
carried, that a tighter linear solve lowers the floor for both positions. The `DIAG_AGGLOM1` chain
stands up to and including *different hierarchy → different V-cycle count → differently
partially-converged `p` → different SIMPLE trajectory*; its **final link — that the elevated floor
follows from the `p` solve being under-converged — does not carry.** Under-convergence of `p` is not
what raises the floor; at this `relTol` *over*-convergence raises it far more.

**A HYPOTHESIS, NAMED AND NOT ADOPTED.** `system/fvSolution` sets `relaxationFactors { fields {
"(p|rho)" 1.0 } equations { p 1.0 } }` — **no under-relaxation on pressure anywhere**. A SIMPLE
loop run with unrelaxed pressure takes part of its damping from the pressure equation *not* being
solved exactly; the published `relTol 0.1` supplies that damping, and removing it can leave the
outer map parked at a higher level. That is consistent with everything above — an inverted response,
a flat parked state, an unchanged `CD` to ~4 figures — but **no experiment in this arm isolates it**,
and it must not be relayed as a finding. The experiment that would isolate it is an arm that varies
`relaxationFactors` `p` at the published `relTol`, and it is not registered here.

### 4. THE COST MODEL OF §2 IS FALSIFIED, AND ITS "FOUR FOR FOUR" VALIDATION WAS CIRCULAR

Registered: step-1 `nIters` **65** for instance 1. Measured: **320** — wrong by **4.92×**. The
registered V-cycle multiplier `ln(r)/ln(0.1) = 2.697` is wrong; the measured step-1 multiplier is
`320/24 = 13.33×`.

**The cause is a methodological error, not bad luck.** §2 fitted `f = (finalRes/initRes)^(1/n)` from
runs at `relTol 0.1` and then "validated" `nIters(0.1) = ln(0.1)/ln(f)`. Substituting the fit back:

    ln(0.1)/ln(f) = n · ln(0.1) / ln(finalRes/initRes)

and at `relTol 0.1` the solver stops as soon as `finalRes/initRes ≲ 0.1`, so that ratio is ≈ 1 and
the expression returns `n` **by algebra**. The four agreements — 24, 21, 2, 7, each to the exact
printed integer — were an **identity, not a test**, and they carried no information about
extrapolating to a different `relTol`. The true asymptotic contraction measured over the 320 cycles
actually run is **`0.980765` per V-cycle**, against the `0.907534` the first 24 cycles implied:
GAMG's rate degrades as the easy modes are removed, which a constant-`f` model cannot see.

**A model fitted at one operating point and checked only at that same point is not validated for
any other point, however many digits agree.** That is the lesson of this arm and it is offered for
`docs/LESSONS.md` at the supervisor's discretion; it is not filed here.

### 5. COST — estimate versus actual (rule 12)

- Registered: **780 core-min** predicted, **1050 core-min** upper bound, for **3** instances.
- Actual: **336.000 core-min** = `720 wall s × 28 ranks / 60` [`ledger.txt`, `D6R3_FIX_ROW
  arm=FIX_RELTOL1 rc=1 wall_s=720 ranks=28 core_min=336.000`]. = 5.600 core-h →
  **$0.2873 DERIVED, NOT MEASURED** (c7a.4xlarge $0.0513/core-h, owner-stated; the box cannot read
  its own billing, `COMPUTE_BUDGET_CHARTER.md` §5). **= gross**; 720 s, nowhere near the 3600-s
  stall rule.
- **Ratio 0.431× — and it is NOT a calibration.** Only **1** of the 3 registered instances ran; the
  arm aborted at `cl04`. The comparable figure is per-instance: registered ≈ **247 core-min** per
  instance against **299.3 core-min** measured (`641.36 s ExecutionTime × 28 / 60`) — **1.21×** over,
  and *that* is the honest number. The registered total came in low only because the arm died early.
- **No waste**: the abort at `cl04` is the measurement, not a loss. The 336 core-min bought the
  falsification of §3(b) and of §2's cost law, which is what the arm was for.
- Cores: 28 ranks on cpuset `1,2,3,5,6,7,8,9,11,13,14,16,18,19,20,21,23,24,25,27,28,29,31,32,33,34,
  35,36`, chosen from 67 cores measured ≥ 85 % idle over a 5 s window at launch. No overlap with the
  reserved 48-core propeller lane or the 20-core DrivAer lane. No cap stopped anything (directive #17).

### 6. WHAT THIS ARM DOES NOT ESTABLISH

- **Nothing about position 2 or position 3 at this `relTol`** — they never ran.
- **Nothing about whether a `relTol` between `0.1` and `2.008e-03` behaves differently.** The
  response is now known to be non-monotone somewhere in that interval; where, is unmeasured.
- **Nothing about the carrier of the hierarchy difference.** That is `FIX_NONGAMG1`'s question.
