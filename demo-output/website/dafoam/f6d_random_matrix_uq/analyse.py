"""
F6d -- quantity-of-interest extraction for the random-matrix UQ ensemble.

QoIs (both are the periodic-hill literature standards, and both are what the
F6b gate record already uses):
  * separation and reattachment x/h on the bottom wall, from the sign changes
    of Cf = -tau_x / (0.5 Ubar^2)  (same convention and same code path as
    f6b_periodic_hills/case_breuer_re10595/gate_analysis.py)
  * mean-velocity profiles at the case's own 9 stations x/h = 0..8, compared
    with the shipped Frohlich/Breuer LES field U_LES on the identical mesh.

Reference values are NOT recomputed here; they are read from the F6b gate
record and from the shipped LES field.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595"
BENCH = Path("/home/ubuntu/closure-challenge-benchmark/data/PH_Breuer")
sys.path.insert(0, str(CASE))
import foam_io as fio  # noqa: E402

UBAR = 0.72
STATIONS = list(range(9))


def bottomwall_x():
    pts = fio.read_points(str(CASE / "constant" / "polyMesh" / "points"))
    faces = fio.read_faces(str(CASE / "constant" / "polyMesh" / "faces"))
    bd = fio.read_boundary(str(CASE / "constant" / "polyMesh" / "boundary"))
    start, n = bd["bottomWall"]
    return fio.face_centroids(pts, faces, start, n)[:, 0]


def cf_crossings(wss_path, x):
    arr, _ = fio.read_vector_boundary_field(str(wss_path), "bottomWall")
    Cf = -arr[:, 0] / (0.5 * UBAR ** 2)
    sign = np.sign(Cf)
    out = []
    for i in np.where(np.diff(sign) != 0)[0]:
        out.append(float(x[i] + (0 - Cf[i]) * (x[i + 1] - x[i]) / (Cf[i + 1] - Cf[i])))
    return out, Cf


def separation_reattachment(crossings):
    """First and last Cf sign change.  Reported alongside, but NOT used as the
    headline QoI: a perturbed Reynolds stress can put small secondary reversed
    patches on the flat floor, and the last crossing then reports the end of a
    sliver rather than the end of the recirculation."""
    if len(crossings) < 2:
        return None, None
    return crossings[0], crossings[-1]


def primary_bubble(Cf, x):
    """Headline QoI: the PRIMARY recirculation region -- the longest contiguous
    run of reversed wall shear (Cf < 0) on the bottom wall, with both endpoints
    linearly interpolated to Cf = 0.

    This is the standard periodic-hill definition (the leeward-face separation
    and the downstream reattachment of the main bubble) and, unlike the
    first/last-crossing rule, it is insensitive to small secondary reversed
    patches that a perturbed Reynolds-stress field can create on the flat
    floor.  On the unperturbed baseline the two definitions agree exactly,
    which is the check that this choice does not move the reference point.

    Returns (separation, reattachment, n_reversed_regions).
    """
    neg = Cf < 0
    runs, s = [], None
    for i, b in enumerate(neg):
        if b and s is None:
            s = i
        if s is not None and (not b or i == len(neg) - 1):
            e = i - 1 if not b else i
            runs.append((s, e))
            s = None
    if not runs:
        return None, None, 0
    i0, i1 = max(runs, key=lambda r: x[r[1]] - x[r[0]])

    def cross(a, b):
        if Cf[b] == Cf[a]:
            return float(x[a])
        return float(x[a] + (0 - Cf[a]) * (x[b] - x[a]) / (Cf[b] - Cf[a]))

    sep = cross(i0 - 1, i0) if i0 > 0 else float(x[i0])
    reat = cross(i1, i1 + 1) if i1 < len(x) - 1 else float(x[i1])
    return sep, reat, len(runs)


def read_line_U(path):
    d = np.loadtxt(path)
    return d[:, 0], d[:, 1], d[:, 3:6]


_LES = {}


def les_interp():
    if "f" not in _LES:
        from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
        Cx = fio.read_internal_field(str(BENCH / "0" / "Cx"))
        Cy = fio.read_internal_field(str(BENCH / "0" / "Cy"))
        UL = fio.read_internal_field(str(BENCH / "0" / "U_LES"))
        pts = np.column_stack([Cx, Cy])
        lin = LinearNDInterpolator(pts, UL)
        near = NearestNDInterpolator(pts, UL)

        def f(xy):
            o = lin(xy)
            bad = np.isnan(o).any(axis=1)
            if bad.any():
                o[bad] = near(xy[bad])
            return o
        _LES["f"] = f
    return _LES["f"]


def station_profiles(case_dir, time):
    """Return {station: (y, Ux)} for a case, from the singleGraph output."""
    out = {}
    pp = Path(case_dir) / "postProcessing"
    for i in STATIONS:
        d = pp / f"singleGraph_x{i}" / str(time)
        if not d.is_dir():
            continue
        cand = list(d.glob("line_*U*.xy"))
        if not cand:
            continue
        f = cand[0]
        cols = f.stem.replace("line_", "").split("_")
        d_ = np.loadtxt(f)
        # columns: x y z then the fields in the order named in the filename;
        # scalars take 1 column, U takes 3.
        c = 3
        U = None
        for name in cols:
            if name == "U":
                U = d_[:, c:c + 3]
                break
            c += 1
        if U is None:
            continue
        out[i] = (d_[:, 0], d_[:, 1], U)
    return out


def profile_mae_vs_les(prof):
    """Scaled MAE of |U| against the LES field -- the SAME metric and scaling
    as f6b_periodic_hills/.../gate_analysis.py, so the numbers here are
    directly comparable to the F6b gate record's 12.511% baseline figure."""
    f = les_interp()
    per, vals = {}, []
    for i, (xs, ys, U) in prof.items():
        UL = f(np.column_stack([xs, ys]))
        mr = np.linalg.norm(U, axis=1)
        ml = np.linalg.norm(UL, axis=1)
        mae = float(np.mean(np.abs(mr - ml)))
        scale = float(np.mean(ml))
        per[f"x{i}"] = round(100.0 * mae / max(scale, 1e-12), 3)
        vals.append(per[f"x{i}"])
    return per, (float(np.mean(vals)) if vals else None)


def latest_written_time(case_dir):
    """Largest numeric time directory that actually contains a wallShearStress.
    Defensive: a member that stopped early still gets analysed at whatever it
    did write, and the time is reported alongside the number."""
    best = None
    for d in Path(case_dir).iterdir():
        if not d.is_dir():
            continue
        try:
            t = int(d.name)
        except ValueError:
            continue
        if t > 0 and (d / "wallShearStress").exists():
            best = t if best is None else max(best, t)
    return best


def analyse_case(case_dir, time=None):
    case_dir = Path(case_dir)
    if time is None:
        time = latest_written_time(case_dir)
        if time is None:
            return {"case": case_dir.name, "time": None}
    x = bottomwall_x()
    wss = case_dir / str(time) / "wallShearStress"
    res = {"case": case_dir.name, "time": time}
    if wss.exists():
        cr, Cf = cf_crossings(wss, x)
        sep_lc, reat_lc = separation_reattachment(cr)
        sep, reat, nreg = primary_bubble(Cf, x)
        res.update({"n_cf_crossings": len(cr), "cf_crossings": cr,
                    "n_reversed_regions": nreg,
                    "separation_x_over_h": sep, "reattachment_x_over_h": reat,
                    "separation_lastcross": sep_lc, "reattachment_lastcross": reat_lc,
                    "bubble_length": (None if sep is None else reat - sep)})
    prof = station_profiles(case_dir, time)
    if prof:
        per, overall = profile_mae_vs_les(prof)
        res["profile_mae_vs_LES_percent"] = per
        res["profile_mae_vs_LES_overall_percent"] = overall
    return res


def residual_history(log_path):
    import re
    t, last = None, {}
    first = {}
    for line in Path(log_path).read_text(errors="ignore").splitlines():
        m = re.match(r"^Time = (\d+)", line)
        if m:
            t = int(m.group(1))
            continue
        m = re.search(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", line)
        if m and t is not None:
            last[m.group(1)] = float(m.group(2))
            first.setdefault(m.group(1), float(m.group(2)))
    return {"final_iteration": t, "final_initial_residuals": last,
            "first_initial_residuals": first}


if __name__ == "__main__":
    for d in sys.argv[1:]:
        r = analyse_case(d, 4000)
        log = Path(d) / "log.simpleFoam"
        if log.exists():
            r["residuals"] = residual_history(log)
        print(json.dumps(r, indent=2))
