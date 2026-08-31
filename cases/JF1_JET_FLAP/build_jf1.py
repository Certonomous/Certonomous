#!/usr/bin/env python3
"""
JF1 JET-FLAP AIRFOIL -- ONE PARAMETRIC MESH SCRIPT.  FEASIBILITY LABEL.

This script emits a complete constant/polyMesh for a 2-D, one-cell-thick
O-topology grid around a NACA 0012 truncated to a blunt trailing-edge base of
height h, with the base carried as its own patch (`jetSlot`).  It is driven by a
single level scale factor; NO LEVEL IS EVER HAND-EDITED.

LABEL: feasibility.  No gate, threshold or verdict of the fixed vocabulary
attaches to any mesh this script emits under the L1 feasibility dispatch of
2026-08-31.  It computes no GCI and no observed order.

Topology (recorded choice, Sanaa CASE 1 section 1.2 "record which"):
    O-MESH, farfield a circle of radius R_far about the quarter chord.
    The O-mesh is chosen for the L1 FEASIBILITY run only.  It does NOT satisfy
    section 1.3's wake-refinement requirement ("a box 3c long behind the TE at
    BL-comparable spacing"); an O-mesh coarsens circumferentially with radius.
    A C-topology is required before any gated / blown row.  This limitation is
    printed by the script itself so it cannot be lost.

Index frame: i = tangential (CLOCKWISE around the section, so that
t x n = +z and (i,j,k) is right-handed), j = wall-normal outward, k = +z span.
"""

import argparse
import math
import os
import sys

# ----------------------------------------------------------------------------
# Section 1.  Registered physical inputs (Sanaa CASE 1 sections 1.1-1.4)
# ----------------------------------------------------------------------------
CHORD = 1.0            # c, m
H_OVER_C = 0.005       # slot / base height h/c
U_INF = 10.0           # m/s
NU = 1.0e-5            # m^2/s   -> Re_c = 1.0e6
RE_C = U_INF * CHORD / NU

# NACA 0012 half-thickness (open-TE coefficient set)
NACA_T = 0.12


def naca_yt(x):
    """Half-thickness of a NACA 00tt at chordwise station x in [0,1]."""
    return 5.0 * NACA_T * (0.2969 * math.sqrt(x)
                           - 0.1260 * x
                           - 0.3516 * x * x
                           + 0.2843 * x ** 3
                           - 0.1015 * x ** 4)


def solve_truncation(half_h_over_c, lo=0.90, hi=0.99999, tol=1e-14):
    """
    Find x_te such that, AFTER rescaling the section by 1/x_te so the truncated
    body has chord exactly 1, the base half-height equals half_h_over_c.
    That is: yt(x_te) / x_te = half_h_over_c.
    """
    def f(x):
        return naca_yt(x) / x - half_h_over_c
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        raise SystemExit("truncation bracket failed: f(lo)=%g f(hi)=%g" % (flo, fhi))
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------------------
# Section 2.  Geometric stacks
# ----------------------------------------------------------------------------
def geom_sum(y1, g, n):
    """Total height of n geometric cells starting at y1 with ratio g."""
    if abs(g - 1.0) < 1e-15:
        return y1 * n
    return y1 * (g ** n - 1.0) / (g - 1.0)


def solve_growth(y1, n, total, lo=1.0 + 1e-12, hi=2.0, tol=1e-15):
    """Solve geometric ratio g so that n cells from y1 stack exactly to total."""
    if geom_sum(y1, lo, n) > total:
        raise SystemExit("even g=1 overshoots: need fewer cells or smaller y1")
    if geom_sum(y1, hi, n) < total:
        raise SystemExit("g=2 undershoots: need more cells")
    for _ in range(500):
        mid = 0.5 * (lo + hi)
        if geom_sum(y1, mid, n) < total:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


def min_count_for_cap(y1, total, gcap):
    """Smallest integer N whose SOLVED g satisfies g <= gcap."""
    n = int(math.ceil(math.log(1.0 + (total / y1) * (gcap - 1.0)) / math.log(gcap)))
    while geom_sum(y1, gcap, n) < total:
        n += 1
    return n


def layers_inside(y1, g, delta):
    """Number of COMPLETE geometric layers whose cumulative stack is <= delta."""
    n, s = 0, 0.0
    while True:
        s_next = s + y1 * g ** n
        if s_next > delta:
            return n
        s = s_next
        n += 1
        if n > 100000:
            return n


def two_sided_spacing(n, total, ds_a, ds_b, ratio):
    """
    n interval sizes summing EXACTLY to total, first = ds_a, last = ds_b,
    growing geometrically at `ratio` from each end and capped by a plateau
    ds_max which is SOLVED so the sum closes.  Local growth never exceeds
    `ratio`, so the tangential growth cap is a property of construction.
    """
    def build(dmax):
        d = []
        for k in range(n):
            d.append(min(ds_a * ratio ** k, ds_b * ratio ** (n - 1 - k), dmax))
        return d

    lo, hi = max(ds_a, ds_b), total  # dmax bracket
    if sum(build(lo)) > total:
        # cannot close even with no plateau -> fall back to proportional scale
        d = build(lo)
        s = sum(d)
        return [v * total / s for v in d], lo, s / total
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if sum(build(mid)) < total:
            lo = mid
        else:
            hi = mid
    dmax = 0.5 * (lo + hi)
    d = build(dmax)
    s = sum(d)
    d = [v * total / s for v in d]          # residual closure, |correction| ~1e-12
    return d, dmax, s / total


# ----------------------------------------------------------------------------
# Section 3.  Surface point set
# ----------------------------------------------------------------------------
def surface_points(n_base, n_low, n_up, ds_te, ds_le, tang_ratio, verbose):
    """
    Return (pts, seg_is_slot) walking CLOCKWISE:
      base  : (1, +h/2) -> (1, -h/2)          n_base intervals
      lower : (1, -h/2) -> (0, 0)             n_low intervals
      upper : (0, 0)    -> (1, +h/2)          n_up  intervals
    pts has Ni entries (the closing point is pts[0], not repeated).
    """
    half_h = 0.5 * H_OVER_C * CHORD
    x_te = solve_truncation(half_h / CHORD)
    scale = CHORD / x_te

    # dense arc-length table of the scaled upper surface, LE -> TE
    m = 40000
    xs, ys, ss = [], [], [0.0]
    for q in range(m + 1):
        # cosine clustering of the raw table towards both ends (table only)
        xi = 0.5 * (1.0 - math.cos(math.pi * q / m)) * x_te
        xs.append(xi * scale)
        ys.append(naca_yt(xi) * scale)
    for q in range(1, m + 1):
        ss.append(ss[-1] + math.hypot(xs[q] - xs[q - 1], ys[q] - ys[q - 1]))
    S = ss[-1]

    def at_arc(s):
        """Point on the scaled upper surface at arc length s from the LE."""
        s = min(max(s, 0.0), S)
        lo, hi = 0, m
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if ss[mid] <= s:
                lo = mid
            else:
                hi = mid
        f = 0.0 if ss[hi] == ss[lo] else (s - ss[lo]) / (ss[hi] - ss[lo])
        return (xs[lo] + f * (xs[hi] - xs[lo]), ys[lo] + f * (ys[hi] - ys[lo]))

    # tangential distributions
    d_up, dmax_up, res_up = two_sided_spacing(n_up, S, ds_le, ds_te, tang_ratio)
    d_low = list(reversed(d_up)) if n_low == n_up else \
        two_sided_spacing(n_low, S, ds_te, ds_le, tang_ratio)[0]

    pts, is_slot = [], []

    # base, top corner -> bottom corner, uniform
    for q in range(n_base):
        t = q / float(n_base)
        pts.append((CHORD, half_h - 2.0 * half_h * t))
        is_slot.append(True)

    # lower surface, TE corner -> LE  (mirror of the upper table)
    s = S
    for q in range(n_low):
        x, y = at_arc(s)
        pts.append((x, -y))
        is_slot.append(False)
        s -= d_low[q]

    # upper surface, LE -> TE corner (last point is the TE-upper corner = pts[0])
    s = 0.0
    for q in range(n_up):
        x, y = at_arc(s)
        pts.append((x, y))
        is_slot.append(False)
        s += d_up[q]

    if verbose:
        print("  truncation station x_te            = %.9f c (raw NACA table)" % x_te)
        print("  rescale factor 1/x_te              = %.9f" % scale)
        print("  base half-height after rescale     = %.9e m  (target %.9e)"
              % (naca_yt(x_te) * scale, half_h))
        print("  one-side surface arc length S      = %.9f m" % S)
        print("  tangential plateau ds_max          = %.6e m (solved), closure residual %.3e"
              % (dmax_up, abs(res_up - 1.0)))
    return pts, is_slot, S, x_te, scale


def nodal_normals(pts, n_smooth):
    """Outward unit normals at each node = normalised mean of adjacent segment
    normals (clockwise traversal -> outward normal is t rotated by -90 deg),
    then n_smooth Jacobi passes so a convex corner's turn is shared."""
    ni = len(pts)
    seg = []
    for i in range(ni):
        j = (i + 1) % ni
        tx, ty = pts[j][0] - pts[i][0], pts[j][1] - pts[i][1]
        L = math.hypot(tx, ty)
        # CLOCKWISE traversal: the OUTWARD normal is t rotated by +90 deg,
        # (x,y) -> (-y,x).  Rotating by -90 gives the INWARD normal and marches
        # the grid into the body (measured: 27 537 negative-volume cells).
        seg.append((-ty / L, tx / L))
    nrm = []
    for i in range(ni):
        a, b = seg[(i - 1) % ni], seg[i]
        vx, vy = a[0] + b[0], a[1] + b[1]
        L = math.hypot(vx, vy)
        nrm.append((vx / L, vy / L))
    for _ in range(n_smooth):
        new = []
        for i in range(ni):
            a, b, c = nrm[(i - 1) % ni], nrm[i], nrm[(i + 1) % ni]
            vx = 0.25 * a[0] + 0.5 * b[0] + 0.25 * c[0]
            vy = 0.25 * a[1] + 0.5 * b[1] + 0.25 * c[1]
            L = math.hypot(vx, vy)
            new.append((vx / L, vy / L))
        nrm = new
    return nrm


# ----------------------------------------------------------------------------
# Section 4.  polyMesh writer
# ----------------------------------------------------------------------------
HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
| JF1 jet-flap airfoil -- generated by cases/JF1_JET_FLAP/build_jf1.py         |
| FEASIBILITY MESH.  No gate attaches to it.                                  |
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


def write_polymesh(outdir, P, faces_int, owner, neigh, patches, nPoints, nCells):
    os.makedirs(outdir, exist_ok=True)
    nInt = len(faces_int)
    nFaces = nInt + sum(len(f) for _, _, f in patches)

    with open(os.path.join(outdir, "points"), "w") as fh:
        fh.write(HEADER % ("vectorField", "points"))
        fh.write("\n%d\n(\n" % nPoints)
        fh.write("".join("(%.10g %.10g %.10g)\n" % p for p in P))
        fh.write(")\n")

    with open(os.path.join(outdir, "faces"), "w") as fh:
        fh.write(HEADER % ("faceList", "faces"))
        fh.write("\n%d\n(\n" % nFaces)
        out = []
        for f in faces_int:
            out.append("4(%d %d %d %d)\n" % f)
        for _, _, fl in patches:
            for f in fl:
                out.append("4(%d %d %d %d)\n" % f)
        fh.write("".join(out))
        fh.write(")\n")

    own = list(owner)
    with open(os.path.join(outdir, "owner"), "w") as fh:
        fh.write(HEADER % ("labelList", "owner"))
        fh.write("\n%d\n(\n" % len(own))
        fh.write("".join("%d\n" % v for v in own))
        fh.write(")\n")

    with open(os.path.join(outdir, "neighbour"), "w") as fh:
        fh.write(HEADER % ("labelList", "neighbour"))
        fh.write("\n%d\n(\n" % len(neigh))
        fh.write("".join("%d\n" % v for v in neigh))
        fh.write(")\n")

    with open(os.path.join(outdir, "boundary"), "w") as fh:
        fh.write(HEADER % ("polyBoundaryMesh", "boundary"))
        fh.write("\n%d\n(\n" % len(patches))
        start = nInt
        for name, ptype, fl in patches:
            fh.write("    %s\n    {\n        type            %s;\n" % (name, ptype))
            if ptype == "wall":
                fh.write("        inGroups        1(wall);\n")
            elif ptype == "empty":
                fh.write("        inGroups        1(empty);\n")
            fh.write("        nFaces          %d;\n        startFace       %d;\n    }\n"
                     % (len(fl), start))
            start += len(fl)
        fh.write(")\n")


# ----------------------------------------------------------------------------
# Section 5.  Driver
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="case directory (writes <out>/constant/polyMesh)")
    ap.add_argument("--level", default="L1")
    ap.add_argument("--scale", type=float, default=1.0,
                    help="ladder scale s: counts x s, spacings / s")
    ap.add_argument("--n-base", type=int, default=12, help="cells across the slot height h")
    ap.add_argument("--n-side", type=int, default=198, help="cells per surface side")
    ap.add_argument("--n-rad", type=int, default=0, help="0 = solve from the growth cap")
    ap.add_argument("--y1", type=float, default=5.0e-06, help="first-cell HEIGHT, m")
    ap.add_argument("--g-cap", type=float, default=1.15)
    ap.add_argument("--r-far", type=float, default=26.0, help="farfield radius about c/4, m")
    ap.add_argument("--span", type=float, default=0.01, help="one-cell span thickness, m")
    ap.add_argument("--tang-ratio", type=float, default=1.12)
    ap.add_argument("--ds-le", type=float, default=2.0e-04)
    # 500 is MEASURED, not guessed: a checkMesh sweep on this exact geometry
    # (2026-08-31) gave max non-orthogonality 78.7 / 73.1 / 66.1 / 64.0 / 62.2 /
    # 59.0 / 58.5 / 61.9 / 67.3 at 60 / 120 / 250 / 300 / 350 / 450 / 550 / 800 /
    # 1600 passes.  Too little smoothing leaves the blunt-TE corner turn on one
    # node; too much tilts the wall-normal marching direction away from the wall.
    # The minimum is broad and flat near 500.
    ap.add_argument("--normal-smooth", type=int, default=500)
    ap.add_argument("--blend-a", type=float, default=0.10)
    ap.add_argument("--blend-b", type=float, default=3.00)
    ap.add_argument("--slot-type", choices=["wall", "patch"], default="wall",
                    help="polyMesh patch type of jetSlot; UNBLOWN run uses wall")
    args = ap.parse_args()

    s = args.scale
    n_base = int(round(args.n_base * s))
    n_side = int(round(args.n_side * s))
    y1 = args.y1 / s
    R = args.r_far

    print("=" * 78)
    print("JF1 MESH BUILD -- level %s, scale %.4f -- LABEL: feasibility" % (args.level, s))
    print("=" * 78)
    print("Re_c = %.4g, c = %g m, U_inf = %g m/s, nu = %g m2/s, h/c = %g"
          % (RE_C, CHORD, U_INF, NU, H_OVER_C))

    # --- near-wall arithmetic, shown ---------------------------------------
    delta = 0.37 * CHORD * RE_C ** -0.2
    cf_c = 0.0576 * RE_C ** -0.2
    utau_c = U_INF * math.sqrt(cf_c / 2.0)
    y1_at_c = NU / utau_c
    print("\n-- NEAR-WALL DISTRIBUTION, ARITHMETIC SHOWN --")
    print("  delta(x=c) = 0.37 c Re^-0.2        = %.6e m" % delta)
    print("  Cf(x=c)    = 0.0576 Re^-0.2        = %.6e" % cf_c)
    print("  u_tau(x=c) = U sqrt(Cf/2)          = %.6f m/s" % utau_c)
    print("  y1 for y+=1 AT x=c                 = %.6e m   <-- the MINIMUM-u_tau station" % y1_at_c)
    print("  y1 REGISTERED (level %-3s)          = %.6e m" % (args.level, y1))
    print("     ratio y1_registered / y1(x=c)   = %.4f  (margin against the LE peak)" % (y1 / y1_at_c))

    if args.n_rad > 0:
        n_rad = int(round(args.n_rad * s))
    else:
        n_rad = min_count_for_cap(y1, R, args.g_cap)
    g = solve_growth(y1, n_rad, R)
    reached = geom_sum(y1, g, n_rad)
    n_in_delta = layers_inside(y1, g, delta)
    g_at_nminus1 = None
    try:
        g_at_nminus1 = solve_growth(y1, n_rad - 1, R)
    except SystemExit:
        pass

    print("  farfield radius about c/4          = %.4f m" % R)
    print("     min body-to-farfield distance   = %.4f c  (TE is 0.75 c from c/4)" % (R - 0.75))
    print("  N_rad SOLVED from the cap          = %d" % n_rad)
    print("     (N-1 = %d would need g = %s -- ABOVE the %.4f cap)"
          % (n_rad - 1, ("%.6f" % g_at_nminus1) if g_at_nminus1 else "n/a", args.g_cap))
    print("  g SOLVED from y1*(g^N-1)/(g-1) = R = %.6f   <= %.4f  ? %s"
          % (g, args.g_cap, "YES" if g <= args.g_cap else "NO"))
    print("  stack reaches                      = %.9f m  (target %.9f, residual %.2e)"
          % (reached, R, abs(reached - R)))
    print("  last cell height                   = %.6e m" % (y1 * g ** (n_rad - 1)))
    print("  COMPLETE layers inside delta       = %d   (floor 30 -> %s)"
          % (n_in_delta, "MET" if n_in_delta >= 30 else "NOT MET"))
    if g > args.g_cap or n_in_delta < 30:
        sys.exit("REFUSED: registered near-wall constraints do not close")

    # --- tangential --------------------------------------------------------
    ds_te = (H_OVER_C * CHORD) / n_base
    ds_le = args.ds_le / s
    print("\n-- TANGENTIAL DISTRIBUTION --")
    print("  cells across the slot height h     = %d   (floor 12 -> %s)"
          % (n_base, "MET" if n_base >= 12 else "NOT MET"))
    print("  base cell size h/n_base            = %.6e m" % ds_te)
    print("  surface spacing AT THE TE          = %.6e m  (matched to the base cell)" % ds_te)
    print("  surface spacing AT THE LE          = %.6e m" % ds_le)
    print("  tangential growth cap              = %.4f" % args.tang_ratio)
    if n_base < 12:
        sys.exit("REFUSED: fewer than 12 cells across h")

    pts2d, is_slot, S_arc, x_te, sc = surface_points(
        n_base, n_side, n_side, ds_te, ds_le, args.tang_ratio, verbose=True)
    Ni = len(pts2d)
    Nj = n_rad
    nCells = Ni * Nj
    print("\n  Ni (tangential) = %d  =  %d base + %d lower + %d upper"
          % (Ni, n_base, n_side, n_side))
    print("  Nj (normal)     = %d" % Nj)
    print("  CELLS           = Ni x Nj x 1 = %d" % nCells)

    # --- node positions ----------------------------------------------------
    nrm = nodal_normals(pts2d, args.normal_smooth)
    cx, cy = 0.25 * CHORD, 0.0
    th_s = []
    prev = None
    for i in range(Ni):
        a = math.atan2(pts2d[i][1] - cy, pts2d[i][0] - cx)
        if prev is not None:                       # make monotone decreasing
            while a > prev:
                a -= 2.0 * math.pi
        th_s.append(a)
        prev = a
    th0 = th_s[0]
    th_u = [th0 - 2.0 * math.pi * i / Ni for i in range(Ni)]

    d = [0.0] * (Nj + 1)
    for j in range(1, Nj + 1):
        d[j] = geom_sum(y1, g, j)
    d[Nj] = R

    def blend(dist):
        if dist <= args.blend_a:
            return 0.0
        if dist >= args.blend_b:
            return 1.0
        t = (dist - args.blend_a) / (args.blend_b - args.blend_a)
        return t * t * (3.0 - 2.0 * t)

    half_span = 0.5 * args.span
    P = []
    for k in (0, 1):
        z = -half_span if k == 0 else half_span
        for j in range(Nj + 1):
            w = blend(d[j])
            for i in range(Ni):
                ix = pts2d[i][0] + d[j] * nrm[i][0]
                iy = pts2d[i][1] + d[j] * nrm[i][1]
                if w == 0.0:
                    P.append((ix, iy, z))
                else:
                    th = (1.0 - w) * th_s[i] + w * th_u[i]
                    ox = cx + d[j] * math.cos(th)
                    oy = cy + d[j] * math.sin(th)
                    P.append(((1.0 - w) * ix + w * ox,
                              (1.0 - w) * iy + w * oy, z))
    nPoints = len(P)

    def pt(i, j, k):
        return k * Ni * (Nj + 1) + j * Ni + (i % Ni)

    def cell(i, j):
        return j * Ni + (i % Ni)

    # --- faces -------------------------------------------------------------
    internal = []
    for j in range(Nj):
        for i in range(Ni):
            ip = (i + 1) % Ni
            a, b = cell(i, j), cell(ip, j)
            f = (pt(ip, j, 0), pt(ip, j + 1, 0), pt(ip, j + 1, 1), pt(ip, j, 1))
            if a < b:
                internal.append((a, b, f))
            else:
                internal.append((b, a, tuple(reversed(f))))
    for j in range(Nj - 1):
        for i in range(Ni):
            ip = (i + 1) % Ni
            f = (pt(i, j + 1, 0), pt(i, j + 1, 1), pt(ip, j + 1, 1), pt(ip, j + 1, 0))
            internal.append((cell(i, j), cell(i, j + 1), f))
    internal.sort(key=lambda t: (t[0], t[1]))
    faces_int = [t[2] for t in internal]
    owner = [t[0] for t in internal]
    neigh = [t[1] for t in internal]

    slot_f, wall_f, far_f, back_f, front_f = [], [], [], [], []
    for i in range(Ni):
        ip = (i + 1) % Ni
        f = (pt(ip, 0, 0), pt(ip, 0, 1), pt(i, 0, 1), pt(i, 0, 0))
        (slot_f if is_slot[i] else wall_f).append(f)
    for i in range(Ni):
        ip = (i + 1) % Ni
        far_f.append((pt(i, Nj, 0), pt(i, Nj, 1), pt(ip, Nj, 1), pt(ip, Nj, 0)))
    for j in range(Nj):
        for i in range(Ni):
            ip = (i + 1) % Ni
            back_f.append((pt(i, j + 1, 0), pt(ip, j + 1, 0), pt(ip, j, 0), pt(i, j, 0)))
            front_f.append((pt(i, j, 1), pt(ip, j, 1), pt(ip, j + 1, 1), pt(i, j + 1, 1)))

    owner_all = list(owner)
    owner_all += [cell(i, 0) for i in range(Ni) if is_slot[i]]
    owner_all += [cell(i, 0) for i in range(Ni) if not is_slot[i]]
    owner_all += [cell(i, Nj - 1) for i in range(Ni)]
    owner_all += [cell(i, j) for j in range(Nj) for i in range(Ni)]
    owner_all += [cell(i, j) for j in range(Nj) for i in range(Ni)]

    patches = [("jetSlot", args.slot_type, slot_f),
               ("airfoil", "wall", wall_f),
               ("farfield", "patch", far_f),
               ("back", "empty", back_f),
               ("front", "empty", front_f)]

    outdir = os.path.join(args.out, "constant", "polyMesh")
    write_polymesh(outdir, P, faces_int, owner_all, neigh, patches, nPoints, nCells)

    print("\n-- POLYMESH WRITTEN --")
    print("  %s" % outdir)
    print("  points %d   cells %d   internal faces %d   total faces %d"
          % (nPoints, nCells, len(faces_int),
             len(faces_int) + sum(len(f) for _, _, f in patches)))
    print("  patches: jetSlot(%s) %d | airfoil(wall) %d | farfield(patch) %d | "
          "back(empty) %d | front(empty) %d"
          % (args.slot_type, len(slot_f), len(wall_f), len(far_f),
             len(back_f), len(front_f)))
    print("\n-- RECORDED CHOICES (Sanaa CASE 1 sections 1.2/1.3 'record which') --")
    print("  topology            : O-MESH (NOT C-mesh)")
    print("  farfield            : circle radius %.2f c about the quarter chord" % R)
    print("  jetSlot patch type  : %s   (UNBLOWN run: the base is treated as a %s)"
          % (args.slot_type, "SOLID WALL, noSlip" if args.slot_type == "wall" else "flow patch"))
    print("  span                : %g m, one cell, front/back empty" % args.span)
    print("  KNOWN LIMITATION, PRINTED SO IT CANNOT BE LOST: an O-mesh does NOT")
    print("  satisfy section 1.3's wake box (3 c at BL-comparable spacing).  This")
    print("  mesh is admissible for the UNBLOWN feasibility row ONLY.")
    print("=" * 78)


if __name__ == "__main__":
    main()
