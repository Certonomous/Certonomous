# D4-SHIPPED — RESULTS: **`NOT A RESULT`** on the grader path

**Item** D4-SHIPPED (`cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED/`, frozen `94ddfc48`, amendment
`c416662e`). **Run root** `/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin`.
**Verdict** `NOT A RESULT`. **Ruling** dafoam-supervisor, route (iii), 2026-08-26 [lab-attributed]:
§2d.1 refused (conditions 3 and 4 satisfiable only vacuously); the item is **closed on its frozen
grader path and re-registered as D4-SHIPPED-R**. **Written 2026-08-26 by the D4-SHIPPED lane.**

## 1. What ran, and what did not

| arm | container | inspect exit / oom | wall s | core-min | cap | ledger row |
|---|---|---|---|---|---|---|
| P1 | `d4_P1_20260826T035214Z_3130694` | 0 / false | 10 | 0.667 | 5.0 | written by launcher |
| P2 | `d4_P2_20260826T035301Z_3131586` | 0 / false | 617 | 41.133 | 55.0 | written by launcher |
| **O** | **`d4_O_20260826T040414Z_3177545`** | **0 / false** | **10,975** | **731.667** | **620.0 (+18.0 %)** | **ABSENT — launcher shell died** |
| ACC | — | — | — | — | 80.0 | not fired |
| F3 | — | — | — | — | 120.0 | not fired |

Arm O's container started 04:04:14.84Z and finished 07:07:09.64Z (`docker inspect`, still
present because the launcher registered no `--rm`). The launching shell — the poller after
`docker run -d` — died with the agent fleet at ~05:00Z. `O_launch.out` ends at
`D4S_RUNAWAY_GUARD`; the CPU sampler file ends at 05:04:07Z (237 samples). The post-container
bookkeeping (`docker logs` → `O_<stamp>.log`, `inspect` → ledger row, `.log.ok` sentinel) never
ran. **This is the exposure ADDENDUM 1 §A1.3 registered OPEN** ("the cap does not survive shell
death") realising; it is not a new defect.

## 2. Why `NOT A RESULT`, gate by gate — from the frozen code, not run on the live root

- **G1** (`d4s_grade.py::g_completion`): an arm absent from `ledger.txt` → `refuse("G1",
  arm_absent_from_ledger)` → exit 2, the whole grade refused. A reconstructed row carrying
  `memavail_post_GiB=NOT_MEASURED` **does not match `LEDGER_RE`** (`:675` requires `[\d.]+`) and is
  indistinguishable from an absent row. No on-disk record of host `MemAvailable` at ~07:07Z exists
  anywhere under `certonomous-runs` (mtime sweep 06:50–07:20Z), so the field cannot be reconstructed
  from a record, and inventing a number is forbidden.
- **G9** (`g_toolchain`): greps `D4_IDWARP_SO_MD5:`; this launcher's containers print
  `D4S_IDWARP_SO_MD5:` (P2's log carries only the `D4S_` form). `uniq_so` is empty → `GATE FAIL`
  on every arm **by construction**. Recorded as **D4S-GRADER-DEF-1 — an instrument defect, NOT a
  finding about the toolchain**, frozen into 94ddfc48 and c416662e.
- **Invocation**: the grader's `--arms` default is `P1,P2,O,F`; this item's launcher writes `F3`;
  no invocation line was registered.
- Age guard (**would PASS**): `O/.d4_age_datum` 1787717054 == mtime of `O/0/U`; 6,253 files in
  `O/` are newer; `OptView.hst` and `opt_IPOPT.txt` at 1787728010. Recorded so the next reader
  knows the artifacts are cold-start clean; it changes no verdict.

Frozen-blob check: `d4s_grade.py` md5 `74841576480992cf21c1cc036537e839` = §8; grader, launcher and
PREREGISTRATION.md blobs identical at HEAD, working tree and `c416662e`.

## 3. THE HAND READING — **NOT A VERDICT**, and never to be quoted as one

The artifacts are intact and were read by eye. This is **information about what the run did**,
not a graded result; nothing below passed a gate.

| | PATCHED (curriculum_D4, graded) | SHIPPED (this item, **NOT A VERDICT**) |
|---|---|---|
| IPOPT majors | 80 | **100** |
| `EXIT:` | `Optimal Solution Found` | **`Maximum Number of Iterations Exceeded`** |
| final objective (CD, `opt_IPOPT.txt`) | — (see D4 RESULTS.md) | 2.1120596268401275e-02 |
| wall s / core-min | 7,667 / 511.133 | 10,975 / 731.667 |
| wall per major | 95.8 s | 109.75 s |
| delivered cores (mean) | 3.9880 (n=508) | 3.9859 (n=237, **partial** — sampler died ~05:04Z) |

The equal-major assumption in §4.2 was a **MISS** (+25 % majors) and §4.2's registered caveat —
"may need more majors than 80" — is the one that fired. **The `libidwarp.so` md5 inside the
shipped container reads `f0fcb488e0e98156575cd19548e91663`** (container log line
`D4S_IDWARP_SO_MD5:`), which is the value prediction S6 named.

## 4. Predictions — scored where the record allows, else UNSCORED

| id | outcome |
|---|---|
| S1 | **HIT** — 731.667 in 400–800; 511.133 was the registered lower bound, not the prediction |
| S2, S3 | **UNSCORED** — no endpoint FD table (F3 not fired) |
| S4 | **HIT** — `EXIT:` printed; not `Optimal Solution Found`, which was not predicted |
| S5 | **MISS by absence** — G1 cannot reach a verdict through any limb on an absent row |
| S6 | **HIT** (hand reading of the container log; the grader's G9 could not have read it) |
| S7 | **UNSCORED** — P2 3.9689 (n=40) met it; O's sampler is partial; ACC/F3 not fired |

## 5. Cost — estimate versus actual (`CLAUDE.md` rule 12)

- Predicted (§4): 598.133 core-min, ceiling 880.0. Actual gross: **773.467 core-min**
  (0.667 + 41.133 + 731.667); ratio actual/predicted for the arms that ran = 773.467 / 548.200 =
  **1.411**. Arm O alone: 731.667 / 511.133 = **1.431** — attributed to +25 % majors (1.25×) and
  +14.6 % wall per major (contention: peers' d12y containers were live for the whole run; no
  uncontended control was bought, so this is NAMED, not explained).
- **Cap crossing: 731.667 > 620.0, +18.0 %**, ceiling 2480 not reached. Reported, named, not
  absorbed — nothing enforced anything after ~05:00Z.
- **WASTE, named separately per COMPUTE_BUDGET_CHARTER §6: 731.667 core-min** — the arm ran to
  completion and produced intact artifacts, and the frozen grader cannot consume them. Dollars
  DERIVED at $0.0513/core-h (reported-by-owner, not measured): waste **$0.6256**; item gross
  **$0.6613**.
- Calibration row: `docs/COST_CALIBRATION.md` C-row landed with this file.

## 6. What is preserved, and what happens next

- **`O/` and container `d4_O_20260826T040414Z_3177545` are PRESERVED byte-for-byte as evidence.**
  Not removed, not chowned, not touched. The `docker inspect` record is the only kernel record of
  the run and lives in that container.
- The item is **superseded by D4-SHIPPED-R** (`cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED_R/`,
  run root `CURRICULUM-D4-SHIPPED-R-a2-wing-cdmin`), which re-registers the same arms and
  predictions with: O cost MEASURED-DERIVED from this run (731.667), D4S-GRADER-DEF-1 repaired at
  registration, the arm list registered in the invocation line, and the cap-dies-with-shell
  exposure CLOSED (deadline inside the container; bookkeeping in a `setsid nohup` driver shown to
  survive its parent's death).

## Appendix — the reconstructed arm-O row: **RECONSTRUCTED, NOT LEDGER**

Never appended to `ledger.txt`; the grader cannot parse it and it must not be mistaken for a
launcher transcription. Field sources: rc/inspect/wall from `docker inspect` (ExitCode,
OOMKilled, StartedAt, FinishedAt); `memavail_pre`, `siblings_pre`, cap fields from the live
`D4_HOST_PRE`/`D4_CAP_ASSERT` lines in `O_launch.out`; digest/cpuset/memory corroborated by
`HostConfig`; `delivered` from the sampler file; `enforced_wall_s=9300` is what the launcher
COMPUTED — nothing was enforced after ~05:00Z.

```
ARM=O ROW=SHIPPED IMG=dafoam/opt-packages:latest DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc rc=0 wall_s=10975 ranks=4 core_min=731.667 cap_core_min=620.0 enforced_wall_s=9300 enforced_core_min=620.000000 memory=12g inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=26.01 memavail_post_GiB=NOT_MEASURED cpuset=5,6,7,9 delivered_cores_mean=[3.9859 n=237 max_nr_throttled=12770 PARTIAL_sampler_died_~0504Z] siblings_pre=[d12y_S4_n40_r1_20260826T033053Z_3069758] siblings_post=[NOT_MEASURED] log=O_20260826T040414Z_3177545.log(NOT_WRITTEN) stamp=20260826T040414Z_3177545 RECONSTRUCTED_FROM_INSPECT=yes shell_death=fleet_kill_~0500Z
```
