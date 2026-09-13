# Published-setup comparison — 2026-09-13

**What this file is.** Sanaa's standing rule of 2026-09-13
(`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md` §G, line 239, byte-exact):

> *"For any public case, the lab starts from a published OpenFOAM setup of that case — mesh recipe,
> layer settings, schemes, wall treatment — ingested into the knowledge base before the first
> registration. Inventing a setup for a case someone has already run in this solver is refused."*

This file publishes, per case, the **parameter | published | ours | same? | deviation reason** table
that rule requires. Every row cites the published **file and line**. **A row with no published line
to cite is itself a deviation**, because it means the value was invented here.

**How teams share this file.** Each team **APPENDS** its own clearly-headed section and **edits
nothing above it**. An append is proved by prefix byte-identity against the pre-append bytes
(`cmp -n <pre-append size>`), never by a bare `git diff` — a bare diff compares against the shared
index and answers differently depending on when a peer last staged (L-594).

**This preamble claims nothing about any section but its own file-level purpose.** Sections below
are written and owned by the teams that signed them.

**SUBMISSIONS PARKED** (`CLAUDE.md` rule 7): nothing in this file is sent, filed, uploaded,
registered, posted or commented, and no defect named here is filed anywhere.

---
---

# dafoam — `CRM_Wing`, the Mach 0.85 wing case for curriculum item **D6R3**

**Section owner:** dafoam. **Written 2026-09-13** by a dafoam `lab-lane` for `dafoam-supervisor`.
**Status: DRAFT — the registration it publishes is `cases/dafoam/ladder-a/A2/curriculum_D6R3/PREREGISTRATION.md` (revision R2), which is NOT FROZEN.**
Nothing below is a verdict; it is a statement of what the published setup says and what we intend to
run.

## d.0 Which published case, and why that one is settled

**`CRM_Wing` is the only 3D WING case at Mach 0.85 in the DAFoam tutorials.** The census below was
read from the tutorial clone by `dafoam-supervisor` and is **relayed here, labelled as the
supervisor's**, not re-derived by this lane (`a = √(1.4 · 287 · 300) = 347.189 m/s`):

| case | `U0` | Mach | solver | extrusion | FFD | complete wing case? |
|---|---|---|---|---|---|---|
| **`CRM_Wing`** | **295.0** | **0.8497** | `DARhoSimpleCFoam` | `N=53`, `s0 1.0e-4`, `marchDist 25×3.758151 = 93.954`, `volSmoothIter 30` | `wingFFD.xyz` | **YES — the case D6R3 uses** |
| `Onera_M6_Wing` | 285.0 | 0.8209 | `DARhoSimpleCFoam` | `N=65`, `s0 1.0e-4`, `marchDist 12.0`, `volSmoothIter 100` | `genFFD.py` + `wingFFD.xyz` | yes (plus a snappyHexMesh route) |
| `DPW4_Aircraft` | 295.0 | **0.8497** | `DARhoSimpleCFoam` | **no `genWingMesh.py`** — the volume mesh is downloaded | `genFFD.py`, `dpw4FFD.xyz`, `wingTailFFD.xyz` | **no — wing + tail + body** |
| `MACH_Tutorial_Wing` | 100.0 | 0.2880 | `DARhoSimpleFoam` | `N=39`, `s0 1.0e-3`, `marchDist 300.0`, `volSmoothIter 200` | `wingFFD.xyz` | yes — **SUBSONIC**; this is D6R2's case |
| `ADODG3_Wing` | 100.0 | 0.2880 | `DARhoSimpleFoam` | `N=65`, `s0 3.0e-4`, `marchDist 30.0`, `volSmoothIter 20` | `genFFD.py` + `wingFFD.xyz` | yes — **SUBSONIC, and NOT the CRM case** |
| `Prowim_Wing_Propeller` | 100.0 | 0.2880 | `DARhoSimpleFoam` | no `genWingMesh.py` | `genFFD.py` + `wingFFD.xyz` | subsonic, propeller-coupled |

**Two rows exist purely to stop a re-derivation going wrong.** `DPW4_Aircraft` shares CRM's Mach
**exactly** (0.8497) and anyone repeating this census will find it — it is wing **+ tail + body** and
ships no `genWingMesh.py`, so it is not a wing case. And **`ADODG3_Wing` is NOT the CRM case**: the
naming invites that confusion, and it is subsonic at **M 0.288**.

## d.1 Provenance of the published files

| field | value |
|---|---|
| repository | `https://github.com/DAFoam/tutorials.git` |
| local clone | `/home/ubuntu/dafoam-tutorials` — already on disk; nothing was fetched |
| HEAD | `d3b7e38b058aba2a98a74092e15c41ec455c570d`, 2026-05-16 15:58:25 -0500 |
| `CRM_Wing/runScript.py` | md5 `0de915d21166a91a9a54b37ab11214cf` |
| `CRM_Wing/genWingMesh.py` | md5 `af9b63c2a22886b40c2309b298288cb8` |
| `UBend_Channel/runScript_meshQualityConstraint_v2.py` | md5 `0d97cb5e619bffe19c8dcc2759c07d09` |
| multipoint pattern | He, Mader, Martins & Maki, **AIAA Journal 2020**, §3.1 and **Table 4** (`docs/papers/adjoint_and_optimization/he_mader_martins_maki_aiaaj2020_dafoam_j058853.pdf`, md5 `bd592e7ea1a5a3c2b9361d43f840f43b`, title-page verified by independent `pdftotext -f 1 -l 1`) |

## d.2 THE TABLE — 59 rows, 46 verbatim, 13 deviations

Line numbers are `grep -n` positions in the files hashed above.

| # | parameter | published | ours | same? | deviation reason |
|---|---|---|---|---|---|
| 1 | `U0` | `295.0` m/s — `runScript.py:24` | `295.0` | **YES** | — |
| 2 | `p0` | `101325.0` Pa — `:25` | `101325.0` | **YES** | — |
| 3 | `T0` | `300.0` K — `:27` | `300.0` | **YES** | — |
| 4 | `nuTilda0` | `4.5e-5` — `:26` | `4.5e-5` | **YES** | — |
| 5 | `aoa0` | `2.11031707` deg — `:29` | `2.11031707` | **YES** | — |
| 6 | `A0` | `3.407014` m² — `:31` | `3.407014` | **YES** | — |
| 7 | `mu` / `Pr` / `molWeight` / `Cp` | `1.8e-5` / `0.7` / `28.97` / `1005` — `constant/thermophysicalProperties:42,43,33,37` | same | **YES** | — |
| 8 | Mach (derived) | `295/347.189 = 0.849678` — from rows 1, 3 | `0.849678` | **YES** | — |
| 9 | RAS model | `SpalartAllmaras`, `turbulence on`, `Prt 1.0` — `constant/turbulenceProperties:21-25` | same | **YES** | — |
| 10 | `nuTildaMin` | `1e-16` — `:24` | `1e-16` | **YES** | — |
| 11 | `nuTilda` wall BC | `fixedValue uniform 0.0` — `0.orig/nuTilda` | same | **YES** | — |
| 12 | `primalBC.useWallFunction` | **`True`** — `runScript.py:42` | **`False`** | **NO — Δ1** | her rule 2: wall functions make friction a strong function of y⁺, and y⁺ drifts under warping. **Measured on this family: y⁺ medians 247 vs 223 fresh-vs-deformed, a 10.8 % drift from warping alone.** Priced separately: the item goes 24,900 → 58,800 core-min, **×2.36** |
| 13 | `nut` wall BC | **`nutUSpaldingWallFunction`** — `0.orig/nut:24` | **`nutLowReWallFunction`** | **NO — Δ1** | as row 12; `nutLowReWallFunction` is the DAFoam-published wall-resolved BC (`UBend_CHT/aero/0.orig/nut`) |
| 14 | mesh pipeline | `tar -xvf` → `cgns_utils coarsen surfMesh.cgns` → `python genWingMesh.py` → `plot3dToFoam -noBlank` → `autoPatch 45 -overwrite` → `createPatch -overwrite` → `renumberMesh -overwrite` — `preProcessing.sh:20-25` | same | **YES** | — |
| 15 | `inputFile` | `surfMesh.cgns` — `genWingMesh.py:3,8` | same | **YES** | — |
| 16 | `fileType` | `CGNS` — `:9` | `CGNS` | **YES** | — |
| 17 | `unattachedEdgesAreSymmetry` | `True` — `:10` | `True` | **YES** | — |
| 18 | `outerFaceBC` | `farfield` — `:11` | `farfield` | **YES** | — |
| 19 | `autoConnect` | `True` — `:12` | `True` | **YES** | — |
| 20 | `families` | `wall` — `:14` | `wall` | **YES** | — |
| 21 | **`N`** | **`53`** (52 cell layers) — `:18` | **`105`** (104 layers) | **NO — Δ1** | the y⁺ ≈ 1 first cell needs ~27 more geometric layers over a 93.954 m march; the growth ratio *improves* 1.2704 → 1.1695 |
| 22 | **`s0`** | **`1.0e-4`** m — `:19` | **`1.35e-6`** m | **NO — Δ1** | sized from a **measurement**: baseline y⁺ max `73.826` at `s0 = 1.0e-4` (`A6-crm-wing/run_model_run1.log`, converged tail) → `1.0e-4 / 73.826 = 1.3546e-6`. Cross-checked against He et al. AIAAJ 2020 `:882`, average y⁺ **33.7**, within 2.6 % of our measured mean 34.587 |
| 23 | `marchDist` | `25 × 3.758151 = 93.953775` — `:20` | same | **YES** | — |
| 24 | `ps0` / `pGridRatio` / `cMax` | `-1.0` / `1.1` / `5.0` — `:25-27` | same | **YES** | — |
| 25 | `epsE` / `epsI` / `theta` | `1.0` / `2.0` / `3.0` — `:31-33` | same | **YES** | — |
| 26 | `volCoef` / `volBlend` / `volSmoothIter` | `0.16` / `0.0005` / `30` — `:34-36` | same | **YES** | — |
| 27 | `kspRelTol` / `kspMaxIts` / `kspSubspaceSize` | `1e-4` / `50` / `50` — `:37-39` | same | **YES** | — |
| 28 | **cell count** | **`NOT MEASURED`** — the tutorial generates the volume mesh from a downloaded surface mesh and publishes no cell count | **`NOT MEASURED` until `P0`** | **YES** (both unknown) | our own A6 build of this recipe measured **579,072** cells (`A6-crm-wing/logMeshGeneration.txt:478`) — **that is OUR number for OUR build and is deliberately NOT written into the published column** |
| 29 | `solverName` | `DARhoSimpleCFoam` — `runScript.py:35` | same | **YES** | — |
| 30 | `primalMinResTol` | `1.0e-8` — `:36` | `1.0e-8` | **YES** | — |
| 31 | `primalMinResTolDiff` | **ABSENT from the CRM file** (the MACH wing sets `1e3`) | absent — DAFoam's own default stands | **YES** | **`NOT MEASURED`**; `P0` records the effective value |
| 32 | `ddtSchemes` | `steadyState` — `system/fvSchemes:20` | same | **YES** | — |
| 33 | `gradSchemes` | `Gauss linear` — `:25` | same | **YES** | — |
| 34 | `div(phi,U)` | `Gauss linearUpwindV grad(U)` — **not** `bounded` — `:31` | same | **YES** | — |
| 35 | `div(phid,p)` | `Gauss limitedLinear 1.0` — the transonic pressure-flux scheme — `:35` | same | **YES** | — |
| 36 | all other `div` | `Gauss upwind` / `Gauss linear` as listed — `:32-43` | same | **YES** | — |
| 37 | `laplacian` / `snGrad` / `interpolation` | `Gauss linear corrected` / `corrected` / `linear` — `:53,58,48` | same | **YES** | — |
| 38 | `wallDist` | `meshWave` — `:62` | same | **YES** | — |
| 39 | `nNonOrthogonalCorrectors` | **`0`** — `system/fvSolution:20` | `0`, `3` or `12` — **selected by arm `P1`** | **YES** (`0` is one of the three) | `P1` measures the cost/convergence trade; D6RF10 measured `nNonOrth 3` at 0.117 s/step against `nNonOrth 12` at 4.650 s/step — **×39.7** — but changed three things at once, so each alone is **UNMEASURED** |
| 40 | linear solvers | `(p\|p_rgh\|G)` GAMG/GaussSeidel `relTol 0.1 tolerance 0`; `(U\|T\|e\|h\|nuTilda\|k\|omega\|epsilon)` smoothSolver/GaussSeidel `relTol 0.1 nSweeps 1`; `Phi $p relTol 0 tolerance 1e-6` — `:25-47` | same | **YES** | — |
| 41 | relaxation | fields `(p\|rho) 1.0`; equations `p 1.0`, `(U\|T\|e\|h\|nuTilda\|k\|epsilon\|omega) 0.80` — `:51-59` | same | **YES** | — |
| 42 | `potentialFlow.nNonOrthogonalCorrectors` | `20` — `:64` | `20` | **YES** | — |
| 43 | `controlDict endTime` | `2000` — `system/controlDict:21` | **set by `P1`**, upper bound 5,000 | **NO — Δ7** | her rule 5: the residual tolerance must be an order tighter than the drag change being chased. **Measured: the chased change is `1.0e-5`** (D6R2C's last accepted objective increment was `1.421e-05`), while D6RF10 measured the SIMPLE-vs-SIMPLEC `CD` gap at **`9.852e-05`** — the primal's own convergence error was **ten times the signal** |
| 44 | `writePrecision` / `timePrecision` | `16` / `16` — `:27,30` | same | **YES** | — |
| 45 | `numberOfSubdomains` | `72` — `system/decomposeParDict:18` | `72` | **YES** | the box now reads 96 cores, so 72 ranks fit |
| 46 | `0.orig/U internalField` | `uniform (100 0 0)` while `U0 = 295.0` — `0.orig/U:20` | same | **YES** | **recorded, not corrected**: DAFoam's `primalBC` overwrites the *boundary*, not the internal initial field. A reader who finds `100` in a M 0.85 case should know it is the published initial condition |
| 47 | `designSurfaces` | `["wing"]` — `runScript.py:34` | same | **YES** | — |
| 48 | `function.CD` / `.CL` | `type force`, `source patchToFace`, `patches ["wing"]`, `directionMode parallelToFlow` / `normalToFlow`, `patchVelocityInputName patchV`, `scale 1/(0.5·U0²·A0·ρ0)` — `:44-62` | same | **YES** | — |
| 49 | `adjStateOrdering` | `cell` — `:63` | `cell` | **YES** | — |
| 50 | `adjEqnOption` | `gmresRelTol 1.0e-6`, `pcFillLevel 1`, `jacMatReOrdering natural`, `gmresMaxIters 2000`, `gmresRestart 2000` — `:64-71` | same | **YES** | arm `P2` tightens `gmresRelTol` to `1e-9` **only if** a component moves > 1 % of `‖g‖∞` |
| 51 | `normalizeStates` | `U: U0`, `p: p0`, `T: T0`, `nuTilda: 1e-3`, `phi: 1.0` — `:72-78` | same | **YES** | — |
| 52 | `checkMeshThreshold` | `maxAspectRatio 2000.0`, `maxNonOrth 75.0`, `maxSkewness 5.0` — `:79-83` | same | **YES** | kept verbatim as the *solver's* abort threshold — see row 59 for our own budget |
| 53 | **`transonicPCOption`** | **`2`** — `:84` | **`1`** | **NO — Δ2** | **this lab MEASURED that `2` is dead code for this solver.** `DAResidualRhoSimpleCFoam.C:172-176` accepts only `== 1`; every archived ONERA M6 adjoint ran with the transonic mitigation silently off (**L-40**; `docs/dafoam/PRIOR_WORK_INVENTORY.md` row D-F, causation nailed by a bit-for-bit negative control). Adopting a line measured to be inert is adopting a null |
| 54 | `inputInfo` | `aero_vol_coords: volCoord`; `patchV: patchVelocity`, `patches ["inout"]`, `flowAxis "x"`, `normalAxis "z"` — `:86-95` | same | **YES** | — |
| 55 | `meshOptions` (IDWarp) | `{gridFile: os.getcwd(), fileType: "OpenFOAM", symmetryPlanes: [[[0,0,0],[0,1,0]]]}` — **every IDWarp option left at its default** — `:97-102` | same three keys, **plus every default written out explicitly by name** | **YES** on values | the values are unchanged; **naming them is the change**, so the record says what ran instead of inheriting it by omission |
| 56 | `evalMode` (IDWarp) | not set → IDWarp default **`"fast"`** (`UnstructuredMesh.py:136`) | **`"exact"`** | **NO — Δ3** | `fast` is a KD-tree approximation bounded by `errTol = 5e-4` **relative to `Ldef`**, and `Ldef0` (`kd_tree.F90:1500-1512`) is the max distance from the surface centroid to any surface node — of order the wing's size. Under Δ1 the first cell is `1.35e-6 m`; that tolerance is not obviously below it. Arm `W1` measures the difference |
| 57 | FFD lattice | `FFD/wingFFD.xyz`, plot3d header `12 8 2` = **192 control points** — `FFD/wingFFD.xyz:2`, used at `runScript.py:120` | same | **YES** | — |
| 58 | reference axis / twist DVs | `nom_addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="j")` → `nRefAxPts = 8`; `rot_y`; root twist **not** free → **7 twist DVs** — `:146-154` | same | **YES** | — |
| 59 | shape DVs | `pts = DVGeo.getLocalIndex(0)`; `pts[:,:,:].flatten()`; `PointSelect("list", …)`; `nom_addLocalDV(dvName="shape", pointSelect=PS)` → **192 shape DVs**. **The displacement axis is NOT specified**; the installed pyGeo default stands — `:157-160` | same call, unchanged | **YES** | **`NOT MEASURED`** — `P0` records the effective axis. **A shape DV displacing spanwise instead of vertically would be a silent defect** |
| 60 | DV bounds / scalers | `twist [-10, 10]` scaler `0.1`; `shape [-1, 1]` scaler `10.0`; `patchV [U0, 0]`–`[U0, 10]` scaler `0.1` — `:200-202` | same | **YES** | — |
| 61 | thickness / volume constraints | `nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=25, nChord=30)` bounds `[0.5, 3.0]`; `nom_addVolumeConstraint("volcon", …)` lower `1.0`; `leList`/`teList` from `LE_pt (0.01,0.01,0)`, `break_pt (0.848,1.119,0)`, `tip_pt (2.855,3.755,0)`, chords `1.689 / 1.036 / 0.390` at 1 % and 99 % — `:171-185`, `:206-207` | same | **YES** | — |
| 62 | LE/TE constraints | `nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")`, `("tecon", …, "iHigh")`, both `linear=True` — `:187-188`, `:208-209` | same | **YES** | — |
| 63 | curvature constraint | **NONE in the published setup** | **none registered** | **YES** (both absent) | her rule 4 asks for one. pyGeo's curvature API was **not found by this lane in the installed toolchain** (no container was started), so **no name was written down** (rule 21). **Recorded as NOT SATISFIED** rather than invented |
| 64 | objective / lift constraint | `add_objective("scenario1.aero_post.CD")`; `add_constraint("…CL", equals=CL_target)`; `CL_target = 0.5`; trim by `optFuncs.findFeasibleDesign(…)` — `:28`, `:204-205`, `:268` | `J = 0.25·CD₀₄ + 0.50·CD₀₅ + 0.25·CD₀₆` at `CL = 0.400/0.500/0.600` | **NO — Δ4** | the **published multipoint pattern** is He et al. AIAAJ 2020 **Table 4**: three conditions, weights **0.25/0.50/0.25**, AoA a DV per condition. **Honest caveat: the pattern and the case now come from two different published sources**, which is a real weakening of "verbatim" |
| 65 | optimiser | default **`SLSQP`** (`:15`); a complete IPOPT block is published at `:240-252` | **IPOPT**, at the published `:240-252` settings | **NO — Δ5** | selecting a **published branch of the published file**, not inventing one; the whole A2 ladder, the `OptView.hst` hot start and the stop-rule vocabulary are IPOPT-shaped |
| 66 | `max_iter` | `100` — `:243` | `25` (`S2`), `15` (`S1`) | **NO — Δ6** | a **budget on major iterations, not a convergence tolerance**; a run that reaches it is `GATE REACHED`, never `PASS`. 25 is D6R2C's budget, kept so the two items compare |
| 67 | grid family | **NONE — the published setup is a single mesh** | three levels at `r = 2.000` exactly: `72,384` / **`579,072` (the published mesh)** / `4,632,576` | **NO — Δ8** | her rule 1. **Not invented**: built on D8G's **measured** `cgns_utils` face counts (44,544 → 11,136 → 2,784 → 696, ratio **4.000** each, and `c4` breaks at 3.702 and is excluded), extended so **the published mesh is itself a member of the family** |
| 68 | mesh-quality constraint in the adjoint | **NONE in the CRM file** | `meshQualityKS` on `faceSkewness` and `nonOrthoAngle`, `addToAdjoint: True`, bounds `skewness ≤ 4.0`, `nonOrtho ≤ 70.0` | **NO — Δ9** | **has a published line, just not in this file**: `UBend_Channel/runScript_meshQualityConstraint_v2.py:67-90` and `:212-213` |
| 69 | `forces` function object | **NONE in the CRM `controlDict`** | `forces` added, writing total / pressure / viscous | **NO — Δ10** | DAFoam's `"type": "force"` returns a **total**; her rule 10's shear/pressure split is impossible without it. Published in this exact form at `Airfoil_DynamicStall/…/system/controlDict:59-80` |
| 70 | parameterisation staging | all DVs at once | `S1` = 7 twist + 3 AoA (**10 DVs**), then `S2` = 192 shape + 7 twist + 3 AoA (**202 DVs**) from `S1`'s optimum | **NO — Δ11** | her rule 4: *"local high-frequency modes only after the smooth optimum is found"* |
| 71 | design-step limits | **NONE** beyond the DV bounds | `0.10` on the scaled `shape` ∞-norm, `0.5°` on `twist`, per major | **NO — Δ12** | her rule 11. **The literal first-cell-height sizing is unusable here**: at `1.35e-6 m` on a 1.689 m root chord that is `8.0e-7` chord per step, needing `10⁴`–`10⁵` majors. Rule 11 is recorded **PARTIALLY SATISFIED** |
| 72 | who enforces the quality budget | the solver's own `checkMesh` verdict — `runScript.py:79-83` | **our own instrument**, reading the as-run mesh and refusing in our code at `nonOrtho ≤ 70.0` | **NO — Δ13** | **MEASURED: the solver's non-orthogonality clause never refuses on this family.** `O_mp`: **202** mesh-check blocks, **76 over 70.0**, worst **`80.90429398`**, and **all 202** print `Non-orthogonality check OK.` `FM10`: **6 of 6** over, worst **`79.21261137`**, and **zero** `Failed 1 mesh checks.` The refusal channel is **live** — the same `O_mp` log carries four `Failed 1 mesh checks.`, all aspect-ratio. A budget that delegates its stop to a channel measured not to stop is not a budget |

**ROW COUNT: 72 listed, of which 59 are parameter rows.** Grouped rows (7, 24–27, 37, 40, 41) carry
several published values each. **Deviations: 13** — Δ1 (rows 12, 13, 21, 22), Δ2 (53), Δ3 (56),
Δ4 (64), Δ5 (65), Δ6 (66), Δ7 (43), Δ8 (67), Δ9 (68), Δ10 (69), Δ11 (70), Δ12 (71), Δ13 (72).
**Rows 28, 31, 59 and 63 are `NOT MEASURED` or absent on both sides and are marked as such rather
than filled with a guess.**

## d.3 What this section does not claim

- **The registration it publishes is a DRAFT and is not frozen.** No gate here is in force.
- **Deviation Δ1 is priced both ways and is awaiting Sanaa's decision**: verbatim wall-function
  **24,900 core-min / $21.29 derived**; with Δ1 **58,800 core-min / $50.27 derived**; **×2.36**.
  Dollars are **DERIVED, NOT MEASURED** — the box cannot read its own billing.
- **The cell count is not known** until the mesh is built (row 28), and our A6 number is ours.
- **The census in §d.0 is the supervisor's**, relayed and labelled; this lane did not re-derive it.
- **The upstream `checkMesh` behaviour in row 72 is a defect candidate only and is NOT FILED
  anywhere.** No filing is drafted or pending. **Filing is Sanaa's alone.**

**SUBMISSIONS PARKED.**
---
---

# cfd — DrivAer, PPTC VP1304, ONERA M6 and DARPA SUBOFF

**Section owner:** cfd. **Written 2026-09-13** by a cfd `lab-lane` for `cfd-supervisor`.
**This section is an APPEND under this file's stated protocol and edits nothing above it.**

🔴 **DISCLOSURE, BECAUSE IT IS THIS LANE'S OWN ERROR AND HIDING IT WOULD BE WORSE THAN MAKING IT.**
This lane checked for this file at the start of its task and found none; the dafoam section landed
at commit `cdcf5f4ea` while this lane was working. This lane's first commit,
**`83ca9e61ce66a64101a3a9f9b591a41630d0ef40`, OVERWROTE the shared preamble and the entire dafoam
`CRM_Wing` section** — 146 lines — instead of appending beneath them. **Nothing was lost: the
content is restored here byte-for-byte from `HEAD~1` and prefix byte-identity is asserted below.**
The cause was writing a whole file rather than re-reading it immediately before the write, on a
shared path, under concurrency. **Recorded so the next lane on this file does not repeat it.**

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

## 1. DrivAer

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

## 2. PPTC VP1304

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

## 3. ONERA M6

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

## 4. DARPA SUBOFF

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

## 5. WHAT THIS DOCUMENT SURFACED THAT WAS NOT ALREADY ON RECORD

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

---

## 7. ADDENDUM, 2026-09-13, cfd lane — THREE SUPERVISOR RULINGS LANDED, AND THREE CLAIMS CORRECTED BEFORE THEY ENTERED THIS FILE

**This is an APPEND. Nothing above it is altered** — prefix byte-identity asserted at commit against
the pre-append bytes, per this file's own protocol. **It does not move any gate, threshold, cap or
label**; §5.6's proposals remain proposals.

### 7.1 🔴 THE MESH COMPUTE IS FIRST COMPUTE. R5's GATES ARE CLOSED, AND R5 SAYS OTHERWISE.

**Ruled by `cfd-supervisor` on this lane's correction.** `R5_SIZING_PROBE` ran to **rc = 0,
`ALL_STEPS_OK`, 191.73 core-min**, with `log.blockMesh`, `log.surfaceFeatureExtract`,
`log.decomposePar`, `log.snappyHexMesh` (an `End` line present), `log.reconstructParMesh`,
`log.checkMeshFull` and `log.checkMeshPlain`. **Rule 2 says "before any run", not "before any
solve."** That build consumed compute and produced the artifact M1 gates on.

🔴 **`DRIVAER_R5_WALLFUNCTION_RANS_PREREGISTRATION_DRAFT.md` still reads "No compute has run against
this document: verified at the run root /home/ubuntu/certonomous-runs/, which holds no R5 directory."
THAT SENTENCE IS NOW FALSE**, and anyone reading it is reading a false sentence. Two R5 directories
exist at `verification/runs/navier_class/DRIVAER/`. **This file does not edit R5** (rule 6); the
correction is the supervisor's to land as a dated addendum there.

**This lane repeated that stale sentence in §1 earlier tonight on the strength of the registration's
own words, and the supervisor then ruled on it.** Both of us quoted a document instead of reading
the disk. **Recorded because it is the same failure as §7.4's, one level up.**

### 7.2 🔴 AND THE R5 MESH BUILD IS RUNNING AS THIS ADDENDUM IS WRITTEN

Measured by this lane at **2026-09-13 18:26:30 UTC** (`date -u` run first — a rate or staleness
judgement made without a clock audit is worthless):

- `r5_wallfunction/log.snappyHexMesh` mtime **18:26:05**, **25 seconds old**; **202 files** in that
  run root modified within 10 minutes; `processor0/constant/polyMesh/{owner,points}` still being
  written.
- The log ends mid-`Smoothing displacement ...` with **no `End` line**, and `BUILD_RC` carries rc
  entries for `blockMesh`, `surfaceFeatureExtract` and `decomposePar` only — **`snappyHexMesh` has
  not recorded an rc.** That is a build **in progress**, not a failed one.
- Process sweep (run **last**, because fleet agents are invisible to `pgrep`): `build_r5.sh full 16`
  → `run_build.sh medium … 16` → `mpirun -np 16 snappyHexMesh -overwrite -parallel`, under
  `PRED_GIB=140`.

**NOTHING IN THAT RUN ROOT IS TOUCHED BY THIS LANE, AND THE SEQUENCING OF §7.3'S FIX DEPENDS ON IT.**

### 7.3 🔴 D7, REWRITTEN: THE DEFECT IS PROSPECTIVE, AND THE WINDOW TO FIX IT IS NARROW AND OPEN

**§1.5's row and §5.1 stand as measurements. What changes is where the repair goes.**

**Answered exhaustively: NOTHING converts `nut` between `0.orig` and `0`.**

| step | finding |
|---|---|
| `build_r5.sh`, all 119 lines | creates only `system/` and `constant/triSurface/` (line 71). **Zero occurrences of `0.orig`, `restore0Dir` or `nut`.** A mesh builder; it touches no field |
| `write_solver_case.py` | the **only** writer of `0.orig` (`launch_stage_a.sh:11` names it in its refusal). Its own line 12: *"It writes `0.orig/`, NEVER `0/`."* `nut` is `nutkWallFunction` at **:137** (floorNoSlip) and **:138** (the `".*"` default) |
| `launch_stage_a.sh:24`, `launch_r2_solve.sh:32` | the only creators of `0/`, both a plain `cp -r 0.orig 0`. The `touch 0/U 0/p 0/k 0/omega 0/nut` that follows is the **rule-4 age-guard** touch — mtime, not content |
| **measured, not inferred** | in `r2_medium`, a case that actually staged and ran, **`diff 0.orig/nut 0/nut` is IDENTICAL.** The copy demonstrably converts nothing, on a real case, at real stage time |

🔴 **THERE IS NO STAGED `0/nut` TO CORRECT.** Neither R5 root has `0.orig` or `0` **at all** — checked
on both. The defect lives in the **writer**, and the file that would carry it **has not been written
yet**. The build in §7.2 will finish and `write_solver_case.py` will then be run against it to create
`0.orig`. **That is the window, it is open now, and it closes when that command runs.**

**The supervisor's ruling, recorded:** the **case conforms to the registration**, never the reverse —
R5 registers `nutUSpaldingWallFunction`, so the writer must emit it. **That is not moving a gate
after first compute; it is making reality match a registered value, the only direction available
once gates are closed.** And it must go **further than flipping the default**: the argument is
**required with no default**, so the writer **refuses to write a case whose wall treatment nobody
stated**. Three reasons, his: other arms legitimately use `nutk` and `floorNoSlip` should keep it; the
value was hardcoded **twice**, which is **L-607's shape — one quantity in two places, and the one you
did not rewrite wins**; and **a default is what let this happen**, because the arm that needed
Spalding got it as a registered one-change and every arm after inherited `nutk` in silence.

**The proposed diff is drafted, compiles, and is NOT APPLIED.** It is filed as a repository artifact
at **`cases/navier_class/DRIVAER/PROPOSED_WRITER_WALL_TREATMENT_FIX.md`** — **not in scratch, which is
never a handoff channel (L-186)**. It is the supervisor's `SUPERVISION_CHARTER` §3 check 1, read as a
diff, personal and undelegated. **This lane did not apply it and `git diff` on
`write_solver_case.py` is empty.**

### 7.4 THE MECHANISM, WHICH IS THE REUSABLE PART

`r2c_coarse_blended_R2/THE_ONE_CHANGE.diff`, verbatim:

```
--- .../r2_coarse/0.orig/nut
+++ .../r2c_coarse_blended/0.orig/nut
-        type            nutkWallFunction;
+        type            nutUSpaldingWallFunction;
```

**Spalding was the R2c arm's registered ONE CHANGE, applied on top of the `nutk` baseline. It was
never the baseline.** R5 §2.1 says *"which this lab already runs on every DrivAer vehicle patch"* —
**generalising one arm's registered change into a standing property of the lab** — and R5 then stages
from `r2_medium`, the arm that never had it.

**That sentence travelled upward.** The supervisor reports having relayed *"our wall treatment is
already the published one"* to the chief on its strength, **without asking which arm R5 stages
from**. It is true of the blended arm and false of the baseline. **A claim made against a state that
had moved — the same family as the stale-index and stale-blob findings, and as §7.1 above.**

### 7.5 THE CONTROLS, BECAUSE THE NULL IS ONLY WORTH SOMETHING WITH THEM (rule 3)

- **The reader is not blind to Spalding:** it found `nutUSpaldingWallFunction` at
  `r2c_medium_blended_R3/0.orig/nut:37`.
- **The grep that returned 0 on `build_r5.sh` fires when there is something to find:** on a planted
  file carrying `restore0Dir` and `cp -r 0.orig 0` it counts **2**; on `build_r5.sh`, **0**.
- **The layer-phase grep is not blind either:** `r2_medium/log.snappyHexMesh` carries **16
  `Extruding` lines**, the last reading *"Extruding 64470 out of 80974 faces (79.618149%)"*.

**A zero from a reader not shown able to see a non-zero is not evidence.**

### 7.6 🔴 THREE CLAIMS CORRECTED BEFORE THEY ENTERED THIS FILE

**All three were relayed to this lane for inclusion. This lane checked them instead of writing
them, and all three were wrong in the direction that would have flattered us.**

**(a) "No retrieved case tree ships a `snappyHexMesh` log" — FALSE AS A BLANKET.** **Six do**, all in
the Alletto tree's `membranBCSend/testCases/…` membrane cases. **The control proves the finder is not
blind: it sees 18 in our own DrivAer tree.** Written as stated, this file would have carried a false
sentence.

**The narrower claim is true, defensible, and is the one that matters:** **none of the six cases
behind §0.4's stack table ships a snappy log** — not Wolf Dynamics coarse or fine, not
`occDrivAerRotMesh`, not `OneraM6Wing` — and **the six logs that do exist contain zero `Extruding`
lines** (only 2 files in all three trees mention extrusion at all, and both are `log.extrudeMesh`, a
different utility). **So no published stack value in §0.4 may be cited as having extruded. They are
REQUESTS, NOT ACHIEVEMENTS — L-590 at the scale of an entire evidence base.** *(The supervisor has
landed this as `MESH_STANDARD.md` §17, commit `64d33975d`.)*

**(b) "Our 0.480" — MISATTRIBUTED. 0.480 IS NOT OURS.** It is **DrivAerML's** 12 mm stack expressed
on **our** 25.0 mm level-4 cell — R5 §2.2, line 90: *"Against the source's 12 mm stack on our 25.0 mm
level-4 (medium) surface cell — 0.48 c."* **Ours are 1.6808 (built, measured) and 0.474 (registered,
not yet built).** §0.4's own table has this right; the sentence beneath it reading *"Ours at 0.480
extrudes"* inherits R5's phrasing and **should read "the source's recipe at 0.480 extrudes."**
Flagged rather than silently edited, because the line sits above the fold in a Sanaa-facing document
and the supervisor may prefer to reword it himself.

**(c) "Our 0.480 remains the only stack this lab has measured extruding" — WRONG TWICE, AND IN OUR
FAVOUR.** Neither 0.480 nor 0.474 has ever been measured extruding by this lab:

| stack | status, measured |
|---|---|
| **0.480** | **never built by us** — it is the source's ratio, not a mesh of ours |
| **0.474** | **never built** — `R5_SIZING_PROBE` ran `addLayers false` by design (castellation-only sizing probe, **0 `Extruding` lines, correctly**); `r5_wallfunction` has `addLayers true` but **has not reached the layer phase** and is still running (§7.2) |
| 🔴 **1.6808** | **the ONLY stack this lab has measured extruding** — and it extruded **partially**: `r2_medium` **79.62 %** of faces, **2.895 of 5** layers; `r2_coarse` **72.27 %**, **2.503 of 5** |

**So the honest statement is the reverse of the one offered:** the lab's only extrusion evidence sits
at the stack §0.4 calls collapsing, and **R5's 0.474 is a prediction with no achieved-coverage
measurement behind it** — which is exactly why gate **L1** is registered on **achievement**, not on
request, and why **L1 FAIL means no solve is launched.**

### 7.7 D8 — THE SUPERVISOR WITHDREW THE COMPETING RECOMMENDATION, AND SANAA HAD ALREADY RULED

**Recorded per the supervisor's instruction.** He recommended registering **Wolf Dynamics** for
DrivAer (complete, self-contained, ships its own STL, no geometry deviation) and has **withdrawn
that recommendation**, in his words reasoning *"about convenience while you were reasoning about the
experiment"*: `[WD]` is the **original TUM DrivAer, a HALF model at 30 m/s with ν = 1.5881e-05**, so
reproducing it exactly reproduces **a different experiment from the one gate C2 is anchored on**.

🔴 **And it was not a lane's call to begin with: Sanaa ruled it herself.** Owner directive **#30-31**,
recorded byte-exact by the chief at commit **`b821405af`**: ***"occDrivAerStaticMesh is the DrivAer
case."*** **This lane had not seen that directive when it wrote D8**, and reached the same conclusion
from the velocity, viscosity, body and solver. **The agreement is corroboration, not authority — the
authority is hers.**

**§5.6's D8 stands as written: `[OCC]` for conditions, numerics and BCs; `[WD]` for snappyHexMesh
practice. Two trees, two purposes.** The disagreement that produced it is resolved and **both
positions are left on the record**, because the reasoning is what makes the ruling checkable.

### 7.8 THE SHARED-FILE LESSON, IN THE WORDING THE SUPERVISOR ADOPTED

> **Re-read immediately before any whole-file write on a shared path** — and treat the **mandatory
> post-commit verify as the backstop that makes an incident repairable rather than a silent loss.**

It earned itself twice tonight. **It was applied to this very append:** the file was re-read from
`HEAD` and `cmp`-ed against the working copy immediately before writing, and the prefix assert is
re-run at commit.

