#!/usr/bin/env python3
"""Round-3 K2 steady panels: per-rack inlet profiles, streamlines, hot cloud.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/plots_K2_steady/render_round3.py

  k2_inlet_profiles.png  T_in(z) on a vertical line in front of EACH of the four racks,
                         R_1..R_4, with the single limit line. Sampled from the fine
                         steady field; no hot-aisle curve.
  k2_streamlines.png     48 lines seeded across the tile, coloured by T, camera showing
                         the row and both aisles.
  k2_hot_cloud.png       the 27 degC iso-surface with the whole rack row drawn.
"""
import csv, os, shutil, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
import demo3d_render_common as C
from workflows.act_paraview_style import style_view, colour_bar
import render_k2bU3R3 as K2B
import render_k2h_l3 as K2H

CASE, TIME = "K2f_L3", "803"
K = 273.15
RACK_X0, RACK_X1 = K2B.RACK_X0, K2B.RACK_X1
RACK_Y0, RACK_Z1 = K2B.RACK_Y0, K2B.RACK_Z1
N_RACK = 4
MIN_PX = 20000


def main():
    C.assert_paraview_version()
    cdir = C.facts(CASE)["case_dir"]
    before = C.run_tree_fingerprint(cdir)
    from paraview.simple import (CellDatatoPointData, PlotOverLine, Show, Render,
                                 ColorBy, GetColorTransferFunction, UpdatePipeline,
                                 StreamTracer, Tube, Contour, Calculator)
    from paraview import servermanager as sm
    from paraview.vtk.util import numpy_support
    import numpy as np
    root = None
    try:
        reader, root, n = C.open_case(CASE, ["T", "U"], [TIME])
        C.announce("  %s: %s cells at t = %s" % (CASE, format(n, ","), TIME))
        p2c = CellDatatoPointData(Input=reader)
        p2c.CellDataArraytoprocess = ["T", "U"]
        UpdatePipeline(time=float(TIME), proxy=p2c)

        # ---- per-rack inlet profiles, sampled IN FRONT of each rack inlet face
        pitch = (RACK_X1 - RACK_X0) / N_RACK
        profiles, rows = [], []
        for i in range(N_RACK):
            xc = RACK_X0 + pitch * (i + 0.5)
            pol = PlotOverLine(Input=p2c)
            pol.Point1 = [xc, RACK_Y0 - 0.05, 0.02]
            pol.Point2 = [xc, RACK_Y0 - 0.05, RACK_Z1 - 0.02]
            try:
                pol.Resolution = 120
            except Exception:
                pass
            UpdatePipeline(time=float(TIME), proxy=pol)
            d = sm.Fetch(pol)
            pts = numpy_support.vtk_to_numpy(d.GetPoints().GetData())
            Ta = d.GetPointData().GetArray("T")
            if Ta is None:
                C.refuse("rack %d: the sample line carries no T" % (i + 1))
            Tv = numpy_support.vtk_to_numpy(Ta)
            ok = np.isfinite(Tv) & (Tv > 0)
            if ok.sum() < 20:
                C.refuse("rack %d: only %d valid samples on the line" % (i + 1, ok.sum()))
            z = pts[ok, 2]; t = Tv[ok] - K
            profiles.append({"label": "rack %d" % (i + 1), "z": list(z), "T": list(t)})
            rows += [[i + 1, float(z[j]), float(t[j])] for j in range(len(z))]
            C.announce("  rack %d at x = %.3f m: %d samples, T %.2f..%.2f degC"
                       % (i + 1, xc, ok.sum(), t.min(), t.max()))
        # THE FIGURE IS NOT DRAWN HERE. matplotlib under pvpython is not the
        # matplotlib every other figure in this repository is drawn with: three
        # attempts to save this axes failed inside its bundled freetype with
        # "FT_Render_Glyph ... raster overflow", with and without the degree sign.
        # This script SAMPLES and writes the CSV; `plot_inlet_profiles.py` draws it
        # under plain python3, where the same call works. Splitting them also makes
        # the sampling re-usable without a display.
        with open(os.path.join(HERE, "k2_inlet_profiles.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["rack", "z_m", "T_degC"]); w.writerows(rows)

        # ---- streamlines from the tile, coloured by T
        st = StreamTracer(Input=p2c, SeedType="Line")
        st.Vectors = ["POINTS", "U"]
        st.MaximumStreamlineLength = 20.0
        st.SeedType.Point1 = [RACK_X0 + 0.05, 0.35, 0.04]
        st.SeedType.Point2 = [RACK_X1 - 0.05, 0.35, 0.04]
        st.SeedType.Resolution = 48
        UpdatePipeline(time=float(TIME), proxy=st)
        if st.GetDataInformation().GetNumberOfPoints() == 0:
            C.refuse("no streamline was integrated from the tile")
        tube = Tube(Input=st); tube.Radius = K2B.ROOM[0] / 260.0
        UpdatePipeline(time=float(TIME), proxy=tube)
        ta = tube.GetPointDataInformation().GetArray("T")
        if ta is None:
            C.refuse("the tubes carry no T to colour by")
        tlo, thi = ta.GetComponentRange(0)
        C.announce("  streamline T range MEASURED %.2f to %.2f K" % (tlo, thi))
        v = _view()
        d = Show(tube, v); _flat(d)
        ColorBy(d, ("POINTS", "T"))
        lut = GetColorTransferFunction("T"); lut.ApplyPreset("Cool to Warm", True)
        lut.RescaleTransferFunction(tlo, thi)
        colour_bar(v, lut, "T  [K]")
        K2B.rack_block(v)
        C.frame_by_extent(v, (K2B.ROOM[0] / 2, K2B.ROOM[1] / 2, K2B.ROOM[2] / 2),
                          (-0.42, -0.86, 0.30), up=(0.0, 0.0, 1.0),
                          bounds=(0.0, K2B.ROOM[0], 0.0, K2B.ROOM[1], 0.0, K2B.ROOM[2]),
                          pad=1.04)
        Render(v)
        nb = C.save_screenshot(v, os.path.join(HERE, "k2_streamlines.png"), size=(1600, 1000))
        _, px = K2H._colour_spread(os.path.join(HERE, "k2_streamlines.png"))
        if px < MIN_PX:
            C.refuse("k2_streamlines drew only %d body pixels" % px)
        C.announce("  wrote k2_streamlines.png (%s bytes, %s body px)"
                   % (format(nb, ","), format(px, ",")))

        # ---- hot cloud with the rack row drawn
        cont = Contour(Input=p2c); cont.ContourBy = ["POINTS", "T"]
        cont.Isosurfaces = [300.15]
        UpdatePipeline(time=float(TIME), proxy=cont)
        nc = cont.GetDataInformation().GetNumberOfCells()
        if nc == 0:
            C.refuse("the 300.15 K iso-surface is empty")
        C.announce("  iso-surface: %s triangles" % format(nc, ","))
        v2 = _view()
        d2 = Show(cont, v2); _flat(d2)
        d2.ColorArrayName = [None, ""]
        d2.DiffuseColor = [0.82, 0.29, 0.09]; d2.AmbientColor = [0.82, 0.29, 0.09]
        d2.Opacity = 0.85
        K2B.rack_block(v2)
        K2B.outline(reader, v2)
        C.frame_by_extent(v2, (K2B.ROOM[0] / 2, K2B.ROOM[1] / 2, K2B.ROOM[2] / 2),
                          (-0.55, -0.80, 0.42), up=(0.0, 0.0, 1.0),
                          bounds=(0.0, K2B.ROOM[0], 0.0, K2B.ROOM[1], 0.0, K2B.ROOM[2]),
                          pad=1.04)
        Render(v2)
        nb2 = C.save_screenshot(v2, os.path.join(HERE, "k2_hot_cloud.png"), size=(1600, 1000))
        _, px2 = K2H._colour_spread(os.path.join(HERE, "k2_hot_cloud.png"))
        if px2 < MIN_PX:
            C.refuse("k2_hot_cloud drew only %d body pixels" % px2)
        C.announce("  wrote k2_hot_cloud.png (%s bytes, %s body px)"
                   % (format(nb2, ","), format(px2, ",")))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)
    C.assert_run_tree_untouched(cdir, before)
    C.announce("  run tree PROVED unchanged: %s" % cdir)
    return 0


def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView(); style_view(v, size); Render(v)
    return v


def _flat(d):
    d.Ambient, d.Diffuse, d.Specular = 1.0, 0.0, 0.0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
