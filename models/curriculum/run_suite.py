"""Run the Tier-0 curriculum end to end, unattended.

Each body is queued as a headless geometry-study mission — the real
mesh-and-solve chain, with ``emit`` capturing the verdict rather than a server
streaming it — and its result plus trust tier is written to
``models/curriculum/results/``.  The queue is resumable (a body with a result
file is skipped), it logs every step, and one body failing to mesh or solve is
recorded and stepped over rather than aborting the night.

    python run_suite.py                 # run the whole suite, skipping finished bodies
    python run_suite.py --only cube     # one body
    python run_suite.py --estimate      # print the runtime estimate and exit
    python run_suite.py --force         # re-run even bodies that already have results

This is also the lab's unattended-autonomy evidence: started once, it walks the
whole curriculum without a human in the loop and leaves an auditable trail.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

CURRICULUM_ROOT = Path(__file__).resolve().parent
REPO_ROOT = CURRICULUM_ROOT.parent.parent
SDK = REPO_ROOT / "sdk"
GEOMETRY_DIR = SDK / "geometry"
RESULTS_DIR = CURRICULUM_ROOT / "results"

if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))
if str(CURRICULUM_ROOT) not in sys.path:
    sys.path.insert(0, str(CURRICULUM_ROOT))

import registry  # noqa: E402  (curriculum package, added to path above)

# Suite-wide solve quality. Kept modest so the whole night is affordable; the
# per-body reference regime (velocity, orientation) is filled from each
# reference.yaml, not here.
DEFAULT_REFINEMENT = 2
DEFAULT_ITERATIONS = 250

# Cells the background mesh spends before snappy refines toward the body; the
# domain is external_aero's, so this mirrors its sizing exactly.
_UP, _DOWN, _LAT, _VERT = 3.0, 6.0, 3.0, 3.0


def _log(message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{stamp}] {message}"
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode("ascii"), flush=True)


def _background_cells(name: str, refinement: int) -> int:
    """Replicate external_aero's background-mesh sizing for a cell estimate."""
    from chief_engineer.external_aero import analyse_surface

    hints = registry.solve_hints(name)
    sw = hints.get("streamwise_axis")
    geometry = analyse_surface(registry.stl_path(name),
                               streamwise_axis=int(sw) if sw is not None else None)
    stream = geometry["streamwise_axis"]
    span_axis = geometry["span_axis"]
    vert = geometry["vertical_axis"]
    length = geometry["length"]
    span = geometry["span"]
    low = list(geometry["min"])
    high = list(geometry["max"])
    centre = [(low[i] + high[i]) / 2 for i in range(3)]

    box_min, box_max = list(centre), list(centre)
    box_min[stream] = low[stream] - _UP * length
    box_max[stream] = high[stream] + _DOWN * length
    box_min[span_axis] = centre[span_axis] - _LAT * span
    box_max[span_axis] = centre[span_axis] + _LAT * span
    box_min[vert] = centre[vert] - _VERT * length
    box_max[vert] = centre[vert] + _VERT * length

    base = max(box_max[i] - box_min[i] for i in range(3)) / 60.0
    cells = 1
    for i in range(3):
        cells *= max(6, round((box_max[i] - box_min[i]) / base))
    return int(cells)


# Calibrated from the cube smoke test on this machine: ~104k cells meshed in
# ~20 s and solved 150 iterations in ~49 s. Meshing scales with cell count,
# the steady solve with cells times iterations.
_MESH_CELLS_PER_MIN = 300_000.0
_SOLVE_CELLITERS_PER_MIN = 1.9e7


def estimate_minutes(names, refinement: int = DEFAULT_REFINEMENT,
                     iterations: int = DEFAULT_ITERATIONS) -> dict[str, float]:
    """Per-body wall-time estimate from the background cell count.

    Snappy grows the mesh a few times over the background count; the final
    count drives a meshing term (cells) and a solve term (cells x iterations),
    both with rates calibrated from the cube smoke test. Deliberately on the
    generous side so the night is not under-planned.
    """
    per_body = {}
    surface_multiplier = 2.5 + 1.2 * max(0, refinement - 1)   # snappy growth vs background
    for name in names:
        final_cells = _background_cells(name, refinement) * surface_multiplier
        mesh_min = final_cells / _MESH_CELLS_PER_MIN
        solve_min = final_cells * iterations / _SOLVE_CELLITERS_PER_MIN
        per_body[name] = max(1.0, mesh_min + solve_min)
    return per_body


def _stage_surface(name: str) -> None:
    """Make the curriculum STL visible to the workflow's surface resolver."""
    GEOMETRY_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(registry.stl_path(name), GEOMETRY_DIR / f"{name}.stl")


def _run_one(name: str, refinement: int, iterations: int) -> dict:
    """Run one geometry-study mission headless and capture its verdict."""
    from workflows.geometry_study import main as geometry_main

    captured: dict[str, dict] = {}

    def emit(event: str, payload) -> None:
        if event in ("result.verdict", "report.ready"):
            captured[event] = payload

    _stage_surface(name)
    reference = registry.reference_for(name)
    began = time.monotonic()
    code = geometry_main(
        request=f"Tier-0 curriculum: mesh and solve {name}, grade against its reference.",
        params={"surface": f"{name}.stl", "refinement": refinement},
        iterations=iterations, emit=emit)
    minutes = (time.monotonic() - began) / 60.0

    verdict = captured.get("result.verdict", {})
    report = captured.get("report.ready", {})
    return {
        "name": name,
        "returncode": code,
        "ok": code == 0,
        "wall_minutes": round(minutes, 2),
        "cd_measured": verdict.get("value"),
        "envelope": verdict.get("envelope"),
        "tier": verdict.get("tier"),
        "reason": verdict.get("reason"),
        "reference_cd": (reference or {}).get("cd"),
        "reference_source": (reference or {}).get("source"),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "report_results": report.get("results"),
    }


def _result_path(name: str) -> Path:
    return RESULTS_DIR / f"{name}.json"


def run_suite(names, *, refinement: int, iterations: int, force: bool) -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    estimates = estimate_minutes(names, refinement, iterations)
    total = sum(estimates.values())
    _log(f"Tier-0 suite: {len(names)} bodies, estimated {total:.0f} min "
         f"({total / 60:.1f} h) at refinement {refinement}.")
    for name in names:
        _log(f"  {name:16s} ~{estimates[name]:5.1f} min"
             + ("  [done]" if _result_path(name).exists() and not force else ""))

    failures = 0
    for name in names:
        path = _result_path(name)
        if path.exists() and not force:
            _log(f"skip {name}: result already present")
            continue
        _log(f"start {name} (refinement {refinement}, {iterations} iterations)")
        try:
            result = _run_one(name, refinement, iterations)
        except Exception as exc:  # one body failing must not abort the night
            failures += 1
            result = {
                "name": name, "ok": False, "returncode": None,
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
                "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            _log(f"FAILED {name}: {exc}")
        else:
            if not result["ok"]:
                failures += 1
            _log(f"done {name}: tier={result.get('tier')} "
                 f"Cd={result.get('cd_measured')} in {result.get('wall_minutes')} min")
        path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    completed = sum(1 for n in names if _result_path(n).exists())
    _log(f"Suite finished: {completed}/{len(names)} bodies have results, {failures} failure(s).")
    return 1 if failures else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run the Tier-0 geometry curriculum.")
    parser.add_argument("--only", help="run a single body by name")
    parser.add_argument("--refinement", type=int, default=DEFAULT_REFINEMENT)
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS)
    parser.add_argument("--force", action="store_true", help="re-run finished bodies")
    parser.add_argument("--estimate", action="store_true",
                        help="print the runtime estimate and exit")
    args = parser.parse_args(argv)

    names = [args.only] if args.only else list(registry.TIER0)
    unknown = [n for n in names if not registry.stl_path(n).exists()]
    if unknown:
        _log(f"missing STL for: {', '.join(unknown)} — run generate.py first")
        return 2

    if args.estimate:
        estimates = estimate_minutes(names, args.refinement, args.iterations)
        total = sum(estimates.values())
        for name in names:
            _log(f"{name:16s} ~{estimates[name]:5.1f} min")
        _log(f"total ~{total:.0f} min ({total / 60:.1f} h) at refinement {args.refinement}")
        return 0

    return run_suite(names, refinement=args.refinement,
                     iterations=args.iterations, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
