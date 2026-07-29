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
              "pulsatile_physio", "pulsatile_lowalpha")}

    doc = {
        "family": "F9",
        "title": "Pulsatile valve-orifice CFD replacing the reduced-order screen",
        "geometry": {
            "opening_angle_deg": 65.0,
            "note": "fixed-leaflet limit of the ROM's own geometry family; "
                    "axisymmetric sharp-edged orifice of matching effective area",
        },
        "analysis": analysis,
        "measured_wall_seconds": costs,
        "measured_wall_seconds_total": sum(v for v in costs.values() if v),
    }
    out_path = HERE.parent / "F9_pulsatile_valve.json"
    out_path.write_text(json.dumps(doc, indent=2, default=str))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
