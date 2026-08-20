# Pre-gate wall-function directories, removed from the T1b case set

`W_10k` and `W_30k` were written at 2026-08-19 19:06 UTC by a build_t1b.py that
did not yet carry the wall-function feasibility gate.  The gated builder, which
produced every case that was actually run (19:43 onward), places both Reynolds
numbers in its `skipped` list and never emits a directory for them.

They were never solved: no `0` directory, no `log.solve`, no time directories.
They are not in the run pool.

They are moved here rather than deleted because the frozen comparator
`analyse_t1b.py` selects the wall-treatment arm with
`os.path.isdir(HERE/W_<tag>)`.  Left in place, two directories that the design
excludes on geometric grounds would have been picked up as if they were arms of
the experiment, and the comparator would have died inside `latest_time` on a
case with no solution.  Moving them one level down restores the disk to the
registered 19-case design without destroying the evidence of the superseded
build.

## Why the gate is right, in numbers

At the target y+ = 50 the required first-cell HEIGHT, against a pipe radius of
0.1 m:

| Re      | u_tau (m/s) | y+=50 cell | as % of R | cells that fit | arm built |
|---------|-------------|------------|-----------|----------------|-----------|
| 10 000  | 0.04705     | 3.188e-02 m| 31.9 %    | 3              | no        |
| 30 000  | 0.12231     | 1.226e-02 m| 12.3 %    | 8              | no        |
| 100 000 | 0.35568     | 4.217e-03 m|  4.2 %    | 23             | yes       |
| 300 000 | 0.95577     | 1.569e-03 m|  1.6 %    | 63             | yes       |

The floor is 12 cells across the radius.  The constraint is physical, not a
tuning failure: at low Re the viscous sublayer occupies a large fraction of a
small pipe, so there is no admissible wall-function mesh there.

## What these two directories actually contain

Both hold `(400 30 1)` with `simpleGrading (1 1 1)` -- 30 UNIFORM radial cells,
not the graded mesh their own CASE.txt describes.  A uniform 30-cell radius puts
the first cell centre at

  Re = 10 000 -> y+ = 5.23
  Re = 30 000 -> y+ = 13.59

Both sit inside the buffer layer, below the comparator's own WF_YPLUS_FLOOR of
30, so even had they run they could only have been REPORTED, never graded.  The
CASE.txt `first_cell` and `u_tau_estimate` fields in these two directories
describe a mesh that was not written; trust the blockMeshDict, not the header.
