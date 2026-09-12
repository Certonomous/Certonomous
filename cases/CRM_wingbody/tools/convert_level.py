#!/usr/bin/env python3
"""
convert_level.py -- convert one DPW-6 committee UGRID level to an OpenFOAM polyMesh,
recording every invariant needed to believe the result.

Patch identity for the Boeing Babcock family, which publishes no .mapbc, is NOT inferred
from geometry alone: the wall tags are identified by matching their wetted area against the
NASA GeoLab family's DOCUMENTED .mapbc components for the same aircraft (agreement 0.027%
on the fuselage and 0.001% on the wing). The geometric classifier used for Sym/Far was
validated blind against GeoLab's 45 documented tags, 45/45.

Units: the grid stays in its native INCHES through the msh; the conversion to metres is a
single explicit transformPoints scale of exactly 0.0254, applied once, at import, and the
volume is checked on both sides of it.
"""
import os, sys, subprocess, json, argparse, hashlib, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ugrid_to_gmsh import read_ugrid, write_msh, classify_tags, face_areas_centroids

INCH = 0.0254
FOAM = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

BABCOCK_TAGS = {1: "body", 2: "wing", 3: "farfield", 4: "farfield", 5: "symmetry"}


def sha256(path, blk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(blk), b""):
            h.update(b)
    return h.hexdigest()


def volume_by_divergence(g):
    nodes = g["nodes"]; tot = 0.0
    for conn in (g["tri"], g["quad"]):
        if not len(conn):
            continue
        pts = nodes[conn - 1]
        if conn.shape[1] == 3:
            nv = 0.5 * np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
            tot += np.einsum("ij,ij->i", pts.mean(1), nv).sum()
        else:
            for a, b, c in ((0, 1, 2), (0, 2, 3)):
                nv = 0.5 * np.cross(pts[:, b] - pts[:, a], pts[:, c] - pts[:, a])
                tot += np.einsum("ij,ij->i", (pts[:, a] + pts[:, b] + pts[:, c]) / 3.0, nv).sum()
    return tot / 3.0


def run(cmd, cwd, log):
    with open(log, "w") as lf:
        r = subprocess.run(["bash", "-lc", f"source {FOAM} >/dev/null 2>&1; cd {cwd} && {cmd}"],
                           stdout=lf, stderr=subprocess.STDOUT)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ugrid", required=True)
    ap.add_argument("--case", required=True)
    ap.add_argument("--tags", default="babcock")
    ap.add_argument("--keep-msh", action="store_true")
    a = ap.parse_args()

    rec = {"ugrid": a.ugrid, "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    t0 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] reading {os.path.basename(a.ugrid)}", flush=True)
    g = read_ugrid(a.ugrid)
    ncell = len(g["tet"]) + len(g["pyr"]) + len(g["prz"]) + len(g["hex"])
    rec.update(nodes=len(g["nodes"]), cells=ncell, tet=len(g["tet"]), pyr=len(g["pyr"]),
               prz=len(g["prz"]), hex=len(g["hex"]),
               boundary_faces=len(g["tri"]) + len(g["quad"]),
               file_size=g["size"], predicted_size=g["predicted"],
               size_diff=g["size"] - g["predicted"], sha256=sha256(a.ugrid))
    print(f"  nodes {rec['nodes']:,} cells {ncell:,} bfaces {rec['boundary_faces']:,} "
          f"size {rec['file_size']:,} (predicted {rec['predicted_size']:,}, diff {rec['size_diff']})", flush=True)

    st, planarity, symtol, bb = classify_tags(g)
    rec["symmetry_planarity_in"] = planarity
    rec["symmetry_tolerance_in"] = symtol
    rec["bbox_in"] = bb.tolist()
    V_in = volume_by_divergence(g)
    rec["winding"] = "inward" if V_in < 0 else "outward"
    rec["volume_divergence_in3"] = abs(V_in)
    print(f"  symmetry planarity {planarity:.3e} in, tolerance {symtol:.3e} in, winding {rec['winding']}", flush=True)
    print(f"  domain volume by divergence over SOURCE boundary = {abs(V_in):.9e} in^3", flush=True)

    patch_of_tag = dict(BABCOCK_TAGS) if a.tags == "babcock" else \
        {t: {"Sym": "symmetry", "Far": "farfield", "WALL": "wall"}[s["class"]] for t, s in st.items()}
    rec["patch_of_tag"] = {str(k): v for k, v in patch_of_tag.items()}
    areas = {}
    at, _ = face_areas_centroids(g["nodes"], g["tri"]) if len(g["tri"]) else (np.zeros(0), None)
    aq, _ = face_areas_centroids(g["nodes"], g["quad"]) if len(g["quad"]) else (np.zeros(0), None)
    allA = np.concatenate([at, aq])
    for t in sorted(st):
        areas.setdefault(patch_of_tag[t], 0.0)
        areas[patch_of_tag[t]] += float(allA[g["tags"] == t].sum())
    rec["source_patch_area_in2"] = areas
    for k, v in areas.items():
        print(f"    patch {k:<10} source area {v:,.1f} in^2", flush=True)

    os.makedirs(a.case, exist_ok=True)
    for d in ("system", "constant"):
        os.makedirs(os.path.join(a.case, d), exist_ok=True)
    open(os.path.join(a.case, "system", "controlDict"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}\n'
        'application rhoSimpleFoam; startFrom startTime; startTime 0; stopAt endTime;\n'
        'endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;\n')
    open(os.path.join(a.case, "system", "fvSchemes"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object fvSchemes;}\n'
        'ddtSchemes{default steadyState;} gradSchemes{default Gauss linear;}\n'
        'divSchemes{default none;} laplacianSchemes{default Gauss linear corrected;}\n')
    open(os.path.join(a.case, "system", "fvSolution"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}\nsolvers{}\n')

    msh = os.path.join(a.case, "mesh.msh")
    print(f"[{time.strftime('%H:%M:%S')}] writing gmsh msh ...", flush=True)
    info = write_msh(g, msh, patch_of_tag, progress=True)
    rec["msh_bytes"] = os.path.getsize(msh)
    rec["cells_flipped_for_orientation"] = info["flipped"]
    print(f"  msh {rec['msh_bytes']:,} bytes; cells flipped for orientation {info['flipped']}", flush=True)
    del g

    print(f"[{time.strftime('%H:%M:%S')}] gmshToFoam ...", flush=True)
    rc = run(f"gmshToFoam {msh}", a.case, os.path.join(a.case, "log.gmshToFoam"))
    rec["rc_gmshToFoam"] = rc
    if rc != 0:
        json.dump(rec, open(os.path.join(a.case, "conversion_record.json"), "w"), indent=2)
        print("gmshToFoam FAILED", flush=True); sys.exit(2)

    print(f"[{time.strftime('%H:%M:%S')}] transformPoints scale {INCH} (inches -> metres) ...", flush=True)
    rc = run(f"transformPoints -scale {INCH}", a.case,
             os.path.join(a.case, "log.transformPoints"))
    rec["rc_transformPoints"] = rc
    if rc != 0:
        json.dump(rec, open(os.path.join(a.case, "conversion_record.json"), "w"), indent=2)
        print("transformPoints FAILED -- mesh would stay in inches; refusing", flush=True)
        sys.exit(3)

    print(f"[{time.strftime('%H:%M:%S')}] checkMesh ...", flush=True)
    rc = run("checkMesh -allGeometry -allTopology", a.case, os.path.join(a.case, "log.checkMesh"))
    rec["rc_checkMesh"] = rc
    cm = open(os.path.join(a.case, "log.checkMesh")).read()
    import re
    def grab(p, d=None):
        m = re.search(p, cm); return m.group(1) if m else d
    rec["foam_cells"] = grab(r"cells:\s+(\d+)")
    rec["foam_faces"] = grab(r"faces:\s+(\d+)")
    rec["foam_volume_m3"] = (grab(r"Total volume\s*=\s*([0-9.eE+-]+)") or "").rstrip(".") or None
    rec["max_cell_openness"] = grab(r"Max cell openness = ([0-9.eE+-]+)")
    rec["max_nonorthogonality"] = grab(r"Mesh non-orthogonality Max: ([0-9.eE+-]+)")
    rec["max_skewness"] = grab(r"Max skewness = ([0-9.eE+-]+)")
    rec["max_aspect_ratio"] = grab(r"Max aspect ratio = ([0-9.eE+-]+)")
    rec["mesh_ok"] = "Mesh OK" in cm

    if rec["foam_volume_m3"]:
        vfoam = float(rec["foam_volume_m3"])
        vexp = abs(V_in) * INCH ** 3
        rec["volume_expected_m3"] = vexp
        rec["volume_rel_diff"] = abs(vfoam - vexp) / vexp
        print(f"  VOLUME: source-boundary divergence -> {vexp:.9e} m^3 ; "
              f"OpenFOAM cell sum -> {vfoam:.9e} m^3 ; rel diff {rec['volume_rel_diff']:.3e}", flush=True)
    rec["elapsed_s"] = time.time() - t0
    json.dump(rec, open(os.path.join(a.case, "conversion_record.json"), "w"), indent=2)
    if not a.keep_msh:
        os.remove(msh)
    print(f"[{time.strftime('%H:%M:%S')}] DONE in {rec['elapsed_s']:.0f}s  "
          f"cells={rec['foam_cells']} meshOK={rec['mesh_ok']} "
          f"maxNonOrtho={rec['max_nonorthogonality']} maxSkew={rec['max_skewness']}", flush=True)

if __name__ == "__main__":
    main()
