# Curriculum D5 — FFD parametrisation study on D4's problem: three FFD densities, same everything else

**Item id:** `D5` (dafoam curriculum, `cases/dafoam/EXPERTISE_CURRICULUM.md:95`).
**Version 1.0 — FROZEN 2026-08-26 by dafoam `lab-lane` Q1 for `dafoam-supervisor`** under Sanaa's
queue-first order (`7def3c6b`, `73eccb1b`) and the supervisor's UPDATE F / UPDATE J dispositions
(`[lab-attributed]`). **Committed BEFORE any container starts** (`CLAUDE.md` rule 2). The freeze
sha is the commit that introduces this file; it is named in `verification/queue/dafoam/D5_chain.json`
(`prereg_commit`) and on the board, and `scripts/queue_entry_check.py` verifies this file exists at it.
Supersedes `PREREGISTRATION_DRAFT.md` v0.1 (`f8cf4700`), removed from the tree in the same commit.
**Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7; `DAFOAM_CHARTER.md` §10).
**No frozen file is edited** (rule 6): D4's and D4-SHIPPED's instruments are cited by path and
copied, never modified. Permission for detached launches: **`bc0e687e`** (Sanaa's words, boarded verbatim).

> **ID-NAMESPACE WARNING, carried in the header of every new document in this family.**
> `docs/DOCKET.md:129,130,139,140` carries rows numbered **D5, D6, D14, D15** — fleet SDK/docs defects
> from the 2026-08-11 B2/B6 audits, entirely different objects from the dafoam curriculum items of the
> same number at `cases/dafoam/EXPERTISE_CURRICULUM.md:95,96,125,126`. `docs/DOCKET.md:211` records
> this collision biting twice. **No document in this family cites a bare `D<n>` without saying which.**
> Every `D5`/`D6`/`D14` in this file is the **curriculum** item.

Short form: everything not stated here is **inherited verbatim** from `curriculum_D4/PREREGISTRATION.md`
§1, §4–§10 (case, mesh, bands A–D, the step ladder, plateau rule, decomposition) and from the
**D4-SHIPPED Addendum-2 launcher family frozen at `8b91be2b`** (`curriculum_D4_SHIPPED/d4s_run_arm.sh`
md5 `51987c2f5c583bc910ffe0f4415b09f5`, `d4s_chain_driver.sh`,
`d4s_aggregate_memory.py`, `d4s_groot5_selftest.sh`). Where a number here disagrees with a cited
source, **the cited source wins and this document is defective.**

---

## 1. What changes, and only this

| | D4 (PATCHED row, `GATE REACHED`, C-97) | D5 |
|---|---|---|
| case, mesh, np, decomposition | A2 wing, 38,304 cells, np=4 `scotch` | **identical** |
| toolchain row | PATCHED `dafoam-idwarp-rot:v1`, digest `sha256:2927768a…dee30f6d35`, `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425` | **identical — PATCHED ONLY**, the row D4 was graded on. The launcher's `G-ROW` refuses SHIPPED. The two-row rule names the SHIPPED row **unbought** here (§6). |
| FFD box | `FFD/wingFFD.xyz` 6×2×8 → 96 local `shape` DVs | **three densities: 4×2×6 (48 DVs), 6×2×8 (96 — D4's own), 8×2×12 (192 DVs)**, same bounding box, same `wingAxis` at `xFraction=0.25`, same twist (7) and `patchV` DVs |
| objective / constraints / optimiser | CD at CL=0.5, IPOPT `max_iter` 100 | **identical**; `d5_opt_runScript.py` = `d4_opt_runScript.py` (md5 `2906d52a…`) with **ONE registered delta**: the FFD path is an argument `-ffd` defaulting to `FFD/wingFFD.xyz` (2 hunks, 3 lines; `diff` reproduced in §7) |
| FD instrument | `d4_fd_endpoint.py` (md5 `c6112b0e…`), refuses any producer but `d4_opt_runScript.py` by md5 | `d5_fd_endpoint.py`: D4's bytes with PRODUCER/PRODUCER_MD5 re-pointed at `d5_opt_runScript.py` and OUT/JSONL renamed `d5_fd_endpoint.*`; step ladder, clearance rule, five COMPONENTS unchanged |
| launcher family | `d4s_run_arm.sh` @ `8b91be2b` | `d5_run_arm.sh`, `d5_chain_driver.sh`, `d5_aggregate_memory.py`, `d5_groot5_selftest.sh` — derived copies, **byte-for-byte except the registered deltas of §7** |

**The 6×2×8 density is NOT re-bought.** D4's PATCHED `O/` artefacts (`GATE REACHED`, 80 majors,
`EXIT: Optimal Solution Found.`, `CD_f = 2.1125978108239574e-02`) are **consumed as density 96**,
read-only. They are **recorded, not imported**: `d5_grade.py` re-reads
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` from disk, re-derives
`CD_f(96)`, **refuses if it differs from the recorded value** (the file changed), and carries a
planted-zero control on that reader (§3).

### 1a. The FFD generator, and a corrected claim

`d5_gen_ffd.py` (md5 `546ba7641e15d61d8a55d3a2072843a7`) reads D4's box, checks it is a uniform
ny=2 Plot3D family (x uniform in i, y symmetric, z constant per plane), and regenerates any (nx, 2, nz).
**The draft claimed the 6×2×8 output "must be byte-identical" to D4's file. That claim is corrected
here before compute, by measurement:** the reference carries 8 decimals and `linspace` over the rounded
endpoints differs from the original unrounded arithmetic by exactly **1.0e-8 on 6 of 51 lines**.
The generator's **planted control 1** is therefore *precision identity*: regenerated 6×2×8 equals the
reference at every value to **≤ 1.0e-8 (one unit of the file's last printed digit)**; measured
`regen_max_abs_diff=1.000e-08`. **Planted control 2**: a 1e-6 perturbation of the y-half-height must
NOT pass — measured `planted_perturbation_max_diff=5.000e-07 seen=yes`. Both controls ran on 2026-08-26
17:0xZ from the host (`numpy`), output reproduced in §8. **No 96-point box is staged by this item** —
density 96 is D4's own file, consumed; `ffd/wingFFD_96_D4_REFERENCE.xyz` is a byte copy of
`…/CURRICULUM-D4-a2-wing-cdmin/base/FFD/wingFFD.xyz` (md5 `f9435ee2ef54df0b08feae6e5127125d`), kept
for the reader.

| box | file | md5 (frozen) | shape DVs |
|---|---|---|---|
| 4×2×6 | `ffd/wingFFD_48.xyz` | `85a8bcd5d39f1b11a612ac0a39aee776` | 48 |
| 8×2×12 | `ffd/wingFFD_192.xyz` | `8eb161df4c546d10d7fcb30132f58907` | 192 |
| 6×2×8 (D4's, consumed) | D4 run root `base/FFD/wingFFD.xyz` | `f9435ee2ef54df0b08feae6e5127125d` | 96 |

Regeneration from the generator on 2026-08-26 reproduced the 48 and 192 files **byte-for-byte**
(`cmp` silent, md5 equal). The launcher md5-asserts the density's box before staging it over
`FFD/wingFFD.xyz` in the arm directory (`D5_FFD_STAGED` line).

## 2. Arms — six, in this order, one detached chain

| arm | kind (G1) | density | task | work dir | container mem | new compute |
|---|---|---|---|---|---|---|
| O48 | SOLVER | 4×2×6 | IPOPT `run_driver`, `max_iter` 100 | `O48/` (cold copy of `base/`) | 12g | yes |
| ACC48 | SCRIPT | 4×2×6 | `compute_totals` on a cold staged copy — the D4-SHIPPED ACC shape; the artefact is the log | `ACC48/` | 8g | yes |
| F48 | SOLVER | 4×2×6 | `d4_extract_endpoint.py` then `d5_fd_endpoint.py`: endpoint FD table, five registered components | `O48/` (F runs in the O directory, the frozen F3 path) | 12g | yes |
| O192 | SOLVER | 8×2×12 | as O48 | `O192/` | 12g | yes |
| ACC192 | SCRIPT | 8×2×12 | as ACC48 | `ACC192/` | 8g | yes |
| F192 | SOLVER | 8×2×12 | as F48 | `O192/` | 12g | yes |
| (O96) | — | 6×2×8 | D4 PATCHED `O/` consumed, read-only | D4 run root | — | **no** |

Chain: `d5_chain_driver.sh O48 ACC48 F48 O192 ACC192 F192`, stops at the first non-zero rc. Arm kinds are
registered here and in `d5_grade.py:ARM_KIND`; an arm outside the table refuses.

Arm commands (the launcher's `case`, verbatim): O — `mpirun --allow-run-as-root -np 4 --bind-to core
--report-bindings -x PYTHONPATH python d5_opt_runScript.py -task run_driver -optimizer IPOPT`; ACC — the
same with `-task compute_totals`; F — `python d4_extract_endpoint.py && mpirun … python d5_fd_endpoint.py`.
Each is written to `<arm>/d5_cmd.sh` and executed **inside the container under `timeout -k 60 <cap wall>`**.

## 3. Gates — registered before compute

All bands below are frozen now. `d5_grade.py` (md5 in §7) is the grading path; the verdict vocabulary is
`PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

* **G1 — completion, ARM-KIND AWARE (from birth; the D4-SHIPPED Addendum-2b form ruled in UPDATE F).**
  SOLVER arms: kernel `rc == 0` read from `docker inspect .State.ExitCode` (the ledger row's
  `inspect(exit,oomkilled)`, refusing on a harness/kernel disagreement), `OOMKilled false`, the
  **positional** terminal statement `Finalising parallel run` as the **last non-empty line** of the
  producer's own log, and the age guard: registered artefacts (`O*/opt_IPOPT.txt`, `O*/OptView.hst`;
  `O*/d5_fd_endpoint.json`, `O*/d4_endpoint_dvs.json` for F) strictly newer than the arm's
  `.d4_age_datum` (`0/U`, touched last at stage). SCRIPT arms (ACC48, ACC192): kernel `rc == 0`,
  the launcher's `.ok` marker, and the registered artefact — the log itself, since `compute_totals`
  writes no file — newer than the arm's datum; the terminal statement is **reported, not composed**.
  Any clause failing on any required arm → item `NOT A RESULT`.
* **L-342 field classes (Sanaa `d4d0c29d`).** `FIELDS_PHYSICS` = rc, inspect_exit, oomkilled,
  terminal_statement, age_guard, wall_s, core_min, cap_core_min, enforced_core_min, DIGEST, cpuset.
  `FIELDS_INFRASTRUCTURE` = memavail_pre/post, delivered, siblings_pre/post, cpu_series, log.
  **Absent infrastructure → `NOT_MEASURED`, named in the verdict line, never composed to PASS.
  Present-but-garbage → REFUSE. Absent physics → REFUSE.** An arm with no ledger row is read from the
  **kernel record** of its container (`d5_<ARM>_<stamp>`, no `--rm`; exactly one candidate), sources
  named per field, infrastructure `NOT_MEASURED`.
* **G-D5-1 — the cross-density metric.** `ΔCD(d) = CD_f(d) − CD_f(96)` for d ∈ {48, 192}, each
  `CD_f` read from that density's `opt_IPOPT.txt` final unscaled objective by the grader, never from the
  runScript's print. **Band: |ΔCD(192)| ≤ 3.0e-4** (1.4 % of CD_f(96); ≈ 9× D4's measured F3 aggregate
  FD error 0.1634 %, so the band sits above the verifiable resolution) → `PASS`, else `GATE FAIL`.
  **ΔCD(48) carries NO band** — sign only (P2). **Planted-zero control (rule 3):** the reader is driven
  on a copy of D4's `opt_IPOPT.txt` with the objective moved by `PLANT = 1.234e-03` and must read back
  exactly the plant (|seen − plant| < 1e-12) and read an unperturbed copy unchanged, else the grade
  **refuses**; the control files land in `<run root>/grader_controls/`.
* **G-D5-P — the "optimiser exploits the parametrisation" pathology, named in advance.** A density
  whose F table has **≥ 2 sign flips** among the five registered components is `NOT A RESULT` for that
  density, and its `CD_f` is quoted only beside that label; if density 192 carries it, G-D5-1 is
  `NOT A RESULT`. Rule 5 has no row (no grid family): **no GCI is quoted anywhere in D5.**
* **G5d — per-density bright line** (D4 band D by citation): per component |d(s_hi) − J_adj|/|d(s_hi)|
  ≤ 5 %, no sign flip, plateau |d(s_hi) − d(s_lo)|/|d(s_hi)| ≤ 10 % (else that component
  `NOT A RESULT`); aggregate vector-relative error over planned components ≤ 5 %. `NEAR_ZERO` /
  `ABSENT` / failed-FD components are `NOT A RESULT` for that component (D4 §6a).
* **The five components, NAMED IN ADVANCE, BY NAME, for BOTH densities:** `shape[46]`, `shape[18]`,
  `shape[0]`, `twist[0]`, `patchV[1]` — D4's five. **Registered consequence:** in a 48- or 192-point
  box the same index names a **different control point** than in D4's 96-point box; the names are kept
  because they are what D4 §6 registered and the instrument is D4's bytes, and the grader refuses an FD
  file whose `components_requested` is not this list. `shape[46]` in the 4×2×6 box (48 DVs, indices
  0–47) exists; it is not the idx46-class near-zero point of the 96 box and is not predicted to be.
* **G9 — toolchain:** every ledger row carries the PATCHED digest and every log the PATCHED
  `libidwarp.so` md5 on the `D4S_IDWARP_SO_MD5:` line (the string the inherited launcher prints,
  unchanged by design so the grader greps what the container writes).
* **G10 — caps** (§4): every row `core_min ≤ cap`, sum ≤ 1,860.0; a crossing is `GATE FAIL` exactly
  as the frozen text says, with the mode of §4 beside it.
* **G12 — placement:** `cpuset == 8,10,11,13` on every row; delivered cores ≥ 3.0 of 4 where
  measured, `NOT_MEASURED` disclosed otherwise.
* **Item verdict composition** (`d5_grade.py:compose`): `NOT A RESULT` if G1 fails or density 192
  carries G-D5-P; else `GATE FAIL` if any of G-D5-1, G9, G10, G12 fails; else `PASS`.
  `NOT_MEASURED` fields are printed **beside** the verdict, never inside it.

## 4. Cost — measured-derived from D4's own rows; committed before compute

| arm | anchor | prediction (core-min) | cap (core-min) | cap wall inside container | mem |
|---|---|---|---|---|---|
| O48 | 6.389 core-min/major (D4 PATCHED, 511.133/80, `curriculum_D4/RESULTS.md` §cost) × 100 majors | **638.9** | 800.0 | 12,000 s | 12g |
| O192 | same anchor; the adjoint solve is DV-independent, the `dRdX`/FFD products are not — **exposure stated: the anchor may under-price 192 DVs** | **638.9** | 800.0 | 12,000 s | 12g |
| ACC48 + ACC192 | 3.000 each (D4 ACC, C-94) | **6.0** | 10.0 each | 150 s each | 8g |
| F48 + F192 | 47.267 each (D4 F3, C-96; five components regardless of density) | **94.5** | 120.0 each | 1,800 s each | 12g |
| comparator / grader | zero compute | 0 | — | — | — |
| **total** | | **1,378.3 core-min** | **ceiling 1,860.0** (sum of caps = `ITEM_CEILING_CORE_MIN`) | | |

* **ranks 4**; wall **5.74 h** at the estimate, **7.75 h** at the ceiling.
* **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot
  read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED, NOT MEASURED**:
  estimate **$1.18** (1,378.3/60 × 0.0513 = 1.178), ceiling **$1.59**.
* **Below the curriculum's 1,500–2,250 because density 96 is not re-bought**, not because anything is cheaper.
* **Cap mode, registered:** each arm's wall deadline is **inside the container** (`timeout -k 60` at
  cap × 60 / 4 s; the launcher asserts the enforced wall equals the registered cap to 0.02 core-min and
  aborts otherwise). The host poller additionally **reports** a crossing to the ledger
  (`D5…CAP_CROSSED`, run continues) and hard-stops at 4× cap — the inherited D4-SHIPPED
  report-then-stop mode (Sanaa 2026-08-25). **The in-container deadline is the cap that survives shell
  death**; the 4× ceiling is reachable only if the in-container `timeout` fails, and is kept as the
  second barrier. A calibration row is owed at completion in `docs/COST_CALIBRATION.md` (rule 12).
* **Memory:** `H5` windowed gate — 45 samples over 60 s, **refuse on ANY sample < 16.0 GiB**;
  **aggregate** (live container caps + this arm's cap + host non-container RSS) **< 30.6 GiB** in the
  **wait-and-retry** form (poll 30 s, bound 4 h, every wait a line in `STATUS.<arm>`, refuse-and-BLOCK
  at the bound with the series file named) — the UPDATE F ruling for D4-SHIPPED, adopted from birth.

## 5. Predictions — scored HIT/MISS afterwards, never adjusted

| # | prediction | band / number |
|---|---|---|
| P1 | both new densities print `EXIT: Optimal Solution Found.` within `max_iter` 100 | majors in **[60, 100]** each |
| P2 | the coarser box is worse: `ΔCD(48) > 0` | sign only; `NOT A RESULT` if 48 carries G-D5-P |
| P3 | the finer box gains little: `ΔCD(192) ∈ [−3.0e-4, 0]` | **point −1.0e-4** |
| P4 | O48 costs **[450, 700]** core-min, point 638.9; O192 **[550, 850]**, point 638.9 | the asymmetric band states the 192-DV exposure |
| P5 | F48 and F192 each ≤ 1 sign flip among the five, aggregate vector-relative error < 5 % | D4's band |

## 5b. Placement, memory and the detached form — registered by measurement at freeze

* **cpuset `8,10,11,13`** (`--cpuset-cpus`, four distinct cores, `--cpus=4`). Measured at 17:01Z–17:16Z
  2026-08-26 by `sudo -n docker inspect` on every running container: **one live container,
  `d12y_S3b…` (W2R) on `12`**, 8 GiB. Registered-and-re-firable sets held clear: D4-SHIPPED
  `5,6,7,9` (its chain stopped `rc=137` on ACC at 16:56:28Z and may be re-fired by its own lane),
  D7FR `2,3,4,6` (F-S and F-P complete, no arm outstanding). D6 (curriculum) is registered on
  `2,3,4,14`. **8,10,11,13 is disjoint from all of them.** Native host processes float on 0–15 and are
  the runner's business (busy-core ceiling), not a cpuset collision.
* **Delivered cores are measured**, not inferred (cgroup `cpu.stat` sampler → `<arm>_<stamp>.cpu.jsonl`);
  an absent sample file reads `NOT_MEASURED`.
* **The detached form.** The queue runner launches `bash d5_chain_driver.sh …` under its own
  `setsid nohup`; the driver writes its pid to `<run root>/d5_driver.pid` (G-ROOT.5 b), opens
  `STATUS.<arm>` at preflight and appends every wait and the final `rc=<n> … source=launcher_exit=docker_inspect_ExitCode`
  line **inside the detached session** — never the `$?` of a `setsid`/`timeout` line (0 for every
  outcome, measured lab-wide). `STATUS.chain` carries the chain state. Container `rc` is read from
  `docker inspect` before `docker rm`; **no `--rm`**.
* **G-ROOT.1–.5 from birth.** `BASE` must equal this item's root through `realpath -m` (G-ROOT.1);
  the forbidden list names **D4's, D4-SHIPPED's, D4-SHIPPED-R's, D7R's, D12R's, D12R2's, D6's and
  D14's** roots (G-ROOT.2); the ledger refuses a foreign `ITEM=` or any `ROW=SHIPPED` row (G-ROOT.3);
  **G-ROOT.5** refuses a RUNNING container carrying `d5_<ARM>_` or a driver pidfile naming a live pid
  that is not an ancestor or whose cwd is the run root — **DEMONSTRATED 2026-08-26T17:15:48Z**
  (`d5_groot5_selftest_evidence.txt`, **12/12**): a sacrificial `sleep` container → `rc=3`; a
  sacrificial live pid with cwd = run root → `rc=3`; a stale pidfile does not block; clear passes and
  the launcher stops at the L-251 mode check before any staging; D4's, D4-SHIPPED's and D6's roots
  refuse at G-ROOT.1; zero backticks on executable lines; the temporary root stayed empty and is
  **absent afterwards**.
* **Run root staging** (driver delta 4): the root **does not exist at freeze**; the first fire creates
  it (mode 777, L-251), copies D4's `base/` read-only from D4's run root, this directory's instruments
  and the two boxes, writes `ITEM=D5 …` as the ledger's first line, and every staged file is
  md5-asserted before any container starts. A second fire stages nothing; an `rc=0` ledger row for an
  arm refuses a re-fire (`ALREADY_BOUGHT`, driver delta 3).

## 6. What this item does NOT claim

Nothing about the SHIPPED row (unbought here; the two-row rule names it unbought in every record).
Nothing at np≠4 or another decomposition. No Strouhal, no grid family, no GCI. The 6×2×8 numbers are
D4's and are cited, never re-derived into a new verdict. Nothing about `shape[46]` being near-zero in
either new box. The multipoint runScript form is D6's, not this item's.

## 7. Instruments, frozen by md5 at this commit

| file | md5 | derivation |
|---|---|---|
| `d5_run_arm.sh` | `b4517d4a8ce1c0d7c3e1df2180f56fb0` | `d4s_run_arm.sh` @ `8b91be2b` (blob md5 `51987c2f5c583bc910ffe0f4415b09f5`) + deltas in `d5_run_arm_DELTAS_from_d4s.diff` (163 diff lines): item/root names; forbidden roots +D4-SHIPPED, +D4-SHIPPED-R, +D6, +D14; G-ROOT.3 refuses `ROW=SHIPPED`; cap table §4; PATCHED-only `G-ROW`; density parsed from the arm name; FFD md5 table and the staged-box replacement; `d5_opt_runScript.py`/`d5_fd_endpoint.py` md5s; F arms run in `O<d>/`; `d5_` container prefix and pidfile; **cpuset 8,10,11,13** |
| `d5_chain_driver.sh` | `ae0ae1df7133684791b0f7c165ac0d81` | `d4s_chain_driver.sh` @ `8b91be2b` (blob md5 `f7b9e125f9058d54a209b859e05e1dcf`) + deltas in `d5_chain_driver_DELTAS_from_d4s.diff` (155 diff lines): names/image/caps/launcher md5; **aggregate wait-and-retry** (UPDATE F); `ALREADY_BOUGHT`; root staging; STATUS opened-and-appended |
| `d5_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | **byte-identical** to `d4s_aggregate_memory.py` @ `8b91be2b` |
| `d5_groot5_selftest.sh` | `32e19fffc33a43efd9959a02dfab5062` | the `d4s_groot5_selftest.sh` pattern against D5's launcher; temporary empty root, `rmdir`, absence asserted; adds (d) G-ROOT.1 refusals |
| `d5_grade.py` | `d50b55f498a0c16367562aa6d09ac380` | **the grading path.** New; the D4-SHIPPED Addendum-2 field classes, kernel-record fallback, positional terminal clause and Addendum-2b arm kinds; G-D5-1/G-D5-P/G5d/G9/G10/G12; 0 `assert` nodes by AST, counter shown to count a planted one |
| `d5_grade_selftest.py` | `3a1b2bd93ab98f7899fe0ae7b084f44e` | **26/26 under `python3` AND `python3 -O`** (`d5_grade_selftest_evidence.txt`): absent infra → `NOT_MEASURED` named; present-garbage → REFUSE; absent physics → REFUSE; clean control PASS; band mutation flips the control; blind reader → REFUSE; D4 reference moved → REFUSE; kernel exit 1 → NOT A RESULT; harness/kernel disagreement → REFUSE; terminal not last → NOT A RESULT; SCRIPT arm without `.ok` → NOT A RESULT; stale artefact → NOT A RESULT; 2 flips → pathology; 1 flip → no pathology; cap crossing → G10 GATE FAIL; wrong digest → G9; wrong cpuset → G12 with delivered `NOT_MEASURED` named; absent `opt_IPOPT.txt` → REFUSE; `NOT_MEASURED` named beside a PASS |
| `d5_fd_endpoint.py` | `91b9f3526a39cb02eafbd5be504d7107` | `d4_fd_endpoint.py` (md5 `c6112b0ec3bfdb5287345e350500f64a`) with PRODUCER/PRODUCER_MD5 → `d5_opt_runScript.py`, OUT/JSONL → `d5_fd_endpoint.*`, header text |
| `d5_opt_runScript.py` | `fa1d91c82d11aacd0ae072652b346952` | `d4_opt_runScript.py` (md5 `2906d52a5dbed2bacbaeaf85a37d3fe8`); `diff` = `+parser.add_argument("-ffd", …, default="FFD/wingFFD.xyz")` and `OM_DVGEOCOMP(file=args.ffd, type="ffd")` |
| `d5_gen_ffd.py` | `546ba7641e15d61d8a55d3a2072843a7` | new; two planted controls (§1a) |
| `ffd/wingFFD_48.xyz`, `ffd/wingFFD_192.xyz` | `85a8bcd5…`, `8eb161df…` | generator output, reproduced byte-for-byte at freeze |
| `d4_extract_endpoint.py` (copied at staging from `curriculum_D4/`) | `ee7d3c99fd716da23779cb651961918e` | D4's, unmodified; writes `d4_endpoint_dvs.json` and `d4_major_history.json` |

**Strings the container prints are inherited unchanged** (`D4S_CONTAINER_UID`, `D4S_IDWARP_SO_MD5`,
`D4S_DEADLINE_IN_CONTAINER_S`, `D4S_G_ROOT5_PASS`, `D4_CAP_ASSERT`, …) so that the grader greps
exactly what the launcher writes — the `D4S-GRADER-DEF-1` string-mismatch class is excluded by not
renaming. **No `assert` carries a guard** in any python file here (AST count 0 on all six; L-332);
`python3 -O d5_aggregate_memory.py 12 30.6` was run and returned a reading (`aggregate_GiB 28.83`,
`ok true` at 17:16Z). **Classifier denials in this lane while building D5: none.** Files were authored
with the harness file-writing tool from the start, one per call, per the supervisor's disposition in
UPDATE D.

## 8. FREEZE

**Condition, and how it was checked (rule 2):** `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density`
→ **false**, executed as the last check of `d5_groot5_selftest.sh` at **2026-08-26T17:15:50Z** and
re-checked by the lane at 17:16Z; `docker ps -a --filter name=d5_` carries no container but the
removed sacrificial one. **This item has burned 0 core-min and started no arm container.**

**Committed BEFORE any container starts.** The grading path is fixed at this commit:
`d5_grade.py` md5 `d50b55f498a0c16367562aa6d09ac380`, to be verified against its committed blob
before grading. **After first compute the gates are closed**; changes land only as dated addenda that
cannot alter a gate, threshold, cap or label; originals are struck, never rewritten.

**Queue entry:** `verification/queue/dafoam/D5_chain.json` — team `dafoam`, `prereg_commit` = this
freeze sha, `launch_cmd` = `bash <abs>/d5_chain_driver.sh O48 ACC48 F48 O192 ACC192 F192`,
`cwd` = this case directory, `ranks 4`, `cost_core_min_estimate 1378.3`, `memory_floor_gb 16.0`,
`permission bc0e687e`. Enqueueing is not authorisation: `SUPERVISION_CHARTER.md` §3 check 4 is the
supervisor's own, discharged at enqueue by verifying the freeze commit is present, and the runner's
sha check is the mechanical second guard.

**Predicted outcome, so it cannot be written afterwards:** P1–P5 as tabled; item `PASS` if P3 holds
and no completion clause fails; the only outcome that is a wasted run is an arm that cannot prove
which row it ran, which `G-ROW` and G9 exist to prevent.
