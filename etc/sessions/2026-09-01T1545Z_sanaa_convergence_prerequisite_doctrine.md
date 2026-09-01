# SANAA-DIRECT — MAKE THE RUNS WORK: convergence as a prerequisite, per-case fixes (2026-09-01, ~15:45Z)

Captured verbatim from the chief session. Her own header: "Cost is not a
constraint. Every gated case runs its grid convergence study automatically; a
case without one is not a result." This is lab law under her authority; the
PLUMBING FREEZE does not bar her own orders.

## Sanaa's words, verbatim

> # MAKE THE RUNS WORK: CONVERGENCE AS A PREREQUISITE, PER-CASE FIXES
> [SANAA-DIRECT. Cost is not a constraint. Every gated case runs its grid
> convergence study automatically; a case without one is not a result.]
>
> ## 0. THE AUTOMATIC CONVERGENCE STUDY (pipeline stage, all cases)
> Every gated case, without being asked:
> 1. Build THREE geometrically similar meshes from one parametric script:
>    same topology, same layer structure, uniform refinement ratio r between
>    1.5 and 2.0 in every direction (r = 1.3 is the floor; larger r gives a
>    cleaner observed order). Near-wall spacing scales with r; y+ stays
>    under 1 on every level where the case is wall-resolved.
> 2. Run all three to TIGHT iterative convergence. Rule: the iterative
>    change in the graded quantity must be at least 10x smaller than the
>    difference between consecutive mesh levels. If it is not, the observed
>    order is noise, not discretisation. Tighten residuals (1e-8) and the
>    stationarity window before concluding anything about the grid.
> 3. Compute the observed order p from the three levels and the GCI on the
>    graded quantity. Acceptance: p within 0.5 of the scheme's formal order
>    (second order: p in 1.5 to 2.5). Report p and the band.
> 4. IF p IS OUTSIDE THE RANGE: do not stop. Automatically (a) check step 2
>    again on the finest level, (b) verify the three meshes are similar (cell
>    count ratios, layer counts, growth ratios: the F28 lesson), (c) add a
>    FOURTH, finer level at the same r and recompute p on the finest three,
>    (d) repeat up to two more levels. A quantity sampled at a single cell
>    (a max) may need a smoother companion quantity for the order study
>    (integrated heat flux, integrated force); use it for p, apply the band
>    to the reported max, and say so.
> 5. Only then is the case gradable. The band goes on every number.
> Compute for a 2D or axisymmetric family: tens of core-minutes to a few
> core-hours. That is never a reason to skip it.
>
> ## 1. MOTOR IN DUCT (Act A): p = 0.375 means "not yet in range", so go there
> - Cause candidates, check in order: (a) iterative convergence too loose
>   relative to the level-to-level difference in T_max (T_max stationarity
>   was 0.05 K; the inter-level differences may be of that size): tighten
>   energy residual to 1e-9 and T_max stationarity to 0.005 K over 2000
>   iterations on every level, re-read p. (b) Mesh similarity: confirm the
>   wall-layer count and growth ratio are identical across levels and only
>   the spacing scaled; if L1 had fewer layers, it is not similar: rebuild.
>   (c) Coarsest level outside the asymptotic range: add L4 at r = 1.5 from
>   L3 (about 130k cells), then L5 if needed; take p from the finest three.
>   (d) Use the core's volume-averaged temperature and the housing surface
>   heat flux as the order-study quantities; apply their band to T_max.
> - Run until p lands in 1.5 to 2.5. Then the sixteen points get their band
>   (measured at 305 W / 20 m/s, applied to all, disclosed).
> - Also record y+ on every level; the 3.5 mm wall must keep 8+ cells at L1.
>
> ## 2. BATTERY MODULE (Act C): the outlet temperature depends on sweep count
> This is under-iteration inside each time step during the fast load change.
> - Ramp the load: replace the step at t = 0 and t = 60 s with a 1 s linear
>   ramp (a discontinuous source destroys time accuracy at the jump).
> - PIMPLE: nOuterCorrectors 3 -> up to 15 with residualControl on p, U, h
>   (1e-7) so each step converges to a fixed tolerance rather than a fixed
>   count; momentumPredictor on; nCorrectors 2.
> - Time step: dt = 0.02 s during the pulse window (t < 70 s), 0.1 s after;
>   or adaptive with maxCo 0.5. No fixed-count sweeps anywhere.
> - Convergence study: three meshes (channel cells 8/12/18, wall layers
>   scaled) AND three time steps (dt, dt/2, dt/4) on the middle mesh; observed
>   order in space and time; gate: the outlet temperature history and per-
>   cell peaks change by less than the registered tolerance between the two
>   finest levels of each ladder.
> - Loads: volumetric, as ruled (1e5 W/m3 pulse, 2.5e4 W/m3 cruise).
> - Act C decision: run this fix now; if graded before the demo, show it; if
>   not, show the honest-refusal act (option a). Never show the 0.4 K run.
>
> ## 3. JET FLAP (Act B): turbulence residual stalls at high blowing
> Escalate in this order, one change per run, pre-registered:
> 1. Continuation: initialise each Cmu case from the converged solution of
>    the next-lower Cmu (0 -> 0.05 -> 0.1 -> 0.2 -> 0.4) instead of from
>    freestream.
> 2. Relaxation: k and omega 0.7 -> 0.5; nNonOrthogonalCorrectors 2; bounded
>    schemes on k and omega already; limitedLinear 1 -> 0.5 if needed.
> 3. Pseudo-transient: run pimpleFoam with local time stepping (or a large
>    fixed dt) toward steady state; the k-channel stall usually resolves.
> 4. If forces still oscillate at Cmu = 0.4, the flow is mildly unsteady: run
>    a true transient (dt ~ 1e-4 s, 20 flow-throughs), time-average, and
>    re-register the point as a time-averaged result with its band.
> - Convergence study: three grids at Cmu = 0.1 (the 39,984-cell grid as L2;
>   build L1 and L3 at r = 1.5 from the same script). p, GCI, band on CL.
> - One grid family on screen for all figures.
>
> ## 4. DUCTED DISK (F28): the 33.5x cell-volume jump
> - Fix the generator: cap the cell-to-cell volume growth at 1.25 everywhere,
>   especially at the duct trailing edge; regenerate the three levels from
>   the fixed script (similarity now guaranteed); confirm with a cell-volume
>   ratio histogram before solving.
> - Absolute floor beside the relative stationarity criterion is approved and
>   landed; run the map; convergence study at (1000 Pa, 20 m/s).
>
> ## 5. COMPRESSIBLE OPTIMIZATION (Act D): the gradient component that never closed
> - Identify the component (likely a trailing-edge or twist variable).
> - FD step sweep on that component only: 1e-2, 1e-3, 1e-4, 1e-5; converge
>   each perturbed primal to 1e-8 so FD noise is below the plateau; report
>   the plateau value against the adjoint.
> - If the adjoint is off on that component alone, check whether its path
>   depends on a non-differentiated quantity (wall distance) and either
>   differentiate it or disclose the frozen term as the cause.
> - Close it, or exclude the variable from the design set with the disclosure
>   on the row. Then re-grade.
> - Convergence study for the wing: build L2 (~100k) and L3 (~300k) from the
>   same script as the 38k baseline; CD at fixed CL on all three; p and GCI;
>   gradient verification repeated on L2. The optimization result carries the
>   band. This is hours of compute, not minutes; run it.
> - Decomposition on the demo table: shape contribution vs incidence
>   contribution (4 deg -> 0.8 deg) before any percentage.
>
> ## 6. ONERA M6: what went wrong and how to do it properly
> [her full text, including:]
> - Option 1 (fastest, real): use a published M6 grid family: public
>   ONERA M6 meshes exist (SU2 distributes inviscid and turbulent M6 meshes;
>   workshop grid families exist for the same geometry). Import, verify the
>   geometry against the AGARD definition, run the three levels.
> - Option 2 (in-house): generate with the cut-cell mesher (snappyHexMesh)
>   from the real M6 surface with tip refinement and wall layers.
> - Option 3: hyperbolic extrusion with a proper tip topology (an O-grid cap
>   over the tip), which is a surface-blocking job, not a parameter change.
> Order: option 1 this week, option 2 as the standing capability.
>
> ## 7. TODAY'S DECISIONS
> - Act C: run the fix in §2 now; demo shows it if graded in time, else the
>   honest-refusal act. (a) as fallback, not as plan.
> - ONERA M6: withdrawn from today; Mach-10 reflection act GO; M6 rebuilt per
>   §6 this week.
> - Act D core-minute line: KEEP. Cost transparency is a rule; a viewer who
>   divides and gets 60 minutes is a viewer we want.
> - Restart line: GO on all acts under demo mode; convergence studies launch
>   in parallel on every case named above, starting now.. This should also be
>   included in all of the relevant lessons of how to proceed whenever any of
>   this class of problems appears in the future. This is the pro activity
>   that the supervisors need to have.
