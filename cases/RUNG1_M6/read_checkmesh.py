#!/usr/bin/env python3
"""R1-M0 checkMesh reader -- verification/campaign/RUNG1_M6_PREREGISTRATION.md §5, §9, §11.4.

WHAT THIS READER IS FOR, AND THE TRAP IT EXISTS TO AVOID
--------------------------------------------------------
`checkMesh` prints its own verdict line and THAT LINE IS WORTHLESS AS A GATE.
Measured on this box's own production artifacts: all 885 `log.checkMesh` files under
`verification/runs/` print `Non-orthogonality check OK.` -- INCLUDING
`verification/runs/F13_ONERA_M6_runs/mesh/m1/log.checkMesh`, whose own numeric line
reads `Mesh non-orthogonality Max: 84.6437`, and including the DPW5/HLPW6 committee
grids at 89.71 / 89.94 / 90.00 / 89.98 degrees.  A reader that takes the verdict line
records a 90-degree mesh as passing.

THEREFORE: this reader parses the NUMBER off `Mesh non-orthogonality Max:` and never
consults `Non-orthogonality check OK.` / `FAILED` / `Failed N mesh checks`.  The verdict
line IS captured, into a field named `verdict_line_IGNORED_NEVER_A_GATE`, so that a
later reader can see it was seen and discarded rather than never looked at.

REFUSES RATHER THAN DEGRADES (rule 4; prereg §8: "An absent checkMesh log reads ABSENT.
It never reads clean.").  Exit 2 on an absent, unreadable or incomplete log.  There is no
path through this file on which a missing number becomes a passing one.

NO VERDICT OF THE FIXED VOCABULARY ATTACHES TO ANYTHING THIS READER PRINTS.  R1-M0 is an
admissibility measurement that gates a freeze (prereg §5 label).  The reader reports
`above_70` / `at_or_below_70` as a plain arithmetic comparison and nothing else.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile

NUM = r"([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)"

# --- the numeric instruments.  ONE form each for non-orthogonality; TWO for aspect ratio
# --- and skewness, because §9's plant is that a reader matching only `=` sees 745 of the
# --- lab's 885 logs and silently misses exactly the 140 pathological ones (measured).
RE_NONORTH = re.compile(r"Mesh non-orthogonality Max:\s*" + NUM + r"\s+average:\s*" + NUM)
RE_SKEW_EQ = re.compile(r"Max skewness\s*=\s*" + NUM)
RE_SKEW_CO = re.compile(r"Max skewness\s*:\s*" + NUM)
RE_AR_EQ = re.compile(r"Max aspect ratio\s*=\s*" + NUM)
RE_AR_CO = re.compile(r"Max aspect ratio\s*:\s*" + NUM)
RE_VOL = re.compile(r"Min volume\s*=\s*" + NUM + r"\.\s*Max volume\s*=\s*" + NUM)
RE_CELLS = re.compile(r"^\s*cells:\s*([0-9]+)\s*$", re.M)
RE_POINTS = re.compile(r"^\s*points:\s*([0-9]+)\s*$", re.M)
RE_FACES = re.compile(r"^\s*faces:\s*([0-9]+)\s*$", re.M)
RE_INTFACES = re.compile(r"^\s*internal faces:\s*([0-9]+)\s*$", re.M)
# DECISIVE, AND THE REASON IT IS HERE: `plot3dToFoam` converts a NINE-BLOCK PLOT3D grid.
# If it failed to merge the coincident block-interface points, those interfaces would
# become BOUNDARY faces -- and checkMesh computes non-orthogonality over INTERNAL faces
# only, so every block interface would drop out of the statistic and the reported maximum
# would be FALSELY OPTIMISTIC.  An unmerged conversion shows up as `Number of regions: 9`.
# The driver REFUSES on anything but 1.  Without this the 70-degree reading would be
# unfalsifiable.
RE_REGIONS = re.compile(r"Number of regions:\s*([0-9]+)")
RE_GEODIR = re.compile(r"Mesh has\s+([0-9]+)\s+geometric")
RE_SEVERE = re.compile(r"Number of severely non-orthogonal\s*\(>\s*" + NUM +
                       r"\s*degrees\)\s*faces:\s*([0-9]+)")
RE_ARFLAG = re.compile(r"High aspect ratio cells found.*?number of cells\s*([0-9]+)")
RE_END = re.compile(r"^End\s*$", re.M)

# CAPTURED AND NEVER USED.  Present so the discard is visible on the record.
RE_VERDICT = re.compile(r"^\s*(Non-orthogonality check .*|Mesh OK\.|Failed [0-9]+ mesh checks?\.)\s*$", re.M)


def _f(m, g=1):
    return None if m is None else float(m.group(g))


def read_log(path: str) -> dict:
    """Parse one checkMesh log.  Returns a dict whose `state` is COMPLETE or a refusal."""
    if not os.path.exists(path):
        return {"state": "ABSENT", "log": path,
                "note": "prereg §8: an absent checkMesh log reads ABSENT, never clean"}
    try:
        s = open(path, errors="replace").read()
    except OSError as exc:
        return {"state": "UNREADABLE", "log": path, "error": str(exc)}
    if not s.strip():
        return {"state": "EMPTY", "log": path}

    mno = RE_NONORTH.search(s)
    msk = RE_SKEW_EQ.search(s) or RE_SKEW_CO.search(s)
    mar = RE_AR_EQ.search(s) or RE_AR_CO.search(s)
    mvol = RE_VOL.search(s)
    msev = RE_SEVERE.search(s)
    marf = RE_ARFLAG.search(s)

    minv, maxv = (_f(mvol, 1), _f(mvol, 2)) if mvol else (None, None)
    vol_ratio = None
    if minv is not None and maxv is not None and minv != 0.0:
        vol_ratio = maxv / minv

    out = {
        "state": "COMPLETE",
        "log": path,
        "log_bytes": os.path.getsize(path),
        "log_mtime": os.path.getmtime(path),
        # ---- THE GATE-A NUMBERS, ALL PARSED NUMERICALLY ----
        "max_non_orthogonality_deg": _f(mno, 1),
        "avg_non_orthogonality_deg": _f(mno, 2),
        "max_skewness": _f(msk),
        "max_skewness_label_form": ("=" if RE_SKEW_EQ.search(s) else
                                    (":" if RE_SKEW_CO.search(s) else None)),
        "max_aspect_ratio": _f(mar),
        "max_aspect_ratio_label_form": ("=" if RE_AR_EQ.search(s) else
                                        (":" if RE_AR_CO.search(s) else None)),
        "aspect_ratio_flagged": (int(marf.group(1)) if marf else 0),
        "min_cell_volume": minv,
        "max_cell_volume": maxv,
        "cell_volume_ratio_DERIVED": vol_ratio,
        "geometric_directions": (int(RE_GEODIR.search(s).group(1)) if RE_GEODIR.search(s) else None),
        "severe_non_orth_faces": (int(msev.group(2)) if msev else None),
        "severe_non_orth_threshold_deg": (_f(msev, 1) if msev else None),
        "cells": (int(RE_CELLS.search(s).group(1)) if RE_CELLS.search(s) else None),
        "points": (int(RE_POINTS.search(s).group(1)) if RE_POINTS.search(s) else None),
        "faces": (int(RE_FACES.search(s).group(1)) if RE_FACES.search(s) else None),
        "internal_faces": (int(RE_INTFACES.search(s).group(1)) if RE_INTFACES.search(s) else None),
        "n_regions": (int(RE_REGIONS.search(s).group(1)) if RE_REGIONS.search(s) else None),
        "has_End_line": bool(RE_END.search(s)),
        # ---- SEEN AND DISCARDED.  NOT A GATE.  NEVER READ BY ANY BRANCH BELOW. ----
        "verdict_line_IGNORED_NEVER_A_GATE": [m.group(1) for m in RE_VERDICT.finditer(s)],
    }

    if out["faces"] is not None and out["internal_faces"] is not None:
        out["boundary_faces_DERIVED"] = out["faces"] - out["internal_faces"]

    # The §11.4 non-null set.  A null here is a REFUSAL, not a soft field.
    required = ["max_non_orthogonality_deg", "max_skewness", "max_aspect_ratio",
                "min_cell_volume", "max_cell_volume", "cell_volume_ratio_DERIVED",
                "geometric_directions", "cells", "n_regions"]
    missing = [k for k in required if out.get(k) is None]
    if missing:
        out["state"] = "INCOMPLETE"
        out["missing_fields"] = missing
        return out

    # Plain arithmetic against MESH_STANDARD §3.1 / §3.2, taken from the NUMBERS.
    # This is NOT a verdict of the fixed vocabulary (prereg §5 label).
    out["non_orth_vs_70"] = ("at_or_below_70" if out["max_non_orthogonality_deg"] <= 70.0
                             else "above_70")
    out["skewness_vs_4"] = ("at_or_below_4" if out["max_skewness"] <= 4.0 else "above_4")
    return out


# ---------------------------------------------------------------------------------------
# PLANTED CONTROLS -- rule 3 and prereg §9.  A ZERO FROM A READER NOT SHOWN ABLE TO SEE A
# NON-ZERO IS NOT EVIDENCE.  Every control below runs against a REAL artifact on this box
# or a mutation of one written to disk and read back from disk.  If ANY control fails the
# caller must stop: a control that fails is a finding, never repaired by loosening a read.
# ---------------------------------------------------------------------------------------
def selftest(eq_log: str, colon_log: str, workdir: str) -> tuple[bool, list]:
    ctl = []

    def add(name, ok, observed, expect):
        ctl.append({"control": name, "pass": bool(ok),
                    "observed": observed, "expected": expect})

    # C1 -- §9 plant: the `=` label form must yield a NON-NULL max aspect ratio.
    a = read_log(eq_log)
    add("C1 `=` label form yields a non-null max aspect ratio",
        a.get("state") == "COMPLETE" and a.get("max_aspect_ratio") is not None
        and a.get("max_aspect_ratio_label_form") == "=",
        {"state": a.get("state"), "max_aspect_ratio": a.get("max_aspect_ratio"),
         "form": a.get("max_aspect_ratio_label_form")},
        "non-null, form '='")

    # C2 -- §9 plant: the `:` label form must ALSO yield a NON-NULL max aspect ratio.
    #       A reader matching only `=` returns null here and silently misses exactly the
    #       pathological logs (measured: 140 of 885 on this box).
    b = read_log(colon_log)
    add("C2 `:` label form yields a non-null max aspect ratio",
        b.get("state") == "COMPLETE" and b.get("max_aspect_ratio") is not None
        and b.get("max_aspect_ratio_label_form") == ":",
        {"state": b.get("state"), "max_aspect_ratio": b.get("max_aspect_ratio"),
         "form": b.get("max_aspect_ratio_label_form")},
        "non-null, form ':'")

    # C3 -- §9 plant: Min volume != Max volume must give a NON-TRIVIAL derived ratio,
    #       never 1.  (A reader that hard-codes or collapses the ratio reads 1 here.)
    r = b.get("cell_volume_ratio_DERIVED")
    add("C3 Min volume != Max volume gives a non-trivial cell-volume ratio (never 1)",
        r is not None and r > 1.0 + 1e-9,
        {"min": b.get("min_cell_volume"), "max": b.get("max_cell_volume"), "ratio": r},
        "ratio strictly > 1")

    # C4 -- THE VERDICT-LINE TRAP, on a REAL production artifact.  This log's numeric max
    #       non-orthogonality is 84.6437 and its own verdict line says
    #       `Non-orthogonality check OK.`  The reader must report ABOVE 70.
    v = b.get("max_non_orthogonality_deg")
    said_ok = any("Non-orthogonality check OK" in x
                  for x in b.get("verdict_line_IGNORED_NEVER_A_GATE", []))
    add("C4 verdict-line trap: a log that SAYS `check OK` at >70 deg is read as above_70",
        v is not None and v > 70.0 and said_ok and b.get("non_orth_vs_70") == "above_70",
        {"numeric_max_deg": v, "log_says_check_OK": said_ok,
         "reader_says": b.get("non_orth_vs_70")},
        "numeric > 70, log says OK, reader says above_70")

    # C5 -- MUTATION, written to disk and read BACK FROM DISK.  Proves the number comes
    #       off the file and is not a constant, a cache or a recollection.
    mut = os.path.join(workdir, "PLANT_mutated_checkMesh.log")
    src = open(colon_log, errors="replace").read()
    planted = 12.3456
    mtxt, nsub = re.subn(r"(Mesh non-orthogonality Max:\s*)" + NUM,
                         r"\g<1>%s" % planted, src, count=1)
    open(mut, "w").write(mtxt)
    m = read_log(mut)
    add("C5 mutation: a planted 12.3456 on disk is read back exactly",
        nsub == 1 and m.get("max_non_orthogonality_deg") == planted
        and m.get("non_orth_vs_70") == "at_or_below_70",
        {"substitutions": nsub, "read_back": m.get("max_non_orthogonality_deg"),
         "reader_says": m.get("non_orth_vs_70")},
        "12.3456, at_or_below_70")

    # C6 -- ABSENCE.  prereg §8: an absent log reads ABSENT.  It NEVER reads clean, and it
    #       never yields a number.
    ab = read_log(os.path.join(workdir, "no_such_checkMesh_log_exists.txt"))
    add("C6 an absent log reads ABSENT and yields no number",
        ab.get("state") == "ABSENT" and ab.get("max_non_orthogonality_deg") is None,
        {"state": ab.get("state"), "max": ab.get("max_non_orthogonality_deg")},
        "ABSENT, no number")

    # C7 -- TRUNCATION.  A log cut off before the geometry block must REFUSE (INCOMPLETE),
    #       not silently return partial numbers that a caller could mistake for a reading.
    trunc = os.path.join(workdir, "PLANT_truncated_checkMesh.log")
    open(trunc, "w").write(src[:src.find("Checking geometry")])
    t = read_log(trunc)
    add("C7 a log truncated before the geometry block REFUSES rather than degrades",
        t.get("state") in ("INCOMPLETE", "EMPTY"),
        {"state": t.get("state"), "missing": t.get("missing_fields")},
        "INCOMPLETE")

    # C8 -- THE PLANTED ZERO, and it is the point of C4/C5 as much as of itself.  The
    #       reader has now been shown able to report 84.6437 (C4) and 12.3456 (C5); a
    #       GENUINE 0 must therefore read as 0.0 and be DISTINGUISHABLE from ABSENT.
    #       Without this pair a zero from this reader would not be evidence (rule 3).
    z = read_log(eq_log)
    add("C8 a genuine 0.0 reads as 0.0 and is distinguishable from ABSENT",
        z.get("state") == "COMPLETE" and z.get("max_non_orthogonality_deg") == 0.0
        and ab.get("state") == "ABSENT",
        {"zero_state": z.get("state"), "zero_value": z.get("max_non_orthogonality_deg"),
         "absent_state": ab.get("state")},
        "COMPLETE/0.0 vs ABSENT")

    return all(c["pass"] for c in ctl), ctl


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log")
    ap.add_argument("--json-out")
    ap.add_argument("--selftest-eq")
    ap.add_argument("--selftest-colon")
    ap.add_argument("--selftest-workdir")
    ap.add_argument("--controls-out")
    a = ap.parse_args()

    if a.selftest_eq:
        wd = a.selftest_workdir or tempfile.mkdtemp()
        os.makedirs(wd, exist_ok=True)
        ok, ctl = selftest(a.selftest_eq, a.selftest_colon, wd)
        blob = {"all_controls_pass": ok, "controls": ctl}
        if a.controls_out:
            json.dump(blob, open(a.controls_out, "w"), indent=2)
        print(json.dumps(blob, indent=2))
        if not ok:
            print("A PLANTED CONTROL FAILED. A control that fails is a finding and stops "
                  "the measurement; it is not repaired by loosening the reading (§9).",
                  file=sys.stderr)
            return 4
        return 0

    if not a.log:
        print("nothing to do: pass --log or --selftest-eq", file=sys.stderr)
        return 2
    out = read_log(a.log)
    if a.json_out:
        json.dump(out, open(a.json_out, "w"), indent=2)
    print(json.dumps(out, indent=2))
    # REFUSES rather than degrades.
    return 0 if out.get("state") == "COMPLETE" else 2


if __name__ == "__main__":
    sys.exit(main())
