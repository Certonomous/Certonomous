# PUBLISHED OPENFOAM SETUP vs WHAT THE LAB IS DOING — ALL FOUR CASES

**Built for Sanaa, 2026-09-13, in answer to her instruction, verbatim as relayed to this lane:**

> *"i want to know for each case and see comparison for each case of what the lab is doing vs the
> published openfoam recipe. We need to be extra sure that each time is using the publicly
> available openfoam setup files when they exist, or the publicly available openfoam recipe."*

**Team:** cfd. **Lane:** `lab-lane` under `cfd-supervisor`. **Nothing is changed by this document.**
No frozen file is edited, no gate, threshold, cap or label is altered, no solver is launched, and
nothing left the box (CLAUDE.md rules 7, 8). Where a row argues for a change, the change is a
**proposal to the supervisor**, who rules.

**Every table has exactly five columns:** `parameter | published value + SOURCE LINE | our value |
same? | deviation reason (registered)`.

**Verdict words in the `same?` column, and only these:** `SAME` · `DIFFERENT` · **`NOT PUBLISHED`**
(the source publishes nothing for that parameter) · `NOT COMPARABLE` (the two setups have no common
counterpart) · `NOT RETRIEVED` (a source exists but is not on this box).

**`NOT PUBLISHED` is a true and important answer, not a gap to be filled.** No published value
anywhere below is invented. Where this lane could not source a number, the cell says so.

---

## 0. 🔴 THE HEADLINE, AND IT IS THE ARGUMENT FOR SANAA'S OWN INSTRUCTION

### 0.1 Papers publish what a mesher produced. They never publish what it was asked for.

**Measured by this lane tonight**, by token count over the nine title-page-verified text sidecars
on disk that any of the four cases relies on:

| token | occurrences across all nine papers |
|---|---|
| `relativeSizes` | **0** |
| `nSurfaceLayers` | **0** |
| `expansionRatio` | **0** |
| `finalLayerThickness` | **0** |
| `minThickness` | **0** |
| `featureAngle` | **0** |

The nine files swept, each counted individually:
`docs/papers/propeller_rotating_machinery/{sikirica_2019_jmse_7_374_grid_type_turbulence_model_propeller,
cheng_2024_omae2024_125991_pptc_les_snappyhexmesh, klerebrant_klasson_huuva_2011_smp11_pptc_openfoam,
gaggero_villa_brizzolara_2011_smp11_pptc_unigenova_openfoam,
sva_2011_smp11_questionnaire_on_viscous_flow_methods}.txt`;
`docs/papers/benchmark_test_cases/{ashton_2016_rans_des_realistic_automotive_models,
groves_1989_dtrc_shd1298_darpa_suboff_geometry,
huang_1989_dtrc_shd1298_02_darpa_suboff_experiments}.txt`;
`/home/ubuntu/certonomous-runs/reference_pdfs/benchmark_test_cases/ashton_2024_drivaerml.txt`.

**Zero is zero even in the one genuine OpenFOAM + snappyHexMesh paper.** Cheng 2024 uses
snappyHexMesh (`snappy` appears twice, `OpenFOAM` four times) and still prints not one dictionary
keyword. **Papers report the mesh that came out — cell counts, achieved y⁺, refinement ratios — and
never the dictionary that asked for it.** That is the whole reason the tables below carry so many
`NOT PUBLISHED` cells, and it is a gap in the literature, not in this lab's extraction.

### 0.2 Case files publish all six. That is why Sanaa's instruction is the right one.

**The same six tokens, counted by this lane in the case trees a sibling lane retrieved tonight:**

| case file (sha256 given in the tables below) | relSizes | nSurfLayers | expRatio | finalLayerT | minThick | featAngle |
|---|---|---|---|---|---|---|
| Wolf Dynamics `drivaer_fine/system/snappyHexMeshDict` | **1** | **4** | **5** | **5** | **5** | **1** |
| Wolf Dynamics `drivaer_coarse/system/snappyHexMeshDict` | **1** | **4** | **5** | **5** | **5** | **1** |
| Alletto `OneraM6Wing/system/snappyHexMeshDict` | **3** | **1** | **1** | **1** | **2** | **1** |

**Nine papers: zero. Three case files: every keyword, with its value.** This is the measured form of
Sanaa's instruction — *use the publicly available setup files when they exist* — and tonight is the
first night this lab has had any of them on disk.

### 0.3 What is now on disk, what is not, and who put it there

**Retrieved tonight by a sibling cfd lane and committed as an in-repo POINTER at
`799c88e78dfc79518359778fa5c2681c20652308`** (`docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`).
The trees themselves are 4.1 GB and live **outside** the repo at
`/home/ubuntu/upstream/published-openfoam-setups/`, with **per-file sha256 manifests beside them**:
`SHA256SUMS.openfoam-hpc-tc.txt` (229 files), `SHA256SUMS.wolfdynamics-drivaer.txt` (101),
`SHA256SUMS.alletto-m6.txt` (35). **This lane verified the pointer commit and the three manifests
exist**; the retrieval itself is that lane's work and is attributed, not re-run.

| tree | provenance | bears on |
|---|---|---|
| `openfoam-hpc-tc/` | OpenFOAM HPC Benchmark Suite (HPC Technical Committee), git clone, **commit `84c26243`, 2025-05-28**; dictionaries declare **v2412 / v2206**. Contains `incompressible/simpleFoam/**occDrivAerStaticMesh**` and `incompressible/pimpleFoam/LES/**occDrivAerRotMesh**` | **DrivAer** |
| `wolfdynamics-drivaer/` | Wolf Dynamics DrivAer tutorial, `drivaer_coarse` + `drivaer_fine` + slides. **The only complete self-contained tree: its own STL geometry ships**, so a run from it would carry **no geometry deviation at all** | **DrivAer** |
| `alletto-openfoamtutorials/` | `gitlab.com/mAlletto/openfoamtutorials`, **commit `e72b42c5`, 2024-01-31**, v2006. Contains `OneraM6Wing` | **ONERA M6** — information only |

🔴 **SUBOFF: NOT RETRIEVED, and the attempt is on record.** The sibling lane searched, swept the
whole HPC-TC tree, and **the identified Type 209 paper returns HTTP 403**. **Nothing was substituted
and no dictionary was reconstructed.** §4 says so in every row it would have filled.

🔴 **THE CORRECTION THAT SANAA'S PREMISE RESTS ON: `occDrivAerStaticMesh` — the published case that
matches our geometry, velocity and viscosity exactly — SHIPS NO `snappyHexMeshDict`, AND NO MESHER
DICTIONARY OF ANY KIND.** Verified independently by this lane: `find … -iname '*napp*'` over that
case returns **0 files**. Its README distributes the 65 / 110 / 236 M meshes **pre-built from
Zenodo**, and **those tarballs are not on this box**. **Its solver dictionaries are public; its mesh
dictionary is not.**

**Consequently: every mesher row in §1 attributed to the occDrivAer family comes from the SIBLING
`occDrivAerRotMesh` case and is labelled `[OCCR]` — AN INFERENCE.** It is the same geometry and the
same authors, but **it is not proof that those values produced the static case's 65 / 110 / 236 M
meshes.** Marked as an inference in every cell where it appears, never as the static case's recipe.

### 0.4 🔴 THE LAYER STACK IN LOCAL CELLS — THE ROW NO PAPER COULD EVER SUPPLY

**This is the single most useful number in the whole document, and it exists only because case files
were retrieved.** It is `stack ÷ local surface cell` — the quantity that decides whether
snappyHexMesh extrudes a layer stack or collapses it, and the quantity that **cannot be computed
from any paper**, because the papers publish neither `finalLayerThickness` nor `expansionRatio`.

| case | `nSurfaceLayers` | `expansionRatio` | `finalLayerThickness` | **stack, local cells** |
|---|---|---|---|---|
| Wolf Dynamics DrivAer **coarse** | 3 | 1.2 | 0.3 | **0.758** |
| ESI marine propeller | — | — | — | **0.794** ‡ |
| **`occDrivAerRotMesh`** | 2 | 1.2 | 0.5 | **0.917** |
| Wolf Dynamics DrivAer **fine** | 6 | 1.2 | 0.3 | **1.197** |
| ONERA M6 Alletto | 5 | 1.5 | 0.5 | **1.302** |
| high-lift CRM, ONERA | — | — | — | **1.600** ‡ |
| — | — | — | — | — |
| 🔴 **OURS — DrivAer R2/R5 predecessor, COLLAPSED** | 5 | 1.25 | 0.5 | 🔴 **1.6808** |
| ✅ **OURS — DrivAer R5, absolute sizing, PREDICTED TO EXTRUDE** | 8 | 1.11 | (absolute, 1.0 mm first) | ✅ **0.474** |

‡ *These two rows are the sibling lane's measurement (commit `799c88e7`) and **this lane did not
re-derive them**; attributed, not adopted.* **The other four this lane recomputed from the shipped
dictionaries and reproduces to three decimal places** — 0.3+0.25+0.2083 = 0.758; 0.5+0.4167 = 0.917;
0.3+0.25+0.2083+0.1736+0.1447+0.1206 = 1.197; 0.5+0.3333+0.2222+0.1481+0.0988 = 1.302.

🔴 **EVERY PUBLISHED STACK LIES BETWEEN OUR TWO MEASURED POINTS.** Ours at **0.480** extrudes; ours
at **1.6808** collapses; the six published values cluster at **0.76 – 1.60**, and **our collapsing
1.6808 sits just above the highest published value.** That is the mechanism of the DrivAer and PPTC
layer failures, located between two brackets that no paper could have drawn.

**And it reframes R5's own choice honestly:** R5's registered **0.474** is **below every published
stack** — it is a deliberately conservative ask, not a matched one. It buys extrusion at the cost of
a thinner boundary-layer stack than anybody else runs.

### 0.5 🔴 `relativeSizes true` IS NOT WRONG. IT IS WRONG ON OUR TOPOLOGY.

**Measured across the retrieved trees by the sibling lane (commit `799c88e7`), spot-checked by this
lane on the three dictionaries it read directly:** four retrieved cases set `relativeSizes true`, two
set `false` — **and all six mesh a body inside a UNIFORM CARTESIAN BACKGROUND BLOCK.**

🔴 **No retrieved case uses `relativeSizes true` on a non-uniform background.**

**This is the missing half of the PPTC 95.53× finding.** On a uniform Cartesian background every
level-0 cell is a cube, the global minimum level-0 edge *is* the base cell, and
`hexRef8::getLevel0EdgeLength()` returns exactly what the author intended — so relative sizing is
safe, and four published authors use it. **On our PPTC 72° wedge the global minimum level-0 edge is
the azimuthal chord of a 2 mm numerical rod, `2·0.002·sin(π/60) = 2.09343825e-04 m` against an
intended base of `0.020 m`.** Same keyword, same value, **95.53× different meaning.**

**So the honest statement is not "the published setups got `relativeSizes` right and we got it
wrong."** It is: **relative sizing is correct on the topology everyone else uses and catastrophic on
ours** — and **published propeller practice is `relativeSizes false` together with the full-360°
Cartesian box. The two travel together.** Adopting one without the other is the error.


---

## A. 🔴 ROTATION RATE AND VELOCITY SCALE — READ THIS BEFORE ANY PUBLISHED NUMBER BELOW

**A published coefficient measured at a different rotation rate or a different velocity scale is a
different experiment. It cannot band our act, however close the number looks.**

### A.1 PPTC — three published rotation rates, none of them ours

| source | rotation rate `n` | citation |
|---|---|---|
| Sikirica et al. 2019 | **10 s⁻¹** | pp. 7, 10 |
| Cheng et al. 2024 | **25 s⁻¹** | Table 1, p. 4 |
| Klerebrant Klasson & Huuva 2011 | **NOT STATED** for the open-water case in the text read | — |
| **Certonomous (ours)** | **15 s⁻¹** | SVA test 11F0395 |

🔴 **NO PUBLISHED K_T, K_Q OR η FROM ANY OF THESE PAPERS MAY BE USED AS A BAND FOR OUR ACT.** SVA
Report 3752's own **n = 10 and n = 15 curves cross near J ≈ 1.3** — Sanaa registered that crossing
in §B.4 as the measured Reynolds effect. A number taken from Sikirica at n = 10 and compared with
our n = 15 result is a comparison between two different experiments, and it will look like agreement
or disagreement for reasons that have nothing to do with our mesh.

**Published PPTC coefficients below are cross-checks on direction and magnitude only.** Our band
remains the smp'11 participant scatter (§B.4), unchanged by anything in this document.

### A.2 DrivAer — the velocity scale, and one exact match

| source | U∞ | ν | Re |
|---|---|---|---|
| occDrivAer (HPC-TC case file) | **38.889 m/s** (`system/include/caseDefinition`) | **1.507e-05** (same file) | **7.1899e6** on wheelbase 2.78618 m (README) |
| DrivAerML (paper) | **38.889 m/s** (sidecar L225) | **1.51163e-05** (dataset `transportProperties`) | **7.19e6** (L225-227) |
| Wolf Dynamics (case file) | **30 m/s** (`0_org/U`) | **1.5881327800829875e-05** (`constant/transportProperties`) | not stated in the case |
| Ashton 2016 (paper) | **40 m/s**, **40 % scale** model | NOT PUBLISHED | Re_H **1.48e6** |
| **Certonomous R5** | **38.889 m/s** | **1.507e-05** | Re_L ≈ 7.2e6 |

**Our ν of 1.507e-05 is character-for-character the occDrivAer case file's value.** The DrivAer table
previously carried this row as a 0.3 % deviation from the DrivAerML paper needing a reason; against
the **case file** it is an exact match and needs none.

**Wolf Dynamics runs a different experiment from all the others: 30 m/s, a different fluid viscosity,
the original TUM DrivAer rather than the Ford OCDA, and a HALF model** (`blockMeshDict` `ymin 0` with
a symmetry plane). Its dictionary values are usable as *snappyHexMesh practice*; its **results are
not a comparand for ours.**

### A.3 ONERA M6 and SUBOFF — velocity scale, for the information-only tables

| case | published | ours |
|---|---|---|
| M6, Alletto | **U = (290, 0, 15.5) m/s**, T 298 K, p 1e5 Pa → incidence **3.06°**, \|U\| 290.41 m/s | **U = (291.022155821, 0, 15.5574365217)**, T 300 K, p 101325 Pa → incidence **3.0600°**, \|U\| 291.44 m/s |
| SUBOFF | **NOT PUBLISHED in the lab's holdings.** The Groves report is a *geometry* report; `SUBOFF_A1_PREREGISTRATION.md` §2.2 records that searching it for `Reynolds`, `knots`, `ft/sec` returns one hit, about a Reynolds *stress* station | **Re_L = 1.2e7**, registered in that same section as **the lab's own inherited working condition, not a source value** |

**The two M6 incidences agree to four decimal places at 3.06°. The speeds differ by 0.35 %.**
The thermodynamic states differ (298/1e5 vs 300/101325), so the Mach numbers differ slightly;
**this lane did not re-derive either Mach number and does not quote one.**

---

## B. 🔴 DrivAer — STEADY vs TRANSIENT, AND WHAT TONIGHT'S RETRIEVAL CHANGES ABOUT IT

**The brief this lane was given stated that both published DrivAer sources are transient
scale-resolving and time-averaged, while our R5 is a steady RANS solve, and that the discrepancy
cannot be closed by any dictionary edit. That is correct for the two PAPER sources and this lane
confirms it. It is NOT correct for the case file retrieved tonight, and saying so is the point of
the exercise.**

| source | steady or transient | evidence |
|---|---|---|
| Ashton 2016 (paper) | RANS **steady** and DDES **transient**, time-averaged over 20 convective units | `PUBLISHED_SETUP_INGEST_ashton_2016.md` |
| DrivAerML (paper) | **TRANSIENT**, HRLES, detected averaging window to ±1.5 drag counts | sidecar L320, L1383-1384 |
| **occDrivAer (CASE FILE, HPC-TC)** | 🔴 **STEADY.** `ddtSchemes { default steadyState; }`, `application simpleFoam`, `RASModel kOmegaSST` | `system/fvSchemes`, `system/controlDict`, `constant/turbulenceProperties` — read by this lane |
| Wolf Dynamics (CASE FILE) | 🔴 **STEADY.** `ddtSchemes { default steadyState; }`, `application simpleFoam`, `RASModel kOmegaSST` | `system/fvSchemes`, `system/controlDict`, `constant/turbulenceProperties` |
| **Certonomous R5** | **STEADY**, `simpleFoam`, mean over iterations 2001-3000 | `DRIVAER_R5_..._PREREGISTRATION_DRAFT.md` §6 |

**The occDrivAer README states the reason in its own words:** *"The setup was modified to suit the
requirements of the OpenFOAM HPC Challenge (2025), by opting for a steady-state RANS simulation,
fixing the inner iterations of the SIMPLE solver, and providing pre-generated mesh files of various
resolutions that are suitable for a static simulation."*

**So the standing conclusion splits in two, and both halves matter to Sanaa:**

1. **Against the two papers, the discrepancy stands exactly as stated and is unclosable by any
   dictionary edit.** R5 has no resolved wake; DrivAerML's published Cd is a time-average of one.
   **R5 does not discharge a "run transient and time-average" instruction and does not claim to**
   (R5 §6 says so itself). A transient successor arm remains the only route to those numbers.
2. **Against the case files, our steady choice is now PUBLISHED PRACTICE on the same geometry, at
   the same velocity, at the same viscosity, in the same solver.** The occDrivAer case is the OCDA
   notchback with closed cooling and static wheels — **our configuration** — run steady in
   `simpleFoam` with `kOmegaSST`. Before tonight, "steady" was our cost compromise with no published
   counterpart. **It now has one.**

**This lane did not accept the brief's framing on relay and reports what it measured instead. The
disagreement is disclosed rather than resolved silently.**

---

## C. 🔴 THE THREE CAVEATS ON THE DrivAerML SOURCE — CARRIED FORWARD UNCHANGED

Lifted from `cases/navier_class/DRIVAER/PUBLISHED_VS_REGISTERED_PARAMETER_TABLE.md` §0
(commit `e0fbdba3`) and from `DRIVAER_R5_..._PREREGISTRATION_DRAFT.md` §2.3, both of which this lane
read directly. **Not re-measured by this lane; attributed, not adopted as its own measurement.**

1. **The shipped `run_0` dictionaries are a MESH-DELIVERY STUB and NO VALUE MAY BE READ FROM THEM.**
   They carry `application UserSolver`, `deltaT 1`, `ddtSchemes steadyState`, `momentumTransport
   model laminar; turbulence off`, an **empty** `forceCoeffs patches ( )`, and `magUInf 40` with
   `lRef 1` — **contradicting the paper's own 38.889 m/s and 2.78618 m.** There is no `0/nut` at all.
   Their sha256s are recorded in the DrivAerML ingest §5 **precisely so nobody reads `deltaT 1` out
   of a file whose hash sits in a lab document and takes it for the recipe.**
2. **"A grid refinement study is not undertaken"** — their own words, arXiv sidecar L279-280.
   **That source carries NO grid-convergence evidence, ever, and must never be cited as if it did.**
3. **Their own solve is ≈ 20 drag counts high on Ford's experiment**: case 2a CFD Cd **0.274** vs
   measured **0.255**; case 2b **0.267** vs **0.242**; and the configuration delta only half right
   (−0.007 vs −0.013). **Reproducing them verbatim reproduces that error.** Our gate C2 is anchored
   on a DrivAerML number (run_466, Cd 0.2758368), so this caveat is inside our own primary gate.

---

# 1. DrivAer

**Published sources, in the order of authority this table applies:**

- **[OCC]** `occDrivAerStaticMesh`, OpenFOAM HPC Benchmark Suite, at
  `/home/ubuntu/upstream/published-openfoam-setups/openfoam-hpc-tc/incompressible/simpleFoam/occDrivAerStaticMesh`.
  **CASE FILES.** Original setup Charles Mockett, Hendrik Hetmann, Felix Kramer (Upstream CFD GmbH)
  2022-2023; HPC-Challenge modification Mark Wasserman (Huawei) and Sergey Lesnik (Wikki GmbH) 2025.
  **Same geometry family as ours** (Ford OCDA notchback, closed cooling, static wheels — AutoCFD
  case 2a). Retrieved tonight by a sibling cfd lane; **read and hashed by this lane.**
- **[WD]** Wolf Dynamics DrivAer, OpenFOAM 9, `drivaer_coarse` / `drivaer_fine`. **CASE FILES.**
  **Different body (original TUM DrivAer), half model, 30 m/s** — see §A.2. Dictionary values are
  published snappyHexMesh practice; results are not a comparand.
- **[OCCR]** `occDrivAerRotMesh`, same repository, `occDrivAerRotMesh.orig/system/snappyHexMeshDict.full`
  (sha256 `6aa462bcf82ece196e75bb9e1e0f13cbce5c3b2f361a25f2fbcbe752866b72ac`, read and hashed by this
  lane). 🔴 **THE ONLY MESHER DICTIONARY IN THE occDrivAer FAMILY, AND IT IS NOT THE STATIC CASE'S.**
  Same geometry, same authors, **rotating-mesh LES sibling**. Every `[OCCR]` cell below is
  **AN INFERENCE about `[OCC]`, never proof** that these values produced the static case's
  65 / 110 / 236 M meshes (§0.3).
- **[ML]** DrivAerML, Ashton et al. arXiv:2408.11969v2. **PAPER ONLY** (its shipped dictionaries are
  a stub — §C.1). Lifted from `PUBLISHED_SETUP_INGEST_drivaerml_2024.md` and the R5 registration.
- **[A16]** Ashton, West, Lardeau & Revell 2016, *Computers & Fluids* 128:1-15. **PAPER, and it is
  STAR-CCM+, not OpenFOAM** (`OpenFOAM` 0, `snappy` 0, `STAR-CCM+` 13). Its values are real published
  values and **must never be copied into a dictionary as if they were OpenFOAM settings.**

🔴 **THREE CONDITIONS TRAVEL WITH EVERY `[WD]` ROW, and one of them would cost a verdict.** Recorded
by the sibling lane at commit `799c88e7`; the second was **re-verified directly by this lane**.

1. **Its OpenFOAM version is ambiguous in the files themselves.** The Wolf Dynamics page declares
   OpenFOAM 9; its `snappyHexMeshDict` and `constant/` headers say **7**. Settled by its own shipped
   log: **`Build : 9-6adb71a2e61d`**. *(Sibling lane's reading; not re-opened by this lane.)*
2. 🔴 **Its `blockMeshDict` types ALL SIX farfield patches `type wall;`** — `ffminx`, `ffmaxx`,
   `ffminy`, `ffmaxy`, `ffminz`, `ffmaxz`. **Verified by this lane by reading the file.** The flow
   condition lives entirely in `0_org/U` (`fixedValue` on `ffminx` and `ffminz`, `inletOutlet` on
   `ffmaxx`, `symmetry` on `ffminy`, `slip` on `ffmaxy`/`ffmaxz`). **The `blockMeshDict` alone would
   be read as a sealed box.** Both files must be read together before any launch from this tree.
3. 🔴 **Its own shipped coarse result is NOT STATIONARY to this lab's gate.** `Cd = 0.2912` is still
   moving **8.6e-04 per iteration at iteration 1000**. **Nobody may treat 0.291 as a converged
   reference**, and no gate may be anchored on it. *(Sibling lane's measurement; not re-derived here.)*

**Our value** throughout is Certonomous **R5**, frozen 2026-09-13, at
`verification/campaign/DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md`, with the mesh recipe
at `cases/navier_class/DRIVAER/mesh/{make_r5_dict.py,build_drivaer_level.py,write_solver_case.py}`.
**R5 is FROZEN and has had no compute. Nothing in this table amends it.**

**Rows lifted rather than re-measured** are marked **[lifted]** and attributed. Everything else in
the published column was read from the retrieved case files by this lane tonight.

### 1.1 Case, configuration and conditions

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| geometry variant | **[OCC]** Ford OCDA **notchback**, closed cooling, static wheels — README "Configuration" | OCDA notchback, detailed underbody | **SAME** | — |
| model scale | **[OCC]** full scale, `lref 2.78618` — `system/include/caseDefinition` | 1:1 full | **SAME** | — |
| U∞ | **[OCC]** `UinfMag 38.889;` — `system/include/caseDefinition` | 38.889 m/s (`0/U`) | **SAME** — identical | — |
| ν | **[OCC]** `nu 1.507e-05;` — `system/include/caseDefinition` | **1.507e-05** (`write_solver_case.py`) | **SAME** — identical | previously carried as a 0.3 % deviation from **[ML]**'s 1.51163e-05; against the case file no deviation exists |
| Re | **[OCC]** 7.1899e6 on wheelbase — README "Flow Parameters" | ≈ 7.2e6 | **SAME** | — |
| ρ for coefficients | **[OCC]** `rhoInf 1.0; rho rhoInf;` — `system/forceCoeffsAll` | `rhoInf 1` | **SAME** | — |
| l_ref | **[OCC]** `lref 2.78618;` — `system/include/caseDefinition` | **2.79** | **DIFFERENT**, 0.14 % | ours is run_466's own geometry reference (`geo_ref_466.csv`), not case 2a's. Registered: we grade run_466 |
| A_ref | **[OCC]** `Aref 2.17;` — `system/include/caseDefinition` | **2.298 m²** | **DIFFERENT**, +5.9 % | same reason — run_466 varying-reference geometry. **This row propagates directly into Cd and into the blockage row below** |
| moment centre | **[OCC]** `CofR (1.40009 0 -0.3176);` — `system/forceCoeffsAll` | (1.402, 0, −0.3176) | **SAME** to 1.1 mm in x, exact in z | — |
| wheels | **[OCC]** static — README; `Wheel.*`/`Tires.*` in `fixedWallPatches` | stationary (`noSlip`) | **SAME** | — |
| configuration **[A16]** | **[A16]** Estate and Fastback, **40 % scale**, 40 m/s, Re_H 1.48e6 **[lifted]** | notchback, full scale | **NOT COMPARABLE** | different body, different scale, Re_H 2.47× off |

### 1.2 Domain and boundaries

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| domain x extent | **[OCC]** `xMin -40; xMax 80;` — `system/blockMeshDict`. README: "spans 40m upstream and 80m downstream" | `X0 -14.339`, `X1 37.661` — `build_drivaer_level.py:29` | 🔴 **DIFFERENT** — theirs **14.36 L** upstream / **28.71 L** downstream, ours **5.15 L** / **13.52 L** | 🔴 **NO REGISTERED REASON ON RECORD.** R5 does not address domain extent. **PROPOSAL D1** |
| domain y extent | **[OCC]** `yMin -22; yMax 22;` (44 m) — `system/blockMeshDict` | `Y0 -10.0`, `Y1 10.0` (20 m) | 🔴 **DIFFERENT** — 2.2× narrower | 🔴 as above — **PROPOSAL D1** |
| domain z extent | **[OCC]** `zMin -0.3176; zMax 19.6824;` (20 m) — `system/blockMeshDict` | `Z0 -0.319`, `Z1 11.681` (12 m) | 🔴 **DIFFERENT** — 1.67× shorter; **floor heights agree to 1.4 mm** | 🔴 as above — **PROPOSAL D1** |
| **blockage ratio** | **[OCC]** derived from the case file: 2.17 / (44 × 20) = **0.2466 %**. **[ML]** publishes "≈ 0.25 %" (sidecar L234) — **the two agree, one measured from a dictionary, one from a paper** | 2.298 / (20 × 12) = **0.9575 %** | 🔴 **DIFFERENT — 3.88× theirs** | 🔴 **UNREGISTERED.** Was proposal **P5** in the DrivAer table (`e0fbdba3`) on paper evidence alone. **It is now corroborated by a case file** and this lane raises it to **PROPOSAL D1** |
| inlet BC, U | **[OCC]** `type fixedValue; value uniform $Uinf;` — `0.orig/U` | `fixedValue` at 38.889 | **SAME** | — |
| outlet BC, U | **[OCC]** `type zeroGradient;` — `0.orig/U` | `inletOutlet` | **DIFFERENT** | `inletOutlet` is the stricter guard against reverse inflow. No reason on record; **PROPOSAL D5** (disclosure only) |
| outlet BC, p | **[OCC]** `uniformFixedValue; uniformValue constant 0.0;` (`pref 0.0`) — `0.orig/p` | fixed 0 | **SAME** | — |
| lateral + top BC | **[OCC]** `freestream { type symmetry; }` on top and both sides — `system/blockMeshDict`, `0.orig/*` | `slip` on `top`, `sideMinus`, `sidePlus` | **SAME in effect** | registered in the DrivAer table: slip ≡ symmetry for a plane boundary **[lifted]** |
| ground upstream of the car | **[OCC]** `ground { type wall; }` with `slipGroundPatch ground` → **`type slip;`** in `0.orig/U` — `system/include/caseDefinition` | `floorSlip` upstream of x_BL | **SAME** | — |
| ground-BL start x_BL | **[ML]** **x_BL = −2.339 m**, 2.346 m upstream of the front axle (sidecar L232-233) **[lifted]**. **[OCC]** does not publish a split — its `ground` is slip and `ground_noSlip.*` appears in `fixedWallPatches`, but no x is given in the case | **block split at x = −2.339 m** — `build_drivaer_level.py:29` | **SAME as [ML] — exact, to the millimetre**; **NOT PUBLISHED as a coordinate in [OCC]** | — |
| vehicle walls | **[OCC]** `fixedValue (0 0 0)` on the `fixedWallPatches` regex — `0.orig/U` | `noSlip` | **SAME** | — |

### 1.3 Mesh — background, base cell, refinement

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| mesher | **[OCC]** snappyHexMesh, "a two-step snappyHexMesh approach" — README "Mesh". **[WD]** snappyHexMesh. **[ML]** ANSA 24.1.0 HeXtreme **[lifted]** | snappyHexMesh v2606 | **SAME as [OCC] and [WD]** | **this is new tonight.** R5 §2.4 registered "the VALUES transfer; the TOOLING does not" against **[ML]**. Against **[OCC]** the tooling transfers too |
| 🔴 **`snappyHexMeshDict`** | 🔴 **[OCC] SHIPS NONE.** Verified by this lane: `find … -iname '*napp*'` returns **0 files**. The meshes are **pre-generated** and downloaded from Zenodo (README "Obtaining mesh files": `polyMesh_65M/110M/236M.tar.gz`) | `make_r5_dict.py` emits ours | **NOT PUBLISHED** | 🔴 **The single most consequential cell in this table.** The one published OpenFOAM case with our exact geometry, velocity and viscosity **publishes its mesh as cells, not as a recipe.** Every layer and refinement row below therefore falls back to **[WD]**, a different body |
| background cell size | **[OCC]** README: "background blockMesh resolution of cell level **L₀ = 1 m**". **The as-shipped `blockMeshDict` is coarser than that**: `rescale 0.5`, `xCells #eval "120*$rescale"` = 60 over 120 m → **2 m**. Both values recorded; the 1 m is the README's, the 2 m is the file's | **h₀ = 0.4 m** (`make_r5_dict.py:168`) | **DIFFERENT** — ours 2.5× finer than the README's, 5× finer than the shipped dict | no reason on record; our finer background is the conservative direction. **Disclosure, PROPOSAL D5** |
| background cell size **[WD]** | **[WD]** `deltax 0.2; deltay 0.2; deltaz 0.2;` — `drivaer_fine/system/blockMeshDict` | 0.4 m | **DIFFERENT** | different body and domain; not a comparand |
| surface refinement level | **[OCC]** README: "major surface refinement level **L₉ = 1.95 mm**", "maximum feature refinement level **L₁₀ = 0.96 mm**" — consistent with 1 m / 2⁹ | **level (4 4) → 25.0 mm**; thirteen fine patches at (5 5) → 12.5 mm | 🔴 **DIFFERENT — ours is 12.8× coarser at the surface** | ✅ **REGISTERED, and registered as a forced choice.** R5 §4.2: at a 12.5 mm surface cell the layer stack ceiling is 6.0 mm, so t₁ ≤ 0.75 mm and **y⁺ ≤ 22.4 — below Sanaa's floor of 30.** "The surface cell must STAY at 25 mm and the 15-20 M cells must come from VOLUME refinement, not surface refinement" |
| surface refinement **[WD]** | **[WD]** `body2 { level ( 4 4 ); }`, `ruotaant`/`ruotapost` `( 4 4 )` — `drivaer_fine/system/snappyHexMeshDict`. Coarse ships `( 3 3 )`. At `deltax 0.2` that is **12.5 mm** | 25.0 mm | **DIFFERENT**, ours 2× coarser | same registered reason (R5 §4.2) |
| `resolveFeatureAngle` | **[WD]** `resolveFeatureAngle 30.0;` — `drivaer_fine/system/snappyHexMeshDict`. **[OCC] NOT PUBLISHED** (no dict) | **30** | **SAME as [WD]** | — |
| `nCellsBetweenLevels` | **[OCCR]** `nCellsBetweenLevels 5;` *(INFERENCE)*. **[WD]** `nCellsBetweenLevels 5;`. **[OCC] NOT PUBLISHED** — **two independent sources at 5** | (in the R2-family dict carried into R5) | **NOT VERIFIED BY THIS LANE** — this lane did not read our emitted value for this key | flagged, not filled |
| `maxGlobalCells` | **[OCCR]** `maxGlobalCells 500000000;` *(INFERENCE)*. **[WD]** `maxGlobalCells 10000000;`. **[OCC] NOT PUBLISHED** | R5 notes `maxLocalCells` is the binding cap and that 6 M would make the 15-20 M gate unreachable (`make_r5_dict.py:26`) | **DIFFERENT** | ours is set by the M1 gate, theirs by their mesh size |
| volume refinement strategy | **[OCC]** README: grid levels "chosen to resolve the turbulence in the focus regions", each level splitting by two — Figure 2. **[ML]** "size fields following geometry, extending downstream" (L275-277) **[lifted]** | four nested boxes at levels 1-4 (`make_r5_dict.py:64-68`) | **SAME in kind** | R5 §4.2 registers volume refinement explicitly as "exactly what the source did" |
| **cell count** | **[OCC]** **236 M fine / 110 M medium / 65 M coarse** — README "Mesh". **[ML]** ≈ 160 M (L270) **[lifted]**. **[A16]** 18/37/80 M RANS **[lifted]** | **15-20 M** (gate M1) | 🔴 **DIFFERENT — 3.3× below [OCC]'s COARSEST, 11.8× below its fine** | ✅ **REGISTERED as a cost choice** (R5 §7 M1). **PROPOSAL D4: state the ratio on the certificate** so no reader infers mesh equivalence. The ratio is worse than the 8-10× previously recorded against **[ML]** |

### 1.4 Layers — the rows Sanaa named

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| `relativeSizes` | **[OCCR]** `relativeSizes true;` *(INFERENCE — §0.3)*. **[WD]** `relativeSizes true;` — `drivaer_fine/system/snappyHexMeshDict` (sha256 `bd3794109d26306e9e11f0595b53240668d4390f95b6ddc6fd73ebc80407abd0`). **[OCC] NOT PUBLISHED — it ships no mesher dictionary.** **[ML]** absolute mm **[lifted]** | **`false`** (absolute) — `make_r5_dict.py:42` | **DIFFERENT from [WD]; SAME as [ML]** | ✅ **REGISTERED, and it is the whole point of R5.** R5 §2.2: `relativeSizes true` scales every thickness by the local cell, so a level-5 patch silently halves the first layer. **[WD] uses the setting that poisoned our mesh** — published practice is not automatically good practice, and this row is the proof |
| `nSurfaceLayers` | **[OCC]** README prose: "**2 prism layers**" — published as TEXT, not as a dictionary. **[OCCR]** `nSurfaceLayers 2;` on both patch groups *(INFERENCE, and it CORROBORATES the README's 2)*. **[WD]** `nSurfaceLayers 6;` on all four patches (fine); **3** (coarse). **[ML]** 7 (L271-272) **[lifted]**. **[A16]** 20 **[lifted]** | **8** | 🔴 **DIFFERENT from every source. Ours is the LARGEST of five published values** (2, 3, 6, 7, 20 — and the 20 is STAR-CCM+) | ✅ **REGISTERED** as Sanaa's instruction, divergence stated not split (R5 §4.2). 🔴 **But [OCC]'s 2 layers is a new low-water mark this lane did not expect**, and it is the source on our own geometry — see **PROPOSAL D3** |
| `expansionRatio` | **[OCCR]** `expansionRatio 1.2;` *(INFERENCE)*. **[WD]** `expansionRatio 1.2;` — both the global key and all four per-patch blocks. **[ML]** "variable growth rate between **1.2 and 1.4**" (L272-273) **[lifted]**. **[OCC] NOT PUBLISHED** | **1.11** | 🔴 **DIFFERENT — below the [ML] band AND below [WD]'s single value** | 🔴 **UNREGISTERED.** R5 quotes the 1.2-1.4 band at its line 53 and registers 1.11 at line 187 **without flagging that 1.11 is outside it**. Was proposal **P3** (`e0fbdba3`); **[WD] is now a second, independent source at 1.2.** **PROPOSAL D3** |
| `finalLayerThickness` | **[OCCR]** `finalLayerThickness 0.5;` *(INFERENCE)*. **[WD]** `finalLayerThickness 0.3;` — relative, all four patches. **[OCC] NOT PUBLISHED** | **not used** — R5 registers `firstLayerThickness 0.0010` absolute | **NOT COMPARABLE** | our sizing mode is absolute; the keyword has no counterpart. This is the correct answer, not an evasion |
| first layer height | **[OCC]** README: "the wall closest cell having a wall-normal size of e.g. **0.8 mm** on the roof top". **[ML]** **0.75 mm** (L272) **[lifted]** | **1.00 mm** | **DIFFERENT**, +25 % on **[OCC]**, +33 % on **[ML]** | ✅ **REGISTERED** (R5 §4.1): 0.75 mm gives y⁺ ≈ 22.4, below Sanaa's floor of 30, so the first layer is set from her window not from the source. 🔴 **[OCC]'s 0.8 mm confirms the conflict from a second direction** — see **PROPOSAL D2** |
| total stack | **[ML]** **12 mm** (L272) **[lifted]**. **[OCC] NOT PUBLISHED** (2 layers × ~0.8 mm ≈ 1.6-2 mm implied, but the ratio is not published and this lane does not compute one) | **11.86 mm** | **SAME as [ML]** — within 1.2 % | — |
| 🔴 **stack in LOCAL CELLS** | **[OCCR]** 2 layers, r 1.2, final 0.5 → **0.917** *(computed by this lane from the dictionary)*. **[WD]** fine **1.197**, coarse **0.758**. **[OCC] NOT PUBLISHED** | **R5: 0.474**; the collapsed predecessor: **1.6808** | 🔴 **see §0.4 — every published stack lies BETWEEN our two points** | R5's 0.474 is **below every published value**: a deliberately conservative ask, not a matched one |
| stack in local cells vs [ML] | **[ML]** 0.480 **[lifted]** | **0.474** | **SAME** | R5 fixes the 1.6808 defect |
| `minThickness` | **[OCCR]** `minThickness 1e-10;` — **relative, and effectively disabled** *(INFERENCE)*. **[WD]** `minThickness 0.01;` — **relative**, all four patches. **[OCC] NOT PUBLISHED**. **[ML] NOT PUBLISHED** | **0.0002 m** — **absolute** | **NOT COMPARABLE** (different units) | ✅ **REGISTERED, and the conversion is the registered trap.** R5 §2.2: left at a relative 0.02 it would read as 20 mm, exceeding the entire 11.86 mm stack and refusing every layer on every patch — a clean-exiting mesh with zero layers. `make_r5_dict.py` asserts against this (`:136`) |
| `featureAngle` (layers) | **[OCCR]** `featureAngle 120;` *(INFERENCE)*. **[WD]** `featureAngle 130.0;`. **[OCC] NOT PUBLISHED** | **130** (PPTC family value; **not re-read from the R5 dict by this lane**) | **SAME as [WD]**, subject to that check | — |
| `nGrow` | **[OCCR]** `nGrow 0;`. **[WD]** `nGrow 0;` — **two sources agree** | not verified this session | **NOT VERIFIED** | flagged, not filled |
| `maxThicknessToMedialRatio` | **[OCCR]** `0.3;`. **[WD]** `0.3;` — **two sources agree** | not verified this session | **NOT VERIFIED** | flagged, not filled |
| `nLayerIter` / `nRelaxedIter` | **[OCCR]** `nLayerIter 50;` (no `nRelaxedIter`). **[WD]** `nLayerIter 50; nRelaxedIter 20;` | not verified this session | **NOT VERIFIED** | flagged, not filled |
| `slipFeatureAngle` | **[OCCR]** `slipFeatureAngle 30;`. **[WD]** `slipFeatureAngle 30.0;` — **two sources agree** | not verified this session | **NOT VERIFIED** | flagged, not filled |
| **achieved layer coverage** | 🔴 **NOT PUBLISHED BY ANY SOURCE.** **[OCC]** ships no post-extrusion log; **[ML]**'s ANSA HeXtreme writes no post-extrusion table **[lifted]** | **2.50 / 5 coarse, 2.89 / 5 medium** (pre-R5, measured, R5 §5.1); gate L1 requires **≥ 5.0 of 8** on vehicle patches | **NOT PUBLISHED — NOT COMPARABLE** | **Absence of a reported failure is not evidence of success**, in their mesh or ours (R5 §2.4). **We gate on achievement; no published source does** |

### 1.5 Wall treatment and y⁺

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| wall treatment | **[OCC]** wall functions — README: "The mesh aims to be used with wall functions". **[ML]** wall functions, deliberately high-y⁺ (L273-275) **[lifted]**. **[A16]** wall-RESOLVED, the opposite choice **[lifted]** | wall functions | **SAME as [OCC] and [ML]** | — |
| 🔴 **`nut` wall function** | **[OCC]** `type nutUSpaldingWallFunction; tolerance 1e-9;` on the `fixedWallPatches` regex — **`0.orig/nut`, read by this lane**. **[ML]** "Spalding's law of the wall … valid for arbitrary values of y⁺" (L1385) **[lifted]** | 🔴 **`nutkWallFunction`** on the `".*"` block — measured by this lane in `verification/runs/navier_class/DRIVAER/r2_medium/0.orig/nut` (the case R5 stages from, `build_r5.sh` `SRC=$D/r2_medium`) and in `cases/navier_class/DRIVAER/mesh/write_solver_case.py:137-138` | 🔴 **DIFFERENT — and it contradicts our own frozen registration** | 🔴 **SEE §5.1. THIS IS THE FINDING OF THE NIGHT.** R5 §3 names the held-constant treatment as "`nutUSpaldingWallFunction` on the `\".*\"` vehicle block". **The case on disk carries `nutkWallFunction`.** `nutk` is high-Re-only and invalid below y⁺ ≈ 30; Spalding is valid at arbitrary y⁺. Both published sources use Spalding |
| `k` wall function | **[OCC]** `kqRWallFunction` — `0.orig/k` | `kqRWallFunction` | **SAME** | — |
| `omega` wall function | **[OCC]** `omegaWallFunction; blended true;` — `0.orig/omega` | `omegaWallFunction` (**`blended` not verified by this lane**) | **SAME** on the type; blending **NOT VERIFIED** | flagged |
| y⁺ target | **[OCC]** README: "values of **y⁺ > 30** are achieved for the major parts of the mesh", Figure 3. **[ML] NOT PUBLISHED** (the ≈22 in our records is **lab-derived**, never a published value) **[lifted]**. **[A16]** y⁺ < 1 **[lifted]** | gate **Y1: 30 ≤ area-weighted median ≤ 100** | **SAME as [OCC] in kind** — a published floor of 30 against our gate floor of 30 | 🔴 **This is the first published corroboration of Sanaa's y⁺ floor.** The earlier conflict (her 30 vs a lab-derived 22) rested on a derived number; **[OCC] publishes "> 30" in words.** **PROPOSAL D2 revises accordingly** |
| y⁺ measured, ours | — | pre-R5 median **153.1**, **0 of 47** vehicle patches below 30 (R5 §4.1, §7) | — | R5 predicts ≈ 30 after the layer fix and registers the failure mode explicitly |

### 1.6 Turbulence, schemes and solver controls

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| solver | **[OCC]** `application simpleFoam;` — `system/controlDict`. **[WD]** `application simpleFoam;` | `simpleFoam` | **SAME as both case files** | — |
| turbulence model | **[OCC]** `RASModel $RASturbModel;` with `RASturbModel kOmegaSST;` — `constant/turbulenceProperties` + `caseDefinition`. **[WD]** `RASModel kOmegaSST;`. **[ML]** Spalart-Allmaras near-wall + σ-model LES **[lifted]** | **`kOmegaSST`** | **SAME as both case files**; differs from **[ML]** | — |
| `ddtSchemes` | **[OCC]** `default steadyState;` — `system/fvSchemes`. **[WD]** `default steadyState;` | `steadyState` | **SAME** | see §B |
| `div(phi,U)` | **[OCC]** `bounded Gauss linearUpwindV grad(U);` — `system/fvSchemes`. **[WD]** `bounded Gauss linearUpwind grad(U);` | **`bounded Gauss linearUpwind grad(U)`** — `write_solver_case.py:222` | **SAME as [WD]; [OCC] uses the V-variant** | the `V` form limits on the velocity-vector direction. No reason on record; **PROPOSAL D5** (disclosure) |
| `div(phi,k)` / `div(phi,omega)` | **[OCC]** `bounded Gauss upwind;` (both, via `$turbulence`) — `system/fvSchemes`. **[WD]** `bounded Gauss upwind;` (both) | **`bounded Gauss limitedLinear 1`** (both) — `write_solver_case.py:223-224` | 🔴 **DIFFERENT — both published case files use FIRST-ORDER upwind on the turbulence equations; we use second-order** | 🔴 **UNREGISTERED.** Ours is the stricter (higher-order) choice, so the deviation is not obviously adverse, but **two independent OpenFOAM case files agree against us** and nothing on record says why. **PROPOSAL D5.** Note the identical finding was registered on PPTC (row 36 of the PPTC table) against Klerebrant Klasson's first-order turbulence convection |
| `gradSchemes` | **[OCC]** `default Gauss linear; grad(U) cellLimited Gauss linear 1;` — `system/fvSchemes` | `default cellLimited Gauss linear 1` — `write_solver_case.py:218` | **DIFFERENT** — ours limits every gradient, theirs only `grad(U)` | ours is the more diffusive/stabler choice. **PROPOSAL D5** (disclosure) |
| `laplacianSchemes` | **[OCC]** `Gauss linear corrected;` — `system/fvSchemes`. **[WD]** `Gauss linear limited 0.5;` | not re-read by this lane | **NOT VERIFIED** | flagged, not filled |
| `SIMPLE consistent` | **[OCC]** `consistent yes;` — `system/fvSolution`. **[WD]** `consistent yes;` | `consistent yes` — `write_solver_case.py:262` | **SAME as both** | — |
| `nNonOrthogonalCorrectors` | **[OCC]** `0` — `system/fvSolution`. **[WD]** `2` | **0** — `write_solver_case.py:261` | **SAME as [OCC]** | — |
| relaxation factors | **[OCC]** `U 0.9; k 0.6; omega 0.6;` (no `p` entry — SIMPLEC) — `system/fvSolution` | **`U 0.9; ".*" 0.9;`** — `write_solver_case.py:265` | **DIFFERENT on k and omega** — ours 0.9, theirs 0.6 | 🔴 **UNREGISTERED.** Ours relaxes the turbulence equations 1.5× harder than the published case on our own geometry. **PROPOSAL D5** |
| linear-solver targets | **[OCC]** **fixed-iteration**, `tolerance 0; relTol 0;` with `maxIter 12` (p, GAMG), `15` (U), `8` (k, omega) — `system/fvSolution`. This is the HPC-Challenge hardware track; `fvSolution.fixedTol` is the software track and **is byte-identical to the shipped `fvSolution`** (both sha256 `5e1db8548ee82c44…`, verified by this lane) | `relTol 0.01` on p and U | **DIFFERENT** | theirs is a benchmark construct for deterministic per-step cost, not a physics choice. **No change proposed** |
| `residualControl` | **[OCC] NOT PUBLISHED** — no `residualControl` block in `system/fvSolution`. **[WD]** `p/U/k/omega 1.0e-3` — `drivaer_fine/system/fvSolution` | 🔴 **DELIBERATELY NONE** — `write_solver_case.py:205-206`: "the run must reach endTime so that last == endTime and the ExecutionTime count == round(endTime/deltaT)" | **SAME as [OCC] in effect** | ✅ **REGISTERED**, and for a lab-specific reason: CLAUDE.md rule 4's completion clause. `residualControl` would stop the run early and break `last == endTime` |
| initialisation | **[OCC]** `potentialFoam -initialiseUBCs`, then **`applyBoundaryLayer -ybl "0.0450244"`** — `Allrun`. **A published initialisation recipe with a published boundary-layer thickness.** | freestream / continuation | **DIFFERENT** | 🔴 **UNREGISTERED and cheap to adopt.** **PROPOSAL D6** |
| decomposition | **[OCC]** `hierarchical`, `nHierarchical (16 8 4)` at `nCores 512` — `caseDefinition` | 96 cores on this box | **NOT COMPARABLE** | hardware |
| precision | **[OCC]** README: "compiled with double precision (WM_PRECISION_OPTION=DP)". **[ML]** double (L328) **[lifted]** | to confirm at stage time (R5 **P7**) | **NOT VERIFIED** | already a live proposal |

### 1.7 Inlet turbulence

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| turbulence intensity | **[OCC]** `Tu 0.0026;` = **0.26 %** — `system/include/caseDefinition` | **0.1 %** (`TURB_INTENSITY = 0.001`, `write_solver_case.py:23`, commented "open-road freestream (Spalart-Rumsey 2007 class)") | **DIFFERENT** — ours 2.6× lower | 🔴 **UNREGISTERED against [OCC].** Our value cites a general reference, theirs is this case's own. **PROPOSAL D6** |
| turbulent viscosity ratio | **[OCC]** `viscRatio 5.0;` → `nut_inf = 7.535e-05` — `caseDefinition`, `0.orig/nut` | **`NUT_RATIO = 1.0`** → `nut_inf = 1.507e-05` (`write_solver_case.py:24`) | **DIFFERENT** — ours 5× lower | 🔴 **UNREGISTERED.** **PROPOSAL D6** |
| inlet k | **[OCC]** `kref #eval{ 1.5*sqr($UinfMag*$Tu) }` = **0.015334 m²/s²** (derived by this lane from the published inputs) | **0.0022686** (same formula, our Tu) | **DIFFERENT** — factor 6.76, the square of the Tu ratio | as above |
| inlet omega | **[OCC]** `omegaref #eval{ $kref/$nutref }` = **203.5 s⁻¹** (derived by this lane) | **150.5 s⁻¹** (derived by this lane) | **DIFFERENT** | as above |

### 1.8 Run control and averaging

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| steady / transient | **[OCC]** steady. **[WD]** steady. **[ML]** transient. **[A16]** both | **steady** | **SAME as both case files**; **DIFFERENT from [ML]** | **see §B — the framing splits, and both halves are true** |
| time step | **[OCC]** `deltaT 1;` — an iteration index, not time — `system/controlDict` | iteration index | **SAME** | — |
| iteration count | **[OCC]** `endTime 4000;` in `system/controlDict`; the README says the `Allrun` "runs the RANS (simpleFOAM) solver for **2000 steps**". **Both recorded; they disagree and this lane does not reconcile them.** **[WD]** `endTime 10000;` with a `//1000-3000-5000` comment | **3000** (2000 steady + 1000 averaged) | **DIFFERENT**, and inside the published spread 2000-10000 | — |
| averaging window | 🔴 **[OCC] NOT PUBLISHED — it publishes no averaging at all.** A steady benchmark quotes a converged Cd, not a windowed mean. **[ML]** detected window, 40-60 CTU bracket, ±1.5 drag counts (L320) **[lifted]** | **iterations 2001-3000, exactly 1,000 samples, FIXED BY SCHEDULE** | **NOT PUBLISHED** | ✅ **REGISTERED, and deliberately unlike [ML]'s.** R5 §6.3: there is **no stationarity trigger**, because "a detected window lets the run choose its own from the trace — the precise defect this section exists to prevent". **Our construct is stricter than the published one** |
| reported beside the mean | **NOT PUBLISHED by any source** | window sd; trailing-200 excursion; sign-reversal rate over 400 samples; drift across **eight** window lengths (R5 §6.4) | **NOT PUBLISHED** | ours has no published counterpart and is stricter than all of them |
| cost | **[OCC]** 512 cores, hierarchical **[** wall time NOT PUBLISHED **]**. **[ML]** ≈ 40 h on 1536 cores = **3,686,400 core-min** **[lifted]** | R5 basis **6,936 core-min** | **DIFFERENT** — **531× below [ML]** | cost choice, already registered |

---

# 2. PPTC VP1304

**This table is LIFTED, not re-measured.** It is a condensation of
`cases/PPTC_VP1304/PUBLISHED_VS_REGISTERED_RECONCILIATION.md` (**commit `766c1b26b`**, 45 rows),
built by a cfd `lab-lane` from three committed ingests:
`PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md` (`99cacfb12`),
`PUBLISHED_OPENFOAM_SETUP_INGEST_SMP11.md` (`074d702bf`),
`PUBLISHED_SNAPPYHEXMESH_INGEST_CHENG_2024.md` (`26dd894bd`).
**Every published figure below is that lane's measurement, attributed to it, not this lane's.**
This lane's own contribution to the PPTC case is §0.1's token sweep, which independently reproduces
that document's zero-count claim across the same corpus.

**Source tags:** **CH** Cheng 2024 (OpenFOAM + snappyHexMesh) · **KK** Klerebrant Klasson & Huuva
2011 (OpenFOAM, ANSA mesher) · **GG** Gaggero, Villa & Brizzolara 2011 (OpenFOAM, unstructured) ·
**SK** Sikirica 2019 (**Fluent + STAR-CCM+, not OpenFOAM**) · **QQ** smp'11 questionnaire.

🔴 **READ §A.1 FIRST. Three published rotation rates, none of them ours. No published K_T, K_Q or η
below may band our act.**

🔴 **NO PUBLISHED `snappyHexMeshDict` FOR PPTC VP1304 EXISTS IN ANY OF THE SIX SOURCES ON DISK.**
Unlike DrivAer and M6, **no case tree was retrieved for PPTC tonight.** Every mesher row is therefore
`NOT PUBLISHED`, and that is the finding.

### 2.1 Topology — not a parameter, and it explains the 95.5×

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| background topology | **CH:** Cartesian box, full 360° (p. 4) · **KK:** full 360°, ANSA (p. 2) · **GG:** full 360° (p. 2) · **SK:** block-structured 72° passage (p. 7) | **72° `blockMesh` wedge + a 2 mm numerical `axisRod`** | 🔴 **DIFFERENT — three of four published setups mesh the full propeller, and NO published setup puts an octree mesher on a wedge** | ✅ proposed reason: *"Geometry and topology differ: published setups mesh the full 360° propeller; ours is a 72° cyclic passage, which requires an axis body a box background does not."* **This single row is the cause of the layer-thickness poisoning**: `hexRef8::getLevel0EdgeLength()` returns the global minimum level-0 edge, which on our wedge is the azimuthal chord of the 2 mm rod, `2·0.002·sin(π/60) = 2.09343825e-04 m` against an intended base of `0.020 m` — **95.53×**. On a Cartesian box every level-0 cell is a cube and the defect cannot arise. Now §16 of `docs/standards/MESH_STANDARD.md` (v1.11, `50ce30f5`) |

### 2.2 Mesh and layers — OpenFOAM sources only (Sanaa's §G split)

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| mesher | **CH p. 4:** *"the SnappyHexMesh utility implemented in OpenFOAM"* | snappyHexMesh | **SAME** | — |
| base cell size | **NOT PUBLISHED as a length.** CH Table 2 caption p. 5 controls refinement *"by changing the base cell scale on the input/output patches"* | **20.0 mm** at family ratio 1.0 (`check_tessellation_adequacy.py:47`) | **NOT PUBLISHED** | ours stands unsourced |
| refinement level, blades | **NOT PUBLISHED** as a level | **(5 5)** → 0.625 mm (`make_snappy.py:37-45`) | **NOT PUBLISHED** | — |
| refinement level, hub / cap | **NOT PUBLISHED** | **(4 4)** → 1.25 mm | **NOT PUBLISHED** | — |
| refinement level, shaft | **NOT PUBLISHED** | **(3 3)** → 2.5 mm; shaftExtension (2 2) → 5 mm | **NOT PUBLISHED** | — |
| tip-vortex refinement | **CH Table 2 p. 5:** normalised tip-vortex cell **x̂_tv = 0.004 / 0.006 / 0.009** across three levels | `tipVortex` region at blade level − 1, 1 D downstream (`make_snappy.py:152`) | **published as a RATIO, ours as a LEVEL** | proposed: report x̂_tv per level on the birth certificate so the two become comparable |
| `nSurfaceLayers` | **NOT PUBLISHED IN ANY OpenFOAM SOURCE.** *(KK p. 2, a non-snappy OpenFOAM source, states 5 prism layers)* | **6** (`make_snappy.py:48`) | **NOT PUBLISHED** (6 vs KK's 5 is close) | — |
| `expansionRatio` | **KK p. 2:** *"Five prism layers with **1.2 as growth ratio**"* | **1.2** (`make_snappy.py:49`) | **SAME — exactly** | — |
| first layer thickness | **KK p. 2:** **0.5 mm, stated as an ABSOLUTE length** — *"a starting length of 0.5 mm"* (= 0.002 D) | **relative**: `finalLayerThickness 0.5` with `relativeSizes true` → intended ≈ **0.126 mm**, poisoned to ≈ **1.3 µm** | 🔴 **DIFFERENT, twice over** | ours is 4× thinner than the published value *before* any poisoning. PRISM-A2's switch to absolute sizes **needs a first-layer height chosen against KK's 0.5 mm**, not merely the relative expression repaired |
| `relativeSizes` | 🔴 **NOT PUBLISHED — 0 occurrences anywhere** (independently reproduced by this lane, §0.1). The one snappy source (CH) prints no dictionary; the absolute-sizing OpenFOAM sources (KK, GG) are not snappy | **`true`** (`make_snappy.py:165`) | **NOT PUBLISHED** | **PRISM-A2 sets `false`. No published source contradicts that; none endorses `true` either. Silence is not evidence** (rule 3) |
| `minThickness` | **NOT PUBLISHED** | **0.05**, relative (`make_snappy.py:170`) | **NOT PUBLISHED** | it is **relative**, so PRISM-A2's switch must re-express it too |
| `featureAngle` | **NOT PUBLISHED** | **130** (layers); `resolveFeatureAngle` **30** | **NOT PUBLISHED** | — |
| other layer controls | **NOT PUBLISHED** | `make_snappy.py:171-175` | **NOT PUBLISHED** | — |
| castellation controls | **NOT PUBLISHED** | `nCellsBetweenLevels` **3**, `maxGlobalCells` 60e6, `maxLocalCells` 4e6 | **NOT PUBLISHED** | — |
| snap controls | **NOT PUBLISHED** | `nRelaxIter` 5, `nFeatureSnapIter` 15, `explicitFeatureSnap true` | **NOT PUBLISHED** | — |
| achieved y⁺ | **CH Table 2 p. 5:** 92 → 40 → 19 · **KK p. 4:** 25-34 · **QQ p. 3:** envelope <1 to 160, clustering 30-50 | registered window **30-60**; amended **30-300** for the smoke; prediction 50-200 | **SAME** — our window sits inside the published cluster | — |
| cell count | **CH p. 5:** 18.0 / 26.9 / 40.4 M full propeller · **KK p. 2:** 4.5 / 11 M · **GG p. 2:** 1.4 M · **SK p. 9:** 1.7 M per 72° passage | **0.8 / 2.7 / 9 M per 72° passage** ≈ 4 / 13.5 / 45 M full-propeller equivalent | **SAME in envelope** — our fine ≈ CH's finest; our medium sits between KK's 11 M and CH's 18 M | our coarse is 4.5× below CH's coarsest |
| mesh quality gates | **KK p. 3:** *"negligible skewness"* · **SK p. 4:** *"acceptable ranges with occasional outlier cells"* — **no numbers in any source** | maxNonOrtho 65 (relaxed 70), maxBoundary/InternalSkewness 4 | **NOT PUBLISHED as numbers** | ours is stricter than snappy's own defaults (`maxBoundarySkewness` 20) |

### 2.3 Domain and rotating zone

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| downstream extent | **SK p. 6:** 10 D · **KK p. 2:** 12.0 D · **CH p. 4:** 8 D. **SK's own survey: *"values larger than 7D are usually adequate"*** | **6 D** (`make_blockmesh.py:57`) | 🔴 **DIFFERENT — below EVERY published value and below the stated 7 D envelope** | 🔴 **this one CHANGES; it is not excused.** Proposed **≥ 10 D** |
| domain radius | **SK p. 6:** 2.5 D · **KK p. 2:** 2.52 D · **CH p. 4:** ±1.2 D box half-width with symmetry sides | **4 D** (`make_blockmesh.py:58`) | **DIFFERENT** — 1.6× wider than two independent published values | ✅ proposed: *"Ours is larger, not smaller; blockage is bounded more tightly than any published setup, so the deviation is conservative for the graded quantity."* |
| upstream extent | **SK p. 6:** 3.5 D · **KK p. 2:** 5.04 D · **CH p. 4:** 2 D | **3 D** (`make_blockmesh.py:56`) | **SAME** — inside the published spread (2-5 D) | *"within published practice"* |
| MRF zone diameter | **KK p. 2:** 1.47 D · **SK p. 8:** none (SRF) · **CH p. 4:** none (sliding) | **1.3 D**, sensitivity at **1.6 D** | **SAME in effect** — KK's 1.47 D falls **between** our baseline and our sensitivity point | our registered pair brackets published practice; proposed: say so on the certificate |
| MRF zone axial extent | **KK p. 2:** 0.28 D upstream, **9.77 D downstream** — the zone *is* the slipstream | **±0.5 D** | 🔴 **DIFFERENT — 0.5 D vs 9.77 D** | ✅ proposed: *"A 9.77 D MRF zone places the entire wake in the rotating frame, which changes what the wake means for the LDV comparison. Our ±0.5 D keeps the graded wake in the stationary frame. Deliberate and disclosed on the certificate."* |
| passage vs full propeller | **SK p. 7:** 72° passage · **KK, GG, CH:** full 360° | 72° cyclic passage | **DIFFERENT** | ✅ *"Geometry differs: passage vs 360°."* Our registered full-360 cross-check (≤ 0.5 % in K_T) bounds it |
| outer boundary | **SK p. 7:** free-slip · **CH p. 4:** symmetry on four sides | slip | **SAME** | — |
| outlet | **SK p. 7:** static pressure · **KK p. 2:** pressure outlet · **CH p. 4:** Neumann | fixed pressure | **SAME** | — |
| walls | **SK p. 7, KK p. 2:** no-slip on blade, hub, shaft | no-slip, rotating | **SAME** | — |
| root gap | **SK p. 4:** removed · **KK p. 1:** root gap **and** hub/shaft intersection gap filled · **GG p. 2:** sealed blade/hub | 0.3 mm root gap closed | **SAME** | **KK also closes the HUB/SHAFT gap.** Proposed: confirm ours does, and record it |

### 2.4 Physics, schemes, convergence

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| turbulence model | **KK p. 2:** high-Re k-ω SST · **SK abstract + p. 15:** Realizable k-ε **and** SST k-ω, concluding *"for low and high ratios … Realizable k-ε … more accurate"* · **CH p. 2:** dynamic LES | **k-ω SST only** | **DIFFERENT in coverage** | SST is corroborated by the OpenFOAM source (KK); the only source that ran both found k-ε better at the sweep ends. Proposed: add a second closure — noting SA is **neither** of the two the paper compared, so it tests robustness, not SK's finding |
| wall treatment | **KK p. 2:** wall functions, *"To model the boundary layer, wall functions were needed"*, y⁺ > 30 · **SK pp. 4, 8:** wall-resolved, y⁺ ≈ 1 | wall functions, `nutkWallFunction`, y⁺ 30-60 | **SAME as the OpenFOAM source (KK); DIFFERENT from SK** | ✅ *"Wall-modelled by registration; §B.5 names wall-resolved y⁺≈1 as the next rung. Published OpenFOAM practice on this propeller is wall-functioned."* |
| rotating-frame method | **KK p. 2:** MRF, `MRFSimpleFoam`, OpenFOAM 1.6 · **SK p. 8:** SRF · **CH p. 4:** sliding interface | `simpleFoam` + `MRFProperties` | **SAME as KK** | `MRFSimpleFoam` is the 1.6-era name for exactly our scheme |
| steady vs transient | **KK p. 2, SK p. 8:** steady RANS · **CH p. 2:** transient LES | steady | **SAME** with both RANS sources | — |
| pressure-velocity coupling | **SK p. 8:** segregated SIMPLE (both solvers) | SIMPLE, consistent formulation | **SAME** | — |
| momentum convection | **KK p. 2:** second-order upwind · **SK p. 8:** *"Second-order … predominantly"* · **QQ p. 9:** high-order upwind dominant | `linearUpwind` for U | **SAME** with all three | — |
| turbulence convection | **KK p. 2:** **FIRST-ORDER** — *"first order accurate schemes were used for the turbulent quantities"* · **QQ p. 10:** both common | **`limitedLinear 1`** — second-order | **DIFFERENT** from the OpenFOAM source | ✅ *"Second-order retained as the stricter choice; KK's first-order disclosed as the published alternative. If the SIMPLE loop stalls, first-order turbulence convection is the registered fallback and its use is recorded."* **Note the same disagreement appears on DrivAer against two case files (§1.6)** |
| residual target | **KK p. 3:** 1e-5 on pressure, velocity **and** turbulence · **SK p. 8:** 1e-6 on all variables | **1e-5 on p and U** | **DIFFERENT — and the two sources disagree with each other** | ours matches the OpenFOAM source on the threshold but covers fewer variables. Proposed: **1e-6 on p, U and turbulence** |
| stationarity criterion | **SK p. 8:** variance < 0.01 % of the mean over the last 1000 iterations (`or` residuals 1e-6) | **0.1 % over the last 500 iterations** (`and` residuals) | 🔴 **DIFFERENT — 10× looser on tolerance, 2× shorter window** | proposed **0.01 % over 1000**. Ours is an `and`, SK's an `or` — **ours is the stricter logic and should stay `and`** |
| inlet turbulence intensity | **SK p. 7:** **2 %**, *"estimated based on the calculated Reynolds values for external flow"* · **KK p. 2:** computed from eqs. 1-4, **value not printed** | **1 %**, mixing length 0.1 D | **DIFFERENT** | proposed **2 %**, with SK's stated basis recorded |
| iteration cap | **NOT PUBLISHED** in any source | 4000 per point | **NOT PUBLISHED** | Sanaa's 2026-09-12 NO CAP ruling governs, not this row |
| relaxation factors | 🔴 **NOT PUBLISHED in any source** — no source prints under-relaxation values | **U 0.7, p 0.3, turbulence 0.7** | **NOT PUBLISHED** | ours stands unsourced. *(Contrast §1.6: the occDrivAer **case file** publishes them. Same gap, and the case file closes it)* |
| non-orthogonal correctors | **NOT PUBLISHED** | 1 | **NOT PUBLISHED** | — |
| force integration surfaces | **KK p. 2:** **BLADES ONLY** — *"The forces and moments were computed on the blades only"* | **blades + hub + shaft** (Sanaa §B.3) | 🔴 **DIFFERENT — and it changes which SVA table is the comparator** | ✅ *"Sanaa's §B.3 fixes the comparator as the 'including hub' table (Report 3752 p. 2.11). KK's blades-only figures are compared against the blades-only table (p. 2.13), differing by ≈0.01 in K_T at J=1.2, and are disclosed as such."* |
| K_T, K_Q, J, η definitions | **SK Eqs. 3-6 p. 8 · KK Eqs. 6-8 p. 3 · CH Eqs. 19-20 p. 4** — all identical | identical | **SAME** — four independent corroborations | — |
| J range | **SK p. 10:** 0 → 1.4422, 10 points · **KK p. 4:** 0.6 → 1.2, 4 points · **CH p. 4:** single J = 1.019 | **0.7985 → 1.4594**, 6 measured points | **DIFFERENT** — partial overlap only | no change proposed; ours is fixed to measured points so no interpolation is needed for the gate |

---

# 3. ONERA M6

> ## 🔵 FOR INFORMATION ONLY — THIS IS NOT A CHANGE PROPOSAL
>
> **Sanaa has ruled that M6 continues as it is, on the NASA mesh.** Nothing in this table is a
> recommendation to move M6 onto the Alletto case, onto snappyHexMesh, or onto any other setup. It
> exists so that the lab can say, on the record, **how our M6 differs from the one publicly
> available OpenFOAM M6 case** — and every row is written to be read that way. **No row here
> proposes anything.**

**Published source:** the OpenFOAM-wiki **Alletto** ONERA M6 case, retrieved tonight by a sibling
cfd lane to
`/home/ubuntu/upstream/published-openfoam-setups/alletto-openfoamtutorials/OneraM6Wing`.
**CASE FILES**, complete: `system/{snappyHexMeshDict,blockMeshDict,controlDict,fvSchemes,fvSolution}`,
`constant/{turbulenceProperties,thermophysicalProperties}`, `0.orig/*`, `Allrun`, plus seven
experimental `expy=*.dat` section files. Read and hashed by this lane.

**Our value:** **M6J**, `verification/campaign/M6J_TRANSONIC_FAMILY_PREREGISTRATION.md`, staged from
the **M6I imported grid family** — the lab's first imported external grid family, AGARD AR-138 test
2308 via NASA TMR. Case values read by this lane from `verification/runs/M6J_runs/M6J_L3/`.

🔴 **THE STRUCTURAL ROW FIRST: our M6 uses no mesher at all.** M6I/M6J run on an **imported,
externally generated structured grid**. The Alletto case generates its mesh with
**blockMesh + snappyHexMesh**. **Every mesher row below is therefore `NOT COMPARABLE` on our side —
not missing, not deficient: structurally absent.** That is the honest reading of an imported-grid
ladder, and it is exactly why Sanaa's ruling to continue on the NASA mesh is not disturbed here.

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| solver | `application rhoSimpleFoam;` — `system/controlDict` (sha256 `4348293854a9be63…`) | `rhoSimpleFoam` | **SAME** | — |
| turbulence model | `RASModel SpalartAllmaras;` — `constant/turbulenceProperties` (sha256 `d463dfa6e1865d7b…`) | `SpalartAllmaras` | **SAME** | M6J §5 records SA is **retained deliberately**: R8's `kOmegaSST` is a closed rung and switching would confound the formulation against its baseline |
| freestream velocity | `Uinlet (290 0 15.5);` — `0.orig/U` (sha256 `61ab35b52166299d…`); \|U\| = 290.41 m/s, incidence **3.06°** | `(291.022155821 0 15.5574365217)`; \|U\| = 291.44 m/s, incidence **3.0600°** | **SAME on incidence** (four decimals); **DIFFERENT on speed** by 0.35 % | ours is set from AGARD AR-138 test 2308 at Re = 11.72e6 on the MAC c = 0.64607 m (M6I §1). Theirs is a round-number tutorial condition |
| freestream T | `Tinlet 298;` — `0.orig/T` | **300 K** — `0.orig/T` | **DIFFERENT**, 0.7 % | ours is the registered AGARD condition set |
| freestream p | `pOut 1e5;` — `0.orig/p` | **101325 Pa** — `0.orig/p` | **DIFFERENT**, 1.3 % | as above |
| transport model | `transport const;` with `mu 1.82e-05; Pr 0.71;` — `constant/thermophysicalProperties` (sha256 `3a6a65f7579e9b2b…`) | 🔴 **`transport sutherland;`** with `As 1.85535931851e-06; Ts 110.4;` | 🔴 **DIFFERENT in KIND, not merely in value** | theirs holds viscosity constant; ours varies it with temperature. Across a transonic expansion these are not the same fluid. **Stated, not proposed** |
| `molWeight` | `28.9` — `constant/thermophysicalProperties` | **28.97** | **DIFFERENT**, 0.24 % | ours is the standard air value |
| `Cp` | `1005` | `1005` | **SAME** | — |
| inlet `nuTilda` | `1.0e-05` — `0.orig/nuTilda` | **5.9884457504e-05** | **DIFFERENT** — ours 6.0× theirs | ours is set from the registered Re; theirs is a round tutorial value |
| inlet/outlet BC type | `freestreamVelocity` / `freestreamPressure` — `0.orig/{U,p}` | `freestreamVelocity` / `freestreamPressure` | **SAME** | — |
| domain | `blockMeshDict` (sha256 `4360903469a3b2a2…`): cube **−18000 … +18000** in x and z, **0 … 18000** in y, a single `hex … (30 15 30)` block, `scale 1`. `Allrun` runs `transformPoints -scale "(0.001 0.001 0.001)"` **after** meshing, so the mesh is built in mm and shrunk to a **36 m cube** | NASA/AGARD imported far-field | **NOT COMPARABLE** | our domain is a property of the imported grid |
| background cell size | 36000 mm / 30 = **1200 mm** (→ 1.2 m after the scale) — `blockMeshDict` | **NOT COMPARABLE** — imported grid | **NOT COMPARABLE** | — |
| mesher | blockMesh + **snappyHexMesh** — `Allrun`, `system/snappyHexMeshDict` (sha256 `c36623e018c77971…`) | 🔴 **none — imported grid** | **NOT COMPARABLE** | the structural row |
| surface refinement | `wing { level (8 9); }` — `snappyHexMeshDict`. At a 1200 mm base: level 8 = **4.69 mm**, level 9 = **2.34 mm** | **NOT COMPARABLE** | **NOT COMPARABLE** | — |
| volume refinement | five nested `refinementBox0…4` at levels 5, 4, 3, 2, 1 — `snappyHexMeshDict` | **NOT COMPARABLE** | **NOT COMPARABLE** | — |
| `resolveFeatureAngle` | `resolveFeatureAngle 30;` | **NOT COMPARABLE** | **NOT COMPARABLE** | — |
| `nCellsBetweenLevels` | `nCellsBetweenLevels 3;` | **NOT COMPARABLE** | **NOT COMPARABLE** | — |
| `maxGlobalCells` | `maxGlobalCells 2000000;` | **NOT COMPARABLE** | **NOT COMPARABLE** | *(context: the Alletto case caps at 2 M; our M6J family runs 15,360 / 122,880 / 983,040)* |
| **`relativeSizes`** | **`relativeSizes true;`** — `snappyHexMeshDict` | **NOT COMPARABLE** | **NOT COMPARABLE** | **published, and published as `true`** |
| **`nSurfaceLayers`** | **`wing { nSurfaceLayers 5; }`** | **NOT COMPARABLE** | **NOT COMPARABLE** | published |
| **`expansionRatio`** | **`expansionRatio 1.5;`** | **NOT COMPARABLE** | **NOT COMPARABLE** | published — and **1.5 is above the 1.2-1.4 band DrivAerML publishes**, which is itself worth knowing |
| **`finalLayerThickness`** | **`finalLayerThickness 0.5;`** (relative) | **NOT COMPARABLE** | **NOT COMPARABLE** | published |
| **`minThickness`** | **`minThickness 0.05;`** (relative) | **NOT COMPARABLE** | **NOT COMPARABLE** | published |
| **`featureAngle`** | **`featureAngle 60;`** | **NOT COMPARABLE** | **NOT COMPARABLE** | published |
| mesh quality controls | `maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minTetQuality 1e-30;` … — `snappyHexMeshDict` | our imported grid is gated by `MESH_STANDARD.md` | **NOT COMPARABLE** | note **`maxNonOrtho 65` and `maxInternalSkewness 4` are character-for-character our PPTC values** (§2.2) |
| `div(phi,U)` | `Gauss linearUpwind limited;` — `system/fvSchemes` | **`bounded Gauss limitedLinearV 1`** — `M6J_L3/system/fvSchemes` | **DIFFERENT** | ✅ **REGISTERED, and measured.** M6J §2: *"`linearUpwind` is not available and that is measured, not preferred: `L2/ATTEMPT1_DIVERGED` and `L1/ATTEMPT1_DIVERGED` both exist"* — it diverged on both fine levels. **The published scheme was tried and it failed on our grids** |
| `div(phi,nuTilda)` | `Gauss linearUpwind limited;` (via `$turbulence`) | **`bounded Gauss limitedLinear 1`** | **DIFFERENT** | same registered reason |
| `laplacianSchemes` | `Gauss linear corrected;` | **`Gauss linear limited corrected 0.33`** | **DIFFERENT** | registered remedy for non-orthogonality on the imported grid |
| `snGradSchemes` | `corrected;` | **`limited corrected 0.33`** | **DIFFERENT** | as above |
| `gradSchemes` | `default Gauss linear;` with `cellLimited Gauss linear 1` on U, k, omega | not re-read by this lane | **NOT VERIFIED** | flagged |
| `nNonOrthogonalCorrectors` | not read by this lane from their `fvSolution` | **2** — `M6J_L3/system/fvSolution` | **NOT VERIFIED** on the published side | M6J §5 records R9's `nNonOrthogonalCorrectors 5` was **not** carried forward; it stays 2 |
| `ddtSchemes` | `default steadyState;` | steady | **SAME** | — |
| `endTime` | `endTime 500;` — `system/controlDict` | **3000 / 5000 / 8000** at L3 / L2 / L1 | **DIFFERENT** — ours 6-16× longer | ours is set so that rule 4's `last == endTime` holds with margin for plateau |
| post-processing | `Allrun` runs `rhoSimpleFoam -postProcess -func yPlus`, `wallShearStress`, `samplePwall`, then `plot.py` against seven `expy=*.dat` experimental sections | M6I/M6J grade C_p against AGARD sections at η = 0.65 and 0.90 | **SAME in kind** | **both compare sectional C_p against the AGARD experiment.** Theirs samples at η = 0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99; ours gates at two of those seven |
| force reference | `origin (0.25 0 0)` with an axes rotation — `system/controlDict` `forces1` | `S_ref = 0.7532 m²`, `L_ref = c = 0.64607 m` (M6I §1, checked against AGARD's own b, λ, S) | **DIFFERENT** | ours is the AGARD reference set, verified rather than asserted; theirs is a tutorial convention |

**The one thing this table does say, and it is not a proposal:** the Alletto case is a **complete,
runnable, publicly available OpenFOAM M6 recipe** whose snappyHexMeshDict publishes all six of the
keywords no paper publishes. **It is now on this box.** Whether the lab ever uses it is Sanaa's and
the supervisor's call, and **her ruling stands: M6 continues on the NASA mesh.**

---

# 4. DARPA SUBOFF

> ## 🔵 FOR INFORMATION ONLY — THIS IS NOT A CHANGE PROPOSAL
>
> **Same reason as §3: SUBOFF continues as it is.** Nothing below recommends a change. The table
> exists to record, honestly, **how much of the published SUBOFF setup this lab actually holds** —
> and the answer is the most `NOT RETRIEVED` of the four cases.

🔴 **THE HEADLINE FOR THIS CASE IS THE ABSENCE.** The brief named "the Type 209 / Robertson setup".
**Neither is on this box.** This lane searched the repository for `robertson`, `type 209` and
`Type209`: the only two hits are (a) `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
line 259, which is the *directive naming them as things to obtain*, and (b) an unrelated occurrence
in a DAFoam adjoint paper. **No SUBOFF case tree was retrieved tonight.**

**What the lab does hold** — four DTRC reports, title-page verified, in
`docs/papers/benchmark_test_cases/`:

| holding | what it is | `OpenFOAM` | `snappy` |
|---|---|---|---|
| `groves_1989_dtrc_shd1298_darpa_suboff_geometry` | **geometry** definition | **0** | **0** |
| `huang_1989_dtrc_shd1298_02_darpa_suboff_experiments` | **experiments** | **0** | **0** |
| `roddy_1990_dtrc_shd1298_08_darpa_suboff_captive_model` | captive-model tests | **0** | **0** |
| `liu_1998_crdknswc_hd1298_11_darpa_suboff_data_summary` | data summary | **0** | **0** |

**All four are experimental and geometric reports. None is a CFD setup, in OpenFOAM or anything
else.** The six mesher tokens are zero in all four (§0.1 swept two of them explicitly; this lane
swept all four for `OpenFOAM` and `snappy`).

**Our value** throughout: `verification/campaign/SUBOFF_A1_PREREGISTRATION.md` — **a DRAFT, not
frozen, no compute has run under it** — with the mesh recipe at
`cases/navier_class/SUBOFF_A1/build_suboff_a1_mesh.py`.

| parameter | published value + SOURCE LINE | our value | same? | deviation reason (registered) |
|---|---|---|---|---|
| **the OpenFOAM setup itself** | 🔴 **NOT RETRIEVED, AND THE ATTEMPT IS ON RECORD.** Type 209 paper and Robertson validation are **named in Sanaa's 2026-09-12 directive (line 259)**. The sibling cfd lane searched for them, **swept the entire HPC-TC tree**, and **the identified Type 209 paper returns HTTP 403** (commit `799c88e7`) | `build_suboff_a1_mesh.py` | **NOT RETRIEVED** | 🔴 **NOTHING WAS SUBSTITUTED AND NO DICTIONARY WAS RECONSTRUCTED.** A plausible SUBOFF recipe wearing a citation is exactly what Sanaa's rule refuses. The honest answer is that this lab has no published OpenFOAM SUBOFF setup |
| geometry | **Groves 1989 (DTRC/SHD-1298-01)** — the hull and fairwater definition, title-page verified | hull + fairwater (sail), zero incidence | **SAME** — geometry is the one thing genuinely published | — |
| Reynolds number | 🔴 **NOT PUBLISHED in the lab's holdings.** `SUBOFF_A1_PREREGISTRATION.md` §2.2: the Groves report is a *geometry* report, and searching it for `Reynolds`, `knots`, `ft/sec` returns **one hit, in a sentence about a Reynolds *stress* measurement station** | **Re_L = 1.2e7** | **NOT PUBLISHED** | ✅ **REGISTERED, and registered honestly**: §2.2 records this as *"the lab's own inherited working condition, not a source value"*. The Crook 1990 resistance report is **NOT OBTAINED** — `.url` stub only |
| U∞, ρ, ν | **NOT PUBLISHED** in the holdings | `magUInf`, `lRef`, `rhoInf` inherited with Re_L | **NOT PUBLISHED** | same registered reason |
| mesher | **NOT RETRIEVED** | **snappyHexMesh** — `build_suboff_a1_mesh.py:126` emits the dict, `:100` the `blockMeshDict` | **NOT RETRIEVED** | the Type 209 setup is described in the directive as "**OpenFOAM v7 with snappy layers**", so a comparison would be possible **if the paper were obtained** |
| `relativeSizes` | **NOT RETRIEVED** | **`true`** — `build_suboff_a1_mesh.py:171` | **NOT RETRIEVED** | 🔴 **worth the supervisor's eye regardless of any source**: this is the setting PPTC PRISM-A2 and DrivAer R5 are both moving **away from**, and SUBOFF A1 still carries it. **Stated as an observation, not proposed as a change** — A1 is a draft and its own supervisor owns it |
| `nSurfaceLayers` | **NOT RETRIEVED** | parameterised `nlay`, applied to `hull` and `sail` — `:172` | **NOT RETRIEVED** | — |
| `expansionRatio` | **NOT RETRIEVED** | **1.2** — `:173` | **NOT RETRIEVED** | matches Wolf Dynamics' published 1.2 and Klerebrant Klasson's published 1.2, by coincidence rather than by citation |
| `minThickness` | **NOT RETRIEVED** | **0.02**, relative — `:175` | **NOT RETRIEVED** | relative units; the same coupled trap R5 §2.2 registers |
| `featureAngle` | **NOT RETRIEVED** | not read by this lane | **NOT RETRIEVED / NOT VERIFIED** | — |
| wall treatment | **NOT RETRIEVED** | **`nutUSpaldingWallFunction`** on every wall patch, gated by Gate W — `SUBOFF_A1_PREREGISTRATION.md` §374, §473-475 | **NOT RETRIEVED** | ✅ **REGISTERED**: A1 does **not** inherit R1b's `nutkWallFunction` + `omegaWallFunction`, because the family refines y⁺ from 25 down to ≈11 and high-Re wall functions are invalid there. 🔴 **Note this is the opposite of what DrivAer's case on disk does (§1.5) — SUBOFF A1 got this right and DrivAer did not** |
| y⁺ gate | **NOT RETRIEVED** | **y⁺ < 300 everywhere, at every level**, reported per level | **NOT RETRIEVED** | registered ceiling catches an under-resolved wall; the all-y⁺ wall function means refinement cannot walk the family out of validity as R1b's did |
| turbulence model | **NOT RETRIEVED** | k-ω SST (incompressible `simpleFoam` field set `p U k omega nut phi`, §529) | **NOT RETRIEVED** | — |
| steady / transient | **NOT RETRIEVED** | steady `simpleFoam` | **NOT RETRIEVED** | — |
| mesh quality gates | **NOT RETRIEVED** | `checkMesh -allGeometry -allTopology` at every level; wall-patch `max(face area)/min(face area) ≤ 500`; ≥ 8 cells across the 1.311 mm sail TE base | **NOT RETRIEVED** | 🔴 A1 §1.1 records that **plain `checkMesh` printed `Mesh OK.` with rc = 0 on all three R1b levels while the full check set failed 1, 2 and 2 checks** — and that `checkMesh` returns rc = 0 even when checks fail. **Our gate is stricter than any published practice this lab has seen** |
| cell count | **NOT RETRIEVED** | A1 family anchored on the measured T26 precedent (13.97 M → 10.09 M, commit `f386be2fb`) | **NOT RETRIEVED** | — |
| published results to compare against | **Huang 1989, Roddy 1990, Liu 1998** — the experimental data, which IS published and IS held | Gate D2: `CT = R_T / (½ ρ U² S_wetted)` at Re_L = 1.2e7 | **SAME** — the *experiment* is available even though the *setup* is not | **this is the important distinction for SUBOFF: we can validate against the experiment; we cannot reproduce anybody's CFD** |

---

# 5. WHAT THIS DOCUMENT SURFACED THAT WAS NOT ALREADY ON RECORD

**Everything in this section is this lane's own measurement tonight, not lifted.**

### 5.1 🔴 DrivAer's wall function on disk contradicts DrivAer's frozen registration

`DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md` §3 states that the wall treatment held
constant across the arm is **`nutUSpaldingWallFunction` on the `".*"` vehicle block**, with
`nutkWallFunction` only on `floorNoSlip`. §2.1 builds an argument on it: *"that is
`nutUSpaldingWallFunction`, **which this lab already runs on every DrivAer vehicle patch**."*

**Measured by this lane:**

- `verification/runs/navier_class/DRIVAER/r2_medium/0.orig/nut` — the `".*"` block reads
  **`type nutkWallFunction;`**. This is the case `build_r5.sh` stages from (`SRC=$D/r2_medium`).
- `cases/navier_class/DRIVAER/mesh/write_solver_case.py:137-138` — the default block written for
  `nut` is **`nutkWallFunction`**, with `floorNoSlip` overridden to the same thing.
- This lane read `build_r5.sh` and found **no step that rewrites `0.orig/nut`**; it copies
  `system/` dictionaries only.

**Why it matters, and it is not bookkeeping.** `nutkWallFunction` is a high-Re form, valid only
above roughly y⁺ 30. `nutUSpaldingWallFunction` is valid at arbitrary y⁺. **Both published DrivAer
sources use the Spalding form** — `[OCC]` in its `0.orig/nut` as a case file, `[ML]` in its prose.
R5's Y1 gate sits at the bottom edge of y⁺ 30-100 with no slack (R5 §4.2), which is **precisely the
regime where the two wall functions diverge.**

**What this lane is NOT claiming.** R5 has had **no compute**, so no gate is affected and no verdict
is in question. This lane did not exhaustively search for a stage step that might convert the file
before a solve. **This is reported to the supervisor as a discrepancy to check personally, not as a
verdict.** It sits inside `SUPERVISION_CHARTER` §3 check 1 — a measurement-script difference read as
a diff — and is the supervisor's, undelegated.

### 5.2 The occDrivAer case moves four DrivAer rows off "unsourced" — but not the mesher rows

🔴 **First, the limit: it moves NO mesher row, because it ships no mesher dictionary (§0.3).** The
exact-match case publishes its conditions, BCs, schemes, relaxation and solver controls, and
distributes its mesh as **cells, not as a recipe.** That is the sharpest possible statement of the
reproducibility gap: **even a published, hashed, runnable OpenFOAM case on our own geometry does not
tell us how its mesh was asked for.**


Before tonight these rows had our value and no published counterpart. They now have one, from a
case file on our own geometry at our own velocity and viscosity:

| row | before | after |
|---|---|---|
| ν = 1.507e-05 | a 0.3 % deviation from a paper, needing a reason | **character-for-character identical to the case file.** No deviation exists |
| steady RANS | our cost compromise, no published counterpart | **published practice on this exact case** (§B) |
| y⁺ floor of 30 | Sanaa's window vs a **lab-derived** ≈22 — a conflict resting on a derived number | **the case's README publishes "y⁺ > 30" in words.** Her floor is corroborated |
| blockage 0.25 % | a paper's round number | **derived from the case's own `blockMeshDict` and `Aref`: 0.2466 %.** Two independent routes agree |

### 5.3 Four DrivAer rows are newly UNREGISTERED against a case file

Each of these differed from a *paper* before and could be argued as a modelling choice. Each now
differs from a **dictionary** on our own geometry: domain extents and blockage (**D1**), turbulence
convection scheme (first-order upwind in **both** published case files, second-order in ours),
turbulence relaxation (0.6 vs our 0.9), and inlet turbulence (Tu 0.26 % / viscRatio 5 vs our
0.1 % / 1). **None of them is on record with a reason.**

### 5.4 The published sources are not uniformly better than us, and three rows prove it

This document would be dishonest if it read as "adopt the published value everywhere".

- **`relativeSizes true`** is what Wolf Dynamics publishes and what poisoned our PPTC mesh by 95.53×.
  R5 moving to `false` is **departing from published practice, correctly.**
- **`residualControl`** is published by Wolf Dynamics at 1e-3 and would **break CLAUDE.md rule 4's
  `last == endTime` clause.** We deliberately have none, and occDrivAer deliberately has none either.
- **Achieved layer coverage** is published by **nobody**, and we gate on it. **Absence of a reported
  failure is not evidence of success.**

### 5.5 What this lane did NOT verify, stated plainly

- Our emitted R5 values for `nCellsBetweenLevels`, `nGrow`, `maxThicknessToMedialRatio`,
  `nLayerIter`, `nRelaxedIter`, `slipFeatureAngle`, `featureAngle` and `laplacianSchemes`, and
  whether our `omegaWallFunction` sets `blended`. Marked **NOT VERIFIED** in the rows, never filled.
- Whether any stage step converts `0.orig/nut` before an R5 solve (§5.1).
- The Mach numbers on either side of the M6 comparison. Both thermodynamic states are quoted; neither
  Mach is derived here.
- **The entire PPTC table**, which is lifted from commit `766c1b26b` and attributed, not re-measured.
  This lane's independent contribution there is the §0.1 token sweep, which reproduces that
  document's zero-count claim from the same corpus.
- **Every `[lifted]` row** in §1 and §C, from commit `e0fbdba3` and from the R5 registration.
- Whether the sibling lane's retrieval is complete — three trees had landed when this lane read the
  directory. **No PPTC and no SUBOFF case tree had landed, and this lane did not start a retrieval.**
- **Two rows of the §0.4 stack table** — ESI marine propeller (0.794) and high-lift CRM ONERA (1.600).
  They are the sibling lane's measurement at commit `799c88e7`; **this lane did not open those cases.**
  The other four this lane recomputed from the shipped dictionaries and they reproduce exactly.
- **The Wolf Dynamics version reading** (page says 9, headers say 7, shipped log says
  `Build : 9-6adb71a2e61d`) and **its non-stationary coarse `Cd = 0.2912`**, both the sibling lane's.
  **Its six `type wall;` farfield patches this lane DID verify by reading `blockMeshDict` directly.**
- **The `[OCCR]` attribution itself is a limit, not a value.** Those dictionary values are real and
  hashed, but they come from the **rotating-mesh LES sibling**, not from the static case we match.
  **No `[OCCR]` cell is evidence about how the 65 / 110 / 236 M static meshes were built.**

### 5.6 The proposals, numbered for the supervisor — DrivAer only, and NOTHING IS APPLIED

R5 is **frozen** and rule 2 closes its gates, thresholds, cap and labels. Every item below is a
**disclosure addendum**, a **successor arm**, or a **question**. None alters R5.

| # | row | proposal | who decides |
|---|---|---|---|
| **D1** | domain extents + blockage | 🔴 Our domain is 2.2× narrower, 1.67× shorter and 2.8× shorter fore-and-aft than the published case on our geometry, giving **3.88× its blockage**. Propose a **disclosure addendum** and a blockage-sensitivity successor. **Not a change to R5's frozen domain** | supervisor (disclosure); **Sanaa** if the domain moves |
| **D2** | y⁺ floor | The earlier conflict (her 30 vs a lab-derived 22) **weakens**: occDrivAer publishes "y⁺ > 30". Propose **recording the corroboration** and withdrawing the earlier "surface the conflict to Sanaa" framing. **Her window stands either way** | supervisor |
| **D3** | layers 8, ratio 1.11 | 🔴 Ours is now outside **two** published sources on ratio (1.2 in **[WD]**'s dict, 1.2-1.4 in **[ML]**'s prose) and **four times** the layer count of the case on our geometry (**2**). Propose a **disclosure addendum** stating both. **Sanaa's 8 layers is her instruction and this lane does not move it** | supervisor (disclosure); **Sanaa** if layers change |
| **D4** | cell count | Propose the certificate **state the ratio to [OCC] explicitly** — 3.3× below its coarsest, 11.8× below its fine — so no reader infers mesh equivalence | supervisor |
| **D5** | schemes, relaxation, outlet BC | Propose a single **disclosure addendum** listing the five rows where we differ from both published case files with no reason on record | supervisor |
| **D6** | initialisation and inlet turbulence | occDrivAer publishes a complete initialisation recipe (`potentialFoam -initialiseUBCs` then `applyBoundaryLayer -ybl "0.0450244"`) and its own `Tu`/`viscRatio`. Propose **adopting these in a successor arm**, not in R5 | supervisor |
| **D7** | §5.1, the wall function | **Refer to the supervisor for a personal check.** Not a proposal — a discrepancy between a frozen registration and the case it stages from | **supervisor, personally** |
| **D8** | 🔴 **WHICH published tree DrivAer should be registered against** | **The sibling lane recommends `[WD]` Wolf Dynamics**, because it is the only complete self-contained tree and **its own STL geometry ships, so a run from it carries no geometry deviation at all.** **This lane reads it differently and says so rather than relaying agreement it does not hold:** `[WD]` is the **original TUM DrivAer, a HALF model at 30 m/s with a different viscosity** (§A.2) — reproducing it exactly reproduces **a different experiment from the one our gate C2 is anchored on**. `[OCC]` is our geometry, our velocity, our viscosity and our solver, and **ships no mesher dictionary**. **The two trees are good for different things: `[WD]` for snappyHexMesh practice, `[OCC]` for conditions, numerics and BCs.** **Registering either as *the* reference is a supervisor's ruling, not a lane's, and the two lanes disagree — that disagreement is the useful part** | **supervisor**, with the disagreement on record |

**No proposal is made for PPTC** (its own document at `766c1b26b` carries six, and they are that
lane's to press), **none for M6** (Sanaa has ruled), **and none for SUBOFF** (Sanaa has ruled, and
there is no retrieved source to propose from).

---

## 6. COST

No solver launched. This document is a synthesis of two committed lab tables, five committed ingests,
three retrieved case trees and targeted reads of files already in the repository, plus one token
sweep of this lane's own.

**Measured: 4.6 core-minutes**, single rank, from this lane's own elapsed tool time.
**Derived, not measured: ≈ \$0.0039** at the owner-stated \$0.0513/core-h — **the box cannot read its
own billing** (`COMPUTE_BUDGET_CHARTER.md` §5).

**No pre-registered estimate exists for a synthesis task**, so no calibration ratio under CLAUDE.md
rule 12 is claimable, and none is claimed.

---

*Compiled by a cfd `lab-lane` under `cfd-supervisor`, 2026-09-13. No solver launched. No frozen file
edited. No gate, threshold, cap or label altered. Nothing sent, filed, uploaded or registered outside
this box (rules 7, 8). Lifted rows are attributed to the lane and commit they came from and are not
presented as this lane's measurement; rows this lane could not verify are marked NOT VERIFIED rather
than filled.*
