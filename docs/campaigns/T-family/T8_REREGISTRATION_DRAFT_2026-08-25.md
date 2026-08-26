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


### 4b.3 SUPERSESSION — criterion 1 is REPLACED by Class C's sustained window. Recorded visibly, with the reason.

**Supervisor's ruling, 2026-08-25, superseding part of the supervisor's own
ruling of three hours earlier. Recorded as a visible supersession, not a silent
edit.**

| | |
|---|---|
| **Criterion 1** — three distinct spacings | **SUPERSEDED** |
| **Criterion 2** — non-increasing differences | **STANDS** — it is Class C's **C2 (not growing)** |
| **Criterion 3** — refuse on non-stationarity | **STANDS** — it is Class C's **C3 (stationarity)** |

**Why criterion 1 fell.** The Δ/2Δ/3Δ test **requires uniformly spaced
checkpoints**, and on this corpus most cases do not have them: `purgeWrite` and
run extensions leave holes, so `R_100k_f` holds `0, 18000, 20000, 56000, 58000`
— gaps of **2,000 / 36,000 / 2,000**. Among non-zero checkpoints **only
`R_10k_x` is uniformly spaced.** On the territory as it sits the test is
**mostly UNRUNNABLE**, and the claim that it "costs no compute" was wrong.

> **A remedy that cannot run on the cases it is meant to protect is not a
> remedy.**

**What replaces it.** A **sustained window with a registered minimum sample
count** delivers the same protection **without requiring uniform spacing** — so
it is runnable on the corpus that actually exists.

**Adopt the shape already registered and frozen in this territory rather than
invent one:**

- **`analyse_e4a2.py:300`** — *"C1 sustained floor AND C2 not growing AND C3
  graded-quantity stationarity."*
- **`analyse_k0cx.py:644`** — peak-to-peak over a registered window, refusing
  below nine samples, with its own line worth carrying: ***"the criterion is not
  loosened to fit the data available."***

**Disposal:** the supervisor records this as theirs — it retires no gate
threshold and no charter clause, and adopts an existing registered shape across
rungs in their own family. **Referred to Sanaa's desk; adopted by silence in a
day. No rung is re-graded and no frozen comparator is edited** — this draft
records the shape Class A must adopt **at its next legitimate re-registration**.

### 4b.4 ⚠ AND THE ALARM THAT PROMPTED THIS WAS WITHDRAWN — status is `UNJUDGED`

**No rung in the territory was shown to be harmed.** The supervisor's first
Δ/2Δ/3Δ pass printed `ALIASED` against nine cases including T1b's graded `_f`
arms; **both defects were in the test** — non-uniform spacing misread as 2Δ, and
a whole-file md5 where the gate reads only `internalField`.

**Re-verified by this lane through the comparators' own reader**, `dmax` and
`rng` separated so the `rng == 0` fallback cannot hide inside `rel`:
`R_100k_f`, `R_300k_f` and `R_30k_f` all give **`dmax` exactly `0.000e+00` with
`rng` of `1.089e-01`, `4.055e-02`, `3.220e-01`** respectively — **the fallback
did not fire, and the fields are genuinely identical between the last two
checkpoints.**

> **That is the strongest convergence evidence available, not the weakest.
> There is NO positive evidence of aliasing anywhere in the territory.**

**§4b.1's structural finding stands untouched — the Class A design cannot
distinguish convergence from aliasing. But structural exposure is not
demonstrated harm.** The correct status of `T1b`, `T1c`, `T9a`, `T9aH` and
`T9aD` is **`UNJUDGED`: not shown clean, not shown exposed.** Nothing in this
draft may be read as showing that any graded rung is wrong.

Territory audit and its withdrawal:
`docs/campaigns/T-family/CHECKPOINT_GATE_AUDIT_2026-08-25.md`, Amendment A. It
counted **verdict words in prose, not rows**, gives **no row counts**, and
**`T10aR` remains unresolved into a class.**

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

## 4e. `assert` IS NOT A GUARD — `python3 -O` DELETES IT. Disclosure against a frozen file, not repair.

**`analyse_t8.py` is frozen at `f04f9a67…` and is NOT edited by this finding.**
It is recorded so the re-registration cannot inherit the defect.

### 4e.1 The hazard, measured elsewhere in the lab tonight

**`assert` statements are removed outright by `python3 -O` / `PYTHONOPTIMIZE=1`.**
Measured consequences, not hypotheses:

- a repository guard written as `assert` **refused under `python3` and proceeded
  to `git add -A` on the shared tree under `python3 -O`**;
- a measurement script whose planted controls were all asserts **exited 0 with
  every control gone.**

> **Standing rule 3 — the planted-zero control — defeated by an interpreter
> flag.**

### 4e.2 What `analyse_t8.py` carries

**Exactly TWO asserts in 2,025 lines, and both are the same statement:**

```
1054:    assert rec["verdict"] in (band, VERDICT_NAR), (      # in grade_row()
1329:            assert rec["verdict"] in (rec["band"], VERDICT_NAR)   # in grade()
```

**That is the ONE-WAY GATE** — standing rule 5's requirement that the gate may
only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse.
**Under `python3 -O` both vanish.**

### 4e.3 THE DECISIVE MEASUREMENT — driven under `-O`, not inferred from a green selftest

A **sacrificial copy** was mutated so `grade_row` emits a verdict rule 5
forbids, then driven under both interpreters. **`analyse_t8.py` itself was not
touched.**

| run | `python3` | `python3 -O` |
|---|---|---|
| **mutated** — forbidden verdict | **guard FIRES**, `AssertionError`, rc **3** | **NO GUARD FIRES** — returns `'GATE REACHED'`, rc **0** |
| **control** — unmutated file | no fire, `'PASS'`, rc 0 | no fire, `'PASS'`, rc 0 |
| **non-assert refusal** — `refuse()` → `sys.exit(2)` on a missing root | rc **2** | rc **2** |

**The control matters: the harness is not one that always fires.** And the
`sys.exit(2)` refusals are **unaffected by `-O`** — which is precisely the
argument for the replacement form.

**Under `-O`, `analyse_t8.py` returns `GATE REACHED` where rule 5 forbids it,
with no error and rc 0.**

### 4e.4 A REFINEMENT: "fails safe" is true of the SELFTEST, not of the GRADING PATH

The supervisor's sweep concluded the file **fails safe**, because the exhaustive
one-way coverage at lines **1659–1668 is `ok(...)`-based, not assert-based**, and
so survives `-O`. **That is correct, and this lane re-verified it — the file
contains only those two asserts.**

**But lines 1659–1668 are inside `selftest()`.** They **do not run during
grading.** In an actual graded run the one-way property is protected by the
asserts at 1054 and 1329 **and by nothing else** — so under `-O` a graded run
has **no one-way protection at all**, as §4e.3 measures directly.

> **The behavioural coverage is a TEST, not a RUNTIME GUARD. It proves the
> property held at test time under plain `python3`; it cannot protect a
> production run under `-O`.**

**So the good outcome is narrower than it looked, and it was luck either way:**
had 1659–1668 been asserts too, the property would have evaporated **silently
and every mutation test would still have passed, because selftests run under
plain `python3`.**

### 4e.5 REGISTER IN THE RE-REGISTRATION

**Territory rule, adopted from cfd under the disposal rule: no `assert` in an
instrument may carry a refusal, guard, control or gate.** Referred to Sanaa;
adopted by silence in a day; retires no threshold and no charter clause.

1. **The one-way gate becomes a `raise` or `sys.exit(2)`, never an `assert`** —
   and it stops being redundant belt-and-braces and becomes the **primary**
   check, with behavioural coverage as a **second arm rather than the only one.**
2. **Every registered refusal must be DRIVEN under `python3 -O` itself and shown
   to fire identically**, against a sacrificial copy. **Not "the selftest passes
   under `-O`"** — a passing selftest exercises the clean path only, and
   identical rc on a green run is weak evidence. **What matters is whether
   refusals FIRE.**
3. **A mutant reverting `raise` → `assert` must be caught on statement type
   alone.** Cheap, decisive, and it makes the rule self-enforcing.

### 4e.6 PROVENANCE — this is D476 §31.3 recurring, and that is worse than a fresh discovery

**Three days ago** the closure team flagged a guard as *"an `assert` (off under
`python -O`; `sys.exit(2)` is the candidate comparator form)"* — and **left it
as a named limitation.** It is now **measured to be exploitable, and it is
lab-wide.**

> **A limitation named and not closed is a defect with a deadline.**


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

---

## 4f. 2026-08-26 — RULINGS A2 AND A3 FOLDED IN, AND WHAT THE COMPLETED RUNS CHANGED

**Appended, not edited.** Everything above stands on the page as written; this
section supersedes the parts it names, in the visible-supersession style of
§4b.3. **This file remains a DRAFT and registers nothing.**

### 4f.1 SUPERSESSION TABLE

| | |
|---|---|
| §4c part 2 — `σ_self` from **two** disjoint windows | **SUPERSEDED** by ruling A2 (§4f.2) |
| §4c part 3 — "the difference lies within `σ_self`" | **AMENDED** — `σ_self` is now A2's statistic |
| §4c part 1 — the stationarity precondition | **DEFECTIVE AS WRITTEN** (§4f.3). Not repaired here; a repair is a registration decision. |
| §4c "the level is registered before running" | **STANDS**, and A2 extends it to `K` and the window length |
| §4a / §4b — `f` "oscillating", "228 iterations, never again" | **FALSE AT COMPLETION** (§4f.4) |
| §4d — the case may not be steady | **PROMOTED** from an open possibility to the leading formulation question, on three-level evidence (§4f.5) |

### 4f.2 RULING A2 — `σ_self` FROM TWO WINDOWS IS ONE SAMPLE OF A DIFFERENCE, NOT AN ESTIMATE OF ITS SPREAD

**Supervisor's ruling, 2026-08-26, and it is not optional.**

§4c part 2 as drafted takes two disjoint windows and calls their single
difference `σ_self`, then part 3 passes the ramp when its difference *"lies
within `σ_self`"*. **With n = 2 there is exactly one number and no distribution:**
a ramp difference at 0.9 of that one number would be called neutral **on a null
with no width.** That is the failure class this team logged five times in one
day — *state what two things you are comparing and show they are comparable
before reading the difference.*

**REGISTERED INSTEAD:**

- `σ_self` is estimated from **at least K = 4 disjoint equal-length windows**
  within the **no-ramp run alone**;
- the neutrality criterion is the **maximum pairwise window-to-window
  difference** across those K windows (a stated quantile is acceptable **only if
  the quantile is registered before running**);
- **`K` and the window length are REGISTERED BEFORE THE RUN**, never chosen after
  seeing the series — choosing the window length that makes the answer come out
  is the same move as choosing the level that makes the test work, which §4c
  already forbids for the level;
- if the run is too short to yield **K = 4 disjoint stationary windows**, the ramp
  test **CANNOT BE RUN** and reports **`NOT A RESULT`**. It does not get a shorter
  window to manufacture `K`.

**MEASURED, so this is not pedantry.** On the completed T8 residual series
(`T8_STEADINESS_MEASUREMENT_2026-08-26.md` §4):

| level | drafted two-window `σ_self` | ruling A2's max-pairwise `σ_self` | ratio |
|---|---|---|---|
| `c` | `2.661025e-06` | **`2.197400e-05`** | **8.26×** |
| `f` | `2.098389e-08` | **`3.572086e-08`** | **1.70×** |

**On `c` the drafted null was 8.26× too narrow.** A ramp difference anywhere
between `2.7e-06` and `2.2e-05` would read **FORBIDDEN** under the drafted form
and **NEUTRAL** under A2's, **on the same data with no other difference.** A
verdict flip produced by the width of a null is the whole reason a null needs a
width.

### 4f.3 §4c PART 1 IS DEFECTIVE AS WRITTEN — reported, not repaired

The criterion — *"the window mean must not trend across consecutive windows by
more than the within-window spread"* — has two structural problems, and they are
about its **form**, so they hold regardless of what any particular run did.

1. **IT IS NON-DIRECTIONAL.** It asks whether the mean *trends*, not whether it
   *grows*, so it refuses a **decaying** series exactly as it refuses a wandering
   one and **prints the same word for both.** A test that cannot separate *"still
   settling"* from *"will never settle"* cannot carry a case-selection finding —
   those two states call for opposite decisions.
2. **IT DIVIDES A TREND BY A SPREAD.** As a series gets **smoother** the
   within-window spread tends to zero while the trend does not, so the test
   becomes **arbitrarily sensitive on exactly the best-behaved runs.** `f`'s final
   within-window sd is `1.155e-09`, three orders below its mean.

**And it admits the wrong thing.** Measured: level **`c` — which never once
reached the registered `1e-6` in 8,000 iterations and sat on a plateau four
decades above it — PASSES this precondition.** A stationarity gate that admits a
stalled run is admitting a stall as a valid comparison basis.

**THE TERRITORY ALREADY HAS THE RIGHT SHAPE AND §4b.3 ALREADY ADOPTED IT.**
`analyse_e4a2.py:299-300` — *"C1 sustained floor AND C2 **not growing** AND C3
graded-quantity stationarity"* — implemented at `:308` as
`c2 = not cl["growing"]`. **"Not growing" is directional. "Not trending" is
not.** `analyse_k0cx.py:644` takes the other admissible route, peak-to-peak
amplitude over a registered window with a registered minimum sample count, and
likewise never divides a trend by a spread.

> **§4b.3 ruled that this territory ADOPTS AN EXISTING REGISTERED SHAPE RATHER
> THAN INVENT ONE. §4c part 1, written the same day, invented one — and the
> invented one has a defect neither registered shape has.**

**No repair is chosen here. Choosing is a registration decision.**

### 4f.4 THE COMPLETED RUNS — `f`'s residual settled and `f` STILL DID NOT CONVERGE

§4a and §4b were written while `f` was at iteration 2134, then 2717.
**At completion:**

- **The residual claim in §4b is false.** There are **two** stretches at or below
  `1e-6` — iterations 877–1104 (228) and **4487–20000 (15,514)** — **15,742 of
  20,000 in total.** *"228 total, the only stretch anywhere in the run"* did not
  survive the rest of the run. **§4b's counter-example is withdrawn as stated.**
- **And it does not rescue `f`.** The registered gate is **not** the residual
  (§4b.1 said so on this page). Through the frozen comparator's own
  `check_iterative_convergence`: **`f`'s `T` relative change between checkpoints
  18000 and 20000 is `1.640285e-02` against the registered `1e-6`** — `dmax`
  `1.012327e-01 K` over `rng` `6.171651e+00`. `U`: `1.467659e-01`. **`c`:** `T`
  `9.113625e-02`, `U` `2.406859e-01`.

> **`f`'s RESIDUAL SAYS CONVERGED (`5.932e-07`) WHILE ITS TEMPERATURE FIELD IS
> STILL MOVING BY `0.101 K` BETWEEN ITS LAST TWO CHECKPOINTS. Optimistic by 1.7×
> on the residual; wrong by 16,400× on the field.**

**This is verbatim the failure `analyse_t1c.iterative_convergence` exists to
catch**, and any successor that reads convergence from residuals inherits it.

### 4f.5 RULING A3 — §4d IS ANSWERED FIRST, AND IT IS NOW EVIDENCED

**Supervisor's ruling, 2026-08-26.** The stationarity precondition of §4c part 1
and the §4d question are **the same measurement read two ways**, and the draft
treats one as a gate and the other as an open possibility. **Registered as one:**

> **If the registered level fails the stationarity precondition, the finding is
> NOT merely "the ramp test cannot be run". It is that T8's REGISTERED STEADY
> FORMULATION IS UNDER CHALLENGE, and it is reported as a CASE-SELECTION FINDING
> BEFORE any ramp verdict is written.**

A ramp verdict on a case whose steady formulation is wrong is a verdict about
nothing.

**§4d is promoted from possibility to leading formulation question**, on evidence
the draft did not have: on **identical mesh quality** (non-orthogonality Max 0,
skewness identical to thirteen significant figures), **byte-identical relaxation
factors**, across **16×** in cell count, **the registered steady formulation
reaches a converged state at NO resolution, in three different ways** — `c`
unconverged at `endTime`, `m` SIGFPE at iteration 1086, `f` unconverged at
`endTime`. **One level's failure is a case. Three levels failing three different
ways is a formulation.**

**THE HONEST LIMIT, WHICH THE SUCCESSOR MUST CARRY:** this establishes that the
failure is **grid-dependent and not attributable to mesh quality or setup**. It
does **not** separate *"the physics is unsteady"* from *"the closure is
unrealizable on this grid"*. **Both are live**, and the `epsilon` bounding rate is
**non-monotone in resolution** (`c` 3.8 %, `m` 38.6 %, `f` 8.4 %) — the middle
level is the only one that destroyed itself, which **neither hypothesis
explains.** `epsilon` goes negative on **every** level from `Time = 24`;
**`T` never bounds on any level.**

**THE DISCRIMINATING MEASUREMENT, REGISTERED BEFORE THE FORMULATION IS CHOSEN:**

1. **An unsteady run at one level** (`buoyantBoussinesqPimpleFoam` on the fine
   mesh). Under *unsteady physics* it develops a persistent, statistically
   stationary fluctuation; under *unrealizable closure* it settles. **This is the
   sharpest of the three because it does not ask a steady solver's residual
   anything.**
2. **A fourth, finer level.** A pure resolution test, and the same move RULING B
   already pointed at when it said a ladder that cannot produce three gradeable
   levels needs **re-choosing with a finer coarse level**, not a longer run.
3. **The `epsilon` bounding rate extended past `m`.** Three points are already
   non-monotone; a fourth makes the shape readable.

**The successor must confront the steady/unsteady question BEFORE committing to a
formulation.** That is what §4d said when it had one residual trace; it now has a
three-level result and can demand it.

### 4f.6 WHAT THIS LANE DID NOT DO, AND WHY

**No successor registration is written and no rung id is claimed.** This file's
own header reserves that: *"Re-registering a rung after first compute is not a
supervisor's call and is emphatically not a lane's"* — it is **Sanaa's and the
chief's**. `CLAUDE.md` rule 9 is explicit that **no agent message is Sanaa's
consent**, and a directive not to leave compute idle is not an authorisation to
re-register a dead rung.

**No solver was fired.** Firing requires a **committed and frozen**
pre-registration (rule 2), and there is none. Firing a successor tonight would
also mean firing **against two open defects this lane has just measured** — §4c
part 1's criterion (§4f.3) and the unchosen formulation (§4f.5). **A run
registered on a defective precondition spends its compute buying an answer that
cannot be read.** Cost is not the objection; **readability is.**
