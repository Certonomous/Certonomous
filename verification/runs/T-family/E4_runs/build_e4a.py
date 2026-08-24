#!/usr/bin/env python3
"""
E4a case builder -- fanPressure BC verification, exact operating-point class.

WRITES DICTIONARIES ONLY.  Runs no OpenFOAM utility and no solver; creates
no mesh and no time directory.  The five cases (F_c F_m F_f S_f N_f) are 2D
planar laminar channels differing ONLY as registered:

    F_c/F_m/F_f : system/blockMeshDict cell counts (8x100 / 12x150 / 18x225)
    S_f  vs F_f : 0.orig/p fanCurve coefficients (curve B)
    N_f  vs F_f : 0.orig/p fanCurve coefficients (zero) + p0 (0.054)

verify() re-reads every written file and REFUSES (exit 2) unless every file
not registered as changed between a case pair is byte-identical (sha256) and
every file registered as changed is not.

GUARDS (rule 4 age guard carried over): refuses to run if any case directory,
DONE.* / STATUS.* marker, or numeric time directory already exists anywhere
under this tree.  The supervisor commits the freeze BEFORE this builder runs.
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REG = json.load(open(os.path.join(HERE, "E4a_registered.json")))
GEO, NU, TIME = REG["geometry"], REG["nu"], REG["time"]
CASES, CURVES = REG["cases"], REG["curves"]
P = REG["patches"]

EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def header(cls, obj, loc):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
"""


def g(x):
    return f"{x:.12g}"


def fan_curve_entry(curve):
    pairs = " ".join(f"({g(c)} {g(e)})" for c, e in CURVES[curve]["coeffs"])
    return f"polynomial ( {pairs} )"


def p_field(curve):
    c = CURVES[curve]
    return header("volScalarField", "p", "0") + f"""
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
    {P['fan']}
    {{
        // fanPressureFvPatchScalarField, ESI v2606.  Entries read by the BC:
        //   direction (.cxx:91), fanCurve via Function1 (.cxx:97-107),
        //   nonDimensional (.cxx:92, default false, NOT used here),
        //   p0/U/phi/rho/psi/gamma/value inherited from totalPressure.
        type            fanPressure;
        direction       in;
        fanCurve        {fan_curve_entry(curve)};
        p0              uniform {g(c['p0_env'])};
        value           uniform 0;
    }}
    {P['outlet']}
    {{
        type            fixedValue;
        value           uniform {g(REG['p_out'])};
    }}
    {P['walls']}
    {{
        type            zeroGradient;
    }}
    {P['empty']}
    {{
        type            empty;
    }}
}}
"""


def u_field():
    return header("volVectorField", "U", "0") + f"""
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{{
    {P['fan']}
    {{
        type            pressureInletOutletVelocity;
        value           uniform (0 0 0);
    }}
    {P['outlet']}
    {{
        type            inletOutlet;
        inletValue      uniform (0 0 0);
        value           uniform (0 0 0);
    }}
    {P['walls']}
    {{
        type            noSlip;
    }}
    {P['empty']}
    {{
        type            empty;
    }}
}}
"""


def block_mesh(nx, ny):
    L, h, t = GEO["L"], GEO["h"], GEO["t"]
    return header("dictionary", "blockMeshDict", "system") + f"""
scale   1;

vertices
(
    (0 0 0)                                 // 0
    ({g(L)} 0 0)                            // 1
    ({g(L)} {g(h)} 0)                       // 2
    (0 {g(h)} 0)                            // 3
    (0 0 {g(t)})                            // 4
    ({g(L)} 0 {g(t)})                       // 5
    ({g(L)} {g(h)} {g(t)})                  // 6
    (0 {g(h)} {g(t)})                       // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    {P['fan']}
    {{
        type patch;
        faces ((0 4 7 3));
    }}
    {P['outlet']}
    {{
        type patch;
        faces ((1 2 6 5));
    }}
    {P['walls']}
    {{
        type wall;
        faces ((0 1 5 4) (3 7 6 2));
    }}
    {P['empty']}
    {{
        type empty;
        faces ((0 3 2 1) (4 5 6 7));
    }}
);
"""


def control_dict():
    return header("dictionary", "controlDict", "system") + f"""
application     simpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {TIME['endTime']};
deltaT          {TIME['deltaT']};

// writeInterval STRICTLY < endTime (L-140): four checkpoints on disk, and the
// convergence gate compares the last two written checkpoints value for value.
writeControl    timeStep;
writeInterval   {TIME['writeInterval']};
purgeWrite      0;
writeFormat     ascii;
writePrecision  {TIME['writePrecision']};
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""


def fv_schemes():
    return header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default                       none;
    div(phi,U)                    bounded Gauss linear;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
"""


def fv_solution():
    return header("dictionary", "fvSolution", "system") + """
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0;
    }
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-10;
        relTol          0;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    // NO residualControl (L-141): convergence is judged by the frozen
    // comparator from written checkpoints, never by the solver.
}

relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; }
}
"""


def transport():
    return header("dictionary", "transportProperties", "constant") + f"""
transportModel  Newtonian;

nu              [0 2 -1 0 0 0 0] {g(NU)};
"""


def turbulence():
    return header("dictionary", "turbulenceProperties", "constant") + """
simulationType  laminar;
"""


FILES = ("0.orig/p", "0.orig/U",
         "constant/transportProperties", "constant/turbulenceProperties",
         "system/blockMeshDict", "system/controlDict",
         "system/fvSchemes", "system/fvSolution")


def guard():
    for name in CASES:
        if os.path.exists(os.path.join(HERE, name)):
            refuse(f"case directory {name} already exists -- the freeze rule "
                   "requires ZERO case directories at build (rule 4)")
    for entry in os.listdir(HERE):
        if entry.startswith(("DONE.", "STATUS.")):
            refuse(f"completion marker {entry} already exists")
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", entry):
            refuse(f"stray numeric time directory {entry} in the run tree")


def write_case(name):
    spec = CASES[name]
    d = os.path.join(HERE, name)
    content = {
        "0.orig/p": p_field(spec["curve"]),
        "0.orig/U": u_field(),
        "constant/transportProperties": transport(),
        "constant/turbulenceProperties": turbulence(),
        "system/blockMeshDict": block_mesh(spec["nx"], spec["ny"]),
        "system/controlDict": control_dict(),
        "system/fvSchemes": fv_schemes(),
        "system/fvSolution": fv_solution(),
    }
    for rel, txt in content.items():
        path = os.path.join(d, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(txt)


# registered one-change structure: pairs (other, reference, files allowed to differ)
DIFF_SPEC = {
    "F_c": ("F_f", {"system/blockMeshDict"}),
    "F_m": ("F_f", {"system/blockMeshDict"}),
    "S_f": ("F_f", {"0.orig/p"}),
    "N_f": ("F_f", {"0.orig/p"}),
}


def verify():
    sha = {name: {rel: sha256_of(os.path.join(HERE, name, rel))
                  for rel in FILES} for name in CASES}
    for other, (ref, allowed) in DIFF_SPEC.items():
        for rel in FILES:
            same = sha[other][rel] == sha[ref][rel]
            if rel in allowed and same:
                refuse(f"{other}/{rel} registered as changed vs {ref} but is "
                       "byte-identical")
            if rel not in allowed and not same:
                refuse(f"{other}/{rel} NOT registered as changed vs {ref} but "
                       "differs")
    return sha


def main():
    guard()
    for name in CASES:
        write_case(name)
    sha = verify()
    man = os.path.join(HERE, "BUILD_MANIFEST.txt")
    with open(man, "w") as fh:
        fh.write("E4a build manifest -- dictionaries only; no utility, no "
                 "solver, no mesh, no time directory was created.\n")
        for name in sorted(CASES):
            for rel in FILES:
                fh.write(f"{sha[name][rel]}  {name}/{rel}\n")
    print(f"built {len(CASES)} case dictionaries; one-change verify() passed; "
          f"manifest {man}")
    for name in sorted(CASES):
        c = CASES[name]
        print(f"  {name:5s} curve {c['curve']:4s} ny {c['ny']:3d} nx "
              f"{c['nx']:3d} cells {c['nx']*c['ny']:6d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
