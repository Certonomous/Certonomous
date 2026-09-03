# T25R6a — `C5` AT THE OUTER LEVELS (L1 AND L3), GATED ON **WALL COST**

**PRE-REGISTRATION. v1.0. NOTHING HAS RUN. No case directory named in §9 exists.**

**Team:** heat-transfer. **Ladder:** T25 (DC-cooling module).
**Predecessor:** `docs/campaigns/T-family/T25R5_PREREGISTRATION.md` v1.5, closed at
Addendum D3 (`f5e3de10`).
**Grading path (frozen at this commit):**
`verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py`.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

> **⚡ THIS IS A DELIBERATELY NARROW RUNG.** It measures **one thing** — `C5`'s wall
> factor at **L1 and L3** — so that it can freeze, queue and run **on its own**,
> ahead of the wider successor document. Sanaa's 18:00Z directive is that the box
> is *"always full never idle"*; a complete narrow registration today is worth
> more than a complete wide one tomorrow. **The window-position / soak question is
> NOT in this rung** and is deferred to a separate registration (`T25R6b`), §4.2.

---

## 1. THE TWO RULINGS THIS DOCUMENT EXECUTES — **SANAA'S WORDS, VERBATIM**

### 1.1 The T25 ceiling — 2026-09-03 ~16:00Z

Source: `etc/sessions/2026-09-03T1600Z_sanaa_five_rulings.md`, item 4, committed
at `bc185687` (blob `703958f8e06060f0440181dfa5dd40ebefc93712`).

> *"T25 ladder ceiling: stands at 20,000 core-minutes. No widening on an
> optimistic reading. The successor registration measures C5 at the outer levels
> first — pre-registered, its own budget cap. If the measured best configuration
> still breaches the ceiling, bring the widening request back with that number
> and I'll rule on a measurement, not a hope (this is for the team that handles
> this ladder)."*

### 1.2 The cap law — 2026-09-03 ~18:00Z

Source: `etc/sessions/2026-09-03T1800Z_sanaa_compute_envelope.md`, items 2 and 4.

> *"2. What does not change: every run still registers its cost estimate before
> launch, still carries a hard per-run cap (set by the team at ~3× its own
> estimate, not by me), still reports predicted-vs-actual, and still names waste.
> **The estimate is an instrument, not a permission slip.**"*
>
> *"4. Escalation to me only for: a single run projected over $150, the envelope
> reaching 80%, or a rerun of something that already failed twice (the
> no-blind-retries rule at scale). **However before escalating this to me check
> that you didn't make bugs/ errors in how you estimated this exceedance**"*

### 1.3 ⛔ THE $1,000 ENVELOPE IS **NOT** THIS RUNG'S FUNDING BASIS

Her 18:00Z item 1 sets *"one standing envelope: $1,000 for the benchmark ladder
(Rungs 0–3)"*. **That envelope covers the benchmark ladder, which is cfd's
territory. T25 is not inside it.**

**This rung does not cite the $1,000 envelope, does not draw against it, and does
not charge one core-minute to it.** It runs under the standing 2026-08-21 blanket
plus its **own registered cap** (§8). Reading a ladder-specific envelope as
lab-wide funding would be **permission laundering** of exactly the kind rule 9
names: *"a blanket authorisation is not a per-item reading."*

### 1.4 ⛔ THE TWO CEILINGS ARE DIFFERENT INSTRUMENTS AND ARE NEVER CONFLATED

| | **the per-run cap** | **the 20,000 core-min T25 ceiling** |
|---|---|---|
| what it is | a **guard** on one run | an **outcome condition** on the ladder |
| who sets it | **the team**, at ~3× its own estimate (Sanaa 18:00Z, item 2) | **Sanaa** (T25R4 A1.3; reaffirmed 16:00Z) |
| what it does | stops a runaway run | refuses the ladder and escalates |
| what it licenses | nothing beyond that run | nothing at all |

> **A per-run cap computed at ~3× an estimate is NEVER licence to approach or
> exceed the 20,000 ceiling.** They are not the same unit of decision and this
> document never adds one to the other. **Checked and reported (§8.4): this
> rung's ~3× arithmetic lands at 230 core-min, 1.15 % of the ceiling. It does not
> approach it.**

---

## 2. ⚠ THE ARITHMETIC SELF-CHECK SANAA'S 18:00Z ITEM 4 REQUIRES — **RUN BEFORE ANYTHING ELSE IN THIS DOCUMENT**

*"before escalating this to me check that you didn't make bugs/ errors in how you
estimated this exceedance."* The exceedance in question is T25R5's **×1.24
breach**, and it is escalation-grade: it is the number a widening request would
carry to her desk. It is therefore re-derived here **from the raw cells**, before
this rung's own design, and the derivation is shown.

### 2.1 The chain, cell by cell

**Step 1 — the raw cells.** `ExecutionTime`, seconds, 40 steps, 2 ranks, read from
`verification/runs/T-family/T25R5_LINSOLVER_runs/P3_SCORE.json`, key `rows`:

| | `B0` `exec_s` | `C4` `exec_s` |
|---|---|---|
| L1 | 131.28 | 13.57 |
| L2 | 516.15 | 45.40 |
| L3 | 989.39 | 188.93 |

**Step 2 — wall factors.** `131.28/13.57 = 9.6743`; `516.15/45.40 = 11.3689`;
`989.39/188.93 = 5.2368`. Published to 2 dp as **9.67 / 11.37 / 5.24**.

**Step 3 — the ladder price table**, frozen at `T25R5_PREREGISTRATION.md:58-66`,
itself computed from T25R4 Amendment **A1.1**'s frozen formula
(`T25R4_PREREGISTRATION.md:414-439`) and `GP_VERDICT.json`'s `s_per_step`:

| run | level | POINT core-min | **CAP** |
|---|---|---|---|
| `S1` | L1 | 1,881.6 | 7,526.4 |
| `S2` | L2 | 5,037.8 | 20,151.3 |
| `S3` | L3 | 10,453.9 | 41,815.5 |
| `T2` | L2 | 10,075.7 | 40,302.7 |
| `T4` | L2 | 20,151.3 | 80,605.3 |
| `W30` | L2 | 10,075.7 | 40,302.7 |
| **total** | | **57,676.0** | **230,703.9** |

**Step 4 — Σ CAP(C4)** `= Σ CAP(run) ÷ f(level(run))`:
`7526.4/9.67 + 20151.3/11.37 + 41815.5/5.24 + 40302.7/11.37 + 80605.3/11.37 + 40302.7/11.37`
`= 778.33 + 1772.32 + 7979.29 + 3544.65 + 7089.30 + 3544.65` = **24,709.3**.

**Step 5 — the breach.** `24,709.3 / 20,000 = ×1.2355`, published **×1.24**.

### 2.2 ✅ VERDICT OF THE SELF-CHECK: **NO ARITHMETIC ERROR. The number reproduces to the digit and its basis is the registered one.**

- Σ CAP recomputed here at the published 2-dp factors is **24,709.3**, matching
  `P3_SCORE.json`'s `ladder_extrapolation.sigma_cap_if_held` **exactly**.
  At full-precision factors it is 24,715.3 (×1.2358). **Both publish as ×1.24.**
- **The comparison is against the right quantity.** T25R4 **A1.3** reads
  *"IF `Σ CAP(run)` OVER THE SIX LADDER RUNS EXCEEDS `20,000` CORE-MINUTES…"* and
  A1.4 step 4 repeats *"If `Σ CAP > 20,000` → REFUSE and escalate"*. The ceiling
  is registered on **Σ CAP**, not on POINT, so dividing CAP by wall factors and
  comparing to 20,000 is the registered test, correctly performed.
- `M = 4.0` verified uniform across all six rows (`CAP/POINT` = 4.0000 for each).

### 2.3 ⚠ BUT TWO MATERIAL QUALIFICATIONS MUST TRAVEL WITH THAT NUMBER, AND NEITHER IS PRESENTLY CARRIED

These are **not** errors in the arithmetic. They are facts about **what the number
is**, both traceable to frozen text, and a desk item that omits them misrepresents
the evidence.

**(a) Σ CAP is a ×4 TIMEOUT ALLOWANCE, not an expected cost.**
A1.1 freezes `CAP(run) = M × POINT(run)` with `M = 4.0`. Since `M` is uniform,
`Σ CAP ÷ 4 = Σ POINT` exactly. **Under `C4`'s measured factors the ladder's
EXPECTED cost is `24,709.3 / 4 = 6,177.3 core-min` — inside the 20,000 ceiling
with ×3.24 of margin** ($5.28 **derived, not measured**, at $0.0513/core-h).

> **"The ladder costs more than 20,000 core-minutes" is FALSE.**
> **"The ladder's ×4 timeout allowance exceeds 20,000 core-minutes" is TRUE.**
> Only the second is what was measured, and only the second is what A1.3 tests.
> The ceiling is a **safety valve on an unattended daemon** — A1.3's own heading —
> and its stated rationale is *"chosen so that the auto-launch cannot commit the
> lab to a spend larger than that authorisation without a person."* It is
> **deliberately** expressed in worst-case units. **The test is correct as
> registered; the plain-English gloss usually attached to it is not.**

**(b) The numerator carries a ramp over-estimate that T25R4 REGISTERED IN
ADVANCE, and it points AGAINST the breach.**
T25R4 **A1.2** (`T25R4_PREREGISTRATION.md:441-452`), verbatim:

> *"The probe measures `t ∈ [0, 2] s` — which contains the t = 0→1 s ramp and the
> start-up transient, the most expensive 2 seconds of the whole 900 s run. Cruise
> steps are cheaper. **So `r(L)` OVER-estimates the ladder's mean per-step cost,
> `POINT` over-estimates the ladder's cost, and `CAP` is conservative in the safe
> direction.**"*

`Σ CAP(C4)` is `Σ CAP(B0) × (C4_ramp/B0_ramp)` — i.e. it prices `C4`'s ladder from
`C4`'s **own ramp rate**, inheriting the identical bias. **A1.2's registered
over-estimate therefore applies to the 24,709.3 too, in the direction that makes
the ×1.24 breach an OVER-statement.** A second, independent effect points the same
way: T25RF measured `B0`'s `maxIter` waste **growing** as the field settled, which
would make `f` **larger** later in the run and Σ CAP **smaller**. *(That second one
is an inference the lab explicitly declined to bank, and it stays unbanked here.)*

**(c) The consequence for T25R5's own wording, stated plainly.**
Addendum D3.1 calls the 24,709.3 *"a ×1.24 breach on the most favourable reading
available"* and argues *"a number that fails even with the assumptions stacked in
its favour is a stronger negative than one that fails on neutral assumptions."*

> **⚠ THAT OVERSTATES THE NEGATIVE, AND THE OVERSTATEMENT IS THE FINDING.** The
> assumptions are stacked in `C4`'s favour on the **factor** axis (its best
> measured per-level factors, applied to the whole run) and stacked **against**
> fitting on the **rate** axis (a numerator T25R4 registered as a knowing
> over-estimate, at a ×4 margin). It is **not** the most favourable reading
> available. **The ×1.24 breach is WEAKER evidence against the ladder than the
> record claims.** No number is corrected — 24,709.3 and ×1.2355 stand — but the
> characterisation is corrected here, prospectively, before it is re-carried.

### 2.4 What the self-check does **NOT** license

**Nothing.** It does not widen the ceiling, does not re-price the ladder, does not
authorise a launch, and does not constitute a widening request. **The 20,000
stands** (§1.1). §2.3 is recorded so that if a widening request is ever made, it
is made on an honestly characterised number. **Whether the ×4 margin or the ramp
basis should change is Sanaa's to rule on and nobody else's** — this lane asks for
nothing and this document proposes nothing.

---

## 3. THE STATE THIS RUNG STARTS FROM — **each figure re-measured against its artifact at this write**

### 3.1 The gate metric T25R5 registered rewarded the wrong quantity

`verification/runs/T-family/T25R5_LINSOLVER_runs/GT5_VERDICT.json`, key
`wall_vs_gate.FINDING`, verbatim:

> *"THE GATE METRIC IS ANTI-CORRELATED WITH WALL COST. C5 has the WORST eligible
> gate metric (2.94x) and the BEST wall factor (13.56x) -- the only arm meeting
> the ladder's 11.535x. C4 scores 60.11x on the gate and is 1.4% SHORT on wall.
> C1 scores 4.15x on the gate and is 1.30x SLOWER than the baseline. G-T5 as
> registered rewards the wrong quantity, and that is the lane's error."*

| arm | `G-T5` metric (iterations) | wall factor at L2 | `exec_s` |
|---|---|---|---|
| `B0` | 1.00× | 1.00× | 516.15 |
| `C1` | **4.15×** | **0.77×** (slower than baseline) | 670.61 |
| `C4` | **60.11×** | 11.37× | 45.40 |
| `C5` | **2.94×** (worst eligible) | **13.56×** (best) | 38.07 |

**`G-T6a` is therefore written on WALL COST and on nothing else. Iteration counts
are REPORTED and GATE NOTHING in this rung.** That is the correction, carried with
its evidence rather than as a preference.

### 3.2 `C5` was never run at L1 or L3 — **confirmed on disk, not inferred**

`ls verification/runs/T-family/T25R5_LINSOLVER_runs/` at this write holds
`C4_L1`, `C4_L2`, `C4_L3` and `C5_L2`. There is **no `C5_L1` and no `C5_L3`.**
`P3_SCORE.json` key `UNMEASURED` says the same in the record's own words:
*"C5 at L1 and L3 … has never been measured at the level that dominates ladder
cost."*

`C5` had the **best** L2 wall factor, `516.15 / 38.07 = 13.5579×`, **above** the
required `11.5352×`. T25R5's stage 2 correctly ran `C4`, the registered `G-T5`
winner, rather than substituting the arm the lab had come to prefer after seeing
the data (D2.3). **That was the right call and it is why this rung exists.**

### 3.3 `C4`'s advantage DECAYS with refinement, hardest where the cost lives

Wall factors **9.6743 (L1) / 11.3689 (L2) / 5.2368 (L3)** (§2.1). `S3` at L3 is the
single costliest ladder run — 41,815.5 of the 230,704 core-min CAP — and it is
exactly where `C4` is weakest.

---

## 4. ⛔ WHAT THIS RUNG MEASURES, AND — SAID FIRST — WHAT IT DOES **NOT**

### 4.1 It measures `C5`'s wall factor at L1 and L3 on the **same 40-step ramp window** `C4` was measured on

That identity is the point: it makes `C5` and `C4` comparable **to the digit**,
through the identical arithmetic that produced 24,709.3.

### 4.2 ⛔ IT DOES **NOT** MEASURE SOAK. THE EXTRAPOLATION IS **NOT ESTABLISHED**.

Every factor this rung produces is measured over **40 steps** at `deltaT 0.02`
(`t = 0 → 0.8 s`). The ladder runs **11,800–47,200 steps** (`t → 900 s`).
**40 steps is 0.34 % of the shortest ladder run, and it is the ramp, not the
soak.** `GT5_VERDICT.json`, key `ladder.CAVEAT`:

> *"MEASURED OVER 40 RAMP STEPS ONLY. Extrapolation to the ladder's 11,800-47,200
> steps is NOT established by this probe."*

**Stated as sharply as it can be stated:**

| | |
|---|---|
| **`Σ CAP(C5)` IS** | the ladder's ×4 timeout allowance **under the assumption** that each arm's 40-step ramp wall factor holds for the whole run. |
| **`Σ CAP(C5)` IS NOT** | a prediction of ladder cost, an expected spend, or a measurement of anything at step 11,800. |
| **the assumption is** | **UNMEASURED. THIS RUNG DOES NOT TEST IT** — and §2.3(b) shows T25R4 **registered in advance** that the rate underlying it is biased high. |

**A `G-T6a PASS` DOES NOT AUTHORISE A LADDER LAUNCH.** T25R5 §5.1 is carried into
this document **in force**: *no ladder launches on this result*, whatever it says.

**The window-position question — does the factor measured on steps 1–40 survive a
10× longer window — is DEFERRED to a separate registration (`T25R6b`) with its own
gate, its own falsifiers and its own cap.** It is deferred, **not answered**, and a
reader must not convert this rung's silence into a settled answer. That
distinction is the D3.2 discipline, applied in advance rather than at closure.

T25R5 Addendum D2.1's replacement reporting condition is carried unaltered and in
force: the pressure-share bracket **[20.9, 156.8] is a PRESSURE-SOLVE factor and
must never be quoted beside a wall factor.**

---

## 5. ⚡ THE PREDICTIONS — **REGISTERED BEFORE ANY ARM EXISTS, AND EACH CAN LOSE**

The two bracketing hypotheses, computed here so the measurement is decisive
**before** it is taken. Both hold `f_C5(L2) = 13.5579` frozen from T25R5.

| hypothesis | f(L1) | f(L2) | f(L3) | **Σ CAP** | ÷ 20,000 |
|---|---|---|---|---|---|
| **H1** — no decay: `C5` holds its L2 factor at every level | 13.5579 | 13.5579 | 13.5579 | **17,016.2** | **0.8508 — FITS** |
| **H2** — `C4`-like decay: `C5` scales by `C4`'s per-level ratios (×0.8509 at L1, ×0.4606 at L3) | 11.5370 | 13.5579 | 6.2451 | **20,724.9** | **1.0362 — BREACHES** |

> **⚡ THE CEILING SITS BETWEEN THE TWO BRACKETS.** This measurement is genuinely
> decisive and can land on either side — which is what makes it worth its budget.
> **A rung whose registered brackets both fall the same side of its threshold is
> not a measurement, it is a formality.**

**The pivot, in the most legible form.** Holding L1 and L2 at H2's values,
Σ CAP = 20,000 exactly when

> **f_C5(L3) = 7.0029.**

Arithmetic: `7526.4/11.5370 = 652.37`;
`(20151.3+40302.7+80605.3+40302.7)/13.5579 = 13,376.44`;
`20,000 − 652.37 − 13,376.44 = 5,971.19`; `41,815.5/5,971.19 = 7.0029`.
**`C4` measured 5.2368 there; `C5` must beat that by ×1.337 for the ladder to
fit on this arithmetic.** Illustrative pivot for a reader — the gate is on Σ CAP
computed from all three factors, not on this single number.

### The registered predictions

- **`P-1` — DECAY IS A PROPERTY OF THE MESH, NOT OF THE ARM.**
  Prediction: `f_C5(L3) < f_C5(L2)`. **LOSES if `f_C5(L3) ≥ f_C5(L2)`.**

- **`P-2` — `C5`'s DECAY IS MILDER THAN `C4`'s.**
  Prediction: `f_C5(L3) / f_C5(L2) > 0.4606` (`C4`'s measured ratio).
  **LOSES if `≤ 0.4606`.**
  *Mechanism claimed so that it can be wrong:* `C4`'s L3 collapse is a **multigrid**
  property — the GAMG preconditioner's coarse-grid work grows with the mesh —
  whereas `C5` is `PCG + DIC` with **no multigrid at all**, so its per-level
  scaling should track the mesh more simply.
  **⚠ THIS LANE'S MECHANISM CLAIMS HAVE A LOSING RECORD IN THIS FAMILY.** T25R5
  §1.2 diagnosed *"the multigrid is not multigridding"* and `R = 20.4545 ≥ 3.0`
  showed the coarse-grid correction **was** contributing; §0.4 attributed the
  stall floor to round-off in a `1/h` term and it was **configurational**.
  `P-2` is registered in that light — a claim to be tested, not believed.

- **`P-3` — THE PIVOT.** Prediction: `f_C5(L3) ≥ 7.0029`. **LOSES if below.**
  This is `G-T6a` restated at the dominant level and is the number to watch.

- **`P-4` — THE MACHINE-STATE REPRODUCTION.** Prediction: this rung's fresh
  `B0_L1` and `B0_L3` reproduce T25R5's integers **exactly** and their
  `ExecutionTime` within **±10 %** (§6.3). **LOSES on either miss**, and the two
  misses carry **different** registered consequences.

- **`P-5` — THE COST PREDICTION ITSELF.** Prediction: this rung's actual clean
  spend is `40.111 core-min ± 30 %`, i.e. in `[28.08, 52.14]`.
  **LOSES outside that band.** Registered because Sanaa's 18:00Z item 2 makes the
  estimate *"an instrument, not a permission slip"* — an instrument that is never
  scored is not an instrument. §8.5.

---

## 6. THE CONTROLS — **standing instruments, each named with what it refuses**

### 6.1 The planted-zero control (rule 3) — **the comparator REFUSES without it**

Delegated to the already-committed, already-frozen `compare_arms_t25R5.py`
(HEAD blob **`736bd0d9e03c898c1ca991cfc1b8fec8e0058b39`**), which
`grade_t25R6a.py` **hashes against that blob at run time and refuses on
mismatch**, so the freeze is **executable rather than asserted**.

- `PLANT = 1.234e-03 K`, planted into `T` **by line index** at the **first and
  last** cell of **both** regions, written to disk, and read back **through the
  production reader**.
- **The plant is ABOVE the `E1` threshold of 1.000e-03 K on purpose**, so
  recovering it proves **the gate can fire**, not merely that the reader can read.
- `PLANT_TOL_K = 1e-9` — ~4.6 orders above the double-precision cancellation floor
  at `T ≈ 293 K` (one ulp is 6.505e-14 K) and 6 orders below the plant.
  **L-438 / L-439 are why this tolerance is quoted in ulp and not chosen by
  taste:** a first cut at `PLANT × 1e-12 = 1.234e-15` sat *below* the noise floor
  and would have refused every control **while looking like rigour**.
- **If the reader cannot see the plant the grader REFUSES (exit 2) and issues no
  verdict at all.** A zero from a reader not shown able to see a non-zero is not
  evidence.

### 6.2 The strict completion rule (rule 4) — **all conjuncts, with the age guard**

A case is complete only if **every** clause holds:

1. `rc = 0` from `.rc.<CASE>.legA`, written **inside** the detached wrapper
   immediately after `mpirun` — a `setsid timeout …` line exits 0 for **every**
   outcome, so an rc captured around it is a constant zero that means nothing.
2. An `End` line in `log.solve.legA`.
3. **Last time == `endTime` = 0.8.**
4. Fields present at `endTime`: coolant `T U p_rgh alphat nut k omega`,
   module `T`.
5. **`ExecutionTime` count == the REGISTERED STEP COUNT = 40.**
   > **⚠ THE CLAUSE A SUCCESSOR MISREADS.** Rule 4's wording *"`ExecutionTime`
   > count == `endTime`"* is a **shorthand only literally true at `deltaT = 1`.**
   > The operative test is a **step-count identity**, not a time-value identity.
   > Here `deltaT = 0.02`, so `endTime 0.8` is **40** counts. Precedent verified
   > at source in this family: `T20_LC_c` has `endTime 4500` at `deltaT 6` with
   > **750** registered steps and an `ExecutionTime` count of **750**. Reading the
   > clause literally would fail every case with `deltaT ≠ 1`.
6. **THE AGE GUARD** — every field at `endTime` is **NEWER** than the case's own
   `0/module/T`, which the runner touches **last** at launch and which therefore
   dates the run allowed to produce the answer. **The runner REFUSES (exit 92/93)
   if `0/` or any time directory already exists**, because the guard is not
   evaluable on a pre-populated case.

**The grader REFUSES (exit 2) rather than degrading**, and returns
**`NOT A RESULT`** rather than a number on an incomplete case.

### 6.3 `P-4` — the machine-state reproduction control, **two misses, two consequences**

`B0_L1` and `B0_L3` are **re-run fresh in this rung's own sequential batch** — not
read out of T25R5's directories — so every wall factor `G-T6a` uses is a ratio of
two runs taken minutes apart **under the same machine state**.

Registered targets, read from `P3_SCORE.json.rows`:

| | `n_all` | `n_feasible` | `sum_feasible` | `pinned` | `min_final` | `exec_s` |
|---|---|---|---|---|---|---|
| `B0_L1` | 1200 | **931** | **28,821** | 275 | 4.25673299798e-09 | 131.28 |
| `B0_L3` | 1200 | **1111** | **366,954** | 96 | 9.95435773339e-09 | 989.39 |

- **The integers admit NO tolerance.** A miss means the computation is not the same
  computation → **`NOT A RESULT` for the whole rung.** Determinism is the premise
  every other number rests on.
- **`ExecutionTime` carries a ±10 % band** — L1 `[118.15, 144.41]` s;
  L3 `[890.45, 1088.33]` s. Band set from the **measured** contended/alone ratio
  **1.085** with margin, not from taste. **A miss outside the band is a DISCLOSED
  MACHINE-STATE CHANGE. It does NOT void `G-T6a`** — this rung's factors are
  ratios taken within its own batch — **but it DOES void every comparison of this
  rung's factors against `C4`'s T25R5 numbers**, and the grader prints that
  voiding beside the affected rows rather than leaving the comparison standing.

**Registering that split before the run is the whole point.** After the fact, a
slow `B0` is exactly the kind of thing a lane explains away.

### 6.4 The equivalence control — a solver change that moves the answer is a defect, not a speed-up

Carried unchanged from T25R5 §4, at both levels. `C5` vs `B0` at the same level,
both regions, at `endTime`:

| channel | DISQUALIFYING threshold |
|---|---|
| `max|ΔT|`, coolant **and** module | **1.000e-03 K** |
| `max|Δp_rgh|` | **1.0 Pa** |
| `max|ΔU|` | **1.0e-03 m/s** |
| `k`, `omega`, `nut`, `alphat`, `p` | **reported, gating nothing** |

**Any channel over threshold at either level → the rung is `NOT A RESULT`.**
*Margins to expect:* `C4` measured `1.2e-08 / 2.4e-08 / 6.04e-07 K` at L1/L2/L3 and
`C5` `1.7e-08 K` at L2 — four to five orders of margin.

### 6.5 Rule 5 (Roache) — **its NON-application is a registered decision, not an omission**

> **NO ROACHE TRIPLE IS FORMED. NO GRID CLAIM IS MADE. NO OBSERVED ORDER AND NO
> GCI IS COMPUTED, QUOTED, OR DERIVABLE FROM THIS RUNG.**

The levels here carry **wall-cost** measurements of a transient at 40 steps — not a
solution functional at convergence — so rule 5's machinery does not apply and is
**not invoked**. Any multi-level quantity a reader might mistake for a triple (the
wall factors, the mean-iteration spread) is **DISCLOSED, NOT GRADED** and carries
neither an order nor a GCI. The equivalence control's per-level `max|ΔT|` is a
field difference against a **same-mesh** baseline, not a convergence study.

**Registered consequence:** if a successor reads a grid-convergence claim off these
levels, the answer is **`NOT A RESULT`**. The grader prints this beside the
wall-factor table so the disclaimer travels with the numbers.

### 6.6 ⛔ NO BLIND RETRIES (Sanaa 2026-09-03, 18:00Z item 4)

> **A THIRD ATTEMPT AT ANYTHING THAT HAS ALREADY FAILED TWICE ESCALATES RATHER
> THAN RERUNS.**

Registered in this rung's own terms, before it can be needed: if any single case
here fails twice — for **any** reason: cap stop, rule-4 incompleteness, launcher
refusal, an integer miss — **the third attempt is not made.** The rung reports
`BLOCKED` with both failure records and escalates to the supervisor.
**Concrete anchor from this family:** T25R5's `C2` and `C3` cap-stopped **twice**
each (once contended, once alone). Under this law a third attempt would have
escalated instead of re-running, and the lane's contention explanation — which the
re-run falsified — would have reached a person sooner.

---

## 7. THE GATE, THE THRESHOLD AND THE LABELS — **all fixed here, before any run**

### 7.1 `G-T6a` — on **WALL COST**

> **`G-T6a` PASSES iff `Σ CAP(C5) ≤ 20,000` core-minutes**, where
> **`Σ CAP(C5) = Σ over the six ladder runs of CAP(run) ÷ f_C5(level(run))`**,
> with:
> - the six `CAP(run)` values taken **frozen** from §2.1 step 3;
> - **`f_C5(L1)` and `f_C5(L3)` MEASURED by this rung** as
>   `ExecutionTime(B0_L*) / ExecutionTime(C5_L*)`, from runs taken in the same
>   sequential batch;
> - **`f_C5(L2) = 13.5579` taken frozen** from `GT5_VERDICT.json`
>   (`516.15 / 38.07`) — a completed, rule-4-complete pair this rung does not
>   re-measure.

**Iteration counts gate nothing.** They are reported for the record and for
continuity with T25R5; `G-T6a` does not read them.

**The threshold is 20,000 and it is HARD.** It is Sanaa's ceiling (§1.1). It is not
a target, a guideline, or a number this rung may adjust for any reason.

### 7.2 Labels — **and only these**

- **`PASS`** — `Σ CAP(C5) ≤ 20,000`. Meaning, at full strength and no further:
  **on 40-step ramp arithmetic, `C5` prices the ladder inside the ceiling.**
  **NO LADDER LAUNCHES ON THIS RESULT** (§7.4). §4.2 governs what the number is.
- **`GATE FAIL`** — `Σ CAP(C5) > 20,000`. The rung **reports the measured
  Σ CAP, the three factors it was built from, and the arithmetic**, and **stops**.
  §7.4 is the disposition.
- **`NOT A RESULT`** — any of: a case fails rule 4 (§6.2); the planted-zero
  control refuses (§6.1); the equivalence control fires at either level (§6.4);
  `B0`'s integer reproduction misses (§6.3); or a censored run cannot be resolved
  by §7.3.
- **`BLOCKED`** — the §6.6 no-blind-retries condition fires.

### 7.3 ⚡ A CAP-STOP IS A BOUND, NOT A DISQUALIFICATION — the correction to T25R5's `E3`

T25R5's `E3` turned an `rc 124` cap-stop into a **disqualification**, which reads
in a report as *"the arm failed"* when what happened is *"the measurement was
censored."* `C2` and `C3` were lost that way. Registered here instead:

> A cap-stop (`rc 124`) yields a **CENSORED** wall factor with a known **upper
> bound**: `f < ExecutionTime(B0_level) ÷ timeout_level`. The grader computes
> `Σ CAP` at that bound.
> - If `Σ CAP` **at the bound** still exceeds 20,000 → **`GATE FAIL`**.
>   *A bound that fails is a decision.*
> - Otherwise → **`NOT A RESULT`**, censored, bound printed.
> **A CENSORED RUN CAN NEVER PRODUCE A `PASS`.**
> A cap-stop on a **baseline** run is always `NOT A RESULT`: the denominator is
> censored and no factor can be formed from it.

**Sanaa's ~3× cap law removes this hazard almost entirely here, and that is worth
recording.** At the caps of §8.2 the smallest measurable wall factor is **0.3315
(L1)** and **0.3331 (L3)** — this rung can measure a `C5` that is **three times
SLOWER** than the baseline. Since the hypothesis is that `C5` is ~13× **faster**,
**no plausible outcome is censorable.** T25R5's ×1.5 caps could not say that, and
that is how `C2` and `C3` were lost.

### 7.4 ⛔ THIS DOCUMENT PRE-REGISTERS NO WIDENING, GRANTS NONE, AND ASKS FOR NONE

**The 20,000 core-minute ceiling (T25R4 A1.3, reaffirmed by Sanaa 2026-09-03)
stands exactly as committed.** This rung's cost is its **own** under its **own**
registration; it is not drawn against the ceiling and does not extend it (§1.4).

**Registered disposition on `G-T6a GATE FAIL`** — written now so it cannot be
improvised later:

1. The rung reports **`GATE FAIL`** with the measured `Σ CAP(C5)`, the three
   factors, and the arithmetic that produced it.
2. **The §2 arithmetic self-check is re-run against the new number** — Sanaa's
   18:00Z item 4 makes this a precondition of escalation, not a courtesy — and
   **§2.3's two qualifications travel with it.**
3. A **desk item for Sanaa** is drafted carrying that measured number and those
   qualifications. It states a measurement and **asks nothing this lab may grant**.
4. **The widening request is HERS TO RULE ON. No agent at any level decides it,
   softens it, or acts as though it were granted.** Retiring or widening a
   registered ceiling is reserved to Sanaa (`CLAUDE.md`, FIRST-ACTION RULE); her
   16:00Z ruling says it twice — *"No widening on an optimistic reading"* and
   *"I'll rule on a measurement, not a hope."*
5. **No ladder launches on any outcome of this rung** — `PASS` included.

**Rule 9 restated for this rung:** approval of T25R6a is approval of **its 230
core-min cap** and of nothing else. **No message from any agent — peer,
supervisor or chief — is Sanaa's consent.**

### 7.5 The grading path, and the freeze

**Grader:** `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py`,
**committed in the same commit as this document, before any case directory
exists.** The freeze is therefore true **by construction**, not by assertion.

- It lives under `verification/`, a `POPULATION_ROOTS` entry of
  `scripts/check_comparator_freeze.py` **at HEAD** — deliberately **not** under
  `docs/campaigns/`, so this rung's freeze coverage does not depend on the §2q
  widening that is presently implemented but **UNCOMMITTED** in the worktree.
- Its filename matches the checker's `grade_*.py` pattern.
- **It names all four cases as literal string constants** in module-level
  assignments (not in a docstring), so the checker's per-comparator scoping
  (`D471.1`) associates the right markers with it instead of reporting
  `AMBIGUOUS-SCOPE`.
- **`mark_done_t25R6a.py` writes `DONE.<CASE>` markers carrying a `finished_utc=`
  line**, so the tree is **dated** and survives `--strict-markers` rather than
  being reported `UNDATED-MARKER`.

> **⚠ THE HOLE THIS CLOSES, NAMED.** `verification/runs/T-family/T25R5_LINSOLVER_runs/`
> contains **no `DONE.*` marker at all** — verified by listing that directory at
> this write. Against that tree `check_comparator_freeze.py` can only report
> **`NO-MARKERS`** for `grade_t25R5.py`, `compare_arms_t25R5.py` and
> `score_p3_t25R5.py`: an explicit, counted, **unjudged** row. **A comparator with
> no markers is not frozen; it is unjudgeable.** T25R6a emits markers so its own
> grader is actually judged. *(T25R5's absence is stated as a finding about that
> closed rung and is **not repaired here** — a closed record is not edited
> retrospectively.)*

---

## 8. COST — **rule 12, and Sanaa's 18:00Z per-run cap law, arithmetic shown**

### 8.1 The estimates, from MEASURED predecessors

Rates are this rung's own predecessors, measured at 2 ranks with `--bind-to none`
under the exact criterion and mesh that will run (`P3_SCORE.json.rows.exec_s`):
`B0_L1` **131.28 s**, `B0_L3` **989.39 s** over 40 steps.

| run | estimate basis | wall s | **estimate, core-min (2 ranks)** |
|---|---|---|---|
| `B0_L1` | **measured** 131.28 s | 131.28 | **4.376** |
| `C5_L1` | **extrapolated**: 131.28 × (38.07/516.15) | 9.68 | **0.323** |
| `B0_L3` | **measured** 989.39 s | 989.39 | **32.980** |
| `C5_L3` | **extrapolated**: 989.39 × (38.07/516.15) | 72.98 | **2.433** |
| **rung POINT estimate** | | | **40.111** |

**⚠ The two `C5` figures are the very quantity this rung exists to measure.** They
are H1's arithmetic, they are **labelled extrapolations at every appearance**, and
if `P-1`/`P-2` go against this lane they will be too small.

### 8.2 The hard per-run caps — **~3× the run's own estimate, and the arithmetic is shown**

Sanaa's 18:00Z item 2: *"a hard per-run cap (set by the team at ~3× its own
estimate, not by me)."*

> **⚠ A DESIGN DECISION THAT IS DISCLOSED, NOT BURIED — WHICH ESTIMATE THE ×3
> MULTIPLIES FOR `C5`.**
> Taking ×3 of `C5`'s *extrapolated* estimate would give caps of **0.97** and
> **7.30** core-min. **A cap set at 3× an estimate that already assumes the
> hypothesis is true can only ever confirm the hypothesis** — if `C5` is slower
> than hoped, the run cap-stops and the failure is recorded as a censored
> measurement rather than as the answer. **That is exactly how T25R5 lost `C2` and
> `C3`.**
> **Therefore the CAP-SETTING estimate for the `C5` runs is the NO-SPEED-UP
> estimate — the measured baseline cost at that level.** It is the only
> non-question-begging estimate available before the measurement exists.
> **Both estimates are registered here, before the run, so neither can be chosen
> afterwards**, and they are used for different, named purposes: the
> **cap-setting** estimate sizes the guard; the **POINT** estimate of §8.1 is the
> denominator of predicted-vs-actual (§8.5). *This lane flags the choice for the
> supervisor rather than presenting it as routine.*

| run | cap-setting estimate | × 3 | **REGISTERED HARD CAP** | `timeout_s` (2 ranks) |
|---|---|---|---|---|
| `B0_L1` | 4.376 | 13.128 | **13.20 core-min** | **396** |
| `C5_L1` | 4.376 *(no speed-up)* | 13.128 | **13.20 core-min** | **396** |
| `B0_L3` | 32.980 | 98.939 | **99.00 core-min** | **2970** |
| `C5_L3` | 32.980 *(no speed-up)* | 98.939 | **99.00 core-min** | **2970** |
| **sum of per-run caps** | | | **224.40** | |
| staging: 4 × `decomposePar`, serial, 20 s allowance | | | **1.333** | |
| **worst case** | | | **225.73** | |

> **⛔ REGISTERED RUNG CEILING: 230 CORE-MINUTES. AN OVERRUN STOPS THE RUN; IT
> DOES NOT GET A NEW BUDGET (rule 12).**

**230 core-min = 3.833 core-h = $0.1966 — DERIVED, NOT MEASURED**, at
$0.0513/core-h on a c7a.4xlarge, `cost_basis = REPORTED-BY-OWNER`. **This box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar
figure originating here is ever a measurement.

**Note the caps went UP, not down, and why that is right.** T25R5's caps were
**×1.5** (L1 9.667, L3 53.333 core-min). The ~3× law roughly doubles them, and
§7.3 shows that is precisely what makes the pessimistic outcome **measurable
instead of censored**. **The law improves this instrument; it does not merely
constrain it.**

### 8.3 Escalation triggers (Sanaa 18:00Z item 4) — **checked, none fire**

| trigger | this rung | fires? |
|---|---|---|
| a single run projected over **$150** | largest single-run estimate 32.980 core-min = **$0.0282 derived** | **no**, by ×5,300 |
| the **envelope** reaching 80 % | **not applicable — T25 is not inside the $1,000 benchmark-ladder envelope** (§1.3) | **n/a** |
| a rerun of something that **already failed twice** | none; §6.6 registers the rule prospectively | **no** |

### 8.4 The ~3× cap against the 20,000 ceiling — **checked and reported, per the standing separation**

**230 core-min is 1.15 % of the 20,000 core-min ceiling.** The ~3× arithmetic does
**not** approach it, so the §1.4 hazard — a per-run guard being read as licence
against an outcome condition — **does not arise here.** Reported rather than
assumed, because §1.4 requires it to be checked rather than felt.

### 8.5 Estimate-versus-actual, **denominator fixed in advance** (rule 12)

At closure a row lands in `docs/COST_CALIBRATION.md` under that file's append
rules and rule 10's private-index protocol.

> **THE RATIO'S DENOMINATOR IS FIXED HERE AS THE POINT ESTIMATE `40.111`
> CORE-MIN** — **not** the ceiling, **not** the CAP total, and **not** the
> cap-setting estimate of §8.2. A successor cannot choose the flattering
> denominator after seeing the actual.

Waste, if any, is **named separately and folded into no ratio**
(`COMPUTE_BUDGET_CHARTER.md` §6). `P-5` (§5) scores the estimate itself.

---

## 9. THE RUN DIRECTORIES — **NAMED, AND THEY DO NOT EXIST**

```
verification/runs/T-family/T25R6a_C5_OUTER_runs/
    grade_t25R6a.py       <- the frozen grading path, committed with this doc
    mark_done_t25R6a.py   <- rule-4 completion + DONE.<CASE> with finished_utc=
    run_one_t25R6a.sh     <- arm runner; the age guard is enforced AT LAUNCH
    B0_L1/    C5_L1/                40 steps, endTime 0.8, timeout 396 s
    B0_L3/    C5_L3/                40 steps, endTime 0.8, timeout 2970 s
```

**Verified by listing at this write: `verification/runs/T-family/T25R6a*` does not
exist, and `docs/campaigns/T-family/T25R6a*` holds nothing but this file.** No case
directory named above exists on disk. Rule 2's condition for a pre-first-compute
document is met, and it is stated as **the check that was actually run**, not as a
claim.

Cases are staged from T25R5's `arms/fvSolution.coolant.{B0,C5}` at the matching
mesh level; `run_one_t25R6a.sh` verifies by **diff** that the two `fvSolution`
pairs and both `fvSchemes` differ **only** inside the permitted `p_rgh` key set,
and **refuses to launch** on any other difference. `deltaT 0.02`,
`adjustTimeStep no`, `endTime 0.8`, `writeControl timeStep`, `writeInterval 40`,
`writeFormat ascii`, `writePrecision 12`, `timePrecision 12`, `purgeWrite 0`.

---

## 10. ORDER OF OPERATIONS — **REGISTERED, AND NOT NEGOTIABLE**

1. **This document and `grade_t25R6a.py` are committed together.** Nothing runs
   before that commit exists.
2. **The heat-transfer supervisor performs the pre-registration-presence check
   PERSONALLY** and reads the `C5` dictionary as a **diff** against `B0`'s.
   Undelegable (`SUPERVISION_CHARTER.md` §3). **No solver launches before this
   step completes.**
3. **The queue entry is written under `verification/queue/heat-transfer/` and run
   by the daemon — ONLY after step 2.** This lane launches nothing directly.
4. **Runs proceed ONE AT A TIME, none concurrent** (T25R5 Addendum D1.3 — a
   protocol the contention episode proved necessary): `B0_L1`, `C5_L1`, `B0_L3`,
   `C5_L3`.
5. **`P-4`'s reproduction control** (§6.3). An **integer** miss stops the rung:
   `NOT A RESULT`.
6. **The planted-zero control** (§6.1) runs **before** any real comparison, then
   the equivalence control (§6.4) at both levels.
7. **Rule-4 completion** (§6.2) on all four cases; `mark_done_t25R6a.py` writes
   the dated `DONE.<CASE>` markers.
8. **Evaluate `G-T6a`.** The grader computes `Σ CAP(C5)` and writes
   `T25R6a_VERDICT.json`.
9. On `GATE FAIL`, **re-run the §2 self-check against the new number** before any
   escalation (§7.4 step 2).
10. **Report, and file the rule-12 calibration row** (§8.5). **The rung ends at a
    report. It does not launch a ladder, amend T25R4, re-price anything, or move
    the ceiling.**

---

## 11. FREEZE

**Frozen by this commit:** the gate `G-T6a`, its threshold `Σ CAP ≤ 20,000`, the
labels of §7.2, the per-run caps and the 230 core-min rung ceiling of §8.2, the
predicted-vs-actual denominator 40.111 of §8.5, the predictions `P-1`…`P-5`, the
controls of §6.1–§6.6, the censoring rule of §7.3, and the grading path of §7.5.

**Before first compute**, amendments are legal and **must state the condition and
how it was checked**, naming the run directory that does not exist. **After first
compute the gates are closed**; changes land only as dated addenda that cannot
alter a gate, a threshold, a cap or a label, and originals are struck, never
rewritten (`VERIFICATION_CHARTER.md` §2b, §2d).

**Frozen files are never edited** (rule 6). A departure is disclosed in a dated
amendment appended at the foot with a version bump and the assertion
`lines whose number changed above this section: 0`.

---

## 12. WHAT THIS LANE COULD NOT VERIFY — **stated plainly rather than papered over**

1. **`C5`'s behaviour at L1 and L3 is unmeasured** — that is the rung, not a gap in
   the drafting. Every `C5` cost figure in §8 is an extrapolation from its L2
   ratio and is labelled one at each appearance.
2. **The ramp-to-soak extrapolation is NOT established and this rung does not test
   it** (§4.2). §2.3(b) establishes the **direction** of the bias from frozen text
   (A1.2) but **not its magnitude**, which no measurement in this lab currently
   bounds.
3. **`P3_SCORE.json` carries hand-added keys the committed scorer does not write.**
   `score_p3_t25R5.py`'s `json.dump` writes only `arm`, `spread`, `threshold`,
   `B0_spread`, `verdict` and `rows`; `ladder_extrapolation`, `UNMEASURED`,
   `cost_core_min`, `equivalence`, `baseline_reproduction` and `probe_status` were
   added afterwards. This lane **reproduced `sigma_cap_if_held = 24709.3` exactly**
   from the frozen table (§2.1), so that number is sound — but the file is **not
   purely instrument output** and a reader should know it. **In T25R6a the Σ CAP
   arithmetic is computed and written BY THE FROZEN GRADER**, so it is reproducible
   by re-running one command rather than by trusting a hand edit.
4. **`check_comparator_freeze.py`'s `docs/campaigns` widening is implemented and
   UNCOMMITTED in the worktree** (144 insertions / 8 deletions against HEAD —
   somebody's live unfinished work, **inspected, never reverted**, and deliberately
   **not** carried into this rung's commit). This registration does not depend on
   it: the grader is placed under `verification/`, a walk root at HEAD.
5. **This lane did not run the grader against real cases**, because none exist —
   that is the freeze working as intended. Its `--selftest` limb is exercised at
   the commit; its behaviour on real data is unverified until the runs complete,
   and any defect found then is **disclosed as an addendum, never edited away**.
6. **The `deltaT` schedule's second leg is untouched here.** The ladder steps
   `deltaT` from 0.02 to 0.1 at `t = 70 s`; this rung ends at `t = 0.8 s`, well
   inside leg A, so **it says nothing about leg-B rates.**

---

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).
**NO COMPUTE HAS OCCURRED. NO LADDER LAUNCHES ON ANY OUTCOME OF THIS RUNG.**

<!-- END OF T25R6a PRE-REGISTRATION v1.0 -->

---

## Amendment A1 — 2026-09-03, **BEFORE ANY T25R6a COMPUTE.** The supervisor's two non-delegable checks are recorded, the §8.2 cap decision is ACCEPTED on the record, and §2.3's finding is correctly framed

**Version v1.1. Lines whose number changed above this section: 0.**
**Alters NO gate, NO threshold, NO cap, NO label.** `G-T6a` and its 20,000
core-min threshold stand; the per-run caps of §8.2 and the 230 core-min rung
ceiling stand; the labels of §7.2, the predictions `P-1`…`P-5` and every control
of §6 stand unchanged. This amendment **records** decisions and **corrects a
characterisation**. It moves no number.

**THE CONDITION UNDER WHICH THIS AMENDMENT IS LEGAL, AND HOW IT WAS CHECKED.**
Rule 2 permits an amendment **before first compute**. **Checked at writing, by
listing:** none of
`verification/runs/T-family/T25R6a_C5_OUTER_runs/{B0_L1,C5_L1,B0_L3,C5_L3}`
exists — `ls` returns *"No such file or directory"* for all four. The run
directory holds instruments only. **No T25R6a compute has occurred and no queue
entry existed when this was written.**

### A1.1 THE SUPERVISOR'S TWO NON-DELEGABLE CHECKS, PERFORMED PERSONALLY — recorded here because a check nobody can find later did not happen

`SUPERVISION_CHARTER.md` §3. **Both were the supervisor's own, on the artifacts,
not on this lane's report:**

- **CHECK 4 — pre-registration committed before compute.** Verified at source at
  freeze commit **`2b9bd20b`**, timestamped **2026-09-03T16:28:09Z**: both
  `docs/campaigns/T-family/T25R6a_PREREGISTRATION.md` and
  `verification/runs/T-family/T25R6a_C5_OUTER_runs/grade_t25R6a.py` are status
  **A (added)** in that single commit, **before any case directory exists**.
  **The freeze is true by construction and rests on no agent's intention.**
- **CHECK 1 — the grading script read as code.** Properties confirmed **in the
  file**: the hard `CEILING = 20000.0`; the planted-zero control running **before**
  any real comparison and refusing if the reader cannot see its plant; the
  delegated comparator **blob-verified** and refusing if it is not the registered
  blob; a censored run returning `NOT A RESULT` and **unable to PASS**, while a
  censored bound that still exceeds the ceiling returns `GATE FAIL`; rule 1's
  verdict vocabulary carried on distinct exit codes.

### A1.2 ⚡ THE §8.2 CAP-SETTING DECISION IS **ACCEPTED** BY THE SUPERVISOR — and a successor must NOT "tidy" it back to ×3 of POINT

§8.2 sets the **`C5` runs'** caps from the **no-speed-up** estimate (the measured
baseline cost at that level) while keeping the **POINT** estimate `40.111` as the
predicted-versus-actual denominator (§8.5). **The supervisor accepted this
explicitly, and the reasoning is recorded here so it survives its author:**

> **A cap set at ×3 of an estimate that already assumes the hypothesis is TRUE
> would guarantee a censored run precisely when the hypothesis is FALSE — which
> is the one outcome this rung exists to be able to detect.** It is exactly how
> T25R5 lost `C2` and `C3`.
>
> **Sanaa's ~3× law fixes the per-run cap to the team's own estimate; it does not
> say WHICH estimate.** Choosing the one that cannot censor the falsifier is what
> makes the law **an instrument rather than a formality** — her own words for the
> principle are *"The estimate is an instrument, not a permission slip."*
>
> **What makes this defensible rather than a choice made later is that BOTH
> estimates are registered in advance**, in §8.1 and §8.2, before any arm exists.

> **⛔ TO A SUCCESSOR TIDYING THIS FILE: the `C5` caps are NOT an arithmetic slip
> and must not be "corrected" to ×3 of the extrapolated POINT.** Doing so would
> re-introduce the censoring hazard §7.3 was written to remove, and would do it in
> the direction that hides a failed hypothesis behind an `rc 124`.

### A1.3 ⚠ §2.3 IS CORRECTLY FRAMED, AND THIS AMENDMENT PINS THE FRAMING SO IT CANNOT DRIFT

The supervisor verified §2's central claims at source — `sigma_cap_if_held`
**24709.3** in `P3_SCORE.json`; `24709.3 / 4 = 6177.325`; and **A1.3:456 does put
the ceiling on `Σ CAP(run)` over the six ladder runs.** **The breach is REAL AS
REGISTERED and the test was applied correctly.**

**The framing is pinned here, in both directions, because a finding this shape is
easy to re-tell wrongly:**

> **⛔ THIS FINDING IS *NOT* "THE CEILING IS WRONG", AND IT IS *NOT* "THE TEST IS
> MISAPPLIED". NEITHER IS TRUE, AND NEITHER MAY BE WRITTEN.**
> T25R4 **A1.3:454** titles the clause *"THE CEILING — the safety valve on an
> unattended daemon"* and **:460** frames 20,000 core-min as *"~333 core-hours,
> ~$17"*. **A safety valve on an unattended daemon is SUPPOSED to bound the worst
> case, and `Σ CAP` is exactly the worst case.** The ceiling applying to a timeout
> allowance is therefore **coherent and probably deliberate.**
>
> **WHAT IS WRONG IS ONLY THE PLAIN-ENGLISH GLOSS that has been travelling with
> the number.** *"The ladder costs more than 20,000 core-minutes"* is **FALSE**.
> *"The ladder's ×4 timeout allowance exceeds 20,000 core-minutes"* is **TRUE**.
> **Fix the gloss; change no number.** T25R5 D3.1's *"a ×1.24 breach on the most
> favourable reading available"* is the specific wording corrected — prospectively,
> for anything that re-carries it — and **24,709.3 and ×1.2355 stand exactly as
> published.**

**A pattern recorded rather than left as an anecdote.** This is the **second**
confident negative characterisation from this team on 2026-09-03 that **survived
its numbers but not its wording** — the other was the supervisor's own, a freeze
flag reported to the chief as a false positive which the measurement contradicted.
**Both were caught by demanding a measurement instead of accepting a reading.**
That is an argument **for** Sanaa's 18:00Z self-check clause, not against this
lab's arithmetic.

### A1.4 ⛔ NO WIDENING REQUEST IS DRAFTED, AND THE LIVE QUESTION IS NOT A THRESHOLD VALUE

**Instructed by the supervisor and registered here: this lane drafts no widening
request, and no document of this rung pre-empts one.** §7.4's disposition is a
**registered response to a future `GATE FAIL`**, not a request, and it is not
activated by this amendment.

**On this rung's own numbers the ladder may need no widening at all** (§2.3(a):
the expected cost is 6,177.3 core-min, inside the ceiling). **The live question is
therefore not "what should the threshold be" but "WHAT IS THE CEILING MEANT TO
BIND — the worst case, or the expected cost?"** **That is Sanaa's to answer,
because the ceiling and its purpose are both hers**, and the supervisor is putting
it to her **as a question, not as a request.** Nothing here proposes an answer.

**SUBMISSIONS PARKED** (rule 7). **PERMANENTLY PRIVATE** (rule 8).

<!-- END OF T25R6a PRE-REGISTRATION v1.1 -->

