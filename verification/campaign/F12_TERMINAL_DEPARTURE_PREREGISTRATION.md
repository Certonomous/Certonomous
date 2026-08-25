# F12 — TERMINAL-DEPARTURE PROBE: PRE-REGISTRATION

**cfd lane, 2026-08-25. Registered and COMMITTED BEFORE the compute it covers.**
Commissioned by `verification/runs/F12_runs/RUNG2_DISPOSITION_AND_CRASH_TRIAGE_2026-08-25.md`
§3.4 and by its AMENDMENT 1 of the same date, which restated the falsifiable test without
the struck FPE mechanism.

**THIS PROBE GRADES NOTHING.** It moves no gate, threshold, band, cap or label. F12 rung 1
stands `NOT A RESULT`; rung 2 stands `BLOCKED` and its `rate_calibration_gate()` interlock is
**not touched, not read around and not edited**; rungs 3–5 remain unlaunched. No verdict from
the fixed vocabulary is due to this probe and none will be issued. Its output is a location,
an iteration number and a census.

---

## 0. WHY THIS ARM EXISTS, AND WHY IT IS NOT ANOTHER LEVER SWAP

The frozen field-localisation replication
(`verification/campaign/F12_FIELD_LOCALISATION_PREREGISTRATION.md`, blob
`0b6a5c59ff07`, hash-verified against disk by this lane before writing this line) answered
§3.4's question **for the first 15 iterations**: the field departs at iteration 1, anchored on
the aerofoil, and the boundaries are the last places to go.

It says, in its own §6, what it does **not** support:

> "does **not** explain the `T ≤ 0` abort at iteration 148 — that lies outside the registered
> window and, per the supervisor's Ruling 3, **needs its own registration and does not ride in
> on this freeze.**"

**This document is that registration.** It carries the same case, the same rank count and the
**same permitted delta class** — `system/controlDict` output controls and nothing else — out
to the iteration at which the registered rung 1 actually died. It swaps no solver, no scheme,
no relaxation factor, no tolerance, no `residualControl` entry, no corrector count, no
`pMinFactor`/`pMaxFactor`, no boundary condition and no initial value.

**What it deliberately does NOT do, and the reason is a ruling, not a preference.** The
supervisor's disposition §1 upheld the rung-2 interlock and recorded that *"an interlock that
can be edited when it fires is not an interlock"*. Two arms that would be more decisive than
this one — a potential-flow initialisation, and the same probe on the medium mesh — both
require either an initial-state change (outside the observation boundary §3.4 drew) or a
medium case built around the interlock. **Neither is taken here.** They are named in the
lane's report as candidates for the supervisor's decision, and this arm stays inside the
boundary already drawn.

## 1. THE QUESTIONS, STATED FALSIFIABLY AND FIXED NOW

Q1. **When.** At which iteration does the on-disk minimum of `T` first fall below each of
    **250 K, 200 K, 100 K and 0 K**? (Thresholds are a descending ladder ending at the
    solver's own range check, `thermoI.H:56-60`; they are not physical claims.)

Q2. **Where.** At each of those crossings, and at the last written time, what is the cell
    index of the `T` minimum, its centre coordinates, its radius `r` from the quarter chord
    `(0.25, 0, 0)`, and its nearest patch? Does the minimum **stay** at the trailing edge —
    where the 15-iteration arm measured it at `(0.995635, 0.001004)` at iteration 1 — or does
    it **migrate**?

Q3. **How much.** Per iteration over the whole run, the pre-clip `p` extremes from the
    solver's own `pressureControl:` print, and the on-disk count of cells outside the case's
    own registered bounds `[10132.5, 202650]` Pa (`pMinFactor 0.1`, `pMaxFactor 2` × `p_ref
    101325`). Does the limited fraction **saturate**, or recover?

Q4. **Whether it is the same death.** Does the run reproduce the registered rung 1's abort —
    same message, same iteration, same `T0`?

## 2. THE RUN — PHYSICS AND MESH UNCHANGED

Copy of `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/`, executed
**outside the repository** under `/home/ubuntu/certonomous-runs/f12_terminal_departure_2026-08-25/`.
**Ranks = 1**, which is what the registered rung 1 itself ran.

**The ONLY permitted delta is `system/controlDict` output controls:**
`endTime` 6000 → **148**; `writeControl timeStep` (already so); `writeInterval` 6000 → **1**;
`purgeWrite` 1 → **0**; `writeCompression off`.

**NOT changed, and asserted byte-identical before the run:** `system/fvSolution`,
`system/fvSchemes`, `system/blockMeshDict`, `system/decomposeParDict`, every `0/` field
(`T U p k omega nut alphat`), `constant/thermophysicalProperties`,
`constant/turbulenceProperties`, and all five `constant/polyMesh/` files. **18 files, byte-
compared, and the run ABORTS if any differs.**

**CHANGING ANYTHING ELSE VOIDS THIS PROBE.**

## 3. PRE-REGISTERED PREDICTIONS — THESE CAN FAIL

- **P1 — FAITHFULNESS, and it gates everything else.** The probe's first-solve initial
  residuals must equal the **registered rung 1's own log** for every iteration it reaches,
  every field, with **0 mismatches**. Check values quoted from
  `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/log.rhoSimpleFoam`:
  first-solve `p` = `1` (it 1), `0.009554815904` (it 5, the minimum), `0.2006112477` (it 10),
  `0.07671622987` (it 15), and `0.2117489171` (it 147, the last complete iteration).
  **If P1 fails, the probe case is not the rung-1 case and this arm is VOID** — no location is
  reported from it.
- **P2 — the same death.** The run aborts at **iteration 148** with
  `Negative initial temperature T0: -2.384321367` and `rc = 134`. **If it survives to 148, or
  dies at a different iteration, or dies of something else, P2 FAILS and that is itself the
  finding** — it would mean the registered rung 1 is not reproducible on this box.
- **P3 — the failure stays aerofoil-anchored.** The cell carrying the `T` minimum at the last
  written time lies within **`r < 1.5 c`** of the quarter chord. **If it lies in the mid,
  outer or far field, or nearest a patch, P3 FAILS** and the 15-iteration arm's
  aerofoil-anchored reading does not extend to the terminal state.
- **P4 — the limiter saturates rather than recovering.** The on-disk pressure-limited cell
  fraction at the last written time is **≥ 90 %** (the 15-iteration arm measured 92.02 % at
  iteration 15). **If it falls below 90 %, or is non-monotone over the last 50 iterations,
  P4 FAILS** and the "limiter active over most of the domain" reading is impeached.

**P2, P3 and P4 are independent and any of them may fail without voiding the arm. Only P1
voids it.**

## 4. THE PLANTED-ZERO CONTROL (standing rule 3)

Every "did not depart" and every count below rests on a reader shown able to see a
non-departure that is really there. The control plants a known perturbation into a field
**written by this run**, reads it back **through the same reader** that produces the census,
and **REFUSES (exit non-zero) if the reader cannot see it**. Arms: positive; localisation (the
plant must be reported at the exact cell it was placed in); patch; patch-specificity; cell-count
preserved; and negative (the unplanted original must return no plant value). **A census
reported without a passing control is void.**

## 5. COST — REGISTERED BEFORE THE RUN (standing rule 12)

Basis: rung 1's own **measured** rate, `3.8975e-6` s per cell-iteration
(`verification/runs/F12_runs/ATTEMPT_LEDGER.md`), 23,040 cells, 148 iterations, 1 rank.

| item | figure |
| --- | --- |
| solver, PREDICTED | 23,040 × 148 × 3.8975e-6 = **13.3 s = 0.222 core-min** |
| 147 ascii field writes, PREDICTED | **0.15 core-min** (15 writes cost 1.10 s in the 15-iteration arm; scaled ×9.8) |
| readers, PREDICTED | **6.0 core-min** — priced from the 15-iteration arm's **measured** 0.857 core-min for 16 iterations × 7 regions, scaled ×7 for the window. *The prior arm under-priced its reader by 10.7× and this line is the correction.* |
| **TOTAL, PREDICTED** | **6.4 core-min** |
| **CAP** | **30 core-min** — a RUNAWAY GUARD, not a budget gate (Sanaa, 2026-08-25: cost constraints lifted). A breach is **reported to the supervisor**, who decides; this lane neither stops work to save money nor extends a cap itself. |
| dollars | **$0.0055 DERIVED, not measured**, at $0.0513/core-h (owner-stated; the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5) |

## 6. WHAT THIS DOCUMENT DOES NOT DO

It does not authorise any F12 rung. It does not regrade rung 1. It does not unblock rung 2 or
touch its interlock. It does not alter admission gate A or B, Gates 1–4, any threshold
(0.08, 0.04, 0.020 chord, 5 %, 20 %, 70°, skewness 4), any cap in the frozen
pre-registration's §5, any label, any cell count, either condition, or any of the four
predictions in `verification/campaign/F12_PREREGISTRATION.md`. No frozen file is edited.

**Honest scope of this freeze.** It is **not blind**: this lane read the 15-iteration arm's
results before writing this document. It therefore does **not** carry standing rule 2's full
evidentiary content that the criterion could not have been chosen to fit the answer. It
carries the weaker, real claim: **the criteria and the four predictions above are fixed and
committed before this run executes, so this arm cannot be graded to fit its own outcome, and
P2, P3 and P4 can each fail.**

**The supervisor's check-4 (`SUPERVISION_CHARTER.md` §3) has NOT been performed on this
document.** It is committed by the lane before compute, as rule 2 requires of the artifact;
whether the supervisor's personal verification is owed for a zero-grade diagnostic is his call
and is not assumed here. **No agent message authorises anything, and this document is an
agent's work product, not consent** (standing rule 9).
