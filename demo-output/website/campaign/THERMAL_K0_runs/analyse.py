#!/usr/bin/env python3
"""analyse.py -- the physics measurements for rung K0, and the residual histories.

    python3 analyse.py            # writes analysis.json next to this file

Measures, from the solved fields and nothing else:
  * K0a  Nusselt ratio  Q(g on)/Q(g off)  -- the advection-vs-conduction test.
         The g=0 twin is what makes this a test rather than a restatement that
         a hot wall heats a cold fluid.
  * K0b  U* and V*, the non-dimensional velocity extrema on the mid-planes,
         which is where a wall plume shows up if there is one.
  * K0b  S, the non-dimensional vertical stratification of the core. The pure
         conduction solution of this cavity has S = 0 exactly, so S is a real
         discriminator and not an identity.
  * residual histories for every case.

Cell centres are obtained from OpenFOAM (`writeCellCentres`), not assumed from
a guessed blockMesh ordering, and are deleted again afterwards.
"""

import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FOAM_BASHRC = os.environ.get("FOAM_BASHRC",
                             "/usr/lib/openfoam/openfoam2606/etc/bashrc")
L = 0.10
ALPHA = 1.589461e-05 / 0.706814     # nu/Pr, m^2/s


def latest_time(case):
    ts = []
    for e in os.listdir(case):
        if os.path.isdir(os.path.join(case, e)):
            try:
                ts.append((float(e), e))
            except ValueError:
                pass
    return sorted(ts)[-1][1]


def foam(case, args):
    cmd = f'. "{FOAM_BASHRC}" >/dev/null 2>&1 && cd {case!r} && {args}'
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)


def read_internal(path):
    """internalField of an ascii OpenFOAM field -> list of floats (scalar) or
    list of 3-tuples (vector). Handles the `uniform` form too."""
    txt = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<(\w+)>\s*\n?\s*(\d+)\s*\n\((.*?)\n\)\s*;",
                  txt, re.S)
    if not m:
        u = re.search(r"internalField\s+uniform\s+([^;]+);", txt)
        if u:
            v = u.group(1).strip()
            if v.startswith("("):
                trip = tuple(float(x) for x in v.strip("()").split())
                return ("uniform_vector", trip)
            return ("uniform_scalar", float(v))
        raise SystemExit(f"cannot parse internalField in {path}")
    kind, n, body = m.group(1), int(m.group(2)), m.group(3)
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", body)]
    if kind == "vector":
        assert len(nums) == 3 * n, (len(nums), n)
        return [tuple(nums[3 * i:3 * i + 3]) for i in range(n)]
    assert len(nums) == n, (len(nums), n)
    return nums


def cell_centres(case, t):
    r = foam(case, f"postProcess -func writeCellCentres -time {t}")
    if r.returncode != 0:
        raise SystemExit(r.stdout[-2000:] + r.stderr[-2000:])
    cx = read_internal(os.path.join(case, t, "Cx"))
    cy = read_internal(os.path.join(case, t, "Cy"))
    for f in ("C", "Cx", "Cy", "Cz"):
        try:
            os.remove(os.path.join(case, t, f))
        except OSError:
            pass
    return cx, cy


def residual_history(logpath):
    """{field: [initial residual per outer iteration]} from a solver log."""
    hist = {}
    pat = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")
    with open(logpath) as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                hist.setdefault(m.group(1), []).append(float(m.group(2)))
    return hist


def summarise_residuals(logpath):
    h = residual_history(logpath)
    out = {}
    for f, v in h.items():
        out[f] = dict(n=len(v), first=v[0], final=v[-1],
                      min=min(v), max_after_10=max(v[10:]) if len(v) > 10 else max(v),
                      at_1pct=v[max(0, len(v) // 100)],
                      at_10pct=v[max(0, len(v) // 10)],
                      at_50pct=v[len(v) // 2])
    return out


def main():
    res = {}

    # ---- residual histories ------------------------------------------------
    res["residuals"] = {}
    for c in sorted(os.listdir(HERE)):
        lp = os.path.join(HERE, c, "log.buoyantBoussinesqSimpleFoam")
        if os.path.isfile(lp):
            res["residuals"][c] = summarise_residuals(lp)

    # ---- K0a Nusselt -------------------------------------------------------
    aud = os.path.join(HERE, "audit")
    def qpatch(jf, patch):
        d = json.load(open(os.path.join(aud, jf)))
        return [p for p in d["patches"] if p["patch"] == patch][0]["Q_in_W"]

    q_on = qpatch("K0a_gon.json", "hotSource")
    q_off = qpatch("K0a_g0.json", "hotSource")
    res["K0a"] = dict(Q_hot_g_on_W=q_on, Q_hot_g_off_W=q_off,
                      Nu_ratio=q_on / q_off)

    # ---- K0b Nusselt, from the closed-form conduction denominator ----------
    qb_on = qpatch("K0b_gon.json", "hotWall")
    cal = json.load(open(os.path.join(aud, "K0b_g0_calibration.json")))
    q_cond_exact = cal["selftest_conduction"]["Q_closed_form_W"]
    q_cond_meas = cal["selftest_conduction"]["Q_measured_W"]
    res["K0b"] = dict(Q_hot_W=qb_on,
                      Q_conduction_closed_form_W=q_cond_exact,
                      Q_conduction_measured_W=q_cond_meas,
                      Nu_vs_closed_form=qb_on / q_cond_exact,
                      Nu_vs_measured_twin=qb_on / q_cond_meas)

    # ---- K0b plume and stratification --------------------------------------
    case = os.path.join(HERE, "K0b_cavity_Ra1e5")
    t = latest_time(case)
    cx, cy = cell_centres(case, t)
    U = read_internal(os.path.join(case, t, "U"))
    T = read_internal(os.path.join(case, t, "T"))
    n = len(T)

    xs = sorted(set(round(v, 9) for v in cx))
    ys = sorted(set(round(v, 9) for v in cy))
    nx, ny = len(xs), len(ys)
    xi = {v: i for i, v in enumerate(xs)}
    yi = {v: i for i, v in enumerate(ys)}
    grid_T = [[None] * nx for _ in range(ny)]
    grid_u = [[None] * nx for _ in range(ny)]
    grid_v = [[None] * nx for _ in range(ny)]
    for c in range(n):
        i, j = xi[round(cx[c], 9)], yi[round(cy[c], 9)]
        grid_T[j][i] = T[c]
        grid_u[j][i] = U[c][0]
        grid_v[j][i] = U[c][1]

    jm = ny // 2            # first row above mid-height
    im = nx // 2
    # mid-plane values by averaging the two rows/columns straddling it
    v_mid = [0.5 * (grid_v[jm - 1][i] + grid_v[jm][i]) for i in range(nx)]
    u_mid = [0.5 * (grid_u[j][im - 1] + grid_u[j][im]) for j in range(ny)]
    Vmax = max(v_mid); Vmin = min(v_mid)
    Umax = max(u_mid); Umin = min(u_mid)
    # WHERE the upward jet sits. A wall plume must peak within a boundary layer
    # of the hot wall; a peak in mid-cavity would mean something else entirely.
    x_vmax = xs[v_mid.index(Vmax)] / L
    x_vmin = xs[v_mid.index(Vmin)] / L

    Th, Tc = 300.546533, 299.453467
    dT = Th - Tc

    # vertical stratification of the core, at the geometric centre
    Tcol = [0.5 * (grid_T[j][im - 1] + grid_T[j][im]) for j in range(ny)]
    dy = L / ny
    # central difference across the centre, over the two straddling cells
    S_local = ((Tcol[jm] - Tcol[jm - 1]) / dy) * (L / dT)
    # least-squares slope over the middle 25% of the height, as a robustness check
    lo, hi = int(0.375 * ny), int(0.625 * ny)
    ysub = [(j + 0.5) * dy / L for j in range(lo, hi)]
    tsub = [(Tcol[j] - Tc) / dT for j in range(lo, hi)]
    mY = sum(ysub) / len(ysub); mT = sum(tsub) / len(tsub)
    S_fit = (sum((a - mY) * (b - mT) for a, b in zip(ysub, tsub))
             / sum((a - mY) ** 2 for a in ysub))

    res["K0b"].update(
        mesh=(nx, ny), time=t,
        v_max_ms=Vmax, v_min_ms=Vmin, u_max_ms=Umax, u_min_ms=Umin,
        V_star_max=Vmax * L / ALPHA, V_star_min=Vmin * L / ALPHA,
        x_over_L_at_v_max=x_vmax, x_over_L_at_v_min=x_vmin,
        U_star_max=Umax * L / ALPHA, U_star_min=Umin * L / ALPHA,
        stratification_S_central_difference=S_local,
        stratification_S_leastsq_mid25pct=S_fit,
        theta_at_centre=0.5 * (Tcol[jm] + Tcol[jm - 1] - 2 * Tc) / dT,
    )

    with open(os.path.join(HERE, "analysis.json"), "w") as fh:
        json.dump(res, fh, indent=2)

    # ---- report ------------------------------------------------------------
    p = print
    p("=" * 72)
    p("K0a -- does temperature actually TRANSPORT (advection vs conduction)?")
    p(f"  Q_hotSource, g on   = {q_on:.9e} W")
    p(f"  Q_hotSource, g OFF  = {q_off:.9e} W   (pure conduction, Nu = 1 by definition)")
    p(f"  Nu = ratio          = {q_on / q_off:.4f}")
    p("=" * 72)
    p("K0b -- plume and core stratification")
    p(f"  mesh {nx} x {ny}, time {t}")
    p(f"  v on mid-height plane : max {Vmax:+.6e}  min {Vmin:+.6e} m/s")
    p(f"  V* = v.L/alpha        : max {Vmax * L / ALPHA:+.3f}  min {Vmin * L / ALPHA:+.3f}")
    p(f"  upward jet peaks at x/L = {x_vmax:.5f} (hot wall at 0), "
      f"downward at x/L = {x_vmin:.5f} (cold wall at 1)")
    p(f"  u on mid-width plane  : max {Umax:+.6e}  min {Umin:+.6e} m/s")
    p(f"  U* = u.L/alpha        : max {Umax * L / ALPHA:+.3f}  min {Umin * L / ALPHA:+.3f}")
    p(f"  stratification S at centre (central difference) = {S_local:.4f}")
    p(f"  stratification S over middle 25% (least squares) = {S_fit:.4f}")
    p("    (pure conduction gives S = 0 exactly)")
    p(f"  Nu_hotWall vs closed-form conduction = {qb_on / q_cond_exact:.4f}")
    p("=" * 72)
    p("residual histories (initial residual of the outer iteration)")
    for c, h in res["residuals"].items():
        p(f"  {c}")
        for f in ("Ux", "Uy", "T", "p_rgh"):
            if f in h:
                d = h[f]
                p(f"    {f:<6} n={d['n']:<5} first={d['first']:.3e} "
                  f"10%={d['at_10pct']:.3e} 50%={d['at_50pct']:.3e} "
                  f"final={d['final']:.3e} min={d['min']:.3e}")
    p("=" * 72)


if __name__ == "__main__":
    main()
