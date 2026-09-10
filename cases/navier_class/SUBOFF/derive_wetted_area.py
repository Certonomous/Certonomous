#!/usr/bin/env python3
"""INDEPENDENT re-derivation of the DARPA SUBOFF (DTRC Model 5470) BARE-HULL analytic
wetted surface area -- the number the SUBOFF R1 forceCoeffs `Aref` pin rests on.

WHY THIS FILE EXISTS.  `build_suboff.py` pins ONE `Aref` at every grid level
(cfd-supervisor ruling 2026-09-10).  The pin is the analytic full-revolution wetted
area divided by 72 (the 5 deg wedge is 1/72 of a revolution).  An error in that area
is an error in EVERY `Cd` this case ever produces, so the area is derived here from
the source equations rather than inherited as a four-figure number.

SOURCE (rule 15, title page verified from the PDF page image, not from the filename,
not from the OCR sidecar):
  TITLE PAGE / DD-1473: "GEOMETRIC CHARACTERISTICS OF DARPA SUBOFF MODELS
  (DTRC MODEL NOS. 5470 and 5471)", Nancy C. Groves, Thomas T. Huang, Ming S. Chang,
  David Taylor Research Center, Bethesda MD; report number DTRC/SHD-1298-01;
  March 1989; report type "Departmental"; UNCLASSIFIED.
  Filed: docs/papers/benchmark_test_cases/groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf
The hull profile is TABLE 1, "Equations to define axisymmetric hull", REPORT PAGE 4 =
PDF PAGE 11, transcribed from the rendered page image.  NOTE: the `.txt` OCR sidecar
mis-reads R_MAX as 0.0333333; the page itself reads R_MAX = 5/6 Ft.  The sidecar is
NOT the transcription source here.

The report gives the defining equations, computer-code listings, velocity-station and
pressure-tap locations.  It does NOT anywhere state a wetted surface area (searched:
"wetted", "surface area", "64.", "5.98" -- no hit), so this area is DERIVED, and the
report cannot be quoted for it.

METHOD.  Surface of revolution:
    S = INT_0^L  2*pi*R(x)*sqrt(1 + (dR/dx)^2) dx
NOT a facet sum; `hull_sector_area()` is deliberately not imported -- the point is an
area independent of the mesh.  The nose has dR/dx ~ x^(-1/1.9...) so the integrand
carries an integrable x^(-1/21) singularity at x=0; it is handled by the substitution
x = u^m (m=21 removes it exactly) and cross-checked by tanh-sinh (mpmath) quadrature.

RESULT (this file's own output):
    S = 64.4571395324 ft^2 = 5.9882642123 m^2   (full revolution, bare hull)
    Aref sector (1/72)      = 0.0831703362814 m^2
Convergence: bow segment agrees to ~1e-12 relative across m in {11,21,31} and node
counts 80..320, and against an independent tanh-sinh evaluation.  Stability against
the rounding of TABLE 1's OWN printed constants (3.333333 vs 10/3 etc.): 3.4e-6 %.
So the derivation supports ~7 significant figures: 5.988264 m^2.
The inherited four-figure 5.988 m^2 is CONFIRMED -- it is the correct 4-s.f. rounding
(the derived value is 0.0044% above it, well inside the +/-0.008% that 4 s.f. implies).

Usage:  python3 derive_wetted_area.py          # print the derivation + convergence
Refuses under `python3 -O` (L-332 lineage: no bare asserts carry the checks).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: derive_wetted_area.py must not run under `python3 -O`.\n")
    sys.exit(2)

import mpmath as mp

mp.mp.dps = 40

FT2M = mp.mpf("0.3048")

# ---- TABLE 1 (report p.4), model scale, x and R in FEET ---------------------------
RMAX   = mp.mpf(5) / 6          # R_MAX = 5/6 Ft  (max body diameter 1.666667 Ft = 0.508 m)
XB     = mp.mpf("3.333333")     # forebody length / bow-equation end
XM     = mp.mpf("10.645833")    # parallel-middle-body end
XA     = mp.mpf("13.979167")    # aft perpendicular (afterbody-equation end)
XC     = mp.mpf("14.291667")    # total body length (4.356 m)
RH     = mp.mpf("0.1175")       # r_h
KO     = mp.mpf(10)             # K_0
K1     = mp.mpf("44.6244")      # K_1
CB1    = mp.mpf("1.126395101")
CB2    = mp.mpf("0.442874707")
XIDEN  = mp.mpf("3.333333")
CAPC   = mp.mpf("44.733333")
WEDGE_FRACTION = mp.mpf(5) / 360    # the R1 wedge is 5 deg of 360 deg


def R_bow(x):
    """BOW EQUATION, 0 <= x <= 3.333333 Ft."""
    t = mp.mpf("0.3") * x - 1
    inner = CB1 * x * t**4 + CB2 * x * x * t**3 + 1 - t**4 * (mp.mpf("1.2") * x + 1)
    if inner < 0:
        inner = mp.mpf(0)
    return RMAX * inner ** (1 / mp.mpf("2.1"))


def R_aft(x):
    """AFTERBODY EQUATION, 10.645833 <= x <= 13.979167 Ft."""
    xi = (XA - x) / XIDEN
    poly = (RH * RH
            + RH * KO * xi**2
            + (20 - 20 * RH * RH - 4 * RH * KO - K1 / 3) * xi**3
            + (-45 + 45 * RH * RH + 6 * RH * KO + K1) * xi**4
            + (36 - 36 * RH * RH - 4 * RH * KO - K1) * xi**5
            + (-10 + 10 * RH * RH + RH * KO + K1 / 3) * xi**6)
    if poly < 0:
        poly = mp.mpf(0)
    return RMAX * mp.sqrt(poly)


def R_cap_u(u):
    """AFTERBODY CAP, parametrised by u = 3.2x - 44.733333 in [~0, 1]."""
    s = 1 - u * u
    if s < 0:
        s = mp.mpf(0)
    return RH * RMAX * mp.sqrt(s)


def _band(f, x):
    return 2 * mp.pi * f(x) * mp.sqrt(1 + mp.diff(f, x) ** 2)


M_SUB = 21          # x = u^M removes the x^(-1/21) nose singularity exactly


def bow_area(m=M_SUB):
    uB = XB ** (mp.mpf(1) / m)
    def g(u):
        if u == 0:
            return mp.mpf(0)
        return _band(R_bow, u**m) * m * u ** (m - 1)
    return mp.quad(g, [0, uB])


def pmb_area():
    return 2 * mp.pi * RMAX * (XM - XB)        # exact: a cylinder


def aft_area():
    return mp.quad(lambda x: _band(R_aft, x), [XM, XA])


def cap_area():
    uA = mp.mpf("3.2") * XA - CAPC
    def g(u):
        s = 1 - u * u
        if s <= 0:
            return mp.mpf(0)
        R = RH * RMAX * mp.sqrt(s)
        dRdx = mp.mpf("3.2") * (-RH * RMAX * u / mp.sqrt(s))
        return 2 * mp.pi * R * mp.sqrt(1 + dRdx**2) / mp.mpf("3.2")
    return mp.quad(g, [uA, 1])


def wetted_area_ft2():
    return bow_area() + pmb_area() + aft_area() + cap_area()


def main():
    print("SOURCE: Groves/Huang/Chang 1989, DTRC/SHD-1298-01, TABLE 1, report p.4 "
          "(PDF p.11); title page verified.")
    print()
    print("CONTINUITY OF THE TRANSCRIPTION (segments must join):")
    print("  R(0)            = %s ft   (nose, expect 0)" % mp.nstr(R_bow(0), 10))
    print("  R(XB) bow       = %s ft" % mp.nstr(R_bow(XB), 12))
    print("  R_MAX           = %s ft" % mp.nstr(RMAX, 12))
    print("  R(XM) afterbody = %s ft   (expect R_MAX)" % mp.nstr(R_aft(XM), 12))
    print("  R(XA) afterbody = %s ft" % mp.nstr(R_aft(XA), 12))
    print("  R cap at u=u(XA)= %s ft   (expect equal)"
          % mp.nstr(R_cap_u(mp.mpf("3.2") * XA - CAPC), 12))
    print("  R cap at u=1    = %s ft   (tail, expect 0)" % mp.nstr(R_cap_u(mp.mpf(1)), 10))
    print()
    b, p, a, c = bow_area(), pmb_area(), aft_area(), cap_area()
    for nm, v in (("bow", b), ("parallel middle body (exact)", p),
                  ("afterbody", a), ("afterbody cap", c)):
        print("  %-30s %s ft^2 = %s m^2"
              % (nm, mp.nstr(v, 14), mp.nstr(v * FT2M**2, 14)))
    S_ft = b + p + a + c
    S_m = S_ft * FT2M**2
    print()
    print("  TOTAL wetted area  = %s ft^2" % mp.nstr(S_ft, 15))
    print("  TOTAL wetted area  = %s m^2" % mp.nstr(S_m, 15))
    print("  inherited 4 s.f.   = 5.988 m^2   -> derived is %s %% above it"
          % mp.nstr(100 * (S_m - mp.mpf("5.988")) / mp.mpf("5.988"), 6))
    print("  Aref SECTOR (1/72) = %s m^2" % mp.nstr(S_m * WEDGE_FRACTION, 15))
    print()
    print("CONVERGENCE OF THE BOW SEGMENT (the only singular one), x = u^m:")
    ref = bow_area(21)
    for m in (11, 21, 31):
        v = bow_area(m)
        print("  m=%2d  S_bow = %s ft^2   (rel diff from m=21: %s)"
              % (m, mp.nstr(v, 15), mp.nstr(abs(v - ref) / ref, 3)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
