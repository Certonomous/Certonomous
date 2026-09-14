#!/usr/bin/env python3
"""The INSTANTANEOUS temperature plane at a time the mean does NOT contain.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient/render_instant_t10.py

Round 3 asks that the instantaneous panel and the time-averaged panel come from
DIFFERENT times, so the pair shows what averaging removed. The reconstructed tree
of K2h_L3 holds only t = 0 and t = 110, so t = 10 is read from the run's own
DECOMPOSED tree (processor0..3/10), which is where the solver wrote it. Nothing is
reconstructed and nothing is written into the run: the scratch case is symlinks.

t = 10 is BEFORE the registered averaging window (42 -> 112 s). That is stated here
and in the folder's SIDECAR rather than glossed: it is a settling instant, not a
sample of the window the mean covers.

The colour window is the one the committed panels already share, T 289.00 to
301.00 K, so this panel may be laid beside `k2t_plane_mid.png` directly.
"""
import os, shutil, sys, tempfile

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo"))
import demo3d_render_common as C
import render_K2_field_panels as K2F

CASE, TIME = "K2h_L3", "10"
T_RNG = (289.00, 301.00)          # the committed shared window, SIDECAR.md line 56
Z_MID = K2F.Z_MID


def decomposed_reader(case, time_dir, arrays):
    from paraview.simple import OpenFOAMReader, UpdatePipeline
    f = C.facts(case)
    cdir = f["case_dir"]
    procs = sorted(d for d in os.listdir(cdir) if d.startswith("processor"))
    if not procs:
        C.refuse("no decomposed tree under %s" % cdir)
    root = tempfile.mkdtemp(prefix="demo3d_%s_dec_" % case)
    os.symlink(os.path.join(cdir, "system"), os.path.join(root, "system"))
    os.symlink(os.path.join(cdir, "constant"), os.path.join(root, "constant"))
    for p in procs:
        src = os.path.join(cdir, p, time_dir)
        if not os.path.isdir(src):
            shutil.rmtree(root, ignore_errors=True)
            C.refuse("t = %s is not on disk at %s; no time is substituted for it"
                     % (time_dir, src))
        os.symlink(os.path.join(cdir, p), os.path.join(root, p))
    foam = os.path.join(root, "%s.foam" % case)
    open(foam, "w").close()
    reader = OpenFOAMReader(FileName=foam)
    reader.CaseType = "Decomposed Case"
    reader.MeshRegions = ["internalMesh"]
    reader.CellArrays = list(arrays)
    reader.UpdatePipelineInformation()
    try:
        reader.FileNameChanged()
    except Exception:
        pass
    try:
        from paraview.simple import Refresh
        Refresh()
    except ImportError:
        pass                 # not in this ParaView build; FileNameChanged did the work
    reader.UpdatePipelineInformation()
    times = list(reader.TimestepValues)
    if float(TIME) not in [float(t) for t in times]:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("the reader does not offer t = %s; it offers %s" % (TIME, times))
    UpdatePipeline(time=float(TIME), proxy=reader)
    n = reader.GetDataInformation().GetNumberOfCells()
    if n != f["cells"]:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("the decomposed read gives %d cells, not the registered %d"
                 % (n, f["cells"]))
    return reader, root, n


def main():
    C.assert_paraview_version()
    cdir = C.facts(CASE)["case_dir"]
    before = C.run_tree_fingerprint(cdir)
    root = None
    try:
        reader, root, n = decomposed_reader(CASE, TIME, ["T", "U"])
        C.announce("  %s DECOMPOSED: %s cells at t = %s" % (CASE, format(n, ","), TIME))
        rng = reader.GetCellDataInformation().GetArray("T").GetComponentRange(0)
        C.announce("  instantaneous T at t = %s spans %.3f to %.3f K" % (TIME, rng[0], rng[1]))
        if abs(rng[1] - rng[0]) < 1.0:
            C.refuse("the instantaneous field spans %.3f K; the reader is not "
                     "seeing this time's data" % (rng[1] - rng[0]))
        total = K2F.room_plane_panel(
            reader, CASE, TIME,
            os.path.join(HERE, "k2t_plane_t10.png"),
            "Tplot", "T*1.0", K2F.PRESET_T, T_RNG, "T  [K]",
            ("z", Z_MID), contour_at=300.15)
        C.announce("  %s bytes written" % format(total, ","))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)
    C.assert_run_tree_untouched(cdir, before)
    C.announce("  run tree PROVED unchanged: %s" % cdir)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
