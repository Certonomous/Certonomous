#!/usr/bin/env python3
"""Driver: F5c backward-facing step, feasibility/physics/gate rungs."""
import argparse
import json
import sys
from pathlib import Path

# NOT `parents[4]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[4]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
_REPO_ROOT = next((_p for _p in Path(__file__).resolve().parents
                  if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
sys.path.insert(0, str(_REPO_ROOT / "sdk"))

from workflows.backstep_case import STEP_LEVELS, run_case


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True, choices=[l.name for l in STEP_LEVELS])
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=float, default=1800.0)
    ap.add_argument("--iterations", type=int, default=None)
    ap.add_argument("--sample-every", type=int, default=0,
                    help="write the wall-shear/near-wall samples every N "
                         "iterations so x_r/H vs iteration is recorded")
    ap.add_argument("--inlet-bl-turbulence", action="store_true",
                    help="SENSITIVITY ONLY: specify inlet k/omega from the "
                         "documented Re_theta=5000 friction velocity instead "
                         "of a uniform freestream level")
    ap.add_argument("--simple", action="store_true",
                    help="plain SIMPLE instead of SIMPLEC (consistent no)")
    ap.add_argument("--relax-p", type=float, default=0.3)
    ap.add_argument("--relax-u", type=float, default=0.6)
    args = ap.parse_args()

    level = next(l for l in STEP_LEVELS if l.name == args.level)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    record = run_case(level, out_dir, iterations=args.iterations, timeout=args.timeout,
                      sample_every=args.sample_every,
                      inlet_bl_turbulence=args.inlet_bl_turbulence,
                      consistent=not args.simple,
                      relax_p=args.relax_p, relax_u=args.relax_u)
    # Trim raw profiles from the console-facing json a bit; keep in a sidecar.
    profile = record.pop("wall_shear_profile")
    pprofile = record.pop("pressure_profile")
    (out_dir / "record.json").write_text(json.dumps(record, indent=2))
    (out_dir / "wall_shear_profile.json").write_text(json.dumps(profile, indent=2))
    (out_dir / "pressure_profile.json").write_text(json.dumps(pprofile, indent=2))
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
