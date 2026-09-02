#!/usr/bin/env python3
"""M6S-P §5 PLANTED CONTROLS -- rule 3.  Run BEFORE the probe; a control that fails is a
finding and STOPS the probe.  It is not repaired by loosening the reading.

Control A -- the Min Quality reader must catch the lab's registered born-broken mesh.
Control B -- the march-closure reader must catch a silently clamped, under-marched grid.
Control C -- the completeness reader must catch a truncated table.
Plus A1.5's header-detector plant: stacked pairs must fall 2 -> 0 on the mutated text.

Every required value below is quoted from the FROZEN registration (§5) and is compared as
the RAW PRINTED TOKEN, not as a re-formatted float.
"""
import json
import subprocess
import sys
from pathlib import Path

READER = Path(__file__).with_name("read_pyhyp_log.py")


def run(log, levels):
    p = subprocess.run([sys.executable, str(READER), "--log", str(log),
                        "--expect-levels", str(levels)],
                       capture_output=True, text=True)
    return json.loads(p.stdout), p.returncode


def main():
    ctlA, ctlB, ctlC = sys.argv[1], sys.argv[2], sys.argv[3]
    results = []
    ok = True

    a, rcA = run(ctlA, 65)
    checks = [
        ("A: state COMPLETE (the specimen's own table is whole)", a["state"] == "COMPLETE", a["state"]),
        ("A: minimum Min Quality over all levels == -1.00000", a["min_quality_min_raw"] == "-1.00000", a["min_quality_min_raw"]),
        ("A: FIRST negative Min Quality == -0.34602", a["min_quality_first_negative_raw"] == "-0.34602", a["min_quality_first_negative_raw"]),
        ("A: ... at marching level 2", a["min_quality_first_negative_level"] == 2, a["min_quality_first_negative_level"]),
        ("A: minimum Min Volume is NEGATIVE", a["min_volume_negative_anywhere"] is True, a["min_volume_min_raw"]),
        ("A: minimum Min Volume == -0.330E-08", a["min_volume_min_raw"] == "-0.330E-08", a["min_volume_min_raw"]),
        ("A: header Grid Ratio == 1.1674", a["header_grid_ratio_raw"] == "1.1674", a["header_grid_ratio_raw"]),
        ("A: level-2 March Distance == 0.108E-03", a["level2_march_distance_raw"] == "0.108E-03", a["level2_march_distance_raw"]),
        ("A: reader does NOT report this known-bad mesh clean", a["min_quality_all_positive"] is False, a["min_quality_n_negative_levels"]),
        ("A: literal string 'Min Quality' occurs 0 times (A1.2)", a["literal_Min_Quality_occurrences"] == 0, a["literal_Min_Quality_occurrences"]),
        ("A: stacked header pairs == 2 (pyHyp reprints the block, A1.5)", a["stacked_header_pairs"] == 2, a["stacked_header_pairs"]),
        ("A: lines beginning '#' == 12 (A1.5)", a["hash_lines"] == 12, a["hash_lines"]),
        ("A: data rows == 64, levels 2..65 (A1.5)", a["n_data_rows"] == 64 and a["levels_contiguous_2_to_N"], a["n_data_rows"]),
    ]

    b, rcB = run(ctlB, 8)
    checks += [
        ("B: header Grid Ratio == 4.0000 (the silent clamp)", b["header_grid_ratio_raw"] == "4.0000", b["header_grid_ratio_raw"]),
        ("B: last-level March Distance == 0.546E+00", b["last_level_march_distance_raw"] == "0.546E+00", b["last_level_march_distance_raw"]),
        ("B: march reported NOT CLOSED on 12.0", b["march_closed"] is False, b["march_closed"]),
    ]

    c, rcC = run(ctlC, 65)
    checks += [
        ("C: truncated table reads INCOMPLETE, not clean", c["state"] == "INCOMPLETE", c["state"]),
        ("C: reader exits 2 rather than degrade (§4.1)", rcC == 2, rcC),
        ("C: truncated row count < 64", c["n_data_rows"] < 64, c["n_data_rows"]),
    ]

    p = subprocess.run([sys.executable, str(READER), "--log", ctlA, "--expect-levels", "65",
                        "--selftest-header"], capture_output=True, text=True)
    plant = json.loads(p.stdout)["header_detector_plant"]
    checks += [
        ("PLANT: stacked-pair detector falls 2 -> 0 on mutated text (A1.5)",
         plant["before"] == 2 and plant["after_second_line_removed"] == 0,
         "%s -> %s" % (plant["before"], plant["after_second_line_removed"])),
    ]

    for name, passed, got in checks:
        results.append({"check": name, "pass": bool(passed), "observed": got})
        if not passed:
            ok = False
        print("%-4s %-64s observed=%s" % ("PASS" if passed else "FAIL", name, got))

    print("\nCONTROLS: %s (%d/%d)" % ("ALL PASS" if ok else "FAILED", sum(r["pass"] for r in results), len(results)))
    Path(sys.argv[4]).write_text(json.dumps(
        {"controls_all_pass": ok, "checks": results,
         "control_A": a, "control_B": b, "control_C": c,
         "header_detector_plant": plant}, indent=2) + "\n")
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
