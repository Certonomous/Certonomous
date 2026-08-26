# D7FR — arm `F-S` graded under Addendum 2's grader: **`G5` SHIPPED row = `PASS`, 5 of 5 components, worst 1.959 %, zero sign flips.** Item verdict PENDING `F-P`, and the ported grader's `O`-arm clauses are a structural finding

**Written 2026-08-26 by a dafoam lab-lane for dafoam-supervisor.** Freeze `b424b44e`; Amendment 1 `9feb0815`; **Addendum 2 `13cc6696`** (grader blob `4df305e4…`, md5 `c451af9f…`, verified equal to the repository copy before this grade). Launcher and §7 caps at the freeze (blob check YES). Grade output: run root `d7fr_grade_FS_interim.json` (`--arms P1,X,ACC,F-S --fd-shipped F-S/d7_fd_endpoint.json`, `--work X`, `--cl-target X/d7_cl_target.json`), grader exit 0, `D7FR_GRADER OK`.

## 1. The kernel's record for `F-S`

| field | value | artifact |
|---|---|---|
| container | `d7fr_F_S_20260826T160553Z_80216`, SHIPPED `dafoam/opt-packages:latest`, digest `9d45679d…` | `ledger.txt` |
| rc | **0** — chain watcher `docker inspect [false 0 false]`; launcher marker `rc=0`; **agree** | `STATUS.F-S`, `F-S_20260826T160553Z_80216.log.ok.…` |
| wall / core-min | 1090 s × 4 = **72.667** (cap 750, ceiling 3000, no crossing) | `ledger.txt` |
| memory | pre 28.12, min during **16.315** (n=72), post 25.95 GiB; OOMKilled false | `ledger.txt` |
| placement | cpuset 2,3,4,6, 4 distinct single cores, `delivered_cores_mean` **3.9894** of 4 | `ledger.txt`, `F-S/d7_placement_rank*.json` (G12 PASS on this arm) |
| `End` lines in the arm log | 23 (22 primals + the acceptance pair's cross-check) | `F-S_20260826T160553Z_80216.log` |

`H5` before the arm: `D7FR_H5_PASS` (45/63 s, floor 16.0). Aggregate rule at launch: 8.0 + 2.94 + 12 = 22.94 < 30.6, HOLDS.

## 2. `G5` — the bright line, SHIPPED row (`F-S/d7_fd_endpoint.json`)

Coverage **5 of 5** registered components, plateau trips 5 of 5, `n_excluded` 0, **sign flips 0**, aggregate worst relative error **1.9588833845447848 %**. Per component (adjoint `J_adj` vs central FD at the plateau `step_lo`/`step_hi` = 0.003/0.01):

| component | `J_adj` | rel err % | plateau % | band D | band E | verdict |
|---|---|---|---|---|---|---|
| `shape[115]` | −1.2316e-01 | **0.0697** | 0.046 | PASS | PASS | **PASS** |
| `twist[1]` | — | **1.9589** | — | PASS | PASS | **PASS** |
| `patchV[1]` | — | **0.6271** | — | PASS | PASS | **PASS** |
| `shape[0]` | — | **0.7071** | — | PASS | PASS | **PASS** |
| `shape[119]` | — | **0.1459** | — | PASS | PASS | **PASS** |

(`J_adj`/plateau shown for the first row as read; every row's `band_D_pass` and `band_E_pass` are `true` in the JSON.) **`G6` planted zero, `G6b` blind-reader negative control, `G7` count control — all PASS on the SHIPPED row.** `G9` two-row distinctness: `two_rows_present` false — **PENDING `F-P`**.

## 3. What the item-level grader says, and why that is a finding rather than a verdict

`map_verdict` returns **`NOT A RESULT`** with `because = [G1 completion/age guard, G13 adjoint health (band F)]`, plus the L-342 limitation line naming `G12 arm P1/X: delivered_cores_mean NOT_MEASURED` (those two arms are not MPI arms and the launcher never measured delivered cores for them — disclosed, not voiding).

Both hard fails are **structural to the port, not to this run**: (a) G1's age guard fails on exactly one artifact, `X/OptView.hst` (`mtime 1787711453 < datum 1787719601`), because it IS D7R arm `O`'s file, staged with its mtime preserved — the launcher's `H4 ENDPOINT_PROVENANCE` (`d7fr_run_arm.sh:353-359`) *requires* it to be D7R's; the other three artifacts are newer than the datum. (b) G13 reads adjoint health for an arm `"O"` hard-coded in `grade()` (`d7fr_grade.py`, `g13_adjoint_health(base, ledger, "O")`), and **D7FR has no arm `O`** — the item re-registers the endpoint FD of D7R's `O`, so `arm_absent_from_ledger` is a category error, not a health finding. (c) For the record, G2/G3/G4 read D7R's own 30-major history (band A false, cap-stop, 30.40 % reduction) — D7R's verdict, not reopened here.

**Not repaired by this lane.** Both are grader clauses inherited from the D7 port that assume an optimisation arm; fixing them is a grader amendment on the supervisor's read (it would touch which arms G1/G13 apply to — a verdict-logic change, outside L-342's licence). Until ruled, **the item verdict is `PENDING`** and this record claims only what §2 shows: the SHIPPED endpoint FD row passes the bright line.

## 4. Cost — estimate versus actual (rule 12)

Predicted **485.0** core-min (22 primals × 20.27 + 24.2 colouring + 14.6 `compute_totals`); actual **72.667** (gross = cleaned; no row over 3600 s); **ratio 0.150**; **$0.0621 DERIVED** at $0.0513/core-h, `cost_basis` REPORTED-BY-OWNER. Attribution: **misprediction, the same mechanism as `ACC` (C-122)** — a primal priced at 20.27 core-min from arm `O`'s per-evaluation mean, which §7 itself says overstates a primal; 22 primals plus colouring ran in 1090 s ≈ 3.3 core-min per primal. Contention present, not limiting (3.9894 of 4 cores delivered; sibling `d12y_S2b`/`S3*` on cpu 12). No waste, no overrun.

## 5. Pending

`F-P` (PATCHED, `dafoam-idwarp-rot:v1`) fired by the chain 16:25:11Z as `d7fr_F_P_20260826T162511Z_139564`; **`PENDING`: run root `STATUS.F-P`**. Full grade when it lands: same command with `--arms P1,X,ACC,F-S,F-P --fd-patched F-P/d7_fd_endpoint.json`, after the blob check against `13cc6696`.
