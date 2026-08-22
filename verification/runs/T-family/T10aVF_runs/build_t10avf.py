#!/usr/bin/env python3
"""
T10a-VF clean-room case builder.

Builds minimal, self-contained OpenFOAM cases whose ONLY purpose is to run
`viewFactorsGen` and write `constant/F`.  No solver is ever invoked and no
0/ directory is written.

Mesh route: blockMesh only, exactly the route used by T10a
(`verification/runs/T-family/T10a_runs/build_t10avf.py` -> sphere_block_mesh /
box_block_mesh), i.e. searchableSurface `project` for the curved geometries and
plain hexes for the flat ones.  No snappyHexMesh anywhere.

Geometries
  BOX    closed cube, 6 flat wall patches                    (convex enclosure)
  SHELL  concentric cubes, flat inner body in a flat box     (convex both)
  SPH    concentric spheres r1=0.05 r2=0.1  (T10a "S" route) (outer concave)
  BALL   solid sphere R=0.1, one patch                       (fully concave)
  CYL    closed cylinder R=0.1 H=0.2                         (side concave)

Every case is a directory holding system/{blockMeshDict,controlDict,fvSchemes,
fvSolution} and constant/viewFactorsDict.  Nothing else is needed: the utility
picks its patches out of the `viewFactorWall` inGroup.
"""
import math, os, json, argparse

R_OUT = 0.1
R_IN = 0.05
BOX_L = 1.0
CYL_R = 0.1
CYL_H = 0.2

ALPHA_EXACT = math.exp(-1.5)   # 0.22313016014842982


def header(cls, obj, loc):
    return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    object      {obj};
    location    "{loc}";
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""


CORNERS = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
           (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]

# 6 shell blocks, T10a ordering (inner cube 0..7, outer cube 8..15)
SHELL_BLOCKS = [("( 8  0  3 11 12  4  7 15)", "r N N"),
                ("( 1  9 10  2  5 13 14  6)", "r N N"),
                ("( 8  9  1  0 12 13  5  4)", "N r N"),
                ("( 3  2 10 11  7  6 14 15)", "N r N"),
                ("( 8  9 10 11  0  1  2  3)", "N N r"),
                ("( 4  5  6  7 12 13 14 15)", "N N r")]
OUTER_FACES = ["(8 12 15 11)", "(9 10 14 13)", "(8 9 13 12)",
               "(11 15 14 10)", "(8 11 10 9)", "(12 13 14 15)"]
INNER_FACES = ["(0 3 7 4)", "(1 5 6 2)", "(0 4 5 1)",
               "(3 2 6 7)", "(0 1 2 3)", "(4 7 6 5)"]
INNER_EDGES = [(0, 1), (2, 3), (6, 7), (4, 5), (0, 3), (1, 2), (5, 6),
               (4, 7), (0, 4), (1, 5), (2, 6), (3, 7)]


def _blocks(nr, N):
    out = []
    for h, d in SHELL_BLOCKS:
        dd = d.replace("r", str(nr)).replace("N", str(N))
        out.append(f"    hex {h} ({dd}) grading (1 1 1)")
    return "\n".join(out)


def _patch(name, faces):
    return (f"    {name}\n    {{\n        type wall;\n"
            f"        inGroups (wall viewFactorWall);\n"
            f"        faces ( {faces} );\n    }}")


def sph_dict(nr, N):
    vi, vo = R_IN / math.sqrt(3.0), R_OUT / math.sqrt(3.0)
    verts = "\n".join(f"    project ({sx*vi:.16g} {sy*vi:.16g} {sz*vi:.16g}) (sphereInner)"
                      for sx, sy, sz in CORNERS) + "\n" + \
            "\n".join(f"    project ({sx*vo:.16g} {sy*vo:.16g} {sz*vo:.16g}) (sphereOuter)"
                      for sx, sy, sz in CORNERS)
    edges = "\n".join(f"    project {a+8} {b+8} (sphereOuter)" for a, b in INNER_EDGES) \
        + "\n" + "\n".join(f"    project {a} {b} (sphereInner)" for a, b in INNER_EDGES)
    faces = "\n".join(f"    project {q} sphereOuter" for q in OUTER_FACES) + "\n" + \
            "\n".join(f"    project {q} sphereInner" for q in INNER_FACES)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

geometry
{{
    sphereInner {{ type sphere; origin (0 0 0); radius {R_IN:.16g}; }}
    sphereOuter {{ type sphere; origin (0 0 0); radius {R_OUT:.16g}; }}
}}

vertices
(
{verts}
);

blocks
(
{_blocks(nr, N)}
);

edges
(
{edges}
);

faces
(
{faces}
);

boundary
(
{_patch("inner", " ".join(INNER_FACES))}
{_patch("outer", " ".join(OUTER_FACES))}
);

mergePatchPairs ();
"""


def ball_dict(nr, N):
    """Solid sphere: the 6 shell blocks plus the inner cube as a plain core."""
    vi, vo = R_IN / math.sqrt(3.0), R_OUT / math.sqrt(3.0)
    verts = "\n".join(f"    ({sx*vi:.16g} {sy*vi:.16g} {sz*vi:.16g})"
                      for sx, sy, sz in CORNERS) + "\n" + \
            "\n".join(f"    project ({sx*vo:.16g} {sy*vo:.16g} {sz*vo:.16g}) (sphereOuter)"
                      for sx, sy, sz in CORNERS)
    edges = "\n".join(f"    project {a+8} {b+8} (sphereOuter)" for a, b in INNER_EDGES)
    faces = "\n".join(f"    project {q} sphereOuter" for q in OUTER_FACES)
    core = f"    hex (0 1 2 3 4 5 6 7) ({N} {N} {N}) grading (1 1 1)"
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

geometry
{{
    sphereOuter {{ type sphere; origin (0 0 0); radius {R_OUT:.16g}; }}
}}

vertices
(
{verts}
);

blocks
(
{_blocks(nr, N)}
{core}
);

edges
(
{edges}
);

faces
(
{faces}
);

boundary
(
{_patch("outer", " ".join(OUTER_FACES))}
);

mergePatchPairs ();
"""


def shell_dict(nr, N):
    """Concentric cubes: shell topology, no projection anywhere."""
    a, b = BOX_L / 4.0, BOX_L / 2.0
    verts = "\n".join(f"    ({sx*a:.16g} {sy*a:.16g} {sz*a:.16g})" for sx, sy, sz in CORNERS) \
        + "\n" + "\n".join(f"    ({sx*b:.16g} {sy*b:.16g} {sz*b:.16g})" for sx, sy, sz in CORNERS)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
{verts}
);

blocks
(
{_blocks(nr, N)}
);

edges ();

faces ();

boundary
(
{_patch("inner", " ".join(INNER_FACES))}
{_patch("outer", " ".join(OUTER_FACES))}
);

mergePatchPairs ();
"""


def box_dict(N):
    L = BOX_L
    V = [(0, 0, 0), (L, 0, 0), (L, L, 0), (0, L, 0),
         (0, 0, L), (L, 0, L), (L, L, L), (0, L, L)]
    vtxt = "\n".join(f"    ({x:.10g} {y:.10g} {z:.10g})" for x, y, z in V)
    P = [("floor", "(0 3 2 1)"), ("ceiling", "(4 5 6 7)"),
         ("x0", "(0 4 7 3)"), ("x1", "(1 2 6 5)"),
         ("y0", "(0 1 5 4)"), ("y1", "(3 7 6 2)")]
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
{vtxt}
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({N} {N} {N}) grading (1 1 1)
);

edges ();

faces ();

boundary
(
{chr(10).join(_patch(n, f) for n, f in P)}
);

mergePatchPairs ();
"""


def cyl_dict(N, Nz):
    """Closed cylinder from ONE hex block whose 4 lateral faces are projected
    onto a searchable cylinder -- the route of tutorials/mesh/blockMesh/pipe."""
    c = CYL_R / math.sqrt(2.0)
    V = [(-c, -c, 0), (c, -c, 0), (c, c, 0), (-c, c, 0),
         (-c, -c, CYL_H), (c, -c, CYL_H), (c, c, CYL_H), (-c, c, CYL_H)]
    vtxt = "\n".join(f"    project ({x:.16g} {y:.16g} {z:.16g}) (cyl)" for x, y, z in V)
    lat = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)]
    edges = "\n".join(f"    project {a} {b} (cyl)" for a, b in lat)
    side_faces = ["(0 1 5 4)", "(1 2 6 5)", "(2 3 7 6)", "(3 0 4 7)"]
    faces = "\n".join(f"    project {q} cyl" for q in side_faces)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

geometry
{{
    cyl
    {{
        type   cylinder;
        point1 (0 0 {-CYL_H:.16g});
        point2 (0 0 {2*CYL_H:.16g});
        radius {CYL_R:.16g};
    }}
}}

vertices
(
{vtxt}
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({N} {N} {Nz}) grading (1 1 1)
);

edges
(
{edges}
);

faces
(
{faces}
);

boundary
(
{_patch("side", " ".join(side_faces))}
{_patch("ends", "(0 3 2 1) (4 5 6 7)")}
);

mergePatchPairs ();
"""


def vf_dict(alpha, gauss, distTol, intTol, agglom):
    agg = ""
    if agglom:
        agg = f"""
writeFacesAgglomeration   false;
patchAgglomeration
{{
    viewFactorWall
    {{
        nFacesInCoarsestLevel   {agglom};
        featureAngle            10;
    }}
}}
"""
    return header("dictionary", "viewFactorsDict", "constant") + f"""
// viewFactorsGen (3D, 2AI/2LI).  The four quadrature keys the utility reads
// with getOrDefault (viewFactorsGen.C:476-486) are written out explicitly so
// that no case depends on a compiled-in default.
writeViewFactorMatrix     true;
writePatchViewFactors     false;
dumpRays                  false;
debug                     0;
maxDynListLength          200000;

GaussQuadTol              {gauss:.12g};
distTol                   {distTol:.12g};
alpha                     {alpha:.17g};
intTol                    {intTol:.12g};
{agg}
// ************************************************************************* //
"""


CONTROL = header("dictionary", "controlDict", "system") + """
application     none;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

// ************************************************************************* //
"""

FVSCHEMES = header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }

// ************************************************************************* //
"""

FVSOLUTION = header("dictionary", "fvSolution", "system") + """
solvers { }

// ************************************************************************* //
"""


def geom_dict(geom, p):
    if geom == "SPH":
        return sph_dict(p["nr"], p["N"])
    if geom == "BALL":
        return ball_dict(p["nr"], p["N"])
    if geom == "SHELL":
        return shell_dict(p["nr"], p["N"])
    if geom == "BOX":
        return box_dict(p["N"])
    if geom == "CYL":
        return cyl_dict(p["N"], p["Nz"])
    raise ValueError(geom)


def nfaces(geom, p):
    N, nr = p.get("N"), p.get("nr")
    if geom in ("SPH", "SHELL"):
        return 2 * 6 * N * N
    if geom == "BALL":
        return 6 * N * N
    if geom == "BOX":
        return 6 * N * N
    if geom == "CYL":
        return 4 * N * p["Nz"] + 2 * N * N
    raise ValueError(geom)


def build(root, name, geom, p, alpha=0.21, gauss=0.01, distTol=8.0,
          intTol=0.01, agglom=0):
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    os.makedirs(os.path.join(d, "constant"), exist_ok=True)
    open(os.path.join(d, "system", "blockMeshDict"), "w").write(geom_dict(geom, p))
    open(os.path.join(d, "system", "controlDict"), "w").write(CONTROL)
    open(os.path.join(d, "system", "fvSchemes"), "w").write(FVSCHEMES)
    open(os.path.join(d, "system", "fvSolution"), "w").write(FVSOLUTION)
    open(os.path.join(d, "constant", "viewFactorsDict"), "w").write(
        vf_dict(alpha, gauss, distTol, intTol, agglom))
    meta = dict(name=name, geom=geom, params=p, alpha=alpha,
                GaussQuadTol=gauss, distTol=distTol, intTol=intTol,
                agglomeration=agglom, nFacesExpected=nfaces(geom, p))
    open(os.path.join(d, "CASE.json"), "w").write(json.dumps(meta, indent=2) + "\n")
    return meta


# ---------------------------------------------------------------- case list --

def case_list():
    A = 0.21
    AE = ALPHA_EXACT
    C = []
    # ---- Sweep 1: mesh family, concentric spheres, identical settings -------
    for tag, nr, N in [("L1", 4, 8), ("L2", 6, 12), ("L3", 8, 16), ("L4", 10, 20)]:
        C.append((f"S1_SPH_{tag}", "SPH", dict(nr=nr, N=N), A, 0.01, 8.0, 0.01, 0))
        C.append((f"S1_SPH_{tag}_afix", "SPH", dict(nr=nr, N=N), AE, 0.01, 8.0, 0.01, 0))
    # ---- Sweep 2: geometry / convexity -------------------------------------
    for tag, N in [("c", 8), ("f", 16)]:
        C.append((f"S2_BOX_{tag}", "BOX", dict(N=N), A, 0.01, 8.0, 0.01, 0))
        C.append((f"S2_SHELL_{tag}", "SHELL", dict(nr=max(3, N // 2), N=N), A, 0.01, 8.0, 0.01, 0))
        C.append((f"S2_BALL_{tag}", "BALL", dict(nr=max(3, N // 2), N=N), A, 0.01, 8.0, 0.01, 0))
        C.append((f"S2_CYL_{tag}", "CYL", dict(N=N, Nz=N), A, 0.01, 8.0, 0.01, 0))
    for g, N in [("BOX", 16), ("SHELL", 16), ("BALL", 16), ("CYL", 16)]:
        p = dict(N=N) if g == "BOX" else (dict(N=N, Nz=N) if g == "CYL"
                                          else dict(nr=N // 2, N=N))
        C.append((f"S2_{g}_f_afix", g, p, AE, 0.01, 8.0, 0.01, 0))
    # ---- Sweep 3: generator knobs, fixed mesh (SPH L2) ----------------------
    M = dict(nr=6, N=12)
    for a in [0.10, 0.15, 0.20, 0.22, 0.25, 0.30]:
        C.append((f"S3_alpha_{a:.3f}".replace(".", "p"), "SPH", M, a, 0.01, 8.0, 0.01, 0))
    for g in [0.001, 1e-6]:
        C.append((f"S3_gauss_{g:g}".replace(".", "p").replace("-", "m"),
                  "SPH", M, A, g, 8.0, 0.01, 0))
    for d in [1.0, 4.0, 100.0]:
        C.append((f"S3_dist_{d:g}", "SPH", M, A, 0.01, d, 0.01, 0))
    C.append(("S3_intTol_1em4", "SPH", M, A, 0.01, 8.0, 1e-4, 0))
    C.append(("S3_agglom_10", "SPH", M, A, 0.01, 8.0, 0.01, 10))
    C.append(("S3_agglom_10_afix", "SPH", M, AE, 0.01, 8.0, 0.01, 10))
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "cases"))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    C = case_list()
    if a.list:
        tot = 0
        for nm, g, p, al, gq, dt, it, ag in C:
            n = nfaces(g, p)
            tot += n * n
            print("%-26s %-6s %-22s n=%5d  alpha=%.6f gauss=%g dist=%g int=%g agg=%d"
                  % (nm, g, p, n, al, gq, dt, it, ag))
        print("\n%d cases, sum n^2 = %.3e" % (len(C), tot))
        print("T10a anchor: 9.4 core-min for sum n^2 = 4.00e8  ->  %.2f core-min"
              % (9.4 * tot / 4.00e8))
        return
    os.makedirs(a.root, exist_ok=True)
    for nm, g, p, al, gq, dt, it, ag in C:
        m = build(a.root, nm, g, p, al, gq, dt, it, ag)
        print("built %-26s n=%5d" % (nm, m["nFacesExpected"]))


if __name__ == "__main__":
    main()
