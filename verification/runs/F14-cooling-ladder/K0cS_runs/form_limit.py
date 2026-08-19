#!/usr/bin/env python3
"""
Can a gradient-diffusion thermal closure represent Ampofo's measured profile?

A gradient-diffusion closure sets alpha_t = nu_t / Prt.  alpha_t is therefore
PROPORTIONAL to nu_t, with Prt setting only the constant of proportionality.
Wherever nu_t is zero the closure forces alpha_t to zero, for every finite Prt,
whether that Prt is constant or a field.

This asks the measurement whether that holds.  ZERO COMPUTE: the only inputs are
the digitised reference file and its stated reading uncertainty.  GRADES
NOTHING.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DAT = os.path.join(os.path.dirname(HERE), "..", "..", "..",
                   "docs", "campaigns", "F14-cooling-ladder",
                   "reference-data", "ampofo_fig11", "ampofo_fig11_digitised.dat")
DAT = os.path.abspath(DAT)
U_LEFT = 0.15      # reading uncertainty on alpha_t/nu and nu_t/nu, D417
PRT_MIN_MEASURED = 0.21   # smallest Prt Ampofo's figure shows, at the wall


def main():
    if not os.path.isfile(DAT):
        print(f"REFUSE: digitised reference not found at {DAT}")
        return 2
    rows = []
    for line in open(DAT):
        if line.startswith("#") or not line.strip():
            continue
        f = line.split()
        if f[1] == "NA" or f[2] == "NA":
            continue
        rows.append((float(f[0]), float(f[1]), float(f[2]), f[3]))

    print("CAN alpha_t = nu_t / Prt REPRODUCE THE MEASURED PROFILE?")
    print("Ampofo Fig. 11, digitised (D417).  Reading uncertainty +/- %.2f on both." % U_LEFT)
    print("=" * 96)
    print("  %-9s %11s %11s | %s" % ("X = x/L", "alphat/nu", "nut/nu",
                                     "Prt required to reproduce alphat from nut"))
    impossible = []
    for X, at, nt, prt in rows:
        # Prt = nu_t / alpha_t.  Ask instead: what alpha_t does the CLOSURE give,
        # at the most generous Prt the experiment anywhere supports?
        best = abs(nt) / PRT_MIN_MEASURED          # |alpha_t/nu| the closure can reach
        nt_lo, nt_hi = abs(nt) - U_LEFT, abs(nt) + U_LEFT
        best_hi = max(0.0, nt_hi) / PRT_MIN_MEASURED   # most generous, uncertainty included
        need = (nt / at) if at not in (0.0,) else None
        s = f"{need:+.4f}" if need is not None else "undefined (alpha_t = 0)"
        flag = ""
        if at - U_LEFT > best_hi:
            flag = "  <-- CANNOT BE REACHED"
            impossible.append((X, at, nt, best_hi))
        print("  %-9.4f %11.2f %11.2f | Prt = %s%s" % (X, at, nt, s, flag))

    print("-" * 96)
    if not impossible:
        print("ZERO VERDICT: NOT_A_ZERO -- every measured point is reachable")
        return 0
    print("  Points the closure CANNOT reach at ANY Prt >= %.2f, uncertainty included:"
          % PRT_MIN_MEASURED)
    for X, at, nt, best_hi in impossible:
        print(f"    X = {X:.4f}: measured alpha_t/nu = {at:.2f} (>= {at - U_LEFT:.2f} "
              f"at the low end of its uncertainty),")
        print(f"                 but nu_t/nu = {nt:+.2f} (<= {abs(nt) + U_LEFT:.2f} at the high end),")
        print(f"                 so the closure can deliver at most {best_hi:.2f}.")
    print()
    print("  The gap is not closed by lowering Prt: alpha_t is PROPORTIONAL to nu_t,")
    print("  and nu_t is zero to within its own reading uncertainty at these points.")
    print("  A variable Prt does not help either, for the same reason.")
    print("VERDICT: the FORM is refuted by the measurement, not the value")
    return 0


if __name__ == "__main__":
    sys.exit(main())
