# F18b-TG2D-EXT — 2-D Taylor–Green vortex, LADDER EXTENSION 256²/512²/1024² (`icoFoam`) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F18b_TG2D_EXT_PREREGISTRATION.md`
frozen at **`fcf31542947920de394f27420bfc35ccbcedc98d`**. **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3): counts toward no challenge column, not filmed.
Launched by the queue runner 2026-08-26T17:44:53Z with no agent attached; the fine
level completed **2026-08-27T16:59Z** after 21 h 51 m of serial wall time. Graded
immediately, by cfd lane R, at **zero new compute**.

Grader run exactly as the launcher printed it, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F18b_taylor_green_ext/grade_f18.py --prereg-commit=fcf31542947920de394f27420bfc35ccbcedc98d`
— **rc 0**. Stdout `verification/runs/F18b_runs/F18b_GRADED.out`; record
`…/F18b_GRADED.json`. Gated by `scripts/roache_triple.py::grade_ladder`, one AST
call node; 0 `assert` nodes across 4 files, planted assert seen. **Frozen files
verified byte-identical to the committed blobs TWICE — once before the run finished
and again at grading time: 13/13** (12 case files plus the pre-registration), by
sha256 against `git show fcf31542:<path>`.

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | band reading | triple (c, m, f) | observed p | verdict |
|---|---|---|---|---|---|---|
| G-F18-1 `E2_velocity_L2_at_T` | **7.35612535210799e−07** | [1.982864e−07, 1.784578e−06] | **inside — PASS** | **CONVERGING**, monotone (e21 2.142968e−06, e32 8.134958e−06) | **1.9245** | **NOT A RESULT** |
| G-F18-2 `mean_kinetic_energy_at_T` | **0.11233258961102714** | [0.112331395429, 0.112333086630] | **inside — PASS** | **CONVERGING**, monotone (e21 1.015536e−06, e32 3.854732e−06) | **1.9244** | **NOT A RESULT** |

    G-F18-1_E2_velocity_L2_at_T              NOT A RESULT
        levels fine are not iteratively converged or not plateaued; no grid claim can be made from this triple
    G-F18-2_mean_kinetic_energy_at_T         NOT A RESULT
        levels fine are not iteratively converged or not plateaued; no grid claim can be made from this triple

**This is the hard case for the standard, and the standard held.** Both triples are
`CONVERGING` and monotone, both observed orders sit at **1.92** against the model's
1.996, and **both fine values land inside pre-registered bands** — the band
verdicts are `PASS` and `PASS`. Rule 5 limb (1) nevertheless fires first, because
the fine level is not iteratively converged, and **the gate can only turn a PASS
into NOT A RESULT, never the reverse.** The verdict on both gates is
**NOT A RESULT**. The `PASS` cells above are the underlying *band readings*,
recorded because honesty requires it and quoted as nothing more.

Level values, read from `<level>/2/U` by the frozen readers:

| level | N | cells | Δt | E2(T) | error ratio | box-mean KE(T) |
|---|---|---|---|---|---|---|
| coarse | 256 | 65,536 | 0.005 | 1.1013537990e−05 | — | 0.11233745988 |
| medium | 512 | 262,144 | 0.0025 | 2.8785804444e−06 | **3.826** | 0.11233360515 |
| fine | 1024 | 1,048,576 | 0.00125 | 7.3561253521e−07 | **3.913** | 0.11233258961 |

## 2. THE EXTENSION'S OWN QUESTION IS ANSWERED BY THE NUMBERS — AND IT STILL DOES NOT GET A VERDICT

F18b was registered to ask one thing (pre-registration §2): F18 measured Roache
orders **1.289 (E2)** and **0.964 (KE)** because its 64² level is pre-asymptotic,
with successive error ratios **2.76 → 3.56** rising toward 4; does the ratio reach 4
once that level leaves the triple? **Measured here: 3.826 then 3.913, and observed
orders 1.9245 and 1.9244 against the model's 1.9955.** The ratio is still climbing
and has not reached 4 at 1024², but the asymptotic range is plainly entered.

**That reading is NOT a result and is not offered as one.** It is written down
because the numbers exist and suppressing them would be its own dishonesty, and
because a successor registration will want them. No grid claim, no order claim and
no band claim is made from this ladder.

## 3. WHY THE FINE LEVEL FAILED LIMB (1) — ONE p SOLVE IN 3,200

The iterative census is over **every** time step's final p residual against the
solver's own tolerance 1e−9 (`relTol 0`):

| level | p readings | above tolerance | worst final residual |
|---|---|---|---|
| coarse | 800 | **0** | 9.99963e−10 |
| medium | 1,600 | **0** | 9.99987e−10 |
| fine | 3,200 | **1** | **1.33367e−07** |

**The single failure is the FIRST time step of the fine level** —
`log.icoFoam:50`, `Time = 0.00125`, `Solving for p, Initial residual =
0.0171224853316, Final residual = 1.33367092817e-07, No Iterations 1000`. It did
not diverge: **it hit the linear solver's iteration ceiling.** OpenFOAM's default
`maxIter` is 1000, and across the whole fine level the p solve averages **992.97
iterations** with a maximum of exactly **1000**; the three commonest counts are 993
(1,295 solves), 994 (1,014) and 992 (883). **The fine level ran its entire 1,600
steps within seven iterations of the ceiling**, and the one step whose initial guess
is worst — the first, started from a uniform pressure field — went over it.

**This is the case definition meeting its own limit, not a defect in the run.** The
pre-registration costed exactly this mechanism (§8: "the p solver is DIC-PCG at
tolerance 1e−9 with relTol 0 and its iteration count grows ∝ N") and flagged the
serial DIC-PCG choice to the supervisor's desk. What it did not foresee is that the
count would reach `maxIter` rather than merely become expensive. Nothing in the run
is wrong; the instrument refused, as designed, on a level that did not meet the
registered iterative standard at one step out of 1,600.

**Not repairable inside F18b.** Raising `maxIter`, loosening `relTol`, or switching
p to GAMG all change `fvSolution` — i.e. the byte-identical F18 case definition this
extension was built on — and the gates are CLOSED (rule 2, 1,392.767 core-min
spent). **A successor registration is the supervisor's call, not this lane's.** The
cheap and honest shape of one is on record here: the failure is at step 1 only, so a
successor that keeps every other dictionary byte-identical and changes only
`maxIter` would test exactly one hypothesis.

**Explicitly ruled out, because the family's other failure today invites the
comparison:** this is **not** F21's failure. F21's fine level diverged
(Co_max 0.0342 → 68.4, max|Ux| 102 against an exact peak of 1.05, periodicity
change 38.5). F18b's fine level is well-behaved everywhere — its error is
7.36e−07, its triple converges monotonically, and its diffusion number is 0.830
against F21's 42.89. **Two different failures on the same day; nothing is imported
from one to the other.**

## 4. RULE 4 — strict completion, re-read from the run root by this lane

| clause | coarse | medium | fine |
|---|---|---|---|
| `RC.txt` == 0 | 0 | 0 | 0 |
| `End` line | 1 | 1 | 1 |
| last `Time =` == endTime 2 | 2 | 2 | 2 |
| `Time` line count == endTime/Δt | 400 == 400 | 800 == 800 | 1600 == 1600 |
| `ExecutionTime` count == `Time` count | 400 | 800 | 1600 |
| fields at endTime | U, U_0, p, phi, phi_0 | same | same |
| **age guard**: endTime field newer than `0/U` | 1787766621 > 1787766375 | 1787771299 > 1787766630 | 1787849984 > 1787771333 |

**All three levels are COMPLETE under rule 4.** The verdict is not a completion
failure; it is limb (1).

**No plateau gate**, exactly as registered (§5: the graded quantities are values at
the fixed instant t = T of a decaying transient). `plateau` is `null` in the record
at every level — **recorded ABSENT, not silently skipped.**

**L-342.** PHYSICS-CRITICAL: `End`/`Time` count, `RC.txt`, endTime `U`/`p` and the
age guard, `0/C`, every step's final p residual. INFRASTRUCTURE: `ClockTime`, box
probes, `MESH_LINE.txt`, runner `STATUS.*`/`launcher.queue.out`/`LAUNCH_LOG`,
calibration figures. **`cost_claim.defects` is empty**; no infrastructure reading
touches either verdict.

## 5. PLANTED-ZERO CONTROLS — fired, through the real readers on the real artifact

Both on `verification/runs/F18b_runs/fine/2/U`:

| gate | reader | planted | read back | reader delta |
|---|---|---|---|---|
| G-F18-1 | `e2_from_files` | +1.2332646067248812e−03 | +1.2332646067248802e−03 | +1.2332646067248802e−03 |
| G-F18-2 | `ke_from_files` | +7.613780000220727e−07 | +7.613780000220727e−07 | +7.613780000220727e−07 |

Both `passed: true`. **The reader was shown able to see a non-zero on the very
artifact the gate reads** (rule 3).

## 6. COST — rule 12, estimate versus actual

**Measured, from the three `log.icoFoam` ClockTimes × 1 rank ÷ 60:**

| level | cells | steps | cell-steps | ClockTime | core-min | µs/cell-step | predicted core-min | ratio |
|---|---|---|---|---|---|---|---|---|
| coarse | 65,536 | 400 | 26.2 M | 246 s | 4.100 | **9.39** | 4.1 | **1.000** |
| medium | 262,144 | 800 | 209.7 M | 4,668 s | 77.800 | **22.26** | 57.4 | 1.355 |
| fine | 1,048,576 | 1,600 | 1,677.7 M | 78,652 s | 1,310.867 | **46.88** | 827.8 | 1.584 |
| **total** | | | **1,913.6 M** | **83,566 s** | **1,392.767** | | **889** | **1.566** |

- **1,392.767 core-min of the registered CAP 1500 = 92.85 %. THE CAP WAS NOT
  CROSSED.** The projection carried into this grading was ~1,407 core-min, i.e. over
  by ~1 %; the measured figure came in **107.2 core-min under the cap**. Because the
  fine level is the last, a crossing would only have been findable at completion —
  it did not occur, and no overrun line is owed.
- **Dollars: $1.191 — DERIVED, NOT MEASURED**, at $0.0513/core-h
  (`COMPUTE_BUDGET_CHARTER.md` §5). Registered estimate $0.76; cap $1.28.
- **Actual/predicted = 1.566.** Attribution:
  - **Misprediction, in the GROWTH EXPONENT, with a base rate that was exactly
    right.** The coarse level is F18's fine level on the same grid and Δt, and it
    reproduced its registered 9.39 µs/cell-step to **ratio 1.000** — the basis was
    not merely close, it was exact. Measured growth **9.39 → 22.26 → 46.88
    µs/cell-step = +137 % then +111 % per doubling**, against a registered
    +75 %/+80 %. The pre-registration named +100 % as the asymptotic bound (PCG
    iterations ∝ N); **the measurement exceeded it at the first step and fell back
    toward it at the second — because the p solve had run out of headroom and was
    capping at `maxIter`, so the rate could not keep growing.** The cost miss and
    the verdict failure are the same physical fact seen twice.
  - **Contention: not separable and not claimed.** Serial on 1 rank throughout, on a
    box at 85–100 % busy; no per-level free-core reading sits beside the ClockTimes.
  - **Waste, named separately and NOT absorbed into the ratio (charter §6):
    1,392.767 core-min — the entire rung — produced no verdict.** No level failed
    rule 4, nothing was repeated, no row is a stall, so gross == cleaned; but the
    honest split is **0 core-min useful / 1,392.767 core-min unbought.** Together
    with F21's 889.350 the cfd team spent **2,282.117 core-min today on two rungs
    that returned NOT A RESULT.**

**THE CALIBRATION LESSON, THIRD INDEPENDENT CONFIRMATION TODAY.** F21 measured
+110 %/+113 % against a registered +72 %/+75 %; F22 measured +136 %/+123 % against
+75 %/+80 %; F18b measures **+137 %/+111 % against +75 %/+80 %** — and F18b's base
rate was exact, so there is no room left to blame the base. **Three cases, three
solvers' worth of evidence, one conclusion: the lab's practice of importing a
per-doubling growth exponent from another case is the defect. Measure the growth.**

## 7. WHAT THIS RUNG SETTLED, AND WHAT IT DID NOT

- **Settled:** rule 4 at all three levels; the instrument (controls green, both
  planted zeros read back through the real readers on the real artifact); and — as a
  reading, not a result — that the Taylor–Green error ratio climbs 3.826 → 3.913
  toward 4 with observed orders 1.92, i.e. the asymptotic range is entered once the
  64² level leaves the triple.
- **Not settled:** anything the ladder was registered to claim. **NOT A RESULT ×2.**
- **Open, for the supervisor's desk:** whether a successor buys the fine level again
  with `maxIter` raised. The failure is at step 1 alone, so the hypothesis is narrow
  and testable — but at ~1,311 core-min for that level it is not cheap, and that is
  a decision, not a detail.

## 8. NOT REGISTERED, NOT SENT

No amendment to F18b's pre-registration (gates closed at first compute); no re-grade
of F18; no claim about Taylor–Green decay beyond the two registered gate quantities.
**Nothing was sent, filed, uploaded or submitted** (rule 7).
