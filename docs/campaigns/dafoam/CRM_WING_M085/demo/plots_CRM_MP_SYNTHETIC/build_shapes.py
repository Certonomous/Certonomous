#!/usr/bin/env python3
"""SYNTHETIC: generated, not computed; illustrative of the registered MP_R2/MP_R3
optimisation whose first design iteration has not completed.

THE BASELINE GEOMETRY IS REAL. It is the wing wall patch of `MP_R2/mp04`, read from
that case's own `constant/polyMesh` — 11,136 faces, 593,865 points. THE DEFORMATION IS
SYNTHETIC: a smooth washout twist and a small thickness redistribution, applied as a
span-varying map, of the order a few millimetres on a 3.25 m semi-span. It is what an
FFD design step of this kind LOOKS like; it is not one this lab computed.

Writes, all prefixed `synthetic_`:
    synthetic_section_eta{20,50,80}.png   baseline against deformed, three span stations
    synthetic_ffd_lattice.png             the REAL FFD lattice against its displaced form
"""
import csv, gzip, os, re, sys
import numpy as np

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/dafoam/CRM_WING_M085/demo",
                    "plots_CRM_MP_SYNTHETIC")
CASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/MP_R2/mp04"
FFD = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R3-crm-wing-mach085/MP_R2/FFD/wingFFD.xyz"
SCR = "/tmp/claude-1000/-home-ubuntu-Certonomous/a4c3e450-daf7-4f58-9d1e-4f43ac1547e8/scratchpad"
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import _plt, INK, BLUE, RED, _finish

TWIST_TIP_DEG = -1.10        # SYNTHETIC washout at the tip, linear in span
THICK_MAX = 0.012            # SYNTHETIC thickness scale change, peaking mid-span
STATIONS = (0.20, 0.50, 0.80)


def wcsv(stem, header, rows):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# SYNTHETIC deformation of a REAL baseline: generated, not "
                    "computed; illustrative of the registered MP_R2/MP_R3 "
                    "optimisation whose first design iteration has not completed"])
        w.writerow(header); w.writerows(rows)


pts = np.load(os.path.join(SCR, "crm_points.npy"))
faces = np.load(os.path.join(SCR, "crm_wingfaces.npy"))
wid = np.unique(faces.ravel())
w = pts[wid]
# the wing lies in x (chord), y (span), z (thickness); take the semi-span from the data
y0, y1 = float(w[:, 1].min()), float(w[:, 1].max())
print("wing patch: %d points, span %.4f..%.4f, chord %.4f..%.4f"
      % (len(w), y0, y1, w[:, 0].min(), w[:, 0].max()))


def deform(p):
    """Span-varying washout twist about the local quarter chord, plus a thickness
    redistribution that peaks at mid span. SYNTHETIC, smooth, and small."""
    q = p.copy()
    eta = (p[:, 1] - y0) / max(y1 - y0, 1e-12)
    for e in np.unique(np.round(eta, 4)):
        pass
    # local chord line per span station, binned so the twist has something to rotate about
    nb = 120
    idx = np.clip((eta * nb).astype(int), 0, nb - 1)
    for b in range(nb):
        m = idx == b
        if m.sum() < 4:
            continue
        xs = p[m, 0]
        xle, xte = xs.min(), xs.max()
        c = max(xte - xle, 1e-9)
        xq = xle + 0.25 * c
        e = eta[m].mean()
        th = np.radians(TWIST_TIP_DEG * e)
        dx = p[m, 0] - xq
        dz = p[m, 2]
        q[m, 0] = xq + dx * np.cos(th) - dz * np.sin(th)
        q[m, 2] = dx * np.sin(th) + dz * np.cos(th)
        q[m, 2] *= 1.0 + THICK_MAX * np.sin(np.pi * e)
    return q


wd = deform(w)
disp = np.linalg.norm(wd - w, axis=1)
print("synthetic displacement: max %.4f m, mean %.5f m" % (disp.max(), disp.mean()))

plt = _plt()
for eta in STATIONS:
    # A THIN SPANWISE SLAB, WIDENED UNTIL IT HOLDS ENOUGH POINTS, because this surface
    # is NOT structured on constant-y stations: a 15 mm band caught 0 points and
    # snapping to the nearest existing y caught 1. The slab starts at 0.2 % of span and
    # doubles until it holds 200 points; its half-width is printed and goes in the CSV,
    # so the reader knows the section is a slab and how thick it is.
    ytarget = y0 + eta * (y1 - y0)
    tol = 0.002 * (y1 - y0)
    while tol < 0.06 * (y1 - y0):
        m = np.abs(w[:, 1] - ytarget) < tol
        if m.sum() >= 200:
            break
        tol *= 1.6
    if m.sum() < 200:
        raise SystemExit("station eta=%.2f caught only %d points at tol %.4f"
                         % (eta, m.sum(), tol))
    a, b = w[m], wd[m]
    # EACH POINT IS NORMALISED BY THE CHORD AT ITS OWN SPAN, NOT THE SLAB'S. The wing is
    # swept and tapered, so a slab thick enough to hold points spans a range of leading
    # edges; normalising them all by one chord smears the section into a zigzag band.
    # A linear fit of the leading and trailing edge across the slab collapses it to one
    # clean section, and the fit is over the slab's own points.
    def _edges(arr):
        ys = arr[:, 1]
        nb = 8
        qs = np.linspace(ys.min(), ys.max(), nb + 1)
        yy, xl, xt = [], [], []
        for i in range(nb):
            k = (ys >= qs[i]) & (ys <= qs[i + 1])
            if k.sum() < 4:
                continue
            yy.append(ys[k].mean()); xl.append(arr[k, 0].min()); xt.append(arr[k, 0].max())
        if len(yy) < 2:
            return (lambda y: arr[:, 0].min()), (lambda y: arr[:, 0].max() - arr[:, 0].min())
        pl = np.polyfit(yy, xl, 1); pt = np.polyfit(yy, xt, 1)
        return (lambda y: np.polyval(pl, y)), (lambda y: np.polyval(pt, y) - np.polyval(pl, y))
    fle, fc = _edges(a)
    c = float(np.mean(fc(a[:, 1])))

    def _envelope(arr, nbin=90):
        """Upper and lower envelope of the slab in chord-normalised coordinates.

        SORTING THE SLAB'S POINTS INTO ONE CURVE DOES NOT WORK and the zigzag is why:
        the slab holds several spanwise stations whose sections differ slightly, so any
        angular ordering alternates between them. Binning in x/c and taking the highest
        and lowest z in each bin collapses them to a single clean upper and lower
        surface, which is what a section plot is.
        """
        cc = fc(arr[:, 1]); xn = (arr[:, 0] - fle(arr[:, 1])) / cc; zn = arr[:, 2] / cc
        edges = np.linspace(0.0, 1.0, nbin + 1)
        xs, zu, zl = [], [], []
        for i in range(nbin):
            k = (xn >= edges[i]) & (xn < edges[i + 1])
            if k.sum() < 2:
                continue
            xs.append(0.5 * (edges[i] + edges[i + 1]))
            zu.append(zn[k].max()); zl.append(zn[k].min())
        return np.array(xs), np.array(zu), np.array(zl)

    fig, ax = plt.subplots(figsize=(6.8, 2.6))
    for arr, col, lab in ((a, INK, r"$\mathrm{baseline}$"),
                          (b, RED, r"$\mathrm{deformed}$")):
        xs, zu, zl = _envelope(arr)
        ax.plot(np.concatenate([xs, xs[::-1], xs[:1]]),
                np.concatenate([zu, zl[::-1], zu[:1]]), color=col, lw=1.4, label=lab)
    ax.set_xlabel(r"$x/c$"); ax.set_ylabel(r"$z/c$")
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(loc="upper right")
    _finish(fig, os.path.join(HERE, "synthetic_section_eta%02d.png" % int(eta * 100)))
    wcsv("synthetic_section_eta%02d" % int(eta * 100),
         ["x_baseline", "z_baseline", "x_deformed", "z_deformed"],
         [[a[i, 0], a[i, 2], b[i, 0], b[i, 2]] for i in range(len(a))])
    print("  eta %.2f -> y = %.4f m, slab +-%.4f m: %d points, chord %.4f m"
          % (eta, ytarget, tol, m.sum(), c))

# ------------------------------------------------------------------ the FFD lattice
txt = open(FFD).read().split()
nb = int(txt[0]); ni, nj, nk = int(txt[1]), int(txt[2]), int(txt[3])
vals = np.array([float(v) for v in txt[4:4 + 3 * ni * nj * nk]])
n = ni * nj * nk
ffd = np.stack([vals[0:n], vals[n:2 * n], vals[2 * n:3 * n]], axis=1)
print("FFD lattice %d x %d x %d = %d control points" % (ni, nj, nk, n))
fy0, fy1 = ffd[:, 1].min(), ffd[:, 1].max()
fe = (ffd[:, 1] - fy0) / max(fy1 - fy0, 1e-12)
fd = ffd.copy()
th = np.radians(TWIST_TIP_DEG * fe)
xq = ffd[:, 0].mean()
fd[:, 0] = xq + (ffd[:, 0] - xq) * np.cos(th) - ffd[:, 2] * np.sin(th)
fd[:, 2] = ((ffd[:, 0] - xq) * np.sin(th) + ffd[:, 2] * np.cos(th)) * \
           (1.0 + THICK_MAX * np.sin(np.pi * fe))
fig, ax = plt.subplots(figsize=(7.0, 4.0))
ax.plot(ffd[:, 0], ffd[:, 1], ".", ms=3.5, color=INK, label=r"$\mathrm{baseline}$")
ax.plot(fd[:, 0], fd[:, 1], ".", ms=3.5, color=RED, label=r"$\mathrm{deformed}$")
ax.set_xlabel(r"$x\ \ [\mathrm{m}]$"); ax.set_ylabel(r"$y\ \ [\mathrm{m}]$")
ax.legend(loc="best")
_finish(fig, os.path.join(HERE, "synthetic_ffd_lattice.png"))
wcsv("synthetic_ffd_lattice", ["x_base", "y_base", "z_base", "x_def", "y_def", "z_def"],
     [[ffd[i, 0], ffd[i, 1], ffd[i, 2], fd[i, 0], fd[i, 1], fd[i, 2]] for i in range(n)])
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
