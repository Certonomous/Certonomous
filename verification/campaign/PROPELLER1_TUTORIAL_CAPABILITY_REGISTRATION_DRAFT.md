# PROPELLER1 — DRAFT REGISTRATION. **NOT FROZEN. NO SHA BINDS IT. NOTHING HAS LAUNCHED.**

> **STATUS BLOCK — DRAFT / UNFROZEN. NOT A GATE.**
> Drafted by a cfd `lab-lane` 2026-09-14 at the cfd-supervisor's direction, against
> `HEAD = 51542d5bffb6c1b78e400ee695c052a978acc471`. Until a freeze commit exists, every gate,
> threshold, cap, band and label below is amendable and carries **no evidentiary weight**
> (CLAUDE.md rule 2). **The title line and this banner are the only two status
> blocks in this document, and BOTH are struck whole at the freeze** — every other sentence is
> written so that freezing and launching cannot make it false. The supervisor's §3 check 1 (measurement-script diff
> read as a diff) and check 4 (pre-registration committed before compute) are not carried by
> this draft and are not claimed by it.
> **Submissions parked (rule 7). No agent's message is Sanaa's consent (rule 9).**

---

## 0. 🔴 THE PREMISE THAT SENT THIS LANE HERE IS FALSE, AND IT IS STATED FIRST

This case was selected as "a resolved-blade propeller, MRF or AMI, ready to put on 32 idle
ranks." **It is neither MRF nor AMI, and as shipped the propeller does not rotate at all.**

Four independent reads off the installed tutorial, each naming its file and line:

| # | what was checked | what is on disk | consequence |
|---|---|---|---|
| 1 | `constant/dynamicMeshDict` | `dynamicFvMesh   staticFvMesh;` is the **active** entry. The line above it, `dynamicMotionSolverFvMesh`, is **commented out** (`// dynamicFvMesh   dynamicMotionSolverFvMesh;`). | The `motionSolver solidBody` / `rotatingMotion` / `omega -158` block below it is **inert**. `staticFvMesh` does not construct a motion solver. |
| 2 | `constant/` directory listing | `dynamicMeshDict`, `transportProperties`, `turbulenceProperties`. **No `MRFProperties`.** | **Not an MRF case.** |
| 3 | `system/` listing | No `createPatchDict`, no `AMIWeights`, no `cyclicAMI` anywhere. | **Not an AMI case.** |
| 4 | `0.orig/U`, patch group `"propeller.*"` | The block contains **two `type` entries**: `movingWallVelocity;` immediately followed by `fixedValue;` with `value uniform (0 0 0)`. | Resolved **with the tool, not by reading**: `foamDictionary -entry 'boundaryField/"propeller.*"' -value` returns `type fixedValue; value uniform (0 0 0)`. **`movingWallVelocity` is dead text.** The blades are stationary no-slip walls. |

**So what the shipped case actually is:** a four-bladed propeller, hub and transmission shaft,
geometrically resolved, held **stationary** in a 5 m/s axial stream, `kEpsilon` RAS, transient
PIMPLE. It is a real, published, non-trivial 3D external-flow case. **It is not a propeller
operating point, and no quantity it produces is a propeller coefficient.**

**The supervisor's stated reason for choosing it — that `topoSetDict` ships staged in
`system/`, so the PPTC defect class cannot occur by construction — IS CONFIRMED AND SURVIVES
INTACT.** `system/topoSetDict` exists (sha256 `d834bf26…`), `Allrun.pre` runs
`runParallel topoSet` with no `-dict` argument in a directory where that dict is already
present, and it creates the `cellZoneSet` named `innerCylinderSmall`. That half of the
reasoning held; the rotation half did not.

### 0.1 What the zone is for here, since there is no MRF and no mesh motion

`innerCylinderSmall` is still **load-bearing at runtime**, which is why §4's precondition is
not ceremonial. Its one live consumer in this case is the `relativeVelocity` function object
(`system/relativeVelocity`: `zone innerCylinderSmall`), which post-processes `U` into a frame
rotating at `n = -25` rev/s **for visualisation only**. A missing zone is a runtime failure of
that FO, not a silently wrong answer — but it is still read off disk by name and count before
launch, per §4, because a logged fatal that nobody reads is how this act lost eleven hours.

---

## 1. THE THREE OPTIONS, SO THAT THE CHOICE IS SANAA'S AND IS MADE ON FACTS

This document **registers Option A only**. B and C are stated so the choice is informed; this
lane does not make it.

| | what it is | rotates? | published setup? | new capability? | cost class |
|---|---|---|---|---|---|
| **A — `propeller1` as shipped** *(registered below)* | resolved blades, **stationary**, axial inflow, `staticFvMesh` | **No** | Yes, unmodified, ships `numberOfSubdomains 32` | No — nothing here the lab has not run | ~1 M cells, ≈ 440 core-min point estimate (§7) |
| **B — the sibling `propeller` tutorial** | genuinely rotating: `dynamicMotionSolverFvMesh` + `solidBody rotatingMotion` across **`cyclicAMI` patches** built by `createPatch` | **Yes** | Yes, unmodified | **YES — AMI has never been run in this lab.** `CHALLENGE_SLATE_2026-08.md` names AMI as "the next qualitatively different step, never run" | smaller base mesh (12×20×12 = 2,880); ships `numberOfSubdomains 4`, so 32 ranks is a **registered departure** from the published decomposition |
| **C — `propeller1` with rotation switched back on** | uncomment `dynamicMotionSolverFvMesh` | Yes | **No — this invents a setup** | — | — |

**Option C is recommended for REFUSAL, and the reason is mechanical, not stylistic.**
`propeller1` has no `createPatchDict` and no `cyclicAMI` patch anywhere. A `solidBody` motion
solver restricted to a `cellZone` moves the points of that zone rigidly while the points
outside it stay put; without an AMI interface on the zone boundary, the shared points are
dragged and the mesh shears. Uncommenting one line therefore does not produce the sibling's
case — it produces an unpublished case whose mesh degrades. Sanaa's rule: *"Inventing a setup
for a case someone has already run in this solver is refused."* **The published rotating
propeller setup in this solver is Option B, and it is one directory away.**

**This lane's honest reading, offered as a recommendation and not as a decision:** if the ask
is *a propeller running*, the answer is **B**, registered openly as the lab's first AMI
capability. **A** is the cheap, clean, same-night 32-rank capability rung that is genuinely
ready, and it is what is registered here — but **A does not answer that ask** and this
document does not pretend it does.

---

## 2. PROVENANCE — §G, DICTIONARIES COPIED AND NOT RE-TYPED

**Source, an unmodified tutorial shipping with the installed binary** (`WM_PROJECT_VERSION =
v2606`, solver at `…/platforms/linux64GccDPInt32Opt/bin/pimpleFoam`):

`/usr/lib/openfoam/openfoam2606/tutorials/incompressible/pimpleFoam/RAS/propeller1`

**Every file is COPIED byte-for-byte. sha256 recorded now, and re-verified against the case
directory as a launch precondition (§4, G-M0).**

| file | sha256 (full) |
|---|---|
| `0.orig/U` | `89f68f7a8385aef2894116f2cc35bf1f98575829e4684c79baad78b7cc48cb40` |
| `0.orig/epsilon` | `127def46c6ea3f9b789f604a100788d0e0e86bdfa56f24fc59e9e1dcb6c4123b` |
| `0.orig/k` | `871d1ac5365363f5fef050dd3878a0928689589e58877f577c8d7b8fe1f56ec5` |
| `0.orig/nut` | `9f038bbd64b1fc5a222759a25b49340794949bdc717761633b4559bc5ac696ee` |
| `0.orig/p` | `e2f1ec5eec001c51f1dc326c83a03c653db521b828d41eb82fbabdce24fcc714` |
| `Allclean` | `e2635ef070584a5d5a87a47706be00082652722cd7adb6c3598fbd3dd8258139` |
| `Allrun` | `9e50d660182a695dba075fe8aac418142d8c12e4f49477f93aefbe1c0bcc0ae9` |
| `Allrun.post` | `0d87a171c7897d4acc7d89da6c8d1e64395de2347c46ce0e66303dfd439a824c` |
| `Allrun.pre` | `7c4e62e23b3ebe4f5c726da96f991dc5554e2b1135a2162e89d5ed5fafe1b2bb` |
| `constant/dynamicMeshDict` | `a628f1c54bfbf35ff89428412e58171c97c06c2c4f6688430319694c27ab0c73` |
| `constant/transportProperties` | `ad2197383f3eb4fc2aee02e8ce81e6d537399c65477015d16b8a84981c1f2d6e` |
| `constant/turbulenceProperties` | `6be4997b6bc220c01c38c54657da44a485ab028c312c535d5f37fbf163ce8a8b` |
| `system/bladeForces` | `2c40be70d20dcfdc16a44781bb3b6ce57068744b065721d4f8b190239f08e68d` |
| `system/blockMeshDict` | `51199ef6d1f5b395d158b0e1885f9e846fb4645307df409ca2c83ea77645977c` |
| `system/controlDict` | `d3357bede1f59e0272948088eb1c193b316f5b9996637e0abffdf8200c727a30` |
| `system/decomposeParDict` | `f641840b9ecbecc2c3e6f3586247d3c23269f889976cab950358710fca430d67` |
| `system/fvSchemes` | `fab19e085e2633a0754f113932c156937eeb8c3b8526280b4640e2f144a048b0` |
| `system/fvSolution` | `0ab9050d1e99cf99da13b6776219c4da452f32c97be018e8c4af28f483b68090` |
| `system/relativeVelocity` | `88ffda322d1a53be8c27622e39b76b66903331317c63ca31b6e4a53de81cb39e` |
| `system/snappyHexMeshDict` | `2b829f8b5cea0bd871b7a787944f7fbd45164a3ad4e219604d3988283279b712` |
| `system/surfaceFeatureExtractDict` | `eee8d70336f93c4f74ad256a1bfe6ec8ab57e1ef72939490511ff01b87231519` |
| `system/surfaceFeatureExtractDict.defaults` | `c9cda58b2a128116afb435077f7e363045598e3e7af831e2c578fec68570121d` |
| `system/topoSetDict` | `d834bf266a077b474b599858acc9e2151a9e293db1c07bb37655556d677b6ed0` |

**Geometry**, copied by `Allrun.pre` from `$FOAM_TUTORIALS/resources/geometry/propeller1`:

| file | sha256 | triangles |
|---|---|---|
| `propeller.obj.gz` | `20c10c0eb6fef74c73e22af5013d57744fe66c5f1b867ef8957b2f73e97c9998` | 144,128 |
| `hub.obj.gz` | `65efac69c7ec46f846c1f0564e29a69983eb38db5116e824f68c2c5b398f58b0` | 1,750 |
| `transmission.obj.gz` | `e0fba38e47113601d5168ea9ed88525a9b4928f4017029e3e4606ac881ac78ac` | 696 |

**Registered departures from the tutorial: NONE at the time of drafting.** Any departure
that is later required is added as a numbered row in a dated addendum and is never taken
silently.

---

## 3. THE CASE, IN ITS OWN NUMBERS — READ FROM THE DICTIONARIES, NOT FROM RECALL

### 3.1 Transient, and the step count is NOT 10,000

`system/controlDict`:

| entry | value |
|---|---|
| `application` | `pimpleFoam` |
| `endTime` | `0.1` s |
| `deltaT` | `1e-5` s |
| **`adjustTimeStep`** | **`yes`** |
| **`maxCo`** | **`2`** |
| `writeControl` | `adjustable` |
| `writeInterval` | `0.001` s → **100 write points** |
| `startFrom` | appears **twice**: `startTime` then `latestTime`; last wins → **`latestTime`** (= 0 on a fresh case) |

> 🔴 **`endTime / deltaT = 10,000` IS NOT THE STEP COUNT AND MUST NOT BE USED AS A COST BASIS.**
> `adjustTimeStep yes` makes `1e-5` the **initial** step only. The step is then set by
> `maxCo = 2` and clipped by `writeControl adjustable` so the run lands exactly on write
> times, which caps `deltaT` at `writeInterval = 1e-3`.
>
> **Registered estimate, made before the run:** smallest registered cell `h ≈ 3.125` mm
> (§3.3), stationary blades, freestream 5 m/s with local peaks taken at 10 m/s ⇒
> `deltaT_Co2 ≈ 2 × 3.125e-3 / 10 ≈ 6.3e-4` s, clipped by `adjustable` to `5e-4` s ⇒
> **≈ 200 steps**. Snapped slivers can be several times smaller than `h`, so the honest
> bracket is **200 to 3,000 steps**, point estimate **600**.
> **PREDICTION (G-N, §6): the realised step count lies in [200, 3000].** Above 3,000 the
> adaptive-`deltaT` reading is wrong and §7's cost model is withdrawn (§9 limb 4).

**Because `deltaT` is adaptive, the strict completion rule's clause 5 is applied in its
adaptive form — `n_exec == steps written` — and NOT as `round(endTime/deltaT)`** (CLAUDE.md
rule 4, the clause-5 adaptive branch, Sanaa 2026-09-09).

### 3.2 Numerics, read from `system/fvSolution` and `system/fvSchemes`

`PIMPLE { nOuterCorrectors 2; nCorrectors 1; nNonOrthogonalCorrectors 0; correctPhi no; }`;
`relaxationFactors "(U|k|epsilon).*" 1`. `ddtSchemes default Euler`;
`div(phi,U) Gauss linearUpwind grad(U)`; turbulence divergence `Gauss upwind`;
laplacian and `snGrad` `limited corrected 0.33`. Pressure `GAMG` (`p` tol `1e-5` relTol `0.01`;
`pFinal` tol `1e-6` relTol `0`); `U,k,epsilon` `smoothSolver`/`symGaussSeidel` tol `1e-6`.

**PARALLEL_GATE_DOCTRINE C2 (per-channel residual tolerances justified or harmonized):** the
spread here is `1e-2` (`pcorr`) to `1e-6`, a factor of `1e4`. **These are the publisher's
values, carried unmodified.** The C2 justification is stated once, here: `pcorr` is a
mesh-flux correction solved to a loose tolerance by design and does not gate this rung;
`pFinal` at `1e-6` with `relTol 0` is the channel that gates the last outer corrector. **No
verdict in §6 rests on a residual channel** — §6 grades stationarity of a physical quantity
plus partition agreement, which is doctrine C3's two-leg form, so the C2 spread is disclosed
rather than load-bearing.

`constant/transportProperties`: `nu = 1e-6` (water). `constant/turbulenceProperties`: `RAS`,
`kEpsilon`, `turbulence on`.

### 3.3 The mesh, and the cell count is an ESTIMATE

`system/blockMeshDict`: domain `x ∈ [-1, 2]`, `y, z ∈ [-1, 1]` m; `xdim = ydim = zdim = 0.05`
⇒ `nx, ny, nz = 60, 40, 40` ⇒ **96,000 base cells at 50 mm**.

`system/snappyHexMeshDict`: `castellatedMesh true`, `snap true`, **`addLayers false`**;
all three surfaces (`hub`, `transmission`, `propeller`) at **`level (4 4)`**;
`nCellsBetweenLevels 3`; `resolveFeatureAngle 30`; feature-edge levels all `0`;
**`refinementRegions` empty — the volume-refinement blocks are commented out**;
`locationInMesh (0.01 -0.5 0.01)`. Level 4 ⇒ **`h = 50/16 = 3.125` mm**.

**Wetted area, MEASURED from the shipped OBJ files by triangle summation** (not estimated):

| surface | area (m²) | bbox |
|---|---:|---|
| `propeller` | 1.03117 | x[−0.0625, 0.1508], y,z[−0.4720, 0.4720] ⇒ **D ≈ 0.944 m** |
| `hub` | 0.19909 | x[−0.1400, 0.1800], y,z[−0.0900, 0.0900] |
| `transmission` | 1.18179 | x[0.1900, **2.1900**], y,z[−0.0900, 0.0900] |
| **total as supplied** | **2.41206** | |
| **total inside the domain** (`transmission` truncated at `x = 2.0`) | **≈ 2.25** | |

> **ESTIMATED CELL COUNT — AND IT IS AN ESTIMATE, NOT A MEASUREMENT. IT COMES FROM THE SHELL
> MODEL BELOW, NOT FROM A BUILT MESH.**
> Shell model, `Σ_{L=1..4} nCellsBetweenLevels × A / h_L²` with `A = 2.25` m², `h_L = 0.05/2^L`:
> `3 × (230,400 + 57,600 + 14,400 + 3,600) ≈ 918,000`, plus 96,000 base, less the cells
> removed inside the solids.
> **Point estimate ≈ 1.0 M cells. Honest bracket 0.7 M – 1.5 M.**
> **PREDICTION (G-M3, §6): the built mesh has between 0.7 M and 1.5 M cells.** A miss is
> recorded as a calibration finding against this shell model, not as a gate failure.

**Cells per rank, at the point estimate (bracket in parentheses):**

| ranks | cells/rank | decomposition |
|---:|---:|---|
| **32** | **≈ 31,000** (22k – 47k) | **`hierarchical`, `n (4 4 2)` — the published setting** |
| **16** | **≈ 63,000** (44k – 94k) | requires changing `n`; a registered departure |

---

## 4. 🔴 LAUNCH PRECONDITIONS — PROVEN ON DISK, BY NAME AND BY COUNT

**None of these is satisfied by an exit code or by a log line.** Each names the artifact that
is parsed and the value that is read out of it. The run does not launch until all pass.

**G-M0 — the case is the tutorial.** `sha256sum` every file in the case directory and compare
against §2. **Any mismatch ⇒ `BLOCKED`**, and the differing file is printed with both hashes.

**G-M1 — THE CELL ZONE, BY NAME AND BY COUNT.**
Parse `constant/polyMesh/cellZones` **directly** — not `log.topoSet`, not `topoSet`'s exit
code, not `checkMesh`'s summary line. Read out:
- the zone **name**, which must be exactly **`innerCylinderSmall`**;
- the zone's **cell count** `N_zone`, read from that zone's own label list.

> **GATE:** the zone exists **by that name**, and `1 ≤ N_zone < N_total`.
> A zone equal to the whole mesh is a `topoSetDict` mis-specification and fails this gate.
>
> **PREDICTION, registered at the freeze and ahead of the mesh build:** the `cylinderToCell` source spans
> `x ∈ [−0.25, 0.25]`, `r ≤ 0.6`, which **encloses the whole propeller** (x[−0.0625, 0.1508],
> r ≤ 0.472) **and the whole hub**, so the zone carries essentially all of their level-4
> refinement: `3 × 1.23 / 0.003125² ≈ 378,000` fine cells plus coarser shells plus the
> unrefined bulk of a 0.565 m³ cylinder. **`N_zone` predicted in [150,000, 800,000].**
> The predicted band is a **prediction, scored at §8**; only the name and `1 ≤ N_zone < N_total`
> are gate-bearing.

**G-M2 — `checkMesh` verdict**, per `docs/standards/MESH_STANDARD.md`, on the built mesh.
**PREDICTION: `Mesh OK`**, `maxNonOrtho < 65` and `maxInternalSkewness < 4` (snappy's own
`meshQualityControls` caps, so a violation means snappy did not honour its own dictionary).
A `checkMesh FAILED` is `GATE FAIL` on the mesh rung and the solver does not launch.

**G-R — 🔴 THE ROTATION STATE, VERIFIED ON THE LAUNCHED CASE, NOT ON THE TUTORIAL.**
This gate exists because §0 found the case is not what it was selected as, and because the
label this rung carries in every downstream record depends on it. Read off the case that is
about to run:

| limb | artifact parsed | required value |
|---|---|---|
| R1 | `constant/dynamicMeshDict` | active `dynamicFvMesh` == `staticFvMesh` |
| R2 | `0.orig/U`, resolved via `foamDictionary -entry 'boundaryField/"propeller.*"' -value` | `type` == `fixedValue` |
| R3 | `constant/` listing | `MRFProperties` **absent** |
| R4 | `constant/polyMesh/boundary` | **no** patch of type `cyclicAMI` |

> **GATE:** all four hold ⇒ the rung is registered, run, graded and reported as
> **STATIONARY-BLADE**, and that word appears on every number it produces.
> **Any limb failing ⇒ `NOT A RESULT`** — not because the case is bad, but because this
> document would then be describing a different case than the one that ran, and the
> registration must be redrawn before compute (§9 limb 3).
> **PREDICTION: all four hold.**

---

## 5. 🔴 PLANTED-ZERO CONTROLS — ONE PER READER — AND THE STOP RULE IN BOTH DIRECTIONS

**Rule 3: a zero from a reader not shown able to see a non-zero is not evidence.** Every
reader below is exercised on a **planted scratch copy** and on the **unplanted original**
before it is allowed to touch a production artifact. Plants are injected into copies under
the case's own `controls/` directory — **never into the production tree, and never into the
scratchpad** (L-186: the scratchpad is not a handoff channel and a repository document never
cites a scratch path).

| reader | plant | value | reader MUST |
|---|---|---|---|
| **P1 — cellZones parser** (G-M1) | copy of `constant/polyMesh/cellZones` with the zone renamed `innerCylinderSmall_PLANT_ABSENT` | *(name plant)* | report the zone **ABSENT** |
| **P1b — cellZones counter** (G-M1) | copy with the zone's label count replaced by a known value | **`PLANT_NZONE = 424242`** | read back **exactly 424242** |
| **P2 — force-history reader** (G-S) | `PLANT_FORCE` added to one **named row index** of a copy of the `bladeForces` output | **`PLANT_FORCE = 1.234e-03`** | read back the perturbed row and recover the difference as `1.234e-03` to within `1e-12` |
| **P3 — completion checker** (G-C) | (a) copy of the solver log with the `End` line deleted; (b) copy with the final time altered | *(structural)* | (a) report **incomplete**; (b) report **last time ≠ `endTime`** |
| **P4 — 🔴 rotation-state reader** (G-R) | copy of `dynamicMeshDict` with `dynamicFvMesh dynamicMotionSolverFvMesh;` active | *(structural)* | report **NOT static** |

> **P4 is the most important plant in this document.** G-R's expected answer is the boring one
> — "yes, static" — and a reader hard-wired to say "static" would pass G-R on **any** input,
> including a case that had been silently switched to rotating. P4 is the only thing that
> distinguishes a working G-R from a constant function.

### 5.1 THE STOP RULE — WRITTEN IN BOTH DIRECTIONS

> **STOP UNLESS THE CONTROL PASSES, IN EITHER DIRECTION.**
>
> For every reader P1–P4, the comparator runs **both** limbs before reading any production
> artifact, and proceeds **only if both** return their own expected answer:
>
> 1. **Planted limb returns the planted answer** — else the reader is **BLIND**.
> 2. **Unplanted limb returns the unplanted answer** — else the reader is **HALLUCINATING**.
>
> A failure in **either** direction ⇒ the comparator **refuses (exit 2)** and the rung is
> **`NOT A RESULT` — instrument defect**, named as such.
>
> 🔴 **A verdict of ANY kind from a reader that failed either limb is DISCARDED, NOT
> RECORDED — `GATE FAIL` included.** This clause is written this way deliberately: a stop
> rule phrased only as *"stop if the gate passes on the known-bad case"* leaves the other
> direction open, and a blind reader then returns a confident `GATE FAIL` from garbage and is
> believed because a failure looks like diligence. **The run is not graded by a reader that
> has not passed both limbs.**

**The comparator refuses rather than degrades** (rule 4). There is no fallback path, no
"partial read", and no clause under which a missing artifact yields a number.

---

## 6. GATES — EACH WITH A THRESHOLD, A LABEL, AND A PREDICTION MADE BEFORE THE RUN

> 🔴 **THERE IS NO VALIDATION TARGET, AND NONE IS INVENTED.**
> Searched and **not found**: the tutorial ships **no** reference `KT`, `KQ`, thrust, torque or
> efficiency — no `README`, no `*.dat`, no validation directory (the tutorial tree is the 23
> files hashed in §2 and nothing else). The geometry is an unnamed generic propeller with a
> `stdHub_1p5` hub and an `STI_YEH_Index-0` transmission; **no published open-water data for
> it is on this box.** The sibling `propeller` tutorial ships none either.
> **The lab's PPTC / VP1304 `KT`–`10KQ` tables (SVA Potsdam Report 3752) are for a DIFFERENT
> PROPELLER and may not be used here.** No paper is cited by this document, so rule 15's
> title-page requirement has nothing to bite on — and that is stated rather than left to
> inference.
>
> **THEREFORE THIS IS REGISTERED AS A CAPABILITY / REPRODUCTION RUNG, NOT A VALIDATION RUNG.**
> It asks: *does this published setup build, mesh, decompose to 32 ranks, run to `endTime`,
> and produce a stationary, partition-independent force?* It does **not** ask whether that
> force is right, because nothing on this box can answer that.

> 🔴 **`KT` AND `KQ` FROM THIS RUN ARE NOT PROPELLER COEFFICIENTS AND MAY NEVER BE REPORTED AS
> SUCH.** `system/bladeForces` carries `n 25` rev/s and `Uref 5`, and will dutifully print
> `KT`/`KQ` — **for blades that are not turning** (§0, G-R). Those numbers are an artefact of a
> hard-coded rotation rate in a post-processing dictionary, not a measurement of anything.
> **The graded quantity is the raw axial force on the blade patches, in newtons.** This
> prohibition has the same force as the one at `verification/campaign/PPTC_CFM1_PREREGISTRATION.md`
> §D9(b), and it is registered at the freeze, ahead of the run.

| gate | statement | threshold | verdict on failure | **prediction** |
|---|---|---|---|---|
| **G-M0** | case files match the §2 hashes | byte-exact | `BLOCKED` | all match |
| **G-M1** | `innerCylinderSmall` present in `constant/polyMesh/cellZones`, by name, with `1 ≤ N_zone < N_total` | as stated | `BLOCKED` — solver does not launch | present; `N_zone ∈ [150k, 800k]` |
| **G-M2** | `checkMesh` verdict | `Mesh OK` | `GATE FAIL` (mesh rung) | `Mesh OK` |
| **G-M3** | built cell count | `∈ [0.7 M, 1.5 M]` | **prediction only** — a miss is a calibration finding, not a failure | `≈ 1.0 M` |
| **G-R** | rotation state, four limbs (§4) | all four | `NOT A RESULT` — re-register before compute | all four hold |
| **G-N** | realised step count | `∈ [200, 3000]` | cost model withdrawn (§9 limb 4); the rung continues | `≈ 600` |
| **G-C** | strict completion, rule 4, **adaptive-`deltaT` branch** | `rc = 0`; `End` line; **last time == `0.1` == `endTime`**; fields `U p k epsilon nut phi` present at `endTime`; **`n_exec == steps written`**; **every field at `endTime` newer than the case's own `0/U`** (age guard) | `NOT A RESULT` | `PASS` |
| **G-S** | **stationarity of the graded axial force** over the **registered window `t ∈ [0.07, 0.10] s`** (the final 30 % of the run, fixed at the freeze and ahead of the force history): `\|mean(second half) − mean(first half)\| / \|mean(window)\| < 0.02` | **2 %** | `GATE FAIL` | `PASS` |
| **G-P** | **partition robustness**, doctrine C3 leg 2: the §G-S window-mean force agrees between the **32-rank** and **16-rank** runs | **1.0 %** | `GATE FAIL` | `PASS` — F6a measured graded quantities moving `2.2e-5` across partitions |

**G-S's window is fixed at the freeze, ahead of the force history.** That is the whole
evidentiary content of registering it: it cannot later be slid to the quietest interval. It is
an **absolute window in simulation time**, not a fraction of the step count, so declaring a
longer run cannot re-classify an existing transient out of it — the same defect repair that
`MRF_R3_RERUN_REGISTRATION_DRAFT.md` §3 makes for iteration windows.

**Doctrine C1 (deterministic decomposition) is satisfied by the published setting**, not by a
departure: `system/decomposeParDict` ships `method hierarchical; n (4 4 2)` at
`numberOfSubdomains 32`. Hierarchical is geometric and reproducible — identical input gives
identical partitions. **Checked, not assumed:** decompose twice and compare
`processor*/constant/polyMesh/cellProcAddressing`.

**No Roache triple is registered and no GCI is quoted.** This is a single-mesh capability
rung; there is no grid family, so rule 5 has nothing to gate and **no order of accuracy, no
GCI and no `PASS` against a reference may appear in its record.**

---

## 7. RANK COUNT AND COST — AND THE 32-RANK SIZING IS EXTRAPOLATION

### 7.1 The honest rank recommendation

At the point estimate the case lands at **≈ 31,000 cells/rank on 32 ranks**.

> 🔴 **THIS LAB HAS NO MEASURED STRONG-SCALING BASIS BELOW ≈ 200,000 CELLS/RANK.** The nearest
> artifact is a 4-rank probe. **The 32-rank sizing in this document is EXTRAPOLATION, and
> saying so is not a formality — it is the reason §7.2 exists.**

Two facts pull in opposite directions and both are stated:

1. **For 32:** it is the **published decomposition**. `numberOfSubdomains 32` with
   `n (4 4 2)` is what the publisher shipped; using it keeps §G intact, satisfies doctrine C1
   without modification, and it is exactly the idle capacity. Changing it is itself a
   registered departure that would need its own justification.
2. **Against 32:** ≈ 31k cells/rank is thin. It sits inside the band general OpenFOAM practice
   treats as usable, but **this lab has not measured that**, and a figure taken from general
   practice is not a measurement (rule 12: a cost is never called measured unless a record
   backs it).

> **RECOMMENDATION: run at 32, as published — and make that recommendation FALSIFIABLE rather
> than asserted, by acquiring the missing basis at negligible cost.**
> Taking 32 ranks because they are free, with no basis, is exactly the move the brief warns
> against. Taking 32 ranks **because the publisher chose 32**, while **measuring** whether it
> was the right choice, is not.

### 7.2 G-P doubles as the scaling probe the lab does not have

The G-P partition-robustness run (§6) is required by doctrine C3 anyway. Running it at **16
ranks** rather than at a second 32-rank partition costs the same and buys the lab its **first
measured strong-scaling point above 4 ranks**: `core-min/step` at 32 and at 16 on an identical
mesh.

> **DECISION RULE, REGISTERED BEFORE THE PROBE:** if the measured 32-rank wall-time-per-step is
> **less than 1.3×** faster than the 16-rank figure, the production run is re-sized to **16
> ranks** and the spare 16 ranks are returned. The measured pair lands in
> `docs/COST_CALIBRATION.md` either way — **this rung's most durable product may well be that
> scaling point, not its force.**

### 7.3 Cost, in core-minutes, before it runs (rule 12)

| stage | ranks | basis | core-min |
|---|---:|---|---:|
| `Allrun.pre` (`surfaceBooleanFeatures` on 144k triangles, `blockMesh`, `surfaceFeatureExtract`, `decomposePar`, `snappyHexMesh`, `topoSet`, `checkMesh`, `renumberMesh`) | 32 | **ESTIMATE**, no measured basis for snappy at this size on this box | **≈ 120** |
| solver, point estimate (600 steps) | 32 | **DERIVED** — see below | **≈ 320** |
| G-P probe at 16 ranks (short, `N` steps, not to `endTime`) | 16 | **ESTIMATE** | **≈ 30** |
| **point-estimate total** | | | **≈ 470** |
| **upper bracket** (3,000 steps, 1.5 M cells, mesh 150) | | | **≈ 1,750** |

**`cost_basis` — DERIVED, and the derivation is shown so it can be attacked.** The solver
figure scales the lab's own measured `simpleFoam` rate of **0.267099 core-min per iteration
per Mcell** (`verification/campaign/SUBOFF_A1_PREREGISTRATION.md:1622`) by **2×** for
`nOuterCorrectors 2`, giving ≈ 0.534 core-min/step/Mcell ⇒ ≈ 0.53 core-min/step at 1.0 M cells
⇒ ≈ 320 core-min at 600 steps. **Two things this basis does NOT carry, stated rather than
buried:** (i) the SUBOFF anchor is **serial** (`ranks = 1`), so it is a
**parallel-efficiency-1.0 FLOOR** — the realised cost will be higher by whatever inefficiency
§7.2 measures at 31k cells/rank; (ii) it is a `simpleFoam` steady rate transplanted to a
transient PIMPLE step, which is an assumption, not a measurement.

**Dollars: ≈ $0.40 at the point estimate, ≈ $1.50 at the upper bracket — DERIVED, NOT
MEASURED.** At the owner-stated `$0.0513/core-h` (c7a.4xlarge, Sanaa 2026-08-21/22); **the box
cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar figure here is a
measurement.

**No cap stops this run** (Sanaa's NO CAP ruling, 2026-09-12, directive #17). The figures above
are rule-12 predictions, and the **estimate-versus-actual row is owed to
`docs/COST_CALIBRATION.md` at completion** — including the §7.2 scaling pair and an honest
scoring of the G-M3 and G-N predictions.

---

## 8. WHAT IS SCORED AT COMPLETION

Predictions registered here and scored afterwards, whether they land or miss:
**G-M3** (cell count in [0.7 M, 1.5 M]) · **G-M1** (`N_zone` in [150k, 800k]) ·
**G-N** (steps in [200, 3000]) · **§7.3** (core-min against actual, with the gap attributed to
contention, waste or misprediction, waste named separately per `COMPUTE_BUDGET_CHARTER` §6) ·
**§7.2** (the 1.3× speed-up decision rule).

---

## 9. REFUSAL LIMBS — WHAT WOULD SAY THE INSTRUMENT IS WRONG, NOT THE CASE

1. **Any reader fails either limb of §5.1.** Instrument. `NOT A RESULT`. No verdict recorded,
   in either direction.
2. **`checkMesh` reports `cell zones: 0` while `topoSet` returned `rc = 0`.** This is the PPTC
   defect class exactly — pipeline, not case. The zone is re-created and the pipeline defect is
   written down before anything is graded.
3. **G-R limb R1 reports NOT-static on the unmodified shipped `dynamicMeshDict`.** Then §0 of
   this document is **wrong**, its premise is false, and **the registration is withdrawn and
   redrawn** rather than amended. A document whose §0 is false cannot be repaired by an
   addendum.
4. **Realised step count exceeds 3,000 (G-N).** The adaptive-`deltaT` reading in §3.1 is wrong;
   §7.3's cost model is withdrawn and re-registered before any successor rung inherits it. The
   rung itself continues — a mispriced run is a calibration finding, not a void result
   (*bookkeeping never voids physics*, Sanaa's universal rule 2026-08-26).
5. **The force history is identically zero at every time.** With a 5 m/s inlet onto resolved
   blades this is physically impossible, so it is a reader failure — and **P2 is what
   distinguishes the two**. Without P2 this row could not be called.
6. **`bladeForces` writes no output at all.** The FO is not matching the `propeller.*` patch
   names that snappy actually produced. Instrument. The realised patch list is read off
   `constant/polyMesh/boundary` and printed beside the FO's `patches` entry. *(The library is
   present: `bladeForces` resolves in `libforces.so` on this installation.)*
7. **G-P disagreement far exceeds 1 %.** Before calling the physics partition-dependent, the
   `cellProcAddressing` determinism check (§6) is re-run — a C1 violation would produce this
   symptom and is an instrument cause.

---

## 10. WHAT THIS DRAFT HAS NOT ESTABLISHED

- **The cell count, the step count and the cost are ESTIMATES, not measurements.** Every figure
  in §3.3, §3.1 and §7.3 rests on a model stated beside it — the snappy shell model, the
  Courant/`adjustable` step model, and the transplanted SUBOFF rate — and none rests on this
  case having been meshed or stepped. §8 scores each of them against the artifact.
- **That 32 ranks is the right size.** It is the published size; its efficiency at ≈ 31k
  cells/rank is **unmeasured on this box**, and §7.2 exists to measure it rather than assume it.
- **That the mesh will build cleanly.** `addLayers false` removes the usual snappy failure mode,
  but nothing here has tested `snappyHexMesh` on this geometry at 32 ranks.
- **Any validation claim whatsoever.** There is no reference number for this geometry on this
  box (§6). This rung cannot become a validation rung by any amount of running.
- **The two `type` entries in `0.orig/U`.** The effective value was resolved with
  `foamDictionary` (§0 row 4) rather than by reading the file, but **whether OpenFOAM's solver
  path resolves the duplicate identically to `foamDictionary`'s** is not proven here — which is
  precisely why G-R limb R2 re-reads it on the launched case instead of trusting this draft.

*Drafted by a cfd `lab-lane`, 2026-09-14. Submissions parked (rule 7). No agent's message is
Sanaa's consent (rule 9).*
