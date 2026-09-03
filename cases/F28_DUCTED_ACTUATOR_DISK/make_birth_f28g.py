#!/usr/bin/env python3
"""Cut the F28G birth certificates for verification/runs/F28_runs/mesh_A4/L{1,2,3}.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
It is a TRANSCRIBER with a reader. It reads M1/M2/M3 off the committed checkMesh
summaries and transcribes M4/M5/M6 from the FROZEN registration's own measured
tables (sections 5.1 and 5.3). It DECIDES NOTHING: every threshold is F28G's
section 6.1 and every value is either parsed from an artifact or quoted from the
freeze.

WHY THESE CERTIFICATES EXIST AT ALL. run_f28.sh quarantines a polyMesh lacking a
birth certificate (MESH_STANDARD section 6). mesh_A4/L1..L3 had none. The
supervisor ruled 2026-09-03 that an F28G mesh is certified against F28G's OWN
section 5/6 gates -- the registration under which a mesh is USED is the one whose
gates it must answer -- not against the parent's three-clause set.

NO BARE `assert` ANYWHERE (L-332): `python3 -O` deletes them, so every refusal
here is a `raise` or a `sys.exit`.

SECTION 6.1's OWN READING RULE IS OBEYED AND IS THE POINT OF THE READER:
"M1 is read off the reported maximum and the severe-face count beside it, NEVER
off `Non-orthogonality check OK.` and NEVER off `Mesh OK.` / `Failed N mesh
checks.`  Any comparator that greps a verdict string is reading the wrong
instrument and its clean result is not evidence."  So the reader parses NUMBERS
and never a verdict string, and --selftest plants a summary whose verdict lines
say OK while its numbers violate the gates, requiring the reader to REJECT it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"
MESH_DIR = os.path.join(REPO, "verification/runs/F28_runs/mesh_A4")
PREREG_REL = "verification/campaign/F28G_GRID_CONVERGENCE_PREREGISTRATION.md"

# F28G section 6.1 thresholds. Quoted, not chosen.
M1_MAX_NON_ORTHO = 65.0          # parent section 5, stricter than MESH_STANDARD 3.1's 70
M2_MAX_SKEWNESS = 4.0            # MESH_STANDARD section 3.2 hard gate
M5_RATIO, M5_TOL = 1.5, 0.05     # Sanaa section 0 step 1
M6_JUMP_LO, M6_JUMP_HI = 0.95, 1.05   # MESH_STANDARD section 9.2

# section 4.1: MAX_GROWTH 1.25 at L1, 1.25**(1/s) at level s.
M4_GROWTH_CAP = {"L1": 1.25000, "L2": 1.16040, "L3": 1.10426}

# Transcribed from the FROZEN registration section 5.1 (cells, per-direction ratios)
# and section 5.3 (similarity read-back). Values quoted, never recomputed here.
CELLS = {"L1": 35544, "L2": 79974, "L3": 180256}
PER_DIRECTION_RATIOS = {   # (r21, r32) per direction, section 5.1's second table
    "nr_I": (1.5000, 1.5000), "nr_BI_BO": (1.5000, 1.5152),
    "nr_O1": (1.5000, 1.5152), "nr_O2": (1.5000, 1.4872),
    "nx_c0": (1.5000, 1.5000), "nx_c1": (1.5000, 1.5000),
    "nx_c2": (1.5000, 1.5000), "nx_c3": (1.5000, 1.4815),
}
# section 5.3: rho (constant across levels), junction_jump per level, q1 per level.
SIMILARITY = {
    "ROW_I": {"rho": [0.73500, 0.73500, 0.73500], "jump": [0.9945, 1.0108, 1.0174],
              "q1": [1.24115, 1.15386, 1.09967]},
    "c1": {"rho": [1.06000] * 3, "jump": [1.0281, 1.0242, 1.0216],
           "q1": [1.20810, 1.13116, 1.08435]},
    "c2": {"rho": [0.68923] * 3, "jump": [1.0003, 0.9942, 1.0274],
           "q1": [1.17786, 1.10972, 1.07350]},
    "c3": {"rho": [0.99000] * 3, "jump": [0.9939, 0.9927, 0.9923],
           "q1": [1.11569, 1.07332, 1.04952]},
    "c4": {"rho": [1.00000] * 3, "jump": [1.0000] * 3, "q1": [1.00000] * 3},
    "c5": {"rho": [1.00174] * 3, "jump": [1.0012, 0.9947, 0.9923],
           "q1": [1.08526, 1.05625, 1.03613]},
    "c6": {"rho": [0.65435] * 3, "jump": [0.9995, 1.0070, 1.0101],
           "q1": [1.08217, 1.05378, 1.03521]},
}

# A FLOAT, not "a run of characters that appear in floats". The naive class
# [0-9.eE+-]+ swallows the SENTENCE-ENDING PERIOD in "Min volume = 1.40612e-16."
# and float() then raises -- measured on the real L1 summary while writing this.
# It raised loudly rather than returning a wrong number, which is the only reason
# it was cheap; a reader that had silently coerced would have certified a mesh on
# a mangled figure.
_F = r"[-+]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?"
RE_NON_ORTHO = re.compile(r"Mesh non-orthogonality Max:\s*(%s)" % _F)
RE_SKEW = re.compile(r"Max skewness\s*=\s*(%s)" % _F)
RE_MIN_VOL = re.compile(r"Min volume\s*=\s*(%s)" % _F)
RE_ASPECT = re.compile(r"Max aspect ratio[:=]\s*(%s)" % _F)
RE_NEG_VOL = re.compile(r"([0-9]+)\s+negative volume", re.I)


def read_checkmesh(path: str) -> dict:
    """Parse NUMBERS only. Never a verdict string (section 6.1's reading rule)."""
    with open(path) as fh:
        txt = fh.read()
    out = {}
    for key, rx in (("max_non_orthogonality", RE_NON_ORTHO),
                    ("max_skewness", RE_SKEW),
                    ("min_volume", RE_MIN_VOL),
                    ("max_aspect_ratio", RE_ASPECT)):
        m = rx.search(txt)
        if m is None:
            raise ValueError("%s: %s not found -- an ABSENT number NEVER reads clean" % (path, key))
        out[key] = float(m.group(1))
    m = RE_NEG_VOL.search(txt)
    out["negative_volume_cells"] = int(m.group(1)) if m else 0
    return out


def gates(level: str, cm: dict) -> dict:
    """F28G section 6.1, M1..M6. Every clause returns a bool and nothing else."""
    idx = {"L1": 0, "L2": 1, "L3": 2}[level]
    # M4 is VERIFIED here from section 5.3's achieved q1 values rather than taken on
    # the generator's word that it refuses an inadmissible mesh. Every distribution's
    # per-cell growth at THIS level must sit under THIS level's 1.25**(1/s) cap.
    m4 = all(d["q1"][idx] <= M4_GROWTH_CAP[level] + 1e-9 for d in SIMILARITY.values())
    m5 = all(abs(r - M5_RATIO) <= M5_RATIO * M5_TOL + 1e-12
             for pair in PER_DIRECTION_RATIOS.values() for r in pair)
    m6_rho = all(len(set(round(x, 9) for x in d["rho"])) == 1 for d in SIMILARITY.values())
    m6_jump = all(M6_JUMP_LO <= d["jump"][idx] <= M6_JUMP_HI for d in SIMILARITY.values())
    return {
        "M1_max_non_orthogonality_lt_65": cm["max_non_orthogonality"] < M1_MAX_NON_ORTHO,
        "M2_max_skewness_lt_4": cm["max_skewness"] < M2_MAX_SKEWNESS,
        "M3_zero_negative_volumes": cm["negative_volume_cells"] == 0 and cm["min_volume"] > 0.0,
        "M4_growth_within_level_cap": bool(m4),
        "M5_refinement_ratio_1p5_within_5pc": bool(m5),
        "M6_similarity_rho_invariant_and_jumps_in_band": bool(m6_rho and m6_jump),
    }


def build(level: str, prereg_commit: str) -> dict:
    summary = os.path.join(MESH_DIR, "checkmesh_summary_%s.txt" % level)
    cm = read_checkmesh(summary)
    g = gates(level, cm)
    idx = {"L1": 0, "L2": 1, "L3": 2}[level]
    return {
        "case": "F28_DUCTED_ACTUATOR_DISK",
        "study": "F28G_GRID_CONVERGENCE",
        "level": level,
        "stage": "stage0_mesh_birth",
        "registration": PREREG_REL,
        "registration_commit": prereg_commit,
        "gates_are_section_6_1_of_THIS_registration": (
            "Certified against F28G's OWN section 6.1 (M1..M6), NOT the parent's "
            "section 5 three-clause set. cfd-supervisor's ruling 2026-09-03: the "
            "registration under which a mesh is USED is the registration whose gates "
            "it must answer. This is a SCHEMA BINDING, NOT A GATE CHANGE -- no "
            "threshold moves and every number below is F28G's own, frozen at 00188f82."),
        "registered_gates_section_5": g,
        "_registered_gates_section_5_note": (
            "This key carries F28G's section 6.1 gates. The KEY NAME is the schema "
            "run_f28.sh reads (it requires every value true); the CONTENT is this "
            "study's gate-set. The name is retained rather than renamed because "
            "renaming it would silently disable the launcher's admissibility check."),
        "checkMesh": cm,
        "checkMesh_summary": os.path.relpath(summary, REPO),
        "checkMesh_full_log_untracked": os.path.relpath(
            os.path.join(MESH_DIR, level, "log.checkMesh"), REPO),
        "cells": CELLS[level],
        "per_direction_refinement_ratios_section_5_1": PER_DIRECTION_RATIOS,
        "similarity_read_back_section_5_3": {
            k: {"rho": v["rho"][idx], "junction_jump": v["jump"][idx], "q1": v["q1"][idx]}
            for k, v in SIMILARITY.items()},
        "growth_cap_this_level_section_4_1": M4_GROWTH_CAP[level],
        "aspect_ratio_note": (
            "RECORDED AND EXPLICITLY NOT GATED (F28G section 6.2; MESH_STANDARD 3.3 "
            "'advisory at 1000, never a lone rejection'; 11.4 'no value of it makes a "
            "mesh inadmissible'). Measured %.1f here, against the lab's own "
            "reference-grade NASA TMR calibration of 66,643-74,041. What makes a "
            "record incomplete is the ABSENCE of this number, never its size."
            % cm["max_aspect_ratio"]),
        "y_plus_status": (
            "ESTIMATE UNTIL A SOLVE RETURNS, and labelled as such (parent Addendum 1 "
            "A1.7, carried by F28G section 7 registered addition 6). No solve has run."),
        "reading_rule_obeyed": (
            "M1 and M2 are parsed as NUMBERS off 'Mesh non-orthogonality Max:' and "
            "'Max skewness =' and NEVER off 'Non-orthogonality check OK.', 'Mesh OK.' "
            "or 'Failed N mesh checks.' (F28G section 6.1; MESH_STANDARD 14.4). A "
            "comparator that greps a verdict string is reading the wrong instrument "
            "and its clean result is not evidence. --selftest plants a summary whose "
            "verdict lines read OK while its numbers violate M1 and M2, and requires "
            "this reader to REJECT it."),
        "stage0_verdict": "GATE REACHED" if all(g.values()) else "GATE FAIL",
        "not_claimed": (
            "This certificate admits a MESH. It is not a solve, not a verdict on any "
            "F28G gate, and no y+ or physics claim follows from it."),
    }


def selftest() -> int:
    """Plant a summary that LOOKS clean and is not, and require rejection."""
    import tempfile
    ok = True
    good = os.path.join(MESH_DIR, "checkmesh_summary_L1.txt")
    cm = read_checkmesh(good)
    g = gates("L1", cm)
    if not all(g.values()):
        print("SELFTEST: the real L1 summary does not pass its own gates: %r" % g)
        ok = False
    else:
        print("SELFTEST silent limb: real L1 summary parses and passes M1..M6")

    planted = ("Mesh non-orthogonality Max: 88.5 average: 9.9\n"
               "    Non-orthogonality check OK.\n"
               "    Max skewness = 9.9 OK.\n"
               "    Min volume = 1e-16. Max volume = 1.0.  Cell volumes OK.\n"
               " ***High aspect ratio cells found, Max aspect ratio: 100.0, number of cells 1\n"
               "Mesh OK.\n")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write(planted)
        p = fh.name
    try:
        pcm = read_checkmesh(p)
        pg = gates("L1", pcm)
        if pg["M1_max_non_orthogonality_lt_65"] or pg["M2_max_skewness_lt_4"]:
            print("SELFTEST FAILED: the planted summary says 'OK' on every verdict line "
                  "and violates M1 (88.5) and M2 (9.9), and the reader ACCEPTED it. "
                  "The reader is grepping verdict strings.")
            ok = False
        else:
            print("SELFTEST control FIRED: planted summary with clean verdict lines and "
                  "M1=88.5, M2=9.9 was REJECTED on the numbers (M1 %s, M2 %s)"
                  % (pg["M1_max_non_orthogonality_lt_65"], pg["M2_max_skewness_lt_4"]))
    finally:
        os.unlink(p)

    missing = "Max skewness = 1.0 OK.\n"
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
        fh.write(missing)
        p2 = fh.name
    try:
        read_checkmesh(p2)
        print("SELFTEST FAILED: a summary missing 'Mesh non-orthogonality Max:' parsed "
              "clean. AN ABSENT NUMBER MUST NEVER READ CLEAN.")
        ok = False
    except ValueError:
        print("SELFTEST control FIRED: a summary missing M1's number RAISED rather than "
              "returning a default")
    finally:
        os.unlink(p2)
    print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 2


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    commit = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H", "--", PREREG_REL],
                            capture_output=True, text=True).stdout.strip()
    if not re.match(r"^[0-9a-f]{40}$", commit):
        sys.stderr.write("REFUSED: could not resolve the registration's commit\n")
        return 2
    rc = 0
    for level in ("L1", "L2", "L3"):
        cert = build(level, commit)
        out = os.path.join(MESH_DIR, "BIRTH_%s.json" % level)
        if os.path.exists(out) and "--force" not in argv:
            sys.stderr.write("REFUSED: %s exists; not overwriting a certificate\n" % out)
            return 2
        with open(out, "w") as fh:
            json.dump(cert, fh, indent=2)
            fh.write("\n")
        bad = [k for k, v in cert["registered_gates_section_5"].items() if not v]
        print("%s  %s  verdict=%s  M1=%.4f M2=%.5f AR=%.1f%s"
              % (out, level, cert["stage0_verdict"],
                 cert["checkMesh"]["max_non_orthogonality"],
                 cert["checkMesh"]["max_skewness"],
                 cert["checkMesh"]["max_aspect_ratio"],
                 ("  FAILED: %s" % bad) if bad else ""))
        if bad:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
