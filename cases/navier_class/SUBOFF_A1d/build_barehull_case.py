#!/usr/bin/env python3
"""
A1d — build the BARE-HULL 3-D half-model case (geometry + blockMesh/snappyHexMesh dicts).

Emits a complete case directory. It does NOT run anything: blockMesh and snappyHexMesh
are executed by build_barehull.sh, which is what the queue entry launches.

WHY THIS REUSES THE A1 GEOMETRY MODULE RATHER THAN COPYING IT
-------------------------------------------------------------
hull.stl is built by calling build_suboff_a1_geometry.build_hull_stl DIRECTLY. That
function is the one GATE X5 (check_barehull_geometry.py) validated against Roddy 1990
Table 2 to 0.081 % at all 25 stations. A copied-and-edited hull function would be a
DIFFERENT function, and X5's PASS would no longer apply to the thing actually built.
Rule 14's shape: the lesson is not applied until the call site asserts it.

WHAT IS DELIBERATELY ABSENT
---------------------------
No sail.stl, no `sail` surface, no sail refinement, no jctBox (the sail/hull junction
does not exist), no sail-TE box. A1d's geometry is hull + nothing. The emitted
boundary must carry FIVE patches -- inlet outlet farfield symm hull -- and a `sail`
patch in an A1d mesh means the wrong geometry was built (A1d §6).

THE HALF MODEL
--------------
Symmetry plane at z = 0, carried unchanged from A1: the block spans z in [0, zmax] and
y in [ymin, ymax]. A PITCH sweep rotates U in the x-y plane and therefore PRESERVES
z = 0. This is why A1d can use a half model for the whole α sweep (A1c §4).
"""
import argparse
import importlib.util
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.normpath(os.path.join(HERE, "..", "SUBOFF_A1"))

# A1d's OWN level table, registered here. Base cell size and hull octree level are
# carried from A1's L1 row UNCHANGED so the two arms are comparable; the sail, junction
# and sail-TE rows simply do not exist. tail_lvl is A1d's own: A1's tail apex is inside
# the sail-TE box, which A1d does not have, so the closed tail needs its own refinement.
LEVELS = {
    #        d0 (m),  hull lvl, tail box lvl, nLayers
    "L1": (0.0787, 4, 7, 6),
    "L2": (0.0525, 4, 7, 7),
}


def load_a1_geometry():
    src = os.path.join(A1, "build_suboff_a1_geometry.py")
    if not os.path.isfile(src):
        sys.stderr.write("REFUSED: A1 geometry module not found: %s\n" % src)
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("a1geom", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, src


def w(path, cls, obj, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
                 "    class %s;\n    object %s;\n}\n\n" % (cls, obj))
        fh.write(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--level", required=True, choices=sorted(LEVELS))
    ap.add_argument("--n-axial", type=int, default=600)
    ap.add_argument("--n-theta", type=int, default=180)
    ap.add_argument("--xmin", type=float, default=-2.0)
    ap.add_argument("--xmax", type=float, default=9.0)
    ap.add_argument("--rfar", type=float, default=3.0)
    a = ap.parse_args()

    # ---- REFUSALS ------------------------------------------------------------
    if os.path.exists(os.path.join(a.case, "constant", "polyMesh")):
        sys.stderr.write("REFUSED: constant/polyMesh already exists. A builder never "
                         "overwrites a built mesh (rule-4 sibling).\n")
        sys.exit(2)

    geom, geom_src = load_a1_geometry()

    # The tail must CLOSE for A1d: Roddy Table 2 station 20.4167 has B/Bmax = 0.00000,
    # and GATE X5 passed against that. A geometry whose tail radius is non-zero here
    # is not the geometry X5 validated.
    r_tail = geom.hull_R_ft(geom.L_TOTAL_FT)
    if abs(r_tail) > 1.0e-9:
        sys.stderr.write("REFUSED: hull tail radius at L_TOTAL_FT is %r, not 0. GATE X5 "
                         "passed against a CLOSED tail; this geometry is not that one.\n"
                         % r_tail)
        sys.exit(2)
    r_nose = geom.hull_R_ft(0.0)
    if abs(r_nose) > 1.0e-9:
        sys.stderr.write("REFUSED: hull nose radius at x=0 is %r, not 0.\n" % r_nose)
        sys.exit(2)

    d0, l_hull, l_tail, nlay = LEVELS[a.level]
    ft2m = geom.FT2M
    L_m = geom.L_TOTAL_FT * ft2m

    geo_dir = os.path.join(a.case, "constant", "triSurface")
    os.makedirs(geo_dir, exist_ok=True)
    n_tris, xs, R = geom.build_hull_stl(os.path.join(geo_dir, "hull.stl"),
                                        a.n_axial, a.n_theta)
    if os.path.exists(os.path.join(geo_dir, "sail.stl")):
        sys.stderr.write("REFUSED: sail.stl present in an A1d case. A1d is HULL ONLY.\n")
        sys.exit(2)

    # ---- background block, snapped to an integer number of d0 ----------------
    nx = int(round((a.xmax - a.xmin) / d0))
    ny = int(round(2 * a.rfar / d0))
    nz = int(round(a.rfar / d0))
    xmax = a.xmin + nx * d0
    ymax = ny * d0 / 2.0
    ymin = -ymax
    zmax = nz * d0

    v = [(a.xmin, ymin, 0), (xmax, ymin, 0), (xmax, ymax, 0), (a.xmin, ymax, 0),
         (a.xmin, ymin, zmax), (xmax, ymin, zmax), (xmax, ymax, zmax), (a.xmin, ymax, zmax)]
    verts = "\n".join("    (%.6f %.6f %.6f)" % p for p in v)
    w(os.path.join(a.case, "system", "blockMeshDict"), "dictionary", "blockMeshDict",
      "scale 1;\n\nvertices\n(\n%s\n);\n\n"
      "blocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d %d) simpleGrading (1 1 1)\n);\n\n"
      "edges ();\n\n"
      "boundary\n(\n"
      "    inlet    { type patch;         faces ((0 4 7 3)); }\n"
      "    outlet   { type patch;         faces ((1 2 6 5)); }\n"
      "    symm     { type symmetryPlane; faces ((0 3 2 1)); }\n"
      "    farfield { type patch;         faces ((4 5 6 7) (0 1 5 4) (3 7 6 2)); }\n"
      ");\n\nmergePatchPairs ();\n" % (verts, nx, ny, nz))

    # tail refinement box: the closed apex, which in A1 sat inside the sail-TE box
    tail_x0 = (geom.L_PMB_END + 0.5 * (geom.L_TOTAL_FT - geom.L_PMB_END)) * ft2m
    tail_r = 0.25 * geom.RMAX_FT * ft2m

    snappy = f"""castellatedMesh true;
snap            true;
addLayers       true;

geometry
{{
    hull.stl {{ type triSurfaceMesh; name hull; }}
    tailBox
    {{
        type searchableBox;
        min ({tail_x0:.6f} {-tail_r:.6f} {-tail_r:.6f});
        max ({L_m + 0.05:.6f} {tail_r:.6f} {tail_r:.6f});
    }}
}}

castellatedMeshControls
{{
    maxLocalCells 4000000;
    maxGlobalCells 40000000;
    minRefinementCells 0;
    nCellsBetweenLevels 3;
    resolveFeatureAngle 30;
    allowFreeStandingZoneFaces false;
    features ();
    refinementSurfaces
    {{
        hull {{ level ({l_hull} {l_hull + 1}); patchInfo {{ type wall; inGroups (wall); }} }}
    }}
    refinementRegions
    {{
        hull    {{ mode distance; levels ((0.030 {l_hull - 1}) (0.150 {l_hull - 2}) (0.500 {l_hull - 3})); }}
        tailBox {{ mode inside;   levels ((1e15 {l_tail})); }}
    }}
    locationInMesh ({a.xmin + 0.5 * d0:.6f} {ymax - 0.5 * d0:.6f} {zmax - 0.5 * d0:.6f});
}}

snapControls
{{
    nSmoothPatch 5; tolerance 2.0; nSolveIter 60; nRelaxIter 8;
    nFeatureSnapIter 15; implicitFeatureSnap true; explicitFeatureSnap false;
    multiRegionFeatureSnap false;
}}

addLayersControls
{{
    relativeSizes true;
    layers {{ hull {{ nSurfaceLayers {nlay}; }} }}
    expansionRatio 1.2;
    finalLayerThickness 0.5;
    minThickness 0.02;
    nGrow 0;
    featureAngle 130; slipFeatureAngle 30;
    nRelaxIter 8; nSmoothSurfaceNormals 3; nSmoothNormals 5; nSmoothThickness 10;
    maxFaceThicknessRatio 0.5; maxThicknessToMedialRatio 0.3;
    minMedialAxisAngle 90; nBufferCellsNoExtrude 0;
    nLayerIter 50; nRelaxedIter 20;
}}

meshQualityControls
{{
    maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 3.5;
    maxConcave 80; minVol 1e-16; minTetQuality 1e-15; minArea -1;
    minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.03; minVolRatio 0.01;
    minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75;
    relaxed {{ maxNonOrtho 70; minDeterminant 0.001; }}
}}

mergeTolerance 1e-6;
writeFlags (noRefinement);
"""
    w(os.path.join(a.case, "system", "snappyHexMeshDict"),
      "dictionary", "snappyHexMeshDict", snappy)

    w(os.path.join(a.case, "system", "controlDict"), "dictionary", "controlDict",
      "application simpleFoam;\nstartFrom startTime;\nstartTime 0;\nstopAt endTime;\n"
      "endTime 1;\ndeltaT 1;\nwriteControl timeStep;\nwriteInterval 1;\n"
      "purgeWrite 0;\nwriteFormat ascii;\nwritePrecision 8;\nrunTimeModifiable false;\n")
    for f, cls, obj in (("fvSchemes", "dictionary", "fvSchemes"),
                        ("fvSolution", "dictionary", "fvSolution")):
        src = os.path.join(A1, "..", "SUBOFF_A1", "system", f)
        dst = os.path.join(a.case, "system", f)
        if os.path.isfile(src):
            shutil.copy(src, dst)
        else:
            w(dst, cls, obj, "// placeholder; setup_solve.py writes the solve dicts\n")

    man = {
        "arm": "SUBOFF A1d -- BARE HULL, 3-D half model, pitch sweep",
        "prereg": "verification/campaign/SUBOFF_A1d_BAREHULL_PREREGISTRATION.md",
        "geometry_source_module": geom_src,
        "geometry_source_paper": "Groves, Huang, Chang 1989, DTRC/SHD-1298-01 (AD-A210 642)",
        "geometry_cross_check": "Roddy 1990 DTRC/SHD-1298-08 Table 2, 25 stations, "
                                "GATE X5 PASS at 0.081 % worst "
                                "(cases/navier_class/SUBOFF_A1d/check_barehull_geometry.py)",
        "hull_function_reused_not_copied": "build_suboff_a1_geometry.build_hull_stl -- the "
                                           "SAME function GATE X5 validated",
        "level": a.level, "d0_m": d0, "hull_level": l_hull,
        "tail_box_level": l_tail, "nLayers": nlay,
        "hull_tris": n_tris,
        "L_m": L_m, "Rmax_m": geom.RMAX_FT * ft2m,
        "expected_patches": ["inlet", "outlet", "farfield", "symm", "hull"],
        "sail_present": False,
        "half_model": "symmetry plane at z = 0; a PITCH sweep preserves it",
        "block": {"nx": nx, "ny": ny, "nz": nz,
                  "xmin": a.xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax, "zmax": zmax},
    }
    with open(os.path.join(a.case, "GEOMETRY_MANIFEST.json"), "w") as fh:
        json.dump(man, fh, indent=2)

    print("A1d case emitted: %s" % a.case)
    print("  level %s  d0=%.5f m  hull lvl %d  tail box lvl %d  nLayers %d"
          % (a.level, d0, l_hull, l_tail, nlay))
    print("  hull.stl: %d triangles, closed nose and tail (both refused if not)" % n_tris)
    print("  block: %d x %d x %d  = %d background cells" % (nx, ny, nz, nx * ny * nz))
    print("  NOTHING HAS BEEN RUN. blockMesh/snappyHexMesh are build_barehull.sh's job.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
