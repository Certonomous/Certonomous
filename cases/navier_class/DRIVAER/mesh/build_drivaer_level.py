#!/usr/bin/env python3
"""DRIVAER R1 -- emit ONE geometrically-similar mesh level.

THE ONLY THING THAT CHANGES BETWEEN LEVELS IS ``h_bg``.  Every refinement
level, every refinement box, every layer thickness and the whole domain are
IDENTICAL across the family, so halving ``h_bg`` halves the cell size
everywhere the mesh is not already at a fixed absolute size.

WHY THE NEAR-WALL LAYER IS ABSOLUTE AND NOT RELATIVE
    ``relativeSizes false`` with a fixed 0.75 mm first layer holds y+ CONSTANT
    across the triple.  The alternative (relativeSizes) walks the first-cell
    centre with h_bg and so walks y+ by the full refinement factor across the
    family -- the wall model would then be a different model on each level and
    the Roache order would be measuring the closure changing, not the grid.
    The counter-example is measured, not asserted: see MEASURED_YPLUS_SWEEP in
    the stage record.

REFUSES an existing level directory.  It never deletes one.
"""
from __future__ import annotations
import argparse, json, os, re, shutil, sys
from pathlib import Path

STL = "/home/ubuntu/certonomous-runs/navier_class/DRIVAER/drivaerml_r7a5c094/run_466/drivaer_466.stl"

# ---- domain, FIXED for every level ---------------------------------------
# STL bbox (measured): x -0.792802..3.779650  y -1.001960..1.001960
#                      z -0.319633..1.225880
X0, XBL, X1 = -14.339, -2.339, 37.661   # xBL = -2.339 m: DrivAerML ground-BL start
Y0, Y1 = -10.0, 10.0
Z0, Z1 = -0.319, 11.681                 # floor 0.633 mm ABOVE the STL minimum,
                                        # 2.325 mm BELOW the tyre bottom, so the
                                        # tyre PLINTH is cut by the floor and the
                                        # contact patch is finite, never a tangent cusp.
AREF, LREF = 2.298, 2.79                # geo_ref_466.csv, this geometry's own

# refinement boxes: FIXED physical size -> they scale as r^3
BOXES = [
    ("box1", (-3.0, -3.0, Z0), (15.0, 3.0, 3.0), 1),
    ("box2", (-1.8, -2.0, Z0), (8.0, 2.0, 2.2), 2),
    ("box3", (-1.2, -1.4, Z0), (5.5, 1.4, 1.6), 3),
]
SURF_LEVEL = (4, 4)
SNAP_TOL = 1.0
FINE_FEATURES = ("TirePlinth", "Mirrors", "BodyDoorhandles", "ClosedGrill",
                 "ExhaustSystem", "BodyHeadlamps", "BodyRocker")
FINE_LEVEL = (5, 5)

LAYERS = dict(nSurfaceLayers=5, firstLayerThickness=0.00075,
              expansionRatio=1.25, minThickness=0.0003)

LOCATION_IN_MESH = (-10.0, 5.0, 5.0)


def solids(stl_path: str):
    out = []
    with open(stl_path) as f:
        for line in f:
            s = line.lstrip()
            if s.startswith("solid "):
                out.append(s[6:].strip())
    return out


def sanitise(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def head(cls, obj, loc="system"):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
"""


def block_mesh(h):
    nxA, nxB = round((XBL - X0) / h), round((X1 - XBL) / h)
    ny, nz = round((Y1 - Y0) / h), round((Z1 - Z0) / h)
    for nm, n, L in (("nxA", nxA, XBL - X0), ("nxB", nxB, X1 - XBL),
                     ("ny", ny, Y1 - Y0), ("nz", nz, Z1 - Z0)):
        got = L / n
        if abs(got - h) / h > 1e-9:
            raise SystemExit(f"REFUSE: {nm} does not divide exactly at h={h}: "
                             f"cell {got} != {h}")
    v = []
    for x in (X0, XBL, X1):
        for y in (Y0, Y1):
            for z in (Z0, Z1):
                v.append((x, y, z))
    # index: i*4 + j*2 + k  with i over x, j over y, k over z
    def V(i, j, k):
        return i * 4 + j * 2 + k
    verts = "\n".join(f"    ({x} {y} {z})" for (x, y, z) in v)

    def hexblk(i0, i1, n1):
        return (f"    hex ({V(i0,0,0)} {V(i1,0,0)} {V(i1,1,0)} {V(i0,1,0)} "
                f"{V(i0,0,1)} {V(i1,0,1)} {V(i1,1,1)} {V(i0,1,1)}) "
                f"({n1} {ny} {nz}) simpleGrading (1 1 1)")

    def face(i0, i1, j0, j1, k0, k1):
        return f"({V(i0,j0,k0)} {V(i0,j1,k1)} {V(i1,j1,k1)} {V(i1,j0,k0)})"

    txt = head("dictionary", "blockMeshDict") + f"""
scale   1;

vertices
(
{verts}
);

blocks
(
{hexblk(0,1,nxA)}
{hexblk(1,2,nxB)}
);

edges ();

boundary
(
    inlet
    {{ type patch; faces ( ({V(0,0,0)} {V(0,0,1)} {V(0,1,1)} {V(0,1,0)}) ); }}
    outlet
    {{ type patch; faces ( ({V(2,0,0)} {V(2,1,0)} {V(2,1,1)} {V(2,0,1)}) ); }}
    floorSlip
    {{ type wall; faces ( ({V(0,0,0)} {V(0,1,0)} {V(1,1,0)} {V(1,0,0)}) ); }}
    floorNoSlip
    {{ type wall; faces ( ({V(1,0,0)} {V(1,1,0)} {V(2,1,0)} {V(2,0,0)}) ); }}
    top
    {{ type wall; faces ( ({V(0,0,1)} {V(1,0,1)} {V(1,1,1)} {V(0,1,1)})
                          ({V(1,0,1)} {V(2,0,1)} {V(2,1,1)} {V(1,1,1)}) ); }}
    sideMinus
    {{ type wall; faces ( ({V(0,0,0)} {V(1,0,0)} {V(1,0,1)} {V(0,0,1)})
                          ({V(1,0,0)} {V(2,0,0)} {V(2,0,1)} {V(1,0,1)}) ); }}
    sidePlus
    {{ type wall; faces ( ({V(0,1,0)} {V(0,1,1)} {V(1,1,1)} {V(1,1,0)})
                          ({V(1,1,0)} {V(1,1,1)} {V(2,1,1)} {V(2,1,0)}) ); }}
);

mergePatchPairs ();
"""
    return txt, dict(nxA=nxA, nxB=nxB, ny=ny, nz=nz,
                     background_cells=(nxA + nxB) * ny * nz, h_bg=h)


def snappy(regions, fsnap, snap_tol, addlayers):
    ADDLAYERS = 'true' if addlayers else 'false'
    reg_geom, reg_ref, reg_lay = [], [], []
    for raw in regions:
        s = sanitise(raw)
        reg_geom.append(f'            "{raw}" {{ name {s}; }}')
        lvl = FINE_LEVEL if any(k in raw for k in FINE_FEATURES) else SURF_LEVEL
        reg_ref.append(f'                {s} {{ level ({lvl[0]} {lvl[1]}); }}')
        reg_lay.append(f'        {s} {{ nSurfaceLayers {LAYERS["nSurfaceLayers"]}; }}')
    boxes_geom = "\n".join(
        f"""    {n}
    {{
        type searchableBox;
        min ({a[0]} {a[1]} {a[2]});
        max ({b[0]} {b[1]} {b[2]});
    }}""" for (n, a, b, _l) in BOXES)
    boxes_ref = "\n".join(
        f"        {n} {{ mode inside; levels ((1E15 {l})); }}"
        for (n, _a, _b, l) in BOXES)
    nl = "\n"
    return head("dictionary", "snappyHexMeshDict") + f"""
castellatedMesh true;
snap            true;
addLayers       {ADDLAYERS};

geometry
{{
    car
    {{
        type triSurfaceMesh;
        file "drivaer_466.stl";
        regions
        {{
{nl.join(reg_geom)}
        }};
    }}
{boxes_geom}
}};

castellatedMeshControls
{{
    maxLocalCells       6000000;
    maxGlobalCells      40000000;
    minRefinementCells  10;
    maxLoadUnbalance    0.10;
    nCellsBetweenLevels 3;

    features
    (
        {{ file "drivaer_466.eMesh"; level {SURF_LEVEL[1]}; }}
    );

    refinementSurfaces
    {{
        car
        {{
            level ({SURF_LEVEL[0]} {SURF_LEVEL[1]});
            patchInfo {{ type wall; }}
            regions
            {{
{nl.join(reg_ref)}
            }}
        }}
    }}

    resolveFeatureAngle 30;

    refinementRegions
    {{
{boxes_ref}
    }}

    locationInMesh ({LOCATION_IN_MESH[0]} {LOCATION_IN_MESH[1]} {LOCATION_IN_MESH[2]});
    allowFreeStandingZoneFaces true;
}}

snapControls
{{
    nSmoothPatch    3;
    tolerance       {snap_tol};
    nSolveIter      50;
    nRelaxIter      6;
    nFeatureSnapIter 12;
    implicitFeatureSnap {'true' if fsnap=='implicit' else 'false'};
    explicitFeatureSnap {'true' if fsnap=='explicit' else 'false'};
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes       false;
    firstLayerThickness {LAYERS['firstLayerThickness']};
    expansionRatio      {LAYERS['expansionRatio']};
    minThickness        {LAYERS['minThickness']};

    layers
    {{
{nl.join(reg_lay)}
        floorNoSlip {{ nSurfaceLayers {LAYERS['nSurfaceLayers']}; }}
    }}

    nGrow               0;
    featureAngle        130;
    slipFeatureAngle    30;
    nRelaxIter          5;
    nSmoothSurfaceNormals 1;
    nSmoothNormals      3;
    nSmoothThickness    10;
    maxFaceThicknessRatio 0.5;
    maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle  90;
    nBufferCellsNoExtrude 0;
    nLayerIter          50;
    nRelaxedIter        20;
}}

meshQualityControls
{{
    #include "meshQualityDict"
}}

writeFlags ( );
mergeTolerance 1e-6;
"""


MESHQUALITY = head("dictionary", "meshQualityDict") + """
maxNonOrtho         65;
maxBoundarySkewness 20;
maxInternalSkewness 4;
maxConcave          80;
minVol              1e-13;
minTetQuality       1e-15;
minArea             -1;
minTwist            0.02;
minDeterminant      0.001;
minFaceWeight       0.05;
minVolRatio         0.01;
minTriangleTwist    -1;
nSmoothScale        4;
errorReduction      0.75;

relaxed
{
    maxNonOrtho     75;
}
"""

CONTROLDICT = head("dictionary", "controlDict") + """
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""

FVSCHEMES = head("dictionary", "fvSchemes") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default cellLimited Gauss linear 1; }
divSchemes
{
    default             none;
    div(phi,U)          bounded Gauss linearUpwind grad(U);
    div(phi,k)          bounded Gauss limitedLinear 1;
    div(phi,omega)      bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
"""

FVSOLUTION = head("dictionary", "fvSolution") + """
solvers
{
    p     { solver GAMG; tolerance 1e-8; relTol 0.01; smoother GaussSeidel; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-9; relTol 0.01; }
}
SIMPLE { nNonOrthogonalCorrectors 0; consistent yes; }
relaxationFactors { equations { U 0.9; ".*" 0.9; } }
"""

SFEDICT = head("dictionary", "surfaceFeatureExtractDict") + """
drivaer_466.stl
{
    extractionMethod    extractFromSurface;
    extractFromSurfaceCoeffs { includedAngle 150; }
    writeObj            no;
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--h", type=float, required=True)
    ap.add_argument("--level-name", required=True)
    ap.add_argument("--feature-snap", default="implicit",
                    choices=["explicit", "implicit", "none"])
    ap.add_argument("--snap-tol", type=float, default=SNAP_TOL)
    ap.add_argument("--no-layers", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    if root.exists():
        raise SystemExit(f"REFUSE: {root} already exists. This script never "
                         f"deletes a level directory; move it aside by hand.")
    regions = solids(STL)
    if len(regions) != 49:
        raise SystemExit(f"REFUSE: expected 49 STL solids, read {len(regions)}")
    bm, meta = block_mesh(a.h)
    (root / "system").mkdir(parents=True)
    (root / "constant" / "triSurface").mkdir(parents=True)
    for name, txt in (("blockMeshDict", bm),
                      ("snappyHexMeshDict", snappy(regions, a.feature_snap, a.snap_tol, not a.no_layers)),
                      ("meshQualityDict", MESHQUALITY),
                      ("controlDict", CONTROLDICT),
                      ("fvSchemes", FVSCHEMES),
                      ("fvSolution", FVSOLUTION),
                      ("surfaceFeatureExtractDict", SFEDICT)):
        (root / "system" / name).write_text(txt)
    os.symlink(STL, root / "constant" / "triSurface" / "drivaer_466.stl")
    meta.update(level=a.level_name, feature_snap=a.feature_snap,
                snap_tolerance=a.snap_tol, add_layers=not a.no_layers, n_regions=len(regions),
                region_map={r: sanitise(r) for r in regions},
                domain=dict(x=[X0, XBL, X1], y=[Y0, Y1], z=[Z0, Z1]),
                aRef=AREF, lRef=LREF,
                blockage_pct=100.0 * AREF / ((Y1 - Y0) * (Z1 - Z0)),
                surf_level=SURF_LEVEL, fine_level=FINE_LEVEL,
                fine_feature_keys=FINE_FEATURES, boxes=BOXES, layers=LAYERS,
                stl=STL)
    (root / "MESH_SPEC.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: v for k, v in meta.items() if k != "region_map"}, indent=1))


if __name__ == "__main__":
    main()
