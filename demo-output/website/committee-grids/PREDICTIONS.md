# Predictions, recorded 2026-08-01T08:03:49Z, before any DPW5 solve was launched

Mesh metrics are already measured (logs/DPW5_*_checkMesh.log, 07:59Z) and are
the basis for these. No solver has yet been run on any DPW5 grid.

P1  DPW5 **hybrid** under `base` (the exact numerics that diverged on HLPW6)
    **diverges**, and does so no later than HLPW6 did. Basis: 1,810,108 of its
    6,216,192 faces are severely non-orthogonal (29.1%) against HLPW6's
    1,256,565 of 6,509,759 (19.3%), and its average non-orthogonality is 51.85
    against HLPW6's 42.24. If non-orthogonality is the mechanism, this grid is
    strictly worse than the one that already broke.

P2  DPW5 **hex** under `base` **survives** 200 iterations at second order.
    Basis: 11,506 severe faces of 1,937,920 (0.59%), average 23.71 -- an order
    of magnitude nearer A6's self-generated mesh (1 severe face, average 18.93)
    than either committee unstructured grid. Same nodes, same geometry, same
    boundary layer as the hybrid: only the element topology differs.

P3  If P1 holds, `nonorth2` (nNonOrthogonalCorrectors 2) is the single
    highest-value fix, because the baseline solves the pressure equation with
    **zero** non-orthogonal correctors on a mesh where a third of the faces
    need them. Predicted: survives, or at minimum survives much longer.

P4  `limlin` / `linupV` (removing or vectorising the linearUpwind gradient
    reconstruction) helps **less** than P3, because the baseline gradient is
    already `cellLimited Gauss linear 1` -- the reconstruction is limited
    already, so it is not the unbounded term.

P5  `pcg` (swapping GAMG for PCG/DIC) does **not** prevent divergence. The
    GAMG iteration ceiling reported on HLPW6 is a symptom of an ill-conditioned
    pressure matrix, not a defect of GAMG. Predicted: slower, same outcome.

P6  `slow` (p 0.1, U 0.3) **delays** divergence without preventing it, because
    relaxation rescales the update but not the discretisation error that
    produces it.

P7  `upwind1` (first order) survives on every grid. Carried only as a control;
    a first-order result is not a submission-quality solve and is not presented
    as one.

---

## Added 2026-08-01T08:17:41Z, after P1 and P2 resolved, before the axis in P8 was tested

P1 resolved **confirmed** (hybrid died at iteration 11, exit 136, signal 8,
logs/hybrid_base_incompressible_a2.11_solve.log).
P2 resolved **confirmed** (hex completed 200 iterations, exit 0,
logs/hex_base_incompressible_a2.11_solve.log).

P8  Swapping kOmegaSST for **SpalartAllmaras** helps materially, and more than
    any single scheme change. Three reasons, stated before the test: the crash
    is a divide-by-zero inside the turbulence stack, not inside the momentum or
    pressure assembly; SA carries no omega equation and no omega wall function,
    which are the stiffest terms in the k-omega stack on cells whose aspect
    ratio runs to 7,488; and SA is the model DPW and HLPW publish their own
    baseline results with, so if it works it is also the more appropriate
    choice rather than merely the more robust one.
    This was not in the original list. It was added because the failure
    signature -- `Foam::divide` in the turbulence model on both grids --
    points at it.

## Added 2026-08-01T08:29:58Z, after P3 was tested

P3 resolved **falsified.** `nonorth2` died at iteration 11 -- the same
iteration as the baseline -- with continuity error 3.3e14, exit 136,
logs/hybrid_nonorth2_incompressible_a2.11_solve.log. Two non-orthogonal
correctors cost 2.65x the wall time (353.3 s against 133.3 s) and bought
nothing at all. The textbook first answer to a non-orthogonal mesh does not
work here, and that is worth more than it being right would have been: it says
the correction loop is not converging rather than being merely under-applied.

P9  Given P3, the axis that matters is the **explicit** non-orthogonal
    correction itself, not how many times it is applied. `uncorr` (drop it
    entirely, keeping only the implicit orthogonal part) survives, at the cost
    of a first-order consistency error in the viscous term. Predicted: survives.

P10 `prod` -- a TVD face-value limiter for convection instead of gradient
    reconstruction, correction limited to 0.25 rather than switched off, two
    correctors, relaxation p 0.2 / U 0.4 -- is the configuration most likely to
    be both survivable and defensible, because `limitedLinear` is second order
    in smooth regions without reconstructing over a nearly tangential
    face-to-cell vector. Predicted: survives, and is the one worth carrying
    forward to HLPW6.

## Added 2026-08-01T08:37:11Z, with `uncorr` running and nothing after it started

P4 resolved **falsified in the direction that matters.** `limlin` -- replacing
the gradient-reconstructing `linearUpwind` with a TVD face-value limiter that
reconstructs nothing -- died at iteration 12, exit 136,
logs/hybrid_limlin_incompressible_a2.11_solve.log. P4 predicted it would help
less than correctors; it helped as little as correctors did, which is not at
all. Neither the convection scheme nor the corrector count is the binding term.

Three further axes are now queued, each a different hypothesis about what
breaks first, and each stated before its run starts:

P11 `potinit` -- initialise from a divergence-free potential-flow solution
    instead of a uniform freestream everywhere. **Predicted: this is the one
    that works.** Every failure so far begins with the pressure equation in the
    first ten to fifteen iterations, which is exactly when a uniform initial
    field is least divergence-free; on a wing-body at incidence that initial
    transient is violent, and on a mesh with a third of its faces at 90 degrees
    the pressure equation has no headroom to absorb it. This is the standard
    remedy and no run so far has used it.

P12 `pcap` -- cap the GAMG pressure solve at 100 iterations with
    DICGaussSeidel smoothing, as the HLPW6 hardened run did. Predicted: helps,
    because every divergence here is preceded by the pressure solve returning a
    half-converged field after 1,000 iterations, and a capped solve returns a
    consistently-under-solved field rather than an inconsistent one.

P13 `wdpois` -- compute wall distance by the Poisson method rather than by
    meshWave. Predicted: **no effect**. The crash is inside the turbulence
    model, which is why this is worth excluding, but the pressure equation goes
    first in every log, and wall distance cannot cause that.

## Added 2026-08-01T08:46:40Z

P9 resolved **falsified.** `uncorr` -- the explicit non-orthogonal correction
removed from the Laplacian and the surface-normal gradient entirely -- died at
iteration 11, exit 136. So the diffusion term is not the binding one either.

P10 resolved **falsified.** `prod` died at iteration 13.

P11 **not tested.** The potentialFoam pre-step aborted (missing
`div(div(phi,U))` scheme entry) and exited 1, so that run started from a
uniform freestream after all and proves nothing. Renamed INVALID_ and requeued.

Four scheme axes -- corrector count, convection scheme, the non-orthogonal
correction itself, and a combination -- all die at iteration 11, 11, 12 and 13.
That they all die at the same place despite discretising differently says the
trigger is not any one term.

P14 The axis that has not been moved is **relaxation**, and it is the only one
    whose movement costs no accuracy: relaxation changes the path to the
    answer, not the answer, so a second-order solve reached slowly is still a
    second-order solve, where a first-order solve reached quickly is not.
    Predicted: `crawl` (p 0.05, U 0.2) or `crawl3` (p 0.02, U 0.1, two
    correctors, TVD convection, capped pressure solve) survives 120 iterations
    at second order. If it does, the answer to the gating question flips from
    "committee grids are out of reach" to "reachable, at a price in iteration
    count" -- and the price is then the thing to measure.
