#!/usr/bin/env python3
"""
Build the two T1c diagnostic cases registered in DIAGNOSTIC_PREDICTION.md.

Each is a SINGLE-parameter change from L_q_f, reusing build_t1c's own generators
so that everything not named below is byte-identical by construction rather than
by inspection.

  D_Pe     Pr 0.71 -> 2.84   (Peclet 71 -> 284, momentum solution unchanged)
  D_wedge  wedge 5 deg -> 1 deg

DIAGNOSTIC, NOT GRADED.  Neither case carries a band and neither can pass or
fail.  No T1c verdict moves.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t1c as B                                    # noqa: E402

NR, NX = B.LEVELS["f"]
CASES = {"D_Pe": dict(Pr=2.84, wedge=5.0),
         "D_wedge": dict(Pr=B.PR, wedge=1.0)}


def main():
    made = []
    for name, c in sorted(CASES.items()):
        d = os.path.join(HERE, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        for sub in ("0.orig", "constant", "system"):
            os.makedirs(os.path.join(d, sub))
        w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)

        # the ONLY two levers, applied by temporarily setting the module globals
        # the generators read, so every other byte comes from the frozen builder
        old_pr, old_wedge = B.PR, B.WEDGE_DEG
        B.PR, B.WEDGE_DEG = c["Pr"], c["wedge"]
        try:
            w("system/blockMeshDict", B.block_mesh(NR, NX))
            w("system/controlDict", B.control_dict())
            w("system/fvSchemes", B.fv_schemes())
            w("system/fvSolution", B.fv_solution())
            w("constant/transportProperties", B.transport())
            w("constant/turbulenceProperties", B.turbulence_properties())
            w("constant/g", B.gravity())
            w("0.orig/U", B.field_U())
            w("0.orig/p_rgh", B.field_p())
            w("0.orig/T", B.field_T("fixedFlux"))
            w("0.orig/alphat", B.field_alphat())
            txt = B.case_txt(name, dict(level="f", nr=NR, nx=NX,
                                        wall="fixedFlux"))
        finally:
            B.PR, B.WEDGE_DEG = old_pr, old_wedge

        txt += (f"diagnostic       yes -- NOT GRADED, no band, cannot pass or fail\n"
                f"changed_from     L_q_f\n"
                f"Pr_diag          {c['Pr']}\n"
                f"wedge_deg        {c['wedge']}\n"
                f"Peclet           {B.RE * c['Pr']:.1f}\n")
        # CASE.txt's Pr line must match what the case actually solves
        txt = "\n".join(("Pr                %.10g" % c["Pr"]) if ln.startswith("Pr ")
                        else ln for ln in txt.split("\n"))
        w("CASE.txt", txt)
        made.append((name, c["Pr"], c["wedge"], B.RE * c["Pr"]))

    print(f"{len(made)} diagnostic cases built ({NR} x {NX} = {NR*NX} cells each,"
          f" endTime {B.END_TIME})")
    print(f"  {'case':10s} {'Pr':>6s} {'wedge':>7s} {'Pe':>8s}")
    for n, pr, wd, pe in made:
        print(f"  {n:10s} {pr:6.2f} {wd:6.1f}d {pe:8.1f}")
    print(f"  baseline L_q_f: Pr {B.PR}, wedge {B.WEDGE_DEG}d, Pe {B.RE*B.PR:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
