# Mid-span pressure-slice regeneration (2026-07-27)

Scope: the four published mid-span pressure-slice PNGs under
`demo-output/plots/pressure_slices/` (`motorBike.png`, `b52.png`,
`naca0015_sail.png`, `naca4412_wing.png`). This is the volume-slice product
rendered by `render_pressure_slice()` / `extract_pressure_slice()` in
`sdk/chief_engineer/field_render.py`, which reads cell-centred `p` directly
from each case's own `foamToVTK` `internal.vtu`. It is **not** the same
product as the normalized 0-1 surface-paint `*_field.json` files served to
the GUI; those are unaffected by this pass.

## Why regeneration was needed

The four PNGs on disk before this pass were stamped 2026-07-25 20:15-22:59
UTC. The cell-centred-pressure fix (commit 47fffd3) was authored
2026-07-26 04:12 UTC, so the published images predated it.

## The two "impossible" blockers, and what was actually true

1. **"foamToVTK not available."** False. `openfoam2606 -c "which foamToVTK"`
   resolves it at `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/foamToVTK`.
   Every OpenFOAM utility must go through the `openfoam2606` prefix; a bare
   PATH lookup failing is expected and does not mean the tool is missing.
2. **"Case data missing / solved remotely."** False. The mesh and the
   solved fields for each case live in two separate, still-present caches on
   this machine and pair by cell count:

   | Body | mesh-cache key | nCells | solve-cache key | time |
   |---|---|---|---|---|
   | motorBike | `motorBike` | 353688 | `motorBike-c353688-i300` | 300 |
   | b52 | `b52` | 193880 | `b52-c193880-i300` | 300 |
   | naca0015_sail | `naca0015_sail` | 243929 | `naca0015_sail-c243929-i300` | 138 |
   | naca4412_wing | `naca4412_wing` | 337334 | `naca4412_wing-c337334-i300` | 120 |

   A runnable case was reassembled per body in a scratch directory
   (`constant/polyMesh` from the mesh cache, the solved time directory from
   the solve cache, a minimal `system/` sufficient for `foamToVTK`), without
   writing into either cache. `foamToVTK -latestTime` was then run through
   the `openfoam2606` prefix (capped to 2 CPU cores via `taskset -c 0,1`) to
   produce `internal.vtu`, which `render_pressure_slice()` consumed directly.

## Two additional bugs found and fixed in the regeneration script itself

`sdk/scripts/regenerate_pressure_slices.py` (written by an earlier, failed
attempt at this same repair and never actually executed) had two copy-paste
defects in its `BODIES` config, caught by comparing the freshly regenerated
b52 image against the git-committed one (`git show HEAD:...b52.png`):

1. `body_label` said "B-52 fuselage at **20 m/s**". The case's own
   `system/controlDict` force block (`magUInf 100`, `dragDir (-0 -0 1)`) and
   `b52_validation_numbers.json` (`u_inf: 100.0`) both say **100 m/s**.
   Fixed to "B-52 fuselage at 100 m/s".
2. `span_axis`/`plane_axes` were copied from the motorBike entry
   (`span_axis=1, plane_axes=(0,2)`), which cuts the B-52 at a single x
   station and shows an unrecognizable sliver, not the fuselage. The B-52's
   flow axis is z (`dragDir (-0 -0 1)`), so the sensible mid-span cut is at
   mid-x (`span_axis=0, plane_axes=(2,1)`) — confirmed by matching the
   `git`-recovered original b52.png exactly (same slice station `x = 55.61
   m`, same stagnation value `p/rho = 3,591`, same recognizable aircraft
   silhouette with tail fin). Fixed in the checked-in script.

motorBike, naca0015_sail and naca4412_wing had no such bug; their
regenerated images match the git-recovered originals' framing and stagnation
values exactly.

## Finding: the slice pipeline itself had no defect to fix

The three stacked rendering defects the corrected pipeline addresses
(decimation-correspondence, cell-centred pressure reading,
`over_bound`/`cp_bound_report` disclosure) all live in the **surface-paint**
path (`_patch_cell_values`, `_package_painted`, `cp_bound_report` inside
`extract_and_paint`), which produces the `*_field.json` files, not in
`render_pressure_slice()`/`read_volume_field()`, which already read
undecimated cell-centred volume values before and after commit 47fffd3.
Confirmed empirically: the stagnation-peak annotation baked into each
git-recovered pre-existing PNG (198, 3591 after the b52 axis fix above, 2491,
99 m2/s2) is pixel-identical to the freshly regenerated one. The visible
change in the regenerated images is the crisper cross-section (this repair
reassembled cases from the post-remesh, lower-skewness mesh cache the
published validation refers to; the motorBike remesh, for example, improved
max skewness 8.94 to 3.99) plus the two b52 label/axis corrections above.
Regeneration was still necessary and correct to do: the images on disk
before this pass were never actually produced from this reassembled,
post-remesh case, so their provenance could not be certified, and the b52
one (once run through the broken script above) would have been wrong.

## Numbers

See `slice_regeneration_numbers.json` in this directory for the full
machine-readable record (title, annotation, note text, colorbar label, Cp
peak/min in the displayed view and over the full slice slab, cell counts,
mtime). Independent cross-checks against the wall-boundary survey:

- motorBike: slice Cp_max (view) 0.9918 == wall survey's
  `cp_max_outside_gap` 0.9918013680027797 exactly (`MOTORBIKE.md`). The
  wall-survey raw maximum 1.1192 (single brake-gap sliver face, 427/44032
  gap faces, 0.0023% of faces) is **not** carried forward as a slice or body
  peak; it is a separate, already-documented open item
  (`MOTORBIKE_Cp_anomaly_investigation.md`) and this mid-span slice plane
  (y = -0.01 m) does not intersect that off-centre gap in any case.
- b52: slice Cp_max/min (view) 0.7182 / -0.4559; independently recomputed
  wall-boundary Cp_max/min from the same freshly-extracted `body.vtp`:
  0.718153 / -1.048201, matching `B52.md`'s corrected wall numbers to 6
  figures.
- naca0015_sail, naca4412_wing: `validate_pressure_fields.py` re-run against
  the freshly-extracted `body.vtp` + `internal.vtu` reproduces
  `stagnation_cp` (0.8856 / 0.8766), `cp_min`/`cp_min_upper` (-0.5795 /
  -0.6670), and every RMS/reference-comparison figure in `VALIDATION.md`
  exactly.

## Verdicts on the regenerated images

All four: Cp_max <= 1.0 (no stagnation-bound violation in the plotted
mid-span slice), "Red high, blue low" stated in the on-image note, colorbar
units (`p/rho`, m2/s2) match the plotted field, and the captioned body
matches the body shown (confirmed visually, see PASS notes above for the
b52 fix). PASS for all four.
