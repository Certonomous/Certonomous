#!/usr/bin/env python3
"""Predicted y+ on `blades` from OUR OWN registered first-layer height and OUR OWN flow
conditions -- no dependence on any published source's rotation rate.

METHOD IS NOT CHOSEN HERE.  It is the instrument already frozen in
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` section A4.2:

    Cf   = 0.058 * Re_c**-0.2          (flat-plate turbulent skin friction)
    Re_c = U * c(r) / nu               <- LOCAL chord, not c0.7 everywhere
    tau  = 0.5 * rho * Cf * U**2
    u_t  = sqrt(tau / rho)
    y+   = y_centre * u_t / nu

with nu = 1.124e-6 m2/s, rho = 998.99 kg/m3, n = 15 s-1, D = 0.250 m.

A4.2 does NOT print the chord it used at each station.  Running it with c0.7 everywhere
reproduces r/R 0.70 exactly and MISSES the other two -- so A4.2 used the LOCAL chord.  The
local chords are recovered from A4.2's own printed U and Re_c as c = Re_c*nu/U:

    r/R 0.30 -> 0.07328 m      r/R 0.70 -> 0.10416 m      r/R 0.90 -> 0.08416 m

CONTROL ON THE RECOVERY: the recovered r/R 0.70 chord is 0.10416 m against the independently
known c0.7 = 0.10417 m (Report 3752 Table 1, Sanaa section B.2) -- a 1e-5 agreement the
recovery could not have produced by accident.  The recovered chords are USED, not assumed.

SELFTEST REPRODUCES A4.2's PUBLISHED TABLE EXACTLY -- that is the control that shows this
script is running the registered method and not a new one.  A4.2 at J = 0.7985, layerless,
first cell centre 0.3125 mm:  r/R 0.30 -> 62, r/R 0.70 -> 107, r/R 0.90 -> 134.

y_centre IS HALF THE FIRST LAYER.  A4.2's own layerless row proves the convention: a 0.625 mm
surface cell with no layer has its centre at 0.3125 mm, i.e. half the cell.  A first LAYER of
thickness t1 therefore puts the first cell CENTRE at t1/2.

NOTHING HERE IS REGISTERED.  This computes; the supervisor rules.
"""
import math

NU, RHO, N, D = 1.124e-6, 998.99, 15.0, 0.250
R_TIP = D / 2.0
CHORD = {0.30: 0.07328, 0.70: 0.10416, 0.90: 0.08416}   # recovered from A4.2; see docstring
LOCAL_CELL_BLADES = 6.25e-4          # 20 mm background / 2**5, make_snappy.py LEVELS['blades']

def u_tau(rOverR, J):
    V = 3.75 * J                                  # V = J n D = J * 15 * 0.25
    Ut = 2.0 * math.pi * N * (rOverR * R_TIP)     # tangential speed at this radius
    U = math.hypot(V, Ut)
    Re = U * CHORD[rOverR] / NU
    Cf = 0.058 * Re ** -0.2
    return U, Re, math.sqrt(0.5 * Cf * U * U)

def yplus(y_centre, rOverR, J):
    return y_centre * u_tau(rOverR, J)[2] / NU

def first_layer_for_yplus(target, rOverR, J):
    """first LAYER thickness (= 2 * first cell centre) giving `target` y+."""
    return 2.0 * target * NU / u_tau(rOverR, J)[2]

def stack(t1, ratio, n_layers):
    """total extruded stack in metres from the FIRST layer."""
    return t1 * (ratio ** n_layers - 1.0) / (ratio - 1.0)

def stack_from_final(t_final, ratio, n_layers):
    """MESH_STANDARD section 16.3 L2 form: S = t_f * sum_{i=0}^{N-1} r**-i."""
    return t_final * sum(ratio ** -i for i in range(n_layers))

def selftest():
    print("=== CONTROL: reproduce A4.2's frozen table (layerless, y_centre = 0.3125 mm, J = 0.7985)")
    print("    A4.2 published:  U 4.632 / 8.773 / 11.018 | u_t 0.2233 / 0.3831 / 0.4804 | y+ 62 / 107 / 134")
    ok = True
    for rr, eU, eu, ey in ((0.30, 4.632, 0.2233, 62), (0.70, 8.773, 0.3831, 107), (0.90, 11.018, 0.4804, 134)):
        U, Re, ut = u_tau(rr, 0.7985)
        yp = yplus(3.125e-4, rr, 0.7985)
        hit = abs(U - eU) < 0.01 and abs(ut - eu) < 0.001 and abs(yp - ey) <= 1.0
        ok &= hit
        print(f"    r/R {rr:.2f}: U {U:7.3f}  Re_c {Re:.3e}  u_t {ut:.4f}  y+ {yp:6.1f}   {'MATCH' if hit else 'MISMATCH'}")
    print(f"    CONTROL {'PASSES -- this script runs the registered method' if ok else 'FAILS -- DO NOT USE THESE NUMBERS'}\n")
    return ok

if __name__ == '__main__':
    if not selftest():
        raise SystemExit(2)

    T1_A2 = 3.125e-4 / 1.2 ** 5      # PRISM-A2: finalLayerThickness 3.125e-4, ratio 1.2, N=6
    print(f"=== (1) PRISM-A2 AS REGISTERED: finalLayerThickness 3.125e-4 m, ratio 1.2, 6 layers")
    print(f"    first layer t1 = 3.125e-4 / 1.2^5 = {T1_A2:.4e} m = {T1_A2*1e3:.4f} mm")
    print(f"    first cell CENTRE = t1/2 = {T1_A2/2*1e3:.4f} mm\n")
    print("    J        r/R 0.30   r/R 0.70   r/R 0.90")
    for J in (0.7985, 1.2021, 1.4594):
        row = [yplus(T1_A2 / 2, rr, J) for rr in (0.30, 0.70, 0.90)]
        print(f"    {J:.4f}   " + "   ".join(f"{v:8.1f}" for v in row))
    print("    registered window 30-60; amended 30-300 (smoke only)\n")

    print("=== (2) FIRST LAYER FOR y+ = 45 (mid-window), per station, per J")
    print("    J        r/R 0.30   r/R 0.70   r/R 0.90     [mm]")
    for J in (0.7985, 1.2021, 1.4594):
        row = [first_layer_for_yplus(45.0, rr, J) * 1e3 for rr in (0.30, 0.70, 0.90)]
        print(f"    {J:.4f}   " + "   ".join(f"{v:8.4f}" for v in row))
    t1_45 = first_layer_for_yplus(45.0, 0.70, 1.2021)
    print(f"\n    ANCHOR (r/R 0.70, design point J = 1.2021): t1 = {t1_45*1e3:.4f} mm\n")

    print("=== (3) IS THE PUBLISHED 0.5 mm CONSISTENT, ON OUR OWN ARITHMETIC?")
    print("    (Klerebrant's 0.5 mm first layer, evaluated at OUR n = 15 s-1 -- no reliance on their n)")
    print("    J        r/R 0.30   r/R 0.70   r/R 0.90")
    for J in (0.7985, 1.2021, 1.4594):
        row = [yplus(0.5e-3 / 2, rr, J) for rr in (0.30, 0.70, 0.90)]
        print(f"    {J:.4f}   " + "   ".join(f"{v:8.1f}" for v in row))
    print()

    print("=== (4) L2 ONE-LOCAL-CELL CHECK (MESH_STANDARD section 16.3); local cell = 0.625 mm")
    print(f"    {'case':34s} {'t1 [mm]':>9s} {'stack [mm]':>11s} {'S [cells]':>10s}  verdict")
    def line(name, t1, nl=6, ratio=1.2):
        st = stack(t1, ratio, nl)
        S = st / LOCAL_CELL_BLADES
        v = 'OK' if S <= 1.0 else ('ABOVE 1.0 -- expect collapse' if S > 1.0 else '')
        print(f"    {name:34s} {t1*1e3:9.4f} {st*1e3:11.4f} {S:10.3f}  {v}")
        return S
    S_a2 = line("PRISM-A2 as registered (6 lyr)", T1_A2)
    S_45 = line("y+=45 anchor (6 lyr)", t1_45)
    S_05 = line("published 0.5 mm (6 lyr)", 0.5e-3)
    # cross-check the L2 formula in its own published form for PRISM-A2
    print(f"\n    L2 formula cross-check, S = t_f*sum(r^-i): "
          f"{stack_from_final(3.125e-4,1.2,6)/LOCAL_CELL_BLADES:.3f} (vs {S_a2:.3f} from the first-layer form)")
    print(f"    reference: DrivAer S = 1.6808 COLLAPSED (2.50 of 5); DrivAerML S = 0.480 EXTRUDED\n")

    print("=== (5) HOW MANY LAYERS FIT UNDER ONE LOCAL CELL, at each candidate first layer")
    for name, t1 in (("PRISM-A2 t1 = 0.1256 mm", T1_A2),
                     (f"y+=45  t1 = {t1_45*1e3:.4f} mm", t1_45),
                     ("published 0.5 mm", 0.5e-3)):
        nmax = 0
        for nl in range(1, 13):
            if stack(t1, 1.2, nl) <= LOCAL_CELL_BLADES:
                nmax = nl
        print(f"    {name:30s} -> max layers at ratio 1.2 under one local cell: {nmax}")
    print("\n    (registered nSurfaceLayers = 6, expansionRatio = 1.2)")
