#!/usr/bin/env python3
"""DRIVAER R1 -- measure the mesh family.  Reads meshes, not targets.

FOUR THINGS IT REFUSES TO DO
 1. It never takes a cell count from a target, a filename or a dict.  The count
    comes from the checkMesh stdout AND is cross-checked against the owner /
    neighbour topology read independently; a mismatch is a refusal.
 2. It never reads dimensionality from the "solution (non-empty)" line.  That
    line counts a wedge direction as present and so certifies a wedge case as
    3D.  Only "Mesh has N geometric (non-empty/wedge) directions" is matched,
    literally.
 3. It never forms a verdict from `"Mesh OK." in out` or from checkMesh's rc.
    MEASURED on this very case: checkMesh returned rc=1 on a mesh with 52,165
    negative-volume cells and rc=0 on a mesh that FAILED 3 checks.  The rc is
    unreliable in BOTH directions.  The verdict is parsed from the
    "Failed N mesh checks" line, and its ABSENCE is what a clean mesh looks like.
 4. It never trusts one reader.  Face areas and cell volumes are recomputed from
    points/faces/owner/neighbour by the divergence theorem, and the reader is
    planted against a pure blockMesh whose every cell volume is known in closed
    form.  A reader not shown able to see the right answer is not evidence.
"""
from __future__ import annotations
import json, re, sys, argparse
from pathlib import Path
import numpy as np

GEOM_DIR_RE = re.compile(r"^\s*Mesh has (\d+) geometric \(non-empty/wedge\) directions")
FAILED_RE = re.compile(r"^Failed (\d+) mesh checks\.")
CELLS_RE = re.compile(r"^\s*cells:\s+(\d+)")


def strip(txt: bytes) -> bytes:
    txt = re.sub(rb"/\*.*?\*/", b" ", txt, flags=re.S)
    txt = re.sub(rb"//[^\n]*", b" ", txt)
    i = txt.index(b"FoamFile"); j = txt.index(b"}", i)
    return txt[j + 1:]


def read_vec(p):
    b = strip(Path(p).read_bytes())
    m = re.search(rb"(\d+)\s*\(", b); n = int(m.group(1))
    body = b[m.end():b.rindex(b")")]
    return np.fromstring(body.replace(b"(", b" ").replace(b")", b" ").decode(),
                         sep=" ").reshape(n, 3)


def read_labels(p):
    b = strip(Path(p).read_bytes())
    m = re.search(rb"(\d+)\s*\(", b)
    body = b[m.end():b.rindex(b")")]
    return np.fromstring(body.decode(), sep=" ").astype(np.int64)


def read_faces(p):
    b = strip(Path(p).read_bytes())
    m = re.search(rb"(\d+)\s*\(", b); n = int(m.group(1))
    body = b[m.end():b.rindex(b")")].decode()
    toks = np.fromstring(body.replace("(", " ").replace(")", " "), sep=" ").astype(np.int64)
    out = []; i = 0
    for _ in range(n):
        k = toks[i]; out.append(toks[i + 1:i + 1 + k]); i += 1 + k
    return out


def read_boundary(p):
    txt = strip(Path(p).read_bytes()).decode()
    txt = txt[txt.index("("):]
    pats = {}
    for m in re.finditer(r"(\S+)\s*\{([^}]*)\}", txt):
        name, body = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", body)
        sf = re.search(r"startFace\s+(\d+)\s*;", body)
        ty = re.search(r"type\s+(\S+)\s*;", body)
        if nf and sf:
            pats[name] = dict(nFaces=int(nf.group(1)), startFace=int(sf.group(1)),
                              type=ty.group(1) if ty else None)
    return pats


def geometry(root: Path):
    pm = root / "constant" / "polyMesh"
    P = read_vec(pm / "points"); F = read_faces(pm / "faces")
    own = read_labels(pm / "owner"); nei = read_labels(pm / "neighbour")
    ncell = int(max(own.max(), nei.max())) + 1
    nf = len(F)
    Sf = np.zeros((nf, 3)); Cf = np.zeros((nf, 3))
    for i, f in enumerate(F):
        pts = P[f]; c0 = pts.mean(0)
        a = pts; b = np.roll(pts, -1, axis=0)
        tri = np.cross(a - c0, b - c0) * 0.5
        at = np.linalg.norm(tri, axis=1)
        Sf[i] = tri.sum(0)
        tot = at.sum()
        Cf[i] = ((a + b + c0) / 3.0 * at[:, None]).sum(0) / tot if tot > 0 else c0
    V = np.zeros(ncell)
    np.add.at(V, own, (Cf * Sf).sum(1))
    np.add.at(V, nei, -(Cf[:len(nei)] * Sf[:len(nei)]).sum(1))
    V /= 3.0
    return dict(points=len(P), faces=nf, cells=ncell, internal=len(nei),
                area=np.linalg.norm(Sf, axis=1), vol=V,
                boundary=read_boundary(pm / "boundary"))


def parse_checkmesh(log: Path):
    out = dict(path=str(log), geometric_directions=None, failed_checks=None,
               cells=None, metrics={})
    txt = log.read_text(errors="replace")
    for line in txt.splitlines():
        m = GEOM_DIR_RE.match(line)
        if m and out["geometric_directions"] is None:
            out["geometric_directions"] = int(m.group(1))
        m = FAILED_RE.match(line)
        if m:
            out["failed_checks"] = int(m.group(1))
        m = CELLS_RE.match(line)
        if m and out["cells"] is None:
            out["cells"] = int(m.group(1))
    for key, pat in (
        ("max_non_ortho", r"Mesh non-orthogonality Max: ([\d.eE+-]+) average: ([\d.eE+-]+)"),
        ("max_skewness", r"Max skewness = ([\d.eE+-]+)"),
        ("max_aspect", r"Max aspect ratio: ([\d.eE+-]+)"),
        ("min_vol", r"Minimum negative volume: (-?[\d.eE+-]+)"),
        ("min_face_area", r"Minimum face area = ([\d.eE+-]+)"),
    ):
        m = re.search(pat, txt)
        if m:
            out["metrics"][key] = float(m.group(1).rstrip("."))
            if key == "max_non_ortho":
                out["metrics"]["avg_non_ortho"] = float(m.group(2).rstrip("."))
    for key, pat in (
        ("n_negative_volume_cells", r"Number of negative volume cells: (\d+)"),
        ("n_severely_non_ortho", r"Number of severely non-orthogonal \(> 70 degrees\) faces: (\d+)"),
        ("n_concave_cells", r"Concave cells \(using face planes\) found, number of cells: (\d+)"),
        ("n_low_determinant", r"Cells with small determinant \(< 0.001\) found, number of cells: (\d+)"),
        ("n_skew_faces", r"([\d]+) highly skew faces detected"),
    ):
        m = re.search(pat, txt)
        out["metrics"][key] = int(m.group(1)) if m else 0
    out["mesh_ok_substring_present"] = ("Mesh OK." in txt)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="+", required=True,
                    help="name=path triples, coarse first")
    ap.add_argument("--stl-solids", required=True,
                    help="solid_bbox.json: per-solid STL areas")
    ap.add_argument("--out", required=True)
    ap.add_argument("--plant", required=True,
                    help="a pure-blockMesh case whose cells are known cubes")
    ap.add_argument("--plant-h", type=float, required=True)
    a = ap.parse_args()

    # ---- RULE 3: the reader is planted before it is believed ---------------
    pg = geometry(Path(a.plant))
    h = a.plant_h
    dv = float(np.abs(pg["vol"] - h ** 3).max())
    da = float(np.abs(pg["area"] - h ** 2).max())
    if dv > 1e-9 * h ** 3 or da > 1e-9 * h ** 2:
        raise SystemExit(f"REFUSE: planted control FAILED -- on a pure blockMesh of "
                         f"cubes of side {h} the reader must return volume {h**3} and "
                         f"face area {h**2} exactly; worst volume error {dv:.3e}, "
                         f"worst area error {da:.3e}.  A reader that cannot read a "
                         f"mesh it knows the answer to cannot judge one it does not.")
    plant = dict(case=a.plant, h=h, cells=pg["cells"],
                 worst_volume_error=dv, worst_area_error=da, passed=True)
    print(f"PLANTED CONTROL PASSED: {pg['cells']} cubes of side {h}; worst volume "
          f"error {dv:.3e} m3, worst face-area error {da:.3e} m2")

    stl = {r["solid"]: r for r in json.load(open(a.stl_solids))}
    sane = {re.sub(r"[^A-Za-z0-9_]", "_", k): v for k, v in stl.items()}

    levels = []
    for spec in a.levels:
        name, path = spec.split("=", 1)
        root = Path(path)
        cm_full = parse_checkmesh(root / "log.checkMeshFull")
        cm_plain = parse_checkmesh(root / "log.checkMeshPlain")
        g = geometry(root)
        if cm_full["cells"] != g["cells"]:
            raise SystemExit(f"REFUSE {name}: checkMesh says {cm_full['cells']} cells, "
                             f"owner/neighbour topology says {g['cells']}")
        # per-patch wall evidence: the cusp limb
        patches = {}
        for pn, pb in g["boundary"].items():
            if pn not in sane:
                continue
            s, n = pb["startFace"], pb["nFaces"]
            amesh = float(g["area"][s:s + n].sum())
            astl = sane[pn]["area"]
            patches[pn] = dict(nFaces=n, area_mesh=amesh, area_stl=astl,
                               area_ratio=(amesh / astl) if astl else None)
        levels.append(dict(
            name=name, path=str(root),
            cells=g["cells"], faces=g["faces"], points=g["points"],
            geometric_directions=cm_full["geometric_directions"],
            failed_checks_full=cm_full["failed_checks"],
            failed_checks_plain=cm_plain["failed_checks"],
            mesh_ok_substring_full=cm_full["mesh_ok_substring_present"],
            mesh_ok_substring_plain=cm_plain["mesh_ok_substring_present"],
            metrics_full=cm_full["metrics"],
            indep_min_cell_volume=float(g["vol"].min()),
            indep_n_nonpositive_cells=int((g["vol"] <= 0).sum()),
            indep_max_face_area=float(g["area"].max()),
            indep_total_volume=float(g["vol"].sum()),
            patches=patches,
            n_wall_patches=len(patches),
            min_patch_faces=min((p["nFaces"] for p in patches.values()), default=None),
            min_patch_area_ratio=min((p["area_ratio"] for p in patches.values()
                                      if p["area_ratio"] is not None), default=None),
            max_patch_area_ratio=max((p["area_ratio"] for p in patches.values()
                                      if p["area_ratio"] is not None), default=None),
        ))

    # delivered refinement ratios against the r^3 law
    ratios = []
    for i in range(1, len(levels)):
        R = levels[i]["cells"] / levels[i - 1]["cells"]
        ratios.append(dict(step=f'{levels[i-1]["name"]}->{levels[i]["name"]}',
                           cell_ratio=R, r_effective=R ** (1.0 / 3.0)))
    rep = dict(planted_control=plant, levels=levels, ratios=ratios,
               nominal_h_ratio=2.0,
               nominal_cell_ratio_if_pure_r3=8.0,
               note=("h_bg is halved exactly between levels and every refinement "
                     "level, box and absolute size is held fixed, so a pure "
                     "volume-filled mesh would deliver 8x and a pure "
                     "surface-banded mesh 4x; the delivered ratio lands between "
                     "and its cube root is the r that must be registered."))
    Path(a.out).write_text(json.dumps(rep, indent=1))

    print("LEVEL      cells      faces  geomDir  failedFull failedPlain  maxNonOrtho  maxSkew  negCells(indep)")
    for L in levels:
        m = L["metrics_full"]
        print("%-8s %9d %10d %8s %11s %11s %12.2f %8.2f %10d" % (
            L["name"], L["cells"], L["faces"], L["geometric_directions"],
            L["failed_checks_full"], L["failed_checks_plain"],
            m.get("max_non_ortho", float("nan")), m.get("max_skewness", float("nan")),
            L["indep_n_nonpositive_cells"]))
    print()
    for r in ratios:
        print("  %-18s cell ratio %.4f   r_effective %.4f   (r^3 law would give 8.0000 / 2.0000)"
              % (r["step"], r["cell_ratio"], r["r_effective"]))
    print()
    for L in levels:
        print("  %-8s wall patches %d  min faces on a patch %s  area ratio mesh/STL  min %.4f  max %.4f"
              % (L["name"], L["n_wall_patches"], L["min_patch_faces"],
                 L["min_patch_area_ratio"], L["max_patch_area_ratio"]))
    print(f"\nwritten: {a.out}")


if __name__ == "__main__":
    main()
