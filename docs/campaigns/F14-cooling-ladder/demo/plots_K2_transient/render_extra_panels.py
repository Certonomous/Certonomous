#!/usr/bin/env python3
"""Two EXTRA ParaView panels for the K2 transient demo folder, on the owner's
2026-09-13 instruction to add the standard field renders beside the ordered plots.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient/render_extra_panels.py

It adds NOTHING of its own: it drives `render_k2h_l3.fig_mean_field` -- the
committed instrument, with its planted colour control and its stamp guard -- on
two fields that driver does not already emit:
    * `UMean` the time-averaged velocity, over the same 42 -> 110 s window as the
      TMean and p_rghMean panels the committed driver emits.

DELIBERATELY NOT DRIVEN HERE: an instantaneous `T` panel.  `fig_mean_field` writes
the caption "mean over simulated 42 to <t> s" as a CONSTANT rather than as a
property of the field it was handed, so an instantaneous panel drawn through it
would ship a caption claiming a time average that was never taken.  Reported as a
finding rather than worked around.
The mesh panel and the TMean / p_rghMean panels come from the committed driver's
own output and are not re-rendered here.
"""
import os, shutil, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
import demo3d_render_common as C
import render_k2h_l3 as K2H

VERDICT = "PASS"          # GRADE.K2h_L3.json verdict, quoted, never composed here


def main():
    C.assert_paraview_version()
    case = K2H.FIELD_CASE
    cdir = C.facts(case)["case_dir"]
    before = C.run_tree_fingerprint(cdir)
    t = K2H.resolve_field_time(cdir)
    K2H.FIELD_END = t
    stamp = ("%s ; 664848 cells ; t = %s ; %s" % (case, t, VERDICT))
    geom = ("Room 3.6 x 3.5 x 2.7 m ; 4 racks ; FINE level, TRANSIENT "
            "buoyantBoussinesqPimpleFoam")
    root = None
    try:
        K2H._repoint(case, t, stamp, geom)
        reader, root, n = C.open_case(case, ["UMean", "TMean"], [t])
        C.announce("  %s: %s cells at t = %s" % (case, format(n, ","), t))
        for field, label, preset, out in (
                ("UMean", "U mean  (m/s)", "Viridis (matplotlib)", "k2t_UMean_field.png"),):
            try:
                K2H.fig_mean_field(reader, os.path.join(HERE, out), field, label,
                                   preset, stamp, geom)
            except C.RenderRefusal as exc:
                C.announce_error("REFUSED %s: %s" % (out, exc))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)
    C.assert_run_tree_untouched(cdir, before)
    C.announce("  run tree PROVED unchanged: %s" % cdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
