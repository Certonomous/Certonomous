#!/usr/bin/env python3
"""G-PV7b / G-PV7c: is the render pipeline coupled to THE CASE, or only to the engine?

Registered in `cases/dafoam/ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md` v1.1
(amendment A1.2). Runs AFTER Stage 0 and BEFORE any act frame.

WHAT STAGE 0 DID NOT ESTABLISH. Stage 0 proved the engine draws a non-blank
frame. It said nothing whatever about whether the pixels have anything to do
with our run. A pipeline that renders a stale surface, a cached image, or a
hard-coded sphere would have passed Stage 0 exactly as cleanly. **"The engine
draws" and "the engine draws THIS RUN" are different claims and only the second
one is worth publishing a frame on.**

  G-PV7b  perturb the GEOMETRY ON DISK, re-render, the frame MUST move
  G-PV7c  re-render the SAME geometry, the frame MUST reproduce

THE PERTURBATION IS ON DISK, NOT IN PARAVIEW. Applying a transform filter inside
ParaView would test ParaView's transform, not the pipeline's coupling to the
case files. The only version of this test that means anything edits the bytes the
reader reads.

THE CAMERA IS FIXED AND EXPLICIT, NEVER `ResetCamera`. `ResetCamera` reframes on
whatever it is given, so it would hide a geometry change by zooming to fit it --
a pure translation would render pixel-identical. A fixed camera is what makes a
geometry change visible as a pixel change.

NO RUN DIRECTORY IS TOUCHED. The mesh is COPIED out of the run root into this
item's own run directory and the perturbation is applied to the copy. The source
case is opened read-only and never written.

    python3 cases/dafoam/actd_paraview_coupling.py
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN_ROOT = REPO / "verification" / "runs" / "actD_paraview" / "coupling"

#: Read-only source. The D19M base mesh: the 4,032-cell 2D NACA0012 section.
SOURCE_CASE = Path("/home/ubuntu/certonomous-runs/"
                   "CURRICULUM-D19M-a1-naca0012-subsonic-multipoint/MESH")

WRAPPER = Path("/opt/paraview/bin/pvbatch")
REAL = Path("/opt/ParaView-5.13.3-egl-MPI-Linux-Python3.10-x86_64/bin/pvbatch-real")
MD5_WRAPPER = "82ec8db976f28f51f2003a56c04fc272"   # G-PV1a
MD5_REAL = "dc272bb98d4ca91fd2f72dd3e89256b4"      # G-PV1b

MODAL_SHARE_MAX = 0.99      # G-PV7a
DISTINCT_COLOURS_MIN = 64   # G-PV7a
DIFF_MIN = 0.001            # G-PV7b: >= 0.1 % of pixels must move
SAME_MAX = 0.001            # G-PV7c: < 0.1 % of pixels may move

#: The perturbation. Localised to the aerofoil so the test is sharp: a change
#: confined to the body must STILL move pixels in a view framed on the body.
#: A whole-domain scaling would pass more easily and prove less.
PERTURB_X = (0.0, 1.0)
PERTURB_Y_ABS = 0.2
PERTURB_Y_SCALE = 1.30

#: Half-height of the view, in metres. Frames the aerofoil, NOT the 18.6 m far
#: field: a perturbation confined to the body has to be visible at the scale the
#: picture is taken at, or the test measures the camera rather than the coupling.
PARALLEL_SCALE = 0.12

RENDER = '''
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
print("SENTINEL_IMPORT_OK", flush=True)
r = OpenFOAMReader(FileName=CASE)
r.MeshRegions = ["internalMesh"]
r.UpdatePipeline()
info = r.GetDataInformation()
print("CELLS", info.GetNumberOfCells(), flush=True)
print("POINTS", info.GetNumberOfPoints(), flush=True)
v = CreateRenderView()
v.ViewSize = [640, 420]
v.Background = [0.12, 0.14, 0.18]
v.OrientationAxesVisibility = 0
d = Show(r, v)
d.Representation = "Surface With Edges"
# FIXED CAMERA. Never ResetCamera: it reframes on what it is given and would
# hide the very change this test exists to detect.
#
# THE CAMERA IS SET *AFTER* THE FIRST Render AND THEN READ BACK. The first
# version of this set the camera before any render, and ParaView overrode
# CameraParallelScale during view initialisation: the frame came back showing
# the whole 18.6 m O-grid instead of the aerofoil, the body was about ten
# pixels wide, and a 30 % geometry perturbation moved 74 ppm of the image. That
# read as a coupling failure and was nothing of the kind -- it was this camera.
# So the value is asserted rather than assumed, on the same principle as every
# other control here: a setting you did not read back is a setting you hope you
# made.
Render(v)
v.CameraParallelProjection = 1
v.CameraPosition = [0.5, 0.0, 3.0]
v.CameraFocalPoint = [0.5, 0.0, 0.0]
v.CameraViewUp = [0.0, 1.0, 0.0]
v.CameraParallelScale = PSCALE
Render(v)
got = float(v.CameraParallelScale)
print("CAMSCALE", got, flush=True)
if abs(got - PSCALE) > 1e-9:
    raise SystemExit("REFUSE: the camera did not take: parallel scale is "
                     "%r, asked for %r" % (got, PSCALE))
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
'''


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def stage_case(dest: Path) -> None:
    """Copy the mesh out of the run root. The source is never written."""
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "constant" / "polyMesh").mkdir(parents=True)
    (dest / "system").mkdir(parents=True)
    for f in (SOURCE_CASE / "constant" / "polyMesh").iterdir():
        out = dest / "constant" / "polyMesh" / f.name.replace(".gz", "")
        if f.name.endswith(".gz"):
            out.write_bytes(gzip.decompress(f.read_bytes()))
        else:
            shutil.copy(f, out)
    for f in ("controlDict", "fvSchemes", "fvSolution"):
        src = SOURCE_CASE / "system" / f
        if src.exists():
            shutil.copy(src, dest / "system" / f)
    (dest / "case.foam").write_text("")


def perturb_points(case: Path) -> dict:
    """Scale y on the aerofoil, in the bytes the reader reads.

    Returns what was actually changed, so the test reports a MEASURED
    perturbation rather than an intended one -- if the filter matched nothing,
    G-PV7b would be asking the frame to move for no reason and the failure
    would look like a coupling defect instead of a broken plant.
    """
    p = case / "constant" / "polyMesh" / "points"
    lines = p.read_text().splitlines()
    moved = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not (s.startswith("(") and s.endswith(")") and s.count(" ") == 2):
            continue
        try:
            x, y, z = (float(v) for v in s[1:-1].split())
        except ValueError:
            continue
        if PERTURB_X[0] <= x <= PERTURB_X[1] and abs(y) <= PERTURB_Y_ABS:
            lines[i] = f"({x:.14g} {y * PERTURB_Y_SCALE:.14g} {z:.14g})"
            moved += 1
    p.write_text("\n".join(lines) + "\n")
    return {"points_moved": moved, "y_scale": PERTURB_Y_SCALE}


def render(case: Path, out: Path, tag: str) -> dict:
    if out.exists():
        out.unlink()
    script = RUN_ROOT / f"render_{tag}.py"
    script.write_text(f"CASE = {str(case / 'case.foam')!r}\n"
                      f"OUT = {str(out)!r}\n"
                      f"PSCALE = {PARALLEL_SCALE!r}\n" + RENDER)
    t0 = time.time()
    r = subprocess.run([str(WRAPPER), str(script)], capture_output=True,
                       text=True, timeout=900)
    wall = time.time() - t0
    cells = points = camscale = None
    for ln in r.stdout.split("\n"):
        if ln.startswith("CAMSCALE"):
            camscale = float(ln.split()[1])
        if ln.startswith("CELLS"):
            cells = int(ln.split()[1])
        if ln.startswith("POINTS"):
            points = int(ln.split()[1])
    return {"rc": r.returncode, "wall_s": round(wall, 3), "ranks": 1,
            "core_min": round(wall / 60.0, 4), "cells": cells, "points": points,
            "camera_parallel_scale_readback": camscale,
            "frame": str(out), "exists": out.exists(),
            "stderr_tail": r.stderr.strip().splitlines()[-5:]}


def content(png: Path) -> dict:
    from PIL import Image
    im = Image.open(png).convert("RGB")
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
        else list(im.getdata())
    c = collections.Counter(px)
    colour, n = c.most_common(1)[0]
    return {"pixels": len(px), "distinct_colours": len(c),
            "modal_share": n / len(px), "size": list(im.size)}


def frac_differing(a: Path, b: Path) -> float:
    from PIL import Image
    import numpy as np
    ia = np.asarray(Image.open(a).convert("RGB"), dtype=np.int16)
    ib = np.asarray(Image.open(b).convert("RGB"), dtype=np.int16)
    if ia.shape != ib.shape:
        return 1.0
    return float((np.abs(ia - ib).sum(axis=2) > 0).mean())


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    rec: dict = {
        "_what": "G-PV7b/G-PV7c coupling plants: is the pipeline coupled to the case?",
        "_preregistration": "cases/dafoam/"
                            "ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md v1.1",
        "_source_case": str(SOURCE_CASE),
        "_source_is_read_only": "the mesh is copied out; the run root is never written",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # ---------------------------------------------- G-PV1a / G-PV1b --------
    for gate, path, want in (("G-PV1a", WRAPPER, MD5_WRAPPER),
                             ("G-PV1b", REAL, MD5_REAL)):
        got = md5(path) if path.exists() else None
        rec[gate] = {"path": str(path), "md5_measured": got,
                     "verdict": "PASS" if got == want else "NOT A RESULT"}
        if got != want:
            rec["VERDICT"] = "NOT A RESULT"
            (RUN_ROOT / "coupling.json").write_text(json.dumps(rec, indent=1))
            print(f"REFUSE: {gate}: md5 {got} != {want}")
            return 2
    print(f"G-PV1a PASS  G-PV1b PASS")

    # ---------------------------------------------------- stage the case ---
    base = RUN_ROOT / "base"
    pert = RUN_ROOT / "perturbed"
    stage_case(base)
    stage_case(pert)
    rec["perturbation"] = perturb_points(pert)
    print(f"perturbation: {rec['perturbation']['points_moved']} points scaled "
          f"in y by {PERTURB_Y_SCALE} on the aerofoil")
    if rec["perturbation"]["points_moved"] == 0:
        rec["VERDICT"] = "NOT A RESULT"
        (RUN_ROOT / "coupling.json").write_text(json.dumps(rec, indent=1))
        print("REFUSE: the perturbation matched no points, so G-PV7b would be "
              "asking the frame to move for no reason. Broken plant, not a "
              "coupling defect.")
        return 2

    # --------------------------------------------------------- render ------
    a1 = RUN_ROOT / "base_1.png"
    a2 = RUN_ROOT / "base_2.png"
    b1 = RUN_ROOT / "perturbed_1.png"
    rec["render_base_1"] = render(base, a1, "base_1")
    rec["render_base_2"] = render(base, a2, "base_2")
    rec["render_perturbed"] = render(pert, b1, "perturbed")
    total_core_min = round(sum(rec[k]["core_min"] for k in
                               ("render_base_1", "render_base_2",
                                "render_perturbed")), 4)
    rec["core_min_total"] = total_core_min

    for k in ("render_base_1", "render_base_2", "render_perturbed"):
        if rec[k]["rc"] != 0 or not rec[k]["exists"]:
            rec["VERDICT"] = "NOT A RESULT"
            (RUN_ROOT / "coupling.json").write_text(json.dumps(rec, indent=1))
            print(f"REFUSE: {k} did not render (rc={rec[k]['rc']})")
            for ln in rec[k]["stderr_tail"]:
                print(f"  {ln}")
            return 2

    print(f"mesh as ParaView reads it: {rec['render_base_1']['cells']} cells, "
          f"{rec['render_base_1']['points']} points")

    # --------------------------------------------------------- G-PV7a ------
    fails = []
    for name, png in (("base_1", a1), ("base_2", a2), ("perturbed", b1)):
        c = content(png)
        blank = (c["modal_share"] >= MODAL_SHARE_MAX
                 or c["distinct_colours"] < DISTINCT_COLOURS_MIN)
        rec[f"G-PV7a_{name}"] = dict(c, verdict="NOT A RESULT" if blank else "PASS")
        print(f"G-PV7a {name:>10}: {c['distinct_colours']:>6} colours, "
              f"modal {c['modal_share']:.4f}  "
              f"{'BLANK' if blank else 'ok'}")
        if blank:
            fails.append(f"G-PV7a {name} is blank")

    # ------------------------------------------------- G-PV7c then G-PV7b --
    same = frac_differing(a1, a2)
    diff = frac_differing(a1, b1)
    rec["G-PV7c"] = {"frac_pixels_differing": same, "threshold_max": SAME_MAX,
                     "verdict": "PASS" if same < SAME_MAX else "NOT A RESULT"}
    rec["G-PV7b"] = {"frac_pixels_differing": diff, "threshold_min": DIFF_MIN,
                     "verdict": "PASS" if diff >= DIFF_MIN else "NOT A RESULT"}
    print(f"G-PV7c  unperturbed re-render differs on {same:.6f} of pixels "
          f"(must be < {SAME_MAX})   {rec['G-PV7c']['verdict']}")
    print(f"G-PV7b  perturbed geometry differs on {diff:.6f} of pixels "
          f"(must be >= {DIFF_MIN})   {rec['G-PV7b']['verdict']}")
    if same >= SAME_MAX:
        fails.append("G-PV7c: the renderer does not reproduce itself")
    if diff < DIFF_MIN:
        fails.append("G-PV7b: the frame did not move when the case did")

    rec["VERDICT"] = "NOT A RESULT" if fails else "PASS"
    rec["_scope"] = ("proves the pipeline reads THIS CASE off disk and that its "
                     "output is stable. Proves nothing about physics.")
    (RUN_ROOT / "coupling.json").write_text(json.dumps(rec, indent=1))

    print(f"\ncost: {total_core_min} core-min, three frames")
    if fails:
        for f in fails:
            print(f"REFUSE: {f}")
        return 1
    print("PASS  the pipeline is coupled to the case, and stable when it is not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
