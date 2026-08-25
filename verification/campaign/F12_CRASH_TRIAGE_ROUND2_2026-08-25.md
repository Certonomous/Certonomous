# F12 — CRASH TRIAGE, ROUND 2, AGAINST THE TERMINAL-DEPARTURE PROBE

**Written by the cfd supervisor personally, 2026-08-25.** Crash triage is a
`SUPERVISION_CHARTER.md` §3 check-2 and **may not be delegated**; a relayed check
is a summary, not a check. `[lab-attributed]` under Sanaa's desk-item disposal
rule of this date; **overrulable**.

**This document GRADES NOTHING.** Rung 1 stays `NOT A RESULT`. Rungs 2–5 stay
`BLOCKED`. No gate, threshold, band, cap or label is touched. It does not read
around, invoke or edit rung 2's interlock.

**Supersedes nothing.** It stands on top of
`verification/runs/F12_runs/RUNG2_DISPOSITION_AND_CRASH_TRIAGE_2026-08-25.md`
(round 1, same supervisor) and takes the new evidence in commit `e6313b48`
against it.

**Evidence read by me, from HEAD, not from the worktree and not from a lane's
summary:**
`verification/runs/F12_runs/terminal_departure_2026-08-25/evidence/terminal_departure.json`
(147-row `Q2_T_min_track`, `Q1_crossings`, `P1`, `P2`, planted-zero block);
`verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/system/fvSchemes` and
`fvSolution`; `0/T`, `0/U`, `0/p` of the same case.

---

## 1. I REJECT THE FRAMING THAT THE EVIDENCE "WAS POINTING THE WRONG WAY"

The probe is reported as showing *the crash is NOT where the evidence was
pointing*. **Read against the probe's own `Q1_crossings`, that is not what
happened, and the distinction is the whole finding.**

| T threshold first crossed | iteration | (x/c, y/c) | r from quarter-chord |
|---|---|---|---|
| 250 K | 14 | (0.0078, −0.0118) | 0.556 — **leading edge, lower surface** |
| 200 K | 102 | (0.7268, 0.1312) | 0.703 — **upper surface, aft** |
| 100 K | 130 | (1.3309, 0.2137) | 1.210 — **near wake** |
| 0 K | 147 | (2.0819, 0.2694) | 1.918 — **one chord into the wake** |

**One disturbance, born on the aerofoil and swept downstream.** The frozen
15-iteration replication located the **origin**. The terminal-departure probe
located the **terminus**. Both are right about their own window and they describe
the same object. The probe says so itself in its best sentence — *"where does the
field first go wrong" and "where does it die" have different answers* — and that
sentence does **not** license discarding the first answer.

The probe's `P3` FAIL (predicted r < 1.5 c, measured 1.91791 c) is a failed
prediction **about the terminus**. It is not a refutation of the origin, and it
must not be quoted as one.

## 2. THE SAME EPISTEMIC ERROR APPEARED TWICE IN THIS TEAM ON ONE DAY

**F1/ONERA M6** (`ed726454`): the >70° **population** is at the sharp trailing
edge — 516 of 598 faces in the tip fill — and the **maximum**, which is the number
`MESH_STANDARD.md` §3.1 actually gates on, is at the **outermost farfield cell**.
The earlier localisation at `c6431c9e` was right about the population and wrong
about the maximum.

**F12** (`e6313b48`): the **origin** is on the aerofoil and the **terminus** is in
the wake.

**Both times a reader was one step from concluding the earlier localisation was
wrong. Both times it was right about a different quantity.** The rule that falls
out, and it is worth a lesson: **name the quantity before you name the place.
"Where is it worst" and "where is it made" are different questions and a
localisation answers only the one it was asked.** Filed for landing as a lesson by
a lane; recorded here so it is not lost if that lane dies.

## 3. THE NEW FACT, AND IT IS MINE: THE SOLUTION WAS NON-PHYSICAL LONG BEFORE IT CRASHED

Read from the case's own `0/` directory: `T = 300 K` uniform,
`U = (254.55661283, 12.40536100, 0)`, `p = 101325 Pa`.

Derived (arithmetic on those three numbers, nothing else):
`|U| = 254.8586 m/s`, `a = sqrt(1.4 · 287 · 300) = 347.190 m/s`,
**`M = 0.734064`** — which independently reproduces the registered `M 0.734` and
`α = atan(12.40536/254.55661) = 2.79°`, so **this is the case it says it is.**

**The stagnation temperature is a physical ceiling on `T` anywhere in an adiabatic
flow:**

> **`T0 = 300 · (1 + 0.2 · 0.734064²) = 332.331 K`. The entire dynamic
> temperature of this flow is `32.331 K`.**

Measured against that ceiling, from the probe's own 147-row track:

| iteration | `T_max` | `T_min` | field span | span ÷ dynamic temp |
|---|---|---|---|---|
| 4 | **332.985** — first crossing of `T0` | — | — | — |
| 8 | last iteration with `T_max ≤ T0` | — | — | — |
| 11 | 335.447 | 264.219 | 71.2 K | 2.2× |
| 20 | 342.627 | 236.504 | 106.1 K | 3.3× |
| 50 | 355.674 | 222.402 | 133.3 K | 4.1× |
| 100 | 397.357 | 203.324 | **194.0 K** | **6.0×** |
| 147 | 608.505 | −8.156 | 616.7 K | 19.1× |

**An honest margin, stated rather than assumed.** `T0` is the *inviscid* adiabatic
bound; a viscous flow at `Pr ≈ 0.7` admits a small total-enthalpy overshoot, so a
**generous** ceiling is `T0 + 10 K = 342.33 K`. Even against that generous
ceiling: first exceeded at **iteration 19**, permanently exceeded after
**iteration 80**, and by iteration 100 `T_max = 397.4 K` — **55 K above the
generous ceiling with 47 iterations of solving still to go.**

**The independent cross-check, and it agrees.** `T_min = 203.324 K` at iteration
100 implies, through the same isentropic relation, a **local Mach number of
1.542** in a flow whose freestream is 0.734. RAE 2822 case 9 carries a local
supersonic pocket, but not at `M = 1.54`. Two different bounds, read off two
different ends of the same field, both broken by iteration 100.

**So the crash at 148 is the last 47 iterations of a solution that was already
outside physics.** This **corroborates** round 1 §3.2 from a completely
independent quantity: the first-solve `p` residual never got below `9.5548e-03`,
at iteration 5, and was rising. **A residual reading and a physical-bounds reading
independently place the failure at iterations 4–5.** That agreement is worth more
than either alone.

## 4. WHAT THIS BUYS THAT NO PREVIOUS ARM DID: A REFUSAL THAT COULD HAVE FIRED

Every arm on this line so far has read a residual, swapped a lever, or looked at a
field **after the fact**. `T0` is different in kind: it is a **bound derivable
from the boundary conditions alone, before the solver starts**, and it is
checkable at every iteration.

**A monitor asserting `T_max ≤ T0 + margin` would have refused this run at
iteration 19 instead of at 148** — and would have refused it with a *reason*
rather than a `SIGABRT`. That is exactly what `docs/standards/MONITOR_STANDARD.md`
exists to require, and F12 had no such monitor. **Recorded as an instrument gap in
cfd's own territory, not as a criticism of any lane.** Landing the general clause
is referred (§7).

## 5. THE `div(phi,e)` CANDIDATE IS WEAKER THAN ITS PHRASING AND I AM NOT PROMOTING IT

The probe offers, explicitly as a candidate only: *`div(phi,e)` is `bounded Gauss
linearUpwind limited`, second-order and not TVD-bounded, on a wake mesh that
coarsens downstream.* **I read the dictionary myself and the phrasing overstates
it in two places:**

1. **`limited` here is not a flux limiter — it is a named `gradSchemes` entry**,
   and that entry resolves to **`cellLimited Gauss linear 1`**. `cellLimited` at
   coefficient **1** is the most restrictive form available and it *does* bound the
   reconstructed face value to the min/max of the neighbouring cell values. The
   reconstruction is limited; the statement "not TVD-bounded" is true of the flux
   interpolation and misleading about the setup.
2. **`bounded` is applied**, and it is precisely the correction for the
   non-conservative mid-SIMPLE mass flux that a steady compressible solve creates.

**It stays a candidate. It does not become the story.** Three of the last four
mechanism claims on this line have been corrected, one of them this supervisor's
own, and **I am not adding a fifth.** No mechanism is claimed in this document.

## 6. THE TWO ARMS I WANT, AND WHY THEY DISCRIMINATE

The terminal-departure probe cost **0.440230 core-minutes** for all 148
iterations. A discriminator costs about the same. **Under Sanaa's 2026-08-25 lift
cost is not a reason to hold anything; caps are runaway guards.**

The question that actually discriminates is **whether the energy overshoot is a
SCHEME artefact or an EQUATION-OF-STATE RELAXATION artefact**, because
`fvSolution` sets:

```
relaxationFactors { fields { p 0.3; rho 0.05; } equations { U 0.3; e 0.5; ... } }
```

**`rho` is relaxed six times more heavily than `p`.** In `rhoSimpleFoam` the
temperature is recovered through the thermodynamics from `p` and `rho`; if `p`
advances six times faster than `rho`, `T` inherits the mismatch directly, and it
inherits it **from iteration 1** — which is exactly when `T_max` starts climbing.
**I state that as the reason the arm is worth running, NOT as a mechanism claim.**

> **Arm 1:** `div(phi,e)` → `bounded Gauss upwind`. Nothing else changed.
> **Arm 2:** `rho` relaxation `0.05` → `0.3`, matching `p`. Nothing else changed.
>
> **The discriminator is `T_max` against `T0` in the first 20 iterations, not the
> crash iteration.** If an arm removes the early stagnation-bound excursion, the
> mechanism is named. **If neither does, both are exonerated** and the search moves
> to the boundary conditions — which is a result, not a null.

**RULE 2 BINDS THIS AND I AM STATING THE CONSTRAINT BEFORE THE ARM IS WRITTEN.**
`N-C4`, landed by this team from the Ekaterinaris intake, rules that **a
scheme-order change is a change of experiment, not a tuning knob**, and rule 2
forbids one inside a fired pre-registration. So these arms:

- carry **their own pre-registration**, committed before compute, exactly as
  `F12_TERMINAL_DEPARTURE_PREREGISTRATION.md` did;
- **grade nothing**, and no F12 gate value may be quoted from them;
- assert the registered rung directories **absent before and after**, and rung 1's
  fingerprint **unchanged**;
- carry a planted-zero control on the field they read.

## 7. THE DISPOSITION OF RUNGS 2–5 — AND THE BLOCKER WAS NEVER THE PIN

The `roache_triple` pin is **DISCHARGED** (`74394729`, `verify_roache_triple_pin.py`
34/34). **Rungs 2–5 are no longer held on the pin. They are still `BLOCKED`, on two
independent grounds, and I name both so the next lane does not clear one and think
it is through.**

**Blocker 1 — the interlock, upheld.** `launch_f12_rung.py`'s
`rate_calibration_gate()` refuses rung 2 on its own unmodified bytes: rung 1's
`rc = 134 ≠ 0`, all six completion limbs false. **Opening it needs launcher bytes
changed, and an interlock that can be edited when it fires is not an interlock**
(round 1 §1; `MESH_STANDARD.md` §8.2 — *a refusal from the tool whose job is to
refuse is a diagnostic, not an obstacle to route around*).

**Blocker 2 — AND NOBODY HAS STATED THIS ONE. THE TRIPLE IS ALREADY DEAD, WHATEVER
RUNGS 2 AND 3 DO.**

- F12 has **exactly one triple and it spans rungs 1–3**. The pin commit establishes
  this mechanically: `all_triples()` refuses fewer than three levels, and rungs 4
  (tape `M 0.730`) and 5 (2× far-field) are **one level each of a different
  experiment** and may not be promoted — *"a single-mesh result is not shipped"*.
- **Standing rule 5, limb (1), is unconditional: any level not iteratively
  converged → `NOT A RESULT`.** Rung 1 is not converged, and `P2` proves it
  reproduces **bit-identically** (`rc = 134`, abort at 148, `T0 = −2.384321367`).
- **Therefore F12 cannot produce a Roache-gated result under its current
  registration no matter how much compute rungs 2–5 receive.** Firing them now buys
  nothing any gate can use.

**An honest caveat that cuts against me, stated because it is testable.** A finer
mesh might well *not* crash — if the mechanism is resolution-dependent, refining
the wake could cure it. That is a **prediction, not a fact**, and it does not
change blocker 2: even a converged rung 2 and rung 3 cannot form a triple with a
rung 1 that rule 5 has already voided.

**The lawful route is a SUCCESSOR REGISTRATION** with its own gates and its own
cap, written once the mechanism is named — **not an amendment to the fired one,
and not a cap raise.** Sanaa lifted a spending constraint; she did not retire rule
2. Reading *"cost constraints are lifted"* as *"the cap can be raised"* is the
exact shape of permission laundering the F3 lane named in `1251a015`, and it is
named again here.

## 8. THE PROBE'S MOST VALUABLE RESULT WAS NOT BILLED AS ITS RESULT

`P1`: **885 first-solve residuals over 148 iterations, 0 mismatches** against the
registered rung-1 log. `P2`: `rc = 134`, abort at iteration 148,
`T0 = −2.384321367` **bit-identical**.

**A deterministic, bit-reproducible crash is a MEASUREMENT, not a failure.** It is
what makes every arm in §6 interpretable: each one has an exact control to differ
from, and any difference is attributable to the one thing the arm changed. Without
it none of them would discriminate anything. **The probe earned its 0.44
core-minutes on `P1`/`P2` alone, before `Q1` and `Q2` were read.**

## 9. THE PROBE'S SELF-REPORTED `P4` DEFECT — ACCEPTED, AND THE CLASS IS NAMED

The lane recorded against itself that `P4` is **not evaluable as registered**: its
own freeze named cells *outside* the pressure bounds, and `pressureControl::limit()`
censors `p` on the way to disk, so a limited cell reads exactly **at** the bound
and never outside it. Measured maximum over 147 iterations: **0. The registered
quantity could not have been non-zero whatever the run did.**

**Accepted, and the self-naming is the right behaviour.** This is the same defect
class as ansys-verification's VMFL059 (`6a9afa0a`, *a mis-specified gate quantity
that could never have passed, not a failed solve*). **Two teams, two days, one
class.** The at-bound proxy the lane actually read (71.34 % against 90 %) disagrees
with the solver's own `pressureControl` print on 44 of 147 iterations and **is
correctly presented as refuting nothing.**

**Standing requirement now placed on every cfd pre-registration, and it is in the
brief of every lane I have live:** for each gate, **prove in the document that the
quantity can take a failing value and a passing value on this solver's actual
on-disk output, and name the write path.**

## 10. WHAT IS NOT SETTLED

- **The mechanism.** Open. No claim made here.
- Whether the wake is **causal** or merely where the coldest cell ends up. The
  probe declines to establish it and I do not establish it either.
- Whether a finer mesh crashes. Predicted both ways above; unmeasured.

## 11. VERDICTS

| object | verdict | on what |
|---|---|---|
| F12 rung 1 | **`NOT A RESULT`** | unchanged; rule 5 limb (1), `rc = 134`, reproduces bit-identically |
| F12 rung 2 | **`BLOCKED`** | interlock (rung 1 `rc ≠ 0`) **and** the triple is void |
| F12 rung 3 | **`BLOCKED`** | same |
| F12 rungs 4, 5 | **`BLOCKED`** | one level each of a different experiment; may not be promoted |
| the F12 rung-1–3 triple, as registered | **`NOT A RESULT`** | rule 5 limb (1) — unconditional and not reachable by more compute |

**Cost of this document: ZERO COMPUTE.** No `docs/COST_CALIBRATION.md` row is owed.
Every number above is arithmetic on artifacts already on disk.
