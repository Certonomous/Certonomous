# Arm D died at 27.0 % — triage, and it was a BUDGET STOP firing exactly as registered

**Author:** `ansys-verification-supervisor`, personally, 2026-08-25T19:1xZ.
**SUPERVISION_CHARTER §3 check 2**, which is not delegable: *a crash, a divergence or a
refused solve is a finding about the case, the method or the toolchain until triage
demonstrates otherwise.* Zero compute — nothing was started to produce this.

**NOT FILED ANYWHERE** (CLAUDE.md rules 7, 8).

---

## What happened

`simpleFoam` pid 2396481, `D_kOmegaSST/L3_1000x5`, exited at ~19:05Z. At 19:00Z it was
reported to me as **live and healthy**. Both statements are true: it was healthy, and then
its wall-clock wrapper reached zero.

Measured from `verification/runs/ansys_verification/VMFL003_M2/D_kOmegaSST/L3_1000x5/log.simpleFoam`:

| | |
|---|---|
| `End` line | **absent** |
| last `Time` | **5949** of `endTime 22000` — **27.0 %** |
| `ExecutionTime` | **1662.74 s** |
| wrapper | `timeout 1663` |

## It was not a crash. It was the frozen cap.

The launcher computes the wrapper from the registered budget:

    TIMEOUT_S = min(CAP_CORE_MIN − spent, PER_ARM_CAP − arm_spent) × 60 / RANKS

with `CAP_CORE_MIN = 160` and **`PER_ARM_CAP = 40`**, both frozen in
`PREREGISTRATION.md` §12. Arm D had already spent 383.41 s (L1) + 353.01 s (L2) =
**12.27 core-min**, leaving 27.73 core-min → **1663 s**. The observed wrapper is 1663 s and
the run consumed 1662.74 s of it. **The cap fired to the second, exactly as registered.**

`resume_fire_arm_d.sh` says so itself in its own abort text: *"rc=124 means the BUDGET
TIMEOUT fired — that is a budget stop, and rule 12 gives it NO new budget."*

**Per-arm consumption against the frozen 40 core-min cap:**

| arm | core-min | of cap |
|---|---|---|
| A `kEpsilon` | 29.96 | 74.9 % |
| B `realizableKE` | 31.15 | 77.9 % |
| **C `RNGkEpsilon`** | **39.93** | **99.8 %** |
| **D `kOmegaSST`** | **39.99** | **100.0 %** |

**Two of four arms were killed by the same frozen cap.** Arm C's `D_500x3` stopped at
`Time = 4085` of 18000 (22.7 %) for the identical reason.

## THE VERDICT

**Arm D is `NOT A RESULT` on ladder incompleteness**, on precisely the ground arm C was
ruled on in `aba61e53`, and **it gets NO FRESH CAP**. CLAUDE.md rule 12: *an overrun stops
the run; it does not get a new budget.* The ruling that bound arm C binds arm D, and a
supervisor who applies his own precedent only to the arm he is less attached to is not
applying a precedent at all.

It is **not** `PENDING`. `PENDING` means not-yet-run and would soften a stop that actually
happened. It is not `BLOCKED`: nothing external prevented it. The registered budget was
spent and the ladder is incomplete. That is `NOT A RESULT`.

Arms **A** and **B** are complete — all six levels, `End` present, last time == `endTime` —
and are being graded under their frozen comparator.

## A hypothesis I formed, tested, and KILLED — recorded because I nearly reported it

My first reading was **contention**: the box was loaded, wall time inflated, and a
core-minute cap computed as `wall × ranks` charged these runs for their neighbours. That
story is attractive right now, because Sanaa has just made core utilisation a saturation
target, and it would have made a tidy lab-wide warning that saturating to 80–90 % will start
killing runs that fit at low load.

**It is false, and OpenFOAM prints the number that falsifies it.** `ExecutionTime` is CPU
time and `ClockTime` is wall; if contention were the mechanism the two would diverge.

| run | ExecutionTime | ClockTime |
|---|---|---|
| A `L2_500x5` | 333.93 s | 334 s |
| C `L2_500x5` | 1413.1 s | 1416 s |
| D `L3_1000x5` | 1662.74 s | 1662 s |

**They track to within 0.3 % everywhere.** These processes were never starved. The budget
was consumed by real CPU. **Contention explains none of it**, and no contention story goes
into any calibration row for this rung.

I am keeping the dead hypothesis in the record rather than deleting it, because it was
one commit away from being repeated upward as a lab-wide finding about Sanaa's new
saturation regime — and it would have been wrong, confidently, in a direction that
flattered a story I already wanted to tell.

## What the numbers actually say — offered as a hypothesis, labelled as one

Identical mesh `L2_500x5`, identical `endTime 18000`, all four models:

| arm | ExecutionTime | vs baseline |
|---|---|---|
| A `kEpsilon` | 333.93 s | 1.00× |
| B `realizableKE` | 322.91 s | 0.97× |
| D `kOmegaSST` | 353.01 s | 1.06× |
| **C `RNGkEpsilon`** | **1413.1 s** | **4.23×** |

**The ordering is inverted from what model cost predicts.** `kOmegaSST` carries an extra
transport equation and a stiff near-wall ω treatment and costs 1.06×. `RNGkEpsilon` differs
from standard `kEpsilon` by a single strain-rate term in the ε equation and costs **4.23×**.

Two further facts rule out a simple per-model multiplier:
- **Arm C's `L3` (633.58 s) is CHEAPER than its own `L2` (1413.1 s)** — twice the cells and
  1.22× the iterations, at 0.45× the cost. A model-cost story cannot produce that.
- **Arm D's `L3` ran at 0.2795 s/iteration** against the ~0.04 s/iteration its own `L2`
  predicts under mesh scaling — **7× over**.

**Hypothesis, not a verdict: certain configurations fall into a badly-converging inner
linear solve and burn multiples of the predicted CPU per outer iteration.** It is
configuration-specific rather than model-specific, which is why it strikes C at L2 and D at
L3 and leaves both alone elsewhere.

**This is exactly the failure Sanaa's own instruction of 2026-08-25 anticipates:** *"When a
grid doesnt converge, try different pre conditioners, see if that's a raised issue
online/in the litterature, check for bugs, if unsteady check cfl, pick different meshing."*
And this team already built the instrument — the `VMFL007_R2` preconditioner sweep
(`A1_GAMG_GaussSeidel`, `A2_GAMG_DICGaussSeidel`, `A3_PCG_DIC`, `A4_PCG_GAMGprecon`,
`A5_PBiCGStab_DIC`, `A6_smoothSolver_symGaussSeidel`).

**That sweep is NOT run here.** Her remedies each change the experiment, so each is a new
frozen registration with the changed thing as the registered variable under test — never a
re-run of a stopped arm until it fits. Cycling until an arm clears is selection, not
prediction, and it would poison every credential in the register.

## The instrument finding that outlives this rung

**No `RC.txt` and no `record.json` exists anywhere under `VMFL003_M2`.** The launcher's
`printf` that would write `rc=` runs only on the path that completes. So for **every** run
in this rung the `rc = 0` clause of strict completion (rule 4) is **unevaluable from disk**.

That is not a bookkeeping gap. Rule 4 is a conjunction — *a run is done only if all of it
holds* — and a conjunct nobody can evaluate is a conjunct nobody is applying. **A launcher
that cannot evidence its own exit code cannot satisfy the completion rule it is run under.**
This is charter-grade for §5 and is carried into this team's close-out duty; the batch
launched today writes `RC.txt` per job by explicit instruction.
