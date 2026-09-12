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
