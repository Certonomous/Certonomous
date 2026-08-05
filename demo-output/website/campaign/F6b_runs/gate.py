"""F6b (2026-08-05) gate analysis on the lab's OWN periodic-hill meshes.

For each rung: separation/reattachment x/h from the bottom-wall wallShearStress
sign change, and the scaled MAE of |U| at the nine standard stations against the
Breuer LES field the benchmark ships (interpolated from the shipped mesh's cell
centres onto our own station points).
"""
import json, sys
from pathlib import Path
import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

sys.path.insert(0, "/home/ubuntu/Certonomous/demo-output/website/dafoam/f6b_periodic_hills/case_breuer_re10595")
import foam_io as fio

BENCH = Path("/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer")
BASE = Path("/home/ubuntu/Certonomous/demo-output/website/campaign/F6b_runs")
UBAR = 0.72
NU = 9.438414346389807e-05


def crossings(x, tau_x):
    Cf = -tau_x / (0.5 * UBAR ** 2)
    s = np.sign(Cf)
    out = []
    for i in np.where(np.diff(s) != 0)[0]:
        out.append(float(x[i] + (0 - Cf[i]) * (x[i + 1] - x[i]) / (Cf[i + 1] - Cf[i])))
    return out


def wall_x(mesh_dir, patch="bottomWall"):
    pts = fio.read_points(str(mesh_dir / "points"))
    faces = fio.read_faces(str(mesh_dir / "faces"))
    bd = fio.read_boundary(str(mesh_dir / "boundary"))
    start, n = bd[patch]
    cent = fio.face_centroids(pts, faces, start, n)
    return cent


def les_interp():
    Cx = fio.read_internal_field(str(BENCH / "0" / "Cx"))
    Cy = fio.read_internal_field(str(BENCH / "0" / "Cy"))
    U = fio.read_internal_field(str(BENCH / "0" / "U_LES"))
    p = np.column_stack([Cx, Cy])
    lin, near = LinearNDInterpolator(p, U), NearestNDInterpolator(p, U)

    def f(xy):
        o = lin(xy)
        bad = np.isnan(o).any(axis=1)
        if bad.any():
            o[bad] = near(xy[bad])
        return o
    return f


def rung(name, time):
    case = BASE / name
    mesh = case / "constant" / "polyMesh"
    cent = wall_x(mesh)
    order = np.argsort(cent[:, 0])
    tau, _ = fio.read_vector_boundary_field(str(case / str(time) / "wallShearStress"), "bottomWall")
    x = cent[order, 0]
    tx = tau[order, 0]
    cr = crossings(x, tx)
    # y+ at the first cell centre, from |tau| on each wall face
    tmag = np.linalg.norm(tau, axis=1)
    utau = np.sqrt(tmag)
    return x, tx, cr, utau


VECTORS = {"U"}


def u_columns(path):
    """Column index of Ux in an OpenFOAM `sets` raw file, read from its NAME.

    The file is line_<f1>_<f2>_...xy with columns x y z then each field in the
    order the name lists, 1 column per scalar and 3 per vector.  Assuming
    `line_U.xy` is exactly the bug that left the 2026-07-29 F6b profile metric
    null, so the order is parsed rather than guessed.
    """
    fields = path.name[len("line_"):-len(".xy")].split("_")
    col = 3
    for f in fields:
        if f == "U":
            return col
        col += 3 if f in VECTORS else 1
    raise KeyError(f"no U field in {path.name}")


def profiles(name, time, interp):
    case = BASE / name
    out, vals = {}, []
    for i in range(9):
        cand = sorted((case / "postProcessing" / f"singleGraph_x{i}" / str(time)).glob("line_*.xy"))
        cand = [c for c in cand if "_U" in c.name or c.name == "line_U.xy"]
        if not cand:
            continue
        f = cand[0]
        c0 = u_columns(f)
        d = np.loadtxt(f)
        xs, ys, U = d[:, 0], d[:, 1], d[:, c0:c0 + 3]
        Ules = interp(np.column_stack([xs, ys]))
        mr, ml = np.linalg.norm(U, axis=1), np.linalg.norm(Ules, axis=1)
        mae = float(np.mean(np.abs(mr - ml)))
        sc = float(np.mean(ml))
        out[f"x{i}"] = round(100.0 * mae / sc, 3)
        vals.append(out[f"x{i}"])
    return out, (float(np.mean(vals)) if vals else None)


def main():
    interp = les_interp()
    res = {"ubar": UBAR, "nu": NU, "Re_H": round(UBAR / NU), "rungs": {}}
    for name, nx, ny, time in [("coarse", 84, 92, None), ("medium", 120, 130, None),
                               ("fine", 170, 184, None), ("veryfine", 240, 260, None)]:
        case = BASE / name
        times = sorted([int(p.name) for p in case.iterdir()
                        if p.name.isdigit() and int(p.name) > 0])
        if not times:
            print(f"{name}: no written time yet")
            continue
        t = times[-1]
        x, tx, cr, utau = rung(name, t)
        prof, overall = profiles(name, t, interp)
        # first-cell-centre y+ needs the wall-normal distance; use the mesh's own
        # first cell height from the blockMeshDict target, recovered from the mesh
        res["rungs"][name] = {
            "cells": nx * ny, "nx": nx, "ny": ny, "time_written": t,
            "crossings_x_over_h": [round(c, 4) for c in cr],
            "separation_x_over_h": round(cr[0], 4) if cr else None,
            "reattachment_x_over_h": round(cr[1], 4) if len(cr) > 1 else None,
            "utau_max": round(float(utau.max()), 6),
            "utau_mean": round(float(utau.mean()), 6),
            "profile_scaled_mae_percent": prof,
            "profile_scaled_mae_overall_percent": round(overall, 3) if overall else None,
        }
        print(name, "t=", t, "crossings", [round(c, 4) for c in cr], "MAE", overall)
    # the benchmark's own shipped RANS field, on the shipped mesh, as the anchor
    cent = wall_x(BENCH / "constant" / "polyMesh")
    o = np.argsort(cent[:, 0])
    tau, _ = fio.read_vector_boundary_field(str(BENCH / "10000" / "wallShearStress"), "bottomWall")
    cr = crossings(cent[o, 0], tau[o, 0])
    res["shipped_mesh_anchor"] = {"crossings_x_over_h": [round(c, 6) for c in cr]}
    print("shipped anchor", [round(c, 6) for c in cr])
    (BASE / "gate_result.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
