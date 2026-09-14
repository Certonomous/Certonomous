# Geometry ingest — a loadable file for every act

**Date:** 2026-09-14 · **Tool:** `scripts/geometry_ingest.py` ·
**Collection:** `docs/campaigns/_geometry/<ACT>/`

Sanaa, 2026-09-14 ~04:05Z, verbatim: *"ok now for all the runs, i need tobe able
to load a real stl file. or even better a cad file then stl"*, then
*"all the acts"*, then *"no need fot eh control room ( i am building this my
self). I just want the stl files or cad files"*, then *"yes no control room, i
just need all the stl files (crm adjoint, data center (K2),driaver, M6) or even
better cad files and when we have them lmk and ill push to the repo"*.

So: no control-room endpoint and no loader panel — those two deliverables were
withdrawn mid-task and were **not built**. What is here is the ingest tool and
one folder per act holding the binary STL the run loads, its JSON sidecar, a
512 px preview, and the original CAD where one exists on this box.

---

## 1. What each act loads

Every number below is read back out of the `*.ingest.json` sidecar beside the
STL it describes. Nothing is retyped from a terminal.

| Act | STL the run loads | Original CAD | In | Units | Bounding box (m) | Triangles | Watertight | Shells |
|---|---|---|---|---|---|---|---|---|
| CRM wing (D6R3 MP_R2) | `docs/campaigns/_geometry/CRM_WING/crm_wing_mach085_MP_R2.stl` | none on this box | stl (ascii) | m (--units flag); none | [-5.041e-06, 0, -0.2029] .. [3.247, 3.767, 0.3461] | 22,272 | no (136 open / 0 nm) | 1 |
| K2 rack row (K2h) | `docs/campaigns/_geometry/K2H/k2h_rack_row_L3.stl` | none on this box | stl (ascii) | m (--units flag); none | [0, 0, 0] .. [3.6, 3.5, 2.7] | 123,768 | yes | 1 |
| K2 rack row (K2h) | `docs/campaigns/_geometry/K2H/k2h_racks_only_L3.stl` | none on this box | stl (ascii) | m (--units flag); none | [0.6, 0, 0] .. [3, 3.5, 2.7] | 29,160 | no (540 open / 0 nm) | 3 |
| DrivAer | `docs/campaigns/_geometry/DRIVAER/drivaer_wolfdynamics_fine.stl` | none on this box | stl (ascii) | m (heuristic); none | [-0.8078, -0.0004, -0.0287] .. [3.805, 1.004, 1.39] | 448,833 | no (0 open / 656 nm) | 5 |
| ONERA M6 (M6J) | `docs/campaigns/_geometry/M6J/onera_m6_wing_L3.stl` | none on this box | stl (ascii) | m (--units flag); none | [-4.441e-16, 0, -0.04596] .. [1.415, 1.501, 0.04596] | 936 | no (24 open / 0 nm) | 1 |

| Act | Conversion tool | Seconds | Binary STL bytes | Source of the geometry |
|---|---|---|---|---|
| CRM wing (D6R3 MP_R2) | geometry_ingest | 0.084 | 1,113,684 | wall patch `wing` extracted from the D6R3 MP_R2 DAFoam mesh |
| K2 rack row (K2h) | geometry_ingest | 0.484 | 6,188,484 | wall patches extracted from the K2h_L3 mesh (`surfaceMeshExtract`) |
| K2 rack row (K2h) | geometry_ingest | 0.102 | 1,458,084 | wall patches extracted from the K2h_L3 mesh (`surfaceMeshExtract`) |
| DrivAer | geometry_ingest | 1.564 | 22,441,734 | Wolf Dynamics published setup, `drivaer_fine/constant/triSurface` |
| ONERA M6 (M6J) | geometry_ingest | 0.004 | 46,884 | wall patch `wing` extracted from the M6J_L3 mesh (`surfaceMeshExtract`) |

Each folder also carries `<name>.ingest.json` (source sha256, units, bbox,
triangle count, watertightness, shells, degenerate triangles, conversion tool
and time) and `<name>.preview.png` (512 px, headless).

**Two K2h surfaces on purpose.** `k2h_rack_row_L3.stl` is the whole enclosure —
racks, perforated tile, return and the room walls — and is closed, so it is the
one a snappyHexMesh case can use unmodified. `k2h_racks_only_L3.stl` drops the
outer walls so the rack bodies are actually visible and can be dropped into a
differently-sized room; it is open along the floor line, which is correct for
what it is.

---

## 2. What CAD this box can convert today

**Today, STEP and IGES convert — through gmsh, and only through gmsh.** The
probe order the brief fixed is gmsh (python module, then CLI), FreeCAD,
cadquery/OCP, and the measured state of the box is: the gmsh **python module is
not installed**, but `/usr/bin/gmsh` is version 4.12.1 built against
**OpenCASCADE 7.6.3**, which is the kernel that reads STEP AP203/AP214 and IGES.
FreeCAD (`freecadcmd`) is
absent, and neither `cadquery` nor `OCP` imports. **Nothing was pip installed**:
the tool runs on numpy alone, with scipy, matplotlib, trimesh and pyvista each
optional and each carrying a fallback (connected components fall back to
vectorised pointer-jumping, the preview is simply omitted if matplotlib is gone,
and the trimesh cross-check reports `null` rather than being required). What
would need an install: **Parasolid (`.x_t`), SolidWorks (`.sldprt`), CATIA
(`.CATPart`) and Creo (`.prt`)** are not readable by any tool here and would
need either a vendor kernel or a FreeCAD/OCP install; `pip install gmsh` into
the lab venv would add in-process control of the same OCC kernel already present
on the CLI (finer deflection control, per-face tolerances) but would not extend
the *format* list. The only CAD on this box at all is the PPTC set — searched
box-wide for `.step/.stp/.iges/.igs`, every other hit was a SystemTap script
inside the bundled ParaView python.

---

## 3. How the tool decides things, and what it refuses

- **Format detection is structural, not textual.** A binary STL whose 80-byte
  header begins with the word `solid` is a real and common file; the reader
  trusts the header's triangle count only when `84 + 50 n` accounts for the file
  exactly, and falls through to the ascii parser otherwise.
- **Watertight** is an edge-manifold test on welded vertices: every non-collapsed
  edge must be used exactly twice. Boundary edges (used once) and non-manifold
  edges (used more than twice) are both reported, because they fail a mesh in
  different ways. For a `--consumer snappy` case a non-watertight surface is
  **refused outright** and the refusal reason is written into the JSON —
  `--allow-open` is required to override it. Every act here was ingested with
  `--allow-open` deliberately: an extracted wall patch is *supposed* to be open
  at the symmetry plane, and refusing it would have been wrong. The gate was
  exercised on its own during development and fires correctly.
- **Units are never silently corrected.** The heuristic reads the bounding-box
  diagonal (< 100 → metres, > 1000 → millimetres, in between → `ambiguous` and
  the caller is told to pass `--units`), and rescaling happens only on
  `--convert-to-m` or `--scale`. Both the detected and the assumed unit, and
  which of the two won, are in every sidecar.
- **Multi-part bodies keep their provenance.** DrivAer is body + two wheel sets,
  SUBOFF is hull + sail + four stern planes, MB13 is tip + three stems. `--extra`
  merges them into one STL and records each constituent's own sha256 and
  triangle count under `merged_parts`.

## 4. What is not verified here

The bounding boxes are the **mesh's or the file's own coordinates**. This record
does not check them against published reference dimensions — for example the
ONERA M6 wall patch measures 1.501 m in span, where the classical M6 reference
semi-span is 1.1963 m, and nothing here establishes which of the two the M6J
campaign intended. That comparison belongs to each act's own registration
document, not to an ingest record, and is flagged rather than guessed.
`normals_outward` is reported only for closed surfaces, where the signed volume
means something.

---

*Tool: `scripts/geometry_ingest.py` (CLI and importable: `from geometry_ingest
import ingest`). `--probe` prints this box's CAD converter state;
`--list <CASE>` prints every sidecar already written for a case.*
