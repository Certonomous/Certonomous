"""F6b gate analysis: periodic hill (PH_Breuer, Re_H=10595).

Computes, from the benchmark's own shipped mesh/fields and (once available)
our own converged solve:
  1. Separation/reattachment x/h on bottomWall via wallShearStress zero
     crossings -- for (a) the benchmark's own shipped, fully-converged
     kOmegaSST RANS baseline (data/PH_Breuer/10000/wallShearStress) and
     (b) our own fresh solve.
  2. Mean-velocity-profile scaled MAE at the case's own 9 standard stations
     (x/h = 0..8) against the shipped LES reference field (U_LES), for both
     RANS fields above -- LES sampled onto the same y-points as the RANS
     singleGraph output via linear interpolation on cell centres.

No fitting/tuning. Every number here is a direct read of shipped or
freshly-solved fields; the only external published number (Frohlich et al.
2005, JFM 526:19-66 -- separation x/h~0.2, reattachment x/h~4.6-4.7) is a
fetched citation, not something computed here.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import foam_io as fio

BENCH = Path("/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer")
HERE = Path(__file__).resolve().parent
MESH = BENCH / "constant" / "polyMesh"
UBAR = 0.72
STATIONS = list(range(9))  # x/h = 0..8


def separation_reattachment(tau_x, x):
    """Cf sign-change crossings (all of them), returned in x order."""
    Cf = -tau_x / (0.5 * UBAR ** 2)
    sign = np.sign(Cf)
    crossings = []
    for idx in np.where(np.diff(sign) != 0)[0]:
        x0, x1 = x[idx], x[idx + 1]
        c0, c1 = Cf[idx], Cf[idx + 1]
        xcross = x0 + (0 - c0) * (x1 - x0) / (c1 - c0)
        crossings.append(float(xcross))
    return crossings, Cf


def bottomwall_geometry():
    pts = fio.read_points(str(MESH / "points"))
    faces = fio.read_faces(str(MESH / "faces"))
    bd = fio.read_boundary(str(MESH / "boundary"))
    start, n = bd["bottomWall"]
    cent = fio.face_centroids(pts, faces, start, n)
    return cent[:, 0]  # x per face, patch order


def wall_cf(wallshearstress_field_path, x):
    arr, _ = fio.read_vector_boundary_field(wallshearstress_field_path, "bottomWall")
    return separation_reattachment(arr[:, 0], x)


def les_interpolator():
    Cx = fio.read_internal_field(str(BENCH / "0" / "Cx"))
    Cy = fio.read_internal_field(str(BENCH / "0" / "Cy"))
    U_LES = fio.read_internal_field(str(BENCH / "0" / "U_LES"))
    pts = np.column_stack([Cx, Cy])
    lin = LinearNDInterpolator(pts, U_LES)
    near = NearestNDInterpolator(pts, U_LES)

    def interp(xy):
        out = lin(xy)
        bad = np.isnan(out).any(axis=1)
        if bad.any():
            out[bad] = near(xy[bad])
        return out

    return interp


def read_line_U(path):
    data = np.loadtxt(path)
    # columns: x y z Ux Uy Uz
    return data[:, 0], data[:, 1], data[:, 3:6]


def profile_scaled_mae(rans_dir, time, les_interp):
    """For each station, scaled MAE of |U| between RANS singleGraph output
    and LES interpolated onto the same y points. Returns dict station->mae,
    plus an overall mean."""
    out = {}
    for i in STATIONS:
        f = Path(rans_dir) / f"singleGraph_x{i}" / str(time) / "line_U.xy"
        if not f.exists():
            continue
        xs, ys, U_rans = read_line_U(f)
        xy = np.column_stack([xs, ys])
        U_les = les_interp(xy)
        mag_rans = np.linalg.norm(U_rans, axis=1)
        mag_les = np.linalg.norm(U_les, axis=1)
        mae = float(np.mean(np.abs(mag_rans - mag_les)))
        scale = float(np.mean(mag_les)) if np.mean(mag_les) > 1e-12 else float(np.mean(np.abs(mag_les))) + 1e-12
        out[f"x{i}"] = {
            "x_over_h": i,
            "n_points": int(len(xs)),
            "scaled_mae_percent": round(100.0 * mae / max(scale, 1e-9), 3) if scale else None,
        }
    vals = [v["scaled_mae_percent"] for v in out.values() if v["scaled_mae_percent"] is not None]
    overall = float(np.mean(vals)) if vals else None
    return out, overall


def main():
    x_face = bottomwall_geometry()

    result = {"ubar": UBAR, "mesh": "PH_Breuer (Re_H=10595, Lx=9h, Ly=3.035h)"}

    # (a) benchmark's own shipped, fully converged kOmegaSST RANS baseline
    shipped_wss = BENCH / "10000" / "wallShearStress"
    crossings_shipped, cf_shipped = wall_cf(str(shipped_wss), x_face)
    result["shipped_rans_baseline"] = {
        "source": str(shipped_wss),
        "iteration": 10000,
        "cf_zero_crossings_x_over_h": crossings_shipped,
    }

    # (b) our own fresh solve, if present
    our_case = HERE
    our_wss_candidates = sorted((our_case).glob("[0-9]*/wallShearStress"), key=lambda p: int(p.parent.name))
    if our_wss_candidates:
        our_final = our_wss_candidates[-1]
        crossings_ours, cf_ours = wall_cf(str(our_final), x_face)
        result["our_solve"] = {
            "source": str(our_final),
            "iteration": int(our_final.parent.name),
            "cf_zero_crossings_x_over_h": crossings_ours,
        }
        np.savetxt(HERE / f"cf_x_ours_{our_final.parent.name}.csv",
                   np.column_stack([x_face, cf_ours]), delimiter=",",
                   header="x_over_h,Cf", comments="")
    np.savetxt(HERE / "cf_x_shipped_10000.csv",
               np.column_stack([x_face, cf_shipped]), delimiter=",",
               header="x_over_h,Cf", comments="")

    # LES literature reference (fetched, cited -- not computed)
    result["frohlich_2005_les_reference"] = {
        "citation": "Frohlich, J., Mellen, C.P., Rodi, W., Temmerman, L., Leschziner, M.A. (2005). "
                     "Highly resolved large-eddy simulation of separated flow in a channel with "
                     "streamwise periodic constrictions. J. Fluid Mech. 526, 19-66.",
        "separation_x_over_h": 0.2,
        "reattachment_x_over_h_range": [4.6, 4.7],
        "reynolds_number": 10595,
        "re_definition": "Re_H = U_bulk(hill crest) * h / nu",
    }

    # Profile comparison vs LES at the 9 standard stations
    les_interp = les_interpolator()
    prof_shipped, overall_shipped = profile_scaled_mae(BENCH / "postProcessing", 10000, les_interp)
    result["profile_scaled_mae_vs_LES"] = {
        "shipped_rans_baseline": {"per_station": prof_shipped, "overall_percent": overall_shipped},
    }
    if our_wss_candidates:
        our_pp = our_case / "postProcessing"
        prof_ours, overall_ours = profile_scaled_mae(our_pp, int(our_final.parent.name), les_interp)
        result["profile_scaled_mae_vs_LES"]["our_solve"] = {"per_station": prof_ours, "overall_percent": overall_ours}

    out_path = HERE / "gate_result.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
