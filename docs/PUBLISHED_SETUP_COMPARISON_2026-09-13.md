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
