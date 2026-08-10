#!/usr/bin/env python3
"""B-52 rung-6 same-recipe replicate arm.

Pre-registration: ``B52_RUNG6_REPLICATE_PREREGISTRATION.md`` (campaign root),
commit 5c6825c7 -- read it first; this script implements it and decides
nothing on its own.

Two replicate draws at rung 6 (330,950 cells, recipe finer2/rung7/rung8),
built by moving only the background blockMesh division triple:
  6b (52 44 76), 6c (50 46 75)  from finer2's (51 45 75).

Machinery the pre-registration binds this arm to:
  * mesh birth certificate written AT CREATION from the mesh's own
    log.checkMesh (chief_engineer.mesh_certificate), and
    certificate_admits() must pass before the solver launches -- G2;
  * the shared solver runner tv._foam, which writes the fenced sha256-bound
    LEVER-ECHO block at the head of each solver log, so
    levers_verified_active is built mechanically from the log -- G4.

Stages, in order, per replicate: mesh -> certificate -> G1 cell-count
admission -> G2 certificate admission -> solve -> settle read.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO / "sdk"))
from workflows import tmr_verification as tv  # noqa: E402
from chief_engineer import lever_echo, mesh_certificate  # noqa: E402

HERE = REPO / "demo-output" / "website" / "campaign" / "B52_RUNG6_REPLICATE_runs"
RUNS = Path("/home/ubuntu/certonomous-runs")
TEMPLATE = RUNS / "study-b52-rung8-uq"
FINER2 = RUNS / "study-b52-finer2-uq"
DRIVER_LOG = HERE / "driver.log"

# --- pre-registered constants, section 3/5/6 of the pre-registration --------
FLOOR = 1.9146e-3                 # W3_MESH_NOISE_FLOOR_RESULTS.md section 4
BAR_REPRODUCE = 0.50 * FLOOR      # >= 9.573e-4
BAR_REFUTE = 0.10 * FLOOR         # <= 1.915e-4
RUNG6_CELLS = 330950
CELL_TOL = 0.02                   # G1: +/-2.0%
SETTLE_FRACTION = 0.20            # final 20% of the force history
SETTLE_CAP_FRAC = 0.05            # G3: 2 sigma < 5% of |Cd|
RANKS = 2

# Per the pre-registration section 6 G1: a draw whose achieved cell count
# misses the +/-2.0% admission band is RE-DRAWN, at most twice, with every
# missed attempt and its cell count recorded. Attempt 1 for each replicate is
# the triple named in the pre-registration; the later entries are the declared
# re-draw allowance, used only if the earlier ones miss. No Cd exists at this
# stage, so a re-draw is experiment design, not tuning (the rung-7
# attempt-1/attempt-2 precedent).
DRAWS = {
    "rung6b": [(52, 44, 76)],
    "rung6c": [(50, 46, 75), (52, 45, 74), (50, 45, 77)],
}
MAX_ATTEMPTS = 3


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    HERE.mkdir(parents=True, exist_ok=True)
    with DRIVER_LOG.open("a") as handle:
        handle.write(line + "\n")


# --------------------------------------------------------------------------
# staging and meshing


def stage(name: str, divisions: tuple[int, int, int]) -> Path:
    """Copy the verified rung-8 case and change ONLY the hex division line."""
    remote = RUNS / f"study-b52-{name}-uq"
    shutil.rmtree(remote, ignore_errors=True)
    shutil.copytree(TEMPLATE, remote, ignore=shutil.ignore_patterns(
        "processor*", "postProcessing", "log.*", "0", "*.out",
        "polyMesh", "extendedFeatureEdgeMesh"))
    bmd = remote / "system" / "blockMeshDict"
    text = bmd.read_text()
    new = f"({divisions[0]} {divisions[1]} {divisions[2]})"
    patched, count = re.subn(r"\(\d+ \d+ \d+\) simpleGrading",
                             f"{new} simpleGrading", text, count=1)
    if count != 1:
        raise RuntimeError(f"{name}: could not find the hex division triple")
    bmd.write_text(patched, newline="\n")
    return remote


def mesh(remote: Path, name: str) -> dict:
    """surfaceFeatureExtract + blockMesh + snappyHexMesh + checkMesh, then the
    birth certificate written at creation from the mesh's own checkMesh log."""
    start = time.monotonic()
    for args, logname in (
        (["surfaceFeatureExtract"], "log.surfaceFeatureExtract"),
        (["blockMesh"], "log.blockMesh"),
        (["snappyHexMesh", "-overwrite"], "log.snappyHexMesh"),
        (["checkMesh"], "log.checkMesh"),
    ):
        result = tv._foam(args, remote, logname, timeout=1800)
        if result.returncode != 0:
            raise RuntimeError(f"{name}: {args[0]} rc={result.returncode}")
    wall = time.monotonic() - start
    check_text = (remote / "log.checkMesh").read_text(errors="replace")
    cert = mesh_certificate.write_certificate(
        remote / "constant", check_log_text=check_text,
        generator=f"snappyHexMesh, B52 rung-6 replicate {name}, "
                  f"B52_RUNG6_REPLICATE_PREREGISTRATION.md")
    if cert is None:
        raise RuntimeError(f"{name}: no birth certificate could be written "
                           f"(charter v1.5 section 9)")
    log(f"{name}: meshed {cert['cells']} cells in {wall:.1f}s, certificate "
        f"verdict={cert['verdict']} skew={cert['max_skewness']} "
        f"nonOrtho={cert['max_non_orthogonality']}")
    return {"mesh_wall_s": round(wall, 1), "certificate": cert}


# --------------------------------------------------------------------------
# gates


def g1_solo(cells: int) -> bool:
    """The per-replicate limb of G1, applied at meshing time to decide a
    re-draw before any solver has been launched."""
    return abs((cells - RUNG6_CELLS) / RUNG6_CELLS) <= CELL_TOL


def gate_g1(cells_by_name: dict[str, int]) -> dict:
    """Cell-count admission: within +/-2.0% of 330,950 and of each other."""
    reasons = []
    for name, cells in cells_by_name.items():
        dev = (cells - RUNG6_CELLS) / RUNG6_CELLS
        if abs(dev) > CELL_TOL:
            reasons.append(f"{name}: {cells} is {dev:+.2%} vs rung 6")
    counts = list(cells_by_name.values())
    pair = abs(counts[0] - counts[1]) / min(counts) if len(counts) == 2 else 0.0
    if pair > CELL_TOL:
        reasons.append(f"replicates {pair:+.2%} apart from each other")
    return {"gate": "G1 cell-count admission", "passed": not reasons,
            "reasons": reasons,
            "deviations": {n: round((c - RUNG6_CELLS) / RUNG6_CELLS, 6)
                           for n, c in cells_by_name.items()},
            "pairwise_cell_deviation": round(pair, 6)}


def gate_g2(remote: Path, name: str) -> tuple[bool, str]:
    """Birth-certificate admission, refused BEFORE the solver launches."""
    admitted, reason = mesh_certificate.certificate_admits(remote / "constant")
    log(f"{name}: G2 certificate admission -> {admitted} ({reason})")
    return admitted, reason


# --------------------------------------------------------------------------
# solve and read


def solve(remote: Path, name: str) -> dict:
    admitted, reason = gate_g2(remote, name)
    if not admitted:
        raise RuntimeError(f"{name}: mesh refused at entry: {reason}")
    shutil.rmtree(remote / "0", ignore_errors=True)
    shutil.copytree(remote / "0.orig", remote / "0")
    start = time.monotonic()
    pf = tv._foam(["potentialFoam", "-writephi"], remote,
                  "log.potentialFoam", timeout=900)
    if pf.returncode != 0:
        raise RuntimeError(f"{name}: potentialFoam rc={pf.returncode}")
    dp = tv._foam(["decomposePar", "-force"], remote, "log.decomposePar",
                  timeout=900)
    if dp.returncode != 0:
        raise RuntimeError(f"{name}: decomposePar rc={dp.returncode}")
    sf = tv._foam(["mpirun", "-np", str(RANKS), "simpleFoam", "-parallel"],
                  remote, "log.simpleFoam", timeout=5400)
    wall = time.monotonic() - start
    log_text = (remote / "log.simpleFoam").read_text(errors="replace")
    exec_t = clock_t = None
    for m in re.finditer(r"ExecutionTime = ([0-9.]+) s\s+ClockTime = (\d+) s",
                         log_text):
        exec_t, clock_t = float(m.group(1)), float(m.group(2))
    return {"solve_wall_s": round(wall, 1), "returncode": sf.returncode,
            "execution_time_s": exec_t, "clock_time_s": clock_t,
            "core_min_clock": round((clock_t or 0) * RANKS / 60.0, 3),
            "core_min_exec": round((exec_t or 0) * RANKS / 60.0, 3),
            "levers_verified_active":
                lever_echo.levers_verified_active(log_text)}


def read_coefficients(remote: Path) -> list[tuple[float, float]]:
    """(time, Cd) rows from the family's coefficient.dat."""
    base = remote / "postProcessing" / "forceCoeffs1"
    dats = sorted(base.glob("*/coefficient.dat"))
    if not dats:
        raise RuntimeError(f"{remote}: no coefficient.dat")
    header, rows = [], []
    for path in dats:
        for line in path.read_text(errors="replace").splitlines():
            if line.startswith("#"):
                if "Time" in line and "Cd" in line:
                    header = line.lstrip("#").split()
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            rows.append([float(v) for v in parts])
    if "Cd" not in header:
        raise RuntimeError(f"{remote}: coefficient.dat header has no Cd column")
    idx = header.index("Cd")
    return [(r[0], r[idx]) for r in rows if len(r) > idx]


def settle(remote: Path, name: str) -> dict:
    """The family's convention: Cd = mean over the final 20% of the history;
    2 sigma over the same window; halves drift over its two halves."""
    rows = read_coefficients(remote)
    n = len(rows)
    window = rows[-max(1, int(round(n * SETTLE_FRACTION))):]
    vals = [v for _, v in window]
    m = len(vals)
    mean = sum(vals) / m
    var = sum((v - mean) ** 2 for v in vals) / (m - 1) if m > 1 else 0.0
    two_sigma = 2.0 * var ** 0.5
    half = m // 2
    first = sum(vals[:half]) / half if half else float("nan")
    second = sum(vals[half:]) / (m - half) if m - half else float("nan")
    passed = two_sigma < SETTLE_CAP_FRAC * abs(mean)
    log(f"{name}: rows={n} window={m} Cd={mean:.9f} 2sigma={two_sigma:.4e} "
        f"({two_sigma / abs(mean):.4%} of |Cd|) G3={'PASS' if passed else 'FAIL'}")
    return {"rows": n, "window_rows": m, "cd": mean, "two_sigma": two_sigma,
            "two_sigma_frac_of_cd": two_sigma / abs(mean),
            "halves_drift": second - first,
            "window_min": min(vals), "window_max": max(vals),
            "g3_settled": passed}


# --------------------------------------------------------------------------


def verdict(d6: float) -> dict:
    if d6 >= BAR_REPRODUCE:
        branch = "REPRODUCE"
        reading = ("the RECIPE owns the floor -- castellation-driven draw "
                   "sensitivity")
    elif d6 <= BAR_REFUTE:
        branch = "NOT_REPRODUCE"
        reading = ("the floor is not draw-generated at this rung; the fork's "
                   "second branch (iteration-history noise, settle gate needs "
                   "work) is the reading")
    else:
        branch = "UNDECIDED"
        reading = ("between 10% and 50% of the floor: a one-pair estimator "
                   "distinguishes nothing here and no branch is claimed")
    return {"d6": d6, "floor": FLOOR, "d6_over_floor": d6 / FLOOR,
            "bar_reproduce": BAR_REPRODUCE, "bar_refute": BAR_REFUTE,
            "branch": branch, "reading": reading}


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log("B52 rung-6 replicate arm starting "
        "(prereg B52_RUNG6_REPLICATE_PREREGISTRATION.md, commit 5c6825c7)")
    results: dict[str, dict] = {}

    # Stage 1: mesh both draws sequentially (1 core each), certificate at
    # creation. No solver has launched at this point and no Cd exists, so a
    # re-draw here is experiment design (pre-registration section 6 G1).
    for name, candidates in DRAWS.items():
        attempts = []
        admitted_case = None
        for divisions in candidates[:MAX_ATTEMPTS]:
            # Reuse a mesh this arm already built and certified for this exact
            # triple, so a re-draw of one replicate never re-spends the other.
            reuse = RUNS / f"study-b52-{name}-uq"
            existing = mesh_certificate.read_certificate(reuse / "constant") \
                if reuse.exists() else None
            same_triple = False
            if existing is not None and (reuse / "system" / "blockMeshDict").exists():
                same_triple = (f"({divisions[0]} {divisions[1]} {divisions[2]})"
                               in (reuse / "system" / "blockMeshDict").read_text())
            if existing is not None and same_triple:
                info = {"mesh_wall_s": None, "certificate": existing}
                log(f"{name}: reusing certified mesh for {divisions}, "
                    f"{existing['cells']} cells")
            else:
                remote = stage(name, divisions)
                info = mesh(remote, name)
            cells = info["certificate"]["cells"]
            passed = g1_solo(cells)
            attempts.append({"divisions": list(divisions), "cells": cells,
                             "deviation_vs_rung6": (cells - RUNG6_CELLS) / RUNG6_CELLS,
                             "admitted": passed,
                             "max_skewness": info["certificate"]["max_skewness"],
                             "max_non_orthogonality":
                                 info["certificate"]["max_non_orthogonality"],
                             "certificate_verdict": info["certificate"]["verdict"]})
            log(f"{name}: attempt {len(attempts)} {divisions} -> {cells} cells, "
                f"{(cells - RUNG6_CELLS) / RUNG6_CELLS:+.2%} vs rung 6, "
                f"{'ADMITTED' if passed else 'RE-DRAW'}")
            if passed:
                admitted_case = RUNS / f"study-b52-{name}-uq"
                results[name] = {"divisions": list(divisions),
                                 "case": str(admitted_case),
                                 "draw_attempts": attempts}
                results[name].update(info)
                break
        if admitted_case is None:
            results[name] = {"draw_attempts": attempts, "case": None,
                             "divisions": None}
            (HERE / "record.json").write_text(json.dumps(
                {"stage": "G1 refusal: re-draw allowance exhausted",
                 "replicates": results, "timestamp": now()},
                indent=2, sort_keys=True, default=str) + "\n")
            log(f"{name}: re-draw allowance exhausted -- G1 REFUSED, "
                f"no solve spent.")
            return 2

    cells = {n: r["certificate"]["cells"] for n, r in results.items()}
    g1 = gate_g1(cells)
    log(f"G1: {g1}")
    if not g1["passed"]:
        (HERE / "record.json").write_text(json.dumps(
            {"stage": "G1 refusal", "g1": g1, "replicates": results,
             "timestamp": now()}, indent=2, sort_keys=True, default=str) + "\n")
        log("G1 REFUSED -- no solve spent. See record.json.")
        return 2

    # Stage 2: solve both, through the shared runner so the lever echo fires.
    for name in DRAWS:
        remote = Path(results[name]["case"])
        results[name].update(solve(remote, name))
        results[name].update({"settle": settle(remote, name)})
        shutil.copy2(remote / "log.checkMesh", HERE / f"{name}.log.checkMesh")
        shutil.copy2(remote / "constant" / "birth_certificate.json",
                     HERE / f"{name}.birth_certificate.json")

    # Stage 3: the pre-registered readings.
    names = list(DRAWS)
    cd_b, cd_c = (results[n]["settle"]["cd"] for n in names)
    d6 = abs(cd_b - cd_c)
    v = verdict(d6)

    # Secondary readings (section 4), none verdict-bearing.
    finer2 = settle(FINER2, "finer2 (2026-08-01/02 draw, re-read)")
    three = [cd_b, cd_c, finer2["cd"]]
    sigma_max = max(results[n]["settle"]["two_sigma"] for n in names)
    echo_b = {e["file"]: e["sha256"]
              for e in results[names[0]]["levers_verified_active"]["verified"]}
    echo_c = {e["file"]: e["sha256"]
              for e in results[names[1]]["levers_verified_active"]["verified"]}
    g4 = {"gate": "G4 lever-echo equality between the two replicates",
          "passed": bool(echo_b) and echo_b == echo_c,
          "files_echoed": len(echo_b),
          "mismatched": sorted(set(echo_b) ^ set(echo_c)) or
                        sorted(k for k in echo_b
                               if echo_c.get(k) != echo_b[k])}
    log(f"G4: {g4}")

    record = {
        "arm": "B52 rung-6 same-recipe replicates",
        "prereg": "campaign/B52_RUNG6_REPLICATE_PREREGISTRATION.md",
        "prereg_commit": "5c6825c7",
        "timestamp": now(),
        "replicates": results,
        "g1_cell_admission": g1,
        "g4_lever_echo_equality": g4,
        "verdict": v,
        "secondary": {
            "finer2_reread": finer2,
            "r6_range_over_three_draws": max(three) - min(three),
            "d6_over_max_two_sigma": d6 / sigma_max if sigma_max else None,
            "max_two_sigma": sigma_max,
            "d6_over_rung6_to_7_increment": d6 / 4.055e-3,
            "d6_over_rung7_to_8_increment": d6 / 2.78e-4,
        },
        "cost_core_min": {
            "mesh": round(sum(r["mesh_wall_s"] for r in results.values())
                          / 60.0, 3),
            "solve_clock": round(sum(r["core_min_clock"]
                                     for r in results.values()), 3),
            "solve_exec": round(sum(r["core_min_exec"]
                                    for r in results.values()), 3),
        },
    }
    (HERE / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True, default=str) + "\n")
    log(f"VERDICT {v['branch']}: D6={d6:.6e} = {v['d6_over_floor']:.3f} x floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
