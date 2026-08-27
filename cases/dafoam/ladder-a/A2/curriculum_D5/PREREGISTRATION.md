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

---

# ADDENDUM 1 — 2026-08-26 — **PRE-COMPUTE** — every arm 12g, never 8g; the capability-grid cell

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.** `CLAUDE.md` rule 2: a
pre-first-compute amendment must state the condition and how it was checked.

**THE CONDITION, AND HOW IT WAS CHECKED.** `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density`
→ **false at 2026-08-26T17:38:53Z**, the final check of `d5_groot5_selftest.sh` re-driven on the amended
launcher (`d5_groot5_selftest_evidence.txt`, **12/12**, temporary root empty throughout and absent after).
No `d5_` container exists but the removed sacrificial one. **0 core-min; no arm has fired.** No gate,
threshold, band or label moves below; one container memory cap moves UP, before compute, for a measured reason.

## A1.1 What moved, and why

**ACC48 and ACC192: container memory cap 8g → 12g.** Every arm of this item now runs at **12g**.
Reason, measured on the sibling item: the D4-SHIPPED ACC arm — the same `compute_totals` shape as ACC48/ACC192 —
was **OOM-killed by its 8g container cgroup, `rc=137` at 16:56:28Z 2026-08-26**
(`/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin/STATUS.ACC`, `STATUS.chain`
`chain=STOPPED_AT_FIRST_NONZERO arm=ACC rc=137`); that lane is registering ACC at 12g as its Addendum 2c.
The supervisor's disposition for D5/D6 `[lab-attributed]`: **no solver-adjacent arm at 8g, ever.**
The `8g` cells in §2 (ACC48, ACC192) and §4 (ACC48 + ACC192 `mem`) are **STRUCK** and read **12g**.
The driver's aggregate check uses 12 GiB for every arm; H5 floor 16.0 GiB (12g + 4 GiB headroom, D4-SHIPPED
§4.4) is unchanged; caps in core-minutes, the ceiling, the cost and every prediction are unchanged.

## A1.2 Instruments re-frozen at this commit

| file | md5 now | md5 at v1.0 | what changed |
|---|---|---|---|
| `d5_run_arm.sh` | `50a976780e357998238ede3bbb8e5521` | `b4517d4a…` | `cap_memory()`: one `case` line (`8g` row removed, ACC arms joined to the `12g` row) + four comment lines |
| `d5_chain_driver.sh` | `47e7767de0312da60cc95a238d7faa00` | `ae0ae1df…` | `MD5_LAUNCHER`; `cap_mem_gib()` returns 12 for every arm; header note |
| `d5_run_arm_DELTAS_from_d4s.diff`, `d5_chain_driver_DELTAS_from_d4s.diff` | regenerated | — | 218 / 158 diff lines against the `8b91be2b` blobs |
| `d5_groot5_selftest_evidence.txt` | re-driven 17:38:52Z | — | 12/12 on the amended launcher |
| `d5_grade.py` | `d50b55f498a0c16367562aa6d09ac380` | unchanged | the grader does not read the memory cap |

## A1.3 Capability-grid cell (`068c2bf0`, Sanaa's taxonomy, stated as ordered)

**Capability-grid cell (068c2bf0): 3D · steady · subsonic-compressible — verdict this item can move:
gradients FD-verified | optimization converged, from "`GATE REACHED`, G5 `PASS` on the PATCHED row,
SHIPPED row `PENDING`" (`curriculum_D4/RESULTS.md`, C-97; D4-SHIPPED F3 ungraded at this commit) to —
honestly — the same verdict: D5 DEEPENS the cell's evidence (FD-verified gradients and converged
optimisations at two further parametrisations, 48 and 192 DVs, on the PATCHED row of the same case)
and does NOT move it; the SHIPPED row stays `PENDING` until D4-SHIPPED grades.**
Regime derived from D4's registered flow conditions, not guessed: `DARhoSimpleFoam` (compressible,
steady), U∞ = 100 m/s, T∞ = 300 K → M∞ = 100/√(1.4·287·300) = **0.288**, Spalart–Allmaras RAS
(`curriculum_D4/d4_opt_runScript.py:24-35`; D4 run root `base/constant/turbulenceProperties`
`RASModel SpalartAllmaras`); the MACH wing is a 3D case (`curriculum_D4/PREREGISTRATION.md` §1).

## A1.4 Classifier denials while landing this addendum — verbatim, twice

*"Permission for this action was denied by the Claude Code auto mode classifier. Reason: Blocked by
classifier."* — (1) on one combined `sed`/`md5sum`/selftest invocation carrying the 8g→12g edit; (2) on
a `bash -n`/`md5sum`/`mkdir` invocation. Neither was reworded and retried; the edits were made with
the harness's file tools, the md5s read with a bare `md5sum`, the selftests run as before.

**The queue entry `verification/queue/dafoam/D5_chain.json` cites the commit that lands this addendum
as `prereg_commit`**, so the sha the runner verifies is the sha at which every md5 above holds.

---

# ADDENDUM 2 — 2026-08-26 — **PRE-COMPUTE** — `D5-DRIVER-DEF-1`: G-ROOT.3 refused the driver's own staging line on the first runner fire

**Version 1.1 → 1.2. Lines whose number changed above this section: 0.** `CLAUDE.md` rule 2, pre-first-compute.

**WHAT HAPPENED, from disk.** `scripts/queue_runner.py` launched `D5_chain.json` at **17:42:43Z**
(`runner.log`: `LAUNCHED team=dafoam case=D5_chain pid=311433 sid=311433 ranks=4 est=1378.3 core-min
prereg=a1dcdb7d`; box 39.8 % busy). The driver (pid 311435, sid 311434) staged the run root (mode 777, base/,
instruments, boxes — every md5 `OK`), passed H5 (45/45, min 26.84 GiB) and the aggregate (22.3 < 30.6, waited
0 s), and called the launcher for O48, which **refused at G-ROOT.3, exit 3, before any staging**:
`ABORT G-ROOT.3 the ledger … carries another item: ITEM=D5 staged=20260826T174243Z base_src=… permission=bc0e687e`
(`O48_launch.out`). `STATUS.O48` last line `rc=3 … source=launcher_exit=docker_inspect_ExitCode`;
`STATUS.chain` `chain=STOPPED_AT_FIRST_NONZERO arm=O48 rc=3`; the runner's `STATUS.D5_chain` `launcher_rc=3`
(an infrastructure record, L-342). **No container started (`docker ps -a` carries no `d5_` name), no `O48/`
exists, no `ARM=` row exists, 0 core-min.**

**THE DEFECT — `D5-DRIVER-DEF-1`, in this lane's own registered delta (4), not in the inherited family.**
The driver wrote the ledger's first line as `ITEM=D5 staged=… permission=…`; the inherited G-ROOT.3 excludes
only an **exact** `ITEM=D5` line (`grep -av "^ITEM=$ITEM$"`), so the staging metadata on the same line made
the item's own identity line read as a foreign item. **The guard did its job on the first line it was ever
shown** — it is the correct instrument and is not changed. The D4-SHIPPED family never wrote an `ITEM=` line;
the line is this item's addition and the defect is this item's.

**THE CORRECTION — driver only; no gate, threshold, cap, label, band, cost or prediction moves.**
`d5_chain_driver.sh` now writes `ITEM=D5` alone on line 1 and the staging metadata on a second line
`STAGED stamp=… base_src=… permission=…` (no `ITEM=` prefix): md5 **`89c9b7e7e43e7dd12d1c551dadfa80c8`**
(was `47e7767d…`; the delta is these two `echo` lines and four comment lines; `d5_chain_driver_DELTAS_from_d4s.diff`
regenerated, 163 diff lines). The launcher is untouched (`50a97678…`). **The already-staged run root is kept**
(re-staging would need the root removed; the staged files are md5-verified copies and nothing in them ran) and
its ledger's first line was corrected by hand to the same two-line form, the second line carrying
`corrected_by=laneQ1_ADDENDUM2` so the hand edit is visible in the record.

**THE CONTROL — the corrected form is shown to pass G-ROOT.3 without staging anything.** At 17:46:08Z the
launcher was invoked on the corrected root with a bogus image (`d5_run_arm.sh O48 no-such-image:selftest`):
`D4S_G_ROOT_PASS item=D5 … ledger_clean=yes`, `D4S_G_ROOT5_PASS … driver_pidfile=absent`, cap assertion,
host pre-read, the three staged-instrument md5s `OK`, then **`ABORT cannot read digest of no-such-image:selftest`,
rc=4 — before the first `rm -rf`/`cp -a`/`docker run`**; `O48/` still absent; `docker ps -a` still carries no
`d5_` name. Output kept in the run root as `ADDENDUM2_groot3_control_<stamp>.out`.

**THE CONDITION, AND HOW IT WAS CHECKED.** The run root **exists** (staged 17:42:43Z by the runner's fire) and
contains `base/`, `ffd/`, the three instruments, `ledger.txt` (two lines, no `ARM=` row), `STATUS.chain`,
`STATUS.O48`, the H5 window and aggregate series files, `O48_launch.out` and the control output —
**and no arm directory, no `.d4_age_datum`, no container record**: `ls O48` → absent, `docker ps -a | grep d5_`
→ 0 lines, checked 17:46:08Z. First compute has not occurred.

**Queue.** The runner moved the fired entry to `launched/D5_chain.json` (`_launch` pid 311433) and will not
re-fire it. A fresh entry **`verification/queue/dafoam/D5_chain_r2.json`** (case_id `D5_chain_r2`, same argv,
same cost 1,378.3, `memory_floor_gb 16.0`) cites **the commit that lands this addendum** as `prereg_commit`.
On the re-fire the driver finds the root present (`D5_ROOT_PRESENT`, stages nothing), asserts the staged
md5s, and proceeds to O48; `STATUS.<arm>` files are re-opened at preflight.

---

# ADDENDUM 3 — 2026-08-26 — **PRE-COMPUTE for the r3 re-fire** — `D5-PREREG-DEF-1`: ACC48 was cut by its own under-registered deadline while still colouring; ACC48/ACC192 caps re-stated from the measured anchor; `CHAIN_DONE` marker registered

**Version 1.2 → 1.3. Lines whose number changed above this section: 0.** Written 2026-08-26T20:54Z by dafoam `lab-lane` Q-A for `dafoam-supervisor` under the supervisor's FOURTEENTH-session triage and ruling (`docs/LAB_STATE.md` `## dafoam` §2, `[lab-attributed]`); permission for detached launches and queue entries `bc0e687e`; L-342 `d4d0c29d`. `CLAUDE.md` rule 2: first compute on this item HAS occurred (O48, ACC48), so this addendum **alters no gate, threshold, band or label**; it moves **two caps** under the supervisor's explicit ruling, states the consequence for the ceiling, and writes the pre-repair fact beside the correction. Rule 6: originals are struck, never rewritten.

## A3.1 What happened, from disk (the pre-repair fact)

The runner launched `D5_chain_r2` at **17:48:08Z** (`verification/queue/LAUNCH_LOG.tsv`, pid 323226, `prereg=a893355d`). The driver (pid 323228) ran with **no agent alive** through the ~17:50Z fleet kill:

* **O48 `rc=0`**, 17:49:11Z → 20:40:20Z: ledger row `wall_s=10268 ranks=4 core_min=684.533 cap_core_min=800.0 enforced_wall_s=12000 memory=12g inspect(exit,oomkilled)=[0 false] cpuset=8,10,11,13 delivered_cores_mean=[3.9954 n=680]` (`ledger.txt`, `STATUS.O48 rc=0 stamp=20260826T204020Z`). P4's O48 band [450, 700] — 684.533 is inside it (scored at grading, not here).
* **ACC48 `rc=124`**, 20:41:23Z → 20:44:05Z: the container was killed by the **in-container deadline `enforced_wall_s=150`** (= cap 10.0 core-min × 60 ÷ 4 ranks) at **162 s**; ledger `D4S_CAP_CROSSED arm=ACC48 core_min=10.133 cap=10.0 ceiling=40.0 action=REPORTED_RUN_CONTINUES` then the row `rc=124 wall_s=162 ranks=4 core_min=10.8 cap_core_min=10.0 enforced_wall_s=150 memory=12g inspect(exit,oomkilled)=[124 false]`. The log's last lines (`ACC48_20260826T204123Z_387321.log`): `ColorSweep: 961 134.67 s` / `number of uncolored: 0 0` / **`Global ColorSweep: 0 135.64 s` / `Number of Uncolored: 98959 4`** — the dRdW colouring's global phase had just begun; **the total-derivative step never started.** `STATUS.chain`: `chain=STOPPED_AT_FIRST_NONZERO arm=ACC48 rc=124 stamp=20260826T204405Z`. The container object is gone by the launcher's registered post-bookkeeping `docker rm` (a NOTE, not a missing run — the row was written from `docker inspect` first).
* **The 10.8 core-min is WASTE**, its own figure, never absorbed: `docs/COST_CALIBRATION.md` C-row filed by this lane (id re-derived at commit). ACC48's `.ok` marker is a 0-byte `test -s log && touch` sentinel and is not success.
* Preserved before the r3 driver re-opens the STATUS files at preflight: `STATUS.ACC48.deadline_20260826T204405Z` and `STATUS.chain.acc48_stop_20260826T204405Z` (byte copies, `cp -p`, in the run root — the D4-SHIPPED `STATUS.ACC.oom_…` form). Nothing else in the run root was touched by hand.

## A3.2 The defect — `D5-PREREG-DEF-1`, in §4's ACC row; the `D4S-LAUNCHER-DEF-2` class

§4 priced ACC48/ACC192 at **3.000 core-min each, cap 10.0, deadline 150 s**, anchored on "D4 ACC, C-94". As UPDATE N / C-132 established for the sibling item, D4's `ACC` (`acc_ledger.txt`, 45 s at 8g) was `d4_accept_primal.py` — a single acceptance primal — **not** `compute_totals`; the D5 ACC arms are registered as `-task compute_totals` on a cold staged copy (§2). A cold `compute_totals` at np=4 on this mesh must first colour the Jacobian: **135.64 s to the end of the local sweep at 4 ranks = 9.04 core-min against a 10.0 cap** before a single adjoint is solved. The registration was wrong about the program it priced; the launcher enforced exactly the cap it was given (`D4_CAP_ASSERT … registered_core_min=10.0 … enforced_wall_s=150`). **Nothing here is about the toolchain**: `inspect [124 false]`, no OOM, no host event, no agent (none alive 17:50Z–20:44Z).

## A3.3 Re-stated ACC caps and prediction — from the measured anchor, stated as a consequence table

| anchor | measured | what it bounds |
|---|---|---|
| D5 ACC48 r2 (this mesh, PATCHED, 12g, 4 ranks) | local colouring complete at **134.67 s**, global phase started at 135.64 s, killed at 162 s | colouring alone ≥ 9.0 core-min |
| D4-SHIPPED ACC (`CURRICULUM-D4-SHIPPED-a2-wing-cdmin/ACC_20260826T164743Z_200655.log`, same mesh, SHIPPED, 8g, 4 ranks, C-132) | local sweep `ColorSweep: 0 40.39 s`; global colouring ends `Global ColorSweep: 1322 415.53 s`; adjoint converged; reached `Computing d[aero_residuals]/d[aero_vol_coords]^T * psi 509.76 s`; OOM-killed at 525 s (35.0 core-min) | `compute_totals` on this mesh takes **> 525 s = > 35.0 core-min** to reach the last product; the remainder (the `dRdXv^T·ψ` product and the FFD/mesh chain) is unmeasured on this mesh |
| D5 O48 r2 | 100 majors in 10,268 s = **102.7 s per major** (primal + adjoint + total derivatives, colouring cached after the first major) | the post-colouring part of one `compute_totals` is of order one major ≈ 100–200 s |
| D7FR ACC (A3, 42,120-cell ONERA M6, C-122) | 2.067 core-min (31 s × 4) | a different mesh and a different program (`LIMIT 1` primal); **not an anchor for this arm**, cited because the ruling names it |

**Re-stated (struck → new):** ACC48 and ACC192 prediction **~~3.000~~ → 40.0 core-min each** (≈ 600 s wall at 4 ranks: ~415 s colouring + ~100–200 s adjoint and products), band **[35.0, 60.0]** each (lower bound = the D4-SHIPPED partial run that was killed before finishing); cap **~~10.0~~ → 60.0 core-min each**, **in-container deadline ~~150 s~~ → 900 s** (`timeout -k 60 900`, asserted by the launcher to 0.02 core-min); launcher runaway ceiling per arm 4 × 60.0 = 240.0 (report-then-stop, inherited). **Consequence for the item ceiling: `ITEM_CEILING_CORE_MIN` = sum of caps = 800 + 800 + 60 + 60 + 120 + 120 = ~~1,860.0~~ → 1,960.0**; item prediction ~~1,378.3~~ → **1,452.3 core-min** (638.9 × 2 + 40.0 × 2 + 47.267 × 2), of which 684.533 (O48) + 10.8 (ACC48 r2, waste) are already spent; **remaining arms' predictions: ACC48 40.0 + F48 47.267 + O192 638.9 + ACC192 40.0 + F192 47.267 = 813.434 core-min** (the r3 entry's cost). Dollars DERIVED, NOT MEASURED, at the owner-stated $0.0513/core-h: remaining $0.70, ceiling $1.68. **UNMOVED: O and F caps (800.0 / 120.0), every gate (G1, G-D5-1 band 3.0e-4, G-D5-P, G5d 5 %/10 %, G9, G10's per-row rule, G12), every band, every label, P1–P5, the five components, cpuset 8,10,11,13, 12g, the H5 floor 16.0, the aggregate ceiling 30.6, the wait-and-retry bound 14,400 s.** G10's item-sum clause reads the new ceiling because the ceiling is defined in §4 as the sum of caps and one addend moved.

## A3.4 Instruments re-frozen at this commit — md5 before → after, and the diffs for the supervisor's own read (SUPERVISION §3 check 1)

| file | md5 before (HEAD `a893355d`…`00afa47c`) | md5 after | change |
|---|---|---|---|
| `d5_run_arm.sh` | `50a976780e357998238ede3bbb8e5521` | `245341836829b1247b8d6efc794b7d08` | `cap_core_min()`: one `case` line (`10.0` → `60.0`) + seven comment lines; G-ROOT.1–.5, staging, deadline mechanics, cpuset, memory untouched |
| `d5_chain_driver.sh` | `89c9b7e7e43e7dd12d1c551dadfa80c8` | `728c0b47df91755e4dd5a7a8f075c9ae` | `MD5_LAUNCHER` re-frozen; the EXIT trap additionally appends one `chain_done …` line to `<run root>/CHAIN_DONE` (fixed name, A3.5); six header comment lines |
| `d5_grade.py` (the grading path) | `d50b55f498a0c16367562aa6d09ac380` | `c87c7a64657107dec4f5b7d1e634ffe6` | `CAPS` ACC 10.0 → 60.0, `ITEM_CEILING_CORE_MIN` 1860.0 → 1960.0, `PREDICTED_CORE_MIN` ACC 3.0 → 40.0, one docstring line, five comment lines; no gate function, band or composition rule touched |
| `d5_grade_selftest.py` | `3a1b2bd93ab98f7899fe0ae7b084f44e` | unchanged | reads `G.CAPS` / `G.PREDICTED_CORE_MIN` from the grader, so its fixtures follow |
| `d5_grade_selftest_evidence.txt` | re-driven 20:53Z | `5206a7176f5d7e8b8e8c0fab8d0ff2fa` | **26/26 under `python3` AND 26/26 under `python3 -O`**, `rc=0` both; AST assert count 0 in the grader, counter shown to count a planted one |
| `d5_run_arm_DELTAS_from_d4s.diff`, `d5_chain_driver_DELTAS_from_d4s.diff` | regenerated | — | plain `diff` against the `8b91be2b` blobs: **175 / 171** lines (the launcher deltas file at v1.2 had been generated against a later D4-SHIPPED launcher state, not the `8b91be2b` blob its header names; regenerated here against the blob) |

**`d5_run_arm.sh` diff (the cap rows), verbatim:**

```diff
@@ -137,9 +137,16 @@
 #   F       120.0            12g
 # D5 REGISTERED CAP TABLE (PREREGISTRATION.md section 4): per density d in {48,192}
 cap_core_min() {
+  # D5 ADDENDUM 3 (pre-compute for the r3 re-fire, 2026-08-26): ACC48/ACC192
+  # 10.0 -> 60.0 core-min (deadline 150 s -> 900 s at 4 ranks).  ACC48 r2 was
+  # cut by its own in-container deadline at 162 s while still colouring the
+  # Jacobian (rc=124, 10.8 core-min WASTE, C-row in docs/COST_CALIBRATION.md):
+  # the 10.0 anchor (D4 ACC, C-94) priced a 45 s acceptance primal, not
+  # compute_totals on 48 FFD DVs (D5-PREREG-DEF-1, the D4S-LAUNCHER-DEF-2
+  # class).  The 10.0 row is STRUCK; every other cap is unmoved.
   case "$1" in
     O48|O192)     echo 800.0 ;;
-    ACC48|ACC192) echo 10.0 ;;
+    ACC48|ACC192) echo 60.0 ;;
     F48|F192)     echo 120.0 ;;
     *)  echo "" ;;
   esac
```

**`d5_chain_driver.sh` diff (executable lines only; the six header comment lines omitted here are in the blob):**

```diff
@@ -42,7 +48,7 @@
-MD5_LAUNCHER=50a976780e357998238ede3bbb8e5521
+MD5_LAUNCHER=245341836829b1247b8d6efc794b7d08   # ADDENDUM 3: ACC cap row 10.0 -> 60.0 (was 50a97678...)
@@ -80,7 +86,7 @@
 echo "$$" > "$PIDFILE"
-trap 'rm -f "$PIDFILE"' EXIT
+trap 'rm -f "$PIDFILE"; echo "chain_done stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ arms=[$ARMS] last=[$(tail -n 1 "$STATUS" 2>/dev/null)] permission=$PERMISSION" >> "$BASE/CHAIN_DONE"' EXIT   # ADDENDUM 3 (6)
```

**`d5_grade.py` diff (constants only):**

```diff
@@ -65,10 +65,15 @@
-CAPS = {"O48": 800.0, "O192": 800.0, "ACC48": 10.0, "ACC192": 10.0,
+CAPS = {"O48": 800.0, "O192": 800.0, "ACC48": 60.0, "ACC192": 60.0,
         "F48": 120.0, "F192": 120.0}
-ITEM_CEILING_CORE_MIN = 1860.0
-PREDICTED_CORE_MIN = {"O48": 638.9, "O192": 638.9, "ACC48": 3.0, "ACC192": 3.0,
+ITEM_CEILING_CORE_MIN = 1960.0
+PREDICTED_CORE_MIN = {"O48": 638.9, "O192": 638.9, "ACC48": 40.0, "ACC192": 40.0,
                       "F48": 47.267, "F192": 47.267}
```

(plus the docstring line `G10 … sum <= 1960.0 (Addendum 3; was 1860.0)` and five comment lines above `CAPS`).

## A3.5 `CHAIN_DONE` — a fixed-name chain-end marker, registered so D6 can wait on it with no agent alive

The driver wrote no terminal marker (its `STATUS.chain` last line is one of `chain=COMPLETE | STOPPED_AT_FIRST_NONZERO | STOPPED_H5 | BLOCKED_AGGREGATE | REFUSED_ALREADY_BOUGHT | ABORT`). D6 (20g per arm) cannot co-run with D5 (12g) beside D4-SHIPPED (12g) under the 30.6 GiB aggregate rule, and its own 4 h wait bound would BLOCK before this chain ends; so D6 is filed as a `dafoam_wait_then_launch.sh` entry (W2R Addendum 2, `331d1a2d`) whose precondition is **`/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density/CHAIN_DONE`** (D6 Addendum 2). Registered semantics: the EXIT trap — armed immediately after the driver's pidfile is written, i.e. after the launcher-md5, root-staging, staged-md5 and second-driver checks — **appends** one line `chain_done stamp=<utc> pid=<pid> arms=[…] last=[<last STATUS.chain line>] permission=bc0e687e` to `CHAIN_DONE` on **every** exit of a started chain: `chain=COMPLETE`, a stop at the first non-zero rc, an H5 stop, an aggregate BLOCK, an `ALREADY_BOUGHT` refusal, a launcher-md5 abort mid-chain. **A pre-chain abort (exit 4 before the pidfile: launcher md5 drift, absent D4 base, staging or staged-md5 failure; exit 3 on a second live driver) writes NO marker** — the chain never started — and a D6 wrapper would then close at its 24 h bound with `rc=6 verdict=BLOCKED`, zero compute, which is the registered consequence, not a defect. The marker is append-only and the wrapper tests existence (`-e`), so a later re-fire of this chain does not remove it; a chain re-fired after D6 has already started is D6's G-ROOT.5 business (disjoint roots, disjoint cpusets) and no coupling exists.

**Controls, zero compute, 20:53Z:** (i) the trap line, evaluated verbatim from the driver (`grep -m1 '^trap ' d5_chain_driver.sh`) in a scratch subshell that `exit 124`s after a `STOPPED_AT_FIRST_NONZERO` status line, wrote `chain_done stamp=20260826T205329Z pid=419023 arms=[ACC48 F48] last=[chain=STOPPED_AT_FIRST_NONZERO arm=ACC48 rc=124] permission=bc0e687e` and removed the pidfile (subshell rc 124 preserved); (ii) the launcher at the new md5 was invoked on the **real, staged r3 root** with a bogus image (`d5_run_arm.sh ACC48 no-such-image:selftest`, the Addendum 2 control form): `D4S_G_ROOT_PASS item=D5 … ledger_clean=yes` (**G-ROOT.3 accepts the r2 ledger** — `ITEM=D5` exact on line 1, the `STAGED`/`ARM=`/`D4S_*` lines carry no `ITEM=` prefix, no `ROW=SHIPPED`), `D4S_G_ROOT5_PASS arm=ACC48 live_same_arm_containers=none driver_pidfile=absent`, **`D4_CAP_ASSERT arm=ACC48 registered_core_min=60.0 ranks=4 enforced_wall_s=900 enforced_core_min=60.000000 memory=12g`**, the three staged-instrument md5s `OK`, then `ABORT cannot read digest of no-such-image:selftest` rc=4 **before any `rm -rf`/`cp -a`/`docker run`** (`ACC48/` mtime unchanged at 20:41:30Z; `docker ps -a` carries no `d5_` name). Output kept as `ADDENDUM3_cap_control_20260826T205329Z.out` in the run root. **`d5_groot5_selftest.sh` is NOT re-driven**: it refuses by design when the run root exists (`run root … already EXISTS — refusing to test over a real root`), and the root now exists; the G-ROOT.5 block (`d5_run_arm.sh:187-218` after this addendum's seven comment lines; `:180-211` at v1.2) is byte-identical to the 12/12-demonstrated blob (the diff above touches only `cap_core_min()`), and control (ii) exercised G-ROOT.1–.5 live on the real root.

## A3.6 The r3 re-fire — what the driver will do, read from its code, not assumed

Entry `verification/queue/dafoam/D5_chain_r3.json`: `bash d5_chain_driver.sh ACC48 F48 O192 ACC192 F192` (O48 omitted: an `rc=0` ledger row exists for it, so the driver's `ALREADY_BOUGHT` guard would refuse the chain at O48 with `rc=3`, zero compute, if it were listed — the guard is the reason the arm list changed, and it stays in force for every arm). On fire: root present → `D5_ROOT_PRESENT`, nothing re-staged; staged md5s asserted; `STATUS.ACC48` re-opened at preflight (r2's line preserved by copy, A3.1); H5 window; aggregate wait-and-retry (D4-SHIPPED's 12g chain on 5,6,7,9 fired by the runner at 20:50:06Z is a live sibling: 12 + 12 + host RSS ≈ 27 < 30.6 — passes; a third 12g sibling would wait); `ACC48/` is `rm -rf`'d and re-staged cold from `base/` by the launcher (r2's partial `ACC48/` holds no artefact — the colouring file was never written; its log and launch output live in the root and stay); then F48 in `O48/` (`OptView.hst` present from r2's O48), O192, ACC192, F192. `prereg_commit` = the commit that lands this addendum; `cost_core_min_estimate` 813.434; `memory_floor_gb` 16.0; `permission bc0e687e`. Enqueueing is not authorisation — `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own.

**Condition, and how it was checked:** no `d5_` container exists (`sudo -n docker ps -a` 20:53Z: only `d4_F3_20260826T205120Z_411184`, another item's); no D5 driver is live (`d5_driver.pid` absent; `ps` shows no `d5_chain_driver`); the ledger carries exactly one `rc=0` row (O48) and one `rc=124` row (ACC48). First compute on ACC48 under the re-stated cap has not occurred.

---

# ADDENDUM 4 — 2026-08-27 — **POST-COMPUTE** — `D5-LAUNCHER-DEF-1`: the container ran the F arm in a directory the launcher never creates. ACC48 is BOUGHT and its Addendum-3 repair is a prediction HIT.

**Version 1.3 → 1.4. Lines whose number changed above this section: 0** — proved on BYTES, not on a line count: the HEAD blob of this file is a byte-exact PREFIX of the amended file, asserted in the commit invocation. Written 2026-08-27 by dafoam `lab-lane` B for `dafoam-supervisor`; ruling `[lab-attributed]`; permission `bc0e687e`. **First compute on this item HAS occurred, so under `CLAUDE.md` rule 2 and `VERIFICATION_CHARTER.md` §2b GATES ARE CLOSED: this addendum alters NO gate, NO threshold, NO cap, NO band, NO label, NO prediction, NO cpuset and NO cost.** It repairs one launcher path defect, records one arm bought, books one waste row, and re-pins two md5s. Rule 6: originals are struck, never rewritten.

## A4.1 What happened on the r3 chain, from disk

`STATUS.chain` and `ledger.txt` in `/home/ubuntu/certonomous-runs/CURRICULUM-D5-a2-wing-ffd-density`:

* **`ACC48` `rc=0`**, 13:38:12Z → 13:47:09Z. Ledger row: `wall_s=537 ranks=4 core_min=35.8 cap_core_min=60.0 enforced_wall_s=900 enforced_core_min=60.000000 memory=12g inspect(exit,oomkilled)=[0 false] memavail_pre_GiB=27.48 memavail_post_GiB=27.30 cpuset=8,10,11,13 delivered_cores_mean=[3.9889 n=35 max_nr_throttled=2568]`. **BOUGHT**, on the artefacts, at 4 ranks on the registered cpuset with no OOM and no sibling on its cores.
* **`F48` `rc=127`**, 13:48:14Z → 13:48:25Z, `wall_s=11`, **0.733 core-min**, `inspect [127 false]`. `chain=STOPPED_AT_FIRST_NONZERO arm=F48`.
* **`CHAIN_DONE`** written 13:48:25Z by the driver's EXIT trap. **Registered behaviour** (A3.5: the trap fires on every exit of a STARTED chain; a pre-chain abort writes none). It is a serialisation token for the memory ceiling, not a data dependency, and D6's wait-wrapper released on it at 13:49Z correctly. **D6 is not contaminated by F48's failure.**

**The queue entry's `launcher_rc=127` is the exit of the LAUNCH ARGV, not of the chain**, and is an INFRASTRUCTURE field under L-342. The chain's own record is `STATUS.chain`, and it says the chain bought one arm and stopped at the second.

## A4.2 The Addendum-3 cap repair is VALIDATED BY MEASUREMENT — a pre-registered prediction HIT

Addendum 3 diagnosed `D5-PREREG-DEF-1` (ACC48 killed at `rc=124` / 10.8 core-min by its own under-registered 10.0 cap while still colouring the Jacobian) and **re-registered, before the re-fire and with no answer in hand**: prediction **40.0** core-min, band **[35.0, 60.0]**, cap **60.0**, in-container deadline **900 s**.

**Measured on the re-fire: 35.8 core-min.** That is **INSIDE the registered band, at its lower edge**, and the ratio actual/predicted is **0.895**. The lower bound of that band was set from the D4-SHIPPED partial run that was killed before finishing — the re-fire landing just above it is the band behaving exactly as its own stated derivation said it would. A repair that re-priced a rung from a measured anchor, froze the band before the re-fire, and then landed inside it is the shape this lab is trying to produce. Booked as its own row in `docs/COST_CALIBRATION.md`.

## A4.3 The defect — `D5-LAUNCHER-DEF-1`, and it is a WORK-versus-ARM divergence

**Established from disk, not inferred.** The container log `F48_20260827T134814Z_789173.log` (369 bytes, read whole) ends:

> `bash: /mnt/F48/d5_cmd.sh: No such file or directory`

and `F48_launch.out` printed, seconds earlier, `D4S_CMDFILE arm=F48 md5=4d1276845bb3a20bb2ba31f335c1094f`.

**The file never vanished. It was never in `F48/`.** In `d5_run_arm.sh` at the Version 1.3 blob:

* `:277` `WORK="$BASE/$ARM"`, then `:281` guards the cold-stage block with `[ "${ARM:0:1}" != "F" ]`, so **an F arm is never staged and `$BASE/F48` is never created by this launcher**;
* `:303` the else branch **REASSIGNS** `WORK="$BASE/O${DENS}"` — which is what **§2 of this pre-registration REGISTERS**: the F48 row's run directory is `O48/`, *"F runs in the O directory, the frozen F3 path"*;
* `:320` `CMDFILE="$WORK/d5_cmd.sh"` therefore wrote to **`O48/d5_cmd.sh`**, correctly, and printed its md5, correctly;
* `:398`/`:403` the container line used **`$ARM`, not `$WORK`**: `-w "/mnt/F48"` and `bash /mnt/F48/d5_cmd.sh`.

Docker created `/mnt/F48` as the container's working directory, as root (`--user 0:0`, `D4S_CONTAINER_UID: 0`), and the `-v "$BASE":/mnt` bind propagated that `mkdir` to the host. **That is the whole mechanism**, and it is confirmed positively rather than by absence:

| the claim | the reading on disk |
| --- | --- |
| the command file was written, and to `O48/` | `$BASE/O48/d5_cmd.sh`, 138 bytes, mtime **13:48**, md5 **`4d1276845bb3a20bb2ba31f335c1094f`** — byte-for-byte the md5 the launcher printed for `arm=F48` |
| `$BASE/F48/` was created by the CONTAINER, not the launcher | `drwxr-xr-x 2 **root root**`, empty (`.` and `..` only), mtime 13:48; the launcher runs as `ubuntu` and its only `mkdir`-equivalent for an arm is the `cp -a` in the block F arms skip |
| `$BASE/F48/` never existed before | F48 had never run: `STATUS.chain` shows chain 1 stopped at O48, chain 2 at ACC48; staging never creates it |
| **nothing removed anything** | the file the launcher wrote is **still on disk, intact, with the matching md5**. A removal hypothesis has to explain a file that was never deleted |

**The sibling is ruled out on evidence, not assumed innocent.** `ledger.txt` records `siblings_pre=[av1_X2-P_20260827T134811Z_788560]` and `siblings_post=[...]` — the same container, live across F48's whole 11 seconds. It is the ansys-verification `AV1_chain` item (`verification/queue/dafoam/launched/AV1_chain.json`), it holds no reference to `CURRICULUM-D5` anywhere in `cases/ansys_verification/` or `verification/runs/ansys_verification/`, and — decisively — **the causal chain is complete without it**: the exec path pointed at a directory this launcher never writes into, and the file it did write is intact. There is no deletion for a concurrent process to have performed.

**This defect could only ever bite an F arm**, because for every other arm `WORK` is exactly `$BASE/$ARM` and the two spellings coincide. That is why O48 (`rc=0`, 684.533 core-min) and both ACC48 fires reached their commands.

## A4.4 The repair, and the guard that makes the class impossible

The container's working directory is now **derived from `$WORK`**, which is the launcher's own single source of truth for where an arm runs:

```
WORKNAME="$(basename "$WORK")"
[ "$WORK" = "$BASE/$WORKNAME" ] || ABORT   # /mnt/$WORKNAME is not $WORK's path in the container
[ -d "$WORK" ]                || ABORT   # the container would CREATE it empty -- the rc=127 shape
echo "D5_WORKDIR arm=$ARM host_workdir=$WORK container_workdir=/mnt/$WORKNAME cmdfile=$WORK/d5_cmd.sh"
```

and `-w "/mnt/$WORKNAME"` / `bash /mnt/$WORKNAME/d5_cmd.sh` replace the two `$ARM` spellings. **The second guard is the one that matters**: it refuses precisely the condition that produced `rc=127` — a container working directory that nothing on the host created — *before* the container starts, instead of after 11 seconds and 0.733 core-min. The `D5_WORKDIR` line puts the host path, the container path and the command-file path in the launch output so a reader can see all three agree without running anything.

**Nothing else in the file is touched**: staging, G-ROOT.1–.5, G-COLD, the age-guard datum, the cap assertion, the deadline mechanics, the cpuset, the memory caps, the runaway guard, the CPU sampler and the ledger row format are byte-identical. The full diff is `d5_run_arm_DELTAS_addendum4.diff` (40 lines) for the supervisor's own read under `SUPERVISION_CHARTER.md` §3 check 1.

**The stray `$BASE/F48/` is LEFT IN PLACE**, empty and root-owned. It is the physical evidence of the defect and deleting it would destroy the record; it is inert (the `ALREADY_BOUGHT` guard reads the ledger, and `G-COLD` applies only to non-F arms).

## A4.5 Controls — twelve, all at ZERO compute

`d5_addendum4_control.sh`, evidence `d5_addendum4_control_evidence.txt`, **pass=12 fail=0**, 2026-08-27T16:45:20–16:45:21Z. Controls (1) and (2) drive lines lifted **verbatim from the launcher** in a scratch subshell — the technique Addendum 3's control (i) used on the EXIT trap.

| # | what is planted | what must happen | reading |
| --- | --- | --- | --- |
| 1 | `ARM=F48` through the launcher's own F-branch line | `WORK` = `$BASE/O48`, `WORKNAME` = `O48` — **the directory §2 registers** | `[OK ]` |
| 2a | `WORK=$BASE/sub/dir` | guard refuses: not directly under `BASE` | `[OK ]` |
| 2b | `WORK` directly under `BASE` but **ABSENT** — **the exact `rc=127` shape** | guard refuses before any container | `[OK ]` |
| 2c | the registered `WORK=$BASE/O48` | guard **PASSES** — a guard that refuses everything is not a guard | `[OK ]` |
| 3 | nothing | **zero EXECUTABLE lines** carry `/mnt/$ARM` (the one remaining occurrence is inside the comment naming the defect) | `[OK ]` |
| 3b | nothing | both container paths read `/mnt/$WORKNAME` | `[OK ]` |
| 4 | **PLANTED CONTROL on (3)'s reader** — a sacrificial copy with `-w "/mnt/$ARM"` restored | the reader must **count it** | `[OK ]`, count 1 |
| 5 | the real launcher, arm **F48**, on the **real r3 run root**, with a bogus image (the Addendum 2/3 control form) | exit 4 at the image digest read, **before any `rm -rf`, `cp -a` or `docker run`** | `[OK ]` |
| 5b | — | `D4S_G_ROOT_PASS item=D5` — G-ROOT.1–.3 accept the r3 ledger unchanged | `[OK ]` |
| 5c | — | `D4_CAP_ASSERT arm=F48 registered_core_min=120.0 ranks=4 enforced_wall_s=1800` — **the F cap has not moved** | `[OK ]` |
| 5d | — | `ledger.txt` md5 **unchanged** across the control | `[OK ]` |
| 5e | — | `O48/` mtime **unchanged** — no staging, no `rm -rf` | `[OK ]` |

Control 4 is why control 3 is evidence and not an assertion (`CLAUDE.md` rule 3). Control 5c is the reading that proves this addendum moves no cap, taken from the launcher itself rather than from this document's own prose.

## A4.6 Instruments re-frozen at this commit

| file | md5 before | md5 after | what changed |
| --- | --- | --- | --- |
| `d5_run_arm.sh` | `245341836829b1247b8d6efc794b7d08` | `8fb1a94c8deeb5d2ea596b05a452dac0` | `WORKNAME` + two guards + one `D5_WORKDIR` line + an 11-line comment; the two container paths `$ARM` → `$WORKNAME`. **Nothing else** — `d5_run_arm_DELTAS_addendum4.diff`, 40 lines, two hunks |
| `d5_chain_driver.sh` | `728c0b47df91755e4dd5a7a8f075c9ae` | `cf0bb2083eebf3333453f5a564189c89` | `MD5_LAUNCHER` re-pinned to the line above. The driver asserts it before staging **and before every arm** (`:60`, `:95`), so a stale pin is the `D8R-DRIVER-DEF-1` death; pin == actual is asserted in the commit invocation |
| `d5_grade.py` (**the grading path**) | `c87c7a64657107dec4f5b7d1e634ffe6` | **UNCHANGED** | the comparator is not touched by this addendum. `CAPS`, `ITEM_CEILING_CORE_MIN` 1,960.0, `PREDICTED_CORE_MIN`, every gate function, band and composition rule stand as frozen at Addendum 3 |
| `d5_addendum4_control.sh` | — | new | the twelve controls above |

## A4.7 The r4 re-fire

**Arms: `F48 O192 ACC192 F192`.** `ACC48` is **omitted because it is BOUGHT**: the driver's `ALREADY_BOUGHT` guard (`d5_chain_driver.sh:101`) refuses any arm carrying an `rc=0` ledger row and would stop the chain at `rc=3` and **zero compute** if it were listed. `O48` is omitted for the same reason, as in r3.

**Cost, remaining arms, from Addendum 3 §A3.4's frozen per-arm predictions — nothing re-priced here:** F48 47.267 + O192 638.9 + ACC192 40.0 + F192 47.267 = **773.434 core-min**. This is **40.0 lower than r3's 813.434**, and the difference is exactly ACC48's prediction, now bought. Dollars **DERIVED, NOT MEASURED**, at the owner-stated `c7a.4xlarge` $0.0513/core-h: **$0.66**. Caps unmoved (O 800.0 / ACC 60.0 / F 120.0), item ceiling unmoved at 1,960.0.

`prereg_commit` = the commit landing this addendum; `memory_floor_gb` 16.0; `ranks` 4; `permission bc0e687e`. **Enqueueing is not authorisation** — `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own.

## A4.8 Calibration rows due at this completion (`CLAUDE.md` rule 12)

| row | predicted | actual | ratio | attribution |
| --- | --- | --- | --- | --- |
| ACC48 (r3), **bought** | 40.0 core-min (Addendum 3, band [35.0, 60.0]) | **35.8** | **0.895** | misprediction, **inside the registered band at its lower edge** — the Addendum-3 repair validated. Not contention: `delivered_cores_mean` 3.9889 of 4 on the registered cpuset, no OOM |
| F48 (r3), **WASTE** | 47.267 core-min | **0.733** spent, **nothing bought** | — | **waste, named separately and never absorbed into any ratio** (`COMPUTE_BUDGET_CHARTER.md` §6). Cause `D5-LAUNCHER-DEF-1`, this addendum. Not a stall (11 s, far under the 3,600 s rule) and not contention |

| what this addendum did | figure |
| --- | --- |
| gates, thresholds, caps, bands, labels, predictions, cpusets or costs altered | **0** |
| defects named and repaired | **1** (`D5-LAUNCHER-DEF-1`) |
| arms bought | **1** (ACC48, 35.8 core-min) |
| core-minutes booked as waste | **0.733** |
| controls driven, all zero compute | **12**, `pass=12 fail=0` |
| lines whose number changed above this section | **0**, proved on bytes |
