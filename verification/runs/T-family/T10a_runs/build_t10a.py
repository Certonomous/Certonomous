#!/usr/bin/env python3
"""
T10a builder: view-factor radiation enclosures against exact S2S theory.

Writes every case named in T10a_registered.json -- dictionaries and 0.orig
fields only; blockMesh / checkMesh / viewFactorsGen are run by the build
driver so their wall times are recorded per case (they are mesh-side
preprocessing under Charter 2d; NO solver is run by anything in this file).
Written by the second instance on 2026-08-21, before the pre-registration
freeze and before any case existed, to the specification the first instance
registered in T10a_registered.json.

DESIGN NOTES THAT ARE DECISIONS, NOT DEFAULTS:

  * buoyantSimpleFoam, single region, laminar, g = (0 0 0), every wall
    fixedValue T (INTERPRETATION 2, approved).  The fluid is a carrier: with
    every wall temperature fixed, qr is determined by T, eps and F at the
    first radiation solve and cannot move afterwards.

  * THE SPHERE SHELL IS THE OUTER SIX BLOCKS of the v2606
    tutorials/mesh/blockMesh/sphere7ProjectedEdges topology with the inner
    block removed; vertices, all 24 curved edges AND both boundary faces are
    projected onto searchableSphere geometries at the registered radii.
    searchableSphere's nearest-point is analytic (r * unit vector), so the
    boundary vertices land on their radii to round-off, which is what
    check_t10a_mesh.py and the comparator assert (1e-9 relative refusal).

  * radiationProperties carries smoothing / constantEmissivity /
    useDirectSolver / nBands / solverFreq EXPLICITLY (none left to a
    default); viewFactorsDict carries the v2606 source defaults
    (GaussQuadTol 0.01, distTol 8, alpha 0.21, intTol 0.01) written out, with
    GaussQuadTol 0.001 in the *_q twins.  NO faceAgglomerate is run
    (INTERPRETATION 4): finalAgglom is absent, so viewFactorsGen and the
    model fall back to the identity and every mesh face radiates.

  * writeInterval 5 STRICTLY LESS than endTime 20, purgeWrite 0 (L-140);
    NO residualControl (L-141): convergence is judged from written
    checkpoints by the frozen comparator, never by the solver.

  * H_2d (T10a-3, REPORTED ONLY) uses createViewFactors, which auto-selects
    viewFactorHottel (crossed strings) for 2D meshes; its viewFactorsDict
    needs that utility's entries (raySearchEngine voxel, agglomerate false,
    nRayPerFace, writeViewFactors), not viewFactorsGen's.
"""
import json
import math
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, "T10a_registered.json")))

SP = REG["spheres"]
BX = REG["box"]
H2 = REG["hottel_2d_reported_only"]
SOL = REG["solver"]

END_TIME = SOL["endTime"]                 # 20
WRITE_INTERVAL = SOL["writeInterval"]     # 5, STRICTLY < endTime (L-140)
assert WRITE_INTERVAL < END_TIME
H2_THICKNESS = 0.05                       # empty-direction depth, cosmetic


def header(cls, obj, loc):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
"""


# ---------------------------------------------------------------------------
# meshes
# ---------------------------------------------------------------------------
def sphere_block_mesh(N, nr):
    r1, r2 = SP["r1"], SP["r2"]
    vi = r1 / math.sqrt(3.0)
    vo = r2 / math.sqrt(3.0)
    corners = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
               (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
    verts = "\n".join(
        f"    project ({sx*vi:.16g} {sy*vi:.16g} {sz*vi:.16g}) (sphereInner)"
        for sx, sy, sz in corners) + "\n" + "\n".join(
        f"    project ({sx*vo:.16g} {sy*vo:.16g} {sz*vo:.16g}) (sphereOuter)"
        for sx, sy, sz in corners)
    inner_edges = [(0, 1), (2, 3), (6, 7), (4, 5), (0, 3), (1, 2), (5, 6),
                   (4, 7), (0, 4), (1, 5), (2, 6), (3, 7)]
    outer_edges = [(a + 8, b + 8) for a, b in inner_edges]
    edges = "\n".join(f"    project {a} {b} (sphereOuter)" for a, b in outer_edges) \
        + "\n" + "\n".join(f"    project {a} {b} (sphereInner)" for a, b in inner_edges)
    # the six outer blocks of sphere7ProjectedEdges, inner block removed.
    blocks = [("( 8  0  3 11 12  4  7 15)", f"({nr} {N} {N})"),   # x-min
              ("( 1  9 10  2  5 13 14  6)", f"({nr} {N} {N})"),   # x-max
              ("( 8  9  1  0 12 13  5  4)", f"({N} {nr} {N})"),   # y-min
              ("( 3  2 10 11  7  6 14 15)", f"({N} {nr} {N})"),   # y-max
              ("( 8  9 10 11  0  1  2  3)", f"({N} {N} {nr})"),   # z-min
              ("( 4  5  6  7 12 13 14 15)", f"({N} {N} {nr})")]   # z-max
    btxt = "\n".join(f"    hex {h} {d} grading (1 1 1)" for h, d in blocks)
    # projected faces and patch faces are given as VERTEX QUADS, ordered so
    # the right-hand normal points OUT of the shell domain.  (block face)
    # pairs are not usable here: blockMesh's duplicate-curved-face check
    # compares them as unordered vertex sets, so (0 1) collides with (1 0).
    outer_faces = ["(8 12 15 11)", "(9 10 14 13)", "(8 9 13 12)",
                   "(11 15 14 10)", "(8 11 10 9)", "(12 13 14 15)"]
    inner_faces = ["(0 3 7 4)", "(1 5 6 2)", "(0 4 5 1)",
                   "(3 2 6 7)", "(0 1 2 3)", "(4 7 6 5)"]
    fouter = "\n".join(f"    project {q} sphereOuter" for q in outer_faces)
    finner = "\n".join(f"    project {q} sphereInner" for q in inner_faces)
    pouter = " ".join(outer_faces)
    pinner = " ".join(inner_faces)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

geometry
{{
    sphereInner {{ type sphere; origin (0 0 0); radius {r1:.16g}; }}
    sphereOuter {{ type sphere; origin (0 0 0); radius {r2:.16g}; }}
}}

vertices
(
{verts}
);

blocks
(
{btxt}
);

edges
(
{edges}
);

faces
(
{fouter}
{finner}
);

boundary
(
    inner
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( {pinner} );
    }}
    outer
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( {pouter} );
    }}
);

mergePatchPairs ();
"""


def box_block_mesh(N):
    Lx, Ly, Lz = BX["Lx"], BX["Ly"], BX["Lz"]
    nx, ny, nz = N, N, N // 2
    assert nz * 2 == N
    V = [(0, 0, 0), (Lx, 0, 0), (Lx, Ly, 0), (0, Ly, 0),
         (0, 0, Lz), (Lx, 0, Lz), (Lx, Ly, Lz), (0, Ly, Lz)]
    vtxt = "\n".join(f"    ({a:.10g} {b:.10g} {c:.10g})" for a, b, c in V)
    P = [("floor", "(0 3 2 1)"), ("ceiling", "(4 5 6 7)"),
         ("x0", "(0 4 7 3)"), ("x1", "(1 2 6 5)"),
         ("y0", "(0 1 5 4)"), ("y1", "(3 7 6 2)")]
    btxt = "\n".join(
        f"""    {n}
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( {f} );
    }}""" for n, f in P)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
{vtxt}
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) grading (1 1 1)
);

edges ();

faces ();

boundary
(
{btxt}
);

mergePatchPairs ();
"""


def hottel_block_mesh(N):
    w, h, d = H2["w"], H2["h"], H2_THICKNESS
    nx, ny = N, N // 2
    V = [(0, 0, 0), (w, 0, 0), (w, h, 0), (0, h, 0),
         (0, 0, d), (w, 0, d), (w, h, d), (0, h, d)]
    vtxt = "\n".join(f"    ({a:.10g} {b:.10g} {c:.10g})" for a, b, c in V)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
{vtxt}
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) grading (1 1 1)
);

edges ();

faces ();

boundary
(
    floor
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( (0 1 5 4) );
    }}
    ceiling
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( (3 7 6 2) );
    }}
    x0
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( (0 4 7 3) );
    }}
    x1
    {{
        type wall;
        inGroups (wall viewFactorWall);
        faces ( (1 2 6 5) );
    }}
    frontAndBack
    {{
        type empty;
        faces ( (0 3 2 1) (4 5 6 7) );
    }}
);

mergePatchPairs ();
"""


# ---------------------------------------------------------------------------
# constant/
# ---------------------------------------------------------------------------
def gravity():
    return header("uniformDimensionedVectorField", "g", "constant") + """
dimensions      [0 1 -2 0 0 0 0];
value           (0 0 0);
"""


def thermo():
    return header("dictionary", "thermophysicalProperties", "constant") + """
thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

pRef            100000;

mixture
{
    specie
    {
        molWeight       28.9;
    }
    thermodynamics
    {
        Cp              1000;
        Hf              0;
    }
    transport
    {
        mu              1.8e-05;
        Pr              0.7;
    }
}
"""


def turbulence():
    return header("dictionary", "turbulenceProperties", "constant") + """
simulationType  laminar;
"""


def radiation_props(smoothing):
    return header("dictionary", "radiationProperties", "constant") + f"""
// Every entry the model reads is written out; none is left to a default.
radiation       on;

radiationModel  viewFactor;

viewFactorCoeffs
{{
    smoothing           {'true' if smoothing else 'false'};
    constantEmissivity  true;
    useDirectSolver     true;
    nBands              1;
}}

solverFreq      1;

absorptionEmissionModel none;

scatterModel    none;

sootModel       none;
"""


def boundary_radiation(patch_eps):
    body = "\n".join(
        f"""{p}
{{
    type            lookup;
    emissivity      {e:.10g};
    absorptivity    {e:.10g};
}}
""" for p, e in patch_eps)
    return header("dictionary", "boundaryRadiationProperties", "constant") + "\n" + body


def view_factors_dict_gen(gauss_quad_tol):
    return header("dictionary", "viewFactorsDict", "constant") + f"""
// viewFactorsGen (3D, 2AI/2LI).  The v2606 source defaults written out
// explicitly; GaussQuadTol is 0.001 in the *_q quadrature-floor twins.
writeViewFactorMatrix   true;
GaussQuadTol            {gauss_quad_tol:.10g};
distTol                 8;
alpha                   0.21;
intTol                  0.01;
"""


def view_factors_dict_hottel():
    return header("dictionary", "viewFactorsDict", "constant") + """
// createViewFactors: auto-selects viewFactorHottel (crossed strings) on a
// 2D mesh.  These are that utility's mandatory entries.
raySearchEngine         voxel;
agglomerate             false;
nRayPerFace             100;
writeViewFactors        true;
"""


# ---------------------------------------------------------------------------
# system/
# ---------------------------------------------------------------------------
def control_dict():
    return header("dictionary", "controlDict", "system") + f"""
application     buoyantSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          1;
writeControl    timeStep;
writeInterval   {WRITE_INTERVAL};
purgeWrite      0;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""


def fv_schemes():
    return header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss upwind;
    div(phi,K)      bounded Gauss upwind;
    div(phi,h)      bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
"""


def fv_solution():
    # NO residualControl (L-141): endTime governs; the frozen comparator
    # judges convergence from the last two written checkpoints of qr.
    return header("dictionary", "fvSolution", "system") + """
solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0.01;
    }
    "(U|h)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-08;
        relTol          0.1;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;
    pRefCell        0;
    pRefValue       100000;
}

relaxationFactors
{
    fields
    {
        rho             1.0;
        p_rgh           0.7;
    }
    equations
    {
        U               0.3;
        h               0.7;
    }
}
"""


# ---------------------------------------------------------------------------
# 0.orig/
# ---------------------------------------------------------------------------
def field_T(patch_T, empty=(), T0=None):
    T0 = T0 if T0 is not None else sum(t for _, t in patch_T) / len(patch_T)
    body = "\n".join(f"    {p} {{ type fixedValue; value uniform {t:.10g}; }}"
                     for p, t in patch_T)
    body += "".join(f"\n    {p} {{ type empty; }}" for p in empty)
    return header("volScalarField", "T", "0") + f"""
dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T0:.10g};
boundaryField
{{
{body}
}}
"""


def field_U(patches, empty=()):
    body = "\n".join(f"    {p} {{ type noSlip; }}" for p in patches)
    body += "".join(f"\n    {p} {{ type empty; }}" for p in empty)
    return header("volVectorField", "U", "0") + f"""
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{{
{body}
}}
"""


def field_p_rgh(patches, empty=()):
    body = "\n".join(f"    {p} {{ type fixedFluxPressure; value uniform 100000; }}"
                     for p in patches)
    body += "".join(f"\n    {p} {{ type empty; }}" for p in empty)
    return header("volScalarField", "p_rgh", "0") + f"""
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 100000;
boundaryField
{{
{body}
}}
"""


def field_p(patches, empty=()):
    body = "\n".join(f"    {p} {{ type calculated; value uniform 100000; }}"
                     for p in patches)
    body += "".join(f"\n    {p} {{ type empty; }}" for p in empty)
    return header("volScalarField", "p", "0") + f"""
dimensions      [1 -1 -2 0 0 0 0];
internalField   uniform 100000;
boundaryField
{{
{body}
}}
"""


def field_qr(patches, empty=()):
    body = "\n".join(
        f"""    {p}
    {{
        type            greyDiffusiveRadiationViewFactor;
        qro             uniform 0;
        value           uniform 0;
    }}""" for p in patches)
    body += "".join(f"\n    {p} {{ type empty; }}" for p in empty)
    return header("volScalarField", "qr", "0") + f"""
dimensions      [1 0 -3 0 0 0 0];
internalField   uniform 0;
boundaryField
{{
{body}
}}
"""


# ---------------------------------------------------------------------------
def case_spec(name, c):
    """patches [(name, T, eps)], empty patches, mesh text, generator."""
    if c["kind"] == "spheres":
        e1, e2 = c["eps"]
        patches = [("inner", SP["T1"], e1), ("outer", SP["T2"], e2)]
        return patches, (), sphere_block_mesh(c["N"], c["nr"]), "viewFactorsGen"
    if c["kind"] == "box":
        Tu = c.get("T_uniform")
        patches = [(p, (Tu if Tu is not None else BX["patches"][p]["T"]), BX["eps"])
                   for p in ("floor", "ceiling", "x0", "x1", "y0", "y1")]
        return patches, (), box_block_mesh(c["N"]), "viewFactorsGen"
    # hottel
    patches = [("floor", H2["T_floor"], 1.0), ("ceiling", H2["T_ceiling"], 1.0),
               ("x0", H2["T_wall"], 1.0), ("x1", H2["T_wall"], 1.0)]
    return patches, ("frontAndBack",), hottel_block_mesh(c["N"]), "createViewFactors"


def case_txt(name, c, patches, generator):
    lines = [f"case              {name}",
             "rung              T10a (view-factor enclosures vs exact S2S theory, EXACT tier)",
             f"kind              {c['kind']}",
             f"role              {c['role']}",
             "solver            buoyantSimpleFoam (ESI v2606), laminar, g = (0 0 0), carrier fluid",
             f"generator         {generator} (preprocessing; run at build, wall time in BUILD.txt)",
             f"endTime           {END_TIME}",
             f"writeInterval     {WRITE_INTERVAL}  (strictly less than endTime, L-140)",
             "residualControl   none (L-141; convergence from written checkpoints of qr)",
             f"registered_faces  {c.get('faces')}",
             f"registered_cells  {c.get('cells')}"]
    if c["kind"] == "spheres":
        lines += [f"r1 r2             {SP['r1']} {SP['r2']} m",
                  f"N nr              {c['N']} {c['nr']}",
                  f"GaussQuadTol      {c['GaussQuadTol']}",
                  f"smoothing         {c['smoothing']}"]
    elif c["kind"] == "box":
        lines += [f"Lx Ly Lz          {BX['Lx']} {BX['Ly']} {BX['Lz']} m",
                  f"N per m           {c['N']}",
                  f"GaussQuadTol      {c['GaussQuadTol']}",
                  f"smoothing         {c['smoothing']}"]
    for p, t, e in patches:
        lines.append(f"patch             {p}: T = {t} K, emissivity = {e}")
    return "\n".join(lines) + "\n"


def main():
    made = []
    for name, c in REG["cases"].items():
        d = os.path.join(HERE, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        for sub in ("0.orig", "constant", "system"):
            os.makedirs(os.path.join(d, sub))
        w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)
        patches, empty, mesh_txt, generator = case_spec(name, c)
        pnames = [p for p, _, _ in patches]
        w("system/blockMeshDict", mesh_txt)
        w("system/controlDict", control_dict())
        w("system/fvSchemes", fv_schemes())
        w("system/fvSolution", fv_solution())
        w("constant/g", gravity())
        w("constant/thermophysicalProperties", thermo())
        w("constant/turbulenceProperties", turbulence())
        w("constant/radiationProperties", radiation_props(c.get("smoothing", False)))
        w("constant/boundaryRadiationProperties",
          boundary_radiation([(p, e) for p, _, e in patches]))
        if generator == "viewFactorsGen":
            w("constant/viewFactorsDict", view_factors_dict_gen(c["GaussQuadTol"]))
        else:
            w("constant/viewFactorsDict", view_factors_dict_hottel())
        w("0.orig/T", field_T([(p, t) for p, t, _ in patches], empty))
        w("0.orig/U", field_U(pnames, empty))
        w("0.orig/p_rgh", field_p_rgh(pnames, empty))
        w("0.orig/p", field_p(pnames, empty))
        w("0.orig/qr", field_qr(pnames, empty))
        w("CASE.txt", case_txt(name, c, patches, generator))
        made.append((name, c))
    print(f"T10a: {len(made)} cases built in {HERE}")
    print(f"  endTime {END_TIME}, writeInterval {WRITE_INTERVAL} (STRICTLY less), purgeWrite 0")
    print(f"  {'case':7s} {'kind':8s} {'faces':>6s} {'cells':>6s}  role")
    for n, c in made:
        print(f"  {n:7s} {c['kind']:8s} {c.get('faces', 0):6d} {c.get('cells', 0):6d}  {c['role']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
