#!/usr/bin/env python3
"""Build T11's three registered cases: 1-D transient conduction in a plane wall.

SOLID ONLY.  There is no fluid in this rung.  It is the TRANSIENT HALF of the
conjugate problem, not conjugate heat transfer.

    x = 0   insulated / symmetry plane   (zeroGradient)
    x = L   convective, Robin:  -k dT/dx = h (T - T_inf)

Non-dimensionalised so that theta = T directly: T_inf = 0, T_0 = 1.

THE valueFraction IS MESH-DEPENDENT AND IS COMPUTED PER LEVEL.  OpenFOAM's
`mixed` boundary condition forms
    T_face = f*refValue + (1-f)*(T_cell + refGrad/deltaCoeff)
and matching it to the Robin condition gives
    f = (h/k) / ((h/k) + deltaCoeff),   deltaCoeff = 1/(dx/2) = 2N/L
    => f = Bi / (Bi + 2N)
**f CONTAINS THE MESH SPACING.**  A hardcoded uniform f is correct on exactly
one level.  In a three-level Roache study a hardcoded f would give every level
a DIFFERENT EFFECTIVE BOUNDARY CONDITION while the dictionaries looked
identical, and the triple would measure boundary-condition error rather than
discretisation error -- converging cleanly to the wrong answer and reporting a
respectable observed order.  Measured before this rung was registered: at
N = 100/200/400 the correct values are 4.975e-03 / 2.494e-03 / 1.248e-03, and a
value of 0.3333 (a plausible guess) put the solution 18 % out while still
looking like a converged field.  This is L-341.

GUARD: `--check-levels` recomputes f for all three levels and REFUSES (exit 2)
unless all three DIFFER.  If somebody later replaces the formula with a
constant, that guard fires.
"""
import argparse
import math
import os
import sys

L      = 0.01        # m, wall half-thickness
ALPHA  = 1.0e-5      # m2/s, thermal diffusivity (laplacianFoam DT)
BI     = 1.0         # Biot number
T_INIT = 1.0         # theta(x,0) = 1
T_INF  = 0.0
END_T  = 2.0         # s  ->  Fo = alpha*t/L^2 = 0.20
DELTA_T = 1.0e-4     # s, FIXED ON EVERY LEVEL (see below)

LEVELS = {"c": 100, "m": 200, "f": 400}      # r21 = r32 = 2 exactly

EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def value_fraction(N, Bi=BI):
    """f = Bi / (Bi + 2N).  Derived above; NEVER a literal."""
    return Bi / (Bi + 2.0 * N)


def check_levels():
    fs = {lv: value_fraction(N) for lv, N in LEVELS.items()}
    vals = list(fs.values())
    if len(set("%.12e" % v for v in vals)) != len(vals):
        refuse("valueFraction is IDENTICAL on two or more levels: %r. It must "
               "vary with mesh spacing (f = Bi/(Bi+2N)); a constant here would "
               "make the Roache triple measure boundary-condition error instead "
               "of discretisation error (L-341)." % fs)
    for lv, N in LEVELS.items():
        want = BI / (BI + 2.0 * N)
        if abs(fs[lv] - want) > 1e-15 * max(want, 1.0):
            refuse("valueFraction on level %s is %.17g, not the derived "
                   "%.17g" % (lv, fs[lv], want))
    print("  valueFraction guard PASSES, all three differ:")
    for lv in ("c", "m", "f"):
        print("    level %s  N=%-4d dx=%.3e  deltaCoeff=%.1f  f=%.8e"
              % (lv, LEVELS[lv], L / LEVELS[lv], 2.0 * LEVELS[lv] / L, fs[lv]))
    return fs


def head(cls, obj, loc=None):
    l = ('    location    "%s";\n' % loc) if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n" % (cls, l, obj))


def build(root, level):
    N = LEVELS[level]
    f = value_fraction(N)
    case = os.path.join(root, "T11_PW_%s" % level)
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)

    w = 0.001
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(
        head("dictionary", "blockMeshDict", "system") +
        "scale 1;\nvertices\n(\n"
        "    (0 0 0) (%g 0 0) (%g %g 0) (0 %g 0)\n"
        "    (0 0 %g) (%g 0 %g) (%g %g %g) (0 %g %g)\n);\n\n"
        "blocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d 1 1) simpleGrading (1 1 1)\n);\n\n"
        "edges ();\n\nboundary\n(\n"
        "    centre  { type patch; faces ( (0 4 7 3) ); }\n"
        "    surface { type patch; faces ( (1 2 6 5) ); }\n"
        "    sides   { type empty; faces ( (0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7) ); }\n"
        ");\n\nmergePatchPairs ();\n"
        % (L, L, w, w, w, L, w, L, w, w, w, w, N))

    open(os.path.join(case, "system", "controlDict"), "w").write(
        head("dictionary", "controlDict", "system") +
        "application     laplacianFoam;\nstartFrom       startTime;\n"
        "startTime       0;\nstopAt          endTime;\nendTime         %g;\n"
        "deltaT          %g;\nwriteControl    runTime;\nwriteInterval   %g;\n"
        "purgeWrite      0;\nwriteFormat     ascii;\nwritePrecision  14;\n"
        "writeCompression off;\ntimeFormat      general;\ntimePrecision   6;\n"
        "runTimeModifiable false;\n" % (END_T, DELTA_T, END_T / 4.0))

    # ddt is Euler and deltaT is FIXED ACROSS LEVELS, deliberately: refining
    # only in space makes the temporal error COMMON-MODE, so the Roache triple
    # isolates spatial discretisation.  The temporal error does NOT cancel in
    # Richardson extrapolation -- it biases all three levels equally -- which is
    # why control C-T halves deltaT at the fine level and reports the movement.
    open(os.path.join(case, "system", "fvSchemes"), "w").write(
        head("dictionary", "fvSchemes", "system") +
        "ddtSchemes      { default Euler; }\n"
        "gradSchemes     { default Gauss linear; }\n"
        "divSchemes      { default none; }\n"
        "laplacianSchemes { default Gauss linear corrected; }\n"
        "interpolationSchemes { default linear; }\n"
        "snGradSchemes   { default corrected; }\n")

    # PCG/DIC, NOT PBiCGStab/DILU: laplacianFoam's matrix is SYMMETRIC and
    # OpenFOAM refuses DILU on it outright ("Unknown symmetric matrix
    # preconditioner type DILU").  Recorded because the refusal is the good
    # outcome -- an asymmetric preconditioner silently accepted on a symmetric
    # system would be far worse than one that stops.
    open(os.path.join(case, "system", "fvSolution"), "w").write(
        head("dictionary", "fvSolution", "system") +
        "solvers\n{\n    T\n    {\n        solver          PCG;\n"
        "        preconditioner  DIC;\n        tolerance       1e-12;\n"
        "        relTol          0;\n    }\n}\n\n"
        "SIMPLE { nNonOrthogonalCorrectors 0; }\n")

    open(os.path.join(case, "constant", "transportProperties"), "w").write(
        head("dictionary", "transportProperties", "constant") +
        "DT              %g;\n" % ALPHA)

    open(os.path.join(case, "0.orig", "T"), "w").write(
        head("volScalarField", "T", "0") +
        "dimensions      [0 0 0 1 0 0 0];\n\ninternalField   uniform %g;\n\n"
        "boundaryField\n{\n"
        "    centre  { type zeroGradient; }\n"
        "    surface\n    {\n        type            mixed;\n"
        "        refValue        uniform %g;\n        refGradient     uniform 0;\n"
        "        valueFraction   uniform %.17g;\n    }\n"
        "    sides   { type empty; }\n}\n" % (T_INIT, T_INF, f))

    open(os.path.join(case, "LEVEL.txt"), "w").write(
        "level=%s\nN=%d\ndx=%.17g\nvalueFraction=%.17g\nBi=%g\nL=%g\n"
        "alpha=%g\nendTime=%g\ndeltaT=%g\nFo_end=%.17g\n"
        % (level, N, L / N, f, BI, L, ALPHA, END_T, DELTA_T,
           ALPHA * END_T / (L * L)))
    print("  built T11_PW_%-2s N=%-4d cells=%-5d valueFraction=%.8e  Fo_end=%.3f"
          % (level, N, N, f, ALPHA * END_T / (L * L)))
    return N


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--level", action="append", choices=list(LEVELS))
    ap.add_argument("--check-levels", action="store_true")
    a = ap.parse_args()
    if a.check_levels:
        check_levels()
        sys.exit(0)
    if not a.root:
        refuse("--root is required")
    check_levels()
    for lv in (a.level or ["c", "m", "f"]):
        build(a.root, lv)
