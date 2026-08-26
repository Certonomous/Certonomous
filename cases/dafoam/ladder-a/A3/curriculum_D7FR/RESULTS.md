# D7FR — ITEM VERDICT: **`PASS`** — SHIPPED row `PASS` (5 of 5, worst 1.959 %), PATCHED row `PASS` (5 of 5, worst 1.959 %); shipped-vs-patched divergence **0.000 % on every component**; 149.534 core-min against 997.75 predicted (ratio 0.150), $0.1279 DERIVED

**Written 2026-08-26T17:06Z by a dafoam lab-lane (VERDICT lane) for dafoam-supervisor.** Item `curriculum_D7FR`, A3 ONERA M6, 42,120 cells, np=4. Freeze `b424b44e`; Amendment 1 `9feb0815` (pre-compute, H5); Addendum 2 `13cc6696`; Addendum 3 `da3bd15d`; **Addendum 4 `faeda019` — the registered composition (`D7FR-GRADER-DEF-1`).** Every decision below is `[lab-attributed]`; nothing leaves the box (rule 7).

**The grading path, verified by hash before the grade (rule 2):**

| copy | blob (`git hash-object`) | md5 | what it is |
|---|---|---|---|
| `HEAD:cases/dafoam/ladder-a/A3/curriculum_D7FR/d7fr_grade.py` at `5da3afc0` | `1b810913de3a0d0d381988a26789ebf577b5c978` | `4303704523de7e1c8fa6d6a34a858ded` | **the Addendum-4 blob registered at `faeda019` §A4.4 — THE GRADING PATH** |
| the case-directory copy that ran this grade | `1b810913de3a0d0d381988a26789ebf577b5c978` | `4303704523de7e1c8fa6d6a34a858ded` | equal to the HEAD blob, byte for byte |
| the run-root copy `/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/d7fr_grade.py` | `35f62221aa175b7e50574d762a55d4c11a3a6375` | `cda7c0492663a3926f2a023476ce9b83` | **the PRE-ADDENDUM frozen blob** (§14 md5 at the freeze; `d7fr_run_arm.sh:181` `MD5_GRADE`, asserted at `:254` before every launch). It exists for the launcher's assertion and every arm ran under it; **it is NOT the grading instrument** (Addenda 2–4 each say so) |

So: the run-root copy is the pre-addendum blob, as the launcher's `:254` assertion requires, and the grade below was taken under the HEAD Addendum-4 blob, which is the registered grading path. Launcher `d7fr_run_arm.sh` md5 `91a561eaf41110be8b914dab7e63086c` = Amendment 1's registered md5 (`PREREGISTRATION.md:631`), blob `c3b815a4…` at HEAD.

**Registered invocation, run from disk:** `python3 d7fr_grade.py --base <run root> --work <run root>/X --cl-target <run root>/X/d7_cl_target.json --arms P1,X,ACC,F-S,F-P --fd-shipped <run root>/F-S/d7_fd_endpoint.json --fd-patched <run root>/F-P/d7_fd_endpoint.json --out <run root>/d7fr_grade_ITEM_20260826T170644Z.json` → `D7FR_GRADER OK verdict=PASS`, exit 0. **Grade JSON: `/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/d7fr_grade_ITEM_20260826T170644Z.json`** (md5 `94ed4755ef9de9db7c48e7285798047a`). The caps assertion read 15 values from §7, all agreeing. (A first invocation with relative `--work X` was REFUSED by G1 on `age_datum_absent X/.d7_age_datum` — the grader resolves `--work` against the cwd, not `--base`; re-issued with absolute paths. The refusal is the guard working; recorded, not a defect of the arm.) The previous lane's `d7fr_grade_FINAL.json` (16:45Z) in the run root carries the same numbers; this file is the record.

**Disclosed before the numbers:** the worktree copy of `PREREGISTRATION.md` in this case directory is 91 lines BEHIND HEAD (a strict prefix — Addenda 2–4 are at HEAD only); the grader read its §7 caps from that copy, which is byte-identical to HEAD's §7. Every citation above is to the HEAD blob. Not repaired by this lane (rule 10: inspected, not reverted; the shared index is the chief's).

---

## 1. SPEND

**Estimate versus actual at process completion (rule 12).** `cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED; every dollar figure DERIVED.

| arm | row | predicted (§7) | actual core-min | source of wall | ratio | cap / ceiling | crossing |
|---|---|---|---|---|---|---|---|
| `P1` | SHIPPED | 0.75 | **0.667** (10 s × 4) | `ledger.txt` | 0.889 | 8.0 / 32.0 | none |
| `X` | SHIPPED | 2.0 (a registered guess) | **0.733** (11 s × 4) | `ledger.txt` | 0.367 | 15.0 / 60.0 | none |
| `ACC` | SHIPPED | 25.0 | **2.067** (31 s × 4) | `ledger.txt` (C-122) | 0.083 | 60.0 / 240.0 | none |
| `F-S` | SHIPPED | 485.0 | **72.667** (1090 s × 4) | `ledger.txt` (C-125) | 0.150 | 750.0 / 3000.0 | none |
| `F-P` | **PATCHED** | 485.0 | **73.4** (1101 s × 4) | `ledger.txt` row written by the launcher from `docker inspect` at 16:43:28Z (`F-P_chain_inspect.txt`) | 0.151 | 750.0 / 3000.0 | none |
| **ITEM** | | **997.75** | **149.534** | grader G10 `total_actual_core_min` | **0.1499** | ceiling sum 6332.0 | **0 overruns** (`LIMB2_REPORTED_NOT_GATING__CARRY_INTO_HEADLINE`: `n_overruns 0`) |

**Dollars, DERIVED:** F-P $0.0628; item **$0.1279** (predicted $0.8531). **Waste: none** — 0.0 core-min, every arm `rc=0`, no row over 3600 wall s, no re-fire, no refused-after-staging arm. (D7F's `P1` 0.733 core-min WASTE is carried RECORDED-NOT-IMPORTED per §7 and is not this item's.)

**Why 0.15, attributed:** misprediction, the mechanism §7 itself registered — a primal priced at 20.27 core-min from D7R arm `O`'s 932.5/46 evaluations, which *"necessarily OVERSTATES a primal"* because it bills the adjoints to it; measured, 22 primals + colouring + one `compute_totals` ran in ~1100 s on both images, ≈ 3.3 core-min per primal. Contention present, not limiting: `delivered_cores_mean` 3.9894 (F-S) and 3.9887 (F-P) of 4. Next estimate for an endpoint-FD arm on this mesh: ≈ 3.5 core-min per primal + 24 colouring + 45 adjoint ≈ **150 core-min per row**, not 485.

**F-P core-min from `docker inspect StartedAt/FinishedAt × 4` cannot be re-read at grading time:** the launcher removes the container after its bookkeeping (`d7fr_run_arm.sh:593`, after the inspect at `:5xx` and the ledger row at `:607`); `docker inspect d7fr_F_P_20260826T162511Z_139564` now returns *no such object*. The surviving kernel-derived record is the ledger row's `wall_s=1101` (computed by the launcher from that inspect) and `F-P_chain_inspect.txt` `inspect=[false 0 false]`. STATUS.F-P's `launcher_wall_s=1165` includes staging and is NOT the container wall.

**Memory, named:** F-S `memavail_min_during` **16.315 GiB** against the 16.0 floor (approached, not crossed; C-125). **F-P `memavail_min_during` 15.725 GiB (n=73) — 2 of 73 samples BELOW the 16.0 floor, by 0.275 GiB, during the run.** H5 (a launch-window gate, 45/60 s) PASSED before F-P fired; the floor is a launch gate, not a run gate, so this is REPORTED, gates nothing, and no OOM occurred (`inspect(exit,oomkilled)=[0 false]`). Peers at the time: `d12y_S3b_*` (W2R, 8 g, cpu 12). Host: kernel `7.0.0-1011-aws` since the 15:19Z reboot; image digests unchanged.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/ledger.txt`; `STATUS.ACC`, `STATUS.F-S`, `STATUS.F-P`; `F-P_20260826T162511Z_139564.mem.jsonl`; `d7fr_grade_ITEM_20260826T170644Z.json` G10; `docs/COST_CALIBRATION.md` C-122, C-125 and the two rows landed with this file (F-P; item).

## 2. LADDER POSITIONS

**A3 ONERA M6, curriculum item D7FR (the D7F re-registration): `PASS`, two rows.** This is the first A3 item on which a PATCHED (`dafoam-idwarp-rot:v1`) arm has ever run (README §3's A3 PATCHED row read *"PENDING everywhere"*), and the first curriculum item graded under an explicitly registered two-row composition (Addendum 4 §A4.2). **It is NOT the family's first two-row verdict:** A1, A5 and A6 (N=16) already carry SHIPPED and PATCHED rows graded on the same FD gate (2026-08-21, README §3). Said so because the brief asked for it only if true.

What the item establishes: at D7R arm `O`'s endpoint (corrected to PHYSICAL coordinates by the `D7-DEF-4` repair, `ACC-1` `rel_CD` 6.917e-4), the DAFoam adjoint gradient agrees with central FD inside band D on all five registered components on BOTH images. What it does not establish: anything about D7R's optimisation (§4 — G2/G3/G4 reported, not gated), or about any component outside the registered five.

Source: `PREREGISTRATION.md` §0.1, §4, §8 (HEAD blob `faeda019`); `docs/dafoam/README.md` §3.

## 3. GATES

**Per-row verdicts (Addendum 4 §A4.2 item 2), and the item verdict (item 3):**

| row | arm / image / `libidwarp.so` md5 | G5 (band D 5.0 %/component, band E aggregate) | G6 planted zero | G6b blind reader | G7 count control | **row verdict** |
|---|---|---|---|---|---|---|
| **SHIPPED** | `F-S` / `dafoam/opt-packages:latest` `9d45679d…` / `f0fcb488e0e98156575cd19548e91663` | **PASS** 5 of 5, worst 1.9589 %, sign flips 0 | PASS (plant 1.234e-3 seen: −0.123079 → −0.121845) | PASS (refused the absent path) | PASS (4 of 4 mutations refused, each named) | **`PASS`** |
| **PATCHED** | `F-P` / `dafoam-idwarp-rot:v1` `2927768a…` / `85f59e87253e0a71a813f64ca6e4c425` | **PASS** 5 of 5, worst 1.9589 %, sign flips 0 | PASS (same plant, seen) | PASS | PASS | **`PASS`** |
| **ITEM** | both rows graded; G9 two distinct `.so` md5s **True** | | | | | **`PASS`** — the worse of two `PASS` rows |

**G5 two-row table** (adjoint `J_adj` vs central FD at the plateau, `step_lo/step_hi` = 0.003/0.01, `eta` 4.891e-8 not floored):

| component | `J_adj` | SHIPPED rel err % | band D / E | PATCHED rel err % | band D / E | sign flips | **divergence SHIPPED − PATCHED** |
|---|---|---|---|---|---|---|---|
| `shape[115]` | −1.2316476e-01 | **0.0697** | PASS / PASS | **0.0697** | PASS / PASS | 0 / 0 | **0.0000 %** |
| `twist[1]` | 1.1547710e-03 | **1.9589** | PASS / PASS | **1.9589** | PASS / PASS | 0 / 0 | **0.0000 %** |
| `patchV[1]` | 4.9753291e-03 | **0.6271** | PASS / PASS | **0.6271** | PASS / PASS | 0 / 0 | **0.0000 %** |
| `shape[0]` | −4.7810581e-03 | **0.7071** | PASS / PASS | **0.7071** | PASS / PASS | 0 / 0 | **0.0000 %** |
| `shape[119]` | −2.1681982e-02 | **0.1459** | PASS / PASS | **0.1459** | PASS / PASS | 0 / 0 | **0.0000 %** |
| aggregate worst | | **1.9589** | PASS | **1.9589** | PASS | **0** | **0.0000 %** |

**G9 — the registered finding, with its number (Addendum 4 §A4.2 item 3; §8's two-row rule):** the two rows are **distinct by toolchain** (`.so` md5s `f0fcb488…` ≠ `85f59e87…`, digests `9d45679d…` ≠ `2927768a…`, G9 `PASS`, prediction C6 HIT) **and identical by result: the shipped-vs-patched divergence is 0.000 % on every one of the five components, and the two FD artefacts are byte-identical (`F-S/d7_fd_endpoint.json` and `F-P/d7_fd_endpoint.json` both md5 `e284d9252854dc9584c3b3324c3f2a93`).** That F-P computed its own table and did not inherit F-S's is on the record: 23 `End` lines in each arm log; per-primal `wall_s` differ in every `d7_fd_endpoint.jsonl` row (baseline 18.951 vs 20.035 s; `compute_totals` 648.35 vs 648.636 s); adjoint `PetscConvergedReason: 2` at 968 iterations in 683.42 s (F-S) vs 687.02 s (F-P); `F-P/.d7_age_datum` 16:25Z and every produced artefact newer. The grader's `finding` field is `null` because both row VERDICTS agree; the divergence NUMBER is reported here as §5 of the pre-registration requires. **Reading, bounded to what was measured:** at this endpoint and for these five components the patched IDWarp rotation code path produces a deformed mesh, primal and adjoint that agree with the shipped image's to every printed digit — the rotation defect the A1/A5 rows measured does not reach the D7R endpoint's registered components. It is NOT a statement about other components, other design points or the D4 wing.

**Hard gates (Addendum 4 §A4.2 item 1):**

| gate | reading | verdict |
|---|---|---|
| **G1** completion + age guard | 5 of 5 arms `rc=0` from ledger rows (`_source rc: ledger_row`), inspect `[0 false]` each; kinds read from the launcher `{P1: DECOMPOSE, X: PYTHON, ACC/F-S/F-P: SOLVER}`; DECOMPOSE evidence `d7_decomp_A/B.json` present, PYTHON `d7_endpoint_dvs_PHYSICAL.json` present, SOLVER `End` line present ×3; markers `OK` ×5. **Age guard: 2 artefacts age-checked and newer (`d7_endpoint_dvs.json`, `d7_major_history.json`, mtime 1787719606 > datum 1787719601); `OptView.hst` and `opt_IPOPT.txt` `STAGED_INPUT_EXEMPT` — the H4 md5-bound exemption (Addendum 3): md5 `ed90aa4f…` and `175969fb…` verified against `D7FR_H4_PASS arm=X` in `X_attempt.log`, mtime 1787711453 (D7R's, older than the datum, as H4 requires).** Named in the verdict line as a limitation. | **PASS** |
| **G8** decomposition determinism | maps A and B identical, `[10635, 10506, 10538, 10441]`, sum 42,120 = registered | **PASS** |
| **G11** OOMKilled | 5 of 5 arms `oom_killed false`, source ledger row, `n_arms_not_measured 0` | **PASS** |
| **G13** adjoint health, band F, **in-item** (Addendum 3) | F-S reason 2 (968 it), F-P reason 2 (968 it); 0 non-positive, 0 `−9` | **PASS** |
| **G9** two rows distinct | see above | **PASS** |

**Reported, not gated (Addendum 4 §A4.2 item 4), §4 verbatim in the JSON:** G2 CL band A `pass False`; G3 `converged False`, `EXIT: Maximum Number of Iterations Exceeded.`; G4 drag reduction **30.402283 %** against [3, 25] — D7R arm `O`'s numbers, *"REPORTED AND NOT GATED. No gate in this item reads it, and no verdict of this item may be stated in terms of it."*

**Infrastructure and placement (L-342 limitation line, every `NOT_MEASURED` limb named):** G10 limb 1 `PASS` (enforced cap == registered cap on 5 of 5 arms); limb 2 `0` overruns. **G12:** MPI arms delivered 3.7267 (ACC) / 3.9894 (F-S) / 3.9887 (F-P) of 4 against floor 3.0, affinity inside cpuset `2,3,4,6`, 4 distinct single cores each — PASS on every MPI arm; **`G12 arm P1: delivered_cores_mean NOT_MEASURED`; `G12 arm X: delivered_cores_mean NOT_MEASURED`** (non-MPI arms the launcher never sampled) — named, non-voiding; G12's composite `pass False` is these two limbs and nothing else. G11: no `NOT_MEASURED` limb.

**Verdict line as the grader composed it:** `PASS` — *"SHIPPED row PASS; PATCHED row PASS; G9 two distinct IDWarp .so md5s: True; LIMITATIONS (L-342, infrastructure NOT_MEASURED): G12 arm P1: delivered_cores_mean NOT_MEASURED; G12 arm X: delivered_cores_mean NOT_MEASURED; G1 age guard: staged inputs opt_IPOPT.txt,OptView.hst EXEMPT by H4 record (Addendum 3)".*

**The pre-repair verdicts, written beside (§2d.1 condition 4):** under the D7-port composition kept as `_map_verdict_core_D7PORT` and written into this grade as `pre_addendum4_composition_D7PORT`: **`NOT A RESULT`** — *"cap-stop AND a frozen band did not hold; band C pass=False; band A pass=False"* (D7R arm `O`'s optimisation bands, which §4 says no gate of this item reads). Earlier pre-repair files: `d7fr_grade_FS_interim.json` (Addendum 2 blob: `NOT A RESULT` on G1 age guard + G13 absent arm `O`), `d7fr_grade_FS_a3.json` (Addendum 3 blob: `NOT A RESULT` on the D7-port composition). Three grader defects were found post-compute and repaired by addenda that moved no band, threshold, cap or label; RESULTS says so in those words.

**Predictions (§11), scored HIT/MISS, cited not re-derived:**

| id | registered | measured | score | cited from |
|---|---|---|---|---|
| C1 | `patchV[0]` driver-scaled reads `29.160000000000004` | `29.160000000000004` from the FINAL history | **HIT** | `RESULTS_P1_X.md` §3 |
| C2 | descales to `291.6` inside 1e-12 | `291.6`, residual 0 | **HIT** | `RESULTS_P1_X.md` §3 |
| C3 | CONTROL B finds `shape` components outside [−1, 1] | **0 of 120 outside**, range [−0.2996, +0.2996] | **MISS (REFUTED)** | `RESULTS_P1_X.md` §3.1 |
| C4 | ACC-1 inside 1e-3 | 6.917e-4 | **HIT** | `RESULTS_ACC.md` |
| C5 | G5 passes band D on ≥ 4 of 5; `shape[115]` registered unlikely-to-be-clean | **5 of 5** on both rows; `shape[115]` 0.0697 % — the registered caveat did not fire | **HIT** | this file §3, grade JSON G5 |
| C6 | F-S and F-P return DISTINCT `.so` md5s and G9 passes for the first time on A3 | `f0fcb488…` vs `85f59e87…`, G9 `PASS` | **HIT** | grade JSON G9 |

5 HIT, 1 MISS.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/d7fr_grade_ITEM_20260826T170644Z.json`; `RESULTS_P1_X.md`; `RESULTS_ACC.md`; `RESULTS_FS.md`; `PREREGISTRATION.md` §5, §11, Addenda 3–4 at HEAD.

## 4. FD TABLES

The G5 two-row table is in §3 above. Raw rows, both images (values identical to every printed digit):

| tag | CD | CL |
|---|---|---|
| baseline | 0.02303298929962691 | 0.28773136683076117 |
| baseline_repeat | 0.023033038211497908 | 0.28773152914410577 |
| `shape[115]` +0.003 / −0.003 | 0.022671051243681017 / 0.02340952510169736 | 0.28034429769380753 / 0.295070552045714 |
| `shape[115]` +0.01 / −0.01 | 0.021882106618030722 / 0.024344828120384382 | 0.2629623023080574 / 0.3119564703909544 |

The other 16 primal rows are in `F-S/d7_fd_endpoint.jsonl` and `F-P/d7_fd_endpoint.jsonl` (they differ only in `wall_s`). Plateau trips 5 of 5 per row; `n_excluded` 0.

Source: `/home/ubuntu/certonomous-runs/CURRICULUM-D7FR-a3-m6-fd/F-S/d7_fd_endpoint.json`, `F-P/d7_fd_endpoint.json` (both md5 `e284d9252854dc9584c3b3324c3f2a93`), `*/d7_fd_endpoint.jsonl`.

## 5. REFILLED QUEUE

nothing

Source: `verification/queue/dafoam/` — this item's entries `D7FR_F-S`, `D7FR_F-P` sit in `launched/` (fired by the chain, never the runner); no new entry from this item.

## 6. WAITING LIST

- The worktree `PREREGISTRATION.md` copy is 91 lines behind HEAD (strict prefix); the chief's index, not this lane's.
- The `F-P` in-run `MemAvailable` floor crossing (15.725 < 16.0, 2 of 73 samples) is a host-load observation for whoever registers the next 12 g arm beside W2R's 8 g stages: the aggregate rule (25.23 < 30.6 at launch) held and the floor still dipped.
- `docs/dafoam/README.md` §3: the A3 PATCHED "PENDING everywhere" row is superseded by the D7FR rows landed with this file.

Source: this file; `docs/dafoam/README.md` §3.
