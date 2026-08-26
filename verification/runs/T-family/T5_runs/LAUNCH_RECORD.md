# T5 LAUNCH RECORD

**Launch authority:** Sanaa's words boarded at commit `bc0e687e` ("anything that leads to the lab having more runs"). Every launch below cites `bc0e687e`. **Route (supervisor, 2026-08-26 ~16:20Z):** no self-launch; entries are dropped in `verification/queue/heat-transfer/` and the cfd queue runner (`scripts/queue_runner.py --daemon`, pid 133204) launches under the 80-90 % band. **Enqueueing is not authorisation** (queue README); supervisor check 4 was performed on `0fcbb92e` at 15:56Z (board `df2719f9`).

Frozen grading path: prereg `0fcbb92e` (blob `8ad8451e`), `digitise_t5.py` `e55d6208`, `analyse_t5.py` `17703b78`, `run_one_t5.sh` `313df45c` -- all verified byte-identical on disk at 15:5xZ before any build. Reference slot commit `89d38653`; instruments + cases commit `b98f3930`.

## Governor readings (`scripts/compute_stage_count.py --cap 4 --ready 1`)

| UTC | busy cores | headroom | STAGE |
|---|---|---|---|
| 2026-08-26T16:0xZ (first read, before build) | 12.12 of 16 (75.7 %) | 2 | 1 |
| 2026-08-26T16:28:28Z (X_2d enqueue) | see runner.log | -- | 1 |

## Timeouts, and where the numbers come from

`--timeout` = per-case cap [core-min] x 60 / ranks. The per-case cap is the **3x Model B guard of prereg S11.3** applied to the Model B core-h of S11.1 (X_2d 0.44 core-h = 26.4 core-min; C and H_c 0.76 core-h = 45.6 core-min each):

| case | Model B core-min | cap = 3x | ranks | timeout s |
|---|---|---|---|---|
| X_2d | 26.4 | 79.2 | 1 | 4752 |
| T5_CUBE_c | 45.6 | 136.8 | 1 (see finding F1) | 8208 |
| H_c | 45.6 | 136.8 | 1 (F1) | 8208 |

## Launches

### X_2d -- enqueued 2026-08-26T16:28Z citing bc0e687e
Entry `verification/queue/heat-transfer/T5_X_2d.json`, `queue_entry_check.py`: ACCEPTED (team=heat-transfer case=T5_X_2d ranks=1 est=26.4 core-min). Runner pickup, pid/sid and STATUS path: appended below when the runner logs them.

### T5_CUBE_c, H_c -- NOT YET ENQUEUED
Prereg S5.3: the mapping plane is selected from the CONVERGED X_2d **before any graded case is launched**, and the 3-D inlet reads `constant/boundaryData/inlet` which does not exist until `map_inflow_t5.py` has run on `DONE.X_2d`. `check_launcher_can_launch.py --one-iteration T5_CUBE_c` at 16:27Z returned **FAIL**: "Need at least 3 non-collinear points for planar interpolation, but only had 0 points" -- the case cannot start today and is not put on a queue it would die on at zero compute (the F16/L-339 shape). Enqueued the moment the map exists.

## Findings against frozen instruments (reported, not worked around)

- **F1 -- `run_one_t5.sh` (313df45c) runs the solver SERIALLY**: line `timeout "$TIMEOUT_S" "$SOLVER_PATH" -case "$CASE_DIR"` -- no `mpirun`, no `-parallel`; `--ranks` only scales `timeout_s` and the `core_min` it writes. Launching C with `--ranks 4` would record core_min = wall x 4 / 60 for a one-core run -- a fabricated cost. C and H_c are therefore enqueued at **ranks 1** with the cap converted at 1 rank, and the S11 `nProcs 4` registration cannot be honoured by the frozen launcher.
- **F2 -- the frozen digitiser refuses every registered figure** (commit 89d38653): all graded rows BLOCKED under S7.5(3).
- **F3 -- `analyse_t5.py` YPLUS_WALLS names `cube_side_s`**, which does not exist on the registered half domain (S5.2, symmetry at z/H = 0). The y+ gate returns NOT A RESULT on every level by construction unless the comparator is amended or a full-span domain is registered.
- **F4 -- T5_CONFIGURATION_RULING.md (2026-08-25) rules T5 onto the MATRIX configuration; the frozen prereg (2026-08-26) registers the SINGLE cube at Re_H 4440.** The frozen document was followed; the contradiction is on the supervisor's desk.
- **F5 -- checkMesh birth certificates: every 3-D air region "Failed 1 mesh checks"** (`***Cells with small determinant (< 0.001)`: C 4406, M 15727, F 59818 cells; max aspect ratio 133 / 135 / 140, above the S5.4 "30-70" expectation). Non-orthogonality 0, skewness ~1e-13. Epoxy regions: Mesh OK. Reported with the numbers, not hidden.
- **F6 -- a smoke test in scratch (S15 tooling disclosure)**: `T5_CUBE_c` dictionaries with a UNIFORM inlet, 60 iterations of `chtMultiRegionSimpleFoam`, ExecutionTime 10.52 s on one core with the box at load ~8/16: **(52684+869) x 60 / 10.52 = 3.05e5 cell-it/core-s**. Model B at 5.4e4 cells is 1.16e5, Model A the same below 2.36e5 cells. Fields deleted; no h read. A measured throughput, not a result.

## X_2d OUTCOME -- REFUSED BY THE FROZEN LAUNCHER AT ZERO COMPUTE (2026-08-26T16:28:57Z)

Runner: `LAUNCHED team=heat-transfer case=T5_X_2d pid=158670 sid=158670` (LAUNCH_LOG.tsv). `X_2d/log.launch`, verbatim:
`REFUSE: no 0/**/T, so the age guard has no datum`. **No `STATUS.X_2d` was written** (correct: nothing ran, no rc is invented). Solver never started; `0/` was armed from `0.orig` and left in place (inspected, not reverted).

- **F7 -- `run_one_t5.sh` (313df45c) cannot launch the X_2d precursor**: its age-guard datum is `0/**/T`, and a `simpleFoam` precursor carries no `T` field. The frozen launcher refuses every X_2d launch; not worked around (a planted passive `T` would be routing around a frozen refusal). Supervisor's call: amend the launcher (re-freeze) or register the datum as `0/U` for X_2d.
- **F8 -- the queue runner recorded `X_2d/STATUS.T5_X_2d` = `rc=0 end=2026-08-26T16:28:57Z`** for a launch that REFUSED. It trusted the exit status of the self-detaching parent (`exit 0` after `exec setsid ... &`), which S16.1 says is meaningless. A refused launch reads as a clean completion in the runner's own STATUS. cfd territory; reported, not repaired.
- Consequence: T5_CUBE_c and H_c stay un-enqueued (no inflow map without a completed X_2d); **no C throughput measurement was possible**; the only rate on record is the scratch smoke F6. Zero core-minutes spent on the rung tree (the F6 smoke spent 10.5 core-s in scratch).

## Supervisor triage applied (2026-08-26 16:33-16:40Z) — amendments, one commit each
A1 `5cf90e52` (run_one_t5_x2d.sh, datum 0/**/U; X_2d UNGRADED) · A2 `05a03a43` (all 3-D cases serial, timeouts re-derived) · A3 `c6bef4fe` (YPLUS_WALLS fix PROPOSED only, blob 9c2c1d44; frozen 17703b78 unchanged — supervisor's read not obtainable in-session) · A4 `9f1cb468` (single cube stands; matrix -> T5m) · A5 `19385198` (aspect band is an expectation; disclosed; cases proceed).

### X_2d re-enqueued 2026-08-26T16:35:00Z citing bc0e687e — `T5_X_2d_v2.json`, prereg_commit `05a03a43`, launcher `run_one_t5_x2d.sh`, timeout 4752 s, ranks 1, ACCEPTED by queue_entry_check; governor STAGE 1 at 16:35Z (11.3/16 busy).
**NOT PICKED UP as of 16:40Z.** `scripts/queue_runner.py` returns `HELD` at the first entry that does not fit (lines 283-288) and orders entries oldest-first, so cfd's older `T3_R_ff.json` (8 ranks, HELD every tick at ~11-12/16 busy) **head-of-line blocks a 1-rank entry** (F9). cfd's runner and cfd's entry; neither touched. Pickup, pid/sid, STATUS.X_2d and DONE.X_2d are to be appended by whoever observes them; then `map_inflow_t5.py`, then C at ranks 1 — only once the reference JSON is committed by the digitisation lane and the supervisor says so.
