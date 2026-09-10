# D6RF10 — GRADE RECORD — A2-wing convergence probe `P_conv`

**Item:** D6RF10 (confound-removal successor to D6RF9 `NOT A RESULT | CONFOUNDED`)
**Frozen pre-registration:** `PREREGISTRATION.md` in this directory, FROZEN 2026-09-09; launcher
`PERMISSION` re-frozen at `19c0fd8c` (after the R4-strike `2fd18eff`).
**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF10-a2-wing-convergence-probe/`
**Graded:** 2026-09-10T05:49:31Z by the committed detached autograder; **verified first-hand by the
dafoam-supervisor 2026-09-10T15:4xZ** (this record). Recorded `[lab-attributed]` under the owner's
2026-09-10T03:45Z directive that each supervisor decides its own team's priorities.
**SUBMISSIONS PARKED** — nothing here is filed, sent or posted anywhere (CLAUDE.md rule 7).

---

## 0. THE ONE-LINE ANSWER, AND WHY IT IS TWO CLAUSES AND NOT ONE

**R3 (SIMPLEC) is the first lever in the D6RF7 → D6RF9 → D6RF10 chain to drive the registered binding
field `p_first_uncorrected` BELOW the 1.0e-05 accept floor with a MEASURED plateau — and R3 is still
not a clean rung PASS, because `nuTilda` remains 1.392x that same floor.**

Both clauses are registered rules of this item and the frozen grader emits both:
`"binding_verdict": "PASS"` and `"verdict": "GATE FAIL"` in the same
`R3_autograde.json`. Anyone who quotes one without the other is misreporting D6RF10.

**And DAFoam itself sides with the second clause.** The R3 candidate leg ends with the solver's own
banner (`R3_20260910T031209Z_953457.log:2711-2714`):

    Primal min residual 1.391750109e-05
    did not satisfy the prescribed tolerance 1e-08
    Primal solution failed!

`1.391750109e-05` is **byte-identical to the `nuTilda initRes` printed on line 2703 of the same log.**
So the figure DAFoam calls its "Primal min residual" is, on this evidence, the **WORST across the
transported-equation set, not a minimum** — the same "worst-across-fields" structure the open
GATE-R-level referral (`docs/dafoam/REFERRAL_TO_VERIFICATION_A2_GC_P_GATE_R_LEVEL_2026-09-10.md`,
`c5f97bd9`) asks verification to rule on. That referral is now **not a bookkeeping question**: see §5.

---

## 1. INSTRUMENT IDENTITY — verified first-hand, not relayed

| instrument | md5 on disk | md5 of the HEAD blob | result |
|---|---|---|---|
| `d6rf10_grade.py` | `0cb9d89a11347bc943acf3b38e1766d2` | `0cb9d89a11347bc943acf3b38e1766d2` | **MATCH** |

`git log -- cases/dafoam/ladder-a/A2/curriculum_D6RF10/` has its most recent entry at `19c0fd8c`
(the re-freeze), and `git status --porcelain` on that directory is **empty**, so the HEAD blob **is**
the frozen blob and the file that ran **is** the file that was frozen (rule 2, last clause).
`D6RF10_AUTOGRADE_DONE.txt:2` independently records the same md5 and the invocation
`--log <log> --rung <Rn>` with **no `--skip-freeze`**.

**Both planted controls EXERCISED-PASS on every graded rung** (rule 3):
- `planted_residual`: baseline first `initRes` `1.62e-05`, plant `1.234000e-03`, read back
  `1.234000e-03`, `reader_saw_the_plant: true`, `original_unchanged: true`.
- `accept_floor_unmoved`: plant `1e12` at 6 sites, `reader_saw_the_plant: true` for both the `all`
  and `last` plant variants; read `primalMinResTol 1e-08`, `primalMinResTolDiff 1000`,
  `accept_floor 1e-05` — **unmoved in both directions** (a tightened floor refuses too).

---

## 2. THE LADDER AS IT ACTUALLY RAN — from `ledger.txt`, read first-hand

    D6RF10_RUNG_GRADED rung=R1 binding_verdict=GATE FAIL
    D6RF10_RUNG_GRADED rung=R2 binding_verdict=NOT A RESULT
    D6RF10_RUNG_GRADED rung=R3 binding_verdict=PASS
    D6RF10_LADDER_STOP rung=R3 reason=binding_PASS
    D6RF10_LADDER_DONE verdict=STOPPED_AT_FIRST_PASS_R3 cumulative_core_min=759.667 hard_stop=1275

R4 was struck from the runnable loop at `2fd18eff` and was never reachable under
`STOPPED_AT_FIRST_PASS`.

**The container is gone because the run FINISHED, not because it was cut.** R3's candidate leg reads
`rc=0`, `wall_s=9264` against a registered deadline of `16905 s` (54.8% used) and `617.6 core-min`
against a cap of `1133` (54.5% used), and `d6rf10_autograde.out` records
`TERMINATION seen (D6RF10_LADDER_DONE) 2026-09-10T05:49:31Z / AUTOGRADE_COMPLETE ... graded=3
any_pass=1`. The chief's session-start reading that R3's fate was UNKNOWN is now **resolved by
artifact: R3 completed to its registered `endTime` 2000 and was graded by the frozen instrument.**

---

## 3. R1 — `GATE FAIL`

- `endTime` 2500, `DARhoSimpleFoam`, `nNonOrth 3`, `relax_p 0.30`, `relax_eqn 0.70`;
  `config_as_registered: true`. `rc=0`, complete.
- **`p_first_uncorrected` = `1.681236312e-05` = 1.681x the `1.0e-05` floor → `GATE FAIL`.**
- `nuTilda` = `1.359027843e-05` = 1.359x → also fails. `U0`/`U1`/`U2`/`he`/`p_corrected` all PASS.
- Plateau layer: `GATE FAIL` — "binding field >= accept floor; the plateau layer does not manufacture
  a PASS (rule 5)". Late window [1500, 2000], 6 samples, `state: READ`.
- **Prediction P1 ("extended horizon predicted INSUFFICIENT") is CONFIRMED**, and it reproduces
  D6RF7/D6RF9's `1.6255e-05` to within 3.4%.
- Cost: candidate 20.733 + control 10.067 = **30.8 core-min**.

## 4. R2 — `NOT A RESULT`, and the reason is a DEADLINE ~4% SHORT, not physics and not either D6RF9 confound

- `endTime` 300 (AMENDMENT A3), `DARhoSimpleFoam`, `nNonOrth 12`, `relax_p 0.30`.
- `rc=124`, `wall_s=1357` against the §2bb deadline `1350 s`. **Killed by its own deadline.**
- The frozen grader returns `verdict: NOT A RESULT`, `reason: CONFIG_NOT_AS_REGISTERED`,
  `final_time: 0`, `reasons: ["nNonOrthogonalCorrectors read None != registered 12"]`.
  **That label is correct and conservative (rule 5) — and its stated reason is true about the
  READBACK while being misleading about the CAUSE.** The leg's own
  `config_install_marker` reads `endTime 300, nNonOrth 12, relax_p 0.30` — i.e. the registered config
  **was** installed. What is absent is a *completed final outer iteration* for the grader to read the
  corrector count back from. The grader is frozen and is **not edited**; the discrepancy is recorded
  here (rule 6).
- **How close it got, measured then extrapolated, and the extrapolation is labelled.** The candidate
  segment prints at `printInterval 100`: `Time=1 ExecutionTime=4.48 s`, `Time=100 155.54 s`,
  `Time=200 712.11 s` — i.e. **1.526 s/step over 1→100 and 5.566 s/step over 100→200**, reproducing
  D6RF9's escalation signature. Leg wall 1357 s minus ~93 s of setup leaves ~1264 s of solver time,
  so at its own last-measured rate R2 died at **`Time` ≈ 292–299 of a registered 300** (range, not a
  point: the rate was still rising, and `printInterval 100` hides the last 99 steps entirely).
  **Completing R2 needed roughly 1400 wall s. The deadline was 1350. It was short by about 4%.**
- **Prediction P2 — "the load-bearing rung, outcome GENUINELY UNCERTAIN" — remains UNMEASURED for the
  third campaign running** (D6RF7 never tried it; D6RF9 confound (i); D6RF10 a short deadline).
- Cost: candidate 90.467 + control 10.733 = **101.2 core-min**, of which the **90.467 core-min
  candidate is WASTE** — it bought no gradeable value. Named separately, never absorbed
  (`COMPUTE_BUDGET_CHARTER.md` §6).
- **INSTRUMENT LESSON, recorded for the successor:** a `printInterval` of 100 on a rung whose
  registered `endTime` is 300 yields three samples and makes "how far did it get" unanswerable from
  the artifact. A rung graded at its endTime needs a print interval that resolves its own deadline.

## 5. R3 — binding field `PASS`; rung `GATE FAIL`. Both, or it is not this item's result.

- `endTime` 2000, **`DARhoSimpleCFoam` (SIMPLEC)**, `nNonOrth 12`, `relax_p 0.70`, `relax_eqn 0.70`.
  `rc=0`, complete to `endTime`. `config_as_registered: true`, with `nNonOrth` **counted back as 12
  from the p-solve count**, not merely read from a marker.
  **This closes §8's honest gap "R3's SIMPLEC *activity* is not confirmed at freeze" BY MEASUREMENT.**
- **AMENDMENT A2's registered two-part PASS criterion, on the registered binding field — BOTH met:**
  1. Below floor: `p_first_uncorrected(2000)` = **`6.3233727e-06`** = **0.632x** the `1.0e-05` floor.
  2. Plateaued: late window [1500, 2000], **6 samples** (min 5 required), relative spread
     `(max-min)/mean` = **`1.4707e-07` = 1.4707e-05 %** against the registered ceiling **0.31%** —
     inside it by four orders of magnitude. Samples: T1500 `6.323372182e-06`, T1600 `6.323372445e-06`,
     T1700 `6.323372351e-06`, T1800 `6.323372173e-06`, and the window min/max
     `6.32337177e-06`/`6.3233727e-06`.
     → grader `plateau_check.verdict: PASS`, `binding_verdict: PASS`.
- **AND the registered §1 leg rule is NOT met.** §1: *"a leg is `PASS` only if every field is"*.
  **`nuTilda initRes` = `1.391750109e-05` = 1.392x the floor → per-field `GATE FAIL`**, so the frozen
  grader's leg `verdict` is **`GATE FAIL`**. `U0` `2.033930036e-07`, `U1` `7.651718366e-07`,
  `U2` `5.524911988e-08`, `he` `9.903640785e-09`, `p_corrected` `9.789387471e-11` all PASS.
- **DAFoam's own acceptance agrees with the leg rule** (§0): its banner reports the `nuTilda` figure
  and declares `Primal solution failed!`. The solver does not accept this run either.
- **P3's CD/CL clause (registered as REPORTED, never gated) is REFUTED as stated.** Predicted
  "CD/CL shift ~0" between SIMPLE and SIMPLEC at the same fixed point. Measured, candidate legs:
  R1 `CD 0.01849343377`, `CL 0.3992825152`; R3 `CD 0.01859195417`, `CL 0.3990844547`.
  **ΔCD = +9.85204e-05 = +0.5327%; ΔCL = -1.980605e-04 = -0.0496%.** The CD shift is half a percent —
  larger than the 0.5% figure A2's sibling items use as a tolerance elsewhere. **The most likely
  reading, stated as a reading and not a measurement: R1 is NOT converged on the binding field
  (1.681e-05) while R3 is (6.32e-06), so the gap is most plausibly R1's distance from the fixed point
  rather than two different fixed points.** Distinguishing those requires a converged SIMPLE leg,
  which this item does not have. Changes no verdict.
- **Reproducibility datum worth keeping:** the R3 control leg's `p_first_uncorrected` is
  `1.681172924e-05`, **byte-identical to the R1 control leg's** value measured 2.5 hours earlier on a
  differently-loaded box. The control reproduces to ten significant digits.
- Cost: candidate 617.6 + control 10.067 = **627.667 core-min**.

## 6. THE COST MODEL — §8's "single largest cost uncertainty" is now MEASURED, and the registered upper model is REFUTED

§8 recorded as UNKNOWN "whether R2's per-step cost plateaus or keeps rising past ~step 250", and §5
bracketed every non-R1 rung between a QUADRATIC upper and a PLATEAU lower model. **R3 ran 2000 steps
and answers it: the per-step cost PLATEAUS.** From the R3 candidate's 21 `ExecutionTime` samples:

| interval | s/step |
|---|---|
| 1 → 100 | 2.176 |
| 100 → 200 | 5.374 |
| 200 → 300 | 5.049 |
| **300 → 2000** | **4.650** |
| 1900 → 2000 | 4.365 |

**The escalation is confined to roughly the first 300 outer iterations and then settles at ~4.65
s/step, mildly DECREASING at the end.** The quadratic "upper" model (which priced R4 at ~14,600
core-min and R2 at ~3,665) is **falsified by measurement**; the plateau model is the right one, and
its constant is **4.650 s/step, not the 4.138 s/step §5 assumed** (+12.4%).
**Mechanism, measured:** in the R3 candidate, **157 of 273 p-solves saturate the linear solver's
`nIters: 1000` cap** with `finalRes` stalling at ~1.5e-11 — the deep corrector loop's cost is
dominated by a linear p-solve that burns its iteration cap once `initRes` falls near 1e-8, not by the
outer loop. R1, at `nNonOrth 3`, shows none of this and runs flat at **0.117 s/step** end to end
(4.07 s at `Time=1` → 293.66 s at `Time=2500`).

## 7. WHERE THE ITEM LANDS AGAINST ITS OWN REGISTERED TERMINAL STATES — neither, and that is the honest answer

**P5** registered a ladder-level `CAPABILITY FINDING` (which would put the N-D43 acceptance-rule
question on Sanaa's desk) **only if** all rungs were MEASURED and **none** reached the floor. Here:
- R3's binding field **did** reach the floor, so the ladder did **not** measure-exhaust; and
- R2 is **still unmeasured**, so the ladder has not exhausted anything either.

**D6RF10 therefore lands in NEITHER registered terminal state, and the lab does not get to pick one.**
What it has produced is a genuine positive on the binding field plus an unresolved leg-level fail on
`nuTilda`, and the question of which of those is "the" verdict is exactly the question already sitting
with verification in the GATE-R-level referral. **No acceptance rule is widened here, under any
outcome (T25).** `N-D43` stays escalated and unruled.

## 8. TWO-ROW RULE (`DAFOAM_CHARTER.md` §6) — one row bought, and the charter's bright line stated plainly

- Row **BOUGHT**: **`PATCHED`** — patched IDWarp image, digest `sha256:2927768a…30f6d35`, the same
  image D6RF7 and D6RF9 bought.
- Row **NOT BOUGHT**: **`SHIPPED`**, **priced anyway at 155.70 core-min** as §6 registered.
- **So D6RF10 is a ONE-ROW measurement on the patched image, and under the charter's bright line it is
  NOT a DAFoam verdict.** It is a primal-convergence measurement that a DAFoam verdict would rest on.
  No adjoint gradient is claimed here, so no finite-difference table is owed — and equally, nothing
  here may be quoted as a DAFoam result. The `SHIPPED` row stays priced so a successor can buy it.

## 9. WHAT I COULD NOT VERIFY

- **Whether R2 would have passed or failed its gate is unknown and unknowable from these artifacts.**
  It died 1–8 outer iterations short and printed no residual block after `Time=200`.
- **How much of R3's 1.372x cost overrun is contention versus misprediction is NOT separable** from
  what is on disk. R3 ran 03:12→05:47Z on a box the S-147 board stamp read at load 24.99 with twelve
  foreign solvers alive. Stated as unattributed rather than split by guess.
- **Whether SIMPLE and SIMPLEC share a fixed point on this case to better than 0.5% in CD** — see §5;
  it needs a converged SIMPLE leg this item does not have.
- **Whether DAFoam's "Primal min residual" is defined as the worst across transported equations** is
  supported here by one byte-identical match on one log, not by reading DAFoam's source. A lane is
  establishing it from source; until then it is a **hypothesis with one strong datum**, not a fact.
