# Curriculum D6R3 — **DRAFT, NOT FROZEN.** The D6R2 multipoint wing optimisation re-run under the owner's standing rules 1–32

> **STATUS: DRAFT. THIS DOCUMENT IS NOT FROZEN, NO GATE IN IT IS IN FORCE, AND NOTHING IT REGISTERS
> AUTHORISES ANY COMPUTE.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`, who
> freezes it personally after reading it. Until a freeze sha exists, every number below is a
> proposal. **This item has burned 0 core-min and started no container.**
> **Nothing here is sent, filed, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7 —
> **SUBMISSIONS PARKED**). No agent message is Sanaa's consent (rule 9).

**Item id:** `D6R3`. **Parent:** `cases/dafoam/ladder-a/A2/curriculum_D6R2C/PREREGISTRATION.md`
(frozen `7f685867d`, four addenda, v1.4).
**Registers under:** `docs/dafoam/SHAPE_OPTIMIZATION_STANDING_RULES.md` rules **1–32**
(hers 1–16, this family's 17–32), adopted into `DAFOAM_CHARTER.md` **§22**; and
`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md` **§G** (the published-setup rule,
line 239).

---

## 0. WHAT D6R3 IS, IN ONE PARAGRAPH, AND WHY IT IS A RE-RUN AND NOT A NEW CASE

D6R2/D6R2C optimised the MACH tutorial wing at three lift points and produced a weighted-drag
reduction of **24.732 %** (`O_mp_GRADE.json`, `G2` PASS, ratio 0.752677). **That figure is
withdrawn** — `DAFOAM_CHARTER.md` §22.2 — because it was measured on the deformed optimisation mesh
and has never been confirmed on a mesh the optimiser never saw. The one attempt to supply that
confirmation, `FM10`, is **`NOT A RESULT`** on a **PRODUCER** defect (the design variables were
applied twice; `d6r2c_freshmesh.py:423-425`), and **every mesh cause class was excluded by
measurement** (§22.3). **D6R3 re-runs that optimisation — same wing, same solver family, same
parameterisation, same three lift points, same weights — designed from the start so that the number
it produces is a fresh-mesh number at matched lift on a mesh in the asymptotic range.** The parent's
§10 reserved `D6R3` for the `DARhoSimpleCFoam` model rung; §3 below takes that reservation up,
because **rule 5 cannot be satisfied without it** and the parent's own words were that the rung was
*"deliberately NOT taken here"*, not that it was wrong.

---

## 1. THE PUBLISHED SETUP THIS REGISTRATION STARTS FROM (Sanaa §G), AND HOW IT WAS VERIFIED

Sanaa, 2026-09-13 ~17:05Z, byte-exact (`…96CORE_ALLOCATION…md:239`): *"For any public case, the lab
starts from a published OpenFOAM setup of that case — mesh recipe, layer settings, schemes, wall
treatment — ingested into the knowledge base before the first registration. Inventing a setup for a
case someone has already run in this solver is refused."*

### 1a. The primary source — the published DAFoam tutorial, already on this box

| field | value |
|---|---|
| repository | `https://github.com/DAFoam/tutorials.git` (`git remote -v`) |
| local clone | `/home/ubuntu/dafoam-tutorials` |
| HEAD at this draft | `d3b7e38b058aba2a98a74092e15c41ec455c570d`, 2026-05-16 15:58:25 -0500, *"Updated VSP script for ADODG"* |
| the case | `MACH_Tutorial_Wing/` |
| `runScript_AeroOnly.py` | md5 `2906d52a5dbed2bacbaeaf85a37d3fe8` |
| `genWingMesh.py` | md5 `dab5e959187ab2e2bfb4e2c0ded0feb6` |
| surface geometry | `mdolab_wing_surface_mesh.cgns`, fetched by `preProcessing.sh:15` from `https://github.com/dafoam/files/releases/download/v1.0.0/`; a copy is on disk at `/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/mdolab_wing_surface_mesh.cgns` (192,512 B, mtime 2021-02-28) |

**Nothing was fetched for this draft.** The clone, the surface geometry and the three papers were
already on disk; they were read, not retrieved.

### 1b. Title-page verification of the papers (`CLAUDE.md` rule 15)

Verified **by independent extraction of page 1 of each PDF** (`pdftotext -f 1 -l 1`), read against
the title, authors and venue on that page — **not** by filename, file type, hash or sidecar. Each
PDF's own first page carries the claimed article; each `.txt` sidecar's head reproduces it.

| PDF | md5 | page-1 title / authors / venue, as printed |
|---|---|---|
| `docs/papers/adjoint_and_optimization/he_mader_martins_maki_aiaaj2020_dafoam_j058853.pdf` | `bd592e7ea1a5a3c2b9361d43f840f43b` | *DAFoam: An Open-Source Adjoint Framework for Multidisciplinary Design Optimization with OpenFOAM* — He, Mader, Martins, Maki — **AIAA Journal**, doi 10.2514/1.J058853 |
| `…/he_mader_martins_maki_caf2018_discrete_adjoint_openfoam.pdf` | `5c27b30cbe47bbf0b136fde2ed6170d5` | *An Aerodynamic Design Optimization Framework Using a Discrete Adjoint Approach with OpenFOAM* — He, Mader, Martins, Maki — **Computers & Fluids** 168 (2018) 285–303 |
| `…/kenway_mader_he_martins_pas2019_effective_adjoint_100542.pdf` | `6b17ccec2a27ab5bc57c13e51b346da9` | *Effective Adjoint Approaches for Computational Fluid Dynamics* — Kenway, Mader, He, Martins — **Progress in Aerospace Sciences**, doi 10.1016/j.paerosci.2019.05.002 |

### 1c. Claim → source → gate, for every setting this registration adopts

Every row is read from the published file by this lane. "**=**" means adopted unchanged;
"**Δ**" means a stated departure, justified in the section named.

| setting | published value | source line | D6R3 | where |
|---|---|---|---|---|
| free stream | `U0 = 100.0`, `p0 = 101325`, `T0 = 300`, `nuTilda0 = 4.5e-5`, `aoa0 = 4.0`, `A0 = 45.5` | `MACH_Tutorial_Wing/runScript_AeroOnly.py:24-31` | **=** | §3 |
| Mach | `M = U0/√(γRT0) = 100/347.189 = 0.288028` — **SUBSONIC** | derived from `:24`, `:27` | **=** | §3 |
| viscosity | `mu = 1.8e-5`, `Pr = 0.7`, `molWeight 28.97`, `Cp 1005` | `constant/thermophysicalProperties` | **=** | §5 |
| turbulence model | `SpalartAllmaras`, `Prt 1.0` | `constant/turbulenceProperties` | **=** | — |
| solver | `DARhoSimpleFoam`, `primalMinResTol 1.0e-8`, `primalMinResTolDiff 1e3` | `runScript_AeroOnly.py:35-37` | **Δ** → `DARhoSimpleCFoam` | §6 |
| wall treatment | `useWallFunction: True`; `0.orig/nut` = `nutUSpaldingWallFunction` | `:43`; `0.orig/nut` | **Δ** → wall-resolved | §5 |
| `fvSchemes` | `steadyState`; `Gauss linear`; `div(phi,U) bounded Gauss linearUpwindV grad(U)`; all other `div` `bounded Gauss upwind`; `laplacian Gauss linear corrected`; `snGrad corrected`; `wallDist meshWave` | `system/fvSchemes` | **=** | — |
| `fvSolution` | `p\|p_rgh\|G` GAMG/GaussSeidel `relTol 0.1`; `U\|T\|e\|h\|nuTilda\|k\|omega\|epsilon` smoothSolver `relTol 0.1`; relax `p 0.30`, `rho 0.3`, equations `0.70`; `nNonOrthogonalCorrectors 0` | `system/fvSolution` | **Δ** on relaxation + `nNonOrth` only | §6 |
| `controlDict` | `endTime 1000`, `deltaT 1`, `writeControl timeStep`, `writeInterval 1000`, `writePrecision 10` | `system/controlDict` | **Δ** `endTime` only | §6 |
| mesh recipe | `cgns_utils coarsen` **once**, `python genWingMesh.py`, `plot3dToFoam -noBlank`, `autoPatch 60 -overwrite`, `createPatch -overwrite`, `renumberMesh -overwrite` | `preProcessing.sh:23-29` | **=** (the pipeline) | §4 |
| extrusion (layers) | `N 39`, `s0 1.0e-3`, `marchDist 300.0`, `cMax 0.1`, `unattachedEdgesAreSymmetry True`, `outerFaceBC farfield`, `autoConnect True`, `families wall`; `epsE/epsI/theta/volCoef/volBlend/volSmoothIter/kspreltol` **all commented out** | `genWingMesh.py:14-42` | **Δ** `N`, `s0` only | §4, §5 |
| warping | `meshOptions = {gridFile, fileType "OpenFOAM", symmetryPlanes [[[0,0,0],[0,0,1]]]}` — i.e. **every IDWarp option left at its default** | `runScript_AeroOnly.py:89-94` | **=**, defaults named explicitly | §7 |
| adjoint | `gmresRelTol 1.0e-6`, `pcFillLevel 1`, `jacMatReOrdering rcm` | `:63` | **=** | §6 |
| `normalizeStates` | `U: U0`, `p: U0²/2`, `T: T0`, `nuTilda: 1e-3`, `phi: 1.0` | `:64-70` | **=** | — |
| `checkMeshThreshold` | `maxAspectRatio 1000.0`, `maxNonOrth 70.0`, `maxSkewness 5.0` | `:71-75` | **=** | §8 |
| shape DVs | `nom_addLocalDV("shape", pointSelect=all FFD pts)`, bounds `[-1, 1]`, scaler `10.0` | `:149-152`, `:174` | **=** | §6b |
| twist DVs | `nom_addRefAxis(xFraction=0.25, alignIndex="k")`, `rot_z`, **root twist NOT free**, bounds `[-10, 10]`, scaler `0.1` | `:138-146`, `:173` | **=** | §6b |
| AoA DV | `patchV = [U0, aoa0]`, `U` pinned, AoA `[0, 10]`, scaler `0.1` | `:166`, `:175` | **=** | §6a |
| lift constraint | `add_constraint("…CL", equals=CL_target, scaler=1.0)` | `:179` | **=** | §6a |
| thickness / volume | `nom_addThicknessConstraints2D(nSpan=10, nChord=10)` bounds `[0.5, 3.0]`; `nom_addVolumeConstraint` lower `1.0`; `leList [[0.1,0,0.01],[7.5,0,13.9]]`, `teList [[4.9,0,0.01],[8.9,0,13.9]]` | `:155-158`, `:180-181` | **=** | §6b |
| LE/TE | `nom_add_LETEConstraint("lecon", volID=0, faceID="iLow")` / `("tecon", …, "iHigh")`, linear | `:160-161`, `:182-183` | **=** | §6b |
| optimiser | IPOPT, `tol 1.0e-5`, `constr_viol_tol 1.0e-5`, `mu_strategy adaptive`, `nlp_scaling_method none`, `limited_memory_max_history 10`, `alpha_for_y full`, `recalc_y yes` | `:212-223` | **=** | §14 |
| trim before iter 1 | `optFuncs.findFeasibleDesign([…CL], ["patchV"], targets=[CL_target], designVarsComp=[1])` | `:241` | **=** | §6a |

### 1d. The multipoint layer — also published, and D6R2 already matched it

The tutorial is single-point. The **multipoint** structure is published in
**He et al., AIAA Journal 2020, §3.1 and Table 4** (`…j058853.txt:795-905`), and **D6R2 already
matched it row for row** — which this registration records so no reader thinks the multipoint
design was invented here:

| published (Table 4, AIAAJ 2020 §3.1) | D6R2/D6R2C | D6R3 |
|---|---|---|
| objective `f = Σ wᵢ CD_i` | `J = 0.25·CD04 + 0.50·CD05 + 0.25·CD06` | **=** |
| weights **0.25, 0.5, 0.25** | 0.25, 0.50, 0.25 | **=** |
| three CL constraints, one per condition | `cl04/cl05/cl06` at 0.400/0.500/0.600 | **=** |
| AoA a design variable **per condition** (3) | `patchV_<pt>` per condition | **=** |
| twist, **root twist fixed** | 7 twist DVs, root not free | **=** |
| FFD `Δz`, thickness ≥ 0.5 baseline, volume ≥ baseline, LE/TE fixed | identical in kind | **=** |
| warping: *"an analytic inverse-distance method [72] through the IDWarp package"* (`:890`) | IDWarp | **=** |
| **mesh: 548,352 cells, average y⁺ 33.7** (`:880-882`) | **38,304 cells, mean y⁺ 321.95** | see §4, §5 |

**The last row is the finding of this section and it is the reason rules 1 and 2 exist.** The
published multipoint wing optimisation of this family ran on a mesh **14.3× finer** than D6R2's
(548,352 / 38,304) at an average y⁺ **9.6× lower** (33.7 / 321.95). The tutorial mesh is a teaching
mesh — `preProcessing.sh:22` even carries the comment *"coarsen the surface mesh three times"* over
a single live `cgns_utils coarsen` call — and **D6R2 optimised on it.** Nothing was invented; a
teaching mesh was used for a production claim.

**What was NOT invented, stated because it was queried:** **M = 0.288 is the published value**
(`runScript_AeroOnly.py:24`, `:27`), not a lab choice. The parent's ADDENDUM 2 corrected only the
*word* "transonic", never the number.

---

## 2. WHAT THIS DRAFT DOES **NOT** RESOLVE, AND MUST NOT BE FROZEN AS RESOLVED

**The operating point is open at the owner's desk.** §3 carries **two** complete, separately-sourced
operating-point blocks. **Exactly one is live at freeze; the supervisor deletes the other by
striking it in the freeze commit.** No number outside §3 depends on which is chosen except the cost
model, which is given for both (§15).

---

## 3. THE OPERATING POINT — ONE SWAPPABLE BLOCK, TWO CANDIDATES

### 3A. **OPTION A — the D6R2 re-run.** MACH tutorial wing, M = 0.288, taken whole from the published tutorial.

```
geometry      mdolab_wing_surface_mesh.cgns  (MACH_Tutorial_Wing)
U0 = 100.0 m/s   p0 = 101325 Pa   T0 = 300 K   nuTilda0 = 4.5e-5   aoa0 = 4.0 deg   A0 = 45.5 m^2
a  = sqrt(1.4 x 287 x 300) = 347.189 m/s   ->   M_inf = 0.288028   COMPRESSIBLE SUBSONIC
CL targets 0.400 / 0.500 / 0.600     weights 0.25 / 0.50 / 0.25
solver        DARhoSimpleCFoam   (departure, Sec. 6)
source        MACH_Tutorial_Wing/runScript_AeroOnly.py:24-31 (md5 2906d52a5dbed2bacbaeaf85a37d3fe8)
```

**This is the option that makes D6R3 a re-run of D6R2.** Same geometry, same FFD, same DV counts,
same targets, same weights. **The word "transonic" is not used of this case** (parent ADDENDUM 2:
maximum *local* Mach measured at 0.380; no shock exists and no shock figure can be produced).

### 3B. **OPTION B — the transonic alternative.** CRM wing, M = 0.850, taken WHOLE from `CRM_Wing`.

```
geometry      CRM_surfMesh.cgns  (CRM_Wing)  -- root chord 1.689, break 1.036, tip 0.390 m
U0 = 295.0 m/s   p0 = 101325 Pa   T0 = 300 K   nuTilda0 = 4.5e-5   aoa0 = 2.11031707 deg
A0 = 3.407014 m^2   ->   M_inf = 295/347.189 = 0.849678
CL_target 0.5 (published, single point)
solver        DARhoSimpleCFoam   (published)
extrusion     N 53, s0 1.0e-4, marchDist 25 x 3.758151 = 93.954, ps0 -1.0, pGridRatio 1.1,
              cMax 5.0, epsE 1.0, epsI 2.0, theta 3.0, volCoef 0.16, volBlend 0.0005,
              volSmoothIter 30, kspRelTol 1e-4, kspMaxIts 50, kspSubspaceSize 50
adjoint       gmresRelTol 1e-6, pcFillLevel 1, jacMatReOrdering "natural",
              gmresMaxIters 2000, gmresRestart 2000, adjStateOrdering "cell"
checkMesh     maxAspectRatio 2000.0, maxNonOrth 75.0, maxSkewness 5.0
source        CRM_Wing/runScript.py    (md5 0de915d21166a91a9a54b37ab11214cf) :24-31, :36-84
              CRM_Wing/genWingMesh.py  (md5 af9b63c2a22886b40c2309b298288cb8) :18-39
```

**THREE THINGS A READER MUST BE TOLD BEFORE OPTION B IS CHOSEN, and all three are measurements or
published lines, not opinions:**

1. **Option B is a DIFFERENT GEOMETRY, so it is not a re-run of D6R2.** `CRM_Wing` is the NASA CRM
   wing (root chord 1.689 m, span 3.755 m), not the MACH tutorial wing (mean chord 3.276 m, span
   13.9 m). Choosing B changes the wing, the FFD, the reference area and the mesh, not only the
   Mach number. **Running the MACH tutorial wing's subsonic mesh and subsonic solver at M 0.85 is
   exactly the invention §G refuses** and is not offered here.
2. **The published `CRM_Wing` case is SINGLE-POINT.** Making it multipoint at three CLs is a
   departure from the published setup; it would be justified by AIAAJ 2020 Table 4's multipoint
   pattern, but the pattern and the case would then come from two different sources.
3. **`"transonicPCOption": 2` in the published file (`CRM_Wing/runScript.py:84`) is DEAD CODE for
   this solver.** Measured by this lab and recorded at `docs/dafoam/PRIOR_WORK_INVENTORY.md` D-F /
   L-40: `DAResidualRhoSimpleCFoam.C:172-176` accepts **only `== 1`**, and *every* archived ONERA M6
   run ran with the solver's own transonic mitigation silently off. **If Option B is taken, the
   registered value is `transonicPCOption: 1`, as a stated departure with that measurement as its
   reason** — adopting a published line the lab has already measured to be inert would be adopting
   a null.

**Lab prior work on Option B, stated so it is not rediscovered:** `A6` ran `CRM_Wing` at
**579,072 cells**, np=4, `DARhoSimpleCFoam`, `run_model` only, **28.73 core-min** for 1000 steps; it
**never converged** (`grep -c "satisfied the prescribed tolerance"` → 0; `nuTilda` plateaued at
t≈600 and needs **≈ 15,573 further iterations ≈ 419 core-min** to cross 1e-8) and **its adjoint has
never been attempted** (`Main iteration` / `KSP Residual` appear **zero** times in all four A6 logs;
`Global Adjoint States: 5,244,840`; memory predicted 95–116 GiB against the then 30 GiB box).
**The memory blocker is no longer binding: this box now reads 96 cores and 739 GiB total / 640 GiB
available** (measured at this draft, 2026-09-13 17:10Z). **The cost of a CRM adjoint remains
UNMEASURED**, and §15B prices it as an estimate, labelled as one.

---

## 4. RULE 1 — **THE BASELINE GETS ITS GRID FAMILY FIRST**, and the optimisation mesh is chosen by measurement

> *"Optimize on a mesh in the asymptotic range. The baseline gets its grid family first; the
> optimization mesh is the coarsest level whose drag is within the band of the fine level."*

### 4a. The three levels, and the refinement ratio

The family is built by the **published pipeline** (`preProcessing.sh:23-29`), unchanged, with only
the `cgns_utils` coarsening depth and the two extrusion numbers varying. The existing lab harness
`/home/ubuntu/certonomous-runs/A2-GC-wing-grid-convergence/L1/mesh.sh` already implements exactly
this (`coarsen0 / coarsen1 / coarsen2 / refine1`) and is the instrument to reuse, not to rewrite.

**Measured basis for the surface counts:** the current mesh is `nCells: 38304` (`base/constant/
polyMesh/owner.gz` FoamFile `note`, corroborated by the 4-way decomposition 9504+9600+9608+9592),
built from `coarsen1` at `N = 39` nodes = **38 wall-normal cells**, so the surface carries
**38304 / 38 = 1008 cells** exactly. `cgns_utils coarsen` halves each structured surface direction.

| level | surface | surface cells | wall-normal cells | `s0` (m) | **cells** | ratio |
|---|---|---|---|---|---|---|
| **L3 coarse** | `coarsen2` | 252 | 42 | `1.6e-6` | **10,584** | — |
| **L2 medium** | `coarsen1` (the published depth) | 1,008 | 84 | `8.0e-7` | **84,672** | ×8.000 |
| **L1 fine** | `coarsen0` | 4,032 | 168 | `4.0e-7` | **677,376** | ×8.000 |

**REFINEMENT RATIO `r = 2` EXACTLY, IN ALL THREE DIRECTIONS** — two surface directions by
`cgns_utils`, the wall-normal direction by doubling the cell count **and halving `s0` together**, so
the near-wall spacing refines with the rest of the mesh. `h` ratio `= 8^(1/3) = 2.000`; the cell
counts are in the exact ratio 8.000 : 1 : 1/8 by construction, not approximately.

**The extrusion is self-consistent and the model is cross-checked against a measurement.** For a
geometric layer distribution `s0(r^n − 1)/(r − 1) = marchDist`, the implied near-wall growth ratios
are **L3 1.5518, L2 1.2439, L1 1.1149**. Applying the same model to the *current* mesh
(`s0 1e-3`, `n 38`, `marchDist 300`) predicts **1.3563** against the **measured median 1.3303**
(`FINDING_NOTE_D6R2C_LAYER_GROWTH.md` §2, 1008 chains, 37,296 pairs) — **agreement to 1.9 %**. The
model is therefore anchored, not assumed.

### 4b. **PRECONDITION, MEASURED AT MESH BUILD, WITH A REGISTERED FALLBACK**

`coarsen2` requires the `coarsen1` surface block dimensions to be even in both directions. **This is
NOT MEASURED at this draft** (`cgns_utils` is inside the container; no container was started).
**If `coarsen2` refuses, the family shifts up one level:** L3 = `coarsen1`, L2 = `coarsen0`,
L1 = `refine1`, with `s0` and the wall-normal counts shifted correspondingly, and **the optimisation
mesh becomes 677,376 cells or larger** — a cost consequence, registered in §15 as the
`FAMILY_SHIFT` contingency, not a surprise.

### 4c. The band, and the choice rule

- **The measured quantity is the baseline weighted drag `J₀ = 0.25·CD₀₄ + 0.50·CD₀₅ + 0.25·CD₀₆`,
  at matched lift** (rule 3 binds the family too: each level is trimmed to `CL = 0.400/0.500/0.600`
  before its drag is read).
- **BAND: a level qualifies if `|J(level) − J(L1)| / J(L1) ≤ 0.010` (1.0 %).** Basis: the smallest
  weighted-drag change this optimisation is asked to resolve is **1.0e-5 in `J`** (§6c, measured),
  which on `J ≈ 0.0306` is **0.033 %**; a 1 % band is **30×** looser than the resolution floor and
  is therefore a discretisation-error criterion, not a noise criterion. It is also the band inside
  which a 10 % drag reduction (the parent's `G2` bar) remains a 10 % drag reduction to one
  significant figure.
- **THE OPTIMISATION MESH IS THE COARSEST QUALIFYING LEVEL.** If **L3** qualifies, the optimisation
  runs on L3 and L2 becomes the rule-13 "next finer level". If only **L2** qualifies, the
  optimisation runs on L2 and L1 is the rule-13 level. **If NO level qualifies — i.e. `|J(L2) −
  J(L1)|/J(L1) > 0.010` — the grid family is `GATE FAIL`, D6R3 does NOT proceed to an
  optimisation, and the finding is that this case has no asymptotic range at any mesh this lab can
  afford.** That outcome is registered here, before the run, so it cannot later be read as a
  setback to be worked around.

### 4d. **NO ROACHE TRIPLE IS CLAIMED AND NO GCI IS QUOTED IN THIS ITEM**

`CLAUDE.md` rule 5 binds: a triple that is not `CONVERGING` is `NOT A RESULT`. **This registration
does not claim a Roache triple.** The three levels exist to *select the optimisation mesh*, not to
extrapolate. **If and only if** the three `J` values are monotone and the observed order lies in a
physically admissible range will a GCI at `Fs = 1.25` be reported, and it will be reported **beside**
the selection, never as the selection's justification. A non-`CONVERGING` triple makes the reported
`J` values `NOT A RESULT` **as grid-convergence evidence**; it does **not** by itself void the
selection, which rests on the band, and this document says so before the numbers exist.

---

## 5. RULE 2 — **WALL-RESOLVED, y⁺ ≈ 1, CHECKED ON THE BASELINE.** A STATED DEPARTURE FROM THE PUBLISHED SETUP

> *"Wall-resolved, not wall functions. Wall functions make friction a strong function of y+, and y+
> drifts under warping. y+ ≈ 1 on the optimization mesh, checked on the baseline."*

### 5a. **THE DEPARTURE, NAMED**

**Every published DAFoam setup for this wing and its siblings is WALL-FUNCTION.** Measured across
the tutorial clone by this lane: `MACH_Tutorial_Wing`, `Onera_M6_Wing`, `CRM_Wing` and
`ADODG3_Wing` all carry `"useWallFunction": True` and `0.orig/nut` of type
`nutUSpaldingWallFunction`. Across the whole clone, `nutUSpaldingWallFunction` appears **16** times
against `nutLowReWallFunction` **5**. **Her rule 2 is therefore a departure from the published
setup, not an adoption of it, and it is registered as one:**

| | published | D6R3 | reason |
|---|---|---|---|
| `primalBC.useWallFunction` | `True` (`runScript_AeroOnly.py:43`) | **`False`** | rule 2 |
| `0.orig/nut` wall BC | `nutUSpaldingWallFunction` | **`nutLowReWallFunction`** | the DAFoam-published wall-resolved BC, used at `UBend_CHT/aero/0.orig/nut` |
| `genWingMesh.py` `s0` | `1.0e-3` (`:25`) | **`8.0e-7`** at L2 | §5b |
| `genWingMesh.py` `N` | `39` (`:24`) | **`85`** nodes = 84 cells at L2 | §5b |

**The reason, in her words and in a number.** Wall functions make friction a strong function of y⁺,
and y⁺ drifts under warping. **Measured on this exact case:** the deformed-versus-fresh comparison
of D6R2 ran at y⁺ medians **247 (deformed) versus 223 (fresh)** (`DAFOAM_CHARTER.md` §22.3) —
a 10.8 % drift in the very quantity the wall function is a function of, produced by warping alone.
**This registration removes that degree of freedom rather than monitoring it.**

**A supporting published caution, cited rather than invented:** Kenway et al., PAS 2019, records
*"linear system stiffness, especially for the viscous layer near the wall when a y⁺ = 1"*
(`…100542.txt:2869`) — i.e. the published literature says this choice costs adjoint conditioning.
It is priced in §15 with that factor **named as an assumption**.

### 5b. **THE SIZING, DERIVED TWO INDEPENDENT WAYS, AND THE CONSERVATIVE ONE IS REGISTERED**

**Anchor 1 — MEASURED y⁺ on the baseline, scaled.** From the converged tail of
`ARM0_4R_20260913T000043Z_152777.log` (the baseline geometry, `shape ≡ twist ≡ 0`, AoA 4.0°, on the
current mesh at `s0 = 1.0e-3`): **y⁺ min `68.787`, max `1266.542`, mean `321.951`**, stable to eight
figures over the last 30 prints. Since `y⁺ ∝ y_wall` at fixed flow,

```
s0 for  max y+ = 1 :  1.0e-3 / 1266.542 = 7.896e-07 m
s0 for mean y+ = 1 :  1.0e-3 /  321.951 = 3.106e-06 m
```

**Anchor 2 — the flat-plate correlation, computed from the PUBLISHED fluid properties, independent
of any lab run.** `rho = p0/(R·T0) = 1.176829 kg/m³`, `nu = mu/rho = 1.529534e-05 m²/s` (from
`mu = 1.8e-5`, `constant/thermophysicalProperties`); mean chord `= A0/span = 45.5/13.89 = 3.2757 m`;
`Re_mac = 2.1417e7`. Schlichting 1/5-power `Cf = 0.0592·Re^-0.2 = 0.002024`, `u_τ = 3.1811 m/s`, so
`y⁺ = 1` at a first-cell **centre** distance of `4.808e-6 m`, i.e. a first-cell **height** of
`9.62e-6 m`. (1/7-power gives `8.96e-6 m` — the two correlations agree to 7 %.)

**REGISTERED: `s0 = 8.0e-7 m` at the L2 optimisation mesh** — the **conservative** of the two
anchors (anchor 1's max-y⁺ scaling). Predicted on the baseline: **max y⁺ 1.013, mean y⁺ 0.258,
min y⁺ 0.055**. Under anchor 2 the same `s0` would read max y⁺ ≈ 0.083. **The two anchors bracket
the answer by a factor of 12 and the finer bound is taken**, because a mesh that is too fine at the
wall costs cells and a mesh that is too coarse at the wall voids the rule.

**MESH-SIZE CONSEQUENCE, which is what the cost turns on:** going from `s0 = 1.0e-3` to
`s0 = 8.0e-7` is a factor **1,250** in near-wall spacing but only **84 / 38 = 2.211** in wall-normal
cells, because the layer distribution is geometric over a `marchDist` of 300 m: the extra 7.13
e-foldings of near-wall refinement cost `ln(1250)/ln(1.2439) = 32.6` layers, and the growth ratio
*improves* from 1.3563 to 1.2439 at the same time. **L2 = 1008 × 84 = 84,672 cells, a factor
2.2105 on D6R2's 38,304.** That is the whole cost consequence of rule 2 on this case, and it is
small because the case's mesh was never layer-limited.

### 5c. **THE GATE (rule 2), AND IT IS A MEASUREMENT, NOT THE PREDICTION**

- **`Y1` — the baseline on L2 measures `max y⁺ ≤ 2.0` and `median y⁺ ≤ 1.0`**, read from the
  primal's own `yPlus min/max/mean` print at the converged tail plus a `yPlus` field write.
- The `max ≤ 2.0` clause is **this lab's reading of "y⁺ ≈ 1" for the single worst face** and is
  stated as a reading: the maximum sits at the leading-edge stagnation band where the sublayer is
  thinnest, and a single face at y⁺ 2 is still inside the region SA integrates to the wall. **The
  binding clause is the median.**
- **If `Y1` misses, `s0` is divided by the measured `max y⁺` and the mesh is rebuilt — ONCE.**
  A second miss is `GATE FAIL` on the mesh family and D6R3 does not proceed to an optimisation.
- **`Y1` is checked on the BASELINE**, as her rule says, before any design variable moves.

---

## 6. THE SOLVER AND THE CONVERGENCE — RULE 5, AS ARITHMETIC

> *"Fully converged primal and adjoint at every iteration. Residual tolerance an order tighter than
> the change in drag the optimizer is chasing."*

### 6c. **THE DRAG CHANGE BEING CHASED — MEASURED, NOT ASSERTED**

From `O_mp/d6r2c_evals.jsonl`, over the **35** successful (`fail = 0`) objective evaluations of the
D6R2C production run, the increments `|ΔJ|` between consecutive accepted evaluations:

| quantity | value |
|---|---|
| median `\|ΔJ\|` | **5.589e-04** |
| last accepted increment | **1.421e-05** |
| smallest observed increment | **5.237e-07** |

**REGISTERED: the drag change being chased is `ΔJ_chased = 1.0e-5`** — the order of the increments
the optimiser was still accepting at the end of D6R2C's run, and one decade above the smallest it
ever took.

**THEREFORE, one order tighter: `the primal's own CD uncertainty must be ≤ 1.0e-6`.** That is the
registered requirement, stated in the quantity of interest rather than in a residual, because a
residual is not a drag.

### 6d. **WHY D6R2 COULD NOT HAVE MET THIS, AND THE ONE MEASURED RESIDUAL→DRAG MAPPING THE LAB HAS**

**D6R2C's primals never converged.** Measured: **48 of 48 `Primal min residual` blocks in the `O_mp`
log are failures**, minimum failed residual `1.000006e-05`, maximum `7.312316e-05`, against a fail
threshold of `primalMinResTol 1.0e-8 × primalMinResTolDiff 1e3 = 1.0e-5`. And **52 of 87 objective
evaluations carried `fail = 1`** (parent §A3.4).

**The mapping from residual level to drag error, measured once, on this exact wing** (D6RF10
`D6RF10_GRADE_RECORD.md` §5): `DARhoSimpleFoam` (SIMPLE, `nNonOrth 3`) floors at
`p_first_uncorrected = 1.681172924e-05` and reads `CD 0.01849343377`; `DARhoSimpleCFoam` (SIMPLEC,
`nNonOrth 12`, `relax_p 0.70`) reaches `6.3233727e-06`, plateaued to a relative spread of
`1.4707e-07` over `[1500, 2000]`, and reads `CD 0.01859195417`. **`ΔCD = 9.85204e-05` = 0.5327 %.**

**THE ARITHMETIC THAT MAKES THIS REGISTRATION NECESSARY:** D6R2's optimiser was chasing drag changes
of **1.0e-5** with a primal whose own distance-from-converged is **9.85e-5** — **ten times larger
than the signal.** Rule 5 is not a refinement of D6R2; it is the statement that D6R2's gradient
signal was below its own numerical noise floor.

### 6e. **THE REGISTERED SOLVER CHANGE, AND IT IS THE RUNG THE PARENT RESERVED**

`curriculum_D6R2C/PREREGISTRATION.md` §10: *"It does not claim the primal reaches the A2 accept
floor of 1.0e-5. D6RF10 measured that this `DARhoSimpleFoam` configuration does not
(`p_first_uncorrected = 1.681e-05`, GATE FAIL) and that a `DARhoSimpleCFoam` configuration does
(`6.323e-06`). **That solver change is `D6R3`, a separate registered successor, and is deliberately
NOT taken here** — its adjoint has never been exercised on this case."*

**D6R3 takes it.** `solverName: DARhoSimpleFoam → DARhoSimpleCFoam`. The parent's own caution —
*"its adjoint has never been exercised on this case"* — is answered by arm **`P1`** (§6f), which
exercises it before any optimisation is authorised.

### 6f. **ARM `P1` — THE PRIMAL-CONVERGENCE AND CONFIGURATION ARM. IT RUNS FIRST AND ITS RESULT SELECTS THE CONFIGURATION.**

**The cost of "converged" is the single largest unknown in this registration and it is NOT
guessed — it is measured.** D6RF10 measured `DARhoSimpleFoam` at `nNonOrth 3` running **flat at
0.117 s/step** end to end, and `DARhoSimpleCFoam` at `nNonOrth 12` at **4.650 s/step** — a factor
**39.7**, caused (measured, `D6RF10_GRADE_RECORD.md` §6) by **157 of 273 p-solves saturating the
linear solver's `nIters: 1000` cap** once `initRes` falls near 1e-8, not by the outer loop.
**D6RF10 changed the solver, `nNonOrth` and `relax_p` together, so the cost of SIMPLEC alone is
UNMEASURED.** Registering `nNonOrth 12` on the strength of that one bundled result would be a
40× cost decision taken on an unattributed measurement.

`P1` runs on the **L2 baseline, one condition (`cl05`), 5,000 SIMPLE steps**, over six registered
configurations — `{SIMPLE, SIMPLEC} × nNonOrth {0, 3, 12}` at the published relaxation, plus
`relax_p 0.70` on the SIMPLEC rows — and records, per configuration, the full `CD(step)` trace and
the per-equation residual trace.

- **`P1-G1` — a configuration PASSES if the last 500 steps' `CD` peak-to-peak is ≤ `1.0e-6`**
  (the §6c requirement) **and** its per-equation residuals are all monotone-or-plateaued over that
  window. This is the binding gate and it is stated in drag, not in residuals.
- **`P1-G2` — the registered primal budget is then the smallest step count at which `P1-G1` holds**,
  and that number replaces the `endTime` of the published `controlDict`. **The registered upper
  bound for costing is `endTime 3000`** (§15); a configuration needing more is reported and the
  cheapest passing configuration is taken.
- **`P1` also DELIVERS the residual→drag-error curve** — `CD` against residual level, on ONE solver
  and ONE mesh — which the D6RF10 pair could not, because it varied two things at once.
- **`O_mp` DOES NOT LAUNCH UNTIL `P1` READS `PASS`.** A `P1` `GATE FAIL` on every configuration is a
  finding about this case's numerics and is reported as one; it is **not** a reason to widen the
  `1.0e-6` requirement.
- **PLANTED CONTROL (rule 3).** `P1`'s reader plants `PLANT = 1.234e-03` into the `CD` trace it has
  read back **from disk** and **REFUSES (exit 2)** if the plant leaves any configuration at `PASS`.
  A reader that cannot see a drag perturbation 1,000× the gate cannot certify the gate.

### 6g. The adjoint side of rule 5

`gmresRelTol 1.0e-6` is **adopted unchanged** from the published setup (`:63`), and `P1`'s successor
arm `P2` records, at the baseline design on L2, the **measured** total-derivative change between
`gmresRelTol 1e-6` and `1e-9`. **REGISTERED: if any component of `dJ/dx` moves by more than 1 % of
`‖dJ/dx‖∞` between the two, `gmresRelTol` is tightened to `1e-9` for the production run** and the
cost consequence is reported. This is registered before the measurement exists.

---

## 6a. RULE 3 — TRIM IN THE LOOP. EVERY EVALUATION AT MATCHED LIFT BY CONSTRUCTION.

> *"Angle of attack is a design variable with lift as an equality constraint at every condition, so
> every evaluation is at matched lift by construction. Drag is never compared across different
> lifts."*

**Adopted unchanged from the published setup — D6R2 already had this and it is not a change:**
`patchV_<pt> = (U, AoA)` per condition with `U` pinned at `U0`, AoA in `[0, 10]°`, scaler `0.1`
(`runScript_AeroOnly.py:166`, `:175`); `add_constraint("<pt>.aero_post.CL", equals=target_i,
scaler=1.0)` (`:179`); and `optFuncs.findFeasibleDesign` before iteration 1 (`:241`).

**WHAT IS NEW, AND IT IS THE CLAUSE THAT MATTERS.** D6R2C had trim in the loop **and still finished
off-target**: its final design missed the lift equalities at `cl04 5.539e-04`, `cl05 1.210e-03`,
`cl06 2.787e-03` against a `1.0e-3` gate — a `GATE FAIL`, corroborated to seventeen digits by
IPOPT's own `Constraint violation....: 2.7869956827836218e-03`. **Having AoA as a DV does not
guarantee matched lift; only a converged constraint does.** D6R3 therefore registers:

- **`T1` — NO DRAG RATIO IS FORMED AT AN UNCONVERGED CONSTRAINT.** Every reported `CD` or `J`, at
  every stage — grid family, checkpoints, after-protocol — is accompanied by its three `|CL_i −
  target_i|`, and **a value whose worst miss exceeds `1.0e-4` is reported as `NOT A RESULT` for the
  purpose of any ratio** (rule 19: every factor of a ratio carries its own condition). `1.0e-4` is
  **ten times tighter** than the parent's `G3` and is the level at which a lift mismatch's induced
  drag contribution falls below `ΔJ_chased = 1.0e-5`.
- **`T2` — the after-protocol numbers (§11) are produced by an EXPLICIT TRIM to the targets, not by
  reading whatever lift the optimiser left**, and the trim's convergence is part of the artefact.
- **The iteration cap is NOT a convergence criterion** (parent §1a, unchanged): a run that stops at
  the cap with `inf_pr` above `constr_viol_tol` is reported as stopped at the cap.

---

## 6b. RULE 4 — REGULARISED DESIGN SPACE, AND SMOOTH MODES FIRST

> *"Bounds on control-point motion, thickness and curvature constraints, and a smooth
> parameterization (fewer, smoother modes first; local high-frequency modes only after the smooth
> optimum is found). Surface wiggles are the cheapest way to fool a discrete drag."*

**Adopted unchanged from the published setup:** shape bounds `[-1, 1]` at scaler `10.0` (`:174`);
twist bounds `[-10, 10]°` at scaler `0.1` (`:173`); thickness `0.5 ≤ t/t₀ ≤ 3.0` on a 10×10
span×chord grid (`:157`, `:180`); volume `V/V₀ ≥ 1.0` (`:158`, `:181`); LE/TE linear equality
constraints (`:160-161`, `:182-183`).

**WHAT IS NEW — the staged parameterisation, which the published setup does not have:**

| stage | design variables | why |
|---|---|---|
| **S1 — SMOOTH** | **7 twist + 3 AoA = 10** | the smooth modes alone. Twist and trim carry the span-load redistribution that is the physical mechanism of induced-drag reduction on a wing. |
| **S2 — LOCAL** | **96 shape + 7 twist + 3 AoA = 106** (the D6R2 set) | started **from S1's converged optimum**, not from the baseline. |

**S2 does not launch until S1 has converged or reached its cap.** Her rule says local high-frequency
modes come *"only after the smooth optimum is found"*, and this is that sentence made into two arms.

**THE CURVATURE CONSTRAINT — AND AN HONEST GAP.** Her rule 4 asks for *"thickness and curvature
constraints"*. The published setup has thickness and volume; **it has no curvature constraint**, and
`pyGeo`'s curvature-constraint API was **not verified by this lane in the installed toolchain** (no
container was started). **Registered as `nom_addCurvatureConstraint` PENDING VERIFICATION**: at
freeze the supervisor either (a) names the verified API call and its registered bound, or (b)
**strikes the row and records rule 4's curvature clause as NOT SATISFIED**, with the LE/TE
constraints and the `[-1, 1]` bounds as the only regularisers. **A name that has not been found in
the toolchain is not registered here** — that is rule 21 and it is the defect that cost L-579.

**THE WIGGLE DETECTOR, which is registered and does exist.** Per accepted design, the reader
computes the **second difference of the FFD `Δz` along each chordwise row** and records its maximum.
**A monotone rise in that quantity across majors, with no change in span load, is the wiggle
signature** and is reported at every checkpoint beside the drag split (§9). It is a **reported
diagnostic, not a gate** — and it is named as one, because a printed quantity annotated as
non-binding is worse than one never computed unless its status is stated.

---

## 7. RULE 6 — WARP SETTINGS THAT CARRY THE NEAR-WALL LAYERS. **VERIFIED IN IDWARP'S OWN SOURCE.**

> *"Warp settings that carry the near-wall layers with the surface (rotation of the near-wall region
> with the surface, deformation region scaled to the geometry) so first-cell height and
> orthogonality are preserved under displacement, not stretched — verify the setting names in the
> warp's documentation and register them."*

**Her rule says verify. Verified by reading IDWarp's own source and documentation on this box**, at
`/home/ubuntu/certonomous-runs/W5-idwarp-source/idwarp_src` (IDWarp **2.6.2**, the version the
pinned image carries per `docs/dafoam/TOOLCHAIN_INVENTORY.md:121`). **No name below was written down
before it was found in the toolchain.**

| option | default | **where the NAME is defined** | **where the VALUE is USED** | what it does, read from the source |
|---|---|---|---|---|
| **`useRotations`** | `True` | `idwarp/UnstructuredMesh.py:138` | `:1058` → `warp.gridinput.userotations`; consumed at `src/modules/kd_tree.F90:1110` and `:1339` | Guards `GETROTATIONMATRIX3D`, which builds the per-node rotation `Mi` from the surface normal's change (`normals0 → normals`) and applies it to every **non-corner** surface node. **This IS her "rotation of the near-wall region with the surface", by name and by line.** |
| **`LdefFact`** | `1.0` | `UnstructuredMesh.py:133` | `:1053` → `warp.gridinput.ldeffact`; `src/warp/warpMesh.F90:39` and `src/warp/warpDeriv.F90:59` set `tp%Ldef = tp%Ldef0 * LdefFact`; `Ldef0` computed at `src/modules/kd_tree.F90:1500-1512` | `Ldef0` is **the maximum distance from the surface-node centroid to any surface node** — the deformation length scale taken from the geometry's own size. `LdefFact` scales it. **This IS her "deformation region scaled to the geometry", by name and by line.** |
| `aExp` | `3.0` | `:131` | `:1055`; weight `Wi = Ai·[(Ldef/dist)^aExp + alpha^bExp·(Ldef/dist)^bExp]`, `kd_tree.F90:685` | near-field decay exponent of the inverse-distance weight |
| `bExp` | `5.0` | `:132` | `:1056`; same expression | far-field decay exponent |
| `alpha` | `0.25` | `:134` | `:1054`; `tp%alphaToBexp = alpha**bExp`, `kd_tree.F90:1528` | blend between the two decay terms |
| `zeroCornerRotations` | `True` | `:139` | `tp%isCorner` guard at `kd_tree.F90:1110`, `:1339` | suppresses rotation at corners |
| `cornerAngle` | `30.0` | `:140` | `:1060` → `gridinput.cornerangle` | angle defining a corner |
| `errTol` | `0.0005` | `:135` | `:1061` → `gridinput.errtol` | fast-evaluation error tolerance |
| `evalMode` | `"fast"` | `:136` | `:1063-1065` | `fast` uses the KD-tree approximation; `exact` does not |
| `bucketSize` | `8` | `:142` | `:1062` → `warp.kd_tree.bucket_size` | KD-tree bucket size |
| `symmTol` | `1e-6` | `:137` | `:1057` | symmetry-plane matching tolerance |
| `symmetryPlanes` | `None` | `:130` | `_setSymmetryConditions`, `:754-766` | the plane list; the published setup supplies `[[[0,0,0],[0,0,1]]]` |

**THE PUBLISHED SETUP SETS NONE OF THESE.** `MACH_Tutorial_Wing/runScript_AeroOnly.py:89-94` passes
only `gridFile`, `fileType` and `symmetryPlanes` — **every warp option runs at its default.**
D6R2 therefore already ran with `useRotations = True` and `LdefFact = 1.0`. **This is recorded, not
claimed as a fix:** rule 6's two named mechanisms were already active on D6R2, and the deformed-
versus-fresh gap happened anyway — which is consistent with §22.3's measured conclusion that the
cause was **PRODUCER**, not warp.

**REGISTERED FOR D6R3:** every option above is written **explicitly** into `meshOptions` at its
published-default value, so the record names what ran instead of inheriting it by omission — with
**two departures**, both registered here and both to be **measured**, not assumed, by arm `W1`:

| | published default | D6R3 | reason |
|---|---|---|---|
| `evalMode` | `"fast"` | **`"exact"`** | `fast` is a KD-tree approximation whose error is bounded by `errTol = 5e-4` **relative to `Ldef`**; on a mesh whose first cell is `8.0e-7 m` against an `Ldef` of order the wing's own size, that tolerance is not obviously below the first-cell height. `exact` removes the question. |
| `LdefFact` | `1.0` | **candidate `1.0`, decided by `W1`** | rule 6 asks that the deformation region be scaled to the geometry; `Ldef0` already is. `W1` measures whether a smaller `LdefFact` (a more local deformation) preserves the near-wall layers better. |

**ARM `W1` — THE WARP-SETTING MEASUREMENT, run on the L2 baseline before `O_mp`.** Apply a
registered representative design perturbation (the D6R2C optimum's own `shape`/`twist` vector,
already on disk) and **measure**, on the warped mesh: minimum first-cell height relative to
baseline, worst-cell skewness, maximum non-orthogonality, minimum volume, and the y⁺ range.
Configurations: `evalMode ∈ {fast, exact}` × `LdefFact ∈ {0.5, 1.0, 2.0}`. **REGISTERED: the
configuration taken is the one with the largest minimum first-cell-height ratio that also satisfies
§8's quality budget; ties break to the published default.** `W1` is a selection arm, not a gate on
the wing.

**Toolchain note, carried so it is not lost:** the pinned image `dafoam-idwarp-rot:v1`
(`sha256:2927768a16ac…`) carries a **rebuilt `libidwarp.so`** (md5 `85f59e87253e0a71a813f64ca6e4c425`)
containing this lab's IDWarp rotation-derivative patch (+44 lines, `vectorUtils_b.f90` /
`vectorUtils_d.f90`). **That patch is on the derivative path of exactly the `useRotations` mechanism
rule 6 names.** It is **NOT FILED** upstream and stays that way (rule 7).

---

## 8. RULE 7 — THE PER-ITERATION QUALITY BUDGET, EVALUATED ON THE **AS-RUN** POINTS

> *"A quality budget per iteration: worst-cell skewness, minimum first-cell height relative to
> baseline, minimum volume, and the y+ range. Logged every iteration; crossing any threshold stops
> the run."*

### 8a. The thresholds, anchored on measured values and on published lines

| quantity | threshold | anchor |
|---|---|---|
| **max non-orthogonality** | **≤ 70.0°** | DAFoam's own declared `checkMeshThreshold.maxNonOrth` for this case (`runScript_AeroOnly.py:73`), **and** the published DAFoam mesh-quality **constraint** upper bound `optProb.addCon("nonOrtho", lower=0, upper=70.0)` (`UBend_Channel/runScript_meshQualityConstraint_v2.py:213`). Two published sources, the same number. |
| **worst-cell skewness** | **≤ 4.0** | the published constraint bound `optProb.addCon("skewness", lower=0., upper=4.0)` (`…v2.py:212`). Tighter than DAFoam's `maxSkewness 5.0` threshold, and taken from the published *constraint* rather than the published *abort threshold*, deliberately. |
| **min first-cell height / baseline** | **≥ 0.80** | the D6R2 deformed-vs-fresh comparison measured first-cell height median within **1.6 %** (`§22.3`); 0.80 is a 20 % allowance, 12× that observed drift. |
| **min cell volume** | **> 0** strictly, and **≥ 0.10 ×** the baseline minimum | D6R2 measured **zero** negative or degenerate volumes (`§22.3`); the ratio clause is the early-warning. |
| **max aspect ratio** | **≤ 1000.0** | DAFoam's declared `checkMeshThreshold.maxAspectRatio` (`:72`). |
| **y⁺** | **median ≤ 1.5 and max ≤ 3.0** | 1.5× and 1.5× the §5c baseline acceptance, allowing measured drift under warping without permitting a return to wall-function territory. |

### 8b. **THE THRESHOLDS ARE WHAT D6R2 ACTUALLY BREACHED, AND THE BREACH WAS NEVER MEASURED**

Rule 31, measured: **the only `checkMesh` on disk for FM10 reports "Mesh OK" at max
non-orthogonality `66.32` — that is the AS-BUILT mesh, before the second warp. The mesh that
actually ran measures `79.21`, and the optimisation mesh measures `71.24`. Both breach DAFoam's
declared `maxNonOrth = 70.0`. Neither as-run mesh had ever been checked.** And the `O_mp` log
carries **four** `High aspect ratio cells found` trips, worst **`1050.3162`** (parent §A4.3) —
**5.03 % over** the declared `1000.0`.

**THEREFORE, and this is the load-bearing clause of §8:** the budget is evaluated on the
**AS-RUN points, after the final design-variable application**, and its log is **written after** that
application. A quality log written before the last operation that touched the points describes a
mesh no solver saw.

### 8c. **THE PUBLISHED MECHANISM, ADOPTED: the quality budget is also a CONSTRAINT IN THE ADJOINT**

DAFoam publishes a differentiable mesh-quality constraint and this registration uses it rather than
inventing a monitor:

```
"skewness": {"part1": {"type": "meshQualityKS", "source": "boxToCell",
                       "min": [-10,-10,-10], "max": [10,10,10],
                       "coeffKS": 20.0, "metric": "faceSkewness",
                       "scale": 1.0, "addToAdjoint": True}},
"nonOrtho":  {"part1": {"type": "meshQualityKS", "source": "boxToCell",
                       "min": [-10,-10,-10], "max": [10,10,10],
                       "coeffKS": 1.0, "metric": "nonOrthoAngle",
                       "scale": 1.0, "addToAdjoint": True}},
...
add_constraint("skewness", upper=4.0, scaler=1.0)
add_constraint("nonOrtho", upper=70.0, scaler=1.0)
```

**Source: `UBend_Channel/runScript_meshQualityConstraint_v2.py:67-90` and `:212-213`**
(md5 `0d97cb5e619bffe19c8dcc2759c07d09`). The `min`/`max` box is widened to enclose this wing's
domain; the metrics, the KS coefficients, the `addToAdjoint` flag and **both bounds** are the
published values. **D6R2 did not use this and breached both quantities.**

### 8d. The stop clause

**Crossing any threshold in §8a STOPS the run** (her words). Operationally: the run stops, the
current design is checkpointed, the mesh is regenerated from the current smooth surface (§9a), the
gradient is spot-checked on the new mesh, and the optimiser resumes from the current design.
**A stop is recorded as a stop with its crossed quantity and its value, and the cause class is
assigned AT THE STOP** (rule 29), never reconstructed afterwards.

**Directive #17 interaction, stated so it is not confused:** a **quality** crossing stops the run —
that is her rule 7 and it is a physics guard. A **cost cap** crossing does **not** stop anything; it
is REPORTED and the row is graded `NOT A RESULT`, and the cap is never raised (§15).

---

## 9. RULES 8 AND 9 — PERIODIC RE-MESHING, AND FRESH-MESH CHECKPOINTS. **N = 3 MAJORS, DERIVED FROM A MEASUREMENT.**

> 8. *"Every N iterations, or whenever the surface displacement exceeds a registered fraction of the
>    local first-cell height, regenerate the mesh from the current smooth surface, spot-check the
>    gradient on the new mesh, and resume from the current design."*
> 9. *"Every N iterations, evaluate the current design on a freshly generated mesh at matched lift.
>    If deformed-mesh and fresh-mesh drag differ by more than the registered tolerance, the run stops
>    and re-meshes."* — her own line: **the rule that would have caught D6R2 on day one.**

### 9a. **`N = 3` IPOPT MAJORS, and here is the measurement it comes from**

The `O_mp` log's four `High aspect ratio cells found` trips were located by this lane at log lines
22928, 31050, 33015 and 46373. Counting `Starting time loop` occurrences before each: **83, 113, 120
and 170 condition-primals**, out of 198 in a 25-major run of 113 evaluations. **The first mesh-quality
breach therefore appeared at roughly evaluation 28 of 113, i.e. IPOPT major ≈ 6 of 25.**

**`N = 3` is half of 6** — the mesh is regenerated **before** the point at which D6R2C's mesh was
measured to have degraded. Eight re-mesh events over a 25-major run.

### 9b. **HER ALTERNATIVE TRIGGER IS UNUSABLE ON THIS CASE, AND SAYING SO IS THE HONEST ANSWER**

Rule 8 offers *"or whenever the surface displacement exceeds a registered fraction of the local
first-cell height"*. **On a y⁺ ≈ 1 mesh of this case that trigger fires on the first design step and
every step thereafter.** Measured: mid-span camber/chord ran base **0.00196** → optimum **0.04810**
over 25 majors (`§22.3`), i.e. a camber change of 0.0461 chord ≈ **0.151 m** of wall displacement,
about **6.0e-3 m per major**. Against a registered first-cell height of **8.0e-7 m**, the surface
moves **≈ 7,500 first-cell heights per major**.

**REGISTERED: the displacement trigger is NOT used. The fixed `N = 3` and the §8 quality budget are
the triggers.** The ratio above is **reported at every checkpoint** so the record carries the reason.

### 9c. The checkpoint protocol, at every `N = 3` majors

1. **Regenerate** the volume mesh from the current smooth design surface, through the **published
   pipeline unchanged** (`genWingMesh.py` → `plot3dToFoam -noBlank` → `autoPatch 60 -overwrite` →
   `createPatch -overwrite` → `renumberMesh -overwrite`).
2. **Trim to matched lift** on the fresh mesh, all three conditions (rule 3; §6a `T2`).
3. **Evaluate the objective** on the fresh mesh at matched lift.
4. **Spot-check the gradient** on the new mesh (rule 8's own clause) against the deformed-mesh
   gradient at the same design.
5. **Resume from the current design on the fresh mesh.** Accumulated warp error is reset to zero.

### 9d. **THE GATE — `FM_CK`. THIS IS THE ONE THAT WOULD HAVE CAUGHT D6R2.**

- **REGISTERED TOLERANCE: `|J_fresh − J_deformed| / J_fresh ≤ 0.010` (1.0 %)**, with **both sides at
  matched lift** and **both trims converged to `|CL_i − target_i| ≤ 1.0e-4`** (§6a `T1`).
- **Basis for 1.0 %:** it is the same band as the grid-family band (§4c) — a deformed mesh that
  disagrees with a fresh one by more than the level spacing of the grid family is no longer
  measuring the same problem. **And it is a bar D6R2 fails by a wide margin:** D6R2's deformed-vs-
  fresh gap was **139 drag counts** on a `CD` of order 0.023 — of order **6 %**, six times this
  tolerance.
- **A crossing STOPS the run and re-meshes.** It does not adjust the tolerance.
- **GRADIENT SPOT-CHECK TOLERANCE: `1.0e-4` relative per component, normalised by `‖g‖∞`** — the
  same tolerance the parent registered for its rank-agreement check (`§7`), reused so the two
  numbers are comparable, and registered before the arm runs.
- **PLANTED CONTROL (rule 3):** the checkpoint comparator plants `PLANT = 1.234e-03` into the value
  it read back from disk for the fresh-mesh side — separately into `J`, into `cl05`'s `CD` and into
  the gradient — and **REFUSES (exit 2)** if any plant leaves the verdict at `PASS`.
- **RULE 25 CLAUSE, and it is not theoretical here:** the plant is applied at a state where the
  quantity is **non-zero**. `shape ≡ twist ≡ 0` at x0 makes 103 of 106 DV components identically
  zero, and the parent's `X0_GUARD` measured that **all discriminating power sat in 6 components**.
  **The checkpoint comparator counts its informative components, prints the count, and REFUSES below
  a registered floor of 6.**

---

## 10. RULE 10 — SHEAR AND PRESSURE DRAG SPLIT PER ITERATION, AND THE ARTEFACT SIGNATURE

> *"Shear and pressure drag split per iteration… Gain arriving in the spurious or friction component
> with no change in span load or pressure distribution is an artefact signature: stop, re-mesh."*

**The instrument is published within the DAFoam tutorials and is adopted rather than invented.**
DAFoam's own `"type": "force"` function returns a total; the split comes from OpenFOAM's `forces`
function object, used in this form in the published `Airfoil_DynamicStall` tutorials
(`…/system/controlDict:59-80`):

```
functions { forces { type forces; libs ("libforces.so");
                     writeControl timeStep; timeInterval 1; log yes;
                     patches (wing); pName p; UName U; rho rhoInf; rhoInf <rho0>;
                     CofR (...); } }
```

`forces` writes `force.dat` / `moment.dat` with **total, pressure and viscous** columns per time
step. **REGISTERED: `forces` is added to `system/controlDict` for every arm, and the pressure and
viscous components of `CD` are recorded per condition at every evaluation**, alongside the span load
(sectional `CL·c` at the 10 thickness-constraint span stations) and the surface `Cp` distribution at
three registered stations (root, mid, tip).

**THE ARTEFACT SIGNATURE, REGISTERED AS AN ARITHMETIC TEST BEFORE THE DATA EXISTS:**

> **Between two consecutive accepted designs, if `ΔCD_total < 0` while `|ΔCD_pressure| < 0.20 ·
> |ΔCD_total|` — i.e. **more than 80 % of the gain is arriving in the viscous component** — and the
> span load changes by less than 1 % at every station, **the run STOPS and re-meshes**, and the
> event is recorded with both components.

**The threshold is the inverse of a measured fact.** D6R2's deformed-versus-fresh gap was carried
**104.5 % / 102.9 % / 99.6 % by PRESSURE drag**, with viscous drag flat to within **7 counts of its
own value** (`§22.3`). That is the shape of a genuine pressure-driven difference. A *gain* that
arrives the other way round — in friction, with the pressure field unchanged — is the signature her
rule names, and the 20 % split is chosen because D6R2's real effect sat at 100 % pressure and a
five-fold departure from that is not noise.

**REPORTED, NOT GATED, and named as such:** a far-field spurious-drag decomposition is **not
available** in this toolchain (no far-field decomposition exists in DAFoam's function set —
verified by enumerating the `"type"` values across the tutorial clone: `force`, `moment`,
`variance`, `meshQualityKS`, `totalPressure`, `field`, `power`, `wallHeatFlux`, `patchMean`,
`massFlowRate`, and others, **none of them a far-field or spurious-drag decomposition**).
**Her rule 10's "where available" clause is therefore NOT satisfied and this registration says so
rather than substituting something else for it.**

---

## 11. RULE 11 — A TRUST REGION SIZED TO THE FIRST-CELL HEIGHT

> *"A trust region on the design update sized to the first-cell height, so no single step deforms the
> near-wall mesh beyond what the warp preserves."*

**HONEST STATEMENT FIRST: a first-cell-height trust region is not directly expressible on this case,
for the same arithmetic as §9b.** The first cell is `8.0e-7 m`; the wing's chord is `3.28 m`; a step
limited to one first-cell height of surface motion is a step of `2.4e-7` chord, and the optimiser
would need of order `10⁵` majors to travel the distance D6R2 travelled. **Registering that number
would be registering a run that cannot finish.**

**WHAT IS REGISTERED INSTEAD, and it is the mechanism her clause is protecting:**

1. **The binding trust region is the §8 QUALITY BUDGET, applied as an in-adjoint constraint**
   (§8c) — `nonOrtho ≤ 70.0`, `skewness ≤ 4.0`, published bounds. **This is a trust region defined
   by what the warp actually preserves, measured, rather than by a proxy for it.**
2. **An explicit IPOPT step bound, registered and measured against:** the `shape` design variables
   are bounded at `[-1, 1]` at scaler `10.0` (published), and D6R3 additionally registers a
   **per-major move limit of `0.10` on the scaled `shape` vector's `∞`-norm** and `0.5°` on `twist`.
   **Anchor:** D6R2C's measured mid-span camber excursion was `0.00196 → 0.04810` over 25 majors;
   a `0.10` scaled-shape move limit permits that trajectory in roughly the same number of majors
   while forbidding any single step from taking a large fraction of it.
3. **`RULE 11 IS RECORDED AS PARTIALLY SATISFIED.** The first-cell-height sizing she names is not
   used, the reason is the arithmetic above, and the substitute is named. A supervisor who disagrees
   has the numbers to disagree with.

---

## 12. RULES 12–14 — THE AFTER-PROTOCOL. **THE CLAIMED NUMBER IS THE FRESH-MESH NUMBER.**

> 12. *"Fresh mesh, matched lift, all conditions, from scratch. The claimed improvement is the
>     fresh-mesh number. The deformed-mesh number is reported beside it, with the difference
>     disclosed."*
> 13. *"The optimized shape re-evaluated on the next finer family level; the improvement must survive
>     within the band."*
> 14. *"Decomposition on the fresh mesh (shape / twist / trim) before any percentage; drag split on
>     both meshes on the certificate."*

And `DAFOAM_CHARTER.md` §22.2, with teeth: **no shape-optimisation improvement figure leaves this
family unless the number quoted is the fresh-mesh number, at matched lift, on all conditions, from
scratch.**

| arm | what it is | level | gate |
|---|---|---|---|
| **`A12`** | the optimum, **freshly extruded from the optimised surface, from scratch**, trimmed to `CL 0.400/0.500/0.600`, all three conditions | **L2** (the optimisation level) | **`A12-G1`: this is THE CLAIMED NUMBER.** Reported as `J_fresh`, with `J_deformed` **beside it** and `(J_fresh − J_deformed)/J_fresh` **printed**. |
| **`A13`** | the same optimum on the **next finer family level** | **L1** | **`A13-G1`: `\|J_fresh(L1) − J_fresh(L2)\| / J_fresh(L1) ≤ 0.010`** — the §4c band. A miss is **`GATE FAIL`**: *"an optimum that holds on one mesh only is not an optimum."* |
| **`A14`** | the **decomposition** — baseline; baseline + twist only; baseline + twist + trim; full — each **freshly meshed and trimmed** | **L2** | reported; **no percentage is quoted before `A14` exists** (her rule 14). |

**`A12`, `A13` and `A14` all run the BASELINE through the identical path** so that every ratio's
numerator and denominator are measured on the same mesh generation, at the same lift, under the same
DV application (rule 19). **A ratio whose two factors did not is not a number.**

**THE DRAG SPLIT ON BOTH MESHES GOES ON THE CERTIFICATE** (rule 14, §10's `forces` output).

**THE FAILURE PATH IS REGISTERED IN ADVANCE (rule 15 + §22.3's fifth class).** If `A12` or `A13`
misses, the cause class is one of **mesh (warp) / parameterization (wiggles) / trim (lift mismatch)
/ solver / PRODUCER**, and **the class is assigned from a measurement that EXCLUDES the other four**:

| class | the measurement that excludes it |
|---|---|
| mesh (warp) | y⁺ medians, first-cell-height ratio, per-layer thicknesses, negative/degenerate volume count — fresh versus deformed (the §22.3 battery, already built) |
| parameterization | the second-difference wiggle metric of §6b, fresh versus deformed surface |
| trim | `\|CL_i − target_i\|` on **both** sides, against `1.0e-4` (§6a `T1`) |
| solver | `P1`'s residual→drag curve evaluated at both states |
| **PRODUCER** | **the rule-18 surface hash equality against the BASE surface at the moment the DVs are applied** (§13), plus the wall-point fit (`cos∠`, `\|d2\|/\|d1\|`) that measured FM10's double deformation at median `0.99965` / `1.234` |

**An attribution with no exclusion measurement is a hypothesis and is labelled one.**

---

## 13. RULES 17–32 — THE RECORD HALF. WHAT MAKES THE RECORD MATCH THE RUN.

| rule | what D6R3 registers | the artefact that will evidence it |
|---|---|---|
| **17** — gate on the mesh the solver READ | Before `run_model()`, each rank rebuilds the `polyMesh` it loaded from `pointProcAddressing` and the hash is compared for **exact equality** against the generated mesh. **Staging the mesh into every processor case happens BEFORE the model is built and is part of the arm, not a convenience.** *Measured why:* FM8 was graded a fresh-mesh confirmation and the retraction found **1,486 processor meshes scanned, zero matching the freshly extruded mesh.* | `MESH_READ_HASH.json` per arm, per rank, written by the running solver's own process |
| **18** — DVs applied EXACTLY ONCE, proved by hash | At the moment the DVs are applied, the surface hash is compared against the **BASE** surface, not against itself. *Measured why:* FM10 — `surfaceMesh.cgns ≡ surfaceMesh_final.cgns ≠ surfaceMesh_base.cgns`, then the solve phase re-read `dv_star` and set shape/twist/patchV again; the three conditions flew at CL **+0.1493/+0.1516/+0.1524** above target, **30× the finding trigger**. The load-bearing line is `d6r2c_freshmesh.py:423-425`. | `DV_APPLY_GUARD.json`: base-surface md5, pre-apply md5, post-apply md5, and the assertion `pre == base` |
| **19** — no ratio across different meshes, lifts or DV applications | Every reported ratio carries **both** factors' mesh id, both trims' `\|CL − target\|`, and both DV-application hashes. *Measured why:* the **1.2063** ratio relayed upward was a fresh-mesh numerator over a deformed-mesh denominator at incompatible lift and was withdrawn. | every `*_GRADE.json` carries a `ratio_provenance` block or the ratio is not printed |
| **20** — drive the CLI the launcher EMITS | The pre-freeze check executes **the exact command line the launcher writes**, not the graded function. *Measured why:* the FM9 grader's launcher emitted `--log`, the parser rejected it, and the frozen CLI path **could only ever return `NOT A RESULT`** while the selftest was green. | `PREFREEZE_CLI.log`, showing the launcher-emitted argv and its exit code |
| **21** — every instrument in the frozen table EXISTS at its md5 | The pre-freeze check **hashes each row's file and refuses on absence**. *Measured why:* a registration was frozen naming four instruments that did not exist; the table was **true as written**. **And the parent repeated it: `d6r2c_grade.py`, named in its §4, did not exist at its freeze** (parent ADDENDUM 3). | §16's table, each row verified by the pre-freeze check, output in `PREFREEZE_INSTRUMENTS.log` |
| **22** — count EXTERNAL ANCHORS, not gates | §16 states, per gate, **which external anchor** it rests on. The grid family's three levels share one mesher and one solver — **one anchor, three levels** — and §4 says so. `A12` vs `A13` share the optimised surface: **one anchor.** | §16's anchor column |
| **23** — derive every constant from the thing under test, in the same invocation, and USE it | The `A13` band is **propagated through the ratio** from the registered absolute band, in the same invocation, not written down. The `y⁺` re-size factor (§5c) is the **measured** max y⁺, not a pinned number. | each comparator prints `derived_from` beside every constant it used |
| **24** — suspect a SUCCESS as hard as a failure | Every "n converged" count is printed **with its failing partner** (`n_pass`, `n_fail`, `n_total`, and `n_pass + n_fail == n_total` asserted). *Measured why:* `"O_mp converged 88 times"` was false — **35 of 87 succeeded, 52 failed, and `n = 88` was an INDEX, not a count.** | every summary line carries the triple |
| **25** — never gate at a state where the quantity is identically zero | Every planted control is applied at a **non-zero** state, and every guard **counts and prints its informative components and REFUSES below a registered floor**. *Measured why:* the scaler-defect gate sat at `shape ≡ twist ≡ 0` and **could not have fired for any scaler whatsoever**. | `INFORMATIVE_COUNT` printed by each guard |
| **26** — drive every guard to its failing side; check non-finite BEFORE the comparison | Each guard's selftest drives it to **`REFUSE`**, and each refuses on non-finite **before** any comparison. *Measured why:* `abs(nan − x) > tol` is `False`, so a refuse-rather-than-degrade guard written that way **never refuses** — and the parent's `gate_g3` was **one evaluation away** from reporting a `GATE FAIL` manufactured out of NaN arithmetic (7 consecutive failures then one success). | each selftest's refuse-side control, counted |
| **27** — every channel a gate reads has a **writer that ran** | **At freeze, for every file any gate reads, the pre-freeze check names the writer and shows it ran.** *Measured why:* `primal_residual.json` had **four reads, zero writes, zero such files anywhere on disk**, leaving `conv[p] = True` standing for every condition. **THIS ONE IS STILL OPEN AND IS ON SANAA'S DESK**, and D6R3 does not pretend to close it — it registers the check. | `PREFREEZE_CHANNELS.log`: reader, writer, and a witness file produced by the writer |
| **28** — name the reference in every git comparison | Append-only claims are proved by **prefix byte-identity against HEAD's blob** (`cmp -n <pre-append size>`), never by a bare `git diff`. | any addendum to this file carries the `cmp -n` exit code |
| **29** — a crash/stall/refused solve is a FINDING and a FIX | Any such event on D6R3 is triaged on the **mesh → numerics → model** ladder, the cause class is recorded **at the stop**, and the fix is one registered change re-run as a new arm. | `STOP_RECORD.json` per event, written at the stop |
| **30** — cost per EVALUATION, calibrated at completion | §15 states **core-min per objective evaluation and per gradient evaluation separately**; at every process completion the ratio actual/predicted lands in `docs/COST_CALIBRATION.md`. | `COST_CALIBRATION_ROW.D6R3_*.md` per arm |
| **31** — `checkMesh` the mesh that RAN | `checkMesh -allGeometry` is run on the **as-run points, after the final DV application**, for **every** mesh state any number is read from. *Measured why:* the only `checkMesh` for FM10 describes the as-built mesh at `66.32`; the mesh that ran measures **`79.21`**, breaching `maxNonOrth 70.0`, and **neither as-run mesh had ever been checked**. | `CHECKMESH_ASRUN.log` per mesh state, mtime **after** the DV-apply guard's |
| **32** — the fifth cause class, assigned by exclusion | §12's exclusion table. | the `A12`/`A13` grade record |

### 13a. `DAFOAM_CHARTER.md` §22.4 — the three clauses the supervisor checks **personally** at freeze

1. **Every instrument in §16's table exists at its stated md5** — `PREFREEZE_INSTRUMENTS.log`.
2. **The pre-freeze check drives the CLI the launcher emits** — `PREFREEZE_CLI.log`.
3. **Every channel a gate reads has a writer shown to have run** — `PREFREEZE_CHANNELS.log`.

**None of the three can be satisfied by this draft**, because no instrument has been written yet.
**They are the freeze's preconditions and they are what the supervisor is being asked to check.**

---

## 14. ARMS, AND THE ORDER THEY RUN IN

| # | arm | what it is | precondition |
|---|---|---|---|
| 0 | `MESH` | build L3, L2, L1 by the published pipeline; `checkMesh -allGeometry` each | §4b `coarsen2` measured |
| 1 | `Y1` | baseline y⁺ on L2 | `MESH` |
| 2 | `P1` | primal convergence / configuration selection | `Y1` PASS |
| 3 | `W1` | warp-setting selection | `P1` PASS |
| 4 | `GF` | grid family: baseline `J` at matched lift on L3, L2, L1 | `P1`, `W1` |
| 5 | `P2` | adjoint tolerance check (§6g) | `GF` selected a level |
| 6 | `S1` | smooth-mode optimisation (10 DVs) | `GF` PASS, `P2` |
| 7 | `S2` | full optimisation (106 DVs), from S1's optimum, with `N = 3` checkpoints | `S1` |
| 8 | `A12` | fresh mesh, matched lift, all conditions, from scratch — **THE CLAIMED NUMBER** | `S2` |
| 9 | `A13` | the optimum on L1 | `A12` |
| 10 | `A14` | decomposition on the fresh mesh | `A12` |

**Nothing after arm 0 launches until its precondition reads `PASS`.** `O_mp`-class compute (`S1`,
`S2`) is launched by the queue runner, never by hand.

**The optimiser's iteration budget is a BUDGET, not a tolerance** (parent §1a, carried forward):
`S1 max_iter 15`, `S2 max_iter 25`. A run that reaches the cap is reported as having reached the
cap; **`GATE REACHED`**, never `PASS` (`DAFOAM_CHARTER.md` §9).

---

## 15. COST, IN CORE-MINUTES, BEFORE THE RUN (`CLAUDE.md` rule 12; rule 30 per evaluation)

### 15a. The measured anchors — every one from D6R2C's own artefacts, none guessed

| anchor | value | where measured |
|---|---|---|
| **`F` objective evaluation** (3 conditions, `fail = 0`) | **3.263 core-min** (mean of **35**; median 3.273; 48.939 s wall × 4 ranks ÷ 60) | `O_mp/d6r2c_evals.jsonl` |
| **`G` gradient evaluation** | **11.666 core-min** (mean of **26**; median 11.863) | same |
| evaluations per major | **3.48 `F`** and **1.04 `G`** (87 F, 26 G, 25 majors) | same |
| **fresh-mesh evaluation incl. extrusion** | **10.667 core-min** (FM10, 160 s × 4 ranks) | `…FM9…/ledger.txt`, `FM10_GRADE.json` |
| one condition-primal, 1000 SIMPLE steps | **1.237 core-min** (18.56 s wall × 4 ranks) | `O_mp…log`, `ExecutionTime` at `Time = 1000` |
| whole 25-major arm | **672.933 core-min**, **26.917 core-min/major**, ratio actual/predicted **0.856** | `RESULTS.md:645-654` |
| mesh | **38,304 cells** | `base/constant/polyMesh/owner.gz` `note` |

### 15b. The scaling factors, each named, each with what justifies it

| factor | value | justification | tag |
|---|---|---|---|
| **`S_cells`** | **2.2105** | 84,672 / 38,304, exact arithmetic from §4a | `DERIVED` |
| **`S_steps`** | **3.0** | primal budget `endTime 3000` against the published `1000`. A **budget**, not a prediction: `P1` sets the real number and it can only come in lower. | `REGISTERED` |
| **`S_adj`** | **2.0** | adjoint conditioning on a y⁺ ≈ 1 mesh. **THIS IS AN ASSUMPTION, NOT A MEASUREMENT.** Its only support is a published caution: Kenway et al., PAS 2019, *"linear system stiffness, especially for the viscous layer near the wall when a y⁺ = 1"* (`…100542.txt:2869`). **Flagged for calibration at the first `G` evaluation.** | `ASSUMED` |

### 15c. **PER EVALUATION** (rule 30), at the L2 optimisation mesh

```
OBJECTIVE evaluation  =  3.263 x 2.2105 x 3.0  =  21.64 core-min   (3 conditions)
GRADIENT  evaluation  = 11.666 x 2.2105 x 2.0  =  51.58 core-min
per IPOPT major       = 3.48 x 21.64 + 1.04 x 51.58 = 128.94 core-min
```

### 15d. **OPTION A — the subsonic re-run.** The registered total.

| item | core-min | basis |
|---|---|---|
| `MESH` + `Y1` + `W1` | **60.0** | 3 extrusions + 6 geometry-only warp configs + one L2 baseline primal (8.2). **`ESTIMATED`** — the extrusion is serial and has no measured anchor in this family at this mesh size. |
| **`P1`** primal-convergence arm | **82.0** | 6 configs × 5,000 steps × 1 condition at L2 |
| **`GF`** grid family (rule 1) | **1,122.8** | L3 **15.4** + L2 **123.0** + L1 **984.4**; each = 5 trim primals × 3 conditions at that level's per-primal cost (`1.237 × S_steps × cells/38,304`) |
| `P2` adjoint tolerance | **103.2** | 2 gradient evaluations |
| **`S1`** smooth-mode optimisation, 15 majors | **1,934.1** | 15 × 128.94 |
| **`S2`** full optimisation, 25 majors | **3,223.6** | 25 × 128.94 ← **the largest single term** |
| **rules 8/9 checkpoints**, 8 events at `N = 3` | **1,962.9** | per event: fresh mesh + 3 primals **70.7** (`10.667 × S_cells × S_steps`) + gradient spot-check **51.6** + trim **123.0** = **245.4** |
| **`A12`** fresh mesh, matched lift, all conditions | **123.0** | 5 trim primals × 3 conditions at L2 |
| **`A13`** the optimum on L1 | **984.4** | the same at L1 |
| **`A14`** decomposition, 3 sub-designs | **369.1** | 3 × 123.0 |
| subtotal | **9,965.1** | |
| + 5 % container preamble, staging, `checkMesh`, grading | **498.3** | |
| **REGISTERED TOTAL** | **10,500** | rounded up |
| **REGISTERED CAP, 3.00×** | **31,500** | the family's registered cap multiplier (parent §8) |

**DERIVED DOLLARS.** `10,500 core-min = 175.0 core-h × $0.0513 = **$8.98**`; cap **$26.93**.
**DERIVED, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5);
`cost_basis` class **reported-by-owner** at the owner-stated c7a.4xlarge rate. *(The box is an
r7a.4xlarge; the rate on record is the c7a.4xlarge figure and is used unchanged rather than
invented, and that substitution is named here rather than buried — as the parent's §8 also named it.)*

**`FAMILY_SHIFT` CONTINGENCY (§4b).** If `coarsen2` refuses and the family shifts up one level, every
level's cell count multiplies by 8 and the registered total becomes **≈ 84,000 core-min**
(`$71.82` derived). **That contingency is registered here, before the mesh is built, so that it is a
disclosed branch and not an overrun.**

### 15e. **OPTION B — the transonic alternative.** Priced separately so the choice is made on a number.

| item | core-min | basis | tag |
|---|---|---|---|
| one condition-primal, converged | **447.7** | A6 measured **28.73** for 1000 steps at 579,072 cells **+ 419** extrapolated to cross 1e-8 on `nuTilda` (15,573 further iterations) | `MEASURED` + `EXTRAPOLATED` |
| objective evaluation (3 conditions) | **1,343.2** | 3 × 447.7 | `DERIVED` |
| gradient evaluation | **529.1** | `11.666 × (579,072/38,304 = 15.118) × 3.0` transonic conditioning | **`ASSUMED`** — **no CRM adjoint has ever been run on this box** |
| per major | **5,225** | 3.48 × 1,343.2 + 1.04 × 529.1 | `DERIVED` |
| **optimisation alone, 25 majors** | **≈ 130,600** | | `DERIVED` |
| **whole item**, scaled at Option A's proportion (`S2` = **30.7 %** of Option A's registered total) | **≈ 425,000** | | `DERIVED` |

**DERIVED DOLLARS: ≈ $363.** At 96 cores that is **≈ 74 hours of the entire box**, minimum, and
**it is priced on the PUBLISHED WALL-FUNCTION mesh** — rule 2's wall-resolved departure would
multiply the cell count again and is **NOT COSTED** here.

**THE THREE HONEST CAVEATS ON OPTION B'S NUMBER:**
1. **The CRM adjoint has never run.** `Global Adjoint States: 5,244,840`; `Main iteration` and
   `KSP Residual` appear **zero** times in all four A6 logs. **The `529.1` is an extrapolation from a
   different case and a different Mach regime, and it is the single largest uncertainty in this
   registration.** A `BLOCKED`-until-measured precondition arm would be owed before any freeze.
2. **A6 never converged**, so the `447.7` rests on a plateau extrapolation that the A6 record itself
   killed as an experiment ("no run can buy it").
3. **Option B changes the geometry**, so the after-protocol has no D6R2 baseline to compare against
   and the item stops being a re-run (§3B).

### 15f. **THE CAP REPORTS; NOTHING KILLS ON IT** (directive #17)

A crossing writes `D6R3_CAP_CROSSED` to the ledger, **the row is graded `NOT A RESULT`, and the cap
is never raised.** No wrapper carries a `timeout`; every container prints
`D6R3_DEADLINE_IN_CONTAINER_S: NONE`. **The quality-budget stop of §8d is a different thing and is
not affected by this clause.**

**CONTENTION.** `core_min = wall_s × ranks / 60` inflates with contention at identical compute work —
D6R2's dying run measured **≈ 277 core-min/major** at load 40–77 against a **31.258** anchor, **8.9×**.
Any recorded figure above prediction attributable to delivered-core starvation is **REPORTED with the
measured `delivered_cores_mean`** and named as **waste**, never absorbed into the ratio
(`COMPUTE_BUDGET_CHARTER.md` §6).

**CALIBRATION ROWS OWED** to `docs/COST_CALIBRATION.md` at **every** process completion — each arm
separately — stating actual/predicted, and attributing contention, waste and misprediction
separately (rule 12; rule 30). **`S_adj = 2.0` is the first row that must be calibrated**, because it
is the one `ASSUMED` factor in §15b.

---

## 16. THE INSTRUMENT TABLE — **EMPTY AT THIS DRAFT, AND THAT IS THE POINT**

| file | purpose | md5 | external anchor (rule 22) |
|---|---|---|---|
| `d6r3_mesh_family.sh` | build L3/L2/L1 by the published pipeline | **NOT WRITTEN** | `cgns_utils` + pyHyp (one anchor for all three levels) |
| `d6r3_yplus_gate.py` | `Y1` | **NOT WRITTEN** | the solver's own `yPlus` print |
| `d6r3_p1_convergence.py` | `P1` + planted control | **NOT WRITTEN** | the primal's `CD` trace |
| `d6r3_w1_warp.py` | `W1` | **NOT WRITTEN** | `checkMesh` on the as-run points |
| `d6r3_opt_runScript.py` | the producer (`S1`, `S2`) | **NOT WRITTEN** | — |
| `d6r3_checkpoint.py` | rules 8/9 + planted control | **NOT WRITTEN** | fresh extrusion (independent of the warp) |
| `d6r3_grade.py` | `GF`, `A12`, `A13`, `A14` | **NOT WRITTEN** | the arm's log + `forces` output |
| `d6r3_prefreeze.sh` | §22.4's three clauses | **NOT WRITTEN** | — |

**RULE 21, APPLIED TO THIS DOCUMENT ITSELF.** Every row above says `NOT WRITTEN`. **A table that
lists what exists cannot show what is missing** — that is the defect that carried the parent's
`d6r2c_grade.py` past its freeze (parent ADDENDUM 3). **This table is therefore written in the
negative, and the freeze cannot happen until every row carries a real md5 and
`d6r3_prefreeze.sh` has hashed it.**

---

## 17. WHAT THIS REGISTRATION DOES NOT CLAIM, AND WHICH RULES IT CANNOT SATISFY

- **It is a DRAFT and it registers nothing.** No gate below is in force; no compute is authorised.
- **It does not claim a Roache triple or a GCI** (§4d). Three levels exist to *select* a mesh.
- **It does not claim the optimisation will succeed**, and `GATE REACHED` at the iteration cap is the
  expected outcome, not `PASS`.
- **It does not inherit D6R2's 24.732 %.** That figure is withdrawn (`§22.2`) and appears here only
  as history.
- **It does not describe this flow as transonic** under Option A. `M∞ = 0.288`; maximum local Mach
  measured at **0.380**; no shock exists and **no shock figure can be produced**.
- **`ARM0`-class parallel-decomposition health is NOT re-registered here.** The parent measured that
  its arm-0 check certified **an untrimmed operating point the deliverable never visits** and that
  the `GATE FAIL` survives discarding every duplicated row. **A trimmed rank-agreement check is
  owed and is a separate item**, not folded into this one.

**RULES I COULD NOT SATISFY IN THIS DRAFT, NAMED:**

| rule | status | what would be needed |
|---|---|---|
| **4 (curvature constraint)** | **NOT SATISFIED.** The published setup has thickness and volume but **no curvature constraint**, and `pyGeo`'s curvature API was **not found by this lane in the installed toolchain** — no container was started. | one container invocation to enumerate `nom_add*Constraint` on the installed `pygeo`, then either register the verified call and its bound or strike the row (§6b) |
| **10 (far-field spurious-drag decomposition)** | **NOT SATISFIED.** No far-field decomposition exists in DAFoam's function set — verified by enumerating every `"type"` across the tutorial clone. Her clause says *"where available"*; **it is not available**. | an external far-field decomposition tool, out of scope |
| **11 (trust region sized to the first-cell height)** | **PARTIALLY SATISFIED.** The literal sizing is `2.4e-7` chord per step and would need ~10⁵ majors (§11). The substitute is the in-adjoint quality constraint plus an explicit move limit. | a supervisor's ruling on whether the substitute is accepted |
| **16 (adjoint-driven mesh adaptation)** | **NOT ATTEMPTED.** Her rule 16 is explicitly a roadmap item. | a separate registered item |
| **27 (status channel with a writer)** | **REGISTERED, NOT CLOSED.** The `primal_residual.json` defect is **still open and on Sanaa's desk**. D6R3 registers the pre-freeze check; it does not close the referral. | Sanaa's ruling |
| **§4b (`coarsen2` feasibility)** | **NOT MEASURED.** No container was started. | one `cgns_utils` invocation; the `FAMILY_SHIFT` contingency is registered against it (§15d) |
| **§15b `S_adj = 2.0`** | **ASSUMED, NOT MEASURED.** Its only support is a published caution. | the first `G` evaluation on L2, then a calibration row |
| **Option B's gradient cost** | **ASSUMED.** No CRM adjoint has ever run on this box. | a `BLOCKED`-until-measured precondition arm before any Option B freeze |

**SUBMISSIONS PARKED.** Nothing here is sent, filed, uploaded, registered, posted or commented. The
IDWarp rotation defect record remains **NOT FILED**.
