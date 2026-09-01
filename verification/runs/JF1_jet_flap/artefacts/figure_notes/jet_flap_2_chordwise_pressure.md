# Chordwise pressure

Pressure around the wing, drawn to full scale with nothing cut off the axis. Same wing, same grid and same flow speed in all five curves. The four blown curves differ from one another only in the strength of the trailing-edge jet, so that comparison is controlled; the fifth is the reference case, with the slot closed. Suction is plotted upward, the usual aerodynamic convention, and the area enclosed between the upper and lower curves is the lift. The lower row magnifies the first 7.5 % of the chord, where every curve reaches Cp = +1, the point at which the oncoming air is brought to rest. With the slot closed that point sits on the nose; the stronger the jet, the further back along the lower surface it moves.

The stagnation pressure comes out between +1.0015 and +1.0057 rather than exactly +1. The overshoot is 0.15 % to 0.57 % and is a resolution effect: pressure is sampled at the centre of each surface cell, not at the exact stagnation point. The strong peaks at the trailing edge are the slot lip; they are real features of the calculation and they set the scale of the top row, which is why the mid-chord detail looks flatter here than it would on a chart with a cropped axis.

None of these calculations reached the convergence target fixed before they ran, which was all five solution channels below 1e-06. The turbulence-energy channel is the slowest everywhere and worsens with blowing, from 3.5e-06 with no jet to 1.5e-04 at the strongest jet, a factor of 43. Mesh sensitivity has not been quantified: no refinement study was run, so no uncertainty is claimed on any pressure value, and the one uncertainty in the table is on where the stagnation point sits, which is half the local surface-cell spacing. No experimental pressure data exists for this configuration, so no measured reference curve is drawn. Treat these as indicative.

Measured values behind this chart. All quantities are dimensionless and every curve is 396 surface samples.

| jet strength | stagnation pressure Cp | its location x/c | location uncertainty | on which surface | strongest suction, x/c < 0.98: Cp | at x/c | lowest Cp on the surface |
|---|---|---|---|---|---|---|---|
| slot closed | +1.0057 | 0.00000 | ±0.00000 | lower | -0.406 | 0.118 | -0.406 |
| 0.05 | +1.0049 | 0.00085 | ±0.00014 | lower | -0.729 | 0.037 | -1.258 |
| 0.10 | +1.0046 | 0.00148 | ±0.00022 | lower | -0.912 | 0.027 | -2.236 |
| 0.20 | +1.0027 | 0.00248 | ±0.00034 | lower | -1.223 | 0.020 | -3.916 |
| 0.40 | +1.0015 | 0.00502 | ±0.00061 | lower | -1.777 | 0.011 | -6.873 |
