"""Two controls on the shock-reflection display act.

A number that cannot be made to move is not a reading, and a gap that gets
drawn around is not a refusal. These are the two things this script proves,
and it proves them by breaking the inputs on a COPY and watching the screen.

CONTROL 1, PLANTED PERTURBATION. The two graded records are copied, a known
offset is added to the measured shock position on the fine grid, and the act
is driven against the copy. If the screen does not move by that offset, the
act is not reading the record it claims to read and every number it shows is
unverified.

CONTROL 2, PLANTED ABSENCE. The act is driven against a copy with the fine
grid's record removed. It must name the empty path and show no row for that
grid: never a zero, never a blank cell under a caption.

The act itself is never modified. Only its two path roots are pointed at the
copy, and the real run tree is opened read only.

    python3 plant_control.py
    python3 plant_control.py --module /path/to/dmr_display.py

STARTS NO SOLVER. Reads two JSON files and writes a copy of them under a
temporary directory that it removes on the next run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SDK = REPO / "sdk"
RUNS = REPO / "verification" / "runs" / "DMR_runs"
FIGURES = REPO / "docs" / "campaigns" / "DMR" / "demo" / "figures"
GRIDS = ("res60", "res120")
PLANT = 0.0500000


def load_act(module_path: Path):
    """Load the act into the real ``workflows`` package namespace.

    Loading it under its real dotted name is what makes its relative imports
    resolve exactly as they will once it is dispatched, so this control tests
    the module that would run and not a rearranged copy of it.
    """
    sys.path.insert(0, str(SDK))
    import workflows  # noqa: F401  (imported for its package side effects)

    spec = importlib.util.spec_from_file_location(
        "workflows.dmr_display", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["workflows.dmr_display"] = module
    spec.loader.exec_module(module)
    return module


def drive(act, runs_root: Path, out_root: Path):
    """Run the act against one run tree and collect what reached the screen."""
    act._RUNS = runs_root
    act._FIGURES = FIGURES
    act.OUT_ROOT = out_root
    rows: list[list[str]] = []
    notes: list[str] = []

    def emit(kind, payload):
        if kind == "transcript.table" and payload["table_id"] == "dmr-shock-position":
            rows.extend(payload["rows"])
        elif kind == "transcript.entry":
            notes.append(str(payload.get("message", "")))

    rc = act.main("double Mach reflection", {}, emit)
    return rc, rows, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--module", default=str(SDK / "workflows" / "dmr_display.py"),
        help="the act to test; defaults to the dispatched module")
    args = parser.parse_args()

    module_path = Path(args.module)
    if not module_path.exists():
        print(f"REFUSED: no act at {module_path}. Nothing was tested.")
        return 2
    act = load_act(module_path)

    work = Path(tempfile.mkdtemp(prefix="dmr_plant_"))
    try:
        planted = work / "planted_tree"
        for grid in GRIDS:
            (planted / grid).mkdir(parents=True)
            shutil.copy(RUNS / grid / "locator_result.json",
                        planted / grid / "locator_result.json")

        # ---- control 1 ----
        record_path = planted / "res120" / "locator_result.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["gateV"]["x_measured"] += PLANT
        record["gateV"]["error"] += PLANT
        record_path.write_text(json.dumps(record), encoding="utf-8")

        _rc, rows_real, _ = drive(act, RUNS, work / "out_real")
        _rc, rows_plant, _ = drive(act, planted, work / "out_plant")
        fine_real = next(r for r in rows_real if r[0] == "Fine grid")
        fine_plant = next(r for r in rows_plant if r[0] == "Fine grid")
        moved = float(fine_plant[2]) - float(fine_real[2])
        seen = abs(moved - PLANT) < 5e-5
        print("=== CONTROL 1: planted perturbation ===")
        print(f"  planted offset, fine grid    : {PLANT:.7f}")
        print(f"  screen, real records         : {fine_real[2]}")
        print(f"  screen, planted records      : {fine_plant[2]}")
        print(f"  screen moved by              : {moved:.7f}")
        print(f"  share of travel              : {fine_real[5]} -> {fine_plant[5]}")
        print("  RESULT: " + ("SEEN, the act is reading disk" if seen else
                              "NOT SEEN, the screen did not follow the record"))

        # ---- control 2 ----
        record_path.unlink()
        rc_gap, rows_gap, notes_gap = drive(act, planted, work / "out_gap")
        named = any("locator_result.json" in note for note in notes_gap)
        missing_rows = [r for r in rows_gap if r[0] == "Fine grid"]
        refused = not missing_rows and named
        print("\n=== CONTROL 2: planted absence ===")
        print(f"  return code                  : {rc_gap}")
        print(f"  rows shown for missing grid  : {len(missing_rows)}")
        print(f"  empty path named on record   : {named}")
        print("  RESULT: " + ("REFUSED and named the gap" if refused else
                              "DID NOT REFUSE, a gap was drawn around"))
        return 0 if (seen and refused) else 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
