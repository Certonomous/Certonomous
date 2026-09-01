#!/usr/bin/env python
# =============================================================================
# A1-WR -- PARAMETRIC WALL-RESOLVED NACA0012 MESH GENERATOR
#
# ONE SCRIPT, THREE LEVELS, ONE REFINEMENT FACTOR.  This exists so the family
# it builds can seed a Roache triple later instead of being a one-off: the
# levels differ ONLY in the refinement factor R, and EVERY length parameter
# that must scale with R does scale with R.
#
# ---------------------------------------------------------------------------
# WHY THAT LAST SENTENCE IS THE WHOLE POINT (L-430)
# ---------------------------------------------------------------------------
# cfd's L-430: "a generator parameter that does not scale with the ladder
# builds three clean meshes and a meaningless observed order."  A generator
# that refines the chordwise spacing but leaves the near-wall spacing, the
# extrusion count, the clustering ratio or the trailing-edge point count fixed
# produces three meshes that LOOK like a ladder, pass checkMesh, and whose
# observed order of convergence is a number about nothing.
#
# This script therefore scales, all together, off the single factor R:
#   dX1, dX2, dXMax  ->  / R      (chordwise spacings)
#   Alpha1, Alpha2   ->  ** (1/R) (clustering ratio -- so the STRETCHED region
#                                  refines too, not just the constant region)
#   NpTE             ->  * R      (blunt trailing-edge points)
#   s0               ->  / R      (first cell height -- the y+ knob)
#   N extrusion      ->  * R      (wall-normal cell count)
#   marchDist        ->  FIXED    (far-field extent is a PHYSICAL choice and
#                                  must NOT move between levels, or the three
#                                  meshes are not the same problem)
#
# `--selfcheck` drives R = 1, 2, 4 and REFUSES (exit 2) if any parameter that
# must scale returned the same value at two different R, or if marchDist moved.
# A ladder whose generator was never driven at more than one R is a ladder
# nobody has checked.
#
# ---------------------------------------------------------------------------
# THE REFINEMENT RATIO THIS FAMILY SUPPORTS
# ---------------------------------------------------------------------------
#   REGISTERED REFINEMENT RATIO r = 2, in ALL THREE directions
#   (chordwise, wall-normal count, and near-wall spacing).
#   L1 : R = 1   L2 : R = 2   L3 : R = 4
#   Unlike `cgns_utils coarsen/refine`, which is factor-2-only on a fixed
#   topology, this generator is continuous in R -- r = 2 is a CHOICE recorded
#   here, not a limitation of the tool.  A non-integer r (e.g. 1.5) is
#   buildable and is left unregistered because no rung has asked for it.
#
# ---------------------------------------------------------------------------
# DERIVED FROM the DAFoam tutorial `genAirFoilMesh.py` as shipped in
# `/home/ubuntu/certonomous-runs/ladder-a1-naca0012/genAirFoilMesh.py`
# (4,032-cell WALL-FUNCTIONED mesh, s0 = 4e-3, N = 33, marchDist = 20).
# The airfoil profile handling and the pyHyp option block are the tutorial's.
# What is NEW here is the R-parameterisation and the wall-resolved s0.
# =============================================================================

from __future__ import print_function
import argparse
import os
import sys

# --------------------------------------------------------------------------
# BASE PARAMETERS -- the R = 1 (L1) level.  FROZEN.  Every level is derived
# from these by the scaling rules above and by nothing else.
# --------------------------------------------------------------------------
BASE = {
    "ZSpan": 0.1,          # span width (2-D case: one cell in z)
    "nSpan": 2,            # points in z -> 1 cell.  DOES NOT SCALE (2-D).
    "dX1PS": 0.005,        # first dx from the LE, pressure side
    "Alpha1PS": 1.2,
    "dX2PS": 2e-3,         # first dx from the TE, pressure side
    "Alpha2PS": 1.2,
    "dXMaxPS": 0.02,
    "dX1SS": 0.005,
    "Alpha1SS": 1.2,
    "dX2SS": 2e-3,
    "Alpha2SS": 1.2,
    "dXMaxSS": 0.02,
    "NpTE": 5,             # blunt-TE points
    "NExtrudeCells": 64,   # wall-normal CELLS (pyHyp N = cells + 1)
    "s0": 2.5e-6,          # FIRST CELL HEIGHT at L1.  See the y+ note below.
                           # AMENDMENT 1 (pre-compute, 2026-09-01): was 3.0e-6,
                           # derived from an INFERRED Sutherland mu = 1.846e-5.
                           # The dictionary says `transport const; mu 0.000018`.
                           # Re-derived from the READ value; see the block below.
    "marchDist": 20.0,     # far-field extent, chords.  FIXED ACROSS LEVELS.
}

# --------------------------------------------------------------------------
# WHY s0 = 2.5e-6 AT L1, AND WHY THE COMPRESSIBLE ARM SET IT
# --------------------------------------------------------------------------
# EVERY CONSTANT BELOW IS READ FROM THE CASE'S OWN DICTIONARY.  The first
# version of this block INFERRED mu = 1.846e-5 (Sutherland air at 300 K) and
# was WRONG: the dictionary specifies `transport const; mu 0.000018`.  Three
# different compressible Re values were in circulation in the lab on the day
# this was written and not one of them had been read from the case.  A number
# nobody measured has no place in a freeze, least of all the one that sizes
# the mesh.  Sources, by path:
#   nu (incompressible)  CURRICULUM-AOAI-.../case_cold/constant/transportProperties
#   mu, W (compressible) CURRICULUM-AOAC-.../case/constant/thermophysicalProperties
#   chord                surfaceMesh.xyz of ladder-a1-naca0012, measured extent
#
# `transport const`, NOT Sutherland: mu does NOT vary with temperature here.
# That is defensible at M = 0.288, where the stagnation temperature rise is
# 4.98 K, but it is stated because a reader meeting a compressible solver will
# otherwise assume Sutherland and mis-derive nu at the wall.
#
# The two arms of this sweep are NOT at the same Reynolds number:
#     incompressible  U = 10  m/s, nu   = 1.5e-5       -> Re_c = 6.6667e5
#     compressible    U = 100 m/s, nu_w = 1.529548e-5  -> Re_c = 6.537877e6
#         where nu_w = mu/rho, rho = p0/(R T0) = 1.1768179 from perfectGas
#         with molWeight 28.97 (R = 287.0028).  NOTE the runScript's
#         force-scaling rho0 = p0/T0/287 = 1.1768293 is a DIFFERENT quantity
#         and differs by 9.6e-6 relative; it scales CD/CL, it is not the
#         thermodynamic density.
# a ratio of 9.8068.  y+ for a GIVEN wall spacing is therefore roughly an order
# of magnitude larger on the compressible arm.  A mesh sized to give y+ < 1 at
# U = 10 gives y+ of order 1.5-2 at U = 100 ON THE SAME CELLS.
#
# So the COMPRESSIBLE arm is the binding constraint and this family is sized on
# it.  Both arms share ONE mesh family deliberately: building a separate mesh
# per regime would confound the regime comparison -- the finding being tested
# is that both arms broke at the same angle to the degree across a tenfold
# Reynolds difference, and that comparison survives only if the discretisation
# is identical.  The incompressible arm is consequently OVER-resolved near the
# wall.  That costs iterations; it does not cost correctness.
#
# THE CHORD IS NOT 1.0 AND WAS MEASURED, NOT ASSUMED.  Every Re above depends
# on it LINEARLY.  The built surface extends to x = 0.99882687 because the
# tutorial truncates PS and SS at ~99.8 % chord for the blunt TE (the profile
# files themselves end at 0.99941610).  Re is nonetheless quoted at a
# REFERENCE chord of 1.0, because A0 = 0.1 in the run scripts is a reference
# AREA consistent with chord 1.0 x span 0.1, and the force coefficients are
# already normalised by it -- so 1.0 is the consistent reference.  Using the
# built extent instead moves every Re by 0.117 % (Re_comp 6.530208e6), which
# is disclosed here and is far inside the sizing margin.
#
# EVERY y+ NUMBER BELOW IS A PREDICTION, NOT A MEASUREMENT.  It uses the
# flat-plate correlation Cf = 0.0576 Re^-0.2 with:
#   - a leading-edge/peak factor of 1.5611, ANCHORED on the measured y+max of
#     92.4 at y_c = 2e-3 on the existing coarse mesh (u_tau 0.693 vs a
#     flat-plate 0.44392) -- this one rests on a measurement;
#   - an incidence factor of 1.8 at alpha = 18, which is an ESTIMATE with no
#     measurement behind it and is the weakest link in the chain.
# Predicted y+ at alpha = 18 (compressible / incompressible):
#     L1 0.811 / 0.104    L2 0.406 / 0.052    L3 0.203 / 0.026
# The compressible arm binds by 7.81x.
# THIS IS NOT EVIDENCE THAT THE MESH IS WALL-RESOLVED.  Only measured y+ is.
# --------------------------------------------------------------------------

LEVELS = {"L1": 1, "L2": 2, "L3": 4}


def params_for(R):
    """Every level's parameter set, derived from BASE and R alone."""
    if R <= 0:
        raise ValueError("R must be positive, got %r" % R)
    p = {
        "R": R,
        "ZSpan": BASE["ZSpan"],
        "nSpan": BASE["nSpan"],
        # chordwise spacings shrink with R
        "dX1PS": BASE["dX1PS"] / R,
        "dX2PS": BASE["dX2PS"] / R,
        "dXMaxPS": BASE["dXMaxPS"] / R,
        "dX1SS": BASE["dX1SS"] / R,
        "dX2SS": BASE["dX2SS"] / R,
        "dXMaxSS": BASE["dXMaxSS"] / R,
        # clustering ratio approaches 1 as R grows, so the STRETCHED region
        # refines by the same factor as the constant region.  Without this the
        # leading and trailing edges would refine more slowly than the mid-chord
        # and the family's effective refinement ratio would not be r.
        "Alpha1PS": BASE["Alpha1PS"] ** (1.0 / R),
        "Alpha2PS": BASE["Alpha2PS"] ** (1.0 / R),
        "Alpha1SS": BASE["Alpha1SS"] ** (1.0 / R),
        "Alpha2SS": BASE["Alpha2SS"] ** (1.0 / R),
        # blunt TE resolution scales with R
        "NpTE": int(round(BASE["NpTE"] * R)),
        # wall-normal: count up, first height down
        "NExtrudeCells": int(round(BASE["NExtrudeCells"] * R)),
        "s0": BASE["s0"] / R,
        # far-field extent is FIXED -- see the header
        "marchDist": BASE["marchDist"],
    }
    return p


def implied_growth_ratio(s0, ncells, dist):
    """Solve s0 * (g^n - 1)/(g - 1) = dist for g by bisection.

    REPORTED, NOT ASSUMED.  pyHyp's actual layer distribution is its own; this
    is the geometric-series equivalent and is the number the growth-ratio
    ceiling is registered against.  The MEASURED distribution is read back off
    the built mesh by the mesh-admission step, not from here.
    """
    if s0 * ncells >= dist:
        return 1.0
    lo, hi = 1.0 + 1e-12, 3.0
    for _ in range(200):
        g = 0.5 * (lo + hi)
        tot = s0 * (g ** ncells - 1.0) / (g - 1.0)
        if tot < dist:
            lo = g
        else:
            hi = g
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------
# THE L-430 GUARD.  A ladder whose generator was driven at exactly one R has
# not been shown to be a ladder.
# --------------------------------------------------------------------------
MUST_SCALE = [
    "dX1PS", "dX2PS", "dXMaxPS", "dX1SS", "dX2SS", "dXMaxSS",
    "Alpha1PS", "Alpha2PS", "Alpha1SS", "Alpha2SS",
    "NpTE", "NExtrudeCells", "s0",
]
MUST_NOT_SCALE = ["marchDist", "ZSpan", "nSpan"]


def selfcheck():
    """Drive R = 1, 2, 4 and refuse if the family is not actually a family."""
    print("=== A1-WR GENERATOR SELFCHECK -- R = 1, 2, 4 ===")
    sets = {}
    for name, R in sorted(LEVELS.items(), key=lambda kv: kv[1]):
        sets[name] = params_for(R)

    failures = []

    # (1) every MUST_SCALE parameter differs at every pair of levels
    names = ["L1", "L2", "L3"]
    for key in MUST_SCALE:
        vals = [sets[n][key] for n in names]
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                if vals[i] == vals[j]:
                    failures.append(
                        "MUST-SCALE PARAMETER DID NOT SCALE: %s is %r at both "
                        "%s and %s" % (key, vals[i], names[i], names[j]))
        print("  scales   %-16s %s" % (key, "  ".join("%s=%.6g" % (n, sets[n][key]) for n in names)))

    # (2) every MUST_NOT_SCALE parameter is identical at every level
    for key in MUST_NOT_SCALE:
        vals = [sets[n][key] for n in names]
        if len(set(vals)) != 1:
            failures.append(
                "FIXED PARAMETER MOVED BETWEEN LEVELS: %s = %r -- the three "
                "levels are then not the same problem" % (key, vals))
        print("  fixed    %-16s %s" % (key, "  ".join("%s=%.6g" % (n, sets[n][key]) for n in names)))

    # (3) THE MUTATION CONTROL.  A checker that cannot fail is not a checker.
    #     Mutate a MUST_SCALE parameter so it does NOT scale, and require the
    #     check above to catch it.  If the mutation does not land -- if the
    #     value we wrote was already what was there -- REFUSE, because a
    #     control that silently no-ops proves nothing.  (Three of the AoA
    #     lane's eleven controls were written against fixture literals and
    #     no-opped on real bytes; one of them was the zero-passing control.)
    victim = "s0"
    before_L1 = sets["L1"][victim]
    before_L2 = sets["L2"][victim]
    if before_L1 == before_L2:
        failures.append("MUTATION CONTROL CANNOT ARM: %s already equal across "
                        "L1/L2 before mutation" % victim)
    else:
        mutated = dict(sets)
        mutated["L2"] = dict(sets["L2"])
        mutated["L2"][victim] = before_L1          # force the non-scaling bug
        if mutated["L2"][victim] == before_L2:
            failures.append("MUTATION CONTROL DID NOT LAND: writing %s left "
                            "the value unchanged" % victim)
        elif mutated["L1"][victim] != mutated["L2"][victim]:
            failures.append("MUTATION CONTROL NOT SEEN: the checker's own "
                            "predicate does not fire on a planted "
                            "non-scaling %s" % victim)
        else:
            print("  CONTROL  mutation landed (%s L2 %.6g -> %.6g) and the "
                  "equality predicate fires on it" % (victim, before_L2, before_L1))

    # (4) report the derived geometry of each level
    print("\n  level  R   chord-cells*  wnormal  s0          growth  marchDist")
    for n in names:
        p = sets[n]
        g = implied_growth_ratio(p["s0"], p["NExtrudeCells"], p["marchDist"])
        print("  %-5s  %-3g %-13s %-8d %-11.4g %-7.4f %g"
              % (n, p["R"], "(built)", p["NExtrudeCells"], p["s0"], g, p["marchDist"]))
    print("  * chordwise cell count is a BUILT quantity -- it comes out of the\n"
          "    spline interpolation, is printed by the build, and is never\n"
          "    asserted here.")

    if failures:
        print("\nSELFCHECK REFUSED (exit 2):")
        for f in failures:
            print("  - %s" % f)
        return 2
    print("\nSELFCHECK PASS -- the family scales in every direction it claims to.")
    return 0


def build(level, outdir, profile_dir):
    """Build one level.  Writes surfaceMesh.xyz and volumeMesh.xyz in outdir."""
    from pyhyp import pyHyp
    import numpy
    from pyspline import Curve

    R = LEVELS[level]
    p = params_for(R)

    print("=== A1-WR BUILD level=%s R=%g ===" % (level, R))
    for k in sorted(p):
        print("  param %-16s %r" % (k, p[k]))

    airfoilProfilePS = os.path.join(profile_dir, "NACA0012PS.profile")
    airfoilProfileSS = os.path.join(profile_dir, "NACA0012SS.profile")
    for f in (airfoilProfilePS, airfoilProfileSS):
        if not os.path.isfile(f):
            print("REFUSE: profile absent at point of use: %s" % f)
            return 3

    def read_profile(path):
        xs, ys = [], []
        with open(path) as fh:
            for line in fh:
                cols = line.split()
                if len(cols) < 2:
                    continue
                xs.append(float(cols[0]))
                ys.append(float(cols[1]))
        return xs, ys, [0.0] * len(xs)

    def side(xs, ys, zs, dX1, Alpha1, dX2, Alpha2, dXMax):
        tmp = dX1
        nStretch1 = 0
        for i in range(100000):
            if tmp > dXMax:
                nStretch1 = i
                break
            tmp *= Alpha1
        tmp = dX2
        nStretch2 = 0
        for i in range(100000):
            if tmp > dXMax:
                nStretch2 = i
                break
            tmp *= Alpha2
        xLConst = xs[-1]
        for i in range(nStretch1):
            xLConst -= dX1 * (Alpha1 ** i)
        for i in range(nStretch2):
            xLConst -= dX2 * (Alpha2 ** i)
        nXConst = int(xLConst / dXMax)
        if nXConst < 1:
            raise ValueError("constant region vanished: nXConst=%d" % nXConst)
        dXMaxAdj = xLConst / nXConst
        xInterp = [0.0]
        tmp = dX1
        for i in range(nStretch1):
            xInterp.append(xInterp[-1] + tmp)
            tmp *= Alpha1
        for i in range(nXConst):
            xInterp.append(xInterp[-1] + dXMaxAdj)
        tmp = dX2 * (Alpha2 ** (nStretch2 - 1))
        for i in range(nStretch2):
            xInterp.append(xInterp[-1] + tmp)
            tmp /= Alpha2
        c1 = Curve(x=xs, y=ys, z=zs, k=3)
        X = c1(xInterp)
        c2 = Curve(X=X, k=3)
        return c2.X[:, 0], c2.X[:, 1], nStretch1, nStretch2, nXConst

    xPS, yPS, zPS = read_profile(airfoilProfilePS)
    xSS, ySS, zSS = read_profile(airfoilProfileSS)

    x1PS, y1PS, s1PS, s2PS, ncPS = side(
        xPS, yPS, zPS, p["dX1PS"], p["Alpha1PS"], p["dX2PS"], p["Alpha2PS"], p["dXMaxPS"])
    x1SS, y1SS, s1SS, s2SS, ncSS = side(
        xSS, ySS, zSS, p["dX1SS"], p["Alpha1SS"], p["dX2SS"], p["Alpha2SS"], p["dXMaxSS"])

    NpTE = p["NpTE"]
    delta_y = numpy.linspace(y1PS[-1], y1SS[-1], NpTE)[1:]
    delta_x = numpy.linspace(x1PS[-1], x1SS[-1], NpTE)[1:]

    xAll = numpy.append(x1SS[::-1], x1PS[1:])
    xAll = numpy.append(xAll, delta_x)
    yAll = numpy.append(y1SS[::-1], y1PS[1:])
    yAll = numpy.append(yAll, delta_y)

    nSurfPts = len(xAll)
    nSurfCells = nSurfPts - 1
    nCells = nSurfCells * p["NExtrudeCells"] * (p["nSpan"] - 1)
    growth = implied_growth_ratio(p["s0"], p["NExtrudeCells"], p["marchDist"])

    print("  BUILT nSurfacePoints=%d nSurfaceCells=%d" % (nSurfPts, nSurfCells))
    print("  BUILT nWallNormalCells=%d" % p["NExtrudeCells"])
    print("  BUILT nCellsPredicted=%d" % nCells)
    print("  BUILT impliedGrowthRatio=%.5f" % growth)
    print("  BUILT s0=%.6g marchDist=%g" % (p["s0"], p["marchDist"]))

    nSpan = p["nSpan"]
    surf = os.path.join(outdir, "surfaceMesh.xyz")
    with open(surf, "w") as f:
        f.write("1\n")
        f.write("%d %d %d\n" % (len(xAll), nSpan, 1))
        for iDim in range(3):
            for z in numpy.linspace(0.0, p["ZSpan"], nSpan):
                for i in range(len(xAll)):
                    if iDim == 0:
                        f.write("%20.16f\n" % xAll[i])
                    elif iDim == 1:
                        f.write("%20.16f\n" % yAll[i])
                    else:
                        f.write("%20.16f\n" % z)

    options = {
        "inputFile": surf,
        "unattachedEdgesAreSymmetry": False,
        "outerFaceBC": "farfield",
        "autoConnect": True,
        "BC": {1: {"jLow": "zSymm", "jHigh": "zSymm"}},
        "families": "wall",
        "N": p["NExtrudeCells"] + 1,
        "s0": p["s0"],
        "marchDist": p["marchDist"],
        "ps0": -1.0,
        "pGridRatio": -1.0,
        "cMax": 1.0,
        "epsE": 2.0,
        "epsI": 4.0,
        "theta": 2.0,
        "volCoef": 0.20,
        "volBlend": 0.0005,
        "volSmoothIter": 20,
    }
    hyp = pyHyp(options=options)
    hyp.run()
    hyp.writePlot3D(os.path.join(outdir, "volumeMesh.xyz"))
    print("  WROTE %s" % os.path.join(outdir, "volumeMesh.xyz"))
    print("=== A1-WR BUILD END level=%s ===" % level)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selfcheck", action="store_true",
                    help="drive R=1,2,4 and refuse if the family does not scale")
    ap.add_argument("--level", choices=sorted(LEVELS), help="level to build")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--profiles", default="./profiles")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    if not a.level:
        ap.error("one of --selfcheck or --level is required")
    return build(a.level, a.outdir, a.profiles)


if __name__ == "__main__":
    sys.exit(main())
