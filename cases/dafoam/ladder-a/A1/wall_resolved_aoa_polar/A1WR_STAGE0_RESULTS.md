# A1WR STAGE 0 — MESH FAMILY BUILT — MEASURED RESULTS

Governed by `A1WR_PREREGISTRATION.md` v1.1 (amendment 1). Instrument:
`a1wr_build_stage0.sh`, generator `a1wr_genmesh.py` pinned to its frozen blob
`1dc36a588b473cd22ef240260bfb081731c22fcb` **and verified bit-identical in the
run root before the build** (rule 2 freeze verification).

**Artifacts on disk:** `/home/ubuntu/certonomous-runs/A1WR/STAGE0.log` and, per
level, `/home/ubuntu/certonomous-runs/A1WR/<L>/log.{genmesh,plot3dToFoam,autoPatch,createPatch,renumberMesh,checkMesh}`.

**Cost: 0.4000 core-min measured (24 s wall × 1 rank), against a registered cap
of 40. actual/cap = 0.0100. WITHIN CAP.** Ratio actual/predicted vs the ≤40
registered estimate is 0.010 — the mesh build was **over-estimated by ~100×**;
attribution is misprediction, not contention (pyHyp marching is near-linear and
far cheaper than the plot3d/renumber overhead I budgeted for). Calibration row
owed to `docs/COST_CALIBRATION.md`.

## 1. MEASURED, NOT PREDICTED

| level | cells | wall faces | s0 | implied growth | checkMesh non-orth max / avg | max skewness |
|---|---|---|---|---|---|---|
| L1 | **8,064** | 126 | 2.5e-6 | 1.25483 | 40.000 / 3.648 | 1.573 |
| L2 | **32,640** | 255 | 1.25e-6 | 1.11964 | 31.872 / 2.550 | 1.443 |
| L3 | **130,304** | 509 | 6.25e-7 | 1.05800 | 31.503 / 1.710 | 1.397 |

Generator selfcheck rc 0; every `genmesh` rc 0; growth ratios all under the
registered 1.35 ceiling, applied **before** each build proceeded.

**The refinement ratio is CONFIRMED BY MEASUREMENT, not by construction:** wall
faces 126 → 255 → 509 give ratios **2.024 / 1.996** against a registered r = 2,
and cells 8,064 → 32,640 → 130,304 give **4.048 / 3.992** against the r² = 4 a
2-D family must show. The ladder is a real ladder.

**`wing` is `type wall` on all three levels** (read from each
`constant/polyMesh/boundary`, not assumed). This was the registered trap: DAFoam's
`useWallFunction: False` branch fires only on `type wall` patches, so a mistyped
patch would have made the wall-resolved setting a **silent no-op**. It did not bite.

Predicted L3 cell count was "of order 1.3e5"; measured **130,304**.

## 2. ⚠ A RED THAT IS NOT WAVED THROUGH: `Failed 1 mesh checks` ON ALL THREE LEVELS

`checkMesh` reports **`Failed 1 mesh checks`** at every level — the high
aspect-ratio check. **Max aspect ratio 53,540.9 / 104,245.8 / 212,103.7.**

**`checkMesh` nonetheless exits rc 0.** A grader keying on the exit code alone
would have recorded these meshes as clean. The rc and the verdict line are
different instruments and the log line is the binding one.

**This is NEW to the wall-resolved family and is not a standing property of the
case.** The existing coarse baseline was re-checked for this comparison and
returns **`Mesh OK`, max aspect ratio 97.87**.

**Origin, MEASURED rather than argued:** the aspect ratio tracks 1/s0 exactly —
level-to-level factors **1.947 and 2.035**, against s0 halving each level — while
the **in-plane** ratio dx/dy is **constant at 2,000 across all three levels by
construction** (both dx and dy scale as 1/R). An in-plane cause would leave AR
flat; a spanwise cause doubles it per level. The observed behaviour is the
spanwise one: span/s0 = 40,000 / 80,000 / 160,000, the same doubling.

So the extreme AR lives in the **z direction, which carries `symmetry` on both
faces and one cell**, i.e. the direction with no gradient in a 2-D case. That is
an argument for the flag being benign, **not a demonstration that it is**, and it
is recorded as such:

- **Recommended, pending the supervisor's call:** reduce `ZSpan` from 0.1 so the
  span cell is comparable to the in-plane cell, which would cut AR by the same
  factor. **`A0` must move with it** — `A0 = 0.1` is a reference *area* equal to
  chord × span, so CD/CL stay numerically identical only if both change together.
  Changed consistently, the comparison against the coarse sweeps is preserved.
- **Not done unilaterally**, because it touches the force-scaling constant in
  both run scripts.

**Stage 1 is NOT launched on this question's answer being assumed.**
