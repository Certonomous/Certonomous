# Act D ParaView frames

Produced by `cases/dafoam/actd_paraview_render.py` against the frozen
pre-registration `cases/dafoam/ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md`
v1.1. `render.json` is the record: every frame, its provenance, its `G-PV7a`
content grading, and `G-PV4` where a `checkMesh` reference exists.

## What is tracked here, and what is deliberately not

**Tracked: the five stills and `render.json`.** They are the evidence.

**NOT tracked: the 48 `wing_morph_*.png` frames (10 MB).** They are DERIVED and
deterministically regenerable from two things that ARE tracked — the stored
surfaces in `cases/dafoam/ladder-a/A2_shape_frames.json` and the render script —
and `render.json` records the grading of every one of them. `G-PV7c` measured a
re-render as bit-identical (0.000000 of pixels differing), so "regenerable" is a
measurement here rather than an assumption. Committing 10 MB of reproducible
output to make a point already made by its inputs is not filing, it is bulk.

Run outputs belong in `verification/runs/` and mostly not in git; tracking the
five stills is a deliberate exception so a reader can see what the pass produced
without a ParaView install.

## The frames

| frame | source | what it is |
|---|---|---|
| `section_grid` | AOAI `case/constant/polyMesh` | the 4,032-cell O-grid, all cells |
| `section_grid_leading_edge` | same | the leading-edge region |
| `polar_field_alpha18_not_converged` | AOAI `case/1000` | velocity magnitude at the angle the platform REFUSED |
| `wing_skin_mesh` | `A2_shape_frames.json` | the baseline wing skin, stored vertices |
| `wing_gradient_on_skin` | same, `gradient` | dC_D/dn, ±22.1 mm per unit step |

## Two things a reader should not over-read

**`polar_field_alpha18_not_converged` is a picture of a NON-CONVERGED state and
is labelled that way on purpose.** Its visible wake striping is the point: it is
what the solver produced at α = 18° before the platform declined to call it
physics. It is not a flow field anyone should read numbers off.

**The converged counterpart does not exist on disk.** The polar sweep re-solves
IN PLACE, so only the final angle's fields survive; the converged branch's were
overwritten. Rendering a neighbouring angle and labelling it converged would be
a fabricated provenance, so the gap is reported instead — in `render.json` under
`_not_rendered`, and here.
