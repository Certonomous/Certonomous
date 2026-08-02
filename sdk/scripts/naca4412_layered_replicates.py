"""Replicate meshes at the NACA 4412 rung the credential is graded from.

WHY. `demo-output/website/campaign/W3_MESH_NOISE_FLOOR_RESULTS.md` and
`W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md` measured mesh-construction scatter by
rebuilding a body's production recipe with only the background blockMesh
division triple changed. Every replicate measured so far -- Ahmed 25 deg, cube,
NACA 0015 sail, NACA 0012 finite wing -- was built with `addLayers false`.

The NACA 4412 credential
(`models/curriculum/results/naca4412_wing.json`) is the lab's only wall
credential graded from a LAYERED mesh: 645,251 cells, refinement 4,
`add_layers=True`, 12 prism layers, 94% of target layer thickness. Its verdict
is NOT VALIDATED at Cd 0.018262 against a derived reference 0.01357, +34.6%.
Nobody has ever measured whether that +34.6% survives a change of background
mesh, and a layered mesh is a different experiment from an unlayered one --
snappyHexMesh's layer-addition stage is where its most path-dependent
decisions are made, so the unlayered scatter is not transferable.

WHAT THIS RUNS. Four cases, identical in every respect except the blockMeshDict
division triple:

    A (control)  (33 60 20)  -- must reproduce 645,251 cells and Cd 0.018262
    B            (34 59 21)
    C            (32 61 21)
    D            (35 58 20)

The three perturbations are the SAME triples used on the NACA 0012 in
`W3_NACA0012_VERDICT_NOT_REPRODUCIBLE.md`, so the two bodies are directly
comparable and the perturbation set was not chosen after seeing this body's
answer.

Everything else -- geometry, refinement, layer sizing, flow condition, solver
settings, rank count, decomposition method -- comes from
`naca4412_credential_repair.py`, which is imported rather than copied so the
two cannot drift.

Run:
    python3 naca4412_layered_replicates.py A B      # or any subset of A B C D
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SDK))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import naca4412_credential_repair as rep  # noqa: E402

RUN_ROOT = Path.home() / "certonomous-runs"
OUT_ROOT = RUN_ROOT / "w3-naca4412-layered-replicates"

# The graded rung: refinement 4 ("fine"), add_layers True, y+ target 30.
# 2026-08-02: made a parameter so the SAME four triples can be rebuilt at a
# second resolution. The item this serves (agp-d392641d60f4) asks for a
# resolution at which mesh-construction scatter is smaller than the acceptance
# band; that needs the scatter measured at more than one rung. Refinement 3
# ("medium") and 5 ("finer") are the credential ladder's own neighbouring rungs
# (naca4412_credential_repair.RUNGS), so nothing about the recipe is invented
# here. Cases land under OUT_ROOT/r<N>/<tag> for N != 4; the original
# refinement-4 cases keep their existing paths so published evidence still
# resolves.
REFINEMENT = 4
Y_PLUS_TARGET = 30.0

VARIANTS = {
    "A": (33, 60, 20),   # control -- the stored production triple
    "B": (34, 59, 21),
    "C": (32, 61, 21),
    # (35 58 20) -- the third 0012 perturbation -- FAILS TO MESH on this body:
    # snappyHexMesh rejects the recipe's own locationInMesh with "Point
    # (6.50165 0 0.0349165) is not inside the mesh or on a face or edge" in the
    # refinement phase. Kept here, not deleted, because the failure is a result.
    "D": (35, 58, 20),
    # Substitute fourth replicate, chosen after D failed and before any of
    # A/B/C's drag was compared to the reference.
    "E": (34, 60, 21),
}

STORED = {"cells": 645251, "cd": 0.018262420944444444, "cl": 0.20954745755555554}


def _log(tag: str, msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] [{tag}] {msg}", flush=True)


def set_divisions(case: Path, triple: tuple[int, int, int]) -> None:
    """Rewrite ONLY the hex division triple in the blockMeshDict."""
    path = case / "system" / "blockMeshDict"
    text = path.read_text()
    new, n = re.subn(r"(hex \(0 1 2 3 4 5 6 7\) \()\d+ \d+ \d+(\))",
                     rf"\g<1>{triple[0]} {triple[1]} {triple[2]}\g<2>", text)
    if n != 1:
        raise RuntimeError(f"expected exactly one hex division line, matched {n}")
    path.write_text(new)


def dest_for(tag: str, refinement: int) -> Path:
    """Refinement 4 keeps the published flat layout; other rungs are namespaced."""
    return OUT_ROOT / tag if refinement == 4 else OUT_ROOT / f"r{refinement}" / tag


def build_variant(tag: str, triple: tuple[int, int, int],
                  refinement: int = REFINEMENT) -> Path:
    """Build the graded rung's case, then perturb the background divisions."""
    # Chord is read from the STL exactly as the graded run read it -- not
    # assumed to be 1.0 -- so the first-layer height is bit-identical to the
    # graded rung's.
    geometry = rep.analyse_surface(rep.GEOMETRY, streamwise_axis=0)
    layer_sizing = rep.target_first_layer_thickness(
        geometry["length"], rep.VELOCITY, rep.VISCOSITY, rep.RHO,
        y_plus_target=Y_PLUS_TARGET)
    # rep.build() writes to certonomous-runs/credential-repair-naca4412-<tag>;
    # give it a private tag then move it under our own root so the original
    # graded case directories are never touched. The refinement is part of the
    # scratch tag so two rungs can be built concurrently without colliding.
    scratch_tag = f"layerrep-r{refinement}-{tag}"
    case = rep.build(scratch_tag, refinement, layer_sizing)
    dest = dest_for(tag, refinement)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(case), str(dest))
    set_divisions(dest, triple)
    (dest / "replicate.json").write_text(json.dumps(
        {"tag": tag, "divisions": list(triple), "refinement": refinement,
         "add_layers": True, "y_plus_target": Y_PLUS_TARGET,
         "layer_sizing": layer_sizing, "nprocs": rep.NPROCS}, indent=2))
    return dest


def cpu_time_from_log(case: Path) -> dict:
    """OpenFOAM prints ExecutionTime (CPU, per rank) beside ClockTime (wall).

    Price on CPU, not wall (COMPUTE_BUDGET_CHARTER): the box is shared.
    """
    out = {}
    text = (case / "log.simpleFoam").read_text(errors="replace")
    hits = re.findall(r"ExecutionTime = ([0-9.]+) s\s+ClockTime = ([0-9.]+) s", text)
    if hits:
        out["solve_execution_s"] = float(hits[-1][0])
        out["solve_clock_s"] = float(hits[-1][1])
        out["solve_core_min"] = float(hits[-1][0]) * rep.NPROCS / 60.0
    for stage in ("snappyHexMesh", "blockMesh", "checkMesh", "surfaceFeatureExtract",
                  "decomposePar", "reconstructPar"):
        p = case / f"log.{stage}"
        if not p.exists():
            continue
        h = re.findall(r"ExecutionTime = ([0-9.]+) s", p.read_text(errors="replace"))
        if h:
            out[f"{stage}_execution_s"] = float(h[-1])
    m = re.search(r"Finished meshing in = ([0-9.]+) s",
                  (case / "log.snappyHexMesh").read_text(errors="replace"))
    if m:
        out["snappy_finished_meshing_s"] = float(m.group(1))
    return out


def run_variant(tag: str, refinement: int = REFINEMENT) -> dict:
    triple = VARIANTS[tag]
    t0 = time.time()
    _log(tag, f"building at divisions {triple}, refinement {refinement}")
    case = build_variant(tag, triple, refinement)
    _log(tag, "meshing")
    rep.mesh(case)
    check = rep.parse_checkmesh((case / "log.checkMesh").read_text(errors="replace"))
    layers = rep.parse_layer_coverage((case / "log.snappyHexMesh").read_text(errors="replace"))
    _log(tag, f"meshed: {check.get('cells')} cells, nonOrtho {check.get('max_non_orthogonality')}")
    _log(tag, "solving")
    rep.solve(case)
    res = rep.parse_residuals((case / "log.simpleFoam").read_text(errors="replace"))
    forces = rep.parse_forcecoeffs(case)
    ypl = rep.parse_yplus(rep.yplus(case))
    record = {
        "tag": tag, "divisions": list(triple), "refinement": refinement,
        "case": str(case),
        "wall_s": time.time() - t0,
        "checkMesh": check, "layers": layers, "residuals": res,
        "forces": forces, "yplus": ypl, "cost": cpu_time_from_log(case),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (case / "result.json").write_text(json.dumps(record, indent=2))
    _log(tag, f"DONE cells={check.get('cells')} "
              f"Cd={forces.get('cd_window_mean')} Cl={forces.get('cl_window_mean')} "
              f"converged={res.get('converged_flag')}")
    return record


def main(argv: list[str]) -> int:
    refinement = REFINEMENT
    for i, a in enumerate(argv):
        if a == "--refinement":
            refinement = int(argv[i + 1])
    tags = [a for a in argv if a in VARIANTS] or list(VARIANTS)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for tag in tags:
        try:
            run_variant(tag, refinement)
        except Exception as exc:  # keep the batch going; a failure is a result
            _log(tag, f"FAILED: {exc}")
            fail = dest_for(tag, refinement).parent / f"{tag}.failed"
            fail.parent.mkdir(parents=True, exist_ok=True)
            fail.write_text(repr(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
