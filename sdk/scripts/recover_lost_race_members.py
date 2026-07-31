"""Re-solve the race lane's 88 designs that never reached the solver.

``mission-output/race-study/work/mc`` holds 176 design directories; 88 carry a
``result.json`` and 88 do not. Every one of the 88 without a result has a
``log.vspaero`` whose entire contents are the Windows python-launcher stub
("Python was not found; run without arguments to install from the Microsoft
Store, or disable this shortcut from Settings ..."). The solver never ran, so
the cause is a launcher misconfiguration, identical for all 88 and independent
of the design -- it is not a convergence gate and not a physics filter.

Their designs are a SECOND, independent 8-sample Reynolds draw over the same
11-point alpha grid. Sample 0 is ``RE_NOMINAL`` exactly in both draws, so 11
of the 176 designs coincide and the union spans 15 distinct Reynolds samples
across 165 distinct designs. The race act reported on the surviving 8 samples
and never said the other 8 were gone.

This script re-solves all 88 from their own recorded ``job.json``, with the
same worker and the same solver build, into a FRESH tree
(``mission-output/mfmc-recovery/work``) so the race act's recorded wall clocks
-- which are themselves a published measurement -- are never touched.

Control, run before trusting any of it: a SURVIVING design (``mc-s0a0``)
re-solved on this host returned L/D 18.140687390989, bit-identical to its
2026-07-25 record, so the recovered lane and the recorded lane are the same
measurement.

Consumed by ``scripts/run_mfmc_error_budget.py``.

Run::

    python scripts/recover_lost_race_members.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
ROOT = SDK.parent
SRC = ROOT / "mission-output" / "race-study" / "work" / "mc"
DST = ROOT / "mission-output" / "mfmc-recovery" / "work"
WORKER = SDK / "chief_engineer" / "vspaero_worker.py"
PYTHONPATH = os.environ.get(
    "OPENVSP_PYTHONPATH",
    "/opt/OpenVSP/python/openvsp:/opt/OpenVSP/python/degen_geom:"
    "/opt/OpenVSP/python/utilities")
MAX_WORKERS = 8

# The one string that identifies the failure as a launcher problem rather
# than anything the solver did. Checked, not assumed: a directory that failed
# for some OTHER reason is reported and skipped, because re-solving it would
# quietly fold a real failure back into the ensemble.
LAUNCHER_STUB = "Python was not found"


def lost_designs() -> tuple[list[str], list[str]]:
    lost, other = [], []
    for case in sorted(SRC.iterdir()):
        if not case.is_dir() or (case / "result.json").exists():
            continue
        log = case / "log.vspaero"
        text = log.read_text(errors="replace") if log.exists() else ""
        (lost if LAUNCHER_STUB in text else other).append(case.name)
    return lost, other


def solve(tag: str) -> tuple[str, float, str]:
    case = DST / tag
    case.mkdir(parents=True, exist_ok=True)
    if (case / "result.json").exists():
        return tag, 0.0, "cached"
    shutil.copy(SRC / tag / "job.json", case)
    env = dict(os.environ, PYTHONPATH=PYTHONPATH)
    began = time.time()
    with open(case / "log.vspaero", "wb") as log:
        proc = subprocess.run([sys.executable, str(WORKER)], cwd=case, env=env,
                              stdout=log, stderr=subprocess.STDOUT, timeout=300)
    elapsed = time.time() - began
    if proc.returncode != 0 or not (case / "result.json").exists():
        return tag, elapsed, f"FAILED rc={proc.returncode}"
    result = json.loads((case / "result.json").read_text(encoding="utf-8"))
    result["elapsed_s"] = round(elapsed, 3)
    result["recovered_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (case / "result.json").write_text(json.dumps(result, indent=1),
                                      encoding="utf-8")
    return tag, elapsed, "ok"


def main() -> None:
    lost, other = lost_designs()
    print(f"{len(lost)} designs died in the launcher and are recoverable")
    if other:
        print(f"{len(other)} designs failed for some OTHER reason and are "
              f"NOT re-solved here: {other}")
    began = time.time()
    failures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for tag, _elapsed, status in pool.map(solve, lost):
            if status not in ("ok", "cached"):
                failures.append((tag, status))
    print(f"recovered {len(lost) - len(failures)}/{len(lost)} in "
          f"{time.time() - began:.1f} s wall on {MAX_WORKERS} workers")
    for tag, status in failures:
        print(f"  {tag}: {status}")


if __name__ == "__main__":
    main()
