# DRIVAER R2c — GATE B2 GRADED. **THE REGISTERED PREDICTION HELD, AND THE Cd IS STILL `NOT A RESULT`.**

**Graded 2026-09-12 by a cfd `lab-lane` under the frozen registration
`DRIVAER_R2C_BLENDED_WALL_TREATMENT_PREREGISTRATION.md` (freeze `76e2030c1`, blob
`2a8c98a08698c2bd80c10048b57ac81846fb9326`, unchanged). This record alters no gate,
threshold, cap or label.**

🔴 **GRADING ROUTE, STATED BECAUSE IT WAS ASKED:** **BY HAND, not by a watcher.** The armed
watchers (`watch_grade_r2.frozen.sh`) live in the *dead* trees and were **never staged into
the fresh `_R2` case directories** — this lane copied `0.orig/`, `system/` and `constant/`
only. **No watcher fired and none was expected to.** Every number below was produced by
importing the **frozen** `cases/navier_class/DRIVAER/grade_drivaer.py` (sha256
`6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7`, **recomputed on disk
before use** and identical to the registration's §8 literal-hash table) and calling **its own**
`read_coeff`, `coefficient_plant_control` and `windowed_plateau`. No reader was re-implemented.

**RULE 3 PLANTED-ZERO CONTROL, RUN BEFORE ANY NUMBER WAS BELIEVED.** `PLANT_COEFF = 0.05`
planted into a copy of each `coefficient.dat` and read back through the same parser:
**PASS on all four** (control Cd/Cl, blended Cd/Cl; read-back delta 0.05). A zero from a
reader not shown able to see a non-zero is not evidence; these readers were shown.

---

## 1. RULE 4 STRICT COMPLETION — MEASURED CLAUSE BY CLAUSE, NOT INFERRED FROM `End`

| clause | `r2_coarse_R2` (control) | `r2c_coarse_blended_R2` |
|---|---|---|
| 1. `rc = 0` | `rc=0` **PASS** | `rc=0` **PASS** |
| 2. `End` line | 1 **PASS** | 1 **PASS** |
| 3. last time == `endTime` | 2000 == 2000 **PASS** | 2000 == 2000 **PASS** |
| 4. fields at `endTime` (`p U k omega nut phi`) | all present **PASS** | all present **PASS** |
| 5. `ExecutionTime` count == `round(endTime/deltaT)` | **2000 == 2000 PASS** | **2000 == 2000 PASS** |
| 6. **age guard** — every field newer than `0/U` | no field older-or-equal **PASS** | no field older-or-equal **PASS** |

**BOTH RUNS COMPLETE UNDER RULE 4 ON ALL SIX CLAUSES.**

🔴 **CLAUSE 5 IS THE VINDICATION OF THE RE-RUN-FROM-ZERO RULING.** It reads **exactly 2000**.
A resume from `t=1000` executes 1,000 iterations and would have produced `1000` on a fresh log
or `2414` on an appended one — and `grade_drivaer.py:241-244` calls `refuse()` (`sys.exit(2)`,
never a degrade) on either. **The ~127 core-min given up bought a gradeable run; the resume
would have bought a refused one.**

---

## 2. 🔴 GATE B2 — **INACTIVE.** THE CLEAN DISCRIMINATOR, IDENTICAL MESH, ONE LINE APART

| quantity | value |
|---|---|
| `Cd` non-blended (control) at `endTime` 2000 | **0.35525032** |
| `Cd` blended at `endTime` 2000 | **0.35516290** |
| `|ΔCd|` | **8.741586e-05** = **0.87 drag counts** |
| **relative difference** | **2.460684e-04** |
| control's trailing-200 plateau excursion | 1.647588e-02 |
| **registered threshold** = 2 × excursion | **3.295176e-02** |
| **VERDICT** | **`INACTIVE`** — relative difference is **134× BELOW** the threshold |

**THE READING IS NOT AN ARTEFACT OF A GENEROUS THRESHOLD, AND THAT WAS CHECKED RATHER THAN
ASSUMED.** The registered threshold is built on the control's own excursion, and the control is
`NOT_PLATEAUED` (§3) — **a larger excursion makes `INACTIVE` EASIER**. So the reading was
re-tested against three tighter thresholds it never had to clear:

| threshold tested | value | B2 |
|---|---|---|
| 2 × excursion (**the registered one**) | 3.295176e-02 | `INACTIVE` |
| 1 × excursion | 1.647588e-02 | `INACTIVE` |
| 2 × the 0.005 plateau tolerance | 1.000000e-02 | `INACTIVE` |
| the 0.005 tolerance itself | 5.000000e-03 | **`INACTIVE`** (still 20× clear) |

**`INACTIVE` on every reading.** The swap moved `Cd` by **0.87 drag counts** on a body whose own
convergence ripple is **~59 drag counts**: the two arms are **indistinguishable within the noise
of either**, which is a stronger statement than the gate arithmetic alone and survives §3.

---

## 3. PLATEAU — **BOTH RUNS `NOT_PLATEAUED`. THE `Cd` IS `NOT A RESULT`.**

Frozen instrument, `W = 200` samples (10 % of `endTime`), tolerance 0.005:

| run | state | excursion_rel | multiple of tol | window mean |
|---|---|---|---|---|
| control | **`NOT_PLATEAUED`** | 1.647588e-02 | **3.30×** | 0.357911 |
| blended | **`NOT_PLATEAUED`** | 2.028951e-02 | **4.06×** | 0.352740 |

This is the registration's **falsifier F3**. **Both `Cd` values are `NOT A RESULT` and neither may
be cited as a DrivAer drag coefficient.**

**DRIFT AT SEVEN WINDOW LENGTHS, BECAUSE ONE WINDOW IS NOT A PLATEAU TEST** — the same series on
this box has previously read +0.787 % / +0.047 % / +7.039 % over 10 / 20 / 30 iterations, so a
single window proves nothing in either direction:

| window (iters) | control excursion_rel | blended excursion_rel | both |
|---:|---|---|---|
| 10 | 1.192208e-02 | 1.164885e-02 | NOT |
| 20 | 1.461627e-02 | 1.285695e-02 | NOT |
| 30 | 1.461555e-02 | 1.584634e-02 | NOT |
| 50 | 1.647880e-02 | 2.006668e-02 | NOT |
| 100 | 1.647383e-02 | 2.006168e-02 | NOT |
| 200 | 1.647588e-02 | 2.028951e-02 | NOT |
| 400 | 1.655133e-02 | 2.101726e-02 | NOT |

**`NOT_PLATEAUED` at every length, and the value is STABLE across them (1.19–1.66 % control).
This is a genuinely unsettled solution, not a windowing choice** — which is the opposite of the
failure mode the multi-window check exists to catch, and it makes the call stronger, not weaker.

---

## 4. y⁺ PER PATCH — LAYERED AND UNLAYERED GROUPS SEPARATELY

From `r2_coarse/R2_MEASURED.json`, written at mesh-build time. **Its own stated basis, quoted
rather than paraphrased:** *"u_tau from U_inf=38.889, Re_L=7.19e6, L=2.79 m ALONE (INPUT); wall
distance from the BUILT mesh (OBSERVATION)"* — **a mesh-derived estimate, not a solved y⁺.**

| group | patches | faces | area m² | y⁺ area-weighted median | y⁺ min | y⁺ max |
|---|---:|---:|---:|---:|---:|---:|
| **layered** | 27 | 14,057 | 24.959 | **481.565** | 34.235 | 3805.767 |
| **unlayered** | 20 | 3,803 | 5.931 | **1940.998** | 56.062 | 5128.807 |

Worst per-patch layer coverage: `Rimsfront` / `Rimsrear` **0.000 mesh layers** (0.0 %),
`Tiresrear` 0.027 (0.1 %), `Tiresfront` 0.107 (1.0 %). Best: `NotchbackRoof` 4.45 (95.2 %),
`BodyHood` 4.14 (91.5 %). **16.3 % of boundary faces carry no usable layer.**

🔴 **THE Y1 CAP STANDS AND IS NOT SOFTENED BY THESE RUNS COMPLETING.** The coarse `Cd` is
`NOT A RESULT` on the pre-registered Y1 wall-admissibility failure, independently of §3's
plateau failure. **A Cd integrated over a body carrying both groups at once is a
mixed-wall-treatment Cd, and is never cited as a Cd on a fully layered body.**

---

## 5. 🔴 THE REGISTERED PREDICTION — **CONFIRMED, AND ITS MECHANISM CONFIRMED TOO**

`DRIVAER_R2C_B2_INTERPRETATION_ADDENDUM.md` (commits `99a49c026`, `2ac8a35f6`), filed
**BEFORE either arm ran**, predicted **B2 would read `INACTIVE`** and that this *"would be
correct physics, not a failed swap"*, because Spalding's law asymptotes to the log law and the
two wall functions agree to **0.440 % at y⁺ 232** and **0.148 % at y⁺ 481.6**, differing only
**below y⁺ ≈ 30**.

**B2 reads `INACTIVE`. The prediction holds.**

**And the mechanism is confirmed independently, not just the outcome:** the prediction's
precondition was that the body sits above y⁺ ≈ 30. §4 measures the **layered-group minimum at
y⁺ 34.235** and the **unlayered-group minimum at y⁺ 56.062** — **the entire body is above the
crossover, with nothing in the buffer layer for the blending to act on.** The wall treatment had
no region in which to differ. **This is a predicted null, not an unexplained one.**

**THE LOCAL-EQUILIBRIUM CAVEAT IS NOT DISCHARGED BY THIS RESULT.** That addendum registered a
named way the prediction could fail — the two functions take *different inputs*
(`nutkWallFunction` forms y⁺ from `k`; `nutUSpaldingWallFunction` solves for `u_τ` from `U`), so
a massively separated rear end can decouple them regardless of y⁺. **A confirming Cd does not
prove the caveat inoperative**; it shows the integrated force did not detect it. A per-patch
discriminator on the rear patches would test it, and is **not run here** — its conditional
pre-authorisation was tied to B2 reading `ACTIVE`, and B2 did not.

**LIFT, MEASURED AND REPORTED, AND DELIBERATELY NOT CLAIMED AS A SIGNAL.** `Cl` moved
0.00507984 → 0.01397983, **+175.2 % relative** — which looks large and **is not evidence the
swap did anything**: it is **0.528×** the control's *own* trailing-200 `Cl` range
(1.685351e-02). **It sits inside the control's own noise.** Recorded because a 175 % figure left
unqualified would be read as a finding by the next person to see it.

---

## 6. GATE B1 — **`PENDING`**

B1 (`|Cd_coarse − Cd_medium| / mean(Cd) ≤ 0.10`) needs the medium blended arm, launched
2026-09-12T19:49:35Z (`GRADER-FREEZE: PINNED`, `GATE-F: DETACHED`) and mid-run at grading time.
**`PENDING: verification/runs/navier_class/DRIVAER/r2c_medium_blended_R2`.**

🔴 **AND B1 IS NOW KNOWN IN ADVANCE TO CARRY NO EVIDENCE OF y⁺ INSENSITIVITY.** The registration
says so in its own words — *"If B2 shows no change, blending does nothing at y⁺ 481.6 and B1's
agreement — if it agrees — means nothing. B2 is the limb that stops a null result being read as
a pass."* **B2 has shown no change. Whatever B1 returns, it must not be reported as y⁺
insensitivity.** This is exactly the null B2 exists to catch, caught.

---

## 7. RULE-12 COST ROWS — CONTENTION NAMED SEPARATELY, NEVER FOLDED INTO THE RATIO

| | control | blended |
|---|---|---|
| wall × ranks | 881 s × 4 | 950 s × 4 |
| **actual (gross)** | **58.7 core-min** | **63.3 core-min** |
| registered estimate | 254 core-min | 254 core-min |
| **actual / predicted** | **0.231** | **0.249** |
| `ExecutionTime` / `ClockTime` | 871.5 / 875.0 = **0.9960** | 938.6 / 945.0 = **0.9932** |
| **contention** | **0.4 %** | **0.7 %** |
| contention-free equivalent | 58.1 core-min | 62.6 core-min |
| per-rank rate | 0.4405 s/it | 0.4750 s/it |
| derived $ at $0.0513/core-h | $0.050 | $0.054 |

**ATTRIBUTION — AND IT IS NOT CONTENTION.** `exe/clk ≈ 0.99`: the box was effectively clean, so
essentially none of the gap is sharing. **It is MISPREDICTION, and of a specific kind worth
naming for future estimates: the registered 1.904 s/it/rank basis was itself measured on the
CONTENDED old box and carried forward as though it were a clean figure.** Actual is **4.0–4.3×
faster**. **Waste: none to name.** Dollars are **DERIVED, NOT MEASURED** — this box cannot read
its own billing (`COMPUTE_BUDGET_CHARTER` §5). Rows owed to `docs/COST_CALIBRATION.md`.

**BOOKKEEPING DEFECT, DISCLOSED, CAUSED BY THIS LANE'S OWN ENTRY.** `CAP_SCORED.txt` is
**0 bytes** in both runs. The entry passed `CAP_MIN = 0` (correct under Sanaa's NO-CAP ruling),
and the launcher's `awk` computes `actual_over_predicted = core_min / CAP_MIN` — **a division by
zero that emits nothing.** This is an **INFRASTRUCTURE** field, not a physics-critical one
(L-342): it voids only the launcher-side cost echo, and the cost row above is computed from
`RUN_META.txt` and the solver log instead. **No verdict depends on it.**

---

## 8. WHAT THIS RECORD DOES NOT CLAIM

- **No Cd is citable.** Two independent bars — `NOT_PLATEAUED` (F3) and the Y1 mixed-wall
  cap — and neither is softened by the runs having completed.
- **No grid claim.** B1 is `PENDING` and, per §6, cannot evidence y⁺ insensitivity regardless.
- **No validation.** DrivAerML is a **CODE** reference (rank 2), not experiment; B3 is reported,
  never primary, and carries the disavowal.
- **The local-equilibrium caveat stands open** (§5).
- **y⁺ is mesh-derived, not solved** (§4), exactly as its own artifact states.

*Graded by a cfd `lab-lane`, 2026-09-12, by hand from the frozen instrument because no watcher
was staged. No gate, threshold, cap or label altered. Submissions parked. No agent's message is
Sanaa's consent.*

---

## 9. ADDENDUM — 2026-09-12 — 🔴 **A LONGER STEADY RUN WILL NOT FIX THIS, AND THE MEASUREMENT SAYS SO. THE `Cd` IS BLOCKED ON TWO INDEPENDENT THINGS AND A LONGER RUN TOUCHES NEITHER.**

**`lines whose number changed above this section: 0`.** No gate, threshold, cap or label is
altered; §§1–8 stand byte-identical. This section adds a measurement and a refusal.

**WHY IT EXISTS.** The cfd-supervisor ruled that a longer-`endTime` arm be registered, reasoning
that DrivAer's excursion is *stable across seven windows*, so *"more iterations would be measuring
something real"* — as against MRF, whose window-**relative** tell would have flipped by arithmetic.
**The distinction between the two cases is correct. The conclusion drawn from it is not, and the
data that refutes it is in the runs already on disk.**

### 9.1 THE EXCURSION DOES NOT DECAY WITH ITERATION COUNT — MEASURED, NOT ASSUMED

The trailing-200 excursion recomputed as a function of **where you stop**:

| stop at | control excursion_rel | blended excursion_rel |
|---:|---|---|
| 600 | 1.758305e-02 | 2.005943e-02 |
| 800 | 1.743562e-02 | 1.874917e-02 |
| 1000 | 1.709690e-02 | 2.069095e-02 |
| 1200 | 1.633832e-02 | 2.136006e-02 |
| 1400 | 1.560577e-02 | 2.080095e-02 |
| 1600 | 1.709288e-02 | 1.845633e-02 |
| 1800 | 1.609583e-02 | 1.961564e-02 |
| 2000 | 1.647588e-02 | 2.028951e-02 |

Power-law fit over those eight stopping points: **control `excursion ~ N^(-0.069)`**, **blended
`excursion ~ N^(+0.000)`**. The control's nominal extrapolation to the 0.005 tolerance is
**N ≈ 5.1 × 10¹⁰ iterations**, which is not a forecast but a demonstration that the fit carries no
decay. **The blended arm does not decay at all.**

### 9.2 THE AMPLITUDE IS STATIONARY — A TRANSIENT SHRINKS, THIS DOES NOT

Mean removed over iterations 1000–2000, four consecutive 250-iteration blocks:

| block | control rms | blended rms |
|---|---|---|
| 1000–1249 | 1.810956e-03 | 1.985652e-03 |
| 1250–1499 | 1.801677e-03 | 2.000793e-03 |
| 1500–1749 | 1.767461e-03 | 1.945197e-03 |
| 1750–1999 | 1.772603e-03 | 2.010776e-03 |

**Constant to ~2 % across a thousand iterations.** A decaying transient does not do this.

### 9.3 🔴 IT IS A **COHERENT PERIODIC OSCILLATION**, AND THAT IS A NAMED STOP RULE

Autocorrelation of the mean-removed `Cd` over iterations 1000–2000:

| | control | blended |
|---|---|---|
| first sign reversal | lag 8 | lag 8 |
| **fundamental period T** | **33 iterations** | **30 iterations** |
| r(T) | **+0.959** | **+0.936** |
| r(T/2) | **−0.845** | **−0.940** |
| r(2T) | **+0.970** | **+0.965** |

**Strongly positive at T and 2T, strongly negative at T/2, in BOTH arms, at nearly the same
period.** That is the textbook signature of a sustained limit cycle, not numerical noise and not a
settling transient.

**Sanaa's run instruction, item 12, names this exact case and routes it:** *"coherent oscillation
in the graded quantity → mark 'physics voting unsteady' > unsteady"*. **The physics is voting
unsteady. A steady solver cannot converge an unsteady flow; a longer steady run reproduces the same
limit cycle at the same amplitude, and lands on the same `NOT_PLATEAUED`.**

**A CORRECTION TO THIS LANE'S OWN PRELIMINARY READING, MADE BEFORE IT COULD TRAVEL.** A first pass
took the strongest autocorrelation peak in 20–400 and read periods of **198 (control) and 60
(blended)** — and nearly reported "the wall treatment changed the shedding period" as a finding.
**Those were harmonics.** The fundamentals are 33 and 30, i.e. **the two arms oscillate at
essentially the same period**, and the swap did *not* change it. The would-be finding was an
artefact of picking a maximum over a range instead of locating the first peak after the first sign
reversal. Recorded because it was wrong in the interesting direction.

### 9.4 THE REFUSAL, AND WHAT IS PROPOSED INSTEAD

**A longer-`endTime` STEADY arm is NOT registered, and this lane declines to draft one**, because
its own pre-registered criterion would be **unsatisfiable by construction**: §9.1–§9.3 measure the
quantity it would have to reduce, and that quantity is flat. Registering a run whose gate cannot be
met by the mechanism the run supplies is the mirror image of MRF's defect — **MRF would have
flipped a verdict without improving the solution; this would fail a verdict no matter how much the
solution ran.** Both are "do not extend", for opposite reasons, and §9.1's decay fit is what
separates them. *The multi-window check that rules out a windowing artefact (§3) is the same
evidence that rules out a cure by lengthening: stability across windows means the excursion is a
real, sustained feature — and a real sustained feature is still there at 6000 iterations.*

**PROPOSED INSTEAD, AS A NEW REGISTRATION, NOT DRAFTED HERE AND NOT FROZEN:** a **transient (URANS)
arm** with time-averaged `Cd` over an integer number of shedding periods, graded on the **average**
rather than the instantaneous endpoint. Sanaa's checkpoint item 3 already governs its form —
*"Every transient writes fields at an interval that gives at most 30 minutes of loss;
time-averaging accumulators are checkpointed with the fields."* **The decision is the
cfd-supervisor's; the measurement above is this lane's contribution to it.**

### 9.5 🔴 WHAT THE `Cd` IS BLOCKED ON — **TWO INDEPENDENT THINGS, AND ONLY ONE IS EVEN ADDRESSABLE BY RUNNING**

| # | blocker | fixable by running longer? | fixable by going unsteady? |
|---|---|---|---|
| 1 | **Mixed wall treatment (Y1).** 16.3 % of boundary faces carry no usable layer (`Rimsfront`/`Rimsrear` 0.000 layers); layered-group y⁺ median 481.565 against unlayered 1940.998. A `Cd` integrated over both groups at once is a mixed-wall-treatment `Cd`. | **NO** | **NO** |
| 2 | **Unconverged solution.** `NOT_PLATEAUED`, excursion 3.30×/4.06× tolerance, and §9.3 says it is a limit cycle. | **NO** (§9.1–§9.3) | **plausibly — untested** |

**BLOCKER 1 IS UNTOUCHED BY EVERYTHING DISCUSSED HERE AND IS NOW ALSO KNOWN NOT TO BE RESCUABLE BY
BLENDING** — that was the hypothesis B2 tested, and B2 read `INACTIVE` (§2) for the measured reason
that the whole body sits above the y⁺ ≈ 30 crossover (§5). **It is a MESH problem and it takes a
mesh fix.** Even a perfectly converged unsteady `Cd` on this mesh would still be uncitable.

**Neither blocker is softened by these two runs having completed, and the completion is still worth
having: they are the first DrivAer solves this lab has finished, they PASS rule 4 on all six
clauses, and they closed the wall-treatment question with a predicted null whose mechanism was
measured.**

*Appended by a cfd `lab-lane`, 2026-09-12. No gate, threshold, cap or label altered. Submissions
parked. No agent's message is Sanaa's consent.*
