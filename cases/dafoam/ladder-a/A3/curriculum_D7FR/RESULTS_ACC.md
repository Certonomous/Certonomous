# D7FR — arm `ACC` graded: **`ACC-1` = `PASS`**, the D7-DEF-4 repair is FROZEN, and the FD chain is running

**Written 2026-08-26 by a dafoam lab-lane for dafoam-supervisor.** Freeze `b424b44e`; Amendment 1 (`H5`) `9feb0815`. Grading path verified: `d7fr_accept_compare.py`, `d7fr_run_arm.sh`, `d7fr_mem_gate.py`, `d7fr_grade.py` on disk and in the run root hash-identical to the `9feb0815` blobs (checked before launch). Permission for the detached launch: Sanaa's words boarded at `bc0e687e`. Host identity note: the box rebooted 15:19Z, kernel `7.0.0-1011-aws` (was 1010). The toolchain identity is the image digest (§8 of the pre-registration) and is unchanged.

## 1. `H5` re-run on the rebooted box — CLEAR

Pre-check window, same gate as registered (`d7fr_mem_gate.py --floor 16.0 --span 63.0 --arm-wall 900`), 45 samples over 63.0 s starting 16:00:25Z: **min 27.66, median 27.89, max 28.21 GiB, `n_below_floor` 0, slope −0.4505 GiB/min, projected at arm end 20.993 GiB → CLEAR, exit 0.** Series: run root `ACC_h5_precheck_20260826T160025Z.txt` (+ `.verdict`). The launcher's own `H5` then ran again inside the arm (`ACC_h5_memwindow.txt`, `D7FR_H5_PASS` in `ACC_chain_launcher.out`).

The 04:5xZ refusal, for the record: `R4_TREND`, min 17.34 above the floor, slope −0.1701 GiB/min projecting 14.978 GiB at arm end. The gate was working on a trend; the floor was not trimmed.

**Aggregate rule (LAB_STATE dafoam 8.2, as amended):** at ACC launch, live caps 8.00 GiB (`d12y_S2b`, cpu 12) + host RSS 2.94 + this arm 12 = **22.94 < 30.6 GiB, HOLDS** (`chain_launch.out`). The chain driver re-checks this before every arm.

## 2. Arm `ACC` — the kernel's record

| field | value | artifact |
|---|---|---|
| container | `d7fr_ACC_20260826T160416Z_56097`, SHIPPED, digest `9d45679d…` | `ledger.txt` |
| rc | **0** — `docker inspect` `[false 0 false]` read by the chain watcher; launcher marker `rc=0`; **agree** | `STATUS.ACC`, `ACC_20260826T160416Z_56097.log.ok.…` |
| wall / core-min | 31 s × 4 = **2.067**, cap 60.0, no crossing, ceiling 240 not reached | `ledger.txt` |
| memory | pre 28.05, min during 26.263, post 28.06 GiB; OOMKilled false | `ledger.txt` |
| placement | cpuset 2,3,4,6; `delivered_cores_mean` **3.7267** of 4, `max_nr_throttled` 45; sibling `d12y_S2b` on cpu 12 | `ledger.txt` |
| `End` lines in the arm log | 2 | `ACC_20260826T160416Z_56097.log` |

## 3. `ACC-1` — `PASS`

`CD_measured = 0.02303298929962691` vs arm `O`'s IPOPT objective `CD_target = 2.3048932443550496e-02`: **`rel_CD = 6.917085623220234e-04` ≤ 1e-3 → `PASS`.** Planted-zero control `G-ACC-PLANT`: plant 1.234e-3, planted `rel_CD` 0.05285 == expected, residual 0.0, blind reader REFUSED → control PASS. Counts verified `{patchV 2, shape 120, twist 5}`, units PHYSICAL, scalers `{0.1, 10.0, 0.1}` applied.

Reported, gating nothing (as registered): `ACC-2` band 1e-6 — not in band; `ACC_CL` `CL 0.287731` vs target `0.287613`, `rel_CL 4.11e-4`, in band.

**Prediction `C4` (lands inside 1e-3) — CONFIRMED.** It landed at 6.9e-4, three times D4's 2.34e-4 — inside the band, and the margin is stated.

Artifact: `ACC/d7fr_accept_verdict.json` (`"verdict": "PASS"`), which is the `LIMIT 1` precondition the launcher reads at `d7fr_run_arm.sh:391-392`. The chain read it and fired `F-S`.

## 4. Cost — estimate versus actual (rule 12)

Predicted **25.0** core-min; actual **2.067** (gross = cleaned, no row over 3600 s); **ratio 0.083**; **$0.0018 DERIVED** at $0.0513/core-h, `cost_basis` REPORTED-BY-OWNER. Attribution: **misprediction** — §7 priced one primal at 20.27 core-min from arm `O`'s 932.5/46 evaluations, and §7 itself says that figure "necessarily OVERSTATES a primal" because it carries adjoint solves; the measured primal was 18.6 s of the 31 s wall. Contention present, not limiting (3.73 of 4 cores delivered). No waste. Ledger row: `docs/COST_CALIBRATION.md`.

## 5. The chain — what is running and what is `PENDING`

`d7fr_chain.sh` (run root; `setsid nohup`, sid = pid) fired `F-S` at 16:05:53Z as `d7fr_F_S_20260826T160553Z_80216` (SHIPPED) after the launcher's own `H5`. ETA at prediction 485 core-min ≈ 121 min wall → ~18:07Z; cap 750 ≈ 19:13Z. `F-P` (PATCHED, `dafoam-idwarp-rot:v1`, digest `2927768a…` present in `docker images`) fires after `STATUS.F-S` reads `rc=0`, ETA ~20:10Z. The chain stops at the first non-zero rc and marks the rest `NOT_FIRED`.

**Grading command for whoever is alive when `STATUS.F-P` lands** (verify blobs first):

```
for f in d7fr_grade.py d7fr_run_arm.sh PREREGISTRATION.md; do test "$(git rev-parse 9feb0815:cases/dafoam/ladder-a/A3/curriculum_D7FR/$f)" = "$(git hash-object cases/dafoam/ladder-a/A3/curriculum_D7FR/$f)" || echo FREEZE-MISMATCH $f; done
python3 cases/dafoam/ladder-a/A3/curriculum_D7FR/d7fr_grade.py --base /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd --work /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd --out /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/d7fr_grade.json --cl-target 0.2876130251655752 --fd-shipped /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/F-S/d7_fd_endpoint.json --fd-patched /home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/F-P/d7_fd_endpoint.json
```

`F-S` and `F-P` rows: **`PENDING`: `STATUS.F-S`, `STATUS.F-P`** in the run root.
