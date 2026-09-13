# DRAFT for `docs/standards/MESH_STANDARD.md` — Section 11

**Status: DRAFT, handed to the cfd supervisor. NOT COMMITTED TO THE STANDARD.**
`docs/standards/MESH_STANDARD.md` is his territory; this lane drafts, he appends
and commits. To adopt: append §11 verbatim at the foot of that file under
standing rule 6, bump **v1.6 → v1.7**, and carry the assertion line. This draft
file is then superseded and may be deleted.

Every number below is cited. Numbers marked **[VERIFIED HERE]** were
re-derived or re-read by this lane in this session against the artifact named.
Numbers marked **[CITED]** are read from another lane's committed record and are
attributed to it rather than re-measured.

---

## 11. SNAPPYHEXMESH LAYER SPECIFICATION: ABSOLUTE IS THE DEFAULT (v1.7, 2026-09-13)

### 11.0 Why this section exists, and why no published source will ever supply it

Three public cases were taken to their published setups under Sanaa's
section-G rule in September 2026. **None of them uses snappyHexMesh:**

| Case | Published setup | Mesher | Can it express our failure? |
|---|---|---|---|
| DrivAer | Ashton, West, Lardeau & Revell (2016), *Computers & Fluids* 128:1-15 | **STAR-CCM+ v9.04** — prism layer is an independently extruded region with its own total thickness | **No** |
| PPTC VP1304 | Sikirica et al. (2019); smp'11 participants | **block-structured** — no octree, **no level-0 cell** | **No** |
| DrivAer | Ashton et al. (2024/2025), DrivAerML, arXiv:2408.11969v2 | OpenFOAM v2212 solver, meshed in **ANSA 24.1.0 HeXtreme** | **No** |

**Three for three. No published source is going to warn this lab about a
snappyHexMesh relative-thickness defect, because none of them has a relative
thickness to get wrong.** Retrieval cannot close this gap. A lab-side rule can.

This section is **house practice with its evidence attached**, at the maturity of
§7: **nothing here is written to `docs/physics_rules.yaml` and no code enforces
it yet.** It binds by being quoted, not by being checked, until §11.8 is built.

---

### 11.1 RULE L1 — ABSOLUTE SIZING IS THE DEFAULT. RELATIVE IS THE EXCEPTION.

> **`relativeSizes true` is REFUSED for any snappyHexMesh layer specification in
> this lab unless the background mesh's minimum level-0 edge has been MEASURED
> and DECLARED in the registration.**
>
> Absolute sizing (`relativeSizes false`, thicknesses in metres) is the default
> and needs no declaration. A relative specification without a declared,
> measured `level0Edge` is **not a layer specification**; it is a layer
> specification multiplied by an unknown.

**Declaration format** (goes in the pre-registration, beside the dictionary):

```
level0Edge_declared   = <value> m
level0Edge_source     = constant/polyMesh/level0Edge   (read from disk, not assumed)
level0Edge_expected   = <the base cell you intended> m
ratio_actual_expected = <expected/actual>          # MUST be 1.00 +- 0.01, or L1 refuses
smallest_feature      = <what sets the global minimum, and where it is>
```

If `ratio_actual_expected` is not 1, **the mesh does not mean what the dictionary
says** and the specification is converted to absolute before the run.

---

### 11.2 THE MECHANISM — why one small feature anywhere rescales layers everywhere

Under `relativeSizes true`, every layer thickness is a multiple of
`level0EdgeLength()`. **That function returns the GLOBAL MINIMUM level-0 edge in
the entire mesh**, and OpenFOAM's own source says so in its own comment.

**[VERIFIED HERE]** — read directly from this box's
`/usr/lib/openfoam/openfoam2606/src/dynamicMesh/polyTopoChange/polyTopoChange/hexRef8/hexRef8.C`
(OpenFOAM **api=2606, patch=0**, `META-INFO/api-info`):

| Line | Source text |
|---|---|
| **357** | `// Bit complex way to determine the unrefined edge length.` |
| **436** | `typEdgeLenSqr[eLevel] = min(typEdgeLenSqr[eLevel], edgeLenSqr);` |
| **441-442** | `// Get the minimum per level over all processors. Note minimum so if`<br>`// cells are not cubic we use the smallest edge side.` |
| **443** | `Pstream::listReduce(typEdgeLenSqr, minOp<scalar>());` |
| **505** | `// Find lowest level present` |
| **514** | `level0Size = Foam::sqrt(lenSqr)*(1<<levelI);` |

`min` at the edge, `minOp` across ranks, then the lowest level present scaled up
by `2^level`. **There is no averaging and no locality anywhere in that path.**
The single smallest level-0 edge in the mesh — wherever it is, however irrelevant
to the surface being layered — sets the scale for every relative thickness on
every patch.

**The measured case. [CITED]** — `verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:83-85`
and `cases/PPTC_VP1304/PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md:223-226`. On the
PPTC wedge the global minimum is the **azimuthal chord of the 2 mm axis rod**:

**[VERIFIED HERE]** the arithmetic reproduces exactly —
`2 · 0.002 · sin(pi/60) = 2.09343825e-04 m` (a 6-degree segment, 60 around the
circle), agreeing with `constant/polyMesh/level0Edge` to **eight significant
figures**, against an intended base cell of 0.020 m:

    0.020 / 2.09343825e-04 = 95.54

**Every relative layer thickness on that mesh was 95.5x too small**, and the rod
is not part of the propeller. **A 2 mm feature on the axis rescaled the layer
growth on the blades.**

---

### 11.3 RULE L2 — THE ONE-LOCAL-CELL RULE

> **A layer stack that asks for more than ONE local cell of total thickness is
> asking the mesher for room it does not have.** Compute the requested stack in
> local cells before the run and record it. Above 1.0, expect collapse; the
> registration must either reduce the stack or state why it expects the
> exception.

Stack in local cells, for `relativeSizes true` with `finalLayerThickness t_f`,
`expansionRatio r`, `nSurfaceLayers N`:

    S = t_f * sum_{i=0}^{N-1} r^(-i)          [multiply by the local cell to get metres]

and for `relativeSizes false`, divide the absolute `thickness` by the local cell
(base cell / 2^refinement level).

**Both sides of the rule are now measured.**

| | **DrivAerML (published, OpenFOAM)** | **Certonomous DrivAer** |
|---|---|---|
| Total stack | **12 mm** absolute | **42.0 mm** |
| Local surface cell | 25 mm (our level-4 equivalent) | **25.0 mm** |
| **STACK IN LOCAL CELLS** | **0.480** | **1.6808** |
| First layer | **0.75 mm** | **5.12 mm** |
| Layers requested | 7 | 5 |
| **Outcome** | **EXTRUDES** | **COLLAPSES — 2.50 of 5 (coarse), 2.89 of 5 (medium)** |

**[VERIFIED HERE]** all six of our values. Our stack:
`0.5 * sum(1.25^-i, i=0..4) = 0.5 * 3.3616 = 1.6808` local cells, from
`verification/runs/navier_class/DRIVAER/r2_medium/system/snappyHexMeshDict:194-197`
(`relativeSizes true; finalLayerThickness 0.5; expansionRatio 1.25;
minThickness 0.02`) with `nSurfaceLayers 5`. Local cell 25.0 mm = blockMesh base
0.400 m (`r2_medium/system/blockMeshDict`, hex `(30 50 30)` over a 12 m block)
divided by `2^4` at surface `level (4 4)`. Achieved coverage from
`verification/runs/navier_class/DRIVAER/LAYERS_ACHIEVED_MEASURED.json`
(post-extrusion, per L-590).
**[CITED]** DrivAerML from `cases/navier_class/DRIVAER/PUBLISHED_SETUP_INGEST_drivaerml_2024.md`
§3.2, quoting arXiv:2408.11969v2 sidecar L269-275.

**Why the failure is total rather than patchy: the margin is of order one.**
**[CITED]** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:56-70`. On PPTC the blade
prisms' collapsed side faces produced a pyramid volume
`w^2 t / 6 = 8.558e-14` against `minVol 1e-13` — **failing by 1.17x**, i.e.
**2.448 sub-`minVol` faces per blade prism cell** (`:65`). A defect whose margin
is 1.17x does not degrade gracefully; it takes the whole extrusion. **Do not
expect a too-thick stack to give you fewer layers. Expect it to give you none.**

---

### 11.4 RULE L3 — UNDER `relativeSizes true`, ACHIEVED THICKNESS IS A FUNCTION OF REFINEMENT LEVEL

> **The same relative dictionary produces different layers on different patches.**
> A relative specification is therefore not a specification of the boundary
> layer; it is a specification of a *ratio to whatever cell happens to be there*.
> **An absolute specification is uniform by construction.**

**[VERIFIED HERE]**, our own dictionary, same four numbers, two refinement levels:

| Patch refinement | Local cell | **Our stack** | **Our first layer** | DrivAerML absolute |
|---|---|---|---|---|
| `level (4 4)` | 25.0 mm | **42.0 mm** | **5.12 mm** | 12 mm / 0.75 mm |
| `level (5 5)` | 12.5 mm | **21.0 mm** | **2.56 mm** | 12 mm / 0.75 mm |

Our `BodyDoorhandles` and `BodyHeadlamps` sit at `level (5 5)` while
`BodyHood`, `BodyFender` and `BodyRear` sit at `level (4 4)`
(`r2_medium/system/snappyHexMeshDict:201-208`). **Under one dictionary those
patches get boundary layers differing by a factor of two, and nothing in the
dictionary says so.** Under DrivAerML's absolute recipe every patch gets
12 mm / 0.75 mm.

This is also why y+ cannot be reasoned about from a relative dictionary: y+ is
set by the first cell in metres, and a relative dictionary does not state one.

---

### 11.5 RULE L4 — `minThickness` CONVERTS IN THE SAME EDIT, OR THE MESH REFUSES EVERY LAYER

> **Converting `relativeSizes true` to `false` converts EVERY thickness field in
> the same edit, `minThickness` included.** A converted dictionary that leaves
> `minThickness` at its relative value is worse than the unconverted one: the
> floor is then read as metres and rejects every layer that was going to work.

**[CITED]** `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:120-129`, whose own
dictionary comment registers the trap in situ:

```
    relativeSizes   false;                      // was true
    minThickness        3.125e-5;               // m  (MUST convert: 0.05 absolute = 50 mm)
```

`minThickness 0.05` left unconverted is read as **0.05 m = 50 mm** — on a case
whose intended blade first layer is `3.125e-4 m`, a floor **160x** above the
layer it is meant to protect. **[VERIFIED HERE]:** the same trap is armed in our
DrivAer dictionary today — `minThickness 0.02` at
`r2_medium/system/snappyHexMeshDict:197` would become **20 mm** absolute against
a target first layer of 0.75 mm.

**[CITED]** `PRISM_A2:132-135` also records that per-patch `finalLayerThickness`
and `minThickness` are honoured under the global switch (`minThickness` is read
after the switch, outside the `thicknessModel` branch), so the conversion is
per-patch as well as global.

---

### 11.6 RULE L5 — READ THE POST-EXTRUSION TABLE. AN ABSENT TABLE MEANS ACHIEVED = 0, NEVER "UNKNOWN".

> **The per-patch layer table printed by snappyHexMesh before extrusion is the
> REQUEST. Coverage is read only from the POST-EXTRUSION table** (L-590).
> **And a run that extrudes nothing prints NO post-extrusion table at all** — so
> the absence of the table is a positive finding of zero, not missing data. A
> reader that reports "unknown" on an absent table will report the request table
> as the achievement.

**[VERIFIED HERE]** — the control flow, read from this box's
`/usr/lib/openfoam/openfoam2606/src/mesh/snappyHexMesh/snappyHexMeshDriver/snappyLayerDriver.C`:

| Line | Source text | Brace depth |
|---|---|---|
| **4958** | `for (label layeri = 0; layeri < layerParams.nOuterIter(); layeri++)` | loop opens, depth 1 |
| **5097** | `// Exit if nothing added` | |
| **5098** | `const label nTotalAdded = gSum(patchNLayers);` | |
| **5104** | `if (nTotalAdded == 0)` | |
| **5106** | **`break;`** | depth 3 |
| **5211** | **`printLayerData`** | **depth 3 — INSIDE the same loop** |
| **5369** | loop closes | |

**`printLayerData` at 5211 is inside the loop that the `break` at 5106 exits.**
If the first outer iteration adds zero layers, the break fires and
`printLayerData` is **never reached**. The log then contains the request table
and nothing else, and the request table looks authoritative.

**[VERIFIED HERE]** the empirical counterpart, from our own
`LAYERS_ACHIEVED_MEASURED.json`, case `DIAG_v5_coarse_layersON_mergeTol1e-8`:
`achieved_table_line: null`, `request_table_line: 3600`, `request_table_rows: 50`,
`extruding_faces: 0`, `added_cells: 0`, `cell_delta: 0`, `no_layer_exists: true`.
**Fifty request rows, zero achievement rows, zero layers.** L-590 is the lesson
that a parser reading the request column would have reported
"blades 6.00 of 6 nominal, coverage 100.0 %, SPECIFICATION MET".

**Required reader behaviour:** a layer reader must cross-check the request table
against **at least one independent extrusion witness** — `added_cells`,
`cell_delta`, or `extruding_faces` — and report **achieved = 0** when the
achievement table is absent. It must never emit "unknown".

---

### 11.7 THE COST OF THE FIX, STATED BECAUSE THE FIX IS NOT FREE

> **`relativeSizes false` on ANY ONE PATCH disables the warped-face extrusion
> check for the WHOLE MESH.** This is a real quality safeguard that absolute
> sizing gives up, and §11.1 requires it to be disclosed on the certificate, not
> discovered later.

**[VERIFIED HERE]**, `snappyLayerDriver.C` (v2606), read directly:

```
3785     // Disable extrusion on warped faces
3786     // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
3787     // It is hard to calculate some length scale if not in relative
3788     // mode so disable this check.
3789     if (!layerParams.relativeSizes().found(false))
3790     {
3792         const scalar edge0Len =
3793             meshRefiner_.meshCutter().level0EdgeLength();
3796         handleWarpedFaces
```

`relativeSizes()` is a `boolList`, so `found(false)` is **true as soon as one
patch is absolute**, and the guard fails mesh-wide. `handleWarpedFaces`
(defined `:817`) is the check that disables extrusion on faces too warped to
carry a layer; it is skipped entirely. **[CITED]** the same reading is the cfd
supervisor's ruling on W1 at `PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:6-8`.

Note the irony and record it: `handleWarpedFaces` itself consumes
`level0EdgeLength()` (`:3792-3793`), the same global minimum §11.2 indicts. **On a
mesh with a small stray feature the warped-face check was being fed a wrong
length scale anyway.** That is a reason to declare `level0Edge` under §11.1, not
a reason to keep relative sizing.

**Required disclosure** on any birth certificate for a mesh with an absolute
layer spec: `handleWarpedFaces: DISABLED (relativeSizes false on >=1 patch,
snappyLayerDriver.C:3789)` plus the checkMesh face-warpage metrics, so the reader
knows which safeguard was traded for which.

---

### 11.8 THE CHECKLIST — what a registration must carry before a layered snappy run

1. `relativeSizes` stated. If `true`: the §11.1 declaration block, with
   `level0Edge` **read from `constant/polyMesh/level0Edge`**, not assumed.
2. **Requested stack in local cells**, computed per §11.3 and printed. `> 1.0`
   requires a stated exception.
3. **First layer in METRES**, per patch refinement level, for every distinct
   level in the layer spec (§11.4).
4. `minThickness` in the same units as the rest of the spec, checked against the
   first layer it must not exceed (§11.5).
5. The layer reader's **planted control**: plant a known coverage, read it back
   from the post-extrusion table, refuse if unseen (standing rule 3).
6. Post-run: achieved coverage from the **post-extrusion** table; **absent table
   recorded as achieved = 0** (§11.6).
7. If absolute: the **`handleWarpedFaces: DISABLED`** disclosure (§11.7).

**Nothing here is enforced by code yet.** Building the check into the birth
certificate (§6) is the natural next step and is not done; until then this is a
reviewer's checklist, and a registration that omits an item is incomplete rather
than refused.

---

### 11.9 SCOPE, AND WHAT THIS SECTION DOES NOT CLAIM

- Binds **snappyHexMesh layer specifications** only. Silent on block-structured,
  ANSA, STAR-CCM+ or any other mesher — §11.0 is precisely the observation that
  those cannot express this failure.
- **Not retroactive.** No frozen ladder is re-opened, no closed verdict moves, no
  existing gate value in §3 changes. It governs **how the next layer spec is
  written**, not what any past one was.
- **Changes no gate in `docs/physics_rules.yaml`** and adds no enforced
  threshold. The one-local-cell rule of §11.2 is a **design rule with two
  measured points** (0.480 extrudes, 1.6808 collapses), not a calibrated
  threshold — the lab has not bracketed where between them the transition sits,
  and this section does not pretend otherwise.
- The 1.17x `minVol` margin and the 95.5x `level0Edge` factor are **[CITED]** from
  the PPTC lane's frozen record, not re-measured here. The arithmetic
  `2*0.002*sin(pi/60) = 2.09343825e-04` and `0.020/2.09343825e-04 = 95.54` **was**
  re-derived here and reproduces.

### 11.10 Sources

| Source | Used for |
|---|---|
| `/usr/lib/openfoam/openfoam2606/.../hexRef8/hexRef8.C:357,436,441-443,505,514` | §11.2, the global-minimum mechanism |
| `/usr/lib/openfoam/openfoam2606/.../snappyLayerDriver.C:817,3785-3796,4958,5097-5107,5211,5369` | §11.6 control flow, §11.7 warped-face guard |
| OpenFOAM `META-INFO/api-info` — `api=2606, patch=0` | the version all line numbers refer to |
| `verification/runs/navier_class/DRIVAER/r2_medium/system/snappyHexMeshDict:194-197,201-208` | §11.3, §11.4, §11.5 our values |
| `verification/runs/navier_class/DRIVAER/r2_medium/system/blockMeshDict` | §11.3 base cell 0.400 m |
| `verification/runs/navier_class/DRIVAER/LAYERS_ACHIEVED_MEASURED.json` | §11.3 achieved 2.50/2.89, §11.6 absent-table case |
| `cases/navier_class/DRIVAER/PUBLISHED_SETUP_INGEST_drivaerml_2024.md` §3.2 | §11.3 DrivAerML 12 mm / 0.75 mm / 7 layers |
| `cases/navier_class/DRIVAER/PUBLISHED_SETUP_INGEST_ashton_2016.md` | §11.0 STAR-CCM+ row |
| `cases/PPTC_VP1304/PUBLISHED_SETUP_INGEST_SIKIRICA_2019.md:223-226` | §11.2 level0Edge diagnosis |
| `verification/campaign/PPTC_PRISM_A2_PREREGISTRATION_DRAFT.md:6-8,56-70,83-85,120-135` | §11.2, §11.3 minVol, §11.5 minThickness, §11.7 W1 ruling |
| `docs/LESSONS.md` L-590 | §11.6, request vs achievement |

---

**Appended at the foot under standing rule 6. Version 1.6 → 1.7. Lines whose
number changed above this section: 0.** Nothing above §11 is edited, and no gate
value anywhere in this standard moves.
