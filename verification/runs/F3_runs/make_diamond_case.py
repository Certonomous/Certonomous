#!/usr/bin/env python3
"""
Parametric generator for a symmetric-diamond-airfoil rhoCentralFoam case
(shock-expansion-theory wave-drag gate), zero angle of attack.

Exploits top/bottom symmetry: only the UPPER half is meshed, with a
symmetryPlane along y=0 ahead of/behind the airfoil, and the airfoil's upper
surface (front compression panel + rear expansion panel) as a wall/slip
patch called "obstacle". Total 2D-section wave drag = 2 * (upper-surface
force), by symmetry.

Geometry breakpoints along the bottom (y=0 line / airfoil upper surface):
  (x0=-Lin, 0) -> (0, 0) -> (c/2, t/2) -> (c, 0) -> (x4=c+Lout, 0)
Four blocks, one per segment, each a simple hex with a linearly-varying
bottom edge (matching the single-ramp block used for the wedge case).

Same nondimensional gas as the wedge/cone cases: gamma=1.4, mu=0 (inviscid),
a=1 at T=1, so U magnitude IS the Mach number directly.
"""
import sys, os, math

RES = {
    "coarse": (20, 20, 30, 20, 30, 20, 20, 20),
    "medium": (40, 40, 60, 40, 60, 40, 40, 40),
    "fine":   (80, 80, 120, 80, 120, 80, 80, 80),
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


def make_case(case_dir, M, eps_deg, res_level, beta_exact_deg, c=1.0,
              endtime_flowthroughs=6.0):
    eps = math.radians(eps_deg)
    t2 = (c / 2) * math.tan(eps)  # half-thickness
    Lin, Lout = 0.4, 0.6
    x0, x1, x2, x3, x4 = -Lin, 0.0, c / 2, c, c + Lout
    beta_ex = math.radians(beta_exact_deg)
    H = max(1.6 * (c / 2) * math.tan(beta_ex), t2 * 2.0, 0.5)
    z = 0.005

    nxs = RES[res_level]
    n1, ny, n2, ny2, n3, ny3, n4, ny4 = nxs
    assert ny == ny2 == ny3 == ny4

    xs = [x0, x1, x2, x3, x4]
    ys = [0.0, 0.0, t2, 0.0, 0.0]
    ncells_x = [n1, n2, n3, n4]

    # vertices: for each of the 5 x-stations, a bottom (surface) and top point,
    # duplicated in z for the thin extruded (empty) direction.
    verts = []
    for xi, yi in zip(xs, ys):
        verts.append((xi, yi, -z))
    for xi in xs:
        verts.append((xi, H, -z))
    for xi, yi in zip(xs, ys):
        verts.append((xi, yi, z))
    for xi in xs:
        verts.append((xi, H, z))
    # index layout: bottom-back[0..4]=0..4, top-back[0..4]=5..9,
    #               bottom-front[0..4]=10..14, top-front[0..4]=15..19
    def bb(i): return i
    def tb(i): return 5 + i
    def bf(i): return 10 + i
    def tf(i): return 15 + i

    vtxt = "\n".join(f"    ({v[0]:.10f} {v[1]:.10f} {v[2]:.10f})" for v in verts)

    blocks = []
    for i in range(4):
        blocks.append(
            f"hex ({bb(i)} {bb(i+1)} {tb(i+1)} {tb(i)} {bf(i)} {bf(i+1)} {tf(i+1)} {tf(i)}) "
            f"({ncells_x[i]} {ny} 1) simpleGrading (1 1 1)"
        )

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
    {chr(10)+"    ".join(blocks)}
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces ((0 {bf(0)} {tf(0)} {tb(0)}));
    }}
    outlet
    {{
        type patch;
        faces (({bb(4)} {tb(4)} {tf(4)} {bf(4)}));
    }}
    bottom
    {{
        type symmetryPlane;
        faces ((0 1 {bf(1)} {bf(0)})({bb(3)} {bb(4)} {bf(4)} {bf(3)}));
    }}
    top
    {{
        type patch;
        faces (({tb(0)} {tf(0)} {tf(1)} {tb(1)})({tb(1)} {tf(1)} {tf(2)} {tb(2)})
               ({tb(2)} {tf(2)} {tf(3)} {tb(3)})({tb(3)} {tf(3)} {tf(4)} {tb(4)}));
    }}
    obstacle
    {{
        type wall;
        faces (({bb(1)} {bb(2)} {bf(2)} {bf(1)})({bb(2)} {bb(3)} {bf(3)} {bf(2)}));
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

    def bcfile(cls, obj, dim, internal, inlet_val, obstacle_type):
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
    }}
    defaultFaces
    {{
        type            empty;
    }}
}}
"""

    write(f"{case_dir}/0/U", bcfile("volVectorField", "U", "[0 1 -1 0 0 0 0]",
                                     f"({M} 0 0)", f"({M} 0 0)", "slip"))
    write(f"{case_dir}/0/p", bcfile("volScalarField", "p", "[1 -1 -2 0 0 0 0]",
                                     "1", "1", "zeroGradient"))
    write(f"{case_dir}/0/T", bcfile("volScalarField", "T", "[0 0 0 1 0 0 0]",
                                     "1", "1", "zeroGradient"))

    Ltot = x4 - x0
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

functions
{{
    forces1
    {{
        type            forces;
        libs            (forces);
        patches         (obstacle);
        rho             rhoInf;
        rhoInf          1;
        CofR            (0.5 0 0);
        writeControl    writeTime;
    }}
}}
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

    meta = dict(case_dir=case_dir, M=M, eps_deg=eps_deg, res_level=res_level, c=c,
                x0=x0, x4=x4, H=H, t2=t2, endTime=endTime, ncells=sum(
                    n * ny for n in ncells_x))
    return meta


if __name__ == "__main__":
    case_dir, M, eps_deg, res_level, beta_exact_deg = sys.argv[1], float(sys.argv[2]), \
        float(sys.argv[3]), sys.argv[4], float(sys.argv[5])
    meta = make_case(case_dir, M, eps_deg, res_level, beta_exact_deg)
    print(meta)
