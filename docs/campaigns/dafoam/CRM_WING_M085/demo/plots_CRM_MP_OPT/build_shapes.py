#!/usr/bin/env python3
"""Section shapes for the CRM optimisation storyline, from TRUE PLANE CUTS.

    python3 docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP_OPT/build_shapes.py

Writes `section_eta{20,50,80}.png` and nothing else. Every number on those figures
comes from the six committed CSVs in this folder, which `cut_sections.py` produced by
intersecting the wing wall surface with a plane in ParaView. This script needs no
solver, no run directory and no scratch file: it is reproducible from the repository
alone, which the previous edition was not -- it loaded `crm_points.npy` from a session
scratchpad that has since been wiped (standing rule 13).

WHAT CHANGED AND WHY. The previous `section_eta*.csv` were SLABS: every wall-patch
point inside a spanwise tolerance band, in mesh-point order. The wing is swept and
tapered, so the band holds several different sections at once and the polyline crosses
itself; ordering the slab does not repair it. These CSVs are single ordered polylines
from a geometric cut, so the profile closes on itself once and only once.

THE `opt` CURVE ON THIS RUN LIES EXACTLY ON THE BASELINE, AND THAT IS THE MEASUREMENT.
`MP_R2_DESIGN_ITERATIONS.tsv` records design iteration 0 and nothing after it: the run
was killed (rc = 137) inside the first adjoint solve, so no design variable ever moved.
The two cuts are taken from two genuinely different files -- `constant/polyMesh` for the
baseline, `processor*/2000/polyMesh` for the final time -- and the final-time mesh is the
baseline mesh re-written by the solver: max point displacement 9.94e-13 m, zero points
moved by more than 1e-12 m. Nothing on the figure is exaggerated to hide that.

The FFD lattice figure that this file used to build is preserved below but is OFF by
default (`--ffd`), because its planform silhouette layer came from the same wiped
scratch array; regenerating it would silently change a committed demo PNG.
"""
import os
import sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "sdk"))

import numpy as np
from workflows.act_plots_lib import _plt, INK, RED, _finish

STATIONS = (0.20, 0.50, 0.80)


def read_cut(path):
    """x, y, z of one cut, in polyline order. The `#` lines carry the provenance."""
    meta, rows = {}, []
    for line in open(path):
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            meta[k.strip()] = v.strip()
        elif line.startswith("x,"):
            continue
        elif line.strip():
            rows.append([float(v) for v in line.split(",")])
    a = np.asarray(rows, float)
    if a.ndim != 2 or a.shape[1] != 3 or len(a) < 8:
        raise SystemExit("REFUSE: %s is not a usable cut (%s)" % (path, a.shape))
    return a, meta


def frame(base):
    """The baseline cut's own leading edge and chord. Both curves are drawn in it."""
    ile = int(np.argmin(base[:, 0]))
    ite = int(np.argmax(base[:, 0]))
    xle, zle = base[ile, 0], base[ile, 2]
    c = float(np.hypot(base[ite, 0] - xle, base[ite, 2] - zle))
    if c <= 0:
        raise SystemExit("REFUSE: degenerate chord")
    return xle, zle, c


def surfaces(a, xle, zle, c):
    """Upper and lower branch of one closed cut, on a common x/c grid.

    FOR THE NUMBER ONLY, NOT FOR THE FIGURE. The figure draws the closed polyline as it
    stands -- no split, no resampling. A branch split is unavoidable to state a single
    max |dz/c| between two closed curves whose point ids do not correspond, because the
    two meshes are read differently (11,205 points reconstructed, 11,865 decomposed) so
    row i of one is not row i of the other.
    """
    xn = (a[:, 0] - xle) / c
    zn = (a[:, 2] - zle) / c
    i0, i1 = int(np.argmin(xn)), int(np.argmax(xn))
    n = len(xn)
    idx = np.arange(n)
    roll = np.roll(idx, -i0)
    j1 = int(np.where(roll == i1)[0][0])
    br1, br2 = roll[:j1 + 1], np.concatenate([roll[j1:], roll[:1]])
    g = np.linspace(0.0, 1.0, 401)
    out = []
    for br in (br1, br2):
        x, z = xn[br], zn[br]
        o = np.argsort(x)
        out.append(np.interp(g, x[o], z[o]))
    return g, out[0], out[1]


def build_sections():
    plt = _plt()
    report = []
    for eta in STATIONS:
        tag = "eta%02d" % int(round(eta * 100))
        base, mb = read_cut(os.path.join(HERE, "section_%s_baseline.csv" % tag))
        opt, mo = read_cut(os.path.join(HERE, "section_%s_opt.csv" % tag))
        xle, zle, c = frame(base)

        fig, ax = plt.subplots(figsize=(6.8, 2.6))
        for a, col, ls, lab in ((base, INK, "-", r"$z/c$"),
                                (opt, RED, "--", r"$z/c^{\mathrm{opt}}$")):
            ax.plot((a[:, 0] - xle) / c, (a[:, 2] - zle) / c,
                    color=col, lw=1.4, ls=ls, label=lab)
        ax.set_xlabel(r"$x/c$  [-]")
        ax.set_ylabel(r"$z/c$  [-]")
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(loc="upper right")
        # the station, and nothing else: no caption, no verdict, no provenance on the PNG
        ax.text(0.02, 0.92, r"$\eta = %.2f$" % eta, transform=ax.transAxes,
                ha="left", va="top", color=INK)
        _finish(fig, os.path.join(HERE, "section_%s.png" % tag))

        g, u1, l1 = surfaces(base, xle, zle, c)
        _, u2, l2 = surfaces(opt, xle, zle, c)
        dz = max(float(np.abs(u2 - u1).max()), float(np.abs(l2 - l1).max()))
        report.append((eta, mb["time_directory"], mo["time_directory"],
                       mb["plane_origin"], mb["halfspan_b_over_2_m"],
                       len(base), len(opt), c, dz))
        print("eta %.2f : chord %.6f m ; baseline %d pts (t=%s), opt %d pts (t=%s) ; "
              "plane origin %s ; max |dz/c| = %.3e"
              % (eta, c, len(base), mb["time_directory"], len(opt),
                 mo["time_directory"], mb["plane_origin"], dz))
    return report


def build_ffd():
    """The FFD lattice, from the committed `ffd_lattice.csv`. Opt-in; see the docstring."""
    plt = _plt()
    p = os.path.join(HERE, "ffd_lattice.csv")
    d = np.genfromtxt(p, delimiter=",", names=True)
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    dx = 0.012 * (d["x_base"].max() - d["x_base"].min())
    ax.plot(d["x_base"] - dx, d["y_base"], "o", ms=3.2, color=INK, mfc="none",
            label=r"$\mathrm{base}$")
    ax.plot(d["x_def"] + dx, d["y_def"], "s", ms=3.2, color=RED, mfc="none",
            label=r"$\mathrm{opt}$")
    ax.set_xlabel(r"$x$  [m]")
    ax.set_ylabel(r"$y$  [m]")
    ax.legend(loc="best")
    _finish(fig, os.path.join(HERE, "ffd_lattice.png"))
    print("ffd_lattice.png rebuilt WITHOUT the planform silhouette layer "
          "(its source array was a scratchpad file, now wiped)")


if __name__ == "__main__":
    build_sections()
    if "--ffd" in sys.argv:
        build_ffd()
