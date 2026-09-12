# KILL-AND-RESUME PROOF — OpenFOAM steady class — 2026-09-12

**Verdict: PASS.** The resumed run reproduces the unkilled reference EXACTLY at the
resolution of the record (12 significant digits), not merely to the solver's tolerance.

Sanaa's run instructions of 2026-09-12 (`docs/SANAA_DIRECTIVE_2026-09-12_RUN_INSTRUCTIONS.md`),
item 5: *"Proof: one kill-and-resume test on one case per solver class, once, before the fleet
launches anything; the resumed result must match an unkilled reference to the solver's
tolerance."* This record discharges that item for the **OpenFOAM steady class only**. The
DAFoam optimisation class and the OpenFOAM transient class are **PENDING** and are not
covered by anything below.

---

## 1. What was run

| | |
|---|---|
| Case | F25 square duct, coarse level, copied from `verification/runs/F25_DUCT3D_runs/coarse` |
| Mesh | 32,768 cells, genuinely 3D (no `empty` patch), cyclic inlet/outlet, wall patch 8,192 faces |
| Solver | `simpleFoam`, laminar, SIMPLEC, fixed streamwise body force (`constant/fvOptions`) |
| Ranks | 4 MPI (`decomposeParDict` `simple (1 2 2)`, the x direction never cut) |
| User | `ubuntu` (uid 1000). Never root. |
| Detachment | every solver launched `setsid nohup bash -c ...`, rc captured INSIDE the wrapper |
| Working root | `/home/ubuntu/certonomous-runs/KILL_RESUME_PROOF/` (`ref/` and `kill/`) |
| Checkpoint policy under test | `writeInterval 50`, `purgeWrite 2`, `endTime 300`, `deltaT 1` |
| Graded quantities | `forces` functionObject on patch `wall` (x-force), and a `volFieldValue` volume average of `U` (the case's physical reading, bulk velocity) — both written EVERY iteration |

The two arms differ in exactly one thing: one was killed.

* **`ref/`** — start from time 0, run to 300, never interrupted. `rc=0`.
* **`kill/`** — start from time 0; at **iteration 120** the whole detached process group was
  sent **SIGKILL** (`kill -9 -<pgid>`, pgid 73170). No `End` line, no rc, nothing cleaned up.
  `purgeWrite 2` had left exactly times **50 and 100** on disk. `startFrom` was then switched
  to `latestTime` and the solver relaunched; it resumed at **Time = 101** and ran to 300.
  `rc=0`.

Loss from the kill: **20 iterations**, the interval between the last checkpoint (100) and the
kill (120) — the miniature of her 30-minute bound, and the bound that gate A now enforces.

## 2. The numbers

Force on the wall patch, x-component, at iteration 300, from
`postProcessing/forces/<start>/force.dat`:

| arm | force_x at 300 |
|---|---|
| `ref` (unkilled) | `2.275999999990e+00` |
| `kill` (killed at 120, resumed from 100) | `2.275999999990e+00` |
| **absolute difference** | **0.000e+00** |

Volume-average U, x-component, at iteration 300, from `postProcessing/Ubar/<start>/volFieldValue.dat`:

| arm | Ubar_x at 300 |
|---|---|
| `ref` | `1.014815998432e+00` |
| `kill` | `1.014815998432e+00` |
| **absolute difference** | **0.000e+00** |

The `.dat` files carry 12 significant digits, so the honest statement of the agreement is
**identical at every digit recorded**, i.e. a relative difference below 5e-13. The solver's
own linear tolerances are 1e-10 (p) and 1e-12 (U); the agreement is tighter than either.
The transverse components differ at O(1e-17), which is round-off noise about zero.

**And it is not only the endpoint.** The resumed arm reproduces the reference's whole
trajectory, iteration by iteration:

| iteration | `ref` force_x | `kill` force_x | difference |
|---|---|---|---|
| 101 | `2.275874427672e+00` | `2.275874427672e+00` | 0.000e+00 |
| 102 | `2.275884708255e+00` | `2.275884708255e+00` | 0.000e+00 |
| 110 | `2.275941784534e+00` | `2.275941784534e+00` | 0.000e+00 |
| 150 | `2.275998088852e+00` | `2.275998088852e+00` | 0.000e+00 |
| 300 | `2.275999999990e+00` | `2.275999999990e+00` | 0.000e+00 |

## 3. The planted control — why this is evidence and not a tautology

A steady solver converging to a unique fixed point would give the same answer at iteration
300 whatever it restarted from, **including a restart that silently threw the checkpoint away
and began again from the `0/` initial fields**. Endpoint agreement alone therefore proves
little, and saying otherwise would be exactly the kind of zero this lab refuses (standing
rule 3).

What discriminates is the value AT THE RESUME POINT, and the reader is shown able to see the
other answer:

* `ref` force_x at iteration **1** (a cold start from `0/`) is **`8.205650989722e-01`** —
  **2.8× different** from the value at 101.
* The resumed arm's first recorded iteration, 101, reads `2.275874427672e+00`, matching the
  reference at 101 to all 12 digits.

A restart that had re-initialised instead of hot-starting would have produced ~0.82 at that
line and could not have been mistaken for a match. It did not.

Two further readings, each of which would have been visible had it failed:

* `kill/processor0/` held exactly `0 50 100` at the moment of the kill — `purgeWrite 2` kept
  the last two writes and no more, which is the policy under test, read off disk rather than
  assumed.
* The resumed log's first time line is `Time = 101`, and its functionObject series starts at
  101, not at 1 — the checkpoint was read, not bypassed.

## 4. Cost

Measured from the solvers' own `ExecutionTime` lines (the artifact, not an estimate):

| arm | ExecutionTime | ranks | core-min |
|---|---|---|---|
| `ref` 0 → 300 | 5.30 s | 4 | 0.353 |
| `kill` part 1, 0 → 120 (killed) | 2.42 s | 4 | 0.161 |
| `kill` part 2, 101 → 300 | 3.31 s | 4 | 0.221 |
| **solver total** | **11.03 s** | 4 | **0.735** |

Gross wall-clock for the whole driver, including two serial `decomposePar` runs, the kill
wait and the poll gaps: 55.2 s → **3.68 core-min** if every one of the 4 cores is charged for
the entire wall period (the pessimistic bound; the serial parts used one core).

**Registered ceiling for this proof: 10 core-min. Actual: 0.74 core-min measured on the
solvers, 3.68 core-min as a gross wall-clock bound. Ratio actual/predicted = 0.07 (measured
basis) or 0.37 (gross basis).** The estimate was conservative by roughly an order of
magnitude because it was written before the case was chosen; the F25 coarse level runs at
~0.021 s/iteration on 4 ranks, a rate now on record for anyone sizing the next proof.
Dollar figures are **derived, not measured** — this box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5).

## 5. What this does NOT establish

* **Only the steady OpenFOAM class.** The DAFoam optimisation class (history + design vector +
  hot-start) and the OpenFOAM transient class (fields + time-averaging accumulators) each need
  their own proof under her item 5. Both are **PENDING**.
* **Only this case's shape.** A laminar 32.8k-cell duct with `writeFormat ascii` and
  `writePrecision 12` restarts about as cleanly as anything can. A turbulent case restarts
  additional state (`nut`, `k`, `omega`, wall functions); a case with `writeFormat binary` or
  a lower precision would round-trip less exactly. The 12-digit agreement here is a property
  of this configuration and must not be quoted as a general figure.
* **Nothing about the runner's gates.** This proof was driven by a standalone script, not by
  `scripts/queue_runner.py`. The gates landing in the same commit are exercised by that
  script's `--selftest`, separately.

## 6. Artifacts

Everything cited above is on disk under `/home/ubuntu/certonomous-runs/KILL_RESUME_PROOF/`:

* `ref/log.simpleFoam`, `ref/RC.log.simpleFoam` (rc=0), `ref/postProcessing/forces/0/force.dat`,
  `ref/postProcessing/Ubar/0/volFieldValue.dat`
* `kill/log.simpleFoam.part1` (120 `Time =` lines, no `End`),
  `kill/log.simpleFoam.part2` (200 `Time =` lines, ends `End`), `kill/RC.log.simpleFoam.part2`
  (rc=0), `kill/TIMES_AFTER_KILL.txt` (`0 constant 50 100`),
  `kill/ALIVE_AFTER_KILL.txt` (`0` — nothing survived the SIGKILL),
  `kill/postProcessing/forces/100/force.dat`, `kill/postProcessing/Ubar/100/volFieldValue.dat`
* `*/system/controlDict` — the policy under test, as it ran.

Run by the chief's infrastructure lane, 2026-09-12 ~18:34Z, on the r7a.4xlarge (16 cores,
123 GiB) rebooted at 17:36Z.
