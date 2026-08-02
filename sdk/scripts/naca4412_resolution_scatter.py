"""Mesh-construction scatter on the NACA 4412 finite wing, as a function of resolution.

WHY. `demo-output/website/campaign/W3_NACA4412_LAYERED_REPLICATES.md` measured
the scatter at ONE rung, the graded one: rebuilding the same recipe at four
background blockMesh division triples moved drag by 12.74% of the mean, which is
**1.69x the entire half-width of the band the credential is graded against**.
Docket item `agp-d392641d60f4` asks for a resolution where that scatter is
smaller than the band, so a verdict can be stated on more than one draw. One
rung cannot answer that; this reads the same four triples at three rungs.

WHAT IT READS. `naca4412_layered_replicates.py --refinement N A B C E`, whose
cases land at

    ~/certonomous-runs/w3-naca4412-layered-replicates/{A,B,C,E}          (N=4)
    ~/certonomous-runs/w3-naca4412-layered-replicates/r<N>/{A,B,C,E}     (N!=4)

D (35 58 20) is excluded at every rung and that is a result, not an omission:
`locationInMesh` sits at the span centre and lands exactly on a block-face plane
whenever the span division count is even, so snappyHexMesh rejects the recipe's
own seed point. That is a property of the blockMesh divisions and therefore
holds at every refinement.

Prices on CPU, never wall (COMPUTE_BUDGET_CHARTER): meshing is serial, the solve
runs on `naca4412_credential_repair.NPROCS` ranks, and both are read out of the
logs' own `ExecutionTime` lines.

Run:
    python3 naca4412_resolution_scatter.py            # every rung found on disk
    python3 naca4412_resolution_scatter.py 3 4 5      # named rungs
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SDK))
sys.path.insert(0, str(Path(__file__).resolve().parent))

OUT_ROOT = Path.home() / "certonomous-runs" / "w3-naca4412-layered-replicates"
TAGS = ("A", "B", "C", "E")
NPROCS = 4

# models/curriculum/naca4412_wing/reference.yaml as repaired 2026-08-01 (commit
# d45f3090), the version that no longer moves with the lift of the solve it
# grades. Read here rather than re-derived.
REFERENCE_CD = 0.015696
BAND_FRACTION = 0.0956


def case_dir(tag: str, refinement: int) -> Path:
    return OUT_ROOT / tag if refinement == 4 else OUT_ROOT / f"r{refinement}" / tag


def read_case(tag: str, refinement: int) -> dict | None:
    case = case_dir(tag, refinement)
    result = case / "result.json"
    if not result.exists():
        return None
    rec = json.loads(result.read_text())
    check = (case / "log.checkMesh").read_text(errors="replace")
    m = re.search(r"non-orthogonality Max:\s*([0-9.]+)\s+average:\s*([0-9.]+)", check)
    sev = re.search(r"severely non-orthogonal \(> [0-9.]+ degrees\) faces:\s*(\d+)", check)
    cells = re.search(r"cells:\s+(\d+)", check)
    faces = re.search(r"faces:\s+(\d+)", check)
    cost = rec.get("cost", {})
    mesh_s = sum(cost.get(k, 0.0) for k in (
        "snappy_finished_meshing_s", "blockMesh_execution_s",
        "surfaceFeatureExtract_execution_s", "checkMesh_execution_s"))
    solve_s = cost.get("solve_execution_s", 0.0)
    extra_s = sum(cost.get(k, 0.0) for k in
                  ("decomposePar_execution_s", "reconstructPar_execution_s"))
    return {
        "tag": tag, "refinement": refinement, "divisions": rec["divisions"],
        "cells": int(cells.group(1)) if cells else None,
        "faces": int(faces.group(1)) if faces else None,
        "cd": rec["forces"]["cd_window_mean"],
        "cl": rec["forces"]["cl_window_mean"],
        "cd_window_std": rec["forces"]["cd_window_std"],
        "max_non_ortho": float(m.group(1)) if m else None,
        "avg_non_ortho": float(m.group(2)) if m else None,
        "severe_faces": int(sev.group(1)) if sev else 0,
        "converged": rec["residuals"]["converged_flag"],
        "mesh_serial_s": mesh_s, "solve_execution_s": solve_s,
        "solve_clock_s": cost.get("solve_clock_s"),
        # Meshing is serial (one core); the solve holds NPROCS.
        "core_min": (mesh_s + extra_s + solve_s * NPROCS) / 60.0,
    }


def summarise(rows: list[dict]) -> dict:
    cds = [r["cd"] for r in rows]
    cls = [r["cl"] for r in rows]
    mean = statistics.mean(cds)
    rng = max(cds) - min(cds)
    half = BAND_FRACTION * REFERENCE_CD
    iterative = max(r["cd_window_std"] or 0.0 for r in rows)
    return {
        "n": len(rows),
        "cells_min": min(r["cells"] for r in rows),
        "cells_max": max(r["cells"] for r in rows),
        "cd_mean": mean,
        "cd_stdev": statistics.stdev(cds) if len(cds) > 1 else 0.0,
        "cd_range": rng,
        "cd_range_pct_of_mean": 100.0 * rng / mean,
        "cl_range_pct_of_mean": 100.0 * (max(cls) - min(cls)) / statistics.mean(cls),
        "band_half_width": half,
        "scatter_over_band_half_width": rng / half,
        "worst_iterative_sigma": iterative,
        "scatter_over_iterative_2sigma": rng / (2 * iterative) if iterative else None,
        "dev_pct_min": 100.0 * (min(cds) - REFERENCE_CD) / REFERENCE_CD,
        "dev_pct_max": 100.0 * (max(cds) - REFERENCE_CD) / REFERENCE_CD,
        "all_out_of_band": all(
            abs(c - REFERENCE_CD) / REFERENCE_CD > BAND_FRACTION for c in cds),
        "any_in_band": any(
            abs(c - REFERENCE_CD) / REFERENCE_CD <= BAND_FRACTION for c in cds),
        "core_min": sum(r["core_min"] for r in rows),
    }


def main(argv: list[str]) -> int:
    rungs = [int(a) for a in argv if a.isdigit()] or [3, 4, 5]
    out: dict[int, dict] = {}
    for refinement in rungs:
        rows = [r for r in (read_case(t, refinement) for t in TAGS) if r]
        if not rows:
            print(f"refinement {refinement}: no cases on disk")
            continue
        print(f"\n=== refinement {refinement} "
              f"({len(rows)} of {len(TAGS)} replicates) ===")
        print(f"{'tag':<4}{'divisions':<14}{'cells':>10}{'Cd':>14}{'dev%':>9}"
              f"{'Cl':>10}{'maxNO':>9}{'avgNO':>8}{'sev':>6}{'core-min':>10}")
        for r in rows:
            dev = 100.0 * (r["cd"] - REFERENCE_CD) / REFERENCE_CD
            print(f"{r['tag']:<4}{str(tuple(r['divisions'])):<14}{r['cells']:>10}"
                  f"{r['cd']:>14.9f}{dev:>+8.2f}%{r['cl']:>10.6f}"
                  f"{r['max_non_ortho']:>9.3f}{r['avg_non_ortho']:>8.3f}"
                  f"{r['severe_faces']:>6}{r['core_min']:>10.2f}")
        s = summarise(rows)
        out[refinement] = {"rows": rows, "summary": s}
        print(f"  Cd range {s['cd_range']:.4e} = {s['cd_range_pct_of_mean']:.2f}% "
              f"of mean; band half-width {s['band_half_width']:.4e}; "
              f"scatter/half-width = {s['scatter_over_band_half_width']:.2f}")
        print(f"  Cl range {s['cl_range_pct_of_mean']:.2f}%; "
              f"deviations {s['dev_pct_min']:+.2f}% to {s['dev_pct_max']:+.2f}%; "
              f"all out of band: {s['all_out_of_band']}")
        print(f"  cost {s['core_min']:.2f} core-min at {NPROCS} ranks, "
              f"{s['cells_min'] // NPROCS}-{s['cells_max'] // NPROCS} cells per rank")

    if len(out) > 1:
        print("\n=== scatter against resolution ===")
        print(f"{'rung':<6}{'cells':>12}{'Cd scatter':>13}{'/band half':>12}"
              f"{'Cl scatter':>13}{'core-min':>10}")
        for refinement in sorted(out):
            s = out[refinement]["summary"]
            print(f"{refinement:<6}{s['cells_min']:>6}-{s['cells_max']:<6}"
                  f"{s['cd_range_pct_of_mean']:>12.2f}%"
                  f"{s['scatter_over_band_half_width']:>12.2f}"
                  f"{s['cl_range_pct_of_mean']:>12.2f}%{s['core_min']:>10.1f}")
    dest = OUT_ROOT / "resolution_scatter.json"
    dest.write_text(json.dumps(
        {str(k): v for k, v in out.items()}, indent=2, default=str))
    print(f"\nwritten {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
