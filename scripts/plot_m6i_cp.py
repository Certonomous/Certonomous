#!/usr/bin/env python3
"""
plot_m6i_cp.py -- Cp vs x/c at the six registered AGARD stations: CFD against experiment.

  usage: plot_m6i_cp.py <reference.dat> <label:cp_extracted.json> [<label:...> ...] <out.png>

THE UPPER/LOWER SPLIT IS THE FROZEN GRADER'S, NOT A NEW ONE.  It is transcribed from
scripts/grade_m6_agard_cp.py:cfd_curve() -- a point is 'upper' if its vertical coordinate
lies above the straight chord line joining the contour's LE and TE points.  The reference's
own split is the sign of its Z/L column, which the data file already resolved into a
`surface` column and documents in its header.  NOTHING HERE RE-DECIDES EITHER.

COLOUR CARRIES NO IDENTITY ON ITS OWN.  Experiment is black open circles, CFD is a solid
line; upper and lower surfaces are separated by MARKER SHAPE and LINE STYLE as well as by
hue, so the figure survives greyscale printing and every form of colour blindness.
THE SKILL'S PALETTE VALIDATOR WAS RUN AND IS BLIND IN THIS ENVIRONMENT -- a deliberately
failing pair (#1f6feb vs #2070ec, one hex step apart) produced ZERO BYTES and exit 0,
exactly as the good palette did, because the script's entry point reads document.body and
never executes under node.  A pass from a reader not shown able to see a failure is not
evidence (CLAUDE.md rule 3), so no claim of validation is made and the design is made safe
by construction instead.
"""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STATIONS = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96)
INK, C_CFD = "#1a1a1a", "#1f6feb"

def read_ref(p):
    out = {}
    for line in open(p):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        f = line.split()
        if len(f) < 5:
            continue
        try:
            eta, surf, xoc, cp = round(float(f[1]), 4), f[2].lower(), float(f[3]), float(f[4])
        except ValueError:
            continue
        out.setdefault((eta, surf), []).append((xoc, cp))
    for k in out:
        out[k].sort()
    return out

def cfd_branch(blk, surface):
    """Transcribed from grade_m6_agard_cp.py:cfd_curve(). Not a new rule."""
    xoc, cp, y = blk["xoc"], blk["cp"], blk["y"]
    pts = sorted(zip(xoc, y, cp))
    x0, y0 = pts[0][0], pts[0][1]
    x1, y1 = pts[-1][0], pts[-1][1]
    out = []
    for xv, yv, cv in zip(xoc, y, cp):
        ych = y0 + (y1 - y0) * (xv - x0) / (x1 - x0)
        if (surface == "upper") == (yv >= ych):
            out.append((xv, cv))
    out.sort()
    ded, seen = [], set()
    for xv, cv in out:
        k = round(xv, 7)
        if k in seen:
            continue
        seen.add(k); ded.append((xv, cv))
    return ded

def main():
    ref = read_ref(sys.argv[1])
    runs = []
    for a in sys.argv[2:-1]:
        lab, path = a.split(":", 1)
        runs.append((lab, json.load(open(path))["stations"]))
    out = sys.argv[-1]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.6), sharex=True, sharey=True)
    for ax, eta in zip(axes.ravel(), STATIONS):
        for surf, mk, ls in (("upper", "o", "-"), ("lower", "s", "--")):
            r = ref.get((eta, surf), [])
            if r:
                ax.plot([p[0] for p in r], [-p[1] for p in r], mk, ms=6,
                        mfc="none", mec=INK, mew=1.3, ls="none",
                        label="AGARD AR-138 %s" % surf, zorder=3)
            for i, (lab, st) in enumerate(runs):
                blk = st.get("%g" % eta)
                if not blk:
                    continue
                c = cfd_branch(blk, surf)
                ax.plot([p[0] for p in c], [-p[1] for p in c], ls,
                        color=C_CFD, lw=2.0, alpha=1.0 - 0.35 * i,
                        marker=mk, ms=3.5, mfc=C_CFD, mec=C_CFD,
                        label="%s %s" % (lab, surf), zorder=2)
        ax.axhline(0, color="#cccccc", lw=0.8, zorder=0)
        ax.set_title(r"$\eta = y/b = %.2f$" % eta, fontsize=12)
        ax.grid(True, color="#eeeeee", lw=0.8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel(r"$-C_p$")
    for ax in axes[1, :]:
        ax.set_xlabel(r"$x/c$")
    axes[0, 0].legend(fontsize=8.5, frameon=False, loc="upper right")
    fig.suptitle("ONERA M6 — surface pressure at the six registered AGARD stations.  "
                 "AGARD AR-138 TABLE B1-14, TEST 2308:  M = 0.8395,  α = 3.06°,  Re = 11.72e6",
                 fontsize=13)
    fig.text(0.5, 0.945, "Open symbols: experiment.  Lines: CFD.  Circles/solid = upper surface, "
                         "squares/dashed = lower.  Marker shape and line style carry the surface, "
                         "not colour alone.",
             ha="center", fontsize=9.5, color="#555555")
    fig.tight_layout(rect=[0, 0, 1, 0.925])
    fig.savefig(out, dpi=150)
    print("wrote", out)

if __name__ == "__main__":
    main()
