#!/usr/bin/env python3
"""
Assemble a full OpenFOAM simpleFoam case for the DPW-8 V2 Joukowski airfoil
verification case (M=0.15, Re_c=6e6, alpha=0, T_static=520 R), reusing the
already-validated flow setup from this lab's own TMR NACA0012 alpha=0 case
(~/certonomous-runs/tmr-naca-a0-coarse, same Re_c=6e6 via U=1, nu=1/6e6,
kOmegaSST) -- including the specific div-scheme combination
(bounded Gauss linearUpwind grad(U) for momentum, bounded Gauss upwind for
k/omega) that this repo's own C4 TMR closure note found necessary to kill a
persistent leading-edge bounding oscillation on a symmetric zero-lift case at
this same Reynolds number. Documented deviations from the literal DPW-8 spec
(incompressible vs compressible, kOmegaSST vs SA-neg-QCR2000-R, our own
freestream turbulence state vs the spec's SA-specific nu_t/nu=3) are recorded
in DPW8_V2_joukowski.md Sec. 6, not hidden here.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))
from build_mesh import build_grid_points, write_openfoam_mesh, GRID_LEVELS

NU = 1.0 / 6.0e6          # m^2/s, chosen so Re = U*c/nu = 1*1/nu = 6e6 exactly (c=1, U=1)
U_INF = 1.0
K_FS = 4e-7
OMEGA_FS = 266.66667
NUT_FS = 1.5e-9


def foam_header(cls, obj, extra_dims=None):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    object      {obj};
}}

"""


def write_case(case_dir, level, eps=0.10, y1_target_physical=3.0e-6, r_outer_chords=120.0):
    _, Ni, Nj = [g for g in GRID_LEVELS if g[0] == level][0]
    X, Y, chord_raw, ratios, y1_raw, af = build_grid_points(
        eps, Ni, Nj, y1_target_physical=y1_target_physical, r_outer_chords=r_outer_chords)
    mesh_info = write_openfoam_mesh(case_dir, X, Y, depth=0.02)

    os.makedirs(f"{case_dir}/system", exist_ok=True)
    os.makedirs(f"{case_dir}/constant", exist_ok=True)
    os.makedirs(f"{case_dir}/0", exist_ok=True)

    with open(f"{case_dir}/constant/transportProperties", "w") as f:
        f.write(foam_header("dictionary", "transportProperties"))
        f.write(f"transportModel  Newtonian;\nnu              {NU!r};\n")

    with open(f"{case_dir}/constant/turbulenceProperties", "w") as f:
        f.write(foam_header("dictionary", "turbulenceProperties"))
        f.write("simulationType  RAS;\nRAS\n{\n    RASModel        kOmegaSST;\n"
                "    turbulence      on;\n    printCoeffs     on;\n}\n")

    with open(f"{case_dir}/system/controlDict", "w") as f:
        f.write(foam_header("dictionary", "controlDict"))
        f.write(f"""application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {{END_TIME}};
deltaT          1;
writeControl    timeStep;
writeInterval   {{END_TIME}};
purgeWrite      2;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   6;

functions
{{
    forceCoeffs1
    {{
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         (airfoil);
        rho             rhoInf;
        rhoInf          1.0;
        magUInf         1.0;
        lRef            1.0;
        Aref            1.0;
        CofR            (0 0 0);
        dragDir         (1 0 0);
        liftDir         (0 1 0);
        pitchAxis       (0 0 1);
    }}
    yPlus1
    {{
        type            yPlus;
        libs            (fieldFunctionObjects);
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    wallShearStress1
    {{
        type            wallShearStress;
        libs            (fieldFunctionObjects);
        patches         (airfoil);
        executeControl  onEnd;
        writeControl    onEnd;
    }}
}}
""")

    with open(f"{case_dir}/system/fvSchemes", "w") as f:
        f.write(foam_header("dictionary", "fvSchemes"))
        f.write("""ddtSchemes      { default steadyState; }
gradSchemes     { default cellLimited Gauss linear 1; }
laplacianSchemes { default Gauss linear limited corrected 0.5; }
snGradSchemes   { default limited corrected 0.5; }

divSchemes
{
    default                         none;
    div(phi,U)                      bounded Gauss linearUpwind grad(U);
    div(phi,k)                      bounded Gauss upwind;
    div(phi,omega)                  bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U)))))   Gauss linear;
}
interpolationSchemes { default linear; }
wallDist        { method meshWave; }
""")

    with open(f"{case_dir}/system/fvSolution", "w") as f:
        f.write(foam_header("dictionary", "fvSolution"))
        f.write("""solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-09;
        relTol          0.01;
    }
    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-10;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 1;
    consistent      no;
    residualControl
    {
        p               1e-06;
        U               1e-08;
        "(k|omega)"     1e-08;
    }
}

relaxationFactors
{
    fields    { p 0.25; }
    equations { U 0.6; k 0.6; omega 0.6; }
}
""")

    with open(f"{case_dir}/0/U", "w") as f:
        f.write(foam_header("volVectorField", "U"))
        f.write(f"""dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({U_INF} 0 0);
boundaryField
{{
    airfoil  {{ type noSlip; }}
    farfield {{ type inletOutlet; inletValue uniform ({U_INF} 0 0); value uniform ({U_INF} 0 0); }}
    front    {{ type empty; }}
    back     {{ type empty; }}
}}
""")

    with open(f"{case_dir}/0/p", "w") as f:
        f.write(foam_header("volScalarField", "p"))
        f.write("""dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    airfoil  { type zeroGradient; }
    farfield { type freestreamPressure; freestreamValue uniform 0; }
    front    { type empty; }
    back     { type empty; }
}
""")

    with open(f"{case_dir}/0/k", "w") as f:
        f.write(foam_header("volScalarField", "k"))
        f.write(f"""dimensions      [0 2 -2 0 0 0 0];
internalField   uniform {K_FS};
boundaryField
{{
    airfoil  {{ type kLowReWallFunction; value uniform 1e-12; }}
    farfield {{ type inletOutlet; inletValue uniform {K_FS}; value uniform {K_FS}; }}
    front    {{ type empty; }}
    back     {{ type empty; }}
}}
""")

    with open(f"{case_dir}/0/omega", "w") as f:
        f.write(foam_header("volScalarField", "omega"))
        f.write(f"""dimensions      [0 0 -1 0 0 0 0];
internalField   uniform {OMEGA_FS};
boundaryField
{{
    airfoil  {{ type omegaWallFunction; blended true; value uniform {OMEGA_FS}; }}
    farfield {{ type inletOutlet; inletValue uniform {OMEGA_FS}; value uniform {OMEGA_FS}; }}
    front    {{ type empty; }}
    back     {{ type empty; }}
}}
""")

    with open(f"{case_dir}/0/nut", "w") as f:
        f.write(foam_header("volScalarField", "nut"))
        f.write(f"""dimensions      [0 2 -1 0 0 0 0];
internalField   uniform {NUT_FS};
boundaryField
{{
    airfoil  {{ type nutLowReWallFunction; value uniform 0; }}
    farfield {{ type calculated; value uniform {NUT_FS}; }}
    front    {{ type empty; }}
    back     {{ type empty; }}
}}
""")

    meta = dict(level=level, Ni=Ni, Nj=Nj, eps=eps, chord_raw=chord_raw,
                y1_target_physical=y1_target_physical, y1_target_raw=y1_raw,
                ratio_min=float(ratios.min()), ratio_max=float(ratios.max()),
                r_outer_chords=r_outer_chords, nu=NU, U_inf=U_INF, Re=U_INF * 1.0 / NU,
                **mesh_info)
    with open(f"{case_dir}/case_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    return meta


if __name__ == "__main__":
    level = int(sys.argv[1])
    case_dir = sys.argv[2]
    end_time = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    meta = write_case(case_dir, level)
    # substitute end time placeholder
    cd_path = f"{case_dir}/system/controlDict"
    s = open(cd_path).read().replace("{END_TIME}", str(end_time))
    open(cd_path, "w").write(s)
    print(json.dumps(meta, indent=2))
