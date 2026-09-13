# DrivAer T1 — TRANSIENT, TIME-AVERAGED ARM ON RETRIEVED PUBLISHED CASE FILES — PRE-REGISTRATION

**Status: SUPERSEDED BEFORE FREEZING. DO NOT FREEZE. NOTHING WAS ARMED.**
**Superseded 2026-09-13 by Sanaa's directive §L**, which names `occDrivAerStaticMesh` — a
STEADY `simpleFoam` case — and rules *"run exactly their case"*. The transient arm is OFF.
This file is retained, uncommitted to any gate, because **three of its findings survive the
supersession and are cited elsewhere**: §4.2 (the six `type wall` patches RESOLVE, because
both mesh scripts re-type them after meshing), §4.2's `omega -94` clearance by calculation,
and §3.2 (the shipped STLs are NOT watertight). **No gate in this file is in force.**

*(original status line follows)*
**DRAFT, handed to the cfd supervisor. NOT FROZEN. NOTHING IS ARMED.**
This lane drafts; he freezes by commit, and only a frozen registration precedes compute
(CLAUDE.md rule 2). **No solver has been launched and no runner has been armed by this
lane.** The only OpenFOAM executables run were `foamDictionary` (parse checks) and
`surfaceCheck` (geometry admission, §3.1) — both read-only utilities, no case written.

**Authority.** Sanaa's directive `docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md`
§G (published-setup rule), §I and §J (*"I KEEP saying i am on a time constraint so we
need to use other ppls files"*), §K (*"for drivaer, there is file to download"*).
Supervisor's instruction, this session: the **transient, time-averaged** arm is the
deliverable; the steady R5 arm is not.

**The governing rule of this document: dictionaries are COPIED, not RE-TYPED.** Every
parameter row below reads either **COPIED VERBATIM** with the sha256 of the file it came
from, or **NAMED DIFF** with a one-line registered reason. A re-typed dictionary is a
transcription with an error rate; a copied one has a hash.

---

## 1. THE PROBLEM THIS REGISTRATION HAS TO SOLVE HONESTLY, STATED FIRST

**The retrieved Wolf Dynamics case is STEADY. The deliverable is TRANSIENT.** Its
`system/controlDict` reads `application simpleFoam;` and its
`constant/turbulenceProperties` reads `RASModel kOmegaSST`. **There is therefore no
single retrieved tree that can be adopted verbatim for this arm**, and any claim that
there is would be false.

**Resolution, and it is the whole architecture of this registration.** Two retrieved
trees are used, each verbatim in its own domain, and **every join between them is a
named diff**:

| Domain | Source, verbatim | Why this source |
|---|---|---|
| Geometry, mesh recipe, boundary conditions, force/y+ post-processing | **Wolf Dynamics DrivAer** (OpenFOAM 9) | Complete, self-contained, **its own STL ships**, and its author's own force and y+ results ship for checking |
| Transient solver, turbulence model, transient schemes, averaging | **HPC-TC `occDrivAerRotMesh`** (Upstream CFD / exaFOAM, pimpleFoam DDES) | A **published OpenFOAM transient DrivAer** setup with a `fieldAverage` function object and a two-stage init-then-average control structure, on disk, hashed |

**occDrivAer's static/HPC-Challenge case is NOT used as a setup and cannot be**: it ships
**no mesher dictionary of any kind**, and its 65/110/236 M polyMesh tarballs (Zenodo
15012221) are not on this box.
*(`docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` F-1, committed `799c88e7`.)*

---

## 2. SOURCES AND THEIR HASHES

All trees at `/home/ubuntu/upstream/published-openfoam-setups/`; per-file manifests at
`SHA256SUMS.wolfdynamics-drivaer.txt` (101 files) and `SHA256SUMS.openfoam-hpc-tc.txt`
(229 files). Provenance, retrieval timestamps and parse verification:
`docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md` §1.

| File adopted | sha256 | Adopted as |
|---|---|---|
| `drivaer_fine/system/snappyHexMeshDict` | `bd3794109d26306e9e11f0595b53240668d4390f95b6ddc6fd73ebc80407abd0` | **VERBATIM** |
| `drivaer_fine/system/blockMeshDict` | `2b3471e81c19ac8270eb69e8f79d6ff49ff98cd3b975bf332eb248e5b315754b` | **VERBATIM** |
| `drivaer_coarse/system/blockMeshDict` | `6226fc88b6cdac40789574edbd2684eb8652395364057a71a27422616bac5080` | **VERBATIM** (T1c only) |
| `drivaer_coarse/system/snappyHexMeshDict` | `15c95efb0633bdb2df49c16a8f54fcbf53d745bb7bc44d816cfd15de17134593` | **VERBATIM** (T1c only) |
| `constant/triSurface/body2.stl` | `fbc6c7a88561f563c42753ce06a00f97a2629fec7a86341eeddc99d67443c7c9` | **VERBATIM** |
| `constant/triSurface/ruotaant.stl` | `fee22c417fb1ad2a59b41c78aaa3ee885348ab68b641602c99ce7b18bb7fe7de` | **VERBATIM** |
| `constant/triSurface/ruotapost.stl` | `29c9b39790b73856b5a2039cbe502706d5c130b26ece503a0e1d3120f14080c2` | **VERBATIM** |
| `drivaer_coarse/constant/transportProperties` | `917ba87a40e207c785ab06471c59d51060533d472208799d5e61d92bb352c86a` | **VERBATIM** |
| `drivaer_coarse/system/controlDict` | `fdd80e811c935cf11efadcce0b9571968723eed2ebd05326c01d1cf0de0aed46` | function objects VERBATIM; time control DIFFED (§5) |
| `occDrivAerRotMesh.orig/system/fieldAverage` | in `SHA256SUMS.openfoam-hpc-tc.txt` | **VERBATIM** |
| `occDrivAerRotMesh.orig/constant/turbulenceProperties.LES` | in `SHA256SUMS.openfoam-hpc-tc.txt` | **VERBATIM** (model + delta) |
| `occDrivAerRotMesh.orig/system/{fvSchemes.DDES,fvSolution.DDES}` | in `SHA256SUMS.openfoam-hpc-tc.txt` | **VERBATIM** |

**[VERIFIED HERE] The three STL files are byte-identical between the coarse and fine
trees** (same sha256 each). Geometry is therefore **one object**, hashed once, common to
every level of the family.

---

## 3. GEOMETRY ADMISSION — MEASURED, NOT ASSUMED

### 3.1 The measurement

**[VERIFIED HERE]**, `surfaceCheck` on the shipped STLs (OpenFOAM v2606, read-only):

| Surface | Triangles | Bounding box span (m) |
|---|---|---|
| `body2.stl` | 367,981 | **4.61283 × 1.00438 × 1.26711** |
| `ruotaant.stl` | 40,426 | 3.88297 × 0.32414 × 1.26065 |
| `ruotapost.stl` | 40,426 | 1.09679 × 0.32730 × 1.26065 |

**Registered scale finding: this is the FULL-SCALE DrivAer as a HALF MODEL, not a 1:2.5
wind-tunnel model.** Three independent numbers agree and are recorded as the basis:
body length **4.61283 m** (published full-scale DrivAer ≈ 4.613 m); the two
`rotatingWallVelocity` origins in `0_org/U` at x = 0.007 and x = 2.793, separation
**2.786 m**, which is the DrivAer full-scale wheelbase to four figures; and
`forceCoeffsAll`'s `Aref 1.073476` m², half of a ≈2.147 m² full-scale frontal area.

### 3.2 ADMISSION DISCLOSURE — the surfaces are NOT watertight, and this is registered, not fixed

**[VERIFIED HERE]** `surfaceCheck` reports **`body2.stl` has 1,101 illegal triangles**
and is **not closed** (550,895 edges not connected to two faces); each wheel STL has
**9 illegal triangles** and is likewise not closed.

**This is registered as a disclosure and the file is NOT repaired.** Sanaa's rule governs:
a value that looks wrong is recorded, not changed; and repairing a shipped STL would
destroy the one property that makes this arm worth running — that the geometry is
byte-identical to the published author's. snappyHexMesh tolerates open surfaces by
construction. **What the disclosure obliges: the mesh birth certificate must report
`checkMesh` in full, and any surface-derived defect is attributed here first.**

---

## 4. THE CASE — copied rows and named diffs

### 4.1 Physics and boundary conditions — ALL COPIED VERBATIM

**[VERIFIED HERE]** from `drivaer_coarse/0_org/{U,p}` and `constant/transportProperties`.
The final patch typing is **not** what `blockMeshDict` declares — see §4.2.

| Quantity | Value | Source |
|---|---|---|
| `nu` | `1.5881327800829875E-5` m²/s | `constant/transportProperties`, VERBATIM |
| Freestream `U` | `(30 0 0)` m/s | `0_org/U`, VERBATIM |
| `rhoInf` | `1.205` | `system/controlDict` forceCoeffs, VERBATIM |
| `Aref` | `1.073476` m², `lRef` `1.0` m, `CofR (0 0 0)` | `system/controlDict`, VERBATIM |
| Inlet `ffminx` | `U` fixedValue (30 0 0); `p` zeroGradient | VERBATIM |
| Outlet `ffmaxx` | `U` inletOutlet (30 0 0); `p` fixedValue 0 | VERBATIM |
| Symmetry `ffminy` | `U`/`p` symmetry | VERBATIM |
| Side `ffmaxy`, roof `ffmaxz` | `U`/`p` slip | VERBATIM |
| **Moving ground** `ffminz` | **`U` fixedValue (30 0 0)**, `p` zeroGradient | VERBATIM |
| Body `body2` | no-slip | VERBATIM |
| **Rotating wheels** | `rotatingWallVelocity`, `omega -94` rad/s, axis (0 1 0), origins (0.007 0 0.29) and (2.793 0 0.29) | VERBATIM |

**Reynolds number, registered as derived not copied:** `Re = U·L_body/nu = 30 × 4.61283 /
1.5881327800829875e-5 = 8.714e6`.

### 4.2 SUPERVISOR CONDITION 2 — THE SIX `type wall` PATCHES. **RESOLVED, NOT BLOCKED.**

The condition raised was that `blockMeshDict` types all six farfield patches `type wall`,
including a half-car `ymin 0`/`ymax 4`, and that if it did not resolve cleanly it is a
`BLOCKED`, not a guess.

**[VERIFIED HERE] It resolves cleanly, and the mechanism is explicit in the shipped
scripts.** *Both* mesh routes — `run_mesh_shm.sh` and `run_mesh_fluent.sh` — end with six
`foamDictionary constant/polyMesh/boundary -entry entry0/<patch>/type -set <type>` calls
that **re-type every farfield patch after meshing**, plus six `-remove` calls stripping
`inGroups`. The `wall` typing in `blockMeshDict` is **scaffolding that never reaches the
solver.** The operative typing is:

| Patch | `blockMeshDict` says | Re-typed by the mesh script to | `0_org/U` | `0_org/p` | Physical role |
|---|---|---|---|---|---|
| `ffminx` | wall | **patch** | fixedValue (30 0 0) | zeroGradient | inlet |
| `ffmaxx` | wall | **patch** | inletOutlet | fixedValue 0 | outlet |
| `ffminy` | wall | **symmetry** | symmetry | symmetry | half-model symmetry plane |
| `ffmaxy` | wall | **patch** | slip | slip | far side, slip |
| `ffminz` | wall | **wall** | **fixedValue (30 0 0)** | zeroGradient | **moving ground / belt** |
| `ffmaxz` | wall | **patch** | slip | slip | roof, slip |

**Registered as a gate, not a note (G4, §7): the `constant/polyMesh/boundary` types must be
read back from disk after meshing and match this table exactly, before the solve.** A
mesh that reaches the solver with six `wall` patches is a `BLOCKED` case, because it would
impose a no-slip tunnel floor, roof and both sides on a half-car domain.

**Second condition cleared, and it was nearly registered as a defect.** `omega -94` rad/s
against a freestream of 30 m/s implies a rolling radius of `30/94 = 0.31915` m, while the
wheel-centre height in the same entry is `0.29` m — a 0.029 m difference that reads as a
9 % slip. **It is not a slip; it is contact-patch flattening**: the DrivAer wheels are
modelled deformed, so the centre sits below the undeformed rolling radius. `omega -94` is
consistent with rolling without slip on a 30 m/s belt. **Recorded as cleared by
calculation, not waved through**, and not changed.

### 4.3 SUPERVISOR CONDITION 3 — THE VERSION DISAGREEMENT. **THE SHIPPED LOG IS THE AUTHORITY.**

| Claim | Says |
|---|---|
| Download page | OpenFOAM 9 |
| `system/blockMeshDict` header | Version 9 |
| `system/snappyHexMeshDict`, `constant/transportProperties`, `constant/turbulenceProperties` headers | **Version 7** |
| **`sol_logs/coarse/log.solver`** | **`Build : 9-6adb71a2e61d`** |

**REGISTERED: the shipped solver log is the authority, and the version-7 headers are stale
banners on files carried forward.** The reason is evidentiary, not preferential: a
dictionary header is an unverified string a human typed and never re-typed; **the build
line is written by the executable that actually produced the distributed results.** One is
a claim, the other is a record of an event.

**Consequence registered:** the lab runs **OpenFOAM v2606**, neither 7 nor 9. Every
dictionary is therefore re-read by `foamDictionary` under v2606 before the solve (G1),
and **any v2606 keyword rejection is a finding to be reported, not silently patched.**

---

## 5. THE TRANSIENT SPECIFICATION — FIXED IN ADVANCE, WHICH IS THE POINT

### 5.1 What the published transient source does, and its own disclaimer

**[VERIFIED HERE]** `occDrivAerRotMesh.orig/system/include/caseDefinition`:

```
dt        1e-4     // Timestep
tAvg      0.2      // Time when to start averaging (in s) - 0.05s approx. equal to 1 full rotation of the wheel
tEnd      0.5      // End time of simulation (in s)
LESturbModel  kOmegaSSTDDES
deltaTurb     maxDeltaxyz
```

with `controlDict.DDES.init` running `endTime $tAvg` and `controlDict.DDES.avg` running
`endTime $tEnd` with `fieldAverage` enabled. **The published practice therefore FIXES the
window in advance in a two-stage structure, and does not detect it from the trace.** That
structure is adopted verbatim.

**Its own README disclaims its own window, and this is quoted because it drives the one
diff that matters:**

> *"The predefined time settings are not meant for a real statistical average. For
> meaningful statistics, the transient is longer and the averaging time frame is too
> short."* — `occDrivAerRotMesh/README.md:86`

**Copying that window would be copying a window its authors say is inadequate.** So: the
**structure** is copied verbatim; the **duration** is a NAMED DIFF, lengthened, with its
reason and its arithmetic below.

### 5.2 The registered window — stated in convective units so it transfers

**[VERIFIED HERE]** scales measured in §3.1 and §4.1: body length `L = 4.61283` m,
`U = 30` m/s, wheel `omega = 94` rad/s.

```
CTU  (convective time unit, body)  = L/U   = 4.61283 / 30  = 0.153761 s
T_wheel (one wheel revolution)     = 2pi/omega = 2pi/94    = 0.0668435 s
```

| Stage | Registered duration | In CTU | In wheel revolutions | Published case, for comparison |
|---|---|---|---|---|
| **Stage A — transient discard** | **0.768805 s** | **5.0 CTU** | 11.50 rev | 0.2 s = 2.79 CTU(wheelbase), 4 rev |
| **Stage B — averaging window** | **3.075220 s** | **20.0 CTU** | 46.01 rev | 0.3 s = 4.19 CTU(wheelbase), 6 rev |
| **Total** | **3.844025 s** | 25.0 CTU | 57.51 rev | 0.5 s |

**Registered reason for the diff, one line:** the published source states in its own README
that its transient is too short and its averaging window too short for meaningful
statistics; 5 CTU discard and 20 CTU averaging is the automotive-DES convention and is
chosen **before** any trace exists.

**THE WINDOW IS FIXED, NOT DETECTED. No part of it may be moved after the trace is seen.**
Stage B begins at `t = 0.768805 s` whatever the trace looks like.

### 5.3 The stationarity evidence required to ENTER the window — registered as a TEST, not a GATE on entry

Entry into Stage B is **unconditional and time-based**, deliberately, so that no
post-hoc judgement can move it. Stationarity is instead **measured and reported**, and it
gates the *verdict*, not the *schedule*:

> At the end of Stage A, the `Cd` trace over the final 1.0 CTU is fitted with a linear
> trend. **The fitted drift must be below 1e-3 per CTU in `Cd`.** If it is not, Stage B
> still runs on schedule, and **the arm is graded `GATE FAIL` on stationarity** with the
> measured drift printed beside it. **A drifting trace is never re-labelled by extending
> Stage A after the fact.**

### 5.4 Numerics — copied, with `deltaT` the one derived diff

| Setting | Value | Status |
|---|---|---|
| Solver | `pimpleFoam` | **COPIED** from `controlDict.DDES.{init,avg}` |
| Turbulence | `kOmegaSSTDDES`, `delta maxDeltaxyz` | **COPIED** from `turbulenceProperties.LES` |
| `fvSchemes`, `fvSolution` | as `fvSchemes.DDES`, `fvSolution.DDES` | **COPIED** |
| `fieldAverage` (`U`, `p` with `prime2Mean on`; `nut`, `wallShearStress` mean) | as shipped | **COPIED** |
| Force/y+ function objects, `Aref`/`lRef`/`CofR`/`rhoInf` | as shipped | **COPIED** from Wolf Dynamics `controlDict` |
| **`deltaT`** | **5.0e-4 s** | **NAMED DIFF — derived, see below** |

**Registered derivation of `deltaT`, because it cannot be copied.** The published `dt = 1e-4`
s is tuned to a 238 M-cell mesh at `U = 38.889` m/s, whose finest surface cell is
1.9531 mm — i.e. a cell Courant number of `38.889 × 1e-4 / 1.9531e-3 = 1.99`. Our fine
level's wall cell is `0.2 / 2^4 = 0.0125` m at `U = 30` m/s. **Matching a Courant number
of 1.2** (deliberately below the published 2.0, since our PIMPLE settings are copied from
a case with different cell aspect ratios) gives `dt = 1.2 × 0.0125 / 30 = 5.0e-4 s`
exactly. **Registered as fixed at 5.0e-4 s**; `adjustableRunTime no`, no adaptive stepping.
Total steps = `3.844025 / 5.0e-4` = **7,689**.

**Registered prediction on the Courant number, so the derivation is falsifiable:** the
`CourantNo` function object's reported **mean** Courant over Stage B lies in **[0.2, 1.5]**
and its **max** below **8**. Outside that, the derivation was wrong and it is recorded as a
misprediction rather than quietly re-tuned.

---

## 6. LEVELS

| Level | Mesh dictionaries | Wall cell | Layers | Ranks |
|---|---|---|---|---|
| **T1f** (the deliverable) | `drivaer_fine/system/{blockMeshDict,snappyHexMeshDict}`, VERBATIM | 0.0125 m | `nSurfaceLayers 6` | 48 |
| **T1c** (companion, same window) | `drivaer_coarse/system/{blockMeshDict,snappyHexMeshDict}`, VERBATIM | 0.025 m | `nSurfaceLayers 3` | 16 |

**REGISTERED RESOLUTION DISCLOSURE, and it is the honest limit of this arm.** Both meshes
are **wall-function RANS meshes**, not DES meshes. Their author's own shipped y+ proves it:
**[VERIFIED HERE]** at the last iteration, `body2` mean y+ is **96.03** (coarse) and
**56.99** (fine). A DDES run on a mesh built for wall functions resolves far less of the
boundary layer than the published 238 M-cell DDES case does. **This arm is registered as
"transient, time-averaged, DDES closure on a published wall-function mesh", and it may
NOT be presented as a wall-resolved DES.** The layer stacks are `S = 1.197` (fine) and
`S = 0.758` (coarse) local cells, both inside published snappyHexMesh practice
(`MESH_STANDARD.md` §17 draft, §17.1).

---

## 7. GATES AND DISCLOSURES — frozen before any compute

| ID | Gate | Threshold | Verdict words |
|---|---|---|---|
| **G1** | Every adopted dictionary parses under **v2606** and its sha256 matches §2 | exact match, all 13 | PASS / BLOCKED |
| **G2** | `checkMesh` on each level | zero negative volumes, zero wrong-oriented pyramids; max non-orthogonality and max skewness **reported beside the result**, not gated (two-tier, §15) | PASS / GATE FAIL |
| **G3** | Layer coverage read from the **post-extrusion table** (§16.6 rule L5) | achieved coverage **reported per patch**; an absent table means achieved = 0, never "unknown" | PASS / GATE FAIL |
| **G4** | `constant/polyMesh/boundary` types read back from disk match §4.2 exactly | 6/6 | PASS / **BLOCKED** |
| **G5** | Stage-A stationarity (§5.3) | `Cd` drift < 1e-3 per CTU over the final 1.0 CTU | PASS / GATE FAIL |
| **G6** | Courant prediction (§5.4) | mean ∈ [0.2, 1.5], max < 8 | PASS / GATE FAIL |
| **G7** | **Planted control** — a known perturbation is written into the force field and the comparator must read it back | comparator **REFUSES** if it cannot see the plant | PASS / **refuse, exit 2** |
| **G8** | Completion (CLAUDE.md rule 4, all clauses) | `rc=0`; `End`; last time == `endTime`; fields present; step count == steps written; **every field newer than the case's own `0/` (age guard)** | PASS / not done |

### 7.1 SUPERVISOR CONDITION 1 — REGISTERED IN TERMS: `Cd = 0.2912` IS NOT A CONVERGED REFERENCE

**[VERIFIED HERE]** from the shipped files, not from any number of ours:

| Wolf Dynamics level | last iteration | `Cd` | drift over the last iteration |
|---|---|---|---|
| coarse (`sol_logs/coarse/postProcessing/all/0/forceCoeffs.dat`) | 1000 | **0.2911626517668** | **−8.64e-04** (0.2920268 → 0.2911627) |
| fine (`sol_logs/fine/postProcessing/all/0/forceCoeffs.dat`) | 10000 | **0.2570314128286** | **+3.31e-04** over the last three, monotone increasing |

> **REGISTERED: neither 0.2912 nor 0.2570 may be used as a converged reference value, cited
> as a validation target, or entered into any comparison table as "the published result".**
> **Neither is stationary to this lab's criterion** (§5.3, 1e-3 per CTU): the coarse trace
> is still moving at 8.64e-04 **per iteration** at its final iteration, and the fine trace
> is drifting monotonically upward at its own. **Our stationarity criterion governs, not
> theirs.** They are recorded as **the published author's terminal values at a stated
> iteration count**, which is what they are, and they may be plotted with that caption.

**Second reason they cannot be a reference, and it is independent of convergence.**
**[VERIFIED HERE]** the tree ships two mutually exclusive mesh routes (`run_mesh_shm.sh`
with snappyHexMesh, `run_mesh_fluent.sh` converting `mesh/mesh_coarse.msh`), and its
`README.TXT` recommends the second: *"Generating the mesh with SHM is time consuming so
better use the pre-generated mesh."* The shipped `log.solver` names no mesher and records
`Case : /home/joegi/OF_training/UNISA/COURSE/session2/Xdrivaer`, `Date : Apr 20 2022`,
`nProcs : 4`. **Which mesh produced the distributed `Cd` is not recoverable from the
tree.** A reference value whose mesh is unknown is not a reference value.

### 7.2 What this arm does NOT claim

No wall-resolved DES; no validation against TUM or AutoCFD experimental data (no
experimental file is in any retrieved tree); no grid-convergence statement (two levels is
not a Roache triple); no claim about the published author's result beyond quoting it as
his terminal value; and no claim that any published layer stack extruded — **no retrieved
tree ships a snappyHexMesh log** (`MESH_STANDARD.md` §17 draft, §17.2).

---

## 8. COST — rule 12, costed before the run

**Basis, MEASURED on this box:** `7.9268e-06` core-s per cell-iteration, from the
`DRIVAER-RATE-PROBE-96C` row of `docs/COST_CALIBRATION.md`
(row `C-20260913T003325.838106Z-f82829e5`; 150 iterations, 4 ranks, 186,709 cells, median
0.3700 wall s/iteration, prediction band [0.30, 0.75] HELD).

**THE BASIS IS FOR STEADY `simpleFoam`, AND THIS RUN IS NOT THAT.** Two honest problems:

1. **The transient/DES multiplier is RELAYED, NOT VERIFIED.** The instruction to this lane
   stated the probe under-predicts OpenFOAM HRLES by **2.3×**. **[NOT VERIFIED HERE]** — a
   search of `docs/COST_CALIBRATION.md` and `docs/LESSONS.md` found several unrelated 2.3×
   rows (D16 transonic cell-scaling, F27 numerics growth, A2 decomposition over-prediction)
   but **none that measures a DrivAer HRLES-over-steady factor.** It is applied here
   because the instruction was to set the prediction against the larger figure, and a
   conservative multiplier is the safe direction — **but it is recorded as relayed, and
   this row must not be cited as evidence for 2.3×.**
2. **A published cost basis is NOT AVAILABLE.** `occDrivAerRotMesh/README.md` gives a mesh
   generation time (238 M cells, 128 processors, ≈4 h) but **states no solve wall time**,
   so no published solve rate can be derived from it. Recorded rather than invented.

**Prediction, set against the larger figure as instructed:**

```
cells (T1f)  = NOT YET KNOWN — the mesh has not been built. Bounded by the dictionary's
               own maxGlobalCells 10,000,000. Working figure 4.05e6 (UNVERIFIED).
steps        = 7,689  (registered, Section 5.4)
steady-equiv = 4.05e6 x 7689 x 7.9268e-6 core-s = 4,114 core-min
x 2.3 relayed transient factor          -> 9,462 core-min  = 157.7 core-h
                                        -> $8.09 DERIVED, NOT MEASURED
T1c companion (186,709-cell class)      ->   436 core-min  = $0.37 DERIVED
TOTAL PREDICTION                        -> 9,898 core-min  = $8.46 DERIVED
```

`cost_basis`: **$0.0513/core-h, c7a.4xlarge, REPORTED-BY-OWNER, not measured** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**REGISTERED OBLIGATION: the cell count is a pre-mesh unknown and the prediction is
provisional on it.** When the mesh birth certificate fixes the true cell count, **this
figure is recomputed and the recomputation recorded as an addendum** — it cannot alter a
gate, threshold or label (rule 2).

**No cap is registered.** Sanaa's ruling of 2026-09-12 (directive #17): no run is stopped
by a time or budget cap. This figure exists for calibration under rule 12, **not as a stop**.

**Calibration obligation at completion (rule 12):** actual core-minutes from the logs
against this prediction, the ratio stated, the gap attributed, and waste named separately
and never absorbed into the ratio — as a row in `docs/COST_CALIBRATION.md`.

---

## 9. OPEN ITEMS FOR THE SUPERVISOR BEFORE FREEZING

1. **§1's two-tree architecture is a judgement and should be his, not this lane's.** The
   alternative is a transient arm with re-typed solver settings, which the copied-not-
   re-typed rule forbids. There is no third option in which one retrieved tree covers both.
2. **§6's resolution disclosure may be judged disqualifying.** A DDES closure on a
   wall-function mesh is a defensible transient arm and an indefensible DES claim. If he
   wants a DES claim, the mesh is the blocker and no retrieved tree supplies one — the
   published DES mesh is the 238 M-cell Zenodo download that is not on this box.
3. **The 2.3× multiplier in §8 needs his ruling** — it is relayed and this lane could not
   locate its record.
4. **Nothing is armed.** If, once he clears it, the runner or the classifier refuses the
   launch, the exact refusal is reported verbatim and not worked around.
