#!/usr/bin/env python3
"""Generate a double-Mach-reflection rhoCentralFoam case per DMR_PREREGISTRATION.md.

Usage: make_case.py <casedir> <N>   (N = cells per unit length, e.g. 120)
Inclined-shock formulation, domain [0,4]x[0,1], x0=1/6, Mach 10, gamma=1.4.
Thermo: F3/F4 nondimensional convention (molWeight 11640.3 -> R=5/7, Cp=2.5,
mu=0) so pre-shock T=1, a=1. States per the pre-registration (Kemm 2014):
post-shock rho=8, u=7.1449625, v=-4.125, p=116.5; pre-shock rho=1.4, p=1.
"""
import os, sys, textwrap

case = sys.argv[1]
N = int(sys.argv[2])

X0 = 1.0/6.0
UPOST = (7.1449625, -4.125, 0.0)
PPOST, TPOST = 116.5, 20.3875   # T = p/(rho*R), R = 5/7
PPRE, TPRE = 1.0, 1.0

hdr = lambda cls, obj, loc: textwrap.dedent(f"""\
    FoamFile
    {{
        version 2.0; format ascii; class {cls}; location "{loc}"; object {obj};
    }}
    """)

def write(rel, content):
    p = os.path.join(case, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(content)

nxA = round(X0 * N)          # 0 .. 1/6
nxB = round((4 - X0) * N)    # 1/6 .. 4
ny = N

write("system/blockMeshDict", hdr("dictionary", "blockMeshDict", "system") + f"""
scale 1;
vertices
(
    (0 0 0) ({X0:.10f} 0 0) (4 0 0)
    (0 1 0) ({X0:.10f} 1 0) (4 1 0)
    (0 0 0.01) ({X0:.10f} 0 0.01) (4 0 0.01)
    (0 1 0.01) ({X0:.10f} 1 0.01) (4 1 0.01)
);
blocks
(
    hex (0 1 4 3 6 7 10 9) ({nxA} {ny} 1) simpleGrading (1 1 1)
    hex (1 2 5 4 7 8 11 10) ({nxB} {ny} 1) simpleGrading (1 1 1)
);
boundary
(
    inlet        {{ type patch; faces ((0 6 9 3)); }}
    outlet       {{ type patch; faces ((2 5 11 8)); }}
    bottomInflow {{ type patch; faces ((0 1 7 6)); }}
    rampWall     {{ type symmetryPlane; faces ((1 2 8 7)); }}
    top          {{ type patch; faces ((3 9 10 4) (4 10 11 5)); }}
    frontAndBack {{ type empty; faces ((0 3 4 1) (1 4 5 2) (6 7 10 9) (7 10 11 8)); }}
);
""")

write("constant/thermophysicalProperties", hdr("dictionary", "thermophysicalProperties", "constant") + """
thermoType
{
    type hePsiThermo; mixture pureMixture; transport const; thermo hConst;
    equationOfState perfectGas; specie specie; energy sensibleInternalEnergy;
}
mixture
{
    specie { molWeight 11640.3; }
    thermodynamics { Cp 2.5; Hf 0; }
    transport { mu 0; Pr 1; }
}
""")
write("constant/turbulenceProperties", hdr("dictionary", "turbulenceProperties", "constant") + "simulationType laminar;\n")

write("system/controlDict", hdr("dictionary", "controlDict", "system") + """
application     rhoCentralFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.2;
deltaT          1e-6;
writeControl    adjustableRunTime;
writeInterval   0.02;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           0.2;
maxDeltaT       5e-4;
""")

write("system/fvSchemes", hdr("dictionary", "fvSchemes", "system") + """
fluxScheme          Kurganov;
ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes { default none; div(tauMC) Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes
{
    default         linear;
    reconstruct(rho) vanLeer;
    reconstruct(U)  vanLeerV;
    reconstruct(T)  vanLeer;
}
snGradSchemes { default corrected; }
""")

write("system/fvSolution", hdr("dictionary", "fvSolution", "system") + """
solvers
{
    "(rho|rhoU|rhoE)" { solver diagonal; }
    "(U|e|h)"
    {
        solver smoothSolver; smoother GaussSeidel; nSweeps 2;
        tolerance 1e-09; relTol 0.01;
    }
}
""")

write("system/decomposeParDict", hdr("dictionary", "decomposeParDict", "system") + """
numberOfSubdomains 4;
method scotch;
""")

# --- 0/ fields with coded, exact-kinematics top BC -------------------------
coded_scalar = lambda name, post, pre: f"""
    top
    {{
        type            codedFixedValue;
        value           uniform {pre};
        name            top{name};
        code
        #{{
            const scalar t = this->db().time().value();
            const scalar xs = 1.0/6.0 + (1.0 + 20.0*t)/Foam::sqrt(3.0);
            scalarField& f = *this;
            const vectorField& Cf = patch().Cf();
            forAll(f, i) {{ f[i] = (Cf[i].x() < xs) ? {post} : {pre}; }}
        #}};
    }}"""

write("0/p", hdr("volScalarField", "p", "0") + f"""
dimensions [1 -1 -2 0 0 0 0];
internalField uniform {PPRE};
boundaryField
{{
    inlet        {{ type fixedValue; value uniform {PPOST}; }}
    outlet       {{ type zeroGradient; }}
    bottomInflow {{ type fixedValue; value uniform {PPOST}; }}
    rampWall     {{ type symmetryPlane; }}
{coded_scalar("P", PPOST, PPRE)}
    frontAndBack {{ type empty; }}
}}
""")

write("0/T", hdr("volScalarField", "T", "0") + f"""
dimensions [0 0 0 1 0 0 0];
internalField uniform {TPRE};
boundaryField
{{
    inlet        {{ type fixedValue; value uniform {TPOST}; }}
    outlet       {{ type zeroGradient; }}
    bottomInflow {{ type fixedValue; value uniform {TPOST}; }}
    rampWall     {{ type symmetryPlane; }}
{coded_scalar("T", TPOST, TPRE)}
    frontAndBack {{ type empty; }}
}}
""")

write("0/U", hdr("volVectorField", "U", "0") + f"""
dimensions [0 1 -1 0 0 0 0];
internalField uniform (0 0 0);
boundaryField
{{
    inlet        {{ type fixedValue; value uniform ({UPOST[0]} {UPOST[1]} {UPOST[2]}); }}
    outlet       {{ type zeroGradient; }}
    bottomInflow {{ type fixedValue; value uniform ({UPOST[0]} {UPOST[1]} {UPOST[2]}); }}
    rampWall     {{ type symmetryPlane; }}
    top
    {{
        type            codedFixedValue;
        value           uniform (0 0 0);
        name            topU;
        code
        #{{
            const scalar t = this->db().time().value();
            const scalar xs = 1.0/6.0 + (1.0 + 20.0*t)/Foam::sqrt(3.0);
            vectorField& f = *this;
            const vectorField& Cf = patch().Cf();
            forAll(f, i)
            {{
                f[i] = (Cf[i].x() < xs)
                    ? vector({UPOST[0]}, {UPOST[1]}, {UPOST[2]})
                    : vector(0, 0, 0);
            }}
        #}};
    }}
    frontAndBack {{ type empty; }}
}}
""")

write("system/setExprFieldsDict", hdr("dictionary", "setExprFieldsDict", "system") + f"""
expressions
(
    pInit
    {{
        field p;
        expression #{{ (pos().x() < 1.0/6.0 + pos().y()/sqrt(3.0)) ? {PPOST} : {PPRE} #}};
    }}
    TInit
    {{
        field T;
        expression #{{ (pos().x() < 1.0/6.0 + pos().y()/sqrt(3.0)) ? {TPOST} : {TPRE} #}};
    }}
    UInit
    {{
        field U;
        expression #{{ (pos().x() < 1.0/6.0 + pos().y()/sqrt(3.0)) ? vector({UPOST[0]}, {UPOST[1]}, {UPOST[2]}) : vector(0, 0, 0) #}};
    }}
);
""")

print(f"case {case} written: {nxA}+{nxB} x {ny}")
