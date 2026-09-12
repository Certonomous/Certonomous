#!/usr/bin/env python3
"""
DARPA SUBOFF -- HULL + BRIDGE FAIRWATER (SAIL) + FOUR IDENTICAL STERN APPENDAGES.
GEOMETRY GENERATOR.  Emits four closed STL solids for snappyHexMesh:
hull.stl, sail.stl and four fin STLs at azimuths 0 / 90 / 180 / 270 degrees.

=============================================================================
THE CONFIGURATION IS NAMED BY ITS GEOMETRY AND NEVER BY A BARE NUMBER, AND
"FULLY APPENDED" IS ITSELF AN AMBIGUOUS LABEL ACROSS THE TWO REPORTS.
=============================================================================
This body is: the DARPA SUBOFF axisymmetric hull, WITH the bridge fairwater
(sail) at top dead centre, WITH four identical stern appendages at the BASELINE
axial position, and WITHOUT any ring wing and WITHOUT ring-wing support struts.

Three numbering schemes are in play across the programme's own reports and they
COLLIDE ON THE SAME INTEGERS.  Every label below was read from a PAGE IMAGE:

  * Roddy 1990 (DTRC/SHD-1298-08), Table 3, report page 17 and page 18:
      "CONFIGURATION 1 - VERTICAL PLANE, FULLY APPENDED WITH RING WING NO. 1"
      "CONFIGURATION 2 - HORIZONTAL PLANE, FULLY APPENDED WITH RING WING NO. 1"
      "CONFIGURATION 3 - HORIZONTAL PLANE, BARE HULL"
      "CONFIGURATION 4 - HORIZONTAL PLANE, HULL AND SAIL ONLY"
      "CONFIGURATION 5 - HORIZONTAL PLANE, HULL AND CONTROL SURFACES ONLY"
      "CONFIGURATION 6 - HORIZONTAL PLANE, HULL AND RING WING NO.1 ONLY"
  * Liu and Huang 1998 (CRDKNSWC/HD-1298-11), report page 6, towing-tank list:
      "Config. 1  Bare hull only / Config. 3  Hull with four stern appendages /
       Config. 8  Hull with sail and four stern appendages / Config. 6 and 7 ring wings"
  * Liu and Huang 1998, Table 14, report page 23, "Config. No." column:
      "8  Fully Appended / 3  Stern Appendages / 1  Bare Hull /
       6  Ringed Wing #1 / 7  Ringed Wing #2"

  RODDY'S CONFIG 1 IS THE FULLEST BODY IN THE PROGRAMME.
  LIU AND HUANG'S CONFIG 1 IS THE EMPTIEST.  Same integer, two official reports.
  AND THE PHRASE "FULLY APPENDED" NAMES TWO DIFFERENT BODIES: Roddy's carries
  RING WING NO. 1; Liu and Huang's Table 14 "Fully Appended" does not (their
  ring wings are separate rows 6 and 7, and the tripwire footnote on that page
  names only "Hull, bridge fairwater and four identical stern appendages").
  THE BODY BUILT HERE IS LIU AND HUANG'S "FULLY APPENDED", NOT RODDY'S.

=============================================================================
GEOMETRY PROVENANCE (CLAUDE.md rule 15 -- title page verified by RENDERING).
=============================================================================
  N.C. Groves, T.T. Huang, M.S. Chang, "GEOMETRIC CHARACTERISTICS OF DARPA
  SUBOFF MODELS (DTRC MODEL NOS. 5470 and 5471)", David Taylor Research Center,
  Bethesda MD 20084-5000, DTRC/SHD-1298-01, March 1989, AD-A210 642,
  Ship Hydromechanics Department, "Approved for public release".
  docs/papers/benchmark_test_cases/groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf
  TITLE PAGE read as a RENDERED IMAGE of PDF page 1 by this lane, 2026-09-12.
  That PDF IS A PURE IMAGE SCAN; its .txt sidecar is Internet Archive OCR and
  is a reading aid only.  EVERY NUMBER BELOW WAS READ FROM A RENDERED PAGE,
  never from the sidecar.

  HULL  -- Table 1, report pages 4-5.   Inherited unchanged (see below).
  SAIL  -- Table 2, report pages 7-8.   Inherited unchanged (see below).
  STERN APPENDAGES:
    * Narrative, report page 6 (PDF page 13), read as an image:
        "The stern appendages consist of four identical appendages mounted on
         the model hull at angles of 0 degrees (top dead center), 90 degrees,
         180 degrees, and 270 degrees."
    * Table 3, "Equations to define stern appendages", REPORT PAGE 14
      (PDF page 21), read as an image.  Its own header:
        "These equations define the upper rudder stern appendage.  The three
         remaining stern appendages are located on the hull at 90 deg
         azimuthal increments."
        z(xi)/c(y) = 0.29690 sqrt(xi) - 0.12600 xi - 0.35160 xi^2
                                      + 0.28520 xi^3 - 0.10450 xi^4
        for 0 <= xi = (x - h)/c(y) + 1.0 <= 1
        h = x coordinate of the stern appendage trailing edge
        c(y) = -0.466308 y + 0.88859 = chord length
        Three values of h:  12.729617 / 13.146284 = BASELINE / 13.562950
        HULL/STERN APPENDAGE INTERSECTION: [R_HA(xi)]^2 = y^2 + [z(xi)]^2
    * Appendix C, "Listing of computer code to generate stern appendages"
      (DARPA2STERNAPP.FOR), report pages 62-65 (PDF pages 69-72), read as
      images.  It repeats every coefficient above IDENTICALLY and supplies the
      TIP, which Table 3 does not state:
        DELR = 0.05 ; DO 850 I=1,NP ; RR = RBSMAX + I*DELR
        IF(RR.GT.RMAX) RR = RMAX            with  PARAMETER RMAX = 0.833333
      i.e. THE APPENDAGE TIP LIES ON THE HULL'S OWN MAXIMUM-RADIUS CYLINDER,
      R = 0.833333 ft = 5/6 ft.  The appendages do not protrude beyond the
      parallel-middle-body diameter.

  A DISCREPANCY IN THE SOURCE, RECORDED AND NOT SILENTLY RESOLVED.
    Groves report page 12 (PDF page 19) prints the FORWARD appendage trailing
    edge as "x=12.729167 Ft (3.880 m)".  Table 3 (report page 14), Figure 5
    (report page 11) and Appendix C (report page 62) all print 12.729617.
    TWO of the three digits-bearing sources agree on 12.729617 and the outlier
    is the running text.  THIS BUILD USES THE BASELINE h = 13.146284, on which
    all four sources agree, so the discrepancy does not touch it.

  THREE INDEPENDENT SELF-CHECKS ON THE DIGITS, ASSERTED AT RUN TIME BELOW.
  Each would be broken by a single transposed digit read off a scanned page:
    (1) 0.29690 - 0.12600 - 0.35160 + 0.28520 - 0.10450 == 0 exactly
        -> the section closes at the trailing edge (closed-TE NACA 4-digit form).
    (2) c(y = RMAX = 0.833333) == 0.500000 ft exactly
        -> the tip chord is exactly half a foot, so BOTH chord coefficients and
           RMAX are mutually consistent.
    (3) max(z/c) == 0.10003 at xi == 0.2997
        -> a 20 %-thick section with maximum thickness at 30 % chord: the
           NACA 0020 thickness family.

=============================================================================
THE HULL AND THE SAIL ARE NOT REBUILT HERE -- THEY ARE IMPORTED.
=============================================================================
build_hull_stl() and build_sail_stl() are imported from the already-validated
cases/navier_class/SUBOFF_A1/build_suboff_a1_geometry.py and called with the
SAME defaults, so hull.stl and sail.stl come out BYTE-IDENTICAL to that build.
--assert-identical-to <dir> hashes them against a reference build and REFUSES
on any difference.  This is the cheapest possible regression test and it is
what lets the appended body inherit the hull's existing verification.

REGISTERED DEPARTURES FROM THE REFERENCE GEOMETRY (three, all printed and
written to the manifest, none discovered after the fact):
  D1  FIN TRAILING EDGE TRUNCATION.  z(xi=1) = 0 exactly in the reference, so
      the section closes to a MATHEMATICAL CUSP.  Truncated at --te-trunc-frac
      of chord; base thickness reported in mm and as % of chord.  Same
      departure, same mechanism and the same default as the sail's.
  D2  FLAT FIN TIP.  Groves stops the appendage at R = RMAX and states NO tip
      shape.  A PLANAR cap normal to the span is applied at R = 0.833333 ft.
  D3  BURIED FIN ROOT.  The fin solid is extended inward to R = --root-inner-ft
      (default 0.10 ft, which is Groves' own Appendix C starting radius) so
      that snappyHexMesh unions it with the hull.  The true root is the
      hull/appendage intersection curve of Table 3, which is COMPUTED and
      REPORTED but is not used to cut the STL.

UNITS.  Source equations are in FEET, model scale.  Everything is emitted in
METRES (x 0.3048), matching the hull and sail builders.

ZERO `assert` (L-332).  Refusals are raise / sys.exit(2).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)

import os, math, json, argparse, hashlib
import numpy as np

_A1_DIR = "/home/ubuntu/Certonomous/cases/navier_class/SUBOFF_A1"
if _A1_DIR not in sys.path:
    sys.path.insert(0, _A1_DIR)
import build_suboff_a1_geometry as A1          # noqa: E402

FT2M = A1.FT2M
RMAX_FT = A1.RMAX_FT                            # 5/6 ft, the hull max radius

# ---------------- TABLE 3 : STERN APPENDAGES (feet) ----------------------------
# Read from the RENDERED PDF page 21 (report page 14) and cross-read against the
# RENDERED Appendix C listing, PDF pages 69-72 (report pages 62-65), 2026-09-12.
SP_COEF = (0.29690, -0.12600, -0.35160, 0.28520, -0.10450)
SP_CHORD_SLOPE = -0.466308      # c(y) = SP_CHORD_SLOPE * y + SP_CHORD_INTERCEPT
SP_CHORD_INTERCEPT = 0.88859
SP_H_FORWARD_FT = 12.729617     # Table 3 / Figure 5 / Appendix C (text p.12: 12.729167)
SP_H_BASELINE_FT = 13.146284    # "= BASELINE" in Table 3, Figure 5 and Appendix C
SP_H_AFT_FT = 13.562950
SP_TIP_R_FT = RMAX_FT           # Appendix C: IF(RR.GT.RMAX) RR = RMAX, RMAX = 0.833333
SP_AZIMUTHS_DEG = (0.0, 90.0, 180.0, 270.0)     # report page 6, read as an image
SP_NAMES = {0.0: "fin000_upper_rudder",         # Table 3 header: "the upper rudder"
            90.0: "fin090_horizontal",
            180.0: "fin180_lower_rudder",
            270.0: "fin270_horizontal"}


def sp_chord_ft(y_ft):
    """Chord length c(y) in ft at spanwise radius y (ft).  TABLE 3 exactly."""
    return SP_CHORD_SLOPE * y_ft + SP_CHORD_INTERCEPT


def sp_halfthk_ft(xi, y_ft):
    """Section HALF-thickness z (ft) at chord fraction xi and radius y (ft).
    TABLE 3 exactly.  xi = 0 is the LEADING edge, xi = 1 the TRAILING edge."""
    if xi < 0.0 or xi > 1.0:
        return 0.0
    a0, a1, a2, a3, a4 = SP_COEF
    t = (a0 * math.sqrt(xi) + a1 * xi + a2 * xi * xi + a3 * xi ** 3 + a4 * xi ** 4)
    return sp_chord_ft(y_ft) * t


def sp_x_ft(xi, y_ft, h_ft):
    """Axial station of chord fraction xi at radius y.  xi = (x-h)/c(y) + 1."""
    return (xi - 1.0) * sp_chord_ft(y_ft) + h_ft


def sp_root_radius_ft(x_ft, h_ft, tol=1e-12):
    """The hull/appendage intersection of TABLE 3: the radius y at which
    [R_HA]^2 = y^2 + [z(xi)]^2 at this axial station.  Returns None where the
    appendage does not reach the hull surface at this x.  Bisection on y."""
    def f(y):
        c = sp_chord_ft(y)
        if c <= 0.0:
            return None
        xi = (x_ft - h_ft) / c + 1.0
        if xi < 0.0 or xi > 1.0:
            return None
        z = sp_halfthk_ft(xi, y)
        return math.hypot(y, z) - A1.hull_R_ft(x_ft)
    lo, hi = 0.02, SP_TIP_R_FT
    flo, fhi = f(lo), f(hi)
    if flo is None or fhi is None or flo * fhi > 0.0:
        return None
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if fm is None:
            return None
        if flo * fm <= 0.0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# ---------------- fin STL --------------------------------------------------------
def _cos_cluster(n):
    """n points on [0,1] clustered at BOTH ends (leading and trailing edge)."""
    t = np.linspace(0.0, math.pi, n)
    return (1.0 - np.cos(t)) / 2.0


def build_fin_stl(path, name, azimuth_deg, h_ft, n_chord, n_span,
                  te_trunc_frac, root_inner_ft):
    """One CLOSED stern-appendage solid at the given azimuth.

    Frame: hull axis is x.  theta = 0 is TOP DEAD CENTRE (+y), matching the
    hull builder's  y = R cos(theta),  z = R sin(theta)  and the sail, which
    sits at theta = 0.  For azimuth A the fin spans along
        s_hat = (0, cos A, sin A)
    and its thickness is along
        t_hat = (0, -sin A, cos A).
    """
    a = math.radians(azimuth_deg)
    s_hat = np.array([0.0, math.cos(a), math.sin(a)])
    t_hat = np.array([0.0, -math.sin(a), math.cos(a)])

    xis = _cos_cluster(n_chord) * te_trunc_frac          # 0 .. te_trunc_frac
    ys = np.linspace(root_inner_ft, SP_TIP_R_FT, n_span)  # ft, radius from axis

    def V(xi, y, sgn):
        x = sp_x_ft(xi, y, h_ft)
        z = sgn * sp_halfthk_ft(xi, y, )
        return (x * FT2M) * np.array([1.0, 0.0, 0.0]) \
            + (y * FT2M) * s_hat + (z * FT2M) * t_hat

    tris = []
    # --- the two section faces --------------------------------------------------
    for i in range(len(xis) - 1):
        for j in range(len(ys) - 1):
            for sgn in (+1.0, -1.0):
                p00 = V(xis[i],     ys[j],     sgn)
                p10 = V(xis[i + 1], ys[j],     sgn)
                p11 = V(xis[i + 1], ys[j + 1], sgn)
                p01 = V(xis[i],     ys[j + 1], sgn)
                if sgn > 0:
                    tris.append((p00, p10, p11)); tris.append((p00, p11, p01))
                else:
                    tris.append((p00, p11, p10)); tris.append((p00, p01, p11))
    # --- flat TIP cap at y = SP_TIP_R_FT  (registered departure D2) -------------
    # At the LEADING edge z(xi=0) = 0 exactly, so the two chordwise-first cap
    # vertices COINCIDE and one of the two triangles of that quad is a null.
    # It is not emitted: emitting it and letting write_stl() drop it would leave
    # the cap's edge bookkeeping short of its LE apex and the closure check would
    # (correctly) call the solid open.
    yt = ys[-1]
    for i in range(len(xis) - 1):
        pa = V(xis[i],     yt, -1.0); pb = V(xis[i],     yt, +1.0)
        pc = V(xis[i + 1], yt, +1.0); pd = V(xis[i + 1], yt, -1.0)
        if not np.array_equal(pa, pb):
            tris.append((pa, pb, pc))
        tris.append((pa, pc, pd))
    # --- flat ROOT lid, BURIED INSIDE THE HULL (registered departure D3) --------
    yr = ys[0]
    for i in range(len(xis) - 1):
        pa = V(xis[i],     yr, -1.0); pb = V(xis[i],     yr, +1.0)
        pc = V(xis[i + 1], yr, +1.0); pd = V(xis[i + 1], yr, -1.0)
        if not np.array_equal(pa, pb):
            tris.append((pa, pc, pb))
        tris.append((pa, pd, pc))
    # --- TRAILING-EDGE base, the truncation (registered departure D1) -----------
    xe = xis[-1]
    for j in range(len(ys) - 1):
        pa = V(xe, ys[j],     -1.0); pb = V(xe, ys[j],     +1.0)
        pc = V(xe, ys[j + 1], +1.0); pd = V(xe, ys[j + 1], -1.0)
        tris.append((pa, pc, pb)); tris.append((pa, pd, pc))
    # The LEADING edge closes on itself: z(xi=0) = 0 exactly, so the two section
    # faces already share those vertices.  Same treatment as the sail's LE.
    A1.write_stl(path, name, tris)
    return len(tris)


# ---------------- closure and hashing -------------------------------------------
def stl_tris(path):
    v = []
    with open(path) as f:
        for line in f:
            if line.lstrip().startswith("vertex "):
                v.append([float(q) for q in line.split()[1:4]])
    v = np.asarray(v)
    if len(v) % 3 != 0:
        raise RuntimeError(f"{path}: vertex count {len(v)} not a multiple of 3")
    return v.reshape(-1, 3, 3)


def closure_report(path):
    """Signed volume by the divergence theorem, plus an edge-manifold count.
    A closed, consistently oriented surface has every directed edge appearing
    exactly once and its mirror exactly once."""
    T = stl_tris(path)
    vol = float(np.einsum('ij,ij->i',
                          T[:, 0, :], np.cross(T[:, 1, :] - T[:, 0, :],
                                               T[:, 2, :] - T[:, 0, :])).sum() / 6.0)
    q = 1e-9
    key = lambda p: (round(p[0] / q), round(p[1] / q), round(p[2] / q))
    seen = {}
    for tri in T:
        k = [key(p) for p in tri]
        for m in range(3):
            e = (k[m], k[(m + 1) % 3])
            seen[e] = seen.get(e, 0) + 1
    bad = 0
    for (u, w), n in seen.items():
        if n != 1 or seen.get((w, u), 0) != 1:
            bad += 1
    return {"n_tris": int(len(T)), "signed_volume_m3": vol,
            "non_manifold_directed_edges": int(bad)}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


# ---------------- main ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-axial", type=int, default=600)
    ap.add_argument("--n-theta", type=int, default=180)
    ap.add_argument("--n-chord", type=int, default=240)
    ap.add_argument("--n-span", type=int, default=120)
    ap.add_argument("--te-trunc-frac", type=float, default=0.995)
    ap.add_argument("--fin-n-chord", type=int, default=161)
    ap.add_argument("--fin-n-span", type=int, default=61)
    ap.add_argument("--fin-te-trunc-frac", type=float, default=0.995)
    ap.add_argument("--root-inner-ft", type=float, default=0.10)
    ap.add_argument("--h-ft", type=float, default=SP_H_BASELINE_FT)
    ap.add_argument("--assert-identical-to", default=None,
                    help="directory holding a reference hull.stl and sail.stl; "
                         "REFUSE unless ours hash identically")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # ---- REFUSALS ON THE SOURCE DIGITS (the three self-checks) -----------------
    csum = sum(SP_COEF)
    if abs(csum) > 1e-12:
        sys.stderr.write(f"REFUSED: stern-appendage coefficients sum to {csum!r}, "
                         "not 0, so the section does not close at the trailing "
                         "edge.  Re-read Groves Table 3 (report page 14) as an "
                         "IMAGE before building.\n"); sys.exit(2)
    c_tip = sp_chord_ft(SP_TIP_R_FT)
    if abs(c_tip - 0.5) > 1e-6:
        sys.stderr.write(f"REFUSED: chord at the tip radius is {c_tip!r} ft, not "
                         "0.500000 ft.  The chord coefficients and RMAX are "
                         "mutually inconsistent; re-read Table 3 and Appendix C.\n")
        sys.exit(2)
    xi_s = np.linspace(1e-12, 1.0, 200001)
    a0, a1, a2, a3, a4 = SP_COEF
    tt = a0 * np.sqrt(xi_s) + a1 * xi_s + a2 * xi_s ** 2 + a3 * xi_s ** 3 + a4 * xi_s ** 4
    t_max, xi_tmax = float(tt.max()), float(xi_s[int(tt.argmax())])
    if not (0.0999 <= t_max <= 0.1001 and 0.295 <= xi_tmax <= 0.305):
        sys.stderr.write(f"REFUSED: max z/c = {t_max!r} at xi = {xi_tmax!r}; the "
                         "section is not the 20 %-thick, 30 %-chord NACA-0020 "
                         "form the coefficients should give.\n"); sys.exit(2)
    z_te = sp_halfthk_ft(1.0, 0.5)
    if abs(z_te) > 1e-12:
        sys.stderr.write(f"REFUSED: fin TE half-thickness is {z_te!r}, not 0; the "
                         "cusp premise of departure D1 is false.\n"); sys.exit(2)
    if not (0.90 <= a.fin_te_trunc_frac < 1.0):
        sys.stderr.write("REFUSED: --fin-te-trunc-frac outside [0.90, 1.0).\n")
        sys.exit(2)
    if a.h_ft not in (SP_H_FORWARD_FT, SP_H_BASELINE_FT, SP_H_AFT_FT):
        sys.stderr.write(f"REFUSED: h = {a.h_ft!r} is not one of Groves' three "
                         "published axial positions.\n"); sys.exit(2)

    # ---- the buried root must actually be buried -------------------------------
    x_le_inner = sp_x_ft(0.0, a.root_inner_ft, a.h_ft)
    for xi in np.linspace(0.0, a.fin_te_trunc_frac, 401):
        x = sp_x_ft(xi, a.root_inner_ft, a.h_ft)
        r_pt = math.hypot(a.root_inner_ft, sp_halfthk_ft(xi, a.root_inner_ft))
        if r_pt >= A1.hull_R_ft(x) - 1e-4:
            sys.stderr.write(f"REFUSED: the buried fin root at R = "
                             f"{a.root_inner_ft} ft reaches radius {r_pt:.6f} ft "
                             f"at x = {x:.6f} ft where the hull radius is only "
                             f"{A1.hull_R_ft(x):.6f} ft.  Departure D3's premise "
                             "(the root lid is inside the hull) is false.\n")
            sys.exit(2)

    # ---- hull and sail, IMPORTED and unchanged ---------------------------------
    nh, xs, R = A1.build_hull_stl(os.path.join(a.out, "hull.stl"),
                                  a.n_axial, a.n_theta)
    ns, sail_x_te, sail_z_base = A1.build_sail_stl(
        os.path.join(a.out, "sail.stl"), a.n_chord, a.n_span, a.te_trunc_frac)

    if a.assert_identical_to:
        for f in ("hull.stl", "sail.stl"):
            ours = sha256(os.path.join(a.out, f))
            ref_p = os.path.join(a.assert_identical_to, f)
            if not os.path.exists(ref_p):
                sys.stderr.write(f"REFUSED: reference {ref_p} does not exist, so "
                                 "the byte-identity regression cannot be run and "
                                 "must not be reported as passed.\n"); sys.exit(2)
            ref = sha256(ref_p)
            if ours != ref:
                sys.stderr.write(f"REFUSED: {f} is NOT byte-identical to the "
                                 f"reference build.\n  ours {ours}\n  ref  {ref}\n"
                                 "The appended body may not inherit the hull's "
                                 "verification.\n"); sys.exit(2)
            print(f"  BYTE-IDENTICAL to reference: {f}  sha256 {ours[:16]}...")

    # ---- the four fins ----------------------------------------------------------
    fins = {}
    for az in SP_AZIMUTHS_DEG:
        nm = SP_NAMES[az]
        p = os.path.join(a.out, nm + ".stl")
        nt = build_fin_stl(p, nm, az, a.h_ft, a.fin_n_chord, a.fin_n_span,
                           a.fin_te_trunc_frac, a.root_inner_ft)
        rep = closure_report(p)
        if rep["non_manifold_directed_edges"] != 0:
            sys.stderr.write(f"REFUSED: {nm}.stl has "
                             f"{rep['non_manifold_directed_edges']} non-manifold "
                             "directed edges; it is not a closed solid.\n")
            sys.exit(2)
        if rep["signed_volume_m3"] <= 0.0:
            sys.stderr.write(f"REFUSED: {nm}.stl signed volume is "
                             f"{rep['signed_volume_m3']!r} <= 0; normals point "
                             "inward.\n"); sys.exit(2)
        fins[nm] = {"azimuth_deg": az, "sha256": sha256(p), **rep}

    # ---- MEASURED geometry, for corroboration against the source ---------------
    y_root_te = sp_root_radius_ft(a.h_ft, a.h_ft)
    xs_root = np.linspace(sp_x_ft(0.0, SP_TIP_R_FT, a.h_ft) - 0.30, a.h_ft, 4001)
    root_curve = [(float(x), sp_root_radius_ft(float(x), a.h_ft)) for x in xs_root]
    root_curve = [(x, y) for x, y in root_curve if y is not None]
    x_root_le = min(x for x, _ in root_curve)
    y_root_max = max(y for _, y in root_curve)
    c_root = sp_chord_ft(y_root_te)
    span_exposed = SP_TIP_R_FT - y_root_te
    # exposed planform area of ONE fin, trapezoid between y_root_te and the tip
    S_one = 0.5 * (c_root + c_tip) * span_exposed

    man = {
        "configuration_named_by_geometry":
            "DARPA SUBOFF axisymmetric hull WITH bridge fairwater (sail) at top "
            "dead centre AND four identical stern appendages at the BASELINE "
            "axial position; NO ring wing, NO ring-wing support struts",
        "configuration_labels_as_printed_in_each_report": {
            "roddy_1990_DTRC_SHD_1298_08_table3_p17_p18":
                "NOT this body.  Roddy's 'FULLY APPENDED' (Configurations 1 and "
                "2) is 'FULLY APPENDED WITH RING WING NO. 1'.",
            "liu_huang_1998_CRDKNSWC_HD_1298_11_p6_towing_tank_list":
                "'Config. 8  Hull with sail and four stern appendages' -- THIS BODY",
            "liu_huang_1998_table14_p23_config_no_column":
                "'8  Fully Appended' -- THIS BODY",
            "WARNING":
                "Roddy Config 1 = fully appended; Liu and Huang Config 1 = bare "
                "hull.  Never cite a configuration by a bare number.",
        },
        "source": "Groves, Huang, Chang 1989, DTRC/SHD-1298-01 (AD-A210 642)",
        "source_pdf": "docs/papers/benchmark_test_cases/"
                      "groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf",
        "title_page_verified_by": "RENDERED IMAGE of PDF page 1, cfd lab-lane 2026-09-12",
        "stern_appendage_source_pages_report": {
            "narrative_four_at_0_90_180_270": 6,
            "table_3_equations": 14,
            "figure_5_axial_positions": 11,
            "figure_6_section_profile": 13,
            "appendix_C_fortran_listing": "62-65",
        },
        "units_emitted": "metres (source is feet, x0.3048)",
        "hull": {"n_tris": nh, "sha256": sha256(os.path.join(a.out, "hull.stl")),
                 "L_ft": A1.L_TOTAL_FT, "L_m": A1.L_TOTAL_FT * FT2M,
                 "Rmax_ft": RMAX_FT, "Dmax_m": 2 * RMAX_FT * FT2M},
        "sail": {"n_tris": ns, "sha256": sha256(os.path.join(a.out, "sail.stl")),
                 "LE_ft": A1.SAIL_LE, "TE_ft_reference": A1.SAIL_TE},
        "stern_appendages": {
            "count": 4, "azimuths_deg": list(SP_AZIMUTHS_DEG),
            "h_trailing_edge_ft": a.h_ft,
            "h_trailing_edge_m": a.h_ft * FT2M,
            "h_label_in_source": ("BASELINE" if a.h_ft == SP_H_BASELINE_FT
                                  else "non-baseline"),
            "chord_coefficients": {"slope": SP_CHORD_SLOPE,
                                   "intercept": SP_CHORD_INTERCEPT},
            "section_coefficients": list(SP_COEF),
            "self_check_coefficient_sum": csum,
            "self_check_tip_chord_ft": c_tip,
            "self_check_max_t_over_c_full": 2.0 * t_max,
            "self_check_xi_at_max_thickness": xi_tmax,
            "tip_radius_ft": SP_TIP_R_FT, "tip_radius_m": SP_TIP_R_FT * FT2M,
            "tip_chord_ft": c_tip, "tip_chord_m": c_tip * FT2M,
            "root_radius_at_TE_ft": y_root_te,
            "root_radius_at_TE_m": None if y_root_te is None else y_root_te * FT2M,
            "root_chord_at_TE_station_ft": c_root,
            "root_chord_at_TE_station_m": c_root * FT2M,
            "exposed_span_ft": span_exposed, "exposed_span_m": span_exposed * FT2M,
            "exposed_planform_area_one_fin_ft2": S_one,
            "exposed_planform_area_one_fin_m2": S_one * FT2M * FT2M,
            "exposed_aspect_ratio_one_fin": span_exposed ** 2 / S_one,
            "taper_ratio_tip_over_root": c_tip / c_root,
            "x_LE_at_tip_ft": sp_x_ft(0.0, SP_TIP_R_FT, a.h_ft),
            "x_LE_at_tip_m": sp_x_ft(0.0, SP_TIP_R_FT, a.h_ft) * FT2M,
            "x_LE_of_root_intersection_ft": x_root_le,
            "max_root_intersection_radius_ft": y_root_max,
            "stls": fins,
        },
        "REGISTERED_DEPARTURES": {
            "D1_fin_TE_truncation": {
                "reference_TE_half_thickness_ft": z_te,
                "reference_TE_closes_to": "a MATHEMATICAL CUSP (exactly zero)",
                "truncation_fraction_of_chord": a.fin_te_trunc_frac,
                "base_FULL_thickness_at_tip_mm":
                    2.0 * sp_halfthk_ft(a.fin_te_trunc_frac, SP_TIP_R_FT) * FT2M * 1000.0,
                "base_FULL_thickness_at_root_mm":
                    2.0 * sp_halfthk_ft(a.fin_te_trunc_frac, y_root_te) * FT2M * 1000.0,
                "base_over_chord_percent_at_tip":
                    100.0 * 2.0 * sp_halfthk_ft(a.fin_te_trunc_frac, SP_TIP_R_FT) / c_tip,
            },
            "D2_flat_fin_tip": {
                "source_states_no_tip_shape": True,
                "applied": "planar cap normal to the span at R = 0.833333 ft",
            },
            "D3_buried_fin_root": {
                "root_inner_ft": a.root_inner_ft,
                "rationale": "snappyHexMesh unions the fin with the hull; the "
                             "true root is the Table 3 intersection curve, which "
                             "is reported above but is not used to cut the STL",
                "verified_inside_hull": True,
            },
            "D4_sail_TE_truncation_inherited": {
                "truncation_fraction_of_chord": a.te_trunc_frac,
                "base_half_thickness_ft": sail_z_base,
                "note": "inherited unchanged from the SUBOFF_A1 sail builder",
            },
        },
    }
    with open(os.path.join(a.out, "geometry_manifest.json"), "w") as f:
        json.dump(man, f, indent=2)

    sp = man["stern_appendages"]
    print(f"hull.stl {nh} tris   sail.stl {ns} tris   "
          f"4 fins {sum(v['n_tris'] for v in fins.values())} tris total")
    print(f"  fin tip   R = {SP_TIP_R_FT:.6f} ft = {SP_TIP_R_FT*FT2M:.6f} m, "
          f"chord {c_tip:.6f} ft = {c_tip*FT2M:.6f} m")
    print(f"  fin root  R = {y_root_te:.6f} ft = {y_root_te*FT2M:.6f} m (at the TE "
          f"station x = {a.h_ft:.6f} ft), chord {c_root:.6f} ft")
    print(f"  exposed span {span_exposed:.6f} ft = {span_exposed*FT2M:.6f} m, "
          f"AR {sp['exposed_aspect_ratio_one_fin']:.4f}, "
          f"taper {sp['taper_ratio_tip_over_root']:.4f}")
    print(f"  SELF-CHECKS  coef sum {csum:.3e} | tip chord {c_tip:.6f} ft | "
          f"t/c {2*t_max:.5f} at xi {xi_tmax:.4f}")


if __name__ == "__main__":
    main()
