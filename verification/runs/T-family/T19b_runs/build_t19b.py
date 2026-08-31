#!/usr/bin/env python3
"""Build T19b's registered cases: fully developed laminar forced convection
between PARALLEL PLATES, 2-D Cartesian (the planar partner of T1c's wedge pipe).

T19b IS T19's SUCCESSOR AND ITS ONLY SUBSTANTIVE DIFFERENCE FROM build_t19.py IS
THAT fv_solution() DOES NOT EMIT A `residualControl` BLOCK.  build_t19.py:211
wrote `residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }`, and on T19 that tripped
on both cases that ran: P_q_c stopped at 828 iterations and P_Ts_c at 541,
against the registered endTime 30000.  Rule 4's `last time == endTime` then
cannot hold and C_PLATEAU -- which compares the graded quantities between the
writes at 28000 and 30000 -- has no pair to read and is UNEVALUABLE.
DEAD_LEVER_AUDIT.md section 21.2 ruled the legal repair is to the CASE and not
to a gate: drop residualControl so the solver runs to the registered endTime as
T1c did.  NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES.  Nothing else in this
file changes: the mesh, the fields, the boundary conditions, the schemes,
endTime, writeInterval and the ladder are byte-identical to the parent's, and
selftest limb `no-residualControl` plus the tree comparison registered in
T19b_PREREGISTRATION.md section 4 measure that rather than assert it.

SOLVER.  `buoyantBoussinesqSimpleFoam` with `simulationType laminar` and
`beta = 0`, exactly as T1c (build_t1c.py:219 "ZERO GRAVITY IS THE POINT"):
with beta = 0 the momentum equation is decoupled from T and the solver is a
pure incompressible forced-convection solver.  The case template is T1c's, with
the wedge replaced by a Cartesian channel and the wall patches doubled.

GEOMETRY.  Full gap b (BOTH walls resolved, no symmetry plane assumed -- the
symmetry of the answer is then a witness rather than an assumption), length
L = 30 Dh, hydraulic diameter Dh = 2b.  Uniform inlet velocity and temperature;
the flow and the thermal field develop and are sampled at ONE registered
station x_s = 20 Dh, which is x+ = x_s/(Dh Re Pr) = 0.2817 -- past the point
where the Graetz solution is within 0.01 percent of its asymptote.

TWO ARMS, six cases:
  * P_Ts_{c,m,f}: both walls at a fixed temperature (grades Nu_T and, as an
    identity control, f.Re)
  * P_q_{c,m,f} : both walls at a fixed uniform normal gradient (grades Nu_H
    and f.Re)
The hydrodynamics is IDENTICAL in the two arms (beta = 0), so f.Re read from
both must agree to round-off; that is control C_ID.

T_WALL IS 400 K, NOT T1c's 310 K, AND THE REASON IS REGISTERED.  The graded
constant-wall-temperature Nusselt number is q"Dh/(k(T_w - T_m)), and at the
registered station T_w - T_m has decayed to about 2.0e-04 of the inlet
difference.  With T1c's 10 K difference that is 2.0e-03 K; with 100 K it is
2.0e-02 K, ten times better conditioned, and beta = 0 makes the larger
difference dynamically inert.  T1c's own constant-T row GATE FAILED
(T1c_RESULTS.md:14, 0.0865 percent against a 0.0301 percent band) and this is
one of the two things this rung changes about it (the other is the band, which
is armed from that measured 0.0865 percent rather than from optimism).

NO assert (L-332).  Every refusal is sys.exit(2).

usage: build_t19b.py --root DIR [--case NAME ...] [--no-mesh] | --check-levels | --selftest
"""
import argparse
import os
import re
import subprocess
import sys
import time

B_GAP = 0.02              # m, FULL gap between the plates
DH = 2.0 * B_GAP          # m, hydraulic diameter of a parallel-plate duct
NU = 1.5e-05              # m2/s
PR = 0.71
RE = 100.0
U0 = RE * NU / DH         # m/s
L = 30.0 * DH             # m, channel length
X_S = 20.0 * DH           # m, the ONE registered sampling station
WIDTH = 0.001             # m, the empty-direction thickness
T_IN = 300.0              # K
T_WALL = 400.0            # K, the constant-Ts arm
DTDN = 500.0              # K/m, the constant-q" arm (outward normal gradient at the wall)
END_TIME = 30000          # SIMPLE iterations (deltaT = 1), T1c's registered count
WRITE_INTERVAL = 2000     # STRICTLY < END_TIME (L-140)

LEVELS = {"c": (120, 20), "m": (240, 40), "f": (480, 80)}     # (nx, ny) over the FULL gap
CASES = {}
for _lv, _d in LEVELS.items():
    CASES["P_Ts_%s" % _lv] = dict(level=_lv, nx=_d[0], ny=_d[1], wall="fixedTemperature")
    CASES["P_q_%s" % _lv] = dict(level=_lv, nx=_d[0], ny=_d[1], wall="fixedFlux")

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def check_levels(levels=None):
    levels = levels or LEVELS
    ny = {k: v[1] for k, v in levels.items()}
    nx = {k: v[0] for k, v in levels.items()}
    if len(set(ny.values())) != len(ny) or len(set(nx.values())) != len(nx):
        refuse("two levels share a mesh count: nx %r ny %r -- the triple would measure nothing" % (nx, ny))
    if not (ny["m"] == 2 * ny["c"] and ny["f"] == 2 * ny["m"]
            and nx["m"] == 2 * nx["c"] and nx["f"] == 2 * nx["m"]):
        refuse("the ladder is not r = 2 in BOTH directions: nx %r ny %r" % (nx, ny))
    for lv, (mx, my) in levels.items():
        if abs(X_S / (L / mx) - round(X_S / (L / mx))) > 1e-12:
            refuse("the station x_s = %g is not on a cell FACE at level %s (dx = %g); the reader "
                   "would interpolate differently on different levels" % (X_S, lv, L / mx))
    return dict(nx=nx, ny=ny)


def header(cls, obj, loc):
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n    location    \"%s\";\n    object      %s;\n}\n" % (cls, loc, obj))


def block_mesh(nx, ny):
    return header("dictionary", "blockMeshDict", "system") + (
        "\nscale 1;\n\nvertices\n(\n"
        "    (0 0 0) (%.8f 0 0) (%.8f %.8f 0) (0 %.8f 0)\n"
        "    (0 0 %.8f) (%.8f 0 %.8f) (%.8f %.8f %.8f) (0 %.8f %.8f)\n);\n\n"
        "blocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d 1) simpleGrading (1 1 1)\n);\n\n"
        "edges ();\n\nboundary\n(\n"
        "    inlet     { type patch; faces ( (0 4 7 3) ); }\n"
        "    outlet    { type patch; faces ( (1 2 6 5) ); }\n"
        "    wallLo    { type wall;  faces ( (0 1 5 4) ); }\n"
        "    wallHi    { type wall;  faces ( (3 7 6 2) ); }\n"
        "    frontBack { type empty; faces ( (0 3 2 1) (4 5 6 7) ); }\n"
        ");\n\nmergePatchPairs ();\n"
        % (L, L, B_GAP, B_GAP, WIDTH, L, WIDTH, L, B_GAP, WIDTH, B_GAP, WIDTH, nx, ny))


def field_U():
    return header("volVectorField", "U", "0") + (
        "\ndimensions      [0 1 -1 0 0 0 0];\ninternalField   uniform (%.10g 0 0);\n"
        "boundaryField\n{\n"
        "    inlet     { type fixedValue; value uniform (%.10g 0 0); }\n"
        "    outlet    { type zeroGradient; }\n"
        "    wallLo    { type noSlip; }\n    wallHi    { type noSlip; }\n"
        "    frontBack { type empty; }\n}\n" % (U0, U0))


def field_p_rgh():
    return header("volScalarField", "p_rgh", "0") + (
        "\ndimensions      [0 2 -2 0 0 0 0];\ninternalField   uniform 0;\n"
        "boundaryField\n{\n"
        "    inlet     { type zeroGradient; }\n"
        "    outlet    { type fixedValue; value uniform 0; }\n"
        "    wallLo    { type zeroGradient; }\n    wallHi    { type zeroGradient; }\n"
        "    frontBack { type empty; }\n}\n")


def field_T(wall):
    if wall == "fixedTemperature":
        wb = "{ type fixedValue; value uniform %.10g; }" % T_WALL
    else:
        wb = "{ type fixedGradient; gradient uniform %.10g; }" % DTDN
    return header("volScalarField", "T", "0") + (
        "\ndimensions      [0 0 0 1 0 0 0];\ninternalField   uniform %.10g;\n"
        "boundaryField\n{\n"
        "    inlet     { type fixedValue; value uniform %.10g; }\n"
        "    outlet    { type zeroGradient; }\n"
        "    wallLo    %s\n    wallHi    %s\n"
        "    frontBack { type empty; }\n}\n" % (T_IN, T_IN, wb, wb))


def field_alphat():
    return header("volScalarField", "alphat", "0") + (
        "\ndimensions      [0 2 -1 0 0 0 0];\ninternalField   uniform 0;\n"
        "boundaryField\n{\n"
        "    inlet     { type calculated; value uniform 0; }\n"
        "    outlet    { type calculated; value uniform 0; }\n"
        "    wallLo    { type fixedValue; value uniform 0; }\n"
        "    wallHi    { type fixedValue; value uniform 0; }\n"
        "    frontBack { type empty; }\n}\n")


def transport():
    return header("dictionary", "transportProperties", "constant") + (
        "\ntransportModel  Newtonian;\nnu              %.10g;\nbeta            0;\n"
        "TRef            %.10g;\nPr              %.10g;\nPrt             0.85;\n" % (NU, T_IN, PR))


def turbulence():
    # ESI OpenFOAM v2606 reads constant/turbulenceProperties and dies at
    # "Creating turbulence model" without it, laminar or not (build_t1c.py:203).
    return header("dictionary", "turbulenceProperties", "constant") + "\nsimulationType  laminar;\n"


def gravity():
    return header("uniformDimensionedVectorField", "g", "constant") + (
        "\ndimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 0);\n")


def control_dict():
    return header("dictionary", "controlDict", "system") + (
        "\napplication     buoyantBoussinesqSimpleFoam;\nstartFrom       startTime;\n"
        "startTime       0;\nstopAt          endTime;\nendTime         %d;\ndeltaT          1;\n"
        "writeControl    timeStep;\nwriteInterval   %d;\npurgeWrite      0;\nwriteFormat     ascii;\n"
        "writePrecision  16;\nwriteCompression off;\ntimeFormat      general;\ntimePrecision   6;\n"
        "runTimeModifiable false;\n" % (END_TIME, WRITE_INTERVAL))


def fv_schemes():
    return header("dictionary", "fvSchemes", "system") + (
        "\nddtSchemes      { default steadyState; }\n"
        "gradSchemes     { default Gauss linear; }\n"
        "divSchemes\n{\n    default none;\n"
        "    div(phi,U)      bounded Gauss linearUpwind grad(U);\n"
        "    div(phi,T)      bounded Gauss linearUpwind grad(T);\n"
        "    div(phi,K)      bounded Gauss linearUpwind grad(K);\n"
        # THE COMPRESSIBLE SPELLING div(((rho*nuEff)*dev2(T(grad(U))))) IS NOT WRITTEN
        # HERE.  It is the T4 provenance defect (scripts/check_case_provenance.py),
        # and check_case_provenance.py refused this case template until it was
        # removed -- driven, not assumed.
        "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n"
        "laplacianSchemes { default Gauss linear corrected; }\n"
        "interpolationSchemes { default linear; }\n"
        "snGradSchemes   { default corrected; }\n")


def fv_solution():
    return header("dictionary", "fvSolution", "system") + (
        "\nsolvers\n{\n"
        "    p_rgh\n    {\n        solver          PCG;\n        preconditioner  DIC;\n"
        "        tolerance       1e-12;\n        relTol          0.001;\n    }\n"
        "    \"(U|T)\"\n    {\n        solver          PBiCGStab;\n        preconditioner  DILU;\n"
        "        tolerance       1e-12;\n        relTol          0.01;\n    }\n}\n"
        "SIMPLE\n{\n    nNonOrthogonalCorrectors 0;\n    pRefCell        0;\n    pRefValue       0;\n"
        # THE ONE SUBSTANTIVE DELTA FROM build_t19.py:211, WHICH WROTE
        #     "    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }\n"
        # HERE.  It is deleted, not relaxed and not made configurable: an
        # absolute residual floor is DELIBERATELY NOT this rung's gate
        # (T19_PREREGISTRATION.md section 3, carried over verbatim), and with the
        # block present the solver stopped at 828/541 iterations against the
        # registered endTime 30000, taking rule-4 completion and C_PLATEAU down
        # with it.  Removing it conforms the CASE to the registration rather than
        # amending the registration to the case (DEAD_LEVER_AUDIT.md 21.2).
        "}\n"
        "relaxationFactors\n{\n    fields { p_rgh 0.3; }\n    equations { U 0.7; T 0.7; }\n}\n")


def write_case(root, name):
    spec = CASES[name]
    nx, ny = spec["nx"], spec["ny"]
    case = os.path.join(root, name)
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)

    def w(rel, txt):
        open(os.path.join(case, rel), "w").write(txt)
    w("system/blockMeshDict", block_mesh(nx, ny))
    w("system/controlDict", control_dict())
    w("system/fvSchemes", fv_schemes())
    w("system/fvSolution", fv_solution())
    w("constant/transportProperties", transport())
    w("constant/turbulenceProperties", turbulence())
    w("constant/g", gravity())
    w("0.orig/U", field_U())
    w("0.orig/p_rgh", field_p_rgh())
    w("0.orig/T", field_T(spec["wall"]))
    w("0.orig/alphat", field_alphat())
    w("CASE.txt",
      "case=%s\nrung=T19\nlevel=%s\nwall_condition=%s\nnx=%d\nny=%d\ncells=%d\n"
      "dx=%.17g\ndy=%.17g\nb_gap=%.17g\nDh=%.17g\nL=%.17g\nx_station=%.17g\n"
      "nu=%.17g\nPr=%.17g\nRe=%.17g\nU0=%.17g\nT_in=%.17g\nT_wall=%.17g\ndTdn_wall=%.17g\n"
      "endTime=%d\ndeltaT=1\nwriteInterval=%d\nsolver=buoyantBoussinesqSimpleFoam\n"
      "turbulence=laminar\nbeta=0\nranks=1\ndecomposition=serial_1_rank_no_decomposition\n"
      "reference_fRe=96\nreference_Nu_q=8.2352942009\nreference_Nu_Ts=7.5407008741\n"
      "x_plus=%.17g\n"
      % (name, spec["level"], spec["wall"], nx, ny, nx * ny, L / nx, B_GAP / ny, B_GAP, DH, L, X_S,
         NU, PR, RE, U0, T_IN, T_WALL, DTDN, END_TIME, WRITE_INTERVAL, X_S / (DH * RE * PR)))
    return case, nx, ny


def mesh(case):
    env = "set +u; . %s >/dev/null 2>&1; " % FOAM_BASHRC
    t0 = time.time()
    bm = subprocess.run(["bash", "-c", env + "blockMesh -case '%s'" % case], capture_output=True, text=True)
    open(os.path.join(case, "log.blockMesh"), "w").write(bm.stdout + bm.stderr)
    t1 = time.time()
    cm = subprocess.run(["bash", "-c", env + "checkMesh -case '%s'" % case], capture_output=True, text=True)
    open(os.path.join(case, "log.checkMesh.build"), "w").write(cm.stdout + cm.stderr)
    t2 = time.time()
    body = cm.stdout + cm.stderr
    lines = [l.strip() for l in body.splitlines()
             if re.search(r"^\s*cells:|Max aspect ratio|non-orthogonality|Max skewness|Mesh OK|Failed|Total volume", l)]
    open(os.path.join(case, "BUILD.txt"), "w").write(
        "case            %s\ndate            %s\nblockMesh_rc    %d   wall %.3f s\ncheckMesh_rc    %d   wall %.3f s\n%s\n"
        % (os.path.basename(case), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), bm.returncode,
           t1 - t0, cm.returncode, t2 - t1, "\n".join("checkMesh       " + l for l in lines)))
    if bm.returncode != 0:
        refuse("blockMesh failed rc=%d in %s" % (bm.returncode, case))
    if cm.returncode != 0 or "Mesh OK" not in body:
        refuse("checkMesh did not report Mesh OK in %s" % case)


def selftest():
    fails = []
    check_levels()
    print("  [ok ] ladder is r = 2 in both directions and the station lies on a cell face on every level")
    fired = False
    try:
        check_levels({"c": (120, 20), "m": (240, 20), "f": (480, 40)})
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] a level pair sharing ny -> REFUSE" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("levels")
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="t19build_")
    try:
        case, nx, ny = write_case(tmp, "P_q_c")
        txt = open(os.path.join(case, "0.orig", "T")).read()
        ok = ("fixedGradient" in txt and "gradient uniform 500" in txt and txt.count("fixedGradient") == 2
              and not os.path.exists(os.path.join(case, "0")))
        print("  [%s] the q arm writes fixedGradient on BOTH walls; no 0/ written" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("q-arm")
        case2, _, _ = write_case(tmp, "P_Ts_c")
        txt2 = open(os.path.join(case2, "0.orig", "T")).read()
        ok = txt2.count("fixedValue; value uniform 400") == 2
        print("  [%s] the Ts arm writes fixedValue 400 K on BOTH walls" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("ts-arm")
        # ---- T19b's OWN limb: the repair is READ BACK OFF DISK, and the
        # detector is shown able to fail on the same invocation.  A limb that
        # cannot fail is the defect T19b exists to repair.
        fvs = open(os.path.join(case, "system", "fvSolution")).read()
        det_clean = ("residualControl" in fvs)
        det_planted = ("residualControl" in fvs.replace(
            "    pRefValue       0;\n", "    pRefValue       0;\n"
            "    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }\n"))
        ok = (not det_clean) and det_planted and ("SIMPLE" in fvs)
        print("  [%s] the built fvSolution emits NO residualControl block (detector on the clean "
              "file: %s; the SAME detector on a copy with build_t19.py:211's line planted back in: "
              "%s -- so the green is not tautological)"
              % ("ok " if ok else "FAIL", "absent" if not det_clean else "PRESENT",
                 "PRESENT" if det_planted else "absent"))
        if not ok:
            fails.append("no-residualControl")
        got = set(os.listdir(os.path.join(case, "0.orig")))
        ok = got == {"U", "p_rgh", "T", "alphat"}
        print("  [%s] 0.orig holds exactly {U, p_rgh, T, alphat} -- the LAMINAR field set, with no "
              "nut/k/omega, because the registered closure is `simulationType laminar` (got %s)"
              % ("ok " if ok else "FAIL", sorted(got)))
        if not ok:
            fails.append("fields")
        prov = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..",
                            "scripts", "check_case_provenance.py")
        if os.path.isfile(prov):
            r = subprocess.run([sys.executable, prov, "--case", case], capture_output=True, text=True)
            ok = (r.returncode == 0)
            print("  [%s] check_case_provenance.py on the built q case: rc=%d" % ("ok " if ok else "FAIL", r.returncode))
            if not ok:
                fails.append("provenance")
                print(r.stdout[-800:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    import ast
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--case", action="append", choices=sorted(CASES))
    ap.add_argument("--check-levels", action="store_true")
    ap.add_argument("--no-mesh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.check_levels:
        print(check_levels())
        print("  Re=%g U0=%.10g m/s Dh=%g L=%g x_s=%g x+=%.6f" % (RE, U0, DH, L, X_S, X_S / (DH * RE * PR)))
        sys.exit(0)
    if not a.root:
        refuse("--root is required")
    check_levels()
    for nm in (a.case or sorted(CASES)):
        case, nx, ny = write_case(a.root, nm)
        if not a.no_mesh:
            mesh(case)
        print("  built %s nx=%d ny=%d cells=%d" % (nm, nx, ny, nx * ny))
