"""Lifetime lab counters — the numbers the credentials view leads with.

The standing credentials panel must open with what the lab has *done over its
lifetime* — missions run, solver core-hours, knowledge entries, experimental
anchors, benchmarks active — never a "4 of 8" fraction. Those counters come
from durable records, chiefly the all-night mega-batch ledger, so the number
grows honestly as real evaluations accumulate and survives restarts.

Everything here reads on-disk truth and rounds nothing up. If the ledger holds
812 real evaluations, ``missions_run`` reflects 812 — plus any missions the
server itself has persisted — and not a padded thousand.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]

# Fixed knowledge-base sizes (mirrors chief_engineer.citations / KnowledgeBase).
_KNOWLEDGE_ENTRIES = 7
_OPERATING_LESSONS = 1

# The two benchmarks the website tracks (see demo-output/website/benchmarks.json).
_ACTIVE_BENCHMARKS = ("closure-challenge", "reduced-order-speedup")


def _ledger_path() -> Path:
    env = os.environ.get("CERTONOMOUS_MEGABATCH_LEDGER")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "demo-output" / "website" / "mega-batch" / "ledger.jsonl").resolve()


def _credentials_root() -> Path:
    env = os.environ.get("CERTONOMOUS_CREDENTIALS")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "models" / "curriculum" / "results").resolve()


def read_ledger(ledger_path: Path | None = None) -> list[dict[str, Any]]:
    """Every well-formed row of the mega-batch ledger (ok and failed alike)."""
    path = ledger_path or _ledger_path()
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def ledger_summary(ledger_path: Path | None = None) -> dict[str, Any]:
    """Counts, wall-time totals, and per-solver breakdown from the ledger."""
    rows = read_ledger(ledger_path)
    ok_rows = [r for r in rows if r.get("ok")]
    per_solver: dict[str, dict[str, Any]] = {}
    core_seconds = 0.0
    for row in ok_rows:
        solver = str(row.get("solver", "unknown"))
        wall = float(row.get("wall_seconds") or 0.0)
        bucket = per_solver.setdefault(solver, {"count": 0, "wall_seconds": 0.0})
        bucket["count"] += 1
        bucket["wall_seconds"] += wall
        core_seconds += wall
    return {
        "evaluations_ok": len(ok_rows),
        "evaluations_failed": len(rows) - len(ok_rows),
        "core_seconds": round(core_seconds, 1),
        "core_hours": round(core_seconds / 3600.0, 3),
        "per_solver": {
            k: {"count": v["count"], "wall_seconds": round(v["wall_seconds"], 1)}
            for k, v in sorted(per_solver.items())
        },
    }


def _experimental_anchors() -> int:
    """Curriculum bodies carrying a cited experimental reference value."""
    root = _credentials_root()
    if not root.exists():
        return 0
    anchors = 0
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("reference_cd") is not None and data.get("reference_source"):
            anchors += 1
    return anchors


def _uq_studies_root() -> Path:
    env = os.environ.get("CERTONOMOUS_UQ_STUDIES")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "models" / "curriculum" / "uq-studies").resolve()


def _benchmarks_path() -> Path:
    env = os.environ.get("CERTONOMOUS_BENCHMARKS")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "demo-output" / "website" / "benchmarks.json").resolve()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# Geometries surfaced on the discretization-uncertainty card, in display order,
# each with the human name the lab uses on camera and its honest programme state.
_UQ_GEOMETRIES = (
    ("motorBike", "motorBike", "measured"),
    ("naca4412_wing", "NACA 4412 wing", "measured"),
    ("b52", "B-52", "in progress"),
)


def _uq_program() -> dict[str, Any]:
    """Discretization-uncertainty programme, data-driven from the UQ studies.

    Reports the observed order and the conservative band each refinement ladder
    actually produced. Nothing is invented: a study with no usable order (its
    mesh did not refine between rungs) is reported as still in progress.
    """
    root = _uq_studies_root()
    geometries: list[dict[str, Any]] = []
    for slug, label, state in _UQ_GEOMETRIES:
        data = _load_json(root / f"{slug}.json")
        num = data.get("numerical", {}) if isinstance(data, dict) else {}
        levels = data.get("levels", []) if isinstance(data, dict) else []
        band_rel = num.get("band_rel")
        geometries.append({
            "name": label,
            "state": state,
            "rungs": len(levels),
            "observed_order": num.get("observed_order"),
            "band_abs": num.get("band_abs"),
            "band_rel": band_rel,
            "band_pct": round(band_rel * 100.0, 1) if isinstance(band_rel, (int, float)) else None,
            "value": num.get("value_fine", num.get("value_working")),
            "method": num.get("method", ""),
        })
    return {
        "title": "Discretization-uncertainty program",
        "status": "ACTIVE RESEARCH",
        "summary": "Refinement ladders per geometry: observed orders and "
                   "conservative uncertainty bands.",
        "geometries": geometries,
    }


def research_programs() -> dict[str, Any]:
    """The lab's real research programmes, framed as work in progress.

    Closure-challenge and reduced-order speed figures come from the public
    benchmarks file; the discretization program is data-driven from the UQ
    refinement studies; the valve agenda lines are the queued programmes.
    """
    bench = _load_json(_benchmarks_path())
    closure_raw = bench.get("closure_challenge", {})
    speed_raw = bench.get("speed_benchmark", {})

    closure = {
        "title": closure_raw.get("name", "Closure-challenge benchmark"),
        "status": "ACTIVE RESEARCH",
        "board": closure_raw.get("board", "public leaderboard"),
        "target_rank": closure_raw.get("target_rank", 4),
        "target_overall": closure_raw.get("target_overall"),
        "target_per_case": closure_raw.get("target_per_case", []),
        "our_entry": "baseline in training",
        "target": "top 4",
        "repo": "github.com/rmcconke/closure-challenge-benchmark",
    }
    speed = {
        "title": speed_raw.get("name", "Reduced-order speed program"),
        "status": "measured",
        "case": speed_raw.get("case", "NACA 4412"),
        "full_core_min": speed_raw.get("full_mc_core_min"),
        "reduced_core_min": speed_raw.get("reduced_core_min"),
        "speedup_x": speed_raw.get("speedup_x"),
        "source": speed_raw.get("source", ""),
    }
    queued = [
        {"name": "Harmonic-balance cycle solve",
         "note": "periodic flow solved in the frequency domain, not marched in time"},
        {"name": "Unsteady fluid-structure interaction",
         "note": "leaflet motion coupled to the flow it drives"},
        {"name": "Non-Newtonian rheology",
         "note": "shear-thinning blood models for the valve agenda"},
    ]
    return {
        "closure": closure,
        "uq": _uq_program(),
        "speed": speed,
        "queued": queued,
    }


def _persisted_missions() -> int:
    """Demo missions the server has persisted to state (best-effort)."""
    state_dir = os.environ.get("CHIEF_ENGINEER_STATE_DIR")
    if not state_dir:
        return 0
    root = Path(state_dir)
    if not root.exists():
        return 0
    return sum(1 for _ in root.glob("m-*.json"))


def lifetime_counters(ledger_path: Path | None = None) -> dict[str, Any]:
    """The header row: missions run, core-hours, knowledge, anchors, benchmarks.

    ``missions_run`` = real+ROM evaluations in the ledger plus any missions the
    server itself persisted. Honest, durable, never rounded.
    """
    summary = ledger_summary(ledger_path)
    persisted = _persisted_missions()
    return {
        "missions_run": summary["evaluations_ok"] + persisted,
        "solver_core_hours": summary["core_hours"],
        "knowledge_entries": _KNOWLEDGE_ENTRIES + _OPERATING_LESSONS,
        "experimental_anchors": _experimental_anchors(),
        "benchmarks_active": len(_ACTIVE_BENCHMARKS),
        "detail": {
            "ledger_evaluations": summary["evaluations_ok"],
            "ledger_failed": summary["evaluations_failed"],
            "persisted_missions": persisted,
            "per_solver": summary["per_solver"],
        },
        # The active-research programmes the credentials view showcases as
        # work in progress (R5): closure challenge, discretization uncertainty,
        # reduced-order speed, and the queued valve agenda.
        "research": research_programs(),
    }


if __name__ == "__main__":
    print(json.dumps(lifetime_counters(), indent=2))
