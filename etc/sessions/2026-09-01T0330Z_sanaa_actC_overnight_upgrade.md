# SANAA-DIRECT — Act C upgrade, overnight, hard priority (2026-09-01, ~03:30Z)

## Sanaa's words, verbatim

> [SANAA-DIRECT] Act C upgrade, overnight, hard priority for heat-transfer:
>
> Configuration: the registered real module, not the feasibility one. Cooling
> channels resolved as a fluid region (air, meshed, inlet velocity and
> temperature imposed, outlet pressure), coupled to the cells at every
> channel face; true transient conjugate. Downstream cells must be able to
> run hotter than upstream ones.
> Loads: replace the representative per-cell loss with a realistic
> aviation-cell takeoff level so the rise is tens of kelvin, not tenths.
> State the assumed loss and the basis (C-rate class) in the assumptions box.
> Pulse 60 s, then cruise, 900 s total.
> Mesh: per the case spec, not 960 cells: wall layers on both channel faces,
> cells across each channel, two mesh levels; two time steps on the finer
> mesh for the step-independence panel.
> Checks that ship with it: T20 exact gate cited as the machinery proof;
> cumulative energy conservation over 900 s; step-independence from the two
> time steps; mesh-independence from the two levels; planted-perturbation
> reader checks as tonight.
> Outputs: temperature fields at t = 0, 30, 60, 120, 300, 900 s; all-8-cell
> histories with the pulse shaded; spread vs time; coolant outlet temperature
> vs time (now defined); per-cell table: peak, time of peak, temperature at
> end of pulse, time to settle. Figures and text per the language rule.
> Cap: 600 core-min; the box is free. If the resolved-channel case is not
> converged and graded by 08:00Z, report exactly where it stands and keep the
> 0.4 K run off screen. Do not present a partially converged transient as
> complete.
