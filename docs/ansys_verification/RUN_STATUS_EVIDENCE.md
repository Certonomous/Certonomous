# ANSYS VM2026R1 Case Inventory and Run Status — Haiku Lane Report

**Date:** 2026-08-25  
**Supervisor:** ansys-verification-supervisor  
**Lane:** ansys-lane-haiku  
**Source:** `git show HEAD:docs/ansys_verification/CASE_MAP.md` (commit eb0feb8b17db07e5dfdd2336b7241ee2c6964f63)  
**Artifact paths:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/`, `/home/ubuntu/Certonomous/verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`

---

## TABLE 1: Lab Solver Column (per case)

The OpenFOAM v2606 application or solver status for each case, exactly as listed in CASE_MAP column "Lab solver (OpenFOAM v2606)".

### Cases WITH a concrete lab solver

| Case | Lab Solver |
|---|---|
| VMFL001 | simpleFoam / icoFoam (rotatingWallVelocity) |
| VMFL002 | simpleFoam + energy / buoyantSimpleFoam |
| VMFL003 | simpleFoam (kEpsilon) |
| VMFL004 | pimpleFoam/simpleFoam (cyclic + pressureGradient) |
| VMFL005 | icoFoam / simpleFoam |
| VMFL006 | reactingFoam (inert) / scalarTransportFoam |
| VMFL007 | nonNewtonianIcoFoam (powerLaw) |
| VMFL008 | SRFSimpleFoam |
| VMFL009 | buoyantSimpleFoam / buoyantBoussinesqSimpleFoam |
| VMFL010 | simpleFoam / icoFoam |
| VMFL011 | icoFoam / simpleFoam |
| VMFL012 | simpleFoam/pimpleFoam (kEpsilon) |
| VMFL013 | rhoSimpleFoam / simpleFoam + energy |
| VMFL014 | reactingFoam (inert) / simpleFoam+scalarTransport |
| VMFL015 | simpleFoam (kEpsilon) |
| VMFL016 | simpleFoam (RSM: LRR/SSG) |
| VMFL017 | rhoSimpleFoam (SST) |
| VMFL018 | sonicFoam / rhoCentralFoam |
| VMFL019 | pimpleFoam / icoFoam (transient) |
| VMFL020 | rhoPimpleFoam (dynamicMesh) |
| VMFL023 | pimpleFoam / icoFoam |
| VMFL024 | interFoam (SRF/MRF) |
| VMFL025 | reactingFoam (hard — combustion model) |
| VMFL026 | sonicFoam/rhoCentralFoam (perfect-gas; real-gas EOS BLOCKED) |
| VMFL027 | simpleFoam (realizableKE) |
| VMFL028 | rhoSimpleFoam / simpleFoam + energy |
| VMFL029 | laplacianFoam (isotropic only; anisotropic tensor DT not native → custom) |
| VMFL030 | simpleFoam (RNGkEpsilon) |
| VMFL031 | simpleFoam / pimpleFoam |
| VMFL032 | simpleFoam (kOmegaSST) |
| VMFL033 | rhoSimpleFoam / chtMultiRegion (viscous dissipation) |
| VMFL035 | rhoSimpleFoam (MRF) |
| VMFL036 | simpleFoam (axisym) |
| VMFL037 | simpleFoam (kOmegaSST) |
| VMFL038 | interFoam |
| VMFL039 | reactingTwoPhaseEulerFoam (wall boiling, hard) |
| VMFL040 | simpleFoam (kOmegaSST) |
| VMFL041 | rhoSimpleFoam (SST) |
| VMFL042 | simpleFoam + energy / buoyantSimpleFoam |
| VMFL043 | simpleFoam (kOmegaSSTLM transition) |
| VMFL044 | rhoSimpleFoam / sonicFoam |
| VMFL045 | rhoCentralFoam / sonicFoam |
| VMFL046 | rhoCentralFoam / sonicFoam |
| VMFL047 | simpleFoam (kOmega) |
| VMFL048 | simpleFoam (kOmegaSST) |
| VMFL049 | reactingFoam (EDM, hard) |
| VMFL050 | laplacianFoam |
| VMFL051 | rhoCentralFoam / sonicFoam |
| VMFL052 | buoyantBoussinesqSimpleFoam / buoyantSimpleFoam |
| VMFL053 | rhoSimpleFoam (RNGkEpsilon) |
| VMFL054 | icoFoam / simpleFoam |
| VMFL055 | simpleFoam (kkLOmega) |
| VMFL056 | chtMultiRegionSimpleFoam + fvDOM |
| VMFL057 | chtMultiRegion + fvDOM |
| VMFL058 | simpleFoam (kOmegaSST) |
| VMFL059 | chtMultiRegionSimpleFoam / laplacianFoam |
| VMFL060 | rhoSimpleFoam / sonicFoam (transition SST) |
| VMFL061 | chtMultiRegion + viewFactor (S2S) radiation |
| VMFL062 | simpleFoam (low-Re kEpsilon) |
| VMFL063 | icoFoam / simpleFoam |
| VMFL064 | icoFoam / simpleFoam |
| VMFL065 | simpleFoam (RSM) |
| VMFL066 | fireFoam / chtMultiRegion + fvDOM |
| VMFL067 | reactingTwoPhaseEulerFoam (boiling, hard) |
| VMFL068 | simpleFoam (RSM) |
| VMFL069 | interFoam (or viscosity-stratified simpleFoam) |
| VMFL070 | chtMultiRegion + fvDOM / viewFactor |
| VMFL071 | rhoSimpleFoam (cascade) |
| VMFL073 | simpleFoam (kOmegaSST) |
| VMFL075 | rhoCentralFoam / sonicFoam |
| VMFL076 | simpleFoam + energy / rhoSimpleFoam |
| VMFL077 | interFoam |
| VMFL078 | icoFoam / simpleFoam |
| VMFLGPU001 | simpleFoam / icoFoam |
| VMFLGPU002 | simpleFoam / icoFoam |
| VMFLGPU003 | icoFoam / simpleFoam |
| VMFLGPU004 | laplacianFoam (anisotropic → custom) |
| VMFLGPU005 | buoyantBoussinesqSimpleFoam |
| VMFLGPU006 | rhoSimpleFoam (cascade) |
| VMFLGPU007 | rhoSimpleFoam / simpleFoam + energy |
| VMFLGPU008 | chtMultiRegion + fvDOM |
| VMFLGPU009 | interFoam |
| VMFLGPU010 | chtMultiRegion + viewFactor (S2S) |
| VMFRT006 | rhoPimpleFoam (dynamicMesh) — feasible |

**Total: 83 cases with a concrete solver**

### Cases WITH NO lab solver (BLOCKED or NONE)

| Case | Lab Solver Status |
|---|---|
| VMFL021 | **BLOCKED** — no cavitation solver (interPhaseChangeFoam absent) |
| VMFL022 | **BLOCKED** — no cavitation solver |
| VMFL026 | sonicFoam/rhoCentralFoam (perfect-gas; **real-gas EOS BLOCKED**) |
| VMFL034 | reactingMultiphaseEulerFoam (PBM, hard) / **NONE (native PBM limited)** |
| VMFL072 | **NONE** — no Eulerian wall-film solver on box |
| VMFL074 | reactingParcelFoam / **NONE (native PBM limited)** |
| VMFRT001 | **NONE** — no LES engine-combustion solver |
| VMFRT002 | reactingParcelFoam (spray, no reaction) — partial / **NONE** |
| VMFRT003 | reactingParcelFoam — partial / **NONE** |
| VMFRT004 | reactingParcelFoam — partial / **NONE** |
| VMFRT005 | sprayFoam / reactingParcelFoam (hard) / **NONE** |
| VMFRT007 | **NONE** — no engine-combustion solver |

**Total: 12 cases with NO lab solver**

---

## TABLE 2: Cost Column (per case)

The cost band assigned to each case (order-of-magnitude for single grid level).

| Cost Band | Count | Cases |
|---|---|---|
| **trivial** (< 5 core-min) | 21 | VMFL001, VMFL002, VMFL003, VMFL004, VMFL005, VMFL007, VMFL010, VMFL019, VMFL029, VMFL033, VMFL045, VMFL050, VMFL051, VMFL059, VMFL061, VMFL070, VMFL076, VMFLGPU001, VMFLGPU002, VMFLGPU004, VMFLGPU010 |
| **small** (< 60 core-min) | 51 | VMFL006, VMFL008, VMFL009, VMFL011, VMFL012, VMFL013, VMFL014, VMFL017, VMFL018, VMFL020, VMFL023, VMFL024, VMFL027, VMFL028, VMFL031, VMFL032, VMFL036, VMFL037, VMFL038, VMFL040, VMFL041, VMFL042, VMFL043, VMFL044, VMFL046, VMFL047, VMFL052, VMFL053, VMFL054, VMFL055, VMFL056, VMFL057, VMFL058, VMFL060, VMFL062, VMFL063, VMFL064, VMFL065, VMFL066, VMFL069, VMFL071, VMFL072, VMFL073, VMFL075, VMFLGPU003, VMFLGPU005, VMFLGPU006, VMFLGPU007, VMFLGPU008, VMFLGPU009, VMFRT006 |
| **medium** (< 600 core-min) | 11 | VMFL025, VMFL026, VMFL030, VMFL034, VMFL039, VMFL048, VMFL049, VMFL067, VMFL068, VMFL074, VMFL078 |
| **large** (≥ 600 core-min) | 10 | VMFL015, VMFL016, VMFL035, VMFL077, VMFRT001, VMFRT002, VMFRT003, VMFRT004, VMFRT005, VMFRT007 |
| **—** (no cost / not applicable) | 2 | VMFL021, VMFL022 |

---

## TABLE 3: Ladder Column (per case)

Whether a Roache 3-level grid-refined triple is feasible for that case.

| Ladder Value | Count | Cases |
|---|---|---|
| **Y** (feasible, clean monotone) | 14 | VMFL001, VMFL002, VMFL005, VMFL007, VMFL010, VMFL036, VMFL045, VMFL051, VMFL059, VMFL063, VMFL064, VMFL078, VMFLGPU001, VMFLGPU002 |
| **Y*** (feasible, with caveat) | 68 | VMFL003, VMFL004, VMFL006, VMFL008, VMFL009, VMFL011, VMFL012, VMFL013, VMFL014, VMFL015, VMFL016, VMFL017, VMFL018, VMFL019, VMFL020, VMFL023, VMFL024, VMFL025, VMFL026, VMFL027, VMFL028, VMFL029, VMFL030, VMFL031, VMFL032, VMFL033, VMFL035, VMFL037, VMFL038, VMFL040, VMFL041, VMFL042, VMFL043, VMFL044, VMFL046, VMFL047, VMFL048, VMFL049, VMFL050, VMFL052, VMFL053, VMFL054, VMFL055, VMFL056, VMFL057, VMFL058, VMFL060, VMFL061, VMFL062, VMFL065, VMFL066, VMFL068, VMFL069, VMFL070, VMFL071, VMFL073, VMFL075, VMFL076, VMFL077, VMFLGPU003, VMFLGPU004, VMFLGPU005, VMFLGPU006, VMFLGPU007, VMFLGPU008, VMFLGPU009, VMFLGPU010, VMFRT006 |
| **N** (not feasible, no solver or architecture blocker) | 8 | VMFL021, VMFL022, VMFL034, VMFL072, VMFL074, VMFRT001, VMFRT005, VMFRT007 |
| **N*** (not feasible, soft blocker — physics hard or partial) | 5 | VMFL039, VMFL067, VMFRT002, VMFRT003, VMFRT004 |

---

## TABLE 4: Dimension (Dim) — count per value

| Dimension | Count | Cases |
|---|---|---|
| **2** (2D) | 54 | VMFL001, VMFL004, VMFL009, VMFL010, VMFL011, VMFL012, VMFL013, VMFL017, VMFL018, VMFL019, VMFL020, VMFL023, VMFL027, VMFL029, VMFL031, VMFL033, VMFL037, VMFL038, VMFL040, VMFL041, VMFL042, VMFL043, VMFL045, VMFL046, VMFL047, VMFL050, VMFL052, VMFL053, VMFL054, VMFL055, VMFL056, VMFL057, VMFL059, VMFL060, VMFL061, VMFL062, VMFL063, VMFL064, VMFL065, VMFL066, VMFL070, VMFL071, VMFL075, VMFL076, VMFLGPU001, VMFLGPU002, VMFLGPU003, VMFLGPU004, VMFLGPU005, VMFLGPU006, VMFLGPU007, VMFLGPU008, VMFLGPU010 |
| **A** (2D axisymmetric) | 22 | VMFL002, VMFL003, VMFL005, VMFL006, VMFL007, VMFL008, VMFL014, VMFL021, VMFL022, VMFL024, VMFL025, VMFL028, VMFL032, VMFL036, VMFL040, VMFL044, VMFL049, VMFL058, VMFL067, VMFL073, VMFLGPU009, VMFLGPU010 |
| **3** (3D) | 19 | VMFL015, VMFL016, VMFL026, VMFL030, VMFL035, VMFL048, VMFL068, VMFL069, VMFL072, VMFL077, VMFL078, VMFLGPU009, VMFRT001, VMFRT002, VMFRT003, VMFRT004, VMFRT005, VMFRT006, VMFRT007 |

---

## TABLE 5: What the lab has actually run

### Tracked case directories in git
**Location:** `/home/ubuntu/Certonomous/cases/ansys_verification/`  
**Result:** 0 case directories tracked (archives live at canonical home `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`)

### Run directories on disk
**Location:** `/home/ubuntu/Certonomous/verification/runs/ansys_verification/`  
**Found:** 3 run directories

| Case ID | Status |
|---|---|
| VMFL001 | Run directory present (includes R2 re-run) |
| VMFL005 | Run directory present |
| VMFL051 | Run directory present |

**Total: 3 runs on disk**

### ANSYS Validation Register rows
**Location:** `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` (at HEAD commit eb0feb8b17db07e5dfdd2336b7241ee2c6964f63)  
**Table rows found:** 3 rows (plus dated correction appended 2026-08-25)

| Row # | Case | Date (UTC) | Verdict |
|---|---|---|---|
| 1 | VMFL001 | 2026-08-24 | NOT A RESULT (comparator refusal + L3 not converged) |
| 2 | VMFL001-R2 | 2026-08-24 | **PASS** |
| 3 | VMFL005 | 2026-08-24 | **PASS** |

**Credential count:** 2 PASS of 3 run (row #1 is NOT A RESULT; rows #2 and #3 are PASS)

**Register status:** Append-only; row #3 carries a dated correction (2026-08-25) correcting a docket citation from D510 to D512. No rows were edited; the correction is appended per CLAUDE.md rule 6.

---

## TABLE 6: Regime Keywords (case-insensitive count across all 95 rows)

| Keyword Category | Count | Breakdown |
|---|---|---|
| Compressible / Supersonic / Shock | 13 | VMFL013, VMFL017, VMFL018, VMFL026, VMFL035, VMFL041, VMFL044, VMFL045, VMFL046, VMFL051, VMFL053, VMFL060, VMFL075 |
| Turbulent | 30 | VMFL003, VMFL012, VMFL013, VMFL014, VMFL015, VMFL016, VMFL017, VMFL018, VMFL021, VMFL022, VMFL025, VMFL027, VMFL028, VMFL030, VMFL031, VMFL032, VMFL034, VMFL035, VMFL037, VMFL047, VMFL048, VMFL049, VMFL052, VMFL058, VMFL062, VMFL065, VMFL068, VMFL073, VMFL074, VMFL077 |
| Heat / Thermal / Conjugate | 10 | VMFL002, VMFL009, VMFL013, VMFL028, VMFL029, VMFL033, VMFL050, VMFL059, VMFL067, VMFL070 |
| Multiphase / Cavitation | 7 | VMFL021, VMFL022, VMFL024, VMFL034, VMFL039, VMFL067, VMFL074 |
| Laminar | 18 | VMFL001, VMFL002, VMFL004, VMFL005, VMFL006, VMFL007, VMFL008, VMFL009, VMFL010, VMFL011, VMFL023, VMFL036, VMFL038, VMFL063, VMFL064, VMFL069, VMFL076, VMFL078 |

**Note:** Cases can appear in multiple categories. No assumption of exclusivity was made.

---

## Summary of inventory extraction

- **Total cases in CASE_MAP:** 95 (VMFL 78 + VMFLGPU 10 + VMFRT 7)
- **Cases with concrete lab solver:** 83
- **Cases with NO lab solver:** 12
- **Run directories observed on disk:** 3 (VMFL001, VMFL005, VMFL051)
- **Credentials (PASS rows in register):** 2
- **Register findings (NOT A RESULT):** 1

All data extracted from CASE_MAP.md at HEAD commit `eb0feb8b17db07e5dfdd2336b7241ee2c6964f63` on 2026-08-25.

