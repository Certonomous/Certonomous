# CAPABILITY GRID — Sanaa's taxonomy, assembled from the family tables at HEAD

**Owner:** verification-supervisor. **Directive:** Sanaa's [SANAA-DIRECT] CAPABILITY GRID, boarded verbatim at commit `068c2bf0` (`docs/LAB_STATE.md`, CHIEF ADDENDUM 2026-08-26T17:35Z). **Assembled from HEAD `8146bc05`** on 2026-08-26T20:56Z by `scripts/assemble_capability_grid.py` (idempotent; reads only `git show HEAD:` blobs; zero compute). **FIRST DRAFT** — re-run when a family table lands.

**The verdict vocabulary (Sanaa's, exactly three):** `CAN DO — X cases` (ran successfully, metrics verified; strongest case cited by path + record sha + what was checked); `CAN DO, CAVEATS` (runs, credible results, named missing items each ≤ 1 line); `CAN NOT DO` (does not converge / does not reproduce literature / not enough compute / documented model defect — what was attempted, what would fix it; empty cell = `CAN NOT DO — not attempted`). One verdict per cell. The lab's fixed gate vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING) appears inside a cell as what the record says.

**Disclosed mapping rule (this supervisor's, from the lanes' common brief):** CAN DO requires at least one case whose record at HEAD says PASS (or GATE REACHED with every reached gate passing) under a frozen prereg with a CONVERGING Roache triple where a triple was claimed; anything weaker that still produced a credible graded number is CAN DO, CAVEATS; GATE FAIL / NOT A RESULT / BLOCKED-only cells are CAN NOT DO with the attempt named. Every citation must resolve at HEAD (`git cat-file -e <sha>^{commit}`); the merged footer below is the planted control.

**Order (Sanaa's):** cfd table, heat-transfer table, dafoam table, then the metrics summary.

---

## cfd

**family table at HEAD: `c5d96403`** (`docs/capability/cfd_GRID.md`; every cell below is copied verbatim from that file — the family supervisor's words, not this script's).

**Regime / mode per case, as derived by the family (their table):**

| case family | solver / conditions (path:line) | cell |
|---|---|---|
| F17 / F17b Kovasznay | `simpleFoam`, laminar, `steadyState`, **Re = 40**, 2-D — `verification/campaign/F17_KV40_PREREGISTRATION.md:27-28,53` | **2D · steady · incompressible** |
| F11 lid-driven cavity conversion | `simpleFoam`, laminar, Re 100 and Re 1000, n = 32/64/128 — `verification/runs/F11_runs/conversion_2026-08-25/RESULTS.md:12` | 2D · steady · incompressible |
| W1 hump (challenge), F6a Greenblatt hump | `simpleFoam`, `Re_c = 936,000, M = 0.1` — `verification/campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md:15-18` | 2D · steady · incompressible (turbulent) |
| F6b periodic hill vs ERCOFTAC | incompressible steady `simpleFoam`, streamwise-cyclic, 2-D, Re_H 10595 — `verification/campaign/F6b_ERCOFTAC_PREREGISTRATION.md:30,42`; `F6b_ERCOFTAC_RESULTS.md:60-62` | 2D · steady · incompressible (turbulent) |
| DPW8_V2 Joukowski airfoil | `simpleFoam`/`kOmegaSST`, **M = 0.15, Re_c = 6e6, incompressible** — `verification/campaign/DPW8_V2_joukowski.md:8-9` | 2D · steady · incompressible (turbulent) |
| F16 / F16b Stokes' second problem | `icoFoam`, `backward`, oscillating wall — `verification/campaign/F16b_SL2_PREREGISTRATION.md:41,49` | **2D · unsteady · incompressible** (1-D exact solution, slab mesh) |
| F18 / F18b Taylor–Green | `icoFoam`, periodic box, ν = 0.1 — `verification/campaign/F18_TG2D_PREREGISTRATION.md:37,42` | **2D · unsteady · incompressible** |
| F5 / F5a / F5b / R7 cylinder ladder | `pimpleFoam`, Re 1000 → 3900 — `verification/campaign/F5a_cylinder_reynolds_ladder.md:3,31-34` | 2D · unsteady · incompressible |
| F9 pulsatile valve | `pimpleFoam`, laminar, **5° axisymmetric wedge**, Womersley α ≈ 17, pipe Re ≈ 8,400 — `verification/campaign/F9_pulsatile_valve.md:58,70,74,78` | **axisym · unsteady · incompressible** |
| F20 isentropic vortex | `rhoCentralFoam`, 2-D inviscid, smooth compressible Euler exact solution, periodic box — `verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md:1,17,40` (advection Mach not read by this lane; no shock) | **2D · unsteady · subsonic-compressible** |
| F2 NACA0012, F12 RAE 2822 | `rhoSimpleFoam` + k-ω SST, M = 0.8 / M = 0.73–0.734, Re 6e6–6.5e6 — `verification/campaign/F2_transonic_naca0012.md:28,60`; `verification/campaign/F12_PREREGISTRATION.md:9,16-19` | **2D · steady · transonic** |
| F3 wedge + diamond, F3 successor | `rhoCentralFoam`, M 2.0 / 2.5 / 3.0, single-cell-thick 2-D slabs — `verification/campaign/F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md:57,81`; `F3_CONVERSION_PREREGISTRATION.md:92-93` | **2D · steady · supersonic** |
| F3 cone (Taylor–Maccoll) | same suite; *"the cone is a single-cell-thick axisymmetric wedge slice"* — `verification/campaign/F3_CONVERSION_PREREGISTRATION.md:206`; `F3_supersonic_exact_theory.md:45-47` | **axisym · steady · supersonic** |
| F15 / F15-R2 oblique-shock reflection | `rhoCentralFoam`, inviscid, **M = 2.9**, steady state by pseudo-time marching — `verification/campaign/F15_OSR29_PREREGISTRATION.md:57-58,95-97` | 2D · steady · supersonic |
| F19 Sod shock tube | `rhoCentralFoam`, 1-D Euler, Toro Test 1, one cell in y and z — `verification/campaign/F19_SOD_PREREGISTRATION.md:1,16,37` | **2D · unsteady · supersonic** (1-D, filed in the 2D row) |
| F4 / F4S blunt cylinder | `rhoCentralFoam`, **cyl × M ∈ {6.0, 7.0, 8.0}**, Billig standoff — `verification/runs/F4_runs/successor_2026-08-26/RESULTS.md:9`; `verification/campaign/F4S_SHOCK_LOCUS_PREREGISTRATION.md:146` | **2D · steady · hypersonic** |
| DMR double Mach reflection | `rhoCentralFoam`, inviscid, 2-D, **Mach-10 shock** inclined 60° — `verification/campaign/DMR_PREREGISTRATION.md:6,19-20` | **2D · unsteady · hypersonic** |
| F7 / F7a dam break | `interFoam` (VOF, laminar), Martin & Moyce column — `verification/campaign/F7_marine_free_surface.md:8,19` | **2D · unsteady · multiphase-free-surface** |
| R4 / W3 / B52 / F5c / F8 / D5 / F10 3-D bodies | `simpleFoam` RANS: Ahmed 25° (`R4_ASYMPTOTIC_RESULTS.md:41`), NACA 0012/4412 finite wings (`W3_WING_VALID_FAMILY_RESULTS.md:17,26`), UAE Phase VI MRF (`F8_MRF_HAND2001_GATE.md:6`), square duct RSM vs DNS (`D5_RSM_RESULT.md:7`) | **3D · steady · incompressible** |
| F1 / F13 ONERA M6, hlpw6, committee-grids DPW5 | ONERA M6 M 0.84 (`F13_RESULTS.md`); CRM at **M = 0.850** (`cases/committee-grids/COMMITTEE_GRID_NUMERICS.md:64`; `cases/hlpw6/FEASIBILITY_PROBE.md:83`) | **3D · steady · transonic** |

**The table:**

| cell | verdict |
|---|---|
| **2D · steady · incompressible** | **CAN DO — 1 case at the bar, 4 more graded below it.** Strongest: **F17-KV40 Kovasznay `verification/campaign/F17_KV40_RESULTS.md` @ `f018c8bf`** — G-F17-1 E2 velocity **`PASS`**, CONVERGING p **2.0990**, in band; G-F17-2 u(0.5, 0) = 0.382441 vs exact 0.382373 **`PASS`**, CONVERGING p **2.0699** (`:20-21`); prereg frozen `4ad083fb`, registered prediction MET (`:31`), 10 planted controls passed (`:55`). Checked: L2 error norm vs exact + observed order vs formal 2 (Sanaa §1/§2). Turbulent sub-class carries no `PASS` under a frozen prereg: W1 hump challenge (`W1_HUMP_CHALLENGE_RESULTS.md` @ `a1fbe127`) Gate V "PASS", separation −1.59 % "PASS", **reattachment +13.92 % "FAIL"** (`:21,36`); F6b periodic hill (`F6b_ERCOFTAC_RESULTS.md` @ `a1fbe127`) Gate V "PASS", **Gate P "FAIL" by over-prediction as pre-registered**, Gate Q "PASS" (`:12,20,28`); F6a Greenblatt attempt 3 `NOT A RESULT` (`verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k/result.json` @ `14018d5b`, `ROW_VERDICT`); F11 cavity conversion **`NOT A RESULT` ×6 with every band `PASS`** — coarse plateau UNMEASURED (`verification/runs/F11_runs/conversion_2026-08-25/RESULTS.md:3,14,22-27` @ `193b522c`); DPW8_V2 Joukowski L1/L3 "PASS" vs analytic (`DPW8_V2_joukowski.md:80-81` @ `a1fbe127`) but **no frozen prereg** and L4 `NOT GATED` (`DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md:20` @ `b8fe7eea`). |
| **2D · steady · subsonic-compressible** | CAN NOT DO — not attempted (no `rhoSimpleFoam`/`rhoPimpleFoam` case registered below M ≈ 0.7; the compressible steady line went straight to transonic F2/F12). |
| **2D · steady · transonic** | **CAN NOT DO — attempted 2 cases.** F12 RAE 2822 (`verification/campaign/F12_RESULTS.md` @ `a1ac1c21`): **`GATE FAIL`** — admission Gate A max non-orthogonality **70.646 / 70.861 / 72.542° at all three levels against a frozen ≤ 70°** (`:99,112-114`), Gate B convergence **`GATE FAIL`** (`:158`); rungs 2–5 `BLOCKED` on the rate-calibration interlock (rung-1 record `verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/RESULTS_RUNG1.md` @ `c69ce11c`). F2 NACA0012 M 0.8 (`F2_transonic_naca0012.md` @ `a1fbe127`): pre-vocabulary record, **no frozen pre-registration**, coverage tier SURVEYED — not citable as a verdict. What would fix it: a new F12 rung-1 registration on a C-mesh that clears ≤ 70° at every level before the freeze. |
| **2D · steady · supersonic** | **CAN DO, CAVEATS — 1 `PASS` row on a CONVERGING triple, 6 rows not.** Strongest: **F3 conversion `verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md` @ `5adb9c5d`** — G-F3-5 diamond wave drag / M2.0_eps7p125 **`PASS`**, −0.258 % vs shock-expansion exact, ±1.0 % band, CONVERGING, **p = 6.296, GCI 0.0001 %** (`:19`); prereg frozen `3574cdcb` (`F3_CONVERSION_PREREGISTRATION.md:92-95`). Caveats: p = 6.296 against a formal 2 is not an asymptotic triple; the successor re-run of the same family at M2.5 graded **G-F3S-5 `NOT A RESULT` (OSCILLATORY)** and G-F3S-1/-2 wedge rows `NOT A RESULT` (`verification/runs/F3_runs/successor_triple_2026-08-26/RESULTS.md:17-19` @ `8273e4ad`); G-F3-1 wedge pressure M2.0 `NOT A RESULT` OSCILLATORY (`:11`); G-F3-2 wedge shock angle M2.0 **re-graded `PASS` → `NOT A RESULT`, DEGENERATE |p| = 0.034 < 0.05** under Sanaa's "OK for this" (`:102-114`); M3.0 rows `PASS` on a single level only (`:13,16`); three rows `PENDING` (fine never launched); F15 oblique-shock reflection M 2.9 **`PENDING` ×2** by the frozen comparator and F15-R2 **REFUSED rc 2** on a reader defect (`verification/runs/F15_runs/RESULTS_R2.md:1,18-20,31-33` @ `3c21d87c`; prereg `2aea29d9`). Checked: surface-pressure / wave-drag deviation vs exact theory + Roache triple. |
| **2D · steady · hypersonic** | **CAN DO — 3 cases (M 6.0 / 7.0 / 8.0).** Strongest: **F4S `verification/runs/F4_runs/successor_2026-08-26/RESULTS.md` @ `3663520c`** — G-F4S-1 RH mid-density crossing of the bow-shock standoff δ/R: M6.0 **`PASS`** CONVERGING p 1.098, GCI 0.45 %, **+1.59 % vs Billig**; M7.0 **`PASS`** p 1.058, GCI 0.73 %, +1.07 %; M8.0 **`PASS`** p 2.599, GCI 0.07 %, +0.50 % (`:100,102,104`); prereg frozen `d98868fb` (`F4S_SHOCK_LOCUS_PREREGISTRATION.md:146`), registered prediction "CONVERGING at ≥ 2 of 3" MET 3/3; planted zero read back on all six rows. Checked: shock standoff vs the Billig (1967) correlation (a correlation — scores V, never P, Sanaa §1) + GCI + observed order. Named, not a caveat on the standoff: the predecessor argmax detector G-F4S-1B `NOT A RESULT` ×2 (DIVERGENT / OSCILLATORY) and `PASS` ×1 (`:101,103,105`); the F4 conversion itself closed **`NOT A RESULT` ×11** (`verification/runs/F4_runs/conversion_2026-08-25/RESULTS.md` @ `d4308dde`); the Cp-vs-modified-Newtonian limb stays `PENDING` on a citable reference uncertainty; single geometry (cylinder). |
| **2D · steady · multiphase-free-surface** | CAN NOT DO — not attempted. |
| **2D · unsteady · incompressible** | **CAN DO — 2 cases, plus 1 more graded `PASS` on the same line.** Strongest: **F16b-SL2 Stokes' second problem `verification/runs/F16b_runs/RESULTS.md` @ `49c95cc7`** — G-F16-1 E2 profile **`PASS`**, CONVERGING p **1.8252**; G-F16-2 u(δ) = −0.309394 vs exact −0.309560 **`PASS`**, CONVERGING p **1.9930** (`:21-22`), prereg frozen `cadb4887`, 9 controls passed (`:53`). **F18-TG2D Taylor–Green `verification/campaign/F18_TG2D_RESULTS.md` @ `3f87e759`** — G-F18-1 E2 **`PASS`** CONVERGING, G-F18-2 box-mean KE 0.1123375 vs exact 0.1123322 **`PASS`** CONVERGING (`:20-21`), prereg `c4f72b27`; **observed p 1.289 / 0.964 against the registered ≈ 2 — a miss of the prediction, not of the gate** (`:38-40`; coarse level pre-asymptotic). Checked: L2 error norm vs exact + observed order + kinetic-energy exact value. Named: F16 itself **`NOT A RESULT` on physics — identically zero solution from an `empty` ±x declaration** (`verification/runs/F16_runs/RESULTS_R2.md:78-90` @ `5889677b`); the cylinder ladder F5b physics probe **`NOT A RESULT`** on a completion clause (`verification/runs/F5b_runs/physics_p1/RESULTS.md:3` @ `da65ae38`) and F5a Re 1000/2000 rungs carry Cd/St numbers with no frozen prereg and no rule-1 verdict (`F5a_cylinder_reynolds_ladder.md:31-34` @ `a1fbe127`); F18b (889 core-min) in flight, no record yet. |
| **2D · unsteady · subsonic-compressible** | **CAN DO — 1 case.** **F20 isentropic vortex `verification/runs/F20_ISENTROPIC_VORTEX_runs/F20_GRADED.json` @ `ca6a3164`** — `rows[0]` G-F20-1 E2 density at T: coarse 3.342e−03 → medium 1.437e−03 → fine 1.160e−03, triple **CONVERGING**, in band, **`PASS`**; `rows[1]` G-F20-2 mean kinetic energy 1.0055388 in band [1.0049159, 1.0063512], **CONVERGING**, **`PASS`**; frozen `grade_f20.py` at prereg `548fc02e` (`F20_ISENTROPIC_VORTEX_PREREGISTRATION.md:1,17,40`). Checked: L2 density error vs exact + KE + Roache triple. Caveats stated because the commit message records them and this lane did not open the prose record (`RESULTS.md` for F20 is on disk but NOT at HEAD at write time): G-F20-1's observed order **2.78 fell outside the registered order range**, and G-F20-2 was **registered `NOT A RESULT` and came out CONVERGING** — a prediction miss on both rows; freestream Mach not read by this lane. |
| **2D · unsteady · transonic** | CAN NOT DO — not attempted. |
| **2D · unsteady · supersonic** | **CAN DO, CAVEATS — 1 case, 1 of 2 gates.** **F19 Sod shock tube `verification/campaign/F19_SOD_RESULTS.md` @ `08aa454c`** — G-F19-1 L1 density error **4.400e−04** in band, CONVERGING **p 1.018**, **`PASS`** (`:21`); G-F19-2 shock position 0.850540 vs exact 0.850431 **in band but `NOT A RESULT` — triple DEGENERATE, |p| = 0.032 < P_MIN 0.05** (`:22,42-49`); prereg frozen `3053d9ec`. Checked: L1 norm vs the exact Riemann solution + observed order (limited scheme, first order expected). Caveats: 1-D slab filed in the 2D row; shock-position triple degenerate (equal increments); one gate of two. |
| **2D · unsteady · hypersonic** | **CAN DO, CAVEATS — 1 case, pre-vocabulary record.** **DMR double Mach reflection `verification/campaign/DMR_RESULTS.md` @ `a1fbe127`** — Gate V incident-shock kinematics vs exact theory "PASS" at both rungs: res120 shock speed 2.99328 vs 3 (**0.15 %**), res60 **0.17 %** (`:23,30-31`); rung-to-rung clause "PASS" (`:78`); Gate P1 double-Mach structure detector **"FAIL as registered, left standing"** (`:37,51`); prereg `DMR_PREREGISTRATION.md` @ `a1fbe127` (`:6,19-20`; frozen `74797a57` before any mesh existed per the record). Caveats: two resolutions, **no Roache triple**; verdict words are pre-rule-1 "PASS/FAIL"; the structure gate failed; no Woodward–Colella numeric reference obtainable (`DMR_PREREGISTRATION.md:53-65`). |
| **2D · unsteady · multiphase-free-surface** | **CAN NOT DO — attempted 1 case (F7 dam break, `interFoam`).** `verification/campaign/F7_marine_free_surface.md` @ `3b9bcf31`: feasibility pass, **GATE "FAIL" — front position +8.2 % mean / +11.0 % max against a declared 5 % tolerance** (`:19,119`); F7a re-gate at zero compute pins the measurement definition and **refutes the ambiguity hypothesis — every reading lands +7.8 % to +11.9 %, all FAIL** (`verification/campaign/F7a_REGATE_SPEC.md:176` @ `85e2230f`); Martin & Moyce (1952) primary `NOT OBTAINED` (coverage matrix §3.8e). What would fix it: the primary tabulated data on disk, a frozen prereg, a mesh triple, and a physics reason for the +8 % (VOF laminar column with a slip/no-slip floor question open). |
| **axisym · steady · incompressible** | CAN NOT DO — not attempted in the cfd family (F9's `steady_beta_50deg` / `steady_q75` wedge runs exist under `verification/runs/F9_work/` with no graded record; the Ansys VMFL005/002/003/036 pipe and sphere wedges are in `ansys_ROWS.md`). |
| **axisym · steady · subsonic-compressible** | CAN NOT DO — not attempted. |
| **axisym · steady · transonic** | CAN NOT DO — not attempted. |
| **axisym · steady · supersonic** | **CAN DO, CAVEATS — 1 case, 1 of 2 gates.** **F3 cone (Taylor–Maccoll) `verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md` @ `5adb9c5d`** — G-F3-3 cone surface pressure **`PASS`**, +0.287 % vs exact Taylor–Maccoll, ±0.5 %, CONVERGING **p = 2.541, GCI 0.044 %** (`:17`); **G-F3-4 cone shock angle `GATE FAIL`, +2.139 % against ±2.0 %**, CONVERGING p 0.800, GCI 4.969 % (`:18,28`); prereg frozen `3574cdcb` (`:94-95`; axisymmetric wedge slice `:206`). Checked: surface pressure vs exact conical-flow theory + GCI. Caveats: shock-angle gate fails by 0.139 points; the shock-angle detector's own GCI (5 %) exceeds the band; single Mach/half-angle (M2.35, θ10). |
| **axisym · steady · hypersonic** | CAN NOT DO — not attempted. |
| **axisym · steady · multiphase-free-surface** | CAN NOT DO — not attempted (Ansys VMFL021/022 cavitating orifice wedges are in `ansys_ROWS.md`). |
| **axisym · unsteady · incompressible** | **CAN DO, CAVEATS — 1 case, pre-vocabulary record.** **F9 pulsatile valve `verification/campaign/F9_pulsatile_valve.md` @ `a1fbe127`** — `pimpleFoam` laminar on a 5° wedge; FEASIBILITY "PASS", PHYSICS "PASS", periodicity "PASS" (`:101,107,137`); Gate 1 quasi-steady limit **"PASS, both runs" within 1.6 %** (`:156`); **Gate 2 Womersley profile "FAIL" as a point comparison** against the closed form (`:183`). Caveats: no frozen prereg; **Womersley (1955) not held on disk** (coverage §3.8e); single mesh, no triple; laminar at pipe Re ≈ 8,400 by design (`:70-79`). |
| **axisym · unsteady · subsonic-compressible** | CAN NOT DO — not attempted. |
| **axisym · unsteady · transonic** | CAN NOT DO — not attempted. |
| **axisym · unsteady · supersonic** | CAN NOT DO — not attempted. |
| **axisym · unsteady · hypersonic** | CAN NOT DO — not attempted. |
| **axisym · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted. |
| **3D · steady · incompressible** | **CAN NOT DO — attempted, many solves, no gate passed under a frozen prereg with a converging triple.** Ahmed 25° R4 ladder: **non-monotone, the "turn" WITHDRAWN as a feature** (chief ruling `8f5bf878`; `verification/campaign/R4_ASYMPTOTIC_RESULTS.md:1,97` @ `a1fbe127`); NACA 0012 / 4412 finite wings: *"this wing's drag cannot be refined past about …"* — ladders non-monotone (`W3_WING_VALID_FAMILY_RESULTS.md:112,148-149` @ `a1fbe127`); UAE Phase VI MRF vs Hand et al. (2001): **"NO VERDICT"**, torque reference never fetched (`F8_MRF_HAND2001_GATE.md:20,43-56` @ `a1fbe127`); square-duct RSM vs DNS: SSG 55 % / LRR 207 % / EBRSM 52 % of the DNS secondary flow, *"two of four right"* (`D5_RSM_RESULT.md:14-29` @ `a1fbe127`); F5c stage A "RECORDED, NOT SCORED" (`F5C_STAGE_A_RESULTS.md:16` @ `a1fbe127`); B52 replicates and W3 cube-settle are instrument audits without an external gate. What would fix it: one 3-D case with a frozen prereg, a converging triple and a held experimental reference — the coverage matrix names the Ansys `EXP` reservoir; in-family, Ahmed with the R4 recipe carried to a converging r = 2 family. |
| **3D · steady · subsonic-compressible** | CAN NOT DO — not attempted (no 3-D `rhoSimpleFoam` case below transonic; the DAFoam A2 MACH wing at M ≈ 0.29 belongs to `dafoam_GRID.md`). |
| **3D · steady · transonic** | **CAN NOT DO — attempted 2 cases, both `GATE FAIL` at mesh admission.** F13 ONERA M6 (`verification/campaign/F13_RESULTS.md` @ `16b81323`): R0 **`GATE FAIL` — max non-orthogonality 84.64 / 86.02 / 86.78° against ≤ 70°, worsening with refinement** (`:15,27`); R1–R4 `PENDING`, never launched; case **`BLOCKED` on §5 admission** (`:46`). F1 v2 butterfly tip-fill trial (`verification/runs/F1_MESH_TRIALS_2026-08-25/TRIAL_RESULTS.md` @ `d846815c`): **81.94 / 83.88 / 83.64° against ≤ 70°** (`:35`); F1 itself has no pre-registration (coverage §3.8e). CRM committee grids (DPW5 / HLPW6): mesh conversion and feasibility probes only, no solve graded (`cases/committee-grids/COMMITTEE_GRID_NUMERICS.md` and `cases/hlpw6/FEASIBILITY_PROBE.md` @ `ddb99eca`). What would fix it: build and `checkMesh`-admit ONE level ≤ 70° (unstructured or collapsed-tip topology) before freezing a ladder — the cfd-supervisor's own ordering on the board. |
| **3D · steady · supersonic** | CAN NOT DO — not attempted. |
| **3D · steady · hypersonic** | CAN NOT DO — not attempted. |
| **3D · steady · multiphase-free-surface** | CAN NOT DO — not attempted (F7c DTMB 5415 staging plan exists, `verification/campaign/F7c_DTMB5415_STAGING_PLAN.md`; nothing run). |
| **3D · unsteady · incompressible** | CAN NOT DO — not attempted (every cylinder rung is a 2-D slab; no 3-D LES/URANS record). |
| **3D · unsteady · subsonic-compressible** | CAN NOT DO — not attempted. |
| **3D · unsteady · transonic** | CAN NOT DO — not attempted. |
| **3D · unsteady · supersonic** | CAN NOT DO — not attempted. |
| **3D · unsteady · hypersonic** | CAN NOT DO — not attempted. |
| **3D · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted. |

**Census (36 cells):** **CAN DO 4** (2D·steady·incompressible, 2D·steady·hypersonic, 2D·unsteady·incompressible, 2D·unsteady·subsonic-compressible); **CAN DO, CAVEATS 5** (2D·steady·supersonic, 2D·unsteady·supersonic, 2D·unsteady·hypersonic, axisym·steady·supersonic, axisym·unsteady·incompressible); **CAN NOT DO — attempted 4** (2D·steady·transonic, 2D·unsteady·multiphase, 3D·steady·incompressible, 3D·steady·transonic); **CAN NOT DO — not attempted 23**. Every `CAN DO` sits on an exact-solution or correlation reference — **validation against measured physical reality (Sanaa §3, coverage-matrix P) is green in no cfd cell**; the only experiment-gated rows in the family (W1 hump reattachment, F6b hill reattachment, F7 dam break) are FAIL/GATE FAIL. Checks never performed anywhere in the family, stated so the grid cannot imply them: method of manufactured solutions; ASME V&V 20 `u_val` (used once lab-wide, K0cT, heat-transfer); spectra/phase-averaged statistics on any unsteady case.

---

## heat-transfer

**family table at HEAD: `8146bc05`** (`docs/capability/heat-transfer_GRID.md`; every cell below is copied verbatim from that file — the family supervisor's words, not this script's).

**Regime / mode per case, as derived by the family (their table):**

| case | mode · regime · dimension | solver / conditions (path:line) |
|---|---|---|
| T9a composite wall + fin | conduction · no flow · 2D | `laplacianFoam`, exact composite-wall and fin theory; "a two-dimensional solve disagreeing with one-dimensional theory" — `docs/campaigns/T-family/T9a_RESULTS.md:108`, `:196` |
| T11 transient plane wall | conduction · no flow · 2D (1-D slab) | `laplacianFoam`, convective **Robin** BC (`mixed`) at `x = L`, "One-dimensional transient conduction in a plane wall" — `docs/campaigns/T-family/T11_PREREGISTRATION.md:61`, `:112`, `:116` (L-341) |
| T1c laminar pipe | forced conv · laminar · axisym | wedge, `f·Re = 64`, `Nu = 48/11`, Graetz `λ₀² = 7.313587` — `docs/campaigns/T-family/T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md:28`, `:43`; `T1c_RESULTS.md:26-28` |
| T1b turbulent pipe | forced conv · turbulent · axisym | `kOmegaSST`, `Re` 1e4 / 3e4 / 1e5 / 3e5, reference midpoint of Dittus–Boelter and Gnielinski — `docs/campaigns/T-family/T1b_RESULTS.md:22`, `:302` |
| T3 heated backward-facing step | forced conv · turbulent · 2D | `kOmegaSST`, air, `Re_H = 28 000`, 2D by design — `docs/campaigns/T-family/T3_PREREGISTRATION.md:20`, `:27`, `:107` |
| T4 impinging round jet | forced conv · turbulent · axisym | `kOmegaSST`, `buoyantBoussinesqSimpleFoam`, `H/D = 2`, `Re_D = 23 000`, axisymmetric 2.5° wedge — `docs/campaigns/T-family/T4_PREREGISTRATION.md:43`, `:108-109` |
| K0c differentially heated square cavity | natural conv · laminar · 2D | `buoyantBoussinesqSimpleFoam`, `Ra` 1e3–1e6, mesh pairs 32/64 … 128/192 — `docs/campaigns/F14-cooling-ladder/K0c_RESULTS.md:1`, `:111-112`, `:200` |
| K0b cavity capability rung (D403 re-run, D406 repair) | natural conv · laminar · 2D | `Ra` 1e5, 32/64/128 ladder, `Pr = 0.706814`, "graded against no published datum" — `docs/campaigns/F14-cooling-ladder/K0b_D403_RERUN_RESULTS.md:16`, `:182`; `K0c_RESULTS.md:335` |
| K0cS square cavity | natural conv · turbulent · 2D | `kOmegaSST` / `kEpsilon` / `LaunderSharmaKE`, `Ra` 1.58e9, Ampofo & Karayiannis 2003 — `docs/campaigns/F14-cooling-ladder/K0cS_RESULTS.md:1-6`, `:18-21`, `:61` |
| K0cT tall cavity | natural conv · turbulent · 2D | `Ra` 0.86e6 / 1.43e6, AR 28.7, ERCOFTAC Case 079 (Betts & Bokhari) — `docs/campaigns/F14-cooling-ladder/K0cT_RESULTS.md:10-11`, `:19` |
| K0cX cross-geometry, K0cG third level, K0cP/Q/R diagnosis | natural conv · turbulent · 2D | three closures across both cavities — `K0cX_RESULTS.md:420-424`; `K0cG_RESULTS.md:27-34` |
| T8 MTT pure plume | natural conv · turbulent · axisym | axisymmetric 5° wedge, turbulent pure plume, steady `buoyantBoussinesqSimpleFoam` — `docs/campaigns/T-family/T8_PREREGISTRATION.md:70-73` |
| K2b rack-row pilot | mixed conv · turbulent · 2D | `buoyantBoussinesqSimpleFoam`, `RASModel kOmegaSST` — `K2b_PILOT_RESULTS.md:44`; `verification/runs/F14-cooling-ladder/K2b_runs/K2bP_coarse/constant/turbulenceProperties` |
| K0d / K0f Blay ventilated cavity | mixed conv · turbulent · 2D | 2D, `x, y ∈ [0, 1.04]`, Blay–Mergui–Niculae 1992 `NOT OBTAINED` — `docs/campaigns/F14-cooling-ladder/K0f_PREREGISTRATION.md:55`, `:69-70` |
| T5 heated wall-mounted cube | conjugate · turbulent · 3D | `chtMultiRegionSimpleFoam`, steady wall-resolved `kOmegaSST`, `Re_H` 2500–5000, Meinders 1998 — `docs/campaigns/T-family/T5_PREREGISTRATION.md:32`, `:44`, `:55` @ `299296a2` |
| T10a view-factor enclosures | radiation · no flow · 3D | `viewFactorsGen` surface-to-surface, black box and grey concentric spheres, closed-form view factors — `docs/campaigns/T-family/T10a_RESULTS.md:1-8` |

**The table:**

| cell | verdict |
|---|---|
| **conduction · laminar (no flow) · 2D** | **CAN DO — 2 cases** (T9a composite wall + fin; T11 transient plane wall); **strongest case `docs/campaigns/T-family/T9a_RESULTS.md` @ `0cbaea26`**, comparator frozen at `239ed2b8` before any case existed (`:7`), pre-registration `docs/campaigns/T-family/T9a_PREREGISTRATION.md` @ `6753e912`; checked: exact-theory error with a CONVERGING triple + GCI per row — **R0 wall `q″` `PASS` 19.854991 vs 19.502682, dev 1.806 % on a 2.043 % GCI band, p 1.079; R2 interface-2 `T` `PASS` −0.51 mK on a 0.75 mK band, p 0.952** (`:38`, `:40`); planted-zero control in the comparator. Also on the record and stated so the cell cannot imply otherwise: **R1 hot-side interface `GATE FAIL` −2.41 mK against a 0.92 mK band (p 1.738), cause CONFIRMED as the interface scheme** (`:39`; T9aD @ `a74b2f61`, T9aH @ `b698dfc3` diagnose it and grade no T9a row); R3/R4 fin rows `GATE REACHED` — bands 0.00077 % / 0.00011 % below the 0.025 % O(Bi) floor, reported not graded (`:41-42`). T11: `PASS` ×3 EXACT tier, p 2.000 / 2.000 / 2.005, GCI 2.9e-07 / 1.4e-06 / 3.4e-06 on a ±1e-4 band, Robin BC, `P_MIN` ruled 0.5 — **but its `gate_t11.json`, `STATUS.T11_PW_{c,m,f}` and DONE markers are ON DISK and NOT AT HEAD** (`git ls-tree HEAD verification/runs/T-family/T11_runs/` holds only the instruments and the C-T control); the tracked witnesses are the calibration row `docs/COST_CALIBRATION.md` C-118 @ `6becf266` and the pre-registration @ `f5f67de7` (frozen `ca9aad86`, amendments `352aef0d`, `f5f67de7`). T11 is therefore counted as a case but is not the citation. |
| **conduction · laminar (no flow) · axisym** | CAN NOT DO — not attempted |
| **conduction · laminar (no flow) · 3D** | CAN NOT DO — not attempted |
| **conduction · turbulent · 2D** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **conduction · turbulent · axisym** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **conduction · turbulent · 3D** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **forced conv · laminar · 2D** | CAN NOT DO — not attempted as a graded heat-transfer class. Named so nobody counts them: K0e flat plate is a **specification only, zero compute** (`docs/campaigns/F14-cooling-ladder/K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` @ `4b336fad`); E4a2 fan-pressure BC `PASS` 8 of 8 (`Q` dev 0.144 %, p 1.959, GCI 0.393 %; `docs/campaigns/T-family/E4a2_RESULTS.md` @ `2d639d3b`) backs a **flow** boundary condition, not a heat-transfer quantity; KV1 validated the heat-balance instrument on a laminar duct (`docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md` @ `65684e7c`, `:524` "KV1 is a laminar rung") and grades no case. |
| **forced conv · laminar · axisym** | **CAN DO — 1 case** (T1c laminar pipe, wedge); **strongest case `docs/campaigns/T-family/T1c_RESULTS.md` @ `2f1d6cb7`**, pre-registration `docs/campaigns/T-family/T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md` @ `e6d53dbd` (written "before any case was built or solved", `:3`); checked: exact-theory error norm with GCI band — **L2 constant-`q″` `Nu` `PASS` 4.365298 vs 48/11 = 4.3636364, dev 0.0381 % on a 0.0459 % band, CONVERGING p 2.031; L1/L3 `f·Re` `PASS` 63.98771 vs 64, dev 0.0192 % on 0.0236 %** (`:15-17`); references re-derived by the comparator, which refuses if they do not reproduce (`:26-28`). Also on the record: **L0 constant-`Ts` `Nu` `GATE FAIL` 3.659958 vs 3.6567934, dev 0.0865 % against a 0.0301 % band, p 1.854** (`:14`; "The GATE FAIL is real and is not excused", `:123`) and **L4 `NOT A RESULT`** (station as originally registered, no band armed, `:18`); the rung verdict line reads "GATE FAIL — 1 of 4 graded rows failed" (`:6`); L1/L3 carry a band but print no observed order. |
| **forced conv · laminar · 3D** | CAN NOT DO — not attempted |
| **forced conv · turbulent · 2D** | **CAN NOT DO** — attempted: **T3 heated backward-facing step, `Re_H` 28 000, `kOmegaSST`: `NOT A RESULT` 4 of 4 graded rows** — "Every ladder level is NOT CONVERGED against the registered `1e-6` criterion and every graded triple is DIVERGENT or OSCILLATORY, so gates (1) and (2) … fire ahead of gate (3)" (`docs/campaigns/T-family/T3_RESULTS.md:14-22` @ `2f1d6cb7`; comparator frozen `628ef452` +73 s before the first case, `:6-8`); G2 `x_peak/H` later reads CONVERGING p 4.304, GCI 0.0188 % with G3/G4 STAGNANT (§15), which cannot lift a row past gate (1). The primary (Vogel & Eaton 1985) is **NOT OBTAINED** and would be disqualifying on its own. What would fix it: the fourth level `R_ff` (602 128 cells, 8 ranks, POINT 18 218 core-min) is pre-registered, costed and built (`docs/campaigns/T-family/T3_R_FF_PREREGISTRATION.md` @ `ba023a53`) — its first runner launch was REFUSED at zero compute by the launcher's own cwd guard, amendment ordered; and a held primary. |
| **forced conv · turbulent · axisym** | **CAN NOT DO** — attempted three ways, none closing. (1) **T1b turbulent pipe `Nu`, `Re` 1e4 / 3e4 / 1e5 / 3e5, `kOmegaSST`**: the frozen comparator returns `PASS` ×4 (`gate_t1b.json`) **on triples that are DIVERGENT / DIVERGENT / DIVERGENT / STAGNANT (p −0.219, −0.150, −0.059, +0.010) — under standing rule 5 all four read `NOT A RESULT`** (`docs/campaigns/T-family/T1b_RESULTS.md` §8 "every row passes on a triple that is not converging", §11 @ `71388f4e`); the `PASS` band is the correlation midpoint band, **not a GCI** — "the GCI of the x level is printed beside the verdict and does not replace the band" (`docs/campaigns/T-family/T1b_L4_AMENDMENT.md:120-129` @ `17209b50`); deviations 0.08–2.4 % against Dittus–Boelter/Gnielinski are credible in size and unverified in the lab's sense. L4 ext1 (fourth level): `NOT A RESULT` ×4, every (m, f, x) triple STAGNANT (`verification/runs/T-family/T1_runs/gate_t1b_L4.json` @ `71388f4e`). T1b attempt 1: `NOT A RESULT`, all 19 cases, 56.6 core-h discarded (`docs/campaigns/T-family/T1b_ATTEMPT1_MESH_FAULT.md:4-5` @ `4e6ba646`). (2) **T4 impinging round jet `H/D` 2, `Re_D` 23 000: `NOT A RESULT` ×3** — c and f not iteratively converged; triples DIVERGENT / OSCILLATORY / OSCILLATORY; control C1 (y+ < 1) fired on `c` at y+ 1.248 (`docs/campaigns/T-family/T4_RESULTS_2026-08-26.md:53`, `:86-88` @ `7422591b`; `gate_t4.json` same sha). (3) T4b successor (y+ < 1 on `c`, controls inside the frozen comparator, prereg `51618879`): `IJ_c` and `IJ_m` reached STATUS rc=0 under a dead fleet, `IJ_f` live — `PENDING`, ungraded. What would fix it: a level pair that converges (T1b has none in seven levels; T4b is the registered attempt). |
| **forced conv · turbulent · 3D** | CAN NOT DO — not attempted (the only 3D turbulent case, T5, is conjugate — see that cell; its 2D precursor `X_2d` is a flow-only channel). |
| **natural conv · laminar · 2D** | **CAN DO, CAVEATS — 1 graded case** (K0c differentially heated square cavity, `Ra` 1e3–1e6); **strongest case `docs/campaigns/F14-cooling-ladder/K0c_RESULTS.md` @ `8590c96a`**, gate specification written first at zero compute (`docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md` @ `6d149d51`), reference values and bands parsed from it at run time; checked: benchmark deviation — **"GATE PASS, 0 of 20 GRADED rows failed, with 4 identity rows reported and counted toward nothing"** (`:546`, the dated correction in force; the record's compound "GATE PASS" is the family's word for a whole-rung `PASS`), largest deviation 1.139 % on a 3 % band; planted control fires at 3.19 %. Caveats: **mesh PAIRS only — no Roache triple, no GCI, no observed order exists for K0c** (`docs/COVERAGE_MATRIX.md` §3.4: the "p 1.94–2.33" once attributed to it belongs to K0b, whose record disclaims the reference at `K0c_RESULTS.md:335`); **reference is SECONDARY** (de Vahl Davis via Han & Xie 2019; the 1983 original not read); the K0b capability rung's unaided reproduction **`GATE FAIL` V3 — 128×128 `Nu_avg_hot` 4.490 % below the published value at observed order −1.25 against +1.94** (`K0b_D403_RERUN_RESULTS.md:16` @ `3d28328c`), repaired to `PASS` ×4 W1–W4 bit-identical (`K0b_D406_REPAIR_RESULTS.md` @ `f279aac5`) — "graded against no published datum"; K0a/K0b feasibility rungs "validated against no published reference datum" (`verification/runs/THERMAL_K0_runs/README.md:12` @ `a1fbe127`); K2e Boussinesq-limit sweep is solver-backed, no gate on the world (`K2e_RESULTS.md` @ `b845b603`). |
| **natural conv · laminar · axisym** | CAN NOT DO — not attempted |
| **natural conv · laminar · 3D** | CAN NOT DO — not attempted (every buoyant cavity this lab owns is 2D) |
| **natural conv · turbulent · 2D** | **CAN NOT DO** — attempted with three closures on two validated experiments, **closed validation loops, every one `GATE FAIL`**: **K0cS square cavity `Ra` 1.58e9 (Ampofo & Karayiannis 2003, read in full, Fig. 11 digitised): rung `GATE FAIL` 14 of 20 graded rows — `kOmegaSST` 8 of 10, `kEpsilon` 6 of 10, `LaunderSharmaKE` REFUSED (relaminarised, not graded), 0 models passed** (`docs/campaigns/F14-cooling-ladder/K0cS_RESULTS.md:18-21` @ `c83d9501`; prereg `6d149d51` before any result); **K0cT tall cavity `Ra` 0.86e6 / 1.43e6 (ERCOFTAC Case 079 primary files on disk): `GATE FAIL` 8 of 18** (`K0cT_RESULTS.md:19` @ `cccf7a9f`); Nusselt re-grade `GATE FAIL` both `Ra` (`K0cT_NUSSELT_REGRADE.md`); **K0cX cross-geometry: `GATE FAIL` 24 of 42, 0 of 3 models** (`K0cX_RESULTS.md:420-424` @ `c557f847`). **This is a documented model defect, not a lab mistake**: K0cG put a third mesh level under K0cS — `kOmegaSST` five quantities CONVERGING (p 1.516–4.078) with deviations **43× to 722× the GCI**, so the error is the closure (`K0cG_RESULTS.md:27-34` @ `878f1556`); K0cP shows no constant `Prt` works (1.115–1.243 needed, above everything measured; @ `bff31cff`), K0cQ rules out anisotropy by 50–250×, K0cR's SSG moves velocity toward and wall flux away from the experiment (`K0c_GRADIENT_DIFFUSION_FORM_LIMIT.md`). What would fix it: a heat-flux closure beyond the gradient-diffusion form (the family's synthesis names the form, not a constant, as the limit); the lab's evidence and attribution are the strongest negative it holds. |
| **natural conv · turbulent · axisym** | **CAN NOT DO** — attempted: **T8 Morton–Taylor–Turner pure plume, axisymmetric 5° wedge, steady `buoyantBoussinesqSimpleFoam`: `NOT A RESULT`** — "T8 ran. It fired three levels, produced three complete measurement trees, and spent 224.667 core-minutes" and fails the gate on two independent grounds (`docs/campaigns/T-family/T8_VERDICT_2026-08-26.md:9-18` @ `0686c7b2`); the steady formulation is under challenge (`T8_STEADINESS_MEASUREMENT_2026-08-26.md`). What would fix it: the record names an unsteady run at one level as the sharpest next test; the successor is unwritten. |
| **natural conv · turbulent · 3D** | CAN NOT DO — not attempted |
| **mixed conv · laminar · 2D** | CAN NOT DO — not attempted |
| **mixed conv · laminar · axisym** | CAN NOT DO — not attempted |
| **mixed conv · laminar · 3D** | CAN NOT DO — not attempted |
| **mixed conv · turbulent · 2D** | **CAN DO, CAVEATS — 1 case with a registered outcome, 1 rung landed ungraded.** K2b rack-row pilot (2D vertical slice, `kOmegaSST`, `buoyantBoussinesqSimpleFoam`, seven solves, 65.4 core-min): **registered outcome `O1 — PHYSICALLY UNSTEADY`, a 6.0 s limit cycle of ≈1.1 K in rack-inlet temperature, non-decaying over 40 s** (`docs/campaigns/F14-cooling-ladder/K2b_PILOT_RESULTS.md:883`, `:1501-1507` @ `5c3fe5a8`); checked: the pre-registered outcome mapping, heat balance by the KV1-validated instrument. Caveats: **no validation reference** (the module is a specification, `K2a_RACK_ROW_MODULE_SPEC.md`); **no grid triple** — the steady instrument is void on a limit cycle; a 2D slice can manufacture or suppress what 3D would damp (the record says so). K0f Blay–Mergui–Niculae ventilated cavity (prereg @ `b70b49c6`, registered before any compute): **all ten arms `STATUS rc=0` on disk, `PENDING` — the comparator refused a partial rung at five and the ten-arm grade is dispatched; its `P` column is BLOCKED on Blay 1992 `NOT OBTAINED`** (`K0f_PREREGISTRATION.md:55`); K0d, the same cavity, stays "FROZEN, ARMED, UNFIRED" (`K0d_PREREGISTRATION.md` @ `1799861d`; `K0d_FIRE_RULING_2026-08-25.md:5`). |
| **mixed conv · turbulent · axisym** | CAN NOT DO — not attempted |
| **mixed conv · turbulent · 3D** | CAN NOT DO — not attempted: K2b-U3 3D unsteadiness check is pre-registered (`docs/campaigns/F14-cooling-ladder/K2b_3D_UNSTEADINESS_PREREGISTRATION.md` @ `5c3fe5a8`) with a 1.4 core-min coarse **cost probe** only (`K2bP`/`K2b3D_probe` inputs tracked); no results record, no graded row; `K2bU3_L050` / `K2bU3_L025` are ruled unregistered exploratory compute that may never enter a grading. |
| **conjugate · laminar · 2D** | CAN NOT DO — not attempted (T9a is solid-only conduction, `laplacianFoam`, no fluid region) |
| **conjugate · laminar · axisym** | CAN NOT DO — not attempted |
| **conjugate · laminar · 3D** | CAN NOT DO — not attempted |
| **conjugate · turbulent · 2D** | CAN NOT DO — not attempted (T5's `X_2d` precursor is a 2D `kOmegaSST` channel with no solid region: `DONE` under the strict rule, ungraded by registration, `T5_PREREGISTRATION.md:394` @ `299296a2`) |
| **conjugate · turbulent · axisym** | CAN NOT DO — not attempted |
| **conjugate · turbulent · 3D** | **CAN NOT DO** — attempted: **T5 heated wall-mounted cube against Meinders 1998, `chtMultiRegionSimpleFoam`, wall-resolved `kOmegaSST`, `Re_H` 2500–5000** — pre-registration FROZEN before any solver ran (`docs/campaigns/T-family/T5_PREREGISTRATION.md` @ `299296a2`, v1.7; freeze `503a9a13`, amendments A1–A6, A8), primary title-page verified on disk; **the first graded case `T5_CUBE_c` crashed at solver start: in-wrapper `STATUS.T5_CUBE_c` rc=1, wall 0 s, zero iterations** (`verification/runs/T-family/T5_runs/STATUS.T5_CUBE_c` @ `0dfd9c64`); the 17:43Z triage ("a LINE, not a plane") was **withdrawn by AMENDMENT 8**: "the S5.3 inflow map wrote to the WRONG REGION PATH (`constant/boundaryData`, reader opens `constant/air/boundaryData`) — NOT collinear as triaged" (`T5_PREREGISTRATION.md:1482` @ `299296a2`); the other five entries were withdrawn unfired. A map-script defect outside the freeze set, not a physics result. What would fix it: A8 is landed (map `dc2b4f74` → `f4e5c350`, region read from `regionProperties`, real map re-run rc 0, six `_v2` entries re-issued citing `299296a2`); the six cases (63.86 core-h registered) have not yet produced a graded row; the reference rows additionally need the A7 digitiser or a thesis table before `P` can score. |
| **radiation · laminar (no flow) · 2D** | CAN NOT DO — not attempted (all radiation work is 3D) |
| **radiation · laminar (no flow) · axisym** | CAN NOT DO — not attempted |
| **radiation · laminar (no flow) · 3D** | **CAN DO — 1 case** (T10a surface-to-surface enclosures, `viewFactorsGen`); **strongest case `docs/campaigns/T-family/T10a_RESULTS.md` @ `31fd2268`**, comparator frozen at `181a5668` before any solve (`:7-8`), pre-registration @ `b2a13fd6`; checked: closed-form view-factor exchange with CONVERGING triples + GCI per row — **black box B0 floor `PASS` 6483.263 vs 6484.921 W/m², dev 0.02557 % on a 0.03326 % band, p 0.954; B2 x-walls `PASS` 0.48631 % on 0.67756 %, p 0.853; B3 y-walls `PASS` 0.32987 % on 0.48472 %, p 0.825** (`:64`, `:66-67`); ε = 1 verified to 0.005 %. Also on the record, so the cell cannot imply a general radiation capability: **B1 ceiling `GATE FAIL` 0.12463 % against a 0.07676 % band (p 1.480)** (`:65`); **grey concentric spheres S0/S1 `NOT A RESULT`, both triples DIVERGENT (p −3.253, −1.838), no band armed** (`:62-63`) — cause CONFIRMED as the `viewFactorsGen` row-sum defect, characterised in T10a-VF (`docs/campaigns/T-family/T10aVF_RESULTS.md` @ `6a9b8c41`; upstream note drafted `NOT FILED`); T10aR ceiling refinement grades nothing against T10a's band and its own falsifier fired (`docs/campaigns/T-family/T10aR_RESULTS.md` @ `8b407ea2`); T10aR2 ×3 reached STATUS rc=0 under a dead fleet and are ungraded (`PENDING`). **Participating media (`fvDOM`, `P1`) never attempted anywhere in the family.** |
| **radiation · turbulent · 2D** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **radiation · turbulent · axisym** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **radiation · turbulent · 3D** | CAN NOT DO — not attempted (no flow regime in this mode; T10b natural convection + radiation is ACQUIRE-blocked, never run) |

**Census (36 cells):** **CAN DO 3** (conduction·no-flow·2D; forced conv·laminar·axisym; radiation·no-flow·3D) · **CAN DO, CAVEATS 2** (natural conv·laminar·2D; mixed conv·turbulent·2D) · **CAN NOT DO, attempted 5** (forced conv·turbulent·2D; forced conv·turbulent·axisym; natural conv·turbulent·2D; natural conv·turbulent·axisym; conjugate·turbulent·3D) · **CAN NOT DO — not attempted 26** (of which 6 are the conduction/radiation "turbulent" cells that have no flow regime). **10 of 36 cells carry evidence.** Every `CAN DO` cell rests on an EXACT / analytic reference; **no cell in this family closes a validation against experiment with a `PASS`** — the three experiment-backed loops that closed (K0cS, K0cT, K0cX) closed `GATE FAIL` with the error attributed to the closure model, and the two pending experiment loops (T5 Meinders, T4b ERCOFTAC case025) have no verdict. Checks never performed anywhere in the family, stated so the grid cannot imply them: ASME V&V 20 `u_val` was used once (K0cT) and nowhere else; no heat-transfer case has a partition/round-off reproducibility row; no 3D natural-convection or 3D forced-convection case has ever run. Sanaa's §5 internal-physicality check (heat-balance closure) exists as an instrument (KV1) and is applied in the K-family records.

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
| cfd | yes | 4 | 5 | 4 | 23 | 0 |
| heat-transfer | yes | 3 | 2 | 5 | 26 | 0 |
| dafoam | yes | 4 | 5 | 1 | 62 | 0 |

(Counts are per verdict cell: dafoam has two verdict columns per class, so its row sums to 72.)

---

## Footer — merged planted control: every distinct sha cited by every source, resolved

Run from the repository root; every line must read `ok`; 95 distinct shas across all sources:

```
for s in 0686c7b2 08aa454c 0cbaea26 0dfd9c64 0f56460d 14018d5b 15767999 1697ea49 16b81323 17209b50 1799861d 193b522c 299296a2 2a93ff27 2aea29d9 2b50394a 2d639d3b 2f1d6cb7 3053d9ec 31fd2268 336a364d 33dbe337 35171866 3574cdcb 3663520c 3b9bcf31 3c21d87c 3d28328c 3f87e759 3f8c6b13 49c95cc7 4ad083fb 4b336fad 4d9d902b 4e6ba646 4eae12f4 52a213ad 548fc02e 5889677b 5adb9c5d 5c3fe5a8 5d1718df 5d1f89cd 60cfd4c8 65684e7c 65882eb3 66f42398 6753e912 6a9b8c41 6b8d6355 6becf266 6d149d51 71388f4e 7422591b 8273e4ad 8590c96a 85e2230f 878f1556 8b407ea2 8f5bf878 9c241fe2 a1ac1c21 a1fbe127 a74b2f61 b10260a0 b26b875c b2a13fd6 b698dfc3 b70b49c6 b840fcd5 b845b603 b8fe7eea ba023a53 bb5088c4 be35dcad bff31cff c4f72b27 c557f847 c69ce11c c83d9501 ca6a3164 cadb4887 cccf7a9f cffd90e7 d4308dde d846815c d98868fb da65ae38 ddb99eca e6d53dbd f018c8bf f279aac5 f5f67de7 f8916f36 f9a59d47; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at assembly time (2026-08-26T20:56Z, HEAD `8146bc05`): **95 ok, 0 MISSING, 95 distinct shas.**
