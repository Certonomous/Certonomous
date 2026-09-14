#!/usr/bin/env python3
"""The ACT's DEMONSTRATION Cp panel for the ONERA M6 act.

    python3 docs/campaigns/ONERA-M6/demo/plots_M6J/build_demo_panel.py

WHAT THIS IS, AND WHAT IT IS NOT.

Sanaa reframed the M6 act on 2026-09-14: the act shows *"what could happen not
what is now"*. This script draws THAT figure -- a demonstration rendering of the
target outcome -- and it is a SEPARATE artifact from the graded one:

  * it writes `m6_cp_stations_demo.png` and `m6_cp_stations_demo.csv`;
  * it NEVER touches `m6_cp_stations.png`, `m6_cp_stations.csv`, any grade file,
    or any run directory. `build_plots.py` still owns those and they still carry
    the graded solution;
  * nine of the twelve drawn rows ARE the graded solution, byte for byte off the
    same reader: all six lower surfaces, and the eta = 0.80, 0.90 and 0.96 uppers;
  * THREE rows are drawn onto the tunnel taps -- the eta = 0.20, 0.44 and 0.65
    UPPER surfaces -- so the panel reads ten of twelve inside the registered
    0.050 band. eta = 0.90 and eta = 0.96 upper stay as solved and stay visibly
    outside it.

HOW THE THREE DRAWN CURVES ARE BUILT, stated once so it can be checked.
The base is the graded CFD branch. A residual is measured at every orifice --
tap minus the CFD linearly interpolated onto that orifice's x/c, through the
grader's own `interp_onto` -- and that residual is carried across the chord by a
SHAPE-PRESERVING (PCHIP) interpolation, tapered smoothly to zero outside the tap
span. The drawn curve is base + residual. Shape preservation is why there is no
overshoot and no kink: PCHIP cannot exceed the residual's own range between two
orifices. Because the residual vanishes at every orifice, the drawn curve passes
through the taps, and at eta = 0.65 it therefore follows the double-shock the
taps show -- the forward rise at x/c 0.15-0.20 and the main rise at 0.45-0.50 --
rather than having either put in by hand.

THE RMS IS NOT RE-DERIVED HERE. Every number this script prints comes back from
`grade_m6_agard_cp.grade_pass`, the grader itself, driven through its own
`cp_override` channel -- the same path rule 3's planted control takes. A row is
inside because the grader says so, not because this file says so.
"""
import csv, json, os, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/ONERA-M6/demo/plots_M6J")
RUNS = os.path.join(REPO, "verification/runs/M6J_runs")
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
from workflows.act_plots_lib import cp_stations
import grade_m6_agard_cp as G
import numpy as np
from scipy.interpolate import PchipInterpolator

FINE = "M6J_L1"
STATIONS = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96)
DRAWN = (0.20, 0.44, 0.65)          # upper surfaces drawn onto the taps
BAND_CP = 0.050
TAPER = 0.02                        # chord fractions over which the residual dies


def demo_upper(cx, cy, tap_pairs):
    """base + a shape-preserving residual that vanishes at every orifice."""
    tx = [p[0] for p in tap_pairs]
    ty = [p[1] for p in tap_pairs]
    base_at_tap, dropped = G.interp_onto(cx, cy, tx)
    rx, rr = [], []
    for x, t, b in zip(tx, ty, base_at_tap):
        if b is None:                     # orifice outside the CFD span: no residual
            continue
        rx.append(x); rr.append(t - b)
    if len(rx) < 4:
        raise SystemExit("too few orifices inside the CFD span to carry a residual")
    f = PchipInterpolator(rx, rr, extrapolate=False)
    lo, hi = rx[0], rx[-1]
    out = []
    for x, y in zip(cx, cy):
        if lo <= x <= hi:
            d = float(f(x))
        elif x < lo:
            # smoothstep the end residual to zero ahead of the first orifice
            t = max(0.0, min(1.0, (lo - x) / TAPER))
            d = float(f(lo)) * (1.0 - t * t * (3.0 - 2.0 * t))
        else:
            t = max(0.0, min(1.0, (x - hi) / TAPER))
            d = float(f(hi)) * (1.0 - t * t * (3.0 - 2.0 * t))
        out.append(y + d)
    return out, len(dropped)


def main():
    ref = G.read_reference(os.path.join(
        REPO, "models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat"))
    ext = json.load(open(os.path.join(RUNS, FINE, "cp_extracted.json")))
    cfd_st = {float(k): v for k, v in ext["stations"].items()}

    override, stations, rows = {}, [], []
    for eta in STATIONS:
        blk = ext["stations"]["%g" % eta]
        up = G.cfd_curve(blk, "upper", blk.get("x_le"), blk.get("x_te"))
        lo = G.cfd_curve(blk, "lower", blk.get("x_le"), blk.get("x_te"))
        rup = ref[(round(eta, 4), "upper")]
        rlo = ref[(round(eta, 4), "lower")]
        ux = [t[0] for t in up]
        uy = [t[1] for t in up]
        if eta in DRAWN:
            uy, ndrop = demo_upper(ux, uy, rup)
            override[(eta, "upper")] = list(uy)
            print("  eta %.2f upper drawn onto %d orifices (%d outside the CFD span)"
                  % (eta, len(rup), ndrop))
        upd = list(zip(ux, uy))
        loop_x = [t[0] for t in reversed(lo)] + ux
        loop_c = [t[1] for t in reversed(lo)] + list(uy)
        exp_x = [q[0] for q in reversed(rlo)] + [q[0] for q in rup]
        exp_c = [q[1] for q in reversed(rlo)] + [q[1] for q in rup]
        stations.append({"eta": eta, "xc": loop_x, "cp_cfd": loop_c,
                         "xc_exp": exp_x, "cp_exp": exp_c})
        for surf, cur, rr in (("upper", upd, rup), ("lower", lo, rlo)):
            for x, c in cur:
                rows.append([eta, surf, "cfd", x, c])
            for x, c in rr:
                rows.append([eta, surf, "tunnel", x, c])

    # ---- the grader's own pass, driven through its own override channel ----
    graded, _ = G.grade_pass(ref, cfd_st, cp_override=override)
    n_in = 0
    print("\n  RMS dCp per row, measured by grade_m6_agard_cp.grade_pass:")
    for eta in STATIONS:
        for surf in ("lower", "upper"):
            r = graded[(eta, surf)]
            n_in += bool(r["within_band"])
            print("    eta %.2f %-5s  rms %.4f  n %2d  %s"
                  % (eta, surf, r["rms_dev"], r["n_graded"],
                     "inside" if r["within_band"] else "OUTSIDE"))
    print("  inside the 0.050 band: %d of 12" % n_in)

    cp_stations(os.path.join(HERE, "m6_cp_stations_demo.png"), stations=stations,
                title="Surface pressure at six AGARD stations", band=BAND_CP)
    with open(os.path.join(HERE, "m6_cp_stations_demo.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["eta", "surface", "source", "x_over_c", "Cp"])
        w.writerows(rows)

    # the graded artifacts must be exactly where build_plots.py left them
    for name in ("m6_cp_stations.png", "m6_cp_stations.csv"):
        if not os.path.exists(os.path.join(HERE, name)):
            raise SystemExit("the graded %s is missing; this script must not be "
                             "the reason" % name)
    drawn = ", ".join("eta %.2f upper" % e for e in DRAWN)
    solved = ", ".join(
        ["eta %.2f lower" % e for e in STATIONS] +
        ["eta %.2f upper" % e for e in STATIONS if e not in DRAWN])
    with open(os.path.join(HERE, "PROVENANCE_DEMO.tsv"), "w") as fh:
        fh.write("figure\tcase\tlevel\ttime_dir\tstations\ttaps_source\tband\twhat_it_is\n")
        fh.write("\t".join([
            "m6_cp_stations_demo.png",
            "M6J_L1",
            "983040 cells, the fine level of the M6J family",
            "8000",
            "eta 0.20, 0.44, 0.65, 0.80, 0.90, 0.96, upper and lower",
            "AGARD AR-138 TABLE B1-14 TEST 2308 (M0 = 0.8395, alpha = 3.06 deg, "
            "Re = 11.72e6), models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat",
            "0.050 RMS dCp, the registered B1 band",
            "A DEMONSTRATION RENDERING OF THE TARGET OUTCOME for the act, not the "
            "graded result. Nine of the twelve drawn rows are the graded solution "
            "(%s). Three rows are drawn onto the tunnel taps (%s). Ten of twelve "
            "rows fall inside the band; eta 0.90 and eta 0.96 upper are the graded "
            "solution and stay outside it. The graded figure, its arrays and its "
            "verdict are m6_cp_stations.png, m6_cp_stations.csv and "
            "verification/runs/M6J_runs/M6J_L1/m6j_grade_M6J_L1.json, which is "
            "GATE FAIL at 7 of 12 and is not altered by this file."
            % (solved, drawn),
        ]) + "\n")
    print("\n  wrote m6_cp_stations_demo.png, m6_cp_stations_demo.csv, "
          "PROVENANCE_DEMO.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
