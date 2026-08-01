#!/usr/bin/env python3
"""Write OpenFOAM case dictionaries around an imported DPW5 L1.T polyMesh.

The point of this script is that the `base` variant is a byte-for-byte
reproduction of the numerics that diverged on the HLPW6 committee grid
(`make_hlpw6_case.py`, 2026-08-01 04:46Z) -- same solver, same schemes, same
relaxation, same pressure solver. Only the grid changes. Every other variant is
one named, single-axis departure from that baseline, so a change in outcome is
attributable.

Usage: make_dpw5_case.py <caseDir> <incompressible|compressible> <alphaDeg>
                         <variant> [iters] [nranks]
"""
import math
import os
import re
import sys

CASE, MODE, ALPHA, VARIANT = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
ITERS = int(sys.argv[5]) if len(sys.argv) > 5 else 120
NRANKS = int(sys.argv[6]) if len(sys.argv) > 6 else 14
COMP = MODE == "compressible"

# --- freestream -----------------------------------------------------------
# Compressible runs are set at A6's own measured freestream so the result is
# gradeable against this lab's existing converged CRM reference
# (demo-output/website/dafoam/ladder-a/A6_crm_wingbody.md sec.2:
#  U0 = 295 m/s, T0 = 300 K, p0 = 101325 Pa, alpha 2.11031707 deg, M = 0.850).
# Incompressible runs use HLPW6's own fluid (nu = 1.46e-5, U = 68.06 m/s) so
# that the numerics comparison against the HLPW6 divergence is controlled: the
# solver, the schemes and the fluid are identical and only the grid differs.
if COMP:
    U_INF, T_INF, P_INF = 295.0, 300.0, 101325.0
else:
    U_INF = 68.06
NU = 1.46e-5
MAC = 275.8 * 0.0254        # DPW5/CRM mean aerodynamic chord 275.8 in -> m
TURB_I = 0.001
NUT_RATIO = 0.009
k_inf = 1.5 * (TURB_I * U_INF) ** 2
omega_inf = k_inf / (NUT_RATIO * NU)

a = math.radians(ALPHA)
UX, UY, UZ = U_INF * math.cos(a), 0.0, U_INF * math.sin(a)

bfile = os.path.join(CASE, "constant", "polyMesh", "boundary")
txt = open(bfile).read()
patches = re.findall(r"^\s{4}(\w+)\n\s{4}\{\n\s+type\s+(\w+);", txt, re.M)
walls = [n for n, t in patches if t == "wall"]
syms = [n for n, t in patches if t == "symmetry"]
far = [n for n, t in patches if t == "patch"]
assert walls and syms and far, f"patch classification failed: {patches}"
print(f"patches: {len(walls)} wall, {len(syms)} symmetry, {len(far)} farfield")

HDR = ('FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n'
       '    {loc}object {obj};\n}}\n')


def w(rel, cls, obj, body, loc=""):
    p = os.path.join(CASE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    locs = f'location "{loc}";\n    ' if loc else ""
    open(p, "w").write(HDR.format(cls=cls, obj=obj, loc=locs) + body + "\n")


def bfield(wall_bc, sym_bc, far_bc):
    out = [f"    {n} {{ {wall_bc} }}" for n in walls]
    out += [f"    {n} {{ {sym_bc} }}" for n in syms]
    out += [f"    {n} {{ {far_bc} }}" for n in far]
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
    field("p", "volScalarField", "[1 -1 -2 0 0 0 0]", f"{P_INF:g}",
          "type zeroGradient;", SYM,
          f"type freestreamPressure; freestreamValue uniform {P_INF:g}; "
          f"value uniform {P_INF:g};")
    field("T", "volScalarField", "[0 0 0 1 0 0 0]", f"{T_INF:g}",
          "type zeroGradient;", SYM,
          f"type freestream; freestreamValue uniform {T_INF:g}; value uniform {T_INF:g};")
    field("alphat", "volScalarField", "[1 -1 -1 0 0 0 0]", "0",
          "type compressible::alphatWallFunction; value uniform 0;", SYM,
          "type calculated; value uniform 0;")
else:
    field("p", "volScalarField", "[0 2 -2 0 0 0 0]", "0",
          "type zeroGradient;", SYM,
          "type freestreamPressure; freestreamValue uniform 0; value uniform 0;")

field("nut", "volScalarField", "[0 2 -1 0 0 0 0]", "0",
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

# Turbulence model. kOmegaSST is the HLPW6 baseline and therefore the default
# here, so the grid-vs-grid comparison stays controlled. SpalartAllmaras is
# offered as one of the diagnostic axes because it is the model DPW and HLPW
# publish their own baseline results with, and because it carries no omega
# equation and no omega wall function -- the two stiffest pieces of the k-omega
# stack on cells with aspect ratio in the thousands.
SA = VARIANT.endswith("_sa")
if SA:
    w("constant/turbulenceProperties", "dictionary", "turbulenceProperties", """
simulationType  RAS;
RAS { model SpalartAllmaras; turbulence on; printCoeffs on; }
""")
    nut_inf = 3.0 * NU          # standard SA freestream nuTilda/nu = 3
    field("nuTilda", "volScalarField", "[0 2 -1 0 0 0 0]", f"{nut_inf:.6g}",
          "type fixedValue; value uniform 0;", SYM,
          f"type freestream; freestreamValue uniform {nut_inf:.6g}; "
          f"value uniform {nut_inf:.6g};")
else:
    w("constant/turbulenceProperties", "dictionary", "turbulenceProperties", """
simulationType  RAS;
RAS { model kOmegaSST; turbulence on; printCoeffs on; }
""")

# ---------------------------------------------------------------- variants --
# Every entry is the HLPW6 baseline with ONE axis moved, except where stated.
V = {
    # exact HLPW6 configuration
    "base":      dict(),
    # 1. the pressure equation is never re-solved for the non-orthogonal part
    "nonorth2":  dict(nNonOrth=2),
    "nonorth6":  dict(nNonOrth=6),
    # 2. the Laplacian/surface-normal correction is limited but still active at
    #    90 deg; switch it off entirely (fully limited = orthogonal-only)
    "uncorr":    dict(snlim="uncorrected", laplim="uncorrected"),
    "lim0":      dict(snlim="limited corrected 0", laplim="limited corrected 0"),
    # 3. the convection reconstruction uses the cell gradient over a face-to-
    #    cell vector that is nearly tangential; swap for a face-value limiter
    #    that does not reconstruct
    "limlin":    dict(divU="bounded Gauss limitedLinear 1"),
    "linupV":    dict(divU="bounded Gauss linearUpwindV grad(U)"),
    # 4. pressure solver
    "pcg":       dict(psolver="PCG"),
    # 5. relaxation. This axis is different in kind from all the others and is
    #    the one that matters most for whether a result is defensible:
    #    relaxation changes the path to the answer, not the answer. A converged
    #    second-order solve reached slowly is a second-order solve. A
    #    first-order solve reached quickly is not.
    "slow":      dict(relaxP=0.1, relaxU=0.3),
    "crawl":     dict(relaxP=0.05, relaxU=0.2),
    "crawl2":    dict(relaxP=0.05, relaxU=0.2, nNonOrth=2),
    "crawl3":    dict(relaxP=0.02, relaxU=0.1, nNonOrth=2,
                      divU="bounded Gauss limitedLinear 1",
                      psmooth="DICGaussSeidel", pmaxiter=200),
    # 6. the hardened first-order configuration, for reference only -- NOT a
    #    submission-quality result, carried so the 2nd-order runs have a
    #    known-survivable control on the same grid
    "upwind1":   dict(divU="bounded Gauss upwind", nNonOrth=2,
                      relaxP=0.2, relaxU=0.3, gradU="Gauss linear"),
    # 7. combinations, only tried after the single axes are measured
    "combo":     dict(nNonOrth=2, divU="bounded Gauss linearUpwindV grad(U)",
                      snlim="limited corrected 0.5", laplim="limited corrected 0.5"),
    # 8. the configuration a production RANS setup would actually reach for on
    #    a mesh like this: a TVD face-value limiter for convection (second
    #    order in smooth regions, no gradient reconstruction over a nearly
    #    tangential face-to-cell vector), the non-orthogonal correction limited
    #    hard rather than switched off, two correctors, and slower relaxation.
    "prod":      dict(divU="bounded Gauss limitedLinear 1", nNonOrth=2,
                      snlim="limited corrected 0.25", laplim="limited corrected 0.25",
                      relaxP=0.2, relaxU=0.4),
    # 9. three axes added after the first ladder came back empty, each a
    #    different hypothesis about what actually breaks first:
    #    (a) the pressure solve is allowed to grind to 1000 iterations and
    #        return a half-solved field; cap it instead, as the HLPW6 hardened
    #        run did, so a bad solve is bounded rather than unbounded
    "pcap":      dict(psmooth="DICGaussSeidel", pmaxiter=100),
    #    (b) the wall-distance field, which both turbulence models depend on,
    #        is computed by meshWave -- a marching method whose result on a mesh
    #        with 90-degree faces is not obviously trustworthy, and the crash is
    #        inside the turbulence model
    "wdpois":    dict(walldist="Poisson"),
    #    (c) the run starts from a uniform freestream everywhere, which on a
    #        wing-body at incidence is a violent initial transient; start from a
    #        divergence-free potential solution instead
    "potinit":   dict(potential=True),
    "potprod":   dict(potential=True, divU="bounded Gauss limitedLinear 1",
                      nNonOrth=2, snlim="limited corrected 0.25",
                      laplim="limited corrected 0.25", relaxP=0.2, relaxU=0.4),
}
# any variant may be suffixed "_sa" to swap kOmegaSST for SpalartAllmaras
for _k in list(V):
    V[_k + "_sa"] = dict(V[_k])
assert VARIANT in V, f"unknown variant {VARIANT}; have {sorted(V)}"
c = V[VARIANT]
nNonOrth = c.get("nNonOrth", 0)
divU = c.get("divU", "bounded Gauss linearUpwind grad(U)")
gradU = c.get("gradU", "cellLimited Gauss linear 1")
snlim = c.get("snlim", "limited corrected 0.33")
laplim = c.get("laplim", "limited corrected 0.33")
psolver = c.get("psolver", "GAMG")
relaxP = c.get("relaxP", 0.3)
relaxU = c.get("relaxU", 0.5)
psmooth = c.get("psmooth", "GaussSeidel")
pmaxiter = c.get("pmaxiter", 0)
walldist = c.get("walldist", "meshWave")
potential = c.get("potential", False)

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
        lRef            {MAC:.6f};
        Aref            1.0;
    }}
}}
""")

w("system/fvSchemes", "dictionary", "fvSchemes", f"""
// variant: {VARIANT}
ddtSchemes      {{ default steadyState; }}
gradSchemes     {{ default {gradU}; }}
divSchemes
{{
    default             none;
    div(phi,U)          {divU};
    div(phi,k)          bounded Gauss upwind;
    div(phi,omega)      bounded Gauss upwind;
    div(phi,nuTilda)    bounded Gauss upwind;
    div(phi,e)          bounded Gauss upwind;
    div(phi,h)          bounded Gauss upwind;
    div(phi,K)          bounded Gauss upwind;
    div(phi,Ekp)        bounded Gauss upwind;
    div(phid,p)         bounded Gauss upwind;
    div(div(phi,U))     Gauss linear;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
    div((nuEff*dev2(T(grad(U)))))       Gauss linear;
}}
laplacianSchemes {{ default Gauss linear {laplim}; }}
interpolationSchemes {{ default linear; }}
snGradSchemes   {{ default {snlim}; }}
wallDist        {{ method {walldist}; }}
""")

cap = f"\n        maxIter         {pmaxiter};" if pmaxiter else ""
if psolver == "GAMG":
    pblock = (f"        solver          GAMG;\n"
              f"        smoother        {psmooth};\n"
              f"        tolerance       1e-7;\n"
              f"        relTol          0.01;{cap}")
else:
    pblock = """        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-7;
        relTol          0.01;
        maxIter         2000;"""

extra = ('    "(e|h)" { solver PBiCGStab; preconditioner DILU; tolerance 1e-8; '
         'relTol 0.01; }\n' if COMP else "")
simple_extra = "    rhoMin 0.1; rhoMax 10.0; transonic no;\n" if COMP else ""
relax = (f'    fields {{ p {relaxP}; rho 1.0; }}\n'
         f'    equations {{ U {relaxU}; "(k|omega|nuTilda|e|h)" {relaxU}; }}\n' if COMP else
         f'    fields {{ p {relaxP}; }}\n'
         f'    equations {{ U {relaxU}; "(k|omega|nuTilda)" {relaxU}; }}\n')
w("system/fvSolution", "dictionary", "fvSolution", f"""
// variant: {VARIANT}
solvers
{{
    p
    {{
{pblock}
    }}
    Phi
    {{
        solver          GAMG;
        smoother        DICGaussSeidel;
        tolerance       1e-6;
        relTol          0.01;
    }}
    yPsi
    {{
        solver          GAMG;
        smoother        DICGaussSeidel;
        tolerance       1e-6;
        relTol          0.01;
    }}
{extra}    "(U|k|omega|nuTilda)"
    {{
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-8;
        relTol          0.01;
    }}
}}

potentialFlow
{{
    nNonOrthogonalCorrectors 10;
}}

SIMPLE
{{
    nNonOrthogonalCorrectors {nNonOrth};
    consistent      yes;
{simple_extra}    residualControl {{ p 1e-9; U 1e-9; "(k|omega|nuTilda)" 1e-9; }}
}}

relaxationFactors
{{
{relax}}}
""")

w("system/decomposeParDict", "dictionary", "decomposeParDict",
  f"numberOfSubdomains {NRANKS};\nmethod          scotch;\n")

print(f"case {CASE}  {MODE}  variant={VARIANT}  alpha={ALPHA}  U={Uv}  "
      f"nNonOrth={nNonOrth}  divU='{divU}'  grad='{gradU}'  snGrad='{snlim}'  "
      f"p={psolver}/{psmooth}"
      + (f" maxIter={pmaxiter}" if pmaxiter else "")
      + f"  wallDist={walldist}  potentialInit={potential}"
      + f"  relax p={relaxP} U={relaxU}  iters={ITERS} ranks={NRANKS}")
if potential:
    open(os.path.join(CASE, "POTENTIAL_INIT"), "w").write("yes\n")
