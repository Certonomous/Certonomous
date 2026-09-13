# DrivAer — PUBLISHED VALUE vs OUR VALUE, every parameter the sources publish

**Built for Sanaa, whose instruction is the reason this document exists:
*"i dont want any discrepancy that way we can ensure to reproduce these results."***

**Status: COMPARISON AND PROPOSALS. NOTHING IS CHANGED BY THIS DOCUMENT.**
`DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md` was **FROZEN 2026-09-13**
by the cfd supervisor. Under standing rule 2 its gates, thresholds, cap and
labels are closed; they move only as dated addenda that cannot alter them. §4
below therefore **proposes**; the supervisor and Sanaa dispose.

Sources, both title-page verified (rule 15), ingests beside this file:

| Col | Source | **SOLVER** | Mesher | Ingest |
|---|---|---|---|---|
| **A** | Ashton, West, Lardeau & Revell (2016), *Computers & Fluids* **128**:1-15 — the source Sanaa named | **STAR-CCM+ v9.04** *(NOT OpenFOAM: `OpenFOAM` 0, `snappy` 0, `STAR-CCM+` 13)* | STAR-CCM+ | `PUBLISHED_SETUP_INGEST_ashton_2016.md` |
| **B** | Ashton et al. (2024/25), **arXiv:2408.11969v2**, DrivAerML | **OpenFOAM v2212** *(custom Upstream CFD `pimpleFoam`)* | **ANSA 24.1.0 HeXtreme** | `PUBLISHED_SETUP_INGEST_drivaerml_2024.md` |
| **C** | Certonomous **R5**, frozen 2026-09-13 | **OpenFOAM v2606, `simpleFoam`** | **snappyHexMesh** | `verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md` |

**Column A's values are STAR-CCM+ settings. They are real published values and
they belong here, but they are not OpenFOAM settings and must never be copied
into a dictionary as if they were.** Column B is the OpenFOAM source and is our
matching configuration.

---

## 0. READ THESE THREE CAVEATS BEFORE TAKING ANY VALUE FROM THIS TABLE

1. **The DrivAerML dataset's shipped `run_0` dictionaries are a MESH-DELIVERY
   STUB. NO VALUE MAY BE READ OUT OF THEM.** They contain `application
   UserSolver`, `deltaT 1`, `ddtSchemes steadyState`, `momentumTransport model
   laminar; turbulence off`, `forceCoeffs patches ( )` empty, and `magUInf 40`
   with `lRef 1` — **contradicting the paper's own 38.889 m/s and 2.78618 m**.
   There is no `0/nut` at all. Their sha256s are recorded in the DrivAerML
   ingest §5 **precisely so that nobody reads `deltaT 1` out of a file whose
   hash sits in a lab document and takes it for the recipe.** Every column-B
   value below comes from the paper's pages, cited by sidecar line.
2. **"A grid refinement study is not undertaken."** Their words
   (arXiv sidecar L279-280). **Column B carries NO grid-convergence evidence,
   ever, and must never be cited as if it did.**
3. **Their own solve is ~20 drag counts high on Ford's experiment**: case 2a CFD
   Cd **0.274** vs measured **0.255**; case 2b **0.267** vs **0.242**; and the
   configuration delta only half right (−0.007 vs −0.013). **Reproducing them
   verbatim reproduces that error too.** Stated here so Sanaa sees it now rather
   than discovering it in a grading record.

---

## 1. THE TABLE

Key: **MATCH** = same value. **REASONED** = differs, reason registered.
**UNREGISTERED** = differs, no reason on record → §4 proposal.
**NOT PUBLISHED** = the source does not publish it; not quietly filled.

### 1.1 Case, configuration, conditions

| Parameter | **A — Ashton 2016 (STAR-CCM+)** | **B — DrivAerML (OpenFOAM)** | **C — OURS (R5)** | Status |
|---|---|---|---|---|
| Configuration | **Estate and Fastback** | **Notchback** | **Notchback** | **MATCH with B**; A is a different body |
| Underbody | **smooth** | detailed (Ford OCDA) | **detailed** (`OCDADetailedUnderbody`) | **MATCH with B** |
| Scale | **40 %** | **1:1 full** | **1:1 full** | **MATCH with B** |
| Freestream U∞ | **40 m/s** | **38.889 m/s** (L225) | **38.889 m/s** (`0/U`) | **MATCH with B — identical** |
| Reference Re | **Re_H 1.48e6** | **Re_L 7.19e6** on wheelbase 2.786 m (L225-227) | Re_L ≈ 7.2e6; Re_H 3.66e6 | **MATCH with B**; **A is 2.47× off in Re_H** |
| Kinematic viscosity ν | NOT PUBLISHED | **1.51163e-05** (dataset `transportProperties`) | **1.507e-05** | **REASONED** — 0.3 %, immaterial; see §4 P6 |
| ρ∞ for coefficients | NOT PUBLISHED | **1 kg/m³** (L2849) | **`rhoInf 1`** | **MATCH** |
| A_ref | NOT PUBLISHED | **2.17 m²** (case-independent), 2.172 case | **2.298 m²** (run_466 varying-ref) | **REASONED** — we grade run_466, not case 2a |
| l_ref | NOT PUBLISHED | **2.78618 m** wheelbase | **2.79 m** | **MATCH** (run_466 basis) |
| Moment centre | NOT PUBLISHED | **(1.40009, 0, −0.3176)** | **(1.402, 0, −0.3176)** | **MATCH** (run_466 basis) |

### 1.2 Domain and boundaries

| Parameter | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS** | Status |
|---|---|---|---|---|
| Domain type | closed tunnel box | **"large open road"** (L230) | large open road box | **MATCH with B** |
| Inlet distance | **4 L upstream** | NOT PUBLISHED as a distance | 12.0 m ≈ **2.6 L** upstream of x_BL | **NOT PUBLISHED in B** |
| Outlet distance | **6 L downstream** | NOT PUBLISHED | 37.66 m from origin | **NOT PUBLISHED in B** |
| Top / lateral BC | slip, top at **8 H**, width **11 W** | **symmetry**, lateral and top (L233) | **`slip`** on `top`, `sideMinus`, `sidePlus` | **REASONED** — slip ≡ symmetry for a plane boundary |
| **Ground-BL start x_BL** | n/a | **x_BL = −2.339 m ≈ −0.84 L**, 2.346 m upstream of the front axle (L232-233) | **block split at x = −2.339 m**, `floorSlip` upstream / `floorNoSlip` downstream | **MATCH — EXACT, to the millimetre** |
| Wheels | **non-rotating** | NOT PUBLISHED in the prose | stationary (`noSlip`) | **MATCH with A** |
| **Blockage ratio** | NOT PUBLISHED | **≈ 0.25 %** (L234) | **0.96 %** (2.298 / (20 × 12)) | 🔴 **UNREGISTERED — 3.8× theirs. §4 P5** |

### 1.3 Mesh and layers — the rows Sanaa named

| Parameter | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS (R5 registered)** | Status |
|---|---|---|---|---|
| Mesh tool | STAR-CCM+ | **ANSA 24.1.0 HeXtreme** | **snappyHexMesh** (v2606) | **REASONED** — no published snappy recipe exists for this case; see §3 |
| Cell type | polyhedral+prism (RANS), hex+prism (DES) | **hexa-dominant & polyhedral** | castellated hex + prism | comparable |
| **Cell count** | 18 / 37 / 80 M (RANS), 80 / 100 M (DES) | **≈ 160 M** (L270) | **15–20 M** (gate M1) | **REASONED** — §4 P4; **8–10× below B** |
| **Layers** | **20** | **7** (L271-272) | **8** | **REASONED** — Sanaa specified 8; source says 7 (R5 §4.2) |
| **First layer height** | NOT PUBLISHED | **0.75 mm** (L272) | **1.00 mm** | **REASONED** — 0.75 mm gives y⁺ ≈ 22, below Sanaa's 30 floor (R5 §4.1) |
| **Total stack** | NOT PUBLISHED | **12 mm** (L272) | **11.86 mm** | **MATCH** — within 1.2 % |
| **Growth ratio** | NOT PUBLISHED | **1.2 – 1.4 variable** (L272-273) | **1.11** | 🔴 **UNREGISTERED — OUTSIDE the published band. §4 P3** |
| **Sizing mode** | absolute (independent prism region) | **absolute (mm)** | **`relativeSizes false`** (absolute) | **MATCH — fixed by R5** |
| `minThickness` | NOT PUBLISHED | NOT PUBLISHED | **0.0002 m** | **NOT PUBLISHED** — converted in the same edit (R5 §2.2) |
| **Stack in local cells** | NOT PUBLISHED | **0.480** | **0.474** | **MATCH** — R5 fixes the 1.6808 defect |
| **Achieved layer coverage** | NOT PUBLISHED | **NOT PUBLISHED — ANSA writes no post-extrusion table, so there is NO counterpart to ours** | **2.50 / 5 coarse, 2.89 / 5 medium** (pre-R5, measured) | **NOT COMPARABLE — stated, not filled** |
| Refinement strategy | rear-concentrated | **size fields following geometry, extending downstream** (L275-277) | volume refinement, surface cell held at 25 mm | **MATCH with B** (R5 §4.2) |

### 1.4 Wall treatment and y⁺ — the row that reverses between sources

| Parameter | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS** | Status |
|---|---|---|---|---|
| Wall treatment | **wall-RESOLVED**, no wall functions | **wall FUNCTIONS**, deliberately high-y⁺, chosen over wall-resolved on 2nd AutoCFD evidence "only a minor difference" (L273-275) | **wall functions** | **MATCH with B. A is the opposite choice.** |
| Wall function | n/a | **Spalding's law, valid at arbitrary y⁺** (L1384-1386) | **`nutUSpaldingWallFunction`** | **MATCH — the same function** |
| **y⁺ achieved** | **< 1** on all five meshes | **NOT PUBLISHED.** *(lab-derived ≈ 22 by scaling from our measured 153.1 — DERIVED, NOT A PUBLISHED VALUE)* | **predicted ≈ 30**; gate Y1 = 30–100. Pre-R5 measured: median **153.1**, 0 of 47 patches < 30 | **REASONED** vs B's derived ≈22; see §4 P2 |

### 1.5 Turbulence, numerics, schemes

| Parameter | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS** | Status |
|---|---|---|---|---|
| Approach | RANS **and** DDES | **HRLES** — Fuchs/Mockett DDES variant | **steady RANS** | 🔴 **REASONED but see §4 P1 — the largest discrepancy in this table** |
| RANS closure | **k-ω SST** (+ SA, RKE, B-EVM, EB-RSM) | **Spalart-Allmaras** near-wall | **k-ω SST** | **MATCH with A**, differs from B |
| LES branch | — | **σ-model (Nicoud)** + **ZDES "enhanced protection"** shielding | none | **REASONED** — no LES branch in a steady arm |
| Solver | steady **coupled**; unsteady segregated (DES) | **custom `pimpleFoam`** derivative, transient SIMPLE, enhanced Rhie-Chow | **`simpleFoam`** (segregated SIMPLE) | **REASONED** — P1 |
| Momentum convection | 2nd-order upwind (RANS); **hybrid CDS/2nd-upwind** (DES) | **Travin hybrid blending**: 2nd-order central in resolved turbulence, 2nd-order upwind elsewhere | **`bounded Gauss linearUpwind grad(U)`** | **REASONED** — a steady arm has no resolved-turbulence region to blend into |
| Turbulence convection | 2nd-order upwind | 2nd-order upwind-biased on ν̃ | **`bounded Gauss limitedLinear 1`** on k, ω | comparable |
| Gradient / Laplacian | NOT PUBLISHED | NOT PUBLISHED | `cellLimited Gauss linear 1` / `Gauss linear corrected` | **NOT PUBLISHED** |
| Time integration | **2nd-order Crank-Nicolson** (DES) | **2nd-order implicit Euler** (L1383-1384) | **`steadyState`** | **REASONED** — P1 |
| Precision | NOT PUBLISHED | **double** (L328) | to confirm at stage time | **§4 P7** |

### 1.6 Time step, averaging window, convergence — Sanaa's named rows

| Parameter | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS** | Status |
|---|---|---|---|---|
| Steady / transient | RANS steady; **DDES transient** | **transient** | **STEADY** | 🔴 **P1** |
| **Time step** | **Δt U/L = 1e-3** (5e-5 s) | **Δt = 2e-4 s** *(DERIVED from "two times finer… 1e-4", L2125 — an inference, not a published figure)* | **n/a — iteration index, not time** | 🔴 **P1** |
| Inner iterations | **5** per step | "multiple sub-iterations", **NOT PUBLISHED** as a number | n/a | **NOT PUBLISHED in B** |
| Initialisation | **from converged steady RANS** | NOT PUBLISHED | freestream / continuation | **REASONED** — our steady solves are `GATE FAIL`, so we do not have A's starting condition |
| **Transient bridged before averaging** | **10 convective flow units** | **DETECTED** by Meancalc from the Cd/Cl/Cs traces, min 25 CTU | **iterations 1–2000, FIXED BY SCHEDULE** | 🔴 **REASONED — P1** |
| **Averaging window** | **20 further convective units** (30 total = 26,000 steps) | **DETECTED**: run until 95 % CI on Cd ≤ **±1.5 drag counts**; hard bracket **40–60 CTU**; < 5 % hit it. Validation: 3.0 s ≈ 42 CTU, 3.6 s ≈ 50 CTU | **iterations 2001–3000, exactly 1,000 samples, FIXED BY SCHEDULE** | 🔴 **REASONED — R5 §6: "a detected window lets the run choose its own from the trace", the defect pre-registration exists to prevent** |
| Convergence criterion | sd(Cd,Cl) < 2e-5 over 400 samples **and** residuals < 1e-5; 2000–5000 iters | statistical: ±1.5 drag counts | endTime 3000, rule-4 completion | **REASONED** |

### 1.7 Results the sources publish

| Quantity | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS** |
|---|---|---|---|
| Cd, CFD vs experiment | SST RANS fastback **0.260** vs **0.261**; SST-IDDES fine **0.2615** | case 2a **0.274** vs **0.255** (**+20 counts**); 2b **0.267** vs **0.242** | reference **0.2758368** (DrivAerML run_466); gate C2 ±10 % → **[0.24825, 0.30342]** |
| Cl, CFD vs experiment | SST RANS fastback **0.124** vs **0.01** (error 0.114); SST-IDDES **0.024** vs 0.01 | 2a **0.033** vs **0.087** | run_466 Cl **−0.0536** |
| Grid convergence | mesh convergence claimed on the fine mesh | **NOT UNDERTAKEN (their words)** | no grid gate registered for R5 |

### 1.8 Cost

| Parameter | **A (STAR-CCM+)** | **B (OpenFOAM)** | **C — OURS** |
|---|---|---|---|
| Hardware | 2.6 GHz Sandy Bridge, 704 cores | **AWS hpc6a.48xlarge**, AMD Milan, **1536 cores** | c7a, 96 cores |
| Wall time | 50 h (DES) | **≈ 40 h** | — |
| **Core-hours** | **35,200** | **61,440** | R5 measured basis **6,936 core-min ≈ 116 core-h** |
| **Core-minutes** | 2,112,000 | **3,686,400** | **6,936** |
| On our 96 cores | 15.3 days | **26.7 DAYS per run** | ~1.2 h |

---

## 2. THE HEADLINE DISCREPANCY, STATED PLAINLY FOR SANAA

**Both published sources run TRANSIENT scale-resolving simulations and
time-average them. R5 is a STEADY RANS solve whose "averaging" is a mean over
iterations 2001–3000.**

R5 says so itself, honestly, in its §6: *"A time-average of a steady SIMPLE
iteration sequence is **not** a time-average of an unsteady flow — the iteration
index is not time. It reduces the arbitrariness of quoting the last sample of a
wandering series. It does not make a non-converged steady solve converged."*

**So R5 does not discharge Sanaa's "run transient and time-average" instruction,
and it does not claim to.** It is the wall-function and layer-fix arm — it fixes
the `relativeSizes` defect, the stack thickness and the y⁺ target, which are
prerequisites for a transient run being worth launching. **But if the goal is
"reproduce these results", R5 cannot reach them, because the published results
are time-averages of a resolved turbulent wake and R5 has no resolved wake.**

This is the one discrepancy on the table that **cannot be closed by editing a
dictionary.** It needs a registered transient successor arm. §4 P1.

---

## 3. WHY NO SNAPPYHEXMESH ROW CAN EVER BE "MATCHED" FROM A PAPER

Three public cases, three published setups, **none in snappyHexMesh**:
STAR-CCM+ (A), ANSA HeXtreme (B), and block-structured for PPTC. **No published
source will warn this lab about a snappy relative-thickness defect, because none
of them has a relative thickness to get wrong.** That is why the lab-side rule
exists: `docs/standards/MESH_STANDARD_SECTION_11_DRAFT.md`. The rows in §1.3
marked NOT PUBLISHED for `minThickness` and coverage are **structurally**
unpublishable, not merely missing.

---

## 4. PROPOSALS — every differing row gets a change or a reason. NOTHING APPLIED.

R5 is frozen. Each item below is either **already reasoned in R5** (no action) or
a candidate for a **dated addendum that cannot alter a gate**, or a question for
Sanaa. Numbered for the supervisor to accept or decline one by one.

| # | Row | Proposal | Who decides |
|---|---|---|---|
| **P1** | **Steady vs transient** | **Register a transient successor arm** (R6) using B's recipe: custom-free `pimpleFoam`, Δt 2e-4 s, detected window at ±1.5 drag counts, 40–60 CTU bracket. **And tell Sanaa plainly that R5 does not discharge her transient instruction.** Do NOT re-open R5. | **Sanaa** — it is her instruction and her cost |
| **P2** | **y⁺ 30 floor vs published ≈22** | **Surface the conflict to Sanaa.** Her window's floor of 30 and the published recipe (0.75 mm → y⁺ ≈ 22) are **incompatible**. The published setup deliberately runs *below* her floor. Either the floor moves to ~20 or we knowingly diverge from the source. **R5's Y1 gate stays as frozen either way.** | **Sanaa** — R5 §7: "The window is Sanaa's and this lane does not move it" |
| **P3** | **Growth ratio 1.11 vs published 1.2–1.4** | 🔴 **NEW, UNREGISTERED.** R5 quotes the 1.2–1.4 band at its line 53 and registers **1.11** at line 187 **without flagging that 1.11 is outside it**. Propose a **disclosure addendum** (no gate moves). **Arithmetic, computed here:** at the 12.0 mm ceiling and a 1.003 mm first layer, r = **1.112** at 8 layers, **1.175** at 7, and **1.274** at 6. **Only 6 layers lands inside the published band.** So Sanaa's 8-layer instruction and the published growth band are jointly unsatisfiable at y⁺ 30. | supervisor (disclosure); **Sanaa** if layers change |
| **P4** | **15–20 M vs 160 M cells** | No change; **already reasoned** as a cost choice. Propose only that the certificate **state the 8–10× ratio explicitly**, so no reader infers mesh equivalence. | supervisor |
| **P5** | **Blockage 0.96 % vs 0.25 %** | 🔴 **NEW, UNREGISTERED.** Our domain cross-section gives **3.8× their blockage**. Their 0.25 % is called "negligible"; ours is not obviously so. Propose a **disclosure addendum**, and a blockage-sensitivity check as a successor item — **not** a change to R5's frozen domain. | supervisor |
| **P6** | **ν 1.507e-05 vs 1.51163e-05** | 0.3 %, immaterial to Cd. Propose **adopt B's value at the next mesh build** for exactness, and disclose meanwhile. | supervisor |
| **P7** | **Precision** | B ran **double**. Propose R5's stage-time check **record** which precision our build uses, so the row stops being blank. | supervisor |
| **P8** | Layers 8 vs 7 | **Already reasoned** in R5 §4.2 (Sanaa's instruction, divergence registered not split). No action — but see P3: 8 is what forces r outside the band. | — |
| **P9** | First layer 1.00 vs 0.75 mm | **Already reasoned** in R5 §4.1 (set from Sanaa's y⁺ window, not the source). No action — but see P2. | — |

### 4.1 What I did NOT propose, and why

- **No change to any R5 gate, threshold, cap or label.** R5 is frozen; rule 2
  closes them. Every item above is a disclosure, a successor, or a question.
- **No adoption of column A's values into any dictionary.** They are STAR-CCM+
  settings for a different body at 2.47× different Reynolds.
- **No value taken from the DrivAerML shipped dictionaries** (§0 caveat 1).
- **No invented number for B's achieved coverage or B's y⁺.** Both are marked
  NOT PUBLISHED; the ≈22 is labelled lab-derived wherever it appears.

---

*Compiled by a cfd lab-lane, 2026-09-13, from the two committed ingests beside
this file and the frozen R5 registration. No solver launched. No frozen file
edited. `grade_drivaer.py` untouched, sha256 6106cf6d…83c26d7. Nothing left the
box.*
