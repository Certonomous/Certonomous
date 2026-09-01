# SANAA-DIRECT — DEMO SHOOTING PROTOCOL, the standard sequence for every act (2026-09-01, ~20:30Z)

Binding for every act. Supersedes conflicting earlier presentation details;
refines the tense rule (present/progressive while running, PAST TENSE FOR
RESULTS) and sets the battery act's beat as the refusal itself.

## Sanaa's words, verbatim

> # DEMO SHOOTING PROTOCOL — THE STANDARD SEQUENCE FOR EVERY ACT
> [SANAA-DIRECT. Demos show the user experience of the finished multi-user
> platform, in its best light. Every number, field and figure is real and
> computed. What the platform will do automatically is shown as the platform
> doing it. Nothing narrates the current state of the lab.]
>
> ## The fixed sequence (every act, same order, same screens)
>
> 1. GEOMETRY APPEARS. The user's uploaded STL renders immediately in the
>    geometry panel. Panel shows geometry, then mesh, then fields, nothing else.
> 2. TEAM PROGRESS, TOP RIGHT. Stage indicator advances live: Forming the
>    team -> Reading the geometry -> Planning -> Meshing -> Solving (n of N)
>    -> Checking -> Report. Counters reflect actual activity.
> 3. ACKNOWLEDGEMENT. The team restates the task in one sentence and
>    summarises the geometry in a table (extent, reference lengths, features
>    found: slot, channels, housing, tip). Confidence stated.
> 4. EXPERT DISCUSSION (short, visible, in the conversation panel):
>    - Lead Researcher: physics identified; turbulence/closure model chosen
>      and why (class, known limits).
>    - Lead Engineer: mesh type and target resolution; solver named.
>    - Lead Numericist: numerical parameters (schemes, tolerances, time step
>      where transient); the checks that will run.
>    - Assumptions table: USER-DEFINED (from the prompt) vs LAB-DEFINED
>      (defaults, representative properties), every quantity with a value and
>      unit. The one user-assumption correction beat, where the act has one.
> 5. RUN. Meshing shown live on the real geometry (cell-by-cell grid, wall
>    zoom, resolution table). Then solving: sweep or multipoint runs shown
>    simultaneously as small multiples on one screen (residuals, force or
>    temperature traces), iteration counter and wall time advancing.
>    Anything smart that happens in between appears here (a check that
>    fires, a setting the team adjusts, a prediction registered).
> 6. RESULTS. Numbers in tables with units; the verification lines in plain
>    words with their references; compute time (estimate vs actual);
>    conclusion in two sentences.
> 7. REPORT TAB. All plots (figure standard: short title, axes with units,
>    one caption line, no paragraphs), the summary, the assumptions, the
>    certificate block, next steps.
> 8. CONVERGENCE STUDY. Either shown as part of the results (band on every
>    number) or the team says: "The grid convergence study for this case is
>    running; the band lands in your inbox with the certificate." The
>    platform always runs it; the demo shows it as done or as automatically
>    underway, never as absent.
>
> ## Language (unchanged, binding)
> Present and progressive tense while running; past tense for results.
> Never: prior runs, replay, agreements, paths, ids, tiers, "not recorded",
> "no solver", "already finished". Physics facts stay (single mesh so far,
> representative properties, no measured data for this configuration) and
> are phrased as the platform's next automatic step, not as an apology.
>
> ## Per act, the beat that makes it memorable
> - Motor: the thermal-resistance estimate shown first, then corrected by the
>   coupled solve; envelope with the 200 C line.
> - Wing optimization: shape morphing live; gradient verified before
>   optimizing; improvement decomposed before the percentage.
> - Multipoint: three conditions solving side by side; the Mach-vs-angle
>   well-posedness correction as the assumption beat.
> - Blown wing: square-root growth vs the straight line an engineer would
>   guess; the jet sheet traced.
> - Mach 10 reflection: two grids vs exact theory to 0.2% on screen.
> - Battery: the run completes, the gate refuses it, the platform says so
>   and schedules the corrected run. The feature is the refusal.
>
> ## Shooting checklist (before each capture)
> [ ] STL is the solved geometry and renders on load
> [ ] Header stages advance and match what is on screen
> [ ] Expert discussion present, assumptions table present
> [ ] Mesh shown as real cells; resolution table present
> [ ] Sweep/multipoint monitors as small multiples on one screen
> [ ] Results table, compute line, conclusion
> [ ] Report tab populated: plots to the figure standard, summary, next steps
> [ ] Convergence study shown done, or the "lands in your inbox" line
> [ ] Zero forbidden language on any screen
