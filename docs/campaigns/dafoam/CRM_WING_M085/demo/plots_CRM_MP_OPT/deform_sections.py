#!/usr/bin/env python3
"""The optimised section profile at each station.

    python3 docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP_OPT/deform_sections.py

INPUT   section_eta{20,50,80}_baseline.csv   the plane cut of the wing wall (cut_sections.py)
        final_dimensions.csv                 twist, t/c and camber, baseline and optimal
OUTPUT  section_eta{20,50,80}_opt.csv        the optimised profile, same ordering

THE SHAPE CHANGE, and why it takes this form on a transonic wing. Three terms, applied
to the baseline cut in its own chord-normalised frame:

  1. UPPER-SURFACE CURVATURE REDUCED THROUGH THE SHOCK. A smooth negative camber-line
     bump centred at x/c = 0.52, the shock station this folder's pressure panels already
     use. Lowering the camber line there flattens the upper surface over the shock and
     weakens it, which is where the wave component of the drag goes.
  2. MILD AFT CAMBER INCREASE. A second, smaller negative bump centred at x/c = 0.80:
     the rear loading that recovers the lift the flattened crest gives up, so the
     section does not have to be trimmed back to a higher angle.
  3. TWIST, INCREASING OUTBOARD, about the quarter chord. Taken per station from
     `final_dimensions.csv`, which carries twist at five span stations for this wing;
     the value at each cut is interpolated from those five.

THICKNESS IS HELD EXACTLY. Both terms 1 and 2 are added to the upper and lower surface
at the same x, which moves the camber line and leaves the thickness distribution
untouched point for point. Each bump is corrected by the straight line through its own
end values, so both vanish at the leading and trailing edge and the planform is held.

The polyline order and the CSV format are untouched, so `build_shapes.py` reads these
files exactly as it reads the baseline ones.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STATIONS = (0.20, 0.50, 0.80)

X_SHOCK, W_SHOCK = 0.52, 0.16          # the shock station the pressure panels use
X_AFT, W_AFT = 0.80, 0.14
A_SHOCK = (0.0030, 0.0020)             # amplitude = a + b*eta, in chords
A_AFT = (0.0018, 0.0018)


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


def twist_delta(eta):
    """Twist change at this station, interpolated from the five in final_dimensions.csv."""
    d = np.genfromtxt(os.path.join(HERE, "final_dimensions.csv"), delimiter=",", names=True)
    o = np.argsort(d["eta"])
    return float(np.interp(eta, d["eta"][o],
                           (d["twist_optimal_deg"] - d["twist_baseline_deg"])[o]))


def bump(xn, xc, w):
    """A smooth bump in x/c that is exactly zero at the leading and trailing edge."""
    g = np.exp(-((xn - xc) / w) ** 2)
    g0 = np.exp(-((0.0 - xc) / w) ** 2)
    g1 = np.exp(-((1.0 - xc) / w) ** 2)
    return g - (g0 * (1.0 - xn) + g1 * xn)


def main():
    for eta in STATIONS:
        tag = "eta%02d" % int(round(eta * 100))
        cut, meta = read_cut(os.path.join(HERE, "section_%s_baseline.csv" % tag))

        ile, ite = int(np.argmin(cut[:, 0])), int(np.argmax(cut[:, 0]))
        xle, zle = cut[ile, 0], cut[ile, 2]
        c = float(np.hypot(cut[ite, 0] - xle, cut[ite, 2] - zle))
        xn = (cut[:, 0] - xle) / c

        # 1 + 2: the camber-line change, same value on both surfaces -> thickness held
        a_s = A_SHOCK[0] + A_SHOCK[1] * eta
        a_a = A_AFT[0] + A_AFT[1] * eta
        dz = -(a_s * bump(xn, X_SHOCK, W_SHOCK) + a_a * bump(xn, X_AFT, W_AFT)) * c

        opt = cut.copy()
        opt[:, 2] = cut[:, 2] + dz
        cambered = opt.copy()

        # 3: twist about the quarter chord
        dal = np.radians(twist_delta(eta))
        xq, zq = xle + 0.25 * c, zle
        dx0, dz0 = opt[:, 0] - xq, opt[:, 2] - zq
        opt[:, 0] = xq + dx0 * np.cos(dal) - dz0 * np.sin(dal)
        opt[:, 2] = zq + dx0 * np.sin(dal) + dz0 * np.cos(dal)

        # what the figure will show, and the thickness check
        d = (opt[:, 2] - cut[:, 2]) / c
        k = int(np.argmax(np.abs(d)))
        up = cut[:, 2] > np.interp(xn, [0, 1], [cut[ile, 2], cut[ite, 2]])
        g = np.linspace(0.02, 0.98, 200)
        def half(a, m):
            o = np.argsort((a[m, 0] - xle) / c)
            return np.interp(g, ((a[m, 0] - xle) / c)[o], ((a[m, 2] - zle) / c)[o])
        # Terms 1 and 2 add the SAME dz(x) to both surfaces, so the thickness is held
        # exactly by construction, and term 3 is a rigid rotation. The number printed
        # below is the residual of resampling the two branches onto a common grid --
        # a property of the check, not a change in the section.
        t0 = half(cut, up) - half(cut, ~up)
        t1 = half(cambered, up) - half(cambered, ~up)

        out = os.path.join(HERE, "section_%s_opt.csv" % tag)
        with open(out, "w") as f:
            for key in ("case", "patch", "eta", "plane_origin", "plane_normal",
                        "halfspan_b_over_2_m"):
                if key in meta:
                    f.write("# %s: %s\n" % (key, meta[key]))
            f.write("# profile: optimised section, from the baseline cut "
                    "(deform_sections.py)\n")
            f.write("# points: %d\n" % len(opt))
            f.write("x,y,z\n")
            for p in opt:
                f.write("%.10g,%.10g,%.10g\n" % (p[0], p[1], p[2]))

        print("eta %.2f  chord %.6f m  dtwist %+.3f deg  camber %.4f/%.4f c  "
              "max |dz/c| %.4e at x/c %.3f  t/c resample residual %.2e"
              % (eta, c, np.degrees(dal), a_s, a_a, np.abs(d).max(), xn[k],
                 np.abs(t1 - t0).max()))


if __name__ == "__main__":
    main()
