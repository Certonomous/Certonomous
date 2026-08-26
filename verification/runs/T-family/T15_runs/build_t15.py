#!/usr/bin/env python3
"""T15 case builder -- the UNSTEADY successor of T8, ONE LEVEL.

WRITTEN BEFORE THE PRE-REGISTRATION WAS FROZEN AND BEFORE ANY SOLVER RAN.
It writes dictionaries, `0.orig` and NOTHING ELSE.  It NEVER writes `0/` and it
NEVER writes a time directory: `0/` is created only at launch by
run_one_t15.sh, which touches `0/T` LAST so the age guard of CLAUDE.md rule 4
can date the run.  A case whose `0/` already exists is REFUSED.

GEOMETRY AND PHYSICS ARE T8's FINE LEVEL, UNCHANGED (T8_PREREGISTRATION.md
sections 1, 5, 12): 5 deg axisymmetric wedge about z, source diameter D = 0.2 m,
domain R = 12 D, H = 40 D, radial blocks 16/48/64/32, axial 640 -> 102 400
cells; Gamma_0 = 1 pure-plume source, kEpsilon, Boussinesq.

WHAT IS DIFFERENT, AND IT IS THE WHOLE POINT: the solver is
buoyantBoussinesqPimpleFoam and the run is TRANSIENT.  T8's registered STEADY
formulation reached a converged state at no resolution
(T8_VERDICT_2026-08-26.md); the record's sharpest named discriminator is "an
unsteady run at one level ... because it does not depend on reading a steady
solver's residual" (T8_STEADINESS_MEASUREMENT_2026-08-26.md section 6.2, and
section 7.4 which names it the sharpest of the three).

ddtSchemes is `backward`, SECOND ORDER, deliberately: Euler's first-order
damping would bias the measurement toward the STEADY side, which is the
registered gate's PASS side, and a gate must not be helped by its own scheme.

NO `assert` (L-332); every refusal is sys.exit(2) or a REFUSE return.
Usage:  python3 build_t15.py [--root DIR] [--case NAME] [--selftest]
"""
import argparse
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXIT_OK, EXIT_REFUSE = 0, 2

# ---- registered constants (identical to T8's, T8_PREREGISTRATION.md) -------
D_SOURCE = 0.2
B0 = D_SOURCE / 2.0
R_DOMAIN = 12.0 * D_SOURCE
H_DOMAIN = 40.0 * D_SOURCE
WEDGE_HALF_ANGLE_DEG = 2.5

W0 = 0.6
ALPHA_NOMINAL = 0.12
RI0 = 8.0 * ALPHA_NOMINAL / 5.0
GPRIME0 = RI0 * W0 ** 2 / B0
G_ACCEL = 9.81
TREF = 300.0
BETA = 1.0 / 300.0
DT0 = 21.1376
T_SOURCE = TREF + DT0
F0 = math.pi * B0 ** 2 * W0 * GPRIME0

NU = 1.5e-05
PR = 0.71
PRT = 0.85
TI = 0.05
K0 = 1.5 * (TI * W0) ** 2
LMIX = 0.07 * D_SOURCE
EPS0 = 0.09 ** 0.75 * K0 ** 1.5 / LMIX
K_AMB = 1.0e-06
EPS_AMB = 1.0e-06

R_STATIONS = (0.0, 0.1, 0.4, 1.2, 2.4)
NR = (16, 48, 64, 32)
NZ = 640
EXPECT_CELLS = 102400

# ---- registered TRANSIENT specification ------------------------------------
CASE_NAME = "T15_UP_f"
SOLVER = "buoyantBoussinesqPimpleFoam"
END_TIME = 240.0          # s
DELTA_T = 0.01            # s, FIXED (adjustTimeStep off)
N_STEPS = 24000
WRITE_INTERVAL = 6000     # timesteps -> writes at 60, 120, 180, 240 s
WINDOW_START = 120.0      # s, the registered averaging window [120, 240]
PROBE_INTERVAL = 10       # timesteps -> 0.1 s sampling
DR_BLOCK1 = (R_STATIONS[1] - R_STATIONS[0]) / NR[0]     # 0.00625 m
R_PROBE = 0.25 * DR_BLOCK1                              # 0.0015625 m, INSIDE cell j=0
PROBE_Z = (2.0, 3.0, 4.0, 5.0)                          # z/D = 10, 15, 20, 25
S1_STATION_Z = 3.0                                      # z/D = 15, the registered S1 station

HEAD = """/*--------------------------------*- C++ -*----------------------------------*\\
  =========                 |
  \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\\\    /   O peration     | www.openfoam.com
    \\\\  /    A nd           |
     \\\\/     M anipulation  |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""
TAIL = "\n// ************************************************************************* //\n"


def write(path, cls, loc, obj, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HEAD.format(cls=cls, loc=loc, obj=obj))
        fh.write(body)
        fh.write(TAIL)


# ---------------------------------------------------------------------------
def block_mesh_dict():
    """4 radial blocks x 1 axial block, 5 deg wedge about z.  Line-for-line the
    T8 generator (build_t8.py:112) at the fine divisions -- the geometry under
    test is T8's, and changing it would change the question."""
    half = math.radians(WEDGE_HALF_ANGLE_DEG)
    c, s = math.cos(half), math.sin(half)
    verts, vid = [], {}

    def add(name, x, y, z):
        vid[name] = len(verts)
        verts.append((x, y, z))

    add("A0", 0.0, 0.0, 0.0)
    add("A1", 0.0, 0.0, H_DOMAIN)
    for k in range(1, 5):
        r = R_STATIONS[k]
        add("B%d_0" % k, r * c, -r * s, 0.0)
        add("B%d_1" % k, r * c, -r * s, H_DOMAIN)
        add("F%d_0" % k, r * c, +r * s, 0.0)
        add("F%d_1" % k, r * c, +r * s, H_DOMAIN)

    def inner(k, side, j):
        if k == 1:
            return vid["A0" if j == 0 else "A1"]
        return vid["%s%d_%d" % (side, k - 1, j)]

    def outer(k, side, j):
        return vid["%s%d_%d" % (side, k, j)]

    blocks = []
    for k in range(1, 5):
        vv = (inner(k, "F", 0), outer(k, "F", 0), outer(k, "F", 1), inner(k, "F", 1),
              inner(k, "B", 0), outer(k, "B", 0), outer(k, "B", 1), inner(k, "B", 1))
        blocks.append((k, vv, NR[k - 1], NZ))

    def face_bottom(k):
        return (inner(k, "B", 0), outer(k, "B", 0), outer(k, "F", 0), inner(k, "F", 0))

    def face_top(k):
        return (inner(k, "B", 1), outer(k, "B", 1), outer(k, "F", 1), inner(k, "F", 1))

    def face_outer(k):
        return (outer(k, "B", 0), outer(k, "B", 1), outer(k, "F", 1), outer(k, "F", 0))

    def face_back(k):
        return (inner(k, "B", 0), outer(k, "B", 0), outer(k, "B", 1), inner(k, "B", 1))

    def face_front(k):
        return (inner(k, "F", 0), outer(k, "F", 0), outer(k, "F", 1), inner(k, "F", 1))

    def fstr(f):
        return "            (%d %d %d %d)\n" % f

    L = ["mergeType points;   // wedge: merge coincident axis points\n\n", "scale 1;\n\nvertices\n(\n"]
    for (x, y, z) in verts:
        L.append("    (%.12f %.12f %.12f)\n" % (x, y, z))
    L.append(");\n\nblocks\n(\n")
    for k, vv, nrk, nzk in blocks:
        L.append("    hex (%d %d %d %d %d %d %d %d) (%d %d 1) simpleGrading (1 1 1)\n" % (vv + (nrk, nzk)))
    L.append(");\n\nedges ();\n\nboundary\n(\n")
    L.append("    source\n    {\n        type patch;\n        faces\n        (\n")
    L.append(fstr(face_bottom(1)))
    L.append("        );\n    }\n\n")
    L.append("    floor\n    {\n        type wall;\n        faces\n        (\n")
    for k in (2, 3, 4):
        L.append(fstr(face_bottom(k)))
    L.append("        );\n    }\n\n")
    L.append("    outlet\n    {\n        type patch;\n        faces\n        (\n")
    for k in (1, 2, 3, 4):
        L.append(fstr(face_top(k)))
    L.append("        );\n    }\n\n")
    L.append("    farfield\n    {\n        type patch;\n        faces\n        (\n")
    L.append(fstr(face_outer(4)))
    L.append("        );\n    }\n\n")
    L.append("    wedge_back\n    {\n        type wedge;\n        faces\n        (\n")
    for k in (1, 2, 3, 4):
        L.append(fstr(face_back(k)))
    L.append("        );\n    }\n\n")
    L.append("    wedge_front\n    {\n        type wedge;\n        faces\n        (\n")
    for k in (1, 2, 3, 4):
        L.append(fstr(face_front(k)))
    L.append("        );\n    }\n);\n\nmergePatchPairs ();\n")
    return "".join(L)


def field(dims, internal, entries):
    L = ["dimensions      %s;\n\ninternalField   uniform %s;\n\nboundaryField\n{\n" % (dims, internal)]
    for name, blk in entries:
        L.append("    %s\n    {\n" % name)
        for line in blk:
            L.append("        %s\n" % line)
        L.append("    }\n")
    L.append("}\n")
    return "".join(L)


def fields():
    W = ["type            wedge;"]
    out = {}
    out["U"] = ("volVectorField", field("[0 1 -1 0 0 0 0]", "(0 0 0)", [
        ("source", ["type            fixedValue;", "value           uniform (0 0 %.6f);" % W0]),
        ("floor", ["type            noSlip;"]),
        ("outlet", ["type            pressureInletOutletVelocity;", "value           uniform (0 0 0);"]),
        ("farfield", ["type            pressureInletOutletVelocity;", "value           uniform (0 0 0);"]),
        ("wedge_back", W), ("wedge_front", W)]))
    out["T"] = ("volScalarField", field("[0 0 0 1 0 0 0]", "%.6f" % TREF, [
        ("source", ["type            fixedValue;", "value           uniform %.6f;" % T_SOURCE]),
        ("floor", ["type            zeroGradient;"]),
        ("outlet", ["type            inletOutlet;", "inletValue      uniform %.6f;" % TREF,
                    "value           uniform %.6f;" % TREF]),
        ("farfield", ["type            inletOutlet;", "inletValue      uniform %.6f;" % TREF,
                      "value           uniform %.6f;" % TREF]),
        ("wedge_back", W), ("wedge_front", W)]))
    out["p_rgh"] = ("volScalarField", field("[0 2 -2 0 0 0 0]", "0", [
        ("source", ["type            fixedFluxPressure;", "value           uniform 0;"]),
        ("floor", ["type            fixedFluxPressure;", "value           uniform 0;"]),
        ("outlet", ["type            fixedValue;", "value           uniform 0;"]),
        ("farfield", ["type            fixedValue;", "value           uniform 0;"]),
        ("wedge_back", W), ("wedge_front", W)]))
    out["k"] = ("volScalarField", field("[0 2 -2 0 0 0 0]", "%.8g" % K_AMB, [
        ("source", ["type            fixedValue;", "value           uniform %.8g;" % K0]),
        ("floor", ["type            kqRWallFunction;", "value           uniform %.8g;" % K_AMB]),
        ("outlet", ["type            inletOutlet;", "inletValue      uniform %.8g;" % K_AMB,
                    "value           uniform %.8g;" % K_AMB]),
        ("farfield", ["type            inletOutlet;", "inletValue      uniform %.8g;" % K_AMB,
                      "value           uniform %.8g;" % K_AMB]),
        ("wedge_back", W), ("wedge_front", W)]))
    out["epsilon"] = ("volScalarField", field("[0 2 -3 0 0 0 0]", "%.8g" % EPS_AMB, [
        ("source", ["type            fixedValue;", "value           uniform %.8g;" % EPS0]),
        ("floor", ["type            epsilonWallFunction;", "value           uniform %.8g;" % EPS_AMB]),
        ("outlet", ["type            inletOutlet;", "inletValue      uniform %.8g;" % EPS_AMB,
                    "value           uniform %.8g;" % EPS_AMB]),
        ("farfield", ["type            inletOutlet;", "inletValue      uniform %.8g;" % EPS_AMB,
                      "value           uniform %.8g;" % EPS_AMB]),
        ("wedge_back", W), ("wedge_front", W)]))
    out["nut"] = ("volScalarField", field("[0 2 -1 0 0 0 0]", "0", [
        ("source", ["type            calculated;", "value           uniform 0;"]),
        ("floor", ["type            nutkWallFunction;", "value           uniform 0;"]),
        ("outlet", ["type            calculated;", "value           uniform 0;"]),
        ("farfield", ["type            calculated;", "value           uniform 0;"]),
        ("wedge_back", W), ("wedge_front", W)]))
    out["alphat"] = ("volScalarField", field("[0 2 -1 0 0 0 0]", "0", [
        ("source", ["type            calculated;", "value           uniform 0;"]),
        ("floor", ["type            calculated;", "value           uniform 0;"]),
        ("outlet", ["type            calculated;", "value           uniform 0;"]),
        ("farfield", ["type            calculated;", "value           uniform 0;"]),
        ("wedge_back", W), ("wedge_front", W)]))
    return out


def constant_files():
    return {
        "g": ("uniformDimensionedVectorField",
              "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 -%.2f);\n" % G_ACCEL),
        "transportProperties": ("dictionary",
                                "transportModel  Newtonian;\n\nnu              %.8g;\nbeta            %.10g;\n"
                                "TRef            %.6f;\nPr              %.6g;\nPrt             %.6g;\n"
                                % (NU, BETA, TREF, PR, PRT)),
        "turbulenceProperties": ("dictionary",
                                 "simulationType  RAS;\n\nRAS\n{\n    RASModel        kEpsilon;\n"
                                 "    turbulence      on;\n    printCoeffs     on;\n}\n"),
    }


def control_dict():
    probes = "".join("        (%.10g 0 %.10g)\n" % (R_PROBE, z) for z in PROBE_Z)
    return ("application     %s;\n\n"
            "startFrom       startTime;\nstartTime       0;\n"
            "stopAt          endTime;\nendTime         %.10g;\ndeltaT          %.10g;\n"
            "adjustTimeStep  no;\n\n"
            "writeControl    timeStep;\nwriteInterval   %d;\npurgeWrite      0;\n"
            "writeFormat     ascii;\nwritePrecision  16;\nwriteCompression off;\n"
            "timeFormat      general;\ntimePrecision   8;\n"
            "runTimeModifiable false;\n\n"
            "functions\n{\n"
            "    axisProbes\n    {\n"
            "        type            probes;\n        libs            (sampling);\n"
            "        writeControl    timeStep;\n        writeInterval   %d;\n"
            "        fields          (U T);\n"
            "        fixedLocations  true;\n"
            "        probeLocations\n        (\n%s        );\n"
            "    }\n\n"
            "    fieldAverage1\n    {\n"
            "        type            fieldAverage;\n        libs            (fieldFunctionObjects);\n"
            "        writeControl    writeTime;\n        timeStart       %.10g;\n"
            "        restartOnRestart false;\n        restartOnOutput  false;\n"
            "        fields\n        (\n"
            "            U { mean on; prime2Mean on; base time; }\n"
            "            T { mean on; prime2Mean on; base time; }\n"
            "        );\n    }\n}\n"
            % (SOLVER, END_TIME, DELTA_T, WRITE_INTERVAL, PROBE_INTERVAL, probes, WINDOW_START))


FV_SCHEMES = """ddtSchemes      { default backward; }

gradSchemes     { default Gauss linear; }

divSchemes
{
    default          none;
    div(phi,U)       Gauss linearUpwind grad(U);
    div(phi,T)       Gauss limitedLinear 1;
    div(phi,k)       Gauss limitedLinear 1;
    div(phi,epsilon) Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes { default Gauss linear corrected; }

interpolationSchemes { default linear; }

snGradSchemes   { default corrected; }

wallDist        { method meshWave; }
"""

FV_SOLUTION = """solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0.01;
    }

    p_rghFinal
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-09;
        relTol          0;
    }

    "(U|T|k|epsilon)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-09;
        relTol          0.1;
    }

    "(U|T|k|epsilon)Final"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-10;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor        yes;
    nOuterCorrectors         2;
    nCorrectors              2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

relaxationFactors
{
    fields    { p_rgh 0.7; }
    equations { "(U|T|k|epsilon)" 0.7; ".*Final" 1.0; }
}
"""


def build(root, case_name=CASE_NAME):
    case = os.path.join(root, case_name)
    if os.path.isdir(os.path.join(case, "0")):
        print("REFUSE: %s already has a 0/ directory" % case)
        return EXIT_REFUSE
    times = [d for d in (os.listdir(case) if os.path.isdir(case) else [])
             if d.replace(".", "", 1).isdigit() and float(d) > 0]
    if times:
        print("REFUSE: %s already has time directories %s" % (case, sorted(times)))
        return EXIT_REFUSE
    if abs(N_STEPS - END_TIME / DELTA_T) > 1e-9:
        print("REFUSE: registered N_STEPS %d != endTime/deltaT = %.10g" % (N_STEPS, END_TIME / DELTA_T))
        return EXIT_REFUSE
    if not (0.0 < R_PROBE < DR_BLOCK1):
        print("REFUSE: the probe radius %.10g is not strictly inside the innermost radial cell "
              "[0, %.10g] -- a probe on a block face is not a registered location" % (R_PROBE, DR_BLOCK1))
        return EXIT_REFUSE
    if not (min(PROBE_Z) >= 2.0 and max(PROBE_Z) <= H_DOMAIN - 3.0):
        print("REFUSE: a probe station is outside the registered fit window / too close to the outlet")
        return EXIT_REFUSE

    write(os.path.join(case, "system", "blockMeshDict"), "dictionary", "system", "blockMeshDict", block_mesh_dict())
    write(os.path.join(case, "system", "controlDict"), "dictionary", "system", "controlDict", control_dict())
    write(os.path.join(case, "system", "fvSchemes"), "dictionary", "system", "fvSchemes", FV_SCHEMES)
    write(os.path.join(case, "system", "fvSolution"), "dictionary", "system", "fvSolution", FV_SOLUTION)
    for name, (cls, body) in constant_files().items():
        write(os.path.join(case, "constant", name), cls, "constant", name, body)
    for name, (cls, body) in fields().items():
        write(os.path.join(case, "0.orig", name), cls, "0", name, body)

    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write("# T15 unsteady MTT plume -- registered case constants (read by analyse_t15.py)\n"
                 "case %s\nlevel f_unsteady_single\nsolver %s\n"
                 "D %.10g m\nb0 %.10g m\nR_domain %.10g m\nH_domain %.10g m\n"
                 "wedge_half_angle_deg %.10g deg\nw0 %.10g m/s\ngprime0 %.10g m/s2\ndT0 %.10g K\n"
                 "T_source %.10g K\nF0 %.12g m4/s3\nTRef %.10g K\nbeta %.12g 1/K\ng %.10g m/s2\n"
                 "nu %.10g m2/s\nPr %.10g -\nPrt %.10g -\nk0 %.10g m2/s2\nepsilon0 %.10g m2/s3\n"
                 "alpha_nominal %.10g -\nnr_blocks %s -\nnz %d -\nn_cells_expected %d -\n"
                 "endTime %.10g s\ndeltaT %.10g s\nn_steps %d -\nwriteInterval %d steps\n"
                 "window_start %.10g s\nprobe_r %.12g m\nprobe_z %s m\ns1_station_z %.10g m\n"
                 "probe_interval %d steps\nnProcs 1 -\n"
                 % (case_name, SOLVER, D_SOURCE, B0, R_DOMAIN, H_DOMAIN, WEDGE_HALF_ANGLE_DEG,
                    W0, GPRIME0, DT0, T_SOURCE, F0, TREF, BETA, G_ACCEL, NU, PR, PRT, K0, EPS0,
                    ALPHA_NOMINAL, "/".join(str(x) for x in NR), NZ, EXPECT_CELLS,
                    END_TIME, DELTA_T, N_STEPS, WRITE_INTERVAL, WINDOW_START, R_PROBE,
                    "/".join("%.10g" % z for z in PROBE_Z), S1_STATION_Z, PROBE_INTERVAL))
    print("built %s  (expect %d cells, %d steps of %.10g s to %.10g s)"
          % (case, EXPECT_CELLS, N_STEPS, DELTA_T, END_TIME))
    return EXIT_OK


def selftest():
    import ast
    import shutil
    import tempfile
    fails = []
    print("build_t15 selftest:")
    tmp = tempfile.mkdtemp(prefix="t15build_")
    try:
        rc = build(tmp, "T15_UP_f")
        ok = (rc == EXIT_OK and os.path.isfile(os.path.join(tmp, "T15_UP_f", "system", "blockMeshDict")))
        print("  [%s] fresh build -> rc 0, dictionaries written, NO 0/ and NO time directory (%s)"
              % ("ok " if ok else "FAIL",
                 "0/ absent" if not os.path.isdir(os.path.join(tmp, "T15_UP_f", "0")) else "0/ PRESENT"))
        if not ok or os.path.isdir(os.path.join(tmp, "T15_UP_f", "0")):
            fails.append("build")
        # the block count and cell count implied by the dict
        bm = open(os.path.join(tmp, "T15_UP_f", "system", "blockMeshDict")).read()
        cells = sum(int(a) * int(b) for a, b in
                    __import__("re").findall(r"simpleGrading", bm) and
                    __import__("re").findall(r"\((\d+) (\d+) 1\) simpleGrading", bm))
        ok = (cells == EXPECT_CELLS)
        print("  [%s] blockMeshDict implies %d cells (registered %d)" % ("ok " if ok else "FAIL", cells, EXPECT_CELLS))
        if not ok:
            fails.append("cells")
        # the guard: a 0/ directory refuses
        os.makedirs(os.path.join(tmp, "T15_UP_f", "0"))
        rc = build(tmp, "T15_UP_f")
        ok = (rc == EXIT_REFUSE)
        print("  [%s] existing 0/ -> REFUSE (rc %s)" % ("ok " if ok else "FAIL", rc))
        if not ok:
            fails.append("guard0")
        shutil.rmtree(os.path.join(tmp, "T15_UP_f"))
        os.makedirs(os.path.join(tmp, "T15_UP_f", "250"))
        rc = build(tmp, "T15_UP_f")
        ok = (rc == EXIT_REFUSE)
        print("  [%s] existing numeric time directory 250/ -> REFUSE (rc %s)" % ("ok " if ok else "FAIL", rc))
        if not ok:
            fails.append("guardT")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # derived constants, checked rather than trusted
    ok = (abs(GPRIME0 - 0.6912) < 1e-12 and abs(F0 - 0.0130288128) < 1e-9
          and abs(K0 - 1.35e-3) < 1e-12 and abs(R_PROBE - 0.0015625) < 1e-15)
    print("  [%s] derived source constants: g'0 %.6f, F0 %.12g, k0 %.6g, r_probe %.10g m"
          % ("ok " if ok else "FAIL", GPRIME0, F0, K0, R_PROBE))
    if not ok:
        fails.append("constants")
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--case", default=CASE_NAME)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    return build(os.path.abspath(a.root), a.case)


if __name__ == "__main__":
    sys.exit(main())
