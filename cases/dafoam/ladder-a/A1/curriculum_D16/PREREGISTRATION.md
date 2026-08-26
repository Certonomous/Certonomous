# CURRICULUM D16 — NACA0012 at TRANSONIC conditions (`DARhoSimpleCFoam`, M ≈ 0.69): the BASELINE adjoint gradient of CD (and the CL constraint gradient) FD-VERIFIED on TWO TOOLCHAIN ROWS — PRE-REGISTRATION

**Version 1.0. FROZEN.** Dated **2026-08-26**. Lane: dafoam `lab-lane` (N). Supervisor: `dafoam-supervisor` (FOURTEENTH session §3, lane N). **This document is `curriculum_D15/PREREGISTRATION.md` with the registered deltas of §7 and nothing else inherited silently: where a number here disagrees with D15's text for a clause this document does not list as a delta, D15's text wins and this document is defective.** Permission: **`bc0e687e`**; queue-first `7def3c6b` / `73eccb1b` / `0b041d1a`; L-342 `d4d0c29d`; grid `068c2bf0`; `3c3ef86c`. `[lab-attributed]`. Nothing here is filed, sent or posted (rule 7; `DAFOAM_CHARTER.md` §10).

> **ID-NAMESPACE WARNING.** `cases/dafoam/EXPERTISE_CURRICULUM.md:75` names a candidate set "D1–D16"; `grep -n '^| \*\*D16\*\*'` finds **no D16 table row** in that file, and `docs/DOCKET.md` carries fleet-defect rows D5/D6/D14/D15 (different objects). **This item is the dafoam CURRICULUM CASE `D16`**, confirmed free by `ls cases/dafoam/ladder-a/A1/`, `cases/dafoam/INDEX.md` and `grep -rn curriculum_D16` (none) at 2026-08-26T20:5xZ, and assigned by the supervisor's dispatch. No document in this family cites a bare `D16` without saying which.

---

## 0. SCOPE, AND THE CAPABILITY-GRID CELL THIS ITEM CAN MOVE

**Cell (`068c2bf0`; `docs/capability/dafoam_GRID.md` @ `6fcfe713`): `2D · steady · transonic`, column "gradients computed + FD-verified" — today `CAN NOT DO — not attempted`.** Regime derived from the case's registered conditions: `d16_runScript.py:31-36,44,72-73` (`U0 = 238.0`, `p0 = 101325`, `T0 = 300.0`, `aoa0 = 3.0`, `solverName = "DARhoSimpleCFoam"`, `"transonicPCOption": 1` — the live value for this solver, L-40 / `DAResidualRhoSimpleCFoam.C:173`); `a = 347.2 m/s` → **M∞ = 0.685**, the tutorial DAFoam ships under the name `transonic` (a supercritical-airfoil regime on a NACA0012 at 3°, where the upper surface goes locally supersonic; whether a shock forms on this coarse mesh is a measurement, P3's band is wide for that reason). Spalart–Allmaras; 2D by the two symmetry planes. **Only the gradient column moves**; no optimiser runs.

**Tutorial location, images, mesh:** exactly as D15 §0 — the tutorial is on the host at `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/transonic` (git `d3b7e38b`), NOT in either image; `genAirFoilMesh.py`, the profiles and `FFD/wingFFD.xyz` are **byte-identical** to the incompressible and subsonic tutorials' (md5s in §7), so the MESH arm regenerates A1's **4,032-cell** mesh and the same 8 `shape` functions + `patchV`. What differs from D15 is the physics only: `DARhoSimpleCFoam` (the compressible solver with the transonic preconditioner), unbounded `Gauss` divergence schemes with `div(phid,p) limitedLinear 1.0` (`system/fvSchemes`), `U0 = 238` at `aoa0 = 3°`, and initial turbulence fields scaled for the higher speed.

## 1. THE AMENDMENT CONDITION, AND HOW IT WAS CHECKED

> **The run root `/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic` DOES NOT EXIST.**

`test -e` → false at **2026-08-26T20:56:01Z** and again as the last leg of `d16_groot5_selftest.sh` at **2026-08-26T21:08:32Z** (`d16_groot5_selftest_evidence.txt`, 18/18). **0 core-min; no arm container has started.** After the first container, gates are **CLOSED**.

## 2. ARMS — as D15 §2, with these values

Chain `d16_chain_driver.sh MESH X-S F-S X-P F-P`; arms MESH (SCRIPT, SHIPPED, 1 rank), X-S / F-S (SOLVER, SHIPPED, 2 ranks), X-P / F-P (SOLVER, PATCHED, 2 ranks); ONE mesh generated once in the SHIPPED image; G-ROW from the arm suffix; **two rows or it is not a verdict**. The instrument `d16_xf.py` is `d15_xf.py` re-pointed at the transonic producer (`d16_runScript.py`, md5 `420cf2e79aaabe7d67b4701bbb99a314`); **the FD design is D15's, unchanged:** components `shape[0]`, `shape[3]`, `shape[6]`, `shape[7]`, `patchV[1]` + the `CTRL` planted-zero control; steps `shape` {1e-2, 1e-3, 1e-4}, `patchV[1]` {1e-1, 1e-2, 1e-3} degrees; 32 primals per F arm; middle-step reference; the CTRL row and its planted twin re-read from disk by the instrument and by the grader (D15 §2, verbatim).

## 3. GATES, THRESHOLDS AND LABELS — `d16_grade.py`

**Every gate, band, label and composition rule is D15 §3, verbatim, with these three registered value changes and no other:** G10 caps sum ≤ **245.0**; G12 `cpuset == 4,14`; the item string. In particular: G1 arm-kind-aware completion with the age guard and the `.inspect.txt` fallback; L-342 field classes; G-M2 `cells == 4,032`; **G5 band D 5.0 % per component with the sign-flip rule, band E 5.0 % aggregate, plateau 10 %, ≥ 3 graded components** — `curriculum_D4/PREREGISTRATION.md:82`, `curriculum_D7FR/PREREGISTRATION.md:228-229`, cited not re-derived; G5c on CL; **G6 dot-product/duality NOT MEASURED, named**; G9 two `.so` md5s (`f0fcb488…` / `85f59e87…`) and two digests; G11 OOM hard at 4g; divergence reported with its number; no GCI. The grader's selftest is D15's with the D16 constants: **22/22 under `python3` and `python3 -O`** (`d16_grade_selftest_evidence.txt`).

## 4. COST — DERIVED FROM NAMED ANCHORS, NOT MEASURED

The anchors are D15 §4's (**C-31, C-71, C-24, C-135**, `curriculum_D7FR/RESULTS.md:36`). For the transonic solver the D7FR cell-scaled figures apply **directly** (same solver class, `DARhoSimpleCFoam`, M 0.84 there): **0.32 core-min per primal at 4,032 cells**; an adjoint scaled linearly from D7FR's 45 core-min at 42,120 cells gives 4.3 per adjoint, which **overstates** at this size (GMRES iteration counts fall with the system size; D1-C′ measured a whole primal + adjoint at 1.48 on this mesh incompressible) — the X point is set between those readings and the cap at the linear figure.

| arm | derivation | point (core-min) | cap (core-min) | in-container wall | mem |
|---|---|---|---|---|---|
| MESH | as D15 | **0.3** | 5.0 | 300 s (1 rank) | 4g |
| X-S, X-P | cold primal ≈ 0.6 + two adjoints (CD, CL) ≈ 2 × 2.2 + colouring ≈ 1 | **6.0** each | 30.0 each | 900 s (2 ranks) | 4g |
| F-S, F-P | 32 primals × 0.32 + colouring/setup ≈ 3.8 | **14.0** each | 90.0 each | 2,700 s (2 ranks) | 4g |
| **total** | | **40.3** point, band **[15, 120]** | **ceiling 245.0 = Σ caps** | ≈ 30 min wall at the point, ≈ 125 min at the caps (+ H5 windows) | |

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5). Dollars **DERIVED**: point **$0.0345**, ceiling **$0.2095**. Cap mode as D15 §4 (deadline inside the container; the runner's `CAP_OVERRUN.txt` at 1.10 × 40.3 × 60 / 2 = 1,330 s is report-only and expected). **Exposure stated:** a transonic primal on this coarse mesh may converge more slowly to `primalMinResTol 1e-8` than the M6 anchor's per-cell rate implies (shock/limiter interaction); the F caps carry 6.4× the point for that reason, and a cap-stop is `NOT A RESULT` on that arm, never a re-budget. Calibration row owed at completion.

## 5. PLACEMENT, MEMORY AND THE DETACHED FORM

As D15 §5 with **cpuset `4,14`** (the supervisor's placement; disjoint from D15 `2,3`, D5 `8,10,11,13`, D4-SHIPPED `5,6,7,9`, W2R `12`; not core 0; the same D6 `2,3,4,14` collision disclosed), 4g per arm, H5 floor 8.0 GiB, aggregate wait-and-retry < 30.6 GiB, the detached driver with `STATUS.<arm>` / `STATUS.chain` / `d16_driver.pid`, no `--rm`, the `.inspect.txt` kernel record, and G-ROOT.1–.5 from birth — the forbidden list names **D15's** root in place of D16's. **G-ROOT.5 DEMONSTRATED 2026-08-26T21:08:2xZ (`d16_groot5_selftest_evidence.txt`, 18/18):** sacrificial `sleep` container on cpuset 14 → `rc=3`; sacrificial live pid with cwd = run root → `rc=3`; stale pidfile ignored; clear passes to the L-251 check; D4/D5/D13/**D15** roots refuse at G-ROOT.1; G-ROW refuses `X-P` on shipped and `MESH` on patched, passes `X-S` on shipped which then refuses for want of `MESH/`; root empty and absent afterwards. Run-root staging as D15 (from the `transonic` checkout; six tutorial inputs md5-asserted; `d16_decomposeParDict` overlay).

## 6. PREDICTIONS — scored HIT/MISS by the comparator, never adjusted

| # | prediction | value / band |
|---|---|---|
| **P1** | MESH reproduces A1's mesh | **cells == 4,032** |
| **P2** | baseline `CL` at `aoa = 3°`, M 0.69 (0.11/deg × 3 × 1/√(1−M²) = 1.37 → 0.45, minus the coarse-mesh/shock loss) | **[0.30, 0.60]**, point 0.42 |
| **P3** | baseline `CD` (wave-drag onset possible at this M on the upper surface; coarse mesh) | **[0.012, 0.045]**, point 0.025 |
| **P4** | the PATCHED row G5 (CD) `PASS` with **≥ 4 of 5** in band D | point 5/5, worst ≤ 2 % (D7FR's transonic worst 1.959 %) |
| **P5** | the SHIPPED row's `shape[6]` (LE function, A1's idx6 class) **outside band D or sign-flipped** — the same geometric defect as D15 P5, now at M 0.69; hence SHIPPED `GATE FAIL`, item `GATE FAIL`, cell → `CAN DO, CAVEATS` | HIT / MISS / `NOT_MEASURED` as D15 |
| **P6** | total graded core-min in **[15, 120]** (point 40.3); MESH wall ≤ 120 s | both scored |

**Registered falsifier and the cross-item reading:** D15 P5 and D16 P5 are the same claim at two Mach numbers. **HIT/HIT** = the rotation defect reaches the baseline gradient independent of regime (the geometric reading); **MISS/MISS** = the shipped row passes at the baseline in both compressible regimes, contradicting the incompressible A1 record at the same design point — a finding about the regime dependence of the defect, not a defect of the items; a **split** is reported as a split with both numbers, never averaged.

## 7. INSTRUMENTS, FROZEN BY MD5 AT THIS COMMIT — copy-and-delta from D15 (itself from D14/D5)

| file | md5 | derivation, and the DELTAS file the supervisor reads |
|---|---|---|
| `d16_run_arm.sh` | `bf29bd90700eebfb37bf01ff5300fa74` | `curriculum_D15/d15_run_arm.sh` (`796a2de5…`) + **`d16_run_arm_DELTAS_from_d15.diff` (221 diff lines)**: item/root names; the transonic checkout path; cpuset `4,14`; cap table (X 30.0, F 90.0); producer md5 `420cf2e7…`; D15's root forbidden in place of D16's; header lineage |
| `d16_chain_driver.sh` | `3214efed8415f6bad5496fc275ecad14` | `curriculum_D15/d15_chain_driver.sh` (`4656f1a0…`) + **`d16_chain_driver_DELTAS_from_d15.diff` (155 lines)**: names/root; `TUT_SRC = …/transonic`; the transonic `runScript.py` md5; launcher/grader/instrument md5s |
| `d16_xf.py` | `c78eaaaabe1b4afb0bd74270843ddf77` | `curriculum_D15/d15_xf.py` (`8a664a97…`) + **`d16_xf_DELTAS_from_d15.diff` (133 lines)**: `ITEM`, `PRODUCER_MD5`, artefact/marker names (`d16_*`, `D16_*`), header text. Step set, components, CTRL control, emit/fsync: unchanged |
| `d16_grade.py` | `0b8338b3e483548da3515e79da28762a` | `curriculum_D15/d15_grade.py` (`b429ec89…`) + **`d16_grade_DELTAS_from_d15.diff` (190 lines)**: item/root/artefact names; `CAPS`, `ITEM_CEILING_CORE_MIN = 245.0`, `PREDICTED_CORE_MIN`; `CPUSET_REGISTERED = "4,14"`; P2/P3/P6 bands; the cell string; the three selftest units that carry a constant (U13 91 > 90, U14 cpuset `2,3`). Bands D/E, plateau, sign-flip rule, field classes, `EXPECTED_UNITS = 22`: unchanged. **22/22 plain and `-O`** |
| `d16_groot5_selftest.sh` | `bf2f4aa87f2b604c310903fa1b5f07dc` | `curriculum_D15/d15_groot5_selftest.sh` + **`d16_groot5_selftest_DELTAS_from_d15.diff` (93 lines)**: names; sacrificial cpuset 14; D15's root in (d) |
| `d16_aggregate_memory.py` | `709ab0b98ef0302a3a3a318588f9493f` | byte-identical to D15's / D5's / D14-M's |
| `d16_runScript.py` | `420cf2e79aaabe7d67b4701bbb99a314` | **byte copy** of `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/transonic/runScript.py` |
| `d16_decomposeParDict` | `68ecc827562886fb43c3aedb0627b344` | identical to D15's (the tutorials' `decomposeParDict` files are identical; `numberOfSubdomains 2`) |
| tutorial inputs, md5-asserted at staging | `genAirFoilMesh.py` `681f1065…`, `preProcessing.sh` `e25c8f8c…`, `NACA0012PS.profile` `51dfed28…`, `NACA0012SS.profile` `4a6b8ef4…`, `FFD/wingFFD.xyz` `6ddf378b…` | identical bytes to the incompressible and subsonic tutorials' |

No `assert` in any python file (AST count 0, counted by the grader). Classifier denials while building: none.

## 8. WHAT THIS ITEM WILL NOT ESTABLISH

D15 §8 verbatim, plus: nothing about the shock's position or strength (no Cp is graded; `CD` is one number on a coarse mesh); nothing about `transonicPCOption` beyond running the tutorial's own live value; nothing about M 0.84 (that is the M6 family, 3D).

## 9. FREEZE AND QUEUE

**Committed BEFORE any container starts.** Grading path fixed at this commit: `d16_grade.py` md5 `0b8338b3e483548da3515e79da28762a`. **Queue entry `verification/queue/dafoam/D16_chain.json`:** team `dafoam`, `prereg_commit` = the sha of the commit introducing this file, `launch_cmd` = `["bash", "<abs>/d16_chain_driver.sh", "MESH", "X-S", "F-S", "X-P", "F-P"]`, `cwd` = this directory, `ranks 2`, `cost_core_min_estimate 40.3`, `memory_floor_gb 8.0`, `cost_basis` derived / not measured, `permission bc0e687e`. Enqueueing is not authorisation (check 4 is the supervisor's). **Predicted outcome:** P1–P4, P6 HIT; P5 HIT → SHIPPED `GATE FAIL`, PATCHED `PASS`, item **`GATE FAIL`**; the `2D · steady · transonic` gradient cell moves from `CAN NOT DO — not attempted` to `CAN DO, CAVEATS`.
