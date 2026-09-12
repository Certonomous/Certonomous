#!/usr/bin/env python3
"""
DARPA SUBOFF **RODDY CONFIGURATION 1** -- GEOMETRY GENERATOR.
hull + bridge fairwater + four stern appendages + RING WING NO. 1 + FOUR STRUTS.

=============================================================================
NAMED BY ITS APPENDAGE INVENTORY, NEVER BY A BARE NUMBER AND NEVER BY THE
PHRASE "FULLY APPENDED" ALONE.
=============================================================================
This body is: the DARPA SUBOFF axisymmetric hull, WITH the bridge fairwater
(sail) at top dead centre, WITH four identical stern appendages at the BASELINE
axial position, WITH ring wing no. 1, and WITH its four support struts.

In Roddy 1990's scheme (Table 3, report pages 17-18, read as page images) this
is the body printed "CONFIGURATION 1 - VERTICAL PLANE, FULLY APPENDED WITH RING
WING NO. 1" -- the ONLY configuration in the entire programme for which
vertical-plane derivatives Z_w', M_w', Z_q', M_q' are published (Table 4,
report page 19).

IT IS **NOT** LIU AND HUANG'S "FULLY APPENDED".  Their Table 14, report page 23,
prints "8  Fully Appended" for the body WITHOUT a ring wing -- their ring wings
are separate rows 6 and 7.  THE SAME TWO WORDS NAME TWO DIFFERENT BODIES IN TWO
OFFICIAL REPORTS ON ONE PROGRAMME.  See build_appended_geometry.py, which builds
the other one.

=============================================================================
PROVENANCE (CLAUDE.md rule 15).  Groves, Huang, Chang 1989, DTRC/SHD-1298-01,
March 1989, AD-A210 642.  Title page read as a RENDERED IMAGE of PDF page 1.
That PDF is a pure image scan; its .txt sidecar is Internet Archive OCR and is a
reading aid only.  EVERY number below was read from a RENDERED PAGE.
=============================================================================
  HULL, SAIL, STERN APPENDAGES -- IMPORTED unchanged from
      build_appended_geometry.py (which imports the hull and sail unchanged from
      SUBOFF_A1).  Not re-typed, not copied.
  RING WING     -- Table 4, report pages 15-16, cross-read against Appendix D
                   ("DARPA2WINGS"), report pages 68-71.
  RING STRUTS   -- Table 5, report pages 19-20; narrative report page 18;
                   AZIMUTHS from Figure 9, report page 22.

FOUR DEFECTS IN THE PRINTED TABLES, FOUND, RESOLVED AND ASSERTED AT RUN TIME:
  D-a  Table 4 prints thickness coefficient b5 = -0.90185.  Appendix D's DATA B
       array reads -0.00185.  SETTLED WITHOUT THE LISTING by an internal
       consistency test: the 17-term sine series (x < 0.45) and the quartic
       polynomial (x >= 0.45) are two branches of ONE curve and must agree where
       they meet.  With -0.00185 they agree to 1.34e-6; with the printed
       -0.90185 they disagree by 7.89e-2, 59,000 times worse.  ASSERTED below.
  D-b  Table 4's camber prints "+ 0.227828 = 0.531076x"; Appendix D has a MINUS.
  D-c  Table 4's placement block prints R_DU twice and never R_DL; Appendix D
       computes the LOWER surface in the fourth line.
  D-d  Table 5's strut section prints "+ 0.28520 xi^2"; the exponent is 3, as in
       Groves Table 3's stern appendage, which uses the same five coefficients.

AND ONE READING THAT WAS WRONG UNTIL FIGURE 9 WAS READ, RECORDED AS A NEAR MISS:
  the strut azimuths were provisionally read as 0/90/180/270 from Table 5's
  sentence about "the upper surface (i.e., the surface with the fairwater)".
  FIGURE 9 SHOWS THEM ON THE DIAGONALS.  The pressure taps in that figure are
  labelled W1U1/W1L1/W1P1/W1S1 -- Upper, Lower, Port, Starboard -- which pins the
  taps to the cardinal directions, and Table 5's "45 degree increment from the
  wing surface pressure tap locations" then gives 45/135/225/315.  The struts sit
  CLEAR of the stern-appendage wakes, not in them.

UNITS.  Source equations are in FEET.  Everything is emitted in METRES (x0.3048).

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
import build_appended_geometry as APP                    # noqa: E402

A1 = APP.A1
FT2M = APP.FT2M

# ---------------- TABLE 4 : RING WING 1 (feet) ---------------------------------
RW1 = {"x_le": 13.46990, "R_le": 0.43004, "x_te": 14.21661, "R_te": 0.35659}
RW2 = {"x_le": 13.46990, "R_le": 0.47681, "x_te": 14.20740, "R_te": 0.33856}

# thickness series, Appendix D DATA B (b5 corrected from Table 4's -0.90185)
RW_B = (0.43756, -0.08136, -0.06496, -0.01926, -0.00185,
        0.00348,  0.00156, -0.00113, -0.00058,  0.00027,
        0.00080,  0.00006, -0.00027, -0.00033,  0.00005,
        0.00014,  0.00008)
RW_POLY = (0.033333, 1.696969, -1.441945, -0.366363, 0.333049)
RW_XSPLIT = 0.45


def rw_yt(x):
    """Ring-wing HALF-thickness, nondimensional on the chord.  Two branches of
    ONE curve: Table 4's 17-term sine series below x = 0.45 and its quartic
    polynomial above."""
    if x < 0.0 or x > 1.0:
        return 0.0
    if x < RW_XSPLIT:
        om = math.acos(2.0 * x - 1.0)
        return 0.1 * sum(RW_B[j] * math.sin((j + 1) * om) for j in range(17))
    X = 1.0 - x
    a0, a1, a2, a3, a4 = RW_POLY
    return 0.1 * (a0 + a1 * X + a2 * X * X + a3 * X ** 3 + a4 * X ** 4)


def _guard(v):
    return 1.0e-30 if abs(v) <= 1.0e-20 else v


def rw_yc(x):
    """Ring-wing meanline (NACA a = 0.4), nondimensional on the chord.
    Table 4 with defect D-b corrected against Appendix D."""
    D = _guard(0.4 - x); E = _guard(1.0 - x); X = _guard(x)
    v = -0.049921 * (0.5 * D * D * math.log(abs(D)) - 0.5 * E * E * math.log(E)
                     + 0.25 * E * E - 0.25 * D * D)
    return v + 0.029953 * (X * math.log(X) + 0.227828 - 0.531076 * X)


def rw_ycp(x):
    """Meanline SLOPE.  Appendix D only -- Table 4 does not print it, and the
    surface construction cannot be done without it."""
    D = _guard(0.4 - x); E = _guard(1.0 - x); X = _guard(x)
    return (-0.049921 * (E * math.log(E) - D * math.log(abs(D)))
            + 0.02995253 * (math.log(X) + 0.4689244))


def rw_surface_ft(x, wing=RW1):
    """Return ((x_upper, R_upper), (x_lower, R_lower)) in FEET, in the hull frame.
    Appendix D's construction, which also settles defect D-c."""
    yt = rw_yt(x); yc = rw_yc(x)
    th = math.atan(rw_ycp(x)); s, c = math.sin(th), math.cos(th)
    xu, Ru = x - yt * s, yc + yt * c
    xl, Rl = x + yt * s, yc - yt * c
    dR = wing["R_te"] - wing["R_le"]; dx = wing["x_te"] - wing["x_le"]
    phi = math.atan2(dR, dx); C = math.hypot(dR, dx)
    cs, sn = math.cos(phi), math.sin(phi)
    return ((wing["x_le"] + C * (xu * cs - Ru * sn),
             wing["R_le"] + C * (xu * sn + Ru * cs)),
            (wing["x_le"] + C * (xl * cs - Rl * sn),
             wing["R_le"] + C * (xl * sn + Rl * cs)))


# ---------------- TABLE 5 : RING-WING STRUTS (feet) -----------------------------
ST_CHORD = 0.243995
ST_DY = 0.054465
ST_TMUL = 0.15
ST_X0A, ST_X0B = 0.223221, 13.556128
ST_COEF = APP.SP_COEF                  # the SAME five coefficients as Table 3
ST_R1, ST_R2 = 0.14726, 0.36886        # ring wing 1
# FIGURE 9, report page 22, read as a page image.  NOT 0/90/180/270.
ST_AZIMUTHS_DEG = (45.0, 135.0, 225.0, 315.0)
ST_NAMES = {45.0: "strut045", 135.0: "strut135",
            225.0: "strut225", 315.0: "strut315"}


def st_x0_ft(y0):
    return ST_X0A * y0 + ST_X0B


def st_halfthk_ft(xi):
    if xi < 0.0 or xi > 1.0:
        return 0.0
    a0, a1, a2, a3, a4 = ST_COEF
    return ST_TMUL * (a0 * math.sqrt(xi) + a1 * xi + a2 * xi * xi
                      + a3 * xi ** 3 + a4 * xi ** 4)


# ---------------- STL builders ---------------------------------------------------
def build_ringwing_stl(path, name, n_chord, n_theta, wing=RW1):
    """CLOSED annular solid of revolution about the hull axis.

    The section's LEADING edge closes to a point (y_t(0) = 0 and y_c(0) = 0), so
    the upper and lower curves share it.  Its TRAILING edge does NOT: y_t(1) =
    0.1 x 0.033333 gives a FINITE base thickness BY DESIGN, so -- unlike the sail
    and the appendages -- THERE IS NO TRUNCATION DEPARTURE HERE.
    """
    xs = APP._cos_cluster(n_chord)
    up = []; lo = []
    for x in xs:
        (xu, Ru), (xl, Rl) = rw_surface_ft(float(x), wing)
        up.append((xu * FT2M, Ru * FT2M)); lo.append((xl * FT2M, Rl * FT2M))
    th = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False)
    ct, st = np.cos(th), np.sin(th)

    def ring(pt):
        x, R = pt
        return np.column_stack([np.full(n_theta, x), R * ct, R * st])

    U = [ring(p) for p in up]
    L = [ring(p) for p in lo]
    tris = []

    def band(A, B, flip):
        for j in range(n_theta):
            k = (j + 1) % n_theta
            a, b, c, d = A[j], A[k], B[k], B[j]
            if flip:
                tris.append((a, c, b)); tris.append((a, d, c))
            else:
                tris.append((a, b, c)); tris.append((a, c, d))

    for i in range(len(xs) - 1):
        band(U[i], U[i + 1], False)          # outer (upper) surface
        band(L[i], L[i + 1], True)           # inner (lower) surface
    # The finite trailing-edge base, U ring -> L ring.  MEASURED DEFECT, recorded
    # rather than quietly fixed: the first version wound this band the other way,
    # which gave 240 non-manifold directed edges (2 x n_theta -- one ring's worth
    # on each of the U and L seams) and a NEGATIVE signed volume.  With
    # theta_hat x r_hat = -x_hat, the unflipped winding is the one whose normal
    # points DOWNSTREAM, i.e. out of the solid.
    band(U[-1], L[-1], False)
    A1.write_stl(path, name, tris)
    return len(tris)


def build_strut_stl(path, name, azimuth_deg, n_chord, n_span,
                    te_trunc_frac, y0_lo, y0_hi, wing_key="RW1"):
    """One CLOSED strut solid at the given azimuth.  Extended INWARD past R1 into
    the hull and OUTWARD past R2 into the ring wing so snappyHexMesh unions all
    three; the true boundaries are Table 5's two intersection conditions, which
    are computed and reported but are not used to cut the STL."""
    a = math.radians(azimuth_deg)
    s_hat = np.array([0.0, math.cos(a), math.sin(a)])
    t_hat = np.array([0.0, -math.sin(a), math.cos(a)])
    xis = APP._cos_cluster(n_chord) * te_trunc_frac
    y0s = np.linspace(y0_lo, y0_hi, n_span)

    def V(xi, y0, sgn):
        x = st_x0_ft(y0) + ST_CHORD * xi
        y = y0 - ST_DY * xi
        z = sgn * st_halfthk_ft(xi)
        return (x * FT2M) * np.array([1.0, 0.0, 0.0]) \
            + (y * FT2M) * s_hat + (z * FT2M) * t_hat

    tris = []
    for i in range(len(xis) - 1):
        for j in range(len(y0s) - 1):
            for sgn in (+1.0, -1.0):
                p00 = V(xis[i], y0s[j], sgn); p10 = V(xis[i + 1], y0s[j], sgn)
                p11 = V(xis[i + 1], y0s[j + 1], sgn); p01 = V(xis[i], y0s[j + 1], sgn)
                if sgn > 0:
                    tris.append((p00, p10, p11)); tris.append((p00, p11, p01))
                else:
                    tris.append((p00, p11, p10)); tris.append((p00, p01, p11))
    for lidy, flip in ((y0s[-1], False), (y0s[0], True)):
        for i in range(len(xis) - 1):
            pa = V(xis[i], lidy, -1.0); pb = V(xis[i], lidy, +1.0)
            pc = V(xis[i + 1], lidy, +1.0); pd = V(xis[i + 1], lidy, -1.0)
            if flip:
                if not np.array_equal(pa, pb):
                    tris.append((pa, pc, pb))
                tris.append((pa, pd, pc))
            else:
                if not np.array_equal(pa, pb):
                    tris.append((pa, pb, pc))
                tris.append((pa, pc, pd))
    xe = xis[-1]
    for j in range(len(y0s) - 1):
        pa = V(xe, y0s[j], -1.0); pb = V(xe, y0s[j], +1.0)
        pc = V(xe, y0s[j + 1], +1.0); pd = V(xe, y0s[j + 1], -1.0)
        tris.append((pa, pc, pb)); tris.append((pa, pd, pc))
    A1.write_stl(path, name, tris)
    return len(tris)


# ---------------- main -------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rw-n-chord", type=int, default=241)
    ap.add_argument("--rw-n-theta", type=int, default=360)
    ap.add_argument("--st-n-chord", type=int, default=161)
    ap.add_argument("--st-n-span", type=int, default=81)
    ap.add_argument("--st-te-trunc-frac", type=float, default=0.98)
    ap.add_argument("--st-y0-inset-ft", type=float, default=0.030)
    ap.add_argument("--st-y0-outset-ft", type=float, default=0.035)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # ---- REFUSALS ON THE SOURCE DIGITS ----------------------------------------
    # D-a: the two thickness branches are ONE curve and must meet.  This test
    # settles b5 WITHOUT reference to Appendix D.
    lo = 0.1 * sum(RW_B[j] * math.sin((j + 1) * math.acos(2 * RW_XSPLIT - 1))
                   for j in range(17))
    X = 1.0 - RW_XSPLIT
    a0, a1, a2, a3, a4 = RW_POLY
    hi = 0.1 * (a0 + a1 * X + a2 * X * X + a3 * X ** 3 + a4 * X ** 4)
    if abs(lo - hi) > 1.0e-5:
        sys.stderr.write(f"REFUSED: the ring-wing thickness branches disagree at "
                         f"x = {RW_XSPLIT}: series {lo!r} vs polynomial {hi!r}.  "
                         "One of the coefficients is misread -- Table 4 prints "
                         "b5 = -0.90185, which fails this test by 7.89e-2; "
                         "Appendix D reads -0.00185.  Re-read the pages as "
                         "IMAGES before building.\n")
        sys.exit(2)
    tmax = max(rw_yt(x) for x in np.linspace(1e-9, 1.0, 40001))
    if not (0.0499 <= tmax <= 0.0501):
        sys.stderr.write(f"REFUSED: ring-wing max half-thickness {tmax!r}, not the "
                         "0.05 (10 % t/c) of the NACA 66 (DTNSRDC mod) family "
                         "Appendix D names.\n"); sys.exit(2)
    if abs(rw_yc(1e-12)) > 1e-6 or abs(rw_yc(1.0 - 1e-12)) > 1e-6:
        sys.stderr.write("REFUSED: the ring-wing meanline does not vanish at both "
                         "ends; Table 4's '= 0.531076x' has not been corrected to "
                         "a MINUS (defect D-b).\n"); sys.exit(2)
    cs = [rw_yc(float(x)) for x in np.linspace(1e-9, 1 - 1e-9, 40001)]
    xc_at_peak = float(np.linspace(1e-9, 1 - 1e-9, 40001)[int(np.argmin(cs))])
    if not (0.38 <= xc_at_peak <= 0.42):
        sys.stderr.write(f"REFUSED: meanline camber peaks at x/c = {xc_at_peak!r}, "
                         "not at the 0.4 of the NACA a = 0.4 meanline.\n")
        sys.exit(2)
    if abs(sum(ST_COEF)) > 1e-12:
        sys.stderr.write("REFUSED: strut section coefficients do not sum to 0.\n")
        sys.exit(2)
    if abs(st_x0_ft(ST_R1) - 13.589) > 1e-6:
        sys.stderr.write(f"REFUSED: x0(R1) = {st_x0_ft(ST_R1)!r}, not Table 5's "
                         "'Strut leading edge attaches to: Hull at x = 13.589'.\n")
        sys.exit(2)
    if abs(A1.hull_R_ft(13.589) - 0.14726) > 2e-5:
        sys.stderr.write("REFUSED: the hull radius at the strut LE attachment does "
                         "not match Table 5's R = 0.14726.\n"); sys.exit(2)

    # ---- the four surfaces already built, IMPORTED and unchanged ---------------
    # (hull, sail and the four fins come from build_appended_geometry.py; this
    # module ADDS to that body and never rebuilds it.)

    nrw = build_ringwing_stl(os.path.join(a.out, "ringwing1.stl"), "ringwing1",
                             a.rw_n_chord, a.rw_n_theta, RW1)
    rep = APP.closure_report(os.path.join(a.out, "ringwing1.stl"))
    if rep["non_manifold_directed_edges"] != 0 or rep["signed_volume_m3"] <= 0.0:
        sys.stderr.write(f"REFUSED: ringwing1.stl is not a closed, outward-oriented "
                         f"solid: {rep}\n"); sys.exit(2)

    struts = {}
    for az in ST_AZIMUTHS_DEG:
        nm = ST_NAMES[az]
        p = os.path.join(a.out, nm + ".stl")
        nt = build_strut_stl(p, nm, az, a.st_n_chord, a.st_n_span,
                             a.st_te_trunc_frac,
                             ST_R1 - a.st_y0_inset_ft, ST_R2 + a.st_y0_outset_ft)
        r = APP.closure_report(p)
        if r["non_manifold_directed_edges"] != 0 or r["signed_volume_m3"] <= 0.0:
            sys.stderr.write(f"REFUSED: {nm}.stl is not a closed, outward-oriented "
                             f"solid: {r}\n"); sys.exit(2)
        struts[nm] = {"azimuth_deg": az, "sha256": APP.sha256(p), **r}

    # ---- MEASURED geometry, for corroboration ----------------------------------
    dR = RW1["R_te"] - RW1["R_le"]; dx = RW1["x_te"] - RW1["x_le"]
    man = {
        "configuration_named_by_geometry":
            "hull WITH sail, four stern appendages at the BASELINE position, "
            "RING WING NO. 1 and four ring-wing struts",
        "label_as_printed": {
            "roddy_1990_table3_p17": "CONFIGURATION 1 - VERTICAL PLANE, FULLY "
                                     "APPENDED WITH RING WING NO. 1",
            "liu_huang_1998_table14_p23":
                "NOT this body -- their '8 Fully Appended' has NO ring wing",
        },
        "ring_wing_1": {
            "source": "Groves Table 4, report pp.15-16, cross-read against "
                      "Appendix D, report pp.68-71, both as page images",
            "x_le_ft": RW1["x_le"], "R_le_ft": RW1["R_le"],
            "x_te_ft": RW1["x_te"], "R_te_ft": RW1["R_te"],
            "chord_ft": math.hypot(dR, dx),
            "chord_m": math.hypot(dR, dx) * FT2M,
            "setting_angle_deg": math.degrees(math.atan2(dR, dx)),
            "max_half_thickness_over_chord": tmax,
            "max_full_t_over_c": 2.0 * tmax,
            "camber_peak_x_over_c": xc_at_peak,
            "TE_base_full_over_chord": 2.0 * rw_yt(1.0),
            "TE_base_full_mm": 2.0 * rw_yt(1.0) * math.hypot(dR, dx) * FT2M * 1000.0,
            "radial_gap_to_hull_at_LE_mm":
                (RW1["R_le"] - A1.hull_R_ft(RW1["x_le"])) * FT2M * 1000.0,
            "radial_gap_to_hull_at_TE_mm":
                (RW1["R_te"] - A1.hull_R_ft(RW1["x_te"])) * FT2M * 1000.0,
            "n_tris": nrw,
            "sha256": APP.sha256(os.path.join(a.out, "ringwing1.stl")),
            "NO_TE_TRUNCATION_DEPARTURE":
                "the section has a FINITE trailing-edge base by design",
        },
        "struts": {
            "source": "Groves Table 5, report pp.19-20; narrative p.18; "
                      "AZIMUTHS from Figure 9, report p.22, read as an image",
            "azimuths_deg": list(ST_AZIMUTHS_DEG),
            "azimuth_note":
                "45/135/225/315 -- STAGGERED BETWEEN the stern appendages, NOT "
                "aligned with them.  Figure 9's taps are labelled U/L/P/S "
                "(Upper/Lower/Port/Starboard), which pins the taps to the "
                "cardinal directions, and Table 5 places the struts at a 45 deg "
                "increment from the taps.",
            "chord_ft": ST_CHORD,
            "x0_of_y0": {"slope": ST_X0A, "intercept": ST_X0B},
            "dy_over_chord_ft": ST_DY,
            "thickness_multiplier_ft": ST_TMUL,
            "R1_ft": ST_R1, "R2_ft": ST_R2,
            "max_t_over_c": 2.0 * ST_TMUL * 0.10002881 / ST_CHORD,
            "self_check_x0_R1_ft": st_x0_ft(ST_R1),
            "self_check_x0_R2_ft": st_x0_ft(ST_R2),
            "self_check_hull_R_at_LE_attach_ft": A1.hull_R_ft(13.589),
            "TE_truncation_frac": a.st_te_trunc_frac,
            "y0_range_built_ft": [ST_R1 - a.st_y0_inset_ft,
                                  ST_R2 + a.st_y0_outset_ft],
            "stls": struts,
        },
        "HALF_MODEL_STILL_EXACT":
            "struts at 45/135/225/315 are mirror-symmetric about z = 0 "
            "(45<->315, 135<->225) and a ring wing is a surface of revolution, "
            "so the whole body keeps the z = 0 symmetry the half model rests on",
    }
    with open(os.path.join(a.out, "config1_manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    rw = man["ring_wing_1"]
    print(f"ringwing1.stl {nrw} tris   4 struts "
          f"{sum(v['n_tris'] for v in struts.values())} tris")
    print(f"  ring wing chord {rw['chord_ft']:.6f} ft = {rw['chord_m']:.6f} m, "
          f"setting angle {rw['setting_angle_deg']:.4f} deg")
    print(f"  t/c {rw['max_full_t_over_c']:.5f}, camber peak at x/c "
          f"{rw['camber_peak_x_over_c']:.4f}, TE base {rw['TE_base_full_mm']:.3f} mm")
    print(f"  radial gap to hull: LE {rw['radial_gap_to_hull_at_LE_mm']:.2f} mm, "
          f"TE {rw['radial_gap_to_hull_at_TE_mm']:.2f} mm")
    print(f"  struts at {ST_AZIMUTHS_DEG} deg (Figure 9, report p.22) -- "
          f"STAGGERED between the appendages")
    print(f"  SELF-CHECKS  x0(R1) {st_x0_ft(ST_R1):.6f} vs Table 5's 13.589 | "
          f"hull R at LE attach {A1.hull_R_ft(13.589):.6f} vs 0.14726 | "
          f"thickness branches meet to {abs(lo-hi):.2e}")


if __name__ == "__main__":
    main()
