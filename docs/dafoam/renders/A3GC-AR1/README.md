# A3GC-AR1 — geometry and mesh render set

**Case id:** `A3GC-AR1` — ONERA M6 anchor rerun, transonic primal.
**Level:** single level, **c2 surface / pyHyp N = 65** (64 wall-normal cells).
**Not a member of the A3GC L3/L2/L1 triple** — those are 99,840 / 798,720 / 6,389,760
cells; this is **399,360**.

| record | sha |
|---|---|
| pre-registration, frozen before the run root existed | **`3d416043b`** |
| grading path, `a3gc_grade.py`, md5 | **`73dbe368934956700da87e5a1f44ea0c`** |
| grading record | `cases/dafoam/ladder-a/A3/curriculum_A3GC/A3GC_AR1_GRADING_RECORD.md` |
| verdict at render time | **`NOT A RESULT`** |

> **READ THIS BEFORE USING THE PICTURES.** The case is **complete and checked**, which is
> what Sanaa's directive #15 fires on, and these frames show **geometry and mesh only** —
> no field, no functional, no claim about the flow. The graded verdict is
> **`NOT A RESULT`**: `nuTilda` finished at 1.008860e-06 against a registered 1e-06 floor.
> CD and CL landed inside their registered ±2 % band (+0.032 % and +0.000 %) and that did
> not lift the verdict and could not have. Do not present any frame here as a passing
> result.

## Provenance of the pictures

Rendered by ParaView 5.13.3 (EGL, offscreen) **read-only on the graded tree**: the mesh
was copied to a scratch case and ParaView read only the copy. `constant/polyMesh` under
`/home/ubuntu/certonomous-runs/A3GC-AR1` was not written to, and no `.foam` marker file
was placed in it.

Scripts, committed beside the frames: `a3gc_ar1_render.py` (frames 01–04, 06) and
`a3gc_ar1_render_frame05.py` (frame 05).

ParaView reported, without being told what to expect: **6,240 wing quad faces** and
**399,360 volume cells** — both exactly the registered §2 values. From a slice of the
wing patch at η = 0.65 it gives local chord 0.57292, thickness 0.05600, **t/c = 0.0977**
against the ONERA D section's 0.10 (2.3 %), and linear taper predicts 0.5763 at that
station (0.6 %). `_station_geometry.json` carries those numbers.

## Frames

| file | what it shows |
|---|---|
| `01_AR1_wing_surface_planform.png` | the wing patch in planform — 6,240 quad faces |
| `02_AR1_wing_surface_mesh_oblique.png` | the same patch with its quad edges — the surface discretisation that ran |
| `03_AR1_wing_leadingedge_mesh.png` | leading-edge region, chordwise clustering on the c2 surface |
| `04_AR1_boundary_layer_mesh_eta065.png` | volume mesh on the η = 0.65 cut — **the 64 wall-normal layers that are the whole point of AR1** |
| `05_AR1_boundary_layer_zoom_LE.png` | wall-normal zoom at the local leading edge, same cut — `s0 = 1.0e-4`, constant growth `r = 1.1674` |
| `06_AR1_domain_extent.png` | the full domain, `marchDist = 12.0`, wing at true relative scale |

## The margin fix, measured

The existing M6 render set was reviewed and found to waste 35–45 % of frame on white
margin in five of ten stills. Two things were done about it and one of them is a
correction to my own first attempt:

1. **Camera fitted to the subject** — parallel projection, `CameraParallelScale` computed
   from the subject's on-screen half-extents in the camera frame and **read back after
   `Render()` to confirm the view actually took it** (it silently did not, the first
   time: the view's own reset had run afterwards and the frame came out at far-field
   scale).
2. **Trimmed to content** with a 14 px pad, which is what makes the fit robust for a thin
   high-aspect subject that cannot fill a 16:11 frame in both axes.

`_margin_audit.json` carries the per-frame audit. **Worst margin 7.0 %**, five of six
frames at or below 7.0 %, two at 0.0 %.

**Honest caveat on the comparison.** Measuring the *prior* set the same way
(non-white bounding box) gives it 1.7–18.9 %, not 35–45 % — so my metric is not the
reviewer's. By **ink fraction** the prior wing views sit at 7.4–24.8 %, which matches the
complaint much better, and the new subject frames sit at 38.8–100 %. I have not
reproduced the 35–45 % figure and am not going to claim I have.

## A correction worth keeping — the wing is swept

Frame 05's first two attempts were wrong and the reason generalises. A camera box built
on the **root** leading edge (`x ≈ 0`) sits in open air at η = 0.65, because the M6's
local leading edge there is at **x = 0.45649**. Attempt 1 rendered far-field triangles
with no aerofoil in frame; attempt 2, using a `Clip` whose `Invert` semantics returned
neither the station nor the local chord, rendered the frame *inside the solid wing*. The
fix is to take the station's chord from a **slice of the wing patch itself** — the
aerofoil contour — and never from the global patch bounds.
