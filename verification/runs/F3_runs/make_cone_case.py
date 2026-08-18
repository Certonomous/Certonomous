#!/usr/bin/env python3
"""
Parametric generator for an axisymmetric supersonic-cone rhoCentralFoam case
(Taylor-Maccoll gate). Same nondimensional gas as the wedge case: gamma=1.4,
mu=0 (inviscid), a=1 at T=1, so U magnitude IS the Mach number directly.

Axisymmetric flow is represented as a thin (2*ALPHA_DEG total) wedge revolved
about the x-axis, using OpenFOAM's standard "wedge" boundary-condition
convention: front/back planes at z = +/- y*tan(ALPHA_DEG), sharing the same
y ("radial") coordinate, merged along the true axis (y=0) into a single edge
of type empty. This is the same convention used in OpenFOAM's own tutorials
(e.g. compressible/rhoCentralFoam/movingCone system/blockMeshDict).
"""
import sys, os, math

ALPHA_DEG = 2.5  # axisymmetric wedge half-angle (standard small-angle convention)

RES = {
    "coarse": (30, 20, 60, 20),
    "medium": (60, 40, 120, 40),
    "fine":   (120, 80, 240, 80),
}


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def foam_header(cls, obj):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    object      {obj};
}}
"""


def make_case(case_dir, M, theta_c_deg, res_level, beta_exact_deg, endtime_flowthroughs=6.0):
    theta_c = math.radians(theta_c_deg)
    alpha = math.radians(ALPHA_DEG)
    tanA = math.tan(alpha)

    x_min = -0.3
    x_max = 1.0
    Ltot = x_max - x_min
    cone_r_max = x_max * math.tan(theta_c)
    beta_ex = math.radians(beta_exact_deg)
    R = max(1.6 * x_max * math.tan(beta_ex), cone_r_max * 1.8, 0.6)

    nx1, nr, nx2, nr2 = RES[res_level]
    assert nr == nr2

    def fv(x, r):
        return (x, r, r * tanA)   # front (wedge +alpha) vertex
    def bv(x, r):
        return (x, r, -r * tanA)  # back (wedge -alpha) vertex

    # Block A (upstream, axis to farfield, x in [x_min, 0]):
    # v0 = axis @ x_min (shared front/back, r=0)
    # v1 = axis @ 0      (shared)
    # v2 = front outer @ 0, v3 = front outer @ x_min
    # v2b = back outer @ 0, v3b = back outer @ x_min
    v0 = (x_min, 0, 0)
    v1 = (0, 0, 0)
    v2 = fv(0, R); v3 = fv(x_min, R)
    v2b = bv(0, R); v3b = bv(x_min, R)

    # Block B (cone region, x in [0, x_max]):
    # v1 = apex (shared with block A, r=0)
    # v4 = cone surface @ x_max (front), v4b = back
    # v2 = outer @ 0 (shared with block A), v2b = back
    # v5 = outer @ x_max (front), v5b = back
    v4 = fv(x_max, cone_r_max); v4b = bv(x_max, cone_r_max)
    v5 = fv(x_max, R); v5b = bv(x_max, R)

    # Vertex list with explicit indices (mergeType points handles axis coincidence
    # automatically since axis vertices are literally the same coordinates and we
    # reuse the same index for front/back copies at r=0)
    verts = [v0, v1, v2, v3, v2b, v3b, v4, v4b, v5, v5b]
    # indices:  0   1   2   3   4    5    6   7    8   9
    vtxt = "\n".join(f"    ({v[0]:.12f} {v[1]:.12f} {v[2]:.12f})" for v in verts)

    # Block A hex: (v0 v1 v2 v3) front-ish loop / (v0 v1 v2b v3b) back loop
    # ordering: (bottom-back0 bottom-back1 top-back1 top-back0  bottom-front0 ... )
    # Using OpenFOAM convention: base face then top face, both CCW.
    # base (axis) face: v0 v1 v1 v0 (degenerate line) -> use pattern from movingCone:
    # hex (0 1 <frontOuter1> <frontOuter0>  0 1 <backOuter1> <backOuter0>)
    blockA = "hex (0 1 4 5 0 1 2 3) (%d %d 1) simpleGrading (1 1 1)" % (nx1, nr)
    blockB = "hex (1 7 9 4 1 6 8 2) (%d %d 1) simpleGrading (1 1 1)" % (nx2, nr)

    blockMeshDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "blockMeshDict")}
mergeType points;

scale 1;

vertices
(
{vtxt}
);

blocks
(
    {blockA}
    {blockB}
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces ((0 3 5 0));
    }}
    outlet
    {{
        type patch;
        faces ((6 8 9 7));
    }}
    axis
    {{
        type empty;
        faces ((0 1 1 0));
    }}
    cone
    {{
        type wall;
        faces ((1 6 7 1));
    }}
    farfield
    {{
        type patch;
        faces ((3 2 4 5)(2 8 9 4));
    }}
    frontWedge
    {{
        type wedge;
        faces ((0 1 2 3)(1 6 8 2));
    }}
    backWedge
    {{
        type wedge;
        faces ((0 5 4 1)(1 4 9 7));
    }}
);

mergePatchPairs
(
);
"""
    write(f"{case_dir}/system/blockMeshDict", blockMeshDict)

    def bcfile(cls, obj, dim, internal, inlet_val, cone_type):
        return f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header(cls, obj)}
dimensions      {dim};

internalField   uniform {internal};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {inlet_val};
    }}
    outlet
    {{
        type            zeroGradient;
    }}
    axis
    {{
        type            empty;
    }}
    farfield
    {{
        type            zeroGradient;
    }}
    cone
    {{
        type            {cone_type};
    }}
    frontWedge
    {{
        type            wedge;
    }}
    backWedge
    {{
        type            wedge;
    }}
}}
"""

    write(f"{case_dir}/0/U", bcfile("volVectorField", "U", "[0 1 -1 0 0 0 0]",
                                     f"({M} 0 0)", f"({M} 0 0)", "slip"))
    write(f"{case_dir}/0/p", bcfile("volScalarField", "p", "[1 -1 -2 0 0 0 0]",
                                     "1", "1", "zeroGradient"))
    write(f"{case_dir}/0/T", bcfile("volScalarField", "T", "[0 0 0 1 0 0 0]",
                                     "1", "1", "zeroGradient"))

    endTime = endtime_flowthroughs * Ltot / M

    controlDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "controlDict")}
application     rhoCentralFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {endTime:.6f};
deltaT          1e-5;
writeControl    runTime;
writeInterval   {endTime/3:.6f};
purgeWrite      2;
writeFormat     ascii;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           0.4;
maxDeltaT       1e-3;
"""
    write(f"{case_dir}/system/controlDict", controlDict)

    fvSchemes = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "fvSchemes")}
fluxScheme          Kurganov;
ddtSchemes {{ default Euler; }}
gradSchemes {{ default Gauss linear; }}
divSchemes {{ default none; div(tauMC) Gauss linear; }}
laplacianSchemes {{ default Gauss linear corrected; }}
interpolationSchemes
{{
    default         linear;
    reconstruct(rho) vanLeer;
    reconstruct(U)  vanLeerV;
    reconstruct(T)  vanLeer;
}}
snGradSchemes {{ default corrected; }}
"""
    write(f"{case_dir}/system/fvSchemes", fvSchemes)

    fvSolution = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "fvSolution")}
solvers
{{
    "(rho|rhoU|rhoE)" {{ solver diagonal; }}
    U
    {{
        solver smoothSolver; smoother GaussSeidel; nSweeps 2;
        tolerance 1e-09; relTol 0.01;
    }}
    h {{ $U; tolerance 1e-10; relTol 0; }}
}}
"""
    write(f"{case_dir}/system/fvSolution", fvSolution)

    thermo = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "thermophysicalProperties")}
thermoType
{{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}}
mixture
{{
    specie {{ molWeight 11640.3; }}
    thermodynamics {{ Cp 2.5; Hf 0; }}
    transport {{ mu 0; Pr 1; }}
}}
"""
    write(f"{case_dir}/constant/thermophysicalProperties", thermo)

    write(f"{case_dir}/constant/turbulenceProperties", f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "turbulenceProperties")}
simulationType laminar;
""")

    meta = dict(case_dir=case_dir, M=M, theta_c_deg=theta_c_deg, res_level=res_level,
                x_min=x_min, x_max=x_max, R=R, cone_r_max=cone_r_max, endTime=endTime,
                nx1=nx1, nr=nr, nx2=nx2, alpha_deg=ALPHA_DEG)
    return meta


if __name__ == "__main__":
    case_dir, M, theta_c_deg, res_level, beta_exact_deg = sys.argv[1], float(sys.argv[2]), \
        float(sys.argv[3]), sys.argv[4], float(sys.argv[5])
    meta = make_case(case_dir, M, theta_c_deg, res_level, beta_exact_deg)
    print(meta)
