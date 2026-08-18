#!/usr/bin/env python3
"""
Parametric generator for a 2D supersonic-wedge rhoCentralFoam case, based on
the OpenFOAM v2606 tutorial compressible/rhoCentralFoam/wedge15Ma5 (same
non-dimensional gas: gamma=1.4, mu=0 (inviscid), a=1 at T=1, so U magnitude
IS the Mach number directly).

Usage: make_wedge_case.py <case_dir> <Mach> <half_angle_deg> <res_level>
  res_level in {coarse, medium, fine}
"""
import sys, os, math

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


def make_case(case_dir, M, theta_deg, res_level, beta_exact_deg, endtime_flowthroughs=6.0):
    theta = math.radians(theta_deg)
    Lin = 0.3
    Lramp = 1.0
    Ltot = Lin + Lramp
    ramp_h = Lramp * math.tan(theta)
    beta_ex = math.radians(beta_exact_deg)
    H = max(1.6 * Lramp * math.tan(beta_ex), ramp_h * 1.8, 0.6)

    nx1, ny, nx2, ny2 = RES[res_level]
    assert ny == ny2

    x0, x1, x2 = -Lin, 0.0, Lramp
    z = 0.005

    verts = [
        (x0, 0, -z), (x1, 0, -z), (x2, ramp_h, -z),
        (x0, H, -z), (x1, H, -z), (x2, H, -z),
        (x0, 0, z), (x1, 0, z), (x2, ramp_h, z),
        (x0, H, z), (x1, H, z), (x2, H, z),
    ]
    vtxt = "\n".join(f"    ({v[0]:.6f} {v[1]:.6f} {v[2]:.6f})" for v in verts)

    blockMeshDict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
\\*---------------------------------------------------------------------------*/
{foam_header("dictionary", "blockMeshDict")}
scale 1;

vertices
(
{vtxt}
);

blocks
(
    hex (0 1 4 3 6 7 10 9) ({nx1} {ny} 1) simpleGrading (1 1 1)
    hex (1 2 5 4 7 8 11 10) ({nx2} {ny} 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces ((0 6 9 3));
    }}
    outlet
    {{
        type patch;
        faces ((2 5 11 8));
    }}
    bottom
    {{
        type symmetryPlane;
        faces ((0 1 7 6));
    }}
    top
    {{
        type patch;
        faces ((3 9 10 4)(4 10 11 5));
    }}
    obstacle
    {{
        type wall;
        faces ((1 2 8 7));
    }}
    defaultFaces
    {{
        type empty;
        faces ();
    }}
);

mergePatchPairs
(
);
"""
    write(f"{case_dir}/system/blockMeshDict", blockMeshDict)

    def bcfile(cls, obj, dim, internal, inlet_val, obstacle_type, obstacle_extra=""):
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
    bottom
    {{
        type            symmetryPlane;
    }}
    top
    {{
        type            zeroGradient;
    }}
    obstacle
    {{
        type            {obstacle_type};
        {obstacle_extra}
    }}
    defaultFaces
    {{
        type            empty;
    }}
}}
"""

    write(f"{case_dir}/0/U", bcfile("volVectorField", "U", "[0 1 -1 0 0 0 0]",
                                     f"({M} 0 0)", f"({M} 0 0)", "slip", ""))
    write(f"{case_dir}/0/p", bcfile("volScalarField", "p", "[1 -1 -2 0 0 0 0]",
                                     "1", "1", "zeroGradient", ""))
    write(f"{case_dir}/0/T", bcfile("volScalarField", "T", "[0 0 0 1 0 0 0]",
                                     "1", "1", "zeroGradient", ""))

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

    meta = dict(case_dir=case_dir, M=M, theta_deg=theta_deg, res_level=res_level,
                Lin=Lin, Lramp=Lramp, H=H, ramp_h=ramp_h, endTime=endTime,
                nx1=nx1, ny=ny, nx2=nx2)
    return meta


if __name__ == "__main__":
    case_dir, M, theta_deg, res_level, beta_exact_deg = sys.argv[1], float(sys.argv[2]), \
        float(sys.argv[3]), sys.argv[4], float(sys.argv[5])
    meta = make_case(case_dir, M, theta_deg, res_level, beta_exact_deg)
    print(meta)
