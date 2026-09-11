# The 52k "negative volumes" are a SPLICED MESH READ, proved from the mesh data

**Measured 2026-09-11 by the cfd lane. Zero compute.**

`checkMesh -constant` on
`DIAG_v3_coarse_explicitSnap_tol2_layersFixed` reported **52,333 negative volume
cells** and **max aspect ratio 2.78e+101**. Neither is a property of any mesh
`snappyHexMesh` built. Both are what you get when a face list is read against the
wrong point list.

## The proof, independent of any log string

A `faces` file indexes into a `points` file, so the highest index it uses says how
many points it was written against. Read directly out of
`DIAG_v3.../constant/polyMesh/`:

| quantity | value |
|---|---|
| `points` file supplies | **157,745** points |
| `faces` file contains | 410,969 faces |
| **max point index used by `faces`** | **156,506** |
| so `faces` were written against | **156,507** points |
| unused trailing points | **1,238** |

The topology in `constant/polyMesh/faces` needs 156,507 points. The coordinates in
`constant/polyMesh/points` are a **different, larger set of 157,745**. The two files
in that one directory do not belong to the same mesh.

## Three independent witnesses agree, and only one of them is a log line

1. **The index range**, above: faces require 156,507 points, the file holds 157,745.
2. **A second `polyMesh` in the same case.** `DIAG_v3.../0/polyMesh/points` exists
   and holds **156,507** points — exactly what the faces require. `A1` (below) has
   no `0/polyMesh` at all.
3. **`checkMesh`'s own arithmetic.** `log.checkMeshFull:78` reports
   *"Unused points found in the mesh, number unused by faces: 1238"*, and
   157,745 − 156,507 = **1,238**. The instrument measured the discrepancy and
   printed it, four lines before the numbers everyone believed.

## Which two meshes were spliced

**This attribution is corroborated, not independently proved by the index test
above.** The index test proves the *files disagree by 1,238 points*; naming *which*
two mesh states they came from reads `snappyHexMesh`'s own log:

    Snapped mesh : cells:128230  faces:412266  points:157745
    Layer mesh   : cells:128230  faces:410969  points:156507

`constant/polyMesh` holds the **snapped** point count (157,745) and the **layer**
face count (410,969). Every shared index therefore addresses a coordinate the layer
topology does not expect: correct connectivity, wrong positions. That is a complete
explanation for both the negative volumes and the 1e101 aspect ratio.

## The control: a case where layers ACTUALLY extruded

`LAYERFIX_A1_coarse_relativeSizes`, same geometry, same box, same binary, built
2026-09-11:

| | DIAG_v3 (0 % layers) | A1 (50.06 % layers) |
|---|---|---|
| `constant/polyMesh` points / faces | 157,745 / 410,969 — **mismatched** | 221,464 / 592,877 |
| matches snappy's final mesh line? | **no** | **yes, exactly** |
| `0/polyMesh` present | **yes**, 156,507 points | **no** |
| max aspect ratio | **2.78e+101** | **19.53 OK** |
| negative volume cells | **52,333** | **0** |
| `checkMesh` verdict | Failed 11 checks | Failed 3 checks |

So the splice is **not** a property of the geometry or of the tool in general. It
appears when the layer-addition phase **collapses to zero extrusion**: the final
mesh-motion step leaves the moved points in `0/polyMesh` while the topology stays in
`constant/polyMesh`. When layers actually extrude, one consistent mesh is written
and there is no `0/polyMesh`.

## What this retires

- **"52,165 negative volumes / 40.7 %" is not a mesh property and must not be
  carried as a defect.** It is a *symptom* of the zero-layer defect. There was only
  ever one defect.
- **The `mergeTolerance` refutation is void.** `1e-8` giving 52,248 against 52,165
  was measuring the size of an index mismatch, which jitters meaninglessly between
  builds. That experiment never tested point merging. The face-merging hypothesis
  dies the same way — both were fitted to an artifact.
- Any figure derived from these `checkMesh` reports on a zero-layer DrivAer build is
  void for the same reason, whether or not it looks reasonable.

## The rule this earns

**A physically impossible value is evidence about the INSTRUMENT, and it outranks
every plausible-looking value printed beside it.**

`2.78e+101` sat in the log from the first build. No mesh has that aspect ratio. It
should have invalidated the entire `checkMesh` report the first time it was seen.
Instead its neighbour `52,165` was believed for days **because it looked
reasonable** — and hypotheses were designed, run and refuted against it. The absurd
number was the honest one; the plausible number beside it was the liar.

