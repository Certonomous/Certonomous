# Curriculum D6R3 — **REVISION R2. DRAFT, NOT FROZEN.** The CRM wing at Mach 0.85, published setup VERBATIM, with the owner's within-run checks built in

> **STATUS: DRAFT, REVISION R2. NOT FROZEN. NO GATE IS IN FORCE. NO COMPUTE IS AUTHORISED.**
> Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`, who freezes it personally.
> **This item has burned 0 core-min and started no container.** No solver was run for this
> revision; every number below is read from artefacts already on disk or from published files.
> **Nothing here is sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7 —
> **SUBMISSIONS PARKED**). **No agent message is Sanaa's consent** (rule 9).

**Supersedes:** revision R1 at commit `9847ffc30162cdd73c0a582d82a1f8c3cd063353`. R1's operating
point (the MACH tutorial wing at M 0.288) is **STRUCK**; its text is preserved unrewritten in
**APPENDIX S** and in that commit (rule 6).

**Item id:** `D6R3`. **Parent:** `curriculum_D6R2C/PREREGISTRATION.md` (frozen `7f685867d`, v1.4).
**Registers under:** `docs/dafoam/SHAPE_OPTIMIZATION_STANDING_RULES.md` rules **1–32**;
`DAFOAM_CHARTER.md` **§22**; `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
**§G** (the published-setup rule, line 239).

---

## 0. THE RULING THIS REVISION CARRIES

Sanaa, 2026-09-13, relayed to this lane by `dafoam-supervisor`: *"for mach 0.85 it must follow the
setup verbatim and we must incorporate the within run checks of the instructions to ensure the
result we get is not from a mesh artefact."*

Two requirements, and this revision is organised around them:

1. **VERBATIM** — §2 is a **paper-value | our-value table**, one row per mesh, warp, DV-
   parameterisation and solver parameter, each citing the published **file and line**. Rows match by
   default. **Every deviation is a separate, numbered, dated entry in §3 with its reason.** A row
   with no published line to cite is itself a deviation, because it means we invented it.
2. **WITHIN-RUN CHECKS** — §9 registers **six instruments that run DURING the optimisation**, one
   per rules 6–11. **Every one has been written and driven against a known-bad input and shown to
   FIRE.** 48 controls, 48 `PASS`, 0 `FAIL`, at `D6R3_INRUN_SELFTEST.json`. A guard that has never
   said no is not a guard.

**AND A BLOCKING PRECONDITION.** §7 registers arm **`P0`** — one primal and one adjoint on the
published CRM mesh, measured, before anything else runs. Until `P0` reads `PASS` every arm after it
is **`PENDING`** and the cost model is **explicitly labelled untested**.

---

## 1. THE PUBLISHED SETUP, AND ITS PROVENANCE

| field | value |
|---|---|
| repository | `https://github.com/DAFoam/tutorials.git` |
| local clone | `/home/ubuntu/dafoam-tutorials` — **already on disk; nothing was fetched for this draft** |
| HEAD | `d3b7e38b058aba2a98a74092e15c41ec455c570d`, 2026-05-16 15:58:25 -0500 |
| the case | **`CRM_Wing/`** |
| `runScript.py` | md5 **`0de915d21166a91a9a54b37ab11214cf`** |
| `genWingMesh.py` | md5 **`af9b63c2a22886b40c2309b298288cb8`** |
| surface geometry | `CRM_surfMesh.cgns`, `preProcessing.sh:17` fetches it from `https://github.com/dafoam/files/releases/download/v1.0.0/`; copies are on disk under `/home/ubuntu/certonomous-runs/act9-crm_wingbody-*/` and `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s2bpv/` |
| supplementary published source | He, Mader, Martins & Maki, **AIAA Journal 2020**, §3.1 and **Table 4** — the published DAFoam **multipoint** wing setup |
| supplementary published source | `UBend_Channel/runScript_meshQualityConstraint_v2.py`, md5 `0d97cb5e619bffe19c8dcc2759c07d09` — the published DAFoam **mesh-quality constraint** |

**Title-page verification (`CLAUDE.md` rule 15)** was performed in R1 by independent `pdftotext -f 1
-l 1` extraction of page 1 of each PDF, read against its printed title, authors and venue — never by
filename, file type or hash. Carried forward unchanged; the three md5s are in APPENDIX S.

### 1a. **THE LAB HAS ALREADY RUN THIS EXACT PUBLISHED PRODUCER, WITH ADJOINTS, AND R1 DID NOT KNOW IT**

**This is the most important measured fact in the revision and it changes the cost model by a
factor of seventeen.**

R1 §15e stated, on the A6 record's authority, that *"the CRM adjoint has never run on this box"*.
**That statement is true of A6's 579,072-cell mesh and FALSE of the case.** Measured by this lane,
2026-09-13, by reading the logs:

| artefact | `Main iteration` | `KSP Residual` | what it is |
|---|---|---|---|
| `CURRICULUM-D8-a6-twist-opt/opt.log` | **475** | **475** | a CRM twist optimisation with real adjoints |
| `CURRICULUM-D8R-a6-twist-opt-conv/O-P_20260827T223101Z_1595223.log` | **1,080** | **1,080** | the graded, FD-verified successor |
| `CURRICULUM-D8R…/O-S_…log` | **1,521** | **1,521** | the SHIPPED row of the same |
| all four A6 logs | **0** | **0** | the 579,072-cell mesh — never attempted |

`D8R` ran **`DARhoSimpleCFoam` on the CRM wing at M 0.8497, on `runScript.py` md5 `0de915d2…` —
byte-identical to the published `CRM_Wing/runScript.py` I hashed above** — at **41,760 cells**,
4 ranks, and its endpoint adjoint passed a finite-difference table: **20 graded components, 20
`PASS`, 0 `GATE FAIL`, 0 sign flips** (`curriculum_D8R/RESULTS.md:40`).

**Consequence.** R1's gradient figure of 529.1 core-min was an extrapolation from a different wing
at a different Mach. §11 replaces it with a **measurement on this wing, this solver, this Mach, this
producer**, and the item's registered total falls from R1's ≈425,000 core-min to **24,900**. That
correction is recorded here rather than quietly applied.

### 1b. **THE GRID FAMILY IS ALSO ALREADY MEASURED — `D8G` DID THE COARSENING ARITHMETIC ON THE REAL TARBALL**

`cases/dafoam/ladder-a/A6/curriculum_D8G/PREREGISTRATION.md` §2.1 measured, on the archived
`CRM_surfMesh.cgns.tar.gz`, the surface quad-face count after each successive `cgns_utils coarsen`:

| coarsen count | surface quad faces | ratio to previous |
|---|---|---|
| **c0** (as shipped) | **44,544** | — |
| **c1** (what `preProcessing.sh:20` does) | **11,136** | **4.000** |
| **c2** | **2,784** | **4.000** |
| **c3** | **696** | **4.000** |
| c4 | 188 | **3.702 ← BREAKS**, excluded |

Two independent confirmations, both on disk: `11,136 × 52 = 579,072`, the archived recipe's own
measured cell count (`A6-crm-wing/logMeshGeneration.txt:478`, `Mesh region0 size: 579072`, at c1
with `N = 53`); and `2,784 × 15 = 41,760`, the graded D8/D8R mesh at c2 with `N = 16`.

**D6R3 reuses this measured coarsening rather than re-deriving it** (§4). **`c4` is excluded and the
reason is inherited: it is not a factor-2 coarsening and must never be used as one.**

---

## 2. THE VERBATIM TABLE — **58 ROWS, 46 VERBATIM, 12 DEVIATIONS**

Every row is read from the published file by this lane. **`=` means adopted unchanged.
`Δn` names a numbered deviation in §3.** Line numbers are `grep -n` positions in the files hashed
in §1.

### 2a. Flow condition and fluid (8 rows, 8 verbatim)

| # | parameter | published value | source file:line | ours |
|---|---|---|---|---|
| 1 | `U0` | `295.0` m/s | `CRM_Wing/runScript.py:24` | **=** |
| 2 | `p0` | `101325.0` Pa | `:25` | **=** |
| 3 | `T0` | `300.0` K | `:27` | **=** |
| 4 | `nuTilda0` | `4.5e-5` | `:26` | **=** |
| 5 | `aoa0` | `2.11031707` deg | `:29` | **=** |
| 6 | `A0` | `3.407014` m² | `:31` | **=** |
| 7 | `mu`, `Pr`, `molWeight`, `Cp` | `1.8e-5`, `0.7`, `28.97`, `1005` | `constant/thermophysicalProperties:42,43,33,37` | **=** |
| 8 | **derived Mach** | `295/√(1.4·287·300) = 295/347.189 = ` **`0.849678`** | derived from rows 1, 3 | **=** |

### 2b. Turbulence and wall treatment (5 rows, 3 verbatim, **2 in deviation Δ1**)

| # | parameter | published value | source | ours |
|---|---|---|---|---|
| 9 | RAS model | `SpalartAllmaras`, `turbulence on`, `Prt 1.0` | `constant/turbulenceProperties:21-25` | **=** |
| 10 | `nuTildaMin` | `1e-16` | `:24` | **=** |
| 11 | `nuTilda` wall BC | `fixedValue uniform 0.0` | `0.orig/nuTilda` | **=** |
| 12 | `primalBC.useWallFunction` | **`True`** | `runScript.py:42` | **Δ1** → `False` |
| 13 | `nut` wall BC | **`nutUSpaldingWallFunction`** | `0.orig/nut:24` | **Δ1** → `nutLowReWallFunction` |

### 2c. Mesh recipe and extrusion (14 rows, 12 verbatim, **2 in Δ1**)

| # | parameter | published value | source | ours |
|---|---|---|---|---|
| 14 | pipeline | `tar -xvf` → `cgns_utils coarsen surfMesh.cgns` → `python genWingMesh.py` → `plot3dToFoam -noBlank` → `autoPatch 45 -overwrite` → `createPatch -overwrite` → `renumberMesh -overwrite` | `preProcessing.sh:20-25` | **=** |
| 15 | `inputFile` | `surfMesh.cgns` | `genWingMesh.py:3,8` | **=** |
| 16 | `fileType` | `CGNS` | `:9` | **=** |
| 17 | `unattachedEdgesAreSymmetry` | `True` | `:10` | **=** |
| 18 | `outerFaceBC` | `farfield` | `:11` | **=** |
| 19 | `autoConnect` | `True` | `:12` | **=** |
| 20 | `families` | `wall` | `:14` | **=** |
| 21 | **`N`** | **`53`** (52 cell layers) | `:18` | **Δ1** → `105` (104 layers) |
| 22 | **`s0`** | **`1.0e-4`** m | `:19` | **Δ1** → `1.35e-6` m |
| 23 | `marchDist` | `25 × 3.758151 = 93.953775` | `:20` | **=** |
| 24 | `ps0`, `pGridRatio`, `cMax` | `-1.0`, `1.1`, `5.0` | `:25-27` | **=** |
| 25 | `epsE`, `epsI`, `theta` | `1.0`, `2.0`, `3.0` | `:31-33` | **=** |
| 26 | `volCoef`, `volBlend`, `volSmoothIter` | `0.16`, `0.0005`, `30` | `:34-36` | **=** |
| 27 | `kspRelTol`, `kspMaxIts`, `kspSubspaceSize` | `1e-4`, `50`, `50` | `:37-39` | **=** |

### 2d. Solver, schemes and linear algebra (14 rows, 12 verbatim, **2 deviations**)

| # | parameter | published value | source | ours |
|---|---|---|---|---|
| 28 | `solverName` | `DARhoSimpleCFoam` | `runScript.py:35` | **=** |
| 29 | `primalMinResTol` | `1.0e-8` | `:36` | **=** |
| 30 | **`primalMinResTolDiff`** | **ABSENT from the published CRM file** — the MACH wing sets `1e3` (`MACH_Tutorial_Wing/runScript_AeroOnly.py:37`) | — | **=** (absent; DAFoam's own default stands, and `P0` **RECORDS** it) |
| 31 | `ddtSchemes` | `steadyState` | `system/fvSchemes:20` | **=** |
| 32 | `gradSchemes` | `Gauss linear` | `:25` | **=** |
| 33 | `div(phi,U)` | `Gauss linearUpwindV grad(U)` — **not** `bounded` | `:31` | **=** |
| 34 | **`div(phid,p)`** | **`Gauss limitedLinear 1.0`** — the transonic pressure-flux scheme | `:35` | **=** |
| 35 | all other `div` | `Gauss upwind` / `Gauss linear` as listed | `:32-43` | **=** |
| 36 | `laplacianSchemes`, `snGradSchemes`, `interpolationSchemes` | `Gauss linear corrected`, `corrected`, `linear` | `:53,58,48` | **=** |
| 37 | `wallDist` | `meshWave` | `:62` | **=** |
| 38 | `nNonOrthogonalCorrectors` | **`0`** | `system/fvSolution:20` | **=** |
| 39 | linear solvers | `(p\|p_rgh\|G)` GAMG/GaussSeidel `relTol 0.1 tolerance 0`; `(U\|T\|e\|h\|nuTilda\|k\|omega\|epsilon)` smoothSolver/GaussSeidel `relTol 0.1 nSweeps 1`; `Phi` `$p relTol 0 tolerance 1e-6` | `:25-47` | **=** |
| 40 | relaxation | fields `(p\|rho) 1.0`; equations `p 1.0`, `(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega) 0.80` | `:51-59` | **=** |
| 41 | `potentialFlow.nNonOrthogonalCorrectors` | `20` | `:64` | **=** |

### 2e. `daOptions` (8 rows, 6 verbatim, **2 deviations**)

| # | parameter | published value | source | ours |
|---|---|---|---|---|
| 42 | `designSurfaces` | `["wing"]` | `runScript.py:34` | **=** |
| 43 | `function.CD` / `.CL` | `type force`, `source patchToFace`, `patches ["wing"]`, `directionMode parallelToFlow` / `normalToFlow`, `patchVelocityInputName patchV`, `scale 1/(0.5·U0²·A0·ρ0)` | `:44-62` | **=** |
| 44 | `adjStateOrdering` | `cell` | `:63` | **=** |
| 45 | `adjEqnOption` | `gmresRelTol 1.0e-6`, `pcFillLevel 1`, `jacMatReOrdering natural`, `gmresMaxIters 2000`, `gmresRestart 2000` | `:64-71` | **=** |
| 46 | `normalizeStates` | `U: U0`, `p: p0`, `T: T0`, `nuTilda: 1e-3`, `phi: 1.0` | `:72-78` | **=** |
| 47 | `checkMeshThreshold` | `maxAspectRatio 2000.0`, `maxNonOrth 75.0`, `maxSkewness 5.0` | `:79-83` | **=** |
| 48 | **`transonicPCOption`** | **`2`** | `:84` | **Δ2** → `1` |
| 49 | `inputInfo` | `aero_vol_coords: volCoord`; `patchV: patchVelocity`, `patches ["inout"]`, `flowAxis "x"`, `normalAxis "z"` | `:86-95` | **=** |

### 2f. Warping (2 rows, 1 verbatim, **1 deviation**)

| # | parameter | published value | source | ours |
|---|---|---|---|---|
| 50 | `meshOptions` | `{gridFile: os.getcwd(), fileType: "OpenFOAM", symmetryPlanes: [[[0,0,0],[0,1,0]]]}` — **every IDWarp option left at its default** | `:97-102` | **=** on `gridFile`, `fileType`, `symmetryPlanes`; **every default named EXPLICITLY** (§9.6) |
| 51 | `evalMode` | not set → IDWarp default **`"fast"`** (`UnstructuredMesh.py:136`) | — | **Δ3** → `"exact"` |

### 2g. Design variables, FFD and constraints (7 rows, 6 verbatim, **1 deviation**)

| # | parameter | published value | source | ours |
|---|---|---|---|---|
| 52 | FFD lattice | `FFD/wingFFD.xyz`, plot3d header **`12 8 2` = 192 control points** | `FFD/wingFFD.xyz:2`, used at `runScript.py:120` | **=** |
| 53 | reference axis | `nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="j")` → `nRefAxPts = 8`; `rot_y`; **root twist NOT free** → **7 twist DVs** | `:146-154` | **=** |
| 54 | shape DVs | `pts = DVGeo.getLocalIndex(0)`, `pts[:,:,:].flatten()`, `PointSelect("list", …)`, `nom_addLocalDV(dvName="shape", pointSelect=PS)` → **192 shape DVs**. **The displacement axis is NOT specified in the published file**; the installed pyGeo default stands. | `:157-160` | **=**; **`P0` RECORDS the effective axis — `NOT MEASURED` at this draft** |
| 55 | DV bounds / scalers | `twist [-10, 10]` scaler `0.1`; `shape [-1, 1]` scaler `10.0`; `patchV [U0, 0]`–`[U0, 10]` scaler `0.1` | `:200-202` | **=** |
| 56 | thickness / volume | `nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=25, nChord=30)` bounds `[0.5, 3.0]`; `nom_addVolumeConstraint("volcon", …)` lower `1.0`; `leList`/`teList` built from `LE_pt (0.01,0.01,0)`, `break_pt (0.848,1.119,0)`, `tip_pt (2.855,3.755,0)`, chords `1.689 / 1.036 / 0.390` at 1 % and 99 % | `:171-185`, `:206-207` | **=** |
| 57 | LE/TE | `nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")`, `("tecon", …, "iHigh")`, both `linear=True` | `:187-188`, `:208-209` | **=** |
| 58 | objective / lift constraint | `add_objective("scenario1.aero_post.CD", scaler=1.0)`; `add_constraint("scenario1.aero_post.CL", equals=CL_target, scaler=1.0)`; `CL_target = 0.5`; trim by `optFuncs.findFeasibleDesign([...CL], ["patchV"], targets=[CL_target], designVarsComp=[1])` | `:28`, `:204-205`, `:268` | **Δ4** → three conditions |

**ROW COUNT: 58. VERBATIM: 46. DEVIATIONS: 13** (rows 12, 13, 21, 22, 48, 51, 58 carry Δ1–Δ4;
Δ5–Δ13 in §3 are **additions**, i.e. rows with **no published line to cite**, which §0 requires be
registered as deviations in their own right).

### 2h. Two published facts recorded rather than silently corrected

- **`0.orig/U:20` carries `internalField uniform (100 0 0)` while `U0 = 295.0`.** DAFoam's
  `primalBC` overwrites the *boundary* at runtime, not the *internal initial field*. **This is the
  published file's own value and it is adopted verbatim**; it is named here because a reader who
  finds `100` in a M 0.85 case is entitled to know it is the published initial condition, not an
  error introduced here. Its only effect is on the transient to the fixed point.
- **`system/decomposeParDict:18` sets `numberOfSubdomains 72`.** That is the published rank count
  and it is adopted (§10). The box now reads **96 cores**, so 72 ranks fit.

---

## 3. THE DEVIATION REGISTER — thirteen numbered, dated entries

> **Every entry is dated 2026-09-13 and is a DRAFT proposal until the freeze.** Her instruction is
> that verbatim is the baseline and any deviation is registered with its reason; these are those
> registrations.

### **Δ1 — WALL-RESOLVED, y⁺ ≈ 1.** Rows 12, 13, 21, 22. *(her rule 2)*

- **What changes:** `useWallFunction True → False`; `nut` wall BC `nutUSpaldingWallFunction →
  nutLowReWallFunction`; `s0 1.0e-4 → 1.35e-6`; `N 53 → 105`.
- **Why:** her rule 2 — *"Wall functions make friction a strong function of y⁺, and y⁺ drifts under
  warping."* **Measured on this exact case:** D6R2's deformed-versus-fresh comparison ran at y⁺
  medians **247 versus 223**, a 10.8 % drift produced by warping alone (`DAFOAM_CHARTER.md` §22.3).
- **The sizing, from a MEASUREMENT on the published mesh.** `A6-crm-wing/run_model_run1.log`, the
  converged tail of the baseline primal at `s0 = 1.0e-4` on the published 579,072-cell mesh:
  **y⁺ min `7.648`, max `73.826`, mean `34.587`.** *(Corroboration, and it is a good one: He et al.
  AIAAJ 2020 `:882` reports **average y⁺ 33.7** for the sibling published wing — **2.6 %** from our
  measured 34.587.)* Since `y⁺ ∝ y_wall`, `s0` for **max** y⁺ = 1 is `1.0e-4 / 73.826 =`
  **`1.3546e-6 m`**; for **mean** y⁺ = 1 it is `2.891e-6 m`. **The conservative (max) figure is
  registered: `s0 = 1.35e-6 m`**, predicting max y⁺ `0.998`, mean y⁺ `0.467`.
- **The cell consequence, exactly:** layers double, `52 → 104`, because the march is geometric over
  93.954 m — `ln(74)/ln(1.17) ≈ 27` extra layers — and **the growth ratio improves from 1.2704 to
  1.1695**. **Every level's cell count doubles, exactly ×2.000.**
- **THE COST OF Δ1 IS STATED SEPARATELY SO SHE CAN SEE IT: the item goes from 24,900 to 58,800
  core-min, a factor 2.36** (§11). **Δ1 is not applied silently and is not assumed accepted.**

### **Δ2 — `transonicPCOption 2 → 1`.** Row 48.

**Because this lab MEASURED that `2` is dead code for this solver.** `DAResidualRhoSimpleCFoam.C:
172-176` accepts **only `== 1`**; every archived ONERA M6 adjoint ran with the solver's own
transonic mitigation **silently off**, and the lesson is `L-40` (`docs/LESSONS.md`, carried at
`docs/dafoam/PRIOR_WORK_INVENTORY.md` row **D-F**, *"CAUSATION NAILED by a bit-for-bit negative
control"*). **Adopting a published line the lab has already measured to be inert is adopting a
null.** Both values are recorded and `P0` reports which one was in force.

### **Δ3 — `evalMode "fast" → "exact"`.** Row 51. *(her rule 6)*

`fast` is a KD-tree approximation whose error is bounded by `errTol = 5e-4` **relative to `Ldef`**,
and `Ldef0` is computed at `kd_tree.F90:1500-1512` as **the maximum distance from the surface-node
centroid to any surface node** — of order the wing's own size. Under Δ1 the first cell is
`1.35e-6 m`; that tolerance is not obviously below it. `exact` removes the question. **Arm `W1`
measures the difference rather than assuming it** (§9.6).

### **Δ4 — SINGLE POINT → MULTIPOINT, three conditions.** Row 58.

- **What changes:** `CL_target 0.5` → `CL = 0.400 / 0.500 / 0.600`; objective
  `CD` → `J = 0.25·CD₀₄ + 0.50·CD₀₅ + 0.25·CD₀₆`; one `patchV` → three.
- **Why, and the source is published:** He et al. **AIAAJ 2020 Table 4** — three flight conditions,
  **weights 0.25 / 0.50 / 0.25**, AoA a design variable per condition, twist with root fixed, FFD
  local shape, thickness/volume/LE-TE constraints. **This is the published multipoint pattern and
  D6R2 already matched it row for row.**
- **HONEST STATEMENT:** the pattern and the case now come from **two different published sources**.
  That is a real weakening of "verbatim" and it is named rather than hidden. **The alternative —
  running the published single-point case — would not be a re-run of D6R2's multipoint problem.**
  The supervisor may strike Δ4 and register D6R3 as single-point; the cost model is unaffected to
  within the evaluation counts.

### **Δ5 — optimiser `SLSQP → IPOPT`.** *(no new line; a published BRANCH of the published file)*

`runScript.py:15` makes **`SLSQP` the default**; `:240-252` carries a complete published IPOPT
block (`tol 1.0e-5`, `constr_viol_tol 1.0e-5`, `mu_strategy adaptive`, `nlp_scaling_method none`,
`limited_memory_max_history 10`, `alpha_for_y full`, `recalc_y yes`). **Selecting the IPOPT branch
is choosing a published option, not inventing one** — but it is not the published default, so it is
registered. Reason: D6R2/D6R2C, D6R and the whole A2 ladder are IPOPT, and `OptView.hst` hot-start,
the `inf_pr` stop rules and the parent's grading vocabulary are all IPOPT-shaped.

### **Δ6 — `max_iter 100 → 25` (and `S1` at 15).** *(published value changed)*

`:243` sets `max_iter 100`. **`max_iter` is a BUDGET ON MAJOR ITERATIONS, NOT A CONVERGENCE
TOLERANCE**, and no reader may present a run that reaches it as converged (parent §1a, carried
forward). 25 is D6R2C's registered budget, kept so the two items are comparable. **A run that
reaches the cap is `GATE REACHED`, never `PASS`** (`DAFOAM_CHARTER.md` §9).

### **Δ7 — `controlDict endTime 2000 → set by arm `P1`.** *(her rule 5)*

**The arithmetic, and it is the reason D6R3 exists.** Measured from `O_mp/d6r2c_evals.jsonl` over
the 35 successful objective evaluations of D6R2C: median increment `|ΔJ| = 5.589e-04`, **last
accepted increment `1.421e-05`**, smallest `5.237e-07`. **So the drag change being chased is
`1.0e-5`.** One order tighter, as her rule requires, is **`the primal's own CD uncertainty ≤ 1.0e-6`**
— stated in the quantity of interest, not in a residual.

**What that requirement rules out, measured:** D6RF10 measured `DARhoSimpleFoam` flooring at
`p_first_uncorrected = 1.681e-05` with `CD 0.01849343377`, against `DARhoSimpleCFoam` reaching
`6.3234e-06` with `CD 0.01859195417` — **ΔCD = 9.852e-05, ten times the signal being chased.**
`P1` (§8) measures the residual→drag curve on **one solver and one mesh** and sets `endTime` to the
smallest step count at which the last 500 steps' `CD` peak-to-peak is ≤ `1.0e-6`. **The registered
upper bound for costing is 5,000 steps**; `P1` can only bring it down.

### **Δ8 — A THREE-LEVEL GRID FAMILY IS ADDED.** *(her rule 1; no published line — the published setup is a single mesh)*

§4. The construction is **not invented**: it is `D8G`'s measured `cgns_utils` coarsening (§1b)
extended so that **the published mesh is itself a member of the family**.

### **Δ9 — THE PUBLISHED MESH-QUALITY CONSTRAINT IS ADDED TO THE ADJOINT.** *(her rules 7 and 11)*

`meshQualityKS` on `faceSkewness` and `nonOrthoAngle` with `addToAdjoint: True`, and the bounds
**`skewness ≤ 4.0`, `nonOrtho ≤ 70.0`**, taken from
`UBend_Channel/runScript_meshQualityConstraint_v2.py:67-90` and `:212-213`. **It has a published
line; it is simply not in the CRM file**, so it is a deviation from the CRM setup and an adoption
from a sibling published DAFoam setup. See §9.7 for the measured reason the CRM file's own
thresholds are not enough on their own.

### **Δ10 — OPENFOAM'S `forces` FUNCTION OBJECT IS ADDED TO `controlDict`.** *(her rule 10)*

DAFoam's own `"type": "force"` returns a **total**. The pressure/viscous split comes from OpenFOAM's
`forces` function object, used in exactly this form in the published
`Airfoil_DynamicStall/…/system/controlDict:59-80`. Without it rule 10 cannot be satisfied at all.

### **Δ11 — THE PARAMETERISATION IS STAGED, `S1` then `S2`.** *(her rule 4)*

Her rule: *"fewer, smoother modes first; local high-frequency modes only after the smooth optimum is
found."* `S1` = 7 twist + 3 AoA = **10 DVs**. `S2` = 192 shape + 7 twist + 3 AoA = **202 DVs**,
started from `S1`'s optimum. The published setup runs all DVs at once.

### **Δ12 — PER-MAJOR MOVE LIMITS ARE ADDED.** *(her rule 11)*

`0.10` on the scaled `shape` ∞-norm and `0.5°` on `twist`. §9.11 explains why the literal
first-cell-height sizing she names is not usable on this case and states the arithmetic.

### **Δ13 — RULE 7's QUALITY BUDGET IS OUR OWN REFUSING INSTRUMENT, AND ITS NON-ORTHOGONALITY THRESHOLD IS 70.0, NOT THE CRM FILE'S 75.0.** *(the delegation refusal has no published line — it is ours)*

**Because the solver's own non-orthogonality clause was MEASURED never to refuse on this family.**
§9.7a: `O_mp` printed `Non-orthogonality check OK.` in **all 202** mesh-check blocks while **76** of
them measured above 70.0, worst **`80.90429398`**; `FM10` did the same in **6 of 6**, worst
**`79.21261137`**. Row 47 stays **verbatim** at `maxNonOrth 75.0` as the *solver's* abort threshold;
**our budget reads the as-run mesh and refuses in our own code at 70.0**, the published constraint
bound. The delegation refusal itself has no published line and is therefore registered as a
deviation in its own right, per §0.

---

## 4. RULE 1 — THE GRID FAMILY, BUILT SO THAT THE PUBLISHED MESH IS A MEMBER OF IT *(Δ8)*

### 4a. The three levels

Built by the **published pipeline unchanged** (`preProcessing.sh:20-25`), varying only the
`cgns_utils` coarsening depth and the two extrusion numbers, on `D8G`'s **measured** face counts.

**VERBATIM family (rows 21, 22 at their published values):**

| level | surface | layers | `s0` | **cells** | ratio | growth ratio |
|---|---|---|---|---|---|---|
| **L3** coarse | c2 (2,784) | 26 | `2.0e-4` | **72,384** | — | 1.6227 |
| **L2** medium | **c1 (11,136) — THE PUBLISHED MESH** | **52** | **`1.0e-4`** | **579,072** | **×8.000** | **1.2704** |
| **L1** fine | c0 (44,544) | 104 | `5.0e-5` | **4,632,576** | **×8.000** | 1.1264 |

**Δ1 family (wall-resolved), every level exactly ×2.000 in cells:**

| level | surface | layers | `s0` | **cells** | growth ratio |
|---|---|---|---|---|---|
| **L3** | c2 (2,784) | 52 | `2.70e-6` | **144,768** | 1.3700 |
| **L2** | c1 (11,136) | 104 | `1.35e-6` | **1,158,144** | 1.1695 |
| **L1** | c0 (44,544) | 208 | `6.75e-7` | **9,265,152** | 1.0812 |

**`r = 2.000 EXACTLY IN ALL THREE DIRECTIONS`** — two surface directions by `cgns_utils` (measured
ratio 4.000 per level, §1b), the third by doubling the layers **and halving `s0` together**. Both
cell ratios are the exact integer 8.

**THE LAYER MODEL IS VALIDATED AGAINST pyHyp'S OWN PRINTED OUTPUT, TO FIVE SIGNIFICANT FIGURES.**
Solving `s0(r^n − 1)/(r − 1) = marchDist` for D8G's L2 (`s0 = 2.0e-4`, `n = 16`, `marchDist =
93.953775`) gives **`r = 2.29932`**; D8G's own table records pyHyp's printed `Grid Ratio` as
**`2.2993`** (`curriculum_D8G/PREREGISTRATION.md` §2.2). **The model is anchored, not assumed.**

**`s0` SCALES WITH THE LEVEL, AND THE CONSEQUENCE IS NAMED, INHERITED FROM D8G §2.2:** y⁺ changes by
a factor of 2 per level, so the near-wall treatment is not identical across the family. The
alternative — fixed `s0` — was rejected there because it makes the near-wall spacing non-systematic,
and that ruling is carried forward rather than re-litigated.

### 4b. The band and the choice rule

- Measured quantity: the baseline **`J` at matched lift** (rule 3 binds the family: every level is
  trimmed to `CL = 0.400/0.500/0.600` before its drag is read).
- **BAND: a level qualifies if `|J(level) − J(L1)| / J(L1) ≤ 0.010`.** Basis: the smallest change
  this optimisation must resolve is `ΔJ = 1.0e-5` (Δ7), which on a `CD` of order 0.021 (A6 measured
  `CD = 0.02090143421526141`) is **0.048 %**; a 1 % band is **20×** looser and is therefore a
  discretisation criterion, not a noise criterion.
- **THE OPTIMISATION MESH IS THE COARSEST QUALIFYING LEVEL.** If **L3** qualifies the optimisation
  runs on L3 and L2 (the published mesh) is the rule-13 finer level — **this is the registered
  expectation and the one §11 prices**. If only L2 qualifies, the optimisation runs on the published
  mesh and L1 is the rule-13 level — the **`L2 BRANCH`**, priced separately at §11c.
- **IF NO LEVEL QUALIFIES the grid family is `GATE FAIL`, D6R3 does not proceed to an optimisation,
  and the finding is that this case has no asymptotic range at any mesh this lab can afford.**
- **NO ROACHE TRIPLE IS CLAIMED AND NO GCI IS QUOTED** (`CLAUDE.md` rule 5). The three levels select
  a mesh. A GCI at `Fs = 1.25` is reported **only if** the triple is monotone and `CONVERGING`, and
  it is reported beside the selection, never as its justification.

---

## 5. RULE 3 — TRIM IN THE LOOP, AND THE CLAUSE D6R2 FAILED

Published and adopted unchanged (rows 55, 58): AoA a design variable, lift an **equality**
constraint, `findFeasibleDesign` before iteration 1.

**WHAT IS NEW.** D6R2C **had** trim in the loop and still finished off-target: final misses
`cl04 5.539e-04`, `cl05 1.210e-03`, `cl06 2.787e-03` against a `1.0e-3` gate, corroborated to
seventeen digits by IPOPT's own `Constraint violation....: 2.7869956827836218e-03`. **Having AoA as
a DV does not guarantee matched lift; only a converged constraint does.**

- **`T1` — NO DRAG RATIO IS FORMED AT AN UNCONVERGED CONSTRAINT.** Every reported `CD` or `J`
  carries its three `|CL_i − target_i|`, and a value whose worst miss exceeds **`1.0e-4`** is
  `NOT A RESULT` for the purpose of any ratio (rule 19). `1.0e-4` is **ten times tighter** than the
  parent's `G3` and is the level at which the induced-drag contribution of a lift mismatch falls
  below `ΔJ_chased = 1.0e-5`. **This tolerance is enforced inside guard 9** (§9.9), which
  **REFUSES** rather than reporting a ratio across different lifts.
- **`T2`** — the after-protocol numbers come from an **explicit trim**, never from whatever lift the
  optimiser left.

---

## 6. THE FIFTH CAUSE CLASS, AND THE EXCLUSION TABLE *(her rule 15; §22.3)*

If `A12` or `A13` (§10) misses, the class is **mesh (warp) / parameterization (wiggles) / trim
(lift mismatch) / solver / PRODUCER**, and **the class is assigned from a measurement that EXCLUDES
the other four**:

| class | the measurement that excludes it |
|---|---|
| mesh (warp) | y⁺ medians, first-cell-height ratio, per-layer thicknesses, negative/degenerate volume count, fresh vs deformed — the §22.3 battery, already built |
| parameterization | the second-difference wiggle metric (§9.10) on the fresh and deformed surfaces |
| trim | `\|CL_i − target_i\|` on **both** sides against `1.0e-4` (`T1`) |
| solver | `P1`'s residual→drag curve evaluated at both states |
| **PRODUCER** | the **rule-18 surface-hash equality against the BASE surface** at the moment the DVs are applied, plus the wall-point fit (`cos∠`, `\|d2\|/\|d1\|`) that measured FM10's double deformation at median `0.99965` / `1.234` |

**An attribution with no exclusion measurement is a hypothesis and is labelled one.**

---

## 7. **ARM `P0` — THE BLOCKING PRECONDITION. IT RUNS FIRST AND EVERYTHING ELSE IS `PENDING` UNTIL IT PASSES.**

**Why it is mandatory.** §1a establishes that the CRM adjoint HAS run — **at 41,760 cells**. It has
**never** run at the published 579,072 (`Main iteration` and `KSP Residual` appear **zero** times in
all four A6 logs; `Global Adjoint States: 5,244,840`). **Rules 6–11 require a gradient at every
major, so the whole item rests on a cell-scaling extrapolation of the adjoint.** `P0` replaces it
with a measurement.

**What `P0` is:** `-task compute_totals` — **one primal and one adjoint** — on the **published CRM
mesh (L2, 579,072 cells, row 21/22 at their published values)**, at the published `aoa0`, with the
published `daOptions`, at the placement of §10.

**What `P0` RECORDS, and each is a value this registration currently cannot state:**

| recorded | why it is not known today |
|---|---|
| wall seconds and core-min **per flow adjoint** at 579,072 cells | §11's only `ASSUMED` factor |
| **peak RSS** of the adjoint | A6 predicted 95–116 GiB against a then-30 GiB box; the box now reads **739 GiB total / 640 GiB available** (measured 2026-09-13 17:10Z), but the prediction has never been tested |
| the effective `primalMinResTolDiff` (row 30) | absent from the published CRM file |
| the effective `nom_addLocalDV` displacement axis (row 54) | not specified in the published file |
| whether `transonicPCOption` was `1` or `2` in force (Δ2) | the lab measured `2` is inert; this records which ran |
| the baseline y⁺ min/max/mean on the as-built mesh | corroborates A6's `7.648 / 73.826 / 34.587` and is the Δ1 sizing anchor |

**`P0` GATES:**
- **`P0-G1` — the adjoint COMPLETED.** `rc = 0`; `Main iteration` count > 0; `KSP Residual` count
  > 0; `compute_totals` returned a finite derivative for every `(of, wrt)` pair. *A run that never
  attempted a linear solve is `NOT A RESULT`, not a fast adjoint.*
- **`P0-G2` — the gradient is not noise.** `‖dCD/dtwist‖∞ > 0` and no component non-finite.
- **`P0-G3` — memory.** Peak RSS recorded and below `MemAvailable` at launch. An OOM (`rc = 137`) is
  a registered outcome and is `NOT A RESULT` about the adjoint's cost.
- **`P0-G4` — the record matches the run.** The rule-17 mesh-read hash and the rule-18 DV-apply hash
  are both written and both assert.

**Until `P0` reads `PASS`, every arm after it is `PENDING` and §11's cost model is labelled
`UNTESTED`.** A `P0` `GATE FAIL` is a finding about the CRM adjoint at production scale and is
reported as one; it is **not** a reason to drop to a coarser mesh and re-grade.

---

## 8. ARM `P1` — THE PRIMAL-CONVERGENCE ARM *(her rule 5; Δ7)*

On the **L3 baseline, one condition, 5,000 steps**, over six registered configurations —
`nNonOrthogonalCorrectors ∈ {0, 3, 12}` × relaxation `{published, p 0.70}` at the published
`DARhoSimpleCFoam`.

**Why the configurations and not one:** D6RF10 measured `nNonOrth 3` running **flat at 0.117 s/step**
and `nNonOrth 12` at **4.650 s/step** — a factor **39.7**, caused by **157 of 273 p-solves
saturating the linear solver's `nIters: 1000` cap** once `initRes` falls near 1e-8. **D6RF10 changed
solver, `nNonOrth` and `relax_p` together, so the cost of each alone is UNMEASURED.** Registering
`nNonOrth 12` on that bundled result would be a 40× cost decision taken on an unattributed
measurement. **The published CRM value is `0` (row 38) and is one of the three.**

- **`P1-G1`** — a configuration `PASS`es if the last 500 steps' `CD` peak-to-peak is ≤ **`1.0e-6`**
  and every per-equation residual is monotone-or-plateaued over that window.
- **`P1-G2`** — `endTime` becomes the smallest step count at which `P1-G1` holds; **the cheapest
  passing configuration is taken**, and if none passes that is a finding about this case's numerics,
  not a reason to widen `1.0e-6`.
- **`P1` also delivers the residual→drag-error curve** on one solver and one mesh.
- **PLANTED CONTROL (rule 3):** the reader plants `PLANT = 1.234e-03` into the `CD` trace it read
  back **from disk** and **REFUSES (exit 2)** if the plant leaves any configuration at `PASS`.

---

## 9. **THE SIX IN-RUN INSTRUMENTS — WRITTEN, AND EVERY ONE DRIVEN AGAINST A KNOWN-BAD INPUT AND SHOWN TO FIRE**

Her requirement: *"we must incorporate the within run checks of the instructions to ensure the
result we get is not from a mesh artefact."*

**Instrument:** `d6r3_inrun_guards.py`, md5 **`57a7d187163feb5120e25967c7c7e959`**.
**Controls:** `D6R3_INRUN_SELFTEST.json`, md5 **`181be48e46aa69761fb39d33674f406d`**.
**Result: `D6R3_INRUN SELFTEST PASS`, `n_total = 48`, `n_pass = 48`, `n_fail = 0`, exit 0.**
**Rule 20 evidence:** the pre-freeze check drives **the command line the launcher emits**, not the
graded function — `D6R3_PREFREEZE_CLI.log` records `--selftest --json <path>` → `rc = 0`, no-args →
`rc = 64` (refuses rather than succeeding silently), unknown flag `--log x` → `rc = 2`. *That is the
FM9 defect class driven to its failing side: the FM9 grader's launcher emitted `--log`, the parser
rejected it, and the frozen CLI path could only ever return `NOT A RESULT` while its selftest stayed
green.*

**Every guard returns exactly one of `OK` / `STOP` / `REFUSE`, checks non-finite BEFORE any
comparison (rule 26), counts its informative inputs and refuses below a floor (rule 25), prints
every count with its failing partner (rule 24), and never degrades to `OK`.**

### 9.6 — RULE 6: the warp settings that carry the near-wall layers are IN FORCE, every iteration

**External anchor:** IDWarp's own **live** option dictionary, read back from the running mesh object
— not the dict we passed in.

**Verified in IDWarp's own source** (2.6.2, `/home/ubuntu/certonomous-runs/W5-idwarp-source/
idwarp_src`), because her rule says *verify*:

| option | registered | **name defined** | **value used** | what the source says it does |
|---|---|---|---|---|
| **`useRotations`** | `True` | `idwarp/UnstructuredMesh.py:138` | `:1058` → `warp.gridinput.userotations`; consumed `src/modules/kd_tree.F90:1110`, `:1339` | guards `GETROTATIONMATRIX3D`, which builds the per-node rotation `Mi` from the surface normal's change (`normals0 → normals`) and applies it to every non-corner surface node — **her "rotation of the near-wall region with the surface", by name and by line** |
| **`LdefFact`** | `1.0` | `:133` | `:1053`; `src/warp/warpMesh.F90:39`, `warpDeriv.F90:59` set `tp%Ldef = tp%Ldef0 * LdefFact`; `Ldef0` at `kd_tree.F90:1500-1512` | `Ldef0` = **the maximum distance from the surface-node centroid to any surface node** — **her "deformation region scaled to the geometry", by name and by line** |
| `aExp` / `bExp` / `alpha` | `3.0` / `5.0` / `0.25` | `:131,132,134` | `:1055,1056,1054`; `Wi = Ai·[(Ldef/dist)^aExp + alpha^bExp(Ldef/dist)^bExp]`, `kd_tree.F90:685`; `alphaToBexp` at `:1528` | the inverse-distance weight |
| `zeroCornerRotations` / `cornerAngle` | `True` / `30.0` | `:139,140` | `tp%isCorner` guard at `:1110`, `:1339`; `:1060` | corners excluded from rotation |
| `errTol` / `bucketSize` / `symmTol` | `0.0005` / `8` / `1e-6` | `:135,142,137` | `:1061,1062,1057` | fast-eval tolerance, KD-tree bucket, symmetry match |
| **`evalMode`** | **`exact`** *(Δ3)* | `:136` | `:1063-1065` | `fast` is the KD-tree approximation |

**The published CRM file sets NONE of these** (row 50) — every one runs at its default. **This
registration writes them all explicitly so the record names what ran instead of inheriting it by
omission**, and guard 6 asserts each one is still in force at every iteration.

**Toolchain fact carried forward:** the pinned image `dafoam-idwarp-rot:v1`
(`sha256:2927768a16ac…`) carries a rebuilt `libidwarp.so` (md5 `85f59e87253e0a71a813f64ca6e4c425`)
holding this lab's IDWarp rotation-**derivative** patch (+44 lines) — **on the derivative path of
exactly the `useRotations` mechanism rule 6 names.** **NOT FILED** upstream, and it stays that way.

**CONTROLS — 5, all PASS:**

| control | want | got |
|---|---|---|
| clean: the registered settings in force | `OK` | **`OK`** |
| **KNOWN-BAD: `useRotations` silently `False`** | `STOP` | **`STOP`** |
| **KNOWN-BAD: `LdefFact` moved to 0.5 unregistered** | `STOP` | **`STOP`** |
| **KNOWN-BAD: `evalMode` back to the published `fast`** | `STOP` | **`STOP`** |
| **BLIND: the option absent from the live dict (IDWarp on its own default)** | `REFUSE` | **`REFUSE`** |

### 9.7 — RULE 7: the per-iteration quality budget, on the **AS-RUN** points

**External anchor:** `checkMesh` run on the points the solver will read, **after** the final DV
application. **Rule 31 is enforced as a REFUSAL, not a warning:** if the quality log's mtime is not
strictly newer than the DV-apply mtime, guard 7 refuses.

**Thresholds — every one from a published line:**

| quantity | threshold | source |
|---|---|---|
| max non-orthogonality | **≤ 70.0** | the published DAFoam mesh-quality **constraint** bound, `UBend_Channel/runScript_meshQualityConstraint_v2.py:213` *(Δ9, Δ13)*. **NOT** the CRM file's own abort threshold of **75.0** (`runScript.py:82`), which stays the registered solver setting (row 47, verbatim) — see §9.7a for the measured reason |
| max aspect ratio | **≤ 2000.0** | **the PUBLISHED CRM value**, `:81` |
| worst-cell skewness | **≤ 4.0** | the published DAFoam mesh-quality **constraint** bound, `UBend_Channel/runScript_meshQualityConstraint_v2.py:212` *(Δ9; tighter than the CRM file's own abort threshold of 5.0, and taken from the published constraint rather than the published abort deliberately)* |
| min first-cell height / baseline | **≥ 0.80** | D6R2 measured first-cell height within **1.6 %** fresh-vs-deformed (§22.3); 0.80 is a 12× allowance |
| min cell volume | **> 0** strictly and **≥ 0.10 ×** baseline min | D6R2 measured **zero** negative or degenerate volumes; the ratio is the early warning |
| y⁺ | **median ≤ 1.5, max ≤ 3.0** under Δ1; **max ≤ 110.0** verbatim | 1.5 × the §5c acceptance; 110.0 is **1.5 × the measured baseline max of 73.826** |

### 9.7a — **THE SOLVER'S OWN MESH CHECK NEVER REFUSES ON THIS CLAUSE. MEASURED — AND IT IS WHY RULE 7's BUDGET IS OUR INSTRUMENT AND NOT THE SOLVER'S VERDICT.** *(Δ13)*

**Reproduced independently by this lane, 2026-09-13.** The finding was relayed by
`dafoam-supervisor` (committed at `efe4c2c4f`, `DAFOAM_CHARTER.md` §22.7) and is **re-measured here
rather than adopted**, because a relayed measurement is not this lane's. **Instrument and path, per
§22.6:** `re.finditer(r'Mesh non-orthogonality Max:\s*([\d.]+)')` plus literal string counts, over
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable/O_mp_20260913T013230Z_226722.log`
and
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-FM9-a2-wing-freshmesh-arrives/FM10_20260913T163543Z_1546115.log`.

| log | mesh-check blocks | **blocks over 70.0** | **worst** | `severely non-orthogonal (> 70 degrees)` lines | `Non-orthogonality check OK.` | `Mesh OK.` | `Failed 1 mesh checks.` |
|---|---|---|---|---|---|---|---|
| `O_mp` | **202** | **76** | **`80.90429398`** | **76** | **202** | 198 | **4** |
| `FM10` | **6** | **6 of 6** | **`79.21261137`** | **6** | **6** | **6** | **0** |

**Every breaching block prints `Non-orthogonality check OK.`, and where no other clause fails,
`Mesh OK.` — at 80.90 against a declared `maxNonOrth = 70.0`.** OpenFOAM's own line
`*Number of severely non-orthogonal (> 70 degrees) faces: N` appears **76 times in `O_mp` and 6
times in `FM10`**, immediately above the `OK` it does not prevent: **the log names the breach and
passes it in consecutive lines.**

**THE REFUSAL CHANNEL IS DEMONSTRABLY LIVE, which is what makes this a finding and not a guess.**
The same `O_mp` log carries **four `Failed 1 mesh checks.` lines, and all four are aspect-ratio
failures** (`1050.3162` against the same dictionary's `1000.0`) at a non-orthogonality of `66.92`.
**The machinery works. It simply never fires on the non-orthogonality clause.**

**TWO CORRECTIONS THIS LANE'S OWN MEASUREMENT MAKES TO THE RELAY**, recorded because §22.6 exists:
**`80.90429398`, not `79.21`, is `O_mp`'s worst** — `79.21261137` is **`FM10`'s**; and
**`71.23798136` appears in BOTH logs' check blocks**, not only `O_mp`'s.

**THREE CONSEQUENCES, REGISTERED:**

1. **Δ13 — RULE 7's BUDGET IS OUR OWN REFUSING INSTRUMENT.** `guard7_quality_budget` requires
   `source == "as_run_mesh_measurement"` and **REFUSES** a verdict string. *A budget that delegates
   its stop to `checkMesh`'s own verdict line is a budget that has already been measured not to
   stop.* Driven: control `G7.DELEGATION`.
2. **The registered threshold is `70.0`, the published constraint bound — not the CRM file's abort
   `75.0`.** At `75.0` the budget would pass `71.24`, one of the two real meshes it exists to catch.
   **The threshold was chosen so the instrument catches both real as-run meshes, and the instrument
   was then driven against them; both candidate values are published lines, and the one that catches
   the known-bad inputs is registered.**
3. **RULE 31 IS ALREADY BREACHED ON BOTH D6R2 ARMS, so no part of this registration cites either
   arm's `Mesh OK.` as evidence about the mesh that ran.** The only quotable `Mesh OK.` in this
   family is of the **as-extruded** mesh at `66.32299475`, before the solve re-applies the design.

**WHERE THE THRESHOLDS POINT FIRST: THE TRAILING EDGE.** The worst face was located geometrically by
the supervisor (the vtp face's max `x = 8.0844` equals the local TE `x = 8.0843` to four decimals).
**That is the supervisor's measurement, relayed and labelled as such — this lane did not reproduce
it.** It is registered as the first place `P0` and `W1` point their quality probes.

**THE UPSTREAM BEHAVIOUR IS A DEFECT CANDIDATE ONLY AND IS NOT FILED ANYWHERE.** No filing is
drafted, none is pending, and none is referenced as pending. **Filing is Sanaa's alone** (rule 7).

**ONE THRESHOLD THAT STILL DOES NOT CATCH A REAL D6R2 BREACH, AND IT IS NOT ACCOMMODATED.** The
worst measured aspect-ratio trip, **`1050.3162`**, breached the MACH wing's own declared `1000.0`
but sits well inside the CRM's published **`2000.0`**, so the budget reads `OK`. **The published CRM
value is kept** (row 47 is verbatim, and a wall-resolved CRM mesh will carry far higher aspect
ratios than the MACH wing by construction); the gap is recorded here so a reader knows this one
clause is looser than D6R2's was, and the control that demonstrates it sits in the table below
marked `OK` rather than hidden.

**CONTROLS — 16, all PASS. Seven are driven on REAL measured as-run values:**

| control | want | got |
|---|---|---|
| clean: as-run mesh inside every threshold | `OK` | **`OK`** |
| **KNOWN-BAD/REAL: `O_mp`'s WORST as-run mesh, `80.90429398` — which OpenFOAM itself called `Non-orthogonality check OK.` then `Mesh OK.`** | `STOP` | **`STOP`** |
| **KNOWN-BAD/REAL: `FM10`'s worst as-run mesh, `79.21261137`, 6 of 6 blocks over 70.0, ZERO `Failed 1 mesh checks.` in that log** | `STOP` | **`STOP`** |
| **KNOWN-BAD/REAL: `71.23798136`, present in BOTH logs' check blocks, 1.8 % over and passed by the solver** | `STOP` | **`STOP`** |
| **KNOWN-BAD/REAL: `70.01418200`, the SMALLEST of `O_mp`'s 76 over-70 values — the marginal breach must be caught too** | `STOP` | **`STOP`** |
| REAL/boundary: `66.96543422`, an `O_mp` block genuinely under 70.0, must NOT fire | `OK` | **`OK`** |
| **DELEGATION: handed the solver's own verdict line instead of a measurement, the budget must REFUSE** | `REFUSE` | **`REFUSE`** |
| KNOWN-BAD/REAL: D6R2's worst aspect trip `1050.3162` against the CRM's published 2000.0 — does **not** fire, and that is the registered gap above | `OK` | **`OK`** |
| KNOWN-BAD: aspect ratio 2100 breaches the published 2000.0 | `STOP` | **`STOP`** |
| KNOWN-BAD: skewness 4.5 breaches the published constraint bound 4.0 | `STOP` | **`STOP`** |
| KNOWN-BAD: first cell collapsed to 0.5× baseline | `STOP` | **`STOP`** |
| KNOWN-BAD: a negative cell volume | `STOP` | **`STOP`** |
| KNOWN-BAD: y⁺ median drifted to 2.0 under warping | `STOP` | **`STOP`** |
| **RULE 31: `checkMesh` written BEFORE the DV apply — the FM10 defect exactly** | `REFUSE` | **`REFUSE`** |
| NON-FINITE: `maxNonOrtho` is NaN (rule 26: `nan > tol` is `False`) | `REFUSE` | **`REFUSE`** |
| BLIND: `maxNonOrtho` was never measured | `REFUSE` | **`REFUSE`** |

### 9.8 — RULE 8: periodic re-meshing with restart, **N = 3 majors**

**External anchor:** the mesh generation stamp — the extrusion's own output identity, not the
warper's.

**`N = 3` IS DERIVED FROM A MEASUREMENT.** The `O_mp` log's four `High aspect ratio cells found`
trips sit at lines 22928, 31050, 33015, 46373; counting `Starting time loop` occurrences before each
gives **83, 113, 120 and 170 condition-primals** out of 198 in a 25-major run of 113 evaluations.
**The first mesh-quality breach appeared at roughly evaluation 28 of 113, i.e. IPOPT major ≈ 6 of
25. `N = 3` is half of 6** — the mesh is regenerated before the point at which D6R2C's mesh was
measured to have degraded. Eight events over a 25-major run.

**HER ALTERNATIVE TRIGGER IS UNUSABLE ON THIS CASE AND THE REGISTRATION SAYS SO.** Rule 8 offers
*"whenever the surface displacement exceeds a registered fraction of the local first-cell height"*.
Under Δ1 the first cell is `1.35e-6 m` while D6R2's measured mid-span camber excursion was
`0.00196 → 0.04810` chord over 25 majors — on a 1.689 m root chord, ≈ `3.1e-3 m` per major, i.e.
**≈ 2,300 first-cell heights per major.** The trigger would fire on the first step and every step
after. **It is NOT used; the fixed `N` and the §9.7 budget are the triggers, and the ratio is
reported at every checkpoint so the record carries the reason.**

**The checkpoint protocol:** regenerate through the published pipeline → trim to matched lift on the
fresh mesh → evaluate the objective → **spot-check the gradient on the new mesh** (her own clause)
against the deformed-mesh gradient at the same design, tolerance **`1.0e-4` relative per component
normalised by `‖g‖∞`** → resume from the current design. Accumulated warp error resets to zero.

**CONTROLS — 5, all PASS:**

| control | want | got |
|---|---|---|
| clean: mesh regenerated at major 6, now at major 7 | `OK` | **`OK`** |
| **KNOWN-BAD: major 7 on a mesh stamped at major 0 — D6R2's whole run** | `STOP` | **`STOP`** |
| boundary: exactly `N = 3` majors old must fire | `STOP` | **`STOP`** |
| boundary: exactly `N − 1 = 2` majors old must not fire | `OK` | **`OK`** |
| BLIND: the mesh stamp is later than the current major, so it is not this run's | `REFUSE` | **`REFUSE`** |

### 9.9 — RULE 9: the fresh-mesh objective checkpoint at matched lift — **THE INSTRUMENT THAT MOST MATTERS**

Her own line: **this is the rule that would have caught D6R2 on day one.**

**External anchor:** a mesh **freshly extruded by pyHyp from the current design surface** —
independent of the warp, which is the entire point. **Not** a re-read of the warped mesh.

- **TOLERANCE: `|J_fresh − J_deformed| / J_fresh ≤ 0.010`**, with **both sides at matched lift** and
  **both trims converged to `|CL_i − target_i| ≤ 1.0e-4`**. Basis: the same band as the grid family
  (§4b) — a deformed mesh that disagrees with a fresh one by more than the family's level spacing is
  no longer measuring the same problem.
- **A crossing STOPS the run and re-meshes.** It does not adjust the tolerance.
- **THE LIFT CHECK RUNS BEFORE THE DRAG COMPARISON, DELIBERATELY** — so that an off-target
  evaluation produces a **`REFUSE`**, not a drag ratio across different lifts (rule 19).

**CONTROLS — 9, all PASS. Three of them are D6R2's own measured numbers:**

| control | want | got |
|---|---|---|
| clean: fresh and deformed agree to 0.3 %, both at matched lift | `OK` | **`OK`** |
| **KNOWN-BAD/MEASURED: D6R2's own deformed 0.753 vs fresh 1.206 ratio pair** | `STOP` | **`STOP`** |
| **KNOWN-BAD/MEASURED: the 139-drag-count deformed-vs-fresh gap on a `CD` of 0.023** | `STOP` | **`STOP`** |
| boundary: a 1.1 % gap must fire against the 1.0 % band | `STOP` | **`STOP`** |
| boundary: a 0.9 % gap must not fire | `OK` | **`OK`** |
| **KNOWN-BAD/MEASURED: FM10's `+0.1493 / +0.1516 / +0.1524` lift excess — refuse the comparison rather than report a ratio across different lifts** | `REFUSE` | **`REFUSE`** |
| NON-FINITE: `J_fresh` is NaN | `REFUSE` | **`REFUSE`** |
| **PLANT: `1.234e-03` on a `J` of 0.023 (5.4 %) must be seen** | `STOP` | **`STOP`** |
| BLIND: the fresh side has no `CL` record at all | `REFUSE` | **`REFUSE`** |

**Read the second and sixth rows together: driven against D6R2's actual artefacts, this guard
stops the run on the drag gap and refuses the comparison on the lift excess. It would have caught
D6R2, and it is now shown to, rather than asserted to.**

### 9.10 — RULE 10: the shear/pressure drag split, every iteration, with the artefact signature

**External anchor:** OpenFOAM's own `forces` function object output (`force.dat`), written by the
solver with **total / pressure / viscous** columns *(Δ10)*. The guard **refuses** if the viscous
column is absent — a channel with readers and no writer defaults to success, silently (rule 27), and
that is the defect still open on Sanaa's desk.

**THE ARTEFACT SIGNATURE, REGISTERED AS ARITHMETIC BEFORE THE DATA EXISTS:**

> Between two consecutive accepted designs, if **`ΔCD_total < 0`** while
> **`|ΔCD_pressure| < 0.20 · |ΔCD_total|`** — more than 80 % of the gain arriving in the **viscous**
> component — **and** the span load changes by less than **1 %** at every station, **the run STOPS
> and re-meshes.**

**The 20 % floor is the inverse of a measurement.** D6R2's deformed-versus-fresh gap was carried
**104.5 % / 102.9 % / 99.6 % by PRESSURE drag**, with viscous drag flat to within **7 counts of its
own value** (§22.3). That is the shape of a genuine pressure-driven difference. A *gain* arriving the
other way round is the signature her rule names, and a five-fold departure from 100 % is not noise.

**Also reported each iteration, as a REPORTED DIAGNOSTIC and named as one:** the **second difference
of the FFD `Δz` along each chordwise row** — the wiggle metric of her rule 4. It is not a gate, and
saying so is required: a printed quantity annotated as non-binding is worse than one never computed
unless its status is stated.

**NOT SATISFIED, and named:** her *"where available, a far-field decomposition with the spurious-drag
component"*. **It is not available.** Enumerating every `"type"` across the tutorial clone gives
`force`, `moment`, `variance`, `meshQualityKS`, `totalPressure`, `field`, `power`, `wallHeatFlux`,
`patchMean`, `massFlowRate`, `regressionPar`, `vonMisesStressKS`, `uniformPressureGradient`,
`totalTemperatureRatio`, `totalPressureRatio`, `variableVolSum`, `fieldUnsteady`, `patchField` —
**none of them a far-field or spurious-drag decomposition.**

**CONTROLS — 8, all PASS:**

| control | want | got |
|---|---|---|
| clean: a real gain carried by PRESSURE with the span load moving | `OK` | **`OK`** |
| **KNOWN-BAD: the artefact signature — 100 % of the gain in FRICTION with the span load flat** | `STOP` | **`STOP`** |
| boundary: 19 % of the gain in pressure (just inside the floor) fires | `STOP` | **`STOP`** |
| boundary: 21 % of the gain in pressure does not fire | `OK` | **`OK`** |
| not-a-gain: a friction-only RISE is not the signature | `OK` | **`OK`** |
| **BLIND: `forces` never wrote the viscous column (rule 27)** | `REFUSE` | **`REFUSE`** |
| INCONSISTENT: pressure + viscous ≠ total | `REFUSE` | **`REFUSE`** |
| BLIND: 3 span stations, below the informative floor of 6 | `REFUSE` | **`REFUSE`** |

### 9.11 — RULE 11: the trust region on the design step

**HONEST STATEMENT FIRST.** A trust region sized literally to the first-cell height is not usable on
this case. Under Δ1 the first cell is `1.35e-6 m` against a 1.689 m root chord: a step limited to one
first-cell height of surface motion is `8.0e-7` chord, and D6R2's trajectory would need of order
`10⁴`–`10⁵` majors. **Registering that number would be registering a run that cannot finish.**

**What is registered instead, and it is the mechanism her clause protects:**

1. **The binding trust region is the §9.7 quality budget, applied as an IN-ADJOINT CONSTRAINT**
   *(Δ9)* — `nonOrtho ≤ 70.0`, `skewness ≤ 4.0`, published bounds, `addToAdjoint: True`. **That is a
   trust region defined by what the warp actually preserves, measured, not by a proxy for it.**
2. **An explicit per-major move limit** *(Δ12)*: `0.10` on the scaled `shape` ∞-norm, `0.5°` on
   `twist`. Anchor: D6R2C's measured camber excursion `0.00196 → 0.04810` over 25 majors is
   reachable under a `0.10` limit in about the same number of majors, while no single step may take
   a large fraction of it.
3. **RULE 11 IS RECORDED AS PARTIALLY SATISFIED**, the substitute is named, and a supervisor who
   disagrees has the arithmetic to disagree with.

**CONTROLS — 5, all PASS:**

| control | want | got |
|---|---|---|
| clean: a 0.02 scaled-shape step inside the 0.10 limit | `OK` | **`OK`** |
| **KNOWN-BAD: a 0.35 scaled-shape step, 3.5× the limit** | `STOP` | **`STOP`** |
| **KNOWN-BAD: a 0.8° twist step against the 0.5° limit** | `STOP` | **`STOP`** |
| **BLIND/MEASURED: at x0, where D6R2C measured 103 of 109 components exactly zero, the guard must REFUSE rather than pass** | `REFUSE` | **`REFUSE`** |
| NON-FINITE: a NaN in the design vector | `REFUSE` | **`REFUSE`** |

### 9.12 — What the six guards do **NOT** do

- **They do not grade the wing.** They stop a run. The verdict on the optimisation is §10's.
- **They share one Python module, and rule 22 requires that be said.** Their **external anchors are
  six different things** — IDWarp's live option dict, `checkMesh` on the as-run points, the mesh
  generation stamp, a freshly extruded mesh, OpenFOAM's `forces` output, and the driver's design
  vector — so this is six anchors, not one. **But a defect in the shared `_finite` / `_counts`
  helpers is common-mode to all six**, and that is named here rather than discovered later.
- **Their controls are SYNTHETIC except where a row says MEASURED.** Eight controls are driven on
  D6R2's real measured values; the rest are constructed. **A synthetic control proves the guard, not
  the case.**

---

## 10. ARMS, ORDER, PLACEMENT, AND THE AFTER-PROTOCOL

| # | arm | what it is | ranks | precondition |
|---|---|---|---|---|
| 0 | **`P0`** | **one primal + one adjoint on the PUBLISHED mesh — BLOCKING** | 72 | mesh built |
| 1 | `MESH` | build L3, L2, L1 by the published pipeline; `checkMesh -allGeometry` each | 1 | — |
| 2 | `Y1` | baseline y⁺ on the optimisation level | 72 | `P0` PASS |
| 3 | `P1` | primal convergence / configuration selection | 24 | `Y1` |
| 4 | `W1` | warp-setting selection (`evalMode`, `LdefFact`), geometry only | 1 | `MESH` |
| 5 | `GF` | grid family: baseline `J` at matched lift on L3, L2, L1 | 72 | `P1`, `W1` |
| 6 | `P2` | adjoint tolerance check: `gmresRelTol 1e-6` vs `1e-9`, tighten if any component moves > 1 % of `‖g‖∞` | 72 | `GF` |
| 7 | `S1` | smooth-mode optimisation, 10 DVs, `max_iter 15` | 72 | `GF` PASS |
| 8 | `S2` | full optimisation, 202 DVs, `max_iter 25`, with the six guards live and `N = 3` checkpoints | 72 | `S1` |
| 9 | **`A12`** | **fresh mesh, matched lift, all conditions, from scratch — THE CLAIMED NUMBER** | 72 | `S2` |
| 10 | `A13` | the optimum on the next finer family level | 72 | `A12` |
| 11 | `A14` | decomposition (shape / twist / trim) on the fresh mesh | 72 | `A12` |

**Placement:** `numberOfSubdomains 72` is the **published** value (`system/decomposeParDict:18`) and
is adopted. The box reads **96 cores, 739 GiB total / 640 GiB available** (measured 2026-09-13
17:10Z). `P0-G3` records peak RSS because **A6 predicted 95–116 GiB for this adjoint against a
then-30 GiB box and the prediction has never been tested.**

**`DAFOAM_CHARTER.md` §22.2, with teeth:** *no shape-optimisation improvement figure leaves this
family unless the number quoted is the fresh-mesh number, at matched lift, on all conditions, from
scratch.* **`A12` is that number.** `A13`'s gate is `|J_fresh(finer) − J_fresh(opt)| / J_fresh(finer)
≤ 0.010` — a miss is **`GATE FAIL`**: *an optimum that holds on one mesh only is not an optimum.*
**No percentage is quoted before `A14` exists.** The drag split on both meshes goes on the
certificate. **`A12`, `A13` and `A14` all run the BASELINE through the identical path**, so every
ratio's two factors share mesh generation, lift and DV application (rule 19).

---

## 11. COST — PRICED **BOTH WAYS**, ON A MEASURED CRM ADJOINT

### 11a. The anchors — and the biggest one is now MEASURED, not extrapolated

**From `D8R` `O-P` — CRM wing, `DARhoSimpleCFoam`, M 0.8497, published producer md5 `0de915d2…`,
41,760 cells, 4 ranks, 4,753 s wall, 316.867 core-min** (`curriculum_D8R/RESULTS.md:179-233`):

| anchor | value | how it was measured by this lane |
|---|---|---|
| **one flow adjoint** | **182.1 s wall = 12.140 core-min** | 20 `Solving Linear Equation... <t> s` stamps; the 10 **within-pair** deltas (adjoint→adjoint, no primal between) have median **182.1 s**; the 9 **across-pair** deltas median 227.4 s, the difference being the intervening primal |
| **one primal** | **69.44 s wall = 4.629 core-min** | `(4753 − 20 × 182.1) / 16`, 16 `Starting time loop` occurrences |
| gradient structure | **2 flow adjoints per gradient evaluation** (`CD` and `CL`); 100 `Computing d[…]` over 10 gradient evaluations | the log |
| evaluations per major | **3.48 `F`**, **1.04 `G`** | D6R2C `O_mp`: 87 F, 26 G, 25 majors |
| baseline y⁺ on the published mesh | **min 7.648 / max 73.826 / mean 34.587** | `A6-crm-wing/run_model_run1.log`, converged tail |
| published-mesh cell count | **579,072** = 11,136 × 52 | `A6-crm-wing/logMeshGeneration.txt:478` |

**Multipoint per-evaluation cost** *(rule 30, stated separately)*, at cell factor `c/41,760`:

```
OBJECTIVE evaluation = 3 primals   = 3 x 4.629 x (c/41760) x k_primal
GRADIENT  evaluation = 6 adjoints  = 6 x 12.140 x (c/41760) x k_adjoint   (CD + CL per condition)
```

| factor | value | justification | tag |
|---|---|---|---|
| cell factor | exact arithmetic | §4a | `DERIVED` |
| `k_adjoint` at L3 (a 1.73× extrapolation) | **1.25** | adjoint conditioning grows super-linearly with cells | **`ASSUMED`** |
| `k_adjoint` at L2 (a 13.9× extrapolation) | **1.50** | same | **`ASSUMED`** — **this is what `P0` measures and replaces** |
| `k_primal`, `k_adjoint` extra under Δ1 | **×1.0**, **×1.5** | Kenway et al. PAS 2019: *"linear system stiffness, especially for the viscous layer near the wall when a y⁺ = 1"* (`…100542.txt:2869`) | **`ASSUMED`** |

### 11b. **OPTION A — VERBATIM (published wall-function). Optimisation on L3.**

`objective evaluation` **24.07 core-min** · `gradient evaluation` **157.82 core-min** ·
**per major 247.9**

| item | core-min |
|---|---|
| `MESH` build, 3 levels (incl. a 4.63 M-cell extrusion) | 120.0 `ESTIMATED` |
| **`P0`** primal + adjoint on the published mesh | **569.2** |
| `P1` primal convergence, 6 configs × 5,000 steps | 120.4 |
| `W1` warp selection | 30.0 `ESTIMATED` |
| **`GF` grid family** (L3 120.4 + L2 962.9 + L1 7,702.9) | **8,786.2** |
| `P2` adjoint tolerance | 315.6 |
| `S1` smooth-mode optimisation, 15 majors | 3,718.5 |
| **`S2` full optimisation, 25 majors** | **6,197.6** |
| rules 8/9 checkpoints × 8 | 2,458.0 |
| `A12` fresh mesh, matched lift | 120.4 |
| `A13` optimum on the next finer level | 962.9 |
| `A14` decomposition × 3 | 361.1 |
| subtotal | 23,759.8 |
| + 5 % preamble, staging, `checkMesh`, grading | 1,188.0 |
| **REGISTERED TOTAL** | **24,900** |
| **CAP, 3.00×** | **74,700** |

**DERIVED DOLLARS: `24,900 core-min = 415.0 core-h × $0.0513 =` $21.29**; cap **$63.87**.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5);
`cost_basis` **reported-by-owner** at the owner-stated c7a.4xlarge rate. *(The box is not a
c7a.4xlarge; the rate on record is used unchanged rather than invented, and the substitution is named
here rather than buried.)*

### 11c. **OPTION B — WITH DEVIATION #1 (wall-resolved y⁺ ≈ 1). Optimisation on L3.**

`objective evaluation` **48.14 core-min** · `gradient evaluation` **473.46 core-min** ·
**per major 659.9**

| item | core-min |
|---|---|
| `MESH` build | 120.0 |
| **`P0`** | **1,643.5** |
| `P1` | 240.7 |
| `W1` | 30.0 |
| **`GF` grid family** | **17,572.3** |
| `P2` | 946.9 |
| `S1`, 15 majors | 9,899.1 |
| **`S2`, 25 majors** | **16,498.4** |
| checkpoints × 8 | 6,138.6 |
| `A12` | 240.7 |
| `A13` | 1,925.7 |
| `A14` | 722.1 |
| subtotal + 5 % | 58,777 |
| **REGISTERED TOTAL** | **58,800** |
| **CAP, 3.00×** | **176,400** |

**DERIVED DOLLARS: $50.27**; cap **$150.82**.

> ### **DEVIATION #1 COSTS A FACTOR 2.36 — 24,900 → 58,800 core-min, $21.29 → $50.27.**
> **She decides on that number. It is not applied by this lane and it is not assumed accepted.**

### 11d. The `L2 BRANCH` contingency — registered in advance, not discovered as an overrun

If L3 fails the §4b band and the optimisation must run on the **published 579,072-cell mesh**:
`objective evaluation` 192.57, `gradient evaluation` 1,515.07, **per major 2,245.8**, item total
**142,200 core-min**, cap 426,600, **$121.58** derived. Under Δ1 that branch is larger again and is
**NOT COSTED** here — it would be re-registered, not absorbed.

### 11e. **R1's COST FIGURE IS SUPERSEDED, AND BY SEVENTEEN TIMES**

R1 §15e priced this option at **≈425,000 core-min / ≈$363 / ≈74 hours of the entire box**. That
figure extrapolated the gradient cost from the A2 wing at M 0.288 because R1 believed no CRM adjoint
had ever run. **A CRM adjoint had run, on this exact published producer, and its cost was on disk**
(§1a). Correcting to the measured anchor, and applying her rule 1 (the optimisation mesh is the
*coarsest* qualifying level, not the finest), gives **24,900**. **The R1 figure is withdrawn.**

### 11f. The cap reports; nothing kills on it

Directive #17: a crossing writes `D6R3_CAP_CROSSED` to the ledger, **the row is graded `NOT A
RESULT`, and the cap is never raised.** No wrapper carries a `timeout`; every container prints
`D6R3_DEADLINE_IN_CONTAINER_S: NONE`. **The §9.7 quality-budget stop and the §9.9 fresh-mesh stop
are different things and are NOT affected by this clause — they are physics guards and they stop the
run, exactly as her rules 7 and 9 require.**

**Contention:** `core_min = wall_s × ranks / 60` inflates with contention at identical compute work
(D6R2's dying run measured ≈ 277 core-min/major against a 31.258 anchor, **8.9×**). Any figure above
prediction attributable to delivered-core starvation is reported with the measured
`delivered_cores_mean` and named as **waste**, never absorbed into the ratio
(`COMPUTE_BUDGET_CHARTER.md` §6).

**Calibration rows owed** to `docs/COST_CALIBRATION.md` at **every** arm completion (rule 12,
rule 30). **`P0`'s row is the first and it re-anchors `k_adjoint`, the one `ASSUMED` factor that the
whole model turns on.**

---

## 12. RULES 17–32 — THE RECORD HALF

Carried forward from R1 unchanged in substance; the entries that this revision has **exercised** are
marked.

| rule | what D6R3 registers | status at this draft |
|---|---|---|
| **17** gate on the mesh the solver READ | hash of the `polyMesh` the running solver loaded, rebuilt from `pointProcAddressing`, compared for exact equality against the generated mesh; staging into every processor case happens **before** the model is built. *Measured why:* FM8 scanned **1,486 processor meshes, zero matching the freshly extruded mesh.* | registered; instrument **NOT WRITTEN** |
| **18** DVs applied EXACTLY ONCE, proved by hash | equality of the surface hash against the **BASE** surface at the moment the DVs are applied. *Measured why:* FM10 flew at CL **+0.1493/+0.1516/+0.1524**, 30× the finding trigger; `d6r2c_freshmesh.py:423-425`. | registered; **guard 9 already refuses the downstream comparison** (§9.9, control 6, driven) |
| **19** no ratio across meshes, lifts or DV applications | every ratio carries both factors' mesh id, trims and DV hashes. *Measured why:* the withdrawn **1.2063**. | **ENFORCED IN CODE** — guard 9 refuses (§9.9) |
| **20** drive the CLI the launcher EMITS | the pre-freeze check executes the launcher's exact argv | **DONE** — `D6R3_PREFREEZE_CLI.log`, rc 0 / 64 / 2 |
| **21** every instrument in the frozen table EXISTS at its md5 | §13's table is written in the **negative** | **PARTLY DONE** — two rows now carry real md5s |
| **22** count EXTERNAL ANCHORS, not gates | §9.12 states the six anchors **and names the common-mode helper risk** | **DONE** |
| **23** derive constants from the thing under test, in the same invocation | guard 7 derives `h1_ratio` and `vol_ratio` from the baseline in-invocation; the Δ1 `s0` is derived from the **measured** y⁺ | **DONE in code** |
| **24** suspect a SUCCESS as hard as a failure | every guard returns `n_ok + n_bad == n_total`, asserted. *Measured why:* `"O_mp converged 88 times"` was false — **35 of 87 succeeded, 52 failed, `n = 88` was an INDEX.** | **DONE in code** |
| **25** never gate where the quantity is identically zero | informative-component counting with `INFORMATIVE_FLOOR = 6`. *Measured why:* the scaler gate sat at `shape ≡ twist ≡ 0`. | **DONE and DRIVEN** — §9.11 control 4 |
| **26** drive every guard to its failing side; non-finite BEFORE the comparison | `_finite()` is called before every comparison. *Measured why:* `abs(nan − x) > tol` is `False`; the parent's `gate_g3` was one evaluation from a `GATE FAIL` manufactured out of NaN. | **DONE and DRIVEN** — 4 non-finite controls |
| **27** every channel a gate reads has a **writer that ran** | guard 10 refuses when `forces` wrote no viscous column; **guard 7 refuses a channel measured never to say no** (§9.7a). *Measured why:* `primal_residual.json` had **four reads, zero writes, zero such files on disk.* **STILL OPEN ON SANAA'S DESK** | **partly** — driven for two channels; the pre-freeze channel table is **NOT WRITTEN** |
| **28** name the reference in every git comparison | append-only proved by `cmp -n <pre-append size>` against HEAD's blob, never a bare `git diff` | registered |
| **29** a crash/stall/refused solve is a FINDING and a FIX | triage on mesh → numerics → model; cause class recorded **at the stop** | registered |
| **30** cost per EVALUATION, calibrated at completion | §11a states objective and gradient separately | **DONE** |
| **31** `checkMesh` the mesh that RAN | guard 7 **REFUSES** if the quality log is not newer than the DV apply, **and refuses a delegated verdict at all** (Δ13). *Measured why:* the only quotable `Mesh OK.` in this family is of the **as-extruded** mesh at `66.32299475`; `O_mp`'s as-run worst is **`80.90429398`** and `FM10`'s **`79.21261137`**, and **both logs called every breaching block `OK`** (§9.7a). | **DONE and DRIVEN on REAL values** — §9.7 controls 2–8 |
| **32** the fifth cause class, assigned by exclusion | §6's table | registered |

### 12a. `DAFOAM_CHARTER.md` §22.4 — the three clauses the supervisor checks personally at freeze

1. **Every instrument in §13 exists at its stated md5.** **Two now do; six do not.**
2. **The pre-freeze check drives the CLI the launcher emits.** **DONE for the guard module**
   (`D6R3_PREFREEZE_CLI.log`); **not done for the arms**, which have no launcher yet.
3. **Every channel a gate reads has a writer shown to have run.** **NOT DONE.** Guard 10 refuses on
   one missing channel, which is the mechanism; the **table** naming every channel's writer does not
   exist.

**§22.4 therefore still blocks the freeze, and this revision says so rather than claiming progress
as completion.**

---

## 13. THE INSTRUMENT TABLE — still written in the NEGATIVE

| file | purpose | md5 | external anchor (rule 22) |
|---|---|---|---|
| **`d6r3_inrun_guards.py`** | the six in-run instruments, rules 6–11 | **`57a7d187163feb5120e25967c7c7e959`** | six (§9.12) |
| **`D6R3_INRUN_SELFTEST.json`** | the 48 driven controls | **`181be48e46aa69761fb39d33674f406d`** | — |
| **`D6R3_PREFREEZE_CLI.log`** | rule 20 evidence | **`1ff07c5256862bb8ab682341397ca705`** | — |
| `d6r3_mesh_family.sh` | build L3/L2/L1 by the published pipeline | **NOT WRITTEN** | `cgns_utils` + pyHyp (one anchor for all three levels) |
| `d6r3_p0_arm.sh` | **`P0`**, the blocking precondition | **NOT WRITTEN** | the solver's own adjoint log |
| `d6r3_p1_convergence.py` | `P1` + planted control | **NOT WRITTEN** | the primal's `CD` trace |
| `d6r3_opt_runScript.py` | the producer (`S1`, `S2`) | **NOT WRITTEN** | — |
| `d6r3_grade.py` | `GF`, `A12`, `A13`, `A14` | **NOT WRITTEN** | the arm's log + `forces` output |
| `d6r3_prefreeze.sh` | §22.4's three clauses | **NOT WRITTEN** | — |

**Rule 21, applied to this document itself: a table that lists what exists cannot show what is
missing.** That is the defect that carried the parent's `d6r2c_grade.py` past its freeze. **The
freeze cannot happen until every row carries a real md5 and `d6r3_prefreeze.sh` has hashed it.**

---

## 14. WHAT THIS REVISION DOES NOT CLAIM, AND WHICH RULES IT STILL CANNOT SATISFY

- **It is a DRAFT. No gate is in force. No compute is authorised.**
- **It does not claim the cost model is tested.** `k_adjoint` is `ASSUMED` and `P0` exists to
  replace it. Until `P0` lands, §11 is **`UNTESTED`**.
- **It does not claim `P0` will pass.** The adjoint at 579,072 cells has never been attempted.
- **It does not claim a Roache triple or a GCI** (§4b).
- **It does not inherit D6R2's withdrawn 24.732 %.**
- **It does not claim the six guards make the result correct.** They make an **artefact** visible
  and stop the run. They cannot make a converged optimum out of a case that has no asymptotic range.
- **It does not claim its synthetic controls prove the case** (§9.12).

| rule | status | what would be needed |
|---|---|---|
| **2** | **DEVIATION Δ1, PRICED BOTH WAYS, AWAITING HER DECISION** | her choice on the 2.36× |
| **4 (curvature constraint)** | **NOT SATISFIED.** The published setup has thickness and volume, **no curvature constraint**, and pyGeo's curvature API was **not found by this lane in the installed toolchain** — no container was started, so **no name was written down** (rule 21) | one container invocation to enumerate `nom_add*Constraint`, then register the verified call and bound or strike it |
| **10 (far-field spurious drag)** | **NOT SATISFIED** — it does not exist in DAFoam's function set (§9.10) | an external far-field decomposition tool, out of scope |
| **11 (first-cell-height trust region)** | **PARTIALLY SATISFIED** (§9.11) | a supervisor's ruling on the substitute |
| **16 (adjoint-driven mesh adaptation)** | **NOT ATTEMPTED** — her own roadmap item | a separate registered item |
| **17, 18** | registered; **instruments NOT WRITTEN** | the producer and its guards |
| **27** | **partly** — one channel driven; the channel table does not exist; **the `primal_residual.json` referral is Sanaa's and is not closed here** | her ruling |
| **row 30 (`primalMinResTolDiff`)** | **NOT MEASURED** — absent from the published CRM file | `P0` records it |
| **row 54 (local-DV displacement axis)** | **NOT MEASURED** — unspecified in the published file; the installed pyGeo default stands. **A shape DV displacing in the spanwise direction instead of the vertical would be a silent defect** | `P0` records it |
| **§22.4 clauses 1–3** | **NOT SATISFIED** (§12a) | the remaining instruments |

**SUBMISSIONS PARKED.** Nothing here is sent, filed, uploaded, registered, posted or commented. The
IDWarp rotation defect record remains **NOT FILED**.

---
---

# APPENDIX S — **STRUCK 2026-09-13.** The R1 operating point and its cost, preserved unrewritten

> **STRUCK, NOT DELETED** (`CLAUDE.md` rule 6: originals are struck, never rewritten). Sanaa ruled
> the operating point to be Mach 0.85 on 2026-09-13. **The block below is the R1 registered
> configuration and the R1 cost table, reproduced as they stood.** Nothing in this appendix is in
> force. The full R1 document is at commit `9847ffc30162cdd73c0a582d82a1f8c3cd063353`.

### S.1 — ~~R1 §3A — OPTION A, the D6R2 re-run at M 0.288~~ **STRUCK**

```
~~ geometry      mdolab_wing_surface_mesh.cgns  (MACH_Tutorial_Wing)
~~ U0 = 100.0 m/s   p0 = 101325 Pa   T0 = 300 K   nuTilda0 = 4.5e-5   aoa0 = 4.0 deg   A0 = 45.5 m^2
~~ a  = sqrt(1.4 x 287 x 300) = 347.189 m/s   ->   M_inf = 0.288028   COMPRESSIBLE SUBSONIC
~~ CL targets 0.400 / 0.500 / 0.600     weights 0.25 / 0.50 / 0.25
~~ solver        DARhoSimpleCFoam   (departure)
~~ source        MACH_Tutorial_Wing/runScript_AeroOnly.py:24-31 (md5 2906d52a5dbed2bacbaeaf85a37d3fe8)
```

### S.2 — ~~R1 §15d — the R1 registered total~~ **STRUCK**

~~`MESH`+`Y1`+`W1` 60.0 · `P1` 82.0 · `GF` 1,122.8 · `P2` 103.2 · `S1` 1,934.1 · `S2` 3,223.6 ·
checkpoints 1,962.9 · `A12` 123.0 · `A13` 984.4 · `A14` 369.1 · subtotal 9,965.1 · **REGISTERED
TOTAL 10,500 core-min**, cap 31,500, **$8.98** derived, cap $26.93.~~

### S.3 — ~~R1 §15e — the R1 transonic estimate~~ **STRUCK AND SUPERSEDED BY MEASUREMENT**

~~objective evaluation 1,343.2 · gradient evaluation 529.1 (`ASSUMED`, no CRM adjoint ever run) ·
per major 5,225 · optimisation 25 majors ≈ 130,600 · whole item ≈ **425,000 core-min ≈ $363 ≈ 74
hours of the entire box**.~~

**Why it is struck:** §1a and §11e. A CRM adjoint **had** run, on this exact published producer, at
41,760 cells, and its cost was on disk; the 529.1 was an extrapolation from a different wing at a
different Mach, and the item was priced 17× too high.

### S.4 — R1's title-page verification, carried forward unchanged

| PDF | md5 |
|---|---|
| `he_mader_martins_maki_aiaaj2020_dafoam_j058853.pdf` | `bd592e7ea1a5a3c2b9361d43f840f43b` |
| `he_mader_martins_maki_caf2018_discrete_adjoint_openfoam.pdf` | `5c27b30cbe47bbf0b136fde2ed6170d5` |
| `kenway_mader_he_martins_pas2019_effective_adjoint_100542.pdf` | `6b17ccec2a27ab5bc57c13e51b346da9` |

**SUBMISSIONS PARKED.**
