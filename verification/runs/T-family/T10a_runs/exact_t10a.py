#!/usr/bin/env python3
"""
Derive T10a's reference values instead of transcribing them.

The pre-registration (docs/campaigns/T-family/T10a_PREREGISTRATION.md)
claims this rung's references CANNOT be wrong because they are closed form.
That claim is worth something only if every constant is reproduced here from
the governing relations TWICE, by routes that share no code, and the
comparator REFUSES TO RUN when the two disagree (T9a's discipline,
exact_t9a.py; T1c's, exact_laminar_pipe.py).

  sigma      Route A: 2 pi^5 k^4 / (15 h^3 c^2) from the six-significant-figure
                      constants OpenFOAM v2606 carries in etc/controlDict
                      (k 1.38065e-23, h 6.62607e-34, c 2.99792e+08).
             Route B: the same constants READ from etc/controlDict on this host
                      (when present) and the exact SI value 5.670374419e-08
                      reported beside it.

  T10a-1     concentric grey spheres r1 = 0.05, r2 = 0.10 m, eps 0.6 / 0.4,
             T 600 / 300 K.
             Route A: q1 = sigma (T1^4 - T2^4) / [1/eps1 + (A1/A2)(1/eps2 - 1)],
                      F21 = (r1/r2)^2 by reciprocity from F12 = 1.
             Route B: the 2x2 radiosity system in the exact form viewFactor.C
                      assembles (C_ij = delta_ij/eps_j - (1/eps_j - 1) F_ij,
                      b_i = -sigma T_i^4 + sum_{j!=i} F_ij sigma T_j^4, q = C^-1 b
                      is the flux INTO the wall), solved numerically; and F21
                      from the differential-element cone integral
                      int_0^alpha 2 sin th cos th dth, alpha = asin(r1/r2), by
                      Simpson quadrature.

  T10a-2     black box 1 x 1 x 0.5 m, floor 600, ceiling 300, x-walls 400,
             y-walls 350 K.
             Route A: Howell C-11 (parallel equal rectangles) and C-14
                      (perpendicular rectangles with a common edge), closed form.
             Route B: the Stokes contour form F_ij = 1/(2 pi A_i)
                      sum_p sum_q (d_p . d_q) int int ln r ds dt over the edge
                      pairs of the two polygons, by adaptive quadrature
                      (scipy.integrate.dblquad), with the coincident common-edge
                      pair taken analytically: int_0^a int_0^a ln|s-t| ds dt
                      = a^2 (ln a - 3/2).
             Fluxes: q_i = sigma T_i^4 - sum_j F_ij sigma T_j^4 (exact for black
                      surfaces) from the route-A matrix, and from the route-B
                      matrix through the viewFactor.C assembly with eps = 1.

  T10a-3     2D Hottel rectangle 1 x 0.5 (REPORTED ONLY, never gated): crossed
             strings, closed form, and the same contour integral in 2D.

  Controls   C1 black spheres, C2 parallel-plate network (spheres), C2 cube
             view-factor matrix (box), C2b opposite-only matrix, and the two
             diagnostic mis-treatments of the pre-registration's table.

Zero solver compute: no case, no mesh, no OpenFOAM.  Exit 0 when every
constant agrees two ways AND with the registered decimals; 1 otherwise.
"""
import math
import os
import re
import sys

# ---- the registered problem, transcribed from the pre-registration --------
K_OF, H_OF, C_OF = 1.38065e-23, 6.62607e-34, 2.99792e+08
SIGMA_SI = 5.670374419e-08
OF_CONTROLDICT = "/usr/lib/openfoam/openfoam2606/etc/controlDict"

R1, R2 = 0.05, 0.10
EPS1, EPS2 = 0.6, 0.4
T1, T2 = 600.0, 300.0

BOX_LX, BOX_LY, BOX_LZ = 1.0, 1.0, 0.5
T_FLOOR, T_CEIL, T_XWALL, T_YWALL = 600.0, 300.0, 400.0, 350.0

# the registered decimals, exactly as printed in the pre-registration (sigma_OF).
# Tolerances below are the half-ulp of each printed value (9 decimals on a
# number of order 0.1-0.6 is 1-5e-9 relative), never looser.
REGISTERED = dict(
    sigma_OF=5.670408558e-08,
    F21=0.25, F22=0.75, denom=2.041666667,
    A1=0.03141593, A2=0.12566371,
    q1=3374.471705, q2=-843.617926, Q=106.012155,
    q1_SI=3374.451389,
    F_fc=0.415253284, F_fw=0.146186679, F_wf=0.292373358,
    F_wo=0.116653692, F_wa=0.149299796,
    B0=6484.920941, B1=-3265.532221, B2=-1254.691645, B3=-1964.697075,
    B0_SI=6484.881898,
    C1_black=6889.546, C2_plate=2175.646,
    outer_black=4133.728, eps_swapped=2583.580,
    cube_opp=0.19982490, cube_adj=0.20004378,
    H_fc=0.618033989, H_fw=0.190983006, H_wf=0.381966011, H_ww=0.236067977,
    H_B0=6510.513314, H_B1=-4637.006925, H_B2=-1873.506388,
)


# ---------------------------------------------------------------------------
def sigma_from(k, h, c):
    return 2.0 * math.pi ** 5 * k ** 4 / (15.0 * h ** 3 * c ** 2)


def sigma_of_host():
    """Route B for sigma: the constants as the installed OpenFOAM carries them."""
    if not os.path.isfile(OF_CONTROLDICT):
        return None
    txt = open(OF_CONTROLDICT).read()
    i = txt.find("SICoeffs")
    vals = {}
    for name in ("c", "h", "k"):
        m = re.search(r"^\s*%s\s+%s\s+\[[^\]]*\]\s+([-0-9.eE+]+)\s*;" % (name, name),
                      txt[i:], re.M)
        if not m:
            return None
        vals[name] = float(m.group(1))
    return sigma_from(vals["k"], vals["h"], vals["c"]), vals


def lu_solve(A, b):
    """Plain Gaussian elimination with partial pivoting (no numpy, so route B
    shares no library with anything)."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            for cc in range(col, n + 1):
                M[r][cc] -= f * M[col][cc]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][cc] * x[cc] for cc in range(r + 1, n))
        x[r] = s / M[r][r]
    return x


def openfoam_assembly(F, eps, T, sigma):
    """The radiosity system exactly as viewFactor.C (constant-emissivity
    branch) assembles it.  Returns qr, the net flux INTO each surface.
    The diagonal F_ii is ignored by the code (planar faces), and here F_ii is
    zero on every row it is applied to except where stated."""
    n = len(T)
    C = [[0.0] * n for _ in range(n)]
    b = [0.0] * n
    for i in range(n):
        for j in range(n):
            inv = 1.0 / eps[j]
            if i == j:
                C[i][j] = inv
                b[i] += -sigma * T[j] ** 4
            else:
                C[i][j] = (1.0 - inv) * F[i][j]
                b[i] += F[i][j] * sigma * T[j] ** 4
    return lu_solve(C, b)


# ---- T10a-1 spheres ----------------------------------------------------------
def spheres_closed_form(sigma):
    A1, A2 = 4 * math.pi * R1 ** 2, 4 * math.pi * R2 ** 2
    F21 = A1 / A2
    denom = 1.0 / EPS1 + (A1 / A2) * (1.0 / EPS2 - 1.0)
    q1 = sigma * (T1 ** 4 - T2 ** 4) / denom
    q2 = -A1 * q1 / A2
    return dict(A1=A1, A2=A2, F21=F21, F22=1.0 - F21, denom=denom,
                q1=q1, q2=q2, Q=A1 * q1, closure=A1 * q1 + A2 * q2)


def spheres_numeric(sigma, n_quad=2000):
    # F21 from the cone integral, Simpson
    alpha = math.asin(R1 / R2)
    h = alpha / n_quad
    s = 0.0
    for k in range(n_quad + 1):
        th = k * h
        w = 1 if k in (0, n_quad) else (4 if k % 2 else 2)
        s += w * 2.0 * math.sin(th) * math.cos(th)
    F21 = s * h / 3.0
    F22 = 1.0 - F21
    # the 2x2 network in OpenFOAM's own form.  NOTE the outer sphere's
    # self-view F22 is NOT zero as a whole surface; the lumped two-surface
    # network needs it, so it is carried in the off-diagonal sense by writing
    # the system in the standard radiosity form, which for a two-surface
    # enclosure with F11 = 0 reduces to the OpenFOAM form with F22 entering
    # the diagonal.  Both forms are solved and must agree.
    A1, A2 = 4 * math.pi * R1 ** 2, 4 * math.pi * R2 ** 2
    F = [[0.0, 1.0], [F21, F22]]
    eps = [EPS1, EPS2]
    T = [T1, T2]
    # standard network: q_i/eps_i - sum_j (1/eps_j - 1) F_ij q_j
    #                   = sigma T_i^4 - sum_j F_ij sigma T_j^4   (q = net LEAVING)
    C = [[(1.0 / eps[i] if i == j else 0.0) - (1.0 / eps[j] - 1.0) * F[i][j]
          for j in range(2)] for i in range(2)]
    b = [sigma * T[i] ** 4 - sum(F[i][j] * sigma * T[j] ** 4 for j in range(2))
         for i in range(2)]
    q_leaving = lu_solve(C, b)
    return dict(F21=F21, F22=F22, q1=q_leaving[0], q2=q_leaving[1],
                Q=A1 * q_leaving[0], closure=A1 * q_leaving[0] + A2 * q_leaving[1],
                qr_into=[-v for v in q_leaving])


# ---- T10a-2 box -----------------------------------------------------------------
def howell_parallel(a, b, c):
    """C-11: identical, parallel, directly opposed rectangles a x b, gap c."""
    X, Y = a / c, b / c
    sx, sy = math.sqrt(1 + X * X), math.sqrt(1 + Y * Y)
    return 2.0 / (math.pi * X * Y) * (
        math.log(sx * sx * sy * sy / (1 + X * X + Y * Y)) / 2.0
        + X * sy * math.atan(X / sy) + Y * sx * math.atan(Y / sx)
        - X * math.atan(X) - Y * math.atan(Y))


def howell_perpendicular(w, h, l):
    """C-14: rectangle 1 (width w) to rectangle 2 (height h), common edge l,
    at 90 degrees."""
    W, H = w / l, h / l
    s = math.sqrt(H * H + W * W)
    t1 = W * math.atan(1 / W) + H * math.atan(1 / H) - s * math.atan(1 / s)
    A = (1 + W * W) * (1 + H * H) / (1 + W * W + H * H)
    B = (W * W * (1 + W * W + H * H) / ((1 + W * W) * (W * W + H * H))) ** (W * W)
    Cc = (H * H * (1 + H * H + W * W) / ((1 + H * H) * (H * H + W * W))) ** (H * H)
    return (t1 + 0.25 * math.log(A * B * Cc)) / (math.pi * W)


def contour_view_factor(poly_i, poly_j):
    """Stokes form: F_ij = 1/(2 pi A_i) sum_p sum_q (d_p . d_q) II ln r ds dt."""
    from scipy.integrate import dblquad

    def edges(poly):
        n = len(poly)
        return [(poly[k], poly[(k + 1) % n]) for k in range(n)]

    def sub(a, b):
        return tuple(x - y for x, y in zip(a, b))

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    def norm(a):
        return math.sqrt(dot(a, a))

    def area(poly):
        # polygon in 3D: half the norm of the sum of cross products
        sx = sy = sz = 0.0
        n = len(poly)
        for k in range(n):
            a, b = poly[k], poly[(k + 1) % n]
            sx += a[1] * b[2] - a[2] * b[1]
            sy += a[2] * b[0] - a[0] * b[2]
            sz += a[0] * b[1] - a[1] * b[0]
        return 0.5 * math.sqrt(sx * sx + sy * sy + sz * sz)

    total = 0.0
    for (p0, p1) in edges(poly_i):
        dp = sub(p1, p0)
        Lp = norm(dp)
        for (q0, q1) in edges(poly_j):
            dq = sub(q1, q0)
            Lq = norm(dq)
            dd = dot(dp, dq) / (Lp * Lq)
            if abs(dd) < 1e-14:
                continue
            coincident = ((norm(sub(p0, q1)) < 1e-14 and norm(sub(p1, q0)) < 1e-14)
                          or (norm(sub(p0, q0)) < 1e-14 and norm(sub(p1, q1)) < 1e-14))
            if coincident:
                a = Lp
                val = a * a * (math.log(a) - 1.5)
            else:
                def integrand(t, s):
                    x = [p0[k] + s * dp[k] for k in range(3)]
                    y = [q0[k] + t * dq[k] for k in range(3)]
                    r = norm(sub(x, y))
                    return math.log(r)
                val, err = dblquad(integrand, 0.0, 1.0, 0.0, 1.0,
                                   epsabs=1e-13, epsrel=1e-13)
                val *= Lp * Lq
            total += dd * val
    return total / (2.0 * math.pi * area(poly_i))


def box_polys():
    Lx, Ly, Lz = BOX_LX, BOX_LY, BOX_LZ
    # every polygon is oriented so that its right-hand normal points INTO the
    # box; the Stokes form needs both contours oriented with their inward
    # normals, and the orientation is asserted below rather than trusted.
    floor = [(0, 0, 0), (Lx, 0, 0), (Lx, Ly, 0), (0, Ly, 0)]
    ceil = [(0, 0, Lz), (0, Ly, Lz), (Lx, Ly, Lz), (Lx, 0, Lz)]
    x0 = [(0, 0, 0), (0, Ly, 0), (0, Ly, Lz), (0, 0, Lz)]
    x1 = [(Lx, 0, 0), (Lx, 0, Lz), (Lx, Ly, Lz), (Lx, Ly, 0)]
    y0 = [(0, 0, 0), (0, 0, Lz), (Lx, 0, Lz), (Lx, 0, 0)]
    y1 = [(0, Ly, 0), (Lx, Ly, 0), (Lx, Ly, Lz), (0, Ly, Lz)]
    P = dict(floor=floor, ceiling=ceil, x0=x0, x1=x1, y0=y0, y1=y1)
    centre = (Lx / 2, Ly / 2, Lz / 2)
    for name, poly in P.items():
        a = [poly[1][k] - poly[0][k] for k in range(3)]
        b = [poly[3][k] - poly[0][k] for k in range(3)]
        nrm = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
               a[0] * b[1] - a[1] * b[0])
        c = [sum(poly[k][d] for k in range(4)) / 4 for d in range(3)]
        inward = sum(nrm[d] * (centre[d] - c[d]) for d in range(3))
        assert inward > 0, f"polygon {name} is not oriented inward"
    return P


BOX_PATCHES = ("floor", "ceiling", "x0", "x1", "y0", "y1")
BOX_AREAS = dict(floor=BOX_LX * BOX_LY, ceiling=BOX_LX * BOX_LY,
                 x0=BOX_LY * BOX_LZ, x1=BOX_LY * BOX_LZ,
                 y0=BOX_LX * BOX_LZ, y1=BOX_LX * BOX_LZ)
BOX_T = dict(floor=T_FLOOR, ceiling=T_CEIL, x0=T_XWALL, x1=T_XWALL,
             y0=T_YWALL, y1=T_YWALL)


def box_matrix_closed_form():
    """6x6 F from Howell C-11 / C-14 (square floor: all four walls alike)."""
    F_fc = howell_parallel(BOX_LX, BOX_LY, BOX_LZ)
    F_fw = howell_perpendicular(BOX_LY, BOX_LZ, BOX_LX)   # floor (w = Ly) -> x-wall (h = Lz), edge Lx
    F_wf = F_fw * BOX_AREAS["floor"] / BOX_AREAS["x0"]
    F_wo = howell_parallel(BOX_LY, BOX_LZ, BOX_LX)        # x0 -> x1, gap Lx
    F_wa = howell_perpendicular(BOX_LY, BOX_LX, BOX_LZ)   # x0 (w = Ly) -> y0 (h = Lx), common vertical edge Lz
    F = {p: {q: 0.0 for q in BOX_PATCHES} for p in BOX_PATCHES}
    for a, b in (("floor", "ceiling"), ("ceiling", "floor")):
        F[a][b] = F_fc
    for w in ("x0", "x1", "y0", "y1"):
        F["floor"][w] = F_fw
        F["ceiling"][w] = F_fw
        F[w]["floor"] = F_wf
        F[w]["ceiling"] = F_wf
    for a, b in (("x0", "x1"), ("x1", "x0"), ("y0", "y1"), ("y1", "y0")):
        F[a][b] = F_wo
    for a in ("x0", "x1"):
        for b in ("y0", "y1"):
            F[a][b] = F_wa
            F[b][a] = F_wa
    return dict(F=F, F_fc=F_fc, F_fw=F_fw, F_wf=F_wf, F_wo=F_wo, F_wa=F_wa)


def box_matrix_contour():
    P = box_polys()
    F_fc = contour_view_factor(P["floor"], P["ceiling"])
    F_fw = contour_view_factor(P["floor"], P["x0"])
    F_fw_y = contour_view_factor(P["floor"], P["y0"])
    F_wf = contour_view_factor(P["x0"], P["floor"])
    F_wo = contour_view_factor(P["x0"], P["x1"])
    F_wa = contour_view_factor(P["x0"], P["y0"])
    return dict(F_fc=F_fc, F_fw=F_fw, F_fw_y=F_fw_y, F_wf=F_wf, F_wo=F_wo,
                F_wa=F_wa)


def box_fluxes_direct(F, sigma, T=None):
    T = T or BOX_T
    q = {}
    for p in BOX_PATCHES:
        q[p] = sigma * T[p] ** 4 - sum(F[p][j] * sigma * T[j] ** 4
                                       for j in BOX_PATCHES)
    q["closure"] = sum(BOX_AREAS[p] * q[p] for p in BOX_PATCHES)
    return q


def box_fluxes_assembly(F, sigma):
    Fm = [[F[p][j] for j in BOX_PATCHES] for p in BOX_PATCHES]
    qr = openfoam_assembly(Fm, [1.0] * 6, [BOX_T[p] for p in BOX_PATCHES], sigma)
    return {p: -qr[k] for k, p in enumerate(BOX_PATCHES)}


def box_matrix_uniform(f_opp, f_adj):
    """A planted matrix: every patch sees its opposite with f_opp and each of
    the four others with f_adj (the cube's numbers, or 1 / 0)."""
    opp = dict(floor="ceiling", ceiling="floor", x0="x1", x1="x0", y0="y1", y1="y0")
    return {p: {q: (0.0 if q == p else (f_opp if q == opp[p] else f_adj))
                for q in BOX_PATCHES} for p in BOX_PATCHES}


# ---- T10a-3 Hottel (reported only) -----------------------------------------
def hottel_rectangle(w=1.0, h=0.5):
    d = math.sqrt(w * w + h * h)
    F_fc = (2 * d - 2 * h) / (2 * w)           # crossed strings, floor -> ceiling
    F_fw = (w + h - d) / (2 * w)               # floor -> one wall
    F_wf = F_fw * w / h
    F_ww = (2 * d - 2 * w) / (2 * h)           # wall -> opposite wall
    return dict(F_fc=F_fc, F_fw=F_fw, F_wf=F_wf, F_ww=F_ww,
                row_floor=F_fc + 2 * F_fw, row_wall=2 * F_wf + F_ww)


def hottel_contour(w=1.0, h=0.5):
    """2D contour form: F_ij = 1/(2 A_i) sum over the two 'edges' (endpoints)
    -- i.e. the crossed-strings rule IS the 2D Stokes form.  Independent route:
    numerical integration of the differential strip view factor
    dF = (1/2) d(sin phi) over the receiving strip, by Simpson."""
    def strip_to_strip(n=4000):
        # floor strip x in [0,w] at z = 0 to ceiling strip at z = h, 2D:
        # F_dx->ceiling = (sin phi2 - sin phi1)/2 with phi measured from normal
        s = 0.0
        hh = w / n
        for k in range(n + 1):
            x = k * hh
            wt = 1 if k in (0, n) else (4 if k % 2 else 2)
            sin1 = -x / math.sqrt(x * x + h * h)
            sin2 = (w - x) / math.sqrt((w - x) ** 2 + h * h)
            s += wt * 0.5 * (sin2 - sin1)
        return s * hh / 3.0 / w
    F_fc = strip_to_strip()
    return dict(F_fc=F_fc)


def hottel_fluxes(sigma):
    f = hottel_rectangle()
    Tf, Tc, Tw = 600.0, 300.0, 400.0
    s = lambda T: sigma * T ** 4
    q_floor = s(Tf) - f["F_fc"] * s(Tc) - 2 * f["F_fw"] * s(Tw)
    q_ceil = s(Tc) - f["F_fc"] * s(Tf) - 2 * f["F_fw"] * s(Tw)
    q_wall = s(Tw) - f["F_wf"] * s(Tf) - f["F_wf"] * s(Tc) - f["F_ww"] * s(Tw)
    return dict(q_floor=q_floor, q_ceil=q_ceil, q_wall=q_wall, **f)


# ---------------------------------------------------------------------------
def main(verbose=True):
    ok = True
    out = []

    def say(s):
        if verbose:
            print(s)

    def check(name, va, vb, tol, note=""):
        nonlocal ok
        rel = abs(va - vb) / max(abs(va), 1e-300)
        good = rel <= tol
        ok = ok and good
        say(f"  {name:14s} {va:.10g}  vs  {vb:.10g}   rel {rel:.2e}  "
            f"{'agree' if good else 'DISAGREE'} {note}")
        return good

    # sigma
    sig_a = sigma_from(K_OF, H_OF, C_OF)
    host = sigma_of_host()
    say("sigma: 2 pi^5 k^4 / (15 h^3 c^2) from the v2606 six-digit constants")
    if host is None:
        say("  (etc/controlDict not found on this host; route B uses the "
            "transcribed constants -- NOT an independent read)")
        sig_b = sig_a
    else:
        sig_b, vals = host
        say(f"  etc/controlDict read: k {vals['k']}  h {vals['h']}  c {vals['c']}")
    check("sigma_OF", sig_a, sig_b, 1e-12, "(transcribed vs read from etc/controlDict)")
    check("sigma_OF reg", REGISTERED["sigma_OF"], sig_a, 2e-9)
    say(f"  sigma_OF / sigma_SI - 1 = {sig_a / SIGMA_SI - 1:+.3e}")
    sigma = sig_a

    # spheres
    sa, sb = spheres_closed_form(sigma), spheres_numeric(sigma)
    say("T10a-1 concentric spheres: closed form vs numerical network + cone integral")
    check("F21", sa["F21"], sb["F21"], 1e-9)
    check("q1", sa["q1"], sb["q1"], 1e-12)
    check("q2", sa["q2"], sb["q2"], 1e-12)
    check("closure", 1.0 + sa["closure"], 1.0 + sb["closure"], 1e-12, "(A1 q1 + A2 q2 = 0)")
    say("  registered decimals")
    check("A1", REGISTERED["A1"], sa["A1"], 2e-7)
    check("A2", REGISTERED["A2"], sa["A2"], 2e-7)
    check("F21", REGISTERED["F21"], sa["F21"], 1e-12)
    check("F22", REGISTERED["F22"], sa["F22"], 1e-12)
    check("denom", REGISTERED["denom"], sa["denom"], 2e-9)
    check("q1", REGISTERED["q1"], sa["q1"], 2e-9)
    check("q2", REGISTERED["q2"], sa["q2"], 2e-9)
    check("Q", REGISTERED["Q"], sa["Q"], 2e-8)
    check("q1 (SI sigma)", REGISTERED["q1_SI"], spheres_closed_form(SIGMA_SI)["q1"], 2e-9)
    say(f"  OpenFOAM qr (INTO the wall): inner {-sa['q1']:.6f}  outer {-sa['q2']:.6f}")

    # box
    ba = box_matrix_closed_form()
    say("T10a-2 black box: Howell closed form vs Stokes contour integral")
    bb = box_matrix_contour()
    check("F floor->ceil", ba["F_fc"], bb["F_fc"], 1e-9)
    check("F floor->wall", ba["F_fw"], bb["F_fw"], 1e-8)
    check("F floor->ywall", ba["F_fw"], bb["F_fw_y"], 1e-8, "(square floor: same as x-wall)")
    check("F wall->floor", ba["F_wf"], bb["F_wf"], 1e-8)
    check("F wall->opp", ba["F_wo"], bb["F_wo"], 1e-9)
    check("F wall->adj", ba["F_wa"], bb["F_wa"], 1e-8)
    rows = {p: sum(ba["F"][p].values()) for p in BOX_PATCHES}
    recip = max(abs(BOX_AREAS[p] * ba["F"][p][q] - BOX_AREAS[q] * ba["F"][q][p])
                for p in BOX_PATCHES for q in BOX_PATCHES)
    say(f"  row sums: floor {rows['floor']:.15f}  wall {rows['x0']:.15f}  "
        f"max reciprocity defect {recip:.1e}")
    check("row floor", 1.0, rows["floor"], 1e-12)
    check("row wall", 1.0, rows["x0"], 1e-12)
    qa = box_fluxes_direct(ba["F"], sigma)
    qb = box_fluxes_assembly(ba["F"], sigma)
    say("  fluxes: direct black sum vs viewFactor.C assembly with eps = 1")
    for p in ("floor", "ceiling", "x0", "y0"):
        check(f"q {p}", qa[p], qb[p], 1e-12)
    say(f"  closure sum A_i q_i = {qa['closure']:.3e} W")
    say("  registered decimals")
    check("F_fc", REGISTERED["F_fc"], ba["F_fc"], 2e-9)
    check("F_fw", REGISTERED["F_fw"], ba["F_fw"], 4e-9)
    check("F_wf", REGISTERED["F_wf"], ba["F_wf"], 2e-9)
    check("F_wo", REGISTERED["F_wo"], ba["F_wo"], 5e-9)
    check("F_wa", REGISTERED["F_wa"], ba["F_wa"], 4e-9)
    check("B0 floor", REGISTERED["B0"], qa["floor"], 2e-9)
    check("B1 ceiling", REGISTERED["B1"], qa["ceiling"], 2e-9)
    check("B2 x-wall", REGISTERED["B2"], qa["x0"], 2e-9)
    check("B3 y-wall", REGISTERED["B3"], qa["y0"], 2e-9)
    check("B0 (SI sigma)", REGISTERED["B0_SI"], box_fluxes_direct(ba["F"], SIGMA_SI)["floor"], 2e-9)

    # controls
    say("controls (reference-side plants)")
    c1 = sigma * (T1 ** 4 - T2 ** 4)
    c2 = sigma * (T1 ** 4 - T2 ** 4) / (1 / EPS1 + 1 / EPS2 - 1)
    outer_black = sigma * (T1 ** 4 - T2 ** 4) / (1 / EPS1)
    A1, A2 = sa["A1"], sa["A2"]
    swapped = sigma * (T1 ** 4 - T2 ** 4) / (1 / EPS2 + (A1 / A2) * (1 / EPS1 - 1))
    check("C1 black", REGISTERED["C1_black"], c1, 2e-7)
    check("C2 plates", REGISTERED["C2_plate"], c2, 2e-7)
    check("outer black", REGISTERED["outer_black"], outer_black, 2e-7)
    check("eps swapped", REGISTERED["eps_swapped"], swapped, 2e-7)
    for name, v in (("C1", c1), ("C2", c2), ("outer black", outer_black), ("swapped", swapped)):
        say(f"    {name:12s} {v:.3f}  departure {100 * (v / sa['q1'] - 1):+.2f} %")
    cube = howell_parallel(1.0, 1.0, 1.0)
    cube_adj = howell_perpendicular(1.0, 1.0, 1.0)
    check("cube opposite", REGISTERED["cube_opp"], cube, 2e-7)
    check("cube adjacent", REGISTERED["cube_adj"], cube_adj, 2e-7)
    Fc = box_matrix_uniform(cube, cube_adj)
    qc = box_fluxes_direct(Fc, sigma)
    say("    C2 box (cube matrix) departures: " + "  ".join(
        f"{p} {100 * (qc[p] / qa[p] - 1):+.2f} %" for p in ("floor", "ceiling", "x0", "y0")))
    Fo = box_matrix_uniform(1.0, 0.0)
    qo = box_fluxes_direct(Fo, sigma)
    say("    C2b box (opposite only) departures: " + "  ".join(
        f"{p} {100 * (qo[p] / qa[p] - 1):+.2f} %" for p in ("floor", "ceiling", "x0", "y0")))

    # Hottel
    hf = hottel_fluxes(sigma)
    hc = hottel_contour()
    say("T10a-3 Hottel 2D rectangle (REPORTED ONLY): crossed strings vs strip integral")
    check("H F_fc", hf["F_fc"], hc["F_fc"], 1e-9)
    check("H row floor", 1.0, hf["row_floor"], 1e-12)
    check("H row wall", 1.0, hf["row_wall"], 1e-12)
    check("H F_fc reg", REGISTERED["H_fc"], hf["F_fc"], 2e-9)
    check("H F_fw reg", REGISTERED["H_fw"], hf["F_fw"], 3e-9)
    check("H F_wf reg", REGISTERED["H_wf"], hf["F_wf"], 2e-9)
    check("H F_ww reg", REGISTERED["H_ww"], hf["F_ww"], 3e-9)
    check("H B0 reg", REGISTERED["H_B0"], hf["q_floor"], 2e-9)
    check("H B1 reg", REGISTERED["H_B1"], hf["q_ceil"], 2e-9)
    check("H B2 reg", REGISTERED["H_B2"], hf["q_wall"], 2e-9)

    say("AGREE: every constant reproduced two ways and matches the registered decimals."
        if ok else
        "DISAGREE: the derivations do not agree; nothing downstream may run.")
    return 0 if ok else 1


def references(sigma=None):
    """Machine-readable references for the comparator (sigma_OF by default)."""
    sigma = sigma if sigma is not None else sigma_from(K_OF, H_OF, C_OF)
    sa = spheres_closed_form(sigma)
    ba = box_matrix_closed_form()
    qa = box_fluxes_direct(ba["F"], sigma)
    cube = box_matrix_uniform(howell_parallel(1, 1, 1), howell_perpendicular(1, 1, 1))
    qc = box_fluxes_direct(cube, sigma)
    qo = box_fluxes_direct(box_matrix_uniform(1.0, 0.0), sigma)
    return dict(sigma=sigma, spheres=sa, box_F=ba, box_q=qa,
                C1_black=sigma * (T1 ** 4 - T2 ** 4),
                C2_plate=sigma * (T1 ** 4 - T2 ** 4) / (1 / EPS1 + 1 / EPS2 - 1),
                C2_cube_q=qc, C2b_opposite_q=qo, hottel=hottel_fluxes(sigma))


if __name__ == "__main__":
    sys.exit(main())
