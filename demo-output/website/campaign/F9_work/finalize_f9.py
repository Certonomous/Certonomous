#!/usr/bin/env python3
"""Assemble demo-output/website/campaign/F9_pulsatile_valve.json from
f9_analysis.json plus the measured per-run wall-clock costs. Run after
analyze_f9.py."""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REG = HERE.parents[1] / "solve_registry"


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
