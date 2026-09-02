#!/usr/bin/env python3
"""M6S-P pyHyp march-log reader.

Frozen registration: verification/campaign/M6S_P_PYHYP_WALL_RESOLVED_PROBE_PREREGISTRATION.md
(blob 8fad9c6019174c235c79ac9948796c9c60b381b8, amended commit 87a6364f).

WHICH INSTRUMENT IS WHICH (amendment A1.3, and it must not be inverted):
  (a) SANITY  -- the log's shape: a line containing '| Min     | Min     |' immediately
      followed by a line containing '| Quality | Volume  |'.  This tests whether the file
      has the shape of a pyHyp march log.  IT IS NOT THE MEASUREMENT.
  (b) INSTRUMENT -- the POSITIONAL read of table column 9 (Min Quality) and column 10
      (Min Volume), column 12 (March Distance), column 2 (CPU Time), column 1 (level).
      This produces the numbers.

The literal string 'Min Quality' occurs ZERO times in any pyHyp log (A1.2); the original
§2/§4.1 clause requiring it is STRUCK.

Data rows are distinguished from header rows by NOT beginning with '#' (A1.5); pyHyp
REPRINTS the whole header block mid-table, so a reader that assumes one header block, or
that counts lines instead of testing the '#' prefix, miscounts.

Refusals (§4.2): an ABSENT log reads ABSENT and never reads clean; a short table reads
INCOMPLETE and never reads clean; the reader refuses (exit 2) rather than degrade.
"""
import argparse
import json
import os
import re
import sys

NUM = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([EeDd][-+]?[0-9]+)?$")
HDR_A = "| Min     | Min     |"
HDR_B = "| Quality | Volume  |"
GRID_RATIO = re.compile(r"^\s*Grid Ratio:\s*([-+0-9.EeDd]+)\s*$")
NCOL = 14
# 1-based table columns, from the stacked header (A1.3 / §2)
C_LVL, C_CPU, C_MINQ, C_MINV, C_MARCH = 1, 2, 9, 10, 12
MARCH_TARGET = 12.0
# 'equals 0.120E+02 at the printed precision' (§2 reading 2b): the printed mantissa carries
# three significant digits, so the last printed digit is worth 0.1 and half an ulp is 0.05.
MARCH_HALF_ULP = 0.05


def _f(tok):
    return float(tok.replace("D", "E").replace("d", "e"))


def stacked_header_pairs(lines):
    """(a) SANITY ONLY. Returns the count of stacked 'Min|Min' / 'Quality|Volume' pairs."""
    n = 0
    for i in range(len(lines) - 1):
        if HDR_A in lines[i] and HDR_B in lines[i + 1]:
            n += 1
    return n


def data_rows(lines):
    """(b) INSTRUMENT. A data row does NOT begin with '#' and carries 14 numeric fields."""
    rows = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        f = s.split()
        if len(f) != NCOL:
            continue
        if not all(NUM.match(x) for x in f):
            continue
        rows.append((i + 1, f))
    return rows


def read(path, expect_levels):
    out = {"log": path, "expect_levels": expect_levels}
    if not os.path.exists(path):
        out["state"] = "ABSENT"
        return out, 2
    lines = open(path, errors="replace").read().split("\n")
    out["stacked_header_pairs"] = stacked_header_pairs(lines)
    out["hash_lines"] = sum(1 for l in lines if l.lstrip().startswith("#"))
    out["literal_Min_Quality_occurrences"] = sum(l.count("Min Quality") for l in lines)

    gr = None
    for l in lines:
        if l.lstrip().startswith("#"):
            continue
        m = GRID_RATIO.match(l)
        if m:
            gr = m.group(1)
            break
    out["header_grid_ratio_raw"] = gr

    rows = data_rows(lines)
    out["n_data_rows"] = len(rows)
    if not rows:
        out["state"] = "INCOMPLETE"
        out["reason"] = "no data rows"
        return out, 2
    levels = [int(_f(f[C_LVL - 1])) for _, f in rows]
    out["level_first"], out["level_last"] = levels[0], levels[-1]
    expected_rows = expect_levels - 1
    contiguous = levels == list(range(2, expect_levels + 1))
    out["expected_data_rows"] = expected_rows
    out["levels_contiguous_2_to_N"] = contiguous
    complete = (len(rows) == expected_rows) and contiguous

    # Reading 1 -- Min Quality (col 9) at EVERY level, and Min Volume (col 10)
    mq = [(lv, f[C_MINQ - 1], _f(f[C_MINQ - 1])) for lv, (_, f) in zip(levels, rows)]
    mv = [(lv, f[C_MINV - 1], _f(f[C_MINV - 1])) for lv, (_, f) in zip(levels, rows)]
    lo_q = min(mq, key=lambda t: t[2])
    lo_v = min(mv, key=lambda t: t[2])
    neg = [t for t in mq if t[2] < 0.0]
    out["min_quality_min_raw"] = lo_q[1]
    out["min_quality_min"] = lo_q[2]
    out["min_quality_min_level"] = lo_q[0]
    out["min_quality_first_negative_raw"] = neg[0][1] if neg else None
    out["min_quality_first_negative_level"] = neg[0][0] if neg else None
    out["min_quality_n_negative_levels"] = len(neg)
    out["min_quality_all_positive"] = len(neg) == 0
    out["min_volume_min_raw"] = lo_v[1]
    out["min_volume_min"] = lo_v[2]
    out["min_volume_min_level"] = lo_v[0]
    out["min_volume_negative_anywhere"] = lo_v[2] < 0.0
    out["min_quality_column"] = [[lv, raw] for lv, raw, _ in mq]

    # Reading 2 -- march closure.  (b) is authoritative; (a) alone is a symptom.
    last_march_raw = rows[-1][1][C_MARCH - 1]
    out["last_level_march_distance_raw"] = last_march_raw
    out["last_level_march_distance"] = _f(last_march_raw)
    out["march_target"] = MARCH_TARGET
    out["march_closed"] = abs(_f(last_march_raw) - MARCH_TARGET) <= MARCH_HALF_ULP
    out["march_fraction_of_target"] = _f(last_march_raw) / MARCH_TARGET

    # Reading 3 -- achieved first cell height = level-2 cumulative March Distance
    l2 = [r for lv, r in zip(levels, rows) if lv == 2]
    out["level2_march_distance_raw"] = l2[0][1][C_MARCH - 1] if l2 else None
    out["achieved_first_cell_height"] = _f(l2[0][1][C_MARCH - 1]) if l2 else None

    # Reading 4 -- pyHyp serial CPU time, col 2 of the last level
    out["last_level_cpu_s_raw"] = rows[-1][1][C_CPU - 1]
    out["last_level_cpu_s"] = _f(rows[-1][1][C_CPU - 1])

    out["state"] = "COMPLETE" if complete else "INCOMPLETE"
    return out, (0 if complete else 2)


def selftest_header_detector(path):
    """Rule 3 for the SANITY limb, as A1.5 registers it: with the second header line
    removed the stacked-pair count must fall to 0.  A detector that still reports a pair
    on the mutated text cannot see the failure it exists to catch."""
    lines = open(path, errors="replace").read().split("\n")
    before = stacked_header_pairs(lines)
    mutated = [l for l in lines if HDR_B not in l]
    after = stacked_header_pairs(mutated)
    return before, after


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--expect-levels", type=int, required=True)
    ap.add_argument("--json-out")
    ap.add_argument("--selftest-header", action="store_true")
    a = ap.parse_args()
    if a.selftest_header:
        b, af = selftest_header_detector(a.log)
        print(json.dumps({"header_detector_plant": {"before": b, "after_second_line_removed": af,
                                                    "fell_to_zero": af == 0}}))
        return 0 if (b > 0 and af == 0) else 2
    out, rc = read(a.log, a.expect_levels)
    if a.json_out:
        with open(a.json_out, "w") as fh:
            json.dump(out, fh, indent=2)
    slim = {k: v for k, v in out.items() if k != "min_quality_column"}
    print(json.dumps(slim, indent=2))
    return rc


if __name__ == "__main__":
    sys.exit(main())
