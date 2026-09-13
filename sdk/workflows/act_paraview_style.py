"""The v2 look for every ParaView panel, in one place.

`docs/plot_orders/README_PLOT_LIBRARY_V2.md` §13, and Sanaa's instruction of
2026-09-13: *"ParaView panels: white background, no axes triad, one legible colour
bar, no caption baked into the image. The captions live in the act; the image is
the field. Colour bars … one quarter of the frame height with a title in the
quantity's unit."*

So: white ground, no orientation triad, ONE colour bar a quarter of the frame high
whose title is the symbol and its unit, and NOTHING WRITTEN ON THE IMAGE. The
verdict, the case, the time and the geometry live in the folder's SIDECAR.md and in
the act beside the figure.

THE VERDICT GUARD IS NOT LOST WITH THE CAPTION. `demo3d_render_common.assert_stamp`
refuses a verdict word a case does not own, and every driver still calls it on the
stamp it WOULD have drawn, before rendering anything. What changed is where the
sentence is printed, not whether it is checked.
"""
from __future__ import annotations

BAR_LENGTH = 0.25          # fraction of the frame height, per the instruction
BAR_THICKNESS = 14         # points; readable at 1600 x 1000 without crowding the field
INK = [0.15, 0.15, 0.15]


def style_view(view, size=(1600, 1000)):
    """White ground, no triad, no annotation furniture."""
    view.ViewSize = list(size)
    view.OrientationAxesVisibility = 0
    view.UseColorPaletteForBackground = 0
    try:
        view.BackgroundColorMode = "Single Color"
    except Exception:
        pass
    view.Background = [1.0, 1.0, 1.0]
    try:
        view.Background2 = [1.0, 1.0, 1.0]
    except Exception:
        pass
    return view


def colour_bar(view, lut, title, *, vertical=True):
    """The ONE colour bar: a quarter of the frame high, titled by symbol and unit."""
    from paraview.simple import GetScalarBar
    b = GetScalarBar(lut, view)
    b.Visibility = 1
    b.Title = title
    b.ComponentTitle = ""
    b.TitleColor = INK
    b.LabelColor = INK
    b.TitleFontSize = 14
    b.LabelFontSize = 12
    b.ScalarBarLength = BAR_LENGTH
    b.ScalarBarThickness = BAR_THICKNESS
    if vertical:
        b.Orientation = "Vertical"
        b.WindowLocation = "Any Location"
        b.Position = [0.90, 0.36]
    b.AutomaticLabelFormat = 0
    b.LabelFormat = "%-#6.3g"
    b.RangeLabelFormat = "%-#6.3g"
    b.AddRangeLabels = 1
    b.DrawTickMarks = 1
    return b
