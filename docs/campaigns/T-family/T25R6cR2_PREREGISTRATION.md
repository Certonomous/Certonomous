# T25R6c-R2 — PRE-REGISTRATION

**Version 1.0. Frozen at the commit that carries this file.**
**Rung:** T25R6c-R2 — the successor to T25R6c, which graded **NOT A RESULT**.
**Team:** heat-transfer. **Case:** `W1150_C4_L1`, one case, two legs.
**Registration path:** `docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md`
**Grading freeze:** `verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py`

> **NOTHING IN THIS DOCUMENT AUTHORISES A LADDER LAUNCH.** T25R5 §5.1 is carried
> IN FORCE: no ladder launches on this rung's result, whatever it says.
> **NOTHING HERE RE-OPENS, WIDENS OR REQUESTS A WIDENING OF THE A1.3 CEILING OF
> 20,000 CORE-MINUTES,** which Sanaa reaffirmed on 2026-09-03 (~16:00Z) and which
> is not this team's to move. This rung's entire registered cap is **45.0
> core-minutes — 0.23 % of that ceiling.**

---

## 1. WHY THERE IS A SUCCESSOR AT ALL

T25R6c graded **NOT A RESULT** on two independent grounds, and both are carried
here unaltered:

1. **Rule 4 — no field directory at `t = 40.8`.** `writeControl timeStep` counts
   on the **global** time index, which does not reset across a `startFrom
   latestTime` restart. Leg A had advanced it to 40, so `writeInterval 400` fired
   at global index 400 = **leg-B step 360, t = 36.8**. The run directory carries
   `36.8/` and no `40.8/`. Artifact:
   `verification/runs/T-family/T25R6c_LEGAB_runs/T25R6c_VERDICT.json`,
   `"ground": "rule 4 incomplete: t=40.8 field dir: 0 found"`.
2. **G-T6c-1 PLATEAU failed independently at 13.939 % against a 5 % threshold.**
   This is **the physics finding and it is the reason a successor is needed.**

**T25R6c's `rho = 1.063997` REMAINS A DIAGNOSTIC AND MAY NOT BE QUOTED AS A
VERDICT.** The registration's §5 plateau clause was the licence for reading rho
beyond the sampled window; the measurement **withdrew** that licence. **That
prohibition stands and this document does not lift it.**

---

## 2. WHAT WAS ACTUALLY MEASURED IN T25R6c, AND WHY IT CHANGES THE DESIGN

Every number in this section is derived by
`verification/runs/T-family/T25R6cR2_LEGAB_runs/derive_t25R6cR2.py`, whose output
`DESIGN_DERIVATION.json` is committed with this registration. That script is
**not a grader**: it issues no verdict, applies no gate and writes no marker. It
runs the **planted-zero control on its own reader** (rule 3) and refuses if the
reader cannot see a known 1.23 s perturbation at a named step; and it carries a
**C-1 control** requiring its retyped reader to reproduce four values *published*
by the frozen `grade_t25R6c.py` — the 13.939 % plateau statistic, `rho =
1.063997`, and the planted-zero line counts 34 and 394 — or refuse. **All four
reproduce exactly.** A retyped reader is a different instrument until it is shown
to agree.

Source artifacts (~9.5 MB, not carried in git; sha256 recorded in
`DESIGN_DERIVATION.json`):
`verification/runs/T-family/T25R6c_LEGAB_runs/W440_C4_L1/log.solve.{legA,legB}`.

### 2.1 The restart transient is real, is 26 steps long, and is CHEAPER not dearer

Located **by solver work, not by cost** — the per-step linear-solver iteration
count, which does not depend on how busy the box is, so a contended re-run finds
the boundary in the same place. Leg-B iterations/step:

| leg-B steps | iterations/step |
|---|---|
| 1–3 | 149, 147, 144 |
| 4–10 | 112 → 93, falling |
| 11–19 | 78 → 65, a **dip** |
| 20–26 | 77, 94, 93, 92, 89, 76, 87 — recovering |
| **27–400** | **92–94, settled band, a 2.150 % integer spread across 374 steps** |

**From leg-B step 27 the solver does the same work every step.** Leg A, for
comparison, runs 115.55 iterations/step.

### 2.2 Within the settled region the cost varies and THE WORK DOES NOT

Over the settled steps the iteration count is constant to 2.15 % (an integer
±1 band) while the **40-step window rate scatters by 2.915 %**, ranging
0.371250 → 0.401750 s/step. Identical work, different cost. **That is the
machine, and it is measured here for the first time in this line.**

Quantisation is excluded as an explanation, not assumed away: a window rate is
the telescoping difference `(E[end] − E[start])/W`, so the 0.01 s `ExecutionTime`
print quantum enters at only two endpoints — ≤ 0.00025 s/step at W = 40, 0.065 %
of the level. The scatter is two orders larger.

### 2.3 The scatter DOES NOT average away, and that is measured

| window W (steps) | non-overlapping windows | sd as % of mean |
|---|---|---|
| 10 | 36 | 3.591 |
| 20 | 18 | 3.332 |
| 30 | 12 | 3.114 |
| 40 | 9 | 2.915 |
| 60 | 6 | 2.729 |
| 90 | 4 | 2.340 |
| 120 | 3 | 2.280 |

Power-law fit: **sd%(W) = e^1.762373 · W^−0.186825**, log-residual rms 0.0548.
**p = 0.187, not 0.5.** Independent noise would give 0.5. Tripling the window
buys **1.23×**, not 1.73×. Lag-1 autocorrelation of the 40-step window rates is
0.273. **The box's throughput drifts on timescales comparable to the run, and no
window length available to this rung removes it.**

### 2.4 THE T25R6c PLATEAU STATISTIC IS UNSATISFIABLE BY LENGTHENING LEG B — at any length

This is the direct answer to the design question, and it is a derivation, not an
opinion. The statistic `|r(last 40) − r(first 40)| / r(last 40)` anchors `first`
on **leg-B steps 1–40, which are the restart transient**, measured **10.43 %
cheaper** (0.345750) than the settled level (0.386000). Extending leg B moves
**only** the `last` window, which is drawn from the settled distribution.
Therefore:

- the statistic **asymptotes to 10.427 %**, not to zero;
- passing at 5 % requires `r(last 40) ≤ 0.363947`;
- **every one of the nine observed post-transient 40-step windows lies above
  that**, the minimum being 0.371250;
- the probability that any given `last 40` window falls below it, drawn from the
  measured post-transient distribution (mean 0.386000, sd 0.011252), is **2.5 %**
  — a coin flip on noise, not a convergence.

**DERIVED ANSWER TO "HOW MANY LEG-B STEPS DRIVE THE R6c STATISTIC TO 5 %":
NO FINITE COUNT.** That is what the computation returns. The statistic tests
*"has the rate stopped changing since the restart"*, not *"has the rate
plateaued"* — the **window** was the defect, not the threshold.

### 2.5 A second, independent defect in the same statistic: 5 % is inside the noise at W = 40

With a 40-step window sd of 2.915 %, the difference of two such windows has sd
≈ 4.12 % of the mean. A **perfectly flat** leg B fails a 5 % endpoint gate
roughly one time in five, on noise alone. The threshold was never wrong; it was
applied to a window too short to resolve it.

---

## 3. THE REGISTERED GATES, THRESHOLDS, BANDS AND LABELS — FROZEN

**The 5 % threshold number is UNCHANGED from T25R6c. Nothing is loosened.**
What changes is the **window** the statistic is computed over, which §2.4 and
§2.5 show was the defect.

### G-R2-1 — PLATEAU (post-transient half-split). Evaluated BEFORE rho is consulted.

- Discard leg-B steps 1–**40** (`D_EXCL`) as the restart transient.
- Split the remaining **1070** steps into two halves of **535**:
  steps **41–575** and **576–1110**.
- Compute **both** normalisations and **grade the larger**:
  `|r₂ − r₁| / r₂` and `|r₂ − r₁| / r₁`.
- **Threshold: 5 %.** Label on failure: **NOT A RESULT** (rho is printed beside
  it and is not graded).

**WHY BOTH NORMALISERS, REGISTERED IN ADVANCE (the supervisor's FINDING A).**
T25R6c divided by `last`. Because its rate was **rising**, `last > first`, so
dividing by `last` yields the **smaller** statistic: T25R6c's **13.939 %** is
**16.197 %** under the stricter normaliser. **ITS GATE FAILED UNDER THE LOOSER OF
THE TWO AND WOULD ONLY HARDEN UNDER THE STRICTER, SO THAT VERDICT IS ROBUST TO
THE CHOICE.** This is recorded here so that nobody later "tightens" the
normaliser and mistakes a harder gate for a moved verdict. R2 removes the choice
entirely by grading the larger.

**THIS IS NOT AN INSTANCE OF THE OPEN D389 HAZARD.** D389 concerns normalising an
**absolute temperature** by its mean, where the zero is arbitrary and the ratio
is therefore not meaningful. A **rate in s/step has a meaningful zero**, so
endpoint normalisation is legitimate here. **D389 IS OPEN, IS NOT OURS TO SETTLE
UNILATERALLY, AND IS NOT SETTLED BY THIS RUNG.**

### G-R2-2 — DIRECTION

- `rho = r(leg B, post-transient) / r(leg A)`.
- **Threshold: `rho < 1.0` → PASS; `rho ≥ 1.0` → GATE FAIL.**

**WHY THE POST-TRANSIENT WINDOW, AND WHY IT IS THE STRICTER CHOICE.** T25R6c's
rho averaged **all** 400 leg-B steps including the cheap transient. Excluding the
40 transient steps **raises** rho from 1.063997 to a predicted 1.075209 and so
makes G-R2-2 **harder**, not easier. The reason is physical and is fixed before
the run: **the ladder runs 8,300 leg-B steps, so a 40-step restart transient is
0.48 % of the mixture** and the settled rate is the one that prices the ladder.
The all-steps rho is **REPORTED** beside it so R2 and R6c stay directly
comparable.

### C-R2-1 — TRANSIENT CONTROL (default-deny)

The run's **own** transient end is measured, by solver work, and must be **at or
before leg-B step 40**. If it is later, the graded window would contain transient
steps — the T25R6c defect repeated — and the label is **NOT A RESULT**.

**WHY `D_EXCL = 40` AND NOT THE MEASURED 26.** Two reasons, both fixed before the
run: a **1.5× margin**, because R2's transient is a fresh draw and may run
longer; and 40 steps is **exactly the T25R6c plateau window**, so R2's excluded
region and R6c's `first` window are the same length and the two rungs stay
comparable. The margin is a **control**, not an assumption, because C-R2-1
measures whether it held.

### Default-deny order

1. **Planted-zero control** on the `ExecutionTime` reader, **both legs** (rule 3)
   → failure is a **REFUSAL**, exit 2, and issues **no verdict at all**.
2. **Rule 4 completion**, all conjuncts, both legs, **age guard vs `0/module/T`**
   → **NOT A RESULT**, exit 4.
3. **C-R2-1** transient control → **NOT A RESULT**, exit 4.
4. **G-R2-1** PLATEAU → **NOT A RESULT**, exit 4.
5. **G-R2-2** DIRECTION → **PASS** (exit 0) or **GATE FAIL** (exit 3).

**THE COMPARATOR REFUSES RATHER THAN DEGRADES.**

### Roache (rule 5) — NOT INVOKED, and that is a registered decision

There is no grid family here and no solution functional at convergence: this is a
**wall-cost measurement inside one transient at one mesh**. No observed order and
no GCI is computed, quoted or derivable. **A successor reading a grid-convergence
claim off these numbers gets NOT A RESULT.**

---

## 4. CASE PROVENANCE AND GEOMETRY

**Case:** `verification/runs/T-family/T25R6cR2_LEGAB_runs/W1150_C4_L1`
**Donor:** `verification/runs/T-family/T25R5_LINSOLVER_runs/C4_L1` — the **same**
donor T25R6c used, so R2 and R6c differ in leg-B length and the write control and
in nothing else.
**Arm dictionary:** `system/coolant/fvSolution` must be byte-identical to
`T25R5_LINSOLVER_runs/arms/fvSolution.coolant.C4` — checked by the stager, not
assumed. **Ranks: 2.** Solver: `chtMultiRegionFoam`. Region: `module` + `coolant`.

| | steps | deltaT | t | log |
|---|---|---|---|---|
| leg A | 40 | 0.02 | 0 → 0.8 | `log.solve.legA` |
| leg B | **1110** | 0.1 | 0.8 → **111.8** | `log.solve.legB` |

Leg A is the donor's controlDict **unchanged** — the window every C4/C5 wall
factor was measured on. Leg B samples **12.4 %** of the 900 s soak, against
T25R6c's 4.4 %.

**HOW THE 1110 WAS DERIVED, NOT CHOSEN.** The half-split statistic is a
difference of two window rates. Treating the halves as independent — which is
**conservative**, since the measured positive autocorrelation would only shrink
the difference's sd and therefore shorten leg B — the 5 % threshold sits at
Z = 1.96 sd when `√2 · sd%(W_half) ≤ 5/1.96`, i.e. `sd%(W_half) ≤ 1.8038 %`.
Inverting the measured power law of §2.3 gives `W_half = 531.5`, rounded up to
**535**, so `N_B = 40 + 2 × 535 = 1110` and the threshold sits at **1.9624 sd**.
**Doubling leg B again would buy only 0.219 % off the per-half sd at p = 0.187,
for double the compute; the return is flattening.**

### 4.1 THE WRITE CONTROL — the T25R6c defect, fixed, and VERIFIED not assumed

**Registered: `writeControl runTime; writeInterval 111;` with `endTime 111.8`.**

`writeControl timeStep` tests `writeTime_ = !(timeIndex_ % label(writeInterval_))`
(OpenFOAM-v2606 `src/OpenFOAM/db/Time/Time.C:1114`) and `timeIndex_` is the
**global** index, which does not reset across a restart — the defect.

`writeControl runTime` computes, at `Time.C:1117–1131`:

```
writeIndex = label(((value() - startTime_) + 0.5*deltaT_) / writeInterval_)
write iff writeIndex > writeTimeIndex_
```

with `writeTimeIndex_` initialised to 0 (`TimeState.C:38`) and `startTime_` set
to the restart time by `startFrom latestTime` (`Time.C:180–183`). The index is
therefore **relative to the restart and independent of leg A's step count
entirely**. With `startTime_ = 0.8` and `writeInterval 111`, it first exceeds 0
at `t = 111.8` and at no earlier step. The `+ 0.5·deltaT_` term also makes it
robust to accumulated float drift in `value()`.

**THE ALTERNATIVE WAS REJECTED, NOT OVERLOOKED.** Keeping `timeStep` with
`writeInterval 1150` (= N_A + N_B) would also write once, at leg-B step 1110 —
but only by **arithmetic coincidence with leg A's step count, which is the exact
quantity that caused the defect**. Change leg A and the write moves again,
silently. **A fix that still depends on what broke it is not a fix.**

**VERIFIED, NOT ASSUMED, at three levels.** (i) The source is quoted above by
file and line. (ii) `derive_t25R6cR2.py` **steps the transcribed branch over the
full 1110-step schedule** and its selftest requires that runTime writes exactly
once at endTime, that a mutated interval writes more than once, **and that the
`timeStep` setting T25R6c actually used reproduces the OBSERVED failure — a write
at leg-B step 360, t = 36.8, and none at 40.8.** (iii) `run_one_t25R6cR2.sh`
greps the leg-B controlDict **on disk** for `runTime` / `111` / `111.8` and
refuses (exit 86/87/85) if any is absent. (iv) The run itself is the final check:
**P-R2-6** predicts exactly one field directory at `t = 111.8` and **rule 4
measures it**.

---

## 5. `ExecutionTime` IS CPU TIME, NOT WALL TIME — ESTABLISHED, WITH EVIDENCE

This was an open question in T25R6c's A1.2(a) and it is settled here **from this
build's own source**, not from convention.

**Source chain, OpenFOAM-v2606, `/usr/lib/openfoam/openfoam2606/src`:**

- `OpenFOAM/db/Time/Time.H:533` — *"Print the elapsed ExecutionTime (cpu-time),
  ClockTime"*
- `OpenFOAM/db/Time/TimeIO.C:631` —
  `os << "ExecutionTime = " << elapsedCpuTime() << " s" << "  ClockTime = " << elapsedClockTime() << " s"`
- `OSspecific/POSIX/cpuTime/cpuTimeFwd.H` — `typedef cpuTimePosix cpuTime`
  (this build selects the POSIX implementation)
- `OSspecific/POSIX/cpuTime/cpuTimePosix.C:40–47` —
  `diff(a,b) = ((a.tms_utime + a.tms_stime) − (b.tms_utime + b.tms_stime)) / sysconf(_SC_CLK_TCK)`,
  with `value_type::update()` calling `::times(this)`

**ABI demonstrated on this box, not inferred.** A C program executing *the exact
OpenFOAM expression* over a 3 s `nanosleep` followed by a 1 s busy-loop returns
**CPU = 0.98 s against wall = 4.00 s**, with `_SC_CLK_TCK = 100`. `times(2)`
fills `tms_utime`/`tms_stime` for the **calling process only** — children go to
`tms_cutime`/`tms_cstime`, which OpenFOAM never reads.

**CONCLUSION: `ExecutionTime` is rank 0's own user+system CPU time. NOT wall
time, and NOT a sum over ranks.**

### 5.1 What that changes about the contention confound — in both directions

**A1.2(a) assumed a contended box INFLATES the measured rate. For the
descheduling pathway that is BACKWARDS:** a process that loses the CPU accrues
**less** cpu-time, not more. So the confound is **weaker than A1.2(a) registered**
for that mechanism.

**But it is NOT eliminated, and two pathways survive that cpu-time does not
filter:**

1. **Memory-bandwidth and last-level-cache contention** — identical work costs
   more real cycles, and those cycles are charged.
2. **MPI busy-wait** — rank 0 **spins** in a collective while a descheduled peer
   catches up, and the spin is charged to rank 0 as user cpu-time. T25R6c
   measured `ExecutionTime/ClockTime` = **0.9573** (leg A) and **0.9921**
   (leg B). A 2-rank job accruing cpu at ~99 % of wall is either never
   descheduled or spinning when it is; either way the ratio is the signature.

**AND THE WITNESS THAT FIRED A1.2(a) DOES NOT SUPPORT THE MECHANISM IT WAS READ
AS EVIDENCE FOR.** The breaking condition fired on `/proc/loadavg` **51.80 →
52.96 → 58.34** on 16 cores. **Field 4 of the same three witnesses reads
`9/625`, `9/625` and `11/625` runnable tasks.** Linux loadavg is a 1-minute EWMA
that counts uninterruptible-sleep tasks alongside runnable ones, so **it does not
establish CPU oversubscription, and 9–11 runnable against 16 cores does not
either.** `run_one_t25R6cR2.sh` records `nproc` beside every loadavg witness so
the ratio is never read without its denominator again.

### 5.2 THE HONEST LIMIT, REGISTERED IN ADVANCE

**A rho measurement finer than about ±3 % IS NOT ACHIEVABLE ON THIS SHARED BOX at
these window lengths.** §2.2 and §2.3 measure that floor at constant solver work,
and cpu-time accounting does not remove it.

**G-R2-2 is nevertheless readable, and here is why:** the predicted effect is
`rho − 1 = 7.52 %`, which is **2.58 floor-widths**. The 1-sd band on the
predicted rho is **[1.0439, 1.1066]**, entirely above 1.0. **The direction is
resolvable; a rho quoted to three decimals as a ceiling input is not.** That
distinction is registered here rather than discovered later.

### 5.3 The rank multiplier is an assumption and is named as one

`core-min = ExecutionTime × 2 / 60` assumes rank 1 burns the same cpu as rank 0.
**`ExecutionTime` cannot see rank 1.** This is the lab's established basis for
this rung and R2 keeps it **unchanged** so R2 and R6c stay comparable — but it is
an assumption, and it is stated as one rather than carried silently.

---

## 6. COST — POINT ESTIMATE, CAP, AND BASIS

**POINT ESTIMATE: 14.707 core-minutes.** A **point**, with a stated basis, never
an inequality (**L-463**).

| component | steps | measured rate (cpu s/step) | core-min |
|---|---|---|---|
| leg A | 40 | 0.359000 | 0.4787 |
| leg B, transient | 40 | 0.345750 | 0.4610 |
| leg B, settled | 1070 | 0.386000 | 13.7673 |
| **total** | **1150** | | **14.707** |

**BASIS: MEASURED**, on T25R6c's own logs — the **same** case, arm dictionary,
mesh, rank count and box. Not scaled from another rung and not a rule of thumb.
This is the material difference from T25R6c's own cost basis, whose `POINT`
denominator was priced from **B0_L1's GAMG rate** while the case ran **C4_L1's
PCG arm** — a mismatch T25R6c honestly registered as prediction P-C1 and which
came in at a ratio of ~0.10. **R2 carries no such mismatch, so a miss here is
contention or waste, not arm misprediction**, and contention and waste stay
separately named (`COMPUTE_BUDGET_CHARTER` §6).

**PER-RUN CAP: 45.0 core-minutes** — 3.06× the point estimate. **The team sets
this cap; it is not a request to Sanaa and it widens nothing.** It is enforced,
not intended: `run_one_t25R6cR2.sh` splits it into per-leg `timeout` wrappers
(leg A 60 s, leg B 1290 s), **asserts `(60 + 1290) × 2 / 60 = 45.0 ≤ 45.0` at
pre-flight and refuses (exit 84) if that ever stops holding**, and captures `rc`
**inside** the wrapper immediately after each `mpirun` — a `setsid timeout` line
exits 0 for every outcome including a kill.

**Dollars: $0.012574 at the point, $0.038475 at the cap. DERIVED, NOT MEASURED**,
at the owner-stated $0.0513/core-h. `cost_basis` is **REPORTED-BY-OWNER**: this
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). Far below the $150
single-run escalation trigger, and **0.23 % of the 20,000 core-min T25 ceiling**,
which this rung does not touch.

**Rule 12 calibration:** a row in `docs/COST_CALIBRATION.md` is **owed at
completion** and is **not discharged** by the verdict.

---

## 7. THE REGISTERED PREDICTIONS — every one a POINT, every one scored

Under Sanaa's 2026-09-03 ~21:00Z rule: *pre-registration predicts, the monitor
watches, the grader judges afterward.* Each of these is frozen here, before
compute, and scored on the certificate.

| id | prediction | value | scored by |
|---|---|---|---|
| **P-R2-1** | the **T25R6c-form** statistic will **NOT** fall below 5 % at this or any length | **10.427 %** | R-R2-1, reported |
| **P-R2-2** | the graded half-split plateau statistic | **1.80 %** (threshold 5 %) | G-R2-1 |
| **P-R2-3** | `rho` (post-transient) | **1.075209**, 1-sd band **[1.0439, 1.1066]** | G-R2-2 |
| **P-R2-4** | cost | **14.707 core-min** | §7 of the grader |
| **P-R2-5** | settled iterations/step | **92–94** inclusive | C-R2-1 |
| **P-R2-6** | field directories at `t = 111.8` | **exactly 1** | rule 4 |
| **P-R2-7** | per-half drift sd | **1.8016 %** | R-R2-3, reported |

### 7.1 THE PREDICTED VERDICT IS **GATE FAIL**, AND IT IS REGISTERED AS SUCH

G-R2-1 is predicted to **pass** (1.80 % against 5 %); G-R2-2 is then predicted to
**fail**, because `rho = 1.075 ≥ 1.0`. **A1.2's registered direction is predicted
to be FALSIFIED: post-transient leg-B steps are NOT cheaper, so every CAP in the
C4/C5 line priced off the 40-step ramp window is conservative in the UNSAFE
direction rather than the safe one.**

**This is registered in advance rather than discovered afterward.** It is stated
as a prediction, not as a result: T25R6c's rho is a diagnostic under an active
prohibition (§1), and the only thing that can turn this prediction into a verdict
is the run.

### 7.2 P-R2-7 IS A 3.0× EXTRAPOLATION AND IS LABELLED AS ONE

`W_half = 535` is three times the longest window T25R6c's log can form (180
steps). The predicted per-half sd of 1.802 % is therefore an **extrapolation** of
the §2.3 power law, and R-R2-3 **measures** it on the R2 run. **If the drift
floor is worse than the power law says, the 5 % threshold sits at fewer than 1.96
sd — and this registration will have said so in advance.** That comparison is
the calibration payoff Sanaa's 21:00Z rule describes.

---

## 8. WHAT IS REPORTED AND GATES NOTHING

Sanaa's 2026-09-03 ~20:00Z default is **reported, not gated**. These run, log and
attach to the certificate; none blocks anything.

- **R-R2-1** — the **T25R6c-form** statistic recomputed on R2's data, scoring
  P-R2-1. The predecessor's instrument, scored.
- **R-R2-2** — the full windowed trajectory, 40-step windows across both legs,
  with **iterations/step beside each window** so a reader can see work and cost
  separately.
- **R-R2-3** — the **drift floor measured on this run** at W = 40, 90, 180, 267
  and 535, beside the settled-work spread. Scores P-R2-7.
- **R-R2-4** — **`rho = rho_work × rho_throughput`**, where
  `rho_work = (settled leg-B iterations/step)/(leg-A iterations/step)` is
  **contention-free** and `rho_throughput` is what is left, which is the machine.
  **A new instrument, reported only.** A raw iteration sum mixes cheap
  `DILUPBiCGStab` sweeps with expensive `GAMGPCG` ones and the two legs need not
  share that mixture, so **`rho_work` is NOT offered as a corrected rho and no
  verdict rests on it.**
- **B-R2** — ceiling relief. **REPORTED, NEVER GATED, AND GRANTS NOTHING.** The
  threshold 0.809412 (= 20000/24709.3) is fixed on `rho_blend` and the
  registration **does not define `rho_blend`'s mixture**; both the ladder mixture
  (3500 A + 8300 B) and the probe mixture are printed, **neither gates, and this
  team resolves nothing.** A `rho ≥ 1` moves the ceiling question in the
  **unsafe** direction, not the safe one.
- **X-R2 / §7 of the grader** — predicted-vs-actual cost under rule 12.

---

## 9. THE STANDING-RULE DEFECT THIS RUNG SURFACED — DOCKETED AS **D588**, NOT RESOLVED

`CLAUDE.md` rule 4's clause **`ExecutionTime count == endTime`** is
**unsatisfiable as literally written for every case with deltaT ≠ 1**: a count is
a dimensionless integer of steps, `endTime` is a time in seconds, and they are
equal only at deltaT = 1 s. Leg A here is 40 steps at deltaT 0.02 to endTime 0.8,
so the literal reading demands `40 == 0.8`.

The witness is `grade_t25R6c.py:335–337`, whose in-code comment states the
problem and its own reinterpretation. **The engineering is correct and the
heat-transfer supervisor has read it personally and endorses it**
(`SUPERVISION_CHARTER` §3 check 1, performed and not delegated). `grade_t25R6cR2.py`
**carries the step-count reading forward unchanged**, deliberately — a successor
silently choosing a *third* reading is the failure mode being reported.

**This is the SECOND unsatisfiable-as-written clause found in this lab today**
(the first being T25R6a's equivalence predicate `r is not True and r != 0`,
tautologically true for every possible return of a function that always returns a
`dict`). **Two in one day is a pattern**, and D588 states it: nothing in the
freeze path asks of a gate *"can any run pass this?"*.

**`CLAUDE.md` IS NOT THIS TEAM'S TO AMEND AND NO AGENT MAY AMEND IT ON ANOTHER
AGENT'S SAY-SO** (rule 9). D588 is filed with owner **verification** and this
registration resolves nothing about it.

---

## 10. WHAT THIS RUNG DOES NOT DO

- **IT AUTHORISES NO LADDER LAUNCH**, on any outcome, a PASS included. T25R5 §5.1
  is carried IN FORCE.
- **IT DOES NOT MEASURE THE SOAK RATE AT STEP 11,800.** It samples t ≤ 111.8 s of
  a soak that runs to t = 900 s — 12.4 %, against T25R6c's 4.4 %. **The plateau
  clause is what licenses reading rho beyond the sampled steps, and that is a
  weaker claim, registered as the weaker claim.**
- **IT DOES NOT RE-OPEN, WIDEN OR RETIRE THE 20,000 CORE-MIN CEILING**, and
  requests no widening of anything.
- **IT DOES NOT LIFT THE PROHIBITION ON QUOTING T25R6c's `rho = 1.063997` AS A
  VERDICT.** That number remains a diagnostic.
- **IT SETTLES NOTHING ABOUT D389**, which is open, **and nothing about the
  CLAUDE.md rule 4 clause**, which is D588 and is verification's.
- **IT CONSUMES NO SOLVER OUTPUT OF T25R6a OR T25R6c.** It reads only
  `ExecutionTime` and iteration counts from logs it produces itself. T25R6c's
  logs enter only the **design derivation** in §2, never the graded numbers.

---

## 11. FREEZE

| item | value |
|---|---|
| gate 1 | **G-R2-1 PLATEAU**, post-transient half-split, **both normalisers, larger graded**, threshold **5 %** |
| gate 2 | **G-R2-2 DIRECTION**, `rho < 1.0` |
| control | **C-R2-1**, the run's own transient must end at or before leg-B step 40 |
| band | `rho` 1-sd band **[1.0439, 1.1066]**, from the measured ±2.915 % drift floor |
| cost point | **14.707 core-min** |
| per-run cap | **45.0 core-min** (3.06×), enforced by per-leg `timeout` 60 s / 1290 s |
| labels | PASS / GATE FAIL / NOT A RESULT / REFUSAL, from the fixed vocabulary only |
| predicted verdict | **GATE FAIL** |
| grading path | `verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py` |

**GRADING_FREEZE:** `verification/runs/T-family/T25R6cR2_LEGAB_runs/grade_t25R6cR2.py`

The grader recomputes and reports **both** its git blob sha1 and the **full
sha256 of its disk bytes** (L-450) into `T25R6cR2_VERDICT.json` at grade time. It
cannot carry its own sha256 as an internal constant, because writing the constant
would change the file and therefore the constant.

**VERIFIED ON DISK BY THIS LANE, BEFORE THE FREEZE:** the case directory
`W1150_C4_L1` held exactly `0.orig`, `constant` and `system` — **no `0/`, no
numeric time directory, no `processor*`, no log.** No compute had occurred.
`grade_t25R6cR2.py --selftest` **PASS, 0 failed, 39 checks**, including planted
mutations that a blind reader fails the planted-zero control, that a smeared
plant does not read back at its step, that a drifting leg B flips the half-split
clause on the same 5 % threshold, that a late work excursion moves the transient
boundary where a `[min,max]` band would have hidden it, and — **demonstrated, not
asserted** — that on a series with a 10.43 % cheap first window and a settled
tail, the R6c-form statistic sits at ~10.4 % while the R2 half-split statistic on
**the same series** is ~0. **The window was the defect, not the threshold.**

**`SUPERVISION_CHARTER` §3 CHECK 1 IS NOT DISCHARGED BY THIS LANE.**
`grade_t25R6cR2.py` is a **CHANGED MEASUREMENT SCRIPT** relative to the frozen
`grade_t25R6c.py` — it changes the plateau window, the normaliser rule and rho's
window, each for a reason stated in §3. **That diff is the supervisor's personal,
non-delegable read. The lane that wrote it has run only `--selftest` and has
NEVER run `--grade`.**

---

*Frozen 2026-09-03 by heat-transfer lab-lane. No gate, threshold, band, cap or
label in this document may be altered after first compute; a departure lands as a
dated addendum at the foot, never as a rewrite (rule 2, rule 6).*
