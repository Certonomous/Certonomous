# Curriculum D6 — Multipoint cruise on D4's case: three CL targets, weighted composite objective

**Item id:** `D6` (dafoam curriculum, `cases/dafoam/EXPERTISE_CURRICULUM.md:96`).
**Version 1.0 — FROZEN 2026-08-26 by dafoam `lab-lane` Q1 for `dafoam-supervisor`** under Sanaa's
queue-first order (`7def3c6b`, `73eccb1b`) and the supervisor's UPDATE F / UPDATE J dispositions
(`[lab-attributed]`). **Committed BEFORE any container starts** (`CLAUDE.md` rule 2). The freeze sha
is the commit that introduces this file; it is named in `verification/queue/dafoam/D6_chain.json`
(`prereg_commit`) and on the board. Supersedes `PREREGISTRATION_DRAFT.md` v0.1 (`f8cf4700`), removed
from the tree in the same commit. **Nothing here is sent, filed, uploaded, registered, posted or
commented** (rule 7; `DAFOAM_CHARTER.md` §10). **No frozen file is edited** (rule 6). Permission for
detached launches: **`bc0e687e`** (Sanaa's words, boarded verbatim).

> **ID-NAMESPACE WARNING.** `docs/DOCKET.md:129,130,139,140` carries fleet-defect rows numbered D5, D6,
> D14, D15 — different objects from the dafoam curriculum items at `cases/dafoam/EXPERTISE_CURRICULUM.md:95,96,125,126`
> (`docs/DOCKET.md:211`). Every `D<n>` in this file is the **curriculum** item.

Short form: everything not stated here is **inherited verbatim** from `curriculum_D4/PREREGISTRATION.md`
§1, §4–§10 and from the **D4-SHIPPED Addendum-2 launcher family frozen at `8b91be2b`**, through
`curriculum_D5` (frozen `c5c25189`, Addendum 1 `a1dcdb7d`), whose launcher family this item derives from
with the deltas of §7. Where a number here disagrees with a cited source, **the cited source wins and
this document is defective.**

---

## 1. What changes, and only this

| | D4 (PATCHED row, `GATE REACHED`, C-97) | D6 |
|---|---|---|
| case, mesh, np, FFD (6×2×8, 96 DVs), twist (7), decomposition | as D4 | **identical**; the FFD is D4's own `base/FFD/wingFFD.xyz` (md5 `f9435ee2ef54df0b08feae6e5127125d`) |
| toolchain row | PATCHED `dafoam-idwarp-rot:v1`, digest `sha256:2927768a…dee30f6d35`, `libidwarp.so` md5 `85f59e87…` | **identical — PATCHED ONLY**; `G-ROW` refuses SHIPPED; the SHIPPED row is named **unbought** (§6) |
| scenarios | one, CL = 0.5 | **three `ScenarioAerodynamic` scenarios `cl04`/`cl05`/`cl06` sharing one geometry, CL targets 0.4 / 0.5 / 0.6**, each with its own `DAFoamBuilder` in its own `run_directory` `mp04/`/`mp05/`/`mp06/` (a full case copy each, staged by the launcher; the image's builder carries `run_directory` — probed at zero compute, §7), its own `patchV_cl0k` (AoA) DV and its own CL equality constraint |
| objective | CD | **composite `J = Σ wᵢ·CDᵢ`, weights FROZEN: w = (0.25, 0.50, 0.25)** for (0.4, 0.5, 0.6), an OpenMDAO `ExecComp`. Weights are not tuned after a run; a second weight set is a new item |
| geometric constraints | thickness, volume, LE/TE on the geometry | the same four, taken from the `cl05` geometry only — three identical FFDs on one surface, one set of constraints (a second copy is the same constraint) |
| optimiser | IPOPT `max_iter` 100, `tol` 1e-5 | **identical**; `findFeasibleDesign` solves the three CL targets on the three `patchV` at once before `run_driver` (the DAFoam multipoint form) |
| runScript | `d4_opt_runScript.py` (md5 `2906d52a…`) | `d6_opt_runScript.py` — the deltas above and nothing else; `d6_opt_runScript_DELTAS_from_d4.diff` (223 diff lines) is the record; the `# OpenMDAO setup` anchor is kept so the FD and REF_off instruments exec the producer's own header |
| launcher family | D5's (`8b91be2b` family) | `d6_run_arm.sh`, `d6_chain_driver.sh`, `d6_aggregate_memory.py`, `d6_groot5_selftest.sh` — derived copies, **byte-for-byte except the registered deltas of §7** |

## 2. Arms — four, in this order, one detached chain

| arm | kind (G1) | task | work dir | container mem | new compute |
|---|---|---|---|---|---|
| O_mp | SOLVER | IPOPT `run_driver` on J, `max_iter` 100 | `O_mp/` (+ `mp04/ mp05/ mp06/` copies inside it) | 20g | yes |
| ACC_mp | SCRIPT | `compute_totals` on a cold staged copy: three primals + three adjoints in one process (the D4-SHIPPED ACC shape, ×3); the artefact is the log | `ACC_mp/` | 20g | yes |
| F_mp | SOLVER | `d6_extract_endpoint.py` then `d6_fd_endpoint.py`: endpoint FD table of **J** over five registered components | `O_mp/` | 20g | yes |
| REF_off | SCRIPT | D4's PATCHED optimum geometry (twist + shape from D4's own `OptView.hst`, staged read-only, md5 `0d956d6ccbc010402915710f662d3b11`, extracted by D4's unmodified `d4_extract_endpoint.py`) re-trimmed to CL 0.4 / 0.5 / 0.6 by `findFeasibleDesign` on the three `patchV` **only** — no shape or twist change; writes `d6_ref_off.json` | `REF_off/` | 20g | yes, three trimmed primals plus Newton steps |

Chain: `d6_chain_driver.sh O_mp ACC_mp F_mp REF_off`, stops at the first non-zero rc. Arm kinds are registered
here and in `d6_grade.py:ARM_KIND`. **The five FD components, NAMED IN ADVANCE, BY NAME:** `shape[46]`,
`shape[18]`, `shape[0]`, `twist[0]`, `patchV_cl05[1]` (the AoA of the CL 0.5 point) — D4's five with the
single-point `patchV[1]` mapped to the design point that carries it.

## 3. Gates — per point AND composite, both mandatory; registered before compute

`d6_grade.py` (md5 in §7) is the grading path. Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING`.

* **G1 — completion, ARM-KIND AWARE** (the D5 form, from birth). SOLVER arms (O_mp, F_mp): kernel
  `rc == 0` from `docker inspect .State.ExitCode` (refuse on a harness/kernel disagreement),
  `OOMKilled false`, the **positional** terminal statement `Finalising parallel run` as the last non-empty
  log line, and the age guard on the registered artefacts (`O_mp/opt_IPOPT.txt`, `O_mp/OptView.hst`;
  `O_mp/d6_fd_endpoint.json`, `d6_endpoint_dvs.json`, `d6_major_history.json` for F_mp). SCRIPT arms
  (ACC_mp, REF_off): kernel `rc == 0`, the `.ok` marker, and the registered artefact (ACC_mp: the log;
  REF_off: `d6_ref_off.json`) newer than the arm's datum; the terminal statement reported, not composed.
  **REF_off's staged input `OptView.hst` is exempt from the age guard BY MD5 only** (registered
  `0d956d6c…`; a moved md5 refuses) — the D7FR H4 form, never by name alone.
* **L-342 field classes** exactly as D5 §3: absent infrastructure → `NOT_MEASURED` named beside the verdict;
  present-but-garbage → REFUSE; absent physics → REFUSE; kernel-record fallback for an arm with no ledger row.
* **G-D6-1 — per-point verdicts (the curriculum's named failure mode):** for each CL target,
  `CDᵢ(mp) ≤ CDᵢ(REF_off)` → `PASS` for that point, else `GATE FAIL` for that point. `CDᵢ(mp)` is the final
  major row of `d6_major_history.json`; `CDᵢ(REF_off)` is `d6_ref_off.json`. **Three verdicts, always all
  three reported; a composite `PASS` with any point `GATE FAIL` is reported as three verdicts, never as one.**
* **G-D6-2 — composite:** `(J₀ − J_f)/J₀` in **[15, 40] %** → `PASS`, else `GATE FAIL` (D4's single-point
  reduction was 28.6758 % in [25, 45]; a composite is bounded by its worst point, so the band opens downward).
  `J₀` is the first major row (after the trim), `J_f` the last.
* **G-D6-3 — the single-point price:** `CD₀.₅(mp) − CD_f(D4) ∈ [0, 1.0e-3]` → `PASS`; `> 1.0e-3` →
  `GATE FAIL`; **negative → `NOT A RESULT` pending triage** (a finding about D4, not about D6). `CD_f(D4)`
  is **re-read** from `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt`
  (read-only), refused if it differs from the recorded `2.1125978108239574e-02`, through a reader that carries
  a **planted-zero control** (`PLANT = 1.234e-03`, plant-and-read-back, unperturbed copy unchanged; refuse
  if blind; control files in `<run root>/grader_controls/`).
* **G-D6-4 — bright line on J:** per component |d(s_hi) − J_adj|/|d(s_hi)| ≤ 5 %, no sign flip, plateau
  ≤ 10 %; aggregate vector-relative error ≤ 5 %; **≥ 2 sign flips → `NOT A RESULT` (the pathology,
  named in advance)**. No grid family: **no GCI is quoted.**
* **G9 / G10 / G12:** PATCHED digest on every row and the PATCHED `libidwarp.so` md5 on every log
  (`D4S_IDWARP_SO_MD5:`); every row `core_min ≤ cap` and the sum ≤ 2,230.0 (a crossing is `GATE FAIL` as
  the frozen text says, report mode beside it); `cpuset == 2,3,4,14` on every row, delivered ≥ 3.0 of 4
  where measured, `NOT_MEASURED` disclosed.
* **Composition** (`d6_grade.py:compose`): `NOT A RESULT` if G1 fails, or G-D6-4 carries the pathology,
  or G-D6-3 is negative; else `GATE FAIL` if any gate (including any per-point verdict) is `GATE FAIL`;
  else `PASS`. `NOT_MEASURED` fields printed **beside** the verdict, never inside it.

## 4. Cost — measured-derived from D4's rows; memory registered as an EXPOSURE

| arm | anchor | prediction (core-min) | cap (core-min) | cap wall inside container | mem |
|---|---|---|---|---|---|
| O_mp | 6.389 core-min/major (D4 PATCHED) × **3 scenarios** (three primals + three adjoints per major; the coloring is shared) × 80 majors point | **1,533.4** (100-major reading 1,916.7) | 2,000.0 | 30,000 s | 20g |
| ACC_mp | 3.0 × 3 (C-94) — one arm, three primal+adjoint pairs | **9.0** | 30.0 (10.0 per pair) | 450 s | 20g |
| F_mp | 47.267 (C-96) × 3 points per FD primal pair | **141.8** | 180.0 | 2,700 s | 20g |
| REF_off | 3.0 × 2 + `findFeasibleDesign` ≈ 5 primals ≈ 4.5 | **10.5** | 20.0 | 300 s | 20g |
| **total** | | **1,694.7 core-min** | **ceiling 2,230.0** (sum of caps) | | |

* **ranks 4**; wall **7.06 h** at the estimate, **9.29 h** at the ceiling.
* **`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot read
  its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED, NOT MEASURED**: estimate **$1.45**
  (1,694.7/60 × 0.0513 = 1.449), ceiling **$1.91**.
* **Exposure stated (cost):** the ×3 per-major scaling assumes three independent adjoint solves per major
  and no shared-primal saving; D4-SHIPPED's measured 7.317 core-min/major (contended, C-117) would put O_mp
  at 1,756 (80 majors) — inside the cap. Above the curriculum's ~1,500 for a stated reason (three adjoints,
  not one).
* **Exposure stated (memory) — the one this item may fail on, registered as P7:** one DAFoam solver at
  np=4 on this case held ~11.7 GB host-side (D4) and 9.263 GiB peak container RSS (A3 rung 2). Three
  solvers in one process share the interpreter and libraries but not their Jacobians. **Every arm runs at
  20g** — the largest cap the 30.6 GiB aggregate ceiling admits beside an 8g sibling — with the **H5 floor
  at 24.0 GiB** (cap + 4 GiB headroom, D4-SHIPPED §4.4 formula; the family's 16.0 is a 12g number and does
  not apply). **Never 8g**: the D4-SHIPPED ACC arm was OOM-killed by its 8g cgroup (rc=137, 16:56:28Z
  2026-08-26). An OOM kill here (`rc=137`, `OOMKilled true`) is `NOT A RESULT` for G1, stops the chain at
  O_mp after minutes, and is **a finding about multipoint feasibility at np=4 on this box, not a wasted
  run** (P7 MISS). The H5 refusal on a loaded box is a STOP (`chain=STOPPED_H5`), re-fireable, and is the
  gate working.
* **Cap mode:** deadline inside the container at cap × 60 / 4 s (asserted to 0.02 core-min); the host poller
  reports a crossing and hard-stops at 4× cap — the inherited report-then-stop mode. Aggregate
  wait-and-retry (poll 30 s, bound 4 h, every wait in `STATUS.<arm>`, BLOCK at the bound). A calibration
  row is owed at completion (`docs/COST_CALIBRATION.md`, rule 12).

## 5. Predictions — scored HIT/MISS afterwards, never adjusted

| # | prediction | band / number |
|---|---|---|
| P1 | `EXIT: Optimal Solution Found.` within `max_iter` 100 | majors **[60, 100]**, point 80 |
| P2 | composite reduction `(J₀ − J_f)/J₀` | **[15, 40] %, point 22 %** |
| P3 | single-point price at CL 0.5 | `CD₀.₅(mp) − 2.1125978e-02 ∈ [0, 1.0e-3]`, point **+3.0e-4** |
| P4 | off-design gain `CDᵢ(REF_off) − CDᵢ(mp)` | at 0.6 **> 0**, point +8.0e-4; at 0.4 **> 0**, point +2.0e-4 |
| P5 | O_mp cost | **[1,200, 2,000]** core-min, point 1,533.4 |
| P6 | per-point verdicts | **all three `PASS`** (the pathology does NOT appear at w = 0.25/0.50/0.25) |
| P7 | no arm OOM-killed at 20g (multipoint feasible at np=4 on this box) | HIT/MISS by `OOMKilled` |

## 5b. Placement, memory and the detached form — registered by measurement at freeze

* **cpuset `2,3,4,14`.** Measured 17:01Z–17:38Z 2026-08-26 by `sudo -n docker inspect` on every running
  container: one live container, W2R's `d12y_…` on `12`, 8 GiB. Held clear: D5's `8,10,11,13`; the
  D4-SHIPPED registered set `5,6,7,9` (its chain stopped `rc=137` on ACC at 16:56:28Z and may be re-fired
  by its own lane — **chosen: D6 does NOT wait on `STATUS.F3` and does not share that set; it is disjoint,
  so no coupling to another item's re-fire decision exists**); D7FR's `2,3,4,6` is released — its F-S and
  F-P arms are complete (`STATUS.F-P rc=0` 16:43:35Z) and no D7FR arm is outstanding, so `2,3,4` are free
  and `14` was measured idle; core 0 (the default landing core) is not used. Native host processes float on
  0–15 and are the runner's business, not a cpuset collision.
* **Delivered cores are measured** (cgroup sampler); absent → `NOT_MEASURED`.
* **The detached form, G-ROOT.1–.5, `rc` from `docker inspect` into `STATUS.<arm>` inside the driver, no
  `--rm`, root staging on first fire, `ALREADY_BOUGHT`:** exactly as D5 §5b. G-ROOT.2's forbidden list names
  D4's, D4-SHIPPED's, D4-SHIPPED-R's, **D5's**, D14's, D7R's, D7FR's, D12R's, D12R2's and D12R2W2R's roots.
  **G-ROOT.5 DEMONSTRATED 2026-08-26T17:38:56Z** (`d6_groot5_selftest_evidence.txt`, **13/13**): a
  sacrificial `sleep` container → `rc=3`; a sacrificial live pid with cwd = run root → `rc=3`; a stale
  pidfile does not block; clear passes and the launcher stops at the L-251 mode check before any staging;
  D4's, D4-SHIPPED's and D5's roots refuse at G-ROOT.1; no unfilled placeholder; zero backticks on
  executable lines; the temporary root stayed empty and is **absent afterwards**.

## 6. What this item does NOT claim

Nothing about the SHIPPED row (unbought; named unbought). Nothing about weight sensitivity — a second item.
Nothing at np≠4. No Strouhal, no grid family, no GCI. Nothing about the multipoint runScript's behaviour
before its first arm: **`d6_opt_runScript.py` has been compiled and AST-parsed on the host and its builder
signature probed in the image, and has NOT been executed** — the first arm is its test; a construction
failure is `rc≠0` at near-zero cost, `NOT A RESULT` by instrument, and the chain stops there (§7).

## 7. Instruments, frozen by md5 at this commit

| file | md5 | derivation |
|---|---|---|
| `d6_run_arm.sh` | `98472772c9cdfd9007fcf6367b0a2a37` | `d5_run_arm.sh` @ `a1dcdb7d` (md5 `50a97678…`) + `d6_run_arm_DELTAS_from_d5.diff` (397 diff lines): item/root; forbidden roots (+D5, +D7FR, +D12R2W2R); **cpuset 2,3,4,14**; cap table §4, every arm 20g; the five instrument md5s; arms O_mp/ACC_mp/F_mp/REF_off; `mp04/mp05/mp06` staging; REF_off's D4 history staged read-only and md5-asserted before the datum; `d6_` prefix and pidfile; `-w` on the arm directory |
| `d6_chain_driver.sh` | `860b984244e628279e6400b2743321fc` | `d5_chain_driver.sh` @ `a1dcdb7d` (md5 `47e7767d…`): names, launcher md5, instruments (no FFD boxes), `cap_mem_gib` 20, **H5 floor 24.0** |
| `d6_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | **byte-identical** to `d4s_aggregate_memory.py` @ `8b91be2b`; `python3 -O d6_aggregate_memory.py 20 30.6` → `aggregate_GiB 30.42, ok true` at 17:40Z |
| `d6_groot5_selftest.sh` | `5c24a2cf03534f481587c1a3288b58fe` | the D5 pattern; adds the placeholder check |
| `d6_grade.py` | `a76a7d5e298a6ba719143f14e10c89bf` | **the grading path.** `d5_grade.py` (md5 `d50b55f4…`) with D6's gates; 0 `assert` nodes by AST, counter shown to count a planted one |
| `d6_grade_selftest.py` | `3a8dbe54bea1371e15f509012ee42369` | **26/26 under `python3` AND `python3 -O`** (`d6_grade_selftest_evidence.txt`): field classes (absent infra named, garbage/absent-physics REFUSE); clean control PASS with three per-point PASS; planted control; one point failing → three verdicts and item GATE FAIL; composite out of band → GATE FAIL and the band mutation flips it; negative price → NOT A RESULT; price > 1e-3 → GATE FAIL; blind reader → REFUSE; D4 reference moved → REFUSE; OOM 137 → NOT A RESULT, P7 MISS; rc disagreement → REFUSE; terminal not last → NOT A RESULT; SCRIPT arms without `.ok` → NOT A RESULT; stale artefact; staged-input md5 moved → REFUSE; 2 flips → pathology; cap crossing → G10; wrong cpuset → G12 with delivered `NOT_MEASURED` named; `NOT_MEASURED` beside a PASS; absent `d6_ref_off.json` → REFUSE |
| `d6_opt_runScript.py` | `ae4b0305f0395b0047f1ce042d4956a5` | §1; `d6_opt_runScript_DELTAS_from_d4.diff` (223 diff lines) |
| `d6_fd_endpoint.py` | `629bdef27a0dfb838f31ccdb5617aa3d` | D5's FD instrument (D4's bytes) re-pointed at the producer, graded function `obj.J`, per-point CD/CL recorded per primal, five components §2 |
| `d6_extract_endpoint.py` | `a8f96e92ec03cd6773c7d8f82406254e` | D4's extractor with D6's DV keys and the J / per-point CL, CD history |
| `d6_ref_off.py` | `674e460e81c316487397eda49370cef6` | new; exec's the producer's header; re-trim on `patchV` only; writes `d6_ref_off.json` with the CL 0.5 consistency difference recorded |
| `d4_extract_endpoint.py` (copied at staging from `curriculum_D4/`) | `ee7d3c99fd716da23779cb651961918e` | D4's, unmodified — reads D4's history for REF_off |

**Zero-compute probe of the image, recorded:** `dafoam-idwarp-rot:v1` `python -c` introspection (no case,
no solve, `--rm`, ~5 s): `DAFoamBuilder.__init__(self, options, mesh_options=None, scenario='aerodynamic',
run_directory='')`; `run_directory` honoured by the mesh, solver and function components (`with cd(...)`
in `dafoam.mphys.mphys_dafoam`); `pyoptsparse 2.10.1`, `openmdao 3.26.0`. **No `assert` carries a guard**
in any python file here (AST count 0 on all six; L-332). **Classifier denials while building D5/D6:** two,
verbatim in D5 Addendum 1 §A1.4; none while writing D6's files, which were authored with the harness's file
tools from the start.

## 8. FREEZE

**Condition, and how it was checked (rule 2):** `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint`
→ **false at 2026-08-26T17:38:57Z**, the final check of `d6_groot5_selftest.sh` (13/13); no `d6_` container
exists but the removed sacrificial one. **This item has burned 0 core-min and started no arm container.**

**Committed BEFORE any container starts.** The grading path is fixed at this commit: `d6_grade.py` md5
`a76a7d5e298a6ba719143f14e10c89bf`, to be verified against its committed blob before grading. **After
first compute the gates are closed**; changes land only as dated addenda that cannot alter a gate,
threshold, cap or label; originals are struck, never rewritten.

**Capability-grid cell (068c2bf0): 3D · steady · subsonic-compressible — verdict this item can move:
optimization converged | gradients FD-verified, from "`GATE REACHED`, G5 `PASS` on the PATCHED row, SHIPPED
row `PENDING`" (`curriculum_D4/RESULTS.md`, C-97; D4-SHIPPED F3 ungraded at this commit) to — honestly — the
same verdict: D6 DEEPENS the cell's evidence (a converged three-point composite optimisation and an
FD-verified composite gradient on the PATCHED row of the same case, plus the off-design reference that
makes single-point dominance measurable) and does NOT move it; the SHIPPED row stays `PENDING` until
D4-SHIPPED grades.** Regime from D4's registered flow, not guessed: `DARhoSimpleFoam`, U∞ = 100 m/s,
T∞ = 300 K → M∞ = 0.288, Spalart–Allmaras RAS (`curriculum_D4/d4_opt_runScript.py:24-35`; D4 run root
`base/constant/turbulenceProperties`); 3D MACH wing (`curriculum_D4/PREREGISTRATION.md` §1).

**Queue entry:** `verification/queue/dafoam/D6_chain.json` — team `dafoam`, `prereg_commit` = this freeze
sha, `launch_cmd` = `bash <abs>/d6_chain_driver.sh O_mp ACC_mp F_mp REF_off`, `cwd` = this case directory,
`ranks 4`, `cost_core_min_estimate 1694.7`, `memory_floor_gb 24.0`, `permission bc0e687e`. Enqueueing is
not authorisation: `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's own, discharged at enqueue.

**Predicted outcome, so it cannot be written afterwards:** P1–P7 as tabled; item `PASS` if P6, P2 and P3
hold and no completion clause fails; the outcome this item is most exposed to is P7 (memory), registered
above as a finding rather than a failure of the run.

---

# ADDENDUM 1 — 2026-08-26 — **PRE-COMPUTE** — `D5-DRIVER-DEF-1` inherited and corrected before this item ever fired

**Version 1.0 → 1.1. Lines whose number changed above this section: 0.** `CLAUDE.md` rule 2, pre-first-compute.

**THE CONDITION, AND HOW IT WAS CHECKED.** `test -e /home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint`
→ **false** (re-checked in the committing invocation, stamp in the commit message); `docker ps -a` carries no
`d6_` name; the queue entry `D6_chain.json` was moved to `held/` at 17:45Z **before the runner's next tick**
so that no fire could occur on the defective driver. **0 core-min; this item has never fired.**

**WHAT MOVED, AND WHY.** D5's first runner fire (17:42:43Z) was refused at zero compute by the launcher's own
G-ROOT.3, because D5's driver wrote its staging metadata on the ledger's `ITEM=` identity line (`D5-DRIVER-DEF-1`,
D5 Addendum 2). `d6_chain_driver.sh` carried the same line by derivation. It now writes `ITEM=D6` alone on line
1 and `STAGED stamp=… base_src=… permission=…` on line 2: md5 **`11dced563a8c4695a2144e6d46862735`** (was
`860b9842…`; the delta is these two `echo` lines and four comment lines; `d6_chain_driver_DELTAS_from_d5.diff`
added, 146 diff lines). The launcher (`98472772…`), the grader (`a76a7d5e…`), every gate, band, cap, label,
cost and prediction are unchanged. The corrected form was shown to pass G-ROOT.3 on D5's staged root
(D5 Addendum 2 control, 17:46:08Z, rc=4 at the digest check, nothing staged); D6's launcher carries the same
G-ROOT.3 bytes.

**Queue.** `D6_chain.json` returns to the drop path citing **the commit that lands this addendum** as `prereg_commit`.
