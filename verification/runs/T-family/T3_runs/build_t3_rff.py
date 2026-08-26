#!/usr/bin/env python3
"""T3 fourth mesh level R_ff -- built THROUGH the frozen build_t3.py, not beside it.

R_ff is level f refined by the family's ratio r = 1.6 in BOTH in-plane directions
(the mesh is 2D, one empty cell in z): every count x 1.6, rounded to the nearest
even integer where the two-sided grading needs it, and the wall y+ target
divided by 1.6 (1.6 / 1.0 / 0.625 / 0.390625) so the first wall cell follows the
family's rule 2*y+*nu/u_tau.  Every ratio is found by build_t3.cell_ratio's
bisection exactly as for R_c/R_m/R_f.  build_t3.py is imported and NOT edited;
its LEVELS dict receives an extra key at runtime only.

Departures from build_t3.build()'s output, applied here and disclosed:
  * system/controlDict  endTime 20000 -> END_TIME_RFF (registered), one line;
    every other line byte-identical to R_f's.
  * system/decomposeParDict  NEW FILE (R_f had none: the family ran serial).
    method simple, n (RANKS 1 1): deterministic, no seed, bit-reproducible from
    the rank count (F15 ruling 2 precedent).
  * CASE.txt  endTime / predicted_core_s lines restated; the frozen builder's
    lines are kept ABOVE, so the design values it wrote are unaltered.
Exit 2 = refusal.  No assert statements (python3 -O deletes them, L-332).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t3 as B

R = 1.6
END_TIME_RFF = 118000        # registered: 78 000 (R_f converged) x 1.5, rounded UP to the writeInterval
RANKS = 8
RATE = 6.50e4                # cell-it / core-s, T3_RESULTS S14.8 item 2

def refuse(m):
    print("REFUSE: " + m); sys.exit(2)

def even(x):
    n = int(round(x))
    return n if n % 2 == 0 else n + (1 if x > n else -1)

def main():
    f = B.LEVELS["f"]
    ff = dict(nx_up=int(round(f["nx_up"] * R)), nx_down=int(round(f["nx_down"] * R)),
              ny_low=even(f["ny_low"] * R), ny_up=even(f["ny_up"] * R),
              yplus=f["yplus"] / R)
    B.LEVELS["ff"] = ff
    if "--check" in sys.argv:
        dz, lv, fc, r = B.design("ff", 48.0, 30.0, False, False, (B.WM_NY_LOW, B.WM_NY_UP))
        if dz is None:
            refuse("first cell does not fit: %s" % r)
        print("R_ff design: counts %s  first wall cell %.6e m  nCells %d  (R_f 235520 x %.4f)"
              % (lv, fc, dz["nCells"], dz["nCells"] / 235520.0))
        print("ratios r: %s" % {k: round(v, 10) for k, v in dz["r"].items()})
        return 0
    m, why = B.build(HERE, "R_ff", "ff", "ladder (fourth level)", 48.0, 30.0,
                     B.PRT_DEFAULT, "resolved", False, "--force" in sys.argv,
                     (B.WM_NY_LOW, B.WM_NY_UP))
    if not m:
        refuse("; ".join(why))
    d = os.path.join(HERE, "R_ff")
    cd = os.path.join(d, "system", "controlDict")
    txt = open(cd).read()
    old = "endTime         %d;\n" % B.END_TIME
    if txt.count(old) != 1:
        refuse("controlDict endTime line not found exactly once")
    open(cd, "w").write(txt.replace(old, "endTime         %d;\n" % END_TIME_RFF))
    if ("endTime         %d;" % END_TIME_RFF) not in open(cd).read():
        refuse("controlDict endTime post-check failed")
    open(os.path.join(d, "system", "decomposeParDict"), "w").write(
        B.header("dictionary", "decomposeParDict", "system") +
        "numberOfSubdomains %d;\nmethod          simple;\ncoeffs\n{\n    n           (%d 1 1);\n}\n"
        % (RANKS, RANKS))
    pred_core_s = m["nCells"] * END_TIME_RFF / RATE
    with open(os.path.join(d, "CASE.txt"), "a") as fh:
        fh.write("# --- R_ff restatements (T3_R_FF_PREREGISTRATION.md); the builder's lines above are unaltered ---\n")
        fh.write("endTime_registered   %d  (78 000 x 1.5 = 117 000, rounded up to the 2 000 writeInterval)\n" % END_TIME_RFF)
        fh.write("ranks_registered     %d  (decomposeParDict simple n (%d 1 1))\n" % (RANKS, RANKS))
        fh.write("predicted_core_s_rff %.0f  (nCells x endTime / %.2e cell-it per core-s, T3_RESULTS S14.8)\n" % (pred_core_s, RATE))
        fh.write("refinement_vs_R_f    %.6f  (nCells ratio; r_eff = sqrt = %.4f, 2D)\n" % (m["nCells"] / 235520.0, (m["nCells"] / 235520.0) ** 0.5))
    print("R_ff built: nCells_design %d, endTime %d, ranks %d, POINT %.0f core-min"
          % (m["nCells"], END_TIME_RFF, RANKS, pred_core_s / 60.0))
    return 0

if __name__ == "__main__":
    sys.exit(main())
