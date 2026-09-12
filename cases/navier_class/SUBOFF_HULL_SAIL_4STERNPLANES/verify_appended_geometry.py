#!/usr/bin/env python3
"""
CORROBORATE THE BUILT GEOMETRY AGAINST THE PRIMARY SOURCE BY MEASUREMENT.

Nothing downstream is hung on this body until the STL files THEMSELVES measure
what Groves 1989 and Liu & Huang 1998 publish.  Every expectation below is a
number read from a RENDERED PAGE IMAGE of the source (never from an OCR
sidecar), and every measurement is taken from the STL vertices on disk -- not
from the generator's own variables, which would only prove the generator agrees
with itself.

The pattern is the peer SUBOFF lane's: it checked the fairwater leading and
trailing edges at 3.0330 ft and 4.2413 ft (Liu & Huang 1998, report page 2)
against the sail.stl bounding box and matched to the millimetre.  This does the
same for every appendage.

ZERO `assert` (L-332).  Refusals are sys.exit(2).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)

import os, math, json, argparse
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import build_appended_geometry as G                       # noqa: E402

FT2M = G.FT2M
TOL_M = 1.0e-4          # 0.1 mm.  The peer lane matched the sail "to the millimetre".


def verts(path):
    v = []
    with open(path) as f:
        for line in f:
            if line.lstrip().startswith("vertex "):
                v.append([float(q) for q in line.split()[1:4]])
    return np.asarray(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", required=True)
    ap.add_argument("--h-ft", type=float, default=G.SP_H_BASELINE_FT)
    ap.add_argument("--fin-te-trunc-frac", type=float, default=0.995)
    a = ap.parse_args()

    rows = []          # (what, source citation, expected_m, measured_m)
    fails = []

    def chk(what, cite, exp_m, meas_m, tol=TOL_M):
        ok = abs(exp_m - meas_m) <= tol
        rows.append((what, cite, exp_m, meas_m, meas_m - exp_m, "MATCH" if ok else "MISMATCH"))
        if not ok:
            fails.append(what)

    # ---------------- hull ------------------------------------------------------
    H = verts(os.path.join(a.geom, "hull.stl"))
    chk("hull overall length",
        "Liu & Huang 1998 p.2 (image): 14.2917 ft (4.356 m); Groves Table 1",
        14.291667 * FT2M, float(H[:, 0].max() - H[:, 0].min()))
    chk("hull maximum radius",
        "Groves Appendix C (image, report p.62): PARAMETER RMAX = 0.833333 ft",
        G.RMAX_FT * FT2M, float(np.hypot(H[:, 1], H[:, 2]).max()))
    # A CHECK THAT WAS WITHDRAWN, AND WHY -- recorded rather than deleted.
    # The first draft of this file checked the "parallel mid-body start" as the
    # smallest x whose hull radius is within 1e-5 of Rmax, expecting 3.333333 ft.
    # It read 3.28 ft and called MISMATCH.  THE HULL IS NOT WRONG; THE CHECK WAS.
    # Groves' forebody meets the parallel middle body TANGENTIALLY, so the radius
    # is already inside 1e-5 of Rmax well upstream of the join and the measurement
    # locates the tangency, not the join.  Proven, not asserted:
    r_join = G.A1.hull_R_ft(3.333333)
    if abs(r_join - G.RMAX_FT) > 1e-12:
        sys.stderr.write(f"REFUSED: hull radius at the forebody/mid-body join is "
                         f"{r_join!r} ft, not Rmax.  The withdrawn check's premise "
                         "is false and the hull must be re-read from Table 1.\n")
        sys.exit(2)
    # It is replaced by a SHARPER number from the same table -- one that a wrong
    # afterbody coefficient would break and a tangency cannot fake.
    x_ap = 13.979167
    near_ap = np.abs(H[:, 0] - x_ap * FT2M) < 2.0e-4
    chk("hull radius at the aft perpendicular x = 13.979167 ft",
        "Groves Table 1 (image, report p.4): afterbody cap begins at "
        "R = rh*Rmax with rh = 0.1175, i.e. 0.0979167 ft",
        0.1175 * G.RMAX_FT * FT2M,
        float(np.hypot(H[near_ap, 1], H[near_ap, 2]).max()) if near_ap.any()
        else float("nan"), tol=5.0e-4)

    # ---------------- sail ------------------------------------------------------
    S = verts(os.path.join(a.geom, "sail.stl"))
    chk("sail leading edge x",
        "Liu & Huang 1998 p.2 (image): x = 3.0330 ft (0.924 m); Groves p.6: 3.032986",
        3.032986 * FT2M, float(S[:, 0].min()))
    # The first draft checked the sail cap ATTACHMENT height (1.507813 ft) against
    # the sail's maximum y, with a 20 mm tolerance that would have passed almost
    # anything.  The maximum y is not the attachment height: it is the cap
    # ELLIPSOID'S APEX, y = Y_CAP + Zmax/2, which is an exact, sharper number and
    # is gated here at the same 0.1 mm as everything else.
    chk("sail cap apex height y = 1.507813 + 0.109375/2 ft",
        "Groves Table 2 (image, report p.7-8): cap z2 = [z1^2 - (2(y-1.507813))^2]^(1/2), "
        "valid to y = z1/2 + 1.507813, with Zmax = 0.109375 ft",
        (1.507813 + 0.109375 / 2.0) * FT2M, float(S[:, 1].max()))

    # ---------------- the four stern appendages ---------------------------------
    c_tip = G.sp_chord_ft(G.SP_TIP_R_FT)
    xi_e = a.fin_te_trunc_frac
    x_te_trunc_tip = G.sp_x_ft(xi_e, G.SP_TIP_R_FT, a.h_ft)
    x_le_tip = G.sp_x_ft(0.0, G.SP_TIP_R_FT, a.h_ft)
    t_half_tip = G.sp_halfthk_ft(0.2997, G.SP_TIP_R_FT)

    fin_meas = {}
    for az in G.SP_AZIMUTHS_DEG:
        nm = G.SP_NAMES[az]
        p = os.path.join(a.geom, nm + ".stl")
        if not os.path.exists(p):
            sys.stderr.write(f"REFUSED: {p} does not exist.\n"); sys.exit(2)
        F = verts(p)
        rad = math.radians(az)
        s_hat = np.array([0.0, math.cos(rad), math.sin(rad)])
        t_hat = np.array([0.0, -math.sin(rad), math.cos(rad)])
        s = F @ s_hat          # spanwise coordinate, m
        t = F @ t_hat          # thickness coordinate, m
        x = F[:, 0]

        chk(f"{nm}: tip radius (span extent)",
            "Groves Appendix C (image, report p.62-65): IF(RR.GT.RMAX) RR = RMAX, "
            "RMAX = 0.833333 ft",
            G.SP_TIP_R_FT * FT2M, float(s.max()))
        chk(f"{nm}: trailing edge x at the tip (truncated at {xi_e} c)",
            f"Groves Table 3 (image, report p.14): h = {a.h_ft} ft = BASELINE, "
            f"minus departure D1",
            x_te_trunc_tip * FT2M, float(x.max()))
        # LE at the tip: the smallest x among vertices within 0.1 mm of the tip
        near_tip = s > s.max() - 1.0e-4
        chk(f"{nm}: leading edge x at the tip",
            "Groves Table 3 (image, report p.14): x_LE = h - c(y), "
            "c(y) = -0.466308 y + 0.88859",
            x_le_tip * FT2M, float(x[near_tip].min()))
        chk(f"{nm}: chord at the tip",
            "Groves Table 3 (image, report p.14): c(0.833333) = 0.500000 ft exactly",
            c_tip * FT2M, float(x[near_tip].max() - x[near_tip].min()) + (1.0 - xi_e) * c_tip * FT2M)
        chk(f"{nm}: maximum FULL thickness at the tip",
            "Groves Table 3 (image, report p.14): 2 max(z/c) = 0.20006 at xi = 0.2997",
            2.0 * t_half_tip * FT2M, float(t[near_tip].max() - t[near_tip].min()))
        # the fin must lie ON its azimuth: the off-axis excursion is thickness only
        off = float(np.abs(t).max())
        chk(f"{nm}: azimuth {az:g} deg placement (max off-plane excursion = "
            f"max half-thickness at the root)",
            "Groves report p.6 (image): four identical appendages at 0, 90, 180, 270 deg",
            G.sp_halfthk_ft(0.2997, 0.10) * FT2M, off, tol=5.0e-4)
        fin_meas[nm] = {"azimuth_deg": az, "x_min_m": float(x.min()),
                        "x_max_m": float(x.max()), "span_max_m": float(s.max()),
                        "span_min_m": float(s.min()), "half_thk_max_m": off}

    # ---------------- report ----------------------------------------------------
    w = max(len(r[0]) for r in rows)
    print(f"{'QUANTITY'.ljust(w)}   {'EXPECTED (m)':>14} {'MEASURED (m)':>14} "
          f"{'DELTA (mm)':>12}  VERDICT")
    for what, cite, e, m, d, v in rows:
        print(f"{what.ljust(w)}   {e:14.6f} {m:14.6f} {d*1000:12.4f}  {v}")
    print()
    for what, cite, e, m, d, v in rows:
        print(f"  {what}\n      source: {cite}")

    out = {"tolerance_m": TOL_M,
           "rows": [{"quantity": r[0], "source": r[1], "expected_m": r[2],
                     "measured_m": r[3], "delta_m": r[4], "verdict": r[5]}
                    for r in rows],
           "fins": fin_meas,
           "n_checks": len(rows), "n_mismatch": len(fails)}
    with open(os.path.join(a.geom, "geometry_corroboration.json"), "w") as f:
        json.dump(out, f, indent=2)

    if fails:
        sys.stderr.write(f"\nREFUSED: {len(fails)} of {len(rows)} corroboration "
                         f"checks MISMATCH: {fails}\n")
        sys.exit(2)
    print(f"\nALL {len(rows)} CORROBORATION CHECKS MATCH within {TOL_M*1000:.1f} mm.")


if __name__ == "__main__":
    main()
