# JF1E RUNG E2a — GRADING RECORD

**Rung:** E2a — turbulence-equation relaxation `k` and `omega` `0.7 -> 0.5`, the ONE
change from E1. Continuation seeding, `fvSchemes`, `nNonOrthogonalCorrectors 1`, `U`
relaxation 0.7 and `p` relaxation 0.3 all inherited from E1 unchanged.

**Registration:** `verification/campaign/JF1E_TURBULENCE_STALL_ESCALATION_PREREGISTRATION.md`,
frozen `6e83157c`, blob `800944bc`. Verified at grading: the working-tree copy and the
blob at the freeze commit both hash to `800944bc` — **the frozen file is the file that
ran** (CLAUDE.md rule 2).

**Grading path:** `verification/runs/JF1_jet_flap/analyse_jf1_ladders.py`, landed
`74c4f5fb`, **byte-identical to HEAD at grading** (blob `ef4c0b0c`). Invoked as
`gateE --rung E2a`. Its self-test ran first and **passed**, including the §4 planted
control: the `bounding k` reader returned **494** on `JF1_L1_BLOWN_CMU010_A0` (required
494 exactly) and **0** on the same log with every `bounding k` line deleted.

**LABEL: `numerics-diagnostic`.** No physics verdict, no lift claim, no observed order,
no GCI, no band comes off this rung (registration §0).

**CAVEAT D-1, carried:** no run in this chain was seeded from a converged field. The
seed is the final field of a stationary-but-clipping-held run. Nothing here may call
the seed converged.

---

## 1. RUNG VERDICT

**RUNG E2a: `GATE FAIL` — escalate to the next rung in the frozen order.**

All four rows completed (rc = 0, `End`, last time == `endTime` == 8000, `ExecutionTime`
count 8000, fields `U p k omega nut` present at 8000 and every one newer than the case's
own `0/`). **Clause E-6 is satisfied on all four rows**, so the rung is `GATE FAIL`, not
`NOT A RESULT`.

Chain launched `2026-09-01T18:15:07Z`, closed `2026-09-01T19:34:34Z`, driver rc = 0.

## 2. PER-ROW, AS THE COMPARATOR GRADED IT

Windows: `bounding k` / `bounding omega` counted over the **final 500 iterations**
(7501–8000); residuals at `endTime`.

| row | verdict | `bounding k` /500 | `bounding omega` /500 | res k | res omega | res p | CL |
|---|---|---|---|---|---|---|---|
| CMU005 | **GATE FAIL** | 20 | 100 | 1.725e-06 | 7.007e-09 | 1.003e-07 | 0.40591345 |
| CMU010 | **GATE FAIL** | 57 | 100 | 5.834e-06 | 8.188e-09 | 1.391e-07 | 0.55011703 |
| CMU020 | **GATE FAIL** | 104 | 83 | 9.215e-06 | 1.157e-08 | 2.659e-07 | 0.74415906 |
| CMU040 | **GATE FAIL** | 139 | 83 | 2.256e-05 | 3.667e-08 | 4.497e-07 | 1.00999182 |

**Clause by clause:** E-1 (`bounding k` == 0) **FAILS on all four**. E-2 (`bounding
omega` == 0) **FAILS on all four**. E-3 (res k < 1e-6) **FAILS on all four**. E-4 (res
omega < 1e-6) passes on all four. E-6 passes on all four. E-5 as the comparator
evaluates it passes on all four — **see §5, where that reading does not survive
inspection.**

## 3. COST — CLAUDE.md RULE 12

Serial (`ranks = 1`) throughout, so core-min == wall-min. Each figure read from that
row's own `RUN_STATUS.<case_id>.txt`.

| row | wall s | **core-min MEASURED** | **$ DERIVED, NOT MEASURED** |
|---|---|---|---|
| CMU005 | 1267 | **21.1167** | $0.018055 |
| CMU010 | 1196 | **19.9333** | $0.017043 |
| CMU020 | 1010 | **16.8333** | $0.014392 |
| CMU040 | 1294 | **21.5667** | $0.018440 |
| **rung** | **4767** | **79.4500** | **$0.067930** |

Registered estimate **94.0 core-min**, registered cap **150**. Actual **79.4500** —
**0.845x the estimate, 53 % of the cap.** No cap struck; no row approached its 40.0
per-link wrapper cap (highest 21.5667, 54 %). **Waste: 0 core-min** — four links, four
completed solves, no re-run, no stall (longest row 1294 wall s, far below the
`COMPUTE_BUDGET_CHARTER` §2 3600-s rule), and chain elapsed wall (79.45 min) equals the
sum of the four link walls exactly, so **zero inter-link dead time**.

**Every dollar figure above is DERIVED at the recorded `c7a.4xlarge` rate of
$0.0513/core-h and is NOT MEASURED — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).**

## 4. L-235 IS BINDING ON THIS READING — THE CL COLUMN IS NOT EVIDENCE OF CONVERGENCE

**`k` is still clipping through the final iteration on all four rows.** E2a's final-500
`bounding k` counts are **20 / 57 / 104 / 139**, against E1's **415 / 495 / 466 / 481**
over the same window. Every one of those counts is a count of distinct iterations, so on
CMU040, 139 of the last 500 iterations bound `k`.

The CL column agrees closely with E1's — CMU040 1.00999182 against E1's 1.00997154, a
2.0e-05 difference; CMU005 0.40591345 against 0.40571058 — and **that agreement may not
be reported as convergence.** CL peak-to-peak over the final 2000 iterations is
1.07e-06 / 4.95e-06 / 4.44e-07 / 3.40e-06 — a settle test on CL alone would call all
four converged, and the reason CL stopped moving is not that the solve converged. That
is L-235 exactly, and it is why E-1 and E-2 are load-bearing clauses.

**What the early window did versus what the gate window did.** The pre-gate signal was
real but did not survive to the gate. Whole-run and windowed `bounding k`:

| | first 2563 it. | middle | **final 500 (THE GATE WINDOW)** | whole run |
|---|---|---|---|---|
| E1 CMU005 | 2163 | 4068 | **415** | 6646 |
| E2a CMU005 | 87 | 168 | **20** | 275 |
| E1 CMU010 | 2504 | 4898 | **495** | 7897 |
| E2a CMU010 | 257 | 505 | **57** | 819 |
| E1 CMU020 | 2397 | 4564 | **466** | 7427 |
| E2a CMU020 | 423 | 826 | **104** | 1353 |
| E1 CMU040 | 2480 | 4801 | **481** | 7762 |
| E2a CMU040 | 731 | 1507 | **139** | 2377 |

The early signal was **87 against 1099** as reported at the time on a partial log, and
against E1's completed log the first-2563 comparison is **87 against 2163, a 24.9x
reduction**. Whole-run clipping fell **24.2x / 9.6x / 5.5x / 3.3x**. **None of that is
the gate.** The gate reads the final 500, where the reduction is **20.8x / 8.7x / 4.5x
/ 3.5x — large, and still not zero.** E1's first link also looked far better early and
ended at 415/500; E2a's ends at 20/500. The direction is unambiguous and the threshold
is unmet. **A reduction is not a clearance, and the frozen threshold is zero.**

## 5. TWO DEFECTS IN THE GRADING PATH, FOUND AT GRADING — NEITHER MOVES THIS VERDICT

Reported here rather than repaired: the grading path is fixed at the pre-registration
commit (rule 2) and a lane does not amend it. **Both defects are conservative in the
wrong direction — they make the solve look MORE converged than it is — and neither
changes E2a's `GATE FAIL`,** because E-1, E-2 and E-3 fail on all four rows under any
reading.

**D-E2a-1 — clause E-5 is evaluated on `p` alone; `Ux` and `Uy` are never read.** The
frozen clause names *"initial residual of `Ux`, `Uy` and `p` at `endTime` < 1e-6"*. The
comparator's gate expression tests `bk`, `bo`, `rk`, `ro` and `rp` only. Measured from
the logs, **`Uy` misses 1e-6 on three of the four E2a rows** (1.082e-06, 1.792e-06,
3.796e-06 for CMU010/020/040) and **`Ux` misses on CMU040** (1.282e-06).

**D-E2a-2 — the `p` residual read is not the one `residualControl` uses.** The
comparator takes the LAST `Solving for p` match, documenting the claim that for `p` this
is *"the value the SIMPLE residualControl itself reads"*. Against the source on this box
(`/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/general/solutionControl/`),
`simpleControl::criteriaSatisfied()` tests `maxResidual(entry).first()`, and
`solutionControl.H` documents that as *"the **maximum** residual for the specified
field … initial residual as first member"* — i.e. the **maximum initial residual over
all solves of that field in the iteration**. With `nNonOrthogonalCorrectors 1`, `p` is
solved twice; the maximum is the first corrector, not the last. Measured maxima at
`endTime`: **2.056e-06 / 3.816e-06 / 7.124e-06 / 1.297e-05** — against the comparator's
1.003e-07 / 1.391e-07 / 2.659e-07 / 4.497e-07, **a factor of 20 to 29.**

**Consequence for the reading, and it is not cosmetic.** Under the corrected reading
**`p` misses its 1e-6 criterion on all four E2a rows**, and E1's rows miss on `Uy` and
`p` throughout with `Ux` missing on CMU040 as well. So the stall is **not** confined to
the turbulence pair. Any successor that reads registration §1 as saying the
momentum/pressure side is essentially converged and only `k` is stuck would be wrong on
this evidence. Recorded so it is falsifiable rather than inherited.

## 6. THE STANDING PREDICTION, SCORED

Before E2a ran, a lane recorded a free, falsifiable forecast from a `k_min` diagnostic
(worst **-2.14e-03** against a mean `k` of **1.33e-01**, a 1.6 % undershoot, decaying
only weakly and barely moved by continuation): **that E2a would NOT clear the stall, and
that E2c — `limitedLinear 1 -> 0.5` — is the likelier fix.**

**The first limb HELD. E2a is `GATE FAIL`; it did not clear the stall.**

**Nothing beyond that limb is claimed.** The second limb — that E2c is the likelier fix
— **is not scored by this rung and remains untested.** E2a's failure is consistent with
it and is not evidence for it: E2b has not run, and §5 above shows the residual stall
extends to `p` and `Uy`, which is not the signal the `k_min` shape was read from. The
prediction is recorded as **half-scored: limb 1 correct, limb 2 open.**

## 7. THE E4 TRIGGER, READ AND REPORTED

Registration §5 fires E4 on a row whose CL peak-to-peak over its final 2000 iterations
exceeds **1.0e-03**. Measured on E2a: **1.073e-06 / 4.949e-06 / 4.438e-07 / 3.403e-06**.
**The trigger does not fire on any row** — as it did not on E0 or E1.

## 8. WHAT COMES NEXT — REGISTERED, NOT CHOSEN

The frozen order of registration §3 puts **E2b** next: **`nNonOrthogonalCorrectors 1 ->
2`**, applied to the same four rows at `endTime` 8000. Registration §6 prices E2b at
**141.0 core-min** (≈ +50 % on `p` for the second corrector) against a **registered cap
of 220** — **$0.1206 derived** at $0.0513/core-h, derived and not measured. E2c
(`limitedLinear 1 -> 0.5`) follows E2b, at 94.0 core-min, cap 150.

**This record states the frozen order; it does not choose it, and it does not reorder
it.** Reordering after first compute is a registered refusal (§7 item 6).

**NO COMPUTE WAS AUTHORISED FOR THIS TASK AND NONE WAS RUN.** E2b is **not** launched by
this record.

**SUBMISSIONS PARKED.** Nothing in or derived from this document is sent, filed,
uploaded, posted or registered outside this box.
