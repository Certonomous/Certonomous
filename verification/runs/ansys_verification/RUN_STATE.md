# ansys_verification RUN_STATE Snapshot

**Generated:** Tue Aug 25 18:21:19 UTC 2026
**Git commit:** 397ad7f5bd76b9b481c0e57a99bc388c9f8d1606

**Note:** This snapshot is point-in-time and will become stale as new runs complete or in-progress runs continue.

**REFUTATION NOTE:** Previous snapshot at RUN_STATE_REFUTED_20260825.md missed 14 of 15 completed VMFL003_M2 runs due to insufficient walk depth.

## State Summary

| State | Count |
|-------|-------|
| COMPLETE | 20 |
| RUNNING | 1 |
| INCOMPLETE | 24 |
| UNDETERMINED | 0 |

## Process Table

Solver processes on system (ps -eo pid,ppid,pcpu,rss,etime,lstart,args):

| PID | Team | CWD | Args |
|-----|------|-----|------|
| 1439 | other | /home/ubuntu/Certonomous/sdk | Aug 21 15:21:55 2026 python3 -u -m chief_engineer.server... |
| 1446 | other | /home/ubuntu/Certonomous | Aug 21 15:21:55 2026 python3 -u -m http.server 8080 --direct... |
| 2092467 | other | /home/ubuntu/Certonomous | Aug 25 14:57:37 2026 -bash... |
| 2095894 | other | /home/ubuntu/Certonomous | Aug 25 15:20:35 2026 claude --resume 64b13819-ff95-4d4d-a50f... |
| 2199763 | other | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_10k_x | Aug 25 16:36:42 2026 /bin/bash /home/ubuntu/Certonomous/veri... |
| 2201241 | other | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_100k_x | Aug 25 16:36:42 2026 /bin/bash /home/ubuntu/Certonomous/veri... |
| 2202714 | other | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_300k_x | Aug 25 16:36:43 2026 /bin/bash /home/ubuntu/Certonomous/veri... |
| 2203926 | heat-transfer | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_10k_x | Aug 25 16:36:46 2026 timeout 66000 buoyantBoussinesqSimpleFo... |
| 2203927 | heat-transfer | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_10k_x | Aug 25 16:36:46 2026 buoyantBoussinesqSimpleFoam... |
| 2203943 | heat-transfer | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_100k_x | Aug 25 16:36:46 2026 timeout 78000 buoyantBoussinesqSimpleFo... |
| 2203944 | heat-transfer | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_100k_x | Aug 25 16:36:46 2026 buoyantBoussinesqSimpleFoam... |
| 2203946 | heat-transfer | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_300k_x | Aug 25 16:36:47 2026 timeout 165000 buoyantBoussinesqSimpleF... |
| 2203947 | heat-transfer | /home/ubuntu/Certonomous/verification/runs/T-family/T1_runs/R_300k_x | Aug 25 16:36:47 2026 buoyantBoussinesqSimpleFoam... |
| 2218904 | other | /home/ubuntu/Certonomous | Aug 25 16:43:19 2026 bash cases/ansys_verification/VMFL003_M... |
| 2261317 | other | /home/ubuntu | Aug 25 17:03:42 2026 /usr/bin/dbus-daemon --session --addres... |
| 2357892 | other | /home/ubuntu/Certonomous | Aug 25 18:11:00 2026 bash cases/ansys_verification/VMFL003_M... |
| 2359354 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:12:37 2026 bash d4_run_arm.sh O dafoam-idwarp-rot:... |
| 2359412 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:12:37 2026 bash d4_run_arm.sh O dafoam-idwarp-rot:... |
| 2359415 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:12:37 2026 timeout 9300 sudo -n docker run --name ... |
| 2359888 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:12:40 2026 bash d4_mem_sampler.sh d4_O_ /home/ubun... |
| 2360987 | ansys-verification | /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L3_1000x5 | Aug 25 18:13:43 2026 bash cases/ansys_verification/VMFL003_M... |
| 2360988 | ansys-verification | /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L3_1000x5 | Aug 25 18:13:43 2026 timeout 670 simpleFoam... |
| 2360989 | ansys-verification | /home/ubuntu/Certonomous/verification/runs/ansys_verification/VMFL003_M2/C_RNGkEpsilon/L3_1000x5 | Aug 25 18:13:43 2026 simpleFoam... |
| 2363036 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:14:59 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2367088 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:16:36 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2370012 | other | /home/ubuntu/Certonomous | Aug 25 18:18:33 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2370463 | dafoam | /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9 | Aug 25 18:18:37 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2370464 | other | /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9 | Aug 25 18:18:37 2026 bash ./d9_stage_and_run.sh... |
| 2372153 | other | /home/ubuntu/Certonomous | Aug 25 18:19:20 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2372645 | other | /home/ubuntu/Certonomous | Aug 25 18:19:26 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2373145 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:19:42 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2374074 | other | /home/ubuntu/Certonomous | Aug 25 18:19:48 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2374512 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:20:00 2026 sleep 60... |
| 2375715 | other | /home/ubuntu/Certonomous | Aug 25 18:20:14 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2376204 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt | Aug 25 18:20:22 2026 bash ./d8_run_arm.sh fd fdsub8 4500... |
| 2376224 | dafoam | /home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt | Aug 25 18:20:22 2026 timeout 4500 sudo -n docker run --name ... |
| 2376225 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt | Aug 25 18:20:22 2026 bash ./d8_run_arm.sh fd fdsub8 4500... |
| 2376802 | other | /home/ubuntu/Certonomous | Aug 25 18:20:30 2026 sleep 30... |
| 2376908 | dafoam | /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A5/curriculum_D9 | Aug 25 18:20:32 2026 timeout 1806 sudo -n docker run --name ... |
| 2377458 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:20:40 2026 sleep 15... |
| 2377460 | other | /home/ubuntu/Certonomous | Aug 25 18:20:41 2026 sleep 15... |
| 2377760 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:20:42 2026 sleep 15... |
| 2377814 | other | /home/ubuntu/Certonomous | Aug 25 18:20:44 2026 sleep 15... |
| 2377830 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:20:47 2026 sleep 10... |
| 2377831 | other | /home/ubuntu/Certonomous | Aug 25 18:20:48 2026 sleep 15... |
| 2377832 | other | /home/ubuntu/Certonomous | Aug 25 18:20:49 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2377854 | other | /home/ubuntu/Certonomous | Aug 25 18:20:49 2026 sleep 20... |
| 2377856 | other | /home/ubuntu/Certonomous | Aug 25 18:20:50 2026 sleep 15... |
| 2377916 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin | Aug 25 18:20:53 2026 sleep 10... |
| 2377917 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt | Aug 25 18:20:53 2026 bash ./d8_run_arm.sh fd fdsub8 4500... |
| 2377919 | other | /home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt | Aug 25 18:20:53 2026 head -1... |
| 2377932 | other | /home/ubuntu/Certonomous | Aug 25 18:20:53 2026 sleep 20... |
| 2377933 | heat-transfer | /home/ubuntu/Certonomous | Aug 25 18:20:53 2026 /bin/bash -c source /home/ubuntu/.claud... |
| 2377954 | other | /home/ubuntu/Certonomous | Aug 25 18:20:53 2026 python3 /tmp/claude-1000/-home-ubuntu-C... |
| 2377956 | unknown | N/A | Aug 25 18:20:53 2026 ps -eo pid,ppid,pcpu,rss,etime,lstart,a... |

Total process table entries: 55

## Run Details by State

### COMPLETE (20)

#### VMFL003/D_500x3

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 8000.0
- **Last Time (from log):** 8000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 8000
- **Time directories:** 41
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787625088, all_fields_newer
- **wall_s:** 67
- **ranks:** 1
- **core_min:** 1.1166666666666667
- **Newest file mtime:** 1787625156.7330952 (2026-08-25 02:32:36)

#### VMFL003/D_500x4

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 8000.0
- **Last Time (from log):** 8000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 8000
- **Time directories:** 41
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787625156, all_fields_newer
- **wall_s:** 56
- **ranks:** 1
- **core_min:** 0.9333333333333333
- **Newest file mtime:** 1787625213.8883543 (2026-08-25 02:33:33)

#### VMFL003/D_500x6

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 8000.0
- **Last Time (from log):** 8000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 8000
- **Time directories:** 41
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787625214, all_fields_newer
- **wall_s:** 98
- **ranks:** 1
- **core_min:** 1.6333333333333333
- **Newest file mtime:** 1787625313.2808044 (2026-08-25 02:35:13)

#### VMFL003/L1_250x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 6000.0
- **Last Time (from log):** 6000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 6000
- **Time directories:** 31
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787624496, all_fields_newer
- **wall_s:** 107
- **ranks:** 1
- **core_min:** 1.7833333333333334
- **Newest file mtime:** 1787624604.6315758 (2026-08-25 02:23:24)

#### VMFL003/L2_500x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 8000.0
- **Last Time (from log):** 8000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 8000
- **Time directories:** 41
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787624604, all_fields_newer
- **wall_s:** 139
- **ranks:** 1
- **core_min:** 2.316666666666667
- **Newest file mtime:** 1787624744.1432319 (2026-08-25 02:25:44)

#### VMFL003/L3_1000x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 12000.0
- **Last Time (from log):** 12000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 12000
- **Time directories:** 61
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787624744, all_fields_newer
- **wall_s:** 343
- **ranks:** 1
- **core_min:** 5.716666666666667
- **Newest file mtime:** 1787625088.392785 (2026-08-25 02:31:28)

#### VMFL003_M2/A_kEpsilon/D_500x3

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787677490, all_fields_newer
- **wall_s:** 153
- **ranks:** 1
- **core_min:** 2.55
- **Newest file mtime:** 1787677644.588647 (2026-08-25 17:07:24)

#### VMFL003_M2/A_kEpsilon/D_500x4

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787677644, all_fields_newer
- **wall_s:** 131
- **ranks:** 1
- **core_min:** 2.183333333333333
- **Newest file mtime:** 1787677776.9263592 (2026-08-25 17:09:36)

#### VMFL003_M2/A_kEpsilon/D_500x6

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787677777, all_fields_newer
- **wall_s:** 230
- **ranks:** 1
- **core_min:** 3.8333333333333335
- **Newest file mtime:** 1787678008.7005625 (2026-08-25 17:13:28)

#### VMFL003_M2/A_kEpsilon/L1_250x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 15000.0
- **Last Time (from log):** 15000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 15000
- **Time directories:** 76
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787676202, all_fields_newer
- **wall_s:** 274
- **ranks:** 1
- **core_min:** 4.566666666666666
- **Newest file mtime:** 1787676478.0406795 (2026-08-25 16:47:58)

#### VMFL003_M2/A_kEpsilon/L2_500x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787676478, all_fields_newer
- **wall_s:** 334
- **ranks:** 1
- **core_min:** 5.566666666666666
- **Newest file mtime:** 1787676813.4174454 (2026-08-25 16:53:33)

#### VMFL003_M2/A_kEpsilon/L3_1000x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 22000.0
- **Last Time (from log):** 22000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 22000
- **Time directories:** 111
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787676813, all_fields_newer
- **wall_s:** 675
- **ranks:** 1
- **core_min:** 11.25
- **Newest file mtime:** 1787677489.8208067 (2026-08-25 17:04:49)

#### VMFL003_M2/B_realizableKE/D_500x3

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787679301, all_fields_newer
- **wall_s:** 153
- **ranks:** 1
- **core_min:** 2.55
- **Newest file mtime:** 1787679456.0165038 (2026-08-25 17:37:36)

#### VMFL003_M2/B_realizableKE/D_500x4

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787679456, all_fields_newer
- **wall_s:** 153
- **ranks:** 1
- **core_min:** 2.55
- **Newest file mtime:** 1787679611.0112703 (2026-08-25 17:40:11)

#### VMFL003_M2/B_realizableKE/D_500x6

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787679611, all_fields_newer
- **wall_s:** 276
- **ranks:** 1
- **core_min:** 4.6
- **Newest file mtime:** 1787679888.583627 (2026-08-25 17:44:48)

#### VMFL003_M2/B_realizableKE/L1_250x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 15000.0
- **Last Time (from log):** 15000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 15000
- **Time directories:** 76
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787678011, all_fields_newer
- **wall_s:** 297
- **ranks:** 1
- **core_min:** 4.95
- **Newest file mtime:** 1787678310.0281916 (2026-08-25 17:18:30)

#### VMFL003_M2/B_realizableKE/L2_500x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787678310, all_fields_newer
- **wall_s:** 323
- **ranks:** 1
- **core_min:** 5.383333333333334
- **Newest file mtime:** 1787678634.3929923 (2026-08-25 17:23:54)

#### VMFL003_M2/B_realizableKE/L3_1000x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 22000.0
- **Last Time (from log):** 22000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 22000
- **Time directories:** 111
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787678634, all_fields_newer
- **wall_s:** 666
- **ranks:** 1
- **core_min:** 11.1
- **Newest file mtime:** 1787679301.3356962 (2026-08-25 17:35:01)

#### VMFL003_M2/C_RNGkEpsilon/L1_250x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 15000.0
- **Last Time (from log):** 15000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 15000
- **Time directories:** 76
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787679890, all_fields_newer
- **wall_s:** 313
- **ranks:** 1
- **core_min:** 5.216666666666667
- **Newest file mtime:** 1787680205.0402052 (2026-08-25 17:50:05)

#### VMFL003_M2/C_RNGkEpsilon/L2_500x5

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 18000.0
- **Last Time (from log):** 18000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 18000
- **Time directories:** 91
- **Required fields present:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680205, all_fields_newer
- **wall_s:** 1416
- **ranks:** 1
- **core_min:** 23.6
- **Newest file mtime:** 1787681622.268407 (2026-08-25 18:13:42)

### RUNNING (1)

#### VMFL003_M2/C_RNGkEpsilon/L3_1000x5

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 22000.0
- **Last Time (from log):** 15171.0
- **End line present:** False
- **ExecutionTime count (Time = lines):** 15171
- **Time directories:** 76
- **Required fields present:** []
- **Required fields missing:** ['U', 'p', 'k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787681622, all_fields_newer
- **Newest file mtime:** 1787682056.821666 (2026-08-25 18:20:56)

### INCOMPLETE (24)

#### VMFL001/L1_16x64

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 3000.0
- **Last Time (from log):** 3000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787593523, all_fields_newer
- **wall_s:** 2
- **ranks:** 1
- **core_min:** 0.0333
- **Newest file mtime:** 1787593525.6197186 (2026-08-24 17:45:25)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL001/L2_32x128

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 3000.0
- **Last Time (from log):** 3000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787593525, all_fields_newer
- **wall_s:** 13
- **ranks:** 1
- **core_min:** 0.2167
- **Newest file mtime:** 1787593538.1567905 (2026-08-24 17:45:38)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL001/L3_64x256

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 3000.0
- **Last Time (from log):** 3000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787593538, all_fields_newer
- **wall_s:** 104
- **ranks:** 1
- **core_min:** 1.7333
- **Newest file mtime:** 1787593642.5733302 (2026-08-24 17:47:22)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL001/R2/L1_16x64

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 3000.0
- **Last Time (from log):** 3000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787595044, all_fields_newer
- **wall_s:** 2
- **ranks:** 1
- **core_min:** 0.0333
- **Newest file mtime:** 1787595047.008456 (2026-08-24 18:10:47)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL001/R2/L2_32x128

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 3000.0
- **Last Time (from log):** 3000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787595047, all_fields_newer
- **wall_s:** 12
- **ranks:** 1
- **core_min:** 0.2000
- **Newest file mtime:** 1787595059.5475254 (2026-08-24 18:10:59)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL001/R2/L3_64x256

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 6000.0
- **Last Time (from log):** 6000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 6000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787595059, all_fields_newer
- **wall_s:** 183
- **ranks:** 1
- **core_min:** 3.0500
- **Newest file mtime:** 1787595242.290561 (2026-08-24 18:14:02)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL005/L1_100x10

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 2000.0
- **Last Time (from log):** 2000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 2000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787597121, all_fields_newer
- **wall_s:** 11
- **ranks:** 1
- **core_min:** 0.1833
- **Newest file mtime:** 1787597132.0669363 (2026-08-24 18:45:32)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL005/L2_200x20

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 3000.0
- **Last Time (from log):** 3000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787597132, all_fields_newer
- **wall_s:** 29
- **ranks:** 1
- **core_min:** 0.4833
- **Newest file mtime:** 1787597161.4771016 (2026-08-24 18:46:01)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL005/L3_400x40

- **Log:** log.simpleFoam
- **RC:** 0
- **endTime (from controlDict):** 6000.0
- **Last Time (from log):** 6000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 6000
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787597161, all_fields_newer
- **wall_s:** 200
- **ranks:** 1
- **core_min:** 3.3333
- **Newest file mtime:** 1787597361.1461935 (2026-08-24 18:49:21)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007/L1_25x25

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787677064, all_fields_newer
- **Newest file mtime:** 1787677298.4068635 (2026-08-25 17:01:38)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007/L2_50x50

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 9065.0
- **End line present:** False
- **ExecutionTime count (Time = lines):** 9065
- **Time directories:** 2
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787677298, all_fields_newer
- **Newest file mtime:** 1787677442.7005708 (2026-08-25 17:04:02)
- **Reasons for non-COMPLETE state:** End_line: ABSENT; missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007_R2/A1_GAMG_GaussSeidel

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680181, all_fields_newer
- **Newest file mtime:** 1787680409.3752027 (2026-08-25 17:53:29)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007_R2/A2_GAMG_DICGaussSeidel

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680409, all_fields_newer
- **Newest file mtime:** 1787680436.2503338 (2026-08-25 17:53:56)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007_R2/A3_PCG_DIC

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680436, all_fields_newer
- **Newest file mtime:** 1787680456.2474303 (2026-08-25 17:54:16)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007_R2/A4_PCG_GAMGprecon

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680456, all_fields_newer
- **Newest file mtime:** 1787680588.704073 (2026-08-25 17:56:28)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007_R2/A5_PBiCGStab_DIC

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680588, all_fields_newer
- **Newest file mtime:** 1787680609.5431776 (2026-08-25 17:56:49)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL007_R2/A6_smoothSolver_symGaussSeidel

- **Log:** log.simpleFoam
- **RC:** None
- **endTime (from controlDict):** 10000.0
- **Last Time (from log):** 10000.0
- **End line present:** True
- **ExecutionTime count (Time = lines):** 10000
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787680609, all_fields_newer
- **Newest file mtime:** 1787680740.4198303 (2026-08-25 17:59:00)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL045/L1_90x76

- **Log:** log.rhoCentralFoam
- **RC:** 1
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 1.2e-08
- **End line present:** False
- **ExecutionTime count (Time = lines):** 1
- **Time directories:** 1
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** FAIL - zero_epoch=1787621805, older_files=3
- **wall_s:** 0
- **ranks:** 1
- **core_min:** 0.0000
- **Newest file mtime:** 1787621805.3418708 (2026-08-25 01:36:45)
- **Reasons for non-COMPLETE state:** End_line: ABSENT; missing_fields: ['k', 'epsilon', 'nut']; age_guard: FAILED; rc: 1

#### VMFL045/R2/L1_90x76

- **Log:** log.rhoCentralFoam
- **RC:** 0
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 0.0069995039
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3127
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787624848, all_fields_newer
- **wall_s:** 22
- **ranks:** 1
- **core_min:** 0.3667
- **Newest file mtime:** 1787624870.0578015 (2026-08-25 02:27:50)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL045/R2/L2_180x152

- **Log:** log.rhoCentralFoam
- **RC:** 0
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 0.0069997326
- **End line present:** True
- **ExecutionTime count (Time = lines):** 6305
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787624870, all_fields_newer
- **wall_s:** 160
- **ranks:** 1
- **core_min:** 2.6667
- **Newest file mtime:** 1787625030.0985215 (2026-08-25 02:30:30)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL045/R2/L3_360x304

- **Log:** log.rhoCentralFoam
- **RC:** 0
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 0.0069997885
- **End line present:** True
- **ExecutionTime count (Time = lines):** 12661
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787625032, all_fields_newer
- **wall_s:** 1418
- **ranks:** 1
- **core_min:** 23.6333
- **Newest file mtime:** 1787626450.427541 (2026-08-25 02:54:10)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL051/L1_120x52

- **Log:** log.rhoCentralFoam
- **RC:** 0
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 0.0070015301
- **End line present:** True
- **ExecutionTime count (Time = lines):** 1693
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787617560, all_fields_newer
- **wall_s:** 9
- **ranks:** 1
- **core_min:** 0.1500
- **Newest file mtime:** 1787617569.238392 (2026-08-25 00:26:09)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL051/L2_240x104

- **Log:** log.rhoCentralFoam
- **RC:** 0
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 0.0069997882
- **End line present:** True
- **ExecutionTime count (Time = lines):** 3365
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787617569, all_fields_newer
- **wall_s:** 207
- **ranks:** 1
- **core_min:** 3.4500
- **Newest file mtime:** 1787617776.144681 (2026-08-25 00:29:36)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

#### VMFL051/L3_480x208

- **Log:** log.rhoCentralFoam
- **RC:** 0
- **endTime (from controlDict):** 0.007
- **Last Time (from log):** 0.0069999107
- **End line present:** True
- **ExecutionTime count (Time = lines):** 6714
- **Time directories:** 3
- **Required fields present:** ['U', 'p']
- **Required fields missing:** ['k', 'epsilon', 'nut']
- **Age guard:** PASS - zero_epoch=1787617781, all_fields_newer
- **wall_s:** 1183
- **ranks:** 1
- **core_min:** 19.7167
- **Newest file mtime:** 1787618964.0634773 (2026-08-25 00:49:24)
- **Reasons for non-COMPLETE state:** missing_fields: ['k', 'epsilon', 'nut']

## Scan Notes

- Depth-unlimited walk using os.walk() to find all run directories
- Positive control verified scanner can see two known-COMPLETE runs
- endTime values read from each directory's own system/controlDict (not sibling values)
- Age guard: all fields at final time directory newer than 0/U or 0/T
- RUNNING state determined by active pid with run directory as cwd
- ExecutionTime count = number of 'Time = ' lines in solver log
- Strict completion: rc=0 AND End line AND last Time == endTime AND required fields present AND ExecutionTime count == endTime AND all fields newer than 0/
