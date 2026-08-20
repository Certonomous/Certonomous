#!/usr/bin/env python3
"""
Build the constant-Ts Reynolds-sweep ladders registered in
DIAGNOSTIC_PREDICTION.md ("NEXT TEST, REGISTERED BEFORE IT IS BUILT,
2026-08-20"): D_Ts_Re25 / D_Ts_Re50 / D_Ts_Re200, each with its own
three-level mesh ladder for an h -> 0 excess.

THE REGISTERED COUNT IS 12 CASES: the log-log fit runs over
Re = 25, 50, 100, 200 and each Re needs a three-level ladder (4 x 3 = 12).
The Re = 100 ladder is the EXISTING, ALREADY-SOLVED L_Ts_c / L_Ts_m / L_Ts_f
and is NOT rebuilt -- the same reuse pattern build_diag_ladder.py used when
D_Pe became the fine level of its own ladder.  This script therefore builds
the NINE new cases:

    D_Ts_Re25_c/m/f   D_Ts_Re50_c/m/f   D_Ts_Re200_c/m/f

Each case is a SINGLE-parameter change from the corresponding L_Ts_* level:
Re (and hence U = Re nu / D) is the only lever.  Pr stays 0.71, the wall is
fixedValue T = 310 K exactly as on the L_Ts_* arm, and the mesh is the same
UNIFORM simpleGrading (1 1 1) ladder -- 20x200, 32x320, 51x512.

The sampling station is NOT fixed at 40 D: it moves with Re under the
committed analyse_t1c.amended_station rule (geometric mean of 2 entry lengths
and the 10 % saturation bound).  The station is a property of the ANALYSIS,
not of the case, but it is recorded in CASE.txt for the record:

    Re =  25: x/D = 2.227   (window [1.775, 2.794])
    Re =  50: x/D = 4.454   (window [3.550, 5.588])
    Re = 200: x/D = 17.816  (window [14.200, 22.353])

All well inside the 50 D domain; the theoretical driving fraction at every
station is 0.160, above the 0.10 discard floor.

DIAGNOSTIC, NOT GRADED.  No band, cannot pass or fail, no T1c verdict moves.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t1c as B                                    # noqa: E402
from analyse_t1c import amended_station                  # noqa: E402  (read-only)

NU_TS = 3.6567934
RES = (25.0, 50.0, 200.0)


def main():
    made = []
    for Re in RES:
        for lvl in ("c", "m", "f"):
            nr, nx = B.LEVELS[lvl]
            name = f"D_Ts_Re{Re:.0f}_{lvl}"
            d = os.path.join(HERE, name)
            if os.path.isdir(d) and any(
                    n.isdigit() and n != "0" for n in os.listdir(d)):
                print(f"  {name}: has a solution on disk, NOT rebuilt")
                continue
            if os.path.exists(d):
                shutil.rmtree(d)
            for sub in ("0.orig", "constant", "system"):
                os.makedirs(os.path.join(d, sub))
            w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)

            # Re (and the U it implies) is the ONLY lever, applied by
            # temporarily setting the module globals the generators read, so
            # every other byte comes from the frozen builder.
            old_re, old_u = B.RE, B.U
            B.RE = Re
            B.U = Re * B.NU / B.D
            try:
                w("system/blockMeshDict", B.block_mesh(nr, nx))
                w("system/controlDict", B.control_dict())
                w("system/fvSchemes", B.fv_schemes())
                w("system/fvSolution", B.fv_solution())
                w("constant/transportProperties", B.transport())
                w("constant/turbulenceProperties", B.turbulence_properties())
                w("constant/g", B.gravity())
                w("0.orig/U", B.field_U())
                w("0.orig/p_rgh", B.field_p())
                w("0.orig/T", B.field_T("fixedTemperature"))
                w("0.orig/alphat", B.field_alphat())
                txt = B.case_txt(name, dict(level=lvl, nr=nr, nx=nx,
                                            wall="fixedTemperature"))
            finally:
                B.RE, B.U = old_re, old_u

            st, lo, hi = amended_station(Re, B.PR, NU_TS)
            pe = Re * B.PR
            txt += (f"diagnostic       yes -- constant-Ts Re sweep, NOT GRADED\n"
                    f"ladder_for       D_Ts_Re{Re:.0f} (Re = {Re:.0f}, "
                    f"Pe = {pe:.2f})\n"
                    f"changed_from     L_Ts_{lvl} (Re 100 -> {Re:.0f}; "
                    f"U scales with Re; nothing else)\n"
                    f"station_rule     analyse_t1c.amended_station "
                    f"(moves with Re; NOT 40 D)\n"
                    f"station_xD       {st:.4f}  (window [{lo:.4f}, {hi:.4f}])\n"
                    f"Peclet           {pe:.2f}\n")
            w("CASE.txt", txt)
            made.append((name, nr, nx, Re, pe, st))

    print(f"D_Ts sweep: {len(made)} cases built in {HERE}")
    print(f"  {'case':16s} {'mesh':>10s} {'cells':>7s} {'Re':>5s} "
          f"{'Pe':>7s} {'station x/D':>12s}")
    for n, nr, nx, Re, pe, st in made:
        print(f"  {n:16s} {nr:3d} x {nx:3d} {nr*nx:7d} {Re:5.0f} "
              f"{pe:7.2f} {st:12.3f}")
    print("\n  The Re = 100 ladder is the existing, solved L_Ts_c/m/f "
          "(station x/D = 8.908) -- not rebuilt.")
    print("  12 registered cases = these 9 + L_Ts_c/m/f.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
