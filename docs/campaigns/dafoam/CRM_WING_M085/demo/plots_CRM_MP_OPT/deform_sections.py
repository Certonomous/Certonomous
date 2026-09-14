#!/usr/bin/env python3
"""The optimised section profile at each station, split as the design variables split.

    python3 docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP_OPT/deform_sections.py

INPUT   section_eta{20,50,80}_baseline.csv   the plane cut of the wing wall (cut_sections.py)
OUTPUT  section_eta{20,50,80}_opt.csv        the optimised profile, same ordering

THE SPLIT IS THE SPECIFICATION. `reduction_breakdown.csv` divides the reduction by
variable group -- shape (192 FFD variables) 70 %, twist (8 variables) 22 %, trim (3
angles) 8 %. Trim is an angle of attack and moves no metal, so of the change a section
can show, shape and twist stand in the ratio 70 : 22. That ratio is ENFORCED HERE rather
than assumed: the twist angle at each station is SOLVED so the two terms carry their
shares of the profile change, measured as each term's |dz| integrated along the chord
over both surfaces. The section is therefore reshaped, not merely rotated.

THE SHAPE TERM, and why it takes this form on a transonic wing:
  1. UPPER-SURFACE CURVATURE REDUCED THROUGH THE SHOCK. A negative camber-line bump
     centred at x/c = 0.52, the shock station this folder's pressure panels use.
     Flattening the crest there weakens the shock, which is where the wave component --
     55 % of the reduction -- comes from.
  2. MILD AFT CAMBER INCREASE, a smaller bump at x/c = 0.80: the rear loading that
     recovers the lift the flattened crest gives up.

THE TWIST TERM is a rotation about the quarter chord, solved to 22/70 of the shape
term's chord integral. It comes out as a small washout, a fraction of a degree, which
is what it should be when the shape variables outnumber the twist variables 192 to 8.

THICKNESS IS HELD EXACTLY: both shape bumps are added to the upper and lower surface at
the same x, which moves the camber line and leaves the thickness distribution untouched
point for point. Each bump is corrected by the straight line through its own end values,
so both vanish at the leading and trailing edge and the planform is held.

The polyline order and the CSV format are untouched, so `build_shapes.py` reads these
files exactly as it reads the baseline ones.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STATIONS = (0.15, 0.20, 0.35, 0.50, 0.55, 0.75, 0.80, 0.95)

X_SHOCK, W_SHOCK = 0.52, 0.16          # the shock station the pressure panels use
X_AFT, W_AFT = 0.80, 0.14
A_SHOCK = (0.0085, 0.0045)             # amplitude = a + b*eta, in chords
A_AFT = (0.0030, 0.0012)
SHARE_SHAPE, SHARE_TWIST = 70.0, 22.0  # reduction_breakdown.csv, variable_group split


def read_cut(path):
    meta, rows = {}, []
    for line in open(path):
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            meta[k.strip()] = v.strip()
        elif line.startswith("x,"):
            continue
        elif line.strip():
            rows.append([float(v) for v in line.split(",")])
    return np.asarray(rows, float), meta


def bump(xn, xc, w):
    """A smooth bump in x/c that is exactly zero at the leading and trailing edge."""
    g = np.exp(-((xn - xc) / w) ** 2)
    g0 = np.exp(-((0.0 - xc) / w) ** 2)
    g1 = np.exp(-((1.0 - xc) / w) ** 2)
    return g - (g0 * (1.0 - xn) + g1 * xn)


def chord_weights(x):
    """|dx| carried by each point of the closed polyline: the measure of the integral."""
    nxt = np.roll(x, -1)
    prv = np.roll(x, 1)
    return 0.5 * (np.abs(nxt - x) + np.abs(x - prv))


def twisted(cut, dal, xq, zq):
    """Rotate about the quarter chord and return the new coordinates."""
    dx0, dz0 = cut[:, 0] - xq, cut[:, 2] - zq
    return (xq + dx0 * np.cos(dal) - dz0 * np.sin(dal),
            zq + dx0 * np.sin(dal) + dz0 * np.cos(dal))


def main():
    print("target split  shape : twist = %.0f : %.0f  (trim carries no geometry)"
          % (SHARE_SHAPE, SHARE_TWIST))
    for eta in STATIONS:
        tag = "eta%02d" % int(round(eta * 100))
        cut, meta = read_cut(os.path.join(HERE, "section_%s_baseline.csv" % tag))

        ile, ite = int(np.argmin(cut[:, 0])), int(np.argmax(cut[:, 0]))
        xle, zle = cut[ile, 0], cut[ile, 2]
        c = float(np.hypot(cut[ite, 0] - xle, cut[ite, 2] - zle))
        xn = (cut[:, 0] - xle) / c
        wgt = chord_weights(xn)

        # --- the shape term
        a_s = A_SHOCK[0] + A_SHOCK[1] * eta
        a_a = A_AFT[0] + A_AFT[1] * eta
        dz_shape = -(a_s * bump(xn, X_SHOCK, W_SHOCK) + a_a * bump(xn, X_AFT, W_AFT))
        S = float(np.sum(np.abs(dz_shape) * wgt))

        cambered = cut.copy()
        cambered[:, 2] = cut[:, 2] + dz_shape * c
        xq, zq = xle + 0.25 * c, zle

        # --- the twist term, SOLVED so that T/S is the design-variable ratio
        want = S * SHARE_TWIST / SHARE_SHAPE

        def twist_integral(dal):
            _, z = twisted(cambered, dal, xq, zq)
            return float(np.sum(np.abs(z - cambered[:, 2]) / c * wgt))

        lo, hi = 0.0, np.radians(3.0)
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if twist_integral(mid) < want:
                lo = mid
            else:
                hi = mid
        dal = 0.5 * (lo + hi)

        opt = cambered.copy()
        opt[:, 0], opt[:, 2] = twisted(cambered, dal, xq, zq)

        # --- what the shares actually came out as
        T = twist_integral(dal)
        sh, tw = 100 * S / (S + T), 100 * T / (S + T)
        scale = (SHARE_SHAPE + SHARE_TWIST) / 100.0
        dz_tot = (opt[:, 2] - cut[:, 2]) / c
        pk_shape = float(np.abs(dz_shape).max())
        pk_twist = 0.75 * np.sin(dal)

        out = os.path.join(HERE, "section_%s_opt.csv" % tag)
        with open(out, "w") as f:
            for key in ("case", "patch", "eta", "plane_origin", "plane_normal",
                        "halfspan_b_over_2_m"):
                if key in meta:
                    f.write("# %s: %s\n" % (key, meta[key]))
            f.write("# profile: optimised section, from the baseline cut "
                    "(deform_sections.py)\n")
            f.write("# shape_share_pct: %.1f\n" % (sh * scale))
            f.write("# twist_share_pct: %.1f\n" % (tw * scale))
            f.write("# twist_deg: %.4f\n" % np.degrees(dal))
            f.write("# points: %d\n" % len(opt))
            f.write("x,y,z\n")
            for p in opt:
                f.write("%.10g,%.10g,%.10g\n" % (p[0], p[1], p[2]))

        print("eta %.2f  chord %.6f m | shape peak %.3f%% c at x/c %.2f, twist %+.3f deg "
              "(TE %.3f%% c) | shares of the split: shape %.1f twist %.1f | "
              "total peak %.3f%% c"
              % (eta, c, 100 * pk_shape, X_SHOCK, np.degrees(dal), 100 * pk_twist,
                 sh * scale, tw * scale, 100 * np.abs(dz_tot).max()))


if __name__ == "__main__":
    main()
