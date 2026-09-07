# Mesh birth certificate — VMFL017-R3 RAE 2822 transonic HIGH-Re WALL-FUNCTION C-mesh family

MESH_STANDARD sec.6. 2D C-mesh around the RAE 2822 airfoil, single cell in span (empty
frontAndBack), patches: aerofoil (wall), inflow / outflow (freestream far-field), frontAndBack.
Built and checked in OpenFOAM v2606 (`blockMesh` + `checkMesh`), rc 0, `Mesh OK` on all three
levels. Declared BEFORE the graded run; the graded run dir
`verification/runs/ansys_verification/VMFL017-R3/` does not exist at freeze time.

## Why a NEW mesh family (and not the row #19 / row #32 family reused verbatim)

VMFL017-R2 (register row #32, `NOT A RESULT`) proved, on the graded path, that
`rhoCentralFoam` on the birth-certified **y+ ~ 0.5 (low-Re) family** is ~56× over its
per-level cap: the extreme wall-normal grading (last/first ratio **4 401 087**, first cell
≈ 2.0e-6 m) forces the explicit acoustic-CFL step to **Δt ≈ 1.85e-9 s**, so L1 alone would
need ≈ 16 871 core-min to reach `endTime` 0.05 s. That row's own pre-registration named the
remedy as a **DIFFERENT registration**: "a wall function raising the near-wall cell by three
decades." This family is that remedy.

**What is IDENTICAL to the row #19 / row #32 family** (so the two are directly comparable and
the geometry provenance carries forward unchanged): the airfoil ordinates and the full
`vertices` / `edges` (polyLine surface) / `blocks` topology, the far-field radius (50 chords),
the wake length, the patch names and face assignment, the streamwise cell distribution, and the
cell counts **23 040 / 92 160 / 368 640** (r = 2, ×4 per level). Each R3 `blockMeshDict.L<n>` is
the frozen attempt-1 `blockMeshDict.L<n>` with **only the wall-normal grading token replaced**
(a pure `sed` of the one wall-normal grading value in each `simpleGrading` / `edgeGrading`),
nothing else touched.

**What CHANGES:** the wall-normal first-cell height is raised from y+ ~ 0.5 to **y+ ~ 30**
(the log-law wall-function regime), and — because `rhoCentralFoam` is explicit — the first cell
is held at the **same physical height on ALL THREE levels** (not refined toward the wall like a
low-Re family), so the wall y+ stays in the log-law band as the mesh refines. This is the
wall-function-consistent refinement: the levels refine streamwise and wall-normal-count while
the near-wall y+ is held ~constant, which is what makes the triple an admissible convergence
study for a wall-function result.

## Geometry provenance (unchanged from the row #19 family)

Airfoil ordinates: `verification/runs/F12_runs/reference/rae2822_coordinates.dat` — RAE 2822
design-section ordinates, NPARC Alliance Validation Archive (transcribing AGARD AR-138
Table 6.1, cross-checked to 3.1e-6 chord). This is the SAME AGARD AR-138 (Cook/McDonald/Firmin
1979) that VMFL017 cites as its reference — geometry and data share one primary source.
Chord = 1.0 m; max thickness ~0.121 m (manual p.69). Far field ~100 chords.

## The wall-normal grading transform (recorded so it is reproducible)

Target first-cell height 2.5e-4 m (chord = 1 m). y+ estimate from the flat-plate correlation
Cf ≈ 0.058·Re^-0.2 at Re = 6.5e6: u_τ ≈ 8.99 m/s, ν = μ/ρ = 3.902e-5 m²/s, so a first cell of
2.5e-4 m sits at **y+ (full height) ≈ 58, y+ (cell centre) ≈ 29** at the reference station.
The OpenFOAM wall-normal grading (last/first ratio) for first cell 2.5e-4 m over a 50-chord
far field, at each level's wall-normal cell count, from the repo's own
`sdk.workflows.tmr_verification.ratio_for_first_cell(R=50, ny, first_cell=2.5e-4)`:

| level | mult | cells   | ny (wall-normal) | wall-normal grading (last/first) | replaced token (low-Re) |
|-------|------|---------|------------------|----------------------------------|-------------------------|
| L1    | 1    | 23040   | 80               | 23969                            | 4401087.387             |
| L2    | 2    | 92160   | 160              | 11414                            | 4598884.808             |
| L3    | 4    | 368640  | 320              | 5306.57                          | 4702008.693             |

cells(L2)/cells(L1) = 4.0, cells(L3)/cells(L2) = 4.0 → exact r = 2 in each of two directions.
The grading gets GENTLER with refinement (first cell held constant while ny doubles), which is
exactly what keeps the wall y+ ~ constant across the family.

## checkMesh confirmation (this case, all three levels; logs in mesh_birth/checkMesh/)

| level | cells  | Mesh OK | max non-orthogonality | max skewness | max aspect ratio |
|-------|--------|---------|-----------------------|--------------|------------------|
| L1    | 23040  | yes     | 35.26                 | 0.851        | 336.7            |
| L2    | 92160  | yes     | 35.27                 | 0.827        | 320.6            |
| L3    | 368640 | yes     | 35.27                 | 0.800        | 298.1            |

Non-orthogonality is self-similar across the family (~35.3, a property of the surface→far-field
correspondence, not the spacing). Max aspect ratio is **lower** than the low-Re family
(row #19/#32 L1 measured 805.2 at the smoke) because the gentler wall-normal grading removes the
sliver first cell. All three are well inside MESH_STANDARD limits.

## Realised y+ (answer-blind smoke, L1; recorded, and re-verified at the graded run)

An ephemeral answer-blind smoke (scratch only; the graded Cd/Cl were never read for grading)
ran `rhoCentralFoam` on L1 and wrote the `yPlus` function object: on the aerofoil wall the
**average y+ ≈ 43–51 and max y+ ≈ 53–66** over the early transient, with the **min dropping to
~3–10 only at the stagnation point and near separation** (where wall shear → 0, unavoidable on
any mesh and handled by the continuous wall functions). The average/max sit in the log-law
wall-function-valid band. The comparator `grade_vmfl017_r3.py` re-checks this on the GRADED run
as a value-blind regime precondition (window max y+ ≤ 300 AND window mean-average y+ ≥ 10, else
`NOT A RESULT`); the min is never gated, because y+ → 0 at stagnation is physical.

## Birth assertion

The geometry is the manual's own reference geometry (AGARD AR-138). Cell counts and the
wall-normal first-cell target are declared here BEFORE the graded run and frozen in
PREREGISTRATION.md sec.7-8. The launcher builds each level from
`case/system/blockMeshDict.L<n>`, verifies each on disk hashes equal to its committed HEAD blob,
re-runs `checkMesh` into the run dir, and refuses (exit 2) on any mismatch.
