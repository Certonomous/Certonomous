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
