#!/usr/bin/env python3
"""
F27 -- THE EXACT SOLUTION of pulsatile (Womersley) laminar flow in a CIRCULAR
PIPE, and the DISCRETISATION-DERIVED error prediction every F27 band is built
from.

    pipe     r in [0, R = 1], wall no-slip; z in [0, LZ = 1] CYCLIC (the
             solution is z-invariant AND azimuthally invariant, so any z- or
             theta-variation the solver produces is error)
    drive    uniform kinematic body force  f(t) = A cos(omega t) z-hat
             (= -1/rho dp/dz), A = 1, omega = 2 pi, PERIOD = 1
    exact    u_z(r, t) = Re[ (A / (i omega)) (1 - I0(lambda r) / I0(lambda R))
                            e^{i omega t} ],   lambda = sqrt(i omega / nu)
             u_r = u_theta = 0,  p = const
             (I0(lambda r) == J0(i^{3/2} alpha r / R) -- the Bessel-function
             Womersley profile in its modified-Bessel form; the two are the
             same function and the identity is DRIVEN in a control below.)
    Womersley number  alpha = R sqrt(omega / nu) = 4 EXACTLY (nu = pi/8)

DISTINCT FROM F21_WOMERSLEY, which is the 2-D PLANAR CHANNEL at alpha = 5 with
a cosh profile.  This rung is the CIRCULAR PIPE at alpha = 4 with a Bessel
profile, on a GENUINE 3-D butterfly (O-grid) mesh refined by 2 in ALL THREE
directions.  Nothing here is inherited from F21's ladder: L-346.

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  The closed
form is substituted symbolically into the unsteady axial-momentum equation in
cylindrical coordinates,

    u_t = nu (u_rr + u_r / r) + A cos(omega t),

(the convective term is identically zero for a z- and theta-invariant purely
axial field and continuity is trivially satisfied); a planted control
(lambda -> 1.1 lambda) must make the residual non-zero.  The same residual is
also evaluated numerically at random points, and the Bessel function itself is
evaluated by TWO INDEPENDENT IMPLEMENTATIONS (scipy.special.iv and
mpmath.besseli) that must agree to 1e-13, with a planted mismatch that must be
seen.

THE BAND PRINCIPLE -- derived from the discretisation, not measured.  The flow
is linear, axisymmetric and one-dimensional in r, so the PHYSICS-carrying part
of the solver's discretisation reduces to a 1-D cylindrical finite-volume heat
equation: cell-centred second-order radial Laplacian on annular control volumes
V_j = 2 pi r_j dr with face areas 2 pi r_{j+-1/2}, the no-slip face gradient
(0 - u_P)/(dr/2) at the wall, the symmetry condition at the axis carried by the
vanishing face area there (NOT by a ghost cell), the `backward` (BDF2) time
derivative with OpenFOAM's Euler-implicit first step, and the explicit cosine
source at the new time level.  The PISO pressure correction is identically zero
on a z-invariant field (p = const), so this discrete solution IS the physics the
solver integrates, up to solver tolerances, the preservation of z- and
theta-invariance, the butterfly mesh's geometry, and round-off.

THE ONE PLACE THIS MODEL IS AN APPROXIMATION AND NOT A REDUCTION, stated
plainly because the band rests on it: THE REGISTERED MESH IS A BUTTERFLY
O-GRID, NOT A RADIAL GRID.  The model's uniform radial grid of MODEL_NR(level)
cells is the level's OWN radial cell count along the +x ray (nc/2 cells through
the Cartesian core block plus nr cells through the O-ring), so it refines by
exactly 2 with the mesh and its spacing matches the mesh's radial spacing along
that ray to within a few per cent -- but it cannot see the azimuthal
discretisation, the Cartesian core block, or the up-to-40-degree
non-orthogonality of the ring.  BAND_FACTOR is a DECLARED JUDGEMENT covering
that mismatch, not a measurement, and the pre-registration says so.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f27.py must not run under `python3 -O`.\n")
    sys.exit(2)

import os
import json
import math
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import roache_triple as RT               # the SAME classifier that will grade the run (L-345)

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
R = 1.0                                 # pipe radius
LZ = 1.0                                # cyclic axial length
CORE_FRAC = 0.5                         # butterfly: the inner square's corners sit at r = CORE_FRAC * R
OMEGA = 2.0 * math.pi                   # drive angular frequency: PERIOD = 1
PERIOD = 2.0 * math.pi / OMEGA
A_DRIVE = 1.0                           # kinematic body-force amplitude, = -1/rho dp/dz amplitude
ALPHA = 4.0                             # Womersley number, EXACT by construction of NU
NU = OMEGA * R ** 2 / ALPHA ** 2        # = pi / 8 = 0.39269908169872414
U_REF = A_DRIVE / OMEGA                 # the Womersley velocity scale A/omega, the normaliser
N_PERIODS = 5                           # periods before the locked phase; DERIVED below, not inherited
PHASE_DEG = 90.0                        # locked phase: the bulk velocity's quarter-period point
T_END = (N_PERIODS + PHASE_DEG / 360.0) * PERIOD          # = 5.25
STEPS_PER_PERIOD = dict(coarse=128, medium=256, fine=512)  # dt refines by exactly 2 with h

# name, nc (core cells per side = azimuthal cells per quadrant), nr (ring radial
# cells), nz (axial cells), steps to T_END.  Cells = (nc^2 + 4 nc nr) * nz.
LEVELS = (("coarse",  8,  8, 12,  672),
          ("medium", 16, 16, 24, 1344),
          ("fine",   32, 32, 48, 2688))
RANKS = 4

# THE MESH'S OWN CROSS-SECTIONAL AREA, one per level: sum(0/V) / LZ of the BUILT
# mesh.  THE BAND DEPENDS ON THIS, so it is registered as a NUMBER and
# build_f27.py REFUSES if the mesh it builds does not reproduce it.  The
# butterfly's wall faces are CHORDS of the circle, so the meshed domain is a
# polygon INSCRIBED in the pipe and its area is short of pi R^2 by O(h^2).  That
# deficit is the DOMINANT error channel at these resolutions and it is not a
# defect -- it is second-order geometry, and the composite model below carries it.
A_MESH = dict(coarse=3.121445152258, medium=3.136548490546, fine=3.140331156954)
A_MESH_TOL = 1.0e-9

# THE SAME-STENCIL REFERENCE for the REPORTED bulk mean, one per level: the volume-weighted mean
# of the EXACT axial velocity at t = T_END over the BUILT mesh's own cell centres
# and cell volumes, / U_REF.  Registered as NUMBERS because the mesh is a
# deterministic function of the frozen blockMeshDict template at (nc, nr, nz);
# grade_f27.py RECOMPUTES each from the run's own 0/C and 0/V and REFUSES if it
# differs by more than W_REF_TOL.  (F17b AMENDMENT 1: the reference goes through
# the SAME stencil as the solved value, so a zero-error solver reads zero.)
W_REF_MESH = dict(coarse=0.649820058760990,
                  medium=0.644677639755022,
                  fine=0.643390292465464)
W_REF_TOL = 1.0e-9                       # ascii 0/C, 0/V at writePrecision 12 round-trip to ~1e-12 relative;
                                        # 1e-9 absolute is 5 orders below the gate-2 band half-width 2.76e-04

GATED_QUANTITIES = ("E2", "Einf")        # W (the bulk mean) is REPORTED-NOT-GATED; see the module docstring
BAND_FACTOR = 5.0                       # the one declared band parameter; see the docstring
FO_CEILING = 5.0                        # registered diffusion-number ceiling; see control_diffusion_number
UNIFORMITY_FRACTION = 0.1               # a level's axial/azimuthal non-uniformity must sit below this x its
                                        # own predicted E2, else the level is NOT_UNIFORM (rule 5 limb 1)
# --- L-346: the resolution floors, DERIVED FROM THIS LADDER'S OWN PREDICTED
#     FINE-LEVEL DISCRETISATION ERROR.  Both windows are DRIVEN in the controls.
PERIOD_TOL = 1.0e-6                     # gate-1 plateau: ||U(T) - U(T-PERIOD)||_2,V / U_REF
W_PERIOD_TOL = 2.0e-6                   # bulk-mean plateau (REPORTED channel): |W(T) - W(T-PERIOD)|
P_SOLVER_TOL = 1.0e-10                  # matches system/fvSolution
U_SOLVER_TOL = 1.0e-12                  # matches system/fvSolution
PLATEAU_UPPER_FRACTION = 0.1            # a plateau tolerance must be <= this x the predicted fine error
PLATEAU_LOWER_MARGIN = 10.0             # ... and >= this x the model's own predicted period-to-period change

LAMBDA = complex(0.0, OMEGA / NU) ** 0.5   # sqrt(i omega / nu), principal root


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# GEOMETRY OF THE LADDER
# ---------------------------------------------------------------------------
def cells_of(nc, nr, nz):
    """Butterfly cross-section: one nc x nc core block plus four nr x nc ring
    blocks, extruded nz cells in z."""
    return (nc * nc + 4 * nc * nr) * nz


def model_nr_of(nc, nr):
    """The level's OWN radial cell count along the +x ray: nc/2 cells through the
    Cartesian core block, then nr through the O-ring.  This is what the 1-D model
    is solved on, so the model refines by exactly 2 with the mesh."""
    if nc % 2:
        refuse("nc must be even so the +x ray crosses nc/2 core cells; got %d" % nc)
    return nc // 2 + nr


def h_of(nc, nr, nz):
    """Representative cell size, the SAME definition roache_triple uses at dim 3:
    (V / N) ** (1/3) with V the pipe volume pi R^2 LZ."""
    return (math.pi * R ** 2 * LZ / cells_of(nc, nr, nz)) ** (1.0 / 3.0)


def dt_of(steps):
    return T_END / float(steps)


LEVEL_NAMES = [nm for nm, _c, _r, _z, _s in LEVELS]
CELLS = dict((nm, cells_of(nc, nr, nz)) for nm, nc, nr, nz, _s in LEVELS)
STEPS = dict((nm, s) for nm, _c, _r, _z, s in LEVELS)
MODEL_NR = dict((nm, model_nr_of(nc, nr)) for nm, nc, nr, _z, _s in LEVELS)
NCNRNZ = dict((nm, (nc, nr, nz)) for nm, nc, nr, nz, _s in LEVELS)


# ---------------------------------------------------------------------------
# THE EXACT SOLUTION
# ---------------------------------------------------------------------------
def _i0(z):
    from scipy.special import iv
    return iv(0, z)


def u_exact(r, t, lam=LAMBDA):
    """Axial velocity of the Womersley pipe solution at radius r, time t."""
    r = np.asarray(r, dtype=float)
    prof = (A_DRIVE / (1j * OMEGA)) * (1.0 - _i0(lam * r) / _i0(lam * R))
    return np.real(prof * np.exp(1j * OMEGA * t))


def u_vector_exact(x, y, t):
    """(u_x, u_y, u_z) at cartesian cell centres: the flow is purely axial."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    uz = u_exact(np.hypot(x, y), t)
    return np.column_stack([np.zeros_like(uz), np.zeros_like(uz), uz])


def u_centreline_exact(t=T_END):
    return float(u_exact(0.0, t) / U_REF)


# ---------------------------------------------------------------------------
# THE DISCRETE MODEL -- the solver's own radial discretisation, solved directly
# ---------------------------------------------------------------------------
def r_eff_of(name):
    """The radius of the circle with the BUILT mesh's own cross-sectional area.
    Read from A_MESH, which build_f27.py pins against the mesh it builds."""
    return math.sqrt(A_MESH[name] / (math.pi * LZ))


def discrete_solution(nr, steps, wall_radius=R, wall_coeff=2.0, axis_flux=0.0):
    """Cell-centred cylindrical FV in r (nr cells over [0, R]), no-slip wall,
    BDF2 with an Euler-implicit first step (OpenFOAM `backward`), cosine source
    at the new time level, started from the EXACT profile at t = 0 (as the case
    is: build_f27.py writes 0/U = u_exact at the mesh's own cell centres).

    `wall_coeff` = 2 is the no-slip face gradient (0 - u_P)/(dr/2); the planted
    control passes 0 (a zero-gradient wall).  `axis_flux` = 0 is the symmetry
    condition at r = 0, carried by the vanishing face area there.
    """
    from scipy.linalg import solve_banded
    if nr < 4 or steps < 4:
        refuse("model needs nr >= 4 and steps >= 4; got %r, %r" % (nr, steps))
    dr = float(wall_radius) / float(nr)
    rc = (np.arange(nr) + 0.5) * dr
    rf = np.arange(nr + 1) * dr
    vol = 2.0 * math.pi * rc * dr                       # annular control volumes, EXACT
    lo = np.zeros(nr); di = np.zeros(nr); up = np.zeros(nr)
    for j in range(nr):
        cw = (rf[j] / (rc[j] * dr * dr)) if j > 0 else axis_flux
        ce = (wall_coeff if j == nr - 1 else 1.0) * rf[j + 1] / (rc[j] * dr * dr)
        lo[j], up[j], di[j] = cw, ce, -(cw + ce)
    dt = dt_of(steps)
    spp = steps / (T_END / PERIOD)
    if abs(spp - round(spp)) > 1e-9:
        refuse("steps %d is not an integer number of steps per period at T_END = %g" % (steps, T_END))
    nspp = int(round(spp))
    # snapshots at EVERY period boundary t = m + PHASE_DEG/360 (m = 0 .. N_PERIODS),
    # so the transient's decay is MEASURED across the run and not asserted once.
    snap_idx = dict((steps - m * nspp, m) for m in range(0, N_PERIODS + 1))
    idx_prev = steps - nspp                             # index of t = T_END - PERIOD
    u = u_exact(rc, 0.0)
    u_prev, u_at_prev_period, snaps = None, None, {}
    for k in range(steps):
        t1 = (k + 1) * dt
        if k == 0:
            c, rhs = 1.0 / dt, u / dt + A_DRIVE * math.cos(OMEGA * t1)
        else:
            c, rhs = 1.5 / dt, (2.0 * u - 0.5 * u_prev) / dt + A_DRIVE * math.cos(OMEGA * t1)
        ab = np.zeros((3, nr))
        ab[0, 1:] = -NU * up[:-1]
        ab[1, :] = c - NU * di
        ab[2, :-1] = -NU * lo[1:]
        u_new = solve_banded((1, 1), ab, rhs)
        u_prev, u = u, u_new
        if k + 1 in snap_idx:
            snaps[snap_idx[k + 1]] = u.copy()
        if k + 1 == idx_prev:
            u_at_prev_period = u.copy()
    if u_at_prev_period is None or 0 not in snaps:
        refuse("model never reached t = T_END - PERIOD")
    err = u - u_exact(rc, T_END)
    sv = float(np.sum(vol))
    # the period-to-period change at each completed period boundary, coarse->fine in TIME
    decay = []
    for m in range(N_PERIODS - 1, -1, -1):
        if m in snaps and (m + 1) in snaps:
            d = snaps[m] - snaps[m + 1]
            decay.append(float(math.sqrt(np.sum(vol * d ** 2) / sv) / U_REF))
    return dict(nr=nr, steps=steps, dr=dr, dt=dt, rc=rc, vol=vol, u_model=u, err=err, decay=decay,
                E2_pred=float(math.sqrt(np.sum(vol * err ** 2) / sv) / U_REF),
                Einf_pred=float(np.max(np.abs(err)) / U_REF),
                wall_radius=float(wall_radius),
                W_err_pred=float(np.sum(vol * err) / sv / U_REF),
                period_change_pred=float(math.sqrt(np.sum(vol * (u - u_at_prev_period) ** 2) / sv) / U_REF),
                W_period_change_pred=float(abs(np.sum(vol * (u - u_at_prev_period)) / sv) / U_REF),
                courant=float(np.max(np.abs(u)) * dt / dr))


_CACHE = {}


def solved(name):
    if name not in MODEL_NR:
        refuse("unknown level %r" % name)
    if name not in _CACHE:
        # THE COMPOSITE MODEL.  The wall sits at the radius of the circle with the
        # BUILT mesh's own cross-sectional area, so the model carries BOTH error
        # channels -- radial discretisation AND the inscribed-polygon geometry --
        # while the error is still measured against the TRUE (radius R) exact
        # solution.  R_eff -> R at second order, so the composite prediction is
        # still O(h^2), and control_ladder_is_geometrically_similar drives that.
        _CACHE[name] = discrete_solution(MODEL_NR[name], STEPS[name], wall_radius=r_eff_of(name))
    return _CACHE[name]


def predictions():
    """Every level is SOLVED directly by the model -- nothing is extrapolated."""
    if "table" not in _CACHE:
        tab = []
        for nm in LEVEL_NAMES:
            m = solved(nm)
            nc, nr, nz = NCNRNZ[nm]
            tab.append(dict(name=nm, nc=nc, nr=nr, nz=nz, cells=CELLS[nm], steps=STEPS[nm],
                            model_nr=MODEL_NR[nm], h=h_of(nc, nr, nz), dr_model=m["dr"], dt=m["dt"],
                            E2_pred=m["E2_pred"], Einf_pred=m["Einf_pred"], W_err_pred=m["W_err_pred"],
                            r_eff=m["wall_radius"], area_deficit=math.pi * R ** 2 * LZ - A_MESH[nm],
                            Fo=NU * m["dt"] / (R / MODEL_NR[nm]) ** 2, h_radial=R / MODEL_NR[nm],
                            uniformity_tol=UNIFORMITY_FRACTION * m["E2_pred"],
                            W_ref_mesh=W_REF_MESH[nm], W_pred=W_REF_MESH[nm] + m["W_err_pred"],
                            period_change_pred=m["period_change_pred"],
                            W_period_change_pred=m["W_period_change_pred"],
                            courant=m["courant"], source="solved directly by the 1-D cylindrical FV model"))
        _CACHE["table"] = tab
    return _CACHE["table"]


def model_orders():
    t = dict((r["name"], r) for r in predictions())
    lr = math.log(t["coarse"]["h"] / t["medium"]["h"])
    return (math.log(t["coarse"]["E2_pred"] / t["medium"]["E2_pred"]) / lr,
            math.log(t["coarse"]["Einf_pred"] / t["medium"]["Einf_pred"]) / lr)


def model_triples():
    """L-345, EXECUTABLE: the registered model's OWN predicted triple for EVERY
    gated quantity, pushed through the SAME classifier that will grade the run."""
    t = dict((r["name"], r) for r in predictions())
    cells = tuple(t[nm]["cells"] for nm in LEVEL_NAMES)
    e2 = tuple(t[nm]["E2_pred"] for nm in LEVEL_NAMES)
    ei = tuple(t[nm]["Einf_pred"] for nm in LEVEL_NAMES)
    wv = tuple(t[nm]["W_pred"] for nm in LEVEL_NAMES)
    return dict(E2=RT.triple_from_cells(e2[0], e2[1], e2[2], cells[0], cells[1], cells[2], dim=3),
                Einf=RT.triple_from_cells(ei[0], ei[1], ei[2], cells[0], cells[1], cells[2], dim=3),
                W_reported_not_gated=RT.triple_from_cells(wv[0], wv[1], wv[2],
                                                          cells[0], cells[1], cells[2], dim=3))


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_symbolic_substitution():
    try:
        import sympy as sp
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    r, t = sp.symbols("r t", positive=True)
    lam = sp.symbols("lambda")
    nu, w, A, Rs = sp.symbols("nu omega A R", positive=True)
    U = (A / (sp.I * w)) * (1 - sp.besseli(0, lam * r) / sp.besseli(0, lam * Rs)) * sp.exp(sp.I * w * t)
    res = sp.diff(U, t) - nu * (sp.diff(U, r, 2) + sp.diff(U, r) / r) - A * sp.exp(sp.I * w * t)
    res = sp.simplify(sp.expand(sp.simplify(res)).subs(lam ** 2, sp.I * w / nu))
    res = sp.simplify(res.rewrite(sp.besseli).subs(lam ** 2, sp.I * w / nu))
    if sp.simplify(res) != 0:
        refuse("SYMBOLIC SUBSTITUTION FAILED: axial-momentum residual %s is not identically zero" % res)
    rng = np.random.RandomState(27)
    rs, ts = rng.uniform(1e-3, R, 200), rng.uniform(0.0, T_END, 200)
    from scipy.special import ivp
    prof = lambda rr: (A_DRIVE / (1j * OMEGA)) * (1.0 - _i0(LAMBDA * rr) / _i0(LAMBDA * R))
    dprof = lambda rr: -(A_DRIVE / (1j * OMEGA)) * LAMBDA * ivp(0, LAMBDA * rr, 1) / _i0(LAMBDA * R)
    d2prof = lambda rr: -(A_DRIVE / (1j * OMEGA)) * LAMBDA ** 2 * ivp(0, LAMBDA * rr, 2) / _i0(LAMBDA * R)
    e = np.exp(1j * OMEGA * ts)
    ut = np.real(1j * OMEGA * prof(rs) * e)
    lap = np.real((d2prof(rs) + dprof(rs) / rs) * e)
    resid = ut - NU * lap - A_DRIVE * np.cos(OMEGA * ts)
    if np.max(np.abs(resid)) > 1e-11:
        refuse("NUMERIC RESIDUAL of the exact solution is %.3e, not round-off" % np.max(np.abs(resid)))
    wall = float(np.max(np.abs(u_exact(R, ts[:8]))))
    if wall > 1e-14:
        refuse("the exact solution does not vanish at the wall: %.3e" % wall)
    if abs(R * math.sqrt(OMEGA / NU) - ALPHA) > 1e-12:
        refuse("Womersley number is not %g" % ALPHA)
    return dict(control="symbolic_substitution_into_unsteady_axisymmetric_axial_momentum",
                residual=str(res), numeric_residual_max=float(np.max(np.abs(resid))),
                wall_value_max=wall, alpha=ALPHA, nu=NU, passed=True)


def control_substitution_is_able_to_fail():
    import sympy as sp
    r, t = sp.symbols("r t", positive=True)
    lam = sp.symbols("lambda")
    nu, w, A, Rs = sp.symbols("nu omega A R", positive=True)
    lp = sp.Rational(11, 10) * lam                                 # PLANT: 1.1 lambda
    U = (A / (sp.I * w)) * (1 - sp.besseli(0, lp * r) / sp.besseli(0, lp * Rs)) * sp.exp(sp.I * w * t)
    res = sp.diff(U, t) - nu * (sp.diff(U, r, 2) + sp.diff(U, r) / r) - A * sp.exp(sp.I * w * t)
    res = sp.simplify(sp.expand(sp.simplify(res)).subs(lam ** 2, sp.I * w / nu))
    if sp.simplify(res) == 0:
        refuse("PLANTED CONTROL FAILED: lambda planted at 1.1 lambda still gave zero residual")
    # and numerically, through the SAME evaluator the real profile uses
    rr = np.linspace(0.05, R, 40)
    good = u_exact(rr, T_END)
    bad = u_exact(rr, T_END, lam=1.1 * LAMBDA)
    if float(np.max(np.abs(good - bad))) < 1e-3 * U_REF:
        refuse("PLANTED CONTROL FAILED numerically: 1.1 lambda moved the profile by only %.3e" %
               float(np.max(np.abs(good - bad))))
    return dict(control="PZ-F27-LAMBDA_planted_1.1lambda_must_be_nonzero_symbolically_and_numerically",
                planted_factor=1.1, residual_is_zero=False,
                max_profile_shift=float(np.max(np.abs(good - bad))), passed=True)


def control_bessel_two_independent_implementations():
    """The profile is a Bessel function; a wrong Bessel is a wrong reference that
    no substitution catches, because the substitution is symbolic.  scipy's
    `iv` and mpmath's `besseli` are independent implementations; they must agree
    to 1e-13 over the whole ladder's radii, and a PLANTED order (I1 for I0) must
    be seen.  Also DRIVEN: I0(lambda r) == J0(i^{3/2} alpha r / R), the form the
    brief and the literature write the Womersley profile in."""
    import mpmath as mp
    rr = np.linspace(0.0, R, 33)
    a = _i0(LAMBDA * rr)
    b = np.array([complex(mp.besseli(0, mp.mpc(float((LAMBDA * x).real), float((LAMBDA * x).imag))))
                  for x in rr])
    rel = float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300)))
    if rel > 1e-13:
        refuse("BESSEL CROSS-CHECK FAILED: scipy.special.iv and mpmath.besseli differ by %.3e" % rel)
    from scipy.special import iv
    planted = iv(1, LAMBDA * rr)                                    # PLANT: order 1 for order 0
    if float(np.max(np.abs(planted - a))) < 1e-6:
        refuse("BESSEL PLANTED CONTROL FAILED: I1 was indistinguishable from I0")
    # J0(i^{3/2} alpha r / R) form
    from scipy.special import jv
    arg = (complex(0.0, 1.0) ** 1.5) * ALPHA * rr / R
    j = jv(0, arg)
    relj = float(np.max(np.abs(j - a) / np.maximum(np.abs(a), 1e-300)))
    if relj > 1e-12:
        refuse("J0(i^{3/2} alpha r/R) does not equal I0(lambda r): rel %.3e" % relj)
    return dict(control="PZ-F27-BESSEL_scipy_vs_mpmath_and_J0_i32_form_with_planted_order",
                scipy_vs_mpmath_rel=rel, J0_form_rel=relj,
                planted_order_shift=float(np.max(np.abs(planted - a))), passed=True)


def control_ladder_is_geometrically_similar():
    """MESH_STANDARD 9.2: the refinement RECIPE is held fixed and every count
    doubles.  There is no grading anywhere in this ladder (simpleGrading (1 1 1)
    in every block at every level), so there is no branch a guard can flip."""
    rows = predictions()
    rh = [rows[i]["h"] / rows[i + 1]["h"] for i in range(2)]
    rt = [rows[i]["dt"] / rows[i + 1]["dt"] for i in range(2)]
    rn = [rows[i + 1]["cells"] / rows[i]["cells"] for i in range(2)]
    rm = [rows[i + 1]["model_nr"] / rows[i]["model_nr"] for i in range(2)]
    if max(abs(x - 2.0) for x in rh + rt + rm) > 1e-12 or max(abs(x - 8.0) for x in rn) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h, dt and model_nr with cells x8: %s %s %s %s"
               % (rh, rt, rn, rm))
    for i in range(2):
        a, b = rows[i], rows[i + 1]
        if (b["nc"], b["nr"], b["nz"]) != (2 * a["nc"], 2 * a["nr"], 2 * a["nz"]):
            refuse("level %s is not exactly 2x level %s in ALL THREE directions" % (b["name"], a["name"]))
        if a["nc"] * b["nr"] != b["nc"] * a["nr"]:
            refuse("the core:ring cell-count recipe nc:nr is not held fixed across levels")
    for nm, nc, nr, nz, s in LEVELS:
        if abs(s - T_END / PERIOD * STEPS_PER_PERIOD[nm]) > 1e-9:
            refuse("level %s: steps %d is not T_END/PERIOD x %d" % (nm, s, STEPS_PER_PERIOD[nm]))
    if abs(T_END - 5.25) > 1e-12:
        refuse("T_END is not the registered 5.25")
    return dict(control="constant_ratio_refinement_h_dt_and_model_nr_recipe_fixed_no_grading_anywhere",
                h_ratios=rh, dt_ratios=rt, cell_ratios=rn, model_nr_ratios=rm,
                grading="simpleGrading (1 1 1) in every block at every level; no first-cell or expansion "
                        "parameter exists, so MESH_STANDARD 9.2's branch-flip hazard cannot arise",
                passed=True)


def control_model_is_second_order_and_sensitive():
    p_e2, p_w = model_orders()
    if not (1.7 <= p_e2 <= 2.3 and 1.7 <= p_w <= 2.3):
        refuse("the model's predicted errors do not scale as h^2: orders %.3f (E2), %.3f (W)" % (p_e2, p_w))
    m = solved("coarse")
    planted_wall = discrete_solution(MODEL_NR["coarse"], STEPS["coarse"], wall_coeff=0.0)
    if planted_wall["E2_pred"] < 10.0 * m["E2_pred"]:
        refuse("PLANTED CONTROL FAILED: a zero-gradient wall did not move the model's E2 by 10x "
               "(%.3e vs %.3e)" % (planted_wall["E2_pred"], m["E2_pred"]))
    planted_axis = discrete_solution(MODEL_NR["coarse"], STEPS["coarse"], axis_flux=4.0 / (R / MODEL_NR["coarse"]) ** 2)
    if planted_axis["E2_pred"] < 10.0 * m["E2_pred"]:
        refuse("PLANTED CONTROL FAILED: a non-zero axis flux did not move the model's E2 by 10x "
               "(%.3e vs %.3e)" % (planted_axis["E2_pred"], m["E2_pred"]))
    if max(r["courant"] for r in predictions()) > 0.5:
        refuse("Courant number above 0.5 at some level")
    return dict(control="model_second_order_and_sees_planted_wall_and_axis_stencil_defects",
                model_orders=dict(E2=p_e2, W=p_w), planted_wall_E2=planted_wall["E2_pred"],
                planted_axis_E2=planted_axis["E2_pred"], clean_E2=m["E2_pred"],
                courant_max=max(r["courant"] for r in predictions()), passed=True)


def control_L345_model_triples_are_gradeable():
    """L-345, at registration and before compute: the registered model's own
    triple for EVERY gated quantity, through the SAME classifier, at the SAME
    dim.  A DEGENERATE / STAGNANT / OSCILLATORY / EXACT prediction is a
    REGISTRATION DEFECT and this control REFUSES on it."""
    tr = model_triples()
    bad = dict((k, v["state"]) for k, v in tr.items()
               if k in GATED_QUANTITIES and v["state"] != "CONVERGING")
    if bad:
        refuse("L-345: the registered model's OWN triple is not CONVERGING for %s; that is a registration "
               "defect, not a run finding. Fix the levels or the gate quantity BEFORE freezing." % json.dumps(bad))
    # a positive control: a deliberately DEGENERATE triple must be SEEN as such
    cells = tuple(CELLS[nm] for nm in LEVEL_NAMES)
    deg = RT.triple_from_cells(1.2, 1.1, 1.0, cells[0], cells[1], cells[2], dim=3)
    if deg["state"] != "DEGENERATE":
        refuse("L-345 CONTROL FAILED: an equal-increment triple was classified %r, not DEGENERATE" % deg["state"])
    return dict(control="PZ-F27-L345_model_triples_through_the_grading_classifier_with_a_degenerate_positive_control",
                dim=3, gated=list(GATED_QUANTITIES),
                reported_not_gated=[k for k in tr if k not in GATED_QUANTITIES],
                states=dict((k, v["state"]) for k, v in tr.items()),
                orders=dict((k, v.get("order")) for k, v in tr.items()),
                GCI_pct=dict((k, v.get("GCI_pct")) for k, v in tr.items()),
                r21=tr["E2"]["r21"], r32=tr["E2"]["r32"],
                degenerate_positive_control=deg["state"], passed=True)


def control_L346_resolution_derived_from_this_ladder():
    """L-346, at registration: EVERY resolution floor is derived from THIS
    ladder's predicted FINE-level discretisation error, and each derivation is
    DRIVEN here rather than asserted in prose.  Nothing is inherited from F21."""
    rows = predictions()
    fine = rows[-1]
    checks = []

    # (1) the two plateau tolerances sit inside their derived windows
    for label, tol, pred_change_key, pred_err in (
            ("PERIOD_TOL", PERIOD_TOL, "period_change_pred", fine["E2_pred"]),
            ("W_PERIOD_TOL", W_PERIOD_TOL, "W_period_change_pred", abs(fine["W_err_pred"]))):
        # PERIOD_TOL is the GATED plateau (both gates read the field); W_PERIOD_TOL
        # belongs to the REPORTED bulk mean and is derived by the same rule anyway.
        worst = max(r[pred_change_key] for r in rows)
        lo, hi = PLATEAU_LOWER_MARGIN * worst, PLATEAU_UPPER_FRACTION * pred_err
        if not (lo <= tol <= hi):
            refuse("L-346: %s = %.3e is outside its derived window [%.3e, %.3e] (>= %g x the model's worst "
                   "predicted period-to-period change %.3e, <= %g x the predicted FINE error %.3e)"
                   % (label, tol, lo, hi, PLATEAU_LOWER_MARGIN, worst, PLATEAU_UPPER_FRACTION, pred_err))
        checks.append(dict(tolerance=label, value=tol, window=[lo, hi], model_worst_change=worst,
                           predicted_fine_error=pred_err))

    # (2) the ITERATIVE floor: a worst-case bound on the accumulated per-step
    #     final-residual contribution to the graded quantity, over THIS ladder's
    #     fine-level step count, at least an order below the predicted fine error.
    bound = STEPS["fine"] * max(P_SOLVER_TOL, U_SOLVER_TOL)
    if bound > PLATEAU_UPPER_FRACTION * fine["E2_pred"]:
        refuse("L-346: the iterative floor bound %.3e (=%d steps x %.1e) is not an order below the predicted "
               "FINE E2 %.3e; tighten the solver tolerances or the step count BEFORE freezing"
               % (bound, STEPS["fine"], max(P_SOLVER_TOL, U_SOLVER_TOL), fine["E2_pred"]))
    checks.append(dict(tolerance="iterative_floor_bound", value=bound,
                       window=[0.0, PLATEAU_UPPER_FRACTION * fine["E2_pred"]],
                       basis="steps_fine x max(p_tol, U_tol): a per-step final residual can move the graded "
                             "quantity by at most that much, and the bound assumes NO cancellation over steps"))

    # (3) N_PERIODS: the model's OWN measured residual transient at T_END is at
    #     least an order below the predicted fine error, AT EVERY LEVEL.
    for r in rows:
        if r["period_change_pred"] > PLATEAU_UPPER_FRACTION * r["E2_pred"]:
            refuse("L-346: at level %s the model's residual transient at T_END (%.3e) is not an order below "
                   "that level's predicted E2 (%.3e); N_PERIODS = %d is too few for THIS ladder"
                   % (r["name"], r["period_change_pred"], r["E2_pred"], N_PERIODS))
    # a positive control: the transient's decay is MEASURED across the run.  The
    # change from period 1 to 2 must be at least 10x the change at T_END, and the
    # sequence must be monotonically decreasing -- so N_PERIODS is what makes the
    # residual small, and a shorter run would NOT have been adequate.
    dec = solved("fine")["decay"]
    if len(dec) < 2:
        refuse("L-346 CONTROL FAILED: fewer than two period-boundary snapshots were taken")
    if not all(dec[i] > dec[i + 1] for i in range(len(dec) - 1)):
        refuse("L-346 CONTROL FAILED: the model's period-to-period change is not monotonically decaying: %s" % dec)
    if dec[0] < 10.0 * dec[-1]:
        refuse("L-346 CONTROL FAILED: the first period-boundary change %.3e is not 10x the change at T_END "
               "%.3e, so N_PERIODS = %d is not doing measurable work" % (dec[0], dec[-1], N_PERIODS))
    return dict(control="PZ-F27-L346_every_floor_derived_from_THIS_ladders_predicted_fine_error",
                inherited_from_a_coarser_ladder="nothing: N_PERIODS, STEPS_PER_PERIOD, both plateau "
                                                "tolerances and both solver tolerances are set here",
                checks=checks, n_periods=N_PERIODS,
                measured_transient_decay_at_fine=dec,
                decay_first_over_last=dec[0] / dec[-1],
                passed=True)


def control_diffusion_number_and_courant():
    """THE GROUP F21 DIED ON, MEASURED HERE AND REGISTERED.

    A ladder that refines dt PROPORTIONAL to h holds the Courant number Co fixed
    but makes the diffusion number Fo = nu dt / h^2 DOUBLE at every level.  That
    doubling is universal and by itself benign; what is not benign is the
    ABSOLUTE value F21_WOMERSLEY reached.  Measured across the cfd unsteady
    family by the cfd supervisor's own triage, 2026-08-27:

        F21_WOMERSLEY   fine DIVERGED    Fo = 10.72 -> 21.45 -> 42.89
        F22_LAMB_OSEEN  PASS x2          Fo =  0.147 ->  0.295 ->  0.590
        F18b_TG2D_EXT   running          Fo =  0.208 ->  0.415 ->  0.830
        F18_TG2D        PASS, closed     Fo =  0.052 ->  0.104 ->  0.208

    F21's fine level ran at 73x the diffusion number of every other case in the
    family and is the only one that failed, with a smooth, WALL-LOCALIZED,
    two-dimensional mode at wavenumber 6 (not checkerboard) in a direction the
    exact solution is invariant along, at Re = 1.3.

    THIS CONTROL DOES NOT CLAIM Fo IS THE MECHANISM.  The supervisor's triage
    explicitly withheld that: correlation is not mechanism, and the wall stencil
    at h = 0.0039 and `backward` BDF2 under PISO with nOuterCorrectors 1 remain
    live alternatives.  What is registered here is (a) THIS ladder's three Fo
    values, (b) a ceiling FO_CEILING = 5.0 chosen BEFORE compute -- an order below
    the only measured failure and about 3x the highest measured pass -- and (c)
    the azimuthal and axial uniformity diagnostics that would CATCH the F21 mode
    directly if it appeared, whatever causes it.  A registered ceiling on a
    correlate is a cheap guard; it is not an explanation and is not offered as one.
    """
    rows = predictions()
    fo = [r["Fo"] for r in rows]
    co = [r["courant"] for r in rows]
    if max(fo) > FO_CEILING:
        refuse("the diffusion number Fo = nu dt / h_r^2 reaches %.4f at the fine level, above the registered "
               "ceiling %.4f. F21_WOMERSLEY's fine level DIVERGED at Fo = 42.89. Change alpha, R, omega or the "
               "time step BEFORE freezing." % (max(fo), FO_CEILING))
    ratios = [fo[i + 1] / fo[i] for i in range(2)]
    if max(abs(x - 2.0) for x in ratios) > 1e-9:
        refuse("Fo does not double per level (%s); the ladder is not refining dt proportional to h" % ratios)
    # Co is a ladder invariant to within the composite model's own R_eff drift:
    # the model's radial spacing is R_eff(level)/nr and R_eff -> R at order 2, so
    # Co varies by ~1e-3 relative across the ladder and by nothing else.
    if max(abs(c / co[0] - 1.0) for c in co) > 1e-2:
        refuse("the Courant number is not a ladder invariant to 1 %% (%s)" % co)
    if max(co) > 0.5:
        refuse("Courant number above 0.5 at some level: %s" % co)
    return dict(control="diffusion_number_registered_with_the_F21_failure_recorded_beside_it",
                Fo=dict(zip(LEVEL_NAMES, fo)), Fo_ceiling=FO_CEILING, Fo_doubling_ratios=ratios,
                Courant=dict(zip(LEVEL_NAMES, co)),
                F21_fine_Fo_that_diverged=42.89, F22_fine_Fo_that_passed=0.590,
                mechanism_claim="NONE: Fo is the measured distinguishing group, not a demonstrated cause "
                                "(cfd-supervisor triage 2026-08-27, held to explicitly)",
                uniformity_tolerances=dict((r["name"], r["uniformity_tol"]) for r in rows),
                passed=True)


def control_same_stencil_reference_is_pinned():
    """The gate-2 reference W_REF_MESH is a property of the MESH, written by
    blockMesh before the solver starts, so it cannot be tuned to an answer.  It
    is registered as a NUMBER here and grade_f27.py recomputes it from the run's
    own 0/C and 0/V, refusing on a mismatch above W_REF_TOL.  Driven: the three
    registered references themselves form a CONVERGING triple at order ~2,
    which is what a geometrically similar mesh family must produce."""
    cells = tuple(CELLS[nm] for nm in LEVEL_NAMES)
    tr = RT.triple_from_cells(W_REF_MESH["coarse"], W_REF_MESH["medium"], W_REF_MESH["fine"],
                              cells[0], cells[1], cells[2], dim=3)
    if tr["state"] != "CONVERGING" or not (1.7 <= tr["order"] <= 2.3):
        refuse("the registered same-stencil references do not converge at order ~2: state %s order %s"
               % (tr["state"], tr.get("order")))
    if abs(W_REF_MESH["fine"] - u_bulk_exact_continuum()) > 5e-3:
        refuse("the fine mesh reference %.9f is not near the continuum bulk mean %.9f"
               % (W_REF_MESH["fine"], u_bulk_exact_continuum()))
    return dict(control="same_stencil_reference_registered_as_numbers_and_converging_at_order_2",
                references=dict(W_REF_MESH), state=tr["state"], order=tr["order"],
                continuum_bulk_mean=u_bulk_exact_continuum(), tolerance=W_REF_TOL, passed=True)


def u_bulk_exact_continuum(t=T_END, n=200001):
    """The continuum area-average (2/R^2) int_0^R u(r,t) r dr / U_REF, by a fine
    midpoint rule.  DISPLAY AND CONTROL ONLY -- no gate reads it: the gate's
    reference is the mesh's own volume-weighted mean (F17b AMENDMENT 1)."""
    r = (np.arange(n) + 0.5) * (R / n)
    return float(2.0 / R ** 2 * np.sum(u_exact(r, t) * r) * (R / n) / U_REF)


def selftest_predicate(controls):
    if len(controls) != 9:
        return False, "expected 9 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("9 controls green: the Bessel closed form satisfies the unsteady axisymmetric axial-momentum "
                  "equation identically under symbolic substitution and to round-off numerically, vanishes at "
                  "the wall, and has alpha = 4; lambda planted at 1.1 lambda makes the residual non-zero; two "
                  "independent Bessel implementations agree to 1e-13 and a planted order is seen; h, dt and the "
                  "model's radial count refine by exactly 2 with cells x8 and no grading parameter exists "
                  "anywhere; the discrete model is second order and sees planted wall and axis stencil defects; "
                  "L-345 -- both gated quantities' MODEL triples are CONVERGING through the grading classifier "
                  "at dim 3, with a DEGENERATE positive control; L-346 -- every resolution floor is derived "
                  "from THIS ladder's predicted fine-level error, driven, with the transient's decay MEASURED at "
                  "every period boundary; and the gate-2 same-stencil references are registered as numbers "
                  "that themselves converge at order 2; and the diffusion number Fo = 0.44 / 0.88 / 1.77 sits under "
                  "the registered ceiling 5.0, against F21_WOMERSLEY's fine level that DIVERGED at 42.89")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_bessel_two_independent_implementations(),
                control_ladder_is_geometrically_similar(), control_model_is_second_order_and_sensitive(),
                control_L345_model_triples_are_gradeable(),
                control_L346_resolution_derived_from_this_ladder(),
                control_diffusion_number_and_courant(),
                control_same_stencil_reference_is_pinned()]
    tab = predictions()
    tri = model_triples()
    if a.json:
        print(json.dumps(dict(constants=dict(R=R, LZ=LZ, core_frac=CORE_FRAC, nu=NU, omega=OMEGA, alpha=ALPHA,
                                             A=A_DRIVE, U_ref=U_REF, T_END=T_END, N_PERIODS=N_PERIODS,
                                             ranks=RANKS, band_factor=BAND_FACTOR, period_tol=PERIOD_TOL,
                                             W_period_tol=W_PERIOD_TOL),
                              levels=tab, W_REF_MESH=W_REF_MESH,
                              model_triples=dict((k, dict(state=v["state"], order=v.get("order"),
                                                          GCI_pct=v.get("GCI_pct"), r21=v["r21"], r32=v["r32"]))
                                                 for k, v in tri.items()),
                              u_centreline_exact=u_centreline_exact(),
                              u_bulk_exact_continuum=u_bulk_exact_continuum(),
                              controls=controls), indent=2, default=str))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab,
                              model_triples=dict((k, dict(state=v["state"], order=v.get("order")))
                                                 for k, v in tri.items()),
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("R=%g LZ=%g core_frac=%g nu=%.17g omega=%.17g alpha=%g A=%g U_ref=%.17g T_END=%g ranks=%d"
          % (R, LZ, CORE_FRAC, NU, OMEGA, ALPHA, A_DRIVE, U_REF, T_END, RANKS))
    for r in tab:
        print("%-7s nc=%d nr=%d nz=%d cells=%d steps=%d model_nr=%d h=%.6g dt=%.6g Co=%.4f  "
              "E2_pred=%.6e  W_err_pred=%.6e  W_ref=%.15f  period_change=%.3e"
              % (r["name"], r["nc"], r["nr"], r["nz"], r["cells"], r["steps"], r["model_nr"], r["h"], r["dt"],
                 r["courant"], r["E2_pred"], r["W_err_pred"], r["W_ref_mesh"], r["period_change_pred"]))
    for k, v in tri.items():
        print("model triple %-3s : %s order %.4f (dim 3)" % (k, v["state"], v.get("order", float("nan"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
