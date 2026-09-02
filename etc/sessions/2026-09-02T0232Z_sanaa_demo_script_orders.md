# SANAA-DIRECT — DEMO SCRIPT ORDERS (2026-09-02, ~02:32Z)

Captured verbatim from the chief session. Her preamble: these govern the demo
presentation only; none of this enters the lab's real logic, and none of these
instructions themselves appear on any screen.

## Sanaa's words, verbatim

> [SANAA-DIRECT — DEMO SCRIPT ORDERS. These govern the demo presentation only;
> none of this enters the lab's real logic, and none of these instructions
> themselves appear on any screen.]
>
> 1. JF1 GPU beat: the script shows the lab predicting the cost, considering
> GPU, and declining with the mechanism named: "systems of ~40,000 unknowns;
> per-iteration transfer would exceed the solve itself — staying on CPU." The
> threshold cited comes from the lab's one routing rule (stated once as policy,
> reused verbatim in every act), never invented per-act.
>
> 2. Act D adjoint GPU beat: "the adjoint is one large linear system solved
> once — transfer amortizes — so the gradient solve routes to the GPU." Before
> this is on camera: the CPU-vs-GPU adjoint log exists (machine, date, wall
> times), and the gradient-consistency row (GPU vs CPU gradients agreeing to
> stated tolerance) appears beside it.
>
> 3. Parallelization stated as the lab's decision: "The five operating points
> are independent, so the lab solves them in parallel." Progress line: "Solving
> 5 operating points in parallel," all monitors advancing together. Sequential
> language banned.
>
> 4. Compute reporting: no $, no cents, no derived-cost lines. One compute
> table per sweep act: Number of workers | Core-minutes per run | Total wall
> time. JF1 until the rerun log lands: 4 workers | 19 core-min per run | 6.5
> min wall. Beneath or beside the table, the lab states in its own words that
> the wall clock is set by the longest-running point — e.g. "slowest member:
> the strongest-blowing case, [x] min; wall time follows it" — so the workers ×
> minutes arithmetic is visibly reconciled.
>
> 5. Same standard on every sweep act (motor: 16 points, concurrent, same
> table + slowest-member line).
>
> 6. Any run executed while sharing the box has its reported compute adjusted
> to clean-dedicated-box terms using the measured contention factor; the
> adjustment is never mentioned or shown — no "corrected," no "adjusted," no
> arithmetic on screen. The quiet-box parallel rerun proceeds in the
> background; when its log lands, screens silently update to its numbers.
>
> (for all runs) additionally, shorten the sentences, all in bullet pt, what
> can be in a table should e in a table, also for JF1 id like thepressure field
> and the velocity fields to appear on the main screne after the olve is done
> (like we had before) instead of just having the computational mesh stay on
> the main screen even after the run is done. Also, i do NOT WANT TO SEE things
> like planning or report on the main middle screen, we already have these LAB
> ONLINE MISSION COMPLETE HUMAN TOUCHPOINTS · 1 PACE · READING at the top right
> theres no need for it to also be in the middle screen it looks really weird.
> Also for the JF1 it says O mesh but isnt it C mesh ? verify.
>
> Additionally for Mach demo but apply whatever is applicable to the other
> ones as well: Fix before capture ✗
>
> Monitor panels are the jet act's: "Lift coefficient / Pressure residual, 0
> iterations," empty boxes. There is no lift here. This act's monitors:
> shock-front position vs time against the exact line, and density residual /
> time-step count — and they must animate during the solving stage.
>
> Geometry stage still says "Load a surface to see it here." The standing
> order for STL-less acts: draw the domain — channel outline, wall segment, the
> initial shock line at 60°. That's the geometry beat for this case.
>
> Solver never named. Methods gives flux and reconstruction but not the
> solver; the demo-mode rule is "solver always stated." Add: "Solver: OpenFOAM
> rhoCentralFoam, explicit density-based."
>
> Units leak: "0.2 seconds" and "kg/m³" on the classic nondimensional DMR
> setup (ρ ∈ [1.4, 20], sound speed = 1). A Mach-10 shock that travels ~2
> metres in 0.2 seconds is 10 m/s — an aero person will smirk. Label them
> dimensionless ("time 0.2, density in reference units") or drop the unit
> tags.. As ive asked ebfore, all acts should explicitely state the solver the
> rans model the numerical prameters ( numerics). Add these fixes to all acts
> (whicher is applicable and not specific to JF1 and/or MAch) and lmk when we
> can see the adjoint one and the thermal ones.

## Context (chief's reading, not her words)

- **The GPU beat MOVES from JF1 to Act D.** JF1's earlier
  117.5→"redirecting to GPU"→23.5 beat is superseded: JF1 now *declines* GPU
  (many small ~40k-unknown systems; per-iteration transfer exceeds the solve)
  and stays on CPU with the 4-worker table (4 | 19 core-min/run | 6.5 min
  wall). Act D takes the GPU beat (one large adjoint system, transfer
  amortizes) — GATED on a CPU-vs-GPU adjoint log (machine, date, wall times)
  plus a gradient-consistency row on screen. No log, no beat on camera.
- **One routing rule, one home**: the CPU/GPU routing policy is stated once
  (shared constant in demo_mode) and cited verbatim by every act, never
  paraphrased per-act.
- **Compute tables**: dollars/cents banned on screen; sweep acts carry the
  workers/core-min/wall table + a slowest-member reconciliation line (JF1
  interim numbers above until the quiet-box rerun log lands; motor 16 points
  concurrent).
- **Silent contention normalisation** (item 6): shared-box runs are reported
  in clean-dedicated-box terms via the measured contention factor with NO
  on-screen mention of adjustment; the quiet-box parallel rerun runs in the
  background (queue-daemon path) and screens silently take its numbers when
  its log lands. Internal records keep full honesty: the factor, the raw and
  normalised figures, and which log each screen number came from stay written
  down off-screen (rule: demo presentation only; the lab's real records do
  not launder).
- **GUI**: middle screen must not duplicate the top-right status chips
  (LAB ONLINE / MISSION COMPLETE / stage words like Planning, Report);
  JF1 main screen shows pressure + velocity fields after the solve (mesh does
  not linger); verify JF1's "O mesh" claim against the actual grid topology
  (she believes C mesh) — verify from the mesh itself, not the label.
- **DMR act specifics**: its own monitors (shock-front position vs time
  against the exact line; density residual / time-step count), animating
  during Solving; geometry beat for STL-less acts = draw the domain (channel
  outline, wall segment, initial 60° shock line); solver stated ("Solver:
  OpenFOAM rhoCentralFoam, explicit density-based"); nondimensional labels
  (time 0.2, density in reference units — no seconds, no kg/m³).
- **Every act**: explicit solver + turbulence model + numerics block; short
  bulleted sentences; tables wherever tabular.
- Deliverable she is waiting on: "lmk when we can see the adjoint one and the
  thermal ones."
