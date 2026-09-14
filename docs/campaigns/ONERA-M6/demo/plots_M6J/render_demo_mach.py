#!/usr/bin/env python3
"""The ACT's DEMONSTRATION Mach panel at 65 % span.

    xvfb-run -a pvpython docs/campaigns/ONERA-M6/demo/plots_M6J/render_demo_mach.py

The counterpart of `m6_cp_stations_demo.png`'s eta = 0.65 row: the field the act
shows for the target outcome, with the lambda foot ahead of the main front. It
writes ONE new file, `m6_mach_eta065_demo.png`, and touches nothing else --
`m6_mach_eta065.png` and `m6_mach_eta090.png` remain the measured field of the
graded solution, and the run tree is proved unchanged at the end exactly as the
graded driver proves it.

EVERYTHING EXCEPT THE FIELD IS THE GRADED PANEL'S OWN PIPELINE, imported from
`render_field_panels` rather than re-written: the same reader, the same y-normal
cut at the extractor's own station, the same camera and window, the same fixed
0 to 1.4 bar with its five ticks, the same black M = 1 contour and section
outline, and the same planted colour control with its 8x margin.

THE FIELD TRANSFORM, WRITTEN OUT IN FULL. With s the chordwise fraction
(x - x_le)/c and z the vertical coordinate, the drawn Mach is

    M' = M + E(z) * [ a_hold * H(s; s_main, w_main)
                      - a_main * (1 - H(s; s_main, w_main))
                      - a_foot * exp(-((s - s_foot)/w_foot)^2) * H(s; s_main, w_main) ]

    H(s; s0, w) = (1 - tanh((s - s0)/w)) / 2          a smooth front at s0
    E(z)        = exp(-(z/h)^2) * (1 + tanh(z/g)) / 2  upper side only, decaying

so the pocket ahead of the main front is held up, the front at `s_main` is
steepened until the sonic line closes on it, and a single Gaussian well at
`s_foot` pinches the sonic line toward the surface to give the forward leg. The
front positions are NOT free parameters: `s_main` and `s_foot` are the two
compression rises the AGARD taps themselves show at this station -- 0.45-0.50 and
0.15-0.20 of chord -- the same two rises the demonstration Cp curve follows.
Everything outside the upper-side envelope, both fronts' sharpness aside, is the
solved field.
"""
import os, shutil, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import demo3d_render_common as C
import render_field_panels as RF

ETA = "0.65"
S_MAIN, W_MAIN = 0.475, 0.012          # the taps' main rise, 0.45 -> 0.50
S_FOOT, W_FOOT = 0.165, 0.045          # the taps' forward rise, 0.15 -> 0.20
K_SLANT, H_FOOT = 0.30, 0.20           # the forward leg leans aft with height
A_HOLD, A_MAIN, A_FOOT = 0.12, 0.32, 0.42
H_DECAY, G_GATE = 0.22, 0.02           # chord fractions


def transform_expression(x_le, c):
    s = "((coordsX-%.9g)/%.9g)" % (x_le, c)
    zc = "(coordsZ/%.9g)" % c
    H = "((1-tanh((%s-%.9g)/%.9g))/2)" % (s, S_MAIN, W_MAIN)
    gate = "((1+tanh(coordsZ/%.9g))/2)" % (G_GATE * c)
    E = "(exp(-((%s/%.9g)^2))*%s)" % (zc, H_DECAY, gate)
    # THE FORWARD LEG IS A SLANTED BAND, NOT A VERTICAL WELL, and that too was
    # driven before it was written: a vertical Gaussian at the tap-indicated
    # forward rise only softened the pocket's front edge and no second front
    # appeared. A real lambda foot leans AFT with height and meets the main
    # front at a triple point, so the band's centre moves aft as K_SLANT * z/c
    # and its strength dies above H_FOOT. Inside it the drawn Mach is reduced
    # far enough to cross M = 1, which is what splits the pocket into the two
    # lobes the taps' two compression rises imply.
    foot = ("(%.9g*exp(-(((%s-%.9g-%.9g*%s)/%.9g)^2))*exp(-((%s/%.9g)^2))*%s)"
            % (A_FOOT, s, S_FOOT, K_SLANT, zc, W_FOOT, zc, H_FOOT, gate))
    # THE DROP BEHIND THE FRONT IS MULTIPLICATIVE, NOT ADDITIVE, and that is a
    # measurement rather than a style choice: the additive form was driven first
    # and took the drawn field to Mach -0.3009 in the wall layer behind the
    # front, where the solved Mach is already near zero. A negative Mach number
    # is not a demonstration of anything. Scaling by M instead bounds the drawn
    # field below by (1 - A_MAIN) * M, so it cannot leave the physical range.
    return ("Mach*(1 - %s*%.9g*(1-%s))*(1-%s) + %s*%.9g*%s"
            % (E, A_MAIN, H, foot, E, A_HOLD, H))


def main():
    C.assert_paraview_version()
    cdir = C.facts(RF.FINE)["case_dir"]
    before = C.run_tree_fingerprint(cdir)
    C.assert_stamp(RF.STAMP, RF.FINE)
    root = None
    try:
        from paraview.simple import (OpenFOAMReader, CellDatatoPointData, Calculator,
                                     Slice, Show, Render, ColorBy, Contour,
                                     GetColorTransferFunction, UpdatePipeline)
        reader, root, n = C.open_case(RF.FINE, ["p", "U", "T"], [RF.FINE_END])
        C.announce("  %s: %s cells at t = %s" % (RF.FINE, format(n, ","), RF.FINE_END))
        foam = os.path.join(root, "%s.foam" % RF.FINE)
        wall = OpenFOAMReader(FileName=foam)
        wall.MeshRegions = ["patch/wing"]
        wall.CellArrays = ["p"]
        UpdatePipeline(time=float(RF.FINE_END), proxy=wall)

        st = RF.EXT["stations"][ETA]
        y_cut = st["y_cut_target"]
        x0, x1, c = st["x_le"], st["x_te"], st["local_chord"]
        expr = transform_expression(x0, c)
        C.announce("  drawn Mach = %s" % expr)

        reader.MeshRegions = ["internalMesh"]
        UpdatePipeline(time=float(RF.FINE_END), proxy=reader)
        p2c = CellDatatoPointData(Input=reader)
        p2c.CellDataArraytoprocess = ["U", "T", "p"]
        UpdatePipeline(time=float(RF.FINE_END), proxy=p2c)
        m = Calculator(Input=p2c)
        m.AttributeType = "Point Data"
        m.ResultArrayName = "Mach"
        m.Function = RF.MACH_EXPR
        UpdatePipeline(time=float(RF.FINE_END), proxy=m)

        sl = Slice(Input=m)
        sl.SliceType = "Plane"
        sl.SliceType.Origin = [0.0, y_cut, 0.0]
        sl.SliceType.Normal = [0.0, 1.0, 0.0]
        UpdatePipeline(time=float(RF.FINE_END), proxy=sl)
        if sl.GetDataInformation().GetNumberOfCells() == 0:
            C.refuse("the eta = %s slice is empty" % ETA)

        d2 = Calculator(Input=sl)
        d2.AttributeType = "Point Data"
        d2.ResultArrayName = "MachDrawn"
        d2.Function = expr
        UpdatePipeline(time=float(RF.FINE_END), proxy=d2)
        a = d2.GetPointDataInformation().GetArray("MachDrawn")
        if a is None:
            C.refuse("the drawn Mach array was not produced, so nothing would be painted")
        C.announce("  drawn Mach spans %.4f to %.4f (solved field spans %.4f to %.4f)"
                   % (a.GetRange(0) + sl.GetPointDataInformation().GetArray("Mach").GetRange(0)))

        v = RF._view()
        disp = Show(d2, v)
        RF._flat_lighting(disp)
        ColorBy(disp, ("POINTS", "MachDrawn"))
        lut = GetColorTransferFunction("MachDrawn")
        lut.ApplyPreset("Viridis (matplotlib)", True)
        lut.RescaleTransferFunction(0.0, 1.4)
        disp.SetScalarBarVisibility(v, True)
        RF._bar(v, lut, "M  [-]", ticks=[0.0, 0.35, 0.70, 1.05, 1.40])
        bnds = (x0 - 0.3 * c, x1 + 0.3 * c, y_cut, y_cut, -0.6 * c, 0.6 * c)
        C.frame_by_extent(v, [(x0 + x1) / 2, y_cut, 0.0], (0.0, -1.0, 0.0),
                          up=(0.0, 0.0, 1.0), bounds=bnds, pad=1.02, bottom_band=0.0)

        def _lines(view):
            iso = Contour(Input=d2)
            iso.ContourBy = ["POINTS", "MachDrawn"]
            iso.Isosurfaces = [1.0]
            UpdatePipeline(time=float(RF.FINE_END), proxy=iso)
            nseg = iso.GetDataInformation().GetNumberOfCells()
            C.announce("      sonic line M = 1: %s line segments" % format(nseg, ","))
            if not nseg:
                C.refuse("the drawn field carries no M = 1 contour, so the pocket "
                         "it exists to close is not there")
            di = Show(iso, view)
            di.DiffuseColor = [0.0, 0.0, 0.0]; di.AmbientColor = [0.0, 0.0, 0.0]
            di.ColorArrayName = [None, ""]; di.LineWidth = 3.0
            ws = Slice(Input=wall)
            ws.SliceType = "Plane"
            ws.SliceType.Origin = [0.0, y_cut, 0.0]
            ws.SliceType.Normal = [0.0, 1.0, 0.0]
            UpdatePipeline(time=float(RF.FINE_END), proxy=ws)
            dw = Show(ws, view)
            dw.DiffuseColor = [0.0, 0.0, 0.0]; dw.AmbientColor = [0.0, 0.0, 0.0]
            dw.ColorArrayName = [None, ""]; dw.LineWidth = 3.0
            disp.SetScalarBarVisibility(view, True)

        Render(v)
        out = os.path.join(HERE, "m6_mach_eta065_demo.png")
        nb = RF._control_and_save(v, d2, out, "MachDrawn", disp, _lines)
        C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(nb, ",")))
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
