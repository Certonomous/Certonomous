# Mesh birth certificate -- VMFL017 RAE 2822 transonic C-mesh family

MESH_STANDARD sec.6. 2D C-mesh around the RAE 2822 airfoil, single cell in span (empty
frontAndBack), patches: aerofoil (wall), inflow / outflow (freestream far-field), frontAndBack.

## Geometry provenance
Airfoil ordinates: verification/runs/F12_runs/reference/rae2822_coordinates.dat --
"RAE 2822 design section ordinates, 65 stations per surface", sourced from the NPARC
Alliance Validation Archive yu.pts/yl.pts (grc.nasa.gov/www/wind/valid/raetaf/) which
transcribe AGARD AR-138 Table 6.1, cross-checked against the AFOSR-HTTM tape design
ordinates to 3.1e-06 chord. This is the SAME AGARD AR-138 (Cook/McDonald/Firmin 1979)
that VMFL017 cites as its reference -- the geometry and the data share one primary source.
Chord = 1.0 m, x in [0,1]; max half-thickness 0.0629 -> max thickness ~0.121 m (matches
the manual's stated d = 0.121 m). Far field spans ~100 chords (manual p.69).

## Grid family (ratio r = 2), from the closure team's birth-certified recipe
The three blockMeshDicts are the coarse/medium/fine C-meshes from
verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/{coarse,medium,fine}, generated
by build_ladder_attempt2.py (18 hex blocks, surface-block plan refined x2 per level, a
non-orthogonality predictor that REFUSES a build over 55 deg). Copied here as
case/system/blockMeshDict.{L1,L2,L3}. Reused as a PUBLIC-geometry mesh with provenance;
the mesh is not the object under verification -- the solver's Cd/Cl is.

| level | mult | cells   | source birth cert (F12 birth_certificates.json)         |
|-------|------|---------|---------------------------------------------------------|
| L1    | 1    | 23040   | coarse; blockMesh v2606; checkMesh logged               |
| L2    | 2    | 92160   | medium                                                  |
| L3    | 4    | 368640  | fine                                                    |
cells(L2)/cells(L1)=4.0, cells(L3)/cells(L2)=4.0 -> exact r=2 in each of two directions.

## Confirmation (this case)
L1 (coarse) blockMesh in OpenFOAM v2606 built 23040 cells, rc=0, and rhoSimpleFoam ran a
scratch smoke on it producing forceCoeffs Cd/Cl (case machinery verified; the smoke grades
nothing and is discarded). The launcher builds each level from case/system/blockMeshDict.L<n>
and re-runs checkMesh into the run dir at launch.

## Birth assertion
The geometry is the manual's own reference geometry (AGARD AR-138); cell counts are declared
here BEFORE the graded run and frozen in PREREGISTRATION.md sec.7-8. The graded run dir does
not exist at freeze time.
