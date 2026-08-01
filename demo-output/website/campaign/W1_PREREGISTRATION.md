# W1 pre-registration — bump SST on NASA's own grids

Written and committed **before any solve on NASA's grids was launched**
(2026-08-01). Approved item `w1-bump-on-nasa-own-grids`, 180 core-min.

## The question

4G section 10.4 measured that on our blockMesh bump family the pressure
component of Cd has **no observed order** — its grid-to-grid increments change
sign at every matched iteration count — while CFL3D on NASA's own grids gets
p = 2.914 on that same component for the same case. This item swaps exactly one
thing: the mesh. NASA's point-dropped family (verified `[::2,::2]` exact,
`models/tmr/bump/grids/PROVENANCE.md`) replaces our blockMesh family. Solver,
numerics, BCs, tolerances are the ones the published `bump_sst.json` runs used
(`sdk/workflows/tmr_verification.py`: same fvSchemes, fvSolution, 0/ fields,
forceCoeffs with Aref = lRef = 1.5).

## Decision rules, stated before the runs

Let the three rungs be NASA 89x41 / 177x81 / 353x161 (3,520 / 14,080 / 56,320
cells — the same counts as our rungs and CFL3D's three coarsest). All values are
read at **settled** states per `tmr_verification.SETTLE_TOL`: peak-to-peak of
the Cd history <= 3e-7 over the trailing `settle_window(n)` iterations. A rung
stopped by its backstop (`iteration_backstop(cells)`) is recorded **unsettled**,
never converged.

1. **"Our mesh was the problem"** requires, on NASA's grids: the pressure-drag
   increments (cdp_medium - cdp_coarse, cdp_fine - cdp_medium) are **monotone
   (same sign)**, and `uq.eca_hoekstra_band(dim=2)` on the cdp ladder returns a
   finite observed order. Direction of the recovery matters: CFL3D's cdp falls
   from 1.479e-3 toward 4.316e-4 across these grids, so a mesh-was-the-problem
   outcome should also move our coarse-grid cdp toward CFL3D's coarse-grid
   value (i.e., the coarse rung stops "landing near the answer for a reason
   that is not convergence").
2. **"The case is the problem"** (our solver/discretization/incompressible
   analog, not our mesh): the cdp increments **still change sign** at settled
   states on NASA's grids — the defect follows the solver onto grids where
   CFL3D achieves p = 2.914. That is a real negative finding about the solver
   setup and ships as such.
3. **Partial/ambiguous** outcomes are recorded as partial, with
   `uq.not_conclusive_reason` quoted: e.g. monotone cdp but a divergent
   extrapolation, or a recovered cdp order alongside a still-refused total.
   No re-classification after the fact into 1 or 2.

Secondary, same rules: cdv (viscous) fitted with `eca_hoekstra_band(dim=2)`
(it had p ≈ 1.09 on our meshes — it should not get worse); total Cd fitted
likewise and graded against CFL3D's matched-grid ladder (0.0045618542592,
0.0037071442412, 0.0036071373739) whose own order on these rungs is 3.095.

Nothing is extrapolated from an unsettled trajectory; `reportable_band` /
`not_conclusive_reason` are read through the helpers, never `band_abs` raw.

## Budget arithmetic (from measured s/iter on this box, bump_sst.json timings)

| rung | cells | s/iter serial (measured) | backstop | worst-case | flat-plate settle-cost prediction |
|---|---|---|---|---|---|
| 89x41 | 3,520 | 0.0247 | 3,000 | 1 core-min | ~1 core-min |
| 177x81 | 14,080 | 0.1354 | 5,000 | 11 core-min | ~7 core-min |
| 353x161 | 56,320 | 0.7905 | 17,000 | 224 core-min | ~109 core-min |
| 705x321 | 225,280 | ~4.6 (extrapolated) | 67,000 | ~5,150 core-min | ~2,550 core-min |
| 1409x641 | 901,120 | ~27 (extrapolated) | 266,000 | ~119,000 core-min | ~59,500 core-min |

So: the finest affordable rung is **353x161**. The 705x321 is ~14x the whole
180 core-min budget at its settle-cost prediction and is not attempted; the
1409x641 is out by ~330x. Expected total for the three rungs ~117 core-min if
they settle near the flat plate's measured settle cost; the 353x161 running to
its backstop would overrun the budget (~236 total) and will be recorded as the
overrun it is, not smoothed. Rungs run sequentially, never in parallel with
each other.

## Held-out predictions (for honesty, not scoring)

- NASA's coarse grid has 40 cells on the wall vs our 64 and first spacing
  8.06e-6 vs our 5e-6, so our-on-NASA coarse Cd will differ from our published
  coarse Cd by more than the settle tolerance.
- If outcome 1 obtains, the total-Cd ladder should turn non-monotone-in-doubt
  into a falling-toward-CFL3D shape (CFL3D's ladder falls monotonically).
