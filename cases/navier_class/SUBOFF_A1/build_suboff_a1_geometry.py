#!/usr/bin/env python3
"""
SUBOFF_A1 -- GEOMETRY GENERATOR.  DARPA SUBOFF Configuration 2 (axisymmetric hull
WITH FAIRWATER/SAIL) as two CLOSED STL solids for snappyHexMesh.

GEOMETRY PROVENANCE (CLAUDE.md rule 15, title page verified by RENDERING).
  N.C. Groves, T.T. Huang, M.S. Chang, "Geometric Characteristics of DARPA SUBOFF
  Models (DTRC Model Nos. 5470 and 5471)", David Taylor Research Center,
  DTRC/SHD-1298-01, March 1989, AD-A210 642, approved for public release.
  docs/papers/benchmark_test_cases/groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf
  TITLE PAGE  read as a RENDERED IMAGE of PDF page 1 by a cfd lab-lane 2026-09-11.
  TABLE 1 (hull)      -- report pages 5-6.
  TABLE 2 (fairwater) -- report pages 7-8  ==  PDF pages 14-15, read as RENDERED
                         IMAGES, not from the OCR sidecar (the sidecar mangles
                         "x=4.241319" to "x*4. 241319" and cannot be trusted for
                         a coefficient).

  NOTE ON A CITATION DEFECT IN THE A1 DRAFT: SUBOFF_A1_PREREGISTRATION.md sec.3.2
  cites Table 2 at "PDF pages 18-19".  PDF pages 18-19 carry FIGURE 5 (stern
  appendage locations) and the stern-appendage / ring-wing text (report pages
  11-12).  Table 2 is at PDF pages 14-15.  The EQUATIONS quoted in that draft are
  nevertheless correct -- verified here term by term against the rendered pages.

UNITS.  The source equations are in FEET, model scale.  Everything is emitted in
METRES (x 0.3048), matching cases/navier_class/SUBOFF/build_suboff.py.

REGISTERED DEPARTURE (the only one).  The sail trailing edge closes to a
MATHEMATICAL POINT in the reference geometry (z1(x=TE) = 0 exactly, verified
numerically below and REFUSED if it is not).  It is TRUNCATED at TE_TRUNC_FRAC of
the sail chord.  Magnitude is printed and written to the manifest.

ZERO `assert` (L-332).  Refusals are raise / sys.exit(2).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)

import os, math, json, argparse
import numpy as np

FT2M = 0.3048

# ---------------- TABLE 1 : HULL (feet) ----------------------------------------
RMAX_FT    = 5.0 / 6.0
L_BOW_END  = 3.333333
L_PMB_END  = 10.645833
L_AFT_PERP = 13.979167
L_TOTAL_FT = 14.291667
AFT_RH, AFT_KO, AFT_K1 = 0.1175, 10.0, 44.6244


def hull_R_ft(x):
    """Hull radius R (ft) at station x (ft).  TABLE 1 exactly."""
    if x < 0.0 or x > L_TOTAL_FT:
        return 0.0
    if x <= L_BOW_END:
        t = 0.3 * x - 1.0
        inner = (1.126395101 * x * t**4 + 0.442874707 * x * x * t**3
                 + 1.0 - (t**4) * (1.2 * x + 1.0))
        return RMAX_FT * max(inner, 0.0) ** (1.0 / 2.1)
    if x <= L_PMB_END:
        return RMAX_FT
    if x <= L_AFT_PERP:
        xi = (L_AFT_PERP - x) / 3.333333
        rh, Ko, K1 = AFT_RH, AFT_KO, AFT_K1
        poly = (rh * rh + rh * Ko * xi * xi
                + (20 - 20 * rh * rh - 4 * rh * Ko - K1 / 3.0) * xi**3
                + (-45 + 45 * rh * rh + 6 * rh * Ko + K1) * xi**4
                + (36 - 36 * rh * rh - 4 * rh * Ko - K1) * xi**5
                + (-10 + 10 * rh * rh + rh * Ko + K1 / 3.0) * xi**6)
        return RMAX_FT * max(poly, 0.0) ** 0.5
    return 0.1175 * RMAX_FT * max(1.0 - (3.2 * x - 44.733333) ** 2, 0.0) ** 0.5


# ---------------- TABLE 2 : FAIRWATER / SAIL (feet) ----------------------------
# Read from the RENDERED PDF pages 14-15 (report pages 7-8), 2026-09-11.
SAIL_LE      = 3.032986      # Ft
SAIL_FB_END  = 3.358507      # Ft   forebody end   (LE + .325521)
SAIL_PMB_END = 3.559028      # Ft   parallel MB end(+ .200521)
SAIL_TE      = 4.241319      # Ft   trailing edge  (+ .682292)
SAIL_CHORD   = 1.208333      # Ft   total sail length
ZMAX_FT      = 0.109375      # Ft   ONE-HALF the maximum sail thickness
Y_CAP        = 1.507813      # Ft   sail cap attaches at this height
SPAN_UNIFORM = 0.674479      # Ft   span of sail with uniform profile (recorded)


def sail_z1_ft(x):
    """Sail HALF-thickness z1 (ft) at station x (ft).  TABLE 2 exactly.
    Forebody   : z1 = Zmax [2.094759 A + .2071781 B + C]^(1/2),
                 A = 2D(D-1)^4, B = 1/3 D^2 (D-1)^3, C = 1 - (D-1)^4 (4D+1),
                 D = 3.072000 (x - 3.032986)
    Parallel MB: z1 = Zmax
    Afterbody  : z1 = .1093750 [ 2.238361 E(E-1)^4 + 3.106529 E^2(E-1)^3
                                 + (1 - (E-1)^4 (4E+1)) ]      <-- NO square root
                 E = (4.241319 - x)/0.6822917
    """
    if x < SAIL_LE or x > SAIL_TE:
        return 0.0
    if x <= SAIL_FB_END:
        D = 3.072000 * (x - SAIL_LE)
        A = 2.0 * D * (D - 1.0) ** 4
        B = (1.0 / 3.0) * D * D * (D - 1.0) ** 3
        C = 1.0 - (D - 1.0) ** 4 * (4.0 * D + 1.0)
        return ZMAX_FT * max(2.094759 * A + 0.2071781 * B + C, 0.0) ** 0.5
    if x <= SAIL_PMB_END:
        return ZMAX_FT
    E = (SAIL_TE - x) / 0.6822917
    return 0.1093750 * max(2.238361 * (E * (E - 1.0) ** 4)
                           + 3.106529 * (E * E * (E - 1.0) ** 3)
                           + (1.0 - (E - 1.0) ** 4 * (4.0 * E + 1.0)), 0.0)


def sail_cap_z2_ft(x, y):
    """Sail cap ellipsoid.  z2 = [z1^2 - (2(y - 1.507813))^2]^(1/2),
    valid 1.507813 <= y <= z1/2 + 1.507813."""
    z1 = sail_z1_ft(x)
    v = z1 * z1 - (2.0 * (y - Y_CAP)) ** 2
    return max(v, 0.0) ** 0.5


# ---------------- STL emission --------------------------------------------------
SNAP_ABS = 2.0e-7      # m = 0.2 um.  Below this a coordinate snaps to exactly 0.
MIN_TRI_AREA = 1.0e-16  # m^2.  Below this the triangle is DROPPED, not written.


def _snap(p):
    q = p.copy()
    q[np.abs(q) < SNAP_ABS] = 0.0
    return q


def write_stl(path, name, tris):
    ndrop = 0
    with open(path, "w") as f:
        f.write(f"solid {name}\n")
        for a, b, c in tris:
            a, b, c = _snap(a), _snap(b), _snap(c)
            n = np.cross(b - a, c - a)
            ln = np.linalg.norm(n)
            if 0.5 * ln < MIN_TRI_AREA:
                ndrop += 1
                continue
            n = n / ln
            f.write(f"  facet normal {n[0]:.8e} {n[1]:.8e} {n[2]:.8e}\n   outer loop\n")
            for p in (a, b, c):
                f.write(f"    vertex {p[0]:.9e} {p[1]:.9e} {p[2]:.9e}\n")
            f.write("   endloop\n  endfacet\n")
        f.write(f"endsolid {name}\n")
    if ndrop:
        print(f"  {name}: dropped {ndrop} degenerate triangles (area < {MIN_TRI_AREA} m2)")


def cosine_stations(lo, hi, n):
    t = np.linspace(0.0, math.pi, n)
    return lo + (hi - lo) * (1.0 - np.cos(t)) / 2.0


def build_hull_stl(path, n_axial, n_theta):
    """Closed body of revolution about x, nose apex at x=0, tail apex at L."""
    xs = np.unique(np.concatenate([
        cosine_stations(0.0, L_BOW_END, n_axial // 3),
        np.linspace(L_BOW_END, L_PMB_END, max(8, n_axial // 6)),
        cosine_stations(L_PMB_END, L_TOTAL_FT, n_axial // 2)]))
    R = np.array([hull_R_ft(x) for x in xs])
    th = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)
    ct, st = np.cos(th), np.sin(th)
    tris = []
    # ring vertices in METRES; y = R cos(theta) (theta=0 is TOP DEAD CENTRE, +y),
    # z = R sin(theta).  The sail sits at top dead centre, so theta=0 is the root.
    P = np.empty((len(xs), n_theta, 3))
    for i, (x, r) in enumerate(zip(xs, R)):
        P[i, :, 0] = x * FT2M
        P[i, :, 1] = r * ct * FT2M
        P[i, :, 2] = r * st * FT2M
    for i in range(len(xs) - 1):
        for j in range(n_theta):
            k = (j + 1) % n_theta
            a, b, c, d = P[i, j], P[i, k], P[i + 1, k], P[i + 1, j]
            if R[i] <= 0.0:        # NOSE apex: one triangle apex->next ring,
                tris.append((a, c, d))          # oriented so n points UPSTREAM
                continue
            if R[i + 1] <= 0.0:    # TAIL apex: ring->apex, n points DOWNSTREAM
                tris.append((a, b, c))
                continue
            tris.append((a, b, c)); tris.append((a, c, d))
    write_stl(path, "hull", tris)
    return len(tris), xs, R


def build_sail_stl(path, n_chord, n_span, te_trunc_frac):
    """CLOSED sail solid.  Spans y from 0 (well inside the hull) up over the cap.
    The trailing edge is TRUNCATED at te_trunc_frac of the sail chord."""
    x_te = SAIL_LE + te_trunc_frac * SAIL_CHORD
    xs = np.unique(np.concatenate([
        cosine_stations(SAIL_LE, SAIL_FB_END, max(8, n_chord // 3)),
        np.linspace(SAIL_FB_END, SAIL_PMB_END, max(4, n_chord // 8)),
        cosine_stations(SAIL_PMB_END, x_te, max(10, n_chord // 2))]))
    z1 = np.array([sail_z1_ft(x) for x in xs])
    y_lo = 0.0                                   # deep inside the hull: union works
    ys_side = np.linspace(y_lo, Y_CAP, n_span)
    tris = []

    def V(x, y, z):
        return np.array([x * FT2M, y * FT2M, z * FT2M])

    # --- the two side walls (prismatic in y up to Y_CAP) ---
    for i in range(len(xs) - 1):
        for j in range(len(ys_side) - 1):
            for s in (+1.0, -1.0):
                a = V(xs[i],     ys_side[j],     s * z1[i])
                b = V(xs[i + 1], ys_side[j],     s * z1[i + 1])
                c = V(xs[i + 1], ys_side[j + 1], s * z1[i + 1])
                d = V(xs[i],     ys_side[j + 1], s * z1[i + 1] * 0 + s * z1[i])
                if s > 0:
                    tris.append((a, b, c)); tris.append((a, c, d))
                else:
                    tris.append((a, c, b)); tris.append((a, d, c))
    # --- the cap ellipsoid ---
    n_cap = max(6, n_span // 3)
    for i in range(len(xs) - 1):
        zc0, zc1 = z1[i], z1[i + 1]
        yt0, yt1 = Y_CAP + zc0 / 2.0, Y_CAP + zc1 / 2.0
        for j in range(n_cap):
            f0, f1 = j / n_cap, (j + 1) / n_cap
            yA0, yA1 = Y_CAP + f0 * (yt0 - Y_CAP), Y_CAP + f0 * (yt1 - Y_CAP)
            yB0, yB1 = Y_CAP + f1 * (yt0 - Y_CAP), Y_CAP + f1 * (yt1 - Y_CAP)
            for s in (+1.0, -1.0):
                a = V(xs[i],     yA0, s * sail_cap_z2_ft(xs[i],     yA0))
                b = V(xs[i + 1], yA1, s * sail_cap_z2_ft(xs[i + 1], yA1))
                c = V(xs[i + 1], yB1, s * sail_cap_z2_ft(xs[i + 1], yB1))
                d = V(xs[i],     yB0, s * sail_cap_z2_ft(xs[i],     yB0))
                if s > 0:
                    tris.append((a, b, c)); tris.append((a, c, d))
                else:
                    tris.append((a, c, b)); tris.append((a, d, c))
    # --- the truncated TRAILING-EDGE BASE (the registered departure) ---
    i = len(xs) - 1
    zb = z1[i]
    ys_base = np.concatenate([ys_side, Y_CAP + np.linspace(0, zb / 2.0, n_cap + 1)[1:]])
    for j in range(len(ys_base) - 1):
        yl, yh = ys_base[j], ys_base[j + 1]
        zl = zb if yl <= Y_CAP else sail_cap_z2_ft(xs[i], yl)
        zh = zb if yh <= Y_CAP else sail_cap_z2_ft(xs[i], yh)
        a = V(xs[i], yl, -zl); b = V(xs[i], yl, zl)
        c = V(xs[i], yh,  zh); d = V(xs[i], yh, -zh)
        tris.append((a, b, c)); tris.append((a, c, d))
    # --- the bottom lid at y = y_lo (buried inside the hull) ---
    for i in range(len(xs) - 1):
        a = V(xs[i],     y_lo, -z1[i])
        b = V(xs[i],     y_lo,  z1[i])
        c = V(xs[i + 1], y_lo,  z1[i + 1])
        d = V(xs[i + 1], y_lo, -z1[i + 1])
        tris.append((a, c, b)); tris.append((a, d, c))
    # --- the leading-edge closure (z1 -> 0 at the LE is a genuine apex) ---
    write_stl(path, "sail", tris)
    return len(tris), x_te, z1[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-axial", type=int, default=600)
    ap.add_argument("--n-theta", type=int, default=180)
    ap.add_argument("--n-chord", type=int, default=240)
    ap.add_argument("--n-span", type=int, default=120)
    ap.add_argument("--te-trunc-frac", type=float, default=0.995)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # ---- REFUSALS that make the departure honest -------------------------------
    z_te_exact = sail_z1_ft(SAIL_TE)
    if abs(z_te_exact) > 1.0e-12:
        sys.stderr.write(f"REFUSED: sail TE half-thickness is {z_te_exact!r}, not 0. "
                         "The cusp premise of the registered truncation is false; "
                         "re-read Table 2 before building.\n")
        sys.exit(2)
    if not (0.90 <= a.te_trunc_frac < 1.0):
        sys.stderr.write("REFUSED: --te-trunc-frac outside [0.90, 1.0).\n"); sys.exit(2)
    r_root = hull_R_ft(SAIL_LE)
    if r_root <= 0.0 or r_root >= RMAX_FT * 1.0001:
        sys.stderr.write("REFUSED: hull radius at the sail LE is not in (0, Rmax].\n")
        sys.exit(2)

    nh, xs, R = build_hull_stl(os.path.join(a.out, "hull.stl"), a.n_axial, a.n_theta)
    ns, x_te, z_base = build_sail_stl(os.path.join(a.out, "sail.stl"),
                                      a.n_chord, a.n_span, a.te_trunc_frac)

    man = {
        "source": "Groves, Huang, Chang 1989, DTRC/SHD-1298-01 (AD-A210 642)",
        "source_pdf": "docs/papers/benchmark_test_cases/"
                      "groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf",
        "title_page_verified_by": "RENDERED IMAGE of PDF page 1, cfd lab-lane 2026-09-11",
        "table1_pages_report": "5-6", "table2_pages_pdf_rendered": "14-15",
        "configuration": "Configuration 2 -- axisymmetric body WITH FAIRWATER, zero incidence",
        "units_emitted": "metres (source is feet, x0.3048)",
        "hull": {"L_ft": L_TOTAL_FT, "L_m": L_TOTAL_FT * FT2M,
                 "Rmax_ft": RMAX_FT, "Dmax_m": 2 * RMAX_FT * FT2M,
                 "LoverD": L_TOTAL_FT / (2 * RMAX_FT), "n_tris": nh},
        "sail": {"LE_ft": SAIL_LE, "TE_ft_reference": SAIL_TE,
                 "chord_ft": SAIL_CHORD, "zmax_ft": ZMAX_FT,
                 "span_uniform_ft": SPAN_UNIFORM, "y_cap_ft": Y_CAP,
                 "root_hull_radius_at_LE_ft": r_root, "n_tris": ns},
        "REGISTERED_DEPARTURE_te_truncation": {
            "reference_TE_half_thickness_ft": z_te_exact,
            "reference_TE_closes_to": "a MATHEMATICAL POINT (exactly zero)",
            "truncation_fraction_of_chord": a.te_trunc_frac,
            "truncated_TE_x_ft": x_te,
            "base_half_thickness_ft": z_base,
            "base_half_thickness_mm": z_base * FT2M * 1000.0,
            "base_FULL_thickness_mm": 2.0 * z_base * FT2M * 1000.0,
            "base_over_chord_percent": 100.0 * 2.0 * z_base / SAIL_CHORD,
            "chord_removed_mm": (SAIL_TE - x_te) * FT2M * 1000.0,
        },
    }
    with open(os.path.join(a.out, "geometry_manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    d = man["REGISTERED_DEPARTURE_te_truncation"]
    print(f"hull.stl  {nh} triangles     sail.stl  {ns} triangles")
    print(f"REGISTERED DEPARTURE: sail TE truncated at {a.te_trunc_frac} c "
          f"-> base FULL thickness {d['base_FULL_thickness_mm']:.4f} mm "
          f"= {d['base_over_chord_percent']:.4f} % of chord; "
          f"{d['chord_removed_mm']:.3f} mm of chord removed.")


if __name__ == "__main__":
    main()
