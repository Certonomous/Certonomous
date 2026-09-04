#!/usr/bin/env python3
"""Entry 10 alternative-generator arm. Pre-registration:
GEN_ALT_PREREGISTRATION.md (same directory) -- this script implements it.

Two blockMesh C-grid meshes at exactly the pyHyp pair's cell counts with the
same user-facing refinement moves; birth certificate at creation; quality
matrix vs the pyHyp measured values; one 500-iteration smoke solve on the
refined mesh through the module's own proven harness.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
from pathlib import Path

REPO = Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO / "sdk"))
from workflows import tmr_verification as tv  # noqa: E402
from workflows import transonic_airfoil as ta  # noqa: E402
from workflows.tmr_verification import NacaGridLevel  # noqa: E402
from scripts import model_form_batch as mfb  # noqa: E402
from chief_engineer import lever_echo  # noqa: E402

# THE SOLVE-EVIDENCE GUARD.  Loaded by explicit path rather than by putting
# `scripts/` on sys.path: this module must not be shadowable by anything, and a
# guard that can be silently replaced is not a guard.  If it is missing, this
# file refuses to run at all -- deleting without the guard IS the defect.
# Pattern copied from verification/runs/F5_runs/run_rung.py:44-70, with ONE
# DELIBERATE DEVIATION recorded here rather than left for a reader to notice:
# F5 DERIVES its repository root by searching upward for `scripts/lab_paths.py`,
# because batch 7 changed that file's depth and silently broke a `parents[4]`
# literal.  This file already carries the absolute `REPO` literal above, which
# sys.path itself depends on, so an independently-derived second root would be a
# NEW way for the two to disagree.  The guard is anchored to the same REPO and
# the is_file() refusal below turns a wrong root into an immediate stop.
import importlib.util as _ilu  # noqa: E402

_GUARD_PATH = REPO / "scripts" / "solve_evidence_guard.py"
if not _GUARD_PATH.is_file():
    raise RuntimeError(
        f"solve-evidence guard not found at {_GUARD_PATH}; refusing to run. "
        "This driver deletes its run directories under the shared run root, "
        "and without the guard those deletes are unconditional -- see the "
        "guard's docstring for the rung that paid for it.")
if "solve_evidence_guard" in sys.modules:
    # Registered ONCE, reused everywhere.  Loading the same file twice under two
    # module objects gives SolveEvidencePresent two DISTINCT classes, and a
    # caller's `except SolveEvidencePresent` then silently misses the refusal
    # raised by the other copy -- the guard appears wired and is not.  Measured:
    # F5's integration control hit exactly that before this branch existed.
    solve_evidence_guard = sys.modules["solve_evidence_guard"]
else:
    _spec = _ilu.spec_from_file_location("solve_evidence_guard", _GUARD_PATH)
    solve_evidence_guard = _ilu.module_from_spec(_spec)
    sys.modules["solve_evidence_guard"] = solve_evidence_guard
    _spec.loader.exec_module(solve_evidence_guard)
safe_rmtree_for_restage = solve_evidence_guard.safe_rmtree_for_restage
SolveEvidencePresent = solve_evidence_guard.SolveEvidencePresent

HERE = REPO / "demo-output" / "website" / "campaign" / "GEN_ALT_runs"
RUN_ROOT = Path(tv._RUN_ROOT)
DRIVER_LOG = HERE / "driver.log"

# The matched pair, exactly as pre-registered.
PAIR = (
    ("alt_coarse", NacaGridLevel("altc", "matched-4032", 21, 21, 32), 4.0e-3),
    ("alt_refined", NacaGridLevel("altr", "matched-14720", 38, 39, 64), 2.0e-3),
)
# pyHyp measured values, from GENERATOR_FINDING_pyhyp_aspect_ratio.md.
PYHYP = {"coarse": {"cells": 4032, "max_ar": 97.87, "max_nonortho": 22.7,
                    "max_skew": 1.43},
         "refined": {"cells": 14720, "max_ar": 167.50, "max_nonortho": 27.0,
                     "max_skew": 0.86}}


def log(msg: str) -> None:
    line = f"[{mfb._now()}] {msg}"
    print(line, flush=True)
    with DRIVER_LOG.open("a") as handle:
        handle.write(line + "\n")


def rmtree_after_harvest(target: Path, what: str) -> bool:
    """Teardown that can never destroy physics.  Detection is the guard's.

    The re-stage sites are FATAL on refusal: continuing there would copy into a
    directory that still exists.  A TEARDOWN refusal is deliberately NOT fatal
    -- the delete is housekeeping, the record has already been written -- so the
    physics stays on disk, the operator is told what survived and where, and the
    driver carries on.  That is not an override flag: nothing here can be told
    to delete anyway, and there is nothing for anyone to paste.
    """
    try:
        return safe_rmtree_for_restage(target)
    except SolveEvidencePresent as exc:
        log(f"{what}: teardown PRESERVED {target} -- {exc}")
        return False


def cell_count(check_text: str) -> int | None:
    hit = re.search(r"^\s*cells:\s*(\d+)", check_text, re.MULTILINE)
    return int(hit.group(1)) if hit else None


def build_and_certify(name: str, level: NacaGridLevel,
                      first_cell: float) -> dict:
    remote = RUN_ROOT / f"genalt-{name}"
    # WAS: shutil.rmtree(remote, ignore_errors=True) -- unconditional, and
    # silent about its own failures, as the FIRST statement of the builder.  So
    # "rebuild this mesh" was the same keystroke as "destroy whatever is at that
    # name", against the shared run root that already strands one gated rung.
    # The guard refuses when the directory holds time directories > 0 with
    # fields (reconstructed or under processor*/) or a postProcessing series
    # with data rows, and names what would have been lost.  Past the guard the
    # delete no longer swallows its errors.
    safe_rmtree_for_restage(remote)
    (remote / "system").mkdir(parents=True)
    (remote / "system" / "blockMeshDict").write_text(
        ta.transonic_blockmesh_dict(level, first_cell=first_cell),
        newline="\n")
    (remote / "system" / "controlDict").write_text(
        tv._foam_header("dictionary", "controlDict", "system")
        + '\napplication simpleFoam;\nstartFrom startTime;\nstartTime 0;\n'
          'stopAt endTime;\nendTime 1;\ndeltaT 1;\nwriteControl timeStep;\n'
          'writeInterval 1;\n', newline="\n")
    # Any OpenFOAM utility needs these two present, even for a mesh-only case.
    (remote / "system" / "fvSchemes").write_text(
        tv._foam_header("dictionary", "fvSchemes", "system")
        + "\nddtSchemes { default steadyState; }\n"
          "gradSchemes { default Gauss linear; }\n"
          "divSchemes { default none; }\n"
          "laplacianSchemes { default Gauss linear corrected; }\n"
          "interpolationSchemes { default linear; }\n"
          "snGradSchemes { default corrected; }\n", newline="\n")
    (remote / "system" / "fvSolution").write_text(
        tv._foam_header("dictionary", "fvSolution", "system")
        + "\nsolvers { }\n", newline="\n")
    out_dir = HERE / name
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    for tool, args in (("blockMesh", ["blockMesh"]),
                       ("checkMesh", ["checkMesh", "-allGeometry"])):
        result = tv._foam(args, remote, f"log.{tool}", timeout=900)
        shutil.copy2(remote / f"log.{tool}", out_dir / f"log.{tool}")
        if result.returncode != 0:
            raise RuntimeError(f"{name}/{tool} failed rc={result.returncode}")
    wall = time.monotonic() - t0
    check_text = (out_dir / "log.checkMesh").read_text(errors="replace")
    meshv = mfb.mesh_verdict(check_text)
    record = {
        "run": name, "prereg": "campaign/GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md",
        "generator": "transonic_airfoil.transonic_blockmesh_dict (blockMesh C-grid)",
        "level": {"n_surf_quarter": level.n_surf_quarter,
                  "n_wake": level.n_wake, "ny": level.ny,
                  "first_cell": first_cell},
        "cells": cell_count(check_text),
        "mesh": meshv,
        "birth_certificate": "checkMesh -allGeometry at creation, log beside the mesh",
        "core_min": round(wall / 60.0, 3),
        "timestamp": mfb._now(),
    }
    (out_dir / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    log(f"{name}: cells {record['cells']}, max AR {meshv['max_aspect_ratio']}, "
        f"non-ortho {meshv['max_non_ortho']}, skew {meshv['max_skewness']}")
    return record


def smoke_solve(level: NacaGridLevel, first_cell: float) -> dict:
    name = "alt_refined_smoke"
    remote = RUN_ROOT / f"genalt-{name}"
    # WAS: shutil.rmtree(remote, ignore_errors=True) -- see build_and_certify.
    safe_rmtree_for_restage(remote)
    remote.mkdir(parents=True)
    # Module harness writes its own dicts; then swap in our matched-pair mesh.
    ta.build_case(remote, mach=0.5, alpha_deg=1.25, reynolds=6.0e6,
                  iterations=500)
    (remote / "system" / "blockMeshDict").write_text(
        ta.transonic_blockmesh_dict(level, first_cell=first_cell),
        newline="\n")
    out_dir = HERE / name
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    for tool in ("blockMesh", "checkMesh"):
        result = tv._foam([tool], remote, f"log.{tool}", timeout=900)
        shutil.copy2(remote / f"log.{tool}", out_dir / f"log.{tool}")
        if result.returncode != 0:
            raise RuntimeError(f"{name}/{tool} failed rc={result.returncode}")
    mfb.assert_mesh_certified_at_entry(remote, "DIAG", name)
    result = tv._foam(["rhoSimpleFoam"], remote, "log.rhoSimpleFoam",
                      timeout=3600)
    wall = time.monotonic() - t0
    log_text = (remote / "log.rhoSimpleFoam").read_text(errors="replace")
    shutil.copy2(remote / "log.rhoSimpleFoam", out_dir / "log.rhoSimpleFoam")
    fatal = []
    if "Foam::sigFpe::sigHandler" in log_text:
        fatal.append("S1 floating point exception")
    coeffs = mfb.history_from_log(log_text)
    record = {
        "run": name, "prereg": "campaign/GEN_ALT_runs/GEN_ALT_PREREGISTRATION.md",
        "harness": "transonic_airfoil.build_case, rhoSimpleFoam, M 0.5 / "
                   "alpha 1.25 / Re 6e6, 500 iterations (smoke test only)",
        "returncode": result.returncode, "fatal": fatal,
        "final_Cd": (coeffs.get("Cd") or [None])[-1],
        "final_Cl": (coeffs.get("Cl") or [None])[-1],
        "levers_verified_active": lever_echo.levers_verified_active(log_text),
        "core_min": round(wall / 60.0, 3),
        "timestamp": mfb._now(),
    }
    (out_dir / "record.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    log(f"{name}: rc={result.returncode} fatal={fatal} "
        f"Cd={record['final_Cd']} Cl={record['final_Cl']} "
        f"{record['core_min']} core-min")
    # WAS: shutil.rmtree(remote, ignore_errors=True) -- and this one is the
    # WORSE half of the pair, because at this line the directory holds a
    # completed 500-iteration rhoSimpleFoam solve.  Only the LOGS and two
    # scalars (final_Cd, final_Cl) have been copied out; every field written by
    # the solve was deleted here, unconditionally and silently, the moment the
    # record was written.  Re-reading that solve for anything the record does
    # not already carry was therefore impossible by construction.  Teardown now
    # preserves instead: see rmtree_after_harvest.
    rmtree_after_harvest(remote, name)
    return record


def main() -> int:
    log("alternative-generator arm starting (prereg GEN_ALT_PREREGISTRATION.md)")
    records = {}
    for name, level, first in PAIR:
        records[name] = build_and_certify(name, level, first)
        # WAS: shutil.rmtree(..., ignore_errors=True).  In the normal path this
        # directory is mesh-only, and the guard lets mesh-only through -- the
        # ladder keeps working.  It preserves instead only if a solve ever left
        # physics under this name, which is exactly when deleting is wrong.
        rmtree_after_harvest(RUN_ROOT / f"genalt-{name}", name)
    ar_c = records["alt_coarse"]["mesh"]["max_aspect_ratio"]
    ar_r = records["alt_refined"]["mesh"]["max_aspect_ratio"]
    factor = (ar_r / ar_c) if (ar_c and ar_r) else None
    log(f"max-AR refinement factor: alternative {factor} vs pyHyp 1.71")
    matrix = {
        "pyhyp_measured": PYHYP,
        "alternative": {n: {"cells": r["cells"], **r["mesh"]}
                        for n, r in records.items()},
        "alt_max_ar_refinement_factor": factor,
        "pyhyp_max_ar_refinement_factor": round(167.50 / 97.87, 3),
    }
    (HERE / "quality_matrix.json").write_text(
        json.dumps(matrix, indent=2, sort_keys=True) + "\n")
    _, level_r, first_r = PAIR[1]
    smoke_solve(level_r, first_r)
    log("alternative-generator arm complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
