#!/usr/bin/env python3
"""Turn the frozen A2 decomposition grader's own output into a display record.

WHY THIS EXISTS. Act D shows a 28.3% drag reduction, and Sanaa's feedback item
2 (2026-09-01) requires the act to show WHERE that 28.3% came from rather than
quote it bare. The decomposition itself was run and graded elsewhere, against
gates frozen before the run, by ``grade_a2_decomposition.py``. That grader
PRINTS; it writes no machine-readable record, and it is the grading path fixed
at the pre-registration commit, so it is not edited to make one.

So this script is a READER, never a second grader. It runs the frozen grader as
a subprocess and parses the numbers out of the grader's own stdout. It computes
NOTHING of its own: every value in the record it writes was printed by the
grader. The only arithmetic here is the two counter-example percentages, and
those are derived from grader-printed CD and CL and are labelled as derived.

Three modes:

  (default)   run the grader, parse it, WRITE the record
  --check     run the grader, parse it, and compare against the record on disk;
              exit 2 on any disagreement
  --selftest  the planted control for --check. A reader that reports "no
              disagreement" is worthless until it has been shown able to report
              one, so this plants a known perturbation into the parsed values
              and REFUSES unless the comparison catches it.

The record carries the grader's sha256 and the run directory, so a number in
the act can be walked back to the solve that produced it.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRADER = HERE / "grade_a2_decomposition.py"
ROWS_SPEC = HERE / "a2_decomposition_rows.json"
PREREG = HERE / "A2_DRAG_DECOMPOSITION_PREREGISTRATION.md"
RUN_DIR = Path("/home/ubuntu/certonomous-runs/ACTD-a2-decomposition")
RECORD = HERE / "ladder-a" / "A2_drag_decomposition.json"

# A row line: id, CD, CL, AoA, thickness min/max, worst final residual.
_ROW = re.compile(
    r"^(\w+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+"
    r"([\d.]+)/\s*([\d.]+)\s+([\d.eE+-]+)\s*$")
_LIFT = re.compile(
    r"^(baseline|twist only  @CL0\.5|twist\+shape @CL0\.5)\s+"
    r"CD\s+([\d.]+)\s+CL\s+([\d.]+)(?:\s+AoA\s+([\d.-]+))?\s*$")
_TOTAL = re.compile(r"^total reduction\s+([\d.]+)%")
_SHARE = re.compile(r"^\s+attributable to (\w+)\s+([+-]?[\d.]+)% of the drop"
                    r"\s+\(([+-][\d.]+)% of baseline drag\)")
_GATE = re.compile(r"^(G\d)\s.*?->\s+(PASS|FAIL.*)$")
_PLANT = re.compile(r"^planted ctrl 1\s+.*deviation over (\d+) rows:\s+"
                    r"([\d.eE+-]+)\s+->\s+(PASS|FAIL.*)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_grader() -> str:
    proc = subprocess.run([sys.executable, str(GRADER)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"grader exited {proc.returncode}\n{proc.stderr}")
    return proc.stdout


def parse(text: str) -> dict:
    rows, lift, shares, gates = {}, {}, {}, {}
    total = None
    plant = None
    for line in text.splitlines():
        m = _ROW.match(line)
        if m and m.group(1) != "row":
            rows[m.group(1)] = {
                "CD": float(m.group(2)), "CL": float(m.group(3)),
                "AoA_deg": float(m.group(4)),
                "thickness_min": float(m.group(5)),
                "thickness_max": float(m.group(6)),
                "final_residual": float(m.group(7))}
            continue
        m = _LIFT.match(line)
        if m:
            key = {"baseline": "baseline",
                   "twist only  @CL0.5": "twist_only_at_CL05",
                   "twist+shape @CL0.5": "twist_and_shape_at_CL05"}[m.group(1)]
            lift[key] = {"CD": float(m.group(2)), "CL": float(m.group(3))}
            if m.group(4):
                lift[key]["AoA_deg"] = float(m.group(4))
            continue
        m = _TOTAL.match(line)
        if m:
            total = float(m.group(1))
            continue
        m = _SHARE.match(line)
        if m:
            shares[m.group(1)] = {"pct_of_drop": float(m.group(2)),
                                  "pct_of_baseline_drag": float(m.group(3))}
            continue
        m = _GATE.match(line)
        if m:
            gates[m.group(1)] = m.group(2)
            continue
        m = _PLANT.match(line)
        if m:
            plant = {"rows": int(m.group(1)), "max_deviation": float(m.group(2)),
                     "verdict": m.group(3)}
    if not rows or not lift or total is None:
        raise SystemExit("the grader's output did not parse; refusing to write "
                         "a record from a reading I cannot make")
    return {"rows": rows, "lift_matched": lift, "total_reduction_pct": total,
            "shares": shares, "gates": gates, "planted_control_1": plant}


def build(parsed: dict) -> dict:
    """The record. Everything measured is the grader's; the two counter-example
    percentages are DERIVED from its CD and CL and say so."""
    r = parsed["rows"]
    base_cd = r["A0_baseline"]["CD"]
    base_cl = r["A0_baseline"]["CL"]
    trap = {}
    if "A3_aoa_only" in r:
        a3 = r["A3_aoa_only"]
        trap["unmodified_wing_at_final_incidence"] = {
            "CD": a3["CD"], "CL": a3["CL"], "AoA_deg": a3["AoA_deg"],
            "apparent_drag_reduction_pct_DERIVED":
                round(100.0 * (base_cd - a3["CD"]) / base_cd, 4),
            "lift_given_up_pct_DERIVED":
                round(100.0 * (base_cl - a3["CL"]) / base_cl, 4)}
    if "A2_twist_shape" in r:
        a2 = r["A2_twist_shape"]
        trap["twist_and_shape_at_original_incidence"] = {
            "CD": a2["CD"], "CL": a2["CL"], "AoA_deg": a2["AoA_deg"],
            "apparent_drag_change_pct_DERIVED":
                round(100.0 * (a2["CD"] - base_cd) / base_cd, 4),
            "lift_gained_pct_DERIVED":
                round(100.0 * (a2["CL"] - base_cl) / base_cl, 4)}
    return {
        "_what": "The lift-matched decomposition of the A2 drag reduction, as "
                 "printed by the frozen grader. Act D reads this file; it does "
                 "not recompute any of it.",
        "_derived_from": "grade_a2_decomposition.py stdout, parsed. The only "
                         "values not printed by the grader are the four keys "
                         "ending _DERIVED, which are ratios of grader-printed "
                         "CD and CL.",
        "_grader": str(GRADER), "_grader_sha256": sha256(GRADER),
        "_rows_spec_sha256": sha256(ROWS_SPEC),
        "_preregistration": str(PREREG), "_preregistration_sha256": sha256(PREREG),
        "_run_dir": str(RUN_DIR),
        "_G5_status": "UNGRADED. The registered independent falsifier row "
                      "B2_twist_shape_CL05 did not run: its primal diverged, so "
                      "it is NOT A RESULT and gate G5 has no verdict. The "
                      "zero angle-of-attack share therefore rests on G6 (both "
                      "endpoints measured at CL 0.500 to better than 1e-3) and "
                      "on lift being an equality constraint of the problem, "
                      "and its independent cross-check did not run.",
        **parsed, "counter_examples": trap}


def compare(a: dict, b: dict, path: str = "") -> list[str]:
    bad = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k.startswith("_"):
                continue
            if k not in a or k not in b:
                bad.append(f"{path}{k}: present in only one")
            else:
                bad += compare(a[k], b[k], f"{path}{k}.")
    elif isinstance(a, float) and isinstance(b, float):
        if a != b:
            bad.append(f"{path[:-1]}: {a!r} != {b!r}")
    elif a != b:
        bad.append(f"{path[:-1]}: {a!r} != {b!r}")
    return bad


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "write"
    parsed = parse(run_grader())
    fresh = build(parsed)

    if mode == "--selftest":
        # THE PLANTED CONTROL. A comparison that reports "no disagreement" is
        # not evidence until it has been shown able to report one.
        clean = compare(fresh, build(parse(run_grader())))
        if clean:
            print("SELFTEST REFUSED: the grader disagrees with itself:", clean)
            return 2
        bent = json.loads(json.dumps(fresh))
        bent["rows"]["A0_baseline"]["CD"] += 1.234e-09
        caught = compare(fresh, bent)
        if not caught:
            print("SELFTEST REFUSED: a planted 1.234e-09 shift in A0's CD was "
                  "NOT caught. This reader cannot see a disagreement, so its "
                  "agreements mean nothing.")
            return 2
        print(f"selftest PASS: clean comparison empty; planted 1.234e-09 shift "
              f"in A0_baseline.CD caught as {caught[0]}")
        return 0

    if mode == "--check":
        if not RECORD.exists():
            print(f"no record at {RECORD}")
            return 2
        bad = compare(fresh, json.loads(RECORD.read_text(encoding="utf-8")))
        if bad:
            print("RECORD DISAGREES WITH THE FROZEN GRADER:")
            for b in bad:
                print("  ", b)
            return 2
        print(f"check PASS: {RECORD.name} matches the frozen grader "
              f"(sha256 {fresh['_grader_sha256'][:12]})")
        return 0

    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(fresh, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {RECORD}")
    print(f"  total reduction {fresh['total_reduction_pct']}%  "
          f"twist {fresh['shares']['twist']['pct_of_drop']}%  "
          f"shape {fresh['shares']['shape']['pct_of_drop']}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
