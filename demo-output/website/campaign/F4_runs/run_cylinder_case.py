#!/usr/bin/env python3
"""
Run a hypersonic-cylinder rhoCentralFoam case (make_cylinder_case.py) and
post-process both F4 gates:
  1. Shock standoff distance at the stagnation line (theta=0), located by the
     peak-density-gradient-locus method (F3's shock-detection technique,
     reused here along the radial sample line instead of a Cartesian one).
  2. Windward surface Cp vs. modified Newtonian theory (billig_theory.py).
"""
import sys
import os
import math
import subprocess
import time
import json
import glob
import re
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from make_cylinder_case import make_case, R, THETA_MAX_DEG
from billig_theory import (billig_delta_over_R, modified_newtonian_cp_of_theta_c,
                            cp_max_rayleigh_pitot)

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def sh(cmd, cwd, logfile=None):
    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    t0 = time.time()
    p = subprocess.run(["bash", "-c", full], cwd=cwd,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    if logfile:
        with open(logfile, "wb") as f:
            f.write(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({cmd}) rc={p.returncode}; see {logfile}")
    return dt


def write_sampledicts(case_dir, R_top, n_theta_stations=7, theta_lo_deg=0.0, theta_hi_deg=None):
    if theta_hi_deg is None:
        theta_hi_deg = THETA_MAX_DEG - 3.0  # stay off the very edge of the domain
    thetas_deg = np.linspace(theta_lo_deg, theta_hi_deg, n_theta_stations)
    sets = []
    for i, th_deg in enumerate(thetas_deg):
        th = math.radians(th_deg)
        x0, y0 = -R * math.cos(th), R * math.sin(th)
        x1, y1 = -R_top * math.cos(th), R_top * math.sin(th)
        sets.append(f"    r{i} {{ type uniform; axis distance; "
                     f"start ({x0:.8f} {y0:.8f} 0); end ({x1:.8f} {y1:.8f} 0); nPoints 400; }}")
    content = f"""FoamFile {{ version 2.0; format ascii; class dictionary; object sampleDict; }}
type sets;
libs (sampling);
interpolationScheme cellPoint;
setFormat raw;
fields (p rho T);
sets
(
{chr(10).join(sets)}
);
"""
    with open(f"{case_dir}/system/sampleDict", "w") as f:
        f.write(content)

    surf_content = """FoamFile { version 2.0; format ascii; class dictionary; object surfaceSampleDict; }
type surfaces;
libs (sampling);
interpolationScheme cellPoint;
surfaceFormat raw;
fields (p rho T);
surfaces
(
    cylSurface
    {
        type patch;
        patches (cylinder);
        interpolate false;
        triangulate false;
    }
);
"""
    with open(f"{case_dir}/system/surfaceSampleDict", "w") as f:
        f.write(surf_content)
    return list(thetas_deg)


def find_shock_r(xy_path):
    """Peak |d(rho)/d(distance)| locus, same technique as F3_runs/run_cone_case.py
    (peak density-gradient locus along the sample line), here along the
    radial direction (distance = r - R, wall at 0)."""
    d = np.loadtxt(xy_path)
    if d.ndim != 2 or len(d) < 10:
        return None, None, None
    dist, T, p, rho = d[:, 0], d[:, 1], d[:, 2], d[:, 3]
    grad = np.gradient(rho, dist)
    i = np.argmax(np.abs(grad))
    return dist[i], p[i], rho[i]


def run_one(case_dir, M, res_level, n_theta_stations=7, n_avg_snapshots=3):
    """n_avg_snapshots: how many of the LATEST write times to sample and
    average over, as an explicit steady-state convergence check (see
    make_cylinder_case.make_case docstring) -- report the scatter across
    them, not just a single latestTime snapshot, per the methodological-
    honesty carryover from F3 (state how sensitive the gate value is to the
    choice/timing of measurement)."""
    os.makedirs(case_dir, exist_ok=True)
    meta = make_case(case_dir, M, res_level)
    t_mesh = sh("blockMesh", case_dir, f"{case_dir}/log.blockMesh")
    t_check = sh("checkMesh -noTopology", case_dir, f"{case_dir}/log.checkMesh")
    ncells = meta["ntheta"] * meta["nr"]
    t_run = sh("rhoCentralFoam", case_dir, f"{case_dir}/log.rhoCentralFoam")

    thetas_deg = write_sampledicts(case_dir, meta["R_top"], n_theta_stations)

    tdirs = [d for d in os.listdir(case_dir) if re.match(r"^[0-9]+\.?[0-9]*$", d)]
    tdirs = sorted(tdirs, key=lambda s: float(s))
    if not tdirs or tdirs[-1] == "0":
        raise RuntimeError(f"{case_dir}: solver produced no post-t=0 write "
                            f"(crashed before first write?) -- see log.rhoCentralFoam")
    latest = tdirs[-1]
    solver_completed = abs(float(latest) - meta["endTime"]) < 1e-3
    snap_times = tdirs[-n_avg_snapshots:] if len(tdirs) >= n_avg_snapshots else tdirs[1:]

    t_samp = sh(f"postProcess -func sampleDict -time '{snap_times[0]}:{snap_times[-1]}'",
                case_dir, f"{case_dir}/log.sample")
    t_surf = sh(f"postProcess -func surfaceSampleDict -time '{snap_times[0]}:{snap_times[-1]}'",
                case_dir, f"{case_dir}/log.surfsample")

    delta_billig = billig_delta_over_R(M) * R
    cpmax = cp_max_rayleigh_pitot(M)
    q1 = 0.5 * 1.4 * 1.0 * M**2  # q1 = 0.5*gamma*p1*M1^2, p1=1 (nondim units, matches F3)

    # ---- Gate 1: shock standoff at the stagnation line (theta=0), per snapshot ----
    standoff_snapshots = []
    shock_stations_last = []
    for st in snap_times:
        sampdir = f"{case_dir}/postProcessing/sampleDict/{st}"
        for i, th_deg in enumerate(thetas_deg):
            cands = glob.glob(f"{sampdir}/r{i}_*.xy")
            if not cands:
                continue
            dist_s, p_s, rho_s = find_shock_r(cands[0])
            if dist_s is None:
                continue
            if i == 0:
                standoff_snapshots.append(dict(time=st, standoff=float(dist_s), p_at_shock=float(p_s)))
            if st == snap_times[-1]:
                shock_stations_last.append(dict(theta_deg=float(th_deg), standoff=float(dist_s),
                                                  p_at_shock=float(p_s), rho_at_shock=float(rho_s)))

    standoff_vals = np.array([s["standoff"] for s in standoff_snapshots])
    standoff_mean = float(np.mean(standoff_vals)) if len(standoff_vals) else None
    standoff_std = float(np.std(standoff_vals)) if len(standoff_vals) else None
    standoff_dev_pct = (100 * (standoff_mean - delta_billig) / delta_billig
                         if standoff_mean is not None else None)

    # ---- Gate 2: windward surface Cp vs modified Newtonian, averaged over the same snapshots ----
    cp_cfd_snaps = []
    theta_wall_deg = None
    for st in snap_times:
        surfdir = f"{case_dir}/postProcessing/surfaceSampleDict/{st}"
        surf_files = glob.glob(f"{surfdir}/cylSurface_p*.raw") or glob.glob(f"{surfdir}/*p*.raw")
        if not surf_files:
            continue
        arr = np.loadtxt(surf_files[0], comments="#")
        x_wall, y_wall, p_wall = arr[:, 0], arr[:, 1], arr[:, 3]
        th = np.degrees(np.arctan2(y_wall, -x_wall))
        order = np.argsort(th)
        th, p_wall = th[order], p_wall[order]
        if theta_wall_deg is None:
            theta_wall_deg = th
        cp_cfd_snaps.append((p_wall - 1.0) / q1)
    cp_cfd_snaps = np.array(cp_cfd_snaps)
    cp_cfd_mean = cp_cfd_snaps.mean(axis=0)
    cp_cfd_std = cp_cfd_snaps.std(axis=0)
    cp_newton = np.array([modified_newtonian_cp_of_theta_c(math.radians(t), M) for t in theta_wall_deg])

    rms_full = float(np.sqrt(np.mean((cp_cfd_mean - cp_newton) ** 2)))
    rms_full_pct_of_cpmax = 100 * rms_full / cpmax

    mask_mid = (theta_wall_deg > 5) & (theta_wall_deg < THETA_MAX_DEG - 8)
    rms_mid = float(np.sqrt(np.mean((cp_cfd_mean[mask_mid] - cp_newton[mask_mid]) ** 2))) if mask_mid.sum() > 3 else None
    cp_snapshot_scatter_mean_pct_of_cpmax = float(100 * np.mean(cp_cfd_std) / cpmax)

    result = dict(
        case_dir=case_dir, M=M, res_level=res_level, ncells=ncells,
        t_mesh_s=t_mesh, t_check_s=t_check, t_run_s=t_run, t_sample_s=t_samp + t_surf,
        R_top=meta["R_top"], theta_max_deg=THETA_MAX_DEG, endTime=meta["endTime"],
        latest_time=latest, solver_completed_to_endTime=solver_completed,
        snapshot_times_used=snap_times,
        delta_billig=delta_billig,
        standoff_snapshots=standoff_snapshots,
        standoff_mean=standoff_mean, standoff_std=standoff_std,
        standoff_dev_pct=standoff_dev_pct,
        shock_stations_last_snapshot=shock_stations_last,
        cp_max=cpmax, rms_cp_full=rms_full, rms_cp_full_pct_of_cpmax=rms_full_pct_of_cpmax,
        rms_cp_mid=rms_mid, cp_snapshot_scatter_mean_pct_of_cpmax=cp_snapshot_scatter_mean_pct_of_cpmax,
        wall_profile=[dict(theta_deg=float(t), cp_cfd_mean=float(a), cp_cfd_std=float(s), cp_newton=float(b))
                      for t, a, s, b in zip(theta_wall_deg, cp_cfd_mean, cp_cfd_std, cp_newton)],
    )
    with open(f"{case_dir}/result.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    case_dir, M, res_level = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    n_theta = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    r = run_one(case_dir, M, res_level, n_theta)
    print(json.dumps({k: v for k, v in r.items() if k not in ("wall_profile", "shock_stations")}, indent=2))
