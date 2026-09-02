#!/usr/bin/env python3
"""Render an uploaded STL surface with ParaView, with provenance beside it.

WHY THIS EXISTS. Sanaa's 2026-09-02 ~17:30Z order on the jet-flap act: "the
first thing that should appear is the STL file geometry, THEN the 2D plot."
The act's every visual is a ParaView render by her standing order ("Never
that trashy canvas"), and no render of the served STL existed: every panel
on disk is rendered from a solved case's polyMesh by
``render_openfoam_paraview.py``, which cannot read a bare STL. This script
renders the surface file itself.

WHAT THE SIDECAR CLAIMS, AND WHAT IT DELIBERATELY DOES NOT. A case panel's
sidecar records the CELL COUNT so the sequencer can assert picture and
printed count are one grid. An STL is not a mesh of the calculation; writing
a cell count into its sidecar would state a fact the picture does not hold.
The sidecar therefore records the surface's own facts: the file, its sha256,
its triangle count read from the file's own header, its bounds, the camera,
and this script's sha -- and no ``cells`` key, so nothing downstream can
mistake it for a grid panel.

REFUSAL DISCIPLINE. A blank or near-blank render exits non-zero (the min-ink
guard, same idea as the case renderer's): a picture that failed to draw must
never land looking like a picture.

HOW TO RUN (ParaView 5.11.2, headless):

    xvfb-run -a pvbatch scripts/render_stl_paraview.py \
        --stl <file.stl> --out <dir> [--prefix <name>]
"""

import argparse
import hashlib
import json
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKGROUND = (0.024, 0.027, 0.031)          # the control room's dark surface
SURFACE_RGB = (0.62, 0.74, 0.86)            # the house body colour, unshaded-ish
RESOLUTION = (1920, 1080)
MIN_INK = 0.02                              # fraction of non-background pixels


def stl_facts(path: Path) -> dict:
    """Triangle count and bounds read from the FILE, never typed."""
    data = path.read_bytes()
    if data[:5] == b"solid" and b"facet" in data[:300]:
        import re

        verts = re.findall(
            rb"vertex\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", data)
        pts = [(float(a), float(b), float(c)) for a, b, c in verts]
        tris = len(pts) // 3
    else:
        tris = struct.unpack("<I", data[80:84])[0]
        pts = []
        for i in range(tris):
            off = 84 + i * 50
            for v in range(3):
                pts.append(struct.unpack_from("<3f", data, off + 12 + v * 12))
    xs, ys, zs = zip(*pts)
    return {"triangles": tris,
            "bounds": [min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)],
            "sha256": hashlib.sha256(data).hexdigest()}


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prefix", default=None)
    args = ap.parse_args(argv)

    stl = Path(args.stl).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix or stl.stem
    facts = stl_facts(stl)

    from paraview.simple import (  # noqa: PLC0415  (pvbatch-only import)
        STLReader, Show, Render, GetActiveViewOrCreate, SaveScreenshot,
        ResetCamera)

    reader = STLReader(FileNames=[str(stl)])
    view = GetActiveViewOrCreate("RenderView")
    view.ViewSize = list(RESOLUTION)
    # 5.11 paints its own palette background unless told not to; without this
    # the Background property is silently ignored.
    view.UseColorPaletteForBackground = 0
    view.Background = list(BACKGROUND)
    view.OrientationAxesVisibility = 0
    disp = Show(reader, view)
    # Solid colour: an STL carries no field, so no ColorBy call at all (5.11's
    # ColorBy(disp, None) raises "invalid association string").
    disp.ColorArrayName = ["POINTS", ""]
    disp.DiffuseColor = list(SURFACE_RGB)
    # Plain surface: at this file's triangle density edge rendering is moire,
    # not information; the triangle count is stated in the sidecar and on the
    # upload panel instead.
    disp.Representation = "Surface"

    # An angled three-quarter view, so the extrusion reads as a surface and
    # the slot at the trailing edge is visible, derived from the measured
    # bounds rather than typed.
    b = facts["bounds"]
    cx, cy, cz = ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2)
    span = max(b[1] - b[0], b[3] - b[2], b[5] - b[4])
    view.CameraFocalPoint = [cx, cy, cz]
    view.CameraPosition = [cx + 0.55 * span, cy + 0.85 * span, cz + 1.35 * span]
    view.CameraViewUp = [0, 1, 0]
    ResetCamera(view)
    view.CameraParallelProjection = 0
    # Pull in after the reset so the body fills the frame without cropping
    # (her fitted-camera standard; ResetCamera leaves wide margins): move the
    # camera 22% of the way toward the focal point along its own axis,
    # leaving the whole chord inside the frame (a cropped body reads as a
    # viewport bug, her Act D correction).
    fp, cp = view.CameraFocalPoint, view.CameraPosition
    view.CameraPosition = [c + 0.22 * (f - c) for c, f in zip(cp, fp)]
    Render(view)

    png = out / f"{prefix}_surface.png"
    SaveScreenshot(str(png), view, ImageResolution=list(RESOLUTION))

    # Min-ink guard: refuse a picture that failed to draw.
    try:
        from paraview.numpy_support import vtk_to_numpy  # noqa: F401
    except Exception:  # noqa: BLE001
        pass
    ink = _ink_fraction(png)
    if ink < MIN_INK:
        png.unlink(missing_ok=True)
        print(f"REFUSED: render carries {ink:.4f} ink fraction, under "
              f"{MIN_INK}; a blank picture must not land looking like one",
              file=sys.stderr)
        return 2

    sidecar = {
        "image": png.name,
        "panel": "stl_surface",
        "source_stl": str(stl),
        "stl_sha256": facts["sha256"],
        "triangles": facts["triangles"],
        "bounds": facts["bounds"],
        "camera": {"position": list(view.CameraPosition),
                   "focal_point": list(view.CameraFocalPoint),
                   "view_up": list(view.CameraViewUp)},
        "background_rgb": list(BACKGROUND),
        "resolution": list(RESOLUTION),
        "ink_fraction": round(ink, 6),
        "data_provenance": ("rendered from the served STL file itself; no "
                            "synthesised, smoothed or decimated geometry"),
        "paraview": "5.11.2 (/usr/bin/pvbatch, xvfb-run)",
        "script": "scripts/render_stl_paraview.py",
        "script_sha256": hashlib.sha256(
            Path(__file__).read_bytes()).hexdigest(),
        "generated_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }
    png.with_suffix(".json").write_text(
        json.dumps(sidecar, indent=2, sort_keys=True), encoding="utf-8")
    print(f"rendered {png} ({facts['triangles']} triangles, ink {ink:.3f})")
    return 0


def _ink_fraction(png: Path) -> float:
    """Non-background fraction of the saved image, read back off disk."""
    try:
        from PIL import Image
    except ImportError:
        # pvbatch's python may lack PIL; fall back to a byte-level heuristic
        # that still catches an all-background PNG (tiny file).
        return 1.0 if png.stat().st_size > 40_000 else 0.0
    img = Image.open(png).convert("RGB")
    bg = tuple(round(c * 255) for c in BACKGROUND)
    px = img.getdata()
    non_bg = sum(1 for p in px
                 if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 18)
    return non_bg / (img.width * img.height)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
