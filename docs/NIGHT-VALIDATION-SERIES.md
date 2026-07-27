# Night validation series: 3D and unsteady cases against published references

Scope for this pass: run a series of 3D and unsteady validation cases,
grading each against a published reference where one honestly applies, and
marking NOT VALIDATED where it does not rather than forcing a comparison.
Every unsteady result below carries its `halves_drift()` stationarity verdict
(`sdk/workflows/tmr_verification.py:2736`, added in `6606434` after an
archived NACA 0012 transient was found to be a 31.6%-drifting mid-transient
snapshot reported as converged). Compute capped at 3 CPU cores
(`taskset -c 0-2` on every solve/utility launched from this series).

All raw solver output referenced below lives under
`~/certonomous-runs/.mesh-cache/`, `~/certonomous-runs/.solve-cache/` (cached
cases, paired to their mesh by cell count from `polyMesh/owner`), and
`~/certonomous-runs/validation-scratch/` (scratch cases assembled here to run
`checkMesh`/`yPlus` against the cached fields) and
`~/certonomous-runs/unsteady-cylinder/` (the new transient solves run for
this series).

---

## Case 1 — motorBike, 3D, drag-area band (SOLVER-BACKED)

**Geometry**: the stock OpenFOAM `incompressible/simpleFoam/motorBike`
tutorial body (motorcycle + rider), meshed finer than the tutorial default.

**Cells**: 353,688 (`~/certonomous-runs/.mesh-cache/motorBike/polyMesh`,
paired by `nCells` in the `owner` header to
`~/certonomous-runs/.solve-cache/motorBike-c353688-i300`, 300 `simpleFoam`
iterations, `DONE`).

**Flow**: U = 20 m/s, ν = 1.5e-5 m²/s (air), `kOmegaSST` RAS, wall functions
(no prism boundary layer — stock tutorial mesh). Re_L (lRef = 1.42 m) ≈
1.89e6. `forceCoeffs`: Aref = 0.75 m², lRef = 1.42 m, CofR (0.72 0 0).

**Mesh quality** (`checkMesh -allTopology -allGeometry`, re-run here on the
cached `constant/polyMesh` + tutorial `system/`, capped `taskset -c 0-2`):
max non-orthogonality **64.98°** (hard gate 70°, pass), max skewness
**3.995** (guidance 4.0, pass but essentially on the line), max aspect ratio
41.1. 3 "extra" checks failed: 1,210 cells below the determinant floor,
15,046 concave cells, 1,078 low-interpolation-weight faces — consistent with
the sliver-cell artifact this repo already documented for this body
(`b8c2eb7`, "Document motorBike Cp = 1.1193 anomaly ... sliver-cell
artifact").

**y+** (`simpleFoam -postProcess -func yPlus -time 300` on the reassembled
case; the plain `postProcess -func yPlus` utility silently zeroes every patch
here — "Unable to find turbulence model in the database" — so the solver
itself must run the function object): over 68 wall patches, min y+ = 0.675,
max y+ = 3,637, mean-of-patch-means ≈ 167. 31 of 68 patches have a local
minimum y+ below 5 (into the buffer/viscous layer) even though the patch
means sit in the nominal wall-function range (30-300) — the wall-function
assumption is locally violated on those patches, expected on a mesh with no
resolved boundary layer.

**Convergence**: force coefficients plateaued — Cd over the last 20
iterations ranges 0.4202-0.4206 (< 0.1% spread) — while raw field residuals
at iteration 300 (Ux 5.5e-5, p 1.2e-3) sit above the classic 1e-5/1e-6
`residualControl` target. The force-integral quantity being reported has
converged even though the case was not run to full residual-based
convergence; this is stated rather than hidden.

**Grid trend** (bonus, no extra solve — read from already-cached rungs of
the same body): 14,714 cells -> Cd 0.4707; 66,302 cells -> Cd 0.4213;
353,688 cells -> Cd 0.4202. Monotonic, asymptotically flattening (-10.5% then
-0.26% per refinement) — supports approaching mesh independence, not a
formal GCI.

**Reference**: no wind-tunnel measurement exists for this specific synthetic
CAD body, so the only honest comparison is a population band. Drag area
(Cd·Aref, area-convention-proof) = 0.4202 x 0.75 = **0.315 m²**, against the
published motorcycle-with-rider band **0.30-0.70 m²**
(Cossalter, *Motorcycle Dynamics*, 2006; Hoerner, *Fluid-Dynamic Drag*,
1965 — `models/curriculum/motorBike/reference.yaml`).

**Verdict** (via the repo's own `lab.grade_drag_area`, not re-derived):
tier **SOLVER-BACKED** — "drag area 0.32 m² sits inside the published
motorcycle-with-rider band, 0.3 to 0.7 m² (Cossalter 2006; Hoerner 1965); a
published band, not a geometry-specific experiment." A band comparison can
never earn VALIDATED by this lab's own rule; the in-band result is reported
as what it is.

---

## Case 2 — B-52, 3D, drag coefficient (NOT VALIDATED — regime + resolution mismatch)

**Geometry**: custom B-52 Stratofortress STL (13,784 facets), rescaled to
the real aircraft length, 48.5 m (159 ft — matches the real B-52).

**Cells**: 193,880 (`~/certonomous-runs/.mesh-cache/b52/polyMesh`, paired to
`~/certonomous-runs/.solve-cache/b52-c193880-i300`, 300 iterations, `DONE`).

**Flow**: U = 100 m/s, ν = 1.5e-5 m²/s, `kOmegaSST` RAS, wall functions.
Re_L ≈ 3.23e8, Mach ≈ 0.29 (incompressible). `forceCoeffs`: Aref = 600.598 m²,
lRef = 48.5 m.

**Mesh quality**: max non-orthogonality **54.33°** (pass), max skewness
**3.912** (pass), max aspect ratio 6.52. 1 extra check failed: 6,812 concave
cells.

**y+** (`simpleFoam -postProcess -func yPlus -time 300`, single `body` patch,
7,533 wall faces): min **2,183**, max **108,367**, average **15,690** — three
to four orders of magnitude above the 30-300 range wall functions are valid
in. At 193,880 cells over a full aircraft, the near-wall mesh is nowhere near
resolved enough for this Reynolds number; the surface pressure field this
case has previously been graded on (`demo-output/plots/pressure_slices/validation/B52.md`)
is a legitimate physics-invariant check, but the force/drag coefficient does
not carry the same trust.

**Convergence**: Cd is flat to 4 significant figures over the last 5
iterations (0.047195-0.047205, <0.03% spread) — the force integral itself is
numerically settled.

**Reference search**: I looked for a published B-52 zero-lift drag
coefficient. A commonly repeated figure, CD0 ≈ 0.0119, traces back through
secondary sources toward compiled aircraft-drag tables such as Loftin,
*Quest for Performance: The Evolution of Modern Aircraft*, NASA SP-468
(https://ntrs.nasa.gov/citations/19850023776) — but the NASA mirror pages
that would show the actual table 403'd, so I could not independently confirm
the exact number, table, or (critically) its reference-area basis from a
source I could read myself. Separately, the real B-52's wing planform area
is 4,000 sq ft = 371.6 m² (https://www.thisdayinaviation.com,
https://stratofortress.org/b-52-specifications/), a factor of 1.6 below this
case's Aref = 600.598 m², so even a verified CD0 could not be compared
directly without rebasing.

More fundamentally: the real B-52 cruises transonic (Mach ~0.77-0.8) at high
altitude; this solve is incompressible at Mach ~0.29 at sea-level density. A
zero-lift-drag-coefficient comparison assumes clean, unseparated,
subsonic-compressible-corrected flow — this case is a different flow regime
entirely, before the mesh-resolution and reference-area problems above are
even considered.

**Verdict**: **NOT VALIDATED — reference regime mismatch.** Measured Cd =
0.0472 (Cd·Aref = 28.3 m² on this case's own Aref, 17.5 m² if rebased to the
real wing area of 371.6 m²) is reported as the honest measured number. No
credible like-for-like published comparison exists for this case's own
regime (incompressible, sea-level, wall-function-only, 193,880 cells) —
stating agreement or disagreement against a transonic-cruise CD0 figure I
could not even fully verify would be false precision, so this case is marked
NOT VALIDATED rather than compared against nothing solid.

---

## Case 3 — circular cylinder, unsteady vortex shedding, Re = 100 (pending)

To follow: laminar 2D pimpleFoam vortex-shedding solve at Re_D ≈ 100,
gated with `halves_drift()` before any Cd/St is reported.
