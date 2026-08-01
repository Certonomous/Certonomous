# W1 — Bump SST on NASA's own grids

Approved item `w1-bump-on-nasa-own-grids` (180 core-min). Pre-registered
before any solve in `W1_PREREGISTRATION.md` (committed 3e252b5c). Everything
below is measured; every number cites a file under `W1_runs/`,
`models/tmr/bump/grids/`, or `demo-output/website/tmr/`.

The question, from 4G section 10.4: on our blockMesh bump family the pressure
component of Cd has no observed order (its increments change sign at every
matched iteration count), while CFL3D achieves p = 2.914 on that component on
NASA's own grids. This item swaps exactly one thing — the mesh — and asks
whether the pressure order comes back.

## 1. Grid provenance

Full byte provenance in `models/tmr/bump/grids/PROVENANCE.md` (commit
1b5749f0). In short: the two grids fetched on 2026-07-31 from the
tmbwg.github.io mirror decompress byte-identically to NASA's own distribution
zip (`nasa.gov/wp-content/uploads/2026/02/bumpgrids-grids.zip`, sha256
recorded); the 353x161 the mirror could not serve (git-lfs pointers, media
endpoint 404) was extracted from that zip unmodified, as were the 177x81
p3dfmt and the 705x321. Nothing was regenerated.

Measured from the node arrays (`W1_runs/read_p3d.py`):

- **Point-drop is exact**: 89x41 = 177x81[::2,::2], 177x81 = 353x161[::2,::2],
  353x161 = 705x321[::2,::2], all to max |delta| = 0.0 in both coordinates.
  The family has one h and refinement ratio exactly 2 — the "no single h"
  defect of our blockMesh family (wall-cell ratios 0.5337 / 0.5167) is gone
  by construction.
- First wall-normal spacing at x = 0.75: 8.05762e-6 / 3.97693e-6 / 1.98201e-6,
  near-exact halving; NASA relaxes it 400x along the symmetry extensions.

## 2. Conversion, and the like-for-like mesh table

Converted by `W1_runs/p3d_to_polymesh.py`: a direct structured-to-polyMesh
writer that uses NASA's node coordinates exactly as read (no rotation, no
shape-matching), with patches assigned by index (wall = bottom faces with
face-center x in (0, 1.5)). Validated three independent ways:

1. On the 89x41 it reproduces the plot3dToFoam-converted mesh to seven
   figures on every checkMesh metric (`log.checkMesh.coarse` vs
   `log.checkMesh.coarse.plot3dToFoam-route`: max AR 4844.490207 vs
   4844.4902, non-ortho 63.95852861 vs 63.95852703).
2. An exact-centroid recomputation of non-orthogonality from the raw node
   arrays returns 63.9585 / 30.2189 / 12.7526 for the three rungs — matching
   checkMesh on the converter's meshes to every printed digit.
3. plot3dToFoam cross-runs on the 177x81 and 353x161
   (`log.checkMesh.{medium,fine}.plot3dToFoam-crosscheck`) agree on the
   medium (30.2189); the fine crosscheck reads 13.1976 only because that
   route rotates the mesh with transformPoints (cos(-90deg) = 2.2e-16
   roundoff); the direct converter never rotates.

A false trail, kept on the record: the first conversion attempt
(plot3dToFoam + box-based topoSet/createPatch) produced two open cells and
two spurious 89.5-degree faces on the medium and fine rungs. That was this
session's patch-splitting bug — the corner inlet faces on those rungs have
centers below y = 0.001 and landed in two faceSets, so createPatch duplicated
them — not a plot3dToFoam defect and not a grid defect. The index-based
converter eliminates the failure mode.

### The table the item asked for (checkMesh, identical cell counts)

| rung | cells | max aspect ratio, NASA grid | max AR, our blockMesh | max non-ortho, NASA | ours | max skew, NASA | ours |
|---|---|---|---|---|---|---|---|
| 89x41 | 3,520 | **4,844.5** | 2,136,801 | 63.96 | 12.77 | 0.175 | 0.072 |
| 177x81 | 14,080 | **5,210.2** | 2,192,933 | 30.22 | 12.92 | 0.132 | 0.036 |
| 353x161 | 56,320 | **5,277.7** | 2,218,683 | 12.75 | 13.48 | 0.132 | 0.018 |

Sources: `W1_runs/mesh/log.checkMesh.*` (NASA grids, this session) and
`demo-output/website/tmr/runs/bump-*/log.checkMesh` (ours). The only failed
check on NASA's meshes is the same AR > 1,000 advisory ours trip. NASA's
grids trade a 400x larger aspect-ratio ceiling for real non-orthogonality on
the coarse rungs (63.96 degrees at the wall-spacing transition just upstream
of x = 0, improving to 12.75 under refinement, where ours is flat ~13); both
are inside what the corrected-Laplacian numerics handle.

## 3. Per-rung solves

Same solver, numerics, BCs, tolerances as the published `bump_sst.json` runs
(`tmr_verification.py`: simpleFoam incompressible, kOmegaSST strain-production,
linearUpwind momentum / upwind turbulence advection, Aref = lRef = 1.5).
Every rung is driven by the settle criterion — `settle_verdict`'s peak-to-peak
<= 3e-7 over the trailing `settle_window` — with `iteration_backstop(cells)`
as the initial cap and documented restarts to chase settle past it. A rung is
only quoted at a settled state.

| rung | start | settled at iteration | window | peak-to-peak at stop | Cd | Cd pressure | Cd viscous | y+ max (bump) | Cf(0.75) |
|---|---|---|---|---|---|---|---|---|---|
| 89x41 | impulsive | **5,288** | 1,322 | 1.50e-7 | 0.0042264331 | 1.18634e-3 | 3.04009e-3 | 0.758 | 5.35498e-3 |
| 177x81 | impulsive | **16,000** | 2,000 | 6.81e-8 | 0.0035977232 | 4.61383e-4 | 3.13634e-3 | 0.429 | 5.71841e-3 |
| 353x161 | seeded from settled 177x81 (mapFields) | *running* | | | | | | | |

Evidence: `W1_runs/{coarse,medium}/collected.json`, full Cd histories under
`W1_runs/*/postProcessing/forceCoeffs1/`, solver logs gzipped beside them.

Incidents, recorded rather than smoothed:

- The coarse and medium backstops (3,000 / 5,000 from `iteration_backstop`)
  both stopped their rungs unsettled (spreads 9.6e-7 / 1.8e-6); both rungs
  were continued by restart to settle. The backstop formula is calibrated on
  the flat plate at 0.147 iterations/cell; the bump needs 1.5 (coarse) to
  1.14 (medium) iterations/cell — 8-10x the flat plate — so for this case the
  formula's caps are floors, not generous bounds.
- One medium continuation was killed by an external SIGTERM at ~100 s
  (log ends mid-iteration, no error, no OOM, `journalctl` empty) — the same
  unexplained termination signature 4G section 10.3 recorded on its fine
  re-run at iteration 10,098. Detaching the driver with setsid avoided it;
  cause still unidentified.
- OpenFOAM renames a restart's force-coefficient output to
  `coefficient_<time>.dat` when the file exists, so a watcher reading only
  `coefficient.dat` goes blind after a restart-over-restart. The medium rung
  consequently overran its settle point by ~2,500 iterations (~2 core-min,
  charged to the budget). The driver now stitches histories keyed by
  iteration number (`W1_runs/stitch.py`).
- The medium rung's 10,001-12,000 range was solved twice (restart replay
  after the SIGTERM kill); the two trajectories agree row-for-row where they
  overlap, so the replay changed nothing downstream.
- The 353x161 rung is seeded from the medium's settled fields via
  `mapFields -consistent` (established lab practice, cf. the seeded NACA
  t-a10 rung). Budget arithmetic forced it: measured settle costs on the
  first two rungs extrapolate an impulsive fine rung to ~34,000 iterations
  (~360 core-min), double the whole item budget. Seeding changes only the
  initial transient; the settle criterion certifies the endpoint state
  regardless of path.
