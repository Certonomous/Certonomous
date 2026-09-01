#!/usr/bin/env python3
"""The Act D ParaView render pass: geometry, meshes and fields, from real cases.

Registered in `cases/dafoam/ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md` v1.1.
Runs AFTER Stage 0 (engine renders: PASS, 64b4ea6e) and AFTER the coupling
plants (G-PV7b/G-PV7c: PASS, b3d36ef3).

WHAT IS RENDERED HERE AND WHAT IS NOT. pvbatch draws GEOMETRY, MESHES AND FIELDS
-- anything depicting the body, the grid, or a field on it. DATA PLOTS stay
latexfied matplotlib/native per the figure standard; a ParaView line chart would
be a worse figure, not a more compliant one. That split is [lab-attributed], is
recorded as such in §1 of the pre-registration, and is disclosed to be overturned;
this file is kept separate from any plot code so a reversal is a routing change.

EVERY FRAME CARRIES ITS PROVENANCE (G-PV2) and every frame is graded for content
(G-PV7a). Cell counts are asserted against the case's own `checkMesh.log`
(G-PV4), never against a number in a document -- a sheet quoting 38,304 and a
mesh holding 38,304 are two different claims and only one of them is evidence.

NOTHING HERE IS A NEW PHYSICAL RESULT. Every field drawn already exists on disk
from a landed run; this produces pictures of existing numbers.

    python3 cases/dafoam/actd_paraview_render.py
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = Path("/home/ubuntu/certonomous-runs")
OUT_ROOT = REPO / "verification" / "runs" / "actD_paraview" / "frames"
LADDER = REPO / "cases" / "dafoam" / "ladder-a"

WRAPPER = Path("/opt/paraview/bin/pvbatch")
REAL = Path("/opt/ParaView-5.13.3-egl-MPI-Linux-Python3.10-x86_64/bin/pvbatch-real")
MD5_WRAPPER = "82ec8db976f28f51f2003a56c04fc272"
MD5_REAL = "dc272bb98d4ca91fd2f72dd3e89256b4"

MODAL_SHARE_MAX = 0.99
DISTINCT_COLOURS_MIN = 64

# ---------------------------------------------------------------- the cases --
SECTION = RUNS / "CURRICULUM-AOAI-a1-naca0012-alpha-polar-incompressible" / "case"
WING = RUNS / "A2-mach-wing"
SHAPE_FRAMES = LADDER / "A2_shape_frames.json"

#: The polar's saved state IS the angle the platform refused. `AOA_POINTS.json`
#: gives the last point as alpha 18.0, verdict NOT CONVERGED, last_time 1000,
#: and `case/1000/uniform/time` reads 1000 -- so the field on disk is that
#: point's. THE CONVERGED COUNTERPART IS NOT ON DISK: the sweep re-solves in
#: place, so only the final angle's field survives. That gap is REPORTED rather
#: than filled with a neighbouring angle relabelled.
POLAR_TIME = "1000"
POLAR_ALPHA_DEG = 18.0
POLAR_VERDICT = "NOT CONVERGED"


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def checkmesh_cells(case: Path) -> int | None:
    """G-PV4's reference: the cell count the MESH CHECKER measured."""
    for name in ("checkMesh.log", "logMeshGeneration.txt"):
        log = case / name
        if not log.exists():
            continue
        m = re.search(r"^\s*cells:\s+(\d+)", log.read_text(errors="replace"), re.M)
        if m:
            return int(m.group(1))
    return None


def content(png: Path) -> dict:
    from PIL import Image
    im = Image.open(png).convert("RGB")
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") \
        else list(im.getdata())
    c = collections.Counter(px)
    _colour, n = c.most_common(1)[0]
    return {"pixels": len(px), "distinct_colours": len(c),
            "modal_share": n / len(px), "size": list(im.size)}


def is_blank(c: dict) -> bool:
    return (c["modal_share"] >= MODAL_SHARE_MAX
            or c["distinct_colours"] < DISTINCT_COLOURS_MIN)


# ------------------------------------------------------------ render scripts --
FOAM_RENDER = '''
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
print("SENTINEL_IMPORT_OK", flush=True)
r = OpenFOAMReader(FileName=CASE)
r.MeshRegions = ["internalMesh"]
r.CaseType = "Reconstructed Case"
r.UpdatePipeline()
times = list(r.TimestepValues or [0.0])
want = float(TIME) if TIME else times[-1]
info = r.GetDataInformation()
print("CELLS", info.GetNumberOfCells(), flush=True)
print("POINTS", info.GetNumberOfPoints(), flush=True)
v = CreateRenderView()
v.ViewSize = SIZE
v.Background = [0.12, 0.14, 0.18]
v.OrientationAxesVisibility = 0
d = Show(r, v)
d.Representation = REPRESENTATION
if FIELD:
    v.ViewTime = want
    r.UpdatePipeline(want)
    ColorBy(d, ("POINTS", FIELD, "Magnitude"))
    d.RescaleTransferFunctionToDataRange(True, False)
    d.SetScalarBarVisibility(v, True)
    print("TIME", want, flush=True)
Render(v)
v.CameraParallelProjection = 1
v.CameraPosition = CAM_POS
v.CameraFocalPoint = CAM_FOCUS
v.CameraViewUp = [0.0, 1.0, 0.0]
v.CameraParallelScale = PSCALE
Render(v)
got = float(v.CameraParallelScale)
print("CAMSCALE", got, flush=True)
if abs(got - PSCALE) > 1e-9:
    raise SystemExit("REFUSE: the camera did not take (%r vs %r)" % (got, PSCALE))
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
'''

#: The morph and the wing skin are drawn from the STORED SURFACES, built as
#: explicit polydata. No interpolation anywhere: frame N is the surface the
#: optimiser actually produced at major iteration N, at true scale.
SURFACE_RENDER = '''
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
import json
from paraview import servermanager as sm
from paraview.vtk import vtkPolyData, vtkPoints, vtkCellArray, vtkFloatArray
print("SENTINEL_IMPORT_OK", flush=True)
doc = json.load(open(FRAMES))
base = doc["base_vertices"]
faces = doc["faces"]
disp = doc["frames"][FRAME_INDEX]["disp"] if FRAME_INDEX is not None else None
# THE GRADIENT IS A PER-FACE FIELD AND THE RECORD SAYS SO BY ARITHMETIC, not
# by a label: `gradient.values_mm_per_step` holds 1008 values and `n_quad_faces`
# is 1008, against `n_points` 1031. Attaching it to POINTS -- the first thing
# tried here -- crashed, and had the counts happened to agree it would instead
# have painted a silently wrong field. The count is asserted below rather than
# assumed, because "it fitted" is not the same as "it belongs".
scal = None
if SCALAR_KEY:
    block = doc[SCALAR_KEY]
    scal = block["values_mm_per_step"] if isinstance(block, dict) else block
    if len(scal) != doc["n_quad_faces"]:
        raise SystemExit("REFUSE: %d scalar values against %d faces; this "
                         "field does not belong to this mesh"
                         % (len(scal), doc["n_quad_faces"]))

pts = vtkPoints()
for i, p in enumerate(base):
    if disp is not None:
        pts.InsertNextPoint(p[0] + disp[i][0], p[1] + disp[i][1], p[2] + disp[i][2])
    else:
        pts.InsertNextPoint(p[0], p[1], p[2])
cells = vtkCellArray()
for f in faces:
    cells.InsertNextCell(len(f))
    for idx in f:
        cells.InsertCellPoint(idx)
pd = vtkPolyData()
pd.SetPoints(pts)
pd.SetPolys(cells)
print("POINTS", pts.GetNumberOfPoints(), flush=True)
print("FACES", cells.GetNumberOfCells(), flush=True)
if scal is not None:
    arr = vtkFloatArray(); arr.SetName(SCALAR_NAME)
    for value in scal:
        arr.InsertNextValue(float(value))
    pd.GetCellData().SetScalars(arr)      # per FACE, per the count assertion

src = TrivialProducer(registrationName="surface")
src.GetClientSideObject().SetOutput(pd)
src.UpdatePipeline()
v = CreateRenderView()
v.ViewSize = SIZE
v.Background = [0.12, 0.14, 0.18]
v.OrientationAxesVisibility = 0
d = Show(src, v)
d.Representation = REPRESENTATION
if scal is not None:
    ColorBy(d, ("CELLS", SCALAR_NAME))
    lut = GetColorTransferFunction(SCALAR_NAME)
    lut.ApplyPreset("Cool to Warm (Extended)", True)
    d.RescaleTransferFunctionToDataRange(True, False)
    d.SetScalarBarVisibility(v, True)
Render(v)
v.CameraParallelProjection = 1
v.CameraPosition = CAM_POS
v.CameraFocalPoint = CAM_FOCUS
v.CameraViewUp = CAM_UP
v.CameraParallelScale = PSCALE
Render(v)
got = float(v.CameraParallelScale)
print("CAMSCALE", got, flush=True)
if abs(got - PSCALE) > 1e-9:
    raise SystemExit("REFUSE: the camera did not take (%r vs %r)" % (got, PSCALE))
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
'''


#: THE PROGRESSIVE GRID REVEAL -- Sanaa's stage 5 asks for the grid drawn "cell
#: by cell", and the 21:10Z directive accepts frame sequencing as the mechanism.
#: This reveals the REAL 4,032-cell mesh outward from the wall, which is also the
#: order a hyperbolic extrusion actually builds it in, so the sequence is not an
#: arbitrary animation over a finished object.
#:
#: NO MESHER RUNS DURING A SHOOT AND THE ACT MAY NOT IMPLY ONE DOES. This is the
#: mesh the numbers came from, revealed; it is not a mesher's live output. The
#: distinction matters because a live `blockMesh` producing a grid that is NOT
#: the grid the results came from would be a false visual -- the same class as
#: an interpolated morph frame, and refused for the same reason.
GRID_REVEAL = '''
print("SENTINEL_PY_OK", flush=True)
from paraview.simple import *
print("SENTINEL_IMPORT_OK", flush=True)
r = OpenFOAMReader(FileName=CASE)
r.MeshRegions = ["internalMesh"]
r.UpdatePipeline()
info = r.GetDataInformation()
print("CELLS", info.GetNumberOfCells(), flush=True)
clip = Clip(Input=r)
clip.ClipType = "Sphere"
clip.ClipType.Center = [CENTRE[0], CENTRE[1], 0.0]
clip.ClipType.Radius = RADIUS
clip.Invert = 1
clip.UpdatePipeline()
kept = clip.GetDataInformation().GetNumberOfCells()
print("KEPT", kept, flush=True)
v = CreateRenderView()
v.ViewSize = SIZE
v.Background = [0.12, 0.14, 0.18]
v.OrientationAxesVisibility = 0
d = Show(clip, v)
d.Representation = "Surface With Edges"
Render(v)
v.CameraParallelProjection = 1
v.CameraPosition = [CENTRE[0], 0.0, 3.0]
v.CameraFocalPoint = [CENTRE[0], 0.0, 0.0]
v.CameraViewUp = [0.0, 1.0, 0.0]
v.CameraParallelScale = PSCALE
Render(v)
got = float(v.CameraParallelScale)
print("CAMSCALE", got, flush=True)
if abs(got - PSCALE) > 1e-9:
    raise SystemExit("REFUSE: the camera did not take (%r vs %r)" % (got, PSCALE))
print("SENTINEL_RENDER_OK", flush=True)
SaveScreenshot(OUT, v)
print("SENTINEL_SAVE_OK", flush=True)
'''


def run_render(tag: str, body: str, consts: dict, out: Path) -> dict:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    scripts = OUT_ROOT / "_scripts"
    scripts.mkdir(exist_ok=True)
    if out.exists():
        out.unlink()
    head = "".join(f"{k} = {v!r}\n" for k, v in consts.items())
    sp = scripts / f"{tag}.py"
    sp.write_text(head + f"OUT = {str(out)!r}\n" + body)
    t0 = time.time()
    r = subprocess.run([str(WRAPPER), str(sp)], capture_output=True,
                       text=True, timeout=1800)
    wall = time.time() - t0
    got = {}
    for ln in r.stdout.split("\n"):
        parts = ln.split()
        if len(parts) == 2 and parts[0] in ("CELLS", "POINTS", "FACES",
                                            "CAMSCALE", "TIME", "KEPT"):
            got[parts[0].lower()] = float(parts[1])
    return {"rc": r.returncode, "wall_s": round(wall, 3),
            "core_min": round(wall / 60.0, 4), "exists": out.exists(),
            "read_back": got, "script": str(sp),
            "stderr_tail": r.stderr.strip().splitlines()[-4:]}


def main() -> int:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rec: dict = {
        "_what": "Act D ParaView render pass: geometry, meshes and fields",
        "_preregistration": "cases/dafoam/"
                            "ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md v1.1",
        "_scope": "pictures of numbers already on disk; no new physical result",
        "_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frames": [],
    }
    # ------------------------------------------------ G-PV1a / G-PV1b -------
    for gate, path, want in (("G-PV1a", WRAPPER, MD5_WRAPPER),
                             ("G-PV1b", REAL, MD5_REAL)):
        got = md5(path) if path.exists() else None
        rec[gate] = {"path": str(path), "md5_measured": got,
                     "verdict": "PASS" if got == want else "NOT A RESULT"}
        if got != want:
            (OUT_ROOT / "render.json").write_text(json.dumps(rec, indent=1))
            print(f"REFUSE: {gate}: md5 {got} != {want}")
            return 2
    print("G-PV1a PASS  G-PV1b PASS")

    section_cells = checkmesh_cells(SECTION)
    wing_cells = checkmesh_cells(WING)
    rec["checkmesh_reference"] = {"section": section_cells, "wing": wing_cells}
    print(f"G-PV4 reference from checkMesh: section {section_cells} cells, "
          f"wing {wing_cells} cells")

    jobs: list[dict] = []

    # ---- the 2D section: grid, leading edge, and the refused field ---------
    foam = str(SECTION / "case.foam")
    if not (SECTION / "case.foam").exists():
        (SECTION / "case.foam").write_text("")
    for tag, pscale, focus, field, rep in (
            ("section_grid", 0.60, [0.5, 0.0, 0.0], None, "Surface With Edges"),
            ("section_grid_leading_edge", 0.055, [0.02, 0.0, 0.0], None,
             "Surface With Edges"),
            ("polar_field_alpha18_not_converged", 0.60, [0.5, 0.0, 0.0], "U",
             "Surface")):
        jobs.append({
            "tag": tag, "body": FOAM_RENDER, "kind": "foam",
            "case": str(SECTION), "expect_cells": section_cells,
            "consts": {"CASE": foam, "SIZE": [900, 620], "PSCALE": pscale,
                       "CAM_POS": [focus[0], 0.0, 3.0], "CAM_FOCUS": focus,
                       "REPRESENTATION": rep, "FIELD": field,
                       "TIME": POLAR_TIME if field else None},
            "provenance": {
                "run_root": str(SECTION.parent), "case": str(SECTION),
                "time_dir": POLAR_TIME if field else "constant/polyMesh",
                "field": field,
                "alpha_deg": POLAR_ALPHA_DEG if field else None,
                "verdict": POLAR_VERDICT if field else None},
        })

    # ---- the progressive grid reveal, on the real mesh ---------------------
    # Radii are LOG-SPACED so the near-wall cells -- the ones a viewer actually
    # wants to see resolved -- get most of the frames, rather than the sequence
    # spending twenty frames on far-field cells that all look alike.
    import math as _math
    # r0 IS SET BY THE GATE, NOT BY TASTE. The first run started at 0.09 m and
    # G-PV7a refused six frames as blank -- measured: r = 0.16082 gives modal
    # share 0.9911 (fails 0.99), r = 0.18062 gives 0.9878 (passes). A revealed
    # annulus that small against a fixed camera is 99 % background and shows a
    # viewer nothing, so the gate and the eye agree here. 0.19 takes the first
    # passing radius with a margin rather than sitting on the threshold.
    n_reveal = 24
    r0, r1 = 0.19, 1.30
    for i in range(n_reveal):
        frac = i / (n_reveal - 1)
        radius = r0 * (r1 / r0) ** frac
        jobs.append({
            "tag": f"section_grid_reveal_{i:02d}", "body": GRID_REVEAL,
            "kind": "foam", "case": str(SECTION), "expect_cells": section_cells,
            "reveal": True,
            "consts": {"CASE": foam, "SIZE": [900, 620], "PSCALE": 0.95,
                       "CENTRE": [0.42, 0.0], "RADIUS": round(radius, 5)},
            "provenance": {"run_root": str(SECTION.parent),
                           "case": str(SECTION),
                           "time_dir": "constant/polyMesh",
                           "reveal_radius_m": round(radius, 5),
                           "note": "the solved mesh revealed; no mesher ran"},
        })

    # ---- the wing: skin, and the graded gradient painted on it -------------
    if SHAPE_FRAMES.exists():
        doc = json.loads(SHAPE_FRAMES.read_text())
        n_frames = len(doc["frames"])
        rec["morph"] = {
            "frames_in_record": n_frames,
            "major_iterations_matched": doc["_checks"]["major_iterations_matched"],
            "major_iterations_unmatched": doc["_checks"]["major_iterations_unmatched"],
            "iter0_reproduces_baseline_m": doc["_checks"]["iter0_reproduces_baseline_m"],
            "no_exaggeration": doc["_no_exaggeration"],
        }
        # THE CAMERA IS DERIVED FROM THE MESH BOUNDS, NOT HAND-TUNED. The first
        # version of this carried PSCALE 3.6 and a focus at x=3.5, guessed; the
        # wing's span is 14.04 m along Z and the frame cut the tip off. Hand
        # constants cannot know the geometry, and a frame that silently crops
        # the subject passes every gate in this item -- it is not blank, its
        # provenance is intact and its cell count is right. Only looking at it
        # catches that, so the framing is computed instead.
        #
        # Planform view: looking down -Y (the thickness direction), span across
        # the frame and chord up it, with a 4 % margin.
        _b = doc["base_vertices"]
        _xs = [q[0] for q in _b]; _ys = [q[1] for q in _b]; _zs = [q[2] for q in _b]
        _cx, _cz = (min(_xs) + max(_xs)) / 2, (min(_zs) + max(_zs)) / 2
        _size = [900, 620]
        _aspect = _size[0] / _size[1]
        _half_v = (max(_xs) - min(_xs)) / 2          # chord, vertical in frame
        _half_h = (max(_zs) - min(_zs)) / 2          # span, horizontal
        _pscale = max(_half_v, _half_h / _aspect) * 1.04
        cam = {"CAM_POS": [_cx, max(_ys) + 40.0, _cz],
               "CAM_FOCUS": [_cx, 0.0, _cz],
               "CAM_UP": [1.0, 0.0, 0.0], "PSCALE": round(_pscale, 4),
               "SIZE": _size}
        jobs.append({"tag": "wing_skin_mesh", "body": SURFACE_RENDER,
                     "kind": "surface", "case": str(SHAPE_FRAMES),
                     "consts": dict(cam, FRAMES=str(SHAPE_FRAMES),
                                    FRAME_INDEX=None, SCALAR_KEY=None,
                                    SCALAR_NAME="none",
                                    REPRESENTATION="Surface With Edges"),
                     "provenance": {"source": str(SHAPE_FRAMES),
                                    "surface": "baseline stored vertices"}})
        jobs.append({"tag": "wing_gradient_on_skin", "body": SURFACE_RENDER,
                     "kind": "surface", "case": str(SHAPE_FRAMES),
                     "consts": dict(cam, FRAMES=str(SHAPE_FRAMES),
                                    FRAME_INDEX=None, SCALAR_KEY="gradient",
                                    SCALAR_NAME="dCD_dn",
                                    REPRESENTATION="Surface"),
                     "provenance": {"source": str(SHAPE_FRAMES),
                                    "field": "gradient (stored)"}})
        # THE MORPH: every stored frame, none interpolated (G-PV5).
        for i in range(n_frames):
            jobs.append({
                "tag": f"wing_morph_{i:03d}", "body": SURFACE_RENDER,
                "kind": "surface", "case": str(SHAPE_FRAMES), "morph": True,
                "consts": dict(cam, FRAMES=str(SHAPE_FRAMES), FRAME_INDEX=i,
                               SCALAR_KEY=None, SCALAR_NAME="none",
                               REPRESENTATION="Surface With Edges"),
                "provenance": {"source": str(SHAPE_FRAMES),
                               "major_iteration": doc["frames"][i]["iter"],
                               "surface": "stored, not interpolated"}})

    # ------------------------------------------------------------ render ----
    fails: list[str] = []
    total = 0.0
    for job in jobs:
        out = OUT_ROOT / f"{job['tag']}.png"
        res = run_render(job["tag"], job["body"], job["consts"], out)
        total += res["core_min"]
        entry = {"tag": job["tag"], "provenance": job["provenance"], **res}
        if res["rc"] != 0 or not res["exists"]:
            entry["verdict"] = "NOT A RESULT"
            fails.append(f"{job['tag']}: did not render (rc={res['rc']}) "
                         f"{res['stderr_tail'][-1] if res['stderr_tail'] else ''}")
            rec["frames"].append(entry)
            print(f"  [FAIL] {job['tag']}")
            continue
        c = content(out)
        entry["G-PV7a"] = dict(c, verdict="NOT A RESULT" if is_blank(c) else "PASS")
        if is_blank(c):
            fails.append(f"{job['tag']}: G-PV7a blank frame")
        # G-PV4, only where a checkMesh reference exists for this case.
        if job.get("expect_cells"):
            got_cells = int(res["read_back"].get("cells", -1))
            ok = got_cells == job["expect_cells"]
            entry["G-PV4"] = {"paraview_cells": got_cells,
                              "checkmesh_cells": job["expect_cells"],
                              "verdict": "PASS" if ok else "GATE FAIL"}
            if not ok:
                fails.append(f"{job['tag']}: G-PV4 {got_cells} != "
                             f"{job['expect_cells']}")
        entry["verdict"] = "PASS" if not is_blank(c) else "NOT A RESULT"
        rec["frames"].append(entry)
        if not job.get("morph") and not job.get("reveal"):
            print(f"  [ok  ] {job['tag']:<38} {c['distinct_colours']:>6} colours, "
                  f"modal {c['modal_share']:.4f}")

    reveal = [f for f in rec["frames"] if f["tag"].startswith("section_grid_reveal_")]
    if reveal:
        good = sum(1 for f in reveal if f.get("verdict") == "PASS")
        print(f"  [ok  ] section_grid_reveal                   "
              f"{good}/{len(reveal)} frames, real mesh revealed outward")
        if good != len(reveal):
            fails.append(f"grid reveal: {len(reveal) - good} frame(s) failed")

    morph = [f for f in rec["frames"] if f["tag"].startswith("wing_morph_")]
    if morph:
        good = sum(1 for f in morph if f.get("verdict") == "PASS")
        print(f"  [ok  ] wing_morph                            "
              f"{good}/{len(morph)} frames, all stored surfaces")
        if rec.get("morph", {}).get("major_iterations_unmatched") != 0:
            fails.append("G-PV5: the morph record has unmatched major iterations")
        if good != len(morph):
            fails.append(f"G-PV5: {len(morph) - good} morph frame(s) failed")

    rec["core_min_total"] = round(total, 3)
    rec["VERDICT"] = "NOT A RESULT" if fails else "PASS"
    rec["_not_rendered"] = [
        "A converged-angle field for the polar act. The sweep re-solves IN "
        "PLACE, so only the final angle's field survives on disk; the "
        "converged branch's fields were overwritten. Rendering a neighbouring "
        "angle and labelling it converged would be a fabricated provenance, so "
        "the gap is reported instead."]
    (OUT_ROOT / "render.json").write_text(json.dumps(rec, indent=1))

    print(f"\ncost: {rec['core_min_total']} core-min, {len(rec['frames'])} frames")
    if fails:
        for f in fails[:12]:
            print(f"REFUSE: {f}")
        return 1
    print(f"PASS  {len(rec['frames'])} frames, every one graded and provenanced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
