# T8 re-registration — **DRAFT. NOT A REGISTRATION. NOT FROZEN. NOTHING HERE BINDS.**

**STATUS: DRAFT ONLY.** This file registers nothing, freezes nothing, gates
nothing and authorises no compute. It is the material a re-registration would
need, written so that the decision can be taken on evidence — **the decision
itself is Sanaa's and the chief's.** Re-registering a rung after first compute
is not a supervisor's call and is emphatically not a lane's.

**No rung id is claimed here.** Whoever authorises this assigns it. "T8-next"
below is a placeholder, not a name.

**Nothing in this file has been sent, filed, submitted, uploaded, registered or
posted outside this box (`CLAUDE.md` rule 7).**

---

## 1. Why the frozen T8 is dead, on two independent grounds

**Ground 1 — the extrapolation precondition is false.** §12 S3 registers the
axis extrapolation `(9f₁ − f₂)/8`, whose precondition is `r₂ = 3·r₁`.
Measured on the real, completed level-c mesh, with geometry written by
OpenFOAM: **`r₂/r₁ = 2.333313`**, against the exact wedge-centroid value
`7/3 = 2.333333`. `resolve_planes` refuses. **No T8 row can be graded.**

**Ground 2 — the ladder never had a gradeable triple anyway.** `CLAUDE.md`
rule 5 order (1) fires before any triple is classified: level `c` finished at
`endTime` with a `T` initial residual of **7.32e-04**, four decades above the
registered `1e-6`, and level `m` **crashed** and wrote no fields. Even with
correct weights, every row was **`NOT A RESULT`**.

**These are separate findings and both belong on the record.** Fixing only the
first would produce a comparator that runs and still cannot grade.

## 2. THE INSTRUMENT CHANGE — weights computed from cell centres READ FROM DISK

**The rule this encodes: do not assert what the mesh does. Measure it.**

Registering `7/3` in place of `3` would repeat the identical mistake one step
smaller — a hard-coded constant asserting a geometric fact about a mesh the
code has not looked at. **That is exactly what just failed.**

For a field quadratic in `r`, `f(r) = a + b·r²`, sampled at the two
axis-adjacent cell centres with `k = r₂/r₁`:

```
a = w1*f1 + w2*f2,    w1 = k**2/(k**2 - 1),    w2 = -1.0/(k**2 - 1)
```

**Proposed instrument:**

- read `r₁` and `r₂` from the `Cx`/`Cy` OpenFOAM wrote at `endTime`, per plane;
- **assert `r₂ > r₁ > 0`** — a structural fact — and **never assert a ratio**;
- compute `k`, `w1`, `w2` from those radii;
- refuse if `k` is not consistent across planes to a registered tolerance
  (a uniform-`dr` first block implies one `k` for every plane; a departure means
  the mesh is not the registered one).

This is immune, **in one stroke**, to wedge-versus-arithmetic centroids, to a
changed `nz`, to radial grading, and to the flat-sided wedge correction — the
last of which **never needs answering, because a measured centroid already
contains it.**

**Sanity of the magnitude, so nobody thinks this is chasing noise.** The
flat-sided correction is `k_measured = 2.333313` against `k_exact = 7/3`;
`Δw₁ = 4.73e-06`, which on a 20 K field difference is **9.5e-05 K** — utterly
negligible against ±0.05 bands. **This change is not about numerical necessity.
It is about deleting an assumption class.**

## 3. THE FIXTURE CHANGE — a fixture that can only produce the ratio the code assumes is not a control

The amendment-A1 fixture `make_synthetic_field_case` places cell centres at
`(j+½)·dr`, which makes `r₂ = 3r₁` **true by construction**. The fixture and
the instrument agreed **because they shared one wrong assumption** — the L-321
shape. 69 selftest checks passed and **not one could have caught this.**

**Proposed:**

- the fixture places cell centres at **annular centroids**,
  `r̄ = (2/3)(r_b³ − r_a³)/(r_b² − r_a²)`, so it reproduces `7/3` naturally
  rather than being told to;
- **a selftest arm at a THIRD ratio** — neither `3` nor `7/3`, e.g. a graded
  radial block giving `k ≈ 1.9` — on which the disk-read weights must still
  recover the analytic axis value exactly;
- the planted-zero arms re-derived from the **computed** `w1`, `w2`.

### 3.1 THE INNERMOST-ONLY ARM IS REGISTERED, NOT SUPPLEMENTARY

`w1 + w2 = k²/(k²−1) − 1/(k²−1) = (k²−1)/(k²−1) = **1**` — **identically, for
every `k`.** Verified symbolically at `k = 3, 7/3, 5/2, 11/7, 9/4`.

A **both-column** plant therefore shifts the axis value by `P·(w1+w2) = P`
**at any ratio whatsoever**, while an **innermost-only** plant shifts it by
`P·w1`, which **does** depend on `k`.

**§9's registered arm tests only partition-of-unity — a property true by
construction — and is blind to a weight error IN GENERAL**, not merely to the
`(7f₁−f₂)/6` case that exposed it. Amendment A1.3 found this as a specific
fact; it is a structural one.

**In any re-registration the innermost-only arm is a REGISTERED arm and the
load-bearing one.** The both-column arm may be retained, but must be labelled
for what it is: a partition-of-unity check, not a weight check.

### 3.2 CANDIDATE LESSON — general, and past T8

> **Any control that plants UNIFORMLY into every input of a weighted stencil
> verifies only that the weights sum to one, never what the individual weights
> are.**

This applies to **every interpolation, extrapolation and reconstruction
comparator in this lab**, not only to T8's centreline. A uniform plant is the
natural thing to write and it is the one plant that cannot see the weights.
**The discriminating plant is a NON-UNIFORM one** — a single input, or any
pattern that breaks the symmetry the weights act on.

**Escalated as a candidate lesson; the number is the chief's to assign and this
lane assigns none.**

## 4. Supervisor's rulings A, B and C — folded in

**Ruled by the heat-transfer supervisor, 2026-08-25. Recorded here as inputs to
a re-registration. They do not make this file a registration and they do not
bind Sanaa or the chief.**

### RULING A — the graded configuration stays **bare `kEpsilon`**: no `epsilon` limiter, no `limitT`

**Do not stabilise the thing being tested.** §9 P1 of the dead document made
`kEpsilon` on this case a **testable claim**. A limiter **clips the solution —
it changes the equations being solved** — so a limited run answers a *different
question while keeping the old label*. That is the failure this lab exists to
prevent, and **compute being effectively free is not a reason to buy a
comfortable answer.**

**A relaxation RAMP is a different category and is NOT banned** — a limiter
changes the steady state, a ramp changes only the path to it, *if* it lands in
the same place. The ruling makes admissibility a **measurement, not a
judgement**:

> Register the ramp as admissible **only if demonstrated neutral**. Run a level
> both with and without it; if the converged fields agree within the registered
> band it is a numerical aid and may be used on all levels. If they differ it is
> a **physical change and is FORBIDDEN.** Pre-register **both arms and the
> criterion before either runs.**

**⚠ THE TEST AS WRITTEN IS NOT EXECUTABLE — see §4a.** It named level `f` as
the comparison level *"which converges cleanly"*. **It does not.** The
principle is unaffected; the test needs repair before it can discriminate.

**Recorded as a finding, not designed around:** `epsilon` **goes negative on
every level from `Time = 24`**, at a benign `min −5.8e-07, max 0.070`, long
before anything else goes wrong. **`T` never bounds on any level.** The
turbulence closure diverged; the momentum and thermal fields did not.

### RULING B — `endTime` is NOT the remedy for `c`; the criterion governs

`c` has **stalled**, it is not slow. `T` initial residual over its last 2000
iterations: **min `5.781e-04`, max `8.576e-04`, mean `6.959e-04`, spread only
`1.48×`** — a **plateau around 7e-04, not a descent**. It descended normally to
`7.23e-04` by iteration 800 and then went nowhere for 7200 more.

- **Register explicitly that reaching `endTime` without meeting the convergence
  criterion is `NOT A RESULT`.** Rule 5 order (1) already gives this; state it
  anyway so nobody reads `endTime` as a stopping **success**.
- **Do NOT raise `endTime` for `c` on the theory that it needs longer.** That
  theory is **refuted** by the plateau above.
- **Recorded honestly:** if `c` still stalls under a new registration, `c` is
  `NOT A RESULT`, the three-level triple is **unreachable at that level**, and
  **the ladder itself needs re-choosing — a finer coarse level — not a longer
  run.** Sanaa's grid ruling fixes three levels as the gate standard, so that is
  a **case-selection question** and must be taken as one rather than papered
  over with a fourth level or a longer run.

### RULING C — existing solves may inform the DESIGN, never the ANSWER

Rule 2 is unambiguous: the grading path was fixed at a registration now known
defective, so **`c`, `m` and `f` cannot supply a graded value, a band, a
plateau claim or a triple.**

Using them as **diagnostic input to designing a new registration** —
characterising the stall, choosing `endTime`, choosing the ladder, sizing the
ramp test — **is pre-compute design work, not grading, and is legitimate.**

> **The line: they may tell us what to REGISTER. They may never tell us what
> the ANSWER is.**

Written in terms so that **nobody later mines these runs for a value on the
strength of their being "already paid for".**

## 4a. ⚠ CORRECTION THAT LANDS ON RULING A: level `f` does **not** converge cleanly

Full record at Appendix 4 of `T8_LANE_STATUS_2026-08-25.md`, committed
`11f5041f`.

`f`'s `T` initial residual: smooth descent to **`7.99e-04` at iteration 800**,
a **three-decade drop to `2.87e-07` by 900**, a **minimum of `2.3333e-07` at
940**, **228 iterations at or below the registered `1e-6` (iterations 877 to
1104)** — and then it **left**, rising two decades to a peak of **`3.85e-05` at
1800**, now descending again (**`2.04e-05` at 2100**). Still running at
`Time = 2134` of 20000.

**`f` is neither converged nor diverging. It is OSCILLATING over more than two
decades**, currently two decades above the registered tolerance.

**Consequence: `f` has no converged fields to compare.** Two runs sampled at
the same iteration could differ **by the oscillation alone**, and the test would
credit that difference to the ramp. **It cannot discriminate anything in its
present form.**

**Repair options — listed, NOT chosen, because choosing is a registration
decision:** compare over a **window** rather than at a point; require the
oscillation to **decay below a registered amplitude first**, treating failure to
decay as `NOT A RESULT`; or use a **windowed norm** of the field difference.
**This lane selects none of them.**

**Ruling A's principle is untouched.** "Do not stabilise the thing being tested"
never depended on `f`'s behaviour. **Bare `kEpsilon`, no limiter, no `limitT`,
stands.** **Ruling B is unaffected** — `c`'s stall was re-verified independently
and does not rest on `f` at all.

**Method lesson, because it caught the supervisor and this lane both:** every
`f` "convergence" reading on record — the supervisor's `1.09e-06`, this lane's
`5.11e-06` — was a **single-point sample of an oscillating quantity, taken on
the way back up**. On this case **one residual reading is not evidence of
convergence.**

## 4b. THE RULE-5 FINDING — standing rule 5's second conjunct HAS independent content, and `f` is the demonstration

**This is the largest result to come out of the dead rung and it is not about T8.**

Standing rule 5 order (1) reads *"any level not iteratively converged **or not
plateaued**"*. Whether *"or not plateaued"* carries content independent of the
first conjunct was referred upward this morning as a **canon question**, with
the lab's own comparators disagreeing: `analyse_e4a.py:346` treats the two as
**one** test, `analyse_t1b_L4.py:225` treats the plateau as a **separate
spatial** test, and the dead T8 document registered **no separate content** for
it at all.

**`f` settles it by counter-example. It is a run that MEETS the convergence
criterion and is NOT plateaued.**

Measured: **228 CONSECUTIVE iterations at or below the registered `1e-6`,
iterations 877 to 1104** — and independently confirmed that this is the **only**
stretch below `1e-6` anywhere in the run (228 consecutive, 228 total, so the
block is contiguous and unique). **`f` touched the registered criterion exactly once, for 228 iterations, and
never again.** The run then **leaves**, peaking at
`3.85e-05` at 1800, and is still oscillating at iteration 2717 —
`2.85e-05` (2000), `2.45e-05` (2200), `3.97e-05` (2400), `4.28e-05` (2600),
**rising into a second excursion**.

**Therefore the registered `1e-6` criterion is satisfiable TRANSIENTLY by a run
that does not converge.** A check asking *"did it reach 1e-6"* **passes `f`**. A
check asking *"is it below 1e-6 at `endTime`"* is a **lottery on where `endTime`
falls in the oscillation.**

**The two conjuncts are independent. "Converged" and "plateaued" are different
properties, and a run can have the first without the second.** Any comparator
that folds them into one test — as the dead T8 document did — **can pass an
oscillating solution.**

### 4b.1 And the defect reaches the ACTUAL registered instrument, not only the residual

The registered T8 convergence gate is **not** the residual: it is the
**last-two-written-checkpoints relative field change ≤ `1e-6`**. That does not
make it safe — **it makes it a phase lottery of a different kind.**

`f`'s `writeInterval` is **2000**, so the gate would compare checkpoints
**18000 and 20000** — two samples **2000 iterations apart on a field whose
residual oscillates over more than two decades**. Two checkpoints landing at
**similar phases** of that oscillation show a **small** field change and the
gate reports **converged**; the same run sampled 500 iterations later reports
otherwise. **The instrument's answer depends on the phase it happens to
sample.**

**This is the same defect class as the point-sample error that produced this
correction, moved from the residual to the field.** A gate built on **two**
samples of an oscillating quantity is a two-point sample. **Recorded as an open
instrument question for the re-registration; this lane does not propose the
fix.**

### 4b.2 RULING — what a checkpoint-difference convergence gate must satisfy

**Supervisor's ruling, 2026-08-25, and it is broader than T8.**

**The mechanism, named: a last-two-checkpoints difference gate is a TWO-POINT
SAMPLE, and on an oscillating quantity it ALIASES.** One spacing, two samples.
If the two checkpoints land at **similar phases** the difference is small, the
gate reports converged, and **nothing in the output signals that anything went
wrong.** That is the same failure as a point-sampled residual and as a
truncating reader, arriving a third way.

**A convergence gate built on differences between written checkpoints must
satisfy all three:**

1. **At least THREE distinct checkpoint SPACINGS, and it must pass at ALL of
   them.** An oscillation aliased at spacing `Δ` is not generally aliased at
   `2Δ` and `3Δ`. This **attacks the mechanism directly, costs nothing — it
   reuses checkpoints already written — and needs no new physics.**
2. **The successive differences must be NON-INCREASING across the window, not
   merely small.** A converging run's checkpoint differences shrink; an
   oscillating run's wander. **"Small" is satisfiable by luck; "shrinking" is
   not.**
3. **It must REFUSE — `NOT A RESULT`, never a pass — when the quantity is not
   shown stationary.** A difference gate on a non-stationary quantity **cannot
   distinguish convergence from aliasing**, and an instrument that cannot tell
   those apart must **say so rather than pick one**. This is deliberately the
   same refusal shape as §4c's stationarity precondition.

**Scope: this is not a T8 fix.** It bears on **every checkpoint-difference
convergence gate in the T-family and the cooling spine**, and an audit of those
is owed. Rungs **already graded** under such a gate are the exposed ones — a
verdict there may rest on a two-point sample. **Audit reported separately; no
rung is re-graded by this draft and no frozen file is touched by it.**

## 4c. THE RAMP TEST, REPAIRED — a CONTROL, not a window

**Supervisor's ruling, 2026-08-25.** None of the three repair options listed at
§4a is sufficient alone, because **all three compare ramp against no-ramp and
none establishes what the difference would be with NO INTERVENTION AT ALL.**
Without that, any difference looks meaningful and the test cannot separate
*"the ramp changed it"* from *"it varies anyway"*.

> **That is a comparison with no null — the same defect as a planted zero with
> no control, applied to a time series instead of a reader.**

Registered in three parts, **in this order**:

### 1. STATIONARITY PRECONDITION — and it can REFUSE

Before any comparison, the oscillation must be shown **statistically
stationary** over the comparison span: the **window mean** of each graded
quantity must not trend across consecutive windows by more than the
**within-window spread**.

**If stationarity fails, the ramp test CANNOT BE RUN and reports
`NOT A RESULT`.** It does **not** report a pass, and it does **not** get a
longer run to reach stationarity.

### 2. THE SELF-CONTROL — the load-bearing part

Within the **no-ramp run alone**, compare **two disjoint windows of equal
length**. Their difference is the **intrinsic window-to-window variability
`σ_self`** of a single, unchanged configuration.

**This is the null the test has been missing.**

### 3. THE TEST

Compare the ramp run's window statistics against the no-ramp run's — **same
iteration span, same window length, same quantities**.

- **Neutral if and only if the difference lies within `σ_self`** → the ramp is
  a numerical aid and may be used on all levels.
- **Exceeds `σ_self`** → the ramp **changed the solution** and is
  **FORBIDDEN**.

Compare **window statistics — mean and spread — never instantaneous values.**
The correction at §4a proves a point sample on this case is worthless.

### The level is registered BEFORE running, and is not chosen to make the test work

**If `f` cannot be shown stationary, the ramp question is unanswerable on `f`,
and it must NOT be answered by picking whichever level looks quieter.** That is
**selecting the comparison to fit the answer** — the thing pre-registration
exists to prevent. **Register the level before running.**

## 4d. THE LARGER POSSIBILITY, NAMED AND NOT SETTLED: the case may not be steady

**`buoyantBoussinesqSimpleFoam` is a STEADY solver.** A steady solver
oscillating over **more than two decades** and never settling — with a second
excursion now forming at iteration 2600 — is **evidence that the case is not
steady.**

**If the physics is genuinely unsteady, no ramp and no number of iterations
produces a steady answer, and the registered steady formulation is the wrong
instrument for this case.**

That is a **case-selection finding**. It is **larger than anything the ramp
test could return** — it would make the ramp question **moot** — and it is
recorded here **as an open possibility now, rather than discovered later after
a ramp verdict has been written.**

**This lane does not attempt to settle it and states no view on whether the
plume is physically unsteady.** It is named so that a re-registration confronts
it before, not after, committing to a steady formulation.

## 5. The measurement that refutes the level-specific-setup hypothesis

Reported in full at §APPENDIX 3 of `T8_LANE_STATUS_2026-08-25.md`. In short:
**every field in `0.orig/`, every file in `constant/`, `fvSchemes` and
`fvSolution` are BYTE-IDENTICAL across `c`, `m` and `f`**; `controlDict`
differs **only** in `endTime` and `writeInterval`; and the three
`blockMeshDict`s are **byte-identical once the hex division counts are
normalised** (same md5). **There is no level-specific initialisation or
boundary difference in `m`.** The defect class the builder audit showed to be
invisible (B7–B11) is **refuted as the cause here** — it remains a real blind
spot in the instruments, but it is not what happened to `m`.

## 6. A control the dead document did not have, and should

The builder audit found **five surviving mutations** — `R_STATIONS` on one
level, source `w0`, source `dT0`, outlet patch type, outlet `U` BC — because
**every structural instrument is geometric or bookkeeping and none reads back
what was initialised or what the boundaries do.**

`CASE.txt` already carries `w0`, `dT0`, `T_source`, `F0`, `k0`, `epsilon0` and
`Prt`. **A re-registration should register a control that reads the `0/` fields
and the boundary types back off disk and checks them against those constants**,
and refuses on disagreement. That closes four of the five survivors and costs
no compute.

## 7. Cost

No compute is proposed by this file. Any re-registration carries its own
`cost_basis` in core-minutes per `CLAUDE.md` rule 12, and the dead rung's
estimate-versus-actual — level `c` came in at **3.817 core-min against 7.13
predicted, ratio 0.54** — is a calibration datum the new estimate should use
instead of the cross-mode PIMPLE rate that over-predicted it.

## 8. Findings retained from the dead rung, because they are worth keeping

**Bounding behaviour, NON-MONOTONE in resolution.** `epsilon` bounding rate:
**c 305/8000 = 3.8 %** (contained, max stays `O(5e-2)`); **m 419/1085 =
38.6 %** (escalates `5.1e3 → 7.0e11 → 1.7e43 → 4.6e64` into SIGFPE); **f
103/1224 = 8.4 %** (contained, max `O(1e6)`). **The middle level is the only one
that destroyed itself.** `epsilon` goes negative on **every** level from
`Time = 24`. **`T` never bounds on any level.**

**No level-specific setup difference exists.** All seven `0.orig` fields, all
three `constant/` files, `fvSchemes` and `fvSolution` are **byte-identical**
across c, m and f; `controlDict` differs **only** in `endTime`/`writeInterval`;
the three `blockMeshDict`s normalise to **one md5** with identical vertices,
patch names, **patch types** and grading. The B7–B11 defect class is **refuted
as the cause of `m`'s crash** — while remaining a real blind spot.

**The read-back control (§6) closes four of the five surviving builder
mutations at zero compute** — source `w0`, source `dT0`, outlet patch type and
outlet `U` BC all become visible once the initialised fields and boundary types
are read back against `CASE.txt`'s constants.

**B7 STAYS OPEN even under this draft.** `R_STATIONS` changed on one level
alters the **mesh**, not a `CASE.txt` constant, so no read-back control sees it.
It leaves cell count, plane count and total volume untouched while breaking the
geometric similarity the Roache ladder assumes. **A re-registration that adopts
§6 and stops there still cannot see B7, and should say so rather than claim the
class is closed.**

## 9. Method note — look at the bytes before believing the number

The `f` history in §4a was **first parsed wrongly by this lane**: a fixed
**12-character substring** silently **truncated the exponent off scientific
notation**, turning `3.775818689978888e-06` into `3.7758186899` — making a
**converged** value look like a residual of **3.8**. It was caught by
**printing the raw log line before trusting the parse**, and fixed by matching
`Initial residual = [0-9.eE+-]+` in full and using the whole matched token.

**This was the fourth parsing artifact across teams on 2026-08-25**, and the
supervisor records committing the same class within the hour by inferring
convergence from a sampled prefix. The rule is the same every time:

> **Look at the bytes before believing the number.**

A truncating reader and a point sampler are the same failure wearing different
clothes: **both report a number the data does not support, with no signal that
anything went wrong.**

---

**DRAFT. NOT A REGISTRATION. NOT FROZEN. Authorisation is Sanaa's and the
chief's.**
