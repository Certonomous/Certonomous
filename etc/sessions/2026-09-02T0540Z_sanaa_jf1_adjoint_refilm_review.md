# SANAA-DIRECT — JF1/adjoint re-film review (2026-09-02, ~05:40Z)

Captured verbatim from the chief session, reviewing the re-film on the
fresh server (pid 812034).

## Sanaa's words, verbatim

> JF1 : script say 40K iteration but the plots say 8K i guess its bc u did
> 8*5. Script shoudl say 8K it. Also pls make sure the worker count, script
> and screen are synchornized. 2. Adjoint opt: same for adjoint, at the
> moment the worker count appears after the tam starts solving, and the
> geometry changes appear after the team has completed working, where as
> these things should be synchronized.Wing renders: computational mesh, not
> tessellation. Every wing view in this act (gradient-on-skin,
> baseline-vs-optimized, inboard closeups, any animation frames) draws the
> solver's wall patch face by face: 1,008 quad faces with their true edges
> — no triangle diagonals anywhere — flat per-face colour, caption "the
> solver's wall patch, 1,008 faces, drawn face by face." Retire the
> STL-triangle export from all Act D visuals.
>
> 5. Add the volume-mesh cut. One additional mesh view: the symmetry-plane
> slice of the 38,304-cell volume mesh showing the wall layers growing off
> the wing, rendered cell by cell by the same renderer the motor act uses.
> Caption: "the volume mesh at the symmetry plane, wall layers resolved."
> This is the view that makes the mesh read as a mesh.
>
> 6. Small consistencies: baseline Cd printed identically everywhere
> (0.029621 or 0.029620, one choice); trace why interpretation confidence
> prints 74% on a fully-characterized case and fix the display if it's
> miscalibrated; keep the coarse-mesh disclosure line exactly as is
> ("chosen for speed; grid independence not assessed; result relative to
> this mesh").Compute totals: one consistent set. The act must state its
> own total: "Optimization total: [x] core-minutes, [y] minutes wall".
> Reconcile with the gradient-cost table.Consitent numbers everywhere for
> both cases, the sentences in the script are still way too long
