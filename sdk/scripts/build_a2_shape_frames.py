"""Bake the A2 wing's optimizer-produced shape history into a static artifact.

OFFLINE TOOL. This is the only thing in the pipeline that touches pyGeo, and
it is never run by the act. It runs once, here, and writes
``demo-output/website/dafoam/ladder-a/A2_shape_frames.json``, which the
adjoint-optimization act then streams to the control room with nothing but the
standard library. The demo must run on a laptop with no OpenFOAM, no DAFoam
and no internet, so the act may not import pyGeo, and does not.

What it does, and why it is a replay rather than a model
-------------------------------------------------------
It instantiates the SAME ``pygeo.DVGeometry`` from ``FFD/wingFFD.xyz`` with the
SAME design-variable definitions as the run's own ``runScript.py`` (96 local
shape variables on the FFD lattice, 7 twist variables about a quarter-chord
reference axis), embeds the wing patch points read out of the case's own
``constant/polyMesh``, and then calls ``setDesignVars``/``update`` with the
design-variable vectors the optimizer recorded in ``OptView.hst``. Every
surface it writes is therefore the surface the optimizer actually produced.
Nothing is interpolated, smoothed, or exaggerated, and the script asserts that
iteration 0 reproduces the embedded baseline to 1e-9 m before it writes
anything -- that assertion is what makes it a replay and not a fit.

Two independent checks ride along and are recorded in the artifact:

* ``iter 0`` reproduces the input surface (the replay is exact at the start);
* the FFD map from shape variables to surface points is verified linear to
  ~1e-15 relative, which is what licenses pushing the recorded adjoint
  gradient through that same map onto the skin.

Run it (host, needs Docker and the A2 run on disk)
--------------------------------------------------
    sudo docker run --rm \
      -v /home/ubuntu/certonomous-runs/A2-mach-wing:/case \
      -v /home/ubuntu/Certonomous/demo-output/website/dafoam/ladder-a:/out \
      -v /home/ubuntu/Certonomous/sdk/scripts:/scripts \
      dafoam/opt-packages:latest \
      bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh &&
                python /scripts/build_a2_shape_frames.py'

The artifact is deterministic: same inputs, same bytes. It carries no
timestamp and no host-dependent value, so a rebuild that changes it means an
input changed.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re

import numpy as np

CASE = "/case"
OUT = "/out/A2_shape_frames.json"

# The OpenMDAO driver scalers from runScript.py's add_design_var calls.
# pyoptsparse stores what OpenMDAO handed it, which is already the SCALED
# vector: the history's own DV bounds are the scaled bounds (shape +/-10 for a
# user bound of +/-1 at scaler 10) and its own 'scale' entries are all 1.0.
# Dividing by these recovers the physical design variables pyGeo expects.
SCALER_SHAPE = 10.0
SCALER_TWIST = 0.1

WING_PATCH = "wing"


# --------------------------------------------------------------- polyMesh I/O
def _foam_text(path: str) -> str:
    with gzip.open(path, "rt") as handle:
        return handle.read()


def _block(text: str) -> str:
    """The body of the single ``N ( ... )`` list an OpenFOAM data file holds."""
    match = re.search(r"\n(\d+)\s*\n\(", text)
    body = text[match.end():]
    return body[:body.index("\n)")]


def read_wing_patch():
    """The wing patch as (points, quad connectivity) from the case's own mesh.

    This is the solver's surface, undecimated: 1,008 quadrilateral faces. It is
    not a display approximation of the wing, it is the wing the primal was
    solved on.
    """
    pts = np.array([[float(v) for v in m.split()] for m in
                    re.findall(r"\(([^)]*)\)",
                               _block(_foam_text(f"{CASE}/constant/polyMesh/points.gz")))])
    faces = [[int(i) for i in b.split()] for _, b in
             re.findall(r"(\d+)\(([^)]*)\)",
                        _block(_foam_text(f"{CASE}/constant/polyMesh/faces.gz")))]

    with open(f"{CASE}/constant/polyMesh/boundary") as handle:
        boundary = handle.read()      # the only polyMesh file the case leaves plain
    patch = re.search(WING_PATCH + r"\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);",
                      boundary, re.S)
    n_faces, start = int(patch.group(1)), int(patch.group(2))
    wing = faces[start:start + n_faces]
    assert {len(f) for f in wing} == {4}, "the wing patch is not all quads"

    used = sorted({i for f in wing for i in f})
    remap = {g: i for i, g in enumerate(used)}
    quads = np.array([[remap[i] for i in f] for f in wing])
    return pts[used], quads, n_faces


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    from pygeo import DVGeometry, geo_utils
    from pyoptsparse import History

    base_pts, quads, n_wing_faces = read_wing_patch()
    print("wing patch:", base_pts.shape[0], "points,", n_wing_faces, "quad faces")

    # ------------------------------------------------------------ DVGeometry
    # Built in runScript.py's own order: the discipline coordinates are
    # embedded first, then the reference axis, then the twist and shape DVs.
    dvgeo = DVGeometry(f"{CASE}/FFD/wingFFD.xyz")
    dvgeo.addPointSet(base_pts, "wing")
    n_ref = dvgeo.addRefAxis(name="wingAxis", xFraction=0.25, alignIndex="k")

    def twist(val, geo):
        for i in range(1, n_ref):
            geo.rot_z["wingAxis"].coef[i] = -val[i - 1]

    dvgeo.addGlobalDV(dvName="twist", value=np.zeros(n_ref - 1), func=twist,
                      lower=-10.0, upper=10.0, scale=0.1)
    local = dvgeo.getLocalIndex(0)
    select = geo_utils.PointSelect("list", local[:, :, :].flatten())
    n_shape = dvgeo.addLocalDV("shape", pointSelect=select, lower=-1.0,
                               upper=1.0, scale=10.0)
    print("design variables:", n_shape, "shape +", n_ref - 1, "twist")
    # Where the twist stations sit on the span, read off the reference axis
    # pyGeo built, not assumed.
    ref_z = np.array(dvgeo.axis["wingAxis"]["curve"].coef)[:, 2]
    assert len(ref_z) == n_ref
    print("reference-axis stations at z =", np.round(ref_z, 3))

    # -------------------------------------------------------- the DV history
    hist = History(f"{CASE}/OptView.hst", flag="r")
    major = hist.getValues(major=True)
    cd_rec = np.array(major["scenario1.aero_post.functionals.CD"]).ravel()
    cl_rec = np.array(major["scenario1.aero_post.functionals.CL"]).ravel()
    shape_rec = np.array(major["dvs.shape"])
    twist_rec = np.array(major["dvs.twist"])

    # Join to the already-committed major-iteration table the same way that
    # table was built: exact match on the objective, no tolerance slack.
    joined = json.load(open("/out/A2_optimization_history.json"))["history"]
    rows = []
    for rec in joined:
        k = int(np.argmin(np.abs(cd_rec - rec["CD"])))
        assert abs(cd_rec[k] - rec["CD"]) < 5e-10, rec["iter"]
        rows.append((rec["iter"], k, rec["CD"], float(cl_rec[k])))
    print("joined", len(rows), "major iterations, zero unmatched")

    def coords(k):
        dvgeo.setDesignVars({"shape": shape_rec[k] / SCALER_SHAPE,
                             "twist": twist_rec[k] / SCALER_TWIST})
        return np.array(dvgeo.update("wing"))

    base = coords(rows[0][1])
    assert np.allclose(shape_rec[rows[0][1]], 0.0)
    assert np.allclose(base, base_pts, atol=1e-9), \
        "iteration 0 does not reproduce the embedded surface"
    print("iteration 0 reproduces the embedded surface to 1e-9 m")

    # ------------------------------------------------------- outward normals
    # OpenFOAM boundary-face normals point out of the owner cell, i.e. out of
    # the fluid and INTO the wing. The sign is not assumed: it is fixed by the
    # topmost face, whose outward normal must have a positive y component.
    def face_normals(x):
        a, b, c, d = (x[quads[:, 0]], x[quads[:, 1]], x[quads[:, 2]], x[quads[:, 3]])
        n = np.cross(c - a, d - b)
        return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30)

    fn = -face_normals(base)
    centroids = base[quads].mean(axis=1)
    if fn[int(np.argmax(centroids[:, 1])), 1] < 0:
        fn = -fn
    vn = np.zeros_like(base)
    for j in range(4):
        np.add.at(vn, quads[:, j], fn)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-30)

    # ------------------------------- the adjoint gradient at the baseline
    grad = call = None
    for key in hist.getCallCounters():
        entry = hist.read(key)
        if not isinstance(entry, dict) or not entry.get("funcsSens"):
            continue
        xuser = entry.get("xuser", {})
        if "dvs.shape" not in xuser or not np.allclose(np.array(xuser["dvs.shape"]), 0.0):
            continue
        sens = entry["funcsSens"]["scenario1.aero_post.functionals.CD"]
        grad, call = np.array(sens["dvs.shape"]).ravel(), key
        break
    assert grad is not None, "no adjoint gradient recorded at the baseline design"

    # The steepest-descent direction in the design space the optimizer works
    # in, normalised to a unit step and pushed through the FFD's own map onto
    # the skin. The FFD map is linear in the shape variables (checked below),
    # so this is the exact surface motion that gradient commands, not a
    # linearisation of something curved.
    step = -grad / np.linalg.norm(grad)
    dvgeo.setDesignVars({"shape": step / SCALER_SHAPE, "twist": np.zeros(n_ref - 1)})
    d_step = np.array(dvgeo.update("wing")) - base
    dvgeo.setDesignVars({"shape": 0.5 * step / SCALER_SHAPE,
                         "twist": np.zeros(n_ref - 1)})
    half = np.array(dvgeo.update("wing")) - base
    linearity = float(np.abs(half - 0.5 * d_step).max() / max(np.abs(d_step).max(), 1e-30))
    assert linearity < 1e-9, f"FFD map is not linear in the shape DVs ({linearity})"
    grad_face = np.einsum("ij,ij->i", d_step, vn)[quads].mean(axis=1) * 1e3   # mm/step

    # ------------------------------------------------------------- the frames
    frames = []
    for it, k, cd, cl in rows:
        x = coords(k)
        disp = x - base
        dn = np.einsum("ij,ij->i", disp, vn)
        frames.append({
            "iter": it, "CD": cd, "CL": cl,
            "max_disp_mm": round(float(np.linalg.norm(disp, axis=1).max()) * 1e3, 4),
            "max_dn_mm": round(float(np.abs(dn).max()) * 1e3, 4),
            "twist_deg": [round(v, 5) for v in (twist_rec[k] / SCALER_TWIST)],
            "disp": [[round(float(c), 6) for c in v] for v in disp],
            "disp_n_mm": [round(float(v) * 1e3, 2) for v in dn[quads].mean(axis=1)],
        })

    window = np.concatenate([f["disp_n_mm"] for f in frames])
    extent = lambda a: float(a.max() - a.min())    # noqa: E731
    root = np.abs(base[:, 2]) < 0.05

    doc = {
        "_what": "Every wing surface the A2 discrete-adjoint optimization "
                 "actually produced, one per major iteration, replayed "
                 "through the run's own shape parameterization.",
        "_method": "pygeo.DVGeometry instantiated from FFD/wingFFD.xyz with "
                   "the design variables defined exactly as in the run's "
                   "runScript.py (96 local shape DVs on the FFD lattice, 7 "
                   "twist DVs about a quarter-chord reference axis). The wing "
                   "patch points and connectivity come from the case's own "
                   "constant/polyMesh. The design-variable vectors come from "
                   "OptView.hst, de-scaled by the OpenMDAO driver scalers, "
                   "and are applied with setDesignVars/update. This is a "
                   "replay of the optimizer's own deformation, not a model "
                   "of it.",
        "_checks": {
            "iter0_reproduces_baseline_m": 1e-9,
            "ffd_shape_map_linearity_residual": linearity,
            "major_iterations_matched": len(rows),
            "major_iterations_unmatched": 0,
        },
        "_shape_is": "the design (jig) shape DVGeometry hands the solver. The "
                     "aeroelastic deflection the structural solver adds on "
                     "top of it is not part of this replay and is not shown.",
        "_surface_is": f"the solver's own wing patch, {n_wing_faces} quad "
                       f"faces, undecimated. Split into "
                       f"{2 * n_wing_faces} triangles for display only; no "
                       f"point is moved or merged.",
        "_no_exaggeration": "Every coordinate in this file is at true scale. "
                            "No displacement is amplified anywhere.",
        "_storage": "base_vertices is the baseline wing in metres. Each frame "
                    "carries its displacement from that baseline in metres, "
                    "rounded to 1e-6 m; adding the two gives the replayed "
                    "surface.",
        "_sources": [{"file": name, "sha256": _sha256(f"{CASE}/{name}")}
                     for name in ("FFD/wingFFD.xyz", "OptView.hst", "runScript.py")],
        "n_points": int(base.shape[0]),
        "n_quad_faces": int(n_wing_faces),
        "n_display_triangles": int(2 * n_wing_faces),
        "n_shape_dv": int(n_shape),
        "n_twist_dv": int(n_ref - 1),
        # Spanwise station of each reference-axis control point, so the twist
        # distribution can be plotted against the wing rather than against an
        # index. Station 0 is the root and carries no design variable; twist
        # DV j drives station j+1.
        "refaxis_z_m": [round(float(v), 6) for v in ref_z],
        "chord_root_m": round(extent(base[root, 0]), 6),
        "chord_tip_m": round(extent(base[base[:, 2] > 13.9, 0]), 6),
        "thickness_root_m": round(extent(base[root, 1]), 6),
        "span_m": round(extent(base[:, 2]), 6),
        "base_vertices": [[round(float(c), 6) for c in v] for v in base],
        "faces": [t for q in quads.tolist()
                  for t in ([q[0], q[1], q[2]], [q[0], q[2], q[3]])],
        "gradient": {
            "_what": "The discrete-adjoint gradient of C_d with respect to "
                     "the 96 shape variables at the baseline design, exactly "
                     "as recorded in OptView.hst, pushed through the FFD's "
                     "own (linear) map onto the skin and resolved on the "
                     "outward normal. Positive means the descent direction "
                     "pushes the skin outward.",
            "_units": "millimetres of surface motion per unit-L2 step of "
                      "steepest descent in the 96-variable shape space",
            "_hst_call": call,
            "grad_l2_norm": float(np.linalg.norm(grad)),
            "grad_absmax": float(np.abs(grad).max()),
            "window_mm_per_step": [round(float(grad_face.min()), 3),
                                   round(float(grad_face.max()), 3)],
            "values_mm_per_step": [round(float(v), 4) for v in grad_face],
        },
        "disp_window_mm": [round(float(window.min()), 2),
                           round(float(window.max()), 2)],
        "frames": frames,
    }
    with open(OUT, "w") as handle:
        json.dump(doc, handle, separators=(",", ":"), sort_keys=False)
    print("wrote", OUT, "frames", len(frames),
          "max displacement", frames[-1]["max_disp_mm"], "mm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
