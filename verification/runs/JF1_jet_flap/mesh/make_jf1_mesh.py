#!/usr/bin/env python3
"""
JF1 JET-FLAP AIRFOIL -- THE ONE PARAMETRIC C-TOPOLOGY MESH SCRIPT.

Registered path: verification/runs/JF1_jet_flap/mesh/make_jf1_mesh.py
(JF1_PREREGISTRATION.md section 4.1, frozen at commit 12b1bd84).

Emits a complete constant/polyMesh for a 2-D, one-cell-thick C-topology grid
around a NACA 0012 truncated to a blunt trailing-edge base of height h, with the
base carried as its own patch (`jetSlot`), from a SINGLE ladder scale factor s.
NO LEVEL IS EVER HAND-EDITED (section 4.1).

TOPOLOGY IS A REQUIRED, EXPLICITLY-NAMED SELECTION.  There is no default.
  --topology c   emits the registered C-mesh (section 3.2).
  --topology o   REFUSES and points at cases/JF1_JET_FLAP/build_jf1.py, which is
                 the O-mesh generator the five completed L1 feasibility rows of
                 2026-08-31 were built with.  That file is NOT modified by this
                 one and is not imported by it; the O-path stays byte-identical
                 so those rows remain reproducible.

BLOCK STRUCTURE (section 4.2, and it reproduces the registered totals exactly):

    one C-block of  Ni x Nj  cells, Ni = 2*n_wake + 2*n_surf, Nj = n_norm
    one sheet block of  n_wake x n_sheet  cells filling the base gap and its
    downstream extension, conformal with the C-block on both its long edges.

    L1: 460*97 + 130*12 =  44620 + 1560 =  46180   (registered  46180)
    L2: 630*133 + 178*16 = 83790 + 2848 =  86638   (registered  86638)
    L3: 860*181 + 243*22 =155660 + 5346 = 161006   (registered 161006)

The C-block's i index runs, as ONE continuous line:

    i = 0 .............. upper wake outlet, (x_out, +h/2)
    i = n_wake ......... trailing-edge UPPER corner, (c, +h/2)
    i = n_wake+n_surf .. leading edge, (0, 0)
    i = n_wake+2n_surf . trailing-edge LOWER corner, (c, -h/2)
    i = Ni ............. lower wake outlet, (x_out, -h/2)

so the traversal is COUNTERCLOCKWISE and the outward normal is (t_y, -t_x).
j runs outward, k is the one-cell span.

DEGENERATE-BRANCH POLICY (F28 lesson, applied here rather than rediscovered).
F28's generator carried a solve_ratio(length, n, first) whose n == 1 branch
returned a ratio of 1.0 WITHOUT checking that length == first, so a fictional
first-cell size scored as a perfect junction match (a measured 64x axial
discontinuity).  Every function below that could take a degenerate branch --
n <= 1, zero length, equal endpoints, unit growth -- REFUSES (SystemExit) unless
the identity that branch presumes is verified numerically.  Nothing is clamped.
"""

import argparse
import hashlib
import math
import os
import sys

# ---------------------------------------------------------------------------
# Section 1.  Registered physical inputs (sections 2, 3.1, 4.3)
# ---------------------------------------------------------------------------
CHORD = 1.0                 # c, m
H_OVER_C = 0.005            # slot / base height h/c  (section 3.1)
U_INF = 10.0                # m/s
NU = 1.0e-5                 # m^2/s -> Re_c = 1.0e6
RE_C = U_INF * CHORD / NU
NACA_T = 0.12

# Registered L1 counts (section 4.2) and L1 sizings (sections 4.3, 4.4)
N_SURF_L1 = 100             # cells per surface side
N_WAKE_L1 = 130             # cells per wake side
N_NORM_L1 = 97              # wall-normal cells
N_SHEET_L1 = 12             # cells across h
Y1_L1 = 5.0e-06             # m, first-cell height (section 4.3.3)
R_NORMAL = 25.0             # m, normal stack total = farfield at 25 c (3.2)
G_CAP = 1.15                # growth cap (section 4.3)
WAKE_FINE = 3.0             # m, the 3 c wake box (section 4.4)
DELTA_FLOOR = 36            # complete layers inside delta (section 4.3.3)

REFUSE = "REFUSED: "


def refuse(msg):
    sys.exit(REFUSE + msg)


# ---------------------------------------------------------------------------
# Section 2.  Geometry primitives -- every degenerate branch refuses
# ---------------------------------------------------------------------------
def naca_yt(x):
    """Half-thickness of a NACA 00tt at chordwise station x in [0,1]."""
    return 5.0 * NACA_T * (0.2969 * math.sqrt(x)
                           - 0.1260 * x
                           - 0.3516 * x * x
                           + 0.2843 * x ** 3
                           - 0.1015 * x ** 4)


def solve_truncation(half_h_over_c, lo=0.90, hi=0.99999, tol=1e-14):
    """x_te with yt(x_te)/x_te == half_h_over_c after rescaling by 1/x_te."""
    def f(x):
        return naca_yt(x) / x - half_h_over_c
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        refuse("truncation bracket failed: f(lo)=%g f(hi)=%g" % (flo, fhi))
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
        if hi - lo < tol:
            break
    x = 0.5 * (lo + hi)
    # VERIFY the identity this return presumes.
    err = abs(naca_yt(x) / x - half_h_over_c) / half_h_over_c
    if err > 1e-9:
        refuse("truncation did not converge: relative error %.3e" % err)
    return x


def geom_sum(y1, g, n):
    """Total height of n geometric cells starting at y1 with ratio g.

    The g == 1 branch is the analytic limit and is exact, but it is only taken
    when g is genuinely 1 to within 1e-15; it is not a fallback.
    """
    if n < 0:
        refuse("geom_sum called with n = %d" % n)
    if abs(g - 1.0) < 1e-15:
        return y1 * n
    return y1 * (g ** n - 1.0) / (g - 1.0)


def solve_growth(y1, n, total, gmax=2.0, tol=1e-15):
    """Solve g so that n cells from y1 stack EXACTLY to total.

    F28-CLASS GUARD.  For n == 1 the stack height is y1 for EVERY g, so no g is
    determined.  A generator that returned a nominal 1.0 here would be scoring a
    fictional match.  This refuses instead, and it refuses even when y1 == total
    (the case where a nominal answer would be harmless) because a caller that
    reaches n == 1 has lost the distribution it thinks it has.
    """
    if n < 2:
        refuse("solve_growth with n = %d: a %d-cell stack determines no growth "
               "ratio (F28 degenerate-branch class)" % (n, n))
    if y1 <= 0.0 or total <= 0.0:
        refuse("solve_growth with y1 = %g, total = %g" % (y1, total))
    lo, hi = 1.0 + 1e-12, gmax
    if geom_sum(y1, lo, n) > total:
        refuse("even g = 1 overshoots: %d x %g = %g > %g"
               % (n, y1, y1 * n, total))
    if geom_sum(y1, hi, n) < total:
        refuse("g = %g undershoots %g with %d cells from y1 = %g"
               % (gmax, total, n, y1))
    for _ in range(600):
        mid = 0.5 * (lo + hi)
        if geom_sum(y1, mid, n) < total:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    g = 0.5 * (lo + hi)
    err = abs(geom_sum(y1, g, n) - total) / total
    if err > 1e-9:
        refuse("solve_growth residual %.3e" % err)
    return g


def min_count_for_cap(y1, total, gcap):
    """Smallest integer N whose SOLVED g satisfies g <= gcap."""
    if gcap <= 1.0 + 1e-12:
        refuse("min_count_for_cap needs gcap > 1, got %g" % gcap)
    n = int(math.ceil(math.log(1.0 + (total / y1) * (gcap - 1.0))
                      / math.log(gcap)))
    n = max(n, 2)
    while geom_sum(y1, gcap, n) < total:
        n += 1
    return n


def layers_inside(y1, g, delta):
    """COMPLETE geometric layers whose cumulative stack is <= delta.

    F28-CLASS GUARD.  A bounded loop that RETURNS its bound when it fails to
    terminate hands back a fictional layer count that then passes a >= 36 floor.
    This refuses on non-termination instead.
    """
    n, s = 0, 0.0
    for _ in range(1000000):
        s_next = s + y1 * g ** n
        if s_next > delta:
            return n
        s = s_next
        n += 1
    refuse("layers_inside did not terminate (y1 = %g, g = %g, delta = %g)"
           % (y1, g, delta))


def two_sided(n, total, ds_a, ds_b, ratio):
    """n intervals summing EXACTLY to total, first ds_a, last ds_b, local growth
    never above `ratio`, plateau ds_max SOLVED so the sum closes.

    F28-CLASS GUARD.  The returned distribution's ENDPOINTS are verified against
    ds_a and ds_b before return.  A proportional-rescale fallback that closes the
    sum while silently moving the endpoints would be exactly the defect: the TE
    spacing is registered (section 4.4) as MATCHED to the base cell, and a
    fictional match there is what F28 shipped.
    """
    if n < 2:
        refuse("two_sided with n = %d" % n)
    if total <= 0.0 or ds_a <= 0.0 or ds_b <= 0.0:
        refuse("two_sided with total = %g, ds_a = %g, ds_b = %g"
               % (total, ds_a, ds_b))
    if ratio <= 1.0 + 1e-12:
        refuse("two_sided needs ratio > 1, got %g" % ratio)

    def build(dmax):
        return [min(ds_a * ratio ** k, ds_b * ratio ** (n - 1 - k), dmax)
                for k in range(n)]

    lo, hi = max(ds_a, ds_b), total
    if sum(build(lo)) > total:
        refuse("two_sided cannot close: the two end ramps alone sum to %.6e > "
               "%.6e with n = %d.  More cells or smaller end spacings are "
               "needed; the endpoints are registered and are NOT rescaled."
               % (sum(build(lo)), total, n))
    if sum(build(hi)) < total:
        refuse("two_sided cannot close upward: plateau at total still sums to "
               "%.6e < %.6e" % (sum(build(hi)), total))
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if sum(build(mid)) < total:
            lo = mid
        else:
            hi = mid
    dmax = 0.5 * (lo + hi)
    d = build(dmax)
    s = sum(d)
    if s <= 0.0:
        refuse("two_sided produced a zero-length distribution")
    d = [v * total / s for v in d]
    # VERIFY the two identities this return presumes.
    ea = abs(d[0] / ds_a - 1.0)
    eb = abs(d[-1] / ds_b - 1.0)
    if ea > 1e-9 or eb > 1e-9:
        refuse("two_sided endpoints moved: first %.9e vs registered %.9e "
               "(rel %.3e), last %.9e vs registered %.9e (rel %.3e)"
               % (d[0], ds_a, ea, d[-1], ds_b, eb))
    es = abs(sum(d) / total - 1.0)
    if es > 1e-12:
        refuse("two_sided closure residual %.3e" % es)
    for k in range(n - 1):
        r = max(d[k], d[k + 1]) / min(d[k], d[k + 1])
        if r > ratio * (1.0 + 1e-9):
            refuse("two_sided local growth %.6f exceeds the cap %.6f at k = %d"
                   % (r, ratio, k))
    return d, dmax


def poly_area(p):
    """Signed shoelace area of a polygon given as a list of (x, y)."""
    a = 0.0
    m = len(p)
    for i in range(m):
        j = (i + 1) % m
        a += p[i][0] * p[j][1] - p[j][0] * p[i][1]
    return 0.5 * a


# ---------------------------------------------------------------------------
# Section 3.  Surface point set
# ---------------------------------------------------------------------------
def surface_table(nsamp=200000):
    """Dense arc-length table of the SCALED truncated upper surface, LE -> TE."""
    half_h = 0.5 * H_OVER_C * CHORD
    x_te = solve_truncation(half_h / CHORD)
    scale = CHORD / x_te
    xs, ys, ss = [], [], [0.0]
    for q in range(nsamp + 1):
        xi = 0.5 * (1.0 - math.cos(math.pi * q / nsamp)) * x_te
        xs.append(xi * scale)
        ys.append(naca_yt(xi) * scale)
    for q in range(1, nsamp + 1):
        ss.append(ss[-1] + math.hypot(xs[q] - xs[q - 1], ys[q] - ys[q - 1]))
    return xs, ys, ss, x_te, scale


def at_arc(xs, ys, ss, s):
    """Point on the scaled upper surface at arc length s from the LE."""
    S = ss[-1]
    s = min(max(s, 0.0), S)
    lo, hi = 0, len(ss) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ss[mid] <= s:
            lo = mid
        else:
            hi = mid
    den = ss[hi] - ss[lo]
    if den <= 0.0:
        # F28-CLASS GUARD: an equal-endpoint bracket means two table points
        # coincide.  Returning f = 0 would be a nominal answer for an identity
        # that has not been verified.
        refuse("arc-length table has a zero-length interval at index %d" % lo)
    f = (s - ss[lo]) / den
    return (xs[lo] + f * (xs[hi] - xs[lo]), ys[lo] + f * (ys[hi] - ys[lo]))


# ---------------------------------------------------------------------------
# Section 4.  polyMesh writer
# ---------------------------------------------------------------------------
HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| JF1 jet-flap airfoil -- C-TOPOLOGY                                          |
| generated by verification/runs/JF1_jet_flap/mesh/make_jf1_mesh.py           |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       %s;
    location    "constant/polyMesh";
    object      %s;
}
"""


def write_polymesh(outdir, P, faces, owner, neigh, patches):
    os.makedirs(outdir, exist_ok=True)
    nInt = len(neigh)

    with open(os.path.join(outdir, "points"), "w") as fh:
        fh.write(HEADER % ("vectorField", "points"))
        fh.write("\n%d\n(\n" % len(P))
        fh.write("".join("(%.12g %.12g %.12g)\n" % p for p in P))
        fh.write(")\n")

    with open(os.path.join(outdir, "faces"), "w") as fh:
        fh.write(HEADER % ("faceList", "faces"))
        fh.write("\n%d\n(\n" % len(faces))
        fh.write("".join("4(%d %d %d %d)\n" % f for f in faces))
        fh.write(")\n")

    with open(os.path.join(outdir, "owner"), "w") as fh:
        fh.write(HEADER % ("labelList", "owner"))
        fh.write("\n%d\n(\n" % len(owner))
        fh.write("".join("%d\n" % v for v in owner))
        fh.write(")\n")

    with open(os.path.join(outdir, "neighbour"), "w") as fh:
        fh.write(HEADER % ("labelList", "neighbour"))
        fh.write("\n%d\n(\n" % nInt)
        fh.write("".join("%d\n" % v for v in neigh))
        fh.write(")\n")

    with open(os.path.join(outdir, "boundary"), "w") as fh:
        fh.write(HEADER % ("polyBoundaryMesh", "boundary"))
        fh.write("\n%d\n(\n" % len(patches))
        start = nInt
        for name, ptype, fl in patches:
            fh.write("    %s\n    {\n        type            %s;\n"
                     % (name, ptype))
            if ptype == "wall":
                fh.write("        inGroups        1(wall);\n")
            elif ptype == "empty":
                fh.write("        inGroups        1(empty);\n")
            fh.write("        nFaces          %d;\n        startFace       %d;\n"
                     "    }\n" % (len(fl), start))
            start += len(fl)
        fh.write(")\n")


# ---------------------------------------------------------------------------
# Section 5.  Driver
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="JF1 C-topology mesh generator (pre-registration 4.1)")
    ap.add_argument("--topology", required=True, choices=["c", "o"],
                    help="REQUIRED and never defaulted.  'c' = the registered "
                         "C-mesh.  'o' refuses and names the O-mesh script.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--level", required=True, choices=["L1", "L2", "L3"])
    ap.add_argument("--t-z", type=float, default=1.0,
                    help="span thickness; section 5.6 registers EXACTLY 1.0 m "
                         "and requires this script to refuse anything else")
    ap.add_argument("--diagnostic-tz", type=float, default=None,
                    help="recompute and print the metrics for this t_z WITHOUT "
                         "writing anything; for reporting only")
    # quality knobs, defaults measured by a checkMesh sweep on this geometry
    ap.add_argument("--outer-ds0", type=float, default=0.02,
                    help="m; outer-boundary cell size at the two "
                         "semicircle/line junctions, scaled 1/s")
    ap.add_argument("--blend-a", type=float, default=0.02)
    ap.add_argument("--blend-b", type=float, default=1.5)
    ap.add_argument("--wake-ramp", type=float, default=0.0,
                    help="m; distance over which the wake first-cell height "
                         "relaxes from y1 to the sheet cell height.  DEFAULT 0 "
                         "= NO RAMP: the wake stations carry the SAME stack as "
                         "the wall.  See the measurement in the code comment.")
    ap.add_argument("--phi-a", type=float, default=1.0e-04)
    ap.add_argument("--phi-b", type=float, default=3.0e-03)
    ap.add_argument("--normal-smooth", type=int, default=1500,
                    help="Jacobi passes spreading the CONCAVE trailing-edge "
                         "corner turn over the direction field.  MEASURED max "
                         "non-orthogonality on L1: 200 -> 86.2, 600 -> 34.2, "
                         "1500 -> 33.6.  200 is on the cliff; 1500 is on the "
                         "plateau, which is why the default is not 600.")
    ap.add_argument("--tang-cap", type=float, default=0.12,
                    help="tangential growth cap is 1 + tang_cap/s")
    ap.add_argument("--wake-cap", type=float, default=0.08,
                    help="wake fine-box growth cap is 1 + wake_cap/s")
    ap.add_argument("--ds-le", type=float, default=2.0e-04)
    ap.add_argument("--x-out", type=float, default=26.0,
                    help="outlet plane; 26.0 m puts it 25 c AFT OF THE TE, so "
                         "every boundary is at least the registered 25 c away")
    args = ap.parse_args()

    if args.topology == "o":
        refuse("this script emits the registered C-topology only.  The O-mesh "
               "used by the five completed L1 feasibility rows of 2026-08-31 "
               "is cases/JF1_JET_FLAP/build_jf1.py, which this script does not "
               "modify, import or supersede.  Run that file directly to "
               "reproduce those rows.")

    LADDER = {"L1": 1.0, "L2": 1.3693, "L3": 1.8708}
    s = LADDER[args.level]

    if abs(args.t_z - 1.0) > 0.0:
        refuse("section 5.6 registers t_z = 1.0 m EXACTLY (Aref = c*t_z = 1.0 "
               "m2 is valid only then, forceCoeffs.C:164) and requires this "
               "script to refuse otherwise.  Got t_z = %g." % args.t_z)
    t_z = args.t_z

    n_surf = int(round(N_SURF_L1 * s))
    n_wake = int(round(N_WAKE_L1 * s))
    n_norm = int(round(N_NORM_L1 * s))
    n_sheet = int(round(N_SHEET_L1 * s))
    y1 = Y1_L1 / s
    h = H_OVER_C * CHORD
    half_h = 0.5 * h

    Ni = 2 * n_wake + 2 * n_surf
    Nj = n_norm
    n_cells = Ni * Nj + n_wake * n_sheet

    REG = {"L1": (100, 130, 97, 12, 46180),
           "L2": (137, 178, 133, 16, 86638),
           "L3": (187, 243, 181, 22, 161006)}
    r_surf, r_wake, r_norm, r_sheet, r_tot = REG[args.level]
    if (n_surf, n_wake, n_norm, n_sheet, n_cells) != \
       (r_surf, r_wake, r_norm, r_sheet, r_tot):
        refuse("counts do not match the registered section 4.2 table for %s: "
               "got surf %d wake %d norm %d sheet %d total %d, registered "
               "%d/%d/%d/%d/%d" % (args.level, n_surf, n_wake, n_norm, n_sheet,
                                   n_cells, r_surf, r_wake, r_norm, r_sheet,
                                   r_tot))

    print("=" * 78)
    print("JF1 C-MESH -- level %s, scale s = %.4f" % (args.level, s))
    print("=" * 78)
    print("Re_c = %.4g, c = %g m, U_inf = %g m/s, nu = %g m2/s, h/c = %g"
          % (RE_C, CHORD, U_INF, NU, H_OVER_C))
    print("counts MATCH the registered 4.2 table: surf %d, wake %d, norm %d, "
          "sheet %d, TOTAL %d" % (n_surf, n_wake, n_norm, n_sheet, n_cells))

    # ---- near-wall stack (section 4.3) -----------------------------------
    delta = 0.37 * CHORD * RE_C ** -0.2
    g_wall = solve_growth(y1, Nj, R_NORMAL)
    n_in_delta = layers_inside(y1, g_wall, delta)
    print("\n-- WALL-NORMAL STACK (4.3) --")
    print("  delta(x=c)                = %.6e m" % delta)
    print("  y1 registered             = %.6e m" % y1)
    print("  N normal                  = %d" % Nj)
    print("  g SOLVED                  = %.6f   (cap %.4f -> %s)"
          % (g_wall, G_CAP, "OK" if g_wall <= G_CAP else "REFUSE"))
    print("  stack reaches             = %.9f m (target %.6f)"
          % (geom_sum(y1, g_wall, Nj), R_NORMAL))
    print("  complete layers in delta  = %d   (floor %d -> %s)"
          % (n_in_delta, DELTA_FLOOR,
             "MET" if n_in_delta >= DELTA_FLOOR else "NOT MET"))
    if g_wall > G_CAP:
        refuse("solved wall growth %.6f exceeds the registered cap %.4f"
               % (g_wall, G_CAP))
    if n_in_delta < DELTA_FLOOR:
        refuse("only %d complete layers inside delta, registered floor is %d"
               % (n_in_delta, DELTA_FLOOR))

    # ---- tangential surface distribution (section 4.4) --------------------
    ds_te = h / n_sheet
    ds_le = args.ds_le / s
    tang_ratio = 1.0 + args.tang_cap / s
    xs, ys, ss, x_te, sc = surface_table()
    S = ss[-1]
    d_upper, dmax_t = two_sided(n_surf, S, ds_te, ds_le, tang_ratio)
    print("\n-- SURFACE TANGENTIAL DISTRIBUTION (4.4) --")
    print("  truncation station x_te   = %.9f c, rescale 1/x_te = %.9f"
          % (x_te, sc))
    print("  one-side arc length S     = %.9f m" % S)
    print("  cells across h            = %d   (floor 12 on L1 -> %s)"
          % (n_sheet, "MET" if n_sheet >= 12 else "NOT MET"))
    print("  base cell h/n_sheet       = %.6e m" % ds_te)
    print("  surface spacing AT THE TE = %.6e m  (matched to the base cell, "
          "verified)" % d_upper[0])
    print("  surface spacing AT THE LE = %.6e m" % d_upper[-1])
    print("  tangential growth cap     = %.6f, solved plateau = %.6e m"
          % (tang_ratio, dmax_t))
    if n_sheet < 12:
        refuse("fewer than 12 cells across h")

    # ---- wake streamwise distribution (section 4.4) ------------------------
    wake_ratio = 1.0 + args.wake_cap / s
    nA = min_count_for_cap(ds_te, WAKE_FINE, wake_ratio)
    nB = n_wake - nA
    if nB < 5:
        refuse("wake fine box needs %d of %d cells, leaving %d for the outer "
               "wake" % (nA, n_wake, nB))
    gA = solve_growth(ds_te, nA, WAKE_FINE)
    dsA = [ds_te * gA ** k for k in range(nA)]
    outer_len = args.x_out - CHORD - WAKE_FINE
    ds_B0 = ds_te * gA ** nA
    gB = solve_growth(ds_B0, nB, outer_len)
    dsB = [ds_B0 * gB ** k for k in range(nB)]
    d_wake = dsA + dsB
    ssum = sum(d_wake)
    if abs(ssum / (args.x_out - CHORD) - 1.0) > 1e-9:
        refuse("wake distribution closure residual %.3e"
               % abs(ssum / (args.x_out - CHORD) - 1.0))
    if gA > G_CAP or gB > G_CAP:
        refuse("wake growth exceeds the cap: gA = %.6f, gB = %.6f, cap %.4f"
               % (gA, gB, G_CAP))
    print("\n-- WAKE STREAMWISE DISTRIBUTION (4.4) --")
    print("  fine box TE -> 3c         = %d cells, g SOLVED %.6f (cap %.6f)"
          % (nA, gA, wake_ratio))
    print("  coarse 3c -> outlet x=%.1f = %d cells, g SOLVED %.6f" % (args.x_out, nB, gB))
    print("  first wake cell           = %.6e m (matched to the base cell)"
          % d_wake[0])
    print("  cell length at x/c = 1 downstream of the TE = %.6e m"
          % _cell_at(d_wake, 1.0))
    print("  cell length at x/c = 3 downstream of the TE = %.6e m"
          % _cell_at(d_wake, 3.0))

    # ---- inner curve ------------------------------------------------------
    x_wake = [CHORD]
    for dd in d_wake:
        x_wake.append(x_wake[-1] + dd)      # n_wake+1 nodes, TE -> outlet

    P2 = []                                  # Ni+1 inner nodes
    for i in range(n_wake + 1):              # upper wake, outlet -> TE
        P2.append((x_wake[n_wake - i], +half_h))
    a = 0.0                                  # upper surface, TE -> LE
    for k in range(n_surf):
        a += d_upper[k]
        xx, yy = at_arc(xs, ys, ss, S - a)
        P2.append((xx, yy))
    for k in range(n_surf):                  # lower surface, LE -> TE
        xx, yy = at_arc(xs, ys, ss, sum(d_upper[n_surf - 1 - q]
                                        for q in range(k + 1)))
        P2.append((xx, -yy))
    for i in range(1, n_wake + 1):           # lower wake, TE -> outlet
        P2.append((x_wake[i], -half_h))
    if len(P2) != Ni + 1:
        refuse("inner curve has %d nodes, expected %d" % (len(P2), Ni + 1))
    # the TE corners and the LE must be exactly where the topology says
    for idx, want, what in ((0, (args.x_out, +half_h), "upper outlet"),
                            (n_wake, (CHORD, +half_h), "TE upper"),
                            (n_wake + n_surf, (0.0, 0.0), "LE"),
                            (n_wake + 2 * n_surf, (CHORD, -half_h), "TE lower"),
                            (Ni, (args.x_out, -half_h), "lower outlet")):
        if (abs(P2[idx][0] - want[0]) > 1e-9
                or abs(P2[idx][1] - want[1]) > 1e-9):
            refuse("inner node %s at (%.9g, %.9g), expected (%.9g, %.9g)"
                   % (what, P2[idx][0], P2[idx][1], want[0], want[1]))

    # ---- nodal normals ----------------------------------------------------
    seg = []
    for i in range(Ni):
        tx = P2[i + 1][0] - P2[i][0]
        ty = P2[i + 1][1] - P2[i][1]
        L = math.hypot(tx, ty)
        if L <= 0.0:
            refuse("zero-length inner segment at i = %d" % i)
        seg.append((ty / L, -tx / L))        # counterclockwise -> outward
    nrm = [seg[0]]
    for i in range(1, Ni):
        vx, vy = seg[i - 1][0] + seg[i][0], seg[i - 1][1] + seg[i][1]
        L = math.hypot(vx, vy)
        if L <= 1e-12:
            refuse("opposed segment normals at node %d (cusp)" % i)
        nrm.append((vx / L, vy / L))
    nrm.append(seg[-1])
    # THE TRAILING-EDGE CORNER IS CONCAVE FROM THE FLUID SIDE (the surface
    # climbs going upstream while the wake cut is flat), so pure normal-offset
    # marching CONVERGES there and folds.  Measured on this geometry with the
    # raw normals: cells invert at d ~ 1.5e-02 m, INSIDE delta.  The remedy is a
    # marching direction that is the TRUE normal at the wall (so y1 and wall
    # orthogonality are exact) and relaxes to a heavily smoothed direction field
    # further out, before the raw field can fold.  Both fields are built here.
    nrm_raw = list(nrm)
    for _ in range(args.normal_smooth):      # endpoints held: outlet stays flat
        new = [nrm[0]]
        for i in range(1, Ni):
            vx = 0.25 * nrm[i - 1][0] + 0.5 * nrm[i][0] + 0.25 * nrm[i + 1][0]
            vy = 0.25 * nrm[i - 1][1] + 0.5 * nrm[i][1] + 0.25 * nrm[i + 1][1]
            L = math.hypot(vx, vy)
            new.append((vx / L, vy / L))
        new.append(nrm[-1])
        nrm = new
    nrm_smooth = nrm

    # ---- outer C boundary -------------------------------------------------
    # The outer boundary is NOT distributed uniformly.  A uniform outer against
    # this strongly graded inner curve makes the grid lines lean by up to 18 deg
    # and back again over the wake, which MEASURED 81.0 deg non-orthogonality.
    # Instead every outer segment carries its own SOLVED grading that matches
    # the outer cell size ds0 at both semicircle/line junctions, so the outer
    # curve is as smooth as the inner one and both scale as 1/s with the ladder.
    R_c = R_NORMAL + half_h
    ds0 = args.outer_ds0 / s
    line_len = args.x_out
    g_out = solve_growth(ds0, n_wake, line_len)
    if g_out > G_CAP:
        refuse("outer wake grading %.6f exceeds the cap %.4f" % (g_out, G_CAP))
    d_out_line = [ds0 * g_out ** k for k in range(n_wake)]
    arc_line = [0.0]
    for v in d_out_line:
        arc_line.append(arc_line[-1] + v)      # 0 (junction) -> x_out (outlet)
    semi_len = math.pi * R_c
    d_out_semi, dmax_o = two_sided(2 * n_surf, semi_len, ds0, ds0,
                                   1.0 + args.tang_cap / s)
    arc_semi = [0.0]
    for v in d_out_semi:
        arc_semi.append(arc_semi[-1] + v)

    O2 = []
    for i in range(n_wake + 1):                # outlet -> junction, upper
        O2.append((arc_line[n_wake - i], +R_c))
    for p in range(1, 2 * n_surf + 1):         # semicircle, upper -> lower
        th = 0.5 * math.pi + math.pi * (arc_semi[p] / semi_len)
        O2.append((R_c * math.cos(th), R_c * math.sin(th)))
    for q in range(1, n_wake + 1):             # junction -> outlet, lower
        O2.append((arc_line[q], -R_c))
    if len(O2) != Ni + 1:
        refuse("outer curve has %d nodes, expected %d" % (len(O2), Ni + 1))
    print("\n-- OUTER C BOUNDARY --")
    print("  radius / half-width       = %.6f m (>= the registered 25 c)" % R_c)
    print("  outlet plane              = x = %.3f m, i.e. 25 c aft of the TE"
          % args.x_out)
    print("  outer cell at the junction= %.6e m, wake grading SOLVED %.6f"
          % (ds0, g_out))
    print("  semicircle plateau SOLVED = %.6e m" % dmax_o)

    # ---- per-station normal stacks ----------------------------------------
    # The wake stations' first cell relaxes from y1 at the TE (so the stack is
    # CONTINUOUS across the trailing edge) to the sheet cell height ds_te (so
    # the sheet/wake interface carries no volume jump downstream).  It is a
    # smoothstep in DOWNSTREAM DISTANCE, not in cell index: an index ramp
    # changes y1 by a fixed factor per cell, and the streamwise cells near the
    # TE are 4.17e-04 m long, which tilted the j-lines by a MEASURED 82.8 deg
    # and put 1691 faces past 70 deg non-orthogonality on the first trial.
    # MEASURED, L1, max non-orthogonality against the wake first-cell ramp
    # length (all other knobs fixed):
    #     0.5 m -> 82.1     1 m -> 77.9     2 m -> 83.8     4 m -> 86.9
    #      8 m -> 87.3      25 m -> 87.8    NO RAMP -> 34.2
    # and the max face-adjacent volume ratio is 83.47 in EVERY one of them,
    # because that maximum sits on the sheet/wake face at the trailing edge and
    # no ramp can move it.  A ramp therefore buys nothing and costs a factor 2.5
    # in non-orthogonality, so the registered construction carries NO ramp: the
    # wake stations use the wall stack unchanged, which also puts the finest
    # cells exactly on the jet sheet's shear layer.  The ramp is retained as an
    # option so the measurement above can be reproduced, never as a default.
    lnr = math.log(ds_te / y1)
    y1_st, g_st = [], []
    for i in range(Ni + 1):
        if args.wake_ramp <= 0.0:
            xw = None
        elif i <= n_wake:
            xw = x_wake[n_wake - i]
        elif i >= n_wake + 2 * n_surf:
            xw = x_wake[i - (n_wake + 2 * n_surf)]
        else:
            xw = None
        if xw is None:
            yy = y1
        else:
            x0 = CHORD + WAKE_FINE
            u = min(1.0, max(0.0, (xw - x0) / args.wake_ramp))
            yy = y1 * math.exp(lnr * u * u * (3.0 - 2.0 * u))
        gg = solve_growth(yy, Nj, R_NORMAL)
        if gg > G_CAP:
            refuse("station %d solved growth %.6f exceeds cap %.4f"
                   % (i, gg, G_CAP))
        y1_st.append(yy)
        g_st.append(gg)

    def logstep(dist, a, b):
        """smoothstep in log(distance): 0 at or below a, 1 at or above b."""
        if dist <= a:
            return 0.0
        if dist >= b:
            return 1.0
        t = math.log(dist / a) / math.log(b / a)
        return t * t * (3.0 - 2.0 * t)

    node2d = []                              # [i][j] -> (x, y)
    for i in range(Ni + 1):
        col = []
        for j in range(Nj + 1):
            d = geom_sum(y1_st[i], g_st[i], j)
            if j == Nj:
                d = R_NORMAL
            phi = logstep(d, args.phi_a, args.phi_b)
            dx = (1.0 - phi) * nrm_raw[i][0] + phi * nrm_smooth[i][0]
            dy = (1.0 - phi) * nrm_raw[i][1] + phi * nrm_smooth[i][1]
            L = math.hypot(dx, dy)
            if L <= 1e-12:
                refuse("marching direction collapsed at (%d, %d)" % (i, j))
            dx, dy = dx / L, dy / L
            w = logstep(d, args.blend_a, args.blend_b)
            ax = P2[i][0] + d * dx
            ay = P2[i][1] + d * dy
            if w == 0.0:
                col.append((ax, ay))
            else:
                f = d / R_NORMAL
                bx = P2[i][0] + f * (O2[i][0] - P2[i][0])
                by = P2[i][1] + f * (O2[i][1] - P2[i][1])
                col.append(((1.0 - w) * ax + w * bx, (1.0 - w) * ay + w * by))
        node2d.append(col)

    # ---- point list -------------------------------------------------------
    P = []
    cidx = {}
    for kz in (0, 1):
        z = (-0.5 if kz == 0 else 0.5) * t_z
        for i in range(Ni + 1):
            for j in range(Nj + 1):
                cidx[(i, j, kz)] = len(P)
                P.append((node2d[i][j][0], node2d[i][j][1], z))
    sidx = {}
    for kz in (0, 1):
        z = (-0.5 if kz == 0 else 0.5) * t_z
        for k in range(n_wake + 1):
            for m in range(1, n_sheet):
                sidx[(k, m, kz)] = len(P)
                P.append((x_wake[k], -half_h + m * (h / n_sheet), z))

    def cnode(i, j, kz):
        return cidx[(i, j, kz)]

    def snode(k, m, kz):
        """Sheet node; m == 0 and m == n_sheet REUSE the C-block nodes so the
        two blocks are conformal by index, not by coincidence of coordinates."""
        if m == n_sheet:
            return cidx[(n_wake - k, 0, kz)]
        if m == 0:
            return cidx[(n_wake + 2 * n_surf + k, 0, kz)]
        return sidx[(k, m, kz)]

    # verify the reuse really is coincident in coordinates too
    for k in (0, n_wake // 2, n_wake):
        pt = P[snode(k, n_sheet, 0)]
        if abs(pt[0] - x_wake[k]) > 1e-9 or abs(pt[1] - half_h) > 1e-9:
            refuse("sheet/C-block node reuse mismatch at k = %d" % k)

    NC = Ni * Nj

    def ccell(i, j):
        return j * Ni + i

    def scell(k, m):
        return NC + m * n_wake + k

    # ---- cells as hexahedra (8 nodes, base ccw at z-) ---------------------
    hexes = [None] * n_cells
    for j in range(Nj):
        for i in range(Ni):
            # ordered so the base quad is COUNTERCLOCKWISE in xy.  The (i, j)
            # frame of a counterclockwise inner traversal with an outward j is
            # left-handed, so the naive (i,j)(i+1,j)(i+1,j+1)(i,j+1) ordering
            # gives a uniformly NEGATIVE shoelace area and would make the fold
            # test below meaningless.
            hexes[ccell(i, j)] = (
                (cnode(i, j, 0), cnode(i, j + 1, 0),
                 cnode(i + 1, j + 1, 0), cnode(i + 1, j, 0)),
                (cnode(i, j, 1), cnode(i, j + 1, 1),
                 cnode(i + 1, j + 1, 1), cnode(i + 1, j, 1)))
    for m in range(n_sheet):
        for k in range(n_wake):
            hexes[scell(k, m)] = (
                (snode(k, m, 0), snode(k + 1, m, 0),
                 snode(k + 1, m + 1, 0), snode(k, m + 1, 0)),
                (snode(k, m, 1), snode(k + 1, m, 1),
                 snode(k + 1, m + 1, 1), snode(k, m + 1, 1)))

    ccent = []
    for hx in hexes:
        xsum = sum(P[n][0] for n in hx[0] + hx[1]) / 8.0
        ysum = sum(P[n][1] for n in hx[0] + hx[1]) / 8.0
        zsum = sum(P[n][2] for n in hx[0] + hx[1]) / 8.0
        ccent.append((xsum, ysum, zsum))

    def area_vec(f):
        c = [sum(P[n][d] for n in f) / len(f) for d in range(3)]
        ax = ay = az = 0.0
        for q in range(len(f)):
            a1 = P[f[q]]
            a2 = P[f[(q + 1) % len(f)]]
            ux, uy, uz = a1[0] - c[0], a1[1] - c[1], a1[2] - c[2]
            vx, vy, vz = a2[0] - c[0], a2[1] - c[1], a2[2] - c[2]
            ax += 0.5 * (uy * vz - uz * vy)
            ay += 0.5 * (uz * vx - ux * vz)
            az += 0.5 * (ux * vy - uy * vx)
        return (ax, ay, az), c

    def oriented(f, own, nei):
        """Return f ordered so its area vector points own -> nei (or outward)."""
        Sf, fc = area_vec(f)
        if nei is None:
            tx = fc[0] - ccent[own][0]
            ty = fc[1] - ccent[own][1]
            tz = fc[2] - ccent[own][2]
        else:
            tx = ccent[nei][0] - ccent[own][0]
            ty = ccent[nei][1] - ccent[own][1]
            tz = ccent[nei][2] - ccent[own][2]
        if Sf[0] * tx + Sf[1] * ty + Sf[2] * tz < 0.0:
            return tuple(reversed(f))
        return tuple(f)

    # ---- faces ------------------------------------------------------------
    internal = []

    def add_int(f, a, b):
        if a == b:
            refuse("internal face with identical owner and neighbour")
        o, n = (a, b) if a < b else (b, a)
        internal.append((o, n, oriented(f, o, n)))

    # C-block: i-normal faces (between i-1 and i columns), j-normal faces
    for j in range(Nj):
        for i in range(1, Ni):
            f = (cnode(i, j, 0), cnode(i, j + 1, 0),
                 cnode(i, j + 1, 1), cnode(i, j, 1))
            add_int(f, ccell(i - 1, j), ccell(i, j))
    for j in range(Nj - 1):
        for i in range(Ni):
            f = (cnode(i, j + 1, 0), cnode(i + 1, j + 1, 0),
                 cnode(i + 1, j + 1, 1), cnode(i, j + 1, 1))
            add_int(f, ccell(i, j), ccell(i, j + 1))
    # sheet block internal
    for m in range(n_sheet):
        for k in range(1, n_wake):
            f = (snode(k, m, 0), snode(k, m + 1, 0),
                 snode(k, m + 1, 1), snode(k, m, 1))
            add_int(f, scell(k - 1, m), scell(k, m))
    for m in range(n_sheet - 1):
        for k in range(n_wake):
            f = (snode(k, m + 1, 0), snode(k + 1, m + 1, 0),
                 snode(k + 1, m + 1, 1), snode(k, m + 1, 1))
            add_int(f, scell(k, m), scell(k, m + 1))
    # sheet <-> C-block, upper (m = n_sheet) and lower (m = 0) edges
    for k in range(n_wake):
        f = (snode(k, n_sheet, 0), snode(k + 1, n_sheet, 0),
             snode(k + 1, n_sheet, 1), snode(k, n_sheet, 1))
        add_int(f, scell(k, n_sheet - 1), ccell(n_wake - 1 - k, 0))
        f = (snode(k, 0, 0), snode(k + 1, 0, 0),
             snode(k + 1, 0, 1), snode(k, 0, 1))
        add_int(f, scell(k, 0), ccell(n_wake + 2 * n_surf + k, 0))

    internal.sort(key=lambda t: (t[0], t[1]))
    faces = [t[2] for t in internal]
    owner = [t[0] for t in internal]
    neigh = [t[1] for t in internal]

    airfoil_f, slot_f, far_f, back_f, front_f = [], [], [], [], []
    for i in range(n_wake, n_wake + 2 * n_surf):     # airfoil wall, j = 0
        f = (cnode(i, 0, 0), cnode(i + 1, 0, 0),
             cnode(i + 1, 0, 1), cnode(i, 0, 1))
        airfoil_f.append(oriented(f, ccell(i, 0), None))
    for m in range(n_sheet):                          # jetSlot, k = 0 plane
        f = (snode(0, m, 0), snode(0, m + 1, 0),
             snode(0, m + 1, 1), snode(0, m, 1))
        slot_f.append(oriented(f, scell(0, m), None))
    for i in range(Ni):                               # outer C boundary
        f = (cnode(i, Nj, 0), cnode(i + 1, Nj, 0),
             cnode(i + 1, Nj, 1), cnode(i, Nj, 1))
        far_f.append(oriented(f, ccell(i, Nj - 1), None))
    for j in range(Nj):                               # outlet, i = 0 plane
        f = (cnode(0, j, 0), cnode(0, j + 1, 0),
             cnode(0, j + 1, 1), cnode(0, j, 1))
        far_f.append(oriented(f, ccell(0, j), None))
    for j in range(Nj):                               # outlet, i = Ni plane
        f = (cnode(Ni, j, 0), cnode(Ni, j + 1, 0),
             cnode(Ni, j + 1, 1), cnode(Ni, j, 1))
        far_f.append(oriented(f, ccell(Ni - 1, j), None))
    for m in range(n_sheet):                          # outlet, sheet end
        f = (snode(n_wake, m, 0), snode(n_wake, m + 1, 0),
             snode(n_wake, m + 1, 1), snode(n_wake, m, 1))
        far_f.append(oriented(f, scell(n_wake - 1, m), None))
    for ci, hx in enumerate(hexes):                   # empty front/back
        back_f.append(oriented(hx[0], ci, None))
        front_f.append(oriented(hx[1], ci, None))

    patches = [("jetSlot", "patch", slot_f),
               ("airfoil", "wall", airfoil_f),
               ("farfield", "patch", far_f),
               ("back", "empty", back_f),
               ("front", "empty", front_f)]

    all_faces = list(faces)
    all_owner = list(owner)
    for _, _, fl in patches:
        all_faces += list(fl)
    for name, _, fl in patches:
        if name == "jetSlot":
            all_owner += [scell(0, m) for m in range(n_sheet)]
        elif name == "airfoil":
            all_owner += [ccell(i, 0)
                          for i in range(n_wake, n_wake + 2 * n_surf)]
        elif name == "farfield":
            all_owner += [ccell(i, Nj - 1) for i in range(Ni)]
            all_owner += [ccell(0, j) for j in range(Nj)]
            all_owner += [ccell(Ni - 1, j) for j in range(Nj)]
            all_owner += [scell(n_wake - 1, m) for m in range(n_sheet)]
        else:
            all_owner += list(range(n_cells))
    if len(all_owner) != len(all_faces):
        refuse("owner/face count mismatch: %d vs %d"
               % (len(all_owner), len(all_faces)))

    # ---- measured metrics, computed here and NOT taken on trust -----------
    # SIGNED areas, deliberately.  Taking abs() here would report a healthy
    # positive volume for a FOLDED (inverted) cell -- a nominal answer for an
    # identity never verified, which is the F28 defect class applied to the
    # generator's own self-check.  Measured on the first trial of this script,
    # abs() concealed 141 inverted cells at the concave trailing-edge corner
    # that checkMesh then found as open cells.
    vol = []
    nfold = 0
    fold_at = None
    for ci, hx in enumerate(hexes):
        quad = [(P[n][0], P[n][1]) for n in hx[0]]
        a = poly_area(quad)
        if a <= 0.0:
            nfold += 1
            if fold_at is None:
                fold_at = ci
        vol.append(a * t_z)
    if nfold:
        refuse("%d cells are folded or degenerate (first: cell %d, signed "
               "volume %.6e m3).  The grid lines cross; no gate may rest on "
               "this level." % (nfold, fold_at, vol[fold_at]))
    vr = 1.0
    vr_at = None
    for o, n, _ in internal:
        r = max(vol[o], vol[n]) / min(vol[o], vol[n])
        if r > vr:
            vr, vr_at = r, (o, n)
    # aspect ratio, OpenFOAM's 2-D definition: max/min over the x,y components
    # of sum|Sf| per cell (primitiveMeshTools::cellClosedness; the empty z
    # direction is excluded from meshD, so t_z cannot enter this number)
    sabs = [[0.0, 0.0] for _ in range(n_cells)]
    for fi, f in enumerate(all_faces):
        Sf, _ = area_vec(f)
        c = all_owner[fi]
        sabs[c][0] += abs(Sf[0])
        sabs[c][1] += abs(Sf[1])
        if fi < len(neigh):
            c2 = neigh[fi]
            sabs[c2][0] += abs(Sf[0])
            sabs[c2][1] += abs(Sf[1])
    ar = [max(a) / min(a) if min(a) > 0 else float("inf") for a in sabs]
    ar_max = max(ar)
    ar_mean = sum(ar) / len(ar)
    # WHERE the anisotropy sits, by region.  Section 4.5's registered alignment
    # justification is that the anisotropy is WALL-NORMAL, aligned with the
    # direction being resolved.  That claim is only honest where a wall or a
    # shear layer is being resolved, so the maximum is reported per region and
    # the certificate states which region carries it.
    # OpenFOAM's aspect ratio is a ratio of CARTESIAN COMPONENTS of sum|Sf|, so
    # an inclined thin cell reports far lower than its true shape: a mid-chord
    # first-layer cell here is 2.9e-02 m by 5.0e-06 m -- a true 5800 -- and
    # OpenFOAM scores it 31.5, because the 1.8 deg surface slope leaks 0.029 x
    # sin(1.8 deg) into the x component.  The TRUE geometric aspect ratio is
    # therefore computed and reported alongside; nothing gates either.
    tar = []
    for hx in hexes:
        q = [(P[n][0], P[n][1]) for n in hx[0]]
        e = [math.hypot(q[(k + 1) % 4][0] - q[k][0], q[(k + 1) % 4][1] - q[k][1])
             for k in range(4)]
        tar.append(max(e) / min(e))
    tar_max = max(tar)
    tar_wall = max(tar[ccell(i, 0)] for i in range(n_wake, n_wake + 2 * n_surf))
    ar_wall = max(ar[ccell(i, 0)] for i in range(n_wake, n_wake + 2 * n_surf))
    ar_surfblk = max(ar[ccell(i, j)]
                     for i in range(n_wake, n_wake + 2 * n_surf)
                     for j in range(Nj))
    ar_sheet = max(ar[scell(k, m)]
                   for k in range(n_wake) for m in range(n_sheet))
    nfine = nA
    ar_wfine = max(ar[ccell(n_wake - 1 - k, j)]
                   for k in range(nfine) for j in range(Nj))
    ar_wfar = max(ar[ccell(n_wake - 1 - k, j)]
                  for k in range(nfine, n_wake) for j in range(Nj))

    # ACHIEVED first-cell wall spacing along the airfoil: constant, or varying?
    # MEASURED, per wall face, as the PERPENDICULAR distance from the wall face
    # to the opposite face of the first cell -- not the along-the-marching-
    # direction distance, which would flatter any tilt in the direction field.
    # F28's radial distribution was a RATIO applied to rows of differing height
    # and its achieved wall spacing varied 1.0e-05 to 1.53e-05; this is the
    # check that would have caught that.
    fch, fcc = [], []
    for i in range(n_wake, n_wake + 2 * n_surf):
        ax, ay = node2d[i][0]
        bx, by = node2d[i + 1][0]
        tx, ty = bx - ax, by - ay
        L = math.hypot(tx, ty)
        nx, ny = ty / L, -tx / L            # outward face normal
        # opposite face of the first cell, midpoint
        ox = 0.5 * (node2d[i][1][0] + node2d[i + 1][1][0])
        oy = 0.5 * (node2d[i][1][1] + node2d[i + 1][1][1])
        mx, my = 0.5 * (ax + bx), 0.5 * (ay + by)
        fch.append((ox - mx) * nx + (oy - my) * ny)
        cc = ccent[ccell(i, 0)]
        fcc.append((cc[0] - mx) * nx + (cc[1] - my) * ny)
    # slot area, measured from the emitted faces
    slot_area = 0.0
    for f in slot_f:
        Sf, _ = area_vec(f)
        slot_area += math.sqrt(Sf[0] ** 2 + Sf[1] ** 2 + Sf[2] ** 2)

    print("\n-- MEASURED FROM THE EMITTED POINT SET --")
    print("  cells                            = %d" % n_cells)
    print("  points                           = %d" % len(P))
    print("  internal faces                   = %d" % len(internal))
    print("  total faces                      = %d" % len(all_faces))
    print("  min cell volume                  = %.6e m3" % min(vol))
    print("  max face-adjacent volume ratio   = %.4f   (cells %s)"
          % (vr, vr_at))
    print("  max aspect ratio (OF 2-D defn)   = %.1f" % ar_max)
    print("  mean aspect ratio                = %.1f" % ar_mean)
    print("    of which: airfoil first layer  = %.1f" % ar_wall)
    print("              airfoil block (all j)= %.1f" % ar_surfblk)
    print("              jet-sheet block      = %.1f" % ar_sheet)
    print("              wake, inside the 3c box = %.1f" % ar_wfine)
    print("              wake, BEYOND the 3c box = %.1f  <-- carries the max"
          % ar_wfar)
    print("  TRUE geometric aspect ratio      max %.1f, airfoil first layer %.1f"
          % (tar_max, tar_wall))
    print("  ACHIEVED wall spacing (perp)     min %.9e  max %.9e  spread %.4f%%"
          % (min(fch), max(fch), 100.0 * (max(fch) / min(fch) - 1.0)))
    print("  first cell-CENTRE wall distance  min %.9e  max %.9e"
          % (min(fcc), max(fcc)))
    print("  t_z used                         = %.9e m" % t_z)
    print("  area(jetSlot) MEASURED           = %.9e m2" % slot_area)
    print("  section 7.4 cross-check vs 0.005 m2 to 1e-9: %s"
          % ("PASS" if abs(slot_area - 0.005) <= 1e-9
             else "WOULD REFUSE (exit 2)"))

    if args.diagnostic_tz is not None:
        dz = args.diagnostic_tz
        print("\n-- DIAGNOSTIC ONLY, NOTHING WRITTEN AT THIS t_z --")
        print("  t_z = %.9e -> area(jetSlot) = %.9e m2, section 7.4 %s"
              % (dz, slot_area * dz / t_z,
                 "PASS" if abs(slot_area * dz / t_z - 0.005) <= 1e-9
                 else "WOULD REFUSE"))
        print("  max aspect ratio is UNCHANGED at %.1f: OpenFOAM's 2-D aspect "
              "ratio takes only the meshD directions, and the span is empty."
              % ar_max)
        print("  max face-adjacent volume ratio is UNCHANGED at %.4f: t_z is a "
              "common factor of every cell volume." % vr)

    # ---- write ------------------------------------------------------------
    outdir = os.path.join(args.out, "constant", "polyMesh")
    write_polymesh(outdir, P, all_faces, all_owner, neigh, patches)
    md5 = hashlib.md5(open(__file__, "rb").read()).hexdigest()
    print("\n-- WRITTEN --")
    print("  %s" % outdir)
    print("  patches: jetSlot %d | airfoil %d | farfield %d | back %d | front %d"
          % (len(slot_f), len(airfoil_f), len(far_f), len(back_f),
             len(front_f)))
    print("  script md5 = %s   scale s = %.4f   level %s"
          % (md5, s, args.level))
    print("=" * 78)


def _cell_at(d, target):
    """Length of the wake cell containing the station `target` m aft of the TE."""
    acc = 0.0
    for v in d:
        acc += v
        if acc >= target:
            return v
    return d[-1]


if __name__ == "__main__":
    main()
