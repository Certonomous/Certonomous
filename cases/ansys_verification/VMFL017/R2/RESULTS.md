# VMFL017-R2 — Transonic Flow over an RAE 2822 Airfoil: `NOT A RESULT` (measured instrument limit)

## VERDICT: `NOT A RESULT` — the registered cap fired, and the frozen comparator REFUSED (exit 2)

L1 stopped at its own pre-registered per-level cap with `rc = 124`; the launcher then
stopped **without launching L2 or L3**, exactly as registered; and the frozen comparator
refused on the strict-completion clause. **This is a measured statement of an explicit
instrument's limit at this cost, not a failed solve and not a fabricated number.** Graded
by `ansys-lane-opus`, **2026-08-26**, for the supervisor's audit. Manual p. 69; reference
AGARD AR-138 (Cook, McDonald & Firmin, 1979); tier ceiling `GATE REACHED`, never reached.

**New row citing attempt 1 (register row #19, `PENDING`, `rhoSimpleFoam`, commit
`d1de064b`).** Row #19 stays exactly as it is — not removed, not re-labelled.

**THE PRE-REGISTRATION PREDICTED THIS OUTCOME BY NAME, IN ADVANCE, WITH NUMBERS, AND THE
NUMBERS LANDED.** PRE-COMPUTE AMENDMENT 2 §E, frozen at `45328f8a` before the launch:
*"L1 is expected to stop at its own cap with rc 124, the launcher then stops without
launching L2 or L3, and the case is `NOT A RESULT`."* **A correctly predicted failure is
still a failure and the verdict is unchanged by having been foreseen.**

### The refusal, exactly — verbatim from `GRADING.txt`

`python3 cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py --run-root <run root>`
→ **exit 2**:

> REFUSE (VMFL017-R2): no End line in solver log: /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL017/R2/L1
> VMFL017-R2  p-floor planted control OK (P_MIN = 0.05): (1.0,1.1,1.2) -> NOT A RESULT, no GCI

No grading JSON exists: the comparator refused before writing one. The captured
stdout/stderr and rc are at
`verification/runs/ansys_verification/VMFL017/R2/GRADING.txt`.

### THE FREEZE HELD — checked, not asserted

| file | on disk | at `45328f8a` (freeze) | at HEAD |
|---|---|---|---|
| `cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py` | `97c556f4a0d07f021480c75144d1b72a811fc391` | same | same |
| `cases/ansys_verification/VMFL017/R2/PREREGISTRATION.md` | `9a58eed3413b7b54b92bbfbee527c7a913cbd8ec` | same | same |

`launcher.queue.out` records `freeze OK` against both blobs before the solver started, and
`RUN_RC.L1` and `LAUNCH_RECORD.txt` carry them independently. Twelve further registered
pre-flight assertions printed `registered OK` in the same file — `endTime = 0.05`,
`deltaT = 1e-9`, `maxCo = 0.2`, `maxDeltaT = 1e-5`, `writeControl adjustableRunTime` with
`writeInterval = 0.05` and `adjustTimeStep yes`, `forceCoeffs1 executeInterval = 1e-4`,
the comparator's `ENDTIME_PHYS == controlDict endTime`, the 500-sample /
20-in-final-window plateau precondition, the mesh birth certificate
(`2a7e82c280c2bad9c191996a26013ca4decf4e6c`), the L1/L2/L3 `blockMeshDict` identity with
the birth-certified attempt-1 family, and the comparator `--selftest` green.

### STRICT COMPLETION (rule 4) — FAILS AT L1, ON THE REGISTERED CLAUSE

| level | `rc` | `End` lines | last `Time` (s) | `endTime` (s) | fraction reached | time dir at `endTime` | age guard | wall s | core-min | cap |
|---|---|---|---|---|---|---|---|---|---|---|
| L1 | **124** | **0** | 8.89114e-04 | 5.0e-02 | **1.778 %** | none | n/a (no field at `endTime`) | 18 000 | **300.0** | 300 |
| L2 | — | — | — | — | — | **NOT LAUNCHED** | — | 0 | 0 | 600 |
| L3 | — | — | — | — | — | **NOT LAUNCHED** | — | 0 | 0 | 1 500 |

`rc = 124` is `timeout` firing at `timeout_s = 18000` = cap 300 core-min × 60 ÷ RANKS 1.
The launcher's own stop text, verbatim from `launcher.queue.out`: **`STOP L1: rc=124 after
18000s = 300.0 core-min (cap 300 core-min).`** followed by *"A non-zero rc is a FINDING,
not a retry. rc=124 means the per-level cap stopped it; an overrun does NOT get a new
budget and endTime is NOT shrunk to fit (rule 12)."* `LAUNCH_RECORD.txt` records
**`later levels are NOT launched`**. **`endTime` was never reduced to fit the cap.**

### THE MEASUREMENT THIS ROW ACTUALLY BUYS — the explicit instrument's cost, converted from a projection into a graded-path number

The pre-registration's §E smoke projection was made before compute, on a scratch smoke, and
is now confronted with the real run. **Every one of its three numbers held.**

| quantity | registered §E projection (before compute) | MEASURED on the graded run | ratio |
|---|---|---|---|
| physical time L1 reaches inside its 300 core-min cap | ≈ 9.0e-04 s (≈ 1.8 % of `endTime`) | **8.89114e-04 s (1.778 %)** | **0.988** |
| integration rate, RANKS = 1 | ≈ 27.7 steps per wall-second | **27.04** (486 748 steps in 17 999 wall s) | **0.976** |
| core-min for L1 alone to reach `endTime` 0.05 s | ≈ 16 700 core-min (≈ 55× the cap) | **16 871 core-min** (300.0 × 0.05 ÷ 8.89114e-04) | **1.010** |

Realised adaptive step at the stop: **Δt = 1.852520264e-09 s** (§E registered 1.806e-9 s at
`maxCo` 0.2). **Contention is falsified as the cause of the stop, and it is measured, not
argued:** `ExecutionTime = 17 761.7 s` against `ClockTime = 17 999 s` is **98.68 % CPU-bound**
on a box carrying load average 13.73 of 16 cores at launch (`CONTENTION.txt`, 17:18:52Z).
**The process was computing, not starved.** The cap did not fire because the box was busy;
it fired because an explicit CFL-limited integration of a Re = 6.5e6 turbulent boundary
layer at Δt ≈ 1.85e-9 s needs ~2.7e7 steps to cross 0.05 s of physical time.

**L2 and L3 are worse by ≈ 8× and ≈ 64×** (four/sixteen times the cells at half/quarter the
step), so the registered family ceiling of 2 400 core-min is not within one order of
magnitude of what `rhoCentralFoam` would need here. **That is the finding.**

### What this row does NOT claim

**No lab value exists.** No `Cd`, no `Cl`, no plateau window, no triple, no observed order,
no GCI — the run never reached a settled state and the comparator refused before any of
them. The bands (`|Cd − 0.0168|/0.0168 ≤ 0.10` **and** `|Cl − 0.803|/0.803 ≤ 0.05`) were
**never evaluated**. Nothing here says the RAE 2822 case is beyond this lab; it says
**`rhoCentralFoam`, explicit, at the registered `endTime` and the registered caps, is the
wrong instrument for this case's cost**. The alternative named in the freeze — a
stiff-capable or implicit/dual-time formulation, or a wall function raising the near-wall
cell by three decades — is a **different registration** and is not claimed here.

**The `P_MIN = 0.05` planted control fired** on the refusal path and is printed in
`GRADING.txt`: `(1.0,1.1,1.2) -> NOT A RESULT, no GCI`. The `PLANT = 7.531e-3` planted-zero
control was verified green in the launcher's pre-flight `--selftest`; it was **not** reached
on the graded path, because there was no settled window to read.

### Artifacts on disk (and at HEAD with this commit)

`verification/runs/ansys_verification/VMFL017/R2/` — `GRADING.txt`, `RUN_RC.L1`,
`STATUS.VMFL017-R2`, `LAUNCH_RECORD.txt`, `CONTENTION.txt`, `launcher.queue.out`, and
`L1/log.blockMesh`, `L1/log.checkMesh`,
`L1/postProcessing/forceCoeffs1/0/coefficient.dat`.

**Disclosed, not hidden:** `L1/log.rhoCentralFoam` is **528 629 457 bytes (504 MB)** —
486 748 timesteps at full print — and is **far over the 5 MB per-file staging refusal**, so
it stays **on disk only**. The three clauses read out of it (zero `End` lines, last
`Time = 8.89114e-04`, `ExecutionTime = 17 761.7 s` against `ClockTime = 17 999 s`) are each
quoted above and the first two are independently recorded in `RUN_RC.L1` and
`LAUNCH_RECORD.txt`, which are at HEAD. There is **no `COST.txt`** at this run root — the
launcher stopped on the cap before writing one; the core-minutes are taken from `RUN_RC.L1`
(`core_min = 300.0`) and `LAUNCH_RECORD.txt` (`total_core_min = 300.0`), which agree. The
`0/` fields and `constant/polyMesh` stay on disk by the same ruling.

### Provenance

- **Prereg sha:** `9a58eed3413b7b54b92bbfbee527c7a913cbd8ec`, frozen at commit
  **`45328f8a4268e3d425a34be42f20ccc378c3e62f`**, before any R2 solver started.
- **Comparator blob:** `97c556f4a0d07f021480c75144d1b72a811fc391` — equal on disk, at the
  freeze commit and at HEAD.
- **Launcher:** `cases/ansys_verification/VMFL017/R2/run_vmfl017_r2.sh`; it stopped at its
  own line 279 (`if [ "$RC" -ne 0 ]` → `break`), which is where the registered
  "no later levels" behaviour lives.
- **Launched** 2026-08-26T17:18:52Z (pid 257744, `timeout 18000`), **stopped**
  2026-08-26T22:18:53Z; `STATUS.VMFL017-R2` reads
  `launcher_rc=124 end=2026-08-26T22:18:55Z`.
- **Mesh:** birth-certified ratio-2 C-mesh family reused from the frozen attempt-1
  `blockMeshDict`s, verified identical by the launcher before compute.
- **Supersedes nothing:** register row #19 (VMFL017 attempt 1, `PENDING`) is unchanged.

## COST (rule 12 calibration)

- **Measured actual: 300.0 core-min** = 18 000 wall s × RANKS 1 ÷ 60 (`RUN_RC.L1`
  `core_min = 300.0`; `LAUNCH_RECORD.txt` `total_core_min = 300.0`). **100.0 % of L1's
  registered per-level cap** — the cap fired exactly, to the second.
- **Pre-registered estimate: 300.0 core-min** for this launch (the queue entry's
  `cost_core_min_estimate`, keyed to L1's cap from `PREREGISTRATION.md` line 12 and to
  AMENDMENT 2 §E's registered expectation that L1 stops at that cap). **Ratio
  actual/predicted = 1.000.** The prereg's *family* figure — "~800–1600 core-min TOTAL",
  declared **UNCERTAIN** and a **runaway-guard basis, not a confident point estimate** —
  was never the operative prediction for this launch and is not used as the denominator.
- **Gap attribution: none. There is no gap.** The ratio is 1.000 because the spend was a
  **cap**, not a forecast — a cap that fires is a budget statement, not a prediction that
  came true, and this row says so rather than banking a false calibration win. **The real
  calibration content is the §E projection**, which predicted the *physics reached* inside
  that cap to **1.2 %** (8.89e-04 s measured against 9.0e-04 s projected) and the *total
  cost to `endTime`* to **1.0 %** (16 871 against 16 700 core-min).
- **Waste: 0.000 core-min** in the `COMPUTE_BUDGET_CHARTER` §6 sense — nothing was
  abandoned, re-run or thrown away, and the cap stopped the level exactly as registered.
  **Named separately and NOT laundered into the ratio: 300.0 core-min bought no graded
  number.** That is the price of the measurement, disclosed in advance and paid on
  purpose; it is not waste, and calling it waste would hide that the lab chose to buy it.
- **$ derived: 300.0 core-min ÷ 60 × $0.0513/core-h = $0.2565** — **DERIVED, NOT
  MEASURED**; the rate is REPORTED-BY-OWNER (c7a.4xlarge, Sanaa 2026-08-21/22) and the box
  cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Inside the 2026-08-21
  under-$25 blanket, and still costed per item.

**Ledger follow-up:** register row **#32** and the calibration row land with this record.
The register's credential-count headline is **not** struck: the verdict is `NOT A RESULT`,
so the `PASS` count does not move.
