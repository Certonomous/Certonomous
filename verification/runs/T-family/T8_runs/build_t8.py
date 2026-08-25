#!/usr/bin/env python3
"""
T8 case builder -- MTT pure-plume self-similarity, axisymmetric wedge.

WRITTEN BEFORE THE PRE-REGISTRATION WAS FROZEN AND BEFORE ANY CASE EXISTED.
It writes dictionaries, `0.orig` and NOTHING ELSE.  It NEVER writes `0/` and
it NEVER writes a time directory: `0/` is created only at launch, by
`run_one_t8.sh`, which touches `0/T` LAST so that the age guard of
CLAUDE.md rule 4 can date the run.  A case whose `0/` already exists is
REFUSED by the launcher, not silently reused.

Registered geometry (T8_PREREGISTRATION.md sections 1 and 5):
  source diameter        D  = 0.2 m       (b0 = 0.1 m)
  domain radius          R  = 12 D = 2.4 m
  domain height          H  = 40 D = 8.0 m
  axisymmetric 5 deg wedge about the z axis, symmetric about the y = 0 plane,
  gravity (0 0 -9.81) m/s^2.

Radial block structure, chosen so that (i) the source patch edge r = b0 is a
BLOCK boundary and therefore an exact mesh face, and (ii) every level is
obtained by doubling the divisions of EVERY block in BOTH directions, so the
refinement ratio is EXACTLY 2 with no grading anywhere:

    block   r range        c    m    f      cell width c / m / f
      1     0.0 -> 0.1     4    8   16      0.0250 0.0125 0.00625
      2     0.1 -> 0.4    12   24   48      0.0250 0.0125 0.00625
      3     0.4 -> 1.2    16   32   64      0.0500 0.0250 0.01250
      4     1.2 -> 2.4     8   16   32      0.1500 0.0750 0.03750
    radial totals        40   80  160
    axial divisions     160  320  640      0.0500 0.0250 0.01250
    cells              6400 25600 102400

Usage:  python3 build_t8.py [--root DIR] [--levels c m f]
"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- registered constants (T8_PREREGISTRATION.md) --------------------------
D_SOURCE = 0.2                  # m, source diameter
B0 = D_SOURCE / 2.0             # m, source radius
R_DOMAIN = 12.0 * D_SOURCE      # m
H_DOMAIN = 40.0 * D_SOURCE      # m
WEDGE_HALF_ANGLE_DEG = 2.5

W0 = 0.6                        # m/s, source vertical velocity
ALPHA_NOMINAL = 0.12            # sets Gamma_0 = 1 only; NEVER graded
RI0 = 8.0 * ALPHA_NOMINAL / 5.0                 # = 0.192, pure-plume source
GPRIME0 = RI0 * W0 ** 2 / B0                    # = 0.6912 m/s^2
G_ACCEL = 9.81
TREF = 300.0
BETA = 1.0 / 300.0
DT0 = 21.1376                   # K, registered; = GPRIME0 / (g*beta) to 6 s.f.
T_SOURCE = TREF + DT0           # 321.1376 K
F0 = math.pi * B0 ** 2 * W0 * GPRIME0            # m^4/s^3, reported

NU = 1.5e-05
PR = 0.71
PRT = 0.85

TI = 0.05                       # source turbulence intensity
K0 = 1.5 * (TI * W0) ** 2                        # 1.35e-3 m^2/s^2
LMIX = 0.07 * D_SOURCE                           # 0.014 m
EPS0 = 0.09 ** 0.75 * K0 ** 1.5 / LMIX           # 5.8232e-4 m^2/s^3
K_AMB = 1.0e-06
EPS_AMB = 1.0e-06

R_STATIONS = (0.0, 0.1, 0.4, 1.2, 2.4)
LEVELS = {
    #        radial divisions per block            axial   endTime  writeInt
    "c": dict(nr=(4, 12, 16, 8),   nz=160, endTime=8000,  write=800),
    "m": dict(nr=(8, 24, 32, 16),  nz=320, endTime=12000, write=1200),
    "f": dict(nr=(16, 48, 64, 32), nz=640, endTime=20000, write=2000),
}
EXPECT_CELLS = {"c": 6400, "m": 25600, "f": 102400}

HEAD = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     |
    \\\\  /    A nd           | www.openfoam.com
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""
TAIL = "\n// ************************************************************************* //\n"


def write(path, cls, loc, obj, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HEAD.format(cls=cls, loc=loc, obj=obj))
        fh.write(body)
        fh.write(TAIL)


# ---------------------------------------------------------------------------
# blockMeshDict: 4 radial blocks x 1 axial block, 5 deg wedge about z
# ---------------------------------------------------------------------------
def block_mesh_dict(level):
    nr = LEVELS[level]["nr"]
    nz = LEVELS[level]["nz"]
    half = math.radians(WEDGE_HALF_ANGLE_DEG)
    c, s = math.cos(half), math.sin(half)

    # vertex ids
    #   axis:  A0 (r=0, z=0), A1 (r=0, z=H)   -- ONE vertex each, shared by
    #          the back and the front side, so the innermost block face at
    #          r = 0 COLLAPSES to an edge and no axis patch is created
    #          (the OpenFOAM wedge convention; LadenburgJet60psi tutorial).
    #   k>=1:  B(k,0) B(k,1) back (y<0);  F(k,0) F(k,1) front (y>0)
    verts, vid = [], {}

    def add(name, x, y, z):
        vid[name] = len(verts)
        verts.append((x, y, z))

    add("A0", 0.0, 0.0, 0.0)
    add("A1", 0.0, 0.0, H_DOMAIN)
    for k in range(1, 5):
        r = R_STATIONS[k]
        add(f"B{k}_0", r * c, -r * s, 0.0)
        add(f"B{k}_1", r * c, -r * s, H_DOMAIN)
        add(f"F{k}_0", r * c, +r * s, 0.0)
        add(f"F{k}_1", r * c, +r * s, H_DOMAIN)

    def inner(k, side, j):
        """id of the vertex at the INNER radius of block k, given side and z."""
        if k == 1:
            return vid["A0" if j == 0 else "A1"]
        return vid[f"{side}{k - 1}_{j}"]

    def outer(k, side, j):
        return vid[f"{side}{k}_{j}"]

    # Local block axes: x = radial (+X), y = axial (+Z), z = front->back (-Y).
    # (+X, +Z, -Y) is RIGHT-handed; (+X, +Z, +Y) is not, and blockMesh rejects
    # it as "inward-pointing faces".  Hence v0..v3 are the FRONT (y > 0) side.
    blocks = []
    for k in range(1, 5):
        v0, v1 = inner(k, "F", 0), outer(k, "F", 0)
        v2, v3 = outer(k, "F", 1), inner(k, "F", 1)
        v4, v5 = inner(k, "B", 0), outer(k, "B", 0)
        v6, v7 = outer(k, "B", 1), inner(k, "B", 1)
        blocks.append((k, (v0, v1, v2, v3, v4, v5, v6, v7), nr[k - 1], nz))

    def face_bottom(k):                      # z = 0
        return (inner(k, "B", 0), outer(k, "B", 0),
                outer(k, "F", 0), inner(k, "F", 0))

    def face_top(k):                         # z = H
        return (inner(k, "B", 1), outer(k, "B", 1),
                outer(k, "F", 1), inner(k, "F", 1))

    def face_outer(k):                       # r = R_STATIONS[k]
        return (outer(k, "B", 0), outer(k, "B", 1),
                outer(k, "F", 1), outer(k, "F", 0))

    def face_back(k):                        # y < 0
        return (inner(k, "B", 0), outer(k, "B", 0),
                outer(k, "B", 1), inner(k, "B", 1))

    def face_front(k):                       # y > 0
        return (inner(k, "F", 0), outer(k, "F", 0),
                outer(k, "F", 1), inner(k, "F", 1))

    def fstr(f):
        return "            (%d %d %d %d)\n" % f

    L = []
    L.append("mergeType points;   // wedge: merge coincident axis points\n\n")
    L.append("scale 1;\n\nvertices\n(\n")
    for (x, y, z) in verts:
        L.append("    (%.12f %.12f %.12f)\n" % (x, y, z))
    L.append(");\n\nblocks\n(\n")
    for k, vv, nrk, nzk in blocks:
        L.append("    hex (%d %d %d %d %d %d %d %d) (%d %d 1) "
                 "simpleGrading (1 1 1)\n" % (vv + (nrk, nzk)))
    L.append(");\n\nedges ();\n\nboundary\n(\n")

    L.append("    source\n    {\n        type patch;\n        faces\n        (\n")
    L.append(fstr(face_bottom(1)))
    L.append("        );\n    }\n\n")

    L.append("    floor\n    {\n        type wall;\n        faces\n        (\n")
    for k in (2, 3, 4):
        L.append(fstr(face_bottom(k)))
    L.append("        );\n    }\n\n")

    L.append("    outlet\n    {\n        type patch;\n        faces\n        (\n")
    for k in (1, 2, 3, 4):
        L.append(fstr(face_top(k)))
    L.append("        );\n    }\n\n")

    L.append("    farfield\n    {\n        type patch;\n        faces\n        (\n")
    L.append(fstr(face_outer(4)))
    L.append("        );\n    }\n\n")

    L.append("    wedge_back\n    {\n        type wedge;\n        faces\n        (\n")
    for k in (1, 2, 3, 4):
        L.append(fstr(face_back(k)))
    L.append("        );\n    }\n\n")

    L.append("    wedge_front\n    {\n        type wedge;\n        faces\n        (\n")
    for k in (1, 2, 3, 4):
        L.append(fstr(face_front(k)))
    L.append("        );\n    }\n);\n\nmergePatchPairs ();\n")
    return "".join(L)


# ---------------------------------------------------------------------------
# field templates
# ---------------------------------------------------------------------------
def field(dims, internal, entries):
    L = ["dimensions      %s;\n\ninternalField   uniform %s;\n\nboundaryField\n{\n"
         % (dims, internal)]
    for name, blk in entries:
        L.append("    %s\n    {\n" % name)
        for line in blk:
            L.append("        %s\n" % line)
        L.append("    }\n")
    L.append("}\n")
    return "".join(L)


def fields():
    W = ["type            wedge;"]
    out = {}

    out["U"] = ("volVectorField", field(
        "[0 1 -1 0 0 0 0]", "(0 0 0)", [
            ("source", ["type            fixedValue;",
                        "value           uniform (0 0 %.6f);" % W0]),
            ("floor", ["type            noSlip;"]),
            ("outlet", ["type            pressureInletOutletVelocity;",
                        "value           uniform (0 0 0);"]),
            ("farfield", ["type            pressureInletOutletVelocity;",
                          "value           uniform (0 0 0);"]),
            ("wedge_back", W), ("wedge_front", W)]))

    out["T"] = ("volScalarField", field(
        "[0 0 0 1 0 0 0]", "%.6f" % TREF, [
            ("source", ["type            fixedValue;",
                        "value           uniform %.6f;" % T_SOURCE]),
            ("floor", ["type            zeroGradient;"]),
            ("outlet", ["type            inletOutlet;",
                        "inletValue      uniform %.6f;" % TREF,
                        "value           uniform %.6f;" % TREF]),
            ("farfield", ["type            inletOutlet;",
                          "inletValue      uniform %.6f;" % TREF,
                          "value           uniform %.6f;" % TREF]),
            ("wedge_back", W), ("wedge_front", W)]))

    out["p_rgh"] = ("volScalarField", field(
        "[0 2 -2 0 0 0 0]", "0", [
            ("source", ["type            fixedFluxPressure;",
                        "value           uniform 0;"]),
            ("floor", ["type            fixedFluxPressure;",
                       "value           uniform 0;"]),
            ("outlet", ["type            fixedValue;",
                        "value           uniform 0;"]),
            ("farfield", ["type            fixedValue;",
                          "value           uniform 0;"]),
            ("wedge_back", W), ("wedge_front", W)]))

    out["k"] = ("volScalarField", field(
        "[0 2 -2 0 0 0 0]", "%.8g" % K_AMB, [
            ("source", ["type            fixedValue;",
                        "value           uniform %.8g;" % K0]),
            ("floor", ["type            kqRWallFunction;",
                       "value           uniform %.8g;" % K_AMB]),
            ("outlet", ["type            inletOutlet;",
                        "inletValue      uniform %.8g;" % K_AMB,
                        "value           uniform %.8g;" % K_AMB]),
            ("farfield", ["type            inletOutlet;",
                          "inletValue      uniform %.8g;" % K_AMB,
                          "value           uniform %.8g;" % K_AMB]),
            ("wedge_back", W), ("wedge_front", W)]))

    out["epsilon"] = ("volScalarField", field(
        "[0 2 -3 0 0 0 0]", "%.8g" % EPS_AMB, [
            ("source", ["type            fixedValue;",
                        "value           uniform %.8g;" % EPS0]),
            ("floor", ["type            epsilonWallFunction;",
                       "value           uniform %.8g;" % EPS_AMB]),
            ("outlet", ["type            inletOutlet;",
                        "inletValue      uniform %.8g;" % EPS_AMB,
                        "value           uniform %.8g;" % EPS_AMB]),
            ("farfield", ["type            inletOutlet;",
                          "inletValue      uniform %.8g;" % EPS_AMB,
                          "value           uniform %.8g;" % EPS_AMB]),
            ("wedge_back", W), ("wedge_front", W)]))

    out["nut"] = ("volScalarField", field(
        "[0 2 -1 0 0 0 0]", "0", [
            ("source", ["type            calculated;", "value           uniform 0;"]),
            ("floor", ["type            nutkWallFunction;",
                       "value           uniform 0;"]),
            ("outlet", ["type            calculated;", "value           uniform 0;"]),
            ("farfield", ["type            calculated;", "value           uniform 0;"]),
            ("wedge_back", W), ("wedge_front", W)]))

    out["alphat"] = ("volScalarField", field(
        "[0 2 -1 0 0 0 0]", "0", [
            ("source", ["type            calculated;", "value           uniform 0;"]),
            ("floor", ["type            calculated;", "value           uniform 0;"]),
            ("outlet", ["type            calculated;", "value           uniform 0;"]),
            ("farfield", ["type            calculated;", "value           uniform 0;"]),
            ("wedge_back", W), ("wedge_front", W)]))
    return out


def constant_files():
    g = ("uniformDimensionedVectorField",
         "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 -%.2f);\n" % G_ACCEL)
    tp = ("dictionary",
          "transportModel  Newtonian;\n\n"
          "nu              %.8g;\n"
          "beta            %.10g;\n"
          "TRef            %.6f;\n"
          "Pr              %.6g;\n"
          "Prt             %.6g;\n" % (NU, BETA, TREF, PR, PRT))
    turb = ("dictionary",
            "simulationType  RAS;\n\nRAS\n{\n"
            "    RASModel        kEpsilon;\n"
            "    turbulence      on;\n"
            "    printCoeffs     on;\n}\n")
    return {"g": g, "transportProperties": tp, "turbulenceProperties": turb}


def control_dict(level):
    L = LEVELS[level]
    return ("application     buoyantBoussinesqSimpleFoam;\n\n"
            "startFrom       startTime;\nstartTime       0;\n"
            "stopAt          endTime;\nendTime         %d;\ndeltaT          1;\n\n"
            "writeControl    timeStep;\nwriteInterval   %d;\npurgeWrite      2;\n"
            "writeFormat     ascii;\nwritePrecision  16;\nwriteCompression off;\n"
            "timeFormat      general;\ntimePrecision   6;\n"
            "runTimeModifiable false;\n" % (L["endTime"], L["write"]))


FV_SCHEMES = """ddtSchemes      { default steadyState; }

gradSchemes     { default Gauss linear; }

divSchemes
{
    default          none;
    div(phi,U)       bounded Gauss linearUpwind grad(U);
    div(phi,T)       bounded Gauss limitedLinear 1;
    div(phi,k)       bounded Gauss limitedLinear 1;
    div(phi,epsilon) bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes { default Gauss linear corrected; }

interpolationSchemes { default linear; }

snGradSchemes   { default corrected; }

wallDist        { method meshWave; }
"""

FV_SOLUTION = """solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-11;
        relTol          0.001;
    }

    "(U|T|k|epsilon)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-11;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

relaxationFactors
{
    fields    { p_rgh 0.3; }
    equations { U 0.5; T 0.5; k 0.5; epsilon 0.5; }
}
"""


def build(root, level):
    case = os.path.join(root, "T8_MTT_" + level)
    if os.path.isdir(os.path.join(case, "0")):
        print("REFUSE: %s already has a 0/ directory" % case)
        return 2
    times = [d for d in (os.listdir(case) if os.path.isdir(case) else [])
             if d.replace(".", "", 1).isdigit() and float(d) > 0]
    if times:
        print("REFUSE: %s already has time directories %s" % (case, sorted(times)))
        return 2

    write(os.path.join(case, "system", "blockMeshDict"),
          "dictionary", "system", "blockMeshDict", block_mesh_dict(level))
    write(os.path.join(case, "system", "controlDict"),
          "dictionary", "system", "controlDict", control_dict(level))
    write(os.path.join(case, "system", "fvSchemes"),
          "dictionary", "system", "fvSchemes", FV_SCHEMES)
    write(os.path.join(case, "system", "fvSolution"),
          "dictionary", "system", "fvSolution", FV_SOLUTION)
    for name, (cls, body) in constant_files().items():
        write(os.path.join(case, "constant", name), cls, "constant", name, body)
    for name, (cls, body) in fields().items():
        write(os.path.join(case, "0.orig", name), cls, "0", name, body)

    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write(
            "# T8 MTT pure plume -- registered case constants (read by analyse_t8.py)\n"
            "level %s\n"
            "D %.10g m\n"
            "b0 %.10g m\n"
            "R_domain %.10g m\n"
            "H_domain %.10g m\n"
            "wedge_half_angle_deg %.10g deg\n"
            "w0 %.10g m/s\n"
            "gprime0 %.10g m/s2\n"
            "dT0 %.10g K\n"
            "T_source %.10g K\n"
            "F0 %.10g m4/s3\n"
            "TRef %.10g K\n"
            "beta %.12g 1/K\n"
            "g %.10g m/s2\n"
            "nu %.10g m2/s\n"
            "Pr %.10g -\n"
            "Prt %.10g -\n"
            "k0 %.10g m2/s2\n"
            "epsilon0 %.10g m2/s3\n"
            "alpha_nominal %.10g -\n"
            "nr_blocks %s -\n"
            "nz %d -\n"
            "n_cells_expected %d -\n"
            "endTime %d -\n"
            "nProcs 1 -\n"
            % (level, D_SOURCE, B0, R_DOMAIN, H_DOMAIN, WEDGE_HALF_ANGLE_DEG,
               W0, GPRIME0, DT0, T_SOURCE, F0, TREF, BETA, G_ACCEL, NU, PR, PRT,
               K0, EPS0, ALPHA_NOMINAL,
               "/".join(str(x) for x in LEVELS[level]["nr"]),
               LEVELS[level]["nz"], EXPECT_CELLS[level], LEVELS[level]["endTime"]))
    print("built %s  (expect %d cells)" % (case, EXPECT_CELLS[level]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--levels", nargs="*", default=["c", "m", "f"])
    a = ap.parse_args()
    rc = 0
    for lv in a.levels:
        rc = max(rc, build(os.path.abspath(a.root), lv))
    return rc


if __name__ == "__main__":
    sys.exit(main())
