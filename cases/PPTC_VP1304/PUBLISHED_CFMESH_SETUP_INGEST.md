# PUBLISHED cfMesh SETUP — INGEST RECORD FOR PPTC VP1304 RUNG CFM-1

Retrieved 2026-09-13 by a cfd lane under Sanaa's published-setup rule
(`docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md` §G). Her operative words:

> "For any public case, the lab starts from a published OpenFOAM setup of that case — mesh
> recipe, layer settings, schemes, wall treatment — ingested into the knowledge base before
> the first registration. Inventing a setup for a case someone has already run in this solver
> is refused."

and her ruling on intent: numerics and domain practice may come from any finite-volume
source; **the mesher recipe must come from an OpenFOAM source.**

**This record exists because no cfMesh recipe was in the knowledge base.** Both places named
in the standing brief were checked first and neither held one:
`/home/ubuntu/upstream/published-openfoam-setups/` carried three trees (HPC-TC, Wolf Dynamics
DrivAer, Alletto OneraM6), all snappyHexMesh; `docs/PUBLISHED_OPENFOAM_CASE_FILES_POINTER.md`
lists the same three and no fourth.

---

## 1. WHAT IS ON THE BOX ALREADY, AND WHY IT WAS NOT USED AS THE BASE

`cartesianMesh` is installed **natively**, not in a container:

| artifact | sha256 |
|---|---|
| `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/cartesianMesh` | `2290d5339163c1b7a66a2d97d2d42b3c466e69d9c548977b5f1582fea42ed3b4` |
| `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/lib/libmeshLibrary.so` | `fcb0efa642421cf39c5c5049e7cbb9c846d97b7c88443f2df3b07ec439e7bc4a` |

The OpenFOAM **v2606 installation itself ships cfMesh `meshDict` files**: 22 of them under
`tutorials/incompressible/adjointOptimisationFoam/topologyOptimisation/monoFluidAero/`, and
all 22 are the **same file**, sha256
`2257b3c00df53e984dec3ef9a341749d2262d66661ebbfb28a701cb7ea7a3097`. That is a published
OpenFOAM source and it is recorded here as corroboration that cfMesh dictionaries ship with
the binary.

**It was not used as the base.** It is an internal-duct topology-optimisation re-evaluation
case: `maxCellSize`, `boundaryCellSize`, `boundaryCellSizeRefinementThickness`, and a
`patchBoundaryLayers` entry carrying only `nLayers` and `thicknessRatio`. It contains no
external-body pattern, no per-patch surface refinement, no `optimiseLayer`, and no feature
handling. Building the PPTC recipe on it would have meant inventing everything that matters.

## 2. THE BASE THAT WAS INGESTED

**cfMesh's own tutorial tree**, from the OpenFOAM Community integration repository.

| field | value |
|---|---|
| URL | `https://develop.openfoam.com/Community/integration-cfmesh.git` |
| Retrieved (UTC) | 2026-09-13 22:53 |
| Clone commit | `3ff8555514827646c34cacfe5f0f691e49cdbc96`, dated Wed 18 Dec 2024 15:43:51 +0000, subject "COMP: scatter v.s. broadcast" |
| Local tree | `/home/ubuntu/upstream/published-openfoam-setups/integration-cfmesh` (outside the repository) |
| Per-file manifest | `/home/ubuntu/upstream/published-openfoam-setups/SHA256SUMS.integration-cfmesh.txt`, **676 files** |

Access note, and nothing was sent: `develop.openfoam.com` refuses plain HTTPS GET with 403
but serves **git** normally. The repository was cloned; no page was scraped, no account was
created, nothing was posted.

### 2.1 The dictionary the PPTC recipe is built on

| file | sha256 |
|---|---|
| `tutorials/cartesianMesh/ship5415Octree/system/meshDict` | `d09a3c61163025b80b294a8cd9826fec3b19bc1e566357713e62271b166277f2` |
| `tutorials/cartesianMesh/ship5415Octree/Allrun` | `b55a10ffbe0ca3f860e9ac4f10738e469806ce8a0e9c0e2a069cf0f14c0f61c2` |

**Why this one of the nine `cartesianMesh` tutorials.** `ship5415Octree` is the only external
naval-hydrodynamics case in the tree: a hull plus a domain box in one closed surface,
`surfaceFeatureEdges` into a `.ftr` feature file, per-body `surfaceMeshRefinement` with
`additionalRefinementLevels` and `refinementThickness`, and a boundary-layer block carrying
`nLayers`, `thicknessRatio`, `optimiseLayer 1` and a full `optimisationParameters` set. That
is the whole shape a propeller in open water needs. `asmoOctree` and `sawOctree` carry no
layers at all; `bunnyOctree` carries none; `elbow_90degree`, `multipleOrifices`,
`singleOrifice` and `sBendOctree` are internal-duct cases.

**Both files are COPIED, NOT RE-TYPED**, into
`cases/PPTC_VP1304/mesh/cfmesh/meshDict.ship5415Octree.PUBLISHED` and
`cases/PPTC_VP1304/mesh/cfmesh/Allrun.ship5415Octree.PUBLISHED`, and both copies re-hash to
the values above.

### 2.2 Two keywords taken from other shipped cfMesh tutorials

| keyword | shipped tutorials it is taken from | sha256 of the one cited |
|---|---|---|
| `maxFirstLayerThickness` | `multipleOrifices`, `singleOrifice`, `elbow_90degree` | `multipleOrifices/system/meshDict` = `0bc02a568a74ff2b83e4c2d6aa647fac69a5b45e0b7be3fddb85cfb91671045d` |
| `renameBoundary` | `elbow_90degree`, `multipleOrifices`, `singleOrifice` | same file |

### 2.3 The user guide, title-page verified (CLAUDE.md rule 15)

`userGuide/User Guide - cfMesh v1.1.pdf`, sha256
`4e1d0f7eb7cf7e8eb85eba6dffdc9e99116bfec95cc95840186e61e6ae9edb4c`. Its title page reads:
*"cfMesh v1.1 / User Guide / Document version: 1.1 / Principal developer and document author:
Dr. Franjo Juretić, M. Eng., Assist. Prof. / Managing Director and Founding Partner /
Creative Fields, Ltd. / Zagreb, May 2015"*. Verified by reading the page, not by filename.

---

## 3. TWO FACTS READ OUT OF THE PUBLISHED SOURCE THAT CHANGE WHAT CAN BE REGISTERED

**3.1 cfMesh prints no layer-achievement table.** Every per-face layer report in
`meshLibrary/utilities/boundaryLayers/refineBoundaryLayers/refineBoundaryLayersFunctions.C`
sits inside `# ifdef DEBUGLayer` (`:302-304`, `:333-337`), and the library's own per-face
count `nLayersAtBndFace_` (`:308-340`) is written to no artifact. cfMesh's
`detectBoundaryLayers` class does carry a per-boundary-face layer index — `layerAtBndFace_`,
`detectBoundaryLayers.H` — but it is an internal class with no utility exposing it.
**Layer achievement on a cfMesh mesh is obtainable only by post-processing the produced
mesh.** Rung CFM-1 therefore registers its own reader as the instrument.

**3.2 In cfMesh the TOTAL layer thickness is not a user parameter.**
`refineBoundaryLayersFunctions.C:684-697` computes the first sub-layer height from the hair
edge that spans the single extruded near-wall cell:

```
const scalar magv = mag(v);                              // :684  the hair edge length
scalar firstThickness = magv/nLayersAtEdge[seI];         // :688
if (thicknessRatio[seI] > (1. + SMALL))
    firstThickness = magv / ((1 - pow(ratio, n))/(1 - ratio));   // :691-696
firstThickness = min(max(firstLayerThickness[seI], SMALL), firstThickness);  // :709-714
```

`nLayers` and `thicknessRatio` **subdivide** a thickness the octree has already fixed, and
`maxFirstLayerThickness` is a **cap** — `min(...)` — which can only make the first layer
thinner, never thicker. The consequence for the registered §6.3 specification is computed in
the rung's pre-registration §5 and it is a predicted `GATE FAIL`, registered before the run.
