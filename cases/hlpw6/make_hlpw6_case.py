#!/usr/bin/env python3
"""Write the OpenFOAM case dictionaries around an imported HLPW6 TC1 polyMesh.

Conditions from the HLPW6 Test Case 1 specification v1.0: M = 0.20,
chord Re = 3.55e6, free air. Reference static temperature 518.67 R = 288.15 K,
static pressure 14.696 psi = 101325 Pa, MAC 30 in = 0.762 m. Those three
together give rho = 1.225 kg/m3, a = 340.3 m/s, U = 68.06 m/s and
nu = 1.46e-5 m2/s -- i.e. standard sea-level air, and U*MAC/nu = 3.55e6, which
is the specified Reynolds number. That consistency is the check that the case
has been set up at the published condition rather than at a guess.

Usage: make_hlpw6_case.py <caseDir> <incompressible|compressible> <alphaDeg> [iters] [nranks]
"""
import math
import os
import re
import sys

CASE, MODE, ALPHA = sys.argv[1], sys.argv[2], float(sys.argv[3])
ITERS = int(sys.argv[4]) if len(sys.argv) > 4 else 20
NRANKS = int(sys.argv[5]) if len(sys.argv) > 5 else 14
COMP = MODE == "compressible"

U_INF = 68.06
NU = 1.46e-5
MAC = 0.762
TURB_I = 0.001              # 0.1 % freestream turbulence
NUT_RATIO = 0.009           # SST freestream defaults (nut/nu ~ 1e-2)
k_inf = 1.5 * (TURB_I * U_INF) ** 2
omega_inf = k_inf / (NUT_RATIO * NU)

# angle of attack applied in the x-z plane; z is the vertical axis of the
# imported mesh (checked against the polyMesh bounding box, see BOUNDS note)
a = math.radians(ALPHA)
UX, UY, UZ = U_INF * math.cos(a), 0.0, U_INF * math.sin(a)

bfile = os.path.join(CASE, "constant", "polyMesh", "boundary")
txt = open(bfile).read()
patches = re.findall(r"^\s{4}(\w+)\n\s{4}\{\n\s+type\s+(\w+);", txt, re.M)
walls = [n for n, t in patches if t == "wall"]
syms = [n for n, t in patches if t == "symmetry"]
far = [n for n, t in patches if t == "patch"]
print(f"patches: {len(walls)} wall, {len(syms)} symmetry, {len(far)} farfield")

HDR = ('FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n'
       '    {loc}object {obj};\n}}\n')


def w(rel, cls, obj, body, loc=""):
    p = os.path.join(CASE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    locs = f'location "{loc}";\n    ' if loc else ""
    open(p, "w").write(HDR.format(cls=cls, obj=obj, loc=locs) + body + "\n")


def bfield(wall_bc, sym_bc, far_bc):
    out = []
    for n in walls:
        out.append(f"    {n} {{ {wall_bc} }}")
    for n in syms:
        out.append(f"    {n} {{ {sym_bc} }}")
    for n in far:
        out.append(f"    {n} {{ {far_bc} }}")
    return "\n".join(out)


def field(name, cls, dim, internal, wall_bc, sym_bc, far_bc):
    w(f"0/{name}", cls, name,
      f"dimensions      {dim};\ninternalField   uniform {internal};\n\n"
      f"boundaryField\n{{\n{bfield(wall_bc, sym_bc, far_bc)}\n}}\n", loc="0")


SYM = "type symmetry;"
Uv = f"({UX:.6f} {UY:.6f} {UZ:.6f})"

field("U", "volVectorField", "[0 1 -1 0 0 0 0]", Uv,
      "type noSlip;", SYM,
      f"type freestreamVelocity; freestreamValue uniform {Uv}; value uniform {Uv};")

if COMP:
    field("p", "volScalarField", "[1 -1 -2 0 0 0 0]", "101325",
          "type zeroGradient;", SYM,
          "type freestreamPressure; freestreamValue uniform 101325; value uniform 101325;")
    field("T", "volScalarField", "[0 0 0 1 0 0 0]", "288.15",
          "type zeroGradient;", SYM,
          "type freestream; freestreamValue uniform 288.15; value uniform 288.15;")
    field("alphat", "volScalarField", "[1 -1 -1 0 0 0 0]", "0",
          "type compressible::alphatWallFunction; value uniform 0;", SYM,
          "type calculated; value uniform 0;")
    nutdim = "[0 2 -1 0 0 0 0]"
else:
    field("p", "volScalarField", "[0 2 -2 0 0 0 0]", "0",
          "type zeroGradient;", SYM,
          "type freestreamPressure; freestreamValue uniform 0; value uniform 0;")
    nutdim = "[0 2 -1 0 0 0 0]"

field("nut", "volScalarField", nutdim, "0",
      "type nutUSpaldingWallFunction; value uniform 0;", SYM,
      "type calculated; value uniform 0;")
field("k", "volScalarField", "[0 2 -2 0 0 0 0]", f"{k_inf:.6g}",
      f"type kqRWallFunction; value uniform {k_inf:.6g};", SYM,
      f"type freestream; freestreamValue uniform {k_inf:.6g}; value uniform {k_inf:.6g};")
field("omega", "volScalarField", "[0 0 -1 0 0 0 0]", f"{omega_inf:.6g}",
      f"type omegaWallFunction; value uniform {omega_inf:.6g};", SYM,
      f"type freestream; freestreamValue uniform {omega_inf:.6g}; "
      f"value uniform {omega_inf:.6g};")

if COMP:
    w("constant/thermophysicalProperties", "dictionary", "thermophysicalProperties", """
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
    specie          { molWeight 28.96; }
    thermodynamics  { Cp 1004.5; Hf 0; }
    transport       { As 1.4580e-06; Ts 110.4; }
}
""")
else:
    w("constant/transportProperties", "dictionary", "transportProperties",
      f"transportModel  Newtonian;\nnu              {NU};\n")

w("constant/turbulenceProperties", "dictionary", "turbulenceProperties", """
simulationType  RAS;
RAS { model kOmegaSST; turbulence on; printCoeffs on; }
""")

app = "rhoSimpleFoam" if COMP else "simpleFoam"
rhoinf = ("        rho         rho;\n        rhoInf      1.225;\n" if COMP else
          "        rho         rhoInf;\n        rhoInf      1.225;\n")
w("system/controlDict", "dictionary", "controlDict", f"""
application     {app};
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {ITERS};
deltaT          1;
writeControl    timeStep;
writeInterval   {ITERS};
purgeWrite      1;
writeFormat     binary;
writePrecision  8;
writeCompression off;
runTimeModifiable false;

functions
{{
    forceCoeffs
    {{
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         ({' '.join(walls)});
{rhoinf}        liftDir         ({-math.sin(a):.6f} 0 {math.cos(a):.6f});
        dragDir         ({math.cos(a):.6f} 0 {math.sin(a):.6f});
        CofR            (0 0 0);
        pitchAxis       (0 1 0);
        magUInf         {U_INF};
        lRef            {MAC};
        Aref            1.0;
    }}
}}
""")

w("system/fvSchemes", "dictionary", "fvSchemes", """
ddtSchemes      { default steadyState; }
gradSchemes     { default cellLimited Gauss linear 1; }
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
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
    div((nuEff*dev2(T(grad(U)))))       Gauss linear;
}
laplacianSchemes { default Gauss linear limited corrected 0.33; }
interpolationSchemes { default linear; }
snGradSchemes   { default limited corrected 0.33; }
wallDist        { method meshWave; }
""")

extra = '    "(e|h)" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; relTol 0.01; }\n' if COMP else ""
simple_extra = "    rhoMin 0.1; rhoMax 10.0; transonic no;\n" if COMP else ""
relax = ("    fields { p 0.3; rho 1.0; }\n    equations { U 0.5; \"(k|omega|e|h)\" 0.5; }\n"
         if COMP else
         "    fields { p 0.3; }\n    equations { U 0.5; \"(k|omega)\" 0.5; }\n")
w("system/fvSolution", "dictionary", "fvSolution", f"""
solvers
{{
    p
    {{
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-7;
        relTol          0.01;
    }}
{extra}    "(U|k|omega)"
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
    consistent      yes;
{simple_extra}    residualControl {{ p 1e-9; U 1e-9; "(k|omega)" 1e-9; }}
}}

relaxationFactors
{{
{relax}}}
""")

w("system/decomposeParDict", "dictionary", "decomposeParDict",
  f"numberOfSubdomains {NRANKS};\nmethod          scotch;\n")

print(f"case written: {CASE}  {MODE}  alpha={ALPHA} deg  U={Uv}  "
      f"k={k_inf:.4g} omega={omega_inf:.4g}  iters={ITERS} ranks={NRANKS}")
