# DRIVAER — COST BASIS, RE-DERIVED AND REGISTERED. **THE OLD 6.073 IS STRUCK, LEGIBLE, AND ITS DEFECT IS NAMED.**

**Filed 2026-09-13 by a cfd `lab-lane` at the cfd-supervisor's direction.**
**NO SOLVER WAS RUN TO PRODUCE THIS DOCUMENT.** Every figure below is read from
`log.simpleFoam` files already on disk. **It grades nothing, re-opens nothing, and touches
no DrivAer verdict** — those stand `NOT A RESULT` on their own gates.

---

## 1. WHY THIS EXISTS

`DRIVAER_R2C_BLENDED_WALL_TREATMENT_PREREGISTRATION.md` §6 registered the medium level's
cost basis as **6.073 CPU s/iter/rank**. That figure was read from a `log.simpleFoam`
taken on the **16-core box under heavy fleet contention** and then used as a **clean**
rate. **Three rows in `docs/COST_CALIBRATION.md` now rest on it**, each attributing its
miss to "misprediction" — which read as three independent errors when it is **one
structural error counted three times.**

The cfd-supervisor ruled that this must not be repaired inside a grading item but get its
own measurement and its own registration. This is that.

## 2. METHOD — AND THE METHOD IS THE POINT

**THE RATE IS TAKEN FROM SUCCESSIVE `ExecutionTime` DIFFERENCES AT STEADY STATE. IT IS
NEVER TAKEN FROM A CUMULATIVE FIGURE AT LOW ITERATION COUNT.** That is the error the CRM
act made and paid for — 21.4 s/iteration read off an early cumulative total and multiplied
by 6,000.

* Source: each run's own `log.simpleFoam`, matching `ExecutionTime = X s  ClockTime = Y s`.
* **The first 10 % of iterations are discarded as startup/ramp.** n = 1,799 differences per
  run, from 2,000 iterations.
* **The MEDIAN is the registered statistic, not the mean.** The contention tail is
  one-sided — the medium level's maximum single-iteration cost is 8.25 s against a median
  of 2.53 — so a mean is dragged by outliers the basis should not carry.
* Both are reported, with min, max, p90 and sd, so nobody has to take the choice on trust.

## 3. THE MEASUREMENT

| run | mesh | wall fn | n | mean s/it | **median s/it** | p90 | min | max | sd |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `r2_coarse_R2` | coarse 186,709 | `nutkWallFunction` | 1,799 | 0.4359 | **0.4400** | 0.4700 | 0.3400 | 0.5900 | 0.0316 |
| `r2c_coarse_blended_R2` | coarse 186,709 | `nutUSpaldingWallFunction` | 1,799 | 0.4689 | **0.4700** | 0.5200 | 0.2600 | 1.0500 | 0.0495 |
| `r2c_medium_blended_R2` | medium 983,106 | `nutUSpaldingWallFunction` | 1,799 | 2.6343 | **2.5300** | 3.1200 | 1.3900 | 8.2500 | 0.6667 |

### 3.1 CONTENTION, REPORTED SEPARATELY AS THE CHARTER REQUIRES (§6)

`exe/clk` at the final iteration — the fraction of wall time the solver actually held CPU:

| run | `exe/clk` | contention | basis is |
|---|---:|---:|---|
| `r2_coarse_R2` | 0.9960 | **0.40 %** | effectively CLEAN |
| `r2c_coarse_blended_R2` | 0.9932 | **0.68 %** | effectively CLEAN |
| `r2c_medium_blended_R2` | 0.9546 | **4.54 %** | GROSS; the 4.5 % is named, not folded in |

**These three ran after the 17:36Z resize and reboot, on a quiet box.** That is precisely
why they are a usable basis and the superseded figure was not.

## 4. 🔴 THE REGISTERED BASIS

> ### `9.93e-06 core-seconds per cell-iteration`
> the mean of the three runs' medians, `simpleFoam`, incompressible RANS, DrivAer.

**Its claim to be transferable is not an assertion — it is the spread:**

| run | core-s / cell-iteration (median) |
|---|---:|
| `r2_coarse_R2` | 9.4264e-06 |
| `r2c_coarse_blended_R2` | 1.0069e-05 |
| `r2c_medium_blended_R2` | 1.0294e-05 |

**A 1.09× spread across three runs, TWO MESHES 5.3× APART IN CELL COUNT, and TWO DIFFERENT
WALL FUNCTIONS.** A basis that holds to 9 % across that range is measuring the solver, not
the run.

**To use it:** `core-min = cells × iterations × 9.93e-06 / 60`, independent of rank count
for the 4-rank decompositions measured here.

## 5. ~~6.073 CPU s/iter/rank~~ — **STRUCK, AND THE REASON STATED**

> ~~**`medium (983,106 cells) | 6.073 | 810 core-min CPU-held`** —
> `DRIVAER_R2C_BLENDED_WALL_TREATMENT_PREREGISTRATION.md` §6~~

**STRUCK 2026-09-13. The figure is not rewritten and §6 is not edited** (rule 6); it is
superseded here and remains legible there.

**WHY IT WAS WRONG:** it was read from a `log.simpleFoam` produced while the whole fleet
contended for 16 cores, and then used as a **CPU-held** — i.e. clean — rate. It is
**9.60×** the measured median (6.073 against 0.6325 s/iter/rank).

**AND THE OTHER REGISTERED BASIS IS WRONG TOO, BY A DIFFERENT FACTOR, WHICH IS THE PROOF
THAT CONTENTION IS THE CAUSE:** `DRIVAER_R2_LAYERED_PREREGISTRATION.md` §4 carries E7 =
**1.9365e-05 core-s/cell-iteration**, taken from the R1 *fine* run. That is **1.95×** the
measured basis — wrong in the same direction, by a different amount, because it was taken
under *different* contention. **Two independently-derived bases, both inflated, both by the
amount of contention present when each was read.** A single bad arithmetic step would have
given one factor; two factors from two sources is the signature of a systematic method
error, and the method error is: **a rate read from a contended log and recorded as clean.**

## 6. WHAT THIS DOES NOT DO

* **It changes no verdict.** `Cd` on all three runs stays `NOT A RESULT` on Gate Y1, the
  disclosed instrument conflict, and rule 5. A cost basis cannot move a physics gate.
* **It re-grades nothing and re-opens nothing.**
* **It is measured on the 16-core `r7a.4xlarge`.** The box is now **96 cores**, and a
  4-rank job's per-cell-iteration cost is set by per-core memory bandwidth, which is an
  instance property. **This basis is NOT claimed to hold on the current box**, and a
  registered rate probe to measure it there is drafted at
  `verification/campaign/DRIVAER_RATE_PROBE_PREREGISTRATION_2026-09-13.md` — **not
  enqueued, awaiting the supervisor's check 4.**

## 7. COMPUTE (rule 12)

**No solver ran.** Reading three logs and computing differences: **under 1 core-minute**,
≈ **$0.001 DERIVED, NOT MEASURED** at $0.0513/core-h, owner-stated — the box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). No estimate-versus-actual row is owed for
a desk task.

*Filed by a cfd `lab-lane`, 2026-09-13. Registers a cost basis; alters no gate, threshold,
band, cap or label. No agent's message is Sanaa's consent. Submissions parked.*
