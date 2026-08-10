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
| 353x161 | seeded from settled 177x81 (mapFields) | **26,996** | 2,000 | 3.00e-7 | 0.0035594313 | 3.825191e-4 | 3.176912e-3 | 0.255 | 5.86703e-3 |

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

## 4. Seed-independence control (added 2026-08-02)

The fine rung is seeded from the medium's settled fields by `mapFields
-consistent` while the coarse and medium rungs start impulsively, so the ladder
mixes initial conditions across its rungs. Section 3 asserted that this is
harmless — *"the settle criterion certifies the endpoint state regardless of
path"* — and asserting it was the weakest line in this document, particularly in
a week when the lab has been finding ladders that change a knob between rungs.

**It is now measured, on this case family, for 1.17 core-minutes.** The coarse
rung was re-solved from the medium's settled field at iteration 16,000 mapped
down onto its 3,520 cells (`coarse-seeded/log.mapFields`), against the same
settle criterion. Prediction recorded before the run: if seeding does not change
the settled answer, it returns the impulsive rung's Cd to within the 3e-07
settle tolerance.

| | iterations | Cd | Cd pressure | settle spread | core-min | cells/rank |
|---|---|---|---|---|---|---|
| coarse, impulsive | 5,288 | 0.0042264331 | 1.18634078e-3 | 1.50e-07 | 1.33 | 3,520 (1 rank) |
| coarse, seeded from medium | 4,828 | 0.0042264581 | 1.186360357e-3 | 2.30e-07 | 1.17 | 3,520 (1 rank) |
| **difference** | −460 | **2.50e-08** | **1.96e-08** | | | |

**The prediction holds.** The two paths agree to 2.50e-08 in total Cd — **8.3%
of the settle tolerance**, 0.0006% relative, and smaller than either rung's own
peak-to-peak spread. On the pressure component, which is the quantity this whole
item exists to measure, they agree to 1.96e-08. The seeded provenance of the
fine rung does not compromise the ladder.

**One rank, deliberately.** 3,520 cells over four ranks would be 880 cells/rank,
far below the 5,600 cells/rank inversion point, so parallel would cost more
core-minutes and buy nothing.

**And an unplanned finding that contradicts this document's own budget
argument.** Section 3 justified seeding the fine rung on cost: an impulsive fine
rung was extrapolated at ~34,000 iterations and ~360 core-minutes, double the
item budget. The control says seeding buys far less than that implies —
**460 iterations of 5,288, or 8.7%.** The settle criterion here is dominated by
the slow tail, not by the initial transient, and a seed skips the transient
only. The fine rung's own numbers agree: seeded, it is settling near 26,700
iterations against the ~34,000 predicted impulsively, a 21% saving rather than
the factor implied. **Seeding was still the right call and it was justified for
the wrong reason**, and the corrected reason is worth carrying: seed to skip a
transient, and do not price a seed as if it halves a settle.

## 5. The reference's own ladder, put through our gate (recorded 2026-08-02 06:25 UTC, before the fine rung settled)

Written and committed **while the 353x161 rung was still running**, so it cannot
be read as a gate moved after seeing the answer. Nothing below uses our fine
rung; it uses only CFL3D's published values on these same three grids, already
stored in `tmr_verification.CFL3D_BUMP_SST`, put through
`uq.eca_hoekstra_band(dim=2)` — the same call this ladder will be graded by.

| CFL3D on 89x41 / 177x81 / 353x161 | observed order | monotone | conclusive | guard that fails |
|---|---|---|---|---|
| total Cd | 3.095 | yes | **no** | `order_window` |
| **Cd pressure** | **2.913** | yes | **no** | `order_window` |
| Cd viscous | 1.619 | yes | yes | — |
| Cf at x = 0.75 | 1.643 | yes | yes | — |

**The reference code fails our own gate on the two components it is famous for,
and passes it on the other two.** `order_window` is [0.5, 2.5] at `dim = 2`;
2.913 and 3.095 sit above it. A ladder whose observed order exceeds the formal
order of the scheme is the classic signature of not being in the asymptotic
range — superconvergence on the coarse rung, not extra accuracy.

**Two consequences, and the first is a correction to this item's own paperwork.**

1. **The docket gate as written is unreachable, and the pre-registration's is
   not.** `w1-bump-on-nasa-own-grids` states its gate as *"An observed order
   inside the theoretical range on the pressure component, on grids refined by
   point-dropping."* If our solve reproduced CFL3D **exactly**, it would return
   2.913 and be graded NOT CONCLUSIVE. The gate cannot be met by agreeing with
   the reference. `W1_PREREGISTRATION.md`, committed before any solve, is the
   careful one: its outcome 1 asks that the cdp increments be *monotone* and
   that the fit return *a finite observed order* — and says nothing about that
   order landing inside the window. **This ladder is graded against the
   pre-registration**, which is the document that was fixed first, and the
   docket gate is recorded here as over-tight rather than quietly satisfied.
2. **The question the item actually answers is still live and still worth its
   cost.** Our blockMesh ladder has *no* observed order on the pressure
   component at all — its increments change sign at every matched iteration
   count. CFL3D's has one, and it is outside the window. Those are **different
   failures**, and moving from the first to the second would be a real result:
   it would say the mesh was the problem, even while the answer stays
   not-conclusive for a second, separate reason that belongs to the grid family
   rather than to us.

The viscous component and Cf are the control in all this: the reference clears
our gate on both, so the gate is not simply too tight for everything on these
grids. It is too tight for the pressure component specifically, which is the
component whose ladder this item exists to recover.

## 6. A defect in the collector, found before it reached the finest rung

Found 2026-08-02 while checking that `collect.py` would read the fine rung's
settled state correctly. It would not have, and it had already misread the
medium rung.

**Three traps, stacked.**

1. **`postProcessing` directories are named for the run's START time**, so
   `yPlus1/0/yPlus.dat` holds the state at the *end* of the first run. Sorting
   directory names does not sort states.
2. **The y+ loop globbed unsorted** and kept the last successful parse, so the
   filesystem's directory order decided which state got published — while the
   `wallCf` loop three lines below it was sorted. One of the two was written
   carefully.
3. **OpenFOAM renames a function object's output to `<name>_<time>.dat` when the
   file already exists on restart.** This is the same restart-collision the lab
   already knows about for `coefficient.dat`, and which `stitch.py` handles for
   the force histories — but nothing handled it for y+. `yPlus1/10000/` on the
   medium rung holds a **header-only** `yPlus.dat` beside the real
   `yPlus_10000.dat`, and the collector only ever opened the former.

**What it cost.** The medium rung's published y+ was the state at iteration
**5,000**, tabulated in §3 beside a Cd from iteration **16,000**. Corrected:

| medium, y+ on the bump | published | corrected (t = 16,000) | delta |
|---|---|---|---|
| min | 0.14930690811 | 0.14927358540 | −3.33e−05 (0.022%) |
| max | 0.42879737165 | 0.42878909954 | −8.27e−06 (0.0019%) |
| average | 0.23653806350 | 0.23649763025 | −4.04e−05 (0.017%) |

Nothing else moved: Cd, its pressure/viscous split, and Cf(0.75) are unchanged,
and the coarse rung was correct all along — its published y+ was already the
settled state, reached by luck of directory order rather than by design.

**The magnitude is small and the kind is not.** A number that is right to
0.002% but describes a different iteration than the one it sits beside is the
same defect the lab has been correcting elsewhere this week, and the mechanism
that produced it was order-dependent: on a filesystem that enumerated
`yPlus1/*` differently, the same code would have published a different number
with no warning.

**Fixed in `collect.py`**: y+ is now chosen by the Time written *inside* the
file, across `yPlus*.dat` including the restart-renamed ones, and the record
carries `yplus_time`, `yplus_source` and `yplus_is_settled_state` so a reader
can check the y+ belongs to the state the Cd beside it came from. Both rungs
re-collected under the fix; both now report `yplus_is_settled_state: true`.

## 7. Result: the pressure order comes back, and the grade does not

The 353x161 rung settled at **iteration 26,996**, peak-to-peak 2.997e-07 over its
trailing 2,000 against the 3e-07 tolerance, exit 0. The continuation was
pre-registered before launch at "settles near 26,600"; it settled at 26,996,
**1.5% out**.

### The ladder, on grids that are exact point-drops of one another (r = 2, one rank throughout)

| quantity | 89x41 | 177x81 | 353x161 | increments | observed order | conclusive | guard that fails |
|---|---|---|---|---|---|---|---|
| Cd total | 4.226433e-3 | 3.597723e-3 | 3.559431e-3 | −6.287e-4, −3.829e-5 | 4.037 | no | `order_window` |
| **Cd pressure** | 1.186341e-3 | 4.613827e-4 | 3.825191e-4 | **−7.250e-4, −7.886e-5** | **3.200** | no | `order_window` |
| Cd viscous | 3.040092e-3 | 3.136341e-3 | 3.176912e-3 | +9.625e-5, +4.057e-5 | 1.246 | no | `extrapolation_sanity` |

### The item's question, answered: outcome 1, the mesh was the problem

`W1_PREREGISTRATION.md` outcome 1 asks two things of the pressure component,
and **both are met**:

1. **The increments are monotone** — both negative, −7.250e-4 then −7.886e-5.
   On our blockMesh family they *changed sign at every matched iteration count*.
   Swapping only the mesh removed that.
2. **The fit returns a finite observed order** — 3.200, where our blockMesh
   family had none at all.

> **[RESTATED 2026-08-10 under `docs/charters/VERIFICATION_CHARTER.md` §17 — no draw-scatter evidence exists at the rung this feature turns on.]** The statement above is a claim about the SHAPE of a sequence of grid-refinement increments for **NASA's bump grids**. Under the adopted rule such a claim is published only with draw-scatter evidence at the deciding rung, or with the absence of that evidence stated on its face. **No replicate mesh has ever been drawn at this ladder's deciding rung.** Recipe class per `campaign/LADDER_RECIPE_CONSISTENCY_SWEEP_2026-08-10.md`: **single-recipe (CLEAN)**, so its increments really are discretization increments and this gap is not confounded away. **This is not a withdrawal — the feature is unchecked, not shown false**; the remedy the rule specifies is exactly this sentence. Original text retained.


The direction test is met too. Against CFL3D on the same grids our pressure
component runs **−19.78%, −16.77%, −11.38%** — converging toward the reference
monotonically under refinement rather than wandering. Cf(0.75) runs +3.70%,
+1.71%, +1.70%, and the viscous component +/−1.39%, −0.52%, **+0.04%** — the
viscous drag agrees with CFL3D to four hundredths of a percent on the finest
rung.

### And the grade is still NOT CONCLUSIVE, for the reason recorded in §5 before this rung landed

`order_window` is [0.5, 2.5] and 3.200 is above it. **This was predicted and
committed while the rung was still running**: CFL3D's own pressure ladder on
these same grids fits to 2.913 and is refused by the same guard. Ours is 3.200.
Both are monotone, both are above the window, and neither is conclusive.

So the honest one-line result is: **the mesh was the problem, and the grids are
not in the asymptotic range** — two separate findings, the first ours and the
second belonging to the grid family, which the reference code shares.

The viscous component fails a different guard and it is worth naming precisely
rather than lumping it in: `extrapolation_sanity` allows the Richardson value to
sit up to `EXTRAPOLATION_TOL_FRAC = 0.15` of the fit triple's range outside it.
Ours lands **0.216** of the range above its finest rung; CFL3D's lands 0.118 and
passes. Not a bracket violation — an overshoot of the allowance by a factor 1.44.

### Cost: measured against estimate, and a correction to something this session already committed

| rung | recorded `core_minutes_cumulative` | solver `ExecutionTime`, all logs | ranks | cells/rank |
|---|---|---|---|---|
| 89x41 | 1.33 | 1.18 | 1 | 3,520 |
| 177x81 | 17.88 | **31.55** | 1 | 14,080 |
| 353x161 | 268.60 | 265.85 | 1 | 56,320 |
| 89x41 seeded control | 1.17 | 1.16 | 1 | 3,520 |
| **total** | **288.98** | **299.74** | | |

**Estimate 180 core-minutes, measured ~300 — a 66% overrun**, and it is reported
rather than netted out. One rank throughout: at 56,320 cells four ranks would be
14,080 cells/rank, still above the 5,600 inversion, but the rung was continued
serially on purpose so that a decomposition change could not perturb a
trajectory already inside its settle tolerance.

**A correction to this session's own commit `7d0f186b`.** That commit's message
says the recorded figures "sum to about 183 core-minutes against a 180 estimate,
a 2 percent overrun" while the logs "say 289". **That comparison was invalid.**
The 183 was a mid-flight subtotal taken while the fine extension was still
running, and it was set against a log total that already included that
extension. Corrected: the recorded total is **288.98** and the log total
**299.74**, and the accounting defect did *not* make the item look on budget —
the fine rung has one extension, so its cumulative chained correctly.

**The defect is still real and still worth the fix**, but its true size is this:
it under-reports the **medium** rung by 13.67 core-minutes, **43.3% of that
rung's true 31.55**, because that rung was restarted three times and only the
last extension was counted. The item-level difference of 10.76 core-minutes is
exactly that 13.67 less the driver-overhead excess on the other three rungs
(2.75 + 0.15 + 0.01). A rung restarted once is fine; a rung restarted three
times was losing two of them.
