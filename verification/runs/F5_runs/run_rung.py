#!/usr/bin/env python3
"""F5a rung driver split into STAGE / SOLVE(launch_solve.sh) / HARVEST so the
long pimpleFoam solve goes through the sanctioned launcher (D12/launch_solve.sh)
instead of a plain foreground subprocess.call that dies with the calling
agent's turn.

  stage     builds the case, blockMesh+checkMesh (fast, foreground)
  launch    prints the exact launch_solve.sh command to run the solve
  harvest   after the solve is done, copies postProcessing back and computes
            the same record.json cylinder_ladder.run_case() would have
            produced (identical stats/probe extraction code, reused, not
            reimplemented)

This performs no physics differently from cylinder_ladder.run_case(); it only
relocates the solve step behind launch_solve.sh so the collector survives a
dropped connection.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))
# NOT `parents[4]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[4]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
_REPO_ROOT = next((_p for _p in Path(__file__).resolve().parents
                  if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
sys.path.insert(0, str(_REPO_ROOT / "sdk"))

import cylinder_ladder as CL  # noqa: E402
from workflows.tmr_verification import (  # noqa: E402
    _foam, _copy_best_effort, time_weighted_stats, measure_period, halves_drift,
)
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402

_RUN_ROOT = Path.home() / "certonomous-runs" / "f5a-cylinder-ladder"


def stage(name: str, out_dir: Path, **build_kwargs) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case = out_dir / "case"
    remote_dir = _RUN_ROOT / name
    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)

    params = CL.build_case(case, **build_kwargs)
    shutil.copytree(case, remote_dir)

    timings = {}
    for step, args, timeout in (("blockMesh", ["blockMesh"], 900),
                                ("checkMesh", ["checkMesh", "-allTopology", "-allGeometry"], 900)):
        import time
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{step}", timeout=timeout)
        timings[step] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{step}", out_dir / f"log.{step}")
        print(f"[{name}] {step} done in {timings[step]:.1f}s (exit {result.returncode})")
        if step == "blockMesh" and result.returncode != 0:
            raise RuntimeError(f"{name}: blockMesh failed")

    (out_dir / "stage_params.json").write_text(json.dumps(
        {"params": params, "timings": timings, "remote_dir": str(remote_dir)}, indent=2))
    print(f"[{name}] staged at {remote_dir}, cells={params['cells']}")
    return {"params": params, "remote_dir": remote_dir, "timings": timings}


def harvest(name: str, out_dir: Path, ranks: int = 1) -> dict:
    out_dir = Path(out_dir)
    staged = json.loads((out_dir / "stage_params.json").read_text())
    params = staged["params"]
    remote_dir = Path(staged["remote_dir"])
    timings = dict(staged["timings"])

    log_path = remote_dir / "log.pimpleFoam"
    if not log_path.exists():
        raise RuntimeError(f"{name}: no log.pimpleFoam in {remote_dir} -- solve did not run")
    _copy_best_effort(log_path, out_dir / "log.pimpleFoam")
    tail = log_path.read_text(errors="replace").splitlines()
    if not any("End" in l or "ExecutionTime" in l for l in tail[-40:]):
        print(f"[{name}] WARNING: log.pimpleFoam does not look terminated cleanly "
              f"(last lines): " + "\n".join(tail[-5:]))

    shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
    _copy_best_effort(remote_dir / "postProcessing", out_dir / "postProcessing")
    coeff_files = sorted((out_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"{name}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history["Time"]
    end_time = params["end_time"]
    t_start = 0.5 * end_time
    cd_stats = time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = time_weighted_stats(times, history["Cl"], t_start)
    period = measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"{name}: averaging window empty (ran to "
                           f"t={times[-1] if times else 0:g}, requested {t_start:g}); "
                           f"run is INCOMPLETE, not a result")
    drift = halves_drift(times, history["Cd"], cd_stats["window_start"], cd_stats["window_end"])
    if drift is None:
        raise RuntimeError(f"{name}: halves_drift undecidable -- stationarity UNKNOWN")

    yplus_files = sorted((out_dir / "postProcessing").rglob("yPlus.dat"))
    yplus_text = yplus_files[-1].read_text(errors="replace") if yplus_files else ""
    cpb = CL.base_cpb(out_dir, t_start)
    lr = CL.recirculation_length(out_dir, t_start, params["centerline_points"])

    from workflows.cylinder_vortex_shedding import DIAMETER, U_INF
    strouhal = (DIAMETER / (period * U_INF)) if period else None

    # wall time: parse ExecutionTime of the LAST line in the log for the
    # true solver wall time regardless of how many restarts contributed.
    import re
    exec_times = re.findall(r"ExecutionTime = ([\d.]+) s", "\n".join(tail))
    solve_wall = float(exec_times[-1]) if exec_times else None
    timings["pimpleFoam"] = solve_wall

    record = {
        "name": name, "reynolds": params["reynolds"], "nu": params["nu"],
        "turbulence": params["turbulence"], "cells": params["cells"],
        "n_radial": params["n_radial"], "n_tangential": params["n_tangential"],
        "first_cell": params["first_cell"], "farfield_diameters": params["farfield_diameters"],
        "ranks": ranks, "end_time": end_time, "dt0": params["dt0"],
        "max_co": params["max_co"], "steps": len(times),
        "cd_mean": cd_stats["mean"], "cd_band": cd_stats["band"],
        "cd_relative_drift": drift["relative_drift"],
        "cd_first_half_mean": drift["first_half_mean"],
        "cd_second_half_mean": drift["second_half_mean"],
        "cl_mean": cl_stats["mean"], "cl_band": cl_stats["band"],
        "averaging_window": [cd_stats["window_start"], cd_stats["window_end"]],
        "period": period, "strouhal": strouhal,
        "cpb": cpb, "recirculation": lr,
        "yplus_raw": yplus_text.strip().splitlines()[-3:] if yplus_text else [],
        "wall_seconds": sum(v for v in timings.values() if v is not None), "timings": timings,
        "stationary": drift["relative_drift"] <= 0.10,
        "final_time_reached": times[-1] if times else None,
    }
    (out_dir / "record.json").write_text(json.dumps(record, indent=2, default=str))
    lr_txt = f"Lr/D {lr['lr_over_d']:.3f}" if lr and lr["lr_over_d"] else "Lr/D not found"
    cpb_txt = f"-Cpb {cpb['cpb_magnitude']:.3f}" if cpb else "Cpb n/a"
    st_txt = f"St {strouhal:.4f}" if strouhal else "no period detected"
    print(f"[{name}] Cd {cd_stats['mean']:.4f} (drift {100*drift['relative_drift']:.1f}%), "
          f"{st_txt}, {cpb_txt}, {lr_txt}, wall {record['wall_seconds']:.0f}s, "
          f"final_t={record['final_time_reached']}")
    return record


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["stage", "harvest"])
    p.add_argument("--name", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--reynolds", type=float)
    p.add_argument("--turbulence", choices=["laminar", "kOmegaSST"])
    p.add_argument("--n-radial", type=int)
    p.add_argument("--n-tangential", type=int)
    p.add_argument("--first-cell", type=float)
    p.add_argument("--farfield-diameters", type=float, default=20.0)
    p.add_argument("--end-time", type=float, default=90.0)
    p.add_argument("--dt0", type=float)
    p.add_argument("--max-co", type=float, default=1.5)
    p.add_argument("--perturbation", type=float, default=0.1)
    p.add_argument("--ranks", type=int, default=1)
    a = p.parse_args()
    if a.mode == "stage":
        stage(a.name, Path(a.out), reynolds=a.reynolds, turbulence=a.turbulence,
              farfield_diameters=a.farfield_diameters, n_radial=a.n_radial,
              n_tangential=a.n_tangential, first_cell=a.first_cell,
              end_time=a.end_time, dt0=a.dt0, max_co=a.max_co,
              perturbation=a.perturbation)
    else:
        harvest(a.name, Path(a.out), ranks=a.ranks)
