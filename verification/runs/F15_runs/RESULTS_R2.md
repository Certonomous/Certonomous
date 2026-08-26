# F15-OSR29 — oblique shock reflection, M∞ = 2.9 (`rhoCentralFoam`, serial ladder) — RUN COMPLETE; GRADED `PENDING` × 2 BY THE FROZEN COMPARATOR; F15-R2 COMPARATOR REFUSED

Team cfd. Run under `verification/campaign/F15_OSR29_PREREGISTRATION.md` frozen at
**`2aea29d97c74f54183c1d99a28d86568ee254815`** (v1.2: Amendment 1 serial at every
level, Amendment 2 the L-339 `set -u` guard, both pre-first-compute). Comparator
re-registration `F15_OSR29_R2_PREREGISTRATION.md` at
**`893cdeaf107771072d3b21fb592b49e8faac9742`**. Written 2026-08-26 by a cfd lab-lane
after `STATUS.F15` landed (`rc=0 end=2026-08-26T17:35:22Z`, the launch argv's exit
status — NOT the solver rc, which is `RC.txt` per level, §2). Zero new compute for
the grading.

## 0. THE TWO GRADINGS, AS THEY PRINTED — neither repaired

**(a) Frozen `grade_f15.py` (blob `e4076c03` at `2aea29d9`), exactly as the launcher printed, plain `python3`:**
`python3 /home/ubuntu/Certonomous/cases/F15_oblique_shock_reflection/grade_f15.py --prereg-commit=2aea29d9`
— **rc 0, both gates `PENDING`.** Stdout (`GRADE_F15.out`), verbatim:

    G-F15-1_E1_pressure_L1_y0.5              PENDING
        level 'coarse' is not complete: no `Time =` lines in the log
    G-F15-2_x_wall_impingement               PENDING
        level 'coarse' is not complete: no `Time =` lines in the log

It wrote `F15_GRADED.json` (rows PENDING, no values). This is defect (i) of the R2
pre-registration §2 exactly as predicted there: `TIME_RE` is `^`-anchored without
`re.MULTILINE`, so it reads 0 of 9,233 `Time =` lines in a log whose `grep -c '^Time = '`
is 9,233. The frozen comparator did **not** refuse (exit 2); it returned PENDING on
complete levels, as F16's did at `6f8048b9`.

**(b) `grade_f15_r2.py` (blob `133820b3` at `893cdeaf`), the R2 prereg's registered command:**
`python3 /home/ubuntu/Certonomous/cases/F15_oblique_shock_reflection/grade_f15_r2.py --prereg-commit=893cdeaf107771072d3b21fb592b49e8faac9742`
— **rc 2, REFUSED.** Stdout empty (`GRADE_F15_R2.out`); stderr (`GRADE_F15_R2.err`), verbatim:

    REFUSED: /home/ubuntu/Certonomous/verification/runs/F15_runs/coarse/postProcessing/lineWall/0.05/lineWall_p.xy: the wall pressure never crosses the half-rise value 1.824133; min 0.714286 max 0.714286. The gate quantity is ABSENT, which is reported as absent and never graded as a pass.

**No `F15_R2_GRADED.json` was written** — the comparator exits before the record.
**Where it comes from (read, not repaired):** `x_wall_from_xy` (`grade_f15_r2.py:252–263`,
inherited unchanged from `grade_f15.py:163`) refuses whenever a wall-pressure sample has
no half-rise crossing; `series_for` (`:832`) feeds it **every** sampled time of the
Class C series, and the sampler writes from t = 0.05 (200 sample times). At t = 0.05 the
incident shock has not reached the wall — the whole line reads the free-stream p1 =
0.714286. **The first sample with a crossing is t = 0.75** (max 2.5848). So this is a
third reader defect of the same lineage — the crossing detector is applied to
pre-arrival samples — and it is not one the R2 registration named. The frozen parent
never reached this code because defect (i) returned PENDING first. **Per the brief and
rule 2, nothing is repaired here**: the R2 comparator's refusal is recorded verbatim and
the repair, if wanted, is a NEW registration (F15-R3) for the supervisor.

**Row state: `PENDING` on both gates** (the frozen path's own reading; the R2 path
refused). The registered prediction p ≈ 1 is **untested** by either comparator.

**The physics artefacts are intact and non-trivial** (§2): wall pressure at t = 10
spans 0.714286 → 3.1665 at coarse; `Solving for rho, rhoUx, rhoUy, rhoE` at every step;
0 `FOAM FATAL`, 0 `nan` in the fine log.

## 1. FROZEN FILES — disk == blob at both registration commits

At `2aea29d9`, every path the freeze carries — **13 of 13 SAME**: `grade_f15.py`
`e4076c03`, `exact_osr.py` `074d18c2`, `run_f15.sh` `44f92e59`, `case/0/{T,U,p}`
`8352231d`/`18a4562c`/`302209d8`, `constant/{thermophysicalProperties,turbulenceProperties}`
`aff1712e`/`ba5bb3d1`, `system/{blockMeshDict.template,controlDict.template,fvSchemes,fvSolution}`
`4e3e97af`/`2136e851`/`aace4acc`/`12f165de`, `F15_OSR29_PREREGISTRATION.md` `43401856`.
At `893cdeaf` — **2 of 2 SAME**: `grade_f15_r2.py` `133820b3` (as the R2 prereg states),
`F15_OSR29_R2_PREREGISTRATION.md` `8acaa5bf`.

## 2. RULE 4 — strict completion, re-read from the run root by this lane

Adaptive Δt (`maxCo 0.2`): the completion clause is `latest + dt_final > endTime`, per
prereg §6; the fixed-count identity does not apply and the substitution is the prereg's.

| level | cells | `RC.txt` | `End` | `Time =` lines | last Time | dt_final | latest + dt > 10 | fields at `10/` | age guard (`0/T` → `10/T,U,p`) | ClockTime / ExecutionTime |
|---|---|---|---|---|---|---|---|---|---|---|
| coarse | 10,000 | 0 | 1 | 9,233 | 10 | 1.136364e−03 | yes | T U p | 16:13:47.919 → 16:14:55.570–.573 Z | 68 s / 67.58 s |
| medium | 40,000 | 0 | 1 | 18,760 | 10 | 5.681818e−04 | yes | T U p | 16:14:56.526 → 16:23:40.353–.367 Z | 524 s / 523.05 s |
| fine | 160,000 | 0 | 1 | 37,851 | 10 | 2.833557e−04 | yes | T U p | 16:23:43.560 → 17:35:22.595–.660 Z | 4,299 s / 4,135.44 s |

All clauses hold at every level. Serial, 1 rank, `decomposePar` never invoked
(Amendment 1; launcher output, seed `none`). Wall samples: `lineWall`, `lineY05`
at 200 times to t = 10 at every level; `pAvg` monitor present.

## 3. LAUNCH PROVENANCE (L-186)

The launcher's stdout was redirected by the launching shell to a scratchpad file
(`f15_attempt2.out`); a scratch path is not a record, so it is **copied verbatim into
this run root as `launcher.out`** (2,336 bytes, ends `ALL THREE LEVELS COMPLETE.
Cumulative spend: 81.51666666666667 core-min of 200`). `STATUS.F15` was written by
the same shell on the launcher's exit. **Attempt 1** (`STATUS.F15.attempt1`:
`rc=1 end=2026-08-26T16:12:33Z`) died at zero compute at the OpenFOAM bashrc source
under `set -u` (L-339, the face Amendment 2 repaired): **0 core-min, named as waste
of zero**.

## 4. COST — rule 12 estimate-versus-actual (the run's spend; the gradings cost 0)

| item | value |
|---|---|
| predicted (prereg §8, Amendment 1: unchanged) | **122.2 core-min** (1.7 / 13.4 / 107.1) at 1.03 µs per cell-step from `VMFL045/R2`; registered cap **200** |
| actual, MEASURED from the logs' `ClockTime × ranks ÷ 60` | coarse 68 s → 1.1333; medium 524 s → 8.7333; fine 4,299 s → 71.6500; **81.5167 core-min gross** (= the launcher's tally) |
| actual cleaned, **by the charter §2 rule mechanically applied** | the fine level (4,299 wall s) **matches the 3600-s stall rule**, so rule-cleaned = 9.8667 core-min. **It is not a stall**: 37,851 monotone steps to `Time = 10`, ExecutionTime 4,135 s = 96 % of ClockTime, fields written, and the level was pre-registered at 6,427 s. Both figures are stated; which one the ledger's cleaned column should carry is the supervisor's reading — this record uses gross for the ratio and says so |
| waste, named separately | **0.000 core-min** (attempt 1 died before any solver ran) |
| quantisation | ± 0.0083 core-min per level |
| share of cap | 40.8 % |
| dollars | 81.5167 / 60 × $0.0513 = **$0.0697 — DERIVED, NOT MEASURED** ($0.0513/core-h, c7a.4xlarge, reported-by-owner; `COMPUTE_BUDGET_CHARTER.md` §5) |
| **ratio actual/predicted** | **0.667** (gross) |

**Gap attribution — misprediction of the rate basis, with a physical reason; not
contention, not waste.** Measured **0.736 / 0.698 / 0.710 µs per cell-step**
(coarse / medium / fine), flat across a 16× cell-count span, against the 1.03 µs basis
from `VMFL045/R2`. That basis case runs `mu 1e-8` — viscous, so `rhoCentralFoam`
assembles the `tauMC`/Laplacian terms every step; this case is `mu 0`, for which the
solver skips them. 0.70/1.03 = 0.68 ≈ the ratio. Contention: **small** — 96 % at fine
(4,135 vs 4,299 s), 99.8 % at medium; the launcher probe read 4.0–4.5 free cores of 16.
**Carry forward:** inviscid `rhoCentralFoam`, serial, 2-D, on this box ≈ 0.70 µs per
cell-step; viscous ≈ 1.03.

Calibration row: landed in `docs/COST_CALIBRATION.md` in the same commit as this
record (id derived at commit time from the ledger's maximum existing id).

## 5. NOT REGISTERED, NOT SENT

No repair of either comparator; no re-grade; no change to any band. The F15/F16
ladder-instrument comparison (p ≈ 1 vs p ≈ 2) waits on an F15 grade. **Nothing is
sent, filed, uploaded or submitted** (rule 7). Field data stays on disk under this run
root and is not committed.
