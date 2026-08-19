#!/usr/bin/env python3
"""
Give the Peclet diagnostic its own mesh ladder, because the single-mesh test was
confounded and the confound was my design error.

DIAGNOSTIC_PREDICTION.md registered Pr as a clean single-parameter lever on the
grounds that raising Pr at fixed Re leaves the MOMENTUM solution untouched.  It
does.  But leaving the momentum field untouched is not the same as leaving the
THERMAL RESOLUTION untouched: the thermal boundary layer scales as Pr^(-1/3), so
at Pr = 2.84 it is 1.59x thinner than at 0.71, and T1c's radial mesh is UNIFORM
(simpleGrading 1 1 1) with no wall clustering at all.  A thinner thermal layer
therefore gets proportionally fewer cells and the fine-mesh discretisation error
grows.

Measured on one mesh the excess went UP by 1.84x where axial conduction predicted
a 16-fold fall -- a comparison that mixes the physical term with a changed
discretisation error and cannot decide anything.

Building the coarse and medium levels at Pr = 2.84 allows Richardson
extrapolation at the higher Peclet number, so the h -> 0 excess can be compared
against the baseline's h -> 0 excess of +0.0748 %, which is the like-for-like
comparison the original design should have specified.

D_Pe (the fine level) IS NOT REBUILT -- it holds a converged solution.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_t1c as B                                    # noqa: E402

PR_DIAG = 2.84
NEW = {"D_Pe_c": B.LEVELS["c"], "D_Pe_m": B.LEVELS["m"]}


def main():
    for name, (nr, nx) in sorted(NEW.items()):
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
        old = B.PR
        B.PR = PR_DIAG
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
            w("0.orig/T", B.field_T("fixedFlux"))
            w("0.orig/alphat", B.field_alphat())
            txt = B.case_txt(name, dict(level="?", nr=nr, nx=nx,
                                        wall="fixedFlux"))
        finally:
            B.PR = old
        txt = "\n".join(("Pr                %.10g" % PR_DIAG)
                        if ln.startswith("Pr ") else ln
                        for ln in txt.split("\n"))
        txt += (f"diagnostic       yes -- NOT GRADED, no band\n"
                f"ladder_for       D_Pe (Pr = {PR_DIAG}, Peclet 284)\n")
        w("CASE.txt", txt)
        print(f"  {name}: built, {nr} x {nx} = {nr*nx} cells, Pr = {PR_DIAG}")
    print(f"\nD_Pe (fine, {B.LEVELS['f'][0]}x{B.LEVELS['f'][1]}) is the third "
          "level and already holds a converged solution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
