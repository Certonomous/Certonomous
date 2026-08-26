# T8 — THE STEADINESS MEASUREMENT, AND **IT CONTRADICTS THE DRAFT AND PART OF THE RULING THAT ORDERED IT**

**Written by a `lab-lane` under `heat-transfer-supervisor`, 2026-08-26.**
**ZERO COMPUTE — no solver was launched; every number here is parsed from a log
that already existed.** **Nothing here grades anything.** No verdict, no band, no
triple, no value that any verdict may rest on. **Nothing has been sent, filed,
submitted, uploaded, registered or posted outside this box (`CLAUDE.md` rule 7).**

---

## 0. THE HEADLINE, FIRST, BECAUSE IT REVERSES A PREMISE

`T8_REREGISTRATION_DRAFT_2026-08-25.md` §4a and §4b were written while level `f`
was **still running**, at iteration 2134 and then 2717. On that partial record
they concluded that `f` *"touched the registered criterion exactly once, for 228
iterations, and never again"*, that it was *"OSCILLATING over more than two
decades"*, and — §4d — that a second excursion forming at iteration 2600 was
**evidence the case is not steady.**

**`f` has since completed to `endTime`, and on the completed log those readings
do not survive.**

| | draft, at iteration 2717 | measured, at completion (iteration 20000) |
|---|---|---|
| iterations at or below the registered `1e-6` | **228**, described as the only stretch anywhere in the run | **15,742 of 20,000** |
| contiguous stretches below `1e-6` | 1 | **2** — iterations 877–1104 (228 long) **and iterations 4487–20000 (15,514 long)** |
| state at the last iteration | rising into a second excursion | `T` initial residual **`5.932102e-07`**, below the criterion |
| termination | still running | `rc = 0`, `End` line, last `Time = 20000` == `endTime`, `ExecutionTime = 13065.88 s` |

**`f` left the second excursion, came back below `1e-6` at iteration 4487, and
stayed there for the last 77.6 % of the run.** The excursion §4d treated as
evidence of unsteadiness **resolved.**

> **This is the same failure the draft itself warns about, arriving a fifth
> time: a reading taken of a quantity that was still moving, reported as a
> property of the run. §9's rule — "look at the bytes before believing the
> number" — has a companion: LOOK AT THE WHOLE RUN BEFORE BELIEVING A
> CHARACTERISATION OF IT. A point sample of a live series and a point sample of
> an oscillating one are the same error.**

The draft's §4b **counter-example claim** — that `f` demonstrates a run meeting
the convergence criterion while not plateaued — **is withdrawn as stated.** Its
structural point (that "converged" and "plateaued" are different properties) may
still be true; **`f` is no longer the demonstration of it**, and §4b's numbers
must not be cited as though they were measured at completion. They were not.

---

## 1. §2d DISCLOSURE — instrumentation added after first compute

`VERIFICATION_CHARTER.md` §2d permits instrumentation **not on the grading path**
to be added after first compute, and requires *"a dated disclosure naming what
was added, when, what was readable at that moment, and which findings rest on it
and which do not."*

- **What was added:** `verification/runs/T-family/T8_runs/stationarity_probe_t8.py`.
- **When:** 2026-08-26, after all three T8 levels had finished.
- **What was readable at that moment:** everything. `c`, `m` and `f` had all
  terminated; every log and `STATUS` file was complete. **A diagnostic written
  with the answers visible is exactly the condition under which a diagnostic gets
  chosen because it will say something**, and that is why the probe's window
  length, window count, span and criterion are **written into its source before
  it was first run** and are not tuned. They are the parameters supervisor ruling
  A2 registered, not parameters this lane selected after looking.
- **What rests on it:** §2 and §3 below, and nothing else. It is not in the §11
  freeze set of `T8_PREREGISTRATION.md`, it emits no verdict, and it can supply
  no graded value.
- **RULING C's line, which this file stays on the right side of:** these runs
  *"may tell us what to REGISTER. They may never tell us what the ANSWER is."*

**T8 remains dead on both independent grounds and nothing here revives it.** The
§12 S3 extrapolation precondition `r₂ = 3·r₁` is false on the built mesh
(`r₂/r₁ = 2.333313`) so `resolve_planes` refuses; and `m` crashed at `rc = 136`
(SIGFPE, core dumped) having written no time directory. **`f` finishing well is
not a T8 result and must not be mined for one.**

---

## 2. THE MEASUREMENT

**Series:** the `T` initial residual, one value per outer iteration, matched as a
whole token (`Initial residual = ([0-9eE.+-]+)`) so no exponent is truncated.
**Span:** the second half of each run — the first half carries the documented
start transient, and a stationarity test run across a transient tests the
transient. **K = 4** disjoint equal windows (ruling A2). **Criterion** (§4c part
1, as ruled): the window **mean** must not trend across **consecutive** windows
by more than the **within-window spread** (sample standard deviation).
**`σ_self`** (ruling A2): the **maximum pairwise** window-to-window mean
difference across the K windows.

### Level `c` — `T8_MTT_c/log.solve`, 8,000 iterations

| window | iterations | mean | within-window sd |
|---|---|---|---|
| 1 | 4001–5000 | `6.786787e-04` | `3.587709e-05` |
| 2 | 5001–6000 | `6.813397e-04` | `3.224433e-05` |
| 3 | 6001–7000 | `6.912450e-04` | `3.499028e-05` |
| 4 | 7001–8000 | `7.006527e-04` | `3.660030e-05` |

Consecutive drifts `2.661e-06`, `9.905e-06`, `9.408e-06` — **all inside their
own window's spread.** **Stationarity precondition: HOLDS.**
**`0` iterations at or below `1e-6` anywhere in the run.** Last value
`7.322808e-04`.

**RULING B is confirmed independently on the completed log.** `c` is a plateau
around `6.8–7.0e-04`, not a descent. It did not stall for lack of iterations and
a longer run is refuted, not merely unpromising.

### Level `f` — `T8_MTT_f/log.solve`, 20,000 iterations

| window | iterations | mean | within-window sd |
|---|---|---|---|
| 1 | 10001–12500 | `6.262246e-07` | `6.702031e-09` |
| 2 | 12501–15000 | `6.052407e-07` | `5.121496e-09` |
| 3 | 15001–17500 | `5.923404e-07` | `2.267551e-09` |
| 4 | 17501–20000 | `5.905037e-07` | `1.154926e-09` |

Consecutive drifts `2.098e-08` (**exceeds** sd `6.702e-09`), `1.290e-08`
(**exceeds** sd `5.121e-09`), `1.837e-09` (within sd `2.268e-09`).
**Stationarity precondition: FAILS.**

---

## 3. THE CONTRADICTION, AND IT IS AGAINST RULING A3 AS WRITTEN

**Ruling A3 says:** *"If level `f` fails stationarity, the finding is NOT merely
'the ramp test cannot be run'. It is that T8's REGISTERED STEADY FORMULATION IS
UNDER CHALLENGE."*

**`f` fails stationarity. The inference does not follow, and the measurement
shows why.**

### 3.1 The failure is in the direction of CONVERGENCE, not of unsteadiness

`f`'s four window means are `6.262e-07 → 6.052e-07 → 5.923e-07 → 5.905e-07` —
**monotone decreasing**, with increments `2.10e-08 → 1.29e-08 → 1.84e-09`,
**shrinking by an order of magnitude across the span**, and the within-window
spread collapsing with them (`6.70e-09 → 1.15e-09`). **That is the signature of a
slow monotone approach to a floor.** The criterion as ruled is **non-directional**
— it asks whether the mean *trends*, not whether it *grows* — so it refuses a
decaying run exactly as it refuses a wandering one, and **prints the same word for
both.**

**A test that cannot distinguish "still settling" from "will never settle" cannot
carry a case-selection finding**, because those two states call for opposite
decisions: one wants more iterations, the other wants a different formulation.

### 3.2 The sharper defect: the criterion divides a trend by a spread, and on a smooth series the spread goes to zero

`f`'s within-window sd in the final window is `1.155e-09` — **three orders of
magnitude below the mean.** The series is not noisy; it is smooth. A criterion of
the form `|Δmean| ≤ within-window spread` therefore becomes **arbitrarily
sensitive as a run gets smoother**: in the limit of a perfectly smooth monotone
approach the spread tends to zero while the trend does not, and **the test refuses
every such run, however well converged.**

> **§4c PART 1 AS RULED FAILS THE BEST-BEHAVED RUNS HARDEST. THE SMOOTHER AND
> MORE CONVERGENT A SERIES IS, THE MORE CERTAINLY IT IS REFUSED.**

### 3.3 The demonstration that settles it: the criterion PASSES the stall and REFUSES the convergence

| level | reached `1e-6`? | last value | §4c part 1 |
|---|---|---|---|
| **`c`** — stalled at a plateau, **never once below `1e-6`** in 8,000 iterations | **no, 0 iterations** | `7.323e-04` | **HOLDS** |
| **`f`** — below `1e-6` for **15,514 consecutive** iterations to `endTime` | **yes** | `5.932e-07` | **FAILS** |

**The level that never converged passes the precondition. The level that
converged and stayed fails it.** A criterion whose two verdicts are assigned to
those two runs *in that order* is not measuring convergence, and no case-selection
finding may be built on it.

### 3.4 The lab's own registered shape already avoids this, and §4c part 1 re-introduced the bug it avoids

`analyse_e4a2.py:299-300` — the shape §4b.3 **already adopted** for this
territory — reads: *"C1 sustained floor AND C2 **not growing** AND C3
graded-quantity stationarity"*, implemented at `analyse_e4a2.py:308` as
`c2 = not cl["growing"]`. **"Not growing" is DIRECTIONAL. "Not trending" is
not.** `analyse_k0cx.py:644` takes the other admissible route — peak-to-peak
amplitude over a registered window with a registered minimum sample count —
and likewise never divides a trend by a spread.

**§4b.3 ruled that the territory adopts an existing registered shape rather than
invent one. §4c part 1, written the same day, invented one, and the invented one
has a defect neither registered shape has.** Recorded here rather than patched:
**the repair is a registration decision and this lane makes none.**

### 3.5 What §4d's question can and cannot be answered with

**The probe is admissible as evidence AGAINST steadiness and is NOT admissible as
evidence FOR it**, and that asymmetry is stated in the probe's own source. The
reason: §4c part 1 applies to the **graded quantities**, and `f` wrote only
checkpoints `18000` and `20000` — **two samples**, which is precisely the
two-point sample §4b.1 identifies as the defect. The residual is the only densely
sampled series the run possesses.

So the honest position is narrower than either the draft's or A3's:

- **The specific evidence §4d rested on is refuted.** "Oscillating over more than
  two decades and never settling, with a second excursion forming at 2600" is not
  what the completed run did.
- **`f` is NOT thereby shown steady.** A monotone decaying residual is consistent
  with a steady state and does not establish one, and the graded quantities remain
  a two-point sample.
- **The case-selection question is therefore still open, and it is open on
  weaker grounds than A3 assumed.** It is the supervisor's to rule
  (`CASE_SELECTION_CHARTER`), and this lane states no view on whether the plume
  is physically unsteady.

---

## 4. RULING A2 IS VINDICATED BY A MEASURED FACTOR, NOT BY ARGUMENT

Ruling A2 replaced the draft's two-window `σ_self` — **one sample of a
difference, with no width** — by the maximum pairwise difference across K = 4
windows. The two forms differ on this data by a factor that would change a ramp
verdict:

| level | `σ_self`, superseded two-window form (windows 1 vs 2) | `σ_self`, ruling A2 (max of 6 pairs) | ratio |
|---|---|---|---|
| `c` | `2.661025e-06` | **`2.197400e-05`** (windows 1 vs 4) | **8.26×** |
| `f` | `2.098389e-08` | **`3.572086e-08`** (windows 1 vs 4) | **1.70×** |

**On `c` the drafted null was 8.26× too narrow.** A ramp difference anywhere
between `2.7e-06` and `2.2e-05` would have been declared **FORBIDDEN — the ramp
changed the solution** under the two-window form and **NEUTRAL** under A2's, on
the same data, with no other difference. **That is a verdict flip produced by the
width of a null, which is the whole reason a null needs a width.**

---

## 5. COST — and the estimate-versus-actual for what T8 actually spent

**This measurement: 0 core-minutes.** Log parsing on the login box.

The rung's own spend, from the `STATUS.*` files it wrote (`rc`, `wall_s`,
`ranks`, `core_min`, `cap_core_min` are recorded by the runner, not by this lane):

| level | rc | wall s | ranks | core-min | cap core-min | against cap |
|---|---|---|---|---|---|---|
| `c` | 0 | 229 | 1 | **3.817** | 15 | 25 % |
| `m` | **136** (SIGFPE, core dumped) | 150 | 1 | **2.500** | 80 | 3 % |
| `f` | 0 | 13,101 | 1 | **218.350** | 500 | 44 % |
| **total** | | | | **224.667** | 595 | **38 %** |

**No cap was overrun.** `c`'s calibration datum — **3.817 core-min actual against
7.13 predicted, ratio 0.54** — is the one already named in the draft's §7 and it
is confirmed here from the `STATUS` file rather than from recall. Derived at the
recorded rate of $0.0513/core-h, the rung's total is **$0.19 — derived, not
measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**No row is added to `docs/COST_CALIBRATION.md` by this file**, because T8 is not
a completed process: it produced no graded rung, and a calibration row for a rung
that never graded would book a prediction against an outcome that does not exist.
**That is a gap and it is named rather than filled** — the supervisor may rule
that a dead rung's spend belongs in the ledger under its own label, and if so the
numbers above are the row.

---

**DIAGNOSTIC ONLY. NOT A REGISTRATION. NOTHING HERE GRADES, AND NOTHING HERE HAS
BEEN SENT.**

---

## 6. ADDENDUM, SAME DAY — **THE THREE-LEVEL PATTERN RUNS THE OTHER WAY, AND IT POINTS AWAY FROM §4d**

The heat-transfer supervisor's crash triage of 2026-08-26 (their own, non-delegable
§3 check 2) reads the three levels as *"the **coarse converges**, the medium
diverges catastrophically, and the **fine reaches endTime while oscillating over
two decades**"*, and concludes that this is *"the classic signature of a steady
solver applied to a flow that is not steady"* — numerical diffusion damping the
instability on the coarse grid, the medium grid resolving enough to destabilise
it, the fine grid oscillating.

**The crash triage of `m` is not in dispute and is not re-done here.** `rc = 136`
= 128 + 8 = SIGFPE at 150 s against `timeout_s = 4800`; the divergence originates
in the pressure-velocity coupling (`p_rgh` initial residual `0.9999999911` at
`Time = 1086`, continuity error sum local `1.84e+45`) and reaches `k` second.
**The mesh-quality and setup-difference explanations are dead**, established by
the supervisor and by §5/§8 of the re-registration draft.

**What is in dispute is the pattern, on both of its ends.** Measured on the
completed logs, one value per outer iteration, whole-token reader:

| level | cells | iterations run | min `T` initial residual | last value | iterations ≤ `1e-6` | what it actually did |
|---|---:|---:|---|---|---:|---|
| `c` | 6,400 | 8,000 / 8,000 | `5.5370e-04` | `7.3228e-04` | **0** | **never converged** — plateau ~`7e-04`, four decades above the criterion |
| `m` | 25,600 | **1,086 / 12,000** | `2.2553e-11` | `1.4662e-01` | 2 (start transient) | **diverged**, SIGFPE |
| `f` | 102,400 | 20,000 / 20,000 | `2.3333e-07` | `5.9321e-07` | **15,742** | **converged and stayed** — the last 15,514 iterations consecutively below `1e-6` |

**"The coarse converges" is not what `c` did.** `c` was **never once** below the
registered `1e-6` in 8,000 iterations; its best value in the whole run is
`5.537e-04`. The supervisor's own **RULING B** says this in the same words —
*"`c` has stalled, it is not slow… a plateau around 7e-04, not a descent"* — so
the triage prose contradicts the triage author's earlier ruling, and §2 above
confirms RULING B independently on the completed log. **`c` completed; `c` did
not converge.** `rc = 0` and an `End` line certify termination, not convergence,
and reading the first as the second is the completion rule's exact failure mode.

**"The fine oscillates" is not what `f` did either** — §0 and §3 above.

### 6.1 The direction is the argument, and reversing it reverses the conclusion

**The unsteady-physics hypothesis makes a directional prediction.** If the flow is
genuinely unsteady and the steady solver is the wrong instrument, then **numerical
diffusion is what buys stability**, so the **coarsest** grid should be the
**calmest** and agitation should **increase with resolution**. That is precisely
the reasoning the triage gives.

**The measurement is the opposite. The FINEST grid is the only one that settled.**

> **Under the unsteady-physics story the fine grid is the one that should not
> settle, and it is the only one that did. The story predicts the ordering
> backwards.**

What the data does show is **non-monotone failure in resolution** — which the
draft's §8 already recorded from the `epsilon` bounding rates (`c` 3.8 %,
`m` 38.6 %, `f` 8.4 %: *"the middle level is the only one that destroyed
itself"*). **The middle level being the outlier is not a resolution trend at all**,
and neither hypothesis in the triage explains why the failure is worst in the
middle and absent at both ends.

### 6.2 The two hypotheses, ranked, and what would discriminate them

**The supervisor is right that grid-dependence rules out a setup error and right
that two hypotheses remain live. This lane ranks them differently on this data,
and says why.**

1. **LEADING — under-resolution of the plume on `c` and `m`, with the closure
   unrealizable there.** It predicts the observed ordering: the coarse grid cannot
   resolve the plume and stalls at a large residual floor; the medium grid is in
   the worst place — fine enough to develop gradients it cannot support, coarse
   enough for `epsilon` to go unphysical (38.6 % bounding, `5.1e3 → 7.0e11 →
   1.7e43 → 4.6e64` into SIGFPE); the fine grid resolves it and converges. It is
   also consistent with `epsilon` going negative on **every** level from
   `Time = 24` while `T` never bounds anywhere — a closure failure, not a
   thermal-field failure.
2. **TRAILING — genuinely unsteady physics.** Not excluded. But it predicts
   agitation increasing with resolution, and the measured ordering is the reverse.
   It would have to explain why the finest grid is the quiet one.

**What discriminates them, and neither needs a re-registration to specify:**

- **A fourth, FINER level.** Under (1) it converges like `f`, only better; under
  (2) it should be the most agitated of all. **This is the single cleanest
  discriminator and it is a pure resolution test.** It also bears on RULING B's
  closing point — that if the ladder cannot produce three gradeable levels, the
  ladder needs re-choosing with a **finer coarse level**, which is the same move.
- **An unsteady run at one level** (`buoyantBoussinesqPimpleFoam` on `f`'s mesh):
  under (2) it develops a persistent, statistically stationary fluctuation; under
  (1) it settles to the same steady state `f` reached. **This is the direct test
  of the §4d question** and it answers it in the only currently honest way,
  because it does not depend on reading a steady solver's residual.
- **The `epsilon` bounding rate as a function of resolution**, extended to a
  fourth level. Under (1) it must fall monotonically past `m`; the existing three
  points (3.8 %, 38.6 %, 8.4 %) are already non-monotone and one more point makes
  the shape readable.

**This lane rules nothing.** `CASE_SELECTION_CHARTER` is the supervisor's and the
call is theirs. **What is recorded here is that §4d's evidence, read at
completion, points the other way, and that a successor registered on the unsteady
hypothesis would be registered against the direction of its own data.**
