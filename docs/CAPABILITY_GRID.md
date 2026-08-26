# CAPABILITY GRID — Sanaa's taxonomy, assembled from the family tables at HEAD

**Owner:** verification-supervisor. **Directive:** Sanaa's [SANAA-DIRECT] CAPABILITY GRID, boarded verbatim at commit `068c2bf0` (`docs/LAB_STATE.md`, CHIEF ADDENDUM 2026-08-26T17:35Z). **Assembled from HEAD `299296a2`** on 2026-08-26T20:53Z by `scripts/assemble_capability_grid.py` (idempotent; reads only `git show HEAD:` blobs; zero compute). **FIRST DRAFT** — re-run when a family table lands.

**The verdict vocabulary (Sanaa's, exactly three):** `CAN DO — X cases` (ran successfully, metrics verified; strongest case cited by path + record sha + what was checked); `CAN DO, CAVEATS` (runs, credible results, named missing items each ≤ 1 line); `CAN NOT DO` (does not converge / does not reproduce literature / not enough compute / documented model defect — what was attempted, what would fix it; empty cell = `CAN NOT DO — not attempted`). One verdict per cell. The lab's fixed gate vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING) appears inside a cell as what the record says.

**Disclosed mapping rule (this supervisor's, from the lanes' common brief):** CAN DO requires at least one case whose record at HEAD says PASS (or GATE REACHED with every reached gate passing) under a frozen prereg with a CONVERGING Roache triple where a triple was claimed; anything weaker that still produced a credible graded number is CAN DO, CAVEATS; GATE FAIL / NOT A RESULT / BLOCKED-only cells are CAN NOT DO with the attempt named. Every citation must resolve at HEAD (`git cat-file -e <sha>^{commit}`); the merged footer below is the planted control.

**Order (Sanaa's):** cfd table, heat-transfer table, dafoam table, then the metrics summary.

---

## cfd

**family table at HEAD: NOT YET LANDED — placeholder: all cells 'CAN NOT DO — not attempted (table not yet built)'.** Owed as `docs/capability/cfd_GRID.md` by the cfd supervisor; this script picks it up on re-run.

| cell | verdict |
|---|---|
| **2D · steady · incompressible** | CAN NOT DO — not attempted (table not yet built) |
| **2D · steady · subsonic-compressible** | CAN NOT DO — not attempted (table not yet built) |
| **2D · steady · transonic** | CAN NOT DO — not attempted (table not yet built) |
| **2D · steady · supersonic** | CAN NOT DO — not attempted (table not yet built) |
| **2D · steady · hypersonic** | CAN NOT DO — not attempted (table not yet built) |
| **2D · steady · multiphase-free-surface** | CAN NOT DO — not attempted (table not yet built) |
| **2D · unsteady · incompressible** | CAN NOT DO — not attempted (table not yet built) |
| **2D · unsteady · subsonic-compressible** | CAN NOT DO — not attempted (table not yet built) |
| **2D · unsteady · transonic** | CAN NOT DO — not attempted (table not yet built) |
| **2D · unsteady · supersonic** | CAN NOT DO — not attempted (table not yet built) |
| **2D · unsteady · hypersonic** | CAN NOT DO — not attempted (table not yet built) |
| **2D · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · steady · incompressible** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · steady · subsonic-compressible** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · steady · transonic** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · steady · supersonic** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · steady · hypersonic** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · steady · multiphase-free-surface** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · unsteady · incompressible** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · unsteady · subsonic-compressible** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · unsteady · transonic** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · unsteady · supersonic** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · unsteady · hypersonic** | CAN NOT DO — not attempted (table not yet built) |
| **axisym · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted (table not yet built) |
| **3D · steady · incompressible** | CAN NOT DO — not attempted (table not yet built) |
| **3D · steady · subsonic-compressible** | CAN NOT DO — not attempted (table not yet built) |
| **3D · steady · transonic** | CAN NOT DO — not attempted (table not yet built) |
| **3D · steady · supersonic** | CAN NOT DO — not attempted (table not yet built) |
| **3D · steady · hypersonic** | CAN NOT DO — not attempted (table not yet built) |
| **3D · steady · multiphase-free-surface** | CAN NOT DO — not attempted (table not yet built) |
| **3D · unsteady · incompressible** | CAN NOT DO — not attempted (table not yet built) |
| **3D · unsteady · subsonic-compressible** | CAN NOT DO — not attempted (table not yet built) |
| **3D · unsteady · transonic** | CAN NOT DO — not attempted (table not yet built) |
| **3D · unsteady · supersonic** | CAN NOT DO — not attempted (table not yet built) |
| **3D · unsteady · hypersonic** | CAN NOT DO — not attempted (table not yet built) |
| **3D · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted (table not yet built) |

---

## heat-transfer

**family table at HEAD: NOT YET LANDED — placeholder: all cells 'CAN NOT DO — not attempted (table not yet built)'.** Owed as `docs/capability/heat-transfer_GRID.md` by the heat-transfer supervisor; this script picks it up on re-run.

| cell | verdict |
|---|---|
| **conduction · laminar · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **conduction · laminar · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **conduction · laminar · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **conduction · turbulent · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **conduction · turbulent · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **conduction · turbulent · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **forced conv · laminar · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **forced conv · laminar · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **forced conv · laminar · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **forced conv · turbulent · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **forced conv · turbulent · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **forced conv · turbulent · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **natural conv · laminar · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **natural conv · laminar · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **natural conv · laminar · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **natural conv · turbulent · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **natural conv · turbulent · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **natural conv · turbulent · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **mixed · laminar · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **mixed · laminar · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **mixed · laminar · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **mixed · turbulent · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **mixed · turbulent · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **mixed · turbulent · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **conjugate · laminar · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **conjugate · laminar · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **conjugate · laminar · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **conjugate · turbulent · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **conjugate · turbulent · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **conjugate · turbulent · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **radiation · laminar · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **radiation · laminar · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **radiation · laminar · 3D** | CAN NOT DO — not attempted (table not yet built) |
| **radiation · turbulent · 2D** | CAN NOT DO — not attempted (table not yet built) |
| **radiation · turbulent · axisym** | CAN NOT DO — not attempted (table not yet built) |
| **radiation · turbulent · 3D** | CAN NOT DO — not attempted (table not yet built) |

---

## dafoam

**family table at HEAD: `6fcfe713`** (`docs/capability/dafoam_GRID.md`; every cell below is copied verbatim from that file — the family supervisor's words, not this script's).

**Regime / mode per case, as derived by the family (their table):**

| case family | solver / conditions (path) | cell |
|---|---|---|
| A1 NACA0012 (D1, D1-C′, D2, D13, A_stepsize) | `DASimpleFoam`, `U0 = 10.0`, 4,032 cells — `cases/dafoam/ladder-a/A1/curriculum_D1/PREREGISTRATION.md:21-43` ("this 2D case") | **2D · steady · incompressible** |
| B3 / S1 CBFS field inversion | `DASimpleFoam`, 21,000 cells, 2D duct — `cases/dafoam/ladder-b/B3/decomposition_np4/RESULTS.md` | **2D · steady · incompressible** |
| A4 Ahmed body (D3, first/shipped optimisation) | `DASimpleFoam` — `cases/dafoam/ladder-a/A4/first_optimisation_np1/RESULTS.md:37` | **3D · steady · incompressible** |
| A5 U-bend (D9, D10) | `DASimpleFoam`, `U0 = 8.4 m/s` — `cases/dafoam/ladder-a/A5/curriculum_D9/PREREGISTRATION.md:19` | **3D · steady · incompressible** |
| D11 MRF rotor probes | `DASimpleFoam` + `MRFProperties` — `cases/dafoam/probes/curriculum_D11_mrf_probe/PREREGISTRATION.md:15-16` | **3D · steady · incompressible** |
| A2 MACH wing (D4, D4-SHIPPED, D14-M) | `DARhoSimpleFoam`, `U0 = 100 m/s`, `T0 = 300 K` → M ≈ 0.29 — `cases/dafoam/ladder-a/A2/curriculum_D4/PREREGISTRATION.md:24`; `/home/ubuntu/certonomous-runs/A2-mach-wing/runScript.py:28-39` | **3D · steady · subsonic-compressible** |
| A3 ONERA M6 (D7, D7R, D7FR, sweep rungs) | `U0 = 291.6 m/s (M 0.84)` — `cases/dafoam/ladder-a/A3/curriculum_D7R/PREREGISTRATION.md:138` | **3D · steady · transonic** |
| A6 CRM wing-alone (D8, N=16 rungs) | `DARhoSimpleCFoam`, transonic, `U0 = 295 m/s` — `cases/dafoam/ladder-a/A6/curriculum_D8/PREREGISTRATION.md:44-45` | **3D · steady · transonic** |
| D12 / D12R / D12R2 / W2 / W2R cylinder | `DAPimpleFoam`, time-accurate unsteady adjoint, 2D, `Re_D = 1.0e6` — `cases/dafoam/curriculum_D12R2/PREREGISTRATION.md:1,313,331` | **2D · unsteady · incompressible** |

**The table:**

| cell | gradients computed + FD-verified | optimization converged |
|---|---|---|
| **2D · steady · incompressible** | **CAN DO — 6 cases** (D1, D1-C′, D2, D13, A1 re-verification, A_stepsize); **strongest case `cases/dafoam/ladder-a/A1/curriculum_D13/RESULTS.md` @ `15767999`**; checked: FD-vs-adjoint relative error per DV at three independently converged endpoints, **4/4 components each, worst 0.2568 / 0.2540 / 0.2557 %**, zero sign flips, on the patched IDWarp image; the SHIPPED row is **design-point dependent** — `GATE FAIL` **11.4274 %, one sign flip** at the baseline (`ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` @ `be35dcad`) and **PASS** at the converged optimum (`ladder-a/A1/curriculum_D1_Cprime/RESULTS.md` @ `cffd90e7`); step-plateau sweep (`ladder-a/A_stepsize_study.md`); np-invariance measured on B3 CBFS: serial vs scotch vs simple decomposition, **G4 `GATE FAIL` as written** — gradients differ by decomposition (`ladder-b/B3/decomposition_np4/RESULTS.md` @ `bb5088c4`); B3 shipped adjoint `BLOCKED` (PETSc `-9`), passes only on the sub-LU patch (`ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` @ `3f8c6b13`); dot-product/duality and complex-step **not checked** anywhere in this family. | **CAN DO — 4 cases** (D13 three restarts, D2 two optimisers, D1); **strongest case `ladder-a/A1/curriculum_D13/RESULTS.md` @ `15767999`**: three starts each reach `EXIT: Optimal Solution Found.` in 9–11 majors at `CD = 0.017527…` (spread ≤ 2e-7), each endpoint FD-verified 4/4 ≤ 0.26 %; D2 IPOPT **and** SLSQP both terminate `Inform = 0` with endpoint FD PASS 0.2553 / 0.2485 % (`ladder-a/A1/curriculum_D2/RESULTS.md` @ `b840fcd5`); D1 arm O PATCHED `PASS`, arm C shipped endpoint `BLOCKED` then `PASS` under D1-C′ (`ladder-a/A1/curriculum_D1/RESULTS.md` @ `b10260a0`). Checked: optimiser convergence line + endpoint FD, both rows. |
| **2D · steady · subsonic-compressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · steady · transonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · steady · supersonic** | CAN NOT DO — not attempted (the image ships `Cone_Supersonic`; never staged) | CAN NOT DO — not attempted |
| **2D · steady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · steady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · unsteady · incompressible** | **CAN DO, CAVEATS** — the time-accurate unsteady adjoint **reaches** (`DAPimpleFoam`, `GATE REACHED`, `cases/dafoam/probes/curriculum_D12_unsteady_probe/RESULTS.md` @ `4d9d902b`), but **no admissible FD step**: D12R2 phase 1 `G12R-4` = `NOT A RESULT` — *"`h_min = 1.742838e-01` EXCEEDS the registered `h_max = 5.000e-02`; no admissible FD step exists at `W = 300`"* (`cases/dafoam/curriculum_D12R2/RESULTS.md` @ `65882eb3`); W2 `BLOCKED` (aggregate guard); W2R at `W = 900` running with phases 2–4 and their plan steps queued agent-independently (`curriculum_D12R2/W2R_PREREGISTRATION.md` @ `5d1f89cd`); its primary prediction P3 is again *no admissible step*. Caveats: no admissible FD step at W = 300; single mesh (2,450 cells); `St ≈ 0.53` is a resolution artifact never quoted as a Strouhal number. | **CAN NOT DO** — attempted: D12 → D12R → D12R2 phases 2–4 all gated on `G12R-11`, which authorises S8 only after an FD-verified gradient; the FD line stops at `G12R-4`, so the optimiser was never authorised (`curriculum_D12R2/RESULTS.md` @ `65882eb3`). What would fix it: an admissible step at a longer averaging window (W2R, `W = 900`, running; phases queued) or an objective whose window derivative `δ_window` cancels by construction. |
| **2D · unsteady · subsonic-compressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · unsteady · transonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · unsteady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · unsteady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · steady · incompressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · steady · subsonic-compressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · steady · transonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · steady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · steady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · steady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · unsteady · incompressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · unsteady · subsonic-compressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · unsteady · transonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · unsteady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · unsteady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **axisym · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · steady · incompressible** | **CAN DO, CAVEATS — 4 cases** (A4 two optimisations, A5 re-verification, D11 MRF probe); **strongest case `cases/dafoam/ladder-a/A4/first_optimisation_np1/RESULTS.md` @ `5d1718df`**: endpoint FD at the converged design **`PASS` 0.4936 %**, zero flips, patched image; A4 shipped row PASS 1.10 % at the baseline (`docs/dafoam/README.md` §3 @ `ddb99eca`, record `ladder-a/A4_ahmed_body.md`). Caveats: A5 U-bend SHIPPED row `GATE FAIL` **46.84 %, two sign flips** (IDWarp rotation defect), PATCHED `PASS` on the aggregate band with **5 of 27 components outside** it (`ladder-a/A5/reverify_patched_idwarp_np1/RESULTS.md` @ `35171866`); D11 MRF adjoint `GATE REACHED` — agrees with a central FD (`probes/curriculum_D11_mrf_probe_Fprime/RESULTS.md` @ `52a213ad`) — but the base probe `NOT A RESULT` (all stages died); D10 thermal objective reaches the adjoint (`GATE REACHED`) while its FD table is `NOT A RESULT` (`ladder-a/A5/curriculum_D10_probe_Fprime/RESULTS.md` @ `4d9d902b`); D9 U-bend `NOT A RESULT` (`ladder-a/A5/curriculum_D9/RESULTS.md` @ `f8916f36`). | **CAN DO, CAVEATS — 2 converged, 2 not**; **strongest case `ladder-a/A4/first_optimisation_np1/RESULTS.md` @ `5d1718df`**: `EXIT: Optimal Solution Found.` in 9 majors, NLP error 6.28e-07, **CD −7.478 %**, endpoint FD `PASS`; the shipped row also converges (`Optimal Solution Found.`, NLP error 6.9114e-08, fewer majors — `ladder-a/A4/shipped_optimisation_np1/RESULTS.md` @ `f9a59d47`). Caveats: **unconstrained A4 only** — the constrained Ahmed item D3 is `BLOCKED` on an instrument (`nom_addThicknessConstraints2D` surface name) across two attempts (`ladder-a/A4/curriculum_D3_attempt2/RESULTS.md` @ `6b8d6355`); D9 U-bend SLSQP driver failed (`G9-3 GATE FAIL`, probe `NOT A RESULT` @ `f8916f36`); single mesh per case. |
| **3D · steady · subsonic-compressible** | **CAN DO — 3 cases** (A2 grading confirmation, D4, D4-SHIPPED grader path); **strongest case `cases/dafoam/ladder-a/A2/curriculum_D4/RESULTS.md` @ `1697ea49` §11**: endpoint FD at the corrected optimum, `G5 PASS` **5 of 5 registered components, aggregate 0.1634 % against 5 %, zero sign flips, zero without a plateau**, np=4 `scotch`, patched image (`ARMF3_d4_grade_verdict.json` @ `4eae12f4`); the SHIPPED row at the baseline `PASS` six rows, `CD/shape` **1.714 %** (`ladder-a/A2/grading_confirmation/RESULTS.md` @ `35171866`). Checked: FD-vs-adjoint per DV with plateau, planted zero, decomposition determinism (G8), toolchain identity by `.so` md5 (G9). Noted, not a caveat on the gradient: the D4-SHIPPED item closed `NOT A RESULT` on its grader path before its F3 table was graded (`ladder-a/A2/curriculum_D4_SHIPPED/RESULTS.md` @ `b26b875c`); **D14-M shows the mesh is regenerable bit-for-bit** (`ladder-a/A2/curriculum_D14/RESULTS.md` @ `60cfd4c8`). | **CAN DO, CAVEATS — 1 converged (patched), 1 cap-stopped (shipped)**; **strongest case `ladder-a/A2/curriculum_D4/RESULTS.md` @ `1697ea49`**: PATCHED arm O `EXIT: Optimal Solution Found.` at 80 majors, **28.6758 % drag reduction at `CL = 0.5`**, rung `GATE REACHED` (G2 band A `GATE FAIL` on CL feasibility reported, endpoint FD `PASS`). Caveats: SHIPPED arm O stopped at `max_iter` 100 (`EXIT: Maximum Number of Iterations Exceeded`) and the item is `NOT A RESULT` on its grader path, 731.667 core-min named waste (`ladder-a/A2/curriculum_D4_SHIPPED/RESULTS.md` @ `b26b875c`); single mesh (38,304 cells); the number is a patched-IDWarp statement, not toolchain-independent. |
| **3D · steady · transonic** | **CAN DO — 4 cases** (D7FR two rows, A3 sweep rung 2, A6 N=16 fixed reference, A3 grading confirmation); **strongest case `cases/dafoam/ladder-a/A3/curriculum_D7FR/RESULTS.md` @ `2a93ff27`**: ONERA M6 at M 0.84, 42,120 cells, np=4 — **SHIPPED row `PASS` 5 of 5 (worst 1.959 %) and PATCHED row `PASS` 5 of 5, divergence 0.000 % on every component**, item `PASS`, two distinct IDWarp `.so` md5s asserted; A3 rung 2 patched np=4 `PASS` (`ladder-a/A3/rung2_patched_idwarp_np4/RESULTS.md` @ `0f56460d`); A6 CRM N=16 with the FD reference fixed: `PASS` ≤ 5 % among graded components (`ladder-a/A6/rung_n16_fixed_reference/RESULTS.md` @ `66f42398`). Checked: FD-vs-adjoint per DV, plateau, np=4 decomposition disclosed. Scale limit, recorded: A3 at 399,360 cells and A6 at 579,072 cells are `BLOCKED` on memory/conditioning (`ladder-a/A6/adjoint_feasibility/RESULTS.md` @ `be35dcad`; `ladder-a/A3/grading_confirmation/RESULTS.md` @ `35171866`). | **CAN DO, CAVEATS — 0 converged to tolerance, 2 cap-stopped**; **strongest case `ladder-a/A6/curriculum_D8/RESULTS.md` @ `9c241fe2`**: CRM N=16 twist-only, `GATE REACHED` — stopped on its registered 3-major cap (`EXIT: Maximum Number of Iterations Exceeded.`), never `PASS` by `DAFOAM_CHARTER.md` §9. Caveats: D7R arm O (M6, 30 majors at `max_iter`) `NOT A RESULT` — the grader refused and the 30.40 % reduction lies outside the frozen band (`ladder-a/A3/curriculum_D7R/RESULTS.md` @ `2b50394a`); no `Optimal Solution Found.` exists on record in this cell; single mesh per case. |
| **3D · steady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · steady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · steady · multiphase-free-surface** | CAN NOT DO — not attempted (the image ships `JBC_Hull`; never staged) | CAN NOT DO — not attempted |
| **3D · unsteady · incompressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · subsonic-compressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · transonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |

**Census:** 5 of 36 cells carry evidence (2D·steady·incompressible, 2D·unsteady·incompressible, 3D·steady·incompressible, 3D·steady·subsonic-compressible, 3D·steady·transonic); **31 not attempted**. Gradient column: CAN DO 3, CAN DO CAVEATS 2. Optimisation column: CAN DO 1, CAN DO CAVEATS 3, CAN NOT DO (attempted) 1. **Checks never performed anywhere in the family, stated so the grid cannot imply them: dot-product/duality test, complex-step** (Sanaa's §6 list); **no grid family exists on any DAFoam case, so no GCI is quoted anywhere above** (standing rule 5).

---

## Evidence: ansys-verification (VMFL register rows mapped onto cfd / heat-transfer classes)

**at HEAD: NOT YET LANDED** — `docs/capability/ansys_ROWS.md` owed by ansys-verification; picked up on re-run.

---

## Metrics summary (Sanaa's §1–§6)

**at HEAD: `dff35b15`** (`docs/capability/METRICS_SUMMARY.md`, reproduced verbatim; its own planted-control footer is superseded by the merged footer below):


**Written 2026-08-26 by a verification-supervisor lane (lane id `metrics`), for the verification
supervisor to fold into `docs/CAPABILITY_GRID.md`.** Taxonomy and wording are Sanaa's
`[SANAA-DIRECT] CAPABILITY GRID` directive, `docs/LAB_STATE.md:1225-1253` at HEAD `33dbe337`.

**The rule this file obeys (Sanaa's):** a summary is written ONLY where an item is ABSENT from
the lab's existing verification/standards files. Where the item already exists, this file gives a
one-line citation — file, section, line range — and nothing else. **Every line range below was
resolved against HEAD `33dbe337` with `git show 33dbe337:<path> | sed -n`.** A summary written
here is labelled `ABSENT from standards — summary written here, not a standard until Sanaa adopts
it`; it binds nobody and moves no threshold.

**ASME V&V 20 itself:** the standard's own text is **NOT** in the repository.
`docs/papers/verification_validation/` holds `dowding_2016_asme_vv.pdf` (Dowding, Sandia
SAND2016-5342C — an *overview* of V&V 20-2009), Oberkampf & Roy 2011, Eça & Hoekstra 2014 and
the Ansys Fluid Dynamics Verification Manual. `docs/NUMERICS_KNOWLEDGE.md:120-123` lists
"ASME V&V 20-2009" as "now supplied", but `git ls-tree -r HEAD | grep -i 'v&v\|vv20\|asme'` returns
only the Dowding overview. Stated so the grid does not imply the standard is on the shelf.

**Predecessor draft:** none at HEAD (`docs/capability/` holds only `dafoam_GRID.md`), on disk or in
the scratchpad root. Nothing was reverted.

---

## §1 Verification metrics (right equations solved right)

**Sanaa's ruling, her words:** *"Your ruling: these score V, never P."* — `docs/LAB_STATE.md:1239`.
The lab's coverage rubric already enforces it: a case scores **V** only against an exact solution,
a manufactured solution or a correlation; **P** only against a public primary source with the
pre-registration on disk — `docs/COVERAGE_MATRIX.md:44-48` (rubric table) and `:95-100` (the
correction that heat-transfer's "V" rows were G rows).

- **Reference versus gate (a correlation yields a deviation, not a verdict, unless banded in
  advance)** — PRESENT: `docs/charters/VERIFICATION_CHARTER.md` §2, lines 62-102. Worked table with
  the Strouhal-vs-Roshko-Williamson row at 0.77 % (`:80-86`). Fixed verdict vocabulary `:96-102`.
- **Observed order versus formal order** — PRESENT: `VERIFICATION_CHARTER.md` §3.1 lines 195-277
  (dimensionality divides p by exactly 1.5), §3.2 lines 278-347 (the two ways an observed order
  lies), §3.4 lines 440-486 (a band is not a demonstrated asymptotic order; order must stop moving).
- **Correlation agreement, % deviation (Colebrook, Dittus-Boelter, Zukauskas)** — the *shape*
  (reference column, % deviation, banded PASS) is PRESENT in §2 `:74-86`; the named correlations
  are not cited by any charter or standard (`git grep -i colebrook\|dittus\|zukauskas` over
  `docs/charters docs/standards` returns nothing).
- **Error norms vs exact/analytic (L2, L∞)** — ABSENT from standards. `git grep` for `L∞`, `L_inf`,
  `Linf`, `L2 norm` over `docs/charters docs/standards CLAUDE.md` returns only two unrelated
  `λ_L2` penalty lines (`VERIFICATION_CHARTER.md:120-121`) and the Ekaterinaris review text.
- **Method of manufactured solutions** — ABSENT from standards. Named only in the coverage rubric
  (`docs/COVERAGE_MATRIX.md:46, 98, 229, 369-371`); no charter defines how an MMS case is graded.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Error norms against an exact solution u_ex on a mesh of N cells with volumes V_i:
`L2 = sqrt( sum_i V_i (u_i - u_ex(x_i))^2 / sum_i V_i )`, `Linf = max_i |u_i - u_ex(x_i)|`,
each stated in the solution's own units and beside its relative form (divided by a named
reference scale). Observed order from two mesh levels with refinement ratio r:
`p_obs = log( E_coarse / E_fine ) / log(r)`; from three levels use the shared instrument
(`scripts/roache_triple.py`, §2 below), never a two-point slope alone. The verification claim is
`p_obs` against the scheme's formal order p_f, reported as a pair `(p_obs, p_f)` with the
dimensionality printed (charter §3.1). MMS: choose a smooth analytic field u_m, compute the
source `S = L(u_m)` symbolically, run the solver with `S` added and u_m as boundary data, and
grade with the L2/Linf norms and `p_obs` exactly as above; a manufactured solution is a code
verification and scores V only. These norms are gate-shaped only when a band was frozen before
the run (charter §2 `:72-74`).

## §2 Grid / numerical convergence

- **Roache triple → GCI + observed order** — PRESENT: `CLAUDE.md` rule 5, lines 58-67 (the gate,
  in order; `Fs = 1.25`; never a GCI on a non-monotone triple); `docs/standards/MESH_STANDARD.md`
  §9.1 lines 448-473 (Sanaa's three-level ruling, verbatim, with the three conditions that stay
  binding); §10.2 lines 586-608 (a GCI at a vortex core bounds MESH error only — disclosure);
  §10.5 lines 623-633 (`STAGNANT_FLOOR = 0.5`, `P_MIN = 0.05` DEGENERATE); the shared instrument
  `scripts/roache_triple.py` lines 1-183 (rule 5 in order `:118-126`, states `:182-183`);
  `docs/UNCERTAINTY-DOCTRINE.md:21-28` (u_num recipe, Eça & Hoekstra least-squares fit, p clamped
  to [0.5, 2.5] for the band). Draw-scatter rule for any claim about the SHAPE of a ladder:
  `VERIFICATION_CHARTER.md` §17 lines 1424-1440.
- **Iterative convergence (residuals)** — PRESENT: `VERIFICATION_CHARTER.md` §4 lines 487-564
  (L-14 Initial-vs-Final residual, 1e-322 underflow `:506-510`, L-15 exit-zero, L-24 "a quantity is
  converged, not a run", iteration cap is a budget `:528-531`); `docs/NUMERICS_KNOWLEDGE.md:856-880`
  (`residualControl` is not a criterion; gate the graded quantity's peak-to-peak over a window).
- **The 10^105 lesson (absolute solution / continuity bounds)** — PRESENT as a numerics fact, not
  as a charter clause: `docs/NUMERICS_KNOWLEDGE.md` **N-AV12**, lines 4226-4293: VMFL007's
  normalised `p` residual sat in [0.157, 0.587] for 9 000 iterations while
  `time step continuity errors : sum local` reached **3.316e+105**; a normalised residual is
  blind to coherent divergence. No L-number carries it (`grep -n 'e+105' docs/LESSONS.md` empty).
- **Partition / round-off reproducibility (the 2.2e-5 finding)** — PRESENT:
  `docs/standards/PARALLEL_GATE_DOCTRINE.md` §2 lines 31-46 (Sanaa's words: "graded quantities
  moved 2.2e-5 across partitions — the answers are stable; the gates aren't"), §3 C1/C3 lines
  53-99 (deterministic decomposition; partition-robustness in gate design), §4.5 lines 184-202
  with the correction at `:194-198` (2.2e-5 = reattachment alone, 2.169e-05; separation moved
  2.857e-07). DAFoam side: `docs/charters/DAFOAM_CHARTER.md` §5 lines 156-198 (serial before
  parallel; every parallel gradient discloses its decomposition); `docs/NUMERICS_KNOWLEDGE.md`
  N-D12 `:3220-3229` (cold-start continuity signature is np-specific). Invariance passing because
  both sides are wrong together: `docs/LESSONS.md` L-38 `:1736`. No L-number carries 2.2e-5.
- **Seed spread** — PRESENT for closure models: `docs/LESSONS.md` L-181 `:8123-8150` ("seed
  spread is an extrapolation detector"); `docs/charters/CLOSURE_MODELLING_CHARTER.md` §4
  `:122-146` (per-seed realisability table). For CFD solves the lab's analogue is the
  partition pair above; there is no seed-spread clause for a deterministic solver.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
An *absolute* iterative-convergence bound, to sit beside the normalised residual: for each
transported field record `max|phi|` and the solver's `time step continuity errors : sum local /
global / cumulative` per iteration; a run is iteratively converged only if the normalised
residual meets its tolerance AND `sum local` is below a frozen absolute ceiling (order 1e-3 for
incompressible cases) AND the graded quantity's peak-to-peak over the frozen window is inside its
band (NUMERICS `:872-880`). Partition reproducibility as a metric: run the gate case at two
decompositions (np pair, pinned method + seed), report `delta_np = |Q(np_a) - Q(np_b)| / |Q|`
per graded quantity, and quote it as the reproducibility floor beneath which no difference is a
result (the lab's measured value on the hump: 2.169e-05 reattachment, 2.857e-07 separation).

## §3 Validation vs experiment — by data type

- **Integral / single-value (Cd, Cl, Nu, f·Re, Δp, St, shock standoff, reattachment) — % error vs
  measurement** — PRESENT: `VERIFICATION_CHARTER.md` §2 `:62-102` (reference column, % deviation,
  banded PASS; hump separation/reattachment row `:82`, Strouhal row `:81`); §5 `:565-648` (detector
  resolution beside every number, L-28 quantised shock position `:568-580`); §6b `:1661-1725`
  (a reference never obtained is recorded in one vocabulary); §2c `:1726-1832` (a row that grades
  a hypothesis must discriminate it from the hypothesis being absent — the K0cS Nusselt row);
  §2d `:1833-1913` (comparator frozen before its cases can answer it).
- **Fields — scaled MAE (the closure-challenge metric)** — PRESENT:
  `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md:239-244` (definition: mean Euclidean error over the
  1000 fixed points divided by the mean magnitude of the truth; overall = plain mean of eight);
  `docs/charters/RESULT_PRIORITY_CHARTER.md:134-138`. Correlation coefficient: Pearson r appears as a
  frozen clause V2 (`r >= 0.85`) in `campaign/R5_PREREGISTRATION.md` via `docs/DOCKET.md:579`
  (D214), not in any charter.
- **Profiles — RMSE/MAE at traverse stations, fraction inside error bars** — ABSENT from standards.
  The lab has graded profiles (F6b Gate Q, scaled MAE of velocity at 9 stations, 12.82 %,
  `docs/VALIDATION_INVENTORY.md:319`) but no charter or standard defines a per-profile RMSE or an
  inside-error-bar fraction (`git grep -i 'error bar\|RMSE\|traverse station'` over
  `docs/charters docs/standards`: only CLOSURE §4 `:146` "regardless of RMSE" and `:315`).
- **Structure / topology (vortex count, separation/reattachment location, stall angle, shock
  position) — "the round-5 lesson: scalar metrics can't see wrong structure"** — PARTLY PRESENT.
  Separation/reattachment *location* and shock position are graded as scalars (charter §2 `:82`,
  §5 `:568-580`). The round-5 record on disk is `docs/DOCKET.md:579-580` (D214: one third of the
  frozen round-5 gate graded fields the entry is not scored on and read PASS on an arm whose graded
  fields never converged; D215). **No L-number or charter clause carrying "scalar metrics cannot
  see wrong structure" was found at HEAD** (`grep -in 'round.5\|wrong structure' docs/LESSONS.md`:
  only L-96 `:4380` and R5 file-path lessons). Explicit structure rows are ABSENT from standards.
- **Statistics (unsteady): means, RMS, spectra peaks, phase averages** — ABSENT from standards.
  Strouhal is the only unsteady statistic a charter grades (`:81`); `git grep -i 'spectr\|phase.averag'`
  over `docs/charters docs/standards` hits only the Ekaterinaris review text.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Profiles: at each published traverse station s with N_s points, `RMSE_s = sqrt( mean_j (u_sim(y_j)
- u_exp(y_j))^2 )`, `MAE_s = mean_j |u_sim - u_exp|`, both divided by a named reference velocity,
plus `f_in,s = (number of j with |u_sim - u_exp| <= sigma_exp(y_j)) / N_s` where `sigma_exp` is
the reference's own stated error bar; the simulated value is interpolated to the experimental
ordinate, never the reverse, and the station list is frozen in the pre-registration. Fields:
scaled MAE as defined in GOALS_AND_PROPOSALS `:239-244`; Pearson r between simulated and truth
fields at the same points, reported beside scaled MAE, never instead of it. Structure: every
structural feature the case exists to show is an explicit row — vortex/bubble count (integer,
detector named), separation and reattachment x/L, stall angle, shock x/c — each with its
detector resolution (charter §5) and its own band; a scalar-metric PASS with a structural row
missing or failed is not a validation of the structure. Unsteady statistics: time-mean and RMS
over a frozen averaging window that starts after a stated transient and spans an integer number
of shedding periods; dominant spectral peak frequency (as St) with the resolution `1/T_window`
printed beside it; phase-averaged quantities only at pre-registered phases. Every unsteady
statistic states its window and its sampling interval or it is not a result.

## §4 The formal standard tying it together — ASME V&V 20 (u_val, E vs u_val)

- **u_val = sqrt(u_num^2 + u_input^2 + u_D^2); comparison error E = S − D judged against u_val**
  — PRESENT: `docs/UNCERTAINTY-DOCTRINE.md` lines 14-40 (the three channel recipes) and
  `:72-108` (combination stated once); `docs/NUMERICS_KNOWLEDGE.md:120-123` (V&V 20 reference),
  `:163-170` (Dowding overview: without an experimental comparison no validation claim can be
  made), `:469-490` (report the three channels separately). Standard's own text: NOT on disk
  (header above).
- **The one use, K0cT** — PRESENT: `docs/campaigns/F14-cooling-ladder/K0cT_NUSSELT_REGRADE.md`
  §2-§3 lines 44-66 at record commit `336a364d`: u_val in quadrature 5.43 % / 5.41 % from Betts &
  Bokhari's stated 5.00 % accuracy, 2.09 % / 2.00 % table inconsistency, 0.28 % / 0.49 % grid
  uncertainty; `E = 100 (Nu_solve - Nu_ref) / Nu_ref` on the fine mesh; verdict by `|E|/u_val`
  (3.09 and 4.57 → GATE FAIL). Every band element external to the solve values (`:44-53`).
- **High_order_grid_convergence.pdf** — PRESENT and RULED OUT as a source:
  `docs/standards/High_order_grid_convergence_PROVENANCE.md:1-30` (the file is Ekaterinaris 2005,
  PAS 41:192-300, a review of high-order schemes; contains no grid-convergence apparatus);
  `MESH_STANDARD.md` §10.1 `:557-585` (prohibition) and §10.2 `:586-608` (the one thing it says).

Nothing is ABSENT in §4 except the standard's own PDF; no summary is written.

## §5 Internal physicality (validity without a reference)

- **Heat balance closure %** — PRESENT: `docs/NUMERICS_KNOWLEDGE.md:881-908` (on a sealed case the
  boundary balance is an identity to 5e-9 %; `scripts/heat_balance.py` stamps
  `closure_is_identity_class`; reported, never counted as evidence on a sealed case); `:1180-1260`
  (open-domain advective enthalpy flux — the closure is convergence-sensitive there);
  `VERIFICATION_CHARTER.md:1947` (K0cS's repair was found by the heat balance).
- **Realisability (b_ij)** — PRESENT as a GATE: `docs/charters/CLOSURE_MODELLING_CHARTER.md` §4
  lines 122-157 (violating-fraction ≤ 3× truth's own, `max||b||_F ≤ 2·sqrt(2/3)`, else NOT A
  RESULT regardless of RMSE); `docs/NUMERICS_KNOWLEDGE.md` N-B3 `:2093-2100` (the `a1` limiter is
  a realisability constraint).
- **Continuity RMS / absolute continuity bound** — PRESENT only as the N-AV12 fact (§2 above,
  `NUMERICS_KNOWLEDGE.md:4226-4293`) and the continuity-error detection-floor lesson L-209
  (`docs/LESSONS.md:8836`); no charter gates on it.
- **Mass balance closure %, boundedness, entropy conditions** — ABSENT from standards
  (`git grep -i 'mass balance\|boundedness\|entropy'` over `docs/charters docs/standards CLAUDE.md`:
  nothing gate-shaped).

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Mass balance: `imbalance_% = 100 · |sum_patches (rho U·n A)| / (0.5 · sum_patches |rho U·n A|)`
over all boundary patches, computed from the solver's own `phi` (never a normal you build,
NUMERICS `:1191-1199`); on a sealed incompressible case this is an identity and is reported, not
counted. Continuity: `sum local` per iteration with its frozen absolute ceiling (§2 summary).
Boundedness: for every physically bounded scalar (alpha in [0,1], T inside its boundary range, k
and omega > 0) report `min/max` over the domain at the graded iteration and the count of cells
outside the bound; a bounded scheme keeping a field inside its bounds is not evidence of accuracy.
Entropy (compressible): `s - s_inf` must be ≥ 0 across a shock and ≈ 0 along an isentropic
streamline; report `max(s_inf - s)` (the largest entropy *decrease*, a discretisation artefact)
beside the shock-position row. Realisability: CLOSURE §4, unchanged.

## §6 Adjoint-specific

- **FD-vs-adjoint relative error per DV** — PRESENT: `docs/charters/VERIFICATION_CHARTER.md` §7
  lines 833-897: PASS ≤ 5 % aggregate with zero flagged components, CONDITIONAL 5-15 % with a
  per-component breakdown, FAIL > 15 % or any sign flip (`:838-847`); five-step reporting protocol
  with the plateau mini-sweep, per-component or cosine-similarity agreement, the 50 %-per-decade
  flag, the 2.5-5 % harness floor, central differences with step 1e-3 to 1e-2 (`:853-868`); three
  table shapes — per-derivative `| derivative | analytic | FD | abs err | rel err |`, per-component
  `| idx | analytic | FD (step) | rel. err % | sign match |`, step sweep `| step | rel err |
  rel err (excl. flagged) | cosine | status |` (`:870-892`). `docs/charters/DAFOAM_CHARTER.md`
  §2 `:41-89` (aggregate named as `‖J_an − J_fd‖ / ‖J_fd‖`; complex-step or forward-AD is the
  reference where reachable `:66-73`), §3 `:90-126` (plateau per component), §4 `:127-155`
  (registered trivial baseline = same probe at a deliberately wrong step), §5 `:156-198`
  (decomposition disclosed), §9 `:331-373` (FD at the final design point, cap-stopped is never
  PASS). A gradient check certifies a contraction, not an operator: `docs/LESSONS.md` L-36 `:1689`.
- **Complex-step** — NAMED but NO STANDARD: `DAFOAM_CHARTER.md:62-73` names it as the preferred
  reference where a build exists and requires a record to state when it did not reach for it;
  `docs/COVERAGE_MATRIX.md:373` records that no complex-step build exists. No build, no procedure,
  no band. `docs/capability/dafoam_GRID.md` census: never performed anywhere in the family.
- **Dot-product / duality test** — NO STANDARD in the lab. `git grep -il 'dot.product\|duality'`
  over `docs/charters docs/standards scripts CLAUDE.md` returns nothing; the only mentions are
  `docs/LESSONS.md` L-29 `:1413` (a random-seed dot-product test as a contraction) and L-36
  `:1689` ("any dot-product/FD test ... at one point"), plus `docs/EXTERNAL_REFERENT_AUDIT.md`.
  `dafoam_GRID.md` census: never performed anywhere in the family.
- **np-invariance** — NO STANDARD as a gradient metric. The nearest clauses are DAFOAM §5
  (disclose the decomposition; serial before parallel), PARALLEL_GATE_DOCTRINE C1/C3 (primal
  reproducibility across a partition pair), N-D12 (a signature is only a signature within one rank
  count) and L-38 (an invariance check can pass with both sides wrong). No clause requires
  `J_adj(np_a)` vs `J_adj(np_b)` agreement or sets a band for it.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Dot-product (duality) test: with tangent operator `A` (forward linearisation, `dR/dw · v`) and
adjoint operator `A^T`, for random `v`, `w` compute `<A v, w>` and `<v, A^T w>`; report
`|<Av,w> - <v,A^T w>| / (|<Av,w>| + |<v,A^T w>|)`, pass at machine precision times a stated
condition-number allowance (order 1e-10 in double); one point certifies the operator pair at that
point only (L-36). np-invariance: the same adjoint gradient at two decompositions,
`delta_np = ‖J_adj(np_a) − J_adj(np_b)‖ / ‖J_adj(np_a)‖`, per DV and aggregate, with both partitions
pinned and disclosed (PARALLEL_GATE C1); a band for it must be frozen before the run and cannot
be looser than the FD band it accompanies. Complex-step: `dJ/dx_i = Im[ J(x + i h e_i) ] / h` with
`h ~ 1e-20`, no subtractive cancellation, and it becomes the reference in the §7 table's FD column
"when built" — until a build exists every record says so on its face (DAFOAM §2 `:71-73`).

---

## Census of this file

Items in Sanaa's §1-§6: 26. PRESENT — cited: 17. NAMED but no standard: 3 (complex-step,
dot-product/duality, np-invariance). ABSENT — summary written: 6 classes (L2/L∞ + MMS; absolute
convergence + partition metric; profile RMSE/error-bar fraction, explicit structure rows, unsteady
statistics; mass balance/boundedness/entropy). Not located at HEAD: an L-number for the 10^105
lesson (lives as N-AV12), for the 2.2e-5 finding (lives in PARALLEL_GATE_DOCTRINE §2/§4.5), and
for the "round-5 / scalar metrics can't see wrong structure" sentence (nearest: D214/D215).

## Footer — the planted control: every cited sha, resolved

Run from the repository root; every line must read `ok` (2 distinct shas cited: HEAD of the
citations and the K0cT record):

```
for s in 33dbe337 336a364d; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: 2 ok, 0 MISSING.

---

## Census per family

| family | table at HEAD | CAN DO | CAN DO, CAVEATS | CAN NOT DO (attempted) | CAN NOT DO — not attempted | unclassified cells |
|---|---|---|---|---|---|---|
| cfd | NOT YET LANDED (placeholder) | 0 | 0 | 0 | 36 | 0 |
| heat-transfer | NOT YET LANDED (placeholder) | 0 | 0 | 0 | 36 | 0 |
| dafoam | yes | 4 | 5 | 1 | 62 | 0 |

(Counts are per verdict cell: dafoam has two verdict columns per class, so its row sums to 72.)

---

## Footer — merged planted control: every distinct sha cited by every source, resolved

Run from the repository root; every line must read `ok`; 28 distinct shas across all sources:

```
for s in 0f56460d 15767999 1697ea49 2a93ff27 2b50394a 336a364d 33dbe337 35171866 3f8c6b13 4d9d902b 4eae12f4 52a213ad 5d1718df 5d1f89cd 60cfd4c8 65882eb3 66f42398 6b8d6355 9c241fe2 b10260a0 b26b875c b840fcd5 bb5088c4 be35dcad cffd90e7 ddb99eca f8916f36 f9a59d47; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at assembly time (2026-08-26T20:53Z, HEAD `299296a2`): **28 ok, 0 MISSING, 28 distinct shas.**
