#!/usr/bin/env python3
"""F12 rung driver -- RAE 2822, AGARD AR-138 Case 9.

Launches ONE registered rung of verification/campaign/F12_PREREGISTRATION.md
(v1.2, blob 41ec748a06b513414101dca9780107f08a25ddec) through the frozen
grading path sdk/workflows/rae2822_case9.py, and writes result.json beside the
case.

This driver ADDS NO PHYSICS AND NO GATE.  Every number it writes is produced by
a function of the frozen module: run_case, cp_deviation, shock_location,
mesh_gate, solver_converged.  What it adds is (a) the rule-4 ABSENT guard the
frozen run_case does NOT have -- run_case rmtree's an existing case directory,
which would destroy evidence -- (b) a wall-clock record, and (c) the cap
arithmetic of the pre-registration's 2026-08-23 addendum section 5.

Usage:  run_f12_rung.py <rung-key>
"""
import json
import pathlib
import sys
import time
import datetime
import traceback

REPO = pathlib.Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "sdk"))

from sdk.workflows import rae2822_case9 as W  # noqa: E402

RUN_ROOT = REPO / "verification" / "runs" / "F12_runs"

# The five run directories the pre-registration registers by name
# (2026-08-23 COSTED ADDENDUM section 1, re-asserted in the 2026-08-25
# MESH-SIMILARITY AMENDMENT section 1), with their caps from section 5.
REGISTERED = {
    "coarse_workshop_M0.734_a2.79":
        dict(level=0, mach=0.734, alpha=2.79, farfield_r=W.FARFIELD_R, cap_core_min=120.0),
    "medium_workshop_M0.734_a2.79":
        dict(level=1, mach=0.734, alpha=2.79, farfield_r=W.FARFIELD_R, cap_core_min=160.0),
    "fine_workshop_M0.734_a2.79":
        dict(level=2, mach=0.734, alpha=2.79, farfield_r=W.FARFIELD_R, cap_core_min=700.0),
    "medium_tape_M0.730_a2.79":
        dict(level=1, mach=0.730, alpha=2.79, farfield_r=W.FARFIELD_R, cap_core_min=160.0),
    "medium_farfield2x_M0.734_a2.79":
        dict(level=1, mach=0.734, alpha=2.79, farfield_r=2.0 * W.FARFIELD_R, cap_core_min=160.0),
}

RANKS = 1
ITERATIONS = 6000
MESH_RESERVE_S = 60.0   # reserved out of the cap for blockMesh + checkMesh


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main(argv):
    if len(argv) != 2 or argv[1] not in REGISTERED:
        sys.stderr.write("usage: run_f12_rung.py <" + "|".join(REGISTERED) + ">\n")
        return 2
    key = argv[1]
    spec = REGISTERED[key]
    case = RUN_ROOT / key

    # ---- rule 4 guard: REFUSE a case that already exists ------------------
    # run_case() rmtree's it.  A rung is fired exactly once.
    existing = [k for k in REGISTERED if (RUN_ROOT / k).exists()]
    if existing:
        sys.stderr.write("REFUSING: registered run directories already exist: "
                         + ", ".join(sorted(existing)) + "\n")
        return 3

    cap_wall_s = spec["cap_core_min"] * 60.0 / RANKS
    solver_timeout = cap_wall_s - MESH_RESERVE_S

    started_utc = utc()
    t0 = time.time()
    status = "OK"
    record = None
    err = None
    try:
        record = W.run_case(
            mach=spec["mach"], alpha_deg=spec["alpha"], work_dir=case,
            level=W.LEVELS[spec["level"]], iterations=ITERATIONS,
            farfield_r=spec["farfield_r"], ranks=RANKS,
            timeout=solver_timeout, log=lambda m: print(m, flush=True))
    except Exception as exc:                       # a crash is a FINDING
        status = type(exc).__name__
        err = traceback.format_exc()
    wall_s = time.time() - t0
    ended_utc = utc()

    out = {
        "rung": key,
        "preregistration": "verification/campaign/F12_PREREGISTRATION.md",
        "preregistration_blob": "41ec748a06b513414101dca9780107f08a25ddec",
        "grading_path_blob": {
            "sdk/workflows/rae2822_case9.py": "a18314f77160b7a58f443073850a44b4d8fada7d",
            "sdk/workflows/tmr_verification.py": "404ce4323127d1cb24836d67720d94ba9f5d401e",
            "scripts/roache_triple.py": "8dee0d31e94d3f59d28658f88a4cd6df80ae8e39"},
        "status": status,
        "started_utc": started_utc, "ended_utc": ended_utc,
        "driver_wall_seconds": round(wall_s, 1),
        "ranks": RANKS,
        "cap_core_min": spec["cap_core_min"],
        "solver_timeout_s": solver_timeout,
    }
    if err:
        out["traceback"] = err
    if record is not None:
        out["record"] = record
        # ---- gate quantities, all from the frozen module ------------------
        exp = W.load_experiment_cp()
        grade = {}
        for surface in ("upper", "lower"):
            cfd = record.get("surfaces", {}).get(surface)
            grade[surface] = (W.cp_deviation(cfd, exp[surface]) if cfd else None)
        grade["experiment_shock"] = W.shock_location(exp["upper"], spec["mach"])
        out["grade"] = grade
        core_min = record["core_seconds"] * 1.0 / 60.0
        out["measured_core_min"] = round(core_min, 3)
        out["cap_breached"] = core_min > spec["cap_core_min"]
        cells = record.get("cells") or 1
        it = record.get("iterations_run") or 1
        solve_s = record.get("timings", {}).get("rhoSimpleFoam", 0.0)
        out["measured_s_per_cell_iteration"] = solve_s / (cells * it)

    (case if case.exists() else RUN_ROOT).joinpath(
        "result.json" if case.exists() else f"result_{key}.json").write_text(
            json.dumps(out, indent=2, default=str) + "\n")
    print("STATUS " + status + "  wall_s " + str(round(wall_s, 1)), flush=True)
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
