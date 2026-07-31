#!/usr/bin/env python3
"""Driver: F5b pitching NACA0012 dynamic stall, feasibility/physics/gate rungs."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "sdk"))

from workflows.tmr_verification import NACA_LEVELS
from workflows.pitching_airfoil_case import run_case


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True, choices=[l.name for l in NACA_LEVELS])
    ap.add_argument("--out", required=True)
    ap.add_argument("--end-time", type=float, required=True)
    ap.add_argument("--dt0", type=float, default=0.002)
    ap.add_argument("--max-co", type=float, default=1.0)
    ap.add_argument("--timeout", type=float, default=1800.0)
    args = ap.parse_args()

    level = next(l for l in NACA_LEVELS if l.name == args.level)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    record = run_case(level, out_dir, end_time=args.end_time, dt0=args.dt0,
                      max_co=args.max_co, timeout=args.timeout)
    (out_dir / "record.json").write_text(json.dumps(record, indent=2))
    summary = {k: v for k, v in record.items() if k not in ("times", "alpha_deg", "cl", "cd")}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
