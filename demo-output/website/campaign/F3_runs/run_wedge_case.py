#!/usr/bin/env python3
import sys, os, math, subprocess, time, json, glob, re
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from make_wedge_case import make_case
from foam_io import read_patch_scalar

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


def write_sampledict(case_dir, Lramp, H, n_stations=6, frac_lo=0.12, frac_hi=0.88):
    xs = np.linspace(frac_lo, frac_hi, n_stations) * Lramp
    sets = []
    for i, x in enumerate(xs):
        name = f"x{i}"
        sets.append(f"    {name} {{ type uniform; axis y; start ({x:.6f} 0 0); "
                     f"end ({x:.6f} {H:.6f} 0); nPoints 800; }}")
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
    wedgeSurface
    {
        type patch;
        patches (obstacle);
        interpolate false;
        triangulate false;
    }
);
"""
    with open(f"{case_dir}/system/surfaceSampleDict", "w") as f:
        f.write(surf_content)
    return list(xs)


def find_shock_y(xy_path, y_lo_frac=0.0):
    d = np.loadtxt(xy_path)
    y, T, p, rho = d[:, 0], d[:, 1], d[:, 2], d[:, 3]
    if len(y) < 10:
        return None
    grad = np.gradient(rho, y)
    i = np.argmin(grad)  # most negative slope = density drop going outward = shock crossing
    return y[i], p, rho, y


def run_one(case_dir, M, theta_deg, res_level, beta_exact_deg, ranks=1):
    os.makedirs(case_dir, exist_ok=True)
    meta = make_case(case_dir, M, theta_deg, res_level, beta_exact_deg)
    t_mesh = sh("blockMesh", case_dir, f"{case_dir}/log.blockMesh")
    sh("checkMesh -noTopology", case_dir, f"{case_dir}/log.checkMesh")
    ncells = meta["nx1"] * meta["ny"] + meta["nx2"] * meta["ny"]
    t_run = sh("rhoCentralFoam", case_dir, f"{case_dir}/log.rhoCentralFoam")

    xs = write_sampledict(case_dir, meta["Lramp"], meta["H"])
    t_samp = sh("postProcess -func sampleDict -latestTime", case_dir, f"{case_dir}/log.sample")
    t_surf = sh("postProcess -func surfaceSampleDict -latestTime", case_dir, f"{case_dir}/log.surfsample")

    # find latest time dir
    tdirs = [d for d in os.listdir(case_dir) if re.match(r"^[0-9]+\.?[0-9]*$", d)]
    tdirs = sorted(tdirs, key=lambda s: float(s))
    latest = tdirs[-1]
    sampdir = sorted(glob.glob(f"{case_dir}/postProcessing/sampleDict/*"))[-1]

    shock_pts = []
    for i, x in enumerate(xs):
        cands = glob.glob(f"{sampdir}/x{i}_*.xy")
        if not cands:
            continue
        f = cands[0]
        res = find_shock_y(f)
        if res is None:
            continue
        y_s, p_arr, rho_arr, y_arr = res
        shock_pts.append((x, y_s))

    shock_pts = np.array(shock_pts)

    def linfit(pts):
        if len(pts) < 3:
            return None, None
        xk, yk = pts[:, 0], pts[:, 1]
        A = np.vstack([xk, np.ones_like(xk)]).T
        m_slope, c0 = np.linalg.lstsq(A, yk, rcond=None)[0]
        beta_deg = math.degrees(math.atan(m_slope))
        pred = m_slope * xk + c0
        ss_res = np.sum((yk - pred) ** 2)
        ss_tot = np.sum((yk - yk.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
        return beta_deg, r2

    # station 0 sits nearest the sharp leading corner, where the shock origin is a
    # singular point and numerical/corner smearing contaminates the density-gradient
    # peak; standard practice (and our own grid study, see report) is to fit the
    # shock locus using stations away from that corner.
    beta_all_deg, r2_all = linfit(shock_pts)
    beta_computed_deg, fit_r2 = linfit(shock_pts[1:]) if len(shock_pts) > 3 else (beta_all_deg, r2_all)

    # surface pressure: read the patch-sampled surface (exact CFD face-centre value)
    surfdir = sorted(glob.glob(f"{case_dir}/postProcessing/surfaceSampleDict/*"))[-1]
    surf_files = glob.glob(f"{surfdir}/wedgeSurface_p*.raw") or glob.glob(f"{surfdir}/*p*.raw")
    arr = np.loadtxt(surf_files[0], comments="#")
    x_wall, p_wall = arr[:, 0], arr[:, 3]
    order = np.argsort(x_wall)
    x_wall, p_wall = x_wall[order], p_wall[order]
    mid = (x_wall > 0.3 * meta["Lramp"]) & (x_wall < 0.85 * meta["Lramp"])
    p_wall_mean = float(np.mean(p_wall[mid]))
    p_wall_std = float(np.std(p_wall[mid]))

    result = dict(
        case_dir=case_dir, M=M, theta_deg=theta_deg, res_level=res_level,
        ncells=ncells, t_mesh_s=t_mesh, t_run_s=t_run, t_sample_s=t_samp,
        beta_exact_deg=beta_exact_deg, beta_computed_deg=beta_computed_deg,
        fit_r2=fit_r2, beta_all_stations_deg=beta_all_deg, fit_r2_all_stations=r2_all,
        shock_pts=shock_pts.tolist(),
        p_wall_mean=p_wall_mean, p_wall_std=p_wall_std,
        p_wall_profile=[[float(x), float(p)] for x, p in zip(x_wall, p_wall)],
        latest_time=latest,
    )
    with open(f"{case_dir}/result.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    case_dir, M, theta_deg, res_level, beta_exact_deg = sys.argv[1], float(sys.argv[2]), \
        float(sys.argv[3]), sys.argv[4], float(sys.argv[5])
    r = run_one(case_dir, M, theta_deg, res_level, beta_exact_deg)
    print(json.dumps({k: v for k, v in r.items() if k not in ("shock_pts", "p_wall_profile")}, indent=2))
