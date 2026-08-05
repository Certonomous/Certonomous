"""Write the 0/ fields and system dictionaries for an in-house PH case.

Patch names follow our own blockMesh (bottomWall, topWall, inlet, outlet,
frontAndBack); the boundary-condition TYPES are the benchmark PH_Breuer case's
own, so that the mesh is the only variable against the 2026-07-29 record.
"""
import sys, os

HDR = """FoamFile
{{
    version 2.0; format ascii; class {cls}; object {obj};
}}
dimensions      {dims};
internalField   uniform {internal};
boundaryField
{{
    bottomWall {{ {wall} }}
    topWall    {{ {wall} }}
    inlet      {{ type cyclic; }}
    outlet     {{ type cyclic; }}
    frontAndBack {{ type empty; }}
}}
"""

FIELDS = [
    ("U", "volVectorField", "[0 1 -1 0 0 0 0]", "(0.72 0 0)",
     "type fixedValue; value uniform (0 0 0);"),
    ("p", "volScalarField", "[0 2 -2 0 0 0 0]", "0",
     "type zeroGradient;"),
    ("k", "volScalarField", "[0 2 -2 0 0 0 0]", "0.00375",
     "type fixedValue; value uniform 1e-15;"),
    ("omega", "volScalarField", "[0 0 -1 0 0 0 0]", "0.11022703842524302",
     "type omegaWallFunction; value uniform 0.11022703842524302;"),
    ("nut", "volScalarField", "[0 2 -1 0 0 0 0]", "0",
     "type nutLowReWallFunction; value uniform 0;"),
]

CONTROL = """FoamFile
{{ version 2.0; format ascii; class dictionary; object controlDict; }}
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      0;
writeFormat     ascii;
writePrecision  12;
writeCompression uncompressed;
timeFormat      general;
timePrecision   12;
runTimeModifiable false;

functions
{{
    wallShearStress
    {{
        type wallShearStress; libs (fieldFunctionObjects);
        patches (bottomWall topWall);
        executeControl writeTime; writeControl writeTime;
    }}
{stations}
}}
"""

STATION = """    singleGraph_x{i}
    {{
        type sets; libs (sampling);
        setFormat raw; interpolationScheme cellPoint;
        fields (U p k omega nut);
        executeControl writeTime; writeControl writeTime;
        sets
        (
            line
            {{
                type midPoint; axis xyz;
                start ({i}.0001 0 0); end ({i}.0001 3.035 0);
            }}
        );
    }}
"""

FVSOL_TAIL = """
SIMPLE
{
    nNonOrthogonalCorrectors 1;
    pRefPoint (0.5 1 0);
    pRefValue 1;
    residualControl
    {
        p       1e-6;
        U       1e-6;
        k       1e-6;
        omega   1e-6;
    }
}

relaxationFactors
{
    p       0.5;
    U       0.5;
    k       0.7;
    omega   0.7;
}
"""

DECOMP = """FoamFile
{{ version 2.0; format ascii; class dictionary; object decomposeParDict; }}
numberOfSubdomains {n};
method scotch;
"""


def main():
    case, end, nranks = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    for obj, cls, dims, internal, wall in FIELDS:
        with open(os.path.join(case, "0", obj), "w") as fh:
            fh.write(HDR.format(cls=cls, obj=obj, dims=dims, internal=internal, wall=wall))
    stations = "".join(STATION.format(i=i) for i in range(9))
    with open(os.path.join(case, "system", "controlDict"), "w") as fh:
        fh.write(CONTROL.format(end=end, stations=stations))
    # keep the benchmark's own solver settings, replace only the SIMPLE block
    src = open(os.path.join(case, "system", "fvSolution")).read()
    src = src[:src.index("SIMPLE")] + FVSOL_TAIL.lstrip()
    open(os.path.join(case, "system", "fvSolution"), "w").write(src)
    open(os.path.join(case, "system", "decomposeParDict"), "w").write(DECOMP.format(n=nranks))
    print("wrote dicts for", case, "endTime", end, "ranks", nranks)


if __name__ == "__main__":
    main()
