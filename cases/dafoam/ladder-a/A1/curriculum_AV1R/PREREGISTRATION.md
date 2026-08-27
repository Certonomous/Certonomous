# CURRICULUM AV-1R — np-INVARIANCE of the A1 NACA0012 baseline adjoint gradient (`DASimpleFoam`, 4,032 cells) at np = 1 / 2 / 4 (`scotch`), ON TWO TOOLCHAIN ROWS — SUCCESSOR PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-27**. Lane: dafoam `lab-lane` (C). Supervisor: `dafoam-supervisor`.
**This item is the SUCCESSOR to `curriculum_AV1`, whose frozen comparator REFUSED at G1 and whose verdict is and remains `NOT A RESULT` (`23dccf38`).** AV-1 is not re-graded, not repaired and not superseded as a record; it stands as a documented refusal and this item is a new rung with its own freeze.

**Nothing in this item is filed, sent, emailed, uploaded, registered, posted or commented outside this box, now or ever** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). SUBMISSIONS PARKED. Permission for the detached launch: Sanaa's own words at **`bc0e687e`**. Every decision here is `[lab-attributed]`.

---

## 1. WHY A SUCCESSOR AND NOT A §2d.1 REPAIR — the supervisor's ruling, reproduced so it is not silently re-litigated

**The defect.** `av1_grade.py:73` fixed `DATUM_REF = {a: ("0.orig/U" if a == "MESH" else "0/U") …}` and AV-1's §3 gate text named `0/U`. The NACA0012 incompressible tutorial runs **`writeCompression on`** (`base/system/controlDict:27`), so on a **serial** arm the solver rewrites time 0 back to disk compressed and `0/U` becomes `0/U.gz`; parallel arms write under `processor*/` and never touch it. **The age guard's SUBSTANCE was satisfied on every refused arm** — AV-1 `X1-S` datum `1787838035` against `0/U.gz` at `1787838086`, 51 s newer; `X1-P` datum `1787838366` against `1787838420`, 54 s newer. **Only the reference PATH vanished.** Measured on AV-1's own run root by this lane and recorded in `av1r_datum_control_evidence.txt`: **5 of 7 arms carry `0/U` with mtime == datum, 2 of 7 (the np = 1 arms) carry only `0/U.gz`.** The same defect refused AV-2 on all four of its solver arms, which are np = 1 by registration — **one cause, two items.**

**THE RULING, `[lab-attributed]`: `VERIFICATION_CHARTER.md` §2d.1 IS REFUSED. Re-register as successors.** The supervisor's reasoning, reproduced verbatim in substance at the supervisor's instruction:

> This family has now refused §2d.1 four times on the same ground — **an exception used when the ordinary path is open is an exception being widened.** Here the ordinary path is not merely open, it is **cheap**: AV-1 and AV-2 together spent **28.187 core-min ($0.024 DERIVED)**, so re-registration costs about half an hour of one core to buy back. **An exception that saves $0.02 is not an exception worth having.**

For completeness, §2d.1's four conditions are not reached and are not argued from: the change is not being made under the exception at all. Nothing in AV-1 is edited; `av1_grade.py` is untouched at `0b3ebaa4`.

**WHAT PROTECTS THIS FREEZE, given that AV-1's artefacts exist and are readable.** §2b's protected property is that *the gate could not have been chosen to fit the answer*. **Every band, threshold, verdict rule, control and prediction in this document is carried forward VERBATIM from AV-1's frozen text at `0b3ebaa4`, which was frozen before AV-1's first container started.** No band is new; none could have been fitted to anything. The only substantive change is the datum resolution in §3's G1, and **a datum resolution cannot move a number** — it decides whether the instrument can read at all, and its correctness is established by a DRIVEN CONTROL (§3a) rather than by the answer it produces.

**Disclosed, because it is the honest limit of that argument.** AV-1's `X*/av1_X.json` artefacts are on disk and contain the gradients G-NP compares. **This lane did not open them**, and AV-1's `RESULTS.md` quotes no gradient, no objective and no spread — it quotes the refusal and nothing else. That is a statement about what was read, not a proof that nothing could have been read, and it is recorded as such.

## 2. ARMS — seven, in this order, one detached chain, TWO ROWS — CARRIED FORWARD UNCHANGED

`MESH`, `X1-S`, `X2-S`, `X4-S`, `X1-P`, `X2-P`, `X4-P`. `-S` = SHIPPED `dafoam/opt-packages:latest` (`sha256:9d45679d…5290f07fc`, `libidwarp.so` md5 `f0fcb488e0e98156575cd19548e91663`); `-P` = PATCHED `dafoam-idwarp-rot:v1` (`sha256:2927768a…dee30f6d35`, md5 `85f59e87253e0a71a813f64ca6e4c425`). The mesh is generated once in the SHIPPED image; every solver arm stages a COLD copy of the MESH arm's output. Run root **`/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv`**.

**The case, unchanged.** A1 NACA0012 on its own 4,032-cell mesh, the INCOMPRESSIBLE tutorial (`/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible`, checkout `d3b7e38b`), `DASimpleFoam`, `U0 = 10.0`, `aoa0 = 5.139°`, SA, `primalMinResTol 1e-8`, `adjEqnOption.gmresRelTol 1e-6`; 8 `shape` functions + `patchV`. **`writeCompression on` is left exactly as the tutorial ships it.** Turning it off would hide the defect rather than instrument it, and would change the case under test.

**The planted control (rule 3), carried forward unchanged.** `av1r_x.py` writes `av1r_X.json`, then `av1r_X_planted.json` = the same artefact with `PLANT = 1.234e-03` added to every total, re-reads both from disk through the same reader and exits 2 unless every value moved by exactly PLANT, printing `AV1R_PLANTED_CONTROL_SEEN` — a line the grader requires in every X log. The grader repeats the plant on the np = 2 SHIPPED artefact into `<root>/grader_controls/` and refuses unless it is seen, and grades a **sign-flipped copy of the np = 4 SHIPPED artefact** through the same G-NP function, refusing unless it reads `GATE FAIL` with every component flipped.

## 3. GATES, THRESHOLDS AND LABELS — `av1r_grade.py` — EVERY BAND CARRIED FORWARD VERBATIM FROM `0b3ebaa4`

Vocabulary: `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING` and nothing else.

* **G1 — completion, ARM-KIND AWARE.** Every arm kernel `rc == 0` from `docker inspect .State.ExitCode` (harness/kernel disagreement refuses), `OOMKilled false`, the **age guard** (artefact strictly newer than the arm's own `.av1r_age_datum`), SOLVER arms also needing `AV1R_X_WRITTEN` **and** `AV1R_PLANTED_CONTROL_SEEN` in the arm log; MESH needs `Mesh OK.`. Any clause failing → **`NOT A RESULT`** (exit 2). An arm with no ledger row is read from the launcher's `<ARM>_<stamp>.inspect.txt` with the source named per field and every infrastructure field `NOT_MEASURED`.
* **G1's age-guard datum — THE ONE SUBSTANTIVE CHANGE, stated as a rule and not as a name.**
  1. The **datum FILE** `.av1r_age_datum` is the anchor. It is written by the launcher one `stat` after the stage-time `touch`, and no solver in this ladder writes it. **Its own mtime must date its own recorded epoch to within `DATUM_SELF_TOL_S = 5 s`**, else REFUSE. (Measured on 10 of 10 arms across AV-1 and AV-2: delta **0 s**.) This is what the old `mtime(0/U) == datum` clause was really protecting, moved onto a file the solver cannot legitimately rewrite.
  2. The staged-field reference is resolved **BY EXISTENCE over a registered candidate SET** — `("0/U", "0/U.gz")`, and `("0.orig/U", "0.orig/U.gz")` on MESH — **never by name**. **Exactly one must exist**: none → REFUSE `age_reference_absent`; more than one → REFUSE `age_reference_ambiguous` (two files carry two mtimes and no registered rule says which dates the run). A hard-coded second name would reproduce this defect at the next compression change and is refused as a repair.
  3. The resolved reference must be **no older than** the datum (`age_reference_older_than_datum` otherwise): a staged field cannot predate the stage that touched it. It MAY be newer — that is the compressed rewrite, and it is legitimate.
  4. **`writeCompression` is read from the arm's OWN `system/controlDict` and RECORDED beside the resolution, never gated.** Absent or unparseable → `NOT_MEASURED` (an infrastructure field, L-342), never a refusal. A record that does not carry the setting cannot explain its own datum.
  5. The resolution travels with the verdict as `datum_resolution` in the grade json: candidate set, resolved name, both mtimes, the recorded epoch and the compression setting, per arm.
* **L-342 field classes (`d4d0c29d`):** absent infrastructure → `NOT_MEASURED` beside the verdict, never composed to PASS; present-but-garbage → REFUSE; absent physics → REFUSE. **The age guard remains a PHYSICS field.**
* **G-M2 — mesh identity:** `cells == 4,032` → `PASS`, else `GATE FAIL`.
* **G-NP — the bright line, per ROW, np = 1 as the serial reference, np ∈ {2, 4}:** (a) **objective spread `s_J ≤ 2.2e-5`** for CD and CL (`PARALLEL_GATE_DOCTRINE.md:38, :194-198` @ `fd9bf1b6`); (b) **gradient spread `s_g ≤ 1.0e-3`** against the serial reference for the CD gradient (`shape` + `patchV`, 10 components) and for the CL gradient — 6× the family's measured floor of 1.1–1.7e-4 (B3 `bb5088c4:16-24`), 50× below band D; (c) **0 sign flips** on components with `|g_1,i| ≥ 1e-14`. Any of (a)/(b)/(c) outside → the row is **`GATE FAIL`** with the np and the quantity named. The np = 2 / np = 4 partition record must carry exactly np entries summing to the mesh's cell count, else **`NOT A RESULT`**; an artefact whose `nprocs` differs from the arm's registered ranks refuses.
* **G9 — toolchain per row:** ledger `DIGEST`, the container's `D4S_IDWARP_SO_MD5:` print and the artefact's in-process `libidwarp.so` md5 must all name the row's toolchain. Mismatch → `GATE FAIL`.
* **G10 — caps (§4):** every arm `core_min ≤ cap`, sum ≤ **95.0**; a crossing is `GATE FAIL`.
* **G11 — OOM hard:** `OOMKilled true` is a G1 refusal, never a re-fire.
* **G12 — placement:** `cpuset` equals the registered one PER ARM (`0,1` at np ≤ 2; `0,1,12,15` at np = 4); delivered cores ≥ 0.75 × ranks where measured, `NOT_MEASURED` disclosed otherwise.
* **DIVERGENCE** shipped-vs-patched on the np = 1 CD gradient is **reported per component with its number**, never gated.
* **Item verdict (composition registered here):** any refusal → **`NOT A RESULT`**; else any of G-M2/G9/G10/G12 or any row `GATE FAIL` → **`GATE FAIL`**; else **`PASS`**. No grid family exists, so standing rule 5 has no row and **NO GCI IS QUOTED**. No FD table exists, so **no FD verdict is quoted**.

### 3a. THE DRIVEN CONTROL ON THE RELAXED GUARD — a guard relaxed without a control showing it can still fire is a guard RETIRED, not repaired

Seven selftest units (`UD1`–`UD7`) drive the change, and the grader refuses to report a pass unless all of them run — the frozen `EXPECTED_UNITS` is raised from 24 to **31** so the count itself is a gate. Evidence: `av1r_grade_selftest_evidence.txt`, **31/31 under `python3` and 31/31 under `python3 -O`, `ast.Assert` count 0**.

| unit | what it drives | required outcome |
|---|---|---|
| UD1 | every solver arm carrying **only** `0/U.gz` — the exact shape that refused AV-1 | grades; no refusal |
| UD2 | the resolution is recorded and names `0/U.gz`, with its candidate set | recorded |
| UD3 | `writeCompression` read from the arm's own `controlDict` | recorded `on`, never gated |
| **UD4** | **NEITHER candidate on disk** | **REFUSE `age_reference_absent`** |
| UD5 | BOTH candidates on disk | REFUSE `age_reference_ambiguous` |
| UD6 | datum content back-dated 60 s against its own mtime | REFUSE `age_datum_self_inconsistent` |
| UD7 | resolved reference older than the datum | REFUSE `age_reference_older_than_datum` |

**UD4 is the control that matters** and it is the one this item would be dishonest without.

**Additionally, driven against the REAL artefacts** (`av1r_datum_control.py`, a pre-compute diagnostic that grades nothing, reads no artefact, quotes no band and reaches no verdict): the successor grader's own `resolve_datum_ref` and `read_write_compression` are called on AV-1's run root — **7 of 7 arms resolve, 5 by `0/U` and 2 by `0/U.gz`, self-delta 0 s on every arm** — and then on a planted directory with neither candidate, where the guard **fires**, and on the same directory with `0/U.gz` planted, where the resolver **sees it**. Recorded in `av1r_datum_control_evidence.txt`. **This does not grade AV-1 and AV-1 remains `NOT A RESULT`.**

## 4. COST — DERIVED FROM NAMED ANCHORS, NOT MEASURED — carried forward, with AV-1's own measurement as a new anchor

Anchors: **C-31** (D1-C′, cold primal + adjoint on this mesh at np = 1, SHIPPED: 1.483 core-min measured), **C-71**, **C-135**, and now **AV-1's own ledger**, which is a measurement of these very arms: MESH 0.167, X1-S 1.017, X2-S 1.367, X4-S 2.067 core-min and the three PATCHED arms alongside, **9.102 core-min for the seven arms**. The registered point is **left at AV-1's 19.3** rather than moved to the measured 9.1 — **the estimate is not tuned to a measurement taken after the freeze it belongs to**; the gap is a calibration finding, not a band, and it will be reported as one.

| arm | derivation | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| MESH | C-135 scaled to 4,032 cells + container start | **0.3** | 5.0 | 300 s (1 rank) | 4g |
| X1-S, X1-P | C-31 + a CL adjoint | **2.5** each | 10.0 each | 600 s (1 rank) | 4g |
| X2-S, X2-P | X1 at efficiency 0.8 | **3.0** each | 15.0 each | 450 s (2 ranks) | 4g |
| X4-S, X4-P | X1 at efficiency 0.6 | **4.0** each | 20.0 each | 300 s (4 ranks) | 6g |
| grader | zero compute | 0 | — | — | — |
| **total** | | **19.3** point, band **[10, 50]** | **ceiling 95.0 = Σ caps** | | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED**: point **$0.0165**, ceiling **$0.0812**. An overrun **stops the run**; it does not get a new budget. **A calibration row is owed at completion** (rule 12) and it must compare against **both** the 19.3 point and AV-1's measured 9.102.

**Already spent on this item before the freeze: 0.000 core-min of solver time.** The G-ROOT.5 selftest fired two sacrificial `sleep` containers pinned to `--cpus=0.1 --cpuset-cpus=1` for a few seconds each; that is instrument time, is not a solve, and is named here rather than absorbed.

## 5. PLACEMENT, MEMORY AND THE DETACHED FORM — carried forward unchanged

`cpuset 0,1` for every arm at np ≤ 2 and `0,1,12,15` for the two np = 4 arms; memory `4g` (`6g` at np = 4) with `--memory-swap` equal and `--oom-score-adj=500`; one detached chain driver runs the seven arms in order; per-arm in-container `timeout -k 60`; the windowed H5 memory gate before each arm; rc is read from `docker inspect .State.ExitCode`, never from the `setsid` parent.

## 6. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted — CARRIED FORWARD VERBATIM FROM `0b3ebaa4`

| # | prediction | value / band | falsifier |
|---|---|---|---|
| **P1** | the PATCHED row is np-invariant: G-NP `PASS` at np = 2 and np = 4 inside the band | `s_g ≤ 1e-3`, `s_J ≤ 2.2e-5`, 0 flips; point `s_g ≈ 1–2e-4` | MISS = a decomposition-dependent gradient on the patched toolchain on this mesh |
| **P2** | the SHIPPED row is np-invariant the same way | as P1 | MISS = the same on the shipped toolchain; a P1 HIT / P2 MISS pair locates the dependence in the shipped IDWarp |
| **P3** | the objective is **not bit-identical** across np but inside the 2.2e-5 band | `0 < max s_J ≤ 2.2e-5`, point ~1e-7 | MISS if every arm reproduces the serial CD and CL to the bit, or if any spread exceeds the band |
| **P4** | np = 4 SHIPPED core-minutes are **1.0–3.0×** the np = 1 arm's | ratio in `[1.0, 3.0]`, point 1.6 | MISS outside |
| **P5** | total graded core-min in **[10, 50]** (point 19.3) | scored on the ledger | |
| **P6** | MESH wall ≤ 120 s | scored | |
| **P7** | the MESH arm reproduces A1's mesh | `cells == 4,032` | |

**Two predictions ADDED for the successor, both about things AV-1 could not answer because it refused before reading anything:**

| # | prediction | value / band | falsifier |
|---|---|---|---|
| **P8** | **the datum resolves without a refusal on all seven arms**, and names `0/U.gz` on exactly the two np = 1 arms and `0/U` on the four np > 1 arms and `0.orig/U` on MESH | `datum_resolution` in the grade json | MISS = any other split, which would mean the compression behaviour is not what §1 measured |
| **P9** | `writeCompression` reads **`on`** on all seven arms | recorded, never gated | MISS = the staged case is not the tutorial's |

**P8 and P9 are about the instrument, not about the physics, and they are labelled as such.** Neither can move G-NP; both would be `NOT_MEASURED` under the old grader, which is the point.

**The falsifier registered up front:** a P1 or P2 MISS is the finding this rung exists to be able to make. Either outcome enters `ADJOINT_VERIFICATION_STANDARD.md` §3's status line with its number.

## 7. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT

| file | md5 | derivation |
|---|---|---|
| `av1r_grade.py` | `b5c1d0092c6d2a2608ad3cc0899ed0fd` | AV-1's grader, renamed, + the §3 datum delta and UD1–UD7 |
| `av1r_run_arm.sh` | `4ce916895994ab87b458a3e5fab2de01` | AV-1's launcher, renamed, + the md5 pins that follow |
| `av1r_chain_driver.sh` | `0f24df6857bb1fe5969a9b5511a85ad8` | AV-1's driver, renamed, + the md5 pins |
| `av1r_x.py` | `7313bab8b15629c9d872a39d0654aa08` | AV-1's instrument, renamed only |
| `av1r_runScript.py` | `0557da51f6f179f6de865144343c499f` | byte copy of the shipped tutorial `runScript.py` — **unchanged by the rename** |
| `av1r_decomposeParDict_np2` | `68ecc827562886fb43c3aedb0627b344` | unchanged by the rename |
| `av1r_decomposeParDict_np4` | `816f5ba44075fde47fa5db4269877bc8` | the tutorial's own; unchanged by the rename |
| `av1r_groot5_selftest.sh` | `1cad80bb16eec8a6616d0bfb9f6bb660` | renamed only |
| `av1r_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | unchanged by the rename |
| `av1r_datum_control.py` | `5e714767e65ea93b893f44f6d7381274` | **NEW** — a pre-compute diagnostic, **not on the grading path** |

**How to audit this in two reads.** `AV1R_RENAME_MANIFEST.txt` records the mechanical step — every file read from the **HEAD blob** of `curriculum_AV1/` (never from the working tree, L-350) and passed through exactly `sed 's/AV1/AV1R/g; s/av1/av1r/g'` — with the md5 before, after the rename, and final, so a reader can see which files the rename alone accounts for. The three `*_DELTAS_from_av1.diff` files then show the substantive delta **against the renamed original**, so the rename does not appear in them: **208 / 14 / 19 lines**.

**G-ROOT.1–.5 driven from birth:** `av1r_groot5_selftest_evidence.txt`, **19 pass / 0 fail**, against a sacrificial live container, a live sacrificial pid, a stale pidfile, five foreign run roots, and G-ROW on both real images — with the run root asserted **ABSENT before and after**. **No `assert` carries a guard** in any python file here (AST count 0, counted by the grader; L-332). **Classifier denials in this lane while building AV-1R: none.**

## 8. WHAT THIS ITEM WILL NOT ESTABLISH

It carries **no FD table**, so it moves **no capability-grid verdict** on its own and no band D reading. It grades the adjoint against itself across rank counts. It says nothing about an optimiser, about grid convergence (one mesh, no GCI), about 3D, or about any Mach number. **A wrong treatment could still pass G-NP by producing the same wrong gradient at every np** — which is why this rung is not an FD verdict, and the frozen text says so before the run. It does not re-grade AV-1 and it does not convert AV-1's `NOT A RESULT` into anything else.

## 9. FREEZE AND QUEUE

**Committed BEFORE any container starts** (rule 2). **Freeze condition, checked and not assumed:** the run root `/home/ubuntu/certonomous-runs/CURRICULUM-AV1R-a1-naca0012-npinv` **does not exist** — asserted by the G-ROOT.5 selftest before and after its own run (`av1r_groot5_selftest_evidence.txt`, both lines), and 0.000 core-min of solver time has been spent in this tree.

The grading path is fixed at this commit: `av1r_grade.py` md5 `b5c1d0092c6d2a2608ad3cc0899ed0fd`, asserted by the chain driver before staging and again before the grade.

**NOT QUEUED BY THIS LANE.** No entry has been written to `verification/queue/dafoam/`, and the drop path is a launch button. **Enqueueing is the supervisor's act**, and `SUPERVISION_CHARTER.md` §3 check 4 — pre-registration committed before compute — is the supervisor's own and is discharged on this sha. The entry, when the supervisor chooses to write it, is: team `dafoam`, `prereg_commit` = the sha of the commit introducing this file, `launch_cmd` = `["bash", "<abs>/av1r_chain_driver.sh", "MESH", "X1-S", "X2-S", "X4-S", "X1-P", "X2-P", "X4-P"]`, `cwd` = this directory, `ranks 4`, `cost_core_min_estimate 19.3`, `cap_core_min_registered 95.0`, `memory_floor_gb 8.0`, `cost_basis` derived / not measured, `permission bc0e687e`.

**Predicted outcome, written here so it cannot be written afterwards:** P1–P9 HIT; both rows `PASS`; item **`PASS`**; `ADJOINT_VERIFICATION_STANDARD.md` §3's status line gains its first banded measurement; no grid cell moves.
