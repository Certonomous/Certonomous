# F12 — ENERGY-BOUND DISCRIMINATOR: RESULTS

**cfd lane, 2026-08-25.** Registered at
`verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md`, frozen body
committed at **`54acad46`** (blob `e976f90a…`, frozen-body sha256
`23c3e4524cf11301ff2e9e38dc2d9de1b3caad77e49f7ba1c940a8dab7790ca3`) **before any arm ran**,
with `ADDENDUM 1` at **`e46d844c`**. The runner re-verified the frozen body and the whole file
against `HEAD` before every arm; evidence at `evidence/freeze_verified.txt`.

**THIS RECORD GRADES NOTHING AND ISSUES NO VERDICT FROM THE FIXED VOCABULARY.** F12 rung 1
stands `NOT A RESULT`; rungs 2–5 stand `BLOCKED`. Rung 2's `rate_calibration_gate()` was not
invoked, read around or edited. Registered rung directories 2–5 were asserted **ABSENT**
before and after **every** arm, and rung 1's recursive fingerprint
(`2fb24ff2109188692df3eb62b2ee83f1f9a952c1513f51af49f1b11f78d0a821`) **UNCHANGED** before and
after every arm — `test -e` and the fingerprint compare in the same shell invocation as the
assertion.

**NO MECHANISM IS CLAIMED. Exonerating or implicating a lever names no third candidate.**

---

## 1. CONTROLS FIRST — BOTH PASSED, AND ONE OF THEM CAUGHT A DEFECT IN MY OWN INSTRUMENT

**`L2` PLANTED-ZERO CONTROL — PASSED, six arms, BOTH extrema.** Planted into
`147/T` of arm 0's own run, read back through the reader that produces every number below:
negative plant `-7.654321e+09` at cell **12345** and positive plant `+9.876543e+09` at cell
**4321**; clean field holds neither; both returned; both localised at the exact planted index;
cell count preserved (23,040); **`min()` relocated to the negative plant and `max()` relocated
to the positive plant.** The max-side limb is an addition to the model probe's control set and
was required here, because **this probe's primary reading is `T_max`** and a min-only control
would never have exercised the path every registered threshold is compared against.
Artifact: `evidence/discriminator.json`, key `L2_planted_zero`.

**`L1` LEVER-EFFECT CONTROL — PASSED for both arms**, and it doubles as the positive control
for the residual comparator, which returns **0** for arm 0 and non-zero for both levers in the
same run:

| arm | first-solve residuals vs arm 0 | mismatches | first divergent iteration |
| --- | --- | --- | --- |
| arm 1 | 885 | **870** | **2** |
| arm 2 | 315 | **310** | **1** |

**`P0` HARNESS FAITHFULNESS — PASS.** Arm 0 against the registered rung-1 log: **885
first-solve residuals, 0 mismatches**; `rc = 134`; abort at iteration **148**;
`Negative initial temperature T0: -2.384321367`. Against the committed control artifact
`verification/runs/F12_runs/terminal_departure_2026-08-25/evidence/terminal_departure.json`
(blob verified equal to `HEAD` at read time): the registered six printed-digit criterion is
**met**, and the stronger check added by `ADDENDUM 1` — **the full 147-row `T_max`/`T_min`
track, exact float equality — is 294 of 294 values, 0 mismatches.**

**The first reader pass returned `P0 FAIL`, and the cause was my own mis-specified check**, not
the run: §2.3's table transcribes a ten-significant-digit artifact at six decimals, and the
reader tested exact float equality against the transcription — **a check with one unreachable
branch, the `P4`/VMFL059 class.** It failed on the one arm whose answer was already known,
which is what a control is for. Disclosed in `ADDENDUM 1`, failing pass preserved at
`evidence/discriminator_P0FAIL_FIRSTPASS_PRESERVED.json`, original reader preserved at
`readers/analyse_discriminator_FIRSTPASS_PRESERVED.py` so the repair reads **as a diff**.

## 2. THE DISCRIMINATION — AND NEITHER LEVER REMOVES THE EXCURSION

Frozen thresholds, all fixed before any arm ran: `T0 = 332.3309915963 K`;
generous ceiling `T0 + 10 = 342.3309915963 K`; dynamic temperature `32.3309915963 K`;
`i_gen` control `19`; `S20` control `3.282372`; MITIGATED at `i_gen >= 38` or
`S20 <= 1.641186`; REMOVED at `i_gen = NONE` and `S20 <= 1.5`.

| | **arm 0 — CONTROL** | **arm 1 — SCHEME** | **arm 2 — RELAXATION** |
| --- | --- | --- | --- |
| the single lever | none | `div(phi,e)` → `bounded Gauss upwind` | `rho` relaxation `0.05` → `0.3` |
| **D1 `i_gen`** (first `T_max > 342.331`) | **19** | **53** | **9** |
| **D2 `S20`** (span ÷ dynamic temp at it 20) | **3.282372** | **2.770126** (−15.6 %) | **8.812329** (+168.5 %) |
| **D3 `i_T0`** (first `T_max > 332.331`) | 4 | 9 | 9 |
| `T_max` over the run | 608.505297 | **431.557459** | 509.016149 |
| `T_min` over the run | −8.156073 | **221.974501** | −124.612738 |
| `rc` | 134 | **0** | 134 |
| last iteration | 148 (abort, `T0 = −2.384321367`) | **148 (reached the registered window's end)** | **53 (abort, `T0 = −124.6127376`)** |
| **CLASSIFICATION (freeze §4)** | *n/a — it is the control* | **MITIGATED** | **EXONERATED** |

**`T_max`/`T_min` at the six registered iterations** (`evidence/discriminator.json`,
`arms.<arm>.reported_iterations`):

| it | arm 0 `T_max` / `T_min` | arm 1 `T_max` / `T_min` | arm 2 `T_max` / `T_min` |
| --- | --- | --- | --- |
| 1 | 302.835189 / 279.879433 | 302.835189 / 279.879433 | 302.835189 / 279.879433 |
| 4 | 332.985381 / 276.161434 | 331.042253 / 276.667193 | 316.940964 / 282.522283 |
| 8 | 329.624836 / 270.272989 | 329.077483 / 273.614372 | 331.356366 / 238.491077 |
| 11 | 335.446862 / 264.218612 | 333.241178 / 267.463904 | 386.855376 / 263.836884 |
| 19 | 342.519742 / 233.939444 | 335.976881 / 240.416189 | 447.584323 / 206.095132 |
| 20 | 342.626798 / 236.504460 | 334.302806 / 244.741899 | 467.658757 / 182.747430 |

*(All three agree exactly at iteration 1: the first energy solve precedes the first divergence
of either lever from the control, and that agreement is itself a consistency check.)*

## 3. THE REGISTERED PREDICTIONS — ONE FAILED, AND IT IS THE MOST USEFUL LINE HERE

| | prediction | outcome |
| --- | --- | --- |
| **`P0`** | arm 0 reproduces rung 1 exactly | **PASS** |
| **`P1`** | **arm 1 is EXONERATED** | **FAIL — arm 1 is MITIGATED** |
| **`P2`** | arm 2 is EXONERATED | **PASS** |
| **`P3`** | arm 1's `S20` within 20 % of 3.282372 | **PASS** — 2.770126, −15.6 %, inside `[2.625898, 3.938846]` |
| **`P4`** | arm 2's `S20` moves ≥ 20 % | **PASS** — +168.5 %; **direction was not predicted and is reported as measured: WORSE** |
| **`P5`** | at least one arm dies differently | **PASS** — arm 1 `rc = 0` at 148, arm 2 `rc = 134` at 53 |

**`P1` FAILED AND I STATE IT PLAINLY: I PREDICTED THE SCHEME LEVER WOULD DO NOTHING AND IT DID
SOMETHING.** Making the implicit energy convection first order pushes the first breach of the
generous ceiling from iteration **19 to 53** — 2.8× later, past the registered MITIGATED
boundary of 38 — and drops `S20` by 15.6 %. **The supervisor's downgrade of this candidate
was a reading of a dictionary; this is a measurement, and it disagrees with the prediction I
built on that reading.** The dictionary reading itself is not impeached (§5) — what is
impeached is my inference that a weak candidate would be an inert one.

**`P4` PASSED IN THE DIRECTION I DECLINED TO PREDICT, AND THAT IS THE SHARPEST RESULT HERE.**
Relaxing `rho` from 0.05 to 0.3 — matching `p`, the change the commissioning triage thought
worth trying — **makes the run dramatically worse**: `S20` rises from 3.28 to **8.81**, the
generous ceiling is breached at iteration **9** instead of 19, and the abort arrives at
iteration **53** instead of 148 with `T = −124.6 K` instead of `−2.4 K`. **The heavy `rho`
under-relaxation was not causing the excursion; it was holding the run together.**

## 4. WHAT IS AND IS NOT ESTABLISHED

**ESTABLISHED, and this is the load-bearing sentence: NEITHER LEVER REMOVES THE EXCURSION.**
All three arms leave the flow's own stagnation-enthalpy ceiling. Arm 0 at iteration 19, arm 1
at 53, arm 2 at 9. **`REMOVED` was reachable under the frozen rule and no arm reached it.**

**ESTABLISHED: the two levers are ASYMMETRIC.** One materially delays the excursion, the other
materially accelerates it. The registered classifications are `MITIGATED` and `EXONERATED`
respectively, and neither is `REMOVED`.

**A READING BEYOND THE REGISTERED RULE, OFFERED AS SUCH AND NOT AS A REGISTERED OUTCOME.**
`bounded Gauss upwind` is the most diffusive treatment available for that term, and under it
**`T_max` still reaches 431.557 K — 99.2 K past `T0`, 3.07 times the entire dynamic temperature
of the flow** — and `T_min` still reaches 221.975 K, implying a local Mach of **1.556**. A
lever that delays a departure by 34 iterations while the field still ends 99 K outside physics
has not been shown to be the thing that causes it. **This is a reading, it is not the
registered classification, and it does not name any other candidate.**

**NOT ESTABLISHED, and stated as absent rather than guessed:**

- **The mechanism.** Open. No claim made, and none follows from two levers behaving differently.
- **Whether arm 1 would abort past iteration 148. UNMEASURED.** The registered window ends at
  exactly 148 and nothing was run beyond it.
- Whether the wake is causal. Not addressed by this probe.
- Whether a finer mesh changes any of this. Not addressed by this probe.

### 4.1 **ARM 1's `rc = 0` IS NOT SURVIVAL, AND IT MUST NOT BE READ AS ONE**

Arm 1 **reached the end of the registered 148-iteration observation window without aborting.**
It did **not** converge and it did **not** stop of its own accord:

- `SIMPLE solution converged` **does not appear** in its log;
- it stopped at `Time = 148`, which is **the `endTime` this lane registered**, chosen to match
  the control's abort iteration and for no physical reason;
- its minimum first-solve `p` residual over the whole run is **6.984446e-04**, three orders of
  magnitude above the case's own `residualControl` of `1e-06`, and at the last iterations it
  oscillates between ~7.7e-02 and ~4.4e-03;
- **its `T_max` was deteriorating again at the end of the window**: 343.070 at iteration 100,
  **431.557 at iteration 148.**

**`rc = 0` here means "reached the iteration count I chose", not "healthy".**

### 4.2 A FINDING ABOUT THE COMPLETION RULE ITSELF, WORTH MORE THAN EITHER ARM

**Arm 1 satisfies EVERY limb of standing rule 4** — `rc = 0`; an `End` line; last written time
`148` == `endTime` `148`; `ExecutionTime` count `148` == `endTime`; all fields present at the
last time (11 of them). **And its solution is 99.2 K — 3.07 dynamic temperatures — outside the
flow's own adiabatic stagnation-enthalpy ceiling, with a `T_min` implying a local Mach of
1.556 in a freestream-0.734 flow.**

**Standing rule 4's completion limbs do not detect a non-physical solution, and on this case
they all hold on one.** That is not a criticism of rule 4, which was written to catch truncated
and stale runs and does catch them. It is the observation that **completion and physical
admissibility are independent**, and that a physical-bounds monitor of the kind
`F12_CRASH_TRIAGE_ROUND2` §4 called for would have refused arm 1 at iteration **53** — with a
reason — while every completion limb reported success. **Recorded for the verification team's
attention; no standard is retired or amended here, which is not this lane's call.**

## 5. THE `div(phi,e)` DICTIONARY READING — THE SUPERVISOR IS CONFIRMED, INDEPENDENTLY

Read from the case's own `system/fvSchemes` by this lane: `gradSchemes` contains an entry
literally named `limited`, reading `cellLimited Gauss linear 1`. `linearUpwind`'s second token
is a **gradient-scheme name looked up in `gradSchemes`**, so `bounded Gauss linearUpwind
limited` resolves that gradient to `cellLimited Gauss linear 1` — the most restrictive form —
and `bounded` is applied. **The supervisor's correction of the terminal-departure probe's
phrasing is confirmed: `limited` there is not a flux limiter.**

**A registered scope limit that survives the result and must be quoted with it.** The
`fvSchemes` entry `energy` is also referenced by `div(phi,K)` and `div(phi,Ekp)`. Arm 1 changed
`div(phi,e)` **only**, as commissioned, so the *explicit* `fvc::div(phi, Ekp)` term in
`EEqn.H` remained `bounded Gauss linearUpwind limited` throughout. **What arm 1 measures is the
implicit energy convection scheme, not second-order energy transport in general.**

## 6. COMPLETION — REPORTED, NEVER CLAIMED (standing rule 4)

| limb | arm 0 | arm 1 | arm 2 |
| --- | --- | --- | --- |
| `rc = 0` | no (134) | **yes** | no (134) |
| `End` line present | no | **yes** | no |
| last written time == `endTime` 148 | no (147) | **yes (148)** | no (52) |
| `ExecutionTime` count == 148 | no (147) | **yes** | no (52) |
| fields present at last time | 9 | 11 | 9 |
| **all limbs hold** | **no** | **yes** | **no** |

**No completed run is claimed from any arm**, including arm 1 — see §4.1 and §4.2. This probe
grades nothing and produces no verdict. **A crash or a bounded stop here is `NOT A RESULT`,
never `GATE FAIL`**; no gate was read at all, and standing rule 5 may only turn a `PASS` or a
`GATE FAIL` **into** `NOT A RESULT`, never the reverse.

## 7. COST — ESTIMATE VERSUS ACTUAL (standing rule 12, Sanaa's directive 2026-08-23)

| item | figure | artifact |
| --- | --- | --- |
| Registered cap (RUNAWAY GUARD, freeze §8) | **10 core-min**, 1 rank | freeze §8 |
| **Predicted** (freeze §8) | **1.31 core-min** | freeze §8 |
| arm 0 solver, **measured** | 27.861256 s ÷ 60 = **0.464354 core-min** | `evidence/arm0/WALL_S.txt` |
| arm 1 solver, **measured** | 29.923741 s ÷ 60 = **0.498729 core-min** | `evidence/arm1/WALL_S.txt` |
| arm 2 solver, **measured** | 11.222970 s ÷ 60 = **0.187050 core-min** | `evidence/arm2/WALL_S.txt` |
| readers, 3 passes, **measured** | (0.660297 + 1.157762 + 1.908252) s ÷ 60 = **0.062105 core-min** | `evidence/WALL_S_reader_*.txt` |
| **MEASURED TOTAL, GROSS** | **1.212238 core-min — 12.1 % of cap. NOT BREACHED.** | |
| **Ratio actual/predicted** | **0.9254×** | |
| Dollars, **DERIVED NOT MEASURED** | **$0.001036** at $0.0513/core-h (owner-stated; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) | |
| disk, transient, outside git | 1.6 GB across three arms | |

**Gap attribution.** A **0.93× ratio on a 1.31 core-min prediction** — the closest calibration
this line has produced, and the reason is named so it can be repeated: **the solver line was
priced from a MEASUREMENT of the identical workload** (the terminal-departure probe's 0.422230
core-min for 148 iterations, 147 ascii writes, 23,040 cells, 1 rank), applying that probe's own
calibration lesson rather than re-learning it. The residual gap is two-sided and small: arms 0
and 1 ran **10–18 % slower** than that measurement under live contention from three
heat-transfer solvers and two peer cfd lanes (load 3.67–4.0 at launch, `evidence/*/CONTENTION_*`),
while **arm 2 came in 56 % under** because it aborted at iteration 53 and never ran the other 95
iterations. The reader was priced at 0.030 and cost 0.062 — a 2.1× under-price, caused by three
passes rather than the one assumed, of which one was the `ADDENDUM 1` defect.

**WASTE, NAMED SEPARATELY AND NOT ABSORBED INTO THE RATIO** (`COMPUTE_BUDGET_CHARTER.md` §6):
**0.011005 core-min** — reader pass 1 (0.660297 s), which returned `P0 FAIL` on a check that
could not have passed and produced no reading any later pass did not produce. **Attributable to
this lane's own transcription defect, disclosed in `ADDENDUM 1`.** Reader pass 2 is **not**
waste: it verified `P0` on arm 0 **before arms 1 and 2 were composed**, which is the freeze's
control-first discipline and required work. **Cleaned total: 1.201233 core-min.**

## 8. ARTIFACTS

| what | path |
| --- | --- |
| pre-registration (frozen body `54acad46`, `ADDENDUM 1` `e46d844c`) | `verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md` |
| runner (and the arm-0 version preserved for the diff) | `run_arms.sh`, `run_arms_ARM0_VERSION_PRESERVED.sh` |
| reader (and the pre-repair version preserved for the diff) | `readers/analyse_discriminator.py`, `readers/analyse_discriminator_FIRSTPASS_PRESERVED.py` |
| all readings, controls, predictions | `evidence/discriminator.json` |
| the preserved failing first pass | `evidence/discriminator_P0FAIL_FIRSTPASS_PRESERVED.json` |
| per-arm solver logs | `evidence/arm{0,1,2}/log.rhoSimpleFoam` |
| per-arm `rc`, wall, contention, UTC bounds | `evidence/arm{0,1,2}/{RC,WALL_S,CONTENTION_at_launch,CONTENTION_at_end,START_UTC,END_UTC}.txt` |
| per-arm case identity and the single-line lever diff | `evidence/arm{0,1,2}/{case_identity_18.txt,lever_THE_ENTIRE_DELTA.diff,controlDict_delta.diff}` |
| rung-1 fingerprint, before and after every arm | `evidence/rung1_fingerprint_before.txt`, `evidence/arm{0,1,2}/rung1_fingerprint_after.txt` |
| freeze verification at each launch | `evidence/freeze_verified.txt` |
| transient time directories (outside git, 1.6 GB) | `/home/ubuntu/certonomous-runs/f12_energy_bound_discriminator_2026-08-25/arm{0,1,2}/case/` |

**Every log path above is matched by `.gitignore` lines 260–266
(`verification/runs/*_runs/**/log.*`) and was landed by explicit `git update-index --add`,
asserted present in `git diff-tree --stat` before `commit-tree` and confirmed with
`git cat-file -e HEAD:<path>` after.**
