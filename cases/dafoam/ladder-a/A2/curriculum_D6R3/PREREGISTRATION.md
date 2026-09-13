# Curriculum D6R3 — **REVISION R4. FROZEN 2026-09-13 by the dafoam-supervisor.** Reproduction of the published `CRM_Wing` case + in-run artefact instruments

> **STATUS: FROZEN, REVISION R4. EVERY GATE BELOW IS IN FORCE. The freeze sha is the commit that
> carries this line; from it, gates, thresholds, caps and labels are closed and change only as dated
> addenda that cannot alter them (`CLAUDE.md` rule 2).**
>
> **THE SUPERVISOR'S FOUR PERSONAL CHECKS, DONE BY HAND BEFORE THIS LINE WAS WRITTEN, NOT RELAYED:**
> **(1) Measurement code read as code, not as a summary.** `d6r3_mesh_read_gate.py:132-153` compares
> `recon == generated` on the parsed values **and** `h_recon == h_gen` on their canonical bytes —
> exact equality on both limbs, no tolerance; `d6r3_opt_runScript.py:355-381` runs it per condition
> **before** `run_model()` and calls `MPI.COMM_WORLD.Abort(17)` on any `REFUSE`, a hard abort and not
> a warning. It reconstructs on **rank 0 only**, reading every `processor*` tree from disk — the
> *opposite* structure to the unguarded collective write that blocked FM12 at
> `d6r2c_freshmesh.py:268`. `D6R3_PRODUCER_DIFF.log` shows lines 1-32, 33-102 (`daOptions` +
> `meshOptions`) and 212-end byte-identical to the published file but for the two registered D1 edits,
> with all **73** removed published lines printed verbatim.
> **(2) Crash triage:** none open in this item; FM12's `BLOCKED` is triaged and carried in its own
> record, and its cause — a producer defect, not a mesh effect — is why §8d exists here.
> **(3) Big-claim verification:** the published band was not adopted from a page alone. `0.02090` is
> corroborated by A6's independently measured `0.02090143421526141`, and the page's `~579K` cells by
> this lane's own `checkMesh` count of `579,072`.
> **(4) Pre-registration before compute, checked on the disk and not on a promise:**
> `/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/` contains **`mesh/` and nothing
> else** — no `P0/`, no solver tree, no `ledger.txt`, no primal or adjoint output. **Zero solver
> core-minutes have been spent by this item.**
>
> **ONE STATED LIMIT OF RULE 17, recorded here rather than discovered later:** the gate proves the
> decomposed meshes reconstruct **exactly** to the mesh this arm staged. It does not instrument
> DAFoam's own reader. It runs in the same process tree immediately before `run_model()`, on the very
> directories the solver then opens, which is the closest this can be taken without patching the
> toolchain — and it is what FM8 lacked when 1,486 processor meshes scanned clean.** Written 2026-09-13 by a dafoam `lab-lane` for `dafoam-supervisor`, who freezes it
> personally and checks `DAFOAM_CHARTER.md` §22.4's three clauses before the sha.
> **This item has burned 0 core-min of SOLVER compute and started no solver.** The only compute
> spent is the mesh build of §5, which is registered there with its measured cost.
> **Nothing here is sent, filed, uploaded, registered, posted or commented** (rule 7).
> **No agent message is Sanaa's consent** (rule 9).

**Registered name:** *reproduction of the published `CRM_Wing` case + in-run artefact instruments.*

**Supersedes** R1 `9847ffc30`, R2 `aaab69942`, R3 (uncommitted). Struck material is preserved
unrewritten in the appendices and in those commits (rule 6).

---

## 0. THE TWO RULINGS THIS REVISION CARRIES, BYTE-EXACT, READ FROM THE DIRECTIVE BY THIS LANE

**§L, 2026-09-13 ~18:25Z** (`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md:285`):

> *"the dafoam team uses exactly that 3D wing at that mach with those files and what that turorial
> has and rruns EXACTLY that. … D6R3: for now lets do the verbatim case and reproduce what they
> have exactl then we can redo wall resolved (but every other in optimization checks remain)."*

**§M, 2026-09-13 ~18:35Z** (`…:285`, section M):

> *"no lets make itmultipoint from the start, keeping everything else verbatim/ cloned from that
> case. Multipiint doesnt change the setup it just allows us to look at the optimization under
> different constraints or conditions, and its moreinteresting."*

**WHAT THAT MAKES D6R3, IN ONE LINE:** the DAFoam `CRM_Wing` tutorial **cloned verbatim** — mesh,
extrusion, FFD, wall functions, solver, schemes, optimiser settings — with **ONE registered
physics-side deviation, the multipoint objective**, plus her rules 6–11 as **in-run instruments that
observe and stop and change nothing**, and her rule 12's fresh-mesh confirmation after.

> ### **THE CONSTRAINT THAT GOVERNS EVERY INSTRUMENT IN THIS DOCUMENT**
> **An in-run check is an OBSERVER AND A STOP. It never changes the published physics or the
> published design variables.** §6 re-examines all six against that constraint and **strikes three
> of this lane's own earlier additions** because they failed it.

**WHAT R4 STRIKES FROM R3, and each is struck because the ruling requires it, not because it was
wrong on its own terms:**

| struck | what it was | why |
|---|---|---|
| **Δ1** wall-resolved y⁺ ≈ 1 | `s0 1e-4 → 1.35e-6`, `N 53 → 105`, `useWallFunction False` | **DEFERRED, not cancelled** (§4). Her words: *"then we can redo wall resolved."* The ×2.36 price is recorded so the successor inherits a costed plan |
| **Δ3** `evalMode fast → exact` | an IDWarp setting change | **it changes the warp.** An observer may not. Guard 6 now asserts the published default `fast` is in force |
| **Δ5** `SLSQP → IPOPT` | optimiser selection | the published default stands (§3a) |
| **Δ6** `max_iter 100 → 25` | iteration budget | the published count stands |
| **Δ8** the three-level grid family | a rule-1 gate | **a reproduction reproduces the tutorial's own mesh; it does not choose a level.** The build is kept as a measurement only (§5) |
| **Δ9** `meshQualityKS` in the adjoint | two added constraints | **it changes the optimisation problem.** Rule 7's stop is delivered by guard 7, an observer (§6.7) |
| **Δ12** move limits as bounds | a changed feasible set | **it changes the optimisation problem.** The guard now observes the step and stops; it hands the optimiser nothing (§6.11) |
| **Δ15** the curvature constraint | an added constraint | **it changes the optimisation problem.** Retained as a **reported diagnostic only**; rule 4's curvature clause is `NOT SATISFIED` for this reproduction, by her ruling (§8) |

---

## 1. THE PUBLISHED SETUP, AND **THE PUBLISHED BAND**

### 1a. Provenance

| field | value |
|---|---|
| repository | `https://github.com/DAFoam/tutorials.git`, local clone `/home/ubuntu/dafoam-tutorials`, HEAD `d3b7e38b058aba2a98a74092e15c41ec455c570d` |
| the case | **`CRM_Wing/`** |
| `runScript.py` | md5 **`0de915d21166a91a9a54b37ab11214cf`** |
| `genWingMesh.py` | md5 **`af9b63c2a22886b40c2309b298288cb8`** |
| surface geometry | `CRM_surfMesh.cgns.tar.gz`, md5 **`0635beaae7d9117eb0d27bceaeb69066`** (staged from `/home/ubuntu/certonomous-runs/P3-a6-n16-ref/s2bpv/`) |
| multipoint pattern | He, Mader, Martins & Maki, **AIAA Journal 2020 §3.1 / Table 4**, md5 `bd592e7ea1a5a3c2b9361d43f840f43b`, title-page verified |

### 1b. **THE BAND — FOUND, ON THE PROJECT'S OWN DOCUMENTATION PAGE, AND QUOTED FROM THE PAGE**

**The hunt ran in the registered order and the first source failed.**

1. **The DAFoam regression archive was unpacked and searched. It carries NO CRM datum.**
   `/home/ubuntu/upstream/dafoam_reg_test_files/reg_test_files-main.tar.gz` → **944 files, 27
   case directories, none of them CRM**; `grep -rl "3.407014|CRM|2.11031707"` returns **one hit, an
   unrelated string inside `NACA0012V4/airfoil.vsp3`**. Measured by this lane, by execution.
2. **The documentation page was retrieved and it carries the number.**

| field | value |
|---|---|
| URL | `https://dafoam.github.io/tutorials-aero-crm.html` (HTTP **200**) |
| retrieved | **2026-09-13T18:22:27Z**, into the box; **nothing left the box** |
| local artefacts | `dafoam_crm_tutorial_page.html` md5 **`cf837d40aabf954e9d11f9a6ae6c8f00`**; text sidecar `dafoam_crm_tutorial_page.txt` md5 **`a536f12b9b71703c62932e0248fa672b`** |
| **title-page verification** (rule 15) | the page's own **`<title>` element** reads **`Common research model (CRM) wing \| DAFoam`**, and its `<h1>`-level heading at sidecar **line 112** reads **`Common research model (CRM) wing`**. **Verified from the document's own title, never from the filename, the file type or the hash.** |
| page's own footer | *"Site last generated: Sep 10, 2026"* (sidecar line 135) |

**The band, quoted verbatim from sidecar line 131:**

> **“The case ran for 160 optimization iterations, the original CD was 0.02090 and the optimized CD
> was 0.01932 (7.6% drag reduction).”**

And the page's own case description, sidecar lines 116–124:

| page line | statement |
|---|---|
| 116 | `Geometry: CRM wing` |
| 117 | `Objective function: Drag coefficient (CD)` |
| 118 | `Lift coefficient (CL): 0.5` |
| 119 | `Design variables: 192 FFD points moving in the z direction, seven twists, and one angle of attack.` |
| 120 | `Constraints: volume, thickness, LE/TE, and lift constraints (total number: 768)` |
| 121 | `Mach number: 0.85` |
| 122 | `Reynolds number: 5 million` |
| 123 | `Mesh cells: ~579K` |
| 124 | `Solver: DARhoSimpleCFoam` |

**TWO INDEPENDENT CORROBORATIONS FROM THIS LAB'S OWN MEASUREMENTS, neither of them recalled:**

- **`Mesh cells: ~579K`.** This lane **built the mesh** on 2026-09-13 by the published pipeline and
  `checkMesh` counted **579,072** (§5). The page and our build agree.
- **`the original CD was 0.02090`.** A6 ran the published case and measured
  **`CD = 0.02090143421526141`** (`curriculum_D8R`-family record via
  `docs/dafoam/PRIOR_WORK_INVENTORY.md` §1g). **The page's baseline and our own independently
  measured baseline agree to four significant figures.** That is the strongest single piece of
  evidence that this reproduction starts where the tutorial starts.

**A CONTRADICTION IN THE PUBLISHED MATERIAL, DISCLOSED AND NOT RESOLVED BY THIS LANE.** The page
says the case **“ran for 160 optimization iterations”** (line 131) while the producer's own
published optimiser block sets **`MAXIT: 100`** (`runScript.py:253`) and its IPOPT alternative sets
`max_iter: 100` (`:243`). **160 > 100 under either block.** No reading is asserted here; it is
recorded, and §7's `G1` grades termination against the **producer's** value because the producer is
what runs.

### 1c. **HOW THE BAND APPLIES, AND THE ONE THING IT MAY NOT BE COMPARED AGAINST**

**The tutorial is SINGLE POINT at `CL_target = 0.5` (`runScript.py:28`, page line 118). That is
exactly this item's `cl05` condition.**

- **The published band is therefore the band for `cl05`'s OWN contribution, and for nothing else.**
  `BAND-CL05`: the reproduction's `cl05` drag reduction is compared against **7.6 %**
  (`0.02090 → 0.01932`), and its **baseline** `CD₀₅` against **`0.02090`**.
- **THE WEIGHTED MULTIPOINT OBJECTIVE `J = 0.25·CD₀₄ + 0.50·CD₀₅ + 0.25·CD₀₆` IS OURS AND HAS NO
  PUBLISHED BAND.** It is reported with **`BAND: NOT AVAILABLE`** beside it.
- **A weighted number is never compared against a single-point published figure.** That is the same
  disease as comparing drag across different lifts (rule 19), and it is forbidden here by name.

---

## 2. THE VERBATIM TABLE — **59 PARAMETER ROWS, 58 "SAME", 1 DEVIATION**

Every row cites the published file and line. **`SAME` means adopted unchanged.** Under §L and §M
this table is now almost entirely `SAME`, and **that is the deliverable**: it shows that multipoint
does not change the setup, exactly as she said.

| # | parameter | published value | source:line | same? |
|---|---|---|---|---|
| 1–6 | `U0 295.0`, `p0 101325.0`, `T0 300.0`, `nuTilda0 4.5e-5`, `aoa0 2.11031707`, `A0 3.407014` | | `runScript.py:24-31` | **SAME** |
| 7 | `mu 1.8e-5`, `Pr 0.7`, `molWeight 28.97`, `Cp 1005` | | `constant/thermophysicalProperties:42,43,33,37` | **SAME** |
| 8 | Mach, derived | `295/347.189 = 0.849678` | rows 1, 3 | **SAME** |
| 9–11 | `SpalartAllmaras`, `turbulence on`, `Prt 1.0`, `nuTildaMin 1e-16`; `nuTilda` wall `fixedValue 0.0` | | `constant/turbulenceProperties:21-25`; `0.orig/nuTilda` | **SAME** |
| 12 | `primalBC.useWallFunction` | **`True`** | `runScript.py:42` | **SAME** ← Δ1 deferred, §4 |
| 13 | `nut` wall BC | **`nutUSpaldingWallFunction`** | `0.orig/nut:24` | **SAME** ← Δ1 deferred |
| 14 | mesh pipeline | `tar` → `cgns_utils coarsen` → `genWingMesh.py` → `plot3dToFoam -noBlank` → `autoPatch 45 -overwrite` → `createPatch -overwrite` → `renumberMesh -overwrite` | `preProcessing.sh:20-25` | **SAME** |
| 15–20 | `inputFile surfMesh.cgns`, `fileType CGNS`, `unattachedEdgesAreSymmetry True`, `outerFaceBC farfield`, `autoConnect True`, `families wall` | | `genWingMesh.py:8-14` | **SAME** |
| 21 | **`N`** | **`53`** (52 cell layers) | `:18` | **SAME** ← Δ1 deferred |
| 22 | **`s0`** | **`1.0e-4`** m | `:19` | **SAME** ← Δ1 deferred |
| 23 | `marchDist` | `25 × 3.758151 = 93.953775` | `:20` | **SAME** |
| 24–27 | `ps0 -1.0`, `pGridRatio 1.1`, `cMax 5.0`, `epsE 1.0`, `epsI 2.0`, `theta 3.0`, `volCoef 0.16`, `volBlend 0.0005`, `volSmoothIter 30`, `kspRelTol 1e-4`, `kspMaxIts 50`, `kspSubspaceSize 50` | | `:25-39` | **SAME** |
| 28 | **cell count** | page line 123: `~579K`; the producer publishes no exact figure | — | **SAME — and now MEASURED at `579,072` by building it** (§5) |
| 29–30 | `solverName DARhoSimpleCFoam`, `primalMinResTol 1.0e-8` | | `runScript.py:35-36` | **SAME** |
| 31 | `primalMinResTolDiff` | **absent from the CRM file** | — | **SAME** (absent; DAFoam's default stands, `P0` records it) |
| 32–38 | `ddtSchemes steadyState`; `gradSchemes Gauss linear`; `div(phi,U) Gauss linearUpwindV grad(U)`; **`div(phid,p) Gauss limitedLinear 1.0`**; all other `div Gauss upwind`; `laplacian Gauss linear corrected`; `snGrad corrected`; `interpolation linear`; `wallDist meshWave` | | `system/fvSchemes:20-62` | **SAME** |
| 39 | `nNonOrthogonalCorrectors` | **`0`** | `system/fvSolution:20` | **SAME** — R3's `P1` selection arm is struck; the published value runs |
| 40–42 | GAMG/smoothSolver blocks; relax fields `(p\|rho) 1.0`, equations `p 1.0`, others `0.80`; `potentialFlow nNonOrth 20` | | `:25-64` | **SAME** |
| 43 | `controlDict endTime` | **`2000`** | `system/controlDict:21` | **SAME** — R3's `P1`-set value is struck |
| 44–45 | `writePrecision 16`, `timePrecision 16`; `numberOfSubdomains 72` | | `:27,30`; `system/decomposeParDict:18` | **SAME** |
| 46 | `0.orig/U internalField` | `uniform (100 0 0)` while `U0 = 295.0` | `0.orig/U:20` | **SAME — recorded, not corrected.** `primalBC` overwrites the *boundary*, not the internal initial field |
| 47–51 | `designSurfaces ["wing"]`; `function.CD/.CL` force/patchToFace/parallelToFlow/normalToFlow with `scale 1/(0.5·U0²·A0·ρ0)`; `adjStateOrdering cell`; `adjEqnOption gmresRelTol 1.0e-6, pcFillLevel 1, jacMatReOrdering natural, gmresMaxIters 2000, gmresRestart 2000`; `normalizeStates` | | `runScript.py:34-78` | **SAME** — R3's `P2` tightening arm is struck |
| 52 | `checkMeshThreshold` | `maxAspectRatio 2000.0`, `maxNonOrth 75.0`, `maxSkewness 5.0` | `:79-83` | **SAME** |
| 53 | **`transonicPCOption`** | **`2`** | `:84` | **SAME.** R3 registered `1` as a deviation on this lab's L-40 measurement that `2` is dead code for this solver (`DAResidualRhoSimpleCFoam.C:172-176` accepts only `== 1`). **Under §L that change is STRUCK: the published value runs.** The measurement stands and is recorded, and `P0` reports which value was in force — **a published null is reproduced as a published null** |
| 54 | `inputInfo` | `aero_vol_coords volCoord`; `patchV patchVelocity`, `patches ["inout"]`, `flowAxis "x"`, `normalAxis "z"` | `:86-95` | **SAME** |
| 55 | `meshOptions` (IDWarp) | `{gridFile, fileType "OpenFOAM", symmetryPlanes [[[0,0,0],[0,1,0]]]}` — **every IDWarp option at its own default**: `useRotations True`, `LdefFact 1.0`, `evalMode "fast"`, `aExp 3.0`, `bExp 5.0`, `alpha 0.25`, `errTol 5e-4`, `cornerAngle 30.0`, `bucketSize 8` | `:97-102`; defaults at `idwarp/UnstructuredMesh.py:131-142` | **SAME.** Guard 6 **asserts** the defaults are in force and changes none |
| 56–59 | FFD `12 8 2` = 192 points; `nom_addRefAxis(xFraction=0.25, alignIndex="j")` → 7 twist DVs, root fixed; `nom_addLocalDV("shape", PS)` → 192 shape DVs, axis unspecified; bounds `twist [-10,10] s 0.1`, `shape [-1,1] s 10.0`, `patchV [U0,0]–[U0,10] s 0.1` | | `FFD/wingFFD.xyz:2`; `runScript.py:146-160`, `:200-202` | **SAME** |
| 60–62 | `nom_addThicknessConstraints2D("thickcon", leList, teList, nSpan=25, nChord=30)` bounds `[0.5,3.0]`; `nom_addVolumeConstraint("volcon", …)` lower `1.0`; `nom_add_LETEConstraint("lecon"/"tecon", volID=0, faceID="iLow"/"iHigh")` linear | | `:184-188`, `:206-209` | **SAME** |
| 63 | optimiser | **`SLSQP`** with `ACC 1.0e-5`, **`MAXIT 100`**, `IFILE opt_SLSQP.txt` | `:15`, `:251-255` | **SAME** — see §3a |
| 64 | trim before iteration 1 | `optFuncs.findFeasibleDesign(["scenario1.aero_post.CL"], ["patchV"], targets=[CL_target], designVarsComp=[1])` | `:268` | **SAME**, extended to three conditions by D1 |
| **65** | **objective / lift constraint** | `add_objective("scenario1.aero_post.CD", scaler=1.0)` `:205`; `add_constraint("scenario1.aero_post.CL", equals=0.5, scaler=1.0)` `:206`; `CL_target = 0.5` `:28` | | **DEVIATION D1 — the only one** |

### 3a. **THE OPTIMISER, AND A CONTRADICTION IN THE PUBLISHED FILE, DISCLOSED BY LINE**

**`runScript.py:14` comments** `# which optimizer to use. Options are: IPOPT (default), SLSQP, and SNOPT`
**while `runScript.py:15` sets** `default="SLSQP"`.

**The comment and the code disagree. The block the file ACTUALLY runs by default is SLSQP**, at
`:251-255`: `{"ACC": 1.0e-5, "MAXIT": 100, "IFILE": "opt_SLSQP.txt"}`. **SLSQP at `MAXIT 100` is
registered**, because it is what the published file runs. The IPOPT block at `:238-249`
(`tol 1.0e-5`, `constr_viol_tol 1.0e-5`, `max_iter 100`, `mu_strategy adaptive`,
`nlp_scaling_method none`, `limited_memory_max_history 10`, `alpha_for_y full`, `recalc_y yes`) is
**registered as the named alternative and is not used.**

**This is recorded as a finding about the published setup**, with both line numbers, so no successor
re-derives it and no reader assumes from the comment that the tutorial's results are IPOPT results.

---

## 3. **DEVIATION D1 — AND IT IS THE ONLY ONE ON THE PHYSICS SIDE**

### **D1 — SINGLE POINT → MULTIPOINT.** Row 65. *(Sanaa §M, 2026-09-13)*

| | published (row 65) | D6R3 |
|---|---|---|
| conditions | one, `CL_target = 0.5` | **three: `cl04`, `cl05`, `cl06`** |
| lift targets | `CL = 0.5` | **`0.400 / 0.500 / 0.600`** |
| weights | — | **`0.25 / 0.50 / 0.25`** |
| objective | `CD` | **`J = 0.25·CD₀₄ + 0.50·CD₀₅ + 0.25·CD₀₆`** |
| lift constraint | one equality | **three equalities**, one per condition, `scaler = 1.0` |
| AoA | one `patchV` DV | **one `patchV` DV per condition**, `U` pinned at `U0`, AoA `[0, 10]°`, `scaler 0.1` |

**HER REASON, IN HER OWN WORDS, AND IT IS THE REGISTRATION'S REASON TOO:** *"Multipiint doesnt
change the setup it just allows us to look at the optimization under different constraints or
conditions."* **§2 is the evidence for that claim: 58 of 59 rows read `SAME`.**

**THE MULTIPOINT WIRING IS PUBLISHED, AND IS CITED BY LINE.** He, Mader, Martins & Maki, **AIAA
Journal 2020, §3.1 and Table 4** (sidecar `he_mader_martins_maki_aiaaj2020_dafoam_j058853.txt`):
three flight conditions (`:887-889`); objective `f = Σᵢ wᵢ CD_i` with **weights 0.25, 0.50, 0.25**
(`:890-891`); **angle of attack a design variable per condition** (`:896-898`); twist with the root
fixed (`:898`); thickness, volume and LE/TE constraints (`:857-869`); IDWarp for the warping
(`:890`). **DAFoam's own authors publishing DAFoam multipoint** — a documented pattern applied to a
documented case.

**THE FALSIFIER, STATED:** *if the multipoint layer requires changing any setting the CRM case
fixes, that setting becomes its own numbered deviation.* **Checked at this revision: none was
found.** Multipoint adds **more scenarios of the same kind**, each carrying the published
`patchV` / `CL`-equality pair of rows 54, 59 and 65. Every mesh, warp, DV-parameterisation, scheme,
wall-treatment and solver row is untouched.

**WHAT D1 COSTS: 2.96×** the single-point reproduction at the same mesh — `88,300 → 261,300`
core-min (§7). **Three conditions, three primals and three pairs of adjoints per evaluation.**

---

## 4. Δ1 — **DEFERRED, NOT CANCELLED, AND COSTED FOR THE SUCCESSOR**

Her words: *"then we can redo wall resolved."* **The wall-resolved rung is a registered successor
item, not a dropped idea**, and R3's work on it is preserved so that item starts costed:

| | value |
|---|---|
| sizing anchor | baseline y⁺ **min 7.648 / max 73.826 / mean 34.587** at `s0 = 1.0e-4` on the published mesh (`grep yPlus /home/ubuntu/certonomous-runs/A6-crm-wing/run_model_run1.log`, converged tail) |
| corroboration | He et al. AIAAJ 2020 `:882` reports **average y⁺ 33.7** for the sibling published wing — **2.6 %** from our measured 34.587 |
| `s0` for max y⁺ = 1 | `1.0e-4 / 73.826 = ` **`1.3546e-6 m`** → register `1.35e-6` |
| layers | `53 → 105` nodes (52 → 104 cells); growth ratio **improves** `1.2704 → 1.1695` |
| cells | **×2.000 exactly**: 579,072 → **1,158,144** |
| **price** | **×2.36 on the item** (R3 §11, preserved in APPENDIX T) |

**Nothing in this reproduction is wall-resolved, and no y⁺ ≈ 1 claim is made anywhere in it.**

---

## 5. THE MESH — **BUILT, MEASURED, AND THE GRID FAMILY STRUCK AS A GATE**

**Δ8's three-level family is STRUCK as a gate** (a reproduction reproduces the tutorial's own mesh).
**The build had already been made when the ruling landed, so its measurements are kept as
measurements and nothing further was spent on it.** The run root is
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/mesh/`.

| level | surface (`cgns_utils coarsen` depth) | pyHyp `N` | `s0` | **cells, MEASURED** | `checkMesh` max non-orth | max aspect | max skewness |
|---|---|---|---|---|---|---|---|
| L3 | c2, **2,784** faces | 27 | `2.0e-4` | **72,384** | **57.50279457** | **249.485** | **2.225** |
| **L2 — THE PUBLISHED MESH** | **c1, 11,136** faces | **53** | **`1.0e-4`** | **579,072** | **70.44640459** | **309.124** | **3.323** |
| L1 | c0, **44,544** faces | 105 | `5.0e-5` | **STOPPED** | — | — | — |

**FOUR THINGS THIS BUILD SETTLED, EACH BY EXECUTION:**

1. **§4b of R2/R3 asked whether `cgns_utils` can coarsen this surface twice. IT CAN.** `coarsen_1`
   and `coarsen_2` both returned `rc=0`, and the measured surface quad-face counts are
   **44,544 → 11,136 → 2,784**, reproducing `D8G`'s independently measured 4.000 ratios. **The
   `L2 BRANCH` contingency registered against that precondition is not triggered.**
2. **The published mesh is `579,072` cells**, counted by `checkMesh` — matching `11,136 × 52`
   exactly, matching the A6 archive's `Mesh region0 size: 579072`, and matching the documentation
   page's `~579K`. Row 28 is no longer `NOT MEASURED`.
3. **The published mesh's as-built max non-orthogonality is `70.44640458682032`** — **above the flat
   `70.0` bound R2 and R3 had registered.** That refuted the flat bound and forced §6.7's derived
   clause. **A number that arrives before the freeze and changes a threshold is the whole reason to
   build first.**
4. **L1 was STOPPED at 18:21:02Z, 4 min 22 s in, at extrusion layer 61 of 104, because the ruling
   struck the gate it existed to feed.** `rc = 137`, by `docker stop`. **This is not a cap stop
   (directive #17 is untouched); it is a scope withdrawal**, and the compute is reported as
   **waste**, named and not absorbed (`COMPUTE_BUDGET_CHARTER.md` §6).

**MEASURED COST OF THE BUILD** — `ALL_LEVELS_WALL_S 353` at 4 ranks:

| level | wall s | core-min | note |
|---|---|---|---|
| L3 | 10 | **0.667** | |
| **L2 (the case mesh)** | **75** | **5.000** | **this is the mesh the reproduction runs on** |
| L1 (stopped) | 262 | **17.467** | **WASTE**, named |
| **total** | **353** | **23.533** | |

**R3's `MESH` cost line was `120.0 core-min ESTIMATED`. The measurement is `23.533`, a ratio of
`0.196` — the estimate was 5.1× high.** A calibration row is owed to `docs/COST_CALIBRATION.md`
(rule 12), stating that ratio and naming the 17.467 core-min of L1 separately as waste rather than
blending it into the ratio.

---

## 6. THE SIX IN-RUN INSTRUMENTS — **OBSERVERS AND STOPS, AND EACH ONE SAYS IN ONE LINE HOW IT TOUCHES NOTHING**

**Instrument:** `d6r3_inrun_guards.py`, md5 **`a553e2dd9c29394303e9e91f3e40366b`**.
**Controls:** `D6R3_INRUN_SELFTEST.json`, md5 **`fb68bc1a802afd433ea60337d01bfc79`** —
**`D6R3_INRUN SELFTEST PASS`, `n_total = 53`, `n_pass = 53`, `n_fail = 0`, exit 0.**
**Rule 20:** `D6R3_PREFREEZE_CLI.log`, md5 **`1ff07c5256862bb8ab682341397ca705`** — the
**launcher-emitted** command line returns `rc = 0`, no-args `rc = 64`, and the FM9 defect class
`--log` `rc = 2`.

Every guard returns exactly one of `OK` / `STOP` / `REFUSE`; checks non-finite **before** any
comparison (rule 26); counts its informative inputs and refuses below a floor (rule 25); prints
every count with its failing partner (rule 24); and **never degrades to `OK`**.

### 6.0 THE OBSERVER TEST, APPLIED TO ALL SIX

| rule | **how it observes or stops WITHOUT touching the published physics or DVs** | verdict |
|---|---|---|
| **6** | Reads IDWarp's **live option dictionary** and asserts the **published defaults** (`useRotations True`, `LdefFact 1.0`, `evalMode "fast"`) are still in force. It **sets nothing**. R3's `evalMode → "exact"` is **STRUCK** because it would have changed the warp. | **OBSERVER** |
| **7** | Reads `checkMesh` quantities off the **as-run** points after the final DV application and **stops the run**. It adds no constraint and hands the optimiser nothing. **Δ9's `meshQualityKS`/`addToAdjoint` is STRUCK** — it would have added two constraints the published case does not carry, changing the optimisation problem. | **OBSERVER + STOP** |
| **8** | Regenerates the mesh from the current design surface every `N = 3` majors and resumes from the same design. **No published value changes**: same `genWingMesh.py` arguments, same pipeline, same DVs; only the accumulated warp error is reset. | **PROCEDURE, changes no value** |
| **9** | Evaluates the current design on a **freshly extruded** mesh at matched lift and **stops** if it disagrees with the deformed-mesh objective. Reads only; the optimiser never sees it. | **OBSERVER + STOP** |
| **10** | Adds OpenFOAM's `forces` function object, which **computes and writes** `force.dat` and **does not enter the equations** — it is post-processing inside the time loop. Reads the split and **stops** on the artefact signature. | **OBSERVER + STOP** |
| **11** | **Observes** the per-major design step and **stops** if it exceeds the registered limit. **Δ12's move limits as OPTIMISER BOUNDS are STRUCK** — a bound changes the feasible set. The guard hands the optimiser nothing; it watches and halts. | **OBSERVER + STOP** |

**THREE OF THIS LANE'S OWN ADDITIONS WERE STRUCK BY THIS TEST — Δ3, Δ9 and Δ12 — plus Δ15's
curvature constraint (§8). That is the test doing its job, and recording it is the point.**

### 6.6 RULE 6 — the warp settings, verified in IDWarp's own source

Her rule says *verify*, and these names were read from the toolchain, never from recollection —
IDWarp **2.6.2** at `/home/ubuntu/certonomous-runs/W5-idwarp-source/idwarp_src`:

| option | published value | **name defined** | **value used** |
|---|---|---|---|
| **`useRotations`** | `True` (default) | `idwarp/UnstructuredMesh.py:138` | `:1058` → `warp.gridinput.userotations`; consumed `src/modules/kd_tree.F90:1110`, `:1339`, guarding `GETROTATIONMATRIX3D`, which builds the per-node rotation from the surface normal's change — **her "rotation of the near-wall region with the surface"** |
| **`LdefFact`** | `1.0` (default) | `:133` | `:1053`; `src/warp/warpMesh.F90:39` sets `tp%Ldef = tp%Ldef0 * LdefFact`; `Ldef0` at `kd_tree.F90:1500-1512` is **the max distance from the surface-node centroid to any surface node** — **her "deformation region scaled to the geometry"** |
| `evalMode` | `"fast"` (default) | `:136` | `:1063-1065` |

**CONTROLS — 5, all PASS:** clean → `OK`; **`useRotations` silently `False` → `STOP`**;
**`LdefFact` moved to 0.5 → `STOP`**; **`evalMode` silently changed away from the published `fast`
→ `STOP`** (a verbatim reproduction must stop on a changed warp **in either direction**); option
absent from the live dict → `REFUSE`.

### 6.7 RULE 7 — the quality budget, on the **AS-RUN** points, **our instrument and not the solver's**

**MEASURED, and re-measured by this lane rather than adopted: the solver's own non-orthogonality
clause NEVER REFUSES on this family.** Over
`.../O_mp_20260913T013230Z_226722.log` and `.../FM10_20260913T163543Z_1546115.log`:

| log | mesh-check blocks | over 70.0 | worst | `severely non-orthogonal` lines | `Non-orthogonality check OK.` | `Mesh OK.` | `Failed 1 mesh checks.` |
|---|---|---|---|---|---|---|---|
| `O_mp` | **202** | **76** | **`80.90429398`** | **76** | **202** | 198 | **4** (all aspect-ratio) |
| `FM10` | **6** | **6 of 6** | **`79.21261137`** | **6** | **6** | **6** | **0** |

OpenFOAM's own `*Number of severely non-orthogonal (> 70 degrees) faces: N` prints **immediately
above the `OK` it does not prevent**. The refusal channel is **live** — the four `Failed 1 mesh
checks.` are all aspect-ratio. **So the budget is ours: guard 7 requires
`source == "as_run_mesh_measurement"` and REFUSES a verdict string.**

**THRESHOLDS — and the binding one is DERIVED, not pinned (rule 23):**

| quantity | bound | basis |
|---|---|---|
| non-orthogonality | **`≤ 75.0` absolute** AND **`≤ baseline + 1.0°` derived** | absolute: **the published CRM value**, `runScript.py:82`. Derived: because the **as-built published baseline measures `70.44640458682032`** (§5) and a flat 70.0 would have been **infeasible at iteration zero**. `1.0°` is **one fifth of the smallest real degradation ever measured on this family** (MACH-wing baseline `66.32299475` → as-run `71.238` / `79.213` / `80.904`, i.e. `+4.915` / `+12.890` / `+14.581`) |
| skewness | `≤ 4.0` | the published constraint bound, `UBend_Channel/runScript_meshQualityConstraint_v2.py:212`. Feasible: the as-built baseline measures **`3.323`** |
| aspect ratio | `≤ 2000.0` | the published CRM value, `runScript.py:81`. As-built baseline **`309.124`** |
| first-cell height / baseline | `≥ 0.80` | D6R2 measured first-cell height within **1.6 %** fresh-vs-deformed; a 12× allowance |
| min volume | `> 0` and `≥ 0.10 ×` baseline | D6R2 measured **zero** negative or degenerate volumes |
| y⁺ | `max ≤ 110.0` | **1.5 × the measured baseline max of 73.826**. *(The wall-resolved `median ≤ 1.5 / max ≤ 3.0` clause belongs to the deferred Δ1 item and is not in force here.)* |

**THE 70.0-NOT-75.0 CHOICE IS A NUMBERED DEVIATION OF OUR INSTRUMENT — `I1`** — legitimate because
the instrument is ours, and recorded because **a guard set to a bound the published file does not
abort on must read as our choice.** Three published values exist for this quantity: `70.0`
(`UBend…:213`, a constraint bound), **`75.0`** (`CRM_Wing/runScript.py:82`, the solver's abort —
**our absolute clause**), and `80.0` (`UAV_Propeller/runScriptMultipoint.py:419`, a constraint bound
on a wing-class case). **The derived clause is what catches the known-bad meshes; the absolute
clause is published.**

**CONTROLS — 21, all PASS. Twelve on REAL measured values** — seven on D6R2's as-run meshes and
five on the CRM meshes this lane built:

| control | want | got |
|---|---|---|
| clean | `OK` | **`OK`** |
| **REAL: `O_mp`'s worst as-run mesh `80.90429398`, which OpenFOAM called `OK` twice** | `STOP` | **`STOP`** |
| **REAL: `FM10`'s worst `79.21261137`, 6 of 6 over, zero `Failed 1 mesh checks.`** | `STOP` | **`STOP`** |
| **REAL: `71.23798136`, in BOTH logs, passed by the solver** | `STOP` | **`STOP`** |
| **REAL: `70.01418200`, the smallest of `O_mp`'s 76 over-70 values** | `STOP` | **`STOP`** |
| REAL/boundary: `66.96543422`, 0.64° above its own baseline | `OK` | **`OK`** |
| **MEASURED: the published CRM mesh as freshly built, `70.44640458682032`, against ITS OWN baseline — must not fire, or the optimiser starts outside its own constraint** | `OK` | **`OK`** |
| **MEASURED: the SAME number against the MACH-wing baseline `66.32299475` DOES fire — the bound is derived from the baseline handed in, not pinned** | `STOP` | **`STOP`** |
| MEASURED/CRM: `76.0` breaches the published absolute `75.0` | `STOP` | **`STOP`** |
| MEASURED/CRM: `71.6`, inside `75.0` but 1.15° above its own baseline, fires on the derived clause alone | `STOP` | **`STOP`** |
| BLIND: the baseline carries no `maxNonOrtho` | `REFUSE` | **`REFUSE`** |
| **DELEGATION: handed the solver's verdict line instead of a measurement** | `REFUSE` | **`REFUSE`** |
| REAL: D6R2's worst aspect trip `1050.3162` against the published `2000.0` — does **not** fire | `OK` | **`OK`** ← registered gap, §8 |
| aspect 2100; skewness 4.5; first cell 0.5×; negative volume; y⁺ median 2.0 | `STOP`×5 | **`STOP`×5** |
| **RULE 31: `checkMesh` written BEFORE the DV apply — the FM10 defect exactly** | `REFUSE` | **`REFUSE`** |
| NON-FINITE `maxNonOrtho` NaN; `maxNonOrtho` never measured | `REFUSE`×2 | **`REFUSE`×2** |

### 6.8 RULE 8 — re-mesh every **`N = 3`** majors, derived from a measurement

The `O_mp` log's four aspect-ratio trips sit at lines 22928, 31050, 33015, 46373; counting
`Starting time loop` occurrences before each gives **83, 113, 120, 170** condition-primals out of
198 in a 25-major run of 113 evaluations — **the first mesh-quality breach appeared at roughly
IPOPT major 6 of 25, and `N = 3` is half of that.**

**HER ALTERNATIVE TRIGGER IS UNUSABLE ON THIS CASE AND THE REGISTRATION SAYS SO.** At the published
`s0 = 1.0e-4 m` against a 1.689 m root chord, D6R2's measured camber travel of `0.04614` chord over
25 majors is `3.1e-3 m` per major = **≈ 31 first-cell heights per major**; under the deferred Δ1 at
`1.35e-6 m` it would be **≈ 2,300**. A displacement trigger in units of the first-cell height fires
on the first step either way. **The fixed `N` and the §6.7 budget are the triggers.**

**CONTROLS — 5, all PASS:** clean `OK`; **major 7 on a mesh stamped at major 0 — D6R2's whole run —
`STOP`**; both `N` boundaries correct; a stamp from the future `REFUSE`.

### 6.9 RULE 9 — the fresh-mesh checkpoint. **HER OWN LINE: the rule that would have caught D6R2 on day one**

External anchor: a mesh **freshly extruded by pyHyp from the current design surface**, independent
of the warp. **Tolerance `|J_fresh − J_deformed| / J_fresh ≤ 0.010`, both sides at matched lift,
both trims converged to `|CL_i − target_i| ≤ 1.0e-4`.** **The lift check runs BEFORE the drag
comparison**, so an off-target evaluation produces a **`REFUSE`**, never a ratio across different
lifts (rule 19).

**CONTROLS — 9, all PASS, three of them D6R2's own measured numbers:** clean `OK`;
**D6R2's own deformed-0.753-vs-fresh-1.206 pair `STOP`**; **the 139-drag-count gap `STOP`**; both
band boundaries correct; **FM10's `+0.1493 / +0.1516 / +0.1524` lift excess `REFUSE`**; NaN
`REFUSE`; the `1.234e-03` plant `STOP`; no `CL` record `REFUSE`.

### 6.10 RULE 10 — the shear/pressure split every iteration

`forces` (`libforces.so`), published in this form at
`Airfoil_DynamicStall/…/system/controlDict:59-80`, writing **total / pressure / viscous**.
**Signature, registered as arithmetic before the data exists:** if `ΔCD_total < 0` while
`|ΔCD_pressure| < 0.20 · |ΔCD_total|` **and** the span load changes by less than 1 % at every
station, **the run STOPS and re-meshes.** The 20 % floor is the inverse of a measurement: D6R2's gap
was carried **104.5 % / 102.9 % / 99.6 % by PRESSURE** with viscous flat to within **7 counts**.

**NOT SATISFIED, and named:** her *"where available, a far-field decomposition with the spurious-drag
component"*. **It is not available** — enumerating every `"type"` across the tutorial clone yields
`force`, `moment`, `variance`, `meshQualityKS`, `totalPressure`, `field`, `power`, `wallHeatFlux`,
`patchMean`, `massFlowRate`, `regressionPar`, `vonMisesStressKS`, `uniformPressureGradient`,
`totalTemperatureRatio`, `totalPressureRatio`, `variableVolSum`, `fieldUnsteady`, `patchField` —
**none a far-field or spurious-drag decomposition.**

**CONTROLS — 8, all PASS:** clean `OK`; **100 % of the gain in friction with the span load flat
`STOP`**; both share boundaries correct; a friction-only *rise* `OK`; missing viscous column
`REFUSE`; pressure+viscous ≠ total `REFUSE`; 3 span stations `REFUSE`.

### 6.11 RULE 11 — **OBSERVED AND STOPPED, NEVER HANDED TO THE OPTIMISER**

**THE ARITHMETIC, IN FULL.** At the **published** `s0 = 1.0e-4 m` on a 1.689 m root chord, one
first-cell height is `5.92e-5` chord; D6R2's measured travel of `0.04614` chord would need **780
majors**. Under the deferred Δ1 at `1.35e-6 m` it is `7.99e-7` chord and **`5.77e+04` majors** —
at 2,245.8 core-min per major, **`1.30e+08` core-min**. **A trust region sized literally to the
first-cell height is not a trust region; it is a halt.**

**REGISTERED:** guard 11 **observes** the per-major step (`0.10` on the scaled `shape` ∞-norm,
`0.5°` on `twist`) and **stops the run** if it is exceeded. **It hands the optimiser no bound**, so
the feasible set of the published problem is untouched. **Δ12's bound form is STRUCK.**

**RULE 11 IS LABELLED `PARTIALLY SATISFIED — LITERAL SIZING INFEASIBLE, SUBSTITUTE REGISTERED`, AND
THE LABEL TRAVELS WITH EVERY VERDICT THIS ITEM PRODUCES.**

> **A QUESTION FOR SANAA'S DESK, PUT AS A QUESTION AND NOT ANSWERED HERE:** **does rule 11 mean the
> literal first-cell-height sizing, or the intent — that no single step deform the near-wall mesh
> beyond what the warp preserves?** **No agent has reinterpreted her rule**, and the item proceeds
> on the substitute with the label visible.

**CONTROLS — 5, all PASS:** clean `OK`; a 3.5× step `STOP`; a 0.8° twist step `STOP`; **at x0, where
D6R2C measured 103 of 109 components exactly zero, `REFUSE` rather than pass**; a NaN `REFUSE`.

---

## 7. ARMS, GATES AND COST

### 7a. Arms, in order

| # | arm | what it is | ranks | precondition |
|---|---|---|---|---|
| 0 | **`P0`** | **one primal + one gradient on the PUBLISHED mesh — BLOCKING** | 72 | mesh built (**DONE**, §5) |
| 1 | `O_mp` | the optimisation, published producer + D1, SLSQP `MAXIT 100`, six guards live, `N = 3` checkpoints | 72 | `P0` `PASS` |
| 2 | **`A12`** | **fresh mesh, matched lift, all three conditions, from scratch — THE CLAIMED NUMBER** (her rule 12) | 72 | `O_mp` |

**`P0`'s SCOPE: it closes the 41,760 → 579,072 CELL SCALE GAP.** §1a's cost anchors are measured at
**41,760** cells; this item runs at **579,072**, a factor **13.867** across which the adjoint's cost
is **not** linear and **not** measured. The adjoint has **never** been attempted at that size —
`Main iteration` and `KSP Residual` appear **zero** times in all four A6 logs, against
`Global Adjoint States: 5,244,840`, and A6 predicted **95–116 GiB** against a then-30 GiB box. The
box now measures **96 cores / 739 GiB total / 640 GiB available**.

**`P0` also RECORDS** what this registration cannot state: peak RSS; the effective
`primalMinResTolDiff` (row 31, absent from the published file); the effective `nom_addLocalDV`
displacement axis (row 58, unspecified — **a shape DV displacing spanwise instead of vertically
would be a silent defect**); which `transonicPCOption` was in force (row 53); and the baseline y⁺.

**`P0` GATES.** `P0-G1` the gradient COMPLETED (`rc = 0`; `Main iteration` > 0; `KSP Residual` > 0;
every total derivative finite) — *a run that never attempted a linear solve is `NOT A RESULT`, not a
fast adjoint*. `P0-G2` `‖dCD/dtwist‖∞ > 0`. `P0-G3` peak RSS recorded and below `MemAvailable`; an
OOM (`rc = 137`) is `NOT A RESULT` about cost. `P0-G4` the rule-17 mesh-read hash and rule-18
DV-apply hash both written and both asserting.

### 7b. The gates

- **`G1` — the optimiser terminated at its published budget.** `rc = 0`; `opt_SLSQP.txt` present and
  newer than the age datum. **`MAXIT = 100` is a BUDGET, not a tolerance**, and a run that reaches
  it is **`GATE REACHED`**, never `PASS` (`DAFOAM_CHARTER.md` §9).
- **`BAND-CL05` — THE REPRODUCTION GATE, and it is the published number.** `cl05`'s own drag
  reduction against the page's **7.6 %** (`0.02090 → 0.01932`), and `cl05`'s **baseline** `CD`
  against **`0.02090`**. **Tolerance registered before the run: baseline within `± 2 %` of
  `0.02090`; reduction within `± 2` percentage points of `7.6 %`.** Basis for `± 2 %` on the
  baseline: A6's independent measurement of this case read `0.02090143421526141`, which agrees with
  the page to **four significant figures**, so a 2 % band is ~200× looser than the reproducibility
  already demonstrated and is a *reproduction* criterion, not a noise one.
- **`G-J` — the weighted objective is REPORTED with `BAND: NOT AVAILABLE`.** §1c. **A weighted
  number is never compared against the single-point published figure.**
- **`G3` — the lift equalities.** `max_i |CL_i − target_i| ≤ 1.0e-3` at the final design, and
  **`≤ 1.0e-4` for any value entering a ratio** (rule 19, enforced inside guard 9).
- **`A12` — THE CLAIMED NUMBER** (`DAFOAM_CHARTER.md` §22.2): fresh mesh, matched lift, all
  conditions, from scratch. The deformed-mesh number is reported **beside** it with the difference
  disclosed, and is never the headline.

### 7c. Cost — re-anchored on the MEASURED adjoint (rule 30, per evaluation)

> **THE PREVIOUS FIGURE IS WITHDRAWN.** R1 priced the gradient evaluation at **529.1 core-min**,
> extrapolated from the A2 wing at **M 0.288** because R1 believed no CRM adjoint had ever run.
> **A CRM adjoint HAD run — at M 0.8497, on the byte-identical published producer** — and its cost
> was on disk. **The 529.1 is withdrawn and no successor may quote it.**

| anchor | value | instrument and path (§22.6) |
|---|---|---|
| **one flow adjoint** | **182.1 s wall = 12.140 core-min** | `re.finditer(r'Solving Linear Equation\.\.\.\s+([\d.]+) s')` over `/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/O-P_20260827T223101Z_1595223.log` → 20 stamps; the 10 **within-pair** deltas (adjoint→adjoint) median **182.1 s** |
| **one primal** | **69.44 s wall = 4.629 core-min** | `(4753 − 20 × 182.1) / 16` from the same log; wall 4,753 s and 316.867 core-min from `cases/dafoam/ladder-a/A6/curriculum_D8R/RESULTS.md:179-233` |
| cells at that measurement | **41,760** | `curriculum_D8R/PREREGISTRATION.md:19` |
| evaluations per major | **3.48 `F`**, **1.04 `G`** | `O_mp/d6r2c_evals.jsonl`: 87 `F`, 26 `G`, 25 majors |
| **mesh build** | **23.533 core-min** | §5, `build_all.log`, `ALL_LEVELS_WALL_S 353` at 4 ranks |

**Scaling: cell factor `579,072 / 41,760 = 13.8667` (exact arithmetic).
`k_adjoint = 1.5`, `ASSUMED` — the single assumed number in this model, and the one `P0` replaces.**

**PER EVALUATION, MULTIPOINT (rule 30):**

```
per condition-primal =  4.629 x 13.8667              =    64.19 core-min
per flow adjoint     = 12.140 x 13.8667 x 1.5        =   252.51 core-min
OBJECTIVE evaluation = 3 primals                     =   192.6  core-min
GRADIENT  evaluation = 6 adjoints (CD + CL x 3 cond) =  1515.1  core-min
per major            = 3.48 x 192.6 + 1.04 x 1515.1  =  2245.8  core-min
```

| item | **multipoint (D1)** | single point, as published |
|---|---|---|
| `MESH` (spent, measured) | **23.5** | 23.5 |
| **`P0`** | **569.2** | 569.2 |
| `O_mp`, 100 majors | **224,580.6** | 74,860.2 |
| rules 8/9 checkpoints × 8 | **21,403.8** | 7,161.3 |
| `A12` fresh mesh, matched lift | **1,155.4** | 385.1 |
| + 5 % preamble, staging, `checkMesh`, grading | **12,441** | 4,204 |
| **REGISTERED TOTAL** | **261,300 core-min** | 88,300 core-min |
| **CAP, 3.00×** | **783,900** | 264,900 |
| **dollars, DERIVED NOT MEASURED** | **$223.41** | $75.49 |

> ### **MULTIPOINT COSTS `2.96×` THE SINGLE-POINT REPRODUCTION AT THE SAME MESH — `88,300 → 261,300` core-min, `$75.49 → $223.41`.**
> Three conditions, three primals and three pairs of adjoints per evaluation. **The `2.96` is
> arithmetic, not an estimate.**

**A COMPARISON THAT WOULD BE WRONG, NAMED SO IT IS NOT MADE.** R2's verbatim figure of **24,900
core-min** was for an optimisation on **L3 (72,384 cells)**, chosen by the now-struck grid-family
gate. **It is not comparable to these numbers**, which run on the published **579,072**-cell mesh.
The honest comparison is single-point versus multipoint **at the same mesh**, which is the table
above.

**Dollars are DERIVED** at the owner-stated c7a.4xlarge rate of `$0.0513/core-h`,
**reported-by-owner, never measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5) — and the box is not a c7a.4xlarge; the substitution is named here
rather than buried.

**THE CAP REPORTS; NOTHING KILLS ON IT** (directive #17). A crossing writes `D6R3_CAP_CROSSED`, the
row is graded **`NOT A RESULT`**, and **the cap is never raised**. No wrapper carries a `timeout`.
**The §6.7 quality stop, the §6.9 fresh-mesh stop and the §6.10 drag-split stop are different things
and are NOT affected by this clause — they are physics guards and they stop the run, exactly as her
rules 7, 9 and 10 require.**

**Calibration rows owed** at every arm completion (rule 12, rule 30). **Two are owed already:** the
`MESH` line (predicted `120.0 ESTIMATED`, actual **`23.533`**, ratio **`0.196`**, with **17.467
core-min of L1 named separately as waste**), and `P0`'s, which **re-anchors `k_adjoint`**.

---

## 8. THE INSTRUMENT TABLE — **EVERY ROW POPULATED. `NOT WRITTEN` IS ZERO.**

| file | purpose | md5 |
|---|---|---|
| **`d6r3_opt_runScript.py`** | the producer: the published `runScript.py` + **D1 only**, and the **rule-17 gate before `run_model()`** | **`efc3e62699690edd32e4ee910aad09c8`** |
| **`d6r3_p0_arm.sh`** | **`P0`**, the blocking precondition | **`4bab810a2e363f0c1e9f6dd4c423b967`** |
| **`d6r3_run_arm.sh`** | the launcher; pins the producer by md5 (`G-FREEZE`) | **`29599c6225fcf9c7e65fdad908eddb5b`** |
| **`d6r3_grade.py`** | `G1`, `BAND-CL05`, `G-J`, `G3`, and the label rule | **`51bdf8ea7354de8d3346ed8956332453`** |
| **`d6r3_prefreeze.sh`** | §22.4's three clauses, driven, with **asserting** rc checks | **`e398541cdd4d5b657ba90ea16cc968bb`** |
| **`d6r3_inrun_guards.py`** | the six in-run instruments, rules 6–11 | **`22757db8d9ec646172e416578c426ee6`** |
| **`d6r3_mesh_read_gate.py`** | **RULE 17 — the mesh the solver READ** | **`8398dcbfc5bd92600f3503fdcc566ed9`** |
| **`D6R3_R17_SELFTEST.json`** | 10 driven controls, 10 `PASS` | **`0e84988da1dbb2abdd64f3379ce4f19c`** |
| **`D6R3_INRUN_SELFTEST.json`** | 53 driven controls, 53 `PASS` | **`9072291a0727d187f2aeab0980618423`** |
| **`D6R3_GRADE_SELFTEST.json`** | 26 driven controls, 26 `PASS` | **`4c5d2c75403d85b99514f808295aaf10`** |
| **`D6R3_PRODUCER_DIFF.log`** | proof the producer carries the published bytes | **`fb21850304f929e35aa3d5df42eabe5c`** |
| **`D6R3_PREFREEZE_CLI.log`** | rule 20 evidence, the launcher-emitted argv | **`816f837c5c2b0970cb429309121c2ac4`** |
| **`D6R3_PREFREEZE_RESULT.log`** | §22.4's three clauses, **ALL THREE GREEN** | **`805c0b788751136f076a0187e28ab22f`** |
| **`dafoam_crm_tutorial_page.html`** | the published band's source, retrieved | **`cf837d40aabf954e9d11f9a6ae6c8f00`** |
| **`dafoam_crm_tutorial_page.txt`** | its sidecar, cited by line in §1b | **`a536f12b9b71703c62932e0248fa672b`** |

### 8a. **THE PRODUCER IS THE PUBLISHED FILE PLUS D1, AND THAT IS PROVED, NOT ASSERTED**

`D6R3_PRODUCER_DIFF.log` compares `d6r3_opt_runScript.py` against
`CRM_Wing/runScript.py` (md5 `0de915d21166a91a9a54b37ab11214cf`, 287 lines) and reports:

| published region | status |
|---|---|
| **lines 1–32** — imports, argparse, Input Parameters | **BYTE-IDENTICAL, carried over** |
| **lines 33–102** — `daOptions` + `meshOptions` | **BYTE-IDENTICAL, carried over** |
| **lines 212–end** — OpenMDAO setup, driver, tasks | **BYTE-IDENTICAL except the TWO registered D1 edits** |

**73 published lines were removed and every one of them is printed verbatim in that log** so a
reader can see exactly what was replaced — all of them single-point wiring (`scenario1`, one
`geometry`, one `patchV`, the single objective and the single CL equality). The geometric
constraints reappear with **identical numbers** (`nSpan=25`, `nChord=30`, `[0.5, 3.0]`, `1.0`,
`lecon`/`tecon`, and the published `LE_pt`/`break_pt`/`tip_pt` planform) on `geometry_cl05`.

The producer also carries **`D1_ASSERT`**, which re-checks those three regions **at import** against
the published file staged read-only at `/pub`, and writes the result into `d6r3_run_record.json`.
**The registration's claim is therefore asserted by the run itself, not only by this document.**

The producer's own banner lists, in the file, **what was NOT added** — `evalMode "exact"`,
`meshQualityKS` with `addToAdjoint`, move limits as bounds, a curvature constraint,
`transonicPCOption 1`, IPOPT — each struck by §6.0's observer test or by §L. **A record of what we
did not add is worth as much here as the table of what we kept.**

### 8d. **RULE 17 — THE MESH THE SOLVER READ. IMPLEMENTED, NOT MERELY REGISTERED.**

**`d6r3_mesh_read_gate.py`, md5 `8398dcbfc5bd92600f3503fdcc566ed9`, called by the producer BEFORE
`run_model()` / `run_driver()`, per condition, and aborting the run (`MPI Abort 17`) on any
refusal.** R4 as first drafted carried rule 17 as *registered but not implemented*; **that was
surfaced rather than left to a complete-looking table, and it is closed here.** After a freeze sha
it could only have become an addendum, and **an addendum cannot add a gate.**

**What it does.** For each condition it rebuilds the global point set from every rank's own
`constant/polyMesh/points` and `constant/polyMesh/pointProcAddressing`, and compares the
reconstruction for **EXACT EQUALITY** — on the parsed values *and* on their canonical bytes —
against the mesh this arm generated. It refuses on: no `processor*` directories; a rank without
`pointProcAddressing`; a point count mismatch; a global index claimed twice with different values;
an incomplete reconstruction; and an unreadable case directory.

***Measured why:*** FM8 was graded a fresh-mesh confirmation and the retraction found **1,486
processor meshes scanned, zero matching the freshly extruded mesh — no arm had ever loaded it.**
**Staging the mesh is the arm; hashing what the ranks read is the gate.**

**EXACT EQUALITY, NO TOLERANCE — AND THE PROHIBITION IS ITSELF UNDER CONTROL.** A tolerance here
would silently re-admit the very defect the gate exists for: a mesh that is *nearly* the one we
generated is a mesh we did not generate. `R17.CONTROL_SOURCE_HAS_NO_TOLERANCE` scans `gate()`'s own
**executable source text** — comments and docstrings stripped with `tokenize` — for
`tol / atol / rtol / isclose / allclose / abs / round / delta / eps`, so a future edit that adds one
**fails there**.

**CONTROLS — 10, all PASS, and two of them are about the control itself:**

| control | want | got |
|---|---|---|
| clean: two ranks whose union reconstructs the generated mesh exactly | `OK` | **`OK`** |
| **KNOWN-BAD: one rank holds the BASE mesh, not the staged one — the FM8 class** | `REFUSE` | **`REFUSE`** |
| **KNOWN-BAD: a SINGLE point differing in its last digits — exact equality must refuse where a tolerance would not** | `REFUSE` | **`REFUSE`** |
| BLIND: no `processor*` directories | `REFUSE` | **`REFUSE`** |
| BLIND: a rank with no `pointProcAddressing` | `REFUSE` | **`REFUSE`** |
| BLIND: addressing that does not cover every global point — a partial reconstruction is not evidence | `REFUSE` | **`REFUSE`** |
| KNOWN-BAD: the generated mesh has a different point count | `REFUSE` | **`REFUSE`** |
| **`CONTROL_SOURCE_HAS_NO_TOLERANCE`: `gate()`'s executable source carries no tolerance construct** | `[]` | **`[]`** |
| **`CONTROL_IS_LIVE` (rule 3): the SAME scan over a MUTATED `gate()` that compares with `math.isclose(rel_tol=…)` must FIND it — or its zero on the real source is not evidence** | `True` | **`True`** |
| `CONTROL_SOURCE_IS_EXACT`: `gate()` compares with `==` on both the values and the canonical bytes | `True` | **`True`** |

**TWO THINGS THIS GATE'S OWN CONTROLS CAUGHT, RECORDED RATHER THAN SILENTLY FIXED:**

1. **The source-text control FIRED ON ITS FIRST RUN** — on the word *"tolerance"* in `gate()`'s own
   **docstring**. **The control was made precise (it now scans executable tokens only); the gate was
   not made loose.** And because a control that was just narrowed needs to be shown still able to
   see, a **planted live control** was added: the same scan over a mutated `gate()` must find the
   planted `math.isclose`.
2. **`--case /nonexistent` returned `rc = 1`, not the registered `2`** — an unhandled
   `FileNotFoundError`. **An unhandled traceback is not a refusal**: it exits on a code this
   registration never registered and a reader cannot tell it from a crash. The gate now refuses;
   **and the pre-freeze check's rc lines, which had *printed* `expect 2` beside an actual `1`
   without failing, now ASSERT.** A line that prints an expectation and does not enforce it is a
   formality.

### 8b. **§22.4's THREE CLAUSES — DRIVEN, AND ALL THREE GREEN**

`./d6r3_prefreeze.sh` → **`D6R3_PREFREEZE ALL THREE CLAUSES GREEN`**, rc 0.

- **Clause 1 — every instrument exists at its stated md5.** 12 of 12 rows `EXISTS`, each with the
  md5 the check computed. **The script refuses on absence**; it does not report a missing file as a
  pass.
- **Clause 2 — the CLI the launcher emits, driven, and the REAL anchors reported SEPARATELY from
  the synthetic case.**
  *Synthetic:* the two selftests, rc 0 and rc 0.
  *Real anchors, 10 of 10 `FOUND` in the artefacts:* `80.90429398`, `79.21261137`, `71.23798136`,
  `70.01418200`, **`70.44640458682032`** (the published mesh as freshly built by this lane),
  `66.32299475`, `0.753`, `1.206`, `0.1493`, `103 of 109`. Grader anchors, 5 of 5: `0.02090`,
  `0.01932`, `0.02090143421526141`, `5.539e-4`, `2.787e-3`.
  *The launcher-emitted argv, driven to its failing side:* `--selftest --json <path>` rc **0**;
  no-args rc **64** (refuses rather than succeeding silently); **`--log x` rc 2 — the FM9 defect
  class**; grader rc 0 and rc 2.
  **THE CHECK REFUSED ON ITS FIRST RUN** — `0.1493` was claimed as an exercised anchor but was not
  visible in the artefact, because the control's name carried `+0.149` and the value itself was
  computed rather than recorded. **The evidence was fixed, not the check**, and the first refusal is
  recorded here rather than overwritten.
- **Clause 3 — every channel a gate reads has a writer that ran.** Six channels enumerated with
  their writers: `opt_SLSQP.txt` (pyOptSparse, `runScript.py:255` — **the grader REFUSES when it is
  unreadable**), `d6r3_run_record.json`, `force.dat` (the `forces` FO staged by the launcher —
  **guard 10 REFUSES when the viscous column is absent**), the `checkMesh` log (**guard 7 REFUSES a
  delegated verdict**), `ledger.txt`, and the arm log. **No channel of this item is a
  `primal_residual.json`-class default-true channel — and the general referral stays open and is
  Sanaa's.**

### 8c. THE EXACT LAUNCH LINE

```
cd /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R3
./d6r3_p0_arm.sh 72 0-71 256
```

`P0` runs first and alone. The launcher refuses to **start** on a loaded box (`G-CORES`: it requires
`RANKS` measurably free cores) — **it refuses to start and never stops anything running**
(directive #17). It refuses as root, on any image but the pinned digest, on any producer but the
pinned md5, and on an arm directory that already exists. On success the ledger's first lines read
`D6R3_G-IMG OK …`, `D6R3_G-FREEZE producer md5 d39ca376d44efe652548f7de39468996`, `D6R3_G-CORES …`,
`D6R3_ARM P0 task=compute_totals …`, and `D6R3_DEADLINE_IN_CONTAINER_S: NONE`.

## 9. WHAT THIS REGISTRATION DOES NOT CLAIM, AND WHAT IT STILL CANNOT SATISFY

- **It is a DRAFT. No gate is in force. It authorises no solver.** **Every instrument now exists
  at a stated md5 and §22.4's three clauses are green, so the remaining distance to a freeze is the
  `dafoam-supervisor`'s personal check and the freeze sha — not a missing file.**
- **It does not claim the cost model is tested.** `k_adjoint = 1.5` is `ASSUMED`; until `P0` lands,
  §7c is **`UNTESTED`**.
- **It does not claim `P0` will pass.** The adjoint has never been attempted at 579,072 cells.
- **It does not claim the reproduction will land in the band.** `BAND-CL05` can be missed, and a
  miss is a `GATE FAIL` about this lab's ability to reproduce a published result.
- **It does not compare the weighted objective against the published single-point figure** (§1c).
- **It does not claim the guards make the result correct.** They make an **artefact** visible and
  stop the run.
- **It does not claim its synthetic controls prove the case.** Twelve of guard 7's controls and
  three of guard 9's are driven on real measured values; the rest are constructed.

| rule | status | what would be needed |
|---|---|---|
| **2** (wall-resolved) | **DEFERRED by Sanaa §L**, costed for the successor at **×2.36** (§4) | her go on the successor item |
| **4** (curvature constraint) | **NOT SATISFIED FOR THIS REPRODUCTION, by her ruling.** The API **does exist** — `nom_addCurvatureConstraint1D` on `OM_DVGEOCOMP`, pyGeo **1.13.0**, enumerated by execution in the container, with published wing precedent at `Prowim_Wing_Propeller/runScript.py:191-199` — but **adding it would add a constraint the published case does not carry**, which §L forbids. Retained as a **reported diagnostic only** | a successor item that is not a verbatim reproduction |
| **10** (far-field spurious drag) | **NOT SATISFIED** — not available in DAFoam's function set (§6.10) | an external tool, out of scope |
| **11** (literal trust region) | **`PARTIALLY SATISFIED — LITERAL SIZING INFEASIBLE, SUBSTITUTE REGISTERED`** (§6.11) | **Sanaa's answer to the §6.11 question** |
| **16** (adjoint-driven adaptation) | **NOT ATTEMPTED** — her own roadmap item | a separate item |
| **17, 18** | **BOTH IMPLEMENTED.** Rule 17: `d6r3_mesh_read_gate.py` rebuilds the global point set from every rank's `pointProcAddressing` and compares for **exact equality** against the generated mesh, per condition, **before `run_model()`**, aborting on refusal — 10 driven controls, 10 `PASS` (§8d). Rule 18: `D1_ASSERT` re-checks the three carried-over published regions **at import** against the read-only published file (§8a). | — |
| **27** (a channel with a writer) | **partly** — driven for two channels; the pre-freeze channel table does not exist; **the `primal_residual.json` referral is Sanaa's and is not closed here** | her ruling |
| rows 31, 58 | **NOT MEASURED** | `P0` records both |
| **§22.4 clauses 1–3** | **ALL THREE GREEN**, driven at `D6R3_PREFREEZE_RESULT.log` (§8b). **Clause 2's real-anchor result is reported separately from the synthetic case, and the check REFUSED on its first run before the evidence was fixed.** | the supervisor's own personal check before the sha — it is not delegable and this script does not replace it |

**A REGISTERED GAP, NOT ACCOMMODATED.** D6R2's worst measured aspect-ratio trip, **`1050.3162`**,
breached the MACH wing's own declared `1000.0` but sits well inside the CRM's published **`2000.0`**,
so guard 7 reads `OK`. **The published CRM value is kept** (row 52 is verbatim); the gap is recorded
so a reader knows this one clause is looser than D6R2's was, and the control demonstrating it is in
§6.7's table marked `OK` rather than hidden.

**SUBMISSIONS PARKED.** Nothing is sent, filed, uploaded, registered, posted or commented. The
IDWarp rotation defect and the `checkMesh` non-orthogonality behaviour are **defect candidates only,
NOT FILED anywhere**; no filing is drafted or pending. **Filing is Sanaa's alone.**

---
---

# APPENDIX T — **STRUCK 2026-09-13.** R1–R3 material, preserved unrewritten

**STRUCK, NOT DELETED** (rule 6). The full prior revisions are at `9847ffc30` (R1) and `aaab69942`
(R2); R3 was never committed and its distinguishing content is carried forward above.

### T.1 — ~~R1 §3A: the MACH tutorial wing at M 0.288~~ **STRUCK** (Sanaa ruled M 0.85, §3B of R1)

### T.2 — ~~R1 §15d: 10,500 core-min / $8.98~~ and ~~R1 §15e: ≈425,000 core-min / ≈$363~~ **STRUCK** — the latter superseded by the measured CRM adjoint (§7c)

### T.3 — ~~R2 §11b: the verbatim item at 24,900 core-min on L3 (72,384 cells)~~ **STRUCK** — the grid-family gate that chose L3 is struck, so the figure has no mesh

### T.4 — ~~R3 Δ3 `evalMode "exact"`, Δ9 `meshQualityKS` in the adjoint, Δ12 move limits as bounds, Δ15 the curvature constraint~~ **STRUCK** — each **changes the published physics or the optimisation problem**, and §6.0's observer test is what caught them

### T.5 — ~~R3 Δ2 `transonicPCOption 2 → 1`~~ **STRUCK** — the published value runs. **The measurement that motivated it stands** (L-40: `DAResidualRhoSimpleCFoam.C:172-176` accepts only `== 1`, so `2` is inert), and `P0` reports which value was in force. A published null is reproduced as a published null.

### T.6 — ~~R3 Δ5 SLSQP→IPOPT, Δ6 `max_iter 100 → 25`, Δ8 the grid family as a gate, Δ7 `endTime` set by an arm, and the `P1` / `W1` / `P2` selection arms~~ **STRUCK** — a reproduction runs the published values.

### T.7 — Δ1's costed plan is **NOT struck**; it is **DEFERRED** and carried in §4 for the successor.

**SUBMISSIONS PARKED.**
