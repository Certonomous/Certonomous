# T18_CU_f demo assets -- 3-D transient conduction

**Case:** `verification/runs/T-family/T18_runs/T18_CU_f`
**Mesh:** 512,000 cells, 80 x 80 x 80, hexahedral
**Solver:** `laplacianFoam`, transient, `deltaT` 1e-4, `endTime` 2 s
**Verdict:** graded rows **G1, G2, G3: `PASS`**. Rung ceiling: **`GATE REACHED`**.

Every figure in this directory carries that verdict burnt into the image. A
figure without its verdict word is not shippable, and the stamp guard refuses
one.

## Why this directory exists

Every rendered demo asset the lab owned before it was Act A, and Act A is a
**five-degree axisymmetric wedge**. T18_CU_f is one of exactly two genuinely
three-dimensional solved cases whose verdict permits it to be shown as a
verified result, and it had no rendered asset at all.

## THE DECLARATION THAT IS NOT OPTIONAL

**The solved domain is an OCTANT, not a cube.** The mesh spans `0..L` in each
direction with `L = 0.01 m`, carrying **zero-gradient symmetry planes at
x = 0, y = 0, z = 0** and **convective Robin faces at x = L, y = L, z = L**
(`build_t18.py` lines 4-6; `T18_registered.json` `/physics/L_half_side_m`).

The body it represents is a cube of side `2L` with six Robin faces. **The solve
has three Robin faces and three symmetry planes.** Anything describing this case
as "a cube with six Robin faces" is describing the physical problem, not the
computation.

That distinction is this case's version of Act A's wedge, and it is handled the
same way Act A handles it -- with two declarations, one per kind of picture:

| Declaration | Goes on |
|---|---|
| `Octant as solved ; symmetry at x=0 y=0 z=0 ; Robin faces at x=L y=L z=L` | every view of the octant as solved |
| `Octant solved ; mirrored to the full cube of side 2L ; display only` | `T18_full_cube_mirrored` only |

Mirroring is permitted. **Silent mirroring is not.** Stamping the as-solved line
on the mirrored figure would be false in the opposite direction -- it would deny
a display choice that was made.

## What is NOT claimed

T18 is graded against an **exact analytic series** (`exact_t18.py`, 80 terms),
not against an experiment. So:

* this is **not validation**, and nothing here may say so;
* the rung ceiling is `GATE REACHED` and never higher -- the reference being
  exact is precisely why the rung scores V and never P
  (`T18_registered.json` `/ceiling`);
* there is no "excellent agreement" anywhere. The deviation is a number with a
  pre-registered band beside it, and both are in `T18_graded_rows.csv`.

The stamp guard refuses all three of those phrasings mechanically.

## The files

| File | What it is |
|---|---|
| `T18_temperature_field_Fo0.1/0.2.png/.pdf` | corner-cutaway octant coloured by theta; the front through the solid |
| `T18_isosurfaces_Fo0.1/0.2.png/.pdf` | nested theta shells; the cooling front marching inward |
| `T18_front_march.png/.pdf` | the two isosurface panels side by side at identical contour levels |
| `T18_mesh.png/.pdf` | the hexahedral mesh, corner octant removed. **The "it is not a wedge" figure** |
| `T18_full_cube_mirrored.png/.pdf` | the octant mirrored into the full cube, display only |
| `T18_graded_rows.png/.pdf` + `.csv` | G1/G2/G3: value, reference, band, triple, order, GCI, verdict |
| `T18_centreline_profile.png/.pdf` + `.csv` | solved profile against the analytic series, cube centre to Robin face, with residuals |

Every plotted number has its CSV beside it, as Act A does.

## Reading the physics

theta = (T - T_inf) / (T0 - T_inf), so theta = 1 is the initial state and
theta = 0 is the ambient. Bi = 1, Fo = alpha t / L^2, and the two rendered times
are Fo = 0.1 (t = 1 s) and Fo = 0.2 (t = 2 s).

The cold front enters through the three Robin faces; the surviving hot core hugs
the symmetry corner at the origin, which is the **centre of the full cube**. In
`T18_front_march` the theta = 0.35 shell exists only in the Fo = 0.2 panel --
at Fo = 0.1 the coldest cell in the octant is still theta = 0.386, so that shell
has not formed. **Its absence on the left is the field, not a plotting choice.**

## Regenerating

```
xvfb-run -a pvpython docs/campaigns/T-family/demo/render_T18_paraview/render_t18.py
python3           docs/campaigns/T-family/demo/render_T18_paraview/make_t18_tables.py
```

The renders read the graded tree through a scratch case of symlinks, write
nothing into it, and prove it unchanged afterwards. **No solver is run.**

## What the renderers refuse

Named here because each one is a defect that actually occurred while these
figures were being made, and each is now a refusal rather than a habit:

1. **a stamp carrying a verdict word this case does not own** -- checked before
   any compute;
2. **a corner cutaway that did not cut.** ParaView's Box clip takes `Position`
   as the box minimum corner and `Invert = 1` keeps the inside; both were
   assumed backwards, and the mesh figure shipped an **uncut cube** under a
   caption reading "corner removed to show the interior". The kept-cell count is
   now asserted;
3. **a figure drawn at the wrong time.** `UpdatePipeline` without an explicit
   `time` resolves to the pipeline's first timestep, so the figure captioned
   Fo = 0.2 was built from the Fo = 0.1 field. The only outward sign was two
   supposedly different PNGs coming out three bytes apart. The peak theta is now
   checked against `exact_t18.Series` for the captioned Fo;
4. **a reflection that did not reflect** -- three reflections must multiply the
   cell count by eight, and that is asserted before the mirrored caption is used;
5. **a framing set by something other than this code.** A fresh view's first
   `Render` performs an automatic reset that overwrites `CameraParallelScale`; a
   requested 1.4850 came back as 2.2102. The scale is now re-applied after that
   render and asserted;
6. **an empty, tiny or stale image**, and a caption glyph the font drops.

## DIMENSIONALITY EVIDENCE — read from the mesh that exists, not from any dict

Recorded 2026-09-10 by a heat-transfer `lab-lane` at the supervisor's standing
instruction, after the closure team offered three "genuinely 3-D" families that
were all one cell thick. **Dimensionality is never inferred from a cell count
and never read from `blockMeshDict`** — a commented-out line in a dict is what
misled that check. The three readings below come from the built mesh.

**1. `log.checkMesh`, verbatim, at every level:**

| Level | `log.checkMesh` line |
|---|---|
| `T18_CU_c` | `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` |
| `T18_CU_m` | `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` |
| `T18_CU_f` | `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` |
| `T18_CU_f_CT` | `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` |

**2. Patch types in `constant/polyMesh/boundary`, counted by type:** every level
carries **6 `patch`** and **zero `empty`**, **zero `wedge`**. An `empty` or
`wedge` patch would disqualify the 3-D claim outright.

**3. The cell-count ratio between grid levels** — an independent check that
needs no log at all. 8,000 → 64,000 → 512,000 is **8.00x then 8.00x** at
r = 2. A 3-D mesh at r = 2 gives 2^3 = 8x; a 2-D mesh gives 2^2 = 4x. The
measured ratios are the 3-D signature.

**Verdict on "is genuinely 3-D": PASS.** Three independent readings agree.

## THE GRADED TREE CARRIES A POST-GRADING WRITE, AND IT WAS NOT THIS PIPELINE

`verification/runs/T-family/T18_runs/T18_CU_f/VTK/` (14 files, 82.6 MB, the
largest `internal.vtu` at 78,284,103 B) was written **2026-09-10 17:46 UTC**,
inside the graded case directory, long after grading on 2026-08-31 15:11 UTC.
It is `foamToVTK` output at time index 20000, which is `endTime` = 2 s.

Three things are established about it, and each is a measurement, not a reading
of intent:

1. **No graded field moved.** Every file under `T18_CU_f` outside `VTK/` still
   carries its solve-time mtime: `0/T` at 2026-08-30 23:57, the `1/` and `2/`
   fields at 2026-08-31 00:19 and 00:43. The age guard compares `endTime`
   fields against `0/T` and is unaffected.
2. **Rule 4 still discharges today.** `mark_done_t18.py --root .` was re-run on
   2026-09-10 and returned rc 0, `DONE` on all four levels, with its
   `--selftest` planted-control arm passing first (every clause shown able to
   fire).
3. **This render pipeline did not write it.** `scripts/demo3d_render_common.py`
   and both render scripts contain no `foamToVTK`, no `SaveData` and no `.vtu`
   write; they materialise a scratch case of symlinks. The writer is unidentified
   and the directory has been **left in place, not deleted** — an unexpected
   change is inspected, never reverted.

The `assert_run_tree_untouched` guard is sound for what it claims and no more:
it proves the tree did not change **during a render**. A write that precedes its
`before` snapshot is outside its reach, which is exactly what happened here.
