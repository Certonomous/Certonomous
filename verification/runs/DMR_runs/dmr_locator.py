#!/usr/bin/env python3
"""DMR locators per DMR_PREREGISTRATION.md section 4 (pre-committed detector).

Gate V : incident-shock x-position on the row nearest y=0.9 at t=0.2,
         midpoint-crossing of rho between pre-shock 1.4 and post-shock 8.0,
         searched in x in [2.5, 3.5]; exact reference 2.99568, tol +/-0.0231.
Gate P1: shock-front polyline x_front(y) (rightmost crossing of rho above
         2.7, scanning from the right, rows up to y=0.85); triple points =
         kinks; primary TP = lowest y where the front's lead over the exact
         incident line falls below 2 cells; secondary TP = max second
         difference of the front below the primary TP. Wall jet: max rho in
         y<0.1 behind the stem vs the plateau behind the stem at y in
         [0.2,0.4].
Gate P2: chi from the primary TP at writes t=0.10..0.20: least-squares line
         x = a + b*y; chi = atan2(1, b); intercept check vs x0=1/6.

Usage: dmr_locator.py <case> <N>
"""
import re, sys, json, math
import numpy as np

case, N = sys.argv[1], int(sys.argv[2])
dx = 1.0 / N
X0 = 1.0 / 6.0
SQ3 = math.sqrt(3.0)


def read_scalar(path):
    s = open(path).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\(\n(.*?)\n\)", s, re.S)
    n = int(m.group(1))
    v = np.fromstring(m.group(2), sep="\n")
    assert v.size == n, (v.size, n)
    return v


cx = read_scalar(f"{case}/0.2/Cx")
cy = read_scalar(f"{case}/0.2/Cy")
ix = np.rint(cx / dx - 0.5).astype(int)
iy = np.rint(cy / dx - 0.5).astype(int)
nx, ny = ix.max() + 1, iy.max() + 1


def grid(v):
    g = np.full((ny, nx), np.nan)
    g[iy, ix] = v
    return g


xc = (np.arange(nx) + 0.5) * dx
yc = (np.arange(ny) + 0.5) * dx


def x_incident(y, t):
    return X0 + (y + 20.0 * t) / SQ3


def front_x(row, xmin=0.5, xmax=4.0, level=2.7):
    """Rightmost x where rho crosses `level` from below (scanning from right)."""
    sel = (xc >= xmin) & (xc <= xmax)
    x, r = xc[sel], row[sel]
    for k in range(len(x) - 2, -1, -1):
        if r[k] >= level > r[k + 1]:
            f = (level - r[k + 1]) / (r[k] - r[k + 1])
            return x[k + 1] + f * (x[k] - x[k + 1])
    return None


def locate(t):
    rho = grid(read_scalar(f"{case}/{t:g}/rho"))
    # ---- incident shock on row nearest y=0.9 (Gate V uses t=0.2)
    j09 = int(np.argmin(np.abs(yc - 0.9)))
    row = rho[j09]
    sel = (xc >= 2.0) & (xc <= 3.8)
    x, r = xc[sel], row[sel]
    lvl = 0.5 * (1.4 + 8.0)
    xinc = None
    for k in range(len(x) - 1):
        if r[k] >= lvl > r[k + 1]:
            f = (lvl - r[k + 1]) / (r[k] - r[k + 1])
            xinc = x[k + 1] + f * (x[k] - x[k + 1])
    # ---- shock front polyline and primary TP
    jmax = int(0.85 / dx)
    ys, xs = [], []
    for j in range(jmax):
        fx = front_x(rho[j])
        if fx is not None:
            ys.append(yc[j])
            xs.append(fx)
    ys, xs = np.array(ys), np.array(xs)
    lead = xs - x_incident(ys, t)
    # primary TP: lowest y where the front's lead falls below 2 cells
    below = np.where(lead < 2 * dx)[0]
    tp = None
    if below.size:
        j = below[0]
        if j > 0:  # interpolate lead crossing 2*dx
            f = (lead[j - 1] - 2 * dx) / (lead[j - 1] - lead[j])
            ytp = ys[j - 1] + f * (ys[j] - ys[j - 1])
            xtp = xs[j - 1] + f * (xs[j] - xs[j - 1])
        else:
            ytp, xtp = ys[j], xs[j]
        tp = (float(xtp), float(ytp))
    # ---- secondary TP: strongest kink of the front below the primary TP
    tp2 = None
    if tp is not None:
        mask = ys < tp[1] - 2 * dx
        if mask.sum() > 6:
            yy, xx = ys[mask], xs[mask]
            d2 = np.abs(np.diff(xx, 2))
            k = int(np.argmax(d2)) + 1
            if d2.max() > 0.6 * dx:
                tp2 = (float(xx[k]), float(yy[k]), float(d2.max() / dx))
    # ---- wall jet (t=0.2 report): max rho in y<0.1 behind the stem
    jet = None
    if tp is not None:
        strip = rho[: int(0.1 / dx), :]
        stem_x = front_x(rho[0])
        if stem_x:
            sel2 = (xc > stem_x - 0.7) & (xc < stem_x)
            rho_jet = np.nanmax(strip[:, sel2])
            j1, j2 = int(0.2 / dx), int(0.4 / dx)
            sel3 = (xc > stem_x - 0.4) & (xc < stem_x - 0.1)
            plateau = float(np.nanmedian(rho[j1:j2][:, sel3]))
            jet = dict(rho_max_wall_strip=float(rho_jet), plateau_behind_stem=plateau,
                       stem_wall_x=float(stem_x))
    return dict(t=t, x_incident_y09=xinc, tp_primary=tp, tp_secondary=tp2, jet=jet)


times = [0.1, 0.12, 0.14, 0.16, 0.18, 0.2]
res = [locate(t) for t in times]

# Gate V
r02 = res[-1]
xexact = x_incident(0.9, 0.2)
# measured on the row nearest y=0.9: compare against exact at that row's y
j09 = int(np.argmin(np.abs(yc - 0.9)))
xexact_row = x_incident(yc[j09], 0.2)
gateV = dict(y_row=float(yc[j09]), x_measured=r02["x_incident_y09"],
             x_exact_at_row=float(xexact_row), x_exact_at_0p9=float(xexact),
             error=float(r02["x_incident_y09"] - xexact_row),
             tol=0.0231, locator_increment=dx,
             PASS=bool(abs(r02["x_incident_y09"] - xexact_row) <= 0.0231))

# Gate P2 inputs: chi fit
pts = [(r["tp_primary"][0], r["tp_primary"][1]) for r in res if r["tp_primary"]]
chi = None
if len(pts) >= 4:
    X = np.array([p[0] for p in pts]); Y = np.array([p[1] for p in pts])
    b, a = np.polyfit(Y, X, 1)  # x = a + b*y
    chi = math.degrees(math.atan2(1.0, b))
    x_at_wall = a
    gateP2 = dict(chi_deg=chi, x_intercept_at_wall=float(x_at_wall), x0=X0,
                  intercept_offset=float(x_at_wall - X0), intercept_tol=2 * dx,
                  n_samples=len(pts),
                  samples=[(float(x), float(y)) for x, y in pts])
else:
    gateP2 = dict(chi_deg=None, note="fewer than 4 TP samples")

out = dict(case=case, N=N, dx=dx, times=times, locates=res, gateV=gateV, gateP2=gateP2)
print(json.dumps(out, indent=1))
json.dump(out, open(f"{case}/locator_result.json", "w"), indent=1)
