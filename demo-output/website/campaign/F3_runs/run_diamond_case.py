#!/usr/bin/env python3
import sys, os, math, subprocess, time, json, glob, re
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from make_diamond_case import make_case

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"
GAMMA = 1.4
Z_THICKNESS = 0.01  # from -0.005 to 0.005 in make_diamond_case.py


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


def run_one(case_dir, M, eps_deg, res_level, beta_exact_deg, cd_exact):
    os.makedirs(case_dir, exist_ok=True)
    meta = make_case(case_dir, M, eps_deg, res_level, beta_exact_deg)
    t_mesh = sh("blockMesh", case_dir, f"{case_dir}/log.blockMesh")
    sh("checkMesh -noTopology", case_dir, f"{case_dir}/log.checkMesh")
    t_run = sh("rhoCentralFoam", case_dir, f"{case_dir}/log.rhoCentralFoam")

    force_files = sorted(glob.glob(f"{case_dir}/postProcessing/forces1/*/force.dat"))
    lines = [l for l in open(force_files[-1]) if not l.startswith("#")]
    last = lines[-1].split()
    Fx_slab = float(last[1])  # total_x, pressure-only (viscous=0, inviscid)

    Fx_per_span_upper = Fx_slab / Z_THICKNESS
    Fx_per_span_total = 2 * Fx_per_span_upper  # upper + mirrored lower
    q1 = 0.5 * GAMMA * 1.0 * M**2  # p1=1
    cd_computed = Fx_per_span_total / (q1 * meta["c"])

    result = dict(
        case_dir=case_dir, M=M, eps_deg=eps_deg, res_level=res_level,
        ncells=meta["ncells"], t_mesh_s=t_mesh, t_run_s=t_run,
        Fx_slab=Fx_slab, Fx_per_span_total=Fx_per_span_total,
        cd_exact=cd_exact, cd_computed=cd_computed,
        deviation=cd_computed - cd_exact,
        deviation_pct=100 * (cd_computed - cd_exact) / cd_exact,
    )
    with open(f"{case_dir}/result.json", "w") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    case_dir, M, eps_deg, res_level, beta_exact_deg, cd_exact = (
        sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4],
        float(sys.argv[5]), float(sys.argv[6]))
    r = run_one(case_dir, M, eps_deg, res_level, beta_exact_deg, cd_exact)
    print(json.dumps(r, indent=2))
