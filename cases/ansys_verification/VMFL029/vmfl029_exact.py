#!/usr/bin/env python3
"""VMFL029 -- Anisotropic Conduction Heat Transfer: the lab's own reference
evaluation, and the instruments that check it.

DRAFT / NOT FROZEN.  This module is committed as working evidence for the
VMFL029 registration.  It is NOT a frozen comparator and NOTHING here has been
used to grade a run.  The registration itself is at PREREGISTRATION.md in this
directory and is explicitly NOT frozen.

--------------------------------------------------------------------------
WHAT THIS FILE IS FOR
--------------------------------------------------------------------------
The Ansys Fluid Dynamics Verification Manual VM2026R1, VMFL029 (p. 109-110),
prints NO conductivity values, NO analytical formula and NO results table.  Its
only results artefact is Figure .29.2, "Comparison of Normalized Temperature
Distribution at X = 0.5 m" -- a FIGURE.  A digitised figure is not admissible as
a gate reference in this lab.  THE ONLY ADMISSIBLE GATE IS THE LAB'S OWN
EVALUATION, to full double precision, of the exact solution of the PDE the lab's
solver discretises.  Setup inputs (geometry, tensor, boundary profiles) may be
recovered from the Ansys archive; A GATE VALUE MAY NOT, EVER.

--------------------------------------------------------------------------
THE CASE
--------------------------------------------------------------------------
Domain      1 m x 1 m square, [0,1] x [0,1], steady conduction, no source.
PDE         div(K grad T) = 0, K a constant symmetric positive-definite tensor.
Material    rho = 2719 kg/m3, Cp = 871 J/(kg K)   [manual p. 109, printed]
BCs         T(0,y) = 100 K            (x = 0 wall)
            T(1,y) = 200 K            (x = 1 wall)
            T(x,0) = 100 + 100 x      (y = 0 wall, UDF prof_aniso)
            T(x,1) = 100 + 100 x^2    (y = 1 wall, UDF prof_aniso)
            -- continuous around the whole boundary; corners agree.
Normalised  Tnorm = (T - 100) / 100.

--------------------------------------------------------------------------
THE TENSOR, AND THE FACT THAT DECIDES THIS CASE
--------------------------------------------------------------------------
The archive (VMFL029_aniso.cas:2628) stores

        K_arch = [[ 0.25 , -0.433, 0 ],
                  [-0.433,  0.75 , 0 ],
                  [ 0    ,  0    , 1 ]]   W/(m K)

whose 2-D block has eigenvalues 1.10001210e-05 and 9.99989e-01 -- condition
number 9.0907e+04.  Those four-digit decimals are a truncation of

        K_rank1 = [[ 1/4      , -sqrt(3)/4 ],
                   [-sqrt(3)/4,  3/4       ]]  =  v v^T ,
        v = (1/2, -sqrt(3)/2),  |v| = 1,

which is EXACTLY RANK ONE: conductivity 1 along v (-60 deg) and EXACTLY ZERO
along the perpendicular (30 deg).  det(K_rank1) = 0.  The only thing that makes
the archived tensor non-singular is the truncation of sqrt(3)/4 = 0.4330127...
to 0.433.

Consequences, all of them measured elsewhere in this package:

  * The rank-1 problem is NOT elliptic.  div(K grad T) = d^2 T/ds^2 along the
    chords in direction v, an ODE.  It has a CLOSED FORM (T_rank1 below):
    T is linear along each chord between the two boundary points the chord hits.
  * The archived (truncated) problem IS elliptic but with layer thickness
    sqrt(lam_min/lam_max) = 3.3167e-03 m in a 1 m domain.
  * The two are DIFFERENT CONTINUUM MODELS in the sense of
    ANSYS_VERIFICATION_CHARTER §12.2 / VERIFICATION_CHARTER §2h.6.1 (v1.27,
    2026-08-31, the exact-PDE rule).  Their solutions differ by up to
    ~2.1e-01 K on the x = 0.5 profile (measured, see PREREGISTRATION.md §7).

--------------------------------------------------------------------------
INSTRUMENTS
--------------------------------------------------------------------------
I1  T_rank1_closed  -- algebraic closed form of the rank-1 exact solution.
I2  T_rank1_ray     -- the same object by an independent code path: numerical
                       ray-tracing of the chord to the boundary, no algebra
                       shared with I1.
I3  pde_residual_along_chord -- differentiates I1 twice along v and checks the
                       rank-1 PDE is satisfied (it must be ~0 away from the
                       corner characteristic).
I4  fd_solve        -- 9-point conservative finite-difference solve of the FULL
                       anisotropic problem for any SPD K, used (a) to show
                       I1 is the lam_min -> 0 limit and (b) as the cross-
                       instrument against OpenFOAM solidFoam/constAnIso.

Run `python3 vmfl029_exact.py selftest` to execute all four.
"""

import numpy as np

# ---------------------------------------------------------------- tensors
K_ARCH = np.array([[0.25, -0.433], [-0.433, 0.75]])
K_RANK1 = np.array([[0.25, -np.sqrt(3) / 4], [-np.sqrt(3) / 4, 0.75]])
RHO, CP = 2719.0, 871.0                      # manual p. 109, printed
V_STRONG = np.array([0.5, -np.sqrt(3) / 2])  # unit; K_RANK1 = v v^T
SQ3 = np.sqrt(3.0)

TL, TR = 100.0, 200.0                        # x=0 and x=1 walls


def eig_report(K):
    """Eigenvalues, eigenvector angles (deg), det, condition number."""
    w, V = np.linalg.eigh(K)
    ang = np.degrees(np.arctan2(V[1], V[0]))
    return dict(lam_lo=w[0], lam_hi=w[1], ang_lo=ang[0], ang_hi=ang[1],
                det=float(np.linalg.det(K)), cond=w[1] / w[0] if w[0] else np.inf,
                layer=np.sqrt(w[0] / w[1]) if w[0] > 0 else 0.0)


# ------------------------------------------------------- boundary data
def T_wall(x, y, tol=1e-12):
    """Dirichlet datum on the boundary point (x,y).  Corners agree."""
    x = float(x); y = float(y)
    if abs(x) < tol:
        return TL
    if abs(x - 1.0) < tol:
        return TR
    if abs(y) < tol:
        return 100.0 + 100.0 * x
    if abs(y - 1.0) < tol:
        return 100.0 + 100.0 * x * x
    raise ValueError(f"({x},{y}) is not on the boundary")


def u_wall(x, y, tol=1e-12):
    """Boundary datum of u = T - (100 + 100 x).  Zero except on y = 1."""
    return T_wall(x, y, tol) - (100.0 + 100.0 * float(x))


# ------------------------------------------------ I1: algebraic closed form
def T_rank1_closed(x, y):
    """EXACT solution of the rank-1 problem  d^2 T/ds^2 = 0 along v, in closed
    algebraic form.

    T = 100 + 100 x + u.  The linear part 100 + 100 x already satisfies EVERY
    constant-K equation and matches three of the four walls, so u is driven only
    by the y = 1 wall, where u = 100 (x^2 - x).

    A chord through (x,y) in direction v = (1/2, -sqrt(3)/2) leaves the square
    backwards through y = 1 iff  x > (1-y)/sqrt(3); otherwise it leaves through
    x = 0 where u = 0, so u = 0 identically there.
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    xb = x - (1.0 - y) / SQ3                       # backward exit abscissa on y=1
    tm = 2.0 * (1.0 - y) / SQ3                     # backward chord length
    tp = np.minimum(2.0 * y / SQ3, 2.0 * (1.0 - x))  # forward chord length
    L = tp + tm
    ub = 100.0 * (xb * xb - xb)                    # u on the y = 1 wall
    with np.errstate(divide='ignore', invalid='ignore'):
        u = np.where(L > 0, ub * tp / np.where(L > 0, L, 1.0), ub)
    u = np.where(xb > 0.0, u, 0.0)                 # chord misses the y=1 wall
    return 100.0 + 100.0 * x + u


# ------------------------------------------------- I2: independent ray-trace
def _exit_t(p, d):
    """Smallest t > 0 with p + t d on the unit-square boundary.  No algebra
    shared with T_rank1_closed -- this is a generic ray/box intersection."""
    best = np.inf
    for comp in (0, 1):
        if abs(d[comp]) < 1e-15:
            continue
        for target in (0.0, 1.0):
            t = (target - p[comp]) / d[comp]
            if t > 1e-13:
                q = p + t * d
                if -1e-9 <= q[0] <= 1 + 1e-9 and -1e-9 <= q[1] <= 1 + 1e-9:
                    best = min(best, t)
    return best


def T_rank1_ray(x, y):
    """Same object as T_rank1_closed, by ray-tracing + linear interpolation
    between the two boundary values.  Independent code path."""
    p = np.array([float(x), float(y)])
    tp = _exit_t(p, V_STRONG)
    tm = _exit_t(p, -V_STRONG)
    a = p + tp * V_STRONG
    b = p - tm * V_STRONG
    a = np.clip(a, 0.0, 1.0); b = np.clip(b, 0.0, 1.0)
    ua, ub = u_wall(*a), u_wall(*b)
    L = tp + tm
    u = ub + (ua - ub) * (tm / L) if L > 1e-12 else ua
    return 100.0 + 100.0 * p[0] + u


# ---------------------------------------------- I3: PDE residual along chord
def pde_residual_along_chord(x, y, ds=1e-4):
    """d^2 T/ds^2 along v, by central differences on the closed form.
    Must be ~0 (the rank-1 PDE) wherever the stencil does not straddle the
    corner characteristic x = (1-y)/sqrt(3)."""
    p = np.array([float(x), float(y)])
    f = lambda q: float(T_rank1_closed(q[0], q[1]))
    return (f(p + ds * V_STRONG) - 2 * f(p) + f(p - ds * V_STRONG)) / ds ** 2


# ---------------------------------------------------- I4: conservative FD
def fd_solve(N, K):
    """Vertex-centred uniform N x N conservative 9-point FD for
    div(K grad T) = 0 with the VMFL029 Dirichlet data.

    The stencil is written in flux-difference form, so the discrete face fluxes
    TELESCOPE: see net_wall_flux() and wall_flux().  Returns (xs, ys, T) with
    T[i,j] at (xs[i], ys[j]).
    """
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl
    h = 1.0 / N
    xs = np.linspace(0, 1, N + 1); ys = np.linspace(0, 1, N + 1)
    ni = N - 1
    idx = lambda i, j: (j - 1) * ni + (i - 1)
    Kxx, Kxy, Kyy = K[0, 0], K[0, 1], K[1, 1]
    T = np.zeros((N + 1, N + 1))
    T[0, :] = TL; T[N, :] = TR
    T[:, 0] = 100.0 + 100.0 * xs
    T[:, N] = 100.0 + 100.0 * xs ** 2
    st = {(0, 0): -2 * Kxx / h ** 2 - 2 * Kyy / h ** 2,
          (1, 0): Kxx / h ** 2, (-1, 0): Kxx / h ** 2,
          (0, 1): Kyy / h ** 2, (0, -1): Kyy / h ** 2,
          (1, 1): Kxy / (2 * h ** 2), (-1, -1): Kxy / (2 * h ** 2),
          (1, -1): -Kxy / (2 * h ** 2), (-1, 1): -Kxy / (2 * h ** 2)}
    rows = []; cols = []; vals = []; rhs = np.zeros(ni * ni)
    for j in range(1, N):
        for i in range(1, N):
            r = idx(i, j)
            for (di, dj), c in st.items():
                ii, jj = i + di, j + dj
                if 0 < ii < N and 0 < jj < N:
                    rows.append(r); cols.append(idx(ii, jj)); vals.append(c)
                else:
                    rhs[r] -= c * T[ii, jj]
    A = sp.csr_matrix(sp.coo_matrix((vals, (rows, cols)), shape=(ni * ni,) * 2))
    T[1:N, 1:N] = spl.spsolve(A, rhs).reshape(N - 1, N - 1).T
    return xs, ys, T


# --------------------------------------------- I5: cell-centred FV instrument
def fv_solve(N, K):
    """Cell-centred finite-volume solve, built the way OpenFOAM's
    gaussLaplacianScheme builds an anisotropic laplacian:

        SfGamma   = Sf & K
        SfGammaSn = SfGamma & n          -> IMPLICIT (orthogonal part)
        SfGammaCorr = SfGamma - SfGammaSn n  -> EXPLICIT (tangential part)

    solved by deferred correction to a tight tolerance.  This is the
    discretisation the lab would actually run, so it is the one in which the
    conservation identity of Task 3 must be tested.  Returns (xc, yc, T) with
    T[i,j] the cell value at (xc[i], yc[j]).
    """
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl
    h = 1.0 / N
    xc = (np.arange(N) + 0.5) * h
    yc = (np.arange(N) + 0.5) * h
    Kxx, Kxy, Kyy = K[0, 0], K[0, 1], K[1, 1]
    idx = lambda i, j: j * N + i
    # implicit part: standard orthogonal 5-point with coefficients Kxx, Kyy
    rows = []; cols = []; vals = []; b0 = np.zeros(N * N)
    Tb_l = np.full(N, TL); Tb_r = np.full(N, TR)
    Tb_b = 100.0 + 100.0 * xc
    Tb_t = 100.0 + 100.0 * xc ** 2
    for j in range(N):
        for i in range(N):
            r = idx(i, j); diag = 0.0
            for (di, dj, kk, bval) in ((-1, 0, Kxx, Tb_l[j]), (1, 0, Kxx, Tb_r[j]),
                                       (0, -1, Kyy, Tb_b[i]), (0, 1, Kyy, Tb_t[i])):
                ii, jj = i + di, j + dj
                if 0 <= ii < N and 0 <= jj < N:
                    rows.append(r); cols.append(idx(ii, jj)); vals.append(kk / h ** 2)
                    diag -= kk / h ** 2
                else:                                   # Dirichlet face, dist h/2
                    diag -= 2 * kk / h ** 2
                    b0[r] -= 2 * kk / h ** 2 * bval
            rows.append(r); cols.append(r); vals.append(diag)
    A = sp.csr_matrix(sp.coo_matrix((vals, (rows, cols)), shape=(N * N,) * 2))
    lu = spl.splu(A.tocsc())

    def _tangential(T):
        """Explicit cross-term source:  -(1/V) sum_f SfGammaCorr . grad(T)|_f ."""
        Fx, Fy = _cross_fluxes(T, K, h, Tb_l, Tb_r, Tb_b, Tb_t)
        s = ((Fx[1:, :] - Fx[:-1, :]) + (Fy[:, 1:] - Fy[:, :-1])) / h ** 2
        return s.flatten(order='F')

    T = np.full((N, N), 150.0)
    for it in range(4000):
        rhs = b0 + _tangential(T)
        Tn = lu.solve(rhs).reshape(N, N, order='F')
        d = np.max(abs(Tn - T)); T = Tn
        if d < 1e-11:
            break
    return xc, yc, T, it + 1, d


def _cross_fluxes(T, K, h, Tb_l, Tb_r, Tb_b, Tb_t):
    """Tangential (cross-term) part of the face flux, INCLUDING boundary faces,
    with the SAME formula on every face.  Fx has shape (N+1, N), Fy (N, N+1).
    Sign: Fx is the flux in +x through that face, times face area h."""
    Kxy = K[0, 1]
    N = T.shape[0]
    # cell-centre gradients (one-sided at walls, using the Dirichlet face value)
    dTdy = np.empty_like(T); dTdx = np.empty_like(T)
    dTdy[:, 1:-1] = (T[:, 2:] - T[:, :-2]) / (2 * h)
    dTdy[:, 0] = (T[:, 1] - Tb_b) / (1.5 * h)
    dTdy[:, -1] = (Tb_t - T[:, -2]) / (1.5 * h)
    dTdx[1:-1, :] = (T[2:, :] - T[:-2, :]) / (2 * h)
    dTdx[0, :] = (T[1, :] - Tb_l) / (1.5 * h)
    dTdx[-1, :] = (Tb_r - T[-2, :]) / (1.5 * h)
    Fx = np.zeros((N + 1, N)); Fy = np.zeros((N, N + 1))
    Fx[1:-1, :] = -Kxy * 0.5 * (dTdy[1:, :] + dTdy[:-1, :]) * h
    Fy[:, 1:-1] = -Kxy * 0.5 * (dTdx[:, 1:] + dTdx[:, :-1]) * h
    # boundary faces: tangential derivative is the EXACT derivative of the
    # Dirichlet data along the wall (constant on x-walls, known on y-walls)
    Fx[0, :] = 0.0                       # dT/dy = 0 along x = 0 (T = 100)
    Fx[-1, :] = 0.0                      # dT/dy = 0 along x = 1 (T = 200)
    Fy[:, 0] = -Kxy * 100.0 * h          # d/dx (100 + 100 x)   = 100
    Fy[:, -1] = -Kxy * 200.0 * (np.arange(N) + 0.5) / N * h   # d/dx (100 + 100 x^2)
    return Fx, Fy


def wall_flux(T, K, h):
    """Integrated heat flux (W per m depth) through each wall, and the NET,
    computed from EXACTLY the face fluxes the fv_solve equations use.
    Sign convention: positive = OUT of the domain.

    Because every internal face flux enters two cell equations with opposite
    signs, and every cell equation sums to zero at convergence, the NET is an
    ALGEBRAIC IDENTITY -- machine zero on any mesh.  That is the VMFL038 tau_w
    shape and it makes the net a NON-DISCRIMINATING gate quantity.
    """
    N = T.shape[0]
    xc = (np.arange(N) + 0.5) * h
    Kxx, Kxy, Kyy = K[0, 0], K[0, 1], K[1, 1]
    Tb_l = np.full(N, TL); Tb_r = np.full(N, TR)
    Tb_b = 100.0 + 100.0 * xc; Tb_t = 100.0 + 100.0 * xc ** 2
    # outward flux = -A [ K_nn dT/dn + (n.K.t) dT/dt ], dT/dn = (T_b - T_P)/(h/2)
    left = h * np.sum(Kxx * (T[0, :] - Tb_l) / (h / 2))                # n.K.t = -Kxy, dT/dt = 0
    right = h * np.sum(Kxx * (T[-1, :] - Tb_r) / (h / 2))              # n.K.t = +Kxy, dT/dt = 0
    bottom = h * np.sum(Kyy * (T[:, 0] - Tb_b) / (h / 2) + Kxy * 100.0)
    top = h * np.sum(Kyy * (T[:, -1] - Tb_t) / (h / 2) - Kxy * 200.0 * xc)
    return dict(left=left, right=right, bottom=bottom, top=top,
                net=left + right + bottom + top)


# ---------------------------------------------------------------- selftest
def selftest():
    ok = True
    print("=== tensors ===")
    for nm, K in (("K_arch", K_ARCH), ("K_rank1", K_RANK1)):
        r = eig_report(K)
        print(f"  {nm}: lam = {r['lam_lo']:.8e}, {r['lam_hi']:.8e}  "
              f"det = {r['det']:.6e}  cond = {r['cond']:.6e}")
        print(f"          evec angles {r['ang_lo']:+.4f} / {r['ang_hi']:+.4f} deg   "
              f"layer = {r['layer']:.6e} m")
    assert np.allclose(K_RANK1, np.outer(V_STRONG, V_STRONG), atol=1e-15), \
        "K_rank1 is not v v^T"
    print("  CHECK K_rank1 == v v^T (rank one)                       : PASS")

    print("\n=== I1 vs I2 (closed form vs independent ray-trace) ===")
    rng = np.random.default_rng(20260831)
    P = rng.uniform(1e-6, 1 - 1e-6, size=(4000, 2))
    d = np.array([abs(T_rank1_closed(px, py) - T_rank1_ray(px, py)) for px, py in P])
    print(f"  4000 interior points, max |I1 - I2| = {d.max():.3e} K")
    ok &= d.max() < 1e-9
    print(f"  CHECK  max |I1 - I2| < 1e-9                             : "
          f"{'PASS' if d.max() < 1e-9 else 'FAIL'}")

    print("\n=== I3 (rank-1 PDE residual on the closed form) ===")
    res = []
    for px, py in P[:1500]:
        if abs(px - (1 - py) / SQ3) < 5e-3:     # skip the corner characteristic
            continue
        r = pde_residual_along_chord(px, py)
        res.append(abs(r))
    res = np.array(res)
    print(f"  {len(res)} points off the characteristic, "
          f"max |d2T/ds2| = {res.max():.3e} K/m^2")
    ok &= res.max() < 1e-4
    print(f"  CHECK  max |d2T/ds2| < 1e-4                             : "
          f"{'PASS' if res.max() < 1e-4 else 'FAIL'}")

    print("\n=== PLANTED-ZERO CONTROL on I3 ===")
    # A residual reader that cannot see a real non-zero is not evidence.
    # Plant a known perturbation by evaluating the residual of a function that
    # is NOT a rank-1 solution and demanding the reader refuse it.
    bad = lambda q: float(T_rank1_closed(q[0], q[1])) + 1.234e-03 * q[0] ** 2
    ds = 1e-4; p = np.array([0.62, 0.55])
    planted = (bad(p + ds * V_STRONG) - 2 * bad(p) + bad(p - ds * V_STRONG)) / ds ** 2
    expect = 2 * 1.234e-03 * V_STRONG[0] ** 2        # = 2 a vx^2
    print(f"  planted d2/ds2 = {planted:.6e}, analytic {expect:.6e}")
    seen = abs(planted - expect) < 1e-6 and abs(planted) > 1e-5
    ok &= seen
    print(f"  CHECK  reader SEES the plant (refuses a blind zero)     : "
          f"{'PASS' if seen else 'FAIL'}")

    print("\n=== I5 / Task 3: which gate quantities are CONSERVATION-PINNED? ===")
    print("  cell-centred FV (the discretisation we would run).")
    print("  Hypothesis: NET wall flux is pinned to machine zero on every mesh")
    print("  (the VMFL038 tau_w shape); a SINGLE wall's flux refines.")
    prev = None; prevprof = None
    for N in (40, 80, 160):
        xc, yc, T, nit, res = fv_solve(N, K_ARCH)
        f = wall_flux(T, K_ARCH, 1.0 / N)
        scale = max(abs(f[k]) for k in ('left', 'right', 'top', 'bottom'))
        print(f"  N={N:4d} ({nit} outer, dTmax={res:.2e})  left={f['left']:+.10e}  "
              f"right={f['right']:+.10e}")
        print(f"          bottom={f['bottom']:+.10e}  top={f['top']:+.10e}")
        print(f"          NET = {f['net']:+.6e}    |NET|/scale = {abs(f['net'])/scale:.3e}")
        if prev is not None:
            print(f"          change in LEFT wall flux from previous level = "
                  f"{f['left']-prev:+.6e}  ({abs(f['left']-prev)/abs(f['left']):.3e} rel)")
        prev = f['left']
        i0 = int(np.argmin(abs(xc - 0.5)))
        prof = np.interp(np.linspace(0.02, 0.98, 97), yc, T[i0, :])
        if prevprof is not None:
            print(f"          change in T(x=0.5) profile from previous level  = "
                  f"{np.max(abs(prof-prevprof)):+.6e} K")
        prevprof = prof

    print("\n=== I4: I1 is the lam_min -> 0 limit ===")
    yq = np.linspace(0.02, 0.98, 97)
    ref = T_rank1_closed(np.full_like(yq, 0.5), yq)
    for lam in (1e-2, 1e-3, 1e-4, 1.10001210e-05):
        K = np.array([[0.25, -0.433], [-0.433, 0.75]])
        w, V = np.linalg.eigh(K_RANK1)
        Kl = V @ np.diag([lam, 1.0]) @ V.T
        xs, ys, T = fd_solve(400, Kl)
        i0 = int(np.argmin(abs(xs - 0.5)))
        p = np.interp(yq, ys, T[i0, :])
        print(f"  lam_min={lam:9.3e}  N=400  max|T - I1| = {np.max(abs(p-ref)):.4e} K"
              f"   L2 = {np.sqrt(np.mean((p-ref)**2)):.4e} K")

    print("\nSELFTEST:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    import sys
    raise SystemExit(selftest() if len(sys.argv) > 1 and sys.argv[1] == "selftest"
                     else selftest())
