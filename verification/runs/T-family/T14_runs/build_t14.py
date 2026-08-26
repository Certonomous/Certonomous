#!/usr/bin/env python3
"""Build T14's registered cases: 2-D transient conduction in a square (T11b).

SOLID ONLY -- there is no fluid in this rung.  Quarter of a square of half-side
L, symmetry planes at x = 0 and y = 0 (zeroGradient), convective Robin faces at
x = L and y = L, uniform initial theta = 1, T_inf = 0 so theta = T directly.

THE valueFraction IS MESH-DEPENDENT (L-341) AND IS COMPUTED PER LEVEL:
    f = Bi / (Bi + 2N)        (T11_PREREGISTRATION.md section 5)
`--check-levels` REFUSES (exit 2) unless all three levels DIFFER and each equals
the derived value.

Cases: T14_SQ_c / T14_SQ_m / T14_SQ_f (N = 50 / 100 / 200 across the half-side,
r = 2 exactly) and T14_SQ_f_CT, the temporal-bias control (fine mesh, deltaT
halved; REPORTED, never gated).  blockMesh and checkMesh run at build so the
launcher can refuse a case with no mesh.  NO assert (L-332).

usage: build_t14.py --root DIR [--level c|m|f|f_CT ...] [--no-mesh] | --check-levels | --selftest
"""
import argparse
import os
import re
import subprocess
import sys
import time

L = 0.01          # m, half-side
ALPHA = 1.0e-5    # m2/s
BI = 1.0
T_INIT, T_INF = 1.0, 0.0
END_T = 2.0       # s -> Fo = 0.20
DELTA_T = 1.0e-4  # s, FIXED on c/m/f (spatial-only refinement; temporal error common-mode)
DEPTH = 0.001

LEVELS = {"c": 50, "m": 100, "f": 200, "f_CT": 200}
DT_OF = {"c": DELTA_T, "m": DELTA_T, "f": DELTA_T, "f_CT": DELTA_T / 2.0}
CASE_OF = {lv: "T14_SQ_%s" % lv for lv in LEVELS}
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def value_fraction(N, Bi=BI):
    return Bi / (Bi + 2.0 * N)


def check_levels(levels=None):
    levels = levels or {k: LEVELS[k] for k in ("c", "m", "f")}
    fs = {lv: value_fraction(N) for lv, N in levels.items()}
    if len(set("%.12e" % v for v in fs.values())) != len(fs):
        refuse("valueFraction is IDENTICAL on two or more levels: %r -- a constant "
               "here makes the triple measure boundary-condition error (L-341)" % fs)
    for lv, N in levels.items():
        want = BI / (BI + 2.0 * N)
        if abs(fs[lv] - want) > 1e-15:
            refuse("valueFraction on level %s is %.17g, not the derived %.17g" % (lv, fs[lv], want))
    return fs


def head(cls, obj, loc=None):
    l = ('    location    "%s";\n' % loc) if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n" % (cls, l, obj))


def write_case(root, level):
    N = LEVELS[level]
    dt = DT_OF[level]
    f = value_fraction(N)
    case = os.path.join(root, CASE_OF[level])
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)
    w = DEPTH
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(
        head("dictionary", "blockMeshDict", "system") +
        "scale 1;\nvertices\n(\n"
        "    (0 0 0) (%g 0 0) (%g %g 0) (0 %g 0)\n"
        "    (0 0 %g) (%g 0 %g) (%g %g %g) (0 %g %g)\n);\n\n"
        "blocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d 1) simpleGrading (1 1 1)\n);\n\n"
        "edges ();\n\nboundary\n(\n"
        "    symX  { type patch; faces ( (0 4 7 3) ); }\n"
        "    faceX { type patch; faces ( (1 2 6 5) ); }\n"
        "    symY  { type patch; faces ( (0 1 5 4) ); }\n"
        "    faceY { type patch; faces ( (3 7 6 2) ); }\n"
        "    frontBack { type empty; faces ( (0 3 2 1) (4 5 6 7) ); }\n"
        ");\n\nmergePatchPairs ();\n"
        % (L, L, L, L, w, L, w, L, L, w, L, w, N, N))
    open(os.path.join(case, "system", "controlDict"), "w").write(
        head("dictionary", "controlDict", "system") +
        "application     laplacianFoam;\nstartFrom       startTime;\n"
        "startTime       0;\nstopAt          endTime;\nendTime         %g;\n"
        "deltaT          %g;\nwriteControl    runTime;\nwriteInterval   %g;\n"
        "purgeWrite      0;\nwriteFormat     ascii;\nwritePrecision  14;\n"
        "writeCompression off;\ntimeFormat      general;\ntimePrecision   6;\n"
        "runTimeModifiable false;\n" % (END_T, dt, END_T / 4.0))
    open(os.path.join(case, "system", "fvSchemes"), "w").write(
        head("dictionary", "fvSchemes", "system") +
        "ddtSchemes      { default Euler; }\n"
        "gradSchemes     { default Gauss linear; }\n"
        "divSchemes      { default none; }\n"
        "laplacianSchemes { default Gauss linear corrected; }\n"
        "interpolationSchemes { default linear; }\n"
        "snGradSchemes   { default corrected; }\n")
    open(os.path.join(case, "system", "fvSolution"), "w").write(
        head("dictionary", "fvSolution", "system") +
        "solvers\n{\n    T\n    {\n        solver          PCG;\n"
        "        preconditioner  DIC;\n        tolerance       1e-12;\n"
        "        relTol          0;\n    }\n}\n\n"
        "SIMPLE { nNonOrthogonalCorrectors 0; }\n")
    open(os.path.join(case, "constant", "transportProperties"), "w").write(
        head("dictionary", "transportProperties", "constant") + "DT              %g;\n" % ALPHA)
    robin = ("    {\n        type            mixed;\n        refValue        uniform %g;\n"
             "        refGradient     uniform 0;\n        valueFraction   uniform %.17g;\n    }\n" % (T_INF, f))
    open(os.path.join(case, "0.orig", "T"), "w").write(
        head("volScalarField", "T", "0") +
        "dimensions      [0 0 0 1 0 0 0];\n\ninternalField   uniform %g;\n\n"
        "boundaryField\n{\n    symX  { type zeroGradient; }\n    symY  { type zeroGradient; }\n"
        "    faceX\n%s    faceY\n%s    frontBack { type empty; }\n}\n" % (T_INIT, robin, robin))
    open(os.path.join(case, "CASE.txt"), "w").write(
        "case=%s\nlevel=%s\nN=%d\ncells=%d\ndx=%.17g\nvalueFraction=%.17g\nBi=%g\nL=%g\n"
        "alpha=%g\nendTime=%g\ndeltaT=%g\nFo_end=%.17g\nsolver=laplacianFoam\nranks=1\n"
        % (CASE_OF[level], level, N, N * N, L / N, f, BI, L, ALPHA, END_T, dt, ALPHA * END_T / (L * L)))
    return case, N, f


def mesh(case):
    env = "set +u; . %s >/dev/null 2>&1; " % FOAM_BASHRC
    t0 = time.time()
    bm = subprocess.run(["bash", "-c", env + "blockMesh -case '%s'" % case], capture_output=True, text=True)
    open(os.path.join(case, "log.blockMesh"), "w").write(bm.stdout + bm.stderr)
    t1 = time.time()
    cm = subprocess.run(["bash", "-c", env + "checkMesh -case '%s'" % case], capture_output=True, text=True)
    open(os.path.join(case, "log.checkMesh.build"), "w").write(cm.stdout + cm.stderr)
    t2 = time.time()
    lines = [l.strip() for l in (cm.stdout + cm.stderr).splitlines()
             if re.search(r"^\s*cells:|Max aspect ratio|non-orthogonality|Max skewness|Mesh OK|Failed", l)]
    open(os.path.join(case, "BUILD.txt"), "w").write(
        "case            %s\ndate            %s\nblockMesh_rc    %d   wall %.3f s\ncheckMesh_rc    %d   wall %.3f s\n%s\n"
        % (os.path.basename(case), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), bm.returncode,
           t1 - t0, cm.returncode, t2 - t1, "\n".join("checkMesh       " + l for l in lines)))
    if bm.returncode != 0:
        refuse("blockMesh failed rc=%d in %s" % (bm.returncode, case))
    if cm.returncode != 0 or "Mesh OK" not in (cm.stdout + cm.stderr):
        refuse("checkMesh did not report Mesh OK in %s" % case)
    return bm.returncode, cm.returncode


def selftest():
    fails = []
    check_levels()
    print("  [ok ] valueFraction guard passes on the registered levels: %s"
          % ", ".join("%s=%.6e" % (k, value_fraction(LEVELS[k])) for k in ("c", "m", "f")))
    fired = False
    try:
        check_levels({"c": 100, "m": 100, "f": 100})
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] identical N on all levels -> REFUSE (L-341)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("levels")
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="t14build_")
    try:
        case, N, f = write_case(tmp, "c")
        txt = open(os.path.join(case, "0.orig", "T")).read()
        vf = re.findall(r"valueFraction\s+uniform\s+([0-9.eE+-]+)", txt)
        ok = (len(vf) == 2 and all(abs(float(v) - BI / (BI + 2 * N)) < 1e-15 for v in vf)
              and not os.path.exists(os.path.join(case, "0")))
        print("  [%s] written 0.orig/T carries the derived valueFraction on BOTH Robin faces; no 0/ written" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("write")
        bmd = open(os.path.join(case, "system", "blockMeshDict")).read()
        ok = ("(%d %d 1)" % (N, N)) in bmd
        print("  [%s] blockMeshDict is N x N x 1 = %d x %d" % ("ok " if ok else "FAIL", N, N))
        if not ok:
            fails.append("mesh-dims")
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
    ap.add_argument("--level", action="append", choices=list(LEVELS))
    ap.add_argument("--check-levels", action="store_true")
    ap.add_argument("--no-mesh", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.check_levels:
        fs = check_levels()
        for lv in ("c", "m", "f"):
            print("  level %s N=%d f=%.8e" % (lv, LEVELS[lv], fs[lv]))
        sys.exit(0)
    if not a.root:
        refuse("--root is required")
    check_levels()
    for lv in (a.level or ["c", "m", "f", "f_CT"]):
        case, N, f = write_case(a.root, lv)
        if not a.no_mesh:
            mesh(case)
        print("  built %s N=%d cells=%d valueFraction=%.8e deltaT=%g" % (os.path.basename(case), N, N * N, f, DT_OF[lv]))
