# Resize census — 2026-09-12 stop/resize/boot

**Status: DRAFT, NOT COMMITTED. Read-only census. No run was launched, killed or edited to produce it.**

Produced by a census lane for the chief, on Sanaa's order
*"No team does anything else until we sort this out"* and her request for
*"(1) list which cases resumed from checkpoint and which need relaunching from their last write"*.

| Field | Value | Source |
|---|---|---|
| Census run at | 2026-09-12 17:44:39 UTC | `date -u` |
| Box booted | 2026-09-12 17:36:41 UTC | `ps` START of pid 1 / `uptime` |
| Instance | r7a.4xlarge, 16 cores (AMD EPYC 9R14, 1 thread/core), 123 GiB | `nproc`, `lscpu`, `free -g` |
| Free RAM now | **116 GiB free, 120 GiB available** of 123 total; 15 GiB swap, 0 used | `free -g` |
| queue_runner | **running as `ubuntu`** (pid 1713, started 17:36:52), `scripts/queue_runner.py --daemon` | `ps -o user,pid,lstart,args -p 1713` |
| Queue depth | **empty** — no `*.json` under `verification/queue/*/` outside `launched/`, `held/`, `refused/` | `ls -la verification/queue/*/` |
| Other daemons | `chief_engineer.server` (pid 1737, ubuntu), `http.server 8080` (pid 1741, ubuntu) | `ps` |

## Did anything resume?

**NONE. Not one case resumed from checkpoint.**

Planted control on the question rather than an assertion: a resumed solver would have
written to its run directory after the boot. A sweep of both run roots for **any** file
with mtime later than 17:36:41 returns:

- `verification/runs/` — **2 files**, both `FLEET_CEILING/ceiling_tick_{latest.json,log.tsv}`
  at 17:49:55, written by the `chief_engineer.server` daemon. Neither is a solve.
- `/home/ubuntu/certonomous-runs/` — **0 files**.

Corroborated by process presence: `ps -eo user,pid,args` shows no `simpleFoam`,
`rhoSimpleFoam`, `rhoCentralFoam`, `chtMultiRegionFoam`, `mpirun`, `python runScript*`
or any DAFoam container. `docker ps` (running) is empty; all 8 containers in
`docker ps -a` are `Exited`.

## The table

Ranks column: `numberOfSubdomains` from the case's own `system/decomposeParDict`, or
`processor*` count on disk. "Lost" counts iterations between the last complete checkpoint
and the last `Time =` in the log. Core-minutes are **gross** (ClockTime x ranks / 60) and
include the heavy contention stalls visible in every watcher log tonight; they are the
cost of the wall-clock window, not of useful work.

### A. Live at the stop — killed mid-solve (13)

| # | Case | Team | Run dir | Solver / container | Last log `Time =` | Last time dir on disk + completeness | endTime / target | Resumable from checkpoint? | What would be lost | Ran as root? | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | VMFL017-R3 L3 | ansys | `verification/runs/ansys_verification/VMFL017-R3/L3` | `rhoCentralFoam`, 1 rank, host (no container) | **0.0489014** (517,182 `Time =` lines; adjustTimeStep yes, maxCo 0.2) | **NO FIELD CHECKPOINT.** 490 time dirs exist; **489 of them hold only `yPlus`** (a functionObject at writeInterval 1e-4). Exactly one dir — `0` — holds `T U alphat k nut omega p`. Field `writeInterval` is 0.05 = endTime, so the first and only field write was to have been at the finish. | 0.05 s | **NO** — `startFrom startTime` and there is no later dir with fields to point `latestTime` at | **The whole run: 97.8 % of the physical endTime.** Started Sep 08 12:19:25; ExecutionTime 321,237.87 s = 89.2 h of solver CPU; ~6,060 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 2 | VMFL078-R2 F3 (128^3) | ansys | `verification/runs/ansys_verification/VMFL078-R2/F3` | `simpleFoam`, 4 ranks, host | **460** | `processor*/0` only — 2 files each (`U`, `p`), the initial condition. No later dir. | 40000 (residualControl stops earlier; F1 stopped at 444, F2 at 839) | **NO** — `writeInterval 40000` never fired | 460 iterations; started 06:46:46, ClockTime 35,470 s, ~2,365 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 3 | DRIVAER r2 coarse | cfd | `verification/runs/navier_class/DRIVAER/r2_coarse` | `simpleFoam`, 4 ranks, host | **1415** | **`processor*/1000` — COMPLETE.** Present in all 4 processor dirs, 7 entries each (`U k nut omega p phi` + `uniform/`), written 05:06. | 2000 | **YES**, after a one-line edit: `startFrom startTime` -> `latestTime` in `system/controlDict`. Checkpoint at t=1000 is intact in all 4 processor dirs. | **415 iterations** (1000 -> 1415). Launched 01:23:40; ExecutionTime 11,235.63 s, ClockTime 57,835 s, ~3,856 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM LAST WRITE (t=1000)** |
| 4 | DRIVAER r2c coarse blended | cfd | `verification/runs/navier_class/DRIVAER/r2c_coarse_blended` | `simpleFoam`, 4 ranks, host | **448** | `processor*/0` only — 5 files each. No later dir. | 2000 | **NO** — `writeInterval 1000` never fired | 448 iterations. Launched 05:18:47, solver start 05:19:26; ClockTime 43,694 s, ~2,913 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 5 | DRIVAER r2c medium blended | cfd | `verification/runs/navier_class/DRIVAER/r2c_medium_blended` | `simpleFoam`, 4 ranks, host | **117** | `processor*/0` only — 5 files each. No later dir. | 2000 | **NO** — `writeInterval 1000` never fired | 117 iterations. Launched 05:27:31, solver start 05:30:33; ClockTime 41,381 s, ~2,759 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 6 | SUBOFF A1 SOLVE_L1 | cfd | `verification/runs/navier_class/SUBOFF_A1/SOLVE_L1` | `simpleFoam`, 4 ranks, host | **369** | `processor*/0` only — 5 files each. No later dir. | 3000 | **NO** — `writeInterval 3000` never fired | 369 iterations. Started 01:46:28; ClockTime 49,425 s, ~3,295 core-min gross. Its own `WATCH.log` records the run pinned at iteration 368 from 16:04 on ("STALL ... NOT KILLED ... the box has run heavily oversubscribed"), so most of the last hour bought nothing. | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 7 | CRM wing-alone SOLVE_L2 | cfd | `verification/runs/CRM_WINGALONE_runs/SOLVE_L2` | `rhoSimpleFoam`, **6 ranks**, host | **1012** | `processor*/0` only — 7 files each (`T U alphat k nut omega p`). No later dir. | 4000 | **NO** — `writeInterval 4000` never fired | 1012 iterations. Started 04:36:12; ExecutionTime 15,702.35 s, ClockTime 45,452 s, ~4,545 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 8 | T5F CUBE fine | heat-transfer | `verification/runs/T-family/T5f_runs/T5F_CUBE_f` | multi-region (`air` + `epoxy`), **1 rank**, host | **147** | Only `0/` and `0.orig/`. No later dir. | 5000 | **NO** — `writeInterval 1000` never fired (and `purgeWrite 3`) | 147 iterations. Started 06:11:03, pid 2928094; ExecutionTime 902.37 s but ClockTime 35,886 s — i.e. **2.5 % CPU efficiency**, the run was almost entirely starved. ~598 core-min gross. | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM SCRATCH** |
| 9 | K2f L3 | heat-transfer | `verification/runs/F14-cooling-ladder/K2g_runs/K2f_L3` | `log.solve` (buoyant thermal), 4 ranks, host | **835** | **`processor*/500` — COMPLETE.** All 4 processor dirs, 10 entries each (`T U alphat k nut omega p p_rgh phi` + `uniform/`), written 06:08. | 2000 | **YES, with no edit at all** — its `system/controlDict` already carries `startFrom latestTime`. This is the only case on the box configured to resume itself. | **335 iterations** (500 -> 835). Started 04:06:20; ExecutionTime 11,728.96 s, ClockTime 47,231 s, ~3,149 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM LAST WRITE (t=500)** |
| 10 | T4e IJ fine | heat-transfer | `verification/runs/T-family/T4e_runs/T4e_IJ_f` | `log.solve`, **1 rank**, host, serial (no `processor*`) | **104646** | **`104000/` — COMPLETE and untruncated.** 9 fields (`T U alphat k nut omega p p_rgh phi`) + `uniform/{time,cumulativeContErr,functionObjects}`; every field ends with the OpenFOAM `// ****` banner; `uniform/time` reads `value 104000; index 104000; deltaT 1`. Written 07:25:57. Age guard holds: `0/T` is dated 2026-09-10 15:44:05, the 104000 fields 2026-09-12 07:25 — **newer**. | 160000 | **YES**, after `startFrom startTime` -> `latestTime`. Checkpoint ladder is dense (writeInterval 4000; dirs to 104000 all present). | **646 iterations** (104000 -> 104646) — by far the cheapest loss on the box. ExecutionTime 140,491.03 s, ClockTime 178,145 s, ~2,969 core-min gross | no (`ubuntu:ubuntu`) | **NEEDS RELAUNCH FROM LAST WRITE (t=104000)** |
| 11 | D6R2 arm O_mp | dafoam | `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic/O_mp` | container `d6r2_O_mp_20260912T033601Z_2772281`, image `dafoam-idwarp-rot:v1`, 4 ranks. Started 03:36:01, **Finished 17:32:57 exit 255** (the stop; not OOM) | primal `Time = 1000` per design iteration (`D6R2_WATCH.tsv` last row 17:31:00) | **Design state:** `OptView.hst` (3.19 MB, 17:26:59) and `opt_IPOPT.txt` (17:26:59) exist. IPOPT table shows **iterations 0-12 complete**, a 13th in flight. Multipoint dirs `mp04/ mp05/ mp06/` hold `processor*` trees written to 17:28. | IPOPT `max_iter: 25` | **NO, as the run script stands.** `d6r2_opt_runScript.py` has **no `hotStart`, no `storeHistory`, no restart branch** — grep for `restart\|hotStart\|storeHistory` returns nothing; the only matches in the file are `pyOptSparseDriver`, `max_iter: 25`, `MAXIT: 100`. `OptView.hst` *could* feed pyOptSparse's `hotStart`, but that is a code change, not a restart the script supports. | **12 completed design iterations** (objective walked 3.0642e-02 -> 2.3260e-02) plus the partial 13th. Watch row 17:31:00 reads **3292.33 core-min measured** against a registered cap of 2900 — already logged `D4S_CAP_CROSSED ... action=REPORTED_RUN_CONTINUES`. | **YES — ROOT.** `docker inspect` `User=0:0`; `OptView.hst`, `opt_IPOPT.txt`, `mphys.html`, `reports/` and all `mp0*/processor*` trees are `root:root` | **NEEDS RELAUNCH FROM SCRATCH** (from-last-write only if someone first adds hotStart support — a pre-registration question, not a census one) |
| 12 | A3GC-L2R primal | dafoam | `/home/ubuntu/certonomous-runs/A3GC-L2R` | `docker run --rm --name a3gc_l2r --cpus=8 -u 1002:1000`, `mpirun -np 8 python runScript_a3gc.py`. Container used `--rm`, so it is gone from `docker ps -a`; killed at the stop (**no `primal.log.rc` was ever written**, and the wrapper writes rc unconditionally after `docker run`) | **400** (only 5 `Time =` lines in `primal.log`; log mtime 17:30:55) | `processor*/0/` holds `T.gz U.gz alphat.gz nuTilda.gz p.gz` — the initial condition (07:48-07:50). No later dir. | 6000 (`writeInterval 2000`) | **NO** — `startFrom startTime`, first write would have been t=2000 | 400 iterations. ExecutionTime 16,530.34 s, ClockTime 33,757 s at 8 ranks -> **~4,501 core-min gross**, the second-largest loss on the box. Pre-registration frozen at `5eaa652fa`. | no — `-u 1002:1000`, outputs `ubuntu:ubuntu` | **NEEDS RELAUNCH FROM SCRATCH** |
| 13 | A3GC-L1 stage 1 (mesh gen) | dafoam | `/home/ubuntu/certonomous-runs/A3GC-L1` (driver `/home/ubuntu/certonomous-runs/A3GC-L1-launch`) | `a3gc_genmesh.sh` -> `docker run --rm --cpus=1` via the `bin/docker` resource shim; stage at the stop was **PLOT3D -> OpenFOAM conversion** | n/a (mesh generation, not a solve). `A3GC_L1_STAGE1_WATCH.txt` last tick **17:11:46**, reading `PLOT3D ... LOG-FROZEN-BUT-CPU-BUSY-NOT-A-STALL` | **`volumeMesh.xyz` — 437,206,919 bytes, complete, written 08:20** (pyHyp stage finished). `logMeshGeneration.txt` (12:01) ends mid-conversion at "Creating cells / Creating boundary patches". **No `constant/polyMesh` exists** — the conversion never landed. | L1 at exactly 6,389,760 cells (PREREG Sec. 2.5) | **PARTIAL YES.** The expensive pyHyp hyperbolic extrusion output (`volumeMesh.xyz`) survives on disk and does not need redoing; only the `plot3dToFoam` conversion must be re-run against it. Whether `a3gc_genmesh.sh` can be entered at that stage is **UNKNOWN to this lane** — the script is md5-pinned (`9fa240d9...`, AMENDMENT 5) and I did not read its stage logic, only its `docker run` line. | The conversion time only: watcher column reads 53,775 s wall / **896.2 core-min** at `--cpus 1`, of which the pyHyp part (to 08:20) is preserved. | no — `volumeMesh.xyz`, `surfaceMesh.cgns`, `logMeshGeneration.txt` all owned by **uid 1002** | **NEEDS RELAUNCH FROM LAST WRITE** (re-enter at plot3dToFoam, reusing `volumeMesh.xyz`) |

### B. Named in the brief but NOT live at the stop — no relaunch decision needed from the resize (9)

| Case | Team | Run dir | State on disk | Evidence |
|---|---|---|---|---|
| MRF R2 ET8000 fine | cfd | `verification/runs/navier_class/MRF/R2/ET8000/fine` | **COMPLETED before the stop.** `rc=0`, `RC.txt=0`, last `Time = 8000` == endTime 8000, 1 `End` line, `8000/` holds `U k nut omega p phi uniform yPlus`, reconstructed 04:36, yPlus 05:22. **No newer log exists** — the no-cap continuation the brief asked about was not restarted. | `cat rc`, `grep End`, `ls 8000/`, newest file in dir 05:22 |
| DRIVAER r2_medium | cfd | `verification/runs/navier_class/DRIVAER/r2_medium` | **Stopped deliberately at 05:21-05:26**, before the resize. `SOLVE_STOP.txt`, `COST_ACTUAL.txt`, `GRADE_STAGE_A_medium.out` and `log.reconstructPar.watch` all dated 05:22-05:26; `log.simpleFoam` frozen at 05:21. Not a resize casualty. | dir mtimes |
| SUBOFF A1 SOLVE_L2 | cfd | `verification/runs/navier_class/SUBOFF_A1/SOLVE_L2` | **NEVER LAUNCHED.** Its gated launcher ran to 17:25:04 and logged `GATE CLOSED available=0 GiB < 19` on every one of 251 readings from 03:34 onward. Dir holds only `0/`, `constant/`, `system/`, a manifest and a controlDict repair note. On the new box its 19 GiB gate would open immediately. | `SOLVE_L2.gatedlaunch.log` |
| MP_A5 R3 arm O | dafoam | `certonomous-runs/CURRICULUM-MP_A5-a5-ubend-multipoint-R3-.../O` | **OOM-KILLED 07:29:43**, ten hours before the stop. `docker inspect`: `Exit=137 OOMKilled=true`. `CHAIN_RC.txt=137`; `chain.out` records `ENDPOINT_DV_ABSENT: the driver left no record; the endpoint arm does not run`. Its successor `curriculum_MP_A5R` was frozen but never launched. | `docker inspect`, `chain.out` |
| MP_A5 R3 arm B | dafoam | same, `/B` | Completed 06:30:28, exit 0. | `docker inspect` |
| D6RF12 F_probe | dafoam | `certonomous-runs/CURRICULUM-D6RF12-a2-wing-fd-nutilda-repair/F_probe` | **Died 15:03:12 on its own, exit 1**, 2.5 h before the stop, not OOM. `STATUS.F_probe: rc=1 wall_s=27159 core_min=1810.6 inspect(exit,oomkilled)=[1 false]`. | `docker inspect`, `STATUS.F_probe` |
| D8G R1 L1-P-R1 | dafoam | `certonomous-runs/CURRICULUM-D8G-R1-a6-grid-triple/L1-P-R1` | **COMPLETED** 05:44:28, exit 0. `rc=0 wall_s=3293 core_min=219.533`. | `docker inspect`, `STATUS.L1-P-R1` |
| D8G R2 L1-P | dafoam | `certonomous-runs/CURRICULUM-D8G-R2-a6-grid-triple/L1-P` | **COMPLETED** 06:52:14, exit 0. `rc=0 wall_s=1480 core_min=98.667`. | `docker inspect`, `STATUS.L1-P` |
| A3GC-L2 / A3GC-AR1 / A3GC-AR1C | dafoam | `certonomous-runs/A3GC-L2`, `A3GC-AR1`, `A3GC-AR1C` | All finished before the stop: `primal.log.rc` = **1** (L2, 06:40), **0** (AR1, 05:34), **0** (AR1C, 09:18). AR1C's `AR1C_WATCH.txt` was still ticking at 17:30 and L2R/L1 watchers likewise — **watchers, not solvers**; the solves themselves had exited hours earlier. | `cat primal.log.rc`, watch tails |

## (a) Which ran as root

Root-owned outputs exist in **exactly one place on the box**: `/home/ubuntu/certonomous-runs/`,
and only from DAFoam containers launched with `-u 0:0`. `find -user root -newermt 2026-09-12`
returns **0 files** under `verification/runs/` and **0** under `cases/`, and **7,276** under
`certonomous-runs/`, attributed:

| Run dir | root-owned files written today | `docker inspect` User | Live at the stop? |
|---|---|---|---|
| `CURRICULUM-D6R2-a2-wing-multipoint-transonic` | 3,456 | **0:0** | **YES** |
| `CURRICULUM-MP_A5-a5-ubend-multipoint-R3-20260912T062921Z` | 1,873 | **0:0** (both arms B and O) | no (OOM 07:29) |
| `CURRICULUM-D8G-R2-a6-grid-triple` | 642 | **0:0** | no (done 06:52) |
| `CURRICULUM-D8G-R1-a6-grid-triple` | 642 | **0:0** | no (done 05:44) |
| `CURRICULUM-D6RF12-a2-wing-fd-nutilda-repair` | 408 | **0:0** | no (died 15:03) |
| `CURRICULUM-D8G-a6-grid-triple` | 189 | not in `docker ps -a` (reaped) | no |
| `CURRICULUM-MP_A5-a5-ubend-multipoint` | 39 | **0:0** | no (exit 1, 06:21) |
| `CURRICULUM-MP_A5-a5-ubend-multipoint-R2-20260912T062734Z` | 27 | **0:0** | no (exit 1, 06:28) |

**Not root, verified:** A3GC-L2R (`-u 1002:1000` in `_l2r_wrapper.sh`, outputs `ubuntu:ubuntu`);
A3GC-L1 / A3GC-L2 / A3GC-AR1 / A3GC-AR1C (outputs owned by uid 1002); **every** OpenFOAM
host run in `verification/runs/` (all outputs `ubuntu:ubuntu`).

Older root-owned trees from previous campaigns are present and larger
(`W5-regrade` 45,807 files, `CURRICULUM-D4-SHIPPED-a2-wing-cdmin` 7,921,
`CURRICULUM-D9SUCCESSOR-a5-ubend-opt` 4,208, and others) — the root-launch habit is
not new to today. Cleaning them is outside this census and is not proposed here.

## (b) RAM and daemon

- **Free RAM: 116 GiB free / 120 GiB available of 123 GiB total**; swap 15 GiB, 0 used.
  For contrast, `SOLVE_L2.gatedlaunch.log` recorded `available=0 GiB` repeatedly from
  13:41 to 17:25 on the old box, and `r2c_coarse_blended`'s watcher logged
  `MemAvailable=1.42GiB` at 10:11. The starvation that produced T5F_CUBE_f's 2.5 %
  CPU efficiency and SUBOFF L1's 1,900-second stalls is gone.
- **queue_runner runs as `ubuntu`** (pid 1713, `uid=1000`), started 17:36:52 by the boot
  path, not by an agent. Queue is empty.

## What this lane could not establish

- **A3GC-L1**: whether `a3gc_genmesh.sh` can be re-entered at the `plot3dToFoam` stage
  without redoing pyHyp. The file is md5-pinned and I read only its `docker run` line,
  not its stage logic. Marked UNKNOWN in the table rather than guessed.
- **D6R2**: whether `OptView.hst` is a usable pyOptSparse `hotStart` file for this
  problem. It exists and holds 13 evaluations; the run script does not reference it.
  Whether a hot-started rerun would be a legitimate continuation of the frozen
  pre-registration (`17eb2a260`) is a pre-registration question for dafoam-supervisor,
  not a disk fact.
- **Core-minute figures** are gross ClockTime x ranks and are inflated by contention;
  ExecutionTime is quoted alongside wherever the two diverge. None of them is a
  cost_basis; the rule-12 estimate-vs-actual calibration for these killed runs is owed
  by each owning team to `docs/COST_CALIBRATION.md` and is not attempted here.
