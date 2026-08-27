# CAPABILITY GRID — Sanaa's taxonomy, assembled from the family tables at HEAD

**Owner:** verification-supervisor. **Directive:** Sanaa's [SANAA-DIRECT] CAPABILITY GRID, boarded verbatim at commit `068c2bf0` (`docs/LAB_STATE.md`, CHIEF ADDENDUM 2026-08-26T17:35Z). **Assembled from HEAD `8506d55c`** on 2026-08-27T16:38Z by `scripts/assemble_capability_grid.py` (idempotent; reads only `git show HEAD:` blobs; zero compute). **REVISION 5** — re-run when a family table lands.

**The verdict vocabulary (Sanaa's, exactly three):** `CAN DO — X cases` (ran successfully, metrics verified; strongest case cited by path + record sha + what was checked); `CAN DO, CAVEATS` (runs, credible results, named missing items each ≤ 1 line); `CAN NOT DO` (does not converge / does not reproduce literature / not enough compute / documented model defect — what was attempted, what would fix it; empty cell = `CAN NOT DO — not attempted`). One verdict per cell. The lab's fixed gate vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING) appears inside a cell as what the record says.

**Disclosed mapping rule (this supervisor's, from the lanes' common brief):** CAN DO requires at least one case whose record at HEAD says PASS (or GATE REACHED with every reached gate passing) under a frozen prereg with a CONVERGING Roache triple where a triple was claimed; anything weaker that still produced a credible graded number is CAN DO, CAVEATS; GATE FAIL / NOT A RESULT / BLOCKED-only cells are CAN NOT DO with the attempt named. Every citation must resolve at HEAD (`git cat-file -e <sha>^{commit}`); the merged footer below is the planted control.

**Order (Sanaa's):** cfd table, heat-transfer table, dafoam table, then the metrics summary.

---

## cfd

**family table at HEAD: `abc00e4a`** (`docs/capability/cfd_GRID.md`; every cell below is copied verbatim from that file — the family supervisor's words, not this script's).

*The family file also carries, below its own table, the **verification supervisor's prior draft, superseded by the family table above** (marker line: `## Verification supervisor's draft — `c5d96403`, retained verbatim below, superseded by the cfd table above`). Only the family's FIRST derivation table, FIRST cell table, FIRST census and FIRST footer are read here; the prior draft is neither counted nor reproduced.*

**Regime / mode per case, as derived by the family (their table):**

| case family | solver / conditions (path:line) | cell |
|---|---|---|
| F17 / F17b Kovasznay | `simpleFoam`, laminar, `steadyState`, Re = 40, 2-D — `verification/campaign/F17_KV40_PREREGISTRATION.md:27-28,53` | **2D · steady · incompressible** |
| F11 lid-driven cavity | `simpleFoam`, laminar, Re 100 / 1000, n = 32/64/128 — `verification/runs/F11_runs/conversion_2026-08-25/RESULTS.md:12` | 2D · steady · incompressible |
| W1 hump (challenge, A1), F6a Greenblatt | `simpleFoam`, Re_c = 936,000, M = 0.1 — `verification/campaign/W1_HUMP_CHALLENGE_PREREGISTRATION.md:15-18` | 2D · steady · incompressible (turbulent) |
| F6b periodic hill, MODEL_FORM band | `simpleFoam`, streamwise-cyclic, Re_H 10,595 — `verification/campaign/F6b_ERCOFTAC_PREREGISTRATION.md:30,42`; `MODEL_FORM_BAND.md:48` (R12 mesh exemption, 85.70°) | 2D · steady · incompressible (turbulent) |
| W2_SPARTA CBFS regression | data-driven closure FORM reproduction on CBFS / PH fields — `verification/campaign/W2_SPARTA_REGRESSION.md:24-29` | 2D · steady · incompressible (instrument, no solve triple) |
| DPW8_V2 Joukowski | `simpleFoam` / `kOmegaSST`, M = 0.15, Re_c = 6e6 — `verification/campaign/DPW8_V2_joukowski.md:8-9` | 2D · steady · incompressible (turbulent) |
| F16 / F16b Stokes II | `icoFoam`, `backward`, oscillating wall — `verification/campaign/F16b_SL2_PREREGISTRATION.md:41,49` | **2D · unsteady · incompressible** (1-D slab) |
| F18 / F18b Taylor–Green | `icoFoam`, doubly-periodic box, ν = 0.1 — `verification/campaign/F18_TG2D_PREREGISTRATION.md:37,42` | **2D · unsteady · incompressible** |
| F5 / F5a / F5b / R7 cylinder | `pimpleFoam`, Re 1000 → 3900 — `verification/campaign/F5a_cylinder_reynolds_ladder.md:3,31-34` | 2D · unsteady · incompressible |
| F9 pulsatile valve | `pimpleFoam`, laminar, 5° wedge, Womersley α ≈ 17 — `verification/campaign/F9_pulsatile_valve.md:58,70,74,78` | **axisym · unsteady · incompressible** |
| F20 isentropic vortex | `rhoCentralFoam`, 2-D inviscid, exact translated Euler field, periodic — `verification/campaign/F20_ISENTROPIC_VORTEX_PREREGISTRATION.md:1,17,40`; frame speed `exact_f20.py:71` | **2D · unsteady · subsonic-compressible** (convention iii) |
| F2 NACA0012, F12 RAE 2822 | `rhoSimpleFoam` + k-ω SST, M 0.8 / M 0.73–0.734 — `verification/campaign/F2_transonic_naca0012.md:28,60`; `F12_PREREGISTRATION.md:9,16-19` | **2D · steady · transonic** |
| F3 wedge + diamond, F3 successor | `rhoCentralFoam`, M 2.0 / 2.5 / 3.0, single-cell slabs — `verification/campaign/F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md:81` ("single-cell-thick 2-D slabs"), `:57`; `F3_CONVERSION_PREREGISTRATION.md:205-206` (slab meshes; the gate rows are `:92-93`) | **2D · steady · supersonic** |
| F3 cone (Taylor–Maccoll) | same suite, single-cell axisymmetric wedge slice — `F3_CONVERSION_PREREGISTRATION.md:206` | **axisym · steady · supersonic** |
| F15 / F15-R2 oblique-shock reflection | `rhoCentralFoam`, inviscid, M = 2.9, pseudo-time to steady — `verification/campaign/F15_OSR29_PREREGISTRATION.md:57-58,95-97` | 2D · steady · supersonic |
| F19 Sod | `rhoCentralFoam`, 1-D Euler, Toro Test 1 — `verification/campaign/F19_SOD_PREREGISTRATION.md:1,16,37` | **2D · unsteady · supersonic** (1-D slab) |
| F4 / F4S blunt cylinder | `rhoCentralFoam`, M ∈ {6, 7, 8}, Billig standoff — `verification/runs/F4_runs/successor_2026-08-26/RESULTS.md:9`; `F4S_SHOCK_LOCUS_PREREGISTRATION.md:146` | **2D · steady · hypersonic** |
| DMR double Mach reflection | `rhoCentralFoam`, inviscid, Mach-10 shock at 60° — `verification/campaign/DMR_PREREGISTRATION.md:6,19-20` | **2D · unsteady · hypersonic** |
| F7 / F7a dam break | `interFoam` VOF laminar, Martin & Moyce — `verification/campaign/F7_marine_free_surface.md:8,19` | **2D · unsteady · multiphase-free-surface** |
| R4 / B52 Ahmed, W3 wings, F8 MRF, D5_rsm duct, F5c, 4G TMR audit | `simpleFoam` RANS 3-D bodies — `R4_ASYMPTOTIC_RESULTS.md:41`; `W3_WING_VALID_FAMILY_RESULTS.md:17,26`; `F8_MRF_HAND2001_GATE.md:6`; `D5_RSM_RESULT.md:7`; `B52_RUNG6_REPLICATE_RESULTS.md:22` | **3D · steady · incompressible** |
| F1 / F13 ONERA M6, committee grids | M 0.84 (`F13_RESULTS.md`); CRM M 0.850 (`cases/committee-grids/COMMITTEE_GRID_NUMERICS.md:64`) | **3D · steady · transonic** |

**The table:**

| cell | verdict |
|---|---|
| **2D · steady · incompressible** | **CAN DO — 1 case at the bar; 6 more graded below it.** Strongest: **F17-KV40 Kovasznay `verification/campaign/F17_KV40_RESULTS.md` @ `f018c8bf`** — G-F17-1 E2 velocity L2 1.423e−04 in band, **`PASS`**, CONVERGING p **2.0990**; G-F17-2 u(0.5, 0) = 0.382441 vs exact 0.382373, **`PASS`**, CONVERGING p **2.0699** (`:20-21`); prereg frozen `4ad083fb`; registered prediction MET (`:31`); 10 planted controls passed (`:55`); ledger `docs/COST_CALIBRATION.md` C-126 @ `db76091e`; genuine 2-D field (Ruling R-1D: CAN DO on its own record). Checked: L2 norm vs exact + observed order vs formal 2 + planted control. Beside it, the extension ladder: **F17b-KV40-EXT 192×128 / 384×256 / 768×512 `verification/campaign/F17b_KV40_EXT_RESULTS.md` @ `f2943b0b`** — G-F17-1 **`NOT A RESULT`**, G-F17-2 **`NOT A RESULT`** by rule 5 limb 1 (the registered Class C plateau fails on medium and fine at the inherited 4,000 fixed iterations; fine values 6.156e−06 and 0.382383 inside both bands and raw triples CONVERGING p 1.858 / 3.471 printed beside, not a result) (`:24-25`); prereg frozen `61b47973`; registered prediction p ≈ 2 NOT MET (`:47`); 11 controls passed; ledger C-142 @ `f8d2d60c`; 26.87 core-min. F17b does not move F17: the strongest record stays F17. Below the bar, quoted as written: F11 cavity **`NOT A RESULT` ×6 with every band `PASS`** — coarse plateau unmeasured (`verification/runs/F11_runs/conversion_2026-08-25/RESULTS.md:3,14` @ `193b522c`); W1 hump challenge Gate V "PASS", separation −1.59 % "PASS", **reattachment +13.92 % "FAIL"** (`W1_HUMP_CHALLENGE_RESULTS.md:21,36` @ `a1fbe127`); F6b periodic hill Gate V "PASS", **Gate P "FAIL" by over-prediction as pre-registered**, Gate Q "PASS" (`F6b_ERCOFTAC_RESULTS.md:12,20,28` @ `a1fbe127`); F6a Greenblatt attempt 3 `NOT A RESULT` (`verification/runs/F6a_GREENBLATT_runs/attempt3_Re936k/result.json` @ `14018d5b`); DPW8_V2 Joukowski L1/L3 "PASS" vs analytic with **no frozen prereg**, L4 `NOT GATED` (`DPW8_V2_joukowski.md:80-81` @ `a1fbe127`; `DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md:20` @ `b8fe7eea`); W2_SPARTA factor-two "PASS" on model form (`W2_SPARTA_REGRESSION.md:24-25` @ `a1fbe127`, instrument, no solve triple). **The turbulent sub-class carries no `PASS` under a frozen prereg.** |
| **2D · steady · subsonic-compressible** | **not attempted** — no `rhoSimpleFoam` / `rhoPimpleFoam` case registered below M ≈ 0.7; the compressible steady line went straight to transonic (F2, F12). |
| **2D · steady · transonic** | **CAN NOT DO — attempted 2 cases.** F12 RAE 2822 (`verification/campaign/F12_RESULTS.md` @ `a1ac1c21`): admission Gate A **`GATE FAIL` — max non-orthogonality 70.646 / 70.861 / 72.542° at all three levels against a frozen ≤ 70°** (`:99,112-114`), Gate B convergence **`GATE FAIL`** (`:158`); rungs 2–5 `BLOCKED` on the rate-calibration interlock (`verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79/RESULTS_RUNG1.md` @ `c69ce11c`). F2 NACA0012 M 0.8 (`F2_transonic_naca0012.md` @ `a1fbe127`): pre-vocabulary, **no frozen pre-registration** — not citable. Solution: a new F12 rung-1 registration on a C-mesh that clears ≤ 70° at every level before the freeze (the 70° gate stays where it is). |
| **2D · steady · supersonic** | **CAN DO, CAVEATS — 1 `PASS` on a CONVERGING triple; every other row `NOT A RESULT`, `PENDING`, `HELD` or single-level; Ruling R-1D applied.** Strongest: **F3 conversion `verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md` @ `5adb9c5d`** — G-F3-5 diamond wave drag / M2.0_eps7p125 **`PASS`**, −0.258 % vs shock-expansion exact, ±1.0 %, CONVERGING **p = 6.296, GCI 0.0001 %** (`:19`); prereg frozen `3574cdcb` (`F3_CONVERSION_PREREGISTRATION.md:92-95`). Checked: wave-drag deviation vs exact theory + Roache triple + GCI. Caveats: **1-D exact-solution on a one-cell-wide mesh; no 2-D field verified** (Ruling R-1D — the F3 suite is registered as single-cell-thick 2-D slabs, `F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md:81`; the wedge/diamond shock-expansion comparison is a 2-D inviscid theory evaluated on a one-cell-deep slab); p = 6.296 against formal 2 is not an asymptotic triple; G-F3-2 / M2.0_th15 `HELD` (`:88-100`) and re-graded `PASS` → `NOT A RESULT`, DEGENERATE |p| = 0.034 (`:102-106`) — never cited; G-F3-1 / M2.0 `NOT A RESULT` OSCILLATORY (`:11`); M3.0 rows `PASS` on a single level only (`:13,16`); successor triples at M2.5 all **`NOT A RESULT` OSCILLATORY** (G-F3S-1/-2/-5, `verification/runs/F3_runs/successor_triple_2026-08-26/RESULTS.md:17-19` @ `8273e4ad`; ledger C-112 @ `db76091e`); F15 M 2.9 **`PENDING` ×2** by the frozen comparator and F15-R2 **REFUSED rc 2** on a reader defect (`verification/runs/F15_runs/RESULTS_R2.md:1,18-20,31-33` @ `3c21d87c`; prereg `2aea29d9`; ledger C-133). F24 Prandtl–Meyer in flight¹. |
| **2D · steady · hypersonic** | **CAN DO — 3 cases (M 6.0 / 7.0 / 8.0), one geometry.** Strongest: **F4S `verification/runs/F4_runs/successor_2026-08-26/RESULTS.md` @ `3663520c`** — G-F4S-1 RH mid-density crossing of bow-shock standoff δ/R: M6.0 **`PASS`** CONVERGING p 1.098, GCI 0.45 %, +1.59 % vs Billig; M7.0 **`PASS`** p 1.058, GCI 0.73 %, +1.07 %; M8.0 **`PASS`** p 2.599, GCI 0.07 %, +0.50 % (`:100,102,104`); prereg frozen `d98868fb` (`F4S_SHOCK_LOCUS_PREREGISTRATION.md:146`); registered prediction "CONVERGING at ≥ 2 of 3" MET 3/3; planted zero read back on all six rows; ledger C-124 @ `db76091e`. Checked: shock standoff vs the Billig (1967) correlation (a correlation scores V, never P — Sanaa §1) + GCI + observed order + planted control. Named, not a caveat on the standoff: predecessor argmax detector G-F4S-1B `NOT A RESULT` ×2, `PASS` ×1 (`:101,103,105`); the F4 conversion closed **`NOT A RESULT` ×11** (`verification/runs/F4_runs/conversion_2026-08-25/RESULTS.md` @ `d4308dde`); Cp-vs-modified-Newtonian limb `PENDING` on a citable reference uncertainty. |
| **2D · steady · multiphase-free-surface** | **not attempted.** |
| **2D · unsteady · incompressible** | **CAN DO — 1 case at the bar (F18), plus 1 caveated (F16b); Ruling R-1D applied.** Strongest: **F18-TG2D Taylor–Green `verification/campaign/F18_TG2D_RESULTS.md` @ `3f87e759`** — a genuine 2-D field (doubly-periodic box, `icoFoam`); G-F18-1 E2 velocity L2 **`PASS`** CONVERGING p **1.2894**; G-F18-2 box-mean KE 0.1123375 vs exact 0.1123322 **`PASS`** CONVERGING p **0.9638** (`:20-21`); `Verdict PASS × 2, as predicted` (`:35`); prereg `c4f72b27`; observed p against registered ≈ 2 — a miss of the prediction, not of the gate (`:38-40`); ledger C-128. The cell holds CAN DO on F18 alone. Checked: L2 norm vs exact + observed order + exact KE + planted control. **CAN DO, CAVEATS evidence: F16b-SL2 Stokes' second problem `verification/runs/F16b_runs/RESULTS.md` @ `49c95cc7`** — G-F16-1 E2 profile **`PASS`** CONVERGING p **1.8252**; G-F16-2 u(δ) = −0.309394 vs exact −0.309560 **`PASS`** CONVERGING p **1.9930** (`:21-22`); prereg frozen `cadb4887`; 9 controls passed (`:53`); ledger C-127 @ `db76091e`; caveat: **1-D exact-solution on a one-cell-wide mesh; no 2-D field verified** (Ruling R-1D). Named: F16 itself **`NOT A RESULT` on physics — identically zero solution from an `empty` ±x declaration** (`verification/runs/F16_runs/RESULTS_R2.md:78-80` @ `5889677b`; ledger C-123); F5b physics probe `NOT A RESULT` on a completion clause (`verification/runs/F5b_runs/physics_p1/RESULTS.md:3` @ `da65ae38`); F5a Re 1000/2000 Cd/St numbers carry no frozen prereg and no rule-1 verdict (`F5a_cylinder_reynolds_ladder.md:31-34` @ `a1fbe127`). **F18b Taylor–Green 256²/512²/1024² extension: in flight, never evidence¹** (prereg `fcf31542`; run root `verification/runs/F18b_runs/`, no record); F21 Womersley, F22 Lamb–Oseen in flight¹. |
| **2D · unsteady · subsonic-compressible** | **CAN DO, CAVEATS — 1 case, `PASS` ×2, converging to a non-zero floor.** **F20 isentropic vortex `verification/runs/F20_ISENTROPIC_VORTEX_runs/RESULTS.md` @ `ca6a3164`** — G-F20-1 L2 density error 3.342e−03 / 1.437e−03 / 1.160e−03, CONVERGING, in band, **`PASS`**, p 2.7786; G-F20-2 box-mean KE 1.0055388 vs exact 1.0056335, CONVERGING p 1.2762, **`PASS`** (`:15-16`); machine record `F20_GRADED.json` @ `ca6a3164`; frozen `grade_f20.py` at prereg `548fc02e`; two planted reads passed, nine registered controls `passed: true` (`:92-94`). Checked: L2 norm vs exact + KE + Roache triple + planted control. Caveats: **the Richardson extrapolate of the E2 triple is 1.1125e−03, not 0, against an exact reference — the triple converges toward a non-zero floor, not toward the exact solution** (`:36-39`); observed order 2.78 lies outside the registered [1.0, 1.6] (`:30-32`); G-F20-2 was registered `NOT A RESULT` and came out CONVERGING (`:44`); frame velocity (1, 1) is M ≈ 1.20 in the box frame (convention iii); ledger C-136 @ `d9fa4161` (68.667 core-min vs 60.0, ratio 1.144; the row was dropped by `db76091e` and restored by `d9fa4161`). |
| **2D · unsteady · transonic** | **not attempted.** |
| **2D · unsteady · supersonic** | **CAN DO, CAVEATS — 1 case, 1 of 2 gates; Ruling R-1D applied.** **F19 Sod `verification/campaign/F19_SOD_RESULTS.md` @ `08aa454c`** — G-F19-1 L1 density error **4.400e−04** in band, CONVERGING **p 1.018**, **`PASS`** (`:21`); G-F19-2 shock position 0.850540 vs exact 0.850431 in band but **`NOT A RESULT` — DEGENERATE, |p| = 0.032 < P_MIN 0.05** (`:22`); prereg frozen `3053d9ec`; ledger C-134 @ `db76091e`. Checked: L1 norm vs the exact Riemann solution + observed order (limited scheme, first order expected). Caveats: **1-D exact-solution on a one-cell-wide mesh; no 2-D field verified** (Ruling R-1D; 1-D Euler slab filed in the 2D row); shock-position triple degenerate (equal increments); one gate of two. |
| **2D · unsteady · hypersonic** | **CAN DO, CAVEATS — 1 case, pre-vocabulary record.** **DMR `verification/campaign/DMR_RESULTS.md` @ `a1fbe127`** — Gate V incident-shock kinematics vs exact theory "PASS" at both rungs: res120 shock speed 2.99328 vs 3 (**0.15 %**), res60 **0.17 %** (`:23,30-31`); rung-to-rung "PASS" (`:78`); Gate P1 double-Mach structure detector **"FAIL as registered, left standing"** (`:37,51`); prereg `DMR_PREREGISTRATION.md` @ `a1fbe127` (`:6,19-20`). Checked: shock kinematics vs exact + structure gate (Sanaa §3 "structure/topology"). Caveats: two resolutions, **no Roache triple**; pre-rule-1 "PASS/FAIL" words; structure gate failed; no Woodward–Colella numeric reference on disk (`DMR_PREREGISTRATION.md:53-65`). |
| **2D · unsteady · multiphase-free-surface** | **CAN NOT DO — attempted 1 case (F7 dam break, `interFoam`).** `verification/campaign/F7_marine_free_surface.md` @ `3b9bcf31`: FEASIBILITY pass, **GATE "FAIL" — front position +8.2 % mean / +11.0 % max against a declared 5 %** (`:19,119`); F7a zero-compute re-gate pins the measurement and **refutes the ambiguity hypothesis — every reading +7.8 % to +11.9 %, all FAIL** (`F7a_REGATE_SPEC.md:176` @ `85e2230f`); Martin & Moyce (1952) primary not held. Solution: the primary tabulated data on disk, a frozen prereg, a mesh triple, and a physics resolution of the +8 % (floor slip/no-slip and VOF compression open). |
| **axisym · steady · incompressible** | **not attempted** as a graded cfd case (F9's `steady_beta_50deg` / `steady_q75` wedge runs under `verification/runs/F9_work/` carry no graded record; Ansys VMFL pipe/sphere wedges are ansys-verification's, `ansys_ROWS.md`). F23 Hagen–Poiseuille wedge in flight¹. |
| **axisym · steady · subsonic-compressible** | **not attempted.** |
| **axisym · steady · transonic** | **not attempted.** |
| **axisym · steady · supersonic** | **CAN DO, CAVEATS — 1 case, 1 of 2 gates.** **F3 cone `verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md` @ `5adb9c5d`** — G-F3-3 cone surface pressure **`PASS`**, +0.287 % vs exact Taylor–Maccoll, ±0.5 %, CONVERGING **p = 2.541, GCI 0.044 %** (`:17`); **G-F3-4 cone shock angle `GATE FAIL`, +2.139 % against ±2.0 %**, CONVERGING p 0.800, GCI 4.969 % (`:18`); prereg frozen `3574cdcb` (axisymmetric wedge slice `F3_CONVERSION_PREREGISTRATION.md:206`). Checked: surface pressure vs exact conical-flow theory + GCI. Caveats: shock-angle gate fails by 0.139 points; the shock-angle detector's own GCI (5 %) exceeds its band; single Mach / half-angle. |
| **axisym · steady · hypersonic** | **not attempted.** |
| **axisym · steady · multiphase-free-surface** | **not attempted** (Ansys VMFL021/022 cavitating orifice wedges are in `ansys_ROWS.md`). |
| **axisym · unsteady · incompressible** | **CAN DO, CAVEATS — 1 case, pre-vocabulary record.** **F9 pulsatile valve `verification/campaign/F9_pulsatile_valve.md` @ `a1fbe127`** — `pimpleFoam` laminar, 5° wedge; Gate 1 quasi-steady limit **"PASS, both runs" within 1.6 %** (`:156`); **Gate 2 Womersley profile "FAIL" as a point comparison** against the closed form (`:183`). Checked: quasi-steady limit + analytic profile point comparison. Caveats: no frozen prereg; Womersley (1955) not held on disk; single mesh, no triple; laminar at pipe Re ≈ 8,400 by design (`:70-79`). F21 Womersley (2D) in flight¹ addresses the profile gate with an exact reference. |
| **axisym · unsteady · subsonic-compressible** | **not attempted.** |
| **axisym · unsteady · transonic** | **not attempted.** |
| **axisym · unsteady · supersonic** | **not attempted.** |
| **axisym · unsteady · hypersonic** | **not attempted.** |
| **axisym · unsteady · multiphase-free-surface** | **not attempted.** |
| **3D · steady · incompressible** | **CAN NOT DO — attempted, many solves; no gate passed under a frozen prereg with a CONVERGING triple.** Ahmed 25° R4 ladder **non-monotone, the "turn" WITHDRAWN as a feature** (chief ruling `8f5bf878`; `R4_ASYMPTOTIC_RESULTS.md:1,97` @ `a1fbe127`); B52 rung-6 replicates "REPRODUCE — the RECIPE owns the floor" (`B52_RUNG6_REPLICATE_RESULTS.md:22` @ `a1fbe127`), rung 8 `conclusive: false`, no observed order (`B52_RUNG8_RESULTS.md:73,100` @ `a1fbe127`); NACA 0012 / 4412 wings ladders non-monotone (`W3_WING_VALID_FAMILY_RESULTS.md:112,148-149` @ `a1fbe127`); UAE Phase VI MRF vs Hand et al. (2001) "NO VERDICT", torque reference never fetched (`F8_MRF_HAND2001_GATE.md:20` @ `a1fbe127`); square-duct RSM vs DNS SSG 55 % / LRR 207 % / EBRSM 52 % of DNS secondary flow (`D5_RSM_RESULT.md:14-29` @ `a1fbe127`); F5c stage A "RECORDED, NOT SCORED" (`F5C_STAGE_A_RESULTS.md:16` @ `a1fbe127`), stage B **`BLOCKED`, "not unblockable by an approval"** (`F5C_STAGE_B_RULING_2026-08-26.md:1,10` @ `f63d347e`). Solution: one 3-D case with a frozen prereg, a converging r = 2 family and a held experimental reference — Ahmed with the R4 recipe carried to a converging family, or the Ansys `EXP` reservoir. |
| **3D · steady · subsonic-compressible** | **not attempted** in cfd (the DAFoam A2 MACH wing at M ≈ 0.29 is `dafoam_GRID.md`'s). |
| **3D · steady · transonic** | **CAN NOT DO — attempted 2 cases, both `GATE FAIL` at mesh admission on the 70° non-orthogonality gate.** F13 ONERA M6 (`verification/campaign/F13_RESULTS.md` @ `16b81323`): R0 **`GATE FAIL` — max non-orthogonality 84.64 / 86.02 / 86.78° against ≤ 70°, worsening with refinement** (`:15,27`); R1–R4 never launched; case **`BLOCKED` on §5 admission** (`:46`). F1 v2 butterfly tip-fill trial: **81.94 / 83.88 / 83.64°** (`verification/runs/F1_MESH_TRIALS_2026-08-25/TRIAL_RESULTS.md:35` @ `d846815c`); F1 has no pre-registration. CRM committee grids (DPW5 / HLPW6): conversion and feasibility probes only, no solve graded (`cases/committee-grids/COMMITTEE_GRID_NUMERICS.md`, `cases/hlpw6/FEASIBILITY_PROBE.md` @ `ddb99eca`). DPW8_V2 is 2-D and sits in the 2D·steady·incompressible cell. Cause: the structured C-O tip-collapse topology cannot clear 70° at any level. Solution: the **unstructured build path** — build and `checkMesh`-admit ONE level ≤ 70° (snappyHexMesh / collapsed-tip unstructured topology) before any ladder is frozen, gate unmoved (cfd-supervisor's ordering on the board; M6 unstructured build in registration¹). |
| **3D · steady · supersonic** | **not attempted.** |
| **3D · steady · hypersonic** | **not attempted.** |
| **3D · steady · multiphase-free-surface** | **not attempted** (F7c DTMB 5415 staging plan only, `F7c_DTMB5415_STAGING_PLAN.md` @ `a1fbe127`; nothing run). |
| **3D · unsteady · incompressible** | **not attempted** (every cylinder rung is a 2-D slab; no 3-D LES/URANS record). |
| **3D · unsteady · subsonic-compressible** | **not attempted.** |
| **3D · unsteady · transonic** | **not attempted.** |
| **3D · unsteady · supersonic** | **not attempted.** |
| **3D · unsteady · hypersonic** | **not attempted.** |
| **3D · unsteady · multiphase-free-surface** | **not attempted.** |

**Census (36 cells): CAN DO 3** (2D·steady·incompressible, 2D·steady·hypersonic, 2D·unsteady·incompressible); **CAN DO, CAVEATS 6** (2D·steady·supersonic, 2D·unsteady·subsonic-compressible, 2D·unsteady·supersonic, 2D·unsteady·hypersonic, axisym·steady·supersonic, axisym·unsteady·incompressible); **CAN NOT DO 4** (2D·steady·transonic, 2D·unsteady·multiphase-free-surface, 3D·steady·incompressible, 3D·steady·transonic); **not attempted 23**. Every `CAN DO` rests on an exact solution or a correlation — **validation against measured experiment (Sanaa §3) is green in no cfd cell**; the family's only experiment-gated rows (W1 hump reattachment, F6b hill reattachment, F7 dam-break front) are FAIL / GATE FAIL. **Not performed anywhere in the family**, stated so the grid cannot imply them: method of manufactured solutions; ASME V&V 20 `u_val` (used once lab-wide, K0cT, heat-transfer); spectra / phase-averaged statistics on any unsteady case; any 3-D CONVERGING triple.

**Census after R-1D: unchanged — CAN DO 3 · CAN DO, CAVEATS 6 · CAN NOT DO (attempted) 4 · not attempted 23.** The 2D·unsteady·incompressible cell holds CAN DO on F18; no cell changed verdict class.

### rulings applied to the cfd table (appended to the family file at `abc00e4a`; amendments of record, reproduced verbatim; a ruling supersedes the cell text above where it says so)

### Ruling R-1D (chief, 2026-08-26, [lab-attributed]) — applied by the verification supervisor

**Appended 2026-08-26 by a verification-supervisor lane (lane `metrics`), append-only, on the HEAD blob `825b1259` of this file. Lines whose number changed above this section: 0.** The ruling sits on Sanaa's desk to overrule; until then it binds the mapping. Quoted verbatim as relayed by the verification supervisor:

> Sanaa's taxonomy has no 1-D class. A case solved on a one-cell-wide mesh verifies a 1-D PDE, not a 2-D field, so it cannot carry CAN DO in a 2D cell in ANY family. Binding treatment for both cfd and heat-transfer: such cases enter the 2D row as CAN DO, CAVEATS with the caveat '1-D exact-solution on a one-cell-wide mesh; no 2-D field verified', cited with their full verdicts. A genuine 2-D case (F17 Kovasznay, F18 Taylor-Green, T5, T13 if 2-D) stays CAN DO on its own record.

**Consequence per affected cell of the family table above (cells are not rewritten; this section is the amendment of record):**

- **2D · unsteady · incompressible — the cell HOLDS `CAN DO`, on F18 alone.** F18-TG2D Taylor–Green (`verification/campaign/F18_TG2D_RESULTS.md` @ `3f87e759`) is a genuine 2-D case — its headline reads *"F18-TG2D — 2-D decaying Taylor–Green vortex (`icoFoam`, periodic box) — GRADED RECORD"*, `Verdict PASS × 2, as predicted` (`:35`), G-F18-1 `E2_velocity_L2_at_T` **PASS** CONVERGING p 1.2894 and G-F18-2 `mean_kinetic_energy_at_T` **PASS** CONVERGING p 0.9638 (`:20-21`) — and carries the cell by itself. F16b-SL2 Stokes' second problem (`verification/runs/F16b_runs/RESULTS.md` @ `49c95cc7`, G-F16-1 PASS p 1.8252, G-F16-2 PASS p 1.9930) is a one-cell-wide slab (derivation row above: "(1-D slab)") and is **re-filed as CAN DO, CAVEATS evidence** with the caveat *1-D exact-solution on a one-cell-wide mesh; no 2-D field verified*. The cell's count becomes **CAN DO — 1 case at the bar (F18), plus 1 caveated (F16b)**.
- **2D · unsteady · supersonic — stays `CAN DO, CAVEATS`.** F19 Sod (`verification/campaign/F19_SOD_RESULTS.md` @ `08aa454c`, G-F19-1 PASS CONVERGING p 1.018; G-F19-2 NOT A RESULT DEGENERATE |p| = 0.032) is a 1-D Euler slab (derivation row: "(1-D slab)"); the existing caveat "1-D slab filed in the 2D row" is restated in the ruling's wording: *1-D exact-solution on a one-cell-wide mesh; no 2-D field verified*.
- **2D · steady · supersonic — stays `CAN DO, CAVEATS`, one caveat added.** The F3 suite is registered as "single-cell slabs" (derivation row above; `F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md:81` "single-cell-thick 2-D slabs", `F3_CONVERSION_PREREGISTRATION.md:205-206`; the `:92-93` cite that stood here points at gate rows G-F3-1/-2 and was corrected in place on the chief's revision-4 audit), so the ruling applies: the strongest row G-F3-5 diamond wave drag **PASS** CONVERGING p 6.296 (`verification/runs/F3_runs/conversion_2026-08-24/RESULTS.md:19` @ `5adb9c5d`) carries the added caveat *1-D exact-solution on a one-cell-wide mesh; no 2-D field verified* (the wedge/diamond shock-expansion comparison is a 2-D inviscid theory evaluated on a one-cell-deep slab; no 2-D field was verified). Verdict unchanged.
- **Untouched by this ruling:** every other cell. F17 Kovasznay (genuine 2-D) is named by the ruling as CAN DO-eligible on its own record where it is cited above.

**Census after R-1D: unchanged — CAN DO 3 · CAN DO, CAVEATS 6 · CAN NOT DO (attempted) 4 · not attempted 23.** The 2D·unsteady·incompressible cell holds CAN DO on F18; no cell changed verdict class.
Applied into the table in place 2026-08-26T22:17:45Z by a cfd lane on the cfd-supervisor's order; line count unchanged (240 lines before and after, above this appended line — every edit was a one-line in-place rewrite: cells at lines 48, 51, 54, 57; derivation row line 30 and this section's F3 parenthetical, both corrected from the `:92-93` gate-row cite to `F3_SUCCESSOR_TRIPLE_PREREGISTRATION.md:81`; in-flight lines 12 and 89 (F17b graded); footer lines 119, 122, 125); footer sha control re-run: 43/43 resolve.

---

## heat-transfer

**family table at HEAD: `f0b3971a`** (`docs/capability/heat-transfer_GRID.md`; every cell below is copied verbatim from that file — the family supervisor's words, not this script's).

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
| **conduction · laminar (no flow) · 2D** | ~~**CAN DO — 2 cases**~~ **CAN DO, CAVEATS — 2 cases** *(corrected 2026-08-26, Correction 1 below: the strongest case's own headline is "Rung verdict: GATE FAIL — 1 of 3 graded rows failed", `T9a_RESULTS.md:13`; T11 has no rung-level record at HEAD)* — caveats: R1 interface `GATE FAIL` (−2.41 mK vs 0.92 mK band); R3/R4 `GATE REACHED` below the O(Bi) floor; T11 gate file uncommitted. Evidence (T9a composite wall + fin; T11 transient plane wall); **strongest case `docs/campaigns/T-family/T9a_RESULTS.md` @ `0cbaea26`**, comparator frozen at `239ed2b8` before any case existed (`:7`), pre-registration `docs/campaigns/T-family/T9a_PREREGISTRATION.md` @ `6753e912`; checked: exact-theory error with a CONVERGING triple + GCI per row — **R0 wall `q″` `PASS` 19.854991 vs 19.502682, dev 1.806 % on a 2.043 % GCI band, p 1.079; R2 interface-2 `T` `PASS` −0.51 mK on a 0.75 mK band, p 0.952** (`:38`, `:40`); planted-zero control in the comparator. Also on the record and stated so the cell cannot imply otherwise: **R1 hot-side interface `GATE FAIL` −2.41 mK against a 0.92 mK band (p 1.738), cause CONFIRMED as the interface scheme** (`:39`; T9aD @ `a74b2f61`, T9aH @ `b698dfc3` diagnose it and grade no T9a row); R3/R4 fin rows `GATE REACHED` — bands 0.00077 % / 0.00011 % below the 0.025 % O(Bi) floor, reported not graded (`:41-42`). T11: `PASS` ×3 EXACT tier, p 2.000 / 2.000 / 2.005, GCI 2.9e-07 / 1.4e-06 / 3.4e-06 on a ±1e-4 band, Robin BC, `P_MIN` ruled 0.5 — **but its `gate_t11.json`, `STATUS.T11_PW_{c,m,f}` and DONE markers are ON DISK and NOT AT HEAD** (`git ls-tree HEAD verification/runs/T-family/T11_runs/` holds only the instruments and the C-T control); the tracked witnesses are the calibration row `docs/COST_CALIBRATION.md` C-118 @ `6becf266` and the pre-registration @ `f5f67de7` (frozen `ca9aad86`, amendments `352aef0d`, `f5f67de7`). T11 is therefore counted as a case but is not the citation. |
| **conduction · laminar (no flow) · axisym** | CAN NOT DO — not attempted |
| **conduction · laminar (no flow) · 3D** | CAN NOT DO — not attempted |
| **conduction · turbulent · 2D** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **conduction · turbulent · axisym** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **conduction · turbulent · 3D** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **forced conv · laminar · 2D** | CAN NOT DO — not attempted as a graded heat-transfer class. Named so nobody counts them: K0e flat plate is a **specification only, zero compute** (`docs/campaigns/F14-cooling-ladder/K0e_FORCED_CONVECTION_FLAT_PLATE_GATE.md` @ `4b336fad`); E4a2 fan-pressure BC `PASS` 8 of 8 (`Q` dev 0.144 %, p 1.959, GCI 0.393 %; `docs/campaigns/T-family/E4a2_RESULTS.md` @ `2d639d3b`) backs a **flow** boundary condition, not a heat-transfer quantity; KV1 validated the heat-balance instrument on a laminar duct (`docs/campaigns/F14-cooling-ladder/KV1_RESULTS.md` @ `65684e7c`, `:524` "KV1 is a laminar rung") and grades no case. |
| **forced conv · laminar · axisym** | ~~**CAN DO — 1 case**~~ **CAN DO, CAVEATS — 1 case** *(corrected 2026-08-26, Correction 1: the record's headline is "Rung verdict: GATE FAIL — 1 of 4 graded rows failed", `T1c_RESULTS.md:6`)* — caveats: L0 constant-`Ts` `Nu` `GATE FAIL` (0.0865 % vs 0.0301 % band); L4 `NOT A RESULT`; L1/L3 carry no observed order. Evidence (T1c laminar pipe, wedge); **strongest case `docs/campaigns/T-family/T1c_RESULTS.md` @ `2f1d6cb7`**, pre-registration `docs/campaigns/T-family/T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md` @ `e6d53dbd` (written "before any case was built or solved", `:3`); checked: exact-theory error norm with GCI band — **L2 constant-`q″` `Nu` `PASS` 4.365298 vs 48/11 = 4.3636364, dev 0.0381 % on a 0.0459 % band, CONVERGING p 2.031; L1/L3 `f·Re` `PASS` 63.98771 vs 64, dev 0.0192 % on 0.0236 %** (`:15-17`); references re-derived by the comparator, which refuses if they do not reproduce (`:26-28`). Also on the record: **L0 constant-`Ts` `Nu` `GATE FAIL` 3.659958 vs 3.6567934, dev 0.0865 % against a 0.0301 % band, p 1.854** (`:14`; "The GATE FAIL is real and is not excused", `:123`) and **L4 `NOT A RESULT`** (station as originally registered, no band armed, `:18`); the rung verdict line reads "GATE FAIL — 1 of 4 graded rows failed" (`:6`); L1/L3 carry a band but print no observed order. |
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
| **radiation · laminar (no flow) · 3D** | ~~**CAN DO — 1 case**~~ **CAN DO, CAVEATS — 1 case** *(corrected 2026-08-26, Correction 1: the record's headline is "Rung verdict: GATE FAIL — the box enclosure grades 3 of 4 rows PASS and one …", `T10a_RESULTS.md:32`; T10aVF is a defect characterisation, not a rung `PASS`)* — caveats: B1 ceiling `GATE FAIL` (0.12463 % vs 0.07676 % band); spheres S0/S1 `NOT A RESULT` on a confirmed `viewFactorsGen` defect; black (ε = 1) enclosure only. Evidence (T10a surface-to-surface enclosures, `viewFactorsGen`); **strongest case `docs/campaigns/T-family/T10a_RESULTS.md` @ `31fd2268`**, comparator frozen at `181a5668` before any solve (`:7-8`), pre-registration @ `b2a13fd6`; checked: closed-form view-factor exchange with CONVERGING triples + GCI per row — **black box B0 floor `PASS` 6483.263 vs 6484.921 W/m², dev 0.02557 % on a 0.03326 % band, p 0.954; B2 x-walls `PASS` 0.48631 % on 0.67756 %, p 0.853; B3 y-walls `PASS` 0.32987 % on 0.48472 %, p 0.825** (`:64`, `:66-67`); ε = 1 verified to 0.005 %. Also on the record, so the cell cannot imply a general radiation capability: **B1 ceiling `GATE FAIL` 0.12463 % against a 0.07676 % band (p 1.480)** (`:65`); **grey concentric spheres S0/S1 `NOT A RESULT`, both triples DIVERGENT (p −3.253, −1.838), no band armed** (`:62-63`) — cause CONFIRMED as the `viewFactorsGen` row-sum defect, characterised in T10a-VF (`docs/campaigns/T-family/T10aVF_RESULTS.md` @ `6a9b8c41`; upstream note drafted `NOT FILED`); T10aR ceiling refinement grades nothing against T10a's band and its own falsifier fired (`docs/campaigns/T-family/T10aR_RESULTS.md` @ `8b407ea2`); T10aR2 ×3 reached STATUS rc=0 under a dead fleet and are ungraded (`PENDING`). **Participating media (`fvDOM`, `P1`) never attempted anywhere in the family.** |
| **radiation · turbulent · 2D** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **radiation · turbulent · axisym** | CAN NOT DO — not attempted (no flow regime in this mode) |
| **radiation · turbulent · 3D** | CAN NOT DO — not attempted (no flow regime in this mode; T10b natural convection + radiation is ACQUIRE-blocked, never run) |

**Census (36 cells), as corrected 2026-08-26 (Correction 1):** ~~CAN DO 3 · CAN DO, CAVEATS 2~~ **CAN DO 0** · **CAN DO, CAVEATS 5** (conduction·no-flow·2D; forced conv·laminar·axisym; radiation·no-flow·3D; natural conv·laminar·2D; mixed conv·turbulent·2D) · **CAN NOT DO, attempted 5** (forced conv·turbulent·2D; forced conv·turbulent·axisym; natural conv·turbulent·2D; natural conv·turbulent·axisym; conjugate·turbulent·3D) · **CAN NOT DO — not attempted 26** (of which 6 are the conduction/radiation "turbulent" cells that have no flow regime). **10 of 36 cells carry evidence.** Every `CAN DO, CAVEATS` cell with a `PASS` row rests on an EXACT / analytic reference; **no cell in this family reaches `CAN DO`, because no strongest case carries a rung-level `PASS` at HEAD** (the T11 `PASS` ×3 gate file is uncommitted); **no cell in this family closes a validation against experiment with a `PASS`** — the three experiment-backed loops that closed (K0cS, K0cT, K0cX) closed `GATE FAIL` with the error attributed to the closure model, and the two pending experiment loops (T5 Meinders, T4b ERCOFTAC case025) have no verdict. Checks never performed anywhere in the family, stated so the grid cannot imply them: ASME V&V 20 `u_val` was used once (K0cT) and nowhere else; no heat-transfer case has a partition/round-off reproducibility row; no 3D natural-convection or 3D forced-convection case has ever run. Sanaa's §5 internal-physicality check (heat-balance closure) exists as an instrument (KV1) and is applied in the K-family records.

**Census after R-1D: unchanged — CAN DO 0 · CAN DO, CAVEATS 5 · CAN NOT DO (attempted) 5 · not attempted 26.**

### heat-transfer family's corrections (appended below its footer at `f0b3971a`; supersede the table above where they strike it; reproduced verbatim)

### Heat-transfer supervisor corrections 2026-08-26T21:20:27Z [lab-attributed]

**Applied by a heat-transfer lane on the supervisor's dispatch; every line above this section is untouched (the file was absent from the working tree at write time and was re-materialised from the HEAD blob `7e2fc497` before appending). Quote-and-strike only; no cell is rewritten. Verdict tally BEFORE this section: CAN DO 0 · CAN DO, CAVEATS 5 · CAN NOT DO, attempted 5 · not attempted 26. AFTER: unchanged — 0 / 5 / 5 / 26. Cells moved: 0. Caveat text corrected in 2 cells; 4 items of the dated "CAN DO 0" section superseded by records now at HEAD.**

#### HT-1 — conduction · laminar (no flow) · 2D: the T11 caveat is stale, and T11 is 1-D evidence, not 2-D

The cell reads *"~~T11 gate file uncommitted~~"* and item 2 of the dated section reads *"~~T11 would carry CAN DO for conduction·2D on its own … the moment heat-transfer commits T11_RESULTS.md and gate_t11.json … the gate file lives on disk only~~"*. **Superseded:** `docs/campaigns/T-family/T11_RESULTS.md` and `verification/runs/T-family/T11_runs/gate_t11.json` are at HEAD since `7b2a12f0` — "`PASS` ×3 (G1, G2, G3), every triple CONVERGING, planted-zero control PASS" (`T11_RESULTS.md:3`), p 2.000 / 2.000 / 2.005, GCI ≤ 3.41e-06 on a ±1e-04 band (`:24-26`), pre-registration frozen at `ca9aad86` before compute.

**But the cell does not move to CAN DO on it.** T11 is a one-dimensional plane wall solved on a one-cell-wide OpenFOAM mesh (`T11_RESULTS.md:37`: "1-D plane wall solved on a 2-D OpenFOAM mesh"; `T11_PREREGISTRATION.md:61`). The taxonomy has no 1-D column; the honest statement is that T11 is **supporting evidence of 1-D transient conduction**, not evidence for the 2-D cell, and the 2-D evidence in this cell remains T9a (fin, 2-D) whose rung headline is GATE FAIL. The cell stays **CAN DO, CAVEATS**; its caveat list is corrected to: R1 interface `GATE FAIL` (−2.41 mK vs 0.92 mK band, cause named — see HT-4); R3/R4 `GATE REACHED` below the O(Bi) floor; T11 `PASS` ×3 is 1-D. **What would lift it:** a graded 2-D conduction rung — **T14** (2-D transient conduction in a square, product of T11's series, EXACT tier) is **PENDING**, frozen at `5a870e54` (`docs/campaigns/T-family/T14_PREREGISTRATION.md`), four entries in `verification/queue/heat-transfer/`.

#### HT-2 — radiation · laminar (no flow) · 3D: T10aR2 is graded at HEAD and does NOT close B1

Item 4 of the dated section reads *"~~T10aR2 ×3 sit at STATUS rc=0 ungraded — a graded T10aR2 that closes B1 is the move~~"*. **Superseded:** `docs/campaigns/T-family/T10aR2_RESULTS.md` is at HEAD since `122f6da3` — "2 PASS, 5 GATE FAIL, 2 NOT A RESULT against this arm's own registered rows … the B1 2LI c/m/f triple is OSCILLATORY" (`:3`), B1 ceiling −3268.222601 → −3268.384010 → −3268.097795 W/m², no band armed (`:40`); "the registered expectation 'the 2LI ladder is CONVERGING at p ≈ 1.48' is refuted by measurement". The cell stays **CAN DO, CAVEATS**; the caveat "B1 ceiling GATE FAIL" now carries: *its H-3(a) refinement arm T10aR2 returned OSCILLATORY on B1 (NOT A RESULT) and does not close it*. No further T10a-B1 registration is made by this family (a "T10a-B1b" would duplicate T10aR2).

#### HT-3 — forced conv · laminar · axisym: "a wider registered band" is struck

Item 4 reads for T1c *"~~needs a level pair that closes it, or a wider registered band grounded before compute~~"*. **Struck:** the supervisor's standing rule for successor rungs is *no band widening*. The record names **no cause** — `verification/runs/T-family/T1_runs/DIAGNOSTIC_PREDICTION.md:140`: "The T1c constant-`Ts` GATE FAIL therefore still has NO identified cause" — and specifies the next diagnostic as a Péclet-scaling sweep (Re 25/50/100/200/400 at the fine mesh, registered prediction: log–log slope −2 if axial conduction; `:166-190`). That arm is **not yet registered**; the cell stays **CAN DO, CAVEATS** and its fix line is: *register the Pe-sweep diagnostic arm (T1c-L0b); no band moves.*

#### HT-4 — conduction · 2D, T9a R1: the corrected re-run is registered

Item 4 reads for T9a *"a corrected re-run is a new rung, not a repair of this one"*. **Done:** **T9a-R1b** is frozen at `3c39d08d` (`docs/campaigns/T-family/T9aR1b_PREREGISTRATION.md`): the parent's three wall levels byte-for-byte from `0cbaea26`, one line moved (`Gauss linear corrected` → `Gauss harmonic corrected`), T9a's row rule unchanged with the EXACT case made operational as a 1e-06 K floor (900× tighter than the parent's 0.92 mK band), three entries in `verification/queue/heat-transfer/` — **PENDING**. The cell does not move until it is graded.

#### HT-5 — natural conv · laminar · 2D: a PENDING EXACT-tier registration is on the queue

**T13** (Batchelor vertical-slot conduction regime, `Ra_L` 100, `buoyantBoussinesqSimpleFoam`, laminar, 2-D, analytic reference, V-column only) is frozen at `0d2dc150` (`docs/campaigns/T-family/T13_PREREGISTRATION.md`), three entries enqueued, **PENDING**. The cell stays **CAN DO, CAVEATS** on K0c until T13 is graded; a T13 PASS with CONVERGING triples would be the first EXACT-tier evidence in this cell.

#### HT-6 — sha audit of this file

Every 8-hex commit sha cited above this section resolves under `git cat-file -e <sha>^{commit}` at HEAD (38 listed in the footer: 38 ok, 0 MISSING, re-run at write time). Two 8-hex tokens in the conjugate·turbulent·3D cell — `dc2b4f74` and `f4e5c350` — are **not commit shas** (they are the T5 A8 region-map identifiers quoted from the record) and are excluded from the count. This section adds six commit shas, each resolved at write time: `7b2a12f0`, `122f6da3`, `ca9aad86`, `5a870e54`, `3c39d08d`, `0d2dc150` (and re-cites `0cbaea26`, `7e2fc497`). **Distinct 8-hex commit shas cited in this file after this section (excluding the two region-map tokens): 53; 53 resolve, 0 unresolved (re-derived by grep + `git cat-file -e` at write time; the figure 46 first written here was a hand count and is corrected in the same day).**

**Lines whose number changed above this section: 0.**

### Supervisor note 2026-08-26T21:22:09Z — chief's cross-family ruling on 1-D cases in the 2D row `[lab-attributed, on Sanaa's desk]`

Chief, ~21:25Z 2026-08-26: *1-D cases on a one-cell-wide mesh enter the 2D row as **CAN DO, CAVEATS** ("1-D exact-solution; no 2-D field verified") in every family.* The **conduction · laminar · 2D** cell above already reads CAN DO, CAVEATS on T11 (`7b2a12f0`, PASS ×3, p 2.000 / 2.000 / 2.005, GCI ≤ 3.4e-06, planted control seen at 1e-07); this note fixes its caveat wording to the ruling's: **"1-D exact-solution; no 2-D field verified."** The cell moves to CAN DO only when T14 (`5a870e54`, 2-D square, queued at 7.24 core-min POINT) grades PASS ×3. No other cell moves. Heat-transfer supervisor, Fable.

---

### Heat-transfer lane note 2026-08-26 `[lab-attributed]` — appended at the foot, **lines whose number changed above this section: 0** (verified by byte-comparing everything above against `git show HEAD:docs/capability/heat-transfer_GRID.md`)

#### HT-7 — forced conv · laminar · axisym: **the Pe-sweep already ran, on BOTH thermal boundary conditions, and HT-3's fix line is struck**

**HT-3 above says of this cell:** *"That arm is **not yet registered**; the cell stays CAN DO, CAVEATS and its fix line is: ~~register the Pe-sweep diagnostic arm (T1c-L0b); no band moves.~~"*

**STRUCK. The premise is false at HEAD.** The Péclet-scaling arm was registered in advance and **has already been executed and analysed — twice, once on each thermal boundary condition** — and a lane dispatched to register it as `T1c-L0b` correctly refused under `CLAUDE.md` rule 2, because a pre-registration written on top of results already on disk is one in name only. Both artefact sets are in HEAD and were read before this note was written.

| arm | artefact | cases | fitted log–log slope of the `Nu` excess against `Pe` | registered `Re` = 25 point | measured |
|---|---|---|---|---:|---:|
| constant `q″` | `verification/runs/T-family/T1_runs/pesweep.json`, `analyse_pesweep.py` | `D_Re25`, `D_Re50`, `L_q_f`, `D_Re200`; `D_Re400` **discarded by that file's own registered development check** | **+0.00170 ± 0.00106**, `R²` 0.563 — **1 894 standard errors from −2** | +1.197 % | **+0.03808 %** |
| constant `Ts` | `verification/runs/T-family/T1_runs/dts.json`, `analyse_dts.py` | **twelve completed cases**: three-level `c/m/f` ladders at `Re` 25, 50, 200 plus the existing `L_Ts` `Re` = 100 ladder | **−0.9782 ± 0.1863** at `f` (`R²` 0.932, **5.485 σ** from −2); **−0.8359 ± 0.1763** at `h → 0` (`R²` 0.918, **6.603 σ**) | +1.78 % | **+0.5068 %** at `h → 0` (frozen sign; **+0.5034 %** under the 2026-08-24 Richardson-sign addendum) |

**What the two slopes refute, against the falsifiers registered before either arm was built** (`DIAGNOSTIC_PREDICTION.md:194-200`, `:249`, `:417`):

- **`1/Pe²` axial conduction is refuted on both arms.** The `q″` slope is **indistinguishable from zero**, which is that file's registered *"Slope ≈ 0 — the excess does not depend on Péclet at all, so axial conduction is refuted and the cause remains unidentified"*. The constant-`Ts` slope is **≈ −1 and significantly different from −2**, which is its registered *"Slope significantly different from −2 — some other Péclet-dependent mechanism, and `1/Pe²` is the wrong form; the fitted slope is then the finding"*.
- **The two arms disagree with each other**, and that is itself the information: the excess is **Péclet-dependent under a fixed wall temperature and Péclet-independent under a fixed wall flux**. A mechanism that acts only when the wall temperature is imposed is a **boundary-condition** effect, not a bulk one — which is why the successor below moves the 300 K / 310 K corner rather than the Péclet number.
- **Nothing here moves a verdict.** The arm is diagnostic and ungraded by its own registration, the `L0` constant-`Ts` `GATE FAIL` (0.0865 % against a 0.0301 % band) stands exactly as `T1c_RESULTS.md:14` records it, and **no band is widened, narrowed or reinterpreted.**

**The cell's fix line, replacing HT-3's:** ~~register the Pe-sweep diagnostic arm (T1c-L0b); no band moves~~ → **run the UNHEATED-UPSTREAM arm** — `D_Ts_Re25_U_{c,m,f}` and `L_Ts_U_{c,m,f}`, the parabolic inlet moved to `x = −10 D` with the wall adiabatic for `−10 D < x < 0` and 310 K for `x > 0`, so the 300 K / 310 K corner does not exist. Registered in advance at `DIAGNOSTIC_PREDICTION.md:786`, **frozen `6a0d7f45d5bc19a3fa06fffac4a20c2a3ecbf82c`** (2026-08-21); **built, instrumented and queued 2026-08-26** under the pre-first-compute build/run amendment at **`994daa49905f7826d8dc5bb47f28e574c8588f70`**, six entries dropped at **`3fafc67ac7132fbe27951e81164ad565ae71ad31`** (`verification/queue/heat-transfer/`, 234.122 core-min POINT, cap 735, validator `ACCEPTED` rc 0 on all six). **No band moves.**

**The cell's verdict is UNCHANGED — `CAN DO, CAVEATS`, on T1c — and the 36-cell census is UNCHANGED.** This note strikes a stale fix line and records what two completed diagnostic arms measured; it enters no new evidence in any cell, and no rung is a capability until it has reported.

### rulings applied to the heat-transfer table (appended to the family file at `f0b3971a`; amendments of record, reproduced verbatim; a ruling supersedes the cell text above where it says so)

### Ruling R-1D (chief, 2026-08-26, [lab-attributed]) — applied by the verification supervisor

**Appended 2026-08-26 by a verification-supervisor lane (lane `metrics`), append-only, on the HEAD blob `825b1259` of this file. Lines whose number changed above this section: 0.** The ruling sits on Sanaa's desk to overrule; until then it binds the mapping. Quoted verbatim as relayed by the verification supervisor:

> Sanaa's taxonomy has no 1-D class. A case solved on a one-cell-wide mesh verifies a 1-D PDE, not a 2-D field, so it cannot carry CAN DO in a 2D cell in ANY family. Binding treatment for both cfd and heat-transfer: such cases enter the 2D row as CAN DO, CAVEATS with the caveat '1-D exact-solution on a one-cell-wide mesh; no 2-D field verified', cited with their full verdicts. A genuine 2-D case (F17 Kovasznay, F18 Taylor-Green, T5, T13 if 2-D) stays CAN DO on its own record.

**Consequence per affected cell of the family table above (cells are not rewritten; this section is the amendment of record):**

- **conduction · laminar (no flow) · 2D — stays `CAN DO, CAVEATS`, on T9a; T11 enters as caveated evidence.** T11 (`docs/campaigns/T-family/T11_RESULTS.md` @ `7b2a12f0`) reads *"Rung verdict, as printed by the frozen comparator: `PASS` ×3 (G1, G2, G3), every triple CONVERGING, planted-zero control PASS"* (`:3`), G1/G2/G3 CONVERGING p 2.000 / 2.000 / 2.005, GCI ≤ 3.41e-06 (`:24-26`), and describes itself as a *"1-D plane wall solved on a 2-D OpenFOAM mesh"* (`:37`). Under R-1D it **enters the cell as CAN DO, CAVEATS evidence** with the caveat *1-D exact-solution on a one-cell-wide mesh; no 2-D field verified*; it cannot lift the cell to CAN DO, which is what section HT-1 above already concluded by a different route (no 1-D column). The cell's verdict is unchanged: CAN DO, CAVEATS on T9a (Correction 1).
- **natural conv · laminar · 2D — no change now.** T13 (frozen `0d2dc150`, PENDING, HT-5 above) is registered as a 2-D vertical slot; if its record lands PASS on a genuine 2-D mesh it may carry CAN DO on its own record per the ruling's last sentence. Nothing is entered until a graded record is at HEAD.
- **Untouched by this ruling:** every other cell.

**Census after R-1D: unchanged — CAN DO 0 · CAN DO, CAVEATS 5 · CAN NOT DO (attempted) 5 · not attempted 26.**

---

---

## dafoam

**family table at HEAD: `bd8ffcd8`** (`docs/capability/dafoam_GRID.md`; every cell below is copied verbatim from that file — the family supervisor's words, not this script's).

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
| **2D · steady · incompressible** | **CAN DO — 6 cases** (D1, D1-C′, D2, D13, A1 re-verification, A_stepsize); **strongest case `cases/dafoam/ladder-a/A1/curriculum_D13/RESULTS.md` @ `15767999`**; checked: FD-vs-adjoint relative error per DV at ~~three~~ **five** independently converged endpoints, **4/4 components each, worst ~~0.2568 / 0.2540 / 0.2557 %~~ 0.2568 / 0.2540 / 0.2557 / 0.2591 / 0.2582 % — family-worst 0.2591 % (s4; `RESULTS.md:29`, `:234` "worst relative error 0.2591 %")** *(corrected 2026-08-26, Correction 1 below)*, zero sign flips, on the patched IDWarp image; the SHIPPED row is **design-point dependent** — `GATE FAIL` **11.4274 %, one sign flip** at the baseline (`ladder-a/A1/reverify_patched_idwarp_np1/RESULTS.md` @ `be35dcad`) and **PASS** at the converged optimum (`ladder-a/A1/curriculum_D1_Cprime/RESULTS.md` @ `cffd90e7`); step-plateau sweep (`ladder-a/A_stepsize_study.md`); np-invariance measured on B3 CBFS: serial vs scotch vs simple decomposition, **G4 `GATE FAIL` as written** — ~~gradients differ by decomposition~~ **G4 is the OBJECTIVE bit-identity gate: objectives spread 1.9e-07, not bit-identical (`:25`); the gradients agree with the serial reference to 1.1–1.7e-4 (`:18`)** *(corrected 2026-08-26, Correction 1 below)* (`ladder-b/B3/decomposition_np4/RESULTS.md` @ `bb5088c4`); B3 shipped adjoint `BLOCKED` (PETSc `-9`), passes only on the sub-LU patch (`ladder-b/B3/adjoint_unblock_reproduce/RESULTS.md` @ `3f8c6b13`); dot-product/duality and complex-step **not checked** anywhere in this family. | **CAN DO — 4 cases** (D13 ~~three~~ **five** restarts *(corrected 2026-08-26, Correction 1 below)*, D2 two optimisers, D1); **strongest case `ladder-a/A1/curriculum_D13/RESULTS.md` @ `15767999`**: ~~three~~ **five** starts each reach `EXIT: Optimal Solution Found.` in 9–11 majors at `CD = 0.017527…` (spread ~~≤ 2e-7~~ **2.036213e-07**, `:123`), each endpoint FD-verified 4/4 ≤ 0.26 % (worst 0.2591 %) *(corrected 2026-08-26, Correction 1 below)* — the item's cross-start BASIN verdict is `GATE FAIL`, 15 of 15 pairs `DIFFERENT` on the design vector while 0 of 15 differ on drag (`:34-36`): a flat valley floor, not a point; reported here because it is the record's own headline, and it is not a caveat on optimiser convergence; D2 IPOPT **and** SLSQP both terminate `Inform = 0` with endpoint FD PASS 0.2553 / 0.2485 % (`ladder-a/A1/curriculum_D2/RESULTS.md` @ `b840fcd5`); D1 arm O PATCHED `PASS`, arm C shipped endpoint `BLOCKED` then `PASS` under D1-C′ (`ladder-a/A1/curriculum_D1/RESULTS.md` @ `b10260a0`). Checked: optimiser convergence line + endpoint FD, both rows. |
| **2D · steady · subsonic-compressible** | CAN NOT DO — not attempted; **`PENDING: cases/dafoam/ladder-a/A1/curriculum_D15/PREREGISTRATION.md`** @ `8fc2bdeb` (D15, `DARhoSimpleFoam` M 0.288, two-row X + FD chain frozen and on the drop path as `verification/queue/dafoam/D15_chain.json`; a queue state, no verdict — *Correction 1a*) | CAN NOT DO — not attempted (D15 runs no optimiser) |
| **2D · steady · transonic** | CAN NOT DO — not attempted; **`PENDING: cases/dafoam/ladder-a/A1/curriculum_D16/PREREGISTRATION.md`** @ `3ccb0c81` (D16, `DARhoSimpleCFoam` M 0.685, frozen, `verification/queue/dafoam/D16_chain.json`; a queue state, no verdict — *Correction 1a*) | CAN NOT DO — not attempted (D16 runs no optimiser) |
| **2D · steady · supersonic** | CAN NOT DO — not attempted (~~the image ships `Cone_Supersonic`; never staged~~ **the tutorial checkout carries `Cone_Supersonic`** — neither image ships the DAFoam tutorials; the checkout is on the host at `/home/ubuntu/dafoam-tutorials` @ `d3b7e38b` (UPDATE N); never staged; **D17 on that case: pending freeze, lane N2** — no `curriculum_D17` directory or commit exists at this write, so no `PENDING: <path>` can be cited yet — *Correction 1a*) | CAN NOT DO — not attempted |
| **2D · steady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · steady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **2D · unsteady · incompressible** | **CAN DO, CAVEATS** — the time-accurate unsteady adjoint **reaches** (`DAPimpleFoam`, `GATE REACHED`, `cases/dafoam/probes/curriculum_D12_unsteady_probe/RESULTS.md` @ `4d9d902b`), but **no admissible FD step**: D12R2 phase 1 `G12R-4` = `NOT A RESULT` — *"`h_min = 1.742838e-01` EXCEEDS the registered `h_max = 5.000e-02`; no admissible FD step exists at `W = 300`"* (`cases/dafoam/curriculum_D12R2/RESULTS.md` @ `65882eb3`); W2 `BLOCKED` (aggregate guard); ~~W2R at `W = 900` running with phases 2–4 and their plan steps queued agent-independently~~ **W2R at `W = 900`: phase 1 complete on disk (ledger `PHASE1_COMPLETE spent=105.2334 core-min`), the frozen comparator's plan step wrote `step_plan.json` `admissible: false`, `h_min = 1.575533e-01` vs `h_max = 5.000e-02`, and phase 2 launched nothing by its registered branch — its `RESULTS_W2R.md` is NOT yet at HEAD (owed by the W2R scoring lane), so no verdict from it enters this cell** *(corrected 2026-08-26, Correction 1 below)* (`curriculum_D12R2/W2R_PREREGISTRATION.md` @ `5d1f89cd`); its primary prediction P3 is again *no admissible step* (`W2R_PREREGISTRATION.md:96`). Caveats: no admissible FD step at W = 300; single mesh (2,450 cells); `St ≈ 0.53` is a resolution artifact never quoted as a Strouhal number. | **CAN NOT DO** — attempted: D12 → D12R → D12R2 phases 2–4 all gated on `G12R-11` ~~(`curriculum_D12R2/RESULTS.md` @ `65882eb3`)~~ **— defined at `cases/dafoam/curriculum_D12R2/PREREGISTRATION.md:277` @ `e6580910` ("`G12R-11` (optimisation)"), the token does not occur in the RESULTS record** *(corrected 2026-08-26, Correction 1 below)* — which authorises S8 only after an FD-verified gradient; the FD line stops at `G12R-4`, so the optimiser was never authorised (`curriculum_D12R2/RESULTS.md:12` @ `65882eb3`, and `:165` "PHASE 2 WAS NOT" launched). What would fix it: an admissible step at a longer averaging window (~~W2R, `W = 900`, running; phases queued~~ **W2R at `W = 900` returned `admissible: false` on disk; the next window is the W3 draft, `curriculum_D12R2/W3_PREREGISTRATION_DRAFT.md`, NOT frozen** *(corrected 2026-08-26, Correction 1 below)*) or an objective whose window derivative `δ_window` cancels by construction. |
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
| **3D · steady · incompressible** | **CAN DO, CAVEATS — 4 cases** (A4 two optimisations, A5 re-verification, D11 MRF probe); **strongest case `cases/dafoam/ladder-a/A4/first_optimisation_np1/RESULTS.md` @ `5d1718df`**: endpoint FD at the converged design **`PASS` 0.4936 %**, zero flips, patched image; A4 shipped row PASS 1.10 % at the baseline (`docs/dafoam/README.md:92` @ ~~`ddb99eca`~~ **`2a93ff27`** — the README did not exist at `ddb99eca` *(corrected 2026-08-26, Correction 1 below)*, record `ladder-a/A4_ahmed_body.md:195`). Caveats: A5 U-bend SHIPPED row `GATE FAIL` **46.84 %, two sign flips** (IDWarp rotation defect), PATCHED `PASS` on the aggregate band with **5 of 27 components outside** it (`ladder-a/A5/reverify_patched_idwarp_np1/RESULTS.md` @ `35171866`); D11 MRF adjoint `GATE REACHED` — agrees with a central FD (`probes/curriculum_D11_mrf_probe_Fprime/RESULTS.md` @ `52a213ad`) — but the base probe `NOT A RESULT` (all stages died); ~~D10 thermal objective reaches the adjoint (`GATE REACHED`) while its FD table is `NOT A RESULT` (`ladder-a/A5/curriculum_D10_probe_Fprime/RESULTS.md` @ `4d9d902b`)~~ **D10-P′ thermal objective (`DAFunctionWallHeatFlux`) reaches the adjoint — `GATE REACHED` (`ladder-a/A5/curriculum_D10_probe_Pprime/RESULTS.md:5` @ `4d9d902b`) — and its FD pair D10-F′ is `PASS`: `d(HFX)/d(patchV[0])` agrees with a central FD at a proved plateau step to 4.401007e-08 relative against a 5.0e-2 band, one component, np=1 (`ladder-a/A5/curriculum_D10_probe_Fprime/RESULTS.md:9-13` @ `4d9d902b`); the base D10 probe is `NOT A RESULT` — grader refused, exit 2, on its own planted control (`ladder-a/A5/curriculum_D10_probe/RESULTS.md:5` @ `52a213ad`)** *(corrected 2026-08-26, Correction 1 below)*; D9 U-bend `NOT A RESULT` (`ladder-a/A5/curriculum_D9/RESULTS.md` @ `f8916f36`). | **CAN DO, CAVEATS — 2 converged, 2 not**; **strongest case `ladder-a/A4/first_optimisation_np1/RESULTS.md` @ `5d1718df`**: `EXIT: Optimal Solution Found.` in 9 majors, NLP error 6.28e-07, **CD −7.478 %**, endpoint FD `PASS`; the shipped row also converges (`Optimal Solution Found.`, NLP error 6.9114e-08, ~~fewer majors~~ **6 majors (`:13-14`)** *(corrected 2026-08-26, Correction 1 below)* — `ladder-a/A4/shipped_optimisation_np1/RESULTS.md` @ `f9a59d47`). Caveats: **unconstrained A4 only** — the constrained Ahmed item D3 is `BLOCKED` on an instrument (`nom_addThicknessConstraints2D` surface name) across two attempts (`ladder-a/A4/curriculum_D3_attempt2/RESULTS.md` @ `6b8d6355`); D9 U-bend SLSQP driver failed (`G9-3 GATE FAIL`, probe `NOT A RESULT` @ `f8916f36`); single mesh per case. |
| **3D · steady · subsonic-compressible** | **CAN DO — 3 cases** (A2 grading confirmation, D4, D4-SHIPPED grader path); **strongest case `cases/dafoam/ladder-a/A2/curriculum_D4/RESULTS.md` @ `1697ea49` §11**: endpoint FD at the corrected optimum, `G5 PASS` **5 of 5 registered components, aggregate 0.1634 % against 5 %, zero sign flips, zero without a plateau**, np=4 `scotch`, patched image (`ARMF3_d4_grade_verdict.json` @ `4eae12f4`); the SHIPPED row at the baseline `PASS` six rows, `CD/shape` **1.714 %** (`ladder-a/A2/grading_confirmation/RESULTS.md` @ `35171866`). Checked: FD-vs-adjoint per DV with plateau, planted zero, decomposition determinism (G8), toolchain identity by `.so` md5 (G9). Noted, not a caveat on the gradient: the D4-SHIPPED item closed `NOT A RESULT` on its grader path before its F3 table was graded (`ladder-a/A2/curriculum_D4_SHIPPED/RESULTS.md` @ `b26b875c`); **D14-M shows the mesh is regenerable bit-for-bit** (`ladder-a/A2/curriculum_D14/RESULTS.md` @ `60cfd4c8`). Supporting mesh-reproduction citation, added 2026-08-26 (Correction 1): **D14-M item `PASS` — the pyHyp toolchain reproduces the 38,304-cell mesh with `points.gz` sha256 equal, P1–P6 6/6 HIT, 0.1833 core-min (C-135)** (`ladder-a/A2/curriculum_D14/RESULTS.md:1,11,18` @ `60cfd4c8`). | **CAN DO, CAVEATS — 1 converged (patched), 1 cap-stopped (shipped)**; **strongest case `ladder-a/A2/curriculum_D4/RESULTS.md` @ `1697ea49`**: PATCHED arm O `EXIT: Optimal Solution Found.` at 80 majors, **28.6758 % drag reduction at `CL = 0.5`**, rung `GATE REACHED` (G2 band A `GATE FAIL` on CL feasibility reported, endpoint FD `PASS`). Caveats: SHIPPED arm O stopped at `max_iter` 100 (`EXIT: Maximum Number of Iterations Exceeded`) and the item is `NOT A RESULT` on its grader path, 731.667 core-min named waste (`ladder-a/A2/curriculum_D4_SHIPPED/RESULTS.md` @ `b26b875c`); single mesh (38,304 cells); the number is a patched-IDWarp statement, not toolchain-independent. |
| **3D · steady · transonic** | **CAN DO — 4 cases** (D7FR two rows, A3 sweep rung 2, A6 N=16 fixed reference, A3 grading confirmation); **strongest case `cases/dafoam/ladder-a/A3/curriculum_D7FR/RESULTS.md` @ `2a93ff27`**: ONERA M6 at M 0.84, 42,120 cells, np=4 — **SHIPPED row `PASS` 5 of 5 (worst 1.959 %) and PATCHED row `PASS` 5 of 5, divergence 0.000 % on every component**, **item verdict `PASS` (`curriculum_D7FR/RESULTS.md:1` @ `2a93ff27` — "ITEM VERDICT: `PASS`"; added explicitly 2026-08-26, Correction 1)**, two distinct IDWarp `.so` md5s asserted; A3 rung 2 patched np=4 `PASS` (`ladder-a/A3/rung2_patched_idwarp_np4/RESULTS.md` @ `0f56460d`); A6 CRM N=16 with the FD reference fixed: `PASS` ≤ 5 % among graded components (`ladder-a/A6/rung_n16_fixed_reference/RESULTS.md` @ `66f42398`). Checked: FD-vs-adjoint per DV, plateau, np=4 decomposition disclosed. Scale limit, recorded: A3 at 399,360 cells and A6 at 579,072 cells are `BLOCKED` on memory/conditioning (`ladder-a/A6/adjoint_feasibility/RESULTS.md` @ `be35dcad`; `ladder-a/A3/grading_confirmation/RESULTS.md` @ `35171866`). | **CAN DO, CAVEATS — 0 converged to tolerance, 2 cap-stopped**; **strongest case `ladder-a/A6/curriculum_D8/RESULTS.md` @ `9c241fe2`**: CRM N=16 twist-only, `GATE REACHED` — stopped on its registered 3-major cap (`EXIT: Maximum Number of Iterations Exceeded.`), never `PASS` by `DAFOAM_CHARTER.md` §9. Caveats: D7R arm O (M6, 30 majors at `max_iter`) `NOT A RESULT` — the grader refused and the 30.40 % reduction lies outside the frozen band (`ladder-a/A3/curriculum_D7R/RESULTS.md` @ `2b50394a`); no `Optimal Solution Found.` exists on record in this cell; single mesh per case. |
| **3D · steady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · steady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · steady · multiphase-free-surface** | CAN NOT DO — not attempted (~~the image ships `JBC_Hull`; never staged~~ **the tutorial checkout carries `JBC_Hull`** — `/home/ubuntu/dafoam-tutorials` @ `d3b7e38b`, not in either image (UPDATE N); never staged — *Correction 1a*) | CAN NOT DO — not attempted |
| **3D · unsteady · incompressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · subsonic-compressible** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · transonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · supersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · hypersonic** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |
| **3D · unsteady · multiphase-free-surface** | CAN NOT DO — not attempted | CAN NOT DO — not attempted |

**Census:** 5 of 36 cells carry evidence (2D·steady·incompressible, 2D·unsteady·incompressible, 3D·steady·incompressible, 3D·steady·subsonic-compressible, 3D·steady·transonic); **31 not attempted**. Gradient column: CAN DO 3, CAN DO CAVEATS 2. Optimisation column: CAN DO 1, CAN DO CAVEATS 3, CAN NOT DO (attempted) 1. **Checks never performed anywhere in the family, stated so the grid cannot imply them: dot-product/duality test, complex-step** (Sanaa's §6 list); **no grid family exists on any DAFoam case, so no GCI is quoted anywhere above** (standing rule 5). **Correction 1 (2026-08-26) moved no verdict: the census above is unchanged.**

### verification audit of the dafoam table

**at HEAD: `4228f216`** (`docs/capability/dafoam_GRID_AUDIT.md`, reproduced verbatim; its own footer is superseded by the merged footer below):


**Written 2026-08-26 by verification lane `ht` for the verification-supervisor.** Zero compute. The file audited is the blob committed at `6fcfe713` (byte-identical to the blob at HEAD when this audit was written: md5 `51bb9649…`). Method: (1) run the file's own 26-sha footer loop; (2) for each of the five evidenced cells, `git show <sha>:<path>` at the sha the grid cites and read the quoted verdict and numbers from the record's own lines. What the record says is quoted; where the grid and the record differ, the difference is stated with its direction.

#### 1. Footer loop — 26 shas

`for s in 15767999 … 2b50394a; do git cat-file -e "$s^{commit}"; done` → **26 ok, 0 MISSING, 26 distinct.** Matches the footer's own reading ("26 ok, 0 MISSING, 26 distinct shas").

#### 2. The five evidenced cells, citation by citation

| # | cell / citation | resolved at the cited sha | verdict matches | numbers — the record's own words | mismatch |
|---|---|---|---|---|---|
| 1 | **2D·steady·incompressible** — D13 `cases/dafoam/ladder-a/A1/curriculum_D13/RESULTS.md` @ `15767999`, "worst 0.2568 / 0.2540 / 0.2557 %", "three restarts … 9–11 majors at `CD = 0.017527…` (spread ≤ 2e-7)" | yes | **yes** — s1/s2/s3 rows: `PASS`, `EXIT: Optimal Solution Found.`, 11 / 9 / 10 majors, **4/4**, worst FD **0.2568 % / 0.2540 % / 0.2557 %** (`:26-28`) | `:20` "**Per start — all five**"; `:29-30` s4 `PASS` 9 majors worst **0.2591 %**, s5 `PASS` 10 majors worst **0.2582 %**; `:234` "4 of 4 named components graded on every start, zero sign flips, **worst relative error 0.2591 %**"; `:122-123` "All six `CD` values span 0.017527829… … 0.017528032… — a spread of **2.036213e-07**" | **Scope understated, worst number understated.** The record has **five** perturbed starts, not three; the family-worst FD is **0.2591 %** (s4), not 0.2568 %; the CD spread is **2.04e-7**, marginally above the grid's "≤ 2e-7". Verdicts unaffected (all five `PASS`, all inside the 5 % band); the grid's "CAN DO — 4 cases (D13 three restarts …)" should read five starts and quote 0.2591 % as the worst. |
| 2 | **2D·unsteady·incompressible** — D12 `cases/dafoam/probes/curriculum_D12_unsteady_probe/RESULTS.md` @ `4d9d902b`, "`DAPimpleFoam`, `GATE REACHED`" | yes | **yes** — `:5` "**`GATE REACHED`.** The **unsteady adjoint** — `DAPimpleFoam` under `DAFoamBuilderUnsteady` … returns a finite, non-zero total derivative of a time-averaged objective"; `:106` "This file's verdict — `GATE REACHED` — STANDS UNCHANGED" | — | none |
| 3 | **2D·unsteady·incompressible** — D12R2 `cases/dafoam/curriculum_D12R2/RESULTS.md` @ `65882eb3`, "`G12R-4` = `NOT A RESULT` — `h_min = 1.742838e-01` EXCEEDS the registered `h_max = 5.000e-02`; no admissible FD step exists at `W = 300`" | yes | **yes** — `:12` "**`G12R-4` STEP SIZING = `NOT A RESULT`. `h_min = 1.742838e-01` EXCEEDS the registered** …"; `:51` table row "`NOT A RESULT` — `h_min = 1.742838e-01` vs `h_max = 5.000e-02`; `steps: []`, `admissible: false`"; `:127` "Measured: `h_min = 0.1743`, 3.49× over" | The optimisation column cites the same record for "phases 2–4 all gated on `G12R-11`" — **the token `G12R-11` does not occur in `RESULTS.md` at `65882eb3`** (0 hits); it is defined in `cases/dafoam/curriculum_D12R2/PREREGISTRATION.md:277` ("`G12R-11` (optimisation)"). The RESULTS record carries the substance under its own words — `:165` "PHASE 2 WAS NOT LAUNCHED, BY THE REGISTERED BRANCH — AND THAT IS THE RESULT", `:172` "Phase 2 is NOT LAUNCHED. That is a RESULT, not a failure", `:175` "the FD line terminates" | **Citation path imprecise, substance holds.** The gate name should be cited to the pre-registration; the `NOT A RESULT` and the not-launched optimiser are as the record says. W2R prereg @ `5d1f89cd` resolves. |
| 4 | **3D·steady·incompressible** — A4 `cases/dafoam/ladder-a/A4/first_optimisation_np1/RESULTS.md` @ `5d1718df`, "endpoint FD `PASS` 0.4936 %, zero flips"; "`Optimal Solution Found.` in 9 majors, NLP error 6.28e-07, CD −7.478 %" | yes | **yes** — `:15` "The endpoint gradient verifies: `CD wrt shape` = 0.4936% against its own FD, zero sign flips"; `:161-163` "relative error `4.936157e-03` = 0.4936%" / "verdict against the lab band (PASS ≤5%, zero flips) — **PASS**"; `:13` "CD fell 7.478%"; `:75` major **9**, `inf_du` **6.28e-07**; `:84` `EXIT: Optimal Solution Found.` | — | none |
| 5 | **3D·steady·subsonic-compressible** — D4 `cases/dafoam/ladder-a/A2/curriculum_D4/RESULTS.md` @ `1697ea49` **§11**, "G5 `PASS` 5 of 5, aggregate 0.1634 % against 5 %, zero sign flips, zero without a plateau"; optimisation "80 majors, 28.6758 %, rung `GATE REACHED`, G2 band A `GATE FAIL`" | yes | **yes** — `:522` "## 11. THE BRIGHT LINE IS CROSSED"; `:530-533` "**RUNG VERDICT: `GATE REACHED`.** … G5 — the bright line — is `PASS`: five of five registered components, aggregate vector-relative error **0.1634 %** against a 5.0 % band, **zero sign flips**, **zero components without a plateau**, **zero near-zero**"; `:576` "`0.1634451673004621 %`"; `:606` G5 row `PASS`; `:127-128` G3 `PASS` at 80 majors, G4 28.6758 %; `:637` "11.6 G2 BAND A IS A `GATE FAIL`" | The same record's earlier sections still carry **G5 `BLOCKED`** (`:129`, `:422`, `:500`, `:518` "D4's rung verdict stays `BLOCKED`") — struck-not-rewritten history superseded by §11. The grid cites §11 explicitly, which is the correct reading. | none (the §11 qualifier in the grid is load-bearing and present) |
| 6 | **3D·steady·transonic** — D7FR `cases/dafoam/ladder-a/A3/curriculum_D7FR/RESULTS.md` @ `2a93ff27`, "SHIPPED row `PASS` 5 of 5 (worst 1.959 %) and PATCHED row `PASS` 5 of 5, divergence 0.000 % on every component, item `PASS`, two distinct IDWarp `.so` md5s" | yes | **yes** — `:1` "ITEM VERDICT: **`PASS`** — SHIPPED row `PASS` (5 of 5, worst 1.959 %), PATCHED row `PASS` (5 of 5, worst 1.959 %); shipped-vs-patched divergence **0.000 % on every component**"; `:3` "A3 ONERA M6, 42,120 cells, np=4"; `:58-60` rows (worst 1.9589 %, sign flips 0), G9 two distinct `.so` md5s **True** | — | none |

#### 3. Result

- **Citations audited: 6 (five cells; the 2D·unsteady cell has two). Resolved at the cited sha: 6 of 6. Verdict token matches the record: 6 of 6.**
- **Numeric / scope mismatches: 1** (D13 — five starts not three; worst 0.2591 % not 0.2568 %; spread 2.04e-7 not ≤ 2e-7; direction: the grid understates both the evidence base and the worst error, so no verdict moves).
- **Citation-path imprecision: 1** (`G12R-11` lives in the D12R2 pre-registration, not in the RESULTS record cited; substance confirmed in the RESULTS record's own words).
- **Nothing found that would move any of the ten verdicts** in the five evidenced cells. The 21 secondary citations inside those cells (be35dcad, cffd90e7, bb5088c4, 3f8c6b13, b840fcd5, b10260a0, 5d1f89cd, ddb99eca, 35171866, 52a213ad, f8916f36, f9a59d47, 6b8d6355, 4eae12f4, b26b875c, 60cfd4c8, 0f56460d, 66f42398, 9c241fe2, 2b50394a) were resolved as commits by the footer loop and **not** re-read line by line here — stated so this audit is not taken as covering them.

**Recommended corrections to `dafoam_GRID.md` (the dafoam supervisor's to make, by dated section):** (a) 2D·steady·incompressible, both columns: "D13 five restarts", worst FD 0.2591 %, spread 2.04e-7; (b) 2D·unsteady·incompressible, optimisation column: cite `G12R-11` to `curriculum_D12R2/PREREGISTRATION.md:277`.

#### Footer — the planted control

```
for s in 6fcfe713 15767999 4d9d902b 65882eb3 5d1f89cd 5d1718df 1697ea49 2a93ff27; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: 8 ok, 0 MISSING, 8 distinct shas.

---

## Evidence: ansys-verification (VMFL register rows mapped onto cfd / heat-transfer classes)

**at HEAD: `6389b9e8`** (`docs/capability/ansys_ROWS.md`, reproduced verbatim):

# ansys-verification — EVERY REGISTER ROW MAPPED ONTO Sanaa's cfd / heat-transfer CLASSES — VERIFICATION SUPERVISOR'S DRAFT FROM THE RECORDS

**Written 2026-08-26 by verification lane `cfd` for the verification-supervisor, FROM THE RECORDS AT HEAD, as the draft the ansys-verification-supervisor (and the cfd- / heat-transfer-supervisors, whose grids these rows feed) are asked to CORRECT by appending a dated section. Zero compute.** Source of every verdict: `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` **at HEAD, commit `eadbe157`** — 29 rows. **The worktree copy of the register is STALE (51 lines short of HEAD, `git diff HEAD --stat`); it was not used and, per rule 10, not touched.** Each row also cites its own record path (`RESULTS.md` / supervisor ruling / lane report) with the sha of the commit that last touched it, and the grading artifact under `verification/runs/ansys_verification/` — five of thirteen named artifacts are at HEAD; the other eight are on disk only and are marked so (they are not cited as records).

**Taxonomy (Sanaa, `068c2bf0`):** cfd cells = dimension (2D / axisym / 3D) × time (steady / unsteady) × regime (incompressible / subsonic-compressible / transonic / supersonic / hypersonic / multiphase-free-surface); heat-transfer cells = mode (conduction / forced conv / natural conv / mixed / conjugate / radiation) × laminar-vs-turbulent × dimension. **Conventions this lane chose, stated so they can be overruled:** (i) 1-D exact-solution rungs (Stokes' first problem, semi-infinite slab) are filed in the **2D** row — the taxonomy has no 1-D class; (ii) a cavitating orifice run with `interPhaseChangeFoam` to a steady discharge coefficient is filed **axisym · steady · multiphase-free-surface** with the note that it is cavitation (VoF phase change), not a free surface; (iii) VMFL002 and VMFL076 carry BOTH a cfd cell (their dP / momentum solve) and a heat-transfer cell (their temperature gate); (iv) "axisym" is asserted only where the prereg or the mesh at HEAD says `wedge` (`grep -l wedge` on `constant/polyMesh/boundary` under `verification/runs/ansys_verification/<case>/`: VMFL002, 003, 003_M2, 005, 007, 021, 022, 036 — all others are Cartesian planar).

**Verdict vocabulary.** The register's tokens (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `PENDING`) are copied verbatim. **Only `PASS` rows are credentials** (register reading rule). Rows that are `NOT A RESULT` because a **frozen comparator refused** rather than because the physics failed are said so per row: the refusal classes on record are the v2606 filename mismatch (row #1), the iterative-convergence residual leg (rows #6, #9, #10), the transverse-residual normalisation-noise clause (**L-338**, row #25), the planted-zero threshold on an averaging reader (**L-340**, row #26), and the wall-shear sign-change reader (row #29). A refusal is not a physics result and not a physics failure; it is also not a credential.

## 1. Class per case, derived from the frozen pre-registration by path:line

| case | solver / conditions (path:line) | cfd cell | heat-transfer cell |
|---|---|---|---|
| VMFL001 / -R2 concentric rotating cylinders | `simpleFoam`, steady laminar, **Re_gap = 2.53**, planar r–θ annulus 64 × 256 — `cases/ansys_verification/VMFL001/PREREGISTRATION.md:25-26,60-63` | 2D · steady · incompressible (laminar) | — |
| VMFL002 laminar pipe, uniform heat flux | `simpleFoam` + `scalarTransport` T, **axisymmetric 5° wedge**, laminar mercury — `cases/ansys_verification/VMFL002/PREREGISTRATION.md:8-11,35` | axisym · steady · incompressible (laminar) | **forced conv · laminar · axisym** |
| VMFL003 / VMFL003-M2 (arms A–D) turbulent pipe | `simpleFoam`, k-ε / realizableKE / RNG / kOmegaSST + `nutkWallFunction`, axisym wedge (mesh `L3_1000x5`), Δp vs Moody/Colebrook — register rows #6, #9–#12 | axisym · steady · incompressible (turbulent) | — |
| VMFL004 / -R2 Couette–Poiseuille | `simpleFoam`, steady incompressible laminar, ν = 1, Cartesian 2-D — `cases/ansys_verification/VMFL004/PREREGISTRATION.md:45,106-109` | 2D · steady · incompressible (laminar) | — |
| VMFL005 Poiseuille pipe | `simpleFoam`, axisym wedge `L3_400x40`, Hagen–Poiseuille dP — register row #3 | axisym · steady · incompressible (laminar) | — |
| VMFL007 non-Newtonian pipe | `simpleFoam`, axisym wedge, power-law (Rabinowitsch–Mooney) — register row #8 | axisym · steady · incompressible (laminar, non-Newtonian) | — |
| VMFL010 90° tee | `simpleFoam`, steady laminar incompressible, planar branch — `cases/ansys_verification/VMFL010/PREREGISTRATION.md:24-30,46` | 2D · steady · incompressible (laminar) | — |
| VMFL011 triangular cavity | `simpleFoam`, steady laminar, **Re = 400** — `cases/ansys_verification/VMFL011/PREREGISTRATION.md:43-44` | 2D · steady · incompressible (laminar) | — |
| VMFL017 RAE 2822 | `rhoSimpleFoam` + kOmegaSST, steady, 2-D C-mesh, **transonic** (magUInf 253.5 m/s) — `cases/ansys_verification/VMFL017/PREREGISTRATION.md:8-9,22,32` | 2D · steady · transonic (turbulent) | — |
| VMFL019 Stokes' first problem | `icoFoam`, transient laminar, ν = 1e−3, 1-D bar — `cases/ansys_verification/VMFL019/PREREGISTRATION.md:25` | 2D · unsteady · incompressible (laminar; 1-D) | — |
| VMFL021 / -R2, VMFL022 cavitating orifice | `interPhaseChangeFoam` / SchnerrSauer / k-ε, **axisymmetric 5° wedge** — `cases/ansys_verification/VMFL021/PREREGISTRATION.md:16-18,46-50`; `VMFL022/PREREGISTRATION.md:15-17,53-61` | axisym · steady · multiphase-free-surface (cavitation, turbulent) | — |
| VMFL023 oscillating cylinder | `pimpleFoam`, **Re = 100**, St from lift zero-crossings — `cases/ansys_verification/VMFL023/PREREGISTRATION.md:17,24-27` | 2D · unsteady · incompressible (laminar) | — |
| VMFL033 viscous heating annulus | `buoyantSimpleFoam` (rhoConst), laminar, **2-D planar, NOT an axisymmetric wedge**, Re 3.3e−3 — `cases/ansys_verification/VMFL033/PREREGISTRATION.md:20,57-62,80,126` | 2D · steady · incompressible (laminar) | **forced conv (viscous dissipation) · laminar · 2D** |
| VMFL036 sphere | `simpleFoam`, steady laminar, **axisymmetric wedge**, Re = 100 — `cases/ansys_verification/VMFL036/PREREGISTRATION.md:18,43,51` | axisym · steady · incompressible (laminar) | — |
| VMFL045 / -R2 oblique shock ramp | `rhoCentralFoam`, **inlet Mach ≈ 2.5**, 15° ramp, laminar (μ = 1e−8) — `cases/ansys_verification/VMFL045/PREREGISTRATION.md:47-48`; register row #7 | 2D · steady · supersonic | — |
| VMFL050 semi-infinite slab | `laplacianFoam`, transient conduction, 1-D bar — `cases/ansys_verification/VMFL050/PREREGISTRATION.md:29-30` | — | **conduction · (no flow) · 2D (1-D bar)** · unsteady |
| VMFL051 Prandtl–Meyer corner | `rhoCentralFoam`, inviscid, post-expansion **M = 3.237** target, 2-D — `cases/ansys_verification/VMFL051/PREREGISTRATION.md:41,45`; register row #4 | 2D · steady · supersonic | — |
| VMFL059 composite block | `laplacianFoam` steady limit, Cartesian planar 2-D — `cases/ansys_verification/VMFL059/PREREGISTRATION.md:25,61-62` | — | **conduction · (no flow) · 2D** · steady |
| VMFL064 / -R2 asymmetric expansion | `simpleFoam`, laminar, **Re_D = 200**, Cartesian planar 2-D — `cases/ansys_verification/VMFL064/PREREGISTRATION.md:4,41-44,66` | 2D · steady · incompressible (laminar) | — |
| VMFL076 flat plate, low Pr | `simpleFoam` laminar + `scalarTransport`, **Re_L = 9.0e4, Pe_L = 270**, planar 2-D — `cases/ansys_verification/VMFL076/PREREGISTRATION.md:21,76-77,108,174` | 2D · steady · incompressible (laminar) | **forced conv · laminar · 2D** |

## 2. Every register row (HEAD `eadbe157`), mapped

| # | case | class (cfd cell / heat cell) | register verdict | what the record says (lab value → reference; triple) | record path @ sha; grading artifact |
|---|---|---|---|---|---|
| 1 | VMFL001 | 2D·steady·incompressible | **`NOT A RESULT`** | **Comparator refusal (exit 2)** — frozen reader expected `U_gateAxis.*` with a header, v2606 wrote header-less `gateAxis_p_U.xy`; independently L3 missed the 1e−6 residual clause. No number produced. | `cases/ansys_verification/VMFL001/RESULTS.md` @ `ebb7da5a`; `verification/runs/ansys_verification/VMFL001/GRADING_VMFL001.stdout.txt` |
| 2 | VMFL001-R2 | 2D·steady·incompressible | **`PASS`** (credential) | v_θ at r = 20/25/30/35 mm 0.0151121 / 0.0105288 / 0.0071835 / 0.0045458 m/s vs White §3-2.3 analytic 0.0151/0.0105/0.0072/0.0046, all inside 2 %; **CONVERGING, p = 2.0102, GCI_fine 0.0563 %**, Richardson extrapolate on exact to 3.7 ppm (register §tier table). | `cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196` |
| 3 | VMFL005 | axisym·steady·incompressible | **`PASS`** (credential) | dP = 10.2909853852 Pa vs Hagen–Poiseuille 10.24 Pa (0.498 %, band 2 %); **CONVERGING, p 1.9341, GCI_fine 0.0502 %**; extrapolate 0.538 % from exact — deviation/GCI 9.92, so the code is measured NOT to converge to exact (register tier note; coverage §3.6). | `cases/ansys_verification/VMFL005/RESULTS.md` @ `4bb0f6a1`; `verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json` |
| 4 | VMFL051 | 2D·steady·supersonic | **`NOT A RESULT`** | Ma = 3.2294 (L3 zone average) vs 3.2370 target — in band, but **G absent: triple not CONVERGING** (register tier table: "V present, G ABSENT, and G decides it"). Physics ran; rule 5 took it. | `cases/ansys_verification/VMFL051/RESULTS.md` @ `63c8d044`; `verification/runs/ansys_verification/VMFL051/GRADING_VMFL051.json` |
| 5 | VMFL045 run 1 | 2D·steady·supersonic | **`NOT A RESULT`** | `rhoCentralFoam` **crashed on its first timestep** (`Entry 'e' not found in fvSolution/solvers`) — a case-file defect inherited from the inviscid VMFL051; nothing gradeable. | `cases/ansys_verification/VMFL045/RESULTS.md` @ `64b02355` |
| 6 | VMFL003 | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | Δp = 20 800.82 Pa vs 21 744 Pa (−4.34 %, band 2.5 %: `gate_verdict_before_rule5 = GATE FAIL`); **comparator refused at rule 5 step 1 — all three levels failed the frozen residual leg** (ε 2.52e−08 vs 1e−08 at L3). Model statement beside it: k-ε under-predicts pipe friction −4.6 % vs Colebrook. | `cases/ansys_verification/VMFL003/RESULTS.md` @ `288a5862`; `verification/runs/ansys_verification/VMFL003/GRADING_VMFL003.json` |
| 7 | VMFL045-R2 | 2D·steady·supersonic | **`PASS`** (credential; tier `GATE REACHED` inline) | M₂ = 1.874779 at L3 vs 1.874 (band 1 %), per level 1.87198 / 1.87453 / 1.87478; **observed order 3.3862 — measured but NOT trusted** as G (register row text). | `cases/ansys_verification/VMFL045/R2/RESULTS.md` @ `f4332fe3` |
| 8 | VMFL007 run 1 | axisym·steady·incompressible (non-Newtonian) | **`NOT A RESULT`** | **DIVERGED** — inlet pressure grew 3.02e4 → 9.45e+… over 10 000 iterations with rc 0 and `End`; no number. A physics/setup failure, not a refusal. | `cases/ansys_verification/VMFL007/RESULTS.md` @ `2793f23e` |
| 9 | VMFL003-M2 arm A (k-ε) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | Δp = 20 800.82 Pa, −4.34 % vs target (−4.55 % vs Colebrook); **refused at the residual leg** (L3 ε 2.49e−08 vs 1e−08); the endTime bump did not fix it. | `cases/ansys_verification/VMFL003_M2/GRADING_LANE_REPORT.md` @ `64b367ef` |
| 10 | VMFL003-M2 arm B (realizableKE) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | Δp = 20 278.13 Pa, −6.74 % (**realizableKE under-predicts friction more than k-ε**); **refused at the residual leg** (L3 k 1.38e−07, ε 7.49e−08). | same lane report @ `64b367ef` |
| 11 | VMFL003-M2 arm C (RNG k-ε) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | **Ladder incomplete — the frozen 40 core-min per-arm cap fired** at `Time = 4085` of 18 000 (22.7 %); no Δp graded; no fresh cap (rule 12). Ruled `aba61e53`. | `cases/ansys_verification/VMFL003_M2/TRIAGE_ARM_D_BUDGET_STOP.md` @ `2dcea996` |
| 12 | VMFL003-M2 arm D (kOmegaSST) | axisym·steady·incompressible (turbulent) | **`NOT A RESULT`** | **Ladder incomplete — cap fired to the second** at `Time = 5949` of 22 000 (27 %); L3 ran 7× over its mesh scaling; no Δp graded. Ruled `2dcea996`. | same triage @ `2dcea996` |
| 13 | VMFL019 | 2D·unsteady·incompressible (1-D) | **`PASS`** (credential) | u_x(0.05 m, 5 s) = 6.16765e−3 (dev 0.050 %) and u_x(0.10 m, 5 s) = 3.17008e−3 m/s (dev 0.095 %) vs U·erfc(·), band 1 %; **both triples CONVERGING, p 1.0933 / 0.9881, GCI_fine 0.058 % / 0.121 %** (space and time refined together). | `cases/ansys_verification/VMFL019/RESULTS.md` @ `f3fad674`; `verification/runs/ansys_verification/VMFL019/GRADING_VMFL019.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 14 | VMFL010 | 2D·steady·incompressible | **`NOT A RESULT`** | flow split 0.88475 vs 0.887 (0.26 %, band 3 % — value-only reading would be inside); **triple OSCILLATORY** (0.88595 / 0.88445 / 0.88475) → rule 5 step 2, no GCI. Physics ran; rule 5 took it. | `cases/ansys_verification/VMFL010/RESULTS.md` @ `f3fad674`; `verification/runs/ansys_verification/VMFL010/GRADING_VMFL010.stdout.txt` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 15 | VMFL050 | **heat: conduction · 2D (1-D bar) · unsteady** | **`PASS`** (credential; tier capped `GATE REACHED` by a frozen clause) | wall T = 392.977 K (0.023 % on the rise) and T(150 mm) = 318.401 K (0.006 %) vs Incropera analytic, band 1 % on the rise; **both triples CONVERGING** — wall p 0.6883, p150 **p 5.5982** (noise-floor order → ceiling `GATE REACHED`, `HOLDS` refused). | `cases/ansys_verification/VMFL050/SUPERVISOR_RULING_VERDICT.md` @ `311feb37`; `verification/runs/ansys_verification/VMFL050/GRADING_VMFL050.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 16 | VMFL059 | **heat: conduction · 2D · steady** | **`NOT A RESULT`** | cooled wall 378.0 K vs 378 K and adiabatic wall 412.948 K vs 413 K — solve clean at all levels; **`rightWall` triple EXACT (378.0 / 378.0 / 378.0)** → rule 5; *"a MIS-SPECIFIED GATE QUANTITY, not a failed solve"*. | `cases/ansys_verification/VMFL059/SUPERVISOR_RULING_VERDICT.md` @ `6a9afa0a` |
| 17 | VMFL022 case B | axisym·steady·multiphase (cavitation) | **`NOT A RESULT`** | L3 Cd = 0.75918 vs Nurick 0.780 (band 5 %); **triple OSCILLATORY** (0.74442 / 0.76091 / 0.75918), p and GCI `None` → rule 5. Physics ran. | `verification/runs/ansys_verification/VMFL022/LANE_REPORT_opus48_collision.md` @ `2e83a89b`; `verification/runs/ansys_verification/VMFL022/GRADING_VMFL022.json` |
| 18 | VMFL021 attempt 1 | axisym·steady·multiphase (cavitation) | **`NOT A RESULT`** | Run cannot be certified (two independent instrument defects) although the physics was going right (Cd 0.663 → 0.642 toward 0.620, stable at P1 = 2.5e8 Pa). Re-run registered as row #23. | register row only (no separate RESULTS path at HEAD) |
| 19 | VMFL017 | 2D·steady·transonic | **`PENDING`** | **`rhoSimpleFoam` DIVERGES** (`Negative initial temperature T0`); no gradeable run; a queue state, NOT a softened `GATE FAIL`. | `cases/ansys_verification/VMFL017/RESULTS.md` @ `f746233a` |
| 20 | VMFL036 | axisym·steady·incompressible | **`GATE REACHED`** (not a credential) | Cd = 1.088834 at L3 (49 152 cells) vs Mittal (1999) 1.0895, band 3 %; **CONVERGING** 1.091486 / 1.089233 / 1.088834, r = 2 by construction; ceiling `GATE REACHED` frozen on prereg lines 3–4 (numerical-benchmark reference); arm B (μ = 0.02 as printed) shows the manual's μ is a transcription error. | `cases/ansys_verification/VMFL036/RESULTS.md` @ `a86357e6` |
| 21 | VMFL033 | 2D·steady·incompressible / **heat: forced conv (viscous heating) · laminar · 2D** | **`NOT A RESULT`** | T_avg(finest) = 286.8955 K; **two of three levels NOT PLATEAUED** (ptp/rise 6.5e−05 and 7.8e−03 vs a frozen 1e−06 floor) and **triple OSCILLATORY (R = −398.5)** → rule 5 step (1); the prereg named this failure before compute. Comparator repaired under §2d.1 before grading (8 mutants × 2 interpreters). | `cases/ansys_verification/VMFL033/RESULTS.md` @ `f5a81a69` |
| 22 | VMFL023 | 2D·unsteady·incompressible | **`GATE REACHED`** (not a credential) | St = 0.165993 at L3 (384 × 128) vs 0.165 (experimental St–Re correlation, White / Kim & Lee), band 3 %; **CONVERGING, p = 1.9140 vs formal 2, GCI 0.3791 %**. | `cases/ansys_verification/VMFL023/RESULTS.md` @ `c487e3c7` |
| 23 | VMFL021-R2 case A | axisym·steady·multiphase (cavitation) | **`GATE REACHED`** (not a credential) | Cd = 0.634868 at L3 vs Nurick 0.620 (2.398 %, band 5 %); **CONVERGING, p = 1.7405 vs formal 1, GCI 0.5524 %**; all three levels PLATEAU; 32.93 core-min. | `cases/ansys_verification/VMFL021/R2/RESULTS.md` @ `c487e3c7` |
| 24 | VMFL002 | axisym·steady·incompressible / **heat: forced conv · laminar · axisym** | **`GATE REACHED`** (not a credential) | dP = 1.000 Pa and centreline outlet T = 341.00 K vs manual targets 1.000 Pa / 341.00 K (White 1994 / Incropera 1981), both inside 2 % at L3, **both triples CONVERGING**; 5.2 core-min. | `cases/ansys_verification/VMFL002/RESULTS.md` @ `959a31b1`; `verification/runs/ansys_verification/VMFL002/GRADING_VMFL002.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 25 | VMFL004 | 2D·steady·incompressible | **`NOT A RESULT`** | **Frozen-instrument block, L-338 class:** volAverage(U)_x 2.50125 / 2.5003125 / 2.5000781 vs exact 2.5, **CONVERGING p = 1.99999997**, rel_dev 3.1e−5 ≪ 0.1 % band — a textbook PASS — but the inherited check gated Uy/p initial residuals (< 1e−7), which are normalisation NOISE in 1-D fully-developed flow. Not edited (rule 2); re-run is row #28. | `cases/ansys_verification/VMFL004/RESULTS.md` @ `959a31b1`; `verification/runs/ansys_verification/VMFL004/GRADING_VMFL004.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 26 | VMFL011 | 2D·steady·incompressible | **`NOT A RESULT`** | **Comparator refusal, L-340 class:** planted-zero control on `rms_vs_benchmark` (401-point RMS) moved 3.68e−7 < 0.1·plant → refused (exit 2). Physics beside it, not a verdict: rms 0.0403 / 0.0348 / 0.0341 all exceed the 3 % band (would be `GATE FAIL`); `u_min` triple CONVERGING p 1.60, extrapolate −0.3465 vs digitised −0.318 (8.9 %, OPEN). | `cases/ansys_verification/VMFL011/RESULTS.md` @ `cb5b6eb8` |
| 27 | VMFL076 | 2D·steady·incompressible / **heat: forced conv · laminar · 2D** | **`NOT A RESULT`** | **"BOTH GATES WERE MET AND RULE 5 TOOK THE ROW ANYWAY"** — Gate A |I_lab − I_ref|/I_ref = 0.9006 % vs frozen 3.00 %, Gate B 5.397e−03 vs its band; verdict `NOT A RESULT` on the triple state. Physics ran; rule 5 took it. | `cases/ansys_verification/VMFL076/RESULTS.md` @ `9c86962e`; `verification/runs/ansys_verification/VMFL076/GRADING_OUTPUT.txt` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 28 | VMFL004-R2 | 2D·steady·incompressible | **`PASS`** (credential) | volAverage(U)_x = 2.50007812 m/s vs exact 2.5, band 0.1 %; **CONVERGING on errors 5.00e−4 / 1.25e−4 / 3.13e−5, p = 1.99999760, GCI_fine 3.906e−5**; transverse mean ≤ 1e−6 clause met; four planted controls fired. Re-registration of row #25 gating on the driven Ux. | `cases/ansys_verification/VMFL004-R2/RESULTS.md` @ `6a0a1a99`; `verification/runs/ansys_verification/VMFL004-R2/GRADING_VMFL004_R2.json` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |
| 29 | VMFL064 | 2D·steady·incompressible | **`NOT A RESULT`** | **Comparator refusal (exit 2) at L3: "wall shear never changes sign — no reattachment found"**; all three levels ran clean (`SIMPLE solution converged` at 424 / 907 / 2 152 iterations); no triple, no GCI, no value vs Armaly et al. (1983) LR/s = 5 (band 10 %). Not a solver failure. Calibration C-131. | `cases/ansys_verification/VMFL064/RESULTS.md` @ `b8b5e2bf`; `verification/runs/ansys_verification/VMFL064/GRADING_ATTEMPT_REFUSED.txt` (on disk, NOT at HEAD — uncommitted grading artifact, not cited as a record) |

**Register census at HEAD `eadbe157` (recomputed from the rows, not read from the count line — the file's last printed count line reads "5 PASS of 16 run" and predates rows #17–#29):** **29 rows: `PASS` 6** (#2, #3, #7, #13, #15, #28), **`GATE REACHED` 4** (#20, #22, #23, #24), **`NOT A RESULT` 18**, **`PENDING` 1** (#19), `GATE FAIL` 0 (two rows carry `gate_verdict_before_rule5 = GATE FAIL`, #6 and #9, and closed `NOT A RESULT`). Of the 18 `NOT A RESULT`: **comparator/instrument refusals 7** (#1, #6, #9, #10, #25, #26, #29), **cap-fired ladders 2** (#11, #12), **crash / divergence 2** (#5, #8), **uncertifiable instrument 1** (#18), **rule 5 on a non-CONVERGING or EXACT triple with the physics clean 6** (#4, #14, #16, #17, #21, #27).

## 3. What the rows put into each grid cell (evidence for the cfd and heat-transfer tables — the family supervisors rule, this is the record's reading)

| cell | rows | reading in Sanaa's words |
|---|---|---|
| **2D · steady · incompressible** | #2 `PASS`, #28 `PASS`, #1/#14/#25/#26/#29 `NOT A RESULT` | **CAN DO — 2 cases**; strongest **VMFL001-R2** (`cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196`): exact-solution check at four radii, p = 2.0102, GCI 0.056 %, extrapolate on exact to 3.7 ppm — the lab's nearest row to HOLDS (coverage §3.8f). Checked: error vs exact + GCI + order. Caveat: exact-solution references only (V, never P); VMFL064's experimental reattachment is unread (refusal). |
| **2D · unsteady · incompressible** | #13 `PASS`, #22 `GATE REACHED` | **CAN DO — 1 case** (VMFL019 @ `f3fad674`, erfc exact, both triples CONVERGING) with VMFL023 St = 0.166 vs 0.165 experimental correlation `GATE REACHED` beside it (p 1.914, GCI 0.38 %). |
| **2D · steady · supersonic** | #7 `PASS`, #4 / #5 `NOT A RESULT` | **CAN DO, CAVEATS — 1 case** (VMFL045-R2 @ `f4332fe3`, M₂ = 1.87478 vs 1.874); caveat: observed order 3.39 measured but not trusted (G held back); VMFL051 Prandtl–Meyer in band but triple not CONVERGING. |
| **2D · steady · transonic** | #19 `PENDING` | **CAN NOT DO — attempted**: `rhoSimpleFoam` diverges (negative T0) on RAE 2822; nothing graded. |
| **axisym · steady · incompressible** | #3 `PASS`; #20 `GATE REACHED`; #6/#8/#9–#12 `NOT A RESULT` | **CAN DO, CAVEATS — 1 `PASS`** (VMFL005 @ `4bb0f6a1`, p 1.934, GCI 0.050 %) + sphere Cd `GATE REACHED`; caveats: VMFL005's extrapolate is measured NOT to converge to exact (deviation/GCI 9.92); **turbulent pipe: 0 of 6 arms graded** — three refusals on the residual leg, two cap-fired, all k-ε family −4.3…−6.7 % vs Moody; non-Newtonian pipe diverged. |
| **axisym · steady · multiphase-free-surface** (cavitation) | #23 `GATE REACHED`; #17 / #18 `NOT A RESULT` | **CAN DO, CAVEATS — 0 `PASS`, 1 `GATE REACHED`** (VMFL021-R2 @ `c487e3c7`, Cd 0.6349 vs Nurick 0.620, CONVERGING p 1.74, GCI 0.55 %); caveats: cavitation not free surface; case B triple OSCILLATORY; no `PASS`. |
| **heat: conduction · 2D** | #15 `PASS` (unsteady, 1-D bar), #16 `NOT A RESULT` (steady) | **CAN DO — 1 case** (VMFL050 @ `311feb37`, erfc exact, both triples CONVERGING; tier capped by a frozen noise-floor clause); steady composite wall EXACT triple → rule 5 (gate quantity mis-specified, solve clean). |
| **heat: forced conv · laminar · axisym** | #24 `GATE REACHED` | **CAN DO, CAVEATS — 0 `PASS`, 1 `GATE REACHED`** (VMFL002 @ `959a31b1`, dP and 41 K outlet rise both inside 2 %, both triples CONVERGING); caveat: reference is the manual's analytic target, tier ceiling. |
| **heat: forced conv · laminar · 2D** | #21, #27 `NOT A RESULT` | **CAN NOT DO — attempted 2**: VMFL076 met both gates and was taken by rule 5 on the triple; VMFL033 two levels not plateaued, triple OSCILLATORY. What would fix it: a plateau-clean ladder (VMFL033 L3 settled to 2e−08 already; L1/L2 need the same). |

**Structural note carried from the coverage matrix (§3.8f), still true at HEAD:** every `PASS` row is an `AN` (analytic) reference — **P (validation against measured physical reality) is green in no ansys row**; the experiment-referenced rows are VMFL064 (refused), VMFL023 (correlation, `GATE REACHED`), VMFL021/022 (Nurick, `GATE REACHED` / `NOT A RESULT`), VMFL017 (`PENDING`).

---

## Footer — the planted control: every cited sha, resolved

Run from the repository root; every line must read `ok`, and the count must equal the number of distinct shas cited above (26):

```
for s in eadbe157 ebb7da5a 5e789196 4bb0f6a1 63c8d044 64b02355 288a5862 f4332fe3 2793f23e 64b367ef aba61e53 2dcea996 f3fad674 311feb37 6a9afa0a 2e83a89b c487e3c7 f746233a a86357e6 f5a81a69 959a31b1 cb5b6eb8 9c86962e 6a0a1a99 b8b5e2bf 068c2bf0; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

(26 shas listed; 26 distinct commits. A `MISSING` line is a defect in this file, not in the record.) Reading at write time, 2026-08-26: 26 ok, 0 MISSING, 26 distinct shas; 27 verdict tokens re-read from `git show <sha>:<path>` and matched.

---

## Correction 2 — 2026-08-26, verification lane ansys-rows: register row #30 (87afd1d6) mapped; census recomputed at HEAD 8c7e1854

**Lines whose number changed above this section: 0.**

Appended by verification lane `ansys-rows` for the verification-supervisor. Zero compute. Everything below was read with `git show <sha>:<path>`; neither the worktree nor the shared index was used. **Numbering note:** no "Correction 1" section exists in this file at HEAD `8c7e1854` (the file's only prior commit is `b847b97f`); this section carries the number its supervisor assigned. **Blob identity, checked:** the register blob at HEAD `8c7e1854` is `0dabcdda…`, identical to the blob at `87afd1d6` (the last commit that touched the register), so "`@ 8c7e1854`" and "`@ 87afd1d6`" cite the same register bytes; likewise `cases/ansys_verification/VMFL064-R2/RESULTS.md` is blob `48c19ae6…` at both shas, and `VMFL064-R2/PREREGISTRATION.md` at HEAD is blob `abe17c3b…`, the blob its own RESULTS names, with `3e7c792c` the only commit that ever touched it.

### C2.1 Register row #30, read from the register at HEAD

Row #30 is one physical line — `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md:513 @ 8c7e1854`; the column header that names the 13 columns is `:22`. Every field below is from `:513` unless another line is named.

| field | reading (`ANSYS_VALIDATION_REGISTER.md:513 @ 8c7e1854`) |
|---|---|
| case | **VMFL064-R2** — Low Reynolds Number Flow in a Channel with Sudden Asymmetric Expansion (VM2026R1, p. 195/196); "Re-registration of row #29 under `ANSYS_VERIFICATION_CHARTER` §6: a NEW row that CITES row #29 and does NOT overwrite it — row #29 stands as `NOT A RESULT` and is unchanged by this row" |
| date | 2026-08-26 |
| verdict token, verbatim | **`GATE REACHED`** |
| lab value | `LR/s` = **4.853056** at L3 (49 152 cells; `LR` = 0.023779973479 m); deviation **2.9389 %** of a 10 % band ("consuming 29 % of the tolerance"); triple 4.714416 / 4.800738 / 4.853056, d21 = 0.086322377043, d32 = 0.052317864523, R = 0.606075, **`CONVERGING` and monotone**; `p_obs` = 0.722431; `GCI_fine` = 2.0733 % at Fs = 1.25; Richardson `f_ex` = 4.933550 |
| reference (source, manual page) | `LR/s` = **5** — "**EXPERIMENTAL**: Armaly, Durst, Pereira & Schoenung, *J. Fluid Mech.* **127**:473, 1983 (also Freitas, *J. Fluids Eng.* **117**, p. 208, 1995). **REFERENCE KIND: measured/experimental — CAN buy P**, and this row still does **not**, because the ceiling was lowered in advance"; Ansys Fluent 4.91 "CONTEXT ONLY, never the gate"; manual **p. 195** |
| tolerance (frozen) | `abs(LR/s − 5.0) / 5.0 ≤ 0.10` (10 %) at the finest level **and** a `CONVERGING` triple (rule 5); "BYTE-IDENTICAL to attempt 1's band"; tier ceiling **`GATE REACHED`** "declared on pre-registration line 4 and hard-coded in the comparator, which cannot print `PASS` or `HOLDS`"; "NOT A CREDENTIAL"; cap **90 core-min** |
| artifact path | `verification/runs/ansys_verification/VMFL064-R2/GRADING_VMFL064_R2.json` (with `{L1,L2,L3}/`, `RUN_RC.{L1,L2,L3}`, `COST.txt`, `LAUNCH_RECORD.txt`, `CONTENTION.txt`, `CAP_OVERRUN.txt`, `STATUS.VMFL064-R2`, `STATUS.VMFL064-R2.attempt1-refused-no-run_root`, `launcher.queue.out`, `launcher.queue.out.attempt1`). **This grading artifact IS at HEAD** (`git ls-tree HEAD` lists `GRADING_VMFL064_R2.json` plus `CAP_OVERRUN.txt`, `CONTENTION.txt`, `COST.txt`, `LAUNCH_RECORD.txt`, `RUN_RC.L1/L2/L3`, both `STATUS.*` files) — unlike the eight on-disk-only artifacts flagged in §2. |
| prereg sha | **`3e7c792cbde23a7cc105d63d01487dc5d01c8040`** ("the only commit that has ever touched that pre-registration, and it landed before any R2 solver started"); prereg blob `abe17c3b990acd31bba12fde01aaf757c6ab398e` |
| comparator sha | blob **`e04fdf937d557b4919928ab72b9fe5eb42f8b49a`** ("the launcher printed `freeze OK` against this blob before every level"); launcher blob `c17ee2e2693b382fd043aadc326bdae8e51fd7b6` |
| cost, core-min | **5.3** MEASURED (L1 0.0167 + L2 0.2833 + L3 5.0; wall 318 s × RANKS 1 ÷ 60) vs **5.4** predicted → ratio **0.98**; 5.9 % of the 90 core-min cap; WASTE 0.000; $0.0045 derived, not measured |
| RESULTS path | `cases/ansys_verification/VMFL064-R2/RESULTS.md`; calibration **C-141** (`docs/COST_CALIBRATION.md:217 @ 87afd1d6`) |

**From the record itself — `cases/ansys_verification/VMFL064-R2/RESULTS.md @ 87afd1d6` (214 lines):**

- Verdict headline, `:20`: `## VERDICT — \`GATE REACHED\``.
- Value vs reference, `:22-23`: "**`LR/s = 4.853056`** at the finest level against the experimental reference **5.0** — **2.9389 %** deviation inside the frozen **10 %** band, on a **`CONVERGING`** triple." Per level, `:40-42`: L1 3 072 cells 4.714416 (corner vortex resolved: no; crossings 1/0), L2 12 288 cells 4.800738 (no; 1/0), L3 49 152 cells 4.853056 (**yes**; 1/1). Gate at L3, `:44-45`: 2.9389 % against 10.00 % — met.
- Triple / order / GCI, `:51-54`: d21 = 0.086322377043, d32 = 0.052317864523, R = 0.606075 → `CONVERGING` (monotone, 0 < R < 1); `p_obs = 0.722431`, `GCI_fine (Fs = 1.25) = 2.0733 %`, `f_extrapolated = 4.933550`. `:57`: "**`p_obs = 0.7224` is BELOW the formal `p_f = 2`, and that is reported as what it is.**" `:61-64`: above the registered floor `P_MIN = 0.05` so a GCI is quoted; "2.0733 % is of the same order as the 2.9389 % deviation itself … not that the reattachment length has been pinned to three digits."
- What changed relative to row #29 (the refusal), `:68-72`: row #29 died at "`REFUSED (exit 2): L3: wall shear never changes sign -- no reattachment found`"; "The R2 changed the reader to the **last** crossing inside a registered window, and nothing else." `:74-79`: `corner_vortex_resolved` false at L1 and L2, true at L3; crossing census `n→p = 1, p→n = 0` at the coarse levels, `n→p = 1, p→n = 1` at L3 with the profile starting positive — "the mechanism named in row #29's triage, measured here rather than argued." `:81-84`: L1 4.714416 and L2 4.800738 "identical to the values row #29 published as the only two that existed."
- Reference kind — **experiment**, not analytic and not a correlation. `:25-26`: "The reference is experimental (Armaly et al. 1983) and experimental references *can* buy P". Pre-registration `cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md:31 @ 3e7c792c`: `3. REFERENCE KIND  : measured/experimental -- CAN buy P.` The manual's own source: `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.txt:5071-5073 @ 8c7e1854` — "Reference  B. Armaly, F. Durst, J. Pereira, B. Schönung. "Experimental and theoretical investigation of a backward-facing step". Journal of Fluid Mechanics, Vol 127, pg. 473, 1983" (Freitas 1995 at `:5075-5076`); `:5086`: "The reattachment length predicted by the solvers is validated against experimental results"; the results table `:5123`: "Non-dimensionalized Reattachment length (LR/Step-height)  5.0  4.91  0.982" (Target / Ansys Fluent / Ratio).
- Why `GATE REACHED` and not `PASS`, `:25-30`: "**`GATE REACHED` is the ceiling, and it is not a `PASS`.** … pre-registration line 4 declared the ceiling `GATE REACHED` in advance because this team's product is **reproducing the Ansys manual**, and the comparator hard-codes that string: it cannot print `PASS` or `HOLDS` whatever the number. **This row is not a credential and must not be counted as one.**" (`PREREGISTRATION.md:32-35 @ 3e7c792c` says the same: "Sanaa's ruling caps that at GATE REACHED. The comparator hard-codes GATE REACHED as the in-band verdict; it cannot print HOLDS or PASS.") `:182`: "It is not a credential. Ceiling `GATE REACHED`, declared before compute."
- Cost, `:125-131`: total 318 s, 5.3 core-min measured vs 5.4 predicted, ratio 0.98, 5.9 % of cap; `:133`: waste 0.000; `:136-138`: $0.0045 derived, C-141.

### C2.2 Its class

**cfd cell: 2D · steady · incompressible (laminar)** — confirmed from the R2 pre-registration `cases/ansys_verification/VMFL064-R2/PREREGISTRATION.md @ 3e7c792c` (= HEAD blob): `:24-25` "Solver = simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, Re_D = 200, 2-D Cartesian"; `:60` "simpleFoam, laminar (momentumTransport = laminar), SIMPLEC consistent yes"; `:63` "Inlet uniform 0.288462 m/s (Re_D = 200.0 on D = 10.4 mm)"; `:70` "z = 1 cell (2-D). SERIAL, RANKS = 1"; `:87` "WEDGE/GEOM BIAS: N/A (Cartesian planar 2-D, not an axisymmetric wedge; N-AV9 does not apply)". The attempt-1 lines §1 cites, `cases/ansys_verification/VMFL064/PREREGISTRATION.md:4,41-44,66 @ 8c7e1854`, agree: `:4` "laminar, Re_D = 200"; `:41` "z is 1 empty cell (2-D)"; `:43-44` "Solver `simpleFoam` (steady incompressible laminar, SIMPLEC `consistent yes`)"; `:66` "Cartesian planar 2-D, not an axisymmetric wedge". The §1 row "VMFL064 / -R2" therefore stands as written; this section adds the R2 prereg citation beside it. **Heat-transfer cell: —** (none; isothermal momentum solve, no temperature gate — the file's convention for "none").

**Row #30 in the §2 format (appended here, not inserted above):**

| # | case | class (cfd cell / heat cell) | register verdict | what the record says (lab value → reference; triple) | record path @ sha; grading artifact |
|---|---|---|---|---|---|
| 30 | VMFL064-R2 | 2D·steady·incompressible | **`GATE REACHED`** (not a credential; ceiling frozen on prereg line 4) | `LR/s` = 4.853056 at L3 (49 152 cells) vs **experimental** Armaly et al. (1983) 5.0 — 2.9389 %, band 10 %; **CONVERGING** 4.714416 / 4.800738 / 4.853056, `p_obs` 0.7224 (below formal 2, above floor 0.05), **GCI_fine 2.0733 %** — the same order as the deviation. Re-registration of row #29: reader changed from FIRST to LAST wall-shear crossing in a window `0 < x ≤ 0.05 m`; corner vortex present at L3 only, confirming #29's diagnosis; L1/L2 values unchanged. 5.3 core-min. | `cases/ansys_verification/VMFL064-R2/RESULTS.md` @ `87afd1d6`; `verification/runs/ansys_verification/VMFL064-R2/GRADING_VMFL064_R2.json` (at HEAD `8c7e1854`) |

### C2.3 Census recomputed at HEAD `8c7e1854` from the Verdict column

Method: `git show HEAD:verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` piped to a small python that takes every line beginning `|`, splits it on **unescaped** pipes only (`re.split(r'(?<!\\)\|', …)` — the Case cell of rows #7 and #21 contains `\|`, and a naive `split('|')` mis-columns exactly those two rows), keeps lines whose first cell is a bare integer (`**n**`), and reads the FIRST backticked fixed-vocabulary token (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`) in the 4th cell, the `Verdict` column named at `:22`. Row #7's cell reads `PASS` first with `GATE REACHED` as an inline tier, so it counts as `PASS` — the same reading §2 made.

Per row (#, register line, case → token): #1 `:24` VMFL001 → NOT A RESULT · #2 `:25` VMFL001-R2 → PASS · #3 `:26` VMFL005 → PASS · #4 `:27` VMFL051 → NOT A RESULT · #5 `:28` VMFL045 run 1 → NOT A RESULT · #6 `:29` VMFL003 → NOT A RESULT · #7 `:30` VMFL045-R2 → PASS · #8 `:32` VMFL007 run 1 → NOT A RESULT · #9 `:34` VMFL003-M2 arm A → NOT A RESULT · #10 `:36` arm B → NOT A RESULT · #11 `:37` arm C → NOT A RESULT · #12 `:38` arm D → NOT A RESULT · #13 `:39` VMFL019 → PASS · #14 `:40` VMFL010 → NOT A RESULT · #15 `:41` VMFL050 → PASS · #16 `:42` VMFL059 → NOT A RESULT · #17 `:43` VMFL022 → NOT A RESULT · #18 `:44` VMFL021 attempt 1 → NOT A RESULT · #19 `:45` VMFL017 → PENDING · #20 `:433` VMFL036 → GATE REACHED · #21 `:460` VMFL033 → NOT A RESULT · #22 `:461` VMFL023 → GATE REACHED · #23 `:462` VMFL021-R2 → GATE REACHED · #24 `:463` VMFL002 → GATE REACHED · #25 `:464` VMFL004 → NOT A RESULT · #26 `:465` VMFL011 → NOT A RESULT · #27 `:466` VMFL076 → NOT A RESULT · #28 `:467` VMFL004-R2 → PASS · #29 `:468` VMFL064 → NOT A RESULT · #30 `:513` VMFL064-R2 → GATE REACHED.

**Totals at HEAD `8c7e1854`: 30 numbered rows, 30 entries, no row number missing or duplicated. `PASS` 6** (#2, #3, #7, #13, #15, #28) · **`GATE REACHED` 5** (#20, #22, #23, #24, #30) · **`NOT A RESULT` 18** (#1, #4, #5, #6, #8–#12, #14, #16, #17, #18, #21, #25, #26, #27, #29) · **`PENDING` 1** (#19) · `GATE FAIL` 0 · `BLOCKED` 0; sum 30. **This matches the supervisor's expectation (30: 6 / 5 / 18 / 1) exactly**, and it matches the register's own re-derived count in its struck-headline paragraph at `:47 @ 8c7e1854` ("30 rows … `PASS` 6 … `GATE REACHED` 5 … `NOT A RESULT` 18 … `PENDING` 1 … Credential count: 6 PASS of 30 run"). Relative to the §2 census at `eadbe157`: one row added, `GATE REACHED` 4 → 5, every other class unchanged; the breakdown of the 18 `NOT A RESULT` (refusals 7, cap-fired 2, crash/divergence 2, uncertifiable 1, rule 5 on a clean solve 6) is unchanged because row #30 is not in that class. **Credentials remain 6; row #30 adds none.**

### C2.4 The `2D · steady · incompressible` cell in §3, re-read

Old line (§3, struck here, not edited above):

~~| **2D · steady · incompressible** | #2 `PASS`, #28 `PASS`, #1/#14/#25/#26/#29 `NOT A RESULT` | **CAN DO — 2 cases**; strongest **VMFL001-R2** (`cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196`): exact-solution check at four radii, p = 2.0102, GCI 0.056 %, extrapolate on exact to 3.7 ppm — the lab's nearest row to HOLDS (coverage §3.8f). Checked: error vs exact + GCI + order. Caveat: exact-solution references only (V, never P); VMFL064's experimental reattachment is unread (refusal). |~~

New line:

| cell | rows | reading in Sanaa's words |
|---|---|---|
| **2D · steady · incompressible** | #2 `PASS`, #28 `PASS`, **#30 `GATE REACHED`**, #1/#14/#25/#26/#29 `NOT A RESULT` | **CAN DO — 2 cases**; strongest **VMFL001-R2** (`cases/ansys_verification/VMFL001/R2/RESULTS.md` @ `5e789196`): exact-solution check at four radii, p = 2.0102, GCI 0.056 %, extrapolate on exact to 3.7 ppm — the lab's nearest row to HOLDS (coverage §3.8f). Checked: error vs exact + GCI + order. **New beside it, row #30 VMFL064-R2 (`cases/ansys_verification/VMFL064-R2/RESULTS.md` @ `87afd1d6`): the first experiment-referenced row in this cell to reach its gate — the P channel — `LR/s` 4.853 vs Armaly et al. (1983) 5.0, 2.94 % of a 10 % band, CONVERGING, GCI 2.07 %; still `GATE REACHED`, not `PASS`, because the tier ceiling was frozen at `GATE REACHED` on prereg line 4 before compute (this team's product is reproducing the Ansys manual, and Sanaa's ruling caps that tier) and the comparator hard-codes that string and cannot print `PASS` or `HOLDS` (RESULTS `:25-30`). Not a credential; P is reached, not banked.** Caveat: the two `PASS` rows are exact-solution references only (V); the one P-channel row is capped by ruling, and its GCI (2.07 %) is the same order as its deviation (2.94 %), so the reattachment length is not pinned to three digits (RESULTS `:61-64`). VMFL064 attempt 1 (#29) stays a refusal on record. |

**Structural note (§3), updated for row #30 — the old sentence is otherwise unchanged:** "every `PASS` row is an `AN` (analytic) reference — P is green in no ansys row" is **still true at HEAD `8c7e1854`** (the six `PASS` rows are unchanged). The list of experiment-referenced rows now reads: **VMFL064 (#29 refused; #30 R2 `GATE REACHED`, experimental Armaly 1983, in band on a CONVERGING triple, ceiling-capped)**, VMFL023 (correlation, `GATE REACHED`), VMFL021/022 (Nurick, `GATE REACHED` / `NOT A RESULT`), VMFL017 (`PENDING`). Row #30 is the first experiment-referenced ansys row in the 2D·steady·incompressible cell to reach its gate; per the register `:513` it "CAN buy P, and this row still does not, because the ceiling was lowered in advance."

### C2.5 Footer extension — the planted control on the shas this section adds

New commit shas cited in this section: `87afd1d6` (row #30 + RESULTS + C-141), `3e7c792c` (R2 prereg freeze), `b847b97f` (this file's own commit), `8c7e1854` (HEAD at write time). `eadbe157` was already in the footer list. Run from the repository root, same form as the footer:

```
for s in 87afd1d6 3e7c792c b847b97f 8c7e1854; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: `87afd1d6 ok` · `3e7c792c ok` · `b847b97f ok` · `8c7e1854 ok` — 4 ok, 0 MISSING. The original 26-sha loop re-run at the same time: 26 ok, 0 MISSING. **Distinct commit shas cited by this file: 26 + 4 = 30.** The three blob ids cited above (`abe17c3b`, `e04fdf93`, `c17ee2e2`) are blobs, not commits, and are deliberately outside the `^{commit}` loop; `git cat-file -t` on each reads `blob` (3 of 3). A `MISSING` line is a defect in this file, not in the record.

---

## Correction 3 — 2026-08-26, ansys-verification lane `ansys-lane-opus`: register rows #31 and #32 mapped; row #30 CONFIRMED already mapped by Correction 2; census recomputed at HEAD `c7aea761`

**Lines whose number changed above this section: 0.**

Appended by the `ansys-verification` team's Opus lane on the supervisor's dispatch. Zero compute
beyond the two gradings this section records. Everything below was read with
`git show <sha>:<path>`; neither the worktree nor the shared index was used (L-333: the worktree
copies of these ledgers have repeatedly been behind HEAD, and one of them — `docs/COST_CALIBRATION.md`
— was measured stale by exactly one row during this lane's own work).

**The dispatch asked for row #30 to be mapped here. It is already mapped, and I am not mapping it
twice.** Correction 2 above maps row #30 (VMFL064-R2, `GATE REACHED`, `87afd1d6`, backward-facing
step, `2D · steady · incompressible`) in §C2.1/§C2.2, and I re-read that entry against the register
row at HEAD `c7aea761` and against `cases/ansys_verification/VMFL064-R2/RESULTS.md`: **it is
correct and complete — verdict token, `LR/s` = 4.853056, 2.9389 % of a 10 % band, `CONVERGING`
4.714416 / 4.800738 / 4.853056, `p_obs` 0.722431, `GCI_fine` 2.0733 %, prereg `3e7c792c`, comparator
blob `e04fdf93`, 5.3 core-min, C-141 — all match.** A duplicate entry would put two rows numbered 30
in this file and would be a defect, so this section maps **#31 and #32 only** and records the check
instead.

### C3.1 Rows #31 and #32 in the §2 format (appended here, not inserted above)

| # | case | class (cfd cell / heat cell) | register verdict | what the record says (lab value → reference; triple) | record path @ sha; grading artifact |
|---|---|---|---|---|---|
| 31 | VMFL011-R2 | 2D·steady·incompressible (laminar) | **`NOT A RESULT`** | **Comparator refusal (exit 2) on the planted-zero control for `u_min_norm`**, verbatim: `planted -0.1234 into …/L1/postProcessing/bisector/20000/bisect_U.xy, reader moved by only 0.` **No value, no triple, no `p_obs`, no GCI** — the refusal preceded every channel read, so nothing is quoted against the digitised Jyotsna & Vanka (1995) `u_min/U_wall` = −0.318062 (band: `rms_vs_benchmark` ≤ 0.030 at L3). Re-registration of row #26: the **L-340 plant SIZING repair worked and is measured on the real attempt-1 bytes** (sized plant delta 1.185698e-01 > threshold 3.221137e-02, inside the derived bounds [8.052843e-02, 1.610569e-01]; the parent pair still refuses at 3.677091e-07 < 1.234000e-04). **The refusal came from the OTHER channel — a SECOND, DISTINCT L-340 failure mode: plant LOCATION, not plant MAGNITUDE.** `_perturb` plants into the FIRST data row of the bisector, which on the real profile is the collapsed-hex apex at y = −4 m where `u ≡ 0`, so −0.1234 sits above `min(u) = −0.528988913215` and a `min()` reader cannot move. It was never caught at the freeze because both comparators build channels in the same dict order (rms first) and attempt 1 exited 2 inside the first entry — **the `u_min` plant had never once run on real VMFL011 bytes.** Strict completion (rule 4) HOLDS at all three levels (rc = 0, one `End`, last `Time` 20000 == `endTime`, `U`/`p` present, `ExecutionTime` count 20000, age guard): **the instrument refused; the solver did not fail.** 9.0833 core-min vs 8.3 predicted, ratio 1.094. | `cases/ansys_verification/VMFL011-R2/RESULTS.md` @ `77096fe8`; `verification/runs/ansys_verification/VMFL011-R2/GRADING.txt` (**at HEAD** `c7aea761`; no grading JSON exists — the comparator exited before writing one); prereg `9f9d6925`, prereg blob `a8c9b6f3…`, comparator blob `45aa4613…`; calibration **C-144** |
| 32 | VMFL017-R2 | **2D·unsteady·transonic (turbulent)** — see §C3.2, this CORRECTS §1's cell for the R2 | **`NOT A RESULT`** | **Registered per-level cap fired (`rc = 124` after 18 000 wall s = 300.0 core-min), launcher stopped without launching L2 or L3, and the frozen comparator REFUSED (exit 2) on strict completion**, verbatim: `REFUSE (VMFL017-R2): no End line in solver log: …/VMFL017/R2/L1`. **No `Cd`, no `Cl`, no plateau window, no triple, no GCI** — L1 reached **1.778 %** of its registered `endTime`, so nothing is quoted against AGARD AR-138 `Cd` = 0.0168 / `Cl` = 0.803 (bands 10 % and 5 %). **A MEASURED INSTRUMENT LIMIT, NOT A FAILED SOLVE, and predicted by name before compute** (PRE-COMPUTE AMENDMENT 2 §E at `45328f8a`). **What it buys is a cost measurement, and all three of §E's pre-compute figures held:** physical time reached 8.89114e-04 s vs projected ~9.0e-04 s (**0.988**); 27.04 steps/wall-s (486 748 steps in 17 999 s) vs projected ~27.7 (**0.976**); **16 871 core-min for L1 ALONE to reach `endTime`** vs projected ~16 700 (**1.010**) — **about 56× L1's own cap**. Realised Δt at the stop 1.852520264e-09 s. **Contention falsified as the cause, measured:** `ExecutionTime` 17 761.7 s vs `ClockTime` 17 999 s = **98.68 % CPU-bound**. Cites row #19 (attempt 1, `PENDING`), which is unchanged. 300.0 core-min vs 300.0 registered, ratio 1.000 — **a cap, not a forecast, and not banked as a calibration win.** | `cases/ansys_verification/VMFL017/R2/RESULTS.md` @ `fd975fcf`; `verification/runs/ansys_verification/VMFL017/R2/GRADING.txt` (**at HEAD** `c7aea761`; no grading JSON, no `COST.txt` — the launcher stopped on the cap before writing one; `L1/log.rhoCentralFoam` is 504 MB and stays on disk only); prereg `45328f8a`, prereg blob `9a58eed3…`, comparator blob `97c556f4…`, mesh birth certificate `2a7e82c2…`; calibration **C-149** |

### C3.2 Their classes, and one correction to §1

**Row #31 — `2D · steady · incompressible (laminar)`; heat cell: —.** Unchanged from §1's VMFL011
line and confirmed from the R2 pre-registration `cases/ansys_verification/VMFL011-R2/PREREGISTRATION.md
@ 9f9d6925` (= HEAD blob `a8c9b6f3…`): line 1 "Solver = simpleFoam (OpenFOAM v2606), steady
incompressible laminar SIMPLEC, Re = U_wall*base/nu = 2*2/0.01 = 400, 2-D"; line 8 "SERIAL, RANKS = 1";
line 11 "N/A (planar 2-D Cartesian, not an axisymmetric wedge)".

**Row #32 — `2D · unsteady · transonic (turbulent)`; heat cell: —. THIS CORRECTS §1's VMFL017 cell for
the R2, and the correction is a solver change, not a re-reading.** §1 maps VMFL017 as
"`rhoSimpleFoam` + kOmegaSST, **steady**, 2-D C-mesh, transonic" — which is right for **attempt 1
(register row #19, `PENDING`)** and wrong for the R2. The supervisor's ladder ruling switched the
instrument to **`rhoCentralFoam`, which is explicit and TRANSIENT**:
`cases/ansys_verification/VMFL017/R2/PREREGISTRATION.md @ 45328f8a` line 1 "Solver = rhoCentralFoam
(OpenFOAM v2606), kOmegaSST RAS, hePsiThermo/perfectGas, **TRANSIENT explicit** (adjustTimeStep,
maxCo), shock-capturing. 2D C-mesh"; line 8 "TRANSIENT; endTime a **physical settling time** (not
iterations), adjustTimeStep, maxCo"; line 11 "N/A (2D Cartesian C-mesh, planar in z, empty
frontAndBack — not axisymmetric)". **The time axis of the cell therefore moves from `steady` to
`unsteady` for row #32 while row #19 keeps `steady`** — the same manual case occupying two different
grid cells because the lab ran it on two different instruments. **Nothing above is edited**; §1's
line stands as written and is corrected here by appending, which is what this file's own convention
requires.

**Consequence for §3's grid reading, stated and NOT applied above.** The `2D · unsteady · transonic`
cell is now **occupied and empty-handed**: one row, `NOT A RESULT`, no value. That is a genuine
capability statement — **the lab has attempted transonic RAE 2822 twice, on two different solvers,
and has produced no number either time** — and it should not be read as "CAN DO". The
`2D · steady · incompressible` cell gains row #31 as a further `NOT A RESULT` and its "CAN DO — 2
cases" reading (from §C2.4) is **unchanged**, because #31 adds no credential and removes none.

### C3.3 Census recomputed at HEAD `c7aea761` from the Verdict column

Same method as §C2.3 — `git show HEAD:verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`
split on **unescaped** pipes only (`re.split(r'(?<!\\)\|', …)`, because the Case cells of rows #7 and
#21 contain `\|` and a naive `split('|')` mis-columns exactly those two), keeping lines whose first
cell is a bare `**n**`, and reading the first backticked fixed-vocabulary token.

**Totals at HEAD `c7aea761`: 32 numbered rows, 32 entries, no row number missing or duplicated.**
**`PASS` 6** (#2, #3, #7, #13, #15, #28) · **`GATE REACHED` 5** (#20, #22, #23, #24, #30) ·
**`NOT A RESULT` 20** (#1, #4, #5, #6, #8–#12, #14, #16, #17, #18, #21, #25, #26, #27, #29, **#31**,
**#32**) · **`PENDING` 1** (#19) · `GATE FAIL` 0 · `BLOCKED` 0; sum **32**. Row #31 is register line
`:549`, row #32 is `:574`.

**The credential count does NOT move: 6 `PASS` of 32 run.** Both new rows are `NOT A RESULT`. The
register's own headline still reads "6 PASS of 30 run" and is **deliberately not struck** — the
standing instruction strikes it only when the `PASS` count changes — so its **denominator is two
behind by design**, recorded in the register's own dated notes for rows #31 and #32 and repeated
here so a reader of this file alone is not misled.

**The reading these two rows share, and it is worth the space.** Neither is a solver failure. Row
#31's instrument refused because a control had never been exercised on real bytes; row #32's
instrument ran flawlessly for five hours and simply cannot afford the physics at the registered
`endTime`. **Two different ways to spend compute and buy no number — one a grading defect, one an
honest cost measurement — and the point of this file is that neither of them reads as a capability.**

### C3.4 Footer extension — the planted control on the shas this section adds

New commit shas cited in this section: `77096fe8` (row #31 + RESULTS + C-144), `fd975fcf` (row #32 +
RESULTS + C-149), `9f9d6925` (VMFL011-R2 prereg freeze), `45328f8a` (VMFL017-R2 prereg freeze),
`db2c7f9a` (the run records landed at HEAD for the rows that cited them). `3e7c792c` and `87afd1d6`
were already in §C2.5's list. Run from the repository root, same form as the footer:

```
for s in 77096fe8 fd975fcf 9f9d6925 45328f8a db2c7f9a; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: 77096fe8 ok · fd975fcf ok · 9f9d6925 ok · 45328f8a ok · db2c7f9a ok  — 5 ok, 0 MISSING. **Distinct commit shas cited by
this file: 26 + 4 + 5 = 35.**

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
| cfd | yes | 3 | 6 | 4 | 23 | 0 |
| heat-transfer | yes | 0 | 5 | 5 | 26 | 0 |
| dafoam | yes | 4 | 5 | 1 | 62 | 0 |

(Counts are per verdict cell: dafoam has two verdict columns per class, so its row sums to 72.)

---

## Footer — merged planted control: every distinct sha cited by every source, resolved

Run from the repository root; every line must read `ok`; 160 distinct shas across all sources:

```
for s in 0686c7b2 068c2bf0 08aa454c 0cbaea26 0d2dc150 0dfd9c64 0f56460d 11e6a187 122f6da3 14018d5b 15767999 1697ea49 16b81323 17209b50 1799861d 193b522c 2793f23e 288a5862 28a770a5 299296a2 2a93ff27 2aea29d9 2b50394a 2d639d3b 2dcea996 2e83a89b 2f1d6cb7 3053d9ec 311feb37 31fd2268 336a364d 33dbe337 35171866 3574cdcb 3663520c 3b9bcf31 3c21d87c 3c39d08d 3ccb0c81 3d28328c 3e7c792c 3f87e759 3f8c6b13 3fafc67ac7132fbe27951e81164ad565ae71ad31 4228f216 45328f8a 49c95cc7 4ad083fb 4b336fad 4bb0f6a1 4d9d902b 4e6ba646 4eae12f4 52a213ad 548fc02e 5889677b 5a870e54 5adb9c5d 5c3fe5a8 5d1718df 5d1f89cd 5e789196 60cfd4c8 61b47973 63c8d044 64b02355 64b367ef 65684e7c 65882eb3 66f42398 6753e912 6a0a1a99 6a0d7f45d5bc19a3fa06fffac4a20c2a3ecbf82c 6a9afa0a 6a9b8c41 6b8d6355 6becf266 6d149d51 6fcfe713 71388f4e 7422591b 77096fe8 7b2a12f0 7e2fc497 825b1259 8273e4ad 8590c96a 85e2230f 878f1556 87afd1d6 8974eb75 8b407ea2 8c7e1854 8f5bf878 8fc2bdeb 959a31b1 994daa49905f7826d8dc5bb47f28e574c8588f70 9c241fe2 9c86962e 9f9d6925 a1ac1c21 a1fbe127 a74b2f61 a86357e6 aba61e53 b10260a0 b26b875c b2a13fd6 b698dfc3 b70b49c6 b840fcd5 b845b603 b847b97f b8b5e2bf b8fe7eea ba023a53 bb5088c4 be35dcad bff31cff c487e3c7 c4f72b27 c557f847 c5d96403 c69ce11c c83d9501 ca6a3164 ca9aad86 cadb4887 cb5b6eb8 cccf7a9f cffd90e7 d3b7e38b d4308dde d846815c d98868fb d9fa4161 da65ae38 db2c7f9a db76091e dc2b4f74 ddb99eca e6580910 e6d53dbd eadbe157 ebb7da5a f018c8bf f279aac5 f2943b0b f3fad674 f4332fe3 f4e5c350 f5a81a69 f5f67de7 f63d347e f746233a f8916f36 f8d2d60c f9a59d47 fcf31542 fd975fcf; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

That loop is the reader's own control and peels every token to a commit, so it honestly prints `MISSING` for the 2 non-commit token(s) classified below with `git cat-file -t`.

Reading at assembly time (2026-08-27T16:38Z, HEAD `8506d55c`): **157 ok, 1 MISSING, 2 non-commit tokens, 160 distinct shas.** MISSING lines, each with the source that cites it — a token that does not resolve HERE is not automatically a lost commit: read the citing file, which may disclose it as a sha in a DIFFERENT repository, and this control deliberately never launders such a token into `ok`: `d3b7e38b` (cited by `docs/capability/dafoam_GRID.md`) Non-commit tokens: `dc2b4f74` (blob), `f4e5c350` (blob) — disclosed by the citing family file as not a commit sha.
