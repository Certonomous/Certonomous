#!/usr/bin/env python3
"""Parse the R1-M1 checkMesh logs into a record. NOT A GRADER. NO VERDICT IS EMITTED.

L-459 IS THE WHOLE DESIGN OF THIS FILE.  On this box `checkMesh` prints

    Mesh non-orthogonality Max: 87.7462 average: 32.9696
   *Number of severely non-orthogonal (> 70 degrees) faces: 191794.
    Non-orthogonality check OK.                <-- AT 87.7462 DEGREES
    ...
    Failed 2 mesh checks.                      <-- counts ASPECT RATIO and SKEWNESS

so the verdict strings say the opposite of the numbers.  Every quantity below is
PARSED OFF THE NAMED NUMERIC LINE.  The verdict strings are captured only to prove they
were seen and discarded, and they live in a field named

    verdict_lines_CAPTURED_AND_DISCARDED_NEVER_A_GATE

which cannot be mistaken for a gate by a later reader, a later grader, or a later agent.

PLANTED CONTROLS (rule 3), all three required or the reader REFUSES (exit 2):
  1. label-form control -- checkMesh writes the max aspect ratio in two forms,
     `Max aspect ratio = 873.822 OK.` and `Max aspect ratio: 1578.62, number of cells`.
     A reader matching only `=` silently misses exactly the pathological logs.  Both
     forms must be read from real logs in this very run before any value is emitted.
  2. non-null control -- min and max cell volume must differ, so the derived volume
     ratio is never the trivial 1.
  3. plant-and-read-back -- a scratch copy of one log has its non-orthogonality
     maximum replaced by a known value; the parser must return THAT value.  A parser
     not shown able to see a different number is not evidence for the number it read.
"""
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PLANT = 12.345678

PATS = {
    "cells": r"^\s*cells:\s*(\d+)",
    "points": r"^\s*points:\s*(\d+)",
    "faces": r"^\s*faces:\s*(\d+)",
    "internal_faces": r"^\s*internal faces:\s*(\d+)",
    "hexahedra": r"^\s*hexahedra:\s*(\d+)",
    "prisms": r"^\s*prisms:\s*(\d+)",
    "polyhedra": r"^\s*polyhedra:\s*(\d+)",
    "boundary_patches": r"^\s*boundary patches:\s*(\d+)",
    "max_non_orthogonality": r"Mesh non-orthogonality Max:\s*([0-9.eE+-]*[0-9])",
    "avg_non_orthogonality": r"Mesh non-orthogonality Max:\s*[0-9.eE+-]*[0-9]\s*average:\s*([0-9.eE+-]*[0-9])",
    "severe_non_ortho_faces": r"severely non-orthogonal \(> 70 degrees\) faces:\s*(\d+)",
    "max_skewness": r"Max skewness\s*[=:]\s*([0-9.eE+-]*[0-9])",
    "min_cell_volume": r"Min volume\s*=\s*([0-9.eE+-]*[0-9])",
    "max_cell_volume": r"Max volume\s*=\s*([0-9.eE+-]*[0-9])",
    "geometric_directions": r"Mesh has (\d+) geometric",
    "boundary_openness": r"Boundary openness \(([^)]*)\)",
    "regions": r"Number of regions:\s*(\d+)",
}
# BOTH label forms, deliberately. `:` is the pathological form.
AR_EQ = r"Max aspect ratio\s*=\s*([0-9.eE+-]*[0-9])"
AR_COLON = r"Max aspect ratio:\s*([0-9.eE+-]*[0-9])"
VERDICT = (r"Non-orthogonality check OK\.|Failed \d+ mesh check|Mesh OK\.|"
           r"Cell volumes OK\.|Face pyramids OK\.")


def grab(text, pat, cast=float):
    m = re.search(pat, text, re.M)
    return cast(m.group(1)) if m else None


def read(path):
    text = open(path).read()
    d = {}
    for k, p in PATS.items():
        d[k] = grab(text, p, str if k == "boundary_openness" else
                    (int if k in ("cells", "points", "faces", "internal_faces",
                                  "hexahedra", "prisms", "polyhedra",
                                  "boundary_patches", "severe_non_ortho_faces",
                                  "geometric_directions", "regions") else float))
    ar_eq, ar_colon = grab(text, AR_EQ), grab(text, AR_COLON)
    d["max_aspect_ratio"] = ar_eq if ar_eq is not None else ar_colon
    d["aspect_ratio_label_form"] = "=" if ar_eq is not None else (":" if ar_colon is not None else None)
    d["verdict_lines_CAPTURED_AND_DISCARDED_NEVER_A_GATE"] = sorted(set(re.findall(VERDICT, text)))
    d["how_the_number_is_read"] = (
        "PARSED off the named numeric line 'Mesh non-orthogonality Max:'. "
        "checkMesh's verdict strings are captured above SOLELY to show they were "
        "DISCARDED: this log prints 'Non-orthogonality check OK.' at "
        f"{d['max_non_orthogonality']} degrees (L-459).")
    if d["min_cell_volume"] and d["max_cell_volume"]:
        d["cell_volume_ratio"] = d["max_cell_volume"] / d["min_cell_volume"]
        d["cell_volume_ratio_basis"] = "DERIVED (max/min), NOT a checkMesh output"
    # patch table, with OpenFOAM type read from the polyMesh boundary file
    bnd = os.path.join(os.path.dirname(path), "constant", "polyMesh", "boundary")
    pat = []
    if os.path.exists(bnd):
        for name, typ, nf in re.findall(
                r"^\s{4}(\w+)\s*\n\s*\{\s*\n\s*type\s+(\w+);\s*\n\s*nFaces\s+(\d+);",
                open(bnd).read(), re.M):
            pat.append({"patch": name, "openfoam_type": typ, "nFaces": int(nf)})
    d["patches"] = pat
    return d


def controls(logs):
    """All three controls. Returns (ok, report)."""
    rep = {}
    forms = {read(p)["aspect_ratio_label_form"] for p in logs}
    rep["label_form_control"] = {
        "forms_seen_in_real_logs_this_run": sorted(f for f in forms if f),
        "must_include_both": ["=", ":"],
        "fired": {"=", ":"} <= forms}
    vols = [read(p) for p in logs]
    rep["non_null_volume_control"] = {
        "min_ne_max_on_every_level": all(
            v["min_cell_volume"] != v["max_cell_volume"] for v in vols),
        "ratios": [v.get("cell_volume_ratio") for v in vols]}
    rep["non_null_volume_control"]["fired"] = \
        rep["non_null_volume_control"]["min_ne_max_on_every_level"]
    with tempfile.TemporaryDirectory() as t:
        src = logs[0]
        dst = os.path.join(t, "PLANT_mutated_checkMesh.log")
        shutil.copyfile(src, dst)
        txt = open(dst).read()
        true_val = grab(txt, PATS["max_non_orthogonality"])
        txt = re.sub(r"(Mesh non-orthogonality Max:\s*)[0-9.eE+-]+",
                     rf"\g<1>{PLANT}", txt, count=1)
        open(dst, "w").write(txt)
        got = grab(open(dst).read(), PATS["max_non_orthogonality"])
        rep["plant_and_read_back_control"] = {
            "log": src, "true_value": true_val, "planted_value": PLANT,
            "value_read_back": got, "fired": got == PLANT and got != true_val}
    return all(c["fired"] for c in rep.values()), rep


def main():
    levels = ["L1", "L2", "L3"]
    logs = [os.path.join(ROOT, f"{L}_ugrid", "log.checkMesh") for L in levels]
    for p in logs:
        if not os.path.exists(p):
            sys.exit(f"ABSENT: {p} -- an absent checkMesh log reads ABSENT, never clean.")
    ok, rep = controls(logs)
    out = {
        "record": "R1-M1 UGRID RE-IMPORT of the M6I nested family",
        "THIS_IS_NOT_A_GRADED_RUN": True,
        "verdict": "NONE -- no verdict of the fixed vocabulary attaches to this record. "
                   "It is an admissibility MEASUREMENT. It grades nothing.",
        "covered_by_a_frozen_preregistration": False,
        "registration_gap_DISCLOSED": (
            "No frozen pre-registration covers a UGRID re-import of the M6I family. "
            "RUNG0_MESH_IMPORT_PREREGISTRATION is frozen but registers exactly four "
            "COMMITTEE grids (DPW5 hex/prism/hybrid, HLPW6 h6c1_rans_3a_1) and M6I is "
            "LAB-BUILT. RUNG1_M6_PREREGISTRATION is a DRAFT and its section 5 registers "
            "a pyHyp probe, not an import. This is surfaced to the cfd supervisor, not "
            "resolved by this lane."),
        "planted_controls": rep,
        "controls_all_fired": ok,
        "levels": {},
    }
    for L, p in zip(levels, logs):
        d = read(p)
        d["checkMesh_log"] = p
        d["source_ugrid"] = (
            f"/home/ubuntu/Certonomous/verification/runs/M6I_runs/mesh/wing_strct.{L[1]}.lb8.ugrid")
        out["levels"][L] = d
    dst = os.path.join(ROOT, "M1_CHECKMESH_READING.json")
    if not ok:
        out["REFUSED"] = "A planted control did not fire. No value here is evidence."
        json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
        sys.exit(2)
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"WROTE {dst}")
    for L, d in out["levels"].items():
        print(f"{L}: cells={d['cells']} nonOrthMax={d['max_non_orthogonality']} "
              f"avg={d['avg_non_orthogonality']} severe>70={d['severe_non_ortho_faces']} "
              f"skew={d['max_skewness']} AR={d['max_aspect_ratio']}({d['aspect_ratio_label_form']}) "
              f"patches={[(x['patch'], x['openfoam_type']) for x in d['patches']]}")


if __name__ == "__main__":
    main()
