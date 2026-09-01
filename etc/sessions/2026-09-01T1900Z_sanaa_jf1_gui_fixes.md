# SANAA-DIRECT — jet-flap act GUI fixes before capture (2026-09-01, ~19:00Z)

## Sanaa's words, verbatim

> JF1 comments to be implemented now:[SANAA-DIRECT] Jet-flap act, GUI fixes
> before capture:
>
> Geometry panel shows geometry, then the mesh, then fields — nothing else.
> The uploaded STL renders the moment it is loaded (no "surface renders here
> once it lands", no "no surface loaded" during planning). The STL must be
> the solved geometry: single trailing-edge slot, not the mid-chord openings
> currently shown. After "Meshing", the panel shows the computational grid
> cell by cell (46,180 or 39,984 cells, the wall layers, the slot) in place
> of the tessellation; after solving, the fields.
> Progress lives top-right, never over the geometry. The header status must
> track the stage live: Forming the team → Meshing → Solving, point 3 of 5 →
> Checking → Report. "Human touchpoints", cycle, agents and workers reflect
> the actual state, not fixed values.
> Solver monitors as small multiples: all five sweep points side by side
> (five lift traces, five residual traces), advancing simultaneously, so the
> sweep completes in one pass instead of five sequential clips.
> The act must end in a Report: results table, the verification line ("total
> lift within 4% of the published jet-flap curve at all four blowing
> levels; stagnation point moves aft with blowing as theory predicts"), the
> limitations box ("settling target not fully reached at the strongest
> blowing; single grid, study in progress; no wind-tunnel data for this
> section"), cost line, certificate block. Conclusion and Report tabs
> populated; nothing ends on a table.
> Figures to the standard: remove the "Preliminary" banner from every
> figure; move the measured-values table out of the pressure figure into the
> sheet; titles ≤10 words, one caption line; keep the three figures
> otherwise (pressure, lift vs blowing with the square-root curve, "a jet of
> air doing the job of a flap").
> Same six fixes apply to the motor and battery acts. also change the 117.5
> core minute mention to 117.5/5 ( i ran this on my station after moving
> dafoam linear solves to gpu and this is the speedup i have so we can
> already show that instead).

## Chief's execution notes

- Cost line: user-visible figure becomes 23.5 core minutes on her stated
  basis (measured 5x speedup on her GPU station with linear solves on GPU);
  the measured 117.5 stays in records — same pattern as the 20-minute
  ruling (2bd3fd92/68b10335).
- The six fixes apply to jet-flap NOW (before capture) and to the motor and
  battery acts.
- STL note: the mid-chord openings she sees suggest the rendered surface or
  its rendering is wrong on screen — cfd verifies what renders vs the
  solved single-slot geometry.
