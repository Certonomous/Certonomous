# Mega-batch physics upgrade: new hard-physics solver families

Added to `sdk/workflows/mega_batch.py` (design space + dispatch) plus two new
modules it imports: `sdk/workflows/transonic_airfoil.py` (new, Family 2) and
`sdk/workflows/cylinder_vortex_shedding.py` (pre-existing prior work, reused
for Family 1). Every number below was measured on this box; none is
estimated or carried over from documentation elsewhere.

Every family still follows the existing hard requirements: `design_for_index`
for the design space, `run_task` dispatch, one JSON ledger line per
evaluation via `append_ledger`, and the case directory `shutil.rmtree`'d
immediately after metrics are extracted -- no meshes or fields are kept.

---

## Family 1 -- unsteady 2D vortex shedding (SHIPPED)

**Solver**: `pimpleFoam`, laminar, 2D circular cylinder, O-grid annulus mesh
(reused verbatim from `sdk/workflows/cylinder_vortex_shedding.py`, prior
work this task built on).

**Design space** (`solver = "openfoam-cylinder-unsteady"`): Reynolds number
uniform in [100, 1000] -- genuinely shedding, well above the pre-existing
steady family's Re <= 45 cap (chosen there specifically so simpleFoam always
converges; Re ~ 40 is roughly where shedding *begins*). Diameter and
freestream velocity are fixed at 1; kinematic viscosity is derived from Re.

**Mesh / batch parameters** (locked in after the validation runs below):
farfield 15 diameters, `n_radial=45`, `n_tangential=48` (8640 cells),
wall-normal first cell `0.01D` for Re <= 200, tightened to
`0.01D * sqrt(200/Re)` above 200 (thinner boundary layer at higher Re).
`end_time = 90` (non-dimensional time units, i.e. 90 convective units --
the bounded cap recorded in every ledger row as `end_time_cap`), adaptive
timestep (`maxCo = 1.5`) seeded from `dt0 = 0.005 * min(1, 200/Re)`.

**Learned metrics per row**: `reynolds`, `cells`, `end_time_cap`,
`perturbation`, `steps`, `cd_mean`, `cd_band`, `cd_relative_drift`,
`cl_mean`, `cl_band`, `period`, `strouhal`, `strouhal_roshko_ref`,
`strouhal_deviation_pct`.

**Stationarity gate (non-negotiable, reused verbatim)**: `halves_drift` on
Cd over the averaging window `[0.5*end_time, end_time]` must be <= 10% or
the row is refused (`ok=False`) rather than reporting a mid-transient
snapshot as a converged Cd/St -- the same gate the NACA 0012 transient
defect (commit 6606434) added.

### The one real fix this family needed

The module's own demo default (a 0.02 cross-stream perturbation on the
initial condition, meant to seed the shedding instability) does not reach
the shedding limit cycle within a batch-sized run:

| Re | perturbation | end_time | Cl at final sample | verdict |
|----|--------------|----------|---------------------|---------|
| 100 | 0.02 | 60 | still rising every sample (0.0596 -> 0.0948 over the last 0.5 time units) | **not stationary** -- Cl amplitude still growing, not a limit cycle |

Raising the perturbation to 0.1 (still small relative to `U=1`) reaches the
limit cycle inside the batch's time budget. `end_time` and drift tolerance
were then tuned:

| Re | perturbation | end_time | St measured | St = 0.198(1-19.7/Re) | deviation | Cd_mean | drift | wall time |
|----|------|------|--------|--------|------|--------|-------|-------|
| 100 | 0.1 | 70 | 0.1493 | 0.1589 | 6.0% | 1.238 | 6.5% | 197 s |
| 100 | 0.1 | **90** | **0.1578** | 0.1589 | **0.7%** | 1.285 | 3.9% | 265 s |
| 150 | 0.1 | 90 | 0.1777 | 0.1720 | 3.3% | 1.284 | 1.3% | 286 s |
| 180 | 0.1 | 70 | 0.1844 | 0.1763 | 4.6% | 1.271 | 2.7% | 232 s |

`end_time=90` was locked in for the batch (the extra 20 time units over the
70-unit run measurably tightens both the drift and the Strouhal deviation).

### VALIDATION GATE RESULT: PASS

All three Re = 100-180 runs land within **0.7-4.6%** of the Roshko/Williamson
correlation `St ~ 0.198*(1 - 19.7/Re)` (the exact form given in this task's
gate), all with stationarity drift under 3.9%. Mean Cd (1.27-1.29) is also
consistent with the classical Re=100 compilations (Henderson 1995, Cd~1.35;
numerous CFD benchmarks converge on 1.3-1.4) cited in
`cylinder_vortex_shedding.py`'s own docstring.

**Measured cost**: ~230-290 s (about 4-5 minutes) per evaluation, single
core -- "low minutes," as the task's bound requires.

**Above Re 200** (up to the design space's 1000 cap): NOT independently
validated. Real circular-cylinder wakes become three-dimensional above
Re ~ 189 (Williamson 1996); a 2D laminar solve above that Re is a genuine,
honestly-labelled numerical idealization, not a claim of matching a real
(3D, eventually turbulent) wake. The first-cell scaling keeps the boundary
layer nominally resolved, but no Re > 200 run was checked against a
published St/Cd number in this task.

---

## Family 2 -- transonic NACA0012 (SHIPPED, with a documented substitution)

**Solver**: `rhoSimpleFoam` (compressible, steady SIMPLE), `kOmegaSST`,
perfect-gas air, constant transport viscosity.

**Geometry substitution -- NACA0012, not RAE2822**: the task allowed either.
RAE2822 Case 9 (M=0.734, alpha=2.79 deg, Re=6.5e6, attached) and Case 10
(M=0.754, alpha=2.57 deg, Re=6.2e6, shock-separated) flow conditions are
corroborated across independent web sources, but this task did not turn up
a citable, directly fetchable **digitized Cp/shock dataset** for RAE2822
within its effort budget (the historical `turbmodels.larc.nasa.gov` /
`tmbwg.github.io/turbmodels` RAE2822 page could not be located live; the
site's NACA0012 page only covers a M=0.15 low-speed case). Per the task's
own instruction ("if you cannot find a citable reference, say so and do not
claim validation"), **no RAE2822 quantitative comparison is made anywhere**.
NACA0012 was used instead: it is exact and analytic (no coordinate-table
risk), and its M=0.8/alpha=1.25 deg transonic case is one of the most
widely reproduced two-shock CFD benchmarks in the literature (confirmed via
web search: inviscid solutions place a strong suction-side shock near
x/c ~ 0.60 and a weak pressure-side shock near x/c ~ 0.35).

**Design space** (`solver = "rhosimplefoam-naca0012-transonic"`): Mach
uniform in [0.70, 0.85], angle of attack uniform in [0, 3] deg, Reynolds
uniform in [3e6, 7e6] (bracketing RAE2822 Case 9/10's Re, applied to the
NACA0012 geometry -- not a claim that Case 9/10's Cl/Cd apply to a different
airfoil).

**Mesh**: O-grid, LE/TE-clustered spline surface (`naca_thickness` /
`naca_surface_points`, imported unchanged from `tmr_verification.py` --
these are pure geometry, independent of compressible vs. incompressible
flow). Cell counts reused from `tmr_verification.NACA_LEVELS[0]` ("coarse":
16 quarter-surface x 24 wake x 32 wall-normal = 3584 cells). **Domain size
was NOT reused**: `tmr_verification.naca_blockmesh_dict`'s fixed 500-chord
farfield/wake (tuned for its incompressible point-vortex-corrected lift
case) produced ~2.8e7-aspect-ratio wake cells that are tolerable for
pressure-based incompressible solving but crashed `rhoSimpleFoam` within 3
iterations here (`FOAM FATAL ERROR: Negative initial temperature T0:
-75.13`, measured). `transonic_airfoil.py` regenerates the same topology at
a 25-chord farfield/wake instead (standard practice for a
characteristic/freestream far boundary in external transonic flow), keeping
the wall-normal first cell at 8e-6 chords (y+ << 1 target, unchanged).

**Solver setup**: fvSchemes/fvSolution/thermophysicalProperties pattern
follow OpenFOAM's own stock tutorial
`$FOAM_TUTORIALS/compressible/rhoSimpleFoam/aerofoilNACA0012` (perfect-gas
air, `hePsiThermo`/`hConstThermo`, `kOmegaSST`, `bounded Gauss linearUpwind
limited` divergence schemes), adapted to this O-grid's `airfoil`/`inflow`/
`outflow` patch names in place of the tutorial's `wall`/`freestream` pair.

### Two real bugs found and fixed during validation

1. **Instability**: the tutorial's own relaxation factors (U=0.3, p=0.7,
   e/k/omega=0.7) combined with `nNonOrthogonalCorrectors=0` produced an
   **unbounded Cd oscillation** on this mesh -- measured Cd cycling between
   -2.2 and +2.8 with no decay across 2000 iterations (mesh non-orthogonality
   measured up to 70.3 deg, 66 severely non-orthogonal faces). Fix: softer
   relaxation (U=0.15, p=0.3, e/k/omega=0.3) and `nNonOrthogonalCorrectors=2`
   -- Cd then settles to a tight band (spread ~0.001) within 2000 iterations.
2. **Aref bug**: `Aref` was initially set to `chord * 0.1` (copied from the
   incompressible cylinder case's 0.1-chord span convention), but this
   airfoil mesh's actual depth is 1.0 chord (`z: 0 -> 1` in the O-grid).
   Measured effect: Cd read 0.432 and Cl read 1.09 at M=0.8/alpha=1.25 --
   **exactly 10x** the physically expected Cd~0.04/Cl~0.11. Fixed to
   `Aref = chord * 1.0`.
3. **Pressure/friction split source**: the `coefficient.dat` file's
   `Cd(f)`/`Cd(r)` columns do NOT correspond to pressure/viscous for this
   solver (measured: they sum to Cd, but a printed value of `Cd(f)=-0.33`
   does not match the solver log's own `Coefficient Total Pressure Viscous`
   table, which gave `Viscous=+0.063` for the same iterate -- these are
   evidently some other decomposition, e.g. a geometric front/rear split).
   The pressure/viscous split reported (`cd_pressure`, `cd_viscous`) is
   parsed from the solver log's table instead (`parse_force_split`, reused
   unchanged from `tmr_verification.py`), which is unambiguous.

### VALIDATION GATE RESULT: PASS (banded, shock position)

Primary case: **M=0.8, alpha=1.25 deg, Re=6e6**, 2000 iterations, 33.8 s
wall time, converged (Cd spread 0.00093):

- Cd = 0.0432 (pressure 0.0369 + viscous 0.0063), Cl = 0.109 -- both
  physically sane orders of magnitude for a thin symmetric airfoil at this
  condition.
- **Upper-surface (suction-side) shock at x/c = 0.556**, found as the
  steepest positive dCp/dx recompression in the sampled surface-pressure
  raw output.
- Reference: the inviscid AGARD/GAMM two-shock benchmark for this exact
  (M, alpha) places the suction-side shock near x/c ~ 0.60. Our **viscous**
  RANS result at 0.556 falls inside a 0.35-0.60 chord band anchored on that
  number, and sits slightly *upstream* of the inviscid 0.60 -- the direction
  a real shock/turbulent-boundary-layer interaction is expected to shift it.
  **This is a banded, qualitative pass, not a point Cp match, and is
  reported as such.**
- The lower-surface "shock" the same algorithm reports (x/c = 0.608) is
  **not gated / not trusted**: at positive incidence the pressure side may
  not carry a genuine shock at all (the inviscid weak shock there is a
  near-zero-lift feature), and the steepest-slope heuristic can just as
  easily flag ordinary trailing-edge recompression. Reported for
  completeness only.

Secondary run (physics coverage, not RAE2822 validation): **M=0.734,
alpha=2.79 deg, Re=6.5e6** (RAE2822 Case 9's flow numbers, applied to our
NACA0012 geometry -- Cd/Cl are NOT compared to Case 9's published values
since the airfoil is different): Cd=0.0405, Cl=0.386, upper shock
x/c=0.556, 26.3 s.

**Measured cost**: 26-34 s per evaluation, single core (2000 SIMPLE
iterations, 3584 cells) -- well inside the seconds-to-low-minutes bound,
and far cheaper than Family 1.

---

## Family 3 -- very high Reynolds flat-plate Cf (DEFERRED)

Not shipped in this task ("if time allows" -- it did not). What it needs,
concretely, building on infrastructure that already exists and is already
validated in this repo:

- `sdk/workflows/tmr_verification.py` already runs and validates a
  zero-pressure-gradient flat-plate `simpleFoam` + `kOmegaSST` case against
  published CFL3D/FUN3D grid-convergence data (`CFL3D_SST_V`,
  `FUN3D_SST_V`, keyed by cell count, at the TMR's Cf-reporting station
  `x=0.970084071`) -- this is exactly Family 3's validation gate, already
  built, just fixed at Re = 5e6/unit-length (Re_x = 1e7 at the trailing
  edge) rather than varying 1e6-1e7 as the task asks.
- To vary Reynolds per design, `transport_properties(nu=...)` is already
  parameterized, but `initial_fields()` is not -- `K_INF`/`OMEGA_INF` are
  derived from the fixed module-level `NU = 2e-7` at import time. A
  Family-3 wrapper would need its own per-Re turbulence-inlet calculation
  (same formula, `k = 9e-9*a^2`, `omega = 1e-6*a^2/nu`, TMR's own
  freestream spec) rather than reusing `initial_fields()` directly.
- The smallest TMR rung (`GridLevel` "coarse", 816 cells, `ITERATIONS=3000`)
  is the natural batch-sized starting point, but that iteration count is
  tuned for verification-grade flatness, not batch throughput -- it would
  need its own measured convergence check (almost certainly can be cut
  substantially, unmeasured here).
- Cf-station extraction (`parse_wall_shear_raw`, `cf_at`) and the yPlus
  function object are already wired into `control_dict`'s `functions{}`
  block and would work unchanged.

---

## Family F10 -- 3D viscous RANS, Ahmed body (SHIPPED)

Added under directive D7. Closes this batch's only-3D-family-is-inviscid
gap: `vspaero-wing` is a vortex-lattice panel method with no boundary layer
and no Reynolds number; F10 (`solver = "simplefoam-ahmed-3d-viscous"`) is
`simpleFoam`, k-omega SST, wall functions, a real `snappyHexMesh` surface
mesh -- the batch's first genuinely 3D **viscous** family. It promotes the
already-VALIDATED `mission-output/geometry-study/study-ahmed_25` body (not
a rebuild) into the batch's design-space/gate/ledger pattern.

**Design space**: Ahmed body slant angle (25 deg / 35 deg, discrete
geometry axis) x Reynolds 1.5e6-4.0e6 (flow-condition axis). 1/12 weight.

**Quality gates** (all four measured and checked per row, non-negotiable):
checkMesh verdict + non-orthogonality/skewness, y+ band [30, 500], SIMPLE
residual <= 1e-4 on Ux/Uy/Uz/p, and Cd stationarity (halves-drift <= 10%,
same discipline as Family 1).

**Validation gate: PASS** at 25 deg -- Cd (frontal-area basis) 0.32284 vs.
Ahmed/Ramm/Faltin 1984 SAE 840300's 0.285, 13.28% off, inside the +-15%
band. The 35 deg point (20.94% off) documents the same pre-existing
TREND-ONLY miss this repo already had on record for that geometry.

**Measured cost**: ~34-35 s per evaluation (single core, ~0.58 core-min) --
cheaper than Family 1 (unsteady cylinder, ~394 s) and only slightly more
than Family 2 (transonic airfoil, ~30 s).

Full design-space rationale, gate derivations, the two real end-to-end test
evaluations, cost-ratio table against every other family, and the answers
to the standing mesh-resolution / 2D-vs-3D / cost-ratio learning questions
are in `F10_3D_VISCOUS_FAMILY.md` (this directory).

---

## Explicitly out of scope (queued separately, per instruction)

- **Hypersonic** (`rhoCentralFoam`): would need a density-based
  shock-capturing central scheme (not `rhoSimpleFoam`'s pressure-based
  SIMPLE), almost certainly a Sutherland (not constant) transport model,
  careful bow-shock-standoff mesh resolution, and a citable hypersonic
  reference (a blunt-body/cone shock-standoff correlation or a published
  Cp/heat-flux dataset) for its own validation gate.
- **Heart valve**: the batch's existing `reduced-order` family is a
  cycle-decomposition orifice screen, not a solve. A hard-physics valve
  family would need real leaflet geometry and either a moving-mesh or
  immersed-boundary unsteady 3D solve -- a much larger step up than either
  family shipped here.
