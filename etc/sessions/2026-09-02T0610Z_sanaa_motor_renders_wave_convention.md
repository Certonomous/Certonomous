# SANAA-DIRECT — motor render defects + wave/compute convention for all acts (2026-09-02, ~06:10Z)

Captured verbatim from the chief session, reviewing the motor take.

## Sanaa's words, verbatim

> motor: The slowest-member line now contradicts the wall clock. "Slowest
> member: 155 W, 30 m/s, 39.2 minutes; the wall time follows it" — but the
> wall time shown is 86 minutes. Both numbers are right; the sentence is
> wrong for this act: 16 runs on 12 workers is two waves (12 then 4), so
> wall ≈ first-wave slowest + second-wave slowest ≈ 39 + 36 ≈ 75–86 min. Fix
> the line for the general case: "16 runs on 12 workers is two waves; the
> wall clock follows the slowest member of each wave (39.2 and 36.x min),
> never the 579 core-minute sum." That phrasing also survives JF1 (one wave)
> unchanged in spirit.
> Confirm the geometry render shows the solved body. The wireframe reads as
> a tall duct with a small stub at the bottom — the solved case has a
> full-length centerbody (nose, heated core section, tail) running the duct.
> Rotate the view or draw the axisymmetric section outline; if the STL
> genuinely lacks the centerbody, it's the wrong export again. [SANAA-DIRECT]
> Motor act, two render defects: (1) The grid panel must draw the solved
> polyMesh section — cell by cell, horizontal, fit-to-extents, wall-layer
> grading visible, with a zoom inset at the housing wall; the
> uniform-squares patch currently shown is not the mesh and is removed. (2)
> Monitors: 16 panels in two rows of eight, one label inside each
> ("80W · 10m/s"), no shared header, caption printed once. Screenshot both
> after the fix. also, for all acts, if things are running in parallel then
> the predicted ncore minutes should be divided by the number of workers.
> For all runs: Compute tables report per-run core-minutes , their plain sum
> as total, and wall time; parallelism is expressed in wall time and the
> wave sentence

## Context (chief's reading, not her words)

- Compute convention, all acts: tables carry per-run core-minutes, their
  plain sum as total, and wall time; parallelism lives in the wall-time
  column and the wave sentence, and the PREDICTED wall time derives from
  predicted core-minutes divided by the worker count. Wave sentence takes
  her general form; one-wave acts keep the spirit (wall follows the
  slowest member).
- Motor: two-wave sentence with the real second-wave slowest filled from
  logs; geometry render must show the full solved centerbody (verify the
  export against the solved case, rotate or draw the axisymmetric section);
  grid panel = solved polyMesh section cell by cell (uniform-squares patch
  removed); monitors 2x8 with in-panel labels, no shared header, caption
  once; both screenshots inspected after the fix.
