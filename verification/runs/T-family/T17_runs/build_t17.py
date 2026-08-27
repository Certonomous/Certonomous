#!/usr/bin/env python3
"""Build T17's registered cases: axisymmetric transient conduction in a finite
cylinder (T11d), on an OpenFOAM WEDGE mesh.

SOLID ONLY -- there is no fluid in this rung.  A quarter section of a solid
cylinder of radius R and half-length H (R = H): the axis at r = 0, a symmetry
plane at z = 0 (zeroGradient), convective Robin surfaces at r = R and z = H,
uniform initial theta = 1, T_inf = 0 so theta = T directly.

MESH.  The proven family wedge form (build_t1c.py:88, the T1c laminar pipe),
with the axial coordinate along x and the radial coordinate in the wedge plane:
a single block `hex (0 1 2 3 0 1 5 4) (nz nr 1)`, front/back of type `wedge`,
an empty `axis` patch with no faces.  T1c used WEDGE_DEG = 5.0; THIS RUNG USES
1.0 DEGREE, and the reason is registered rather than left implicit: the planar
faces of a wedge make the discrete radial operator larger than the true
axisymmetric one by sec^2(h) where h is the HALF angle (derivation in
T17_PREREGISTRATION.md section 2b), a bias that does NOT vanish under mesh
refinement.  At 5 degrees that is 1.9e-03; at 1 degree it is 7.6e-05, small
enough to sit inside a band that still discriminates the ladder.

THE valueFraction IS MESH-DEPENDENT (L-341) AND DIFFERS BETWEEN THE TWO ROBIN
FACES, because the cell-centre-to-face distance differs:

  * axial face (z = H): the mesh is uniform in z, so delta = dz/2 and
        f_z = Bi / (Bi + 2N)                      (the T11/T14 form)
  * radial face (r = R): the outermost cell's centroid sits at the ANNULAR
    SECTOR centroid r_c = (2/3)(r2^3 - r1^3)/(r2^2 - r1^2), NOT at (N-1/2)dr,
    and the face-normal distance carries the wedge factor cos(h):
        delta_r = (R - r_c(N-1)) cos(h),  Bi_d = Bi delta_r / R,
        f_r = Bi_d / (1 + Bi_d)
    which tends to the axial form as N grows but is NOT equal to it.

`--check-levels` REFUSES (exit 2) unless all three levels DIFFER in both
fractions and each equals the derived value.

Cases: T17_CY_c / T17_CY_m / T17_CY_f (N = 50 / 100 / 200 in BOTH directions,
r = 2 exactly) and T17_CY_f_CT, the temporal-bias control (fine mesh, deltaT
halved; REPORTED, never gated).  blockMesh and checkMesh run at build so the
launcher can refuse a case with no mesh, and so that checkMesh's own Total /
Min / Max volume can be checked against this file's analytic volume model
(control C_GEOM).  NO assert (L-332).

usage: build_t17.py --root DIR [--level c|m|f|f_CT ...] [--no-mesh] | --check-levels | --selftest
"""
import argparse
import math
import os
import re
import subprocess
import sys
import time

R = 0.01          # m, cylinder radius
H = 0.01          # m, half-length (R = H, so Bi and Fo are the same in both directions)
ALPHA = 1.0e-5    # m2/s
BI = 1.0
T_INIT, T_INF = 1.0, 0.0
END_T = 2.0       # s -> Fo = 0.20
DELTA_T = 1.0e-4  # s, FIXED on c/m/f (spatial-only refinement; temporal error common-mode)
WEDGE_DEG = 1.0   # TOTAL wedge angle; see the module docstring

LEVELS = {"c": 50, "m": 100, "f": 200, "f_CT": 200}
DT_OF = {"c": DELTA_T, "m": DELTA_T, "f": DELTA_T, "f_CT": DELTA_T / 2.0}
CASE_OF = {lv: "T17_CY_%s" % lv for lv in LEVELS}
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------- geometry
def r_centroid(i, N, Rout=R):
    """The exact volume centroid radius of radial cell i on a uniform radial mesh.
    For the planar-faced wedge the cell cross-section is a trapezoid whose centroid
    is at exactly the annular-sector centroid, so this is exact, not an
    approximation (T17_PREREGISTRATION.md section 2a)."""
    dr = Rout / N
    r1, r2 = i * dr, (i + 1) * dr
    return (2.0 / 3.0) * (r2 ** 3 - r1 ** 3) / (r2 ** 2 - r1 ** 2)


def cell_weight(i, N, Rout=R):
    """Cell volume up to the constant sin(h)cos(h)dz: (r2^2 - r1^2)."""
    dr = Rout / N
    return ((i + 1) * dr) ** 2 - (i * dr) ** 2


def value_fraction_axial(N, Bi=BI):
    return Bi / (Bi + 2.0 * N)


def value_fraction_radial(N, Bi=BI, deg=WEDGE_DEG):
    h = math.radians(deg / 2.0)
    delta = (R - r_centroid(N - 1, N)) * math.cos(h)
    Bid = Bi * delta / R
    return Bid / (1.0 + Bid)


def analytic_volumes(N, Nz, deg=WEDGE_DEG):
    """(total, min, max) cell volume of the wedge mesh, from the planar-face
    geometry -- checked against checkMesh's own three numbers (C_GEOM)."""
    h = math.radians(deg / 2.0)
    k = math.sin(h) * math.cos(h) * (H / Nz)
    vols = [k * cell_weight(i, N) for i in range(N)]
    return sum(vols) * Nz, min(vols), max(vols)


def check_levels(levels=None):
    levels = levels or {k: LEVELS[k] for k in ("c", "m", "f")}
    fa = {lv: value_fraction_axial(N) for lv, N in levels.items()}
    fr = {lv: value_fraction_radial(N) for lv, N in levels.items()}
    for name, fs in (("axial", fa), ("radial", fr)):
        if len(set("%.12e" % v for v in fs.values())) != len(fs):
            refuse("the %s valueFraction is IDENTICAL on two or more levels: %r -- a constant "
                   "here makes the triple measure boundary-condition error (L-341)" % (name, fs))
    for lv, N in levels.items():
        if abs(fa[lv] - BI / (BI + 2.0 * N)) > 1e-15:
            refuse("axial valueFraction on level %s is %.17g, not the derived value" % (lv, fa[lv]))
        if fr[lv] >= fa[lv]:
            refuse("radial valueFraction %.17g on level %s is not BELOW the axial %.17g -- the "
                   "outermost sector centroid lies inside (N-1/2)dr, so delta_r < dz/2 must hold"
                   % (fr[lv], lv, fa[lv]))
    return fa, fr


def head(cls, obj, loc=None):
    l = ('    location    "%s";\n' % loc) if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n" % (cls, l, obj))


def write_case(root, level):
    N = LEVELS[level]
    dt = DT_OF[level]
    fa, fr = value_fraction_axial(N), value_fraction_radial(N)
    h = math.radians(WEDGE_DEG / 2.0)
    y, z = R * math.cos(h), R * math.sin(h)
    case = os.path.join(root, CASE_OF[level])
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(
        head("dictionary", "blockMeshDict", "system") +
        "scale 1;\n\nvertices\n(\n"
        "    (0          0            0)\n"
        "    (%.10f      0            0)\n"
        "    (%.10f      %.12f      %.12f)\n"
        "    (0          %.12f      %.12f)\n"
        "    (0          %.12f      %.12f)\n"
        "    (%.10f      %.12f      %.12f)\n"
        ");\n\nblocks\n(\n    hex (0 1 2 3 0 1 5 4) (%d %d 1) simpleGrading (1 1 1)\n);\n\n"
        "edges ();\n\nboundary\n(\n"
        "    symZ  { type patch; faces ( (0 3 4 0) ); }\n"
        "    faceZ { type patch; faces ( (1 2 5 1) ); }\n"
        "    faceR { type patch; faces ( (3 2 5 4) ); }\n"
        "    front { type wedge; faces ( (0 1 5 4) ); }\n"
        "    back  { type wedge; faces ( (0 1 2 3) ); }\n"
        "    axis  { type empty; faces ( ); }\n"
        ");\n\nmergePatchPairs ();\n"
        % (H, H, y, -z, y, -z, y, z, H, y, z, N, N))
    open(os.path.join(case, "system", "controlDict"), "w").write(
        head("dictionary", "controlDict", "system") +
        "application     laplacianFoam;\nstartFrom       startTime;\n"
        "startTime       0;\nstopAt          endTime;\nendTime         %g;\n"
        "deltaT          %g;\nwriteControl    runTime;\nwriteInterval   %g;\n"
        "purgeWrite      0;\nwriteFormat     ascii;\nwritePrecision  14;\n"
        "writeCompression off;\ntimeFormat      general;\ntimePrecision   6;\n"
        "runTimeModifiable false;\n" % (END_T, dt, END_T / 2.0))
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

    def robin(f):
        return ("    {\n        type            mixed;\n        refValue        uniform %g;\n"
                "        refGradient     uniform 0;\n        valueFraction   uniform %.17g;\n    }\n"
                % (T_INF, f))
    open(os.path.join(case, "0.orig", "T"), "w").write(
        head("volScalarField", "T", "0") +
        "dimensions      [0 0 0 1 0 0 0];\n\ninternalField   uniform %g;\n\n"
        "boundaryField\n{\n    symZ  { type zeroGradient; }\n"
        "    faceZ\n%s    faceR\n%s"
        "    front { type wedge; }\n    back  { type wedge; }\n}\n" % (T_INIT, robin(fa), robin(fr)))
    vt, vmin, vmax = analytic_volumes(N, N)
    open(os.path.join(case, "CASE.txt"), "w").write(
        "case=%s\nlevel=%s\nN=%d\ncells=%d\ndr=%.17g\ndz=%.17g\n"
        "valueFraction_axial=%.17g\nvalueFraction_radial=%.17g\nwedge_deg=%.17g\n"
        "Bi=%g\nR=%g\nHhalf=%g\nalpha=%g\nendTime=%g\ndeltaT=%g\nFo_end=%.17g\n"
        "analytic_total_volume=%.17g\nanalytic_min_volume=%.17g\nanalytic_max_volume=%.17g\n"
        "solver=laplacianFoam\nranks=1\ndecomposition=serial_1_rank_no_decomposition\n"
        % (CASE_OF[level], level, N, N * N, R / N, H / N, fa, fr, WEDGE_DEG, BI, R, H,
           ALPHA, END_T, dt, ALPHA * END_T / (R * R), vt, vmin, vmax))
    return case, N, fa, fr


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
    return bm.returncode, cm.returncode


def selftest():
    fails = []
    fa, fr = check_levels()
    print("  [ok ] valueFraction guard passes: axial %s ; radial %s"
          % (", ".join("%s=%.6e" % (k, fa[k]) for k in ("c", "m", "f")),
             ", ".join("%s=%.6e" % (k, fr[k]) for k in ("c", "m", "f"))))
    fired = False
    try:
        check_levels({"c": 100, "m": 100, "f": 100})
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] identical N on all levels -> REFUSE (L-341)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("levels")
    # the geometry identity: the volume-weighted mean of r_c is exactly (2/3)R for
    # ANY N.  The naive centroid (i+1/2)dr fails it by 1/(6N^2).
    for N in (7, 50, 200):
        num = sum(cell_weight(i, N) * r_centroid(i, N) for i in range(N))
        den = sum(cell_weight(i, N) for i in range(N))
        ok = abs(num / den - (2.0 / 3.0) * R) < 1e-17
        if not ok:
            fails.append("geom-identity-%d" % N)
    print("  [%s] volume-weighted mean of the sector centroid == (2/3)R exactly at N=7,50,200"
          % ("ok " if not [f for f in fails if f.startswith("geom-identity")] else "FAIL"))
    N = 50
    num = sum(cell_weight(i, N) * ((i + 0.5) * R / N) for i in range(N))
    den = sum(cell_weight(i, N) for i in range(N))
    bad = abs(num / den - (2.0 / 3.0) * R) / R
    ok = bad > 1e-6
    print("  [%s] the NAIVE centroid (i+1/2)dr FAILS that identity by %.2e relative at N=50 "
          "(the control discriminates)" % ("ok " if ok else "FAIL", bad))
    if not ok:
        fails.append("geom-discriminates")
    import tempfile, shutil
    tmp = tempfile.mkdtemp(prefix="t17build_")
    try:
        case, N, fa1, fr1 = write_case(tmp, "c")
        txt = open(os.path.join(case, "0.orig", "T")).read()
        vf = [float(v) for v in re.findall(r"valueFraction\s+uniform\s+([0-9.eE+-]+)", txt)]
        ok = (len(vf) == 2 and abs(vf[0] - fa1) < 1e-15 and abs(vf[1] - fr1) < 1e-15
              and vf[0] != vf[1] and not os.path.exists(os.path.join(case, "0")))
        print("  [%s] 0.orig/T carries the axial and radial valueFractions SEPARATELY (%.8e, %.8e); no 0/ written"
              % ("ok " if ok else "FAIL", vf[0] if vf else -1, vf[1] if len(vf) > 1 else -1))
        if not ok:
            fails.append("write")
        ok = txt.count("type wedge") == 2 and txt.count("zeroGradient") == 1
        print("  [%s] two wedge patches and one symmetry plane in 0.orig/T" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("patches")
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
        fa, fr = check_levels()
        for lv in ("c", "m", "f"):
            print("  level %s N=%d f_axial=%.10e f_radial=%.10e" % (lv, LEVELS[lv], fa[lv], fr[lv]))
        sys.exit(0)
    if not a.root:
        refuse("--root is required")
    check_levels()
    for lv in (a.level or ["c", "m", "f", "f_CT"]):
        case, N, fa1, fr1 = write_case(a.root, lv)
        if not a.no_mesh:
            mesh(case)
        print("  built %s N=%d cells=%d f_axial=%.8e f_radial=%.8e deltaT=%g"
              % (os.path.basename(case), N, N * N, fa1, fr1, DT_OF[lv]))
