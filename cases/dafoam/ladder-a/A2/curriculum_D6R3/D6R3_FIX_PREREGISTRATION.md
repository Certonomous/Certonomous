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
