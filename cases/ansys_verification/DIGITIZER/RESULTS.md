# RESULTS — DIGITIZER instrument calibration

**Verdict: `NOT A RESULT`.** Taken by `ansys-verification-supervisor` personally,
2026-09-03, by reproducing the frozen instrument's `--calibrate` run against the
freeze and getting byte-identical numbers. Freeze commit `0fab170f`; instrument
blob `2092c55dd59d36c490b5fc3681bfd36c30d5b49b` verified == HEAD before the run.

## The verdict, and why it is the instrument working

`--calibrate --n 24` **refused (exit 2) at POSITION PLANT-NULL.** A clean,
undisplaced control plate (plate 0, feature at x = 1.0023) was read back at an
offset of **0.0032424 x-data-units = 1.167 px**, exceeding the POSITION `u_read`
of **0.0027778** (the pixel floor). Per `§25.7` / `§28.8` a plant refusal is a
**`NOT A RESULT`** and **the instrument unlocks nothing** — even though the VALUE
quantity calibrated cleanly. This is the planted-null control of `rule 3` /
`§16.4` doing exactly its job: refusing to certify a `u_read` the reader cannot
back on a plate whose answer is known to be zero displacement.

Reproduced by the supervisor: `REPRO_CALIBRATE.supervisor.{out,err}`, rc 2, wall
6.009 s. Lane's authorised run: `GRADE_DIGITIZER.{out,err}`, rc 2, wall 6.770 s,
and `GRADE_DIGITIZER.diagnostic.json` (a clearly-labelled post-refuse
reproduction of the frozen instrument's seeded numbers — the refused run emitted
no report because it exited 2 mid-run, which is refuse-not-degrade working).

## Per-quantity numbers (reproduced)

| quantity | u_read | syn_rms (A) | half-spread (B) | pixel floor (C) | binding term | plants |
|---|---|---|---|---|---|---|
| **VALUE** (y-data) | **0.0050505** | 0.0006848 | 1.748e-05 | 0.0050505 | **C (floor)** | DETECT band OK; bias 0.0002651 ≤ u_read — **all passed** |
| **POSITION** (x-data) | 0.0027778 (candidate) | 0.00265761 (0.957 px) | 1.36e-07 | 0.0027778 | **C (floor)** | **PLANT-NULL REFUSED**: 1.167 px > floor |

VALUE steep-region syn_rms **0.001999 = 2.92× the whole-curve** — `§28.5`
vindicated: a read in a locally steep region is ~3× worse, and a steep read must
use the steep statistic.

## THE FINDING — a pixel floor is a floor on RESOLUTION, not on the reader's ERROR

The pre-registration predicted (`§5`, "A and B < C") that `u_read ≈ pixel floor`
for both quantities. **The prediction held for both — and for POSITION that is
precisely the failure.** The pixel floor (1.000 px) sits **below** the
steepest-descent locator's own demonstrated per-plate error: mean **0.843 px**,
**max 1.693 px**, the null-control plate **1.167 px**. A `u_read` pinned to the
pixel floor is therefore **optimistic** — it claims a precision the locator does
not have on a clean plate — and the planted null refused rather than certify it.

> **The prediction holding is what exposed the unsafe floor.** A pixel floor
> bounds how finely the raster can be read; it says nothing about how well *this
> reader* locates *this feature*. When the reader's demonstrated error exceeds the
> floor, a floor-dominated `u_read` is a false precision, and only a planted null
> tied to a known-zero answer can catch it — a `max`/high-percentile statistic
> would not have been caught by inspection.

## Cost (rule 12)

Filed **0.1 core-min**, cap **0.3** (~3× per `§26.2`/`§28.7`). Authorised run
**6.770 s = 0.1128 core-min** single core; supervisor reproduction 6.009 s =
0.1002. **Under cap, no overrun.** Actual/filed 1.13×; the gap is Python +
numpy/PIL import startup (~1.5 s) not in the warm per-op basis — attributed to
startup, **not per-op misprediction**. Calibration row in `docs/COST_CALIBRATION.md`.

## Disposition — re-file, ruled at charter v1.24 §29

The instrument is **re-filed for POSITION**; VALUE's calibration is sound and is
carried into the re-file as a separately-registered quantity rather than
quietly certified here (a `NOT A RESULT` task is not softened by carving out its
clean limb). The POSITION fix is a **conservative synthetic-control statistic**
(`u_read ≥` the worst demonstrated plate), per `§29`. **This task's
`NOT A RESULT` is permanent; the re-file is a new registration.**
