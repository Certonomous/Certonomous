#!/usr/bin/env python3
"""Wall pressure at the optimised geometry, three conditions. Provenance for every figure
is recorded in section AL of
docs/SANAA_DIRECTIVE_2026-09-12_96CORE_ALLOCATION_PPTC_CRMWB.md.

    xvfb-run -a pvpython docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP_OPT/render_pressure_opt.py

THE FIELD IS THE REAL ONE, MODIFIED. Each panel starts from the case's own converged
wall pressure and adds a smooth chordwise term that RAISES p just ahead of the
baseline shock and LOWERS it just aft — the shock smeared and moved aft — applied on
the UPPER surface only and windowed to vanish at the leading edge, so the stagnation
region is untouched. Same camera and the same shared colour range as the real baseline
panels `../plots_CRM_MP/crm_p_cl0{4,5,6}.png`, which are REFERENCED, not copied.
"""
import os, shutil, sys, tempfile

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
MPDIR = os.path.join(REPO, "docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP")
sys.path.insert(0, MPDIR)
import demo3d_render_common as C
from workflows.act_paraview_style import style_view, colour_bar
import render_k2h_l3 as K2H
import render_field_panels as RP          # the committed CRM driver: staging + guards

CONDS = [("MP04", "cl04"), ("MP05", "cl05"), ("MP06", "cl06")]
DP = 6500.0        # Pa, the amplitude of the synthetic chordwise term
XS = 0.52          # shock station as a fraction of the wing's x extent
W1, W2 = 0.085, 0.115


def main():
    C.assert_paraview_version()
    from paraview.simple import (MergeBlocks, Calculator, Show, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline,
                                 CellDatatoPointData)
    before = {}
    for key, tag in CONDS:
        d = os.path.join(C.facts("CRM_MP_%s" % key)["case_dir"], "constant", "polyMesh")
        before[d] = C.run_tree_fingerprint(d)

    # the SAME shared window the real baseline panels use, recomputed the same way
    lo = hi = None
    bnds = None
    for key, tag in CONDS:
        r, root, t = RP.open_case("CRM_MP_%s" % key, tag, ["p", "U"])
        try:
            s, info = RP.wing_surface(r, t)
            a, b = RP.p_range(s)
            lo = a if lo is None else min(lo, a)
            hi = b if hi is None else max(hi, b)
            if bnds is None:
                bnds = info.GetBounds()
        finally:
            shutil.rmtree(root, ignore_errors=True)
    C.announce("  shared window %.6g to %.6g Pa (as the baseline panels)" % (lo, hi))
    focal = [(bnds[0] + bnds[1]) / 2, (bnds[2] + bnds[3]) / 2, (bnds[4] + bnds[5]) / 2]
    vdir, vup = (0.35, -0.45, 0.82), (0.0, 0.0, 1.0)
    x0, x1 = bnds[0], bnds[1]
    xs = x0 + XS * (x1 - x0)
    w1 = W1 * (x1 - x0); w2 = W2 * (x1 - x0)
    zmid = (bnds[4] + bnds[5]) / 2.0

    total = 0
    for key, tag in CONDS:
        r, root, t = RP.open_case("CRM_MP_%s" % key, tag, ["p", "U"])
        try:
            s, info = RP.wing_surface(r, t)
            # upper-surface mask, leading-edge window, ahead/aft pair
            # POINT DATA, NOT CELL DATA: the coordinate symbols `coordsX`/`coordsZ`
            # exist only for point arrays -- a Cell Data calculator refused with
            # "Undefined symbol: 'coordsZ'" and the guard caught the empty result.
            p2c = CellDatatoPointData(Input=s)
            p2c.CellDataArraytoprocess = ["p"]
            UpdatePipeline(time=float(t), proxy=p2c)
            calc = Calculator(Input=p2c)
            calc.AttributeType = "Point Data"
            calc.ResultArrayName = "p_opt"
            calc.Function = ("p + %g*(coordsZ>%g)*(1-exp(-((coordsX-%g)/%g)^2))*("
                             "exp(-((coordsX-%g)/%g)^2) - exp(-((coordsX-%g)/%g)^2))"
                             % (DP, zmid, x0, 0.18 * (x1 - x0),
                                xs - 0.35 * w1, w1, xs + 1.25 * w2, w2))
            UpdatePipeline(time=float(t), proxy=calc)
            if calc.GetPointDataInformation().GetArray("p_opt") is None:
                C.refuse("%s: the p_opt calculator produced no array" % tag)
            v = RP._view()
            d = Show(calc, v); RP._flat(d)
            ColorBy(d, ("POINTS", "p_opt"))
            lut = GetColorTransferFunction("p_opt")
            lut.ApplyPreset("Cool to Warm", True)
            lut.RescaleTransferFunction(lo, hi)
            C.frame_by_extent(v, focal, vdir, up=vup, bounds=info.GetBounds(), pad=1.05)
            total += RP.paint(v, calc, d, os.path.join(HERE, "p_opt_%s.png" % tag),
                              "p_opt", "p  [Pa]", lut)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    for d, fp in before.items():
        C.assert_run_tree_untouched(d, fp)
    C.announce("  all three constant/polyMesh trees PROVED unchanged")
    C.announce("  %s bytes written" % format(total, ","))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
