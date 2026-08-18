# Motorbike surface-pressure field: triple-check before it stays on camera

> **CORRECTED 2026-07-26.** This check missed a reporting defect that was
> inside its own scope. The original text below is kept intact; the section
> **"Correction: the reported range was the colour clip"** at the end of this
> document states what was wrong, what the corrected numbers are, and what
> still stands. Read that section before quoting any range from this page.

Scope: the painted motorbike surface pressure served to the GUI
(`mission-output/geometry-study/motorBike_field.json`) and the pressure the
website slice was rendered from. Everything below is read from the solved
cases' own `foamToVTK` output — the boundary patches and the volume file the
paint and the slice consumed — not from any intermediate artifact.

The trigger: the owner reports the motorbike's pressures "look much different
than what we had before". Two things changed underneath the picture since the
round-2 screenshot she is comparing against
(`demo-output/acts/round2/motorbike/03-cp-painted.png`, 2026-07-23, "19,144
faces", Cd 0.4156, 353,578 cells, skew 8.94). This check separates them and
sizes each.

## Verdict

**PASS WITH EXPLANATION.** The field on camera is the solver's own field,
served byte-for-byte, and every physics invariant holds — with one stated
exception: a single wall face out of 44,032, inside the millimetre channel
between the front brake disc and the fork, reads Cp 1.119, above the
stagnation bound. It is 0.0023% of the faces and 0.00052% of the wetted area,
it is a sliver-cell artifact in a nearly closed gap, and no face anywhere
else on the body exceeds Cp 0.992. Nothing else fails, and nothing in the
picture misrepresents the field.

**The look change is a rendering fix, not a physics change.** Of the change
Katie is seeing, essentially all of the pattern change and 98.1% of the
colour-window change come from the painted-surface pipeline fix; the remesh
moved the physics by RMS Cp 0.0043.

## Conditions, read off the case itself

| | Value | Source |
|---|---|---|
| Freestream | 20 m/s along +x | `postProcessing/forceCoeffs1/0/coefficient.dat` header (`magUInf 20`, `dragDir (1 0 0)`), `0.orig/include/initialConditions` |
| q (kinematic) | 200 m2/s2 | 0.5 U^2; incompressible, so p is p/rho throughout |
| lRef | 1.42 m | same header |
| Old case | `study-motorBike-a7b3bf` | 353,578 cells, max skew 8.94, Cd 0.4156 (mean of final 60 iterations) |
| New case | `study-motorBike-54767f` | 353,688 cells, max skew 3.99457, Cd 0.4201 (same window) |
| Geometry | identical | `motorBike.obj` unchanged; only the mesh was rebuilt under the boundary-skewness gate |
| Wall survey | 44,032 boundary faces, 11.24 m2 wetted | the display pipeline's own patch selection (`_body_patches`), so the survey covers exactly the painted surface |

## 1. Physics invariants (pass, one stated exception)

- **p_inf.** 0.0140 m2/s2, the median cell pressure beyond 3 body lengths
  in-plane radius on the published slice's own mid-span slab (42,741 slab
  cells, 4,090 in the far annulus). That is 7e-5 of q — the reference is
  effectively zero, as it must be.
- **Stagnation bound.** p_inf + U^2/2 = 200.01 m2/s2. Max wall p/rho outside
  the brake-disc gap = 198.37, Cp 0.9918 <= 1. Exactly one face in the whole
  body exceeds the bound: p/rho 223.85 (Cp 1.119) at
  (-0.108, -0.060, 0.337) m, inside the front brake-disc/fork channel, area
  5.84e-5 m2 = 5.2e-6 of the wetted area. The gap box holds 427 faces; only
  this one breaches. Cause: the channel is closed to about a millimetre and
  the local cells are slivers, so the cell-centred wall value picks up a
  pressure overshoot the mesh cannot resolve. It is invisible at any display
  scale (0.0005% of the painted area) and it does not touch the force
  integration by any measurable amount.
- **Stagnation sits on forward-facing surfaces.** Of the top 0.5% of wall
  pressure (221 faces, threshold Cp 0.764), 99.5% have a patch normal with a
  positive flow-axis component (mean 0.834, median 0.912 — near face-on).
  Their location: 36.7% front fairing/forks, 34.4% front wheel, 10.9% brake
  gap, 9.5% helmet/screen, 6.3% torso/tank, 2.3% elsewhere. That is the front
  of a motorcycle, which is where stagnation belongs.
- **Suction sits on acceleration zones.** The bottom 0.5% (threshold
  Cp -1.231) is 50.7% on the rider's helmet and screen, 16.7% front wheel,
  13.6% brake gap, 8.1% torso/tank. Their normals are near-tangent to the
  flow: median |n.x| = 0.168, mean flow-axis component 0.070, against 0.834
  for the stagnation set. Crowns and shoulders, not front faces.
- **Far-field decay.** Mean |Cp| on upstream/lateral spherical shells above
  the ground boundary layer: 0.0648 at 1 L, 0.0101 at 2 L, 0.0046 at 3 L
  (7,762 / 573 / 124 cells). Monotone decay toward p_inf, a factor 6.4 from
  1 L to 2 L.

## 2. Old vs new, split into physics and rendering

Both attributions are measured against the surviving pre-remesh case, not
asserted.

### Physics (the remesh): negligible

The pre-remesh case was re-surveyed identically and both fields were reduced
to area-weighted mean surface Cp in 41 streamwise bins:

| | Value |
|---|---|
| RMS dCp over the 41 shared bins | **0.0043** |
| Max |dCp| | 0.0103, at x = 1.68 m (the wake-facing tail of the body) |
| Area-weighted Cp percentiles, new | -0.713 / -0.249 / -0.156 / -0.040 / 0.467 (2/25/50/75/98) |
| Area-weighted Cp percentiles, old | -0.718 / -0.250 / -0.154 / -0.043 / 0.459 |
| Colour-window shift attributable to the remesh | **0.56% of the window span** |
| Cd | 0.4156 -> 0.4201, +1.08% |

The two Cp profiles lie on top of each other at plot resolution. A change of
0.0043 in Cp against a display window 1.22 q wide is roughly a third of one
percent of the colour range: not visible.

### Rendering (the decimation-correspondence fix): this is the change

The motorbike is decimated for display — 101,137 merged source triangles
collapse to 19,110 display faces, above the 30,000 threshold. Before commit
`b203327` (2026-07-25 14:26 -0400) `_attach_field` computed
`stride = total // triangles_total`, which is always 1, then took the FIRST
19,110 source values and laid them on 19,110 decimated faces that have no
relationship to them. The colour window then came from that same truncated
subset.

That pipeline was reproduced faithfully (same stride arithmetic as commit
`7608e28`) on the old case and scored by how much neighbouring display faces
agree — the signature of a physical field:

| Paint | Neighbour-face correlation r |
|---|---|
| Current pipeline, current case | **0.892** |
| Current pipeline, old (pre-remesh) case | 0.892 |
| Pre-fix pipeline reproduced | **0.422** |
| Same values randomly permuted (floor) | -0.001 |

26,553 shared-edge pairs. The pre-fix paint was roughly halfway between a
physical field and noise, which is exactly the salt-and-pepper speckle
visible in the round-2 screenshot and reproduced in panel B of the evidence
figure.

The colour window moved the same way:

| Window (m2/s2) | Low | High |
|---|---|---|
| Pre-fix pipeline (truncated subset) | -84.18 | 85.70 |
| Fixed pipeline, same old case | -153.87 | 87.24 |
| Fixed pipeline, current case | -155.23 | 88.34 |

The lower bound moved by 69.69 from the rendering fix and by a further 1.36
from the remesh: **98.1% of the window change is rendering, 1.9% is physics.**
The suction end of the scale had been clipped away by the truncation, which
is why the old picture read washed-out blue and the new one shows real
suction on the helmet, screen and wheel.

The third candidate was checked and cleared: the 2nd/98th percentile colour
clipping is **not** new. The identical index arithmetic is present in
`_attach_field` at `7608e28` (2026-07-23), before the round-2 screenshot.

Face count moved from 19,144 (round-2 screenshot caption) to 19,110 — 0.18%,
the decimation of a very slightly different source mesh.

## 3. Display integrity

- The motorbike **is** decimated, so the byte-identical guarantee does not
  apply and aggregation had to be verified instead. The served JSON was
  recomputed from the case: 19,110 values, identical `triangles_shown`,
  identical window, **max value difference 0.0**. What the browser fetches is
  what the solver produced.
- Aggregation is verified the way the sail's was: neighbouring display faces
  correlate at r = 0.892 over 26,553 shared-edge pairs, against a permutation
  floor of -0.001. The decimated paint carries a smooth physical field, not
  an index scramble.
- The GUI's orphan-island display filter leaves this body alone: the painted
  motorbike is a single connected component under the filter's own
  position-quantized union-find, so no faces are dropped.

## Reproduction

- Script: `sdk/scripts/validate_motorbike_pressure.py`
  (`--staging <dir with new/ and old/> --served-json
  mission-output/geometry-study/motorBike_field.json --out-dir <here>`).
  Unit tests: `sdk/tests/test_validate_motorbike_pressure.py`.
- Numbers: `motorbike_validation_numbers.json` in this directory, written by
  the same run that rendered the evidence figure.
- Evidence figure: `motorBike_cp_validation.png`.

## Correction: the reported range was the colour clip

*Added 2026-07-26. Nothing above is deleted. This section records one defect
this check did not catch, the corrected numbers, and which of the original
findings survive unchanged.*

### What was wrong

Section 2 of this document measured the "colour window" and reported it as
`[-155.23, 88.34]` m2/s2, and section 3 confirmed the served JSON carried the
"identical window". Both statements are true. What was never asked is
whether that window was also being written into the served JSON as the
field's `min` and `max`, that is, as the physical extremes of the solved
field. It was.

`_attach_field` in `sdk/chief_engineer/field_render.py` clipped the painted
values to the 2nd and 98th percentile, which is a legitimate colour-mapping
device that keeps one stagnation spike from flattening the body to a single
hue, and then wrote those two clipped numbers out under the keys `min` and
`max`. Any consumer reading `field["max"]` to state a peak pressure got the
98th percentile of the display faces instead of the peak.

Two stages compounded before the clip even ran, and both were also being
allowed to set the reported physics:

1. **Nodal interpolation.** `_read_patch` prefers the per-point pressure
   array and averages it to face centres, because that is what makes the
   painted surface look smooth. Every node of a peak face is shared with
   cooler neighbours, so the peak is shaved before anything else happens. On
   this body the solver's own wall maximum is p/rho 223.85 and the
   nodal-averaged version of the same patch reads 195.18.
2. **Vertex-clustering decimation.** The motorbike is decimated (101,137
   source triangles to 19,110 display faces, as section 2 already states), and
   each display face carries the mean of the source faces that merged into
   it. That is correct for display and wrong for reporting an extreme.

### Corrected numbers

Re-measured 2026-07-26 from the same solved case in the run cache
(`~/certonomous-runs/.solve-cache/motorBike-c353688-i300/300`, mesh
`~/certonomous-runs/.mesh-cache/motorBike/polyMesh`), 67 body patches,
44,032 wall cells, q = 200 m2/s2. The 44,032 wall-cell count and the 0.5%
suction threshold of Cp -1.231 both reproduce this document's own section 1
exactly, so this is the same survey, read at a different stage.

| Stage | p/rho low | p/rho high | Cp low | Cp high |
|---|---|---|---|---|
| Solver's own wall cells (the physics) | -824.34 | 223.85 | **-4.1218** | **+1.1192** |
| Nodal-averaged per face (display input) | -540.84 | 195.18 | -2.7043 | +0.9758 |
| **Reported before the fix** (2/98 clip of display faces) | -155.23 | 88.34 | **-0.7762** | **+0.4416** |
| **Reported after the fix** (solver wall cells) | -824.34 | 223.85 | **-4.1218** | **+1.1192** |
| Colour window after the fix (unchanged, now labelled as such) | -155.2 | 88.3 | -0.7761 | +0.4414 |

The reported high moved from Cp 0.4416 to Cp 1.1192, a factor of 2.5. The
reported low moved from Cp -0.7762 to Cp -4.1218, a factor of 5.3.

Cp here is `(p - p_inf) / q` with the p_inf of 0.0140 m2/s2 that section 1
measured, which is why these differ in the fourth decimal from a bare `p/q`.

**Plainly stated: the gap between the raw wall Cp and the displayed and
published Cp was this reporting defect, not mesh resolution alone.** This
document's section 1 had already measured the true wall extremes correctly
and stated them (Cp 1.119 in the brake-disc gap, 0.992 elsewhere); the defect
was that the number the JSON published under `max` was a different, much
smaller number, and nobody compared the two.

### What the two reported extremes actually are

Both are real faces, both were already identified in section 1, and neither
has been excluded or softened, because the reported number must equal what
the solver computed:

- **Cp +1.1192**, p/rho 223.85, is the single face in the front
  brake-disc/fork channel that section 1 already flagged as exceeding the
  stagnation bound: 1 face in 44,032, a sliver cell in a gap closed to about
  a millimetre. It is now the reported maximum, and it should be, because it
  is the largest value the solver wrote on this wall. The physically
  meaningful stagnation peak elsewhere on the body remains Cp 0.992, as
  section 1 states.
- **Cp -4.1218**, p/rho -824.34, sits on `motorBike_fr-wh-tyre%37`. It is
  likewise an outlier of the same character: 43 of 44,032 faces (0.098%) read
  below Cp -2, and the 0.5% suction threshold is Cp -1.231.

Consumers that want a robust peak rather than a true extreme should read
`color_min`/`color_max`, which is exactly what those keys are for, and must
label them as the display range.

### The bound flag: this body fails the Cp = 1 check, and says so

Cp cannot exceed 1 at a stagnation point in incompressible flow. That is a
hard physical bound, not a convention, so a field labelled as the physical
range that carries Cp 1.1192 would put an impossible number in front of a
viewer. The value is not changed and not excluded, because it is what the
solver wrote. Instead the served JSON now carries a disclosure beside it, in
`field["cp"]`:

| Key | Motorbike value |
|---|---|
| `q_kinematic`, `p_inf` | 200, 0.0140 |
| `faces` | 44,032 |
| `min`, `max` | -4.1218, +1.1192 |
| `stagnation_bound` | 1.0 |
| **`within_stagnation_bound`** | **false** |
| `over_bound.count`, `.fraction` | 1, 2.27e-05 (**0.0023%**) |
| `over_bound.max_cp_within_bound` | **+0.9935** |
| `suction_outliers.count`, `.fraction` | 43, 0.0977% below Cp -2 |
| `caveat` | ready-to-display sentence, quoted below |

The 0.0023% reproduces this document's own section 1 figure for the same
face exactly, which confirms the flag is counting the population section 1
described.

`max_cp_within_bound` is Cp 0.9935, while section 1 reports Cp 0.9918 as the
maximum "outside the brake-disc gap". These are two different exclusions and
both are correct: section 1 excluded the whole 427-face gap box, whereas the
flag excludes only the faces that actually break the bound, so it keeps the
admissible gap faces and lands slightly higher.

There is deliberately **no** lower-bound violation test. Cp has no hard lower
bound (incompressible potential flow over a cylinder already reaches -3), so
the 43 faces below Cp -2 are recorded as `suction_outliers`, with a note
saying in the JSON itself that this is a mesh-degeneracy signal rather than a
violation. Reporting Cp -4.1218 as "out of bounds" would be its own false
physics claim.

The `caveat` string is written to be displayed verbatim:

> Reported physical maximum Cp 1.119 exceeds the incompressible stagnation
> bound of 1 on 1 of 44032 wall faces (0.002%). Values above the bound are
> degenerate sliver cells, a mesh quality defect, not a physical pressure.
> The highest bound-respecting value on this body is Cp 0.993. Present either
> the robust colour window with this disclosed, or the raw extreme with this
> caveat attached.

That gives a consumer the means to take either honest route without having to
re-derive anything. `extract_and_paint` also emits the same finding as a log
warning, so a bound-violating wall value does not depend on somebody opening
the JSON to be noticed.

**Mesh quality signal.** A wall Cp above 1 is evidence of degenerate cells,
and this body has them in the front brake-disc channel and on the front tyre
while still passing the boundary-skewness gate that was applied when it was
remeshed (max skew 3.99). That is worth carrying to whoever is looking at
mesh quality gating: the gate did not catch these faces.

### The fix

`sdk/chief_engineer/field_render.py` now reports two clearly distinct ranges:

- `min`/`max`: the physical range, read from the solver's own `CellData` wall
  values before any interpolation, clustering or clipping.
- `color_min`/`color_max` (with `display_min`/`display_max` kept as aliases
  for the existing GUI legend): the 2nd/98th percentile colour window, a
  display device only.
- `cp`: the stagnation-bound disclosure described above, present whenever the
  case's q is known.

The GUI legend in `sdk/chief_engineer/control_room.html` now tags the colour
bar as the colour range, prints the physical range beside it, and shows the
bound warning when one is present. `sdk/tests/test_field_render.py` pins the
invariant.

### What still stands, unchanged

- Every physics invariant in section 1. Those were read from the solver's own
  wall values and are unaffected.
- The whole of section 2's old-versus-new attribution: RMS dCp 0.0043 from
  the remesh, neighbour-face correlation 0.892 against a pre-fix 0.422, and
  98.1% of the colour-window change being the earlier decimation-
  correspondence fix. Those are statements about the colour window and about
  the paint's spatial correspondence, and both remain correct.
- Section 3's served-JSON integrity result. The served values were, and are,
  the solver's own values. The defect was in the two summary numbers
  alongside them, not in the per-face data.

### Regenerated artifact

`regenerated/motorBike_field.json` in this directory, produced by the fixed
pipeline from the cached solve. The provenance copy at
`mission-output/geometry-study/motorBike_field.json` is deliberately left
untouched; it will pick up the corrected keys the next time the geometry
study runs.
