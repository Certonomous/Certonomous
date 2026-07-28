"""Re-mesh the NACA4412 wing 'finer' rung (refinement 5, ~1.85M cells) with
relaxed snappyHexMesh layer-addition controls only, to test whether the
finer rung's collapsed boundary-layer coverage was a meshing defect rather
than physics.

Context (mission-output/uq-studies/naca4412_repair_finer.json): the finer
rung achieved only 58.3% layer coverage / 6 of 12 wanted layers, versus
~94% / 12 layers on both coarser rungs. log.snappyHexMesh for that run shows
a classic layer-collapse signature: the extrusion fraction starts at 87.7%
in "Layer addition iteration 0" and monotonically decays to ~66% as
non-orthogonality / illegal-face checks strip extrusion at the medial axis
near the wing's thin trailing edge, well before the outer loop even reaches
the point (nRelaxedIter=20) where meshQuality is allowed to relax.

This script reuses naca4412_credential_repair.py's case builder byte-for-byte
(same geometry, same refinement=5, same firstLayerThickness sized for the
y+=30 target, same flow setup, same solver settings) and, after the dict is
written, patches ONLY the addLayersControls block:

    nGrow                    0    -> 1
    featureAngle             60   -> 70
    nRelaxIter               5    -> 20   (mesh-quality relaxation attempts
                                            per layer-addition outer iteration,
                                            see medialAxisMeshMover::shrinkMesh)
    nSmoothSurfaceNormals    1    -> 5
    nSmoothNormals           3    -> 5
    maxFaceThicknessRatio    0.5  -> 0.6
    maxThicknessToMedialRatio 0.3 -> 0.5   (less aggressive thickness
                                            reduction near the medial axis,
                                            i.e. near the thin trailing edge)
    nLayerIter               60   -> 100
    nRelaxedIter              20   -> 35   (same ~1/3 strict : 2/3 relaxed
                                            split as the original, scaled up)
    minThickness           5% of firstLayerThickness -> 1%
                                            (let a partially-collapsed layer
                                            survive instead of being dropped)

firstLayerThickness itself (the y+=30 sizing target), the geometry, the
castellatedMesh refinement levels, the flow boundary conditions, and every
solver/fvSchemes/fvSolution setting are untouched -- verified by exact
literal-substring patch (fails loudly if the expected text isn't found).

Run:
    python3 naca4412_relayer_finer.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SDK))
sys.path.insert(0, str(SCRIPTS))

from chief_engineer.external_aero import analyse_surface  # noqa: E402
import naca4412_credential_repair as base  # noqa: E402

TAG = "finer_relayered"
REFINEMENT = 5  # identical to the "finer" rung

# (literal text as written by chief_engineer.external_aero._snappy, old -> new)
RELAXED_LAYER_OVERRIDES = {
    "nGrow": ("nGrow 0;", "nGrow 1;"),
    "featureAngle": ("featureAngle 60;", "featureAngle 70;"),
    "nRelaxIter": ("nRelaxIter 5;", "nRelaxIter 20;"),
    "nSmoothSurfaceNormals": ("nSmoothSurfaceNormals 1;", "nSmoothSurfaceNormals 5;"),
    "nSmoothNormals": ("nSmoothNormals 3;", "nSmoothNormals 5;"),
    "maxFaceThicknessRatio": ("maxFaceThicknessRatio 0.5;", "maxFaceThicknessRatio 0.6;"),
    "maxThicknessToMedialRatio": ("maxThicknessToMedialRatio 0.3;", "maxThicknessToMedialRatio 0.5;"),
    "nLayerIter": ("nLayerIter 60;", "nLayerIter 100;"),
    "nRelaxedIter": ("nRelaxedIter 20;", "nRelaxedIter 35;"),
}


def patch_layer_controls(case: Path) -> dict:
    path = case / "system" / "snappyHexMeshDict"
    text = path.read_text()
    applied: dict[str, str] = {}
    for name, (old, new) in RELAXED_LAYER_OVERRIDES.items():
        n = text.count(old)
        if n != 1:
            raise RuntimeError(
                f"expected exactly one occurrence of {old!r} in {path}, found {n}")
        text = text.replace(old, new, 1)
        applied[name] = new

    # minThickness: relative to firstLayerThickness, which is left untouched
    # (it is the y+=30 sizing target and is a hard constraint on this task).
    m = re.search(r"firstLayerThickness ([0-9.eE+-]+);", text)
    if not m:
        raise RuntimeError(f"could not find firstLayerThickness in {path}")
    first_layer = float(m.group(1))
    m2 = re.search(r"    minThickness [0-9.eE+-]+;\n", text)
    if not m2:
        raise RuntimeError(f"could not find minThickness in {path}")
    new_min = first_layer * 0.01
    old_min_line = m2.group(0)
    new_min_line = f"    minThickness {new_min:.6g};\n"
    text = text.replace(old_min_line, new_min_line, 1)
    applied["minThickness"] = f"{new_min:.6g} (1% of firstLayerThickness={first_layer:.6g}, was 5%)"

    path.write_text(text)
    return applied


def build(tag: str, refinement: int, layer_sizing: dict) -> Path:
    case = base.build(tag, refinement, layer_sizing)
    applied = patch_layer_controls(case)
    (case / "layer_override_applied.json").write_text(json.dumps(applied, indent=2))
    base._log(f"applied relaxed layer overrides: {applied}")
    return case


def main() -> int:
    geometry = analyse_surface(base.GEOMETRY, streamwise_axis=0)
    chord = geometry["length"]
    layer_sizing = base.target_first_layer_thickness(
        chord, base.VELOCITY, base.VISCOSITY, base.RHO, y_plus_target=30.0)
    base._log(f"rung={TAG} refinement={REFINEMENT} chord={chord:.4f} m "
              f"first_layer_thickness={layer_sizing['first_layer_thickness_m']:.4g} m "
              f"(target y+={layer_sizing['y_plus_target']:g}) -- relayered attempt "
              f"(relaxed addLayersControls only)")

    case = build(TAG, REFINEMENT, layer_sizing)
    base._log(f"case staged at {case}")

    t0 = time.monotonic()
    base.mesh(case)
    t_mesh = time.monotonic() - t0
    check = base.parse_checkmesh((case / "log.checkMesh").read_text(errors="replace"))
    layers = base.parse_layer_coverage((case / "log.snappyHexMesh").read_text(errors="replace"))
    base._log(f"mesh done in {t_mesh:.0f}s: {check}")
    base._log(f"layer coverage: {layers}")

    t1 = time.monotonic()
    base.solve(case)
    t_solve = time.monotonic() - t1
    log_solve = (case / "log.simpleFoam").read_text(errors="replace")
    residuals = base.parse_residuals(log_solve)
    forces = base.parse_forcecoeffs(case)
    base._log(f"solve done in {t_solve:.0f}s: residuals={residuals} forces={forces}")

    yp_text = base.yplus(case)
    yp = base.parse_yplus(yp_text)
    base._log(f"y+ (post-solve, actual): {yp}")

    result = {
        "tag": TAG, "refinement": REFINEMENT, "case": str(case),
        "note": ("Re-mesh of the 'finer' rung (refinement 5) with relaxed "
                 "snappyHexMesh layer-addition controls only (addLayersControls: "
                 "nGrow 0->1, featureAngle 60->70, nRelaxIter 5->20, "
                 "nSmoothSurfaceNormals 1->5, nSmoothNormals 3->5, "
                 "maxFaceThicknessRatio 0.5->0.6, maxThicknessToMedialRatio "
                 "0.3->0.5, nLayerIter 60->100, nRelaxedIter 20->35, "
                 "minThickness 5%->1% of firstLayerThickness). Geometry, "
                 "castellatedMesh refinement levels, firstLayerThickness "
                 "(y+=30 target), flow setup, and solver settings are "
                 "byte-identical to naca4412_repair_finer.json."),
        "layer_overrides": {k: v[1] if isinstance(v, tuple) else v
                             for k, v in RELAXED_LAYER_OVERRIDES.items()},
        "wall_seconds_mesh": round(t_mesh, 1), "wall_seconds_solve": round(t_solve, 1),
        "layer_sizing": layer_sizing, "checkmesh": check, "layer_coverage": layers,
        "residuals": residuals, "forces": forces, "y_plus": yp,
        "geometry": {k: v for k, v in geometry.items() if k not in ("min", "max")},
        "velocity": base.VELOCITY, "viscosity": base.VISCOSITY, "nprocs": base.NPROCS,
        "iterations_budget": base.ITERATIONS,
    }
    out_path = SDK.parent / "mission-output" / "uq-studies" / f"naca4412_repair_{TAG}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=str))
    base._log(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
