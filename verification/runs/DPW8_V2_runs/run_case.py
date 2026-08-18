#!/usr/bin/env python3
import os
import sys
import glob
import json
import time
import subprocess
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from make_case import write_case
from build_mesh import build_grid_points, GRID_LEVELS
from joukowski_theory import JoukowskiAirfoil

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def sh(cmd, cwd, logfile=None, timeout=None):
    full = f"source {FOAM_BASHRC} >/dev/null 2>&1; {cmd}"
    t0 = time.time()
    p = subprocess.run(["bash", "-c", full], cwd=cwd, timeout=timeout,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    if logfile:
        with open(logfile, "wb") as f:
            f.write(p.stdout)
    if p.returncode != 0:
        raise RuntimeError(f"command failed ({cmd}) rc={p.returncode}; see {logfile}\n"
                            + p.stdout.decode(errors="replace")[-3000:])
    return dt


def write_surface_sample_dict(case_dir):
    content = """FoamFile { version 2.0; format ascii; class dictionary; object surfaceSampleDict; }
type surfaces;
libs (sampling);
interpolationScheme cellPoint;
surfaceFormat raw;
fields (p);
surfaces
(
    airfoilSurface
    {
        type patch;
        patches (airfoil);
        interpolate false;
        triangulate false;
    }
);
"""
    with open(f"{case_dir}/system/surfaceSampleDict", "w") as f:
        f.write(content)


def write_decompose_par_dict(case_dir, n_ranks):
    content = f"""FoamFile {{ version 2.0; format ascii; class dictionary; object decomposeParDict; }}
numberOfSubdomains {n_ranks};
method          scotch;
"""
    with open(f"{case_dir}/system/decomposeParDict", "w") as f:
        f.write(content)


def run_level(level, case_dir, end_time, eps=0.10, y1_target_physical=3.0e-6,
              r_outer_chords=120.0, timeout_s=1800, n_ranks=1):
    meta = write_case(case_dir, level, eps=eps, y1_target_physical=y1_target_physical,
                       r_outer_chords=r_outer_chords)
    cd_path = f"{case_dir}/system/controlDict"
    s = open(cd_path).read().replace("{END_TIME}", str(end_time))
    open(cd_path, "w").write(s)

    t_mesh = 0.0  # mesh built in-process above (python), included in meta separately
    t_check = sh("checkMesh -noTopology", case_dir, f"{case_dir}/log.checkMesh")
    if n_ranks > 1:
        write_decompose_par_dict(case_dir, n_ranks)
        sh("decomposePar", case_dir, f"{case_dir}/log.decomposePar")
        t_run = sh(f"mpirun --oversubscribe -np {n_ranks} simpleFoam -parallel", case_dir,
                    f"{case_dir}/log.simpleFoam", timeout=timeout_s)
        sh("reconstructPar -latestTime", case_dir, f"{case_dir}/log.reconstructPar")
    else:
        t_run = sh("simpleFoam", case_dir, f"{case_dir}/log.simpleFoam", timeout=timeout_s)

    write_surface_sample_dict(case_dir)
    t_samp = sh("postProcess -func surfaceSampleDict -latestTime", case_dir, f"{case_dir}/log.surfsample")

    tdirs = [d for d in os.listdir(case_dir) if __import__("re").match(r"^[0-9]+\.?[0-9]*$", d)]
    tdirs = sorted(tdirs, key=lambda x: float(x))
    latest = tdirs[-1]

    surfdir = sorted(glob.glob(f"{case_dir}/postProcessing/surfaceSampleDict/*"))[-1]
    surf_files = glob.glob(f"{surfdir}/p_airfoilSurface.raw") or glob.glob(f"{surfdir}/airfoilSurface_p*.raw")
    arr = np.loadtxt(surf_files[0], comments="#")
    xw, yw, zw, pw = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]

    # match sampled (x,y) to the known wall theta array via nearest-neighbor
    af = JoukowskiAirfoil(eps=eps, alpha_deg=0.0)
    _, Ni, Nj = [g for g in GRID_LEVELS if g[0] == level][0]
    theta_wall = (np.arange(Ni) + 0.5) * (2 * np.pi / Ni)
    zeta_wall = af.circle_point(theta_wall)
    z_wall = af.z_of_zeta(zeta_wall)
    chord_raw = meta["chord_raw"]
    xw_ref, yw_ref = z_wall.real / chord_raw, z_wall.imag / chord_raw

    theta_matched = np.zeros(len(xw))
    for k in range(len(xw)):
        d2 = (xw_ref - xw[k]) ** 2 + (yw_ref - yw[k]) ** 2
        theta_matched[k] = theta_wall[np.argmin(d2)]

    order = np.argsort(theta_matched)
    theta_sorted = theta_matched[order]
    cp_cfd = (2.0 * pw)[order]  # Cp = p_kinematic/(0.5*Uinf^2), Uinf=1 -> Cp=2p

    _, cp_exact = af.surface_cp(n=len(theta_sorted))
    # evaluate exact Cp at the SAME matched theta (not the internal n-grid) for a clean comparison
    theta_exact_grid, cp_exact_grid = af.surface_cp(n=20000)
    cp_exact_at_matched = np.interp(theta_sorted, theta_exact_grid, cp_exact_grid,
                                     period=2 * np.pi)

    # forceCoeffs history (last window)
    fc_files = sorted(glob.glob(f"{case_dir}/postProcessing/forceCoeffs1/*/coefficient.dat"))
    cl_hist = cd_hist = None
    if fc_files:
        d = np.loadtxt(fc_files[-1], comments="#")
        # columns: Time Cd Cd(f) Cd(r) Cl Cl(f) Cl(r) CmPitch ... Cs ...
        t_col = d[:, 0]
        cd_col = d[:, 1]
        cl_col = d[:, 4]
        n_tail = max(1, len(t_col) // 5)
        cl_hist = cl_col[-n_tail:]
        cd_hist = cd_col[-n_tail:]

    ypfiles = sorted(glob.glob(f"{case_dir}/{latest}/yPlus")) or sorted(glob.glob(f"{case_dir}/postProcessing/yPlus1/*/yPlus*"))
    result = dict(
        level=level, case_dir=case_dir, meta=meta,
        t_check_s=t_check, t_run_s=t_run, t_samp_s=t_samp,
        latest_time=latest,
        cl_mean=float(np.mean(cl_hist)) if cl_hist is not None else None,
        cl_std=float(np.std(cl_hist)) if cl_hist is not None else None,
        cd_mean=float(np.mean(cd_hist)) if cd_hist is not None else None,
        cd_std=float(np.std(cd_hist)) if cd_hist is not None else None,
        theta=theta_sorted.tolist(),
        cp_cfd=cp_cfd.tolist(),
        cp_exact=cp_exact_at_matched.tolist(),
        cp_abs_err=(np.abs(cp_cfd - cp_exact_at_matched)).tolist(),
    )
    with open(f"{case_dir}/result.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    level = int(sys.argv[1])
    case_dir = sys.argv[2]
    end_time = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    timeout_s = int(sys.argv[4]) if len(sys.argv) > 4 else 1800
    n_ranks = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    r = run_level(level, case_dir, end_time, timeout_s=timeout_s, n_ranks=n_ranks)
    printable = {k: v for k, v in r.items() if k not in ("theta", "cp_cfd", "cp_exact", "cp_abs_err")}
    print(json.dumps(printable, indent=2))
