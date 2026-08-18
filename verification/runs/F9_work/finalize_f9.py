#!/usr/bin/env python3
"""Assemble demo-output/website/campaign/F9_pulsatile_valve.json from
f9_analysis.json plus the measured per-run wall-clock costs. Run after
analyze_f9.py."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
# NOT `HERE.parents[1]`.  Two defects, and the second is why this one
# resolves a NAME rather than a path.  (1) MOVE_MAP batch 7 made this file
# one segment shallower, so `parents[1]` went from the webroot to
# `verification/`.  (2) `solve_registry` holds no tracked file, so no
# `git mv` reaches it: batch 7H HAND-CARRIES it to `evidence/solve_registry`
# (1,508,128,888 bytes), and a repo-root-relative literal would dangle the
# moment it lands.  `lab_paths.SOLVE_REGISTRY` is bound to the PAIR and is
# correct on both sides of that carry.
_REPO_ROOT = next((_p for _p in Path(__file__).resolve().parents
                  if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
import sys as _sys                                            # noqa: E402
_sys.path.insert(0, str(_REPO_ROOT / "scripts"))
import lab_paths as _lab_paths                                # noqa: E402
REG = _lab_paths.SOLVE_REGISTRY


def exec_time(job_prefix: str) -> float | None:
    logs = sorted(REG.glob(f"{job_prefix}_*.log"))
    if not logs:
        return None
    text = logs[-1].read_text(errors="replace")
    matches = re.findall(r"ExecutionTime = ([\d.]+) s", text)
    return float(matches[-1]) if matches else None


def main():
    analysis = json.loads((HERE / "f9_analysis.json").read_text())

    costs = {name: exec_time(f"F9_{name}") for name in
             ("steady_q25", "steady_q50", "steady_q75", "steady_q100",
              "pulsatile_physio", "pulsatile_lowalpha",
              "womersley_probe_check", "steady_beta50", "steady_beta55",
              "mesh_coarse_q100", "mesh_med_q100", "mesh_fine_q100",
              "lowalpha_ext", "physio_dt_half", "pulsatile_fine")}

    # Round 3 (2026-07-30). Two fields the earlier analysis emitted are
    # retracted rather than deleted, so a reader who has the old JSON can
    # see WHY the number they are holding is gone.
    criteria_path = HERE / "f9_criteria.json"
    criteria = (json.loads(criteria_path.read_text())
                if criteria_path.exists() else None)
    retractions = {
        "analysis.steady_reference_map.*.Cd_cfd": (
            "WITHDRAWN 2026-07-30. Computed as Q/(A*sqrt(2*dp/rho)), which "
            "omits the velocity-of-approach factor 1/sqrt(1-beta^4) that "
            "ISO 5167's discharge coefficient carries, from a dp measured "
            "between two centreline probes whose total heads agree to "
            "0.01-0.34% of that dp. It is a reversible acceleration, not a "
            "loss, and no discharge coefficient can be fitted to it. See "
            "round3.total_head_check and round3.discharge_coefficient_audit."),
        "analysis.steady_reference_map.*.dp_upstream_to_downstream_Pa": (
            "NOT CONVERGED for steady_q100 (and for the 50/55 deg points in "
            "beta_boundary_results.json). Criterion F9-STAT-1 fails on this "
            "signal: tail-window band 39-128% of its own mean, a "
            "self-sustained jet oscillation rather than a settling "
            "transient. See round3.stationarity."),
    }

    doc = {
        "family": "F9",
        "title": "Pulsatile valve-orifice CFD replacing the reduced-order screen",
        "geometry": {
            "opening_angle_deg": 65.0,
            "note": "fixed-leaflet limit of the ROM's own geometry family; "
                    "axisymmetric sharp-edged orifice of matching effective area",
        },
        "analysis": analysis,
        "retracted_fields": retractions,
        "round3": criteria,
        "measured_wall_seconds": costs,
        "measured_wall_seconds_total": sum(v for v in costs.values() if v),
    }
    out_path = HERE.parent / "F9_pulsatile_valve.json"
    out_path.write_text(json.dumps(doc, indent=2, default=str))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
