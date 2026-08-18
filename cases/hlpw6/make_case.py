#!/usr/bin/env python3
"""Generate a parametric OpenFOAM RANS box case at a chosen cell count.

Purpose: measure the memory footprint of the OpenFOAM v2606 RANS solver stack
as a function of cell count, so a 2.66M-cell HLPW6 grid can be priced from a
measured slope instead of a single-point linear extrapolation.

Geometry is a graded box with a no-slip floor -- deliberately trivial, because
mesh *topology* (cells, faces) is what sets memory, not shape. A structured hex
mesh has 3.0 internal faces/cell, the highest of any element type (tet 2.0,
prism ~2.5), so at equal cell count a hex probe is a conservative upper bound
on the matrix storage of a mixed prism/tet workshop grid.

Usage: make_case.py <casedir> <nx> <ny> <nz> <incompressible|compressible>
"""
import os
import sys

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    {extra}object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""


def w(path, cls, obj, body, extra=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(HDR.format(cls=cls, obj=obj, extra=extra))
        f.write(body)
        f.write("\n// ************************************************************************* //\n")


def main():
    case, nx, ny, nz, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    comp = mode == "compressible"
    loc = 'location    "{}";\n    '

    # ---------------- blockMesh ----------------
    # 20 x 4 x 10 m box; floor is a wall, graded to give a near-wall layer.
    w(f"{case}/system/blockMeshDict", "dictionary", "blockMeshDict", f"""
scale   1;

vertices
(
    (0  0 0) (20 0 0) (20 4 0) (0 4 0)
    (0  0 10) (20 0 10) (20 4 10) (0 4 10)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 200 1)
);

boundary
(
    inlet   {{ type patch;  faces ((0 4 7 3)); }}
    outlet  {{ type patch;  faces ((1 2 6 5)); }}
    floor   {{ type wall;   faces ((0 1 5 4)); }}
    top     {{ type patch;  faces ((3 7 6 2)); }}
    sides   {{ type symmetry; faces ((0 3 2 1) (4 5 6 7)); }}
);
""")

    # ---------------- controlDict ----------------
    app = "rhoSimpleFoam" if comp else "simpleFoam"
    w(f"{case}/system/controlDict", "dictionary", "controlDict", f"""
application     {app};
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         20;
deltaT          1;
writeControl    timeStep;
writeInterval   100000;
purgeWrite      1;
writeFormat     binary;
writePrecision  8;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
""")

    # ---------------- fvSchemes / fvSolution ----------------
    w(f"{case}/system/fvSchemes", "dictionary", "fvSchemes", """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default             none;
    div(phi,U)          bounded Gauss linearUpwind grad(U);
    div(phi,k)          bounded Gauss upwind;
    div(phi,omega)      bounded Gauss upwind;
    div(phi,e)          bounded Gauss upwind;
    div(phi,h)          bounded Gauss upwind;
    div(phi,K)          bounded Gauss upwind;
    div(phi,Ekp)        bounded Gauss upwind;
    div(phid,p)         bounded Gauss upwind;
    div(phi,epsilon)    bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
    div((nuEff*dev2(T(grad(U)))))       Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
""")

    presolver = """
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-7;
        relTol          0.01;
    }
"""
    if comp:
        presolver = """
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-7;
        relTol          0.01;
    }
    "(e|h)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-8;
        relTol          0.01;
    }
"""
    relax = """
    fields  { p 0.3; rho 1.0; }
    equations { U 0.7; "(k|omega|e|h)" 0.7; }
""" if comp else """
    fields  { p 0.3; }
    equations { U 0.7; "(k|omega)" 0.7; }
"""
    w(f"{case}/system/fvSolution", "dictionary", "fvSolution", f"""
solvers
{{
{presolver}
    "(U|k|omega)"
    {{
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-8;
        relTol          0.01;
    }}
}}

SIMPLE
{{
    nNonOrthogonalCorrectors 0;
    consistent          yes;
    {'rhoMin 0.1; rhoMax 10.0; transonic no;' if comp else ''}
    residualControl {{ p 1e-9; U 1e-9; "(k|omega)" 1e-9; }}
}}

relaxationFactors
{{
{relax}
}}
""")

    w(f"{case}/system/decomposeParDict", "dictionary", "decomposeParDict", """
numberOfSubdomains 14;
method          scotch;
""")

    # ---------------- constant ----------------
    w(f"{case}/constant/turbulenceProperties", "dictionary", "turbulenceProperties", """
simulationType  RAS;
RAS
{
    model           kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
""")

    if comp:
        w(f"{case}/constant/thermophysicalProperties", "dictionary", "thermophysicalProperties", """
thermoType
{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       sutherland;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}
mixture
{
    specie      { molWeight 28.9; }
    thermodynamics { Cp 1005; Hf 0; }
    transport   { As 1.4792e-06; Ts 116; }
}
""")
    else:
        w(f"{case}/constant/transportProperties", "dictionary", "transportProperties", """
transportModel  Newtonian;
nu              1.5e-05;
""")

    # ---------------- 0/ fields ----------------
    U = 68.0  # m/s, ~M0.2
    k = 0.24
    om = 40.0

    def field(name, cls, dim, internal, bcs):
        w(f"{case}/0/{name}", cls, name, f"""
dimensions      {dim};
internalField   uniform {internal};

boundaryField
{{
{bcs}
}}
""", extra=loc.format('"0"'))

    field("U", "volVectorField", "[0 1 -1 0 0 0 0]", f"({U} 0 0)", f"""
    inlet   {{ type fixedValue; value uniform ({U} 0 0); }}
    outlet  {{ type zeroGradient; }}
    floor   {{ type noSlip; }}
    top     {{ type slip; }}
    sides   {{ type symmetry; }}
""")

    if comp:
        field("p", "volScalarField", "[1 -1 -2 0 0 0 0]", "101325", """
    inlet   { type zeroGradient; }
    outlet  { type fixedValue; value uniform 101325; }
    floor   { type zeroGradient; }
    top     { type slip; }
    sides   { type symmetry; }
""")
        field("T", "volScalarField", "[0 0 0 1 0 0 0]", "288.15", """
    inlet   { type fixedValue; value uniform 288.15; }
    outlet  { type zeroGradient; }
    floor   { type zeroGradient; }
    top     { type slip; }
    sides   { type symmetry; }
""")
        field("alphat", "volScalarField", "[1 -1 -1 0 0 0 0]", "0", """
    inlet   { type calculated; value uniform 0; }
    outlet  { type calculated; value uniform 0; }
    floor   { type compressible::alphatWallFunction; value uniform 0; }
    top     { type slip; }
    sides   { type symmetry; }
""")
        nutbc = """
    inlet   { type calculated; value uniform 0; }
    outlet  { type calculated; value uniform 0; }
    floor   { type nutkWallFunction; value uniform 0; }
    top     { type slip; }
    sides   { type symmetry; }
"""
        field("nut", "volScalarField", "[0 2 -1 0 0 0 0]", "0", nutbc)
    else:
        field("p", "volScalarField", "[0 2 -2 0 0 0 0]", "0", """
    inlet   { type zeroGradient; }
    outlet  { type fixedValue; value uniform 0; }
    floor   { type zeroGradient; }
    top     { type slip; }
    sides   { type symmetry; }
""")
        field("nut", "volScalarField", "[0 2 -1 0 0 0 0]", "0", """
    inlet   { type calculated; value uniform 0; }
    outlet  { type calculated; value uniform 0; }
    floor   { type nutkWallFunction; value uniform 0; }
    top     { type slip; }
    sides   { type symmetry; }
""")

    kdim = "[0 2 -2 0 0 0 0]"
    odim = "[0 0 -1 0 0 0 0]"
    field("k", "volScalarField", kdim, str(k), f"""
    inlet   {{ type fixedValue; value uniform {k}; }}
    outlet  {{ type zeroGradient; }}
    floor   {{ type kqRWallFunction; value uniform {k}; }}
    top     {{ type slip; }}
    sides   {{ type symmetry; }}
""")
    field("omega", "volScalarField", odim, str(om), f"""
    inlet   {{ type fixedValue; value uniform {om}; }}
    outlet  {{ type zeroGradient; }}
    floor   {{ type omegaWallFunction; value uniform {om}; }}
    top     {{ type slip; }}
    sides   {{ type symmetry; }}
""")
    print(f"{case}: {nx*ny*nz} cells, {mode}")


if __name__ == "__main__":
    main()
