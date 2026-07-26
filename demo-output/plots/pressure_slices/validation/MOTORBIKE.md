# Motorbike surface-pressure field: triple-check before it stays on camera

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
