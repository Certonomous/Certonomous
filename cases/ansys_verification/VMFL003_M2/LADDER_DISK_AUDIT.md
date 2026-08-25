# VMFL003_M2 Ladder Disk Audit — 2026-08-25T18:01Z

**Audit date:** 2026-08-25  
**Audit time reference:** 18:05 UTC  
**Task:** Read-only disk inventory of all run directories under `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/`  
**Auditor:** ansys-lane-haiku (Haiku 4.5)

---

## Executive Summary

- **Total run directories found:** 14
- **Completed runs:** 13
- **Incomplete/active runs:** 1
- **Expected but not found:** D_kOmegaSST (confirmed absent)

All 13 completed runs:
- Have `End` line in log
- Last time equals endTime from controlDict
- Have rc=0 status in RUN_RC.txt
- Pass age guard (all fields newer than 0/U)
- Have complete field set (U, p, k, epsilon, nut) at endTime
- ExecutionTime count equals endTime

One incomplete run in progress: C_RNGkEpsilon/L2_500x5 (PIDs 2324887/2324888, timeout 2087s, started 17:50:05Z).

No pressure-drop output files found in any run.

---

## Directory List Verification

**Derived from find:**
```
A_kEpsilon/D_500x3
A_kEpsilon/D_500x4
A_kEpsilon/D_500x6
A_kEpsilon/L1_250x5
A_kEpsilon/L2_500x5
A_kEpsilon/L3_1000x5
B_realizableKE/D_500x3
B_realizableKE/D_500x4
B_realizableKE/D_500x6
B_realizableKE/L1_250x5
B_realizableKE/L2_500x5
B_realizableKE/L3_1000x5
C_RNGkEpsilon/L1_250x5
C_RNGkEpsilon/L2_500x5
```

D_kOmegaSST: **Does not exist** (confirmed)

---

## Run-by-Run Audit Table

| Run | Log Path | Log Exists | End Line | Last Time | endTime | Match | RC | Age Guard | Completed |
|-----|----------|-----------|----------|-----------|---------|-------|----|-----------|----|
| A_kEpsilon/D_500x3 | log.simpleFoam | 18.2 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| A_kEpsilon/D_500x4 | log.simpleFoam | 18.1 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| A_kEpsilon/D_500x6 | log.simpleFoam | 18.2 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| A_kEpsilon/L1_250x5 | log.simpleFoam | 15.2 MB | yes | 15000 | 15000 | yes | 0 | PASS | YES |
| A_kEpsilon/L2_500x5 | log.simpleFoam | 18.2 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| A_kEpsilon/L3_1000x5 | log.simpleFoam | 22.2 MB | yes | 22000 | 22000 | yes | 0 | PASS | YES |
| B_realizableKE/D_500x3 | log.simpleFoam | 18.2 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| B_realizableKE/D_500x4 | log.simpleFoam | 18.1 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| B_realizableKE/D_500x6 | log.simpleFoam | 18.2 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| B_realizableKE/L1_250x5 | log.simpleFoam | 15.2 MB | yes | 15000 | 15000 | yes | 0 | PASS | YES |
| B_realizableKE/L2_500x5 | log.simpleFoam | 18.2 MB | yes | 18000 | 18000 | yes | 0 | PASS | YES |
| B_realizableKE/L3_1000x5 | log.simpleFoam | 22.2 MB | yes | 22000 | 22000 | yes | 0 | PASS | YES |
| C_RNGkEpsilon/L1_250x5 | log.simpleFoam | 15.2 MB | yes | 15000 | 15000 | yes | 0 | PASS | YES |
| C_RNGkEpsilon/L2_500x5 | log.simpleFoam | 11.9 MB | **no** | 11706 | 18000 | **no** | — | — | **NO (RUNNING)** |

---

## Detailed Run Reports

### Completed Runs (13)

All 13 completed runs follow the strict completion rule:
- rc=0 in RUN_RC.txt
- `End` line present in log
- Last `Time = ` equals endTime from controlDict
- ExecutionTime count equals endTime
- All required fields (U, p, k, epsilon, nut) present at endTime
- Age guard passes: all field files newer than 0/U

#### A_kEpsilon/D_500x3
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/D_500x3/log.simpleFoam` (18,154,506 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787677490 (2026-08-25 17:04:50.046807897 +0000)
- **Fields mtime at 18000:** 1787677644 (2026-08-25 17:07:24.5206 +0000)
- **Age guard:** PASS (fields 154 s newer than 0/U)
- **Newest file:** 2026-08-25 17:07:24.588646959 (RUN_RC.txt)
- **Status:** COMPLETED

#### A_kEpsilon/D_500x4
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/D_500x4/log.simpleFoam` (18,116,287 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787677644 (2026-08-25 17:07:24.819648223 +0000)
- **Fields mtime at 18000:** 1787677776 (2026-08-25 17:09:36.8603 +0000)
- **Age guard:** PASS (fields 132 s newer than 0/U)
- **Newest file:** 2026-08-25 17:09:36.926359170 (RUN_RC.txt)
- **Status:** COMPLETED

#### A_kEpsilon/D_500x6
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/D_500x6/log.simpleFoam` (18,162,327 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787677777 (2026-08-25 17:09:37.169360412 +0000)
- **Fields mtime at 18000:** 1787678008 (2026-08-25 17:13:28.6235 +0000)
- **Age guard:** PASS (fields 231 s newer than 0/U)
- **Newest file:** 2026-08-25 17:13:28.700562376 (RUN_RC.txt)
- **Status:** COMPLETED

#### A_kEpsilon/L1_250x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/L1_250x5/log.simpleFoam` (15,166,597 bytes)
- **Last time:** 15000 (matches endTime)
- **EndTime:** 15000
- **Fields at 15000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 15000
- **0/U mtime:** 1787676202 (2026-08-25 16:43:22.067138129 +0000)
- **Fields mtime at 15000:** 1787676477 (2026-08-25 16:47:57.9646 +0000)
- **Age guard:** PASS (fields 275 s newer than 0/U)
- **Newest file:** 2026-08-25 16:47:58.040679377 (RUN_RC.txt)
- **Status:** COMPLETED

#### A_kEpsilon/L2_500x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/L2_500x5/log.simpleFoam` (18,185,285 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787676478 (2026-08-25 16:47:58.298680795 +0000)
- **Fields mtime at 18000:** 1787676813 (2026-08-25 16:53:33.3324 +0000)
- **Age guard:** PASS (fields 335 s newer than 0/U)
- **Newest file:** 2026-08-25 16:53:33.417445507 (RUN_RC.txt)
- **Status:** COMPLETED

#### A_kEpsilon/L3_1000x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/A_kEpsilon/L3_1000x5/log.simpleFoam` (22,214,900 bytes)
- **Last time:** 22000 (matches endTime)
- **EndTime:** 22000
- **Fields at 22000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 22000
- **0/U mtime:** 1787676813 (2026-08-25 16:53:33.763447127 +0000)
- **Fields mtime at 22000:** 1787677489 (2026-08-25 17:04:49.7388 +0000)
- **Age guard:** PASS (fields 676 s newer than 0/U)
- **Newest file:** 2026-08-25 17:04:49.820806756 (RUN_RC.txt)
- **Status:** COMPLETED

#### B_realizableKE/D_500x3
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/D_500x3/log.simpleFoam` (18,154,101 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787679301 (2026-08-25 17:35:01.573697494 +0000)
- **Fields mtime at 18000:** 1787679455 (2026-08-25 17:37:35.9485 +0000)
- **Age guard:** PASS (fields 154 s newer than 0/U)
- **Newest file:** 2026-08-25 17:37:36.016503866 (RUN_RC.txt)
- **Status:** COMPLETED

#### B_realizableKE/D_500x4
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/D_500x4/log.simpleFoam` (18,138,319 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787679456 (2026-08-25 17:37:36.238504951 +0000)
- **Fields mtime at 18000:** 1787679610 (2026-08-25 17:40:10.9422 +0000)
- **Age guard:** PASS (fields 154 s newer than 0/U)
- **Newest file:** 2026-08-25 17:40:11.011270373 (RUN_RC.txt)
- **Status:** COMPLETED

#### B_realizableKE/D_500x6
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/D_500x6/log.simpleFoam` (18,165,341 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787679611 (2026-08-25 17:40:11.269271444 +0000)
- **Fields mtime at 18000:** 1787679888 (2026-08-25 17:44:48.5056 +0000)
- **Age guard:** PASS (fields 277 s newer than 0/U)
- **Newest file:** 2026-08-25 17:44:48.583626947 (RUN_RC.txt)
- **Status:** COMPLETED

#### B_realizableKE/L1_250x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/L1_250x5/log.simpleFoam` (15,167,453 bytes)
- **Last time:** 15000 (matches endTime)
- **EndTime:** 15000
- **Fields at 15000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 15000
- **0/U mtime:** 1787678011 (2026-08-25 17:13:31.037574775 +0000)
- **Fields mtime at 15000:** 1787678309 (2026-08-25 17:18:29.9581 +0000)
- **Age guard:** PASS (fields 298 s newer than 0/U)
- **Newest file:** 2026-08-25 17:18:30.028191496 (RUN_RC.txt)
- **Status:** COMPLETED

#### B_realizableKE/L2_500x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/L2_500x5/log.simpleFoam` (18,167,591 bytes)
- **Last time:** 18000 (matches endTime)
- **EndTime:** 18000
- **Fields at 18000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 18000
- **0/U mtime:** 1787678310 (2026-08-25 17:18:30.297192990 +0000)
- **Fields mtime at 18000:** 1787678634 (2026-08-25 17:23:54.3156 +0000)
- **Age guard:** PASS (fields 324 s newer than 0/U)
- **Newest file:** 2026-08-25 17:23:54.392992231 (RUN_RC.txt)
- **Status:** COMPLETED

#### B_realizableKE/L3_1000x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/B_realizableKE/L3_1000x5/log.simpleFoam` (22,213,870 bytes)
- **Last time:** 22000 (matches endTime)
- **EndTime:** 22000
- **Fields at 22000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 22000
- **0/U mtime:** 1787678634 (2026-08-25 17:23:54.712994022 +0000)
- **Fields mtime at 22000:** 1787679301 (2026-08-25 17:35:01.2526 +0000)
- **Age guard:** PASS (fields 667 s newer than 0/U)
- **Newest file:** 2026-08-25 17:35:01.335696169 (RUN_RC.txt)
- **Status:** COMPLETED

#### C_RNGkEpsilon/L1_250x5
- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L1_250x5/log.simpleFoam` (15,167,463 bytes)
- **Last time:** 15000 (matches endTime)
- **EndTime:** 15000
- **Fields at 15000:** U, epsilon, k, nut, p
- **ExecutionTime count:** 15000
- **0/U mtime:** 1787679890 (2026-08-25 17:44:50.940638329 +0000)
- **Fields mtime at 15000:** 1787680204 (2026-08-25 17:50:04.9651 +0000)
- **Age guard:** PASS (fields 314 s newer than 0/U)
- **Newest file:** 2026-08-25 17:50:05.040205253 (RUN_RC.txt)
- **Status:** COMPLETED

---

### Incomplete/Active Run (1)

#### C_RNGkEpsilon/L2_500x5 — INCOMPLETE, RUNNING

- **Log:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L2_500x5/log.simpleFoam` (11,828,859 bytes)
- **End line:** **NOT PRESENT**
- **Last time in log:** 11706 (endTime: 18000, **MISMATCH**)
- **Last time directory on disk:** 11600 (no 11706 directory exists yet)
- **ExecutionTime count:** 11706
- **ProcessState:** 
  - PID 2324887: timeout 2087 simpleFoam (started 2026-08-25 17:50:05Z)
  - PID 2324888: simpleFoam child
  - Running for: 15 minutes 30 seconds (at audit time 18:05Z)
  - Wall timeout remaining: 2087 s - 930 s ≈ 1157 s ≈ 19 minutes
- **Newest file:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L2_500x5/log.simpleFoam` (2026-08-25 18:04:22.045809095 +0000)
  - Log still being written (mtime 18:04:22Z, 40 seconds before audit completion)
- **Expected completion time:** ~18:25 UTC (wall time remaining)
- **Status:** **INCOMPLETE — ACTIVELY RUNNING, DO NOT TOUCH**

---

## Pressure-Drop Output Artifacts

**Search:** for `postProcessing/forceCoeffs/*/forceCoeffs.dat` and `postProcessing/pressureDrop/*/pressureDrop.dat`

**Result:** No pressure-drop output files found in any run directory.

---

## Summary by Cohort

### A_kEpsilon (6/6 completed)
- D_500x3: COMPLETED
- D_500x4: COMPLETED
- D_500x6: COMPLETED
- L1_250x5: COMPLETED
- L2_500x5: COMPLETED
- L3_1000x5: COMPLETED

### B_realizableKE (6/6 completed)
- D_500x3: COMPLETED
- D_500x4: COMPLETED
- D_500x6: COMPLETED
- L1_250x5: COMPLETED
- L2_500x5: COMPLETED
- L3_1000x5: COMPLETED

### C_RNGkEpsilon (1/2 completed)
- L1_250x5: COMPLETED
- L2_500x5: **INCOMPLETE — RUNNING**

### D_kOmegaSST
- Not found (as expected)

---

## Audit Completion

- **Audit performed:** 2026-08-25 18:04:22 UTC
- **Audit duration:** Read-only disk inspection, no modifications
- **Live processes confirmed:** PIDs 2324887/2324888 running under timeout 2087 s
- **No files written, no files touched during audit**
- **Disk state verified:** 14 run directories, 13 complete, 1 running

