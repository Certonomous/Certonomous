# F18-TG2D — 2-D decaying Taylor–Green vortex (`icoFoam`, periodic box) — GRADED RECORD

Team cfd. Pre-registration `verification/campaign/F18_TG2D_PREREGISTRATION.md`
frozen at **`c4f72b277d74ecce19c6f81d651038ab16c338af`**. **Instrument-check**
(`CASE_SELECTION_CHARTER.md` §3, labelled at registration): counts toward no
challenge column. Graded 2026-08-26 by a cfd lab-lane at **zero new compute**,
on a peer session's addition to the lane's brief (same rules as F17 / F16b).

Grader run **exactly as the launcher printed it**, plain `python3`:
`python3 /home/ubuntu/Certonomous/cases/F18_taylor_green/grade_f18.py --prereg-commit=c4f72b277d74ecce19c6f81d651038ab16c338af`
— **rc 0**. Stdout: `verification/runs/F18_runs/F18_GRADED.out`. Record:
`verification/runs/F18_runs/F18_GRADED.json` (the grader's default output path).
Gated by `scripts/roache_triple.py::grade_ladder`, one call node (0 `assert`
nodes across 4 files, planted assert seen).

## 1. VERDICTS — fixed vocabulary

| gate | fine value | registered band | triple (c, m, f) | observed p (grader) | GCI (Fs = 1.25) | verdict |
|---|---|---|---|---|---|---|
| G-F18-1 `E2_velocity_L2_at_T` | **1.101354e−05** | [3.153003e−06, 2.837702e−05] | **CONVERGING** (dim 2, r = 2.000, monotone) | **1.2894** | 221.4820 % = 2.439300e−05 absolute | **PASS** |
| G-F18-2 `mean_kinetic_energy_at_T` | **0.112337460** | [0.112318792, 0.112345690], exact 0.112332241 | **CONVERGING** (dim 2, r = 2.000, monotone) | **0.9638** | 0.0156 % = 1.748626e−05 absolute | **PASS** |

Level values (from `<level>/2/U`, read by the frozen reader), beside the
registered model:

| level | cells | h | Δt | E2(T) measured | E2 model (§4) | measured/model | KE(T) measured | KE − exact | KE error model |
|---|---|---|---|---|---|---|---|---|---|
| coarse | 4,096 | 0.098175 | 0.02 | 1.080786e−04 | 1.504101e−04 | 0.72 | 0.112376686 | +4.4445e−05 | +7.130385e−05 |
| medium | 16,384 | 0.049087 | 0.01 | 3.919587e−05 | 3.771909e−05 | 1.04 | 0.112350755 | +1.8514e−05 | +1.787910e−05 |
| fine | 65,536 | 0.024544 | 0.005 | 1.101354e−05 | 9.459008e−06 | 1.16 | 0.112337460 | +5.2189e−06 | +4.483101e−06 |

**Registered prediction (prereg §5): "both triples CONVERGING with observed
order p ≈ 2 (model 1.996); fine values inside both bands → PASS."**
- CONVERGING on both rows: **MET.** Fine values inside both bands: **MET.**
  Verdict PASS × 2, as predicted.
- **Observed order p ≈ 2: NOT MET by the grader's measure** — the registered
  three-level order (from the level-to-level differences e32, e21) is
  **1.289** on E2 and **0.964** on KE. Recorded as a miss of the prediction,
  not of the gate; the gate only turns PASS into NOT A RESULT through the
  triple state, and both triples are CONVERGING.
- Reading, not a verdict (this lane's arithmetic on the values above, stated
  so it is not mistaken for the grader's): the pairwise orders of the error
  against the exact solution are 1.46 (c→m) and **1.83** (m→f) on E2, and
  1.26 (c→m) and **1.83** (m→f) on KE. The coarse level (cell Reynolds 0.98,
  100 steps) sits off the h² line — its E2 is 0.72× the model, its KE error
  0.62× — while medium and fine track the model to 4–16 %. The three-level
  order is pulled down by the pre-asymptotic coarse level; the KE Richardson
  extrapolant 0.1123235 differs from the exact 0.1123322 by −8.8e−06, the
  same reading. Whether a fourth level is wanted is the supervisor's call; it
  is not registered here.
- The model's **positive sign** of the KE error (under-damped (1,1) mode,
  prereg §4) is confirmed at all three levels.
- The 221 % relative GCI on G-F18-1 is the relative form on a quantity whose
  Richardson extrapolant is −8.5e−06 (near zero, and negative — the
  pre-asymptotic coarse level again); the absolute GCI 2.44e−05 carries the
  meaning. Both printed as the grader printed them.

**Rule 5 limbs, in order.** (1) Iterative convergence: census of every time
step's final p residual over both PISO correctors against 1e−09 — **0 above
tolerance at every level** (200 / 400 / 800 readings; worst 9.99524e−10 /
9.96781e−10 / 9.99963e−10). Plateau: **ABSENT by construction** (value at a
fixed instant of a transient; `plateau_states = None`, recorded ABSENT in every
row as the prereg §6 requires — reported as absent, not as a pass). (2) Triple
CONVERGING on both rows. (3) Inside band → PASS.

**Planted-zero control (rule 3), into the real artefact through the real
reader** (`fine/2/U`): E2 — planted 1.223036e−03, read back 1.223036e−03
(delta 1e−18 class), `e2_from_files`; KE — planted 7.613780e−07, read back
7.613780e−07, `ke_from_files`. **Both PASS.** All 8 registered controls passed
(symbolic substitution into the unsteady NS with residuals identically 0 and
the 2.3ν decay plant non-zero; constant-ratio refinement in h and Δt; model
forced and second order; single `grade_ladder` call site both ways; solver
dictionaries agree with the registration; reader parses real solver-written
`U` on this box; L-342 field classes driven both ways).

## 2. FROZEN FILES — disk == blob at the pre-registration commit

Every path the freeze commit carries (the five the brief named and the case
dictionaries), checked `git hash-object <disk>` against `git rev-parse
c4f72b27:<path>` before grading — **13 of 13 SAME**:

| path | blob |
|---|---|
| `cases/F18_taylor_green/grade_f18.py` | `6ff39cb8` |
| `exact_f18.py` / `foam_io_f18.py` / `build_f18.py` / `run_f18.sh` | `cb84b382` / `4281f86b` / `042ee1c3` / `3a0b2c47` |
| `case/0/U.template`, `case/0/p.template` | `5ab01754`, `6eb92d17` |
| `case/constant/transportProperties` | `07c22d01` |
| `case/system/blockMeshDict.template`, `controlDict.template`, `fvSchemes`, `fvSolution` | `1c35d291`, `2927e0f0`, `f0be4f91`, `e52782bb` |
| `verification/campaign/F18_TG2D_PREREGISTRATION.md` | `3614fd11` |

## 3. RULE 4 — strict completion, re-read from the run root by this lane

| level | `RC.txt` | `End` lines | `Time =` lines == endTime/Δt | last Time == endTime | fields at `2/` | age guard (`0/U` → `2/U`, `2/p`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|
| coarse | 0 | 1 | 100 == 100 | 2 == 2 | U p (+ U_0, phi, phi_0) | 16:57:33.208 → 16:57:34.627 / .632 Z | 1 s / 1.39 s |
| medium | 0 | 1 | 200 == 200 | 2 == 2 | U p (+ U_0, phi, phi_0) | 16:57:36.275 → 16:57:54.225 / .243 Z | 18 s / 17.92 s |
| fine | 0 | 1 | 400 == 400 | 2 == 2 | U p (+ U_0, phi, phi_0) | 16:57:57.221 → 17:02:03.413 / .484 Z | 246 s / 246.17 s |

All clauses hold at every level; the grader's `completion()` agrees (`done:
True`, rc 0, `n_times` 100/200/400, `latest` 2.0). `Solving for Ux` at every
step (100 / 200 / 400 lines). Serial, 1 rank, `decomposePar` never invoked
(launcher output, decomposition seed `none`). Mesh gates at every level from
`log.checkMesh`: non-orthogonality 0°, skewness ≤ 2.2e−13.

## 4. COST — rule 12 estimate-versus-actual

| item | value |
|---|---|
| predicted (prereg §8) | **2.5 core-min** (coarse 0.03, medium 0.27, fine 2.18) from a flat 5 µs per cell-step; registered cap **30** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 1 s → 0.0167; medium 18 s → 0.3000; fine 246 s → 4.1000; **4.4167 core-min gross** |
| actual cleaned | **4.4167** — cleaned == gross (longest level 246 wall s; nothing matches the 3600-s stall rule) |
| waste, named separately | **0.000 core-min** — no stall, kill, re-run or cap movement |
| quantisation | ClockTime is integer-second: ± 0.0083 core-min per level |
| share of cap | 14.7 % |
| dollars | 4.4167 / 60 × $0.0513 = **$0.00378 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **1.767** |

**Gap attribution — misprediction of the rate's scaling with cell count, the
unknown the pre-registration named; not contention, not waste.** Measured
per cell-step: **2.44 / 5.49 / 9.38 µs** (coarse / medium / fine) against the
flat 5 µs basis borrowed from `VMFL019/L1_30` (480 cells). The driver is the
pressure solve: PCG/DIC at `tolerance 1e-9, relTol 0` took a mean of **76.7 /
144.0 / 257.4 iterations per solve** (max 87 / 167 / 321) — growing ≈ 1.8×
per level, i.e. ∝ N, as an un-preconditioned-in-scale Krylov solve on a
uniform grid does — so the cost per cell-step doubles at each level. The flat
rate matched the medium level (1.10×) and under-predicted fine by 1.88×.
Contention: **none** — ExecutionTime 246.17 s against ClockTime 246 s at fine
(0 %), launcher probe 6.9–7.2 free cores of 16. **Carry forward:** for
`icoFoam` PCG/DIC at 1e−9/relTol 0 on uniform 2-D grids, price the pressure
solve as ∝ N^1.5 (iterations ∝ N^0.5 per level-doubling of N here: 1.88× and
1.79×), or ≈ 10 µs per cell-step at 65k cells on this box; a flat rate from a
480-cell record does not extrapolate.

**Runner watchdog note (infrastructure, L-342):**
`cases/F18_taylor_green/CAP_OVERRUN.txt` (16:59:17Z, written by the queue
runner — neither the launcher nor the grader names that file) reads *"CAP
OVERRUN REPORTED, NOT ENFORCED: case F18_TG2D elapsed 190 s > 1.10 × registered
150 s (2.5 core-min / 1 ranks). The run was NOT killed"*. That is the runner
comparing wall time against the **estimate** (150 s), not against the
**registered cap** (30 core-min = 1,800 s): the cap was never approached
(4.42 of 30, 14.7 %), the launcher's own incremental cap check passed every
level, and rule 12's "an overrun stops the run" was not triggered. Named
here so the file is not read as a cap crossing. Whether the runner's watchdog
should key on the cap rather than the estimate is on the supervisor's desk.

Calibration row: landed in `docs/COST_CALIBRATION.md` in the same commit as
this record (id derived at commit time from the ledger's maximum existing id).

## 5. BOOKKEEPING — L-342 infrastructure fields; none touches the verdict

- `cases/F18_taylor_green/STATUS.F18_TG2D` reads `launcher_rc=0
  end=2026-08-26T17:02:03Z note=exit-status-of-the-launch-argv-NOT-the-solver-rc`
  — the launch argv's exit status, not the solver rc; the solver rc per level
  is `RC.txt` = 0 (§3). Runner outputs (`launcher.queue.out`,
  `queue_entry_F18_TG2D.json`, `CAP_OVERRUN.txt`) are the runner's records;
  not committed by this lane.
- The grader's `cost_claim` carries **no defects**; the cost claim above is
  not refused.
- The frozen grader was run with plain `python3`, never `-O` (the launcher's
  instrument line confirms `grade_f18 exits 2 under -O`).

## 6. NOT REGISTERED, NOT SENT

No fourth level; no re-grade of any row; no turbulence claim; no claim about p
beyond its role as an initial field. **Nothing is sent, filed, uploaded or
submitted** (rule 7). Field data stays on disk under
`verification/runs/F18_runs/` and is not committed.
