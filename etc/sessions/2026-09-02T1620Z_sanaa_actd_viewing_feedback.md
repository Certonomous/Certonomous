# SANAA-DIRECT — Act D viewing feedback (2026-09-02, ~16:20Z)

## Sanaa's words, verbatim

> 1. MAKE MONITOR say this instead: Gradient check: adjoint against central
> finite differences
>
> remove the word act NUMERICIST
> • Results are relative to this mesh; grid independence not assessed in
> this act. and check that we dont use that word in ANY act anywhere. And
> insead ofthissentence say grid independence study in your inbox, ETA: 11
> min (dont argue).
> PUT THIS IN A table! CHIEF ENGINEER
> • Solver: DAFoam DARhoSimpleFoam on OpenFOAM v2506, steady compressible
> RANS (Spalart-Allmaras), with a reverse-mode discrete adjoint.
> • Solved on this geometry: 47 major iterations, 38,304 cells.
> - for the geometry plots, can we make the geometry and its color bar
> bigger pls? rn its so small inside a big box so the geometry itself is
> small but we have a lot of empty space around it. Itd be nicer if we could
> see the geometry big and the color bar big as well.
> - gpu beat is missing: The researcher should say: Cell number : .. :
> Primal solve: CPU, adjoint solve: GPU. Even though this is a small system,
> the adjoint is just one linear solve. Transfer is paid once
>
> remove th eline: CHIEF ENGINEER
> • From a verified gradient to drag 28.3% below untwisted baseline at
> matched lift.
>
> this in the report: ethods
> Solver: DAFoam DARhoSimpleFoam on OpenFOAM v2506, steady compressible
> RANS (Spalart-Allmaras), with a reverse-mode discrete adjoint. Solved to
> its own residual tolerance with wall functions.
> Discrete adjoint for drag and for lift with respect to surface control
> points, spanwise twist and the flow state. The derivative is taken by
> reverse-mode automatic differentiation of the discretized residuals, with
> the one-equation turbulence transport equation among the 5 differentiated
> state fields rather than frozen; the wall distance feeding its source term
> is the one term not differentiated.
> Verification by central finite difference of the full primal at a single
> absolute step of 0.001, 210 perturbation solves covering every one of the
> 105 design variables. This case was graded at that one step and was not
> itself swept across decades; the step comes from a sweep run on the
> smaller case at the foot of the same ladder.
> Graded against this lab's current gradient standard, applied uniformly
> across the whole ladder: pass at 5% or better with no flagged component,
> conditional between 5 and 15%, fail above 15% or on any sign-flipped
> component whatever the aggregate says.
> Gradient-based optimization with lift equality-constrained to 0.5 and
> thickness, volume and edge constraints active.
> Nothing on screen is scaled. The wing is shown twice, once whole and once
> on the inboard 2.2 m of span on a closer viewing convention, and both
> section figures are unscaled with equal aspect. make it a table

## Context (chief's reading, not her words)

1. Monitor panel title: "Gradient check: adjoint against central finite
   differences".
2. The word "act" is internal vocabulary and appears on no screen of ANY
   act — sweep all five. The mesh-relativity sentence is REPLACED by
   "grid independence study in your inbox, ETA: 11 min" — her explicit
   "dont argue"; this supersedes the request-declined convergence line from
   her earlier prompt order for this beat (the assumptions row can stay
   consistent with whatever the beat now says — the lane reconciles and
   reports the shape; the gate's convergence limb already has an inbox
   branch). ETA 11 min is her stated figure.
3. Solver + solved-on-geometry bullets become a table.
4. ParaView geometry views: geometry and colour bar fill the frame (fit
   camera tighter, bigger scalar bar), less empty space.
5. GPU beat restored on the researcher, her content: cell number, primal
   solve CPU, adjoint solve GPU, "Even though this is a small system, the
   adjoint is just one linear solve. Transfer is paid once."
6. The chief-engineer line "From a verified gradient to drag 28.3% below
   untwisted baseline at matched lift." is removed.
7. Report Methods becomes a table carrying her text row by row.
