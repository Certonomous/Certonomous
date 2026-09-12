# 3D CASE INVENTORY — WHAT IS SHOOTABLE, 2026-09-12

**Written 2026-09-12T17:5xZ by an inventory `lab-lane` for the chief, at Sanaa's order.**
**READ-ONLY PRODUCT. Nothing was launched, killed, edited or committed to produce it.**
Not committed. Not filed. Not sent.

**Her ask, verbatim:** *"I want to have the full list of what was completed (3D), what was
running, what was getting fixed, whats the progress on each (any 3D case), across all teams
so i know what could be ready for shooting"*.

## How "3D" was decided — the load-bearing check

Every row's dimensionality was read from the case's **own `constant/polyMesh/boundary` file on
disk**, not from its name, its prose or anybody's board. A case is **3D** here only if that file
carries **zero `empty` and zero `wedge` patches**. Cases carrying either are listed in the
"NOT 3D" line at the foot with the patch type that excluded them — several of them are cases the
lab has been calling 3D in conversation, including one that was filmed as a demo act.

**Clock context:** the box went down at **~17:36Z** (uptime at the 17:48Z reading was 872 s, and
the process table holds **no solver of any kind** — only `queue_runner.py`). **Every run in the
"running at the stop" column is now dead.** None of them wrote an `End` line, so none of them is
complete under rule 4. A parallel lane is doing the checkpoint census
(`docs/RESIZE_CENSUS_2026-09-12.md`); this document does not duplicate it.

---

## THE TABLE — every genuinely 3D case in the lab

| case (what it physically is) | team | P1: one healthy completed run in band, saved? | P2: grid triple | verdict word on record + artifact | running at 17:36Z stop | being fixed | renders on disk? | SHOOTABLE NOW? | next step |
|---|---|---|---|---|---|---|---|---|---|
| **T18_CU** — transient conduction in a solid copper cube, Bi=1, Fo=0.2 | heat-transfer | **YES — `T18_CU_f`, 512,000 cells (80³).** G1 0.6176037 in [0.6175588, 0.6176205]; G2 0.8591831 in [0.8588990, 0.8593286]; G3 0.5815193 in [0.5812706, 0.5816194] | **CONVERGING ×3**, 8,000/64,000/512,000 (r=2, refined in all three directions), p ≈ 1.9996 / 2.0006 / 2.0130, GCI 0.0021 % / 0.010 % / 0.015 % at Fs 1.25 | **`PASS` ×3** — `verification/runs/T-family/T18_runs/gate_t18.json` (`dim: 3`). Registered ceiling in that same file is `GATE REACHED at best` because the reference is exact | nothing | nothing open | **YES** — `docs/campaigns/T-family/demo/figures_T18/` (6 PNG: full cube mirrored, front march, centreline profile, graded rows) + `render_T18_paraview/render_t18.py` | **YES** | film it |
| **VMFL078** — lid-driven 3D cavity, half-cube with a symmetry plane (Ansys VM2026R1 pp. 223-224) | ansys-verification | **YES — L3, 1,048,576 cells.** J = 0.1825063. **PASS is unavailable by construction, registered before compute**: the manual prints only Figure .78.2, no scalar | **CONVERGING**, 16,384/131,072/1,048,576, R = 0.3798, **p = 1.3966**, **GCI_fine = 1.9911 %** ≤ 5 % | **`GATE REACHED`** — `verification/runs/ansys_verification/VMFL078/GRADE_VMFL078.json` (`row_verdict`). limb A `PASS`, limb B `BLOCKED` (no printed reference) | nothing (its **R2** successor was, see next row) | nothing open | **YES** — `docs/ansys_verification/demo/VMFL078/` (`VMFL078_L3_mesh_*.png`, `VMFL078_geometry_*.png`) | **YES** | append its register row (it is **not yet in** `ANSYS_VALIDATION_REGISTER.md`, whose last row is #80) and film |
| **K2bU3R3_D59** — DC room, four racks, open row ends, h = 59 mm, 3D transient | heat-transfer | **YES — single level, 137,000 cells.** Final-window p2p **0.6058 K**, preceding-window ratio **0.420** against the ≤ 0.5 DAMPS arm | **No triple — single level by registration.** Planted-zero control PASSES with a demonstrated floor of 1.234e-03 K, 81× below the 0.1 K DAMPS floor | **`GATE REACHED`** — `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59/K2bU3R3_GRADE.txt` ("DAMPS") | nothing | nothing open | **YES** — `docs/campaigns/F14-cooling-ladder/demo/figures_K2bU3R3/` (mesh, open row ends, recirculation, rack inlet series, gate) | **YES** | film it |
| **F25_DUCT3D** — fully-developed laminar flow in a 3D square duct, exact series solution | cfd | **YES — fine, 2,097,152 cells.** E2 profile 7.4215e-04 in [2.4738e-04, 2.2265e-03]; f·Re 56.85474 in [56.74760, 57.06902] | **CONVERGING ×2**, 32,768/262,144/2,097,152, p = 1.9529 and 1.9698 | **`PASS` ×2** — `verification/runs/F25_DUCT3D_runs/F25_GRADED.json` (`rows[].verdict`) | nothing | nothing open | **YES, one PNG** — `docs/campaigns/navier_class/F25_DUCT3D/demo/F25_DUCT3D_fine_surface.png` (ParaView, 131,072 faces rendered == 131,072 in the boundary file, measured) | **YES** (thin — one surface view, no mesh-detail set) | film it, or add a mesh-detail render first |
| **A3GC — ONERA M6 primal grid family** (AR1 / AR1C anchors, L1 / L2 / L2R / L3) | dafoam | **PARTLY — the ANCHORS completed, not a graded level.** `A3GC-AR1` rc=0 at Time 6000, CD 0.0230030, CL 0.313116; `A3GC-AR1C` rc=0 at 6000, CD 0.0229853, CL 0.313089. **No band is claimed for them** | **NOT REACHABLE — the triple is structurally invalid.** `genWingMesh.py` varies only `N` while the prereg pins `s0`=1e-4 and `marchDist`=12.0, so wall-normal growth differs: **r = 2.0880 (L3) / 1.4006 (L2) / 1.1674 (ref)**. An order across meshes whose stretching varies 1.8× is meaningless | **L3 `NOT A RESULT`** (`39e299af8`); **L2 `PENDING`**, registered before it landed as predicted-to-miss. Run roots `/home/ubuntu/certonomous-runs/A3GC-L3`, `.../A3GC-L2` (rc=1 at Time 1200) | **`A3GC-L2R`** — `primal.log` at **Time 400 of 6000**, CD 0.0208374, CL 0.326634 | **A3GC-R2 registration**: hold N fixed, refine the SURFACE — one growth ratio and one first-cell height per level, y+ preserved, targeted to land a lawful triple cheaply. **Not frozen** | **YES, the best set in the lab** — `docs/dafoam/renders/A3GC-AR1/` (6 PNG: planform, surface mesh oblique, LE mesh, BL mesh at η=0.65, BL zoom at LE, domain extent) + `_margin_audit.json` | **PARTIAL** — a completed 3D wing primal with excellent renders, but **no band and no lawful triple** | freeze A3GC-R2 and run the cheap surface-refined family |
| **K2f / K2g rack** (K2f_L1 / L2 / L3, 58,368 / 196,992 / 664,848 cells) | heat-transfer | **PARTLY — L1 and L2 both DONE** under rule 4, cell ratio **3.37500** dead inside the registered [3.2063, 3.5438], 13.267 + 64.000 core-min | **NOT YET — 2 of 3 levels complete.** L3 was mid-flight at the stop | rung K2d/K2f closed **`BLOCKED`**; **K2g registered `b456d1107`**, gate = module pressure drop (L1 27.189119 → L2 27.729680, +1.988 %, the one quantity of 23 that moves with the mesh by more than its own iteration noise) | **`K2f_L3`** — `verification/runs/F14-cooling-ladder/K2g_runs/K2f_L3/log.solve` at **Time 835 of 2000** | K2d/K2f both registered gates on quantities with **no signal on this geometry** (θ_max 4.876e-05 at L1 vs 4.678e-05 at L2) — successor may not rest its gate on `T_in` or θ; **applied in K2g's registration** | NO | **PARTIAL** | relaunch K2f_L3 (it had cleared the permission block and was 42 % in), then grade the triple |
| **MRF impeller R2** — Rushton turbine in a baffled stirred tank, power number Np | cfd | **YES on the band, NO on the verdict.** Fine, 2,418,780 cells, Np = 4.381719 inside the registered [4, 6] → `band_verdict: PASS`. All three levels rc=0 at endTime 8000 | **DIVERGENT.** 154,715/601,696/2,418,780; observed order **−0.2971**; fine level **NOT_CONVERGED** iteratively. No GCI quoted (values not monotone at 4000 either, order −5.778) | **`NOT A RESULT`** — `verification/runs/navier_class/MRF/R2/ET8000/MRF_R2_GRADED_ROW_ET8000.json` (`verdict`), and the same at 4000 in `MRF_R2_TRIPLE_AT_4000.json` | nothing | **OPEN, referred not fixed.** The graded statistic is a **point sample at `endTime`** whose own relative sd (1.0e-02) is **2.87× the coarse→medium signal** it must resolve. Referral drafted to verification, `verification/runs/navier_class/MRF/R2/REFERRAL_GRADING_STATISTIC_NOISE.md`. **cfd has NOT touched the grading path** | **YES, one PNG** — `docs/campaigns/navier_class/MRF/demo/MRF_R2_fine_surface.png` (impeller + baffles + shaft, 74,804 faces rendered == boundary, measured) | **PARTIAL** — a beautiful 3D geometry with a value in band, but the verdict on record is `NOT A RESULT` and must be said on camera | rule on the referral: the gate needs a windowed statistic, not a point sample |
| **DrivAer R2 / R2c** — notchback passenger car, external aero | cfd | **NO — no DrivAer solve has ever completed.** Mesh gates only: r2_coarse M1 `PASS`, M2 `PASS`, M3 **`GATE FAIL` 50.057 %**, Y1 not wall-function admissible (y+ 481.6); r2_medium M1/M2 `PASS`, M3 **`GATE FAIL` 57.907 %**, **Y1 `PASS`, layered median y+ 232.0 — the first DrivAer level ever inside [30,300]** | **NOT YET — 0 of 3 solve levels complete** | **`GATE FAIL`** on M3 at both levels; **r2_fine `BLOCKED`** (snappy deliberately stopped on expected value while holding the largest contested memory block; the guard was not touched) | **three at once:** `r2_coarse` Time **1415/2000**; `r2c_coarse_blended` **448/2000**; `r2c_medium_blended` **117/2000** | **snappy zero-layer / layer-addition defect.** Five measured arms on disk (`LAYERFIX_A1_relativeSizes`, `B1_medialRatio`, `B2_medialAxisAngle`, `C1/C2_absoluteFirstLayer`), each with its own MEASURED/VERDICT file. **Measured, not resolved** | **YES but of the WRONG MESH** — `docs/campaigns/navier_class/DRIVAER/demo/DRIVAER_r1_fine_surface.png` renders **`r1_fine`**, the superseded R1 mesh, not R2 | **NO** | let a level finish; Y1 passing on medium does **not** lift the Y2 cap (16 unlayered patches at y+ 556.6) |
| **SUBOFF A1 / A1b** — DARPA SUBOFF submarine hull, towed resistance | cfd | **NO — SUBOFF has never had a completed solve.** `SOLVE_L1` reached Time **369 of 3000**; `SOLVE_L2` **never started** (memory gate closed 251 consecutive readings, `available=0 GiB < 19`). Mesh gates: **Gate M at L2 `PASS`, all four limbs**; M-d at L1 `GATE FAIL` 8.6227e-04 vs 1.0e-03; M-b-1 at L0c `GATE FAIL`, 6 cells across the TE | **NOT YET — 0 of 3 solves; family Gate M not evaluable at L3** | **`GATE FAIL`** (family Gate M) + **`BLOCKED`** on L3. Run root `verification/runs/navier_class/SUBOFF_A1/` | `SOLVE_L1` Time **369/3000**; `SOLVE_L2` waiting on memory, never launched | L1 geometric defect (not purchasable); L3 is a **RAM** defect and **is** purchasable | NO | **NO** | **On Sanaa's desk:** the admissible triple needs **~128 GiB AND ~$153.78** of compute at 5.6× the registered cap — both halves |
| **CRM wing-alone, M 0.85** — NASA Common Research Model wing, transonic | cfd | **NO.** `SOLVE_L2` reached Time **1012 of 4000** and had **near-stalled**: its autograde watcher logged 991 → 1009 iterations over six hours | **NOT YET — 0 of 3** | mesh **FROZEN** (`d2629d326`); **no flow verdict exists.** Run root `verification/runs/CRM_WINGALONE_runs/SOLVE_L2/` | `SOLVE_L2` `log.rhoSimpleFoam` at **Time 1012/4000** | **`Y_SYMM_TOL = 1e-9`** against a plane measured planar to 9.49e-06 is ~1000× too tight and loses exactly **832** root-plane faces. **Ruled correctable by the cfd supervisor; the correction is NOT yet applied** | NO | **NO** | decide whether L2 is stalled or merely slow before relaunching it |
| **ONERA M6 (M6CP1 + successors M6H1, M6I, M6SR, RUNG1_M6_R2)** — swept transonic wing, AGARD-AR-138 TEST 2308 | cfd | **NO.** Meshes exist on disk at L3 for M6I (15,360), M6_OWN_FAMILY (8,970), RUNG1_M6_R2 (8,970), M6SR. No completed graded solve | **NOT YET** | **M6C1 `BLOCKED`; route (c) TERMINATED.** M6H1 **FROZEN `fcec859bf`**, check 4 discharged, **launch HELD on cores, not on physics** | nothing | new mesh route — **a mechanism change, not a parameter change** (lane was live on it at the last board write) | NO | **NO** | release M6H1 when cores free |
| **VMFL078-R2** — the SAME lid-driven cavity as the **full cube** (symmetry removed), F1/F2/F3 = 32,768 / 262,144 / 2,097,152 | ansys-verification | **NO — none of the three finished.** Registered `endTime` 40,000 | **NOT YET — 0 of 3** | none yet. Run root `verification/runs/ansys_verification/VMFL078-R2/` | **all three at once:** F1 **444/40000**, F2 **839/40000**, F3 **460/40000** | `F1_ABORTED_GUARD_FALSE_POSITIVE_2026-09-12T0638Z` — a guard false positive aborted F1 once; **relaunched, and the aborted tree was preserved not deleted** | NO (the R1 renders are of the half-cube) | **NO** | relaunch all three; the half-cube (`VMFL078`) already carries the shootable verdict |
| **VMFL072-R2/R3/R4-A/R5** — liquid water film over a flat plate under gravity (thin-film) | ansys-verification | **NO.** R5 ran to completion — the first in the R2→R3→R4-A chain that did not SIGFPE — but the graded field is absent | n/a (R5 is a single 256×64 grid) | **`NOT A RESULT`** — register **Row #80**, `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md:3101`; log `verification/runs/ansys_verification/VMFL072-R5/GRADING_VMFL072_R5.log` (`grade_rc=3`) | nothing | **`kinematicSingleLayer` is ABANDONED for VMFL072.** R3's L3 rc=136 = **SIGFPE inside OpenFOAM's own `kinematicThinFilm::evolveRegion()`** — **on Sanaa's desk, surfaced not worked around**, per her standing instruction | NO | **NO** | successor approach; the SIGFPE is hers to decide on |
| **T5F_CUBE** — conjugate cube, air + epoxy solid regions (896,531 / 14,507 / 882,024 cells at f) | heat-transfer | **NO.** `c` DONE under rule 4 on all six clauses (17.533 core-min, ratio 0.909 of prediction, `note=clean`); `m` **right-censored** at its cap; `f` was relaunched and reached only Time 147 | **NO TRIPLE, and the ruling is arithmetic:** m is censored, so a perfect f still gives two of three | **no verdict assigned.** The frozen limb-A instrument `analyse_t5e.py:217` hardcodes `CASE_OF = {"c": "T5_CUBE_c", …}` and **cannot open the cases its own registration names** — a rule-2 problem, referred under §2d.1 rather than repaired | `T5F_CUBE_f` `log.solve` at **Time 147/5000** | the frozen-instrument defect above — **referred, NOT repaired**; limb B passed on a real case for the first time in its existence (`T5F_CUBE_c` `CONVERGED` on limb B) | NO | **NO** | rule on the §2d.1 referral before spending more on f |
| **PRD porous radiator E1** — porous block, Δp against Ergun, five face velocities | cfd | **NO — 0 of 5 velocity arms pass.** Every arm `NOT A RESULT`; `credential: false`, `n_pass: 0` | triples ran at L1/L2/L3 (18,432 / 147,456 / 1,179,648) but **no arm produced an admissible order** | **`NOT A RESULT` ×5** — `verification/runs/navier_class/PRD/gate_prd_e1.json`, graded 2026-09-12T00:53:24Z | nothing | nothing open | **YES, one PNG** — `docs/campaigns/navier_class/PRD/demo/PRD_E1_us1.00_L3_surface.png` | **NO** (renders exist, but nothing passed) | re-register; the Ergun reference and the measured Δp agree to ~0.1 % yet no order is recoverable |
| **F27 Womersley pipe 3D** — oscillatory laminar pipe flow, exact Womersley solution, α = 4 | cfd | **NO.** E2 90.7576 and E∞ 367.7251 against bands — both **`GATE FAIL`** | **OSCILLATORY** — no order, no GCI | **`NOT A RESULT` ×2** — `verification/runs/F27_WOMERSLEY_PIPE_runs/F27_GRADED.json` (`rows[].verdict`); 265.47 core-min of 680 cap | nothing | nothing open | NO | **NO** | successor rung; the bulk mean velocity also reads OSCILLATORY (0.6426 / 0.6428 / 0.5061) |
| **D6R2** — compressible **multipoint** optimisation of the A2 wing, transonic | dafoam | **NO — no completed optimisation.** Watch file shows the arm alive to 17:31Z, objective cycling 0.02326–0.02685, 3,292 core-min spent | n/a (an optimisation, not a grid study) | **none.** `D6R2_AUTOGRADE.out` reads `ARMED … waiting for D6R2_ARM_RC.txt`, which does not exist. Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D6R2-a2-wing-multipoint-transonic/` | **arm `O_mp`** live at **17:31:00Z**, `Time = 1000` inside a multipoint sub-solve, **3,292.33 core-min**, `D4S_CAP_CROSSED … action=REPORTED_RUN_CONTINUES` under Sanaa's no-cap ruling | nothing open | NO (`D6R2_RENDER_PREP.out` exists; no images) | **NO** | relaunch; this is one of the two **multipoint optimisations Sanaa named as a dafoam deliverable** |
| **MP_A5** — incompressible **multipoint** optimisation of the U-bend duct | dafoam | **NO — the R3 chain failed.** `CHAIN_RC.txt` = **137**: arm B rc=0, **arm O rc=137** (killed), **arm E never ran**. 60.4 core-min spent | n/a | **none.** Run root `/home/ubuntu/certonomous-runs/CURRICULUM-MP_A5-a5-ubend-multipoint-R3-20260912T062921Z/` | arm O was mid-flight when it died | **BOTH DEFECTS INHERITED FROM THE OOM-KILLED PREDECESSOR ARE REPAIRED AND FROZEN** — `MP_A5R ADDENDUM 1`, HEAD commit `d72bee62a`, plus a **launch precondition that refuses to START rather than stopping anything** | NO | **NO** | relaunch the repaired successor; the other named multipoint deliverable |
| **D8G** — CRM **wing-body** grid triple | dafoam | **NO.** R2 `L1-P` mesh build rc=0, 98.667 core-min. No solve has run | **NOT YET — 0 of 3 solves** | **`BLOCKED`** on a permission denial (`Security Weaken`, **twice**). Run root `/home/ubuntu/certonomous-runs/CURRICULUM-D8G-R2-a6-grid-triple/` | nothing | the launcher repair exists; **a no-denied-change path was found but it moves a registered cap and needs a dated addendum.** The supervisor's refusal to substitute his word for the permission system **stands** | NO | **NO** | write the dated addendum, then launch |
| **D6RF11 / D6RF12** — A2 wing finite-difference gradient probes (SIMPLEC probe; nuTilda repair) | dafoam | **NO.** `STATUS.F_probe` for D6RF12 reads **rc=1**, 1,810.6 core-min, `oomkilled=false` | n/a | none on record | nothing (last write 15:03Z) | **nuTilda repair APPLIED and FROZEN** (`b880dabfd`), with a first-match residual reader whose planted control is **mutation-tested against the exact defect that produced a false PASS**; knobs 7-8 installed at all four sites and **read back from disk by the installer before the solver started** (`3315fe0bd`) | NO | **NO** | triage the rc=1 |
| **T26 / T26b** — motor cooling duct successor, hub + duct + struts (`T26_GEO8_DUCT4`, L1 16,384 cells) | heat-transfer | **NO.** L1 mesh built 2026-09-12; no solve graded | **NOT YET — 0 of 3** | none. Run roots `/home/ubuntu/certonomous-runs/T26_GEO8_DUCT4_20260912/`, `T26_DICT_CONTROL_20260912/`, `T26_TOPOLOGY_PROBE_20260912/` | nothing | **BUILDER DEFECT FIXED.** Root cause: hub + duct + 3 struts were bundled into **one `triSurfaceMesh`**. **The registration predicts its own unsuitability for the deadline**, and `T26b` needs a single-level-capable grader that does not exist yet | NO | **NO** | not a filming candidate this cycle, by its own registration |
| **RUNG2_CRM (M0 compressible admission)** — CRM at 638,976 cells | cfd | **UNKNOWN** — mesh on disk, no current grade artifact found in this sweep | UNKNOWN | UNKNOWN | nothing | UNKNOWN | NO | **NO** | ask cfd whether this rung is live or superseded by CRM_WINGALONE |
| **Ahmed body 25°** — bluff-body automotive reference, 79,439 cells | cfd (demo era) | **legacy.** Run trees `/home/ubuntu/certonomous-runs/act7-ahmed_25-*` (8 of them), last touched **2026-07-31**. `mission-output/ahmed-body/` holds `Cd_envelope.png`, `Cl_envelope.png`, `ahmed_25_pressure_slice.png`, `certificate.pdf` | none on the current board | **no current verdict** — these predate the present gating regime | nothing | nothing | **YES, legacy** — `Certonomous/mission-output/ahmed-body/` | **PARTIAL, with a caveat** — pictures and a certificate exist, but **no row on any current board and no pre-registration in the present regime**. Do not present it as a current lab verdict | decide whether to re-register it as a fast 3D win |
| **B-52** — full aircraft, 193,880 cells | cfd (demo era) | **legacy.** `/home/ubuntu/certonomous-runs/study-b52-*` (many), last touched **2026-08-01**; `verification/runs/B52_RUNG6_REPLICATE_runs/record.json` records **G1 cell-count admission PASSED** (pairwise deviation 0.006266) and **G4 lever-echo equality** over 10 files, 13.5 core-min | replicate arm, not a Roache triple | **no rung verdict** — the replicate record carries gate results, not a rung verdict | nothing | nothing | NO images found | **NO** | as above — re-register if wanted |

---

## NOT 3D — excluded, and why (every one read from its own `boundary` file)

These were checked because they are commonly *spoken of* as 3D cases in this lab. They are not,
and the patch type that excludes them is named so nobody has to re-litigate it:

- **`SUP_BOOSTER`** (supersonic cone/booster) — **2 `wedge` + 1 `empty`**, axisymmetric. Its
  `graded_e2/VERDICT.json` carries a healthy `CONVERGING` triple and a passing planted-zero
  control; it is a **good result and a 2D one**.
- **`T23G2` / `T23G2Rn2`** (electric motor in a cooling duct) — **2 `wedge`**, axisymmetric,
  across all four regions. **This is the geometry of demo Act "motor thermal".** Verdict on
  record `NOT A RESULT` (`docs/campaigns/T-family/T23G2Rn2_RESULTS.md`).
- **`T4e`** (impinging jet) — **2 `wedge` + 1 `empty`**. `c` and `m` DONE, `f` was at
  Time 104,000+ of 160,000 at the stop. A near-complete triple, and 2D.
- **`T21`** (cylinder, 6 cases, all solved `DONE` 6/6 under rule 4) — **2 `wedge`**. Rung
  `BLOCKED` on four defects in one grading path.
- **`VMFL017-R3`** (Ansys) — **1 `empty`**. Was at Time 0.0311 of 0.05 and running at the stop.
- **`K2bU3_*`, `K2bP_*`** (the 2D arms of the K2b rack family) — **1 `empty`** each. Only
  `K2bU3R3_D59` and `K2b3D_probe` in that family are 3D.
- **`F18`/`F18b` (Taylor-Green), `F20` (isentropic vortex), `F26D` (Ringleb), `F28` (ducted
  actuator disk), `DPW8_V2`, `JF1_jet_flap`** — all carry `empty` or `wedge`.
- **The Ansys corpus at large** — the ansys-verification supervisor's own census of 82 manual
  cases: **48 `empty` (2D), 15 `wedge` (axisymmetric), 16 unparseable**. **`VMFL078` and the
  `VMFL072` chain are the 3D exceptions**, and `VMFL078` post-dates that census.

**closure** — **no 3D case, and no case at all.** §7 bars every closure launch; the supervisor's
own board records *"7 board commits, 6 lessons, 3 instrument repairs and ZERO RUNS"* and that
closure owns **zero processes on the box**.

**verification** — **none expected and none found.** The team owns standards, gating and audit,
not cases. Its newest block is the shared-launch-tooling kill-primitive audit (V-188).

---

## FOUR SUMMARY LISTS

**SHOOTABLE NOW (4):** `T18_CU` (PASS ×3 in band, CONVERGING triple, GCI ≤ 0.015 %, full render
set) · `VMFL078` (GATE REACHED, CONVERGING, GCI 1.99 %, mesh + geometry renders) ·
`K2bU3R3_D59` (GATE REACHED, DAMPS at ratio 0.420, full render set) · `F25_DUCT3D` (PASS ×2,
CONVERGING p ≈ 1.95/1.97, one verified surface render).

**PARTIAL (5):** `A3GC-AR1/AR1C` (completed M6 primal + the lab's best renders, no band, triple
structurally invalid) · `MRF_R2` (value 4.3817 in band, renders on disk, but verdict on record is
`NOT A RESULT` and the grading statistic is under referral) · `K2f/K2g` (2 of 3 levels DONE,
ratio in band, no renders) · `Ahmed 25°` (legacy pictures + certificate, no current registration)
· `PRD` / `DrivAer` renders exist but of a failed gate and a superseded mesh respectively — do
not film either as a result.

**RUNNING AT THE 17:36Z STOP (11 solvers, all now dead, none with an `End` line):**
`DrivAer r2_coarse` 1415/2000 · `DrivAer r2c_coarse_blended` 448/2000 · `DrivAer r2c_medium_blended`
117/2000 · `SUBOFF SOLVE_L1` 369/3000 · `CRM wing-alone SOLVE_L2` 1012/4000 · `K2f_L3` 835/2000 ·
`T5F_CUBE_f` 147/5000 · `A3GC-L2R` 400/6000 · `VMFL078-R2 F1/F2/F3` 444 / 839 / 460 of 40000 ·
`D6R2 arm O_mp` (multipoint, 3292 core-min) — plus two 2D runs, `VMFL017-R3/L3` and `T4e_IJ_f`.
`SUBOFF SOLVE_L2` was **not** running: its memory gate had been closed for 251 consecutive
readings at `available=0 GiB < 19` and it never launched.

**BEING FIXED (8):** MP_A5 — two defects inherited from the OOM-killed predecessor, **repaired,
frozen, unlaunched** · D6RF12 — nuTilda repair **applied and frozen**, planted control
mutation-tested · DrivAer — snappy zero-layer/layer defect, **five arms measured, unresolved** ·
CRM wing-alone — `Y_SYMM_TOL` 1e-9 losing 832 faces, **ruled correctable, not yet applied** ·
MRF — point-sample grading statistic whose noise is 2.87× its signal, **referred, path untouched**
· T5f — frozen limb-A instrument cannot open its own registered cases, **referred under §2d.1,
unrepaired** · T26 — geometry builder defect (one bundled `triSurfaceMesh`), **fixed** · D8G —
launcher repair blocked twice by the permission system, **needs a dated addendum, not a
workaround**.

---

## WHAT I COULD NOT VERIFY

- **`RUNG2_CRM`** — mesh on disk, no grade artifact located. Marked UNKNOWN rather than guessed.
- **Ahmed and B-52** — I read their meshes and their legacy output files. I did **not** find a
  pre-registration for either in the current regime, so I cannot say what band they were ever
  graded against. They are listed as legacy for exactly that reason.
- **Cost calibration rows** — this is a status inventory, not a completion report; I did not
  re-derive any rule-12 estimate-vs-actual ratio, and none is claimed here.
- **No verdict in this document is new.** Every verdict word quoted is one already written by its
  owning team into the artifact cited beside it.
