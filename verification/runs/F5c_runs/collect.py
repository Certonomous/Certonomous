#!/usr/bin/env python3
"""Copy an F5c scratch run into the committed evidence layout.

``**/postProcessing/`` and campaign time directories are gitignored (see
`.gitignore`), so the raw samples a claim rests on have to be lifted out of
the run tree to survive as primary artifacts -- the same pattern F2_runs uses
with its `evidence/` directory.

Writes, under DEST:
  system/, 0/, constant/{transportProperties,turbulenceProperties}
  log.blockMesh, log.checkMesh, log.simpleFoam.gz
  record.json, wall_shear_profile.json, pressure_profile.json
  xr_history.json    -- per-sample reattachment AND wall-flow topology, so the
                        oscillation band can be re-derived by a reader
  evidence/wallShearStress_bottomWallDownstream_iter<N>.raw   (first and last)
  evidence/nearWall_U_iter<N>.xy                              (last)

Usage: collect.py SCRATCH_RUN_DIR DEST_DIR
"""
import gzip
import json
import shutil
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

from workflows.backstep_case import parse_wall_raw, reattachment_length  # noqa: E402


def main() -> int:
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    case = src / "case"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "evidence").mkdir(exist_ok=True)

    for sub in ("system", "0"):
        shutil.copytree(case / sub, dest / sub, dirs_exist_ok=True)
    (dest / "constant").mkdir(exist_ok=True)
    for f in ("transportProperties", "turbulenceProperties"):
        shutil.copy2(case / "constant" / f, dest / "constant" / f)
    for f in ("log.blockMesh", "log.checkMesh"):
        shutil.copy2(case / f, dest / f)
    with open(case / "log.simpleFoam", "rb") as fi, \
            gzip.open(dest / "log.simpleFoam.gz", "wb") as fo:
        shutil.copyfileobj(fi, fo)
    for f in ("record.json", "wall_shear_profile.json", "pressure_profile.json"):
        if (src / f).exists():
            shutil.copy2(src / f, dest / f)

    ws = sorted((int(p.parent.name), p) for p in
                (case / "postProcessing" / "wallSample")
                .rglob("*wallShearStress*.raw"))
    history = []
    for t, p in ws:
        r = reattachment_length(parse_wall_raw(p.read_text(errors="replace")))
        runs = (r or {}).get("sign_runs_over_h", [])
        reversed_runs = [s for s in runs
                         if s["sign"] == "reversed"
                         and s["x_end_over_h"] - s["x_start_over_h"] > 0.5]
        history.append({
            "iteration": t,
            "x_r_over_h": (r or {}).get("x_r_over_h"),
            "bubble_start_over_h": (r or {}).get("bubble_start_over_h"),
            "n_reversed_regions_over_half_H": len(reversed_runs),
            "attached_to_outlet": (r or {}).get("attached_to_outlet"),
            # "clean" = the textbook single-primary-bubble topology: exactly one
            # substantial reversed region, and attached flow all the way out.
            "clean_topology": len(reversed_runs) == 1 and bool(
                (r or {}).get("attached_to_outlet")),
        })
    (dest / "xr_history.json").write_text(json.dumps(history, indent=1))

    if ws:
        for t, p in (ws[0], ws[-1]):
            shutil.copy2(p, dest / "evidence" /
                         f"wallShearStress_bottomWallDownstream_iter{t}.raw")
    nl = sorted((int(p.parent.name), p) for p in
                (case / "postProcessing" / "nearWallLine").rglob("*U*.xy"))
    if nl:
        t, p = nl[-1]
        shutil.copy2(p, dest / "evidence" / f"nearWall_U_iter{t}.xy")

    print(f"collected {src.name} -> {dest} "
          f"({len(history)} history samples, "
          f"{sum(h['clean_topology'] for h in history)} clean)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
