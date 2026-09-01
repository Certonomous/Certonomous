# SANAA-DIRECT — DEMO MODE, binding for every act tomorrow (2026-09-01, ~03:40Z)

## Sanaa's words, verbatim

> comment for all demos: [SANAA-DIRECT] DEMO MODE, binding for every act
> tomorrow:
> What it is. A demo act is the live GUI pipeline fed by a completed run
> tree. It looks and behaves exactly like a user running the case: every
> stage renders in its normal place and its normal order. The only difference
> from a fresh run is that the solver stage replays the stored logs at
> accelerated pace instead of computing. Every number, field and figure is
> the real run's; nothing is invented. The run record carries an internal
> flag "presentation of run X"; that flag is never on screen.
> The stages, all mandatory, all visible:
>
> Prompt (professional wording) → restatement, confidence, cost estimate →
> one user-assumption check.
> Geometry: the uploaded STL renders. It is the exact solved geometry
> (regenerate the STL from the solved case where it differs). "No surface
> loaded" never appears.
> Meshing runs live (2D/axisymmetric cases mesh in seconds to a minute): the
> real mesher on the uploaded STL, the computational grid drawn cell by cell,
> wall-layer zoom, slot/wall resolution table.
> Feasibility beat: "30-second check before committing budget", with its
> result.
> Solving: monitors advance in real time from the stored logs at accelerated
> pace: iteration counter, residuals, lift/drag or temperature curves moving;
> progress across the sweep points. Elapsed time shown is the run's real wall
> time.
> Gates and checks: planted-perturbation reader checks, conservation, grid
> statement, in tables.
> Results: fields, plots, tables, verification lines, limitations box, cost
> line (the run's real cost, shown as this run's cost, because it is).
> Language. Progressive tense while running ("Meshing", "Solving, iteration
> 4,000 of 20,000", "Sweep point 3 of 5"), past tense for results. Never:
> "already finished", "presenting", "nothing new is solved", "no compute
> booked", "screens come from", "reference body", "surface on file", "not
> meshed by this screen", any path, any "two grids were built". Physics
> limitations stay, compact: "exploratory; settling target not reached at
> high blowing; single grid; no wind-tunnel data for this section."
> Jet-flap specifics. One grid on screen: use the 39,984-cell force grid for
> fields, pressures and the lift table alike; if a flow picture exists only
> on the finer grid, the sheet says "flow picture from a finer companion
> grid" in the limitations box and nowhere else. Prompt: "Blown-wing
> high-lift: sweep the trailing-edge jet momentum coefficient from 0 to 0.4
> and report lift against blowing with the classical jet-flap theory."
> Reference stated once: Williams, Butler and Wood, ARC R&M 3304 (1961),
> eq. 2. The lift table (surface lift, jet push, total, published) is the
> deliverable; keep it exactly.
> Motor and battery acts: same mode, same stages, same language rule. Build
> the mode once and route all four acts through it.

## Chief's routing

- cfd builds DEMO MODE once in the GUI pipeline (stage sequencing, log-replay
  solver stage at accelerated pace with real wall time shown, live mesher
  stage, feasibility beat, language rules); all four acts route through it.
- heat-transfer plugs the motor and battery acts in; dafoam plugs Act D in.
- Jet-flap specifics: one grid on screen (39,984-cell force grid); finer-grid
  flow picture named only in the limitations box; her exact prompt and the
  lift table kept exactly; WBW 1961 eq. 2 stated once.
- The "presentation of run X" flag lives in the run record only, never on
  screen — every number, cost and elapsed time is the real run's.
