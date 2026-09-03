#!/usr/bin/env python3
"""S2 -- BLOCKING PHYSICS FIX: give R1-M0's pyHyp mesh its boundary identity back.

THE DEFECT.  verification/runs/RUNG1_M6_runs/M0_pyhyp_admission/foam/constant/polyMesh/
boundary declares ONE patch: `defaultFaces`, type `wall`, 9,376 faces.  The wing, the
symmetry plane and the 12-chord farfield are fused into a single wall, so the domain is
a CLOSED ALL-WALL BOX with no inlet, no outlet and no symmetry condition.  Sanaa's
2026-09-03 ~21:00Z ruling names exactly this class -- "no outlet, inconsistent boundary
conditions" -- as a setup that "will diverge and teach nothing", a BLOCKING PHYSICS FIX
that jumps every queue and needs no petition.  Her ~20:00Z taxonomy lists "wrong patch
identity on a mesh" first among blocking physics fixes.

The cause is the converter, not the grid: `plot3dToFoam` reads a structured PLOT3D file
that carries no boundary-condition metadata, so it can only emit `defaultFaces`.
RUNG0_MESH_IMPORT_PREREGISTRATION section 4 drops Plot3D for this reason, having measured
the same destruction on M6I L1 (983,040 cells imported as one 27,648-face wall).

WHAT THIS IS NOT.  This does not touch geometry.  No point moves.  checkMesh's
non-orthogonality, skewness, aspect ratio and volume readings are properties of the cell
geometry and MUST come out identical afterwards -- and that identity is asserted below as
the proof that this was a re-labelling and not a re-meshing.  In particular the
88.88926674 degree maximum stands untouched; it is a recorded prediction, not a thing
this fix erases.

THE CLASSIFICATION, AND WHY IT IS NOT A GUESS.  Measured on the 9,376 boundary face
centres of the mesh itself:

  * symmetry -- 6,256 faces at z = 0 EXACTLY (max |z| over the set = 0.000e+00, not a
    tolerance hit).  6,256 / 92 extrusion layers = 68.0 exactly, i.e. the wing surface
    has 68 edges on the symmetry plane.  An integer, not a rounding.
  * the remaining 3,120 faces split at a MEASURED GAP 8.486384 units wide: the outermost
    is at radius 1.655014 and the innermost of the rest at 10.141397.  There is nothing
    in between.  A threshold anywhere in that gap gives the same answer.
  * wall 1,560 and farfield 1,560 -- EQUAL, which a hyperbolic extrusion requires: the
    outer surface is the inner surface marched outward and has the same face topology.
    That equality is an independent check on the split and is asserted below.

pyHyp's own options in work/genWingMesh_R1M0.py corroborate every label:
`"families": "wall"`, `"outerFaceBC": "farfield"`, `"unattachedEdgesAreSymmetry": True`,
`marchDist 12.0` (the farfield radius measured here is 10.14-12.89).

THE ORIGINAL IS NOT TOUCHED.  This writes a NEW case beside it and copies the polyMesh in.
MOVE, never delete.

NO BARE `assert` (L-332): `python3 -O` deletes asserts, so every check here raises.
"""
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

SRC = "/home/ubuntu/Certonomous/verification/runs/RUNG1_M6_runs/M0_pyhyp_admission/foam"
DST = "/home/ubuntu/Certonomous/verification/runs/RUNG1_M6_runs/M2_M0_patch_identity/foam"
BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
SYM_TOL = 1e-9

PATCHES = [("wing", "wall", 1), ("symmetry", "symmetry", 0), ("farfield", "patch", 2)]


def die(msg):
    raise SystemExit(f"REFUSED: {msg}")


def block(pm, fn):
    t = open(os.path.join(pm, fn)).read()
    t = t[t.index("// * * *"):]
    m = re.search(r"^\s*(\d+)\s*\n\(", t, re.M)
    if not m:
        die(f"cannot find the list header in {fn}")
    return t[m.end():t.index("\n)", m.end())]


def classify(pm):
    pts = np.fromstring(block(pm, "points").replace("(", " ").replace(")", " "),
                        sep=" ").reshape(-1, 3)
    faces = [[int(x) for x in ln.strip().split("(", 1)[1].rstrip(")").split()]
             for ln in block(pm, "faces").strip().split("\n") if ln.strip()]
    m = re.search(r"nInternalFaces:(\d+)", open(os.path.join(pm, "owner")).read())
    if not m:
        die("owner carries no nInternalFaces note")
    n_int = int(m.group(1))
    cen = np.array([pts[f].mean(axis=0) for f in faces[n_int:]])
    r = np.linalg.norm(cen, axis=1)
    sym = np.abs(cen[:, 2]) < SYM_TOL
    off = ~sym
    lo = np.sort(r[off])
    gaps = np.diff(lo)
    i = int(np.argmax(gaps))
    cut = (lo[i] + lo[i + 1]) / 2.0
    cls = np.where(sym, 0, np.where(r <= cut, 1, 2))
    ev = {
        "n_boundary_faces": int(len(cen)),
        "n_internal_faces": n_int,
        "symmetry_faces": int((cls == 0).sum()),
        "wall_faces": int((cls == 1).sum()),
        "farfield_faces": int((cls == 2).sum()),
        "symmetry_plane_max_abs_z": float(np.abs(cen[sym][:, 2]).max()),
        "gap_lower_radius": float(lo[i]),
        "gap_upper_radius": float(lo[i + 1]),
        "gap_width": float(gaps[i]),
        "cut_radius_used": float(cut),
        "wall_radius_range": [float(r[cls == 1].min()), float(r[cls == 1].max())],
        "farfield_radius_range": [float(r[cls == 2].min()), float(r[cls == 2].max())],
        "extrusion_layers": 92,
        "symmetry_faces_per_layer": float((cls == 0).sum() / 92.0),
    }
    # explicit guards, never asserts (L-332)
    if ev["wall_faces"] != ev["farfield_faces"]:
        die(f"wall {ev['wall_faces']} != farfield {ev['farfield_faces']}; a hyperbolic "
            f"extrusion must give equal inner and outer face counts. The split is wrong.")
    if ev["gap_width"] < 1.0:
        die(f"radius gap is only {ev['gap_width']:.6f}; the wall/farfield split is not "
            f"unambiguous and this script will not guess.")
    if ev["symmetry_plane_max_abs_z"] > SYM_TOL:
        die("a face classified as symmetry is off the z=0 plane")
    if sum((cls == k).sum() for k in (0, 1, 2)) != len(cen):
        die("classification does not partition the boundary faces")
    return cls, ev, n_int


def write_set(pm, name, idx, n_int):
    d = os.path.join(pm, "sets")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name), "w") as f:
        f.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                "    class       faceSet;\n    location    \"constant/polyMesh/sets\";\n"
                f"    object      {name};\n}}\n\n")
        f.write(f"{len(idx)}\n(\n")
        f.write("\n".join(str(int(i) + n_int) for i in idx))
        f.write("\n)\n")


def read_quality(log):
    t = open(log).read()

    def g(p):
        m = re.search(p, t, re.M)
        return m.group(1) if m else None
    return {
        "cells": g(r"^\s*cells:\s*(\d+)"),
        "max_non_orthogonality": g(r"Mesh non-orthogonality Max:\s*([0-9.eE+-]*[0-9])"),
        "avg_non_orthogonality": g(r"Max:\s*[0-9.eE+-]*[0-9]\s*average:\s*([0-9.eE+-]*[0-9])"),
        "severe_non_ortho_faces": g(r"non-orthogonal \(> 70 degrees\) faces:\s*(\d+)"),
        "max_skewness": g(r"Max skewness\s*[=:]\s*([0-9.eE+-]*[0-9])"),
        "max_aspect_ratio": (g(r"Max aspect ratio\s*=\s*([0-9.eE+-]*[0-9])")
                             or g(r"Max aspect ratio:\s*([0-9.eE+-]*[0-9])")),
        "min_cell_volume": g(r"Min volume\s*=\s*([0-9.eE+-]*[0-9])"),
        "max_cell_volume": g(r"Max volume\s*=\s*([0-9.eE+-]*[0-9])"),
    }


def foam(cmd, cwd):
    return subprocess.run(["bash", "-c", f"source {BASHRC} >/dev/null 2>&1; {cmd}"],
                          cwd=cwd, capture_output=True, text=True)


def main():
    if os.path.exists(DST):
        die(f"{DST} already exists -- guard refuses to overwrite an existing case")
    if not os.path.isdir(SRC):
        die(f"source case ABSENT: {SRC}")
    os.makedirs(DST)
    shutil.copytree(os.path.join(SRC, "constant"), os.path.join(DST, "constant"))
    shutil.copytree(os.path.join(SRC, "system"), os.path.join(DST, "system"))
    pm = os.path.join(DST, "constant", "polyMesh")

    cls, ev, n_int = classify(pm)
    for name, _, code in PATCHES:
        write_set(pm, f"{name}Faces", np.where(cls == code)[0], n_int)

    with open(os.path.join(DST, "system", "createPatchDict"), "w") as f:
        f.write("FoamFile{version 2.0;format ascii;class dictionary;"
                "object createPatchDict;}\npointSync false;\npatches\n(\n")
        for name, typ, _ in PATCHES:
            f.write(f"    {{ name {name}; patchInfo {{ type {typ}; }} "
                    f"constructFrom set; set {name}Faces; }}\n")
        f.write(");\n")

    r = foam("createPatch -overwrite > log.createPatch 2>&1", DST)
    if r.returncode != 0:
        die(f"createPatch rc={r.returncode}; see {DST}/log.createPatch")
    r = foam("checkMesh > log.checkMesh 2>&1", DST)
    if r.returncode != 0:
        die(f"checkMesh rc={r.returncode}; see {DST}/log.checkMesh")

    before = read_quality(os.path.join(SRC, "log.checkMesh"))
    after = read_quality(os.path.join(DST, "log.checkMesh"))
    missing = ([f"before.{k}" for k, v in before.items() if v is None]
               + [f"after.{k}" for k, v in after.items() if v is None])
    if missing:
        die("the quality reader returned None for " + ", ".join(missing) + ". A field "
            "unread on BOTH sides would compare equal and certify an identity the "
            "reader never established. Planted-zero rule: refusing.")
    identical = before == after

    bnd = open(os.path.join(pm, "boundary")).read()
    got = re.findall(r"^\s{4}(\w+)\s*\n\s*\{(.*?)\}", bnd, re.M | re.S)
    got = [(n, re.search(r"type\s+(\w+);", b).group(1),
            re.search(r"nFaces\s+(\d+);", b).group(1)) for n, b in got]
    out = {
        "fix": "S2 -- BLOCKING PHYSICS FIX: boundary identity restored to R1-M0",
        "THIS_IS_NOT_A_GRADED_RUN": True,
        "verdict": "NONE -- no verdict of the fixed vocabulary attaches to a mesh repair.",
        "source_case_UNTOUCHED": SRC,
        "repaired_case": DST,
        "defect": "single patch `defaultFaces` type wall, 9376 faces -- a closed "
                  "all-wall box with no inlet, no outlet and no symmetry condition",
        "cause": "plot3dToFoam: PLOT3D carries no boundary-condition metadata",
        "classification_evidence": ev,
        "patches_after": [{"patch": n, "openfoam_type": t, "nFaces": int(c)}
                          for n, t, c in got],
        "checkMesh_before": before,
        "checkMesh_after": after,
        "geometry_UNCHANGED_by_the_repair": identical,
        "what_this_does_NOT_change": (
            "No point moved. The 88.88926674 degree maximum non-orthogonality, its 206 "
            "severe faces and the 35820.55869 max aspect ratio stand exactly as measured "
            "and remain recorded predictions."),
    }
    dst_json = os.path.join(os.path.dirname(DST), "M2_PATCH_IDENTITY.json")
    json.dump(out, open(dst_json, "w"), indent=2, sort_keys=True)
    if not identical:
        die(f"geometry CHANGED across a re-labelling: {before} -> {after}. "
            f"Record at {dst_json}")
    print(f"WROTE {dst_json}")
    print("patches after:", [(n, t, c) for n, t, c in got])
    print("geometry identical before/after:", identical)
    print("  max non-orth:", after["max_non_orthogonality"],
          " skew:", after["max_skewness"], " cells:", after["cells"])


if __name__ == "__main__":
    main()
