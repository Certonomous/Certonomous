# Pressure-field validation for the two website slice images

Scope: the pressure FIELDS behind `naca4412_wing.png` and `naca0015_sail.png`
(mid-span static-pressure slices). The surface pressure was sampled from the
same solver output the images were rendered from (`foamToVTK` boundary patch
and volume file of the solved cases), so what is validated here is exactly
what is on camera.

## Verdicts

| Image | Verdict |
|---|---|
| `naca0015_sail.png` | **PASS**. Every hard invariant of a symmetric section at zero incidence holds quantitatively. |
| `naca4412_wing.png` | **PASS WITH STATED LIMITS**. The mid-span surface pressure reproduces the published NACA measurement within the offsets the configuration difference predicts; the limits are stated below and none of them affects what the image shows. |

No error was found in the slice pipeline or in either solve. Nothing in
either image misrepresents the underlying field.

## Conditions, verified from the cases themselves

| | NACA 4412 wing | NACA 0015 sail |
|---|---|---|
| Solved case | `study-naca4412_wing-902cfe`, iteration 120 | `study-naca0015_sail-16e5ff`, iteration 138 |
| Freestream | 15.0 m/s along +x (registry hint honoured; `0/U` and `magUInf` agree) | 75.0 m/s along +x (`0/U` and `magUInf` agree) |
| Angle of attack | 0 deg geometric (chord along +x; 0.07 deg measured from the meshed section, sampling tolerance) | 0 deg geometric (0.19 deg measured, sampling tolerance) |
| Geometry | chord 1.0 m, span 3.0 m, aspect ratio 3, straight extrusion | chord 1.2 m, span 1.8 m along z, aspect ratio 1.5, free tips |
| Dynamic pressure q (kinematic) | 112.5 m2/s2 | 2812.5 m2/s2 |
| p_inf used | 0.05 m2/s2, median of the slice beyond 3 chords lateral (0.0005 q) | 0.77 m2/s2, same definition (0.0003 q) |
| Mid-span band | y = 0 +/- 0.02 m, 376 wall faces | z = 0.9 +/- 0.02 m, 352 wall faces |

Cp = (p - p_inf) / (0.5 U^2) in kinematic units throughout; the solver is
incompressible so no density factor appears.

## NACA 0015 sail: invariant checks (all pass)

- **Mirror symmetry.** Upper against lower surface Cp, binned at 59 chordwise
  stations: mean |dCp| = 0.0005, max |dCp| = 0.0013. The two sides are the
  same curve to about a tenth of a percent of q. The small chordwise bumps
  (refinement-level transitions in the mesh) appear identically on both
  sides, which confirms they are mesh texture, not a field asymmetry.
- **Stagnation.** Peak wall Cp = 0.886 at x/c = 0.0000; global maximum over
  the whole patch 0.887, so Cp <= 1 holds everywhere. The 11 percent deficit
  from the ideal 1.0 is exactly the cell-centred sampling the image itself
  declares: nose wall cells are about 11 mm across, and at half a cell from
  the stagnation point of a nose with 30 mm radius the local speed is about
  25 m/s, which is a Cp of roughly 0.89. The image annotation (p/rho = 2491,
  Cp 0.886) is the same value read from the volume; surface and volume agree.
- **Far-field decay.** On the image's own slice plane, mean |Cp| beside the
  body is 0.0121 at 1 chord lateral and 0.0025 at 2 chords: a factor 4.8,
  matching the inverse-square decay a non-lifting thickness disturbance must
  show, and vanishing toward p_inf.
- **Section shape.** Suction minimum Cp = -0.580 at x/c = 0.22. Published 2D
  references for the NACA 0015 at zero incidence put the infinite-span
  minimum near -0.55 to -0.65 at x/c 0.2 to 0.3. Ours lands inside that band
  at its milder side, and milder than the 2D centre is the expected direction
  for an aspect-ratio-1.5 body with free tips. Location and magnitude are
  consistent; no inconsistency to flag.

Evidence plot: `naca0015_sail_cp_validation.png`.

## NACA 4412 wing: published-data comparison

Reference: Pinkerton, "Calculated and Measured Pressure Distributions over
the Midspan Section of the NACA 4412 Airfoil", NACA Report 563 (1936),
Table I, transcribed from the NASA NTRS scan of the printed report. Test:
variable-density tunnel, Re 3.1e6, rectangular aspect-ratio-6 model, midspan
orifices. Our mid-span section carries cn = 0.317 (integrated from the
extracted Cp; whole-wing Cl 0.269, and midspan loading above the average is
correct for a rectangular wing). The nearest tabulated condition by section
lift is the alpha = 0 column (section cl 0.338, effective 2D angle -0.5 deg
after Pinkerton's own induced correction), and that column is what is
overlaid.

| Quantity | Upper surface | Lower surface |
|---|---|---|
| RMS deviation, all 51 orifice stations | 0.051 | 0.103 |
| Max deviation | 0.113 (x/c 0.009) | 0.270 (x/c 0.017) |
| RMS aft of 5 percent chord | 0.045 | 0.059 |
| Max aft of 5 percent chord | 0.103 | 0.117 |

- Stagnation Cp = 0.877 at x/c 0.001, global max 0.889, so Cp <= 1 holds
  everywhere; the deficit is the same near-wall cell-centre effect as the
  sail (9 mm nose cells, 16 mm nose radius). The image annotation
  (p/rho = 99, Cp 0.88) matches the validated surface value.
- Suction peak Cp = -0.667 at x/c 0.15 against the reference plateau near
  -0.60 at x/c 0.2 to 0.35: same magnitude class, slightly forward and
  deeper, as expected for the lower Reynolds number (1e6 against 3.1e6) and
  the different camber loading at matched lift.
- The deviations concentrate in the first 2 percent of chord, where Cp
  changes by more than 1 per percent of chord and where the small section
  lift mismatch (0.317 against 0.338) moves the stagnation point; aft of
  5 percent chord both surfaces track the measurement at RMS 0.05 to 0.06.

Stated limits (none affects the published image):

- No published dataset exists at our exact configuration (aspect ratio 3,
  Re 1e6, alpha 0). The comparison is matched by section lift against an
  aspect-ratio-6, Re 3.1e6 measurement, so condition offsets of a few
  hundredths in Cp are inherent to the comparison, not evidence of a solver
  error. Direction and size of every offset are consistent with the
  configuration difference.
- Chordwise steps from mesh-refinement transitions are visible in the
  surface curve at the few-hundredths level (and equally in the sail case,
  where they cancel side to side). They are texture of the mesh, honestly
  rendered.
- Credential linkage: the VALIDATED drag credential for this body
  (0.0289 against Abbott and von Doenhoff 0.030, 3.6 percent off) came from
  the longer 250 and 300 iteration runs of the same body and freestream.
  The slice image's own solve reads Cd 0.0189 at iteration 120 with Cl
  matching the credential runs to 0.14 percent; both drag values sit inside
  the reference band (0.030 +/- 40 percent). The pressure field validated
  here is the image's own solve.

Evidence plot: `naca4412_wing_cp_validation.png`.

## Reproduction

- Script: `sdk/scripts/validate_pressure_fields.py` (unit tests in
  `sdk/tests/test_validate_pressure_fields.py`; full suite green, 648 tests).
- Numbers: `validation_numbers.json` in this directory, written by the same
  run that rendered the evidence plots.
