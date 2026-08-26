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

---

## 7. THE L-342 RE-GRADE ON THE REPAIRED GRADER, THE F3 r2 TRIAGE, AND THE TWO-ROW TABLE AS IT STANDS — added 2026-08-26T22:17:46Z by dafoam lane V2 (fifteenth session)

**This section supersedes §2's "why `NOT A RESULT`" on the grader path** (that grader, `74841576…`, was struck at Addendum 2 and replaced by the L-342 grader, now `f825c2cd…` at Addendum 2d) **and §5's WASTE label on arm O** (struck below, and in `docs/COST_CALIBRATION.md` by quote-and-strike, row `C-145`). **The item verdict is unchanged in token — `NOT A RESULT` — and changed in reason.** Nothing here is sent, filed, uploaded, registered, posted or commented (rule 7). No frozen file was edited; the pre-registration carries Addendum 2e (the triage record).

### 7.1 What ran since §1, and what it cost

| arm | container | inspect exit / oom | wall s | core-min | cap | ledger row | disposition |
|---|---|---|---|---|---|---|---|
| ACC (16:47Z, `compute_totals`, 8 g) | `d4_ACC_20260826T164743Z_200655` | 137 / **true** | 525 | 35.0 | 80.0 | written | **WASTE** (Addendum 2c, C-132); directory moved aside, not removed |
| F3 (17:24Z) | — (guard refusal `:281`, no container) | — | — | 0 | 120.0 | — | `rc=5` preserved as `STATUS.F3.guard_20260826T172512Z` (Addendum 2d) |
| **F3 r2 (20:50Z, runner-launched, prereg `08039792`)** | **`d4_F3_20260826T205120Z_411184`** | **1 / false** | **41** | **2.733** | 120.0 | written | **`rc=1`: endpoint primal not accepted — §7.2; SPEND, not waste (Addendum 2e A2e.3)** |
| ACC (chain position 2 of r2) | — | — | — | 0 | 80.0 | — | never fired: `STATUS.chain` `STOPPED_AT_FIRST_NONZERO arm=F3 rc=1` |

Gross to date **811.200 core-min** (P1 0.667 + P2 41.133 + O 731.667 + ACC 35.0 + F3 2.733); graded-arm spend (P1, P2, O, F3) **776.200**; waste, named separately and never absorbed: **35.0** (C-132). Dollars DERIVED at $0.0513/core-h, not measured: gross **$0.6936**.

### 7.2 F3 r2 crash triage — condensed from `PREREGISTRATION.md` Addendum 2e, which carries every line citation

The container's log shows DAFoam's own initialisation `decomposePar` refusing an already-decomposed case (`:76-112`) — **the identical block, at the identical lines, in D4 PATCHED F3's log** (`CURRICULUM-D4-a2-wing-cdmin/F3_20260825T220706Z_2733788.log:76-112`), which went on to `rc=0` — so it is a shared warning, not a defect; the inherited `processor*` decomposition is byte-identical (per-processor polyMesh md5) across `F3/`, `O/`, `P1/`, `P2/` and D4's own `F3/` and `O/`, and equals what P1's two `decomposePar -force` runs produced (G8 `PASS`). **The primal then ran to `endTime` 1000 on the SHIPPED endpoint and plateaued from Time ≈ 400 at `nuTilda` initRes 1.115891818e-05, above the producer's registered acceptance `primalMinResTol × primalMinResTolDiff = 1e-8 × 1e3 = 1e-5` (`d4_opt_runScript.py:36-37`)** — the log's own words: `Primal min residual 1.115891818e-05 / did not satisfy the prescribed tolerance 1e-08 / Primal solution failed!` (`:867-869`), `AnalysisError` from `mphys_dafoam.py:345`, mpirun exit 1. **The PATCHED endpoint's floor on the same rule was 9.780100659e-06 — accepted by 2.2 %; the SHIPPED endpoint's is 11.6 % above it; the two floors differ by 1.141×.** RULING (supervisor's frame, `[lab-attributed]`): the failure is **INDEPENDENT of staging** — a tolerance-at-the-residual-floor condition at the SHIPPED endpoint; **no re-fire buys anything; `D4-SHIPPED_F3_ACC_r3` NOT filed; 0 further core-min.** Named **`D4S-PREREG-DEF-1`** (the acceptance threshold sits at the instrument's own residual floor on this case; found, not repaired). An uncommitted wrapper on disk that would restate `primalMinResTolDiff` 1e3 → 2e3 (`d4s_primal_accept_wrap.py`, previous lane's draft, absent from HEAD) is a post-compute threshold change and is **referred, not adopted** (Addendum 2e A2e.4).

### 7.3 The grade, on the registered invocation — output VERBATIM

Grader `d4s_grade.py` md5 `f825c2cd81631b83b7d0954981540c15` == `git show 08039792:…/d4s_grade.py` (asserted before the run); launcher `d4s_run_arm.sh` `506c99e6…` == its blob. Invocation as registered at Addendum 2d: `--base <run root> --work <run root>/F3 --arms P1,P2,O,F3 --launcher d4s_run_arm.sh`. Output file **`cases/dafoam/ladder-a/A2/curriculum_D4_SHIPPED/d4s_grade_ITEM_F3r2_20260826T220904Z.json`** (stdout beside it, `.stdout`), exit **2**. The stdout line, verbatim:

```
D4_GRADER REFUSED G1-age: {"graded_artifact_absent": "/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/F3/d4_fd_endpoint.json"}
```

The `verdicts` object of that file, verbatim (the gates that composed a token before the refusal):

```
{"G10_cap_discipline": "GATE FAIL", "G11_memory_envelope": "NOT A RESULT", "G12_cpu_placement": "PASS", "G8_decomposition_determinism": "PASS", "G9_toolchain_identity": "PASS"}
```

and `"REFUSED": "G1-age: {\"graded_artifact_absent\": \"…/F3/d4_fd_endpoint.json\"}"`.

**Gate readings in the same file's `report`, by gate** (readings, not tokens, where the composition was interrupted):

| gate | reading (`report.<key>`) | what it says |
|---|---|---|
| G1 rc clause | `rc_failures: [{"arm": "F3", "kernel_rc": 1, "oomkilled": "false"}]`; P1 (SCRIPT) / P2 / O (SOLVER, kernel record) `rc_clause_pass: true` | F3 fails clause 1; O passes from `docker inspect` (`field_sources` named per field) |
| G1 terminal clause | `terminal_failures: [F3: last_nonempty_line "----…", n_lines_after_last_occurrence 10, terminal_ok_POSITIONAL false]`; O `true` (kernel-held stream, positional); P1 `true` under the SCRIPT rule (6 artefacts newer than datum 1787716334) | F3's log ends on the mpirun abort banner, exactly the §3.2 discriminator |
| G1 age clause | **REFUSED**: `graded_artifact_absent F3/d4_fd_endpoint.json` | the graded FD artefact does not exist; the grade stops here (exit 2), as the frozen clause says |
| `arm_kinds_from_launcher` == `arm_kinds_registered` | `{ACC: SOLVER, F3: SOLVER, O: SOLVER, P1: SCRIPT, P2: SOLVER}` | Addendum 2b/2d kinds agree |
| G2 CL feasibility (arm O, from `F3/d4_major_history.json`, 164 rows) | `n_outside_per_major_band: 50`, `worst_abs_dev: 2.149e-02`, `final_abs_dev: 6.5897e-05`, `pass_per_major: false`, `pass_final: false` | band A fails over the full history (the population D4 §11.6 names — line-search rows included); **band B fails: the SHIPPED terminus is 6.59e-05 from `CL = 0.5` against 1e-5**, consistent with IPOPT's `inf_pr 6.59e-05` at max-iter |
| G3 termination (arm O) | `converged: false`, `n_majors: 100`, `EXIT: Maximum Number of Iterations Exceeded.`, `final_objective: 0.021120596`, `final_inf_du 3.52e-05`, `final_inf_pr 6.59e-05` | per the frozen rule `converged=False` → `NOT A RESULT` for the optimisation (G2 does not pass, so not `GATE REACHED`) |
| G4 drag reduction (arm O) | `reduction_pct: 28.6939`, `CD_first_major 0.0296196` (matches A2 baseline), `CD_final 0.0211206`, `in_band: true` [25, 45] | in band; **not composed** (G3 not converged). Hand note, NOT A VERDICT: PATCHED 28.6758 % (D4 §11.4) |
| G8 | A == B `{9504, 9600, 9608, 9592}`, 38,304 cells, scotch | `PASS` |
| **G9** | `idwarp_so_md5_distinct: ["f0fcb488e0e98156575cd19548e91663"]` over **5** sources (P1, P2, ACC, F3 logs + `docker_logs:d4_O_20260826T040414Z_3177545`), one digest `9d45679d…`, `rows: ["SHIPPED"]` | **`PASS`** — S6 HIT, graded |
| G10 | O `731.667 > 620.0` `within_cap: false`; P1 0.667 / P2 41.133 / ACC 35.0 / F3 2.733 within; total ≤ 880 | **`GATE FAIL`** exactly as registered at A2.3 (the +18.0 % crossing, named, never absorbed) |
| G11 | `arms_oomkilled: ["ACC"]`, `n_arms: 5` | **`NOT A RESULT`** — the frozen clause reads every ledger row, and the 16:47Z ACC waste row (Addendum 2c) is OOM-killed; disclosed, not re-labelled |
| G12 | affinity union `[5,6,7,9]`, distinct single cores, P2 3.9689 (n=40), F3 3.7450 (n=2), O/P1 delivered `NOT_MEASURED` | `PASS` |
| `NOT_MEASURED` (disclosure, never composed) | O: `memavail_pre/post, delivered, siblings_pre/post, cpu_series, log`; P1: `delivered` | L-342 field classes, as registered |

**Does arm O grade on its artefacts under the repaired grader? YES.** G1's rc and terminal limbs, G2, G3, G4, G8, G9, G10 and G12 all reached readings from `O/` plus the kernel record (`G1_kernel_record_fallback.O`: `field_sources` per field, `wall_s` from `StartedAt/FinishedAt`, 731.667 core-min). The refusal is on **F3's** absent artefact, not on O. **Therefore §5's "WASTE 731.667" is STRUCK — quoted and struck, never rewritten: ~~"WASTE, named separately per COMPUTE_BUDGET_CHARTER §6: 731.667 core-min — the arm ran to completion and produced intact artifacts, and the frozen grader cannot consume them"~~ → the repaired grader consumes them; the 731.667 core-min are SPEND on arm O of this item (`docs/COST_CALIBRATION.md` `C-145` quotes and strikes C-117's label the same way).** What that spend bought is stated in the G2/G3/G4 rows above and in §7.4.

### 7.4 THE TWO-ROW TABLE, as it honestly stands (`DAFOAM_CHARTER.md` §6; prereg §1, §5)

| row | image digest | `libidwarp.so` md5 (G9) | O: majors / `EXIT:` / CD at terminus | **G5 endpoint FD (5 registered components, band D 5 %)** | source |
|---|---|---|---|---|---|
| **PATCHED** | `2927768a…` | `85f59e87253e0a71a813f64ca6e4c425` (`CURRICULUM-D4-a2-wing-cdmin/f3_ledger.txt`) | 80 / `Optimal Solution Found` / 0.021130919 | **`PASS` — 5/5, aggregate 0.1634451673004621 %, 0 sign flips, worst `shape[0]` 2.29 %** | D4 `RESULTS.md` §11.3–§11.4 at `1697ea49` |
| **SHIPPED** | `9d45679d…` | `f0fcb488e0e98156575cd19548e91663` (this grade, 5 sources) | 100 / `Maximum Number of Iterations Exceeded` / 0.021120596 (`inf_pr` 6.59e-05) | **`NOT A RESULT` — no FD table: F3 `rc=1`, `d4_fd_endpoint.json` absent; grader `REFUSED G1-age graded_artifact_absent`; cause §7.2 (endpoint primal min residual 1.1159e-05 > 1e-5 acceptance, `D4S-PREREG-DEF-1`)** | `d4s_grade_ITEM_F3r2_20260826T220904Z.json` |

**The two rows are two toolchains by hash (G9 `PASS` on each, distinct md5s) and the family still holds no two-row G5 verdict on this case.** Under prereg §5 the registered reading of a SHIPPED driver that *"fails to converge"* is *`NOT A RESULT` for the optimisation, and a RESULT about the gradient*; **what this item measured on the SHIPPED row is narrower and is stated as such**: (i) the driver on the shipped gradient exhausted its 100-major budget without reaching feasibility (`inf_pr` 6.59e-05 vs band B 1e-5) where the patched driver reported `Optimal Solution Found` at 80 majors — a hand comparison, NOT A VERDICT (§3 stands); (ii) the SHIPPED endpoint's primal floors 14 % higher than the PATCHED endpoint's on the same rule and lands above the registered acceptance, so **no FD table exists on the SHIPPED row and none can be bought without a threshold restatement that is not the lane's to make** (Addendum 2e A2e.4). Nothing about band D on the SHIPPED row is claimed in either direction.

### 7.5 ITEM VERDICT

> **`NOT A RESULT`.** The registered grade REFUSED at G1's age clause on the absent SHIPPED FD artefact (exit 2, file above); G10 `GATE FAIL` (O +18.0 % over cap, registered consequence); G11 `NOT A RESULT` (the ACC waste row); G8/G9/G12 `PASS`; G3 `converged=False`. **The pre-repair verdict (§2, grader `74841576…`: refused on the absent O row) stands beside this one; the reason moved from bookkeeping to physics, which is what L-342 was for.**

### 7.6 Predictions — scored where the record allows, never adjusted (supersedes §4)

| id | outcome |
|---|---|
| S1 | **HIT** — 731.667 in 400–800 (511.133 the registered lower bound) |
| S2, S3 | **UNSCORED** — no SHIPPED endpoint FD table |
| S4 | **HIT** — `EXIT:` printed (`Maximum Number of Iterations Exceeded`) |
| S5 | **UNSCORED** — G1's rc and terminal limbs reached readings on all four arms; the age limb REFUSED on F3's absent artefact before a G1 verdict composed |
| S6 | **HIT, graded** — G9 `PASS`, one distinct md5 `f0fcb488…` over 5 sources including the kernel-held O stream |
| S7 | **UNSCORED** — P2 3.9689 (n=40) and F3 3.7450 (n=2) ≥ 3.0; O's sampler partial (`NOT_MEASURED` in the grade) |

### 7.7 Cost — estimate versus actual (`CLAUDE.md` rule 12), rows `C-145` and `C-146`

- **Arm O**: 731.667 core-min measured-derived (`docker inspect` StartedAt/FinishedAt × 4 ranks, the grader's `G1_kernel_record_fallback.O.field_sources`) vs 511.133 registered as a **lower bound** (§4.2) → ratio **1.431**; cap crossing **+18.0 %** (731.667 > 620.0), named, never absorbed; gap: +25 % majors (100 vs 80 — §4.2's caveat fired) × +14.6 % wall/major (contention named, no uncontended control bought). $ **0.6256 DERIVED**, not measured. **C-117's WASTE label struck; SPEND.**
- **Arm F3 r2**: 2.733 core-min vs 47.267 predicted (D4's measured F3) → ratio **0.058**; gap: the arm ended at its first primal's acceptance decision (41 s) — the prediction priced a full FD sweep that never began; SPEND (Addendum 2e A2e.3), the supervisor may relabel. $ **0.0023 DERIVED**.
- Item to date: graded arms 776.200 vs 595.133 predicted for those arms (P1 0.333 + P2 36.400 + O 511.133 + F3 47.267) → ratio **1.304**; waste beside it 35.0 (C-132). Not closed: no two-row verdict, and no further compute is registered.

### 7.8 What is preserved, and what is on the desk

`O/`, `F3/` (staged copy with its `.d4_stage_F3_copy_epoch`, the r2 outputs `d4_endpoint_dvs*.json`, `d4_major_history.json`, `d4_fd_endpoint.jsonl` (102 bytes, the `endpoint_dvs` line only), `d4s_cmd.sh`), `ACC_oom_compute_totals_20260826T164743Z/`, every `STATUS.*` (current and `cp -p` copies), both grade JSONs, and container `d4_O_20260826T040414Z_3177545` — **preserved, nothing removed.** On the supervisor's desk, and through them Sanaa's: whether a restated primal acceptance (`primalMinResTolDiff` 2e3, ≈ 47.3 core-min) is a repair the lab will register for BOTH rows under one rule, or whether this case closes as it stands.
