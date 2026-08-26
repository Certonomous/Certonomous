# VMFL017-R2 — LAUNCHER SMOKE TEST (PREREG_TEMPLATE Amendment 3, item 6)

**This is the artifact the frozen pre-registration named as its REGISTERED REMAINING GATE**
("the case inputs and the launcher MUST be built and MUST pass the Amendment-3 item-6
launcher smoke test on the box"), and which PRE-COMPUTE AMENDMENT 1 §D.3 held the launch on.
It is recorded here, beside the case, because a repository record never cites a scratch path
as evidence (CLAUDE.md rule 13) — the scratch tree below is where the run happened and is
temporary; the numbers are here.

**Amendment 3 item 6 exists because smoke tests were passing by running the solver in a
bypass environment, leaving the launcher as the one artifact nothing tested.** This smoke
therefore runs **`run_vmfl017_r2.sh` itself**, unmodified, with `VMFL_SMOKE=1`.

## What was run

| | |
|---|---|
| **utc (launcher start)** | **2026-08-26T17:08:16Z** |
| script | `cases/ansys_verification/VMFL017/R2/run_vmfl017_r2.sh`, invoked as `VMFL_SMOKE=1 bash run_vmfl017_r2.sh <scratch root>` |
| run root | a **scratch** root under the session scratchpad — **NOT** `verification/runs/ansys_verification/VMFL017/R2`, which did not exist and still holds no answer |
| level | **L1 only** (23040 cells), built from the committed templates by the launcher's own copy/`blockMeshDict.L1` selection path |
| `endTime` | shortened to **2e-8 s** **IN THE SCRATCH COPY ONLY** by the launcher's smoke hook; `forceCoeffs` intervals shortened to 2e-9 s in the same copy so the reader path is exercised. **The committed `case/system/controlDict` is untouched and still carries `endTime 0.05`.** |
| **rc** | **0** (launcher overall rc 0; `rhoCentralFoam` rc 0 under `timeout 18000`) |
| **rhoCentralFoam binary** | **`/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/rhoCentralFoam`** |
| OpenFOAM build | `_481094f-20260618 OPENFOAM=2606 version=2606`, sourced from `/usr/lib/openfoam/openfoam2606/etc/bashrc` (path verified present on this box) |
| host | `ip-172-31-43-247`, 16 cores, RANKS = 1 |
| wall | 2 s = 0.0333 core-min |

## Solver `Time` lines

* **first:** `Time = 1.17647e-09`
* **last:** `Time = 2e-08`
* **13** `Time` lines; **one `End` line**; last written time directory `2e-08`, containing
  `U`, and **newer than the `0/U` age-guard datum** (`field_at_endTime_newer_than_0_U=yes` in
  `RUN_RC.L1`).

The adaptive step ramped from the registered initial `deltaT = 1e-9` and settled at
`deltaT = 1.602e-9` s at a realised max Courant of **0.1837**, under the registered
`maxCo = 0.2`. `blockMesh` produced 23040 cells / 92480 faces with the `aerofoil`, `inflow`,
`outflow` and `frontAndBack` patches; `checkMesh` returned **Mesh OK** (max
non-orthogonality 51.1, max skewness 0.957, max aspect ratio 805.2 — a low-Re wall mesh).

## Every Amendment-3 artifact the smoke actually exercised

1. **Launch-time freeze verification** — passed on the run above (prereg blob
   `31ba194c32e6a5b7e280eb4db106e3bb9ef04722`, comparator blob
   `97c556f4a0d07f021480c75144d1b72a811fc391`), **and PLANTED (rule 3): the same launcher was
   re-run at 2026-08-26T17:13:18Z with `PREREGISTRATION.md` on disk carrying PRE-COMPUTE
   AMENDMENT 2 and therefore differing from its HEAD blob. It REFUSED with exit 2** —
   *"The file that would run is NOT the file that was frozen"* — **and built nothing: the
   scratch root was never created.** A guard not shown able to refuse is not a guard.
2. **Cap enforcement in the executable path** — `timeout_s = cap_core_min × 60 / RANKS`
   computed and applied: L1 `cap 300 core-min → timeout 18000s`, recorded in `RUN_RC.L1` and
   `LAUNCH_RECORD.txt` together with the realised `wall_s`, `core_min` and running total.
3. **No `set -u`** — none in the file, reason named in the header (v2606 `etc/bashrc`
   dereferences `WM_PROJECT_DIR` before assigning it; measured rc 127).
4. **Planted-zero control** — the launcher runs `grade_vmfl017_r2.py --selftest` before
   spending a core-minute and refuses unless it is green **and** the `plant seen` line is
   present; the comparator's `PLANT = 7.531e-3` and its `P_MIN = 0.05` probes both fired.
5. **Mesh birth certificate** — `cases/ansys_verification/VMFL017/mesh_birth/BIRTH_CERTIFICATE.md`
   confirmed at HEAD (`2a7e82c280c2bad9c191996a26013ca4decf4e6c`), **and all three
   `blockMeshDict.L1/L2/L3` confirmed byte-identical to the birth-certified attempt-1 family**.
6. **The launcher itself** — this document.

Additionally, the smoke drove the **registered-number assertion** (AMENDMENT 2 §B): the
launcher read `endTime 0.05`, `deltaT 1e-9`, `maxCo 0.2`, `maxDeltaT 1e-5`,
`writeControl adjustableRunTime` / `writeInterval 0.05`, `forceCoeffs1 executeInterval 1e-4`
out of `controlDict`, confirmed the comparator's `ENDTIME_PHYS = 0.05` is the **same number**,
and confirmed the sampling arithmetic: **500 forceCoeffs samples over the run, 100 in the
comparator's final 20 % window, against `PLATEAU_MIN_SAMPLES = 20`.** A second guard refuses
a smoke aimed at the graded run root; it was driven and refused (2026-08-26T17:13:18Z).

## The comparator's reader path was exercised, not assumed

`postProcessing/forceCoeffs1/0/coefficient.dat` was written with **10 data rows × 13
columns**, header `# Time Cd Cd(f) Cd(r) Cl …` — **column 1 = `Cd`, column 4 = `Cl`, exactly
the `COL_CD = 1` / `COL_CL = 4` the frozen comparator reads.** Last row of the smoke:
`Cd = 7.2889908109e-01`, `Cl = 2.7564764409e-01`.

> **THESE ARE NOT A RESULT AND ARE NOT COMPARABLE TO ANYTHING.** They are the coefficients
> after **2e-8 s** of physical time — 2.5e-6 of a chord flow-through, an impulsive start that
> has not begun to develop. They are recorded for one purpose only: to show that the reader
> the gate depends on **can see a non-zero number** off a real solver write.

## The cost measurement this smoke produced, and what it predicts

A companion scratch probe on the same L1 mesh (not the graded run root) ran **3319 steps in
110.2 s of `ExecutionTime`** — ≈ **27.7 steps per wall-second** at RANKS = 1 on a box measured
~50 % busy — with the adaptive step settled at **Δt = 1.806e-9 s** at max Courant **0.2000**,
reaching **5.977e-6 s of physical time in 120 wall-seconds**.

**Projected: L1 needs ≈ 2.8e7 steps ≈ 1.0e6 wall-seconds ≈ 16 700 core-min to reach the
registered `endTime` of 0.05 s — about 55× its registered 300 core-min cap, inside which it
reaches ≈ 1.8 % of `endTime`.**

This is registered in PRE-COMPUTE AMENDMENT 2 §E as a **measured pre-compute finding**. It is
the freeze's own PRINCIPAL RISK, quantified. **Nothing was changed to accommodate it**:
`endTime` is not reduced, the caps are not raised, `maxCo` is not loosened, the bands are
untouched. The registered consequence stands — L1 is expected to stop at its own cap with
rc 124, the launcher then stops without launching L2 or L3, and the case is `NOT A RESULT`.

## Memory, measured

On **L3** (368640 cells, the largest level): `blockMesh` peak RSS **442 MB** (22.9 s wall),
`rhoCentralFoam` peak RSS **1020 MB**. The queue entry's `memory_floor_gb = 2.0` is that
measurement plus headroom.

## What this smoke did NOT establish

* It did **not** run the physics to any settled state, and states **no** Cd or Cl result.
* It did **not** exercise L2 or L3 through the launcher (L1 only, by design of the smoke
  hook); their `blockMeshDict`s were verified by hash against the birth-certified family and
  L3 was meshed once for the memory measurement, but neither level was launched.
* It did **not** measure step rate on an idle box: the box was ~50 % busy throughout, so the
  wall-clock projection above carries contention that `CONTENTION.txt` records at the real
  launch (`COMPUTE_BUDGET_CHARTER` §6 — waste is reported, never absorbed into a ratio).
