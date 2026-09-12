#!/usr/bin/env python3
"""Order-of-magnitude sizing of the PPTC shaft-diameter question.

PURPOSE.  Sanaa's registered modelling choice (b) puts the dynamometer shaft at diameter
0.075 m; the first-party CAD she directed us to use carries a 0.040 m shaft behind a
tapering aft fairing (GEOMETRY_ADMISSION_RECORD.md section 4).  This script sizes the
DIFFERENCE between the two so the choice can be made knowing what it costs.

THIS IS AN ESTIMATE, ORDER OF MAGNITUDE, AND IT IS NOT A MEASUREMENT.  It replaces a
three-dimensional rotating boundary layer with a flat-plate friction line wrapped onto a
cylinder.  It is fit for answering "tenths of a percent, or several percent?" and for
nothing else.  No gate is decided by it and no number from it enters any certificate as a
result.

THE METHOD IS FIXED HERE, BEFORE THE ARITHMETIC IS RUN, so it cannot be tuned to give a
convenient answer:

  1. The shaft is a cylinder of radius r rotating at omega about its own axis with the
     freestream V along it.  Wetted length L is taken from the hub's aft face to the
     outlet, identical for both candidates, so only r differs.
  2. Local effective speed  u = sqrt(V^2 + (omega r)^2).
  3. Skin friction from the ITTC-1957 line on the shaft's own Reynolds number,
     Cf = 0.075 / (log10(Re_L) - 2)^2,  Re_L = u L / nu.
  4. Wall stress tau = 0.5 rho Cf u^2, resolved into
       tangential  tau_t = 0.5 rho Cf u (omega r)      -> torque
       axial       tau_x = 0.5 rho Cf u V              -> drag (opposes thrust)
  5. Torque   Q = tau_t * r * 2 pi r L = pi rho Cf u omega r^3 L     (scales as r^3)
     Drag     F = tau_x * 2 pi r L     = pi rho Cf u V r L           (scales as r^1)
  6. Both are expressed as a percentage of the MEASURED KT and 10KQ at the design point
     J = 1.2021 (0.2797 and 0.7676, Report 3752 page 2.11) and compared against the
     registered gate half-widths (7.55 % on KT, 8.10 % on 10KQ).

WHAT IT DELIBERATELY DOES NOT ESTIMATE: the base-pressure change behind the hub, and the
aft fairing that the CAD has and a bare cylinder does not -- which the smp'11 setup sheet
says exists "to avoid a pressure build-up".  That is a form effect, it is not accessible to
a friction line, and it is disclosed rather than guessed.  It acts on thrust, in the
direction of making the bare-cylinder case worse, so the thrust figure below is a LOWER
bound on the difference.
"""
import math

RHO = 998.99
NU = 1.124e-6
D = 0.250
N_RPS = 15.0
OMEGA = 2.0 * math.pi * N_RPS
J = 1.2021
V = J * N_RPS * D

KT_M, TENKQ_M = 0.2797, 0.7676
BAND_KT_PCT, BAND_KQ_PCT = 7.55, 8.10

# Hub aft face at x = -50 mm (measured, GEOMETRY_ADMISSION_RECORD.md section 3);
# outlet at 6D = -1500 mm from the propeller plane.
L = (1500.0 - 50.0) / 1000.0

CANDIDATES = [('CAD, measured', 0.040), ("registered choice (b)", 0.075)]


def cf_ittc(re_l: float) -> float:
    return 0.075 / (math.log10(re_l) - 2.0) ** 2


def shaft(r_out: float):
    r = r_out / 2.0
    u = math.hypot(V, OMEGA * r)
    re_l = u * L / NU
    cf = cf_ittc(re_l)
    q = math.pi * RHO * cf * u * OMEGA * r ** 3 * L
    f = math.pi * RHO * cf * u * V * r * L
    return dict(r=r, u=u, re=re_l, cf=cf, q=q, f=f,
                dkt=f / (RHO * N_RPS ** 2 * D ** 4),
                dkq10=10.0 * q / (RHO * N_RPS ** 2 * D ** 5))


def main() -> None:
    print('PPTC shaft sizing -- ESTIMATE, ORDER OF MAGNITUDE, NOT A MEASUREMENT')
    print(f'  J = {J}, V = {V:.4f} m/s, omega = {OMEGA:.4f} rad/s, '
          f'wetted length L = {L:.3f} m (identical for both candidates)')
    print(f'  measured at this J: KT = {KT_M}, 10KQ = {TENKQ_M}; '
          f'registered band half-widths KT +-{BAND_KT_PCT}%, 10KQ +-{BAND_KQ_PCT}%\n')
    res = []
    for name, dia in CANDIDATES:
        s = shaft(dia)
        res.append((name, dia, s))
        print(f'  {name:24s} diameter {dia:.3f} m')
        print(f'      wall speed {s["u"]:8.4f} m/s   Re_L {s["re"]:.3e}   Cf {s["cf"]:.5f}')
        print(f'      torque     {s["q"]:8.4f} N m  -> contributes {s["dkq10"]:.4f} to 10KQ '
              f'= {100*s["dkq10"]/TENKQ_M:6.2f}% of the measured value')
        print(f'      axial drag {s["f"]:8.4f} N    -> contributes {-s["dkt"]:.4f} to KT '
              f'= {100*s["dkt"]/KT_M:6.2f}% of the measured value (opposing thrust)\n')
    (_, d0, a), (_, d1, b) = res
    d_kq = b['dkq10'] - a['dkq10']
    d_kt = b['dkt'] - a['dkt']
    print('  DIFFERENCE, registered choice (b) minus CAD:')
    print(f'      10KQ  {d_kq:+.4f}  = {100*d_kq/TENKQ_M:+6.2f}% of measured  '
          f'-> {100*abs(d_kq)/TENKQ_M/BAND_KQ_PCT*100:5.1f}% of the gate half-width')
    print(f'      KT    {-d_kt:+.4f}  = {-100*d_kt/KT_M:+6.2f}% of measured  '
          f'-> {100*abs(d_kt)/KT_M/BAND_KT_PCT*100:5.1f}% of the gate half-width')
    print(f'      torque ratio (r^3 scaling): {b["q"]/a["q"]:.2f}x')
    print('\n  Not included, and it acts on thrust in the direction of making the bare')
    print('  0.075 m cylinder differ MORE: the aft fairing and the base pressure behind')
    print('  the hub. The KT figure above is therefore a LOWER bound on the difference.')


if __name__ == '__main__':
    main()
